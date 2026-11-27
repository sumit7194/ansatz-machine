# Route (i) production at spin 3/5: result (Air, 2026-11-27)

**Office ansatz-machine (Claude Opus), owner of `~/GitHub/ansatz-air` since 2026-11-27 afternoon.** The seal is
`PROD_SEAL.md`, written by the personal session and committed with the runners and manifest before launch. The run
used registration §5A (main, d1c24d6).

**Outputs:** copied back unchanged into `air_prod_3_5/`, and their sha256 equal the Air's copies (6 files). They are:
- the driver log `route1_prod_3_5.out`;
- the state `route1_prod_3_5_state.jsonl`;
- the floats `route1_floats_prod_3_5.json`;
- the job, guard and footprint logs.

**The run:**
- launched 2026-11-27 04:49:08 as PID 36413 (from `logs/prod_3_5.pid`);
- exited rc 0 at 20:44:42;
- one Air core, nice 15, under the pause-only guard, which never paused.

## Result

**Certified: for every real k in [1/640, 3] at spin 3/5, F(k) ≠ 0, tr M0 ≠ 0 and tr M1 ∉ [−2, 2].** This covers the
target [ε_a, 3] (ε_a = 1.92e−3; 1/640 = 1.5625e−3). The driver's last lines:

    batch rerun of every certified verdict: identical True
    REACH (identical reruns only): certified contiguous [1/640, 3] = [1.5625e-03, 3.0]; covers the target [eps_a, 3]: True

- **Segments:** 35, all certified at depth 0, with no splits, no stop rule and no radius-limited stop.
  - 6 dyadic segments in mode F/k²: [1/640, 1/320] up to [1/20, 1/10], with n 16–20.
  - 29 segments 0.1 wide in mode F: [1/10, 1/5] up to [29/10, 3].
    - n is 16 at the bottom, falls to 12 over [4/5, 11/5], and rises to 18 at the top.
- **The engine gate:** 36 of 36 gate runs had every node value inside its enclosure. That is one per segment, plus a
  second run on the pilot segment [1/640, 1/320]: once in the pilot and again when production resumed it.
- **Full controls:** passed on the first segment of each mode ([1/20, 1/10] in F/k², [1/10, 1/5] in F):
  - the planted zero was refused;
  - the held-out node broke nothing;
  - the shrunken-M control was caught by the sampled-maximum check, and the planted precondition fired.
- **No ALARM and no Traceback.**
- **Smallest proved lower bound:**
  - upward chain: |F| ≥ 2.21e−3 on [1/10, 1/5], where F is small (F ≈ c2 k² near k = 0);
  - dyadic chain: |F/k²| ≥ 0.184 on [1/640, 1/320].
- **Cost:**
  - production wall time 15.9 h, at 22–36 min per segment;
  - the pilot segment [1/640, 1/320] (run 02:31–04:49) was reused from its checkpoint in 54 s;
  - peak footprint 90 MB.

## Against the seal (the 3/5 rows; the 9/10 rows wait for its result)

| prediction | outcome |
|---|---|
| no ALARM, engine miss or gate stop (both spins, 90%) | 3/5: **holds**; 9/10 still running |
| 3/5 covers [ε_a, 3] (75%) | **HIT** |
| 3/5 splits 0–3 (75%) | 0: **HIT** |
| batch rerun byte-identical and full controls passed per mode (both spins, 95%) | 3/5: **holds**; 9/10 pending |
| wall time 3/5 18–30 h (70%) | 15.9 h: **MISS** (under; 18.2 h counting the pilot from 02:31) |
| peak footprint < 150 MB (95%) | 90 MB: **HIT** |
| surprise: a split below k = 1 | did not happen |

## What it means, and what it does not

- **Together with Statement A** (0 < |k| ≤ ε_a, certified separately), the lower axis at spin 3/5 is now covered by
  interval certificates from k = 0 to k = 3, with no gap. Statement A's interval and this one overlap on
  [1/640, ε_a].
  - This holds for the three conditions above, under the applicability chain, and with registration §5A's settings.
  - It is part of region A, not all of it. The top of region A (k > 3) is parked, and the method's own ceiling is near
    3.7–3.8.
- It does not change claim v3.1. "Only Kerr" along the lower axis stays a numerical result. Route (i) stays internal
  until the release notes say otherwise and Sumit approves them.
- The 9/10 production (bottom at 1/80, a sealed miss) and the 3/10 and 4/5 productions are still running, and are
  reported separately.

**Environment:**
- MacBook Air M1, 8 cores; one core at nice 15;
- arithmetic under `.venv313`: Python 3.13.18, python-flint 0.9.0;
- floats under `.venv`: Python 3.14.10;
- code v6, the engine gate and the driver, byte-identical to `MANIFEST_PROD.sha256`.
