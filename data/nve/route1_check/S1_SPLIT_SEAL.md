# SEAL: S1, the split discriminator (a NEW registered stage after stage P stopped; diagnostic only)

**Office ansatz-machine (Claude Opus), 2026-11-28.** Go from the Bridge, under Sumit's delegation of planning. This is
committed before anything runs.

**Code:** the v7 and v7B layers exactly as at dab2a9d (the stage-P code). **ρ = 4, mode F, tol rel.** Mac mini, 2 cores,
nice 10, under the pause-only guard. **It certifies NOTHING for production:** prove stages only, and no verdict.

## Question
All three P pilots were rejected because v2's crude dq bound could not certify G1/G2 ≠ 0 over a step box × the ρ = 4
k-box, an enclosure artifact from the k-Taylor inflation. Does the registered split rule (halve the segment, to depth
2) recover the rows on the existing machinery?

## What runs (prove only; each segment's loops fixed at its own centre, as production does)
- **Region B (pilot 2's segment [4.1, 4.2]):**
  - depth 1 (half-width 1/40): k_c = 33/8 (4.125) and 167/40 (4.175);
  - depth 2 (half-width 1/80): k_c = 329/80, 331/80, 333/80 and 335/80.
  - Floats come from `_nve_v7_floatsB.py`, the registered geometry rule, at each centre.
- **Circle (pilot 1's segment [3.9, 4.0]):**
  - depth 1 (1/40): k_c = 157/40 and 159/40;
  - depth 2 (1/80): k_c = 313/80, 315/80, 317/80 and 319/80.
  - Floats come from `_nve_route1_floats.py` at each centre.
- Every sub-segment at both depths runs (12 proves), so the reading needs no adaptivity.

## Reading (fixed now)
**Per region,** the split rule "recovers" the segment if EITHER every depth-1 half admits a ρ = 4 row (n ≤ 40), OR, for
each depth-1 half that does not, BOTH of its depth-2 quarters admit one.

| circle | region B | reading |
|---|---|---|
| recovers | recovers | **the split rule recovers; the plan survives on existing machinery** (cost: 2–4× segments near such boxes) |
| one of the two | | **partial**: the recovering region proceeds on existing machinery; the other needs candidate 2 |
| neither | neither | **the crude dq bound needs replacing (candidate 2)** |

**Also recorded per sub-segment:** admitted or rejected, with the reason, n, M_F, and the prove time (the cost input).

## Must-fail control (it must FIRE before the reading counts)
- A planted near-zero of G inside a split box: v2's crude `dq_sup`, on a box of radius 0.01 centred on a TRUE zero of
  G1 (r+, from the floats entry), with K the depth-2 k-box, must return None (refused). This is done in both regions
  (the circle layer and v7B) by `scripts/_nve_v7_s1_control.py`.
- A crude bound that accepted a box containing a true zero would make the whole S1 reading worthless.

## Predictions

| | P |
|---|---|
| control fires in both regions | 97% |
| region B recovers (depth ≤ 2) | 55% |
| circle recovers (depth ≤ 2) | 55% |
| both recover | 35% |
| neither | 25% |
| wall time under 1 h on 2 cores | 80% |
