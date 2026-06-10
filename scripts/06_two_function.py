#!/usr/bin/env python3
"""Step 06 — the TWO-FUNCTION hall (v2's bigger search space).

Ansatz:   ds² = -f(r)·dt² + dr²/h(r) + r²·dΩ²
with f and h INDEPENDENT genomes — the search space of v1's one-function
room, squared.

Why this hall is the perfect honesty stress test: Birkhoff's theorem
(and its Λ/higher-D generalizations) says static spherical vacuum is
EXHAUSTED by the known families — h must be the standard f_vac-family
form and f can differ from h only by a constant time-rescaling
f = c·h (pure gauge). So the correct output here is ZERO false
novelty: every exact hit must classify as a known or previously-grown
family, because curvature invariants are immune to the t → λt gauge
freedom. A sloppy machine with a 2× genome would spray CANDIDATE_NEWs;
an honest one rediscovers Birkhoff empirically.

Rung 2 deliberately depends on the machine's MEMORY: it hunts in
(4+1, Λ=-1), where the only mass-bearing family is the one the machine
itself discovered and grew in steps 04/05 (catalog_discoveries.json).

The evolutionary scaffold parallels 03_rediscover.py for a pair genome;
if a third ansatz class ever appears, consolidate them (rule of three).

Run:  .venv/bin/python scripts/06_two_function.py [--quick]
"""

import argparse
import importlib.util
import os
import random
import time

import sympy as sp

from gr_engine import Geometry, verify, VERIFIED, R_SYM

