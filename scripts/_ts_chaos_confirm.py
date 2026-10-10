#!/usr/bin/env python3
"""Amendment-5 re-confirmation of v2 candidates: tol 1e-13, step cap 30M; confirmed only if status != 3, n >= 100,
fd > 0.0115 and S_ex >= 10. Step-capped re-runs are INCONCLUSIVE.
    .venv/bin/python scripts/_ts_chaos_confirm.py data/ts_chaos/bscan_<system>_v2.json"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ts_chaos_scan import FD_THR, SEX_THR, PLUNGE_X, SYSTEMS, _engine  # noqa: E402


def main():
    path = sys.argv[1]
    d = json.load(open(path))
    spec, m, x_in = SYSTEMS[d["system"]]
    eng = _engine(spec)
    out = []
    for lv in d["levels"]:
        for o in lv["orbits"]:
            if not o["cand"]:
                continue
            r = eng.orbit(o["x0"], lv["E"], lv["L"], nsec=300, tmax=5e6, xmin=max(x_in, PLUNGE_X), xmax=2000.0,
                          tol=1e-13, maxsteps=30_000_000)
            capped = r["status"] == 3
            ok = (not capped) and r["n"] >= 100 and r["fd"] == r["fd"] and r["fd"] > FD_THR and r["sex"] >= SEX_THR
            verdict = "INCONCLUSIVE (step-capped)" if capped else ("CONFIRMED" if ok else "rejected")
            out.append(dict(E=lv["E"], L=lv["L"], x0=o["x0"], fd1=o["fd"], sex1=o["sex"], n1=o["n"], st1=o["status"],
                            fd13=r["fd"], sex13=r["sex"], n13=r["n"], st13=r["status"], drift13=r["drift_window"],
                            verdict=verdict))
            print(f"  E={lv['E']} L={lv['L']:.4f} x0={o['x0']:.5f}: 1e-11 fd {o['fd']:.4f} S_ex {o['sex']:.1f} n {o['n']} | "
                  f"1e-13 fd {r['fd']:.4f} S_ex {r['sex']:.1f} n {r['n']} st {r['status']} -> {verdict}", flush=True)
    nconf = sum(x["verdict"] == "CONFIRMED" for x in out)
    ninc = sum(x["verdict"].startswith("INCONCLUSIVE") for x in out)
    json.dump(out, open(path.replace(".json", "_confirm.json"), "w"), indent=1)
    print(f"VERDICT-A5 [{d['system']}] candidates {len(out)}: CONFIRMED {nconf}, INCONCLUSIVE {ninc}, rejected {len(out)-nconf-ninc}")


if __name__ == "__main__":
    main()
