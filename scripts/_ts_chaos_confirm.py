#!/usr/bin/env python3
"""Amendment-5 re-confirmation of v2 candidates: tol 1e-13, step cap 30M; confirmed only if status != 3, n >= 100,
fd > 0.0115 and S_ex >= 10. Step-capped re-runs are INCONCLUSIVE.
    .venv/bin/python scripts/_ts_chaos_confirm.py data/ts_chaos/bscan_<system>_v2.json"""
import json
import os
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ts_chaos_scan import FD_THR, SEX_THR, PLUNGE_X, SYSTEMS, _engine  # noqa: E402


def _job(a):
    sysname, E, L, x0, fd1, sex1, n1, st1 = a
    spec, m, x_in = SYSTEMS[sysname]
    eng = _engine(spec)
    r = eng.orbit(x0, E, L, nsec=300, tmax=5e6, xmin=max(x_in, PLUNGE_X), xmax=2000.0, tol=1e-13, maxsteps=30_000_000)
    capped = r["status"] == 3
    ok = (not capped) and r["n"] >= 100 and r["fd"] == r["fd"] and r["fd"] > FD_THR and r["sex"] >= SEX_THR
    verdict = "INCONCLUSIVE (step-capped)" if capped else ("CONFIRMED" if ok else "rejected")
    return dict(E=E, L=L, x0=x0, fd1=fd1, sex1=sex1, n1=n1, st1=st1, fd13=r["fd"], sex13=r["sex"], n13=r["n"],
                st13=r["status"], drift13=r["drift_window"], verdict=verdict)


def main():
    path = sys.argv[1]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    d = json.load(open(path))
    jobs = [(d["system"], lv["E"], lv["L"], o["x0"], o["fd"], o["sex"], o["n"], o["status"])
            for lv in d["levels"] for o in lv["orbits"] if o["cand"]]
    with Pool(workers) as pool:
        out = pool.map(_job, jobs, chunksize=1)
    for x in out:
        print(f"  E={x['E']} L={x['L']:.4f} x0={x['x0']:.5f}: 1e-11 fd {x['fd1']:.4f} S_ex {x['sex1']:.1f} n {x['n1']} | "
              f"1e-13 fd {x['fd13']:.4f} S_ex {x['sex13']:.1f} n {x['n13']} st {x['st13']} -> {x['verdict']}", flush=True)
    nconf = sum(x["verdict"] == "CONFIRMED" for x in out)
    ninc = sum(x["verdict"].startswith("INCONCLUSIVE") for x in out)
    json.dump(out, open(path.replace(".json", "_confirm.json"), "w"), indent=1)
    print(f"VERDICT-A5 [{d['system']}] candidates {len(out)}: CONFIRMED {nconf}, INCONCLUSIVE {ninc}, rejected {len(out)-nconf-ninc}",
          flush=True)


if __name__ == "__main__":
    main()
