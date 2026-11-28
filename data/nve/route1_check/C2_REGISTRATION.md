# C2 registration: a k-uniform M machinery (a NEW registered stage after S1). Committed BEFORE any C2 code or measurement

**Office ansatz-machine (Claude Opus), 2026-11-28.** Go from the Bridge, under Sumit's delegation; production still goes
to Sumit. Up to 2 Mac mini cores, nice 10, pause-only guards.

**Time box (kill criterion, a state AND a date):** if C2's pilots have not certified at least one of the three P boxes
by **2026-12-12**, STOP. The top of the range then goes back to Sumit as "parked; numerical grade only", his
good-enough line of 11-25.

## Why it matters
- v7's new parts passed: V1 (both spins), V2 (3/5) and P-B, with the c0 evaluator, the field, the region-B port and
  the second-derivative bound all read as sound.
- Stage P and S1 showed the blocker is the INHERITED M machinery. v2/v4's crude dq bound encloses c0 over Z × K by a
  second-order k-Taylor, c0(k_c) + dk·D0 + dk²E/2, and evaluates dq/dk = (3/8)λλ' by plain ball arithmetic. That
  refuses boxes where the true G-zeros are 0.27–0.45 away, and where it does evaluate, it yields M_F up to 1e253
  (region B, depth 2).
- **Without a k-uniform M that keeps the k-correlation, no top segment can certify,** and the claim's top stays
  numerical.

## Step 0: measure first (a diagnostic; minutes; certifies nothing)
**Question:** on the refused boxes, is the inflation dependency (an artifact) or genuine?
- **Boxes:** P1's refused circle box (1.3213 + 0.2754i, k_c 79/20); P2's base-point box (1.5032, k_c 83/20); S1's
  1e253 segment (k_c 331/80; its largest per-step bound).
- **For each, three numbers:**
  - (a) the crude `dq_sup` value on Z × K (or "refused");
  - (b) the SAMPLED sup of |dq/dk| over Z × K: point k on a 9 × 9 grid of K and 5 points of Z, with dq/dk from the
    field at point k (V1/V2-validated) and an exact formula, no k-Taylor;
  - (c) the sampled sup of |q|, as a sanity check.
- **Reading, fixed now:**
  - (b) finite and (a)/(b) ≥ 1e3, or (a) refused while (b) is finite: **dependency artifact**, and C2's design
    proceeds;
  - (b) itself ≥ 1e6 × its value at k_c (q genuinely explodes on K): **geometry**. No k-uniform rewrite can help. C2
    stops, and the top is parked (numerical grade).
- Each box gets a verdict; the majority decides, and a split is reported.

## Design (chosen after step 0; weighed now)
**(A) Taylor models in dk (Berz–Makino), the Bridge's suggestion.**
- Carry c0, c0', the field's √B, G1, G2, λ, λ' and q as polynomials in dk = k − k_c of degree d, with a rigorous
  remainder ball (acb_poly coefficients plus an error ball).
- Bound sup over K of |dq/dk| by range-bounding the TM derivative.
- **Pro:** keeps the k-correlation through every operation, which is the textbook cure for exactly this blow-up.
- **Con:** needs TM arithmetic with remainders for products, √ and division (1/G) inside the field's Taylor
  propagation, which then becomes bivariate (z-series × dk-polynomials). That is a large new surface, every operation a
  place for a remainder error.

**(B) Cauchy in k from a larger circle (the K-uniform route, reusing validated parts).**
- sup over K of |∂q/∂k| ≤ sup over |k − k_c| = R' of |q(Z, k)| / (R' − R_K), with R_K the radius of the disc
  containing K and R' = 1.5·R_K. This is Cauchy's estimate for a function holomorphic in k on the disc of radius R'.
- The circle is covered by n_arc small k-balls. On each, q(Z, k-ball) comes from the V1/V2-validated field at that
  k-ball. A small radius means little dependency, and there is no k-Taylor.
