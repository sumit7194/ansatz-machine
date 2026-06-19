#!/usr/bin/env python3
"""Step 62 — KOMAR CHARGES: what mass and spin ARE, geometrically.

The conceptual capstone of the symmetry arc (§58 Killing → §61 Smarr): a spacetime's
mass and angular momentum are not put in by hand — they are the conserved CHARGES of
its symmetries, read off as surface integrals of the Killing vectors (Komar 1959). The
analyzer now reports them (`analyzer.komar`):

    mass  M = lim_{r→∞} r(1+g_tt)/2        (charge of the time-translation Killing vector ∂_t)
    spin  J = lim_{r→∞} −r g_tφ/(2sin²θ)   (charge of the rotational Killing vector ∂_φ)

Experiments:
  (A) the engine reads M off Schwarzschild, Reissner–Nordström and Kerr, and J=Ma off
      Kerr — mass and spin as symmetry charges, straight from the metric;
  (B) the Komar mass WITHIN radius r, M(r)=½r²f′(r), exposes FIELD ENERGY: in vacuum
      (Schwarzschild) it is constant M (a Gauss law — same on every sphere), but for
      Reissner–Nordström it is M−Q²/r, rising to M only at infinity — the electromagnetic
      field outside r carries the missing energy. Mass is r-dependent exactly when fields
      carry energy;
  (C) the SMARR formula M = 2TS + 2Ω_H J (§61) is itself a Komar identity: the mass at
      infinity equals the Komar integral over the horizon — energy bookkeeping closes;
  (D) so the four "constants" of a black hole — M, J (and Q) — are the Noether charges of
      time-translation, rotation (and the gauge symmetry): geometry, not inputs.

Honest scope: textbook Komar/ADM charges. New is the same engine reading them off any
metric and tying mass↔time-symmetry, spin↔rotation-symmetry, field-energy↔r-dependence.

Run:  .venv/bin/python scripts/62_komar.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry
from analyzer import komar_charges


def main():
    print("KOMAR CHARGES — what mass and spin ARE, geometrically\n")
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    M, Q, a = sp.symbols("M Q a", positive=True)
    ok = []

    def sph(f):
        return Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph])

    # (A) mass (and spin) as symmetry charges, read by the analyzer
    mS = komar_charges(sph(1 - 2 * M / r)).get("mass")
    mR = komar_charges(sph(1 - 2 * M / r + Q**2 / r**2)).get("mass")
    Sig = r**2 + a**2 * sp.cos(th)**2
    s2 = sp.sin(th)**2
    gK = sp.zeros(4)
    gK[0, 0] = -(1 - 2 * M * r / Sig)
    gK[0, 3] = gK[3, 0] = -2 * M * r * a * s2 / Sig
    gK[1, 1] = Sig / (r**2 - 2 * M * r + a**2)
    gK[2, 2] = Sig
    gK[3, 3] = (r**2 + a**2 + 2 * M * r * a**2 * s2 / Sig) * s2
    kerr = komar_charges(Geometry(gK, [t, r, th, ph]))
    okA = (mS == M and mR == M and kerr["mass"] == M and kerr["angular_momentum"] == M * a)
    ok.append(okA)
    print("  (A) mass = charge of ∂_t,  spin = charge of ∂_φ (read by analyzer.komar):")
    print(f"      Schwarzschild M={mS};  RN M={mR};  Kerr M={kerr['mass']}, J={kerr['angular_momentum']} "
          f"(= Ma)   {'✅' if okA else '❌'}")

    # (B) Komar mass within r exposes field energy
    def M_within(f):
        return sp.simplify(sp.Rational(1, 2) * r**2 * sp.diff(f, r))
    MK_S = M_within(1 - 2 * M / r)
    MK_R = M_within(1 - 2 * M / r + Q**2 / r**2)
    vac_const = sp.diff(MK_S, r) == 0
    field_dep = sp.diff(MK_R, r) != 0 and sp.limit(MK_R, r, sp.oo) == M
    okB = vac_const and field_dep
    ok.append(okB)
    print(f"\n  (B) Komar mass within r,  M(r)=½r²f′:")
    print(f"      Schwarzschild: M(r) = {MK_S}  (constant — vacuum Gauss law)")
    print(f"      Reissner–Nordström: M(r) = {MK_R}  → M at ∞ (EM field outside r carries Q²/r)   "
          f"{'✅' if okB else '❌'}")

    # (C) the Smarr formula is a Komar identity: M(∞) = horizon Komar integral
    rp = M + sp.sqrt(M**2 - a**2)
    A = 4 * sp.pi * (rp**2 + a**2)
    T = (rp - M) / (rp**2 + a**2) / (2 * sp.pi)
    S = A / 4
    Om = a / (rp**2 + a**2)
    smarr = sp.simplify(2 * T * S + 2 * Om * (M * a))
    okC = sp.simplify(smarr - kerr["mass"]) == 0
    ok.append(okC)
    print(f"\n  (C) Smarr as a Komar identity: 2TS + 2Ω_H J = {smarr} = M (the Komar mass at ∞)   "
          f"{'✅' if okC else '❌'}")

    # (D) the black-hole "constants" are symmetry charges, not inputs
    okD = okA and okC
    ok.append(okD)
    print(f"\n  (D) M (time-translation), J (rotation), Q (gauge) are NOETHER CHARGES of the")
    print(f"      symmetries (§58) — a black hole's hair is geometry, not free input   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nKOMAR: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(mass↔time symmetry, spin↔rotation, field-energy↔r-dependence, Smarr↔Komar)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
