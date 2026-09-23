#!/usr/bin/env python3
"""EXP-002 -- Wick rotation of Cariglia-Galajinsky's second Drach metric into a Lorentzian vacuum
pp-wave, and the three exact checks (field equations, conservation, irreducibility in BOTH senses).

SOURCE OBJECT (arXiv:1503.02162, eq. 1, 20, 21; text in prior_art/CG_1503.02162.txt):
    dtau^2 = -2U dt^2 + 2 dt ds + 2 dx dy,      U = alpha/sqrt(x) + beta/sqrt(y)         [signature (2,2)]
    I = x px^2 py - y px py^2 + (beta x/sqrt(y)) px - (alpha y/sqrt(x)) py                [cubic integral]
    footnote 9: an extra quadratic integral  x px py - y py^2 + beta x/sqrt(y) - alpha * (garbled)

THE CONTINUATION. Put x = w^2, y = wbar^2 with w = xi + i eta (so sqrt(x) = w, sqrt(y) = wbar,
X + iY = w^2 are Cartesian coordinates on the transverse plane and (xi, eta) are parabolic
coordinates). Then 2 dx dy = 2 |2 w dw|^2 = 8 (xi^2 + eta^2)(dxi^2 + deta^2), and the metric is
    dtau^2 = -2U dt^2 + 2 dt ds + 8 rho^2 (dxi^2 + deta^2),   rho^2 = xi^2 + eta^2,
    U = alpha/w + beta/wbar,  real iff beta = conj(alpha);  alpha = beta = a real gives U = 2 a xi/rho^2.
Momenta: p_x dx + p_y dy = p_w dw + p_wbar dwbar with p_w = (p_xi - i p_eta)/2, dx = 2 w dw, so
    p_x = (p_xi - i p_eta)/(4 w),    p_y = (p_xi + i p_eta)/(4 wbar).
The scale of a is a gauge: t -> mu t, s -> s/mu rescales U by mu^2, and a -> -a is xi -> -xi.
So a = 1 is fully general (a != 0); symbolic a is kept where it costs nothing.

CONVENTIONS. H = (1/2) g^{ab} p_a p_b. {A,B} = sum_a (dA/dx^a dB/dp_a - dA/dp_a dB/dx^a).
A Killing tensor of rank r <-> F homogeneous of degree r in p with {H,F} = 0.
Reducible (polynomial sense) = linear combination of symmetrized products of lower-rank Killing
tensors. Functional sense = Jacobian rank of (p_t, p_s, H, Q1, Q2, F) on the 8-dim phase space.

Run:  ../conjecture_machine/.venv/bin/python scripts/exp002_ppwave.py
(the sibling's interpreter is used for its sympy; nothing of theirs is imported or written here.)
"""
import itertools
import random
import sys
import time

import sympy as sp
from sympy import Rational as Q_

T0 = time.time()


def log(msg=""):
    print(f"[{time.time()-T0:7.1f}s] {msg}", flush=True)


# ----------------------------------------------------------------------------- coordinates & metric
t, xi, eta, s = sp.symbols("t xi eta s", real=True)
pt, pxi, peta, ps = sp.symbols("p_t p_xi p_eta p_s", real=True)
a = sp.Symbol("a", positive=True)
XS = [t, xi, eta, s]
PS = [pt, pxi, peta, ps]
N = 4
rho2 = xi**2 + eta**2
U = 2 * a * xi / rho2

g = sp.zeros(4, 4)
g[0, 0] = -2 * U
g[0, 3] = g[3, 0] = 1
g[1, 1] = g[2, 2] = 8 * rho2
ginv = g.inv().applyfunc(sp.cancel)
H = sp.expand(Q_(1, 2) * sum(ginv[i, j] * PS[i] * PS[j] for i in range(N) for j in range(N)))
log(f"H = {H}")


def poisson(A, B):
    return sp.expand(sum(sp.diff(A, XS[i]) * sp.diff(B, PS[i]) - sp.diff(A, PS[i]) * sp.diff(B, XS[i])
                         for i in range(N)))


def is_zero(expr):
    return sp.cancel(sp.together(sp.expand(expr))) == 0


