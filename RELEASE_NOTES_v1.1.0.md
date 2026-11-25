# Ansatz Machine v1.1.0: release notes (2026-11-25)

**Status: UNCHANGED.** The "Only Kerr" result is still a careful numerical result, not a theorem. v1.1.0 adds one
local piece that is rigorous relative to the applicability chain, and it fixes several points in the argument. No
number in the main claim changed.

## What changed since v1.0.0 (tag v1.0.0, 2026-11-22)
- **New: Statement A (claim v3; `data/nve/CLAIM_FAMILY_II.md`).**
  - **What it says.** For each tested spin a ∈ {3/10, 3/5, 4/5, 9/10} at E = 4/5 there is ε_a > 0 such that, for
    every k ∈ (0, ε_a), the monodromy group of the lower-axis ρ-equation is Zariski-dense in SL(2, C).
  - **How.** The k²-coefficient c2 of tr[M1, M0] − 2 has a closed form in terms of Kerr's explicit solutions, and its
    nonvanishing is certified in interval arithmetic. ε_a is not quantified.
  - **It comes with four conditions:**
    1. It is an anchor, not new range: the numerical counts already covered (0, ε_a), and at spin 9/10 the interval
       is small.
    2. It is rigorous only relative to the chain, whose caveats stand:
       - Proposition 2 rests on our own proof, not yet independently checked;
       - e₋ = 1/e₊ is assumed, or taken as the definition;
       - one cited theorem number (Lemma C(a)) is secondhand.
    3. c2 ≠ 0 is certified spin by spin, and it is false at the untested spin ≈ 0.908.
    4. Credit as below.
- **New: Lemma K (`MRS_SECTION.md` §5d).** The monodromies are holomorphic in the twist parameter k at k = 0. With
  its proof, this is what turns c2 ≠ 0 into Statement A.
- **Explained: the extra zero at spin 9/10.** c2 changes sign near spin 0.908, so a third zero passes through k = 0
  there.
- **Corrected: the transverse variational equation in regular coordinates (`MRS_SECTION.md` §5b).**
  - The old claim: the two transverse directions are "two identical copies" of the axis equation.
  - What is true: frame dragging (g^{tφ}) rotates one copy into the other.
  - The conclusion is unchanged, by a corrected argument.
- **Corrected: which system the theorem is applied to (`MRS_SECTION.md` §1).** It is the system reduced by the time
  coordinate t, in Cartesian coordinates around the axis, not the system reduced by the rotation (which is singular on
  the axis). The complexified orbit and the holomorphy of the Hamiltonian near the complex loops are now stated
  explicitly.
- **Made consistent: the status of Proposition 2,** across all files: our own majorant proof, checked by its author
  and by a numerical control, not yet independently checked.
- **Added: two arguments in `MRS_SECTION.md` §3.**
  - c0 is holomorphic at infinity with real coefficients.
  - c0 ≠ 0 at both rod endpoints, so those are ordinary points. Proved by hand and checked numerically.
  - Also recorded there: the real lower-axis data are not continuous in k at k → 0+ near the lower rod end, nor at
    k = 30/7. No computation is affected.
- **New scripts and outputs:**
  - `scripts/_nve_c2_analytic.py` and `scripts/_nve_c2_certify.py` → `data/nve/c2/`;
  - `scripts/_nve_c2_sympy_check.py` and `scripts/_nve_c2_engine_check.py` → `data/nve/c2_*_check.out`;
  - `scripts/_nve_rodend_c0.py` → `data/nve/rodend_c0.out`.

## Credit
- **The c2 formula and its interval certificate:** a Fable side-session. Branch `fable/2026-11-25-c2-analytic`,
  commits 5b6110b and 8d8d04c, brought into main as 66873a2 and 29d2555.
- **Independent verification:** the ansatz-machine session, commit c3766aa (`data/nve/C2_OFFICE_CHECK.md`).
- **The §5b error and the Prop. 2 inconsistency:** found by an independent reader, organised by the coordinating
  session ("the Bridge").
- **The §1 point:** raised by a hostile referee read ("Neon").
- **How it was made:** these are AI sessions (Anthropic's Claude) working under the author's direction, as described
  in `ONLY_KERR.md`. The author chose the questions, reviewed the work, and takes responsibility for it.

## Citation
Cite all versions as DOI 10.5281/zenodo.24431694. The version DOI of v1.1.0 will be assigned by Zenodo on release.
