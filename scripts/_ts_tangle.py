#!/usr/bin/env python3
"""Homoclinic-tangle test at the TS delta=2 capture edge (data/ts_chaos/TANGLE_PREREGISTRATION.md).

Section y = 0 crossed upward (p_y > 0), coordinates (x, p_x). Reversor R(x, p_x) = (x, -p_x), so W^s = R(W^u), and a
crossing of W^u with the line p_x = 0 is a symmetric homoclinic point. The splitting angle there is
theta = 2 atan(|t_along| / |t_normal|) between W^u and R(W^u); it is 0 iff the manifolds coincide.
The TRACER (fixed point, eigenvectors, manifold growth, crossing, tangent, angle) is map-agnostic and shared with the
forced-pendulum positive control (G1).

    .venv/bin/python scripts/_ts_tangle.py g0            # structure checks (symmetry, neck), both systems
    .venv/bin/python scripts/_ts_tangle.py g1            # forced-pendulum Melnikov control
    .venv/bin/python scripts/_ts_tangle.py run <kerr|ts> [R1|R2] [delta]
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
import sympy as sp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "ts_chaos", "tangle")
mp.mp.dps = 40
LEV = {"ts": dict(spec="ts2:4/5", E=sp.Rational(97, 100), L=sp.Rational(41, 8)),
       "kerr": dict(spec="ts2kerr:4/5", E=sp.Rational(97, 100), L=sp.Rational(2550268, 1000000))}
TOL = {"R1": 1e-22, "R2": 1e-28}


# ======================================================================================== generic tracer (shared)
def fixed_point(P, z0, hfd, tol, maxit=30):
    """Newton on P(z) - z = 0 with a central-difference Jacobian. z: list of 2 mpf. Returns (z, J, residual)."""
    z = [mp.mpf(z0[0]), mp.mpf(z0[1])]
    res = None
    for _ in range(maxit):
        Pz = P(z)
        F = [Pz[0] - z[0], Pz[1] - z[1]]
        res = max(abs(F[0]), abs(F[1]))
        J = jac(P, z, hfd)
        A = mp.matrix([[J[0][0] - 1, J[0][1]], [J[1][0], J[1][1] - 1]])
        d = mp.lu_solve(A, mp.matrix([-F[0], -F[1]]))
        z = [z[0] + d[0], z[1] + d[1]]
        if res < tol:
            break
    Pz = P(z)
    res = max(abs(Pz[0] - z[0]), abs(Pz[1] - z[1]))
    return z, jac(P, z, hfd), res


def jac(P, z, h):
    cols = []
    for i in range(2):
        zp = list(z); zm = list(z)
        zp[i] += h; zm[i] -= h
        a, b = P(zp), P(zm)
        cols.append([(a[0] - b[0]) / (2 * h), (a[1] - b[1]) / (2 * h)])
    return [[cols[0][0], cols[1][0]], [cols[0][1], cols[1][1]]]


def eig2(J):
    tr = J[0][0] + J[1][1]
    det = J[0][0] * J[1][1] - J[0][1] * J[1][0]
    disc = tr * tr / 4 - det
    if disc <= 0:
        return None
    lu = tr / 2 + mp.sqrt(disc) if tr > 0 else tr / 2 - mp.sqrt(disc)      # |lu| > 1
    ls = det / lu

    def vec(l):
        a, b = J[0][0] - l, J[0][1]
        v = [b, -a] if abs(b) > abs(J[1][0]) or abs(J[1][1] - l) == 0 else [J[1][1] - l, -J[1][0]]
        n = mp.sqrt(v[0] ** 2 + v[1] ** 2)
        return [v[0] / n, v[1] / n]
    return lu, ls, vec(lu), vec(ls), det


def branch_point(P, zs, vu, delta, lam, u, alive):
    """Point of W^u at continuous parameter u = k + f: P^k(zs + delta*lam^f * vu). alive(z) False -> None."""
    k = int(mp.floor(u))
    f = u - k
    s = delta * abs(lam) ** f
    z = [zs[0] + s * vu[0], zs[1] + s * vu[1]]
    for _ in range(k):
        z = P(z)
        if z is None or not alive(z):
            return None
    return z


def first_crossing(P, zs, vu, delta, lam, line, Kmax, alive, J=48, iters=110):
    """First u > 0 where coordinate `line` of the branch changes sign. Returns (u*, z*, tangent, info)."""
    g0 = None
    prev = None
    rows = []
    zrow = [[zs[0] + delta * abs(lam) ** (j / J) * vu[0], zs[1] + delta * abs(lam) ** (j / J) * vu[1]] for j in range(J)]
    bracket = None
    for k in range(Kmax + 1):
        for j in range(J):
            z = zrow[j]
            if z is None:
                continue
            g = z[line]
            u = mp.mpf(k) + mp.mpf(j) / J
            if g0 is None:
                g0 = mp.sign(g)
            elif mp.sign(g) != g0 and prev is not None:
                bracket = (prev[0], u)
                break
            prev = (u, z)
            rows.append((float(u), float(z[0]), float(z[1])))
        if bracket:
            break
        zrow = [P(z) if (z is not None and alive(z)) else None for z in zrow]
        zrow = [z if (z is not None and alive(z)) else None for z in zrow]
    if not bracket:
        return None, None, None, dict(rows=rows, note="no crossing within Kmax")
    a, b = bracket
    ga = branch_point(P, zs, vu, delta, lam, a, alive)[line]
    for _ in range(iters):
        m = (a + b) / 2
        zm = branch_point(P, zs, vu, delta, lam, m, alive)
        if mp.sign(zm[line]) == mp.sign(ga):
            a, ga = m, zm[line]
        else:
            b = m
        if b - a < mp.mpf(10) ** (-(mp.mp.dps - 6)):
            break
    u = (a + b) / 2
    zc = branch_point(P, zs, vu, delta, lam, u, alive)
    return u, zc, None, dict(rows=rows[-6:], bracket=[float(bracket[0]), float(bracket[1])])


def tangent(P, zs, vu, delta, lam, u, du, alive):
    zp = branch_point(P, zs, vu, delta, lam, u + du, alive)
    zm = branch_point(P, zs, vu, delta, lam, u - du, alive)
    return [(zp[0] - zm[0]) / (2 * du), (zp[1] - zm[1]) / (2 * du)]


def split_angle(t, line):
    along = 1 - line
    return 2 * mp.atan(abs(t[along]) / abs(t[line]))


# ======================================================================================== G1: forced pendulum
@numba.njit(fastmath=False)
def _pend_map(x, p, eps, nsteps):
    """Stroboscopic map over one period 2 pi of x'' = -sin x + eps sin t, from phase 0. Classical RK4."""
    h = 2 * math.pi / nsteps
    t = 0.0
    for _ in range(nsteps):
        k1x = p; k1p = -math.sin(x) + eps * math.sin(t)
        k2x = p + 0.5 * h * k1p; k2p = -math.sin(x + 0.5 * h * k1x) + eps * math.sin(t + 0.5 * h)
        k3x = p + 0.5 * h * k2p; k3p = -math.sin(x + 0.5 * h * k2x) + eps * math.sin(t + 0.5 * h)
        k4x = p + h * k3p; k4p = -math.sin(x + h * k3x) + eps * math.sin(t + h)
        x += h * (k1x + 2 * k2x + 2 * k3x + k4x) / 6
        p += h * (k1p + 2 * k2p + 2 * k3p + k4p) / 6
        t += h
    return x, p


def g1():
    out = {}
    for eps in (0.0, 1e-3, 3e-3):
        def P(z, eps=eps):
            a, b = _pend_map(float(z[0]), float(z[1]), eps, 20000)
            return [mp.mpf(a), mp.mpf(b)]
        zs, J, res = fixed_point(P, [-math.pi, 0.0], mp.mpf("1e-6"), mp.mpf("1e-14"))
        e = eig2(J)
        lu, ls, vu, vs, det = e
        if vu[1] < 0:
            vu = [-vu[0], -vu[1]]                  # upper branch (p > 0), heading right from x = -pi
        alive = lambda z: abs(z[0]) < 10      # noqa: E731
        u, zc, _, info = first_crossing(P, zs, vu, mp.mpf("1e-6"), lu, 0, 12, alive)
        t = tangent(P, zs, vu, mp.mpf("1e-6"), lu, u, mp.mpf("1e-5"), alive)
        th = split_angle(t, 0)
        pred = eps * math.pi / math.cosh(math.pi / 2) / 2
        out[eps] = dict(fixed=[float(zs[0]), float(zs[1])], res=float(res), lam=float(lu), det=float(det),
                        u=float(u), cross=[float(zc[0]), float(zc[1])], theta=float(th), melnikov=pred,
                        ratio=(float(th) / pred if pred else None))
        print(f"  eps={eps:g}: theta={float(th):.6e}  Melnikov={pred:.6e}  ratio={out[eps]['ratio']}  "
              f"lam={float(lu):.4g} det-1={float(det) - 1:.1e} cross p={float(zc[1]):.6f}", flush=True)
    ok = (out[0.0]["theta"] <= 1e-9 and all(abs(out[e]["ratio"] - 1) <= 0.10 for e in (1e-3, 3e-3)))
    print(f"VERDICT-G1: {'PASS' if ok else 'FAIL'}", flush=True)
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(results={str(k): v for k, v in out.items()}, pass_=ok), open(os.path.join(OUT, "g1.json"), "w"),
              indent=1)


# ======================================================================================== DD section map (TS, Kerr)
def make_secmap(eng):
    from _hp_ddprim import dd_add, dd_div, dd_mul, dd_sqrt, dd_sub
    f = eng.f
    gbs = eng._run.gbs_step

    @numba.njit
    def secmap(xh, xl, pxh, pxl, Eh, El, Lh, Ll, tol, k, hmax, xmin, xmax, maxsteps):
        """One upward crossing of y = 0, located exactly (Newton on the last step length, in DD).
        Returns status (0 ok, -1 off shell, 1 plunge, 2 escape, 3 cap), state hi[4], lo[4], |y| residual."""
        sh = np.zeros(4); sl = np.zeros(4)
        sh[0], sl[0] = xh, xl
        sh[2], sl[2] = pxh, pxl
        v = f(xh, xl, 0.0, 0.0, Eh, El, Lh, Ll)
        a = dd_mul(v[0], v[1], pxh, pxl); a = dd_mul(a[0], a[1], pxh, pxl)
        num = dd_sub(-1.0, 0.0, v[16], v[17]); num = dd_sub(num[0], num[1], a[0], a[1])
        if num[0] <= 0.0:
            return -1, sh, sl, 0.0
        q = dd_div(num[0], num[1], v[2], v[3])
        sh[3], sl[3] = dd_sqrt(q[0], q[1])
        h = 0.05
        seen_neg = False
        expo = 1.0 / (2 * k - 1)
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
                if seen_neg and sh[1] < 0.0 <= nh[1] and nh[3] > 0.0:
                    # Newton on the step length from the pre-step state s0 = (sh, sl)
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
                    return 0, zh, zl, abs(zh[1] + zl[1])
                if nh[1] < 0.0:
                    seen_neg = True
                sh, sl = nh, nl
                if sh[0] < xmin:
                    return 1, sh, sl, 0.0
                if sh[0] > xmax or abs(sh[1]) > 0.999999:
                    return 2, sh, sl, 0.0
            fac = 0.94 * (1.0 / e) ** expo if e > 0.0 else 4.0
            h *= min(4.0, max(0.2, fac))
        return 3, sh, sl, 0.0
    return secmap


def dd_of(v):
    v = mp.mpf(v)
    hi = float(v)
    return hi, float(v - hi)


class TSMap:
    def __init__(self, sys_, rung):
        import _hp_dd as H
        self.lv = LEV[sys_]
        self.eng = H.DDEngine(self.lv["spec"])
        self.secmap = make_secmap(self.eng)
        self.E = tuple(float(c) for c in H.dd_const(self.lv["E"]))
        self.L = tuple(float(c) for c in H.dd_const(self.lv["L"]))
        self.tol = TOL[rung]
        self.calls = 0
        self.last = None

    def __call__(self, z):
        xh, xl = dd_of(z[0]); ph, pl = dd_of(z[1])
        st, sh, sl, yres = self.secmap(xh, xl, ph, pl, self.E[0], self.E[1], self.L[0], self.L[1], self.tol, 12,
                                       2.0, 1.5, 2000.0, 5_000_000)
        self.calls += 1
        if st != 0:
            return None
        self.last = (sh.copy(), sl.copy(), yres)
        return [mp.mpf(sh[0]) + sl[0], mp.mpf(sh[2]) + sl[2]]


def g0(sys_):
    from _kt_exact_op import get_metric
    import _hp_dd as H
    lv = LEV[sys_]
    ginv, name = get_metric(lv["spec"])
    xs_, ys_ = H.x, H.y
    sym = all(sp.cancel(ginv[i, j] - ginv[i, j].subs(ys_, -ys_)) == 0 for i in range(4) for j in range(4))
    W = sp.together(ginv[0, 0] * lv["E"] ** 2 - 2 * ginv[0, 3] * lv["E"] * lv["L"] + ginv[3, 3] * lv["L"] ** 2)
    W0 = sp.lambdify(xs_, W.subs(ys_, 0), "mpmath")
    W0x = sp.lambdify(xs_, sp.diff(W, xs_).subs(ys_, 0), "mpmath")
    W0yy = sp.lambdify(xs_, sp.diff(W, ys_, 2).subs(ys_, 0), "mpmath")
    grid = [mp.mpf(1.5) + mp.mpf(i) / 20 for i in range(1, 2000)]
    vals = [W0(g) for g in grid]
    crit = []
    for i in range(1, len(grid) - 1):
        if (vals[i] - vals[i - 1]) * (vals[i + 1] - vals[i]) < 0:
            xc = mp.findroot(W0x, grid[i])
            kind = "max" if vals[i] > vals[i - 1] else "min"
            crit.append(dict(x=xc, kind=kind, access=-1 - W0(xc), Wyy=W0yy(xc)))
    return dict(name=name, reflection_symmetric=bool(sym), critical=crit)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "g1":
        g1()
    if mode == "g0":
        for s_ in sys.argv[2:] or ["kerr", "ts"]:
            r = g0(s_)
            print(f"[{s_}] {r['name']}: reflection symmetric = {r['reflection_symmetric']}")
            for c in r["critical"]:
                print(f"   W(x,0) {c['kind']} at x = {mp.nstr(c['x'], 12)}; -1-W = {mp.nstr(c['access'], 6)} "
                      f"(>0: accessible); W_yy = {mp.nstr(c['Wyy'], 6)}")
