#!/usr/bin/env python3
"""Step 63 — PROPER DISTANCE & THE EMBEDDING DIAGRAM: how stretched is space?

A visual, geometric lens (a change of scenery from the curvature/symmetry/charge
work): the coordinate r is NOT distance. The radial coordinate labels spheres by
their circumference (2πr), but the actual ruler distance between them — the proper
distance ℓ(r)=∫dr/√f — is larger near a black hole: space is stretched. Picture an
equatorial slice (t=const, θ=π/2) as a curved surface embedded in flat 3D; its height
z(r) is the famous **Flamm paraboloid**, the "funnel" of every black-hole illustration.

  (A) the EMBEDDING equation: a flat-3D surface z(r) reproduces the slice's geometry
      when (dz/dr)²+1 = g_rr. For Schwarzschild the solution is z = √(8M(r−2M)) —
      the Flamm paraboloid — verified exactly: (dz/dr)²+1 = 1/f = g_rr;
  (B) the THROAT: at the horizon r=2M, z=0 and dz/dr→∞ — a vertical funnel wall, the
      narrowest point; the maximal extension joins a mirror sheet into the
      Einstein–Rosen bridge (a wormhole — ties to §38);
  (C) PROPER DISTANCE is finite but stretched: the ruler distance from horizon to
      r=6M (M=1) is ≈7.19, well over the coordinate gap 4 — and the horizon is
      reachable in finite proper distance (the 1/√f singularity is integrable);
  (D) far away space FLATTENS: dz/dr→0 as r→∞ (asymptotically flat — proper distance
      → coordinate distance, the funnel levels out).

Honest scope: textbook (Flamm 1916). New is the same engine checking the embedding
equation and the stretch straight off the metric, beside everything else.

Run:  .venv/bin/python scripts/63_embedding.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("PROPER DISTANCE & THE EMBEDDING DIAGRAM — how stretched is space?\n")
    r = sp.Symbol("r", positive=True)
    M = sp.Symbol("M", positive=True)
    f = 1 - 2 * M / r
    g_rr = 1 / f
    ok = []

    # (A) the Flamm paraboloid solves the embedding equation (dz/dr)²+1 = g_rr
    z = sp.sqrt(8 * M * (r - 2 * M))
    embed = sp.simplify((sp.diff(z, r))**2 + 1 - g_rr)
    okA = embed == 0
    ok.append(okA)
    print(f"  (A) Flamm paraboloid z = √(8M(r−2M)):  (dz/dr)²+1 − g_rr = {embed}   "
          f"{'✅ embeds the slice exactly' if okA else '❌'}")

    # (B) the throat: z=0 and dz/dr→∞ at r=2M
    z_h = sp.simplify(z.subs(r, 2 * M))
    slope_h = sp.limit(sp.diff(z, r), r, 2 * M, "+")
    okB = z_h == 0 and slope_h == sp.oo
    ok.append(okB)
    print(f"\n  (B) throat at r=2M:  z={z_h}, dz/dr→{slope_h}  (vertical wall — the funnel's neck;")
    print(f"      the maximal extension is the Einstein–Rosen bridge, §38)   {'✅' if okB else '❌'}")

    # (C) proper distance: finite but larger than coordinate distance
    import mpmath
    ell = float(mpmath.quad(lambda rr: 1 / mpmath.sqrt(1 - 2 / rr), [2, 6]))      # M=1
    ell_near = float(mpmath.quad(lambda rr: 1 / mpmath.sqrt(1 - 2 / rr), [2.0 + 1e-9, 2.5]))
    okC = ell > 4 and ell_near < 10            # stretched, and finite to the horizon
    ok.append(okC)
    print(f"\n  (C) proper distance (M=1): horizon→6M = {ell:.3f}  vs coordinate gap 4.0 "
          f"⇒ space STRETCHED   {'✅' if ell > 4 else '❌'}")
    print(f"      just-above-horizon (2→2.5) = {ell_near:.3f} ⇒ finite, the horizon is reachable   "
          f"{'✅' if okC else '❌'}")

    # (D) far field flattens
    okD = sp.limit(sp.sqrt(g_rr - 1), r, sp.oo) == 0
    ok.append(okD)
    print(f"\n  (D) far field: dz/dr = √(g_rr−1) → {sp.limit(sp.sqrt(g_rr-1), r, sp.oo)} as r→∞ "
          f"⇒ space flattens (asymptotically flat)   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nEMBEDDING: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(the Flamm funnel verified, the throat, the stretch, the flat far field)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
