#!/usr/bin/env python3
"""Step 08 — the STATIONARY hall: first off-diagonal ansatz.

Ansatz (2+1, rational in r — D4):
    ds² = -f(r)·dt² + dr²/h(r) + r²·(dφ + ω(r)·dt)²
i.e. g_tt = -f + r²ω², g_tφ = r²ω, g_φφ = r², g_rr = 1/h.
Three independent genomes (f, h, ω). The known answer in this hall is the
ROTATING BTZ black hole (Λ<0): f = h = r²/ℓ² - M + J²/(4r²), ω = -J/(2r²).

Why this hall matters: it is the training ground for everything the
Kerr-shaped mansion needs — off-diagonal REDUCE, multi-function genomes,
and the frame-gauge subtlety (a CONSTANT ω is pure gauge: φ' = φ + ωt
absorbs it, so the loop must be forced to hunt non-constant ω).

Honest expectations, stated up front:
 - Any verified solution here is locally AdS₃ (2+1 has no local degrees of
   freedom), so the fingerprint's verdict will be BLIND_SPOT — correct and
   permanent. The win condition is a VERIFIED solution with genuinely
   non-constant ω: the rotating-BTZ family, machine-found.
 - If every seed stagnates, that is the D12 trigger for island-model GP —
   a measured result, not a failure to hide.

Battery: (1) ground truth — rotating BTZ verifies through the engine,
sabotaged rotation is rejected; (2) the hunt.

Run:  .venv/bin/python scripts/08_stationary.py [--quick]
"""

import argparse
import importlib.util
import os
import random
import time

import sympy as sp

from gr_engine import Geometry, verify, VERIFIED, REJECTED, R_SYM

