"""Complex-k version of the §159 lower-axis problem, for gap B (argument-principle zero count of F(k) = tr[M1, M0] - 2).
The radicand numerator is linear in k: R = (N0 + k N1) / D^6. So the Laurent data of c0 are built once, and each
complex k costs only a series square root. Branch: principal sqrt of the leading radicand coefficient, which is
continuous off k in [30/7, inf). Reuses _nve_lower's Walker/taylor/find_zeros unchanged.
    .venv/bin/python scripts/_nve_lower_kc.py measure     # timing + reproduction of lower_comm at real k (control C0)
"""
import json
import os
import sys
import time

import mpmath as mp
import numpy as np
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _nve_lower import Problem, Walker, arc, find_zeros, A, z, OUT, RIN, poly_mp, pder   # noqa: E402
from _nve_monodromy import comm                                                         # noqa: E402

mp.mp.dps = 50
ks = sp.symbols("k")


def _radicand_sym():
    D = z**2 + A**2
    cK2 = sp.diff(-2 * A / D, z, 2)
    v = (z + sp.I * A) / (z - sp.I * A)
    Q = sp.together(sp.expand(v**3 + v**-3 - sp.Rational(3, 5) * (v + 1 / v) - sp.Rational(4, 5)))
    N, Dn = sp.fraction(sp.cancel(sp.together(cK2**2 + ks * Q / D**3)))
    Np = sp.Poly(sp.expand(N), z, ks)
    N0 = sp.Poly(sp.expand(N.subs(ks, 0)), z)
    N1 = sp.Poly(sp.expand(sp.diff(N, ks)), z)
    assert sp.expand(N - N0.as_expr() - ks * N1.as_expr()) == 0, "numerator not linear in k"
    return N0, N1, sp.Poly(sp.expand(Dn), z)


N0, N1, DEN = _radicand_sym()


def _asc(P, deg):
    c = [mp.mpc(sp.N(x, 60)) for x in reversed(P.all_coeffs())]
    return c + [mp.mpc(0)] * (deg + 1 - len(c))


def c0_laurent_c(k, NW=None):
    """Complex k. -> (C, rho, NW). Same construction and branch convention as _nve_lower.c0_laurent."""
    k = mp.mpc(k)
    dN = max(N0.degree(), N1.degree())
    nc = [x + k * y for x, y in zip(_asc(N0, dN), _asc(N1, dN))]
    while abs(nc[-1]) < mp.mpf(10) ** -40:
        nc.pop()
    dc = _asc(DEN, DEN.degree())
    # rho only sets NW and is a guard: double precision suffices (numerator has double roots at k = 0;
    # the denominator is (z^2 + a^2)^6, poles exactly +-ia)
    zeros = np.roots([complex(x) for x in reversed(nc)])
    rho = mp.mpf(max([float(A)] + [abs(q) for q in zeros]))
    if NW is None:      # series must converge to 45 digits at radius RIN (0.9, as registered in §159) or, when the
        rmin = RIN if rho < mp.mpf("0.85") else mp.mpf("1.3")    # radicand roots grow (k near 30/7), at 1.3
        if rho >= mp.mpf("1.15"):
            raise RuntimeError(f"rho_c = {rho} too large for loops at |z| >= 1.35")
        NW = int(45 * mp.log(10) / mp.log(rmin / rho)) + 20
    dN, dD = len(nc) - 1, len(dc) - 1
    L = NW + 12
    Nrev = [nc[dN - j] for j in range(dN + 1)] + [mp.mpc(0)] * L
    Drev = [dc[dD - j] for j in range(dD + 1)] + [mp.mpc(0)] * L
    S = [mp.mpc(0)] * L
    for j in range(L):
        S[j] = (Nrev[j] - mp.fsum(S[i] * Drev[j - i] for i in range(j))) / Drev[0]
    j0 = next(j for j in range(L) if abs(S[j]) > mp.mpf(10) ** (-40))
    if dD - dN + j0 != 8:
        raise RuntimeError("radicand leading power != w^8")
    Sa = S[j0:]
    B = [mp.mpc(0)] * NW
    B[0] = -mp.sqrt(Sa[0])
    for j in range(1, NW):
        B[j] = (Sa[j] - mp.fsum(B[i] * B[j - i] for i in range(1, j))) / (2 * B[0])
    C = [mp.mpc(0)] * (NW + 3)
    for jj in range(NW):
        n = jj + 4
        C[n - 2] = B[jj] / ((n - 1) * (n - 2))
    return C, rho, NW


