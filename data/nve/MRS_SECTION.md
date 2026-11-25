# Applicability of the Morales–Ramis(–Simó) theorem: the section for the Only-Kerr write-up (draft v2, 2026-11-22; §5 rewritten and §5b–§5e added for Neon T51)

*Built on Neon's T49 draft (UNVERIFIED Gemini output, relayed by the Bridge). Every point was checked or corrected
here; see `data/nve/T48_T49_CHECK.md`. Claims numerically checked by our own code are marked [checked here].
Citation status is in §6.*

## 1. The theorem, and the class of integrals it excludes
Let H be a complex-analytic Hamiltonian with n degrees of freedom. Here n = 2: the reduced (ρ, z, p_ρ, p_z) geodesic
system at fixed E, μ and L_z = 0. Let Γ be a non-equilibrium integral curve, viewed as a connected Riemann surface. It
may be open, or restricted to an open subsurface Ũ on which the coefficients are single-valued.

**CORRECTED 2026-11-24 (Neon, layer 5 of the Maciejewski-reply check): which system the theorem is applied to.**
- **Do not reduce by p_φ.** The (ρ, z) system at L_z = 0 above is the convenient source of the ρ-equation. But the
  S¹ action is singular on the axis, so it is not the system to which the theorem is applied.
- **Do not work on T*M with t present either.** t(z) = ∫E/(f0⁻ ż) dz is multivalued around our loops, so the lifts
  of the loops do not close in T*M.
- **Reduce by the cyclic coordinate t instead.** Fix p_t = −E. Any further first integral F of the geodesic flow with
  {F, p_t} = 0 is independent of t and descends.
- **The system used.** The t-reduced Hamiltonian H_E on the 3-degree-of-freedom phase space
  (x, y, z, p_x, p_y, p_z), with x = ρ cos φ and y = ρ sin φ (regular near the outer axes, §5b), on the level
  H_E = −μ²/2. It has the integrals H_E and p_φ = x p_y − y p_x.
- **The curve Γ0.** The axis orbit x = y = p_x = p_y = 0, p_z² = P/f0⁻², viewed over a bounded domain D ⊂ U_a that
  contains all our loops, minus the zeros and poles of P. On the double cover y² = P (Lemma C) the loops close.
- **What the theorem excludes.** A third integral, independent of H_E and p_φ, in involution with them, and
  meromorphic in a neighbourhood of Γ0. Equivalently, on T*M: a fourth integral beyond H, p_t and p_φ.
- **Holomorphy of H_E near all of Γ0, including the complex loops.** Prop. 2 (§4b) is proved on compact subsets of the
  COMPLEX z-domain W = U_a ∖ {f0 = 0, f0² + c0² = 0}; on the lower axis these are f0⁻ ≠ 0 and no poles of e₋. The loops
  lie in W (§5c), and γ and ω are holomorphic quadratures there (§4). So H_E is holomorphic on a neighbourhood of Γ0.
- The rest of the argument is §5b's transverse block and Lemma C, unchanged.

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
  - **(Added 2026-11-24.)** c0″ has no u⁻¹ term at ∞, so c0′ and c0 have no logarithm there. c0 is holomorphic at ∞
    with c0(∞) = 0, and its Laurent coefficients are real (B has real coefficients and the branch is fixed real at
    +∞). So c0 is real on the lower outer axis too, which justifies f0⁻ and c0⁻ as real axis data.
