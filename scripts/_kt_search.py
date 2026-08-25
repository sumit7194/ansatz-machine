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

# ---------------------------------------------------------------- dimension, configurable
# DEFAULT: the 4D stationary-axisymmetric setting (t, r, u, phi) where the metric depends only on
# (r, u) and t, phi are ignorable. DEP names the coordinate indices the metric actually depends on;
# the Poisson bracket then needs only those terms, since dF/dx^a and dH/dx^a vanish elsewhere.
#
# WHY THIS IS CONFIGURABLE NOW: the rank-4 positive control is Cariglia-Galajinsky's FIVE-dimensional
# oxidation (their Eq. 26), and a prover that hardcodes four coordinates cannot use it. Running rank
# 4 on the deformed metric without that control would be a null from an instrument never shown to
# find one when it exists -- exactly what we told tabula not to do.
DIM = 4
COORDS = (t, r, u, ph)
MOM = (pt, pr, pu, pp)
DEP = (1, 2)


def set_dim(coords, mom, dep):
    """Reconfigure for an n-dimensional metric. `dep` = indices the metric depends on."""
    global DIM, COORDS, MOM, DEP
    assert len(coords) == len(mom), "one momentum per coordinate"
    DIM, COORDS, MOM, DEP = len(coords), tuple(coords), tuple(mom), tuple(dep)


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


def cariglia_galajinsky_inv(alpha=1, beta=1):
    """Cariglia & Galajinsky, arXiv:1503.02162, their SECOND Drach solution (their Eq. 20-21) --
    a Ricci-flat 4D metric with a KNOWN IRREDUCIBLE RANK-3 Killing tensor. Our positive control.

        dtau^2 = -2 U(x,y) dt^2 + 2 dt ds + 2 dx dy,     U = alpha/sqrt(x) + beta/sqrt(y)

    THE HALF-INTEGER POWERS ARE REMOVED BY x = X^2, y = Y^2, which makes every component rational
    and lets the polynomial ansatz apply. A Killing tensor is a chart-independent object, so this
    costs nothing. Then 2 dx dy = 8 X Y dX dY and U = alpha/X + beta/Y.

    WHY THIS ONE. The authors state it is irreducible when alpha and beta are BOTH nonzero, and that
    it BECOMES REDUCIBLE when either vanishes ("the isometry group is extended by extra Killing
    vectors"). So the same family carries a known-PASS and a known-FAIL -- exactly what rule 1 of
    our verification discipline demands of any criterion before it gates anything. Most Drach
    systems would NOT do: 7 of the 10 are reducible, their "cubic" integral being just the Poisson
    bracket of two quadratic ones, so picking one blindly would validate nothing.

    Index order matches this module's convention (0 and 3 ignorable, 1 and 2 carry the dependence):
    (t, X, Y, s) with t <-> t, r <-> X, u <-> Y, ph <-> s."""
    U = alpha / r + beta / u
    g = sp.zeros(4, 4)
    g[0, 3] = g[3, 0] = 1                    # from the 2 dt ds cross term
    g[3, 3] = 2 * U                          # inverse of [[-2U, 1], [1, 0]] is [[0, 1], [1, 2U]]
    g[1, 2] = g[2, 1] = sp.Rational(1, 4) / (r * u)     # inverse of the 8XY dXdY block
    return g


METRICS = {"kerr": kerr_inv, "deformed": lambda: deformed_kerr_inv(eps=sp.Integer(2)), "cg": cariglia_galajinsky_inv,
           "cg_reducible": lambda: cariglia_galajinsky_inv(alpha=1, beta=0)}


def monomials(deg):
    """All momentum monomials of total degree `deg`, as exponent tuples over (pt, pr, pu, pp)."""
    out = []
    for e in itertools.product(range(deg + 1), repeat=DIM):
        if sum(e) == deg:
            out.append(e)
    return sorted(out, reverse=True)


def mono_expr(e):
    return sp.prod([m**k for m, k in zip(MOM, e)])


def ansatz(rank, deg_r, deg_u, den_pow, a_spin=sp.Rational(1, 2), M=1, den_S=0, den_D=0,
           den_r=0, den_u=0):
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
            den *= (D0**2 + a_spin**2 * D1**2)**den_S
        if den_D:
            den *= (r**2 - 2 * M * r + a_spin**2)**den_D
        if den_r:
            den *= D0**den_r
        if den_u:
            den *= D1**den_u
        cs.append(terms / den)
    return cs, mons, unknowns