class ProblemC(Problem):
    def __init__(self, f0, k, E2):
        n, g = sp.fraction(sp.cancel(sp.together(f0)))
        self.n, self.g = poly_mp(n), poly_mp(g)
        self.dn, self.dg = pder(self.n), pder(self.g)
        self.C, self.rho, self.NW = c0_laurent_c(k)
        self.E2 = mp.mpf(sp.N(E2, 60))


def rect(x0, x1, y0, y1, b=mp.mpf("1.35")):
    c = [mp.mpc(x0, 0), mp.mpc(x0, y0), mp.mpc(x1, y0), mp.mpc(x1, y1), mp.mpc(x0, y1), mp.mpc(x0, 0)]
    return [mp.mpc(b, 0)] + c + [mp.mpc(b, 0)]


I2 = lambda: [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]]
FK = 1 - 1 / (z - sp.I * A) - 1 / (z + sp.I * A)
M1_PATH = rect(1.6, 2.4, -0.3, 0.9)
M0_PATH = arc(mp.mpf("1.35"), 0, 2 * mp.pi)


def newton(pr, x, which, tol=mp.mpf(10) ** -45):
    for _ in range(100):
        G1, dG1, G2, dG2 = pr.G(x)
        F, dF = (G1, dG1) if which == 1 else (G2, dG2)
        dx = F / dF
        x -= dx
        if abs(dx) < tol:
            return x
    raise RuntimeError("newton did not converge")


def seg_dist(c, A_, B_):
    ab = B_ - A_
    t = max(0, min(1, float(mp.re((c - A_) * mp.conj(ab)) / (abs(ab) ** 2 + mp.mpf(10) ** -60))))
    return abs(A_ + t * ab - c)


def path_dist(c, path):
    return min(seg_dist(c, A_, B_) for A_, B_ in zip(path[:-1], path[1:]))


def capsule_lasso(r, p, others, b=mp.mpf("1.35"), dmax=mp.mpf("0.15"), npts=24):
    """Based lasso around the segment [r, p]: straight tail from b to the capsule point nearest b, the capsule
    (all points at distance delta from [r, p]) once counter-clockwise, and back. delta = min(dmax, 0.4 * clearance)."""
    clear = min(seg_dist(c, r, p) for c in others)
    delta = min(dmax, mp.mpf("0.4") * clear)
    e = (p - r) / abs(p - r)
    th = mp.arg(e)
    cap = [p + delta * mp.expj(th - mp.pi / 2 + mp.pi * j / npts) for j in range(npts + 1)]
    cap += [r + delta * mp.expj(th + mp.pi / 2 + mp.pi * j / npts) for j in range(npts + 1)]     # CCW polygon
    i0 = min(range(len(cap)), key=lambda i: abs(cap[i] - b))
    ring = cap[i0:] + cap[:i0] + [cap[i0]]
    return [mp.mpc(b)] + ring + [mp.mpc(b)], delta


def F_of_k(k, E=sp.Rational(4, 5), step="0.35"):
    pr = ProblemC(FK, k, E**2)
    z1, _ = find_zeros(pr, 1)
    z2, _ = find_zeros(pr, 2)
    W = Walker(pr, z1 + z2, step)
    M0 = W.walk(M0_PATH, I2())
    M1 = W.walk(M1_PATH, I2())
    C = comm(M1, M0)
    return dict(F=C[0][0] + C[1][1] - 2, trM0m2=M0[0][0] + M0[1][1] - 2, trM1=M1[0][0] + M1[1][1],
                sing=z1 + z2, rho=pr.rho, NW=pr.NW)


if __name__ == "__main__" and sys.argv[1:] == ["measure"]:
    for k, st in ((mp.mpf(1) / 10, "0.35"), (mp.mpc("0.1", "0.5"), "0.35"), (mp.mpc("0.1", "0.5"), "0.2")):
        t0 = time.time()
        r = F_of_k(k, step=st)
        print(dict(k=str(k), step=st, F=mp.nstr(r["F"], 18), trM0m2=mp.nstr(r["trM0m2"], 12),
                   trM1=mp.nstr(r["trM1"], 12), rho=mp.nstr(r["rho"], 4), NW=r["NW"],
                   sing=[mp.nstr(c, 6) for c in r["sing"]], sec=round(time.time() - t0, 1)), flush=True)
    print("reference (lower_comm, k=1/10): F = 0.00196656555091338 + 0.00101256196325471j")
