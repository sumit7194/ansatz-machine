#!/usr/bin/env python3
"""WHICH background Killing tensors SURVIVE a metric perturbation, order by order in the coupling.

WHY THE EXACT TEST CANNOT SIMPLY BE POINTED AT A PERTURBATIVE METRIC. The slowly-rotating sGB and
dCS black holes are TRUNCATED double series in coupling zeta and spin chi -- they solve no field
equation exactly. Asking `_kt_exact` for an exact Killing tensor of the truncated metric would
return ZERO almost automatically, because a truncated metric generically has no exact symmetry at
all, and that zero would be an artifact of truncation rather than a statement about the theory. It
is the same shape of error as §124's substrate-independent reducible table: a correct computation
answering the wrong question.

WHAT THE RIGHT QUESTION IS. Write g = g0 + zeta*g1 and expand BOTH sides:

    O(zeta^0):   {H0, F0} = 0            F0 is a Killing tensor of the BACKGROUND
    O(zeta^1):   {H0, F1} + {H1, F0} = 0 inhomogeneous, sourced by the background tensor

So the question is not "does a Killing tensor exist" but "which background Killing tensors EXTEND
to first order", and a background tensor extends exactly when its source {H1, F0} lies in the image
of L: F1 -> {H0, F1}. Writing F0 = sum c_i F0_i over a basis of the background Killing space, this
is ONE linear system in the unknowns (F1, c), of exactly the kind already solved here.

ONE MATRIX BUILDER, TWO USES. With M0[key, j] the coefficient of `key` in {H0, w_j} over the
coefficient basis w_j:

    nullspace(M0)             = the background Killing space           (stage 1)
    nullspace([M0 | S]) -> c  = the directions that survive to O(zeta) (stage 2)

where S[key, i] is the coefficient of `key` in {H1, F0_i}. Stage 2 is stage 1 with extra columns.

THIS IS EXACT, NOT SAMPLED. Every bracket is expanded symbolically and collected coefficient by
coefficient, so there is no sampling slack to subtract (§126) and no upper-bound caveat: the
nullity IS the dimension. Sampling is what one reaches for when the basis is too large to expand;
at the ranks where this question is open it is not.

LINEARITY IS ENFORCED THE SAME WAY AS IN _kt_exact. Every bracket is formed UNCLEARED, the lcm of
all denominators is taken across the whole matrix, and only then is each cleared by that single
common D. A per-column cancel() would divide out whatever factor that column happens to carry,
which is not linear and would silently corrupt the matrix into a clean wrong answer.

WHAT SURVIVES TRIVIALLY, AND WHY IT IS THE FLOOR NOT THE ANSWER. The perturbations of interest stay
stationary and axisymmetric, so p_t and p_phi remain Killing vectors and H remains conserved
exactly. Every REDUCIBLE background tensor therefore survives by construction. The question is
strictly whether anything ABOVE that floor survives -- on Kerr at rank 2 that means the Carter
constant, which is the one case with a published answer to check against.

Repro:
  .venv/bin/python scripts/_kt_perturb.py --selftest
  .venv/bin/python scripts/_kt_perturb.py --background kerr --rank 2 --pert dM
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import sympy as sp
import _kt_search as K
import _kt_metrics as MM
import _kt_reducible as R
import _kt_exact as EX

t, x, y, ph = sp.symbols("t x y phi", real=True)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIMES = (2147483647, 2147483629)


def hamiltonian(ginv):
    return sp.Rational(1, 2) * sum(ginv[i, j] * K.MOM[i] * K.MOM[j]
                                   for i in range(K.DIM) for j in range(K.DIM))


def bracket_raw_coeffs(F_co, H, mons):
    """{H, F} uncleared, where F = sum_mi F_co[mi] * mono_mi. Returns (expr, denominator)."""
    COORDS, MOM, DEP = K.COORDS, K.MOM, K.DEP
    me = [K.mono_expr(e) for e in mons]
    dm = [[sp.diff(K.mono_expr(e), MOM[i]) for i in DEP] for e in mons]
    dH = [sp.diff(H, COORDS[i]) for i in DEP]
    dHdp = [sp.diff(H, MOM[i]) for i in DEP]
    br = sp.Integer(0)
    for q in range(len(DEP)):
        s1 = sum(F_co[mi] * dm[mi][q] for mi in range(len(mons)) if F_co[mi] != 0)
        s2 = sum(sp.diff(F_co[mi], COORDS[DEP[q]]) * me[mi]
                 for mi in range(len(mons)) if F_co[mi] != 0)
        br += dH[q] * s1 - dHdp[q] * s2
    tog = sp.together(br)
    return tog, sp.denom(tog)


def clear(tog, D, p):
    """Clear one bracket by the COMMON denominator D and reduce mod p.

    NOT sp.cancel(tog * D): that runs a full multivariate gcd on a rational function whose
    numerator and denominator both have degree ~24, once per column, and it took >30 min for 1690
    columns. Instead split tog = num/dd, form the COFACTOR D/dd -- which is a ratio of products of
    the same small irreducible factors, so cancel is trivial on it -- and multiply. Same result,
    polynomial arithmetic instead of rational-function gcd. The linearity guarantee is unchanged
    because D is still the single common denominator for every column."""
    num, dd = sp.fraction(sp.together(tog))
    q = sp.cancel(D / dd)
    if sp.denom(q) != 1:
        raise ValueError("the common denominator does not clear this bracket")
    cl = sp.expand(num * q)
    out = {}
    if cl == 0:
        return out
    poly = sp.Poly(sp.expand(cl), *K.MOM)
    for e, co in zip(poly.monoms(), poly.coeffs()):
        pp = sp.Poly(sp.expand(co), x, y)
        for jk, c2 in zip(pp.monoms(), pp.coeffs()):
            r = int(c2) % p
            if r:
                out[(e, jk)] = r
    return out


def build_columns(col_specs, mons, verbose=True, label=""):
    """col_specs: list of (H, F_co) pairs -> list of uncleared brackets and their denominators."""
    raws, dens = [], []
    t0 = time.time()
    for n, (H, F_co) in enumerate(col_specs):
        tog, dd = bracket_raw_coeffs(F_co, H, mons)
        raws.append(tog)
        dens.append(dd)
        if verbose and (n + 1) % 200 == 0:
            print(f"    {label}{n+1}/{len(col_specs)} brackets ({time.time()-t0:.0f}s)", flush=True)
    return raws, dens


def matrix_from(raws, D, p, ncols):
    """Assemble the dense coefficient matrix over GF(p) from cleared brackets."""
    dicts = [clear(r, D, p) for r in raws]
    return matrix_from_dicts(dicts, ncols), dicts


def matrix_from_dicts(dicts, ncols):
    """Assemble from ALREADY-CLEARED dicts, so stage 2 need not re-clear stage 1's columns."""
    keys = sorted(set().union(*dicts)) if dicts else []
    kidx = {k: i for i, k in enumerate(keys)}   # dict, not keys.index -- that was O(n^2)
    M = np.zeros((len(keys), ncols), dtype=np.int64)
    for j, d in enumerate(dicts):
        for k, v in d.items():
            M[kidx[k], j] = v
    return M


