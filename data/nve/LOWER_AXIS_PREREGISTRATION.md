# Lower-axis first-order NVE for the "invisible" twist family: is the monodromy non-virtually-abelian? Blind second implementation. Pre-registration, 2026-11-20, BEFORE any code

**Ask:** the Bridge (V26), with Sumit's go to help. A blind, independent, high-precision second implementation.
**Blind to (not opened):** TheBridge `falsification/V26_single_centre_lower_axis/results/` (v26_B8.\*),
`fable_work/only_kerr_single_centre/` (incl. checks/t5\*), and the B8 parts of V26 FINDINGS. Only the problem
statement in the Bridge's message is used.

## Problem, as given
- M = 1, a = 3/5. f0 = 1 − 1/(z − ia) − 1/(z + ia).
- c_K = −2a/(z² + a²).
- (c0″)² = (c_K″)² + k Q/D³, with D = z² + a², v = (z + ia)/(z − ia), Q = v³ + v⁻³ − (3/5)(v + 1/v) − 4/5.
- c0 and c0′ → 0 as z → +∞ on the real axis; the branch of c0″ is continuous with c_K″ there.
- Lower-axis mass function f0⁻ = f0/(f0² + c0²). NVE: v″ = −(3/16)(P′/P)² v, with P = E² − f0⁻ (μ = 1).
- Question: on loops in |z| > 1.3, for k ≠ 0, is the monodromy group non-virtually-abelian?

