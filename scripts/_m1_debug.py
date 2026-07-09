#!/usr/bin/env python3
"""Diagnostic: why does the M1 monodromy bracket set differ from the untwisted set?"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry, zero_simplify

t, r, th, ph, w1, w2 = sp.symbols("t r theta phi w1 w2", real=True)
lam, n, L6, m = sp.symbols("lam n Lambda6 m", real=True)
P1s, P2s = sp.symbols("Phi1 Phi2", positive=True)
X6 = [t, r, th, ph, w1, w2]


def eqs_of(fib, nv, L6v):
    F = 1 - lam * r**2
    g4 = sp.diag(-F, 1 / F, r**2, r**2 * sp.sin(th)**2)
    g6 = sp.zeros(6)
    for a in range(4):
        for b in range(4):
            g6[a, b] = g4[a, b]
    for a in range(2):
        for b in range(2):
            g6[4 + a, 4 + b] = fib[a, b]
    G = sp.zeros(6)
    G[4, 5] = nv
    G[5, 4] = -nv
    geo = Geometry(g6, X6)
    R6 = geo.ricci
    g6inv = g6.inv()
    Rs = sp.simplify(sum(g6inv[i, j] * R6[i, j] for i in range(6) for j in range(6)))
    Gup = sp.Matrix(6, 6, lambda i, j: sum(
        g6inv[i, p] * g6inv[j, q] * G[p, q] for p in range(6) for q in range(6)))
    G2 = sp.simplify(sum(G[i, j] * Gup[i, j] for i in range(6) for j in range(6)))
    out = []
    for i in range(6):
        for j in range(i, 6):
            Tij = sum(G[i, p] * g6inv[p, q] * G[j, q] for p in range(6) for q in range(6)) \
                - sp.Rational(1, 4) * g6[i, j] * G2
            e = sp.simplify(R6[i, j] - sp.Rational(1, 2) * g6[i, j] * Rs + L6v * g6[i, j] - Tij)
            if e != 0:
                nu, _ = sp.fraction(sp.together(e))
                out.append(((i, j), sp.factor(nu)))
    return out


fibM = sp.Matrix([[P1s**2 + P2s**2 * m**2 * w1**2, P2s**2 * m * w1],
                  [P2s**2 * m * w1, P2s**2]])
fibU = sp.diag(P1s**2, P2s**2)

print("MONODROMY factored equations:")
for ij, e in eqs_of(fibM, n, L6):
    print(f"  {ij}: {e}")
print("\nUNTWISTED factored equations:")
for ij, e in eqs_of(fibU, n, L6):
    print(f"  {ij}: {e}")
