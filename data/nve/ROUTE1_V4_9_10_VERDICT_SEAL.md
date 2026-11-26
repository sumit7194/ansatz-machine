# SEAL (office, 2026-11-26, BEFORE the run): the full spin-9/10 segment verdict on the v4 proved M

**Approved by** the Bridge, 2026-11-26.
- **Code:** `scripts/_nve_route1_v4_verdict.py` runs Fable's UNCHANGED v2 `nodes` and `verdict` stages on the v4 chosen
  row from a75d7e3 (ρ = 4, n = 18, M_F ≤ 1.458e7, M_trM0 ≤ 4.814, M_trM1 ≤ 522.6). Every node record is fsynced, and a
  torn last record is repaired.
- **Resources:** 1 core, nice 12, about 80 MB. No caps. Correctness gates stop the run only at node boundaries.

## Diagnosis first (cited by the write-up): the 11× circle disc/point ratio at spin 9/10
Source: `scripts/_nve_route1_v4_circle_diag.py` → `data/nve/eps/route1_v4_circle_diag_9_10.out`, run at ρ = 3.
- **It is enclosure overhead, not intrinsic k-variation.**
  - The weighted sums in the row's own gauge are: point bound P 0.887; sampled disc maximum S 0.792 (9 k-points at the
    step midpoints); certified disc bound B 8.620. B reproduces the row constant exactly.
  - S/P = 0.89, while B/S = 10.9.
- **It is localised.** Almost 70% of B comes from the two angular bins [−60°, −30°) and [30°, 60°). Those bins hold
  4337 steps each, densely refined, near polar angle ±43.6°.
  - There, B/S ≈ 131 and B/P reaches about 15,000 per step, while S/P ≈ 0.1–0.6.
  - Elsewhere B/S is about 1.7–4.9.
- **The seal's suspected cause is refuted.** |1 − k_c φ| ≈ 0.74 on the whole circle, nowhere small. The overhead sits
  where the circle passes close to a singular point: the step refinement marks it.
- **Not yet attributed** between the two candidate terms there: the (dk²/2)·E k-remainder and the outer-box Cauchy
  remainder (crude bound × 2^−31). A local fix (finer k-sub-boxes or a smaller outer box on those steps) would bring
  the circle constant down to about 1. It is not needed at present, since the lasso term dominates M_F.

## Predictions for the verdict
- **VERDICT: CERTIFIED** for every real k in [1, 1.1]: F ≠ 0, tr M0 ≠ 0, tr M1 ∉ [−2, 2].
- **Margins.** The engine values (route1_floats_9_10.json) at k = 1, 21/20 and 11/10 give |F| = 0.0527, 0.0617 and
  0.0717 (increasing), tr M0 ≈ 1.9807, 1.9785 and 1.9761, and Im tr M1 ≈ 3.8428, 3.8450 and 3.8471. The proved
  interpolation bounds at (4, 18) are about 2.8e−4 (F), 9e−11 (tr M0) and 1e−8 (tr M1). So:
  - |F| ≥ 0.0524, in the range [0.0515, 0.0527];
  - |tr M0| ≥ 1.97614, in the range [1.9760, 1.9762];
  - |Im tr M1| ≥ 3.84280, in the range [3.8427, 3.8429].
- **Controls:**
  - the planted zero is REFUSED;
  - the held-out points (t = −5/8, 1/8, 3/4) are consistent;
  - the proved M ≥ sampled on the ρ = 4 ellipse, with an overestimate of F of order 1e7–1e9;
  - the engine end values (k = 1, 11/10) lie inside the node enclosures;
  - the shrunken-M control (bounds/1e12) falls below the sampled maximum for at least F.
- **Cost:** 19 + 3 + 8 = 30 node evaluations at about 3 min each (Fable's 9/10 end nodes took 181–188 s), so
  1.5–2.5 h in all. The complex-k ellipse points are possibly slower.
