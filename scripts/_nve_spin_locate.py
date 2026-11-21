"""POST-HOC (labelled; not in SPIN_PREREGISTRATION): spin 4/5 region B had count(TG) = count(T1G) = 1, so the registered
sufficient rule failed (verdict EXCEPTIONAL CANDIDATES). Imprimitivity needs two of (T1, TG, T1G) to vanish at the
SAME k; T1 is zero-free in B. So: locate the zero of TG (real on real k, because the disc loop is reflection-symmetric,
so a single zero in the symmetric box is real) and the zero of T1G (complex secant), then evaluate the other traces
there. Distinct zeros mean no imprimitive point in B.
    NVE_SPIN=4/5 .venv/bin/python scripts/_nve_spin_locate.py     -> data/nve/spin_locate_4_5.out"""
import json
import os
import sys

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_spin_scan as SS          # noqa: E402
import _nve_lower_kc as KC           # noqa: E402
import _nve_lower as L               # noqa: E402

mp.mp.dps = 50


def setup():
    G = json.load(open(os.path.join(L.OUT, f"spin_geo_{SS.TAG}.json")))
    seeds = SS.kerr_points()
    RB = SS.HalfB(G["B_rule"]["Z0"], G["B_rule"]["bB"], 0, 0)
    st = [seeds[0], seeds[2], seeds[3]]
    for q in range(1, 43):
        prb = RB.problem(SS.B_X1 * q / 42)
        st = [(KC.newton(prb, x, w), w) for x, w in st]
    RB.cen0 = sum(x for x, _ in st) / 3
    RB.span = mp.mpf("0.6417605290138165")          # frozen value printed by the registered run
    return RB, st


def evaluate(RB, k, st):
    prb = RB.problem(k)
    p_ = [KC.newton(prb, x, w) for x, w in st]
    l_, g_, gg = RB.loops(prb, p_)
    r = RB.evaluate(prb, p_, l_, g_)
    return r, [(p, w) for p, (_, w) in zip(p_, st)], gg


def main():
    RB, st_end = setup()
    # 1. real scan of TG on [3.95, X1], tracking leftwards from the endpoint
    xs = [SS.B_X1 - (SS.B_X1 - SS.B_X0) * j / 12 for j in range(13)]
    st, vals = list(st_end), []
    for x in xs:
        r, st, gg = evaluate(RB, mp.mpc(x, 0), st)
        vals.append((x, r, list(st)))
        print(f"k={mp.nstr(x, 10)} TG={mp.nstr(r['TG'], 12)} T1G={mp.nstr(r['T1G'], 10)} geo_ok={gg['ok']}", flush=True)
    br = next(((vals[i], vals[i + 1]) for i in range(12) if mp.re(vals[i][1]["TG"]) * mp.re(vals[i + 1][1]["TG"]) < 0), None)
    out = {}
    if br is None:
        print("no real sign change of TG found on the grid", flush=True)
    else:
        (xa, ra, sa), (xb, rb, sb) = br
        for _ in range(40):                      # bisection on Re TG (TG real on real k)
            xm = (xa + xb) / 2
            rm, sm, _ = evaluate(RB, mp.mpc(xm, 0), sa)
            if mp.re(ra["TG"]) * mp.re(rm["TG"]) <= 0:
                xb, rb, sb = xm, rm, sm
            else:
                xa, ra, sa = xm, rm, sm
            if xb - xa < mp.mpf("1e-14"):
                break
        kTG = (xa + xb) / 2
        rT, sT, _ = evaluate(RB, mp.mpc(kTG, 0), sa)
        out["TG_zero"] = dict(k=mp.nstr(kTG, 16), TG=mp.nstr(rT["TG"], 6), T1G=mp.nstr(rT["T1G"], 12), T1=mp.nstr(rT["T1"], 12),
                              F=mp.nstr(rT["F"], 12), Im_TG_offaxis_check=None)
        print("TG zero:", out["TG_zero"], flush=True)
        # 2. zero of T1G by complex secant, started near the TG zero
        k0, k1 = mp.mpc(kTG, 0), mp.mpc(kTG, "0.02")
        s0 = sT
        f0 = rT["T1G"]
        r1, s1, _ = evaluate(RB, k1, s0)
        f1 = r1["T1G"]
        for it in range(40):
            k2 = k1 - f1 * (k1 - k0) / (f1 - f0)
            if abs(mp.im(k2)) > SS.B_Y or mp.re(k2) < SS.B_X0 or mp.re(k2) > SS.B_X1:
                print("secant left the region at", mp.nstr(k2, 10), flush=True)
                break
            r2, s2, _ = evaluate(RB, k2, s1)
            k0, f0, k1, f1, s1 = k1, f1, k2, r2["T1G"], s2
            if abs(f1) < mp.mpf("1e-30"):
                break
        out["T1G_zero"] = dict(k=mp.nstr(k1, 16), T1G=mp.nstr(f1, 6), TG=mp.nstr(r2["TG"], 12), T1=mp.nstr(r2["T1"], 12), F=mp.nstr(r2["F"], 12))
        print("T1G zero:", out["T1G_zero"], flush=True)
        out["distance"] = mp.nstr(abs(k1 - kTG), 10)
        print("distance between the zeros:", out["distance"], flush=True)
    json.dump(out, open(os.path.join(L.OUT, f"spin_locate_{SS.TAG}.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
