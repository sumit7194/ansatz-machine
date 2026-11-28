# C2 step 0'' result (addendum C2-4 (c), errata E1 and E2): FAIL. C2-via-CAPD is FAILED

**Office ansatz-machine, 2026-11-28.** The run is `air/c2_step0pp.sh` at d073dee, with driver v2 (`c2_driver_v2`,
IdQR). Settings, sizes, bar and grids are those of C2-3, unchanged; the step 0' samples are reused. Records are in
`c2/step0pp_P{1,2}_k{5,10,20}_o20_v2_tol1e-15_*` and the log `v7/c2_step0pp.log`.

**Grade line:** post-failure fix after step 0' FAILED (C2-4: s eliminated as a state; exact-time stepping). The
step-0' bar was amended (C2-3) after development smoke runs indicated the registered width/range bar would fail at R/5;
the new bar matches the certificate's use (sup bounds). The smoke widths at R/5, R/50 and R/500 on retraced loops were
seen.

**Verdict: FAIL at every size for both boxes.** Under the C2-4 ruling, C2-via-CAPD is FAILED, and the
fallback-or-STOP choice goes to the Bridge.

## P2 (region B, k_c 83/20)
| size | CAPD time per sub-box | F: sup / sampled max | tr M0 | tr M1 | original bar | cost (h/segment) |
|---|---|---|---|---|---|---|
| R/5 | 234 s | 1.1e59 / 4.32 = 2.5e58 | 6.9e10 | 2.0e20 | FAIL | 0.81 |
| R/10 | 230 s | 9.0e13 / 4.20 = 2.1e13 | 9.2e3 | 4.1e4 | FAIL | 3.19 |
| R/20 | 218 s | 2.1e7 / 4.14 = 5.2e6 | 437 | 257 | FAIL | 12.1 |

(The tr M0 and tr M1 columns give the same sup/max ratio.) Every enclosure is finite and contains all 81 sampled
values, for each quantity, so the enclosures are correct; they are vastly too wide.

## P1 (circle, k_c 79/20)
| size | outcome |
|---|---|
| R/5 | REFUSED: CAPD's step collapses on the circle, edge 80 of 96 (step 0': edge 6) |
| R/10 | REFUSED: the same, edge 90 of 96 (step 0': edge 10) |
| R/20 | completes. F +-1.2e9 (true |F| about 15), tr M0 +-634, tr M1 +-42; the formal judge waits for P1's samples (running) and cannot pass |

## What C2-4 fixed, and what remains (from the step logs)
**Fixed: s.** Eliminating s removed the s blow-up completely. c0 and c0' stay at widths 0.013–0.05 around all of P2's
Gamma (they exploded in step 0'), and P1 gets 80–90 edges round the circle instead of 6–16.

**Remaining on P2: Y wraps exponentially near G2's zeros.**
- Gamma runs where |G2| is about 0.01, so q, proportional to lambda^2 with lambda ~ 1/G2, is extremely sensitive to
  c0.
- c0's genuine k-variation over the sub-box becomes a wide interval for q, which enters Y' = A(q) Y. Y's width grows
  exponentially: at R/5, 0.03 -> 3e9 over 98 edges.
- ln(width of F) goes 135 -> 32 -> 16.5 for R/5, R/10, R/20: hs^2-like from R/5 to R/10, closer to hs below that.
- This is second-order k-dependence, which a first-order (affine, C r0) doubleton cannot carry.

**Remaining on P1: c0 accumulates width round the circle.** At R/10, 0.005 -> 0.34 by edge 90 (IdQR's axis-aligned
box on a rotating complex block, plus the genuine k-variation). Back near the base point, where the true |G2| is about
0.07, G2's enclosure reaches 0 (its certified |G2|^2 margin falls from 1.25 at edge 80 to 4e-14 at edge 90), q
explodes, and CAPD's step collapses.

**Cost would bind regardless:** about 220–400 s per sub-box, so R/20 needs 12 h or more per segment against the 2 h bar.

**Predictions against the outcome:**
- (a) removes the s blow-up: predicted 70%; it did;
- step 0'' passes the sup bar at some size: predicted 45%; it did not;
- cost binds at R/10 or finer: predicted 60%; it does (3.2 h at R/10, 12 h at R/20 for P2).
