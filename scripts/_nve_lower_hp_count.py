"""Window count (data/nve/WINDOW_PREREGISTRATION.md): half-plane argument principle over k in
R = [3.95, 30/7 - 1e-12] x [-0.25, 0.25]i, spin 3/5, E = 4/5, with c0 from the _nve_lower_hp engine.
Output: data/nve/window.out (log), data/nve/window_verdict.json"""
import json
import os
import sys

import mpmath as mp
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_lower as L                       # noqa: E402
import _nve_lower_kc as KC                   # noqa: E402
import _nve_lower_hp as HP                   # noqa: E402
import _nve_lower_k307 as K7                 # noqa: E402
from _nve_monodromy import comm, mul         # noqa: E402
from _ts_edge2 import fleet_guard            # noqa: E402

mp.mp.dps = 50
E2 = sp.Rational(16, 25)
X0, X1, Y = mp.mpf("3.95"), mp.mpf(30) / 7 - mp.mpf("1e-12"), mp.mpf("0.25")
CC, CR = mp.mpc("1.85"), mp.mpf("0.6")
S_FIN = [2, -2, 1, -1, 0, mp.sqrt(2), -mp.sqrt(2), (mp.sqrt(5) - 1) / 2, -(mp.sqrt(5) - 1) / 2,
         (mp.sqrt(5) + 1) / 2, -(mp.sqrt(5) + 1) / 2]
SEED_END = [(mp.mpc("1.80082086157"), 1), (mp.mpc("1.80332022637", "0.0534116583167"), 2),
            (mp.mpc("1.80332022637", "-0.0534116583167"), 2)]
PI4 = float(mp.pi / 4) + 1e-12
V = dict(controls={}, guards={})


def log(*a):
    print(*a, flush=True)


def tr(M):
    return M[0][0] + M[1][1]


def build(k, NC=220):
    return HP.ProblemHP(KC.FK, k, E2, NC)


def track(pr, st):
    return [KC.newton(pr, x, w) for x, w in st]


def loops(pr, pos, contain=True):
    rp, pp, pm = pos
    excl = list(pr.eng.sing)
    lasso, delta = KC.capsule_lasso(rp, pp, [pm])
    sep = KC.seg_dist(pm, rp, pp)
    cen = (rp + pp + pm) / 3
    md = max(abs(c - cen) for c in pos)
    clear = min(abs(e - cen) for e in excl) - md
    R = md + min(mp.mpf("0.15"), mp.mpf("0.4") * clear)
    gam = K7.disc_lasso(cen, R)
    pts = lasso + gam
    reach = max(abs(p - HP.Z0) for p in pts)
    g = dict(sep=float(sep), lasso_pm=float(KC.path_dist(pm, lasso)),
             lasso_excl=float(min(KC.path_dist(e, lasso) for e in excl)),
             disc_excl=float(min(abs(e - cen) - R for e in excl)), reach=float(reach), Rc=float(pr.eng.Rc),
             cut_ok=pr.eng.guard(CC, CR)["cut_ok"],
             contain=float(max(abs(p - CC) for p in pts)))
    g["ok"] = bool(g["lasso_pm"] >= 0.3 * g["sep"] and g["lasso_excl"] >= 0.05 and g["disc_excl"] >= 0.05
                   and g["reach"] <= 0.6 * g["Rc"] and g["cut_ok"] and (g["contain"] <= 0.55 or not contain))
    return lasso, gam, g


def evaluate(pr, pos, lasso, gam, step="0.35"):
    W = L.Walker(pr, list(pos) + list(pr.eng.sing), step)
    M1, Gm = W.walk(lasso, KC.I2()), W.walk(gam, KC.I2())
    return dict(F=tr(comm(M1, Gm)) - 2, T1=tr(M1), TG=tr(Gm), T1G=tr(mul(M1, Gm)))


def classify(r, tol=mp.mpf("1e-12")):
    small = [abs(r[x]) < tol for x in ("T1", "TG", "T1G")]
    if abs(r["F"]) < tol:
        return "reducible?"
    if sum(small) >= 2:
        return "imprimitive (VA)"
    if min(abs(r["T1"] - s) for s in S_FIN) < mp.mpf("1e-3") and abs(mp.im(r["T1"])) < tol:
        return "finite?"
    return "non-VA"


def count(vals):
    v = vals + vals[:1]
    tot = mp.fsum(mp.arg(b / a) for a, b in zip(v[:-1], v[1:]))
    mx = max(abs(mp.arg(b / a)) for a, b in zip(v[:-1], v[1:]))
    return int(mp.nint(tot / (2 * mp.pi))), float(tot / (2 * mp.pi)), float(mx)


