#!/usr/bin/env python3
"""Edge-link v2 (data/ts_chaos/EDGE_LINK2_PREREGISTRATION.md): exit-sign bisection and the ownership slope.
Built on _ts_edge.py (EdgeMap, Frame, fixed point/frame, v1 fate) and _ts_tangle.py, unchanged.
    .venv/bin/python scripts/_ts_edge2.py controls     # K-sep, K-star, MF-1, MF-2, T-sep
    .venv/bin/python scripts/_ts_edge2.py window       # TS window test (only after controls PASS)
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

mp.mp.dps = 40
OUT = os.path.join(E.ROOT, "data", "ts_chaos", "edge2")
EPS, K, CAP = mp.mpf("1e-2"), 6, 300


def history(M, F, x, eps=EPS, stop_after=None, cap=CAP):
    """-> dict(sig, rmin (per visit), fate, n, end, gmin (min rho over crossings >= 1))."""
    z = [mp.mpf(x), mp.mpf(0)]
    sig, rmins = [], []
    r0 = F.rho(z)
    inv, cur = (r0 <= eps), (r0 if r0 <= eps else None)
    recording = True
    gmin = mp.inf
    n = 0
    end = 0
    for _ in range(cap):
        st, zn, _mx = M.step(z)
        if st != 0:
            end = st
            if inv and recording:
                sig.append(-1); rmins.append(cur)
            break
        n += 1
        r = F.rho(zn)
        gmin = min(gmin, r)
        if recording:
            if inv:
                if r <= eps:
                    cur = min(cur, r)
                else:
                    s_ = 1 if F.us(zn)[0] > 0 else -1
                    sig.append(s_); rmins.append(cur); inv = False
                    if s_ == -1 or len(sig) >= K:
                        recording = False
                    if stop_after is not None and len(sig) >= stop_after:
                        return dict(sig=sig, rmin=rmins, fate=None, n=n, end=None, gmin=gmin)
            elif r <= eps:
                inv, cur = True, r
        z = zn
    return dict(sig=sig, rmin=rmins, fate=(end == 1), n=n, end=end, gmin=gmin)


def fit(stages, x):
    pts = [(math.log10(s["w"]), math.log10(s["rho"])) for s in stages
           if s["rho"] and s["rho"] > 0 and 1e-15 <= s["w"] / abs(x) <= 1e-5]
    if len(pts) < 3:
        return None, 0.0
    X = np.array([p[0] for p in pts]); Y = np.array([p[1] for p in pts])
    return float(np.polyfit(X, Y, 1)[0]), float(X.max() - X.min())


def classify_slope(sl, dec):
    if sl is None or dec < 6:
        return "insufficient"
    if 0.4 <= sl <= 0.6:
        return "strand"
    if 0.85 <= sl <= 1.15:
        return "at_gamma"
    if sl < 0.2:
        return "not_owned"
    return "other"


def bisect_sigma(M, M1, F, xa, xb, eps=EPS):
    """xa, xb on l whose histories first differ by a sigma flip. Bisection on sigma_v."""
    Ha, Hb = history(M, F, xa, eps), history(M, F, xb, eps)
    v = None
    for i in range(min(len(Ha["sig"]), len(Hb["sig"]))):
        if Ha["sig"][i] != Hb["sig"][i]:
            v = i + 1
            break
    if v is None:
        return dict(ok=False, why="no sigma flip", Ha=Ha["sig"], Hb=Hb["sig"])
    pre = Ha["sig"][:v - 1]
    a, b, ra, rb = mp.mpf(xa), mp.mpf(xb), Ha["rmin"][v - 1], Hb["rmin"][v - 1]
    sa = Ha["sig"][v - 1]
    stages, r1 = [], []
    for h in range(1, 71):
        m = (a + b) / 2
        Hm = history(M, F, m, eps, stop_after=v)
        if len(Hm["sig"]) < v or Hm["sig"][:v - 1] != pre:
            return dict(ok=False, why="broken", v=v, halvings=h, stages=stages)
        if Hm["sig"][v - 1] == sa:
            a, ra = m, Hm["rmin"][v - 1]
        else:
            b, rb = m, Hm["rmin"][v - 1]
        w = abs(b - a)
        stages.append(dict(w=float(w), rho=float(max(ra, rb))))
        if h % 10 == 0 or w / abs(a) <= mp.mpf("1e-18"):
            s1a = history(M1, F, a, eps, stop_after=v)["sig"]
            s1b = history(M1, F, b, eps, stop_after=v)["sig"]
            r1.append(len(s1a) >= v and len(s1b) >= v and s1a[v - 1] == sa and s1b[v - 1] == -sa)
        if w / abs(a) <= mp.mpf("1e-18"):
            break
    sl, dec = fit(stages, a)
    # epsilon independence: first differing sigma at eps 3e-3 must equal (sa, -sa)
    ha, hb = history(M, F, a, mp.mpf("3e-3")), history(M, F, b, mp.mpf("3e-3"))
    first = next(((p, q) for p, q in zip(ha["sig"], hb["sig"]) if p != q), None)
    eps_ok = first == (sa, -sa)
    return dict(ok=True, v=v, a=mp.nstr(a, 30), b=mp.nstr(b, 30), mid=(a + b) / 2, slope=sl, decades=dec,
                cls=classify_slope(sl, dec), r1_agree=all(r1) and bool(r1), eps_ok=eps_ok, stages=stages,
                certified=(classify_slope(sl, dec) == "strand" and all(r1) and bool(r1) and eps_ok))


def bisect_pred(M, F, pred, xa, xb, stop_rel=1e-15, nmax=120, Mlist=None):
    """Bisection on an arbitrary predicate; rho_min = larger of the two members' minimum rho over their orbits."""
    a, b = mp.mpf(xa), mp.mpf(xb)
    pa = pred(a)
    if pred(b) == pa:
        return dict(ok=False, why="predicate equal at ends")

    def gmin(x):
        return history(M, F, x, cap=nmax)["gmin"]
    stages = []
    ga, gb = gmin(a), gmin(b)
    for h in range(1, 71):
        m = (a + b) / 2
        if pred(m) == pa:
            a, ga = m, gmin(m)
        else:
            b, gb = m, gmin(m)
        w = abs(b - a)
        stages.append(dict(w=float(w), rho=float(max(ga, gb))))
        if w / abs(a) <= stop_rel:
            break
    sl, dec = fit(stages, a)
    return dict(ok=True, a=mp.nstr(a, 30), b=mp.nstr(b, 30), slope=sl, decades=dec, cls=classify_slope(sl, dec),
                gmin_final=float(max(ga, gb)), stages=stages)


