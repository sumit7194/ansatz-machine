#!/usr/bin/env python3
"""Step 88 — THE THREE MESSENGERS: shadow (EHT) + ISCO (X-ray) + ringdown (LIGO), any hole.

The observational campaign's capstone. From ONE rotating black-hole metric, the engine
predicts what all three of today's black-hole telescopes measure — and whether they could
tell the hole apart from Kerr:

  · EHT      → the shadow (photon-ring impact parameter b),          §86/§87
  · X-ray    → the ISCO (accretion-disk inner edge),                 §87
  · LIGO     → the ringdown frequency (eikonal QNM from the photon    NEW (observe_rotating)
               ring: ω = ℓΩ_c − i(n+½)|λ|, Cardoso correspondence).

  (A) the eikonal ringdown VALIDATES against the precise Leaver spectrum (§77) to eikonal
      accuracy (~3–6% on ω_R for ℓ=2), with the correct spin trend ω_R↑ with a;
  (B) the three messengers, read off one Kerr metric (a=0.6);
  (C) MULTI-MESSENGER DISCRIMINATION with COMPLEMENTARY sensitivity: Kerr–Newman (a global
      change) shifts all three observables; the §85 near-horizon bump shifts the disk-edge
      ones (shadow, ISCO) much more than the photon-ring ringdown — because the three
      messengers probe different radii. So a joint EHT+X-ray+LIGO measurement both sharpens
      the "is it exactly Kerr?" test AND localizes WHERE any deviation lives.

Run:  .venv/bin/python scripts/88_three_messengers.py
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


def deformed_kerr(a, eps):
    return (lambda r: -(1 - 2 / r) * (1 - eps / r**3), lambda r: -2 * a / r,
            lambda r: r * r + a * a + 2 * a * a / r, lambda r: r * r / (r * r - 2 * r + a * a))


# precise Leaver ℓ=m=2, n=0 ω_R (Mω) for validation (Berti et al. tables / §77)
PRECISE_wR = {0.0: 0.3737, 0.3: 0.4317, 0.6: 0.4940, 0.9: 0.6716}


def main():
    print("THE THREE MESSENGERS — shadow (EHT) + ISCO (X-ray) + ringdown (LIGO), any hole\n")
    ok = []

    # (A) eikonal ringdown vs precise QNM (§77), and the spin trend
    print("  (A) eikonal ringdown ω_R from the photon ring vs precise Leaver (§77):")
    errs, wRs = [], []
    for a in (0.0, 0.3, 0.6, 0.9):
        rd = equatorial_observables(*kerr(a))["prograde"]["ringdown"]
        e = abs(rd["omega_R"] - PRECISE_wR[a]) / PRECISE_wR[a]
        errs.append(e)
        wRs.append(rd["omega_R"])
        print(f"      a={a}: eikonal ω_R={rd['omega_R']:.4f} vs precise {PRECISE_wR[a]:.4f} ({100*e:.1f}%), "
              f"ω_I={rd['omega_I']:.4f}")
    trend = all(wRs[i] < wRs[i + 1] for i in range(len(wRs) - 1))
    okA = max(errs) < 0.07 and trend
    ok.append(okA)
    print(f"      max error {100*max(errs):.1f}% (eikonal ℓ=2), ω_R rises with spin {trend}   {'✅' if okA else '❌'}")

    # (B) the three messengers from one Kerr metric
    a = 0.6
    o = equatorial_observables(*kerr(a))["prograde"]
    okB = o["shadow_b"] and o["isco"] and o["ringdown"]
    ok.append(bool(okB))
    print(f"\n  (B) Kerr a={a}, read off one metric: shadow b={o['shadow_b']:.3f}M (EHT), "
          f"ISCO={o['isco']:.3f}M (X-ray), ringdown ω={o['ringdown']['omega_R']:.3f}−{o['ringdown']['omega_I']:.3f}i (LIGO)"
          f"   {'✅' if okB else '❌'}")

    # (C) multi-messenger discrimination. NB: the §85 bump ∝1/r³ is a near-horizon
    # deformation — push it (ε≳2) and the photon ring falls INSIDE the ergosphere where
    # the shadow b=L/E diverges (unphysical); ε=1 keeps it outside (r>2). Guard physical b.
    kn = equatorial_observables(*kerr_newman(a, 0.5))["prograde"]
    df = equatorial_observables(*deformed_kerr(a, 1.0))["prograde"]
    def physical(x):                                    # shadow in a sane range, orbits exist
        return (x["shadow_b"] and 2 < abs(x["shadow_b"]) < 8 and x["isco"] and x["ringdown"])
    def shifts(x):
        return (abs(x["shadow_b"] - o["shadow_b"]), abs(x["isco"] - o["isco"]),
                abs(x["ringdown"]["omega_R"] - o["ringdown"]["omega_R"]))
    kns, dfs = shifts(kn), shifts(df)
    # KN (a global change) moves all three; the near-horizon bump moves the disk-edge
    # observables (shadow, ISCO) but barely the ringdown — messengers probe different radii.
    okC = (physical(kn) and physical(df)
           and all(s > 0.02 for s in kns)            # KN: all three move
           and dfs[0] > 0.02 and dfs[1] > 0.02       # deformed: shadow + ISCO move
           and dfs[2] < dfs[1])                       # deformed ringdown moves LESS (near-horizon)
    ok.append(okC)
    print(f"\n  (C) multi-messenger discrimination at a={a} (Δ from Kerr in shadow b / ISCO / ringdown ω_R):")
    print(f"      Kerr–Newman Q=0.5:  ({kns[0]:.3f}, {kns[1]:.3f}, {kns[2]:.3f})  [b={kn['shadow_b']:.3f}] — all three move")
    print(f"      deformed ε=1:       ({dfs[0]:.3f}, {dfs[1]:.3f}, {dfs[2]:.3f})  [b={df['shadow_b']:.3f}] — disk edge moves, ringdown barely")
    print(f"      messengers have COMPLEMENTARY sensitivity (near-horizon bump → shadow/ISCO ≫ ringdown):")
    print(f"      a joint EHT+X-ray+LIGO measurement both sharpens 'is it Kerr?' AND localizes the deviation   "
          f"{'✅' if okC else '❌'}")

    passed = all(ok)
    print(f"\nTHREE MESSENGERS: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(eikonal ringdown ≈Leaver; shadow+ISCO+ringdown from one metric; complementary discrimination)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
