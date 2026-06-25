#!/usr/bin/env python3
"""Step 94 — RELATIVISTIC PRECESSION & QPOs: frame-dragging you can time.

A circular orbit has THREE frequencies, not one: the orbital ν_φ, the radial epicyclic
ν_r (how fast a slightly eccentric orbit oscillates in radius), and the vertical epicyclic
ν_θ (how fast a slightly tilted orbit oscillates up/down). Their splittings are
observable strong-field effects:

  • periastron precession  ν_φ − ν_r  — the orbit's ellipse turns (Mercury's anomaly, now
    in the strong field); nonzero even for a non-spinning hole;
  • NODAL precession  ν_φ − ν_θ  — the orbit plane is DRAGGED around (Lense–Thirring frame
    dragging); ZERO for Schwarzschild, grows with spin — pure gravitomagnetism.

These are exactly the quasi-periodic oscillations (QPOs) seen in accreting black-hole
X-ray binaries (the relativistic-precession model): timing them measures the spin and
tests GR in the strong field.

  (A) the radial epicyclic ν_r → 0 at the ISCO (marginal stability) — a cross-check of the
      ISCO via an independent frequency;
  (B) periastron precession is nonzero even at a=0 (the strong-field Mercury effect);
  (C) NODAL Lense–Thirring precession is exactly 0 for Schwarzschild and grows with spin —
      the frame-dragging signature;
  (D) the SCALE: for a 10 M⊙ hole the ISCO orbital frequency is ~hundreds of Hz (the
      observed kHz-QPO band), the nodal precession ~Hz (the low-frequency QPO).

Run:  .venv/bin/python scripts/94_precession_qpos.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from observe_rotating import equatorial_observables

GM_C3_SUN = 4.925e-6   # GM_sun/c^3 in seconds (geometric freq /M → Hz: divide by M[M_sun]*this)


def kerr(a):
    return (lambda r: -(1 - 2 / r), lambda r: -2 * a / r,
            lambda r: r * r + a * a + 2 * a * a / r, lambda r: r * r / (r * r - 2 * r + a * a))


def kerr_freqs(a, r):
    """Orbital, radial-epicyclic, vertical-epicyclic frequencies (geometric, M=1, prograde)."""
    nu_phi = 1 / (2 * math.pi * (r**1.5 + a))
    rad = 1 - 6 / r + 8 * a / r**1.5 - 3 * a * a / r**2
    vert = 1 - 4 * a / r**1.5 + 3 * a * a / r**2
    nu_r = nu_phi * math.sqrt(rad) if rad > 0 else 0.0
    nu_th = nu_phi * math.sqrt(vert) if vert > 0 else 0.0
    return nu_phi, nu_r, nu_th


def main():
    print("RELATIVISTIC PRECESSION & QPOs — frame-dragging you can time\n")
    ok = []

    # (A) ν_r → 0 at the ISCO
    print("  (A) radial epicyclic ν_r at the ISCO (should vanish — marginal stability):")
    okA = True
    for a in (0.0, 0.5, 0.9):
        risco = equatorial_observables(*kerr(a))["prograde"]["isco"]
        _, nr, _ = kerr_freqs(a, risco)
        okA = okA and nr < 1e-3
        print(f"      a={a}: ISCO={risco:.3f}M, ν_r={nr:.5f}")
    ok.append(okA)
    print(f"      ν_r=0 at the ISCO — the radial epicyclic vanishing IS the inner edge   {'✅' if okA else '❌'}")

    # (B) periastron precession nonzero even at a=0 (strong-field Mercury)
    r = 8.0
    nphi0, nr0, nth0 = kerr_freqs(0.0, r)
    peri0 = nphi0 - nr0
    okB = peri0 > 1e-4
    ok.append(okB)
    print(f"\n  (B) periastron precession ν_φ−ν_r at r={r:.0f}M: Schwarzschild = {peri0:.5f} > 0 "
          f"(the strong-field Mercury effect, no spin needed)   {'✅' if okB else '❌'}")

    # (C) nodal Lense–Thirring precession: 0 for Schwarzschild, grows with spin
    print(f"\n  (C) NODAL (Lense–Thirring) precession ν_φ−ν_θ at r={r:.0f}M (frame-dragging):")
    nods = []
    for a in (0.0, 0.3, 0.6, 0.9, 0.998):
        nphi, nr, nth = kerr_freqs(a, r)
        nods.append(nphi - nth)
        print(f"      a={a}: ν_φ−ν_θ = {nphi - nth:.6f}")
    okC = abs(nods[0]) < 1e-9 and all(nods[i] < nods[i + 1] for i in range(len(nods) - 1))
    ok.append(okC)
    print(f"      exactly 0 at a=0 (no frame-dragging), monotone up with spin ⇒ pure gravitomagnetism   "
          f"{'✅' if okC else '❌'}")

    # (D) the observable scale: 10 M_sun BH
    M = 10.0
    risco = equatorial_observables(*kerr(0.9))["prograde"]["isco"]
    nphi, nr, nth = kerr_freqs(0.9, risco)
    nphi6, _, _ = kerr_freqs(0.0, equatorial_observables(*kerr(0.0))["prograde"]["isco"])
    f_isco_hz = nphi6 / (M * GM_C3_SUN)
    f_nodal_hz = (kerr_freqs(0.9, 20.0)[0] - kerr_freqs(0.9, 20.0)[2]) / (M * GM_C3_SUN)
    okD = 100 < f_isco_hz < 1000 and 0.1 < f_nodal_hz < 50
    ok.append(okD)
    print(f"\n  (D) scale for a {M:.0f} M⊙ hole: ISCO orbital frequency ≈ {f_isco_hz:.0f} Hz (the kHz-QPO band);")
    print(f"      nodal precession at r=20M ≈ {f_nodal_hz:.1f} Hz (the low-frequency QPO) ⇒ QPOs time the spin   "
          f"{'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nPRECESSION & QPOs: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(ν_r=0 at ISCO; periastron even at a=0; nodal LT precession ∝ spin; matches the observed QPO band)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
