#!/usr/bin/env python3
"""EXP-002: functional rank of (p_t, p_s, H, Q1, F) WITHOUT Q2 -- CG's footnote-9 framing."""
import random, sympy as sp
from sympy import Rational as Q_
exec(open("scripts/exp002_ppwave.py").read().split("# ----------------------------------------------------------------------------- CHECK 1")[0])
Hb = H - pt*ps
Q1 = sp.expand(pxi**2/16 + 2*a*xi*ps**2 - xi**2*Hb)
Q2 = sp.expand((pxi-peta)**2/32 + a*(xi-eta)*ps**2 - Q_(1,2)*(xi-eta)**2*Hb)
F = sp.expand(-4*poisson(Q1, Q2))
rng = random.Random(11); allv = XS + PS
for trial in range(3):
    d = {a: Q_(rng.randint(1, 9), rng.randint(1, 5))}
    for v in allv: d[v] = Q_(rng.randint(-9, 9), rng.randint(1, 5)) + Q_(1, 7)
    J = lambda fs: sp.Matrix([[sp.diff(f, v).subs(d) for v in allv] for f in fs]).rank()
    print(f"trial {trial}: rank(p_t,p_s,H,Q1,F) = {J([pt,ps,H,Q1,F])}   rank(p_t,p_s,H,Q1) = {J([pt,ps,H,Q1])}   rank(p_t,p_s,H,Q1,Q2,F) = {J([pt,ps,H,Q1,Q2,F])}")
