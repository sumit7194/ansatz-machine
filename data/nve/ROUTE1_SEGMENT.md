# Route (i): the first certified segment (spin 3/5, E = 4/5, real k ∈ [1, 1.1])

**[model: Fable 5.2] UNVERIFIED until the office ansatz-machine checks it.** 2026-11-26. Answers
`docs/BRIEF_FABLE_ROUTE1_SEGMENT_2026-11-26.md` (brief v1). Branch `fable/2026-11-26-route1-seg`.
A single-segment build-and-measure step, not the route-(i) registration.

**Version 2 (same day, the Bridge's follow-up): see §13–§15.** Every bound is now a ball from the first evaluation
to the printed verdict numbers, the enclosure of dq/dk is asserted complete, and the gauge is spelled out. The
verdict and all three lower bounds are unchanged. §0–§12 describe version 1 (commit 604d520) and are left as written,
except where a line says "v2".

## 0. Result

**VERDICT: CERTIFIED.** For every real k ∈ [1, 1.1], at spin 3/5 and E = 4/5:

- F(k) ≠ 0, with |F(k)| ≥ 0.26502;
- tr M0(k) ≠ 0, with |tr M0(k)| ≥ 1.99315;
- tr M1(k) ∉ [−2, 2], because |Im tr M1(k)| ≥ 2.64882.

M0 is the circle |z| = 1.35 and M1 the engine's lasso polygon of k = 21/20, both kept fixed over the segment.

| quantity | value |
|---|---|
| Laurent-disc precondition on the k-box used | certified; largest root \|w\| ≤ 0.4868 against the limit 1.2346 |
| proved M on the k-disc \|k − 21/20\| ≤ 0.1063 | M_F = 6.57e10, M_trM0 = 9.22, M_trM1 = 1.54e4 |
| Bernstein ρ, nodes | ρ = 4, n = 24 (25 Chebyshev points) |
| proved interpolation error | F 3.11e−4, tr M0 4.4e−14, tr M1 7.3e−11 |
| all six controls | behaved as required; the shrunken-M control is uninformative for the verdict and the held-out test (§7) |
| wall time | 39 s proof + 25 × 22 s nodes + 11 × 22 s control evaluations ≈ 14 min, one core |

One sealed prediction was wrong: the proved M_F (6.6e10) is above the predicted range 1e2–1e8. The others held (§8).

The method differs from the brief's sketch in two places, both stated in §2: the perturbation is bounded through
dq/dk in ball arithmetic instead of the closed form with a binomial majorant, and the Dyson bound is taken in an
optimised constant gauge. Without the gauge the lasso's Dyson constant is 598 per unit k instead of 46, and the node
count would have been in the hundreds.

## 1. What is certified, and what is only argued

**Certified in ball arithmetic** (Arb through python-flint 0.9.0, 256 bits):

1. The Laurent-disc precondition, for every k in the square of half-side R = 0.1063 around 21/20 (§4).
2. On boxes covering both loops, for every k in the disc |k − 21/20| ≤ R: G1 ≠ 0, G2 ≠ 0 and Re(1 − kφ) > 0 along
   the radial rays. So q(z; k) is holomorphic in k there, and no singular point of the equation reaches either loop.
3. An enclosure of dq/dk on the same boxes, hence |q(k) − q(k_c)| ≤ R·sup|dq/dk|.
4. The reference solution at k_c = 21/20 on every step segment (not only at step ends).
5. The proved M on the disc, by the Dyson bound (§5).
6. The 25 node values, each a validated point evaluation (the Part B evaluator, unchanged).
7. The interpolant's enclosure on 128 sub-balls of the segment, with the all-finite assert, ± the proved error.

**Argued or taken from elsewhere, not certified here:**

- **The interpolation theorem** (ATAP Thm 8.2). The office read it at source (`EPS_OFFICE_CHECK.md` B1); I did not
  re-read it this round.
- **The Dyson chain itself** (§2 steps 4–5) is a hand derivation. The code certifies its inputs, not the algebra. The
  derivative rule and the two integral formulas are sympy-checked (§3); the norm identities are not machine-checked.
- **The Taylor-tail majorant of the point evaluator** (Part B, office-checked as a prototype).
- **The lasso's homotopy class at k_c.** The polygon is the engine's own vertex list at k = 21/20. Item 2 certifies
  that the class cannot change inside the disc; it does not certify that the engine's class at 21/20 is the intended
  one.
- **Upward rounding of the final float steps.** Sums are in Arb; the last conversions (exp, the M products, the
  error formula) are Python floats, each inflated by 1 + 1e−7. This is not directed rounding.
  **v2: closed.** See §13.
- **The two-implementation rule.** This is one implementation.

## 2. The method

Write v″ + q v = 0 with q = (3/16)λ², λ = G1′/G1 − G2′/G2, G2 = f0² + c0², G1 = E²G2 − f0 (as in Part B).

1. **Precondition** (§4).
2. **Reference.** The validated solution Φ_c at k_c along both loops, normalised to I at the base point. On each
   Taylor step the two local solutions are enclosed on the whole step segment: the Taylor polynomial on a ball that
   contains the segment, plus the step's own tail bound. This gives enclosures (a1, a2) of the first row (v1, v2) of
   Φ_c on every piece of path.
3. **Perturbation.** For a ball Z containing a step segment, and k in the disc:
   - d c0/dk and d c0′/dk at k_c come from the k-derivative of the Laurent series, with its own Cauchy tail on
     |ω| = 0.9/a (the same precondition covers it).
   - Their variation over the disc is the second k-derivative times (k − k_c). The second derivative is a radial
     integral from infinity, enclosed by a rectangle rule on 24 balls of s ∈ [0, 1].
   - The k-square is cut into 5 × 5 sub-boxes. On each, c0 = c0_c + δk·D0_c + δk²·E0/2 and D0 = D0_c + δk·E0.
   - dq/dk = (3/8)·λ·∂_kλ, with ∂_kλ evaluated in the combined form (2b) of §3. The uncombined form loses a factor
     1.2–6 to cancellation (measured in the first run, kept in `route1_seg_3_5_dev.out`).
   - The disc is convex, so |q(z; k) − q(z; k_c)| ≤ |k − k_c|·sup|dq/dk|.
4. **Dyson bound in a constant gauge C.** Write Y_k = Φ_c C T C⁻¹. Then T′ = −Δq·(Φ_cC)⁻¹E21(Φ_cC)·T, T = I at the
   base point. Because det Φ_c = 1 (Abel; no first-derivative term), the rank-one matrix has 2-norm
   |(v1, v2)C|²/|det C|. So ‖T‖₂ ≤ e^I with
   I = R·Σ_steps sup|dq/dk|·sup|(v1, v2)C|²·|h| / |det C|.
   Any C gives a valid bound. C is chosen in floats to minimise the sum: C C† = √(det W)·W⁻¹ with
   W = Σ sup|dq/dk|·|h|·r†r, r = (v1, v2). The certificate then recomputes the sum for that C in ball arithmetic.
5. **M.** ‖M(k)‖_F ≤ ‖M_c C‖_F·‖C⁻¹‖_F·e^I; |tr M(k)| ≤ √2·‖C⁻¹M_cC‖_F·e^I;
   |F(k)| ≤ 2 + ‖M1(k)‖_F²·‖M0(k)‖_F² (2 × 2 and det 1, so ‖X⁻¹‖_F = ‖X‖_F).
6. **Interpolation.** The Bernstein ellipse E_ρ of [1, 1.1] lies in the disc of radius R = 0.05(ρ + 1/ρ)/2 around
   21/20. ATAP Thm 8.2: ‖f − p_n‖ ≤ 4Mρ⁻ⁿ/(ρ − 1).
7. **Node values** at cos(jπ/n) mapped to k. Each evaluation is at the midpoint of the ball that holds the exact
   node, so the value is widened by (M/(R − 0.05))·(ball width), by Cauchy's estimate. The widening is about 1e−60.
8. **Verdict.** The interpolant by the Chebyshev recurrence on 128 sub-balls of t ∈ [−1, 1]. F and tr M0: the lower
   bound of |p| must exceed the error bound. tr M1: |Im p| must exceed the bound, or |Re p| − 2 must.

**Two departures from the brief's sketch.**

- **The perturbation bound.** The brief proposed the closed form P = P_c(1 + γ_c s_c) with a binomial majorant along
  the rays. I used the mean-value bound through dq/dk instead. It has no subtraction either, it needs no lower bound
  on |1 − k_cφ| along the rays beyond Re(1 − kφ) > 0, and it reuses the Laurent machinery. The closed form is
  sympy-checked (§3) but not used.
- **The gauge.** In the base-point basis the lasso's Dyson constant is 598 per unit k. The optimised gauge gives 46.
  The price is the factor ‖M_cC‖_F‖C⁻¹‖_F = 11.7 in place of ‖M_c‖_F = 7.18.

## 3. The closed form referenced to k_c, and the sympy checks

`scripts/_nve_route1_kc_identity.py` → `data/nve/eps/route1_seg_identity.out` (sympy 1.14.0; every difference
simplifies to 0):

- **(1) The generalised closed form.** With δ = c0 − c0_c: G2 = G2_c(1 + σ_c), σ_c = (2c0_cδ + δ²)/G2_c, and
  P = P_c(1 + γ_c s_c), s_c = σ_c/(1 + σ_c), γ_c = f0/(G2_c P_c).
- **(2) The derivative rule:** dq/dk = (3/8)λ·∂_kλ with
  ∂_kλ = ∂_kG1′/G1 − G1′∂_kG1/G1² − ∂_kG2′/G2 + G2′∂_kG2/G2².
- **(2b) The combined form the certifier evaluates:** ∂_k log P = 2f0c0D0/(G1G2), and
  ∂_kλ = 2(f0′c0D0 + f0c0′D0 + f0c0D1)/(G1G2) − [2f0c0D0/(G1G2)]·(G1′/G1 + G2′/G2), with D0 = ∂_kc0, D1 = ∂_kc0′.
- **(3) The radial integrals** c0 = z⁻²∫₀¹(s − s²)g(s/z)ds and c0′ = −z⁻³∫₀¹s²g(s/z)ds, against the Laurent rule on
  monomials.
- **(4) The closed-form roots** of 1 − kφ(w) = 0, and the ω-form of φ used in the code.

A numerical self-test that can fail runs inside the proof stage, at five points of the loops: the Laurent k-derivative
against central differences in k (agreement 4e−16 to 3e−15), the second-derivative enclosure against its finite
difference (overlaps), and |FD of q| ≤ sup|dq/dk| at a point (ratio 1.000000 at all five).

## 4. The Laurent-disc precondition

c0″ = c_K″√(1 − kφ) must be holomorphic on the whole disc |ω| ≤ 0.9/a (ω = 1/z). In w = z²/a² the disc is
|w| ≥ 1/0.81 = 1.2346, so every singular w must satisfy |w| < 1.2346:

- zeros of 1 − kφ: w = [(30 − 9k) ± √(60k(k − 4))]/(90 − 21k), enclosed for k in a complex box;
- the pole of φ at w = 1/3 and the poles of c_K″ at w = −1.

On the box used (half-side 0.1063 around 21/20) the largest root modulus is ≤ 0.4868. The check passed on every box
tried, up to half-side 0.2525 (largest root 0.6346).

**Where it fails.** For k > 4 the roots are real and one runs to −∞ as k → 30/7. It crosses |w| = 1.2346 at
k ≈ 4.006 (hand estimate). The planted control at k = 4.2 fires (§7).

## 5. The proved M, and the choice of (ρ, n)

Reference at k_c = 21/20: 2163 steps on the circle, 703 on the lasso; ‖M0‖_F ≤ 1.4264, ‖M1‖_F ≤ 7.1788.

| ρ | R | I0 (circle) | I1 (lasso) | M_F | M_trM0 | M_trM1 | n for 1e−3 | error bound on F |
|---|---|---|---|---|---|---|---|---|
| 3 | 0.0833 | 1.104 | 5.424 | 2.88e8 | 6.09 | 1.54e3 | 26 | 2.3e−4 |
| **4** | **0.1063** | **1.518** | **7.711** | **6.57e10** | **9.22** | **1.54e4** | **24** | **3.1e−4** |
| 5 | 0.1300 | 2.021 | 10.630 | 6.34e13 | 15.2 | 2.91e5 | 26 | 4.3e−5 |
| 6.5 | 0.1663 | 2.976 | 16.559 | 6.38e19 | 39.6 | 1.13e8 | 28 | 8.0e−4 |
| 8 | 0.2031 | 4.250 | 25.181 | 2.69e28 | 142 | 6.50e11 | 36 | 4.7e−5 |
| 10 | 0.2525 | 6.688 | 43.741 | 5.25e46 | 1.62e3 | 7.97e19 | 50 | 2.3e−4 |

**The trade-off.** A larger ρ converges faster per node but needs a larger k-disc, and the Dyson exponent grows with
the disc. The node count is flat between ρ = 3 and ρ = 6.5 (24–28) and rises beyond. ρ = 4 was chosen as the
smallest n (n is kept even so that k_c is a node).

**What dominates M_F.** M_F = 2 + (g1·e^{I1})²·(g0·e^{I0})², with gauge factors g0 = 2.15 and g1 = 11.69. At ρ = 4
the exponential part is e^{2(I0+I1)} = e^{18.5} ≈ 1e8 and the gauge factors give 630. The sampled |F| on the same
ellipse is 0.363, so the proved M overestimates by a factor 1.8e11. The Dyson bound is a norm bound: it cannot see
the cancellation in the oscillating integrand. The true k-sensitivity of tr M1 is about 0.2 per unit k (from the
engine's values at k = 1 and 1.1), against a norm integral of 46.

## 6. The verdict

From `data/nve/eps/route1_seg_3_5.out`:

```
  sub-segment 0 (k_c = 1.050000; rho = 4.0, n = 24; proved M_F = 6.565e+10, M_trM0 = 9.216e+00, M_trM1 = 1.543e+04):
    F:     min |p| >= 0.265334; proved error bound 3.110e-04  -> F != 0: True
    tr M0: min |p| >= 1.993158; proved error bound 4.366e-14  -> tr M0 != 0: True
    tr M1: min over sub-balls of max(|Im p|, |Re p| - 2) >= 2.648821; proved error bound 7.311e-11  -> tr M1 not in [-2, 2]: True
  certified min |F| on [1, 1.1] >= 0.265023
  VERDICT: CERTIFIED  (F != 0, tr M0 != 0, tr M1 not in [-2, 2] for every real k in [1, 1.1])
```

## 7. Controls

| control | must | outcome |
|---|---|---|
| planted zero (F − F(k_c), same segment, same nodes) | refuse | **refused.** min \|p\| ≥ 0 against a bound 3.1e−4 (k_c is a node, so the interpolant is 0 there) |
| planted precondition at k = 4.2 ± 0.01 (complex box) | fire | **fired.** A root has \|w\| up to 10.41 ≥ 1.2346. Also fires at 4.01 ± 0.001 (1.343); certifies at 4.0 ± 0.001 (1.0996) and at 1.05 ± 0.2 (0.5789) |
| held-out points (3 non-node k) | overlap interpolant ± bound | **consistent** at t = −5/8, 1/8, 3/4. \|p − f\| ≤ 1.4e−7 (F), 9.2e−11 (tr M0), 1.3e−10 (tr M1); all enclosures overlap |
| proved M ≥ sampled (8 points of the ρ = 4 ellipse) | every sampled value ≤ M | **true.** Sampled max \|F\| 0.3629, \|tr M0\| 1.9950, \|tr M1\| 2.8860 against 6.57e10, 9.22, 1.54e4 (overestimates ×1.8e11, ×4.6, ×5.3e3) |
| engine at two nodes (k = 1 and k = 11/10) | inside the node enclosures | **inside,** all six values (F, tr M0, tr M1 at both ends); node radii 4e−9 to 6e−9 on F, 4e−12 to 5e−12 on the traces |
| shrunken M (bounds ÷ 1e12) | something breaks, or say why not | **nothing breaks in the verdict or the held-out test** (uninformative there; reason below). The shrunken M does fall below the sampled maximum for all three functions, so control 4 refuses it |

Notes:

- **Proved M ≥ sampled.** Part B's stored samples sit on the ρ = 8 ellipse, which reaches outside the disc used here,
  so the 8 samples were rerun on the ρ = 4 ellipse.
- **Engine.** The engine's stored values at k = 1 and 11/10 use the engine's own lasso of that k; the node values use
  the lasso of 21/20. Agreement is therefore also a check that the fixed lasso stays in the engine's class.
- **Why the shrunken M breaks nothing in the verdict.** The true interpolation error at n = 24 is far below even the
  shrunken bound (3e−16): F is analytic well beyond the ρ = 4 ellipse, and Part B reached 1e−7 with 8 points. The
  held-out differences are limited by the node radii (1e−9 on F), not by interpolation. So this control cannot
  detect a wrong M here; only the comparison with sampled values can. The finding is that the proved M asks for about
  three times more nodes than the function needs.
- **Derivative self-test** (§3) is a seventh control; it passed.
- **A loose first verdict, kept in the log.** The first verdict run enclosed the interpolant on t-balls by the
  three-term recurrence, which inflates like 2.4^m on a wide ball. It certified, but with |F| ≥ 0.1500 only. The
  second run uses balls of θ with T_m(cos θ) = cos(mθ) and gives 0.2650. Both blocks are in `route1_seg_3_5.out`;
  the node values are the same.

## 8. Sealed-prediction scorecard

| office prediction | outcome |
|---|---|
| Laurent precondition certifies at k ∈ [1, 1.1]; fails at large k | **held.** Certified on every box tried; fires at 4.2 |
| proved M_F between 1e2 and 1e8 | **WRONG.** 6.57e10 at the chosen ρ = 4 (2.88e8 at ρ = 3) |
| nodes for a certified error ≤ 1e−3: between 10 and 40 | **held.** n = 24 (25 points) |
| certified min \|F\| on [1, 1.1] ≥ 0.26 | **held.** ≥ 0.26502 (the engine gives 0.26533 at k = 1, where \|F\| is smallest) |
| the certificate succeeds (≈ 70%) | **held.** Certified |
| wall time 15–60 min on one core of a busy box | **just under.** ≈ 14 min, on a reserved core at normal priority |

## 9. The measured Dyson constants (the missing input of B5)

Exponent per unit |k − k_c| at k_c = 21/20, spin 3/5:

| loop | base-point basis | optimised gauge, K a point | optimised gauge, on the k-disc R = 0.1063 |
|---|---|---|---|
| circle \|z\| = 1.35 | 11.3 | 10.5 | 14.3 |
| lasso of k = 21/20 | 598 | 45.8 | 72.6 |

- ∫ sup|dq/dk| |dz| is 5.56 on the circle and 41.3 on the lasso.
- The growth from the point to the disc (46 → 73) is partly real and partly box overestimate. With one k-box instead
  of 5 × 5 the lasso figure at the same R was 194.
- For comparison, the brief quotes about 80 per unit k for Part A's lasso constant at k = 0, in its own form.

**The same constants at other k** (`scripts/_nve_route1_consts.py` → `route1_seg_consts.out`; a measurement, not a
certificate; no point evaluations were run there). Each row uses the engine's lasso of that k and a segment of
half-width 0.05 around it, with the tolerance scaled to |F(k_c)| as on the certified segment:

| k_c | \|F(k_c)\| | circle, point | lasso, base basis | lasso, optimised, point | best (ρ, n) | lasso on that box |
|---|---|---|---|---|---|---|
| 1/2 | 0.0597 | 9.97 | 545 | 41.5 | (4, 24) | 62.3 |
| 21/20 | 0.2958 | 10.5 | 598 | 45.8 | (4, 24) | 72.6 |
| 2 | 1.362 | 11.8 | 741 | 57.9 | (3, 28) | 92.3 |
| 3 | 4.323 | 14.5 | 1110 | 91.0 | (3, 46) | 199.8 |

- The constant doubles between k = 1 and k = 3, and the box overestimate grows faster than the point value.
- At k_c = 3 the Laurent precondition already fails on the box of half-side 0.2525: for complex k near 3.25 ± 0.25i a
  root reaches |w| = 1.45. So the precondition limits the ellipse size well before real k reaches 4.

## 10. Revised cost estimate for the full run

**The node-count model, now with a measured constant.** For a segment of half-width h,
n ≈ [ln(4·g²/((ρ − 1)·tol)) + 2c·h·(ρ + 1/ρ)/2] / ln ρ, with c = c0 + c1 the two Dyson constants on the box and
g = g0·g1. At k ≈ 1: c ≈ 87, g ≈ 25, tol = 1e−3 gives n = 24 for h = 0.05, as measured.

- **Per unit of k near k ≈ 1:** about 250 point evaluations (this run: 25 for Δk = 0.1). Of these, about 130 are the
  Dyson term and about 100 the fixed overhead ln(4g²/tol)/ln ρ per segment.
- **Per unit of k elsewhere** (from the §9 table, 0.1-wide segments): about 250 at k = 1/2, 290 at k = 2, 470 at k = 3.
- **Per spin, region A (k up to ≈ 4), spin 3/5:** roughly 1,500–2,500 point evaluations, plus one 40 s proof stage per
  segment. The stretch from 3 to 4 is extrapolated, not measured. At 22 s per evaluation on a free core that is 9–15
  core-hours. Part B's estimate was 400–2,400 evaluations and 3–20 core-hours; this is in its upper half.
- **With the step-size fix** (B5; about 10× fewer Taylor steps), 1–2 core-hours per spin.

**What can move this estimate:**

- c between 3 and 4 and near turning-point approaches (not measured).
- Small-|F| stretches need a tighter absolute tolerance: each factor 10 costs ln 10/ln ρ ≈ 1.7 nodes per segment.
- Other spins: the evaluator's constants are still hard-coded for 3/5.
- A tighter F bound would cut the count directly. M_F carries e^{2(I0+I1)}. Interpolating the entries of M0 and M1
  instead (each bounded by g·e^{I}) and forming F from the interpolants would roughly halve the Dyson term; my
  estimate for this segment is n ≈ 18 instead of 24. Not built: the node file stores F and the traces only.

## 11. Limits

- One segment, one spin. Nothing here covers k outside [1, 1.1].
- The items listed as argued in §1.
- The 5 × 5 k-sub-boxes and the 24-ball rectangle rule are choices; coarser ones give a valid but larger M.
- The reference walk repeats the point evaluator's steps with extra output (`step_ref` copies `step`). The node
  values come from the unchanged Part B evaluator.
- No independent second implementation.

## 12. Reproduce

Interpreter: `/Users/sumit/Github/quantum/sims/.venv/bin/python -I` (Python 3.13.12, python-flint 0.9.0; Quantum's
pinned environment, used read-only). Sympy check: the repo's `.venv` (sympy 1.14.0). One process, one core; measured
footprint 16 MB (top MEM), peak RSS 33 MB.

```bash
.venv/bin/python scripts/_nve_route1_kc_identity.py
```
```bash
/Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_segment.py prove 1
```
```bash
/Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_segment.py nodes 1
```
```bash
/Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_segment.py verdict 1
```

**v2** (the same interpreter; `verdict 1 partB` needs only the proof stage, `verdict 1 arb` needs `nodes 1 arb`):

```bash
/Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_segment_v2.py prove 1
```
```bash
/Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_segment_v2.py verdict 1 partB
```
```bash
/Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_segment_v2.py nodes 1 arb
```
```bash
/Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_segment_v2.py verdict 1 arb
```

v2 outputs: `route1_seg_3_5_v2.out`, `route1_seg_M_v2_nseg1.json`, `route1_seg_nodes_arb.jsonl`,
`route1_seg_verdict_v2_partB_nseg1.json`, `route1_seg_verdict_v2_arb_nseg1.json`.

Outputs in `data/nve/eps/`: `route1_seg_identity.out`, `route1_seg_3_5.out` (the log of all three stages),
`route1_seg_M_nseg1.json` (the proved M and every ρ row), `route1_seg_nodes.jsonl` (one line per point evaluation;
a rerun resumes), `route1_seg_verdict_nseg1.json`, `route1_seg_3_5_dev.out` (the first, looser proof run),
`route1_seg_consts.out`.

## 13. Version 2: no bound relies on float rounding

`scripts/_nve_route1_segment_v2.py` (version 1's file is left as committed). Log: `data/nve/eps/route1_seg_3_5_v2.out`.

**What changed.**

- Every bound is an Arb ball or an exact upper end of one: the precondition comparison, the Dyson sums and exponents,
  exp, the gauge norms, M, the error formula, the node inflation, the sub-ball comparisons and the three lower bounds.
- Printed bounds are rounded outward in decimal and re-checked against the ball (`lo_dec`, `hi_sci`).
- The point evaluator is re-implemented in the same file with ball tails: the Laurent Cauchy bound, the Laurent tail
  and the Taylor tail. Part B's evaluator computes these three as floats with a 1 + 1e−7 inflation.
- The covers are exact: the 400 arcs of the Laurent circle, the 24 balls of s, the k-sub-boxes and the 256 balls of
  θ are built as centre + radius·[−1, 1] in ball arithmetic, with asserts that neighbours share their end points.

**Where floats remain, and why that is harmless.** Only as choices that any value of would be valid for: polygon
vertices and step points (binary numbers, converted exactly), the disc radius ρ_step of a Taylor step, the Bernstein
ρ and n, the gauge matrix C, and the sample points of the controls. Display-only numbers (ratios, times) are floats.

**A gap found in Part B's walk while doing this.** `_nve_route1_proto.walk` computes the end point of each polygon
edge in floats, `P0 + (P1 − P0)·((done + h)/seglen)`, and starts the next edge at the vertex `P1`. The two can differ
by rounding, and the edge loop stops once it is within 1e−15 of the edge length, so the transport can skip a gap of
up to about 1e−15 at a vertex. The effect is far below the enclosure radii (1e−9 on F), but it is not covered by
them. The v2 walk ends every edge exactly on its vertex and asserts the polygon is closed. I read this off the code;
I did not measure whether a gap actually occurred in any Part B evaluation.

**The paths of different k.** A walk follows the polyline through its own binary step points. These sit on the
polygon's edges up to rounding of the point (1e−16) and differ between k, because the step lengths adapt. All of them
lie inside the reference walk's step boxes, where q is certified holomorphic for every k in the disc, so they are
homotopic and give the same monodromy as the reference polyline that the Dyson bound uses.

**Result: does any lower bound change?**

| | v1 (floats at the end, Part B nodes) | v2 chain, Part B nodes | v2 chain, v2 all-ball nodes |
|---|---|---|---|
| proved M_F | 6.565e10 | ≤ 6.565E+10 | same proof stage |
| error bound on F | 3.110e−4 | ≤ 3.110E−4 | same |
| \|F\| ≥ | 0.265023 | 0.265023401 | 0.265023401 |
| \|tr M0\| ≥ | 1.993158 | 1.993158418 | 1.993158418 |
| \|Im tr M1\| ≥ | 2.648821 (printed) | 2.648820919 | 2.648820919 |
| verdict | CERTIFIED | CERTIFIED | CERTIFIED |
| controls | as §7 | identical outcomes | identical outcomes |

- No lower bound changed at the digits shown, with one printing exception: v1 printed 2.648821 for |Im tr M1| by
  rounding to nearest, which rounded 2.6488209 up. The certified value is 2.648820919. §0 quoted 2.64882, which was
  already safe.
- The proof stage reproduces version 1's constants to the digits printed (M_F, the exponents 1.519 and 7.712, the
  gauge factors).
- **The two node sets agree.** All 36 evaluations were rerun with the all-ball evaluator (915 s at nice 12). All 108
  enclosures (F, tr M0, tr M1 at 25 nodes, 3 held-out points and 8 ellipse points) overlap Part B's; 107 of the 108
  printed enclosures are identical strings, the midpoints agree to float resolution, and the step counts are the same
  in all 36 records. So neither the float tails nor the vertex gap moved any value at the precision carried.

## 14. How dq/dk is enclosed over the whole k-disc and every path box (not sampled)

Line numbers are in `scripts/_nve_route1_segment_v2.py`.

1. **The path boxes.** `walk(..., record=True)` (l. 261) returns, for every Taylor step, a box Z = z_c + h/2 +
   (|h|/2)·([−1, 1] + i[−1, 1]) (built in `step`, l. 203; `hb`). Z is convex and the assert at l. 287 checks that it
   contains both ends of the step, so it contains the whole step segment. Steps chain exactly: each starts at the
   binary point where the last one ended, each edge ends on its vertex (`while pos != P1`), and the polygon is closed
   (assert, l. 266). So the boxes cover the loop with no gap: 2,163 boxes on the circle, 703 on the lasso.
2. **The k-region.** `kbox` (l. 394) builds the closed square K of half-side R around k_c, which contains the disc
   |k − k_c| ≤ R, and cuts K − k_c into 5 × 5 closed sub-boxes. None is dropped. The asserts at l. 404–407 fail unless
   each cell contains both of its edges, the outer edges reach ±R, and there are exactly 25.
3. **One enclosure per (path box, k-sub-box).** `dq_sup` (l. 351) evaluates dq/dk with Z and the sub-box δk as balls,
   so the result contains dq/dk(z; k) for every z in Z and every k in k_c + δk. Nothing is evaluated at a point:
   - c0, c0′ and their k-derivatives at k_c on Z: `c0_at(Z, ·)` (l. 173), a polynomial in the ball 1/Z plus the
     Cauchy tail;
   - the second k-derivative on Z × K: `d2kc0` (l. 330). Each of the 24 balls of s carries an enclosure of the
     integrand; the integral over that ball lies in (enclosure) × (width);
   - Taylor in k with that second derivative as remainder, then the chain rule (2b).
4. **Refusals are not skips.** `dq_sup` returns None if G1 or G2 may vanish, if Re(1 − kφ) > 0 is not certified, or
   if the result is not finite. `dq_list` (l. 411) then returns None for the whole loop, and `prove` rejects that ρ
   and prints where it failed. A ρ row is used only if both loops returned a full list.
5. **The asserts that fail if anything was skipped or non-finite.**
   - l. 390: the number of sub-boxes evaluated on this path box equals the number given, and the supremum is finite;
   - l. 423: one value per step, the total count equals steps × 25, every value finite;
   - l. 574: the two counts equal 2,163 × 25 = 54,075 and 703 × 25 = 17,575;
   - l. 733: the verdict stage refuses a proof file whose counts differ from the expected ones;
   - l. 325–327 (`coverage_asserts`, run at the start of `prove` and `verdict`): the balls of s cover [0, 1] and the
     balls of θ cover [0, π].
   The log prints "all 54075 + 17575 (step box, k-sub-box) pairs enclosed" on every ρ row.
6. **From the enclosure to the bound.** The disc is convex, so for k in it
   |q(z; k) − q(z; k_c)| ≤ |k − k_c|·sup over the segment from k_c to k of |dq/dk| ≤ R·(largest of the 25 enclosures).
   `dyson_sum` (l. 452) then adds sup|dq/dk| × sup|(v1, v2)C|² × |h| over all steps, in balls.

**What this does not cover.** The Dyson step that turns this into a bound on M is the hand derivation of §2.

## 15. Gauge legitimacy

**The claim used.** For any constant invertible C, write Y_k = Φ_c C T C⁻¹. Then T(base) = I and
T′ = −Δq·(Φ_cC)⁻¹E21(Φ_cC)·T. C does not depend on z or k, so T is as holomorphic in k as Y_k is, and the bound
‖T‖₂ ≤ e^I needs only det C ≠ 0. A poor C gives a larger M, never a wrong one. That is why C may be chosen in floats
from the data: nothing about the choice needs proof. The certificate converts the float entries exactly, asserts
det C ≠ 0 (l. 456), and recomputes every quantity that involves C in balls (`dyson_sum`, `gauge_norms`).

**The matrices of the certified row** (ρ = 4; upper triangular, det = 1 to float accuracy, so C⁻¹ = [[d, −b], [0, a]]
for C = [[a, b], [0, d]]):

| loop | C | C⁻¹ | ‖C‖_F‖C⁻¹‖_F |
|---|---|---|---|
| circle | [[0.930032, 0.347288 − 0.091852i], [0, 1.075231]] | [[1.075231, −0.347288 + 0.091852i], [0, 0.930032]] | ≤ 2.151 |
| lasso | [[0.228215, −3.433938 + 0.250609i], [0, 4.381825]] | [[4.381825, 3.433938 − 0.250609i], [0, 0.228215]] | ≤ 31.11 |

**How the condition number enters.** M(k) = M_c C T C⁻¹, so
‖M(k)‖_F ≤ ‖M_cC‖_F·‖C⁻¹‖_F·e^I ≤ κ_F(C)·‖M_c‖_F·e^I, with κ_F(C) = ‖C‖_F‖C⁻¹‖_F.

- The code uses the sharper middle expression, not κ_F: ‖M_cC‖_F‖C⁻¹‖_F ≤ 2.151 on the circle and 11.70 on the lasso.
  With κ_F it would be 2.151 × 1.4264 = 3.07 and 31.11 × 7.1788 = 223.
- For the traces, tr M(k) = tr(C⁻¹M_cC·T), so |tr M(k)| ≤ √2·‖C⁻¹M_cC‖_F·e^I, with ‖C⁻¹M_cC‖_F ≤ 1.428 and 4.888.
- Each factor enters M_F squared: (2.151 × 11.70)² ≈ 633, against (1.4264 × 7.1788)² ≈ 105 with no gauge.

**What the gauge buys for that price.** The lasso's Dyson constant at k_c falls from ≤ 597.9 to ≤ 45.80 per unit k
(circle: 11.32 to 10.50). On the certified disc that is roughly e^{2·0.106·550} in M_F, against the factor 6 paid.

**Each loop and each ρ row has its own C.** That is allowed: the bounds for M0 and M1 are proved separately and only
multiplied at the end.

## 16. Generality check at spin 9/10 (the Bridge's last task; seal 620c470)

**Outcome: NO certificate tonight, by cost and not by refusal.** The procedure runs unchanged at spin 9/10 and the
proof stage delivers a proved M. That M asks for 141 Chebyshev points at about 3 minutes each (about 7.5 core-hours
for this one segment), against 25 points at 27 s for spin 3/5. Only the two end nodes were evaluated. So there are
no certified lower bounds on the segment at spin 9/10; the table below says what there is.

Setup: spin 9/10, E = 4/5, real k ∈ [1, 11/10], circle R0 = 1.2639, the engine's lasso of k_c = 21/20 fixed
(`route1_floats_9_10.json`, from `_nve_spin_scan.LauA` through `_nve_route1_floats.py`). Log:
`data/nve/eps/route1_seg_9_10_v2.out`. Proof file: `route1_seg_M_v2_9_10_nseg1.json`.

**What ran, and what it gave.**

| stage | result at spin 9/10 | spin 3/5, for comparison |
|---|---|---|
| derivative self-test | passes at all five points | passes |
| Laurent-disc precondition on the k-box | certified (largest root \|w\| ≤ 0.4649 < 1.2346; the roots do not depend on the spin) | certified |
| reference walk | 17,955 steps on the circle, 895 on the lasso, 194 s | 2,163 and 703, 28 s |
| every (path box, k-sub-box) pair enclosed | 448,875 + 22,375, none skipped | 54,075 + 17,575 |
| Dyson constant, lasso (optimised gauge, point) | ≤ 83.64 | 45.8 |
| Dyson constant, circle (optimised gauge, point) | ≤ 478.2 | 10.5 |
| the same on the k-disc of the chosen ρ | 140 (lasso), 687 (circle) at ρ = 3 | 72.6, 14.3 at ρ = 4 |
| proved M_F | ≤ 4.678E+62 (ρ = 3, R ≤ 0.0834) | 6.565E+10 |
| node count for the 1e−3 target | n = 140 at ρ = 3 (156 at ρ = 4, 190 at ρ = 5, 274 at ρ = 6.5) | 24 |
| point evaluations done | 2 of 141 (the end nodes) | all |
| verdict | none: the node run was not attempted beyond the end nodes | CERTIFIED |

**The controls that could be run without the nodes.**

- **Engine at two nodes** (k = 11/10 and k = 1, all-ball evaluator): all six engine values lie inside the
  enclosures. Each evaluation took about 185 s (17,893 to 18,008 + 895 steps); the radius of F is 7.4e−8.
- **Reference point** k_c = 21/20: the validated F is 0.0168748387 + 0.0593012374i; the engine's is
  0.0168748386811 + 0.0593012373839i.
- **Planted precondition** at k = 4.2, 4.01, 4.0: fires at 4.2 and 4.01, certifies at 4.0, as at spin 3/5.
- **Planted zero, held-out points, proved M ≥ sampled:** NOT RUN. They need the node values.

**Values at the nodes evaluated** (enclosures at single k, not bounds on the segment): at k = 1,
|F| ≥ 0.052661605, |tr M0| ≥ 1.980659534, |Im tr M1| ≥ 3.842809567; at k = 11/10, |F| ≥ 0.071729189,
|tr M0| ≥ 1.976145517, |Im tr M1| ≥ 3.847113436. The 1e−3 target is 2% of the smaller |F|.

**Against the seal (620c470).**

| prediction | sealed | measured | |
|---|---|---|---|
| lasso constant at k_c | 150 (80 to 400) | 83.64 | in range, at its low end |
| circle constant at k_c | 40 (20 to 120) | 478.2 | **WRONG**, 4 times above the range |
| best ρ | 3 (3 or 4) | 3 | held |
| node count n | 50 (30 to 90) | 140 | **WRONG**, above the range |
| precondition certifies | yes | yes | held |
| the proof stage gives a finite proved M | 80% | it did | |
| certified inside tonight's window | 30% | no | |
| certified if the nodes were allowed to finish | 65% | not tested | |

**What I got wrong, and what I do not know.** I expected both loops to get harder by a similar factor. The lasso did
(×1.8). The circle got harder by ×46 and now dominates: I0 = 57 against I1 = 12 at ρ = 3, and M_F carries
e^{2(I0+I1)}. The outer singular points are as far from the circle as at spin 3/5 (0.52 against 0.55), so the cause is
on the inner side, where the ring |z| = a is 0.36 from the circle against 0.75 at spin 3/5. I did not locate where
along the circle the Dyson sum concentrates; that is one 200 s run with a per-step printout.

**Two code changes the new spin needed.** Both leave spin 3/5 as committed: after the changes, `prove 1` and
`verdict 1 arb` at spin 3/5 reproduce the committed proof file and verdict file byte for byte.

- A step box that reaches the edge of the Laurent series' domain is now refused like any other bad box, and the
  step radius is halved (`safe_step`, at the end of the file so that §14's line numbers stay valid). At spin 3/5 this
  never triggers. At spin 9/10 it is why the circle needs 17,955 steps: the circle sits at 0.79 of the Laurent
  radius, against 0.49.
- The spin and the circle radius are read from `NVE_SPIN` and `R1_R0`; outputs carry a spin tag.

**Revised cost estimate, spin 9/10 region A** (k up to about 3.85, 0.1-wide segments, constants as at k ≈ 1, which is
an assumption):

- **As the code stands:** about 140 evaluations per 0.1 of k at about 3.2 minutes each, so about 7.5 core-hours per
  0.1 of k and roughly 250 to 300 core-hours for the region. That is not usable.
- **Where the cost sits:** the circle, twice over. Its Dyson constant sets the node count (about 85% of the
  exponent), and its 17,955 steps set the time per evaluation (95% of the steps).
- **Cheapest fixes, none built or tested:**
  1. Steps: represent c0 near the circle by something other than the Laurent series at infinity (or re-expand it),
     so that step boxes are not limited by the Laurent ratio. If the circle then needs about as many steps as at
     3/5, an evaluation costs about 30 s instead of 190 s.
  2. Nodes: interpolate the entries of M0 and M1 instead of F (§10). That roughly halves the Dyson term, so about 75
     nodes instead of 140.
  3. With both, roughly 20 to 30 core-hours for the region. This is an extrapolation from one k.
- **What would change the picture more:** a different circle for this spin, if the registered rule allows one further
  from the ring. I did not look at whether it does.

**Reproduce** (spin 3/5 commands unchanged):

```bash
NVE_SPIN=9/10 R1_R0=1.2639 R1_FLOATS=route1_floats_9_10.json .venv/bin/python scripts/_nve_route1_floats.py 1 21/20 11/10
```
```bash
NVE_SPIN=9/10 R1_R0=1.2639 /Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_segment_v2.py prove 1
```
```bash
NVE_SPIN=9/10 R1_R0=1.2639 /Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_seg_endnodes.py
```

To finish the certificate, run `nodes 1 arb` and then `verdict 1 arb` with the same two variables. The node file
`route1_seg_nodes_arb_9_10.jsonl` already holds the two end nodes and the run resumes from it. Expect about 7.5 hours.