_here = os.path.dirname(os.path.abspath(__file__))


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(_here, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fp = _load("fingerprints", "02_fingerprints.py")
rd = _load("rediscover", "03_rediscover.py")

SAMPLE_R = rd.SAMPLE_R
PROMOTE_TOL = rd.PROMOTE_TOL
PARSIMONY = rd.PARSIMONY
INF = float("inf")


# ---------------------------------------------------------------------------
# REDUCE: two-function ansatz -> residuals res(r, f, f', f'', h, h', h'')
# ---------------------------------------------------------------------------

def build_ansatz_metric2(n, fexpr, hexpr):
    t = sp.Symbol("t", real=True)
    angles = sp.symbols(f"x1:{n - 1}", real=True)
    parts = [-fexpr, 1 / hexpr]
    area = R_SYM**2
    for i in range(n - 2):
        parts.append(area)
        area = area * sp.sin(angles[i]) ** 2
    coords = [t, R_SYM] + list(angles)
    return sp.diag(*parts), coords, angles


def reduce_ansatz2(n, Lambda):
    F = sp.Function("F")(R_SYM)
    H = sp.Function("H")(R_SYM)
    metric, coords, angles = build_ansatz_metric2(n, F, H)
    geo = Geometry(metric, coords)
    residual = geo.vacuum_residual(Lambda)

    s0, s1, s2, u0, u1, u2 = sp.symbols("s0 s1 s2 u0 u1 u2")
    rep = {sp.Derivative(F, (R_SYM, 2)): s2, sp.Derivative(F, R_SYM): s1,
           F: s0,
           sp.Derivative(H, (R_SYM, 2)): u2, sp.Derivative(H, R_SYM): u1,
           H: u0}
    ang_sub = {a: sp.Rational(11, 10) for a in angles}

    seen, funcs = set(), []
    for i in range(geo.n):
        for j in range(i, geo.n):
            expr = residual[i, j]
            if expr == 0:
                continue
            expr = sp.simplify(expr.subs(ang_sub)).xreplace(rep)
            key = sp.srepr(expr)
            if key in seen:
                continue
            seen.add(key)
            funcs.append(sp.lambdify((R_SYM, s0, s1, s2, u0, u1, u2),
                                     expr, modules="math"))
    return funcs


# ---------------------------------------------------------------------------
# Fitness over the pair genome
# ---------------------------------------------------------------------------

def make_fitness2(res_funcs, trivial_fvals):
    cache = {}

    def compile_tree(tree):
        e = rd.to_sympy(tree)
        e1 = sp.diff(e, R_SYM)
        e2 = sp.diff(e1, R_SYM)
        return (sp.lambdify(R_SYM, e, modules="math"),
                sp.lambdify(R_SYM, e1, modules="math"),
                sp.lambdify(R_SYM, e2, modules="math"))

    def fitness(pair):
        if pair in cache:
            return cache[pair]
        try:
            fF = compile_tree(pair[0])
            fH = compile_tree(pair[1])
            total = 0.0
            f_vals, h_vals = [], []
            for rv in SAMPLE_R:
                f0, f1v, f2v = fF[0](rv), fF[1](rv), fF[2](rv)
                h0, h1v, h2v = fH[0](rv), fH[1](rv), fH[2](rv)
                if abs(f0) < 1e-12 or abs(h0) < 1e-12:
                    raise ZeroDivisionError
                f_vals.append(f0)
                h_vals.append(h0)
                for rf in res_funcs:
                    total += abs(rf(rv, f0, f1v, f2v, h0, h1v, h2v))
                    if total > 1e12:
                        raise OverflowError
            raw = total / len(SAMPLE_R)
            # triviality shaping (same ladder as 03, lifted to the pair):
            # both numerically constant -> flat-or-nothing
            if max(f_vals) - min(f_vals) < 1e-9 \
                    and max(h_vals) - min(h_vals) < 1e-9:
                raw += 1.0
            # h on the vacuum ground state AND f proportional to it
            # (t-rescaling gauge of the maximally symmetric member)
            if all(abs(h - tv) < 1e-6 * max(1.0, abs(tv))
                   for h, tv in zip(h_vals, trivial_fvals)):
                ratios = [f / tv for f, tv in zip(f_vals, trivial_fvals)
                          if abs(tv) > 1e-12]
                if ratios and max(ratios) - min(ratios) \
                        < 1e-6 * max(1.0, abs(ratios[0])):
                    raw += 1.0
        except (ZeroDivisionError, OverflowError, ValueError, TypeError):
            raw = INF
        out = (raw, raw + PARSIMONY * (rd.size(pair[0]) + rd.size(pair[1]))
               if raw < INF else INF)
        cache[pair] = out
        return out

    return fitness


# ---------------------------------------------------------------------------
# The loop (pair genome)
# ---------------------------------------------------------------------------

def hunt(label, n, Lambda, catalog, seed=0, pop_size=400, max_gen=250,
         reject_csi=True, stagnation_gens=40, verbose=True):
    rng = random.Random(seed)
    t0 = time.time()
    if verbose:
        print(f"\n—— {label}: n={n}, Λ={Lambda} (seed {seed}) ——")
    f_vac = 1 - 2 * Lambda * R_SYM**2 / ((n - 1) * (n - 2))
    trivial_fvals = [float(f_vac.subs(R_SYM, rv)) for rv in SAMPLE_R]
    fit = make_fitness2(reduce_ansatz2(n, Lambda), trivial_fvals)
    if verbose:
        print(f"   REDUCE done ({time.time() - t0:.1f}s)")

    def rand_pair():
        return (rd.rand_tree(rng, 4), rd.rand_tree(rng, 4))

    pop = [rand_pair() for _ in range(pop_size)]
    tried = set()
    stag_best, stag_n = INF, 0

    for gen in range(max_gen):
        scored = sorted(((fit(p), p) for p in pop), key=lambda x: x[0][1])
        (best_raw, _), best = scored[0]

        if best_raw < PROMOTE_TOL and best not in tried:
            tried.add(best)
            eF = sp.simplify(sp.together(rd.to_sympy(best[0])))
            eH = sp.simplify(sp.together(rd.to_sympy(best[1])))
            if verbose:
                print(f"   gen {gen:3d}: numeric hit  f = {eF}   h = {eH}  "
                      f"({best_raw:.1e}) — promoting...")
            metric, coords, _ = build_ansatz_metric2(n, eF, eH)
            verdict, detail = verify(metric, coords, params=[],
                                     Lambda=Lambda)
            if verdict == VERIFIED:
                geo = Geometry(metric, coords)
                if geo.kretschmann == 0:
                    if verbose:
                        print("   ↩ flat — trivial, evolving on")
                    continue
                if reject_csi and not any(geo.kretschmann.has(x)
                                          for x in coords):
                    if verbose:
                        print("   ↩ maximally symmetric — trivial, "
                              "evolving on")
                    continue
                cls, cdetail = fp.classify(geo, catalog)
                gauge = sp.simplify(eF / eH)
                dt = time.time() - t0
                if verbose:
                    print(f"   ✅ VERIFIED ({detail})")
                    print(f"   🔎 NOVELTY: {cls} — {cdetail}")
                    print(f"   gauge check f/h = {gauge} "
                          f"({'pure t-rescaling — Birkhoff' if gauge.is_constant() else 'NOT proportional'})")
                return {"label": label, "f": eF, "h": eH, "gauge": gauge,
                        "class": cls, "class_detail": cdetail,
                        "gen": gen, "time": dt}
            if verbose:
                print(f"   ↩ promotion failed ({verdict}) — evolving on")

        if verbose and gen % 20 == 0:
            print(f"   gen {gen:3d}: best {best_raw:.3e}")

        if best_raw < stag_best * 0.99:
            stag_best, stag_n = best_raw, 0
        else:
            stag_n += 1
            if stag_n >= stagnation_gens:
                if verbose:
                    print(f"   ⏹ stagnant at {best_raw:.3e} "
                          f"(gen {gen}) — restarting")
                return None

        elites = [p for _, p in scored[:max(2, pop_size // 50)]]
        newpop = list(elites)

        def tournament():
            return scored[min(rng.sample(range(len(scored)), 5))][1]

        while len(newpop) < pop_size:
            roll = rng.random()
            if roll < 0.50:
                a, b = tournament(), tournament()
                child = tuple(rd.crossover(rng, a[i], b[i])
                              if rng.random() < 0.7 else a[i]
                              for i in range(2))
            elif roll < 0.82:
                a = tournament()
                slot = rng.randint(0, 1)
                child = tuple(rd.mutate(rng, a[i]) if i == slot else a[i]
                              for i in range(2))
            elif roll < 0.94:
                # gene duplication: without this, a building block found
                # in the h-slot can never reach the f-slot — and
                # Birkhoff-type solutions need the SAME structure (same
                # mass constant) in both. Measured: per-slot crossover
                # alone stagnated at residual ~1-3 on every 3+1/4+1 seed.
                a = tournament()
                if rng.random() < 0.5:
                    src = rng.randint(0, 1)
                    child = (a[src], a[src])
                else:  # subtree graft across slots
                    src = rng.randint(0, 1)
                    dst = 1 - src
                    grafted = rd.crossover(rng, a[dst], a[src])
                    child = (grafted, a[1]) if dst == 0 else (a[0], grafted)
            else:
                child = rand_pair()
            if rd.size(child[0]) <= 25 and rd.size(child[1]) <= 25:
                newpop.append(child)
        pop = newpop

    if verbose:
        print(f"   ✗ no exact hit in {max_gen} generations")
    return None


def hunt_with_restarts(label, n, Lambda, catalog, seeds=(0, 1, 2, 3, 4, 5),
                       **kw):
    for s in seeds:
        out = hunt(label, n, Lambda, catalog, seed=s, **kw)
        if out:
            return out
    return None


# ---------------------------------------------------------------------------
# The Birkhoff battery
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    kw = dict(pop_size=150, max_gen=80) if args.quick else {}

    catalog = fp.build_catalog()  # WITH the machine's own discoveries
    has_memory = any("discovered" in e.name for e in catalog)
    print(f"catalog: {len(catalog)} families "
          f"({'memory loaded' if has_memory else 'NO grown families — run 05 first'})")

    rungs = [
        ("Birkhoff rung (3+1, Λ=0, f≠h allowed)", 4, sp.S.Zero, True,
         fp.KNOWN_LIKELY, "Schwarzschild (3+1)"),
        ("Memory rung (4+1, Λ=-1, f≠h allowed)", 5, sp.Integer(-1), True,
         fp.KNOWN_LIKELY, "discovered"),
        ("Flatland rung (2+1, Λ=-1, f≠h allowed)", 3, sp.Integer(-1),
         False, fp.BLIND_SPOT, "CSI"),
    ]
    results = []
    for label, n, lam, rcsi, _, _ in rungs:
        results.append(hunt_with_restarts(label, n, lam, catalog,
                                          reject_csi=rcsi, **kw))

    print("\n" + "=" * 72)
    print("TWO-FUNCTION HALL SUMMARY")
    ok = True
    for (label, _, _, _, want_cls, want_sub), res in zip(rungs, results):
        if res and res["class"] == want_cls \
                and want_sub in res["class_detail"]:
            print(f"  ✅ {label}")
            print(f"       f = {res['f']}   h = {res['h']}   "
                  f"f/h = {res['gauge']}")
            print(f"       {res['class']} — {res['class_detail'][:90]}")
        elif res:
            print(f"  ❌ {label}: got {res['class']} "
                  f"({res['class_detail'][:90]}) wanted {want_cls} "
                  f"[{want_sub}]  f={res['f']} h={res['h']}")
            ok = False
        else:
            print(f"  ❌ {label}: no exact hit (null result)")
            ok = False
    print("TWO-FUNCTION HALL " + ("PASSED ✅" if ok else "HAS FAILURES ❌"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
