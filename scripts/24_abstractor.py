#!/usr/bin/env python3
"""Step 24 — the ABSTRACTOR: recover the meta-law behind a family of
verified solutions, including its dimension dependence.

The catalog stores many proved metrics, one per (n, Λ) rung. Each earlier
step generalized ONE constant within ONE rung (05_generalize). This step
goes a level up: read the whole family and recover the SINGLE law
f(n, Λ) that produces every rung — the exponent and coefficients as
functions of the dimension n — using exact symbolic fitting only
(search the simplest functional forms, solve over the rationals; no
numeric "weights", no neural net, glass-box throughout).

This run is the UNIT TEST: pointed at the static-vacuum catalog, whose
answer is known (Tangherlini–(A)dS), it must rediscover the exponent
n−3 and the cosmological coefficient −2Λ/((n−1)(n−2)) WITHOUT being told
them — and then PREDICT a held-out dimension. Only once it passes here
is it trustworthy to point at families whose law is unknown (e.g. the
EdGB fit coefficients).

Run:  .venv/bin/python scripts/24_abstractor.py
"""

import json
import os

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(_here, "..", "catalog_discoveries.json")

r = sp.Symbol("r", positive=True)
c1 = sp.Symbol("c1", real=True)
N = sp.Symbol("N")  # the dimension, carried as a symbol in the recovered law


def decompose(f_expr):
    """Split one rung's f(r) into (constant, mass-term power p, r²-coeff).

    These metrics have the shape  const + c1·r^(−p) + β·r²  — but we do NOT
    assume that; we read each piece off symbolically so a wrong shape would
    show up as a leftover."""
    f = sp.expand(f_expr)
    mass = f.coeff(c1)                       # coefficient of the free param = r^(−p)
    p = -sp.Add(*[t for t in [mass]])         # placeholder; real power below
    # power of r in the mass term (mass is r**(−p))
    base, exp = mass.as_base_exp()
    p = -exp if base == r else sp.nan
    rest = sp.expand(f - c1 * mass)          # everything except the mass term
    beta = rest.coeff(r, 2)                  # coefficient of r²  (0 when Λ=0)
    const = rest.coeff(r, 0)                 # constant term
    leftover = sp.expand(rest - const - beta * r**2)  # must be 0 for our shape
    return const, p, beta, leftover


def recover_poly(points, var, max_deg=4):
    """Lowest-degree polynomial in `var` that fits ALL (x,y) points exactly
    over the rationals, or None. Occam's razor: try degree 0,1,2,… and stop
    at the first that reproduces every point exactly."""
    # dedupe by x: each dimension recurs once per Λ sector with the SAME
    # value, and repeated x-values make the fit's linear system singular.
    # (A genuine disagreement at the same x would mean the quantity isn't a
    # function of n alone — surface it rather than hide it.)
    seen = {}
    for x, y in points:
        xr, yv = sp.Rational(x), sp.sympify(y)
        if xr in seen and sp.simplify(seen[xr] - yv) != 0:
            raise ValueError(f"inconsistent values at n={xr}: {seen[xr]} vs {yv}")
        seen[xr] = yv
    pts = sorted(seen.items(), key=lambda t: t[0])
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    for deg in range(0, min(max_deg, len(xs) - 1) + 1):
        a = sp.symbols(f"a0:{deg+1}")
        poly = sum(a[k] * var**k for k in range(deg + 1))
        sol = sp.solve([poly.subs(var, xs[i]) - ys[i] for i in range(deg + 1)],
                       a, dict=True)
        if not sol:
            continue
        cand = sp.expand(poly.subs(sol[0]))
        if all(sp.simplify(cand.subs(var, xs[i]) - ys[i]) == 0
               for i in range(len(xs))):
            return cand
    return None


def recover_coeff_law(points, var):
    """Recover y(n) that may be a polynomial OR a reciprocal-polynomial
    (rational). Tries y directly, then 1/y — enough to catch the
    (n−1)(n−2)-type denominators that show up in cosmological terms."""
    direct = recover_poly(points, var)
    if direct is not None:
        return direct, "polynomial"
    inv = recover_poly([(x, 1 / sp.sympify(y)) for x, y in points], var)
    if inv is not None:
        return sp.simplify(1 / inv), "reciprocal-polynomial"
    return None, None


