# Axial ℓ-scan at rank 4 — result (2026-09-24)

Pre-registration: `PREREGISTRATION.md` (commit 4693296). Runs: `r4_o*.out`, footprints in `*.time`
(max 0.74 GB).

**Regression (must hold): HELD.** ℓ = 1 → 0 (base 12, as before), ℓ = 3 → exactly 1·o3tphi_1 − 1·o3tphi_2 −
2·o3tphi_3 with survivors (10, {0:9, 1:0, 2:1}), ℓ = 5 → 0. All floors at 9.

| axial ℓ | y-parity of A_ℓ | pole-order-1 directions | validity | notes |
|---|---|---|---|---|
| 1 | even | 0 | floor 9 | base 12 of 18 |
| **2** | **odd** | **2** | floor 9; **margin 8 and prime 1 identical** | o2tphi_2 − 2·o2tphi_3, and o2rphi_1; both survivors (10, {0:9, 1:0, 2:1}) |
| 3 | even | 1 | floor 9 (§146: both primes, margin 8, L⁹/L¹¹) | o3tphi_1 − o3tphi_2 − 2·o3tphi_3 |
| 4 | odd | 0 | floor 9 | |
| 5 | even | 0 | floor 9 (§146) | |
| 6 | odd | 0 | **margin 4 INVALID (floor 8)**; margin 8 valid (floor 9) | L⁹ at margin 4 still floor 8 |
| 7 | even | 0 | **margin 4 INVALID (floor 8)**; margin 8 valid (floor 9) | L⁹ at margin 4 still floor 8 |

**Prediction scorecard:** ℓ = 7 → 0 ✓. ℓ = 2, 4, 6 → 0 (low confidence): **wrong for ℓ = 2.**

**Box knob, measured, not guessed (rule 114):** for ℓ = 6, 7 at rank 4 the fix is the **margin** (the numerator
box, i.e. the angular degree), not the denominator. That's the opposite of the rank-8 axial case, where L⁸ was
needed. The same symptom (random below the floor) had two different causes.

**What the ℓ = 2 result is, as pre-registered:** two directions in the reduced rank-4 system at pole order 1,
for O(χ²) axial probes at first order in ε, surviving margin 8 and the second prime, with the same survivor
anatomy as ℓ = 3. **It is not a Killing tensor, not exact, not a physical metric, and says nothing above rank 4.**

**Observations, not explanations:** (i) only ℓ = 2 and 3 carry pole-order-1 directions at rank 4, and all
ℓ ≥ 4 give 0. (ii) Both h_tφ directions have radial profiles that vanish at the horizon: ℓ = 2 gives
(r − 2)/r³ and ℓ = 3 gives (r − 2)(r + 1)/r³ (M = 1). (iii) Equatorial parity does not block a direction (ℓ = 2 is
odd in y). A hypothesis worth a separate, pre-registered test, NOT claimed: at rank 4 only low harmonics
(ℓ ≤ 3) can couple to the Carter-power structure at pole order 1. That would predict polar ℓ = 4 at rank 4 also
has no new direction there, and that axial ℓ = 4, 5 might first appear at rank 6.

---

## Frozen predictions for the candidate "at rank 4 only low harmonics (ℓ ≤ 3) couple at pole order 1"
*Committed 2026-09-24 BEFORE the runs, at The Bridge's request.*

1. **Polar ℓ = 4 at rank 4 → 0 new directions at pole order 1.** (Run: `_kt_pole_reduced.py --rank 4 --denpow 7
   --margin 4 --slots l4tt,l4rr,l4ang`, same controls; floor 9 must hold, and if it fails, margin 8.)
2. **Axial ℓ = 4 at rank 6:** the candidate predicts a direction may appear at pole order 1 or 2. Frozen
   operationally as "nonzero at pole order ≤ 2" = candidate supported; "0" = candidate weakened.
3. **Axial ℓ = 5 at rank 6 was ALREADY MEASURED earlier tonight** (`data/anat/reduced_r6_o5_p{0,1}.out`, 0 at pole
   orders 1 and 2, both primes, floor 16 valid). The candidate's "ℓ = 5 might first appear at rank 6" is already
   **contradicted by data I had in hand**. It should have been checked against my own notebook before the
   candidate was written (rule 110). It is scored as a miss here and not re-run as if it were fresh.

## Scorecard for the candidate (2026-09-24)
| frozen prediction | result | score |
|---|---|---|
| polar ℓ = 4, rank 4: 0 at pole order 1 | **2** (floor 9; footprint 0.47 GB), with exactly §143's rank-8 pole-order-1 coefficients | **MISS** |
| axial ℓ = 5, rank 6: may appear | 0 at pole orders 1 and 2 (measured earlier tonight, both primes) | **MISS** (data already in hand) |
| axial ℓ = 4, rank 6 | not run: the candidate is already falsified, so the run has lost its purpose | — |

**The candidate "only ℓ ≤ 3 couple at pole order 1 at rank 4" is DEAD.** Worse, **both** of its checkable clauses
were contradicted by data already in this notebook when it was written: §143 had polar ℓ = 4 with +2 at pole
order 1, and §142 records pole-order-1 counts as stable across ranks; the rank-6 ℓ = 5 result was also in
hand. That is the rule-110 failure twice in one evening: the candidate should have been checked against the
notebook before it was put in writing. The fresh polar run still earns something: **rank 4 reproduces §143's
rank-8 ℓ = 4 directions exactly**, a cross-rank consistency check.

What survives: the axial table ℓ = 1…7 → 0, 2, 1, 0, 0, 0, 0, and the uniform anatomy (10, {0:9, 1:0, 2:1}) of every
pole-order-1 direction seen (polar ℓ = 2 and 4, axial ℓ = 2 and 3). "Which harmonics couple, and why" is open,
and it is not a low-ℓ cutoff.
