"""The general spacetime analyzer — `analyze(metric, coords)` → one report.

The widening (2026-06-16): instead of a bespoke script per domain, ONE entry
point that eats ANY metric — black hole, expanding universe, wormhole, warp
bubble, any coordinates, any dimension — and returns one honest report. This is
the CORE: it answers three questions, and leaves room to grow (symmetries,
singularities, horizons/thermodynamics come next).

    • what is it made of?     — read the stress-energy off the Einstein tensor,
                                 then classify (vacuum / Λ / perfect fluid /
                                 traceless / anisotropic);
    • is that matter physical? — the energy conditions, computed FRAME-
                                 INDEPENDENTLY from the principal components of
                                 T^a_b (the single upgrade that frees the check
                                 from the static-black-hole frame and makes it
                                 work on cosmology, wormholes, warp, …);
    • does it solve Einstein's equations? — vacuum / vacuum+Λ / sourced.

Design rules inherited from the engine: pure SymPy, reuse gr_engine.Geometry for
all curvature, and stay THREE-VALUED — every answer is True / False / UNKNOWN,
never a guess. It does NOT touch scripts 01–38; those stay frozen as the proven
base and the analyzer's regression suite (see 40_analyzer.py).
"""

import os
import random
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry, zero_simplify

UNKNOWN = None  # three-valued, as everywhere in this project


# ---------------------------------------------------------------------------
# sign / nonneg helpers (three-valued)
# ---------------------------------------------------------------------------

def _sign(expr, domain=None):
    """+1 / −1 / 0 / None — sign of expr over the physical domain (positive
    parameters & coordinates). Symbolic when SymPy can decide, else sampled;
    None (UNKNOWN) if the sign is mixed or too few samples are real-evaluable.

    A sample that doesn't evaluate to a real number (e.g. a √ of a negative —
    common for an interior solution sampled outside its radial domain r≤R) is
    SKIPPED, not fatal: a single out-of-domain point shouldn't poison a verdict
    the in-domain points agree on (this is what let stellar interiors finally
    certify physical). We still demand a quorum of real samples that unanimously
    agree before committing to a sign; otherwise UNKNOWN, as ever.

    `domain` (optional): {symbol: (lo, hi)} restricting where a coordinate is
    sampled — e.g. {r: (0, R)} for a stellar interior, real only inside the star.
    Symbols absent from `domain` keep the default (1..25)/(1..6) rational draw, so
    `domain=None` reproduces the original sampling sequence byte-for-byte."""
    e = sp.simplify(expr)
    if e == 0:
        return 0
    if e.is_positive:
        return 1
    if e.is_negative:
        return -1
    rng = random.Random(0)
    free = sorted(e.free_symbols, key=str)
    seen = set()
    valid = 0
    for _ in range(60):
        sub = {}
        for s in free:                         # default draw first (preserves rng
            d = sp.Rational(rng.randint(1, 25), rng.randint(1, 6))   # sequence)
            if domain and s in domain:          # …then override bounded coordinates
                lo, hi = (float(b) for b in domain[s])
                d = sp.Float(lo + (hi - lo) * rng.random())
            sub[s] = d
        try:
            v = float(e.subs(sub))
        except (TypeError, ValueError):
            continue                       # not real here — skip, don't bail
        valid += 1
        if v > 1e-12:
            seen.add(1)
        elif v < -1e-12:
            seen.add(-1)
        else:
            seen.add(0)
    if valid < 20:           # too little real signal to trust unanimity ⇒ UNKNOWN
        return None
    if seen == {1}:
        return 1
    if seen == {-1}:
        return -1
    if seen <= {0}:
        return 0
    return None        # mixed sign over the domain ⇒ cannot give one verdict


def _nonneg(expr, domain=None):
    s = _sign(expr, domain)
    return None if s is None else (s >= 0)


