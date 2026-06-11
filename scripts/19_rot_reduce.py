#!/usr/bin/env python3
"""Step 19 — v5 battery R0: the slow-rotation EdGB frame-dragging ODE.

Perturb the static EdGB ansatz with the standard slow-rotation
off-diagonal term,
    g_tφ = −ε · w(r) · r² sin²θ,
expand the FULL EdGB Lagrangian density to O(ε²) (the O(ε) term vanishes
by parity; w's equation of motion is the EL equation of the O(ε²) piece),
integrate the θ-dependence out symbolically, and take the Euler-Lagrange
equation in w.

R0 gates (pre-registered in docs/ROTATING.md):
  R0a  GR limit: at α′=0 on the Schwarzschild background, w = c/r³ must
       solve the equation IDENTICALLY (the exterior Lense-Thirring /
       Hartle first-order result).
  R0b  the equation is LINEAR in (w, w′, w″) and second order.
  R0c  no θ survives the reduction.

Run:  .venv/bin/python scripts/19_rot_reduce.py
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


def rotating_lagrangian_order2():
    """O(ε²) piece of the EdGB Lagrangian density on the slow-rotation
    ansatz, θ-integrated. Returns (L2, function objects)."""
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
    Rs = geo.ricci_scalar
    GB = geo.kretschmann - 4 * geo.ricci_squared + Rs**2
    detg = g.det()
    sqrtg = sp.sqrt(-detg)
    L = sqrtg * (Rs / 2
                 - sp.Rational(1, 4) * sp.exp(-Lam) * sp.diff(Phi, r)**2
                 + (ap / 8) * sp.exp(Phi) * GB)

    # O(ε²) coefficient, then integrate θ over [0, π]
    L2 = sp.diff(L, eps, 2).subs(eps, 0) / 2
    L2 = sp.simplify(L2)
    L2int = sp.integrate(L2, (th, 0, sp.pi))
    return sp.simplify(L2int), (Gam, Lam, Phi, W)


def main():
    results = []
    print("Building O(ε²) rotating EdGB Lagrangian (symbolic, heavy)...")
    L2, (Gam, Lam, Phi, W) = rotating_lagrangian_order2()
    print("   L2 ready; Euler-Lagrange in w...")
    E_W = m10.euler_lagrange(L2, W)

    # R0c: θ-free
    th = sp.Symbol("theta", real=True)
    ok_c = not E_W.has(th)
    results.append(ok_c)
    print(f"  {'✓' if ok_c else '✗✗'} R0c: equation is θ-free")

    # R0b: linear & second order in w
    w0, w1, w2 = sp.symbols("w0 w1 w2")
    flat = E_W.subs({sp.Derivative(W, (r, 2)): w2,
                     sp.Derivative(W, r): w1, W: w0})
    ok_order = not any(flat.has(sp.Derivative(W, (r, k)))
                       for k in (3, 4))
    lin_check = sp.expand(
        flat - (w0 * sp.diff(flat, w0) + w1 * sp.diff(flat, w1)
                + w2 * sp.diff(flat, w2)))
    # linear homogeneous ⇒ subtracting the Euler decomposition leaves 0
    ok_lin = sp.simplify(lin_check) == 0 and ok_order
    results.append(ok_lin)
    print(f"  {'✓' if ok_lin else '✗✗'} R0b: linear, second order, "
          "homogeneous in w")

    # R0a: GR limit — Schwarzschild + w = c/r³ solves identically
    M, c = sp.symbols("M c", positive=True)
    f = 1 - 2 * M / r
    subs_gr = {ap: 0, Gam: sp.log(f), Lam: -sp.log(f),
               Phi: sp.S.Zero, W: c / r**3}
    resid = zero_simplify(E_W.subs(subs_gr).doit())
    ok_a = resid == 0
    results.append(ok_a)
    print(f"  {'✓' if ok_a else '✗✗'} R0a: GR limit — w = c/r³ on "
          f"Schwarzschild: {'≡ 0' if ok_a else f'NONZERO: {resid}'}")

    print(f"\n{'ALL EXPECTATIONS MET ✅' if all(results) else 'EXPECTATION FAILURES ❌'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
