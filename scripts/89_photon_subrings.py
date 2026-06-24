#!/usr/bin/env python3
"""Step 89 — THE PHOTON SUBRINGS: one instability, two telescopes.

Light that loops around a black hole n times before reaching us forms a series of nested
"photon subrings" converging on the shadow edge — the interferometric signature the EHT
sees and next-gen space VLBI (BHEX) is built to resolve. Each successive subring is
demagnified by e^{−γ}, with γ the photon ring's instability exponent:

    γ = π · λ / Ω_c      (λ = Lyapunov rate, Ω_c = photon-orbit angular velocity).

  (A) the UNIVERSAL anchor: Schwarzschild γ = π exactly — each subring is e^{−π} ≈ 0.043
      (~23×) fainter than the one outside it;
  (B) SPIN dependence (corotating subrings): γ DECREASES with spin (23× → ~2× demag at
      a→1), so a fast-spinning hole's subrings are nearly equally bright — far easier to
      resolve. Charge (Kerr–Newman) shifts the spacing too;
  (C) THE DEEP LINK: the SAME photon-ring λ sets BOTH the EHT subring demagnification (γ)
      AND the LIGO ringdown damping (ω_I, §88). One orbital instability of one light ring,
      written into two utterly different observations — a quantitative cross-check between
      an image and a gravitational wave.

Uses the general numeric tool (`observe_rotating.py`), so it works for any rotating hole.
Run:  .venv/bin/python scripts/89_photon_subrings.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from observe_rotating import equatorial_observables


def kerr(a):
    return (lambda r: -(1 - 2 / r), lambda r: -2 * a / r,
            lambda r: r * r + a * a + 2 * a * a / r, lambda r: r * r / (r * r - 2 * r + a * a))


def kerr_newman(a, Q):
    return (lambda r: -(1 - (2 * r - Q * Q) / r**2), lambda r: -a * (2 * r - Q * Q) / r**2,
            lambda r: r * r + a * a + a * a * (2 * r - Q * Q) / r**2,
            lambda r: r * r / (r * r - 2 * r + a * a + Q * Q))


def main():
    print("THE PHOTON SUBRINGS — one instability, two telescopes\n")
    ok = []

    # (A) Schwarzschild γ = π
    rd0 = equatorial_observables(*kerr(0.0))["prograde"]["ringdown"]
    g0 = rd0["subring_gamma"]
    okA = abs(g0 - math.pi) < 1e-3
    ok.append(okA)
    print(f"  (A) Schwarzschild: subring exponent γ = {g0:.4f} (π = {math.pi:.4f}); "
          f"demag e^−γ = {math.exp(-g0):.4f} (~{1/math.exp(-g0):.0f}× per subring)   {'✅' if okA else '❌'}")

    # (B) spin dependence: γ decreases with spin; charge shifts it
    gammas = [equatorial_observables(*kerr(a))["prograde"]["ringdown"]["subring_gamma"]
              for a in (0.0, 0.3, 0.6, 0.9, 0.99)]
    mono = all(gammas[i] > gammas[i + 1] for i in range(len(gammas) - 1))
    gkn = equatorial_observables(*kerr_newman(0.6, 0.5))["prograde"]["ringdown"]["subring_gamma"]
    gk6 = gammas[2]
    okB = mono and gammas[-1] < 1.0 and abs(gkn - gk6) > 0.05
    ok.append(okB)
    print(f"\n  (B) Kerr corotating subring γ vs spin a=(0,0.3,0.6,0.9,0.99): "
          + ", ".join(f"{g:.2f}" for g in gammas))
    print(f"      demag a=0 → 0.99: {1/math.exp(-gammas[0]):.0f}× → {1/math.exp(-gammas[-1]):.0f}× "
          f"(high spin ⇒ resolvable subrings); Kerr–Newman γ={gkn:.2f} ≠ Kerr {gk6:.2f}   {'✅' if okB else '❌'}")

    # (C) the deep link, made NON-trivial: the λ that sets the EHT subring γ ALSO sets the
    # LIGO ringdown damping ω_I — and that ω_I matches the INDEPENDENT precise Leaver QNM
    # (§77) to eikonal accuracy. (γ is independently anchored at π in (A).) Both observables
    # are tied to their own references and share the one λ — so the correspondence is real,
    # not a code identity.
    leaver_wI = {0.0: 0.0890, 0.6: 0.0837, 0.9: 0.0649}                   # precise ℓ=m=2 n=0 (Berti tables)
    print(f"\n  (C) one λ, two telescopes — the same λ gives the EHT subring γ AND the LIGO ω_I (vs Leaver):")
    okC = True
    for a in (0.0, 0.6, 0.9):
        rd = equatorial_observables(*kerr(a))["prograde"]["ringdown"]
        e = abs(rd["omega_I"] - leaver_wI[a]) / leaver_wI[a]
        okC = okC and e < 0.10                                            # eikonal ω_I ≈ Leaver
        print(f"      a={a}: λ={rd['lyapunov']:.4f} → subring γ={rd['subring_gamma']:.3f} (EHT) "
              f"& ω_I={rd['omega_I']:.4f} vs Leaver {leaver_wI[a]:.4f} ({100*e:.1f}%, LIGO)  {'✓' if e<0.10 else '✗'}")
    ok.append(okC)
    print(f"      γ anchored at π (A) and ω_I anchored at Leaver — both from ONE λ ⇒ the correspondence is real   "
          f"{'✅' if okC else '❌'}")

    passed = all(ok)
    print(f"\nPHOTON SUBRINGS: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Schwarzschild γ=π; γ falls with spin; same λ in EHT subrings and LIGO ringdown)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