def _all(*vals):
    if any(v is False for v in vals):
        return False
    if any(v is None for v in vals):
        return None
    return True


def _is_zero_matrix(M):
    return all(zero_simplify(M[i, j]) == 0 for i in range(M.rows) for j in range(M.cols))


def _numeric_nonzero(M, coords, trials=4):
    """Fast definitive 'sourced' detector: True if M is non-zero at a sampled
    exact-rational point (so the metric is provably non-vacuum without symbolic
    zero-testing). False means 'inconclusive → fall through to the symbolic
    check'. Mirrors the engine's numeric_spot_check; the point is to AVOID the
    expensive blanket simplify on heavy off-diagonal (Kerr) curvature."""
    rng = random.Random(0)
    for _ in range(trials):
        sub = {s: sp.Rational(rng.randint(11, 99), rng.randint(7, 13)) for s in coords}
        for i in range(M.rows):
            for j in range(i, M.cols):
                try:
                    if abs(complex(M[i, j].subs(sub).evalf(20))) > 1e-6:
                        return True
                except (TypeError, ValueError):
                    return False
    return False


# ---------------------------------------------------------------------------
# the matter and its physicality
# ---------------------------------------------------------------------------

def stress_energy(geo):
    """Mixed stress-energy T^a_b = G^a_b / 8π that sources the metric. Reduced
    per-component with the cheap cancel(together) (NOT a blanket simplify — that
    drowns on heavy off-diagonal curvature; same lesson as the engine's D2/D22)."""
    G = geo.ricci - sp.Rational(1, 2) * geo.ricci_scalar * geo.g
    raw = geo.ginv * G / (8 * sp.pi)
    n = geo.n
    return sp.Matrix(n, n, lambda i, j: sp.cancel(sp.together(raw[i, j])))


def principal_components(geo, Tmix):
    """Frame-independent (ρ, [pressures]) — the energy density and principal
    pressures, i.e. the eigenvalues of T^a_b (timelike eigenvalue = −ρ,
    spacelike = pressures). Returns (UNKNOWN, UNKNOWN) if not cleanly Type I.

    Diagonal metrics (the common case — FLRW, wormhole, RN, …) take the direct
    route with coordinate 0 as the time direction; off-diagonal metrics go
    through a genuine eigen-decomposition and are UNKNOWN if it isn't clean."""
    n = geo.n
    if Tmix.is_diagonal():
        rho = sp.simplify(-Tmix[0, 0])
        pressures = [sp.simplify(Tmix[i, i]) for i in range(1, n)]
        return rho, pressures
    try:
        eig = Tmix.eigenvects()
    except Exception:
        return UNKNOWN, UNKNOWN
    rho, pressures = None, []
    for val, _mult, vecs in eig:
        for v in vecs:
            v = sp.Matrix(v)
            norm = _sign(sp.simplify((v.T * geo.g * v)[0]))
            if norm is None:
                return UNKNOWN, UNKNOWN
            if norm < 0:                       # timelike eigenvector ⇒ density
                if rho is not None:
                    return UNKNOWN, UNKNOWN     # >1 timelike ⇒ not Type I
                rho = sp.simplify(-val)
            else:
                pressures.append(sp.simplify(val))
    if rho is None or len(pressures) != n - 1:
        return UNKNOWN, UNKNOWN
    return rho, pressures


def energy_conditions(rho, pressures, domain=None):
    """NEC / WEC / DEC / SEC, three-valued, from (ρ, pressures).

    `domain` (optional) restricts where the coordinate-dependent ρ,p are sampled
    for the sign tests — e.g. {r: (0, R)} to certify a stellar interior, which is
    only real inside the star."""
    if rho is UNKNOWN:
        return {k: UNKNOWN for k in ("NEC", "WEC", "DEC", "SEC")}
    nec = _all(*[_nonneg(rho + p, domain) for p in pressures])
    wec = _all(nec, _nonneg(rho, domain))
    dec = _all(_nonneg(rho, domain), *[_nonneg(rho - p, domain) for p in pressures],
               *[_nonneg(rho + p, domain) for p in pressures])
    sec = _all(nec, _nonneg(rho + sum(pressures), domain))
    return {"NEC": nec, "WEC": wec, "DEC": dec, "SEC": sec}


