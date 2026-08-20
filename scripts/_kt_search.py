#!/usr/bin/env python3
"""SYMBOLIC higher-rank Killing-tensor search, momentum-space form.

THE QUESTION (open; named in §85's own caveat): does the quadrupole-deformed Kerr admit an
IRREDUCIBLE Killing tensor of rank 3 or rank 4?

WHY THIS ROUTE AND NOT THE OLD ONE. scripts/_killing_search.py tried the tensor form -- expand
nabla_(a K_bc) in the deformed connection -- and is marked DEAD END: 7.5 h at 98% CPU, no output.
The grading theorem (scripts/_p3_grading_check.py, VERIFIED not assumed) licenses the equivalent
momentum form, which is far cheaper:

    a rank-r Killing tensor  <=>  a conserved F = K^{a1..ar} p_a1 .. p_ar,
    homogeneous of degree r in the momenta, with {H, F} = 0.

For a stationary + axisymmetric metric the coefficients depend only on (r, u), so F is a sum of
degree-r momentum monomials with unknown functions of two variables, and {H, F} = 0 collects into a
linear PDE system. Positing each unknown as a bounded polynomial in (r, u) turns that into LINEAR
ALGEBRA -- decidable, and the size is measurable BEFORE committing.

Because H and F depend on position only through (r, u), the bracket needs only two terms:
    {H, F} = sum_{a in {r,u}} [ dH/dx^a dF/dp_a  -  dH/dp_a dF/dx^a ]

WHAT A NULL WOULD MEAN, and why it is worth more than a numerical screen: "no irreducible rank-3 or
rank-4 KT with coefficients polynomial of degree <= N" is a THEOREM about a stated family, not
"we looked and did not find one".

Repro:  .venv/bin/python scripts/_kt_search.py --rank 2 --metric kerr        (must find Carter)
        .venv/bin/python scripts/_kt_search.py --rank 3 --metric kerr --sizes-only
"""
import argparse
import itertools
import os
import sys
import time

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
import sympy as sp

t, r, u, ph = sp.symbols("t r u phi", real=True)
pt, pr, pu, pp = sp.symbols("p_t p_r p_u p_phi", real=True)
COORDS = (t, r, u, ph)
MOM = (pt, pr, pu, pp)


def kerr_inv(a=sp.Rational(1, 2), M=1):
    """Kerr inverse metric in Boyer-Lindquist with u = cos(theta) (rational: the trig form swells)."""
    S = r**2 + a**2 * u**2
    D = r**2 - 2 * M * r + a**2
    s2 = 1 - u**2
    g = sp.zeros(4, 4)
    g[0, 0] = -((r**2 + a**2)**2 - D * a**2 * s2) / (S * D)
    g[0, 3] = g[3, 0] = -2 * M * r * a / (S * D)
    g[3, 3] = (D - a**2 * s2) / (S * D * s2)
    g[1, 1] = D / S
    g[2, 2] = s2 / S
    return g


def deformed_kerr_inv(a=sp.Rational(3, 5), M=1, eps=sp.Symbol("epsilon")):
    """§82/§85's deformation: g_tt -> g_tt * (1 + eps*(3u^2-1)/r^3), everything else Kerr.
    Inverting the 2x2 (t,phi) block exactly keeps it a rational function."""
    S = r**2 + a**2 * u**2
    D = r**2 - 2 * M * r + a**2
    s2 = 1 - u**2
    bump = 1 + eps * (3 * u**2 - 1) / r**3
    gtt = -(1 - 2 * M * r / S) * bump
    gtp = -2 * M * r * a * s2 / S
    gpp = (r**2 + a**2 + 2 * M * r * a**2 * s2 / S) * s2
    det = gtt * gpp - gtp**2
    g = sp.zeros(4, 4)
    g[0, 0] = sp.cancel(gpp / det)
    g[0, 3] = g[3, 0] = sp.cancel(-gtp / det)
    g[3, 3] = sp.cancel(gtt / det)
    g[1, 1] = D / S
    g[2, 2] = s2 / S
    return g


