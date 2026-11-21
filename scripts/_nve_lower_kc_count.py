"""Gap B run (data/nve/GAPB_PREREGISTRATION.md): argument-principle zero count of F(k) = tr[M1, M0] - 2 over the
complex-k rectangle R = [-10.5, 4.05] x [-1, 1], spin 3/5, E = 4/5. Controls C0-C3, guards G-geo/G-count/G-step/G-arg.
    .venv/bin/python scripts/_nve_lower_kc_count.py        # resumable; F values cached in data/nve/gapb.jsonl
Output: data/nve/gapb.out (log), data/nve/gapb.jsonl (per-k cache), data/nve/gapb_verdict.json"""
import json
import os
import sys
import time

import mpmath as mp
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_lower as L                                                  # noqa: E402
import _nve_lower_kc as KC                                              # noqa: E402
from _ts_edge2 import fleet_guard                                       # noqa: E402

mp.mp.dps = 50
E2 = sp.Rational(16, 25)
OUT = L.OUT
CACHE = os.path.join(OUT, "gapb.jsonl")
NTOL = mp.mpf(10) ** -40
PI4 = float(mp.pi / 4) + 1e-12
X0, X1, Y = mp.mpf("-10.5"), mp.mpf("4.05"), mp.mpf(1)
REF_C0 = mp.mpc("0.00196656555091338", "0.00101256196325471")
# outer points at k = 0 (closed form: r = roots of Q at E = 4/5, p = 2 +- ia), extras seeds at k = -1 (measured)
K0_OUTER = [(mp.mpc("1.9344259"), 1), (mp.mpc("-3.4899815"), 1), (mp.mpc(2, "0.6"), 2), (mp.mpc(2, "-0.6"), 2)]
KM1_EXTRAS = [(mp.mpc("-0.0090093915", "0.66755508"), 1), (mp.mpc("-0.0090093915", "-0.66755508"), 1),
              (mp.mpc("-0.030425688", "0.65009665"), 2), (mp.mpc("-0.030425688", "-0.65009665"), 2)]


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------------------------------------- tracking
class State:
    def __init__(self, outer, extras, dropped):
        self.outer, self.extras, self.dropped = outer, extras, dropped


def track(k, st):
    pr = KC.ProblemC(KC.FK, k, E2)
    outer = [(KC.newton(pr, x, w, NTOL), w) for x, w in st.outer]
    lim = pr.rho + mp.mpf("0.05")
    extras, dropped = [], []
    for x, w in st.extras + st.dropped:
        seed = x if abs(x) > lim else (pr.rho + mp.mpf("0.08")) * x / abs(x)
        try:
            y = KC.newton(pr, seed, w, NTOL)
        except (RuntimeError, ZeroDivisionError):
            y = None
        if y is not None and abs(y) > lim and all(abs(y - e) > mp.mpf(10) ** -10 for e, _ in extras):
            extras.append((y, w))
        else:
            dropped.append((x if y is None else y, w))
    return pr, State(outer, extras, dropped)


def walk_to(ks, st):
    pr = None
    for k in ks:
        pr, st = track(k, st)
    return pr, st


def line(a, b, h):
    n = max(1, int(mp.ceil(abs(b - a) / h)))
    return [a + (b - a) * j / n for j in range(1, n + 1)]


def start_state(k_target):
    """continue from k = 0 to -1 (outer), add extras, then to k_target via -10.5 real or directly."""
    st = State(list(K0_OUTER), [], [])
    _, st = walk_to(line(mp.mpc(0), mp.mpc(-1), mp.mpf("0.25")), st)
    st.extras = list(KM1_EXTRAS)
    pr, st = track(mp.mpc(-1), st)
    return walk_to(line(mp.mpc(-1), k_target, mp.mpf("0.25")), st)


def geo(pr, st):
    (rp, _), (rm, _), (pp, _), (pm, _) = st.outer
    others = [rm, pm] + [e for e, _ in st.extras]
    lasso, delta = KC.capsule_lasso(rp, pp, others)
    lclr = min(KC.path_dist(c, lasso) for c in others)
    m0 = min(abs(x) for x, _ in st.outer) - mp.mpf("1.35")
    mx = max([abs(e) for e, _ in st.extras] + [mp.mpf(0)])
    ok = lclr >= mp.mpf("0.05") and m0 >= mp.mpf("0.2") and mx <= mp.mpf("1.25") and pr.rho <= mp.mpf("1.1")
    return dict(ok=bool(ok), lasso_clr=float(lclr), delta=float(delta), M0_clr=float(m0), extra_max=float(mx),
                rho=float(pr.rho), n_extras=len(st.extras)), lasso


