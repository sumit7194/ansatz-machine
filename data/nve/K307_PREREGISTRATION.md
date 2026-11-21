# The endpoint k = 30/7 of the branched-twist family: lower-axis first-order NVE test (pre-registration, 2026-11-21)

**Ask.** The Bridge GO (2026-11-21), after `T38_GRADING.md` point 1d.

**Why.**
- At k = 30/7, B(w) = (40/7)(3w + 1) > 0, and the twist's 1/z² (angular-momentum) term, which is proportional to
  √(90 − 21k), vanishes.
- So the endpoint is a real, asymptotically flat, J = 0 member of the family, and no result covers it. "k < 30/7" in
  the relayed proof excludes it, and the §159 code refused it.
- Also, k ↦ c0 is not analytic at 30/7 (terms c4^{3/2} and c4² log c4, with c4 = 90 − 21k). So "K*(a) is discrete in
  (0, 30/7)" leaves open infinitely many exceptional k accumulating at 30/7.

**Fixed.** Spin a = 3/5, M = 1, E = 4/5. The §159 lower-axis NVE v″ = −(3/16)(P′/P)²v, with P = E² − f0⁻ and
f0⁻ = f0/(f0² + c0²). 50 digits, Taylor order 50. Code: `scripts/_nve_lower_kc.py`. Its Laurent builder now accepts
the endpoint's leading power w¹⁰ (c0″ ~ w⁵) as well as w⁸; nothing else changed. Run script:
`scripts/_nve_lower_k307.py`.

## What is computed at k = 30/7
1. **Circle picture** (as §159 / gap B; valid at the endpoint because ρ_c = a there):
   - M0 = the circle |z| = 1.35;
   - M1 = the capsule lasso around {r+, p+};
   - all based at 1.35.
   - Record F = tr[M1, M0] − 2, tr M0 and tr M1, at steps 0.35 and 0.2.
2. **Half-plane picture** (the one the continuity argument needs):
   - Γ = a lasso from 1.35 to a disc containing {r+, p+, p−}, lying in Re z > a + 0.1;
   - M1 as above.
   - Record F_h = tr[M1, Γ] − 2, tr Γ and tr M1, at both steps.
3. **Finite-group exclusion:** the distance of tr M1, tr M0 and tr Γ from S = {±2, ±1, 0, ±√2, ±0.618…, ±1.618…}
   (the traces of finite subgroups of SL₂), and Im tr M1.

## The continuity-from-below argument (registered as an argument; exercised by C-cont)
- On any compact K in {Re z > a}, c0(·; k) → c0(·; 30/7) and c0′(·; k) → c0′(·; 30/7) uniformly as k → 30/7⁻.
  - T14's ray formula has a jointly continuous integrand on [k₀, 30/7] × [0, 1] × K, because √ is uniformly
    continuous and the radicand is bounded.
  - The derivative is handled the same way.
- So the NVE coefficient converges uniformly on K minus small discs around the singular points.
  - Those points (p±, r+: zeros of analytic functions that converge uniformly) converge by Hurwitz's theorem.
  - Loops in K that avoid them carry monodromies that converge, by continuous dependence on parameters.
- Hence F_h, tr Γ and tr M1 are continuous at 30/7 from below.
- **If** they are nonzero at 30/7 (and tr M1 ∉ S), they are nonzero on some (30/7 − δ, 30/7]. Then K*(3/5) cannot
  accumulate at 30/7. Combined with analyticity on (0, 30/7) and the isolated double zero at k = 0, K*(3/5) ∩
  (0, 30/7] is **finite** at E = 4/5, and by gap B it lies inside (4.05, 30/7).
- The circle picture is NOT continuous there: one √B branch point escapes along the imaginary axis through
  |z| = 1.35 as k → 30/7⁻. That is why the half-plane picture carries the argument.

## Controls (any failure → VOID)
| control | what | must give |
|---|---|---|
| C0 reproduction | k = 1/10 through the edited builder (w⁸ path) | F agrees with the registered 0.00196656555091338 + 0.00101256196325471i to 1e−15 |
| C-c0 (the w¹⁰ path) | the endpoint Laurent c0 vs T14's independent ray formula at 6 points with \|z\| ∈ [1.4, 4] | agreement to 1e−15 |
| P1, must give VA | Kerr (k = 0) through the same script and loops | \|F\| ≤ 1e−25 and \|tr M0 − 2\| ≤ 1e−25 (known: §159 / lower_comm) |
| P2, planted, must give F = 0 at the endpoint | at k = 30/7, M1 replaced by the circle loop traversed twice (based class M0²), which commutes with M0 | \|tr[M0², M0] − 2\| ≤ 1e−25 |
| C-step | steps 0.35 vs 0.2 at the endpoint | F, F_h and every trace agree to a relative 1e−15 |
| C-geo | at the endpoint: ρ_c ≤ 1.1; lasso and disc clearance ≥ 0.05; outer points \|z\| ≥ 1.55; disc in Re z > a + 0.1; argument-principle counts (2, 2) outer and (0, 0) inner | all hold |
| C-cont (exercises the continuity clause) | c0 and c0′ (ray formula) at k = 30/7 − δ, δ ∈ {1e−1, 1e−2, 1e−3, 1e−4}, at 8 points on the Γ and M1 contours; and r+, p± (Newton on the ray-formula G) at the same k | max differences from the endpoint decrease monotonically in δ, with a fitted log-log slope in [0.3, 1.2] for both; at δ = 1e−4, point shifts < 1e−2 |
| C-cont must-fire | the escaping branch point \|z_b(δ)\| = a√\|w_big\| at the same δ | > 1.35 for the smallest δ, so the circle picture is refused near 30/7 |

