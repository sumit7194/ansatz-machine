#!/usr/bin/env python3
"""One rank of the deformed-Kerr Killing-tensor search, as its own process.

LIVES IN THE REPO, NOT THE SCRATCHPAD. This machine loses power in the daytime and /private/tmp
does not survive a reboot -- a driver script written there was wiped mid-investigation. Anything
needed to resume belongs under version control.

Usage:  .venv/bin/python scripts/_kt_deformed_rank.py <rank> [eps] [degree_bump]

ROBUSTNESS, which is why eps and degree_bump are arguments. A null is only as good as the family
it is stated over, and ours was scoped to eps = 2 with numerator degrees (12,12). Two things it
could be hiding: the ansatz might be too small to hold a tensor that exists (basis adequacy -- the
failure that returned dimension 3 and then dimension 0 on Kerr), or the null might be an accident
of one deformation value. Bumping the degrees and changing eps tests exactly those.

Assembled rows are banked to data/kt_def_rows_r<rank>.pkl, so a cut during the (cheap) modular-rank
step no longer throws away the (expensive) assembly.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
import _kt_search as K

rank = int(sys.argv[1])
eps_val = sp.Integer(sys.argv[2]) if len(sys.argv) > 2 else sp.Integer(2)
bump = int(sys.argv[3]) if len(sys.argv) > 3 else 0
r, u = K.r, K.u
ginv = K.deformed_kerr_inv(eps=eps_val)

# the ansatz denominator must contain every denominator the inverse metric carries, or the span
# cannot hold even a constant coefficient -- the failure that returned dimension 0 on Kerr
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
pL = sp.Poly(sp.expand(L), r, u)
dr, du = pL.degree(r) + 1 + bump, pL.degree(u) + 2 + bump
print(f"  common denominator: r-degree {pL.degree(r)}, u-degree {pL.degree(u)}; "
      f"numerator degrees r<={dr}, u<={du}", flush=True)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ckpt = os.path.join(ROOT, "data", f"kt_def_rows_r{rank}_e{eps_val}_b{bump}.pkl")
t0 = time.time()
d = K.solve_kt_sampled(rank, ginv, dr, du, L, verbose=True, rows_ckpt=ckpt)
print(f"\nDEFORMED KERR (a=3/5, eps={eps_val}, degree bump +{bump})  "
      f"RANK {rank}: DIMENSION {d}   [{time.time()-t0:.0f}s]",
      flush=True)
