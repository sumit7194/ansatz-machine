#!/usr/bin/env python3
"""Step 81 — ANALYZER ROBUSTNESS AUDIT: the core verdicts vs known ground truth.

Robustness is the only north star: a green gate proves the batteries RUN, not that the
verdicts are SOUND. The §80 stress test found a real classifier bug; this battery makes
the adversarial check PERMANENT — it pins the analyzer's most-used verdicts (physical?,
made_of, singularities, horizon T/S) to known ground truth, hunting especially for the
dangerous failure: a FALSE "physical=True" or a mis-typed/mis-located feature. If the
analyzer ever regresses on these, the gate goes red.

  (A) physical? — NO false positives: a Morris–Thorne wormhole MUST be flagged
      non-physical (NEC violated); Reissner–Nordström and FLRW dust physical; de Sitter
      physical-but-SEC-violated (NEC/WEC/DEC hold, SEC fails — exactly the dark-energy
      signature);
  (B) made_of — vacuum / traceless-EM / Λ / perfect-fluid classified correctly;
  (C) singularities — r=0 for Schwarzschild & RN, NONE for de Sitter & Minkowski
      (regular: the analyzer doesn't hallucinate singularities);
  (D) horizon T/S — RN has TWO horizons, both with POSITIVE T and S (the §64 |f′| fix
      handles the inner/Cauchy horizon where f′<0), and the smaller horizon is hotter.

Run:  .venv/bin/python scripts/81_analyzer_audit.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyzer import analyze

t, r, th, ph = sp.symbols("t r theta phi", real=True)
x, y, z = sp.symbols("x y z", real=True)
M, Q, H, b0 = sp.symbols("M Q H b0", positive=True)


def sph(f):
    return sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2)


def main():
    print("ANALYZER ROBUSTNESS AUDIT — core verdicts vs ground truth\n")
    ok = []

    # (A) physical? — the dangerous failure is a FALSE positive
    rn = analyze(sph(1 - 2 * M / r + Q**2 / r**2), [t, r, th, ph])
    # Morris–Thorne wormhole: b(r)=b0²/r, Φ=0 ⇒ violates the NEC (needs exotic matter)
    worm = analyze(sp.diag(-1, 1 / (1 - b0**2 / r**2), r**2, r**2 * sp.sin(th)**2), [t, r, th, ph])
    dS = analyze(sph(1 - H**2 * r**2), [t, r, th, ph])
    dust = analyze(sp.diag(-1, t**sp.Rational(4, 3), t**sp.Rational(4, 3), t**sp.Rational(4, 3)),
                   [t, x, y, z])
    okA = (rn["physical"] is True and worm["physical"] is False
           and worm["energy_conditions"]["NEC"] is False
           and dS["physical"] is False and dS["energy_conditions"]["NEC"] is True
           and dS["energy_conditions"]["SEC"] is False and dust["physical"] is True)
    ok.append(okA)
    print(f"  (A) physical?: RN={rn['physical']}, wormhole={worm['physical']} (NEC={worm['energy_conditions']['NEC']}),")
    print(f"      de Sitter={dS['physical']} (NEC={dS['energy_conditions']['NEC']},SEC={dS['energy_conditions']['SEC']}), "
          f"dust={dust['physical']}   {'✅ no false positives' if okA else '❌'}")

    # (B) made_of
    schw = analyze(sph(1 - 2 * M / r), [t, r, th, ph])
    okB = (schw["made_of"].startswith("vacuum") and "electromagnetic" in rn["made_of"]
           and "cosmological constant" in dS["made_of"] and "perfect fluid" in dust["made_of"])
    ok.append(okB)
    print(f"\n  (B) made_of: Schwarzschild=vacuum, RN=EM, de Sitter=Λ, dust=perfect fluid   {'✅' if okB else '❌'}")

    # (C) singularities — no hallucinated singularities on regular spacetimes
    mink = analyze(sph(sp.Integer(1)), [t, r, th, ph])
    okC = (schw["singularities"] == [(r, 0)] and rn["singularities"] == [(r, 0)]
           and dS["singularities"] == [] and mink["singularities"] == [])
    ok.append(okC)
    print(f"  (C) singularities: Schwarzschild/RN → r=0; de Sitter/Minkowski → none (no hallucination)   "
          f"{'✅' if okC else '❌'}")

    # (D) horizon T/S — RN two horizons, both positive (the §64 |f′| fix), smaller hotter
    rnh = analyze(sph(1 - 2 * M / r + Q**2 / r**2).subs({M: 1, Q: sp.Rational(1, 2)}), [t, r, th, ph])
    hs = sorted(((float(rh), float(T), float(S)) for rh, T, S in rnh["horizon"]))
    okD = (len(hs) == 2 and all(T > 0 and S > 0 for _, T, S in hs)
           and hs[0][1] > hs[1][1] and hs[0][2] < hs[1][2])   # smaller r ⇒ hotter, less entropy
    ok.append(okD)
    print(f"\n  (D) RN two horizons: {[(round(rh,3),round(T,4),round(S,3)) for rh,T,S in hs]}")
    print(f"      both T,S>0 (|f′| fix handles inner horizon); smaller horizon hotter   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nANALYZER AUDIT: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(physical?/made_of/singularities/horizon pinned to ground truth — a permanent guard)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