def gcount(pr, n_extras):
    w = lambda f, R: L.winding(f, mp.mpf(R), N=2000)
    g1, g2 = (lambda x: pr.G(x)[0]), (lambda x: pr.G(x)[2])
    rin = pr.rho + mp.mpf("0.05")
    c = (w(g1, 60) - w(g1, "1.3"), w(g2, 60) - w(g2, "1.3"), w(g1, "1.3") - w(g1, rin), w(g2, "1.3") - w(g2, rin))
    return c, (c[0] == 2 and c[1] == 2 and c[2] + c[3] == n_extras)


# ---------------------------------------------------------------------------------------------- F evaluation (cached)
CACHED = {}
if os.path.exists(CACHE):
    for ln in open(CACHE):
        r = json.loads(ln)
        CACHED[(r["k"], r["step"])] = r


def key(k):
    return mp.nstr(mp.re(k), 20) + "," + mp.nstr(mp.im(k), 20)


def evalF(k, pr, st, step="0.35"):
    kk = key(k)
    if (kk, step) in CACHED:
        r = CACHED[(kk, step)]
        return mp.mpc(*r["F"]), mp.mpc(*r["T0"]), mp.mpc(*r["T1"]), r
    g, lasso = geo(pr, st)
    t0 = time.time()
    W = L.Walker(pr, [x for x, _ in st.outer] + [e for e, _ in st.extras], step)
    M0 = W.walk(KC.M0_PATH, KC.I2())
    M1 = W.walk(lasso, KC.I2())
    C = KC.comm(M1, M0)
    F, T0, T1 = C[0][0] + C[1][1] - 2, M0[0][0] + M0[1][1], M1[0][0] + M1[1][1]
    r = dict(k=kk, step=step, F=[mp.nstr(mp.re(F), 40), mp.nstr(mp.im(F), 40)],
             T0=[mp.nstr(mp.re(T0), 40), mp.nstr(mp.im(T0), 40)], T1=[mp.nstr(mp.re(T1), 40), mp.nstr(mp.im(T1), 40)],
             geo=g, pts=[mp.nstr(x, 12) for x, _ in st.outer], extras=[mp.nstr(e, 12) for e, _ in st.extras],
             sec=round(time.time() - t0, 1))
    with open(CACHE, "a") as fh:
        fh.write(json.dumps(r) + "\n")
    CACHED[(kk, step)] = r
    return F, T0, T1, r


def count(vals):
    v = vals + vals[:1]
    tot = mp.fsum(mp.arg(b / a) for a, b in zip(v[:-1], v[1:]))
    mx = max(abs(mp.arg(b / a)) for a, b in zip(v[:-1], v[1:]))
    return int(mp.nint(tot / (2 * mp.pi))), float(tot / (2 * mp.pi)), float(mx)


def contour_run(ks, st0, label, levels=5):
    """ks closed CCW list (first not repeated). Returns samples [(k, F, T0, T1)] after adaptive refinement."""
    samples = []
    st = st0
    states = []
    for k in ks:
        pr, st = track(k, st)
        F, T0, T1, r = evalF(k, pr, st)
        if not r["geo"]["ok"]:
            log(f"[{label}] G-geo FAIL at k={kk_s(k)}: {r['geo']}")
        samples.append([k, F, T0, T1, r["geo"]["ok"]])
        states.append(st)
    for lev in range(levels):
        new, newst, ins = [], [], 0
        n = len(samples)
        for i in range(n):
            new.append(samples[i]); newst.append(states[i])
            a, b = samples[i], samples[(i + 1) % n]
            fa, fb = [a[1], a[2] - 2, a[2], a[3]], [b[1], b[2] - 2, b[2], b[3]]
            if max(abs(mp.arg(y / x)) for x, y in zip(fa, fb)) > mp.pi / 4:
                km = (a[0] + b[0]) / 2
                pr, stm = track(km, states[i])
                F, T0, T1, r = evalF(km, pr, stm)
                new.append([km, F, T0, T1, r["geo"]["ok"]]); newst.append(stm)
                ins += 1
        samples, states = new, newst
        log(f"[{label}] refinement level {lev + 1}: inserted {ins}, now {len(samples)} samples")
        if ins == 0:
            break
    return samples, states


