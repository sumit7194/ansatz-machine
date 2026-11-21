# Check of Neon T48 (sliver δ0, interval) and T49 (MRS applicability draft), 2026-11-21

Both are relayed by the Bridge and UNVERIFIED. They were read from `neon_work/onlykerr/T48_full.md` and
`T49_MRS_section_draft.md`. T48's script, `sliver_closure_iv.py`, was **not yet available**, so the T48 grade is a
reading of the method, not of the code.

## T49, the MRS applicability draft: SOUND where it is checkable. A few labels to soften and one scope note.
**Independent numerical agreement with our code:**
- **Lower-axis poles u_D± (zeros of f0² + c0²):** k = 1: 3.27889 ± 0.90574i, i.e. z = 1.967 ± 0.543i (ours, from
  `kc_geometry.out`). k = 2: z = 1.930 ± 0.472i (ours). k = 30/7: z = 1.80332022637 ± 0.0534116583167i, ours
  (§161/§162) to every printed digit.
- **Physical lower-axis turning point at E = 0.9:** our Newton on G1 gives u = −14.150188915044283… (k = 1) and
  −14.139807205785085… (k = 30/7). T49 agrees to 2.5e−44 and 2.3e−44.
- **Further agreements:**
  - Zeros of f0 at u = 1/3 and 3 (z = 0.2 and 1.8, the rod endpoints).
  - The B roots at k = 1: ±0.5768 ± 0.1685i (checked by hand).
  - The modulus rule |u| = ((10 − k)/(90 − 21k))^{1/4} < 1 for 0 < k < 4.
  - The endpoint form B = (40/7)(3w + 1) with c0″ = O(u⁻⁵) (our w¹⁰ leading power).
  - c0 has log branch points at ±i for k > 0, matching our earlier reading of δc0.
- **U_a matches our working domains.** It is P¹ minus a tree through u = 1, joining every branch point, ±i included.
  Our |z| > ρ_c circle picture and our half-plane picture both lie inside it. T49's loop-return control (closed loops
  inside U_a return to 1e−55; a loop around +i alone fails) is consistent with our design.

**Notes for the write-up:**
1. **Scope of the "caveat for the proof's owner"** (loops around ±i alone leave U_a). This concerns only an
   upper-axis VE3 test of family (ii), which the proof does not use: family (ii) is obstructed at first order on the
   lower axis. For the rational-twist class, c0 is rational and has no logs, so the caveat does not apply there either.
   Say that, so a reader doesn't think a used step is affected.
2. **Proposition 2** (off-axis metric single-valued on a tubular neighbourhood of W = U_a ∖ {f0 = 0, D₊ = 0}) is
   plausible and correctly excludes the zeros of f0. It rests on the Baouendi–Goulaouic / Hauser–Ernst reconstruction:
   cite precisely, and don't label it [SURE] without that check. The zero-period argument for dω and dγ (the pullback to
   ρ = 0 vanishes, and the tube retracts onto W) is fine.
3. **§4 ("both segments are needed")** is an argument, not a proof. Label it as such. It is also what removes k < 0 in
   our T38 grading 1c: c0 is complex on the lower outer axis there.
4. **Over-strong labels.** The [SURE] tags on "unique zeros of e₊, ẽ₊ in |u| > 1.1" rest on three k values at one
   spin. Say "checked at k ∈ {1, 2, 30/7}, a = 0.6".
5. **Citations to verify at source before use:** Morales-Ruiz–Ramis–Simó 2007 (Ann. Sci. ÉNS 40, 845); Casale 2009
   (Ann. Inst. Fourier 59, 2593); Beig–Simon (Proc. R. Soc. A 376 (1981) 333).

## T48, the interval δ0 for the sliver (30/7 − 10⁻¹², 30/7): promising, with ONE LOGICAL GAP and one weak control.
**What checks out:**
- **Geometry matches ours exactly.** Its loop centres u_p ≈ 3.005534 + 0.089019i and u_tp ≈ 3.001368 (E = 0.8) are our
  p+/a and r+/a at the endpoint.
