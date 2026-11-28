# RESULT: S1, the split discriminator. NEITHER region recovers at split depth ≤ 2, so the crude dq bound needs replacing (candidate 2)

**Office ansatz-machine (Claude Opus), 2026-11-28.** The seal is `S1_SPLIT_SEAL.md`, committed before the run (02da2f8).
- **The run:** Mac mini, 2 cores (one per region), nice 10, under the pause-only guard. Launched 16:39:15: region A as
  PID 64328, region B as PID 64327. Done 16:53:26 and 16:47:45.
- **Code:** the stage-P code (dab2a9d), ρ = 4, prove only, so this certifies nothing.
- **Outputs:** `v7/s1A.log`, `v7/s1B.log`, and the floats and rows in `v7/s1/`.

## The control fired in both regions
v2's crude `dq_sup` REFUSED a box of radius 0.01 around a true zero of G1 (r+) with the depth-2 k-box:
- circle: r+ = 1.8145 at k_c = 313/80;
- region B: r+ = 1.8073 − 1.42e−… i at k_c = 329/80.

So the crude bound can say no to a real zero, and the reading below counts.

## Measured (ρ = 4)

| region | depth | k_c (half-width) | result | n | M_F | prove time |
|---|---|---|---|---|---|---|
| circle | 1 | 157/40 (1/40) | REJECTED: holomorphy box fails at 0.92 + 0.99i | — | — | 67 s |
| circle | 1 | 159/40 (1/40) | REJECTED: holomorphy box fails at 1.02 + 0.88i | — | — | 71 s |
| circle | 2 | 313/80 (1/80) | admitted | 14 | 1.1e7 | 180 s |
| circle | 2 | 315/80 (1/80) | admitted | 18 | 4.7e8 | 185 s |
| circle | 2 | 317/80 (1/80) | admitted | 34 | 2.5e19 | 168 s |
| circle | 2 | 319/80 (1/80) | REJECTED: holomorphy box fails at 0.61 + 1.20i | — | — | 72 s |
| region B | 1 | 33/8 (1/40) | REJECTED: holomorphy box fails at 1.5032 (beside bB) | — | — | 28 s |
| region B | 1 | 167/40 (1/40) | REJECTED: holomorphy box fails at 1.5032 | — | — | 29 s |
| region B | 2 | 329/80 (1/80) | REJECTED: n > 40 (log10 M_F ≤ 69.0) | — | ~1e69 | 113 s |
| region B | 2 | 331/80 (1/80) | REJECTED: n > 40 (log10 M_F ≤ 252.9) | — | ~1e253 | 117 s |
| region B | 2 | 333/80 (1/80) | REJECTED: holomorphy box fails at 1.763 − 0.283i | — | — | 39 s |
| region B | 2 | 335/80 (1/80) | REJECTED: holomorphy box fails at 1.717 − 0.259i | — | — | 42 s |

## The registered reading
- **Circle:** its first depth-1 half, [3.9, 3.95], is recovered by both quarters at depth 2. Its second half,
  [3.95, 4.0], is NOT, because the quarter [3.975, 4.0] is rejected. **Not recovered.**
- **Region B:** neither depth-1 half admits a row, and no depth-2 quarter does. **Not recovered.**
- **Neither region recovers: the crude dq bound needs replacing (candidate 2).**

**What the numbers add:**
- In the circle picture, M_F grows steeply toward k = 4: 1e7, then 5e8, then 2.5e19 across the quarters from 3.9 to
  3.975, before the last one fails. So even admitted rows near 4 cost n ≈ 34.
- In region B the problem is not only the crude refusal. Where a row is evaluated at depth 2, M_F is
  **astronomical** (1e69, 1e253). The k-direction bounds feeding the Dyson M bound are hugely inflated there: the
  k-Taylor remainder with addendum 5's E enclosures, plus the field's box remainder M·d²/2.
- Candidate 2, a K-uniform field c0 in place of the second-order k-Taylor, targets exactly this. It needs its own
  registration, read and controls.

## Against the seal

| prediction | P | outcome |
|---|---|---|
| the control fires in both regions | 97% | **HIT** |
| region B recovers | 55% | **MISS** |
| the circle recovers | 55% | **MISS** |
| both recover | 35% | did not happen |
| neither recovers | 25% | **HIT** |
| wall time under 1 h | 80% | about 15 min: **HIT** |
