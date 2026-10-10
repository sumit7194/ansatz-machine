#!/usr/bin/env python3
"""Ergosurface precision check (the Bridge, 2026-10-11: its own f/omega-built Kerr chart loses precision at f = 0).
Compares the chaos engine's compiled float RHS (all 9 components, at the alpha levels' E, L) with 50-digit evaluation of
the same exact expressions, at x_e +- 1e-2 .. 1e-12 from the outermost equatorial ergosurface, y = 0 and 0.5.
    .venv/bin/python scripts/_ts_chaos_ergocheck.py
"""
import sys, os
sys.path.insert(0, "scripts")
import sympy as sp, mpmath as mp
import _kt_exact_op as O, _ts_chaos as C, _kt_metrics as MM
from _ts_chaos_scan import SYSTEMS
mp.mp.dps = 50
x, y = MM.x, MM.y
E_, L_ = C.E_, C.L_
LEVELS = {"kerr35": (0.95, -2.589928), "ts35": (0.95, -5.333333333333334), "ts45": (0.97, 5.125), "kerr45": (0.97, 2.550268)}
worst_all = 0.0
for s, (E, L) in LEVELS.items():
    spec = SYSTEMS[s][0]
    kind, _, par = spec.partition(":")
    tag = O.ts2_tag(par)
    f = f"ts2_{'KERR_' if kind == 'ts2kerr' else ''}metric_components_{tag}.txt"
    g = O.load_package(os.path.join("data", "sealed", "TS2_for_quantum", f))
    num = sp.numer(sp.together(g[0, 0].subs(y, 0)))
    roots = [r for r in sp.Poly(num, x).nroots(n=30) if r.is_real and r > 1]
    xe = max(float(r) for r in roots)           # outermost equatorial ergosurface
    ginv, name = O.get_metric(spec)
    eng = C.Engine(ginv, name)
    gxx, gyy = sp.cancel(ginv[1, 1]), sp.cancel(ginv[2, 2])
    W = sp.together(ginv[0, 0] * E_**2 - 2 * ginv[0, 3] * E_ * L_ + ginv[3, 3] * L_**2)
    exprs = [gxx, gyy, sp.diff(gxx, x), sp.diff(gxx, y), sp.diff(gyy, x), sp.diff(gyy, y), sp.diff(W, x), sp.diff(W, y), W]
    F = sp.lambdify((x, y, E_, L_), exprs, "mpmath")
    names = ["gxx", "gyy", "gxx_x", "gxx_y", "gyy_x", "gyy_y", "W_x", "W_y", "W"]
    print(f"[{s}] {name}: equatorial ergosurface x_e = {xe:.12f}")
    for yv in (0.0, 0.5):
        for dx in (1e-2, 1e-4, 1e-6, 1e-8, 1e-10, 1e-12):
            for sgn in (+1, -1):
                xv = xe + sgn * dx
                fl = eng.f(xv, yv, E, L)
                hp = F(mp.mpf(xv), mp.mpf(yv), mp.mpf(E), mp.mpf(L))
                rel = []
                for a, b, nm in zip(fl, hp, names):
                    b = float(b)
                    scale = max(abs(b), 1e-300)
                    if abs(b) < 1e-14 and abs(a) < 1e-14:
                        rel.append(0.0); continue
                    rel.append(abs(a - b) / scale)
                w = max(rel); worst_all = max(worst_all, w)
                if dx in (1e-2, 1e-6, 1e-10, 1e-12):
                    print(f"   y={yv} x_e{'+' if sgn>0 else '-'}{dx:.0e}: worst rel err {w:.1e} ({names[rel.index(w)]})")
print(f"OVERALL worst relative error over all charts/points/components: {worst_all:.2e}")
