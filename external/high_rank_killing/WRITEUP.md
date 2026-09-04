# A Lorentzian vacuum pp-wave with an irreducible rank-3 Killing tensor — and what "irreducible" buys

*Working note, 2026-09-05. Everything below is reproduced by the scripts in `scripts/` with logs in
`results/`; the experiment records are `report.md` EXP-002 and EXP-003.*

## 0. Summary

Cariglia and Galajinsky (2015) constructed Ricci-flat metrics of signature **(2,2)** carrying
irreducible rank-3 Killing tensors and stated that no *Lorentzian* vacuum spacetime with a
Killing tensor of rank ≥ 3 was known; Fordy and Galajinsky (2019) repeated the statement and
called the "empirical barrier of rank 2" puzzling. Their construction is a Bargmann/Eisenhart lift
of Drach's two-dimensional systems on a `(1,1)` base, where Ricci-flatness is `U = f(x) + g(y)`.
Putting `x = z`, `y = z̄` turns that base into the Euclidean plane and `U` into a harmonic function,
so each of their (2,2) metrics is a complex form of a Lorentzian vacuum pp-wave. For their second
Drach system the real form is the σ = 0 member of the 1965 Smorodinsky–Winternitz potential V⁽⁴⁾.

**Result (4D, signature (1,3), Ricci-flat):**

    ds² = −(4aξ/ρ²) dt² + 2 dt ds + 8ρ² (dξ² + dη²),          ρ² = ξ² + η²,  a ≠ 0,

carries the rank-3 Killing tensor

    F = (η p_ξ − ξ p_η)(p_ξ² + p_η²)/(32ρ²) + (a p_s²/ρ²)[ξη p_ξ + ½(η² − ξ²) p_η],

which is **irreducible in the polynomial sense** — not a sum of symmetrized products of
lower-rank Killing tensors; proved without any ansatz — and **functionally dependent** on the
quadratic integrals: `F = −4{Q1,Q2}` and `F² = 4[(H − p_t p_s)(Q1² + Q2²) − a² Q1 p_s⁴]`.

Both statements travel together. Under the definition the literature uses when it says no such
vacuum spacetime is known, this closes that statement; under the functional definition the tensor
adds no dynamical information. **The same is true of the published (2,2) examples**: CG's own cubic
is `−½{Q_a, Q_b}` in their own variables, with `I² = −H Q_a Q_b − β² Q_a − α² Q_b`. So the new
object sits on exactly the footing of the ones already called irreducible; its new content is the
signature.

A 5D Lorentzian vacuum companion exists (§6), obtained by oxidising the coupling `a` into a
gyratonic term; it has the same cubic, three Killing vectors, and the same two verdicts. CG's
rank-4 metrics do **not** continue to Lorentzian signature (§6, an invariant obstruction), so
rank 4 in vacuum is not reached here.

Prior-art status of the object itself (§7): the ingredients are all in print — the general lift
with its vacuum condition, the SW-IV potential and its Riemannian Eisenhart lift, bracket cubics
treated as Killing tensors — but neither the σ = 0 vacuum member nor its rank-3 tensor was found
anywhere.

## 1. Definitions and conventions

A rank-`r` Killing tensor `K^{a₁…a_r}` is equivalent to `F = K^{a₁…a_r} p_{a₁}⋯p_{a_r}` with
`{H, F} = 0`, `H = ½ g^{ab} p_a p_b`, `{A,B} = Σ_a (∂_{x^a}A ∂_{p_a}B − ∂_{p_a}A ∂_{x^a}B)`.

*Reducible (polynomial sense)*: a linear combination of symmetrized products of lower-rank Killing
tensors (Killing vectors and `g^{ab}` included). This is the sense of GHKW 2011, CG 2015, GOKK 2025.
*Functional sense*: `F` is independent iff the Jacobian of `(p_t, p_s, H, Q1, Q2, F)` on phase
space has full rank 6. A Schouten–Nijenhuis bracket of two rank-2 tensors is typically irreducible
in the first sense and dependent in the second. Signature `(p,q)` has `p` negative eigenvalues.

