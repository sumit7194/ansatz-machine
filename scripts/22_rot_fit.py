#!/usr/bin/env python3
"""Step 22 — v5 R2: slow-rotating EdGB frame-dragging universal fit.

Systematic search over structures and p-dependent parameterizations:
  - Structures:
      R1: H(x) = 1 + (1-x)^2 * (a1 + a2*x) / (1 + a3*x)
      R3: H(x) = 1 + (1-x)^2 * a1 / (1 + a2*x)
  - Parameterizations of a_i(p) (corrections vanish linearly in p):
      1 coeff:  c1*p
      2 coeffs: c1*p + c2*p^2
      3 coeffs: c1*p + c2*p^2 + c3*p^3

Protocol (repaired 2026-06-12 — criteria-integrity disclosure):
  An earlier version selected the winning combination by HOLDOUT error
  across the printed grid — model selection on the sealed holdout, the
  post-hoc sin this project's rules forbid. The p=0.7 holdout is
  therefore PARTIALLY CONSUMED (it also saw at least one structure
  iteration, the p^1 scaling fix). Repair, pre-registered before any
  re-run:
    1. The winner is selected by TRAINING error only; per-combination
       holdout numbers are never computed during selection.
    2. The frozen winner is scored ONCE on the p=0.7 holdout
       (disclosed as consumed) and ONCE on a FRESH sealed p=0.75
       holdout built before any fitting and used in nothing else.
    3. Gate: both holdout errors < 1%. Fallback only if the p=0.75
       background shoot itself fails: p=0.65, disclosed.
"""

import importlib.util
import json
import math
import os
import random
import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))

# Import slow-rotation shooting code
_spec = importlib.util.spec_from_file_location(
    "rot_shoot", os.path.join(_here, "20_rot_shoot.py"))
m20 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m20)

HOLDOUT_PATH = os.path.join(_here, "..", "rot_truth_holdout.json")
HOLDOUT2_PATH = os.path.join(_here, "..", "rot_truth_holdout2.json")
P_TRAIN = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
P_HOLD = 0.7
P_HOLD2 = 0.75
R_FIT_MAX = 50.0


def generate_profile(p, subsample=True):
    M, rows = m20.background(p)
    rs, om = m20.omega_profile(rows, kc=1.0)
    J = m20.J_from_tail(rs, om)
    assert not math.isnan(J), f"failed to read J for p={p}"
    
    profile_data = []
    for i, rv in enumerate(rs):
        if rv < 1.0001 or rv > R_FIT_MAX:
            continue
        x = 1.0 - 1.0 / rv
        y = om[i] * rv**3 / (2.0 * J)
        profile_data.append((x, y))
    if subsample:
        profile_data = profile_data[::15]
    return M, J, profile_data


def build_and_seal_holdout(path, p_hold, force=False):
    if os.path.exists(path) and not force:
        with open(path) as fh:
            return json.load(fh)

    print(f"Sealing holdout truth at p={p_hold}...")
    M, J, profile = generate_profile(p_hold, subsample=False)
    holdout = {
        "p": p_hold,
        "M": M,
        "J": J,
        "profile": profile
    }
    with open(path, "w") as fh:
        json.dump(holdout, fh)
    return holdout


# Scorers
def make_scorer_R1(profile_data):
    x_vals = [pt[0] for pt in profile_data]
    y_vals = [pt[1] for pt in profile_data]
    def score_R1(a):
        a1, a2, a3 = a
        worst = 0.0
        for x, y in zip(x_vals, y_vals):
            denom = 1.0 + a3 * x
            if abs(denom) < 1e-9:
                return float("inf")
            h = 1.0 + (1.0 - x)**2 * (a1 + a2 * x) / denom
            dev = abs(h / y - 1.0)
            if dev > worst:
                worst = dev
        return worst
    return score_R1


def make_scorer_R3(profile_data):
    x_vals = [pt[0] for pt in profile_data]
    y_vals = [pt[1] for pt in profile_data]
    def score_R3(a):
        a1, a2 = a
        worst = 0.0
        for x, y in zip(x_vals, y_vals):
            denom = 1.0 + a2 * x
            if abs(denom) < 1e-9:
                return float("inf")
            h = 1.0 + (1.0 - x)**2 * a1 / denom
            dev = abs(h / y - 1.0)
            if dev > worst:
                worst = dev
        return worst
    return score_R3


