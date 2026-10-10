#!/usr/bin/env python3
"""Uncertainty exponent of the survive/plunge boundary (section 150, the Bridge's option B; pre-registration
data/ts_chaos/ALPHA_PREREGISTRATION.md). For x0 uniform in a window W around the boundary, x0 is UNCERTAIN at scale
eps if the outcome (status after nsec crossings) at x0 differs from that at x0 - eps or x0 + eps. The uncertain
fraction scales as f(eps) ~ eps^alpha: alpha = 1 for a smooth boundary (isolated boundary points, integrable), alpha < 1
for a fractal basin boundary (chaotic). Same orbit settings as the v2 scan (tol 1e-11, nsec 300).
    .venv/bin/python scripts/_ts_chaos_alpha.py [workers=2] [K=1500]                       # the 81c988f run
    .venv/bin/python scripts/_ts_chaos_alpha.py 2 1500 --ts ts35 --E 0.95 --L -5.333333333333334 --kerr kerr35 --tag p35
    ... --nsec 600 (horizon test; the window is still chosen from the 300-crossing dense scan)
"""
import json
import os
import random
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

from _ts_chaos_scan import PLUNGE_X, SYSTEMS, _engine, _level_job, find_Lsep  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "ts_chaos")
E0, L_TS, SYS_TS, SYS_K = 0.97, 5.125, "ts45", "kerr45"
EPS = (3e-3, 1e-3, 3e-4, 1e-4, 3e-5)
MIN_HITS = 10


def plunge_cut(eng, E, L, x_in):
    """Exactly the v2 scan's plunge cut (_level_job): below the equatorial ridge of W(x, 0), never above PLUNGE_X."""
    xs_r = np.geomspace(x_in * 1.0001, 60.0, 4000)
    Wv = np.array([eng.W(xx, 0.0, E, L) for xx in xs_r])
    imax = [i for i in range(1, len(Wv) - 1) if Wv[i] > Wv[i - 1] and Wv[i] >= Wv[i + 1]]
    x_ridge = float(xs_r[imax[0]]) if imax else None
    return max(x_in, PLUNGE_X if x_ridge is None else min(PLUNGE_X, 0.8 * x_ridge))


def window(level, xmax_inner=None):
    """W rule (pre-registered): in the INNER survive/plunge window, from the first to the last status change of the
    dense seeding, padded by 2 dense steps each side."""
    w1 = level["windows"][0]
    orb = sorted((o for o in level["orbits"] if w1[0] <= o["x0"] <= w1[1]), key=lambda o: o["x0"])
    ch = [i for i in range(len(orb) - 1) if orb[i]["status"] != orb[i + 1]["status"]]
    step = (w1[1] - w1[0]) / (len(orb) - 1)
    return orb[ch[0]]["x0"] - 2 * step, orb[ch[-1] + 1]["x0"] + 2 * step, len(ch), step


NSEC = 300


def _sample(a):
    sysname, L, x0, xpl, E0, NSEC = a
    spec, m, x_in = SYSTEMS[sysname]
    eng = _engine(spec)

    def st(xx):
        r = eng.orbit(float(xx), E0, L, nsec=NSEC, tmax=5e6, xmin=xpl, xmax=2000.0, tol=1e-11)
        return -1 if r is None else int(r["status"])
    c = st(x0)
    out = dict(x0=x0, c=c, pm={})
    for e in EPS:
        out["pm"][str(e)] = (st(x0 - e), st(x0 + e))
    return out


def analyse(samples):
    valid = [s for s in samples if s["c"] in (0, 1, 2) and all(v in (0, 1, 2) for pm in s["pm"].values() for v in pm)]
    U = np.array([[int(s["pm"][str(e)][0] != s["c"] or s["pm"][str(e)][1] != s["c"]) for e in EPS] for s in valid])
    hits = U.sum(0)
    f = hits / len(valid)
    use = hits >= MIN_HITS

    def fit(Um):
        h = Um.sum(0)
        ok = use & (h > 0)
        if ok.sum() < 3:
            return float("nan")
        lx, ly = np.log(np.array(EPS)[ok]), np.log(h[ok] / len(Um))
        w = h[ok]                                   # Poisson: var(log f) ~ 1/hits
        A = np.vstack([lx, np.ones_like(lx)]).T * np.sqrt(w)[:, None]
        return float(np.linalg.lstsq(A, ly * np.sqrt(w), rcond=None)[0][0])
    alpha = fit(U)
    rng = np.random.default_rng(150)
    boots = [fit(U[rng.integers(0, len(U), len(U))]) for _ in range(1000)]
    boots = np.array([b for b in boots if b == b])
    lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (float("nan"), float("nan")))
    return dict(n_valid=len(valid), n_invalid=len(samples) - len(valid), hits=hits.tolist(), f=f.tolist(),
                fit_points=int(use.sum()), alpha=alpha, ci95=[float(lo), float(hi)])


