# C2-M production at spin 3/5, region B (the Bridge's value-gate ruling (A), 2026-11-28). Committed BEFORE any segment runs
**Office ansatz-machine.** Ruling (A): GO for Pmid-size segments over the uniform part plus the dyadic segments that H1 can reach. Each segment's certificate stands alone, with C2-M's full controls. 4 cores, nice 10, pause-only guard. Check in at about 25%.

## What runs: 35 segments, `C2_PROD_MANIFEST.txt` (lane, label, k_c, half)
- **Uniform part [4.0, 30/7 − 1/500], in 29 pieces:**
  - U00 = [4.0, 4.005];
  - U01–U27, centres 4.01 to 4.27, half 1/200;
  - U28 = [4.275, 30/7 − 1/500], half 61/14000.
  - U15 is Pmid's segment [829/200, 831/200], already certified, so it is not re-run. **28 run.**
- **Dyadic chain:** D1–D7 = [30/7 − 2d, 30/7 − d] with d = 1/(1000·2^j), j = 1..7, half d/2. **7 run.**
  - D0 is P3, already certified.
  - D7 reaches 30/7 − 7.8125e−6. Below that, base2's H1 guard refuses (d* = 7.08e−6), and that is ruling (B)'s job: j = 8..27, 20 segments, down to the 3/5 sliver δ0 = 1.37e−11 (erratum E-δ0, `C2_PRODUCTION_ESTIMATE.md`).
- **Floats entries:** one per k_c, from the committed region-B geometry rule (`_nve_v7_floatsB.py`, unchanged), generated before any segment runs and committed with this file.
  - An entry whose geometry guard fails (`geometry_ok` False) is recorded, and its segment is not run.

## How each segment runs: `air/c2m_segment.sh LABEL KC HALF`
- **The code under test is C2-M's, unchanged.** CODE is the same hash as Pmid's (the runner is not in it).
- **The sequence is the pilot's:** M3 (dry), the cover (refinement rule, R/20 STOP), M1, the v6 verdict with full controls, M2F, M2T0, M2T1, M4, engine gate B.
- **Two runner changes only** (the read covers them):
  1. **The runner defect is fixed.** If the cover did not end with every cell accepted (stop set, or no leaves), the later stages are SKIPPED and the segment is recorded as STOPPED. Pend ran them on an empty cover.
  2. **The pilot's pause of the old lane-B child (a fixed PID) is removed.** That process is gone, and the PID could now belong to anyone.
- **After the non-author glance (2026-11-29), three guards were added; each is exercised on known cases:**
  - the registration's geometry rule is enforced: no floats entry, or `geometry_ok` not True, means the segment is not run (exit 4) (F2);
  - the segment's cover JSON is deleted before the cover runs, so a stale file can never be read as this run's (F3);
  - acceptance needs `stop` null, `n_leaves` > 0 and the cover's `code` equal to this run's CODE. A missing key or file fails closed. Tested: Pmid's cover is accepted, Pend's is rejected, and a missing file or floats entry gives a skip.
- **Lanes:** `air/c2m_prod.sh A|B`. Two lanes, each running its segments in manifest order, one at a time, with 2 cover workers each, so 4 cores.
  - Each lane runs under `air/v7_job.sh` (pause-only: memory pressure or low disk SIGSTOPs the tree; nothing is killed).

## The reading, fixed now
- **A segment CERTIFIES** when its verdict is CERTIFIED with no ALARM, M1 passes, the M2 plants each ALARM, M4 trips, and the engine gate passes. Exactly the pilots' bar.
- **Any other outcome is recorded with its reason, and the lane goes on.** The segment's stretch stays at the numerical grade. No retry, halving or change runs without a ruling.
- **The reported reach** is the exact union of the certified segments, with P3 and Pmid. The uncovered stretches are named.

## Check-in and kill criteria
- **Check-in at about 25%** (about 9 segments done): the per-segment wall times, the outcomes, and a projection, sent to the Bridge.
- **Projection:** about 1.1 h wall per segment per lane (as P3 and Pmid), so about 20 h for 35 segments on 2 lanes.
- **STOP and re-gate** if any of these happen:
  - an engine-gate miss or an ALARM on an unplanted verdict;
  - more than 3 of the first 9 segments not certifying;
  - the projection exceeding 40 h.

## Predictions (before any run)
- The floats geometry is ok for all 35: 90%.
- U00–U28 certify: 75% all, 95% at least 24 of 28. The clearance is lowest near the ends of the uniform part, so the likeliest failures are there.
- D1–D7 certify: 60% all. The near-end caveats (node precision against |F|, the outer branch point) are untested below d = 1e−3.
- Wall time within 30 h: 75%.
