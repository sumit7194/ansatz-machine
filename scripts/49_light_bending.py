#!/usr/bin/env python3
"""Step 49 — LIGHT BENDING: the 1919 Eddington test, from any metric.

The observables lens (45) gave the strong-field icons (photon sphere, shadow,
ISCO). This adds the classic WEAK-field test — the deflection of starlight grazing
the Sun that confirmed general relativity in 1919. For the static lapse f, a photon
with closest approach r₀ (impact parameter b = r₀/√f(r₀)) is deflected by

    Δφ = 2 ∫_{r₀}^∞ dr / (r² √(1/b² − f(r)/r²))  −  π.

The engine integrates this numerically (the turning-point √-singularity is handled
by mpmath). Validation:
  • weak field (large r₀): Δφ → 4M/b — Einstein's value (twice the Newtonian);
  • strong field (r₀ → photon sphere 3M): Δφ grows without bound — light winds
    around the hole (the shadow's edge);
  • charge (Reissner–Nordström): the deflection shrinks.

Run:  .venv/bin/python scripts/49_light_bending.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import R_SYM

r = R_SYM


def deflection(fexpr, r0):
    """Numeric light-deflection angle (radians) for closest approach r0."""
    b2 = (r0**2 / fexpr.subs(r, r0))
    integrand = 1 / (r**2 * sp.sqrt(1 / b2 - fexpr / r**2))
    val = sp.Integral(integrand, (r, r0, sp.oo)).evalf(18)
    return float(2 * val - sp.pi)


def main():
    M, Q = sp.symbols("M Q", positive=True)
    print("LIGHT BENDING — the 1919 test, computed from the metric\n")
    fS = (1 - 2 * M / r).subs(M, 1)

    print("  Schwarzschild (M=1): deflection vs weak-field 4M/b")
    rows = []
    for r0 in (500, 100, 20, 6, 4):
        dphi = deflection(fS, sp.Rational(r0))
        b = r0 / (1 - 2 / r0)**0.5
        rows.append((r0, dphi, 4 / b))
        print(f"     r₀={r0:>4}M:  Δφ={dphi:.5f} rad   4M/b={4/b:.5f}   ratio {dphi/(4/b):.3f}")

    weak_ok = abs(rows[0][1] / rows[0][2] - 1) < 0.01          # large r0 → matches 4M/b
    grows_ok = rows[-1][1] > rows[0][1] * 5                    # strong field bends far more
    near_ph = deflection(fS, sp.Rational(7, 2))               # r0=3.5M, just outside photon sphere
    winds_ok = near_ph > 2.0                                  # light bends > 2 rad near the ring
    print(f"\n     weak field → 4M/b (1919 value): {'✅' if weak_ok else '❌'}")
    print(f"     strong field bends far more:     {'✅' if grows_ok else '❌'}")
    print(f"     near photon sphere (r₀=3.5M): Δφ={near_ph:.3f} rad — light nearly wraps {'✅' if winds_ok else '❌'}")

    # charge reduces the deflection
    fR = (1 - 2 * M / r + Q**2 / r**2).subs({M: 1, Q: sp.Rational(1, 2)})
    d_rn = deflection(fR, sp.Rational(6))
    d_s = rows[3][1]   # Schwarzschild at r0=6
    charge_ok = d_rn < d_s
    print(f"     charge (Q=1/2) at r₀=6M: Δφ={d_rn:.4f} < Schwarzschild {d_s:.4f}  {'✅' if charge_ok else '❌'}")

    passed = weak_ok and grows_ok and winds_ok and charge_ok
    print("\n  the engine reproduces the deflection of light — Eddington's 1919 eclipse test —")
    print("  straight from the metric, from the weak field to the edge of the shadow.")
    print(f"\nLIGHT BENDING: {'PASSED ✅' if passed else 'FAILED ❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
