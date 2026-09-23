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
