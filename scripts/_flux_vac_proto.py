#!/usr/bin/env python3
"""Prototype — §114 Stage B: the VACUUM ATLAS scan. Which {flux, Lambda6, twist} stabilize which moduli.

Constant moduli + 4D maximally-symmetric base:
    g4 = -(1 - lam r^2) dt^2 + dr^2/(1 - lam r^2) + r^2 dOmega^2      (lam ~ Lambda4/3)
    fibre M = [[P1^2, chi],[chi, P2^2]] const,  flux G_{w1w2} = n,  6D cosmological constant Lambda6.
6D equations E_MN = R_MN - 1/2 g R + L6 g - T_MN = 0 become ALGEBRAIC in (lam, P1, P2, chi, n, L6):
each config's system is solved EXACTLY -> verdict {consistent-with-stabilization / obstructed(runaway)
/ flat-directions}, with the obstruction EXTRACTED as the unsatisfiable condition, §112-style.

CONFIGS scanned:
  C0: n=0, L6=0                 -> expect: lam=0 forced, moduli FREE (flat directions, nothing stabilized)
  C1: n!=0, L6=0                -> expect: OBSTRUCTED (no constant-moduli vacuum; runaway -- extract n^2=0)
  C2: n!=0, L6 free             -> expect: solution with detM ~ n^2/L6-type relation: VOLUME (+axion chi=0?)
                                    stabilized, SHAPE P1/P2 flat; sign of lam extracted (AdS4/dS4?)
  C3: chi free in C2            -> is chi=0 forced at the vacuum, or flat?
Durable log data/flux_vac_proto.log.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry, zero_simplify

t, r, th, ph, w1, w2 = sp.symbols("t r theta phi w1 w2", real=True)
lam, n, L6 = sp.symbols("lam n Lambda6", real=True)
P1, P2 = sp.symbols("Phi1 Phi2", positive=True)
chi = sp.symbols("chi", real=True)

X6 = [t, r, th, ph, w1, w2]


def einstein_system(P1v, P2v, chiv, nv, L6v):
    """Build the 6D Einstein+Maxwell system for constant moduli; return the set of independent
    algebraic equations (simplified, deduplicated)."""
    F = 1 - lam * r**2
    g4 = sp.diag(-F, 1 / F, r**2, r**2 * sp.sin(th)**2)
    M = sp.Matrix([[P1v**2, chiv], [chiv, P2v**2]])
    g6 = sp.zeros(6)
    for a in range(4):
        for b in range(4):
            g6[a, b] = g4[a, b]
    for a in range(2):
        for b in range(2):
            g6[4 + a, 4 + b] = M[a, b]
    G = sp.zeros(6)
    G[4, 5] = nv
    G[5, 4] = -nv
    geo = Geometry(g6, X6)
    R6 = geo.ricci
    g6inv = g6.inv()
    Rs = sp.simplify(sum(g6inv[i, j] * R6[i, j] for i in range(6) for j in range(6)))
    Gup = sp.zeros(6)
    for i in range(6):
        for j in range(6):
            Gup[i, j] = sum(g6inv[i, p] * g6inv[j, q] * G[p, q] for p in range(6) for q in range(6))
    G2 = sp.simplify(sum(G[i, j] * Gup[i, j] for i in range(6) for j in range(6)))
    eqs = set()
    for i in range(6):
        for j in range(i, 6):
            Tij = sum(G[i, p] * g6inv[p, q] * G[j, q] for p in range(6) for q in range(6)) \
                - sp.Rational(1, 4) * g6[i, j] * G2
            e = sp.simplify(R6[i, j] - sp.Rational(1, 2) * g6[i, j] * Rs + L6v * g6[i, j] - Tij)
            e = sp.simplify(sp.together(e))
            if e != 0:
                nu, _ = sp.fraction(e)
                nu = sp.factor(nu)
                # strip metric prefactors that never vanish
                eqs.add(nu)
    return sorted(eqs, key=sp.count_ops)


print("§114 Stage B -- the vacuum atlas scan (exact algebra per config)\n")

print("C0: n=0, L6=0")
sys.stdout.flush()
eqs = einstein_system(P1, P2, 0, 0, 0)
print(f"  independent equations: {eqs}")
sol = sp.solve(eqs, [lam], dict=True)
print(f"  solve for lam: {sol}   -> moduli appear in NO equation => FLAT directions (nothing stabilized)\n")

print("C1: n!=0, L6=0")
sys.stdout.flush()
eqs = einstein_system(P1, P2, 0, n, 0)
print(f"  independent equations: {eqs}")
sol = sp.solve(eqs, [lam, P1], dict=True)
print(f"  solve for (lam, P1): {sol}   -> if only n=0-type solutions: OBSTRUCTED (runaway; extract)\n")

print("C2: n!=0, L6 free (chi=0)")
sys.stdout.flush()
eqs = einstein_system(P1, P2, 0, n, L6)
print(f"  independent equations: {eqs}")
sol = sp.solve(eqs, [lam, L6], dict=True)
print(f"  solve for (lam, L6): {sol}")
print("  -> read off: which combinations of P1,P2 are FIXED (detM?) vs flat (shape?); sign of lam\n")

print("C3: n!=0, L6 free, chi free")
sys.stdout.flush()
eqs = einstein_system(P1, P2, chi, n, L6)
print(f"  independent equations: {eqs}")
sol = sp.solve(eqs, [lam, L6, chi], dict=True)
print(f"  solve for (lam, L6, chi): {sol}   -> is chi=0 forced at the vacuum?\n")

print("DONE -- atlas scan raw material extracted.")
