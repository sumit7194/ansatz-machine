#!/usr/bin/env python3
"""EXP-004 addendum: at p_v = 0 the 5D Hamiltonian equals the 4D one, so F|_{p_v=0} should be a
rank-3 Killing tensor of the 4D Einstein-Maxwell pp-wave g4 (profile 2V = (4a xi + kappa^2)/rho^2).
F is taken from the EXP-003 computation itself (re-derived as -4{Q1,Q2} for g4), and compared
with the transcription in WRITEUP.md sec. 6. dim K1 by the Lie-derivative jet count."""
import itertools, random, sympy as sp
from sympy import Rational as Q_
t, xi, eta, s = sp.symbols("t xi eta s", real=True)
pt, pxi, peta, ps = sp.symbols("p_t p_xi p_eta p_s", real=True)
a, kap = sp.symbols("a kappa", real=True)
XS, PS = [t, xi, eta, s], [pt, pxi, peta, ps]
rho2 = xi**2 + eta**2
H4 = pt*ps + (4*a*xi + kap**2)/(2*rho2)*ps**2 + (pxi**2 + peta**2)/(16*rho2)
pb = lambda A, B: sp.expand(sum(sp.diff(A, XS[i])*sp.diff(B, PS[i]) - sp.diff(A, PS[i])*sp.diff(B, XS[i]) for i in range(4)))
z = lambda e: sp.cancel(sp.together(sp.expand(e))) == 0
Hb = H4 - pt*ps
Q1 = sp.expand(pxi**2/16 + kap**2*ps**2/2 + 2*a*ps**2*xi - xi**2*Hb)
Q2 = sp.expand((pxi - peta)**2/32 + kap**2*ps**2/2 + a*ps**2*(xi - eta) - Q_(1, 2)*(xi - eta)**2*Hb)
print("{H4,Q1} = 0:", z(pb(H4, Q1)), "  {H4,Q2} = 0:", z(pb(H4, Q2)))
F = sp.expand(sp.cancel(sp.together(-4*pb(Q1, Q2))))
print("{H4, F} = 0 with F = -4{Q1,Q2}:", z(pb(H4, F)))
F_writeup = ((eta*pxi - xi*peta)*(pxi**2 + peta**2)/(32*rho2)
             + a*ps**2/rho2*(xi*eta*pxi + (eta**2 - xi**2)*peta/2)
             + kap**2*ps**2/(4*rho2)*(eta*pxi - xi*peta))
print("F equals WRITEUP sec.6 formula at p_v = 0:", z(F - F_writeup))
print("pure (p_xi,p_eta) part:", sp.factor(F.subs({pt: 0, ps: 0})))
# functional rank
rng = random.Random(5)
for k in range(2):
    d = {a: 1, kap: Q_(3, 2)}
    for v_ in XS + PS: d[v_] = Q_(rng.randint(-9, 9), rng.randint(1, 5)) + Q_(1, 7)
    J = lambda fs: sp.Matrix([[sp.diff(f, v_).subs(d) for v_ in XS + PS] for f in fs]).rank()
    print(f"trial {k}: rank(p_t,p_s,H,Q1,Q2) = {J([pt, ps, H4, Q1, Q2])}   rank(..,F) = {J([pt, ps, H4, Q1, Q2, F])}")
# dim K1 by jets: metric g4 at a = 1, kappa = 3/2
g = sp.zeros(4, 4); g[0, 0] = -(4*xi + Q_(9, 4))/rho2; g[0, 3] = g[3, 0] = 1; g[1, 1] = g[2, 2] = 8*rho2
gi = g.inv().applyfunc(sp.cancel); N = 4
Gam = [[[sp.cancel(Q_(1, 2)*sum(gi[i, l]*(sp.diff(g[l, j], XS[k]) + sp.diff(g[l, k], XS[j]) - sp.diff(g[j, k], XS[l])) for l in range(N)))
         for k in range(N)] for j in range(N)] for i in range(N)]
Rup = lambda i, j, k, l: sp.cancel(sp.diff(Gam[i][l][j], XS[k]) - sp.diff(Gam[i][k][j], XS[l])
                                   + sum(Gam[i][k][m]*Gam[m][l][j] - Gam[i][l][m]*Gam[m][k][j] for m in range(N)))
Rd = sp.MutableDenseNDimArray([[[[sp.cancel(sum(g[i, m]*Rup(m, j, k, l) for m in range(N))) for l in range(N)]
                                 for k in range(N)] for j in range(N)] for i in range(N)])
def cov(T, r):
    out = sp.MutableDenseNDimArray.zeros(*([N]*(r + 1)))
    for idx in itertools.product(range(N), repeat=r):
        for e in range(N):
            val = sp.diff(T[idx], XS[e])
            for pos in range(r):
                for f in range(N):
                    if Gam[f][e][idx[pos]] != 0:
                        jdx = list(idx); jdx[pos] = f; val -= Gam[f][e][idx[pos]]*T[tuple(jdx)]
            out[idx + (e,)] = val
    return out
xv = sp.symbols("v0:4"); om = {}
for i in range(N):
    for j in range(i + 1, N): om[(i, j)] = sp.Symbol(f"w{i}{j}"); om[(j, i)] = -om[(i, j)]
    om[(i, i)] = 0
unk = list(xv) + [om[(i, j)] for i in range(N) for j in range(i + 1, N)]
def rows(T, r, p0):
    gi0 = gi.subs(p0); T0 = T.applyfunc(lambda e: e.subs(p0)); DT0 = cov(T, r).applyfunc(lambda e: e.subs(p0))
    up = [[sum(gi0[b, c]*om[(aa, c)] for c in range(N)) for b in range(N)] for aa in range(N)]
    out = []
    for idx in itertools.product(range(N), repeat=r):
        val = sum(xv[e]*DT0[idx + (e,)] for e in range(N))
        for pos in range(r):
            for e in range(N):
                jdx = list(idx); jdx[pos] = e; val += T0[tuple(jdx)]*up[idx[pos]][e]
        val = sp.expand(val)
        if val != 0: out.append([val.coeff(u_) for u_ in unk])
    return out
DR = cov(Rd, 4)
for p0 in ({xi: Q_(5, 3), eta: Q_(7, 4), t: 0, s: 0}, {xi: Q_(-2, 7), eta: Q_(9, 5), t: 0, s: 0}):
    R_ = rows(Rd, 4, p0) + rows(DR, 5, p0)
    print(f"jet count at ({p0[xi]},{p0[eta]}): admissible 1-jets = {10 - sp.Matrix(R_).rank()}  (d_t, d_s are 2)")