def nullspace_modp(M, p):
    """Full nullspace basis over GF(p) by Gauss-Jordan; returns list of int64 vectors."""
    A = np.array(M, dtype=np.int64) % p
    rows, ncols = A.shape if A.size else (0, M.shape[1])
    piv_col, piv = [], 0
    for c in range(ncols):
        if piv >= rows:
            break
        nz = np.nonzero(A[piv:, c])[0]
        if nz.size == 0:
            continue
        i0 = piv + nz[0]
        if i0 != piv:
            A[[piv, i0]] = A[[i0, piv]]
        A[piv] = (A[piv] * pow(int(A[piv, c]), p - 2, p)) % p
        col = A[:, c].copy()
        col[piv] = 0
        nzb = np.nonzero(col)[0]
        if nzb.size:
            A[nzb] = (A[nzb] - np.outer(A[nzb, c], A[piv])) % p
        piv_col.append(c)
        piv += 1
    pset = set(piv_col)
    free = [c for c in range(ncols) if c not in pset]
    vecs = []
    for f in free:
        v = np.zeros(ncols, dtype=np.int64)
        v[f] = 1
        for r, c in enumerate(piv_col):
            if A[r, f]:
                v[c] = (-int(A[r, f])) % p
        vecs.append(v)
    return vecs


