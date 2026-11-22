# Applicability of the Morales–Ramis(–Simó) theorem: the section for the Only-Kerr write-up (draft v2, 2026-11-22; §5 rewritten and §5b–§5e added for Neon T51)

*Built on Neon's T49 draft (UNVERIFIED Gemini output, relayed by the Bridge). Every point was checked or corrected
here; see `data/nve/T48_T49_CHECK.md`. Claims numerically checked by our own code are marked [checked here].
Citation status is in §6.*

## 1. The theorem, and the class of integrals it excludes
Let H be a complex-analytic Hamiltonian with n degrees of freedom. Here n = 2: the reduced (ρ, z, p_ρ, p_z) geodesic
system at fixed E, μ and L_z = 0. Let Γ be a non-equilibrium integral curve, viewed as a connected Riemann surface. It
may be open, or restricted to an open subsurface Ũ on which the coefficients are single-valued.

**Theorem (Morales-Ruiz–Ramis 2001; Morales-Ruiz–Ramis–Simó 2007, Theorem 2 p. 849 and Theorem 5 "Main theorem"
pp. 867–868, for every order k).** Γ is a connected Riemann surface (open allowed; it is the default there), and the
coefficient field is the meromorphic functions on Γ. If H has n functionally
independent first integrals in involution, meromorphic in a neighbourhood of Γ, then the identity component of the
differential Galois group of the m-th variational equation along Γ, over the field of meromorphic functions on Γ, is
abelian for every m ≥ 1.

**Use.** Analytic continuation along loops in Γ (or Ũ) gives elements of the Galois group over M(Γ). The monodromy
we compute, however, belongs to the v-equation in the axis coordinate u, not to the NVE on Γ in the time parameter.
Two finite steps connect them, covered by Lemma C.

**Lemma C (covering and gauge; sources in §6).** Let L be a linear differential equation over the
field K of meromorphic functions on a Riemann surface X, with Galois group G.
- **(a)** If π: X̃ → X is a finite branched covering and L̃ is L pulled back to X̃, over K̃ = M(X̃) ⊇ K a finite
  extension, then Gal(L̃) is a finite-index subgroup of G. So (Gal L̃)⁰ = G⁰.
- **(b)** If ξ = g·v with g algebraic over K (gⁿ ∈ K), the identity components of the Galois groups of the equations
  for ξ and for v coincide.
  - **Proof.** First pass to K′ = K(g), a finite extension. That leaves each identity component unchanged (finite base
    extension; §6).
  - Over K′ the gauge is rational, so the two equations have the same Picard–Vessiot extension and the same Galois
    group over K′.

**Application.**
- **The covering.** Let t be the time along the axis geodesic. Γ_E (y² = P) is a double cover of the u-sphere,
  branched at the odd zeros and poles of P, and du/dt = y·(algebraic factor). So passing from t on Γ to u is a finite
  covering plus an algebraic rescaling of d/dt.
- **The gauge.** The NVE variable ξ1 and v are related by ξ1 = U0^{−1/4}·v = f0^{1/2}·P^{−1/4}·v. That is an algebraic
  gauge: (f0^{1/2}P^{−1/4})⁴ = f0²/P lies in the coefficient field.
- **Conclusion.** Hence (G_NVE)⁰ = (G_v)⁰.
  - The u-plane monodromy is Zariski-dense in SL₂ (checked numerically, and interval-certified on the end sliver), so
    G_v = SL₂ and (G_v)⁰ = SL₂.
  - The index-≤ 2 subgroup coming from Γ_E is still Zariski-dense, because SL₂ is connected.
  - So (G_NVE)⁰ = SL₂, which is non-abelian, and integrability fails by the theorem above.

**On the tree K_k.** It crosses ℝ at u = 1 because the rod endpoints (1 ± √(1 − a²))/a have product 1 and so straddle
u = 1. A crossing at u = 0 would instead cut the physical lower axis.

**Excluded:** every complete set of integrals in involution that is complex-meromorphic in a neighbourhood of the
complexified orbit. This includes all Carter-type, polynomial and rational-in-momenta integrals with coefficients
meromorphic there.

**NOT excluded:**
- (i) integrals that are real-analytic (or C^∞) on the physical exterior but do not continue meromorphically to a
  complex neighbourhood of the orbit;
- (ii) integrals that exist only on isolated energy levels;
- (iii) formal or purely local integrals.

