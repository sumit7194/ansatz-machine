#!/usr/bin/env python3
"""The level matrices as flat arrays: rescale by q WITHOUT building Python dicts.

WHY. Rescaling multiplies every operator column by the same polynomial q (D2 = D*q), and that
DENSIFIES the matrix: at rank 4, zeta chi^2, 1.2M operator nonzeros became 32.6M, held as Python
dict entries at ~200 bytes each -- a 6.8 GB process. Rank 6 starts from 4.0M nonzeros, so its
zeta chi^2 would be ~100M entries, ~20 GB of dicts on a 16 GB machine: the thrashing that stopped
the legacy run (D48), rebuilt one layer up. The Rust solver itself holds 100M nonzeros in ~1 GB.
The fix is to never materialise the product as dicts.

HOW. A row key (e, (j, k)) -- momentum exponent tuple e, powers of x and y -- is packed into one
integer code  (e_id * W + j) * W + k.  Multiplying a column by x^a y^b is then `code + a*W + b`,
so the rescale is vectorised: for each of q's terms, shift the codes and scale the values; then
merge equal (column, code) pairs by sorting. It runs over COLUMN CHUNKS, so the temporary
T-fold expansion never exists for the whole matrix at once.

EXACTNESS. The same entries as _kt_prep.rescale, only stored differently -- checked entry for entry
on real operators below. Rows are renumbered at the end (np.unique), and the nullspace does not
depend on row order, so the Rust solver returns the same unique basis.
"""
import os

import numpy as np

W = 1 << 11          # j, k < 2048; codes stay below 2^32 for up to 1024 momentum monomials


class Codec:
    """Row key (e, (j, k))  <->  int64 code. Momentum tuples get ids as they are first seen."""

    def __init__(self):
        self.eid = {}

    def code(self, e, j, k):
        i = self.eid.get(e)
        if i is None:
            i = self.eid[e] = len(self.eid)
        if not (0 <= j < W and 0 <= k < W):
            raise ValueError(f"exponent ({j},{k}) outside the packing width {W}")
        return (i * W + j) * W + k


class Coo:
    """Entries (code, col, val), val in [1, p). Columns are GLOBAL indices."""

    def __init__(self, rc, ci, vi):
        self.rc, self.ci, self.vi = rc, ci, vi

    @property
    def nnz(self):
        return int(self.rc.shape[0])


def from_dicts(dicts, codec, p, col0=0):
    """Cleared column dicts -> Coo, columns numbered from col0. Stored as uint32 (12 B/entry)."""
    n = sum(len(d) for d in dicts)
    rc = np.empty(n, np.uint32)
    ci = np.empty(n, np.uint32)
    vi = np.empty(n, np.uint32)
    t = 0
    for j, d in enumerate(dicts):
        for (e, (a, b)), v in d.items():
            v %= p
            if v:
                rc[t] = codec.code(e, a, b)
                ci[t] = col0 + j
                vi[t] = v
                t += 1
    return Coo(rc[:t], ci[:t], vi[:t])


class Level:
    """A level's matrix as a list of Coo parts (rescaled operator chunks + sources), never joined."""

    def __init__(self, parts):
        self.parts = parts


def concat(*parts):
    return Coo(np.concatenate([q.rc for q in parts]), np.concatenate([q.ci for q in parts]),
               np.concatenate([q.vi for q in parts]))


def _merge(rc, ci, vi, p):
    """Sum entries with equal (col, code) mod p; drop zeros."""
    key = ci * (1 << 32) + rc
    order = np.argsort(key, kind="stable")
    key, vi = key[order], vi[order]
    first = np.ones(key.shape[0], bool)
    first[1:] = key[1:] != key[:-1]
    starts = np.nonzero(first)[0]
    sums = np.add.reduceat(vi, starts) % p if starts.size else vi[:0]
    ukey = key[starts]
    keep = sums != 0
    ukey, sums = ukey[keep], sums[keep]
    return ukey & 0xFFFFFFFF, ukey >> 32, sums


