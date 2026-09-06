#!/usr/bin/env python3
"""THE DECISIVE TEST: fill-in of sparse elimination on a REAL bracket matrix, not a random one.

Random sparse matrices are the worst case for fill-in and _kt_sparse.py's self-test shows it --
16x, 50x, 103x, growing with size. That says nothing about OUR matrices, which come from Poisson
brackets of polynomials and are structured. Whether rank 6 is reachable turns entirely on which
regime the real thing is in, and that is a measurement.

KNOWN ANSWER, so this is a control and not an exploration: the rank-4 denpow-7 operator matrix has
nullity 14 (the Schwarzschild Killing space at rank 4). §133 measured it with the dense routine.
Sparse must return exactly 14, with identical vectors -- the RREF is unique, so anything else is a
bug in the sparse code and not a different-but-valid answer.

Reports peak fill and the memory a rank-6 run would need if the same fill factor holds.
"""
import sys, os, time, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, sympy as sp
import _kt_double as D, _kt_search as K, _kt_metrics as MM, _kt_perturb as PB, _kt_exact as EX
from _kt_sparse import nullspace_sparse
from _kt_modp32 import matrix_from_dicts32, nullspace_modp32

t, x, y, ph = sp.symbols("t x y phi", real=True)
p = 2147483647

if __name__ == "__main__":
    K.set_dim((t, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    T0 = time.time()
    GI = D.kerr_chi_pieces(); gi0 = GI[0]
    L, _, _ = MM.denominator(gi0); den = L**7
    gn, prods, pn = EX.generators(gi0, 4, den)
    bx, by = EX.reducible_box(prods, den); dx, dy = bx + 6, by + 6
    mons = K.monomials(4)
    cols, F_cos = PB.coefficient_basis(mons, dx, dy, den)
    print(f"rank 4, denpow 7, box {dx}x{dy}, {len(cols)} columns", flush=True)

    H0 = D.hamiltonian(gi0)
    raws, dens = PB.build_columns([(H0, F) for F in F_cos], mons, True, "op ")
    Dd = sp.Integer(1)
    for d_ in dens:
        Dd = sp.lcm(Dd, d_)
    dicts = [PB.clear(r, Dd, p) for r in raws]
    nz = sum(len(d) for d in dicts)
    nrows = len(set().union(*dicts))
    print(f"  built in {time.time()-T0:.0f}s: {nrows} rows, {nz} nonzeros, "
          f"density {100*nz/(nrows*len(cols)):.4f}%", flush=True)
    pickle.dump({"ncols": len(cols), "nrows": nrows, "nz": nz},
                open("data/kt_fillin_r4_meta.pkl", "wb"))

    t0 = time.time()
    vs, st = nullspace_sparse(dicts, len(cols), p, track=True)
    ts = time.time() - t0
    print(f"\n  SPARSE : nullity {st['nullity']}  rank {st['rank']}  "
          f"peak nonzeros {st['nonzeros_peak']:,} ({st['fill_factor']:.1f}x)  [{ts:.0f}s]", flush=True)

    t0 = time.time()
    M = matrix_from_dicts32(dicts, len(cols), p)
    vd = nullspace_modp32(M, p)
    td = time.time() - t0
    print(f"  DENSE  : nullity {len(vd)}  [{td:.0f}s]  matrix {M.nbytes/2**30:.2f} GB", flush=True)

    same = len(vs) == len(vd) and all(np.array_equal(a % p, b % p) for a, b in zip(vs, vd))
    print(f"\n  identical vectors: {same}", flush=True)
    print(f"  expected nullity 14 (Schwarzschild Killing space at rank 4): "
          f"{'PASS' if st['nullity'] == 14 else 'FAIL'}", flush=True)

    # what it implies for rank 6
    peak_bytes = st["nonzeros_peak"] * 16      # dict overhead is far worse; 16 B/nz is optimistic
    r6_cols = 84 * 23 * 25
    scale = (r6_cols / len(cols)) ** 2
    print(f"\n  IMPLICATION FOR RANK 6 (denpow 8, box 22x24, {r6_cols} cols):", flush=True)
    print(f"    if fill scales as cols^2: peak ~{st['nonzeros_peak']*scale:,.0f} nonzeros "
          f"~ {st['nonzeros_peak']*scale*16/2**30:.1f} GB at 16 B/nz", flush=True)
    print(f"    dense for comparison: {r6_cols*int(2.27*r6_cols)*4/2**30:.1f} GB", flush=True)
    print(f"\nTOTAL {time.time()-T0:.0f}s", flush=True)
