# C2 ruling (B): the base2 fix, a NEW mechanism, and the 20 dyadic segments it opens. Committed BEFORE the read and any run
**Office ansatz-machine, 2026-11-29.** The Bridge's ruling (B): GO for the base2 fix as a new mechanism. The order:
1. the code;
2. a non-author read, including d2kc0_B's other s-ball loops;
3. the controls (P3 still certifies with the changed code; the old squaring refuses at 5e−6);
4. then the sliver segments, after production (A), or alongside if cores free up.

Branch `personal/2026-11-29-base2-fix`, worktree `conjecture_machine-b2fix`. It is kept apart so that production (A), which re-imports v7B at every segment, never sees the change.

## The mechanism (`scripts/_nve_route1_segment_v7B.py`, `base2` only)
`base2(K)` encloses d²c0/dk² and d²c0′/dk² at the base point over a k-set K. It is the integral over s ∈ [0, 1/bB] of d²√P/dk² = −P_k²/(4 P^{3/2}), with P = (90 − 21k) − (60 − 18k)a²s² + (10 − k)a⁴s⁴, under weights (C2-M's H1 guard). Three changes:
1. **Endpoint squares.**
   - s ≥ 0 on the domain, so a²s² and a⁴s⁴ are enclosed from each piece's endpoints (they are monotone there).
   - The old midpoint-radius s·s had a negative lower bound on the first cell. With −(60 − 18k) about +17 near 30/7, Re P > 0 failed for 30/7 − k below 7.08e−6 (measured; predicted 7.1e−6). That was probe Pend's refusal.
2. **P^(−3/2) = exp(−(3/2) log P),** on the principal branch; Re P > 0 is certified first.
   - The old 1/(P √P) is a midpoint-radius product of two balls. Near 30/7, P varies several-fold over a cell, the product's ball contains 0, and the old code returned NaN instead of refusing.
   - This happened at d = 1e−5, and on P3's own cells L0_21 and L0_23. There the NaN crashed the glue's exact-binary writer, so no record was written, the cell was refused and refined: fail-closed by accident, not by design.
3. **Adaptive and geometric pieces.**
   - The first cell [0, 1/SM] is split into geometric pieces [2^−(m+1), 2^−m]/SM, for m < 60, plus [0, 2^−60/SM]. The integrand peaks at s = 0 like (90 − 21k)^(−3/2).
   - Any piece whose Re P > 0 or finiteness is not certified is halved, down to 40 levels, with at most 4096 pieces per call. Beyond either limit the call is refused (None).
   - Each piece contributes its enclosure times its exact width.

## Controls B1–B4 (`scripts/_nve_base2_fix_controls.py`; development runs, recorded in `c2/b2fix_controls.json`; re-run after the read)
- **B1, must-fail:** the OLD base2, exec'd from git at 408b56e, refuses at 30/7 − 5e−6 and is non-finite at 30/7 − 1e−5. The new one is finite at both.
- **B2, truth:** at 30/7 − d, for d ∈ {1e−3, 1e−5, 1e−6, 1e−9, 1e−11, 7e−15}, the new enclosures contain an independent Arb quadrature.
  - The over-estimates are 0.1–2.8 times |value|.
  - Before change 3 they reached about 1e8 at d = 1e−11, which was still a valid enclosure.
- **B3, agreement:** wherever the old code is finite (d = 1e−3 and P3's 25 R/5 cells), the old and new enclosures overlap. The old code is non-finite exactly on P3's refined cells L0_21 and L0_23.
- **B4, cells:** the worst R/5 cell (nearest 30/7, on and off the real axis) of every dyadic segment j = 1..27 gives a finite enclosure.
- **Status of the development run:** B1–B4 PASS.

## Control B5: P3 certifies with the changed code (a full C2-M segment run)
- `air/c2m_segment.sh P3B2 59979/14000 1/2000`, from this worktree, once, after the read.
- **PASS** means the same bar as P3: CERTIFIED with no ALARM, M1, the M2 plants ALARM, M4 trips, the engine gate.
- Expected: L0_21 and L0_23 are now accepted at R/5, with no refinement.

## The segments: D8–D27 (`C2_B2FIX_MANIFEST.txt`)
- **The segments:** [30/7 − 2d, 30/7 − d], with d = 1/(1000·2^j), j = 8..27, and half d/2. That is 20 segments, two lanes, run with `C2_MANIFEST=… air/c2m_prod.sh`.
- **Where the chain ends:** D27 ends at 30/7 − 7.45e−12, inside the 3/5 end sliver (30/7 − 1.37e−11, 30/7] (erratum E-δ0). The chain from P3 = D0 through D27 then meets it.
- **Floats entries:** from the committed geometry rule, generated before any run and committed before any segment runs; geometry_ok is enforced by the runner.
- **Reading:** as production (A). Each certificate stands alone; a failure is recorded with its reason, and no retry runs without a ruling.

## Predictions
- B5 (P3) certifies: 90%.
- D8–D27 all certify: 50%. Node precision against |F| and the outer branch point are untested below d = 1e−3, and tr M0 (tr Gamma) is about −0.0031 near the end, small against its error bound at that size.
- At least 15 of 20 certify: 75%.
