#!/usr/bin/env python3
"""Route (i) production: the two-implementation gate at every node of a v6 segment. [ansatz-machine-personal,
2026-11-27; NOT yet read or tested]

`_nve_route1_engine_nodes.py` (§3(b)) generalised from k_c = 21/20 to the segment [k_c - half, k_c + half] of
R1_KC, R1_HALF: for every Chebyshev node record in a v6 node file, compute F, tr M0, tr M1 with the registered
50-digit engine (`_nve_spin_scan.LauA`, mpmath), which shares no code with the Arb evaluator, on the same loops (the
circle |z| = R0 and the lasso of k_c from the floats file). PASS iff every engine value lies inside its node enclosure.
The first miss stops the run at that node boundary, exit code 2 (a correctness gate). The node's k is recomputed
exactly from the key (n, j) and k_c, half, and must agree with the stored k.
Shared with the Arb side, so NOT made independent by this check: the formula for c0'' and the lasso vertices.
One fsynced jsonl line per node; a rerun skips nodes already done. No caps.
    NVE_SPIN=3/5 R1_R0=1.35 R1_KC=3/20 R1_HALF=1/20 NODES=<v6 node file> FLOATS=<floats file> OUTJ=<gate jsonl> \
        <.venv python> -I -u scripts/_nve_route1_engine_gate.py"""
import json
import os
import sys
import time

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_spin_scan as S      # noqa: E402  (mp.dps = 50, E = 4/5, spin from NVE_SPIN)

R0S, KCS, HALFS = os.environ["R1_R0"], os.environ["R1_KC"], os.environ["R1_HALF"]
NODES, FLOATS, OUTJ = os.environ["NODES"], os.environ["FLOATS"], os.environ["OUTJ"]


def q(s):
    num, _, den = s.partition("/")
    return mp.mpf(num) / mp.mpf(den or 1)


def parse_ball(s):
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


def main():
    kc, half = q(KCS), q(HALFS)
    ref = json.load(open(FLOATS))[KCS]
    lasso = [mp.mpc(mp.mpf(p[0]), mp.mpf(p[1])) for p in ref["lasso"]]
    recs = [json.loads(l) for l in open(NODES) if l.strip()]
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
    print(f"== engine gate == spin {S.SPIN}, R0 {R0S}, mp.dps {mp.mp.dps}; segment k_c {KCS}, half {HALFS}; "
          f"{len(recs)} node records; lasso of {KCS} ({len(lasso)} vertices); {len(done)} done", flush=True)
    assert recs, "no node records"
    npass = 0
    for r in recs:
        key = r["key"]
        if key in done:
            assert done[key]["pass"], f"a recorded miss at {key}"
            npass += 1
            continue
        t0 = time.time()
        n = int(key.split("|n=")[1].split("|")[0])
        j = int(key.split("|node")[1])
        kr = kc + half * mp.cos(mp.pi * j / n)
        lo, hi = parse_ball(r["k"][0])
        assert abs(kr - (lo + hi) / 2) < mp.mpf("1e-12") * max(1, abs(kr)) and parse_ball(r["k"][1])[0] == 0, \
            f"key and stored k disagree at {key}"
        k = mp.mpc(kr, 0)
        cur = st
        for jj in range(1, 9):                       # walk the singular points from Kerr, as the floats script does
            pr, outer, extras = lau.state(k * jj / 8, cur)
            cur = outer
        res = lau.evaluate(pr, outer, extras, lasso)
        out = dict(key=key, k=mp.nstr(kr, 30))
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
        print(f"  node{j}: k = {mp.nstr(kr, 12)}; F inside {out['F_inside']} (radius {out['F_radius']}), "
              f"tr M0 {out['T0_inside']}, tr M1 {out['T1_inside']}; {out['sec']} s", flush=True)
        if not ok_all:
            print(f"  FIRST MISS at {key}: stopping at this node boundary (gate). {npass} passed before it.", flush=True)
            sys.exit(2)
        npass += 1
    print(f"  ENGINE GATE: {npass}/{len(recs)} node values inside their enclosures", flush=True)


if __name__ == "__main__":
    main()
