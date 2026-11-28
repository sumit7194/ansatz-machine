# C2-M registration: CAPD's finite M_F plus more Chebyshev nodes, for the region-B pilots. Committed BEFORE any C2-M code
**Office ansatz-machine, 2026-11-28.** GO from the Bridge's final C2 ruling (after the Neon outside view; C2-M first,
then C2-TM, `C2_TM_REGISTRATION.md`). Up to 2 Mac mini cores, nice 10, pause-only guards. The C2 time box stands:
STOP by 2026-12-12 if no pilot certifies.

**Grade line:** post-failure, informed by step 0'''s widths. The bar change is efficiency-only, and the certificate's
soundness is unaffected: ATAP is rigorous for ANY rigorous M_F, and a wider M_F costs only more nodes.

## Why
ATAP's bound is 4 M rho^-n/(rho - 1), and the certifier's n is ceil(log(4 M_F/((rho - 1) tol))/log rho) (v5's row
logic). At rho = 4 each factor of 4 in M_F costs one node. Step 0'''s centre R/5 sub-box at P2 gave a FINITE rigorous
sup|F| of about 1.1e59 in 234 s, which means n = 104 at tol 1e-3. The C2-3 bar (100x the sampled max) measured
efficiency, not soundness.

## Scope
**The region-B pilots P2 (k_c 83/20, half 1/20) and P3 (k_c 30/7 - 1.5e-3, half 1/2000).**
- P1 (the circle) is NOT in scope: CAPD was refused there at R/5 and R/10, and an R/20 cover costs about 22 h.
- P1 stays with C2-TM, or with nothing.

## Method
**1. M_F, M_T0 and M_T1 on E_rho (rho = 4) from CAPD driver v2** (`c2_driver_v2`, C2-4 with errata E1 and E2, as
read and controlled):
- the sub-box cover is the 25 closed R/5 sub-boxes of v2's kbox. They cover the square box, which contains E_rho (the
  kbox asserts). All 25 are run, since even the corner sub-boxes meet E_rho;
- each sub-box gives finite enclosures of F, tr M0 and tr M1. M_X = max over the sub-boxes of sup|X enclosure|.

**2. A refused or non-finite sub-box, fixed now, before any run:** that sub-box ONLY is refined into its 4 quadrants
(half-side R/10), each run once.
- If a quadrant is refused, that quadrant only is refined into its 4 quadrants (R/20), each run once.
- If any R/20 cell is refused or non-finite, C2-M STOPS for that pilot (reported, no further refinement).
- The refinements count against the cost bar.

**3. Nodes:** the v7B node evaluator (V.evaluate, V1/V2-validated; the v6 node file and its hash rules), at
n = ceil(log(4 M_F/((rho - 1) tol))/log rho) and likewise for the traces. n + 1 point evaluations per segment, of about
20–35 s each.

**4. NMAX = 160, by the Bridge's ruling, asserted in code.** v5's split threshold of 40 is, by its own comment,
"efficiency only, never soundness". 160 is enough for M up to about 1e90 at tol 1e-3. A row with n > 160 is rejected,
as v5 rejects n > 40 now.

**5. Holomorphy, the argument M_F rests on (Bridge clause; Neon's pitfall: M is usable only if F is certified
HOLOMORPHIC on the whole region, not merely bounded at sampled points).**

ATAP's theorem needs F analytic in the OPEN Bernstein ellipse E_rho with |F| <= M_F there.
- E_rho (semi-axes R and (15/17) R) lies inside the OPEN square |Re dk|, |Im dk| < R.
- The 25 closed R/5 sub-boxes (or their refinement cells) make up the CLOSED square.

For every k in a closed cell, the cell's completed CAPD run certifies the following guards:
- **(H1) the start.** d2kc0_B(zb, K_cell) succeeds; its base2 certifies Re P > 0 for the start integrand on every
  s-ball x the cell. So c0 and c0' at the base point are holomorphic in k on the cell, and the initial doubleton
  encloses them.
- **(H2) the root's branch.** C2-4's off-cut guard: lower(|A| + Re A) > 0, certified A PRIORI over every edge x the
  cell and AGAIN on every whole-step enclosure. So s(z, k) is the holomorphic continuation of the base branch along
  both loops for every k in the cell.
- **(H3) the singular points.** z^2 + a^2 != 0, G1 != 0 and G2 != 0, certified on every whole-step enclosure, so q has
  no pole on the loops for any k in the cell. The certified lower margins are recorded.
- **(H4) existence and finiteness.** Both loops complete, every enclosure is finite, and every edge ends exactly at
  j + 1 (C2-4 (b)). CAPD's enclosure is a proof that the solution EXISTS along the whole loop for every k in the cell.

