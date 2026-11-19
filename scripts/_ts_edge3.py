#!/usr/bin/env python3
"""Edge-link v3 (data/ts_chaos/EDGE_LINK3_PREREGISTRATION.md): fate bisection + ownership slope, TIMING class.
    .venv/bin/python scripts/_ts_edge3.py step1      # Kerr precision check (P-log, K-sep-F, K-timing, MFs)
    .venv/bin/python scripts/_ts_edge3.py window     # TS window (only after step 1 PASS)
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpmath as mp  # noqa: E402
import numpy as np  # noqa: E402

import _ts_edge as E  # noqa: E402
import _ts_edge2 as V  # noqa: E402

mp.mp.dps = 40
OUT = os.path.join(E.ROOT, "data", "ts_chaos", "edge3")


def FN(M, F, x, N):
    h = V.history(M, F, x, cap=N)
    return bool(h["fate"]), h


def bisect_F(M, M1, F, xa, xb, N):
    a, b = mp.mpf(xa), mp.mpf(xb)
    fa, ha = FN(M, F, a, N)
    fb, hb = FN(M, F, b, N)
    if fa == fb:
        return dict(ok=False, why="F equal at ends")
    if not fa:
        a, b, ha, hb = b, a, hb, ha                  # a: F true (plunges within N)
    ga, gb = ha["gmin"], hb["gmin"]
    stages = []
    for hh in range(1, 71):
        m = (a + b) / 2
        fm, hm = FN(M, F, m, N)
        if fm:
            a, ga = m, hm["gmin"]
        else:
            b, gb = m, hm["gmin"]
        w = abs(b - a)
        stages.append(dict(w=float(w), rho=float(max(ga, gb))))
        if w / abs(a) <= mp.mpf("1e-18"):
            break
    sl, dec = V.fit(stages, a)
    p6, q6 = V.history(M, F, a, cap=600), V.history(M, F, b, cap=600)
    p6r1, q6r1 = V.history(M1, F, a, cap=600), V.history(M1, F, b, cap=600)
    f1a, f1b = FN(M1, F, a, N)[0], FN(M1, F, b, N)[0]
    timing = bool(p6["fate"] and q6["fate"] and abs(p6["n"] - q6["n"]) <= 2)
    scls = V.classify_slope(sl, dec)
    r1_F = (f1a, f1b) == (True, False)
    r1_600 = (p6r1["fate"], q6r1["fate"]) == (p6["fate"], q6["fate"])
    gfin = float(max(ga, gb))
    if timing:
        cls = "TIMING"
    elif scls == "strand" and r1_F:
        cls = "STRAND"
    elif sl is not None and dec >= 6 and sl < 0.2 and gfin >= 0.1 and r1_F and r1_600:
        cls = "FALSIFIER"
    else:
        cls = "OTHER"
    return dict(ok=True, cls=cls, slope=sl, decades=dec, slope_cls=scls, a=mp.nstr(a, 30), b=mp.nstr(b, 30),
                mid=(a + b) / 2, life600=dict(p=(p6["fate"], p6["n"]), q=(q6["fate"], q6["n"]),
                                             p_R1=(p6r1["fate"], p6r1["n"]), q_R1=(q6r1["fate"], q6r1["n"])),
                r1_F=r1_F, r1_600=r1_600, gmin_final=gfin, stages=stages)


def step1():
    t0 = time.time()
    out = {}
    V.checkpoint(os.path.join(OUT, "step1_histories.jsonl"))
    kc = E.kerr_closed_form()
    M, M1, F, zs = E.setup("kerr")
    _, lu, _, _, _, _ = E.fixed_and_frame(M, "kerr")
    ds = [mp.mpf(10) ** (-mp.mpf(k) / 2) for k in range(4, 33)]
    ns = [V.history(M, F, kc["x_h"] + d, cap=600) for d in ds]
    pts = [(float(-mp.log10(d)), h["n"]) for d, h in zip(ds, ns) if h["fate"]]
    sl = float(np.polyfit([p[0] for p in pts], [p[1] for p in pts], 1)[0]) if len(pts) >= 5 else None
    target = float(1 / mp.log10(lu))
    out["P-log"] = dict(slope=sl, target=target, n=[h["n"] for h in ns], fates=[h["fate"] for h in ns],
                        pass_=bool(sl is not None and abs(sl / target - 1) <= 0.05))
    print("P-log", {k: out["P-log"][k] for k in ("slope", "target", "pass_")}, f"[{time.time() - t0:.0f}s]", flush=True)
    r = bisect_F(M, M1, F, kc["x_h"] - mp.mpf("1e-6"), kc["x_h"] + mp.mpf("1e-6"), 300)
    if r["ok"]:
        r["conv"] = float(abs(r["mid"] - kc["x_h"]))
        r["pass_"] = r["conv"] <= 1e-16 and r["cls"] == "STRAND"
    else:
        r["pass_"] = False
    r.pop("mid", None)
    out["K-sep-F"] = r
    print("K-sep-F", {k: r.get(k) for k in ("ok", "why", "cls", "slope", "decades", "conv", "life600", "pass_")},
          f"[{time.time() - t0:.0f}s]", flush=True)
    step_ = next((i for i in range(len(ns) - 1) if ns[i]["fate"] and ns[i + 1]["fate"]
                  and ns[i]["n"] != ns[i + 1]["n"]), None)
    if step_ is None:
        out["K-timing"] = dict(pass_=False, why="no lifetime step found")
    else:
        N = min(ns[step_]["n"], ns[step_ + 1]["n"]) + 1          # addendum 1: F_N true iff n <= N - 1
        r = bisect_F(M, M1, F, kc["x_h"] + ds[step_], kc["x_h"] + ds[step_ + 1], N)
        r.pop("mid", None)
        r["N"] = N
        r["pass_"] = r.get("cls") == "TIMING"
        out["K-timing"] = r
    print("K-timing", {k: out["K-timing"].get(k) for k in ("ok", "why", "cls", "slope", "life600", "N", "pass_")},
          f"[{time.time() - t0:.0f}s]", flush=True)
    c2 = json.load(open(os.path.join(V.OUT, "controls.json")))
    for mf in ("MF-1", "MF-2"):
        out[mf] = dict(slope=c2[mf]["slope"], slope_cls=c2[mf]["cls"], pass_=c2[mf]["cls"] != "strand")
        print(mf, out[mf], flush=True)
    out["all_pass"] = all(v["pass_"] for v in out.values() if isinstance(v, dict))
    out["sec"] = time.time() - t0
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == "step1":
        o = step1()
        json.dump(o, open(os.path.join(OUT, "step1.json"), "w"), indent=1, default=str)
        print("VERDICT-step1:", "PASS" if o["all_pass"] else "FAIL (STOP)", flush=True)
