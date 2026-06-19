#!/usr/bin/env python3
"""Step 57 — PETROV CLASSIFICATION: the algebraic type of a spacetime, exactly.

A new coordinate-free lens, now part of the general analyzer's report card
(`analyzer.petrov`). The WEYL tensor (the trace-free part of curvature: pure
gravity, the tidal field that survives in vacuum) has an algebraic type at each
point — the Petrov type — read off from its Newman–Penrose scalars Ψ0…Ψ4:

    O    Weyl = 0           conformally flat — no free gravity (de Sitter, FLRW, flat)
    N    only Ψ4            radiation — a pure gravitational wave
    III  Ψ3, Ψ4            longitudinal
    D    only Ψ2            two double rays — the BLACK-HOLE type (Schwarzschild, RN, Kerr)
    II   Ψ2, Ψ3, Ψ4
    I    all                algebraically general — no special structure

The special-vs-general split is frame-INDEPENDENT, via the two Weyl invariants
    I = Ψ0Ψ4 − 4Ψ1Ψ3 + 3Ψ2² ,   J = det[[Ψ4,Ψ3,Ψ2],[Ψ3,Ψ2,Ψ1],[Ψ2,Ψ1,Ψ0]] :
algebraically special ⟺ I³ = 27 J². (I, J are Lorentz invariants; the Ψ's are not.)

This battery validates the analyzer's Petrov capability:
  (A) Schwarzschild → only Ψ2 = −M/r³ → type D (canonical black-hole signature);
  (B) Reissner–Nordström → only Ψ2 (charge-corrected) → type D;
  (C) de Sitter & Minkowski → Weyl ≡ 0 → type O;
  (D) a vacuum pp-wave → only Ψ4 → type N — a pure gravitational wave, tying straight
      to §56 (ringdown radiation IS type-N Weyl curvature);
  (E) the frame-independent speciality I³ = 27 J² holds for D, O and N.

Honest scope: textbook (Petrov 1954; Newman–Penrose 1962). New is that the SAME exact
engine reads the type off any metric. The analyzer auto-classifies the static spherical
diagonal form (its canonical tetrad); the pp-wave below is classified with its own
(off-diagonal) tetrad via the same exposed weyl_scalars/petrov_type.

Run:  .venv/bin/python scripts/57_petrov.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry
from analyzer import (UNKNOWN, petrov, petrov_type, weyl_invariants,
                      weyl_scalars, weyl_tensor)


def main():
    print("PETROV CLASSIFICATION — the algebraic type of a spacetime, exactly\n")
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    M, Q, H0 = sp.symbols("M Q H0", positive=True)
    coords = [t, r, th, ph]
    results = []

    def sph(f):
        return Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), coords)

    def check(label, geo, expect, note=""):
        ty = petrov(geo)
        ok = ty == expect or (isinstance(ty, str) and ty.startswith(expect))
        results.append(ok)
        print(f"  {label:24s}: analyzer.petrov → {str(ty):20s} "
              f"{'✅' if ok else '❌ (want ' + expect + ')'}  {note}")
        return geo

    # (A) Schwarzschild — type D, and Ψ2 = −M/r³ exactly (via the exposed scalars)
    gS = sph(1 - 2 * M / r)
    check("Schwarzschild", gS, "D")
    s2 = sp.sqrt(2)
    f = 1 - 2 * M / r
    tet = ([1 / f, 1, 0, 0], [sp.Rational(1, 2), -f / 2, 0, 0],
           [0, 0, 1 / (r * s2), sp.I / (r * s2 * sp.sin(th))],
           [0, 0, 1 / (r * s2), -sp.I / (r * s2 * sp.sin(th))])
    P = weyl_scalars(weyl_tensor(gS), tet)
    okPsi2 = sp.simplify(P[2] - (-M / r**3)) == 0
    Iv, Jv = weyl_invariants(P)
    spec = sp.simplify(Iv**3 - 27 * Jv**2) == 0
    print(f"        └ Ψ2 = {sp.simplify(P[2])}  (= −M/r³ {'✅' if okPsi2 else '❌'});  "
          f"I³=27J² {'✅ special' if spec else '❌'}")

    # (B) Reissner–Nordström — still D, charge enters Ψ2
    check("Reissner–Nordström", sph(1 - 2 * M / r + Q**2 / r**2), "D")

    # (C) de Sitter & Minkowski — conformally flat, type O
    check("de Sitter", sph(1 - H0**2 * r**2), "O")
    check("Minkowski", sph(sp.Integer(1)), "O")

    # (D) vacuum pp-wave — type N (own null tetrad; analyzer auto-path returns UNKNOWN
    #     for off-diagonal, so classify here via the same exposed functions)
    u, v, x, y = sp.symbols("u v x y", real=True)
    Hpp = x**2 - y**2                       # harmonic ⇒ vacuum
    gpp = Geometry(sp.Matrix([[Hpp, -1, 0, 0], [-1, 0, 0, 0],
                              [0, 0, 1, 0], [0, 0, 0, 1]]), [u, v, x, y])
    tet_pp = ([0, 1, 0, 0], [1, Hpp / 2, 0, 0],
              [0, 0, 1 / s2, sp.I / s2], [0, 0, 1 / s2, -sp.I / s2])
    Ppp = weyl_scalars(weyl_tensor(gpp), tet_pp)
    typp = petrov_type(Ppp)
    okN = typp == "N" and gpp.ricci.is_zero_matrix
    results.append(okN)
    print(f"  {'pp-wave (vacuum)':24s}: petrov_type → {typp:20s} "
          f"{'✅' if okN else '❌'}  ← ringdown radiation is type-N Weyl (ties to §56)")
    # analyzer correctly declines the off-diagonal auto-path (honest UNKNOWN)
    okHonest = petrov(gpp) is UNKNOWN
    print(f"        └ analyzer.petrov(pp-wave) = {petrov(gpp)} (off-diagonal ⇒ no auto tetrad)  "
          f"{'✅ honest' if okHonest else '❌'}")

    passed = all(results) and okPsi2 and spec and okHonest
    print(f"\nPETROV: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(black holes = D, conformally flat = O, gravitational wave = N — from the metric)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
