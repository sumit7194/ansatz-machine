#!/usr/bin/env python3
"""Exact Killing-tensor count, ONE PARITY SECTOR AT A TIME, with the operator columns built in NumPy.

WHY (docs/notes/TS2_rank6_design.md). On TS the Rust solver already finds exactly 4 blocks: the operator never couples
columns of different parity under (i) y -> -y, p_y -> -p_y (g^ab is even in y, checked) and (ii) (t, phi) -> (-t, -phi),
with p_t, p_phi -> -. Both are canonical and leave H invariant, and the common denominator D is even in y. So the
cost is building and holding the WHOLE operator, not solving it. Here each sector is built, solved and released on its
own, about 1/4 of the memory and disk at a time.

    sector (sy, sT):   column m(p) x^a y^b  with  sy = (b + e_y) mod 2,  sT = (e_t + e_phi) mod 2.

Columns are built from the three D49 templates per monomial by integer index shifts in NumPy:
cleared(m, a, b) = shift(U; a, b) + a shift(V; a-1, b) + b shift(W; a, b-1) mod p. There are no per-column dicts;
entries go straight to uint32 (row code, local column, value) triples, merged mod p.

A sector is solved as its own matrix with LOCAL column indices. An absent column would otherwise count as a free
column and inflate the nullity. Its vectors are mapped back to the global basis for hashing.
  exact = sum of sector nullities; reducible = sum of sector reducible ranks (each product lies in one sector).
  set-hash = SHA-256 of the SORTED global null vectors: basis-order independent and comparable with _kt_exact_op.

    KT_SOLVER=rust .venv/bin/python scripts/_kt_exact_sector.py --metric ts2:4/5 --rank 6 --denpow 3 --prime 0 \\
        [--sectors 0,1,2,3] [--margin 4] [--outdir data/ts2_exact/sectors]
"""
import hashlib
import json
import os
import sys
import time

os.environ.setdefault("KT_SOLVER", "rust")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
import _kt_exact as EX  # noqa: E402
import _kt_metrics as MM  # noqa: E402
import _kt_reducible as R  # noqa: E402
import _kt_search as K  # noqa: E402
from _kt_carter_space import rank_np  # noqa: E402
from _kt_coo import W as WPACK, Coo, Level, _merge  # noqa: E402
from _kt_exact_op import get_metric  # noqa: E402
from _kt_opfast import templates  # noqa: E402

x, y = MM.x, MM.y
SECTORS = [(0, 0), (1, 0), (0, 1), (1, 1)]          # (sy, sT); index = sy + 2 sT


def set_hash(vecs):
    return hashlib.sha256(b"".join(sorted(np.asarray(v, dtype=np.int64).tobytes() for v in vecs))).hexdigest()[:16]


