# SEAL (before any run): pilot P1, the spin-3/5 v4 segment verdict at its own n = 12

**ansatz-machine-personal (Claude Opus), 2026-11-26. Written and committed before P1 runs.** Registration draft
c3a61ab, §3(c) / §5 P1. Nothing of P1 has been computed when this is committed.

**What runs:** `scripts/_nve_route1_v4_verdict.py` at `NVE_SPIN=3/5 R1_R0=1.35`, unchanged from c2dd39c, on the v4
chosen row of `route1_seg_M_v4_nseg1.json` (6d411a8): ρ = 6.5, n = 12, R ≤ 0.16635, proved error bounds
F 2.952e−4, tr M0 3.434e−10, tr M1 4.052e−8. It evaluates 13 new nodes, 3 held-out points (t = −5/8, 1/8, 3/4) and
8 points on the ρ = 6.5 ellipse with v2's all-ball evaluator, then v2's verdict and controls. One process, nice 15.

**Predictions:**

| quantity | prediction |
|---|---|
| verdict | CERTIFIED, P = 97% |
| \|F\| ≥ | between 0.26500 and 0.26508 (the minimum of the interpolant ≈ 0.26533, minus ≈ 2.95e−4) |
| \|tr M0\| ≥ | 1.9931584 (to 7 decimals) |
| \|Im tr M1\| ≥ | 2.6488208 or 2.6488209 at 7 decimals |
| planted zero | refused |
| held-out points | consistent: \|p − f\| ≤ 1e−6 for F, far below the bound |
| proved M ≥ sampled on the ρ = 6.5 ellipse | true; F overestimated by 1e5 to 1e7 (the ρ = 4 row overestimated by 6.7e4) |
| engine end values (k = 1, 11/10) inside the node enclosures | true |
| shrunken M (÷1e12) | below the sampled maximum for F; for the traces, below at tr M1, possibly not at tr M0 (M_trM0 = 2.69 against \|tr M0\| ≈ 2.0) |
| wall time | 10–20 min (24 evaluations at 25–45 s on a loaded box at nice 15) |

**Why the 3% doubt:** ρ = 6.5 is the widest ellipse used so far at spin 3/5. The ellipse samples run farther into
complex k than any earlier verdict, so an evaluator failure there (a refused step disc, a non-finite enclosure) is
possible. The certificate itself does not depend on the samples, but the run would stop.
