#!/usr/bin/env python3
"""Step 02 — the FINGERPRINT library (novelty filter).

The costume problem: relativists keep "discovering" known solutions in
new coordinates (MacCallum keeps a top-ten rediscovered list). Two
metrics related by a coordinate change are the same program compiled
with different register names — you can't diff the source, you need a
coordinate-free fingerprint.

The fingerprint: scalar curvature invariants. Coordinate changes can't
touch them. We use:
    R      — Ricci scalar (fixes Λ: R = 2nΛ/(n-2) in vacuum-with-Λ)
    K      — Kretschmann R_abcd R^abcd
    G1     — |∇K|² = g^ab ∂_a K ∂_b K  (a DIFFERENTIAL invariant)
The pair (K, G1) traces a coordinate-free CURVE through invariant
space as you move through the spacetime — the poor man's Cartan
invariant. Same solution in any disguise → same curve. Different
curve → provably different spacetime (invariants differing is a
sufficient condition for inequivalence).

HONEST LIMITS (encoded, not hidden):
 - Invariants are necessary, not sufficient: matching curves do NOT
   prove equivalence. A match is reported as KNOWN_LIKELY, not "same" —
   but it is no longer the last word: Cartan–Karlhede IS implemented now
   (scripts/ck.py, §116–§118), and §118 upgrades these verdicts to
   PROVEN_KNOWN / PROVEN_NEW_vs_CATALOG by decision procedure.
 - Blind spot: metrics whose invariants are all CONSTANT (de Sitter,
   BTZ — anything locally homogeneous / CSI) or all ZERO (flat space,
   pp-waves / VSI) cannot be fingerprinted this way. The filter says
   so explicitly instead of concluding anything.

Verdicts:
    FLAT_OR_VSI   — all invariants zero: Minkowski or a pp-wave; CK needed.
    BLIND_SPOT    — invariants constant: CSI class; CK needed.
    KNOWN_LIKELY(name, params) — curve matches a catalog entry.
    CANDIDATE_NEW — vacuum-verified AND curve matches nothing known.

Run the self-test battery:  .venv/bin/python scripts/02_fingerprints.py
"""

import json
import os
import time

import sympy as sp

from gr_engine import Geometry, R_SYM, build_ansatz_metric

DISCOVERIES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "catalog_discoveries.json")

# ---------------------------------------------------------------------------
# Fingerprinting
# ---------------------------------------------------------------------------

FLAT_OR_VSI = "FLAT_OR_VSI"
BLIND_SPOT = "BLIND_SPOT"
KNOWN_LIKELY = "KNOWN_LIKELY"
CANDIDATE_NEW = "CANDIDATE_NEW"


def depends_on(expr, coords):
    return [x for x in coords if expr.has(x)]


class Profile:
    """The invariant fingerprint of one geometry: R, K, G1 = |∇K|²."""

    def __init__(self, geo: Geometry):
        self.geo = geo
        self.n = geo.n
        self.R = sp.simplify(geo.ricci_scalar)
        self.K = geo.kretschmann
        self.K_coords = depends_on(self.K, geo.coords)
        self.G1 = (geo.grad_invariant(self.K) if self.K_coords
                   else sp.S.Zero)


class StoredProfile:
    """Profile rebuilt from persisted expressions — skips the expensive
    Geometry computation (measured: 29 min per build_catalog with 12
    families up to n=8)."""

    def __init__(self, n, R, K, G1):
        self.n = n
        self.R = R
        self.K = K
        self.K_coords = [R_SYM] if K.has(R_SYM) else []
        self.G1 = G1


class CatalogEntry:
    """A known solution family: symbolic profile with one free shape
    parameter (Λ-type parameters are fixed directly by R)."""

    def __init__(self, name, metric, coords, shape_param, Lambda_param=None,
                 Lambda_from_R=None, sample_coord=None, profile=None):
        self.name = name
        self.profile = profile or Profile(Geometry(metric, coords))
        self.coords = coords
        self.shape_param = shape_param        # e.g. M
        self.Lambda_param = Lambda_param      # e.g. Λ symbol in the profile
        self.Lambda_from_R = Lambda_from_R    # lambda R_value -> Λ value
        # the coordinate the invariants vary along (curve parameter)
        cs = self.profile.K_coords
        self.curve_coord = sample_coord or (cs[0] if cs else None)