- **Sign of c0″ on the real line, and c0 at the rod endpoints (added 2026-11-24, hand; checked numerically).**
  - **Why √B keeps one sign.** For 0 < k ≤ 30/7, B(u², k) > 0 for all real u (§5c). Each real segment of U_a,
    u > 1 and u < 1, is connected without crossing the tree. So √B has one sign on each segment:
    - on u > 1: + (the normalisation at +∞);
    - on u < 1, reached through ∞: + for k < 30/7, where √B ~ √(90 − 21k)u² is even; − at k = 30/7, where
      √B ~ √(120/7)u is odd.
  - **Hence c0 never vanishes on the outer axes.** On the upper side c0 = ∫_z^∞ (s − z)c0″ ds with c0″ < 0, so
    c0 < 0. On the lower side c0 = ∫_{−∞}^z (z − s)c0″ ds: < 0 for k < 30/7, > 0 at k = 30/7. So c0 ≠ 0 on both
    outer axes, in particular at both rod endpoints. Therefore f0² + c0² ≠ 0 there, and the rod endpoints are ordinary
    points of NVE1, as stated.
  - **Numerical check** (`scripts/_nve_rodend_c0.py` → `data/nve/rodend_c0.out`; spins 3/10, 3/5, 4/5, 9/10; 12 values
    of k in (0, 30/7]):
    - every rod-end c0 is nonzero, with the predicted sign;
    - the real-line quadratures agree with the code's own Laurent series at z = ±2 to ≤ 6e−42, wherever that series
      exists (spins 3/10, 3/5, 4/5);
    - the wrong lower branch disagrees by 0.26–0.61 (must-fail).
- **Two discontinuities in k of the REAL lower-axis data (found 2026-11-24 while doing the check above; hand, plus
  `rodend_c0.out`). Neither affects any monodromy computation.**
  - **At k → 0+.** For k > 0, √B stays positive on all of u < 1. At k = 0 the analytic branch is √10(3u² − 1), which
    is negative for |u| < 1/√3. So on the lower-axis segment −1/√3 < u < min(1/√3, u_rod−), with
    u_rod− = (1 − √(1 − a²))/a, the k → 0+ limit of c0″ is −c_K″, not Kerr's c_K″. (The min matters at spin 9/10,
    where u_rod− = 0.627 > 1/√3; the Bridge's correction.) The branch points pinch the real line at u = ±1/√3.
    Examples:
    - c0″(0) → −4/a³, while Kerr's value is +4/a³;
    - at spin 3/5, c0 at the lower rod end → −5.94, while Kerr's is −3.0.
    So the family is NOT a small deformation of Kerr near the lower end of the rod. Near z = −a/√3, on the physical
    lower axis, the data vary on a scale ~√k.
  - **At k → 30/7−.** On the whole lower axis c0 → −|c0|, but at k = 30/7 exactly c0 = +|c0|: the twist flips sign.
    f0⁻ = f0/(f0² + c0²) is even in c0, so NVE1 on the lower axis is continuous there. Only c0⁻, and hence the
    frame-dragging angle Θ of §5b, changes sign.
  - **Why the loops are unaffected.** All our loops lie where the data are analytic in k: the circle |z| = R0 > ρ_c,
    the lassos in |z| > 1.3, and the half-plane disc near z = 2.
  - **Distances, checked against the stored geometry** (`spin_geo_*.json`, `GAPB_PREREGISTRATION.md`; the loop
    constructors are `_nve_spin_scan.py` L206 and L228, and `_nve_lower_kc.py` L105 and L129).
    - In the circle picture, which contains k = 0, M0 is |z| = R0 and the lasso M1 is based at b = R0 on ℝ. Its tail
      runs along ℝ toward the capsule around [r+, p+], which sits at Re z ≈ 1.85–2 at k = 0.
    - So the smallest distance from any loop or base point to the pinch interval |z| ≤ a/√3 is R0 − a/√3:
      0.976, 1.004, 0.876 and 0.744 at spins 3/10, 3/5, 4/5 and 9/10.
    - The half-plane bases (used only for k ≥ 3.8, far from the pinch in k) are 1.481, 1.004, 0.843 and 0.630 away.
    - So the O(k²) statement of §5d is unaffected. The physical lower orbit lies on the same connected
    Γ0 through U_a. The claim's "k = 0 is Kerr" holds at k = 0 exactly. Continuity of the family at k = 0 was never
    claimed, and it fails near the lower rod end.

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
- **Proposition 2 (the off-axis metric is single-valued; proof in §4b, not yet independently checked; sources §6).**
  - On a tubular neighbourhood of W = U_a ∖ {f0 = 0, f0² + c0² = 0}, the Ernst potential reconstructed from the axis
    data (even series in ρ², with recursion 4n² f0 e_{2n} = P_n(e_0, …, e_{2n−2})) converges and is single-valued
    (Fuchsian Cauchy–Kovalevskaya; Hauser–Ernst / Sibgatullin axis-data reconstruction).
  - ω and γ come from closed 1-forms whose pullbacks to ρ = 0 vanish, so all their periods are zero.
  - **Status (2026-11-22, after the source check in §6): uniqueness CHECKED here; convergence CITED, with the fit to
    the cited theorem written out here but not confirmed in any source.**
    - **Setting.** Complexify to the pair (E, Ẽ) with ẽ(z) = conj e(conj z), and f = (E + Ẽ)/2. With t = ρ², the
      flat axisymmetric Laplacian is Δ = 4t∂t² + 4∂t + ∂z² = (4/t)(t∂t)² + ∂z², and |∇E|² = 4tE_t² + E_z².
    - **The formal recursion (checked here).** The equation f ΔE = ∇E·∇E becomes, at order t^{n−1},
      4n² f0 e_n = (terms in e_0 … e_{n−1} and their z-derivatives). The only term containing e_n is f0·4n² e_n. The
      indicial polynomial is 4f0 k², which vanishes only at k = 0, the free axis datum. **So for f0 ≠ 0 the even
      series is uniquely determined by the axis value.** This is the recursion stated above.
    - **Convergence: the Fuchsian Cauchy–Kovalevskaya theorem of Baouendi–Goulaouic.**
      - The 1974 announcements were read at source. Their Theorem 4 covers the scalar higher-order case. Their
        Example (31) is the axisymmetric problem Δ_y u + f(|y|², x, y·∇_y u, D_x^α u) = 0 with u(x, 0) given, which
        has a unique analytic solution ũ(x, |y|²), analytic in x and so in complex z.
      - **The Ernst equation fits only after a reduction:** subtract e0 + t·e2 so that |∇_y E|² becomes admissible,
        then treat (E, Ẽ) as a system. The reduction was written by the checking agent, not found in a source. The
        systems version is in the 1976 JDE paper, which was NOT read (paywalled).
    - **Closest rigorous analogue, read at source:** Bäckdahl, gr-qc/0612043. In complexified Weyl coordinates it
      proves convergence of the analogous recursion by majorants (Lemma 7), and uniqueness in the analytic class
      (Theorem 8). But it does so at infinity, with data on a characteristic, not on the real axis.
    - **ω and γ:** quadratures of closed 1-forms whose pullbacks to ρ = 0 vanish, so all periods are zero (unchanged).
    - **Net:** Prop. 2 is no longer an argument with nothing cited. It is "unique by the recursion (checked);
      convergent by Baouendi–Goulaouic, via a reduction we state ourselves". Calling it proved needs either the 1976
      systems theorem read at source, or a short majorant proof written out, as in Bäckdahl's Lemma 7.
    - **Superseded:** the majorant proof is now written out in §4b. It is not yet independently checked.