# ----------------------------------------------------------------------------- CHECK 1: curvature
log("CHECK 1: field equations and signature")
Gam = [[[sp.cancel(Q_(1, 2) * sum(ginv[i, l] * (sp.diff(g[l, j], XS[k]) + sp.diff(g[l, k], XS[j])
                                                  - sp.diff(g[j, k], XS[l])) for l in range(N)))
         for k in range(N)] for j in range(N)] for i in range(N)]


def riemann_up(i, j, k, l):
    # R^i_{jkl} = d_k Gam^i_{lj} - d_l Gam^i_{kj} + Gam^i_{km} Gam^m_{lj} - Gam^i_{lm} Gam^m_{kj}
    e = sp.diff(Gam[i][l][j], XS[k]) - sp.diff(Gam[i][k][j], XS[l])
    e += sum(Gam[i][k][m] * Gam[m][l][j] - Gam[i][l][m] * Gam[m][k][j] for m in range(N))
    return sp.cancel(e)


Rup = [[[[riemann_up(i, j, k, l) for l in range(N)] for k in range(N)] for j in range(N)] for i in range(N)]
Ric = sp.Matrix(N, N, lambda j, l: sp.cancel(sum(Rup[i][j][i][l] for i in range(N))))
riem_nonzero = [(i, j, k, l) for i in range(N) for j in range(N) for k in range(N) for l in range(N)
                if Rup[i][j][k][l] != 0]
log(f"  Ricci tensor identically zero: {Ric == sp.zeros(4,4)}   (symbolic a)")
log(f"  Riemann nonzero components: {len(riem_nonzero)}  e.g. R^{riem_nonzero[0]} = {Rup[riem_nonzero[0][0]][riem_nonzero[0][1]][riem_nonzero[0][2]][riem_nonzero[0][3]]}")
# Kretschmann (CG note it vanishes for their metrics)
Rdown = [[[[sp.cancel(sum(g[i, m] * Rup[m][j][k][l] for m in range(N))) for l in range(N)]
           for k in range(N)] for j in range(N)] for i in range(N)]
Rupup = lambda i, j, k, l: sum(ginv[j, b] * ginv[k, c] * ginv[l, d] * Rup[i][b][c][d]
                               for b in range(N) for c in range(N) for d in range(N))
K = sp.cancel(sum(Rdown[i][j][k][l] * Rupup(i, j, k, l) for (i, j, k, l) in riem_nonzero))
log(f"  Kretschmann scalar: {K}")
# signature: the (t,s) block has det -1 (one negative, one positive eigenvalue); the (xi,eta) block is 8 rho^2 > 0
blk = g.extract([0, 3], [0, 3])
log(f"  (t,s) block det = {sp.cancel(blk.det())}  ->  (1,1);  transverse block = 8 rho^2 I  ->  (0,2);  total (1,3) LORENTZIAN wherever rho^2 > 0")
ev = [sp.N(v) for v in g.subs({a: 1, xi: Q_(5, 3), eta: Q_(7, 4)}).eigenvals().keys()]
log(f"  numeric eigenvalues at a=1, (xi,eta)=(5/3,7/4): {sorted(ev)}")
ricci_ok = (Ric == sp.zeros(4, 4))

# ----------------------------------------------------------------------------- transcription control (2D, CG's variables)
log("TRANSCRIPTION CONTROL: CG eq. 20 in their own variables")
x, y, px, py = sp.symbols("x y p_x p_y", positive=True)
al, be = sp.symbols("alpha beta", real=True)
H2 = px * py + al / sp.sqrt(x) + be / sp.sqrt(y)
I2 = x * px**2 * py - y * px * py**2 + be * x / sp.sqrt(y) * px - al * y / sp.sqrt(x) * py


def poisson2(A, B):
    return sp.expand(sum(sp.diff(A, q) * sp.diff(B, p) - sp.diff(A, p) * sp.diff(B, q)
                         for q, p in ((x, px), (y, py))))


log(f"  {{H2, I}} == 0 : {is_zero(poisson2(H2, I2))}")
c1, c2 = sp.symbols("c1 c2")
Q2d = x * px * py - y * py**2 + c1 * be * x / sp.sqrt(y) + c2 * al * sp.sqrt(x)
br = sp.expand(poisson2(H2, Q2d))
sol = sp.solve(sp.Poly(sp.expand(br * sp.sqrt(x) ** 3 * sp.sqrt(y) ** 3), px, py).coeffs(), [c1, c2], dict=True)
log(f"  quadratic of footnote 9: coefficients solve to {sol}  (so the garbled last term is c2*alpha*sqrt(x))")

