# Route (i): input for a FUTURE registration (not a registration; nothing launches). 2026-11-26

**Route (i)** = certifying the claim's main statement over the whole k-range in interval arithmetic, instead of with
50-digit floating-point counts.
**Status:** a design input only. The registration itself must be written, pre-registered and approved (Bridge, Sumit)
before any run.
**Sources:** Fable's plan, `data/nve/EPS_EFFECTIVE.md` Part B (B4, B5). The office check is
`data/nve/EPS_OFFICE_CHECK.md` (Part B section).

## Scope, to be stated explicitly in the registration
- **Target.** For each spin, every REAL k in [ε_a, k_top] satisfies F ≠ 0, tr M0 ≠ 0 and tr M1 ∉ [−2, 2] (circle
  picture; k_top ≈ 4.05).
  - (0, ε_a] is already certified (Statement A, claim v3.1).
  - The top sliver is already interval-certified.
  - Region B (half-plane loops, near 30/7) needs its own design.
- **Real k, not complex rectangles.** The claim is about real k ("for every real k ∈ (0, 30/7]"), and route (i) was
  never registered as a complex argument-principle count. The registration states this choice openly.
- **What stays.** The existing registered floating counts (GAPB, WINDOW, SPIN) are unchanged.

## Method (from B4, office-checked)
- **Point evaluations** of M0 and M1 at Chebyshev points of each k-segment: the validated Arb evaluator of
  `scripts/_nve_route1_proto.py`, reproduced exactly by the office.
- **Interpolation bound** ‖f − p_n‖ ≤ 4Mρ⁻ⁿ/(ρ − 1), with f analytic and |f| ≤ M in the open Bernstein ellipse E_ρ.
  This is ATAP Thm 8.2, read at source in `chebfun.org/ATAP/chap8.m`. Points cos(jπ/n), j = 0..n.
- **k-balls are ruled out** (measured: wrapping inflates them by 10⁴–10⁷).

## Gaps the registration must close FIRST (none is built)
1. **A PROVED M on each ellipse** (B4 steps 1–2): holomorphy boxes around a reference k_c, plus a Dyson bound relative
   to the validated solution at k_c. The demonstration only SAMPLED M at 8 points.
2. **Laurent-disc holomorphy, certified** (the office's finding).
   - The evaluator's Laurent tail uses Cauchy's estimate on |w| ≤ 0.9/a, which needs c0″ holomorphic in the WHOLE
     disc. The code samples |c0″| only on its boundary.
   - It holds for spin 3/5 and k ≲ 3 by the closed-form B roots (|u| = ((10 − k)/(90 − 21k))^{1/4} < 1); the poles of
     φ (|w| = √3/a) and of c_K″ (|w| = 1/a) lie outside.
   - It must be certified per segment by root enclosures. It fails as k → 4 and above, where the Laurent radius or the
     representation of c0″ must change.
3. **Measure the Dyson constant c at k ≠ 0** before fixing the segment lengths. The node count, 100–600 per unit of
   k, rests on c, which is unmeasured away from k = 0.
4. **Generalise the evaluator beyond spin 3/5** (its constants are hard-coded).
5. **Small-F spots:**
   - just above ε_a, interpolate F/k² (|F| ~ |c2|k² ~ 1e−7 to 1e−10);
   - spin 9/10's third zero at k ≈ 0.11 + 0.34i (keep it outside the ellipses);
   - spin 4/5's k\* ≈ 4.0082, where the circle pair is the one to certify.
6. **An independent second implementation,** or an independent rerun, for any verdict. This is the two-implementation
   rule.

## Fleet rules the registration must follow
- **NO job-ending caps** (no wall-clock or step caps). Pressure means pause your own processes and alert.
- **Correctness gates** (a non-finite enclosure, a failed holomorphy box) stop only at a checkpoint.
- **One jsonl line per point evaluation,** keyed (spin, segment, node), so a rerun resumes. `route1_segment.jsonl`
  already does this.
- **Every remaining limit listed beside the time estimate.** B5 estimates 3–20 core-h per spin for region A on a busy
  machine, and under 2 h with the step fix.
- **One core, nice 12,** and the core counts toward the fleet's 9.

## Measured Dyson constants (added 2026-11-26): two columns, certified-as-coded and intrinsic
Optimised-gauge exponent per unit k at k_c = 21/20 (sources: `data/nve/ROUTE1_9_10_OFFICE_DIAG.md`,
`data/nve/ROUTE1_CENTRED_OFFICE.md`).

| | v2 as coded | v3 centred in z | v4 + k-Taylor | intrinsic (float) |
|---|---|---|---|---|
| spin 3/5 circle, point / k-disc (ρ = 4) | 10.5 / 14.3 | 0.415 / 4.30 | 0.415 / 1.039 | 0.36 |
| spin 3/5 lasso, point / k-disc | 45.8 / 72.6 | 9.33 / 41.6 | 9.33 / 15.8 | — |
| spin 9/10 circle, point / k-disc (ρ = 3) | 478 / — | 0.773 / 669 | 0.773 / 8.62 | 0.65 |
| spin 9/10 lasso, point / k-disc | 83.6 / — | 21.8 / 124 | 21.8 / 34.5 | — |
| n (segment [1, 1.1]) | 24 (3/5), 140 (9/10) | 18 (3/5, certified), 134 (9/10) | 12 (3/5), 18 (9/10) | — |

**Two rules for the registration:**
- **Do NOT use any cost estimate built on the as-coded constants,** e.g. Fable's ~250–300 core-h for spin 9/10
  region A. It is an enclosure artifact.
- **Re-estimate the cost** from the v4 column (`data/nve/ROUTE1_KTAYLOR_OFFICE.md`). At spin 9/10 one 0.1-wide
  segment costs about 1.1 core-h of proof plus about 1.5 core-h of nodes (n = 18). The 9/10 circle stays 11× its point
  value on the k-disc (cause not yet measured).
