#!/usr/bin/env python3
"""Stress-test ONE deformation against the pole-order picture, from scratch.  (§141)

If Carter survives a deformation only as Q + eps*G with G carrying Q^m in its denominator, the first
polynomial power of Carter that survives is Q^(m+1). For §141's d3 (pole order 2) that predicts:
Carter dies at rank 2 (checked with a larger ansatz, both primes); Q^2 ALSO dies at rank 4 (one power of
Q cannot cancel a double pole -- a prediction the data could contradict); Q^3 survives at rank 6 on the
other prime. The deformation is rebuilt as one concrete metric in each run; nothing is reused.
Usage: _kt_pole_check.py [--rank6-prime 1]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

from _kt_carter_space import (arg, build_space, compatible_space, kernel_np, matmul_mod,  # noqa: E402
                              rank_np, rref_np, setup)
from _kt_q2_candidate import combine  # noqa: E402
from _kt_qpower import chain_to_products_fast, lsq_power  # noqa: E402
from _kt_rank4_rule import pair_tower  # noqa: E402

D3 = {"l2rr_5": 1, "l2ang_3": sp.Rational(100, 609), "l2ang_4": sp.Rational(25, 203),
      "l2ang_5": sp.Rational(321, 2030), "l2ang_6": sp.Rational(103, 174)}


def build(ctx, coef, kmax=6):
    names, gis, roles = build_space(ctx["GI"], kmax)
    slot = [(n, g) for n, g, r in zip(names, gis, roles) if r == "slot"]
    w = [sp.Rational(coef.get(n, 0)) for n, _ in slot]
    return combine([g for _, g in slot], w)


def breakdown_single(ctx, dgi):
    """Survivors of the one deformation, by leading power of Carter."""
    p = ctx["p"]
    T, pn = chain_to_products_fast(ctx, ctx["chains"], p)
    lp = np.array([lsq_power(n) for n in pn])
    alive, keys, V = pair_tower(ctx, ["d"], [dgi])
    if not alive:
        return None
    Kc, S = ctx["Kc"], V.shape[1]
    U = np.zeros((Kc, S), dtype=np.int64)
    for j, (k, a) in enumerate(keys):
        U[k, j] = 1
    ker = kernel_np(np.concatenate([U, V]).T, Kc + V.shape[0], p)
    G = rref_np(ker[:, :Kc], p)[0] if ker.shape[0] else np.zeros((0, Kc), np.int64)
    PG = matmul_mod(G, T, p)
    q = ctx["rank"] // 2
    r = [rank_np(PG[:, lp >= m], int((lp >= m).sum()), p) if (lp >= m).any() else 0 for m in range(q + 2)]
    return G.shape[0], {m: r[m] - r[m + 1] for m in range(q + 1)}


if __name__ == "__main__":
    t0 = time.time()
    for prime in (0, 1):
        ctx = setup(2, 8, 10, prime)
        W = compatible_space(ctx, ["d3"], [build(ctx, D3)])
        print(f"rank 2, L^8 box {ctx['dx']}x{ctx['dy']}, prime {prime}: Carter survives: {W.shape[0] == 1}  "
              f"(predicted False) [{time.time()-t0:.0f}s]", flush=True)
    for prime in (0, 1):
        ctx = setup(4, 7, 6, prime)
        print(f"rank 4, L^7, prime {prime}: survivors {breakdown_single(ctx, build(ctx, D3))}  "
              f"(predicted 9: {{0: 9, 1: 0, 2: 0}} -- Q^2 must DIE too) [{time.time()-t0:.0f}s]", flush=True)
    pr6 = arg("--rank6-prime", 1)
    ctx = setup(6, 8, 6, pr6)
    print(f"rank 6, L^8, prime {pr6}: survivors {breakdown_single(ctx, build(ctx, D3))}  "
          f"(predicted 17: {{0: 16, 1: 0, 2: 0, 3: 1}}) [{time.time()-t0:.0f}s]", flush=True)
    print(f"\n  total {time.time()-t0:.0f}s")