def matter_type(geo, Tmix):
    """A plain-language description of what sources the metric, plus its
    principal components (computed for everything except true vacuum, so the
    energy conditions can always be evaluated when there is matter)."""
    n = geo.n
    if _is_zero_matrix(Tmix):
        return "vacuum (empty space)", UNKNOWN, UNKNOWN
    rho, pressures = principal_components(geo, Tmix)
    if rho is UNKNOWN:
        return "matter (could not classify — UNKNOWN)", rho, pressures
    if _is_zero_matrix(Tmix - Tmix[0, 0] * sp.eye(n)):   # T^a_b ∝ δ ⇒ p = −ρ
        return "cosmological constant Λ (w = −1)", rho, pressures
    if all(zero_simplify(p - pressures[0]) == 0 for p in pressures):
        w = sp.simplify(pressures[0] / rho) if rho != 0 else UNKNOWN
        return f"perfect fluid (isotropic, w = {w})", rho, pressures
    if zero_simplify(sum([-rho] + pressures)) == 0:   # traceless: −ρ+Σp = 0
        return "traceless matter (radiation / electromagnetic-like)", rho, pressures
    return "anisotropic matter", rho, pressures


def field_verdict(geo):
    """vacuum (Ricci-flat) / vacuum + Λ / sourced — three-valued. Uses the
    traceless-Ricci residual with a NUMERIC pre-check so a sourced metric is
    caught instantly (no symbolic zero-testing of heavy off-diagonal curvature),
    and only a numerically-vacuum metric pays for the symbolic confirmation."""
    n = geo.n
    Ric = geo.ricci
    # Ricci numerically zero ⇒ candidate PURE VACUUM — confirm symbolically WITHOUT
    # ever forming ricci_scalar (the heavy contraction that hangs on Kerr).
    if not _numeric_nonzero(Ric, geo.coords):
        if _is_zero_matrix(Ric):
            return "vacuum (Ricci-flat)"
    # Ricci is (numerically) non-zero: Einstein space (vacuum+Λ) or genuinely sourced.
    Lam = sp.cancel(sp.together(geo.ricci_scalar * (n - 2) / (2 * n)))
    resid = Ric - (2 * Lam / (n - 2)) * geo.g          # traceless part of Ricci
    if _numeric_nonzero(resid, geo.coords):
        return "sourced (non-vacuum matter)"           # provably non-Einstein-space
    if _is_zero_matrix(resid):
        return f"vacuum + cosmological constant (Λ = {sp.simplify(Lam)})"
    return "sourced (non-vacuum matter)"


# ---------------------------------------------------------------------------
# singularities, symmetries, horizons (the growth increments)
# ---------------------------------------------------------------------------

def singularities(geo):
    """Curvature blow-ups: coordinate values where the Kretschmann scalar
    diverges. Returns [] (none — K finite), a list of (coord, value), or
    UNKNOWN if K can't be formed. (Raw blow-ups; not restricted to a metric's
    physical coordinate domain.)"""
    if not geo.g.is_diagonal():
        return UNKNOWN     # off-diagonal Kretschmann needs full simplify (expensive) — #2 TODO
    try:
        K = sp.simplify(geo.kretschmann)
    except Exception:
        return UNKNOWN
    if not any(K.has(c) for c in geo.coords):
        return []                              # K constant in coords ⇒ no singularity
    _num, den = sp.fraction(sp.together(K))
    sings = []
    for var in geo.coords:
        if den.has(var):
            d = sp.Dummy(real=True)            # generic symbol: don't let r>0 hide r=0
            try:
                roots = sp.solve(den.subs(var, d), d)
            except Exception:
                continue
            for rt in roots:
                if (var, rt) not in sings:
                    sings.append((var, rt))
    return sings