## 4b. Proposition 2: convergence by a majorant (our own proof, 2026-11-22)
**Claim.** Let K be a compact subset of W, the complex z-domain where the axis data a0 = e (and b0 = ẽ) are
holomorphic and c0 = (a0 + b0)/2 = f0 ≠ 0. Then the formal series E = Σ a_n(z) tⁿ and Ẽ = Σ b_n(z) tⁿ (t = ρ²) of
§4 converge for |t| < τ_K, uniformly for z in K, with τ_K > 0. So E and Ẽ are holomorphic in (t, z) there and
solve the complexified Ernst system.

**Recursion.** For n ≥ 1, read off at order t^{n−1} from f·(4tE_tt + 4E_t + E_zz) = 4tE_t² + E_z², with
f = (E + Ẽ)/2 = Σ c_n tⁿ:

    4n² c0 a_n = − Σ_{j=1}^{n−1} 4(n−j)² c_j a_{n−j} − Σ_{i+j=n−1} c_j a_i″ + 4 Σ_{i+j=n; i,j≥1} i j a_i a_j
                 + Σ_{i+j=n−1} a_i′ a_j′,

and the same with a and b swapped (c_j is common). Only the term 4n² c0 a_n contains index n, so the recursion is
well defined exactly where c0 ≠ 0.

