"""Spin coverage for the branched-twist family (follow-up to §162, Bridge GO 2026-11-21).
Spin is set by the environment, e.g. NVE_SPIN=3/10. E = 4/5. Modes:
    geo   geometry only, no F (design measurement: region-A circle radius, region-B guards)
    run   the registered pipeline (prereg data/nve/SPIN_PREREGISTRATION.md)
Region A (circle picture, Laurent c0): k in [-1/2, 4] x [-1/2, 1/2]i, contains the Kerr double zero at k = 0.
Region B (half-plane picture, exact-radicand engine): k in [3.95, 30/7 - 1e-12] x [-1/4, 1/4]i.
"""
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

mp.mp.dps = 50
E2 = sp.Rational(16, 25)
Ev = mp.mpf(4) / 5
A = mp.mpf(sp.N(L.A, 60))
SPIN = str(L.A)
TAG = SPIN.replace("/", "_")
# per-spin region edges, fixed from the geometry scan (data/nve/spin_geo.out), before any F: (A_X1, B_X0, B_Y)
EDGES = {"3/10": ("4", "3.95", "0.25"), "4/5": ("4", "3.95", "0.25"), "9/10": ("3.85", "3.8", "0.15"),
         "3/5": ("4", "3.95", "0.25")}
_e = EDGES.get(SPIN, ("4", "3.95", "0.25"))
A_X0, A_X1, A_Y = mp.mpf("-0.5"), mp.mpf(_e[0]), mp.mpf("0.5")
B_X0, B_X1, B_Y = mp.mpf(_e[1]), mp.mpf(30) / 7 - mp.mpf("1e-12"), mp.mpf(_e[2])


def log(*a):
    print(*a, flush=True)


def kerr_points():
    """k = 0: r+-, roots of (E^2-1) z^2 - (4E^2-2) z + E^2(4+a^2) - a^2; p+- = 2 +- ia."""
    c = [Ev**2 - 1, -(4 * Ev**2 - 2), Ev**2 * (4 + A**2) - A**2]
    r = sorted(mp.polyroots(c), key=lambda x: -mp.re(x))
    return [(r[0], 1), (r[1], 1), (mp.mpc(2, A), 2), (mp.mpc(2, -A), 2)]


def rho_B(k):
    """Laurent radius from the B roots: max(a, a*sqrt|w|)."""
    k = mp.mpc(k)
    w = mp.polyroots([90 - 21 * k, -(60 - 18 * k), 10 - k])
    return max([A] + [A * mp.sqrt(abs(x)) for x in w])


def track_laurent(k_path, st):
    pr = None
    for k in k_path:
        pr = KC.ProblemC(KC.FK, k, E2)
        st = [(KC.newton(pr, x, w), w) for x, w in st]
    return pr, st


def find_extras(pr):
    """zeros of G1, G2 in rho+0.05 < |z| < 1.3*... by a coarse |G| grid + Newton (k < 0 only)."""
    out = []
    for which, idx in ((1, 0), (2, 2)):
        for sgn in (1, -1):
            x = mp.mpc(0, sgn) * (pr.rho + mp.mpf("0.1"))
            try:
                y = KC.newton(pr, x, which)
                if abs(y) > pr.rho + mp.mpf("0.02") and all(abs(y - e) > 1e-8 for e, _ in out):
                    out.append((y, which))
            except (RuntimeError, ZeroDivisionError):
                pass
    return out


