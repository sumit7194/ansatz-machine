#!/usr/bin/env python3
"""Control for the dCS C-tensor: TRACELESSNESS, on a background where it is not trivially zero.

WHY THIS CONTROL. "C vanishes when theta is constant" passes for a great many wrong formulas -- the
same weakness as "*RR = 0 on Schwarzschild", which passed while the contraction was wrong (see
_kt_dcs.pontryagin). g_ab C^{ab} = 0 is a nontrivial identity of the CORRECT C-tensor; a misplaced
or wrongly-raised index generically breaks it, so it is a control that can fail.

Background: Kerr truncated at O(a) with a nonconstant theta (the dipole shape), evaluated in exact
arithmetic at random points. Also checks C -> 0 for constant theta, which is necessary but weak.

Repro:  .venv/bin/python scripts/_kt_dcs_ctensor_test.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from gr_engine import Geometry  # noqa: E402
from _kt_dcs import c_tensor  # noqa: E402

t, r, th, ph = sp.symbols("t r theta phi", real=True)

if __name__ == "__main__":
    M, a = sp.Integer(1), sp.Rational(1, 5)
    f = 1 - 2 * M / r
    g = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th) ** 2)
    g[0, 3] = g[3, 0] = -2 * M * a * sp.sin(th) ** 2 / r          # Lense-Thirring, O(a)
    geom = Geometry(g, [t, r, th, ph])
    print(f"background: Schwarzschild + Lense-Thirring, M={M}, a={a}\n", flush=True)

    print("  (1) constant theta must give C = 0 (necessary, weak) ...", flush=True)
    C0 = c_tensor(geom, sp.Integer(1))
    print(f"      C == 0 : {sp.simplify(C0) == sp.zeros(4, 4)}\n", flush=True)

    theta = sp.cos(th) / r**2 * (1 + 2 * M / r + sp.Rational(18, 5) * M**2 / r**2)
    print("  (2) dipole theta: C must be NONZERO and TRACELESS ...", flush=True)
    C = c_tensor(geom, theta)
    nz = any(C[i, j] != 0 for i in range(4) for j in range(4))
    print(f"      C nonzero: {nz}", flush=True)
    tr = sum(geom.ginv[i, j] * C[i, j] for i in range(4) for j in range(4))
    pts = [(sp.Rational(7, 2), sp.Rational(1, 3)), (sp.Rational(5), sp.Rational(-2, 5)),
           (sp.Rational(11, 4), sp.Rational(3, 4)), (sp.Rational(6), sp.Rational(2, 3))]
    ok = True
    for rv, cv in pts:
        v = sp.N(tr.subs({r: rv, th: sp.acos(cv)}), 50)
        small = abs(v) < sp.Float("1e-40")
        ok &= bool(small)
        print(f"      r={rv}, cos(th)={cv}:  g_ab C^ab = {sp.N(v, 8)}   zero: {small}", flush=True)
    print()
    if ok and nz:
        print("  PASS: C is nonzero and traceless.")
    else:
        print("  FAIL: " + ("trace does not vanish" if nz else "C is identically zero"))
        raise SystemExit(1)
