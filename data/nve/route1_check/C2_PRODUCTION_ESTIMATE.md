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
