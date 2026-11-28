# v7 registration: the first stages (V1, V2, P-B, P). Committed before V1's first run

**Office ansatz-machine (Claude Opus), 2026-11-28 (day 0).** Sumit's go via the Bridge: "the v7 FIRST STAGES on the
Mac mini: V1, then V2, then P-B, then P. About 6 core-h in all." Production is **NOT** included.

**Gate:** each stage starts only after the previous one PASSES its criterion below. Every verdict goes to the Bridge.

**Slot:** 1 core while the stop-(c) discriminator runs, then up to 2 cores; nice 10, pause-only guard, under 0.2 GB
per core.

**Plan:** `V7_PLAN_DRAFT.md`, with the loops from `CLOSURE_STOPC_RESULT.md`.

## Why it matters
If v7 certifies the top of the range ([3, 30/7 − δ0]) at a spin, then together with Statement A, route (i) and the
end sliver, every real k in (0, 30/7] at that spin is covered by interval arithmetic, apart from any small-k gap. That
would let the claim's status change in kind at that spin, from numerical to computer-assisted, relative to the chain.
These first stages decide, for about 6 core-h, whether the method can do that before any production is proposed.

## Environment (pinned)
| | v7 stages (Mac mini) | production (Air), for comparison |
|---|---|---|
| Arb side | `.venv313` in this worktree: Python 3.13.12, python-flint 0.9.0 (FLINT 3.6.0), mpmath 1.3.0, numpy 2.4.6, sympy 1.14.0 | Python 3.13.18, python-flint 0.9.0 (FLINT 3.6.0), mpmath 1.3.0, numpy 2.5.0, sympy 1.14.0 |
| 50-digit engine side | repo `.venv`: Python 3.14.5, mpmath 1.3.0, numpy 2.4.6, sympy 1.14.0 | Python 3.14.10, mpmath 1.3.0 |

The arithmetic library is the same build. The interpreter patch releases differ, and so does numpy, which no bound
uses. Each stage's result file re-reads and records the versions.

## A fact the design uses (proved here; checked in SymPy)
B(w, k) = 10(3w − 1)² − k(21w² − 18w + 1). So B(w, k) = 0 with real w ≥ 0 forces
k = g(w) = 10(3w − 1)²/(21w² − 18w + 1), which is REAL. g − 30/7 = 40(3w + 1)/(7(21w² − 18w + 1)), so on w ≥ 0 g takes
exactly the values (−∞, 0] ∪ (30/7, ∞). The denominator's roots are 0.0597 and 0.7974.

**Hence: for every complex k whose real values lie in (0, 30/7], B(u², k) ≠ 0 for all real u.** So the real-axis
quadrature of c0 from z_s to +∞ meets no branch point, for every k-ellipse whose intersection with the real axis lies
in (0, 30/7]. Near k = 0 the branch points approach u = 1/√3, so the quadrature gets costly there. The v7 segments
start at k = 3, where this does not arise.

