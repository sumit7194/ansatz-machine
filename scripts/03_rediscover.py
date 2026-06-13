#!/usr/bin/env python3
"""Step 03 — the REDISCOVERY loop (the injection test).

The full conjecture machine, end to end:

    PROPOSE  genetic programming over expression trees for f(r)
             (PySR-style: no LLM, no API — evolution does the proposing)
    REDUCE   the static ansatz  ds² = -f dt² + dr²/f + r² dΩ²  is fed
             through the GR engine ONCE with f symbolic; what comes out
             is a small set of ODE residuals in (f, f', f'')
    VERIFY   stage 1: residuals evaluated numerically at sample radii
             (milliseconds per candidate — this is the fitness function);
             stage 2: survivors get the full symbolic proof from step 01
    NOVELTY  verified hits get fingerprinted against the step-02 catalog
    EVOLVE   tournament selection, subtree crossover/mutation, elitism;
             near-misses breed

Ground rule 2 ("rediscovery before discovery"): before this loop is
allowed to hunt anything new, it must REdiscover the classics from a
ansatz it was never told the answer to — Schwarzschild (3+1), BTZ
(2+1, Λ<0), Tangherlini (4+1). Same logic as echoes/ injections: if
the search can't find the thing we hid, it can't find anything.

A deliberate design point: GP constants are EXACT rationals all the way
through. A "numeric hit" is therefore already an exact symbolic
expression — promotion to theorem needs no constant-snapping, just the
step-01 symbolic proof.

Run:  .venv/bin/python scripts/03_rediscover.py [--quick]
"""

import argparse
import importlib.util
import os
import random
import time

import sympy as sp

from gr_engine import (Geometry, verify, VERIFIED, R_SYM,
                       build_ansatz_metric)
from finisher import snap_constants, structure_sig

