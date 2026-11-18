#!/usr/bin/env python3
"""Edge-link tests (data/ts_chaos/EDGE_LINK_PREREGISTRATION.md): is the TS capture edge on the start line the stable
manifold of the §154 orbit gamma? Built on _ts_tangle.py (fixed point, eigenvectors, branch parametrisation) and
_hp_dd.py (DD RHS, GBS step), both imported unchanged.

    .venv/bin/python scripts/_ts_edge.py gate                 # engine gate (Kerr and TS vs the §154 section routine)
    .venv/bin/python scripts/_ts_edge.py tl3 <kerr|ts> [R2|R1] # T-L3 census
"""
import json
import math
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpmath as mp  # noqa: E402
import numba  # noqa: E402
import numpy as np  # noqa: E402

import _ts_tangle as TT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "ts_chaos", "edge")
TANG = os.path.join(ROOT, "data", "ts_chaos", "tangle")
mp.mp.dps = 40
XFAR = {"ts": 30.0, "kerr": 15.0}


# ======================================================================================== section routine variant
def make_secmap2(eng):
    """As _ts_tangle.make_secmap, plus: plunge cut xpl as an argument, the largest x since the start, and an option to
    stop at the first DOWNWARD crossing (half-return map). Crossings located exactly by Newton on the step length."""
    from _hp_ddprim import dd_add, dd_div, dd_mul, dd_sqrt, dd_sub
    f = eng.f
    gbs = eng._run.gbs_step

    @numba.njit
    def secmap2(xh, xl, pxh, pxl, Eh, El, Lh, Ll, tol, k, hmax, xpl, xmax, maxsteps, down):
        sh = np.zeros(4); sl = np.zeros(4)
        sh[0], sl[0] = xh, xl
        sh[2], sl[2] = pxh, pxl
        v = f(xh, xl, 0.0, 0.0, Eh, El, Lh, Ll)
        a = dd_mul(v[0], v[1], pxh, pxl); a = dd_mul(a[0], a[1], pxh, pxl)
        num = dd_sub(-1.0, 0.0, v[16], v[17]); num = dd_sub(num[0], num[1], a[0], a[1])
        if num[0] <= 0.0:
            return -1, sh, sl, xh
        q = dd_div(num[0], num[1], v[2], v[3])
        sh[3], sl[3] = dd_sqrt(q[0], q[1])
        h = 0.05
        seen_neg = False
        expo = 1.0 / (2 * k - 1)
        maxx = xh
        for _ in range(maxsteps):
            if h > hmax:
                h = hmax
            nh, nl, err = gbs(sh, sl, h, 0.0, k, Eh, El, Lh, Ll)
            e = 0.0
            for i in range(4):
                w = abs(err[i]) / (tol * (1.0 + max(abs(sh[i]), abs(nh[i]))))
                if not (w == w):
                    e = 1e300
                elif w > e:
                    e = w
            if e <= 1.0:
                up = seen_neg and sh[1] < 0.0 <= nh[1] and nh[3] > 0.0
                dn = down and sh[1] > 0.0 >= nh[1] and nh[3] < 0.0
                if up or dn:
                    y0 = sh[1]; y1 = nh[1]
                    hh = h * (-y0) / (y1 - y0); hl = 0.0
                    zh, zl = nh, nl
                    for _ in range(8):
                        zh, zl, _e = gbs(sh, sl, hh, hl, k, Eh, El, Lh, Ll)
                        w = f(zh[0], zl[0], zh[1], zl[1], Eh, El, Lh, Ll)
                        yd = dd_mul(w[2], w[3], zh[3], zl[3])
                        corr = dd_div(-zh[1], -zl[1], yd[0], yd[1])
                        r = dd_add(hh, hl, corr[0], corr[1])
                        hh, hl = r[0], r[1]
                        if abs(corr[0]) < 1e-33 * (1.0 + abs(hh)):
                            break
                    zh, zl, _e = gbs(sh, sl, hh, hl, k, Eh, El, Lh, Ll)
                    if zh[0] > maxx:
                        maxx = zh[0]
                    return 0, zh, zl, maxx
                if nh[1] < 0.0:
                    seen_neg = True
                sh, sl = nh, nl
                if sh[0] > maxx:
                    maxx = sh[0]
                if sh[0] < xpl:
                    return 1, sh, sl, maxx
                if sh[0] > xmax or abs(sh[1]) > 0.999999:
                    return 2, sh, sl, maxx
            fac = 0.94 * (1.0 / e) ** expo if e > 0.0 else 4.0
            h *= min(4.0, max(0.2, fac))
        return 3, sh, sl, maxx
    return secmap2


