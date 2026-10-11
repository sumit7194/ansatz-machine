#!/usr/bin/env python3
"""Crossover phase of the high-precision probe (HP_PREREGISTRATION.md section (2) + addendum 1). Run only after
`gates` passed and `base` was read.
- Converged set: probe x0 whose base outcome converged (R1 = R2 in (outcome, n)) at BOTH N = 300 and N = 600.
- K_cross by the pre-registered sizing rule: 12 h on 2 workers at the measured mean R1 + R2 cost per 600-crossing orbit
  (10 orbits per x0 per rung), capped at 40, taken in seeded order alternating SENSITIVE / STABLE; < 12 -> INSUFFICIENT
  BUDGET. Kerr: the first 10 converged Kerr x0.
- Neighbours x0 +- eps, eps in {1e-8, 1e-11, 1e-14, 1e-17, 1e-20}, at R1 and R2, N = 600 (N = 300 comes free).
- Uncertain at eps: a converged neighbour whose outcome CLASS differs from the converged base. PRIMARY: x0 with an
  unresolved neighbour are excluded at that eps. SECONDARY bound: unresolved neighbours counted as uncertain.
- An eps rung enters eps_c only if >= 80% of its neighbour outcomes converged. eps_c(N) = the largest eps at which the
  pairwise slope to the next smaller eps first exceeds 0.5 (f falling toward s = 1). Never: "below reach" (< 1e-20).
- Kerr control: 0 uncertain at every eps, or (2) is void.
    .venv/bin/python scripts/_hp_cross.py run [workers=2]      # integrations (checkpointed)
    .venv/bin/python scripts/_hp_cross.py analyse
"""
import json
import math
import os
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _hp_probe as P  # noqa: E402

EPS = P.EPS


def base_table():
    sens, stab, kerr = P.probe_set()
    d = P.ck_load("base")
    rows = []
    for tag, s, lst in (("S", "ts", sens), ("T", "ts", stab), ("K", "kerr", kerr)):
        for i, v in lst:
            a, b = d[f"{tag}:{s}:{i}:R1"], d[f"{tag}:{s}:{i}:R2"]
            conv = {}
            for N in (300, 600):
                oa = (P.outcome(a["status"], a["n"], N), min(a["n"], N))
                ob = (P.outcome(b["status"], b["n"], N), min(b["n"], N))
                conv[N] = oa[0] if (oa == ob and oa[0] != "capped") else None
            rows.append(dict(tag=tag, sys=s, i=i, x0=v["x0"], out300=conv[300], out600=conv[600],
                             sec=a["sec"] + b["sec"]))
    return rows


def crossover_set():
    rows = base_table()
    ts = [r for r in rows if r["sys"] == "ts"]
    mean_cost = sum(r["sec"] for r in ts) / len(ts)               # R1 + R2 per 600-crossing orbit
    per_x0 = 10 * mean_cost
    K = min(40, int(12 * 3600 * 2 / per_x0))
    conv = lambda r: r["out300"] is not None and r["out600"] is not None
    S = [r for r in rows if r["tag"] == "S" and conv(r)]
    T = [r for r in rows if r["tag"] == "T" and conv(r)]
    alt = [r for pair in zip(S, T) for r in pair] + S[len(T):] + T[len(S):]
    chosen = alt[:K]
    kerr = [r for r in rows if r["tag"] == "K" and conv(r)][:10]
    return chosen, kerr, dict(mean_cost=mean_cost, K=K, nS=len(S), nT=len(T))


