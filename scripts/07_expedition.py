#!/usr/bin/env python3
"""Step 07 — EXPEDITION mode: the self-extending hunt.

v2 closed the memory loop as separate steps (04 discover → 05 generalize).
This wires them together: the machine walks uncharted (dimension, Λ) rungs
and, on every confirmed CANDIDATE_NEW, generalizes the find and grows its
catalog MID-RUN. The last leg re-hunts a rung whose family was grown
earlier in the same expedition — with a different seed, so a different
specific solution is found — and must come out KNOWN_LIKELY. That is the
machine recognizing, live, a family it learned minutes earlier.

Rungs (uncharted by the base catalog and by each other):
    1. 6+1, Λ=0      → expect 7D Tangherlini  f = 1 - c/r⁴   → grow
    2. 4+1, Λ=3/4    → expect Tangherlini-dS  f = 1 - c/r² - r²/8 → grow
    3. 6+1, Λ=0 again (fresh seed) → must now be KNOWN_LIKELY (memory!)

Run:  .venv/bin/python scripts/07_expedition.py
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


def main():
    t0 = time.time()
    results = []

    # legs: (label, n, Λ, seeds, expected class, expected detail substring)
    legs = [
        # n = total spacetime dimensions: n=7 is 6+1 — the 5+1 rung is
        # already in the grown catalog from step 05, so it would be
        # KNOWN, not NEW
        ("Leg 1 — uncharted 6+1, Λ=0", 7, sp.S.Zero, (0, 1, 2, 3),
         fp.CANDIDATE_NEW, None),
        ("Leg 2 — uncharted 4+1, Λ=3/4", 5, sp.Rational(3, 4), (0, 1, 2, 3),
         fp.CANDIDATE_NEW, None),
        # different seeds on purpose: a DIFFERENT solution of the same
        # family must be found, and recognized via the grown catalog
        ("Leg 3 — memory replay: 6+1, Λ=0", 7, sp.S.Zero, (7, 8, 9),
         fp.KNOWN_LIKELY, "discovered"),
    ]

    for label, n, lam, seeds, want_cls, want_sub in legs:
        catalog = fp.build_catalog()  # reload: includes growth from prior legs
        res = rd.run_with_restarts(label, n, lam, catalog, seeds=seeds,
                                   reject_csi=True)
        if res is None:
            print(f"  ❌ {label}: no exact hit")
            results.append(False)
            continue
        # idempotency: on a re-run the catalog already remembers earlier
        # expeditions, so a discovery leg legitimately comes out
        # KNOWN_LIKELY[discovered] — that is the memory working, not a
        # failed discovery
        ok = (res["class"] == want_cls and (
              want_sub is None or want_sub in res["class_detail"])) \
            or (want_cls == fp.CANDIDATE_NEW
                and res["class"] == fp.KNOWN_LIKELY
                and "discovered" in res["class_detail"])
        if res["class"] == fp.CANDIDATE_NEW:
            print(f"   🌱 growing catalog from f(r) = {res['f']} ...")
            entry = gen5.grow(res["f"], n, lam,
                              provenance=f"expedition {label}")
            ok = ok and entry is not None
        results.append(ok)
        print(f"  {'✅' if ok else '❌ EXPECTATION FAILED'} {label}: "
              f"f(r) = {res['f']} → {res['class']}"
              + (f" [{res['class_detail'][:70]}]"
                 if res["class"] != fp.CANDIDATE_NEW else ""))

    print(f"\ntotal expedition time {time.time() - t0:.1f}s")
    print("EXPEDITION " + ("PASSED ✅" if all(results) else "FAILED ❌"))
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
