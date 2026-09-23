#!/usr/bin/env python3
"""EXP-002 Tier 2/3: the sibling's modular nullspace prover, driven BY IMPORT on (a) its own
Cariglia-Galajinsky (2,2) control and (b) the Wick-rotated Lorentzian pp-wave.

Derives from ../conjecture_machine/scripts/_kt_search.py (solve_kt_modp), imported in place.
ckpt=None so nothing is written anywhere. Nothing of theirs is modified.

The number returned is the SAMPLED nullspace dimension (two primes must agree): an UPPER bound on
the dimension of the solution space within the ansatz  c_m(r,u) = poly_{<=deg}(r,u) / den.
Combined with the explicitly exhibited solutions (a LOWER bound) it closes the squeeze.

Coordinate slots: theirs are (t, r, u, phi) with (r, u) the dependent pair; here
  pp-wave:  (t, r, u, phi) = (t, xi, eta, s),  a = 1
  CG (2,2): their own cariglia_galajinsky_inv(alpha=1, beta=1) in (t, X, Y, s), x = X^2, y = Y^2
"""
import os, sys, time
sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
import sympy as sp
import _kt_search as K

print(f"PID {os.getpid()}  (single process, single core, no files written)", flush=True)
r, u = K.r, K.u
rho2 = r**2 + u**2
ginv_pp = sp.zeros(4, 4)
ginv_pp[0, 3] = ginv_pp[3, 0] = 1
ginv_pp[3, 3] = 4 * r / rho2          # 2U with U = 2 a xi / rho^2, a = 1
ginv_pp[1, 1] = ginv_pp[2, 2] = 1 / (8 * rho2)
ginv_cg = K.cariglia_galajinsky_inv(alpha=1, beta=1)

DEG = 6
for name, ginv, den, expect in (("CG (2,2) control", ginv_cg, r * u, {1: 2, 2: 6, 3: 11}),
                                ("Lorentzian pp-wave", ginv_pp, rho2, {1: 2, 2: 6, 3: 11})):
    print(f"\n=== {name}: ansatz poly deg <= ({DEG},{DEG}) / ({den}) ===", flush=True)
    for rank in (1, 2, 3):
        t0 = time.time()
        dim = K.solve_kt_modp(rank, ginv, DEG, DEG, den, ckpt=None, verbose=False)
        print(f"  rank {rank}: sampled nullspace dimension = {dim}   expected {expect[rank]}   "
              f"[{time.time()-t0:.1f}s]  {'OK' if dim == expect[rank] else '** MISMATCH **'}", flush=True)
