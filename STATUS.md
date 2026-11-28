# Ansatz Machine: status (plain language; updated only when something changes)

*Last change: 2026-11-28 05:20. Owner of the running work: the office ansatz-machine session.*

## What we know (with grades)
- **The main claim is unchanged (claim v3.1, `data/nve/CLAIM_FAMILY_II.md`).** "Only Kerr" along the lower axis, at
  four tested spins, is a careful NUMERICAL result (50-digit counts), not a theorem.
- **Statement A is rigorous relative to the applicability chain.** Near Kerr (twist 0 < |k| ≤ ε_a), with ε_a
  interval-certified per spin: 2.79e−3, 1.92e−3, 8.39e−4 and about 1e−4 at spins 3/10, 3/5, 4/5 and 9/10.
- **Route (i): interval certificates over stretches of k.** Internal, not in the claim:
  - **spin 3/5 is certified for every real k in [1/640, 3], production finished and checked (2026-11-27 20:44).**
    With Statement A this covers 0 < k ≤ 3 at 3/5 with no gap;
  - **spin 3/10 is certified for every real k in [1/320, 3]** (done and checked 2026-11-28 05:04); the gap is
    [2.79e−3, 3.125e−3] above Statement A, at the evaluator's floor;
  - earlier, two stretches were certified and checked (k ∈ [1, 1.1] at spins 3/5 and 9/10);
  - the method reaches k ≈ 3 at most (segment centres stop at 3.7–3.8, and 9/10 stops near 2);
  - near k = 0 the evaluator's own uncertainty leaves gaps above Statement A: none at 3/5 and 4/5, small at 3/10, and up to
    1.25e−2 at 9/10.

## What is running (MacBook Air, one core each, nice 15, pause-only guards)

| run | target | state | expected finish |
|---|---|---|---|
| spin 9/10 production | [ε_a, 2] | bottom stopped at k = 1/80 (gap from about 1e−4 to 1.25e−2; a sealed miss); upward chain running | about 2026-11-29 evening |
| spin 4/5 production | [ε_a, 3] | bottom certified to 1/1280 (no gap); upward chain running; check-in passed (projected 45–50 h) | about 2026-11-29 13:00 (08:00–20:00) |

## The next decision, and who makes it
- **v1.2.0 is released** (2026-11-27, tag on 312571f; approved by Sumit via the Bridge). Version DOI
  10.5281/zenodo.24593416, verified on Zenodo by the Bridge.
- **v1.3** waits for the 9/10, 3/10 and 4/5 productions. **Sumit** approves its notes.

## Practices in force
- **Fleet rule 7 (2026-11-27):**
  - public text uses the field's terms ("predictions fixed before the data were examined", "computer-assisted
    proof"); "pre-registration", "registered" and "sealed" stay internal;
  - before any claim leaves, a field-expert checklist (each item done or open) goes to the Bridge with it.
- **Air allocation (2026-11-28, Sumit via the Bridge):** from about 06:15, the Air's memory and GPU belong to Sumit's
  AlphaMate training. Only the running 4/5 and 9/10 productions stay. No new Air job goes on without the Bridge's OK. A
  guard pause from AlphaMate's memory pressure is fine, and it is reported to the Bridge.

## Kill criteria
- **4/5:** stop and re-plan if the upward chain has not reached k = 2 by 2026-11-29 18:00. Stop and report the reach
  if it has not reached 3 by 2026-12-01 00:00. Check-in done 2026-11-28 04:57: projected 45–50 h, no re-gate.
- **9/10:** it runs within its sealed estimate (checked at about 25%). It stops for a decision on any
  alarm or engine miss. A segment that will not certify after two halvings ends its chain, and the reach is reported.
- **All:** no code changes mid-run. "Good enough" is certified over the reach actually achieved, stated plainly as part
  of region A.
