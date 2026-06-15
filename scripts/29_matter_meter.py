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


UNKNOWN = None  # three-valued: a hair count of None means "could not measure"


def _clean_polynomial(num, consts):
    """True iff `num` is a clean polynomial in r with coefficients only in
    the candidate constants — i.e. we can honestly extract constraints from
    it. Transcendental/branch residue (log, exp, Abs, re/im, Piecewise),
    fractional powers of r, or stray symbols ⇒ NOT clean ⇒ the meter must
    say UNKNOWN rather than silently over-count."""
    bad = (sp.log, sp.exp, sp.Abs, sp.Piecewise, sp.re, sp.im)
    if any(num.has(b) for b in bad):
        return False
    if not num.is_polynomial(R_SYM):
        return False
    if num.free_symbols - set(consts) - {R_SYM}:
        return False
    return True


def count_free_matter(coords, residuals, consts):
    """Three-valued hair count. Returns (n, cls) with n = number of genuinely
    free constants, or n = UNKNOWN (None) if the meter cannot honestly decide
    — extraction choked on a transcendental/fractional residual, or solve
    failed. NEVER reports a count it isn't sure of (the over-count trap)."""
    angles = coords[2:]
    asub = {a: sp.atan(sp.Rational(3, 4)) for a in angles}
    eqs = set()
    for comp in residuals:
        comp = sp.expand_trig(comp.subs(asub)) if angles else comp
        if comp == 0:
            continue
        num, _ = sp.fraction(sp.together(comp))
        num = sp.expand(num)
        if not _clean_polynomial(num, consts):
            return UNKNOWN, {c: "UNKNOWN — non-polynomial/transcendental "
                             "residual (declared blind spot; rationalize first)"
                             for c in consts}
        for c in sp.Poly(num, R_SYM).all_coeffs():
            if c != 0:
                eqs.add(sp.expand(c))
    eqs = list(eqs)
    if not eqs:               # clean AND no constraints ⇒ genuinely all free
        return len(consts), {c: "free (hair)" for c in consts}
    # Positive-dimensional variety: greedily eliminate determined constants.
    # A solve that ERRORS (not merely "no solution") is a blind spot, not
    # evidence of freedom — so it forces UNKNOWN rather than padding the count.
    free = list(consts)
    determined = {}
    work = list(eqs)
    progress = True
    while progress and work:
        progress = False
        for c in reversed(free):   # eliminate caller's later (candidate-derived) consts first
            try:
                sols = sp.solve(work, c, dict=True)
            except Exception:
                return UNKNOWN, {k: "UNKNOWN — solve failure (blind spot)"
                                 for k in consts}
            if sols and c in sols[0]:
                val = sols[0][c]
                determined[c] = val
                free.remove(c)
                work = [w for w in (sp.simplify(e.subs(c, val)) for e in work)
                        if w != 0]
                progress = True
                break
    cls = {}
    for c in consts:
        if c in free:
            cls[c] = "free (hair)"
        else:
            val = sp.simplify(determined[c])
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
    r = R_SYM
    print("MATTER METER — validation\n")

    # (1) clean physical case: RN → 2 primary hairs
    coords, residuals = rn_residuals(M, Q)
    nfree, cls = count_free_matter(coords, residuals, [M, Q])
    print(f"  RN hair count = {nfree}  (expected 2: mass + charge)")
    for c, k in cls.items():
        print(f"    {c}: {k}")
    ok_rn = (nfree == 2)

    # (2) HONESTY gate — the meter must say UNKNOWN, never over-count, when it
    # cannot honestly reduce the residual. Genuine choke cases:
    g = sp.Symbol("g")
    coords4 = [sp.Symbol("t", real=True), r, sp.Symbol("th", real=True), sp.Symbol("ch", real=True)]
    frac = [M * r**g - Q]                 # fractional/symbolic power of r
    logr = [M * sp.log(r) - Q]            # transcendental in r
    n_frac, _ = count_free_matter(coords4, frac, [M, Q])
    n_log, _ = count_free_matter(coords4, logr, [M, Q])
    print(f"\n  honesty: fractional-power residual → {n_frac}  "
          f"({'✅ UNKNOWN' if n_frac is UNKNOWN else '❌ over-counted'})")
    print(f"  honesty: log(r) residual          → {n_log}  "
          f"({'✅ UNKNOWN' if n_log is UNKNOWN else '❌ over-counted'})")
    ok_honest = (n_frac is UNKNOWN) and (n_log is UNKNOWN)

    passed = ok_rn and ok_honest
    print("  blind spot (D25): 'free' = EOM-independent modulo gauge; "
          "physical-vs-redundant (e.g. shift-symmetric φ₀) NOT decided.")
    print(f"\nMATTER METER: {'PASSED ✅ (reads clean cases AND refuses to guess when it chokes)' if passed else 'FAILED ❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