## 2. The equations used
- **Weyl–Papapetrou form; L_z = 0.** The effective potential near the axis is U_eff = U0 + U2ρ² + U4ρ⁴ + …, even in ρ,
  with U0 = P/f0² and P = E² − μ²f0.
- **NVE1:** in the variable v it reads v″ + (3/16)(P′/P)²v = 0. It depends on f0 only.
- **The twist** enters first at VE3, through −μ²(c0″)²/(64f0³) in U4. [The ρ⁴ structure: V25 P1, relayed.]
- **Lower axis:** e₋ = 1/e₊ (a general fact for asymptotically flat data, derived in §5a; no reflection symmetry), so f0⁻ = f0/(f0² + c0²) and c0⁻ = −c0/(f0² + c0²).
- **The curve Γ_E:** the double cover y² = P of the axis line. It is ramified at the odd-order zeros and poles of P.

## 3. Punctures (singular points), checked against our code
**General rational axis data (upper axis; on the lower axis with f0 → f0⁻):**
| point | NVE1 (v) | VE3 | note |
|---|---|---|---|
| simple zeros of P (turning points) | regular singular, exponents ¼, ¾, local monodromy order 4 | yes | on Γ_E the ξ1-monodromy is trivial |
| simple poles of f0 (poles of P) | regular singular, exponents ¼, ¾ | yes, higher-order poles of U4 | |
| poles of c0 that are not poles of f0 | ordinary | regular singular | VE3 only |
| zeros of f0 (P = E² ≠ 0) | ordinary in v | poles of U4 (order 6 static, order 3 twist) | ξ1 sees −I |
| z = ∞ | ordinary for E² ≠ μ² (q = O(z⁻⁴)) | regular singular | asymptotic flatness |

**Family (ii) (branched twist; u = z/a; 0 < a < 1; 0 < k ≤ 30/7):**
- **u = ±i:** poles of f0 and P. **c0 has a (u ∓ i)log(u ∓ i) branch point there for every k ∈ (0, 30/7]**, from the
  t⁻¹ residue of √B/(u² + 1)³.
- **The zeros of B(u², k):**
  - 0 < k < 4: four points ±α ± iβ with |u| = ((10 − k)/(90 − 21k))^{1/4} < 1;
  - 4 < k < 30/7: four points ±iy1 and ±iy2, with 0 < y1 < 1 < y2;
  - k = 30/7: two points ±i/√3.
  - These are square-root branch points of c0 (c0 ~ (u − ζ)^{5/2}). [The B roots at k = 1 were checked by hand.]
- **Zeros of f0:** u = (1 ± √(1 − a²))/a, the horizon-rod endpoints. [At spin 0.6: u = 1/3 and 3, i.e. z = 0.2 and 1.8,
  matching ours.]
- **Lower-axis poles:** the zeros of f0² + c0², the pair p±. [Checked here: at spin 0.6 they match our p± at
  k = 1, 2 and 30/7, at the endpoint to every printed digit.]
- **Lower-axis turning points:** the zeros of P₋, which are transcendental for k > 0. Bound orbits (E < 1) have a real
  one on the physical lower axis. [Checked here: at spin 0.6, E = 0.9, u = −14.150188915044… (k = 1) and
  −14.139807205785… (k = 30/7), agreeing with T49 to 2.5e−44 and 2.3e−44.]
- **u = ∞:** not a branch point of c0, because deg B is even and c0″ = O(u⁻⁴), or O(u⁻⁵) at k = 30/7.

## 4. The single-valued domain U_a, and the off-axis metric
- **U_a:**
  - Let K_k be a compact tree joining every finite branch point of c0 (the zeros of B and ±i). It crosses ℝ only at
    u = 1, inside the horizon rod for every 0 < a < 1. Set U_a = P¹ ∖ K_k.
  - **Proposition 1.** On U_a the functions c0″, c0′ and c0 (the asymptotically-flat integrals from ∞) are
    single-valued and holomorphic. Then e₊, e₋ and the NVE and VE coefficients on both axes are single-valued and
    meromorphic.
  - **Proof.** π₁(ℂ ∖ K_k) is generated by a large circle. √B is single-valued there, because it encloses an even number
    of simple roots. And ∮ c0″ = ∮ s·c0″ = 0, because c0″ = O(u⁻⁴).
  - U_a contains both physical outer axis segments and a neighbourhood of ∞.
  - [Consistent with our computations: the circle picture |z| > ρ_c and the half-plane picture both lie in U_a. T49's
    loop-return control (1e−55 inside U_a; a loop around +i alone fails) agrees.]
