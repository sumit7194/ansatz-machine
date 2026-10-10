#!/usr/bin/env python3
"""Fast geodesic-chaos engine for stationary axisymmetric metrics (TS delta=2, Kerr, ZV) -- data/ts_chaos/PREREGISTRATION.md.

Reduced 2-DOF Hamiltonian with p_t = -E, p_phi = L frozen, timelike (mu = 1):
    H = 1/2 [ g^xx p_x^2 + g^yy p_y^2 + W(x, y) ],   W = g^tt E^2 - 2 g^tphi E L + g^phiphi L^2,   H = -1/2.
The RHS is generated from the EXACT rational inverse metric: sympy -> CSE -> a generated module file in
data/ts_chaos/gen/ -> imported -> numba njit. Integration is adaptive Dormand-Prince 5(4) with a TANGENT vector carried
in the same step (8-dim state), so the finite-time Lyapunov exponent comes for free. The Poincare section is y = 0
crossed with p_y > 0; at each crossing (x, p_x) and the proper time are recorded, by cubic Hermite interpolation.

Diagnostics per orbit:
  - frequency drift of the x-section sequence (poincare.frequency_drift, threshold 0.0115)
  - FTLE(t) = (1/t) sum ln(d_k/d0) with renormalisation every dt_ren, and the SLOPE of log FTLE vs log t over the
    last decade (~ -1 regular, plateau chaotic)
  - lifetime: crossings before plunge (x < xmin) or escape (x > xmax)
  - mass-shell drift max |2H + 1|
"""
import hashlib
import importlib.util
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402
import numba  # noqa: E402

import _kt_metrics as MM  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "data", "ts_chaos", "gen")
x, y = MM.x, MM.y
E_, L_ = sp.symbols("E L", real=True)