_here = os.path.dirname(os.path.abspath(__file__))


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(_here, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fp = _load("fingerprints", "02_fingerprints.py")
rd = _load("rediscover", "03_rediscover.py")
gen5 = _load("generalize", "05_generalize.py")

SAMPLE_R = rd.SAMPLE_R
PROMOTE_TOL = rd.PROMOTE_TOL
PARSIMONY = rd.PARSIMONY
INF = float("inf")
LAMBDA = sp.Integer(-1)  # ℓ = 1 throughout this hall


def build_metric(fexpr, hexpr, wexpr):
    t, ph = sp.symbols("t phi", real=True)
    g = sp.zeros(3, 3)
    g[0, 0] = -fexpr + R_SYM**2 * wexpr**2
    g[0, 2] = g[2, 0] = R_SYM**2 * wexpr
    g[1, 1] = 1 / hexpr
    g[2, 2] = R_SYM**2
    return g, [t, R_SYM, ph]


def reduce_ansatz3():
    F = sp.Function("F")(R_SYM)
    H = sp.Function("H")(R_SYM)
    W = sp.Function("W")(R_SYM)
    metric, coords = build_metric(F, H, W)
    geo = Geometry(metric, coords)
    residual = geo.vacuum_residual(LAMBDA)

    syms = sp.symbols("s0 s1 s2 u0 u1 u2 v0 v1 v2")
    rep = {}
    for fn, (a0, a1, a2) in ((F, syms[0:3]), (H, syms[3:6]), (W, syms[6:9])):
        rep[sp.Derivative(fn, (R_SYM, 2))] = a2
        rep[sp.Derivative(fn, R_SYM)] = a1
        rep[fn] = a0

    seen, funcs, sym_res = set(), [], []
    for i in range(3):
        for j in range(i, 3):
            expr = residual[i, j]
            if expr == 0:
                continue
            simplified = sp.simplify(expr)
            key = sp.srepr(simplified.xreplace(rep))
            if key in seen:
                continue
            seen.add(key)
            sym_res.append(simplified)  # still in terms of F, H, W
            funcs.append(sp.lambdify((R_SYM,) + syms,
                                     simplified.xreplace(rep),
                                     modules="math"))
    return funcs, sym_res, (F, H, W)


# ---------------------------------------------------------------------------
# Fitness over the triple genome (generic over slot count)
# ---------------------------------------------------------------------------

def make_fitness3(res_funcs):
    cache = {}

    def compile_tree(tree):
        e = rd.to_sympy(tree)
        e1 = sp.diff(e, R_SYM)
        e2 = sp.diff(e1, R_SYM)
        return tuple(sp.lambdify(R_SYM, x, modules="math")
                     for x in (e, e1, e2))

    def fitness(triple):
        if triple in cache:
            return cache[triple]
        try:
            fns = [compile_tree(tr) for tr in triple]
            total = 0.0
            vals = [[], [], []]
            for rv in SAMPLE_R:
                args = [rv]
                for k in range(3):
                    v0, v1, v2 = fns[k][0](rv), fns[k][1](rv), fns[k][2](rv)
                    args += [v0, v1, v2]
                    vals[k].append(v0)
                if abs(args[1]) < 1e-12 or abs(args[4]) < 1e-12:
                    raise ZeroDivisionError  # f or h vanishing at sample
                for rf in res_funcs:
                    total += abs(rf(*args))
                    if total > 1e12:
                        raise OverflowError
            raw = total / len(SAMPLE_R)
            # constant ω is pure frame gauge (φ' = φ + ωt) — without this
            # penalty the loop wins with non-rotating BTZ + ω=0 forever
            if max(vals[2]) - min(vals[2]) < 1e-9:
                raw += 1.0
            # ...and NEGLIGIBLE ω is the measured gauge-evasion exploit:
            # the loop made ω ≈ tiny/r (non-constant, physically nothing)
            # and converged to the non-rotating solution anyway; the
            # finisher then solved onto the ω=const branch every time.
            # Demand rotation you could measure.
            if max(abs(v) for v in vals[2]) < 1e-2:
                raw += 1.0
            # f and h both constant: no solution lives there in this hall
            if max(vals[0]) - min(vals[0]) < 1e-9 \
                    and max(vals[1]) - min(vals[1]) < 1e-9:
                raw += 1.0
        except (ZeroDivisionError, OverflowError, ValueError, TypeError):
            raw = INF
        out = (raw, raw + PARSIMONY * sum(rd.size(tr) for tr in triple)
               if raw < INF else INF)
        cache[triple] = out
        return out

    return fitness


# ---------------------------------------------------------------------------
# The algebraic finisher: GP finds the structure, algebra nails the constants
# ---------------------------------------------------------------------------
# Measured failure that bought this: hunts converged steadily into the right
# basin (residuals 5e-6) and stalled — constant-jitter mutation is a poor
# local optimizer when constants are CORRELATED across slots (rotating BTZ
# needs J²/4 in f and J/2 in ω). So: symbolize every numeric constant in a
# near-miss, substitute the family into the symbolic residuals, demand each
# residual vanish identically in r (polynomial coefficients = 0), and let
# sp.solve deliver the exact constants.

from finisher import snap_constants, structure_sig  # noqa: E402

SNAP_TOL = 1e-2


# ---------------------------------------------------------------------------
# The loop (k-slot genome, k=3)
# ---------------------------------------------------------------------------

def hunt(label, catalog, seed=0, pop_size=500, max_gen=300,
         stagnation_gens=40, verbose=True):
    rng = random.Random(seed)
    t0 = time.time()
    if verbose:
        print(f"\n—— {label} (seed {seed}) ——")
    res_funcs, sym_res, FHW = reduce_ansatz3()
    fit = make_fitness3(res_funcs)
    if verbose:
        print(f"   REDUCE done ({time.time() - t0:.1f}s)")

    K = 3

    def rand_genome():
        return tuple(rd.rand_tree(rng, 4) for _ in range(K))

    def promote(eF, eH, eW, gen, note=""):
        """Symbolic proof + novelty check on exact (f, h, ω)."""
        try:
            metric, coords = build_metric(eF, eH, eW)
            verdict, detail = verify(metric, coords, params=[],
                                     Lambda=LAMBDA)
        except Exception:
            return None  # degenerate metric (singular inverse etc.)
        if verdict != VERIFIED:
            if verbose:
                print(f"   ↩ promotion failed ({verdict}){note}")
            return None
        if not eW.has(R_SYM):
            if verbose:
                print("   ↩ constant ω (frame gauge) — trivial")
            return None
        geo = Geometry(metric, coords)
        cls, cdetail = fp.classify(geo, catalog)
        dt = time.time() - t0
        if verbose:
            print(f"   ✅ VERIFIED rotating solution ({detail}){note}")
            print(f"   🔎 NOVELTY: {cls} — {cdetail}")
        return {"label": label, "f": eF, "h": eH, "w": eW,
                "class": cls, "class_detail": cdetail,
                "gen": gen, "time": dt}

    pop = [rand_genome() for _ in range(pop_size)]
    tried = set()
    snapped = set()
    stag_best, stag_n = INF, 0

    for gen in range(max_gen):
        scored = sorted(((fit(g), g) for g in pop), key=lambda x: x[0][1])
        (best_raw, _), best = scored[0]

        if best_raw < PROMOTE_TOL and best not in tried:
            tried.add(best)
            eF, eH, eW = [sp.simplify(sp.together(rd.to_sympy(tr)))
                          for tr in best]
            if verbose:
                print(f"   gen {gen:3d}: numeric hit  f={eF}  h={eH}  "
                      f"ω={eW}  ({best_raw:.1e}) — promoting...")
            out = promote(eF, eH, eW, gen)
            if out:
                return out

        # the algebraic finisher: near-miss structure -> exact constants
        if PROMOTE_TOL <= best_raw < SNAP_TOL:
            exprs = [rd.to_sympy(tr) for tr in best]
            sig = structure_sig(exprs)
            if sig not in snapped:
                snapped.add(sig)
                if verbose:
                    print(f"   gen {gen:3d}: near-miss ({best_raw:.1e}) — "
                          "snapping constants algebraically...")
                for eF, eH, eW in snap_constants(exprs, sym_res, FHW):
                    out = promote(sp.simplify(eF), sp.simplify(eH),
                                  sp.simplify(eW), gen, note=" [snapped]")
                    if out:
                        return out

        if verbose and gen % 20 == 0:
            print(f"   gen {gen:3d}: best {best_raw:.3e}")

        if best_raw < stag_best * 0.99:
            stag_best, stag_n = best_raw, 0
        else:
            stag_n += 1
            if stag_n >= stagnation_gens:
                if verbose:
                    print(f"   ⏹ stagnant at {best_raw:.3e} (gen {gen}) — "
                          "restarting")
                return None

        elites = [g for _, g in scored[:max(2, pop_size // 50)]]
        newpop = list(elites)

        def tournament():
            return scored[min(rng.sample(range(len(scored)), 5))][1]

        while len(newpop) < pop_size:
            roll = rng.random()
            if roll < 0.50:
                a, b = tournament(), tournament()
                child = tuple(rd.crossover(rng, a[i], b[i])
                              if rng.random() < 0.7 else a[i]
                              for i in range(K))
            elif roll < 0.80:
                a = tournament()
                slot = rng.randint(0, K - 1)
                child = tuple(rd.mutate(rng, a[i]) if i == slot else a[i]
                              for i in range(K))
            elif roll < 0.94:
                # gene duplication across slots (D10) — here it also
                # carries the J-correlation between f and ω terms
                a = tournament()
                src, dst = rng.sample(range(K), 2)
                lst = list(a)
                if rng.random() < 0.5:
                    lst[dst] = a[src]
                else:
                    lst[dst] = rd.crossover(rng, a[dst], a[src])
                child = tuple(lst)
            else:
                child = rand_genome()
            if all(rd.size(tr) <= 25 for tr in child):
                newpop.append(child)
        pop = newpop

    if verbose:
        print(f"   ✗ no exact hit in {max_gen} generations")
    return None


# ---------------------------------------------------------------------------
# Battery
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    kw = dict(pop_size=200, max_gen=100) if args.quick else {}

    results = []

    print("== Ground truth: the engine must handle off-diagonal 2+1 ==")
    M, J = sp.Rational(1), sp.Rational(4, 5)
    fb = R_SYM**2 - M + J**2 / (4 * R_SYM**2)
    wb = -J / (2 * R_SYM**2)
    metric, coords = build_metric(fb, fb, wb)
    verdict, detail = verify(metric, coords, Lambda=LAMBDA)
    ok = verdict == VERIFIED
    results.append(ok)
    print(f"  {'✓' if ok else '✗✗'} rotating BTZ (M=1, J=4/5): {verdict} "
          f"({detail})")

    # sabotage: wrong frame-dragging falloff (ω ∝ 1/r³)
    wbad = -J / (2 * R_SYM**3)
    metric, coords = build_metric(fb, fb, wbad)
    verdict, detail = verify(metric, coords, Lambda=LAMBDA)
    ok = verdict == REJECTED
    results.append(ok)
    print(f"  {'✓' if ok else '✗✗'} sabotaged rotation (ω∝1/r³): {verdict} "
          f"({detail})")

    print("\n== The hunt: find a rotating vacuum solution blind ==")
    catalog = fp.build_catalog()
    res = None
    for seed in (0, 1, 2, 3, 4, 5):
        res = hunt("rotating hall 2+1, Λ=-1", catalog, seed=seed, **kw)
        if res:
            break
    if res:
        ok = res["class"] == fp.BLIND_SPOT and res["w"].has(R_SYM)
        results.append(ok)
        print(f"\n  {'✅' if ok else '❌'} FOUND rotating solution "
              f"[gen {res['gen']}, {res['time']:.1f}s]:")
        print(f"     f = {res['f']}")
        print(f"     h = {res['h']}")
        print(f"     ω = {res['w']}")
        print(f"     verdict: VERIFIED + {res['class']} (correct for 2+1 — "
              "locally AdS₃, rotation is global structure)")
    else:
        results.append(False)
        print("\n  ❌ all seeds stagnated — D12 trigger: build island-model "
              "GP before re-attempting (this is a measured result; "
              "record it in the journal)")

    print(f"\n{'ALL EXPECTATIONS MET ✅' if all(results) else 'EXPECTATION FAILURES ❌'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