**Norms (Nagumo).** Fix z0 ∈ K and R > 0 with the closed disc D = {|z − z0| ≤ R} inside W. Let d(z) = R − |z − z0|,
and for u holomorphic on the open disc set ‖u‖_p = sup_D |u(z)| d(z)^p.
- (N1) ‖uv‖_{p+q} ≤ ‖u‖_p ‖v‖_q. Immediate.
- (N2) Nagumo's lemma: ‖u′‖_{p+1} ≤ e(p + 1)‖u‖_p. Proof: apply Cauchy's estimate on the disc of radius
  d(z)/(p + 1) about z. On it d ≥ d(z)·p/(p + 1), so |u′(z)| ≤ ((p + 1)/d(z))·‖u‖_p·(d(z)p/(p + 1))^{−p}, and
  (1 + 1/p)^p ≤ e. For p = 0 the plain Cauchy estimate gives the bound with 1 in place of e.
- Hence ‖u″‖_{p+2} ≤ e²(p + 1)(p + 2)‖u‖_p.

**The induction.** Put M = sup_D max(|a0|, |b0|), m = inf_D |c0| > 0, and A_n = max(‖a_n‖_{2n}, ‖b_n‖_{2n}), so that
‖c_j‖_{2j} ≤ A_j and A_0 ≤ M. Every term on the right has total weight 2n. Bound each one:
- (n − j)² ≤ n², so the first sum is ≤ 4n² Σ_{j=1}^{n−1} A_j A_{n−j}.
- ‖a_i″‖_{2i+2} ≤ e²(2i + 1)(2i + 2) A_i ≤ 4e²n² A_i, because i ≤ n − 1. So the second sum is ≤ 4e²n² Σ_{i+j=n−1} A_i A_j.
- i·j ≤ n²/4, so the third sum is ≤ n² Σ_{i+j=n; i,j≥1} A_i A_j.
- (2i + 1)(2j + 1) ≤ n² when i + j = n − 1, so the fourth sum is ≤ e² n² Σ_{i+j=n−1} A_i A_j.

With ‖1/c0‖_0 ≤ 1/m, the factor n² cancels, and that is the whole point: the Fuchsian indicial factor 4n² exactly
pays for the two z-derivatives that each step costs. We get

    A_n ≤ (5/(4m)) [ Σ_{i+j=n; i,j≥1} A_i A_j + e² Σ_{i+j=n−1; i,j≥0} A_i A_j ].

**The majorant series.** Let B_0 = M and define B_n (n ≥ 1) by the same inequality with "=". By induction
0 ≤ A_n ≤ B_n. The generating function Y(x) = Σ_{n≥1} B_n xⁿ satisfies

    Y = α Y² + β x (M + Y)²,   α = 5/(4m),   β = 5e²/(4m),

which is the coefficient identity. The root with Y(0) = 0 is
Y = [1 − 2βMx − √((1 − 2βMx)² − 4(α + βx)βM²x)] / (2(α + βx)). Its nearest singularity is the zero of the
discriminant, 1 = 4βMx(1 + αM), at

    x0 = 1/(4βM(1 + αM)) = 4m² / (5e² M (4m + 5M)).

The coefficients B_n are nonnegative, so Pringsheim's theorem puts the singularity of smallest modulus on the
positive axis. The radius of convergence is therefore x0, and B_n ≤ C_ε (x0 − ε)^{−n} for each ε > 0.

**Conclusion.**
- |a_n(z)| ≤ A_n d(z)^{−2n} ≤ C_ε ((x0 − ε) d(z)²)^{−n}. So Σ a_n tⁿ converges for |t| < x0 d(z)², and uniformly on
  |z − z0| ≤ R/2 for |t| < x0R²/4. The same holds for b_n.
- **Uniform on K.** M, m and a common R can be chosen uniformly on the compact K, with R < dist(K, ∂W). So
  τ_K = x0R²/4 works for all of K. The limit is holomorphic in (t, z), and by the recursion it solves the system.
- Uniqueness among solutions analytic in (ρ², z) is the recursion itself (§4).
- Only f0 ≠ 0 was used, never f0 > 0. The hypotheses of Hauser–Ernst and Müller zum Hagen are not imported.