def geo():
    res = dict(spin=SPIN)
    seeds = kerr_points()
    res["kerr_points"] = [mp.nstr(x, 10) for x, _ in seeds]
    # region A scan
    rho_max, outer_min, extra_max = mp.mpf(0), mp.mpf(99), mp.mpf(0)
    bad = []
    for jy in range(-4, 5):
        y = A_Y * jy / 4
        st = list(seeds)
        path = [mp.mpc(0, y * q / 4) for q in range(1, 5)] if jy else [mp.mpc(0)]
        try:
            pr, st = track_laurent(path, st)
        except RuntimeError as ex:
            bad.append((float(y), str(ex))); continue
        for direction in (1, -1):
            s2 = list(st)
            xs = [mp.mpf(q) / 8 for q in range(1, 33) if mp.mpf(q) / 8 < A_X1] + [A_X1] if direction == 1 else [-mp.mpf(q) / 8 for q in range(1, 5)]
            for x in xs:
                k = mp.mpc(x, y)
                try:
                    pr, s2 = track_laurent([k], s2)
                except RuntimeError as ex:
                    bad.append((mp.nstr(k, 5), str(ex)[:60])); break
                rho_max = max(rho_max, pr.rho)
                outer_min = min(outer_min, min(abs(p) for p, _ in s2))
                if x < 0:
                    ex_ = find_extras(pr)
                    if ex_:
                        extra_max = max(extra_max, max(abs(e) for e, _ in ex_))
    R0 = (max(rho_max, extra_max) + outer_min) / 2
    res["A"] = dict(rho_max=float(rho_max), extra_max=float(extra_max), outer_min=float(outer_min), R0=float(R0),
                    inner_margin=float(R0 - max(rho_max, extra_max)), outer_margin=float(outer_min - R0), errors=bad[:5])
    log("region A:", res["A"])
    # region B scan (hp engine). Rule (fixed before any F): series centre Z0 = Re(centroid of r+, p+- at the endpoint);
    # base point bB = Re(r+ at the endpoint) - 0.3, but >= a + 0.08; working disc = centroid, radius = max loop reach.
    st = [seeds[0], seeds[2], seeds[3]]
    for q in range(1, 43):
        k = B_X1 * q / 42
        pr = HP.ProblemHP(KC.FK, k, E2, z0=1.6 if A > 0.7 else None)
        st = [(KC.newton(pr, x, w), w) for x, w in st]
    endpts = list(st)
    cen0 = sum(x for x, _ in endpts) / 3
    Z0 = mp.re(cen0)
    bB = max(mp.re(endpts[0][0]) - mp.mpf("0.3"), A + mp.mpf("0.08"))
    res["endpoint_points"] = [mp.nstr(x, 10) for x, _ in endpts]
    res["B_rule"] = dict(Z0=float(Z0), bB=float(bB))
    worst = dict(Rc=99.0, ratio=0.0, sep=99.0, cut_ok=True, base_clear=99.0)
    for jy in range(-5, 6):
        y = B_Y * jy / 5
        s2 = list(endpts)
        for q in range(1, 6):
            pr = HP.ProblemHP(KC.FK, mp.mpc(B_X1, y * q / 5), E2, z0=Z0)
            s2 = [(KC.newton(pr, x, w), w) for x, w in s2]
        for q in range(0, 15):
            k = mp.mpc(B_X1 - (B_X1 - B_X0) * q / 14, y)
            pr = HP.ProblemHP(KC.FK, k, E2, z0=Z0)
            s2 = [(KC.newton(pr, x, w), w) for x, w in s2]
            rp, pp, pm = [x for x, _ in s2]
            cen = (rp + pp + pm) / 3
            md = max(abs(c - cen) for c in (rp, pp, pm))
            Rd = md + mp.mpf("0.15")
            reach_c = max(abs(cen - Z0) + Rd, abs(bB - Z0))
            span = max(abs(cen - cen0) + Rd, abs(bB - cen0)) + mp.mpf("0.05")
            worst["Rc"] = min(worst["Rc"], float(pr.eng.Rc))
            worst["ratio"] = max(worst["ratio"], float(reach_c / pr.eng.Rc))
            worst["sep"] = min(worst["sep"], float(KC.seg_dist(pm, rp, pp)))
            worst["base_clear"] = min(worst["base_clear"], float(min(abs(bB - e) for e in pr.eng.sing)))
            worst["cut_ok"] = worst["cut_ok"] and pr.eng.guard(cen0, span)["cut_ok"]
    res["B"] = worst
    log("region B:", worst, "rule", res["B_rule"], "endpoint points", res["endpoint_points"])
    json.dump(res, open(os.path.join(L.OUT, f"spin_geo_{TAG}.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    if sys.argv[1:] == ["geo"]:
        geo()


# ======================================================================================== run mode (registered)
from _nve_monodromy import comm, mul          # noqa: E402
from _ts_edge2 import fleet_guard              # noqa: E402

S_FIN = [2, -2, 1, -1, 0, mp.sqrt(2), -mp.sqrt(2), (mp.sqrt(5) - 1) / 2, -(mp.sqrt(5) - 1) / 2,
         (mp.sqrt(5) + 1) / 2, -(mp.sqrt(5) + 1) / 2]
PI4 = float(mp.pi / 4) + 1e-12
HI = A >= mp.mpf("0.85")
NC_B = 300 if HI else 220
RATIO_B = mp.mpf("0.7") if HI else mp.mpf("0.6")


def tr(M):
    return M[0][0] + M[1][1]


def count(vals):
    v = vals + vals[:1]
    tot = mp.fsum(mp.arg(b / a) for a, b in zip(v[:-1], v[1:]))
    mx = max(abs(mp.arg(b / a)) for a, b in zip(v[:-1], v[1:]))
    return int(mp.nint(tot / (2 * mp.pi))), float(tot / (2 * mp.pi)), float(mx)


def rect(x0, x1, y, h):
    c = [mp.mpc(x0, -y), mp.mpc(x1, -y), mp.mpc(x1, y), mp.mpc(x0, y), mp.mpc(x0, -y)]
    ks = [c[0]]
    for a_, b_ in zip(c[:-1], c[1:]):
        n = max(1, int(mp.ceil(abs(b_ - a_) / h)))
        ks += [a_ + (b_ - a_) * j / n for j in range(1, n + 1)]
    return ks[:-1]


def refine(samples, evalfn, levels=5, tag=""):
    for lev in range(levels):
        new, ins = [], 0
        for i in range(len(samples)):
            new.append(samples[i])
            a_, b_ = samples[i], samples[(i + 1) % len(samples)]
            if max(abs(mp.arg(b_[1][f] / a_[1][f])) for f in a_[1]) > mp.pi / 4:
                new.append(evalfn((a_[0] + b_[0]) / 2, a_[3])); ins += 1
        samples = new
        log(f"[{tag}] refinement {lev + 1}: +{ins} -> {len(samples)}")
        if ins == 0:
            break
    return samples


# ---- region A: circle picture (Laurent c0)
class LauA:
    def __init__(self, R0):
        self.R0 = mp.mpf(R0)
        self.M0 = L.arc(self.R0, 0, 2 * mp.pi)

    def problem(self, k):
        C, rho, NW = KC.c0_laurent_c(k)
        need = int(50 * mp.log(10) / mp.log((self.R0 - mp.mpf("0.05")) / rho)) + 20 if rho < self.R0 - mp.mpf("0.05") else None
        if need is None:
            raise RuntimeError(f"rho_c {rho} too close to R0 {self.R0}")
        pr = KC.ProblemC(KC.FK, k, E2)
        if need > pr.NW:
            pr.C, pr.rho, pr.NW = KC.c0_laurent_c(k, NW=need)
        return pr

    def state(self, k, st):
        pr = self.problem(k)
        outer = [(KC.newton(pr, x, w), w) for x, w in st[:4]]
        om = min(abs(x) for x, _ in outer)
        extras = [e for e in find_extras(pr) if abs(e[0]) < (self.R0 + om) / 2] if mp.re(k) < mp.mpf("0.05") else []
        return pr, outer, extras

    def loops(self, pr, outer, extras):
        rp, rm, pp, pm = [x for x, _ in outer]
        ex = [e for e, _ in extras]
        lasso, delta = KC.capsule_lasso(rp, pp, [rm, pm] + ex, b=self.R0)
        sep = KC.seg_dist(pm, rp, pp)
        g = dict(rho=float(pr.rho), outer_min=float(min(abs(x) for x in (rp, rm, pp, pm))),
                 extra_max=float(max([abs(e) for e in ex] + [0])), sep=float(sep),
                 lasso_pm=float(KC.path_dist(pm, lasso)),
                 lasso_other=float(min([KC.path_dist(c, lasso) for c in [rm] + ex])))
        g["ok"] = bool(g["outer_min"] >= self.R0 + 0.1 and g["extra_max"] <= self.R0 - 0.1 and g["rho"] <= self.R0 - 0.1
                       and g["lasso_pm"] >= 0.3 * g["sep"] and g["lasso_other"] >= 0.05)
        return lasso, g

    def evaluate(self, pr, outer, extras, lasso, step="0.35"):
        W = L.Walker(pr, [x for x, _ in outer] + [e for e, _ in extras], step)
        M0, M1 = W.walk(self.M0, KC.I2()), W.walk(lasso, KC.I2())
        return dict(F=tr(comm(M1, M0)) - 2, T0=tr(M0), T1=tr(M1))


def funcsA(r):
    d = {"F": r["F"], "T0m2": r["T0"] - 2, "T0": r["T0"], "T1": r["T1"]}
    for i, s in enumerate(S_FIN):
        d[f"T1-s{i}"] = r["T1"] - s
    return d


# ---- region B: half-plane picture (exact-radicand engine)
class HalfB:
    def __init__(self, Z0, bB, cen0, span):
        self.Z0, self.bB, self.cen0, self.span = mp.mpf(Z0), mp.mpf(bB), cen0, mp.mpf(span)

    def problem(self, k, NC=None):
        return HP.ProblemHP(KC.FK, k, E2, NC or NC_B, z0=self.Z0)

    def disc_lasso(self, center, R, n=96):
        left = center - R
        circ = [center + R * mp.expj(mp.pi + 2 * mp.pi * j / n) for j in range(n + 1)]
        return [mp.mpc(self.bB), left] + circ[1:] + [mp.mpc(self.bB)]

    def loops(self, pr, pos):
        rp, pp, pm = pos
        excl = list(pr.eng.sing)
        lasso, delta = KC.capsule_lasso(rp, pp, [pm], b=self.bB)
        sep = KC.seg_dist(pm, rp, pp)
        cen = (rp + pp + pm) / 3
        md = max(abs(c - cen) for c in pos)
        clear = min(abs(e - cen) for e in excl) - md
        R = md + min(mp.mpf("0.15"), mp.mpf("0.4") * clear)
        gam = self.disc_lasso(cen, R)
        pts = lasso + gam
        g = dict(sep=float(sep), lasso_pm=float(KC.path_dist(pm, lasso)),
                 lasso_excl=float(min(KC.path_dist(e, lasso) for e in excl)),
                 disc_excl=float(min(abs(e - cen) - R for e in excl)),
                 ratio=float(max(abs(p - self.Z0) for p in pts) / pr.eng.Rc),
                 cut_ok=pr.eng.guard(self.cen0, self.span)["cut_ok"],
                 contain=float(max(abs(p - self.cen0) for p in pts)))
        g["ok"] = bool(g["lasso_pm"] >= 0.3 * g["sep"] and g["lasso_excl"] >= 0.05 and g["disc_excl"] >= 0.05
                       and g["ratio"] <= float(RATIO_B) and g["cut_ok"] and g["contain"] <= float(self.span) - 0.04)
        return lasso, gam, g

    def evaluate(self, pr, pos, lasso, gam, step="0.35"):
        W = L.Walker(pr, list(pos) + list(pr.eng.sing), step)
        M1, Gm = W.walk(lasso, KC.I2()), W.walk(gam, KC.I2())
        return dict(F=tr(comm(M1, Gm)) - 2, T1=tr(M1), TG=tr(Gm), T1G=tr(mul(M1, Gm)))

    def wind_G(self, pr, which, rad):
        with mp.workdps(30):
            tot, prev = mp.mpf(0), None
            for j in range(1601):
                v = pr.G(self.cen0 + rad * mp.expj(2 * mp.pi * j / 1600))[0 if which == 1 else 2]
                if prev is not None:
                    tot += mp.arg(v / prev)
                prev = v
            return int(mp.nint(tot / (2 * mp.pi)))


def funcsB(r):
    d = {"F": r["F"], "T1": r["T1"], "TG": r["TG"], "T1G": r["T1G"]}
    for i, s in enumerate(S_FIN):
        d[f"T1-s{i}"] = r["T1"] - s
    return d


def classifyB(r, tol=mp.mpf("1e-12")):
    small = [abs(r[x]) < tol for x in ("T1", "TG", "T1G")]
    if abs(r["F"]) < tol:
        return "reducible?"
    if sum(small) >= 2:
        return "imprimitive (VA)"
    if min(abs(r["T1"] - s) for s in S_FIN) < mp.mpf("1e-3") and abs(mp.im(r["T1"])) < tol:
        return "finite?"
    return "non-VA"


def run():
    g = fleet_guard()
    if g:
        raise SystemExit(f"NOT STARTED: {g}")
    G = json.load(open(os.path.join(L.OUT, f"spin_geo_{TAG}.json")))
    V = dict(spin=SPIN, controls={}, guards={}, A={}, B={})
    seeds = kerr_points()
    RA = LauA(G["A"]["R0"])
    # ---------------- region A
    st = list(seeds)
    for k in [-A_X0 * 0 + A_X0 * q / 4 for q in range(1, 5)]:
        pr, st, ex = RA.state(k, st)
    pr, st, ex = RA.state(mp.mpc(A_X0, -A_Y / 2), st)
    pr, st, ex = RA.state(mp.mpc(A_X0, -A_Y), st)

    def evalA(k, s_):
        pr_, o_, ex_ = RA.state(k, s_)
        l_, gg = RA.loops(pr_, o_, ex_)
        r_ = RA.evaluate(pr_, o_, ex_, l_)
        return [k, funcsA(r_), gg["ok"], o_, gg, r_]
    ksA = rect(A_X0, A_X1, A_Y, mp.mpf("0.0625"))
    samples, s_ = [], st
    for k in ksA:
        smp = evalA(k, s_); samples.append(smp); s_ = smp[3]
    log(f"[A] {len(samples)} samples; geo fails {sum(not x[2] for x in samples)}")
    samples = refine(samples, evalA, tag="A")
    V["guards"]["A-geo"] = dict(ok=all(x[2] for x in samples), fails=[str(x[4]) for x in samples if not x[2]][:3])
    worst = 0.0
    for i in range(0, len(ksA), 6):
        smp = next(x for x in samples if x[0] == ksA[i])
        pr_, o_, ex_ = RA.state(smp[0], smp[3])
        l_, _ = RA.loops(pr_, o_, ex_)
        rs = [RA.evaluate(pr_, o_, ex_, l_, stp) for stp in ("0.35", "0.2", "0.12")]
        for x in ("F", "T0", "T1"):
            for a_, b_ in ((0, 1), (0, 2), (1, 2)):
                worst = max(worst, float(abs(rs[a_][x] - rs[b_][x]) / max(abs(rs[b_][x]), mp.mpf(10) ** -30)))
    V["guards"]["A-step"] = dict(worst_rel=worst, ok=worst <= 1e-15)
    CA = {f: count([x[1][f] for x in samples]) for f in samples[0][1]}
    V["A"]["counts"] = {f: c[0] for f, c in CA.items()}
    V["guards"]["A-arg"] = dict(ok=all(c[2] <= PI4 for c in CA.values()), max=max(c[2] for c in CA.values()))
    Fs = [x[1]["F"] for x in samples]
    kin = mp.mpc("2", "0.2")
    c2 = (count([f * (x[0] - kin) for f, x in zip(Fs, samples)])[0], count([f / (x[0] - kin) for f, x in zip(Fs, samples)])[0])
    V["controls"]["A-C2"] = dict(mul=c2[0], div=c2[1], ok=c2 == (CA["F"][0] + 1, CA["F"][0] - 1))
    log("[A] counts", V["A"]["counts"], "step", worst, "C2", V["controls"]["A-C2"])
    # A controls: Kerr F = 0 and C1 small circle
    pr0, o0, e0 = RA.state(mp.mpf(0), seeds)
    l0, _ = RA.loops(pr0, o0, e0)
    r0 = RA.evaluate(pr0, o0, e0, l0)
    V["controls"]["A-Kerr"] = dict(F=float(abs(r0["F"])), T0m2=float(abs(r0["T0"] - 2)), ok=bool(abs(r0["F"]) <= 1e-25 and abs(r0["T0"] - 2) <= 1e-25))
    c1s, s_ = [], seeds
    for j in range(16):
        smp = evalA(mp.mpf("0.3") * mp.expj(2 * mp.pi * j / 16), s_); c1s.append(smp); s_ = smp[3]
    c1s = refine(c1s, evalA, tag="C1")
    c1F, c1M = count([x[1]["F"] for x in c1s]), count([x[1]["T0m2"] for x in c1s])
    V["controls"]["A-C1"] = dict(F=c1F[0], T0m2=c1M[0], ok=c1F[0] == 2 and c1M[0] == 2)
    log("[A] Kerr", V["controls"]["A-Kerr"], "C1", V["controls"]["A-C1"])
    # ---------------- region B
    RB = HalfB(G["B_rule"]["Z0"], G["B_rule"]["bB"], 0, 0)
    stB = [seeds[0], seeds[2], seeds[3]]
    for q in range(1, 43):
        prb = RB.problem(B_X1 * q / 42)
        stB = [(KC.newton(prb, x, w), w) for x, w in stB]
    end_pts = [x for x, _ in stB]
    cen0 = sum(end_pts) / 3
    RB.cen0, RB.span = cen0, mp.mpf("0.05")
    # span: max loop reach from cen0 over the grid, +0.05 (computed below on the interior grid, then frozen)

    def evalB(k, s_, step="0.35"):
        prb = RB.problem(k)
        p_ = [KC.newton(prb, x, w) for x, w in s_]
        l_, g_, gg = RB.loops(prb, p_)
        r_ = RB.evaluate(prb, p_, l_, g_, step)
        return [k, funcsB(r_), gg["ok"], [(p, w) for p, (_, w) in zip(p_, s_)], gg, r_]
    # interior grid: compute span first (geometry only), then check all guards
    grid_states, spans = [], []
    for j in range(11):
        im = B_Y * (j - 5) / 5
        s2 = list(stB)
        for q in range(1, 6):
            prb = RB.problem(mp.mpc(B_X1, im * q / 5)); s2 = [(KC.newton(prb, x, w), w) for x, w in s2]
        for q in range(0, 15):
            k = mp.mpc(B_X1 - (B_X1 - B_X0) * q / 14, im)
            prb = RB.problem(k); s2 = [(KC.newton(prb, x, w), w) for x, w in s2]
            RB.span = mp.mpf(99)
            l_, g_, gg = RB.loops(prb, [x for x, _ in s2])
            spans.append(gg["contain"]); grid_states.append((k, list(s2)))
    RB.span = mp.mpf(max(spans)) + mp.mpf("0.05")
    fails, cnts = [], {}
    for k, s2 in grid_states:
        prb = RB.problem(k)
        l_, g_, gg = RB.loops(prb, [x for x, _ in s2])
        if not gg["ok"]:
            fails.append((mp.nstr(k, 6), gg))
    for k, s2 in [grid_states[0], grid_states[14], grid_states[-15], grid_states[-1], grid_states[5 * 15]]:
        prb = RB.problem(k)
        cnts[mp.nstr(k, 6)] = (RB.wind_G(prb, 1, RB.span), RB.wind_G(prb, 2, RB.span))
    V["guards"]["B-geo"] = dict(ok=not fails, span=float(RB.span), fails=[str(f) for f in fails[:3]])
    V["guards"]["B-count"] = dict(counts=cnts, ok=all(v == (1, 2) for v in cnts.values()))
    log("[B] span", float(RB.span), "geo fails", len(fails), "counts", cnts)
    # B controls
    worst_c, worst_t = 0.0, 0.0
    k_ov = A_X1
    for kk in (k_ov, mp.mpf(30) / 7):
        e, et = HP.C0Engine(kk, NC_B, z0=RB.Z0), HP.C0Engine(kk, 12, z0=RB.Z0)
        pts6 = [cen0 + mp.mpf("0.3") * mp.expj(2 * mp.pi * j / 6) for j in range(6)]
        rho_k = KC.c0_laurent_c(kk)[1]
        nw = int(60 * mp.log(10) / mp.log(min(abs(p) for p in pts6) / rho_k)) + 20
        Cl = KC.c0_laurent_c(kk, NW=nw)[0]
        for p in pts6:
            worst_c = max(worst_c, float(abs(e.c0(p) - L.c0_eval(Cl, p))), float(abs(e.c0(p, 1) - L.c0_eval(Cl, p, 1))))
            worst_t = max(worst_t, float(abs(et.c0(p) - L.c0_eval(Cl, p))))
    V["controls"]["B-repro"] = dict(worst=worst_c, ok=worst_c <= 1e-40)
    s_ = list(stB)
    for q in range(1, 13):
        prb = RB.problem(B_X1 - (B_X1 - k_ov) * q / 12); s_ = [(KC.newton(prb, x, w), w) for x, w in s_]
    smp = evalB(k_ov, s_)
    prb = RB.problem(k_ov); p_ = [x for x, _ in smp[3]]; l_, g_, _ = RB.loops(prb, p_)
    lau = KC.ProblemC(KC.FK, k_ov, E2)
    rmin_l = min(abs(p) for p in l_ + g_) - mp.mpf("0.02")
    lau.C, lau.rho, lau.NW = KC.c0_laurent_c(k_ov, NW=int(60 * mp.log(10) / mp.log(rmin_l / lau.rho)) + 20)
    pl = [KC.newton(lau, x, w) for x, w in smp[3]]
    W = L.Walker(lau, pl + list(prb.eng.sing), "0.35")
    M1, Gm = W.walk(l_, KC.I2()), W.walk(g_, KC.I2())
    dF = float(abs(tr(comm(M1, Gm)) - 2 - smp[5]["F"]))
    prt = RB.problem(k_ov, NC=12)
    rt = RB.evaluate(prt, p_, l_, g_)
    V["controls"]["B-repro-F"] = dict(diff=dF, ok=dF <= 1e-20)
    V["controls"]["B-MF-trunc"] = dict(c0=worst_t, F=float(abs(rt["F"] - smp[5]["F"])), ok=bool(worst_t >= 1e-30 and abs(rt["F"] - smp[5]["F"]) >= 1e-15))
    # P2 planted at k_ov: circle (region A machinery) and half-plane must both be non-VA
    prA, oA, eA = RA.state(k_ov, next(x for x in samples if abs(x[0] - k_ov) < 0.07)[3])
    lA, _ = RA.loops(prA, oA, eA)
    rA = RA.evaluate(prA, oA, eA, lA)
    circ_nonva = bool(all(abs(rA[x]) > 1e-8 for x in ("F", "T0", "T1")) and abs(mp.im(rA["T1"])) > 1e-8
                      and min(abs(rA["T1"] - s) for s in S_FIN) > 1e-3)
    V["controls"]["P2-planted"] = dict(k=float(k_ov), circle_nonVA=circ_nonva, halfplane=classifyB(smp[5]),
                                       ok=bool(circ_nonva and classifyB(smp[5]) == "non-VA"))
    # P1 Kerr imprimitive (half-plane, own centre)
    cK = (seeds[0][0] + seeds[2][0] + seeds[3][0]) / 3
    RK = HalfB(mp.re(cK), RB.bB, cK, mp.mpf(5))
    prk = RK.problem(mp.mpf(0))
    pk = [KC.newton(prk, x, w) for x, w in [seeds[0], seeds[2], seeds[3]]]
    lk, gk, _ = RK.loops(prk, pk)
    rk = RK.evaluate(prk, pk, lk, gk)
    V["controls"]["P1-Kerr-imprimitive"] = dict(TG=float(abs(rk["TG"])), T1G=float(abs(rk["T1G"])), cls=classifyB(rk),
                                                ok=bool(classifyB(rk) == "imprimitive (VA)"))
    log("[B] controls", {k_: V["controls"][k_] for k_ in ("B-repro", "B-repro-F", "B-MF-trunc", "P2-planted", "P1-Kerr-imprimitive")})
    # B boundary
    ksB = [mp.mpc(B_X1, 0)]
    cB = [mp.mpc(B_X1, 0), mp.mpc(B_X1, B_Y), mp.mpc(B_X0, B_Y), mp.mpc(B_X0, -B_Y), mp.mpc(B_X1, -B_Y), mp.mpc(B_X1, 0)]
    for a_, b_ in zip(cB[:-1], cB[1:]):
        n = max(1, int(mp.ceil(abs(b_ - a_) / mp.mpf("0.02"))))
        ksB += [a_ + (b_ - a_) * j / n for j in range(1, n + 1)]
    ksB = ksB[:-1]
    sB, s_ = [], list(stB)
    for k in ksB:
        smp = evalB(k, s_); sB.append(smp); s_ = smp[3]
    log(f"[B] {len(sB)} samples; geo fails {sum(not x[2] for x in sB)}")
    sB = refine(sB, evalB, tag="B")
    V["guards"]["B-geo-boundary"] = dict(ok=all(x[2] for x in sB))
    worst = 0.0
    for i in range(0, len(ksB), 4):
        smp = next(x for x in sB if x[0] == ksB[i])
        rs = [smp[5]] + [evalB(smp[0], smp[3], stp)[5] for stp in ("0.2", "0.12")]
        for x in ("F", "T1", "TG", "T1G"):
            for a_, b_ in ((0, 1), (0, 2), (1, 2)):
                worst = max(worst, float(abs(rs[a_][x] - rs[b_][x]) / max(abs(rs[b_][x]), mp.mpf(10) ** -30)))
    V["guards"]["B-step"] = dict(worst_rel=worst, ok=worst <= 1e-15)
    CB = {f: count([x[1][f] for x in sB]) for f in sB[0][1]}
    V["B"]["counts"] = {f: c[0] for f, c in CB.items()}
    V["guards"]["B-arg"] = dict(ok=all(c[2] <= PI4 for c in CB.values()), max=max(c[2] for c in CB.values()))
    Fs = [x[1]["F"] for x in sB]
    kin = (B_X0 + B_X1) / 2 + B_Y * mp.mpc(0, 0.4)
    c2 = (count([f * (x[0] - kin) for f, x in zip(Fs, sB)])[0], count([f / (x[0] - kin) for f, x in zip(Fs, sB)])[0])
    V["controls"]["B-C2"] = dict(mul=c2[0], div=c2[1], ok=c2 == (CB["F"][0] + 1, CB["F"][0] - 1))
    log("[B] counts", V["B"]["counts"], "step", worst, "C2", V["controls"]["B-C2"])
    sl = {}
    s_ = list(stB)
    for j in (13, 14, 15):
        smp = evalB(mp.mpf(30) / 7 - mp.mpf(10) ** (-j), s_)
        sl[f"30/7-1e-{j}"] = dict(F=mp.nstr(smp[5]["F"], 12), cls=classifyB(smp[5]))
    sme = evalB(mp.mpf(30) / 7, s_)
    sl["30/7"] = dict(F=mp.nstr(sme[5]["F"], 12), T1=mp.nstr(sme[5]["T1"], 12), cls=classifyB(sme[5]))
    V["sliver_and_endpoint"] = sl
    log("[B] sliver/endpoint", sl)
    # verdict
    ok = all(v["ok"] for v in V["controls"].values()) and all(v["ok"] for n, v in V["guards"].items() if not n.endswith("arg"))
    a_ok = CA["F"][0] == 2 and CA["T0"][0] == 0 and CA["T1"][0] == 0 and all(CA[f"T1-s{i}"][0] == 0 for i in range(11))
    b_ok = CB["F"][0] == 0 and CB["T1"][0] == 0 and (CB["TG"][0] == 0 or CB["T1G"][0] == 0) and all(CB[f"T1-s{i}"][0] == 0 for i in range(11))
    if not ok:
        V["verdict"] = "VOID"
    elif not (V["guards"]["A-arg"]["ok"] and V["guards"]["B-arg"]["ok"]):
        V["verdict"] = "UNDETERMINED (arg resolution)"
    elif a_ok and b_ok and sl["30/7"]["cls"] == "non-VA":
        V["verdict"] = "NO EXCEPTIONAL k IN (0, 30/7 - 1e-12] AND AT 30/7"
    else:
        V["verdict"] = f"EXCEPTIONAL CANDIDATES (A {V['A']['counts']}, B {V['B']['counts']})"
    json.dump(V, open(os.path.join(L.OUT, f"spin_run_{TAG}.json"), "w"), indent=1, default=str)
    log("VERDICT", SPIN, V["verdict"])


if __name__ == "__main__" and sys.argv[1:] == ["run"]:
    run()