# ----------------------------------------------------------------------------- CHECK 2: transport CG's cubic
log("CHECK 2: transport of CG's cubic and conservation")
w = xi + sp.I * eta
wb = xi - sp.I * eta
px_c = (pxi - sp.I * peta) / (4 * w)
py_c = (pxi + sp.I * peta) / (4 * wb)
# x = w^2, y = wbar^2, sqrt(x) = w, sqrt(y) = wbar ; alpha = beta = a ; potential-type terms carry p_s^2
F_D = (w**2 * px_c**2 * py_c - wb**2 * px_c * py_c**2
       + ps**2 * (a * w**2 / wb * px_c - a * wb**2 / w * py_c))
F_D = sp.expand(sp.cancel(sp.together(F_D)))
# sanity: the 2D Hamiltonian transports onto H at p_s = 1, p_t = 0
H2_transported = sp.cancel(px_c * py_c + a / w + a / wb)
log(f"  transported 2D Hamiltonian == H|_(p_t=0,p_s=1): {is_zero(H2_transported - H.subs({pt: 0, ps: 1}))}")
log(f"  {{H, F_D}} == 0 : {is_zero(poisson(H, F_D))}")
F_re, F_im = [sp.expand(sp.cancel(sp.together(z))) for z in F_D.as_real_imag()]
log(f"  F_D real part nonzero: {F_re != 0};  imaginary part nonzero: {F_im != 0}")
log(f"  {{H, Re F_D}} == 0 : {is_zero(poisson(H, F_re))}   {{H, Im F_D}} == 0 : {is_zero(poisson(H, F_im))}")
pure = lambda F: sp.expand(F.subs({pt: 0, ps: 0}))
log(f"  pure (p_xi,p_eta)-cubic part of Re F_D: {sp.factor(pure(F_re))}")
log(f"  pure (p_xi,p_eta)-cubic part of Im F_D: {sp.factor(pure(F_im))}")
F = F_re if F_re != 0 else F_im
Fname = "Re F_D" if F_re != 0 else "Im F_D"
log(f"  taking F := {Fname}")
log(f"  F = {sp.collect(F, PS)}")

# ----------------------------------------------------------------------------- rank-2 Killing tensors (explicit)
log("RANK 2: the two parabolic separation constants")
Hb = H - pt * ps                       # (xi^2+eta^2)*Hb = p_xi^2/16 + p_eta^2/16 + 2 a xi p_s^2
Q1 = sp.expand(pxi**2 / 16 + 2 * a * xi * ps**2 - xi**2 * Hb)
Q2 = sp.expand((pxi - peta)**2 / 32 + a * (xi - eta) * ps**2 - Q_(1, 2) * (xi - eta)**2 * Hb)
log(f"  {{H, Q1}} == 0 : {is_zero(poisson(H, Q1))}    {{H, Q2}} == 0 : {is_zero(poisson(H, Q2))}")
log(f"  {{Q1, Q2}} == 0 ? {is_zero(poisson(Q1, Q2))}")
F_B = sp.expand(sp.cancel(sp.together(poisson(Q1, Q2))))
log(f"  {{H, {{Q1,Q2}}}} == 0 : {is_zero(poisson(H, F_B))}")
log(f"  pure part of {{Q1,Q2}}: {sp.factor(pure(F_B))}")

# ----------------------------------------------------------------------------- CHECK 3a: polynomial irreducibility
log("CHECK 3a: polynomial irreducibility")
log("  (i) Killing vectors: upper bound on dim K1 from the 1-jet at a generic point")
# unknown jet: xi^a (4) and omega_ab antisymmetric (6); nabla_a xi_b = omega_ab.
# For every Killing vector, L_xi (nabla^k R) = 0 at every point. Each such condition is linear in
# the jet, so #Killing vectors <= dim of the jets satisfying them (a KV is fixed by its 1-jet).
a1 = {a: 1}
Rd = sp.MutableDenseNDimArray([[[[Rdown[i][j][k][l].subs(a1) for l in range(N)] for k in range(N)]
                                for j in range(N)] for i in range(N)])
