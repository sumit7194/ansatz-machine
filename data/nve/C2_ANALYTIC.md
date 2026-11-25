# The k² coefficient of the irreducibility function, from Kerr's explicit solutions (route (ii))

**[model: Fable 5.2] Session ansatz-machine-personal, 2026-11-25. Ask: the Bridge, for Sumit. Branch
`fable/2026-11-25-c2-analytic`. STATUS: UNVERIFIED until the office ansatz-machine checks it.**
Hand derivation plus one small double-precision script (`scripts/_nve_c2_analytic.py`, about 0.2 s per spin).
Nothing here is interval-certified yet; §6 says exactly what a certificate needs.

## 0. The simple version
- Near Kerr (k = 0) the test function F(k) = tr[M1, M0] − 2 starts at order k²: F = c2·k² + O(k³). If c2 ≠ 0, then F ≠ 0
  for every small enough k > 0, with no numerical counting at all.
- **c2 has an exact formula in terms of Kerr's own solutions:**

      c2 = sinh²(κω) · I₊ · I₋ / κ²,      κ = a·√(1 − E²).

  ω is a period of an elliptic integral. I₊ and I₋ are two explicit contour integrals.
- **Numerically c2 ≠ 0 at all four spins** (E = 4/5). At spin 3/5 the formula agrees with the stored 50-digit
  monodromy data to 12 digits.
- **Not a closed form in elementary functions**, and none should be expected: I± contain the exponential of an
  incomplete elliptic integral. But they are explicit and cheap to certify (§6): about a hundred interval
  evaluations of an explicit function, instead of validated ODE integration.
- **New finding:** c2 is not nonzero at every spin. I₊ changes sign at a\* ≈ 0.9080 (E = 4/5). Spin 9/10 sits
  close to it, which is why |c2| is small there and why that spin alone showed an "extra zero" of F near k = 0.

## 1. The formula checked (the Bridge's first request)
The Bridge's transcription: c2 = tr X² − tr(M1 X M1⁻¹ X), with X = ∮ Φ_K⁻¹ ∂_k A Φ_K "along the loops".
- **The formula is right.** Write M0(k) = I + kX + k²Y + …. Then M0⁻¹ = I − kX + k²(X² − Y), and with X̃ = M1 X M1⁻¹,

      M1 M0 M1⁻¹ M0⁻¹ = I + k(X̃ − X) + k²(Ỹ − X̃X + X² − Y) + O(k³).

  The trace of the k term is 0 and tr Ỹ = tr Y, so tr[M1, M0] − 2 = k²(tr X² − tr X̃X) + O(k³). To this order M1 is
  M1(0). This matches note 3 of the reply draft and `MRS_SECTION.md` §5d. (tr X = 0 is not even needed.)
- **Which loop: X belongs to the circle M0 only**, not to "the loops". X = M0′(0) = ∮_{|z| = R0} Φ_K⁻¹ (∂_k A) Φ_K dz.
  M1 enters only through its Kerr value M1(0). That is what note 3 says; the Bridge's plural was a slip.
- **Why X is that integral.** At k = 0 the circle encloses no singular point, so Φ_K returns to itself around it.
  Variation of constants then gives the first-order change of the circle monodromy as the closed integral.
