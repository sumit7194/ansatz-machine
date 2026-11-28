#!/usr/bin/env python3
"""v7 stage V2 must-fail control for the F1b gate (the non-author read, item 5; registration addendum 4).
F1b asserts that the principal-branch c0'' series v2/v4 build equals the field's carried branch. Control: corrupt the
carried branch (negate s) in a cached field state and call v7's step there; F1b MUST fire. And the same call on a clean
field must NOT fire (so the gate is not a blanket refusal).
    R1_KC=21/20 R1_HALF=1/20 R1_FLOATS=route1_floats_v7t1_3_5.json R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel NVE_SPIN=3/5 \\
        R1_R0=1.35 .venv313/bin/python -I -u scripts/_nve_v7_controls.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_route1_segment_v7 as S7             # noqa: E402
import _nve_v7_field as FLD                     # noqa: E402
from flint import acb, arb                      # noqa: E402

k = acb(S7.S6.KC)
z = acb(arb(S7.V.R0S))
h = acb(arb(1) / 100)

f_clean = FLD.Field(S7.V.SPIN, k, S7.V.R0S)
try:
    S7.step7(z, h, k, FLD.View(f_clean, False), 0.2)
    clean_ok = True
except AssertionError as e:
    clean_ok = f"clean field refused: {e}"

f_bad = FLD.Field(S7.V.SPIN, k, S7.V.R0S)
st = f_bad.at(z)
st["s"] = -st["s"]                               # the planted corruption of the carried branch
try:
    S7.step7(z, h, k, FLD.View(f_bad, False), 0.2)
    fired = False
except AssertionError as e:
    fired = True if "F1b" in str(e) else f"other AssertionError: {e}"

ok = clean_ok is True and fired is True
print(f"F1b control: clean field passes {clean_ok}; corrupted branch fires {fired} -> {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
