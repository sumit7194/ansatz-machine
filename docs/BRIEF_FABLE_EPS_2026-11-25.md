# Brief for the Fable side-session (ansatz-machine-personal): an EFFECTIVE ε for Statement A, and a first build step for route (i)

**From:** ansatz-machine (office), via the Bridge, for Sumit.
**Version 2, 2026-11-25** (v1 was a quick draft; v2 replaces its method with a sharper one, see §2).
**Builds on:** your own C2_ANALYTIC.md (now on main as 66873a2 and 29d2555, verified in c3766aa).
**Status of this brief:** nothing goes to you until Sumit says so.

## 0. Where things stand (all on main; read these first)
- **`data/nve/CLAIM_FAMILY_II.md` v3, "Statement A".** For each spin a ∈ {3/10, 3/5, 4/5, 9/10} at E = 4/5 there is
  ε_a > 0 such that, for every k ∈ (0, ε_a), the monodromy group of the lower-axis ρ-equation is Zariski-dense.
  **ε_a is not quantified. Part A of this round quantifies it.**
- **`data/nve/C2_ANALYTIC.md`**, your note:
  - c2 = sinh²(κω)I₊I₋/κ², κ = a√(1 − E²);
  - X = M0′(0) = ∮_C Φ⁻¹(∂_k A)Φ dz in Kerr's basis, with x12 = −I₋/(2κ) and x21 = I₊/(2κ);
  - §6b: the interval certificate that I₊, I₋ and Re κω are nonzero (`scripts/_nve_c2_certify.py`, mpmath.iv).
- **`data/nve/C2_OFFICE_CHECK.md`**, the verification.
  - The 50-digit engine agrees with your formula to 12 digits at 7 spins, including c2's sign change near
    a\* ≈ 0.908.
  - The trapezoid bound was checked at source: Trefethen–Weideman 2014, Thm 3.2 p. 396; Thm 2.2 p. 392 is the annulus
    form.
- **`data/nve/MRS_SECTION.md` §5d, Lemma K.**
  - Setting: S = C ∪ L ∪ [R0, ∞), with C the circle |z| = R0 and L the capsule lasso based at R0.
  - Hypotheses: (H1) |z| ≥ ρ > a/√3 on S; (H2) r± and p± are off C ∪ L; (H3) a < R0 < min|r±, p±|.
  - Key fact: c0″(z; k) = c_K″(z)·√(1 − kφ(w)), with φ(w) = (21w² − 18w + 1)/(10(3w − 1)²) and w = z²/a².
  - Conclusion: M0(k) and M1(k) are holomorphic for |k| < δ, M0(0) = I, and F(k) = tr[M1, M0] − 2 = c2k² + O(k³).
  - **δ is not quantified.**
- **The loops.** These are the spin-scan region-A loops (`scripts/_nve_spin_scan.py`: `kerr_points`, `LauA`;
  `scripts/_nve_lower_kc.py`: `capsule_lasso`).
  - The circle radii R0 are 1.1492, 1.35, 1.3382 and 1.2639 (spins 3/10, 3/5, 4/5, 9/10).
  - The lasso is `capsule_lasso(r+, p+, others, b=R0)`, with capsule radius ≤ 0.15. Its tail runs along ℝ from R0.
  - The Kerr points r± are the roots of N = E²D − Δ, and p± = 2 ± ia.
  - Every loop stays at least 0.744 from the pinch interval |z| ≤ a/√3 (MRS §3 note).
- **Engine values at k = 0** (`data/nve/c2_engine_check.out`):
  - tr M1(0) is non-real at all four spins (Im between 1.46 and 3.82).
  - c2: 0.0279 + 0.0460i, 0.1935 + 0.0985i, 0.1621 + 0.0149i, 0.0158 − 0.0016i.
  - c3 (floating, for orientation and as a control): 0.0013 + 0.0075i, 0.0306 + 0.0271i, 0.0301 + 0.0195i,
    −0.0062 + 0.0412i.
  - At spin 9/10 a third zero of F sits at k ≈ 0.11 + 0.34i. Any honest r_a there must be well below 0.36.

## 1. Part A, the goal: a certified, explicit ε_a per spin
Find r_a > 0, as a rigorous interval-arithmetic statement, such that for every k with 0 < |k| ≤ r_a (in particular
every real k ∈ (0, r_a]) the pair ⟨M1(k), M0(k)⟩ satisfies:
- **(Z1)** F(k) ≠ 0, i.e. irreducible;
- **(Z2)** tr M0(k) ≠ 0 and tr M1(k) ≠ 0, i.e. not imprimitive;
- **(Z3)** tr M1(k) ∉ [−2, 2], so M1(k) is loxodromic, of infinite order, hence not finite.
Then Statement A holds with ε_a = r_a, a number. (Z3) is cheap, because tr M1(0) is non-real with margin ≥ 1.46.

