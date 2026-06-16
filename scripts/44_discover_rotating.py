#!/usr/bin/env python3
"""Step 44 — ROTATING DISCOVERY: invent a spinning black hole (rediscover Kerr).

The discovery loop (43) searched the static one-function ansatz. Rotating metrics
are off-diagonal and analyzing each takes ~seconds — so the naive "search arbitrary
rotating metrics" would crawl. The smart design (proven feasible first): FIX the
rational Kerr STRUCTURE and search just the one radial function Δ(r) inside it —

  Σ = r²+a²u²,  g_tt = −(Δ−a²(1−u²))/Σ,  g_rr = Σ/Δ,  g_uu = Σ/(1−u²),
  g_tφ = −a(1−u²)(r²+a²−Δ)/Σ,  g_φφ = (1−u²)[(r²+a²)² − Δa²(1−u²)]/Σ,   u=cosθ.

The vacuum residual reduces ONCE (7.5s) to formulas in (Δ, Δ', Δ''); candidates are
then scored NUMERICALLY (milliseconds) — same trick as the static loop, so this
runs locally in minutes, no VM run needed.

Target {vacuum, horizon} → rediscover KERR  Δ = r² − 2Mr + a²  (a spinning black
hole, found from spec — the rotating analogue of 43's Schwarzschild rediscovery).

Run:  .venv/bin/python scripts/44_discover_rotating.py [--quick]
"""

import argparse
import importlib.util
import math
import os
import random
import sys
import time

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from gr_engine import Geometry, R_SYM
from analyzer import analyze, format_report

_g = importlib.util.spec_from_file_location("g3", os.path.join(_here, "03_rediscover.py"))
gp = importlib.util.module_from_spec(_g); sys.modules["g3"] = gp
_g.loader.exec_module(gp)               # rand_tree, to_sympy, size, mutate, crossover

r = R_SYM
A_VAL = 0.5                              # fixed spin for the search (a=1/2)
RS = [2.0, 3.0, 4.0, 6.0, 9.0]          # sample radii (Δ>0 region)
US = [0.0, 0.4, 0.8]                    # sample u = cosθ


def kerr_delta_metric(Dexpr):
    t, u, ph = sp.symbols("t u phi", real=True)
    a = sp.Symbol("a", positive=True)
    s2 = 1 - u**2
    Sig = r**2 + a**2 * u**2
    g = sp.zeros(4, 4)
    g[0, 0] = -(Dexpr - a**2 * s2) / Sig
    g[0, 3] = g[3, 0] = -a * s2 * (r**2 + a**2 - Dexpr) / Sig
    g[1, 1] = Sig / Dexpr
    g[2, 2] = Sig / s2
    g[3, 3] = s2 * ((r**2 + a**2)**2 - Dexpr * a**2 * s2) / Sig
    return g, [t, r, u, ph], a


def reduce_residual():
    """Reduce the Kerr-ansatz vacuum residual ONCE to numeric callables
    res(r, u, Δ, Δ', Δ'', a) — the cheap fitness ingredients."""
    D = sp.Function("Delta")
    g, coords, a = kerr_delta_metric(D(r))
    Ric = Geometry(g, coords).ricci
    u = coords[2]
    Dv, Dpv, Dppv, av = sp.symbols("Dv Dpv Dppv av")
    sub = {sp.Derivative(D(r), (r, 2)): Dppv, sp.Derivative(D(r), r): Dpv, D(r): Dv, a: av}
    funcs = []
    for i in range(4):
        for j in range(i, 4):
            comp = Ric[i, j]
            if comp == 0:
                continue
            expr = sp.cancel(sp.together(comp)).subs(sub)
            funcs.append(sp.lambdify((r, u, Dv, Dpv, Dppv, av), expr, "math"))
    return funcs