class EdgeMap:
    def __init__(self, sys_, rung="R2", xpl=1.5):
        import _hp_dd as H
        self.sys = sys_
        self.lv = TT.LEV[sys_]
        self.eng = H.DDEngine(self.lv["spec"])
        self.sm = make_secmap2(self.eng)
        self.E = tuple(float(c) for c in H.dd_const(self.lv["E"]))
        self.L = tuple(float(c) for c in H.dd_const(self.lv["L"]))
        self.tol = TT.TOL[rung]
        self.xpl = xpl
        self.calls = 0

    def step(self, z, down=False):
        """-> (status, z_next or None, maxx). status 0 = a crossing was reached."""
        xh, xl = TT.dd_of(z[0]); ph, pl = TT.dd_of(z[1])
        st, sh, sl, mx = self.sm(xh, xl, ph, pl, self.E[0], self.E[1], self.L[0], self.L[1], self.tol, 12, 2.0,
                                 self.xpl, 2000.0, 5_000_000, down)
        self.calls += 1
        if st != 0:
            return int(st), None, float(mx)
        return 0, [mp.mpf(sh[0]) + sl[0], mp.mpf(sh[2]) + sl[2]], float(mx)

    def P(self, z):
        st, zn, _ = self.step(z)
        return zn if st == 0 else None

    def orbit(self, z0, N):
        """Up to N crossings. -> dict(pts=[(x, px, maxx_leg)], status_end, n). n = crossings completed."""
        z = z0
        pts = []
        for _ in range(N):
            st, zn, mx = self.step(z)
            if st != 0:
                return dict(pts=pts, end=st, n=len(pts), lastmax=mx)
            pts.append((float(zn[0]), float(zn[1]), mx))
            z = zn
        return dict(pts=pts, end=0, n=len(pts), lastmax=None)


def stored(sys_):
    r = json.load(open(os.path.join(TANG, f"{sys_}_R2_d1e-12.json")))
    return mp.mpf(r["fixed"][0]), mp.mpf(r["lam"]), mp.mpf(r["branches"]["1"]["cross"][0]), r


def fixed_and_frame(M, sys_):
    xs, lam_st, xh, _ = stored(sys_)
    zs, J, res = TT.fixed_point(M.P, [xs, mp.mpf(0)], mp.mpf("1e-12"), mp.mpf("1e-27"))
    lu, ls, vu, vs, det = TT.eig2(J)
    if vu[0] < 0:
        vu = [-vu[0], -vu[1]]
    vs = [vu[0], -vu[1]]                       # R(v_u): the stable direction by reversibility
    return zs, lu, vu, vs, res, det


# ======================================================================================== engine gate
def gate():
    out = {}
    for s_ in ("kerr", "ts"):
        t0 = time.time()
        M = EdgeMap(s_)
        old = TT.TSMap(s_, "R2")
        xs, lam_st, xh, _ = stored(s_)
        zs, lu, vu, vs, res, det = fixed_and_frame(M, s_)
        zo, Jo, reso = TT.fixed_point(old, [xs, mp.mpf(0)], mp.mpf("1e-12"), mp.mpf("1e-27"))
        luo = TT.eig2(Jo)[0]
        # one-step agreement of the two routines at a generic point
        zt = [zs[0] + mp.mpf("0.05"), mp.mpf("0.01")]
        a, b = M.P(zt), old(zt)
        rec = dict(x_new_vs_stored=float(abs(zs[0] - xs) / xs), x_new_vs_old=float(abs(zs[0] - zo[0]) / zo[0]),
                   lam_new_vs_old=float(abs(lu - luo) / luo), lam_new_vs_stored_double=float(abs(lu - lam_st) / lam_st),
                   step_agree=float(max(abs(a[0] - b[0]), abs(a[1] - b[1]))), residual=float(res), sec=time.time() - t0)
        rec["pass"] = (rec["x_new_vs_stored"] <= 1e-20 and rec["x_new_vs_old"] <= 1e-20 and rec["lam_new_vs_old"] <= 1e-20
                       and rec["step_agree"] <= 1e-25)
        out[s_] = rec
        if s_ == "kerr":
            print(f"[kerr] {rec}", flush=True)
        else:
            print(f"[ts] engine gate {'PASS' if rec['pass'] else 'FAIL'} (values in file)", flush=True)
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "engine_gate.json"), "w"), indent=1)
    print("VERDICT-engine-gate:", "PASS" if all(v["pass"] for v in out.values()) else "FAIL", flush=True)


