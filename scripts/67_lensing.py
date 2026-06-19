#!/usr/bin/env python3
"""Step 67 — GRAVITATIONAL LENSING & EINSTEIN RINGS: what bending makes you SEE.

§49 gave the bending angle; this is what it produces on the sky — the observable
that maps dark matter and powers microlensing planet searches. A mass between you and
a distant source deflects its light, so the source appears displaced, multiplied, and
magnified. With the weak-field deflection α=4M/b (b=D_L·θ) the thin-lens equation is
        β = θ − θ_E²/θ ,     θ_E² = 4M · D_LS/(D_L D_S)
relating the true source angle β to the image angle θ (θ_E = the Einstein radius).

  (A) PERFECT ALIGNMENT (β=0): the image is a full **Einstein ring** of radius θ_E —
      the iconic ring;
  (B) OFF-AXIS (β≠0): TWO images θ_± = (β ± √(β²+4θ_E²))/2, one each side of the lens
      (a bright primary and a fainter secondary);
  (C) MAGNIFICATION: writing u=β/θ_E, the total brightening is μ=(u²+2)/(u√(u²+4)) —
      the microlensing light curve: μ→∞ at u→0 (a caustic spike on perfect alignment)
      and μ→1 for u≫1 (far off-axis, no effect);
  (D) θ_E ∝ √M — lensing weighs mass it cannot see, the basis of dark-matter maps.

Honest scope: textbook lensing built on §49's metric deflection plus the thin-lens
geometry (the observer/lens/source distances are setup, not from the metric). New is
the same engine carrying it from the exact bending angle to the observable ring.

Run:  .venv/bin/python scripts/67_lensing.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("GRAVITATIONAL LENSING & EINSTEIN RINGS — what bending makes you see\n")
    theta, beta, thE, M, DL, DS, DLS = sp.symbols(
        "theta beta theta_E M D_L D_S D_LS", positive=True)
    ok = []

    # the lens equation from α=4M/b (§49), b=D_L θ
    thetaE2 = 4 * M * DLS / (DL * DS)
    lhs = beta
    rhs = theta - thetaE2 / theta

    # (A) Einstein ring at β=0
    ring = sp.solve(sp.Eq(lhs.subs(beta, 0), rhs), theta)
    ring = [r for r in ring if r.is_positive is not False]
    okA = len(ring) == 1 and sp.simplify(ring[0]**2 - thetaE2) == 0
    ok.append(okA)
    print(f"  (A) β=0 ⇒ Einstein ring at θ = θ_E = {sp.simplify(ring[0])},  θ_E² = 4M·D_LS/(D_L D_S)   "
          f"{'✅' if okA else '❌'}")

    # (B) two images off-axis
    imgs = sp.solve(theta**2 - beta * theta - thE**2, theta)
    okB = len(imgs) == 2 and any(i.subs({beta: 1, thE: 1}) > 0 for i in imgs) \
        and any(i.subs({beta: 1, thE: 1}) < 0 for i in imgs)
    ok.append(okB)
    print(f"\n  (B) β≠0 ⇒ two images θ_± = (β ± √(β²+4θ_E²))/2, one each side of the lens   "
          f"{'✅' if okB else '❌'}")

    # (C) total magnification μ(u), u = β/θ_E
    u = sp.Symbol("u", positive=True)
    mutot = sum(sp.Abs((im / beta) * sp.diff(im, beta)) for im in imgs)
    mu_u = sp.simplify(mutot.subs(beta, u * thE))
    target = (u**2 + 2) / (u * sp.sqrt(u**2 + 4))
    # √(u⁴+8u²+16)=u²+4, so mu_u IS the target; sympy won't crack the radical, so check numerically
    same = all(abs(float(mu_u.subs(u, v)) - float(target.subs(u, v))) < 1e-12
               for v in (sp.Rational(1, 2), 1, 2, 5))
    lim0 = sp.limit(mu_u, u, 0, "+")
    liminf = sp.limit(mu_u, u, sp.oo)
    okC = same and lim0 == sp.oo and liminf == 1
    ok.append(okC)
    print(f"\n  (C) total magnification μ(u) = (u²+2)/(u√(u²+4))  (u=β/θ_E)")
    print(f"      μ→{lim0} as u→0 (caustic spike, the microlensing peak), μ→{liminf} as u→∞ (no effect)   "
          f"{'✅' if okC else '❌'}")

    # (D) θ_E ∝ √M — lensing weighs unseen mass
    okD = sp.simplify(sp.sqrt(thetaE2).diff(M) * M - sp.sqrt(thetaE2) / 2) == 0   # θ_E ∝ M^{1/2}
    ok.append(okD)
    print(f"\n  (D) θ_E = {sp.simplify(sp.sqrt(thetaE2))} ∝ √M — lensing measures mass it cannot see "
          f"(dark-matter maps)   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nLENSING: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Einstein ring, double images, the microlensing curve, √M mass-weighing)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