- **The O(L) bound** comes from the exact rationalisation c0″(k) − c0″(30/7) ∝ L·P1/(√(B0 + LP1) + √B0), with
  Re√B0 > 0 on the half-strip. That is a clean way to dodge the non-analytic terms. The bound's integration path (a
  horizontal ray to ∞ inside U_a) is legitimate, by T49's Proposition 1 (path independence).
- **Low precision is not by itself a problem.** iv.dps = 16 is fine for interval arithmetic: outward rounding stays
  rigorous and only widens the enclosures. The endpoint commutator enclosure [0.0036, 0.0099] is wide but excludes 0.

**The gap: "C_VE1 ≠ 0 ⇒ G1⁰ non-abelian" does not follow as stated.**
- α = γ2γ1 and β = γ3γ2 are only asserted to be "identity-component loops".
- In an imprimitive (D∞-type) group, which is VA, commutators of group elements need not be trivial.
- In ξ1/v variables each γ_j has trace 0 and order 4, exactly like the antidiagonal elements of such a group. So
  α, β ∈ G1⁰ needs an argument. For Kerr's two-pole data it holds, because single-point loops are antidiagonal and
  products of two are diagonal. For the twisted endpoint it is what has to be proved.
- **Fix:** certify an open set of conditions that implies Zariski density, with the same Gronwall machinery: the
  commutator ≠ I, PLUS two of tr A, tr B, tr AB ≠ 0, PLUS one trace non-real or outside S. That is what our §161 / §162
  classifier uses. All of these are finitely many strict inequalities on the monodromy matrices, so the existing
  d_j(L) bounds transfer directly.
- Alternatively, cite our floating-point endpoint result (§161: Zariski-dense at 30/7) and certify only that the trace
  functionals stay away from their bad sets on [30/7 − δ0, 30/7].

**Weak control: the Kerr enclosure [0, 0.33] "contains 0".**
- Its width (0.33) is 30 times the endpoint effect (≤ 0.0099). An enclosure that wide would contain 0 for almost
  anything, so as a must-detect control it cannot fail.
- Ask for a Kerr enclosure as tight as the endpoint's (same step and degree settings), or a planted near-Kerr case
  whose true commutator is smaller than the endpoint's but nonzero, which the certificate must still exclude from 0.

**To check once the script is available:** that the defect is enclosed over each WHOLE subinterval (q‴ over the box,
not sampled); that the floating-point interpolant only seeds an a-posteriori interval check; and that S, P and the
basepoint conjugations are applied consistently to the three loops.

**Status:** conditional on (a) the gap fix and (b) a code read, T48 would close the sliver at spin 0.6 for E = 0.8
and 1.5. It is also conditional on our floating-point counts on (0, 30/7 − 10⁻¹²], as it says itself.

---

## T48b (the Zariski-density certificate), code read plus independent reproduction, 2026-11-21: SOUND; the sliver is closed at spin 0.6 for E = 0.8 and 1.5 (with one trivial rigour fix)
Script: `neon_work/onlykerr/T48b_code/sliver_closure_iv.py` (sha256 80f6b0c9…). Run from a scratch copy with
`python -I`. Output: `data/nve/t48b_rerun.out`.

**Reproduced:** δ0 = 1.37288e−11 at E = 0.8 (13.7 × 10⁻¹²) and 2.03609e−10 at E = 1.5. All of Z1–Z4 hold. The Kerr
controls are tight and disjoint from the endpoint: [0, 0.00168] vs ≥ 0.00361, and [0, 0.108] vs ≥ 1.110. The
wrong-tail controls collapse δ0 by 3e9 and 2e8. Runtime 201 s.

