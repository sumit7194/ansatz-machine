#!/usr/bin/env python3
"""Prototype — 6D Kaluza-Klein on T^2 (diagonal fibre), machine-derived dictionary (Stage A of §112).

Ansatz: ds^2_6 = g4_{mu nu} dx^mu dx^nu + Phi1^2 (dw1 + A1)^2 + Phi2^2 (dw2 + A2)^2, cylinder
condition on both circles; free-function family f,h,a1,a2,Phi1,Phi2 of r (A^a = a_a(r) dt, electric).
Machine-matches the dictionary with a GENEROUS candidate basis so the CROSS-COUPLINGS (the other
fibre's volume in each Maxwell density; dPhi1.dPhi2 terms) are DISCOVERED, not assumed:

  (III)_a  R6(w_a,w_a)  =  c1 Phi_a box(Phi_a) + c2 Phi_a^4 F_a^2 + c3 Phi_a (dPhi_a.dPhi_b)/Phi_b + ...
  (II)_a   R6(e_mu,w_a) ~  D^nu(Phi_a^3 Phi_b^p F^a_{nu mu})   [matching the power p!]
  (I)      R6(e,e)      =  R4 + sum_a [cE_a Phi_a^2 F^a F^a + cD_a Hess(Phi_a)/Phi_a] + cross dPhi dPhi

Durable log data/kk6_proto.log.
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
sq = sp.sqrt(-g4.det()).subs(sp.Abs(sp.sin(th)), sp.sin(th))

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

def F2_of(F):
    return sum(F[m, n] * g4inv[m, mm] * g4inv[n, nn] * F[mm, nn]
               for m in range(4) for n in range(4) for mm in range(4) for nn in range(4))

def hess(S):
    H = sp.zeros(4)
    for m in range(4):
        for n in range(4):
            H[m, n] = sp.diff(S, X4[m], X4[n]) - sum(Gam4[lam][m][n] * sp.diff(S, X4[lam])
                                                     for lam in range(4))
    return H

def box(S):
    return sum(sp.diff(sq * g4inv[m, n] * sp.diff(S, X4[n]), X4[m])
               for m in range(4) for n in range(4)) / sq

def divF_low(F, dens):
    """D^mu(dens * F_{mu nu}) lowered free index; dens a scalar density factor (e.g. Phi1^3 Phi2)."""
    Fup = sp.zeros(4)
    for m in range(4):
        for n in range(4):
            Fup[m, n] = sum(g4inv[m, mm] * g4inv[n, nn] * F[mm, nn] for mm in range(4) for nn in range(4))
    du = [sum(sp.diff(sq * dens * Fup[m, n], X4[m]) for m in range(4)) / sq for n in range(4)]
    return [sum(g4[n, s] * du[s] for s in range(4)) for n in range(4)]

F1 = maxwell(A1); F2m = maxwell(A2)
F1sq = F2_of(F1); F2sq = F2_of(F2m)
dP = lambda S: [sp.diff(S, x) for x in X4]
dot = lambda u, v: sum(g4inv[m, n] * u[m] * v[n] for m in range(4) for n in range(4))
dd12 = dot(dP(P1), dP(P2))

print("computing 6D Ricci (6 free functions)..."); sys.stdout.flush()
geo6 = Geometry(g6, X6)
R6 = geo6.ricci
print("done."); sys.stdout.flush()

Aall = [A1, A2]
Pall = [P1, P2]

# horizontal lift: e_mu = d_mu - A1_mu d_w1 - A2_mu d_w2
def lift_ee(m, n):
    e = R6[m, n]
    for ai, (Aa, wa) in enumerate([(A1, 4), (A2, 5)]):
        e += -Aa[m] * R6[n, wa] - Aa[n] * R6[m, wa]
    e += (A1[m] * A1[n] * R6[4, 4] + A2[m] * A2[n] * R6[5, 5]
          + (A1[m] * A2[n] + A2[m] * A1[n]) * R6[4, 5])
    return e

def lift_ew(m, wa):
    return R6[m, wa] - A1[m] * R6[4, wa] - A2[m] * R6[5, wa]

# ---- (III)_1: match R6(w1,w1) against a generous basis ----
c = sp.symbols("c1:8")
basis1 = [P1 * box(P1), P1**4 * F1sq, P1**2 * P2**2 * F2sq, P1 * dd12 * P1 / P2,
          dot(dP(P1), dP(P1)), P1**2 * dot(dP(P2), dP(P2)) / P2**2]
res = sp.expand(sp.simplify(R6[4, 4] - sum(ci * bi for ci, bi in zip(c, basis1))))
# collect coefficients of independent function-derivative monomials and solve
monos = [sp.diff(P1, r, 2), sp.diff(a1, r)**2, sp.diff(a2, r)**2,
         sp.diff(P1, r) * sp.diff(P2, r), sp.diff(P1, r)**2, sp.diff(P2, r)**2]
eqs = [res.coeff(mo) for mo in monos]
sol = sp.solve(eqs, list(c[:6]), dict=True)
print("\n(III)_1 match:", sol)
if sol:
    left = zero_simplify(res.subs(sol[0]))
    print("   leftover:", left)

# ---- (II)_1: find the density power p in D(Phi1^3 Phi2^p F1) ----
print("\n(II)_1 density-power hunt:")
lhs = sp.simplify(lift_ew(0, 4))
for p in (0, 1, 2):
    dens = P1**3 * P2**p
    rhs = [-x / (2 * P1 * P2**0) for x in divF_low(F1, dens)]     # try plain -(1/2Phi1) norm first
    ratio = sp.simplify(lhs / rhs[0]) if rhs[0] != 0 else None
    print(f"   p={p}: R6(e_t,w1)/[-(1/2P1) D(P1^3 P2^{p} F1)_t] =", ratio)
