#!/usr/bin/env python3
"""KK reduction, full derivation — horizontal-lift projection + machine-matched dictionary.

The correct 4D projection of the 5D Ricci uses the HORIZONTAL LIFT e_mu = d_mu - A_mu d_w (the frame
orthogonal to the fibre): Rhat(mu,nu) = R5_{mu nu} - A_mu R5_{nu w} - A_nu R5_{mu w} + A_mu A_nu R5_{ww}.
Three dictionary identities to machine-match over the free-function family {f,h,a,Phi}(r):

  (I)   R5(e_mu,e_nu) = R4_{mu nu} + cE * Phi^2 F_mu^lam F_nu lam + cD * (1/Phi) grad_mu grad_nu Phi
  (II)  R5(e_mu, d_w) = cM * (Phi/1) * covdiv(Phi^3 F)_mu-type expression
  (III) R5(d_w, d_w)  = -Phi box(Phi) + (1/4) Phi^4 F^2          [matched exactly in _kk_reduce.py]

All coefficients DERIVED by matching, none assumed. Then the trap: Phi->1 kills boxPhi and grad-grad
terms; (III) forces F^2 = 0. Durable log data/kk_proto2.log.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry, zero_simplify

t, r, th, ph, w = sp.symbols("t r theta phi w", real=True)
f = sp.Function("f", positive=True)(r)
h = sp.Function("h", positive=True)(r)
a = sp.Function("a")(r)
Phi = sp.Function("Phi", positive=True)(r)

g5 = sp.zeros(5)
g5[0, 0] = -f + Phi**2 * a**2
g5[0, 4] = g5[4, 0] = Phi**2 * a
g5[4, 4] = Phi**2
g5[1, 1] = h
g5[2, 2] = r**2
g5[3, 3] = r**2 * sp.sin(th)**2
X5 = [t, r, th, ph, w]

g4 = sp.diag(-f, h, r**2, r**2 * sp.sin(th)**2)
X4 = [t, r, th, ph]
geo4 = Geometry(g4, X4)
g4inv = g4.inv()
R4 = geo4.ricci

# Maxwell A = a dt
A4 = [a, 0, 0, 0]
F = sp.zeros(4)
F[1, 0] = sp.diff(a, r); F[0, 1] = -F[1, 0]
Fud = sp.zeros(4)                                  # F^lam_ nu
for lam in range(4):
    for nu in range(4):
        Fud[lam, nu] = sum(g4inv[lam, m] * F[m, nu] for m in range(4))
FF = sp.zeros(4)                                   # F_mu^lam F_nu lam  = F_{mu lam} g^{lam s} F_{nu s}
for m in range(4):
    for n in range(4):
        FF[m, n] = sp.simplify(sum(F[m, lam] * g4inv[lam, s] * F[n, s] for lam in range(4) for s in range(4)))
F2 = sp.simplify(sum(F[m, n] * g4inv[m, mm] * g4inv[n, nn] * F[mm, nn]
                     for m in range(4) for n in range(4) for mm in range(4) for nn in range(4)))

# grad_mu grad_nu Phi (4D covariant Hessian)
Gam4 = geo4.christoffel
Hess = sp.zeros(4)
for m in range(4):
    for n in range(4):
        Hess[m, n] = sp.simplify(sp.diff(sp.diff(Phi, X4[n]), X4[m])
                                 - sum(Gam4[lam][m][n] * sp.diff(Phi, X4[lam]) for lam in range(4)))
sq = sp.sqrt(-g4.det())
boxPhi = sp.simplify(sum(sp.diff(sq * g4inv[m, n] * sp.diff(Phi, X4[n]), X4[m])
                         for m in range(4) for n in range(4)) / sq)
# covariant div(Phi^3 F)_nu (lower free index): D^mu (Phi^3 F_{mu nu}) = (1/sq) d_mu (sq Phi^3 F^{mu}_{ nu}) ... use
divF_low = [sp.simplify(sum(sp.diff(sq * Phi**3 * g4inv[m, mm] * F[mm, n], X4[m])
                            for m in range(4) for mm in range(4)) / sq) for n in range(4)]

print("computing 5D Ricci..."); sys.stdout.flush()
geo5 = Geometry(g5, X5)
R5 = geo5.ricci
print("done."); sys.stdout.flush()

# horizontal-lift projections
Rhat = sp.zeros(4)
for m in range(4):
    for n in range(4):
        Rhat[m, n] = R5[m, n] - A4[m] * R5[n, 4] - A4[n] * R5[m, 4] + A4[m] * A4[n] * R5[4, 4]
Rw = [sp.simplify(R5[m, 4] - A4[m] * R5[4, 4]) for m in range(4)]   # R5(e_mu, d_w)

# (I) match cE, cD on the tt, rr, thth components simultaneously
cE, cD = sp.symbols("cE cD")
print("\n(I) matching R5(e,e) = R4 + cE*Phi^2*FF + cD*Hess/Phi ...")
eqs = []
for (m, n) in [(0, 0), (1, 1), (2, 2)]:
    resmn = sp.expand(sp.simplify(Rhat[m, n] - (R4[m, n] + cE * Phi**2 * FF[m, n] + cD * Hess[m, n] / Phi)))
    eqs.append(resmn)
sol = sp.solve([eqs[0].coeff(sp.diff(a, r)**2), eqs[1].coeff(sp.diff(Phi, r, 2))], [cE, cD], dict=True)
print("   candidate cE,cD =", sol)
if sol:
    allzero = all(zero_simplify(e.subs(sol[0])) == 0 for e in eqs)
    extra = zero_simplify(sp.simplify(Rhat[3, 3] - (R4[3, 3] + cE * Phi**2 * FF[3, 3]
                                                    + cD * Hess[3, 3] / Phi)).subs(sol[0]))
    print("   tt,rr,thth leftovers all zero:", allzero, "; phph leftover:", extra)

# (II) match cM: R5(e_mu,d_w) = cM * (1/Phi) * divF_low[mu]  (try; machine finds the right power of Phi)
print("\n(II) matching R5(e,w) vs div(Phi^3 F)_mu ...")
cM, p = sp.symbols("cM p")
res_t = sp.simplify(Rw[0] / divF_low[0])
print("   R5(e_t,d_w) / div(Phi^3F)_t =", sp.simplify(res_t))
