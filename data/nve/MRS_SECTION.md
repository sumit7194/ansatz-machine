# Applicability of the Morales–Ramis(–Simó) theorem: the section for the Only-Kerr write-up (draft v1, 2026-11-22)

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

**Lemma C (covering and gauge; source being checked, see §6).** Let L be a linear differential equation over the
field K of meromorphic functions on a Riemann surface X, with Galois group G.
- **(a)** If π: X̃ → X is a finite branched covering and L̃ is L pulled back to X̃, over K̃ = M(X̃) ⊇ K a finite
  extension, then Gal(L̃) is a finite-index subgroup of G. So (Gal L̃)⁰ = G⁰.
- **(b)** If ξ = g·v with g algebraic over K (gⁿ ∈ K), the equations for ξ and for v have Picard–Vessiot extensions
  that differ by the finite algebraic extension K(g). So their Galois groups have the same identity component.

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
- **Lower axis:** e₋ = 1/e₊, so f0⁻ = f0/(f0² + c0²) and c0⁻ = −c0/(f0² + c0²).
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

## 5. Why both outer axis segments must be regular (an argument, not a proof)
1. **e₋ = 1/e₊** comes from analyticity at spatial infinity: Beig–Simon 1981 (not 1980), together with the
   Fodor–Hoenselaers–Perjés relation between multipole moments and axis data. It also uses the Meinel–Neugebauer
   1995 relation, which was read in the original.
2. **The axis expansions** U0, U2, U4 on a segment need that segment to be regular, with no strut or Misner string.
3. **Consequence used in the family:** regularity on the LOWER outer axis excludes k < 0. For k < 0, B has two
   positive roots in w, so c0 is complex on part of z < 1 − √(1 − a²) (`T38_GRADING.md` 1c).
4. No equatorial symmetry is needed.

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
- **Fodor, Hoenselaers & Perjés, J. Math. Phys. 30 (1989) 2252–2257, DOI 10.1063/1.528551: VERIFIED (abstract).**
  Moments are expressed through the expansion coefficients of the axis Ernst potential.
- Baouendi–Goulaouic (Fuchsian Cauchy–Kovalevskaya); Hauser–Ernst 1981; Sibgatullin: to check.
- Maciejewski–Przybylska–Stachowiak 2013: body read in full by the Bridge and Neon T47 (relayed); used only for ZV
  δ = 2 (first-order NVE along an equatorial radial geodesic).