def _solve_coord_1d(fK, K_target, lo=0.05, hi=500.0, ngrid=90):
    """All roots of fK(x) = K_target on [lo, hi] by geometric-grid scan
    + bisection. Pure float math — fast."""
    import math
    xs = [lo * (hi / lo) ** (i / (ngrid - 1)) for i in range(ngrid)]
    vals = []
    for x in xs:
        try:
            v = fK(x) - K_target
            vals.append(v if math.isfinite(v) else None)
        except Exception:
            vals.append(None)
    roots = []
    for i in range(len(xs) - 1):
        a, b = vals[i], vals[i + 1]
        if a is None or b is None or a * b > 0:
            continue
        x0, x1, va = xs[i], xs[i + 1], a
        for _ in range(80):
            xm = math.sqrt(x0 * x1)
            try:
                vm = fK(xm) - K_target
            except Exception:
                break
            if va * vm <= 0:
                x1 = xm
            else:
                x0, va = xm, vm
        roots.append(math.sqrt(x0 * x1))
    return roots


def _nsolve_pair(K_expr, G1_expr, K_val, G1_val, coord, param):
    """Solve K(coord,param)=K_val, G1(coord,param)=G1_val for both
    unknowns. Returns ALL distinct real param values found; every
    candidate gets validated against the full sample set by the caller.

    Method: nested 1D bisection, NO Newton. (Measured failure: with
    invariants like G1 ∝ p⁴(p+r³)/r²⁵ the Jacobian is so steep that 2D
    Newton stalls at ~1e-6 from every start.) For each trial parameter
    on a signed log-grid, solve the K-equation for the coordinate by
    bisection; the relative G1 mismatch φ(p) then changes sign at a true
    family match, and a second bisection pins the parameter. The sign of
    the parameter floats freely — the same family covers both branches
    (e.g. negative-mass Schwarzschild, a naked singularity, still exact
    vacuum)."""
    FK = sp.lambdify((coord, param), K_expr, modules="math")
    FG = sp.lambdify((coord, param), G1_expr, modules="math")

    def phi(p):
        """Relative G1 mismatch on the K-surface (closest branch)."""
        best = None
        for c in _solve_coord_1d(lambda x: FK(x, p), K_val):
            try:
                v = FG(c, p) / G1_val - 1
            except Exception:
                continue
            if best is None or abs(v) < abs(best):
                best = v
        return best

    found = []
    for sgn in (1, -1):
        grid = [sgn * 1e-3 * (1e6) ** (i / 79) for i in range(80)]
        vals = [(p, phi(p)) for p in grid]
        for (pa, va), (pb, vb) in zip(vals, vals[1:]):
            if va is None or vb is None or va * vb > 0:
                continue
            lo, hi, vlo = pa, pb, va
            for _ in range(100):
                mid = sgn * (abs(lo) * abs(hi)) ** 0.5
                vm = phi(mid)
                if vm is None:
                    break
                if vlo * vm <= 0:
                    hi = mid
                else:
                    lo, vlo = mid, vm
            p_hat = (lo + hi) / 2
            vfin = phi(p_hat)
            if vfin is not None and abs(vfin) < 1e-6 \
                    and not any(abs(p_hat - q) < 1e-9 * max(abs(q), 1)
                                for q in found):
                found.append(p_hat)
    return found


def _curve_matches(entry, samples, rel_tol=1e-6):
    """Does the candidate's sampled (K, G1) curve lie on the entry's?
    Fit the shape parameter from the first sample, check the rest."""
    K_e, G1_e = entry.profile.K, entry.profile.G1
    coord, param = entry.curve_coord, entry.shape_param

    K1, G11 = samples[0]
    for p_hat in _nsolve_pair(K_e, G1_e, K1, G11, coord, param):
        FKp = sp.lambdify(coord, K_e.subs(param, p_hat), modules="math")
        FGp = sp.lambdify(coord, G1_e.subs(param, p_hat), modules="math")
        all_ok = True
        for K_i, G1_i in samples[1:]:
            ok = False
            # bisection over the full coordinate range — Newton from
            # fixed starts misses roots outside its basin (measured:
            # samples at r≈0.7 were unreachable from starts ≥ 2)
            for c_hat in _solve_coord_1d(FKp, K_i):
                try:
                    g = FGp(c_hat)
                except Exception:
                    continue
                if abs(g - G1_i) <= rel_tol * max(abs(G1_i), 1e-30):
                    ok = True
                    break
            if not ok:
                all_ok = False
                break
        if all_ok:
            return True, p_hat
    return False, None