METRICS = {"kerr": kerr_inv, "deformed": deformed_kerr_inv}


def monomials(deg):
    """All momentum monomials of total degree `deg`, as exponent tuples over (pt, pr, pu, pp)."""
    out = []
    for e in itertools.product(range(deg + 1), repeat=4):
        if sum(e) == deg:
            out.append(e)
    return sorted(out, reverse=True)


def mono_expr(e):
    return sp.prod([m**k for m, k in zip(MOM, e)])


def ansatz(rank, deg_r, deg_u, den_pow, a_spin=sp.Rational(1, 2), M=1, den_S=0, den_D=0):
    """Explicit ansatz for the coefficient functions, built BEFORE the bracket so no substitution
    into Derivative() is ever needed.

        c_m(r,u) = ( sum_{j<=deg_r, k<=deg_u} a_mjk r^j u^k ) / (1-u^2)^den_pow

    THE DENOMINATORS ARE NOT OPTIONAL, and (1-u^2) ALONE IS NOT ENOUGH -- measured, by the control
    failing. Kerr's own g^{ab} carry S = r^2+a^2u^2 and D = r^2-2Mr+a^2 in their denominators, and
    Carter (Walker-Penrose: K = 2 l^(a n^b) + r^2 g^{ab}, with the Kinnersley vectors) carries both.
    With denominator (1-u^2) only, the rank-2 solve on KERR returned dimension 3 -- just the
    Killing-vector products p_t^2, p_t p_phi, p_phi^2 -- missing BOTH H and Carter. A confident null
    from an inadequate span, exactly what §85 (E) taught numerically.
    Historical note on why the plain form still matters: Carter in the u = cos(theta) chart is
    p_u^2 (1-u^2) + u^2 p_phi^2/(1-u^2) + ..., so a purely POLYNOMIAL ansatz cannot represent the
    one rank-2 tensor we know exists -- it would return a confident null on the validation case.
    (§85's slice-specific-basis lesson, arriving in symbolic form.)"""
    mons = monomials(rank)
    unknowns, cs = [], []
    for i, _ in enumerate(mons):
        terms = sp.S.Zero
        for j in range(deg_r + 1):
            for k in range(deg_u + 1):
                a = sp.Symbol(f"a_{i}_{j}_{k}")
                unknowns.append(a)
                terms += a * r**j * u**k
        den = (1 - u**2)**den_pow
        if den_S:
            den *= (r**2 + a_spin**2 * u**2)**den_S
        if den_D:
            den *= (r**2 - 2 * M * r + a_spin**2)**den_D
        cs.append(terms / den)
    return cs, mons, unknowns