**Code read (the rigour points):**
- **Interval primitives:** csqrt and clog raise unless Re > 0. c0 at 30/7 comes from Neon's elementary closed form,
  which agrees with our Laurent c0 to double precision at 4 loop points. Its box enclosure is a centred form. That is
  valid for complex functions, because the integral remainder lies in a convex box.
- **q and its derivatives:** exact interval Taylor arithmetic on f0⁻ = Re(1/e) and P′/P. I checked the c0‴ and c0⁗
  chain rule and the q″ and q‴ factors.
- **The defect is enclosed over WHOLE subintervals:** Horner over t ∈ [−½, ½], plus the q‴(U_box) Taylor remainder ×
  [−1/8, 1/8]. Nothing is sampled. The quintic Hermite coefficients reproduce the endpoint value, first derivative and
  second derivative exactly (checked symbolically), so the piecewise interpolant is continuous and Gronwall applies.
- **Floating point only seeds:** float DOP853 supplies only the Hermite data and is converted into intervals. The
  endpoint monodromy is inflated by ‖S⁻¹Φ̃(1)‖·η.
- **The classifier logic (Z1–Z4) is correct and complete** for algebraic subgroups of SL₂: reducible, imprimitive,
  finite, or SL₂. The trace drift is bounded by 2 × the ∞-norm bounds.

**Independent reproduction on Neon's own loops** (our 50-digit walker, steps 0.35 and 0.2 agreeing to 12 digits):
- |τ(M1, M3)| = 2.86550 ∈ [2.86336, 2.86765];
- |tr A| = 3.57243 ∈ [3.57080, 3.57406];
- |tr B| = |tr AB| = 2.06866 ∈ the certified intervals;
- Im tr B = 0.71296 ∈ [0.71214, 0.71378];
- tr M1 = tr M3 = 0 to 1e−46 (single-point loops, as expected).

**Remaining issues (minor):**
1. **The basis is not exactly a conjugation.** M^(S) = S_iv⁻¹·M·Φ̃(0), but Φ̃(0) is the float midpoint of S, which may
   lie about 1e−16 outside the decimal-string interval S_iv. So it is not exactly a conjugation. Every margin is many
   orders larger, but the fix is one line: make S_iv the exact float matrix, or start from S_iv as an interval.
2. **Z1b at E = 1.5 is unnecessary and sets δ0 there** (lower bound 1.07e−14). Z1 alone, |τ(M1, M3)| ≥ 1.58, already
   gives irreducibility. Dropping Z1b would raise δ0 at E = 1.5.

**Combined status at spin 0.6:** (0, 4.05] (gap B), [3.95, 30/7 − 10⁻¹²] (§162), [30/7 − δ0, 30/7] (T48b,
interval-certified) and k = 30/7 (§161) leave no exceptional k at E = 0.8, and likewise at E = 1.5 for the sliver.
Only the sliver part is interval-certified; the rest are 50-digit floating-point counts.

**Both minor items fixed in our copy** (`data/nve/t48b_fixed/`: the patched script, PATCH.diff and the output):
- S is built from the exact float matrix (iv.mpf(float)), so Φ̃(0) = S exactly and M^(S) is a true conjugation;
- Z1b is dropped.

Rerun: δ0 = 1.37288e−11 at E = 0.8 (unchanged) and **1.90372e−9 at E = 1.5** (up from 2.04e−10, since Z1b had set it).
All Z1–Z4 and both controls pass. **This patched copy is the one to cite.** Neon may adopt the same two lines.

## T49 citations, checked at source (2026-11-22): see `MRS_SECTION.md` §6
- **MRS 2007:** verified (open Γ is the default).
- **Casale 2009:** algebraic setting only; T49's "covering open Riemann subsurfaces" is NOT supported.
- **Beig–Simon 1981:** verified (abstract); caveat: may require nonzero mass.
- **Beig–Simon 1980:** a uniqueness result, not analyticity.
- **Fodor–Hoenselaers–Perjés 1989:** verified.
