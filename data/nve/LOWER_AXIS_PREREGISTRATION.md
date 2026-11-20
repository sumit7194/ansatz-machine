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

## Outcome (2026-11-21, rerun under addendum 1; `data/nve/lower_run.out`, `lower_results.json`)
**VERDICT: OBSTRUCTED.** All 13 runs pass every gate. ρ_c = 0.600 at every k, so the c0 Laurent series is
single-valued and analytic in |z| > 0.6.

| run | k | E | zeros of P (annulus) | poles of P (annulus) | S(0.35) | S(0.2) | class |
|---|---|---|---|---|---|---|---|
| C-K | 0 | 0.7 | 1.905944, −1.827513 | 2 ± 0.6i | 2.4e−23 | 1.6e−35 | VA |
| C-K | 0 | 0.8 | 1.934426, −3.489982 | 2 ± 0.6i | 9.3e−25 | 1.2e−36 | VA |
| C-K | 0 | 0.9 | 1.965688, −8.492004 | 2 ± 0.6i | 1.3e−24 | 3.6e−37 | VA |
| C-NV | 0 | 0.8 | 4 real (1.707736, 2.338769, 4.721897, −5.464362) | 6 (3 conjugate pairs) | 2.8745e−8 | 2.8745e−8 | NON-VA |
| T | 1/100 | 0.7 | 1.905729, −1.827280 | 1.999694 ± 0.599486i | 8.7781e−6 | 8.7781e−6 | NON-VA |
| T | 1/100 | 0.8 | 1.934159, −3.489894 | same | 1.9646e−4 | 1.9646e−4 | NON-VA |
| T | 1/100 | 0.9 | 1.965365, −8.491985 | same | 8.3311e−5 | 8.3311e−5 | NON-VA |
| T | 1/30 | 0.7 | 1.905226, −1.826738 | 1.998977 ± 0.598283i | 1.4499e−6 | 1.4499e−6 | NON-VA |
| T | 1/30 | 0.8 | 1.933535, −3.489689 | same | 4.3943e−5 | 4.3943e−5 | NON-VA |
| T | 1/30 | 0.9 | 1.964612, −8.491941 | same | 4.0042e−5 | 4.0042e−5 | NON-VA |
| T | 1/10 | 0.7 | 1.903785, −1.825183 | 1.996919 ± 0.594820i | 2.1175e−6 | 2.1175e−6 | NON-VA |
| T | 1/10 | 0.8 | 1.931748, −3.489104 | same | 5.4216e−6 | 5.4216e−6 | NON-VA |
| T | 1/10 | 0.9 | 1.962452, −8.491815 | same | 6.5099e−6 | 6.5099e−6 | NON-VA |

- Gates at STEP 0.2: det ≤ 6e−33, eig ≤ 9e−33, big loop ≤ 5e−39 (C-NV included; its 6 inner-ring points are now in
  the step control). C-NV's ordered product is 1.0, information only, as the addendum expected for crossing tails.
- Every target is irreducible (red False), not finite, and S agrees between the two steps to all printed digits.
  Kerr's S drops by 12 orders, which is what pure numerical noise does.
- **Predictions:** ρ_c ≤ 1.2 yes; controls behave yes, but only after addendum 1 (first run VOID); OBSTRUCTED yes.
- **Grade:** post-failure amendment. The target classes were identical in the VOID run and the rerun, and the
  amendment did not touch the statistic or the classification rule.
- **Not yet understood (post-hoc, not part of the verdict):** at fixed E, S *decreases* as k grows (E = 0.8:
  2.0e−4, 4.4e−5, 5.4e−6), yet S ≈ 0 at k = 0. If S is continuous in k, it must rise and then fall. A k-scan toward
  0 is the check (§159).

## Post-hoc k → 0 scan (2026-11-21, registered before running; NOT part of the verdict)
E = 0.8, k ∈ {1/10000, 1/1000, 1/300}, same code (`scripts/_nve_lower_kscan.py`).
**Prediction:** S → 0 as k → 0 (continuity). S rises from ~0 to a maximum somewhere below k = 1/100, then falls as
§159 saw. If S stays ~1e−4 down to k = 1e−4, then either S is discontinuous at k = 0 (some feature of c0 is not
analytic in k) or the statistic's normalisation is doing it. That would need a diagnosis before §159's numbers are
read as a measure of "how obstructed".

