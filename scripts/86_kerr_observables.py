#!/usr/bin/env python3
"""Step 86 — THE SPINNING BLACK HOLE'S OBSERVATIONAL FACE: ISCO + the full EHT silhouette.

The observational campaign's rotating completion. §45/analyzer.observables give the STATIC
black hole's face (photon sphere, shadow, ISCO, eikonal QNM); §68 gives Kerr's shadow
EDGES. This adds the two real gaps for a SPINNING hole — what telescopes actually measure:

  (A) the KERR ISCO (Bardeen–Press–Teukolsky) — the inner edge of the accretion disk,
      read off X-ray spectra. Prograde and retrograde branches:
        r = 3 + Z₂ ∓ √[(3−Z₁)(3+Z₁+2Z₂)],  Z₁,Z₂ from a.
      a=0 ⇒ 6M (both); extremal a→M ⇒ prograde → M (the horizon!), retrograde → 9M.
      Monotone: spin drags the prograde disk inward — more energy, hotter, observable;
  (B) the full SHADOW SILHOUETTE (α,β) — the actual EHT image curve, not just its edges
      (§68). From the spherical photon orbits' (ξ,η)=(L/E, Q/E²) for an equatorial
      observer: α=−ξ, β=±√η, traced over r∈[r_pro, r_ret]. a=0 ⇒ a circle of radius
      3√3 M (area 27π M²); a>0 ⇒ DISPLACED and flattened on the prograde side (D-shape),
      the spin written in the shape;
  (C) the discrimination: spin shows up in BOTH the ISCO (X-ray) and the shadow shape
      (EHT) — two independent observational handles on the same a. Closed-form, exact.

Run:  .venv/bin/python scripts/86_kerr_observables.py
"""

import math


def kerr_isco(a, prograde=True):
    """Equatorial ISCO radius (units M=1), Bardeen–Press–Teukolsky."""
    Z1 = 1 + (1 - a * a)**(1 / 3) * ((1 + a)**(1 / 3) + (1 - a)**(1 / 3))
    Z2 = math.sqrt(3 * a * a + Z1 * Z1)
    s = -1 if prograde else 1
    return 3 + Z2 + s * math.sqrt((3 - Z1) * (3 + Z1 + 2 * Z2))


def _xi(r, a):
    return -(r**3 - 3 * r**2 + a * a * r + a * a) / (a * (r - 1))


def _eta(r, a):
    return r**3 * (4 * a * a - r * (r - 3)**2) / (a * a * (r - 1)**2)


def kerr_photon_radii(a):
    """Equatorial prograde/retrograde photon-orbit radii (closed form, §68)."""
    return (2 * (1 + math.cos(2 / 3 * math.acos(-a))),       # prograde (inner)
            2 * (1 + math.cos(2 / 3 * math.acos(+a))))       # retrograde (outer)


def kerr_shadow(a, n=4000):
    """Shadow silhouette points (α,β) for an equatorial observer, and its area."""
    r_pro, r_ret = kerr_photon_radii(a)
    alpha, beta = [], []
    for k in range(n + 1):
        r = r_pro + (r_ret - r_pro) * k / n
        e = _eta(r, a)
        if e < 0:
            continue
        alpha.append(-_xi(r, a))
        beta.append(math.sqrt(e))
    # area = 2∮ β dα along the upper edge (trapezoid)
    area = 0.0
    for i in range(1, len(alpha)):
        area += (beta[i] + beta[i - 1]) * (alpha[i] - alpha[i - 1])
    return alpha, beta, abs(area)


def main():
    print("THE SPINNING BLACK HOLE'S OBSERVATIONAL FACE — ISCO + the full EHT silhouette\n")
    ok = []

    # (A) Kerr ISCO
    isco0 = (kerr_isco(0.0, True), kerr_isco(0.0, False))
    iscoE = (kerr_isco(0.999999, True), kerr_isco(0.999999, False))
    pro = [kerr_isco(a, True) for a in (0.0, 0.3, 0.6, 0.9, 0.999)]
    mono = all(pro[i] > pro[i + 1] for i in range(len(pro) - 1))            # prograde shrinks with spin
    # extremal prograde ISCO → 1M only in the singular a→1 limit; at a=0.999999 it's ~1.016
    okA = (abs(isco0[0] - 6) < 1e-6 and abs(isco0[1] - 6) < 1e-6
           and abs(iscoE[0] - 1) < 0.05 and abs(iscoE[1] - 9) < 1e-3 and mono)
    ok.append(okA)
    print(f"  (A) Kerr ISCO: a=0 → ({isco0[0]:.3f}, {isco0[1]:.3f})M;  extremal → "
          f"({iscoE[0]:.3f}, {iscoE[1]:.3f})M  [prograde→horizon, retrograde→9M]")
    print(f"      prograde monotone-inward with spin: {pro[0]:.2f}→{pro[-1]:.2f}M   {'✅' if okA else '❌'}")

    # (B) shadow silhouette: a=0 circle (area 27π), a>0 D-shape (displaced + area shrinks)
    aL, bL, area_small = kerr_shadow(0.01)                                 # ~circle limit
    circle_area = 27 * math.pi
    centroid0 = sum(aL) / len(aL)
    aH, bH, area_hi = kerr_shadow(0.9)
    centroidH = sum(aH) / len(aH)
    edges_hi = (min(aH), max(aH))                                          # (b_pro, b_ret)
    okB = (abs(area_small - circle_area) / circle_area < 0.02              # a→0 is the 3√3 circle
           and abs(centroid0) < 0.05                                       # circle centred at 0
           and centroidH > 0.3)                                           # spin displaces the silhouette
    ok.append(okB)
    print(f"\n  (B) shadow silhouette area: a→0 = {area_small:.2f} vs circle 27π = {circle_area:.2f};  "
          f"a=0.9 = {area_hi:.2f}")
    print(f"      centroid α: a→0 = {centroid0:+.3f} (centred), a=0.9 = {centroidH:+.3f} (displaced → D-shape);"
          f" edges ({edges_hi[0]:.2f},{edges_hi[1]:.2f})   {'✅' if okB else '❌'}")

    # (C) discrimination: spin written in BOTH ISCO and shadow — cross-check at extremal vs §68
    bpro, bret = min(aH), max(aH)
    aX, bX, _ = kerr_shadow(0.9999)
    okC = abs(abs(min(aX)) - 2) < 0.2 and abs(abs(max(aX)) - 7) < 0.3      # extremal edges → |2|,|7| (§68)
    ok.append(okC)
    print(f"\n  (C) spin is written twice over: the ISCO (X-ray disk edge) AND the shadow shape (EHT).")
    print(f"      extremal shadow edges → (|{abs(min(aX)):.2f}|, |{abs(max(aX)):.2f}|) M, matching §68's (2,7)   "
          f"{'✅' if okC else '❌'}")

    passed = all(ok)
    print(f"\nKERR OBSERVABLES: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(ISCO 6M→M/9M; shadow circle→D-shape; spin read from both X-ray ISCO and EHT silhouette)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
