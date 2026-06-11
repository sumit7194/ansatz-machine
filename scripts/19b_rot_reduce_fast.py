#!/usr/bin/env python3
"""Step 19b — R0 via ε-truncated contraction (fallback for 19's swell).

Same physics as 19_rot_reduce.py; the difference is purely computational:
every Riemann entry is truncated at O(ε²) BEFORE the invariant
contractions, and every product in the contractions is truncated again —
intermediate expression swell (the measured bottleneck) never happens.

Run:  .venv/bin/python scripts/19b_rot_reduce_fast.py
"""

import importlib.util
import os

import sympy as sp

from gr_engine import Geometry, R_SYM, zero_simplify

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "edgb_reduce", os.path.join(_here, "10_edgb_reduce.py"))
m10 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m10)

r = R_SYM
eps = sp.Symbol("epsilon")
ap = m10.ap


def trunc(e):
    """Drop O(ε³) and higher. Series, not Poly: the inverse metric puts
    ε in DENOMINATORS (rational in ε — Poly raised PolynomialError)."""
    if not e.has(eps):
        return e
    return e.series(eps, 0, 3).removeO()


def rotating_L2():
    t, th, ph = sp.symbols("t theta phi", real=True)
    Gam = sp.Function("Gam")(r)
    Lam = sp.Function("Lam")(r)
    Phi = sp.Function("Phi")(r)
    W = sp.Function("W")(r)

    g = sp.zeros(4, 4)
    g[0, 0] = -sp.exp(Gam)
    g[1, 1] = sp.exp(Lam)
    g[2, 2] = r**2
    g[3, 3] = r**2 * sp.sin(th)**2
    g[0, 3] = g[3, 0] = -eps * W * r**2 * sp.sin(th)**2

    geo = Geometry(g, [t, r, th, ph])
    n = 4
    ginv = sp.Matrix(4, 4, lambda i, j: trunc(sp.cancel(geo.ginv[i, j]
                                                        .series(eps, 0, 3)
                                                        .removeO())))
    Riem = geo.riemann
    Rt = [[[[trunc(sp.expand(Riem[a][b][c][d]))
             for d in range(n)] for c in range(n)]
           for b in range(n)] for a in range(n)]

    # Ricci, scalar — truncated at every step
    Ric = [[trunc(sp.expand(sum(Rt[a][i][a][j] for a in range(n))))
            for j in range(n)] for i in range(n)]
    Rs = trunc(sp.expand(sum(ginv[i, j] * Ric[i][j]
                             for i in range(n) for j in range(n))))
    RicSq = trunc(sp.expand(sum(
        ginv[i, a] * ginv[j, b] * Ric[i][j] * Ric[a][b]
        for i in range(n) for j in range(n)
        for a in range(n) for b in range(n))))

    # Kretschmann: lower first index, then full raise — truncating
    Rdown = [[[[trunc(sp.expand(sum(g[a, e] * Rt[e][b][c][d]
                                    for e in range(n))))
                for d in range(n)] for c in range(n)]
              for b in range(n)] for a in range(n)]
    Rup = [[[[trunc(sp.expand(sum(
        ginv[a, p_] * ginv[b, q] * ginv[c, s] * ginv[d, u]
        * Rdown[p_][q][s][u]
        for p_ in range(n) for q in range(n)
        for s in range(n) for u in range(n))))
        for d in range(n)] for c in range(n)]
        for b in range(n)] for a in range(n)]
    K = trunc(sp.expand(sum(
        Rdown[a][b][c][d] * Rup[a][b][c][d]
        for a in range(n) for b in range(n)
        for c in range(n) for d in range(n))))

    GB = trunc(sp.expand(K - 4 * RicSq + Rs**2))
    det = trunc(sp.expand(g.det()))
    sqrtg = sp.sqrt(sp.expand(-det))
    # √−g to O(ε²): −det = D0 + D2 ε²  ⇒  √ = √D0·(1 + D2 ε²/(2 D0))
    D = sp.Poly(sp.expand(-det), eps)
    D0 = D.coeff_monomial(1)
    D2 = D.coeff_monomial(eps**2)
    sqrtg = sp.sqrt(D0) * (1 + (D2 / (2 * D0)) * eps**2)

    L = trunc(sp.expand(sqrtg * (
        Rs / 2 - sp.Rational(1, 4) * sp.exp(-Lam) * sp.diff(Phi, r)**2
        + (ap / 8) * sp.exp(Phi) * GB)))
    L2 = sp.diff(L, eps, 2).subs(eps, 0) / 2
    L2int = sp.integrate(sp.simplify(L2), (sp.Symbol("theta", real=True),
                                           0, sp.pi))
    return sp.simplify(L2int), (Gam, Lam, Phi, W)