def fit_profile(scorer, num_params, restarts=4, rounds=3000, seed=0, is_rational=True):
    rng = random.Random(seed)
    best_score = float("inf")
    best_params = None
    
    for r in range(restarts):
        params = [rng.uniform(-1.0, 1.0) for _ in range(num_params)]
        if is_rational and params[-1] <= -0.99:
            params[-1] = rng.uniform(-0.5, 1.0)
            
        score = scorer(params)
        scale = 0.5
        
        for i in range(rounds):
            j = rng.randrange(num_params)
            trial = list(params)
            trial[j] = params[j] * (1.0 + scale * (rng.random() - 0.5)) + 0.02 * scale * (rng.random() - 0.5)
            
            if is_rational and j == (num_params - 1) and trial[-1] <= -0.99:
                continue
                
            s = scorer(trial)
            if s < score:
                score, params = s, trial
            else:
                scale = max(scale * 0.9996, 0.005)
                
        if score < best_score:
            best_score, best_params = score, params
            
    return best_params, best_score


def eval_universal(x, p, uni_coeffs, is_r1):
    a = []
    for coeffs in uni_coeffs:
        val = 0.0
        if len(coeffs) >= 1:
            val += coeffs[0] * p**1
        if len(coeffs) >= 2:
            val += coeffs[1] * p**2
        if len(coeffs) >= 3:
            val += coeffs[2] * p**3
        a.append(val)
        
    if is_r1:
        denom = 1.0 + a[2] * x
        if denom <= 0.0:
            return float("inf")
        return 1.0 + (1.0 - x)**2 * (a[0] + a[1] * x) / denom
    else:
        denom = 1.0 + a[1] * x
        if denom <= 0.0:
            return float("inf")
        return 1.0 + (1.0 - x)**2 * a[0] / denom


def make_global_scorer(train_profiles, is_r1, num_coeffs_per_a):
    data = []
    for p, profile in train_profiles.items():
        x_vals = [pt[0] for pt in profile]
        y_vals = [pt[1] for pt in profile]
        data.append((p, x_vals, y_vals))
        
    num_a = 3 if is_r1 else 2
    
    def score_global(c_vals):
        uni = [c_vals[i*num_coeffs_per_a : (i+1)*num_coeffs_per_a] for i in range(num_a)]
        worst = 0.0
        for p, x_vals, y_vals in data:
            a = []
            for coeffs in uni:
                val = 0.0
                if num_coeffs_per_a >= 1:
                    val += coeffs[0] * p**1
                if num_coeffs_per_a >= 2:
                    val += coeffs[1] * p**2
                if num_coeffs_per_a >= 3:
                    val += coeffs[2] * p**3
                a.append(val)
                
            if is_r1:
                a1, a2, a3 = a
                for x, y in zip(x_vals, y_vals):
                    denom = 1.0 + a3 * x
                    if denom <= 0.01:
                        return float("inf")
                    h = 1.0 + (1.0 - x)**2 * (a1 + a2 * x) / denom
                    dev = abs(h / y - 1.0)
                    if dev > worst:
                        worst = dev
            else:
                a1, a2 = a
                for x, y in zip(x_vals, y_vals):
                    denom = 1.0 + a2 * x
                    if denom <= 0.01:
                        return float("inf")
                    h = 1.0 + (1.0 - x)**2 * a1 / denom
                    dev = abs(h / y - 1.0)
                    if dev > worst:
                        worst = dev
        return worst
    return score_global


def fit_global(scorer, num_c, init_params, restarts=10, rounds=10000, seed=0):
    rng = random.Random(seed)
    best_score = scorer(init_params)
    best_params = list(init_params)
    
    for r in range(restarts):
        if r == 0:
            params = list(best_params)
        else:
            params = [v * (1.0 + 0.3 * (rng.random() - 0.5)) + 0.05 * (rng.random() - 0.5) for v in best_params]
            
        score = scorer(params)
        if score == float("inf"):
            continue
            
        scale = 0.5
        for i in range(rounds):
            j = rng.randrange(num_c)
            trial = list(params)
            trial[j] = params[j] * (1.0 + scale * (rng.random() - 0.5)) + 0.02 * scale * (rng.random() - 0.5)
            s = scorer(trial)
            if s < score:
                score, params = s, trial
            else:
                scale = max(scale * 0.9996, 0.005)
                
        if score < best_score:
            best_score, best_params = score, params
            
    return best_params, best_score


def solve_least_squares(p_vals, y_vals, num_coeffs):
    if num_coeffs == 1:
        X_mat = sp.Matrix([[p**1] for p in p_vals])
    elif num_coeffs == 2:
        X_mat = sp.Matrix([[p**1, p**2] for p in p_vals])
    else:
        X_mat = sp.Matrix([[p**1, p**2, p**3] for p in p_vals])
        
    Y_mat = sp.Matrix(y_vals)
    C = (X_mat.T * X_mat).inv() * X_mat.T * Y_mat
    return [float(val) for val in C]


def score_holdout(holdout, uni_coeffs, is_r1):
    try:
        return max(abs(eval_universal(x, holdout["p"], uni_coeffs, is_r1) / y - 1.0)
                   for x, y in holdout["profile"])
    except Exception:
        return float("inf")


