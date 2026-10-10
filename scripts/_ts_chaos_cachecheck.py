#!/usr/bin/env python3
"""Evidence that the engine-cache bug (one Engine per process, regardless of metric; fixed in 04bb688) did not touch the
v2 scans (the Bridge asked for this to be shown, not argued). This re-runs whole scan levels with the FIXED cache. They go
through ONE pool with the systems interleaved, so every worker serves several metrics (the exact situation the bug
corrupted). Each re-run level is compared, as a whole JSON object, with the level stored in bscan_<sys>_v2.json.
Per system: the level with the most candidates, plus one level picked with a fixed seed among the levels that have
windows but no candidates. 8 levels in total. A bit-identical match on all of them is the PASS.
Comparison is on canonical JSON text (sorted keys, float repr). Run 1 compared dicts with ==, and that FAILED 0/8.
A plunged orbit stores fd = NaN, and nan != nan unless both are the SAME object. json.loads hands out one shared NaN,
so stored-vs-stored passes, but levels coming back from a worker carry fresh NaN objects, so == could never pass.
The comparator now self-tests in both directions before use: stored vs a copy with fresh NaN objects must read
IDENTICAL, and stored vs a copy with one fd moved by one ulp must read DIFFERS. The re-run levels are saved to
cachecheck.json, and any differing field is reported.
    .venv/bin/python scripts/_ts_chaos_cachecheck.py [workers=4]
"""
import json
import math
import os
import random
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ts_chaos_scan import SYSTEMS, _level_job  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "ts_chaos")
SYS = ("ts45", "kerr45", "ts35", "kerr35")


def canon(x):
    return json.dumps(x, sort_keys=True)


def _fresh_nans(x):
    if isinstance(x, dict):
        return {k: _fresh_nans(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_fresh_nans(v) for v in x]
    return float("nan") if isinstance(x, float) and math.isnan(x) else x


def selftest(level):
    fresh = _fresh_nans(level)
    bumped = _fresh_nans(level)
    o = next(o for o in bumped["orbits"] if o["fd"] == o["fd"])
    o["fd"] = math.nextafter(o["fd"], 1.0)
    old_rule = level == fresh                          # what run 1 did
    ok = canon(level) == canon(fresh) and canon(level) != canon(bumped)
    print(f"  comparator self-test: fresh-NaN copy IDENTICAL {canon(level) == canon(fresh)}, one-ulp copy DIFFERS "
          f"{canon(level) != canon(bumped)}  (run-1 rule == on the fresh-NaN copy: {old_rule})", flush=True)
    if not ok:
        raise SystemExit("comparator self-test FAILED")


def diff(old, new):
    out = []
    for k in sorted(set(old) | set(new)):
        if k == "orbits":
            continue
        if canon(old.get(k)) != canon(new.get(k)):
            out.append(f"{k}: {old.get(k)} vs {new.get(k)}")
    oo, no = old["orbits"], new["orbits"]
    if len(oo) != len(no):
        out.append(f"orbit count {len(oo)} vs {len(no)}")
    nd = 0
    for a, b in zip(oo, no):
        for k in sorted(set(a) | set(b)):
            if canon(a.get(k)) != canon(b.get(k)):
                nd += 1
                if nd <= 5:
                    out.append(f"x0={a.get('x0')} {k}: {a.get(k)} vs {b.get(k)}")
    if nd:
        out.append(f"{nd} differing orbit fields")
    return out


def _job(a):
    sysname, i, args = a
    return sysname, i, json.loads(json.dumps(_level_job(args)))


def main():
    rng = random.Random(150)
    jobs = []
    for s in SYS:
        spec, m, x_in = SYSTEMS[s]
        levels = json.load(open(os.path.join(D, f"bscan_{s}_v2.json")))["levels"]
        ncand = [sum(o["cand"] for o in lv["orbits"]) for lv in levels]
        top = max(range(len(levels)), key=lambda i: (ncand[i], -i))
        quiet = [i for i, lv in enumerate(levels) if lv.get("windows") and ncand[i] == 0 and i != top]
        for i in (top, rng.choice(quiet)):
            lv = levels[i]
            jobs.append((s, i, (spec, lv["E"], lv["L"], x_in, 60, 200, 300)))
    selftest(json.load(open(os.path.join(D, f"bscan_{jobs[0][0]}_v2.json")))["levels"][jobs[0][1]])
    order = [j for k in range(2) for j in jobs[k::2]]          # interleave systems: ts45, kerr45, ts35, kerr35, ...
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    with Pool(workers) as pool:
        out = pool.map(_job, order, chunksize=1)
    json.dump([dict(system=s, index=i, level=new) for s, i, new in out], open(os.path.join(D, "cachecheck.json"), "w"))
    ok = 0
    for s, i, new in out:
        old = json.load(open(os.path.join(D, f"bscan_{s}_v2.json")))["levels"][i]
        same = canon(new) == canon(old)
        ok += same
        print(f"  {s:7s} level {i:3d} E={old['E']} L={old['L']:+.4f}: {len(old['orbits'])} orbits, "
              f"{sum(o['cand'] for o in old['orbits'])} candidates -> {'IDENTICAL' if same else 'DIFFERS'}", flush=True)
        if not same:
            for line in diff(old, new):
                print("      " + line, flush=True)
    print(f"VERDICT cachecheck: {ok}/{len(out)} levels bit-identical to the stored v2 scan "
          f"({'PASS' if ok == len(out) else 'FAIL'})", flush=True)
    return 0 if ok == len(out) else 1


if __name__ == "__main__":
    sys.exit(main())