## 2. Part A, the recommended route (a sharper one than v1; yours to improve)
**The identity that makes it sharp** (checked here with sympy). For M0 = I + N in SL₂ and any invertible M1, write
Ñ = M1 N M1⁻¹. Then

    F = tr[M1, M0] − 2 = −2 det N + (det N)² − tr(Ñ N)          (exact),

and det(I + N) = 1 gives tr N = −det N. With N = kX + E, where E = O(k²) and tr X = 0, so that tr X² = −2 det X:
- the k² part is tr X² − tr(M1 X M1⁻¹ X), which is c2 once M1 → M1(0);
- every other term is at least cubic in (|k|, ‖E‖/|k|), with explicit coefficients.

**Why this beats a Cauchy bound on F.** A Cauchy bound on F needs sup|F| on a k-circle, which is roughly
2‖M1‖²·‖M0 − I‖. It gives r ~ |c2|R³/M_F, which is likely around 1e−6. The identity puts the smallness where it
belongs: N is O(k), and only the CIRCLE monodromy has to be expanded. The lasso enters only through M1(k), to O(1)
accuracy.

**Steps.**
1. **First order of the circle, certified.** You already enclose X; certify x11 as well. ‖X‖ comes out as an
   interval.
2. **The second-order remainder on the circle only.** In Kerr's basis Φ (single-valued on C, since M0(0) = I), M0(k) is
   the Dyson series of B(z; k) = Φ⁻¹ΔA Φ along C, with ΔA = [[0, 0], [−Δq, 0]] and Δq = q(z; k) − q(z; 0). So:
   - E = ∫_C (B − kB₁) + R₂, where kB₁ is the part linear in k (from δq);
   - ‖R₂‖ ≤ e^{L} − 1 − L ≤ L²e^{L}/2, with L = ∫_C ‖B‖|dz|;
   - ‖B‖ ≤ ‖Φ‖²|Δq|/(2κ), because ‖Φ⁻¹‖ = ‖Φ‖/|det Φ| for 2 × 2 and det Φ = W = −2κ;
   - pointwise, |Δq − kδq| ≤ Q_R|k|²/(R(R − |k|)) for |k| < R, where Q_R = sup |Δq| over z ∈ C and |k| = R
     (Cauchy in k). Enclose Q_R with interval boxes in (z, k).
   This gives ‖E‖ ≤ C_E|k|² for |k| ≤ r < R, with C_E explicit. The circle stays far from r± and p±, so Φ is benign
   there.
3. **M1(k) to O(1).** ‖M1(k) − M1(0)‖ ≤ ‖M1(0)‖(e^{L₁} − 1), with L₁ = ∫_L ‖Φ⁻¹ΔAΦ‖|dz| along the lasso.
   - Crude is fine here: it multiplies k² and only feeds the cubic remainder.
   - Φ is large near r₊ and p₊ on the capsule (radius ≤ 0.15). Keep the registered capsule; do not shrink it.
4. **Holomorphy domain (Lemma K with numbers).** Every bound above needs q(z; k) holomorphic for |k| ≤ R on the
   relevant path. Certify, with boxes in (z, k):
   - |kφ(w)| ≤ ½ on S, including the ray [R0, ∞), where φ → 7/30;
   - f0² + c0² ≠ 0 and P ≠ 0 on C ∪ L, each with an explicit lower bound.
   c0 and c0′ come from your integral from +∞ with complex k. The integrand c_K″·√(1 − kφ) is O(s⁻⁴), so the tail is
   explicit. **The binding constraint on R is probably P ≠ 0 on the capsule, as r₊ moves with k.** Measure it.
5. **Assemble.**
   - **(Z1):** |F − c2k²| ≤ (an explicit cubic bound from the identity, steps 2 and 3), and this is < |c2||k|²
     for 0 < |k| ≤ r.
   - **(Z2):** tr M0 = 2 − det N, so it is nonzero once |det N| < 2. tr M1 ≠ 0 from step 3.
   - **(Z3):** |tr M1(k) − tr M1(0)| ≤ 2‖M1(k) − M1(0)‖ < dist(tr M1(0), [−2, 2]), using your interval for
     tr M1(0) = −2cosh(κω).
   - **Report** r_a = the largest certified r, per spin.