def funcs(r):
    d = {"F": r["F"], "T1": r["T1"], "TG": r["TG"], "T1G": r["T1G"]}
    for i, s in enumerate(S_FIN):
        d[f"T1-s{i}"] = r["T1"] - s
    return d


def wind_G(pr, which):
    with mp.workdps(30):
        tot, prev = mp.mpf(0), None
        for j in range(1601):
            v = pr.G(CC + CR * mp.expj(2 * mp.pi * j / 1600))[0 if which == 1 else 2]
            if prev is not None:
                tot += mp.arg(v / prev)
            prev = v
        return int(mp.nint(tot / (2 * mp.pi)))


def main():
    g = fleet_guard()
    if g:
        raise SystemExit(f"NOT STARTED: {g}")
    pts6 = [mp.mpc(1.35, 0), mp.mpc(1.8, 0.2), mp.mpc(2.3, -0.4), mp.mpc(1.6, 0.5), mp.mpc(2.5, 0.3), mp.mpc(1.9, -0.6)]
    # C-repro and MF-trunc
    worst, worst_tr = 0.0, 0.0
    for k in (mp.mpf(4), mp.mpf(30) / 7):
        e, et, lau = HP.C0Engine(k), HP.C0Engine(k, NC=12), KC.ProblemC(KC.FK, k, E2)
        for p in pts6:
            worst = max(worst, float(abs(e.c0(p) - L.c0_eval(lau.C, p))), float(abs(e.c0(p, 1) - L.c0_eval(lau.C, p, 1))))
            worst_tr = max(worst_tr, float(abs(et.c0(p) - L.c0_eval(lau.C, p))))
    V["controls"]["C-repro"] = dict(worst=worst, ok=worst <= 1e-40)
    # C-repro-F at 4.05 (engine vs Laurent, same loops) + MF-trunc F
    k = mp.mpf("4.05")
    st = list(SEED_END)
    for kk in [X1 - (X1 - k) * j / 12 for j in range(1, 13)]:
        prh = build(kk); pos = track(prh, st); st = [(p, w) for p, (_, w) in zip(pos, SEED_END)]
    lasso, gam, geo = loops(prh, pos)
    rh = evaluate(prh, pos, lasso, gam)
    prl = KC.ProblemC(KC.FK, k, E2)
    posl = [KC.newton(prl, x, w) for x, (_, w) in zip(pos, SEED_END)]
    W = L.Walker(prl, list(posl) + list(prh.eng.sing), "0.35")
    M1, Gm = W.walk(lasso, KC.I2()), W.walk(gam, KC.I2())
    rl = dict(F=tr(comm(M1, Gm)) - 2, T1=tr(M1), TG=tr(Gm))
    dF = max(float(abs(rh[x] - rl[x])) for x in ("F", "T1", "TG"))
    prt = build(k, NC=12)
    rt = evaluate(prt, pos, lasso, gam)
    V["controls"]["C-repro-F-4.05"] = dict(diff=dF, ok=dF <= 1e-20)
    V["controls"]["MF-trunc"] = dict(c0_diff=worst_tr, F_diff=float(abs(rt["F"] - rh["F"])),
                                     ok=bool(worst_tr >= 1e-30 and abs(rt["F"] - rh["F"]) >= 1e-15))
    log("C-repro", V["controls"]["C-repro"], "C-repro-F", V["controls"]["C-repro-F-4.05"], "MF-trunc", V["controls"]["MF-trunc"])
    # endpoint vs §161
    prE = build(mp.mpf(30) / 7); posE = track(prE, SEED_END); lE, gE, _ = loops(prE, posE)
    rE = evaluate(prE, posE, lE, gE)
    d161 = float(abs(rE["F"] - mp.mpc("-0.737260531790084", "-2.7690338008439")))
    V["controls"]["C-repro-F-30/7"] = dict(diff=d161, ok=d161 <= 1e-12)
    log("C-repro-F-30/7", V["controls"]["C-repro-F-30/7"])
    # P1 Kerr: imprimitive
    pr0 = build(mp.mpf(0))
    pos0 = track(pr0, [(mp.mpc("1.9344259"), 1), (mp.mpc(2, "0.6"), 2), (mp.mpc(2, "-0.6"), 2)])
    l0, g0, geo0 = loops(pr0, pos0, contain=False)
    r0 = evaluate(pr0, pos0, l0, g0)
    V["controls"]["P1-Kerr"] = dict(TG=float(abs(r0["TG"])), T1G=float(abs(r0["T1G"])), cls=classify(r0),
                                    ok=bool(abs(r0["TG"]) <= 1e-15 and abs(r0["T1G"]) <= 1e-15 and classify(r0) == "imprimitive (VA)"))
    log("P1", V["controls"]["P1-Kerr"])
    # P2 planted non-VA member k = 41/10: circle pair (Laurent) and half-plane classifier
    k2 = mp.mpf(41) / 10
    seeds0 = [(mp.mpc("1.9344259"), 1), (mp.mpc("-3.4899815"), 1), (mp.mpc(2, "0.6"), 2), (mp.mpc(2, "-0.6"), 2)]
    st = list(seeds0)
    for kk in [mp.mpf(j) / 10 for j in range(1, 42)]:
        prc, pc = K7.track_to(kk, st); st = [(p, w) for p, (_, w) in zip(pc, seeds0)]
    lc_, gc_, _ = K7.loops_at(prc, pc)
    M0c, M1c = K7.mono(prc, pc, "0.35", [KC.M0_PATH, lc_])
    circ = dict(F=tr(comm(M1c, M0c)) - 2, trM0=tr(M0c), trM1=tr(M1c))
    circ_nonva = bool(all(abs(circ[x]) > 1e-8 for x in circ) and abs(mp.im(circ["trM1"])) > 1e-8
                      and min(abs(circ["trM1"] - s) for s in S_FIN) > 1e-3)
    prh2 = build(k2); posh2 = track(prh2, [(pc[0], 1), (pc[2], 2), (pc[3], 2)]); l2, g2, _ = loops(prh2, posh2)
    r2 = evaluate(prh2, posh2, l2, g2)
    V["controls"]["P2-planted-4.1"] = dict(circle={x: mp.nstr(v, 10) for x, v in circ.items()}, circle_nonVA=circ_nonva,
                                           halfplane=classify(r2), ok=bool(circ_nonva and classify(r2) == "non-VA"))
    log("P2", V["controls"]["P2-planted-4.1"])
    # G-geo interior grid + G-count
    geo_fail, cnt = [], {}
    for j in range(11):
        im = mp.mpf(j - 5) / 20                      # exact: -0.25 ... 0.25, im == 0 at j = 5
        st = list(SEED_END)
        for kk in [mp.mpc(X1, im * q / 5) for q in range(1, 6)] if im != 0 else []:
            pr_ = build(kk); p_ = track(pr_, st); st = [(p, w) for p, (_, w) in zip(p_, SEED_END)]
        nx = int((X1 - X0) / mp.mpf("0.025")) + 1
        xs = [X1 - mp.mpf("0.025") * i for i in range(nx) if X1 - mp.mpf("0.025") * i > X0 + mp.mpf("1e-9")] + [X0]
        for x in xs:
            kk = mp.mpc(x, im)
            pr_ = build(kk); p_ = track(pr_, st); st = [(p, w) for p, (_, w) in zip(p_, SEED_END)]
            _, _, gg = loops(pr_, p_)
            if not gg["ok"]:
                geo_fail.append((mp.nstr(kk, 8), gg))
            corner = abs(im) == Y and (x == X1 or x == X0)
            if corner or (im == 0 and (x == X1 or abs(x - mp.mpf("4.1")) < mp.mpf("0.0126"))):
                c = (wind_G(pr_, 1), wind_G(pr_, 2))
                cnt[mp.nstr(kk, 8)] = c
        log(f"G-geo row Im={float(im):+.2f}: fails so far {len(geo_fail)}")
    V["guards"]["G-geo"] = dict(ok=not geo_fail, fails=[str(f) for f in geo_fail[:5]])
    V["guards"]["G-count"] = dict(counts=cnt, ok=bool(cnt) and all(v == (1, 2) for v in cnt.values()))
    log("G-geo", V["guards"]["G-geo"]["ok"], "G-count", cnt)
    # boundary (ccw from (X1, 0))
    corners = [mp.mpc(X1, 0), mp.mpc(X1, Y), mp.mpc(X0, Y), mp.mpc(X0, -Y), mp.mpc(X1, -Y), mp.mpc(X1, 0)]
    ks = [corners[0]]
    for a_, b_ in zip(corners[:-1], corners[1:]):
        n = max(1, int(mp.ceil(abs(b_ - a_) / mp.mpf("0.02"))))
        ks += [a_ + (b_ - a_) * j / n for j in range(1, n + 1)]
    ks = ks[:-1]
    st = list(SEED_END)
    samples = []
    for k in ks:
        pr_ = build(k); p_ = track(pr_, st); st = [(p, w) for p, (_, w) in zip(p_, SEED_END)]
        l_, g_, gg = loops(pr_, p_)
        samples.append([k, funcs(evaluate(pr_, p_, l_, g_)), gg["ok"], st, gg])
    log(f"boundary: {len(samples)} samples, geo fails {sum(not s[2] for s in samples)}")
    for lev in range(5):
        new, ins = [], 0
        for i in range(len(samples)):
            new.append(samples[i])
            a_, b_ = samples[i], samples[(i + 1) % len(samples)]
            if max(abs(mp.arg(b_[1][f] / a_[1][f])) for f in a_[1]) > mp.pi / 4:
                km = (a_[0] + b_[0]) / 2
                pr_ = build(km); p_ = track(pr_, a_[3]); stm = [(p, w) for p, (_, w) in zip(p_, SEED_END)]
                l_, g_, gg = loops(pr_, p_)
                new.append([km, funcs(evaluate(pr_, p_, l_, g_)), gg["ok"], stm, gg]); ins += 1
        samples = new
        log(f"refinement {lev + 1}: inserted {ins}, now {len(samples)}")
        if ins == 0:
            break
    V["guards"]["G-geo-boundary"] = dict(ok=all(s[2] for s in samples))
    # G-step at every 4th original sample
    worst = 0.0
    for i in range(0, len(ks), 4):
        s_ = next(s for s in samples if s[0] == ks[i])
        pr_ = build(s_[0]); p_ = [x for x, _ in s_[3]]; l_, g_, _ = loops(pr_, p_)
        rs = [evaluate(pr_, p_, l_, g_, st_) for st_ in ("0.35", "0.2", "0.12")]
        for x in ("F", "T1", "TG", "T1G"):
            for a_, b_ in ((0, 1), (0, 2), (1, 2)):
                worst = max(worst, float(abs(rs[a_][x] - rs[b_][x]) / max(abs(rs[b_][x]), mp.mpf(10) ** -30)))
    V["guards"]["G-step"] = dict(worst_rel=worst, ok=worst <= 1e-15)
    log("G-step", V["guards"]["G-step"])
    C = {f: count([s[1][f] for s in samples]) for f in samples[0][1]}
    V["counts"] = {f: dict(count=c[0], raw=c[1], max_darg=c[2]) for f, c in C.items()}
    V["guards"]["G-arg"] = dict(ok=all(c[2] <= PI4 for c in C.values()))
    log("counts", {f: c[0] for f, c in C.items()}, "max darg", max(c[2] for c in C.values()))
    Fs = [s[1]["F"] for s in samples]
    kin, kout = mp.mpc("4.15", "0.1"), mp.mpc(5, 1)
    c2 = (count([f * (s[0] - kin) for f, s in zip(Fs, samples)])[0], count([f / (s[0] - kin) for f, s in zip(Fs, samples)])[0],
          count([f * (s[0] - kout) for f, s in zip(Fs, samples)])[0])
    V["controls"]["C2"] = dict(mul=c2[0], div=c2[1], out=c2[2], ok=c2 == (C["F"][0] + 1, C["F"][0] - 1, C["F"][0]))
    log("C2", V["controls"]["C2"])
    # sliver samples
    sl = {}
    st = list(SEED_END)
    for j in (13, 14, 15):
        kk = mp.mpf(30) / 7 - mp.mpf(10) ** (-j)
        pr_ = build(kk); p_ = track(pr_, st); l_, g_, _ = loops(pr_, p_)
        r_ = evaluate(pr_, p_, l_, g_)
        sl[f"30/7-1e-{j}"] = dict(F=mp.nstr(r_["F"], 15), T1=mp.nstr(r_["T1"], 15), cls=classify(r_))
    V["sliver"] = sl
    log("sliver", sl)
    ok = all(v["ok"] for v in V["controls"].values()) and all(v["ok"] for n, v in V["guards"].items() if n != "G-arg")
    cF, cT1 = C["F"][0], C["T1"][0]
    cS = all(C[f"T1-s{i}"][0] == 0 for i in range(len(S_FIN)))
    if not ok:
        V["verdict"] = "VOID"
    elif not V["guards"]["G-arg"]["ok"]:
        V["verdict"] = "UNDETERMINED (arg resolution)"
    elif cF == 0 and cT1 == 0 and cS and (C["TG"][0] == 0 or C["T1G"][0] == 0):
        V["verdict"] = "NO EXCEPTIONAL k IN R"
    elif cF == 0 and cT1 == 0 and cS:
        V["verdict"] = "UNDETERMINED (TG and T1G both have zeros in R; locate before deciding)"
    else:
        V["verdict"] = f"EXCEPTIONAL CANDIDATES (counts F {cF}, T1 {cT1}, S-ok {cS})"
    json.dump(V, open(os.path.join(L.OUT, "window_verdict.json"), "w"), indent=1, default=str)
    log("VERDICT", V["verdict"])


if __name__ == "__main__":
    main()