def classify(geo: Geometry, catalog, n_samples=4, seed=0):
    """Fingerprint a (numeric-parameter) geometry against the catalog.
    Returns (verdict, detail)."""
    prof = Profile(geo)

    if prof.K == 0 and prof.R == 0:
        return FLAT_OR_VSI, ("all polynomial invariants vanish — flat "
                             "space or a VSI metric (pp-wave); invariants "
                             "are blind here — escalate to Cartan–Karlhede "
                             "(scripts/ck.py; §118 adjudicates this case)")
    if not prof.K_coords:
        return BLIND_SPOT, (f"invariants constant (K={prof.K}, R={prof.R}) "
                            "— CSI class (de Sitter / BTZ / homogeneous); "
                            "invariants are blind here, CK needed")
    if len(prof.K_coords) > 1:
        return CANDIDATE_NEW, (f"K varies along {len(prof.K_coords)} "
                               f"coordinates {prof.K_coords} — multi-"
                               "dimensional invariant variation; no "
                               "curve-comparison against 1D catalog "
                               "entries possible, inspect manually")

    # sample the candidate's (K, G1) curve WHERE IT VARIES. Random radii
    # fail when K has a constant floor (e.g. Schwarzschild-de Sitter:
    # K = 8Λ²/3 + 48M²/r⁶ — at large r the mass term is a 1e-5 ripple
    # on the Λ term and the curve fit is hopelessly ill-conditioned).
    # Greedy pick: anchor at max |K|, then only keep points whose K
    # differs ≥10% from every point already chosen.
    import math
    x = prof.K_coords[0]
    FKc = sp.lambdify(x, prof.K, modules="math")
    FGc = sp.lambdify(x, prof.G1, modules="math")
    grid = [0.7 * (60 / 0.7) ** (i / 119) for i in range(120)]
    pts = []
    for rr in grid:
        try:
            kv, gv = FKc(rr), FGc(rr)
            if math.isfinite(kv) and math.isfinite(gv) \
                    and abs(kv) > 1e-18:
                pts.append((kv, gv))
        except Exception:
            continue
    pts.sort(key=lambda p: -abs(p[0]))
    samples = []
    for p in pts:
        if len(samples) >= n_samples:
            break
        if all(abs(p[0] - c[0]) > 0.1 * max(abs(c[0]), 1e-18)
               for c in samples):
            samples.append(p)
    if len(samples) < 3:
        return CANDIDATE_NEW, ("could not find enough invariant-curve "
                               "variation to sample — inspect manually")

    # candidate's R must match the entry's R (fixes Λ-type parameters)
    R_c = complex(prof.R.evalf(30)).real if prof.R.is_number else None

    for entry in catalog:
        if entry.profile.n != prof.n:
            continue
        # check R compatibility
        e_R = entry.profile.R
        subs = {}
        if entry.Lambda_param is not None:
            if R_c is None:
                continue
            lam = entry.Lambda_from_R(R_c)
            subs[entry.Lambda_param] = lam
            if abs(complex(e_R.subs(subs).evalf(30)) - R_c) > 1e-8 * max(abs(R_c), 1):
                continue
        else:
            # entry has a FIXED R (0 for Λ=0 entries; a nonzero constant
            # for grown fixed-Λ families) — sectors must agree
            if not e_R.is_number or R_c is None:
                continue
            e_R_num = complex(e_R.evalf(30)).real
            if abs(R_c - e_R_num) > 1e-8 * max(abs(e_R_num), 1.0):
                continue
        K_e = entry.profile.K.subs(subs)
        G1_e = entry.profile.G1.subs(subs)
        probe = CatalogEntry.__new__(CatalogEntry)
        probe.name, probe.shape_param = entry.name, entry.shape_param
        probe.curve_coord = entry.curve_coord
        probe.profile = type("P", (), {"K": K_e, "G1": G1_e})
        ok, p_hat = _curve_matches(probe, samples)
        if ok:
            return KNOWN_LIKELY, (f"invariant curve matches {entry.name} "
                                  f"with {entry.shape_param}≈{p_hat:.6g} "
                                  "(necessary-condition match — not a "
                                  "proof of equivalence)")
    return CANDIDATE_NEW, ("vacuum-verified and invariant curve matches "
                           "no catalog entry — escalate to human")