- **Scope note.** A small loop around u = ±i alone leaves U_a, because of the log branch point. That would matter only
  for an upper-axis VE3 test of family (ii). **The proof does not use one:** family (ii) is obstructed at FIRST order
  on the lower axis, by loops inside U_a. For the rational-twist class, c0 is rational and has no logs, so the issue
  does not arise there either.
- **Proposition 2 (the off-axis metric is single-valued; citation pending, see §6).**
  - On a tubular neighbourhood of W = U_a ∖ {f0 = 0, f0² + c0² = 0}, the Ernst potential reconstructed from the axis
    data (even series in ρ², with recursion 4n² f0 e_{2n} = P_n(e_0, …, e_{2n−2})) converges and is single-valued
    (Fuchsian Cauchy–Kovalevskaya; Hauser–Ernst / Sibgatullin axis-data reconstruction).
  - ω and γ come from closed 1-forms whose pullbacks to ρ = 0 vanish, so all their periods are zero.
  - **Status:** plausible, and correctly excludes the zeros of f0. The citations must be checked before it is called
    proved.

## 5. The lower-axis data, and why both outer axis segments must be regular (rewritten 2026-11-22 for Neon T51)
**Conventions (stated, because T51 found them missing).**
- M = 1 and μ = 1 (timelike geodesics; E is the energy per unit mass).
- z is the Weyl coordinate shifted by M: z = z_Weyl + M. Then Kerr's upper-axis data read
  e₊ = (z − ia − 2)/(z − ia) and f0 = 1 − 2z/(z² + a²). On the upper axis z is the Boyer–Lindquist r.
- The rod endpoints are z = 1 ± √(1 − a²). **The lower outer axis is z < 1 − √(1 − a²), which contains every z ≤ 0.**
- c0 is fixed by c0, c0′ → 0 as z → +∞ (asymptotic flatness, no NUT charge). The branch of √B is the one analytic
  on U_a and positive as u → +∞, so c0″ < 0 there. At k = 0 this gives Kerr's c0 = −2a/(z² + a²) (checked:
  c0″ = −4(3u² − 1)/(a³(u² + 1)³), whose square is the k = 0 member).

**(a) The identity e₋ = 1/e₊ is general for asymptotically flat data, and has nothing to do with equatorial symmetry.**
Here e₊ means the upper-axis function continued in z through z = ∞, i.e. analytically in 1/z, to the lower axis.
Write ξ = (1 − E)/(1 + E). Then e₋ = 1/e₊ is the same statement as ξ₋ = −ξ₊.
1. **Analyticity at infinity.** Conformally compactify the 3-space near spatial infinity, with r̄ = 1/r and
   conformal factor Ω = r̄². The rescaled potential ξ̃ = Ω^{−1/2} ξ = ξ/r̄ is analytic in the compactified Cartesian
   coordinates x̄ at the point Λ added at infinity (Beig–Simon 1981; FHP 1989 do this in compactified Weyl
   coordinates, ρ̄ = ρ/(ρ² + z²) and z̄ = z/(ρ² + z²)).
2. **Restrict to the axis.** The axis is the line ρ̄ = 0 through Λ, and both outer axis segments end there. On the
   axis z̄ = 1/z on BOTH segments: positive on the upper one, negative on the lower. So ξ̃|axis = F(1/z) for ONE
   function F, analytic at 0.
3. **The conformal-factor step.** Undo the rescaling: ξ = r̄ ξ̃, and on the axis r̄ = |z̄| = 1/|z|. Hence
   - ξ₊(z) = F(1/z)/z on the upper axis (z > 0, |z| = z), and
   - ξ₋(z) = F(1/z)/(−z) on the lower axis (z < 0, |z| = −z).
   So **ξ₋ = −ξ₊ as analytic functions of 1/z, i.e. e₋ = 1/e₊.** The only non-analytic ingredient is the conformal
   factor |z|, and it supplies the sign. (Shifting z by a constant changes nothing at this order: F(1/z) stays analytic
   in 1/(z − c).) In the static case this is just the exterior multipole expansion: ψ = −Σ M_n P_n(cos θ)/r^{n+1}
   gives ψ₋(z) = −ψ₊(z), because P_n(−1)/(−z)^{n+1} = −1/z^{n+1}.
4. **From near infinity to the whole lower outer segment.** e₋ is real-analytic along any regular axis segment, and
   1/e₊, continued along the real line from −∞, is meromorphic there. For 0 ≤ k ≤ 30/7 no branch point of c0 lies on
   the real line (the B roots are complex or on the imaginary axis; the logs sit at ±ia). Two analytic functions that
   agree near −∞ agree on the whole segment.
