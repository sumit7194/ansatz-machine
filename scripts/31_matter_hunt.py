#!/usr/bin/env python3
"""Step 31 — MATTER DISCOVERY: the propose→verify→evolve loop, now sourced.

Path 2 of v6: the original conjecture-machine loop (genetic programming over
exact-rational f(r), numeric residual as fitness, symbolic proof at the end)
turned loose on a MATTER theory rather than vacuum. The exact-metric discovery
loop is the project's genuinely-unclaimed-by-machines capability; this opens it
to sourced gravity using the engine extensions just built (27/28).

Test theory: Einstein–Maxwell with a unit-charge electric field A_t = Q/r.
The machine is NOT told Reissner–Nordström. It searches f(r) and the cheapest
residual of  R^a_b = κ T^a_b[EM]  pulls it toward the charge term: it should
DISCOVER f = 1 − 2M/r + Q²/r² — i.e. that charge adds a +Q²/r² well — then the
exact verifier confirms it.

Run:  .venv/bin/python scripts/31_matter_hunt.py
"""

import importlib.util
import os
import sys
import time

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from gr_engine import Geometry, build_ansatz_metric, R_SYM


def _load(n, f):
    s = importlib.util.spec_from_file_location(n, os.path.join(_here, f))
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


gp = _load("gp", "03_rediscover.py")     # rand_tree, mutate, crossover, to_sympy, size
mx = _load("mx", "28_maxwell.py")        # faraday, em_stress, verify_em

SAMPLE_R = gp.SAMPLE_R
Q_VAL = sp.Integer(1)                     # unit charge
KAPPA = sp.Integer(2)


def reduce_em(Qv):
    """Symbolic-once: Einstein–Maxwell residual as cheap funcs(r,f,f',f'')."""
    F = sp.Function("F")(R_SYM)
    metric, coords, angles = build_ansatz_metric(4, F)
    geo = Geometry(metric, coords)
    Ffield = mx.faraday([Qv / R_SYM, 0, 0, 0], coords)
    T = mx.em_stress(geo, Ffield)
    residual = geo.ginv * (geo.ricci - KAPPA * T)     # mixed R^a_b − κT^a_b
    s0, s1, s2 = sp.symbols("s0 s1 s2")
    rep = {sp.Derivative(F, (R_SYM, 2)): s2, sp.Derivative(F, R_SYM): s1, F: s0}
    asub = {a: sp.Rational(11, 10) for a in angles}
    seen, funcs = set(), []
    for i in range(geo.n):
        for j in range(geo.n):
            e = residual[i, j]
            if e == 0:
                continue
            e = sp.simplify(e)
            if any(e.has(a) for a in angles):
                e = sp.simplify(e.subs(asub))
            key = sp.srepr(e.xreplace(rep))
            if key in seen:
                continue
            seen.add(key)
            funcs.append(sp.lambdify((R_SYM, s0, s1, s2), e.xreplace(rep), "math"))
    return funcs


def make_fitness(funcs):
    cache = {}
    def fitness(tree):
        if tree in cache:
            return cache[tree]
        e = gp.to_sympy(tree)
        try:
            fe = sp.lambdify(R_SYM, e, "math")
            fe1 = sp.lambdify(R_SYM, sp.diff(e, R_SYM), "math")
            fe2 = sp.lambdify(R_SYM, sp.diff(e, R_SYM, 2), "math")
            tot, fvals = 0.0, []
            for rv in SAMPLE_R:
                f0 = fe(rv)
                if abs(f0) < 1e-12:
                    raise ZeroDivisionError
                fvals.append(f0)
                for rf in funcs:
                    tot += abs(rf(rv, f0, fe1(rv), fe2(rv)))
                    if tot > 1e12:
                        raise OverflowError
            raw = tot / len(SAMPLE_R)
            if max(fvals) - min(fvals) < 1e-9:   # constant f = no solution here
                raw += 1.0
        except (ZeroDivisionError, OverflowError, ValueError, TypeError):
            raw = float("inf")
        out = (raw, raw + 1e-3 * gp.size(tree) if raw < float("inf") else float("inf"))
        cache[tree] = out
        return out
    return fitness


def evolve(fitness, seed=0, pop_size=250, gens=60):
    import random
    rng = random.Random(seed)
    pop = [gp.rand_tree(rng, 4) for _ in range(pop_size)]
    best = None
    for g in range(gens):
        scored = sorted(pop, key=lambda t: fitness(t)[1])
        if best is None or fitness(scored[0])[0] < fitness(best)[0]:
            best = scored[0]
        if fitness(best)[0] < 1e-10:
            break
        keep = scored[:max(2, pop_size // 10)]
        newpop = list(keep)
        while len(newpop) < pop_size:
            a = min(rng.sample(scored[:pop_size // 2], 3), key=lambda t: fitness(t)[1])
            b = min(rng.sample(scored[:pop_size // 2], 3), key=lambda t: fitness(t)[1])
            child = gp.crossover(rng, a, b)
            if rng.random() < 0.4:
                child = gp.mutate(rng, child)
            if gp.size(child) <= 25:
                newpop.append(child)
        pop = newpop
    return best, fitness(best)[0]


def main():
    print("MATTER DISCOVERY — Einstein–Maxwell (unit charge), no RN supplied\n")
    t0 = time.time()
    funcs = reduce_em(Q_VAL)
    print(f"  reduced EM residual ({len(funcs)} eqs) in {time.time()-t0:.1f}s; evolving f(r)...", flush=True)
    best, res = evolve(make_fitness(funcs), seed=0)
    f = sp.nsimplify(sp.cancel(gp.to_sympy(best)), rational=True)
    print(f"  best f(r) = {f}   (residual {res:.2e}, {time.time()-t0:.0f}s)")

    # verify the discovery exactly + check the charge term emerged
    t, r = sp.Symbol("t", real=True), R_SYM
    metric, coords, _ = build_ansatz_metric(4, f)
    verdict, detail = mx.verify_em(metric, coords, [Q_VAL / r, 0, 0, 0], KAPPA)
    fexp = sp.expand(f)
    q2 = sp.simplify(fexp.coeff(r, -2))      # the Q²/r² charge term
    mass = sp.simplify(-fexp.coeff(r, -1) / 2)  # 1/r coeff = −2M
    print(f"  exact verdict: {verdict}  ({detail})")
    print(f"  charge term: coeff(1/r²) = {q2} (should be Q²={Q_VAL**2}); discovered mass M = {mass}")
    found = (verdict == "VERIFIED") and (sp.simplify(q2 - Q_VAL**2) == 0)
    print(f"\nMATTER DISCOVERY: {'✅ rediscovered the Reissner–Nordström charge term' if found else 'verdict '+str(verdict)+' — see above'}")
    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