Gam1 = [[[Gam[i][j][k].subs(a1) for k in range(N)] for j in range(N)] for i in range(N)]


def cov_deriv(T, rank):
    """nabla_e T_{a1..ak} -> array of rank k+1 with the derivative index LAST."""
    out = sp.MutableDenseNDimArray.zeros(*([N] * (rank + 1)))
    for idx in itertools.product(range(N), repeat=rank):
        for e in range(N):
            val = sp.diff(T[idx], XS[e])
            for pos in range(rank):
                for f in range(N):
                    gam = Gam1[f][e][idx[pos]]
                    if gam != 0:
                        jdx = list(idx)
                        jdx[pos] = f
                        val -= gam * T[tuple(jdx)]
            out[idx + (e,)] = val
    return out


log("     computing nabla R and nabla nabla R ...")
DR = cov_deriv(Rd, 4)
DDR = cov_deriv(DR, 5)
log("     done")
xv = sp.symbols("v0:4")
om = {}
for i in range(N):
    for j in range(i + 1, N):
        om[(i, j)] = sp.Symbol(f"w{i}{j}")
        om[(j, i)] = -om[(i, j)]
    om[(i, i)] = 0
unk = list(xv) + [om[(i, j)] for i in range(N) for j in range(i + 1, N)]


def lie_rows(T, rank, pt0):
    gi0 = ginv.subs(a1).subs(pt0)
    T0 = T.subs(pt0) if hasattr(T, "subs") else T.applyfunc(lambda e: e.subs(pt0))
    DT = cov_deriv(T, rank)
    DT0 = DT.applyfunc(lambda e: e.subs(pt0))
    dxi_up = [[sum(gi0[b, c] * om[(aa, c)] for c in range(N)) for b in range(N)] for aa in range(N)]  # nabla_a xi^b
    rows = []
    for idx in itertools.product(range(N), repeat=rank):
        val = sum(xv[e] * DT0[idx + (e,)] for e in range(N))
        for pos in range(rank):
            for e in range(N):
                jdx = list(idx)
                jdx[pos] = e
                val += T0[tuple(jdx)] * dxi_up[idx[pos]][e]
        val = sp.expand(val)
        if val != 0:
            rows.append([val.coeff(u_) for u_ in unk])
    return rows


for pt0 in ({xi: Q_(5, 3), eta: Q_(7, 4), t: 0, s: 0}, {xi: Q_(-2, 7), eta: Q_(9, 5), t: 0, s: 0}):
    rows = lie_rows(Rd, 4, pt0)
    rk = sp.Matrix(rows).rank()
    log(f"     point {pt0[xi]},{pt0[eta]}: L_xi R = 0 -> rank {rk}, admissible jets {10-rk}")
    rows += lie_rows(DR, 5, pt0)
    rk = sp.Matrix(rows).rank()
    log(f"        + L_xi nabla R = 0 -> rank {rk}, admissible jets {10-rk}")
    if 10 - rk > 2:
        rows += lie_rows(DDR, 6, pt0)
        rk = sp.Matrix(rows).rank()
        log(f"        + L_xi nabla^2 R = 0 -> rank {rk}, admissible jets {10-rk}")
    kv_bound = 10 - rk
log(f"  => dim K1 <= {kv_bound}; d_t and d_s are Killing, so dim K1 = 2 exactly" if kv_bound == 2
    else f"  => dim K1 <= {kv_bound}: NOT closed, more prolongation needed")

log("  (ii) every reducible rank-3 tensor is (c1 p_t + c2 p_s) * K2, hence has zero pure part;")
log(f"       pure part of F is {'NONZERO' if pure(F) != 0 else 'ZERO'} -> F is {'polynomially IRREDUCIBLE' if pure(F) != 0 and kv_bound == 2 else 'undecided'}")

# and the explicit relation between F (transported) and {Q1,Q2} modulo the reducible span
log("  (iii) F versus {Q1,Q2} modulo the reducible span K1 * K2")
K2 = [pt**2, pt * ps, ps**2, H, Q1, Q2]
red3 = [sp.expand(v * k) for v in (pt, ps) for k in K2]
lam = sp.Symbol("lam")
mus = sp.symbols("mu0:12")
expr = sp.expand(F - lam * F_B - sum(m * r for m, r in zip(mus, red3)))
polyP = sp.Poly(expr, *PS)
eqs = []
for c in polyP.coeffs():
    num = sp.numer(sp.together(c))
    eqs += sp.Poly(sp.expand(num), xi, eta).coeffs()