def coefficient_basis(mons, dx, dy, den):
    """The w_j basis: (momentum monomial index, x^a y^b / den)."""
    cols, F_cos = [], []
    for mi in range(len(mons)):
        for a in range(dx + 1):
            for b in range(dy + 1):
                cols.append((mi, a, b))
                F = [sp.Integer(0)] * len(mons)
                F[mi] = x**a * y**b / den
                F_cos.append(F)
    return cols, F_cos


def survive(ginv0, ginv1, rank, dx, dy, den, p, verbose=True):
    """Return (background KT dim, surviving dim, background basis as coefficient lists)."""
    mons = K.monomials(rank)
    H0, H1 = hamiltonian(ginv0), hamiltonian(ginv1)
    cols, F_cos = coefficient_basis(mons, dx, dy, den)
    n_w = len(cols)
    if verbose:
        print(f"  rank {rank}: {n_w} coefficient unknowns, box x<={dx} y<={dy}", flush=True)

    # ---- stage 1: the background Killing space, EXACTLY ----
    raws0, dens0 = build_columns([(H0, F) for F in F_cos], mons, verbose, "H0 ")
    D = sp.Integer(1)
    for dd in dens0:
        D = sp.lcm(D, dd)
    M0, dicts0 = matrix_from(raws0, D, p, n_w)
    bg = nullspace_modp(M0, p)
    d0 = len(bg)
    if verbose:
        print(f"  background Killing space: dimension {d0}  (matrix {M0.shape})", flush=True)
    if d0 == 0:
        return 0, 0, []

    # Background basis as coefficient functions, for use as O(zeta) sources.
    bg_co = []
    for v in bg:
        F = [sp.Integer(0)] * len(mons)
        for j, (mi, a, b) in enumerate(cols):
            if v[j]:
                F[mi] += int(v[j]) * x**a * y**b
        bg_co.append([sp.cancel(f / den) for f in F])

    # ---- stage 2: [M0 | S], where S columns are {H1, F0_i} ----
    rawsS, densS = build_columns([(H1, F) for F in bg_co], mons, verbose, "H1 ")
    D2 = D
    for dd in densS:
        D2 = sp.lcm(D2, dd)
    # The two blocks MUST be cleared by the same denominator: clearing them by different factors
    # rescales them relative to each other, which is not a linear change of the combined system
    # and would silently alter which c survive. But when the sources need no larger denominator
    # (D2 == D, the common case) the stage-1 columns are ALREADY correctly cleared, so re-clearing
    # all 1690 of them is pure duplicated work -- it was roughly half the runtime.
    if sp.simplify(D2 - D) == 0:
        if verbose:
            print("  sources need no larger denominator; reusing stage-1 columns", flush=True)
        dictsS = [clear(rr, D, p) for rr in rawsS]
        Mfull = matrix_from_dicts(dicts0 + dictsS, n_w + d0)
    else:
        if verbose:
            print(f"  sources enlarge the denominator; re-clearing all columns", flush=True)
        Mfull, _ = matrix_from(raws0 + rawsS, D2, p, n_w + d0)
    ns = nullspace_modp(Mfull, p)
    # The c-block of the nullspace. Its dimension counts the background tensors that extend;
    # vectors with c = 0 are background tensors added to F1 and carry no information.
    cblock = [list(v[n_w:]) for v in ns]
    d_surv = EX.rank_modp(cblock, d0, p) if cblock else 0
    if verbose:
        print(f"  combined system {Mfull.shape}, nullity {len(ns)}; "
              f"surviving directions {d_surv} of {d0}", flush=True)
    return d0, d_surv, bg_co


def reducible_dim(ginv0, rank, dx, dy, den, p):
    """Dimension of the reducible span at this rank -- the floor that survives by construction."""
    _, prods, names = EX.generators(ginv0, rank, den)
    mons = K.monomials(rank)
    mkey = {tuple(m): n for n, m in enumerate(mons)}
    cols, _ = coefficient_basis(mons, dx, dy, den)
    cidx = {c: n for n, c in enumerate(cols)}
    rvecs = []
    for val in prods:
        v = np.zeros(len(cols), dtype=np.int64)
        pol = sp.Poly(sp.expand(val), *R.MO)
        for e, co in zip(pol.monoms(), pol.coeffs()):
            mi = mkey.get(tuple(e))
            if mi is None:
                continue
            num, dd = sp.fraction(sp.cancel(sp.together(co)))
            q = sp.cancel(sp.together(den / dd))
            assert sp.denom(q) == 1, "a reducible needs a larger denominator power"
            pp = sp.Poly(sp.expand(num * q), x, y)
            for jk, c2 in zip(pp.monoms(), pp.coeffs()):
                assert jk[0] <= dx and jk[1] <= dy, "a reducible does not fit the box"
                v[cidx[(mi, jk[0], jk[1])]] = int(c2) % p
        rvecs.append(v)
    return EX.rank_modp([list(v) for v in rvecs], len(cols), p), names