def symmetries(geo):
    """Manifest Killing vectors from cyclic coordinates — a coordinate the
    metric doesn't depend on gives the Killing vector ∂/∂(that coord) and a
    conserved quantity. A LOWER BOUND on the full isometry group (it doesn't
    find symmetries that mix coordinates, e.g. the full rotation group)."""
    return [x for x in geo.coords
            if not any(geo.g[i, j].has(x) for i in range(geo.n) for j in range(geo.n))]


def is_killing_vector(geo, xi):
    """Exact check of the Killing equation ∇_a ξ_b + ∇_b ξ_a = 0 for a
    contravariant field ξ^a (a list of n components). True/False."""
    g, X, n, G = geo.g, geo.coords, geo.n, geo.christoffel
    xil = [sp.simplify(sum(g[b, c] * xi[c] for c in range(n))) for b in range(n)]
    for a in range(n):
        for b in range(a, n):
            lhs = (sp.diff(xil[b], X[a]) + sp.diff(xil[a], X[b])
                   - 2 * sum(G[c][a][b] * xil[c] for c in range(n)))
            if sp.simplify(lhs) != 0:
                return False
    return True


def killing_vectors(geo):
    """The Killing vectors the engine can pin down: the manifest cyclic ones,
    PLUS the coordinate-mixing rotation group SO(3) when the metric is spherically
    symmetric (angular block r²dΩ²) — the symmetries `symmetries()` misses. Each is
    verified against the Killing equation. Still a lower bound for maximally
    symmetric spaces (de Sitter/Minkowski have the full 10). Returns [(label, ξ^a)]."""
    g, X, n = geo.g, geo.coords, geo.n
    found = []
    for i, x in enumerate(X):                       # manifest cyclic KVs
        if not any(g[a, b].has(x) for a in range(n) for b in range(n)):
            found.append((f"∂/∂{x}", [sp.Integer(1) if k == i else sp.S.Zero
                                      for k in range(n)]))
    if n == 4:                                       # rotational SO(3) if spherical
        r, th, ph = X[1], X[2], X[3]
        if (sp.simplify(g[2, 2] - r**2) == 0
                and sp.simplify(g[3, 3] - r**2 * sp.sin(th)**2) == 0):
            for nm, v in (("R_x", [0, 0, -sp.sin(ph), -sp.cos(ph) / sp.tan(th)]),
                          ("R_y", [0, 0, sp.cos(ph), -sp.sin(ph) / sp.tan(th)])):
                if is_killing_vector(geo, v):
                    found.append((nm, v))
    return found


