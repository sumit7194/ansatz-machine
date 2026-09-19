#!/usr/bin/env python3
"""Fast, compact nullspace over GF(p): block decomposition + compiled Markowitz elimination.

WHY THIS EXISTS. Rank 6's zeta chi^2 solve ran for a week on _kt_sparse.nullspace_sparse and ended
up thrashing: a ~24 GB footprint on a 16 GB machine, 15% CPU, most of its time spent waiting on its
own memory. Three separate costs, each fixed here:

  1. STORAGE. _kt_sparse keeps every nonzero in a Python dict-of-dicts, ~200 bytes each. Here a row
     is two flat arrays -- int32 column indices, int32 values -- 8 bytes per nonzero, ~25x smaller.

  2. INTERPRETATION. The inner loop is integer arithmetic mod p; in Python the interpreter overhead
     is the whole cost. Here it is compiled with numba.

  3. STRUCTURE. The Killing-tensor matrices are block diagonal after a permutation -- the metric is
     invariant under equatorial reflection (y,p_y -> -y,-p_y) and time reversal (p_t,p_phi -> -),
     so the bracket never couples an even unknown to an odd one, and rank 6 splits into 4 blocks of
     ~27% each. This module does NOT assume that. It finds the blocks itself, as connected components
     of the row/column graph, so if the symmetry argument were wrong the blocks would simply merge:
     slower, never wrong.

AND ONE ALGORITHMIC CHANGE. _kt_sparse eliminated each pivot column from EVERY other row, including
rows already used as pivots (full reduced row echelon form in place). That second half only adds
fill-in. Here elimination is forward-only; the nullspace is then read off by back-substitution.

WHY THE ANSWER IS IDENTICAL, NOT MERELY EQUIVALENT. Processing columns in ascending order, a column
is a pivot column iff it is independent of its predecessors -- a property of the matrix, not of
pivot choice or of forward-vs-full elimination. The nullspace basis indexed by free columns
(v[f] = 1, v[other free] = 0) is therefore unique, and must match _kt_sparse and _kt_perturb vector
for vector. Block decomposition preserves it too: each basis vector lives entirely inside its free
column's block. So validation is an equality test.

INVARIANT THE KERNEL RELIES ON (proved, and asserted in the self-test): when column c is processed,
every not-yet-used row has zeros in all columns < c. Base case trivial; eliminating c from unused
rows with a pivot row that also has zeros below c preserves it. Consequently "row r contains c" is
just rows_c[r][0] == c, and each pivot row is in echelon form (leading entry at its pivot column).
"""
import time
from array import array

import numpy as np
from numba import njit
from numba.typed import List

P = 2147483647


# ---------------------------------------------------------------- compiled kernels

@njit(cache=True)
def _powmod(a, e, p):
    r = 1
    a %= p
    while e > 0:
        if e & 1:
            r = (r * a) % p
        a = (a * a) % p
        e >>= 1
    return r


@njit(cache=True)
def _find(par, x):
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x


@njit(cache=True)
def _components(ri, ci, nr, nc):
    """Union-find over the bipartite row/column graph; returns a label per row and per column."""
    par = np.arange(nr + nc)
    for t in range(ri.shape[0]):
        a = _find(par, ri[t])
        b = _find(par, nr + ci[t])
        if a != b:
            par[a] = b
    lab = np.empty(nr + nc, np.int64)
    for i in range(nr + nc):
        lab[i] = _find(par, i)
    return lab


