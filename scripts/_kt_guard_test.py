#!/usr/bin/env python3
"""Validate the Freivalds residual guard in BOTH directions.  (D54)

The guard protects every dimension this repo reports: if the returned vectors are not in the
nullspace, the nullity is fiction. Replacing an exhaustive check with a probabilistic one is
therefore only allowed with a control that can FAIL -- so this asserts, on exact GF(p) data:

  1. AGREEMENT. On a correct nullspace, 'full' and 'freivalds' both report zero bad rows.
  2. DETECTION. On a nullspace corrupted by ONE unit in ONE coordinate of ONE vector -- the
     smallest possible defect, and the one a sampling guard would be likeliest to miss --
     'freivalds' reports it, over many independent corruptions and probe seeds.
  3. NO FALSE ALARMS. The probe combination of a correct nullspace is itself exactly in the
     nullspace, which is the one-sided property the bound rests on.
  4. The bound is not being leaned on: a 1-probe guard is also tested, and must still detect.

Usage: .venv/bin/python scripts/_kt_guard_test.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

from _kt_carter_space import kernel_np  # noqa: E402
from _kt_coo import guard_vectors, residual_count  # noqa: E402

P = 2147483647


def case(seed, nrows=60, ncols=90, density=0.15):
    """A random sparse M over GF(p) and an exact basis of its nullspace."""
    rng = np.random.default_rng(seed)
    M = rng.integers(0, P, (nrows, ncols), dtype=np.int64)
    M[rng.random((nrows, ncols)) > density] = 0
    vecs = [v for v in kernel_np(M, ncols, P)]
    ri, ci = np.nonzero(M)
    return (ri.astype(np.int64), ci.astype(np.int64), M[ri, ci].astype(np.int64), nrows), vecs


def run(coo, vecs, mode):
    ri, ci, vi, nr = coo
    return residual_count(ri, ci, vi, nr, guard_vectors(vecs, P, mode=mode)[0], P)


if __name__ == "__main__":
    fails = []
    for seed in range(6):
        coo, vecs = case(seed)
        if not vecs:
            fails.append(f"seed {seed}: empty nullspace, nothing to test")
            continue

        # 1. agreement on a correct nullspace
        for mode in ("full", "freivalds", "freivalds:1"):
            bad = run(coo, vecs, mode)
            if bad:
                fails.append(f"seed {seed}: {mode} reported {bad} bad on a CORRECT nullspace")

        # 3. the probe vectors are themselves exactly in the nullspace (one-sidedness)
        probes, _ = guard_vectors(vecs, P, mode="freivalds:4")
        ri, ci, vi, nr = coo
        if residual_count(ri, ci, vi, nr, probes, P):
            fails.append(f"seed {seed}: probe combination is NOT in the nullspace")

        # 2 & 4. detection of the smallest possible corruption
        rng = np.random.default_rng(1000 + seed)
        for trial in range(25):
            bent = [np.array(v, dtype=np.int64) for v in vecs]
            i = int(rng.integers(0, len(bent)))
            j = int(rng.integers(0, bent[i].shape[0]))
            bent[i][j] = (bent[i][j] + 1) % P          # ONE unit, ONE coordinate
            if not run(coo, bent, "full"):
                fails.append(f"seed {seed} trial {trial}: FULL guard missed a corruption")
            for k in (1, 4):
                if not run(coo, bent, f"freivalds:{k}"):
                    fails.append(f"seed {seed} trial {trial}: freivalds:{k} MISSED vec {i} coord {j}")

        print(f"  seed {seed}: nullity {len(vecs)}, 25 corruptions, agreement + detection ok",
              flush=True)

    print()
    if fails:
        for f in fails[:20]:
            print("  FAIL:", f)
        raise SystemExit(f"GUARD VALIDATION FAILED ({len(fails)} problems)")
    print("  guard validation PASSED: agrees when correct, detects when broken, no false alarms")
