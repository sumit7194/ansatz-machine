#!/usr/bin/env python3
"""Build the operator matrix from 3 SymPy brackets per momentum monomial, not one per column.

THE COST IT REMOVES. The operator {H0, w_j} is built one SymPy bracket and one SymPy clear per
basis column -- 75,516 of each at rank 6, about 90 minutes before any solving starts.

WHY 3 PER MONOMIAL SUFFICE. A basis column is w = m(p) * x^a y^b / den, with m a momentum monomial.
In the Poisson bracket, (a, b) enter only through d(x^a y^b)/dx = a x^(a-1) y^b and
d(x^a y^b)/dy = b x^a y^(b-1). So for each monomial m there are three fixed polynomials U, V, W with

        cleared(m, a, b)  =  x^a y^b U  +  a x^(a-1) y^b V  +  b x^a y^(b-1) W

and they are read off the three columns (a,b) = (0,0), (1,0), (0,1):
        U = cleared(m,0,0),   V = cleared(m,1,0) - x U,   W = cleared(m,0,1) - y U.
Every other column is then integer shifting and scaling, mod p.

THE COMMON DENOMINATOR IS THE SAME. Each column is a combination of the three templates with
monomial multipliers, so its denominator divides theirs; and the templates are themselves
combinations of columns. Hence lcm over the templates = lcm over all columns = the D the full build
computes. Checked, not assumed, in the self-test.

VALIDATION: every column must equal PB.clear of its own SymPy bracket, exactly.
"""
import sympy as sp

import _kt_perturb as PB

x, y = sp.symbols("x y", real=True)


def _shift(d, a, b):
    return {(e, (j + a, k + b)): v for (e, (j, k)), v in d.items()}


def _axpy(out, d, scale, a, b, p):
    """out += scale * shift(d, a, b)   (mod p)"""
    for (e, (j, k)), v in d.items():
        key = (e, (j + a, k + b))
        out[key] = (out.get(key, 0) + scale * v) % p


def operator_from_templates(H0, mons, dx, dy, den, p, verbose=False):
    """Return (dicts0, D) in coefficient_basis order: for each monomial, a in 0..dx, b in 0..dy."""
    specs = []
    for mi in range(len(mons)):
        for (a, b) in ((0, 0), (1, 0), (0, 1)):
            F = [sp.Integer(0)] * len(mons)
            F[mi] = x**a * y**b / den
            specs.append((H0, F))
    raws, dens = PB.build_columns(specs, mons, False)
    D = sp.Integer(1)
    for d_ in dens:
        D = sp.lcm(D, d_)
    cl = [PB.clear(r, D, p) for r in raws]
    dicts0 = []
    for mi in range(len(mons)):
        U = cl[3 * mi]
        V = dict(cl[3 * mi + 1])
        _axpy(V, U, p - 1, 1, 0, p)          # V = cleared(1,0) - x U
        W = dict(cl[3 * mi + 2])
        _axpy(W, U, p - 1, 0, 1, p)          # W = cleared(0,1) - y U
        V = {k: v for k, v in V.items() if v}
        W = {k: v for k, v in W.items() if v}
        for a in range(dx + 1):
            for b in range(dy + 1):
                out = _shift(U, a, b)
                if a:
                    _axpy(out, V, a % p, a - 1, b, p)
                if b:
                    _axpy(out, W, b % p, a, b - 1, p)
                dicts0.append({k: v for k, v in out.items() if v})
    if verbose:
        print(f"    operator from templates: {3 * len(mons)} SymPy brackets for "
              f"{len(dicts0)} columns", flush=True)
    return dicts0, D


if __name__ == "__main__":
    import os
    import random
    import sys
    import time
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _kt_double as KD
    import _kt_exact as EX
    import _kt_metrics as MM
    import _kt_search as K

    p = 2147483647
    t, ph = sp.symbols("t phi", real=True)
    K.set_dim((t, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    GI = KD.kerr_chi_pieces()
    gi0 = GI[0]
    L, _, _ = MM.denominator(gi0)
    H0 = KD.hamiltonian(gi0)
    ok = True

    def setup(rank, denpow, margin):
        den = L ** denpow
        _, prods, _ = EX.generators(gi0, rank, den)
        bx, by = EX.reducible_box(prods, den)
        dx, dy = bx + margin, by + margin
        mons = K.monomials(rank)
        cols, F_cos = PB.coefficient_basis(mons, dx, dy, den)
        return den, dx, dy, mons, cols, F_cos

    # ---- rank 2, the production config (denpow 6, margin 6): EVERY column against SymPy.
    # --quick (the verify.sh gate): D still over every column, but 300 random columns cleared.
    quick = "--quick" in sys.argv
    den, dx, dy, mons, cols, F_cos = setup(2, 6, 6)
    t0 = time.time(); fast, Dt = operator_from_templates(H0, mons, dx, dy, den, p); tf = time.time() - t0
    t0 = time.time()
    raws, dens = PB.build_columns([(H0, F) for F in F_cos], mons, False)
    Df = sp.Integer(1)
    for d_ in dens:
        Df = sp.lcm(Df, d_)
    idx = random.Random(2).sample(range(len(raws)), 300) if quick else range(len(raws))
    nbad = sum(1 for j in idx if fast[j] != PB.clear(raws[j], Df, p))
    tr = time.time() - t0
    sameD = sp.simplify(Dt - Df) == 0
    print(f"  rank 2, denpow 6, box {dx}x{dy}: {len(cols)} columns   same D {sameD}   "
          f"{len(idx)} compared, differing {nbad}   templates {tf:.1f}s vs full {tr:.1f}s",
          flush=True)
    ok &= sameD and nbad == 0 and len(fast) == len(raws)
    if quick:
        print("\n  " + ("VALIDATED (quick): template-built operator matches the full SymPy build."
                        if ok else "FAILED"))
        sys.exit(0 if ok else 1)

    # ---- rank 4, denpow 7, margin 6 (the rank-4 verdict's config): D over ALL columns, and a
    # random sample of columns cleared by SymPy -- the full clear there takes ~25 minutes.
    den, dx, dy, mons, cols, F_cos = setup(4, 7, 6)
    t0 = time.time(); fast, Dt = operator_from_templates(H0, mons, dx, dy, den, p); tf = time.time() - t0
    raws, dens = PB.build_columns([(H0, F) for F in F_cos], mons, False)
    Df = sp.Integer(1)
    for d_ in dens:
        Df = sp.lcm(Df, d_)
    sameD = sp.simplify(Dt - Df) == 0
    rng = random.Random(4)
    sample = rng.sample(range(len(cols)), 400)
    nbad = sum(1 for j in sample if fast[j] != PB.clear(raws[j], Df, p))
    print(f"  rank 4, denpow 7, box {dx}x{dy}: {len(cols)} columns   same D {sameD}   "
          f"sampled 400, differing {nbad}   templates {tf:.1f}s", flush=True)
    ok &= sameD and nbad == 0

    print("\n  " + ("VALIDATED: template-built operator is identical to the full SymPy build."
                    if ok else "FAILED"))
    sys.exit(0 if ok else 1)
