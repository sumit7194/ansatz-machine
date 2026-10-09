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
}
FD_THR, SEX_THR = 0.0115, 10.0
_ENG = None


def _engine(spec):
    global _ENG
    if _ENG is None:
        from _kt_exact_op import get_metric
        from _ts_chaos import Engine
        gi, name = get_metric(spec)
        _ENG = Engine(gi, name)
    return _ENG


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
