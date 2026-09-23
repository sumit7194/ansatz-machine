#!/usr/bin/env python3
"""Kerr (delta = 1) through the SAME _ts2_build.py pipeline, as the in-stage control requested by quantum.
Same Ernst construction (xi = p x - i q y), same Weyl-Papapetrou prolate form, coordinates (T, x, y, phi), same
omega sign convention (fixed by the twist equations), same srepr format as the TS files.  Vacuum re-verified at
each fixed (p, q) before writing.  Usage: _ts2_kerr_control.py"""
import sys
sys.path.insert(0, "scripts")
import sympy as sp
import _ts2_build as B

for tval, tag in ((sp.Rational(1, 2), "t1o2"), (sp.Rational(1, 3), "t1o3")):
    B.T_FIXED = tval
    p, q = B.pq()
    g, info = B.metric(1)
    worst = B.vacuum_test(g, "Kerr", npts=4, seed=17)
    print(f"(p,q) = ({p},{q}): omega sign s = {info['sign']}; Kerr vacuum at 4 random rational points: max |R_ab| = {worst}")
    assert worst == 0, "Kerr control failed vacuum -- not writing"
    fn = f"data/sealed/TS2_for_quantum/ts2_KERR_metric_components_{tag}.txt"
    with open(fn, "w") as fh:
        fh.write(f"# KERR (delta=1) via the SAME _ts2_build.py pipeline as the TS files: xi = p x - i q y; coordinates (T, x, y, phi);"
                 f" p={p}, q={q}; omega sign s={info['sign']}; vacuum verified exactly at 4 random rational points; srepr per component\n")
        for nm, cc in (("g_TT", g[0, 0]), ("g_Tphi", g[0, 3]), ("g_phiphi", g[3, 3]), ("g_xx", g[1, 1]), ("g_yy", g[2, 2])):
            fh.write(f"{nm} = {sp.srepr(sp.cancel(cc))}\n")
        fh.write(f"omega = {sp.srepr(info['omega'])}\nA = {sp.srepr(info['A'])}\nB = {sp.srepr(info['B'])}\n")
    print(f"  written {fn}")