def horizon_thermo(geo):
    """Static Killing horizons (where ∂_t goes null, g_tt=0) and their
    temperature/entropy, for the standard form g_tt=−f, g_rr=1/f. Returns []
    (none), a list of (r_h, T, S), or UNKNOWN if the form/solve doesn't fit."""
    g, coords, n = geo.g, geo.coords, geo.n
    rc = coords[1]
    if not g.is_diagonal():
        # stationary / off-diagonal (e.g. Kerr): the Killing horizon is the null
        # hypersurface r=const where g^{rr}=0 (Δ=0), NOT g_tt=0 (that's the
        # ergosphere). Report LOCATION only — rotating-horizon T,S is a later task.
        grr = sp.cancel(sp.together(geo.ginv[1, 1]))
        if not grr.has(rc):
            return []                          # no radial structure ⇒ no horizon (e.g. Gödel)
        fnum = sp.numer(grr)
        try:
            if sp.Poly(fnum, rc).degree() > 2:
                return UNKNOWN
        except sp.PolynomialError:
            return UNKNOWN
        try:
            roots = sp.solve(fnum, rc)
        except Exception:
            return UNKNOWN
        return [(sp.simplify(rh), UNKNOWN, UNKNOWN) for rh in roots]
    gtt = g[0, 0]
    if not gtt.has(rc):
        return []                              # ∂_t never null along r ⇒ no horizon here
    f = sp.simplify(-gtt)
    if sp.simplify(g[1, 1] * f - 1) != 0:      # need g_tt=−f and g_rr=1/f
        return UNKNOWN
    fnum = sp.numer(sp.together(f))            # clear 1/r etc. to a polynomial in r
    try:
        if sp.Poly(fnum, rc).degree() > 2:     # cubic+ horizon roots: present but not clean — #2 TODO
            return UNKNOWN
    except sp.PolynomialError:
        return UNKNOWN
    try:
        roots = sp.solve(f, rc)
    except Exception:
        return UNKNOWN
    out = []
    for rh in roots:
        T = sp.simplify(sp.diff(f, rc).subs(rc, rh) / (4 * sp.pi))   # κ/2π, κ=f'(r_h)/2
        A = sp.sqrt(sp.simplify(g[2:, 2:].subs(rc, rh).det()))       # horizon area element
        ranges = [(coords[2], 0, sp.pi)] + [(coords[k], 0, 2 * sp.pi) for k in range(3, n)]
        try:
            for v, lo, hi in ranges:
                A = sp.integrate(A, (v, lo, hi))
            S = sp.simplify(A / 4)                                   # Bekenstein–Hawking A/4
        except Exception:
            S = UNKNOWN
        out.append((sp.simplify(rh), T, S))
    return out


def signature_flip(geo):
    """Does the timelike Killing direction ∂_t go spacelike somewhere (g_tt
    changes sign)? That's the 'space and time swap roles' inside a horizon — the
    timelike direction rotating ∂_t → ∂_r. Scans the radial coordinate DENSELY
    (random param samples × a fine radial grid) so a narrow flip band between two
    close horizons isn't missed."""
    gtt = geo.g[0, 0]
    fs = gtt.free_symbols
    if not fs:
        return False
    rc = geo.coords[1]
    params = [s for s in fs if s != rc]
    rgrid = [0.05 * k for k in range(1, 400)]          # 0.05 .. ~20, fine
    rng = random.Random(0)
    for _ in range(8):
        psub = {s: sp.Rational(rng.randint(1, 12), rng.randint(1, 5)) for s in params}
        gr = gtt.subs(psub) if params else gtt
        signs = set()
        for rv in rgrid:
            try:
                v = float(gr.subs(rc, rv)) if gr.has(rc) else float(gr)
            except (TypeError, ValueError):
                continue
            signs.add(1 if v > 1e-9 else (-1 if v < -1e-9 else 0))
        if 1 in signs and -1 in signs:
            return True
        if not params:
            break
    return False


def causal_structure(geo, sings):
    """The causal-structure lens (#2): the CHARACTER of each singularity —
    spacelike ('a moment, the end of time' — unavoidable) vs timelike ('a place'
    — avoidable), from the sign of g^{kk} along the singular direction — plus
    whether the timelike direction flips inside a horizon (signature_flip)."""
    out = {"singularity_character": [], "signature_flip": signature_flip(geo)}
    if not sings or sings is UNKNOWN:
        return out
    for var, val in sings:
        try:
            k = geo.coords.index(var)
            lim = sp.limit(geo.ginv[k, k], var, val)
            if lim == sp.oo or lim.is_positive:
                ch = "timelike (avoidable — 'a place')"
            elif lim == -sp.oo or lim.is_negative:
                ch = "spacelike (unavoidable — 'the end of time')"
            else:
                ch = "null / UNKNOWN"
        except Exception:
            ch = "UNKNOWN"
        out["singularity_character"].append((var, val, ch))
    return out


