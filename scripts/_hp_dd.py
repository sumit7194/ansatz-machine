#!/usr/bin/env python3
"""High-precision geodesic engine for the probe (data/ts_chaos/HP_PREREGISTRATION.md).

The reduced 2-DOF Hamiltonian is that of scripts/_ts_chaos.py (p_t = -E, p_phi = L, H = -1/2), built from the SAME
exact rational inverse metric. Two arithmetics:
  DD     double-double (~32 digits), numba. The RHS is GENERATED from sympy -> CSE -> DD operations
         (scripts/_hp_ddprim.py), with every rational constant split exactly into hi + lo.
  MP     mpmath at a chosen precision (the R3 spot-check rung), same RHS via lambdify.
Integrator: Gragg-Bulirsch-Stoer, modified midpoint with step sequence 2, 4, ..., 2k, Aitken-Neville extrapolation, fixed
order k, adaptive step on |T_kk - T_k,k-1|. Events at accepted step ends (the conventions of _ts_chaos.run):
  - crossing: y from < 0 to >= 0 with p_y > 0;
  - plunge: x < xmin;
  - escape: x > xmax or |y| > ymax;
  - also stops at tmax, at N crossings, or at maxsteps (status 3).
h <= hmax = min(hmax0, 0.1 * the last inter-crossing proper time), so no step can contain two crossings.
Status: 0 survive (N crossings or tmax), 1 plunge, 2 escape, 3 step cap / failure.
"""
import hashlib
import importlib.util
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numba  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_metrics as MM  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "data", "ts_chaos", "gen")
x, y = MM.x, MM.y
E_, L_ = sp.symbols("E L", real=True)
NAMES = ["gxx", "gyy", "gxx_x", "gxx_y", "gyy_x", "gyy_y", "W_x", "W_y", "W"]


def rhs_exprs(ginv):
    """Exactly the 9 expressions of _ts_chaos.build_rhs."""
    gxx, gyy = sp.cancel(ginv[1, 1]), sp.cancel(ginv[2, 2])
    W = sp.together(ginv[0, 0] * E_**2 - 2 * ginv[0, 3] * E_ * L_ + ginv[3, 3] * L_**2)
    return [gxx, gyy, sp.diff(gxx, x), sp.diff(gxx, y), sp.diff(gyy, x), sp.diff(gyy, y), sp.diff(W, x), sp.diff(W, y), W]


def dd_const(r):
    r = sp.Rational(r)
    hi = float(r)
    lo = float(r - sp.Rational(hi))
    return repr(hi), repr(lo)


class _Emitter:
    def __init__(self):
        self.lines, self.n, self.sym = [], 0, {}

    def tmp(self):
        self.n += 1
        return f"t{self.n}h", f"t{self.n}l"

    def op(self, fn, a, b):
        h, l = self.tmp()
        self.lines.append(f"    {h}, {l} = {fn}({a[0]}, {a[1]}, {b[0]}, {b[1]})")
        return h, l

    def pw(self, a, n):
        out = None
        base = a
        while n:
            if n & 1:
                out = base if out is None else self.op("dd_mul", out, base)
            n >>= 1
            if n:
                base = self.op("dd_mul", base, base)
        return out

    def conv(self, e):
        if e in self.sym:
            return self.sym[e]
        if e.is_Rational:
            return dd_const(e)
        if e.is_Add:
            args = list(e.args)
            acc = self.conv(args[0])
            for a in args[1:]:
                acc = self.op("dd_add", acc, self.conv(a))
            return acc
        if e.is_Mul:
            c, facs = e.as_coeff_mul()
            num, den = [], []
            for f in facs:
                if f.is_Pow and f.exp.is_Integer and f.exp < 0:
                    den.append(self.pw(self.conv(f.base), int(-f.exp)))
                else:
                    num.append(self.conv(f))
            acc = None
            for v in num:
                acc = v if acc is None else self.op("dd_mul", acc, v)
            if acc is None:
                acc = ("1.0", "0.0")
            if den:
                d = den[0]
                for v in den[1:]:
                    d = self.op("dd_mul", d, v)
                acc = self.op("dd_div", acc, d)
            if c != 1:
                acc = self.op("dd_mul", acc, dd_const(c))
            return acc
        if e.is_Pow and e.exp.is_Integer:
            n = int(e.exp)
            if n > 0:
                return self.pw(self.conv(e.base), n)
            return self.op("dd_div", ("1.0", "0.0"), self.pw(self.conv(e.base), -n))
        raise ValueError(f"cannot emit {type(e).__name__}: {e}")


