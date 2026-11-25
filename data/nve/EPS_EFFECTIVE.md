# An explicit ε for Statement A, and a first step toward the whole k-range

> **VERIFIED 2026-11-26 by the office ansatz-machine (a non-author): `EPS_OFFICE_CHECK.md` (e10f274, bcd9292).**
> - Part A is verified, with one slip in `assemble`: the |m|⁻⁴ weight used an upper bound of |m|².
>   - It was fixed in 9d0ee9f and all runs were redone.
>   - **The quoted ε_a are the corrected r rounded down:** 2.79e−3, 1.92e−3, 8.39e−4 and 1.06e−4. Those, not the
>     unrounded values in §4 below, are what CLAIM v3.1 states.
> - Part B is checked as a prototype only: ATAP Thm 8.2 was read at source, and the run reproduces exactly.
> - Merged into main in bd74e05. The "UNVERIFIED" labels below are historical.

**[model: Fable 5.2] Session ansatz-machine-personal, 2026-11-25/26. Ask: the Bridge, for Sumit (brief
`docs/BRIEF_FABLE_EPS_2026-11-25.md` v2.1). Branch `fable/2026-11-25-eps`. STATUS: UNVERIFIED until the office
ansatz-machine checks it.**

## 0. The simple version
- Statement A says: for every small enough twist k > 0 the monodromy group is as large as it can be. "Small enough"
  had no number. **Part A puts a number on it**, per spin, by interval arithmetic: r_a in the table of §4.
- The numbers are small. That is a property of the bound, not of the physics: the method controls the loop around
  the turning point only crudely. §5 says which factor costs what.
- **Part B** is a design and a first measurement for certifying the whole range of k, not a result.

---

# Part A

## 1. What r certifies, exactly
For one spin a and E = 4/5, the certifier returns r > 0 with this meaning. For every **complex** k with
0 < |k| ≤ r:
1. the coefficient q(z; k) of the ρ-equation is holomorphic in k on both loops (no zero of P or of f0² + c0² reaches
   them);
2. the monodromies M0(k), around the circle C: |z| = R0, and M1(k), around **the fixed k = 0 capsule lasso L**,
   satisfy
   - (Z1) F(k) = tr[M1, M0] − 2 ≠ 0;
   - (Z2) tr M0 ≠ 0 and tr M1 ≠ 0;
   - (Z3) tr M1 ∉ [−2, 2].

Then ⟨M0(k), M1(k)⟩ is irreducible, not imprimitive and infinite, hence Zariski-dense in SL(2, ℂ), and so is the
full monodromy group. Statement A holds with ε_a = r.

**The lasso is not the engine's lasso for k ≠ 0.** The engine re-centres its capsule on r₊(k), p₊(k). Here L is the
k = 0 polygon, kept fixed. Both are loops in the same domain, so both give elements of the monodromy group, and for
|k| ≤ r they are homotopic (item 1: nothing crosses L), so F is the same function.