def solve_kt(rank, ginv, deg_r=3, deg_u=3, den_pow=1, verbose=True, den_S=0, den_D=0,
             ckpt=None, den_r=0, den_u=0, den_det=0):
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

    H = sp.Rational(1, 2) * sum(ginv[i, j] * MOM[i] * MOM[j] for i in range(DIM) for j in range(DIM))
    mons = monomials(rank)
    a_spin = sp.Rational(1, 2)
    D0, D1 = COORDS[DEP[0]], COORDS[DEP[1]]
    den = (1 - D1**2)**den_pow
    if den_S:
        den *= (D0**2 + a_spin**2 * D1**2)**den_S
    if den_D:
        den *= (D0**2 - 2 * D0 + a_spin**2)**den_D
    if den_r:
        den *= D0**den_r
    if den_u:
        den *= D1**den_u
    if den_det:
        # the deformed metric's inverse carries the determinant polynomial (r-degree 9) in its
        # denominators; nothing smaller can represent even a constant coefficient
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
        den *= sp.factor(L)**den_det

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
        Fi = (COORDS[DEP[0]]**j * COORDS[DEP[1]]**k * mono_expr(mons[mi]) / den)
        br = sp.S.Zero
        for idx, x in [(i, COORDS[i]) for i in DEP]:
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
        pc = sp.Poly(sp.expand(lin), COORDS[DEP[0]], COORDS[DEP[1]])
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
                F += v[i] * COORDS[DEP[0]]**j * COORDS[DEP[1]]**k * mono_expr(mons[mi]) / den
        sols.append(sp.cancel(sp.together(F)))
    return sols


def build(rank, ginv, verbose=True):
    """Assemble {H, F} for a general degree-`rank` F, and collect it into equations.

    Returns (equations, unknown_functions, timing). Each equation is the coefficient of one
    degree-(rank+1) momentum monomial -- a linear PDE in the unknowns and their (r,u) derivatives."""
    H = sp.Rational(1, 2) * sum(ginv[i, j] * MOM[i] * MOM[j] for i in range(DIM) for j in range(DIM))
    mons = monomials(rank)
    cs = [sp.Function(f"c{i}")(r, u) for i in range(len(mons))]
    F = sum(c * mono_expr(e) for c, e in zip(cs, mons))
    if verbose:
        print(f"  rank {rank}: {len(mons)} unknown coefficient functions of (r,u)", flush=True)

    t0 = time.time()
    # position dependence is only through r (index 1) and u (index 2)
    br = sp.S.Zero
    for idx, x in [(i, COORDS[i]) for i in DEP]:
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
    ap.add_argument("--den-r", type=int, default=0)
    ap.add_argument("--den-u", type=int, default=0)
    ap.add_argument("--den-det", type=int, default=0)
    args = ap.parse_args()

    print(f"KILLING-TENSOR SEARCH -- metric={args.metric}, rank={args.rank}\n")
    ginv = METRICS[args.metric]()
    print(f"  inverse metric: {int(sp.count_ops(ginv))} ops")
    if args.solve:
        ck_path = (f"data/kt_{args.metric}_r{args.rank}_{args.deg_r}_{args.deg_u}"
                   f"_{args.den}{args.den_S}{args.den_D}.ckpt")
        sols = solve_kt(args.rank, ginv, args.deg_r, args.deg_u, args.den,
                        den_S=args.den_S, den_D=args.den_D, ckpt=ck_path,
                        den_r=args.den_r, den_u=args.den_u, den_det=args.den_det)
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


# --------------------------------------------------------------------- the point-sampling route
# A SANITY CHECK THAT MUST NEVER FAIL, and did:
#   every REDUCIBLE is a product of lower-rank solutions, hence itself a solution.
#   So dim(reducible span) <= dim(solution space), ALWAYS.
# On the CG 5D control at rank 4 this came out 30 > 28, which is impossible -- and the cause was
# the ansatz: products of four rank-1 solutions carry denominators up to den^4, while the rank-4
# ansatz was given den^1, so it could not hold the reducibles it is obliged to contain. A negative
# "irreducible count" is the cheapest possible detector of an inadequate ansatz; check it before
# reading any dimension as a result.


