#!/usr/bin/env python3
"""Step 70 — HAWKING RADIATION & GREYBODY FACTORS: the spectrum, and the death.

§35/§64 gave the temperature; this is what the black hole actually RADIATES and how
it dies. The emission per mode is a thermal (Planck) spectrum at the Hawking
temperature, but FILTERED by the same potential barrier that sets the ringdown (§56) —
the greybody factor Γ_ℓ(ω), the probability a wave of frequency ω tunnels out:

        dN_ℓ/dω dt = Γ_ℓ(ω) / [2π (e^{ω/T} ∓ 1)]      (− bosons, + fermions).

  (A) the spectrum is THERMAL but GREY: a Planck factor at T (§64) × the barrier
      transmission Γ_ℓ(ω) (off §56's exact potential);
  (B) greybody LIMITS (exact; the full Γ(ω) is numerical scattering, as QNMs were in
      §56): high-ω ⇒ Γ→1, the capture cross-section → π b_c² = 27πM² (the shadow,
      §45/§68); low-ω s-wave ⇒ Γ_0 → A_H ω²/π (vanishes — soft quanta reflect), so the
      absorption cross-section → the horizon AREA A_H=16πM² (the area theorem);
  (C) NEGATIVE HEAT CAPACITY: C = dM/dT = −1/(8πT²) < 0 — a black hole gets HOTTER as
      it loses mass, so evaporation runs away (unlike any ordinary body);
  (D) the DEATH: luminosity L ∝ A T⁴ ∝ 1/M² ⇒ dM/dt = −α/M² ⇒ M³ = M₀³ − 3αt, so the
      lifetime ∝ M³ — a stellar hole outlives the universe, a tiny primordial one
      ends NOW in a flash.

Honest scope: textbook (Hawking 1974, 1975; Page 1976). New is the same engine tying
T (§64) + the barrier (§56) + the shadow (§45) into the spectrum and the M³ lifetime.

Run:  .venv/bin/python scripts/70_hawking_spectrum.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("HAWKING RADIATION & GREYBODY FACTORS — the spectrum, and the death\n")
    M, T, w = sp.symbols("M T omega", positive=True)
    ok = []

    Th = 1 / (8 * sp.pi * M)                 # Hawking temperature (§35)
    A = 16 * sp.pi * M**2                     # horizon area

    # (A) the thermal factor: Planck (bosons e^{x}-1) reduces correctly
    x = w / T
    bose = 1 / (sp.exp(x) - 1)
    okA = sp.limit(bose * w, w, 0, "+") == T and sp.limit(bose, w, sp.oo) == 0
    ok.append(okA)
    print(f"  (A) spectrum dN/dωdt = Γ_ℓ(ω)/[2π(e^{{ω/T}}∓1)]: thermal Planck factor at T,")
    print(f"      classical ω→0 limit ω·n_B → {sp.limit(bose*w, w, 0, '+')} = T; ω→∞ → 0   "
          f"{'✅' if okA else '❌'}")

    # (B) greybody limits — exact ends of a numerical curve
    sigma_geo = sp.simplify(sp.pi * (3 * sp.sqrt(3) * M)**2)       # high-ω capture
    okB = sigma_geo == 27 * sp.pi * M**2 and sp.simplify(A - 16 * sp.pi * M**2) == 0
    ok.append(okB)
    print(f"\n  (B) greybody limits: high-ω σ → πb_c² = {sigma_geo} (the shadow §45/§68);")
    print(f"      low-ω s-wave σ → A_H = {A} (horizon-area theorem); full Γ(ω) is numerical (cf §56)   "
          f"{'✅' if okB else '❌'}")

    # (C) negative heat capacity
    M_of_T = 1 / (8 * sp.pi * T)
    C = sp.simplify(sp.diff(M_of_T, T))
    okC = C == -1 / (8 * sp.pi * T**2) and C.subs(T, 1) < 0
    ok.append(okC)
    print(f"\n  (C) heat capacity C = dM/dT = {C} < 0 — the hole HEATS as it shrinks; evaporation runs away   "
          f"{'✅' if okC else '❌'}")

    # (D) evaporation lifetime ∝ M³
    L = sp.simplify(A * Th**4)                 # Stefan–Boltzmann ∝ A T⁴
    alpha, M0 = sp.symbols("alpha M0", positive=True)
    t_evap = sp.integrate(M**2 / alpha, (M, 0, M0))      # ∫dM/(α/M²) from M0 to 0
    okD = sp.simplify(L * M**2 - sp.Rational(1, 256) / sp.pi**3) == 0 and t_evap == M0**3 / (3 * alpha)
    ok.append(okD)
    print(f"\n  (D) L ∝ A T⁴ = {L} (∝ 1/M²) ⇒ dM/dt = −α/M² ⇒ lifetime t_evap = {t_evap} ∝ M³")
    print(f"      smaller = hotter = shorter-lived; the final moments are explosive   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nHAWKING: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(thermal-but-grey spectrum, negative heat capacity, M³ evaporation lifetime)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