def kerr_family_derivative(wrt):
    """d(g^ab)/d(parameter) for the Kerr family, evaluated at M=1, a=1/2.

    THE POINT OF THIS CONTROL. Kerr(M+zeta, a) and Kerr(M, a+zeta) ARE Kerr for every zeta, so
    the Carter constant survives to first order by construction -- exactly, not approximately.
    A solver that reports Carter dying under this perturbation is broken, and every "does not
    survive" it prints elsewhere would be worthless."""
    Ms, As = sp.symbols("M_s a_s", positive=True)
    g = MM.kerr_metric(Ms, As)
    gi = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(g.inv()[i, j])))
    par = Ms if wrt == "M" else As
    d = sp.Matrix(4, 4, lambda i, j: sp.diff(gi[i, j], par))
    return sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(
        d[i, j].subs({Ms: sp.Integer(1), As: sp.Rational(1, 2)}))))


def representable(expr, dx, dy, den):
    """Is `expr` of the form (polynomial of degree <= (dx,dy)) / den?"""
    num, dd = sp.fraction(sp.cancel(sp.together(expr)))
    q = sp.cancel(sp.together(den / dd))
    if sp.denom(q) != 1:
        return False
    pp = sp.Poly(sp.expand(num * q), x, y)
    return pp.degree(x) <= dx and pp.degree(y) <= dy


def check_perturbation_representable(ginv1, dx, dy, den):
    """H1 MUST lie inside the ansatz, or the reducible floor is not what it looks like.

    H = H0 + zeta*H1 is exactly conserved, so the background Hamiltonian H0 extends if and only if
    F1 = H1 is available -- and H1's coefficients are just the entries of ginv1. If those are not
    representable as (polynomial)/den, the solver correctly reports that H0 does not extend WITHIN
    ITS ANSATZ, the floor drops from 4 to 3, and the control fails for a reason that has nothing to
    do with the solver.

    That is exactly what happened on 2026-09-02: a 'generic' perturbation was written with
    denominators (1+x^2+y^2), (1+x^3), (2+x+y^4), (3+x^2), (1+x^4), none of which divide L^2. The
    run took 4.5 hours to report 'surviving 3, expected 4' and the control was blamed on the
    solver. This check costs milliseconds and answers it up front."""
    bad = [(i, j) for i in range(4) for j in range(i, 4)
           if ginv1[i, j] != 0 and not representable(ginv1[i, j], dx, dy, den)]
    return bad


def generic_perturbation(L=None):
    """A stationary, axisymmetric perturbation with no reason to preserve Carter.

    KNOWN-FAIL PARTNER to the Kerr-family control. t and phi stay cyclic, so p_t, p_phi and H
    remain conserved and every REDUCIBLE tensor must still survive -- the floor of 4. Carter has
    no reason to, and a solver that keeps it here is not discriminating.

    THE DENOMINATOR IS NOT COSMETIC. Entries are polynomials over L so that H1 lands inside the
    ansatz; an 'arbitrary' rational perturbation puts H1 outside it and lowers the floor to 3 for
    reasons that say nothing about the geometry. See check_perturbation_representable."""
    if L is None:
        raise ValueError("generic_perturbation needs the substrate denominator L")
    d = sp.zeros(4, 4)
    d[0, 0] = x / L
    d[1, 1] = (1 + y**2) / L
    d[2, 2] = x**2 / L
    d[3, 3] = (x - y**2) / L
    d[0, 3] = d[3, 0] = y**2 / L
    return sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(d[i, j])))



# ---------------------------------------------------------------------------
# INDEPENDENT CROSS-CHECK: the COVARIANT Killing equation, via gr_engine
# ---------------------------------------------------------------------------
# Everything above works in the Hamiltonian formulation: F = K^{ab} p_a p_b and {H,F} = 0.
# gr_engine implements the SAME physics the other way -- the covariant condition
# grad_(a K_bc) = 0, built from Christoffel symbols, sharing no code with any of this. Two
# formulations agreeing is worth more than either checked twice, and it is the check that a
# formulation error (a sign, a factor of 2 in the index symmetrisation, a wrong bracket
# convention) would survive within one route and not across two.

