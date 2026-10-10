# Uncertainty exponent α of the survive/plunge boundary — pre-registration, 2026-10-10, BEFORE any α run

Ask: the Bridge, option B. Purpose: make §150's chaos claim quantitative with a single number per level, and
independent of the fd/S_ex detectors.

## Definition
- Sample x0 uniformly in a window W across the survive/plunge boundary of a level.
- x0 is UNCERTAIN at scale ε if the outcome (orbit status after 300 crossings: survive / plunge / escape) at x0
  differs from that at x0 − ε or at x0 + ε.
- The uncertain fraction scales as f(ε) ∝ ε^α:
  - **α = 1**: a smooth boundary of isolated points (expected for integrable Kerr);
  - **α < 1**: a fractal basin boundary (chaotic scattering / sticky layers).

The orbit settings are identical to the v2 scan: tol 1e-11, nsec 300, tmax 5e6, the scan's plunge cut, xmax 2000.

## Levels
- **TS** p = 4/5 (`ts45`), E = 0.97, L = 5.125: the level with the most confirmed (non-flip) chaotic orbits, 6.
- **Kerr** p = 4/5 (`kerr45`), E = 0.97, separatrix-matched: L_K = L_sep,K · (1 + ε_sep), where
  ε_sep = (5.125 − L_sep,TS)/L_sep,TS and L_sep comes from `find_Lsep` (as in the matched table). The Kerr level is
  built with the scan's own `_level_job` (coarse 60, dense 200).

## Window rule (fixed in advance)
In each level's INNER survive/plunge window: from the first to the last status change of the dense 200-point seeding,
padded by 2 dense steps on each side. (For the TS level that is ≈ [9.912, 9.942]; the dense seeding there already
shows 5 status changes.)

## Sampling and fit
- K = 1500 x0 per level (seeded); ε ∈ {3e-3, 1e-3, 3e-4, 1e-4, 3e-5}, nested, on the same x0.
- Samples with any step-capped or forbidden orbit are excluded and counted.
- α = the slope of log f against log ε, Poisson-weighted least squares, over the ε values with ≥ 10 uncertain samples.
  At least 3 such ε are required, otherwise INSUFFICIENT.
- 95% CI by bootstrap over x0 (1000 resamples).

## Predictions (sealed by this commit)
| level | prediction | confidence |
|---|---|---|
| Kerr (matched) | α within [0.85, 1.15], CI containing 1 | ~85% |
| TS | α < 0.85, with the CI excluding 1 | ~65% |

The TS confidence is lower because a thin layer can sit beside a smooth main boundary. Then f = c₁ε + c₂ε^α′, and the
fitted slope over this ε range can read close to 1 even with a fractal component.

## Reading rules
- **Kerr α CI excluding 1:** the instrument fails its control, and the TS number is not interpreted.
- **TS α CI excluding 1 with Kerr ≈ 1:** a fractal basin boundary, an independent quantitative confirmation of §150.
- **TS ≈ 1:** reported as is. It is not a refutation of §150 (see the caveat above), but it does NOT add confirmation.

## Fit validated offline before commit (synthetic outcome functions, same analyse(), K = 1500)
- Smooth: 3 isolated boundary points in a 0.03 window → α = 0.985, CI [0.913, 1.068].
- Fractal: middle-thirds Cantor boundary (expected α = 1 − log 2/log 3 = 0.369) → α = 0.337, CI [0.311, 0.363].
- TS window by the rule: [9.912067, 9.945202], 5 status changes, dense step 3.0e-3.
