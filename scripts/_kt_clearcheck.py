#!/usr/bin/env python3
"""Validate the ring-based PB.clear against the expression-based reference PB.clear_expr.

Clearing is where every matrix entry comes from, so the fast version must agree EXACTLY -- the same
dict, key for key -- and must fail in the same places:

  1. all 8 zeta chi^2 SOURCES of rank 3 (the case that motivated it: 210 s of a 346 s run);
  2. operator columns: 300 random raw brackets at rank 2 (denpow 6) and every template bracket at
     rank 3 -- these carry the operator's denominator rather than a source's;
  3. edge cases: zero, a D that does not clear (must raise), a coefficient D cannot make integral
     (must raise -- int() would otherwise truncate 6/7 to 0 and corrupt the matrix silently).
"""
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

import _kt_exact as EX  # noqa: E402
import _kt_metrics as MM  # noqa: E402
import _kt_perturb as PB  # noqa: E402
import _kt_search as K  # noqa: E402
from _kt_srcprof import build_sources  # noqa: E402

x, y = sp.symbols("x y", real=True)
ok = True


def same(tog, D, p, label):
    global ok
    t0 = time.time(); a = PB.clear(tog, D, p); ta = time.time() - t0
    t0 = time.time(); b = PB.clear_expr(tog, D, p); tb = time.time() - t0
    good = a == b
    ok &= good
    return good, ta, tb


def raises(f, *a):
    try:
        f(*a)
    except ValueError:
        return True
    return False


if __name__ == "__main__":
    quick = "--quick" in sys.argv          # the verify.sh gate: 2 sources, 100 operator columns
    srcs, _, D2, p = build_sources(3, 6, 6)
    if quick:
        srcs = srcs[:2]
    ta_s = tb_s = 0
    nbad = 0
    for i, e in enumerate(srcs):
        g, ta, tb = same(e, D2, p, f"src{i}")
        nbad += not g; ta_s += ta; tb_s += tb
    print(f"  rank 3 zeta chi^2 sources: {len(srcs)} checked, {nbad} differing   "
          f"ring {ta_s:.1f}s vs expr {tb_s:.1f}s ({tb_s / ta_s:.0f}x)", flush=True)

    import _kt_double as KD
    GI = KD.kerr_chi_pieces()
    L, _, _ = MM.denominator(GI[0])
    H0 = KD.hamiltonian(GI[0])
    for rank, sample in ((2, 100 if quick else 300), (3, None)):
        den = L ** 6
        _, prods, _ = EX.generators(GI[0], rank, den)
        bx, by = EX.reducible_box(prods, den)
        mons = K.monomials(rank)
        cols, F_cos = PB.coefficient_basis(mons, bx + 6, by + 6, den)
        if sample:
            idx = random.Random(rank).sample(range(len(F_cos)), sample)
            specs = [(H0, F_cos[j]) for j in idx]
            what = f"{sample} random operator columns"
        else:
            specs = []
            for mi in range(len(mons)):
                for (a, b) in ((0, 0), (1, 0), (0, 1)):
                    F = [sp.Integer(0)] * len(mons)
                    F[mi] = x**a * y**b / den
                    specs.append((H0, F))
            what = f"all {len(specs)} template brackets"
        raws, dens = PB.build_columns(specs, mons, False)
        D = sp.Integer(1)
        for d_ in dens:
            D = sp.lcm(D, d_)
        ta_s = tb_s = 0
        nbad = 0
        for r in raws:
            g, ta, tb = same(r, D, p, "")
            nbad += not g; ta_s += ta; tb_s += tb
        print(f"  rank {rank} operator, {what}: {nbad} differing   "
              f"ring {ta_s:.1f}s vs expr {tb_s:.1f}s ({tb_s / max(ta_s, 1e-9):.0f}x)", flush=True)

    z_ok = PB.clear(sp.Integer(0), x**2, p) == {} == PB.clear_expr(sp.Integer(0), x**2, p)
    e1 = (x * y + 3) / (x * (x - 2))
    nc = raises(PB.clear, e1, x, p) and raises(PB.clear_expr, e1, x, p)
    e2 = sp.Rational(6, 7) * x / (x - 2)
    ni = raises(PB.clear, e2, x - 2, p) and raises(PB.clear_expr, e2, x - 2, p)
    print(f"  edge cases: zero -> empty {z_ok}   D not clearing raises {nc}   "
          f"non-integer coefficient raises {ni}")
    ok &= z_ok and nc and ni
    print("\n  " + ("VALIDATED: ring clear() is identical to clear_expr() and fails where it fails."
                    if ok else "FAILED"))
    sys.exit(0 if ok else 1)
