#!/usr/bin/env python3
"""Step 91 — THE EHT IMAGE'S TILT: the shadow shape depends on how the hole faces us.

§86 drew Kerr's shadow for an EDGE-ON observer (the most D-shaped view). But the real
silhouette an interferometer measures depends on the observer's inclination θ_obs to the
spin axis (Bardeen): α = −ξ/sinθ_obs, β = ±√(η + a²cos²θ_obs − ξ²cot²θ_obs), traced over
the spherical photon orbits. This computes the full inclination dependence — directly
relevant to reading the actual M87*/Sgr A* images.

  (A) the shadow ASYMMETRY (centroid displacement / radius) scales with inclination:
      EDGE-ON (90°) is the most displaced D-shape; as the hole turns FACE-ON (θ_obs→0)
      the displacement → 0 and the shadow becomes a CIRCLE — monotone in between;
  (B) limits check: edge-on reproduces §86's displaced silhouette; face-on → circular;
  (C) the SPIN–INCLINATION DEGENERACY: a near-circular shadow does NOT imply low spin — a
      FAST hole seen nearly face-on is also circular. We show a=0.9 at 5° is MORE circular
      than a=0.3 edge-on. M87*'s near-circular ring is consistent with its ~17° (near
      face-on) view; the shape alone cannot fix the spin — you need the brightness
      asymmetry / other messengers. An honest caveat the engine makes quantitative.

Run:  .venv/bin/python scripts/91_shadow_inclination.py
"""

import math


def _xi(r, a):
    return -(r**3 - 3 * r**2 + a * a * r + a * a) / (a * (r - 1))


def _eta(r, a):
    return r**3 * (4 * a * a - r * (r - 3)**2) / (a * a * (r - 1)**2)


def _photon_radii(a):
    return (2 * (1 + math.cos(2 / 3 * math.acos(-a))),
            2 * (1 + math.cos(2 / 3 * math.acos(a))))


def shadow_asymmetry(a, theta_deg, n=6000):
    """Centroid displacement / shadow radius for an observer at inclination θ (0=face-on)."""
    th = math.radians(theta_deg)
    s, c = math.sin(th), math.cos(th)
    cot = c / s if s > 1e-9 else 1e12
    r1, r2 = _photon_radii(a)
    al, be = [], []
    for k in range(n + 1):
        r = r1 + (r2 - r1) * k / n
        X, H = _xi(r, a), _eta(r, a)
        val = H + a * a * c * c - X * X * cot * cot
        if val < 0:
            continue
        al.append(-X / s)
        be.append(math.sqrt(val))
    if not al or max(be) < 1e-6:
        return None
    radius = max(be)                       # vertical half-extent = shadow radius
    centroid = (max(al) + min(al)) / 2
    return abs(centroid) / radius


def main():
    print("THE EHT IMAGE'S TILT — the shadow shape depends on how the hole faces us\n")
    ok = []
    a = 0.9

    # (A) asymmetry scales monotonically with inclination
    incs = (90, 60, 45, 30, 17, 5)
    asy = [shadow_asymmetry(a, t) for t in incs]
    mono = all(asy[i] > asy[i + 1] for i in range(len(asy) - 1))
    okA = mono and asy[0] > 0.3 and asy[-1] < 0.05
    ok.append(okA)
    print(f"  (A) Kerr a={a} shadow asymmetry vs observer inclination:")
    print("      " + ",  ".join(f"{t}°→{x:.3f}" for t, x in zip(incs, asy)))
    print(f"      edge-on most D-shaped ({asy[0]:.2f}); face-on → circular ({asy[-1]:.2f}); monotone   "
          f"{'✅' if okA else '❌'}")

    # (B) limits: edge-on D-shaped (displaced), face-on circular
    edge = shadow_asymmetry(a, 90)
    face = shadow_asymmetry(a, 0.5)
    okB = edge > 0.3 and face < 0.01
    ok.append(okB)
    print(f"\n  (B) limits: edge-on (90°) asymmetry={edge:.3f} (D-shaped, cf §86); "
          f"face-on (0.5°) asymmetry={face:.4f} (circular)   {'✅' if okB else '❌'}")

    # (C) spin–inclination degeneracy: fast hole face-on is MORE circular than slow hole edge-on
    fast_faceon = shadow_asymmetry(0.9, 5)
    slow_edgeon = shadow_asymmetry(0.3, 90)
    m87 = shadow_asymmetry(0.9, 17)
    okC = fast_faceon < slow_edgeon and m87 < 0.2
    ok.append(okC)
    print(f"\n  (C) spin–inclination degeneracy: a=0.9 face-on (5°) asymmetry={fast_faceon:.3f} "
          f"< a=0.3 edge-on (90°)={slow_edgeon:.3f}")
    print(f"      ⇒ a circular shadow does NOT mean low spin. M87* (~17°, near face-on): asymmetry={m87:.3f} "
          f"(nearly circular)")
    print(f"      the shape alone can't fix spin — need brightness asymmetry / other messengers   "
          f"{'✅' if okC else '❌'}")

    passed = all(ok)
    print(f"\nSHADOW INCLINATION: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(asymmetry scales with tilt; face-on→circular; spin–inclination degeneracy quantified)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