- Needs a **holomorphy certificate:** G1, G2 ≠ 0 on Z × disc(R'), by a k-sub-box cover of the disc (adaptive). Only
  nonzero-ness, not magnitude, which is far less sensitive to dependency.
- **Pro:** the new mathematics is one textbook estimate plus one certificate, and the evaluators are already read and
  tested.
- **Con:** compute, since n_arc fields (say 16–32) walk the loops in parallel, an estimated 5–30× the current prove.

**Provisional choice: (B)**, because its new-mathematics surface is the smallest, and the review discipline (a read per
new piece) favours that. **(A)** if (B)'s cost probe exceeds 30× the current prove, or its bound is still too loose.
The choice is fixed in an addendum after step 0 and a one-box cost probe, before any pilot.

## Controls (must FIRE before any pilot)
- **Shrunken bound:** the new sup |dq/dk| divided by 1e6 must be caught by v6's sampled-maximum check on the ellipse,
  or, if that cannot see it, by a direct check against step 0's sampled values on the same box.
- **Planted spike:** a step box containing a true zero of G1 (r+), with K the pilot k-box, must be refused by the
  holomorphy certificate (B) or produce an unbounded TM remainder (A).
- **Positive check:** on the three step-0 boxes the new bound must be ≥ step 0's sampled sup, and within 1e3 of it (so
  it is not vacuous).

## Pilots (one attempt each; the same boxes as P)
P1 (circle, k_c 79/20, half 1/20), P2 (region B, k_c 83/20, half 1/20), P3 (region B, k_c 30/7 − 1.5e−3, half 1/2000).
Each runs prove, then verdict with full controls, then the engine gate.

| certified | reading |
|---|---|
| 3 | **C2 works**: a production projection goes to the Bridge and Sumit |
| 1–2 | **partial**: report and re-gate |
| 0 by 2026-12-12 | **STOP**: the top is parked, numerical grade |

## Order
1. This registration.
2. Step 0, with its result committed.
3. The design choice as an addendum, with a cost probe.
4. Code.
5. A non-author read of the design and the code.
6. Controls.
7. Pilots.

## Predictions

| | P |
|---|---|
| step 0 reads "dependency artifact" on at least 2 of the 3 boxes | 70% |
| (B) chosen after the cost probe | 60% |
| at least 1 pilot certifies by 2026-12-12 | 40% |
| all 3 certify | 15% |

## Addendum C2-1 (2026-11-28): the design. CAPD for the monodromy enclosure over k-sub-boxes. Committed BEFORE any build or code
**Inputs:** the tools survey (`C2_TOOLS_SURVEY.md`, fbd33f3), and Quantum's CAPD notes relayed by the Bridge: method
notes from its own runs, not tested on our system.