def main():
    results = []
    print("Building O(ε²) Lagrangian (truncated contractions)...")
    L2, (Gam, Lam, Phi, W) = rotating_L2()
    print("   L2 ready; EL in w...")
    E_W = m10.euler_lagrange(L2, W)

    th = sp.Symbol("theta", real=True)
    ok_c = not E_W.has(th)
    results.append(ok_c)
    print(f"  {'✓' if ok_c else '✗✗'} R0c: θ-free")

    w0, w1, w2 = sp.symbols("w0 w1 w2")
    flat = E_W.subs({sp.Derivative(W, (r, 2)): w2,
                     sp.Derivative(W, r): w1, W: w0})
    ok_order = not any(flat.has(sp.Derivative(W, (r, k))) for k in (3, 4))
    lin_check = sp.expand(flat - (w0 * sp.diff(flat, w0)
                                  + w1 * sp.diff(flat, w1)
                                  + w2 * sp.diff(flat, w2)))
    ok_lin = sp.simplify(lin_check) == 0 and ok_order
    results.append(ok_lin)
    print(f"  {'✓' if ok_lin else '✗✗'} R0b: linear, 2nd order, homogeneous")

    M, c = sp.symbols("M c", positive=True)
    f = 1 - 2 * M / r
    subs_gr = {ap: 0, Gam: sp.log(f), Lam: -sp.log(f),
               Phi: sp.S.Zero, W: c / r**3}
    resid = zero_simplify(E_W.subs(subs_gr).doit())
    ok_a = resid == 0
    results.append(ok_a)
    print(f"  {'✓' if ok_a else '✗✗'} R0a: GR limit w=c/r³: "
          f"{'≡ 0' if ok_a else f'NONZERO: {resid}'}")

    # R0d: w⁰ coefficient vanishes (l=1) and GR ratio = 4/r − (Γ′+Λ′)/2
    c0 = sp.simplify(sp.diff(flat, w0))
    ok_l1 = c0 == 0
    print(f"  {'✓' if ok_l1 else '✗✗'} R0d: no w⁰ term (l=1 structure): "
          f"{ok_l1 if ok_l1 else c0}")
    results.append(ok_l1)
    ratio_gr = sp.simplify((sp.diff(flat, w1) / sp.diff(flat, w2))
                           .subs(ap, 0))
    target = 4 / r - (sp.Derivative(Gam, r) + sp.Derivative(Lam, r)) / 2
    ok_pc = sp.simplify(ratio_gr - target) == 0
    results.append(ok_pc)
    print(f"  {'✓' if ok_pc else '✗✗'} R0d: GR-limit G₂/G₃ = "
          f"4/r − (Γ′+Λ′)/2 (Pani-Cardoso structure)"
          + ("" if ok_pc else f" — ours: {ratio_gr}"))

    if all(results):
        # persist the coefficient ratio for R1 (srepr, D18 practice)
        g23 = sp.simplify(sp.diff(flat, w1) / sp.diff(flat, w2))
        with open(os.path.join(_here, "..", "rot_g23.srepr"), "w") as fh:
            fh.write(sp.srepr(g23))
        print("   G₂/G₃ persisted to rot_g23.srepr for R1")

    print(f"\n{'ALL EXPECTATIONS MET ✅' if all(results) else 'EXPECTATION FAILURES ❌'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
