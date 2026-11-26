#!/usr/bin/env python3
"""The route-(i) segment verdict on the v4 proved M (office, 2026-11-26; seal data/nve/ROUTE1_V4_9_10_VERDICT_SEAL.md).
Runs Fable's UNCHANGED v2 `nodes` and `verdict` stages (the all-ball evaluator; every control of v2) on the v4 chosen
row (rho, n, M, error bounds), written in v2's JSON format under a separate tag. Node values go to a separate jsonl.
Two additions, both outside v2's logic:
  - every node record is flushed and FSYNCED (v2's `get` with os.fsync; the record format is unchanged);
  - a torn LAST record (a power cut mid-write) is dropped and the file truncated before loading; a bad record
    anywhere else still raises (v2's json.loads), which is a correctness gate at a node boundary.
Resumable: a rerun skips every node already on disk (v2's mechanism).
    NVE_SPIN=9/10 R1_R0=1.2639 nice -n 12 <quantum python> -I -u scripts/_nve_route1_v4_verdict.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_route1_segment_v2 as V      # noqa: E402

J4 = json.load(open(os.path.join(V.OUTD, f"route1_seg_M_v4{V.TAG}_nseg1.json")))
ch = dict(J4["chosen"])
ch["boxes"] = ch["expected_boxes"] = [0, 0]          # v4 asserts its own coverage; v2's count check is not applicable
(kc, half), = V.seg_centres(1)
seg = dict(i=0, kc=f"{float(kc.mid()):.6f}", selftest=J4["selftest"], chosen=ch)
tag = V.TAG + "_v4cert"
json.dump(dict(seg=V.SEG, nseg=1, segs=[seg], version="4-cert"), open(os.path.join(V.OUTD, f"route1_seg_M_v2{tag}_nseg1.json"), "w"), indent=1)
V.TAG = tag
V.NODEFILE["arb"] = os.path.join(V.OUTD, f"route1_seg_nodes_arb{tag}.jsonl")
V.LOG = os.path.join(V.OUTD, f"route1_seg_{V.SPIN.replace('/', '_')}_v4cert.out")

nf = V.NODEFILE["arb"]
if os.path.exists(nf):
    raw = open(nf, "rb").read()
    cut = raw.rfind(b"\n") + 1
    if cut < len(raw):
        V.say(f"  node file: torn last record ({len(raw) - cut} bytes) dropped; truncated to {cut} bytes")
        with open(nf, "r+b") as fh:
            fh.truncate(cut)
            fh.flush()
            os.fsync(fh.fileno())


def get_fsync(done, which, key, kre, kim, ref):
    """v2.get, with the record flushed and fsynced."""
    if key not in done:
        if which != "arb":
            raise RuntimeError(f"missing Part B node value {key}")
        r = dict(key=key, **V.evaluate(kre, kim, ref))
        with open(V.NODEFILE[which], "a") as fh:
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        done[key] = r
        V.say(f"  {key}: {r['sec']} s, steps {r['steps']}, radius of F {r['rad_F']:.1e}")
    r = done[key]
    return tuple(V.acb(V.arb(r[nm][0]), V.arb(r[nm][1])) for nm in ("F", "T0", "T1"))


V.get = get_fsync
V.say(f"== v4 verdict == {V.SEG}; chosen rho = {ch['rho']}, n = {ch['n']}; nodes -> {os.path.basename(nf)} (fsynced)")
V.nodes(1, "arb")
V.verdict(1, "arb")