**Choice: CAPD replaces the Dyson M machinery.** The v7 node values, the engine gate, ATAP, the loops and geometry
(closure, FieldB's disc, free_square) stay unchanged. The fallback, an own Arb Taylor-model layer, is used only if
step 0' fails.

**The system:**
- s = √B carried as a state: ds/dz = B_z/(2s), dc0'/dz = −√(8/5)a³ s/(z² + a²)³, dc0/dz = c0';
- the ρ-equation's 2 × 2 fundamental matrix Y' = [[0, 1], [−q, 0]]·Y, with q rational in (z, k, c0, c0');
- k carried as two constant real states (dk/dτ = 0);
- each straight path segment z = z0 + τh (τ ∈ [0, 1]) is a real ODE in 14 + 2 = 16 dimensions, with every right-hand
  side rational.

**The certificate's M from CAPD:**
- **Covering:** the ellipse box E_ρ (ρ = 4) is covered by k-sub-boxes (as fine as step 0' requires).
- **Initial set,** an affine doubleton in dk, so the k-correlation starts right:
  - x0 = (s, c0, c0') at the base point and k_c, from V1's C0 start (Arb);
  - C = the real Jacobian of (s, c0, c0') in (Re dk, Im dk), from C0's d/dk start (Arb);
  - plus a remainder box from addendum 5's E-type second-derivative bound over the sub-box;
  - Y0 = I.
- **Integration:** both loops (circle or Γ, and the lasso), segment by segment, with CAPD's MPFR C0 solver
  (MpIOdeSolver, doubleton sets).
- **Output:** enclosures of M0(K_j), M1(K_j). Arb then computes F, tr M0 and tr M1 over K_j; M_F, M_T0 and M_T1 are the
  maxima over the sub-boxes, then ATAP as now.

**Rules from Quantum (mandatory):**
- our OWN build of CAPD master at the commit Quantum uses (recorded in the build log; v6.0.0 does not build on
  arm64), with MPFR and GMP from Homebrew;
- the full ctest must pass;
- MPFR intervals ONLY, with a compile-time guard rejecting non-MPFR types;
- after EVERY step: every enclosure finite, and the denominator domains (|s| away from 0, z² + a² ≠ 0, G1, G2 ≠ 0)
  checked on the WHOLE-STEP enclosure; any failure FAILS the sub-box (the box is refused, never silently accepted);
- step sizes logged, since hard shrinkage is the early warning of a near-singular denominator.

## Step 0' (registered now; a cost and width probe; certifies nothing)
- **What:** one k-sub-box of half-side R/5 (KSUB = 5), centred at k_c, for P2 (region B, k_c 83/20) and for P1
  (circle, k_c 79/20).
- **CAPD encloses** M0 and M1 over it, giving F, tr M0 and tr M1 over the sub-box.
- **Point values** of F at the sub-box's 9 × 9 grid come from the Arb evaluator.

**Measured:**
- (a) the CAPD width of F over the sub-box, against the sampled range of F on the grid: the wrapping factor;
- (b) the wall time per sub-box;
- (c) the step-size log.

**Pass bar (fixed now):**
- the CAPD enclosure is finite and contains every sampled F;
- the width of F is at most 100 × the sampled range (so M_F from a covering is within about 2 orders of the truth,
  which ATAP's log turns into at most about +4 in n);
- the projected cost (time per sub-box × the number of sub-boxes covering E_ρ at that size) is at most 2 h per
  segment.

**Fail →** the fallback (an own Arb TM layer), or STOP if the 12-12 box makes that infeasible. Reported either way.

**Order:**
1. this addendum;
2. build CAPD (own copy; the full ctest);
3. the system code (C++ driver plus Python glue), committed;
4. step 0';
5. if it passes: the non-author read of the driver and glue;
6. the controls (a shrunken M; a planted spike, a k-sub-box whose path crosses a singular point, which must be
   refused; a positive check against step 0's samples);
7. the pilots P1/P2/P3, one attempt each.

## Build record (order step 2), 2026-11-28
- **CAPD:** own clone `/Users/sumit/Github/capd-ansatz`, at commit 2f060980d0685cc9bf88352e08c242197cd7d686 (the commit
  Quantum builds, relayed by the Bridge).
- **Deps:** Homebrew gmp 6.3.0, mpfr 4.2.2, cmake 4.4.4, boost 1.92.0; Apple clang 21.0.0.
- **Flags:** `-DCAPD_INTERVAL_TYPE=NATIVE -DCAPD_ENABLE_MULTIPRECISION=ON -DCMAKE_PREFIX_PATH=/opt/homebrew
  -DCAPD_BUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Release`, plus -I/-L for /opt/homebrew.
- **Timing:** built 17:18–17:21 IST.
- **Records:** script and summary in `c2/capd_build_summary.txt`, the full log in `c2/capd_ctest.log`.

**ctest: 41 of 44 pass, 3 FAIL.** The registered condition "the full ctest must pass" was not met as written.
**Bridge ruling, 2026-11-28 (amended wording):** "full ctest" reads as "every rigorous and MPFR test passes, and the
three failures are recorded with their reasons". Quantum's build at the same commit on arm64 shows the SAME three
failures (41/44), accepted there on 2026-10-11 with the same reasoning; cross-reference: Quantum's record
`qsim/capd/CTEST_REPORT.md` (relayed by the Bridge, not read here). Quantum's extra detail: #44 assumes extended
precision, but long double on Apple arm64 is a plain 64-bit double.
- **#7 intervalTest** (`parse_from_sstream`): parsing "[…, 4.324324324]" gives the upper bound 4.3243243240000009, the
  next double above the nearest one. The nearest double lies BELOW the decimal (checked exactly with Python
  fractions), so rounding up is the correct, enclosing behaviour. The test asks for exact equality with the nearest
  double, which would not enclose. This is the NATIVE double interval, which the driver never uses.
- **#43 DPoincareMapMaskTest, #44 SingularNaturalPowerTest:** NON-rigorous double tests whose absolute tolerances of
  1e-12 and 1e-13 are missed by about 1e-12 on arm64. No interval or MPFR code is involved.
- **Passed, among others:** MpIntervalTest, mpsintest, the doubleton, Rect2, CenteredAffine, FactorReorganization,
  C0Rect and Pped set tests, SolverGetStepTest and CnSolverTest.

## Compile-time guard check (Bridge condition 2), 2026-11-28
`scripts/c2_capd/c2_guard_check.sh`, log in `c2/guard_check.log`. The driver's static assertions require the map's
scalar, the solver's scalar and the matrix type to be MPFR intervals (`capd::MpInterval`). Each excluded type is planted
in turn and must FAIL to compile ON THE GUARD's own message ("C2 GUARD"):
- native double intervals (IMap);
- double (DMap);
- long double (LDMap);
- non-interval MPFR (MpMap).
The MPFR-interval build must compile. **Result: PASS** (all four refused by the guard, three guard diagnostics each; the
MpIMap build compiles).

## Addendum C2-2 (2026-11-28): development findings BEFORE step 0'; NOT step 0'. Committed before step 0' runs
These are smoke runs of the driver plus glue, made to debug the plumbing. They are NOT the registered measurement:
- the loops are truncated, retraced out and back (v0 -> v1 -> v2 -> v1 -> v0), so the true monodromy is exactly I for
  every k;
- P2's environment;
- records in `c2/step0p_P2_o20*_smoke*`.

**1. Correctness of the vector field and the exact I/O.** In every smoke run that completed, the Arb walk's monodromy
at kc0 (the v7 field and v2's Taylor walk, an independent implementation) lies INSIDE CAPD's enclosure, on both loops:
- QR policies IdQR and InverseQR;
- sub-box half-sides hs, hs/10 and hs/100 (hs = R/5).

**2. Driver fixes found by the smoke (before any registered run):**
- The end-of-edge check: the set's time is an interval a few ulps wide, so it now requires the final time to lie inside
  it, with a width below 1e-60; the next edge's z-enclosure uses the whole time interval.
- A truncated loop closed by an artificial chord through a pole region was REFUSED by CAPD's "possible division by
  zero". The refusal path works; the smoke then retraced its path instead.

**3. The QR policy: IdQR (B = I), chosen on this evidence.**
- With CAPD's Rect2 QR (FullQRWithPivoting), B mixes all 16 coordinates. On the lasso's return leg the large Y errors
  near the singular point leaked into s: the certified min |s|^2 fell from 296 to 3.8 (true about 210), and the box was
  refused by a "possible division by zero".
- With IdQR the system's block-triangular structure is respected ((s, c0, c0', k) never see Y), and both loops complete.
- InverseQR also completes, but its F enclosure is about 3x wider (+-40.8 against +-13.9).
- No reorganization in any case, so the k-dependence stays in C r0.

**4. How the width scales with the sub-box size** (IdQR, retraced loops; the true F is 0 and the true tr M1 is 2, so
every width is pure overestimate):

| sub-box half-side | F enclosure | tr M1 enclosure | CAPD time |
|---|---|---|---|
| hs = R/5 | +-13.9 | +-4.8 | 88 s |
| hs/10 | +-0.0108 | +-5.3e-3 | 90 s |
| hs/100 | +-1.02e-4 | +-5.1e-5 | 84 s |

- From hs/10 to hs/100 every width falls by exactly 100x: the clean hs^2 regime, the second-order k-curvature an
  affine form cannot carry.
- From hs to hs/10, F falls by 1300x: at the registered R/5 the P2 lasso is BEYOND that regime (a superlinear blow-up).
- Cost: about 0.27 s per CAPD step at 256 bits, order 20.

**What this predicts for step 0' as registered:** at R/5 the width-to-sampled-range bar will likely FAIL at P2. Yet the
sup bound would sit within about 4x of the true |F| (about 4 at P2's centre). The certificate consumes the sup bound
(M_F in ATAP), and the addendum justified the bar by exactly that ("so M_F … is within about 2 orders of the truth").
Whether to amend step 0' before it runs (a scan of sub-box sizes, and/or the bar M_F actually needs) is a design
question put to the Bridge. **Step 0' does not run until it is answered.**

## Addendum C2-3 (2026-11-28): step 0' amended BEFORE it runs (Bridge ruling (B)). Committed before step 0' runs
**Disclosure (it goes in the grading line):** step-0' bar amended (C2-3) after development smoke runs indicated the
registered width/range bar would fail at R/5; the new bar matches the certificate's use (sup bounds). The smoke widths at
R/5, R/50 and R/500 on retraced loops were seen.

**Why:** the certificate consumes only SUP bounds on the ellipse (M_F, M_T0, M_T1 in ATAP). A width/range bar is the
wrong instrument where the true F barely varies over a sub-box; it is mis-specified, not a stricter good bar.

**The amended step 0':**
- **Cases:** sub-box half-sides R/5, R/10 and R/20 (`C2_KDIV` = 5, 10, 20), centred at kc0, at P2 (region B, k_c 83/20)
  and P1 (circle, k_c 79/20), on the FULL loops. Six drives, each with its own 9 x 9 grid of point samples from the node
  evaluator.
- **Decision bar, per case, for EACH of F, tr M0 and tr M1:** the CAPD enclosure is finite; it contains every sampled
  value; and sup|enclosure| <= 100 x the sampled max |.|.
- **What 100x costs:** ATAP's bound is 4M rho^-n / (rho - 1), so a factor of 100 in M costs
  delta n = ln 100 / ln 4 ~ 3.3 extra Chebyshev nodes at rho = 4.
- **Cost bar, unchanged:** (CAPD time per sub-box) x KDIV^2 sub-boxes (the square cover) / 2 cores <= 2 h per segment,
  at the coarsest size that passes.
- **The C2 step 0' verdict:**
  - PASS if some size passes both bars, and that size is the covering for the controls and pilots;
  - FAIL if none does. FAIL on cost alone is reported as a C2 result: first-order doubletons are too expensive here.
- **Still reported, not hidden:** the width/range ratio of F, and the ORIGINAL bar's verdict per case.

**Settings fixed now, never tuned after seeing step 0's numbers:**
- MPFR 256 bits, Taylor order 20, step-control tolerance 1e-15;
- the IdQR doubleton without reorganization (`-DC2_POLICY_ID`).

The tolerance and order were chosen on the smoke loops at hs/10 (records `c2/step0p_P2_*smoke_hs10*`):

| tol | order | time | F width |
|---|---|---|---|
| 1e-30 | 20 | 90 s | +-0.0108 |
| 1e-15 | 20 | 23 s | +-0.0119 |
| 1e-10 | 20 | 18 s | +-0.0127 |
| 1e-15 | 30 | 34 s | +-0.0126 |

1e-15 is 4x faster than 1e-30 for about 10% more width; neither a looser tolerance nor a higher order is worth it. One
point evaluation (v7B) takes about 20 s.

**Run:** `air/c2_step0p_lane.sh A|B` under `air/v7_job.sh` (pause-only guard, nice 10), two lanes. Lane A runs the six
drives and then half the samples; lane B runs the other half. The judge follows. Each lane's log records HEAD and the
driver binary's checksum.

**Prediction (honest, recorded before the run):**
- The original bar FAILS at R/5 at P2 (90%).
- The sup bar passes for F at R/5 at P2 (55%); the full loops wind round the singular point, so the blow-up seen on
  the retraced smoke may be worse.
- Cost per sub-box on the full loops is several minutes, so R/5 meets the cost bar (60%) but R/10 and R/20 do not
  (85%): **cost may bind.**
- C2 step 0' PASS overall: 40%.

## Addendum C2-4 (2026-11-28): ONE post-failure fix after step 0' FAILED (Bridge GO). Committed BEFORE any C2-4 code runs
**Grade line (it goes in every result this addendum governs):** post-failure fix after step 0' FAILED (C2-4: s
eliminated as a state; exact-time stepping). Step 0' itself stays FAILED (`C2_STEP0P_RESULT.md`).

**(a) s = sqrt B is no longer a state.** The system has 14 real dims: c0, c0', Y (2x2 complex) and k (2). s(z, k) is a
closed-form PRINCIPAL root inside the vector field, with the principal root of a complex A = (ar, ai) written as
re = sqrt((|A| + ar)/2), im = ai/(2 re):
- **region B (P2, P3):** s = sqrt_p(B(z^2/a^2, k)), the principal root of B itself.
- **circle (P1):** s = w * sqrt_p(I), with w = z^2/a^2 and I = c2 + c1/w + cc/w^2 (c2 = 90 - 21k, c1 = -(60 - 18k),
  cc = 10 - k), since B = w^2 I.

Certified per step, on the WHOLE-step enclosure (z over the step's time interval, k over the sub-box, as the k-states'
enclosure):
- **(a1) off the cut:** the root's argument A (B, or I on the circle) has lower(|A| + Re A) > 0. Then the principal
  root is continuous on the enclosure, and consecutive steps share their end sets, so along the loop the formula is
  one continuous branch.
- **(a2) circle only:** the inner argument I is certified to lie in the disc |I - I_c| <= 2.4, with I_c = c2(kc0).
  The disc lies in Re > 0 for the pilot k-boxes (Re c2 >= 6.9 there), so (a2) implies (a1) with margin. It is checked
  as a separate guard: certified per step, not assumed.
- **(a3) at the start (glue, Arb):** the formula's value at the base point and kc0 must OVERLAP V1's start value s0
  (the field's carried branch: real, positive at the real base point), and must NOT overlap -s0. So the formula's
  branch equals the field's at the start, and by (a1) on every step thereafter.

Any failure of (a1), (a2) or (a3) refuses the box.

**Changes elsewhere:**
- ds/dz no longer appears, so B_z and the s-row of the initial doubleton go.
- c0's initial rows (and their E-type remainders) are unchanged.
- dc0'/dz = pref s(z, k)/(z^2 + a^2)^3.
- q, G1, G2 as before, with the c0 states.
- The domain checks of addendum C2-1 (z^2 + a^2, G1, G2 != 0 and finiteness) are unchanged.

**(b) Exact time: the driver's own step loop replaces CAPD's TimeMap.**
- Per edge, time runs from j to j + 1.
- Each step's maxStep is the EXACT remainder of the edge (j + 1 - t, a point), and the solver's step control picks
  step <= maxStep.
- After every step the set's time must be a POINT (lower = upper), or the box is refused.
- On a CAPD exception (no validated step) the driver retries with maxStep halved (dyadic, exact). Below 2^-40 it
  refuses.
- The edge ends exactly at j + 1 (asserted as equality of points).

**(c) Step 0'' (once):** the C2-3 bar, settings (256 bits, order 20, tolerance 1e-15, IdQR), sizes (R/5, R/10, R/20),
boxes (P2, P1) and grids are unchanged. The point samples from step 0' are reused (they do not depend on the driver).

**Order:**
1. this addendum;
2. code;
3. development smoke on the retraced loops, with the Arb walk's monodromy contained;
4. a FOCUSED non-author read of (a) and (b), covering (i) the root equals the field's branch at the start and stays
   continuous; (ii) the circle disc is certified per step; (iii) the time stays an exact point, retries halve, and a
   non-point time refuses;
5. the controls below (must fire);
6. step 0'' once.

**Controls (must FIRE before step 0''):**
- **(K1) planted branch error:** the start value of the s-branch with the WRONG sign (-s0 handed to the glue's start
  match). It must be refused by (a3).
- **(K2) planted cut crossing:** a region-B formula step whose enclosure crosses B's cut (a segment from bB toward a B
  branch point, as in control (B) of `_nve_v7_controlsB.py`, with the disc guard set aside). It must be refused by (a1).
- **(K3) planted circle disc:** the disc radius 2.4 replaced by 0.01. It must be refused by (a2).
- **(K4) planted time:** a non-dyadic maxStep injected once. The non-point time must be refused by (b).

**If step 0'' FAILS:** C2-via-CAPD is FAILED. I report the fallback-or-STOP choice to the Bridge; there is no third
mechanism without a new ruling. The 2026-12-12 time box stands.

**Predictions (recorded before any C2-4 code):**
- (a) removes the observed blow-up of s: 70%;
- step 0'' passes the sup bar at some size: 45%;
- given a pass, cost binds at R/10 or finer: 60%.

### C2-4 erratum E1 (2026-11-28; committed before any C2-4 code runs)
(a2)'s numbers were wrong, written from a single-k estimate. For P1's ellipse box (k_c 79/20, R = upper(half (4 + 1/4)/2),
|dk| <= sqrt 2 R):
- Re c2 drops to about 4.82, not ">= 6.9";
- the inner argument's spread obeys |I - c2(kc0)| <= 21|dk| + |c1|/|w| + |cc|/|w|^2 <= 6.128 on the circle's chords,
  with |w| >= (1.35 cos(pi/96))^2/a^2 = 5.057 (computed in Arb).

A radius of 2.4 would have refused every P1 box for a reason of my own making. **Corrected (a2):**
- the disc radius is **6.5**;
- the disc's leftmost point is Re c2(kc0) - 6.5 = 0.55 > 0, so (a2) still implies (a1);
- (a1) stays checked separately.

Control (K3) is unchanged: the radius planted at 0.01 must refuse.

### C2-4 development notes (code committed before the focused read; NOT step 0'')
- **Exact time in practice.** CAPD's step control returns 5-bit dyadics or exactly maxStep, but its first-step
  initialisation uses h = min(1/Lipschitz, 1, maxStep), which has a full mantissa. CAPD re-initialises at a loop's
  start, after a retry, and at new edges. So every edge start and every retry is a "fresh" step whose maxStep is capped
  at the dyadic 2^-6. Guard (b) caught each inexact time during development (records `c2/step0pp_*smoke*`), and still
  refuses any inexact time.
- **The (a1)/(a2) guards are applied twice:** a priori over each whole edge x the k-box (tau bisected to depth 10), and
  on every step's whole-step enclosure.
- **The (a2) disc centre** is the exact midpoint of c2(kc0), within 1e-76 of it; the 0.55 margin absorbs that.
- **Control (K4)** plants the non-point time directly (the set's time widened by [0, 2^-80] once). A planted non-dyadic
  maxStep may never fire, because the step control can choose a smaller step, so it is not used.
- **Smoke on the retraced loops** (the true M is I), with the Arb walk's M at kc0 contained in every run:

  | case | F | tr M0 | tr M1 | earlier s-state version |
  |---|---|---|---|---|
  | P2 hs/10 | +-0.0118 | +-1.7e-5 | +-5.9e-3 | F +-0.0119 |
  | P1 hs/10 | +-3.5e-3 | | | |
  | P2 R/5 | +-19.1 | | +-5.4 | F +-13.9 |
  | P1 R/5 | +-0.75 | | | |

  The P2 lasso at R/5 is Y's own k-nonlinearity near the lasso's singular point; it is not the s blow-up that (a)
  removes.