def solve_kt(rank, ginv, deg_r=3, deg_u=3, den_pow=1, verbose=True, den_S=0, den_D=0,
             ckpt=None):
    """Solve {H, F} = 0 over the ansatz, assembling the linear system COLUMN BY COLUMN.

    WHY COLUMN-WISE. The first version built one expression carrying all ~150 symbolic unknowns and
    expanded it: 394 s on Kerr rank 2, and it did not survive a power cut. But {H, .} is LINEAR in
    the unknowns, so the giant object is never needed -- each basis element r^j u^k m(p)/den
    contributes ONE COLUMN, its bracket is tiny, and the columns are independent. Same lesson as
    every wall in this project: do not build the big thing, and do not hand a normalizer swell it
    then has to undo.

    DENOMINATORS ARE CLEARED PER ROW, NEVER PER COLUMN. Scaling one column rescales one unknown and
    changes the solution set; scaling a ROW is just multiplying an equation by a nonzero factor and
    is free. So coefficients are kept as rational functions until a whole momentum-monomial row is
    assembled, then that row is cleared and split by powers of (r, u).

    `ckpt` is a path: columns are appended as they complete, so a daytime power cut costs one
    column instead of the whole assembly."""
    import pickle
    from collections import defaultdict

    H = sp.Rational(1, 2) * sum(ginv[i, j] * MOM[i] * MOM[j] for i in range(4) for j in range(4))
    mons = monomials(rank)
    a_spin = sp.Rational(1, 2)
    den = (1 - u**2)**den_pow
    if den_S:
        den *= (r**2 + a_spin**2 * u**2)**den_S
    if den_D:
        den *= (r**2 - 2 * r + a_spin**2)**den_D

    cols = [(mi, j, k) for mi in range(len(mons))
            for j in range(deg_r + 1) for k in range(deg_u + 1)]
    if verbose:
        print(f"  ansatz: {len(mons)} coefficients x {(deg_r+1)*(deg_u+1)} terms = {len(cols)} "
              f"unknowns; denominator (1-u^2)^{den_pow} S^{den_S} D^{den_D}", flush=True)

    rows = defaultdict(dict)                 # momentum monomial -> {column index: rational coeff}
    done = 0
    if ckpt and os.path.exists(ckpt):
        try:
            with open(ckpt, "rb") as fh:
                rows_raw, done = pickle.load(fh)
            rows = defaultdict(dict, {k: v for k, v in rows_raw.items()})
            if verbose:
                print(f"  RESUMED from checkpoint: {done}/{len(cols)} columns already assembled",
                      flush=True)
        except Exception:
            rows, done = defaultdict(dict), 0

    t0 = time.time()
    out_mons = monomials(rank + 1)
    for i in range(done, len(cols)):
        mi, j, k = cols[i]
        Fi = r**j * u**k * mono_expr(mons[mi]) / den
        br = sp.S.Zero
        for idx, x in ((1, r), (2, u)):
            br += sp.diff(H, x) * sp.diff(Fi, MOM[idx]) - sp.diff(H, MOM[idx]) * sp.diff(Fi, x)
        poly = sp.Poly(sp.expand(br), *MOM)
        for e in out_mons:
            c = poly.coeff_monomial(mono_expr(e))
            if c != 0:
                rows[e][i] = sp.cancel(sp.together(c))
        if ckpt and (i + 1) % 10 == 0:
            with open(ckpt + ".tmp", "wb") as fh:
                pickle.dump((dict(rows), i + 1), fh)
            os.replace(ckpt + ".tmp", ckpt)
        if verbose and (i + 1) % 25 == 0:
            print(f"    column {i+1}/{len(cols)}  ({time.time()-t0:.0f}s)", flush=True)
    if verbose:
        print(f"  columns assembled in {time.time()-t0:.1f}s", flush=True)

    # clear denominators PER ROW, then split each row by powers of (r, u)
    t0 = time.time()
    eqs = []
    for e, colmap in rows.items():
        dens = [sp.denom(c) for c in colmap.values()]
        L = dens[0]
        for d in dens[1:]:
            L = sp.lcm(L, d)
        lin = sp.S.Zero
        for i, c in colmap.items():
            lin += sp.Symbol(f"A{i}") * sp.cancel(c * L)
        pc = sp.Poly(sp.expand(lin), r, u)
        for coeff in pc.coeffs():
            if coeff != 0:
                eqs.append(coeff)
    unknown_syms = [sp.Symbol(f"A{i}") for i in range(len(cols))]
    if verbose:
        print(f"  rows cleared + split in {time.time()-t0:.1f}s: {len(eqs)} linear equations",
              flush=True)

    t0 = time.time()
    A, _ = sp.linear_eq_to_matrix(eqs, unknown_syms)
    ns = A.nullspace()
    if verbose:
        print(f"  nullspace in {time.time()-t0:.1f}s: DIMENSION {len(ns)}", flush=True)
    sols = []
    for v in ns:
        F = sp.S.Zero
        for i, (mi, j, k) in enumerate(cols):
            if v[i] != 0:
                F += v[i] * r**j * u**k * mono_expr(mons[mi]) / den
        sols.append(sp.cancel(sp.together(F)))
    return sols


