# Office check of Fable's c2 work (branch `fable/2026-11-25-c2-analytic`, commits 5b6110b and 8d8d04c), 2026-11-25

**Checker:** ansatz-machine (office), a non-author.
**Ask:** the Bridge, items (a)–(i).
**Verdict:** **VERIFIED.**
- The formula, its numbers, the a\* finding and the interval certificate all hold.
- The one source quote, a theorem number, is right.
- Statement A is safe wording once the analyticity lemma is written down. It is **rigorous relative to the
  applicability chain, not absolutely**; see (e).

The claim and ONLY_KERR are unchanged. That is Sumit's decision.

## (a) The algebra of C2_ANALYTIC §1–§3: CHECKED BY HAND
- **The k-expansion.** With M0 = I + kX + k²Y + O(k³):
  tr[M1, M0] − 2 = k²[tr X² − tr(M1 X M1⁻¹ X)] + O(k³).
  - Conjugation by M1(k) is exact, so the k-dependence of M1 enters only at O(k³).
  - X belongs to the circle M0 alone.
  - lim (tr M0 − 2)/k² = −det X = x11² + x12x21, using tr X = 0.
- **The first-order term.** With A = [[0, 1], [−q, 0]] and Φ = [[v₊, v₋], [v₊′, v₋′]], W = −2κ:
  Φ⁻¹(∂_k A)Φ = (δq/W)[[v₊v₋, v₋²], [−v₊², −v₊v₋]].
- **The diagonal lasso.** With M1(0) = c·diag(m, 1/m), c a 4th root of unity:
  c2 = (2 − m² − m⁻²)·x12·x21 = sinh²(κω)·I₊I₋/κ².
  - The phase c cancels, so the formula does not depend on it.
- **δq.** δq = (3/8)(P′/P)(g c1)′, with g = −4aΔ/(DN). This uses ∂_k f0⁻ = 4aΔ c1/D² (S4b below).

## (b) Exact sympy checks: 11/11 PASS, must-fail fires
(`scripts/_nve_c2_sympy_check.py` → `c2_sympy_check.out`; 69 MB)
- c1″ equals ∂_k c0″ at k = 0, both from the repo's own `radicand()` (spin 3/5) and with a symbolic spin.
- The partial fractions.
- The closed forms: R1′ = −Rr and Iu′ = −R1; both → 0 at +∞; c1 ~ 7a/(30z²).
- f0⁻ = Δ/D, and ∂f0⁻/∂c0 = 4aΔ/D².
- Kerr's v± solve the ODE, with Wronskian −2κ.

## (c), (d) The 50-digit engine against the formula: agreement to 12 digits at 7 spin values
(`scripts/_nve_c2_engine_check.py` → `c2_engine_check.out`)
- **Method.** This is the registered spin-scan region-A pipeline (circle R0, capsule lasso), which shares no code with
  Fable's scripts. c2 and c3 come from Cauchy means of F/k² and F/k³ over 8 points on |k| = 0.01, with alias O(k⁸).
- **Controls.** The k¹ coefficient is ≤ 3e−22 everywhere. Step control agrees to ≤ 1.5e−19. Peak 126 MB.

| spin | engine c2 | formula c2 (Fable) | engine −c2/c3 |
|---|---|---|---|
| 3/10 | 0.027942230930004 + 0.046011985576238i | 0.027942230930 + 0.046011985576i | −6.62 + 2.59i |
| 3/5 | 0.193546372212345 + 0.098488026524070i | 0.193546372212 + 0.098488026524i | −5.14 + 1.33i |
| 4/5 | 0.162134805551131 + 0.014905796103372i | 0.162134805551 + 0.014905796103i | −4.02 + 2.12i |
| 9/10 (R0 1.2639 and 1.30, identical) | 0.015814535719371 − 0.001617584836059i | 0.015814535719 − 0.001617584836i | 0.0951 + 0.3697i |
| 0.905 | 0.005993319798220 − 0.000672221095297i | 0.005993319798 − 0.000672221095i | 0.0412 + 0.1297i |
| 0.908 | −7.43336576e−6 + 8.77898030e−7i | −0.000007433366 + 0.000000877898i | −5.4e−5 − 1.5e−4i |
| 0.911 | −0.006088373557135 + 0.000755289219827i | −0.006088373557 + 0.000755289220i | −0.0461 − 0.1196i |

