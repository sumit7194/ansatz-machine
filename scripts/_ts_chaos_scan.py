#!/usr/bin/env python3
"""TS delta=2 chaos search driver (data/ts_chaos/PREREGISTRATION.md, amendments 1-2 frozen at c0358a1).

For each system (Kerr controls via the TS2 pipeline; TS delta=2 at p = 4/5 and 3/5) and each energy E:
  1. map equatorial bound pockets: intervals of x with W(x, 0) <= -1 that are closed (not touching the inner
     boundary x_in, nor x_far);
  2. find the SEPARATRIX value L_sep(E): the smallest |L| at which a closed pocket exists (below it the pocket merges
     with the plunge region). Chaos in ZV sat exactly here (section 106);
  3. scan seeds x0 across pockets at |L| = L_sep * (1 + eps) for a few eps (near-separatrix) AND far-field pockets
     (Dubeibe-like, inner turning point > far_min);
  4. per orbit: frequency drift (fd) and excess stretching S_ex at tol 1e-11; candidates (fd > 0.0115 and S_ex >= 10)
     re-run at tol 1e-13 and kept only if both still fire.
Both signs of L (pro/retrograde). Parallel over seeds.

    .venv/bin/python scripts/_ts_chaos_scan.py --system ts45 [--workers 6] [--quick]
"""
import json
import math
import os
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "ts_chaos")
SYSTEMS = {   # spec, mass m (sigma = 1), inner boundary x_in (ring for TS, horizon x = 1 for Kerr)
    "kerr45": ("ts2kerr:4/5", 1 / 0.8, 1.0005),
    "kerr35": ("ts2kerr:3/5", 1 / 0.6, 1.0005),
    "ts45": ("ts2:4/5", 2 / 0.8, 1.057417014479 + 0.01),
    "ts35": ("ts2:3/5", 2 / 0.6, 1.136801654533 + 0.01),
    "zv2": ("zv:2", 2.0, 1.0005),        # POSITIVE CONTROL for the search DESIGN (known thin layer, section 106)
}
FD_THR, SEX_THR = 0.0115, 10.0
_ENG = None
_ENGS = {}


def _engine(spec):
    """One Engine per METRIC per process. (It was a single global, which returned the wrong metric to a worker serving
    mixed systems. All scans so far ran one system per pool, so they were unaffected; caught by check3.)"""
    global _ENG
    if spec not in _ENGS:
        from _kt_exact_op import get_metric
        from _ts_chaos import Engine
        gi, name = get_metric(spec)
        _ENGS[spec] = Engine(gi, name)
    _ENG = _ENGS[spec]
    return _ENGS[spec]


def pockets(eng, E, L, x_in, x_far=400.0, n=6000):
    xs = np.geomspace(x_in, x_far, n)
    allowed = np.array([eng.W(xx, 0.0, E, L) <= -1.0 for xx in xs])
    out, i = [], 0
    while i < n:
        if allowed[i]:
            j = i
            while j + 1 < n and allowed[j + 1]:
                j += 1
            out.append((float(xs[i]), float(xs[j]), i == 0, j == n - 1))
            i = j + 1
        else:
            i += 1
    return out          # (a, b, touches_inner, touches_far)


def closed_pockets(eng, E, L, x_in):
    return [(a, b) for a, b, ti, tf in pockets(eng, E, L, x_in) if not ti and not tf]


def find_Lsep(eng, E, m, x_in, sign):
    """Smallest |L| (in units of m, scanned from 1.5 m up) with a closed equatorial pocket."""
    for lm in np.arange(1.5, 8.0, 0.01):
        L = sign * lm * m
        if closed_pockets(eng, E, L, x_in):
            return float(L)
    return None


def _orbit_job(args):
    spec, x0, E, L, x_in = args
    eng = _engine(spec)
    r = eng.orbit(x0, E, L, nsec=600, tmax=5e6, xmin=x_in, xmax=2000.0, tol=1e-11)
    if r is None:
        return None
    cand = (r["fd"] == r["fd"]) and r["fd"] > FD_THR and r["sex"] >= SEX_THR
    res = dict(x0=x0, E=E, L=L, n=r["n"], status=r["status"], fd=r["fd"], sex=r["sex"], slope=r["slope"],
               drift=r["drift"], cand=bool(cand))
    if cand:
        r2 = eng.orbit(x0, E, L, nsec=600, tmax=5e6, xmin=x_in, xmax=2000.0, tol=1e-13)
        res.update(fd2=r2["fd"], sex2=r2["sex"], n2=r2["n"], status2=r2["status"], drift2=r2["drift"],
                   confirmed=bool((r2["fd"] == r2["fd"]) and r2["fd"] > FD_THR and r2["sex"] >= SEX_THR))
    return res


