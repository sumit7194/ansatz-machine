#!/usr/bin/env python3
"""v7 region B: the floats entry for a segment centre k_c (engine side, mpmath 50 digits; addendum 5's pilots 2, 3).
The registered region-B geometry rule (_nve_spin_scan.geo / run mode): r+, p+- tracked from Kerr's points to the endpoint
30/7 - 1e-12, then back to k_c; Z0 = 2 at spin 3/5; base bB = max(Re r+(endpoint) - 0.3, a + 0.08); loops = HalfB.loops
(capsule lasso around [r+, p+], Gamma disc), span by the run-mode rule (the loops' reach + its margin).
Writes an entry like _nve_route1_floats.py's, with "lasso" = the region-B lasso and "gam" = the Gamma loop (the loop the
certifier walks in place of the circle), "T0" = tr Gamma, plus the geometry.
    NVE_SPIN=3/5 R1_FLOATS=route1_floats_v7B_3_5.json .venv/bin/python -I -u scripts/_nve_v7_floatsB.py 83/20
"""
import json
import os
import sys
import time

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_spin_scan as SS                   # noqa: E402
import _nve_lower_kc as KC                    # noqa: E402

mp.mp.dps = 50
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "nve", "eps", os.environ["R1_FLOATS"])
assert SS.SPIN == "3/5", "Z0 = 2 is the spin-3/5 centre; other spins need their own rule"


def q(s):
    num, _, den = s.partition("/")
    return mp.mpf(num) / mp.mpf(den or 1)


def geometry():
    A = SS.A
    seeds = SS.kerr_points()
    st = [seeds[0], seeds[2], seeds[3]]
    Z0 = mp.mpf(2)
    RB0 = SS.HalfB(Z0, mp.mpf(0), 0, mp.mpf(99))
    for j in range(1, 43):
        prb = RB0.problem(SS.B_X1 * j / 42)
        st = [(KC.newton(prb, x, w), w) for x, w in st]
    cen0 = sum(x for x, _ in st) / 3
    bB = max(mp.re(st[0][0]) - mp.mpf("0.3"), A + mp.mpf("0.08"))
    return Z0, bB, cen0, st


def main():
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    Z0, bB, cen0, endpts = geometry()
    RB = SS.HalfB(Z0, bB, cen0, mp.mpf(99))
    for ks in sys.argv[1:]:
        t0 = time.time()
        kc = q(ks)
        s2 = list(endpts)
        for j in range(1, 21):
            prb = RB.problem(SS.B_X1 + (kc - SS.B_X1) * j / 20)
            s2 = [(KC.newton(prb, x, w), w) for x, w in s2]
        prb = RB.problem(kc)
        pos = [KC.newton(prb, x, w) for x, w in s2]
        RB.span = mp.mpf(99)
        _l, _g, g0 = RB.loops(prb, pos)
        RB.span = mp.mpf(g0["contain"]) + mp.mpf("0.05")
        lasso, gam, g = RB.loops(prb, pos)
        r = RB.evaluate(prb, pos, lasso, gam)
        cs = lambda x: [mp.nstr(mp.re(x), 40), mp.nstr(mp.im(x), 40)]
        fl = lambda p: [repr(float(mp.re(p))), repr(float(mp.im(p)))]       # exact binary vertices, as the walk uses
        res[ks] = dict(spin=SS.SPIN, picture="B", Z0=str(Z0), bB=mp.nstr(bB, 40), span=float(RB.span),
                       F=cs(r["F"]), T0=cs(r["TG"]), T1=cs(r["T1"]), T1G=cs(r["T1G"]),
                       points=[cs(p) for p in pos], lasso=[fl(p) for p in lasso], gam=[fl(p) for p in gam],
                       sing=[cs(s) for s in prb.eng.sing], Rc=mp.nstr(prb.eng.Rc, 20), guards=g,
                       geometry_ok=bool(g["ok"]), sec=round(time.time() - t0, 1))
        print(f"{ks} F {mp.nstr(r['F'], 15)} T0(=tr Gamma) {mp.nstr(r['TG'], 15)} T1 {mp.nstr(r['T1'], 15)} "
              f"geo {g['ok']} {res[ks]['sec']}s", flush=True)
        json.dump(res, open(OUT, "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
