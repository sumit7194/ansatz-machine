#!/usr/bin/env python3
"""Emit a COEFFICIENT-FUNCTION BASIS for a numerical conservation screen, independent BY
CONSTRUCTION rather than by numerical filtering afterward.

THE REQUEST (bridge, 2026-08-22): their degree-4 screen died because a degree-4 coefficient is a
PRODUCT of degree-2 coefficients, so they formed all pairwise products -- 1260 columns of true
numerical rank ~259 -- and projecting onto the independent subspace destroyed conserved directions
lying partly in the discarded part. Representation failure, not sampling.

THE TRAP IN THE OBVIOUS ANSWER, which is why this script does not do the obvious thing. The
tempting move is to hand them the coefficient span of my own reducible products, reduced to an
independent subset. That basis is CIRCULAR: it is exactly large enough to hold the reducibles, so
their screen would recover the reducibles and could not possibly find anything else. A calibration
it passes by construction proves nothing about the treatment.

WHAT IT EMITS INSTEAD. The monomial basis {x^i y^j / L^k}, where L is the metric's common
denominator. These are linearly independent as rational functions for free -- distinct numerator
monomials over a common denominator -- so there is no rank estimate, no tolerance, and no
catastrophic cancellation anywhere in the construction. The degree bounds are MEASURED: chosen as
the smallest box that represents every known reducible product at that rank, then reported, so the
basis provably CONTAINS the calibration targets while being strictly larger than their span.

k=1 reproduces my prover's scope. k=2 is the region my prover is blind in (not negative -- blind),
which is exactly where an irreducible tensor could hide from me and not from them.

Repro:  .venv/bin/python scripts/_kt_emit_basis.py <delta> <rank> <den_power>
"""
import os
import sys
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
import _kt_reducible as R
import _kt_zv as ZV

t, x, y, ph = R.CO
MO = R.MO


def main():
    delta, rank, k = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    ginv = ZV.zv_inv(delta)
    H = sp.cancel(sp.together(sum(ginv[i, j] * MO[i] * MO[j] for i in range(4) for j in range(4))))
    Lsq = (1 - y**2) * MO[2]**2 + MO[3]**2 / (1 - y**2)

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

    gens = [("p_t", MO[0], 1), ("p_phi", MO[3], 1), ("H", H, 2)]
    if sp.cancel(sp.together(sp.expand(R.poisson(H, Lsq)))) == 0:
        gens.append(("Lsq", Lsq, 2))
    degs = [d for _, _, d in gens]

    # MEASURE the box: the smallest (dx, dy) that holds every reducible product at this rank,
    # written over L^k. Not inferred, not padded by a guessed margin -- read off the numerators.
    dx = dy = 0
    prods = []
    for expo in itertools.product(*[range(rank // d + 1) for d in degs]):
        if sum(e * d for e, d in zip(expo, degs)) != rank:
            continue
        lab = "*".join(f"{gens[i][0]}^{e}" if e > 1 else gens[i][0]
                       for i, e in enumerate(expo) if e)
        v = sp.Integer(1)
        for i, e in enumerate(expo):
            if e:
                v *= gens[i][1]**e
        prods.append((lab, v))
        for coeff in sp.Poly(sp.expand(v), *MO).coeffs():
            num, den = sp.fraction(sp.cancel(sp.together(coeff)))
            q = sp.cancel(sp.together(L**k / den))
            if sp.denom(q) != 1:
                print(f"  !! {lab} needs a denominator beyond L^{k}", flush=True)
                continue
            p = sp.Poly(sp.expand(num * q), x, y)
            dx, dy = max(dx, p.degree(x)), max(dy, p.degree(y))

    print(f"ZV delta={delta}, momentum degree {rank}, denominator power k={k}")
    print(f"  L = {L}")
    print(f"  reducible products at this degree: {len(prods)}")
    print(f"  MEASURED numerator box that holds every one of them over L^{k}: "
          f"x<={dx}, y<={dy}")
    n = (dx + 1) * (dy + 1)
    print(f"  => COEFFICIENT BASIS: {{ x^i y^j / L^{k} : 0<=i<={dx}, 0<=j<={dy} }}  "
          f"= {n} functions")
    print(f"     linearly independent BY CONSTRUCTION (distinct numerator monomials over a")
    print(f"     common denominator) -- no rank estimate, no tolerance, no cancellation.")
    print(f"  With {sp.binomial(rank + 3, 3)} momentum monomials of degree {rank}: "
          f"{n * sp.binomial(rank + 3, 3)} screen columns.")
    print()
    print(f"  CALIBRATION TARGETS -- your screen must return exactly {len(prods)} at delta={delta}:")
    for lab, _ in prods:
        print(f"     {lab}")
    print()
    print(f"  DENOMINATOR, expanded, for direct use:")
    print(f"     L^{k} = {sp.expand(L**k)}")


if __name__ == "__main__":
    main()
