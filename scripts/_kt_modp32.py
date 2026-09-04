#!/usr/bin/env python3
"""Memory-lean nullspace over GF(p): int32 STORAGE, int64 ARITHMETIC on row chunks.

WHY. The dense int64 operator for the double-expansion solver is ~2 GB at rank 3 and ~8 GB at
rank 4 -- against 7.5 GB usable, so rank 4 would swap and rank 5 (20 GB) cannot run at all.
Residues mod a 31-bit prime fit in int32, halving storage; the elimination forms products up to
p^2 ~ 4.6e18, which needs int64, so the update is done on int64 views of row CHUNKS rather than a
whole-matrix temporary. Same trick as solve_kt_modp in _kt_search.

A SEPARATE MODULE, DELIBERATELY. nullspace_modp lives in _kt_perturb.py, which the rank-3 run has
loaded. Editing it mid-run would not affect that process but would leave the on-disk code differing
from what produced its output. This file is new; nothing running depends on it.

Same interface and same elimination ORDER as nullspace_modp, so the two must agree exactly --
checked below on random matrices before this is trusted on anything real.
"""
import numpy as np


def matrix_from_dicts32(dicts, ncols, p):
    """Assemble the coefficient matrix DIRECTLY as int32, reduced into [0, p).

    Why this exists rather than reusing _kt_perturb.matrix_from_dicts: that one allocates int64,
    and at rank 4 the matrix is ~52000 x 20125, i.e. 7.8 GB int64 against 3.9 GB int32 -- more than
    this laptop can hold. Downcasting AFTER assembly does not help; the int64 array has to exist
    first. So the reduction has to happen as the matrix is filled.

    Safe because clear() already returns every entry as int(c) % p, and p = 2^31 - 1, so the
    largest possible value p-1 = 2147483646 is exactly representable in int32."""
    keys = sorted(set().union(*dicts)) if dicts else []
    kidx = {k: i for i, k in enumerate(keys)}
    M = np.zeros((len(keys), ncols), dtype=np.int32)
    for j, d in enumerate(dicts):
        for k, v in d.items():
            r = int(v) % p
            if r:
                M[kidx[k], j] = r
    return M


def matrix_from32(raws, D, p, ncols, clear_fn):
    """matrix_from, assembling int32. clear_fn is _kt_perturb.clear, injected to avoid a cycle."""
    dicts = [clear_fn(r, D, p) for r in raws]
    return matrix_from_dicts32(dicts, ncols, p), dicts


def nullspace_modp32(M, p, chunk=None):
    """Full nullspace basis over GF(p) of an integer matrix. Returns a list of int64 vectors.

    chunk=None sizes the row block so the int64 promotion inside the elimination stays near
    256 MB. At rank 4 (20125 columns) a fixed chunk of 4000 promotes a 644 MB block and then
    allocates another for the outer product -- 1.3 GB of transient on top of a 3.9 GB matrix,
    which is a lot of the headroom to spend on a constant that was picked for a smaller problem."""
    Ain = np.asarray(M)
    if Ain.dtype == np.int32:
        # ALREADY REDUCED, by contract (see matrix_from_dicts32). Do NOT promote to int64 here:
        # at rank 4 that is a transient 7.8 GB allocation to produce the 3.9 GB array we came for,
        # which defeats the entire point of this module. Verified rather than trusted, cheaply.
        if Ain.size and (int(Ain.min()) < 0 or int(Ain.max()) >= p):
            raise AssertionError("int32 input is not reduced into [0, p) -- refusing to eliminate")
        A = np.ascontiguousarray(Ain)
    else:
        A = np.ascontiguousarray(np.asarray(M, dtype=np.int64) % p).astype(np.int32)
    rows, ncols = A.shape if A.size else (0, np.asarray(M).shape[1])
    if chunk is None:
        chunk = max(256, min(4000, (256 * 2**20) // max(1, ncols * 8)))
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
        inv = pow(int(A[piv, c]), p - 2, p)
        A[piv] = ((A[piv].astype(np.int64) * inv) % p).astype(np.int32)
        col = A[:, c].copy()
        col[piv] = 0
        nzb = np.nonzero(col)[0]
        pivrow = A[piv].astype(np.int64)
        for s in range(0, nzb.size, chunk):
            idx = nzb[s:s + chunk]
            blk = A[idx].astype(np.int64)
            blk -= np.outer(blk[:, c], pivrow)
            A[idx] = (blk % p).astype(np.int32)
        piv_col.append(c)
        piv += 1
    pset = set(piv_col)
    free = [c for c in range(ncols) if c not in pset]
    vecs = []
    for f in free:
        v = np.zeros(ncols, dtype=np.int64)
        v[f] = 1
        for r_, c in enumerate(piv_col):
            if A[r_, f]:
                v[c] = (-int(A[r_, f])) % p
        vecs.append(v)
    return vecs


if __name__ == "__main__":
    import sys, os, time
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _kt_perturb import nullspace_modp
    p = 2147483647
    rng = np.random.default_rng(7)
    ok = True
    for (r_, c_, rk) in ((60, 40, 25), (300, 120, 90), (800, 300, 260)):
        # a matrix of KNOWN rank rk: product of random (r_ x rk) and (rk x c_), so the true
        # nullity is c_ - rk and both routines must find exactly that many independent vectors.
        # SMALL ENTRIES, deliberately: with entries near 2^31 the int64 product overflows before
        # the % p, and the "known-rank" matrix silently becomes full-rank garbage -- both routines
        # then correctly report nullity 0 and the test blames them. The first version of this test
        # did exactly that.
        Lm = rng.integers(0, 1000, size=(r_, rk)).astype(np.int64)
        Rm = rng.integers(0, 1000, size=(rk, c_)).astype(np.int64)
        M = (Lm @ Rm) % p
        t0 = time.time(); a = nullspace_modp(M.copy(), p); ta = time.time() - t0
        t0 = time.time(); b = nullspace_modp32(M.copy(), p); tb = time.time() - t0
        same = len(a) == len(b) and all(np.array_equal(u % p, v % p) for u, v in zip(a, b))
        # and every returned vector must actually be in the nullspace -- computed with Python
        # big integers (object dtype), because M @ v in int64 overflows for the same reason the
        # test matrix did: 300 products of ~2^31 x 2^31 exceed 2^63. Two overflows in one test,
        # both reading as failures of a correct routine.
        Mo = M.astype(object)
        inN = all(all(int(z) % p == 0 for z in (Mo @ v.astype(object))) for v in b)
        ok &= same and inN and len(b) == c_ - rk
        print(f"  {r_}x{c_} rank {rk}: nullity int64={len(a)} int32={len(b)} expect {c_-rk}; "
              f"identical={same}; in-nullspace={inN}; {ta:.2f}s vs {tb:.2f}s")
    print("\n  int32 nullspace AGREES with int64 on all cases" if ok else
          "\n  DISAGREEMENT -- do not use the int32 routine")
    sys.exit(0 if ok else 1)