def solve_kt_sampled(rank, ginv, deg_r, deg_u, den, n_points=None, primes=(2147483647, 2147483629),
                     verbose=True, seed=12345, rows_ckpt=None):
    """Same Killing-tensor system, assembled by EVALUATION AT EXACT RATIONAL POINTS.

    WHY. The symbolic column route costs 19 s/column on the deformed metric (its inverse carries a
    degree-9 determinant polynomial), i.e. ~10 h at rank 3 -- unaffordable on a machine with daytime
    power cuts. This is §21's trick, credited in the roadmap to Sumit's "terms-as-vector-dimensions"
    intuition: NEVER MATERIALIZE THE GIANT EXPRESSION. {H,F}=0 is linear in the unknowns, so
    evaluating the coefficient conditions at many exact rational (r,u) points gives the SAME linear
    system with rational entries and no expression swell anywhere.

    Rank is taken modulo two large primes rather than over Q: an exact rational nullspace on a
    ~3000 x 2000 matrix is the new bottleneck, while a modular rank is fast and, agreeing across two
    independent primes, is wrong only with probability ~1/p^2. Disagreement is reported, never
    averaged -- if the primes differ the answer is UNKNOWN, not the mean.

    The system is deliberately OVERDETERMINED (more points than unknowns); §21's G0 gate is the
    same idea -- solve on part and verify on held-out probes."""
    import numpy as np

    H = sp.Rational(1, 2) * sum(ginv[i, j] * MOM[i] * MOM[j] for i in range(DIM) for j in range(DIM))
    mons = monomials(rank)
    out_mons = monomials(rank + 1)
    cols = [(mi, j, k) for mi in range(len(mons))
            for j in range(deg_r + 1) for k in range(deg_u + 1)]
    n_unk = len(cols)
    if n_points is None:                       # overdetermine by ~50%
        n_points = int(1.5 * n_unk / len(out_mons)) + 4
    if verbose:
        print(f"  rank {rank}: {n_unk} unknowns, {len(out_mons)} momentum monomials, "
              f"{n_points} sample points -> {n_points*len(out_mons)} rows", flush=True)

    dH = [sp.diff(H, COORDS[i]) for i in DEP]
    dHdp = [sp.diff(H, MOM[i]) for i in DEP]
    # (r,u)-dependent weight of each column and its derivatives, symbolic but TINY
    ws = []
    for (mi, j, k) in cols:
        w = COORDS[DEP[0]]**j * COORDS[DEP[1]]**k / den
        ws.append((w, sp.diff(w, COORDS[DEP[0]]), sp.diff(w, COORDS[DEP[1]])))
    dm = [[sp.diff(mono_expr(e), MOM[i]) for i in DEP] for e in mons]
    me = [mono_expr(e) for e in mons]

    # BANK THE ASSEMBLED ROWS. Assembly is the expensive half (24 min at rank 3 on the deformed
    # metric) and the modular rank is the cheap half -- but a power cut during the RANK step was
    # throwing the assembly away too. Same rule as the order-2 component cache: cache granularity
    # must match the failure mode, not the code structure.
    # BANKED INCREMENTALLY, NOT ONLY AT THE END. Three power cuts in two days cost three FULL
    # assemblies, because the old checkpoint was all-or-nothing: a run 95% through its points had
    # written nothing and restarted from zero. The saved state carries the RNG's bit-generator
    # state as well as the rows, so a resumed run draws THE IDENTICAL point sequence it would have
    # drawn -- a resume is the same computation, not a similar one. Rule 15 (cache granularity must
    # match the failure mode) applied to the failure mode we actually have, which is power.
    import pickle
    rng = np.random.default_rng(seed)
    rows_num, t0 = [], time.time()
    pts_used = 0
    tries = 0
    if rows_ckpt and os.path.exists(rows_ckpt):
        try:
            with open(rows_ckpt, "rb") as fh:
                saved = pickle.load(fh)
            if len(saved) == 2:                       # legacy: complete assembly only
                saved_unk, saved_rows = saved
                if saved_unk == n_unk:
                    if verbose:
                        print(f"  RESUMED {len(saved_rows)} assembled rows from {rows_ckpt}",
                              flush=True)
                    return _rank_from_rows(saved_rows, n_unk, primes, verbose)
            else:
                saved_unk, saved_rows, saved_pts, saved_tries, saved_state = saved
                if saved_unk == n_unk:
                    rows_num, pts_used, tries = saved_rows, saved_pts, saved_tries
                    rng.bit_generator.state = saved_state
                    if pts_used >= n_points:
                        if verbose:
                            print(f"  RESUMED {len(rows_num)} assembled rows from {rows_ckpt}",
                                  flush=True)
                        return _rank_from_rows(rows_num, n_unk, primes, verbose)
                    if verbose:
                        print(f"  RESUMED PARTIAL assembly: {pts_used}/{n_points} points, "
                              f"{len(rows_num)} rows, RNG state restored", flush=True)
            if saved_unk != n_unk and verbose:
                print(f"  checkpoint is for {saved_unk} unknowns, need {n_unk}; reassembling",
                      flush=True)
                rows_num, pts_used, tries = [], 0, 0
        except Exception:
            rows_num, pts_used, tries = [], 0, 0
    while pts_used < n_points and tries < 20 * n_points:
        tries += 1
        r0 = sp.Rational(int(rng.integers(3, 60)), int(rng.integers(1, 7)))
        u0 = sp.Rational(int(rng.integers(-9, 10)), 11)
        sub = {COORDS[DEP[0]]: r0, COORDS[DEP[1]]: u0}
        try:
            dH0 = [sp.together(d.subs(sub)) for d in dH]
            dHdp0 = [sp.together(d.subs(sub)) for d in dHdp]
            if any(x.has(sp.zoo, sp.nan, sp.oo) for x in dH0 + dHdp0):
                continue
            wv = []
            ok = True
            for (w, wr, wu) in ws:
                a, b, c = w.subs(sub), wr.subs(sub), wu.subs(sub)
                if any(x.has(sp.zoo, sp.nan, sp.oo) for x in (a, b, c)):
                    ok = False
                    break
                wv.append((a, b, c))
            if not ok:
                continue
        except Exception:
            continue
        # build this point's block of rows: one per output momentum monomial
        block = {e: [sp.S.Zero] * n_unk for e in out_mons}
        for i, (mi, j, k) in enumerate(cols):
            w, wr, wu = wv[i]
            expr = sum(dH0[q] * w * dm[mi][q] for q in range(len(DEP)))
            expr -= sum((wr, wu)[q] * dHdp0[q] * me[mi] for q in range(len(DEP)))
            if expr == 0:
                continue
            poly = sp.Poly(sp.expand(expr), *MOM)
            for e in out_mons:
                c = poly.coeff_monomial(mono_expr(e))
                if c != 0:
                    block[e][i] = c
        for e in out_mons:
            row = block[e]
            if any(x != 0 for x in row):
                rows_num.append(row)
        pts_used += 1
        if verbose and pts_used % 10 == 0:
            print(f"    {pts_used}/{n_points} points  ({time.time()-t0:.0f}s)", flush=True)
        if rows_ckpt and pts_used % 20 == 0:
            with open(rows_ckpt + ".tmp", "wb") as fh:
                pickle.dump((n_unk, rows_num, pts_used, tries, rng.bit_generator.state), fh)
            os.replace(rows_ckpt + ".tmp", rows_ckpt)
    if verbose:
        print(f"  {len(rows_num)} rows assembled in {time.time()-t0:.1f}s", flush=True)
    if rows_ckpt:
        with open(rows_ckpt + ".tmp", "wb") as fh:
            pickle.dump((n_unk, rows_num, pts_used, tries, rng.bit_generator.state), fh)
        os.replace(rows_ckpt + ".tmp", rows_ckpt)
        if verbose:
            print(f"  rows banked to {rows_ckpt}", flush=True)
    return _rank_from_rows(rows_num, n_unk, primes, verbose)


