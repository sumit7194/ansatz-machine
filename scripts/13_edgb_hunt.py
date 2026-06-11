#!/usr/bin/env python3
"""Step 13 — Track B: the hunt for a closed-form EdGB metric fit.

The prize (docs/EDGB.md): the EdGB black hole has no closed form; the
published state of the art is KKZ's third-order continued fraction —
max relative error "a few tenths of one percent" with ~10 fitted
coefficients (arXiv:1706.07460). The hunt: GP over expression trees in
the compactified variable x ≡ 1 − r_h/r (RZ coordinate; x=0 horizon,
x→1 infinity), scoring candidates' regular parts (A, B) against step
12's numerical truth tables.

Tiered honest bars, per family parameter p:
    T1  ≤ 1.0%  with ≤ 6 constants   (compact and competitive)
    T2  ≤ 0.3%  with ≤ 8 constants   (matches KKZ with fewer knobs)
    T3  ≤ 0.1%                        (beats KKZ outright)
A fit is NOT a theorem — no symbolic verdict here; the verifier IS the
score. Constants are polished by float hill-climb (the fit analogue of
the algebraic finisher) and snapped back to small rationals when that
costs nothing.

Run:  .venv/bin/python scripts/13_edgb_hunt.py [--p 0.3] [--budget 300]
"""

import argparse
import importlib.util
import math
import os
import random
import time

import sympy as sp

from gr_engine import R_SYM

