# Route (i) production: status (plain language)

*Updated 2026-11-27 (production launched), only when something changes. Written for Sumit.*

## What we are doing

We are proving, with computer arithmetic that cannot round the wrong way (interval arithmetic), that a certain
function F(k) is never zero on part of the range of k. That is what "certified" means here. Statement A already covers
the tiny stretch next to k = 0. This run extends the proof upward from there.

## Your decision (2026-11-27)

- **Goal:** spin 3/5 from Statement A's edge up to k ≈ 3, and spin 9/10 from its edge up to k ≈ 2. It is stated
  plainly as a partial result covering part of region A.
- **The top of region A (k ≈ 3.7 to 4) is parked.** The method cannot get there without new code.

## Where it stands

- **Production is running** (since 2026-11-27 04:49, one Air core per spin).
  - Spin 3/5 is expected to take about a day.
  - Spin 9/10 is expected to take about 3–3.5 days.
- **The production code was read twice on the Bridge's side and found sound.** Every final test passed.
- **Two trial segments already certified,** one at the very bottom of 3/5's range and one at 9/10.
- **If a stretch will not certify,** it is cut in half at most twice. If it still fails, that part stops, and we
  report how far we got. No code is changed mid-run.

## The small-k check is in (P4-r, 2026-11-27)

- **Spin 3/5 is fine all the way down.** The arithmetic's uncertainty is about 1/1000 of F, even at the bottom.
- **Spin 9/10 is not.** Its uncertainty stays at about 2.6e-8 at every k, while F shrinks like k². Below roughly
  k ≈ 2e-3, F is smaller than the uncertainty, so the proof cannot tell it from zero, and cutting the range finer does
  not help.
- **So the expected 9/10 result is "certified from about 2e-3 to 2".** There is a small gap between Statement A's edge
  (about 1e-4) and 2e-3, which will be stated plainly. Closing it would need an evaluator change, which is parked.
- **The other two conditions (the traces) are comfortably satisfied at small k** at both spins. Only F is the problem.

## What would change this page

A part of the range that stops; any alarm; each spin's final reach.
