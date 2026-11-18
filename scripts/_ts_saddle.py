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
CAP_FOR_EDGES = NCAP          # addendum 1 (tent control sets its own cap)


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
            if seq[i][1] >= CAP_FOR_EDGES:          # addendum 1: a capped plateau is refined at its two EDGES
                if i > 0:
                    out.append((seq[i][1], seq[i - 1][0], seq[i][0]))
                if j + 1 < m:
                    out.append((seq[i][1], seq[j][0], seq[j + 1][0]))
            else:
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
    refined = set()
    for lev in range(1, MAXLEV + 1):
        brs = []
        for seq in seqs:
            brs += local_max_brackets(seq, thr)
        brs = [br for br in brs if (br[2] - br[1]) > WREL * abs(br[1]) and br[2] > br[1]
               and (br[1], br[2]) not in refined]                      # addendum 1: never re-refine a bracket
        brs.sort(key=lambda t: -t[0])
        brs = brs[:MAXB]
        refined.update((br[1], br[2]) for br in brs)
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
        global CAP_FOR_EDGES
        CAP_FOR_EDGES = 30
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
    if mode == "precision":
        workers = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        g = guard_ok()
        if g:
            print(f"[precision] NOT STARTED: guard {g}", flush=True)
            return
        peaks = top_peaks(load_pts("ts"), 30)
        with Pool(workers) as pool:
            res = pool.map(life_dd, [("ts", hi, lo, "R2") for (hi, lo, _) in peaks], chunksize=1)
        rows = [dict(hi=hi, lo=lo, n_R1=n1, n_R2=r[2], status_R2=r[3]) for (hi, lo, n1), r in zip(peaks, res)]
        agree = sum(r["n_R1"] == r["n_R2"] for r in rows)
        json.dump(dict(rows=rows, agree=agree, total=len(rows)), open(os.path.join(OUT, "precision.json"), "w"), indent=1)
        print(f"VERDICT-precision: {agree}/{len(rows)} identical at R2 (pass needs >= 27/30)", flush=True)
        return
    if mode == "analyse":
        which = sys.argv[2:] or ["kerr", "ts"]
        out = {}
        for s_ in which:
            out[s_] = analyse(s_)
            print(f"[{s_}] {out[s_]['n_points']} points; N(t) (LOWER BOUNDS) = {out[s_]['Nt']}; "
                  f"h = {out[s_]['h']}; 95% CI = {out[s_]['ci']}", flush=True)
        if which == ["kerr", "ts"]:
            out["verdict"] = verdict(out)
            print("VERDICT:", json.dumps(out["verdict"]), flush=True)
            json.dump(out, open(os.path.join(OUT, "analysis.json"), "w"), indent=1)
        return
    raise SystemExit(f"unknown mode {mode}")


# ---------------------------------------------------------------------------------------------------- analysis
# Fixed 2026-11-18 AFTER the run finished and BEFORE any TS output was read (prereg: "precision and analyse are added
# after the run, before reading results"). Operational choices the prereg left open are stated here:
#  * "peak" = a local maximum of n over all evaluated points sorted by x0 (a plateau counts once, represented by its
#    first point); the 30 longest-lived = sorted by (-n, x0).
#  * bootstrap over level-0 cells: cell i = [g_i, g_{i+1}) of the level-0 grid (the last grid point joins the last
#    cell). Each run of {n >= t} is assigned to the cell holding its first point; a resample draws 2000 cells with
#    replacement and sums their run-start counts. 1000 resamples, seed 20261118. A resample whose h is undefined
#    counts as h <= 0 (conservative for the saddle reading). CI = 2.5 / 97.5 percentiles.
#  * h = least-squares slope of ln N(t) on t over t in [50, 400] with N(t) >= 2; needs >= 2 such t, else undefined.
#  * "grows with t" is read as: h > 0 with the bootstrap CI excluding 0.
def load_pts(sys_):
    d = {}
    for line in open(os.path.join(OUT, f"{sys_}.jsonl")):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        d[(r["hi"], r["lo"])] = r["n"]
    return sorted(((hi, lo, n) for (hi, lo), n in d.items()), key=lambda t: mpv(t[:2]))


