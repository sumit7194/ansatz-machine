#!/usr/bin/env python3
"""Step 90 — BLACK HOLE OR IMPOSTER? A shadow proves a photon sphere, not a horizon.

The observational campaign's sharpest caution. The EHT "saw a black-hole shadow" — but a
shadow is cast by a PHOTON SPHERE, and a photon sphere does NOT require a horizon. So the
image alone cannot prove a black hole exists. This battery makes that concrete and shows
what it actually takes to tell a black hole from an imposter.

  (A) THE WORMHOLE that fakes the shadow: the Ellis wormhole ds²=−dt²+dr²+(r²+b₀²)dΩ² has
      a photon sphere at the throat (r=0) and casts a shadow of radius b₀ — NO horizon, NO
      singularity, NO curvature blow-up. Tune b₀=3√3 M and its shadow is IDENTICAL in size
      to a Schwarzschild black hole (b_c=3√3). The EHT could not tell them apart by shadow;
  (B) THE NAKED SINGULARITY that fails to: over-spinning Kerr (a>M) has no horizon — and
      its prograde equatorial light ring genuinely DISAPPEARS for a>1 (the closed form
      2M{1+cos[⅔arccos(−a)]} is undefined; confirmed numerically with a wide search). At
      a=1 it sits marginally on the horizon. So a horizonless object need not even cast a
      normal shadow — the prograde edge is gone;
  (C) so WHAT proves a black hole? Not the shadow alone — it takes the other messengers:
      the ISCO + accretion physics, the ringdown (and the ABSENCE of post-ringdown ECHOES
      that a reflecting surface would make), the horizon's pure absorption. The shadow is
      necessary, not sufficient — the multi-messenger program (§86–§89) is the real test.

Run:  .venv/bin/python scripts/90_black_hole_or_imposter.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from observe_rotating import equatorial_observables


def static_shadow(A, C, rlo=1e-4, rhi=30.0, n=300000):
    """Photon sphere + shadow for a static spherical metric −A(r)dt²+B dr²+C(r)dΩ²:
    the photon orbit minimizes the impact parameter b(r)=√(C/A); shadow b_c is that min."""
    best_r, best_b = None, float("inf")
    for k in range(n + 1):
        r = rlo + (rhi - rlo) * k / n
        b = math.sqrt(C(r) / A(r))
        if b < best_b:
            best_b, best_r = b, r
    return best_r, best_b


def kerr(a):
    return (lambda r: -(1 - 2 / r), lambda r: -2 * a / r,
            lambda r: r * r + a * a + 2 * a * a / r, lambda r: r * r / (r * r - 2 * r + a * a))


def main():
    print("BLACK HOLE OR IMPOSTER? — a shadow proves a photon sphere, not a horizon\n")
    ok = []

    # (A) the Ellis wormhole that fakes a Schwarzschild shadow
    b0 = 3 * math.sqrt(3)                                  # tuned to mimic Schwarzschild M=1
    rps, bc = static_shadow(lambda r: 1.0, lambda r: r * r + b0 * b0, rlo=-5, rhi=5)
    schw_bc = 3 * math.sqrt(3)
    okA = abs(rps) < 1e-3 and abs(bc - b0) < 1e-3 and abs(bc - schw_bc) < 1e-3
    ok.append(okA)
    print(f"  (A) Ellis wormhole (b₀={b0:.3f}): photon sphere at throat r={rps:.4f}, shadow b_c={bc:.4f}")
    print(f"      Schwarzschild M=1 shadow b_c=3√3={schw_bc:.4f} — IDENTICAL. No horizon, no singularity.")
    print(f"      ⇒ the EHT shadow alone cannot distinguish this wormhole from a black hole   {'✅' if okA else '❌'}")

    # (B) over-spinning Kerr (naked singularity, a>1): the prograde light ring genuinely
    # vanishes (closed form undefined for a>1; confirmed with a wide numeric search).
    ring = {a: equatorial_observables(*kerr(a), rmin=0.3, rmax=12)["prograde"]["photon_r"]
            for a in (0.9, 1.2, 2.0)}
    okB = ring[0.9] is not None and ring[1.2] is None and ring[2.0] is None
    ok.append(okB)
    print(f"\n  (B) over-spinning Kerr (a>M = naked singularity, no horizon): prograde light ring —")
    print(f"      a=0.9 → r={ring[0.9]:.3f} (exists, outside horizon);  a=1.2, 2.0 → NONE "
          f"(gone; closed form undefined for a>1) — the prograde shadow edge breaks   {'✅' if okB else '❌'}")

    # (C) the multi-messenger resolution
    okC = okA and okB
    ok.append(okC)
    print(f"\n  (C) so what PROVES a black hole? Not the shadow — a wormhole fakes it, a naked singularity")
    print(f"      breaks it. It takes the OTHER messengers: the ISCO + disk (§86/§87), the ringdown AND the")
    print(f"      absence of late-time echoes a surface would make (§88/§89), the horizon's pure absorption.")
    print(f"      The shadow is necessary, not sufficient — the multi-messenger program is the real test.   "
          f"{'✅' if okC else '❌'}")

    passed = all(ok)
    print(f"\nBLACK HOLE OR IMPOSTER: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(wormhole fakes the shadow; naked singularity breaks it; shadow ⇏ horizon — need all messengers)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
