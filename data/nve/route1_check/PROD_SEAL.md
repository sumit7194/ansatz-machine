# SEAL: route (i) production at spins 3/5 and 9/10 (committed with its runners and manifest before launch)

**ansatz-machine-personal (Claude Opus), 2026-11-27.** The order's steps 2 and 3. Code: v6, the engine gate and the
driver, as tested in `T6_RESULT.md` (1c21a2d); the production code hash is the one the pilots used. Registration §5A
(main, d1c24d6).

## The value gate, in one plain paragraph

**What it certifies:** at spin 3/5, every real k from Statement A's edge (ε_a = 1.92e−3) up to k = 3; at spin 9/10,
every real k from wherever the small-k limit stops it (expected near k ≈ 1e−3 to 2e−3; P4-r measured that limit) up to
k = 2. On that range, F(k) ≠ 0, tr M0 ≠ 0 and tr M1 ∉ [−2, 2]. Each is proved by interval arithmetic and checked
against a second, independent 50-digit engine at every node. It is a partial result: part of region A, stated as such.
At 9/10 there is a gap of about [1e−4, 2e−3] just above Statement A, stated plainly, and the top of region A is parked.

**Cost, measured by the pilots on the loaded Air:**
- 3/5: about 38 min per segment, 6 dyadic + 29 segments, so about 23 h on one core.
- 9/10: about 3 h 10 min per segment, about 6–7 dyadic + 19 segments, so about 3–3.5 days on a second core.
- Splits add to both.

**Stop rule:**
- **Splitting:** a segment that will not certify is halved at most twice.
- **Stop rule:** if it still fails, that chain stops there, and the reach actually achieved is reported.
- **Radius-limited:** a failure that would persist even with zero interpolation error stops its chain at once.
- **Correctness:** any correctness alarm (a failed control, an engine miss, a gate) stops the run for a decision.
- **No new code is written mid-run.**

## What runs

`air/prod_3_5.sh` and `air/prod_9_10.sh`, one per Air core, each one process at a time, nice 15 under `job.sh`, with
footprint logged by `fp.sh`. Each runs `_nve_route1_production.py` for its spin:

| | PROD_EPS (ε_a, claim v3.1) | PROD_TOP | R1_R0 | dyadic (F/k²) + 0.1-wide (F) segments |
|---|---|---|---|---|
| 3/5 | 1.92e−3 | 3 | 1.35 | 6 + 29 |
| 9/10 | 1.06e−4 | 2 | 1.2639 | 10 + 19 (the downward chain is expected to stop early) |

Production reuses the pilots' checkpoints (same code hash, same file names): 3/5 [1/640, 1/320] and 9/10 [1/20, 1/10]
resume without new evaluations. It also reuses P4-r's floats entries.

## Predictions

| | prediction | P |
|---|---|---|
| no ALARM, no engine miss, no gate stop, at either spin | holds | 90% |
| 3/5 covers its target [ε_a, 3] (covers_target True) | yes | 75% |
| 3/5 splits | 0–3 | 75% |
| 9/10 downward chain | stops by the radius-limited rule (not DMAX), at a dyadic segment with k_c in [3/2560, 3/640] | 70% |
| 9/10 reach, lower end | in [1/1280, 1/320] (7.8e−4 to 3.1e−3) | 70% |
| 9/10 reach, upper end | 2 (the upward chain completes) | 80% |
| batch rerun byte-identical, full controls passed per mode | both spins | 95% |
| wall time | 3/5: 18–30 h; 9/10: 2.5–4 days | 70% |
| peak footprint | under 150 MB per process | 95% |

**What would surprise me:**
- 9/10 certifying a segment that P4-r called radius-limited (k_c 3/2560 or below).
- Any ALARM.
- 3/5 needing a split below k = 1.
