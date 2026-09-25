# Re-derivation of the two EXP-003 statements borrowed by the rank-3 note — pre-registration

Asked by The Bridge, 2026-09-26, before any outside draft. Source is CG 2015 (arXiv:1503.02162), read from the
**typeset PDF** (`external/high_rank_killing/prior_art/CG_1503.02162.pdf`, pp. 4–8), never the text extraction.
EXP-003's code is not used or read. Script: `scripts/_cg_recheck.py` (fresh).

## (a) "CG's cubic is −½{Q_a, Q_b} in their own variables, with I² = −H Q_a Q_b − β² Q_a − α² Q_b"
System: CG eq. (20), H = p_x p_y + α/√x + β/√y, {x,p_x} = {y,p_y} = 1,
I = x p_x² p_y − y p_x p_y² + (βx/√y) p_x − (αy/√x) p_y. Q_a = CG footnote 9, Q_b = its image under (x,α)↔(y,β).
- A1: {H,Q_a} = {H,Q_b} = {H,I} = 0 exactly.
- A2: {Q_a,Q_b} + 2I = 0 exactly.
- A3: DERIVE the relation, don't just check it. Fit I² = Σ c_ijk H^i Q_a^j Q_b^k over i+j+k ≤ 3, with c
  allowed to depend on (α,β). Expect the unique solution to be the stated one.
- A4: functional rank of (H,Q_a,Q_b,I) = 3, and of (H,Q_a,I) = 3.
- Sabotage: flipping the sign of I's β-term must break A1 and A2, and A3 must find no relation.
Label: CONFIRMED if A1–A4 hold and the sabotage turns them red. CORRECTED if the relation differs.
WITHDRAWN if the bracket statement fails.

## (b) "The rank-4 (2,2) metrics admit no Lorentzian real form, by an anti-self-duality argument"
Expected from reading CG before computing: CG's rank-4 metrics are 5D (2,3) eq. 26 and 6D (2,4) eq. 30, both
oxidations of the FIRST Drach system (16). There are no rank-4 (2,2) metrics. ASD is a 4D notion. So the claim
as worded is expected to need correction, and the question becomes what the ASD argument actually covers.
- B1: the 4D lift of (16) (CG eq. 1 with U = α(y − βx) + γ/√x) is Ricci-flat, non-flat, and ASD by CG's own
  eq. (6): the lower sign holds and the upper does not.
- B2: the Lorentzian step (ARGUED, textbook). On 2-forms, ** = +1 in (2,2) and −1 in (1,3), so for a real
  Lorentzian Weyl tensor the two chiral halves are complex conjugates. W⁻ = 0 is a holomorphic condition, so it
  holds on every real slice. W⁻ = 0 then gives W = 0, and Ricci-flat plus W = 0 is flat, which contradicts B1.
  Computed: the sign of ** in both signatures.
- B3: 5D eq. 26 as a Kaluza–Klein metric, g₅ = h + (dw + αx dt)², where the base h is CG eq. 1 with
  U = αy + γ/√x. Expect h to be Ricci-flat, ASD, non-flat, with vanishing Kretschmann. Then any real
  Lorentzian slice on which ∂_w is real is excluded: either the base is a Lorentzian real form of h (B2), or it
  is definite and flat (Kretschmann 0). Slices where ∂_w is not real are NOT covered.
- B4: 6D eq. 30, the same decomposition over the two fibres. If its base is flat, the ASD argument does not
  transfer at all.
Label (b): CONFIRMED only if the statement holds as worded. Expected: CORRECTED, narrowed to what B1–B4 cover.

## RESULT (2026-09-26, `data/cg_recheck/recheck.out`)
- **(a) CONFIRMED.** A1–A4 all hold. The relation was derived, not only checked: the unique fit at three generic
  (α,β) is exactly −H Q_a Q_b − β² Q_a − α² Q_b, and the symbolic identity holds for all α, β. The sabotage turns
  all three tests red.
- **(b) CORRECTED**, as predicted. There are no rank-4 (2,2) metrics in CG. B1 holds: the 4D first-system
  metric is non-flat, Ricci-flat, ASD and not SD, so it has no Lorentzian real form (B2: ** = +1 in (2,2) and −1
  in (1,3), computed; the rest is textbook). B3: the 5D metric is h + (dw + αx dt)² over an ASD, non-flat,
  Kretschmann-0 base, so it is excluded on real slices with real ∂_w only. B4: the 6D base is flat
  (U_base = αy), so there is no transfer.
- Process note: the first run used a symbolic-parameter solve and SymPy `Matrix.rank`, and stalled for over
  20 min. It was replaced by exact QQ row reduction at fixed rational parameters plus the symbolic identity,
  with the same content (the change is stated in the fit's docstring).
