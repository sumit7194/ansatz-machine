#!/usr/bin/env python3
"""Step 27 — SCALAR SOURCE: extend the engine beyond vacuum.

First rung of the field menu (v6). A minimally-coupled massless scalar φ
sources gravity. In trace-reversed (Ricci) form — same trick as D2 — the
coupled field equations are simply

    R_ab − [2Λ/(n−2)] g_ab = κ ∂_a φ ∂_b φ        (Einstein, scalar source)
    □φ = 0                                          (scalar equation of motion)

(the ½g(∂φ)² term cancels under trace reversal for a massless scalar, so we
never build the Einstein tensor). This module adds T_ab[φ] and □φ on top of
gr_engine and a three-valued verifier for the COUPLED system.

This run is the sanity gate: a CONSTANT scalar has ∂φ=0 ⇒ zero source ⇒ any
vacuum solution must still verify, and □(const)=0. Schwarzschild + φ=const
must pass; a non-constant scalar on plain Schwarzschild must FAIL (it isn't a
scalar solution). Real exact-solution validation (JNW) comes next.

Run:  .venv/bin/python scripts/27_scalar.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import (Geometry, build_ansatz_metric, R_SYM, zero_simplify,
                       numeric_spot_check, VERIFIED, REJECTED, UNPROVEN)


def box(geo, phi):
    """Covariant d'Alembertian □φ = (1/√|g|) ∂_a(√|g| g^{ab} ∂_b φ)."""
    n, g, ginv, x = geo.n, geo.g, geo.ginv, geo.coords
    detg = sp.simplify(g.det())
    sq = sp.sqrt(sp.Abs(detg))
    total = sp.S.Zero
    for a in range(n):
        flux = sq * sum(ginv[a, b] * sp.diff(phi, x[b]) for b in range(n))
        total += sp.diff(flux, x[a])
    return sp.cancel(sp.together(total / sq))


def scalar_residual(geo, phi, kappa, Lambda):
    """R_ab − [2Λ/(n−2)]g_ab − κ ∂_aφ ∂_bφ  (≡0 for a scalar solution)."""
    n, x = geo.n, geo.coords
    Ric = geo.ricci
    src = sp.zeros(n, n)
    for a in range(n):
        for b in range(a, n):
            src[a, b] = src[b, a] = kappa * sp.diff(phi, x[a]) * sp.diff(phi, x[b])
    return Ric - (2 * Lambda / (n - 2)) * geo.g - src


def verify_scalar(metric, coords, phi, kappa=sp.Integer(2), Lambda=sp.S.Zero,
                  params=()):
    """Three-valued verdict on the coupled (metric, φ) system."""
    geo = Geometry(metric, coords)
    res = scalar_residual(geo, phi, kappa, Lambda)
    eom = box(geo, phi)
    free = list(coords) + list(params)
    ok_e, worst_e = numeric_spot_check(res, coords, params)
    if not ok_e:
        return REJECTED, f"Einstein residual {worst_e:.2e}"
    # numeric check on the scalar EOM
    import random
    rng = random.Random(1)
    for _ in range(5):
        sub = {s: sp.Rational(rng.randint(11, 99), rng.randint(7, 13)) for s in free}
        try:
            if abs(complex(eom.subs(sub).evalf(30))) > 1e-8:
                return REJECTED, "scalar EOM nonzero numerically"
        except (TypeError, ValueError):
            return REJECTED, "scalar EOM not evaluable"
    stuck = []
    for i in range(geo.n):
        for j in range(i, geo.n):
            if zero_simplify(res[i, j]) != 0:
                stuck.append(("E", i, j))
    if zero_simplify(eom) != 0:
        stuck.append(("EOM",))
    if not stuck:
        return VERIFIED, "R_ab−Λ−κ∂φ∂φ ≡ 0 and □φ ≡ 0 symbolically"
    return UNPROVEN, f"numerically ok but {len(stuck)} piece(s) stuck: {stuck[:2]}"


def main():
    t, r = sp.Symbol("t", real=True), R_SYM
    M = sp.Symbol("M", positive=True)
    metric, coords, _ = build_ansatz_metric(4, 1 - 2 * M / r)  # Schwarzschild

    print("SCALAR SOURCE — sanity gate\n")
    phi_const = sp.Integer(7)
    v, d = verify_scalar(metric, coords, phi_const)
    print(f"  Schwarzschild + φ=const : {v}  ({d})")
    ok1 = v == VERIFIED

    phi_bad = r  # a non-constant scalar that is NOT sourced correctly here
    v2, d2 = verify_scalar(metric, coords, phi_bad)
    print(f"  Schwarzschild + φ=r     : {v2}  ({d2})")
    ok2 = v2 == REJECTED

    passed = ok1 and ok2
    print(f"\nSCALAR SANITY: {'PASSED ✅' if passed else 'FAILED ❌'}"
          + ("  (const scalar leaves vacuum intact; a bogus scalar is rejected)"
             if passed else ""))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
