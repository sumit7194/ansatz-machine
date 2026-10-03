#!/usr/bin/env python3
"""OPERATOR-equality check for the sector builder (the Bridge's Gate-2 addition, 2026-10-04).

Builds the FULL operator by the independent dict path (_kt_opfast.operator_columns, as _kt_exact_op uses), finds
its blocks by UNION-FIND (scipy connected components on the bipartite row/column graph), and prints for each block
its column count, nnz and a canonical sorted-COO hash of (global column, canonical row code, value). The canonical row
code uses sorted momentum ids, exactly as _kt_exact_sector.py does. Compare against
`_kt_exact_sector.py ... --ophash --no-solve`: every sector, including the EMPTY-nullspace odd ones, must match one
block entry for entry, and the block column sets must equal the sector column sets.

    .venv/bin/python scripts/_kt_sector_opcheck.py --metric ts2:4/5 --rank 4 --denpow 2 [--prime 0]
"""
import hashlib
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import scipy.sparse as sps  # noqa: E402
from scipy.sparse.csgraph import connected_components  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
import _kt_exact as EX  # noqa: E402
import _kt_metrics as MM  # noqa: E402
import _kt_search as K  # noqa: E402
from _kt_coo import W as WPACK, Codec, from_dicts  # noqa: E402
from _kt_exact_op import get_metric  # noqa: E402
from _kt_opfast import operator_columns  # noqa: E402

x, y = MM.x, MM.y


def main():
    def arg(fl, d=None, c=str):
        return c(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else d
    t0 = time.time()
    spec, rank, denpow = arg("--metric"), arg("--rank", 2, int), arg("--denpow", 1, int)
    margin, prime = arg("--margin", EX.MARGIN, int), arg("--prime", 0, int)
    p = KD.PRIMES[prime]
    t_, ph = sp.symbols("t phi", real=True)
    K.set_dim((t_, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    ginv, name = get_metric(spec)
    L, _, _ = MM.denominator(ginv)
    den = L ** denpow
    _, prods, _ = EX.generators(ginv, rank, den)
    bx, by = EX.reducible_box(prods, den)
    dx, dy = bx + margin, by + margin
    mons = K.monomials(rank)
    n_w = len(mons) * (dx + 1) * (dy + 1)
    H = KD.hamiltonian(ginv)
    D, cols = operator_columns(H, mons, dx, dy, den, p)
    codec, rcs, cis, vis, col0, block = Codec(), [], [], [], 0, []
    per = (dx + 1) * (dy + 1)
    for c in cols:                                   # dict path, streamed to arrays per monomial block
        block.append(c)
        if len(block) == per:
            q = from_dicts(block, codec, p, col0=col0)
            rcs.append(q.rc); cis.append(q.ci); vis.append(q.vi); col0 += per; block = []
    rc = np.concatenate(rcs).astype(np.int64); ci = np.concatenate(cis).astype(np.int64)
    vi = np.concatenate(vis).astype(np.int64)
    del rcs, cis, vis
    # canonical row codes: codec ids (discovery order) -> rank of the momentum tuple in sorted order
    ids = sorted(codec.eid, key=lambda e: e)
    canon = np.zeros(len(codec.eid), np.int64)
    for r_, e in enumerate(ids):
        canon[codec.eid[e]] = r_
    rc = canon[rc // (WPACK * WPACK)] * (WPACK * WPACK) + rc % (WPACK * WPACK)
    print(f"{name} rank {rank} den^{denpow} box {dx}x{dy} prime {prime}: FULL operator (dict path) {n_w} columns, "
          f"{len(vi):,} nonzeros [{time.time()-t0:.0f}s]", flush=True)
    ur, rdense = np.unique(rc, return_inverse=True)
    nr = len(ur)
    G = sps.coo_matrix((np.ones(len(vi), np.int8), (rdense, nr + ci)), shape=(nr + n_w, nr + n_w)).tocsr()
    ncomp, lab = connected_components(G, directed=False)
    collab = lab[nr:]
    used = np.unique(collab[np.unique(ci)])
    print(f"  union-find: {len(used)} blocks containing nonzero columns (empty columns: {n_w - len(np.unique(ci))})",
          flush=True)
    for b in used:
        cmask = collab[ci] == b
        gcol, code, val = ci[cmask], rc[cmask], vi[cmask]
        o = np.lexsort((code, gcol))
        hh = hashlib.sha256(np.stack([gcol[o], code[o], val[o]]).tobytes()).hexdigest()[:16]
        ncols_b = int((collab == b).sum())
        print(f"  BLOCK: cols {ncols_b}, nnz {len(val):,}, canonical-COO hash {hh}", flush=True)
    print(f"  total {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
