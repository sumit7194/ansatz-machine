#!/usr/bin/env python3
"""Step 48 — KERR'S RING SINGULARITY (what the symbolic Kretschmann couldn't reach).

A loose thread closed by the numeric engine. The analyzer marks off-diagonal
singularities UNKNOWN because the symbolic Kretschmann of Kerr swamps/OOMs. The
finite-difference Kretschmann (numeric_curvature.py) computes it anyway — and
reveals Kerr's famous structure: the singularity is a RING, not a point.

Kerr's curvature diverges only where Σ = r² + a²cos²θ = 0, i.e. r=0 AND θ=π/2
(u=cosθ=0) — the equatorial ring. Approach r→0 ON the equator and K → ∞; approach
r→0 OFF the equator and K stays FINITE (you'd pass through the disk, not hit a
singularity). The numeric Kretschmann shows exactly this.

Validation: numeric K matches the exact Schwarzschild K=48M²/r⁶, then exhibits
Kerr's ring (diverging on the equator as r→0, bounded off it).

Run:  .venv/bin/python scripts/48_ring_singularity.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from numeric_curvature import kretschmann_numeric

M, a = 1.0, 0.5


def schwarzschild(x):
    t, r, th, ph = x
    f = 1 - 2 * M / r
    return [[-f, 0, 0, 0], [0, 1 / f, 0, 0], [0, 0, r * r, 0], [0, 0, 0, r * r * math.sin(th)**2]]


def kerr(x):
    t, r, u, ph = x
    s2 = 1 - u * u
    Sig = r * r + a * a * u * u
    D = r * r - 2 * M * r + a * a
    g = [[0.0] * 4 for _ in range(4)]
    g[0][0] = -(D - a * a * s2) / Sig
    g[0][3] = g[3][0] = -a * s2 * (r * r + a * a - D) / Sig
    g[1][1] = Sig / D
    g[2][2] = Sig / s2
    g[3][3] = s2 * ((r * r + a * a)**2 - D * a * a * s2) / Sig
    return g


def main():
    print("KERR'S RING SINGULARITY — numeric Kretschmann does what symbolic can't\n")

    # (1) validate numeric K against the exact Schwarzschild value
    print("  Schwarzschild (validate numeric K vs exact 48M²/r⁶):")
    ok_sch = True
    for rv in (3.0, 5.0):
        K = kretschmann_numeric(schwarzschild, [0, rv, 1.0, 0.4])
        exact = 48 * M**2 / rv**6
        rel = abs(K - exact) / exact
        ok_sch = ok_sch and rel < 1e-2
        print(f"     K(r={rv}) = {K:.5f}   exact {exact:.5f}   rel err {rel:.1e}")

    # (2) Kerr: the singularity is a RING — diverges on the equator, finite off it
    print("\n  Kerr (a=1/2) — approach r→0:")
    eq_far = kretschmann_numeric(kerr, [0, 0.05, 0.0, 0.4])     # equator, r=0.05
    eq_near = kretschmann_numeric(kerr, [0, 0.02, 0.0, 0.4])    # equator, r=0.02 (closer)
    off_far = kretschmann_numeric(kerr, [0, 0.05, 0.5, 0.4])    # off-equator, r=0.05
    off_near = kretschmann_numeric(kerr, [0, 0.02, 0.5, 0.4])   # off-equator, r=0.02
    eq_ratio = abs(eq_near) / abs(eq_far)
    off_ratio = abs(off_near) / abs(off_far)
    print(f"     ON  equator (u=0):   K(0.05)={eq_far:.3e}  →  K(0.02)={eq_near:.3e}   ×{eq_ratio:.0f}  (DIVERGES)")
    print(f"     OFF equator (u=0.5): K(0.05)={off_far:.3e}  →  K(0.02)={off_near:.3e}   ×{off_ratio:.1f}  (bounded)")
    ring = eq_ratio > 50 and off_ratio < 5
    print(f"     → ring singularity: blows up on the equatorial ring, regular off it   {'✅' if ring else '❌'}")

    passed = ok_sch and ring
    print("\n  the numeric Kretschmann reveals Kerr's RING singularity — the structure the")
    print("  analyzer had to mark UNKNOWN (symbolic K OOMs). Off-diagonal singularities, closed.")
    print(f"\nRING SINGULARITY: {'PASSED ✅' if passed else 'FAILED ❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
