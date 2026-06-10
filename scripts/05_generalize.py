#!/usr/bin/env python3
"""Step 05 — catalog AUTO-GROWTH (the machine's memory).

v1 caveat, now closed: the machine had no memory. A CANDIDATE_NEW found
on Tuesday would be re-"discovered" on Wednesday. This module turns a
confirmed find into a permanent catalog entry:

    GENERALIZE   the GP find has specific rational constants
                 (f = 1 - (375/32)/r³). Replace each numeric constant
                 with a symbol, one at a time, and re-run the FULL
                 symbolic verifier. Constants whose symbolic version
                 still verifies are FREE PARAMETERS of a solution
                 family; constants that break verification are
                 structural (fixed by the field equations).
    RE-VERIFY    the family with all free parameters symbolic is
                 proved as a theorem (vacuum for ALL parameter values).
    APPEND       the family is written to catalog_discoveries.json;
                 02's build_catalog() loads it on every run, so the
                 fingerprint filter now recognizes the whole family —
                 the machine never rediscovers it again.

Note the physics this performs automatically: deciding which constants
in a solution are "hair" (free: mass) and which are law (fixed: the Λ
coefficient) is exactly the family-classification step a relativist
does by hand.

Battery: grow v1's two campaign finds (rungs E and F), then re-classify
the original numeric geometries — both must flip CANDIDATE_NEW →
KNOWN_LIKELY against the grown catalog.

Run:  .venv/bin/python scripts/05_generalize.py
"""

import importlib.util
import json
import os
import time

import sympy as sp

