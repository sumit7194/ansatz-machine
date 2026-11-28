# C2-AN registration: region A by analyticity in k. Item 1, the circle-picture loop chain on real k, at spin 3/5. Committed BEFORE any C2-AN code
**Office ansatz-machine, 2026-11-29.** The Bridge's ruling (C): GO, with priority over further region-B spend beyond the running production. The order:
1. commit the note as this registration's design section;
2. register item 1 with controls that can fail;
3. code from C2-L, a non-author read, then run 3/5;
4. item 3 (the lemma in MRS_SECTION.md) and its read.

The Bridge is running a hostile read of the argument itself, sent to Neon and to an independent Opus reader. Items 2–4 are not built on any point those reads flag as MAJOR until it is resolved; item 1 may proceed.

**Design section:** `C2_ANALYTICITY_DESIGN.md`, committed with this file, unchanged from the version sent to the Bridge. It contains the group lemma (with P_fin(tr M1) ≠ 0 in place of tr M1 ∉ [−2, 2]), the analyticity argument, the answers to Q1–Q3, and what it would not do.

## Item 1: what is certified
**Goal.** The circle-picture words (M0 = route (i)'s circle polygon, M1 = the per-k_c capsule lasso) define ONE real-analytic family F, tr M0, tr M1 on J = [2.895, 4.005] at spin 3/5, E = 4/5.
- The family must contain route (i)'s certified segment [2.9, 3.0], whose words are exactly link 0's below.
- This is the analyticity hypothesis of the design note §1, made rigorous. **Item 1 certifies NO monodromy value.**

**The words.**
- **M0:** the 96-gon of radius R0 = 1.35 starting at R0 (`circle_vertices()`, route (i)'s), the same for every link.
- **M1 for link i:** the floats lasso of k_c = 59/20 + i/10, for i = 0..10 (59/20, 61/20, …, 79/20), from the committed circle-picture rule `_nve_route1_floats.py` (R0 = 1.35). The entries are in `route1_floats_an_3_5.json`.
  - Two cross-checks are recorded, not gated:
    - the 59/20 lasso equals route (i)'s `route1_floats_prod_3_5.json` entry vertex for vertex;
    - the 79/20 lasso equals v7p's.
- **Link i's k-interval:** J_i = [k_c − 0.055, k_c + 0.055]. Consecutive links overlap on O_i = [k_c,i + 0.045, k_c,i + 0.055].

**The certificates.** Each is over real k-cells of width 0.01, refined into halves on failure down to 3 levels; a failure at the deepest level STOPS the chain at that link. "Nonsingular" means G1 = E²(f0² + c0²) − f0 ≠ 0, G2 = f0² + c0² ≠ 0, B(z²/a², k) ≠ 0 and z² + a² ≠ 0 on the closed box, for every k in the cell.
- **(a) The circle.** Every edge of the 96-gon is covered by boxes certified nonsingular.
  - c0 on the circle is the field continued ALONG the polygon from R0. That is C0's point walk at the cell centre (deriv=True, the carried branch), plus a Taylor model in k whose second-order remainder bounds |c0_kk| by the path length from R0 and sup|c0_kk″| over a tube about the walked path.
- **(b) The lasso.** Every edge of L_i is covered by boxes certified nonsingular.
  - c0 here is C2-L's CellField on the square 2 ± 1.15(1 ± i). It contains R0 and every lasso, and its freedom from c0's singular points (B ≠ 0, z² + a² ≠ 0) for every k in the cell is certified first. On that convex, singularity-free square c0 is single-valued: the sheet continued from +∞ along ℝ.
- **(c) The normalisation.** Re P > 0 on s ∈ [0, 1/R0] for every k in the cell, i.e. B > 0 on [R0, +∞). Then c0 at R0 (the start integrals from +∞) is analytic in k on the cell.
- **(d) Gluing.** On each overlap O_i, the homotopy region between L_i and L_{i+1} is certified nonsingular for every k in O_i. That region is C2-L's convex patches of same-angle matched vertices about an interior point, plus the two tail triangles at the base. Then M1 continues from link i to link i+1, and F_i = F_{i+1} on O_i (identity theorem). The circle is common to every link.
- **(e) Diagnostics (recorded, not gated).** Krawczyk sweeps of r+, p+ and p− over each link's real k-cells, and the minimum clearance of each loop from them.

**Controls that can fail** (the Bridge's two, plus a positive check):
- **K1, a singular point moved onto a loop.** Link 5's lasso with one vertex replaced by the exact p+(k_c) of its floats entry, so a G2 zero sits on the loop. (a)/(b) MUST refuse on the cell containing k_c.
- **K1c.** A polygon from R0 out to ia (c0's log branch point, at 0.6i) and back. The walk's singular-point guard, or (a), MUST refuse.
- **K2, a non-homotopic lasso swap.** In link pair (4, 5), L_5 is replaced by its complex conjugate. That lasso encloses r+ and p− instead of r+ and p+, so the swept region must contain p+ or p−, and (d) MUST refuse on O_4.
- **P (positive).** The unplanted chain over all 11 links: (a)–(d) pass.
- **Reading of the controls.** A control that does not refuse, or refuses through a guard other than the named one, is recorded as "not as specified". The run is then not used until a ruling.

**Reading of the run.**
- **All 11 links pass (a)–(d), and the controls behave.** The circle-picture F, tr M0 and tr M1 are each ONE real-analytic function on J = [2.895, 4.005]. Combined with route (i)'s certificate on [2.9, 3.0] (same words), each is not identically zero on J. That is the hypothesis of the design note's finiteness argument, to be used by item 3 (the lemma) only after its read.
- **A gluing failure at O_i.** The chain splits there; each piece needs its own rigorous point value, a ruling.
- **A loop failure.** That link is redrawn: a ruling, no retry.

**Code, read and run.**
- `scripts/_nve_c2an.py`, new, from `_nve_c2l.py` (the k-ball Taylor-model cell field, Krawczyk, tube and region checks), restricted to real k.
- A non-author read before the run. Then one run at 3/5, at most 2 cores, nice 10, pause-only guard.
- **Cost bar:** 3 h wall. Over it, STOP and report.

**Predictions:**
- (a)–(c) pass for all 11 links: 75%. The lasso clearance near p+ is the risk (C2-M P2's 0.0136 was on a complex k-ellipse; real k only is easier).
- (d) passes for all 10 overlaps: 85%.
- K1, K1c and K2 refuse as specified: 90%.
- Within the cost bar: 80%.

## Addendum C2-AN-1 (2026-11-29; committed before the read and any registered run): item 1 adapted to the hostile reads' points 1, 2, 5 and 6
The Bridge forwarded two hostile reads (Neon and an independent Opus reader) of the design note. Item 1 may proceed, adapted to points 1, 2, 5 and 6. The note's revision (v2, all ten points) is separate.
- **Point 1, closed lifts.** A loop gives a monodromy element only if q returns to its starting branch along it.
  - **(f), the circle.** Every singular point of c0″ = pref √B/(z² + a²)³ (±ia and the four zeros of B(z²/a², k)) is certified inside |z| < R0 for every k in the cell: |w±| < (R0/a)² for B's roots w (interval quadratic formula over the k-ball; valid through k = 4, where the discriminant vanishes), and a < R0. Then c0″ is single-valued and holomorphic on |z| ≥ R0, including at ∞, where it is O(z⁻⁴) (an even number of B zeros inside, so √B returns). So ∮c0″ = ∮s c0″ = 0 (no z⁻¹ term at ∞): c0, c0′ and hence q return round the circle. The certificate also checks α(k) = 90 − 21k > 0 on the cell.
  - **The lasso.** Every vertex lies inside the square 2 ± 1.15(1 + i) with a margin of 0.05, and the square's freedom from c0's singular points is certified per cell. So c0 is single-valued there and the lift closes.
- **Point 2, based homotopy of the PAIR.** In the circle picture the base point and the normalisation point coincide, b = R0: c0 is normalised from +∞ along [R0, +∞), and both words start and end at R0. The circle is common to every link, and the lasso homotopy fixes R0 (vertex 0) and moves the stem with the rest (every quadrilateral, stem included). So the pair (M0, M1) is continued as a based pair, and tr[M1, M0] is preserved, not just conjugacy classes.
- **Point 5, direct non-vanishing.** This was already the design: (a), (b) and (d) certify G1, G2, B and z² + a² ≠ 0 on box covers of the loops and the homotopy regions, so no root is tracked as the certificate. The Krawczyk sweeps (e) are dropped; (e) is now only the float clearance of the lasso from r+ and p+, for loop placement.
- **Point 6, the continued branch.** This was already the design: the circle's c0 is continued along the polygon itself (PathField), and the lasso's comes from the single-valued square, which is the continuation along the lasso from R0. The compactness remark (one uniform complex neighbourhood) belongs to the note.
- **New control K3 (natural must-fail):** at k = 4.2, beyond 3/5's k_cross, the circle's closed-lift check (f) MUST refuse. Development: it holds at 2.9, 3.5, 3.995, 4.0, 4.005, 4.05 and 4.1, and refuses at 4.2 (|w| ≤ 8.87 against 5.06).
- **Development timings:** about 4 s per k-cell; the whole chain is projected at about 10 min on one core.
