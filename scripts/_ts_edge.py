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

    xc = None                                  # addendum 2: optional SECTION cut (plunge at a crossing with x < xc)

    def step(self, z, down=False):
        """-> (status, z_next or None, maxx). status 0 = a crossing was reached."""
        if self.xc is not None and not down:
            st, zn, mx = self._step(z, down)
            if st == 0 and zn[0] < self.xc:
                return 1, None, mx
            return st, zn, mx
        return self._step(z, down)

    def _step(self, z, down=False):
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
    Mpts = [xs + mp.mpf("0.2") + (xh - xs - mp.mpf("0.4")) * i / 59 for i in range(60)]    # addendum 1: group (m)
    samples = [("a", [x, mp.mpf(0)]) for x in A] + [("a", [x, mp.mpf(0)]) for x in Mpts] + [("b", list(z)) for z in Bx] + [("c", [x, mp.mpf(0)]) for x in C]
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
               brake=brake, n_samples=dict(a=len(A), m=len(Mpts), b=len(Bx), c=len(C)), details=det_[:200],
               map_calls=M.calls, sec_trace=t_trace, sec_orbits=t_orb, sec=time.time() - t0)
    return out


# ======================================================================================== frame, fates, certificate
class Frame:
    def __init__(self, zs, vu, vs):
        self.zs = zs
        a, b = vu; c, d = vs
        det = a * d - b * c
        self.inv = (d / det, -c / det, -b / det, a / det)

    def us(self, z):
        dx, dp = z[0] - self.zs[0], z[1] - self.zs[1]
        i = self.inv
        return i[0] * dx + i[1] * dp, i[2] * dx + i[3] * dp

    def rho(self, z):
        u, s_ = self.us(z)
        return max(abs(u), abs(s_))


def fate(M, z0, xfar, cap=60):
    """T = plunges after exactly one excursion; B = starts a second excursion; X = anything else."""
    z = z0
    exc = 0
    for _ in range(cap):
        st, zn, mx = M.step(z)
        if mx > xfar:
            exc += 1
            if exc >= 2:
                return "B"
        if st != 0:
            return "T" if (st == 1 and exc == 1) else "X"
        z = zn
    return "X"


def certificate(Ms, F, xfar, p, q, kmax=80):
    """Straddle certificate for (p, q) on the start line, p the plunging member. Ms = [M_R2, M_R1]. -> (ok, info)."""
    ks = []
    for M in Ms:
        segs = [[p[0] + (q[0] - p[0]) * i / 8, p[1] + (q[1] - p[1]) * i / 8] for i in range(9)]
        k_ok = None
        for j in range(1, kmax + 1):
            segs = [M.P(z) if z is not None else None for z in segs]
            if any(z is None for z in segs):
                break
            spread = max(max(z[c] for z in segs) - min(z[c] for z in segs) for c in (0, 1))
            if spread > mp.mpf("1e-6"):
                break
            if F.rho(segs[0]) <= mp.mpf("1e-2") and F.rho(segs[-1]) <= mp.mpf("1e-2"):
                k_ok = j
                break
        if k_ok is None:
            return False, dict(reason="no short close approach", rung=len(ks))
        zp, zq = segs[0], segs[-1]
        sides = []
        for z, want in ((zp, -1), (zq, 1)):
            u = None
            exc_after = 0
            end = None
            for _ in range(kmax):
                st, zn, mx = M.step(z)
                if u is None and (st != 0 or F.rho(zn) > mp.mpf("1e-2")):
                    u = F.us(z if st != 0 else zn)[0]
                    exc_after = 0
                if u is not None and mx > xfar:
                    exc_after += 1
                if st != 0:
                    end = st
                    break
                z = zn
                if u is not None and exc_after >= 1 and want == 1:
                    break
            sides.append((mp.sign(u) if u is not None else 0, exc_after, end))
        okp = sides[0][0] == -1 and sides[0][2] == 1 and sides[0][1] == 0
        okq = sides[1][0] == 1 and sides[1][1] >= 1
        if not (okp and okq):
            return False, dict(reason="exits not opposite", rung=len(ks), sides=[(int(a), b, c) for a, b, c in sides])
        ks.append(k_ok)
    if ks[0] != ks[1]:
        return False, dict(reason="R1/R2 k differ", ks=ks)
    return True, dict(k=ks[0])