# import the step-02 fingerprint module (filename starts with a digit)
_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "fingerprints", os.path.join(_here, "02_fingerprints.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

# ---------------------------------------------------------------------------
# Expression trees (the genome)
# ---------------------------------------------------------------------------
# node = ('+',l,r) ('-',l,r) ('*',l,r) ('/',l,r) ('powi',child,k) ('r',) ('c',Rational)

BIN_OPS = ["+", "-", "*", "/"]


def rand_const(rng):
    return ("c", sp.Rational(rng.randint(1, 9), rng.randint(1, 4)))


def rand_tree(rng, depth):
    if depth <= 0 or rng.random() < 0.3:
        return ("r",) if rng.random() < 0.5 else rand_const(rng)
    roll = rng.random()
    if roll < 0.85:
        op = rng.choice(BIN_OPS)
        return (op, rand_tree(rng, depth - 1), rand_tree(rng, depth - 1))
    return ("powi", rand_tree(rng, depth - 1), rng.randint(2, 3))


def to_sympy(node):
    k = node[0]
    if k == "r":
        return R_SYM
    if k == "c":
        return node[1]
    if k == "powi":
        return to_sympy(node[1]) ** node[2]
    a, b = to_sympy(node[1]), to_sympy(node[2])
    return {"+": a + b, "-": a - b, "*": a * b,
            "/": a / b}[k]


def size(node):
    if node[0] in ("r", "c"):
        return 1
    if node[0] == "powi":
        return 1 + size(node[1])
    return 1 + size(node[1]) + size(node[2])


def paths(node, prefix=()):
    yield prefix
    if node[0] == "powi":
        yield from paths(node[1], prefix + (1,))
    elif node[0] in BIN_OPS:
        yield from paths(node[1], prefix + (1,))
        yield from paths(node[2], prefix + (2,))


def get_at(node, path):
    for i in path:
        node = node[i]
    return node


def set_at(node, path, new):
    if not path:
        return new
    lst = list(node)
    lst[path[0]] = set_at(node[path[0]], path[1:], new)
    return tuple(lst)


def mutate(rng, node, max_depth=4):
    p = rng.choice(list(paths(node)))
    target = get_at(node, p)
    if target[0] == "c" and rng.random() < 0.5:
        # constant jitter, staying exact-rational
        c = target[1] + sp.Rational(rng.randint(-2, 2), rng.randint(1, 4))
        return set_at(node, p, ("c", c))
    return set_at(node, p, rand_tree(rng, rng.randint(1, max_depth - 1)))


def crossover(rng, a, b):
    pa = rng.choice(list(paths(a)))
    pb = rng.choice(list(paths(b)))
    return set_at(a, pa, get_at(b, pb))


# ---------------------------------------------------------------------------
# REDUCE: ansatz -> ODE residuals, once per (dimension, Λ)
# ---------------------------------------------------------------------------

def reduce_ansatz(n, Lambda):
    """Run the symbolic ansatz through the engine once. Returns fast
    numeric residual callables res(r, f, f', f''), the symbolic residuals
    (in terms of F — the finisher needs them), and F itself."""
    F = sp.Function("F")(R_SYM)
    metric, coords, angles = build_ansatz_metric(n, F)
    geo = Geometry(metric, coords)
    # MIXED residual R^a_b: for the diagonal ansatz g^φφ cancels every
    # sin²θ factor, so the components are angle-free. (Bought by: with
    # lower-index components + numeric angle-fixing, unsimplifiable trig
    # CONSTANTS leaked into the finisher's equations and sp.solve could
    # not prove the system consistent — Richardson inside the solver.)
    residual = geo.ginv * geo.vacuum_residual(Lambda)

    s0, s1, s2 = sp.symbols("s0 s1 s2")
    rep = {sp.Derivative(F, (R_SYM, 2)): s2,
           sp.Derivative(F, R_SYM): s1, F: s0}
    ang_sub = {a: sp.Rational(11, 10) for a in angles}  # safety net only

    seen, funcs, sym_res = set(), [], []
    for i in range(geo.n):
        for j in range(geo.n):
            expr = residual[i, j]
            if expr == 0:
                continue
            # simplify SYMBOLICALLY FIRST: trig identities in θ fire and
            # the angular components collapse to θ-free form. Numeric
            # angle substitution before simplify leaves unsimplifiable
            # trig constants that poison the finisher's equations.
            simplified = sp.simplify(expr)
            if any(simplified.has(a) for a in angles):
                simplified = sp.simplify(simplified.subs(ang_sub))
            key = sp.srepr(simplified.xreplace(rep))
            if key in seen:
                continue
            seen.add(key)
            sym_res.append(simplified)
            funcs.append(sp.lambdify((R_SYM, s0, s1, s2),
                                     simplified.xreplace(rep),
                                     modules="math"))
    return funcs, sym_res, F


# ---------------------------------------------------------------------------
# Fitness: numeric residual at sample radii (+ parsimony)
# ---------------------------------------------------------------------------

SAMPLE_R = [2.31, 3.77, 5.13, 7.91, 11.37, 17.03]
PROMOTE_TOL = 1e-10
SNAP_TOL = 1e-2  # near-miss band handed to the algebraic finisher (D14)
PARSIMONY = 1e-3
INF = float("inf")


def make_fitness(res_funcs, trivial_fvals=None):
    """trivial_fvals: values of the maximally-symmetric member of this
    (n, Λ) family at SAMPLE_R — f_vac = 1 - 2Λr²/((n-1)(n-2)) (Minkowski
    when Λ=0, de Sitter/AdS otherwise). Candidates sitting on it get
    penalized: the vacuum ground state solves the equations perfectly
    but discovering it is not discovering anything."""
    cache = {}

    def fitness(tree):
        key = tree
        if key in cache:
            return cache[key]
        e = to_sympy(tree)
        try:
            e1 = sp.diff(e, R_SYM)
            e2 = sp.diff(e1, R_SYM)
            fe = sp.lambdify(R_SYM, e, modules="math")
            fe1 = sp.lambdify(R_SYM, e1, modules="math")
            fe2 = sp.lambdify(R_SYM, e2, modules="math")
            total = 0.0
            f_vals = []
            for rv in SAMPLE_R:
                f0, f1v, f2v = fe(rv), fe1(rv), fe2(rv)
                if abs(f0) < 1e-12:  # 1/f in the metric
                    raise ZeroDivisionError
                f_vals.append(f0)
                for rf in res_funcs:
                    v = rf(rv, f0, f1v, f2v)
                    total += abs(v)
                    if total > 1e12:
                        raise OverflowError
            raw = total / len(SAMPLE_R)
            # triviality penalty: a numerically-constant f is flat space
            # in this ansatz (or no solution at all) — the loop must not
            # be allowed to "win" with Minkowski. Catches r/r tricks too.
            if max(f_vals) - min(f_vals) < 1e-9:
                raw += 1.0
            # maximally-symmetric-member penalty (the de Sitter/AdS
            # ground state — the "flat space" of nonzero Λ)
            if trivial_fvals is not None and all(
                    abs(fv - tv) < 1e-6 * max(1.0, abs(tv))
                    for fv, tv in zip(f_vals, trivial_fvals)):
                raw += 1.0
        except (ZeroDivisionError, OverflowError, ValueError, TypeError):
            raw = INF
        out = (raw, raw + PARSIMONY * size(tree) if raw < INF else INF)
        cache[key] = out
        return out

    return fitness


# ---------------------------------------------------------------------------
# The loop
# ---------------------------------------------------------------------------

def rediscover(label, n, Lambda, catalog, seed=0, pop_size=300,
               max_gen=150, verbose=True, reject_csi=False,
               stagnation_gens=30):
    """Run the full machine for one (dimension, Λ) rung.
    Returns a result dict or None.

    reject_csi: treat constant-invariant (maximally symmetric) hits as
    trivial and keep hunting for a mass-bearing solution. Leave False in
    2+1, where CSI is all that locally exists (no local degrees of
    freedom) and the blind-spot verdict IS the result."""
    rng = random.Random(seed)
    t0 = time.time()
    if verbose:
        print(f"\n—— {label}: n={n}, Λ={Lambda} "
              f"(seed {seed}) ——")
    trivial_fvals = None
    if reject_csi:
        f_vac = 1 - 2 * Lambda * R_SYM**2 / ((n - 1) * (n - 2))
        trivial_fvals = [float(f_vac.subs(R_SYM, rv)) for rv in SAMPLE_R]
    res_funcs, sym_res, F_obj = reduce_ansatz(n, Lambda)
    fitness = make_fitness(res_funcs, trivial_fvals)
    if verbose:
        print(f"   REDUCE done ({time.time() - t0:.1f}s) — ansatz residuals "
              "compiled to fast numeric form")

    def promote(e, gen, note=""):
        """Symbolic proof + triviality gates + novelty check."""
        try:
            metric, coords, _ = build_ansatz_metric(n, e)
            verdict, detail = verify(metric, coords, params=[],
                                     Lambda=Lambda)
        except Exception:
            return None  # degenerate metric
        if verdict != VERIFIED:
            if verbose:
                print(f"   ↩ symbolic promotion failed ({verdict}: "
                      f"{detail}) — evolving on{note}")
            return None
        geo = Geometry(metric, coords)
        if geo.kretschmann == 0:
            if verbose:
                print("   ↩ verified but FLAT (Kretschmann ≡ 0) — "
                      "Minkowski in a costume; rejected as trivial")
            return None
        if reject_csi and not any(geo.kretschmann.has(x) for x in coords):
            if verbose:
                print("   ↩ verified but maximally symmetric "
                      f"(K = {geo.kretschmann}, constant) — the vacuum "
                      "ground state of this Λ; rejected as trivial")
            return None
        cls, cdetail = fp.classify(geo, catalog)
        dt = time.time() - t0
        if verbose:
            print(f"   ✅ VERIFIED as exact solution ({detail}){note}")
            print(f"   🔎 NOVELTY: {cls} — {cdetail}")
            print(f"   total {dt:.1f}s, generation {gen}")
        return {"label": label, "n": n, "Lambda": Lambda,
                "f": e, "verdict": verdict, "class": cls,
                "class_detail": cdetail, "gen": gen, "time": dt}

    # dimension-aware enrichment for the finisher: the mass falloff in n
    # spacetime dimensions is r^-(n-3) — exactly the term GP near-misses
    # were missing (measured: expedition leg 2 stalled at 6e-3 circling
    # the ground state without its -c/r² tail)
    enrich = tuple(sorted({-(n - 3), -2, -1} - {0}))

    pop = [rand_tree(rng, 4) for _ in range(pop_size)]
    tried_promote = set()
    snapped = set()
    stagnant_best, stagnant_count = float("inf"), 0

    for gen in range(max_gen):
        scored = sorted(((fitness(ind), ind) for ind in pop),
                        key=lambda x: x[0][1])
        (best_raw, _), best = scored[0]

        if best_raw < PROMOTE_TOL and best not in tried_promote:
            tried_promote.add(best)
            e = sp.simplify(sp.together(to_sympy(best)))
            if verbose:
                print(f"   gen {gen:3d}: numeric hit  f(r) = {e}  "
                      f"(residual {best_raw:.1e}) — promoting...")
            out = promote(e, gen)
            if out:
                return out

        # the algebraic finisher (D14): near-miss -> exact constants
        if PROMOTE_TOL <= best_raw < SNAP_TOL:
            e_raw = to_sympy(best)
            sig = structure_sig([e_raw])
            if sig not in snapped:
                snapped.add(sig)
                if verbose:
                    print(f"   gen {gen:3d}: near-miss ({best_raw:.1e}) — "
                          "snapping constants algebraically...")
                for (fe,) in snap_constants([e_raw], sym_res, [F_obj],
                                            enrich_powers=enrich):
                    out = promote(sp.simplify(fe), gen, note=" [snapped]")
                    if out:
                        return out

        if verbose and gen % 10 == 0:
            print(f"   gen {gen:3d}: best raw residual {best_raw:.3e}  "
                  f"f(r) = {sp.sstr(to_sympy(best))[:60]}")

        # stagnation cutoff: a GP run that stops improving rarely
        # recovers (measured: one seed sat at 6.8e-4 for 140 gens,
        # 2200s) — cheaper to restart with a fresh seed
        if best_raw < stagnant_best * 0.99:
            stagnant_best, stagnant_count = best_raw, 0
        else:
            stagnant_count += 1
            if stagnant_count >= stagnation_gens:
                if verbose:
                    print(f"   ⏹ stagnant for {stagnation_gens} gens at "
                          f"{best_raw:.3e} (gen {gen}, "
                          f"{time.time() - t0:.1f}s) — restarting")
                return None

        # next generation: elitism + tournament offspring
        elites = [ind for _, ind in scored[:max(2, pop_size // 50)]]
        newpop = list(elites)

        def tournament():
            picks = rng.sample(range(len(scored)), 5)
            return scored[min(picks)][1]

        while len(newpop) < pop_size:
            roll = rng.random()
            if roll < 0.55:
                child = crossover(rng, tournament(), tournament())
            elif roll < 0.90:
                child = mutate(rng, tournament())
            else:
                child = rand_tree(rng, 4)
            if size(child) <= 25:
                newpop.append(child)
        pop = newpop

    if verbose:
        print(f"   ✗ no exact hit in {max_gen} generations "
              f"({time.time() - t0:.1f}s) — null result for this run")
    return None


def run_with_restarts(label, n, Lambda, catalog, seeds=(0, 1, 2),
                      workers=None, **kw):
    """Try seeds until one finds an exact hit.

    Default: sequential (deterministic — same seed order every run; the
    regression batteries rely on this). With workers=N > 1, seeds run as
    N parallel forked processes and the FIRST success wins. Honest note:
    which seed wins can vary run-to-run with completion order — fine for
    hunts (any find is verifier-proved regardless of the seed that found
    it), wrong for regression batteries, so parallel stays opt-in."""
    if workers and workers > 1 and len(seeds) > 1:
        return _run_seeds_parallel(label, n, Lambda, catalog, seeds,
                                   workers, **kw)
    for s in seeds:
        out = rediscover(label, n, Lambda, catalog, seed=s, **kw)
        if out:
            return out
    return None


def _run_seeds_parallel(label, n, Lambda, catalog, seeds, workers, **kw):
    import multiprocessing as mp
    import queue as _queue
    ctx = mp.get_context("fork")  # fork: children inherit loaded modules
    q = ctx.Queue()

    def _worker(s):
        try:
            q.put((s, rediscover(label, n, Lambda, catalog, seed=s, **kw)))
        except Exception:
            q.put((s, None))

    pending = list(seeds)
    running = {}
    try:
        while pending or running:
            while pending and len(running) < workers:
                s = pending.pop(0)
                p = ctx.Process(target=_worker, args=(s,), daemon=True)
                p.start()
                running[s] = p
            try:
                s_done, out = q.get(timeout=15)
            except _queue.Empty:
                # reap workers that died without reporting (counts as a miss)
                for s, p in list(running.items()):
                    if not p.is_alive():
                        running.pop(s).join()
                continue
            if s_done in running:
                running.pop(s_done).join()
            if out:
                return out
    finally:
        for p in running.values():
            p.terminate()
    return None


# ---------------------------------------------------------------------------
# The injection battery: the machine must rediscover the classics blind
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="smaller populations (smoke test)")
    args = ap.parse_args()
    kw = dict(pop_size=120, max_gen=60) if args.quick else {}

    print("Building fingerprint catalog...")
    catalog = fp.build_catalog()

    # (label, dim, Λ, expected classification, expected detail substring)
    runs = [
        ("Schwarzschild rung (3+1, Λ=0)", 4, sp.S.Zero,
         fp.KNOWN_LIKELY, "Schwarzschild (3+1)"),
        ("BTZ rung (2+1, Λ=-1)", 3, sp.Integer(-1),
         fp.BLIND_SPOT, "CSI"),  # all 2+1 Λ<0 vacua are locally AdS₃ —
        # BTZ differs only globally; invariants are constant, and the
        # honest verdict is a declared blind spot, not a match
        ("Tangherlini rung (4+1, Λ=0)", 5, sp.S.Zero,
         fp.KNOWN_LIKELY, "Tangherlini"),
    ]
    results = []
    for label, n, lam, _, _ in runs:
        results.append(run_with_restarts(label, n, lam, catalog, **kw))

    print("\n" + "=" * 70)
    print("INJECTION TEST SUMMARY")
    ok = True
    for (label, _, _, want_cls, want_sub), res in zip(runs, results):
        if res and res["class"] == want_cls \
                and want_sub in res["class_detail"]:
            print(f"  ✅ {label}: f(r) = {res['f']}  →  {res['class']} "
                  f"[{want_sub}]")
        elif res:
            print(f"  ❌ {label}: found f(r) = {res['f']} but classified "
                  f"{res['class']} ({res['class_detail']}) — "
                  f"expected {want_cls} [{want_sub}]")
            ok = False
        else:
            print(f"  ❌ {label}: not rediscovered")
            ok = False
    print("INJECTION TEST " + ("PASSED ✅" if ok else "FAILED ❌"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
