#!/usr/bin/env python3
"""Is the parallel source prep (KT_PREP_WORKERS > 1, scripts/_kt_double.py) IDENTICAL to the serial one?

Runs the real _kt_pole_reduced.py pipeline twice in fresh processes, serial and parallel, stops each one
right after _prep_level, and compares the level matrix it would hand to the solver: every Coo part's row
codes, column indices and values, byte for byte (SHA-256), plus the part count and nnz. Identical bytes
mean an identical linear system, so everything downstream (nullspace, dim V, directions) is the same.
The end-to-end check against old committed outputs is separate: run the pipeline and diff its .out.

    .venv/bin/python scripts/_kt_prep_parallel_check.py [--sabotage] [workers] -- <_kt_pole_reduced.py args>

--sabotage flips one matrix value in the parallel run; the check then PASSES only if it says DIFFERENT
(a comparison that has only ever said "identical" has not been shown able to say anything else).
"""
import hashlib, os, subprocess, sys

if os.environ.get("_PREP_CHILD"):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _kt_double as KD
    real = KD._prep_level

    def hashed(*a, **k):
        lev = real(*a, **k)
        h = hashlib.sha256()
        nnz = 0
        sab = os.environ.get("_PREP_SABOTAGE") and int(os.environ.get("KT_PREP_WORKERS", "1")) > 1
        for q in lev.parts:
            if sab:                          # plant ONE wrong value in the parallel run: must turn it red
                q.vi = q.vi.copy(); q.vi[len(q.vi) // 2] ^= 1; sab = False
            for arr in (q.rc, q.ci, q.vi):
                h.update(arr.dtype.str.encode()); h.update(arr.tobytes())
            nnz += len(q.vi)
        print(f"PREPHASH parts={len(lev.parts)} nnz={nnz} sha256={h.hexdigest()}", flush=True)
        raise SystemExit(0)
    KD._prep_level = hashed
    import runpy
    sys.argv = ["_kt_pole_reduced.py"] + sys.argv[1:]
    runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kt_pole_reduced.py"),
                   run_name="__main__")
    sys.exit("pipeline ended without reaching _prep_level")

args = sys.argv[1:]
sabotage = bool(args) and args[0] == "--sabotage"
if sabotage:
    args.pop(0)
workers = "6"
if args and args[0] != "--":
    workers = args.pop(0)
if args and args[0] == "--":
    args.pop(0)
res = {}
for w in ("1", workers):
    env = dict(os.environ, _PREP_CHILD="1", KT_PREP_WORKERS=w, KT_SOLVER="rust")
    if sabotage:
        env["_PREP_SABOTAGE"] = "1"
    out = subprocess.run([sys.executable, "-u", __file__] + args, env=env, capture_output=True, text=True)
    lines = [l for l in out.stdout.splitlines() if l.startswith("PREPHASH")]
    timing = [l.strip() for l in out.stdout.splitlines() if "timing]" in l]
    print(f"workers={w}: {lines[0] if lines else 'NO HASH (exit %d)' % out.returncode}")
    print(f"           {timing[0] if timing else ''}")
    if not lines:
        print(out.stdout[-2000:], out.stderr[-2000:])
    res[w] = lines[0] if lines else None
ok = res["1"] is not None and res["1"] == res[workers]
print("IDENTICAL" if ok else "DIFFERENT")
if sabotage:
    caught = res["1"] is not None and res[workers] is not None and not ok
    print("SABOTAGE CAUGHT" if caught else "SABOTAGE MISSED -- the comparison cannot see a planted error")
    sys.exit(0 if caught else 1)
sys.exit(0 if ok else 1)