def observables(geo):
    """What a telescope would SEE, for a static black hole (g_tt=−f, g_rr=1/f):
    photon sphere (light ring, 2f=rf'), shadow (b_c=r_ph/√f(r_ph)), and ISCO
    (3ff'−2rf'²+rff''=0). Returns {} if not the static form or not a black hole.
    Degree-capped + wrapped so it can't slow the general report."""
    g, coords, n = geo.g, geo.coords, geo.n
    if n != 4 or not g.is_diagonal():
        return {}
    rc = coords[1]
    f = sp.cancel(sp.together(-g[0, 0]))
    if not f.has(rc) or sp.simplify(g[1, 1] * f - 1) != 0:
        return {}

    def _roots(expr):
        num = sp.numer(sp.together(expr))
        try:
            if sp.Poly(num, rc).degree() > 4:
                return None
        except sp.PolynomialError:
            return None
        try:
            return [sp.simplify(rt) for rt in sp.solve(num, rc)
                    if rt.is_positive is not False and rt.is_real is not False]
        except Exception:
            return None

    out = {}
    ps = _roots(2 * f - rc * sp.diff(f, rc))
    if ps:
        out["photon_sphere"] = ps
        rp = ps[0]
        fp = sp.simplify(f.subs(rc, rp))
        if fp != 0 and fp.is_positive is not False:
            out["shadow"] = sp.simplify(rp / sp.sqrt(fp))
            # eikonal ringdown (Cardoso correspondence): QNM ω = ℓ·Ω_c − i(n+½)λ,
            # both closed-form from the photon sphere. ω_R = ℓ/shadow; λ is the
            # orbit's instability rate. The exact overtone spectrum needs Leaver
            # (numerical) — this is the exact eikonal limit. (battery 56)
            out["ringdown_omega_c"] = sp.simplify(sp.sqrt(fp) / rp)
            fpp = sp.simplify(f.diff(rc, 2).subs(rc, rp))
            out["ringdown_lyapunov"] = sp.simplify(
                sp.sqrt(fp * (2 * fp - rp**2 * fpp) / (2 * rp**2)))
    isc = _roots(3 * f * sp.diff(f, rc) - 2 * rc * sp.diff(f, rc)**2 + rc * f * sp.diff(f, rc, 2))
    if isc:
        out["isco"] = isc
    return out


# ---------------------------------------------------------------------------
# Petrov classification — the algebraic type of the Weyl (pure-gravity) tensor
# ---------------------------------------------------------------------------

def weyl_tensor(geo):
    """C_{abcd} (all indices down), 4D, from the metric's Riemann/Ricci."""
    n, g, Ric, Rs, Rm = geo.n, geo.g, geo.ricci, geo.ricci_scalar, geo.riemann
    Rl = [[[[sp.cancel(sp.together(sum(g[a, e] * Rm[e][b][c][d] for e in range(n))))
             for d in range(n)] for c in range(n)] for b in range(n)] for a in range(n)]

    def C(a, b, c, d):
        t = (Rl[a][b][c][d]
             - sp.Rational(1, 2) * (g[a, c] * Ric[b, d] - g[a, d] * Ric[b, c]
                                    - g[b, c] * Ric[a, d] + g[b, d] * Ric[a, c])
             + sp.Rational(1, 6) * Rs * (g[a, c] * g[b, d] - g[a, d] * g[b, c]))
        return sp.simplify(t)

    return [[[[C(a, b, c, d) for d in range(n)] for c in range(n)]
             for b in range(n)] for a in range(n)]


def weyl_scalars(C, tetrad):
    """(Ψ0…Ψ4) from the Weyl tensor and a null tetrad (l, n, m, mbar)."""
    l, nn, m, mb = tetrad

    def k(v1, v2, v3, v4):
        s = sp.S.Zero
        for a in range(4):
            if v1[a] == 0:
                continue
            for b in range(4):
                if v2[b] == 0:
                    continue
                for c in range(4):
                    if v3[c] == 0:
                        continue
                    for d in range(4):
                        if v4[d] != 0:
                            s += C[a][b][c][d] * v1[a] * v2[b] * v3[c] * v4[d]
        return sp.simplify(s)

    return (k(l, m, l, m), k(l, nn, l, m), k(l, m, mb, nn),
            k(l, nn, mb, nn), k(nn, mb, nn, mb))


