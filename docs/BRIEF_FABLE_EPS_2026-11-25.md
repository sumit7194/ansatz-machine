# Brief for the Fable side-session (ansatz-machine-personal): an EFFECTIVE ε for Statement A (2026-11-25)

**From:** ansatz-machine (office), via the Bridge, for Sumit.
**Builds on:** your own C2_ANALYTIC.md (now on main as 66873a2 and 29d2555, verified in c3766aa).

## 0. Where things stand (all on main; read these first)
- **`data/nve/CLAIM_FAMILY_II.md` v3, "Statement A".** For each spin a ∈ {3/10, 3/5, 4/5, 9/10} at E = 4/5 there is
  ε_a > 0 such that, for every k ∈ (0, ε_a), the monodromy group of the lower-axis ρ-equation is Zariski-dense.
  **ε_a is NOT quantified.** This round is to quantify it.
- **`data/nve/C2_ANALYTIC.md`**, your note: the formula c2 = sinh²(κω)I₊I₋/κ², and §6b, the certificate that I₊, I₋
  and Re κω are nonzero (`scripts/_nve_c2_certify.py`, mpmath.iv).
- **`data/nve/C2_OFFICE_CHECK.md`**, the verification. The engine agrees with your formula to 12 digits at 7 spins.
  The trapezoid bound was checked at source: Trefethen–Weideman 2014, Thm 3.2 p. 396 and Thm 2.2 p. 392.
- **`data/nve/MRS_SECTION.md` §5d, Lemma K.**
  - Setting: S = C ∪ L ∪ [R0, ∞), with C the circle |z| = R0 and L the capsule lasso based at R0.
  - Hypotheses: (H1) |z| ≥ ρ > a/√3 on S; (H2) r± and p± are off C ∪ L; (H3) a < R0 < min|r±, p±|.
  - Key fact: c0″(z; k) = c_K″(z)·√(1 − kφ(w)), with φ(w) = (21w² − 18w + 1)/(10(3w − 1)²) and w = z²/a².
  - Conclusion: M0(k) and M1(k) are holomorphic for |k| < δ, M0(0) = I, and F(k) = tr[M1, M0] − 2 = c2k² + O(k³).
  - **δ is not quantified.**
- **The loops.** These are the spin-scan region-A loops. The circle radii R0 are 1.1492, 1.35, 1.3382 and 1.2639 (spins
  3/10, 3/5, 4/5, 9/10). The lasso is `KC.capsule_lasso(r+, p+, others, b=R0)`. The Kerr points r± are the roots of N,
  and p± = 2 ± ia. See `scripts/_nve_spin_scan.py` (`kerr_points`, `LauA`) and `scripts/_nve_lower_kc.py`.
  - All loops stay at least 0.744 from the pinch interval |z| ≤ a/√3. Every circle-picture path has |z| ≥ R0 − 0.05.
- **Engine values at k = 0** (`data/nve/c2_engine_check.out`):
  - tr M1(0) is NON-REAL at all four spins, with Im between 1.46 and 3.82.
  - c2 at each spin: 0.0279 + 0.0460i, 0.1935 + 0.0985i, 0.1621 + 0.0149i, 0.0158 − 0.0016i.
  - c3 (floating, for orientation only): 0.0013 + 0.0075i, 0.0306 + 0.0271i, 0.0301 + 0.0195i, −0.0062 + 0.0412i.

## 1. The goal: a certified, explicit ε_a per spin
Find r_a > 0, as a rigorous interval-arithmetic statement, such that for every real k ∈ (0, r_a] the pair ⟨M1, M0⟩
satisfies:
- **(Z1)** F(k) ≠ 0, i.e. irreducible;
- **(Z2)** tr M0(k) ≠ 0 and tr M1(k) ≠ 0, i.e. not imprimitive;
- **(Z3)** tr M1(k) ∉ [−2, 2], so M1(k) is loxodromic, of infinite order, hence not finite.
Then Statement A holds with ε_a = r_a, a number. (Z3) is the cheap one: tr M1(0) is non-real with margin ≥ 1.46.

## 2. A suggested route (yours to improve). Everything is explicit; no validated ODE integration of the k ≠ 0 system
1. **Quantified holomorphy domain (Lemma K with numbers).** Find R_k > 0 such that, on |k| ≤ R_k and on the whole path
   set S′ = C ∪ L, rigorously:
   - |kφ(w)| ≤ ½ (this needs sup_S |φ|, including the ray [R0, ∞), where φ → 7/30);
   - f0² + c0² ≠ 0 and P ≠ 0;
   - with explicit lower bounds on both.
   c0 and c0′ on S′ come from your integral from +∞, now with k complex: the integrand c_K″·√(1 − kφ) is O(s⁻⁴), so
   the tail is explicit. Interval boxes in (z, k) do the rest.
