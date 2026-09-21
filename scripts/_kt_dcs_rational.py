#!/usr/bin/env python3
"""dCS step 5b: does dCS keep a RATIONAL Carter? The question nobody has asked.

THE LOGIC, and it is falsifiable against us rather than against them. §141-§142: a Carter surviving
as a rational first integral Q + eps K1/(2 Q^m) is invisible to every POLYNOMIAL Killing search, but
its powers Q^(m+1) DO reappear as polynomial tensors at rank 2(m+1). The pole order saturates at 2 in
every family mapped so far. So:

    pole order 1  ->  a survivor above the floor at RANK 4
    pole order 2  ->  a survivor above the floor at RANK 6
    no rational Carter  ->  the floor and nothing else at both

Owen-Yunes-Witek report no Killing tensor at ranks 4 or 6 for dCS. OUR OWN FRAMEWORK THEREFORE
PREDICTS THEIR NULL. A survivor here contradicts one of us and would be the more interesting result;
its absence confirms both, by methods sharing no code.

WHY THIS IS NOT THEIR LADDER REPEATED. They asked "is there a polynomial Killing tensor". We ask
"is there a rational first integral", and read the answer off the polynomial ladder using the
dictionary §141 established. Same computation, different question, and only the second one can
reconcile their null with Cardenas-Avendano's opposite chaos-based conjecture.

Repro:  .venv/bin/python scripts/_kt_dcs_rational.py --rank 4 [--denpow 7] [--margin 6] [--prime 0]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
from _kt_carter_space import arg, setup  # noqa: E402
from _kt_dcs_carter import dcs_h_lower, dcs_solution  # noqa: E402
from _kt_pole_check import breakdown_single  # noqa: E402

FLOOR = {2: 4, 4: 9, 6: 16}

if __name__ == "__main__":
    t0 = time.time()
    rank_ = arg("--rank", 4)
    denpow = arg("--denpow", 7 if rank_ == 4 else 8)
    margin = arg("--margin", 6)
    prime = arg("--prime", 0)
    print(f"dCS rational-Carter test at rank {rank_}\n", flush=True)
    fn = dcs_solution()
    h = dcs_h_lower(fn)
    ctx = setup(rank_, denpow, margin, prime)
    print(f"  rank {rank_}, L^{denpow}, box {ctx['dx']}x{ctx['dy']}, prime {prime}, "
          f"{ctx['Kc']} Kerr directions [{time.time()-t0:.0f}s]", flush=True)
    gi = KD.ginv_perturbation(ctx["GI"], h)
    res = breakdown_single(ctx, gi)
    print(f"\n  survivors, by leading power of Carter: {res}", flush=True)
    floor = FLOOR.get(rank_)
    if res is None:
        print("  NOTHING survives -- impossible: the reducible floor is exactly conserved.")
    else:
        tot, by_q = res
        above = tot - floor if floor else None
        print(f"\n  reducible floor at rank {rank_}: {floor}", flush=True)
        print(f"  total survivors: {tot}   ABOVE THE FLOOR: {above}", flush=True)
        if above == 0:
            print(f"\n  => the floor and nothing else. NO rational Carter of pole order "
                  f"{rank_//2 - 1} for dCS.", flush=True)
            print(f"     Consistent with Owen-Yunes-Witek's rank-{rank_} null, and with our own", flush=True)
            print(f"     §142 prediction that it would be.", flush=True)
        else:
            print(f"\n  => {above} DIRECTION(S) ABOVE THE FLOOR. Before calling this a rational", flush=True)
            print(f"     Carter, D52 applies: divide out powers of lower-rank integrals and check", flush=True)
            print(f"     the quotient solves the lower-rank equation. And it CONTRADICTS the", flush=True)
            print(f"     published rank-{rank_} null, so the metric and the box get rechecked first.", flush=True)
    print(f"\n  total {time.time()-t0:.0f}s")
