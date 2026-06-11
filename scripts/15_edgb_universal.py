#!/usr/bin/env python3
"""Step 15 — the UNIVERSAL EdGB formula attempt (pre-registered).

Protocol (registered before running — see journal):
  1. Build numerical truth at p=0.7 FIRST and seal it (holdout — used in
     no fit, touched only by the final scoring).
  2. Structure selection on TRAINING p ∈ {0.1, 0.3, 0.5} only:
       S1: A = 1 − a1(1−x)²/(a2+a3x),  B = 1 − b1(1−x)⁴/(b2+b3x)
       S2: A = 1 + a1(1−x) /(a2+a3x),  B = 1 + b1(1−x)²/(b2+b3x)
     (S1 = the p=0.3 evolved shape; S2 = the p=0.5 evolved motifs with
     A(1)=B(1)=1 — asymptotic flatness — enforced by construction.)
     Constants fitted per p by multi-restart hill-climb (the single-run
     hill-climb measured weak: continuation run REGRESSED 0.23→0.46%).
  3. For the winning structure: fit each constant as a function of p —
     primary: quadratic through the 3 training points (interpolation;
     the literature's own coefficients are rational in p); secondary:
     linear least squares. Assemble the universal formula.
  4. Score on the SEALED p=0.7. Pass = max deviation < 1%.

Run:  .venv/bin/python scripts/15_edgb_universal.py
"""

import importlib.util
import json
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


m11 = _load("edgb_shoot", "11_edgb_shoot.py")
m12 = _load("edgb_fit", "12_edgb_fit.py")
m13 = _load("edgb_hunt", "13_edgb_hunt.py")

HOLDOUT_PATH = os.path.join(_here, "..", "edgb_truth_holdout.json")
P_TRAIN = (0.1, 0.3, 0.5)
P_HOLD = 0.7
X = sp.Symbol("x", real=True)

# NORMALIZED structures (denominator constant ≡ 1): a1/(a2+a3x) is
# invariant under joint rescaling — the constant-space gauge of D16, at
# it again. Without normalization each restart lands in a random gauge
# and constants-vs-p interpolation is garbage (measured: a1 jumped
# 0.20 → 2.27 → 1.29 across p). True dof: 2 per function.
S1 = ("S1", lambda a: 1 - a[0] * (1 - X)**2 / (1 + a[1] * X),
      lambda b: 1 - b[0] * (1 - X)**4 / (1 + b[1] * X))
S2 = ("S2", lambda a: 1 + a[0] * (1 - X) / (1 + a[1] * X),
      lambda b: 1 + b[0] * (1 - X)**2 / (1 + b[1] * X))
N_CONSTS = 4


def build_holdout():
    if os.path.exists(HOLDOUT_PATH):
        with open(HOLDOUT_PATH) as fh:
            return json.load(fh)
    print(f"   sealing holdout truth at p={P_HOLD}...")
    f_g2, f_p2, f_y, *_ = m11.build_rhs(verbose=False)
    rec = []
    M, D, ok = m11.shoot(f_g2, f_p2, P_HOLD, record=rec)
    assert ok is True, f"holdout shoot failed: {ok}"
    Gacc_inf, r_inf = rec[-1][4], rec[-1][0]
    norm = 1 - 2 * M / r_inf
    rows = []
    for (rv, phi, p1, gp, gacc) in rec:
        if rv > m12.R_FIT_MAX or rv < 1.0001:
            continue
        eG = math.exp(gacc - Gacc_inf) * norm
        eL = f_y(rv, phi, p1, gp)
        A = eG / (1 - 1.0 / rv)
        B = math.sqrt(max(eG * eL, 0.0))
        rows.append([rv, A, B, phi])
    hold = {"M": M, "D": D, "rows": rows}
    with open(HOLDOUT_PATH, "w") as fh:
        json.dump(hold, fh)
    print(f"   holdout sealed: M={M:.6f}, D={D:.4f}, {len(rows)} rows")
    return hold


def fams(struct, consts):
    _, fa, fb = struct
    A = fa(consts[:2])
    B = fb(consts[2:])
    return (sp.lambdify(X, A, modules="math"),
            sp.lambdify(X, B, modules="math"))


