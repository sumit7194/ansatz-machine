# TS δ = 2 p-sweep of the §149 jet bound — pre-registration, 2026-10-11, BEFORE any new metric is built or run

Ask: the Bridge (the user wants every sister contributing to the TS/MN work). Question: is "no invariant Killing
tensor beyond trivial" special to p = 3/5 and 4/5 (§149), or does it hold across the TS δ = 2 family?

## Parameter points
p = (1 − t²)/(1 + t²) with t rational, so every metric component is rational (the `_ts2_build.py` construction).
Eight new points, four q-swap pairs (p ↔ q = √(1 − p²)), spanning p from 0.28 to 0.96:

| t | 2/3 | 3/5 | 3/7 | 2/5 | 1/4 | 1/5 | 1/7 | 3/4 |
|---|---|---|---|---|---|---|---|---|
| p | 5/13 | 8/17 | 20/29 | 21/29 | 15/17 | 12/13 | 24/25 | 7/25 |
| q | 12/13 | 15/17 | 21/29 | 20/29 | 8/17 | 5/13 | 7/25 | 24/25 |

## Metric generation (each must pass before it is used)
- `_ts2_build.py --t <t>`, the same Ernst construction as the sealed t1o2/t1o3 files:
  - the Ernst equation holds exactly;
  - TS R_ab = 0 exactly at 4 random rational points;
  - a perturbed TS metric is NOT vacuum (the test can fail);
  - Kerr through the same pipeline is vacuum;
  - m = 2σ/p and |J| = q m² are read off the asymptotics.
- `_ts2_kerr_control.py <t>` writes the Kerr control file at the same (p, q), vacuum re-verified before writing.
- A point whose build reports any FAIL is dropped and reported, not repaired silently.

## Jet runs (`_kt_jet.py`, unchanged since §149/§151)
- Valence d = 1..8, M = d, prime 0.
- Two physical points, x > 1 and |y| < 1: PA = (3, 1/3) (§149's second point) and PB = (17/10, 3/5). If the code
  refuses a point because a denominator vanishes there, it is reported and replaced by (5/2, −1/4).
- Any bound above trivial: rerun at M = d+1 and d+2, at prime 1 and at the other point, before any claim, then send to
  the Bridge for independent reproduction.
- Controls at EVERY p: Kerr (`ts2kerr:<p>`) at PA, d = 1..4 must give 2, 5, 8, 14 (Carter recovered). A Kerr failure
  at a given p voids that p's TS rows.
- Resources: rank engine on 2 threads, BLAS pinned, one process; started only when a core is free (the box is shared).

## Predictions (sealed by this commit)
| target | predicted | confidence |
|---|---|---|
| TS δ=2 at all 8 new p, d = 1..8, both points | bound = trivial (2, 4, 6, 9, 12, 16, 20, 25) | ~92% overall |
| Kerr control at all 8 p | 2, 5, 8, 14 | ~98% |

The residual risk is a special p with extra structure. None is known: Vollmer's and §149's nulls carry no p-dependent
mechanism.

## Scope of a null
The same as §149: invariant under ∂t, ∂φ; local near the point; smooth coefficients of any form; valence ≤ 8. A sweep
of 10 points (8 new plus 3/5 and 4/5) is evidence across the family, NOT a proof for all p.
