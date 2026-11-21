# Spin coverage of the branched-twist family: spins 3/10, 4/5, 9/10 (pre-registration, 2026-11-21)

**Ask.** The Bridge GO after §162 (T38 point 1e: K*(a) had been shown empty only at a = 0.6). It continues the current
line. E = 4/5 throughout.

**Spins and why.**
- 3/10, 4/5 and 9/10 cover low, mid and high spin.
- 19/20 was scanned and **dropped before any F**: in the half-plane region a branch cut crosses the working region,
  and the series ratio is 0.70 (`spin_geo.out`). It is not attempted here.

**Code.** `scripts/_nve_spin_scan.py` (`NVE_SPIN=<a> … run`). It reuses the validated machinery:
- the Laurent c0 and the §159 walker for region A;
- the exact-radicand engine `_nve_lower_hp.py` (§162) for region B.

Spin now enters only through `NVE_SPIN`, whose default 3/5 reproduces every earlier run. The family's constants are
spin-independent: checked symbolically, our radicand equals Neon's (8/(5a⁶(u² + 1)⁶))·B(u², k) at spins 3/5, 3/10
and 19/20.

## Regions (edges fixed from the geometry scan, before any F)
| spin | region A (circle picture) | region B (half-plane picture) |
|---|---|---|
| 3/10 | [−1/2, 4] × [−1/2, 1/2]i, circle R0 = 1.1492 | [3.95, 30/7 − 1e−12] × [−1/4, 1/4]i; centre Z0 = 1.9540, base 1.6540; 220 terms; ratio ≤ 0.6 |
| 4/5 | [−1/2, 4] × [−1/2, 1/2]i, R0 = 1.3382 | same box; Z0 = 1.6181, base 1.3047; 220 terms; ratio ≤ 0.6 |
| 9/10 | [−1/2, 3.85] × [−1/2, 1/2]i, R0 = 1.2639 | [3.8, 30/7 − 1e−12] × [−0.15, 0.15]i; Z0 = 1.4926, base 1.1494; **300 terms; ratio ≤ 0.7** (0.7³⁰⁰ ≈ 1e−46) |

**Rules behind those numbers:**
- R0 is midway between the largest inner radius (ρ_c or an extra) and the smallest outer |z|. The margins are 0.75,
  0.29 and 0.26.
- Z0 is Re(centroid of r+, p± at the endpoint).
- The base is Re(r+ at the endpoint) − 0.3, but at least a + 0.08.

