"""Endpoint k = 30/7 of the branched-twist family (data/nve/K307_PREREGISTRATION.md). Spin 3/5, E = 4/5.
Output: data/nve/k307.out (log), data/nve/k307_verdict.json"""
import json
import os
import sys

import mpmath as mp
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_lower as L                     # noqa: E402
import _nve_lower_kc as KC                 # noqa: E402
from _nve_monodromy import comm            # noqa: E402
from _ts_edge2 import fleet_guard          # noqa: E402

mp.mp.dps = 50
E2 = sp.Rational(16, 25)
A = mp.mpf(sp.N(L.A, 60))                     # spin from _nve_lower (NVE_SPIN, default 3/5)
K307 = mp.mpf(30) / 7
B0 = mp.mpf("1.35")
REF_C0 = mp.mpc("0.00196656555091338", "0.00101256196325471")
S_FIN = [2, -2, 1, -1, 0, mp.sqrt(2), -mp.sqrt(2), (mp.sqrt(5) - 1) / 2, -(mp.sqrt(5) - 1) / 2,
         (mp.sqrt(5) + 1) / 2, -(mp.sqrt(5) + 1) / 2]
V = dict(controls={}, endpoint={})


def log(*a):
    print(*a, flush=True)


def tr(M):
    return M[0][0] + M[1][1]


def disc_lasso(center, R, n=96):
    left = center - R
    circ = [center + R * mp.expj(mp.pi + 2 * mp.pi * j / n) for j in range(n + 1)]
    return [mp.mpc(B0), left] + circ[1:] + [mp.mpc(B0)]


def loops_at(pr, outer):
    rp, rm, pp, pm = outer
    lasso, delta = KC.capsule_lasso(rp, pp, [rm, pm])
    sep_l = KC.seg_dist(pm, rp, pp)
    cen = (rp + pp + pm) / 3
    md = max(abs(c - cen) for c in (rp, pp, pm))
    clear = abs(rm - cen) - md
    R = md + min(mp.mpf("0.15"), mp.mpf("0.4") * clear)
    gam = disc_lasso(cen, R)
    geo = dict(rho=float(pr.rho), lasso_clr=float(min(KC.path_dist(c, lasso) for c in (rm, pm))),
               disc_clr=float(abs(rm - cen) - R), disc_left=float(mp.re(cen) - R),
               outer_min_abs=float(min(abs(c) for c in outer)))
    geo["sep_lasso"], geo["sep_disc"] = float(sep_l), float(clear)
    geo["ok"] = (pr.rho <= 1.1 and geo["lasso_clr"] >= 0.3 * float(sep_l) and geo["disc_clr"] >= 0.3 * float(clear)
                 and geo["disc_left"] >= float(A) + 0.1 and geo["outer_min_abs"] >= 1.55)   # A1: scale-relative
    return lasso, gam, geo


def mono(pr, outer, step, paths):
    W = L.Walker(pr, list(outer), step)
    return [W.walk(p, KC.I2()) for p in paths]


def track_to(k_target, seeds):
    pr = KC.ProblemC(KC.FK, k_target, E2)
    return pr, [KC.newton(pr, x, w) for x, w in seeds]


# ---------------------------------------------------------------------------------------- ray formula (T14)
def c0_ray(zz, k):          # A1: runs at the caller's precision (the old internal workdps(30) zeroed mp.diff)
    if True:
        u = zz / A
        c4, c2, c0p = 90 - 21 * k, -(60 - 18 * k), 10 - k
        f = lambda x: x * (1 - x) * u**-2 * (1 + x**2 * u**-2) ** -3 * mp.sqrt(c4 + c2 * x**2 * u**-2 + c0p * x**4 * u**-4)
        return -(mp.sqrt(mp.mpf(8) / 5) / A) * mp.quad(f, [0, 1])


def G_ray(zz, k, which):
    n, g = zz**2 - 2 * zz + A**2, zz**2 + A**2
    c = c0_ray(zz, k)
    G2 = n * n + c * c * g * g
    return (mp.mpf(16) / 25) * G2 - n * g if which == 1 else G2   # A1 rerun 2: mp E^2 (a sympy E2 leaked here and crashed mp.diff)


def newton_ray(x, k, which):
    with mp.workdps(30):
        for _ in range(40):
            f = G_ray(x, k, which)
            d = mp.diff(lambda t: G_ray(t, k, which), x)
            dx = f / d
            x = x - dx
            if abs(dx) < mp.mpf(10) ** -20:
                return x
    raise RuntimeError("newton_ray")


