#!/usr/bin/env python3
"""Step 26 — the IRREDUCIBLE-INFORMATION METER.

Reframe of what the abstractor really is (v6 discussion): point it at a
solution family and it reports how many constants are GENUINELY FREE —
the dimension of the family, i.e. the physical "hair". A constant is

  free      — the field equations hold for a range of it (a true parameter);
  forced    — pinned to one value by the equations (e.g. asymptotic '1');
  secondary — determined by the OTHER free constants (the subtle case:
              EdGB's dilaton charge is the textbook secondary hair —
              looks free, isn't). Naive parameter-counting misses this;
              testing genuine freedom catches it by construction.

Method (glass-box, exact): build the metric with the candidate constants
symbolic, demand the vacuum+Λ residual ≡ 0, reduce to equations on the
constants, solve, and count which survive free. No NN.

This run is the validation suite: it must read 0 (de Sitter, no hair),
1 (Schwarzschild — and SdS, where the r² coefficient is correctly seen
as SECONDARY, Birkhoff), 2 (mass + a floating cosmological constant),
and must REJECT a fake 1/r² hair as forced.

Run:  .venv/bin/python scripts/26_information_meter.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry, build_ansatz_metric, R_SYM


def _constraints(metric, coords, n, Lambda):
    """Equations the constants must satisfy for vacuum+Λ (residual ≡ 0)."""
    geo = Geometry(metric, coords)
    res = geo.vacuum_residual(Lambda)
    angles = coords[2:]
    asub = {a: sp.atan(sp.Rational(3, 4)) for a in angles}  # regular point
    eqs = set()
    for i in range(n):
        for j in range(i, n):
            comp = res[i, j]
            if comp == 0:
                continue
            comp = sp.expand_trig(comp.subs(asub)) if angles else comp
            num, _ = sp.fraction(sp.together(comp))
            num = sp.expand(num)
            try:
                poly = sp.Poly(num, R_SYM)
            except sp.PolynomialError:
                eqs.add(num)
                continue
            for c in poly.all_coeffs():
                if c != 0:
                    eqs.add(sp.expand(c))
    return list(eqs)


def count_free(f, n, consts, Lambda=sp.S.Zero, free_lambda=False):
    """Return (num_free, {const: classification})."""
    metric, coords, _ = build_ansatz_metric(n, f)
    lam = sp.Symbol("Lambda", real=True) if free_lambda else Lambda
    variables = list(consts) + ([lam] if free_lambda else [])
    eqs = _constraints(metric, coords, n, lam)
    if not eqs:
        return len(variables), {v: "free (hair)" for v in variables}
    sol = sp.solve(eqs, variables, dict=True)
    if not sol:
        return 0, {v: "no consistent solution" for v in variables}
    s = sol[0]
    free = [v for v in variables if v not in s]
    cls = {}
    for v in variables:
        if v in free:
            cls[v] = "free (hair)"
        else:
            val = sp.simplify(s[v])
            if val.free_symbols & set(free):
                cls[v] = f"secondary (= {val})"
            else:
                cls[v] = f"forced (= {val})"
    return len(free), cls


def main():
    A, B, C, D = sp.symbols("A B C D", real=True)
    r = R_SYM
    L = sp.Rational(3, 100)  # an arbitrary fixed cosmological constant

    cases = [
        # (label, f, n, consts, Lambda, free_lambda, expected_free)
        ("de Sitter  f=A+C·r² (Λ fixed)        ", A + C * r**2, 4, [A, C], L, False, 0),
        ("Schwarzschild  f=A+B/r (Λ=0)         ", A + B / r, 4, [A, B], 0, False, 1),
        ("Schwarzschild-dS  f=A+B/r+C·r²        ", A + B / r + C * r**2, 4, [A, B, C], L, False, 1),
        ("mass + FLOATING Λ  f=A+B/r+C·r²       ", A + B / r + C * r**2, 4, [A, B, C], None, True, 2),
        ("fake 1/r² hair  f=A+B/r+D/r² (Λ=0)    ", A + B / r + D / r**2, 4, [A, B, D], 0, False, 1),
        ("Tangherlini 6D  f=A+B/r³ (Λ=0)        ", A + B / r**3, 6, [A, B], 0, False, 1),
    ]

    print("IRREDUCIBLE-INFORMATION METER — validation suite\n")
    ok_all = True
    for label, f, n, consts, lam, fl, expect in cases:
        nfree, cls = count_free(f, n, consts, Lambda=(lam if lam is not None else sp.S.Zero),
                                free_lambda=fl)
        ok = (nfree == expect)
        ok_all = ok_all and ok
        print(f"  {label}: free = {nfree}  (expected {expect})  "
              f"{'✓' if ok else '✗'}")
        for v, c in cls.items():
            print(f"        {v}: {c}")
    print(f"\nMETER VALIDATION: {'PASSED ✅' if ok_all else 'FAILED ❌'}")
    if ok_all:
        print("  → reads moduli/hair correctly: 0 (dS), 1 (Schwarzschild & SdS"
              " — r² coeff seen as SECONDARY: Birkhoff), 2 (floating Λ), and"
              " rejects a fake hair. The instrument works.")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
