#!/usr/bin/env python3
"""EXP-003 -- a 5D Lorentzian vacuum member of the family: the coupling a of the 4D pp-wave is
oxidised into a momentum p_v by adding a gyratonic term 2A dt dv + dv^2 with A = 2 kappa xi/rho^2
(= kappa (z^{-1/2} + zbar^{-1/2})), and the profile U is re-solved from R_ab = 0.

WHY NOT CG eq. 26. CG's rank-4 metrics descend from Drach's FIRST system, U = alpha y + gamma/sqrt(x)
- (alpha x)^2/2, which is not symmetric under x <-> y (U_yy = 0 != U_xx) and carries the cross term
2 alpha x dt dw; under x = z, y = zbar none of it is real. In 4D the obstruction is invariant: CG
state the first-system metric is anti-self-dual, and a non-flat ASD (2,2) metric has no Lorentzian
real form (W^- = 0 would force W = 0). Their symmetric-system oxidations (eq. 33, 35) fail
differently: dw^2 + du^2 becomes 2(dchi^2 - dpsi^2) under w = conj(u).

WHAT IS DONE HERE. Metric in coordinates (t, xi, eta, s, v):
    ds^2 = -2U dt^2 + 2 dt ds + 2A dt dv + dv^2 + 8 rho^2 (dxi^2 + deta^2),
    A = 2 kappa xi / rho^2,   U = 2 a xi/rho^2 - lam A^2 + 2 mu (xi^2 - eta^2)/rho^4.
lam is fixed by R_ab = 0 (the gauge field's energy must be absorbed), mu is a free harmonic
admixture chosen so the reduced 2D system is Smorodinsky-Winternitz IV again (now with sigma != 0).
Then the two parabolic separation constants Q1, Q2 and F = {Q1, Q2} are built and the checks of
EXP-002 are repeated: Ricci-flat, signature, {H,F} = 0, dim K1 by jets, pure part, functional rank.
Run:  ../conjecture_machine/.venv/bin/python scripts/exp003_5d_gyraton.py
"""
import itertools
import random
import time

import sympy as sp
from sympy import Rational as Q_

T0 = time.time()


def log(msg=""):
    print(f"[{time.time()-T0:7.1f}s] {msg}", flush=True)


t, xi, eta, s, v = sp.symbols("t xi eta s v", real=True)
pt, pxi, peta, ps, pv = sp.symbols("p_t p_xi p_eta p_s p_v", real=True)
a, kap, lam, mu = sp.symbols("a kappa lam mu", real=True)
XS = [t, xi, eta, s, v]
PS = [pt, pxi, peta, ps, pv]
N = 5
rho2 = xi**2 + eta**2
A = 2 * kap * xi / rho2
U = 2 * a * xi / rho2 - lam * A**2 + 2 * mu * (xi**2 - eta**2) / rho2**2

g = sp.zeros(N, N)
g[0, 0] = -2 * U
g[0, 3] = g[3, 0] = 1
g[0, 4] = g[4, 0] = A
g[4, 4] = 1
g[1, 1] = g[2, 2] = 8 * rho2


def christoffel(g, ginv):
    return [[[sp.cancel(Q_(1, 2) * sum(ginv[i, l] * (sp.diff(g[l, j], XS[k]) + sp.diff(g[l, k], XS[j])
                                                       - sp.diff(g[j, k], XS[l])) for l in range(N)))
              for k in range(N)] for j in range(N)] for i in range(N)]


def ricci(g):
    ginv = g.inv().applyfunc(sp.cancel)
    Gam = christoffel(g, ginv)
    Rup = [[[[sp.cancel(sp.diff(Gam[i][l][j], XS[k]) - sp.diff(Gam[i][k][j], XS[l])
                        + sum(Gam[i][k][m] * Gam[m][l][j] - Gam[i][l][m] * Gam[m][k][j] for m in range(N)))
              for l in range(N)] for k in range(N)] for j in range(N)] for i in range(N)]
    Ric = sp.Matrix(N, N, lambda j, l: sp.cancel(sum(Rup[i][j][i][l] for i in range(N))))
    return ginv, Gam, Rup, Ric


