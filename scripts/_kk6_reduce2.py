#!/usr/bin/env python3
"""6D KK prototype, part 2 — the (I) match, the (w1,w2) TWIST-SOURCING constraint, and (II)_2.

The star question: with a DIAGONAL fibre (no twist degree of freedom), the off-diagonal fibre
equation R6(w1,w2)=0 is a CONSTRAINT nothing can absorb. Expectation: it forces F1.F2 = 0 --
two non-orthogonal gauge fields DEMAND a dynamical twist. Machine-match to confirm + get the
exact form. Durable log data/kk6_proto2.log.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry, zero_simplify

t, r, th, ph, w1, w2 = sp.symbols("t r theta phi w1 w2", real=True)
f = sp.Function("f", positive=True)(r)
h = sp.Function("h", positive=True)(r)
a1 = sp.Function("a1")(r)
a2 = sp.Function("a2")(r)
P1 = sp.Function("Phi1", positive=True)(r)
P2 = sp.Function("Phi2", positive=True)(r)

g4 = sp.diag(-f, h, r**2, r**2 * sp.sin(th)**2)
X4 = [t, r, th, ph]
A1 = [a1, 0, 0, 0]
A2 = [a2, 0, 0, 0]
X6 = X4 + [w1, w2]
g6 = sp.zeros(6)
for m in range(4):
    for n in range(4):
        g6[m, n] = g4[m, n] + P1**2 * A1[m] * A1[n] + P2**2 * A2[m] * A2[n]
for m in range(4):
    g6[m, 4] = g6[4, m] = P1**2 * A1[m]
    g6[m, 5] = g6[5, m] = P2**2 * A2[m]
g6[4, 4] = P1**2
g6[5, 5] = P2**2

geo4 = Geometry(g4, X4)
g4inv = g4.inv()
R4 = geo4.ricci
Gam4 = geo4.christoffel

def maxwell(A):
    F = sp.zeros(4)
    for m in range(4):
        for n in range(4):
            F[m, n] = sp.diff(A[n], X4[m]) - sp.diff(A[m], X4[n])
    return F

def FF_of(F):
    M = sp.zeros(4)
    for m in range(4):
        for n in range(4):
            M[m, n] = sum(F[m, lam] * g4inv[lam, s] * F[n, s] for lam in range(4) for s in range(4))
    return M

def FdotF(Fa, Fb):
    return sum(Fa[m, n] * g4inv[m, mm] * g4inv[n, nn] * Fb[mm, nn]
               for m in range(4) for n in range(4) for mm in range(4) for nn in range(4))

def hess(S):
    H = sp.zeros(4)
    for m in range(4):
        for n in range(4):
            H[m, n] = sp.diff(S, X4[m], X4[n]) - sum(Gam4[lam][m][n] * sp.diff(S, X4[lam])
                                                     for lam in range(4))
    return H

F1 = maxwell(A1); F2m = maxwell(A2)
FF1 = FF_of(F1); FF2 = FF_of(F2m)
FF12 = sp.zeros(4)                                     # F1_{mu lam} F2_nu^lam symmetrized
for m in range(4):
    for n in range(4):
        s1 = sum(F1[m, lam] * g4inv[lam, s] * F2m[n, s] for lam in range(4) for s in range(4))
        s2 = sum(F2m[m, lam] * g4inv[lam, s] * F1[n, s] for lam in range(4) for s in range(4))
        FF12[m, n] = (s1 + s2) / 2
F12 = FdotF(F1, F2m)
dP = lambda S: [sp.diff(S, x) for x in X4]
dot = lambda u, v: sum(g4inv[m, n] * u[m] * v[n] for m in range(4) for n in range(4))

print("computing 6D Ricci..."); sys.stdout.flush()
geo6 = Geometry(g6, X6)
R6 = geo6.ricci
print("done."); sys.stdout.flush()

def lift_ee(m, n):
    return (R6[m, n] - A1[m] * R6[n, 4] - A1[n] * R6[m, 4] - A2[m] * R6[n, 5] - A2[n] * R6[m, 5]
            + A1[m] * A1[n] * R6[4, 4] + A2[m] * A2[n] * R6[5, 5]
            + (A1[m] * A2[n] + A2[m] * A1[n]) * R6[4, 5])

# ---- (w1,w2): the twist-sourcing constraint ----
cc = sp.symbols("k1:6")
lhs12 = sp.simplify(R6[4, 5])
basis12 = [P1**2 * P2**2 * F12, dot(dP(P1), dP(P2)) * P1 * P2,
           P1 * P2 * dot(dP(P1), dP(P1)) / P1**2 * 0 + P1**2 * dot(dP(P2), dP(P2)) * 0 + 1 * 0]
res12 = sp.expand(sp.simplify(lhs12 - (cc[0] * basis12[0] + cc[1] * basis12[1])))
sol12 = sp.solve([res12.coeff(sp.diff(a1, r) * sp.diff(a2, r)),
                  res12.coeff(sp.diff(P1, r) * sp.diff(P2, r))], [cc[0], cc[1]], dict=True)
print("\n(w1,w2) twist-sourcing match:", sol12)
if sol12:
    print("   leftover:", zero_simplify(res12.subs(sol12[0])))
print("   raw R6(w1,w2) =", lhs12)

# ---- (I): R6(e,e) = R4 + cE1 P1^2 FF1 + cE2 P2^2 FF2 + cX P1 P2 FF12 + cD1 Hess(P1)/P1 + cD2 Hess(P2)/P2 ----
cE1, cE2, cX, cD1, cD2 = sp.symbols("cE1 cE2 cX cD1 cD2")
H1, H2 = hess(P1), hess(P2)
okI, sols = True, None
res_tt = sp.expand(sp.simplify(lift_ee(0, 0) - (R4[0, 0] + cE1 * P1**2 * FF1[0, 0] + cE2 * P2**2 * FF2[0, 0]
                                                + cX * P1 * P2 * FF12[0, 0] + cD1 * H1[0, 0] / P1 + cD2 * H2[0, 0] / P2)))
res_rr = sp.expand(sp.simplify(lift_ee(1, 1) - (R4[1, 1] + cE1 * P1**2 * FF1[1, 1] + cE2 * P2**2 * FF2[1, 1]
                                                + cX * P1 * P2 * FF12[1, 1] + cD1 * H1[1, 1] / P1 + cD2 * H2[1, 1] / P2)))
eqs = [res_tt.coeff(sp.diff(a1, r)**2), res_tt.coeff(sp.diff(a2, r)**2),
       res_tt.coeff(sp.diff(a1, r) * sp.diff(a2, r)),
       res_rr.coeff(sp.diff(P1, r, 2)), res_rr.coeff(sp.diff(P2, r, 2))]
sols = sp.solve(eqs, [cE1, cE2, cX, cD1, cD2], dict=True)
print("\n(I) match:", sols)
if sols:
    l_tt = zero_simplify(res_tt.subs(sols[0]))
    l_rr = zero_simplify(res_rr.subs(sols[0]))
    l_th = zero_simplify(sp.simplify(lift_ee(2, 2) - (R4[2, 2] + cE1 * P1**2 * FF1[2, 2]
                                                      + cE2 * P2**2 * FF2[2, 2] + cX * P1 * P2 * FF12[2, 2]
                                                      + cD1 * H1[2, 2] / P1 + cD2 * H2[2, 2] / P2)).subs(sols[0]))
    print("   leftovers tt,rr,thth:", l_tt, l_rr, l_th)