2. **A Gronwall bound for the monodromies at |k| ≤ R_k.** Use Kerr's basis Φ = [[v₊, v₋], [v₊′, v₋′]],
   v± = (ND)^{1/4}e^{±κU}, W = −2κ.
   - Write Y = ΦC. Then C′ = B(z; k)C, with B = Φ⁻¹ΔA Φ and ΔA = [[0, 0], [−(q(k) − q(0)), 0]].
   - So M(k) = M(0)·T(k) with ‖T(k)‖ ≤ exp(∫_γ ‖B‖|dz|), and ‖T(k) − I‖ ≤ exp(∫‖B‖) − 1.
   - ‖B‖ ≤ ‖Φ⁻¹‖‖Φ‖·|q(z; k) − q(z; 0)|. Enclose that on boxes of the path, and of the k-disc.
   - **Watch:** Φ is large near r₊ and p₊ on the capsule (distance δ_caps ≤ 0.15). Keep the capsule radius; do not
     shrink it.
3. **Cauchy remainder in k.** F is holomorphic on |k| < R_k. With M_F := sup_{|k| = R_k} |F(k)|, bounded from step 2
   (|tr[M1, M0]| ≤ 2‖M1‖²‖M0‖² for SL₂):
       |F(k) − c2k²| ≤ M_F (|k|/R_k)³ / (1 − |k|/R_k).
   So (Z1) holds for 0 < |k| ≤ r whenever |c2| r² > M_F (r/R_k)³/(1 − r/R_k). c2 is already certified nonzero; take
   its interval from your certificate, or certify |c2| directly.
4. **(Z2) and (Z3)** from the same bounds:
   - |tr M1(k) − tr M1(0)| ≤ 2‖M1(0)‖·(e^{∫‖B₁‖} − 1). This needs to be < dist(tr M1(0), [−2, 2]), using the
     interval for tr M1(0) = −2cosh(κω) from your certificate.
   - tr M0(k) = 2 + O(k²); bound it the same way. tr M0 ≠ 0 is trivial for small k.
5. **Report r_a per spin.** Report it whether it is small or not, with every enclosure. Optimise the choice of R_k
   (the bound is r ~ R_k·|c2|R_k²/M_F, roughly). Also report what r_a would be with a sharper M_F, so we know whether
   a better bound is worth having.

**Better ideas are welcome.** For example: bound F directly on a k-circle through a certified Dyson expansion to second
order, plus a remainder; or use the c3 term. Any route counts if it ends in a rigorous number and you state exactly
what is certified.

## 3. Deliverables (branch only, as before)
- **Branch** `fable/2026-11-25-eps` from current main (8 commits ahead of your last branch; includes Lemma K and
  claim v3).
- **`data/nve/EPS_EFFECTIVE.md`.** The derivation; what is certified and what is only argued; r_a per spin with its
  enclosures; a planted must-fail. A good one: claim r_a at spin 0.908, where c2 ≈ −7e−6. The certificate must
  return a tiny r_a or fail there, not a large one.
- **`scripts/_nve_eps_certify.py`** (mpmath.iv), with outputs in `data/nve/eps/`.
- **Commits** tagged `[model: Fable 5.2]` and marked UNVERIFIED. **Do not edit** the claim, ONLY_KERR, MRS_SECTION,
  RESULTS or the JOURNAL: the office session checks your work and integrates it, as last time.
- **A handover** `docs/HANDOVER_FABLE_<date>.md`: what was done, what wasn't, and the runs made.

## 4. House rules for this round
- **Small runs only:** 1 core, nice 12, minutes. Declare a peak, and keep it well under 1 GB.
- **NO job-ending caps** (Sumit's standing rule since today): no `timeout`, no alarm, no step caps that end a run. On
  memory or disk pressure, pause and report. Correctness gates may stop a run only at a checkpoint. If any single
  computation would take over ~10 minutes, checkpoint it (a jsonl per box or segment).
- **Literature:** quote at source or say "from memory" (as you did for Trefethen–Weideman).
- **If the bound comes out useless** (r_a absurdly small, or no r at all), that is a result. Report why: which factor
  dominates, ‖Φ‖ near the capsule or M_F. Then propose the cheapest fix, e.g. a shorter lasso or a certified
  second-order Dyson term.

## 5. If time remains (stretch; design only, no long runs)
Size route (i): an interval-certified argument principle over the whole k-range (0, 30/7]. Give:
- the stepper (Arb/python-flint, or mpmath.iv);
- the per-segment checkpoint plan;
- an honest time estimate per spin on one core, with any remaining limits listed beside it (fleet rule);
- where F is small on the boundary (near k = 0, which this round's r_a handles; and near the spin-4/5 point
  k* ≈ 4.0082) and how to handle it.
