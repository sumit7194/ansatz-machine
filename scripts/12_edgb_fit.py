#!/usr/bin/env python3
"""Step 12 — v4 battery E2 + Track B foundation: the EdGB FIT VERIFIER.

A second verifier track (docs/EDGB.md): candidates are scored by maximum
relative deviation from the NUMERICAL EdGB metric (built by step 11's
E0/E1-validated shooting code), not by exact-zero field equations.

Ground truth tables are cached to edgb_truth.json: for each family
parameter p, samples of (r, e^Γ, e^Λ, φ) over the exterior
r ∈ [1.0001·r_h, 50·r_h], with e^Γ normalized to 1 at infinity through
the integrated Γ_acc and the measured M.

PRE-REGISTRATION AMENDMENT (honest change to docs/EDGB.md E2): the KKZ
published-fit comparison is DEFERRED — the research pass captured their
fit's STRUCTURE but not the full rational coefficient functions
(eqs. 24-28 of arXiv:1706.07460), so transcribing it tonight would mean
guessing. E2 tonight = the checks that need no transcription:
  E2a  self-consistency: the truth table re-scored against itself → 0.
  E2b  Schwarzschild with the SAME mass must score ≈ the known EdGB
       deviation scale (it must NOT score well — the verifier cannot be
       allowed to absorb the new physics; KKZ's own criterion).
  E2c  the deviation grows with p (more dilaton → more deviation).

Run:  .venv/bin/python scripts/12_edgb_fit.py
"""

import importlib.util
import json
import math
import os

import sympy as sp

from gr_engine import R_SYM

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "edgb_shoot", os.path.join(_here, "11_edgb_shoot.py"))
m11 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m11)

TRUTH_PATH = os.path.join(_here, "..", "edgb_truth.json")
P_SET = (0.1, 0.3, 0.5)
R_FIT_MAX = 50.0  # score over r/r_h ∈ [1.0001, 50]


def build_truth(force=False):
    """Numerical EdGB tables for each p in P_SET, cached to disk."""
    if os.path.exists(TRUTH_PATH) and not force:
        with open(TRUTH_PATH) as fh:
            return json.load(fh)
    print("   building numerical ground truth (one-time)...")
    f_g2, f_p2, f_y, *_ = m11.build_rhs(verbose=False)
    truth = {}
    for p in P_SET:
        rec = []
        M, D, ok = m11.shoot(f_g2, f_p2, p, record=rec)
        assert ok is True, f"shoot failed for p={p}: {ok}"
        Gacc_inf = rec[-1][4]
        r_inf = rec[-1][0]
        # e^Γ(r) = exp(Γacc − Γacc_inf)·(1 − 2M/r_inf)
        norm = (1 - 2 * M / r_inf)
        rows = []
        for (rv, phi, p1, gp, gacc) in rec:
            if rv > R_FIT_MAX or rv < 1.0001:
                continue
            eG = math.exp(gacc - Gacc_inf) * norm
            eL = f_y(rv, phi, p1, gp)
            # store the REGULAR RZ-style parts (KKZ compare these):
            # A = e^Γ/(1−r_h/r) — divides out the horizon zero;
            # B = e^{(Γ+Λ)/2}. Raw e^Γ relative error blows up ~100×
            # near the horizon (measured: Schwarzschild "deviated" 9847%)
            # and would drown the hunt's fitness signal in horizon noise.
            A = eG / (1 - 1.0 / rv)   # r_h = 1
            B = math.sqrt(max(eG * eL, 0.0))
            rows.append([rv, A, B, phi])
        truth[str(p)] = {"M": M, "D": D, "rows": rows}
        print(f"     p={p}: M={M:.6f}, D={D:.4f}, {len(rows)} samples")
    with open(TRUTH_PATH, "w") as fh:
        json.dump(truth, fh)
    return truth


def score(truth_entry, A_func, B_func=None):
    """Max relative deviation of the candidate's regular parts (A, B)
    from truth over the exterior."""
    worst = 0.0
    for rv, A, B, _ in truth_entry["rows"]:
        try:
            da = abs(A_func(rv) / A - 1)
            db = abs(B_func(rv) / B - 1) if B_func is not None else 0.0
        except Exception:
            return float("inf")
        # guard EACH part before any max — max(finite, nan) returns the
        # finite arg, so a post-max guard lets nan parts ride free
        if not (math.isfinite(da) and math.isfinite(db)):
            return float("inf")
        worst = max(worst, da, db)
    return worst


def main():
    results = []
    truth = build_truth()

    # E2a: truth scored against itself (interpolation-free: exact rows)
    for p in P_SET:
        ent = truth[str(p)]
        rows = {row[0]: row for row in ent["rows"]}
        s = score(ent, lambda rv: rows[rv][1], lambda rv: rows[rv][2])
        ok = s < 1e-12
        results.append(ok)
        print(f"  {'✓' if ok else '✗✗'} E2a p={p}: self-score = {s:.2e}")

    # E2b: the RZ-Schwarzschild (A≡1, B≡1 — horizon at r_h) must score
    # in the percent band: clearly nonzero (new physics not absorbed)
    # but sane (no horizon blowup)
    for p in P_SET:
        s = score(truth[str(p)], lambda rv: 1.0, lambda rv: 1.0)
        ok = 0.005 < s < 1.0
        results.append(ok)
        print(f"  {'✓' if ok else '✗✗'} E2b p={p}: RZ-Schwarzschild "
              f"scores {s:.2%} (must be in (0.5%, 100%))")

    # E2c: deviation grows with p
    devs = [score(truth[str(p)], lambda rv: 1.0, lambda rv: 1.0)
            for p in P_SET]
    ok = devs[0] < devs[1] < devs[2]
    results.append(ok)
    print(f"  {'✓' if ok else '✗✗'} E2c deviation monotone in p: "
          f"{['%.4f' % d for d in devs]}")

    print(f"\n{'ALL EXPECTATIONS MET ✅' if all(results) else 'EXPECTATION FAILURES ❌'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