## What is counted, and the verdict
- **Region A** (loops M0 = circle R0, M1 = capsule lasso around [r+, p+], based at R0): count F, tr M0 − 2, tr M0,
  tr M1, and tr M1 − s for each finite-subgroup trace s.
  - Required: F has 2 zeros (Kerr's double zero at 0); tr M0, tr M1 and every tr M1 − s have none.
  - That gives irreducible, not imprimitive and not finite at every k ≠ 0 in A.
- **Region B** (M1 lasso and Γ disc, half-plane, as §162): count F_h, tr M1, tr Γ, tr M1Γ, and tr M1 − s.
  - Required: all zero-free, with tr Γ or tr M1Γ zero-free.
- **The endpoint k = 30/7** is classified directly (non-VA required), with samples at 30/7 − 10^{−13, −14, −15}.
- **Verdict per spin:** NO EXCEPTIONAL k IN (0, 30/7 − 1e−12] AND AT 30/7, if A and B both pass, the endpoint is
  non-VA, and every control and guard holds. Otherwise VOID, UNDETERMINED, or EXCEPTIONAL CANDIDATES, as in the code.

## Controls and guards per spin (any failure → VOID)
- **A-Kerr:** k = 0 gives |F| ≤ 1e−25 and |tr M0 − 2| ≤ 1e−25.
- **A-C1:** on the circle |k| = 0.3, F and tr M0 − 2 each have exactly 2 zeros.
- **A-C2 (counter must-detect):** the count of F·(k − (2 + 0.2i)) is count + 1, and of F/(k − (2 + 0.2i)) is
  count − 1.
- **A-geo** at every sample:
  - outer |z| ≥ R0 + 0.1;
  - extras and ρ_c ≤ R0 − 0.1;
  - lasso clearance ≥ 0.3 × dist(p−, segment) and ≥ 0.05 from the rest.
- **A-step:** every 6th sample at steps 0.35, 0.2 and 0.12 agrees to a relative 1e−15. **A-arg:** |Δarg| ≤ π/4 after
  refinement.
- **B-repro:** engine vs Laurent c0 and c0′ (Laurent at raised order) at k = A's right edge and k = 30/7, at 6 points,
  ≤ 1e−40.
- **B-repro-F:** F_h at k = A's right edge, engine vs Laurent, with the same loops: ≤ 1e−20.
- **B-MF-trunc (must fail):** a 12-term series differs by ≥ 1e−30 in c0 and by ≥ 1e−15 in F_h.
- **P1 Kerr (must be imprimitive):** the half-plane classifier says imprimitive (VA) at k = 0.
- **P2 (planted non-VA member) at k = A's right edge:** the circle pair (region A machinery) and the half-plane
  classifier both say non-VA.
- **B-geo** on an interior 11 × 15 grid and every boundary sample:
  - engine cut guard;
  - series ratio ≤ the spin's limit;
  - lasso and disc clearances as in §162;
  - containment in the working disc (radius = max reach + 0.05).
- **B-count:** G1 and G2 have (1, 2) zeros in the working disc at 5 grid points.
- **B-step:** every 4th sample at three steps agrees to 1e−15. **B-arg:** as in A. **B-C2:** as in A.

## Scope
- First-order lower-axis NVE; E = 4/5; three spins; 50-digit floating point, not interval.
- At each spin, the open sliver (30/7 − 1e−12, 30/7) is sampled, not counted.
- The physical family is 0 ≤ k ≤ 30/7 (T38 grading 1c). Region A's k < 0 part is a complex-metric region, included
  only to enclose k = 0.
- Peak memory < 1 GB. Run sequentially, 1 core, nice 10, roughly 1–2 h per spin.

**Run 1 (chain PID 29686): CRASH at spin 3/10, no verdict.**
- Region A had completed and passed every registered check: F 2 zeros; tr M0, tr M1 and every T1 − s with 0; step
  8e−23; C2 OK; Kerr 6e−50; C1 (2, 2). Region B's geometry and counts were also clean (span 0.35, (1, 2)).
- The crash was in B-repro: the Laurent builder's ABSOLUTE 1e−40 thresholds (trimming the vanishing leading radicand
  coefficient at k = 30/7, and detecting the leading series power) failed at spin 3/10, where the residual is larger
  than 1e−40. That left a spurious root, ρ ~ 3e24.
- Fixed with RELATIVE thresholds (1e−35 × scale) in `_nve_lower_kc.py` and `_nve_lower_hp.py`. Checked at spins 3/5,
  3/10, 4/5 and 9/10, k ∈ {0.1, 4, 30/7} (ρ_c correct). At spin 3/5 it reproduces the original `_nve_lower.c0_laurent`
  to ≤ 1e−50.
- No criterion changed. The chain was stopped by me and is rerun from the start as run 2 (log of run 1:
  `spin_run_3_10_crash1.out`).

## Spin 4/5 (run 2): registered verdict **EXCEPTIONAL CANDIDATES**, resolved POST HOC as no exception (labelled)
**Region A passes in full:**
- F has 2 zeros (the Kerr double zero); tr M0, tr M1 and every T1 − s have none.
- Step agreement 4.6e−22; C2 and C1 OK; Kerr |F| 1e−50.

