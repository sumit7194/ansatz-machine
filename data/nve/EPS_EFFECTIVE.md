# An explicit ε for Statement A, and a first step toward the whole k-range

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
