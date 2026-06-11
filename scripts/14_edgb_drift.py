#!/usr/bin/env python3
"""Step 14 — constants-drift study: one structure across the EdGB family.

Track B's p=0.3 hunt found a T2-band form (0.23%); per-p re-evolution is
seed-lottery (measured: at p=0.1 the parsimony tax beat structure and two
flat constants "won"). The clean experiment: FIX the winning structure,
re-polish only its constants at each p, and watch them drift. Smooth,
monotone drift ⇒ the constants are functions of p ⇒ a universal
p-parametrized closed form (the real prize) is one fit away.

Structure under test (from the p=0.3 hunt, gen ~900):
    A(x) = 1 − a1·(1−x)² / (a2 + a3·x)
    B(x) = 1 − b1·(1−x)⁴ / (b2 + b3·x)

Run:  .venv/bin/python scripts/14_edgb_drift.py
"""

import importlib.util
import math
import os
import random

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(_here, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m12 = _load("edgb_fit", "12_edgb_fit.py")
m13 = _load("edgb_hunt", "13_edgb_hunt.py")

X = sp.Symbol("x", real=True)


def family(consts):
    a1, a2, a3, b1, b2, b3 = consts
    A = 1 - a1 * (1 - X)**2 / (a2 + a3 * X)
    B = 1 - b1 * (1 - X)**4 / (b2 + b3 * X)
    return (sp.lambdify(X, A, modules="math"),
            sp.lambdify(X, B, modules="math"))


def polish_consts(entry, consts0, rounds=4000, seed=0):
    """Hill-climb the six constants against one truth table."""
    score_pair = m13.make_scorer(entry)
    rng = random.Random(seed)
    vals = list(consts0)
    best = score_pair(*family(vals))
    scale = 0.5
    for i in range(rounds):
        j = rng.randrange(len(vals))
        trial = list(vals)
        trial[j] = vals[j] * (1 + scale * (rng.random() - 0.5)) \
            + 0.02 * scale * (rng.random() - 0.5)
        s = score_pair(*family(trial))
        if s < best:
            best, vals = s, trial
        else:
            scale = max(scale * 0.999, 0.02)
    return vals, best


def main():
    truth = m12.build_truth()
    start = [0.86, 10.5, -2.83, 0.86, 10.6, 18.9]  # p=0.3 hunt values
    print("structure: A = 1 − a1(1−x)²/(a2+a3x),  "
          "B = 1 − b1(1−x)⁴/(b2+b3x)")
    print(f"{'p':>5} {'score':>9}  a1, a2, a3 | b1, b2, b3")
    rows = []
    for p in (0.1, 0.3, 0.5):
        # continuation: each p starts from the previous p's fit (first
        # pass had b3 frozen at p=0.5 — under-converged from a far start)
        vals, s = polish_consts(truth[str(p)], start, rounds=12000,
                                seed=int(p * 100))
        start = vals
        rows.append((p, s, vals))
        print(f"{p:>5} {s:>9.4%}  "
              + ", ".join(f"{v:+.4f}" for v in vals[:3]) + " | "
              + ", ".join(f"{v:+.4f}" for v in vals[3:]))
    ok = all(s < 0.01 for _, s, _ in rows)
    print(f"\n{'structure TRANSFERS across p (all <1%) ✅' if ok else 'structure does NOT transfer everywhere — record honestly ❌'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