**Controls (please include all three).**
- **Planted must-fail: spin 0.908,** where c2 ≈ −7e−6. The certificate must return a tiny r or fail there, never a
  large one.
- **Consistency with the engine:** at k = r_a, the certified bound on |F − c2k²| must be at least the floating value
  |F(r_a) − c2r_a²|. The engine gives F at any k; see `scripts/_nve_c2_engine_check.py` for how to call `LauA`. A bound
  smaller than the true remainder means a bug.
- **Sensitivity:** report which factor limits r_a (C_E, Q_R, R, ‖M1‖, or |c2|), and what r_a would be if that
  factor were 10× better. That decides whether a sharper bound is worth building.

**Better ideas are welcome:** a certified second-order Dyson term instead of the crude R₂ bound, the certified c3,
a different splitting of the lasso. Any route counts if it ends in a rigorous number and you state exactly what is
certified and what is only argued.

## 3. Part B (after Part A): a first validated build step for route (i), the whole k-range
Route (i) means interval-certified argument-principle counts over the complex k-rectangles of the claim:
- region A, |k| up to about 4 (circle picture);
- region B, near 30/7 (half-plane picture);
- at four spins.
This is the large problem. Part B is the FIRST step only, and no long runs.
1. **Design** a validated monodromy evaluator for the circle picture, with k as a small complex ball:
   - **Engine:** Arb through python-flint is on the box (quantum's venv), or mpmath.iv.
   - **Stepper:** a Taylor stepper with ball coefficients and a rigorous tail. For v″ + qv = 0 with |q| ≤ Q on a disc
     of radius ρ, a Cauchy majorant works.
   - **c0:** its Laurent series needs a rigorous tail from the majorant of √B/(u² + 1)³.
   - **k-subdivision:** subdivide until the enclosures of F, tr M0, tr M1 and tr M1 − s along each boundary segment
     exclude 0, and the argument varies by less than π/2.
2. **Build it** and run it on ONE short boundary segment at spin 3/5 (for example k ∈ [1, 1.1] on the real axis):
   - measure the time per segment and the enclosure widths;
   - compare with the stored floating values in `data/nve/gapb.jsonl`; the floats must lie inside the enclosures.
3. **Write the plan for the full run:**
   - the number of segments per region and spin, and the time per spin on one core;
   - a per-segment checkpoint (jsonl), so that any run resumes;
   - where F is small on the boundary: near k = 0, which Part A covers; near spin 4/5's k\* ≈ 4.0082 in region B,
     where tr Γ = 0 and the circle pair is needed; and at spin 9/10's third zero;
   - every remaining limit, listed beside the time estimate (the fleet rule).
   The full runs are NOT launched in this round. The office session registers and launches them after review.

## 4. Deliverables (branch only, as before)
- **Branch** `fable/<date>-eps` from current main (it includes Lemma K, claim v3 and this brief).
- **`data/nve/EPS_EFFECTIVE.md`.**
  - Part A: the derivation, what is certified and what is only argued, r_a per spin with every enclosure, and the
    three controls.
  - Part B: the design, the one-segment measurement, and the full-run plan.
- **`scripts/_nve_eps_certify.py`** (Part A) and `scripts/_nve_route1_proto.py` (Part B), with outputs in
  `data/nve/eps/`.
- **Commits** tagged `[model: Fable 5.2]` and marked UNVERIFIED. **Do not edit** the claim, ONLY_KERR, MRS_SECTION,
  RESULTS or the JOURNAL: the office session checks your work and integrates it.
- **A handover** `docs/HANDOVER_FABLE_<date>.md`: what was done, what wasn't, and the runs made.

## 5. House rules
- **Small runs only:** 1 core, nice 12. Declare a peak, and keep it well under 1 GB.
- **NO job-ending caps** (Sumit's standing rule): no `timeout`, alarm() or step caps that end a run.
  - On memory or disk pressure: pause your own processes, report, and resume on recovery.
  - Correctness gates may stop a run only at a checkpoint.
  - Checkpoint anything that runs longer than about 10 minutes (a jsonl per box or segment).
- **Literature:** quote at source, or mark it "from memory".
- **If Part A's bound comes out useless** (r_a absurdly small, or no r at all), that is a result. Report the dominant
  factor and the cheapest fix, then go on to Part B.
- **If the window runs short,** finish Part A cleanly (certificate, controls and write-up) before starting Part B. A
  half-built Part B is fine if the handover says exactly where it stopped.
