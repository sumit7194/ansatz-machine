#!/usr/bin/env python3
"""Step 43 — DISCOVERY BY REPORT CARD (PLAN #3): the engine invents to spec.

The culmination. The analyzer DESCRIBES a metric you hand it; this flips it —
you describe the report card you WANT, and the genetic loop (reused from 03)
searches rational f(r) for a metric whose report matches. The analyzer becomes
the fitness judge, closing the circle back to the project's original
propose→verify→evolve loop, now driven by physical PROPERTIES instead of a
residual.

Search space: the static round ansatz ds² = −f dt² + dr²/f + r²dΩ² (so it invents
static, spherical spacetimes — rotating discovery is the later, heavier VM run).

Fitness is LIGHT: the energy density and pressures reduce to closed formulas in
(f, f', f''), evaluated numerically per candidate (milliseconds) — only the boxes
the target asks for are scored. The FULL report is run once, on the winner.

  ρ   = (1 − f − r f') / r²          (8π=1 units)
  p_r = −ρ                           (automatic for g_tt = −1/g_rr)
  p_t = (r f'' + 2 f') / (2r)

Two stages:
  (1) target {vacuum, horizon}            → rediscover SCHWARZSCHILD.
  (2) target {physical, horizon, timelike singularity}
                                          → invent a SURVIVABLE (charge-like)
      black hole: the engine must add a +c/r² term so the singularity is timelike
      (avoidable) — discovering, from a physical WISH, the charge that grants it.

Run:  .venv/bin/python scripts/43_discover.py [--quick]
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
from gr_engine import R_SYM
from analyzer import analyze, format_report

_g = importlib.util.spec_from_file_location("g3", os.path.join(_here, "03_rediscover.py"))
gp = importlib.util.module_from_spec(_g)
sys.modules["g3"] = gp
_g.loader.exec_module(gp)        # rand_tree, to_sympy, size, mutate, crossover

r = R_SYM
RS = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0]          # sample radii for ρ, p_t
RH = [0.2 * k for k in range(1, 60)]              # finer scan for a horizon
R0 = 0.03                                         # near the centre (singularity probe)


def _callables(tree):
    """Numeric f, f', f'' from a candidate tree (None if it won't lambdify)."""
    f = gp.to_sympy(tree)
    try:
        fl = sp.lambdify(r, f, "math")
        fpl = sp.lambdify(r, sp.diff(f, r), "math")
        fppl = sp.lambdify(r, sp.diff(f, r, 2), "math")
        return f, fl, fpl, fppl
    except Exception:
        return None


def _ev(fn, x):
    try:
        v = fn(x)
        return v if math.isfinite(v) else None
    except Exception:
        return None


def fitness(tree, target):
    """Continuous score: how well the candidate's (cheap) report matches `target`.
    target is a subset of {'vacuum','physical','horizon','timelike','spacelike'}."""
    c = _callables(tree)
    if c is None:
        return -1.0
    f, fl, fpl, fppl = c
    score = 0.0

    def rho_pt(x):
        fv, fp, fpp = _ev(fl, x), _ev(fpl, x), _ev(fppl, x)
        if None in (fv, fp, fpp):
            return None
        return (1 - fv - x * fp) / x**2, (x * fpp + 2 * fp) / (2 * x)

    if "vacuum" in target:                         # reward ρ,p_t → 0
        err = 0.0
        for x in RS:
            rp = rho_pt(x)
            if rp is None:
                return -1.0
            err += abs(rp[0]) + abs(rp[1])
        score += 1.0 / (1.0 + err)

    if "physical" in target:                       # fraction of EC that hold
        ok = tot = 0
        for x in RS:
            rp = rho_pt(x)
            if rp is None:
                return -1.0
            rho, pt = rp
            for cond in (rho >= -1e-9, rho + pt >= -1e-9, rho - abs(pt) >= -1e-9, pt >= -1e-9):
                tot += 1
                ok += int(cond)
        score += ok / tot

    if "horizon" in target:                        # f changes sign (a real horizon)
        vals = [_ev(fl, x) for x in RH]
        vals = [v for v in vals if v is not None]
        flip = any(a * b < 0 for a, b in zip(vals, vals[1:]))
        score += 1.0 if flip else 0.5 / (1.0 + min((abs(v) for v in vals), default=9))

    if "timelike" in target or "spacelike" in target:   # singularity character: sign of f→r=0
        f0 = _ev(fl, R0)
        want_pos = "timelike" in target
        if f0 is None:
            score += 0.0
        elif (f0 > 5) == want_pos and abs(f0) > 5:
            score += 1.0
        else:
            score += 0.0

    if "asymptotic" in target:                     # asymptotically flat: f → 1 far away
        fbig = _ev(fl, 1e3)
        score += 1.0 / (1.0 + abs(fbig - 1.0)) if fbig is not None else 0.0

    return score - 0.01 * gp.size(tree)            # mild parsimony


def evolve(target, seed=0, pop_size=240, gens=60, quick=False):
    if quick:
        pop_size, gens = 120, 30
    rng = random.Random(seed)
    pop = [gp.rand_tree(rng, 4) for _ in range(pop_size)]
    n_box = len(set(target) & {"vacuum", "physical", "horizon", "timelike", "spacelike", "asymptotic"})
    best, best_fit = None, -9
    for gen in range(gens):
        scored = sorted(((fitness(ind, target), ind) for ind in pop),
                        key=lambda t: t[0], reverse=True)
        if scored[0][0] > best_fit:
            best_fit, best = scored[0]
        if best_fit >= n_box - 0.05:               # all boxes essentially ticked
            break
        elite = [ind for _, ind in scored[:max(2, pop_size // 10)]]
        nxt = list(elite)
        while len(nxt) < pop_size:
            a = min(rng.sample(scored, 3), key=lambda t: -t[0])[1]
            b = min(rng.sample(scored, 3), key=lambda t: -t[0])[1]
            child = gp.crossover(rng, a, b)
            if rng.random() < 0.4:
                child = gp.mutate(rng, child)
            nxt.append(child)
        pop = nxt
    return gp.to_sympy(best), best_fit, gen


def run_stage(name, target, coords_label, want, seed, quick):
    print(f"\n── {name} — target: {{{', '.join(target)}}} ──")
    t0 = time.time()
    fexpr, fit, gen = evolve(target, seed=seed, quick=quick)
    fexpr = sp.nsimplify(sp.simplify(fexpr), rational=True)
    print(f"   discovered f(r) = {fexpr}   (fit {fit:.2f}, gen {gen}, {time.time()-t0:.1f}s)")
    t, th, ph = sp.symbols("t theta phi", real=True)
    g = sp.diag(-fexpr, 1 / fexpr, r**2, r**2 * sp.sin(th)**2)
    rep = analyze(g, [t, r, th, ph])
    print("   full report card:")
    print("\n".join("   " + ln for ln in format_report(rep).splitlines()))
    ok = want(rep, fexpr)
    print(f"   → {name}: {'✅ matches the spec' if ok else '❌ off-spec'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    print("DISCOVERY BY REPORT CARD — the engine invents to spec")

    # Stage 1: vacuum + horizon (+asymptotically flat) → Schwarzschild
    ok1 = run_stage(
        "Stage 1 (rediscover Schwarzschild)", ["vacuum", "horizon", "asymptotic"], None,
        lambda R, f: ("vacuum" in R["made_of"] and R["horizon"] not in (None, [])),
        seed=1, quick=args.quick)

    # Stage 2: asymptotically-flat + physical + horizon + timelike singularity
    #          → invent a SURVIVABLE (charge-like) black hole
    ok2 = run_stage(
        "Stage 2 (invent a survivable black hole)",
        ["asymptotic", "physical", "horizon", "timelike"], None,
        lambda R, f: (R["horizon"] not in (None, [])
                      and any("timelike" in ch for *_, ch in R["causal"]["singularity_character"])),
        seed=2, quick=args.quick)

    passed = ok1 and ok2
    print(f"\nDISCOVERY: {'PASSED ✅' if passed else 'PARTIAL/❌'}  "
          "(report-card-driven search: rediscovers Schwarzschild, invents a survivable hole)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
