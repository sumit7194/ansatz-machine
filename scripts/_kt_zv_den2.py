#!/usr/bin/env python3
"""ZIPOY-VOORHEES Killing-tensor search at den^2 -- the region the den^1 prover is BLIND in.

WHY THIS AND NOT ANOTHER RANK. §124 closed ranks 1-6 at den^1 and its headline caveat is that a
Killing tensor whose coefficients carry L^2 produces THE SAME CLEAN INTEGER as its absence: the
prover is blind there, not negative. That is the only open region where a positive result would be
a discovery rather than an extension of a map.

THE BOX IS NOT SIZED TO THE REDUCIBLES, DELIBERATELY. Choosing the smallest box that holds the
known reducible products would make the calibration pass BY CONSTRUCTION and leave an irreducible
tensor no room to appear -- the circularity we refused to export to the bridge's screen. The box
here is the measured reducible-holding box PLUS A MARGIN OF 4 in each variable, so the search space
strictly contains what it must contain and is strictly larger than it.

A FREE STRUCTURAL CHECK COMES WITH IT. Any p/L equals (p*L)/L^2, so with the margin chosen below
the den^1 ansatz sits INSIDE the den^2 ansatz. Therefore dim(den^2 solution) >= dim(den^1 solution)
ALWAYS. A den^2 answer below the den^1 answer is impossible and condemns the run -- the same class
of guard as dim(reducible) <= dim(solution), and it costs nothing.

Repro:  .venv/bin/python scripts/_kt_zv_den2.py <delta> <rank>
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
import _kt_search as K
import _kt_zv as ZV

MARGIN = 4

t, x, y, ph = sp.symbols("t x y phi", real=True)

if __name__ == "__main__":
    delta, rank = int(sys.argv[1]), int(sys.argv[2])
    K.set_dim((t, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    ginv = ZV.zv_inv(delta)
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

    # the reducible-holding box at den^2, MEASURED the same way _kt_emit_basis.py measures it
    import itertools
    import _kt_reducible as R
    H = sp.cancel(sp.together(sum(ginv[i, j] * R.MO[i] * R.MO[j]
                                  for i in range(4) for j in range(4))))
    Lsq = (1 - y**2) * R.MO[2]**2 + R.MO[3]**2 / (1 - y**2)
    gens = [("p_t", R.MO[0], 1), ("p_phi", R.MO[3], 1), ("H", H, 2)]
    if sp.cancel(sp.together(sp.expand(R.poisson(H, Lsq)))) == 0:
        gens.append(("Lsq", Lsq, 2))
    degs = [d for _, _, d in gens]
    bx = by = 0
    nred = 0
    for expo in itertools.product(*[range(rank // d + 1) for d in degs]):
        if sum(e * d for e, d in zip(expo, degs)) != rank:
            continue
        nred += 1
        v = sp.Integer(1)
        for i, e in enumerate(expo):
            if e:
                v *= gens[i][1]**e
        for coeff in sp.Poly(sp.expand(v), *R.MO).coeffs():
            num, den = sp.fraction(sp.cancel(sp.together(coeff)))
            q = sp.cancel(sp.together(L**2 / den))
            assert sp.denom(q) == 1, "a reducible needs more than L^2 -- box is not valid"
            pp = sp.Poly(sp.expand(num * q), x, y)
            bx, by = max(bx, pp.degree(x)), max(by, pp.degree(y))

    dx, dy = bx + MARGIN, by + MARGIN
    print(f"ZV delta={delta}, RANK {rank}, DENOMINATOR L^2", flush=True)
    print(f"  reducible-holding box x<={bx}, y<={by}; ansatz box x<={dx}, y<={dy} "
          f"(margin {MARGIN})", flush=True)
    print(f"  {nred} reducible products at this rank, all representable at den^2", flush=True)
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ck = os.path.join(ROOT, "data", f"kt_zvd2_d{delta}_r{rank}.pkl")
    t0 = time.time()
    # --modp reduces each row mod p AS IT IS ASSEMBLED, so the exact-integer Python structure never
    # exists. Same system, same points, same seed -- different storage. It must reproduce a known
    # rung EXACTLY before it is used on one with no known answer.
    if "--modp" in sys.argv:
        d = K.solve_kt_modp(rank, ginv, dx, dy, L**2, verbose=True, ckpt=ck + ".modp")
    else:
        d = K.solve_kt_sampled(rank, ginv, dx, dy, L**2, verbose=True, rows_ckpt=ck)
    print(f"\n  ZV delta={delta} RANK {rank} den^2: DIMENSION {d}   [{time.time()-t0:.0f}s]",
          flush=True)
