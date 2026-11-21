# Grading of Neon T38 (referee-style read of the Only Kerr proof), 2026-11-21

For the Bridge. Inputs: `neon_work/onlykerr/T38_summary.md` (relayed, unverified) and the proof's current structure as
given in `TheBridge/digests/ONLY_KERR.md` §3, §12, §13. The V26 blinding was lifted at unblinding. The full proof text
(Lemmas P and X, the VE3 derivation) was **not** read; where a grade depends on it, the grade says so. The only new
computation is the symbolic check of point 1 below (roots of B, the k = 30/7 form, and the J coefficient); its outputs
are quoted inline.

Grades:
- **VALID:** the objection is right and needs a change.
- **ALREADY-HANDLED:** covered by a registered result or by existing text.
- **REAL GAP:** a mathematical hole that needs new work.

## 1. Step (6), the branched-twist family. B(w,k) = (90 − 21k)w² − (60 − 18k)w + (10 − k), with w = u², u = z/a

**1a. k = 0 is Kerr. VALID; a wording slip; ALREADY-HANDLED in the registered result.** §159 / gap B says "irreducible
and non-imprimitive at every k ≠ 0 in R", because F has its known double zero at k = 0. The digest's "K*(0.6) = ∅ on
[−10.5, 4.05]" must read "on [−10.5, 4.05] ∖ {0}", or define K*(a) ⊂ (−∞, 30/7) ∖ {0}. No computation needed.

**1b. k = 4. ALREADY-HANDLED.**
- B(u², 4) = 6(u² + 1)² (checked), so c0″ is rational and the √B branch points merge with ±ia, f0's poles.
- That merger is at Re z = 0 < a. It happens inside the inner set, so the half-plane separation (Re z > a, T14 /
  V26-J) does not see it.
- At k = 4 the ray-formula radicand is 6(1 + x²/u²)², which vanishes only on Re u = 0. So c0 is analytic in k at k = 4
  on Re u > 1.
- Measured directly:
  - §159 k = 4 and k = 3.9: NON-VA, all gates pass;
  - gap B's region contains k = 4, with every guard passing (ρ_c = a there).
- No computation needed.

**1c. k < 0 (real branch points). VALID, with a consequence the referee did not draw: k < 0 is not a physical member
of the family once regularity on both outer axes is assumed.**
- For k < 0, B has two positive roots in w (checked: k = −1/10, −1, −10). So (c0″)² < 0 for |z| between a√w₁ and
  a√w₂. Examples: (0.27, 0.43) at k = −1 and (0.18, 0.50) at k = −10, spin 0.6.
- The physical lower outer axis is z < 1 − √(1 − a²) = 0.2 (spin 0.6, M = 1). It contains the negative-z copy of that
  interval for every k < 0, since every w > 0 is u² for some negative u.
- So c0 is complex on part of the lower outer axis. The lower-axis Ernst data (1/e₊) are then not real, and the metric
  is not a real regular spacetime there.