**Status (wording amended 2026-11-24): PROVED HERE, checked by its author and by the numerical control below; NOT yet independently checked.** It is a standard Cauchy–Kovalevskaya majorant in Nagumo norms, with
the indicial factor in place of the time derivative. It supersedes the reliance on the unread 1976
Baouendi–Goulaouic systems theorem, which stays as the supporting reference with our stated reduction.

**Numerical control** (`scripts/_nve_prop2_majorant_control.py` → `prop2_majorant_control.out`; Kerr, spin 0.6,
z0 = 6 in shifted z, recursion to n = 12, 30 digits, peak RSS 22 MB).
- **The recursion reproduces Kerr's exact off-axis Ernst potential** E = 1 − 2/(r − ia cos θ):

  | ρ | \|partial sum − exact\| |
  |---|---|
  | 0.5 | 3e−27 |
  | 1 | 2e−19 |
  | 2 | 1e−11 |
  | 3 | 4e−7 |

  The error grows as ρ² approaches the radius, as truncation should.
- **Must-fail control:** with the j-sum's sign flipped, the error at ρ = 1 is 2e−5, about 10¹⁴ times worse.
- **The radius is not contradicted.**
  - The true radius in t at z0 is (distance to the rod end)² = 17.64.
  - |a_n|^{−1/n} falls from 56 (n = 3) to 28 (n = 12), heading toward it from above.
  - The majorant guarantees x0R² = 0.026, 0.030 and 0.0033 for R = 2, 3 and 4. That is far inside the true radius:
    conservative, as a majorant should be, and never above it.

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
condition, not a consequence of it.** [Source check: Meinel–Neugebauer 1995 (gr-qc/0302114) derive f⁽ˡ⁾ = 1/f⁽ᵘ⁾, their Eq. 35, in §III from
asymptotic flatness alone, and combine it with symmetry in §IV. Ernst–Manko–Ruiz 2006 (gr-qc/0701112), Eqs. 56–58,
use the same continuation of ξ̃. Kordas 1995: abstract only. Details in `T51_GRADING.md`.]
- The condition also depends on where the origin is. Kerr satisfies it in z_c, but in the claim's shifted z,
  e₊(z)·conj e₊(−z) − 1 = −4M²/(z − ia)² ≠ 0 (checked). Kerr is symmetric; the shifted origin is simply not on its
  equatorial plane.
- **Family (ii) with k ≠ 0 is NOT reflection-symmetric, at any spin, about any plane** (exact;
  `scripts/_nve_family2_reflection.py` → `family2_reflection.out`). The test is the EMR multipole criterion in the
  centred coordinate, about a plane z_c = c.
  - Re m_1 = −c forces c = 0.
  - Then the symmetry-violating part of m_3 is −a²(R² − 90)/90 = 7ka²/30 ≠ 0, where R = √(90 − 21k).
  - At k = 30/7 the same follows by continuity in k.
  - Control: k = 0 reproduces Kerr's c0, and every violating part vanishes there.
  Nothing in the proof uses reflection symmetry.

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
- **CORRECTED 2026-11-24 (found by the Bridge's independent reader, layer 4 of the Maciejewski-reply check, and
  confirmed by the Bridge).** The text here used to say: "The (x, y) block is two identical copies of NVE1. ... To
  second order the only rotation-invariant quadratic form in (x, y) is x² + y²", giving the group {diag(g, g)}.
  - **That is wrong.** It considered quadratic forms in position only. In phase space the rotation-invariant quadratic
    forms are x² + y², p_x² + p_y², x p_x + y p_y AND L_z = x p_y − y p_x.
  - L_z does occur. g^{tφ} = f ω/ρ² gives H ⊃ g^{tφ} p_t p_φ = −E (f ω/ρ²) L_z, and ω = ω2 ρ² + O(ρ⁴), so the
    transverse quadratic Hamiltonian contains −E f0 ω2 L_z with f0 ω2 ≠ 0 on the axis.
  - The block is therefore two copies of the ρ-equation rotated into each other, not two identical copies.
