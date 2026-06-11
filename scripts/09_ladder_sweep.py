#!/usr/bin/env python3
"""Step 09 — the WIDE LADDER SWEEP: conquer the static vacuum territory.

Walks every (dimension, Λ-sign) rung of the static one-function ansatz
up to 7+1, growing the catalog mid-run (the 07 expedition machinery at
full width). With the algebraic finisher, rungs that took 50-150
generations now take 2-20 — so the whole ladder is one sitting.

Per-rung expectation is OUTCOME-agnostic but honesty-strict: a rung may
yield CANDIDATE_NEW (then it must grow a family) or recognize a known/
grown family (idempotent reruns, overlapping families) — but never a
false novelty, never an unverified claim, and 2+1 rungs must come out
BLIND_SPOT (no local dof, forever).

Run:  .venv/bin/python scripts/09_ladder_sweep.py
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


fp = _load("fingerprints", "02_fingerprints.py")
rd = _load("rediscover", "03_rediscover.py")
gen5 = _load("generalize", "05_generalize.py")

LAM_NEG, LAM_POS = sp.Integer(-1), sp.Rational(3, 4)


def main():
    t0 = time.time()
    # the full static-vacuum ladder, 2+1 through 7+1, three Λ sectors
    rungs = []
    for n in range(3, 9):
        for lam, tag in ((sp.S.Zero, "Λ=0"), (LAM_NEG, "Λ<0"),
                         (LAM_POS, "Λ>0")):
            if n == 3 and lam == sp.S.Zero:
                continue  # 2+1 Λ=0 vacuum is locally flat — nothing to hunt
            rungs.append((f"{n - 1}+1, {tag}", n, lam))

    results, grown, ok_all = [], 0, True
    for label, n, lam in rungs:
        catalog = fp.build_catalog()  # reload — includes growth so far
        reject = n > 3  # in 2+1 CSI is all that exists; elsewhere hunt mass
        res = rd.run_with_restarts(label, n, lam, catalog,
                                   seeds=(0, 1, 2, 3), reject_csi=reject,
                                   verbose=False)
        if res is None:
            print(f"  ❌ {label}: no exact hit (null result)")
            results.append((label, None))
            ok_all = False
            continue
        cls = res["class"]
        ok = True
        note = ""
        if cls == fp.CANDIDATE_NEW:
            entry = gen5.grow(res["f"], n, lam,
                              provenance=f"ladder sweep {label}",
                              verbose=False)
            ok = entry is not None
            grown += ok
            note = f"grew: {entry['name']}" if entry else \
                "GROWTH FAILED — isolated solution?"
        elif cls == fp.KNOWN_LIKELY:
            note = res["class_detail"][:60]
        elif cls == fp.BLIND_SPOT:
            ok = (n == 3)  # only 2+1 may be CSI here (reject_csi elsewhere)
            note = "CSI (correct: no local dof)" if ok else \
                "CSI on a mass rung — should not happen"
        ok_all = ok_all and ok
        print(f"  {'✅' if ok else '❌'} {label}: f(r) = {res['f']}"
              f"  → {cls}  [{note}] (gen {res['gen']}, {res['time']:.0f}s)")
        results.append((label, res))

    print(f"\nladder swept in {time.time() - t0:.0f}s — "
          f"{grown} new families grown, catalog now "
          f"{len(fp.build_catalog())} entries")
    print("LADDER SWEEP " + ("PASSED ✅" if ok_all else "HAS FAILURES ❌"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
