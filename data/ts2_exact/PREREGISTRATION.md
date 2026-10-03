# TS δ=2 at p = 4/5: exact Killing-tensor rungs — pre-registration (committed BEFORE any TS run)

Asked by The Bridge, approved by the user, 2026-10-04 (overnight, unattended). Vollmer 2016 (arXiv:1602.08968)
excluded Killing tensors up to valence 7 for TS δ=2 at p = 3/5. **This run is at p = 4/5 (q = 3/5), which he did
not cover.** A null here complements Vollmer at a different parameter point; it does not reproduce him.

## Instrument
`scripts/_kt_exact_op.py`: the template operator (_kt_opfast, D49) gives {H, F} = 0 as an exact GF(p) system.
The Rust nullspace (D48) is residual-guarded. The nullity is the exact dimension, with no sampling.
- The reducible span ⟨p_t, p_φ, H (, L² if conserved)⟩ is measured in the same basis and must lie inside the
  solution space, or the run is condemned.
- IRREDUCIBLE = exact − reducible.
- Ansatz: K^{a..}(x, y) = polynomial in (x, y) / L^d, with L the measured lcm of the g^ab denominators.
  The box is the reducible-holding box + margin 4. The denominator power d is the smallest that holds the
  COMPLETE reducible algebra at that rank: d = 1 for ranks 2–3, 2 for rank 4, 3 for rank 6. This is stricter
  than the published den¹ rows, where H² was outside the ansatz.
- Metric: the TS2 package at p = 4/5 (`data/sealed/TS2_for_quantum/ts2_metric_components_t1o3.txt`, σ = 1),
  exact in (x, y), vacuum verified in its own build. Kerr control: the same package's δ = 1 build at the same
  p, i.e. the same chart, the same pipeline and J/M² = 3/5.

## G0: validation by REPRODUCTION, already run (outputs committed with this file)
- Kerr BL (M = 1, a = 1/2), rank 2, den¹, box 8×8: exact 5, reducible 4, **irreducible 1** = §127 exactly.
- ZV δ=2 den¹: rank 2 exact 4 / irreducible 0; rank 3 exact 6 / irreducible 0. This equals the published §124
  rows (4, 6). At rank 4, den¹ is correctly refused: H² needs L².

## Predictions (sealed by this commit), and the gates
| gate | run | prediction (exact / reducible / irreducible) |
|---|---|---|
| G1 | Kerr (TS2 pipeline) r2 den¹ | 5 / 4 / **1** (Carter) |
| G1 | Kerr r3 den¹ | 8 / 6 / **2** (Q·p_t, Q·p_φ) |
| G1 | Kerr r4 den² | 14 / 9 / **5** (Q·{p_t², p_tp_φ, p_φ², H}, Q²) |
| G1 | ZV δ=2 r4 den² | 9 / 9 / **0** (literature: MPS 2013 all ranks; §126) |
| G2 | **TS δ=2 p=4/5 r2 den¹** | 4 / 4 / **0** |
| G2 | **TS r3 den¹** | 6 / 6 / **0** |
| G3 | **TS r4 den²** | 9 / 9 / **0** |
| G4 | **TS r6 den³** (only if G3's measured size projects to ≤ 30 GB whole-tree and ≤ 10 GB disk) | 16 / 16 / **0** |

Every run is done on both primes (2147483647, 2147483629), and the counts must agree.
- **TS confidence: ~95% for irreducible 0 at every rank.** Basis: Vollmer's exclusion at p = 3/5; numerical
  chaos in TS; the fleet's TS integrability obstruction; and no mechanism (no principal tensor off Kerr).
- **What would surprise me:** any TS irreducible > 0. A Kerr control coming in below its prediction would mean
  the ansatz (box or margin) cannot hold the Carter tensors in this chart. That is a box failure, not physics,
  and it stops the queue.

## Decision rules
- A control mismatch: STOP, report, and no TS run.
- A TS irreducible > 0: run the second prime of that configuration, then STOP. Report to the Bridge for an
  independent check. **No claim of any kind before that.**
- A prime disagreement: STOP (false vanishing).
- A condemned run (a reducible outside the solution space): STOP.
- Scope of a null: "no irreducible Killing tensor at rank r on TS δ=2, p = 4/5, within {x^a y^b / L^d}, box as
  stated, exact over GF(p) on two primes, reducible span subtracted". The ceilings of CLAUDE.md §3 apply (rank,
  ansatz; the result is exact, not perturbative).
- Resources (the Bridge's budget): ≤ 4 threads (2 by default), detached, whole-tree footprint logged, disk floor
  5 GB, caffeinate. Rank 6 only if the measured projection fits.