_here = os.path.dirname(os.path.abspath(__file__))


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(_here, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rd = _load("rediscover", "03_rediscover.py")
m12 = _load("edgb_fit", "12_edgb_fit.py")

X = R_SYM  # the GP variable is interpreted as x = 1 − r_h/r here


def tree_constants(tree, path=()):
    """(path, value) pairs of all Rational leaves."""
    out = []
    if tree[0] == "c":
        return [(path, tree[1])]
    if tree[0] == "powi":
        return tree_constants(tree[1], path + (1,))
    if tree[0] in rd.BIN_OPS:
        out += tree_constants(tree[1], path + (1,))
        out += tree_constants(tree[2], path + (2,))
    return out


def with_constants(tree, consts):
    """Replace constants by position with given values."""
    it = iter(consts)

    def rebuild(t):
        if t[0] == "c":
            return ("c", next(it))
        if t[0] == "powi":
            return ("powi", rebuild(t[1]), t[2])
        if t[0] in rd.BIN_OPS:
            return (t[0], rebuild(t[1]), rebuild(t[2]))
        return t

    return rebuild(tree)


def make_scorer(entry):
    rows = [(rv, A, B) for rv, A, B, _ in entry["rows"]]

    def score_pair(fA, fB):
        worst = 0.0
        for rv, A, B in rows:
            x = 1 - 1.0 / rv
            try:
                da = abs(fA(x) / A - 1)
                db = abs(fB(x) / B - 1)
            except Exception:
                return float("inf")
            # NaN guard on EACH part BEFORE any max: max(finite, nan)
            # returns the finite arg (nan comparisons always False), so
            # guarding after the max let nan-B candidates score on A
            # alone — measured: the "T1" hit had B ≡ nan
            if not (math.isfinite(da) and math.isfinite(db)):
                return float("inf")
            worst = max(worst, da, db)
            if worst > 10:
                return worst
        return worst

    return score_pair


def compile_pair(pair):
    eA, eB = (rd.to_sympy(t) for t in pair)
    return (sp.lambdify(X, eA, modules="math"),
            sp.lambdify(X, eB, modules="math"))


def polish(pair, score_pair, rounds=60, seed=0):
    """Float hill-climb on the constants — the fit-world finisher."""
    rng = random.Random(seed)
    consts = [(p, float(v)) for t in pair for p, v in tree_constants(t)]
    nA = len(tree_constants(pair[0]))

    def apply(vals):
        a = with_constants(pair[0], [sp.Float(v) for v in vals[:nA]])
        b = with_constants(pair[1], [sp.Float(v) for v in vals[nA:]])
        return (a, b)

    vals = [v for _, v in consts]
    best = score_pair(*compile_pair(apply(vals)))
    scale = 0.3
    for i in range(rounds):
        trial = [v * (1 + scale * (rng.random() - 0.5)) +
                 0.01 * scale * (rng.random() - 0.5) for v in vals]
        s = score_pair(*compile_pair(apply(trial)))
        if s < best:
            best, vals = s, trial
        else:
            scale *= 0.93
    # snap floats back to small rationals where free
    snapped = []
    for v in vals:
        rat = sp.nsimplify(v, rational=True, tolerance=abs(v) * 1e-3 + 1e-9)
        if rat.q <= 9999:
            cand = snapped + [rat] + [sp.Float(x)
                                      for x in vals[len(snapped) + 1:]]
            a = with_constants(pair[0], cand[:nA])
            b = with_constants(pair[1], cand[nA:])
            if score_pair(*compile_pair((a, b))) <= best * 1.02:
                snapped.append(rat)
                continue
        snapped.append(sp.Float(v))
    return apply(snapped), best


def structured_seed(rng):
    """RZ-structured genome: A = 1 + c1·(1−x) + c2·(1−x)²/(1 + c3·x).
    Design choice, recorded openly: KKZ also FIX the structural form and
    fit coefficients — seeding the same family is the same move, and GP
    remains free to mutate away from it."""
    def c():
        return ("c", sp.Rational(rng.randint(-9, 9), rng.randint(2, 12)))

    one_minus_x = ("-", ("c", sp.Integer(1)), ("r",))
    term1 = ("*", c(), one_minus_x)
    term2 = ("/", ("*", c(), ("powi", one_minus_x, 2)),
             ("+", ("c", sp.Integer(1)), ("*", c(), ("r",))))
    return ("+", ("+", ("c", sp.Integer(1)), term1), term2)


def hunt(entry, budget_gen=300, pop_size=250, seed=0, verbose=True):
    rng = random.Random(seed)
    score_pair = make_scorer(entry)
    t0 = time.time()

    def rand_pair():
        if rng.random() < 0.3:
            return (structured_seed(rng), structured_seed(rng))
        return (rd.rand_tree(rng, 4), rd.rand_tree(rng, 4))

    def fitness(pair):
        try:
            s = score_pair(*compile_pair(pair))
        except Exception:
            return float("inf")
        return s + 1e-4 * (rd.size(pair[0]) + rd.size(pair[1]))

    cache = {}

    def fit(pair):
        if pair not in cache:
            cache[pair] = fitness(pair)
        return cache[pair]

    pop = [rand_pair() for _ in range(pop_size)]
    best_overall, best_pair = float("inf"), None
    polished = set()

    for gen in range(budget_gen):
        scored = sorted(pop, key=fit)
        b = scored[0]
        fb = fit(b)
        if fb < best_overall:
            best_overall, best_pair = fb, b
        if verbose and gen % 20 == 0:
            raw = score_pair(*compile_pair(b))
            print(f"   gen {gen:3d}: best score {raw:.4%} "
                  f"({rd.size(b[0]) + rd.size(b[1])} nodes, "
                  f"{time.time() - t0:.0f}s)")
        # polish promising structures once each
        sig = (sp.srepr(rd.to_sympy(b[0])), sp.srepr(rd.to_sympy(b[1])))
        if score_pair(*compile_pair(b)) < 0.05 and sig not in polished:
            polished.add(sig)
            (pa, pb), s = polish(b, score_pair, seed=gen)
            if verbose:
                print(f"   gen {gen:3d}: polished structure → {s:.4%}")
            if s < best_overall:
                best_overall = s
                best_pair = (pa, pb)

        nxt = scored[:max(2, pop_size // 50)]
        while len(nxt) < pop_size:
            roll = rng.random()
            t1_, t2_ = (scored[min(rng.sample(range(len(scored)), 5))]
                        for _ in range(2))
            if roll < 0.5:
                child = tuple(rd.crossover(rng, t1_[i], t2_[i])
                              if rng.random() < 0.7 else t1_[i]
                              for i in range(2))
            elif roll < 0.85:
                slot = rng.randint(0, 1)
                child = tuple(rd.mutate(rng, t1_[i]) if i == slot
                              else t1_[i] for i in range(2))
            elif roll < 0.94:
                src = rng.randint(0, 1)
                child = (t1_[src], t1_[src])
            else:
                child = rand_pair()
            if all(rd.size(t) <= 30 for t in child):
                nxt.append(child)
        pop = nxt

    return best_pair, best_overall


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=float, default=0.3)
    ap.add_argument("--budget", type=int, default=300)
    args = ap.parse_args()

    truth = m12.build_truth()
    entry = truth[str(args.p)]
    print(f"Track B hunt: p={args.p}, M={entry['M']:.6f}, "
          f"{len(entry['rows'])} samples, budget {args.budget} gens")
    print("Bars: T1 ≤1%/≤6 consts · T2 ≤0.3%/≤8 · T3 <0.1% (beats KKZ)")

    best_pair, best = hunt(entry, budget_gen=args.budget)
    if best_pair is None:
        print("no viable candidate found — null result")
        return 1
    # no simplify here: sympy's simplify on float-constant trees can
    # produce zoo/nan DISPLAY artifacts for expressions that evaluate
    # perfectly (measured twice) — print the raw tree
    eA = rd.to_sympy(best_pair[0])
    eB = rd.to_sympy(best_pair[1])
    ncon = len(tree_constants(best_pair[0])) + \
        len(tree_constants(best_pair[1]))
    sc = make_scorer(entry)(*compile_pair(best_pair))
    tier = ("T3 — BEATS KKZ" if sc < 0.001 else
            "T2 — matches KKZ, check constant count" if sc < 0.003 else
            "T1 — compact & competitive" if sc < 0.01 else
            "below bar (record as progress, not victory)")
    print(f"\nBEST: score {sc:.4%} with {ncon} constants → {tier}")
    print(f"  A(x) = {eA}")
    print(f"  B(x) = {eB}")
    print("  (x = 1 − r_h/r;  e^Γ = x·A,  e^Λ = B²/(x·A))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
