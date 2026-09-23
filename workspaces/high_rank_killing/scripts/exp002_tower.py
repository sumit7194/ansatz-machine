#!/usr/bin/env python3
"""EXP-002: does the Schouten-Nijenhuis tower continue past rank 3?  {Q1,F} and {Q2,F} are rank-4
Killing tensors (Jacobi identity); test membership in the rank-4 reducible span
    K2*K2 (21 products) + p_t F + p_s F
by an exact rank test at random rational phase-space points: G in span <=> the rank does not rise.
Pointwise evaluation from the small expressions Q1, Q2, F and their derivatives; rank over GF(p)
for two primes (a rational is mapped to num * den^-1 mod p). Instrumented after three silent stalls."""
import itertools, random, time, sympy as sp
from sympy import Rational as Q_
T0 = time.time()
def log(m): print(f"[{time.time()-T0:6.1f}s] {m}", flush=True)
exec(open("scripts/exp002_ppwave.py").read().split("# ----------------------------------------------------------------------------- CHECK 1")[0])
Hb = H - pt*ps
Q1 = sp.expand(pxi**2/16 + 2*a*xi*ps**2 - xi**2*Hb)
Q2 = sp.expand((pxi-peta)**2/32 + a*(xi-eta)*ps**2 - Q_(1,2)*(xi-eta)**2*Hb)
F = sp.expand(sp.cancel(sp.together(-4*poisson(Q1, Q2))))
log("F built")
K2 = [pt**2, pt*ps, ps**2, H, Q1, Q2]
dQ = {name: ([sp.diff(f, v) for v in XS], [sp.diff(f, v) for v in PS]) for name, f in (("Q1", Q1), ("Q2", Q2), ("F", F))}
log("derivatives built")
def ev(e, d):
    return sp.Rational(e.subs(d))
def bracket_at(A, B, d):
    dA, dB = dQ[A], dQ[B]
    return sum(ev(dA[0][i], d) * ev(dB[1][i], d) - ev(dA[1][i], d) * ev(dB[0][i], d) for i in range(N))
# NOTE (first run): randomising a PER POINT is wrong for an "in the span" test -- span coefficients
# must be constants, and the closure formula carries a^2 -- so a is FIXED per run below.
# Closure predicted by bracketing the relation F^2 = 4[(H-p_t p_s)(Q1^2+Q2^2) - a^2 Q1 p_s^4]:
#     {Q1,F} = -(H - p_t p_s) Q2,        {Q2,F} = (H - p_t p_s) Q1 - a^2 p_s^4 / 2
import sys
AFIX = Q_(sys.argv[1]) if len(sys.argv) > 1 else Q_(1)
log(f"a fixed at {AFIX}")
rng = random.Random(5)
rows_red, rows_G1, rows_G2, clos1, clos2 = [], [], [], [], []
for k in range(40):
    d = {a: AFIX}
    for v in XS + PS: d[v] = Q_(rng.randint(-9, 9), rng.randint(1, 5)) + Q_(1, 7)
    k2v = [ev(f, d) for f in K2]
    Fv = ev(F, d)
    rows_red.append([A*B for A, B in itertools.combinations_with_replacement(k2v, 2)] + [d[pt]*Fv, d[ps]*Fv])
    rows_G1.append(bracket_at("Q1", "F", d)); rows_G2.append(bracket_at("Q2", "F", d))
    Hbv = ev(Hb, d)
    clos1.append(rows_G1[-1] + Hbv * k2v[5]); clos2.append(rows_G2[-1] - Hbv * k2v[4] + AFIX**2 * d[ps]**4 / 2)
    if k % 10 == 9: log(f"{k+1} points evaluated")
def rank_modp(rows, p):
    M = [[(int(x.p) * pow(int(x.q), p - 2, p)) % p for x in row] for row in rows]
    rk, piv = 0, 0
    ncol = len(M[0])
    for c in range(ncol):
        pr = next((i for i in range(piv, len(M)) if M[i][c]), None)
        if pr is None: continue
        M[piv], M[pr] = M[pr], M[piv]
        inv = pow(M[piv][c], p - 2, p)
        M[piv] = [(x * inv) % p for x in M[piv]]
        for i in range(len(M)):
            if i != piv and M[i][c]:
                f = M[i][c]; M[i] = [(x - f * y) % p for x, y in zip(M[i], M[piv])]
        piv += 1; rk += 1
    return rk
for p in (2147483647, 2147483629):
    r0 = rank_modp(rows_red, p)
    r1 = rank_modp([r + [g] for r, g in zip(rows_red, rows_G1)], p)
    r2 = rank_modp([r + [g] for r, g in zip(rows_red, rows_G2)], p)
    log(f"mod {p}: reducible span rank {r0};  +{{Q1,F}} -> {r1};  +{{Q2,F}} -> {r2}")
    log(f"   {{Q1,F}}: {'REDUCIBLE (tower closes)' if r1 == r0 else 'NEW IRREDUCIBLE RANK 4'};   {{Q2,F}}: {'REDUCIBLE (tower closes)' if r2 == r0 else 'NEW IRREDUCIBLE RANK 4'}")
log(f"closure {{Q1,F}} + (H-p_t p_s)Q2 == 0 at all 40 points: {all(v == 0 for v in clos1)};   {{Q2,F}} - (H-p_t p_s)Q1 + a^2 p_s^4/2 == 0: {all(v == 0 for v in clos2)}")
log(f"{{Q1,F}} nonzero at points: {any(v != 0 for v in rows_G1)};  {{Q2,F}} nonzero: {any(v != 0 for v in rows_G2)}")
