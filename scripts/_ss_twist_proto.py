#!/usr/bin/env python3
"""Prototype — §114 Stage C: the TWIST axis of the atlas (geometric flux + the absorbable-monodromy trap).

Two twists, machine-separated:
 (i) ABSORBABLE MONODROMY (the folklore trap): fibre ds^2 = P1^2 dw1^2 + P2^2 (dw2 + m w1 dw1)^2.
     This is chi -> chi + const shift = large diffeo of T^2. PREDICTION: pure gauge -- the vacuum
     equations are m-INDEPENDENT (no potential; SS on metric-only T^2 stabilizes NOTHING).
 (ii) GEOMETRIC FLUX (the 2D affine algebra [e1,e2] = m e2): fibre ds^2 = P1^2 dw1^2 + P2^2 e^{2 m w1} dw2^2.
     Internal space now CURVED -> a genuine shape-dependent potential. Known global caveat (extract,
     don't hide): the 2D affine group is non-compact; T^2 periodicity is obstructed (the classic
     compactness obstruction of geometric flux). Locally the reduction is testable exactly.
     SS consistency = the w1-dependence must CANCEL in every equation (machine-checked).

Vacuum scan (constant moduli, 4D static max-sym base, flux n, Lambda6):
  E4: m!=0 alone            -> stabilize anything? (expect: runaway, extract obstruction)
  E5: m, n, L6 all on       -> shape AND volume stabilized? THE prize entry.
Durable log data/ss_twist_proto.log.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry, zero_simplify

t, r, th, ph, w1, w2 = sp.symbols("t r theta phi w1 w2", real=True)
lam, n, L6, m = sp.symbols("lam n Lambda6 m", real=True)
P1, P2 = sp.symbols("Phi1 Phi2", positive=True)

X6 = [t, r, th, ph, w1, w2]


def einstein_eqs(fib, nv, L6v, flux_profile=1):
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
    G[4, 5] = nv * flux_profile          # flux wraps the internal VOLUME form, not the coordinate form
    G[5, 4] = -nv * flux_profile
    geo = Geometry(g6, X6)
    R6 = geo.ricci
    g6inv = g6.inv()
    Rs = sp.simplify(sum(g6inv[i, j] * R6[i, j] for i in range(6) for j in range(6)))
    Gup = sp.zeros(6)
    for i in range(6):
        for j in range(6):
            Gup[i, j] = sum(g6inv[i, p] * g6inv[j, q] * G[p, q] for p in range(6) for q in range(6))
    G2 = sp.simplify(sum(G[i, j] * Gup[i, j] for i in range(6) for j in range(6)))
    # Maxwell check (nv could interplay with twist volume element)
    sq = sp.sqrt(-g6.det()).subs(sp.Abs(sp.sin(th)), sp.sin(th))
    mx = [zero_simplify(sp.simplify(sum(sp.diff(sq * Gup[a, b], X6[a]) for a in range(6)) / sq))
          for b in range(6)]
    eqs, wdep = set(), []
    for i in range(6):
        for j in range(i, 6):
            Tij = sum(G[i, p] * g6inv[p, q] * G[j, q] for p in range(6) for q in range(6)) \
                - sp.Rational(1, 4) * g6[i, j] * G2
            e = sp.simplify(R6[i, j] - sp.Rational(1, 2) * g6[i, j] * Rs + L6v * g6[i, j] - Tij)
            if e != 0:
                if e.has(w1) or e.has(w2):
                    wdep.append(((i, j), e))          # SS consistency violation marker
                nu, _ = sp.fraction(sp.together(e))
                eqs.add(sp.factor(nu))
    return sorted(eqs, key=sp.count_ops), wdep, mx


print("§114 Stage C -- the twist axis\n")

print("(i) ABSORBABLE MONODROMY  fibre: P1^2 dw1^2 + P2^2 (dw2 + m w1 dw1)^2, plus flux n, L6")
sys.stdout.flush()
# build via frame: dw2 + m w1 dw1 -> fibre matrix [[P1^2 + P2^2 m^2 w1^2, P2^2 m w1],[P2^2 m w1, P2^2]]
fibA = sp.Matrix([[P1**2 + P2**2 * m**2 * w1**2, P2**2 * m * w1],
                  [P2**2 * m * w1, P2**2]])
eqsA, wdepA, mxA = einstein_eqs(fibA, n, L6)
print(f"  Maxwell residuals: {mxA}")
print(f"  w-dependent (SS-inconsistent) equations: {len(wdepA)}")
print(f"  independent equations: {eqsA}")
print(f"  m appears in the system: {any(e.has(m) for e in eqsA)}   (False = twist ABSORBED, no potential)\n")

print("(ii) GEOMETRIC FLUX  fibre: P1^2 dw1^2 + P2^2 e^{2 m w1} dw2^2, flux G = n e^{m w1} dw1^dw2, L6")
print("     (flux profile e^{m w1} = the internal volume form -- machine-caught: constant flux")
print("      VIOLATES Maxwell on the twisted space)")
sys.stdout.flush()
fibB = sp.diag(P1**2, P2**2 * sp.exp(2 * m * w1))
eqsB, wdepB, mxB = einstein_eqs(fibB, n, L6, flux_profile=sp.exp(m * w1))
print(f"  Maxwell residuals: {mxB}")
print(f"  w-dependent (SS-inconsistent) equations: {len(wdepB)} {[ij for ij, _ in wdepB]}")
print(f"  independent equations: {eqsB}")
print("\n  E4: m!=0, n=0, L6=0:")
eqs4 = [sp.factor(e.subs([(n, 0), (L6, 0)])) for e in eqsB]
eqs4 = [e for e in eqs4 if e != 0]
print(f"    equations: {eqs4}")
print(f"    solve (lam,P1): {sp.solve(eqs4, [lam, P1], dict=True)}")
print("\n  E5: m, n, L6 all free -- solve for the MODULI (P1, P2) + lam at given couplings:")
sol5 = sp.solve(eqsB, [P1, P2, lam], dict=True)
print(f"    {sol5}")
print("    -> if (P1, P2) both fixed by (m, n, L6): SHAPE AND VOLUME stabilized (the prize entry)")
print("\nDONE.")