log("STEP 1: fix lam from R_ab = 0 (symbolic a, kappa, mu)")
ginv, Gam, Rup, Ric = ricci(g)
nz = {(i, j): sp.factor(Ric[i, j]) for i in range(N) for j in range(i, N) if Ric[i, j] != 0}
log(f"  nonzero Ricci components before fixing lam: { {k: str(v_) for k, v_ in nz.items()} }")
sols = sp.solve([sp.numer(sp.together(e)) for e in nz.values()], lam, dict=True)
log(f"  lam solutions: {sols}")
LAM = sols[0][lam]
g = g.subs(lam, LAM)
U = U.subs(lam, LAM)
ginv, Gam, Rup, Ric = ricci(g)
log(f"  Ricci identically zero with lam = {LAM}: {Ric == sp.zeros(N, N)}  (a, kappa, mu symbolic)")
riem_nz = [(i, j, k, l) for i in range(N) for j in range(N) for k in range(N) for l in range(N) if Rup[i][j][k][l] != 0]
log(f"  Riemann nonzero components: {len(riem_nz)}")
log(f"  signature: (t,s) block det = {sp.cancel(g.extract([0,3],[0,3]).det())}; v-direction +1; transverse 8 rho^2 I  ->  (1,4)")
import numpy as np
ev = sorted(np.linalg.eigvalsh(np.array(g.subs({a: 1, kap: 1, mu: 1, xi: Q_(5, 3), eta: Q_(7, 4)}).evalf(), dtype=float)))
log(f"  numeric eigenvalues at a=kappa=mu=1, (xi,eta)=(5/3,7/4): {[round(float(e), 4) for e in ev]}")

log("STEP 2: the reduced 2D system and the choice of mu")
H = sp.expand(Q_(1, 2) * sum(ginv[i, j] * PS[i] * PS[j] for i in range(N) for j in range(N)))
# H = (p_xi^2 + p_eta^2)/(16 rho^2) + K0(p) + Veff(xi,eta;p);  every position-dependent term carries a, kappa or mu
kin = (pxi**2 + peta**2) / (16 * rho2)
rest = sp.cancel(sp.together(H - kin))
K0 = sp.expand(rest.subs({a: 0, kap: 0, mu: 0}))
log(f"  K0 = {K0}")
Veff = sp.cancel(sp.together(rest - K0))
log(f"  V_eff = {sp.factor(Veff)}")
# SW-IV form needs rho^2 V_eff to be a polynomial of degree <= 1 in (xi, eta); fix mu by divisibility
num, den = sp.fraction(sp.cancel(sp.together(rho2 * Veff)))
qpoly, rpoly = sp.div(sp.Poly(sp.expand(num), xi, eta), sp.Poly(sp.expand(den), xi, eta))
musol = sp.solve(rpoly.coeffs(), mu, dict=True)
log(f"  remainder of rho^2 V_eff on division by its denominator vanishes for mu = {musol}")
MU = musol[0][mu]
g = g.subs(mu, MU); U = U.subs(mu, MU); ginv = ginv.subs(mu, MU); H = sp.expand(H.subs(mu, MU))
fg = sp.expand(sp.cancel(sp.together((rho2 * Veff).subs(mu, MU))))
log(f"  with mu = {MU}:  rho^2 V_eff = f(xi) + g(eta) = {fg}")
assert sp.Poly(fg, xi, eta).total_degree() <= 1
sigma = fg.subs({xi: 0, eta: 0})
fxi = sp.expand(fg.coeff(xi, 1) * xi + sigma)      # constant assigned to f
geta = sp.expand(fg.coeff(eta, 1) * eta)
log(f"  SW-IV form (sigma + a' xi + b' eta)/rho^2:  sigma = {sp.factor(sigma)},  a' = {sp.factor(fg.coeff(xi, 1))},  b' = {fg.coeff(eta, 1)}")


def poisson(Aa, Bb):
    return sp.expand(sum(sp.diff(Aa, XS[i]) * sp.diff(Bb, PS[i]) - sp.diff(Aa, PS[i]) * sp.diff(Bb, XS[i]) for i in range(N)))


def is_zero(e):
    return sp.cancel(sp.together(sp.expand(e))) == 0


log("STEP 3: Q1, Q2, F")
Hb = H - K0
Q1 = sp.expand(pxi**2 / 16 + fxi - xi**2 * Hb)
# rotated parabolic system xi' = (xi - eta)/sqrt2: f'(xi') + g'(eta') from  f + g  rewritten
xp, ep = sp.symbols("xip etap")
fg_rot = sp.expand(fg.subs({xi: (xp + ep) / sp.sqrt(2), eta: (ep - xp) / sp.sqrt(2)}, simultaneous=True))
fxp = sp.expand(fg_rot.coeff(xp, 1) * xp + fg_rot.subs({xp: 0, ep: 0}))
Q2 = sp.expand((fxp.subs(xp, (xi - eta) / sp.sqrt(2))) + (pxi - peta)**2 / 32 - Q_(1, 2) * (xi - eta)**2 * Hb)
log(f"  {{H,Q1}} = 0: {is_zero(poisson(H, Q1))}   {{H,Q2}} = 0: {is_zero(poisson(H, Q2))}")
F = sp.expand(sp.cancel(sp.together(-4 * poisson(Q1, Q2))))
log(f"  F := -4{{Q1,Q2}} nonzero: {F != 0};   {{H,F}} = 0: {is_zero(poisson(H, F))}")
pure = sp.expand(F.subs({pt: 0, ps: 0, pv: 0}))
log(f"  pure (p_xi,p_eta)-cubic part of F: {sp.factor(pure)}")
log(f"  F|kappa=0 (must be the 4D object) = {sp.collect(F.subs(kap, 0), PS)}")

