#!/usr/bin/env python3
"""Route (i) registration §3(b): the two-implementation check of the NODE VALUES of a certified segment.
[ansatz-machine-personal, 2026-11-26]

For every Chebyshev node record in an Arb node file (the certificate's node values), compute F, tr M0, tr M1 with the
registered 50-digit engine (`_nve_spin_scan.LauA`, mpmath), which shares no code with the Arb evaluator
(`_nve_route1_segment_v2.evaluate`), on the SAME loops: the circle |z| = R0 and the fixed lasso polygon of k_c = 21/20
from the floats file. (The engine walks a true circle arc, the Arb evaluator an inscribed 96-gon through the same base
point R0; no singular point lies between them, so the monodromies are equal.)

PASS iff every engine value lies inside its node enclosure. The first miss is reported and the run stops at that node
boundary (a correctness gate; everything before it is on disk).
Shared with the Arb side, so NOT made independent by this check: the formula for c0'' and the lasso vertices.

One jsonl line per node, flushed and fsynced; a rerun skips nodes already done. No caps.
    NVE_SPIN=3/5  R1_R0=1.35   NODES=data/nve/eps/route1_seg_nodes_arb.jsonl            FLOATS=data/nve/eps/route1_floats.json \
        nice -n 15 .venv/bin/python scripts/_nve_route1_engine_nodes.py
    NVE_SPIN=9/10 R1_R0=1.2639 NODES=data/nve/eps/route1_seg_nodes_arb_9_10_v4cert.jsonl FLOATS=data/nve/eps/route1_floats_9_10.json \
        nice -n 15 .venv/bin/python scripts/_nve_route1_engine_nodes.py
Output: data/nve/route1_check/engine_nodes_<spin>.jsonl and .out."""
import json
import os
import sys
import time

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_spin_scan as S      # noqa: E402  (mp.dps = 50, E = 4/5, spin from NVE_SPIN)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R0S = os.environ["R1_R0"]
NODES = os.path.join(ROOT, os.environ["NODES"])
FLOATS = os.path.join(ROOT, os.environ["FLOATS"])
tag = str(S.SPIN).replace("/", "_")
OUTJ = os.path.join(ROOT, "data", "nve", "route1_check", f"engine_nodes_{tag}.jsonl")
OUTL = os.path.join(ROOT, "data", "nve", "route1_check", f"engine_nodes_{tag}.out")


def say(s):
    print(s, flush=True)
    with open(OUTL, "a") as fh:
        fh.write(s + "\n")


def parse_ball(s):
    """'[m +/- r]' or a plain number -> (mpf lo, mpf hi)."""
    s = s.strip()
    if s.startswith("["):
        body = s[1:-1]
        if "+/-" in body:
            m, r = body.split("+/-")
            m = mp.mpf(m.strip()) if m.strip() else mp.mpf(0)
            r = mp.mpf(r.strip())
            return m - r, m + r
        return mp.mpf(body), mp.mpf(body)
    return mp.mpf(s), mp.mpf(s)


def inside(val, enc):
    (rl, rh), (il, ih) = parse_ball(enc[0]), parse_ball(enc[1])
    return rl <= mp.re(val) <= rh and il <= mp.im(val) <= ih, max(rh - rl, ih - il) / 2


ref = json.load(open(FLOATS))["21/20"]
lasso = [mp.mpc(mp.mpf(p[0]), mp.mpf(p[1])) for p in ref["lasso"]]
recs = [json.loads(l) for l in open(NODES)]
recs = [r for r in recs if "|node" in r["key"]]
done = {}
if os.path.exists(OUTJ):
    raw = open(OUTJ, "rb").read()
    cut = raw.rfind(b"\n") + 1
    if cut < len(raw):
        with open(OUTJ, "r+b") as fh:
            fh.truncate(cut)
            fh.flush()
            os.fsync(fh.fileno())
    for l in raw[:cut].split(b"\n")[:-1]:
        r = json.loads(l)
        done[r["key"]] = r
lau = S.LauA(mp.mpf(R0S))
st = S.kerr_points()
say(f"== engine at the nodes == spin {S.SPIN}, R0 {R0S}, mp.dps {mp.mp.dps}; node file {os.path.relpath(NODES, ROOT)} "
    f"({len(recs)} nodes); lasso of 21/20 from {os.path.relpath(FLOATS, ROOT)} ({len(lasso)} vertices); {len(done)} done")
npass = 0
for r in recs:
    key = r["key"]
    if key in done:
        npass += done[key]["pass"]
        continue
    t0 = time.time()
    # the node's exact k (the stored string is rounded): k = 21/20 + (1/20) cos(j pi / n), from the key
    n = int(key.split("|n=")[1].split("|")[0])
    j = int(key.split("|node")[1])
    kr = mp.mpf(21) / 20 + mp.cos(mp.pi * j / n) / 20
    lo, hi = parse_ball(r["k"][0])
    assert abs(kr - (lo + hi) / 2) < mp.mpf("1e-12") and parse_ball(r["k"][1])[0] == 0, "key and stored k disagree"
    k = mp.mpc(kr, 0)
    cur = st
    for j in range(1, 9):                         # walk the singular points from Kerr, as the floats script does
        pr, outer, extras = lau.state(k * j / 8, cur)
        cur = outer
    res = lau.evaluate(pr, outer, extras, lasso)
    out = dict(key=key, k=mp.nstr(kr, 30), sec=None)
    ok_all = True
    for nm in ("F", "T0", "T1"):
        ok, rad = inside(res[nm], r[nm])
        out[nm] = [mp.nstr(mp.re(res[nm]), 30), mp.nstr(mp.im(res[nm]), 30)]
        out[nm + "_inside"] = bool(ok)
        out[nm + "_radius"] = mp.nstr(rad, 3)
        ok_all &= ok
    out["pass"] = bool(ok_all)
    out["sec"] = round(time.time() - t0, 1)
    with open(OUTJ, "a") as fh:
        fh.write(json.dumps(out) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    say(f"  {key.split('|')[-1]}: k = {mp.nstr(kr, 12)}; F inside {out['F_inside']} (radius {out['F_radius']}), "
        f"tr M0 {out['T0_inside']}, tr M1 {out['T1_inside']}; {out['sec']} s")
    if not ok_all:
        say(f"  FIRST MISS at {key}: stopping at this node boundary (gate). {npass} passed before it.")
        sys.exit(2)
    npass += 1
say(f"  RESULT: {npass}/{len(recs)} node values inside their enclosures")
