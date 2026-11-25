# Route (i): the first certified segment (spin 3/5, E = 4/5, real k ∈ [1, 1.1])

**[model: Fable 5.2] UNVERIFIED until the office ansatz-machine checks it.** 2026-11-26. Answers
`docs/BRIEF_FABLE_ROUTE1_SEGMENT_2026-11-26.md` (brief v1). Branch `fable/2026-11-26-route1-seg`.
A single-segment build-and-measure step, not the route-(i) registration.

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

Outputs in `data/nve/eps/`: `route1_seg_identity.out`, `route1_seg_3_5.out` (the log of all three stages),
`route1_seg_M_nseg1.json` (the proved M and every ρ row), `route1_seg_nodes.jsonl` (one line per point evaluation;
a rerun resumes), `route1_seg_verdict_nseg1.json`, `route1_seg_3_5_dev.out` (the first, looser proof run),
`route1_seg_consts.out`.
