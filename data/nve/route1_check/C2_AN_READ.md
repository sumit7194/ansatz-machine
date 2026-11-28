# C2-AN item 1: non-author read of `scripts/_nve_c2an.py` (e73b3e4), 2026-11-29
**Reader:** a fresh agent (not the author). Read-only; it ran short snippets and the four controls (outputs to its scratchpad).
**Verdict: OK to run. No major findings, and no path to a false "CHAIN CERTIFIED".**

**What it confirmed:**
- **The k-remainder Q0 = E0 + E1·l + Mkk·l²/2** is valid for any path, from the integral form. SquareField's straight remainder path need not match the walk, because c0 is single-valued on the free square.
- **PathField** walks each edge from its own vertex, so the sheet is correct; its Mkk boxes cover the polygon.
- **taylor_box:** the square zm ± r contains Zb. The ratio-branch argument holds for a real k-ball.
- **Coverage:** the loop pieces tile the edges, and the bilinear homotopy lies in each quadrilateral's hull. Based-ness is asserted.
- **The closed lift:** Arb's sqrt of a discriminant ball straddling 0 encloses both roots. The certified max |w| over J is 1.415.
- **Cells:** the cells and halves cover the intervals completely. Exceptions give ok = False, and MAXLEV is fail-closed.
- **Data:** route (i)'s 59/20 lasso matches string for string, and v7p's 79/20 matches too. R0 is one double throughout, and E2 = 16/25.

**Minors, and what was done:**

| # | finding | action |
|---|---|---|
| 1 | `region_ok` returned True for a degenerate hull (fewer than 3 points). Latent: none of the 520 quadrilaterals is degenerate. | fixed: a degenerate hull is covered with no disjointness skip |
| 2 | The closed-lift limit used R0, but the 96-gon's chords reach in to R0 cos(π/96). | fixed: the limit is (R0 cos(π/96)/a)², about 5.057 |
| 3 | A control was marked a pass on any refusal. | fixed: it passes only through its named guard. All four re-run: REFUSED through the named guard |
| 4 | The diagnostic (e) ran inside the gated job, so it could fail or crash a cell. | fixed: (e) is wrapped and never gates |
| 5 | (d) differs from the registration text: vertex-index quadrilaterals with the stem included, not C2-L's same-angle patches plus tail triangles. It is a valid based homotopy, as C2-AN-1 point 2 implies. | recorded in addendum C2-AN-2 |
| 6 | `_disjoint` uses floats with a −1e−12 margin (C2-L's used Arb). Sound at these magnitudes. | recorded |
| 7 | Guards written as `assert` vanish under `-O`; the registered command uses `-I` without `-O`. | recorded |

**The controls as the reader ran them:**
- **K3:** refused by the closed lift (|w| ≤ 8.87).
- **K1c:** refused by the walk's singular-point guard, before any box check. So K1c does not exercise (a)'s box cover; K1 does that for the lasso.
- **K1:** refused by the lasso check at p+, only on the cells containing k_c.
- **K2:** refused by the gluing at every level. The first failing quadrilateral holds r+; on one O_4 cell, quadrilaterals 12, 37 and 39 fail (37 holds p+ and p−; 12 and 39 hold r+).

**A path correction to the registration:** route (i)'s floats file is at `data/nve/route1_check/air_prod_3_5/data/nve/eps/route1_floats_prod_3_5.json`.
