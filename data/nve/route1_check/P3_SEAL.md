# SEAL (before any run): pilot P3, the proof-stage constants as k grows (spins 3/5 and 9/10)

**ansatz-machine-personal (Claude Opus), 2026-11-26. Written and committed before anything of P3 is computed, its
floats inputs included.** Registration v1 §5, P3. It runs only after v5.1 + B1 (b64a43c) has passed T1 to T4 again on the
Air. No proof stage has been run at k_c ≠ 21/20 with v3, v4 or v5; v2's crude-bound constants at 3/5 are the only
earlier measurement away from k = 1.

**What runs (on the Air, one process, nice 15, pause-only guard):**
1. Inputs: `_nve_route1_floats.py 1/2 2 3 39/10` (the 50-digit engine, `.venv`, Python 3.14.10, as for P2) into
   `route1_floats_p3_3_5.json` (R0 1.35) and `route1_floats_p3_9_10.json` (R0 1.2639). The committed floats files are not
   touched.
2. v5.1's proof stage, ONE row ρ = 4 (`R1_RHOS=4`), half-width 1/20, at k_c ∈ {1/2, 2, 3, 39/10} for each spin
   (`R1_KC`, `R1_HALF=1/20`, `R1_FLOATS`), under `.venv313` (Python 3.13.18). That is 8 proof stages.

**Baselines (v4 at k_c = 21/20, ρ = 4):** spin 3/5: c0 = 1.04, c1 = 15.8 per unit k, n = 14. Spin 9/10: c0 = 7.89,
c1 = 40.3, n = 18.

**Computed before sealing (numpy, not a run of P3; the numbers are why I predict a rejection):**
- **Laurent precondition on the ρ = 4 k-square** (half-side R = 0.10625): the largest root |w| is 0.363, 0.432 and 0.562
  at k_c = 1/2, 2 and 3, all below the limit 1/0.81 = 1.2346. At k_c = 3.9 it is **1.700**, from the corner region near
  k ≈ 4 + 0.1i, where the discriminant √(60k(k − 4)) turns.
- **The F1 margin on the circle** at the centre k (min over 20,001 points of Re(1 − kφ)): 0.88, 0.52, 0.28 and 0.062 at
  spin 3/5 (k = 1/2, 2, 3, 3.9), and 0.88, 0.50, 0.26 and 0.034 at spin 9/10. It stays positive throughout but shrinks
  linearly toward k ≈ 4.

**Predictions:**

| | k_c = 1/2 | k_c = 2 | k_c = 3 | k_c = 3.9 |
|---|---|---|---|---|
| ρ = 4 row at both spins | admitted (P = 95%) | admitted (P = 90%) | admitted (P = 85%) | **REJECTED, "precondition not certified"** (P = 95%) |
| spin 3/5: c0 / c1 per unit k | 0.6–1.2 / 9–17 | 1.0–2.5 / 16–30 | 1.5–4 / 20–45 | none (rejected) |
| spin 3/5: n | 12–14 | 14–16 | 14–18 | none |
| spin 9/10: c0 / c1 per unit k | 4–9 / 25–45 | 8–20 / 45–90 | 10–30 / 55–120 | none |
| spin 9/10: n | 16–18 | 18–24 | 20–30 | none |
| F1 gate fires (AssertionError) | no (P = 97%) | no (P = 95%) | no (P = 90%) | no in the reference walks (P = 85%; the margin there is 0.03–0.06 on the circle and unmeasured on the lasso) |

**The growth I expect, with more confidence than any single cell (P = 80%):** c1 increases with k at both spins
(1/2 < 21/20 < 2 < 3), and the ratio c1(3)/c1(21/20) is between 1.3 and 3 (v2's crude constants doubled at 3/5).

**Wall time on the loaded Air:** spin 3/5, 8–20 min per k_c; spin 9/10, 30–70 min per k_c (the 17,900-step circle walk
dominates). For k_c = 3.9 only the reference walks run before the rejection, since the precondition is checked
before any dq bound. Floats inputs: under 2 min (3/5) and under 10 min (9/10) in all.

**What a rejection at k_c = 3.9 means (the Bridge's v5.1 read asked for this to be written here):** LIMZ depends on the
spin only, so a rejected row there is a **valid result about the top of region A**, not a failure of P3. It says that a
0.1-wide segment centred at 3.9 cannot be certified with ρ = 4, because its k-square reaches the Laurent-precondition
crossing near k ≈ 4. Segments near the top must shrink, as the registration's §4.1 plan already says, and P3's cost
redo must price that. It does not by itself say where the last certifiable segment ends.

**What would surprise me:** a row admitted at 3.9; c1 decreasing with k anywhere; the F1 gate firing at k_c ≤ 3. That
last one would need a diagnosis before production, because production would meet it too.