def main():
    g = fleet_guard()
    if g:
        raise SystemExit(f"NOT STARTED: {g}")
    # C0 reproduction (w^8 path)
    seeds = [(mp.mpc("1.9344259"), 1), (mp.mpc("-3.4899815"), 1), (mp.mpc(2, "0.6"), 2), (mp.mpc(2, "-0.6"), 2)]
    st = list(seeds)
    for kk in [mp.mpf(j) / 100 for j in range(1, 11)]:
        pr, pos = track_to(kk, st)
        st = [(p, w) for p, (_, w) in zip(pos, seeds)]
    lasso, gam, geo = loops_at(pr, pos)
    M0, M1 = mono(pr, pos, "0.35", [KC.M0_PATH, lasso])
    F = tr(comm(M1, M0)) - 2
    V["controls"]["C0"] = dict(F=mp.nstr(F, 20), diff=float(abs(F - REF_C0)), ok=bool(abs(F - REF_C0) < 1e-15))
    log("C0", V["controls"]["C0"])
    # P1 Kerr through the same script
    pr0, pos0 = track_to(mp.mpf(0), seeds)
    lasso0, gam0, geo0 = loops_at(pr0, pos0)
    M0k, M1k = mono(pr0, pos0, "0.35", [KC.M0_PATH, lasso0])
    Fk, t0k = tr(comm(M1k, M0k)) - 2, tr(M0k) - 2
    V["controls"]["P1"] = dict(F=float(abs(Fk)), trM0m2=float(abs(t0k)), ok=bool(abs(Fk) <= 1e-25 and abs(t0k) <= 1e-25))
    log("P1", V["controls"]["P1"])
    # endpoint: positions by Newton from the k = 4.1 track, then geometry + counts
    st = list(seeds)
    for kk in [mp.mpf(j) / 10 for j in range(1, 41)] + [mp.mpf("4.05"), mp.mpf("4.1")]:
        pr, pos = track_to(kk, st)
        st = [(p, w) for p, (_, w) in zip(pos, seeds)]
    prE, posE = track_to(K307, st)
    lassoE, gamE, geoE = loops_at(prE, posE)
    with mp.workdps(30):
        w = lambda f, R: L.winding(f, mp.mpf(R), N=2000)
        g1, g2 = (lambda x: prE.G(x)[0]), (lambda x: prE.G(x)[2])
        rin = prE.rho + mp.mpf("0.05")
        cnt = (w(g1, 60) - w(g1, "1.3"), w(g2, 60) - w(g2, "1.3"), w(g1, "1.3") - w(g1, rin), w(g2, "1.3") - w(g2, rin))
    geoE["counts"] = cnt
    geoE["ok"] = geoE["ok"] and cnt == (2, 2, 0, 0)
    geoE["points"] = [mp.nstr(p, 12) for p in posE]
    V["controls"]["C-geo"] = geoE
    log("C-geo", geoE)
    # C-c0: Laurent (w^10 path) vs ray
    errs = []
    for zz in (mp.mpc(1.4, 0.3), mp.mpc(2, 0.5), mp.mpc(2.5, -1), mp.mpc(3, 2), mp.mpc(1.2, 2.5)):   # A1: Re z > a only
        errs.append(abs(L.c0_eval(prE.C, zz) - c0_ray(zz, K307)))
    V["controls"]["C-c0"] = dict(maxdiff=float(max(errs)), ok=bool(max(errs) < 1e-15))
    zo = mp.mpc(-1.8, 2.2)                                   # A1 must-fail: off-domain point, other branch
    lo, ro = L.c0_eval(prE.C, zo), c0_ray(zo, K307)
    V["controls"]["C-c0-mustfail"] = dict(diff=float(abs(lo - ro)), sum=float(abs(lo + ro)),
                                          ok=bool(abs(lo - ro) >= 1e-3 and abs(lo + ro) <= 1e-15))
    log("C-c0", V["controls"]["C-c0"], "must-fail (flagged other branch)", V["controls"]["C-c0-mustfail"])
    # A1: planted known derivative (Laurent exact derivative vs mp.diff of the ray formula)
    worst, small = 0.0, 9.0
    for kk in (mp.mpf(4), mp.mpf(39) / 10, K307):
        prk = KC.ProblemC(KC.FK, kk, E2)
        for zz in (mp.mpc(1.4, 0.3), mp.mpc(2, 0.5), mp.mpc(3, 2)):
            dl = L.c0_eval(prk.C, zz, 1)
            dr = mp.diff(lambda t: c0_ray(t, kk), zz)
            worst, small = max(worst, float(abs(dl - dr))), min(small, float(abs(dl)))
    V["controls"]["C-deriv"] = dict(worst=worst, min_abs=small, ok=bool(worst <= 1e-15 and small >= 1e-4))
    log("C-deriv", V["controls"]["C-deriv"])
    # endpoint monodromies at two steps
    res = {}
    for step in ("0.35", "0.2", "0.12"):
        M0, M1, Gm, M0sq = mono(prE, posE, step, [KC.M0_PATH, lassoE, gamE, L.arc(B0, 0, 4 * mp.pi)])
        res[step] = dict(F=tr(comm(M1, M0)) - 2, Fh=tr(comm(M1, Gm)) - 2, trM0=tr(M0), trM1=tr(M1), trG=tr(Gm),
                         P2=tr(comm(M0sq, M0)) - 2)
        log("endpoint", step, {kk: mp.nstr(v, 15) for kk, v in res[step].items()})
    a, b = res["0.35"], res["0.12"]
    rel = max(float(abs(x[kk] - y[kk]) / max(abs(y[kk]), mp.mpf(10) ** -30)) for kk in ("F", "Fh", "trM0", "trM1", "trG")
              for x, y in ((res["0.35"], res["0.2"]), (res["0.35"], res["0.12"]), (res["0.2"], res["0.12"])))
    V["controls"]["C-step"] = dict(worst_rel=rel, ok=rel <= 1e-15)
    V["controls"]["P2"] = dict(val=float(abs(b["P2"])), ok=bool(abs(b["P2"]) <= 1e-25))
    log("C-step", V["controls"]["C-step"], "P2", V["controls"]["P2"])
    dS = min(abs(b["trM1"] - s) for s in S_FIN)
    V["endpoint"] = {kk: mp.nstr(v, 20) for kk, v in b.items()}
    V["endpoint"]["dist_trM1_to_S"] = float(dS)
    # C-cont: convergence from below (ray formula), and the circle picture's escaping branch point
    samp = [lassoE[i] for i in range(1, len(lassoE) - 1, max(1, len(lassoE) // 5))][:4] + \
           [gamE[i] for i in range(2, len(gamE) - 1, max(1, len(gamE) // 5))][:4]
    with mp.workdps(30):
        cE = [c0_ray(p, K307) for p in samp]
        dE = [mp.diff(lambda t: c0_ray(t, K307), p) for p in samp]
        rows = []
        posR = [newton_ray(posE[i], K307, 1 if i < 2 else 2) for i in (0, 2, 3)]
        for dl in (mp.mpf("1e-1"), mp.mpf("1e-2"), mp.mpf("1e-3"), mp.mpf("1e-4")):
            kk = K307 - dl
            dc = max(abs(c0_ray(p, kk) - c) for p, c in zip(samp, cE))
            dd = max(abs(mp.diff(lambda t: c0_ray(t, kk), p) - d) for p, d in zip(samp, dE))
            pk = [newton_ray(x, kk, 1 if j == 0 else 2) for j, x in enumerate(posR)]
            dp = max(abs(x - y) for x, y in zip(pk, posR))
            wr = sp.Poly((90 - 21 * sp.nsimplify(str(kk))) * sp.Symbol('w')**2 - (60 - 18 * sp.nsimplify(str(kk))) * sp.Symbol('w')
                         + (10 - sp.nsimplify(str(kk))), sp.Symbol('w')).nroots()
            zb = float(A) * max(abs(complex(r)) for r in wr) ** 0.5
            rows.append((float(dl), float(dc), float(dd), float(dp), zb))
            log(f"C-cont delta={float(dl):.0e}: max|dc0|={float(dc):.3e} max|dc0'|={float(dd):.3e} max|dpoint|={float(dp):.3e} |z_b|={zb:.3f}")
    import math
    def slope(col):
        xs = [math.log(r[0]) for r in rows]; ys = [math.log(r[col]) for r in rows]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    mono_ok = all(rows[i][c] > rows[i + 1][c] for i in range(3) for c in (1, 2, 3)) and all(r[2] > 0 for r in rows)
    sl = (slope(1), slope(3))
    V["controls"]["C-cont"] = dict(rows=rows, slope_c0=sl[0], slope_points=sl[1],
                                   ok=bool(mono_ok and all(0.3 <= s_ <= 1.2 for s_ in sl) and rows[-1][3] < 1e-2))
    V["controls"]["C-cont-fire"] = dict(zb_smallest_delta=rows[-1][4], ok=rows[-1][4] > 1.35)
    log("C-cont", V["controls"]["C-cont"]["ok"], "slopes", sl, "| must-fire", V["controls"]["C-cont-fire"])
    ok = all(v["ok"] for v in V["controls"].values())
    nz = lambda x: abs(x) >= 1e-8
    if not ok:
        V["verdict"] = "VOID"
    elif V["controls"]["C-step"]["worst_rel"] > 1e-15:
        V["verdict"] = "UNDETERMINED"
    elif abs(b["F"]) <= 1e-25:
        V["verdict"] = "ENDPOINT VA-COMPATIBLE"
    elif all(nz(b[kk]) for kk in ("F", "Fh", "trM0", "trM1", "trG")) and abs(mp.im(b["trM1"])) > 1e-8 and dS >= 1e-3:
        V["verdict"] = "ENDPOINT OBSTRUCTED (non-VA); no accumulation of K*(3/5) at 30/7 at E = 4/5 [verdict under post-unblinding amendment A1]"
    else:
        V["verdict"] = "UNDETERMINED (a trace near zero or near S)"
    json.dump(V, open(os.path.join(L.OUT, "k307_A1_verdict.json"), "w"), indent=1, default=str)
    log("VERDICT", V["verdict"])


if __name__ == "__main__":
    main()
