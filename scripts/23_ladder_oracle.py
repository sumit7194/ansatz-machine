#!/usr/bin/env python3
"""Step 23 — the LADDER ORACLE: prove the ladder, don't search it.

Plain idea: every static-vacuum rung the machine has ever conquered fits
one pattern —

    f(r) = 1 − c/r^(n−3) − 2Λ r² / ((n−1)(n−2))

(the Tangherlini family: the higher-dimensional Schwarzschild black
hole, with the cosmological term when Λ ≠ 0). Hunting each rung with
genetic search costs ~15 minutes; PROVING the predicted formula for a
rung costs seconds, using the same symbolic verifier — and the proof is
the same theorem the hunt would have produced. So: predict → prove →
grow the catalog. Searching is saved for rungs where the prediction
FAILS, which would be the genuinely interesting outcome.

This script walks 8+1 .. 12+1 × {Λ=0, Λ=−1, Λ=3/4} (the rungs the VM
high-ladder hunt was grinding through) and proves each one via
05_generalize.grow() — which re-derives the family with the mass
constant symbolic, i.e. a one-parameter theorem, and persists it to
the catalog. Idempotent: already-grown families are skipped.

Run:  .venv/bin/python scripts/23_ladder_oracle.py
"""

import importlib.util
import os
import time

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(_here, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen5 = _load("generalize", "05_generalize.py")
R = gen5.R_SYM

LAMS = ((sp.S.Zero, "Λ=0"), (sp.Integer(-1), "Λ<0"), (sp.Rational(3, 4), "Λ>0"))
N_RANGE = range(9, 14)  # 8+1 .. 12+1 total spacetime dimensions


def predicted_f(n, lam):
    """The oracle's prediction (instance with c = 1; grow() frees it)."""
    return 1 - 1 / R**(n - 3) - 2 * lam * R**2 / ((n - 1) * (n - 2))


def main():
    t0 = time.time()
    ok_all = True
    proved = 0
    done = {(e["n"], e["Lambda"]) for e in gen5.load_discoveries()}
    for n in N_RANGE:
        for lam, tag in LAMS:
            label = f"{n - 1}+1, {tag}"
            if (n, sp.sstr(lam)) in done:
                print(f"  ✓ {label}: already proved (skipping)")
                proved += 1
                continue
            f_inst = sp.together(predicted_f(n, lam))
            t1 = time.time()
            entry = gen5.grow(f_inst, n, lam,
                              provenance=f"ladder oracle (predicted + "
                                         f"proved, 2026-06-12)",
                              verbose=False)
            ok = entry is not None and len(entry["params"]) == 1
            ok_all = ok_all and ok
            proved += ok
            print(f"  {'✅' if ok else '❌ PREDICTION FAILED — investigate!'}"
                  f" {label}: f = {sp.sstr(f_inst)}"
                  f"  ({time.time() - t1:.1f}s)")
    print(f"\noracle swept {len(N_RANGE) * len(LAMS)} rungs in "
          f"{time.time() - t0:.0f}s — {proved} one-parameter families "
          f"proved/confirmed, catalog now "
          f"{len(gen5.load_discoveries())} entries")
    print("LADDER ORACLE " + ("PASSED ✅" if ok_all else "HAS FAILURES ❌"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
