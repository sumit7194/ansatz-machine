#!/usr/bin/env python3
"""v7 region B: the independent 50-digit ENGINE GATE for a region-B segment (the two-implementation rule).
For every Chebyshev node record in a v7B node file, compute F, tr Gamma (stored as T0), tr M1 with the HP engine
(_nve_lower_hp: its own c0, a 220-term series about Z0 from real-axis quadrature), on the SAME loops as the Arb run
(the floats entry's "lasso" and "gam", fixed at k_c), with r+, p+- tracked by Newton from k_c to the node. Each must lie
inside the Arb node enclosure. Mirrors _nve_route1_engine_gate.py (region A); one fsynced jsonl line per node; exit 2 on
any miss.
    NVE_SPIN=3/5 R1_KC=83/20 R1_HALF=1/20 R1_CODE=<v7B content hash> NODES=<node file> FLOATS=<floats file> OUTJ=<out> \\
        .venv/bin/python -I -u scripts/_nve_v7_engine_gate_B.py
"""
import json
import os
import sys
import time

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_spin_scan as SS                   # noqa: E402
import _nve_lower_kc as KC                    # noqa: E402
from _nve_route1_engine_gate import parse_ball, inside, q   # noqa: E402  (the region-A gate's own helpers)

mp.mp.dps = 50
KCS, HALFS = os.environ["R1_KC"], os.environ["R1_HALF"]
CODE = os.environ["R1_CODE"]
NODES, FLOATS, OUTJ = os.environ["NODES"], os.environ["FLOATS"], os.environ["OUTJ"]


def main():
    kc, half = q(KCS), q(HALFS)
    ref = json.load(open(FLOATS))[KCS]
    assert ref.get("picture") == "B"
    Z0, bB = mp.mpf(ref["Z0"]), mp.mpf(ref["bB"])
    lasso = [mp.mpc(mp.mpf(p[0]), mp.mpf(p[1])) for p in ref["lasso"]]
    gam = [mp.mpc(mp.mpf(p[0]), mp.mpf(p[1])) for p in ref["gam"]]
    pts_c = [mp.mpc(mp.mpf(p[0]), mp.mpf(p[1])) for p in ref["points"]]
    whs = [1, 2, 2]                                  # r+ is a zero of G1, p+- of G2
    RB = SS.HalfB(Z0, bB, 0, mp.mpf(ref["span"]))
    recs = [json.loads(l) for l in open(NODES) if l.strip()]
    recs = [r for r in recs if "|node" in r["key"]]
    done = {}
    if os.path.exists(OUTJ):
        for l in open(OUTJ):
            if l.strip():
                r = json.loads(l)
                assert r.get("code") == CODE, f"engine-gate record from code {r.get('code')}, not {CODE}"
                done[r["key"]] = r
    print(f"== engine gate B == spin {SS.SPIN}; segment k_c {KCS}, half {HALFS}; {len(recs)} node records; "
          f"lasso {len(lasso)} / Gamma {len(gam)} vertices; {len(done)} done", flush=True)
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
        assert abs(kr - (lo + hi) / 2) < mp.mpf("1e-12") * max(1, abs(kr)) and parse_ball(r["k"][1])[0] == 0
        pos = list(pts_c)
        for jj in range(1, 9):                       # track r+, p+- from k_c to the node
            prb = RB.problem(kc + (kr - kc) * jj / 8)
            pos = [KC.newton(prb, x, w) for x, w in zip(pos, whs)]
        res = RB.evaluate(prb, pos, lasso, gam)
        vals = dict(F=res["F"], T0=res["TG"], T1=res["T1"])
        out = dict(key=key, code=CODE, k=mp.nstr(kr, 30))
        ok_all = True
        for nm, v in vals.items():
            ok, rad = inside(v, r[nm])
            out[nm] = [mp.nstr(mp.re(v), 30), mp.nstr(mp.im(v), 30)]
            out[nm + "_inside"] = bool(ok)
            out[nm + "_radius"] = mp.nstr(rad, 3)
            ok_all &= ok
        out["pass"] = bool(ok_all)
        out["sec"] = round(time.time() - t0, 1)
        with open(OUTJ, "a") as fh:
            fh.write(json.dumps(out) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        npass += ok_all
        print(f"  {key.split('|')[-1]}: F {'in' if out['F_inside'] else 'OUT'}, trG {'in' if out['T0_inside'] else 'OUT'}, "
              f"T1 {'in' if out['T1_inside'] else 'OUT'}  [{out['sec']} s]", flush=True)
    print(f"  ENGINE GATE B: {npass}/{len(recs)} node values inside their enclosures", flush=True)
    sys.exit(0 if npass == len(recs) else 2)


if __name__ == "__main__":
    main()
