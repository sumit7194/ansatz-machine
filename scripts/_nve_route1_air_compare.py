#!/usr/bin/env python3
"""Compare the Air reproduction of the spin-9/10 v4 certificate with the committed outputs (c2dd39c).
[ansatz-machine-personal, 2026-11-26]
    python3 scripts/_nve_route1_air_compare.py <dir with the Air outputs>
Committed copies: data/nve/route1_check/committed/.
- BYTE-identical required: the per-step dq checkpoint (exact mantissa/exponent bounds) and the verdict JSON.
- Identical after removing ONLY run-environment fields: the rows file (drop "sec", the row's wall time), the v4 proof
  JSON (drop "env": interpreter path and Python version, and each row's "sec"), the v2-format cert JSON (drop "sec" inside the chosen row).
Prints one line per file and a final IDENTICAL / DIFFERS."""
import hashlib
import json
import os
import sys

AIR = sys.argv[1]
COM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "nve", "route1_check", "committed")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def strip(obj, drop):
    if isinstance(obj, dict):
        return {k: strip(v, drop) for k, v in obj.items() if k not in drop}
    if isinstance(obj, list):
        return [strip(v, drop) for v in obj]
    return obj


ok_all = True
for name, mode, drop in (("route1_seg_v4_9_10_dqck.jsonl", "bytes", ()),
                         ("route1_seg_verdict_v2_arb_9_10_v4cert_nseg1.json", "bytes", ()),
                         ("route1_seg_v4_9_10_rows.jsonl", "jsonl", ("sec",)),
                         ("route1_seg_M_v4_9_10_nseg1.json", "json", ("env", "sec")),
                         ("route1_seg_M_v2_9_10_v4cert_nseg1.json", "json", ("sec",))):
    a, b = os.path.join(AIR, name), os.path.join(COM, name)
    if not os.path.exists(a):
        print(f"MISSING on the Air side: {name}")
        ok_all = False
        continue
    if mode == "bytes":
        same = sha(a) == sha(b)
        how = f"sha256 {sha(a)[:16]} vs {sha(b)[:16]}"
    elif mode == "jsonl":
        ra = [strip(json.loads(l), drop) for l in open(a) if l.strip()]
        rb = [strip(json.loads(l), drop) for l in open(b) if l.strip()]
        same = ra == rb
        how = f"{len(ra)} vs {len(rb)} records, fields dropped: {drop}; byte-identical too: {sha(a) == sha(b)}"
    else:
        ja, jb = strip(json.load(open(a)), drop), strip(json.load(open(b)), drop)
        same = ja == jb
        how = f"fields dropped: {drop}; byte-identical too: {sha(a) == sha(b)}"
    ok_all &= same
    print(f"{'IDENTICAL' if same else 'DIFFERS  '}  {name}  ({how})")
print("RESULT:", "IDENTICAL" if ok_all else "DIFFERS")
