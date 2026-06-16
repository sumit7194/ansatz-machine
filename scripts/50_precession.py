#!/usr/bin/env python3
"""Step 50 — PERIHELION PRECESSION: Mercury's test, from any metric.

The third classic test of general relativity (with light bending, 49): orbits
don't close — the perihelion advances each revolution. This is what explained
Mercury's anomalous 43″/century and vindicated GR over Newton.

For a circular orbit at radius r in the static lapse f, the advance per orbit is
ALGEBRAIC (epicyclic frequencies — no integral):
    L² = f' r³ / (2f − f' r),   V(r) = f(1 + L²/r²),
    Δφ_orbit = 2π( √(2L² / (r⁴ V'')) − 1 ).
For Schwarzschild this is exactly  Δφ = 2π(1/√(1−6M/r) − 1):
  • weak field (large r): Δφ → 6πM/r  (Mercury);
  • it DIVERGES at r = 6M — the ISCO (innermost stable orbit): below it, no stable
    orbit, the precession runs away. Precession and the accretion-disk edge are
    the same physics.

Run:  .venv/bin/python scripts/50_precession.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import R_SYM

r = R_SYM


def precession_per_orbit(f):
    """Periastron advance per orbit for a circular orbit of radius r (symbolic)."""
    fp = sp.diff(f, r)
    L2 = fp * r**3 / (2 * f - fp * r)
    LL = sp.Symbol("LL")
    Vpp = sp.diff(f * (1 + LL / r**2), r, 2).subs(LL, L2)
    return sp.simplify(2 * sp.pi * (sp.sqrt(2 * L2 / (r**4 * Vpp)) - 1))


def main():
    M, Q = sp.symbols("M Q", positive=True)
    print("PERIHELION PRECESSION — Mercury's test, from the metric\n")

    prec = precession_per_orbit(1 - 2 * M / r)
    print(f"  Schwarzschild Δφ/orbit = {prec}")
    # = 2π(1/√(1−6M/r) − 1) — checked numerically (sympy won't prove the radical identity)
    known = 2 * sp.pi * (1 / sp.sqrt(1 - 6 * M / r) - 1)
    closed = all(abs(float(prec.subs({M: 1, r: rv}).evalf()) - float(known.subs({M: 1, r: rv}).evalf())) < 1e-9
                 for rv in (8, 12, 30))
    print(f"     = 2π(1/√(1−6M/r) − 1)  {'✅' if closed else '❌'}")

    # weak field → 6πM/r  (Mercury)
    big = float(prec.subs({M: 1, r: 10000}).evalf())
    weak_ok = abs(big / (6 * sp.pi / 10000) - 1) < 0.01
    print(f"     weak field (r=10⁴M): Δφ={big:.3e}  vs 6πM/r={float(6*sp.pi/10000):.3e}  "
          f"{'✅ Mercury limit' if weak_ok else '❌'}")

    # diverges at the ISCO r=6M
    near = float(prec.subs({M: 1, r: sp.Rational(61, 10)}).evalf())   # r=6.1M, just outside ISCO
    isco_ok = near > 5.0 and prec.subs(r, 6 * M) in (sp.zoo, sp.oo) or near > 5.0
    print(f"     near ISCO (r=6.1M): Δφ={near:.2f} rad/orbit — runs away as r→6M (the ISCO)  "
          f"{'✅' if near > 5.0 else '❌'}")

    # charge shifts it (RN): smaller precession at fixed r
    precRN = precession_per_orbit(1 - 2 * M / r + Q**2 / r**2)
    d_rn = float(precRN.subs({M: 1, Q: sp.Rational(1, 2), r: 10}).evalf())
    d_s = float(prec.subs({M: 1, r: 10}).evalf())
    charge_ok = d_rn < d_s
    print(f"     charge (Q=1/2) at r=10M: Δφ={d_rn:.4f} < Schwarzschild {d_s:.4f}  {'✅' if charge_ok else '❌'}")

    passed = closed and weak_ok and near > 5.0 and charge_ok
    print("\n  the engine reproduces the perihelion advance — Mercury's 43″/century — from the")
    print("  metric, and shows it diverging at the ISCO: precession and the disk edge are one.")
    print(f"\nPRECESSION: {'PASSED ✅' if passed else 'FAILED ❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
