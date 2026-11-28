# C2-M production at P3's size: compute only, no runs (re-gate (C)), 2026-11-28
**Scope.** The top of the range is [3, 30/7 - delta0] (V7 registration). At 3/5, delta0 = 7.4e-15.
- Region A, [3, 4] (the circle picture, below the A/B switch at k = 4.0), has NO C2 route: CAPD was refused on the
  circle, and the C2-TM probe failed. Region A's top [3.7, 4] was already parked (STATUS).
- So C2-M covers region B only: [4.0, 30/7 - delta0].

**Count at P3's half-width (1/2000, segment length 1e-3), spin 3/5:**
- **Uniform part,** [4.0, 30/7 - 2e-3], length 0.28371: **284 segments**.
- **Dyadic chain** [30/7 - 2d, 30/7 - d] from d = 1e-3 down to delta0, where it meets the interval-certified sliver:
  ceil(log2(1e-3 / 7.4e-15)) = **37 segments**. P3 is the first (d = 1e-3), already certified, so **36 remain**.
- **Total: 320 segments.**

**Cost** (P3 measured: about 1.1 h wall per segment on 2 cores, so about 2.2 core-h): 320 x 2.2 = **about 700 core-h** at
3/5. Wall time on the Mac mini (10 cores, load about 5, so about 4–6 free):
- 2 segments at a time (4 cores): about 176 h, **about 7.3 days**;
- 4 at a time (8 cores): about 88 h, **about 3.7 days**.
All four spins (the V7 plan's production row) would be roughly 4x: about 2800 core-h.

**By the Bridge's thresholds this is over 3 days, so it goes to Sumit (via the value gate, with Neon).**

**Caveats, stated now:**
1. Each segment needs its own floats entry (loops built for that k_c by the committed geometry rule,
   `_nve_v7_floatsB.py`); the time for that is small and not counted above.
2. P3's 1.1 h may not hold everywhere. Near 30/7, the dyadic segments' ellipses shrink (cheaper covers?), but node
   precision against |F| and the outer branch point (V7 addendum 8) are untested there. In the middle of region B the
   lasso's clearance varies with k_c (P2's 0.057 at 4.15).
3. A LARGER half-width may work in the middle of region B, where the clearance is comfortable. With the zero's sweep
   at about 0.42 |dk|, half = 1/200 gives a sweep of about 0.006, far below P2's centre clearance. That would give
   about 29 + 36 = 65 segments, about 140 core-h, roughly 1.5 days on 4 cores. **This is an extrapolation, not a
   measurement:** it needs its own one-segment probe (for example half 1/200 at k_c 4.15) before any production
   claim.

## Erratum E-δ0 (2026-11-29, found by the author while scoping ruling (B)): the 3/5 sliver is δ0 = 1.37e−11, not 7.4e−15
- **The error.** `C2_PRODUCTION_ESTIMATE.md` took δ0 = 7.4e−15 for spin 3/5. That is spin 3/10's sliver. The claim's table (`CLAIM_FAMILY_II.md`, end-sliver row) gives δ0 = 1.37e−11, 2.4e−10, 3.6e−10 and 7.4e−15 at spins 0.6, 0.8, 0.9 and 0.3, with E = 0.8. The count also had an off-by-one: the chain [30/7 − 2d_j, 30/7 − d_j], d_j = 1e−3/2^j, j = 0..J, reaches 30/7 − d_J, so it needs d_J ≤ δ0, not ceil(log2(1e−3/δ0)) segments.
- **Corrected at 3/5:** d_J ≤ 1.37e−11 needs J = 27 (d_27 = 7.45e−12; d_26 = 1.49e−11 is too large). So the chain is **28 segments, j = 0..27**:
  - P3 is j = 0, certified;
  - j = 1..7 pass H1 and are in production (A);
  - **j = 8..27, 20 segments, refuse at H1** and are ruling (B)'s job (not 29).
- **Effect on the other numbers:**
  - the region-B length, its reachable fraction (99.997%) and the coverage percentages change only in the eleventh digit;
  - the production total becomes 29 + 28 = 57 segments at the Pmid size, not 65;
  - (B)'s run is about 20 × 2.2 = 44 core-h, not 64.
- Nothing that ran used δ0; no record or certificate is affected.
