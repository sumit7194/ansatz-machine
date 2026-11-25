# Handover: Fable side-session, route (i) first certified segment (2026-11-26)

**[model: Fable 5.2] Everything here is UNVERIFIED until the office ansatz-machine checks it.**
Brief: `docs/BRIEF_FABLE_ROUTE1_SEGMENT_2026-11-26.md` (v1, commit f6988c8). Branch `fable/2026-11-26-route1-seg`, cut
from main at f6988c8. Main was not touched. Nothing was merged, published or sent outside the fleet.

## What was asked, and what came out

Certify, at spin 3/5 and E = 4/5, that for every real k ∈ [1, 1.1]: F ≠ 0, tr M0 ≠ 0, tr M1 ∉ [−2, 2], with the
circle |z| = 1.35 and the lasso of k = 21/20 fixed.

**Outcome: CERTIFIED. |F| ≥ 0.26502, |tr M0| ≥ 1.99315, |Im tr M1| ≥ 2.64882 on the whole segment, with a proved M_F = 6.57e10 on the k-disc of radius 0.1063, ρ = 4 and 25 Chebyshev points. Every control behaved as required, except that the shrunken-M control is uninformative for the verdict (explained in the write-up §7). One sealed prediction was wrong: M_F is above the predicted 1e2–1e8.** The write-up is `data/nve/ROUTE1_SEGMENT.md`; read its §0 and §1 first.

## Files

| file | what |
|---|---|
| `data/nve/ROUTE1_SEGMENT.md` | the write-up: what is certified, what is argued, method, proved M, verdict, controls, scorecard, constants, cost |
| `scripts/_nve_route1_segment.py` | the certifier; stages `prove`, `nodes`, `verdict` |
| `scripts/_nve_route1_kc_identity.py` | sympy checks (closed form at k_c, derivative rule, integrals, roots) |
| `scripts/_nve_route1_consts.py` | Dyson constants at other k (measurement only) |
| `data/nve/eps/route1_seg_3_5.out` | log of the three stages of the certified run |
| `data/nve/eps/route1_seg_M_nseg1.json` | proved M, every ρ row, the gauge matrices |
| `data/nve/eps/route1_seg_nodes.jsonl` | one line per point evaluation (25 nodes, 3 held-out, 8 ellipse) |
| `data/nve/eps/route1_seg_verdict_nseg1.json` | verdict and control outcomes |
| `data/nve/eps/route1_seg_identity.out` | sympy output |
| `data/nve/eps/route1_seg_3_5_dev.out` | the two earlier, looser proof runs (kept as the record of what was tried) |
| `data/nve/eps/route1_seg_consts.out` | constants at other k |
| `data/nve/eps/route1_floats.json` | CHANGED: three entries added (k = 1/2, 2, 3; the engine's values and lasso there, for the constants run). The entries for 1, 21/20 and 11/10 are untouched |

## Runs made (all one process, one core, normal priority as the Bridge allowed this round)

| run | time | note |
|---|---|---|
| sympy identity check | 2 s | repo `.venv`, sympy 1.14.0 |
| proof stage, first version | 30 s | uncombined derivative, base gauge: lasso constant 653 per unit k, n ≈ 1,000. Crashed with a float overflow at ρ = 2.5 (M too large to represent). Kept in the dev log |
| proof stage, second version | 39 s | combined derivative + optimised gauge, one k-box: n = 38 |
| proof stage, final | 39 s | + 5 × 5 k-sub-boxes: n = 24 |
| nodes + verdict | 815 s + 2 s | 36 point evaluations at about 22 s |
| verdict, second run | 2 s | interpolant enclosed on θ-balls instead of t-balls: certified min \|F\| 0.1500 → 0.2650; same nodes |
| constants at other k | 64 s engine (repo `.venv`, k = 1/2, 2, 3) + 115 s | |

Memory: footprint 16 MB by `top` (MEM), peak RSS 33 MB. No run passed 15 minutes. No caps were used.
Interpreter for all Arb work: `/Users/sumit/Github/quantum/sims/.venv/bin/python -I`, Python 3.13.12, python-flint
0.9.0, read-only; nothing was installed.

## What the office should check

1. **The Dyson chain** (`ROUTE1_SEGMENT.md` §2 steps 4–5). It is a hand derivation: the gauge form
   Y_k = Φ_c C T C⁻¹, the rank-one norm |(v1, v2)C|²/|det C| (uses det Φ_c = 1), and the three M formulas.
2. **The Taylor remainder in k** used on the sub-boxes: c0 = c0_c + δk·D0_c + δk²·E0/2 with E0 enclosed on the whole
   k-square, and the claim that the rectangle-rule enclosure of the radial integral is valid (integrand enclosed on
   each s-ball, times the width).
3. **`step_ref` against `P.step`.** It is a copy with one addition (the enclosure on the whole step segment). A diff
   should show only that.
4. **The node inflation** for midpoint evaluation (§2 step 7).
5. **Float steps.** The last conversions use floats with a 1 + 1e−7 inflation, not directed rounding.
6. **The θ-ball enclosure** of the interpolant (`interp`'s `p_th`): the balls of θ must cover [0, π].
7. **Reproduce:** the four commands in `ROUTE1_SEGMENT.md` §12. The node file makes `nodes` a no-op on a rerun;
   move it aside to recompute.

## Departures from the brief, stated plainly

- The perturbation is bounded through dq/dk (mean value in k), not through the closed form with a binomial majorant.
  The closed form is sympy-checked but unused.
- The Dyson bound is in an optimised constant gauge. This is what made the node count feasible.
- "Proved M ≥ sampled" uses 8 fresh samples on the ρ = 4 ellipse; Part B's ρ = 8 samples lie outside the disc used.
- The Bridge's compute note replaced the brief's "nice 12 / wait if the box is full" line.

## Not done

- Any k outside [1, 1.1], any other spin.
- An independent second implementation.
- A tighter bound on F (see `ROUTE1_SEGMENT.md` §10, last bullet): it would cut the node count further.
- The step-size fix of B5.