**Conclusion:**
- The vector field is analytic in (z, k) on a neighbourhood of the loops x the closed square: the margins in (H1)–(H3)
  are positive on a compact set, so they persist on an open neighbourhood.
- By analytic dependence on parameters, the monodromy matrices M0(k) and M1(k) of the FIXED polygons are holomorphic in
  k there.
- F, tr M0 and tr M1 are polynomials in their entries (the adjugate is the inverse, since det = 1), so they are
  holomorphic on an open set containing the closed square, and therefore on E_rho. |F| <= M_F, the max of the cells'
  sup bounds.
- The node evaluator walks the SAME polygons (the floats entry's Gamma and lasso), so the node values are values of
  this same F.

**The run record shows, per cell:**
- H1 (d2kc0_B's result);
- the minima over both loops of the certified lower bounds of |A| + Re A, |z^2 + a^2|^2, |G1|^2 and |G2|^2 (H2, H3);
- completion, finiteness and the edge-end exactness (H4).

The cover is accepted only if every cell shows all four. A cell that fails any of them takes the refinement rule in 2.

## Rigour at n = 104 (Bridge item 2; checked in the code, `_nve_route1_segment_v2.py` `interp` and `conditions`)
- **Node balls:** every node value is an Arb ball from the evaluator (F radii about 3e-8 at P2). The Chebyshev
  coefficients c_m = (2/n) sum'' f_j cos(pi m j/n) are computed in Arb from those balls. So the interpolant's enclosure
  holds for EVERY choice of node values inside their balls, the true values included. No Lebesgue-constant argument
  is needed: the node errors enter the coefficient radii directly, each about <= 2 max_j rad f_j.
- **The sup bound:** `p_th` evaluates sum'' c_m cos(m theta) on the NSUB = 256 balls of theta covering [0, pi]. Its
  overestimate grows like m rad(theta) |c_m|, and the c_m decay with the TRUE F's analyticity, not with M_F. So the
  enclosure stays rigorous at any n. NSUB affects only how tight the conditions come out (efficiency); if the
  conditions fail by margin alone, NSUB may be raised, and that too is fixed by the ruling, not tuned.
- **Precision:** ctx.prec = 256 throughout. Node radii (about 1e-8) are far below the ATAP term at tol 1e-3, so the
  node errors cannot dominate tol.

**To be asserted in the run:**
- every coefficient finite;
- max rad(c_m) <= 1e-3 x the ATAP term (the node errors do not dominate);
- the conditions' minimum margins recorded.

## Bars
- **Soundness:** unchanged (the certifier's verdict with full controls, then the engine gate, as for every pilot).
- **Cost:** CAPD's cover (25 sub-boxes plus any refinements) / 2 cores + (n + 1) node evaluations / 2 cores + M1's
  new centre evaluations (24 plus any refinement cells) / 2 cores <= 3 h per segment for a pilot. That is the C2-3 bar's
  2 h plus the node and control time it did not count; accepted by the Bridge.

## Controls (each must be able to fail)
- **(M1) containment (Bridge edit 2: the new evaluations are stated and counted):** every CAPD sub-box enclosure of F,
  tr M0 and tr M1 must contain the point values inside it.
  - **Reused:** the 81 step 0' R/5 samples of the CENTRE sub-box (the only existing samples off the real axis; the
    R/10 and R/20 grids lie inside the same centre box).
  - **New:** ONE point evaluation at the centre of each of the other 24 sub-boxes (and at the centre of any
    refinement cell): 24 evaluations at about 20–35 s, roughly 7 min on 2 cores. They are COUNTED in the cost bar.
  - Any non-contained value fails M1.
- **(M2) a planted M BELOW the truth (Bridge edit 1).** For each X in (F, tr M0, tr M1), M_X is planted at 0.5 x the
  sampled max |X| on E_rho (the largest |X| among v6's own sampled-maximum points on the ellipse and the M1 values).
  - v6's sampled-maximum check MUST REJECT each of the three plants: that is three must-fail cases, each recorded with
    the check that refused it.
  - The earlier "M_F/1e6" plant is dropped: about 1e53 is still far above the truth (about 4.3), so no check could see
    it.
- **(M3) a planted refused sub-box:** a sub-box forced to REFUSE (a plant flag) must trigger the R/10 refinement
  path, and a forced refusal at R/20 must STOP. Both are checked against the record.
- **(M4) the node-precision assertion:** a planted node radius of 1e-2 must trip "max rad(c_m) <= 1e-3 x the ATAP
  term".

## Provenance of the outside view
The Neon answer (relayed by the Bridge, which checked its citations at source). The point-value route is standard
numerical complex analysis (Austin, Kravanja and Trefethen 2014, doi:10.1137/130931035). Its roots-of-unity bound
2M (rho/R)^N/(1 - rho/R) was rederived by the Bridge from the aliasing identity; ATAP's ellipse version, which we use,
has the same structure. These citations are NOT read here. C2-M's soundness rests on ATAP (read at source earlier for
v2) and on (H1)–(H4), not on them.

## Order
1. Registration, committed (with NMAX and the cost bar named in the ruling).
2. The cover runner (it reuses driver v2 and the glue; new code only for the 25-box loop, refinement and plants).
3. A non-author read of the new code.
4. Controls M1–M4.
5. P2: the cover, then the nodes, the verdict and the engine gate.
6. P3: likewise.
Once each.

## Predictions
- All 25 P2 R/5 sub-boxes finite (no refinement): 50%.
- P2's cover finishes within the cost bar: 60%.
- P2 certifies (all three conditions plus the engine gate): 35%.
- P3 certifies: 55% (its box is 100x smaller).

## Addendum C2-M-1 (2026-11-28): the order of the controls, made explicit (committed with the code, before the read and before any registered run)
The registration lists "controls M1–M4, then P2". Three of them depend on P2's own run, so the actual sequence per
pilot is fixed now:
1. **M3** (a DRY run of the cover's control flow; no CAPD).
2. The **cover**.
3. **M1** (containment, on the cover's cells).
4. The **verdict** with v6's full controls (R1_FULLCTL=1: held-out points, ellipse samples, the planted zero, the
   shrunken-M and planted-precondition checks).
5. **M2 and M4**, run on that verdict's node file.
6. The **engine gate** (`_nve_v7_engine_gate_B.py`, as in `air/v7_pB.sh`).

**The pilot counts as CERTIFIED only if** the verdict says certified with no ALARM, M1 passes, M2 ALARMs with
"proved M below a sample", M4 trips the node-precision assertion, M3 fired, and the engine gate passes. Any other
combination is reported as it is.

**What the code does (`scripts/_nve_c2m.py`):**
- The proof file is written in v5's schema; NMAX = 160 is asserted.
- v6's verdict is reused with EXACTLY two source substitutions, each asserted to find its original text verbatim:
  - v5's Dyson coverage gate (F3) becomes the C2-M cover gate (every leaf accepted with H1–H4, the cover complete,
    the proof file's coverage equal to the cover's);
  - the node-precision assertion is inserted after the interpolants.
- The region-B precondition and self-test over the box are kept, as in v5's prove.
- The code hash covers v7B's files plus the driver, the glue and the C2-M module, so the node files are new.

**Development check (not a registered run):** the centre R/5 cell through the glue (`c2/c2mdev_*`) reproduces step
0'''s enclosure (F +-7.7e58). Its margins are all positive (min |G2|^2 >= 2.7e-6 on the lasso; the off-cut margin is
about 379). A dry M3 run fired both ways.

## Erratum C2-M-2 (2026-11-28): after the non-author read of 199f9cf (committed before any registered C2-M run)
**F1, the node-precision assertion, as registered, was wrong for the traces.** n is sized from M_F (v5's formula), so
tr M0's and tr M1's ATAP terms come out far below their node radii BY CONSTRUCTION (at P2 R/5: about 1e-53 and 1e-41,
against node radii of about 1e-12). The real verdict would always have tripped it, and M4 would have tested nothing.
- **Amended:** the assertion is 2 x the largest F-node radius <= 1e-3 x F's ATAP term, for F only.
- For tr M0 and tr M1, node errors are carried rigorously in the interpolant's ball coefficients and judged by
  conditions(); soundness never depended on the assertion.
- M4 plants an F-node radius of 1e-2, which must trip it; the unplanted check now can pass.

**F3, M2 becomes three separate plants (M2F, M2T0, M2T1).**
- Each plants ONE quantity's M at 0.5 x the largest |X| among the REAL verdict's v6 ellipse samples, and each must
  ALARM "proved M below a sample".
- The M1 values are dropped from the sampled max: they lie at cell centres, possibly outside E_rho, where |X| may
  exceed the sup over E_rho and push the plant above the truth.
- Plants write their own proof and verdict files.
- Their extra evaluations (about 16 per plant) are counted and reported.

**F2, F4 and F5, provenance:**
- every cell record carries this run's nonce and the cell's exact centre and half-side, and is deleted before launch;
- M1's records are keyed by the cover's CODE and the cell's geometry, and all 81 centre samples must be used;
- the driver BINARY's bytes are in CODE, and the record's header must show the IdQR policy.

**F6, the cover gate:** M is recomputed from the leaves' records, the cells' geometry is re-checked against each run's
environment, and the proof file's M must be at least the leaves' sup (except in an M2 plant).

**F7, M3** now exercises each of accept()'s refusal branches (a crash, a driver refusal, a missing loop's margins, a
non-finite enclosure, a zero margin) and the R/20 STOP.

**F8:** F mode is asserted.

**A re-read of the fix diff precedes any registered run.**
