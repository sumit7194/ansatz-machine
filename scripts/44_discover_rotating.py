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


def reduce_residual_charged(Q_val):
    """Einstein–Maxwell residual for the Kerr-Δ ansatz + the Kerr–Newman EM field
    (charge Q_val fixed), reduced to numeric res(r,u,Δ,Δ',Δ'',a) — the charged
    analogue. Vanishes at Δ = r²−2Mr+a²+Q²."""
    mx_s = importlib.util.spec_from_file_location("mx", os.path.join(_here, "28_maxwell.py"))
    mx = importlib.util.module_from_spec(mx_s); mx_s.loader.exec_module(mx)
    D = sp.Function("Delta")
    g, coords, a = kerr_delta_metric(D(r))
    geo = Geometry(g, coords)
    u = coords[2]
    s2 = 1 - u**2
    Sig = r**2 + a**2 * u**2
    Q = sp.Symbol("Q", positive=True)
    A = [-Q * r / Sig, 0, 0, Q * r * a * s2 / Sig]        # Kerr–Newman potential
    F = mx.faraday(A, coords)
    res_mat = geo.ricci - 2 * mx.em_stress(geo, F)        # R_ab − κT_ab[F], κ=2
    Dv, Dpv, Dppv, av = sp.symbols("Dv Dpv Dppv av")
    sub = {sp.Derivative(D(r), (r, 2)): Dppv, sp.Derivative(D(r), r): Dpv,
           D(r): Dv, a: av, Q: Q_val}
    funcs = []
    for i in range(4):
        for j in range(i, 4):
            comp = res_mat[i, j]
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


def _quadratic_const(D, const):
    """True iff D(r) is a quadratic in r with constant term == const."""
    if D.free_symbols - {r}:
        return False
    try:
        return sp.degree(sp.Poly(D, r)) == 2 and sp.simplify(D.coeff(r, 0) - const) == 0
    except Exception:
        return False


def _discover(label, res_funcs, t0, seed, quick):
    D, bf, gen = evolve(res_funcs, seed=seed, quick=quick)
    D = sp.nsimplify(sp.expand(sp.simplify(D)), rational=True)
    print(f"  [{label}] discovered Δ(r) = {D}   (fit {bf:.2f}, gen {gen}, {time.time()-t0:.1f}s)")
    return D


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    print("ROTATING DISCOVERY — invent spinning black holes from spec\n")
    t0 = time.time()

    # Stage 1: VACUUM → Kerr.  a=1/2 ⇒ const a² = 1/4
    print("  reducing the vacuum residual once ...", flush=True)
    res_v = reduce_residual()
    print(f"  → {len(res_v)} cheap formulas ({time.time()-t0:.1f}s)", flush=True)
    Dk = _discover("Kerr", res_v, t0, seed=3, quick=args.quick)
    g, coords, a = kerr_delta_metric(Dk)
    rep = analyze(g.subs(a, sp.Rational(1, 2)), coords)
    nh = len(rep["horizon"]) if rep["horizon"] not in (None, []) else 0
    print(f"     analyzer: {rep['made_of']} | {len(rep['symmetries'])} Killing vectors | {nh} horizons")
    ok1 = ("vacuum" in rep["made_of"] and _quadratic_const(Dk, sp.Rational(1, 4))
           and len(rep["symmetries"]) >= 2 and nh == 2)

    # Stage 2: CHARGED (Kerr–Newman EM field, Q=1/2) → Kerr–Newman.  const a²+Q² = 1/4+1/4 = 1/2
    Qc = sp.Rational(1, 2)
    print("\n  reducing the charged (Einstein–Maxwell) residual once ...", flush=True)
    res_c = reduce_residual_charged(Qc)
    print(f"  → {len(res_c)} cheap formulas ({time.time()-t0:.1f}s)", flush=True)
    Dkn = _discover("Kerr–Newman", res_c, t0, seed=5, quick=args.quick)
    const_kn = sp.Rational(1, 4) + Qc**2
    got = Dkn.coeff(r, 0) if Dkn.free_symbols <= {r} else "?"
    ok2 = _quadratic_const(Dkn, const_kn)
    print(f"     target Δ = r²−2Mr+a²+Q² ⇒ const a²+Q² = {const_kn}; got {got}  "
          f"→ {'✓ Kerr–Newman (charge adds Q² to Δ)' if ok2 else '✗'}")

    passed = ok1 and ok2
    print(f"\nROTATING DISCOVERY: "
          f"{'PASSED ✅ (rediscovered Kerr AND Kerr–Newman from spec)' if passed else 'PARTIAL/❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