# ======================================================================================== T-L3
def trace_U(M, zs, vu, lu, uh, delta=mp.mpf("1e-12")):
    """W^u_out samples from z* to h: 400 per fundamental domain, 3200 on the last two. -> sorted [(u, x, px)]."""
    kh = int(mp.floor(uh))
    pts = []
    for J, rows in ((400, range(0, kh + 1)), (3200, (kh - 1, kh))):
        rows = set(rows)
        zrow = [[zs[0] + delta * lu ** (mp.mpf(j) / J) * vu[0], zs[1] + delta * lu ** (mp.mpf(j) / J) * vu[1]]
                for j in range(J)]
        for k in range(kh + 1):
            for j, z in enumerate(zrow):
                u = k + mp.mpf(j) / J
                if z is not None and u < uh and k in rows:
                    pts.append((float(u), z[0], z[1]))
            if k < kh:
                zrow = [M.P(z) if z is not None else None for z in zrow]
    pts.sort(key=lambda t: t[0])
    return pts


def polygon(zs, U, xh):
    up = [(float(zs[0]), 0.0)] + [(float(x), float(p)) for _, x, p in U] + [(float(xh), 0.0)]
    return np.array(up + [(x, -p) for x, p in reversed(up[1:-1])])


def inside(poly, x, p):
    xs, ps = poly[:, 0], poly[:, 1]
    xs2, ps2 = np.roll(xs, -1), np.roll(ps, -1)
    c = ((ps > p) != (ps2 > p)) & (x < (xs2 - xs) * (p - ps) / (ps2 - ps + 1e-300) + xs)
    return bool(np.count_nonzero(c) % 2)


def dist(poly, x, p):
    a = poly; b = np.roll(poly, -1, axis=0)
    d = b - a
    t = np.clip(((x - a[:, 0]) * d[:, 0] + (p - a[:, 1]) * d[:, 1]) / (d[:, 0] ** 2 + d[:, 1] ** 2 + 1e-300), 0, 1)
    return float(np.min(np.hypot(a[:, 0] + t * d[:, 0] - x, a[:, 1] + t * d[:, 1] - p)))


AMB = 1e-3 * math.sqrt(2)          # Euclidean superset of "max-norm distance < 1e-3" (conservative)


def classify(poly, x, p):
    if dist(poly, x, p) < AMB:
        return "amb"
    return "in" if inside(poly, x, p) else "out"