def main():
    def arg(fl, dflt, cast=str):
        return cast(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else dflt
    pos = [a for a in sys.argv[1:3] if not a.startswith("--")]
    workers = int(pos[0]) if len(pos) > 0 else 2
    K = int(pos[1]) if len(pos) > 1 else 1500
    global E0, L_TS, SYS_TS, SYS_K
    SYS_TS, E0, L_TS, SYS_K = arg("--ts", SYS_TS), arg("--E", E0, float), arg("--L", L_TS, float), arg("--kerr", SYS_K)
    nsec, tag = arg("--nsec", 300, int), arg("--tag", "")
    sign = 1 if L_TS > 0 else -1
    # TS level: stored v2 scan (bit-identical on re-run, cachecheck)
    lv_ts = [l for l in json.load(open(os.path.join(D, f"bscan_{SYS_TS}_v2.json")))["levels"]
             if abs(l["E"] - E0) < 1e-12 and abs(l["L"] - L_TS) < 1e-9][0]
    spec_ts, m_ts, xin_ts = SYSTEMS[SYS_TS]
    spec_k, m_k, xin_k = SYSTEMS[SYS_K]
    e_ts, e_k = _engine(spec_ts), _engine(spec_k)
    Ls_ts, Ls_k = abs(find_Lsep(e_ts, E0, m_ts, xin_ts, sign)), abs(find_Lsep(e_k, E0, m_k, xin_k, sign))
    eps_sep = (abs(L_TS) - Ls_ts) / Ls_ts
    L_K = sign * Ls_k * (1 + eps_sep)
    print(f"separatrix-matched: TS L_sep {Ls_ts:.6f}, eps {eps_sep:+.5f} at L = {L_TS}; Kerr L_sep {Ls_k:.6f} -> Kerr L = {L_K:.6f}",
          flush=True)
    lv_k = _level_job((spec_k, E0, L_K, xin_k, 60, 200, 300))
    levels = {SYS_TS: (L_TS, lv_ts, plunge_cut(e_ts, E0, L_TS, xin_ts)), SYS_K: (L_K, lv_k, plunge_cut(e_k, E0, L_K, xin_k))}
    res = {}
    for s, (L, lv, xpl) in levels.items():
        a, b, nch, step = window(lv)
        print(f"[{s}] L = {L:.6f}: inner window {lv['windows'][0]}, {nch} status changes in the dense seeding "
              f"(step {step:.2e}) -> W = [{a:.6f}, {b:.6f}] (width {b - a:.4f}); plunge cut {xpl:.3f}", flush=True)
        rnd = random.Random(1500 + len(s))
        jobs = [(s, L, rnd.uniform(a, b), xpl, E0, nsec) for _ in range(K)]
        with Pool(workers) as pool:
            samples = pool.map(_sample, jobs, chunksize=8)
        an = analyse(samples)
        an.update(system=s, E=E0, L=L, W=[a, b], dense_changes=nch, eps=list(EPS), nsec=nsec)
        res[s] = dict(analysis=an, samples=samples)
        print(f"  [{s}] valid {an['n_valid']} (invalid {an['n_invalid']}): uncertain hits per eps {dict(zip(EPS, an['hits']))}",
              flush=True)
        print(f"VERDICT-alpha [{s}{' ' + tag if tag else ''}] E={E0} L={L:.4f} nsec={nsec}: alpha = {an['alpha']:.3f}  95% CI [{an['ci95'][0]:.3f}, {an['ci95'][1]:.3f}]  "
              f"({an['fit_points']} eps points with >= {MIN_HITS} hits)", flush=True)
        json.dump(res, open(os.path.join(D, f"alpha{'_' + tag if tag else ''}.json"), "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
