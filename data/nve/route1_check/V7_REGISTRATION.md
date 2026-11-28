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

## Addendum 1 (2026-11-28, the Bridge's read; committed before V1's first run): radius bars, so (b) and (c) can fail
- **V1(b):** at every one of the 20 points, BOTH the v7 ball and the Laurent ball (for c0 and for c0') must have
  radius ≤ 1e−30. Overlap then counts as agreement. If either ball is wider at any point, (b) is **UNINFORMATIVE**, not
  PASS.
  - The bar is a fixed 1e−30, not derived from the Laurent series' own tolerance.
  - Both evaluators work at 256 bits (about 77 digits), so 1e−30 leaves wide room for honest enclosures while making a
    vacuous overlap impossible.
- **V1(c):** after one circuit of |z| = R0, the returned enclosures of c0 and c0' must have radius ≤ 1e−30 AND contain
  the starting values. A wider returned ball makes (c) **UNINFORMATIVE**, not PASS.
- **V1(a)** already has a bar (radius ≤ 1e−40). Unchanged.

## Addendum 2 (2026-11-28, before the registered V1 tests run; one smoke call of start() was made, with no test points)
- "The engine's value lies in the v7 ball" (V1(b), and the engine half of V1(a)) is read with the engine's own
  precision. The 50-digit mpmath engine value is taken as a ball of radius 1e−40, and that ball must overlap the v7
  ball. The v7 balls are about 1e−70 wide at 256 bits, so a literal containment would fail on the engine's precision,
  not on any disagreement.
- The bar for disagreement stays as tight as the engine allows: 1e−40, the same bar as V1(a).

## Addendum 3 (2026-11-28, the Bridge's ruling on V1 at 9/10, option (b); committed BEFORE the rerun)
- **What reruns:** V1(b) at spin 9/10 ONLY, with the production Laurent evaluator (v2's `laurent`/`c0_at`, the same
  formula) at N = **386** terms instead of production's NW = 190. Everything else is as registered, and the engine JSON
  is reused unchanged.
- **How N was chosen, fixed in advance:** the smallest N such that the evaluator's OWN truncation bound is ≤ 1e−35 for
  both c0 and c0' on |z| = R0 = 1.2639, at all 10 test values of k.
  - The bound is t = M·θ^(N+1)/(1 − θ), divided by |w|² for c0 and by |w| for c0', with θ = |1/z|/(0.9/a) = 0.79120.
  - M is the evaluator's Cauchy bound of c0'' on |ω| = 0.9/a (independent of N), computed per k: from 2.74e3 at
    k = 1 to 1.03e3 at k = 3.7.
  - The per-k minima are N_k = 382–386, so N = max_k N_k = 386.
- **Bar unchanged:** both balls ≤ 1e−30 at all 20 points. If the Laurent balls are still not under it, (b) at 9/10 stays
  **UNINFORMATIVE**, is reported, and N is NOT raised again.
- **Gate per spin:** nothing in v7 runs at 9/10 until V1 passes at 9/10. V2 proceeds at 3/5, where V1 passed.

## Addendum 4 (2026-11-28): the non-author read, its fixes, and the redesigned controls. Committed BEFORE the re-tests
**The read** was by a separate AI session with fresh context, which wrote none of the code. It found no definite
soundness bug in `start`, the Taylor remainders, the adaptive `sup_box` cover (graded rigorous), `Field.box`,
`precondition7` or F1b. Its five actionable items:
1. **(DOUBTFUL)** The branch at each step's end was chosen with the √B series truncated, with no remainder. Fix: the
   prediction carries the Cauchy tail MS·θ^N/(1 − θ), with MS = sup |√B| from `sup_box`, so the branch comparison is
   rigorous.
2. **(VACUOUS)** Control (ii) as corrected negated the chosen branch after the same comparison chose it, so it fired
   by construction. **Replaced:** a planted branch error (the prediction negated at step 3 of a circuit at k = 3)
   must make the CLOSURE check fail. That is a downstream gate catching a wrong branch.
3. **(VACUOUS)** Control (iv) was caught by the floating-point distance guard and never reached the rigorous one.
   **Added (iv'):** `sup_box` on a Cauchy square covering a k = 3 branch point must refuse. Control (iv) is kept.
4. **(DOUBTFUL)** `step` changed the global series cap in the middle of v2's step. Fix: saved and restored.
5. **(DOUBTFUL)** F1b had no must-fail control. **Added:** `scripts/_nve_v7_controls.py`. A corrupted carried branch
   in a cached field state must make F1b fire, and a clean field must not.

**Also fixed (NOTE items):**
- the start integrals are checked for finiteness;
- ρ_safe uses Arb roots of B, not float midpoints;
- fields are keyed by the exact midpoint and radius of k.

**Re-tests, in order, each before the next stage counts:**
- V1 in full at both spins, with (d) now (i), (ii) as replaced, (iii), (iv) and (iv'). PASS criteria otherwise as
  registered, with addenda 1–3.
- The F1b control: PASS = the corrupted branch fires and the clean field passes.
- T1'–T4' on the fixed code.

**The earlier T1' run** (launched 15:22:50 on the pre-fix code, 3724663) is a **development run**. Its outputs carry
the pre-fix code hash and count for nothing.

## Addendum 5 (2026-11-28, the Bridge's condition before pilots 2 and 3): the region-B k-uniform bound for d²c0/dk², derived before any code
**Why it is needed.** The segment certificate's M bound needs sup |dq/dk| on (step box Z) × (k-box K). v2/v4 get it from
c0 and dc0/dk at k_c (now the field's) plus a Taylor-in-k remainder with E = d²c0/dk² and d²c0'/dk² enclosed on Z × K.
v2's `d2kc0` encloses E by an integral along the ray from z to ∞, with a guard Re(1 − kφ) > 0. In the half-plane that
ray and guard are not the natural ones. Region B's single-valued domain is the disc D = {|z − Z0| ≤ R_d}, with
R_d = 0.9 R_c and R_c a certified lower bound of the distance from Z0 to c0's singular points over K (the FieldB disc).

**Representation (exact, for every k in K and every z in D).** Let bB be the real base point, in D. Then:
- c0'(z; k) = c0'(bB; k) + (z − bB) ∫₀¹ c0''(t(τ); k) dτ,
- c0(z; k) = c0(bB; k) + c0'(bB; k)(z − bB) + (z − bB)² ∫₀¹ (1 − τ) c0''(t(τ); k) dτ,

where t(τ) = bB + τ(z − bB) is the straight segment, which lies in D because D is convex. The base values come from
the s = 1/t integrals along the real axis, as V1's `start`:
- c0'(bB; k) = √(8/5)·a ∫₀^{1/bB} s²·√P(s, k)/(1 + a²s²)³ ds,
- c0(bB; k) = −√(8/5)·a ∫₀^{1/bB} (s − bB s²)·√P(s, k)/(1 + a²s²)³ ds,

with P(s, k) = (90 − 21k) − (60 − 18k)a²s² + (10 − k)a⁴s⁴, and c0''(t; k) = −√(8/5)·a³·√B(t²/a², k)/(t² + a²)³.

**Second k-derivatives.** P and B are linear in k, so ∂²P/∂k² = ∂²B/∂k² = 0 and
- ∂²_k √P = −(∂_k P)²/(4 P^{3/2}), with ∂_k P = −21 + 18a²s² − a⁴s⁴;
- ∂²_k √B = −(∂_k B)²/(4 B^{3/2}), with ∂_k B = −(21w² − 18w + 1), w = t²/a².

E0 = ∂²_k c0 and E1 = ∂²_k c0' on Z × K are therefore the same four integrals, with √P and √B replaced by their second
k-derivatives (differentiation under the integral sign: the integrands are holomorphic in k on a neighbourhood of K,
by the guards below).

**Enclosure (rigorous; the rectangle rule as in `d2kc0`).**
- [0, 1] in τ, and [0, 1/bB] in s, are each covered by SM closed balls T_j (asserted to cover).
- For a holomorphic integrand g, ∫₀¹ g ∈ (1/SM)·Σ_j g(T_j), each g(T_j) an Arb enclosure on the ball, with K the
  whole k-box and Z the whole step box. No sampling.

**Guards; any failure returns "not certified", so the row is refused, fail closed:**
1. **Base integrals:** Re P > 0 on every s-ball × K. By the reader's V1 argument, P ∉ (−∞, 0] there, so the principal
   √P is the global branch, and P^{3/2} = P·√P is nonzero.
2. **Segment integrals:** on every τ-ball × Z × K, the ball of B excludes 0 AND lies in one open half-plane avoiding
   the cut (Re B > 0, or Im B > 0 throughout, or Im B < 0 throughout). So the principal √B is continuous on the ball.
   Its sign σ_j ∈ {±1} is fixed by the field at k_c: σ_j·√B(t_mid, k_c) must be certified closer to the field's
   carried s(t_mid) than its negative. The segment from bB to every point of Z must lie in D (|t − Z0| ≤ R_d,
   certified on every ball).
3. **The k-box K:** Re k < 30/7 on K, so P(0, k) = 90 − 21k has positive real part. For the dyadic pilot near 30/7 this
   is the ellipse condition ρ + 1/ρ < 6.

**Must-fail controls (both must fire before any pilot uses the bound):**
- (A) A shrunken bound: E0/1e6 on a pilot-2 step box must be refused by v6's sampled-maximum check on M (the existing
  shrunken-M control, run with the scaled E).
- (B) A planted spike: a step box whose straight segment from bB crosses a c0 branch point, outside D. Guard 2 must
  refuse it.
- Plus a positive check: at k_c, E0 and E1 must overlap the central finite difference of the field's dc0/dk (the
  v2 selftest's second-derivative test).

**Order:** this addendum, then the code (committed), then the non-author read of the derivation AND the code, then
controls (A) and (B), then pilots 2 and 3.
