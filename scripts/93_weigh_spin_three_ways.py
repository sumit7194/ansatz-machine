#!/usr/bin/env python3
"""Step 93 — WEIGHING THE SPIN THREE WAYS: the consistency null-test of the Kerr hypothesis.

The observational campaign's capstone (ties §86–§92). A black hole's spin can be read
three independent ways — from the EHT shadow, the X-ray ISCO, and the LIGO ringdown. For a
TRUE Kerr hole they must all give the SAME spin. So: ASSUME Kerr, infer the spin from each
observable, and check whether they agree. Disagreement is a model-independent signature
that the hole is NOT Kerr — a null test of general relativity's no-hair prediction.

  (A) CONSISTENCY — a true Kerr hole (a=0.70): all three inferred spins agree to <0.005.
      The test passes (as it must);
  (B) the BLIND SPOT (an honest limit) — Kerr–Newman (a=0.6, Q=0.5): charge mimics spin
      CONSISTENTLY, so all three infer ~the same (wrong) spin a≈0.72. The test does NOT
      flag it — a charged hole is observationally degenerate with a slightly faster Kerr.
      Passing the test does not prove Kerr;
  (C) the SIGNAL — a near-horizon deformation (§85 bump): it shifts the ISCO (near-horizon)
      more than the photon-ring observables (shadow, ringdown) — §88's complementary
      sensitivity — so the three inferred spins DISAGREE, and the spread GROWS with the
      deformation. The inconsistency IS the detection: failing the test proves non-Kerr.

Run:  .venv/bin/python scripts/93_weigh_spin_three_ways.py
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


def deformed(a, eps):
    return (lambda r: -(1 - 2 / r) * (1 - eps / r**3), lambda r: -2 * a / r,
            lambda r: r * r + a * a + 2 * a * a / r, lambda r: r * r / (r * r - 2 * r + a * a))


def kerr_obs(a):
    o = equatorial_observables(*kerr(a))["prograde"]
    return o["isco"], o["shadow_b"], o["ringdown"]["omega_R"]


def infer_spin(target, idx):
    """The Kerr spin whose observable idx (0=ISCO,1=shadow,2=ringdown) equals target."""
    lo, hi = 0.0, 0.9989
    flo = kerr_obs(lo)[idx] - target
    for _ in range(60):
        m = (lo + hi) / 2
        fm = kerr_obs(m)[idx] - target
        if flo * fm < 0:
            hi = m
        else:
            lo, flo = m, fm
    return (lo + hi) / 2


def three_spins(obs):
    return (infer_spin(obs["isco"], 0), infer_spin(obs["shadow_b"], 1),
            infer_spin(obs["ringdown"]["omega_R"], 2))


def main():
    print("WEIGHING THE SPIN THREE WAYS — the consistency null-test of the Kerr hypothesis\n")
    ok = []

    # (A) true Kerr → all three agree
    aI, aS, aQ = three_spins(equatorial_observables(*kerr(0.70))["prograde"])
    spreadK = max(aI, aS, aQ) - min(aI, aS, aQ)
    okA = spreadK < 0.005 and abs(aI - 0.70) < 0.01
    ok.append(okA)
    print(f"  (A) TRUE Kerr (a=0.70): inferred spin from ISCO={aI:.3f}, shadow={aS:.3f}, ringdown={aQ:.3f}")
    print(f"      spread={spreadK:.4f} ⇒ consistent — the test passes, as it must   {'✅' if okA else '❌'}")

    # (B) Kerr–Newman: charge mimics spin consistently (the blind spot)
    bI, bS, bQ = three_spins(equatorial_observables(*kerr_newman(0.6, 0.5))["prograde"])
    spreadKN = max(bI, bS, bQ) - min(bI, bS, bQ)
    okB = spreadKN < 0.01 and bI > 0.65          # consistent, but the inferred spin ≠ true 0.6
    ok.append(okB)
    print(f"\n  (B) Kerr–Newman (a=0.6, Q=0.5): inferred from ISCO={bI:.3f}, shadow={bS:.3f}, ringdown={bQ:.3f}")
    print(f"      spread={spreadKN:.4f} ⇒ all agree on a≈{bI:.2f} (≠ true 0.6): charge mimics spin CONSISTENTLY,")
    print(f"      so the test does NOT flag it — passing the test does not prove Kerr   {'✅' if okB else '❌'}")

    # (C) near-horizon deformation: the three DISAGREE; spread grows with deformation
    spreads = []
    print(f"\n  (C) near-horizon deformed Kerr (a=0.6) assumed Kerr — three inferred spins:")
    for eps in (0.0, 0.5, 1.0):
        s = three_spins(equatorial_observables(*deformed(0.6, eps))["prograde"])
        sp = max(s) - min(s)
        spreads.append(sp)
        print(f"      ε={eps}: ISCO={s[0]:.3f}, shadow={s[1]:.3f}, ringdown={s[2]:.3f} → spread={sp:.3f}")
    grows = spreads[0] < 0.005 and spreads[1] < spreads[2] and spreads[2] > 0.02
    okC = grows
    ok.append(okC)
    print(f"      spread grows with deformation (ISCO disagrees most — near-horizon, §88) ⇒ the inconsistency")
    print(f"      IS the detection: failing the test proves non-Kerr   {'✅' if okC else '❌'}")

    passed = all(ok)
    print(f"\nWEIGH SPIN THREE WAYS: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Kerr consistent; charge degenerate/blind; near-horizon deformation caught — a null test of no-hair)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
