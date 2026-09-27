#!/usr/bin/env python3
"""Where are MN's bad sets? Numeric scan (double precision, grid) of the package's own functions (_mn_build.mn_functions):
CTCs (g_phiphi < 0), ergoregion (f < 0), B = 0 (f blows up), sign of A, over x in (1, 6], |y| < 1.  MEASURED, not recalled.
    .venv/bin/python scripts/_mn_singular_scan.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import sympy as sp
from _mn_build import mn_functions, metric, x, y, R, EA, EB, EP, EQ

for tag, M, a, beta in (("p1", 5, 3, sp.Rational(1, 5)), ("p2", 13, 5, sp.Rational(-1, 3)), ("kerr", 5, 3, sp.Integer(0))):
    F = mn_functions(M, a, beta)
    g = metric(F)
    ex = [sp.lambdify((x, y, R), F["expo"][E], "numpy") for E in (EA, EB, EP, EQ)]
    fun = {n: sp.lambdify((x, y, R, EA, EB, EP, EQ), e, "numpy")
           for n, e in (("f", F["f"]), ("gpp", g[3, 3]), ("A", F["A"]), ("B", F["B"]))}
    xs = 1 + np.geomspace(1e-4, 5, 700)
    ys = np.linspace(-0.999, 0.999, 401)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    RR = np.sqrt(X ** 2 + Y ** 2 - 1)
    with np.errstate(all="ignore"):
        Es = [np.exp(e(X, Y, RR) * np.ones_like(X)) for e in ex]
        V = {n: fn(X, Y, RR, *Es) * np.ones_like(X) for n, fn in fun.items()}
    ctc = V["gpp"] < 0
    erg = V["f"] < 0
    print(f"[{tag}] M={M} a={a} beta={beta}")
    for name, mask in (("CTC region (g_phiphi < 0)", ctc), ("ergoregion (f < 0)", erg)):
        if mask.any():
            print(f"    {name}: present; x-extent {X[mask].min():.5f} .. {X[mask].max():.5f}"
                  f"  (x - 1 from {X[mask].min() - 1:.2e}); |y| range {np.abs(Y[mask]).min():.3f} .. {np.abs(Y[mask]).max():.3f}")
        else:
            print(f"    {name}: none on the grid")
    Bmin = np.nanmin(np.abs(V["B"]))
    print(f"    min |B| on grid = {Bmin:.3e}  (B = 0 would make f singular)   min A = {np.nanmin(V['A']):.3e}, max A = {np.nanmax(V['A']):.3e}")
    print(f"    f near x = 1+1e-4: range {np.nanmin(V['f'][0]):.4e} .. {np.nanmax(V['f'][0]):.4e}")

# where the exponentials overflow: R = sqrt(x^2 + y^2 - 1) -> 0 only at (x, y) = (1, 0)
print("\nexponential blow-up locus (non-finite f), and |exponent of E_Q| vs R:")
for tag, M, a, beta in (("p1", 5, 3, sp.Rational(1, 5)), ("p2", 13, 5, sp.Rational(-1, 3))):
    F = mn_functions(M, a, beta)
    eq = sp.lambdify((x, y, R), F["expo"][EQ], "numpy")
    fl = sp.lambdify((x, y, R, EA, EB, EP, EQ), F["f"], "numpy")
    ex = [sp.lambdify((x, y, R), F["expo"][E], "numpy") for E in (EA, EB, EP, EQ)]
    xs = 1 + np.geomspace(1e-4, 5, 700); ys = np.linspace(-0.999, 0.999, 401)
    X, Y = np.meshgrid(xs, ys, indexing="ij"); RR = np.sqrt(X ** 2 + Y ** 2 - 1)
    with np.errstate(all="ignore"):
        fv = fl(X, Y, RR, *[np.exp(e(X, Y, RR) * np.ones_like(X)) for e in ex])
    bad = ~np.isfinite(fv) | (np.abs(fv) > 1e12)
    print(f"  [{tag}] non-finite or |f| > 1e12 on {bad.sum()} of {bad.size} grid points; "
          f"max R there = {RR[bad].max() if bad.any() else float('nan'):.3e}; x - 1 <= {(X[bad] - 1).max() if bad.any() else float('nan'):.2e}, |y| <= {np.abs(Y[bad]).max() if bad.any() else float('nan'):.3f}")
    for Rv in (0.5, 0.2, 0.1, 0.05):
        print(f"      R = {Rv}: exponent of E_Q at y = 0 is {eq(np.sqrt(1 + Rv**2), 0.0, Rv):.3e}")
