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

---

# Follow-up, same day: version 2 (the Bridge's three items)

**[model: Fable 5.2] UNVERIFIED.** Same branch, new commit on top of 604d520. Write-up: `ROUTE1_SEGMENT.md` §13–§15.

## What was asked, and what came out

1. **No float rounding up to the verdict numbers.** Done in a new file, `scripts/_nve_route1_segment_v2.py`; version
   1's file is untouched so that 604d520 stays reproducible. The verdict is unchanged and no lower bound moved: |F| ≥ 0.265023401, |tr M0| ≥ 1.993158418, |Im tr M1| ≥ 2.648820919, on Part B's node values and on a fresh set from an all-ball evaluator alike. One v1 print was rounded up (2.648821 for |Im tr M1|); the certified value is 2.648820919.
2. **How dq/dk is enclosed, with code pointers and asserts.** `ROUTE1_SEGMENT.md` §14. The asserts count every
   (path box, k-sub-box) pair: 54,075 on the circle and 17,575 on the lasso, all enclosed, none skipped.
3. **Gauge legitimacy.** `ROUTE1_SEGMENT.md` §15: the two matrices, their inverses, and how the condition number
   enters.

## A finding the office should know about

Part B's `walk` (`_nve_route1_proto.py`) can leave a gap of up to about 1e−15 at a polygon vertex: the edge's end
point is computed in floats and the next edge starts at the vertex itself. It is far below the enclosure radii but
not covered by them. Read off the code, not measured. The v2 walk closes it. This touches the office-reproduced Part B
point enclosures in the formal sense only.

## Files added

| file | what |
|---|---|
| `scripts/_nve_route1_segment_v2.py` | the all-ball certifier and point evaluator; stages `prove 1`, `nodes 1 arb`, `verdict 1 arb`, `verdict 1 partB` |
| `data/nve/eps/route1_seg_3_5_v2.out` | log of the v2 stages |
| `data/nve/eps/route1_seg_M_v2_nseg1.json` | the proved M as ball strings, box counts, gauge matrices |
| `data/nve/eps/route1_seg_nodes_arb.jsonl` | point evaluations by the v2 evaluator (one line each) |
| `data/nve/eps/route1_seg_verdict_v2_partB_nseg1.json`, `..._arb_nseg1.json` | verdicts on the two node sets |

## Runs (one process, nice 12, shared core)

| run | time | note |
|---|---|---|
| v2 proof stage, first try | 60 s | stopped at ρ = 8 on a printing error (Python decimal precision too small for 2.7e28); nothing was written. Fixed by raising the decimal precision; rerun below |
| v1 proof stage, by mistake | 47 s | my write of the new file failed and the old script ran again; it only appended a duplicate block to two v1 outputs, which I restored from git |
| v2 proof stage | 48 s | |
| v2 verdict on Part B nodes | 2 s | |
| v2 nodes (all-ball evaluator) | 915 s | 36 evaluations at about 27 s |
| v2 verdict on those | 2 s | |

## What the office should check in v2

- `lo_dec` / `hi_sci`: the printed decimal is re-checked against the ball before printing.
- `walk`: `nxt = P1 if rem <= rho/4 else ...`; the loop ends only when `pos == P1`.
- `step` against Part B's `step`: same recurrence and majorant; tails as balls; extra return values.
- The paragraph "The paths of different k" in §13.

---

# Last task of the window: generality check at spin 9/10

**[model: Fable 5.2] UNVERIFIED.** Seal committed first (620c470, 04:33), then the runs. Write-up:
`ROUTE1_SEGMENT.md` §16; seal: `data/nve/ROUTE1_SEG_9_10_SEAL.md`.

**Where it stopped: after the proof stage and the two end nodes. There is NO certificate at spin 9/10.** The proved M
asks for 141 point evaluations at about 3 minutes each (about 7.5 core-hours); the window had about 35 minutes. The
node file resumes: `nodes 1 arb` then `verdict 1 arb` with `NVE_SPIN=9/10 R1_R0=1.2639` finishes it.

**What is in hand:** the precondition certified; a proved M_F ≤ 4.678E+62 at ρ = 3 with all 471,250 (path box,
k-sub-box) pairs enclosed; Dyson constants 83.64 (lasso) and 478.2 (circle), against 45.8 and 10.5 at spin 3/5; the
all-ball evaluator agreeing with the engine at k = 1, 21/20 and 11/10. Planted zero, held-out points and
proved-M-against-samples were not run (they need the nodes).

**Seal scorecard:** the lasso constant, the best ρ and the precondition held; the circle constant (sealed 40,
measured 478) and the node count (sealed 50, measured 140) were wrong.

## Files added or changed

| file | what |
|---|---|
| `data/nve/ROUTE1_SEG_9_10_SEAL.md` | the seal (620c470) |
| `scripts/_nve_route1_segment_v2.py` | CHANGED: spin and circle radius from `NVE_SPIN`, `R1_R0`; output tag; `safe_step`. Line numbers before the last 10 lines are unchanged; spin 3/5 output is unchanged (checked: see below) |
| `scripts/_nve_route1_floats.py` | CHANGED: circle radius and output file from `R1_R0`, `R1_FLOATS`; defaults as before |
| `scripts/_nve_route1_seg_endnodes.py` | the two end nodes only, with the engine comparison |
| `data/nve/eps/route1_floats_9_10.json` | engine values and lassos at k = 1, 21/20, 11/10, spin 9/10, R0 = 1.2639 |
| `data/nve/eps/route1_seg_9_10_v2.out`, `route1_seg_M_v2_9_10_nseg1.json`, `route1_seg_nodes_arb_9_10.jsonl` | log, proof file, the two node records |

## Slips and things not checked

- **The engine-reference script ran once before my patch to it had applied** (the patch aborted on a failed assert).
  It ran at spin 9/10 with the default circle 1.35 and overwrote three entries of the tracked `route1_floats.json`.
  I restored the file from git at once and reran into `route1_floats_9_10.json`. This was after the seal. F at
  R0 = 1.35 and at 1.2639 came out the same to the digits printed.
- **Two proof-stage attempts at 9/10 stopped on "point too close to the Laurent circle"** before `safe_step` existed.
  Nothing was written by them.
- **Spin 3/5 regression after the spin changes: done.** `prove 1` and `verdict 1 arb` at spin 3/5 reproduce the
  committed `route1_seg_M_v2_nseg1.json` and `route1_seg_verdict_v2_arb_nseg1.json` byte for byte (git shows no
  difference). The duplicate log block that rerun appended was removed by restoring the log from git.
- **The circle's large constant is not diagnosed.**