sol = sp.solve(eqs, [lam] + list(mus), dict=True)
log(f"     solution: {sol if sol else 'NONE (F not in span{{Q1,Q2}} + reducibles)'}")
if sol:
    chk = sp.expand(F - (lam * F_B + sum(m * r for m, r in zip(mus, red3))).subs(sol[0]))
    log(f"     verified identically: {is_zero(chk)}")

# ----------------------------------------------------------------------------- CHECK 3b: functional independence
log("CHECK 3b: functional (in)dependence -- Jacobian rank on the 8-dim phase space")
allv = XS + PS
rng = random.Random(20260905)


def rand_pt():
    d = {a: 1}
    for v in allv:
        d[v] = Q_(rng.randint(-9, 9), rng.randint(1, 5)) + Q_(1, 7)
    return d


for trial in range(3):
    d = rand_pt()
    Jrows = []
    for fn in (pt, ps, H, Q1, Q2, F):
        Jrows.append([sp.diff(fn, v).subs(d) for v in allv])
    J = sp.Matrix(Jrows)
    log(f"  trial {trial}: rank J(p_t,p_s,H,Q1,Q2)    = {J[:5, :].rank()}   rank J(p_t,p_s,H,Q1,Q2,F) = {J.rank()}")
    JB = sp.Matrix(Jrows[:5] + [[sp.diff(F_B, v).subs(d) for v in allv]])
    log(f"           rank J(p_t,p_s,H,Q1,Q2,{{Q1,Q2}}) = {JB.rank()}")

# ----------------------------------------------------------------------------- the algebraic relation
log("ALGEBRAIC RELATION: F^2 as a weighted-homogeneous polynomial in (H, Q1, Q2, p_t, p_s), weight 6")
gens = [(H, 2), (Q1, 2), (Q2, 2), (pt, 1), (ps, 1)]
mons = []
for ex in itertools.product(range(4), range(4), range(4), range(7), range(7)):
    if sum(e * wgt for e, (_, wgt) in zip(ex, gens)) == 6:
        mons.append(ex)
cs = sp.symbols(f"c0:{len(mons)}")
Pgen = sum(c * sp.prod([gg**e for e, (gg, _) in zip(ex, gens)]) for c, ex in zip(cs, mons))
target = sp.expand(F**2)
rows, rhs = [], []
for _ in range(len(mons) + 15):
    d = rand_pt()
    rows.append([sp.prod([gg.subs(d)**e for e, (gg, _) in zip(ex, gens)]) for ex in mons])
    rhs.append(target.subs(d))
solc = sp.linsolve((sp.Matrix(rows), sp.Matrix(rhs)), cs)
if solc == sp.EmptySet:
    log("  no relation F^2 = P(H,Q1,Q2,p_t,p_s) of weight 6 -- try weight-6 relation with F*(linear) later")
else:
    csol = list(solc)[0]
    Prel = sp.expand(Pgen.subs(dict(zip(cs, csol))))
    ok = is_zero(F**2 - Prel.subs({H: H, Q1: Q1, Q2: Q2}))
    Hs, Q1s, Q2s = sp.symbols("H Q1 Q2")
    Pshow = sum(c * sp.prod([gg**e for e, gg in zip(ex, (Hs, Q1s, Q2s, pt, ps))]) for c, ex in zip(csol, mons))
    log(f"  F^2 = {sp.factor(Pshow)}")
    log(f"  verified identically in phase space: {ok}")

# ----------------------------------------------------------------------------- summary
log("SUMMARY")
log(f"  1. Ricci-flat (symbolic a): {ricci_ok};  Lorentzian (1,3) for rho^2>0: True;  Riemann != 0: {len(riem_nonzero) > 0}")
log(f"  2. transported CG cubic conserved: {is_zero(poisson(H, F_D))};  real part conserved and nonzero: {is_zero(poisson(H, F)) and F != 0}")
log(f"  3a. polynomial irreducibility: dim K1 = {kv_bound}, pure part nonzero = {pure(F) != 0}")
log(f"  3b. functional dependence: see Jacobian ranks above")