def tbands(sys_):
    t0 = time.time()
    M = EdgeMap(sys_, "R2")
    M1 = EdgeMap(sys_, "R1")
    xs_st, lam_st, xh, _ = stored(sys_)
    zs, lu, vu, vs, res, det = fixed_and_frame(M, sys_)
    F = Frame(zs, vu, vs)
    xfar = XFAR[sys_]
    ds = [mp.mpf("0.14") * lu ** (-mp.mpf(j) / 96) for j in range(373)]
    fates = [fate(M, [zs[0] + d, mp.mpf(0)], xfar) for d in ds]
    t_grid = time.time() - t0
    deep = list(range(70, 373))
    fd = [fates[j] for j in deep]
    tfrac = sum(f == "T" for f in fd) / len(fd)
    xfrac = sum(f == "X" for f in fates) / len(fates)
    A = {}
    for tau in range(60, 141):
        pairs = [(fates[j], fates[j + tau]) for j in deep if j + tau < 373]
        A[tau] = sum(a == b for a, b in pairs) / len(pairs) if pairs else None
    best = max((t for t in A if A[t] is not None), key=lambda t: A[t])
    # edges in the two deepest full periods
    lo_j = 373 - 192
    ch = [j for j in range(lo_j, 372) if fates[j] != fates[j + 1] and {fates[j], fates[j + 1]} == {"T", "B"}][:8]
    edges = []
    for j in ch:
        a, b = ds[j], ds[j + 1]                    # a > b
        fa = fates[j]
        while abs(a - b) > mp.mpf("1e-10") * abs(b):
            m = (a + b) / 2
            if fate(M, [zs[0] + m, mp.mpf(0)], xfar) == fa:
                a = m
            else:
                b = m
        pT, pB = (a, b) if fa == "T" else (b, a)
        ok, info = certificate([M, M1], F, xfar, [zs[0] + pT, mp.mpf(0)], [zs[0] + pB, mp.mpf(0)])
        edges.append(dict(j=j, d=mp.nstr((a + b) / 2, 20), cert=ok, info=info))
    ratios = []
    for e in edges:
        for e2 in edges:
            if e2["j"] - e["j"] == 96 or abs(e2["j"] - e["j"] - 96) <= 1:
                ratios.append(float(mp.mpf(e["d"]) / mp.mpf(e2["d"]) / lu))
    out = dict(sys=sys_, fates="".join(fates), T_frac_deep=tfrac, X_frac=xfrac, A=A, best_tau=best, A96=A[96],
               edges=edges, ratio_over_lambda=ratios, n_cert=sum(e["cert"] for e in edges),
               map_calls=M.calls + M1.calls, sec_grid=t_grid, sec=time.time() - t0)
    return out


# ======================================================================================== T-SWITCH
def kerr_closed_form():
    m = mp.mpf(5) / 4; a = mp.mpf(3) / 5 * m; E = mp.mpf(97) / 100; L = -mp.mpf(2550268) / 1000000
    R = lambda r, Q: (E * (r**2 + a**2) - a * L) ** 2 - (r**2 - 2 * m * r + a**2) * (r**2 + (L - a * E) ** 2 + Q)  # noqa
    dR = lambda r, Q: mp.diff(lambda rr: R(rr, Q), r)  # noqa
    rs, Qs = mp.findroot([R, dR], (mp.mpf(6.24), mp.mpf(18)))
    S = 2 * m / (1 - E**2) - 2 * rs
    Pq = R(0, Qs) / ((E**2 - 1) * rs**2)
    ra = (S + mp.sqrt(S * S - 4 * Pq)) / 2
    rst, Qst = None, None
    for r0 in (10, 14, 18, 22, 26):                       # the stable spherical orbit (other double root)
        try:
            r1, Q1 = mp.findroot([R, dR], (mp.mpf(r0), mp.mpf(25)))
            if abs(r1 - rs) > 1:
                rst, Qst = r1, Q1
                break
        except Exception:
            pass
    return dict(x_star=rs - m, Q_sph=Qs, x_h=ra - m, x_stable=(rst - m) if rst is not None else None, Q_stable=Qst)


