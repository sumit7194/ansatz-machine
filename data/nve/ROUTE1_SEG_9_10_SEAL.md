# SEALED prediction: the v2 certified-segment procedure at spin 9/10 (written before any spin-9/10 run)

**[model: Fable 5.2] UNVERIFIED.** 2026-11-26, 04:33 local. The Bridge's last task of the window: run
`scripts/_nve_route1_segment_v2.py` at spin 9/10, E = 4/5, real k ∈ [1, 11/10], circle R0 = 1.2639, the engine's
lasso of k_c = 21/20 fixed. Nothing at spin 9/10 has been run in this round when this file is committed: no engine
reference, no proof stage, no point evaluation.

## What I know going in

- Spin 3/5, measured tonight: Dyson constants at k_c (optimised gauge, K a point) 45.8 (lasso) and 10.5 (circle);
  on the certified k-disc 72.6 and 14.3; n = 24 at ρ = 4.
- Spin 9/10 was the hardest spin in Part A (certified radius 18 times smaller than at 3/5). I have no value of F,
  of the singular points or of the lasso at spin 9/10 near k = 1.

## Predictions

| quantity | prediction | range I would not be surprised by |
|---|---|---|
| lasso Dyson constant at k_c (optimised gauge, point) | 150 | 80 to 400 |
| circle Dyson constant at k_c (optimised gauge, point) | 40 | 20 to 120 |
| best ρ among those tried | 3 | 3 or 4 |
| node count n for the 1e−3 target | 50 | 30 to 90 |
| Laurent-disc precondition on the k-box | certifies | (the roots do not depend on the spin in w = z²/a²) |
| the proof stage gives a finite proved M at some ρ | 80% | |
| VERDICT: CERTIFIED, reached inside tonight's window (by about 05:25) | 30% | |
| VERDICT: CERTIFIED, if the node evaluations were allowed to finish | 65% | |

## Reasons

- **Larger constants.** c0 scales with a, so dq/dk scales roughly with a²: (0.9/0.6)² = 2.25. The geometry is
  tighter as well: the circle at 1.2639 sits between the ring |z| = 0.9 and r₊ = 1.436, so q and its k-derivative are
  larger on both loops. I guess another factor 1.5 to 2 on top.
- **Node count.** With the measured model n ≈ [ln(4g²/((ρ − 1)·tol)) + 2c·0.05·(ρ + 1/ρ)/2] / ln ρ and c about
  1.5 × (150 + 40) on the box, ρ = 3 gives n ≈ 55.
- **Why the certificate may not come tonight.** About 60 to 70 point evaluations at 30 s or more each is 30 to 45
  minutes, and about 35 are left after setup. Other risks: a holomorphy box failing where the capsule passes close to
  a singular point; the Laurent tail converging slowly (|ω| up to 0.93 of the Laurent radius on step boxes of the
  circle, against 0.5 at spin 3/5); |F| on the segment being small against the 1e−3 target.
- **If the run is cut short,** the node file resumes: the office can finish it.
