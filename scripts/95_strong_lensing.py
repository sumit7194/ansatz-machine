#!/usr/bin/env python3
"""Step 95 — STRONG-FIELD LENSING: from Eddington's 1919 test to the relativistic images.

Light bending is the oldest test of GR. Far from the hole it is the weak Eddington
deflection α = 4M/b; close to the photon sphere it DIVERGES — a photon can loop the hole
any number of times, producing an infinite sequence of "relativistic images" piled up at
the shadow edge. The deflection is the integral

    α(b) = 2 ∫_{r₀}^∞ b dr / (r²√(1 − b²f(r)/r²)) − π     (static −f,1/f; r₀ = closest approach)

  (A) WEAK: α → 4M/b as b → ∞ (Eddington 1919);
  (B) STRONG: α ≈ −ā·ln(b/b_c − 1) + const as b → b_c (the photon sphere) — logarithmic
      divergence, coefficient ā = 1 for Schwarzschild; photons make >1 loop;
  (C) THE UNIFICATION: the strong-deflection coefficient is ā = Ω_c/λ — the SAME photon-ring
      Lyapunov instability λ that sets the subring demagnification γ (§89) and the ringdown
      damping (§88). So ā·γ = π exactly. Lensing, imaging, and the gravitational-wave
      ringdown all encode one number — the light ring's instability.

Run:  .venv/bin/python scripts/95_strong_lensing.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from observe_rotating import equatorial_observables


def f_schw(r):
    return 1 - 2 / r


def _turning(b, f):
    lo, hi = 2.001, max(b * 1.5, 10.0)
    for _ in range(90):
        m = (lo + hi) / 2
        if m * m / f(m) < b * b:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def deflection(b, f=f_schw, n=40000):
    """Light deflection angle (radians) at impact parameter b, static −f,1/f metric."""
    r0 = _turning(b, f)
    s = 0.0
    for k in range(1, n):
        t = k / n
        w = 1 - t * t                                  # w∈(0,1), w=1-t² regularizes the turning point
        val = 1 - b * b * f(r0 / w) * w * w / (r0 * r0)
        if val > 0:
            s += (b / r0) / math.sqrt(val) * (2 * t) / n
    return 2 * s - math.pi


def main():
    print("STRONG-FIELD LENSING — from Eddington's 1919 test to the relativistic images\n")
    ok = []
    bc = 3 * math.sqrt(3)

    # (A) weak field → 4M/b. (Use moderate b: at huge b the deflection is a tiny difference
    # of large numbers, 2∫≈π, and loses precision. The physical ratio is 1+(15π/16)/b → 1
    # from ABOVE as b→∞.)
    print("  (A) weak deflection α vs Eddington 4M/b (ratio = 1 + 2nd-order, → 1 from above):")
    ratios = []
    for b in (100, 200, 400):
        a = deflection(b, n=80000)
        ratios.append(a / (4 / b))
        print(f"      b={b:4d}M: α={a:.6f} rad, 4M/b={4/b:.6f} (ratio {a/(4/b):.4f})")
    okA = (1.0 <= ratios[0] < 1.05 and ratios[2] < ratios[1] < ratios[0]    # >1, monotone → 1
           and abs(ratios[2] - 1) < 0.015)
    ok.append(okA)
    print(f"      ratio → 1 monotonically as b grows ⇒ α → 4M/b (the 1919 light-bending test)   {'✅' if okA else '❌'}")

    # (B) strong field: logarithmic divergence, slope = ā
    print(f"\n  (B) strong deflection near the photon sphere b_c=3√3={bc:.4f}:")
    pts = []
    for b in (5.25, 5.21, 5.2, 5.1965):
        x = b / bc - 1
        a = deflection(b)
        pts.append((x, a))
        print(f"      b={b:.4f} (b/b_c−1={x:.1e}): α={a:.3f} rad = {a/(2*math.pi):.2f} loops")
    a_coeff = -(pts[-1][1] - pts[1][1]) / (math.log(pts[-1][0]) - math.log(pts[1][0]))   # slope of α vs −ln(x)
    okB = abs(a_coeff - 1) < 0.06 and pts[-1][1] > 2 * math.pi      # ā≈1; photon loops > once
    ok.append(okB)
    print(f"      α diverges as −ā·ln(b/b_c−1): fitted ā={a_coeff:.3f} (Schwarzschild ā=1); loops > 1   "
          f"{'✅' if okB else '❌'}")

    # (C) the unification: ā = Ω_c/λ, ā·γ = π
    rd = equatorial_observables(lambda r: -(1 - 2 / r), lambda r: 0.0,
                                lambda r: r * r, lambda r: 1 / (1 - 2 / r))["prograde"]["ringdown"]
    Omega_c, lam, gamma = rd["Omega_c"], rd["lyapunov"], rd["subring_gamma"]
    a_from_ring = Omega_c / lam
    okC = abs(a_from_ring - a_coeff) < 0.06 and abs(a_coeff * gamma - math.pi) < 0.1
    ok.append(okC)
    print(f"\n  (C) unification — strong-deflection ā vs the photon ring (Ω_c={Omega_c:.4f}, λ={lam:.4f}, γ={gamma:.4f}):")
    print(f"      ā(lensing)={a_coeff:.3f}  ≈  Ω_c/λ={a_from_ring:.3f};   ā·γ={a_coeff*gamma:.3f} = π={math.pi:.3f}")
    print(f"      lensing, the subrings (§89), and the ringdown (§88) all encode ONE λ — the light ring's   "
          f"{'✅' if okC else '❌'}")

    passed = all(ok)
    print(f"\nSTRONG LENSING: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(weak→4M/b; strong log-divergence ā=1; ā=Ω_c/λ and ā·γ=π — lensing, subrings, ringdown share one λ)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