def life(M, x, N):
    o = M.orbit([x, mp.mpf(0)], N)
    return o["end"], o["n"]


def switch_pair(M, M1, F, xfar, xa, xo, n_a, accept_cert=True):
    """xa: the plunging member (Pi true), xo: the other. Bisection on Pi(x) = plunges with n <= n_a + 12."""
    def Pi(x):
        e, n = life(M, x, n_a + 12)
        return e == 1
    a, b = xa, xo
    stages = []
    h = 0
    cls, info = None, {}
    while True:
        m_ = (a + b) / 2
        if Pi(m_):
            a = m_
        else:
            b = m_
        h += 1
        w = abs(a - b)
        if accept_cert and h >= 25 and (h - 25) % 5 == 0:
            ok, ci = certificate([M, M1], F, xfar, [a, mp.mpf(0)], [b, mp.mpf(0)])
            stages.append(dict(halvings=h, width=float(w), cert=ok, info=ci))
            if ok:
                cls = "H"
                break
        if w <= mp.mpf("1e-18") * abs(a) or h > 80:
            break
    if cls is None:
        (ep, np_), (eq, nq) = life(M, a, 120), life(M, b, 120)
        (ep1, np1), (eq1, nq1) = life(M1, a, 120), life(M1, b, 120)
        if ep == 1 and eq == 1 and abs(np_ - nq) <= 2:
            cls = "A"
        elif (ep == 1 and np_ <= n_a + 12) != (eq == 1 and nq <= n_a + 12):      # addendum 2: fates = Pi
            zp, zq = [a, mp.mpf(0)], [b, mp.mpf(0)]
            hist = []
            for _ in range(120):
                sp_, zp2, _m = M.step(zp)
                sq_, zq2, _m2 = M.step(zq)
                if sp_ != 0 or sq_ != 0:
                    break
                close = max(abs(zp2[0] - zq2[0]), abs(zp2[1] - zq2[1])) <= mp.mpf("1e-6")
                hist.append((close, F.rho(zp2) > mp.mpf("1e-2") and F.rho(zq2) > mp.mpf("1e-2")))
                zp, zq = zp2, zq2
            idx = [i for i, (c, _) in enumerate(hist) if c]
            far_ok = bool(idx) and idx[-1] >= 8 and all(hist[i][1] for i in range(idx[-1] - 8, idx[-1] + 1))
            agree = (ep, np_, eq, nq) == (ep1, np1, eq1, nq1)
            cls = "O" if (far_ok and agree) else "U"
            info = dict(last_close=idx[-1] if idx else None, far_ok=far_ok, r1r2_agree=agree)
        else:
            cls = "U"
        info.update(final=dict(p=(ep, np_), q=(eq, nq), p_R1=(ep1, np1), q_R1=(eq1, nq1)))
    return dict(cls=cls, a=mp.nstr(a, 30), b=mp.nstr(b, 30), halvings=h, stages=stages, info=info)


def cut_indep(sys_, a, b, base):
    res = {}
    for xpl in (1.3, 1.7):
        Mx = EdgeMap(sys_, "R2", xpl=xpl)
        res[str(xpl)] = [life(Mx, mp.mpf(a), 120)[0] == 1, life(Mx, mp.mpf(b), 120)[0] == 1]
    ok = all(v == base for v in res.values())
    return ok, res


def setup(sys_):
    M = EdgeMap(sys_, "R2"); M1 = EdgeMap(sys_, "R1")
    zs, lu, vu, vs, res, det = fixed_and_frame(M, sys_)
    return M, M1, Frame(zs, vu, vs), zs