Eisenhart lift of a natural system with potential `V` on flat `E²`:
`dτ² = −2V dt² + 2 dt ds + dx_i dx_i`, with `R_tt = ΔV` the only Ricci component (GHKW eq. 55).
So the lift is vacuum iff `V` is harmonic. A polynomial integral of degree `r` lifts to a rank-`r`
Killing tensor (potential-type terms acquire `p_s²`).

## 2. The 4D object

Coordinates `(t, ξ, η, s)`. `w = ξ + iη`, `z = X + iY = w²`, so `(ξ,η)` are parabolic coordinates
on the transverse plane and `dX² + dY² = 4ρ² (dξ² + dη²)`.

    ds² = −2U dt² + 2 dt ds + 8ρ² (dξ² + dη²),      U = 2aξ/ρ² = 2a Re(z^{−1/2}) = √2 a √(r+X)/r
    H   = p_t p_s + 2aξ p_s²/ρ² + (p_ξ² + p_η²)/(16ρ²)

`a → −a` is `ξ → −ξ`; `|a|` is a gauge (`t → μt, s → s/μ`), so `a = 1` is general. The metric is
smooth on `(w-plane ∖ {0}) × R²`, which double-covers the punctured `(X,Y)` plane; it is singular
at `w = 0` and not geodesically complete (as CG's). Riemann has 16 nonzero components; all scalar
invariants vanish (pp-wave).

Killing vectors: `∂_t, ∂_s` and no others (§3). Rank-2 Killing tensors (the two parabolic
separation constants; `V⁽⁴⁾` separates in two parabolic systems rotated by 90°):

    Q1 = p_ξ²/16 + 2aξ p_s² − ξ²(H − p_t p_s)
    Q2 = (p_ξ − p_η)²/32 + a(ξ − η) p_s² − ½(ξ − η)²(H − p_t p_s)

Rank 3: `F = −4{Q1, Q2}` as above. Nonzero contravariant components (index order `t, ξ, η, s`):

    K^{ξξξ} = η/(32ρ²)     K^{ηηη} = −ξ/(32ρ²)     K^{ξξη} = −ξ/(96ρ²)     K^{ξηη} = η/(96ρ²)
    K^{ssξ} = aξη/(3ρ²)    K^{ssη} = a(η² − ξ²)/(6ρ²)

In Cartesian terms the pure part is `−¼ L (p_X² + p_Y²)`, `L = X p_Y − Y p_X`.

## 3. The three checks

| check | route(s) | result |
|---|---|---|
| Ricci-flat | SymPy, exact, `a` symbolic | `R_ab ≡ 0` |
| signature | `(t,s)` block `det = −1`; transverse `8ρ² I` | **(1,3)** for `ρ ≠ 0` |
| `{H,F} = 0` | exact bracket, `a` symbolic; RK4 geodesics with a known-fail control | exact; drift ≤ 2·10⁻¹², known-fail drifts by 6–10⁴ |
| `dim K1 = 2` | 1-jet count: `L_ξR = 0`, `L_ξ∇R = 0` at two generic points, rank 8 of 10 | ≤ 2, and `∂_t, ∂_s` are two |
| polynomial irreducibility | every element of `K1 ⊙ K2` carries `p_t` or `p_s`; pure part of `F` is `(ηp_ξ − ξp_η)(p_ξ²+p_η²)/(32ρ²) ≠ 0` | **irreducible**, no ansatz |
| count | 10 reducible products + `F` (rank 11, exact); sibling's two-prime sampled nullspace on the same ansatz: 11 (its CG (2,2) control returns its published 2/6/11) | `dim K3 = 11` within the ansatz `poly_{≤6}(ξ,η)/ρ²`: exactly one irreducible direction |
| functional | Jacobian ranks at random rational points | `rank(p_t,p_s,H,Q1,Q2) = 5 = rank(…,F)` → **dependent**; but `rank(p_t,p_s,H,Q1,F) = 5`: independent of the set *without* `Q2` (CG's footnote-9 framing) |
| relation | fit then exact identity, `a` symbolic | `F² = 4[(H − p_t p_s)(Q1² + Q2²) − a² Q1 p_s⁴]` |
| tower | `{Q1,F} = −(H − p_t p_s)Q2`, `{Q2,F} = (H − p_t p_s)Q1 − ½a²p_s⁴`, both in `K2⊙K2 + K1⊙F` (rank 22, unchanged, two primes) | closes at rank 3: no rank-4 from brackets |

The polynomial-irreducibility proof uses only `dim K1 = 2` (proved) and the nonzero pure part;
the count "exactly one" is ansatz-scoped; "at least one" is not.

## 4. The two senses, spelled out

*Polynomial.* Reducible rank-3 tensors are `Σ ξ_i ⊙ K_i` with `ξ_i ∈ K1 = span{p_t, p_s}`, so every
one has zero `(p_ξ,p_η)`-cubic part. `F`'s is nonzero. Hence `F` is not reducible, whatever `K2`
is (t,s-dependent members included).

*Functional.* On the 6-dimensional space of `(t,s)`-independent functions of phase space,
`(p_t,p_s,H,Q1,Q2)` are five independent functions whose common level sets are the orbits, so any
further integral is a function of them; the explicit relation is the one above. Bracketing it
gives the closure formulas, verified pointwise for two values of `a`.

## 5. Where it comes from, and the (2,2) computation

CG (arXiv:1503.02162) eq. 20:

    H = p_x p_y + α/√x + β/√y
    I = x p_x² p_y − y p_x p_y² + (βx/√y) p_x − (αy/√x) p_y                       (their cubic)

Their footnote 9 gives an extra quadratic, garbled in the PDF; it is (verified `{H,Q_a} = 0`):

    Q_a = x p_x p_y − y p_y² + βx/√y − α√x
    Q_b = y p_x p_y − x p_x² + αy/√x − β√y        (image of Q_a under (x,α)↔(y,β), a symmetry of H)

Then, in their variables, explicitly:

    {Q_a, Q_b} = 2αy p_y/√x − 2βx p_x/√y − 2x p_x² p_y + 2y p_x p_y²  =  −2 I
    rank J(H, Q_a, I) = 3   (their footnote: "functionally independent" — true)
    rank J(H, Q_a, Q_b, I) = 3   (maximum for 2 dof: I depends on H, Q_a, Q_b)
    I² = −H Q_a Q_b − β² Q_a − α² Q_b            (identity, checked symbolically)

So CG's rank-3 tensor is the bracket of two quadratic ones and is functionally dependent, exactly
like the Lorentzian object; the sibling repository's exact count on CG's 4D metric
(rank-2 space 6 = `p_t², p_t p_s, p_s², H, Q_a, Q_b`; rank-3 space 11 = 10 + 1) says the same.

The continuation: `x = w²`, `y = w̄²` (so `√x = w`), `p_x = (p_ξ − ip_η)/(4w)`, `p_y = conj`,
`α = β = a`. `2 dx dy → 8ρ²(dξ² + dη²)`, `U → 2aξ/ρ²`. The transported cubic is conserved; its real
part vanishes identically and its imaginary part is `F`.

## 6. Higher dimension: what continues and what does not

**CG's rank-4 metrics do not.** Their eq. 26 (5D) and eq. 30 (6D) descend from Drach's *first*
system, `U = αy + γ/√x − (αx)²/2`, asymmetric in `x ↔ y` (`U_yy = 0 ≠ U_xx`) with the cross term
`2αx dt dw`; under `x = z, y = z̄` none of it is real. In 4D the obstruction is invariant: CG state
that metric is anti-self-dual, and a non-flat ASD (2,2) metric has no Lorentzian real form
(Lorentzian signature forces `W⁻ = conj(W⁺)`, so `W⁻ = 0` means `W = 0`, and Ricci-flat + `W = 0`
is flat). Their symmetric-system oxidations (eq. 33, 35) fail differently: under `w = conj(u)`,
`dw² + du² = 2(dχ² − dψ²)`, adding a (1,1) block.

**A 5D vacuum member exists** (`scripts/exp003_5d_gyraton.py`): oxidise `a` into a momentum `p_v`
through a gyratonic term and re-solve the field equations. Coordinates `(t, ξ, η, s, v)`:

    ds² = −2U dt² + 2 dt ds + 2A dt dv + dv² + 8ρ² (dξ² + dη²)
    A = 2κξ/ρ²,      U = 2aξ/ρ² + κ²(η² − 3ξ²)/(2ρ⁴)

`R_ab = 0` fixes the coefficient of `A²` in `U` to `−¼` (exact, `a, κ` symbolic); the harmonic
admixture `−(κ²/4)(z⁻¹ + z̄⁻¹)` is the unique one for which the reduced 2D system is again SW-IV,
now with a Kepler term: `ρ² V_eff = κ²p_s²/2 + 2p_s(a p_s − κ p_v) ξ`. Signature **(1,4)**.
Then

    Q1 = p_ξ²/16 + κ²p_s²/2 + 2p_s(a p_s − κp_v) ξ − ξ²(H − p_t p_s − ½p_v²)
    Q2 = (p_ξ − p_η)²/32 + κ²p_s²/2 + p_s(a p_s − κp_v)(ξ − η) − ½(ξ − η)²(H − p_t p_s − ½p_v²)
    F  = −4{Q1,Q2}
       = (ηp_ξ − ξp_η)(p_ξ²+p_η²)/(32ρ²) + (p_s(a p_s − κp_v)/ρ²)[ξη p_ξ + ½(η²−ξ²) p_η] + (κ²p_s²/(4ρ²))(η p_ξ − ξ p_η)

with `{H,Q1} = {H,Q2} = {H,F} = 0` exact; `F|_{κ=0}` is the 4D tensor. Killing vectors: exactly
`∂_t, ∂_s, ∂_v` (jet count, 15 − 12 = 3 at two points); pure part nonzero → polynomially
irreducible. Functional: `rank(p_t,p_s,p_v,H,Q1,Q2) = 6 = rank(…,F)` → dependent. Counts
(`a = κ = 1`): exhibited `K1 = 3`, `K2 = 9`, `K1⊙K2 = 19`, `+F = 20`; the sibling's sampled
nullspace (5D, ansatz `poly_{≤8}/ρ⁴`) returns `3`, `9`, `20` for ranks 1, 2, 3 — the squeeze closes: exactly one irreducible rank-3
direction in that ansatz, and it is `F`.

Reading: `ds₅² = ds₄² + (dv + A dt)²` with `ds₄²` the pp-wave of profile `2U + A² = (4aξ + κ²)/ρ²`,
i.e. the 5D vacuum is the Kaluza–Klein lift of a 4D Einstein–Maxwell pp-wave whose null Maxwell
field `dA ∧ dt` sources exactly the Kepler term of SW-IV (standard KK reduction; not separately
re-verified).

## 7. Prior art on the object

Searched for the metric, not the problem: Eisenhart/Bargmann lifts of Smorodinsky–Winternitz
potentials, pp-waves with `Re z^{−1/2}` / `√(r+x)/r` profiles, higher-rank Killing tensors on
pp-waves, Stäckel/Shapovalov wave spacetimes, INSPIRE full-text, forward citations of the six
nearest papers (through Aug 2026).

- GHKW 2011 give the general lift `g = dx² + dy² − 2V dt² + 2 dt ds` with `R_tt = ΔV` and say
  "many superintegrable systems … give rise to higher-rank Killing tensors", but work out only the
  Post–Winternitz potential (non-harmonic).
- Cariñena–Herranz–Rañada 2017 lift all four SW families, SW-IV included, in the *Riemannian*
  Eisenhart lift (3D, `g = diag(1,1,V)`), and state they "restrict [the] study to Killing vectors
  and p = 2 Killing tensors", naming p > 2 as open. No field equations in that setting.
- Kubů–Tempesta 2025/26 (Stäckel lifts) say the SW-IV lift can be done "analogously" and do not do
  it; their Lorentzian example is a Platonic wave with an inverse-square potential, "not an
  Einstein manifold", field equations "left for future work".
- Fordy–Galajinsky 2019 compute a bracket cubic `F3 = {F1,F2}` with its relation
  `F3² + 8(H+2p_vp_t)F1F2 + 4F2³ + 32m p_v²(H+2p_vp_t)² = 0` on the lift of a Darboux–Koenigs
  metric — the same phenomenon, on a non-vacuum metric — and in the same paper state that no
  vacuum solution with a higher-rank Killing tensor is known.
- Keane–Tupper 2010 solve the rank-2 Killing equation on pp-waves; Kruglikov–Steneker 2022 show
  that on generic *conformally flat* pp-waves all degree-3/4 Killing tensors are reducible (a
  different family: ours is type N, not conformally flat).

Nothing found containing the σ = 0 vacuum member or its rank-3 tensor. A negative sweep is never
complete.

## 8. Scope, and what is not claimed

- Rank ≥ 4 in Lorentzian vacuum is not reached: the bracket tower closes at rank 3 (proved for
  the 4D metric), and CG's rank-4 metrics have no Lorentzian form.
- "Exactly one irreducible direction" is a statement within the stated polynomial ansatz;
  "at least one" is unconditional.
- The generalisation — any vacuum pp-wave whose harmonic profile is multiseparable with
  non-commuting separation tensors and no extra Killing vectors carries a polynomially
  irreducible `{Q_a,Q_b}` — is stated as an expectation, not computed.
- The spacetimes are singular on the null line `w = 0` and geodesically incomplete, as CG's are.

## 9. Reproduction

`scripts/exp002_ppwave.py` (4D checks 1–3), `exp002_relation_check.py`, `exp002_sibling_prover.py`
(sibling prover by import, `ckpt=None`), `exp002_geodesic_check.py`, `exp002_cg22_bracket.py`,
`exp002_cg22_relation.py`, `exp002_jac_noQ2.py`, `exp002_tower.py`, `exp003_5d_gyraton.py`,
`exp003_5d_squeeze.py`; logs in `results/`. Run with `../conjecture_machine/.venv/bin/python`
(SymPy 1.14). Papers read in full are in `prior_art/`.

## References

- M. Cariglia, A. Galajinsky, *Ricci-flat spacetimes admitting higher rank Killing tensors*, Phys. Lett. B 744 (2015) 320, arXiv:1503.02162.
- A. P. Fordy, A. Galajinsky, *Eisenhart lift of 2-dimensional mechanics*, Eur. Phys. J. C 79 (2019) 301, arXiv:1901.03699.
- G. W. Gibbons, T. Houri, D. Kubizňák, C. M. Warnick, *Some spacetimes with higher rank Killing–Stäckel tensors*, Phys. Lett. B 700 (2011) 68, arXiv:1103.5366.
- G. W. Gibbons, C. Rugina, J. Math. Phys. 52 (2011) 122901, arXiv:1107.5987.
- A. Galajinsky, *Higher rank Killing tensors and Calogero model*, Phys. Rev. D 85 (2012) 085002, arXiv:1201.3085.
- J. Friš, V. Mandrosov, Ya. A. Smorodinsky, M. Uhlíř, P. Winternitz, Phys. Lett. 16 (1965) 354.
- I. Popper, S. Post, P. Winternitz, J. Math. Phys. 53 (2012) 062105, arXiv:1204.0700.
- J. F. Cariñena, F. J. Herranz, M. F. Rañada, *Superintegrable systems on 3-dimensional curved spaces: Eisenhart formalism and separability*, arXiv:1701.05783.
- O. Kubů, P. Tempesta, *Stäckel and Eisenhart lifts, Haantjes geometry and Gravitation*, arXiv:2509.19950 (v3, 2026).
- A. J. Keane, B. O. J. Tupper, Class. Quantum Grav. 27 (2010) 245011, arXiv:1011.6401.
- B. Kruglikov, W. Steneker, Class. Quantum Grav. 39 (2022) 225005, arXiv:2207.03474.
- F. Gray, G. Odak, P. Krtouš, D. Kubizňák, JHEP 07 (2025) 098, arXiv:2504.18287.
- Sibling repository `../conjecture_machine`: `_kt_search.solve_kt_modp` (the sampled modular nullspace), its CG controls (JOURNAL 2026-08-21).
