#!/usr/bin/env python3
"""High-precision probe driver (data/ts_chaos/HP_PREREGISTRATION.md, fdb028d + addendum 1 d556df2).
Phases (each checkpointed per orbit in data/ts_chaos/hp/<phase>.jsonl; a restart skips finished jobs):
  select   200 TS + 25 Kerr L1 x0 (seeded); DP5 at tol 1e-11/1e-12/1e-13 (maxsteps 3e7), N = 300 -> SENSITIVE/STABLE
  gates    G1 Kerr Carter + G2 shell at R2 (N = 300); G3 R1 vs DP5 (20 stable TS + 25 Kerr); G4 R3 mpmath spot checks
  base     R1 and R2 at N = 600 on the probe set (50 sensitive + 50 stable TS + 25 Kerr)
  cross    x0 +- eps at R1 and R2, eps in {1e-8, 1e-11, 1e-14, 1e-17, 1e-20}, on K_cross converged x0 + 10 Kerr
    .venv/bin/python scripts/_hp_probe.py <phase> [workers=2]
"""
import json
import os
import random
import sys
import time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "ts_chaos", "hp")
LEV = {"ts": dict(spec="ts2:4/5", E=sp.Rational(97, 100), L=sp.Rational(41, 8), Ef=0.97, Lf=5.125,
                  W=(9.912067, 9.945202), seed=2026101101, n=200),
       "kerr": dict(spec="ts2kerr:4/5", E=sp.Rational(97, 100), L=sp.Rational(2550268, 1000000), Ef=0.97, Lf=2.550268,
                    W=(4.990213, 4.996584), seed=2026101102, n=25)}
R = {"R1": 1e-22, "R2": 1e-28}
EPS = [1e-8, 1e-11, 1e-14, 1e-17, 1e-20]
XPL = 1.5
_E = {}


def dd_engine(sys_):
    if ("dd", sys_) not in _E:
        import _hp_dd as H
        _E[("dd", sys_)] = H.DDEngine(LEV[sys_]["spec"])
    return _E[("dd", sys_)]


def dp_engine(sys_):
    if ("dp", sys_) not in _E:
        from _ts_chaos_scan import _engine
        _E[("dp", sys_)] = _engine(LEV[sys_]["spec"])
    return _E[("dp", sys_)]


def pool_x0(sys_):
    lv = LEV[sys_]
    rnd = random.Random(lv["seed"])
    return [rnd.uniform(*lv["W"]) for _ in range(lv["n"])]


def outcome(status, n, N):
    """Outcome at horizon N from a run to >= N crossings: survive if n >= N, else the terminal status."""
    if status == 3:
        return "capped"
    if status == -1:
        return "forbidden"
    return "survive" if n >= N else {0: "survive", 1: "plunge", 2: "escape"}[status]


def ck_load(name):
    p = os.path.join(OUT, name + ".jsonl")
    done = {}
    if os.path.exists(p):
        for line in open(p):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done[r["key"]] = r
    return done


