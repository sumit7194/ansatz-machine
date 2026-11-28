# C2 step 0 result: the inflation is a dependency artifact (2 of 3 boxes, and the third is explained). Design (B) fails its cost probe, so (A) Taylor models is indicated

**Office ansatz-machine (Claude Opus), 2026-11-28.** The registration is `C2_REGISTRATION.md`, committed before step 0
(9345e6a); the script is `scripts/_nve_c2_step0.py` (1bc74d9, before its run). Mac mini, nice 10, seconds per box.
Outputs are in `v7/c2_step0_*.json/.out`. It certifies nothing.

## Measured: crude bound against sampled truth (405 point samples of Z × K: 9 × 9 k-grid × 5 z points, from the v7 field at point k)

| box | crude sup \|dq/dk\| | sampled sup \|dq/dk\| | at k_c | sampled sup \|q\| | crude/sampled | registered reading |
|---|---|---|---|---|---|---|
| P1 (circle, k_c 79/20, Z = 1.3213 + 0.2754i ± 0.01) | **refused** | 1.07 | 0.71 | 0.61 | — | **dependency artifact** |
| P2 (region B, k_c 83/20, Z = 1.5032 ± 0.01) | **refused** | 10.8 | 4.6 | 1.6 | — | **dependency artifact** |
| S1 (region B, k_c 331/80, lasso step 486) | 6.46e5 | 1.63e3 | 6.0e2 | 80 | 396 | "neither" (< 1e3, no explosion) |

**Majority: dependency artifact, so C2 proceeds.** The true |dq/dk| over the whole k-box is modest at P1 and P2, and the
crude bound refuses there only through ball dependency.

**Why S1 still gives M_F ≈ 1e253:** the Dyson bound exponentiates the per-step bounds. A uniform inflation of about
400× turns a true exponent of about 1.5 into about 580, i.e. e^580 ≈ 1e252. **So C2's bound must be within a small
factor of the truth, not merely finite.** That raises the bar for any design.

**Prediction scored:** "step 0 reads dependency on ≥ 2 of 3 boxes" (70%): **HIT**.

## Cost probe for design (B): FAILED, so (A) is indicated (registration: "(A) if (B)'s probe exceeds 30× or the bound is too loose")
- (B) needs the field at small k-BALLS on a circle of radius R' ≈ 0.22 around k_c.
- **The probe:** a region-B field at the k-ball k_c ± 0.03(1 + i), walked through the Γ loop's step centres.
  - **It refused at step 45: "branch continuity of √B not certified".** With k a ball, the √B prediction is too wide
    to choose the branch. That is the same dependency, now in the field itself.
  - The ODE walk of Γ at point k_c took 7.8 s for 683 steps.
- Making (B) certifiable would need k-balls of about 0.005, so about 150 fields covering the circle and the holomorphy
  certificate's disc. Each walks both loops. That is an estimated 70 min per prove, against today's 0.5–3 min: **far
  over 30×**.
- (B)'s holomorphy certificate (G ≠ 0 on Z × disc) also meets the very dependency that refused P1 and P2, unless its
  k-cells are tiny.

## Consequence for the design addendum (next, before code)
**(A), Taylor models in dk (Berz–Makino), as the Bridge suggested.** Carry c0, c0' and dc0/dk at k_c, together with the
field's √B, as polynomials in dk of degree d with a rigorous remainder.
- **Range bounding** over K then keeps the k-correlation, which is exactly what step 0 shows is lost.
- **The design must state:** the TM arithmetic rules with remainders (+, ×, 1/G, √ with the field's branch), the
  degree d, how the z-series and the dk-polynomial interleave in the field step, and how sup |dq/dk| over Z × K is
  bounded from the TM. It must also show a bound within a small factor of step 0's sampled values on these three
  boxes, before any pilot.
- **Effort, honestly:** this is a substantial new arithmetic layer, about 2–4 sessions with its read, against the time
  box of 2026-12-12.