def petrov_type(P):
    """Petrov type from the Ψ-pattern in an adapted (canonical) tetrad."""
    s = {k for k, p in enumerate(P) if sp.simplify(p) != 0}
    if not s:
        return "O"
    if s == {2}:
        return "D"
    if s in ({0}, {4}):
        return "N"
    if s <= {0, 1} or s <= {3, 4}:
        return "III"
    if s <= {0, 1, 2} or s <= {2, 3, 4}:
        return "II"
    return "I"


def weyl_invariants(P):
    """The frame-independent Weyl invariants I, J (Lorentz scalars); the spacetime
    is algebraically special ⟺ I³ = 27 J²."""
    P0, P1, P2, P3, P4 = P
    I = sp.simplify(P0 * P4 - 4 * P1 * P3 + 3 * P2**2)
    J = sp.simplify(sp.Matrix([[P4, P3, P2], [P3, P2, P1], [P2, P1, P0]]).det())
    return I, J


def petrov(geo):
    """Petrov type, three-valued. Computed for the static spherical diagonal form
    −f dt²+dr²/f+r²dΩ² (its canonical tetrad is known) — covering Schwarzschild/RN/
    de Sitter/Minkowski; UNKNOWN elsewhere (off-diagonal/cosmological get no auto
    tetrad, and we never compute the heavy Weyl tensor for them)."""
    n, g, x = geo.n, geo.g, geo.coords
    if n != 4 or not g.is_diagonal():
        return UNKNOWN
    rc, th = x[1], x[2]
    f = sp.cancel(sp.together(-g[0, 0]))
    if (sp.simplify(g[1, 1] * f - 1) != 0 or sp.simplify(g[2, 2] - rc**2) != 0
            or sp.simplify(g[3, 3] - rc**2 * sp.sin(th)**2) != 0):
        return UNKNOWN
    try:
        C = weyl_tensor(geo)
        if all(C[a][b][c][d] == 0 for a in range(4) for b in range(4)
               for c in range(4) for d in range(4)):
            return "O (conformally flat)"
        s2 = sp.sqrt(2)
        tet = ([1 / f, 1, 0, 0], [sp.Rational(1, 2), -f / 2, 0, 0],
               [0, 0, 1 / (rc * s2), sp.I / (rc * s2 * sp.sin(th))],
               [0, 0, 1 / (rc * s2), -sp.I / (rc * s2 * sp.sin(th))])
        return petrov_type(weyl_scalars(C, tet))
    except Exception:
        return UNKNOWN


# ---------------------------------------------------------------------------
# the report
# ---------------------------------------------------------------------------