def build_dd_rhs(ginv, name):
    """Generate, import and njit the DD RHS f(xh, xl, yh, yl, Eh, El, Lh, Ll) -> 18 floats (9 DD values)."""
    exprs = rhs_exprs(ginv)
    key = "dd_" + hashlib.sha256(sp.srepr(sp.Matrix(exprs)).encode()).hexdigest()[:16]
    os.makedirs(GEN, exist_ok=True)
    path = os.path.join(GEN, f"rhs_{key}.py")
    if not os.path.exists(path):
        reps, red = sp.cse(exprs, optimizations="basic")
        em = _Emitter()
        em.sym = {x: ("xh", "xl"), y: ("yh", "yl"), E_: ("Eh", "El"), L_: ("Lh", "Ll")}
        for s_, e_ in reps:
            em.sym[s_] = em.conv(e_)
        outs = [em.conv(e_) for e_ in red]
        head = [f"# GENERATED double-double RHS from the exact inverse metric of: {name}",
                "import numba", "from _hp_ddprim import dd_add, dd_mul, dd_div", "",
                "@numba.njit", "def f(xh, xl, yh, yl, Eh, El, Lh, Ll):"]
        tail = ["    return (" + ", ".join(f"{h}, {l}" for h, l in outs) + ",)"]
        with open(path, "w") as fh:
            fh.write("\n".join(head + em.lines + tail) + "\n")
    spec = importlib.util.spec_from_file_location(f"rhs_{key}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.f, path


def make_dd_integrator(f):
    from _hp_ddprim import dd_add, dd_div, dd_mul, dd_mul_d, dd_sqrt, dd_sub

    @numba.njit
    def rhs(sh, sl, Eh, El, Lh, Ll):
        v = f(sh[0], sl[0], sh[1], sl[1], Eh, El, Lh, Ll)
        gxx = (v[0], v[1]); gyy = (v[2], v[3])
        gxx_x = (v[4], v[5]); gxx_y = (v[6], v[7]); gyy_x = (v[8], v[9]); gyy_y = (v[10], v[11])
        W_x = (v[12], v[13]); W_y = (v[14], v[15])
        dh = np.empty(4); dl = np.empty(4)
        dh[0], dl[0] = dd_mul(gxx[0], gxx[1], sh[2], sl[2])
        dh[1], dl[1] = dd_mul(gyy[0], gyy[1], sh[3], sl[3])
        px2 = dd_mul(sh[2], sl[2], sh[2], sl[2])
        py2 = dd_mul(sh[3], sl[3], sh[3], sl[3])
        a = dd_mul(gxx_x[0], gxx_x[1], px2[0], px2[1])
        b = dd_mul(gyy_x[0], gyy_x[1], py2[0], py2[1])
        s = dd_add(a[0], a[1], b[0], b[1]); s = dd_add(s[0], s[1], W_x[0], W_x[1])
        dh[2], dl[2] = dd_mul_d(s[0], s[1], -0.5)
        a = dd_mul(gxx_y[0], gxx_y[1], px2[0], px2[1])
        b = dd_mul(gyy_y[0], gyy_y[1], py2[0], py2[1])
        s = dd_add(a[0], a[1], b[0], b[1]); s = dd_add(s[0], s[1], W_y[0], W_y[1])
        dh[3], dl[3] = dd_mul_d(s[0], s[1], -0.5)
        return dh, dl

    @numba.njit
    def shell(sh, sl, Eh, El, Lh, Ll):
        """2H + 1 in DD (should be 0)."""
        v = f(sh[0], sl[0], sh[1], sl[1], Eh, El, Lh, Ll)
        a = dd_mul(v[0], v[1], sh[2], sl[2]); a = dd_mul(a[0], a[1], sh[2], sl[2])
        b = dd_mul(v[2], v[3], sh[3], sl[3]); b = dd_mul(b[0], b[1], sh[3], sl[3])
        s = dd_add(a[0], a[1], b[0], b[1]); s = dd_add(s[0], s[1], v[16], v[17])
        return dd_add(s[0], s[1], 1.0, 0.0)

    @numba.njit
    def py_on_shell(x0, Eh, El, Lh, Ll):
        v = f(x0, 0.0, 0.0, 0.0, Eh, El, Lh, Ll)
        num = dd_sub(-1.0, 0.0, v[16], v[17])                  # -1 - W  (p_x = 0)
        if num[0] <= 0.0:
            return -1.0, 0.0
        q = dd_div(num[0], num[1], v[2], v[3])
        return dd_sqrt(q[0], q[1])

    @numba.njit
    def axpy(yh, yl, ch, cl, dh, dl):
        """y + c*d for 4-vectors in DD (c a DD scalar)."""
        oh = np.empty(4); ol = np.empty(4)
        for i in range(4):
            m = dd_mul(ch, cl, dh[i], dl[i])
            oh[i], ol[i] = dd_add(yh[i], yl[i], m[0], m[1])
        return oh, ol

    @numba.njit
    def midpoint(yh, yl, f0h, f0l, h, hl, n, Eh, El, Lh, Ll):
        hs = dd_div(h, hl, float(n), 0.0)                       # the step is the DD value h + hl (hl = 0 in run())
        h2 = dd_mul_d(hs[0], hs[1], 2.0)
        zph, zpl = yh.copy(), yl.copy()                         # z_{m-1}
        zh, zl = axpy(yh, yl, hs[0], hs[1], f0h, f0l)           # z_1
        for _ in range(n - 1):
            fh, fl = rhs(zh, zl, Eh, El, Lh, Ll)
            znh, znl = axpy(zph, zpl, h2[0], h2[1], fh, fl)
            zph, zpl, zh, zl = zh, zl, znh, znl
        fh, fl = rhs(zh, zl, Eh, El, Lh, Ll)
        th, tl = axpy(zh, zl, hs[0], hs[1], fh, fl)
        oh = np.empty(4); ol = np.empty(4)
        for i in range(4):
            s = dd_add(th[i], tl[i], zph[i], zpl[i])
            oh[i], ol[i] = dd_mul_d(s[0], s[1], 0.5)
        return oh, ol

    @numba.njit
    def gbs_step(yh, yl, h, hl, k, Eh, El, Lh, Ll):
        """One GBS step of order k. Returns (new state hi, lo, error estimate hi-vector)."""
        f0h, f0l = rhs(yh, yl, Eh, El, Lh, Ll)
        Th = np.empty((k, k, 4)); Tl = np.empty((k, k, 4))
        for j in range(k):
            nj = 2 * (j + 1)
            mh, ml = midpoint(yh, yl, f0h, f0l, h, hl, nj, Eh, El, Lh, Ll)
            Th[j, 0], Tl[j, 0] = mh, ml
            for m in range(1, j + 1):
                nm = 2 * (j - m + 1)
                r = dd_div(float(nj * nj - nm * nm), 0.0, float(nm * nm), 0.0)
                for i in range(4):
                    d = dd_sub(Th[j, m - 1, i], Tl[j, m - 1, i], Th[j - 1, m - 1, i], Tl[j - 1, m - 1, i])
                    q = dd_div(d[0], d[1], r[0], r[1])
                    Th[j, m, i], Tl[j, m, i] = dd_add(Th[j, m - 1, i], Tl[j, m - 1, i], q[0], q[1])
        err = np.empty(4)
        for i in range(4):
            d = dd_sub(Th[k - 1, k - 1, i], Tl[k - 1, k - 1, i], Th[k - 1, k - 2, i], Tl[k - 1, k - 2, i])
            err[i] = d[0]
        return Th[k - 1, k - 1].copy(), Tl[k - 1, k - 1].copy(), err

    @numba.njit
    def run(x0, Eh, El, Lh, Ll, tol, k, nsec, tmax, xmin, xmax, ymax, hmax0, maxsteps):
        sh = np.zeros(4); sl = np.zeros(4)
        sh[0] = x0
        p = py_on_shell(x0, Eh, El, Lh, Ll)
        if p[0] < 0.0:
            return -1, 0, 0.0, 0, np.zeros((1, 8)), 0.0
        sh[3], sl[3] = p
        th, tl = 0.0, 0.0
        h = 0.05
        ns = 0
        status = 0
        nsteps = 0
        t_last = 0.0
        dt_cross = 1e300
        secs = np.zeros((nsec, 8))
        maxshell = 0.0
        expo = 1.0 / (2 * k - 1)
        while ns < nsec and th < tmax:
            if nsteps >= maxsteps:
                status = 3
                break
            hmax = min(hmax0, 0.1 * dt_cross)
            if h > hmax:
                h = hmax
            nh, nl, err = gbs_step(sh, sl, h, 0.0, k, Eh, El, Lh, Ll)
            e = 0.0
            bad = False
            for i in range(4):
                sc = tol * (1.0 + max(abs(sh[i]), abs(nh[i])))
                v = abs(err[i]) / sc
                if not (v == v):
                    bad = True
                if v > e:
                    e = v
            if bad:
                h *= 0.25
                if h < 1e-12:
                    status = 3
                    break
                continue
            if e <= 1.0:
                y0, y1 = sh[1], nh[1]
                sh, sl = nh, nl
                th, tl = dd_add(th, tl, h, 0.0)
                nsteps += 1
                if y0 < 0.0 <= y1 and sh[3] > 0.0:
                    for i in range(4):
                        secs[ns, 2 * i] = sh[i]
                        secs[ns, 2 * i + 1] = sl[i]
                    sv = shell(sh, sl, Eh, El, Lh, Ll)
                    if abs(sv[0]) > maxshell:
                        maxshell = abs(sv[0])
                    if ns > 0:
                        dt_cross = th - t_last
                    t_last = th
                    ns += 1
                if sh[0] < xmin:
                    status = 1
                    break
                if sh[0] > xmax or abs(sh[1]) > ymax:
                    status = 2
                    break
            fac = 0.94 * (1.0 / e) ** expo if e > 0.0 else 4.0
            h *= min(4.0, max(0.2, fac))
        return status, ns, th, nsteps, secs[:ns], maxshell

    @numba.njit
    def run_to_time(x0, Eh, El, Lh, Ll, tol, k, T, hmax0):
        """G4 (addendum 2): integrate to proper time T exactly (last step clipped), no events. Returns the DD state."""
        sh = np.zeros(4); sl = np.zeros(4)
        sh[0] = x0
        p = py_on_shell(x0, Eh, El, Lh, Ll)
        sh[3], sl[3] = p
        th, tl = 0.0, 0.0
        h = 0.05
        expo = 1.0 / (2 * k - 1)
        for _ in range(100_000_000):
            rem = dd_sub(T, 0.0, th, tl)
            if rem[0] <= 0.0:
                break
            if h > hmax0:
                h = hmax0
            clipped = False
            hl = 0.0
            if h >= rem[0]:
                h, hl = rem[0], rem[1]          # the clipped step is the EXACT DD remainder (dropping rem[1] cost ~1e-17 in time)
                clipped = True
            nh, nl, err = gbs_step(sh, sl, h, hl, k, Eh, El, Lh, Ll)
            e = 0.0
            for i in range(4):
                v = abs(err[i]) / (tol * (1.0 + max(abs(sh[i]), abs(nh[i]))))
                if v > e:
                    e = v
            if not (e == e) or not (nh[0] == nh[0]):
                sh[0] = math.nan                  # non-finite: report, never loop (addendum 3)
                break
            if e <= 1.0:
                sh, sl = nh, nl
                if sh[0] < 1.5:                    # plunge before T (addendum 3): stop and flag
                    sh[0] = -sh[0]
                    break
                if clipped:
                    th, tl = T, 0.0
                    break
                th, tl = dd_add(th, tl, h, 0.0)
            fac = 0.94 * (1.0 / e) ** expo if e > 0.0 else 4.0
            h *= min(4.0, max(0.2, fac))
        return sh, sl

    run.gbs_step = gbs_step          # exposed for debugging (no effect on run())
    return run, run_to_time


class DDEngine:
    def __init__(self, spec):
        from _kt_exact_op import get_metric
        self.ginv, self.name = get_metric(spec)
        self.f, self.path = build_dd_rhs(self.ginv, self.name)
        self._run, self._run_to_time = make_dd_integrator(self.f)

    def orbit(self, x0, E, L, tol, nsec, k=12, tmax=5e6, xmin=1.5, xmax=2000.0, ymax=0.999999, hmax0=20.0,
              maxsteps=50_000_000):
        Eh, El = (float(v) for v in dd_const(E)) if not isinstance(E, tuple) else E
        Lh, Ll = (float(v) for v in dd_const(L)) if not isinstance(L, tuple) else L
        st, n, t, steps, secs, mshell = self._run(float(x0), Eh, El, Lh, Ll, tol, k, nsec, tmax, xmin, xmax, ymax,
                                                 hmax0, maxsteps)
        return dict(status=int(st), n=int(n), t_end=float(t), steps=int(steps), secs=secs, maxshell=float(mshell))


def _ddpair(v):
    return v if isinstance(v, tuple) else tuple(float(c) for c in dd_const(v))


def dd_state_at(eng, x0, E, L, T, tol=1e-28, k=12, hmax0=20.0):
    (Eh, El), (Lh, Ll) = _ddpair(E), _ddpair(L)
    sh, sl = eng._run_to_time(float(x0), Eh, El, Lh, Ll, tol, k, float(T), hmax0)
    return sh, sl


def carter_Q(ginv, E, L, xstar=3):
    """Kerr Carter constant in the Weyl chart: Q = (1 - y^2) p_y^2 + G(x*, y) - G(x*, 0), G = (x^2-1)(W+1)/g^xx.
    Returns an mpmath callable Q(x, y, px, py). Uses g^yy/(1-y^2) = g^xx/(x^2-1), which the Weyl form guarantees."""
    import mpmath as mp
    gxx = sp.cancel(ginv[1, 1])
    W = ginv[0, 0] * E_**2 - 2 * ginv[0, 3] * E_ * L_ + ginv[3, 3] * L_**2
    G = (x**2 - 1) * (W + 1) / gxx
    Gf = sp.lambdify((x, y, E_, L_), G, "mpmath")
    Er, Lr = sp.Rational(E), sp.Rational(L)

    def Q(xv, yv, pxv, pyv):
        Em, Lm = mp.mpf(Er.p) / Er.q, mp.mpf(Lr.p) / Lr.q
        return (1 - yv**2) * pyv**2 + Gf(mp.mpf(xstar), yv, Em, Lm) - Gf(mp.mpf(xstar), mp.mpf(0), Em, Lm)
    return Q


class MPEngine:
    """The R3 rung: the same GBS algorithm and event rules as the DD engine, in mpmath at `dps` digits (pure Python,
    slow: spot checks only). RHS = lambdify(mpmath) of the same 9 exact expressions."""

    def __init__(self, spec, dps=50):
        import mpmath as mp
        from _kt_exact_op import get_metric
        self.mp = mp
        self.dps = dps
        self.ginv, self.name = get_metric(spec)
        self.F = sp.lambdify((x, y, E_, L_), rhs_exprs(self.ginv), "mpmath")

    def _rhs(self, s, E, L):
        gxx, gyy, gxx_x, gxx_y, gyy_x, gyy_y, W_x, W_y, W = self.F(s[0], s[1], E, L)
        return [gxx * s[2], gyy * s[3], -(gxx_x * s[2] ** 2 + gyy_x * s[3] ** 2 + W_x) / 2,
                -(gxx_y * s[2] ** 2 + gyy_y * s[3] ** 2 + W_y) / 2]

    def orbit(self, x0, E, L, tol, nsec, k=14, tmax=5e6, xmin=1.5, xmax=2000.0, ymax=0.999999, hmax0=20.0,
              maxsteps=10_000_000):
        mp = self.mp
        mp.mp.dps = self.dps
        Er, Lr = sp.Rational(E), sp.Rational(L)
        Em, Lm = mp.mpf(Er.p) / Er.q, mp.mpf(Lr.p) / Lr.q
        x0m = mp.mpf(float(x0))
        v = self.F(x0m, mp.mpf(0), Em, Lm)
        q = (-1 - v[8]) / v[1]
        if q <= 0:
            return dict(status=-1, n=0, t_end=0.0, steps=0)
        s = [x0m, mp.mpf(0), mp.mpf(0), mp.sqrt(q)]
        t, h, ns, status, steps, t_last, dtc = mp.mpf(0), mp.mpf("0.05"), 0, 0, 0, mp.mpf(0), mp.mpf("1e300")
        tolm = mp.mpf(tol)
        expo = mp.mpf(1) / (2 * k - 1)
        while ns < nsec and t < tmax:
            if steps >= maxsteps:
                status = 3
                break
            h = min(h, min(mp.mpf(hmax0), dtc / 10))
            f0 = self._rhs(s, Em, Lm)
            T = []
            for j in range(k):
                nj = 2 * (j + 1)
                hs = h / nj
                zp, z = list(s), [s[i] + hs * f0[i] for i in range(4)]
                for _ in range(nj - 1):
                    fz = self._rhs(z, Em, Lm)
                    zp, z = z, [zp[i] + 2 * hs * fz[i] for i in range(4)]
                fz = self._rhs(z, Em, Lm)
                row = [[(z[i] + zp[i] + hs * fz[i]) / 2 for i in range(4)]]
                for m in range(1, j + 1):
                    nm = 2 * (j - m + 1)
                    r = mp.mpf(nj * nj - nm * nm) / (nm * nm)
                    row.append([row[m - 1][i] + (row[m - 1][i] - T[j - 1][m - 1][i]) / r for i in range(4)])
                T.append(row)
            new = T[k - 1][k - 1]
            e = max(abs(new[i] - T[k - 1][k - 2][i]) / (tolm * (1 + max(abs(s[i]), abs(new[i])))) for i in range(4))
            if e <= 1:
                y0, y1 = s[1], new[1]
                s = new
                t += h
                steps += 1
                if y0 < 0 <= y1 and s[3] > 0:
                    if ns > 0:
                        dtc = t - t_last
                    t_last = t
                    ns += 1
                if s[0] < xmin:
                    status = 1
                    break
                if s[0] > xmax or abs(s[1]) > ymax:
                    status = 2
                    break
            fac = mp.mpf("0.94") * (1 / e) ** expo if e > 0 else mp.mpf(4)
            h *= min(mp.mpf(4), max(mp.mpf("0.2"), fac))
        return dict(status=status, n=ns, t_end=float(t), steps=steps)


def mp_state_at(m, x0, E, L, T, tol=1e-40, k=14, hmax0=20.0):
    """G4 (addendum 2): the mpmath twin of dd_state_at."""
    mp = m.mp
    mp.mp.dps = m.dps
    Er, Lr = sp.Rational(E), sp.Rational(L)
    Em, Lm = mp.mpf(Er.p) / Er.q, mp.mpf(Lr.p) / Lr.q
    x0m = mp.mpf(float(x0))
    v = m.F(x0m, mp.mpf(0), Em, Lm)
    s = [x0m, mp.mpf(0), mp.mpf(0), mp.sqrt((-1 - v[8]) / v[1])]
    t, h, Tm, tolm = mp.mpf(0), mp.mpf("0.05"), mp.mpf(float(T)), mp.mpf(tol)
    expo = mp.mpf(1) / (2 * k - 1)
    while t < Tm:
        h = min(h, mp.mpf(hmax0))
        clipped = h >= Tm - t
        if clipped:
            h = Tm - t
        f0 = m._rhs(s, Em, Lm)
        Tab = []
        for j in range(k):
            nj = 2 * (j + 1)
            hs = h / nj
            zp, z = list(s), [s[i] + hs * f0[i] for i in range(4)]
            for _ in range(nj - 1):
                fz = m._rhs(z, Em, Lm)
                zp, z = z, [zp[i] + 2 * hs * fz[i] for i in range(4)]
            fz = m._rhs(z, Em, Lm)
            row = [[(z[i] + zp[i] + hs * fz[i]) / 2 for i in range(4)]]
            for q in range(1, j + 1):
                nm = 2 * (j - q + 1)
                r = mp.mpf(nj * nj - nm * nm) / (nm * nm)
                row.append([row[q - 1][i] + (row[q - 1][i] - Tab[j - 1][q - 1][i]) / r for i in range(4)])
            Tab.append(row)
        new = Tab[k - 1][k - 1]
        e = max(abs(new[i] - Tab[k - 1][k - 2][i]) / (tolm * (1 + max(abs(s[i]), abs(new[i])))) for i in range(4))
        if not mp.isfinite(e) or not mp.isfinite(new[0]):
            return None                            # non-finite (addendum 3)
        if e <= 1:
            s = new
            if s[0] < mp.mpf("1.5"):
                return None                        # plunge before T (addendum 3)
            if clipped:
                t = Tm
                break
            t += h
        fac = mp.mpf("0.94") * (1 / e) ** expo if e > 0 else mp.mpf(4)
        h *= min(mp.mpf(4), max(mp.mpf("0.2"), fac))
    return s
