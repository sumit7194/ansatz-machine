# Route (i) production: status (plain language)

*Updated 2026-11-27 (after P4-r), only when something changes. Written for Sumit.*

## What we are doing

We are proving, with computer arithmetic that cannot round the wrong way (interval arithmetic), that a certain
function F(k) is never zero on part of the range of k. That is what "certified" means here. Statement A already covers
the tiny stretch next to k = 0. This run extends the proof upward from there.

## Your decision (2026-11-27)

- **Goal:** spin 3/5 from Statement A's edge up to k ≈ 3, and spin 9/10 from its edge up to k ≈ 2. It is stated
  plainly as a partial result covering part of region A.
- **The top of region A (k ≈ 3.7 to 4) is parked.** The method cannot get there without new code.

## Where it stands

- **The production code was read twice on the Bridge's side and found sound.** Their fixes are in.
- **The final tests are running now** (started 01:10, about 3–4 hours, two Air cores).
- **Production follows:** about 1 day for spin 3/5 and about 3.5 days for spin 9/10.

## The small-k check is in (P4-r, 2026-11-27)

- **Spin 3/5 is fine all the way down.** The arithmetic's uncertainty is about 1/1000 of F, even at the bottom.
- **Spin 9/10 is not.** Its uncertainty stays at about 2.6e-8 at every k, while F shrinks like k². Below roughly
  k ≈ 2e-3, F is smaller than the uncertainty, so the proof cannot tell it from zero, and cutting the range finer does
  not help.
- **So the expected 9/10 result is "certified from about 2e-3 to 2".** There is a small gap between Statement A's edge
  (about 1e-4) and 2e-3, which will be stated plainly. Closing it would need an evaluator change, which is parked.
- **The other two conditions (the traces) are comfortably satisfied at small k** at both spins. Only F is the problem.

## What would change this page

The test results; the launch; each spin's final reach.