def load_family():
    data = json.load(open(CATALOG))
    fam = []
    for d in data:
        if len(d.get("params", [])) != 1:
            continue
        f = sp.sympify(d["f"], locals={"r": r, d["params"][0]: c1})
        fam.append({"n": d["n"], "Lambda": sp.sympify(d["Lambda"]), "f": f,
                    "name": d["name"]})
    return fam


def abstract(fam, verbose=True):
    """Recover f(N, Λ) from a family. Returns (law, pieces) or (None, why)."""
    exp_pts, const_pts, lam_pts, bad = [], [], [], []
    for e in fam:
        const, p, beta, leftover = decompose(e["f"])
        if leftover != 0 or p is sp.nan:
            bad.append((e["name"], leftover))
            continue
        exp_pts.append((e["n"], p))
        const_pts.append((e["n"], const))
        if e["Lambda"] != 0:
            lam_pts.append((e["n"], sp.simplify(beta / e["Lambda"])))
    if bad:
        return None, f"unexpected shape in {len(bad)} rungs: {bad[:2]}"

    exp_law = recover_poly(exp_pts, N)
    const_law = recover_poly(const_pts, N)
    lam_law, kind = recover_coeff_law(lam_pts, N) if lam_pts else (sp.S.Zero, "none")
    if exp_law is None or const_law is None or (lam_pts and lam_law is None):
        return None, "no low-degree exact fit found"

    lam = sp.Symbol("Lambda")
    law = const_law + c1 * r**(-exp_law) + lam_law * lam * r**2
    pieces = {"exponent": exp_law, "constant": const_law,
              "lambda_coeff": sp.factor(lam_law), "lambda_kind": kind}
    if verbose:
        print("  recovered law:  f(N, Λ) = "
              f"{const_law} + c1·r^(−({exp_law})) + ({sp.factor(lam_law)})·Λ·r²")
        print(f"    mass-term exponent p(N) = {exp_law}")
        print(f"    cosmological coeff      = {sp.factor(lam_law)}·Λ  "
              f"({kind})")
    return law, pieces


def instantiate(law, n, Lambda):
    return sp.expand(law.subs({N: n, sp.Symbol("Lambda"): Lambda}))


def main():
    fam = load_family()
    print(f"ABSTRACTOR — read {len(fam)} verified rungs "
          f"(n = {min(e['n'] for e in fam)}..{max(e['n'] for e in fam)}, "
          f"3 Λ sectors)\n")

    print("== Step 1–2: recover the meta-law from ALL rungs ==")
    law, info = abstract(fam)
    if law is None:
        print(f"  ✗ FAILED: {info}")
        return 1

    print("\n== Step 3a: must reproduce every rung EXACTLY ==")
    ok = 0
    for e in fam:
        got = instantiate(law, e["n"], e["Lambda"])
        if sp.simplify(got - e["f"]) == 0:
            ok += 1
        else:
            print(f"  ✗ MISMATCH {e['name'][:34]}: got {got}")
    print(f"  {ok}/{len(fam)} rungs reproduced exactly "
          f"{'✓' if ok == len(fam) else '✗'}")

    print("\n== Step 3b: PREDICT a held-out dimension (leave-one-out) ==")
    dims = sorted({e["n"] for e in fam})
    pred_ok = True
    for hold in dims:
        train = [e for e in fam if e["n"] != hold]
        test = [e for e in fam if e["n"] == hold]
        law_h, _ = abstract(train, verbose=False)
        if law_h is None:
            print(f"  n={hold}: could not recover law from the rest ✗")
            pred_ok = False
            continue
        good = all(sp.simplify(instantiate(law_h, t["n"], t["Lambda"]) - t["f"]) == 0
                   for t in test)
        pred_ok = pred_ok and good
        print(f"  hold out {hold-1}+1 dims → law from other {len(dims)-1} "
              f"dims predicts it: {'✓' if good else '✗'}")

    passed = (ok == len(fam)) and pred_ok
    print(f"\nABSTRACTOR UNIT TEST: {'PASSED ✅' if passed else 'FAILED ❌'}")
    if passed:
        print("  → recovered Tangherlini–(A)dS unaided AND predicted held-out"
              " dimensions. The abstractor is trustworthy; safe to point at"
              " families whose law is unknown (e.g. EdGB fit coefficients).")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
