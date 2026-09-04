#!/usr/bin/env python3
"""EXP-002: the algebraic relation for CG's (2,2) cubic, allowing the couplings alpha, beta in the
coefficients (momentum weight 6 = 2(i+j+k); alpha, beta carry weight 2 each in the scaling
x -> l^2 x, p -> p/l ... so a term alpha^m beta^n H^i Qa^j Qb^k needs 2(i+j+k) + 2(m+n)... we just
allow m+n <= 2 and let linear algebra decide)."""
import random, itertools, sympy as sp
x, y, px, py = sp.symbols("x y p_x p_y", positive=True)
al, be = sp.symbols("alpha beta", positive=True)
H2 = px*py + al/sp.sqrt(x) + be/sp.sqrt(y)
I2 = x*px**2*py - y*px*py**2 + be*x/sp.sqrt(y)*px - al*y/sp.sqrt(x)*py
Qa = x*px*py - y*py**2 + be*x/sp.sqrt(y) - al*sp.sqrt(x)
Qb = y*px*py - x*px**2 + al*y/sp.sqrt(x) - be*sp.sqrt(y)
Hs, Qas, Qbs = sp.symbols("H Q_a Q_b")
mons = [(i, j, k, m, n) for i in range(4) for j in range(4) for k in range(4) for m in range(3) for n in range(3)
        if i + j + k <= 3 and m + n <= 2 and (i + j + k) + (m + n) == 3]   # weight: H,Q ~ p^2 ~ alpha ~ beta under x->l^2 x
cs = sp.symbols(f"c0:{len(mons)}")
rng = random.Random(11)
rows, rhs = [], []
for _ in range(len(mons) + 12):
    d = {w: sp.Rational(rng.randint(1, 9), rng.randint(1, 4)) for w in (x, y, al, be)}
    d.update({px: sp.Rational(rng.randint(-9, 9), 3), py: sp.Rational(rng.randint(-9, 9), 5)})
    rows.append([H2.subs(d)**i * Qa.subs(d)**j * Qb.subs(d)**k * d[al]**m * d[be]**n for (i, j, k, m, n) in mons])
    rhs.append(I2.subs(d)**2)
sol = sp.linsolve((sp.Matrix(rows), sp.Matrix(rhs)), cs)
if sol == sp.EmptySet:
    print("no relation in this ansatz")
else:
    csol = list(sol)[0]
    P = sum(c * Hs**i * Qas**j * Qbs**k * al**m * be**n for c, (i, j, k, m, n) in zip(csol, mons))
    print("I^2 =", sp.factor(P))
    print("verified identically:", sp.simplify(sp.expand(I2**2 - P.subs({Hs: H2, Qas: Qa, Qbs: Qb}))) == 0)
