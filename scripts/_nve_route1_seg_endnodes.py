#!/usr/bin/env python3
"""Route (i) segment, v2: evaluate only the two END nodes (k = 11/10 and k = 1) with the all-ball evaluator and compare
with the engine's values (the "engine at two nodes" control), when the full node run is too long to finish.
[model: Fable 5.2; UNVERIFIED]   The records go into the same node file under the same keys, so a later
`_nve_route1_segment_v2.py nodes 1 arb` resumes and skips them. Same environment variables as that script.
    NVE_SPIN=9/10 R1_R0=1.2639 /Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_seg_endnodes.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flint import acb, arb                       # noqa: E402
import _nve_route1_segment_v2 as S               # noqa: E402

J = json.load(open(os.path.join(S.OUTD, f"route1_seg_M_v2{S.TAG}_nseg1.json")))
refs = json.load(open(os.path.join(S.OUTD, S.FLOATS)))
ref = dict(refs["21/20"])
ch = J["segs"][0]["chosen"]
n = ch["n"]
kc, half = S.seg_centres(1)[0]
kn = S.keys(1, 0, ch)[0]
done = S.load_nodes("arb")
S.say(f"== end nodes only (all-ball evaluator) == {S.SEG}; circle {S.R0S}; chosen rho = {ch['rho']}, n = {n}")
for lab, j in (("11/10", 0), ("1", n)):
    v = S.get(done, "arb", kn(j), kc + half * (arb.pi() * j / n).cos(), arb(0), ref)
    e = refs[lab]
    ins = [bool(v[m].overlaps(acb(arb(e[nm][0]), arb(e[nm][1])))) for m, nm in enumerate(("F", "T0", "T1"))]
    S.say(f"  engine F, tr M0, tr M1 at k = {lab} (node {j}; the engine used its own lasso of that k): inside the enclosures "
          f"{ins}; radius of F {S.P.rad(v[0]):.1e}; |F| >= {S.lo_dec(v[0].abs_lower(), 9)}, |tr M0| >= {S.lo_dec(v[1].abs_lower(), 9)}, "
          f"|Im tr M1| >= {S.lo_dec(v[2].imag.abs_lower(), 9)}")
for kk, rr in (("4.2", "0.01"), ("4.01", "0.001"), ("4.0", "0.001")):
    pre = S.precondition(arb(kk) + arb(rr) * S.UNIT)
    S.say(f"  planted precondition at k = {kk} +- {rr} (complex box): certified {pre['ok']}" + (f"; {pre['why']}" if not pre["ok"] else ""))