def run_jobs(name, jobs, fn, workers):
    os.makedirs(OUT, exist_ok=True)
    done = ck_load(name)
    todo = [j for j in jobs if j["key"] not in done]
    print(f"[{name}] {len(done)} done, {len(todo)} to run", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, open(os.path.join(OUT, name + ".jsonl"), "a") as fh:
        for i, r in enumerate(pool.imap_unordered(fn, todo, chunksize=1)):
            done[r["key"]] = r
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            if (i + 1) % 20 == 0:
                print(f"  [{name}] {i + 1}/{len(todo)}  [{time.time() - t0:.0f}s]", flush=True)
    return done


# ---------------------------------------------------------------------------------------------------- jobs
def job_dp(j):
    lv = LEV[j["sys"]]
    r = dp_engine(j["sys"]).orbit(j["x0"], lv["Ef"], lv["Lf"], nsec=300, tmax=5e6, xmin=XPL, xmax=2000.0, tol=j["tol"],
                                  maxsteps=30_000_000)
    st, n = (-1, 0) if r is None else (r["status"], r["n"])
    return dict(key=j["key"], sys=j["sys"], x0=j["x0"], tol=j["tol"], status=st, n=n)


def job_dd(j):
    lv = LEV[j["sys"]]
    t0 = time.time()
    r = dd_engine(j["sys"]).orbit(j["x0"], lv["E"], lv["L"], tol=R[j["rung"]], nsec=j["N"])
    out = dict(key=j["key"], sys=j["sys"], x0=j["x0"], rung=j["rung"], N=j["N"], status=r["status"], n=r["n"],
               t_end=r["t_end"], steps=r["steps"], maxshell=r["maxshell"], sec=time.time() - t0)
    for k in ("eps", "side", "base"):
        if k in j:
            out[k] = j[k]
    if j.get("carter"):
        import mpmath as mp
        import _hp_dd as H
        mp.mp.dps = 40
        Q = H.carter_Q(dd_engine(j["sys"]).ginv, lv["E"], lv["L"])
        qs = [Q(mp.mpf(s[0]) + s[1], mp.mpf(s[2]) + s[3], mp.mpf(s[4]) + s[5], mp.mpf(s[6]) + s[7]) for s in r["secs"]]
        out["carter_rel_drift"] = float(max(abs(q - qs[0]) for q in qs) / abs(qs[0])) if qs else None
    return out


# ---------------------------------------------------------------------------------------------------- phases
def classify():
    d = ck_load("select")
    res = {}
    for sys_ in ("ts", "kerr"):
        for i, x0 in enumerate(pool_x0(sys_)):
            rs = [d.get(f"{sys_}:{i}:{tol}") for tol in (1e-11, 1e-12, 1e-13)]
            if any(r is None for r in rs):
                continue
            outs = [(outcome(r["status"], r["n"], 300), min(r["n"], 300)) for r in rs]
            res[(sys_, i)] = dict(x0=x0, outs=outs, sensitive=len(set(outs)) > 1,
                                  capped=any(o[0] == "capped" for o in outs))
    return res


def probe_set():
    c = classify()
    ts = [(i, v) for (s, i), v in sorted(c.items()) if s == "ts"]
    sens = [(i, v) for i, v in ts if v["sensitive"]][:50]
    stab = [(i, v) for i, v in ts if not v["sensitive"]][:50]
    kerr = [(i, v) for (s, i), v in sorted(c.items()) if s == "kerr"]
    return sens, stab, kerr


def main():
    phase = sys.argv[1]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    if phase == "select":
        jobs = [dict(key=f"{s}:{i}:{tol}", sys=s, x0=x0, tol=tol) for s in ("ts", "kerr")
                for i, x0 in enumerate(pool_x0(s)) for tol in (1e-11, 1e-12, 1e-13)]
        run_jobs("select", jobs, job_dp, workers)
        c = classify()
        nts = sum(1 for (s, _) in c if s == "ts")
        ns = sum(1 for (s, _), v in c.items() if s == "ts" and v["sensitive"])
        nk = sum(1 for (s, _), v in c.items() if s == "kerr" and v["sensitive"])
        ncap = sum(1 for v in c.values() if v["capped"])
        print(f"VERDICT-select: TS {nts} classified, SENSITIVE {ns} ({ns / max(nts, 1):.0%}), STABLE {nts - ns}; "
              f"Kerr sensitive {nk}/25; any DP5 step-capped: {ncap}", flush=True)
    elif phase == "gates":
        sens, stab, kerr = probe_set()
        jobs = []
        for i, v in kerr[:5]:
            jobs.append(dict(key=f"G1:kerr:{i}", sys="kerr", x0=v["x0"], rung="R2", N=300, carter=True))
        for i, v in stab[:5]:
            jobs.append(dict(key=f"G2:ts:{i}", sys="ts", x0=v["x0"], rung="R2", N=300))
        for i, v in stab[:20]:
            jobs.append(dict(key=f"G3:ts:{i}", sys="ts", x0=v["x0"], rung="R1", N=300))
        for i, v in kerr:
            jobs.append(dict(key=f"G3:kerr:{i}", sys="kerr", x0=v["x0"], rung="R1", N=300))
        d = run_jobs("gates", jobs, job_dd, workers)
        g1 = [d[f"G1:kerr:{i}"] for i, _ in kerr[:5]]
        g1ok = all(r["carter_rel_drift"] is not None and r["carter_rel_drift"] <= 1e-24 for r in g1)
        g2 = g1 + [d[f"G2:ts:{i}"] for i, _ in stab[:5]]
        g2ok = all(r["maxshell"] <= 1e-24 for r in g2)
        agree_ts = [outcome(d[f"G3:ts:{i}"]["status"], d[f"G3:ts:{i}"]["n"], 300) == v["outs"][0][0]
                    and min(d[f"G3:ts:{i}"]["n"], 300) == v["outs"][0][1] for i, v in stab[:20]]
        agree_k = [outcome(d[f"G3:kerr:{i}"]["status"], d[f"G3:kerr:{i}"]["n"], 300) == v["outs"][0][0]
                   and min(d[f"G3:kerr:{i}"]["n"], 300) == v["outs"][0][1] for i, v in kerr]
        g3ok = sum(agree_ts) >= 0.9 * len(agree_ts) and all(agree_k)
        print(f"G1 Kerr Carter drift (R2, N=300): {[f'{r['carter_rel_drift']:.1e}' for r in g1]} -> {'PASS' if g1ok else 'FAIL'}")
        print(f"G2 shell max|2H+1| (R2): {[f'{r['maxshell']:.1e}' for r in g2]} -> {'PASS' if g2ok else 'FAIL'}")
        print(f"G3 R1 vs DP5 (outcome, n at N=300): TS stable {sum(agree_ts)}/{len(agree_ts)}, Kerr {sum(agree_k)}/{len(agree_k)}"
              f" -> {'PASS' if g3ok else 'FAIL'}")
        for (i, v), a in zip(stab[:20], agree_ts):
            if not a:
                r = d[f"G3:ts:{i}"]
                print(f"   G3 disagreement ts:{i} x0={v['x0']:.9f}: DP5 {v['outs'][0]} vs R1 {(outcome(r['status'], r['n'], 300), min(r['n'], 300))}")
        print(f"VERDICT-gates G1-G3: {'ALL PASS' if g1ok and g2ok and g3ok else 'FAILED'}", flush=True)
    elif phase == "base":
        sens, stab, kerr = probe_set()
        sets = [("S", "ts", sens), ("T", "ts", stab), ("K", "kerr", kerr)]
        jobs = [dict(key=f"{tag}:{s}:{i}:{rung}", sys=s, x0=v["x0"], rung=rung, N=600)
                for tag, s, lst in sets for i, v in lst for rung in ("R1", "R2")]
        d = run_jobs("base", jobs, job_dd, workers)
        for tag, s, lst in sets:
            for N in (300, 600):
                conv = 0
                for i, v in lst:
                    a, b = d[f"{tag}:{s}:{i}:R1"], d[f"{tag}:{s}:{i}:R2"]
                    oa = (outcome(a["status"], a["n"], N), min(a["n"], N))
                    ob = (outcome(b["status"], b["n"], N), min(b["n"], N))
                    conv += oa == ob and oa[0] != "capped"
                print(f"VERDICT-base [{ {'S': 'TS sensitive', 'T': 'TS stable', 'K': 'Kerr'}[tag] }] N={N}: converged "
                      f"{conv}/{len(lst)} (U = {1 - conv / max(len(lst), 1):.2f})", flush=True)
    else:
        raise SystemExit(f"unknown phase {phase} (cross is a separate step, after gates and base are read)")


if __name__ == "__main__":
    main()