# ---------------------------------------------------------------------------
# The known-solution catalog (symbolic shape parameters)
# ---------------------------------------------------------------------------

def build_catalog(include_discoveries=True):
    """The base (hand-verified) catalog, plus — by default — every
    family the machine has discovered and generalized itself
    (catalog_discoveries.json, written by 05_generalize.py). Pass
    include_discoveries=False for the frozen memoryless machine
    (used by the 04 campaign regression)."""
    t, r, th, ph, z = sp.symbols("t r theta phi z", real=True)
    M, mu, lam = sp.symbols("M mu lambda_", positive=True)

    f = 1 - 2 * M / r
    schw = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2)

    # Schwarzschild–de Sitter: Λ fixed by R = 4Λ (n=4), M is the shape param
    fsds = 1 - 2 * M / r - lam * r**2 / 3
    sds = sp.diag(-fsds, 1 / fsds, r**2, r**2 * sp.sin(th)**2)

    ft = 1 - mu / r**2
    tang = sp.diag(-ft, 1 / ft, r**2, r**2 * sp.sin(th)**2,
                   r**2 * sp.sin(th)**2 * sp.sin(ph)**2)

    catalog = [
        CatalogEntry("Schwarzschild (3+1)", schw, [t, r, th, ph],
                     shape_param=M),
        CatalogEntry("Schwarzschild-de Sitter (3+1)", sds, [t, r, th, ph],
                     shape_param=M, Lambda_param=lam,
                     Lambda_from_R=lambda Rv: Rv / 4),
        CatalogEntry("Schwarzschild-Tangherlini (4+1)", tang,
                     [t, r, th, ph, z], shape_param=mu),
    ]

    if include_discoveries and os.path.exists(DISCOVERIES_PATH):
        with open(DISCOVERIES_PATH) as fh:
            data = json.load(fh)
        changed = False
        for d in data:
            if len(d["params"]) != 1:
                continue  # curve matcher handles one shape param;
                # multi-param grown families need CK-grade tooling
            psym = sp.Symbol(d["params"][0], real=True)
            f = sp.sympify(d["f"], locals={"r": R_SYM,
                                           d["params"][0]: psym})
            metric, coords, _ = build_ansatz_metric(d["n"], f)
            if "profile" in d:
                # fast path: srepr round-trips symbols WITH assumptions
                prof = StoredProfile(
                    d["n"],
                    sp.sympify(d["profile"]["R"]),
                    sp.sympify(d["profile"]["K"]),
                    sp.sympify(d["profile"]["G1"]))
                entry = CatalogEntry(d["name"], metric, coords,
                                     shape_param=psym, profile=prof)
            else:
                # self-healing cache: compute once, persist forever
                entry = CatalogEntry(d["name"], metric, coords,
                                     shape_param=psym)
                d["profile"] = {"R": sp.srepr(entry.profile.R),
                                "K": sp.srepr(entry.profile.K),
                                "G1": sp.srepr(entry.profile.G1)}
                changed = True
            catalog.append(entry)
        if changed:
            with open(DISCOVERIES_PATH, "w") as fh:
                json.dump(data, fh, indent=2)
    return catalog


# ---------------------------------------------------------------------------
# Self-test battery: costumes must be unmasked, blind spots declared
# ---------------------------------------------------------------------------

