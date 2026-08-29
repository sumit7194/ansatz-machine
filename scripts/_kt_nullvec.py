#!/usr/bin/env python3
"""EXTRACT a den^2 solution vector and check {H,F}=0 as a POLYNOMIAL IDENTITY, not at points.

WHY A COUNT IS NOT AN ANSWER. Every den^2 number so far -- delta=2 rank 4 giving 14 at box 357, 24
at 437, 34 at 525 against a reducible span of 9 -- is the nullspace dimension of a system sampled at
random points. Sampling is sound for REJECTING a candidate: a fixed nonzero polynomial almost never
vanishes at random points. It is NOT sound for ACCEPTING one, because the nullspace is chosen AFTER
the points are drawn. Schwartz-Zippel bounds the wrong direction here. dim(sampled) >= dim(true)
always, and nothing in a count says which it is.

So the growth law dim = 5*dx - 66 (exact on all three boxes) admits two readings that no further
sweep can separate: a family of genuine solutions growing with degree, or sampled-nullspace slack
growing with the unknown count. This script separates them. It reconstructs F from a nullspace
vector and asks whether {H,F} vanishes IDENTICALLY in x and y -- one exact question per vector,
cheap next to the runs that produced the counts.

MOD p IS NOT A COMPROMISE HERE. The vector is only defined mod p, so the identity is checked mod p:
{H,F} is formed over Q with the residues as integers, its numerator cleared, and every coefficient
tested === 0 (mod p). A true identity survives; a point-coincidence does not, because it would have
to make a polynomial of bounded degree vanish coefficient-by-coefficient rather than at 338 places.

THE CHECKER IS ITSELF CHECKED. A verifier that has never rejected anything has not been shown to be
able to. --known-fail perturbs one coefficient of a vector that passed and requires the check to
REJECT it. If the perturbed vector also passes, the checker is blind and every PASS it printed is
void; the script says so and exits nonzero.

NO PICKLE. The banked .npz is read with allow_pickle=False. Only M0 and three scalars are needed;
the RNG state (the one pickled member) is irrelevant here because nothing is being resumed.

Repro:  .venv/bin/python scripts/_kt_nullvec.py --box 16 20 --points 338 [--vectors 3] [--known-fail]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import sympy as sp
import _kt_search as K
import _kt_zv as ZV

t, x, y, ph = sp.symbols("t x y phi", real=True)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rref_nullspace(M, n_unk, p, want, verbose=True):
    """Gauss-Jordan mod p, returning `want` nullspace vectors and the dimension.

    Deliberately the SAME elimination as solve_kt_modp, so the vectors come from the reduction
    that produced the published dimension rather than from a second implementation that could
    differ. It records pivot columns, which the dimension-only version had no reason to keep."""
    piv_col, piv = [], 0
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
        for s in range(0, nzb.size, 2000):
            idx = nzb[s:s + 2000]
            blk = M[idx].astype(np.int64)
            blk -= np.outer(blk[:, c], pivrow)
            M[idx] = (blk % p).astype(np.int32)
        piv_col.append(c)
        piv += 1
        if verbose and piv % 2000 == 0:
            print(f"    {piv} pivots  ({time.time()-t1:.0f}s)", flush=True)
    rk = len(piv_col)
    pset = set(piv_col)
    free = [c for c in range(n_unk) if c not in pset]
    if verbose:
        print(f"    rank {rk} -> nullspace dimension {n_unk - rk}  [{time.time()-t1:.0f}s]",
              flush=True)
    # In RREF, each free column f gives a nullspace vector: 1 at f, and -M[r,f] at pivot column r.
    vecs = []
    for f in free[:want]:
        v = np.zeros(n_unk, dtype=np.int64)
        v[f] = 1
        for r, c in enumerate(piv_col):
            if M[r, f]:
                v[c] = (-int(M[r, f])) % p
        vecs.append(v)
    return vecs, n_unk - rk


def check_identity(v, cols, mons, out_mons, ginv, den, p, label):
    """Is {H,F} identically zero mod p? Returns (ok, n_bad_coefficients)."""
    COORDS, MOM, DEP = K.COORDS, K.MOM, K.DEP
    H = sp.Rational(1, 2) * sum(ginv[i, j] * MOM[i] * MOM[j]
                                for i in range(K.DIM) for j in range(K.DIM))
    # Group the unknowns into ONE coefficient function per momentum monomial before any symbolic
    # work. This is what makes the check cheap: 35 polynomials in x,y, not 12495 separate terms.
    A = [sp.Integer(0)] * len(mons)
    for i, (mi, j, k) in enumerate(cols):
        if v[i]:
            A[mi] += int(v[i]) * x**j * y**k
    F_co = [sp.cancel(a / den) for a in A]

    dH = [sp.diff(H, COORDS[i]) for i in DEP]
    dHdp = [sp.diff(H, MOM[i]) for i in DEP]
    me = [K.mono_expr(e) for e in mons]
    dm = [[sp.diff(K.mono_expr(e), MOM[i]) for i in DEP] for e in mons]

    # Same bracket the row assembly builds, grouped: {H,F} = sum_q dH/dq . dF/dp - dH/dp . dF/dq
    br = sp.Integer(0)
    for q in range(len(DEP)):
        s1 = sum(F_co[mi] * dm[mi][q] for mi in range(len(mons)))
        s2 = sum(sp.diff(F_co[mi], COORDS[DEP[q]]) * me[mi] for mi in range(len(mons)))
        br += dH[q] * s1 - dHdp[q] * s2

    poly = sp.Poly(sp.expand(sp.numer(sp.cancel(sp.together(br)))), *MOM)
    bad = 0
    for e in out_mons:
        c = poly.coeff_monomial(K.mono_expr(e))
        if c == 0:
            continue
        num = sp.numer(sp.cancel(sp.together(c)))
        for co in sp.Poly(sp.expand(num), x, y).coeffs():
            if sp.Integer(co) % p != 0:
                bad += 1
    ok = bad == 0
    print(f"  {label}: {'IDENTITY HOLDS' if ok else 'NOT AN IDENTITY'} "
          f"({bad} nonzero coefficients mod p)", flush=True)
    return ok, bad


if __name__ == "__main__":
    delta, rank = 2, 4
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
    den = L**2

    i = sys.argv.index("--box")
    dx, dy = int(sys.argv[i + 1]), int(sys.argv[i + 2])
    npts = int(sys.argv[sys.argv.index("--points") + 1])
    want = int(sys.argv[sys.argv.index("--vectors") + 1]) if "--vectors" in sys.argv else 2

    mons = K.monomials(rank)
    out_mons = K.monomials(rank + 1)
    cols = [(mi, j, k) for mi in range(len(mons))
            for j in range(dx + 1) for k in range(dy + 1)]
    n_unk = len(cols)
    p = 2147483647
    cidx = {c: i for i, c in enumerate(cols)}

    def embed(coeff_by_mono):
        """Coefficient functions {momentum-monomial index: polynomial in x,y} -> a column vector.
        F = sum_mi (A_mi / L^2) * mono_mi, so a tensor with polynomial coefficient C_mi needs
        A_mi = C_mi * L^2."""
        v = np.zeros(n_unk, dtype=np.int64)
        for mi, poly in coeff_by_mono.items():
            pp = sp.Poly(sp.expand(poly * den), x, y)
            for (j, k), co in zip(pp.monoms(), pp.coeffs()):
                assert j <= dx and k <= dy, f"box too small for the self-test: needs x^{j} y^{k}"
                v[cidx[(mi, j, k)]] = int(co) % p
        return v

    if "--selftest" in sys.argv:
        # Validate the CHECKER against tensors whose status is known independently of any run.
        # t and phi are cyclic, so {H, p_t} = {H, p_phi} = 0 and every product of them is a
        # rank-4 solution. If the checker cannot confirm these it cannot be trusted on anything.
        idx = {K.mono_expr(e): i for i, e in enumerate(mons)}
        Pt, Pph = K.MOM[0], K.MOM[3]
        known = [("p_t^4", {idx[Pt**4]: sp.Integer(1)}),
                 ("p_t^2 p_phi^2", {idx[Pt**2 * Pph**2]: sp.Integer(1)}),
                 ("p_phi^4", {idx[Pph**4]: sp.Integer(1)}),
                 ("p_t^3 p_phi + 2 p_phi^4",
                  {idx[Pt**3 * Pph]: sp.Integer(1), idx[Pph**4]: sp.Integer(2)})]
        print("SELFTEST: tensors that are solutions because t and phi are cyclic\n", flush=True)
        good = True
        for name, cb in known:
            ok, _ = check_identity(embed(cb), cols, mons, out_mons, ginv, den, p, name)
            good &= ok
        # And one that is NOT a solution: p_x^4 has no reason to commute with H.
        okbad, badn = check_identity(embed({idx[K.MOM[1]**4]: sp.Integer(1)}),
                                     cols, mons, out_mons, ginv, den, p,
                                     "KNOWN-FAIL p_x^4 (not conserved)")
        if not good:
            sys.exit("\n  SELFTEST FAILED: a known solution was not recognised. The checker is "
                     "wrong; no verdict it gives on a real vector means anything.")
        if okbad:
            sys.exit("\n  SELFTEST FAILED: p_x^4 was accepted as a solution. The checker cannot "
                     "say FAIL and every PASS it prints is void.")
        print(f"\n  SELFTEST PASSED: 4 known solutions accepted, p_x^4 rejected "
              f"({badn} bad coefficients). The checker can say both.", flush=True)
        sys.exit(0)
    ck = os.path.join(ROOT, "data", f"kt_zvd2_d{delta}_r{rank}.pkl.modp.p{npts}.npz")
    print(f"ZV delta={delta} rank {rank} den^2, box x<={dx} y<={dy}, {npts} points", flush=True)
    print(f"  {n_unk} unknowns; reusing banked matrix {os.path.basename(ck)}", flush=True)
    if not os.path.exists(ck):
        sys.exit(f"  banked matrix not found: {ck}")
    z = np.load(ck, allow_pickle=False)
    assert int(z["n_unk"]) == n_unk, f"banked n_unk {int(z['n_unk'])} != {n_unk}"
    nrows = int(z["nrows"])
    assert int(z["pts"]) == npts, f"banked points {int(z['pts'])} != {npts}"
    M = np.ascontiguousarray(z["M0"][:nrows])
    z.close()
    print(f"  loaded int32[{nrows},{n_unk}] = {M.nbytes/2**30:.2f} GiB, prime {p}", flush=True)

    vecs, dim = rref_nullspace(M, n_unk, p, want)
    del M
    print(f"  extracted {len(vecs)} of {dim} nullspace vectors\n", flush=True)

    results = []
    for n, v in enumerate(vecs):
        ok, _ = check_identity(v, cols, mons, out_mons, ginv, den, p, f"vector {n}")
        results.append(ok)

    if "--known-fail" in sys.argv and vecs:
        # A checker that has only ever said PASS has not been shown capable of saying FAIL.
        w = vecs[0].copy()
        j0 = int(np.nonzero(w)[0][0])
        w[j0] = (int(w[j0]) + 1) % p
        ok, bad = check_identity(w, cols, mons, out_mons, ginv, den, p,
                                 "KNOWN-FAIL (vector 0, one coefficient +1)")
        if ok:
            print("\n  CHECKER IS BLIND: a deliberately corrupted vector passed. Every PASS "
                  "above is void.", flush=True)
            sys.exit(2)
        print(f"  checker rejects a 1-coefficient perturbation ({bad} bad coefficients) -- "
              "it is able to say FAIL", flush=True)

    n_ok = sum(results)
    print(f"\n  {n_ok}/{len(results)} extracted vectors are EXACT solutions of the "
          f"Killing equation", flush=True)
    if results and n_ok == len(results):
        print("  The sampled nullspace is NOT slack: these are genuine solutions, and the open "
              "question moves to whether they are reducible.", flush=True)
    elif results and n_ok == 0:
        print("  The sampled nullspace IS slack: 14/24/34 are upper bounds inflated by sampling, "
              "and no irreducibility claim survives them.", flush=True)
