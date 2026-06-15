#!/usr/bin/env python3
"""Step 29 — MATTER METER: count hair of a SOURCED solution.

The information meter (26) was vacuum-only. This generalizes it: given any
set of residual expressions that must vanish for a solution (Einstein-with-
source components, field EOMs, Maxwell divergences), count how many of the
solution's constants are genuinely FREE (primary hair) vs SECONDARY
(determined by the free ones — the surprise we're hunting) vs FORCED.

Same glass-box method as 26: demand every residual ≡ 0, reduce to equations
on the constants, solve, count survivors. The point of building it: on the
dilaton (EMD) black hole the dilaton charge is SECONDARY — and this meter
should catch that, the first non-trivial hair reading of the project.

This run validates on Reissner–Nordström: M and Q are both PRIMARY ⇒ reads 2.

Run:  .venv/bin/python scripts/29_matter_meter.py
"""

import importlib.util
import os
import sys

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from gr_engine import Geometry, build_ansatz_metric, R_SYM

_mx = importlib.util.spec_from_file_location("mx", os.path.join(_here, "28_maxwell.py"))
maxwell = importlib.util.module_from_spec(_mx); _mx.loader.exec_module(maxwell)


def count_free_matter(coords, residuals, consts):
    """residuals: list of expressions that must ≡0. consts: candidate
    constants. Returns (num_free, {const: classification})."""
    angles = coords[2:]
    asub = {a: sp.atan(sp.Rational(3, 4)) for a in angles}
    eqs = set()
    for comp in residuals:
        comp = sp.expand_trig(comp.subs(asub)) if angles else comp
        if comp == 0:
            continue
        num, _ = sp.fraction(sp.together(comp))
        num = sp.expand(num)
        try:
            poly = sp.Poly(num, R_SYM)
            for c in poly.all_coeffs():
                if c != 0:
                    eqs.add(sp.expand(c))
        except sp.PolynomialError:
            if num != 0:
                eqs.add(num)
    eqs = list(eqs)
    if not eqs:
        return len(consts), {c: "free (hair)" for c in consts}
    sol = sp.solve(eqs, list(consts), dict=True)
    if not sol:
        return 0, {c: "no consistent solution" for c in consts}
    s = sol[0]
    free = [c for c in consts if c not in s]
    cls = {}
    for c in consts:
        if c in free:
            cls[c] = "free (hair)"
        else:
            val = sp.simplify(s[c])
            cls[c] = (f"secondary (= {val})" if val.free_symbols & set(free)
                      else f"forced (= {val})")
    return len(free), cls


def rn_residuals(M, Q, kappa=sp.Integer(2)):
    t, r = sp.Symbol("t", real=True), R_SYM
    f = 1 - 2 * M / r + Q**2 / r**2
    metric, coords, _ = build_ansatz_metric(4, f)
    geo = Geometry(metric, coords)
    F = maxwell.faraday([Q / r, 0, 0, 0], coords)
    T = maxwell.em_stress(geo, F)
    res = geo.ricci - kappa * T
    comps = [res[i, j] for i in range(4) for j in range(i, 4)]
    comps += maxwell.maxwell_div(geo, F)
    return coords, comps


def main():
    M, Q = sp.symbols("M Q", positive=True)
    print("MATTER METER — validation on Reissner–Nordström\n")
    coords, residuals = rn_residuals(M, Q)
    nfree, cls = count_free_matter(coords, residuals, [M, Q])
    print(f"  RN hair count = {nfree}  (expected 2: mass + charge)")
    for c, k in cls.items():
        print(f"    {c}: {k}")
    passed = (nfree == 2)
    print(f"\nMATTER METER: {'PASSED ✅' if passed else 'FAILED ❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
