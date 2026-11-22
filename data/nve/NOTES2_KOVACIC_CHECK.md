# Check of the necessary direction "deg f0 ≥ 3 ⇒ Galois group SL(2, C) at generic E" (2026-11-22)

**Object checked:** `fable_work/axis_integrability_classification/NOTES.md` §2 (the "s + 2h ≤ 4" checklist). Also
the matching Kovacic step of `THEOREM_TS.md` §4.2. Both are UNVERIFIED Fable-era drafts, read here read-only at the
Bridge's request. Our earlier grade (RESULTS §158; `NVE_PREREGISTRATION.md`) was "~95%: Kovacic count re-derived,
plus 9 numerical runs".

**Kovacic data checked against:** the full restatement of Kovacic's algorithm in Acosta-Humánez & Blázquez-Sanz,
arXiv:math-ph/0610010, Appendix A. The original, Kovacic 1986 (J. Symb. Comput. 2, 3), is being fetched for one
detail; see Case 3.

## Set-up
- The equation is v″ = r v with r = −(3/16)(P′/P)², P = E² − μ² f0, and f0 rational of degree d.
- At a zero or pole of P of order m, r has a double pole with leading coefficient b = −3m²/16. So
  √(1 + 4b) = √(1 − 3m²/4):
  - 1/2 at a simple point (|m| = 1);
  - imaginary for |m| ≥ 2, e.g. i√2 at |m| = 2.
- At ∞, P → E² − μ² f0(∞) ≠ 0 at generic E. Then r = O(z⁻⁴): order > 2, and ∞ is ordinary. CHECKED.

## The three cases, entry by entry (restatement, App. A)
**Case 1:** α_c^± = (1 ± √(1 + 4b))/2.
- Simple point: {1/4, 3/4}. Heavy point: 1/2 ± i·(real ≠ 0). At ∞ (order > 2): α⁺ = 0, α⁻ = 1. **Matches NOTES.**
- Degree d = α_∞ − Σ α_c must be in Z≥0. The imaginary parts of heavy α must cancel, and the real part is then
  ≤ 1 − s/4 − h/2. **So s/4 + h/2 ≤ 1 is necessary. CHECKED.**

**Case 2:** E_c = {2 + k√(1 + 4b) : k = 0, ±2} ∩ Z.
- Simple point: {1, 2, 3}. Heavy point: {2}. At ∞ (order > 2): {0, 2, 4}. **Matches NOTES.**
- d = (e_∞ − Σ e_c)/2 ∈ Z≥0 needs Σ e_c ≤ 4, hence **s + 2h ≤ 4. CHECKED.**

**Case 3:**
- Finite points: E_c = {6 + (12k/n)√(1 + 4b)} ∩ Z. Simple point: min 3, max 9, for every n. Heavy point: {6} (only
  k = 0 survives ∩ Z). **Matches NOTES.**
- **The one detail not settled by the restatement:**
  - App. A lets k run to ±6 for every n ∈ {4, 6, 12}. With γ = 0 at ∞, that would allow e_∞ up to 6 + 3·6 = 24 for
    n = 4.
  - NOTES assumes e_∞ ≤ 12, which is Kovacic's range k ≤ n/2 as usually stated.
  - The original is being checked.
- **Case 3 is excluded INDEPENDENTLY of that range** (argument written here):
  - **If h ≥ 1:** a heavy point has local monodromy eigenvalues e^{2πis} with s = 1/2 ± i t, t ≠ 0, so of modulus
    ≠ 1. That is an element of infinite order, so the group is not finite and Case 3 cannot hold.
  - **If h = 0**, suppose the projective monodromy group were finite, of order N.
    - Let X be its Galois cover of the sphere. Each simple point has projective local monodromy of order 2, so
      Riemann–Hurwitz gives g_X = 1 − N + sN/4.
    - The Schwarz map η = y1/y2 is single-valued on X. It is unramified at the lifts of ordinary points (Wronskian
      ≠ 0). At the lifts of simple points the exponent difference 1/2 doubles to 1, so η is locally bijective there
      too.
    - So η: X → P¹ is an unramified finite cover, hence an isomorphism, so g_X = 0. That gives s = 4 − 4/N < 4.
  - **So finite (projective) monodromy needs s ≤ 3.** For s + 2h ≥ 5 Case 3 is impossible. **CHECKED** (independent
    of Kovacic's Case 3 data).

**Conclusion of Kovacic's theorem:** if no case holds, G = SL(2, C).
- Restatement: Theorem 2 and App. A ("falls in the case 4").
- Galois group = Zariski closure of the monodromy, since the equation is Fuchsian.

## The count for d ≥ 3 (NOTES §2 "Result")
At generic E:
- d simple zeros of P (f0 = E²/μ² has d simple solutions off the finitely many critical values, and none at ∞);
- plus the poles of f0, whose orders sum to d.
- If the poles sit at one point, it is heavy (order d ≥ 3) and contributes 2. Otherwise there are ≥ 2 poles,
  contributing ≥ 2.
- **So s + 2h ≥ d + 2 ≥ 5. CHECKED.**

## Verdict
**The necessary direction is CHECKED:** deg f0 ≥ 3 ⇒ G = SL(2, C) for the axis normal form, at every E with
E²/μ² ≠ 0, not a critical value of f0, and ≠ f0(∞).
- Cases 1 and 2 are checked against Kovacic's conditions as restated in full by Acosta-Humánez & Blázquez-Sanz.
- Case 3 is excluded by an independent monodromy argument (heavy point ⇒ infinite order; Riemann–Hurwitz for h = 0).
- The count is checked.
- **This is upgraded from "~95%" to checked, at generic E.**

**Scope, as before:**
- "Generic E" is essential: the explicit degree-3 counterexample M3 (§158) has three zeros merging at one E.
- From "G = SL(2) on the sphere" to Morales–Ramis on Γ needs Lemma 1–2 (the axis reduction; verified by Bridge V21)
  and the covering/gauge step (our Lemma C, MRS_SECTION §1).
- **The sufficiency direction (deg ≤ 2 ⇒ solvable) is NOT part of this check.**
  - NOTES §2's table rows (4 simple points via the elliptic double cover; the Kimura dihedral row) look right.
  - They were not checked line by line here, and §158 still grades sufficiency ~80–85%.

## THEOREM_TS §2/§4.2 (TS δ = 2), the Kovacic step
- **Its axis data agree with ours.** The poles are the roots of 2x⁴ + 10x³ + 21x² + 10x + 2 at (p, q) = (4/5, 3/5),
  identical to `ts2_axis_deg.out`, which came from our verified-vacuum `_ts2_build.py` potential.
- **Its three energy regimes all have s + 2h ≥ 5:** (8, 0) generic, (8, 0) at λ = 1 with ∞ simple, and (4, 2) at
  λ = 1 + 1/|q|. So its "every E ≠ 0" claim for (i) is consistent with the checked bound, and the generic-E caveat
  does not bite.
  - The reason: the four simple poles alone give 4, and zeros can merge only in pairs.
  - The discriminants it quotes were not recomputed here.
- **§4.3 (covering, dt-periods, MR Theorem 7) was not checked here.** It parallels our Lemma C.
- **TS meromorphic non-integrability stays Quantum's / Fable's result, relayed (CLAUDE.md §0).** What this repo
  checked is the Kovacic step and the axis data.