**Certified vs argued.**
- Certified in interval arithmetic: every number in the inequality of §3, and item 1 on the boxes covering C and L.
- Argued, not machine-checked: the derivation of §2–§3 (hand algebra); that the polygon L is a simple closed curve
  around exactly r₊ and p₊ (its winding numbers are computed and its U-increment is compared with ω, §4);
  everything upstream (Lemma K's setting, Proposition 2, the Morales–Ramis chain).

## 2. The derivation
**(a) The identity, sharpened.** Write M0 = I + N. The brief's identity is F = −2 det N + (det N)² − tr(M1 N M1⁻¹ N).
Since det M0 = 1 gives tr N = −det N, Cayley–Hamilton gives tr N² = (tr N)² − 2 det N = (det N)² − 2 det N. So

    F = tr(N²) − tr(M1 N M1⁻¹ N)        (exact, for every k).

This is the c2 formula with X replaced by N, to all orders.

**(b) Kerr's basis.** With Φ = (v₊, v₋), v± = (ND)^{1/4}e^{±κU}, W = −2κ, write Y = ΦZ. Then Z′ = BZ with

    B = (Δq/W)·[[v₊v₋, v₋²], [−v₊², −v₊v₋]],    Δq = q(z; k) − q(z; 0),    ‖B‖_F = |Δq|·ψ,
    ψ(z) = |√(ND)|·cosh(2κ(Re U − u0))/κ.

(The Frobenius norm of the bracket is |√(ND)|·2cosh(2κ Re U). u0 is the free rescaling v± → e^{∓κu0}v±; any
value is allowed and the code tries a few.)
- On C, Φ is single-valued, so M0 = Pexp∮_C B and N = ∮_C B + R₂, ‖R₂‖_F ≤ e^{ℓ} − 1 − ℓ ≤ ℓ²e^{ℓ}/2, ℓ = ∮_C ‖B‖_F|dz|.
- On L, Φ returns multiplied by M1(0) = −diag(m, 1/m), m = e^{κω}. So M1(k) = M1(0)·Z₁ with Z₁ = Pexp∫_L B and
  ‖Z₁^{±1} − I‖_F ≤ η := e^{ℓ_L} − 1.

**(c) The twist to second order, without Cauchy estimates.** On |z| ≥ aν₀, c0″ = c_K″√(1 − kφ(w)). The integrals from
∞ may be taken along the radial ray from z (the integrand is holomorphic outside the cross and O(s⁻⁴) at ∞, so they
are path-independent there). The binomial series gives |√(1 − x) − 1 + x/2| ≤ |x|²/(8(1 − |x|)), hence

    c0 = c_K + k·c1 + ε₂,   |ε₂| ≤ A0(ν₀)·Φ̄(ν₀)·|k|²/(8(1 − |k|Φ̄)),      and the same for c0′ with A1,

where c1 is the closed form of `C2_ANALYTIC.md` §2 and, on |u| = ν,
- Φ̄(ν) = (21ν⁴ + 18ν² + 1)/(10(3ν² − 1)²) ≥ |φ|, decreasing;
- h(ν) = 4(3ν² + 1)/(a³(ν² − 1)³)·Φ̄(ν) ≥ |c_K″||φ|, decreasing;
- A1 = a∫_{ν₀}^∞ h, A0 = a²∫_{ν₀}^∞ (ν − ν₀)h, tabulated once as upper Riemann sums with an explicit tail.

**(d) q to second order.** At fixed z, q = (3/16)Λ², Λ = G1′/G1 − G2′/G2, G2 = f0² + c0², G1 = E²G2 − f0, is a
rational function of (c0, c0′). With q_c, q_c′ its partial derivatives at Kerr, δq = q_c·c1 + q_c′·c1′ (this is the
δq of the c2 note), and the mean-value form gives, at |k| = r,

    |Δq − kδq| ≤ β(z) := |q_c|e₀ + |q_c′|e₁ + sup|q_c(box) − q_c(Kerr)|·ρ₀ + sup|q_c′(box) − q_c′(Kerr)|·ρ₁,
    |Δq| ≤ α(z) := r|δq| + β(z),

with ρ₀ = r|c1| + e₀, ρ₁ = r|c1′| + e₁ and the box (c_K ± ρ₀, c_K′ ± ρ₁). Evaluating q's derivatives on that box in
interval arithmetic fails if G1 or G2 could vanish there, so a pass is also the holomorphy certificate of §1 item 1.
For |k| ≤ r the maximum principle (applied to Δq/k and to (Δq − kδq)/k²) gives |Δq| ≤ α|k|/r and
|Δq − kδq| ≤ β(|k|/r)².

**(e) The constants.** With sums over interval boxes covering the paths:

    ℓ_C = ∮_C αψ,   ε_C = ∮_C βψ,   ℓ_L = ∫_L αψ,
    N = kX + E,   ‖E‖_F ≤ C_E|k|²,   C_E = (ε_C + ℓ_C²e^{ℓ_C}/2)/r²,   c_L = ℓ_L/r,   η(k) ≤ e^{c_L|k|} − 1.

## 3. The inequality
- With M1(0) diagonal, F₀ := tr N² − tr(M1(0)NM1(0)⁻¹N) = −4 sinh²(κω)·n12·n21, and c2k² is its part with
  n → kx. So

      |F₀ − c2k²| ≤ 4|sinh²(κω)|·(|k|³·√(|x12|² + |x21|²)·C_E + C_E²|k|⁴).

- Replacing M1(0) by M1(k) = M1(0)Z₁ replaces N by Z₁NZ₁⁻¹ inside the conjugation, and
  ‖Z₁NZ₁⁻¹ − N‖_F ≤ η(2 + η)‖N‖_F. Conjugation by diag(m, 1/m) costs at most μ² = e^{2|Re κω|}. So

      |F − F₀| ≤ μ²·η(2 + η)·‖N‖_F²,     ‖N‖_F ≤ |k|‖X‖_F + C_E|k|².

- **(Z1)** holds at |k| = t if |c2|t² exceeds the sum of the two right-hand sides. Their ratio to t² increases with
  t, so checking t = r covers all smaller t.
- **(Z2)** tr M0 = 2 + tr N and |tr N| ≤ √2‖N‖_F < 2.
- **(Z3)** |tr M1(k) − tr M1(0)| ≤ ‖M1(0)‖_F·η < |Im tr M1(0)|. This also gives tr M1 ≠ 0.

x11, x12, x21, κω and c2 are certified as in `C2_ANALYTIC.md` §6b (trapezoid with a proved error bound).

## 4. Results (`scripts/_nve_eps_certify.py`; outputs `data/nve/eps/eps_*.out` and `.json`)
`mpmath.iv` at 40 digits; 720 boxes on the circle, lasso pieces of length 0.003; one core, about 90 s per spin under
load, peak 32 MB.

**Registered loops** (circle R0 as in the spin scan; lasso = `capsule_lasso(r₊, p₊, [r₋, p₋], b = R0)` at k = 0):

| spin | R0 | **r_a (certified)** | c_L | C_E | ℓ_C/r | share of \|c2\|r²: circle / lasso | r if lasso 10× better | r if circle 10× better | r if both |
|---|---|---|---|---|---|---|---|---|---|
| 3/10 | 1.1492 | **2.80e−3** | 40 | 8.1 | 3.58 | 0.49 / 0.51 | 5.1e−3 | 7.0e−3 | 2.6e−2 |
| 3/5 | 1.35 | **1.93e−3** | 81 | 11.2 | 4.16 | 0.42 / 0.58 | 4.3e−3 | 4.5e−3 | 1.8e−2 |
| 4/5 | 1.3382 | **8.40e−4** | 176 | 15.2 | 4.76 | 0.45 / 0.55 | 1.8e−3 | 2.0e−3 | 8.2e−3 |
| 9/10 | 1.2639 | **1.06e−4** | 383 | 24.5 | 5.83 | 0.67 / 0.33 | 1.6e−4 | 3.0e−4 | 1.0e−3 |

The last three columns are hypothetical (the same inequality with a constant divided by 10), not certified.

**So Statement A holds with ε_a = 2.80e−3, 1.93e−3, 8.40e−4 and 1.06e−4 at spins 3/10, 3/5, 4/5 and 9/10**: for
every k with 0 < |k| ≤ ε_a, real or complex.

**A wider representative of the same lasso class** (capsule radius 0.4 × clearance instead of at most 0.15;
`EPS_DELTA=wide`, outputs `eps_*_wide.*`). It is homotopic to the registered lasso wherever both are certified, so
it bounds the same M1(k):

| spin | 3/10 | 3/5 | 4/5 | 9/10 |
|---|---|---|---|---|
| capsule radius | 0.120 (unchanged) | 0.241 | 0.320 | 0.360 |
| r_a (certified) | 2.80e−3 | 2.80e−3 | 1.44e−3 | 1.47e−4 |

Moving the circle (R0 = 1.2 or 1.5 at spin 3/5) changes r by less than 20%.

**At k = 0** every run re-certifies X, κω and c2, and checks the lasso:
- c2 intervals (3/5: [0.19354634, 0.19354640] + i[0.09848800, 0.09848805]) contain the engine's values of
  `c2_engine_check.out` at all four spins and at the control spin;
- winding numbers of the polygon about r₊, r₋, p₊, p₋: 1, 0, 1, 0 at every spin (from the tracked branch angles);
- κ × (U-increment around the lasso), by interval Euler, contains κω at every spin (width about ±0.07).

## 5. Controls
| control | what | result |
|---|---|---|
| **planted, spin 227/250** (R0 = 1.30, the brief's geometry) | c2 ≈ −7.4e−6; the third zero of F sits at \|k\| ≈ 1.6e−4, so an honest r must be far below that | r = **5.4e−8**. The certified c2 interval, [−7.49e−6, −7.37e−6] + i[8.2e−7, 9.4e−7], contains the engine's −7.4334e−6 + 8.779e−7i |
| **must-refuse, spin 3/5** (`EPS_REFUSE=1`: \|c2\| lower bound set to 0) | the refusal path | **"NO r"**, with the reason printed: "c2 interval contains 0 (\|c2\| lower bound is 0), so (Z1) cannot be certified at any r" |
| **spin 9/10** | the third zero at \|k\| ≈ 0.36 | r = 1.06e−4, far below it |
| **engine consistency** | the 50-digit engine's F at k = r and k = ir against the certified bound on \|F − c2k²\| | consistent at all four spins and at the control spin (`scripts/_nve_eps_engine_check.py` → `eps/engine_check.out`). The certified bound is 2,500 to 5,400 times the true remainder, which is \|c3\|r³ to three digits |
| **float gate** (in every run) | the closed form Δq = (3/8)Lλ + (3/16)λ² against the definition of q | relative error 5e−15 |

## 6. What limits r, and what would move it
- **Two terms share the budget about equally:** the lasso remainder (c_L) and the circle's second-order remainder
  (C_E). Neither is negligible, so improving one alone gains only a factor of about 2. Improving both by 10× would
  give r of order 1e−2 (1e−3 at spin 9/10).
- **c_L is large because the lasso passes within 0.12–0.15 of r₊ and p₊**, where δq grows like the inverse cube of
  the distance. A wider loop helps a little (table above). The real fix is to certify the lasso's first-order
  matrix as well, which moves its remainder from k³ to k⁴.
- **C_E is dominated by the crude Dyson tail** ℓ_C²e^{ℓ_C}/2 (about 8 of the 11 at spin 3/5), which bounds a double
  integral by the square of an integral of absolute values. The real fix is the certified second-order term, i.e. a
  certified c3. With both fixes the natural limit is |c2/c3| (about 5 at spin 3/5, 0.36 at 9/10) or the holomorphy
  radius, whichever is smaller. Neither is built.
- **|c2| is the reason spin 9/10 is 20× worse** than 3/5: it sits next to a\* ≈ 0.908, where c2 vanishes.
- **The conjugation by M1(0) costs little now.** The bound weights each matrix entry separately: the entry
  amplified by |m|² pairs with n21, which is the small one in the best scaling u0.
- **Holomorphy is not the binding constraint.** The boxes pass up to r_ref = 0.3 at every spin (σ < ½ and
  |γs| < ½ on both loops), far above r_a.

**A lesson from building it (measured).** The first version evaluated the general formula for q and its derivatives
on interval boxes and subtracted the Kerr value. That lost a factor of several hundred to cancellation and gave
r ≈ 1e−9. The fix was the exact structure P = P_K(1 + γs), which turns Δq into a closed form with no subtraction.

---

# Part B: a first validated build step for the whole k-range (route (i))

**Status: a working prototype of the validated evaluator at a POINT k, a measurement that k-BALLS do not work, a
one-segment demonstration of the alternative, and a plan. No certificate of anything over a k-interval yet.**

## B1. The simple version
- The evaluator (`scripts/_nve_route1_proto.py`, Arb ball arithmetic) encloses both loop monodromies at one value
  of k, rigorously. At k = 1, 1.05 and 1.1 its enclosures contain the 50-digit engine's values.
- Feeding it a **ball** of k, as the brief proposed, fails: the enclosure blows up by a factor of 10³ to 10⁷.
- What works instead: evaluate at points of k and interpolate in k, with a rigorous bound for the interpolation
  error. That needs one more piece, a crude bound on |F| over a complex neighbourhood of the k-segment. Part A's
  machinery can supply it; it is not built.
- **And the argument principle is not needed.** The claim is about real k, so it is enough to enclose F, tr M0 and
  tr M1 along the real k-interval and see that the enclosures avoid 0. That is a shorter path than a complex
  rectangle.

## B2. The evaluator (built)
Interpreter: `/Users/sumit/Github/quantum/sims/.venv/bin/python -I` (Quantum's pinned environment, used read-only;
Python 3.13.12, python-flint 0.9.0 on FLINT/Arb, mpmath 1.3.0). 256-bit balls. Spin 3/5, E = 4/5, circle R0 = 1.35,
the engine's own lasso polygon.
- **c0 and c0′ at a point:** the Laurent series at infinity of c0″ = c_K″√(1 − kφ), to order 190, by ball
  power-series arithmetic; the tail from a bound of |c0″| on |w| = 0.9/a (400 arcs) and Cauchy's estimate.
- **One step:** the Taylor series of q at the step centre to order 70 (series arithmetic on f0 and c0); the two
  solutions by the three-term-style recurrence; the tail beyond order 70 from the majorant |v_j| ≤ Kμʲ, μ = 2/ρ,
  which holds once Qρ² ≤ 2·70·71, where Q ≥ sup|q| on the disc of radius ρ. Step length ρ/4.
- **Holomorphy on the path** is certified as a by-product: a disc on which G1 or G2 could vanish is refused and ρ is
  halved.
- **Output:** M0, M1 as ball matrices; tr M0, tr M1, F.

**Measured (thin k; `data/nve/eps/route1_proto.out`, `.jsonl`).**
| k | steps (circle, lasso) | time | radius of F | of tr M0 | of tr M1 | engine float inside |
|---|---|---|---|---|---|---|
| 1 | 2164, 704 | 30 s | 1.4e−9 | 1.4e−12 | 1.7e−12 | yes (F, tr M0, tr M1) |
| 21/20 | 2163, 703 | 30 s | 1.4e−9 | 1.4e−12 | 1.7e−12 | yes |
| 11/10 | 2163, 701 | 30 s | 1.4e−9 | 1.4e−12 | 1.7e−12 | yes |

Times are on a machine whose ten cores were all busy with other jobs; peak memory 28 MB.

**Known inefficiency.** The bound Q is taken on the whole disc as one box, which overestimates it by about 10⁶
(Q ≈ 2e7). That forces ρ down, so the walk takes about ten times more steps than the geometry needs. Bounding q on
small balls around the disc's boundary circle, with a winding-number check that G1 and G2 have no zero inside, would
fix it. The radius of F is 10³ times that of the traces because the commutator is formed from ball matrices.

## B3. k as a ball: measured, and it fails
The same evaluator with k = 1.05 ± r (a complex box):

| radius of the k-ball | radius of tr M0 | radius of tr M1 | radius of F |
|---|---|---|---|
| 0 | 1.4e−12 | 1.7e−12 | 1.4e−9 |
| 1e−8 | 1.9e−5 | 2.9e−4 | 0.19 |
| 1e−6 | 1.2e−3 | 1.8e−2 | 19 |
| 1e−4 | 0.12 | 1.8 | not finite |
| 1e−3 (an earlier run) | 1.3 | 19 | not finite |

- The true changes over a radius of 1e−6 are about 1e−7 (traces) and 5e−7 (F). The enclosures are 10⁴ to 10⁷ times
  wider: the radius of F is 2e7 times the radius of the k-ball.
- Cause: the wrapping effect. Thousands of ball matrices are multiplied, and each product adds the radii as if every
  error pointed the worst way. Fewer steps would help by a constant, not in kind.
- **So "subdivide k until the enclosures exclude 0" would need balls of radius about 1e−9 on F**, i.e. about 10⁹
  evaluations per unit of k. Not viable.

## B4. What to do instead: points in k, plus rigorous interpolation
F, tr M0 and tr M1 are holomorphic in k on a complex neighbourhood of a real segment, as long as the two fixed loops
stay clear of the moving singular points. For a function bounded by M on the Bernstein ellipse of parameter ρ around
a segment, the Chebyshev interpolant through n + 1 extreme points has error at most 4Mρ⁻ⁿ/(ρ − 1) (Trefethen,
*Approximation Theory and Approximation Practice*, Theorem 8.2; **quoted from memory, to be checked at source**).
The convergence is geometric, so a crude M is enough, exactly as with the trapezoid rule in Part A.

Per segment the certificate would be:
1. **Fixed loops and holomorphy** for every k in the ellipse: σ < ½ and |γs| < ½ on boxes covering both loops, as in
   Part A's `box_bounds`, but around the reference k_c at the segment's centre instead of around Kerr. The reference
   data (G1, G2, c0 at k_c along the loops) come from the evaluator.
2. **M:** from the Dyson bound relative to the validated solution at k_c,
   ‖M_loop(k)‖ ≤ ‖M_loop(k_c)‖·exp(∫ |Δq|·‖Φ‖‖Φ⁻¹‖ |dz|), with |Δq| from step 1's closed form.
3. **Point evaluations** at the n + 1 Chebyshev points (thin k), with the loops of k_c.
4. **Enclosure** of the interpolant over the segment (Clenshaw on sub-balls) ± the error bound; check that it avoids
   0 for F and tr M0, and that tr M1 avoids [−2, 2].

Steps 3 and 4 are built (`segment` mode). Steps 1 and 2 are not: in the demonstration below M is only **sampled**
at 8 points of the ellipse.

**One-segment demonstration, k ∈ [1, 1.1]** (`data/nve/eps/route1_segment.out`, `.jsonl`): 
- 8 Chebyshev points (n = 7) with the loops of k = 1.05, and 8 samples on the Bernstein ellipse ρ = 8 (it reaches
  0.20 from the centre in every direction). 16 point evaluations, 446 s in all (28 s each, busy machine).

| function | sampled max on the ellipse | error bound 4Mρ⁻ⁿ/(ρ − 1) | smallest \|interpolant\| on the segment | test at k = 1.05 (not a node): \|interpolant − engine\| |
|---|---|---|---|---|
| F | 0.433 | 1.2e−7 | ≥ 0.26527 | 3.4e−8 |
| tr M0 | 1.996 | 5.4e−7 | ≥ 1.99316 | 2.3e−11 |
| tr M1 | 2.905 | 7.9e−7 | ≥ 2.86330 | 2.8e−11 |

- **Read it as a measurement.** If M were a proved bound of that size, 8 point evaluations would enclose all three
  functions on [1, 1.1] to about 1e−6 and show they do not vanish there. The test at the centre is consistent with
  the bound.
- The engine's values at k = 1 and 1.1 give |F| = 0.26533 and 0.32830, consistent with the enclosure's lower end.
- **A bug caught here.** The first version evaluated the Chebyshev polynomials through acos of a ball. For the two
  end sub-balls, which touch ±1, that is not finite, and they were silently dropped: the reported minimum (0.26619)
  was larger than the true |F(1)| = 0.26533. The recurrence T_{m+1} = 2tT_m − T_{m−1} replaced it, with an assert
  that every sub-ball is finite. (The same family as the acos-free rule in the certifiers: a non-finite enclosure
  must stop the run, never be skipped.)


## B5. Plan for the full run (not launched; the office session registers and launches after review)
**What to certify.** For each spin, on the real interval [r_a, k_top] (r_a from Part A; k_top ≈ 4.05, the end of the
circle picture): F ≠ 0, tr M0 ≠ 0, tr M1 ∉ [−2, 2]. Region B (near 30/7) needs the half-plane loops and is a separate
build; the top sliver is already interval-certified.

**Size.**
- Nodes per unit of k-length ≈ (2c·D + ln(1/tol))/(ln ρ)/(segment length), where c is the Dyson constant per unit
  |Δk| (Part A measured c_L = 40 to 380 and c_C ≈ 4 to 6 at k = 0) and D the size of the ellipse. For large segments
  this tends to about 1.6·c: **roughly 100 to 600 point evaluations per unit of k**, depending on the spin.
- Region A is about 4 units long: **400 to 2,400 point evaluations per spin.** At 30 s each on a busy machine that
  is 3 to 20 core-hours per spin; with the step fix of B2 (about 10× fewer steps) and an idle core, well under
  2 hours.
- These numbers rest on c at k ≠ 0, which has not been measured. **Measure c first** (step 1–2 of B4 at one
  segment), then fix the segment length.

**Checkpoint.** One jsonl line per point evaluation, keyed by (spin, segment, node), as `route1_segment.jsonl`
already does; a rerun skips finished keys. A segment's verdict is recomputed from its lines.

**Where F is small or the picture changes.**
- **Near k = 0:** Part A covers (0, r_a]. Just above it F ≈ c2k² ≈ 1e−7 to 1e−10, so the first segments must be
  short and geometric in k (interpolate F/k², which is holomorphic and of size |c2|).
- **Spin 9/10:** the third zero at k ≈ 0.11 + 0.34i limits the ellipse there: it must not contain it if one
  interpolates 1/F, and in any case M and F vary fast. Short segments near k ≈ 0.1.
- **Spin 4/5, k\* ≈ 4.0082:** in region B, where tr Γ = 0 for the half-plane pair; the circle pair (M1, M0) is the
  one to certify there, so region A's method should be pushed as far up as its loops allow.
- **k = 4:** the B roots meet ±i. On the loops nothing happens (MRS §5e), but |kφ| < 1 on the Laurent circle
  |w| = 0.9/a fails before that (φ → 7/30 at ∞, larger near |u| = 1.1). The Laurent radius or the representation
  of c0″ must change for k ≳ 3; `laurent()` refuses loudly if the tail bound is not finite.

**Every remaining limit (the fleet rule: listed beside the time estimate).**
1. M (B4 steps 1–2) is not built; without it nothing over an interval is certified.
2. c at k ≠ 0 is unmeasured, so the node count is a range, not a number.
3. The evaluator handles spin 3/5 only as written (constants at the top), real or complex k, |k| ≲ 3.
4. The loops' homotopy class is taken from the engine's vertices at the segment centre; that they stay clear of the
   singular points for all k in the ellipse is what step 1 would certify.
5. The interpolation theorem is quoted from memory.
6. Region B is not designed.
7. The evaluator has had no independent check beyond agreement with the engine at three k.
