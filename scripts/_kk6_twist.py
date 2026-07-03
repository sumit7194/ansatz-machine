#!/usr/bin/env python3
"""Prototype — 6D KK on T^2 with a TWISTED fibre (chi != 0), the decisive check (§113 Stage A).

Fibre internal metric M = [[Phi1^2, chi],[chi, Phi2^2]] (chi(r) the dynamical twist / off-diagonal
modulus); full 6D metric g6[mu,nu]=g4 + M_ab A^a_mu A^b_nu, g6[mu,w_a]=M_ab A^b_mu, g6[w_a,w_b]=M_ab.
Both A^a = a_a(r) dt (parallel electric -> F1.F2 != 0: the §112-REJECTED case).

THE DECISIVE QUESTION: in §112 (chi=0), R6(w1,w2) = 1/4 Phi1^2 Phi2^2 F1.F2 was a bare CONSTRAINT
(nothing to absorb it -> forced F1.F2=0). With chi dynamical it should become an EOM for chi:
R6(w1,w2) ~ [wave operator on chi] + [F1.F2 source]  -> the obstruction is ABSORBED. This prototype
computes the raw R6 fibre components and reports whether R6(w1,w2) now carries a chi'' term (an EOM,
not a constraint) alongside the a1'*a2' (F1.F2) source. Durable log data/kk6tw_proto.log.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry

t, r, th, ph, w1, w2 = sp.symbols("t r theta phi w1 w2", real=True)
f = sp.Function("f", positive=True)(r)
h = sp.Function("h", positive=True)(r)
a1 = sp.Function("a1")(r)
a2 = sp.Function("a2")(r)
P1 = sp.Function("Phi1", positive=True)(r)
P2 = sp.Function("Phi2", positive=True)(r)
chi = sp.Function("chi")(r)

g4 = sp.diag(-f, h, r**2, r**2 * sp.sin(th)**2)
X4 = [t, r, th, ph]
A = [[a1, 0, 0, 0], [a2, 0, 0, 0]]                     # A^1, A^2 (index a, then mu)
M = sp.Matrix([[P1**2, chi], [chi, P2**2]])            # internal fibre metric

X6 = X4 + [w1, w2]
g6 = sp.zeros(6)
for mu in range(4):
    for nu in range(4):
        g6[mu, nu] = g4[mu, nu] + sum(M[a, b] * A[a][mu] * A[b][nu] for a in range(2) for b in range(2))
for mu in range(4):
    for a in range(2):
        g6[mu, 4 + a] = g6[4 + a, mu] = sum(M[a, b] * A[b][mu] for b in range(2))
for a in range(2):
    for b in range(2):
        g6[4 + a, 4 + b] = M[a, b]

print("computing 6D Ricci with twisted fibre (7 free functions f,h,a1,a2,Phi1,Phi2,chi)...")
sys.stdout.flush()
geo6 = Geometry(g6, X6)
R6 = geo6.ricci
print("done.\n")
sys.stdout.flush()

R12 = sp.simplify(R6[4, 5])
R11 = sp.simplify(R6[4, 4])
R22 = sp.simplify(R6[5, 5])
print("RAW fibre-sector Ricci components (twisted):")
print("  R6(w1,w2) =", R12)
print()
print("  R6(w1,w1) =", R11)
print()
print("  R6(w2,w2) =", R22)

# decisive markers
has_chi2 = R12.has(sp.diff(chi, r, 2))
has_source = R12.has(sp.diff(a1, r) * sp.diff(a2, r)) or sp.simplify(
    R12.coeff(sp.diff(a1, r) * sp.diff(a2, r))) != 0
print("\nDECISIVE:")
print("  R6(w1,w2) contains chi'' (a wave operator / EOM for the twist)?  ", has_chi2)
print("  R6(w1,w2) still carries the F1.F2 (a1'*a2') source?              ", has_source)
print("  => the diagonal-ansatz CONSTRAINT has become the twist's EOM (source absorbed)"
      if (has_chi2 and has_source) else "  => (inspect above)")
