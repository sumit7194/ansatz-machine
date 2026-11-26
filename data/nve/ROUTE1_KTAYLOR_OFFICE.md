# v4: k-Taylor starting values in the centred enclosure (office, 2026-11-26). Results, seal scorecard, controls

**Branch:** `office/2026-11-26-ktaylor`.

| commit | what |
|---|---|
| 5bcca66 | seal, pushed before any run |
| d08b1ca | code restored after the power cut |
| 6d411a8 | spin-3/5 outputs and equal-n verdicts |
| 7187b5b | per-step checkpoint and resume test |
| a75d7e3 | spin-9/10 outputs |

**Asked by** the Bridge. Proof stage only; one process, 1 core, nice 12.

## What changed (v3 → v4)
- **The z-series of dq/dk now gets its starting values in k-Taylor form, as Fable's v2 crude bound already does.**
  - At the step midpoint z_m, the values c0, c0′, ∂_k c0 and ∂_k c0′ are the POINT-k_c Laurent values, plus dk·∂_k,
    plus (dk²/2)·E.
  - E = `d2kc0(z_m, K)` encloses the second k-derivative on the whole k-square, by a radial integral on balls with
    Re(1 − kφ) > 0 certified. The remainder R₂ is ENCLOSED, not sampled.
  - This replaces v3's Laurent series evaluated at a k-ball, which inflated.
- **Everything else is v3's:** the closed-form z-series with k a ball, the outer-box Cauchy remainder, min(centred,
  crude), order 30.
- **The seal's design note had proposed a Cauchy estimate on the Laurent circle instead.** The radial-integral
  enclosure was chosen because it is already in v2's office-verified chain and needs no second Laurent tail.

## Results: optimised-gauge Dyson constants per unit k (k_c = 21/20)

| | v2 (as coded) | v3 (centred in z) | **v4 (+ k-Taylor)** | intrinsic (float) |
|---|---|---|---|---|
| 3/5 circle, point | 10.5 | 0.415 | **0.415** (= v3) | 0.36 |
| 3/5 lasso, point | 45.8 | 9.33 | **9.33** (= v3) | — |
| 3/5 circle, disc ρ = 4 | 14.3 | 4.30 | **1.039** | — |
| 3/5 lasso, disc ρ = 4 | 72.6 | 41.6 | **15.8** | — |
| 3/5 best (ρ, n), M_F | (4, 24), 6.6e10 | (4, 18), 1.5e7 | **(6.5, 12), 2.3e6**; at ρ = 4: n 14, 2.4e4 | — |
| 9/10 circle, point | 478 | 0.773 | **0.773** (= v3) | 0.65 |
| 9/10 lasso, point | 83.6 | 21.8 | **21.8** (= v3) | — |
| 9/10 circle, disc ρ = 3 | — | 669.5 | **8.62** | — |
| 9/10 lasso, disc ρ = 3 | — | 123.8 | **34.5** | — |
| 9/10 best (ρ, n), M_F | (3, 140), 4.7e62 | (3, 134), 1.8e60 | **(4, 18), 1.5e7** | — |

**Per-row detail for v4 at spin 9/10:**

| ρ | circle (per unit k) | lasso (per unit k) | n |
|---|---|---|---|
| 3 | 8.62 | 34.5 | 20 |
| 4 | 7.89 | 40.3 | 18 |
| 5 | 11.7 | 47.9 | 18 |
| 6.5 | 21.4 | 63.2 | 22 |

- The crude bound was kept on 29 of 37,700 (step, row) evaluations at ρ = 3.
- The run took 4070 s and peaked at 76 MB.

**Spin 3/5 at v4:** n = 16, 14, 12 and 12 at ρ = 3, 4, 5 and 6.5. The crude bound was kept on at most 8 steps in total.

## Controls (the Bridge's)
1. **The z-direction is unchanged.** The point constants are identical to v3's at both spins, to every printed digit.
2. **Spin 3/5 certifies at EQUAL n = 24** (ρ = 4, v2's own 25 nodes plus held-out; the node copy is byte-identical to
   v2's file). Every lower bound is ≥ v2's.

   | | \|F\| ≥ | \|tr M0\| ≥ | \|Im tr M1\| ≥ |
   |---|---|---|---|
   | v4 | 0.265334372 | 1.993158418 | 2.648820919 |
   | v3 | 0.265334299 | 1.993158418 | 2.648820919 |
   | v2 | 0.265023401 | 1.993158418 | 2.648820919 |

   - Every proved M is at or below v2's. For v4: M_F 2.4e4 against 6.6e10, M_trM0 2.26 against 9.22, M_trM1 38.7
     against 1.54e4.
   - The planted zero is refused, the held-out points are consistent, and the engine end values lie inside the
     enclosures.
   - The proved M_F still overestimates the sampled maximum by ×6.7e4 (v3: ×4.2e7).
3. **v3 reproducibility.** A clean checkout of 8b9971c regenerates `route1_seg_M_v3_nseg1.json` byte-identical. The v2
   outputs at their own commits were confirmed earlier (`ROUTE1_9_10_OFFICE_DIAG.md`).
4. **Restore fidelity after the power cut.** The spin-3/5 rerun reproduced every number logged before the cut.

## Seal scorecard (5bcca66)

| prediction | outcome |
|---|---|
| z-direction: point constants identical to v3, both spins | identical: **HIT** |
| 3/5 circle disc/point ratio 1.2–3; disc 0.5–1.3 | 2.50; 1.039: **HIT** |
| 3/5 lasso ratio 1.2–3; disc 11–28 | 1.70; 15.8: **HIT** |
| 9/10 circle ratio 1.2–5; disc 0.9–3.9 | **11.2; 8.62: MISS** (high) |
| 9/10 lasso ratio 1.2–5; disc 26–110 | 1.58; 34.5: **HIT** |
| n 3/5: 10–16 | 12: **HIT** |
| n 9/10: 14–32 | 18: **HIT** |
| P(n at 9/10 ≤ 40) = 80% | yes |
| 3/5 certifies at equal n = 24, every bound ≥ v2's | **HIT** (PASS on both clauses) |
| v2/v3 outputs reproducible | **HIT** (v3 byte-identical) |

- **The one miss is the 9/10 circle on the k-disc,** at 11× its point value against a predicted 1.2–5×.
  - The seal named the likely cause in advance: k-sensitivity near the inner poles, where √(1 − kφ) is small on the
    circle. It is not yet measured.
  - The lasso, which stays away from them, behaves as predicted.
- **n hit anyway,** because M_F is dominated by the lasso term.

## What this means
- **The enclosure artifact is now removed on both sides,** z and k. At spin 9/10 the certified segment needs 19 nodes
  instead of 141.
- **Cost of the full spin-9/10 segment verdict.** It needs 19 nodes, 3 held-out points and 8 ellipse points: about 30
  node evaluations at about 3 min each (Fable's 9/10 end nodes took 181–188 s). That is about 1.5–2.5 core-h, and it
  needs the Bridge's word.
- **Cost of a full region-A route-(i).** Each 0.1-wide segment costs about 1.1 h of proof plus about 1.5 h of nodes at
  this spin, and less at spin 3/5. It should be re-estimated per spin from these numbers, not from v2's.

## The power cut (2026-11-26, about 06:52)
- The first v4 worktree lived in /private/tmp and was cleared at boot. The code was restored verbatim from the session
  transcript (d08b1ca) and verified by reproducing every pre-cut number.
- New guard: per-step checkpoints, flushed and fsynced, with a resume test that passes (7187b5b).
- Branch note: `data/nve/ROUTE1_KTAYLOR_OUTAGE.md`.