## POST-UNBLINDING addition (2026-11-21, after the Bridge's V26 addendum C was read)
- The Bridge agrees on the verdict (obstructed at every k ≠ 0; Kerr at the floor) and on the singular-point
  locations.
- The statistics disagree in trend:
  - The Bridge's S_B = max ‖KK′ − K′K‖_F/(‖K‖_F‖K′‖_F) over generator commutators K. At E = 0.8 it **rises**
    linearly in k (log–log slope 1.0001).
  - Ours **falls** with k.
- At the Bridge's request, `scripts/_nve_lower_stat.py` computes both S and S_B from the same 50-digit monodromy
  matrices, at E = 0.8 and k ∈ {1/10, 1/30, 1/100, 3/1000, 1/1000, 1/10000, 0}, at both steps. S_B is reported for
  all generators, and for the point loops only. This **supersedes** the k-scan above (stopped after 40 s, no
  output); its grid includes the Bridge's scan points.
- **Expectation:** the monodromy agrees and the difference is the statistic. Ours takes the max over G′ commutators
  *including conjugates*, normalised by 1 + ‖A‖²‖B‖², so a few large-norm elements can dominate. If S_B here
  reproduces the Bridge's linear trend, the discrepancy is in the statistic.
- **Result (`data/nve/lower_stat.out`, `.jsonl`; 50-digit generators stored):**

| k | S ours | S_B (point loops) | S_B (all, incl. inner) | ‖g_in − I‖_F | tr(g_in) − 2 |
|---|---|---|---|---|---|
| 1/10 | 5.42e−6 | 1.7198e−5 | 1.71e−3 | 8.09 | −4.8500e−5 |
| 1/30 | 4.39e−5 | 5.7044e−6 | 1.67e−3 | 2.69 | −5.3401e−6 |
| 1/100 | 1.96e−4 | 1.7084e−6 | 1.29e−3 | 0.805 | −4.7909e−7 |
| 3/1000 | 8.40e−5 | 5.1225e−7 | 1.17e−3 | 0.241 | −4.3078e−8 |
| 1/1000 | 1.31e−4 | 1.7072e−7 | 8.35e−4 | 0.0805 | −4.7851e−9 |
| 1/10000 | 1.90e−4 | 1.7071e−8 | 9.25e−5 | 0.00805 | −4.7845e−11 |
| 0 | 1e−36 | 2e−37 | 2e−34 | 2e−33 | ~1e−35 |

  - **The monodromy agrees with the Bridge in trend.** S_B on the point loops is linear in k, with log–log slope
    1.0002 over 1e−4 to 1e−2 (Bridge: 1.0001). Both steps agree to 5 figures.
  - **The magnitude differs** (ours 1.7e−6 at k = 1/100, Bridge's 3.2e−4). That is expected: Frobenius norms are not
    conjugation-invariant, and our basis (identity at base point z = 40) gives generators of norm 1.2e3 to 4.2e3.
  - **Why our S is not monotone (diagnosed):**
    - The inner-loop generator deviates from I linearly, ‖g_in − I‖ ≈ 80.5k.
    - Commutators with large-norm generators amplify that by about ‖M‖‖M⁻¹‖ ~ 1e7, so any statistic that involves
      g_in is already **saturated** (non-linear in k) at k = 1e−4. S_B over all generators shows the crossover: linear
      below ~1e−3, then flat.
    - Ours takes commutators of commutators, conjugates included, so it is saturated throughout the scanned range.
  - **Conclusion:** S is a valid zero-versus-nonzero detector, since the refinement test separates noise from a
    real value. It is **not** a measure of "how obstructed", and §159's S values should not be read as one.
  - **A basis-free, path-free number for comparison:** the inner loop is a circle |z| = r (1.3 < r < 1.9 at
    E = 0.8), so its free homotopy class is unique and its trace is implementation-independent.
    **tr(g_in) − 2 = −4.7845e−3·k² + O(k³)**: real and negative, so the monodromy is elliptic with rotation angle
    ≈ 0.0692k.
- **Follow-up note (Bridge request, 2026-11-21):** tr(g_in) − 2 on |z| = 1.35 (and r = 1.6 as a control; it must
  agree) at E = 0.7, 0.8, 0.9 × k ∈ {1e−3, 1e−2, 1/30, 1/10, 0}, at two steps (`scripts/_nve_lower_trace.py`).
  The k² coefficient c(E) comes from a fit of (tr − 2)/k² = c + c′k. Expectation: c < 0 at every E.
