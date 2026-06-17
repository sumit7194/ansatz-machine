#!/usr/bin/env python3
"""Step 51 — GRAVITATIONAL REDSHIFT: the third classic test (Pound–Rebka).

Completes the three classic tests of general relativity, all now computed from the
metric by the engine: light bending (49), perihelion precession (50), and — here —
gravitational redshift. A photon climbing out of a gravitational well loses energy:
a static source at radius r, seen from infinity, is redshifted by

    1 + z = 1/√f(r)   ⇒   z(r) = 1/√f(r) − 1.

  • weak field: z ≈ M/r  (the Pound–Rebka tower experiment, gh/c²);
  • at the horizon (f→0): z → ∞ — light is infinitely redshifted, the surface of
    a black hole fades to black;
  • charge (Reissner–Nordström) raises f at fixed r, so it REDUCES the redshift.

Run:  .venv/bin/python scripts/51_redshift.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import R_SYM

r = R_SYM


def redshift(f):
    return 1 / sp.sqrt(f) - 1


def main():
    M, Q = sp.symbols("M Q", positive=True)
    print("GRAVITATIONAL REDSHIFT — the third classic test (Pound–Rebka)\n")

    z = redshift(1 - 2 * M / r)
    print(f"  Schwarzschild z(r) = {z}")

    # weak field z ≈ M/r
    weak = sp.series(z, M, 0, 2).removeO()
    weak_ok = sp.simplify(weak - M / r) == 0
    print(f"     weak field: z ≈ {weak}  = M/r (Pound–Rebka)  {'✅' if weak_ok else '❌'}")

    # infinite redshift at the horizon
    horizon_z = sp.limit(z, r, 2 * M, "+")
    horizon_ok = horizon_z == sp.oo
    print(f"     at horizon r→2M: z → {horizon_z}  (light fades to black)  {'✅' if horizon_ok else '❌'}")

    # charge reduces the redshift (f larger at fixed r)
    zR = redshift(1 - 2 * M / r + Q**2 / r**2)
    z_s = float(z.subs({M: 1, r: 4}).evalf())
    z_rn = float(zR.subs({M: 1, Q: sp.Rational(1, 2), r: 4}).evalf())
    charge_ok = z_rn < z_s
    print(f"     charge (Q=1/2) at r=4M: z={z_rn:.4f} < Schwarzschild {z_s:.4f}  {'✅' if charge_ok else '❌'}")

    passed = weak_ok and horizon_ok and charge_ok
    print("\n  with this the engine reproduces ALL THREE classic tests of GR — light bending (49),")
    print("  perihelion precession (50), gravitational redshift (51) — each straight from the metric.")
    print(f"\nREDSHIFT: {'PASSED ✅' if passed else 'FAILED ❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