def build(rank, ginv, verbose=True):
    """Assemble {H, F} for a general degree-`rank` F, and collect it into equations.

    Returns (equations, unknown_functions, timing). Each equation is the coefficient of one
    degree-(rank+1) momentum monomial -- a linear PDE in the unknowns and their (r,u) derivatives."""
    H = sp.Rational(1, 2) * sum(ginv[i, j] * MOM[i] * MOM[j] for i in range(4) for j in range(4))
    mons = monomials(rank)
    cs = [sp.Function(f"c{i}")(r, u) for i in range(len(mons))]
    F = sum(c * mono_expr(e) for c, e in zip(cs, mons))
    if verbose:
        print(f"  rank {rank}: {len(mons)} unknown coefficient functions of (r,u)", flush=True)

    t0 = time.time()
    # position dependence is only through r (index 1) and u (index 2)
    br = sp.S.Zero
    for idx, x in ((1, r), (2, u)):
        br += sp.diff(H, x) * sp.diff(F, MOM[idx]) - sp.diff(H, MOM[idx]) * sp.diff(F, x)
    t_br = time.time() - t0

    t0 = time.time()
    # COLLECT WITHOUT SWELLING. The first version did together() -> numer() -> simplify() per
    # coefficient: 289 s and 5k-13k-op equations on Kerr rank 2. That is precisely the pattern this
    # project spent a week learning to recognise -- a giant common denominator built so a simplifier
    # can undo it. The bracket is LINEAR in the unknowns, so Poly over the momenta reads each
    # coefficient off directly, and cancel() is the right normal form (never simplify()).
    poly = sp.Poly(sp.expand(br), *MOM)
    eqs = []
    for e in monomials(rank + 1):
        c = poly.coeff_monomial(mono_expr(e))
        if c == 0:
            continue
        c = sp.cancel(sp.together(c))
        if c != 0:
            eqs.append(sp.numer(c))          # clearing the denominator is safe: it never vanishes
    t_col = time.time() - t0
    if verbose:
        print(f"  bracket built in {t_br:.2f}s; collected into {len(eqs)} nonzero equations "
              f"in {t_col:.2f}s", flush=True)
    return eqs, cs, mons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rank", type=int, default=2)
    ap.add_argument("--metric", default="kerr", choices=sorted(METRICS))
    ap.add_argument("--sizes-only", action="store_true")
    ap.add_argument("--solve", action="store_true")
    ap.add_argument("--deg-r", type=int, default=3)
    ap.add_argument("--deg-u", type=int, default=3)
    ap.add_argument("--den", type=int, default=1)
    ap.add_argument("--den-S", type=int, default=0)
    ap.add_argument("--den-D", type=int, default=0)
    args = ap.parse_args()

    print(f"KILLING-TENSOR SEARCH -- metric={args.metric}, rank={args.rank}\n")
    ginv = METRICS[args.metric]()
    print(f"  inverse metric: {int(sp.count_ops(ginv))} ops")
    if args.solve:
        ck_path = (f"data/kt_{args.metric}_r{args.rank}_{args.deg_r}_{args.deg_u}"
                   f"_{args.den}{args.den_S}{args.den_D}.ckpt")
        sols = solve_kt(args.rank, ginv, args.deg_r, args.deg_u, args.den,
                        den_S=args.den_S, den_D=args.den_D, ckpt=ck_path)
        print(f"\n  SOLUTION SPACE: dimension {len(sols)}")
        for i, F in enumerate(sols):
            print(f"    [{i}] {sp.sstr(F)[:150]}")
        return 0
    eqs, cs, mons = build(args.rank, ginv)
    if eqs:
        sizes = sorted(int(sp.count_ops(e)) for e in eqs)
        print(f"  equation sizes: min {sizes[0]}, median {sizes[len(sizes)//2]}, max {sizes[-1]}")
    print(f"\n  SYSTEM: {len(eqs)} PDEs in {len(cs)} unknown functions of 2 variables")


if __name__ == "__main__":
    raise SystemExit(main())
