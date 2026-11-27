# Route (i) production at spin 3/10: result (Air, 2026-11-28)

**Office ansatz-machine (Claude Opus).** The seal is `PROD_SEAL_3_10_4_5.md` §2, committed before launch with its
runner and manifest (8d94f79). The scope was Sumit's, via the Bridge: [ε_a, 3], with any small-k gap stated plainly.

**Outputs:** copied back unchanged into `air_prod_3_10/`, with sha256 equal to the Air's copies (6 files).

**The run:**
- launched 2026-11-27 14:59:39 as PID 52798 (from `logs/prod_3_10.pid`);
- exited rc 0 at 2026-11-28 05:04:36;
- one Air core, nice 15, under the pause-only guard, which never paused.

## Result

**Certified: for every real k in [1/320, 3] at spin 3/10, F(k) ≠ 0, tr M0 ≠ 0 and tr M1 ∉ [−2, 2].** It does NOT cover
the target [ε_a, 3], whose lower end is ε_a = 2.79e−3. **The gap is [2.79e−3, 3.125e−3]**, a sliver just above
Statement A, about 12% of ε_a. The driver's last lines:

    batch rerun of every certified verdict: identical True
    REACH (identical reruns only): certified contiguous [1/320, 3] = [3.1250e-03, 3.0]; covers the target [eps_a, 3]: False

- **The downward chain** (mode F/k²):
  - 5 dyadic segments certified, [1/320, 1/160] up to [1/20, 1/10], with n 18–22.
  - [1/640, 1/320] stopped by the **radius-limited rule**, without splitting. Its node radii alone defeat the
    condition: the largest node radius of F/k² is 3.03e−2, against a smallest |F/k²| of 4.18e−2.
  - So this is the Arb evaluator's floor, not interpolation error. A finer split cannot cure it.
- **The upward chain** (mode F): 29 segments 0.1 wide, [1/10, 1/5] up to [29/10, 3], all certified at depth 0, with
  n = 14–18 and no splits.
  - [29/10, 3] reused the top check's checkpoint.
- **The engine gate:** 34 of 34 gate runs, one per certified segment, each with every node value inside its
  enclosure.
- **Full controls:** passed on the first segment of each mode.
- **No ALARM and no Traceback.**
- **Smallest proved lower bound:**
  - upward chain: |F| ≥ 5.43e−4 on [1/10, 1/5], where F ≈ c2 k² is small;
  - downward chain: |F/k²| ≥ 2.89e−2 on [1/320, 1/160].
- **Cost:**
  - wall time 14.1 h;
  - downward segments about 36 min each, upward 20–26 min;
  - peak footprint 90 MB.

## Against the seal (`PROD_SEAL_3_10_4_5.md` §2)

| prediction | P | outcome |
|---|---|---|
| no ALARM, engine miss or gate stop | 90% | **HIT** |
| the downward chain stops radius-limited at [1/640, 1/320]; reach [1/320, 3]; gap [2.79e−3, 3.13e−3] | 60% | **HIT**, exactly |
| the downward chain certifies to the bottom | 25% | did not happen |
| it stops higher than [1/640, 1/320] | 15% | did not happen |
| upward chain completes to 3 with 0–2 splits | 80% | 0 splits: **HIT** |
| n on the upward chain within [10, 20] on every segment | 80% | 14–18: **HIT** |
| batch rerun byte-identical, full controls passed per mode | 95% | **HIT** |
| wall time 11–25 h | 70% | 14.1 h: **HIT** |
| peak footprint < 150 MB | 95% | 90 MB: **HIT** |
| 25% check-in (2026-11-27 18:45): projected about 18 h, no re-gate | — | actual 14.1 h |

## What it means, and what it does not

- **At spin 3/10, (0, 3] is covered by interval certificates except the sliver [2.79e−3, 3.125e−3].**
  - Statement A covers (0, ε_a]; this production covers [1/320, 3].
  - The sliver is numerical only, covered by the registered 50-digit counts, like the rest of region A.
  - All of this is relative to the applicability chain, with registration §5A's settings.
  - It is part of region A, not all of it; the top (k > 3) is parked, and is the subject of the v7 plan draft.
- **The gap is the evaluator's own floor.** Closing it needs tighter node enclosures, not more segments. It is listed as
  a separate item in `V7_PLAN_DRAFT.md` §7.
- **Claim v3.1 is unchanged.** Route (i) stays internal until notes say otherwise, on Sumit's go via the Bridge.

**Environment:**
- MacBook Air M1; one core at nice 15;
- arithmetic under `.venv313`: Python 3.13.18, python-flint 0.9.0;
- floats under `.venv`: Python 3.14.10;
- code v6, the engine gate and the driver, byte-identical to `MANIFEST_PROD_3_10.sha256`.