def accept(M, x1, x2):
    """Exactly one plunges with n_a <= 60 and the other survives past n_a + 24 (R2, <= 120 crossings)."""
    (e1, n1), (e2, n2) = life(M, x1, 120), life(M, x2, 120)
    for (ea, na, xa), (eo, no, xo) in (((e1, n1, x1), (e2, n2, x2)), ((e2, n2, x2), (e1, n1, x1))):
        if ea == 1 and na <= 60 and not (eo == 1 and no <= na + 24) and eo in (0, 1):
            return dict(xa=xa, xo=xo, n_a=na)
    return dict(reject=f"fates ({e1},{n1}) / ({e2},{n2})")


def controls():
    out = {}
    kc = kerr_closed_form()
    _, _, xh_st, _ = stored("kerr")
    out["K-x_h"] = dict(closed=mp.nstr(kc["x_h"], 30), stored=mp.nstr(xh_st, 25), diff=float(abs(kc["x_h"] - xh_st)),
                        pass_=bool(abs(kc["x_h"] - xh_st) <= mp.mpf("1e-18")))
    print("K-x_h:", out["K-x_h"], flush=True)
    M, M1, F, zs = setup("kerr")
    # K-H
    acc = accept(M, kc["x_h"] + mp.mpf("1e-5"), kc["x_h"] - mp.mpf("2e-5"))
    if "reject" in acc:
        out["K-H"] = dict(pass_=False, why=acc)
    else:
        r = switch_pair(M, M1, F, XFAR["kerr"], acc["xa"], acc["xo"], acc["n_a"])
        inside = min(mp.mpf(r["a"]), mp.mpf(r["b"])) <= kc["x_h"] <= max(mp.mpf(r["a"]), mp.mpf(r["b"]))
        ci, cres = cut_indep("kerr", r["a"], r["b"], [True, False])
        out["K-H"] = dict(result=r, xh_inside=bool(inside), cut_indep=ci, cut=cres,
                          pass_=(r["cls"] == "H" and inside and ci))
    print("K-H:", {k: v for k, v in out["K-H"].items() if k != "result"}, out["K-H"].get("result", {}).get("cls"), flush=True)
    # K-O' (addendum 2): SECTION cut at the midpoint between x* and the stable spherical orbit
    xc = (zs[0] + kc["x_stable"]) / 2
    Mo, Mo1 = EdgeMap("kerr", "R2"), EdgeMap("kerr", "R1")
    Mo.xc = Mo1.xc = xc
    xs_scan = [kc["x_stable"] + (kc["x_h"] - kc["x_stable"]) * i / 200 for i in range(1, 200)]
    prev, flip = None, None
    for x in xs_scan:
        e, n = life(Mo, x, 120)
        pl = e == 1
        if prev is not None and pl != prev[1]:
            flip = (prev[0], x, prev[1])
            break
        prev = (x, pl)
    if flip is None:
        out["K-O"] = dict(pass_=False, why="no flip found", xc=float(xc))
    else:
        xa, xo = (flip[0], flip[1]) if flip[2] else (flip[1], flip[0])
        ea, na = life(Mo, xa, 120)
        r = switch_pair(Mo, Mo1, F, XFAR["kerr"], xa, xo, na)
        out["K-O"] = dict(result=r, xc=float(xc), pass_=r["cls"] == "O")
    print("K-O':", out["K-O"].get("result", {}).get("cls"), out["K-O"].get("why"), "xc", float(xc), flush=True)
    # K-A: a one-whirl lifetime step outside x_h
    xs2 = [kc["x_h"] + mp.mpf(10) ** (-mp.mpf(g) / 4) for g in range(4, 40)]
    ns = [life(M, x, 120) for x in xs2]
    step_ = None
    for i in range(len(xs2) - 1):
        if ns[i][0] == 1 and ns[i + 1][0] == 1 and ns[i][1] != ns[i + 1][1]:
            step_ = i
            break
    if step_ is None:
        out["K-A"] = dict(pass_=False, why="no lifetime step", ns=ns)
    else:
        n0 = min(ns[step_][1], ns[step_ + 1][1])
        lo_, hi_ = (xs2[step_], xs2[step_ + 1]) if ns[step_][1] == n0 else (xs2[step_ + 1], xs2[step_])
        r = switch_pair(M, M1, F, XFAR["kerr"], lo_, hi_, n0 - 12)        # Pi(x) = plunges with n <= n0
        out["K-A"] = dict(result=r, n0=n0, pass_=r["cls"] == "A")
    print("K-A:", out["K-A"].get("result", {}).get("cls"), out["K-A"].get("why"), flush=True)
    # T-H (TS; written to file only)
    Mt, Mt1, Ft, zst = setup("ts")
    _, _, xh_ts, _ = stored("ts")
    ok, ci = certificate([Mt, Mt1], Ft, XFAR["ts"], [xh_ts + mp.mpf("1e-12"), mp.mpf(0)],
                         [xh_ts - mp.mpf("1e-12"), mp.mpf(0)])            # addendum 2: certificate directly
    out["T-H"] = dict(cert=ok, info=ci, pass_=ok)
    print("T-H:", "PASS" if out["T-H"]["pass_"] else "FAIL", flush=True)
    out["all_pass"] = all(v["pass_"] for v in out.values() if isinstance(v, dict))
    return out