def build_rhs(ginv, name):
    """numba-compiled f(x, y, E, L) -> (gxx, gyy, gxx_x, gxx_y, gyy_x, gyy_y, W_x, W_y, W)."""
    from sympy.printing.pycode import pycode
    gxx, gyy = sp.cancel(ginv[1, 1]), sp.cancel(ginv[2, 2])
    W = sp.together(ginv[0, 0] * E_**2 - 2 * ginv[0, 3] * E_ * L_ + ginv[3, 3] * L_**2)
    exprs = [gxx, gyy, sp.diff(gxx, x), sp.diff(gxx, y), sp.diff(gyy, x), sp.diff(gyy, y), sp.diff(W, x), sp.diff(W, y), W]
    key = hashlib.sha256(sp.srepr(sp.Matrix(exprs)).encode()).hexdigest()[:16]
    os.makedirs(GEN, exist_ok=True)
    path = os.path.join(GEN, f"rhs_{key}.py")
    t0 = time.time()
    if not os.path.exists(path):
        reps, red = sp.cse(exprs, optimizations="basic")
        lines = [f"# generated from the exact inverse metric of: {name}", "import math", "", "def f(x, y, E, L):"]
        for s_, e_ in reps:
            lines.append(f"    {s_} = {pycode(e_, fully_qualified_modules=True)}")
        lines.append("    return (" + ", ".join(pycode(e_, fully_qualified_modules=True) for e_ in red) + ",)")
        with open(path, "w") as fh:
            fh.write("\n".join(lines) + "\n")
    spec = importlib.util.spec_from_file_location(f"rhs_{key}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print(f"  [{name}] rhs module {os.path.basename(path)} [{time.time()-t0:.0f}s]", flush=True)
    return numba.njit(mod.f)


def make_integrator(f):
    @numba.njit
    def rhs(s, E, L):
        gxx, gyy, gxx_x, gxx_y, gyy_x, gyy_y, W_x, W_y, W = f(s[0], s[1], E, L)
        return np.array([gxx * s[2], gyy * s[3],
                         -0.5 * (gxx_x * s[2] ** 2 + gyy_x * s[3] ** 2 + W_x),
                         -0.5 * (gxx_y * s[2] ** 2 + gyy_y * s[3] ** 2 + W_y)])

    @numba.njit
    def shell(s, E, L):
        gxx, gyy, gxx_x, gxx_y, gyy_x, gyy_y, W_x, W_y, W = f(s[0], s[1], E, L)
        return gxx * s[2] ** 2 + gyy * s[3] ** 2 + W            # = 2H, should be -1

    @numba.njit
    def rhs8(S, E, L):
        """Orbit + TANGENT vector: v' = J(s) v, with J v from a central difference of the VECTOR FIELD along v
        (step 1e-6 in the unit direction; error O(1e-12)). A shadow ORBIT would instead carry the integrator's own
        truncation noise into the separation (measured: it fakes a positive FTLE on regular tori)."""
        out = np.empty(8)
        s = S[:4]
        out[:4] = rhs(s, E, L)
        v = S[4:]
        nv = math.sqrt((v ** 2).sum())
        if nv == 0.0:
            out[4:] = 0.0
            return out
        u = v / nv
        eps = 1e-6
        out[4:] = (rhs(s + eps * u, E, L) - rhs(s - eps * u, E, L)) * (nv / (2.0 * eps))
        return out

    a21 = 1 / 5
    a31, a32 = 3 / 40, 9 / 40
    a41, a42, a43 = 44 / 45, -56 / 15, 32 / 9
    a51, a52, a53, a54 = 19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729
    a61, a62, a63, a64, a65 = 9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656
    b1, b3, b4, b5, b6 = 35 / 384, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84
    e1, e3, e4, e5, e6, e7 = 71 / 57600, -71 / 16695, 71 / 1920, -17253 / 339200, 22 / 525, -1 / 40

    @numba.njit
    def run(s0, E, L, tol, nsec, tmax, xmin, xmax, d0, dt_ren, ymax, maxsteps):
        """status 0 = reached nsec or tmax, 1 = plunge (x < xmin), 2 = escape (x > xmax or |y| > ymax),
        3 = step failure or step cap (maxsteps) -- reported, never silently counted as regular."""
        S = np.empty(8)
        S[:4] = s0
        pert = np.array([1.0, 0.7, -0.4, 0.3])
        pert = pert / math.sqrt((pert ** 2).sum())
        S[4:] = pert                      # unit tangent vector (d0 is unused with the tangent method)
        t = 0.0
        h = 1e-3
        secx = np.empty(nsec); secpx = np.empty(nsec); sect = np.empty(nsec)
        ns = 0
        nft = int(tmax / dt_ren) + 2
        ft_t = np.empty(nft); ft_v = np.empty(nft)
        nf = 0
        lsum = 0.0
        t_next_ren = dt_ren
        maxdrift = 0.0
        status = 0
        nsteps = 0
        k1 = rhs8(S, E, L)
        while ns < nsec and t < tmax:
            if nsteps > maxsteps:
                status = 3
                break
            k2 = rhs8(S + h * (a21 * k1), E, L)
            k3 = rhs8(S + h * (a31 * k1 + a32 * k2), E, L)
            k4 = rhs8(S + h * (a41 * k1 + a42 * k2 + a43 * k3), E, L)
            k5 = rhs8(S + h * (a51 * k1 + a52 * k2 + a53 * k3 + a54 * k4), E, L)
            k6 = rhs8(S + h * (a61 * k1 + a62 * k2 + a63 * k3 + a64 * k4 + a65 * k5), E, L)
            Sn = S + h * (b1 * k1 + b3 * k3 + b4 * k4 + b5 * k5 + b6 * k6)
            k7 = rhs8(Sn, E, L)
            err_v = h * (e1 * k1 + e3 * k3 + e4 * k4 + e5 * k5 + e6 * k6 + e7 * k7)
            sc = tol * (1.0 + np.maximum(np.abs(S), np.abs(Sn)))
            err = math.sqrt(((err_v / sc) ** 2).mean())
            if not (err == err):
                h *= 0.1
                if h < 1e-14:
                    status = 3
                    break
                continue
            if err <= 1.0:
                y0, y1 = S[1], Sn[1]
                if y0 < 0.0 <= y1 and Sn[3] > 0:
                    lo, hi = 0.0, 1.0
                    for _ in range(40):
                        mid = 0.5 * (lo + hi)
                        h00 = 2 * mid ** 3 - 3 * mid ** 2 + 1
                        h10 = mid ** 3 - 2 * mid ** 2 + mid
                        h01 = -2 * mid ** 3 + 3 * mid ** 2
                        h11 = mid ** 3 - mid ** 2
                        ym = h00 * y0 + h10 * h * k1[1] + h01 * y1 + h11 * h * k7[1]
                        if ym < 0:
                            lo = mid
                        else:
                            hi = mid
                    u = 0.5 * (lo + hi)
                    h00 = 2 * u ** 3 - 3 * u ** 2 + 1
                    h10 = u ** 3 - 2 * u ** 2 + u
                    h01 = -2 * u ** 3 + 3 * u ** 2
                    h11 = u ** 3 - u ** 2
                    secx[ns] = h00 * S[0] + h10 * h * k1[0] + h01 * Sn[0] + h11 * h * k7[0]
                    secpx[ns] = h00 * S[2] + h10 * h * k1[2] + h01 * Sn[2] + h11 * h * k7[2]
                    sect[ns] = t + u * h
                    ns += 1
                S = Sn
                t += h
                k1 = k7
                nsteps += 1
                dr = abs(shell(S[:4], E, L) + 1.0)
                if dr > maxdrift:
                    maxdrift = dr
                if S[0] < xmin:
                    status = 1
                    break
                if S[0] > xmax or abs(S[1]) > ymax:
                    status = 2
                    break
                if t >= t_next_ren:
                    d = math.sqrt((S[4:] ** 2).sum())
                    if d > 0:
                        lsum += math.log(d)
                        S[4:] = S[4:] / d
                        k1 = rhs8(S, E, L)
                    if nf < nft:
                        ft_t[nf] = t
                        ft_v[nf] = lsum / t
                        nf += 1
                    t_next_ren += dt_ren
            fac = 0.9 * err ** (-0.2) if err > 0 else 5.0
            h *= min(5.0, max(0.2, fac))
        return secx[:ns], secpx[:ns], sect[:ns], ft_t[:nf], ft_v[:nf], status, maxdrift, nsteps

    return run, shell


def ftle_slope(ft_t, ft_v):
    """Slope of log FTLE vs log t over the last decade of t (needs positive FTLE values)."""
    if len(ft_t) < 20:
        return float("nan")
    tmax = ft_t[-1]
    m = (ft_t >= tmax / 10) & (ft_v > 0)
    if m.sum() < 10:
        return float("nan")
    return float(np.polyfit(np.log(ft_t[m]), np.log(ft_v[m]), 1)[0])


class Engine:
    def __init__(self, ginv, name):
        self.name = name
        self.f = build_rhs(ginv, name)
        self.run, self.shell = make_integrator(self.f)
        self._W = sp.lambdify((x, y, E_, L_), ginv[0, 0] * E_**2 - 2 * ginv[0, 3] * E_ * L_ + ginv[3, 3] * L_**2, "math")
        self._gyy = sp.lambdify((x, y), ginv[2, 2], "math")
        self._gxx = sp.lambdify((x, y), ginv[1, 1], "math")

    def W(self, x0, y0, E, L):
        return self._W(x0, y0, E, L)

    def py_on_shell(self, x0, px0, E, L):
        """p_y > 0 at (x0, y=0, px0) on the mass shell; None if forbidden there."""
        val = (-1.0 - self._W(x0, 0.0, E, L) - self._gxx(x0, 0.0) * px0 * px0) / self._gyy(x0, 0.0)
        return math.sqrt(val) if val > 0 else None

    def orbit(self, x0, E, L, px0=0.0, tol=1e-11, nsec=400, tmax=2e6, xmin=1.0, xmax=1e3, d0=1e-9, dt_ren=10.0,
              ymax=0.999999, maxsteps=3_000_000):
        from poincare import frequency_drift
        py0 = self.py_on_shell(x0, px0, E, L)
        if py0 is None:
            return None
        s0 = np.array([x0, 0.0, px0, py0])
        sx, spx, st, ft, fv, status, drift, nst = self.run(s0, E, L, tol, nsec, tmax, xmin, xmax, d0, dt_ren, ymax, maxsteps)
        fd = frequency_drift(list(sx)) if len(sx) >= 100 else float("nan")
        return dict(x0=x0, E=E, L=L, n=len(sx), secx=sx, secpx=spx, status=int(status), drift=float(drift),
                    fd=float(fd), slope=ftle_slope(ft, fv), ftle_final=float(fv[-1]) if len(fv) else float("nan"),
                    sex=float(fv[-1] * ft[-1] - math.log(ft[-1])) if len(fv) else float("nan"),
                    steps=int(nst), t_end=float(st[-1]) if len(st) else 0.0)
