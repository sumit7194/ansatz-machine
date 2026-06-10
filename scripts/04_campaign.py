#!/usr/bin/env python3
"""Step 04 — the CAMPAIGN: run the machine across the dimensional ladder.

Six rungs. The first four re-discover catalog physics (the machine must
keep passing its own injection test); the last two are aimed OUTSIDE
the catalog on purpose — vacuum families the fingerprint library has
never heard of. There the correct output is CANDIDATE_NEW: the full
discovery pathway, exercised end to end.

(Honesty note: the "new" hits are new to the MACHINE's catalog, not to
the literature — 6D Tangherlini and Tangherlini-AdS are known. The
point being demonstrated is the pipeline: propose → verify → classify →
escalate. Aiming at genuinely unmined ansatz families is the next
phase, and it needs exactly this machinery.)

Run:  .venv/bin/python scripts/04_campaign.py
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


def main():
    # frozen v1 regression: the MEMORYLESS machine. Rungs E/F must keep
    # coming out CANDIDATE_NEW here even after 05 grows the persistent
    # catalog — this campaign is the time capsule of first discovery.
    catalog = fp.build_catalog(include_discoveries=False)

    # (label, n, Λ, reject_csi, expected class, expected detail substring)
    # reject_csi=True on every rung where we hunt a MASS-BEARING
    # solution: the maximally-symmetric member (Minkowski/dS/AdS) is the
    # vacuum ground state, not a discovery. The one exception is 2+1:
    # no local degrees of freedom, so CSI is all that locally exists —
    # there the declared blind spot IS the result.
    rungs = [
        ("A. Schwarzschild rung (3+1, Λ=0)", 4, sp.S.Zero, True,
         fp.KNOWN_LIKELY, "Schwarzschild (3+1)"),
        ("B. BTZ rung (2+1, Λ=-1)", 3, sp.Integer(-1), False,
         fp.BLIND_SPOT, "CSI"),
        ("C. Tangherlini rung (4+1, Λ=0)", 5, sp.S.Zero, True,
         fp.KNOWN_LIKELY, "Tangherlini"),
        ("D. Λ-vacuum rung (3+1, Λ=3/4)", 4, sp.Rational(3, 4), True,
         fp.KNOWN_LIKELY, "Schwarzschild-de Sitter"),
        # ---- aimed OUTSIDE the catalog ----
        ("E. Uncharted: 5+1, Λ=0", 6, sp.S.Zero, True,
         fp.CANDIDATE_NEW, None),
        ("F. Uncharted: 4+1, Λ=-1", 5, sp.Integer(-1), True,
         fp.CANDIDATE_NEW, None),
    ]

    t0 = time.time()
    results = []
    for label, n, lam, rcsi, _, _ in rungs:
        results.append(rd.run_with_restarts(label, n, lam, catalog,
                                            seeds=(0, 1, 2, 3, 4, 5),
                                            reject_csi=rcsi))

    print("\n" + "=" * 72)
    print("CAMPAIGN SUMMARY")
    print("=" * 72)
    ok = True
    for (label, n, lam, rcsi, want_cls, want_sub), res in zip(rungs,
                                                              results):
        if res is None:
            print(f"  ❌ {label}: no exact hit (null result)")
            ok = False
            continue
        good = res["class"] == want_cls and (
            want_sub is None or want_sub in res["class_detail"])
        mark = "✅" if good else "❌"
        ok = ok and good
        print(f"  {mark} {label}")
        print(f"       f(r) = {res['f']}   "
              f"[gen {res['gen']}, {res['time']:.1f}s]")
        print(f"       VERIFY: {res['verdict']}   NOVELTY: {res['class']}")
        print(f"       {res['class_detail']}")
    print(f"\ntotal campaign time {time.time() - t0:.1f}s")
    print("CAMPAIGN " + ("PASSED ✅" if ok else "HAS FAILURES ❌"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