def top_peaks(pts, k):
    peaks, i, m = [], 0, len(pts)
    while i < m:
        j = i
        while j + 1 < m and pts[j + 1][2] == pts[i][2]:
            j += 1
        left = pts[i - 1][2] if i > 0 else -10
        right = pts[j + 1][2] if j + 1 < m else -10
        if pts[i][2] > left and pts[i][2] > right:
            peaks.append(pts[i])
        i = j + 1
    peaks.sort(key=lambda t: (-t[2], mpv(t[:2])))
    return peaks[:k]


def fit_h2(Nt, ts):
    q = [(t, math.log(Nt[t])) for t in ts if 50 <= t <= 400 and Nt[t] >= 2]
    if len(q) < 2:
        return None
    return float(np.polyfit([a for a, _ in q], [b for _, b in q], 1)[0])


def analyse(sys_):
    pts = load_pts(sys_)
    a, b = WIN[sys_]
    grid = [mpv(split(a + (b - a) * i / (G0 - 1))) for i in range(G0)]
    starts = np.zeros((G0 - 1, len(TS_T)), int)
    import bisect
    xs = [mpv(p[:2]) for p in pts]
    for k, t in enumerate(TS_T):
        prev = False
        for x, p in zip(xs, pts):
            on = p[2] >= t
            if on and not prev:
                c = min(max(bisect.bisect_right(grid, x) - 1, 0), G0 - 2)
                starts[c, k] += 1
            prev = on
    Nt = {t: int(starts[:, k].sum()) for k, t in enumerate(TS_T)}
    h = fit_h2(Nt, TS_T)
    rng = np.random.default_rng(20261118)
    hs = []
    for _ in range(1000):
        idx = rng.integers(0, G0 - 1, G0 - 1)
        s = starts[idx].sum(axis=0)
        hb = fit_h2({t: int(s[k]) for k, t in enumerate(TS_T)}, TS_T)
        hs.append(hb if hb is not None else -math.inf)
    hs = np.array(hs)
    ci = [float(np.percentile(hs, 2.5)), float(np.percentile(hs, 97.5))]
    return dict(n_points=len(pts), Nt=Nt, h=h, ci=ci, undefined_resamples=int(np.isinf(hs).sum()))


def verdict(out):
    ctl = json.load(open(os.path.join(OUT, "control.json")))
    ctl_ok = 0.6 <= ctl["h"] <= 0.8
    kerr_ok = all(v <= 2 for v in out["kerr"]["Nt"].values())
    ts = out["ts"]
    prec = None
    if os.path.exists(os.path.join(OUT, "precision.json")):
        pr = json.load(open(os.path.join(OUT, "precision.json")))
        bad = [r["n_R1"] for r in pr["rows"] if r["n_R1"] != r["n_R2"]]
        prec = dict(agree=pr["agree"], total=pr["total"], pass_=pr["agree"] >= 27,
                    unreliable_above_n=(min(bad) if (bad and pr["agree"] < 27) else None))
    Nt = ts["Nt"]
    if not (ctl_ok and kerr_ok):
        v = "VOID (control failed)"
    elif ts["h"] is not None and ts["h"] > 0 and ts["ci"][0] > 0 and Nt[400] >= 3 * Nt[100]:
        v = "SUPPORTS CHAOTIC SADDLE"
    elif all(x <= 3 for x in Nt.values()):
        v = "SUPPORTS NO SADDLE"
    else:
        v = "INCONCLUSIVE"
    return dict(control_h=ctl["h"], control_pass=ctl_ok, kerr_pass=kerr_ok, precision=prec, ts=v)


if __name__ == "__main__":
    main()
