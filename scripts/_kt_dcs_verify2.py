#!/usr/bin/env python3
"""Independent check of the O(zeta chi^2) dCS solution: back-substitute and demand zero.  (step 4b)

WHY THIS EXISTS. linsolve returning a solution is not evidence that the solution solves anything --
today alone this build produced a PASS on a result of zero and a NO SOLUTION for a solvable system,
both from scaffolding rather than physics. So the solution is fed back into the ORIGINAL residuals.

AND THE FREE PARAMETERS ARE SET RANDOMLY, which is the second test. The solve left ~30 coefficients
undetermined; the claim is that these are pure GAUGE (the ansatz deliberately did not fix a gauge).
If that is right, ANY values satisfy the field equations. If the solver was sloppy, random values
break it. A verification that reuses the solver's own convenient choice would not distinguish the two.

Repro:  .venv/bin/python scripts/_kt_dcs_verify2.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from _kt_dcs_metric2 import even_ansatz, r, th, subs_series  # noqa: E402
from _kt_dcs_order2 import build_source, chi2_part  # noqa: E402

M = sp.Symbol("M", positive=True)
KMAX = 12

if __name__ == "__main__":
    t0 = time.time()
    _, fs = even_ansatz()
    lines = open("data/dcs_lhs_srepr.txt").read().strip().split("\n")
    L, comps = {}, []
    for k in range(0, len(lines), 2):
        i, j = (int(v) for v in lines[k].split())
        L[(i, j)] = sp.sympify(lines[k + 1])
        comps.append((i, j))
    print(f"loaded LHS, components {comps}", flush=True)

    c2 = sp.Symbol("c2")
    ser, unk = {}, []
    for n in fs:
        cs = sp.symbols(f"{n}_0:{KMAX}")
        unk += list(cs)
        ser[n] = sum(cs[k] / r**(k + 1) for k in range(KMAX))

    Cs, Ts = build_source(verbose=False)
    u, sv = sp.Symbol("u"), sp.Symbol("sv")
    S_, C_ = sp.sin(th), sp.cos(th)

    def ang(num):
        e = sp.expand(sp.expand_trig(sp.sympify(num)).subs({S_: sv, C_: u}))
        A = B = sp.S.Zero
        for (k,), coef in sp.Poly(e, sv).terms():
            t_ = sp.expand(coef * (1 - u**2) ** (k // 2))
            B, A = (B + t_, A) if k % 2 else (B, A + t_)
        out = []
        for part in (sp.expand(A), sp.expand(B)):
            if part != 0:
                out += list(sp.Poly(part, u, r).coeffs())
        return out

    resid = {}
    eqs = []
    for i, j in comps:
        lhs = subs_series(L[(i, j)], fs, ser)
        rhs = chi2_part(Cs[i, j]) + c2 * chi2_part(Ts[i, j])
        resid[(i, j)] = sp.cancel(sp.together(lhs - rhs))
        eqs += ang(sp.expand(sp.numer(resid[(i, j)])))
    eqs = [e for e in eqs if e != 0]
    A_, b_ = sp.linear_eq_to_matrix(eqs, unk + [c2])
    sol = list(sp.linsolve((A_, b_), unk + [c2]))[0]
    subs0 = dict(zip(unk + [c2], sol))
    free = sorted({s for v in sol for s in v.free_symbols} & set(unk), key=str)
    print(f"{len(eqs)} equations, {len(unk)+1} unknowns, {len(free)} free (gauge) parameters",
          flush=True)
    print(f"c2 = {sp.nsimplify(subs0[c2])}", flush=True)

    rng = sp.Rational
    for trial, seed in enumerate((rng(3, 7), rng(-5, 4), rng(11, 2))):
        gauge = {s: seed * (1 + k) * M**0 for k, s in enumerate(free)}
        full = {k_: sp.simplify(v.subs(gauge)) for k_, v in subs0.items()}
        full.update(gauge)
        bad = []
        for i, j in comps:
            e = sp.cancel(sp.together(resid[(i, j)].subs(full)))
            e = sp.simplify(e.subs(M, 1).subs(th, sp.acos(rng(1, 3))).subs(r, rng(7, 2)))
            if abs(sp.N(e, 40)) > sp.Float("1e-30"):
                bad.append(((i, j), sp.N(e, 8)))
        print(f"  gauge trial {trial} (seed {seed}): "
              + ("ALL FIVE RESIDUALS ZERO" if not bad else f"NONZERO {bad}"), flush=True)
    print(f"\ntotal {time.time()-t0:.0f}s")
