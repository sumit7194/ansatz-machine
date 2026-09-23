#!/usr/bin/env python3
"""EXP-003 Tier 2/3 for the 5D member: lower bound on dim K3 from the exhibited solutions
(reducible span K1*K2 + F, exact rank at random rational points, my code) and upper bound from
the sibling's sampled modular nullspace (_kt_search.solve_kt_modp, imported, set_dim to 5D as they
did for their own cg5d control; ckpt=None, nothing written).  a = kappa = 1."""
import os, sys, time, random, itertools
import sympy as sp
from sympy import Rational as Q_
sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
import _kt_search as K
print(f"PID {os.getpid()}", flush=True)
t, r, u, ph, w = K.t, K.r, K.u, K.ph, sp.Symbol("w", real=True)
pt, pr, pu, pp, pw = K.pt, K.pr, K.pu, K.pp, sp.Symbol("p_w", real=True)
K.set_dim((t, r, u, ph, w), (pt, pr, pu, pp, pw), (1, 2))
rho2 = r**2 + u**2
# slots: (t, r, u, ph, w) = (t, xi, eta, s, v)
A = 2 * r / rho2
U = 2 * r / rho2 + (u**2 - 3 * r**2) / (2 * rho2**2)
g = sp.zeros(5, 5)
g[0, 0] = -2 * U; g[0, 3] = g[3, 0] = 1; g[0, 4] = g[4, 0] = A; g[4, 4] = 1; g[1, 1] = g[2, 2] = 8 * rho2
ginv = g.inv().applyfunc(sp.cancel)
H = sp.expand(Q_(1, 2) * sum(ginv[i, j] * K.MOM[i] * K.MOM[j] for i in range(5) for j in range(5)))
def poisson(Aa, Bb):
    return sp.expand(sum(sp.diff(Aa, K.COORDS[i]) * sp.diff(Bb, K.MOM[i]) - sp.diff(Aa, K.MOM[i]) * sp.diff(Bb, K.COORDS[i]) for i in range(5)))
K0 = pt * pp + pw**2 / 2
Hb = H - K0
f_xi = 2 * pp**2 * r + pp**2 / 2 - 2 * pp * pw * r          # sigma + a' xi with a=kappa=1
Q1 = sp.expand(pr**2 / 16 + f_xi - r**2 * Hb)
# rotated: f'(xi') + g'(eta') from  sigma + a' xi,  xi = (xi'+eta')/sqrt2  ->  f' = sigma + a' xi'/sqrt2
ap = 2 * pp**2 - 2 * pp * pw
Q2 = sp.expand(pp**2 / 2 + ap * (r - u) / 2 + (pr - pu)**2 / 32 - Q_(1, 2) * (r - u)**2 * Hb)
assert sp.cancel(sp.together(poisson(H, Q1))) == 0 and sp.cancel(sp.together(poisson(H, Q2))) == 0
F = sp.expand(sp.cancel(sp.together(-4 * poisson(Q1, Q2))))
assert sp.cancel(sp.together(poisson(H, F))) == 0
print("H, Q1, Q2, F rebuilt in the sibling's coordinate slots; conservation re-verified", flush=True)
K1 = [pt, pp, pw]
K2 = [x * y for x, y in itertools.combinations_with_replacement(K1, 2)] + [H, Q1, Q2]
red3 = [sp.expand(x * y) for x in K1 for y in K2]
rng = random.Random(3)
allv = list(K.COORDS) + list(K.MOM)
def rank_at_points(funcs, npts=50):
    rows = []
    for _ in range(npts):
        d = {v_: Q_(rng.randint(-9, 9), rng.randint(1, 5)) + Q_(1, 7) for v_ in allv}
        rows.append([f.subs(d) for f in funcs])
    M = [[(int(x.p) * pow(int(x.q), 2147483647 - 2, 2147483647)) % 2147483647 for x in row] for row in rows]
    p = 2147483647; rk = 0; piv = 0
    for c in range(len(M[0])):
        pr_ = next((i for i in range(piv, len(M)) if M[i][c]), None)
        if pr_ is None: continue
        M[piv], M[pr_] = M[pr_], M[piv]; inv = pow(M[piv][c], p - 2, p); M[piv] = [(x * inv) % p for x in M[piv]]
        for i in range(len(M)):
            if i != piv and M[i][c]:
                f = M[i][c]; M[i] = [(x - f * y) % p for x, y in zip(M[i], M[piv])]
        piv += 1; rk += 1
    return rk
print(f"LOWER BOUNDS (exact rank at 50 random points, mod p):  K1 = {rank_at_points(K1)}   K2 = {rank_at_points(K2)}   "
      f"K1*K2 = {rank_at_points(red3)}   K1*K2 + F = {rank_at_points(red3 + [F])}", flush=True)
DEG = 8
den = rho2**2
for rank in (1, 2, 3):
    t0 = time.time()
    dim = K.solve_kt_modp(rank, ginv, DEG, DEG, den, ckpt=None, verbose=False)
    print(f"UPPER BOUND sibling prover, rank {rank}, ansatz poly<=({DEG},{DEG})/rho^4: sampled nullspace dimension = {dim}   [{time.time()-t0:.0f}s]", flush=True)