def controls():
    out = {}
    t0 = time.time()
    kc = E.kerr_closed_form()
    M, M1, F, zs = E.setup("kerr")
    for name, x0, tgt in (("K-sep", kc["x_h"], kc["x_h"]), ("K-star", kc["x_star"], kc["x_star"])):
        r = bisect_sigma(M, M1, F, x0 - mp.mpf("1e-6"), x0 + mp.mpf("1e-6"))
        if r["ok"]:
            r["conv"] = float(abs(r["mid"] - tgt))
            need = "strand" if name == "K-sep" else "at_gamma"
            r["pass_"] = r["conv"] <= 1e-16 and r["cls"] == need and r["r1_agree"]
        else:
            r["pass_"] = False
        r.pop("mid", None)
        out[name] = r
        print(name, {k: r.get(k) for k in ("ok", "why", "v", "slope", "decades", "cls", "conv", "r1_agree", "eps_ok", "pass_")},
              f"[{time.time() - t0:.0f}s, {M.calls + M1.calls} calls]", flush=True)
    # MF-2: Kerr section-cut boundary
    xc = (zs[0] + kc["x_stable"]) / 2
    Mc = E.EdgeMap("kerr", "R2"); Mc.xc = xc
    ko = json.load(open(os.path.join(E.OUT, "tswitch_controls.json")))["K-O"]["result"]
    mid = (mp.mpf(ko["a"]) + mp.mpf(ko["b"])) / 2
    pa_, pb_ = mid - mp.mpf("1e-6"), mid + mp.mpf("1e-6")
    hA, hB = history(M, F, pa_, cap=120), history(M, F, pb_, cap=120)
    same = hA["sig"] == hB["sig"]
    r = bisect_pred(M, F, lambda x: E.life(Mc, x, 120)[0] == 1, pa_, pb_)
    r.update(identical_histories=same, pass_=bool(same and r.get("cls") == "not_owned"))
    out["MF-2"] = r
    print("MF-2", {k: r.get(k) for k in ("ok", "why", "identical_histories", "slope", "decades", "cls", "pass_")},
          f"[{time.time() - t0:.0f}s]", flush=True)
    # TS controls (to file; printed as pass/fail only)
    Mt, Mt1, Ft, zst = E.setup("ts")
    bt = json.load(open(os.path.join(E.OUT, "tbands_ts.json")))
    e = [e_ for e_ in bt["edges"] if e_["j"] == 244][0]
    lu_ = mp.mpf(json.load(open(os.path.join(E.TANG, "ts_R2_d1e-12.json")))["lam"])
    _, lu_, _, _, _, _ = E.fixed_and_frame(Mt, "ts")                      # addendum 1: grid neighbours d_244, d_245
    pb_, pa_ = (zst[0] + mp.mpf("0.14") * lu_ ** (-mp.mpf(j) / 96) for j in (244, 245))
    hA, hB = history(Mt, Ft, pa_, cap=120), history(Mt, Ft, pb_, cap=120)
    same = hA["sig"] == hB["sig"]
    fa = E.fate(Mt, [pa_, mp.mpf(0)], E.XFAR["ts"])
    r = bisect_pred(Mt, Ft, lambda x: E.fate(Mt, [x, mp.mpf(0)], E.XFAR["ts"]) == fa, pa_, pb_)
    r.update(identical_histories=same, pass_=bool(same and r.get("cls") == "not_owned"))
    out["MF-1"] = r
    print("MF-1", "PASS" if r["pass_"] else "FAIL", f"[{time.time() - t0:.0f}s]", flush=True)
    _, _, xh_ts, _ = E.stored("ts")
    r = bisect_sigma(Mt, Mt1, Ft, xh_ts - mp.mpf("1e-6"), xh_ts + mp.mpf("1e-6"))
    if r["ok"]:
        r["conv"] = float(abs(r["mid"] - xh_ts))
        r["pass_"] = r["conv"] <= 1e-14 and r["cls"] == "strand" and r["r1_agree"]
    else:
        r["pass_"] = False
    r.pop("mid", None)
    out["T-sep"] = r
    print("T-sep", "PASS" if r["pass_"] else "FAIL", f"[{time.time() - t0:.0f}s, TS calls {Mt.calls + Mt1.calls}]", flush=True)
    out["all_pass"] = all(v["pass_"] for v in out.values() if isinstance(v, dict))
    out["sec"] = time.time() - t0
    return out


