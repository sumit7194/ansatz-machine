#!/usr/bin/env python3
"""v7 region-B must-fail controls (registration addenda 5, 7, 8), run before pilots 2 and 3. Each records WHICH guard
refused, so a control cannot pass on a different guard (the region-B read, item 2).
  (pos) the region-B self-test (dc0/dk, E0 and E1 against central differences; |FD dq/dk| <= sup) PASSES at k_c;
  (A)   with E replaced by E/1e6, the self-test FAILS;
  (A2)  with E replaced by E * 0.5, the self-test FAILS (a sharper must-fail; read item 4);
  (B)   with the disc radius patched large, a segment from bB through a c0 branch point is refused by the B-CUT guard;
  (B2)  with the true disc, a step box outside the disc is refused by the DISC guard;
  (R)   with the loops' reach planted at 10, the precondition refuses (its R_c part, not the 30/7 line);
  (P)   v6's hard-coded planted box (4.2 +- 0.01), substituted by 30/7 + 0.02 +- 0.01 (registered, addendum 8), refuses.
Diagnostics (no pass/fail): the precondition at pilots 2 and 3's rho = 4 k-boxes.
    R1_KC=83/20 R1_HALF=1/20 R1_FLOATS=route1_floats_v7B_3_5.json R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel NVE_SPIN=3/5 \\
        R1_R0=1.35 .venv313/bin/python -I -u scripts/_nve_v7_controlsB.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_route1_segment_v7B as B             # noqa: E402
from flint import acb, arb                      # noqa: E402

kc = B.S6.KC
lau_c, laud_c = B.V.laurent(acb(kc)), B.V.laurent(acb(kc), True)
res = {}

res["pos"] = bool(B.selftest_B(kc, lau_c, laud_c))

real = B.d2kc0_B
for name, fac in (("A", arb(10) ** -6), ("A2", arb(1) / 2)):
    B.V.d2kc0 = lambda Z, K, f=fac: (lambda e: None if e is None else (e[0] * f, e[1] * f))(real(Z, K))
    res[name] = not B.selftest_B(kc, lau_c, laud_c)
B.V.d2kc0 = real

c = B.fieldB_for(acb(kc)).c
p = max((q for q in c.sing_points() if q.imag > 0), key=lambda q: -abs(q))   # the inner branch point with Im > 0
bb = float(B.BB.mid())
Zs = acb(2 * p.real - bb, 2 * p.imag)                    # the segment bB -> Zs passes through p at tau = 1/2
real_Rd = B.Rd_for
B.Rd_for = lambda K: arb(99)
e = B.d2kc0_B(Zs, acb(kc))
res["B"] = e is None and B.LAST["refused"] == "B-cut"
resB = B.LAST["refused"]
B.Rd_for = real_Rd
e = B.d2kc0_B(acb(float(B.Z0.mid()) + 5.0), acb(kc))
res["B2"] = e is None and B.LAST["refused"] == "disc"
resB2 = B.LAST["refused"]

Kp = acb(kc) + arb("0.10625") * B.V.UNIT
real_reach = B.REACH
B.REACH = 10.0
pr = B.precondition_B(Kp)
res["R"] = (not pr["ok"]) and "reach" in pr.get("why", "")
B.REACH = real_reach
pp = B.precondition_B(arb("4.2") + arb("0.01") * B.V.UNIT)
res["P"] = (not pp["ok"]) and pp.get("planted_substituted") is not None

d2 = B.precondition_B(acb(arb(83) / 20) + (arb(1) / 20 * (arb(4) + arb(1) / 4) / 2) * B.V.UNIT)
kc3 = arb(59979) / 14000
d3 = B.precondition_B(acb(kc3) + (arb(1) / 2000 * (arb(4) + arb(1) / 4) / 2) * B.V.UNIT)
print(f"  diagnostics: pilot 2 rho=4 precondition ok {d2['ok']} (Rd {d2.get('Rd')}, reach {d2.get('reach')}); "
      f"pilot 3 rho=4 ok {d3['ok']} (Rd {d3.get('Rd')}) {d3.get('why', '')}", flush=True)
ok = all(res.values())
print(f"region-B controls: {res}; (B) refused by {resB}, (B2) by {resB2}; branch point used {p:.5f} -> "
      f"{'PASS' if ok else 'FAIL'}", flush=True)
sys.exit(0 if ok else 1)
