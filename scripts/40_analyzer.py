#!/usr/bin/env python3
"""Step 40 — the GENERAL ANALYZER, validated against the frozen zoo.

The core of the universal tool (analyzer.py): one `analyze(metric, coords)` that
eats ANY spacetime and reports what it's made of, whether that matter is physical
(frame-independent energy conditions), and whether it solves Einstein's equations.

This battery is the proof it's sound: feed it a zoo of completely different
metrics — flat space, a black hole, a charged hole, an expanding universe, de
Sitter, a wormhole — and check the single tool reproduces what scripts 27–38
proved case by case. If the general tool agrees with the frozen base, we can
trust it on new inputs.

Run:  .venv/bin/python scripts/40_analyzer.py
"""

import os
import sys

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from gr_engine import R_SYM
from analyzer import analyze, format_report


def zoo():
    r = R_SYM
    t, x, y, z = sp.symbols("t x y z", real=True)
    th, ph = sp.symbols("theta phi", real=True)
    M, Q, r0, H = sp.symbols("M Q r0 H", positive=True)
    cases = []

    # flat space
    cases.append(("Minkowski (flat)",
                  sp.diag(-1, 1, 1, 1), [t, x, y, z],
                  lambda R: "vacuum" in R["made_of"] and "vacuum" in R["solves_einstein"]))

    # Schwarzschild black hole — vacuum
    fS = 1 - 2 * M / r
    cases.append(("Schwarzschild black hole",
                  sp.diag(-fS, 1 / fS, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph],
                  lambda R: "vacuum" in R["made_of"] and "Ricci-flat" in R["solves_einstein"]))

    # Reissner–Nordström — electromagnetic (traceless), physical
    fR = 1 - 2 * M / r + Q**2 / r**2
    cases.append(("Reissner–Nordström",
                  sp.diag(-fR, 1 / fR, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph],
                  lambda R: (R["physical"] is True and "sourced" in R["solves_einstein"]
                            and ("traceless" in R["made_of"] or "electromagnetic" in R["made_of"]))))

    # FLRW dust universe a=t^(2/3) — perfect fluid w=0, physical
    a = t**sp.Rational(2, 3)
    cases.append(("FLRW dust universe",
                  sp.diag(-1, a**2, a**2, a**2), [t, x, y, z],
                  lambda R: ("perfect fluid" in R["made_of"] and "w = 0" in R["made_of"]
                            and R["physical"] is True and "sourced" in R["solves_einstein"])))

    # de Sitter a=e^{Ht} — cosmological constant, SEC violated (accelerating)
    aD = sp.exp(H * t)
    cases.append(("de Sitter (Λ)",
                  sp.diag(-1, aD**2, aD**2, aD**2), [t, x, y, z],
                  lambda R: ("cosmological constant" in R["made_of"]
                            and R["energy_conditions"]["SEC"] is False
                            and R["physical"] is False)))

    # Morris–Thorne wormhole b=r0²/r — exotic, NEC/WEC violated
    b = r0**2 / r
    cases.append(("Morris–Thorne wormhole",
                  sp.diag(-1, 1 / (1 - b / r), r**2, r**2 * sp.sin(th)**2), [t, r, th, ph],
                  lambda R: (R["physical"] is False
                            and "sourced" in R["solves_einstein"])))
    return cases


def main():
    print("GENERAL ANALYZER — one tool, the whole zoo\n")
    ok_all = True
    for label, metric, coords, check in zoo():
        report = analyze(metric, coords)
        ok = bool(check(report))
        ok_all = ok_all and ok
        print(f"▸ {label}   {'✓' if ok else '✗ UNEXPECTED'}")
        print(format_report(report))
        print()

    print(f"GENERAL ANALYZER: {'PASSED ✅' if ok_all else 'FAILED ❌'}  "
          "(one analyze() reproduces 27–38 across flat space, black holes, a "
          "charged hole, an expanding universe, de Sitter, and a wormhole)")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
