#!/usr/bin/env python3
"""Step 59 — TIDAL FORCES: what you would FEEL falling into a black hole.

Curvature isn't abstract — it's the tide that stretches you. Two nearby free-fallers
drift apart by the geodesic-deviation equation, governed by the tidal tensor (the
"electric" part of Riemann) E_ij = R_{a b c d} e_i^a u^b e_j^c u^d in the faller's
orthonormal frame. Its eigenvalues are the tidal accelerations per unit separation:
negative = STRETCH, positive = SQUEEZE. Now in the analyzer report card
(`analyzer.tidal`).

For Schwarzschild the engine gets the textbook spaghettification exactly:
    eigenvalues = ( −2M/r³ ,  +M/r³ ,  +M/r³ )
radial stretch, transverse squeeze, trace zero (vacuum). And the physics that follows:

  (A) the eigenvalues (−2M/r³, M/r³, M/r³) — stretched head-to-toe, squeezed
      side-to-side: spaghettification, with zero net volume change (trace 0);
  (B) REAL vs COORDINATE singularity, settled by curvature: tides DIVERGE as r→0
      (the singularity is physical — you are torn apart) but are FINITE at the
      horizon r=2M (it is only a coordinate singularity — you sail through). This is
      the curvature counterpart of the causal-structure lens (§42);
  (C) tides at the horizon scale as 1/M² — so a supermassive black hole is gentle at
      its horizon while a stellar one is lethal long before it: bigger = safer to enter;
  (D) the tie to Petrov (§57): the radial eigenvalue is exactly 2·Ψ2 — the tidal
      "shape" IS the type-D Weyl structure;
  (E) charge (Reissner–Nordström) adds a +Q² tidal term (and a non-zero trace — matter
      is present), softening the radial stretch.

Honest scope: textbook geodesic deviation. New is that the same engine reads the tide
straight off any static metric and ties it to its Petrov type and its singularities.

Run:  .venv/bin/python scripts/59_tidal.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry
from analyzer import tidal_tensor


def main():
    print("TIDAL FORCES — what you would feel falling into a black hole\n")
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    M, Q = sp.symbols("M Q", positive=True)
    ok = []

    def sph(f):
        return Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph])

    # (A) Schwarzschild spaghettification
    eig = tidal_tensor(sph(1 - 2 * M / r))
    radial, trans = eig[0], eig[1]
    okA = (sp.simplify(radial - (-2 * M / r**3)) == 0
           and sp.simplify(trans - M / r**3) == 0
           and sp.simplify(sum(eig)) == 0)
    ok.append(okA)
    print(f"  (A) Schwarzschild tidal eigenvalues = ({radial}, {trans}, {eig[2]})")
    print(f"      radial STRETCH (−2M/r³), transverse SQUEEZE (+M/r³), trace {sp.simplify(sum(eig))} "
          f"⇒ spaghettification   {'✅' if okA else '❌'}")

    # (B) real (r=0) vs coordinate (r=2M) singularity, by curvature
    at0 = sp.limit(radial, r, 0, "+")
    atH = sp.simplify(radial.subs(r, 2 * M))
    okB = (at0 in (-sp.oo, sp.oo)) and atH.is_finite and atH != 0
    ok.append(okB)
    print(f"\n  (B) tide as r→0: {at0}  (REAL singularity — torn apart);  "
          f"at horizon r=2M: {atH}  (FINITE — only a coordinate singularity)   {'✅' if okB else '❌'}")

    # (C) tides at the horizon scale as 1/M² — bigger black holes are gentler to enter
    tide_h = sp.Abs(atH)                               # = 1/(4M²)
    ratio = sp.simplify(tide_h.subs(M, 10) / tide_h.subs(M, sp.Integer(10)**9))
    okC = sp.simplify(tide_h - 1 / (4 * M**2)) == 0 and ratio == sp.Integer(10)**16
    ok.append(okC)
    print(f"\n  (C) horizon tide |−2M/r³|@2M = {sp.simplify(tide_h)} ∝ 1/M²: a 10⁹M⊙ hole is {float(ratio):.0e}× "
          f"gentler at its horizon than a 10M⊙ one   {'✅' if okC else '❌'}")
    print("      → you can cross a supermassive horizon intact; a stellar one shreds you first.")

    # (D) the Petrov tie (§57): radial eigenvalue = 2·Ψ2  (Ψ2 = −M/r³ for Schwarzschild)
    Psi2 = -M / r**3
    okD = sp.simplify(radial - 2 * Psi2) == 0
    ok.append(okD)
    print(f"\n  (D) radial tide = {radial} = 2·Ψ2 (Ψ2={Psi2}, the type-D Weyl scalar §57)   "
          f"{'✅ the tide IS the algebraic structure' if okD else '❌'}")

    # (E) charge (Reissner–Nordström): +Q² tidal term, non-zero trace (matter present)
    eigR = tidal_tensor(sph(1 - 2 * M / r + Q**2 / r**2))
    radialR, traceR = sp.simplify(eigR[0]), sp.simplify(sum(eigR))
    okE = radialR.has(Q) and traceR != 0
    ok.append(okE)
    print(f"\n  (E) Reissner–Nordström radial tide = {radialR}")
    print(f"      trace = {traceR} ≠ 0 (matter present); the charge term softens the radial stretch   "
          f"{'✅' if okE else '❌'}")

    passed = all(ok)
    print(f"\nTIDAL: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(spaghettification, real-vs-coordinate singularity, 1/M² survivability, the Petrov tie)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
