#!/usr/bin/env python3
"""Step 92 — THE ACCRETION ENGINE: radiative efficiency + disk heat → the X-ray spin scale.

The X-ray messenger (§87/§88) made concrete: HOW spin is actually measured. A thin
accretion disk radiates the binding energy released as matter spirals to the ISCO, then
plunges. So the inner edge (the ISCO we compute) fixes two observables:

  (A) the RADIATIVE EFFICIENCY η = 1 − E_ISCO — the fraction of rest mass converted to
      light. Schwarzschild: E_ISCO = √(8/9) ⇒ η = 5.72%. Prograde spin shrinks the ISCO
      and DEEPENS the binding, so η climbs toward 1 − 1/√3 = 42.3% at extremal Kerr — the
      most efficient steady engine known (nuclear fusion is 0.7%). This powers quasars/AGN;
  (B) the DISK TEMPERATURE: the inner edge sets the peak. Thin-disk scaling T_peak ∝
      r_ISCO^{−3/4} (fixed Ṁ, M), so a smaller ISCO ⇒ a HOTTER inner disk ⇒ a HARDER
      X-ray spectrum. Spin is written in the spectrum;
  (C) the chain: spin → ISCO → {efficiency, disk temperature} → the thermal X-ray
      continuum. Fitting that continuum is exactly how stellar-mass BH spins (Cygnus X-1,
      GRS 1915, …) are measured. The engine computes the whole chain from the metric.

Run:  .venv/bin/python scripts/92_accretion_engine.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from observe_rotating import equatorial_observables, _energy


def kerr(a):
    return (lambda r: -(1 - 2 / r), lambda r: -2 * a / r,
            lambda r: r * r + a * a + 2 * a * a / r, lambda r: r * r / (r * r - 2 * r + a * a))


def efficiency(a):
    gtt, gtp, gpp, grr = kerr(a)
    risco = equatorial_observables(gtt, gtp, gpp)["prograde"]["isco"]
    return risco, 1 - _energy(gtt, gtp, gpp, risco, True)


def main():
    print("THE ACCRETION ENGINE — radiative efficiency + disk heat → the X-ray spin scale\n")
    ok = []

    # (A) radiative efficiency η = 1 − E_ISCO
    spins = (0.0, 0.5, 0.9, 0.998, 0.9999)
    rows = [(a, *efficiency(a)) for a in spins]
    eta0 = rows[0][2]
    etas = [r[2] for r in rows]
    mono = all(etas[i] < etas[i + 1] for i in range(len(etas) - 1))
    okA = abs(eta0 - 0.0572) < 5e-4 and mono and etas[-1] > 0.37          # Schw 5.72%, rises toward 42.3%
    ok.append(okA)
    print("  (A) radiative efficiency η = 1 − E_ISCO:")
    for a, risco, eta in rows:
        print(f"      a={a:7.4f}: ISCO={risco:.3f}M, η={100*eta:5.2f}%")
    print(f"      Schwarzschild 5.72% (=1−√(8/9)) → {100*etas[-1]:.1f}% near-extremal (→42.3% at a=1); "
          f"monotone   {'✅' if okA else '❌'}")
    print(f"      cf nuclear fusion 0.7%: black-hole accretion is ~8–60× more efficient — it lights up quasars")

    # (B) disk temperature: smaller ISCO ⇒ hotter (harder X-ray)
    iscos = [r[1] for r in rows]
    Trel = [(iscos[0] / ri)**0.75 for ri in iscos]                       # T_peak ∝ r_ISCO^-3/4, vs Schwarzschild
    hotter = all(Trel[i] < Trel[i + 1] for i in range(len(Trel) - 1))
    okB = hotter and Trel[-1] > 3
    ok.append(okB)
    print(f"\n  (B) disk peak temperature (∝ r_ISCO^−3/4), relative to Schwarzschild:")
    print("      " + ",  ".join(f"a={a:.3g}→{t:.2f}×" for a, t in zip(spins, Trel)))
    print(f"      smaller ISCO ⇒ hotter inner disk ⇒ harder X-ray spectrum   {'✅' if okB else '❌'}")

    # (C) the chain = the continuum-fitting spin measurement
    okC = okA and okB
    ok.append(okC)
    print(f"\n  (C) spin → ISCO → {{efficiency, disk temperature}} → thermal X-ray continuum. Fitting that")
    print(f"      continuum is how stellar-mass BH spins are measured (Cygnus X-1, GRS 1915). The engine")
    print(f"      runs the whole chain from the metric — the X-ray messenger, made quantitative.   "
          f"{'✅' if okC else '❌'}")

    passed = all(ok)
    print(f"\nACCRETION ENGINE: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(η: 5.7%→42%; smaller ISCO ⇒ hotter/harder; spin→ISCO→spectrum is the continuum-fitting method)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
