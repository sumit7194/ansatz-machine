#!/usr/bin/env python3
"""S1 must-fail control (S1_SPLIT_SEAL.md): v2's crude dq_sup must REFUSE a box containing a true zero of G1 (r+).
    PICTURE=A|B R1_KC=... R1_HALF=1/80 R1_FLOATS=... R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel NVE_SPIN=3/5 R1_R0=1.35 \\
        .venv313/bin/python -I -u scripts/_nve_v7_s1_control.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.environ["PICTURE"] == "B":
    import _nve_route1_segment_v7B as L        # noqa: E402
else:
    import _nve_route1_segment_v7 as L         # noqa: E402
from flint import acb, arb                      # noqa: E402

V = L.V
kc = L.S6.KC
R = (arb(1) / 80 * (arb(4) + arb(1) / 4) / 2).upper()
K, subs = V.kbox(kc, R)
rp = L.S6.REF["points"][0]                                   # r+ (a zero of G1) at k_c
Z = acb(arb(rp[0]), arb(rp[1])) + arb("0.01") * V.UNIT
lau, laud = V.laurent(acb(kc)), V.laurent(acb(kc), True)
try:
    r = V.dq_sup(Z, K, subs, lau, laud)
    refused = r is None
    how = "None" if r is None else f"ACCEPTED with sup {r[0]}"
except RuntimeError as e:
    refused, how = True, f"RuntimeError (refused box): {e}"
print(f"S1 control {os.environ['PICTURE']}: box around r+ = {rp[0][:10]}{'+' if not rp[1].startswith('-') else ''}{rp[1][:8]}i "
      f"at k_c {os.environ['R1_KC']} -> {how} -> {'FIRES' if refused else 'DOES NOT FIRE'}", flush=True)
sys.exit(0 if refused else 1)
