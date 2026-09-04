#!/usr/bin/env python3
"""EXP-002 interpretive check, in CG's OWN (2,2) variables (arXiv:1503.02162 eq. 20, footnote 9):
is their published cubic I the Poisson bracket of two quadratic integrals?  Everything printed
explicitly so the write-up can show the computation rather than assert it."""
import random, sympy as sp
x, y, px, py = sp.symbols("x y p_x p_y", positive=True)
al, be = sp.symbols("alpha beta", positive=True)
H2 = px*py + al/sp.sqrt(x) + be/sp.sqrt(y)
I2 = x*px**2*py - y*px*py**2 + be*x/sp.sqrt(y)*px - al*y/sp.sqrt(x)*py
Qa = x*px*py - y*py**2 + be*x/sp.sqrt(y) - al*sp.sqrt(x)        # footnote 9; last term fixed in exp002_ppwave.py
Qb = y*px*py - x*px**2 + al*y/sp.sqrt(x) - be*sp.sqrt(y)        # image of Qa under (x,alpha) <-> (y,beta), a symmetry of H2
def pb(A, B):
    return sp.expand(sum(sp.diff(A, q)*sp.diff(B, p) - sp.diff(A, p)*sp.diff(B, q) for q, p in ((x, px), (y, py))))
z = lambda e: sp.simplify(sp.expand(e)) == 0
print("H  =", H2)
print("I  =", I2, "   (CG eq. 20)")
print("Qa =", Qa, "   (CG footnote 9)")
print("Qb =", Qb, "   (mirror of Qa)")
print("{H,Qa} = 0:", z(pb(H2, Qa)), "  {H,Qb} = 0:", z(pb(H2, Qb)), "  {H,I} = 0:", z(pb(H2, I2)))
Bq = sp.expand(pb(Qa, Qb))
print("{Qa,Qb} =", sp.collect(Bq, [px, py]))
print("I + (1/2){Qa,Qb} == 0 identically:", z(I2 + Bq/2))
rng = random.Random(3)
def jac_rank(fs, npts=6):
    best = 0
    for _ in range(npts):
        d = {w: sp.Rational(rng.randint(1, 9), rng.randint(1, 4)) for w in (x, y, al, be)}
        d.update({px: sp.Rational(rng.randint(-9, 9), 3), py: sp.Rational(rng.randint(-9, 9), 5)})
        best = max(best, sp.Matrix([[sp.diff(f, w).subs(d) for w in (x, y, px, py)] for f in fs]).rank())
    return best
print("functional rank (H, Qa, I)     =", jac_rank([H2, Qa, I2]), "  (CG footnote 9: 'functionally independent' -- true)")
print("functional rank (H, Qa, Qb)    =", jac_rank([H2, Qa, Qb]))
print("functional rank (H, Qa, Qb, I) =", jac_rank([H2, Qa, Qb, I2]), "  (max possible for 2 dof is 3: I is dependent on H, Qa, Qb)")
# the algebraic relation in CG's variables
Hs, Qas, Qbs = sp.symbols("H Q_a Q_b")
mons = [(i, j, k) for i in range(4) for j in range(4) for k in range(4) if i + j + k == 3]
cs = sp.symbols(f"c0:{len(mons)}")
rows, rhs = [], []
for _ in range(len(mons) + 8):
    d = {w: sp.Rational(rng.randint(1, 9), rng.randint(1, 4)) for w in (x, y, al, be)}
    d.update({px: sp.Rational(rng.randint(-9, 9), 3), py: sp.Rational(rng.randint(-9, 9), 5)})
    rows.append([H2.subs(d)**i * Qa.subs(d)**j * Qb.subs(d)**k for (i, j, k) in mons]); rhs.append(I2.subs(d)**2)
sol = sp.linsolve((sp.Matrix(rows), sp.Matrix(rhs)), cs)
if sol != sp.EmptySet:
    csol = list(sol)[0]
    P = sum(c * Hs**i * Qas**j * Qbs**k for c, (i, j, k) in zip(csol, mons))
    Pexpr = P.subs({Hs: H2, Qas: Qa, Qbs: Qb})
    print("I^2 =", sp.factor(P), "   verified identically:", z(I2**2 - Pexpr))
else:
    print("no cubic relation I^2 = P(H,Qa,Qb) with constant coefficients (parameters alpha, beta may enter)")
