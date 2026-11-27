# P4-r at spins 3/10 and 4/5: result (Air, 2026-11-27), and the SEAL of the top-of-reach check

**Office ansatz-machine (Claude Opus).** Seal: `P4R_3_10_4_5_SEAL.md`, at e6bc4f4, committed before the run. Outputs
are copied back unchanged into `air_p4r_3_10_4_5/`, and their sha256 match the Air's copies.
- Code: unchanged, with manifest `MANIFEST_P4R_3_10_4_5.sha256`, verified on the Air before launch.
- Launched 14:29:26 on two spare Air cores (PIDs 45444 and 45445, from `logs/*.pid`). Both exited rc 0, at 14:34:57
  and 14:44:27.
- Peak footprint 90 MB. The guard never paused.

## Measured

| spin | k | engine \|F\| | Arb radius of F | ratio | trace margins (radius) |
|---|---|---|---|---|---|
| 3/10 | **1/640** (lowest segment's lower end) | 1.315e−7 | 5.684e−9 | **4.32e−2** | 2.0, 1.46 (≤ 8e−12) |
| 3/10 | 3/1280 | 2.958e−7 | 5.685e−9 | 1.92e−2 | same |
| 3/10 | 3/640 | 1.184e−6 | 5.689e−9 | 4.81e−3 | same |
| 3/10 | 3/40 | 3.058e−4 | 5.841e−9 | 1.91e−5 | same |
| 4/5 | **1/1280** (lowest segment's lower end) | 9.939e−8 | 1.040e−9 | **1.05e−2** | 2.0, 3.50 (≤ 1.2e−11) |
| 4/5 | 3/2560 | 2.236e−7 | 1.040e−9 | 4.65e−3 | same |
| 4/5 | 3/1280 | 8.948e−7 | 1.040e−9 | 1.16e−3 | same |
| 4/5 | 3/40 | 9.295e−4 | 1.051e−9 | 1.13e−6 | same |

The floats entries all have geo True. Walks: 2009/719 steps at 3/10, and 2744/820 at 4/5.

## Against the seal

| prediction | outcome |
|---|---|
| radius flat in k at each spin (factor 3) | flat to 3%: **HIT** both |
| radius at 3/10 in [5e−10, 1e−8] | 5.7e−9: **HIT** |
| radius at 4/5 in [5e−10, 1e−8] | 1.04e−9: **HIT** |
| \|F\| at 3/10, k = 1/640, in [0.78, 2.6]e−7 | 1.315e−7: **HIT** |
| \|F\| at 4/5, k = 1/1280, in [0.6, 2.0]e−7 | 9.94e−8: **HIT** |
| ρ_lo at 3/10 in [3e−3, 4e−2] | 4.32e−2: **MISS** (just above) |
| ρ_lo at 4/5 in [3e−3, 5e−2] | 1.05e−2: **HIT** |
| decision outcome 3/10 "≤ 1e−2" (P 55%) | no (4.3e−2): the 45% branch occurred |
| decision outcome 4/5 "≤ 1e−2" (P 45%) | no (1.05e−2, just over): the 55% branch occurred |
| trace margins > 1e3 × radii everywhere | ≥ 1e11×: **HIT** |
| geo True everywhere | **HIT** |
| wall time per spin 6–20 min | 3/10 5.5 min (**MISS**, under); 4/5 15 min (**HIT**) |
| peak footprint < 150 MB | 90 MB: **HIT** |

## What it means, by the sealed decision rule
Both spins fall in the "uncertain" band (1e−2 < ρ_lo < 5e−2), so this goes to the Bridge before launch.

**The binding test is harsher than the probe ratio.** The running 9/10 production, at [1/160, 1/80], had a probe
ratio of 1.9e−2 at its centre. But its verdict's worst node ratio (largest node radius / smallest |f|) was 0.21, and
it was radius-limited. The two segments above it certified at worst-node ratios of 0.037 and 0.008. So the verdict's
node enclosures are roughly 10× wider than the bare probe radius, and the cut lies somewhere between worst-node 0.04
and 0.2.

**Expected outcome:**
- **3/10:** worst-node ratio about 0.4 on the lowest segment [1/640, 1/320], so it is likely radius-limited. The next
  segment up, [1/320, 1/160], has about 0.1, so it likely certifies. Expected reach [1/320, 3]. That leaves a gap of
  **[2.79e−3, 3.13e−3]** above Statement A, a few percent of ε_a.
- **4/5:** worst-node ratio about 0.1 on [1/1280, 1/640]. That is at the cut, so it may or may not certify. If not,
  the reach is [1/640, 3], with a gap of **[8.39e−4, 1.56e−3]**.
- In both cases the driver's radius-limited stop handles it without splitting, and the gap is reported plainly. The
  traces are no obstacle.

## SEAL: top-of-reach check (sealed here, before it runs; the premortem's cheap first check)

**Why.** The likeliest way these productions get wasted is a walk-side stop below k = 3, as at 9/10 (between k_c 2
and 3). The check: one v6 PROVE stage, with no verdict, on the production's last segment [29/10, 3] (k_c 59/20).
- It uses the driver's own `env_for` settings (ρ = 4, mode F, tol rel), so production reuses the checkpoint.
- Runners `air/top_3_10.sh` and `air/top_4_5.sh`, one core each, nice 15, under `job.sh`.
- Manifest `MANIFEST_TOP_3_10_4_5.sha256`.

| prediction | P |
|---|---|
| 3/10: an admissible row (precondition passes, finite M_F), n in [12, 24] | 75% |
| 4/5: an admissible row, n in [14, 30] | 60% |
| 4/5: no admissible row (the walk-side stop seen at 9/10) | 25% |
| F1 never fires; both exit rc 0 (a rejected row also exits 0) | 95% |
| wall time: 3/10 5–15 min, 4/5 8–25 min (floats included) | 75% |
| peak footprint < 150 MB | 95% |

**If 4/5 has no row at 59/20,** the expected 4/5 reach stops below 3. I report that before launch, with the scope
question for Sumit.
