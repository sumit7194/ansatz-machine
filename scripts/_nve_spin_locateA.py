"""POST HOC (labelled; region A was not covered by amendment S1, and its count was seen first): spin 9/10 region A has
count(F) = 3, against the expected 2 (Kerr's double zero). Locate the extra zero of F = tr[M1, M0] - 2 (circle pair,
Laurent c0): a coarse |F| grid over A, then a complex secant from the best grid point away from k = 0. Report whether
it is on the real axis (physical twist) or off it. If real, also evaluate the half-plane pair there (engine) for
Z1-Z4.
    NVE_SPIN=9/10 .venv/bin/python scripts/_nve_spin_locateA.py      -> data/nve/spin_locateA_9_10.out / .json"""
import json
import os
import sys

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_spin_scan as SS        # noqa: E402
import _nve_lower_kc as KC         # noqa: E402
import _nve_lower as L             # noqa: E402

mp.mp.dps = 50
G = json.load(open(os.path.join(L.OUT, f"spin_geo_{SS.TAG}.json")))
RA = SS.LauA(G["A"]["R0"])
seeds = SS.kerr_points()


def Fval(k, st):
    pr, o, ex = RA.state(k, st)
    lasso, gg = RA.loops(pr, o, ex)
    r = RA.evaluate(pr, o, ex, lasso, "0.35")
    return r, o, gg


def main():
    out = dict(grid=[])
    best = []
    FV = {}
    for im in (mp.mpf("-0.5"), mp.mpf("-0.25"), mp.mpf(0), mp.mpf("0.25"), mp.mpf("0.5")):
        st = list(seeds)
        if im != 0:
            for q in range(1, 5):
                _, st, _ = RA.state(mp.mpc(0, im * q / 4), st)
        base = list(st)
        for direction, xs in ((1, [mp.mpf(j) / 4 for j in range(0, 16)] + [SS.A_X1]), (-1, [-mp.mpf(1) / 4, -mp.mpf(1) / 2])):
            st = list(base)
            for x in xs:
                k = mp.mpc(x, im)
                r, st, gg = Fval(k, st)
                out["grid"].append((mp.nstr(k, 6), mp.nstr(abs(r["F"]), 6), gg["ok"]))
                FV[(mp.nstr(mp.re(k), 8), mp.nstr(mp.im(k), 8))] = r["F"]
                if abs(k) > mp.mpf("0.6"):
                    best.append((abs(r["F"]), k, list(st)))
                print(f"k={mp.nstr(k, 6)} |F|={mp.nstr(abs(r['F']), 6)} F={mp.nstr(r['F'], 8)} geo={gg['ok']}", flush=True)
    # Bridge (b): does F(conj k) = conj F(k) hold? Compare the Im = +0.25 and -0.25 rows.
    devs = []
    for (re_, im_), v in FV.items():
        if im_ == mp.nstr(mp.mpf("0.25"), 8) and (re_, mp.nstr(mp.mpf("-0.25"), 8)) in FV:
            w = FV[(re_, mp.nstr(mp.mpf("-0.25"), 8))]
            devs.append(float(abs(v - mp.conj(w)) / max(abs(v), mp.mpf(10) ** -30)))
    out["reflection_rel_dev"] = dict(max=max(devs), min=min(devs), n=len(devs))
    print("reflection F(conj k) vs conj F(k): relative deviation min/max", min(devs), max(devs), flush=True)
    best.sort(key=lambda t: t[0])
    f0v, k0, s0 = best[0]
    print("best grid point:", mp.nstr(k0, 8), mp.nstr(f0v, 6), flush=True)
    # complex secant on F
    rA, _, _ = Fval(k0, s0)
    k1 = k0 + mp.mpc("0.05", "0.05")
    rB, s1, _ = Fval(k1, s0)
    fa, fb, ka, kb = rA["F"], rB["F"], k0, k1
    for it in range(60):
        kc = kb - fb * (kb - ka) / (fb - fa)
        if abs(mp.im(kc)) > SS.A_Y + mp.mpf("0.2") or not (SS.A_X0 - mp.mpf("0.2") < mp.re(kc) < SS.A_X1 + mp.mpf("0.2")):
            print("secant left the region at", mp.nstr(kc, 10), flush=True)
            break
        rC, s1, gg = Fval(kc, s1)
        ka, fa, kb, fb = kb, fb, kc, rC["F"]
        if abs(fb) < mp.mpf("1e-30"):
            break
    out["zero"] = dict(k=mp.nstr(kb, 20), F=mp.nstr(fb, 6), trM0=mp.nstr(rC["T0"], 12), trM1=mp.nstr(rC["T1"], 12), geo_ok=gg["ok"])
    out["on_real_axis"] = bool(abs(mp.im(kb)) < mp.mpf("1e-20"))
    out["in_region_A"] = bool(SS.A_X0 <= mp.re(kb) <= SS.A_X1 and abs(mp.im(kb)) <= SS.A_Y)
    print("extra zero:", out["zero"], "on real axis:", out["on_real_axis"], "in A:", out["in_region_A"], flush=True)
    json.dump(out, open(os.path.join(L.OUT, f"spin_locateA_{SS.TAG}.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