- **tr M1(0) and the k² coefficient of tr M0 − 2** also match −2cosh(κω) and x11² + x12x21 at every spin.
- **The a\* finding is confirmed.** c2 changes sign between 0.905 and 0.911 and is ≈ −7e−6 at 0.908. The third zero
  −c2/c3 passes through k = 0 there.
- **The spin-9/10 extra zero is explained.** At spin 9/10, −c2/c3 = 0.095 + 0.370i, against the post-hoc located extra
  zero 0.110 + 0.341i (`spin_locateA_9_10.out`). It is a first-order estimate at |k| ≈ 0.36, so close is as good as
  can be expected.

## (f), (g) The interval certificate (`_nve_c2_certify.py`): read line by line against §6b; rerun
- **Rerun:** CERTIFIED at all four spins (≈ 6 s each), with intervals identical to the stored outputs. The planted
  control (c1 := 1, true I± = 0) returns **NOT CERTIFIED**, with the intervals containing 0.
- **Code against §6b. Faithful:**
  - the trapezoid sum on θ ∈ {2πj/N}, with h = i z f(z);
  - M as an upper bound of |h| on 360 boxes per boundary circle, covering [0, 2π] with outward endpoints;
  - error = 4πM/(e^{σN} − 1) with σ = ½ ln(R_out/R_in) and R0 the geometric mean, so the θ-strip of half-width σ
    is exactly the annulus.
- **The series for U.** Exact rational coefficients, then enclosure. Its tail bound (R_out/C0)·Ŝ·θ^{N+1}/(1 − θ) follows
  from the majorant Π(1 − x/|r|)^{−1/2} and Cauchy at ρ1 = 1.7 < min|root|. It is applied only at box midpoints
  (|z_m| ≤ R_out), with the rest of the box covered by sup|U′|·half-diagonal.
- **Every sqrt, log and division** is guarded (a box with Re > 0, or a denominator excluding 0).
- **κω = ∓2a e^{−iπ/4} J** is re-derived here from z = c − (d/2)cos φ:
  - (z − r₊)(z − p₊) = −(d²/4) sin²φ;
  - √(n2) = (3/5)i;
  - √(z − p₋) = e^{iπ/4}√(−i(z − p₋)).
  - The overall sign is irrelevant to Re κω ≠ 0.
- **Logical sufficiency.** I₊ ≠ 0, I₋ ≠ 0, Re κω ≠ 0 and κ ≠ 0 imply sinh(κω) ≠ 0, hence c2 ≠ 0. This leans on the
  formula (a), which is proved algebra, not an interval statement.

## (h) The error bound at source: VERIFIED
Trefethen & Weideman, SIAM Rev. 56 (2014) 385–458. Author PDF: people.maths.ox.ac.uk/trefethen/sirev56-3_385.pdf,
read here.
- **Theorem 3.2 (p. 396).** "Suppose v is 2π-periodic and analytic and satisfies |v(θ)| ≤ M in the strip −a < Im θ < a
  for some a > 0. Then for any N ≥ 1, |I_N − I| ≤ 4πM/(e^{aN} − 1), and the constant 4π is as small as possible."
  - I = ∫₀^{2π} v (eq. 3.1); I_N = (2π/N)Σ_{k=1}^N v(θ_k) with θ_k = 2πk/N (eq. 3.2).
- **Theorem 2.2 (p. 392)** is the annulus form, r⁻¹ < |z| < r, with the same 4πM/(r^N − 1). That is literally our I±
  setting after scaling by R0.
- The number quoted from memory (Theorem 3.2) is right.
- **M is a bound on the closed annulus.** Analyticity holds on the closed annulus (point (i)), so maximum modulus gives
  the bound inside from the boundary. That covers the theorem's open-strip hypothesis.

