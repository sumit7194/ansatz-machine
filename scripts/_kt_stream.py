#!/usr/bin/env python3
"""Streaming dense nullspace over GF(p): keep the echelon basis, not the whole matrix.

WHY. The coefficient matrices are ~2.27x taller than wide (rank 4 denpow 7: 55663 x 24500). The
existing routine materialises all of it — 5.1 GB int32 — but Gaussian elimination never needs the
rows it has already consumed: the echelon basis holds AT MOST `ncols` rows, and any row that
reduces to zero is discardable the moment it does. Feeding rows through in blocks and keeping only
pivot rows makes the working set `ncols x ncols` instead of `nrows x ncols`.

    rank 5, box 27x24    dense 13.0 GB  ->  streaming  5.7 GB    fits
    rank 6, box 22x24    dense 19.7 GB  ->  streaming  8.7 GB    fits, but that box is the FLOOR's
                                                                 own minimum, i.e. zero search slack

So this buys rank 5 outright and rank 6 only in a degenerate box. It is a certain 2.27x, unlike the
sparse route whose payoff depends on fill-in and is being measured separately.

CORRECTNESS. Processing columns left to right, the pivot columns are a property of the matrix, and
the reduced row echelon form is unique — so the nullspace basis is identical to the dense routine's,
not merely equivalent. Validation is an equality test.
"""
import numpy as np


def nullspace_stream(row_iter, ncols, p, block=2048, verbose=False):
    """Nullspace over GF(p) from an iterator of dense int64/int32 row blocks (each (k, ncols)).

    Holds at most (ncols x ncols) int32 plus one incoming block."""
    basis = np.zeros((0, ncols), dtype=np.int32)   # echelon rows, one per pivot column
    piv = []                                        # piv[i] = pivot column of basis row i
    for blk in row_iter:
        A = np.asarray(blk, dtype=np.int64) % p
        for r in range(A.shape[0]):
            row = A[r]
            # reduce against the existing basis
            for i, c in enumerate(piv):
                v = row[c]
                if v:
                    row = (row - v * basis[i].astype(np.int64)) % p
            nzs = np.nonzero(row)[0]
            if nzs.size == 0:
                continue                            # dependent: discard, this is the whole saving
            c = int(nzs[0])
            inv = pow(int(row[c]), p - 2, p)
            row = (row * inv) % p
            # back-substitute into the basis so the form stays REDUCED
            col = basis[:, c].astype(np.int64)
            hit = np.nonzero(col)[0]
            if hit.size:
                basis[hit] = ((basis[hit].astype(np.int64)
                               - np.outer(col[hit], row)) % p).astype(np.int32)
            basis = np.vstack([basis, row.astype(np.int32)])
            piv.append(c)
            order = np.argsort(piv)
            basis = basis[order]
            piv = [piv[i] for i in order]
            if len(piv) == ncols:
                break
        if verbose:
            print(f"    stream: {len(piv)} pivots, basis {basis.nbytes/2**30:.2f} GB", flush=True)
        if len(piv) == ncols:
            break
    pset = set(piv)
    free = [c for c in range(ncols) if c not in pset]
    vecs = []
    for f in free:
        v = np.zeros(ncols, dtype=np.int64)
        v[f] = 1
        for i, c in enumerate(piv):
            a = int(basis[i, f])
            if a:
                v[c] = (-a) % p
        vecs.append(v)
    return vecs, {"rank": len(piv), "nullity": len(free),
                  "basis_gb": basis.nbytes / 2**30}


def row_blocks_from_col_dicts(col_dicts, ncols, p, block=512):
    """Yield dense int64 row blocks from COLUMN-oriented sparse dicts, never materialising the
    whole matrix. The sparse pivot is tiny (~168k nonzeros at rank 4); only the emitted block is
    dense, and at block=512 x 24500 that is 100 MB transient against a 5.1 GB full matrix."""
    rows = {}
    for j, d in enumerate(col_dicts):
        for k, v in d.items():
            v %= p
            if v:
                rows.setdefault(k, {})[j] = v
    keys = list(rows)
    for i in range(0, len(keys), block):
        chunk = keys[i:i + block]
        A = np.zeros((len(chunk), ncols), dtype=np.int64)
        for r, k in enumerate(chunk):
            for j, v in rows[k].items():
                A[r, j] = v
        yield A


def nullspace_from_col_dicts(col_dicts, ncols, p, block=512, verbose=False):
    """Streaming nullspace straight from the solver's cleared column dicts."""
    return nullspace_stream(row_blocks_from_col_dicts(col_dicts, ncols, p, block),
                            ncols, p, verbose=verbose)


if __name__ == "__main__":
    import sys, os, time
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _kt_perturb import nullspace_modp
    p = 2147483647
    rng = np.random.default_rng(97)
    ok = True
    print("VALIDATION: streaming vs dense, matrices with KNOWN nonzero nullity.\n")
    for (r_, c_, rk) in ((300, 120, 90), (900, 400, 330), (1500, 700, 600)):
        Lm = rng.integers(0, 1000, size=(r_, rk)).astype(np.int64)
        Rm = rng.integers(0, 1000, size=(rk, c_)).astype(np.int64)
        M = (Lm @ Rm) % p
        t0 = time.time(); dense = nullspace_modp(M.copy(), p); td = time.time() - t0
        def blocks(M=M, n=256):
            for i in range(0, M.shape[0], n):
                yield M[i:i+n]
        t0 = time.time(); strm, st = nullspace_stream(blocks(), c_, p); ts = time.time() - t0
        same = (len(dense) == len(strm)
                and all(np.array_equal(a % p, b % p) for a, b in zip(dense, strm)))
        exp = c_ - rk
        print(f"  {r_}x{c_} rank {rk}: nullity dense {len(dense)} stream {len(strm)} (expect {exp})"
              f"  identical={same}  basis {st['basis_gb']*1024:.1f} MB vs matrix "
              f"{M.nbytes/2**20:.1f} MB  ({td:.2f}s / {ts:.2f}s)")
        ok &= same and len(dense) == exp
    print("\n  " + ("VALIDATED: identical vectors, and the basis is the smaller object."
                    if ok else "FAILED"))
    sys.exit(0 if ok else 1)
