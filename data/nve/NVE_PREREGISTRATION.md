# Independent check of the axis-NVE classification ("solvable iff deg f0 ≤ 2"). Pre-registration, 2026-11-20, BEFORE any code

**Ask:** the Bridge (after Sumit asked me to offer help). Test Fable's hand-derived claim. For
v'' + (3/16)(P'/P)² v = 0 with P = E² − μ² f0, where f0 is real rational of degree d with f0(∞) = 1: G⁰ is solvable
for all E in an interval iff d ≤ 2, and for d ≥ 3, G = SL(2, C) at generic E. Not embargoed. Nothing of Fable's notes
is used beyond the claim as stated.

## (a) Derivation, done here first (independent of the notes)
Write y'' = r y with r = −(3/16) L², where L = P'/P = Σ m_c/(z − c). The sum runs over zeros (m > 0) and poles
(m < 0) of P.
- **Singular points:** exactly the zeros and poles of P. The double-pole coefficient is b_c = −(3/16) m_c².
- **Exponents:** ρ = ½ ± ½ √(1 − ¾ m²).
  - |m| = 1, "simple": ρ ∈ {¼, ¾}, difference ½.
  - |m| ≥ 2, "heavy": ρ = ½ ± (i/4)√(3m² − 4), a complex difference. (This matches the claim's formula.)
  - 1 − ¾m² is never the square of a rational for integer m ≥ 1 (it is ¼ at m = 1, and negative for m ≥ 2). So no
    exponent difference is an integer: **no logarithmic and no apparent singularities.**
- **Infinity:** P(∞) = E² − μ² ≠ 0, so L = O(z⁻²) and r = O(z⁻⁴). Infinity is an ordinary point, and in Kovacic's
  terms has "order > 2".
- **Kovacic's necessary conditions** (Kovacic 1986), with s simple and h heavy points:
  - **Case 1:** d₁ = α∞ − Σ α_c ∈ Z≥0, with α∞ ∈ {0, 1}. Re α_c ≥ ¼ (simple) and Re α_c = ½ (heavy), so
    s/4 + h/2 ≤ 1, i.e. **s + 2h ≤ 4.**
  - **Case 2:** E_c = {1, 2, 3} (simple), {2} (heavy), E∞ = {0, 2, 4}, and d₂ = ½(e∞ − Σ e_c) ≥ 0. So
    **s + 2h ≤ 4.**
  - **Case 3** (n = 4, 6, 12): min E_c = 3 (simple), E_c = {6} (heavy), max E∞ = 12, and d₃ = (n/12)(e∞ − Σ e_c) ≥ 0.
    So **3s + 6h ≤ 12, the same bound.**
  - If no case applies, G = SL(2, C). **So s + 2h ≥ 5 implies G = SL(2, C)**, which confirms the claim's bound.
- **Counting:** at generic E, P has d simple zeros (from f0 = E²/μ²), and its poles are those of f0 (orders summing to
  d). The minimum of s + 2h is d + 2 (one pole of order d ≥ 2), or 2 when d = 1. So **d ≥ 3 gives s + 2h ≥ 5,
  hence SL(2, C)**, as claimed.
- **Special E:**
  - Two zeros merging (a critical value with ramification 2) give s − 2 and h + 1, so s + 2h is unchanged and SL(2)
    persists.
  - **Three zeros merging (ramification 3) give s − 3 and h + 1, so s + 2h drops by 1.** Example (constructed here):
    f0 = ½ + ½((z − 1)/(z + 1))³ at E² = ½μ². Then P ∝ ((z − 1)/(z + 1))³, so s = 0 and h = 2, giving s + 2h = 4. In
    fact r = −(27/4)/(z² − 1)², with elementary solutions √(z² − 1)·((z + 1)/(z − 1))^(±iν/2), ν² = 23/4. **G⁰ is a
    torus, which is solvable.**
  - So a degree-3 f0 is solvable at an isolated special E. This is consistent with "generic E" but refutes any
    "every E" reading.
  - E² = μ² (a zero at ∞) and E = 0 are excluded by the claim.
- **What (a) does NOT settle:** the "if" direction. Passing the necessary conditions (s + 2h ≤ 4) is not sufficient.
  For d = 2 with two simple poles (s = 4, h = 0) the equation is, up to a Möbius map, a one-parameter family in the
  cross-ratio, with sign pattern (+, +, −, −). Kerr is solvable because it is integrable, but a GENERIC degree-2 f0
  needs checking. That is added as a test.

## (b) Computation (method chosen here: numerical monodromy plus a derived-subgroup test)
- **Monodromy:** mpmath at 40 digits, by power-series analytic continuation. The Taylor series of r is computed from
  the numerator and denominator polynomials of P, with order 60 and steps ≤ 0.5 × the distance to the nearest singular
  point. Loops around each finite singular point start from a common base point.
- **Sanity gates:**
  - det M = 1 to 1e−20;
  - the eigenvalues of each local monodromy equal exp(2πiρ±) to 1e−15 (this checks (a)'s exponents);
  - the ordered product of all loops equals I to 1e−15 (∞ ordinary).
- **Solvability test:** G (the Zariski closure of monodromy) has solvable G⁰ iff G is reducible, imprimitive or
  finite. Then G' is abelian, or G is finite.
  - Compute the commutators of all generator pairs, and their conjugates by each generator.
  - **Derived-abelian** if every pair of these commute: ‖[C_a, C_b] − I‖ / (1 + ‖C_a‖²‖C_b‖²) ≤ 1e−15.
  - Also report: a common eigenvector (reducible), and whether all traces are real in [−2, 2] (finite).
  - **SOLVABLE** = derived-abelian, or (finite traces and the group closes under 200 random words).
  - **NON-SOLVABLE** = some normalised commutator pair is ≥ 1e−6.
  - **Undetermined** otherwise.
- **Test set** (μ = 1, f0(∞) = 1):

| id | f0 | d | E | prediction |
|---|---|---|---|---|
| K | 1 − 1/(z − 0.6i) − 1/(z + 0.6i) (Kerr, M = 1, a = 3/5) | 2 | 0.80, 0.95 | SOLVABLE (~97%) |
| Z | ((z − 1)/(z + 1))² (double pole) | 2 | 0.5, 0.8 | SOLVABLE (~75%) |
| S1 | 1 − 2/(z + 1) (degree 1) | 1 | 0.7 | SOLVABLE (~95%) |
| G2 | 1 − 1/(z − 1) − 2/(z + 3) (generic degree 2, not Kerr) | 2 | 0.6, 0.9 | SOLVABLE (~60%; the "if" direction) |
| A3 | 1 − 1/(z − 1) − 1/(z + 2) − 1/(z − 3) | 3 | 0.7, 0.9, 1.3 | NON-SOLVABLE (~95%) |
| B3 | ((z − 1)/(z + 1))³ (a triple pole) | 3 | 0.6, 0.9 | NON-SOLVABLE (~95%) |
| C3 | (z³ + 2z + 1)/(z³ + z + 1) | 3 | 0.8, 1.2 | NON-SOLVABLE (~95%) |
| M2 | a degree-3 f0 with a positive critical value c ≠ 1 (chosen in code from its critical values), at E² = c (two zeros merge) | 3 | √c | NON-SOLVABLE (~85%) |
| M3 | ½ + ½((z − 1)/(z + 1))³ at E² = ½ (three zeros merge) | 3 | √½ | SOLVABLE (~85%) |

## (c) Verdict rule
- **"deg f0 ≤ 2 is exactly right (generic E)"** if: K, Z, S1 and G2 are SOLVABLE; A3, B3, C3 and M2 are NON-SOLVABLE;
  and every sanity gate passes. M3 SOLVABLE then confirms that "generic E" is needed.
- **"Necessary direction only":** if G2 (or Z) comes out NON-SOLVABLE. Then not every degree-2 f0 is solvable, and
  the right condition is narrower (a sign pattern or Kerr-type constraint).
- **"Claim fails":** if any d ≥ 3 case is SOLVABLE at a generic E.
- **"Undetermined":** any gate fails or a case is undetermined.

## Resources
One core, nice 10, < 1 GB. Seconds to minutes per case, with a stop guard if a case exceeds 10 min.

## Outcome (2026-11-20)
**Registered verdict: UNDETERMINED.**
- 14 of 16 case×E runs came out as predicted, with every gate passing (det ≤ 1e−23, eigenvalues ≤ 2e−21, product at ∞
  ≤ 3e−16).
- **Two degree-3 runs, A3 and B3 at E² = 81/100, gave normalised commutator measures of 2.0e−7 and 4.3e−8.** These are
  below the registered 1e−6 NON-SOLVABLE line, but far above the floor of the solvable cases (≤ 5e−24). The
  registered line was set too high.

**Post-hoc precision check (labelled; asked for by Sumit):**
- Raising dps from 30 to 60 changes nothing (the floor is series truncation, not rounding).
- Halving the step factor from 0.4 to 0.2 (at dps 50):
  - **Kerr and G2 drop from ~1e−27 to ~1e−46:** noise, so SOLVABLE.
  - **A3 and B3 are unchanged to 4 digits (1.984e−7, 4.251e−8):** genuinely non-zero, so NON-SOLVABLE.
- **With that check, all 16 runs agree with the predictions.**

| case | d | s + 2h | result |
|---|---|---|---|
| K (Kerr), 2 E | 2 | 4 | SOLVABLE |
| Z (double pole), 2 E | 2 | 4 | SOLVABLE |
| S1, 1 E | 1 | 2 | SOLVABLE (reducible, finite-like) |
| **G2 (generic, non-Kerr degree 2), 2 E** | 2 | 4 | **SOLVABLE** |
| A3, 3 E | 3 | 6 | NON-SOLVABLE |
| B3, 2 E | 3 | 5 | NON-SOLVABLE |
| C3, 2 E | 3 | 6 | NON-SOLVABLE |
| M2 (2 zeros merge) | 3 | 6 | NON-SOLVABLE |
| **M3 (3 zeros merge)** | 3 | 4 | **SOLVABLE (reducible): the "generic E" qualifier is necessary** |

**Verdict (c): "deg f0 ≤ 2" is the right condition at generic E.**
- **Necessary direction (d ≥ 3 ⇒ G = SL(2, C) at generic E): confirmed, ~95%.** It is a short Kovacic count
  (s + 2h ≥ 5, re-derived independently above, with no log or apparent singularities and ∞ ordinary), and it agrees
  with 9 numerical runs.
- **Sufficiency (every degree-2 f0 solvable): supported but NOT proven, ~80–85%.** It holds for Kerr, the double-pole
  pattern and a generic non-Kerr two-simple-pole f0, at 2 energies each. A proof would need Kovacic's Case 1/2 solution
  for the (+, +, −, −) cross-ratio family and for the (+, +, −2) pattern. Not done.
- **Caveats for the write-up:**
  1. "Generic E" is essential. At isolated E where three zeros of P merge, a degree-3 f0 can be solvable (M3, explicit).
  2. E² = μ² (∞ singular) and E = 0 are excluded.
  3. Monodromy is numerical, and solvability rests on the derived-subgroup test.