## (i) Analyticity of the integrands: CHECKED BY HAND
- **The three log arguments, for |u| > 1** (the annulus has |u| ≥ 1.05/a ≥ 1.167):
  - Re[(√3u − 1)/(√3u + 1)] = (3|u|² − 1)/|√3u + 1|² > 0;
  - Re[(u + i)/(u − i)] = (|u|² − 1)/|u − i|² > 0;
  - Re[(u² + 1)/(u² − 1/3)] ≥ (|u|² − 1)(|u|² + 1/3)/|u² − 1/3|² > 0 (using Re u² ≥ −|u|²).
- **Why principal logs are the right branch.** The principal-log closed form is analytic on the connected region
  |u| > 1. There it has the right second derivative (S3) and tends to 0 at +∞. The true c1 is single-valued there,
  because the residues of c1″ sum to 0 and c1′ = O(z⁻³). So they are equal.
- **No other singularities in the annulus:** N, D, u² + 1, 3u² − 1, √3u ± 1 and u ± i are all nonzero (roots
  ≥ 1.850 > 1.55; a < 1.05).
- **The strip for ω:**
  - Im z + a = 3a/2 − (a/2)cos x·cosh y + ((2 − r₊)/2)·sin x·sinh y ≥ a(3/2 − cosh(½)/2) − 0.075·sinh(½) > 0 for
    a ≥ 0.3, using |2 − r₊| ≤ 0.15;
  - Re(z − r₋) > 0 trivially (r₋ ≈ −3.4).

## (e) Statement A: safe wording, and what it still needs
**Logic: sound.**
- F ≈ c2k² ≠ 0 gives irreducibility.
- tr M1 ≈ −2c·cosh(κω) ≠ 0 and tr M0 ≈ 2 rule out imprimitivity.
- |e^{κω}| ≠ 1 gives infinite order.
- An irreducible, primitive, infinite subgroup of SL₂ has Zariski closure SL₂ (the classification of algebraic
  subgroups of SL₂).

**Proposed wording (for Sumit, if adopted):**
> For each tested spin a ∈ {3/10, 3/5, 4/5, 9/10} at E = 4/5 there is ε_a > 0 such that, for every k ∈ (0, ε_a), the
> monodromy group of the lower-axis ρ-equation is Zariski-dense in SL(2, C). The k²-coefficient of tr[M1, M0] − 2 is
> given in closed form by Kerr's explicit solutions, and its nonvanishing is certified in interval arithmetic. ε_a is
> not quantified. The statement is rigorous relative to the applicability chain (MRS_SECTION.md).

**Still needed before any claim change:**
1. **Write the analyticity lemma into MRS §5d.** M0(k) and M1(k) are analytic at k = 0 because, on the circle, the
   lasso and the real ray [R0, ∞):
   - c0″ = c_K″·√(1 − kφ(w)), with φ = (21w² − 18w + 1)/(10(3w − 1)²) bounded (|3w − 1| ≥ 3R0²/a² − 1 > 0);
   - r± and p± are simple and move analytically.
   C2 §1 argues this correctly. It should be a stated lemma, not prose.
2. **Say what it adds.** Rigour only on an unquantified neighbourhood (0, ε_a), which the numerical counts already
   covered. It is an anchor, not a new range. At spin 9/10 the neighbourhood is small: the third zero sits at
   |k| ≈ 0.36.
3. **Keep the chain caveats verbatim:**
   - Prop. 2: own proof, not independently checked;
   - e₋ = 1/e₊: assumed, or taken as the definition;
   - Lemma C(a): the MR01 theorem number is secondhand;
   - MRS 2007: read.
4. **Do not generalise across spins.** c2 = 0 at a\* ≈ 0.908, so "c2 ≠ 0" is a per-spin certified fact, not a
   spin-uniform one.

**Environment:** Python 3.14.5 (.venv), mpmath 1.3.0, sympy 1.14.0, numpy 2.4.6, scipy 1.18.0, macOS arm64. One core,
nice 12. Engine runs 18:01–18:39, about 38 min in total.