def fit_structure(struct, entry, restarts=6, rounds=8000, seed=0):
    """Multi-restart hill-climb of the 4 constants on one truth table."""
    score_pair = m13.make_scorer(entry)
    best_v, best_s = None, float("inf")
    for k in range(restarts):
        rng = random.Random(seed * 100 + k)
        vals = [rng.uniform(-1, 1), rng.uniform(-4, 8),
                rng.uniform(-1, 1), rng.uniform(-4, 8)]
        s = score_pair(*fams(struct, vals))
        scale = 0.6
        for i in range(rounds):
            j = rng.randrange(N_CONSTS)
            trial = list(vals)
            trial[j] = vals[j] * (1 + scale * (rng.random() - 0.5)) \
                + 0.05 * scale * (rng.random() - 0.5)
            s2 = score_pair(*fams(struct, trial))
            if s2 < s:
                s, vals = s2, trial
            else:
                scale = max(scale * 0.9995, 0.02)
        if s < best_s:
            best_s, best_v = s, vals
    return best_v, best_s


def main():
    hold = build_holdout()          # SEALED — touched again only at step 4
    truth = m12.build_truth()

    print("\n== structure selection on training p only ==")
    fits = {}
    for struct in (S1, S2):
        name = struct[0]
        per_p = {}
        worst = 0.0
        for p in P_TRAIN:
            vals, s = fit_structure(struct, truth[str(p)],
                                    seed=int(p * 1000))
            per_p[p] = (vals, s)
            worst = max(worst, s)
            print(f"   {name} p={p}: {s:.4%}  "
                  + ", ".join(f"{v:+.3f}" for v in vals))
        fits[name] = (per_p, worst)
    winner = min(fits, key=lambda n: fits[n][1])
    print(f"   → winner: {winner} (worst training score "
          f"{fits[winner][1]:.4%})")
    struct = S1 if winner == "S1" else S2
    per_p = fits[winner][0]

    print("\n== constants as functions of p ==")
    ps = list(P_TRAIN)
    universal_quad, universal_lin = [], []
    for i in range(N_CONSTS):
        ys = [per_p[p][0][i] for p in ps]
        # quadratic through 3 points (exact interpolation)
        Mq = [[1, p, p * p] for p in ps]
        det = (Mq[0][0] * (Mq[1][1] * Mq[2][2] - Mq[1][2] * Mq[2][1])
               - Mq[0][1] * (Mq[1][0] * Mq[2][2] - Mq[1][2] * Mq[2][0])
               + Mq[0][2] * (Mq[1][0] * Mq[2][1] - Mq[1][1] * Mq[2][0]))
        if abs(det) < 1e-12:
            universal_quad.append((ys[1], 0, 0))
        else:
            import itertools
            def solve3(Mtx, rhs):
                import copy
                out = []
                for col in range(3):
                    Mc = [row[:] for row in Mtx]
                    for r_ in range(3):
                        Mc[r_][col] = rhs[r_]
                    d = (Mc[0][0] * (Mc[1][1] * Mc[2][2] - Mc[1][2] * Mc[2][1])
                         - Mc[0][1] * (Mc[1][0] * Mc[2][2] - Mc[1][2] * Mc[2][0])
                         + Mc[0][2] * (Mc[1][0] * Mc[2][1] - Mc[1][1] * Mc[2][0]))
                    out.append(d / det)
                return out
            universal_quad.append(tuple(solve3(Mq, ys)))
        # linear least squares
        n = len(ps)
        sx, sy = sum(ps), sum(ys)
        sxx = sum(p * p for p in ps)
        sxy = sum(p * y for p, y in zip(ps, ys))
        beta = (n * sxy - sx * sy) / (n * sxx - sx * sx)
        alpha = (sy - beta * sx) / n
        universal_lin.append((alpha, beta, 0.0))
        print(f"   c{i + 1}(p): quad {universal_quad[-1][0]:+.3f} "
              f"{universal_quad[-1][1]:+.3f}p {universal_quad[-1][2]:+.3f}p² "
              f"| lin {alpha:+.3f} {beta:+.3f}p")

    print(f"\n== SEALED HOLDOUT: p={P_HOLD} ==")
    score_hold = m13.make_scorer(hold)
    verdicts = []
    for label, uni in (("quadratic", universal_quad),
                       ("linear", universal_lin)):
        consts = [c0 + c1 * P_HOLD + c2 * P_HOLD**2 for c0, c1, c2 in uni]
        s = score_hold(*fams(struct, consts))
        verdicts.append((label, s))
        print(f"   universal-{label} at p={P_HOLD}: {s:.4%} "
              f"({'PASS <1%' if s < 0.01 else 'FAIL'})")

    best = min(verdicts, key=lambda v: v[1])
    print(f"\nUNIVERSAL FORMULA VERDICT: {winner}/{best[0]} scores "
          f"{best[1]:.4%} on the sealed p={P_HOLD} "
          f"{'✅ GENERALIZES' if best[1] < 0.01 else '❌ does not generalize — honest null, refine next'}")
    return 0 if best[1] < 0.01 else 1


if __name__ == "__main__":
    raise SystemExit(main())