def tswitch():
    d = json.load(open(os.path.join(ROOT, "data", "ts_chaos", "alpha.json")))["ts45"]["samples"]
    M, M1, F, zs = setup("ts")
    examined, accepted, log = 0, [], []
    for smp in d:
        if examined >= 60 or len(accepted) >= 8:
            break
        x0 = mp.mpf(smp["x0"])
        for side, k in ((-1, 0), (1, 1)):
            if examined >= 60 or len(accepted) >= 8:
                break
            if smp["c"] == smp["pm"]["3e-05"][k]:
                continue
            examined += 1
            x1 = x0 + side * mp.mpf("3e-5")
            acc = accept(M, x0, x1)
            if "reject" in acc:
                log.append(dict(x0=smp["x0"], side=side, reject=acc["reject"]))
                continue
            r = switch_pair(M, M1, F, XFAR["ts"], acc["xa"], acc["xo"], acc["n_a"])
            if r["cls"] == "H":
                pl = [True, False]
                ci, cres = cut_indep("ts", r["a"], r["b"], pl)
                r["cut_indep"], r["cut"] = ci, cres
            accepted.append(dict(x0=smp["x0"], side=side, n_a=acc["n_a"], **r))
            log.append(dict(x0=smp["x0"], side=side, cls=r["cls"]))
    return dict(examined=examined, accepted=accepted, log=log, accept_rate=len(accepted) / max(examined, 1))


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
    if mode == "tbands":
        s_ = sys.argv[2]
        os.makedirs(OUT, exist_ok=True)
        out = tbands(s_)
        fn = os.path.join(OUT, f"tbands_{s_}.json")
        json.dump(out, open(fn, "w"), indent=1, default=str)
        if s_ == "kerr":
            print(json.dumps({k: v for k, v in out.items() if k != "A"}, indent=1, default=str), flush=True)
        print(f"[{s_}] T-BANDS done -> {fn}  [{out['sec']:.0f}s, {out['map_calls']} map calls]", flush=True)
    if mode == "tswitch":
        os.makedirs(OUT, exist_ok=True)
        if sys.argv[2] == "controls":
            out = controls()
            json.dump(out, open(os.path.join(OUT, "tswitch_controls.json"), "w"), indent=1, default=str)
            print("VERDICT-controls:", "PASS" if out["all_pass"] else "FAIL (T-SWITCH VOID)", flush=True)
        else:
            out = tswitch()
            json.dump(out, open(os.path.join(OUT, "tswitch_ts.json"), "w"), indent=1, default=str)
            print("[ts] T-SWITCH done (values in file)", flush=True)
