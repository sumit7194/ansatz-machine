#!/usr/bin/env python3
"""Symbolic higher-rank Killing-tensor search on ZIPOY-VOORHEES (the Weyl gamma-metric).

WHY THIS OBJECT, after closing the deformed Kerr. That metric is NOT a vacuum solution -- §119
proved R_ab != 0 -- so "no irreducible Killing tensor there" is a statement about an ad-hoc
testbed. Zipoy-Voorhees is an EXACT VACUUM solution, a genuine spacetime, and it is RATIONAL at
integer delta, so the same prover applies directly. Verified Ricci-flat at delta = 1 and 2 before
any of this was written (the Taub-NUT lesson: check the input is what you think it is).

WHAT IT UPGRADES. §97/§98 claim ZV delta != 1 has "no conserved quantity quadratic OR quartic in
the momenta" -- from a NUMERICAL null-space screen over sampled orbits, the same instrument class
whose failure modes tabula catalogued all week. This asks the same question of the KILLING
EQUATION, exactly, over GF(p).

THE CONTROL IS FREE, WHICH IS THE REASON TO DO IT THIS WAY. ZV at delta = 1 IS Schwarzschild, in
prolate spheroidal coordinates where nothing about the metric functions looks like 1 - 2M/r. So the
prover must recover Schwarzschild's Killing algebra in the SAME coordinate family and the SAME
denominator structure as the delta = 2 run -- an on-substrate positive control by construction.
That is precisely what our eps=0 control FAILED to be for the deformed Kerr, where eps=0 is Kerr
and therefore a different substrate.

Repro:  .venv/bin/python scripts/_kt_zv.py <delta> <rank>
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
import _kt_search as K

t, x, y, ph = sp.symbols("t x y phi", real=True)


def zv_metric(delta):
    """Zipoy-Voorhees in prolate spheroidal coordinates. delta = 1 is Schwarzschild."""
    F = ((x - 1) / (x + 1))**delta
    Hh = ((x**2 - 1) / (x**2 - y**2))**(delta**2)
    return sp.diag(-F,
                   Hh * (x**2 - y**2) / (F * (x**2 - 1)),
                   Hh * (x**2 - y**2) / (F * (1 - y**2)),
                   (x**2 - 1) * (1 - y**2) / F)


def zv_inv(delta):
    g = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(zv_metric(delta)[i, j])))
    gi = g.inv()
    return sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(gi[i, j])))


if __name__ == "__main__":
    delta = int(sys.argv[1])
    rank = int(sys.argv[2])
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
    # THE ANSATZ DEGREE MUST BE MEASURED FROM WHAT IT HAS TO REPRESENT, NOT GUESSED FROM THE
    # DENOMINATOR. Setting it to deg(L) + margin worked on the deformed Kerr by luck; on ZV it
    # failed silently in the worst way -- the solution space came out SMALLER than the reducible
    # span (3 vs 4 at rank 2), which is impossible, because every reducible IS a solution. Cause:
    # ZV's ((x^2-1)/(x^2-y^2))^(delta^2) factor drives the coefficient NUMERATORS to y-degree 10
    # while the denominator is only y-degree 2. So: read the numerator degrees off g^ab directly.
    nx = ny = 0
    for i in range(4):
        for j in range(i, 4):
            if ginv[i, j] != 0:
                pN = sp.Poly(sp.expand(sp.cancel(sp.together(ginv[i, j]) * L)), x, y)
                nx, ny = max(nx, pN.degree(x)), max(ny, pN.degree(y))
    dx, dy = max(pL.degree(x), nx) + 2, max(pL.degree(y), ny) + 2
    print(f"ZIPOY-VOORHEES delta={delta}, rank {rank}", flush=True)
    print(f"  denominator x-deg {pL.degree(x)}, y-deg {pL.degree(y)}; "
          f"coefficient numerators x-deg {nx}, y-deg {ny}; ansatz x<={dx}, y<={dy}",
          flush=True)
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ck = os.path.join(ROOT, "data", f"kt_zv_d{delta}_r{rank}.pkl")
    t0 = time.time()
    d = K.solve_kt_sampled(rank, ginv, dx, dy, L, verbose=True, rows_ckpt=ck)
    print(f"\n  ZV delta={delta} RANK {rank}: DIMENSION {d}   [{time.time()-t0:.0f}s]", flush=True)
