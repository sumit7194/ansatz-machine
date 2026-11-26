# The centred enclosure of dq/dk (office build, 2026-11-26): results, seal scorecard, next fix

**Branch:** `office/2026-11-26-centred-encl`:
- seal 67c7661, committed before any run;
- code and outputs 8b9971c.
**Builds on** Fable's v2 (d18de63), imported unchanged. The v2 outputs at d855810 and d18de63 stay byte-reproducible
from their own commits (shown in `ROUTE1_9_10_OFFICE_DIAG.md`).

## What was built (`scripts/_nve_route1_segment_v3.py`)
- **The bound, per step segment and per k-sub-box.** A Taylor series of dq/dk in z at the POINT step midpoint, to order
  30, with k a ball over the sub-box.
- **Its remainder.** A Cauchy remainder from an outer box 2× (else 1.5×) wider, bounded by v2's own crude `dq_sup`,
  which also certifies holomorphy.
- **Never weaker than v2.** The per-step value is min(centred, v2 crude), so v3 is never weaker than v2.
- **A first try (order 10, outer box 4×/2×) was stopped and measured.** The 4× box does not certify, and at order 10
  the remainder from the 2× box dominated. The fix was order 30 (`ROUTE1_9_10_OFFICE_DIAG.md` has the profile; this
  note has the numbers).

## Results: optimised-gauge Dyson constants per unit k at k_c = 21/20

| | v2 as coded (Fable) | **v3 centred (office)** | intrinsic (office float) |
|---|---|---|---|
| spin 3/5, circle, at the point k_c | 10.5 | **0.415** | 0.36 |
| spin 3/5, lasso, at the point k_c | 45.8 | **9.33** | not measured |
| spin 3/5, circle, on the k-disc (ρ = 4) | 14.3 | **4.30** | — |
| spin 3/5, lasso, on the k-disc (ρ = 4) | 72.6 | **41.6** | — |
| spin 3/5, chosen (ρ, n), M_F | (4, 24), 6.57e10 | **(4, 18), 1.54e7** | — |
| spin 9/10, circle, at the point k_c | 478 | **0.773** | 0.65 |
| spin 9/10, lasso, at the point k_c | 83.6 | **21.8** | not measured |
| spin 9/10, circle, on the k-disc (ρ = 3) | (v2 row ρ = 3) | 669.5: **no gain** | — |
| spin 9/10, lasso, on the k-disc (ρ = 3) | | 123.8 | — |
| spin 9/10, chosen (ρ, n), M_F | (3, 140), 4.7e62 | (3, 134), 1.83e60 | — |

**Control: spin 3/5 CERTIFIES with v3** (`scripts/_nve_route1_v3_verdict.py`, which is Fable's unchanged v2 nodes and
verdict stages, all-ball evaluator; n = 18; 19 nodes plus controls). For every real k ∈ [1, 1.1]:
- |F| ≥ 0.265035987, BETTER than v2's 0.265023401;
- |tr M0| ≥ 1.993158418, the same;
- |Im tr M1| ≥ 2.648820906, 1.3e−8 below v2's margin of 2.648820919. That is the cost of choosing 18 nodes instead of
  24, not a weaker bound: every proved M is smaller (M_F 1.5e7 against 6.6e10, M_trM0 3.22 against 9.22, M_trM1 667
  against 1.54e4).

The planted zero is refused, the held-out points are consistent, the proved M is at least the sampled values, and the
engine end values lie inside the node enclosures.

## Reading
- **At the POINT k_c the centred enclosure reaches the intrinsic constants.** The circle is within 15% at spin 3/5
  and 19% at spin 9/10. This confirms the diagnosis: the z-direction wrapping is gone.
- **On the k-DISC, k is now the bottleneck.** The Laurent series of c0, evaluated with k as a ball over a sub-box,
  inflates.
  - At spin 9/10, c0 at the step midpoint gets an enclosure radius of 0.08–4.2 for a k half-width of 0.017, while c0
    itself is about 0.01–0.07. The radius shrinks only linearly with the k-width.
  - So at spin 9/10 the centred series failed or lost on about 75% of (step, k-sub-box) pairs. v3 then kept the crude
    value, and n stayed at 134.
  - At spin 3/5 the k-effect is milder: the disc constants are 4.3 and 41.6, against 0.4 and 9.3 at the point.

## Seal scorecard (67c7661)

| prediction | outcome |
|---|---|
| circle 3/5 on the disc: 0.4–3 | 4.30: **MISS** (above; the point value 0.415 is in range) |
| lasso 3/5 on the disc: 5–40 | 41.6: **MISS**, narrowly |
| circle 9/10 on the disc: 0.7–10 | 669: **MISS** (the point value 0.773 is in range) |
| lasso 9/10 on the disc: 5–60 | 124: **MISS** (the point value 21.8 is in range) |
| n 3/5: 10–18 | 18: **HIT** |
| n 9/10: 12–40 | 134: **MISS** |
| P(n at 9/10 ≤ 40) = 75% | no |
| spin 3/5 certifies, no weaker | **HIT** (every M smaller; F bound better; tr M1 margin −1.3e−8 from the node choice) |

**Why the seal missed.** I predicted the k-disc behaviour from the point behaviour and did not foresee the k-ball
inflation of the Laurent series. A lesson: seal the k-direction separately from the z-direction.

## The next fix (designed, not built): Taylor in k with point Laurents
1. Write c0(z; k) = c0(z; k_c) + (k − k_c)·∂_k c0(z; k_c) + R₂. The first two terms come from POINT-k_c Laurent series,
   which are precise.
2. Bound R₂ with Cauchy's estimate on the Laurent circle, using the CLOSED FORM
   ∂²_k c0″ = c_K″·(−φ²/4)(1 − kφ)^{−3/2} evaluated on arcs with k a box. That is a short formula, not a 190-term
   series, so it does not inflate.
3. The coefficients of the second k-derivative are then at most M2·r_w^{−n}, so |R₂| ≤ |k − k_c|²/2 · M2 θ⁴/(6(1 − θ)|w|²).
   ∂_k c0 = D0 + (k − k_c)·(the same kind of bound) follows likewise.
4. Feed these as series plus a remainder ball into the z-centred series. The outer-box Cauchy remainder must then
   bound the formula over the outer box with the same remainder balls; Fable's crude form, suppressed by
   (1/2)^{31}, suffices.

**Expected:** the disc constants approach the point constants. At spin 9/10 that should bring n from 134 toward the
spin-3/5 count, and the segment to minutes. A sealed prediction will precede the run.