def analyze(metric, coords, domain=None):
    """Run the core analysis on any metric. Returns a report dict. Decides the
    solution TYPE first (cheap, numeric-prechecked) and only computes the full
    stress-energy when the metric is genuinely sourced — so vacuum metrics
    (e.g. Kerr) skip the expensive matter step that used to hang.

    `domain` (optional): {coordinate: (lo, hi)} bounding where a coordinate
    physically lives — e.g. {r: (0, R)} for a stellar interior (real only inside
    the star). It steers the energy-condition sign tests so domain-restricted
    solutions can be certified physical instead of returning UNKNOWN. Omit it and
    the analysis is exactly as before."""
    geo = Geometry(sp.Matrix(metric), list(coords))
    n = geo.n
    verdict = field_verdict(geo)
    if "Ricci-flat" in verdict:                       # pure vacuum — no matter
        desc, rho, pressures = "vacuum (empty space)", UNKNOWN, UNKNOWN
    elif "cosmological constant" in verdict:          # vacuum+Λ — matter is Λ
        Lam = sp.simplify(geo.ricci_scalar * (n - 2) / (2 * n))
        rho = sp.simplify(Lam / (8 * sp.pi))          # T^0_0 = −Λ/8π = −ρ ⇒ ρ = Λ/8π
        pressures = [sp.simplify(-rho)] * (n - 1)     # p = −ρ (w = −1)
        desc = "cosmological constant Λ (w = −1)"
    else:                                             # genuinely sourced — worth the stress-energy
        desc, rho, pressures = matter_type(geo, stress_energy(geo))
    ec = energy_conditions(rho, pressures, domain)
    physical = _all(*[ec[k] for k in ("NEC", "WEC", "DEC", "SEC")])
    sings = singularities(geo)
    return {
        "dim": n,
        "made_of": desc,
        "rho": rho,
        "pressures": pressures,
        "energy_conditions": ec,
        "physical": physical,           # all four hold? True/False/UNKNOWN
        "solves_einstein": verdict,
        "symmetries": symmetries(geo),
        "singularities": sings,
        "horizon": horizon_thermo(geo),
        "causal": causal_structure(geo, sings),
        "observables": observables(geo),
        "petrov": petrov(geo),          # algebraic type of the Weyl tensor
    }


def _mark(v):
    return "hold" if v is True else ("VIOLATED" if v is False else "UNKNOWN")


def format_report(report):
    ec = report["energy_conditions"]
    phys = ("physical (all conditions hold)" if report["physical"] is True else
            "EXOTIC (an energy condition is violated)" if report["physical"] is False
            else "UNKNOWN")
    sym = report["symmetries"]
    sym_str = (", ".join(f"∂/∂{s}" for s in sym) + f"  (≥{len(sym)} Killing vectors)"
               if sym else "none manifest")
    sings = report["singularities"]
    sing_str = ("none" if sings == [] else "UNKNOWN" if sings is UNKNOWN else
                ", ".join(f"{v} = {val}" for v, val in sings) + "  (curvature → ∞)")
    hz = report["horizon"]
    if hz is UNKNOWN:
        hz_str = "UNKNOWN"
    elif not hz:
        hz_str = "none"
    else:
        hz_str = " ; ".join(f"r_h={rh} · T={T} · S={S}" for rh, T, S in hz)
    cz = report.get("causal", {})
    sc = cz.get("singularity_character", [])
    flip = cz.get("signature_flip", None)
    cc = "; ".join(f"{v}={val} {ch.split(' (')[0]}" for v, val, ch in sc) if sc else "—"
    causal_str = f"sing {cc} · signature flip {flip}"
    obs = report.get("observables", {})
    if obs:
        bits = []
        if obs.get("photon_sphere"):
            bits.append(f"light ring r={obs['photon_sphere'][0]}")
        if obs.get("shadow") is not None:
            bits.append(f"shadow b={obs['shadow']}")
        if obs.get("isco"):
            bits.append(f"ISCO r={obs['isco'][0]}")
        obs_str = " · ".join(bits)
    else:
        obs_str = "—"
    lines = [
        f"  made of      : {report['made_of']}",
        f"  density ρ    : {report['rho']}",
        f"  pressures    : {report['pressures']}",
        f"  physical?    : {phys}   [" + ", ".join(f"{k}:{_mark(ec[k])}" for k in
                                                   ('NEC', 'WEC', 'DEC', 'SEC')) + "]",
        f"  symmetries   : {sym_str}",
        f"  singularities: {sing_str}",
        f"  causal       : {causal_str}",
        f"  observables  : {obs_str}",
        f"  horizon      : {hz_str}",
        f"  solves EFE   : {report['solves_einstein']}",
        f"  dimension    : {report['dim']}",
    ]
    return "\n".join(lines)
