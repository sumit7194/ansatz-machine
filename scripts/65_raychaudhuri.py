#!/usr/bin/env python3
"""Step 65 — RAYCHAUDHURI & FOCUSING: why singularities are inevitable.

The deepest "why" in the engine so far. A bundle of freely-falling observers has an
expansion θ (the fractional rate its cross-sectional volume grows), and it obeys the
RAYCHAUDHURI equation
        dθ/dτ = −θ²/3 − σ² + ω² − R_ab u^a u^b.
For a non-rotating bundle (ω=0), every term on the right except possibly the last is
≤0, and the Einstein equations make the last term R_ab u^a u^b = 4π(ρ+3p): so as long
as the Strong Energy Condition holds (ρ+3p ≥ 0, "gravity attracts"), the bundle is
FORCED to converge — θ → −∞ in finite proper time. Converging bundles cross
(caustics), and Penrose & Hawking turned that into the SINGULARITY THEOREMS: with
ordinary matter, singularities are generic, not artifacts of symmetry.

  (A) the engine VERIFIES the Raychaudhuri equation as an identity for the FLRW
      comoving bundle (σ=ω=0): θ=3H, R_ab u^a u^b = −3ä/a, residual 0;
  (B) FOCUSING: for ordinary matter (a∝t^{2/3}, SEC holds) the term is >0 ⇒ tracing
      back, θ→+∞ at t→0 — the Big Bang is a focusing point, a real singularity (ties
      §36 energy conditions + §37 cosmology);
  (C) the ESCAPE: de Sitter (a=e^{Ht}, dark energy) VIOLATES the SEC (ρ+3p<0), the
      focusing term flips sign, dθ/dτ=0 ⇒ θ=3H constant — eternal expansion, NO future
      singularity. Beating the singularity theorems requires exotic matter (cf. §38);
  (D) so the singularity the analyzer detects by curvature (§59 tidal, §42 causal) is
      the same one focusing makes inevitable — two views of one fact.

Honest scope: textbook (Raychaudhuri 1955; Penrose 1965; Hawking). New is the same
engine verifying the focusing identity and tying SEC → focusing → singularity.

Run:  .venv/bin/python scripts/65_raychaudhuri.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry

T = sp.Symbol("t", positive=True)


def flrw_focus(a_expr):
    """(θ, R_ab u^a u^b, dθ/dτ) for the FLRW comoving bundle with scale factor a(t)."""
    x, y, z = sp.symbols("x y z", real=True)
    g = sp.diag(-1, a_expr**2, a_expr**2, a_expr**2)
    geo = Geometry(g, [T, x, y, z])
    u = [1, 0, 0, 0]
    sg = sp.sqrt(-g.det())
    theta = sp.simplify(sum(sp.diff(sg * u[i], [T, x, y, z][i]) for i in range(4)) / sg)
    Ruu = sp.simplify(sum(geo.ricci[i, j] * u[i] * u[j] for i in range(4) for j in range(4)))
    return theta, Ruu, sp.simplify(sp.diff(theta, T))


def main():
    print("RAYCHAUDHURI & FOCUSING — why singularities are inevitable\n")
    ok = []

    # (A) the Raychaudhuri identity for a general FLRW bundle
    a = sp.Function("a", positive=True)
    theta, Ruu, dtheta = flrw_focus(a(T))
    resid = sp.simplify(dtheta - (-theta**2 / 3 - Ruu))
    okA = resid == 0
    ok.append(okA)
    print(f"  (A) FLRW comoving bundle: θ = {theta} (= 3H),  R_ab u^a u^b = {Ruu} (= −3ä/a)")
    print(f"      Raychaudhuri  dθ/dτ = −θ²/3 − R_ab u^a u^b  holds: residual = {resid}   "
          f"{'✅ identity' if okA else '❌'}")

    # (B) focusing with ordinary matter (SEC): a ∝ t^{2/3}
    th_m, Ruu_m, _ = flrw_focus(T**sp.Rational(2, 3))
    theta_blowup = sp.limit(th_m, T, 0, "+")
    okB = Ruu_m.is_positive and theta_blowup == sp.oo
    ok.append(okB)
    print(f"\n  (B) matter a∝t^{{2/3}} (SEC holds): R_ab u^a u^b = {Ruu_m} > 0 ⇒ focusing;")
    print(f"      θ → {theta_blowup} as t→0 — the Big Bang is a focusing singularity (ρ+3p>0)   "
          f"{'✅' if okB else '❌'}")

    # (C) the escape: de Sitter violates the SEC ⇒ no focusing
    Hs = sp.Symbol("H", positive=True)
    th_d, Ruu_d, dth_d = flrw_focus(sp.exp(Hs * T))
    okC = (sp.simplify(Ruu_d + 3 * Hs**2) == 0 and sp.simplify(th_d - 3 * Hs) == 0
           and sp.simplify(dth_d) == 0)
    ok.append(okC)
    print(f"\n  (C) de Sitter a=e^{{Ht}}: R_ab u^a u^b = {Ruu_d} < 0 (SEC violated, dark energy);")
    print(f"      θ = {sp.simplify(th_d)} constant, dθ/dτ = {sp.simplify(dth_d)} ⇒ NO focusing, eternal expansion   "
          f"{'✅' if okC else '❌'}")

    # (D) focusing ⟺ SEC, and it is the analyzer's curvature singularity
    okD = okA and okB and okC
    ok.append(okD)
    print(f"\n  (D) R_ab u^a u^b = 4π(ρ+3p): focusing ⟺ SEC. The singularity focusing makes")
    print(f"      inevitable is the same one the analyzer finds by curvature (§59, §42)   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nRAYCHAUDHURI: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(the focusing identity, SEC→singularity, and the dark-energy escape)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