- **The corrected argument (the conclusion is unchanged).**
  - **Splitting.** The transverse quadratic Hamiltonian is H2 = H_A + c(τ) L_z, where:
    - H_A is the L_z = 0 part, which gives the ρ-equation in each of x and y;
    - c = −E f0 ω2. Its sign is convention-dependent; on the lower axis f0, ω2 are the lower-axis functions.
  - **Rotation.** L_z Poisson-commutes with every rotation-invariant quadratic form, so {H_A, L_z} = 0 at every τ. The
    fundamental solution is therefore R(Θ(τ))·diag(g(τ), g(τ)), with R the rotation generated by L_z and
    Θ = ∫ c dτ, a frame-dragging angle. Θ is a quadrature, not an algebraic gauge.
  - **Diagonalising.** In the complex variables q± = x ± iy (with conjugate momenta) L_z is diagonal. The block splits
    into two 2 × 2 systems, each the ρ-system tensored with the rank-one equation λ′ = ±i c λ.
  - **Galois group.** Each system's Galois group G± lies in C*·SL₂. Its image in PGL₂ = PSL₂ is the Galois group of
    the associated Riccati equation, because ratios of solutions do not see the scalar factor. That Riccati equation is
    the same as the ρ-equation's.
  - **Conclusion.** If the ρ-equation has Galois group SL₂, each G± maps onto PSL₂. So G±⁰ maps onto PSL₂, a
    connected finite-index image, and G±⁰ is non-abelian.
  - **Scope of the earlier claim.** "The first-order equation sees the twist only through f0⁻" is true of the
    ρ-equation only. The Cartesian block also sees c0⁻ through Θ.
- **This passes to the full VE.** G⁰ of a subquotient of the full VE is a quotient of the full G⁰, and quotients of
  abelian groups are abelian. So a non-abelian G±⁰ (from a non-abelian G1⁰, above) forbids abelian (G_VE)⁰, which Morales–Ramis requires of an
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
- **Proposition 2 (amended 2026-11-24):** a majorant proof written here (MRS_SECTION.md §4b), checked by its author and by a numerical control, NOT yet independently checked.

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
- **(Added 2026-11-25.) The spin-9/10 extra zero is now explained:** c2 vanishes at spin a\* ≈ 0.908, so a third zero
  passes through k = 0 there (`C2_ANALYTIC.md` §5; verified in `C2_OFFICE_CHECK.md`).

