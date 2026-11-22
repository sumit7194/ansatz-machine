# Grading of Neon T51 (hostile referee read of the reference claim, eed501f), 2026-11-22

Source: `neon_work/onlykerr/T51_full.md`. It is relayed and UNVERIFIED until checked here. The Bridge's
pre-assessment was checked, not adopted. Grades: **WRONG** (the objection fails), **FAIR** (real, fixed in the text),
**RIGHT** (agreed, scope changed), **MOOT**.

| # | T51 objection | Bridge pre-assessment | our grade | where fixed |
|---|---|---|---|---|
| 1 | e₋ = 1/e₊ holds only under reflection symmetry (T51's "single strongest objection") | wrong | **WRONG**, and backwards | MRS §5a, b |
| 2 | 4D metric holomorphic near every loop; f₋ = 0 | fair | **FAIR**; f0 = 0 handled; Prop. 2 citations still open | MRS §5c, §4 |
| 3 | singular reduction at ρ = 0 | fair | **FAIR**, fixed in one paragraph | MRS §5b |
| 4 | "regular on both outer axes" false for k < 0 at a ≤ 0.8 | wrong | **WRONG** (convention); the convention was unstated, now stated | MRS §5 conventions, §5c |
| 5 | no k > 0 member is a regular BH; off-axis unchecked | right | **RIGHT**; scope changed. Part about the outer axes is wrong | MRS §5c, d; claim v2 |
| 6 | can't exclude zeros splitting into (0, ε) | – | **WRONG** (closed structurally: F = O(k²)) | MRS §5d |
| 7 | k = 4 collision | – | **FAIR question, no defect** | MRS §5e |
| 8 | Im tr is not holomorphic | moot | **MOOT** (we count tr M1 − s) | below |
| 9 | theorem-grade wording | adopt | **RIGHT**; claim v2, status-first | `CLAIM_FAMILY_II.md` v2 |
| 10 | prior art (Markakis 2014, Kruglikov–Matveev 2016, …) | check | see below (checked at source) | below |

## 1. e₋ = 1/e₊ "only under reflection symmetry": WRONG, and the logic runs the other way
- **What T51 says.** Kordas 1995 and Meinel–Neugebauer 1995 show e₋ = 1/e₊ holds under equatorial symmetry, which
  requires e₊(z)·conj e₊(−z) = 1. Our family breaks that condition, so the lower-axis NVE is "not the NVE of the
  spacetime".
- **Why it fails.** e₋ = 1/e₊ (equivalently ξ₋ = −ξ₊) holds for ANY asymptotically flat solution. It follows from
  the analyticity of the conformally rescaled potential ξ̃ = ξ/r̄ at spatial infinity (Beig–Simon 1981; FHP 1989).
  - On the axis, both outer segments end at the same point Λ, with z̄ = 1/z on both. So ξ̃ = F(1/z) for one analytic F.
  - Undoing the conformal factor, r̄ = 1/|z|, gives ξ₊ = F(1/z)/z and ξ₋ = F(1/z)/(−z), so ξ₋ = −ξ₊.
  - Full derivation, with the conformal-factor step and the continuation along the lower segment: `MRS_SECTION.md`
    §5a.
- **Exact checks** (`scripts/_nve_t51_axis_check.py` → `t51_axis_check.out`):
  - **Kerr, from the closed form** 1 − 2M/(r − ia cos θ): e₋·e₊ − 1 = 0 identically.
  - **Two Curzon particles of unequal mass,** a static vacuum solution with NO plane of reflection symmetry (checked:
    the only candidate plane, z0 = 3/4, fails at order t⁻⁴): ψ₋ + ψ₊ = 0 identically, so e₋ = 1/e₊ exactly. This is a
    direct counterexample to "only under reflection symmetry".
- **Where the reflection condition really comes from.** Reflection symmetry on the axis says
  e₋(−z_c) = conj e₊(z_c). Combine it with the general e₋ = 1/e₊ and you get e₊(z_c)·conj e₊(−z_c) = 1. So our identity
  is an INPUT to the Kordas–Meinel–Neugebauer condition, not a consequence of it.
- **The condition also depends on the origin.** In the claim's shifted z, even Kerr gives
  e₊(z)·conj e₊(−z) − 1 = −4/(z − ia)² ≠ 0. That illustrates the unstated-convention problem (point 4).
- **Robustness, independent of all this** (MRS §5b). Morales–Ramis is local near Γ. The NVE we integrate is the NVE of
  the vacuum metric near the lower axis with data 1/e₊, which exists by Prop. 2 applied there. The identity only adds
  that this is the same spacetime as the one with upper data e₊.
- **Source check:** Meinel–Neugebauer 1995 derive f⁽ˡ⁾ = 1/f⁽ᵘ⁾ (their Eq. 35) in §III, BEFORE assuming
  reflection symmetry, and get the reflection condition in §IV by combining the two. Ernst–Manko–Ruiz 2006
  (Eqs. 56–58) use the same continuation. See "Literature".
- **Partly right:** family (ii) with k ≠ 0 is probably not reflection-symmetric. The proof never uses reflection
  symmetry, and the claim never states it.

## 2. Holomorphy of the 4D metric near the loops: FAIR; the f0 = 0 part is closed, Prop. 2 stays open
- **f₋ = 0 is exactly f0 = 0,** the two rod endpoints, because f0⁻ = f0/(f0² + c0²). Proposition 2 is stated on
  W = U_a ∖ {f0 = 0, f0² + c0² = 0}.
- **NVE1 is holomorphic at f0 = 0** (P = E²). Since π₁(X ∖ pts) → π₁(X) is onto, the NVE1 monodromy group over W is
  the same group. Every generator is realised by a loop in W, and nothing is continued across f₋ = 0 (MRS §5c).
- **Prop. 2 is needed only at REAL k on those loops.** The k-counts use only the axis data.
- **Still open, as before:** Prop. 2 is an argument. Its citations (Baouendi–Goulaouic; Hauser–Ernst; Sibgatullin)
  are not yet checked. That is the one soft link in the applicability chain, and claim v2 says so up front.

## 3. Singular reduction at ρ = 0: FAIR, fixed
- Work in x = ρ cos φ, y = ρ sin φ on the full T*M; these are regular because the outer axes are elementarily flat.
- Rotation invariance makes the transverse Hessian ∝ the identity. So the (x, y) block of the VE is two identical
  copies of NVE1, with group {diag(g, g)}.
- Its identity component is non-abelian iff G1⁰ is, and that passes to the full VE through a subquotient (MRS §5b).
- T51 suggested exactly this fix, and it changes no number.

## 4. "Regular on both outer axes is false for k < 0 at a ≤ 0.8": WRONG (a convention mix-up), but the convention was unstated
- **T51 places the k < 0 roots z = ±a√w in the CENTRED Weyl coordinate,** where the rod is [−σ, σ]. Its threshold
  a < √3/2 is exactly the test "a/√3 < σ".
- **The family is defined in z = z_Weyl + M.** There the negative roots z = −a√w are < 0 < 1 − σ, so they lie on the
  lower outer axis at EVERY spin, and c0″ is imaginary between them.
  - Example: k = −1, a = 0.6 gives roots at z = −0.265 and −0.427 (`T38_GRADING.md` 1c).
  - T51's parenthetical tried the shifted coordinate, but checked only the positive roots against the upper rod end.
- **The range 0 ≤ k ≤ 30/7 is exact** (MRS §5c): B > 0 on w ≥ 0 for 0 ≤ k ≤ 30/7, B fails on the lower axis for
  k < 0, and B fails on both axes for k > 30/7.
- **Fixed:** the conventions (z shifted, M = 1, μ = 1, the c0 normalisation and branch) are now stated in claim v2 and
  MRS §5. T51's "missing normalisations" MINOR is fully adopted.

## 5. No k > 0 member is a regular black hole; off-axis unchecked: RIGHT, scope changed
- **Agreed:** by uniqueness (Chruściel–Costa), the k ≠ 0 members are not regular black holes.
  - Claim v2 calls them "stationary axisymmetric vacuum fields", not black holes.
  - It states that nothing off the axis is checked: horizons, rod, naked singularities, CTCs.
- **Does the record check anything off the axis? No.** Everything is axis data plus the near-axis expansion.
- **One sub-claim of T51 is wrong:** "prescribing (c0″)² does not guarantee elementary flatness on both outer axes."
  For asymptotically flat data it does (MRS §5c):
  - γ is constant on each regular axis segment and → 0 at infinity.
  - ω's jump across infinity is the NUT charge, which is zero because c0 = O(u⁻²).
  - Struts can sit only on inner segments.

## 6. Zeros splitting off k = 0 into (0, ε): WRONG; closed structurally
- **At k = 0 the circle encloses no NVE1 singular point,** so M0(0) = I. The reasons: Kerr data are rational,
  f0⁻ is regular at ±ia, B(w, 0) = 10(3w − 1)² is a perfect square, and r±, p± lie outside.
- **Hence F = tr[M1, M0] − 2 = O(k²),** and likewise tr M0 − 2 = O(k²) from det M0 = 1. The order at 0 is ≥ 2.
- **The region counts total 2,** or 3 at spin 0.9 with the extra located and non-real. So the order at 0 is exactly 2
  and there is no real zero in (0, ε). (MRS §5d.)
- **What T51 missed:** the argument principle counts total multiplicity. Once the order at 0 is known structurally,
  the count does separate "all at 0" from "split off".
- **The control in the record matches:** C1 gives (2, 2) for (F, tr M0 − 2) on |k| < 0.3 at every spin.

## 7. k = 4: FAIR question, no defect
- B(w, 4) = 6(w + 1)², so the roots meet ±i. That happens inside the circle picture's disc, where the circle data
  stay analytic in k (leading coefficient ∝ 90 − 21k ≠ 0). In the half-plane picture it is far left of every loop,
  and the window guards checked this at every sample.
- k = 4 is covered twice: gap B (0, 4.05] and the window [3.95, …].
- The spin-0.8 degeneracy at 4.0082 is a zero of tr Γ. Its nearness to 4 is noted; no mechanism ties them, and it is
  settled independently (MRS §5e).
- **T51's general point stands, and claim v2 states it:** guards between grid samples are floating-point checks,
  not proofs.

## 8. "Im tr is not holomorphic": MOOT
- The finite-group exclusion counts the holomorphic functions tr M1 − s, for all 11 finite-subgroup traces s ∈ S
  (`WINDOW_PREREGISTRATION.md`; gap-B post-hoc `gapb_finite.out`; the spin chain).
- Im tr ≠ 0 was recorded only as evidence, never counted.
- T51's second half (post-hoc classifications are floating point) is true and was already disclosed. Claim v2 puts it
  in the status block.

## 9. Theorem-grade wording: RIGHT; claim v2 written
`CLAIM_FAMILY_II.md` VERSION 2 (2026-11-22):
- the status comes first ("numerical result, not a theorem");
- one sentence, with "Numerically (…)" leading;
- an evidence table with a grade per piece;
- a scope list, adding null geodesics and "not black holes / off-axis unchecked";
- a_c moved out of the main sentence.
v1 is kept below it, marked superseded. No number changed.

## 10. Prior art
- **All five sources check out.** T51 grades its own prior-art section FINE (novelty not undercut), and that stands.
- **Two corrections to how T51 uses them:**
  - **Markakis's conjecture assumes equatorial symmetry,** so our family sits just outside its stated class.
  - **Kruglikov–Matveev is about generic metrics,** not the stationary axisymmetric vacuum class.
- **Cite all of them, with those caveats.** Details are in "Literature" below.

## Literature (checked at source 2026-11-22 by a web agent; the MN and EMR passages re-read here)
PDFs and text extractions are in the session scratchpad `lit/`.
**On point 1, the sources say the opposite of what T51 attributes to them:**
- **Meinel & Neugebauer, CQG 12 (1995) 2045 = arXiv gr-qc/0302114: VERIFIED AT SOURCE (full text; Eq. 35 re-read
  here).**
  - §III, using only asymptotic flatness and regular axis pieces, derives f⁽ˡ⁾(ζ) = F(ζ)/(1 + G(ζ)) and
    f⁽ᵘ⁾(ζ) = (1 + G(ζ))/F(ζ), where one pair F(K), G(K) is fixed by the upper-axis data.
  - **So f⁽ˡ⁾ = 1/f⁽ᵘ⁾, continued.** That is our e₋ = 1/e₊, derived BEFORE any symmetry is assumed.
  - Reflection symmetry first enters in §IV, as f⁽ˡ⁾(−ζ) = conj f⁽ᵘ⁾(ζ) (Eq. 38). Combined with Eq. 35 it gives
    Eqs. 39–40, which are equivalent to e₊(ζ)·conj e₊(−ζ) = 1.
  - This is exactly the decomposition in MRS §5a.
- **Ernst, Manko & Ruiz, CQG 23 (2006) 4945 = arXiv gr-qc/0701112** (three authors; T51 wrote "Manko & Ruiz"):
  **VERIFIED AT SOURCE, Eqs. 45–59 re-read here.**
  - They define ξ̃ = √(z² + ρ²)·ξ with z̄ = z/(z² + ρ²), and continue e₊ through z̄ → −z̄ using analyticity of ξ̃ at
    z̄ = 0, crediting "the method of reasoning developed by Kordas".
  - Continuing their Eq. 56 gives e₊(−z) = (1 + z̄ξ̃(−z̄))/(1 − z̄ξ̃(−z̄)), the first equality of Eq. 58, which uses no
    symmetry. The actual axis value is E(−z, 0) = (1 − z̄ξ̃(−z̄))/(1 + z̄ξ̃(−z̄)). **So E(−z, 0) = 1/e₊(−z):** our
    conformal-factor step, in their notation.
  - Their warning that the continued data "are not in general … equal to the axis values" at negative z is this
    reciprocal relation.
- **Kordas, CQG 12 (1995) 2037: ABSTRACT ONLY** (the full text was blocked). The theorem is "AF solution is
  reflection-symmetric iff e₊(z)·e₊*(−z) = 1". The abstract says nothing about the lower axis. EMR describe his method
  as the analyticity of ξ̃ at infinity (SECONDHAND).
- **Pachón & Sanabria-Gómez, CQG 23 (2006) 3251 = gr-qc/0603081: VERIFIED.** They state the condition and credit
  Kordas and MN, and use the same ξ̃ = Ω^{−1/2}ξ set-up. Nothing on the lower axis.
- **FHP 1989: ABSTRACT ONLY.** That they state analyticity of ξ̃ at the origin is NOT confirmed. The compactified-Weyl
  set-up is confirmed SECONDHAND (Sotiriou–Apostolatos gr-qc/0407064) and directly in EMR and Pachón–Sanabria-Gómez.
- **Beig–Simon 1981: ABSTRACT ONLY.** "Analytic in a neighbourhood of spatial infinity". Cite it for that, not for the
  exact phrasing about rescaled potentials.
- **Net for point 1:** T51 cited the right papers for the wrong statement. **Cite MN 1995 Eq. 35 and EMR 2006
  Eqs. 56–58 for e₋ = 1/e₊.**

**Point 10, prior art:**
- **Markakis, MNRAS 441 (2014) 2974 = arXiv:1202.5228: VERIFIED.**
  - Newtonian, stationary, axisymmetric AND equatorially symmetric potentials.
  - A quadratic constant forces the Euler two-centre family, with Kerr-like moments M₂ₗ₊₂ = a²M₂ₗ.
  - No independent quartic invariant exists, within an ansatz where the rank-4 tensor is itself Z₂-symmetric.
  - Conjecture: a stationary axisymmetric equatorially symmetric vacuum spacetime is integrable iff it is Kerr (or
    Kerr–de Sitter).
  - **Relevance:** that conjecture is restricted to EQUATORIALLY SYMMETRIC spacetimes. Family (ii) with k ≠ 0 is
    probably not reflection-symmetric, so our result sits just outside the conjecture's stated class rather than
    inside it. Cite it as motivation, and say so.
- **Kruglikov & Matveev, Nonlinearity 29 (2016) 1755 = arXiv:1510.01493 (T51 gave no number; not 1410.0791):
  VERIFIED.**
  - Any signature, dimension ≥ 2. For each degree, an open set of metrics near any Cᵏ metric has no nontrivial
    polynomial integral of that degree.
  - Generic (residual in Cᵏ) metrics have only trivial polynomial integrals, and also only trivial integrals analytic
    in the momenta.
  - **Says nothing about the non-generic stationary axisymmetric vacuum class,** which already carries Killing
    vectors. Cite it as context only.
- **Vollmer, J. Geom. Phys. 115 (2017) 28 = arXiv:1602.08968: VERIFIED.** No additional Killing tensors, up to
  valence 7 (Tomimatsu–Sato δ = 2), 9 (C-metric) and 11 (Zipoy–Voorhees δ = 2), each at ONE parameter choice.
  **Vollmer, PRD 92 (2015) 084036 = arXiv:1506.06926: VERIFIED** (valence 3 in the Weyl static class).
  (Already known to this repo; see CLAUDE.md, D39.)
- **Lu & Wu, arXiv:2603.12674 (2026): ABSTRACT ONLY.** Spacetimes where null geodesics are integrable while timelike
  ones are not: conformally rescaled Kerr, Kerr–Bertotti–Robinson, accelerating Schwarzschild. None is a
  multipole-deformed Kerr. It supports adding "null geodesics untested" to the scope (done in v2); it is not evidence
  about our family.
- **T51's own grade, "novelty not undercut", stands** on these five. Maciejewski–Przybylska–Stachowiak 2013 remains
  the closest methodological precedent (static, closed form).

## Net
- **Of T51's two SERIOUS logic objections:**
  - The first, e₋ = 1/e₊, is wrong. There is a derivation, two exact checks, and a direct counterexample to "only
    under reflection symmetry".
  - The second, the metric near the loops, reduces to Prop. 2's pending citations, which were already on our list.
    The f0 = 0 handling is now explicit.
- **Physics:** point 4 is a convention mix-up, now prevented by stated conventions. Point 5 is right and the scope
  changed.
- **Numerics:** point 6 is closed structurally, point 7 is no defect, point 8 is moot. The floating-point status was
  correct and is now stated first.
- **Wording:** v2 adopted.
