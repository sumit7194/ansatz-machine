#!/usr/bin/env python3
"""EXACT Killing-tensor count on an exact metric, by the template operator + Rust nullspace: no sampling at all.

WHY A NEW DRIVER. _kt_exact.py reaches the exact dimension in two stages: a sampled nullspace (an upper bound), then
an exact bracket test on its basis. That was the right tool when the solver was Python. The template operator
(_kt_opfast, validated identical, D49) builds {H, F} = 0 directly as an exact linear system over GF(p), with columns
m(p) x^a y^b / L^d and rows the (momentum monomial, x^j y^k) coefficients of the cleared bracket. Its nullity IS the
dimension of Killing tensors in the ansatz. Rust solves it (D48), and the residual guard checks every returned vector
against the real matrix.

    exact dim   = nullity of the operator
    reducible   = rank of the products of {p_t, p_phi, H (, Lsq if conserved)} in the same basis, checked INSIDE the
                  solution space (if not, the run is condemned, as in _kt_exact)
    IRREDUCIBLE = exact dim - reducible

Substrates come from _kt_metrics (kerr, zv) plus the TS2 package (ts2:4/5, and ts2kerr:4/5, the Kerr control built by
the SAME pipeline in the same prolate chart). Validated by reproducing the published rungs before use (§127 Kerr,
§124 ZV), and run on two primes.

    KT_SOLVER=rust .venv/bin/python scripts/_kt_exact_op.py --metric ts2:4/5 --rank 2 --denpow 1 [--margin 4] [--prime 0]
"""
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
from _kt_opfast import operator_from_templates  # noqa: E402

x, y = MM.x, MM.y
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS2_FILES = {"4/5": "t1o3", "3/5": "t1o2"}
SREPR_NAMES = {n: getattr(sp, n) for n in ("Add", "Mul", "Pow", "Integer", "Rational", "Symbol")}


def load_package(path):
    """TS2-package component file (our own srepr output) -> 4x4 metric in (t, x, y, phi), sigma = 1 (the scale)."""
    comps = {}
    for line in open(path):
        if line.startswith("#") or " = " not in line:
            continue
        k, v = line.split(" = ", 1)
        comps[k.strip()] = sp.sympify(v.strip(), locals=SREPR_NAMES)
    syms = set().union(*[e.free_symbols for e in comps.values()])
    unknown = [s for s in syms if s.name not in ("x", "y", "sigma")]
    if unknown:
        raise SystemExit(f"unexpected symbols in {path}: {unknown}")
    sub = {s: (x if s.name == "x" else y if s.name == "y" else sp.Integer(1)) for s in syms}
    g = sp.zeros(4, 4)
    for k, (i, j) in {"g_TT": (0, 0), "g_Tphi": (0, 3), "g_phiphi": (3, 3), "g_xx": (1, 1), "g_yy": (2, 2)}.items():
        g[i, j] = g[j, i] = sp.cancel(comps[k].xreplace(sub))
    return g


def get_metric(spec):
    kind, _, par = spec.partition(":")
    if kind in ("ts2", "ts2kerr"):
        tag = TS2_FILES[par]
        f = f"ts2_{'KERR_' if kind == 'ts2kerr' else ''}metric_components_{tag}.txt"
        g = load_package(os.path.join(ROOT, "data", "sealed", "TS2_for_quantum", f))
        name = f"{'Kerr (TS2 pipeline, delta=1)' if kind == 'ts2kerr' else 'Tomimatsu-Sato delta=2'} p={par}"
        return MM.inverse(g), name
    return MM.get(spec)


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
    L, nx, ny = MM.denominator(ginv)
    den = L ** denpow
    gnames, prods, pnames = EX.generators(ginv, rank, den)
    bx, by = EX.reducible_box(prods, den)
    dx, dy = bx + margin, by + margin
    mons = K.monomials(rank)
    n_w = len(mons) * (dx + 1) * (dy + 1)
    pL = sp.Poly(sp.expand(L), x, y)
    print(f"{name}: rank {rank}, den L^{denpow} (L degrees {pL.degree(x)},{pL.degree(y)}; g^ab numerators {nx},{ny}), "
          f"reducible box {bx}x{by} + margin {margin} -> box {dx}x{dy}, {len(mons)} monomials, {n_w} unknowns, "
          f"prime {p}", flush=True)
    print(f"  generators {gnames}; {len(prods)} products: {', '.join(pnames)}", flush=True)

    H = KD.hamiltonian(ginv)
    dicts, D = operator_from_templates(H, mons, dx, dy, den, p)
    nnz = sum(len(d) for d in dicts)
    print(f"  operator built: {len(dicts)} columns, {nnz:,} nonzeros [{time.time()-t0:.0f}s]", flush=True)
    ns = KD.nullspace_dicts(dicts, n_w, p)
    dim = len(ns)
    print(f"  EXACT solution dimension (operator nullity, guarded): {dim} [{time.time()-t0:.0f}s]", flush=True)

    # reducible products in the SAME coefficient basis (monomial-major, then a, then b -- _kt_opfast's order)
    mkey = {tuple(m): n for n, m in enumerate(mons)}
    idx = lambda mi, a, b: (mi * (dx + 1) + a) * (dy + 1) + b
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
    r_rank = rank_np(np.array(rvecs, dtype=np.int64), n_w, p) if rvecs else 0
    N = np.array([[int(z) % p for z in v] for v in ns], dtype=np.int64).reshape(-1, n_w)
    joint = rank_np(np.vstack([N, np.array(rvecs, dtype=np.int64)]), n_w, p) if rvecs else dim
    print(f"  reducible span: {r_rank}; inside the solution space: {joint == dim} "
          f"(rank of solutions + reducibles = {joint})", flush=True)
    if joint != dim:
        print("  CONDEMNED: a reducible product is not in the solution space -- the operator or the basis is wrong.",
              flush=True)
        return 3
    print(f"\n  VERDICT {name} rank {rank} den^{denpow} box {dx}x{dy} prime {prime}: exact {dim}, reducible {r_rank}, "
          f"IRREDUCIBLE {dim - r_rank}", flush=True)
    print(f"  total {time.time()-t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
