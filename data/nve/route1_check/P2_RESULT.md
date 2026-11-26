# RESULT: pilot P2, the proof stage at k_c = 21/20 for spins 3/10 and 4/5

**ansatz-machine-personal (Claude Opus), 2026-11-26.** Seal: `P2_SEAL.md`, with its amendment, which says P2 runs
on v4 because T1 failed on 7f96efc. Runner `air/p2.sh` v2, manifest `MANIFEST_P2_4bc2ebd`. Outputs were copied from the
Air into `air_p2/` and are committed unchanged: the floats JSONs, the v4 rows, the proof JSONs, the dq checkpoints and
the logs.

**Environment:** MacBook Air on the loaded fleet, one process, nice 15, pause-only guard (`job.sh` v2; the guard never
paused it). Floats ran on `.venv`: Python 3.14.10, python-flint 0.9.0, mpmath 1.3.0. The proof ran on `.venv313`:
Python 3.13.18, python-flint 0.9.0, prec 256 bits. Code: `_nve_route1_segment_v4.py` as committed at c2dd39c,
unchanged. Start 18:17:26, `JOB_EXIT 0` at 19:18:49. Peak RSS 38 MB and 37 MB.

**P2 measures cost. It certifies nothing**, since the verdict stage was not run.

## The rows (v4 rule; constants per unit k; every row admissible, precondition `ok` True)

| spin | ρ | c0 (circle) | c1 (lasso) | n |
|---|---|---|---|---|
| 3/10 | 3 | 0.154 | 8.717 | 16 |
| 3/10 | 4 | 0.173 | 9.715 | 14 |
| 3/10 | 5 | 0.197 | 10.935 | 12 |
| 3/10 | 6.5 | 0.241 | 13.249 | **10 (chosen)** |
| 4/5 | 3 | 1.753 | 26.079 | 18 |
| 4/5 | 4 | 2.526 | 29.903 | 16 |
| 4/5 | 5 | 3.801 | 34.868 | **16 (chosen, M_F ≤ 1.213E+7)** |
| 4/5 | 6.5 | 6.484 | 44.727 | 18 |

- **Reference walks.** At 3/10, 1,988 circle steps and 725 lasso steps. At 4/5, 2,679 and 796.
- **K-point z-direction control.** At 3/10, circle 1.041E-1 and lasso 6.022E+0. At 4/5, 6.287E-1 and 1.698E+1.
- **Wall time.** The proof stage took 1,433 s (23.9 min) at 3/10 and 2,026 s (33.8 min) at 4/5. Floats took 28 s and
  174 s.
- **The floats selftests.** Every dq/dk finite-difference check printed `ok` (the `route1_seg_*_v2.out` files), and
  `geo True` at both spins.

## Against the seal

| sealed prediction | measured | |
|---|---|---|
| geometry_ok True at both spins (P = 95%) | True, True | hit |
| all four rows admissible (P = 85%) | 4/4 at both spins | hit |
| c1 at ρ = 4: 3/10 in 7–15 (point 10) | 9.715 | hit |
| c1 at ρ = 4: 4/5 in 18–35 (point 25) | 29.903 | hit |
| c0 at ρ = 4: 3/10 in 0.2–2 | **0.173** | **miss (just below)** |
| c0 at ρ = 4: 4/5 in 1–6 | 2.526 | hit |
| n: 3/10 in 8–12 (point 10) | 10 | hit |
| n: 4/5 in 12–18 (point 14) | 16 | hit |
| chosen ρ: 3/10 in {5, 6.5} | 6.5 | hit |
| chosen ρ: 4/5 in {4, 5, 6.5} | 5 | hit |
| circle walk steps: 3/10 in 1,000–3,000 | 1,988 | hit |
| circle walk steps: 4/5 in 3,000–10,000 | **2,679** | **miss (below)** |
| proof time: 3/10 in 8–25 min | 23.9 min | hit |
| proof time: 4/5 in 15–60 min | 33.8 min | hit |
| F1 row | not applicable (v4 has no F1 gate; see the amendment) | — |

**The ordering (P = 85%) holds in full.** For n, 10 (3/10) ≤ 12 (3/5) ≤ 16 (4/5) ≤ 18 (9/10). For c1, the order
3/10 < 3/5 < 4/5 < 9/10 holds at every ρ: 8.7 < 14.0 < 26.1 < 34.5 at ρ = 3, 9.7 < 15.8 < 29.9 < 40.3 at ρ = 4,
10.9 < 18.1 < 34.9 < 47.9 at ρ = 5, and 13.2 < 22.6 < 44.7 < 63.2 at ρ = 6.5. The 3/5 and 9/10 rows are the committed
v4 rows (`data/nve/eps/route1_seg_M_v4_nseg1.json`, `route1_seg_M_v4_9_10_nseg1.json`).

Nothing the seal named as surprising happened: no row was rejected, and the 3/10 circle constant is smaller than 3/5's,
not larger.

## The two misses, plainly

1. **c0 at 3/10 is 0.173 against a floor of 0.2.** The seal said c0 "has no clean scaling" and gave a wide range. The
   circle constant falls faster from 3/5 to 3/10 (1.04 to 0.17, a factor of 6) than I allowed for. It does not change
   n, because the lasso term dominates the ATAP bound at every spin measured.
2. **The circle walk at 4/5 took 2,679 steps against a floor of 3,000.** I interpolated walk length between 3/5 (2,163)
   and 9/10 (17,955) as if it grew smoothly. It does not: 3/5 to 4/5 adds only 24%. Most of 9/10's walk comes from
   something that sets in between 4/5 and 9/10. For the cost redo, this means the 9/10 walk length is not a guide to
   the spins below it.

## What it buys the cost redo

At k_c = 21/20, the number of Chebyshev points per segment is now measured at four spins: 11, 13, 17, 19 (n + 1). The
proof-stage time per segment on the loaded Air is 24 min at 3/10 and 34 min at 4/5, for all four ρ rows together. The
log prints 316–379 s per row at 3/10 and 475–484 s at 4/5. I have not split out how much of that a single chosen row
would cost on its own, so the cost redo must measure it, not infer it. How the constants grow with k is P3's
question.