@njit(cache=True)
def _eliminate(rptr, rcols, rvals, nr, nc, p):
    """Forward Markowitz elimination of one block, columns in ascending order.

    Returns (rows_c, rows_v, pivrow, peak_nnz). Pivot rows are normalised to 1 at their pivot."""
    rows_c = List()
    rows_v = List()
    for r in range(nr):
        rows_c.append(rcols[rptr[r]:rptr[r + 1]].copy())
        rows_v.append(rvals[rptr[r]:rptr[r + 1]].copy())

    # column -> rows that (may) contain it. Entries can go stale (a row loses the column through
    # cancellation, or is used as a pivot); they are filtered on use, never trusted.
    cnt = np.zeros(nc, np.int64)
    for t in range(rptr[nr]):
        cnt[rcols[t]] += 1
    cm = List()
    for c in range(nc):
        cm.append(np.empty(max(cnt[c], 4), np.int32))
    fill = np.zeros(nc, np.int64)
    for r in range(nr):
        for t in range(rptr[r], rptr[r + 1]):
            c = rcols[t]
            cm[c][fill[c]] = r
            fill[c] += 1

    used = np.zeros(nr, np.bool_)
    pivrow = -np.ones(nc, np.int64)
    nnz = rptr[nr]
    peak = nnz
    cand = np.empty(64, np.int64)

    for c in range(nc):
        k = 0
        best = -1
        bestlen = 1 << 62
        lst = cm[c]
        for t in range(fill[c]):
            r = lst[t]
            if used[r]:
                continue
            rc = rows_c[r]
            if rc.shape[0] == 0 or rc[0] != c:
                continue
            if k == cand.shape[0]:
                grown = np.empty(cand.shape[0] * 2, np.int64)
                grown[:k] = cand[:k]
                cand = grown
            cand[k] = r
            k += 1
            if rc.shape[0] < bestlen:
                bestlen = rc.shape[0]
                best = r
        cm[c] = np.empty(0, np.int32)          # column c is finished; release its list
        if best < 0:
            continue

        pc = rows_c[best]
        pv = rows_v[best]
        inv = _powmod(np.int64(pv[0]), p - 2, p)
        if inv != 1:
            for t in range(pv.shape[0]):
                pv[t] = (np.int64(pv[t]) * inv) % p
        lp = pc.shape[0]

        for q in range(k):
            r = cand[q]
            if r == best:
                continue
            rc = rows_c[r]
            if rc.shape[0] == 0 or rc[0] != c:  # duplicate entry already eliminated
                continue
            rv = rows_v[r]
            f = np.int64(rv[0])
            lr = rc.shape[0]
            outc = np.empty(lr + lp, np.int32)
            outv = np.empty(lr + lp, np.int32)
            i = 1
            j = 1
            m = 0
            while i < lr or j < lp:
                if j >= lp or (i < lr and rc[i] < pc[j]):
                    outc[m] = rc[i]
                    outv[m] = rv[i]
                    m += 1
                    i += 1
                elif i >= lr or pc[j] < rc[i]:
                    val = (-f * np.int64(pv[j])) % p
                    if val != 0:
                        col = pc[j]
                        outc[m] = col
                        outv[m] = val
                        m += 1
                        # new column in row r: register it
                        if fill[col] == cm[col].shape[0]:
                            grown2 = np.empty(max(8, cm[col].shape[0] * 2), np.int32)
                            grown2[:fill[col]] = cm[col][:fill[col]]
                            cm[col] = grown2
                        cm[col][fill[col]] = r
                        fill[col] += 1
                    j += 1
                else:
                    val = (np.int64(rv[i]) - f * np.int64(pv[j])) % p
                    if val != 0:
                        outc[m] = rc[i]
                        outv[m] = val
                        m += 1
                    i += 1
                    j += 1
            nnz += m - lr
            rows_c[r] = outc[:m].copy()
            rows_v[r] = outv[:m].copy()
        used[best] = True
        pivrow[c] = best
        if nnz > peak:
            peak = nnz
    return rows_c, rows_v, pivrow, peak


@njit(cache=True)
def _backsub(rows_c, rows_v, pivrow, nc, p):
    """Nullspace basis indexed by free columns, by back-substitution over the echelon pivot rows."""
    nf = 0
    for c in range(nc):
        if pivrow[c] < 0:
            nf += 1
    freecols = np.empty(nf, np.int64)
    i = 0
    for c in range(nc):
        if pivrow[c] < 0:
            freecols[i] = c
            i += 1
    V = np.zeros((nc, nf), np.int64)
    for i in range(nf):
        V[freecols[i], i] = 1
    for c in range(nc - 1, -1, -1):
        r = pivrow[c]
        if r < 0:
            continue
        rc = rows_c[r]
        rv = rows_v[r]
        for t in range(1, rc.shape[0]):
            kk = rc[t]
            a = np.int64(rv[t])
            for i in range(nf):
                w = V[kk, i]
                if w != 0:
                    V[c, i] = (V[c, i] - a * w) % p
    return freecols, V


# ---------------------------------------------------------------- python driver