def rescale(op, terms, p, chunk_entries=40_000_000):
    """op * q for q given as [((a, b), c mod p)], column by column, in bounded memory.

    Values are reduced mod p before summing, so a sum of T terms stays below T * 2^31 < 2^63."""
    T = len(terms)
    if op.nnz and T:
        jmax = int(((op.rc // W) % W).max()) + max(a for (a, _), _ in terms)
        kmax = int((op.rc % W).max()) + max(b for (_, b), _ in terms)
        if jmax >= W or kmax >= W:
            raise ValueError(f"shifted exponents ({jmax},{kmax}) overflow the packing width {W}")
    shift = np.array([a * W + b for (a, b), _ in terms], np.int64)
    coef = np.array([c for _, c in terms], np.int64)
    order = np.argsort(op.ci, kind="stable")
    rc, ci, vi = op.rc[order], op.ci[order], op.vi[order]
    per = max(1, chunk_entries // max(T, 1))      # source entries per chunk
    parts = []
    s = 0
    n = rc.shape[0]
    while s < n:
        e = min(n, s + per)
        if e < n:                                  # never split a column across chunks
            while e < n and ci[e] == ci[e - 1]:
                e += 1
        crc = (rc[s:e, None].astype(np.int64) + shift[None, :]).ravel()
        cci = np.repeat(ci[s:e].astype(np.int64), T)
        cvi = ((vi[s:e, None].astype(np.int64) * coef[None, :]) % p).ravel()
        mrc, mci, mvi = _merge(crc, cci, cvi, p)
        del crc, cci, cvi
        parts.append(Coo(mrc.astype(np.uint32), mci.astype(np.uint32), mvi.astype(np.uint32)))
        s = e
    return parts


def nnz_of(parts):
    return sum(q.nnz for q in parts)


def write_ktm_parts(path, parts, ncols, p):
    """Write the level matrix straight to a KTM1 file from its parts -- no concatenated copy.

    Rows are renumbered through a DENSE lookup table over (e_id, j, k) sized by the actual maxima
    (a few hundred thousand cells), not by np.unique over every entry. Returns (nnz, nrows)."""
    E = J = K = 0
    for q in parts:
        if q.nnz:
            c = q.rc.astype(np.int64)
            E = max(E, int((c >> 22).max()) + 1)
            J = max(J, int(((c >> 11) & (W - 1)).max()) + 1)
            K = max(K, int((c & (W - 1)).max()) + 1)

    def dense(q):
        c = q.rc.astype(np.int64)
        return ((c >> 22) * J + ((c >> 11) & (W - 1))) * K + (c & (W - 1))

    used = np.zeros(max(E * J * K, 1), bool)
    for q in parts:
        if q.nnz:
            used[dense(q)] = True
    remap = (np.cumsum(used) - 1).astype(np.uint32)
    nrows = int(used.sum())
    nnz = nnz_of(parts)
    with open(path, "wb") as fh:
        fh.write(b"KTM1")
        fh.write(np.array([nrows, ncols, nnz, p], dtype="<u8").tobytes())
        for q in parts:
            remap[dense(q)].astype("<u4").tofile(fh)
        for q in parts:
            q.ci.astype("<u4", copy=False).tofile(fh)
        for q in parts:
            q.vi.astype("<u4", copy=False).tofile(fh)
    return nnz, nrows


def guard_vectors(vecs, p, mode=None, seed=0):
    """The vectors a residual guard actually has to check, plus a label naming the policy.

    ``full`` (the default) checks every nullspace vector, which costs one pass over the matrix each.
    At rank 8 that is 941 passes over 585M nonzeros -- 1.7 h of CPU, measured, and more than half the
    wall time of the whole run once the Rust solve is done.

    ``freivalds[:k]`` checks k uniformly random GF(p) combinations instead. Collect the residuals as
    one matrix R = M V^T, where V's rows are the nullspace vectors; the guard is asking whether
    R == 0. For a uniformly random z, R z == 0 holds with probability at most 1/p per probe whenever
    R != 0, so k independent probes miss a broken nullspace with probability at most p^-k. At
    p ~ 2^31 and k = 4 that bound is below 1e-37, for 4 passes instead of 941.

    **The error is one-sided, which is why this is a guard and not a sample.** M (sum_i z_i v_i) =
    sum_i z_i (M v_i), so if every M v_i vanishes the probe vanishes exactly. A nonzero probe
    residual therefore proves a real defect -- there are no false alarms, only a bounded chance of a
    false pass. Contrast a guard that checked a random SUBSET of the vectors, which would miss any
    defect outside the subset with probability nowhere near p^-k.

    Exactness of the combination: each term is reduced by the same 16-bit split the residual loops
    use, so it is below 2^48, and fewer than 2^15 of them are summed -- every accumulator stays
    below 2^63 and the final reduction is exact.
    """
    mode = (mode if mode is not None else os.environ.get("KT_GUARD", "full")).strip().lower()
    n = len(vecs)
    if mode in ("", "full", "all"):
        return list(vecs), f"full, {n} vectors"
    name, _, ks = mode.partition(":")
    if name not in ("freivalds", "probe"):
        raise ValueError(f"KT_GUARD must be 'full' or 'freivalds[:k]', got {mode!r}")
    k = int(ks) if ks else 4
    if k < 1:
        raise ValueError(f"KT_GUARD probe count must be >= 1, got {k}")
    if k >= n:
        return list(vecs), f"full, {n} vectors ({k} probes would cost no less)"
    rng = np.random.default_rng(seed)
    z = rng.integers(0, p, size=(k, n), dtype=np.int64)   # the whole field, so the 1/p bound
    #                                                     is exact (Schwartz-Zippel, degree 1)
    acc = None
    for i, v in enumerate(vecs):
        w = np.asarray(v, dtype=np.int64) % p
        if acc is None:
            acc = [np.zeros(w.shape[0], np.int64) for _ in range(k)]
        for j in range(k):
            b = int(z[j, i])
            acc[j] += (w * (b >> 16)) % p * 65536 + w * (b & 0xFFFF)
    return [a % p for a in acc], f"freivalds, {k} probes over {n} vectors, false-pass < p^-{k}"


def residual_count_file(path, vecs, p, chunk=20_000_000):
    """residual_count on a KTM1 file, read through a memory map in chunks: the matrix is never
    resident in this process, which is the point -- the Rust solver needed that memory."""
    head = np.fromfile(path, dtype="<u8", count=4, offset=4)
    nrows, _, nnz, _ = (int(v) for v in head)
    ri = np.memmap(path, dtype="<u4", mode="r", offset=36, shape=(nnz,))
    ci = np.memmap(path, dtype="<u4", mode="r", offset=36 + 4 * nnz, shape=(nnz,))
    vi = np.memmap(path, dtype="<u4", mode="r", offset=36 + 8 * nnz, shape=(nnz,))
    check, policy = guard_vectors(vecs, p)
    print(f"    residual guard: {policy}", flush=True)
    bad = 0
    for v in check:
        v = np.asarray(v, dtype=np.int64) % p
        acc = np.zeros(nrows, np.float64)
        for s in range(0, nnz, chunk):
            r = np.asarray(ri[s:s + chunk], dtype=np.int64)
            x = np.asarray(vi[s:s + chunk], dtype=np.int64)
            w = v[np.asarray(ci[s:s + chunk], dtype=np.int64)]
            prod = ((x * (w >> 16)) % p * 65536 + x * (w & 0xFFFF)) % p
            acc += np.bincount(r, weights=prod.astype(np.float64), minlength=nrows)
        bad += int(np.count_nonzero(acc.astype(np.int64) % p))
    del ri, ci, vi
    return bad


def compact(m):
    """(ri, ci, vi, nrows) with rows renumbered 0..nrows-1 -- what the solvers take."""
    codes, ri = np.unique(m.rc, return_inverse=True)
    return (ri.astype(np.int64).ravel(), m.ci.astype(np.int64), m.vi.astype(np.int64),
            int(codes.shape[0]))


def residual_count(ri, ci, vi, nrows, vecs, p, chunk=20_000_000):
    """Nonzero rows of M v, summed over vectors; exact, overflow-safe, bounded memory.

    Each product v*w is reduced mod p via a 16-bit split (so no product exceeds 2^47), then row
    sums are accumulated with bincount in float64: every addend is < 2^31 and a row holds far
    fewer than 2^22 entries, so every partial sum is an exact integer below 2^53."""
    bad = 0
    n = ri.shape[0]
    for v in guard_vectors(vecs, p)[0]:
        v = np.asarray(v, dtype=np.int64) % p
        acc = np.zeros(nrows, np.float64)
        for s in range(0, n, chunk):
            r, c, x = ri[s:s + chunk], ci[s:s + chunk], vi[s:s + chunk]
            w = v[c]
            prod = ((x * (w >> 16)) % p * 65536 + x * (w & 0xFFFF)) % p
            acc += np.bincount(r, weights=prod.astype(np.float64), minlength=nrows)
        bad += int(np.count_nonzero(acc.astype(np.int64) % p))
    return bad


if __name__ == "__main__":
    # VALIDATION on real operators: rescale here == _kt_prep.rescale on dicts, entry for entry,
    # and the Rust nullspace of the result == the nullspace of the dict-built matrix.
    import os
    import sys
    import time
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import sympy as sp
    import _kt_double as KD
    import _kt_exact as EX
    import _kt_metrics as MM
    import _kt_search as K
    from _kt_opfast import operator_from_templates
    from _kt_prep import q_terms, rescale as rescale_dicts
    from _kt_rust import nullspace_rust, nullspace_rust_coo

    x, y = sp.symbols("x y", real=True)
    p = KD.PRIMES[0]
    t_, ph = sp.symbols("t phi", real=True)
    K.set_dim((t_, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    GI = KD.kerr_chi_pieces()
    L, _, _ = MM.denominator(GI[0])
    H0 = KD.hamiltonian(GI[0])
    ok = True
    for rank, denpow in ((2, 6), (3, 6)):
        den = L ** denpow
        _, prods, _ = EX.generators(GI[0], rank, den)
        bx, by = EX.reducible_box(prods, den)
        mons = K.monomials(rank)
        dicts0, D = operator_from_templates(H0, mons, bx + 6, by + 6, den, p)
        # the real zeta chi^2 cofactor at these ranks, and a smaller one
        for qexpr in (55125 * (x - 2) ** 20 * (y - 1) ** 7 * (y + 1) ** 7, (x - 2) ** 3 * (y + 1)):
            terms = q_terms(D, sp.expand(D * qexpr), p)
            t0 = time.time()
            ref = [rescale_dicts(d, terms, p) for d in dicts0]
            t_ref = time.time() - t0
            codec = Codec()
            t0 = time.time()
            parts = rescale(from_dicts(dicts0, codec, p), terms, p, chunk_entries=3_000_000)
            t_got = time.time() - t0
            got = concat(*parts)
            refc = from_dicts(ref, codec, p)
            a = sorted(zip(refc.ci.tolist(), refc.rc.tolist(), refc.vi.tolist()))
            b = sorted(zip(got.ci.tolist(), got.rc.tolist(), got.vi.tolist()))
            same_entries = a == b
            # and the nullspace, through both paths
            v_ref, _ = nullspace_rust(ref, len(ref), p, threads=4)
            ri, ci, vi, nr = compact(got)
            v_got, _ = nullspace_rust_coo(ri, ci, vi, nr, len(ref), p, threads=4)
            same_ns = len(v_ref) == len(v_got) and all(np.array_equal(u % p, w % p)
                                                         for u, w in zip(v_ref, v_got))
            # the production path: parts -> file -> Rust on the file -> guard via memory map
            import tempfile
            from _kt_rust import nullspace_rust_file
            with tempfile.TemporaryDirectory() as d:
                path = os.path.join(d, "l.ktm")
                write_ktm_parts(path, parts, len(ref), p)
                v_file, _ = nullspace_rust_file(path, threads=4)
                same_ns &= len(v_file) == len(v_ref) and all(
                    np.array_equal(u % p, w % p) for u, w in zip(v_ref, v_file))
                guard_file = residual_count_file(path, v_file, p)
                bent_f = [v_file[0].copy()] if v_file else []
                if bent_f:
                    jf = int(np.nonzero(bent_f[0])[0][0])
                    bent_f[0][jf] = (bent_f[0][jf] + 1) % p
                guard_file_bad = residual_count_file(path, bent_f, p) if bent_f else 1
            same_ns &= guard_file == 0 and guard_file_bad > 0
            guard0 = residual_count(ri, ci, vi, nr, v_got, p)
            # sabotage: a perturbed vector MUST fail the guard
            bent = [v_got[0].copy()] if v_got else []
            if bent:
                j = int(np.nonzero(bent[0])[0][0])
                bent[0][j] = (bent[0][j] + 1) % p
            guard_bad = residual_count(ri, ci, vi, nr, bent, p) if bent else 1
            good = same_entries and same_ns and guard0 == 0 and guard_bad > 0
            ok &= good
            print(f"  rank {rank}, q with {len(terms):3d} terms: {len(dicts0)} cols, nnz "
                  f"{sum(map(len, dicts0)):,} -> {got.nnz:,}   entries identical {same_entries}   "
                  f"nullspace identical {same_ns} ({len(v_got)})   guard 0 on it {guard0 == 0}, "
                  f"fires on a bent vector {guard_bad > 0}   arrays {t_got:.1f}s vs dicts "
                  f"{t_ref:.1f}s", flush=True)
    print("\n  " + ("VALIDATED: array rescale == dict rescale, same nullspace, guard both ways."
                    if ok else "FAILED"))
    sys.exit(0 if ok else 1)