- **The family is therefore 0 ≤ k ≤ 30/7 under the both-axes hypothesis**, with k = 0 being Kerr.
- **Correction to my own earlier review** (`T11_LOOP_REVIEW.md`, "for k < 0 the negative-B interval lies inside the
  horizon"): it lies in |z| < a, which is NOT inside the horizon segment on the lower side. I checked only the upper
  axis.
- This shrinks what must be covered. The k < 0 results (gap B's [−10.5, 0)) become statements about complex metrics:
  harmless, but they should be labelled so.

**1d. k = 30/7. VALID and a REAL GAP. My earlier review accepted "k = 30/7 gives a NUT charge", and that was wrong.**
- B(w, 30/7) = (40/7)(3w + 1) > 0 (checked).
- (c0″)² ~ u⁻⁸ times the u⁴ coefficient of B, which is 90 − 21k. So the 1/z² (angular-momentum) term of c0 is
  proportional to √(90 − 21k) and vanishes at k = 30/7. There c0 ~ u⁻³: a real, asymptotically flat, **J = 0**
  profile with no NUT term. It is a genuine member of the family and is not covered.
- **A second, related gap: exceptional k can accumulate at 30/7.**
  - k ↦ c0 is not analytic at 30/7. The ray formula's √(c4 + c2x²/u² + …), with c4 = 90 − 21k, produces c4^{3/2} and
    c4² log c4 terms.
  - So "K*(a) is discrete in (0, 30/7)" allows infinitely many exceptions accumulating at 30/7.
  - It is closed if F(30/7) ≠ 0 and F is continuous at 30/7 from below. Continuity holds in the half-plane
    formulation, because c0 converges uniformly on compact subsets of Re z > a and ∞ stays ordinary.
- **Needs computation:** a direct lower-axis NVE test at k = 30/7.
  - The §159 code refuses it (the radicand's leading power changes from w⁸ to w¹⁰). Two lines change; ρ_c = a there,
    so the registered circle loops work.
  - Report F(30/7), tr M0, tr M1, and the VA/non-VA class.
  - About 1 h with a short prereg.
- What it does not close: (4.05, 30/7) at spin 0.6 is still only "discrete exceptions, finitely many if F(30/7) ≠ 0".
  Gap B's count cannot reach it with M0 a circle, because ρ_c grows. A half-plane M0 would be needed, which is a
  bigger job (not proposed).

**1e. Only spin 0.6, bounded k; spin ≥ 1 not covered. VALID; ALREADY-HANDLED as caveats** (gap B's four caveat lines).
- Add: the family's black-hole meaning needs 0 < a < 1. For a ≥ 1 there is no horizon segment, and the lower-axis
  construction changes. State the theorem for a ∈ (0, 1).

## 2. Lemma X (needs the proof text; graded from the digest)
**2a. Abelian G3⁰ when G1 is finite. VALID as a wording requirement; probably ALREADY-HANDLED in structure.**
- Per the digest, Lemmas P and X are used in the rational two-centre case: two simple poles, deg f0 = 2.
- The single-centre case goes through the lower axis instead:
  - twisted data are obstructed at FIRST order (deg f0⁻ ≥ 4);
  - static double-pole data look two-centre from below, so Lemmas P and X are applied to two-simple-pole data there
    too.
- So every use should sit where G1⁰ = C*. That holds only if the first-order Liouvillian solutions √Δ·exp(±κu) have
  a nonconstant κω(E) at generic E. **The digest lists "writing out that κω_i(E) is non-constant" as an open small
  item: that is exactly this point.**
- Supporting evidence from our side:
  - Kerr data (k = 0) on the lower axis have tr M1 non-real, so G1 is infinite (§159);
  - the §158 numerics found all two-simple-pole cases solvable and non-finite.
- **Needs:** the written κω(E) argument. A small symbolic check is optional.

**2b. Confluence at E*. VALID as a rigour request; likely a paragraph, not a hole.**
- The residue at the fixed twist pole z1, as a function of E, is analytic on the E-plane minus a discrete set. It is
  generally multivalued around E*, since the turning point's circling swaps sheets at z1.
- Vanishing on I_E implies vanishing on every branch of its analytic continuation, by the identity theorem on the
  residue's Riemann surface. So no evaluation AT E* is needed: only the asymptotic expansion near E* along some
  continuation path, whose leading coefficient (the e^{c′ arsinh ξ} Taylor coefficient, V25 addendum B) must be
  nonzero.
- The text should say this, including that the residue (a single-valued object on Σ_E near z1) equals the Galois
  obstruction for E off E*.
- Not verified here: whether the written proof already does.

**2c. ZV δ = 2. ALREADY-HANDLED** (digest §12: "forces Kerr, Schwarzschild or static ZV δ = 2", with ZV excluded via
MPS 2013). Make step (5)'s wording match.

## 3. MRS punctures and the domain. VALID (write-up), no computation
- List the punctures of Γ_E, including f0 = 0. f0 enters VE3 through 1/f0, and its zeros are the rod endpoints.
- For the branched family, restrict Γ_E to the single-valued domain: the half-plane (or |z| > ρ_c). Then state that
  the off-axis metric is single-valued there, because its ρ² expansion is built from e(z) and its derivatives.
- §159 already works on that domain.

## 4. Reference subtraction and the ρ⁴ cancellation. ALREADY-HANDLED by check (V25 P1, two derivations, exact Kerr
to 1e−52). VALID that the text should carry the derivation, and should define the complexified Kerr–NUT through the
Ernst pair (e, ẽ). No new computation.

## 5. Integrability class. ALREADY-HANDLED in substance (digest §6). VALID that it should be in the abstract.
Contrast Kruglikov–Matveev (polynomial, arXiv:1111.4690) and Lukes-Gerakopoulos (arXiv:1206.0660).

## 6. Hypotheses. VALID (wording)
- State regularity on both outer axis segments. This is also what removes k < 0; see 1c.
- For e₋ = 1/e₊, cite the i⁰-analyticity basis (Beig–Simon; Fodor–Hoenselaers–Perjés) alongside Meinel–Neugebauer.
  The MN 1995 eq. (35) was read in the original.
- No equatorial symmetry is needed.

## 7. "Honestly open" list. Agree.
Null geodesics (μ = 0) make the test blind, so restrict to timelike geodesics explicitly.

## Summary
- **Real gaps:** 1d (k = 30/7, plus accumulation of exceptions at 30/7) and 2a (written κω(E) non-constancy).
- **Corrections from 1c:** the family is 0 ≤ k ≤ 30/7 under the both-axes hypothesis, and my T11 review was wrong on
  k < 0 and on k = 30/7.
- **Rest:** wording or already handled.
- **New computation worth doing:** one, the k = 30/7 lower-axis NVE test, about 1 h, registered.