def window():
    t0 = time.time()
    M, M1, F, zs = E.setup("ts")
    a0, b0 = mp.mpf("9.912067"), mp.mpf("9.945202")
    xs = [a0 + (b0 - a0) * i / 399 for i in range(400)]
    H = [history(M, F, x) for x in xs]
    t_hist = time.time() - t0
    with_visit = sum(1 for h in H if h["sig"])
    plunging = [h for h in H if h["fate"]]
    covered = sum(1 for h in plunging if h["sig"] and h["sig"][-1] == -1)
    coverage = covered / len(plunging) if plunging else None
    guards = dict(with_visit=with_visit, plunging=len(plunging), coverage=coverage,
                  pass_=with_visit >= 30 and coverage is not None and coverage >= 0.9)
    strands, fals, cand_s, cand_f = [], [], [], []
    for i in range(399):
        ha, hb = H[i]["sig"], H[i + 1]["sig"]
        first = next((k for k in range(min(len(ha), len(hb))) if ha[k] != hb[k]), None)
        if first is not None:
            cand_s.append(i)
        complete = all((h["sig"] and h["sig"][-1] == -1) or len(h["sig"]) < K for h in (H[i], H[i + 1]))
        if H[i]["fate"] != H[i + 1]["fate"] and ha == hb and complete:
            cand_f.append(i)
    if guards["pass_"]:
        for i in cand_s[:20]:
            r = bisect_sigma(M, M1, F, xs[i], xs[i + 1])
            r.pop("mid", None)
            strands.append(dict(i=i, **r))
        for i in cand_f:
            fa = H[i]["fate"]
            r = bisect_pred(M, F, lambda x: history(M, F, x)["fate"] == fa, xs[i], xs[i + 1], nmax=CAP)
            if r.get("ok"):
                ha_ = history(M, F, mp.mpf(r["a"])); hb_ = history(M, F, mp.mpf(r["b"]))
                f1a = history(M1, F, mp.mpf(r["a"]))["fate"]; f1b = history(M1, F, mp.mpf(r["b"]))["fate"]
                r["falsifier"] = bool(ha_["sig"] == hb_["sig"] and ha_["fate"] != hb_["fate"]
                                      and min(ha_["gmin"], hb_["gmin"]) >= 0.1
                                      and (f1a, f1b) == (ha_["fate"], hb_["fate"]))
            fals.append(dict(i=i, **{k: v for k, v in r.items() if k != "stages"}))
    n_cert = sum(1 for s_ in strands if s_.get("certified"))
    n_fals = sum(1 for f in fals if f.get("falsifier"))
    if not guards["pass_"]:
        verdict = "VACUOUS"
    elif n_fals > 0:
        verdict = "FALSIFIED"
    elif n_cert >= 3:
        verdict = "SUPPORTED on the sample"
    else:
        verdict = "NOT ESTABLISHED"
    return dict(guards=guards, n_cand_strand=len(cand_s), n_cand_fals=len(cand_f), strands=strands, fals=fals,
                n_cert=n_cert, n_falsifiers=n_fals, verdict=verdict, sec_hist=t_hist, sec=time.time() - t0,
                calls=M.calls + M1.calls)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == "controls":
        o = controls()
        json.dump(o, open(os.path.join(OUT, "controls.json"), "w"), indent=1, default=str)
        print("VERDICT-controls:", "PASS" if o["all_pass"] else "FAIL (VOID)", flush=True)
    if sys.argv[1] == "window":
        o = window()
        json.dump(o, open(os.path.join(OUT, "window_ts.json"), "w"), indent=1, default=str)
        print("[ts] window done (values in file)", flush=True)