5. **Exact checks** (`scripts/_nve_t51_axis_check.py`, output `t51_axis_check.out`):
   - **Kerr, from its closed-form Ernst potential** 1 − 2M/(r − ia cos θ). With θ = 0 at z = r and θ = π at
     z = 2M − r, e₋·e₊ − 1 = 0 identically.
   - **Two Curzon particles of unequal mass (1 and 3, at 0 and 1).** This static vacuum solution has NO plane of
     reflection symmetry: the 1/t² term of ψ₊(z0 + t) + ψ₊(z0 − t) vanishes only at z0 = 3/4, and the 1/t⁴ term is
     3/4 ≠ 0 there. Yet ψ₋ + ψ₊ = 0 identically, so e₋ = 1/e₊ exactly.
**Where the reflection condition comes from.** Equatorial reflection symmetry means E(ρ, −z_c) = conj E(ρ, z_c), with
z_c centred on the equatorial plane. On the axis this says e₋(−z_c) = conj e₊(z_c). Combine it with (a), e₋ = 1/e₊,
and you get the Kordas / Meinel–Neugebauer condition e₊(z_c)·conj e₊(−z_c) = 1. **So (a) is an input to that
condition, not a consequence of it.** [Source check of Kordas 1995 / Meinel–Neugebauer 1995: see §6.]
- The condition also depends on where the origin is. Kerr satisfies it in z_c, but in the claim's shifted z,
  e₊(z)·conj e₊(−z) − 1 = −4M²/(z − ia)² ≠ 0 (checked). Kerr is symmetric; the shifted origin is simply not on its
  equatorial plane.
- Family (ii) with k ≠ 0 is probably not reflection-symmetric. Nothing in the proof uses reflection symmetry.

**(b) Robustness: what the NVE is the NVE of.** Morales–Ramis is local around Γ. Proposition 2, applied on the lower
axis, gives a vacuum metric near the lower outer axis whose axis data are e₋ := 1/e₊. The NVE we integrate is the NVE
of that metric. So even a reader who doubted (a) would get a non-integrability statement about a definite vacuum
metric. What (a) adds is the identification: this is the same spacetime as the one with upper-axis data e₊.

**(c) Regularity on the outer axes.**
1. The axis expansions U0, U2, U4 on a segment need the data to be real-analytic there, i.e. the segment regular.
2. **Elementary flatness on the outer segments comes free for asymptotically flat data.**
   - γ is constant along each regular axis segment, and → 0 at infinity. Both outer segments reach infinity, so γ = 0
     on both.
   - ω is constant on each segment. Its jump across infinity is the NUT charge, i.e. the 1/z term of Im ξ₊. For
     family (ii) that term is zero (c0 = O(u⁻²), or O(u⁻³) at 30/7), so ω = 0 on both.
   - Struts can appear only on INNER segments; the rod [1 − √(1 − a²), 1 + √(1 − a²)] is one, unchecked.
3. **Which k are regular on both outer axes:**
   - For k < 0, B(w, k) has two roots 0 < w1 < w2. The points z = −a√w1 and −a√w2 are negative, so they lie on the
     lower outer axis for EVERY spin, and c0″ is imaginary between them (`T38_GRADING.md` 1c). At k = −1 and a = 0.6
     they sit at z = −0.265 and −0.427.
   - (T51's "inside the horizon rod" places these roots in the centred coordinate. Its threshold a < √3/2 is exactly
     the centred-rod test, which is the wrong convention for this family.)
   - For 0 ≤ k < 4, B > 0 on w ≥ 0 (negative discriminant, positive leading coefficient).
   - For 4 ≤ k ≤ 30/7, all three coefficients of B are positive (or the leading one is zero at 30/7), so B > 0 on
     w ≥ 0.
   - For k > 30/7, B < 0 at large w, on both axes.
   - So the outer-axis-regular range is exactly 0 ≤ k ≤ 30/7. **"Regular on both outer axes" means exactly this
     axis statement. It is not a claim about off-axis regularity, horizons or black holes (see (d)).**

**(d) Off the axis, and what the members are (T51 point 5; agreed).**
- By black-hole uniqueness (Chruściel–Costa 2008), no k ≠ 0 member is a regular, stationary, asymptotically flat
  vacuum black hole with a connected non-degenerate horizon and no naked singularities or CTCs.