## V1: the new c0 evaluator (deadline day 7, 2026-12-05)
**Built:**
- **`scripts/_nve_v7_c0.py` (Arb):**
  - c0'' = −√(8/5)·a³·√B(z²/a², k)/(z² + a²)³, with √B continued by continuity: each new value is chosen in the ball
    of the previous one, or an AssertionError is raised;
  - the starting constants c0'(z_s) = −∫_{z_s}^∞ c0'' and c0(z_s) = ∫_{z_s}^∞ (t − z_s)c0''(t) dt, by Arb's rigorous
    integration on [z_s, U], plus an explicit tail bound on [U, ∞) from |√B| ≤ √|a2|·u² + √|a1|·u + √|a0|, added as a
    ball radius;
  - (c0, c0') propagated along any polygon path by Taylor steps of c0'' (acb series), with a Cauchy remainder bound.
- **`scripts/_nve_v7_c0_engine.py` (mpmath, 50 digits):** an independent second implementation, using mp.quad from z_s
  to ∞ and mpmath Taylor steps. It shares only the formula for c0''.

**PASS requires all of:**
- **(a) Exact controls.** At k = 0 (c0 = −2a/(z² + a²)) and k = 4 (closed form with atan, from SymPy), at spins 3/5
  and 9/10, at 10 points (5 on the circle |z| = R0, 5 on the real axis in [R0, 4]):
  - the Arb enclosures of c0 and c0' contain the exact values, with radius ≤ 1e−40;
  - the engine agrees with the exact values to 1e−40.
- **(b) Agreement with the Laurent evaluator** (v2's c0, the one in production) at 10 values of k in [1, 3.7] × 2
  points on the circle, at spins 3/5 and 9/10: the Arb balls overlap, and the engine's value lies in the v7 ball.
- **(c) Closure.** Propagating (c0, c0') once around |z| = R0 at k = 3 and k = 3.9 returns enclosures containing the
  starting values, consistent with `CLOSURE_STOPC_RESULT.md`.
- **(d) Must-fail controls, all of which must FIRE:**
  - (i) a planted error of 1e−30 in c0'(z_s) makes (a) fail;
  - (ii) a planted sign flip of √B mid-path trips the continuity assertion;
  - (iii) k = 4.5 (real, above 30/7) is refused by the B ≠ 0 guard;
  - (iv) a path through a branch point is refused (the step radius reaches the singularity).

**FAIL, or not done by day 7** → stop and report to the Bridge.

## V2: v7 inside the segment certifier (deadline day 10, 2026-12-08)
**Built:** `scripts/_nve_route1_segment_v7.py` = v6 with c0 and its k-dependence taken from V1 instead of the Laurent
series. The ρ-ellipse M bound needs c0 for complex k in the k-box, and V1 accepts acb balls in k. Then a **non-author
read** of the V1 and V2 diffs by an AI session that did not write them.

**PASS requires all of:**
- **T1'.** v7 on the certified segment k ∈ [1, 1.1] at spin 3/5 certifies, with every bound (M_F, n, the error terms)
  no worse than 2× v6's on the same segment.
- **T2'.** The engine gate holds at all nodes.
- **T3'.** The must-fail controls behave: the planted zero is refused, the held-out node passes, the shrunken M is
  caught, and the planted precondition fires.
- **T4'.** v7's checkpoint keys differ from v6's, so nothing is reused across versions.
- The read finds no soundness issue, or every issue found is fixed and re-tested.

**FAIL, or not done by day 10** → stop.

## P-B: region-B port, the premortem's check (deadline day 14, 2026-12-12)
**Built:** the half-plane loops (capsule lasso and Γ disc, inside |z − Z0| ≤ ratio·R_c) in the Arb certifier, with V1's
c0.
- **PASS:** at spin 3/5, single-node Arb enclosures of F, tr M1 and tr Γ at k = 4.2 and k = 30/7 − 1e−6 have
  radius ≤ 1e−3 × |value|, and the engine's values lie inside them.
- **FAIL by day 14** → stop and bring a fresh plan, e.g. a finer centre grid.

## P: three pilot segments at spin 3/5 (deadline day 17, 2026-12-15)
1. Circle picture, k_c = 3.95, half-width 1/20.
2. Region B, k_c = 4.15, half-width 1/20.
3. Dyadic near the endpoint: [30/7 − 2d, 30/7 − d] with d = 1e−3. The ellipse excludes 30/7.

- **PASS:** all three certify, with the engine gate and full controls. Measured core-h per segment is reported.
- **1–2 certify** → report and re-gate.
- **None by day 17** → stop.
- **After P:** the measured core-h per segment and a production projection go to the Bridge, for the value gate
  (outside view, premortem) and Sumit's decision. Production is not part of this registration.

## Predictions (for scoring)

| | P |
|---|---|
| V1 passes by day 7 | 75% |
| V2 passes by day 10 | 65% |
| P-B passes by day 14 | 55% |
| all three pilots certify by day 17 | 45% |
| core-h per pilot segment at 3/5 within 2× of v6's at k ≈ 3 (about 0.6 h) | 50% |
