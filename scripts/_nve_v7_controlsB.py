#!/usr/bin/env python3
"""v7 region-B must-fail controls (registration addenda 5 and 7), run before pilots 2 and 3:
  (pos) the region-B self-test (dc0/dk, d2c0/dk2 against central differences; |FD dq/dk| <= sup) PASSES at k_c;
  (A)   with d2kc0_B replaced by E/1e6, the same self-test FAILS (the second-derivative check catches the bound);
  (B)   a step box whose straight segment from bB crosses a c0 branch point makes d2kc0_B return None.
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
pos = B.selftest_B(kc, lau_c, laud_c)

real = B.d2kc0_B
B.V.d2kc0 = B.d2kc0_B = lambda Z, K: (lambda e: None if e is None else (e[0] / 10 ** 6, e[1] / 10 ** 6))(real(Z, K))
shrunk = B.selftest_B(kc, lau_c, laud_c)
B.V.d2kc0 = B.d2kc0_B = real
fired_A = not shrunk

c = B.fieldB_for(acb(kc)).c
bp = [p for p in c.sing_points() if p.real > 0]
p = min(bp, key=lambda q: abs(q - complex(float(B.BB.mid()))))      # the nearest branch point with Re > 0
Zs = acb(2 * p.real - float(B.BB.mid()), 2 * p.imag)                 # bB -> Zs passes through p (its midpoint)
fired_B = B.d2kc0_B(Zs, acb(kc)) is None

ok = pos and fired_A and fired_B
print(f"region-B controls: positive self-test {pos}; (A) shrunken E caught {fired_A}; (B) segment through a branch point "
      f"refused {fired_B} (branch point {p:.5f}) -> {'PASS' if ok else 'FAIL'}", flush=True)
sys.exit(0 if ok else 1)
