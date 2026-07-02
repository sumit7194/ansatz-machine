#!/usr/bin/env python3
"""Prototype — Kaluza-Klein 5D->4D reduction, machine-derived (quantum-project ask, Stage 1).

5D Kaluza ansatz (classic form, cylinder condition structural -- nothing depends on w):
    ds^2_5 = g^4_{mu nu} dx^mu dx^nu + Phi(r)^2 (dw + a(r) dt)^2
with the 4D block a FREE-FUNCTION static spherical family: diag(-f(r), h(r), r^2, r^2 sin^2 th).
So the claim proven is a THEOREM over the functional family {f,h,a,Phi} (the §52-TOV move), not a
single metric.

This prototype computes the 5D Ricci components and the 4D dictionary objects (4D Ricci of the block,
Maxwell tensor of A = a dt with dilaton coupling, box(Phi), F^2) and lets the MACHINE derive the
dictionary factors by symbolic matching -- we do not trust textbook constants from memory (the §102
Manko-Novikov lesson). Then the honesty trap: freeze Phi=1 and show R^5_ww = -(1/4)Phi^3 F^2-type
residual survives, i.e. 5D vacuum with a frozen dilaton FORCES F^2=0 -> the naive claim is REJECTED.

Repro: .venv/bin/python scripts/_kk_reduce.py   (durable log data/kk_proto.log)
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

# ---- 5D Kaluza metric: 4D block + Phi^2 (dw + a dt)^2 ----
g5 = sp.zeros(5)
g5[0, 0] = -f + Phi**2 * a**2
g5[0, 4] = g5[4, 0] = Phi**2 * a
g5[4, 4] = Phi**2
g5[1, 1] = h
g5[2, 2] = r**2
g5[3, 3] = r**2 * sp.sin(th)**2
X5 = [t, r, th, ph, w]

# ---- 4D block + matter dictionary objects ----
g4 = sp.diag(-f, h, r**2, r**2 * sp.sin(th)**2)
X4 = [t, r, th, ph]
geo4 = Geometry(g4, X4)
g4inv = g4.inv()

# Maxwell of A = a(r) dt:  F_{rt} = a'
F = sp.zeros(4)
F[1, 0] = sp.diff(a, r)
F[0, 1] = -F[1, 0]
F2 = sp.simplify(sum(F[m, n] * g4inv[m, mm] * g4inv[n, nn] * F[mm, nn]
                     for m in range(4) for n in range(4) for mm in range(4) for nn in range(4)))
# box(Phi) on the 4D block
sq = sp.sqrt(-g4.det())
boxPhi = sp.simplify(sum(sp.diff(sq * g4inv[m, n] * sp.diff(Phi, X4[n]), X4[m])
                         for m in range(4) for n in range(4)) / sq)
# div(Phi^3 F)^t : the dilaton-coupled Maxwell equation (nu = t component)
divF_t = sp.simplify(sum(sp.diff(sq * Phi**3 * g4inv[m, mm] * g4inv[0, nn] * F[mm, nn], X4[m])
                         for m in range(4) for mm in range(4) for nn in range(4)) / sq)

print("dictionary objects (4D):")
print("  F^2      =", F2)
print("  box(Phi) =", boxPhi)
print("  div(Phi^3 F)^t =", divF_t)

# ---- 5D Ricci ----
print("\ncomputing 5D Ricci (free functions of r; tractable)...")
geo5 = Geometry(g5, X5)
R5 = geo5.ricci
print("done.")

# (1) the dilaton equation from R5_ww: expect  R5_ww = c1 * Phi*boxPhi + c2 * Phi^4 * F2  (machine-match c1,c2)
c1, c2 = sp.symbols("c1 c2")
res = sp.simplify(R5[4, 4] - (c1 * Phi * boxPhi + c2 * Phi**4 * F2))
sol = sp.solve([sp.expand(res).coeff(sp.diff(Phi, r, 2)),
                sp.expand(res).coeff(sp.diff(a, r)**2)], [c1, c2], dict=True)
print("\n(1) R5_ww dictionary match: candidate c1,c2 =", sol)
if sol:
    leftover = zero_simplify(res.subs(sol[0]))
    print("    leftover after match:", leftover)

# (2) the Maxwell equation from the (t,w) sector: expect R5_tw (index-raised combo) ∝ div(Phi^3 F)^t
# use mixed component: R5^A_B via ginv
R5_tw = sp.simplify(R5[0, 4])
print("\n(2) R5_tw =", R5_tw)
c3 = sp.symbols("c3")
res2 = sp.simplify(R5_tw - c3 * (Phi**2 / 2) * (-f) * 0 - c3 * divF_t)   # try direct proportionality first
# direct ratio attempt:
ratio = sp.simplify(R5_tw / divF_t)
print("    R5_tw / div(Phi^3 F)^t =", ratio)
