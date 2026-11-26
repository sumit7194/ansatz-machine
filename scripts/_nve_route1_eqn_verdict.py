#!/usr/bin/env python3
"""Equal-n control (office, 2026-11-26; the Bridge's grading lesson: a "no weaker" clause must compare at equal n).
Runs Fable's UNCHANGED v2 verdict at v2's own (rho, n) = (4, 24) on v2's own node values (a COPY of
route1_seg_nodes_arb.jsonl from d855810; the original is never written), with the proved M of a later version
(SRC = v3 or v4) at rho = 4. Same nodes, same interpolant: every lower bound is then >= v2's iff each proved M is <=.
    NVE_SPIN=3/5 R1_R0=1.35 SRC=v4 nice -n 12 <quantum python> -I -u scripts/_nve_route1_eqn_verdict.py
(Restored verbatim 2026-11-26 after the power cut; see _nve_route1_segment_v4.py.)"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flint import arb                   # noqa: E402
import _nve_route1_segment_v2 as V      # noqa: E402

SRC = os.environ["SRC"]
J = json.load(open(os.path.join(V.OUTD, f"route1_seg_M_{SRC}{V.TAG}_nseg1.json")))
J2 = json.load(open(os.path.join(V.OUTD, f"route1_seg_M_v2{V.TAG}_nseg1.json")))
v2ch = J2["segs"][0]["chosen"]
assert (v2ch["rho"], v2ch["n"]) == (4.0, 24)
row = dict(next(r for r in J["rows"] if r["rho"] == 4.0))
n, rb = 24, arb(4)
den = rb ** n * (rb - 1)
for m, e in (("MF", "errF"), ("MT0", "errT0"), ("MT1", "errT1")):
    row[e] = V.ser((4 * V.par_up(row[m]) / den).upper())
row["n"] = n
row["boxes"] = row["expected_boxes"] = [0, 0]      # v3/v4 assert their own coverage; v2's count check does not apply
cmp = {m: (V.par_up(row[m]) <= V.par_up(v2ch[m])) for m in ("MF", "MT0", "MT1")}
(kc, half), = V.seg_centres(1)
tag = V.TAG + f"_{SRC}eqn24"
json.dump(dict(seg=V.SEG, nseg=1, segs=[dict(i=0, kc=f"{float(kc.mid()):.6f}", selftest=J["selftest"], chosen=row)],
               version=f"{SRC}-eqn24", M_le_v2=cmp), open(os.path.join(V.OUTD, f"route1_seg_M_v2{tag}_nseg1.json"), "w"), indent=1)
src_nodes = os.path.join(V.OUTD, f"route1_seg_nodes_arb{V.TAG}.jsonl")
dst_nodes = os.path.join(V.OUTD, f"route1_seg_nodes_arb{tag}.jsonl")
if not os.path.exists(dst_nodes):
    shutil.copyfile(src_nodes, dst_nodes)
V.TAG = tag
V.NODEFILE["arb"] = dst_nodes
V.LOG = os.path.join(V.OUTD, f"route1_seg_{V.SPIN.replace('/', '_')}_{SRC}eqn24.out")
V.say(f"== equal-n control: {SRC} proved M at v2's (rho, n) = (4, 24), on v2's node values (copy) ==")
for m in ("MF", "MT0", "MT1"):
    V.say(f"  {m}: {SRC} <= {V.hi_sci(V.par_up(row[m]))}, v2 <= {V.hi_sci(V.par_up(v2ch[m]))}; {SRC} <= v2: {cmp[m]}")
V.nodes(1, "arb")
V.verdict(1, "arb")