def main():
    def arg(fl, d=None, c=str):
        return c(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else d
    t0 = time.time()
    spec, rank, denpow = arg("--metric"), arg("--rank", 2, int), arg("--denpow", 1, int)
    margin, prime = arg("--margin", EX.MARGIN, int), arg("--prime", 0, int)
    want = [int(s) for s in arg("--sectors", "0,1,2,3").split(",")]
    outdir = arg("--outdir", "data/ts2_exact/sectors")
    os.makedirs(outdir, exist_ok=True)
    p = KD.PRIMES[prime]
    t_, ph = sp.symbols("t phi", real=True)
    K.set_dim((t_, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    ginv, name = get_metric(spec)
    # the sector argument needs g^ab even in y and the (t,phi)-reversal structure: CHECK it, never assume it
    even_y = all(sp.cancel(ginv[i, j] - ginv[i, j].subs(y, -y)) == 0 for i in range(4) for j in range(4))
    cross_ok = all(ginv[i, j] == 0 for i, j in ((0, 1), (0, 2), (1, 2), (1, 3), (2, 3)))
    if not (even_y and cross_ok):
        sys.exit(f"REFUSE: the parity sectors are not exact for {name} (even in y: {even_y}; no t/phi-x/y cross terms: {cross_ok})")
    L, nx, ny = MM.denominator(ginv)
    den = L ** denpow
    gnames, prods, pnames = EX.generators(ginv, rank, den)
    bx, by = EX.reducible_box(prods, den)
    dx, dy = bx + margin, by + margin
    mons = K.monomials(rank)
    n_w = len(mons) * (dx + 1) * (dy + 1)
    tag = f"{spec.replace(':', '').replace('/', 'o')}_r{rank}_d{denpow}_b{dx}x{dy}_p{prime}"
    print(f"{name}: rank {rank}, den L^{denpow}, box {dx}x{dy}, {len(mons)} monomials, {n_w} unknowns, prime {p}; "
          f"sectors {want}; parity structure checked (even in y, no cross terms)", flush=True)

    H = KD.hamiltonian(ginv)
    cache = arg("--templates-cache")
    if cache:   # exact templates computed once (_kt_templates_cache.py; selftest == _kt_opfast.templates), mod this prime
        import _kt_templates_cache as TC
        meta = json.load(open(f"{cache}_meta.json"))
        if (meta["metric"], meta["rank"], meta["denpow"]) != (spec, rank, denpow):
            sys.exit(f"REFUSE: template cache is for {meta}, not ({spec}, {rank}, {denpow})")
        D, cl = TC.load(cache, prime)
        if len(cl) != 3 * len(mons):
            sys.exit(f"REFUSE: template cache has {len(cl)} templates, need {3 * len(mons)}")
        print(f"  templates loaded from cache {cache}_p{prime}.npz", flush=True)
    else:
        D, cl = templates(H, mons, den, p)
    if sp.cancel(D - D.subs(y, -y)) != 0:
        sys.exit("REFUSE: the common denominator D is not even in y; the y-parity sectors would not be exact")
    print(f"  templates: {len(cl)} cleared columns, D even in y [{time.time()-t0:.0f}s]", flush=True)
    # deterministic momentum ids (sorted exponent tuples), so codes do not depend on discovery order
    eids = sorted({e for d in cl for (e, _) in d})
    eid = {e: i for i, e in enumerate(eids)}
    if len(eids) >= 1024:
        sys.exit("too many momentum monomials for the 32-bit code packing")

    def arr(d):
        if not d:
            return np.zeros(0, np.int64), np.zeros(0, np.int64)
        c = np.array([(eid[e] * WPACK + j) * WPACK + k for (e, (j, k)) in d], np.int64)
        v = np.array([v for v in d.values()], np.int64) % p
        return c, v

    def vw(mi):   # U, V = cleared(1,0) - x U, W = cleared(0,1) - y U, as dicts then arrays (once per monomial)
        U = cl[3 * mi]
        V = dict(cl[3 * mi + 1])
        for (e, (j, k)), v in U.items():
            key = (e, (j + 1, k)); V[key] = (V.get(key, 0) - v) % p
        Wd = dict(cl[3 * mi + 2])
        for (e, (j, k)), v in U.items():
            key = (e, (j, k + 1)); Wd[key] = (Wd.get(key, 0) - v) % p
        return arr(U), arr({k: v for k, v in V.items() if v}), arr({k: v for k, v in Wd.items() if v})

    tpl = [vw(mi) for mi in range(len(mons))]
    idx = lambda mi, a, b: (mi * (dx + 1) + a) * (dy + 1) + b

    # reducible products, global basis
    mkey = {tuple(m): n for n, m in enumerate(mons)}
    rvecs = []
    for val in prods:
        vec = np.zeros(n_w, dtype=np.int64)
        pol = sp.Poly(sp.expand(val), *R.MO)
        for e, co in zip(pol.monoms(), pol.coeffs()):
            num, dd = sp.fraction(sp.cancel(sp.together(co)))
            q = sp.cancel(sp.together(den / dd))
            assert sp.denom(q) == 1, "a reducible needs a larger denominator power"
            pp = sp.Poly(sp.expand(num * q), x, y)
            for (a, b), c2 in zip(pp.monoms(), pp.coeffs()):
                assert a <= dx and b <= dy, "a reducible does not fit the box"
                vec[idx(mkey[tuple(e)], a, b)] = int(c2) % p
        rvecs.append(vec)

    summary = {}
    for s in want:
        sy, sT = SECTORS[s]
        ts = time.time()
        gcols = [idx(mi, a, b) for mi, m in enumerate(mons) if (m[0] + m[3]) % 2 == sT
                 for a in range(dx + 1) for b in range(dy + 1) if (b + m[2]) % 2 == sy]
        loc = {g: n for n, g in enumerate(gcols)}
        n_s = len(gcols)
        parts, nnz = [], 0
        for mi, m in enumerate(mons):
            if (m[0] + m[3]) % 2 != sT:
                continue
            bs = np.array([b for b in range(dy + 1) if (b + m[2]) % 2 == sy], np.int64)
            A = np.repeat(np.arange(dx + 1, dtype=np.int64), len(bs))
            B = np.tile(bs, dx + 1)
            col = np.array([loc[idx(mi, a, b)] for a, b in zip(A, B)], np.int64)
            (Uc, Uv), (Vc, Vv), (Wc, Wv) = tpl[mi]
            rc = [(Uc[None, :] + (A * WPACK + B)[:, None]).ravel()]
            ci = [np.repeat(col, len(Uc))]
            vi = [np.tile(Uv, len(A))]
            ma = A > 0
            if ma.any() and len(Vc):
                rc.append((Vc[None, :] + ((A[ma] - 1) * WPACK + B[ma])[:, None]).ravel())
                ci.append(np.repeat(col[ma], len(Vc)))
                vi.append((Vv[None, :] * A[ma][:, None] % p).ravel())
            mb = B > 0
            if mb.any() and len(Wc):
                rc.append((Wc[None, :] + (A[mb] * WPACK + (B[mb] - 1))[:, None]).ravel())
                ci.append(np.repeat(col[mb], len(Wc)))
                vi.append((Wv[None, :] * B[mb][:, None] % p).ravel())
            rcs, cis, vis = _merge(np.concatenate(rc), np.concatenate(ci), np.concatenate(vi), p)
            parts.append(Coo(rcs.astype(np.uint32), cis.astype(np.uint32), vis.astype(np.uint32)))
            nnz += len(vis)
            del rc, ci, vi, rcs, cis, vis
        print(f"  sector {s} (sy={sy}, sT={sT}): {n_s} columns, {nnz:,} nonzeros built [{time.time()-ts:.0f}s]", flush=True)
        if "--ophash" in sys.argv:
            # canonical entry list for the operator-equality check: (GLOBAL column, row code, value), sorted. Row codes
            # use the sorted-momentum ids, so they are canonical; _kt_sector_opcheck.py builds the same from the FULL
            # dict-path operator and its union-find blocks.
            gc_ = np.array(gcols, np.int64)
            gcol = np.concatenate([gc_[q.ci.astype(np.int64)] for q in parts]) if parts else np.zeros(0, np.int64)
            code = np.concatenate([q.rc.astype(np.int64) for q in parts]) if parts else np.zeros(0, np.int64)
            val = np.concatenate([q.vi.astype(np.int64) for q in parts]) if parts else np.zeros(0, np.int64)
            o = np.lexsort((code, gcol))
            hh = hashlib.sha256(np.stack([gcol[o], code[o], val[o]]).tobytes()).hexdigest()[:16]
            print(f"  SECTOR-OPHASH {s}: cols {n_s}, nnz {len(val):,}, canonical-COO hash {hh}", flush=True)
            del gcol, code, val, o
            if "--no-solve" in sys.argv:
                continue
        ns = KD.nullspace_dicts(Level(parts), n_s, p)      # writes its own file in a temp dir, guards, deletes it
        del parts
        dim_s = len(ns)
        G = np.zeros((dim_s, n_w), np.int64)
        gc = np.array(gcols, np.int64)
        for r_, v in enumerate(ns):
            G[r_, gc] = np.array([int(z) % p for z in v], np.int64)
        rs = [v for v in rvecs if v[gc].any()]
        assert all(not v[np.setdiff1d(np.arange(n_w), gc)].any() for v in rs), "a reducible straddles sectors"
        r_rank = rank_np(np.array([v[gc] for v in rs], np.int64), n_s, p) if rs else 0
        joint = rank_np(np.vstack([G[:, gc]] + ([np.array([v[gc] for v in rs], np.int64)] if rs else [])), n_s, p) \
            if (rs or dim_s) else 0
        inside = joint == dim_s
        h = set_hash(list(G))
        summary[s] = dict(sector=[sy, sT], cols=n_s, nnz=nnz, nullity=dim_s, reducible=r_rank,
                          irreducible=dim_s - r_rank, reducibles_inside=inside, set_hash=h,
                          seconds=round(time.time() - ts))
        np.savez_compressed(os.path.join(outdir, f"{tag}_s{s}.npz"), G=G[:, gc], gcols=gc)
        print(f"  SECTOR {s}: nullity {dim_s}, reducible {r_rank}, IRREDUCIBLE {dim_s - r_rank}, reducibles inside "
              f"{inside}, set-hash {h} [{time.time()-ts:.0f}s]", flush=True)
        with open(os.path.join(outdir, f"{tag}_s{s}.json"), "w") as fh:
            json.dump(summary[s], fh)
        if not inside:
            print("  CONDEMNED: a reducible product is not in this sector's solution space", flush=True)
            return 3
    if len(want) == 4:
        tot = sum(v["nullity"] for v in summary.values())
        red = sum(v["reducible"] for v in summary.values())
        allv = []
        for s in want:
            z = np.load(os.path.join(outdir, f"{tag}_s{s}.npz"))
            for row in z["G"]:
                g = np.zeros(n_w, np.int64); g[z["gcols"]] = row; allv.append(g)
        print(f"\n  VERDICT {name} rank {rank} den^{denpow} box {dx}x{dy} prime {prime} (4 sectors): exact {tot}, "
              f"reducible {red}, IRREDUCIBLE {tot - red}; global set-hash {set_hash(allv)}", flush=True)
    print(f"  total {time.time()-t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
