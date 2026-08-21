#!/usr/bin/env python3
"""ZV ranks 5 and 6 -- closing §98's last stated caveat.

§98's own words: "this closes the quadratic+quartic question; a rank>=6 tensor isn't excluded".
Ranks 2/3/4 are now closed symbolically (dimension = reducible span at each). This goes after
ranks 5 and 6, which retires that sentence.

ODD RANK IS A REAL QUESTION, not a formality: we established (against tabula's initial instinct)
that odd-rank Killing tensors are NOT excluded by the discrete symmetries -- p_t is a rank-1
example. So rank 5 is genuinely open, not obviously empty.

Every rank runs as its own process with rows banked, because this machine loses power without
warning (four cuts in three days) and the assembly is the expensive half.

Usage:  .venv/bin/python scripts/_kt_zv_high.py <delta> <rank>
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
import _kt_search as K
from _kt_zv import zv_inv, t, x, y, ph

delta, rank = int(sys.argv[1]), int(sys.argv[2])
K.set_dim((t, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
ginv = zv_inv(delta)
dens = set()
for i in range(4):
    for j in range(4):
        if ginv[i, j] != 0:
            d = sp.denom(sp.together(ginv[i, j]))
            if d != 1:
                dens.add(d)
L = sp.Integer(1)
for d in dens:
    L = sp.lcm(L, d)
L = sp.factor(L)
pL = sp.Poly(sp.expand(L), x, y)
# ansatz degrees MEASURED from the coefficient numerators, never inferred from the denominator --
# the heuristic that failed silently here and returned a solution space SMALLER than the reducible
# span, which is impossible and was only visible via the dim(reducible) <= dim(solution) invariant
nx = ny = 0
for i in range(4):
    for j in range(i, 4):
        if ginv[i, j] != 0:
            pN = sp.Poly(sp.expand(sp.cancel(sp.together(ginv[i, j]) * L)), x, y)
            nx, ny = max(nx, pN.degree(x)), max(ny, pN.degree(y))
dx, dy = max(pL.degree(x), nx) + 2, max(pL.degree(y), ny) + 2
print(f"ZV delta={delta}, RANK {rank}   ansatz x<={dx}, y<={dy}", flush=True)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ck = os.path.join(ROOT, "data", f"kt_zvhigh_d{delta}_r{rank}.pkl")
t0 = time.time()
d = K.solve_kt_sampled(rank, ginv, dx, dy, L, verbose=True, rows_ckpt=ck)
print(f"\n  ZV delta={delta} RANK {rank}: DIMENSION {d}   [{time.time()-t0:.0f}s]", flush=True)
# NO HAND-COUNT IS PRINTED HERE, DELIBERATELY. This line used to emit a table
# {1:2, 2:4, 3:6, 4:8, 5:10, 6:13} labelled "MUST be measured before it is believed", and the
# label did not save it: at delta=1 rank 5 it said 10 against a solution space of 14, which
# subtracts to "four irreducible Killing tensors on SCHWARZSCHILD" -- integrable since 1916.
# The count was missing L^2, whose rotation generators are not axisymmetric and so are absent
# from the rank-1 ansatz, while L^2 ITSELF is axisymmetric and present from rank 2 upward.
# A GENERATOR CAN BE INVISIBLE AT ITS OWN RANK AND PRESENT AT TWICE IT, so a hand-count built
# from the manifest Killing vectors agrees at low rank and diverges silently as it climbs.
# Note this is NOT caught by dim(reducible) <= dim(solution): an UNDER-counted reducible span
# keeps that inequality satisfied and simply moves the surplus into the "irreducible" column.
# The impossibility check guards ansatz-too-small; nothing free guards reducible-count-too-small.
print("  reducible span: run scripts/_kt_reducible.py -- it is MEASURED, not counted", flush=True)