def main():
    mode = sys.argv[1]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    chosen, kerr, info = crossover_set()
    print(f"[cross] mean R1+R2 cost per 600-crossing TS orbit {info['mean_cost']:.1f}s -> K_cross = {info['K']} "
          f"(converged at both N: sensitive {info['nS']}, stable {info['nT']}); Kerr {len(kerr)}", flush=True)
    if info["K"] < 12:
        print("VERDICT-cross: INSUFFICIENT BUDGET (K_cross < 12), per the pre-registration", flush=True)
        return
    if mode == "run":
        jobs = [dict(key=f"{r['tag']}:{r['sys']}:{r['i']}:{e:.0e}:{side}:{rung}", sys=r["sys"], x0=r["x0"] + sgn * e,
                     rung=rung, N=600, eps=e, side=side, base=f"{r['tag']}:{r['i']}")
                for r in chosen + kerr for e in EPS for side, sgn in (("m", -1), ("p", 1)) for rung in ("R1", "R2")]
        P.run_jobs("cross", jobs, P.job_dd, workers)
        print("[cross] integrations done", flush=True)
        return
    d = P.ck_load("cross")
    res = {}
    for group, lst in (("TS", chosen), ("Kerr", kerr)):
        for N in (300, 600):
            f_pri, f_sec, cov = [], [], []
            for e in EPS:
                unc = tot = unc2 = tot2 = nconv = nnb = 0
                for r in lst:
                    base = r["out300"] if N == 300 else r["out600"]
                    nb = []
                    for side in ("m", "p"):
                        a = d.get(f"{r['tag']}:{r['sys']}:{r['i']}:{e:.0e}:{side}:R1")
                        b = d.get(f"{r['tag']}:{r['sys']}:{r['i']}:{e:.0e}:{side}:R2")
                        if a is None or b is None:
                            nb.append("missing")
                            continue
                        oa = (P.outcome(a["status"], a["n"], N), min(a["n"], N))
                        ob = (P.outcome(b["status"], b["n"], N), min(b["n"], N))
                        nb.append(oa[0] if (oa == ob and oa[0] != "capped") else None)
                    nnb += 2
                    nconv += sum(1 for o in nb if o not in (None, "missing"))
                    tot2 += 1
                    unc2 += any(o is None or (o != "missing" and o != base) for o in nb)
                    if all(o not in (None, "missing") for o in nb):
                        tot += 1
                        unc += any(o != base for o in nb)
                f_pri.append((unc, tot)); f_sec.append((unc2, tot2)); cov.append(nconv / max(nnb, 1))

            def eps_c(fs):
                fr = [u / t if t else float("nan") for u, t in fs]
                for i in range(len(EPS) - 1):
                    if cov[i] < 0.8 or cov[i + 1] < 0.8:
                        return f"rung below DD resolution at eps={EPS[i + 1]:.0e} (eps_c stated as inequality)"
                    a, b = fr[i], fr[i + 1]
                    if a > 0 and b == 0:
                        return EPS[i]
                    if a > 0 and b > 0 and math.log(a / b) / math.log(EPS[i] / EPS[i + 1]) > 0.5:
                        return EPS[i]
                return "below reach (< 1e-20)"
            res[(group, N)] = dict(primary=f_pri, secondary=f_sec, coverage=cov,
                                   eps_c_primary=eps_c(f_pri), eps_c_secondary=eps_c(f_sec))
            print(f"  {group:4s} N={N}: f PRIMARY " + "  ".join(f"{e:.0e}:{u}/{t}" for e, (u, t) in zip(EPS, f_pri))
                  + f" | coverage " + " ".join(f"{c:.2f}" for c in cov), flush=True)
            print(f"       SECONDARY " + "  ".join(f"{e:.0e}:{u}/{t}" for e, (u, t) in zip(EPS, f_sec))
                  + f" | eps_c primary {res[(group, N)]['eps_c_primary']}, secondary {res[(group, N)]['eps_c_secondary']}",
                  flush=True)
    kerr_unc = sum(u for N in (300, 600) for u, _ in res[("Kerr", N)]["primary"])
    c300, c600 = res[("TS", 300)]["eps_c_primary"], res[("TS", 600)]["eps_c_primary"]
    robust = all(res[("TS", N)]["eps_c_primary"] == res[("TS", N)]["eps_c_secondary"] for N in (300, 600))
    if kerr_unc:
        verdict = f"VOID: Kerr control shows {kerr_unc} uncertain"
    elif isinstance(c300, float) and isinstance(c600, float):
        verdict = ("SUPPORTS GENUINE FRACTAL (eps_c(600) < eps_c(300))" if c600 < c300 else
                   "SUPPORTS FINITE-TIME ARTEFACT (eps_c(600) >= eps_c(300))")
    elif isinstance(c300, float) and c600 == "below reach (< 1e-20)":
        verdict = "SUPPORTS GENUINE FRACTAL (eps_c(300) inside reach, eps_c(600) below reach)"
    elif c300 == "below reach (< 1e-20)" and c600 == "below reach (< 1e-20)":
        verdict = "NOT DECIDABLE AT DD: flat to 1e-20 at both horizons"
    else:
        verdict = f"INCONCLUSIVE (eps_c(300) = {c300}, eps_c(600) = {c600})"
    print(f"VERDICT-cross: {verdict}; Kerr uncertain {kerr_unc}; primary/secondary {'agree' if robust else 'NOT ROBUST'}",
          flush=True)
    json.dump({f"{g}|{N}": v for (g, N), v in res.items()}, open(os.path.join(P.OUT, "cross_analysis.json"), "w"),
              indent=1, default=str)


if __name__ == "__main__":
    main()
