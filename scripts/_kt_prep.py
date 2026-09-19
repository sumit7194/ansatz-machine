#!/usr/bin/env python3
"""Rescale already-cleared columns to a bigger common denominator -- without redoing SymPy.

THE STEP IT REPLACES. In _kt_double, each level's source terms can bring a denominator factor the
operator columns did not have. The old code then RE-CLEARED EVERY OPERATOR COLUMN from its raw
SymPy bracket with the new common denominator D2 -- 5,250 columns at rank 2, 75,516 at rank 6,
where one clearing pass took ~78 minutes. At rank 2 that is why the chi^2 level took 38 minutes
while chi^1, the same matrix size, took 25 seconds.

WHY IT IS UNNECESSARY. clear(r, D, p) returns the coefficients of the polynomial r * D. With
D2 = D * q for a polynomial q in (x, y), the coefficients of r * D2 = (r * D) * q are just a
convolution of what we already have with q's coefficients. Exact, integer arithmetic mod p, no
SymPy on the columns at all. q's own content can be a rational; it is inverted mod p.

VALIDATION: rescale(clear(r, D)) must equal clear(r, D * q) exactly, dict for dict.
"""
import sympy as sp

x, y = sp.symbols("x y", real=True)


def q_terms(D, D2, p):
    """The polynomial q = D2 / D as a list of ((a, b), coefficient mod p)."""
    q = sp.cancel(D2 / D)
    num, den = sp.fraction(sp.together(q))
    den_poly = sp.Poly(den, x, y)
    if den_poly.total_degree() != 0:
        raise ValueError(f"D does not divide D2: quotient has denominator {den}")
    den_c = int(den_poly.as_expr())
    inv = pow(den_c % p, p - 2, p)
    terms = []
    for (a, b), c in sp.Poly(num, x, y).terms():
        cn, cd = sp.fraction(sp.Rational(c))
        v = int(cn) % p * pow(int(cd) % p, p - 2, p) % p * inv % p
        if v:
            terms.append(((a, b), v))
    return terms


def rescale(d, terms, p):
    """Coefficients of (column polynomial) * q, from the column's cleared dict."""
    out = {}
    for (e, (j, k)), v in d.items():
        for (a, b), c in terms:
            key = (e, (j + a, k + b))
            out[key] = (out.get(key, 0) + v * c) % p
    return {k: v for k, v in out.items() if v}


def rescale_all(dicts, D, D2, p):
    terms = q_terms(D, D2, p)
    return [rescale(d, terms, p) for d in dicts], terms


if __name__ == "__main__":
    import os
    import sys
    import time
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _kt_double as KD
    import _kt_exact as EX
    import _kt_metrics as MM
    import _kt_perturb as PB
    import _kt_search as K

    p = 2147483647
    t, ph = sp.symbols("t phi", real=True)
    K.set_dim((t, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    GI = KD.kerr_chi_pieces()
    gi0 = GI[0]
    L, _, _ = MM.denominator(gi0)
    rank, denpow = 2, 2
    den = L ** denpow
    _, prods, _ = EX.generators(gi0, rank, den)
    bx, by = EX.reducible_box(prods, den)
    dx, dy = bx + 2, by + 2
    mons = K.monomials(rank)
    cols, F_cos = PB.coefficient_basis(mons, dx, dy, den)
    H0 = KD.hamiltonian(gi0)
    raws, dens = PB.build_columns([(H0, F) for F in F_cos], mons, False)
    D = sp.Integer(1)
    for d_ in dens:
        D = sp.lcm(D, d_)
    base = [PB.clear(r, D, p) for r in raws]
    print(f"rank {rank}, denpow {denpow}: {len(raws)} columns, D = {sp.factor(D)}\n")

    ok = True
    # q choices: a factor of L already present, one that is not, a multi-term one with a rational
    # content, and a product -- the real D2/D is some such polynomial.
    # The pipeline's D2 is an lcm over ZZ, so its q always has integer coefficients. The first four
    # q are of that kind; the last is the lcm route itself, exactly as _kt_double builds D2.
    qs = [x - 2, x**2 + 1, 15 * (x * y + 5), (x - 2) ** 2 * (y + 1) * (x**2 + x + 3)]
    lcm_q = sp.cancel(sp.lcm(D, 110250 * x**3 * (x - 2) ** 2 * (x**2 + 3)) / D)
    qs.append(lcm_q)
    for q in qs:
        D2 = sp.expand(D * q)
        t0 = time.time()
        new, terms = rescale_all(base, D, D2, p)
        t_new = time.time() - t0
        t0 = time.time()
        ref = [PB.clear(r, D2, p) for r in raws]
        t_ref = time.time() - t0
        same = all(a == b for a, b in zip(new, ref))
        print(f"  q = {str(q)[:38]:38s} {len(terms):3d} terms   identical {same}   "
              f"rescale {t_new:6.2f}s  vs SymPy re-clear {t_ref:6.2f}s  ({t_ref / max(t_new, 1e-9):.0f}x)")
        ok &= same
    # A q with fractional coefficients cannot arise from the pipeline, but rescale() must still be
    # right on it. SymPy's clear() cannot serve as the reference here (it would truncate), so the
    # check is linearity: rescaling by q/7 must equal rescaling by q, times the inverse of 7 mod p.
    qa = 3 * (x * y + 5)
    a_new, _ = rescale_all(base, D, sp.expand(D * qa / 7), p)
    b_new, _ = rescale_all(base, D, sp.expand(D * qa), p)
    inv7 = pow(7, p - 2, p)
    same = all(a == {k: v * inv7 % p for k, v in b.items()} for a, b in zip(a_new, b_new))
    print(f"  q = 3(xy+5)/7 (fractional; checked by linearity)     identical {same}")
    ok &= same
    print("\n  " + ("VALIDATED: rescaling reproduces SymPy re-clearing exactly." if ok else "FAILED"))
    sys.exit(0 if ok else 1)