from gr_engine import (Geometry, verify, VERIFIED, R_SYM,
                       build_ansatz_metric)

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "fingerprints", os.path.join(_here, "02_fingerprints.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

CATALOG_PATH = os.path.join(_here, "..", "catalog_discoveries.json")


# ---------------------------------------------------------------------------
# Positional numeric-leaf surgery lives in finisher.py (shared with the
# snap machinery); re-exported here for callers using this module's API
# ---------------------------------------------------------------------------

import finisher  # noqa: E402
from finisher import numeric_slots, replace_slots  # noqa: E402


# ---------------------------------------------------------------------------
# Generalize + persist
# ---------------------------------------------------------------------------

def generalize(f_expr, n, Lambda, verbose=True):
    """Find which numeric constants of a verified f(r) are free
    parameters. Returns (family_expr, param_symbols) or None.

    Laurent-polynomial finds are generalized COEFFICIENT-wise, not tree-
    leaf-wise (bought by: the find -r²/8 + 1 + r⁻² has an IMPLICIT
    coefficient 1 on the mass term — no tree leaf exists for it, so
    slot-based generalization never tested the one constant that was
    actually free). Tree slots remain the fallback for pole structures."""
    lc = finisher._laurent_coeffs(f_expr)

    def test(cand, syms):
        metric, coords, _ = build_ansatz_metric(n, cand)
        verdict, _ = verify(metric, coords, params=syms, Lambda=Lambda)
        return verdict == VERIFIED

    if lc is not None:
        powers = sorted(lc)
        free = []
        for p in powers:
            sym = sp.Symbol("ctest", real=True)
            cand = sum((sym if q == p else v) * R_SYM**q
                       for q, v in lc.items())
            ok = test(cand, [sym])
            if verbose:
                print(f"     coefficient of r^{p} ({lc[p]}): "
                      f"{'FREE parameter' if ok else 'structural (fixed by field equations)'}")
            if ok:
                free.append(p)
        if not free:
            return None
        syms = [sp.Symbol(f"c{i + 1}", real=True)
                for i in range(len(free))]
        sub = dict(zip(free, syms))
        family = sum((sub.get(q, lc[q])) * R_SYM**q for q in powers)
        if len(free) > 1 and not test(family, syms):
            # independently free ≠ jointly free — keep the first only
            family = sum((syms[0] if q == free[0] else lc[q]) * R_SYM**q
                         for q in powers)
            syms = syms[:1]
        return family, syms

    # fallback: tree-slot generalization for non-Laurent structures
    slots = numeric_slots(f_expr)
    free = []
    for i, p in enumerate(slots):
        sym = sp.Symbol(f"c{len(free) + 1}", real=True)
        cand = replace_slots(f_expr, [p], [sym])
        ok = test(cand, [sym])
        if verbose:
            val = f_expr
            for j in p:
                val = val.args[j] if val.args else val
            print(f"     constant {sp.sstr(val)}: "
                  f"{'FREE parameter' if ok else 'structural (fixed by field equations)'}")
        if ok:
            free.append(p)
    if not free:
        return None
    syms = [sp.Symbol(f"c{i + 1}", real=True) for i in range(len(free))]
    family = replace_slots(f_expr, free, syms)
    if len(free) > 1 and not test(family, syms):
        family = replace_slots(f_expr, [free[0]], [syms[0]])
        syms = syms[:1]
    return family, syms


def load_discoveries(path=CATALOG_PATH):
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return json.load(fh)


def grow(f_expr, n, Lambda, provenance, path=CATALOG_PATH, verbose=True):
    """Generalize a confirmed find and append the family to the
    persistent catalog. Idempotent: an already-known family is skipped.
    Returns the entry dict, or None if nothing generalized."""
    out = generalize(f_expr, n, Lambda, verbose=verbose)
    if out is None:
        if verbose:
            print("     no free parameters found — isolated solution, "
                  "storing nothing (inspect manually)")
        return None
    family, syms = out
    entry = {
        "name": f"discovered: {n - 1}+1, Λ={sp.sstr(Lambda)}, "
                f"f = {sp.sstr(family)}",
        "n": n,
        "Lambda": sp.sstr(Lambda),
        "f": sp.sstr(family),
        "params": [s.name for s in syms],
        "provenance": provenance,
    }
    existing = load_discoveries(path)
    if any(e["n"] == entry["n"] and e["Lambda"] == entry["Lambda"]
           and e["f"] == entry["f"] for e in existing):
        if verbose:
            print(f"     family already in catalog: {entry['name']}")
        return entry
    existing.append(entry)
    with open(path, "w") as fh:
        json.dump(existing, fh, indent=2)
    if verbose:
        print(f"     📚 catalog grew: {entry['name']}")
    return entry


# ---------------------------------------------------------------------------
# Battery: grow v1's finds, then the machine must RECOGNIZE them
# ---------------------------------------------------------------------------

def main():
    results = []

    # v1 campaign finds (RESULTS.md, rungs E and F), exact expressions
    finds = [
        ("rung E find (6D black hole)",
         1 - sp.Rational(375, 32) / R_SYM**3, 6, sp.S.Zero,
         "campaign rung E (2026-06-10)"),
        ("rung F find (5D AdS black hole)",
         R_SYM**2 / 6 + 1 - sp.Rational(2, 3) / R_SYM**2, 5,
         sp.Integer(-1), "campaign rung F (2026-06-10)"),
    ]

    print("== GENERALIZE + GROW ==")
    for label, f_expr, n, lam, prov in finds:
        print(f"  {label}: f(r) = {sp.sstr(f_expr)}")
        t0 = time.time()
        entry = grow(f_expr, n, lam, prov)
        ok = entry is not None and len(entry["params"]) == 1
        results.append(ok)
        print(f"     {'✓' if ok else '✗✗ EXPECTATION FAILED'} "
              f"one-parameter family ({time.time() - t0:.1f}s)")

    print("\n== MEMORY TEST: the machine must now recognize its own finds ==")
    catalog = fp.build_catalog()  # loads catalog_discoveries.json
    for label, f_expr, n, lam, _ in finds:
        metric, coords, _ = build_ansatz_metric(n, f_expr)
        t0 = time.time()
        cls, detail = fp.classify(Geometry(metric, coords), catalog)
        ok = cls == fp.KNOWN_LIKELY and "discovered" in detail
        results.append(ok)
        print(f"  {'✓' if ok else '✗✗ EXPECTATION FAILED'} {label}: "
              f"{cls} — {detail} ({time.time() - t0:.1f}s)")

    print(f"\n{'ALL EXPECTATIONS MET ✅' if all(results) else 'EXPECTATION FAILURES ❌'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
