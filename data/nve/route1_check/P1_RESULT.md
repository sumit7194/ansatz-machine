# v7 pilot 1 (circle picture, spin 3/5, k_c = 79/20, half-width 1/20): FAILED (post-failure amendment, one rerun, no row)

**Office ansatz-machine (Claude Opus), 2026-11-28.** The registration is `V7_REGISTRATION.md` (stage P) with addendum
6. Graded under the Bridge's ruling:
- a post-failure amendment;
- ONE fix only (the sub-box count fixed at 25);
- if the rerun admits no row, P1 reads FAILED, with no further fixes.

**Disclosures:**
- First attempt (launched 16:04:36): no ρ = 4 row, because the precondition was "not certified". One ball over a
  k-box straddling k = 4 gave |w| ≤ 5.51, against a true 2.21. Fixed by addendum 6 (the max over 25 kbox sub-boxes).
- The same attempt had a runner bug: the code hash was computed before the floats file existed, so it was empty.
  Only its engine-gate paths were affected, and it is fixed.
- After addendum 6, T1' was re-tested (PASS: bounds identical to the registered T1', engine gate 13/13) and the F1b
  control re-tested (PASS).
- **The rerun** (launched 16:28:33, PID 42556; Mac mini, nice 10, pause-only guard; rc 0): the precondition now
  PASSES, but the ρ = 4 row is **REJECTED**: "holomorphy box fails at (1.3213 + 0.2754i)". There was no verdict and
  no engine gate (no node file).

## Diagnosis (read-only, after the verdict; nothing rerun, nothing fixed)
- The refusal comes from v2's CRUDE dq bound (`dq_sup`) on one circle step box. v4 requires the crude bound to
  succeed before trying the centred one.
- v2's radial second-derivative bound `d2kc0` is NOT the cause: it certifies on that box × K, with Re(1 − kφ) ≥ 0.054
  along the ray.
- **G2 = f0² + c0² is not certified nonzero** on 12 of the 25 k-sub-boxes for a box of radius 0.01. On the same box at
  radius 0.003 it is certified on all 25.
- The true zeros are far: a float scan over the k-square finds the nearest zero of G1 or G2 to the circle 0.45 away
  (a p-point of G2 at 1.79 − 0.19i, for k = 4.056 + 0.106i).
- **So this is an enclosure-width artifact:** the v7 field's box enclosure of c0 (midpoint plus M·d²/2, with
  M = sup |c0''|) combined with the k-Taylor inflation is too wide at this step size near k = 4. It is not geometry.

## What it means
- **Pilot 1 FAILED.** The single segment [3.9, 4.0] at 3/5 is not certified by v7 at production width.
- **In production, a rejected row goes to the split rule.** Half-width segments mean a smaller k-box and less
  k-Taylor inflation; the step boxes are set by the walk. Whether that recovers this segment is UNTESTED, and the
  pilot's verdict stands.
- A tighter c0 box enclosure (for example, the field's Taylor series to higher order on the box instead of the
  M·d²/2 remainder) is a candidate fix for any later plan. It is NOT applied here.

## Cost (for the projection; the Bridge's point 4)
- First attempt: floats 14 s, prove 53 s.
- Rerun: floats 14 s, prove 58 s, including the sub-box precondition, which costs well under a second per call.
- No segment completed, so there is no measured core-h per certified segment from P1. T1' (k ≈ 1) took about 21 min
  per segment, full controls and engine included.
- Production segments straddling k = 4 at ρ = 4 (half-width 1/20): the 0.1-wide segments with centres from 3.95 up to
  the region-A/B switch. At 3/5 that is [3.9, 4.0] (and [4.0, 4.1] if region A were pushed past 4). Under the split
  rule each would become 2–4 segments.