def main():
    def arg(fl, d=None, c=str):
        return c(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else d
    sysname = arg("--system")
    workers = arg("--workers", 6, int)
    quick = "--quick" in sys.argv
    spec, m, x_in = SYSTEMS[sysname]
    eng = _engine(spec)
    t0 = time.time()
    Es = [0.95, 0.97] if quick else [0.93, 0.94, 0.95, 0.96, 0.97, 0.98]
    eps_list = [0.002, 0.01, 0.03] if quick else [0.001, 0.003, 0.01, 0.03, 0.1]
    nseed = 12 if quick else 30
    jobs, meta = [], []
    for E in Es:
        for sign in (+1, -1):
            Ls = find_Lsep(eng, E, m, x_in, sign)
            if Ls is None:
                print(f"  E={E} sign={sign:+d}: no closed pocket found", flush=True)
                continue
            levels = [("sep", Ls * (1 + e)) for e in eps_list] + [("far", Ls * 1.6)]
            for kind, L in levels:
                cps = closed_pockets(eng, E, L, x_in)
                if not cps:
                    continue
                a, b = max(cps, key=lambda ab: ab[1] - ab[0])
                meta.append(dict(E=E, L=L, kind=kind, pocket=[a, b], Lsep=Ls))
                for x0 in np.linspace(a, b, nseed + 2)[1:-1]:
                    jobs.append((spec, float(x0), E, float(L), x_in))
    print(f"[{sysname}] {spec}: {len(meta)} (E, L) levels, {len(jobs)} orbits; workers {workers} "
          f"[setup {time.time()-t0:.0f}s]", flush=True)
    with Pool(workers) as pool:
        res = [r for r in pool.map(_orbit_job, jobs, chunksize=4) if r is not None]
    ncand = sum(r["cand"] for r in res)
    ncon = sum(r.get("confirmed", False) for r in res)
    nplunge = sum(r["status"] == 1 for r in res)
    maxdr = max(r["drift"] for r in res) if res else float("nan")
    summary = dict(system=sysname, spec=spec, levels=meta, n_orbits=len(res), candidates=ncand, confirmed=ncon,
                   plunged=nplunge, max_shell_drift=maxdr, seconds=round(time.time() - t0))
    tag = sysname + ("_quick" if quick else "")
    with open(os.path.join(OUT, f"scan_{tag}.json"), "w") as fh:
        json.dump(dict(summary=summary, orbits=res), fh)
    print(f"VERDICT [{sysname}] orbits {len(res)}: candidates (fd>{FD_THR} & S_ex>={SEX_THR}) {ncand}, CONFIRMED at "
          f"tol 1e-13 {ncon}; plunged {nplunge}; max |2H+1| {maxdr:.1e}  [{time.time()-t0:.0f}s]", flush=True)
    for r in res:
        if r.get("confirmed"):
            print(f"  CHAOS E={r['E']} L={r['L']:.4f} x0={r['x0']:.5f}: fd {r['fd']:.4f}/{r['fd2']:.4f}, "
                  f"S_ex {r['sex']:.1f}/{r['sex2']:.1f}, n {r['n']}/{r['n2']}, status {r['status']}/{r['status2']}",
                  flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ------------------------------------------------------------------------------------------------------------------
# DESIGN v2 ("boundary"), amendment 3. The v1 design (closed equatorial pockets, uniform seeds) FAILED its search-design
# control: 0 detections on ZV delta=2, where a layer is known (section 106). That layer sits at the trapped/plunge
# boundary of an OPEN level. v2 hunts that boundary: a coarse x0 scan classifies survive vs plunge, then dense
# seeding around every transition.
PLUNGE_X = 1.5          # orbits diving below x = 1.5 are plunging; integrating into the singular core only burns steps
def _level_job(args):
    spec, E, L, x_in, ncoarse, ndense, nsec = args
    eng = _engine(spec)
    # The plunge cut must sit INSIDE the potential barrier (the Bridge): find the equatorial ridge, the local max of
    # W(x, 0) (the unstable circular orbit for this L), and keep the cut below 0.8 of it. Orbits that dip deep and
    # come back (the sticky behaviour hunted here) must never be misfiled as plunges.
    xs_r = np.geomspace(x_in * 1.0001, 60.0, 4000)
    Wv = np.array([eng.W(xx, 0.0, E, L) for xx in xs_r])
    imax = [i for i in range(1, len(Wv) - 1) if Wv[i] > Wv[i - 1] and Wv[i] >= Wv[i + 1]]
    x_ridge = float(xs_r[imax[0]]) if imax else None
    x_pl = max(x_in, PLUNGE_X if x_ridge is None else min(PLUNGE_X, 0.8 * x_ridge))
    if x_ridge is not None and not (x_pl < x_ridge * 0.95):
        raise RuntimeError(f"plunge cut {x_pl} not safely inside the ridge {x_ridge} at E={E} L={L}")
    P = pockets(eng, E, L, x_in)
    if not P:
        return dict(E=E, L=L, orbits=[], note="no allowed region")
    a, b, ti, tf = max(P, key=lambda r: r[1] - r[0])
    if tf:
        return dict(E=E, L=L, orbits=[], note="allowed region open to infinity")
    lo = max(a, 2.0) if ti else a
    xs = np.geomspace(lo * 1.0005, b * 0.9995, ncoarse)
    coarse = []
    for x0 in xs:
        r = eng.orbit(float(x0), E, L, nsec=nsec, tmax=5e6, xmin=x_pl, xmax=2000.0, tol=1e-11)
        coarse.append((float(x0), None if r is None else r["status"]))
    windows = []
    for (x1, s1), (x2, s2) in zip(coarse, coarse[1:]):
        if s1 is not None and s2 is not None and s1 != s2:
            windows.append((x1, x2))
    out = []
    for x1, x2 in windows:
        for x0 in np.linspace(x1, x2, ndense):
            r = eng.orbit(float(x0), E, L, nsec=nsec, tmax=5e6, xmin=x_pl, xmax=2000.0, tol=1e-11)
            if r is None:
                continue
            cand = (r["fd"] == r["fd"]) and r["fd"] > FD_THR and r["sex"] >= SEX_THR
            rec = dict(x0=float(x0), n=r["n"], status=r["status"], fd=r["fd"], sex=r["sex"], drift=r["drift"],
                       drift_window=r["drift_window"], t_end=r["t_end"], cand=bool(cand))
            if cand:
                r2 = eng.orbit(float(x0), E, L, nsec=nsec, tmax=5e6, xmin=x_pl, xmax=2000.0, tol=1e-13)
                rec.update(fd2=r2["fd"], sex2=r2["sex"], n2=r2["n"], status2=r2["status"], drift_window2=r2["drift_window"],
                           confirmed=bool((r2["fd"] == r2["fd"]) and r2["fd"] > FD_THR and r2["sex"] >= SEX_THR))
            out.append(rec)
    print(f"    level E={E} L={L:.4f}: ridge {x_ridge}, plunge cut {x_pl:.3f}; region [{a:.3f}, {b:.3f}] inner-open={ti}, {len(windows)} windows, "
          f"{len(out)} boundary orbits, {sum(o['cand'] for o in out)} candidates, "
          f"{sum(o['status'] == 3 for o in out)} step-capped", flush=True)
    return dict(E=E, L=L, region=[a, b, ti, tf], n_coarse=len(coarse),
                n_survive=sum(1 for _, s in coarse if s == 0), windows=windows, orbits=out)


def boundary_scan(sysname, Es, Lms, signs=(+1, -1), ncoarse=60, ndense=40, nsec=300, workers=7, tag=""):
    spec, m, x_in = SYSTEMS[sysname]
    t0 = time.time()
    jobs = [(spec, E, s * lm * m, x_in, ncoarse, ndense, nsec) for E in Es for lm in Lms for s in signs]
    with Pool(workers) as pool:
        levels = pool.map(_level_job, jobs, chunksize=1)
    orbits = [dict(o, E=lv["E"], L=lv["L"]) for lv in levels for o in lv["orbits"]]
    ncand = sum(o["cand"] for o in orbits)
    conf = [o for o in orbits if o.get("confirmed")]
    with open(os.path.join(OUT, f"bscan_{sysname}{tag}.json"), "w") as fh:
        json.dump(dict(system=sysname, Es=Es, Lms=list(map(float, Lms)), levels=levels), fh)
    print(f"VERDICT-v2 [{sysname}{tag}] {len(jobs)} levels, {sum(len(lv.get('windows', [])) for lv in levels)} survive/plunge "
          f"windows, {len(orbits)} boundary orbits: candidates {ncand}, CONFIRMED at tol 1e-13 {len(conf)}  "
          f"[{time.time()-t0:.0f}s]", flush=True)
    for o in conf[:12]:
        print(f"  CHAOS E={o['E']} L={o['L']:.4f} x0={o['x0']:.5f}: fd {o['fd']:.4f}/{o['fd2']:.4f} S_ex {o['sex']:.1f}/"
              f"{o['sex2']:.1f} n {o['n']}/{o['n2']} status {o['status']}/{o['status2']}", flush=True)
    return conf
