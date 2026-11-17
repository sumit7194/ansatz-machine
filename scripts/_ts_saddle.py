#!/usr/bin/env python3
"""Lifetime-interval (topological-entropy) test of the TS delta=2 capture edge (data/ts_chaos/SADDLE_PREREGISTRATION.md).

n(x0) = section crossings before plunge/escape, capped at 600, along the line y = 0, p_x = 0 across a window W.
N(t) = number of maximal runs of evaluated points (sorted by x0) with n >= t. A chaotic saddle gives N(t) ~ e^{h t};
a smooth boundary keeps N(t) bounded. Search: a level-0 grid of 2001 points; then, at each level, every local maximum
(a plateau counts once) with n >= THR gets 17 equally spaced points across its bracket; at most 300 brackets per level
(highest n first); stop at bracket width < 1e-18 relative, level 10, or the orbit budget.
x0 values are double-double (hi, lo), generated with mpmath at 60 digits.
    .venv/bin/python scripts/_ts_saddle.py control                 # tent-map positive control (seconds)
    .venv/bin/python scripts/_ts_saddle.py run <ts|kerr> [workers]   # checkpointed, guarded
    .venv/bin/python scripts/_ts_saddle.py precision [workers]      # top-30 TS peaks at R2
    .venv/bin/python scripts/_ts_saddle.py analyse
"""
import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpmath as mp  # noqa: E402
import numpy as np  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "ts_chaos", "saddle")
mp.mp.dps = 60
NCAP, G0, SUB, MAXB, MAXLEV, WREL = 600, 2001, 17, 300, 10, 1e-18
TS_T = [50, 100, 150, 200, 300, 400, 500, 600]
WIN = {"ts": (mp.mpf("9.912067"), mp.mpf("9.945202")),
       "kerr": (mp.mpf("4.9933985") - mp.mpf("0.015"), mp.mpf("4.9933985") + mp.mpf("0.015"))}
BUDGET = {"ts": 10000, "kerr": 3000}
THR = 20


def split(v):
    hi = float(v)
    return hi, float(v - mp.mpf(hi))


def mpv(p):
    return mp.mpf(p[0]) + p[1]


# ---------------------------------------------------------------------------------------------------- lifetime functions
_E = {}


def life_dd(args):
    sys_, hi, lo, rung = args
    import _hp_probe as P
    if sys_ not in _E:
        _E[sys_] = P.dd_engine(sys_)
    lv = P.LEV[sys_]
    r = _E[sys_].orbit(hi, lv["E"], lv["L"], tol=P.R[rung], nsec=NCAP, x0l=lo)
    n = NCAP if (r["status"] == 0) else (max(r["n"], 0) if r["status"] in (1, 2) else -1)
    return hi, lo, n, r["status"]


def life_tent(x):
    """Middle-thirds open map: escape when x in (1/3, 2/3); else x -> 3x (left) or 3x - 2 (right). Exact rationals."""
    n = 0
    while n < 30:
        if Fraction(1, 3) < x < Fraction(2, 3) or x < 0 or x > 1:
            return n
        x = 3 * x if x <= Fraction(1, 3) else 3 * x - 2
        n += 1
    return 30


# ---------------------------------------------------------------------------------------------------- search
def local_max_brackets(seq, thr):
    """seq: list of (x_mp, n) sorted by x. Return brackets (n, a, b) around plateau local maxima with n >= thr."""
    out = []
    i, m = 0, len(seq)
    while i < m:
        j = i
        while j + 1 < m and seq[j + 1][1] == seq[i][1]:
            j += 1
        left = seq[i - 1][1] if i > 0 else -10
        right = seq[j + 1][1] if j + 1 < m else -10
        if seq[i][1] >= thr and seq[i][1] > left and seq[i][1] > right:
            a = seq[i - 1][0] if i > 0 else seq[i][0]
            b = seq[j + 1][0] if j + 1 < m else seq[j][0]
            out.append((seq[i][1], a, b))
        i = j + 1
    return out


def guard_ok():
    try:
        st = os.statvfs("/")
        if st.f_bavail * st.f_frsize / 2**30 < 5.0:
            return "free disk < 5 GB"
        lvl = int(subprocess.run(["sysctl", "-n", "kern.memorystatus_vm_pressure_level"], capture_output=True,
                                 text=True, timeout=10).stdout.strip() or 1)
        if lvl > 1:
            return f"memory pressure level {lvl}"
        sw = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True, timeout=10).stdout
        used = float(sw.split("used = ")[1].split("M")[0])
        if used > 2048:
            return f"swap {used:.0f} MB > 2 GB"
    except Exception as e:                                     # a guard that cannot read must not pass silently
        return f"guard read failed: {e}"
    return None