def main():
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    rho = sp.symbols("rho", positive=True)

    print("Building catalog (symbolic fingerprints of known solutions)...")
    t0 = time.time()
    catalog = build_catalog()
    print(f"  catalog ready ({time.time() - t0:.1f}s): "
          + ", ".join(e.name for e in catalog))

    results = []

    def case(name, expected_verdict, expect_substr, geo):
        t1 = time.time()
        verdict, detail = classify(geo, catalog)
        ok = verdict == expected_verdict and (expect_substr in detail
                                              if expect_substr else True)
        results.append(ok)
        mark = "✓" if ok else "✗✗ EXPECTATION FAILED"
        print(f"  {mark} {name}: {verdict} — {detail} "
              f"({time.time() - t1:.1f}s)")

    print("\n== Costume tests: disguised knowns must be unmasked ==")

    # Schwarzschild in ISOTROPIC coordinates (M=1): different radial
    # coordinate, conformally flat spatial part — a real costume.
    Miso = sp.Integer(1)
    A = 1 + Miso / (2 * rho)
    B = 1 - Miso / (2 * rho)
    iso = sp.diag(-(B / A)**2, A**4, A**4 * rho**2,
                  A**4 * rho**2 * sp.sin(th)**2)
    case("Schwarzschild in isotropic coords (M=1)", KNOWN_LIKELY,
         "Schwarzschild (3+1)", Geometry(iso, [t, rho, th, ph]))

    # Schwarzschild in PAINLEVÉ-GULLSTRAND form (M=2): off-diagonal,
    # regular at the horizon — a different kind of costume.
    Mpg = sp.Integer(2)
    pg = sp.Matrix([
        [-(1 - 2 * Mpg / r), sp.sqrt(2 * Mpg / r), 0, 0],
        [sp.sqrt(2 * Mpg / r), 1, 0, 0],
        [0, 0, r**2, 0],
        [0, 0, 0, r**2 * sp.sin(th)**2]])
    case("Schwarzschild in Painlevé-Gullstrand (M=2)", KNOWN_LIKELY,
         "Schwarzschild (3+1)", Geometry(pg, [t, r, th, ph]))

    # Schwarzschild-de Sitter (M=1, Λ=0.03): must match SdS, not Schw.
    lam_n = sp.Rational(3, 100)
    fsds = 1 - 2 / r - lam_n * r**2 / 3
    sds_n = sp.diag(-fsds, 1 / fsds, r**2, r**2 * sp.sin(th)**2)
    case("Schwarzschild-de Sitter (M=1, Λ=0.03)", KNOWN_LIKELY,
         "Schwarzschild-de Sitter", Geometry(sds_n, [t, r, th, ph]))

    print("\n== Genuinely-different test: must NOT match ==")

    # 4+1 Tangherlini (μ=1): no 4D entry can claim it (dimension gate),
    # and it must match the 5D entry.
    z = sp.symbols("z", real=True)
    ft = 1 - 1 / r**2
    tang_n = sp.diag(-ft, 1 / ft, r**2, r**2 * sp.sin(th)**2,
                     r**2 * sp.sin(th)**2 * sp.sin(ph)**2)
    case("Tangherlini 4+1 (μ=1)", KNOWN_LIKELY, "Tangherlini",
         Geometry(tang_n, [t, r, th, ph, z]))

    print("\n== Blind spots: must be DECLARED, not bluffed ==")

    # Minkowski in spherical coords: curved-looking components, flat space.
    mink = sp.diag(-1, 1, r**2, r**2 * sp.sin(th)**2)
    case("Minkowski in spherical coords", FLAT_OR_VSI, None,
         Geometry(mink, [t, r, th, ph]))

    # de Sitter: maximally symmetric — all invariants constant.
    fds = 1 - r**2 / 100
    ds = sp.diag(-fds, 1 / fds, r**2, r**2 * sp.sin(th)**2)
    case("de Sitter (Λ=0.03)", BLIND_SPOT, "CSI",
         Geometry(ds, [t, r, th, ph]))

    # BTZ (M=1, ℓ=5): locally AdS₃ — the famous quotient black hole.
    fb = r**2 / 25 - 1
    btz = sp.diag(-fb, 1 / fb, r**2)
    case("BTZ 2+1 (M=1, ℓ=5)", BLIND_SPOT, "CSI",
         Geometry(btz, [t, r, ph]))

    print(f"\n{'ALL EXPECTATIONS MET ✅' if all(results) else 'EXPECTATION FAILURES ❌'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
