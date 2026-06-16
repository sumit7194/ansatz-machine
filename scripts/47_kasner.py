#!/usr/bin/env python3
"""Step 47 — KASNER: the engine recovers the anisotropic-vacuum meta-law.

A loose thread from ATTACK_ANGLES #4, closed. The Kasner metric is an EXPANDING,
ANISOTROPIC, empty universe — space stretches at different rates along x, y, z:

    ds² = −dt² + t^{2p₁}dx² + t^{2p₂}dy² + t^{2p₃}dz²

It is vacuum (R_ab = 0) only for special exponents. The engine recovers the famous
**Kasner conditions** straight from the vacuum residual — the abstractor move (24),
now on a cosmology instead of a black hole:

    R_tt · t²        = (Σpᵢ) − (Σpᵢ²)            ⇒  Σpᵢ² = Σpᵢ
    R_{x_i x_i}·t²   = pᵢ·(Σpⱼ − 1) · t^{2pᵢ}      ⇒  Σpⱼ = 1
    together:  **p₁+p₂+p₃ = 1  AND  p₁²+p₂²+p₃² = 1.**

These define the Kasner sphere∩plane circle — the building block of the BKL
description of generic cosmological singularities. Verified necessary AND
sufficient: zero residual exactly on the conditions, nonzero off them.

Run:  .venv/bin/python scripts/47_kasner.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry


def main():
    t, x, y, z = sp.symbols("t x y z", real=True, positive=True)
    p1, p2, p3 = sp.symbols("p1 p2 p3", real=True)
    print("KASNER — recover the conditions for an anisotropic vacuum universe\n")

    g = sp.diag(-1, t**(2 * p1), t**(2 * p2), t**(2 * p3))
    Ric = Geometry(g, [t, x, y, z]).ricci
    S1, S2 = p1 + p2 + p3, p1**2 + p2**2 + p3**2

    # (1) recover the conditions from the residual structure
    tt = sp.expand(Ric[0, 0] * t**2)
    ok_tt = sp.simplify(tt - (S1 - S2)) == 0
    xx = sp.simplify(Ric[1, 1] * t**2 / t**(2 * p1))
    ok_xx = sp.simplify(xx - p1 * (S1 - 1)) == 0
    print("  the engine's vacuum residual factors into the conditions:")
    print(f"     R_tt·t²      = {tt}   = Σp − Σp²   {'✓' if ok_tt else '✗'}")
    print(f"     R_xx·t²/t^2p₁ = {xx}   = p₁(Σp − 1)  {'✓' if ok_xx else '✗'}")
    print("     ⇒ vacuum needs  Σp = 1  (from the spatial eqs)  and  Σp² = Σp = 1  (from R_tt)")
    print("     ⇒ KASNER CONDITIONS:  p₁+p₂+p₃ = 1   and   p₁²+p₂²+p₃² = 1")

    # (2) sufficient: zero on the conditions
    on = [(1, 0, 0), (sp.Rational(2, 3), sp.Rational(2, 3), sp.Rational(-1, 3))]
    suff = all(max(abs(sp.simplify(Ric[i, j].subs({p1: a, p2: b, p3: c})))
                   for i in range(4) for j in range(4)) == 0 for a, b, c in on)
    # (3) necessary: nonzero off them
    off = [(1, 1, 1), (sp.Rational(1, 2), sp.Rational(1, 2), 0)]   # Σp≠1, or Σp=1 but Σp²≠1
    nec = all(max(abs(sp.simplify(Ric[i, j].subs({p1: a, p2: b, p3: c})))
                  for i in range(4) for j in range(4)) != 0 for a, b, c in off)
    print(f"\n  sufficient — Ric≡0 on the Kasner circle (1,0,0),(⅔,⅔,−⅓): {'✅' if suff else '❌'}")
    print(f"  necessary  — Ric≠0 off it, e.g. (1,1,1) and (½,½,0):       {'✅' if nec else '❌'}")

    passed = ok_tt and ok_xx and suff and nec
    print("\n  the engine rediscovered the Kasner conditions — the meta-law of anisotropic")
    print("  vacuum cosmology (BKL) — the same 'recover the constraint' move as the Tangherlini")
    print("  abstractor (24), now in a cosmological setting.")
    print(f"\nKASNER: {'PASSED ✅' if passed else 'FAILED ❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
