#!/usr/bin/env python3
"""Step 28 — MAXWELL (electric) SOURCE: charged black holes.

Second rung of the v6 field menu. An electromagnetic field A_a sources
gravity. In 4D the EM stress-energy is TRACELESS, so the Ricci form holds
cleanly again (R = 0 ⇒ R_ab = κ T_ab) — and the metric is RATIONAL in r
(no fractional powers), so none of the JNW branch-cut wall.

    F_ab = ∂_a A_b − ∂_b A_a
    T_ab = F_ac F_b{}^c − ¼ g_ab F_cd F^cd
    R_ab = κ T_ab          (4D, traceless source)
    ∇_a F^{ab} = 0          (Maxwell)

Validation: Reissner–Nordström  f = 1 − 2M/r + Q²/r²,  A_t = Q/r.
Let κ be symbolic and have the engine recover it (like it recovered JNW's
γ²+2κC²=1). Two free PRIMARY hairs expected: M and Q.

Run:  .venv/bin/python scripts/28_maxwell.py
"""

import os
import sys
import random

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import (Geometry, build_ansatz_metric, R_SYM, zero_simplify,
                       numeric_spot_check, VERIFIED, REJECTED, UNPROVEN)


def faraday(A, coords):
    n = len(coords)
    F = sp.zeros(n, n)
    for a in range(n):
        for b in range(n):
            F[a, b] = sp.diff(A[b], coords[a]) - sp.diff(A[a], coords[b])
    return F


def em_stress(geo, F):
    """T_ab = F_ac F_b{}^c − ¼ g_ab F_cd F^cd."""
    n, g, ginv = geo.n, geo.g, geo.ginv
    Fud = [[sum(ginv[c, d] * F[b, d] for d in range(n)) for c in range(n)]
           for b in range(n)]               # F_b{}^c
    Fsq = sum(F[c, d] * sum(ginv[c, a] * ginv[d, e] * F[a, e]
                            for a in range(n) for e in range(n))
              for c in range(n) for d in range(n))   # F_cd F^cd
    T = sp.zeros(n, n)
    for a in range(n):
        for b in range(a, n):
            t = sum(F[a, c] * Fud[b][c] for c in range(n)) \
                - sp.Rational(1, 4) * g[a, b] * Fsq
            T[a, b] = T[b, a] = sp.cancel(sp.together(t))
    return T


def maxwell_div(geo, F, weight=None):
    """∇_a(W F^{ab}) via the Christoffel form (rational; avoids √|g| Abs):
    for antisymmetric F, ∇_a(W F^{ab}) = ∂_a(W F^{ab}) + Γ^a_{ac}(W F^{cb})
    (the Γ^b_{ac}F^{ac} term vanishes by antisymmetry). W defaults to 1."""
    n, ginv, x = geo.n, geo.ginv, geo.coords
    Gam = geo.christoffel
    W = sp.Integer(1) if weight is None else weight
    Fuu = [[sum(ginv[a, c] * ginv[b, d] * F[c, d] for c in range(n) for d in range(n))
            for b in range(n)] for a in range(n)]
    trace = [sum(Gam[a][a][c] for a in range(n)) for c in range(n)]  # Γ^a_{ac}
    out = []
    for b in range(n):
        div = sum(sp.diff(W * Fuu[a][b], x[a]) for a in range(n)) \
            + sum(trace[c] * W * Fuu[c][b] for c in range(n))
        out.append(sp.cancel(sp.together(div)))
    return out


def verify_em(metric, coords, A, kappa, Lambda=sp.S.Zero, params=()):
    geo = Geometry(metric, coords)
    F = faraday(A, coords)
    T = em_stress(geo, F)
    res = geo.ricci - (2 * Lambda / (geo.n - 2)) * geo.g - kappa * T
    div = maxwell_div(geo, F)
    ok, worst = numeric_spot_check(res, coords, params)
    if not ok:
        return REJECTED, f"Einstein residual {worst:.2e}"
    rng = random.Random(2)
    for _ in range(5):
        sub = {s: sp.Rational(rng.randint(11, 99), rng.randint(7, 13))
               for s in list(coords) + list(params)}
        for d in div:
            try:
                if abs(complex(d.subs(sub).evalf(30))) > 1e-8:
                    return REJECTED, "Maxwell ∇F nonzero"
            except (TypeError, ValueError):
                return REJECTED, "Maxwell not evaluable"
    stuck = sum(1 for i in range(geo.n) for j in range(i, geo.n)
                if zero_simplify(res[i, j]) != 0)
    stuck += sum(1 for d in div if zero_simplify(d) != 0)
    if stuck == 0:
        return VERIFIED, "R_ab=κT_ab and ∇F=0 symbolically"
    return UNPROVEN, f"numerically ok, {stuck} piece(s) stuck"


def main():
    t, r = sp.Symbol("t", real=True), R_SYM
    M, Q = sp.symbols("M Q", positive=True)
    f = 1 - 2 * M / r + Q**2 / r**2
    metric, coords, _ = build_ansatz_metric(4, f)
    A = [Q / r, 0, 0, 0]  # A_t = Q/r

    print("MAXWELL SOURCE — Reissner–Nordström\n")
    # recover the coupling κ from the residual (expect κ = 2 in geometric units)
    kap = sp.Symbol("kappa", positive=True)
    geo = Geometry(metric, coords)
    F = faraday(A, coords)
    T = em_stress(geo, F)
    res_sym = sp.simplify((geo.ricci - kap * T)[1, 1])
    ksol = sp.solve(sp.numer(sp.together(res_sym)), kap)
    print(f"  engine recovers coupling: κ = {ksol}")
    kappa = ksol[0] if ksol else sp.Integer(2)

    v, d = verify_em(metric, coords, A, kappa, params=(M, Q))
    print(f"  RN (M,Q) with κ={kappa}: {v}  ({d})")
    passed = v == VERIFIED
    print(f"\nMAXWELL: {'PASSED ✅' if passed else 'verdict '+v+' — see above'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