def main():
    # Seal BOTH holdouts before any fitting. Neither is consulted again
    # until the winner is frozen.
    holdout = build_and_seal_holdout(HOLDOUT_PATH, P_HOLD)
    holdout2 = build_and_seal_holdout(HOLDOUT2_PATH, P_HOLD2)

    print("\nGenerating training data and fitting structures per p...")
    train_profiles = {}
    for p in P_TRAIN:
        _, _, profile = generate_profile(p)
        train_profiles[p] = profile
        
    fits_R1, fits_R3 = {}, {}
    for p in P_TRAIN:
        profile = train_profiles[p]
        fits_R1[p] = fit_profile(make_scorer_R1(profile), 3, seed=int(p * 1000), is_rational=True)[0]
        fits_R3[p] = fit_profile(make_scorer_R3(profile), 2, seed=int(p * 1000), is_rational=True)[0]

    # Grid search combinations
    combinations = [
        # (structure_name, is_r1, num_coeffs_per_a)
        ("R1 (3-param Rational)", True, 1),
        ("R1 (3-param Rational)", True, 2),
        ("R1 (3-param Rational)", True, 3),
        ("R3 (2-param Rational)", False, 1),
        ("R3 (2-param Rational)", False, 2),
        ("R3 (2-param Rational)", False, 3),
    ]
    
    results = []
    
    for name, is_r1, num_coeffs in combinations:
        print(f"\n--- Fitting {name} with {num_coeffs} coefficients per parameter ---")
        
        # 1. Least squares guess
        uni_ls = []
        num_a = 3 if is_r1 else 2
        fits_map = fits_R1 if is_r1 else fits_R3
        
        for i in range(num_a):
            y_vals = [fits_map[p][i] for p in P_TRAIN]
            uni_ls.append(solve_least_squares(P_TRAIN, y_vals, num_coeffs))
            
        flat_ls = []
        for coeffs in uni_ls:
            flat_ls += coeffs
            
        # 2. Global hill climb
        scorer_global = make_global_scorer(train_profiles, is_r1, num_coeffs)
        best_c, global_score = fit_global(scorer_global, num_a * num_coeffs, flat_ls, seed=42)
        
        uni_coeffs = [best_c[i*num_coeffs : (i+1)*num_coeffs] for i in range(num_a)]

        # Holdouts are NOT scored here — selection sees training error only.
        print(f"  Training max error: {global_score:.4%}")

        results.append({
            "name": name,
            "is_r1": is_r1,
            "num_coeffs": num_coeffs,
            "coeffs": uni_coeffs,
            "train_err": global_score
        })

    # Select the winner on TRAINING error alone (pre-registered repair).
    results_valid = [r for r in results if math.isfinite(r["train_err"])]
    best = min(results_valid, key=lambda x: x["train_err"])

    print("\n========================================================")
    print("GRID SEARCH RESULTS SUMMARY (training error only)")
    print("========================================================")
    for r in results:
        print(f"  {r['name']} ({r['num_coeffs']} coeffs/a): train={r['train_err']:.4%}")

    # Frozen winner: score each sealed holdout exactly once.
    holdout_err = score_holdout(holdout, best["coeffs"], best["is_r1"])
    holdout2_err = score_holdout(holdout2, best["coeffs"], best["is_r1"])

    print("\n========================================================")
    print(f"WINNING COMBINATION (by training error): {best['name']} ({best['num_coeffs']} coeffs/a)")
    print("========================================================")
    print(f"  Training maximum relative error:          {best['train_err']:.4%}")
    print(f"  Holdout p={P_HOLD} (disclosed: consumed):    {holdout_err:.4%}")
    print(f"  Holdout p={P_HOLD2} (fresh, sealed, scored once): {holdout2_err:.4%}")
    print(f"  Formula details:")
    
    win_coeffs = best["coeffs"]
    if best["is_r1"]:
        print("    H(x, p) = 1 + (1 - x)^2 * (a1 + a2 * x) / (1 + a3 * x)")
        for i in range(3):
            terms = [f"({win_coeffs[i][k]:+.6f})*p**{k+1}" for k in range(best["num_coeffs"])]
            print(f"      a{i+1}(p) = " + " + ".join(terms))
    else:
        print("    H(x, p) = 1 + (1 - x)^2 * a1 / (1 + a2 * x)")
        for i in range(2):
            terms = [f"({win_coeffs[i][k]:+.6f})*p**{k+1}" for k in range(best["num_coeffs"])]
            print(f"      a{i+1}(p) = " + " + ".join(terms))
            
    success = holdout_err < 0.01 and holdout2_err < 0.01
    print(f"\nVERDICT: {'ALL GREEN ✅ Universal fit generalizes below 1.0% on both sealed holdouts!' if success else 'FAILURES ❌ Fit does not generalize below 1.0% on both holdouts'}")

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
