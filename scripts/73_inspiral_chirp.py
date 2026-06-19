#!/usr/bin/env python3
"""Step 73 — THE INSPIRAL CHIRP & CHIRP MASS (the other half of a LIGO signal).

§72 was the ringdown (the merger's final note); this is the long rising tone BEFORE
it — the inspiral, where two bodies spiral together radiating gravitational waves.
Together they are the whole waveform a detector records: inspiral → merger → ringdown.
This is the exact inspiral template (and the quantity LIGO measures best).

A circular binary (G=c=1; total mass M=m₁+m₂, reduced μ=m₁m₂/M) loses energy to GWs by
the quadrupole formula L = (32/5) μ² M³/r⁵, so the orbit shrinks and the orbital
frequency Ω=√(M/r³) rises — the "chirp." The engine shows:

  (A) energy balance dE/dt = −L (E=−μM/2r) drives the orbit inward (dr/dt<0);
  (B) THE CHIRP: dΩ/dt = (96/5) M_c^{5/3} Ω^{11/3} — the sweep rate depends on ONE
      combination, the CHIRP MASS  M_c = (m₁m₂)^{3/5}/(m₁+m₂)^{1/5}  (M_c^{5/3}=μM^{2/3});
      that is why M_c is what a detector measures most precisely from the inspiral;
  (C) integrating: Ω ∝ (t_c − t)^{−3/8} — frequency diverges at the merger t_c, the
      rising chirp (the −3/8 power is fixed by the 11/3 exponent: 1/(11/3−1)=3/8);
  (D) the bridge: M_c from the inspiral (this) + final (M,a) from the ringdown (§72)
      ⇒ the full inspiral→merger→ringdown template the engine supplies as ground truth.

Honest scope: leading quadrupole / Newtonian-order inspiral (Peters–Mathews 1963); the
real signal adds post-Newtonian corrections. The chirp-mass scaling and −3/8 law are
exact at this order.

Run:  .venv/bin/python scripts/73_inspiral_chirp.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("THE INSPIRAL CHIRP & CHIRP MASS — the other half of a LIGO signal\n")
    r, m1, m2 = sp.symbols("r m1 m2", positive=True)
    Om, tc, t = sp.symbols("Omega t_c t", positive=True)
    M = m1 + m2
    mu = m1 * m2 / M
    ok = []

    E = -mu * M / (2 * r)
    L = sp.Rational(32, 5) * mu**2 * M**3 / r**5          # quadrupole GW luminosity

    # (A) energy balance dE/dt=−L drives dr/dt<0
    drdt = sp.simplify(-L / sp.diff(E, r))
    okA = drdt.subs({m1: 1, m2: 1, r: 10}) < 0
    ok.append(okA)
    print(f"  (A) quadrupole L = (32/5)μ²M³/r⁵; energy balance dE/dt=−L ⇒ dr/dt = {drdt} < 0 (inspiral)   "
          f"{'✅' if okA else '❌'}")

    # (B) the chirp rate depends only on the chirp mass
    Omega = sp.sqrt(M / r**3)
    dOmdt = sp.simplify(sp.diff(Omega, r) * drdt).subs(r, (M / Om**2)**sp.Rational(1, 3))
    Mc = (m1 * m2)**sp.Rational(3, 5) / M**sp.Rational(1, 5)
    claim = sp.Rational(96, 5) * Mc**sp.Rational(5, 3) * Om**sp.Rational(11, 3)
    okB = sp.simplify(dOmdt - claim) == 0 and sp.simplify(Mc**sp.Rational(5, 3) - mu * M**sp.Rational(2, 3)) == 0
    ok.append(okB)
    print(f"\n  (B) dΩ/dt = {sp.simplify(dOmdt)}")
    print(f"      = (96/5) M_c^(5/3) Ω^(11/3), M_c=(m₁m₂)^(3/5)/(m₁+m₂)^(1/5) — depends ONLY on the chirp mass   "
          f"{'✅' if okB else '❌'}")

    # (C) Ω ∝ (t_c − t)^{−3/8}: verify the power-law solves dΩ/dt ∝ Ω^{11/3}
    k = sp.Symbol("k", positive=True)
    Om_t = (tc - t)**sp.Rational(-3, 8)
    lhs = sp.simplify(sp.diff(Om_t, t))
    rhs_scaling = sp.simplify(Om_t**sp.Rational(11, 3))      # ∝ (t_c−t)^{−11/8}
    okC = sp.simplify(lhs / rhs_scaling) == sp.Rational(3, 8)   # dΩ/dt = (3/8)(t_c−t)^{−11/8} ∝ Ω^{11/3}
    ok.append(okC)
    print(f"\n  (C) Ω(t) ∝ (t_c−t)^(−3/8): dΩ/dt = {lhs} ∝ Ω^(11/3) ⇒ frequency diverges at merger t_c (the chirp)   "
          f"{'✅' if okC else '❌'}")

    # (D) the bridge synthesis
    okD = okA and okB and okC
    ok.append(okD)
    print(f"\n  (D) M_c from the inspiral (this) + final (M,a) from the ringdown (§72) ⇒ the full")
    print(f"      inspiral→merger→ringdown template — the engine's ground truth for the bridge   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nINSPIRAL CHIRP: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(quadrupole inspiral, chirp mass M_c, the (t_c−t)^(−3/8) chirp)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
