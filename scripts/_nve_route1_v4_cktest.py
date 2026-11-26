#!/usr/bin/env python3
"""Resume test for v4's per-step checkpoint (office, 2026-11-26, the Bridge's condition before the 9/10 run).
Kills nothing: an interruption is SIMULATED by writing a partial checkpoint file (complete records + a torn half line,
as a power cut mid-write would leave), then resuming from it. Spin 3/5, rho = 4 k-square, the lasso (703 steps),
CK_EVERY = 100. Every file lives under data/nve/eps/cktest/ (never the production checkpoint).
  1. reference: the dq list with NO checkpoint;
  2. full: with a fresh checkpoint A; must equal 1 exactly (every bound, as an exact number);
  3. resume: file B = the first 3 records of A + half of the 4th (torn); must report "resuming after 300", drop the
     torn tail, finish, equal 1 exactly, and leave B record-for-record equal to A;
  4. gate: file C = A with record 2 garbled; loading must RAISE (a bad record mid-file is not silently skipped);
  5. control that can fail: a planted change of one stored bound in a copy D must make the resumed list DIFFER from 1
     (so the comparison in 2-3 is not vacuous).
    NVE_SPIN=3/5 R1_R0=1.35 nice -n 12 <quantum python> -I -u scripts/_nve_route1_v4_cktest.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flint import acb, arb             # noqa: E402
import _nve_route1_segment_v2 as V     # noqa: E402
import _nve_route1_segment_v4 as W     # noqa: E402

D = os.path.join(V.OUTD, "cktest")
os.makedirs(D, exist_ok=True)
W.CK_EVERY = 100
W.LOG4 = os.path.join(D, "cktest.out")
say = W.say


def same(a, b):
    return len(a) == len(b) and all(x.mid() == y.mid() and x.rad() == y.rad() for x, y in zip(a, b))


def run(ckfile):
    W.CKFILE = ckfile
    return W.dq_list_v4(st1, kc, R, lau_c, laud_c, name=None if ckfile is None else "lasso")


ref = json.load(open(os.path.join(V.OUTD, V.FLOATS)))["21/20"]
sing = [complex(float(p[0]), float(p[1])) for p in ref["points"]]
lasso = [complex(float(p[0]), float(p[1])) for p in ref["lasso"]]
(kc, half), = V.seg_centres(1)
lau_c, laud_c = V.laurent(acb(kc)), V.laurent(acb(kc), True)
M1, st1 = V.walk(lasso, acb(kc), lau_c, sing, record=True)
rb = arb(4)
R = (half * (rb + 1 / rb) / 2).upper()
A, B, C, Dp = (os.path.join(D, f) for f in ("A.jsonl", "B.jsonl", "C.jsonl", "D.jsonl"))
for f in (A, B, C, Dp, W.LOG4):
    if os.path.exists(f):
        os.remove(f)                     # files of a previous run of THIS test only (in cktest/)
say(f"== v4 checkpoint resume test == {V.SEG}; lasso {len(st1)} steps; rho = 4 (R <= {V.hi_sci(R)}); CK_EVERY = 100")
L0 = run(None)[0]
LA = run(A)[0]
okA = same(L0, LA)
linesA = open(A, "rb").read().split(b"\n")[:-1]
say(f"  1-2. no-checkpoint list vs fresh-checkpoint list: identical {okA}; A has {len(linesA)} records")
with open(B, "wb") as fh:
    fh.write(b"\n".join(linesA[:3]) + b"\n" + linesA[3][: len(linesA[3]) // 2])
LB = run(B)[0]
linesB = open(B, "rb").read().split(b"\n")[:-1]
okB = same(L0, LB) and linesB == linesA
log = open(W.LOG4).read()
okmsg = "resuming after 300 of" in log and "torn last record" in log
say(f"  3. resume from 3 records + a torn half record: identical list {same(L0, LB)}; B == A record for record "
    f"{linesB == linesA}; resume and torn-tail messages printed {okmsg}")
with open(C, "wb") as fh:
    bad = linesA[:]
    bad[1] = bad[1][:20] + b"#garbled#" + bad[1][29:]
    fh.write(b"\n".join(bad) + b"\n")
try:
    W.CKFILE = C
    W.ck_load(W.ck_key(st1, R, "lasso"))
    okC = False
except Exception as e:            # noqa: BLE001  (any failure to load IS the expected outcome)
    okC = True
    say(f"  4. garbled record mid-file: load raised ({type(e).__name__}) -> gate works: {okC}")
if not okC:
    say("  4. garbled record mid-file: load did NOT raise -> GATE FAILED")
r0 = json.loads(linesA[0])
m, e = r0["vals"][5][1]
r0["vals"][5][1] = [m + 1, e]
with open(Dp, "wb") as fh:
    fh.write(json.dumps(r0).encode() + b"\n" + b"\n".join(linesA[1:]) + b"\n")
LD = run(Dp)[0]
okD = not same(L0, LD)
say(f"  5. planted change of one stored bound: resumed list differs from the reference {okD} (must be True)")
allok = okA and okB and okmsg and okC and okD
say(f"  RESUME TEST: {'PASS' if allok else 'FAIL'}")
sys.exit(0 if allok else 1)
