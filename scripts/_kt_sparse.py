#!/usr/bin/env python3
"""Sparse nullspace over GF(p) — because these matrices are 0.01% dense and we were storing 0s.

WHY. The rank-4 coefficient matrix is 55663 x 24500 = 1.36e9 cells holding ~168,000 nonzeros: about
6.9 per column, 3 per row, density 0.0124%. Dense int32 that is 5.1 GB; the actual information is
~1.3 MB. Rank 6 needs denpow 8 and would be ~29 GB dense, which does not fit in ~9 GB usable — so
for weeks the box size has been chosen against a number four orders of magnitude larger than the
content of the matrix.

THE REAL CONSTRAINT IS FILL-IN, NOT STORAGE, and that is why this module reports it. Elimination
densifies a sparse matrix; whether rank 6 is reachable depends on how much, which cannot be read off
the density and has to be measured. `nullspace_sparse` returns (vectors, stats) with peak nonzero
count so the question is answered by data rather than by hope.

WHY THE ANSWER IS EXACTLY THE DENSE ONE, not merely close. Processing columns left to right, a
column is a pivot column iff it is independent of its predecessors — a property of the matrix, not
of pivot choice. The reduced row echelon form is therefore UNIQUE, so any correct elimination
yields the same pivot columns, the same free columns, and the same nullspace basis. Choosing pivot
ROWS by sparsity (a Markowitz heuristic) changes the work done and not the result. That is what
makes validation against `nullspace_modp` an equality test rather than a comparison.
"""
import numpy as np


def nullspace_sparse(col_dicts, ncols, p, track=True):
    """Nullspace of the matrix whose column j is col_dicts[j] : {row_key: value}.

    Returns (list of int64 vectors, stats). Row keys may be any hashable; they are interned to
    integers here. Output order matches nullspace_modp: free columns ascending, and within a
    vector, pivot columns carry the back-substituted entries."""
    rows = {}                                   # rid -> {col: val}
    colmap = {}                                 # col -> set of rids
    rid_of = {}
    for j, d in enumerate(col_dicts):
        for k, v in d.items():
            v %= p
            if not v:
                continue
            r = rid_of.setdefault(k, len(rid_of))
            rows.setdefault(r, {})[j] = v
            colmap.setdefault(j, set()).add(r)

    nz0 = sum(len(r) for r in rows.values())
    peak = nz0
    pivot_cols, pivot_row = [], {}
    used = set()

    for c in range(ncols):
        cand = [r for r in colmap.get(c, ()) if r not in used]
        if not cand:
            continue
        # MARKOWITZ: the sparsest eligible row. Fill-in from eliminating with a row of k nonzeros
        # is at worst k-1 new entries per target row, so the sparsest pivot is the cheapest.
        pr = min(cand, key=lambda r: len(rows[r]))
        inv = pow(rows[pr][c], p - 2, p)
        if inv != 1:
            rows[pr] = {k: (v * inv) % p for k, v in rows[pr].items()}
        prow = rows[pr]
        for r in list(colmap.get(c, ())):
            if r == pr:
                continue
            f = rows[r].get(c)
            if not f:
                continue
            tr = rows[r]
            for k, v in prow.items():
                nv = (tr.get(k, 0) - f * v) % p
                if nv:
                    if k not in tr:
                        colmap.setdefault(k, set()).add(r)
                    tr[k] = nv
                elif k in tr:
                    del tr[k]
                    colmap[k].discard(r)
        used.add(pr)
        pivot_cols.append(c)
        pivot_row[c] = pr
        if track:
            nz = sum(len(r) for r in rows.values())
            if nz > peak:
                peak = nz

    pset = set(pivot_cols)
    free = [c for c in range(ncols) if c not in pset]
    vecs = []
    for f in free:
        v = np.zeros(ncols, dtype=np.int64)
        v[f] = 1
        for c in pivot_cols:
            a = rows[pivot_row[c]].get(f)
            if a:
                v[c] = (-int(a)) % p
        vecs.append(v)
    stats = {"nonzeros_in": nz0, "nonzeros_peak": peak,
             "fill_factor": (peak / nz0 if nz0 else 1.0),
             "rank": len(pivot_cols), "nullity": len(free), "rows": len(rows)}
    return vecs, stats


if __name__ == "__main__":
    import sys, os, time
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _kt_perturb import nullspace_modp, matrix_from_dicts
    p = 2147483647
    rng = np.random.default_rng(41)
    ok = True
    print("VALIDATION: sparse vs dense, on matrices with KNOWN nonzero nullity.\n")
    for (nkeys, ncols, per_col) in ((120, 300, 4), (400, 900, 6), (900, 2000, 7)):
        col_dicts = []
        for j in range(ncols):
            d = {}
            for _ in range(rng.integers(2, per_col + 1)):
                d[int(rng.integers(0, nkeys))] = int(rng.integers(1, 10**9))
            col_dicts.append(d)
        M = matrix_from_dicts(col_dicts, ncols)
        t0 = time.time(); dense = nullspace_modp(M.copy(), p); td = time.time() - t0
        t0 = time.time(); sparse, st = nullspace_sparse(col_dicts, ncols, p); ts = time.time() - t0
        same = (len(dense) == len(sparse)
                and all(np.array_equal(a % p, b % p) for a, b in zip(dense, sparse)))
        # and the vectors must really be in the nullspace, checked in exact Python ints
        resid = 0
        for v in sparse[:3]:
            for j, d in enumerate(col_dicts):
                pass
            for k in set().union(*col_dicts):
                s = sum(int(col_dicts[j].get(k, 0)) * int(v[j]) for j in range(ncols))
                resid += s % p
        print(f"  {nkeys}x{ncols}: nullity dense {len(dense)} sparse {len(sparse)}  identical={same}"
              f"  residual={resid}  fill {st['fill_factor']:.2f}x  ({td:.2f}s dense / {ts:.2f}s sparse)")
        ok &= same and resid == 0 and len(dense) > 0
    print("\n  " + ("VALIDATED: identical vectors, zero residual." if ok else "FAILED"))
    sys.exit(0 if ok else 1)