**Lemma K (k-analyticity at k = 0; added 2026-11-25, on Sumit's go via the Bridge).**
*Setting.*
- Fix 0 < a < 1 and E with 0 < E² < 1.
- Let C be the circle |z| = R0 and L the lasso path of the circle picture, both based at b = R0 > 0. The ray
  [R0, +∞) carries the normalisation of c0.
- Put S = C ∪ L ∪ [R0, +∞).
*Hypotheses.*
- (H1) every point of S has |z| ≥ ρ for some ρ > a/√3;
- (H2) at k = 0, the four points r± (zeros of P) and p± (zeros of f0² + c0²) do not lie on C ∪ L;
- (H3) a < R0 < min(|r±|, |p±|).
*Conclusion.* There is δ > 0 such that M0(k) and M1(k), the monodromies along C and L, are holomorphic in k for
|k| < δ, with M0(0) = I. Consequently F(k) = tr[M1, M0] − 2 = c2k² + O(k³), with
c2 = tr X² − tr(M1(0) X M1(0)⁻¹ X) and X = M0′(0).

*Proof.*
1. **The twist factorises.** From (c0″)² = 8B(u², k)/(5a⁶(u² + 1)⁶), B(w, k) = 10(3w − 1)² − k(21w² − 18w + 1) and
   (c_K″)² = 16(3w − 1)²/(a⁶(w + 1)⁶), w = z²/a², we get
       c0″(z; k) = c_K″(z)·√(1 − kφ(w)),   φ(w) = (21w² − 18w + 1)/(10(3w − 1)²),
   with the principal root. It equals 1 at k = 0, so the branch agrees with the normalisation, c0″ → c_K″ as
   z → +∞.
2. **φ is bounded on S.** By (H1), |3w − 1| ≥ 3ρ²/a² − 1 > 0 on S. φ(w) → 7/30 as w → ∞, so Φ := sup_S |φ| < ∞.
   For |k| < 1/(2Φ), √(1 − kφ) is holomorphic in k, uniformly on S, and bounded by √(3/2).
3. **c0 and c0′ are holomorphic in k on C ∪ L.** c0′(z) = −∫_z^∞ c0″ and c0(z) = ∫_z^∞ (s − z)c0″ ds, taken along
   [R0, ∞) and then along the loop path inside S. The integrands are holomorphic in k and bounded by a constant
   times |c_K″(s)|·(1 + |s|) = O(|s|⁻³), uniformly in |k| < 1/(2Φ). So the integrals converge uniformly, and they
   are holomorphic in k (Weierstrass).
4. **The NVE coefficient is holomorphic in k on C ∪ L.**
   - q = (3/16)(P′/P)², with P = E² − f0/(f0² + c0²), is holomorphic in (c0, c0′) wherever f0² + c0² ≠ 0 and P ≠ 0.
   - At k = 0 the zeros of f0² + c0² = D/D₊ are p±, and the zeros of P = N/D are r±. By (H2) neither vanishes on
     the compact set C ∪ L.
   - By continuity in k (step 3) they stay nonzero for |k| < δ, with some δ ≤ 1/(2Φ). So q(z; k) is holomorphic in
     k, uniformly on C ∪ L.
5. **Monodromies.** The solution of the linear system Y′ = A(z; k)Y along a fixed compact path, with A holomorphic
   in a parameter uniformly on the path, is holomorphic in the parameter: the Picard iterates are holomorphic and
   converge uniformly. So M0(k) and M1(k) are holomorphic for |k| < δ.
6. **M0(0) = I.** At k = 0 the lower-axis data are Kerr's, f0⁻ = Δ/D (rational). The coefficient's only singular
   points are r± and p±, and by (H3) they lie outside |z| ≤ R0. So the coefficient is holomorphic on the closed
   disc, and the solutions continue single-valuedly around C.
7. **The expansion of F.** M0 = I + kX + k²Y + O(k³), and conjugation by M1(k) is exact. So
   tr[M1, M0] − 2 = k²(tr X² − tr(M1(0)XM1(0)⁻¹X)) + O(k³). □

*The hypotheses hold for every loop used.*
- (H1): every loop and base point is at least 0.744 from the interval |z| ≤ a/√3 (§3, the 2026-11-24 note).
  Every circle-picture path has |z| ≥ R0 − 0.05 ≥ 1.10, while a/√3 ≤ 0.52.
- (H2) and (H3): these are the registered geometry guards. For example, at spin 9/10, R0 = 1.264 and
  min|r±, p±| = 1.850.
*What Lemma K is for.* With c2 ≠ 0 (certified per spin, `C2_ANALYTIC.md` §6b), it gives Statement A of the claim
(v3). δ is not quantified, so neither is the ε of Statement A.

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

## 6. Citations: status (checked at source 2026-11-22; downloaded texts kept locally, not committed)
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
- **For e₋ = 1/e₊ (§5a):**
  - Meinel & Neugebauer, CQG 12 (1995) 2045 = gr-qc/0302114, Eq. 35 (§III): VERIFIED (full text).
  - Ernst, Manko & Ruiz, CQG 23 (2006) 4945 = gr-qc/0701112, Eqs. 50–58: VERIFIED (full text).
  - Kordas, CQG 12 (1995) 2037: abstract only.
  - FHP's statement that ξ̃ is analytic at the origin: NOT confirmed at source (abstract only). The set-up is
    confirmed in EMR and in Pachón–Sanabria-Gómez gr-qc/0603081.
- **Proposition 2, checked at source 2026-11-22.** Downloaded texts kept locally, not committed.
  - **Baouendi & Goulaouic, J. Differential Equations 22 (1976) 268–291:**
    - The 1976 text was NOT READ (paywalled).
    - The 1974 announcements were VERIFIED AT SOURCE (Numdam: Sém. Goulaouic–Lions–Schwartz 1974–75, exp. 3–4;
      Publ. Math. Rennes 1974):
      - Thm 1: the first-order Fuchsian system, with non-resonance det(Λ(0) − k) ≠ 0 for k ∈ ℕ;
      - Thm 4: the scalar m-th-order case;
      - Ex. (31): the axisymmetric problem with axis data, unique analytic solution in (x, |y|²).
    - Bacani–Tahara (Publ. RIMS 48 (2012)) describe the 1976 paper's content SECONDHAND.
    - **No paper applying it to the Ernst equation was found.**
  - **Hauser & Ernst, J. Math. Phys. 22 (1981) 1051, "Proof of a Geroch conjecture": ABSTRACT ONLY.**
    - The set of Kinnersley–Chitre transformations between two spacetimes is uniquely determined by their axis values
      of E. This is global, needs C³ and a timelike Killing vector on the axis (f > 0), and gives no local
      convergence.
    - Hauser & Ernst, gr-qc/0002049 p. 2 (VERIFIED): C³ solutions of the axis-accessible Ernst equation are
      automatically analytic (no proof given there).
  - **Sibgatullin (book 1984/1991): NOT READ.** Manko–Sibgatullin, CQG 10 (1993) 1383: abstract only.
    Ernst–Manko–Ruiz, arXiv:1006.5118 (VERIFIED): axis data are continued holomorphically to ξ = z + iρσ. It is a
    construction, with no uniqueness or convergence theorem. Not a citation for Prop. 2.
  - **Bäckdahl, CQG 24 (2007) 2205 = gr-qc/0612043: VERIFIED.** Complexified Weyl coordinates; recursion (Lemma 5),
    majorant convergence (Lemma 7), uniqueness (Thm 8). Done at infinity, with characteristic data; it also says that
    convergence of the FHP axis-data method is "still an open question". The closest rigorous model for our step.
  - **Müller zum Hagen, Proc. Camb. Phil. Soc. 68 (1970) 199: ABSTRACT ONLY.** Analyticity of a given stationary C³
    vacuum metric. It gives neither existence nor uniqueness from data, and assumes a timelike Killing vector.
  - **Chruściel, Greuel, Meinel & Szybka, gr-qc/0603041: VERIFIED.** Off-axis analyticity only; ρ = 0 is set aside
    explicitly.
  - **Caution:** citing Hauser–Ernst or Müller zum Hagen imports f > 0. On the Fuchsian route only f0 ≠ 0 is needed
    (it is the non-resonance condition), which is what W assumes.
- Maciejewski–Przybylska–Stachowiak 2013: body read in full by the Bridge and Neon T47 (relayed); used only for ZV
  δ = 2 (first-order NVE along an equatorial radial geodesic).

- **Prior art, read at source 2026-11-22; neither covers nor contradicts our results, and both complement them.**
  - **Ramond, arXiv:2607.27129 (29 Jul 2026).**
    - The background is exact Kerr and is NOT deformed. What carries the deformation is the orbiting body, through
      a tidally induced quadrupole (MPTD/Dixon–Harte equations), to first order in the tidal coupling ε. So the
      motion is non-geodesic, with generic L_z.
    - The proof is perturbative (Eqs. 5.1–5.15): it shows that no first-order deformation of Carter's constant
      exists, polynomial in the momenta up to rank 4, global in (r, θ), when a ≠ 0. The numerical chaos is labelled
      illustrative.
    - Its Sec. VII.D names Morales–Ramis / Melnikov methods as the open next step.
    - It has no exact vacuum deformation, no axis orbit, and no Galois or Kovacic step.
  - **Destounis & Kokkotas, arXiv:2305.18522, GRG 55, 123 (2023).**
    - The spacetime is Hartle–Thorne truncated at O(Ω²): a perturbative metric with an intrinsic quadrupole
      deviation δq.
    - The orbits are generic, with L_z ≠ 0.
    - The evidence is purely numerical: Poincaré maps, plus rotation-curve plateaus of the 2/3 island. Nothing is
      formally excluded.
    - HT has no exact axis function f0, so our rational-class result does not even apply to it.
  - **Neither paper cites any differential-Galois work on Kerr-like spacetimes.** Maciejewski–Przybylska–Stachowiak
    2013 remains the closest methodological precedent.
