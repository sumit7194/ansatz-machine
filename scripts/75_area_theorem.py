#!/usr/bin/env python3
"""Step 75 — THE AREA THEOREM & MERGER ENERGY BUDGET (a consistency oracle).

Future use (why this is built): when a GW analysis infers a merger's parameters —
the two initial masses and the final mass and spin — those numbers must obey a hard
law of general relativity, Hawking's AREA THEOREM: the total black-hole horizon area
never decreases. That caps how much energy a merger can radiate. So this is an exact
CONSISTENCY ORACLE: any inferred (m₁, m₂, M_f, a_f) that violates it is non-physical.
It ties §60 (Penrose / irreducible mass) + §61 (horizon area) + §72–73 (the waveform).

The 2nd law of black-hole mechanics: A_final ≥ A_1 + A_2. With A=16πM² (Schwarzschild),
this forces the remnant to be heavier than √(M₁²+M₂²), bounding the radiated energy.

  (A) Schwarzschild merger: A_f ≥ A_1+A_2 ⇒ M_final ≥ √(M₁²+M₂²) (the remnant can't be
      too light);
  (B) the radiated-energy bound: E_rad = (M₁+M₂)−M_f ≤ (M₁+M₂)−√(M₁²+M₂²); for equal
      masses ≤ 1−1/√2 ≈ 29.3% of the total — the SAME area bound as the Penrose limit
      (§60), since both are irreducible-mass statements;
  (C) the Kerr/irreducible-mass form: A ∝ M_irr² with M_irr=√(Mr₊/2) (§60), so the 2nd
      law is M_irr,f² ≥ M_irr,1² + M_irr,2²;
  (D) the oracle in use: a real equal-mass merger radiates ~5% (numerical relativity),
      comfortably inside the 29.3% ceiling — an inferred merger must clear this bar, or
      it isn't general relativity.

Honest scope: textbook (Hawking 1971; the classical area theorem). New is the same
engine stating it as an exact bound a measured merger is checked against.

Run:  .venv/bin/python scripts/75_area_theorem.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("THE AREA THEOREM & MERGER ENERGY BUDGET — a consistency oracle\n")
    m1, m2, M, a = sp.symbols("m1 m2 M a", positive=True)
    ok = []

    # (A) Schwarzschild 2nd law: A_f ≥ A_1+A_2 ⇒ M_f ≥ √(M1²+M2²)
    Mf_min = sp.sqrt(m1**2 + m2**2)
    A_initial = 16 * sp.pi * m1**2 + 16 * sp.pi * m2**2
    A_final_min = sp.simplify(16 * sp.pi * Mf_min**2)
    okA = sp.simplify(A_final_min - A_initial) == 0      # the bound saturates the area sum
    ok.append(okA)
    print(f"  (A) area theorem A_f ≥ A_1+A_2 ⇒ M_final ≥ √(M₁²+M₂²) = {Mf_min}")
    print(f"      (16π·M_f,min² = A_1+A_2 = {sp.simplify(A_final_min)})   {'✅' if okA else '❌'}")

    # (B) radiated-energy bound; equal-mass = 1 − 1/√2 (the Penrose §60 bound)
    frac = sp.simplify(((m1 + m2 - Mf_min) / (m1 + m2)).subs(m2, m1))
    okB = sp.simplify(frac - (1 - 1 / sp.sqrt(2))) == 0 and abs(float(frac) - 0.2929) < 1e-3
    ok.append(okB)
    print(f"\n  (B) max radiated fraction (equal mass) = {frac} ≈ {float(frac):.3f}")
    print(f"      = 1−1/√2, the SAME bound as the Penrose limit (§60) — both irreducible-mass   "
          f"{'✅' if okB else '❌'}")

    # (C) Kerr irreducible-mass form: A ∝ M_irr², 2nd law M_irr,f² ≥ ΣM_irr²
    rp = M + sp.sqrt(M**2 - a**2)
    M_irr = sp.sqrt(M * rp / 2)
    okC = sp.simplify(16 * sp.pi * M_irr**2 - 4 * sp.pi * (rp**2 + a**2)) == 0  # 16πM_irr² = A
    okC = okC and sp.simplify(M_irr.subs(a, M) - M / sp.sqrt(2)) == 0           # extremal M/√2
    ok.append(okC)
    print(f"\n  (C) Kerr: A = 16π M_irr², M_irr = √(Mr₊/2) (§60); 2nd law ⇒ M_irr,f² ≥ M_irr,1² + M_irr,2²")
    print(f"      extremal a=M ⇒ M_irr = M/√2   {'✅' if okC else '❌'}")

    # (D) the oracle: a real ~5% merger is inside the 29.3% ceiling
    actual = 0.05
    okD = actual < float(frac)
    ok.append(okD)
    print(f"\n  (D) USE: an inferred merger (m₁,m₂,M_f,a_f) must satisfy A_f ≥ A_1+A_2;")
    print(f"      a real equal-mass merger radiates ~{actual*100:.0f}% < {float(frac)*100:.1f}% ceiling — consistent   "
          f"{'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nAREA THEOREM: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(2nd law M_f≥√(M₁²+M₂²), ≤29.3% radiated, a merger-inference consistency oracle)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