def kk_s(k):
    return f"{float(mp.re(k)):+.4f}{float(mp.im(k)):+.4f}i"


def rect_boundary(x0, x1, y, h=mp.mpf("0.25")):
    c = [mp.mpc(x0, -y), mp.mpc(x1, -y), mp.mpc(x1, y), mp.mpc(x0, y)]
    ks = [c[0]]
    for a, b in zip(c, c[1:] + c[:1]):
        ks += line(a, b, h)
    return ks[:-1]


# ---------------------------------------------------------------------------------------------- main
def main():
    g = fleet_guard()
    if g:
        raise SystemExit(f"NOT STARTED: {g}")
    V = dict(controls={}, guards={})
    # C0 reproduction
    pr, st = start_state(mp.mpc(0))
    pr, st = walk_to(line(mp.mpc(0), mp.mpf(1) / 10, mp.mpf("0.05")), st)
    F, T0, T1, r = evalF(mp.mpf(1) / 10, pr, st)
    d = abs(F - REF_C0)
    V["controls"]["C0"] = dict(F=r["F"], diff=float(d), ok=bool(d < 1e-15))
    log("C0", V["controls"]["C0"])
    # C3 must-fail guards (geometry only)
    for name, ks, st_k in (("C3a", line(X0, mp.mpc(-25), mp.mpf("0.25")), X0), ("C3b", line(X1, mp.mpc("4.2"), mp.mpf("0.025")), X1)):
        prs, sts = start_state(mp.mpc(st_k)) if name == "C3a" else walk_to(line(mp.mpc(0), mp.mpc(X1), mp.mpf("0.25")), start_state(mp.mpc(0))[1])
        fired, where = False, None
        for k in ks:
            try:
                prs, sts = track(k, sts)
                gg, _ = geo(prs, sts)
                if not gg["ok"]:
                    fired, where = True, (kk_s(k), gg)
                    break
            except RuntimeError as ex:
                fired, where = True, (kk_s(k), str(ex))
                break
        V["controls"][name] = dict(fired=fired, where=str(where), ok=fired)
        log(name, V["controls"][name])
    # G-geo interior grid + G-count
    geo_fail, cnt_fail, cnts = [], [], {}
    count_pts = (0.0, 4.0, -5.0, -10.0)
    for j in range(9):
        im = -Y + mp.mpf("0.25") * j
        pr, st = start_state(mp.mpc(X0, im))
        xs = [X0 + mp.mpf("0.5") * i for i in range(int((X1 - X0) / mp.mpf("0.5")) + 1)] + [X1]
        prev = X0
        for x in xs:
            pr, st = walk_to(line(mp.mpc(prev, im), mp.mpc(x, im), mp.mpf("0.25")) if x != prev else [mp.mpc(x, im)], st)
            prev = x
            gg, _ = geo(pr, st)
            if not gg["ok"]:
                geo_fail.append((kk_s(mp.mpc(x, im)), gg))
            xf = float(x)
            if (abs(im) == Y and xf in (float(X0), float(X1), -3.5)) or (im == 0 and xf in (float(X0), float(X1)) + count_pts):
                mp.mp.dps = 30
                c, okc = gcount(pr, gg["n_extras"])
                mp.mp.dps = 50
                cnts[kk_s(mp.mpc(x, im))] = (c, okc)
                if not okc:
                    cnt_fail.append((kk_s(mp.mpc(x, im)), c, gg["n_extras"]))
                log("G-count", kk_s(mp.mpc(x, im)), c, "extras", gg["n_extras"], "ok" if okc else "FAIL")
        log(f"G-geo row Im k={float(im):+.2f} done; fails so far {len(geo_fail)}")
    V["guards"]["G-geo"] = dict(ok=not geo_fail, fails=[str(f) for f in geo_fail[:10]])
    V["guards"]["G-count"] = dict(ok=not cnt_fail, counts={k: str(v) for k, v in cnts.items()})
    log("G-geo", V["guards"]["G-geo"]["ok"], "G-count", V["guards"]["G-count"]["ok"])
    # C1 local count
    ks1 = [mp.mpf("0.3") * mp.expj(2 * mp.pi * j / 16) for j in range(16)]
    pr, st = start_state(ks1[0])
    s1, _ = contour_run(ks1, st, "C1")
    cF, cM = count([s[1] for s in s1]), count([s[2] - 2 for s in s1])
    V["controls"]["C1"] = dict(countF=cF, count_trM0m2=cM, ok=cF[0] == 2 and cM[0] == 2 and cF[2] <= PI4 and cM[2] <= PI4)
    log("C1", V["controls"]["C1"])
    # boundary of R
    ksR = rect_boundary(X0, X1, Y)
    pr, st = start_state(ksR[0])
    sR, stR = contour_run(ksR, st, "R")
    V["guards"]["G-geo-boundary"] = dict(ok=all(s[4] for s in sR))
    # G-step at every 4th original sample
    worst = 0.0
    for i in range(0, len(ksR), 4):
        k = ksR[i]
        j = next(n for n, s in enumerate(sR) if s[0] == k)
        prk = KC.ProblemC(KC.FK, k, E2)
        F2, T02, T12, _ = evalF(k, prk, stR[j], "0.2")
        for a, b in ((sR[j][1], F2), (sR[j][2], T02), (sR[j][3], T12)):
            worst = max(worst, float(abs(a - b) / max(abs(a), mp.mpf(10) ** -30)))
    V["guards"]["G-step"] = dict(worst_rel=worst, ok=worst <= 1e-15)
    log("G-step", V["guards"]["G-step"])
    res = {}
    for nm, vals in (("F", [s[1] for s in sR]), ("trM0m2", [s[2] - 2 for s in sR]), ("T0", [s[2] for s in sR]), ("T1", [s[3] for s in sR])):
        res[nm] = count(vals)
    V["counts"] = {k: dict(count=v[0], raw=v[1], max_darg=v[2]) for k, v in res.items()}
    V["guards"]["G-arg"] = dict(ok=all(v[2] <= PI4 for v in res.values()))
    log("counts", V["counts"])
    # C2 counter must-detect
    Fs = [s[1] for s in sR]
    ks_in, ks_out = mp.mpc(-3, "0.5"), mp.mpc(6, 3)
    c_mul = count([f * (s[0] - ks_in) for f, s in zip(Fs, sR)])[0]
    c_div = count([f / (s[0] - ks_in) for f, s in zip(Fs, sR)])[0]
    c_out = count([f * (s[0] - ks_out) for f, s in zip(Fs, sR)])[0]
    V["controls"]["C2"] = dict(mul=c_mul, div=c_div, out=c_out, ok=(c_mul == res["F"][0] + 1 and c_div == res["F"][0] - 1 and c_out == res["F"][0]))
    log("C2", V["controls"]["C2"])
    # real-axis evidence for the finite case: Im T1 at the real-k samples of R? (R's boundary has no real points) -> record at |k| circle
    V["ImT1_real_k"] = {kk_s(s[0]): float(mp.im(s[3])) for s in s1 + sR if mp.im(s[0]) == 0}
    ctl_ok = all(v["ok"] for v in V["controls"].values())
    gd_ok = all(v["ok"] for n, v in V["guards"].items() if n != "G-arg")
    if not (ctl_ok and gd_ok):
        V["verdict"] = "VOID"
    elif not V["guards"]["G-arg"]["ok"]:
        V["verdict"] = "UNDETERMINED"
    elif res["F"][0] == 2:
        V["verdict"] = "NO SPECIAL k IN R"
    else:
        V["verdict"] = f"SPECIAL k FOUND (count {res['F'][0]})"
    V["nonimprimitive_in_R"] = res["T0"][0] == 0 and res["T1"][0] == 0
    json.dump(V, open(os.path.join(OUT, "gapb_verdict.json"), "w"), indent=1, default=str)
    log("VERDICT", V["verdict"], "| T0/T1 zero-free in R:", V["nonimprimitive_in_R"])


if __name__ == "__main__":
    main()
