# C2-M production probes (re-gate (C)): Pmid CERTIFIED, Pend FAILED (refused at H1, an evaluator artefact near 30/7)
**Registration:** `C2_M_PROBES_REGISTRATION.md`, committed before either probe ran. Each is a full C2-M attempt under C2_M_REGISTRATION.md, addendum C2-M-1 and erratum C2-M-2, unchanged, and each ran once.
**Runs:** `air/c2m_pilot.sh Pmid` and `air/c2m_pilot.sh Pend`, in parallel from 2026-11-28 22:41:25, at HEAD 8c12b9b (Pend's floats entry was committed there, before the run). Logs: `v7/c2m_Pmid.log`, `v7/c2m_Pend.log`; their first lines carry the code hashes.
**Environment:** Mac mini, `.venv313` (python-flint, Arb), CAPD driver v2 (`build/c2_driver_v2`), 2 cover workers each, nice 10, pause-only guards (no pause fired).

## (i) Pmid, mid-region at ten times P3's size: CERTIFIED
**Claim, certified for EVERY real k in [829/200, 831/200]** (k_c = 83/20, half 1/200):
- F(k) ≠ 0;
- tr M0(k) ≠ 0;
- tr M1(k) is not in [−2, 2].

| gate | result |
|---|---|
| M3 (dry) | FIRED, all modes, and the R/20 STOP |
| cover: 25 R/5 cells | **25 leaves of 25 cells, no refinement needed**, no STOP; every leaf shows H1–H4 |
| M = max over the leaves | M_F 1.626e4, M_T0 0.7511, M_T1 31.13 |
| M1 (containment, 25 values) | PASS |
| verdict, v6 with full controls (n = 10, rho = 4) | **CERTIFIED**, no ALARM |
| v6's own controls | held-out consistent (3 points); proved M ≥ sampled on the ellipse (over-estimates ×3.9e3, ×40, ×14); planted zero refused; planted precondition fires; the shrunken M breaks it |
| M2F, M2T0, M2T1 (M planted at 0.5 × the sampled max) | each ALARMed: "proved M below a sample" |
| M4 (a planted F-node radius of 1e−2) | tripped the node-precision assertion (the unplanted verdict passes it) |
| engine gate B | 16/16 node values inside their enclosures |

**The certified margins:**
- |F| ≥ 4.0183 against F's error bound 2.07e−2;
- |tr M0| ≥ 0.017406 against 9.6e−7;
- |Im tr M1| ≥ 0.99948 against 4.0e−5;
- the largest node radius is 7.8e−8.

**Cost:**
- the cover was 2920 s wall (5611 CAPD core-seconds);
- the whole run, the controls included, took 22:41 to 23:47, **about 1.1 h wall on 2 cores per segment**, the same as P3 for a segment ten times longer.

**What it confirms and what it does not.**
- It confirms the production estimate's caveat 3 at one point: in the middle of region B, at k ≈ 4.15, a segment of half 1/200 certifies with no refinement. The design guidance predicted a sweep of about 0.006 against a clearance of about 0.057.
- It is one k_c. The lasso clearance varies along region B, so half 1/200 elsewhere in [4.0, 30/7 − 2e−3] is an extrapolation until measured. A production would carry its own per-segment STOP and refine rule (the registered halving).

## (ii) Pend, near 30/7 (d = 1e−6, half 1/2000000): FAILED, refused at the start
- **The cover STOPPED:** 0 leaves of 525 cells. Every R/5, R/10 and R/20 cell was refused in about 2 s, before CAPD ran, with "d2kc0 refused at the base point over the sub-box". That is the H1 guard (the base point's second k-derivative).
- The runner then ran its later stages anyway: the controls, the verdict and the engine gate.
  - These ran on an empty cover and say nothing. The engine gate crashed on a missing node file.
  - This is a runner defect (it should stop after a cover STOP), recorded here, not a result.
- **The cause is an evaluator artefact, not a property of F.**
  - `base2` (`_nve_route1_segment_v7B.py`) must certify Re P > 0 on each of 96 s-balls covering [0, 1/bB].
  - For real k < 30/7, every term of P = (90 − 21k) − (60 − 18k) a²s² + (10 − k) a⁴s⁴ is ≥ 0. But midpoint-radius squaring of the first s-ball gives s·s a negative lower bound. With −(60 − 18k) about +17.1, that makes the middle term's lower bound about −1.5e−4.
  - The guard fails once 90 − 21k, which is 21 d, drops below that: d < 7.1e−6 (predicted).
- **Measured afterwards** (a diagnostic, design-grade; it certifies nothing): bisection on `base2` itself, with Pend's floats entry, gives **d* = 7.08e−6**. It passes at 1e−5 and fails at 5e−6 and below, at point k and on the segment's k-ball alike. The prediction and the measurement agree.
- Pend's segment (d = 1e−6) is below d*, so this refusal was certain. The other near-end caveats (node precision against |F|, the outer branch point) were therefore not reached, and remain untested below d = 1e−3.

## What the two probes do to the production estimate (`C2_PRODUCTION_ESTIMATE.md`, revised in `C2_WHY_IT_MATTERS.md`)
- **Uniform part** [4.0, 30/7 − 2e−3]: 29 segments at half 1/200 instead of 284, **about 64 core-h**, if the clearance holds along the stretch.
- **Dyadic chain** (37 segments, with P3 = the first certified):
  - H1 passes for d down to 7.8e−6, which is 7 more segments, about 15 core-h;
  - the last **29 refuse at H1**;
  - without a base2 fix (a new mechanism; it is described in the note and not run), production cannot reach δ0;
  - the unreachable length is about 7.8e−6, roughly 0.003% of region B.
- **Region A** [3, 4] still has no route, so no region-B outcome changes the claim's status.

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