## Outcomes
- **ENDPOINT OBSTRUCTED (non-VA):**
  - |F| ≥ 1e−8 and |F_h| ≥ 1e−8, stable under C-step;
  - tr M0, tr M1 and tr Γ all nonzero (≥ 1e−8);
  - tr M1 non-real and at distance ≥ 1e−3 from S.
  - Then the circle pair is Zariski-dense in SL₂ at k = 30/7. With C-cont, **K*(3/5) does not accumulate at 30/7 at
    E = 4/5, so K*(3/5) ∩ (0, 30/7] is finite and lies in (4.05, 30/7).**
- **ENDPOINT VA-COMPATIBLE:** F = 0 to 1e−25. The endpoint is a candidate exception, to be reported as such.
- **VOID:** any control fails. **UNDETERMINED:** the steps disagree.

## Scope
- One (E, spin), floating-point (50 digits).
- The continuity step is an argument plus a numerical exercise, not an interval certificate.
- It does not decide whether K*(3/5) ∩ (4.05, 30/7) is empty.
- Memory peak expected < 1 GB (§159 runs used ~200 MB). Estimate ~20–40 min, 1 core, nice 10.

## OUTCOME (run 2026-11-21 16:31, PID 87948, from the registered code 7702285): **VOID**
Three registered controls failed. Passed: C0 (diff 3.8e−18), P1 (|F| 2.7e−50, |tr M0 − 2| 1.3e−36), P2 (5.3e−51),
C-step (worst relative 6.1e−21), the counts (2, 2, 0, 0), and C-cont-fire (|z_b| = 54 at δ = 1e−4).

**Diagnosis (post hoc, labelled):**
1. **C-c0 failed (max diff 0.0138): a design error in the control, not in the builder.**
   - Per point (diagnostic run): the five points with Re z > a agree to ≤ 4.6e−33.
   - The one failure is z = −1.8 + 2.2i (arg u = 129°): equal magnitude, opposite sign.
   - The ray formula is T14's representation for Re u > 1 only. Near c4 = 0, its x-path passes close to the escaping
     radicand root, and it lands on the other sheet. The Laurent series is the continuation from ∞, the one used
     everywhere else.
   - Test points should have been restricted to the ray formula's domain.
2. **C-geo failed: a genuine near-collision at the endpoint.** At k = 30/7, E = 4/5:
   - r+ = 1.8008 and p± = 1.8033 ± 0.0534i, so the poles sit ~0.053 from the zero.
   - The lasso clearance is 0.032 against an ABSOLUTE threshold of 0.05 that was set at gap-B scale.
   - Walker accuracy is unaffected: C-step agrees to 6e−21.
3. **C-cont failed: a bug in the measurement code.** `c0_ray` forces `workdps(30)` internally, so `mp.diff`'s
   higher-precision evaluations are rounded back and every c0′ difference is exactly 0. That made the monotonicity
   test fail. The c0 and point columns behaved as the argument predicts: monotone, slopes 0.88 and 0.87.

**Endpoint values (seen; NOT a verdict, because the run is VOID):**
- F = 18.08 + 66.86i; F_h = −0.737 − 2.769i;
- tr M0 = 1.7034; tr M1 = −1.942 + 0.713i; tr Γ = −0.0031;
- identical at both steps.

**Proposed amendment A1 (post-failure, made AFTER the endpoint values were seen; it needs the Bridge's OK before a
rerun):**
- C-c0: test points restricted to Re z > a.
- C-cont: `c0_ray` uses the caller's precision, so mp.diff works.
- C-geo: scale-relative clearance, ≥ 0.3 × the separation of the nearest singular points (here 0.6×), with C-step as
  the accuracy arbiter.
- The endpoint computation itself is unchanged (deterministic), so A1 can only turn VOID into a verdict, not change the
  numbers. That grade must stay visible.
