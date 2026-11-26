# Route (i) production: status (plain language)

*Updated 2026-11-27, only when something changes. Written for Sumit.*

## What we are doing

We are proving, with computer arithmetic that cannot round the wrong way (interval arithmetic), that a certain
function F(k) is never zero on part of the range of k. That is what "certified" means here. Statement A already covers
the tiny stretch next to k = 0. This run extends the proof upward from there.

## Your decision (2026-11-27)

- **Goal:** spin 3/5 from Statement A's edge up to k ≈ 3, and spin 9/10 from its edge up to k ≈ 2. It is stated
  plainly as a partial result covering part of region A.
- **The top of region A (k ≈ 3.7 to 4) is parked.** The method cannot get there without new code.

## Where it stands

- **The production code is written and waiting for the Bridge's independent read.** It checks itself several ways:
  each segment has controls that must fail when they should, and a second, independent engine checks every value
  used.
- **Nothing is running yet.** After the read, about 3–4 hours of tests run on two cores of the Air. Production follows:
  about 1 day for 3/5 and about 3.5 days for 9/10.

## One risk you should know about

**At spin 9/10, the very bottom of the range (k between about 1e−4 and 1e−2) is probably out of reach.** There F is
extremely small, about a billionth or less. The arithmetic's built-in uncertainty is larger than F itself, so the
proof cannot tell F from zero. Cutting the range into smaller pieces does not help. Fixing it would need changes to
the evaluator, which is new code, and that is parked.

A 25-minute check (P4-r) measures this before anything long runs. If it confirms the risk, the 9/10 result would be
"certified from about 1e−2 to 2", with the small gap stated. Spin 3/5 has plenty of room and should be fine.

## What would change this page

The read result; the 25-minute check; the test results; the launch; each spin's final reach.
