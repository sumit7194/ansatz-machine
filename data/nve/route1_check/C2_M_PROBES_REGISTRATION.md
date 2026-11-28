# C2-M production probes (re-gate (C)): two registered one-segment certificate attempts. Committed BEFORE either runs
**Office ansatz-machine, 2026-11-28.** The Bridge's ruling: the production estimate (`C2_PRODUCTION_ESTIMATE.md`, about
700 core-h at 3/5) rests on named extrapolations, so measure them first. Each probe is a FULL C2-M certificate attempt
under C2_M_REGISTRATION.md, addendum C2-M-1 and erratum C2-M-2, unchanged: the cover with H1–H4 and the refinement
rule; M1–M4; the verdict with v6's full controls; the engine gate. Each runs once.

**(i) MID-REGION at a larger half-width:**
- k_c = 83/20 (P2's centre; its floats entry exists), half = **1/200**: ten times P3's half-width.
- Tests whether segments 10x P3's size certify mid-region. The design guidance: the zero's sweep is about 0.006 against
  a clearance of about 0.057.
- It measures the cost per segment at that size.

**(ii) NEAR 30/7, deep in the dyadic chain:**
- The d = 1e-6 segment [30/7 - 2e-6, 30/7 - 1e-6], so k_c = 59999979/14000000 and half = 1/2000000.
- Its floats entry comes from the committed region-B geometry rule (`_nve_v7_floatsB.py`), generated before the run
  and committed.
- Tests the near-endpoint caveats: node precision against |F|, the outer branch point (V7 addendum 8), and the cost
  there.

**Cores:** each uses 2 cover workers plus 1. They run in parallel with C2-L's code writing (which has no compute), on
the free cores (the Bridge: load about 4 of 10, memory 78% free). Nice 10, pause-only guards.

**How the results feed the estimate:**
- If (i) certifies within the cost bar, mid-region production uses half 1/200 (about 29 segments for the uniform part
  instead of 284).
- If (ii) certifies, the dyadic chain's cost per segment is measured. If either fails, the estimate is revised with the
  failure stated.
- Then the why-it-matters note, the value gate with a Neon outside view, and then Sumit.

**Predictions:** (i) certifies 55%; (ii) certifies 45%; both within the 3 h cost bar if they certify, 70%.
