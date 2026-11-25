#!/usr/bin/env python3
"""Consistency control for the epsilon certificate (data/nve/EPS_EFFECTIVE.md, Part A): the registered 50-digit
engine's F at k = r_a must satisfy |F(r_a) - c2 r_a^2| <= the certified bound on |F - c2 k^2| at |k| = r_a.
[model: Fable 5.2; UNVERIFIED until the office ansatz-machine checks it]

It shares nothing with the certifier except the numbers it reads from data/nve/eps/eps_<spin><tag>.json.
One engine evaluation at k = r (and one at k = r*i), as in scripts/_nve_c2_engine_check.py. 1 core, nice 12,
declared peak < 300 MB, about a minute.
    NVE_SPIN=3/5 EPS_TAG= .venv/bin/python scripts/_nve_eps_engine_check.py     (appends to data/nve/eps/engine_check.out)
"""
import json
import os
import resource
import sys
import time

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_spin_scan as S      # noqa: E402  (mp.dps = 50, E = 4/5, spin from NVE_SPIN)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = os.environ.get("EPS_TAG", "")
J = json.load(open(os.path.join(ROOT, "data", "nve", "eps", f"eps_{str(S.SPIN).replace('/', '_')}{TAG}.json")))
t0 = time.time()
r = mp.mpf(J["r"])
c2 = mp.mpc((J["c2"][0] + J["c2"][1]) / 2, (J["c2"][2] + J["c2"][3]) / 2)
bound = J["parts"]["circ"] + J["parts"]["lass"]
lau = S.LauA(mp.mpf(J["R0"]))
st = S.kerr_points()
rows = [f"spin {S.SPIN}{TAG}, R0 {J['R0']}: certified r = {mp.nstr(r, 8)}, certified bound on |F - c2 k^2| at |k| = r: {bound:.6e}"]
ok_all = True
for k in (r, r * 1j):
    pr, outer, extras = lau.state(mp.mpc(k), st)
    lasso, g = lau.loops(pr, outer, extras)
    res = lau.evaluate(pr, outer, extras, lasso)
    rem = abs(res["F"] - c2 * k**2)
    ok = bool(rem <= bound) and bool(g["ok"]) and abs(res["F"]) > 0
    ok_all &= ok
    rows.append(f"  k = {mp.nstr(k, 6)}: engine F = {mp.nstr(res['F'], 12)}, c2 k^2 = {mp.nstr(c2 * k**2, 12)}, "
                f"|F - c2 k^2| = {mp.nstr(rem, 6)}  (<= bound: {ok}; ratio bound/true = {mp.nstr(bound / rem, 4)}); "
                f"tr M0 = {mp.nstr(res['T0'], 10)}, tr M1 = {mp.nstr(res['T1'], 10)}; geometry ok {g['ok']}")
rows.append(f"  CONSISTENT: {ok_all}   [{time.time() - t0:.0f} s, peak {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB]")
print("\n".join(rows), flush=True)
with open(os.path.join(ROOT, "data", "nve", "eps", "engine_check.out"), "a") as fh:
    fh.write("\n".join(rows) + "\n\n")