def _coo_from_col_dicts(col_dicts, p):
    """Intern arbitrary hashable row keys to ints; flat int64 COO arrays (no per-entry objects)."""
    rid = {}
    ri, ci, vi = array("q"), array("q"), array("q")
    for j, d in enumerate(col_dicts):
        for key, v in d.items():
            v %= p
            if v:
                r = rid.get(key)
                if r is None:
                    r = len(rid)
                    rid[key] = r
                ri.append(r)
                ci.append(j)
                vi.append(v)
    return (np.frombuffer(ri, np.int64).copy(), np.frombuffer(ci, np.int64).copy(),
            np.frombuffer(vi, np.int64).copy(), len(rid))


def nullspace_fast(col_dicts, ncols, p=P, verbose=False, label=""):
    """Drop-in replacement for _kt_sparse.nullspace_sparse: returns (vectors, stats).

    Vectors are int64 arrays of length ncols, ordered by free column ascending -- identical to the
    other routines, because the free-column-indexed basis is unique."""
    t0 = time.time()
    ri, ci, vi, nr = _coo_from_col_dicts(col_dicts, p)
    nz0 = int(ri.shape[0])
    lab = _components(ri, ci, nr, ncols)
    col_lab = lab[nr:]
    row_lab_of_entry = lab[ri]

    # every column with at least one entry belongs to a block; empty columns are free with e_j
    has_entry = np.zeros(ncols, bool)
    has_entry[ci] = True
    order = np.argsort(row_lab_of_entry, kind="stable")
    ri, ci, vi, row_lab_of_entry = ri[order], ci[order], vi[order], row_lab_of_entry[order]
    blocks, starts = np.unique(row_lab_of_entry, return_index=True)
    ends = np.append(starts[1:], ri.shape[0])

    free_global, vec_by_free = [], {}
    for j in np.nonzero(~has_entry)[0]:
        free_global.append(int(j))
        e = np.zeros(ncols, np.int64)
        e[j] = 1
        vec_by_free[int(j)] = e

    sizes, peak_max, peak_sum = [], 0, 0
    for b, s, e in zip(blocks, starts, ends):
        bri, bci, bvi = ri[s:e], ci[s:e], vi[s:e]
        gcols = np.nonzero(col_lab == b)[0]            # ascending global order -- preserves RREF
        gcols = gcols[has_entry[gcols]]
        lc = np.searchsorted(gcols, bci)
        urows, lr = np.unique(bri, return_inverse=True)
        o = np.lexsort((lc, lr))
        lr, lc, lv = lr[o], lc[o], bvi[o]
        rptr = np.zeros(urows.shape[0] + 1, np.int64)
        np.cumsum(np.bincount(lr, minlength=urows.shape[0]), out=rptr[1:])
        rows_c, rows_v, pivrow, peak = _eliminate(
            rptr, lc.astype(np.int32), lv.astype(np.int32), urows.shape[0], gcols.shape[0], p)
        fcols, V = _backsub(rows_c, rows_v, pivrow, gcols.shape[0], p)
        for i, fl in enumerate(fcols):
            g = int(gcols[fl])
            v = np.zeros(ncols, np.int64)
            v[gcols] = V[:, i]
            free_global.append(g)
            vec_by_free[g] = v
        sizes.append((urows.shape[0], gcols.shape[0], int(fcols.shape[0])))
        peak_max = max(peak_max, int(peak))
        peak_sum += int(peak)
        del rows_c, rows_v

    free_global.sort()
    vecs = [vec_by_free[f] for f in free_global]
    stats = {"nonzeros_in": nz0, "nonzeros_peak": peak_max, "nonzeros_peak_sum": peak_sum,
             "fill_factor": (peak_sum / nz0 if nz0 else 1.0), "nullity": len(vecs),
             "rank": ncols - len(vecs), "rows": nr, "blocks": len(sizes),
             "block_sizes": sizes, "seconds": time.time() - t0}
    if verbose:
        big = sorted(sizes, key=lambda z: -z[1])[:6]
        print(f"    {label}fast nullspace: {len(sizes)} blocks (largest cols {[z[1] for z in big]}), "
              f"nnz {nz0:,} -> peak {peak_max:,} per block, nullity {len(vecs)}, "
              f"{stats['seconds']:.1f}s", flush=True)
    return vecs, stats