- So the members are stationary axisymmetric vacuum fields with Kerr's mass profile on the axis. At best they model
  the exterior of some non-black-hole source; at worst they carry singularities or CTCs off the axis.
- **Nothing off the axis has been checked: horizons, the rod, naked singularities, CTCs.** The NVE needs the metric
  only in a complex neighbourhood of the axis orbit (Proposition 2).

## 5b. The NVE in regular transverse coordinates (T51 point 3)
- **The problem.** ρ = 0 is the fixed-point set of the axial U(1). So (ρ, φ) and the L_z = 0 reduction are singular
  on Γ.
- **The fix.** Work instead with x = ρ cos φ, y = ρ sin φ. These are regular near the axis, because the outer segments
  are elementarily flat (§5c). Use the full geodesic Hamiltonian on T*M, with p_t = −E a global integral.
- **The variational equation along the axis orbit is block-triangular:**
  - an (x, p_x, y, p_y) block, and
  - the tangential and (t, p_t) blocks, which are solvable by quadratures.
- **The (x, y) block is two identical copies of NVE1.** Rotation about the axis acts on the (x, y) plane and fixes
  the orbit. To second order the only rotation-invariant quadratic form in (x, y) is x² + y². So the transverse
  Hessian is a multiple of the identity, and the δx and δy equations coincide with our ρ-equation.
- **So the monodromy and Galois group of the (x, y) block are {diag(g, g) : g ∈ G1}**, with Zariski closure the
  diagonal copy of the closure of G1. Its identity component is non-abelian iff G1⁰ is.
- **This passes to the full VE.** G⁰ of a subquotient of the full VE is a quotient of the full G⁰, and quotients of
  abelian groups are abelian. So a non-abelian G1⁰ forbids abelian (G_VE)⁰, which Morales–Ramis requires of an
  integrable system.
- No singular reduction is used.

## 5c. Loops and the zeros of f0 (T51 point 2)
- **Proposition 2 is stated on W = U_a ∖ {f0 = 0, f0² + c0² = 0}.** On the lower axis the Ernst reconstruction
  degenerates where f0⁻ = 0, which happens exactly where f0 = 0: the two rod endpoints.
- **NVE1 is holomorphic at those points** (P = E² ≠ 0, §3). Removing finitely many points from a Riemann surface X
  gives π₁(X ∖ pts) → π₁(X) onto. So the NVE1 monodromy group over W equals the group over the larger NVE1 domain.
- **Concretely:** any of our loops that happened to pass through a rod endpoint can be pushed off it without changing
  its matrix. Every generator is therefore realised by a loop in W.
- Proposition 2 is needed only on such loops, at REAL k. The k-region counts need only holomorphy of the NVE1
  monodromy in k, which comes from the axis data alone.
- **Proposition 2 itself is still an argument with citations pending (§6).**

## 5d. The neighbourhood of k = 0 (T51 point 6)
- **The question.** The argument-principle region encloses k = 0, where F = tr[M1, M0] − 2 has Kerr's zero. Could
  some zeros have split off onto (0, ε)?
- **F = O(k²), structurally.**
  - At k = 0 the circle |z| = R0 encloses no singular point of NVE1:
    - the data are Kerr's (rational, c0 = −2a/(z² + a²));
    - f0⁻ is regular at ±ia (1/e₊ is regular there);
    - B(w, 0) = 10(3w − 1)² is a perfect square, so √B is single-valued;
    - r± and p± lie outside the circle (the geometry guard).
  - So M0(0) = I, and M0(k) = I + kX + O(k²) on a neighbourhood where the circle data are analytic in k
    (B(u², 0) ≠ 0 on the circle).
  - Then tr[M1, M0] − 2 = k(tr M1XM1⁻¹ − tr X) + O(k²) = O(k²). Likewise det M0 = 1 forces tr X = 0, so
    tr M0 − 2 = O(k²).
- **Hence the zero at k = 0 has order ≥ 2.** The counts give:
  - |k| < 0.3: exactly 2 at every spin (control C1);
  - the whole region: 2 (gap B at spin 0.6; region A at spins 0.3 and 0.8), or 3 at spin 0.9, where the extra zero
    was located and is non-real.
- So the zero at 0 has order exactly 2, and the only other zero is that located non-real one. Given the counts this is
  exact; the counts themselves are 50-digit floating point, like the rest.

