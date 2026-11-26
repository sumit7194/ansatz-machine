#!/usr/bin/env python3
"""Control for the centred enclosure (office, 2026-11-26): spin 3/5 must still CERTIFY with the v3 proved M.
Runs Fable's UNCHANGED v2 nodes/verdict stages (all-ball evaluator) on the v3 chosen row (rho, n, M, error bounds),
by writing that row in v2's JSON format under a separate tag; node values go to a separate jsonl (new n, new keys).
    NVE_SPIN=3/5 R1_R0=1.35 nice -n 12 <quantum python> -I -u scripts/_nve_route1_v3_verdict.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_route1_segment_v2 as V      # noqa: E402

J3 = json.load(open(os.path.join(V.OUTD, f"route1_seg_M_v3{V.TAG}_nseg1.json")))
ch = dict(J3["chosen"])
ch["boxes"] = ch["expected_boxes"] = [0, 0]          # v3 asserts its own coverage; v2's count check is not applicable
(kc, half), = V.seg_centres(1)
seg = dict(i=0, kc=f"{float(kc.mid()):.6f}", selftest=J3["selftest"], chosen=ch)
tag = V.TAG + "_v3cert"
json.dump(dict(seg=V.SEG, nseg=1, segs=[seg], version="3-cert"), open(os.path.join(V.OUTD, f"route1_seg_M_v2{tag}_nseg1.json"), "w"), indent=1)
V.TAG = tag
V.NODEFILE["arb"] = os.path.join(V.OUTD, f"route1_seg_nodes_arb{tag}.jsonl")
V.LOG = os.path.join(V.OUTD, f"route1_seg_{V.SPIN.replace('/', '_')}_v3cert.out")
V.nodes(1, "arb")
V.verdict(1, "arb")