def _rank_from_rows(rows_num, n_unk, primes, verbose):
    """Clear denominators per row, reduce mod p, rank by Gaussian elimination over GF(p)."""
    import numpy as np
    dims = []
    for p in primes:
        M = np.zeros((len(rows_num), n_unk), dtype=np.int64)
        for a, row in enumerate(rows_num):
            L = sp.Integer(1)
            for x in row:
                if x != 0:
                    L = sp.lcm(L, sp.denom(x))
            for b, x in enumerate(row):
                if x != 0:
                    M[a, b] = int(sp.Integer(sp.cancel(x * L)) % p)
        rank_p, piv = 0, 0
        rows_n, cols_n = M.shape
        for c in range(cols_n):
            nz = np.nonzero(M[piv:, c])[0]
            if nz.size == 0:
                continue
            i0 = piv + nz[0]
            if i0 != piv:
                M[[piv, i0]] = M[[i0, piv]]
            inv = pow(int(M[piv, c]), p - 2, p)
            M[piv] = (M[piv] * inv) % p
            nzb = np.nonzero(M[:, c])[0]
            nzb = nzb[nzb != piv]
            if nzb.size:
                M[nzb] = (M[nzb] - np.outer(M[nzb, c], M[piv])) % p
            piv += 1
            rank_p += 1
            if piv == rows_n:
                break
        dims.append(n_unk - rank_p)
        if verbose:
            print(f"    mod {p}: rank {rank_p} -> nullspace dimension {n_unk - rank_p}", flush=True)
    if dims[0] != dims[1]:
        print(f"  PRIMES DISAGREE {dims} -> UNKNOWN, not averaged", flush=True)
        return None
    return dims[0]