## 5e. k = 4 (T51 point 7)
- **At k = 4, B(w, 4) = 6(w + 1)².** The B roots meet ±i, so √B becomes rational there.
- **This does not affect holomorphy in k of either loop family.**
  - **Circle picture.** The collision is inside |z| = R0. On the circle, B(u², k) ≠ 0 and the Laurent data are
    analytic in k across 4: the leading coefficient is ∝ 90 − 21k, which is nonzero at k = 4.
  - **Half-plane picture (window [3.95, 30/7 − 10⁻¹²]).** The branch points involved sit near Re z = 0, and every
    cut ray points left. The window's guards checked at every grid and boundary sample that no cut ray crosses the
    working region.
- k = 4 lies inside both the gap-B region (0, 4.05] and the window, so it is covered twice.
- **The spin-0.8 degeneracy near 4.0082** is a zero of tr Γ in the half-plane pair. No mechanism ties it to k = 4. It
  is settled by an independent pair either way.

## 6. Citations: status (checked at source 2026-11-22; texts in our scratchpad)
- **Morales-Ruiz, Ramis & Simó, Ann. Sci. ÉNS (4) 40 (2007) 845–884, DOI 10.1016/j.ansens.2007.09.002: VERIFIED (full
  text).**
  - Theorem 2 (p. 849): first integrals meromorphic "in a neighbourhood of Γ"; (G_k)⁰ is commutative for each k.
  - Theorem 5 (Main theorem, pp. 867–868).
  - Γ is a connected Riemann surface, **open by default**. So MRS itself covers our open subsurface Ũ.
- **Casale, Ann. Inst. Fourier 59 (2009) 2593–2610, DOI 10.5802/aif.2501: citation real, but T49's use is NOT
  SUPPORTED.**
  - Casale's setting is algebraic: rational equations, algebraic solutions, rational first integrals.
  - It is not a wider, open-surface version. **Do not cite it for open Γ.** Cite MRS 2007 instead.
  - (It does generalise to virtually solvable groups for integrability by quadratures.)
- **Beig & Simon, "On the multipole expansion for stationary space-times", Proc. R. Soc. Lond. A 376 (1981) 333–341,
  DOI 10.1098/rspa.1981.0095: VERIFIED (abstract).**
  - Stationary asymptotically flat space-times are "analytic in a neighbourhood of spatial infinity".
  - Caveat, read secondhand (Bäckdahl–Herberthson gr-qc/0606115): this may require nonzero mass. Ours is M = 1.
- **Beig & Simon, Commun. Math. Phys. 78 (1980) 75–82: a static UNIQUENESS result.** Do not cite it for analyticity.
- **Lemma C(a), finite branched coverings:** Morales-Ruiz & Ramis, Methods Appl. Anal. 8 (2001) 33–95, **Theorem 5**.
  - SECONDHAND: quoted with this number by Acosta-Humánez & Blázquez-Sanz, arXiv:math-ph/0610010, p. 8 ("injective
    homomorphism Gal(∇′) → Gal(∇) … isomorphism between their Lie algebras").
  - Worked double-cover case VERIFIED at source: Audin, Ann. Fac. Sci. Toulouse 12 (2003) 1–23, p. 7. A double cover
    ramified at the roots of P and at ∞, with identity components isomorphic. That is exactly our Γ_E → u-sphere step.
  - Morales-Ruiz 1999 (Progr. Math. 179), "Theorem 2.5": NOT confirmed (the book was not accessible).
- **Lemma C(b), finite base extension and gauge:**
  - Combot, arXiv:1209.4747, Lemma 3 (p. 4): a finite extension of the base field gives the same identity component.
    VERIFIED.
  - Singer, arXiv:0712.4124, Corollary 1.3.10(3) (p. 14): K^{G⁰} is the algebraic closure of k in K. VERIFIED.
  - The rational-gauge step over K(g) is immediate.
  - (van der Put–Singer 2003, "Prop. 1.34": number NOT confirmed.)
- **Fodor, Hoenselaers & Perjés, J. Math. Phys. 30 (1989) 2252–2257, DOI 10.1063/1.528551: VERIFIED (abstract).**
  Moments are expressed through the expansion coefficients of the axis Ernst potential.
- Baouendi–Goulaouic (Fuchsian Cauchy–Kovalevskaya); Hauser–Ernst 1981; Sibgatullin: to check.
- Maciejewski–Przybylska–Stachowiak 2013: body read in full by the Bridge and Neon T47 (relayed); used only for ZV
  δ = 2 (first-order NVE along an equatorial radial geodesic).
