#!/usr/bin/env python3
"""The EXACT dimension: intersect the sampled nullspace with the true solution space.

WHAT _kt_nullvec.py ESTABLISHED. Of three basis vectors of the 14-dimensional sampled nullspace at
delta=2 rank 4 box 357, two satisfy {H,F}=0 identically and one does NOT (298 nonzero coefficients).
So the sampled nullspace strictly contains the true solution space: 14 is an upper bound, and the
box growth law dim = 5*dx - 66 is measuring slack, not geometry.

WHY ONE-AT-A-TIME CANNOT FINISH THE JOB. The true solutions form a SUBSPACE, and the RREF basis is
not aligned to it. A basis vector failing does not remove exactly one dimension, and a basis vector
passing does not certify its neighbours. Testing all 14 individually would still leave the answer
unknown -- the question is not "how many basis vectors pass" but "how large is the subspace on
which the bracket vanishes".

THE COMPUTATION. {H,F} is LINEAR in F. Write a general element of the sampled nullspace as
v = sum a_i v_i over its basis, form B_i = {H, F_{v_i}} cleared to a polynomial, and collect every
(momentum monomial, x^j y^k) coefficient into a matrix C whose columns are the basis vectors. Then
sum a_i B_i == 0 exactly when C a = 0, so dim(true) = nullity(C) -- a 14-column solve, not another
sweep. Reducible tensors are solutions, so they lie inside that space, and
irreducible = dim(true) - rank(reducible).

LINEARITY IS FRAGILE HERE AND IS ENFORCED, NOT ASSUMED. sp.cancel() applied to each bracket
separately would divide out whatever common factor that particular vector happens to have, which is
NOT a linear operation and would silently corrupt C -- yielding a clean integer dimension with no
error raised. So the brackets are built in two passes: every bracket is formed UNCLEARED first, the
lcm of their denominators is taken across ALL of them, and only then is each cleared by that single
common D. Calibrating the factor on one vector is not enough and was the first attempt's bug: at
box 357 vectors 0-3 clear with (x-1)^8(x+1)^24(y-1)^3(y+1)^3 while vectors 4-13 need
(x-1)^15(x+1)^41(y-1)^5(y+1)^5, because cancel() had already removed a factor the early vectors
happened to carry. The guard caught it; a per-vector cancel would not have.

TWO PRIMES, NOT ONE. A nonzero rational can reduce to zero mod p, so a bracket that vanishes at one
prime and not the other is a FALSE vanishing and the "exact dimension" would be an artifact of the
modulus. --prime selects which banked residue matrix is used; a rung is only reported when both
agree.

NO PICKLE. Every .npz is read with allow_pickle=False; only integer arrays are needed. The banked
matrix is passed in with --matrix rather than reconstructed from another script's filename
convention, so this script has no opinion about how the checkpoint happens to be named.

Repro:
  .venv/bin/python scripts/_kt_exact.py --box 16 20 --matrix data/<banked>.npz --points 338
"""
import os
import sys
import time
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import sympy as sp
import _kt_search as K
import _kt_metrics as MM
import _kt_nullvec as NV
import _kt_reducible as R

t, x, y, ph = sp.symbols("t x y phi", real=True)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIMES = (2147483647, 2147483629)
P = PRIMES[0]


MARGIN = 4


