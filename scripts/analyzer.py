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

def _sign(expr):
    """+1 / −1 / 0 / None — sign of expr over the physical domain (positive
    parameters & coordinates). Symbolic when SymPy can decide, else sampled;
    None (UNKNOWN) if a sample is not real-evaluable or the sign is mixed."""
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
    for _ in range(60):
        sub = {s: sp.Rational(rng.randint(1, 25), rng.randint(1, 6)) for s in free}
        try:
            v = float(e.subs(sub))
        except (TypeError, ValueError):
            return None
        if v > 1e-12:
            seen.add(1)
        elif v < -1e-12:
            seen.add(-1)
        else:
            seen.add(0)
    if seen == {1}:
        return 1
    if seen == {-1}:
        return -1
    if seen <= {0}:
        return 0
    return None        # mixed sign over the domain ⇒ cannot give one verdict


def _nonneg(expr):
    s = _sign(expr)
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


def energy_conditions(rho, pressures):
    """NEC / WEC / DEC / SEC, three-valued, from (ρ, pressures)."""
    if rho is UNKNOWN:
        return {k: UNKNOWN for k in ("NEC", "WEC", "DEC", "SEC")}
    nec = _all(*[_nonneg(rho + p) for p in pressures])
    wec = _all(nec, _nonneg(rho))
    dec = _all(_nonneg(rho), *[_nonneg(rho - p) for p in pressures],
               *[_nonneg(rho + p) for p in pressures])
    sec = _all(nec, _nonneg(rho + sum(pressures)))
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
    timelike direction rotating ∂_t → ∂_r. Sampled over the domain."""
    gtt = geo.g[0, 0]
    fs = list(gtt.free_symbols)
    if not fs:
        return False
    rng = random.Random(0)
    signs = set()
    for _ in range(60):
        sub = {s: sp.Rational(rng.randint(1, 40), rng.randint(1, 5)) for s in fs}
        try:
            v = float(gtt.subs(sub))
        except (TypeError, ValueError):
            continue
        if v > 1e-9:
            signs.add(1)
        elif v < -1e-9:
            signs.add(-1)
    return (1 in signs) and (-1 in signs)


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


# ---------------------------------------------------------------------------
# the report
# ---------------------------------------------------------------------------

def analyze(metric, coords):
    """Run the core analysis on any metric. Returns a report dict. Decides the
    solution TYPE first (cheap, numeric-prechecked) and only computes the full
    stress-energy when the metric is genuinely sourced — so vacuum metrics
    (e.g. Kerr) skip the expensive matter step that used to hang."""
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
    ec = energy_conditions(rho, pressures)
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
    lines = [
        f"  made of      : {report['made_of']}",
        f"  density ρ    : {report['rho']}",
        f"  pressures    : {report['pressures']}",
        f"  physical?    : {phys}   [" + ", ".join(f"{k}:{_mark(ec[k])}" for k in
                                                   ('NEC', 'WEC', 'DEC', 'SEC')) + "]",
        f"  symmetries   : {sym_str}",
        f"  singularities: {sing_str}",
        f"  causal       : {causal_str}",
        f"  horizon      : {hz_str}",
        f"  solves EFE   : {report['solves_einstein']}",
        f"  dimension    : {report['dim']}",
    ]
    return "\n".join(lines)
