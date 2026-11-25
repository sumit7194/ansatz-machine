#!/usr/bin/env python3
"""Floating reference values for the route (i) prototype (data/nve/EPS_EFFECTIVE.md, Part B): the registered 50-digit
engine's tr M0, tr M1, F and its singular points at a few real k, spin from NVE_SPIN, circle R0 = 1.35.
[model: Fable 5.2; UNVERIFIED]   1 core, nice 12, peak < 300 MB, about 20 s per k.
    NVE_SPIN=3/5 .venv/bin/python scripts/_nve_route1_floats.py 1 21/20 11/10      -> data/nve/eps/route1_floats.json
"""
import json
import os
import sys
import time

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_spin_scan as S      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "nve", "eps", os.environ.get("R1_FLOATS", "route1_floats.json"))
R0S = os.environ.get("R1_R0", "1.35")
lau = S.LauA(mp.mpf(R0S))
st = S.kerr_points()
res = json.load(open(OUT)) if os.path.exists(OUT) else {}
for ks in sys.argv[1:]:
    t0 = time.time()
    num, _, den = ks.partition("/")
    k = mp.mpf(num) / mp.mpf(den or 1)
    kpath = [k * j / 8 for j in range(1, 9)]            # walk the singular points from k = 0
    cur = st
    for kk in kpath:
        pr, outer, extras = lau.state(mp.mpc(kk), cur)
        cur = outer
    lasso, g = lau.loops(pr, outer, extras)
    r = lau.evaluate(pr, outer, extras, lasso)

    def c(x):
        return [mp.nstr(mp.re(x), 40), mp.nstr(mp.im(x), 40)]
    res[ks] = dict(spin=str(S.SPIN), R0=R0S, F=c(r["F"]), T0=c(r["T0"]), T1=c(r["T1"]),
                   points=[c(x) for x, _ in outer], lasso=[c(x) for x in lasso], geometry_ok=bool(g["ok"]),
                   sec=round(time.time() - t0, 1))
    print(ks, "F", mp.nstr(r["F"], 15), "T0", mp.nstr(r["T0"], 15), "T1", mp.nstr(r["T1"], 15), "geo", g["ok"],
          f"{time.time() - t0:.0f}s", flush=True)
    json.dump(res, open(OUT, "w"), indent=1)