def solve_kt_modp(rank, ginv, deg_r, deg_u, den, n_points=None,
                  primes=(2147483647, 2147483629), verbose=True, seed=12345,
                  ckpt=None, ckpt_every=150, chunk=2000):
    """Same system as solve_kt_sampled, but REDUCED MOD p DURING ASSEMBLY.

    WHY THIS EXISTS. solve_kt_sampled accumulates every row as a Python list of exact rationals and
    only converts to numpy at the end, so BOTH structures are live at once. Measured at 63 bytes per
    entry, delta=2 rank 4 at den^2 needs 638M entries = 37 GB for the Python half alone, plus 4.75
    GiB for the numpy half: 42 GB, which fits nowhere. We published "4.75 GiB/prime" for a day and
    declined the rung on it; that figure was the numpy matrix at the RANK STEP, not the peak.

    THE 37 GB WAS NEVER A PROPERTY OF THE PROBLEM. It is the cost of holding, as Python objects,
    integers that fit in 4 bytes. Reducing each row mod p as it is produced means the Python
    structure never exists: storage is two int32 arrays, 3.8 GiB total, and the run fits in RAM.

    int32 STORAGE, int64 ARITHMETIC. Residues are < 2^31 so they store in int32, but the
    elimination forms products up to p^2 ~ 4.6e18, which needs int64. The update is therefore done
    on int64 views of row CHUNKS -- a whole-matrix int64 temporary would be 4 GiB and reintroduce
    the problem one level down.

    NOT A DROP-IN REPLACEMENT AND NOT YET TRUSTED. This changes the numerical path, so it is held to
    the bar the resume fix met: reproduce a known-answer rung EXACTLY before it is believed on a rung
    with no known answer."""
    import numpy as np

    H = sp.Rational(1, 2) * sum(ginv[i, j] * MOM[i] * MOM[j] for i in range(DIM) for j in range(DIM))
    mons = monomials(rank)
    out_mons = monomials(rank + 1)
    cols = [(mi, j, k) for mi in range(len(mons))
            for j in range(deg_r + 1) for k in range(deg_u + 1)]
    n_unk = len(cols)
    if n_points is None:
        n_points = int(1.5 * n_unk / len(out_mons)) + 4
    max_rows = n_points * len(out_mons)
    if verbose:
        print(f"  rank {rank}: {n_unk} unknowns, {len(out_mons)} momentum monomials, "
              f"{n_points} sample points -> up to {max_rows} rows", flush=True)
        print(f"  storage: {len(primes)} x int32[{max_rows},{n_unk}] = "
              f"{len(primes)*max_rows*n_unk*4/2**30:.2f} GiB resident", flush=True)

    dH = [sp.diff(H, COORDS[i]) for i in DEP]
    dHdp = [sp.diff(H, MOM[i]) for i in DEP]
    ws = []
    for (mi, j, k) in cols:
        w = COORDS[DEP[0]]**j * COORDS[DEP[1]]**k / den
        ws.append((w, sp.diff(w, COORDS[DEP[0]]), sp.diff(w, COORDS[DEP[1]])))
    dm = [[sp.diff(mono_expr(e), MOM[i]) for i in DEP] for e in mons]
    me = [mono_expr(e) for e in mons]

    Ms = [np.zeros((max_rows, n_unk), dtype=np.int32) for _ in primes]
    nrows, pts_used, tries = 0, 0, 0
    rng = np.random.default_rng(seed)
    t0 = time.time()

    if ckpt and os.path.exists(ckpt + ".npz"):
        try:
            z = np.load(ckpt + ".npz", allow_pickle=True)
            if int(z["n_unk"]) == n_unk:
                nrows, pts_used, tries = int(z["nrows"]), int(z["pts"]), int(z["tries"])
                for pi in range(len(primes)):
                    Ms[pi][:nrows] = z[f"M{pi}"]
                rng.bit_generator.state = z["rng"].item()
                if verbose:
                    print(f"  RESUMED PARTIAL: {pts_used}/{n_points} points, {nrows} rows, "
                          f"RNG state restored", flush=True)
        except Exception:
            nrows, pts_used, tries = 0, 0, 0

    def bank():
        if not ckpt:
            return
        np.savez(ckpt + ".tmp.npz", n_unk=n_unk, nrows=nrows, pts=pts_used, tries=tries,
                 rng=np.array(rng.bit_generator.state, dtype=object),
                 **{f"M{pi}": Ms[pi][:nrows] for pi in range(len(primes))})
        os.replace(ckpt + ".tmp.npz", ckpt + ".npz")

    while pts_used < n_points and tries < 20 * n_points:
        tries += 1
        r0 = sp.Rational(int(rng.integers(3, 60)), int(rng.integers(1, 7)))
        u0 = sp.Rational(int(rng.integers(-9, 10)), 11)
        sub = {COORDS[DEP[0]]: r0, COORDS[DEP[1]]: u0}
        try:
            dH0 = [sp.together(d.subs(sub)) for d in dH]
            dHdp0 = [sp.together(d.subs(sub)) for d in dHdp]
            if any(x.has(sp.zoo, sp.nan, sp.oo) for x in dH0 + dHdp0):
                continue
            wv, ok = [], True
            for (w, wr, wu) in ws:
                a, b, c = w.subs(sub), wr.subs(sub), wu.subs(sub)
                if any(x.has(sp.zoo, sp.nan, sp.oo) for x in (a, b, c)):
                    ok = False
                    break
                wv.append((a, b, c))
            if not ok:
                continue
        except Exception:
            continue
        block = {e: [sp.S.Zero] * n_unk for e in out_mons}
        for i, (mi, j, k) in enumerate(cols):
            w, wr, wu = wv[i]
            expr = sum(dH0[q] * w * dm[mi][q] for q in range(len(DEP)))
            expr -= sum((wr, wu)[q] * dHdp0[q] * me[mi] for q in range(len(DEP)))
            if expr == 0:
                continue
            poly = sp.Poly(sp.expand(expr), *MOM)
            for e in out_mons:
                c = poly.coeff_monomial(mono_expr(e))
                if c != 0:
                    block[e][i] = c
        for e in out_mons:
            row = block[e]
            nz = [(b, x) for b, x in enumerate(row) if x != 0]
            if not nz:
                continue
            L = sp.Integer(1)
            for _, x in nz:
                L = sp.lcm(L, sp.denom(x))
            for pi, p in enumerate(primes):
                for b, x in nz:
                    Ms[pi][nrows, b] = int(sp.Integer(sp.cancel(x * L)) % p)
            nrows += 1
        pts_used += 1
        if verbose and pts_used % 10 == 0:
            print(f"    {pts_used}/{n_points} points, {nrows} rows  ({time.time()-t0:.0f}s)",
                  flush=True)
        if ckpt and pts_used % ckpt_every == 0:
            bank()
    bank()
    if verbose:
        print(f"  {nrows} rows assembled in {time.time()-t0:.1f}s", flush=True)

    dims = []
    for pi, p in enumerate(primes):
        M = Ms[pi][:nrows]
        rk, piv = 0, 0
        t1 = time.time()
        for c in range(n_unk):
            nz = np.nonzero(M[piv:, c])[0]
            if nz.size == 0:
                continue
            i0 = piv + nz[0]
            if i0 != piv:
                M[[piv, i0]] = M[[i0, piv]]
            inv = pow(int(M[piv, c]), p - 2, p)
            M[piv] = ((M[piv].astype(np.int64) * inv) % p).astype(np.int32)
            nzb = np.nonzero(M[:, c])[0]
            nzb = nzb[nzb != piv]
            pivrow = M[piv].astype(np.int64)
            for s in range(0, nzb.size, chunk):     # chunked: a whole-matrix int64 temp is 4 GiB
                idx = nzb[s:s + chunk]
                blk = M[idx].astype(np.int64)
                blk -= np.outer(blk[:, c], pivrow)
                M[idx] = (blk % p).astype(np.int32)
            piv += 1
            rk += 1
            if verbose and rk % 2000 == 0:
                print(f"    mod {p}: {rk} pivots  ({time.time()-t1:.0f}s)", flush=True)
        if verbose:
            print(f"    mod {p}: rank {rk} -> nullspace dimension {n_unk - rk}  "
                  f"[{time.time()-t1:.0f}s]", flush=True)
        dims.append(n_unk - rk)
    if len(set(dims)) != 1:
        print(f"  PRIMES DISAGREE: {dims} -- UNKNOWN, not averaged", flush=True)
        return None
    return dims[0]