def fitness(tree, res_funcs):
    D = gp.to_sympy(tree)
    try:
        Dl = sp.lambdify(r, D, "math")
        Dpl = sp.lambdify(r, sp.diff(D, r), "math")
        Dppl = sp.lambdify(r, sp.diff(D, r, 2), "math")
    except Exception:
        return -9.0
    err = 0.0
    for rv in RS:
        try:
            Dv, Dpv, Dppv = Dl(rv), Dpl(rv), Dppl(rv)
        except Exception:
            return -9.0
        if not all(math.isfinite(x) for x in (Dv, Dpv, Dppv)) or abs(Dv) < 1e-6:
            return -9.0
        for uv in US:
            for f in res_funcs:
                try:
                    v = f(rv, uv, Dv, Dpv, Dppv, A_VAL)
                except Exception:
                    return -9.0
                if not math.isfinite(v):
                    return -9.0
                err += abs(v)
    score = 1.0 / (1.0 + err)                       # vacuum: residual → 0
    # horizon: Δ should have a real positive root (a black hole, not naked)
    vals = []
    for x in [0.1 * k for k in range(1, 120)]:
        try:
            vals.append(Dl(x))
        except Exception:
            pass
    flip = any(p * q < 0 for p, q in zip(vals, vals[1:]))
    score += 1.0 if flip else 0.0
    return score - 0.01 * gp.size(tree)


def evolve(res_funcs, seed=0, pop=260, gens=70, quick=False):
    if quick:
        pop, gens = 140, 35
    rng = random.Random(seed)
    P = [gp.rand_tree(rng, 4) for _ in range(pop)]
    best, bf = None, -9
    for gen in range(gens):
        scored = sorted(((fitness(t, res_funcs), t) for t in P), key=lambda x: x[0], reverse=True)
        if scored[0][0] > bf:
            bf, best = scored[0]
        if bf >= 1.95:                              # vacuum (residual→0) + horizon
            break
        elite = [t for _, t in scored[:max(2, pop // 10)]]
        P = list(elite)
        while len(P) < pop:
            a = min(rng.sample(scored, 3), key=lambda x: -x[0])[1]
            b = min(rng.sample(scored, 3), key=lambda x: -x[0])[1]
            c = gp.crossover(rng, a, b)
            if rng.random() < 0.4:
                c = gp.mutate(rng, c)
            P.append(c)
    return gp.to_sympy(best), bf, gen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    print("ROTATING DISCOVERY — invent a spinning black hole (rediscover Kerr)\n")

    t0 = time.time()
    print("  reducing the Kerr-ansatz vacuum residual once ...", flush=True)
    res_funcs = reduce_residual()
    print(f"  reduced to {len(res_funcs)} cheap residual formulas ({time.time()-t0:.1f}s)\n", flush=True)

    Dexpr, bf, gen = evolve(res_funcs, seed=3, quick=args.quick)
    Dexpr = sp.nsimplify(sp.expand(sp.simplify(Dexpr)), rational=True)
    print(f"  discovered Δ(r) = {Dexpr}   (fit {bf:.2f}, gen {gen}, {time.time()-t0:.1f}s)")
    print(f"  Kerr target (a=1/2): Δ = r² − 2M r + 1/4  →  a quadratic r² + (free)·r + 1/4")

    # verify: the discovered Δ in the full Kerr metric is genuinely vacuum + rotating
    g, coords, a = kerr_delta_metric(Dexpr.subs(R_SYM, r))
    rep = analyze(g.subs(a, sp.Rational(1, 2)), coords)
    print("\n  full report card of the discovered spinning metric:")
    print("\n".join("   " + ln for ln in format_report(rep).splitlines()))

    is_quadratic = sp.degree(sp.Poly(Dexpr, r)) == 2 if Dexpr.free_symbols <= {r} else False
    const_ok = sp.simplify(Dexpr.coeff(r, 0) - sp.Rational(1, 4)) == 0
    vacuum = "vacuum" in rep["made_of"]
    rotating = rep["horizon"] not in (None, []) and len(rep["symmetries"]) >= 2
    ok = vacuum and rotating and is_quadratic and const_ok
    print(f"\n  → quadratic Δ with a²=1/4 const: {is_quadratic and const_ok}; vacuum: {vacuum}; "
          f"rotating w/ horizon: {rotating}")
    print(f"\nROTATING DISCOVERY: {'PASSED ✅ (rediscovered Kerr from spec)' if ok else 'PARTIAL/❌'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