def search(sys_, evaluate, budget, thr, label, pool=None, ck=None):
    """Generic recursive peak refinement. evaluate(list of (hi,lo)) -> list of n. Returns all (x_mp, n)."""
    done = {}
    if ck and os.path.exists(ck):
        for line in open(ck):
            try:
                r = json.loads(line)
                done[(r["hi"], r["lo"])] = r["n"]
            except ValueError:
                pass
    fh = open(ck, "a") if ck else None
    count = [0]

    def ev(points):
        todo = [p for p in points if p not in done]
        if todo:
            ns = evaluate(todo, fh)
            for p, n in zip(todo, ns):
                done[p] = n
        count[0] = len(done)
        return [done[p] for p in points]

    a, b = WIN[sys_] if sys_ in WIN else (mp.mpf(0), mp.mpf(1))
    pts = [split(a + (b - a) * i / (G0 - 1)) for i in range(G0)]
    ev(pts)
    levels = [dict(level=0, points=G0, brackets=None)]
    seqs = [[(mpv(p), done[p]) for p in pts]]
    for lev in range(1, MAXLEV + 1):
        brs = []
        for seq in seqs:
            brs += local_max_brackets(seq, thr)
        brs = [br for br in brs if (br[2] - br[1]) > WREL * abs(br[1]) and br[2] > br[1]]
        brs.sort(key=lambda t: -t[0])
        brs = brs[:MAXB]
        if not brs or count[0] >= budget:
            break
        new_seqs = []
        for n0, lo_, hi_ in brs:
            if count[0] >= budget:
                break
            sub = [split(lo_ + (hi_ - lo_) * k / (SUB - 1)) for k in range(SUB)]
            ns = ev(sub)
            new_seqs.append([(mpv(p), n) for p, n in zip(sub, ns)])
        levels.append(dict(level=lev, brackets=len(new_seqs), evaluated=count[0],
                           max_n=max((n for s in new_seqs for _, n in s), default=None),
                           min_width=float(min(br[2] - br[1] for br in brs))))
        print(f"  [{label}] level {lev}: {len(new_seqs)} brackets refined, {count[0]} orbits so far, "
              f"min bracket width {levels[-1]['min_width']:.2e}", flush=True)
        seqs = new_seqs
        if guard_ok():
            print(f"  [{label}] STOP GUARD: {guard_ok()} (checkpoint kept)", flush=True)
            break
    if fh:
        fh.close()
    allpts = sorted(((mpv(p), n) for p, n in done.items()), key=lambda t: t[0])
    return allpts, levels


def N_of_t(allpts, ts):
    out = {}
    for t in ts:
        runs, inrun = 0, False
        for _, n in allpts:
            if n >= t and not inrun:
                runs += 1
            inrun = n >= t
        out[t] = runs
    return out


def fit_h(Nt, ts):
    pts = [(t, math.log(Nt[t])) for t in ts if Nt[t] >= 2]
    if len(pts) < 3:
        return float("nan")
    x = np.array([p[0] for p in pts], float)
    y = np.array([p[1] for p in pts])
    return float(np.polyfit(x, y, 1)[0])


def main():
    mode = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    if mode == "control":
        def ev(points, fh):
            return [life_tent(Fraction(p[0]) + Fraction(p[1])) for p in points]
        WIN["tent"] = (mp.mpf(0), mp.mpf(1))
        allpts, levels = search("tent", ev, 20000, 1, "tent")
        ts = list(range(1, 11))
        Nt = N_of_t(allpts, ts)
        h = fit_h(Nt, [t for t in ts if 2 <= t <= 8])
        print("  tent N(t):", Nt, flush=True)
        print(f"VERDICT-control: h = {h:.3f} (expected ln 2 = 0.693; pass band [0.6, 0.8]) -> "
              f"{'PASS' if 0.6 <= h <= 0.8 else 'FAIL'}", flush=True)
        json.dump(dict(Nt=Nt, h=h, levels=levels), open(os.path.join(OUT, "control.json"), "w"), indent=1)
        return
    if mode == "run":
        sys_ = sys.argv[2]
        workers = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        g = guard_ok()
        if g:
            print(f"[{sys_}] NOT STARTED: guard {g}", flush=True)
            return
        pool = Pool(workers)

        def ev(points, fh):
            res = {}
            for k, (hi, lo, n, st) in enumerate(pool.imap(life_dd, [(sys_, p[0], p[1], "R1") for p in points], chunksize=1)):
                res[(hi, lo)] = n
                fh.write(json.dumps(dict(hi=hi, lo=lo, n=n, status=st)) + "\n")
                fh.flush()
                if k % 25 == 24 and guard_ok():
                    raise SystemExit(f"STOP GUARD: {guard_ok()} (checkpoint kept; rerun resumes)")
            return [res[p] for p in points]
        t0 = time.time()
        allpts, levels = search(sys_, ev, BUDGET[sys_], THR, sys_, ck=os.path.join(OUT, f"{sys_}.jsonl"))
        pool.close()
        Nt = N_of_t(allpts, TS_T)
        json.dump(dict(levels=levels, Nt=Nt, n_points=len(allpts)), open(os.path.join(OUT, f"{sys_}_summary.json"), "w"),
                  indent=1)
        print(f"VERDICT-run [{sys_}]: {len(allpts)} orbits, N(t) = {Nt}  [{time.time() - t0:.0f}s]", flush=True)
        return
    raise SystemExit(f"unknown mode {mode} (precision and analyse are added after the run, before reading results)")


if __name__ == "__main__":
    main()