log("STEP 4: dim K1 by the jet count (a = kappa = 1)")
num = {a: 1, kap: 1}
g1 = g.subs(num); ginv1 = ginv.subs(num); Gam1 = [[[e.subs(num) for e in r] for r in m] for m in Gam]
Rd = sp.MutableDenseNDimArray([[[[sp.cancel(sum(g1[i, m] * Rup[m][j][k][l].subs(num) for m in range(N)))
                                  for l in range(N)] for k in range(N)] for j in range(N)] for i in range(N)])


def cov_deriv(T, rank):
    out = sp.MutableDenseNDimArray.zeros(*([N] * (rank + 1)))
    for idx in itertools.product(range(N), repeat=rank):
        for e in range(N):
            val = sp.diff(T[idx], XS[e])
            for pos in range(rank):
                for f in range(N):
                    gam = Gam1[f][e][idx[pos]]
                    if gam != 0:
                        jdx = list(idx); jdx[pos] = f
                        val -= gam * T[tuple(jdx)]
            out[idx + (e,)] = val
    return out


DR = cov_deriv(Rd, 4)
log("  nabla R built")
xv = sp.symbols("v0:5")
om = {}
for i in range(N):
    for j in range(i + 1, N):
        om[(i, j)] = sp.Symbol(f"w{i}{j}"); om[(j, i)] = -om[(i, j)]
    om[(i, i)] = 0
unk = list(xv) + [om[(i, j)] for i in range(N) for j in range(i + 1, N)]


def lie_rows(T, rank, pt0):
    gi0 = ginv1.subs(pt0)
    T0 = T.applyfunc(lambda e: e.subs(pt0))
    DT0 = cov_deriv(T, rank).applyfunc(lambda e: e.subs(pt0))
    dxi_up = [[sum(gi0[b, c] * om[(aa, c)] for c in range(N)) for b in range(N)] for aa in range(N)]
    rows = []
    for idx in itertools.product(range(N), repeat=rank):
        val = sum(xv[e] * DT0[idx + (e,)] for e in range(N))
        for pos in range(rank):
            for e in range(N):
                jdx = list(idx); jdx[pos] = e
                val += T0[tuple(jdx)] * dxi_up[idx[pos]][e]
        val = sp.expand(val)
        if val != 0:
            rows.append([val.coeff(u_) for u_ in unk])
    return rows


for pt0 in ({xi: Q_(5, 3), eta: Q_(7, 4), t: 0, s: 0, v: 0}, {xi: Q_(-2, 7), eta: Q_(9, 5), t: 0, s: 0, v: 0}):
    rows = lie_rows(Rd, 4, pt0)
    rk = sp.Matrix(rows).rank()
    log(f"  point ({pt0[xi]},{pt0[eta]}): L_xi R -> rank {rk}, admissible jets {15-rk}")
    rows += lie_rows(DR, 5, pt0)
    rk = sp.Matrix(rows).rank()
    log(f"     + L_xi nabla R -> rank {rk}, admissible jets {15-rk}")
    kv_bound = 15 - rk
log(f"  => dim K1 <= {kv_bound}; d_t, d_s, d_v are Killing" + (" -> dim K1 = 3 exactly" if kv_bound == 3 else " -> NOT closed"))
log(f"  polynomial irreducibility: every reducible rank-3 carries p_t, p_s or p_v; pure part of F nonzero = {pure != 0}")

log("STEP 5: functional rank (a = kappa = 1)")
rng = random.Random(7)
allv = XS + PS
for trial in range(3):
    d = dict(num)
    for w_ in allv:
        d[w_] = Q_(rng.randint(-9, 9), rng.randint(1, 5)) + Q_(1, 7)
    J = lambda fs: sp.Matrix([[sp.diff(f, w_).subs(d) for w_ in allv] for f in fs]).rank()
    log(f"  trial {trial}: rank(p_t,p_s,p_v,H,Q1,Q2) = {J([pt,ps,pv,H,Q1,Q2])}   rank(...,F) = {J([pt,ps,pv,H,Q1,Q2,F])}")

log("STEP 6: the object")
log(f"  U = {sp.factor(U)}")
log(f"  A = {A}")
log(f"  H = {sp.collect(H, PS)}")
log(f"  Q1 = {sp.collect(Q1, PS)}")
log(f"  Q2 = {sp.collect(Q2, PS)}")
log(f"  F = {sp.collect(F, PS)}")
