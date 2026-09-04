#!/usr/bin/env python3
"""EXP-002 follow-up: verify the algebraic relation exactly (symbolic a) and the rank of the reducible span."""
import random, sympy as sp
from sympy import Rational as Q_
exec(open("scripts/exp002_ppwave.py").read().split("# ----------------------------------------------------------------------------- CHECK 1")[0])
Hb = H - pt*ps
Q1 = sp.expand(pxi**2/16 + 2*a*xi*ps**2 - xi**2*Hb)
Q2 = sp.expand((pxi-peta)**2/32 + a*(xi-eta)*ps**2 - Q_(1,2)*(xi-eta)**2*Hb)
F_B = sp.expand(poisson(Q1, Q2))
F = -4*F_B                      # = Im F_D, verified identically in exp002_ppwave.py
rel = sp.expand(F**2 - 4*(Hb*(Q1**2 + Q2**2) - a**2*Q1*ps**4))
print("F^2 - 4[(H - p_t p_s)(Q1^2+Q2^2) - a^2 Q1 p_s^4] == 0 identically (symbolic a):", is_zero(rel))
rel1 = sp.expand(F**2 - 4*(Hb*(Q1**2 + Q2**2) - Q1*ps**4))
print("   (without the a^2: identically zero only at a=1?)  symbolic:", is_zero(rel1), "  at a=1:", is_zero(rel1.subs(a,1)))
K2 = [pt**2, pt*ps, ps**2, H, Q1, Q2]
red3 = [sp.expand(v*k) for v in (pt, ps) for k in K2]
rng = random.Random(7)
def rank_at_points(funcs, npts=40):
    rows = []
    for _ in range(npts):
        d = {a: Q_(rng.randint(1, 9), rng.randint(1, 5))}
        for v in XS + PS:
            d[v] = Q_(rng.randint(-9, 9), rng.randint(1, 5)) + Q_(1, 7)
        rows.append([f.subs(d) for f in funcs])
    return sp.Matrix(rows).rank()
print("rank of the 12 products (p_t,p_s) x K2 :", rank_at_points(red3), " (expect 10: two overlaps)")
print("rank with F adjoined                  :", rank_at_points(red3 + [F]), " (expect 11)")
print("rank with F and {Q1,Q2} adjoined      :", rank_at_points(red3 + [F, F_B]), " (expect 11: same direction)")