- **X is analytic at k = 0** (the Bridge's pinch question). On the circle, and on the path from +∞ that defines c0,

      c0″(z; k) = c_K″(z) · √(1 − k(21w² − 18w + 1)/(10(3w − 1)²)),     w = (z/a)²,

  which is analytic in k for |k| < 10·min|3w − 1|²/max|21w² − 18w + 1| over those paths. The pinch points
  w = 1/3 (z = ±a/√3) are inside the circle, at distance ≥ 0.74 from every loop, so the minimum is positive. The
  integrand is O(z⁻⁴) uniformly, so c0, the coefficient matrix A, M0(k) and M1(k) are analytic at k = 0, and
  ∂_k c0 at k = 0 is the function c1 of §2.

## 2. The ingredients at k = 0 (all explicit)
Units M = μ = 1; z is the shifted Weyl coordinate of the claim. Write

    D₊ = z² + a²,   Δ = z² − 2z + a²,   D = (z − 2)² + a²,   N = E²D − Δ,   P = N/D.

- **Lower-axis Kerr data:** f0⁻ = Δ/D (because f0² + c_K² = D/D₊). Poles p± = 2 ± ia; turning points r± = roots of N.
- **Kerr's solutions** (`T38_GRADING.md` addendum): v± = (ND)^{1/4} e^{±κU}, U(z) = ∫ dz/√(ND), κ² = a²(1 − E²).
  Their Wronskian is −2κ. Products: v₊v₋ = √(ND), v±² = √(ND) e^{±2κU}.
- **M1(0)** in the basis (v₊, v₋): the lasso encloses r₊ and p₊, so M1(0) = −diag(e^{κω}, e^{−κω}), with
  ω = ∮ dz/√(ND) around them (= 2∫ from r₊ to p₊).
- **The first-order twist.** From the family's formula, ∂_k c0″ at k = 0 is rational:

      c1″(z) = (21u⁴ − 18u² + 1) / (5a³ (u² + 1)³ (3u² − 1)),     u = z/a,
             = (1/(5a³)) [ −(9/8)/(3u² − 1) + (3/8)/(u² + 1) + (15/2)/(u² + 1)² − 10/(u² + 1)³ ].

  Integrating twice from +∞ (no NUT term):

      c1(z)  = (1/(5a)) [ (5/4)/(u² + 1) − (3/8) u·arccot u − (3√3/16) u·Λ(u) − (3/16) log((u² + 1)/(u² − 1/3)) ],
      c1′(z) = −(1/(5a²)) [ (3/8) arccot u + (3√3/16) Λ(u) + (5/2) u/(u² + 1)² ],

  with Λ(u) = log((√3u − 1)/(√3u + 1)) and arccot u = (1/2i) log((u + i)/(u − i)), principal branches. The cuts are
  the real segment [−a/√3, a/√3] and the imaginary segment [−ia, ia]: a cross inside the circle. c1 ~ 7a/(30z²)
  at infinity.
- **The first-order coefficient.** q = (3/16)(P′/P)² and ∂_k f0⁻ = 4aΔ·c1/D², so

      δq = (3/8)(P′/P)·(g·c1)′,     g = −4aΔ/(D·N).

  g and P′/P are holomorphic inside the circle (their poles are r±, p±). Every singularity of δq inside the
  circle comes from c1.

## 3. The result
With A = [[0, 1], [−q, 0]]: Φ_K⁻¹(∂_k A)Φ_K = (δq/W)·[[v₊v₋, v₋²], [−v₊², −v₊v₋]], W = −2κ. Hence

    x11 = −(1/2κ) ∮ δq √(ND) dz,    x12 = −(1/2κ) I₋,    x21 = (1/2κ) I₊,    I± = ∮_{|z| = R0} δq √(ND) e^{±2κU} dz.

M1(0) is diagonal with entries −m, −1/m (m = e^{κω}), so conjugation multiplies x12 by m² and x21 by m⁻². Then

    c2 = tr X² − tr(M1 X M1⁻¹ X) = (2 − m² − m⁻²)·x12·x21 = −4 sinh²(κω)·x12·x21,

    **c2 = sinh²(κω) · I₊ · I₋ / κ².**

- **The diagonal of X drops out.** Only the two off-diagonal integrals matter.
- **Independence.** I₊I₋ does not depend on R0 (any circle with a < R0 < min|r±, p±|), on the orientation, on the
  base point of U, or on how v± are scaled.
- **I± are purely imaginary.** The integrand is real on the real axis and the circle is symmetric, so
  conj(I±) = −I±. So c2 = −sinh²(κω)·(Im I₊)(Im I₋)/κ².
- **Residue form.** T± = (3/8)(P′/P)·v±² is holomorphic in the disc. Let Ψ± solve Ψ″ = −T±′·g there. Integrating
  by parts three times (c1 and c1′ are single-valued on the circle),

      I± = ∮ Ψ± · c1″ dz = 2πi · Σ Res(Ψ± c1″)   over z = ±a/√3 (simple poles) and z = ±ia (triple poles).

  So I± is a finite combination of the values of one holomorphic function at four explicit points (and its first
  two derivatives at ±ia). Ψ± satisfies a linear ODE with rational coefficients (for rational a and E), with no
  singular point in the disc.
- **Also:** lim (tr M0 − 2)/k² = x11² + x12·x21 = x11² − I₊I₋/(4κ²).

## 4. Numbers (double precision; E = 4/5; `scripts/_nve_c2_analytic.py`)
| spin | κω | tr M1(0) | Im I₊ | Im I₋ | c2 |
|---|---|---|---|---|---|
| 3/10 | 0.84160 − 0.88432i | −1.74370 + 1.46116i | 0.0259336 | 0.0451246 | 0.027942231 + 0.046011986i |
| 3/5 | 1.16468 − 1.28713i | −0.98431 + 2.77728i | 0.0530165 | 0.1761392 | 0.193546372 + 0.098488027i |
| 4/5 | 1.32677 − 1.51803i | −0.21278 + 3.49866i | 0.0313603 | 0.2942039 | 0.162134806 + 0.014905796i |
| 9/10 | 1.39810 − 1.62837i | 0.24714 + 3.79416i | 0.0027764 | 0.3623743 | 0.015814536 − 0.001617585i |

**Checks.**
- **Against the independent 50-digit engine, spin 3/5** (`data/nve/gapb.jsonl`, the 16 stored samples on |k| = 0.3;
  their mean of F/k² is c2 by Cauchy's formula, up to a k¹⁶ alias):

  | quantity | stored (50-digit monodromy code) | this formula |
  |---|---|---|
  | c2 | 0.193546372212344924 + 0.0984880265240703976i | 0.193546372212 + 0.098488026524i |
  | lim (tr M0 − 2)/k² | −0.00478447249769660818 | −0.004784472497697 |
  | tr M1(0) (`lower_comm.jsonl`, via the T38 addendum) | −0.984309504290635 + 2.7772800733203i | −0.9843095042906 + 2.7772800733203i |

  Agreement to every digit the double-precision script prints (12–13). The two share no code.
- **Two routes to I±** (the circle integral, and the residues of Ψ·c1″) agree to ≤ 1e−14 at all four spins.
- **Moving the circle** (R0 = 1.3 → 1.7 at spin 3/5; 1.3 → 1.0 at spin 9/10) changes nothing.
- **Gates on the closed forms:** c1 against direct quadrature of the rational c1″ (≤ 1e−16); c1″ against a finite
  difference in k of the published c0″ (9e−12); Kerr's v± against the ODE; f0⁻ = Δ/D.
- **Other spins:** no stored small-k samples exist (only the count "2 zeros in |k| < 0.3", which is the statement
  c2 ≠ 0). The formula's values at 3/10, 4/5 and 9/10 are therefore checked only by the two internal routes.
- **Where the size comes from:** the ±ia residues dominate (at spin 3/5: 8.66e−3 against −2.2e−4 from the pinch
  points ±a/√3, for I₊).

## 5. Finding: c2 vanishes at a spin near 0.908
| spin | 0.85 | 0.90 | 0.905 | 0.907 | 0.908 | 0.909 | 0.91 | 0.95 | 0.99 |
|---|---|---|---|---|---|---|---|---|---|
| Im I₊ | 1.85e−2 | 2.78e−3 | 1.05e−3 | 3.5e−4 | −1.3e−6 | −3.5e−4 | −7.1e−4 | −1.56e−2 | −3.20e−2 |

- I₊ crosses zero at **a\* ≈ 0.90800** (E = 4/5). I₋ stays positive (0.0046 at spin 0.1, rising to 0.43 at 0.99).
- At a\* the zero of F at k = 0 has order ≥ 3. For a near a\* a third zero sits near k ≈ −c2/c3.
- **This explains the "extra zero" at spin 9/10** (`spin_locateA_9_10.out`: k = 0.110 + 0.341i, |k| = 0.36, found
  post hoc and until now unexplained). It is the third zero, on its way through k = 0 as the spin passes a\*. It is
  non-real for a ≠ a\* because c2 is complex.
- **Consequences.**
  - "c2 ≠ 0" is a per-spin fact, true at the four stated spins and false at a\*.
  - At spin 9/10, c2k² dominates F only for |k| well below 0.36. Any small-k statement there has a small radius.
  - At a\* itself nothing breaks: F = c3k³ + …, still nonzero for small k > 0 if c3 ≠ 0. Not computed.
- Not checked: whether a\* depends on E in a simple way, or has a meaning.

## 6. What this buys, and what a certificate needs
**Statement A (local, would be rigorous once two numbers are certified).** For a ∈ {3/10, 3/5, 4/5, 9/10} and
E = 4/5 there is ε > 0 such that the monodromy group of the ρ-equation is Zariski-dense in SL(2, ℂ) for every
k ∈ (0, ε). It needs only, at k = 0:
1. **Re(κω) ≠ 0.** Then |e^{κω}| ≠ 1, so M1(0) has infinite order, tr M1(0) = −2cosh(κω) ≠ 0, and sinh(κω) ≠ 0.
2. **I₊ ≠ 0 and I₋ ≠ 0.**
3. Analyticity of M0(k), M1(k) at k = 0 (§1).

Then for small k > 0: F ≠ 0 (irreducible); tr M1 ≠ 0 and tr M0 ≈ 2 ≠ 0, so both would be diagonal in an
imprimitive group, contradicting irreducibility; M1 has an eigenvalue off the unit circle, so the group is infinite.
An infinite, irreducible, primitive subgroup of SL₂ is Zariski-dense.
- **ε is not effective.** A is "for all sufficiently small k", not a k-interval with a number on it.
- It is rigorous only relative to the rest of the chain (Proposition 2, Lemma C, the e₋ = 1/e₊ assumption).

**Statement B (stronger, needs one more thing).** F, tr M0, tr M1 and tr M1 − s are analytic in k wherever the two
loops keep their homotopy classes. F ≢ 0 because c2 ≠ 0, and tr M1(0) is non-real, so none of them vanishes
identically. Their zeros on a compact k-interval are then finite in number. So **Zariski-density holds for all but
finitely many k in (0, k1]**, where k1 is the end of the circle picture (about 4.05 in the runs). The extra
requirement is a rigorous version of the geometry guards up to k1: that r₊, p± and the branch points do not cross
the loops. That is root isolation in k, not monodromy certification. The existing counts would then only be needed
to locate the finitely many exceptions.

**How to certify 1 and 2 (cost: seconds).**
- I± is the integral of an explicit analytic function over a circle. For an analytic periodic integrand the
  N-point trapezoid rule has the rigorous error bound 4πM/(e^{Nσ} − 1), where the integrand is analytic and
  bounded by M on the annulus R0·e^{−σ} ≤ |z| ≤ R0·e^{σ}.
- Take R0 = 1.3 and the annulus 1.0 ≤ |z| ≤ 1.69. It contains no singularity at any of the four spins (a ≤ 0.9;
  r₊ ≥ 1.85). With N = 256 the factor is 10⁻²⁹, so any crude M works.
- Needed in interval arithmetic (`mpmath.iv`, as in the sliver certificates, or Arb):
  - the integrand at the N nodes, built from rational functions, two logarithms, a square root and an exponential;
  - U(z): the Taylor series of 1/√(ND) at 0, with the explicit majorant (1/C0)·Π(1 − x/|root|)^{−1/2} for the tail;
  - M: an enclosure of the integrand on arcs covering the two boundary circles.
- ω: the same trapezoid argument after the substitution z = r₊ + (p₊ − r₊)(1 − cos φ)/2, or Arb's elliptic integrals.
- Margins are comfortable: |Im I₊| ≥ 2.8e−3 (spin 9/10, the tightest), |Im I₋| ≥ 0.045, |Re κω| ≥ 0.84.

## 7. If route (i) is still wanted (the whole k-range)
Route (ii) does not replace the k-range certification; Statement B reduces it to geometry plus finitely many
points, but the counts stay numerical until that is done. A concrete plan for (i):
- **What to replace.** The 50-digit power-series continuation in `scripts/_nve_lower.py` / `_nve_lower_kc.py`
  (`Problem.taylor`, the stepper, `F_of_k`) and the boundary sampling in `_nve_lower_kc_count.py` /
  `_nve_lower_hp_count.py`. The geometry code (`capsule_lasso`, the guards) stays, but its inputs (root positions)
  need interval enclosures.
- **Tool: Arb through python-flint (`acb`, `acb_series`)**, already on the box for the quantum project (not in this
  repo's venv). The engine is a Taylor-series stepper, so the natural validated version is the same stepper with
  ball coefficients and a rigorous tail per step: for v″ + qv = 0 with |q| ≤ Q on a disc of radius r, the Taylor
  coefficients of v are majorised by those of y″ = Q·y/(1 − t/r) (Cauchy's estimate on q), and Q comes from a ball
  evaluation of q on the disc. c0 needs the same treatment for its Laurent series (tail from the majorant of √B/(u² + 1)³).
- **k as a ball.** The argument principle needs F on whole boundary segments. Run the stepper with k a ball of
  width h, and subdivide until the enclosure of F along each boundary segment excludes 0 and its argument varies by
  less than π. The alternative used in the sliver, a Gronwall bound on ∂_k, also works but is cruder.
- **Cost, rough.** The floating run at one spin used about 130–200 boundary samples at seconds each. Ball
  arithmetic with a k-ball needs perhaps 10–50 times as many pieces and each is a few times slower: of order hours
  per spin on one core, well under 1 GB. The hard part is not time but the places where F is small on the boundary
  (near k = 0, where F ~ c2k², and near the spin-4/5 degeneracy), which need the local expansions of this note.
- **Alternative:** CAPD (C++), treating (c0, c0′, √B, v, v′) as a polynomial vector field along each path, with k
  as an interval parameter. More machinery to install; no clear gain over Arb here.
- **Recommendation:** do Statement A's certificate first (it is tiny and gives a real theorem near Kerr), then
  decide whether B's geometry or the full (i) is worth the build.

## 8. What the office ansatz-machine should check
1. The algebra of §1–§3, independently, in particular δq, g, the Wronskian and the sign in c2.
2. c1: differentiate the closed form twice (sympy) and compare with ∂_k c0″ of `radicand()` at k = 0.
3. Rerun `scripts/_nve_c2_analytic.py` at the four spins, and add one engine sample of F at k = 0.01 for spins
   3/10, 4/5 and 9/10 (`F_of_k`), to compare F/k² with the table (expect agreement to about 3 digits at k = 0.01).
4. The a\* ≈ 0.908 finding: one engine count or a few F samples near k = 0 at spin 0.908 should show F/k² ≈ 0.
5. Whether Statement A's wording is safe to put in the claim, and whether B's geometry step is worth doing.
