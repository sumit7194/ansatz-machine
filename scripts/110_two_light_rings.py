#!/usr/bin/env python3
"""Step 110 — the two-light-ring test: a horizon-INDEPENDENT black-hole-vs-mimicker discriminator
(plan item 3: the full engine on a horizonless ultracompact object).

§90 showed a shadow proves a photon sphere, not a horizon. This sharpens 'how would you tell it's not a
black hole?' into a metric-computable YES/NO that needs neither the horizon nor the singularity: COUNT
the light rings. A black hole has exactly ONE circular photon orbit (unstable, the peak of V=f/r^2 at
r=3M for Schwarzschild). A horizonless ULTRACOMPACT object (surface radius between the light-ring radius
3M and the Buchdahl bound 9M/4, i.e. compactness 1/3 < M/R < 4/9) has TWO: the same outer UNSTABLE ring
PLUS an inner STABLE 'anti-photon sphere' inside the matter. The inner stable ring is the horizonless
signature (and the seat of the nonlinear light-ring instability / the GW-echo phenomenology of
Cardoso-Pani et al).

We reuse the engine's EXACT constant-density (Schwarzschild interior) star (§53) — no new metric — made
ultracompact, and just count/classify the extrema of the photon potential V(r)=f(r)/r^2 (MAX=unstable
ring, MIN=stable ring). All algebraic; no orbit integration.

  (A) UCO (M/R=0.435): horizonless (R>2M) with TWO light rings (interior STABLE + exterior unstable).
  (B) Schwarzschild BH: ONE (unstable) light ring at 3M.
  (C) THRESHOLD: sweep compactness — the inner stable ring APPEARS exactly as M/R crosses 1/3 (R=3M);
      a merely-compact star (M/R<1/3) has one ring like a BH; ultracompactness is what splits them.
  (D) the star is physical + horizonless: M/R < 4/9 (Buchdahl, §53) and R > 2M (no horizon).

Optional dep: numpy. Repro: .venv/bin/python scripts/110_two_light_rings.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import numpy as np
    _HAVE_NUMPY = True
except ImportError:
    _HAVE_NUMPY = False


def _f_star(r, M, R):
    """Schwarzschild-interior redshift^2 (r<=R) matched to the exterior 1-2M/r (r>R)."""
    if r <= R:
        return (1.5 * math.sqrt(1 - 2 * M / R) - 0.5 * math.sqrt(1 - 2 * M * r * r / R**3))**2
    return 1 - 2 * M / r


def light_rings(ff, rmin=1e-3, rmax=8.0, n=80000):
    """extrema of the photon potential V=f/r^2 in (rmin, rmax): (r, 'stable'|'unstable').
    rmin excludes any horizon (no static photon orbits inside it)."""
    rs = np.linspace(rmin, rmax, n)
    V = np.array([ff(r) / (r * r) for r in rs])
    out = []
    for i in range(2, len(rs) - 2):
        if (V[i] - V[i - 1]) * (V[i + 1] - V[i]) < 0:
            out.append((rs[i], "unstable" if V[i] > V[i - 1] else "stable"))
    return out


def main():
    if not _HAVE_NUMPY:
        print("TWO LIGHT RINGS: SKIPPED (numpy not installed)")
        return 0
    ok = []
    M = 1.0

    # (A) ultracompact horizonless star
    R = 2.3                                             # M/R=0.435: 1/3 < C < 4/9
    lr = light_rings(lambda r: _f_star(r, M, R))
    inner = [x for x in lr if x[0] < R and x[1] == "stable"]
    outer = [x for x in lr if x[0] > R and x[1] == "unstable"]
    okA = len(lr) == 2 and len(inner) == 1 and len(outer) == 1
    ok.append(okA)
    print(f"  (A) horizonless UCO (M=1, R={R}, M/R={M/R:.3f}): {len(lr)} light rings")
    for (r, k) in lr:
        print(f"        r={r:.4f}  {k}  ({'interior' if r < R else 'exterior'})")
    print(f"      inner STABLE + outer unstable = the horizonless signature   {'✅' if okA else '❌'}")

    # (B) Schwarzschild BH control — scan only the exterior r>2M (no static photon orbit inside a horizon)
    lrb = light_rings(lambda r: 1 - 2 * M / r, rmin=2 * M + 1e-3)
    okB = len(lrb) == 1 and lrb[0][1] == "unstable" and abs(lrb[0][0] - 3 * M) < 1e-2
    ok.append(okB)
    print(f"\n  (B) Schwarzschild BH (exterior): {len(lrb)} light ring — "
          + ", ".join(f"r={r:.3f} {k}" for r, k in lrb) + f"   {'✅' if okB else '❌'}")

    # (C) ultracompactness threshold: the INNER STABLE ring exists iff M/R>1/3 (R<3M). A normal star
    # (R>3M) has NO light ring at all (the would-be r=3M ring is buried in matter); the pair appears
    # together as the surface crosses r=3M.
    def n_stable(R_):
        return sum(1 for (r, k) in light_rings(lambda r: _f_star(r, M, R_)) if k == "stable")
    below = n_stable(3.5)     # M/R=0.286 < 1/3
    above = n_stable(2.6)     # M/R=0.385 > 1/3
    okC = below == 0 and above == 1
    ok.append(okC)
    print(f"\n  (C) inner STABLE ring: R=3.5 (M/R=0.29) -> {below}; R=2.6 (M/R=0.385) -> {above}")
    print(f"      the inner stable ring exists ONLY above ultracompactness M/R=1/3   {'✅' if okC else '❌'}")

    # (D) physical + horizonless
    okD = (M / R < 4.0 / 9.0) and (R > 2 * M) and (1.0 / 3.0 < M / R)
    ok.append(okD)
    print(f"\n  (D) M/R={M/R:.3f}: horizonless (>2M surface), Buchdahl-allowed (<4/9), ultracompact (>1/3)"
          f"   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nTWO LIGHT RINGS: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(inner stable ring = horizon-independent 'not a black hole' signature; BH has one, UCO has two)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