**Region B:** F_h, T1 and all T1 − s have no zeros, but **count(TΓ) = count(T1Γ) = 1**, so the registered rule ("TΓ or
T1Γ zero-free") failed. Every control passed: B-repro 7e−52; repro-F 1.5e−48; MF-trunc fired; P2 non-VA by both
pictures; P1 Kerr imprimitive; steps agree to 3e−21; geometry and counts clean. The endpoint is non-VA.

**Post-hoc diagnosis (scripts `_nve_spin_locate.py` and `_nve_spin_kstar.py`; outputs `spin_locate_4_5.out` and
`spin_kstar_4_5.out`):**
- **The registered rule had a DESIGN FLAW: T1Γ is not independent.**
  - M1 encloses {r+, p+} and Γ encloses {r+, p+, p−}, so M1Γ⁻¹ encircles the single simple point p−. Its trace is
    identically 0.
  - So the Fricke identity gives **tr(M1Γ) = tr M1 · tr Γ identically**.
  - Check at the endpoint: (−1.49828 + 2.04609i)(−0.030099) = 0.045097 − 0.061585i, equal to T1Γ.
  - Hence count(T1Γ) = count(T1) + count(TΓ), so 0 + 1. Every zero of TΓ is a zero of T1Γ, and there the half-plane pair
    is genuinely imprimitive (two order-4 elements generate a dihedral group).
  - The rule could therefore never exclude imprimitivity where TΓ = 0. At spin 3/5 (§162) and 3/10, TΓ has no zeros,
    so those verdicts are unaffected.
- **The common zero:** k* = 4.008164511150082 (real). There T1Γ ≈ 2.5e−43, TΓ ≈ 5e−23 (the secant tolerance), and
  F_h = −10.17 − 5.69i ≠ 0.
  - My bisection for TΓ alone had a reversed-bracket bug and stopped after one step. The secant on T1Γ is the reliable
    locator.
- **At k* the GROUP is not imprimitive.** The independent circle pair (M0 = circle R0, M1 lasso; Laurent c0; ρ_c 0.906
  < R0 − 0.1) gives:
  - F = 15.59 + 8.72i; tr M0 = 1.459; tr M1 = −1.0541 + 2.6989i (non-real, at distance 2.70 from S).
  - So it is Zariski-dense at k* and at k* ± 0.002. The lasso trace equals the half-plane T1 at k*, as it must.
- **Conclusion (post hoc, labelled):** no exceptional k at spin 4/5, E = 4/5, in (0, 30/7 − 1e−12] ∪ {30/7}. The
  half-plane pair degenerates only at k*, where the full group is SL₂ by the circle pair.

**Lesson:** a classifier's trace triple must consist of INDEPENDENT functions on the region. Check the Fricke
relations (here M1Γ⁻¹ is a single-point loop) before registering. Spin 9/10 runs under the same rule. If TΓ has zeros
there, they are resolved the same way, with an independent pair at each zero.

## AMENDMENT S1 (2026-11-22, dated; committed BEFORE any spin 9/10 output exists: spin_run_9_10.out is empty, region A still running). The zero-resolution protocol for region B, now REGISTERED for spin 9/10
Reason: the spin 4/5 diagnosis. Because tr(M1Γ) = tr M1·tr Γ identically, the region-B rule cannot exclude
imprimitivity at zeros of TΓ. For spin 9/10, if count(T1) = 0, count(T1 − s) = 0 for all s and count(F_h) = 0, but
count(TΓ) > 0:
1. **Locate every zero of TΓ in B.**
   - TΓ is real on real k (Γ is reflection-symmetric), so find real zeros by bisection on Re TΓ over a 25-point real
     grid on [B_X0, B_X1], with a correctly ordered bracket, to |Δk| < 1e−14.
   - If the number of real zeros is less than count(TΓ), find the complex ones by complex secant on T1Γ from the
     boundary samples of smallest |TΓ|, to |T1Γ| < 1e−30.
   - The protocol fails (UNDETERMINED) unless the number located equals count(TΓ).
2. **At each zero k_j, test the full group with an independent pair:**
   - **(a) If ρ_c(k_j) < R0 − 0.1 and the region-A geometry holds at k_j: use the circle pair (M0 = circle R0,
     M1 = lasso; Laurent c0).** Require Z1–Z4 at steps 0.2 and 0.12, with every pair agreeing to a relative 1e−15:
     - F ≠ 0;
     - tr M0, tr M1 and tr M0M1 all nonzero (≥ 1e−8);
     - Im tr M1 ≠ 0 (≥ 1e−8);
     - distance of tr M1 from S ≥ 1e−3.
   - **(b) Otherwise, near 30/7: use the extra half-plane pair (M1, M1′),** with M1′ the capsule lasso around [r+, p−]
     (the mirror of M1), so M1M1′⁻¹ is not a single-point loop. Require Z1–Z4 for (M1, M1′) with the same thresholds,
     using the engine.
3. **Verdict at spin 9/10:**
   - NO EXCEPTIONAL k if every k_j passes;
   - EXCEPTIONAL CANDIDATE at any k_j that fails, listed;
   - UNDETERMINED if the location fails.
   - Labels: "registered (amendment S1)" for spin 9/10; spin 4/5's resolution stays labelled post hoc.

## AMENDMENT S2 (2026-11-22, before running): the interval-certified sliver (30/7 − δ0, 30/7] at each tested spin, E = 4/5
Asked by the Bridge. Code: `data/nve/t48b_spin/sliver_spin.py`. It is our patched T48b (`t48b_fixed`: exact float S,
Z1b dropped) with three changes:
- **Spin as input:** `T48_GEO` → `geo_<spin>.json`, built from OUR endpoint positions (`spin_geo_*.json`; §161 at
  3/5).
- **Loops by a fixed rule:**
  - box around u_p of half-width 0.49·Im u_p;
  - box around u_tp of half-width 0.1 and half-height 0.45·Im u_p;
  - base point max(Re u_p, u_tp) + max(0.25, 2·Im u_p).
  - Kerr: box around 2/a + i of half-width 0.45; box around r+_Kerr/a of half-width 0.25; base point
    max(2/a, r+_K/a) + 0.35.
  - At spin 3/5 this reproduces Neon's geometry to within a base-point shift.
- **Z4b (|tr A| > 2) dropped.** Z4 (Im tr B ≠ 0) alone gives infinite order.
- **Everything else is unchanged:** the O(L) bounds, the whole-box defect enclosure, the Gronwall drift, Z1
  (τ(M1, M3) ≠ 0), Z2 ([A, B] ≠ 0) and Z3 (tr A, tr B, tr AB ≠ 0).

**Spins:** 3/5 (cross-check against T48b: δ0 should be ~1.4e−11), then 3/10, 4/5, 9/10.

**Pass at a spin requires all of:**
- endpoint Z1–Z4 certified;
- the Kerr control's enclosure upper bound below the endpoint's lower bound;
- the wrong-tail control shrinking δ0;
- certified **δ0 > 1e−12**.

**Report rules:**
- If δ0 ≤ 1e−12, report it as is. Nothing is widened or retuned.
- An assertion failure (defect too large, or the endpoint certificate failing) is reported as FAIL at that spin, with
  its reason.

**S2 RESULT (run 2026-11-22):**
- **Spin 3/5 (cross-check): PASS.** δ0 = 1.32869e−11 (T48b: 1.37e−11). Kerr enclosure top 0.0013 < endpoint bottom
  0.0036. The wrong tail shrinks δ0 by 3.6e9.
- **Spins 4/5 and 9/10: FAIL, as registered.** An assertion in the VE3-only Cauchy bounds (C3, C4; the disk r = 0.4
  violates cos 4θ > 0 at these geometries) aborted the run. **C3 and C4 are never used by the first-order certificate**
  (the Gronwall drift uses C0 and C1 only; checked in the code).
- **Spin 3/10: FAIL, as registered.** At the endpoint, Z2's ∞-norm enclosure of [A, B] has lower bound 0, so it is too
  loose. Every other condition holds clearly: |τ(M1, M3)| ≈ 0.51; |tr A| ≈ 2.26; |tr B| and |tr AB| ≈ 2.00;
  Im tr B ≈ 0.128 (diagnostic copy).

## AMENDMENT S3 (post-failure, 2026-11-22, before any rerun; results will be labelled "under post-failure amendment S3")
1. **Remove the Cauchy-disk block (C3, C4, and its two assertions).** It is unused by the VE1 certificate.
2. **Z2 holds if EITHER** the matrix-norm drift test (unchanged) **OR** |τ(A, B)| > 0 on the drift-inflated trace
   enclosures (Fricke: τ(A, B) = tr[A, B] − 2 ≠ 0 implies [A, B] ≠ I).
   - Mathematically this is the same condition, evaluated from the tighter trace enclosures.
   - At spin 3/5 the matrix test already passes, so 3/5 is unaffected.
3. **Rerun spins 3/10, 4/5 and 9/10.** Pass criteria and report rules are as in S2, including δ0 > 1e−12, the Kerr
   control and the wrong tail.

**S3 RESULT (2026-11-22; label: under post-failure amendment S3):**
- **Spin 4/5: PASS.** Certified δ0 = 2.40765e−10 (241 × 1e−12).
  - Z1 |τ(M1, M3)| ≥ 8.49; Z3 |tr A| ≥ 7.47, |tr B| ≥ 2.53, |tr AB| ≥ 2.43; Z4 Im tr B ∈ [2.041, 2.051].
  - Kerr enclosure top 0.0020 < endpoint bottom 0.0759. The wrong tail shrinks δ0 to 1.2e−18.
- **Spin 9/10: PASS.** Certified δ0 = 3.63466e−10 (363 × 1e−12).
  - Z1 ≥ 16.97; Z3 ≥ 15.0, 3.60, 2.95; Z4 Im tr B ∈ [3.602, 3.642].
  - Kerr 0.0025 < 0.668. Wrong tail 2.8e−18.
- **Spin 3/10: FAIL. The method's margin is genuinely too small at low spin.** It is not a precision accident. Our
  50-digit walker on the same loops gives:
  - τ(A, B) = −4.455e−10, identical for every pairing of the three single-point loops, while τ(M1, M3) = −0.0238 −
    0.5099i;
  - for the alternative pair X = M3M1 (the lasso) and Y = M2M3M1 (Γ-like): τ(X, Y) = −0.0238 − 0.5099i, but
    **tr Y = 2.1e−5** and tr XY = 4.2e−5.
  - So the endpoint group at spin 3/10 is NEAR-imprimitive: either the pair nearly commutes or one trace is nearly 0.
    It is still Zariski-dense in floating point (region B counts, §161-type endpoint classification, sliver samples).
  - With drift constants r ~ 1e5, Z2 on (A, B) cannot keep a 4e−10 margin for any δ0 near 1e−12.
  - **A possible S4 (not run; needs the Bridge's OK):** the (X, Y) pair at iv.dps ≥ 30 with tighter defect tolerances,
    so that tr Y ≈ 2e−5 is enclosed away from 0, with the drift kept below 2e−5. A rough estimate gives δ0 ~ 1e−11,
    which is marginal.
- **Net for the sliver:** interval-certified at spins 3/5, 4/5 and 9/10 (E = 4/5). At spin 3/10 it is covered by
  50-digit floating point only (samples at 30/7 − 1e−13 to 1e−15, and the endpoint, all non-VA).

**Wording fix (the Bridge):** "τ(A, B) identical for every pairing of the three single-point loops" is automatic, not
three confirmations. For three loops whose product is the identity, τ(A, B) = τ(B, C) = τ(C, A) identically, so it
is ONE number. (The same lesson as fleet slip 11.)

## AMENDMENT S4 (2026-11-22, registered BEFORE running; Bridge OK; ITS FAILURE IS FINAL, with no S5): the sliver at spin 3/10
Code: `data/nve/t48b_s4/sliver_s4.py`. It is `sliver_spin.py` with these changes:
- **Pair:** X = M3M1 (lasso-like) and Y = M2M3M1 (Γ-like). Same loops (S2 rule) and basis.
- **Precision:** iv.dps = mp.dps = 30; defect tolerance 1e−11 per subinterval (Kerr and endpoint); nsub = 16;
  bisection depth ≤ 18.
- **Conditions on [30/7 − δ0, 30/7]**, on drift-inflated traces (dX, dY, dXY from the loop Gronwall bounds; drift
  2d per trace):
  - Z1 + Z2: |τ(X, Y)| > 0 (irreducible, and [X, Y] ≠ I);
  - Z3: |tr X|, |tr Y| and |tr XY| > 0;
  - Z4: Im tr X ≠ 0.
- **Kerr control:** Kerr's Y is a 3-point loop, hence antidiagonal with tr = 0. Its enclosure must contain 0 AND its
  |·| upper bound must be below the endpoint's |tr Y| lower bound. (The certificate must distinguish exact
  imprimitivity from |tr Y| ≈ 2e−5.)
- **Wrong-tail control** as before.
- **PASS:** endpoint certified, both controls OK, and δ0 > 1e−12. δ0 is reported even if marginal.
- **FAIL:** anything else. The spin 3/10 sliver then stays floating-point only, with no further amendment.
- **Expected margins** (50-digit walker): |tr Y| ≈ 2.1e−5, |tr XY| ≈ 4.2e−5, |τ| ≈ 0.51.

**S4 RESULT (2026-11-22, `t48b_s4/out_3_10.txt`, 833 s): FAIL as registered, and FINAL.**
- **The endpoint k = 30/7 at spin 3/10 IS interval-certified Zariski-dense:**
  - |τ(X, Y)| ∈ [0.510459, 0.510462];
  - |tr X| ≈ 2.00218; Im tr X ∈ [0.127596, 0.127597];
  - **|tr Y| ∈ [2.0423e−5, 2.1802e−5]** (the 50-digit value is 2.1107e−5, inside);
  - |tr XY| ∈ [4.088e−5, 4.368e−5];
  - max defect ρ = 6.4e−8.
- **Kerr control passes and is sharp:** the enclosure of tr Y_Kerr contains 0, and |tr Y_Kerr| ≤ 1.34e−6 < 2.04e−5.
- **But certified δ0 = 7.37e−15 < 1e−12.** The tr Y margin (2e−5) is exhausted by the Gronwall drift within ~1e−14 of
  30/7. The wrong tail gives 1.1e−27.
- **Final status at spin 3/10:** the sliver is interval-certified on (30/7 − 7.4e−15, 30/7] only. On
  (30/7 − 1e−12, 30/7 − 7.4e−15] it is 50-digit floating point (samples non-VA). No S5.

## Endpoint obstruction vs spin (`scripts/_nve_endpoint_scaling.py`, `endpoint_scaling.out`; S2 loop rule; every value stable to < 1e−33 across dps 50 and 70 and steps 0.35 and 0.2)
| spin | tr Y (Γ-like loop; the imprimitivity margin of the half-plane pair) | τ(A, B) = −(tr Y)² | \|τ(M1, M3)\| |
|---|---|---|---|
| 0.3 | +2.1107e−5 | −4.4551e−10 | 0.510 |
| 0.6 | +3.1167e−3 | −9.7137e−6 | 2.866 |
| 0.8 | +3.0099e−2 | −9.0593e−4 | 8.54 |
| 0.9 | −0.17550 | −3.0800e−2 | 17.12 |

- **τ(A, B) = −(tr Y)² holds to every digit at all four spins** (a Fricke relation for these loops). So one number
  carries the near-imprimitivity.
- **|tr Y| grows steeply with spin:** log-log slope 7.2 on 0.3–0.6 and 7.9 on 0.6–0.8. **The obstruction weakens
  rapidly toward low spin; spins below 0.3 are not tested.**
- **tr Y changes sign between 0.8 and 0.9,** so it vanishes at some spin a_c ∈ (0.8, 0.9) at the endpoint. That is
  the same zero curve that passes through (0.8, k* = 4.0082).
  - Along that curve the half-plane pair is imprimitive. The full group must be settled there by an independent pair,
    as at k*.
  - It does not affect the tested spins, but it is worth stating.

**Why τ(A, B) = −(tr Y)² holds exactly (for the write-up).**
- M1, M2 and M3 are single-point loops, with exponents ¼ and ¾ at a simple zero or pole of P. So tr Mᵢ = 0, and with
  det = 1 this gives Mᵢ² = −I, i.e. Mᵢ⁻¹ = −Mᵢ.
- With A = M2M1 and B = M3M2: A⁻¹ = M1M2 and B⁻¹ = M2M3. Hence [A, B] = M2M1M3M2·M1M2M2M3 = −(M2M1M3)².
- By tr(W²) = (tr W)² − 2, τ(A, B) = −(tr M2M1M3)².
- For trace-zero X, Y, Z, tr(XYZ) = −tr(XZY). So tr(M2M1M3) = −tr(M2M3M1) = −tr Y, and τ(A, B) = −(tr Y)².
- In words: A and B commute exactly when the 3-point loop Y has trace 0, which is the imprimitive (Kerr-like) case.

## Comparison with Neon T50 (blind; our numbers were not given to it), graded 2026-11-22: **AGREE to every printed digit**
Source: `neon_work/onlykerr/T50_full.md` and `T50_code/endpoint_spin_study.py` (sha256 b4024130…). T50's values were
compared with our committed `endpoint_scaling.out` (e025bbf, 15 significant digits printed):
- **Spin 0.3:** τ(M1, M3) −0.023827775480582 − 0.509903821338622i; τ(A, B) −4.4550650918703e−10. Equal.
- **Spin 0.6:** τ(M1, M3) −0.737270245448137 − 2.7690338008439i; τ(A, B) −9.71365805269462e−6. Equal.
- **Spin 0.8:** τ(M1, M3) −5.94162746200745 − 6.13124334276386i; τ(A, B) −9.0592502892551e−4. Equal.
- **Spin 0.9:** τ(M1, M3) −17.1099311668528 + 0.608299045397344i; τ(A, B) −0.0308000378939229; tr Y −0.175499395708142.
  Equal.
- **Also found independently by T50:** the exact relation τ(A, B) = −(tr M1M2M3)². Its Kerr controls are imprimitive at
  every spin.

**Independence, stated exactly:**
- **Independent:**
  - the integrators: T50's order-44 Taylor scheme vs our §159 power-series walker;
  - the endpoint c0: T50's elementary closed form vs our Laurent series at ∞;
  - the root finding;
  - the code.
- **Shared:** the CHOICE of loop classes (single-point loops around p+, p− and r+, based on the real axis to the right).
  Both descend from Neon's T48b loops; T50's box sizes and base point differ from ours (0.45 vs 0.49 × Im u_p, base
  3·Im u_p vs max(0.25, 2·Im u_p)). Traces depend only on the classes.
- **Wording:** "two independent implementations of the same loop invariants". The classes are a choice of generators,
  not an input that could bias the values.

**T50's degenerate spin** a_c = 0.858446198791717253… (secant, 30 digits) lies in our (0.8, 0.9). Its independent
circle-type pair there is Zariski-dense (floating point, relayed). We have not reproduced it yet.

**Dated line (2026-11-22, before running): reproduction of T50's a_c** (known target 0.858446198791717…). Script
`scripts/_nve_ac.py`.
- Secant in spin on tr Y at the endpoint (S2 loop rule, our walker), starting from spins 0.85 and 0.87, to
  |Δa| < 1e−12.
- Then the circle pair at a_c, with Z1–Z4 at steps 0.2 and 0.12.
- **Pass:** a_c agrees with T50 to ≥ 10 digits, and the circle pair is non-VA.

**a_c reproduction RESULT (2026-11-22; `ac_secant.out`, `ac_circle.out`): PASS. a_c is two-implementation.**
- **Our secant on the endpoint tr Y:** a_c = 0.858446198791717253463097 (final residual tr Y = 5.7e−23). T50:
  0.858446198791717253463067. Agreement to 22 digits.
- **Circle pair at a_c** (R0 = 1.190, with ρ_c = 0.858 and outer min |z| = 1.521, so margins of 0.33 on each side):
  - F = 35.297 + 15.820i;
  - tr M0 = 0.89973;
  - tr M1 = −0.89489 + 2.88422i (non-real, at distance 2.886 from S);
  - tr M0M1 = 6.4250 + 2.7575i;
  - steps 0.2 and 0.12 agree to 1.0e−34.
  - So Z1–Z4 hold: Zariski-dense, non-VA, at the spin where the half-plane pair degenerates. Floating point (50 digits).