def tl3(sys_, rung):
    t0 = time.time()
    M = EdgeMap(sys_, rung)
    xs_st, lam_st, xh, rec154 = stored(sys_)
    uh = mp.mpf(rec154["branches"]["1"]["u"])
    zs, lu, vu, vs, res, det = fixed_and_frame(M, sys_)
    xs = zs[0]
    U = trace_U(M, zs, vu, lu, uh)
    sg = [mp.sign(p) for _, _, p in U]
    fb = dict(n=len(U), one_sign=len(set(sg)) == 1, min_abs_px=float(min(abs(p) for _, _, p in U)),
              min_abs_px_last_domain=float(min(abs(p) for u, _, p in U if u > float(uh) - 1)))
    poly = polygon(zs, U, xh)
    cen = poly.mean(axis=0)
    poly_s = cen + 0.5 * (poly - cen)
    t_trace = time.time() - t0
    a, b = float(vu[0]), float(vu[1])
    lamf = float(lu)
    A = [xs + mp.mpf(0.14) * lu ** (-mp.mpf(j) / 96) for j in range(373)]
    A += [xh - mp.mpf(10) ** (-(1 + mp.mpf(i) * 6 / 100)) for i in range(101)]
    Bx = []
    for i in range(31):
        for j in range(31):
            x = float(xs) + -0.3 + 0.6 * i / 30
            p = (-0.3 + 0.6 * j / 30) * abs(b / a)
            if inside(poly, x, p):
                Bx.append((mp.mpf(x), mp.mpf(p)))
    C = [xh + mp.mpf(10) ** (-(1 + mp.mpf(i) * 6 / 100)) for i in range(101)]
    samples = [("a", [x, mp.mpf(0)]) for x in A] + [("b", list(z)) for z in Bx] + [("c", [x, mp.mpf(0)]) for x in C]
    cnt = dict(C0=0, exits=0, C1=0, C2=0, C3=0, C4=0, C5=0, mf_C4=0, mf_C1=0, amb_crossings=0, orbits=0)
    det_ = []
    for grp, z0 in samples:
        o = M.orbit(z0, 60)
        pts = o["pts"]
        cnt["orbits"] += 1
        if grp in "ab" and o["n"] == 0:
            cnt["C0"] += 1
        exit_i = None
        if grp in "ab":
            for i, (x, p, _) in enumerate(pts):
                c = classify(poly, x, p)
                cnt["amb_crossings"] += c == "amb"
                if c == "out":
                    exit_i = i
                    break
            if exit_i is not None:
                cnt["exits"] += 1
                need = exit_i + 1 + 40
                if o["end"] == 0 and o["n"] < need:          # extend to decide C2 (implementation choice, logged)
                    z = [mp.mpf(pts[-1][0]), mp.mpf(pts[-1][1])]
                    o2 = M.orbit(z, need - o["n"])
                    pts = pts + o2["pts"]; o = dict(o, end=o2["end"], n=len(pts))
                if any(classify(poly, x, p) == "in" for x, p, _ in pts[exit_i + 1:]):
                    cnt["C1"] += 1
                    det_.append(dict(kind="C1", grp=grp, z0=[float(z0[0]), float(z0[1])]))
                if not (o["end"] == 1 and o["n"] <= need):
                    cnt["C2"] += 1
                    det_.append(dict(kind="C2", grp=grp, z0=[float(z0[0]), float(z0[1])], end=o["end"], n=o["n"]))
        if o["end"] not in (0, 1):
            cnt["C3"] += 1
            det_.append(dict(kind="C3", grp=grp, z0=[float(z0[0]), float(z0[1])], end=o["end"], n=o["n"]))
        xsf = float(xs)
        xsx = [x for x, _, _ in pts]
        lo = [i for i, x in enumerate(xsx) if x < 0.9 * xsf]
        if lo and any(x > xsf for x in xsx[lo[0] + 1:]):
            cnt["C4"] += 1
            det_.append(dict(kind="C4", grp=grp, z0=[float(z0[0]), float(z0[1])]))
        lo2 = [i for i, x in enumerate(xsx) if x < 2 * xsf]
        if lo2 and any(x > 2.5 * xsf for x in xsx[lo2[0] + 1:]):
            cnt["mf_C4"] += 1
        if grp == "c" and not (o["end"] == 1 and o["n"] <= 40):
            cnt["C5"] += 1
            det_.append(dict(kind="C5", z0=float(z0[0]), end=o["end"], n=o["n"]))
        if grp in "ab":
            left = False
            for x, p, _ in pts:
                ins = inside(poly_s, x, p) and dist(poly_s, x, p) >= AMB
                outs = (not inside(poly_s, x, p)) and dist(poly_s, x, p) >= AMB
                if outs:
                    left = True
                elif left and ins:
                    cnt["mf_C1"] += 1
                    break
    t_orb = time.time() - t0 - t_trace
    a2 = []
    for j in range(64):
        f = mp.mpf(j) / 64
        s = mp.mpf("1e-6") * lu ** f
        o = M.orbit([zs[0] - s * vu[0], zs[1] - s * vu[1]], 40)
        a2.append(o["end"])
    st, zH, _ = M.step(zs, down=True)
    brake = dict(status=st, dx=float(abs(zH[0] - zs[0])) if zH else None, dpx=float(abs(zH[1])) if zH else None)
    out = dict(sys=sys_, rung=rung, Fb=fb, counts=cnt, A2_status=a2, A2_all_plunge=all(e == 1 for e in a2),
               brake=brake, n_samples=dict(a=len(A), b=len(Bx), c=len(C)), details=det_[:200],
               map_calls=M.calls, sec_trace=t_trace, sec_orbits=t_orb, sec=time.time() - t0)
    return out


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "gate":
        gate()
    if mode == "tl3":
        s_ = sys.argv[2]; rung = sys.argv[3] if len(sys.argv) > 3 else "R2"
        os.makedirs(OUT, exist_ok=True)
        out = tl3(s_, rung)
        fn = os.path.join(OUT, f"tl3_{s_}_{rung}.json")
        json.dump(out, open(fn, "w"), indent=1, default=str)
        if s_ == "kerr":
            print(json.dumps({k: v for k, v in out.items() if k != "details"}, indent=1, default=str), flush=True)
        print(f"[{s_}] T-L3 done -> {fn}  [{out['sec']:.0f}s, {out['map_calls']} map calls]", flush=True)