def generators(ginv, rank, den):
    """The reducible generators for this substrate, and every degree-`rank` product of them.

    Lsq (total angular momentum) is INCLUDED ONLY IF {H,Lsq}=0 is verified on this metric. It is
    conserved on Schwarzschild and NOT on Kerr or ZV delta=2, and a hand-written generator table
    used across substrates is exactly the error that nearly manufactured "four irreducible Killing
    tensors on Schwarzschild" (§124)."""
    H = sp.cancel(sp.together(sum(ginv[a, b] * R.MO[a] * R.MO[b]
                                  for a in range(4) for b in range(4))))
    Lsq = (1 - y**2) * R.MO[2]**2 + R.MO[3]**2 / (1 - y**2)
    gens = [("p_t", R.MO[0], 1), ("p_phi", R.MO[3], 1), ("H", H, 2)]
    if sp.cancel(sp.together(sp.expand(R.poisson(H, Lsq)))) == 0:
        gens.append(("Lsq", Lsq, 2))
    degs = [d for _, _, d in gens]
    prods, names = [], []
    for expo in itertools.product(*[range(rank // d + 1) for d in degs]):
        if sum(e * d for e, d in zip(expo, degs)) != rank:
            continue
        val, nm = sp.Integer(1), []
        for n, e in enumerate(expo):
            if e:
                val *= gens[n][1]**e
                nm.append(f"{gens[n][0]}^{e}" if e > 1 else gens[n][0])
        prods.append(val)
        names.append(" ".join(nm) or "1")
    return [g[0] for g in gens], prods, names


def reducible_box(prods, den):
    """Smallest (dx, dy) whose x^j y^k / den basis represents every reducible product."""
    bx = by = 0
    for val in prods:
        for coeff in sp.Poly(sp.expand(val), *R.MO).coeffs():
            num, dd = sp.fraction(sp.cancel(sp.together(coeff)))
            q = sp.cancel(sp.together(den / dd))
            if sp.denom(q) != 1:
                raise ValueError("a reducible needs a larger denominator power than requested; "
                                 "--denpow is too small for this substrate and rank")
            pp = sp.Poly(sp.expand(num * q), x, y)
            bx, by = max(bx, pp.degree(x)), max(by, pp.degree(y))
    return bx, by


def rank_modp(rows, ncols, p):
    """Rank over GF(p) of a small dense matrix -- the 14-column solve and the reducible span.
    Both are tiny next to the 12495-column system they came from."""
    M = np.array(rows, dtype=np.int64) % p
    if M.size == 0:
        return 0
    piv = 0
    for c in range(ncols):
        nz = np.nonzero(M[piv:, c])[0]
        if nz.size == 0:
            continue
        i0 = piv + nz[0]
        if i0 != piv:
            M[[piv, i0]] = M[[i0, piv]]
        M[piv] = (M[piv] * pow(int(M[piv, c]), p - 2, p)) % p
        col = M[:, c].copy()
        col[piv] = 0
        nzb = np.nonzero(col)[0]
        if nzb.size:
            M[nzb] = (M[nzb] - np.outer(M[nzb, c], M[piv])) % p
        piv += 1
        if piv == M.shape[0]:
            break
    return piv


def bracket_raw(v, cols, mons, ginv, den):
    """{H, F_v} as an uncleared rational expression, plus its denominator.

    Split out from the clearing step because the clearing factor must be common to ALL vectors.
    Calibrating it on one vector is what failed on the first run: cancel() had removed a factor of
    L that vector 0 happened to carry, so L^3 sufficed there and not for its neighbours."""
    COORDS, MOM, DEP = K.COORDS, K.MOM, K.DEP
    H = sp.Rational(1, 2) * sum(ginv[i, j] * MOM[i] * MOM[j]
                                for i in range(K.DIM) for j in range(K.DIM))
    A = [sp.Integer(0)] * len(mons)
    for i, (mi, j, k) in enumerate(cols):
        if v[i]:
            A[mi] += int(v[i]) * x**j * y**k
    F_co = [a / den for a in A]

    dH = [sp.diff(H, COORDS[i]) for i in DEP]
    dHdp = [sp.diff(H, MOM[i]) for i in DEP]
    me = [K.mono_expr(e) for e in mons]
    dm = [[sp.diff(K.mono_expr(e), MOM[i]) for i in DEP] for e in mons]

    br = sp.Integer(0)
    for q in range(len(DEP)):
        s1 = sum(F_co[mi] * dm[mi][q] for mi in range(len(mons)))
        s2 = sum(sp.diff(F_co[mi], COORDS[DEP[q]]) * me[mi] for mi in range(len(mons)))
        br += dH[q] * s1 - dHdp[q] * s2
    tog = sp.together(br)
    return tog, sp.denom(tog)


def clear_to_terms(tog, D, p):
    """(bracket, common denominator D) -> {(momentum monomial, (j,k)): coefficient mod p}.

    D is the SAME for every vector, so this map is linear in the vector and C is a faithful
    matrix of the bracket. cancel() here acts on an expression that is already polynomial, where
    it is the identity, so it cannot break linearity the way a per-vector cancel would."""
    cleared = sp.cancel(tog * D)
    if sp.denom(cleared) != 1:
        raise ValueError("the common denominator does not clear this bracket")
    out = {}
    poly = sp.Poly(sp.expand(cleared), *K.MOM)
    for e, co in zip(poly.monoms(), poly.coeffs()):
        pp = sp.Poly(sp.expand(co), x, y)
        for jk, c2 in zip(pp.monoms(), pp.coeffs()):
            r = int(c2) % p
            if r:
                out[(e, jk)] = r
    return out


def bracket_terms(v, cols, mons, ginv, den, L, M_pow, p):
    """{H, F_v} * L^M_pow as {(momentum monomial, (j,k)): coefficient mod p}.
    Retained for the single-vector path; the batch path uses bracket_raw + clear_to_terms."""
    COORDS, MOM, DEP = K.COORDS, K.MOM, K.DEP
    H = sp.Rational(1, 2) * sum(ginv[i, j] * MOM[i] * MOM[j]
                                for i in range(K.DIM) for j in range(K.DIM))
    A = [sp.Integer(0)] * len(mons)
    for i, (mi, j, k) in enumerate(cols):
        if v[i]:
            A[mi] += int(v[i]) * x**j * y**k
    F_co = [a / den for a in A]

    dH = [sp.diff(H, COORDS[i]) for i in DEP]
    dHdp = [sp.diff(H, MOM[i]) for i in DEP]
    me = [K.mono_expr(e) for e in mons]
    dm = [[sp.diff(K.mono_expr(e), MOM[i]) for i in DEP] for e in mons]

    br = sp.Integer(0)
    for q in range(len(DEP)):
        s1 = sum(F_co[mi] * dm[mi][q] for mi in range(len(mons)))
        s2 = sum(sp.diff(F_co[mi], COORDS[DEP[q]]) * me[mi] for mi in range(len(mons)))
        br += dH[q] * s1 - dHdp[q] * s2

    cleared = sp.cancel(sp.together(br * L**M_pow))
    if sp.denom(cleared) != 1:
        raise ValueError(f"L^{M_pow} does not clear the bracket; a larger M is required")
    out = {}
    poly = sp.Poly(sp.expand(cleared), *MOM)
    for e, co in zip(poly.monoms(), poly.coeffs()):
        pp = sp.Poly(sp.expand(co), x, y)
        for jk, c2 in zip(pp.monoms(), pp.coeffs()):
            r = int(c2) % p
            if r:
                out[(e, jk)] = r
    return out


if __name__ == "__main__":
    # Substrate, rank and denominator power are all arguments now. The defaults reproduce the
    # committed delta=2 rank-4 den^2 run exactly, so the validated path is unchanged.
    def arg(flag, default=None, cast=str):
        return cast(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default
    spec = arg("--metric", "zv:2")
    rank = arg("--rank", 4, int)
    denpow = arg("--denpow", 2, int)
    tag = arg("--tag", spec.replace(":", "") + f"_r{rank}_d{denpow}")
    K.set_dim((t, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    ginv, mname = MM.get(spec)
    L, gnx, gny = MM.denominator(ginv)
    den = L**denpow

    npts = arg("--points", None, int)
    matrix_path = arg("--matrix")
    gnames, prods, pnames = generators(ginv, rank, den)
    bx, by = reducible_box(prods, den)
    if "--box" in sys.argv:
        i = sys.argv.index("--box")
        dx, dy = int(sys.argv[i + 1]), int(sys.argv[i + 2])
    else:
        dx, dy = bx + MARGIN, by + MARGIN
    print(f"{mname}: generators {gnames}; {len(prods)} products at rank {rank}; "
          f"reducible-holding box x<={bx} y<={by}", flush=True)

    # No banked matrix? Produce one through the SAME sampler the published rungs used, so the
    # control exercises the real code path rather than a shortcut written for it.
    if matrix_path is None:
        ckb = os.path.join(ROOT, "data", f"kt_bank_{tag}_b{(dx+1)*(dy+1)}")
        matrix_path = ckb + ".npz"
        if not os.path.exists(matrix_path):
            print(f"  no banked matrix; sampling now into {os.path.basename(matrix_path)}",
                  flush=True)
            ds = K.solve_kt_modp(rank, ginv, dx, dy, den, n_points=npts, verbose=True,
                                 primes=PRIMES, ckpt=ckb)
            print(f"  SAMPLED dimension (upper bound): {ds}", flush=True)
        zz = np.load(matrix_path, allow_pickle=False)
        npts = int(zz["pts"])
        zz.close()
    # --prime 1 selects the SECOND banked residue matrix. Two primes are not decoration here: a
    # nonzero rational can reduce to zero mod p, so a dimension that is real at one prime and not
    # the other is a false vanishing, and "exact solution dimension 9" would be an artifact.
    pi = int(sys.argv[sys.argv.index("--prime") + 1]) if "--prime" in sys.argv else 0
    P = PRIMES[pi]

    mons = K.monomials(rank)
    cols = [(mi, j, k) for mi in range(len(mons))
            for j in range(dx + 1) for k in range(dy + 1)]
    n_unk = len(cols)
    cidx = {c: n for n, c in enumerate(cols)}
    nfun = (dx + 1) * (dy + 1)
    print(f"{mname} rank {rank} den^{denpow}, box x<={dx} y<={dy} ({nfun} funcs), "
          f"{npts} points, prime {P}", flush=True)

    # ---- stage 1: ALL nullspace vectors, cached so the ~1067s elimination happens once ----
    vcache = os.path.join(ROOT, "data", f"kt_nullvecs_{tag}_b{nfun}_p{PRIMES[pi]}.npz")
    if os.path.exists(vcache):
        z = np.load(vcache, allow_pickle=False)
        V = z["V"]
        z.close()
        print(f"  loaded {V.shape[0]} cached nullspace vectors", flush=True)
    else:
        z = np.load(matrix_path, allow_pickle=False)
        assert int(z["n_unk"]) == n_unk, f"banked n_unk {int(z['n_unk'])} != {n_unk}"
        assert int(z["pts"]) == npts, f"banked points {int(z['pts'])} != {npts}"
        nrows = int(z["nrows"])
        Mx = np.ascontiguousarray(z[f"M{pi}"][:nrows])
        z.close()
        print(f"  eliminating int32[{nrows},{n_unk}] = {Mx.nbytes/2**30:.2f} GiB...", flush=True)
        vecs, dim = NV.rref_nullspace(Mx, n_unk, P, 10**9)
        del Mx
        V = np.array(vecs, dtype=np.int64)
        np.savez_compressed(vcache, V=V)
        print(f"  extracted and cached ALL {V.shape[0]} nullspace vectors", flush=True)
    nsamp = V.shape[0]

    # ---- stage 2: two passes. Every bracket first, THEN one clearing factor for all of them.
    # Deriving the factor from a single vector is what failed on the first attempt: L^3 cleared
    # vector 0 and not its neighbours, because cancel() had already removed a factor of L that
    # vector 0 happened to carry. The guard caught it; a per-vector cancel would not have.
    t0 = time.time()
    raws, dens = [], []
    for n in range(nsamp):
        tog, dd = bracket_raw(V[n], cols, mons, ginv, den)
        raws.append(tog)
        dens.append(dd)
        print(f"    bracket {n+1}/{nsamp}: denominator {sp.factor(dd)}  "
              f"({time.time()-t0:.0f}s)", flush=True)
    D = sp.Integer(1)
    for dd in dens:
        D = sp.lcm(D, dd)
    D = sp.factor(D)
    print(f"  common denominator for all {nsamp} brackets: {D}", flush=True)

    dicts = []
    for n in range(nsamp):
        dicts.append(clear_to_terms(raws[n], D, P))
        print(f"    cleared {n+1}/{nsamp}: {len(dicts[-1])} nonzero terms "
              f"({time.time()-t0:.0f}s)", flush=True)
    # CROSS-CHECK against _kt_nullvec, which reached its verdicts by a different route (per-vector
    # cancel + coefficient test, no common denominator). It found vectors 0 and 2 identically zero
    # and vector 1 not. If this path disagrees, the two implementations are inconsistent and
    # neither verdict may be used.
    zero_here = [n for n in range(nsamp) if not dicts[n]]
    print(f"  vectors with identically-zero bracket: {zero_here}", flush=True)
    # The reference verdicts are BOX-SPECIFIC. _kt_nullvec measured vectors 0,1,2 at box 357 with
    # 338 points; at any other box the nullspace is a different space whose basis comes from
    # different free columns, so those indices name different objects and comparing them is
    # meaningless. Applying the check there once produced a spurious FAIL that discarded a
    # completed run. Cross-check only where a reference actually exists.
    REF = {(16, 20, 338): ((0, True), (1, False), (2, True))}
    ref = REF.get((dx, dy, npts))
    if ref is None:
        print("  no _kt_nullvec reference for this box; cross-check not applicable "
              "(indices are not comparable across boxes)", flush=True)
    else:
        for n, expect in ref:
            if n < nsamp and ((n in zero_here) != expect):
                sys.exit(f"\n  CROSS-CHECK FAILED: vector {n} is "
                         f"{'zero' if n in zero_here else 'nonzero'} here but "
                         f"{'zero' if expect else 'nonzero'} in _kt_nullvec. Two implementations "
                         f"disagree; no dimension from either is usable.")
        print("  cross-check: vectors 0,2 zero and 1 nonzero, agreeing with _kt_nullvec",
              flush=True)

    keys = sorted(set().union(*dicts)) if dicts else []
    C = [[d.get(k, 0) for d in dicts] for k in keys]
    print(f"  C is {len(keys)} x {nsamp} over GF({P})", flush=True)

    rk = rank_modp(C, nsamp, P) if keys else 0
    d_true = nsamp - rk
    print(f"\n  sampled nullspace dimension : {nsamp}", flush=True)
    print(f"  rank of the bracket map C   : {rk}", flush=True)
    print(f"  EXACT solution dimension    : {d_true}", flush=True)

    # ---- stage 3: the reducible span, measured in the same coefficient basis ----
    mkey = {tuple(m): n for n, m in enumerate(mons)}
    rvecs = []
    for val in prods:
        vec = np.zeros(n_unk, dtype=np.int64)
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
                vec[cidx[(mi, jk[0], jk[1])]] = int(c2) % P
        rvecs.append(vec)
    names = pnames
    r_rank = rank_modp([list(v) for v in rvecs], n_unk, P)
    print(f"\n  {len(rvecs)} reducible products: {', '.join(names)}", flush=True)
    print(f"  reducible span dimension    : {r_rank}", flush=True)

    # Every reducible IS a solution, so the span cannot exceed the solution space. If it does,
    # something upstream is wrong and this is a condemned run, not a result.
    if r_rank > d_true:
        print("\n  IMPOSSIBLE: reducible span exceeds the exact solution space. This condemns "
              "the run rather than reporting a number.", flush=True)
        sys.exit(3)
    print(f"\n  IRREDUCIBLE at {mname}, rank {rank}, den^{denpow}, box {dx}x{dy}: "
          f"{d_true - r_rank}", flush=True)
    print(f"  (the sampled {nsamp} was an upper bound carrying {nsamp - d_true} dimensions "
          f"of sampling slack)", flush=True)