def K_lower_from_coeffs(F_co, mons, g):
    """rank-2 coefficient functions -> K_ab with LOWER indices.

    F = K^{ab} p_a p_b, so the coefficient of p_a p_b with a != b is 2 K^{ab} (both orderings
    contribute) and the coefficient of p_a^2 is K^{aa}. Getting that factor of 2 wrong is exactly
    the kind of error this cross-check exists to catch, so it is written explicitly."""
    n = K.DIM
    Kup = sp.zeros(n, n)
    for mi, e in enumerate(mons):
        idx = [i for i in range(n) for _ in range(e[i])]
        assert len(idx) == 2, "K_lower_from_coeffs is rank-2 only"
        a, b = idx
        if a == b:
            Kup[a, a] = F_co[mi]
        else:
            Kup[a, b] = Kup[b, a] = sp.Rational(1, 2) * F_co[mi]
    gm = sp.Matrix(g)
    return sp.Matrix(n, n, lambda i, j: sp.cancel(sp.together((gm * Kup * gm)[i, j])))


def covariant_residual_modp(geo, Kd, p):
    """Count nonzero coefficients of grad_(a K_bc) WITH COEFFICIENTS REDUCED MOD p.

    WHY MOD p AND NOT OVER Q. The solver's vectors are residues in [0,p); lifting one naively to
    an integer gives a DIFFERENT rational number from the true solution, so its bracket is zero
    mod p and generically nonzero over Q. Feeding those residues to an exact rational criterion
    compares two different objects and reports a disagreement that is not there -- which is
    exactly what the first version of this cross-check did, calling all five Kerr tensors
    non-Killing. The comparison has to be made mod p on BOTH sides. (Rational reconstruction is
    the other way to close the gap, and would additionally yield the tensors explicitly.)"""
    n = K.DIM
    X, G = list(K.COORDS), geo.christoffel

    def nab(a, b, c):
        return (sp.diff(Kd[b, c], X[a])
                - sum(G[d][a][b] * Kd[d, c] + G[d][a][c] * Kd[b, d] for d in range(n)))

    bad = 0
    for a in range(n):
        for b in range(n):
            for c in range(b, n):
                term = sp.cancel(sp.together(nab(a, b, c) + nab(b, c, a) + nab(c, a, b)))
                if term == 0:
                    continue
                num, _ = sp.fraction(term)
                for co in sp.Poly(sp.expand(num), x, y).coeffs():
                    q = sp.Rational(co)
                    r = (int(q.p) * pow(int(q.q), p - 2, p)) % p
                    if r:
                        bad += 1
    return bad


def covariant_check_background(g0, bg_co, mons, p, verbose=True):
    """Every background Killing tensor found by the bracket route must satisfy grad_(a K_bc)=0,
    checked mod p so the two sides are the same object (see covariant_residual_modp)."""
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from gr_engine import Geometry
    geo = Geometry(g0, list(K.COORDS))
    good = 0
    for n, F_co in enumerate(bg_co):
        Kd = K_lower_from_coeffs(F_co, mons, g0)
        bad = covariant_residual_modp(geo, Kd, p)
        good += (bad == 0)
        if verbose:
            print(f"    background tensor {n}: covariant residual mod p "
                  f"{'0 -- IS a Killing tensor' if bad == 0 else f'{bad} nonzero -- NOT one'}",
                  flush=True)
    return good


def covariant_known_fail(g0, bg_co, mons, p, verbose=True):
    """The partner check: a deliberately corrupted tensor must be REJECTED by the same routine.

    A covariant checker that has only ever returned 0 has not been shown able to return nonzero,
    and then 'all background tensors verified' would be vacuous."""
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from gr_engine import Geometry
    geo = Geometry(g0, list(K.COORDS))
    F = list(bg_co[0])
    F[0] = F[0] + x**2 * y          # a perturbation with no reason to preserve the equation
    Kd = K_lower_from_coeffs(F, mons, g0)
    bad = covariant_residual_modp(geo, Kd, p)
    if verbose:
        print(f"    KNOWN-FAIL (corrupted tensor 0): residual mod p "
              f"{'0 -- CHECKER IS BLIND' if bad == 0 else f'{bad} nonzero -- checker can reject'}",
              flush=True)
    return bad != 0