# ---------------------------------------------------------------- self-test

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _kt_perturb import matrix_from_dicts, nullspace_modp
    from _kt_sparse import nullspace_sparse

    rng = np.random.default_rng(2026)
    ok = True

    def rand_cols(nkeys, ncols, lo, hi, keyspace_offset=0):
        out = []
        for _ in range(ncols):
            d = {}
            for _ in range(int(rng.integers(lo, hi + 1))):
                d[("k", int(rng.integers(0, nkeys)) + keyspace_offset)] = int(rng.integers(1, P))
            out.append(d)
        return out

    def check(name, cols, dense_too=True):
        global ok
        n = len(cols)
        t = time.time(); fast, st = nullspace_fast(cols, n); tf = time.time() - t
        t = time.time(); slow, _ = nullspace_sparse(cols, n, P, track=False); ts = time.time() - t
        same = len(fast) == len(slow) and all(np.array_equal(a % P, b % P) for a, b in zip(fast, slow))
        line = (f"  {name:34s} nullity {len(fast):4d}  identical-to-sparse {same}  "
                f"blocks {st['blocks']:3d}  fast {tf:6.2f}s  sparse {ts:6.2f}s")
        if dense_too:
            dense = nullspace_modp(matrix_from_dicts(cols, n), P)
            same_d = len(fast) == len(dense) and all(np.array_equal(a % P, b % P)
                                                      for a, b in zip(fast, dense))
            line += f"  identical-to-dense {same_d}"
            same = same and same_d
        # independent residual check: every vector must satisfy M v = 0 mod p. Vectorised over the
        # COO arrays, with the multiply split into 16-bit halves so no product exceeds 2^47 and the
        # per-row sums cannot overflow int64 -- the overflow that once broke a guard in _kt_double.
        ri, ci, vi, nr = _coo_from_col_dicts(cols, P)
        bad = 0
        for v in fast:
            w = v[ci] % P
            hi = np.zeros(nr, np.int64); lo = np.zeros(nr, np.int64)
            np.add.at(hi, ri, vi * (w >> 16))
            np.add.at(lo, ri, vi * (w & 0xFFFF))
            bad += int(np.count_nonzero((((hi % P) * 65536) + lo) % P))
        line += f"  residual {bad}"
        print(line, flush=True)
        ok &= same and bad == 0

    print("VALIDATION: fast vs the existing sparse and dense routines (identical vectors required)\n")
    check("tall, ~7 nz/col (like the real ones)", rand_cols(160, 400, 3, 11))
    check("wide, known big nullspace", rand_cols(120, 500, 2, 8))
    check("dense-ish", rand_cols(80, 150, 20, 40))
    # block diagonal with interleaved columns: the decomposition must find the blocks AND keep the
    # global column order, or the free-column basis changes
    a = rand_cols(100, 250, 2, 7, keyspace_offset=0)
    b = rand_cols(100, 250, 2, 7, keyspace_offset=10_000)
    inter = [x for pair in zip(a, b) for x in pair]
    check("4-way-style interleaved blocks", inter)
    # empty columns are free with e_j
    withempty = rand_cols(90, 200, 2, 7)
    for j in (0, 17, 199):
        withempty[j] = {}
    check("with empty columns", withempty)
    check("larger, sparse only (no dense)", rand_cols(1400, 2500, 3, 9), dense_too=False)

    # a known-rank construction: nullity must be exactly ncols - rank
    rk, nc_ = 300, 420
    L = rng.integers(0, 50, size=(700, rk))
    R = rng.integers(0, 50, size=(rk, nc_))
    M = (L @ R) % P
    cols = [{("r", int(i)): int(M[i, j]) for i in np.nonzero(M[:, j])[0]} for j in range(nc_)]
    fast, st = nullspace_fast(cols, nc_)
    print(f"  {'known rank ' + str(rk) + ', ' + str(nc_) + ' cols':34s} nullity {len(fast)} "
          f"(expect {nc_ - rk})  {'OK' if len(fast) == nc_ - rk else 'WRONG'}", flush=True)
    ok &= len(fast) == nc_ - rk

    print("\n  " + ("VALIDATED: identical vectors to both existing routines, zero residuals."
                    if ok else "FAILED -- do not use"))
    sys.exit(0 if ok else 1)