## Method (my own; written before code)
1. **c0 by a Laurent series at ∞.** Write w = 1/z, so φ = arctan(aw) and v = e^(2iφ).
   - Q = 2cos 6φ − (6/5)cos 2φ − 4/5 = −(168/5)φ² + O(φ⁴), so k Q/D³ = O(w⁸). With (c_K″)² = 144a²w⁸ + …, the
     radicand is R = (144 − 33.6k)a²w⁸ + O(w⁹).
   - So c0″ = Σ_{n≥4} s_n wⁿ (sign: matches c_K″'s leading −12a), and c0 = Σ_{n≥4} s_n/((n − 1)(n − 2)) w^(n−2).
     Both conditions at +∞ hold, and there are no log terms.
   - The series converges for |z| > ρ_c = the largest |·| of the poles (±ia) and zeros of R. **Gate:** ρ_c ≤ 1.2.
     That certifies c0 is single-valued and analytic in |z| > 1.3, which answers the Bridge's "check that".
   - **Control:** k = 0 must give c0 = c_K to 1e−30 on a test circle.
2. **Singular points in the annulus.** These are the zeros of F1 = E²(f0² + c0²) − f0 (zeros of P) and of
   F2 = f0² + c0² (poles of P), in 1.3 < |z| < 60.
   - Count them with the argument principle on |z| = 1.3 and |z| = 60. (At ∞, F1 → E² − 1 ≠ 0 and F2 → 1, so the
     outer winding must be 0.)
   - Locate them by Newton from a grid. **Gate:** the located count equals the argument-principle count, for both F1
     and F2.
3. **Monodromy.** The engine is that of §158: 2×2 fundamental matrix, power-series continuation, mpmath 50 digits.
   Here the Taylor coefficients of r at each centre come from f0 (exact rational) and c0, re-expanded from its Laurent
   series by binomial sums. The step is ≤ STEP × min(distance to the nearest annulus singular point, |z0| − ρ_c).
   - Paths stay in |z| > 1.3. Base point b = 40 (real). From b, go along the circle |b| to arg c, radially in to the
     circle around c, round it counter-clockwise, and back.
   - Generators: one loop per annulus singular point, plus the loop |z| = 1.35 around the inner disk.
   - **Gates:** det = 1 to 1e−20; local eigenvalues = exp(2πiρ±) to 1e−15 (ρ from the order m of P there); and the
     product of all loops, ordered, equals I to 1e−15 (∞ is ordinary).
4. **Virtually-abelian test:** an irreducible subgroup of SL₂ is virtually abelian iff it is imprimitive or finite.
   - Statistic S: if a common eigenvector exists (reducible), S = the largest normalised ‖[g_i, g_j] − I‖ over the
     generators. Otherwise S = the largest normalised commutator of pairs drawn from G′ (pairwise commutators of the
     generators and their conjugates), as in §158. A finiteness flag holds if all traces of 200 random words are real
     and in [−2, 2].
   - **Built-in refinement (the §158 lesson):** every run at STEP = 0.35 and STEP = 0.2.
     - **NON-VA:** S stable, |S₁ − S₂|/S₂ < 1e−3, and S₂ > 1e−12.
     - **VA:** S₂ < 1e−30, or S₂ < 1e−6·S₁, or finite.
     - **UNDETERMINED:** otherwise.

## Runs
- **Controls:**
  - **C-K:** k = 0, at E = 0.7, 0.8, 0.9 (Kerr seen from below). Must be **VA**.
  - **C-NV:** a pipeline control. Replace f0 by §158's degree-3 A3, f0 = 1 − 1/(z − 1) − 1/(z + 2) − 1/(z − 3), keep
    c0 = c_K (k = 0), at E = 0.8. f0⁻ is then rational of degree ≥ 3, so it must be **NON-VA**. Singular points inside
    |z| < 1.3 are allowed; the inner loop absorbs them.
- **Target:** k ∈ {1/100, 1/30, 1/10} × E ∈ {0.7, 0.8, 0.9}. That is 9 runs.

## Verdict words
- **VOID:** any gate or control fails.
- **OBSTRUCTED:** all 9 target runs are NON-VA. The family is obstructed at first order on the lower axis, at every
  sampled (k, E).
- **NOT OBSTRUCTED:** all 9 are VA.
- **MIXED:** otherwise, reported per (k, E).
- Numbers go to the Bridge for the unblinding comparison: per run, the singular-point count and locations, S at both
  steps, and the class.

## Predictions (sealed)
| item | prediction | confidence |
|---|---|---|
| ρ_c ≤ 1.2 at all k | yes | ~80% |
| controls behave | yes | ~80% |
| target verdict OBSTRUCTED | yes | ~70% (f0⁻ is non-rational for k ≠ 0; generic expectation) |

## Resources
1 core, nice 10, < 1 GB, minutes per run, with a guard (fleet rule).

## Addendum 1 (2026-11-20, AFTER the first full run; NOT blind to its target results)
**First run: VOID.** The pipeline control C-NV failed its gates (det 1.5e−17; ordered product ≠ I). All other runs
passed every gate. Recorded before the fix:
- **C-K:** VA ×3 (S falls 1e−23 → 1e−36 under refinement).
- **C-NV:** S stable at 2.875e−8.
- **All 9 targets: NON-VA**, with S stable to ≥ 4 digits at 1e−6 to 2e−4, and every gate passing.

**Diagnosis, two implementation defects that only C-NV exposed:**
1. **Step control** ignored the singular points of r inside |z| < 1.3. C-NV (degree 3) has zeros of G1 and G2 between
   0.9 and 1.3, so steps near the inner circle overran the series' radius (the det error). The Kerr-family runs have no
   such points, and their gates are at 1e−35.
2. **The "ordered product = I" gate** assumes non-crossing lasso tails. C-NV has three singular points on the
   positive real axis, so its tails needed angular detours that cross. The generators are still a valid generating set
   (lassos with any tails generate π₁ of the punctured annulus), but the simple ordered relation no longer holds.

**Fix (applies to all runs; everything is rerun):**
- The step size also uses the zeros of G1 and G2 in 0.9 < |z| < 1.3 (same zero-finder; the c0 series is extended to
  converge there).
- The product gate is replaced by **a direct loop around |z| = 40, which must equal I to 1e−15** (∞ ordinary, plus
  accuracy). The ordered product is reported for information only.
- **Grade:** "post-failure amendment, NOT blind to the target results." The amendment changes only the controls'
  numerics, not the statistic or the classification.