if __name__ == "__main__":
    def arg(flag, default=None, cast=str):
        return cast(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default

    rank = arg("--rank", 2, int)
    denpow = arg("--denpow", 2, int)
    margin = arg("--margin", 4, int)
    p = PRIMES[arg("--prime", 0, int)]
    K.set_dim((t, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    ginv0, bname = MM.get(arg("--background", "kerr"))
    L, _, _ = MM.denominator(ginv0)
    den = L**denpow
    _, prods, _ = EX.generators(ginv0, rank, den)
    bx, by = EX.reducible_box(prods, den)
    dx = arg("--dx", bx + margin, int)
    dy = arg("--dy", by + margin, int)
    print(f"{bname}, rank {rank}, den^{denpow}, reducible-holding box x<={bx} y<={by}, "
          f"ansatz x<={dx} y<={dy}, prime {p}", flush=True)
    nred, rnames = reducible_dim(ginv0, rank, dx, dy, den, p)
    print(f"  reducible span: {nred}  ({', '.join(rnames)})", flush=True)

    if "--sgb-static" in sys.argv:
        # THE POSITIVE CONTROL ON REAL sGB DATA. The static (chi^0) sGB solution is still
        # SPHERICALLY SYMMETRIC -- the corrections depend on r only and the angular part is
        # untouched -- so total angular momentum is still conserved and EVERY background Killing
        # tensor must survive. A pipeline reporting anything less at chi^0 is broken, and this
        # tests it on the actual transcribed metric rather than a synthetic perturbation.
        #
        # NOTE ON THE BACKGROUND. Here it is SCHWARZSCHILD, not Kerr. In the axisymmetric sector
        # its rank-2 Killing space is also 5-dimensional -- p_t^2, p_t p_phi, p_phi^2, H and L^2 --
        # but the fifth element is L^2 rather than Carter. (L_x and L_y are Killing vectors of
        # Schwarzschild too, but are not axisymmetric and so lie outside this ansatz by
        # construction; that is a scope limit of the coordinates, not a missing solution.)
        import _kt_sgb as SGB
        gi0, gi1 = SGB.inverse_split()
        # THE ANSATZ MUST BE BUILT FROM THIS BACKGROUND, NOT THE DEFAULT ONE. The first version of
        # this branch swapped in the Schwarzschild-based sGB metric but kept L, den, the box and
        # the reducible span computed from Kerr. Kerr's L carries 4*Delta = 4x^2-8x+1 where
        # Schwarzschild needs (x-2), so the coefficient space was simply wrong for the background:
        # the Killing space came out 4 instead of 5 because L^2 (total angular momentum) was not
        # representable, and since a spherically symmetric perturbation preserves everything in
        # ANY ansatz, the control passed while testing nothing. A control that cannot fail is not
        # a control.
        L, _, _ = MM.denominator(gi0)
        den = L**denpow
        gnames, prods, pnames = EX.generators(gi0, rank, den)
        bx, by = EX.reducible_box(prods, den)
        dx, dy = (dx, dy) if "--box" in sys.argv else (bx + margin, by + margin)
        nred, rnames = reducible_dim(gi0, rank, dx, dy, den, p)
        print(f"\n  sGB static background: generators {gnames}; reducible span {nred} "
              f"({', '.join(rnames)}); box x<={dx} y<={dy}", flush=True)
        bad = check_perturbation_representable(gi1, dx, dy, den)
        if bad:
            sys.exit(f"  PERTURBATION NOT REPRESENTABLE at {bad}: H1 outside the ansatz, so the "
                     f"floor is wrong and this control would be meaningless.")
        print("\n== sGB static (chi^0): every background tensor MUST survive "
              "(spherical symmetry is preserved) ==", flush=True)
        d0, ds, _ = survive(gi0, gi1, rank, dx, dy, den, p)
        print(f"  background {d0}, surviving {ds}", flush=True)
        if ds != d0:
            sys.exit(f"\n  CONTROL FAILED: only {ds} of {d0} survive a perturbation that "
                     f"preserves spherical symmetry. Either the pipeline or the transcribed "
                     f"metric is wrong; no sGB result may be reported.")
        # Schwarzschild is spherically symmetric, so Lsq IS conserved and the axisymmetric rank-2
        # Killing space is 5-dimensional. Anything less means the ansatz cannot hold Lsq and the
        # control is not exercising the property it claims to test.
        if rank == 2 and d0 < 5:
            sys.exit(f"\n  CONTROL VACUOUS: background dimension {d0} < 5 at rank 2 on a "
                     f"spherically symmetric background -- Lsq is not representable in this "
                     f"ansatz, so 'everything survives' is trivially true and tests nothing.")
        print("  CONTROL PASSED: the static sGB correction kills nothing, as spherical symmetry "
              "requires.", flush=True)
        sys.exit(0)

    if "--crosscheck" in sys.argv:
        # Independent validation of the BACKGROUND stage against the covariant formulation.
        g0 = MM.kerr_metric() if arg("--background", "kerr").startswith("kerr") \
            else MM.zv_metric(int(arg("--background", "kerr").split(":")[1]))
        mons = K.monomials(rank)
        print("\n== covariant cross-check (gr_engine, shares no code with the bracket route) ==",
              flush=True)
        _, _, bg_co = survive(ginv0, sp.zeros(4, 4), rank, dx, dy, den, p, verbose=True)
        good = covariant_check_background(g0, bg_co, mons, p)
        can_fail = covariant_known_fail(g0, bg_co, mons, p)
        print(f"  {good}/{len(bg_co)} background tensors satisfy the COVARIANT Killing equation",
              flush=True)
        if good != len(bg_co):
            sys.exit("\n  CROSS-CHECK FAILED: the two formulations disagree. A tensor the bracket "
                     "route calls Killing is not one covariantly, so one of them is wrong and "
                     "neither may be used.")
        if not can_fail:
            sys.exit("\n  CROSS-CHECK VACUOUS: the covariant routine accepted a corrupted tensor, "
                     "so its agreement above proves nothing.")
        print("  CROSS-CHECK PASSED: both formulations agree on all background tensors, and the "
              "covariant routine rejects a corrupted one.", flush=True)
        sys.exit(0)

    if "--selftest" in sys.argv:
        cases = [("Kerr family d/dM  (Carter MUST survive)", kerr_family_derivative("M"), "all"),
                 ("Kerr family d/da  (Carter MUST survive)", kerr_family_derivative("a"), "all"),
                 ("generic perturbation (Carter must NOT)", generic_perturbation(L), "floor")]
        # --only N runs a single case. The two Kerr-family cases already PASSED on 2026-08-30
        # (5 of 5 surviving, both of them); re-running them costs ~5h before reaching the one
        # case whose answer is still unknown. Their results stand in data/ and are not re-derived
        # here -- but note that a --only run is therefore NOT a full validation on its own, and
        # the PASSED banner below says which cases actually ran.
        if "--only" in sys.argv:
            k = int(sys.argv[sys.argv.index("--only") + 1])
            cases = [cases[k]]
            print(f"  --only {k}: running a single case; the others are not re-verified here",
                  flush=True)
        ok = True
        for name, g1, expect in cases:
            print(f"\n== {name} ==", flush=True)
            bad = check_perturbation_representable(g1, dx, dy, den)
            if bad:
                sys.exit(f"\n  PERTURBATION NOT REPRESENTABLE at entries {bad}: H1 lies outside "
                         f"the ansatz, so H0 cannot extend and the reducible floor is 3, not 4. "
                         f"The control would fail for a reason unrelated to the solver. Fix the "
                         f"perturbation or raise --denpow / the box.")
            d0, ds, _ = survive(ginv0, g1, rank, dx, dy, den, p)
            want = d0 if expect == "all" else nred
            verdict = "PASS" if ds == want else "FAIL"
            if ds != want:
                ok = False
            print(f"  background {d0}, surviving {ds}, expected {want} -> {verdict}", flush=True)
        if not ok:
            sys.exit("\n  SELFTEST FAILED: the perturbation solver does not reproduce a case whose "
                     "answer is known independently. No verdict it gives on sGB would mean anything.")
        ran = ", ".join(n for n, _, _ in cases)
        print(f"\n  SELFTEST PASSED for: {ran}", flush=True)
        if len(cases) == 3:
            print("  Exact Kerr-family deformations keep every background tensor, and a generic "
                  "deformation keeps only the reducible floor. The solver can say both.",
                  flush=True)

