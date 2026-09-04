# Report

*Rule IX: every experiment gets an entry. If it is not here, it did not happen.*

Required fields per entry:

    ## EXP-NNN  <short title>
    **Goal**            what problem is this solving
    **Hypothesis**      why should this approach work
    **Method**          the mathematics, with notation defined before use (M2)
    **Implementation**  files and lines changed
    **Results**         table: method, instance, metric, delta
    **Analysis**        why it worked or did not; what it reveals
    **Grade**           verified / partially verified / unverified
    **Next steps**      what to try based on this

---

## EXP-001  Prior-art sweep (the M1 gate) — 2026-09-04

**Goal.** Before building anything: (1) which irreducible Killing tensors of rank ≥ 3 actually
exist — dimension, signature, field equations, rank, authors, identifiers; (2) whether rank ≥ 5
is already covered by an existence *or* a non-existence result (the outcome-F check); (3) whether
any rank bound exists in 4D; (4) which claims in `TASK.md` are wrong.

**Hypothesis.** `TASK.md` (written from recollection) expected: rank 3/4 exist by construction;
rank ≥ 5 unexplored; Cariglia–Galajinsky possibly 5D. Prior experience in this family: expect at
least two claims to fall.

**Method.** Every primary claim below was checked against the arXiv abstract page fetched today;
ten load-bearing papers were read in full (`pdftotext`; PDFs and extractions kept in
`prior_art/`). Forward-citation lists (Semantic Scholar API) were pulled for the
three construction papers (Cariglia–Galajinsky 2015, Gibbons–Houri–Kubizňák–Warnick 2011,
Galajinsky 2012) and for Gibbons–Rugina 2011, Gray–Odak–Krtouš–Kubizňák 2025 and Vollmer 2017,
to catch 2022–2026 work. Targeted searches covered the 2D-Riemannian line (Kiyohara / Valent /
Bolsinov–Kozlov–Fomenko), the dimension-bound line (Delong–Takeuchi–Thompson), Kerr, and
pp-waves. The sibling `../conjecture_machine` record (JOURNAL 2026-08-16/21, RESULTS §124/§127,
DECISIONS D39–D42) was read for what it had already established; nothing was copied.
Quotations below are verbatim from the fetched texts.

**Notation (M2).** A rank-*r* Killing tensor `K^{a1…ar}` ↔ `F = K^{a1…ar} p_{a1}…p_{ar}` with
`{H,F} = 0`, `H = ½ g^{ab} p_a p_b`. **Reducible** = linear combination of symmetrized products
of lower-rank Killing tensors (Killing vectors and `g^{ab}` included); **irreducible** otherwise.
This is the *polynomial* notion used by GHKW 2011, CG 2015, GOKK 2025 and by check 3 of
`TASK.md`. The integrable-systems literature uses a different notion — *functional* independence
— and the two disagree in exactly the case that matters below. Signature `(p,q)` = `p` negative
eigenvalues; Lorentzian = `(1,n−1)`; `(2,q)` = ultrahyperbolic. **Eisenhart lift** of a natural
system with `n` degrees of freedom and potential `V(x)`: the `(n+2)`-dimensional metric
`dτ² = −2V dt² + 2 dt ds + dx_i dx_i`, Lorentzian; its Ricci tensor has the single component
`R_tt = ΔV` (Galajinsky 2012 eq. 24; GHKW 2011 eq. 55), so **Ricci-flat ⇔ V harmonic on the
base**. A polynomial integral of degree `r` of the base system lifts to a rank-`r` Killing tensor.

---

### Results — the map of what exists

| # | class | rank | dim | signature | field eqs | source | grade |
|---|---|---|---|---|---|---|---|
| A1 | Eisenhart lift of Goryachev–Chaplygin top | 3 | 4 | Lorentzian | **not** Ricci-flat ("nor does the Ricci scalar vanish") | GHKW 2011 §3.1 | verified (full text) |
| A2 | Eisenhart lift of Kovalevskaya top | 4 | 4 (and 5) | Lorentzian | "not Ricci flat" | GHKW 2011 §3.2 | verified |
| A3 | pp-wave `g = 2ds dt − (2αy/x^{2/3})dt² + dx² + dy²` (Post–Winternitz lift) | 3 **and** 4 | 4 | Lorentzian | `R_tt = ΔV ≠ 0` | GHKW 2011 §4.1, eqs 59–66 | verified |
| A4 | GC / Kovalevskaya gyrostats; Brdička–Eardley–Nappi–Witten pp-wave | 3, 4 | 4, 5 | Lorentzian | not Ricci-flat; BENW is Einstein–Maxwell | Gibbons–Rugina 2011 | verified |
| A5 | Eisenhart lift of the `n`-body Calogero model | **3 ≤ r ≤ n**, rank-5 components written out (eq. 30) | `n+2` (rank 5 needs `n ≥ 5`, i.e. **D ≥ 7**) | Lorentzian | not Ricci-flat (Calogero potential "does not belong to this special class") | Galajinsky 2012 | verified that the object is published; irreducibility is asserted "by construction", not proved there |
| A6 | Generalized Lense–Thirring, "tower" by nested Schouten–Nijenhuis brackets | 2, 3, 4, …, "arbitrary rank k+1" | any `d`; brackets non-vanishing for `d > 6` | Lorentzian | **off-shell** ("no field equations imposed") | Gray et al. 2022; GOKK 2025 | verified as claims; irreducibility of rank ≥ 3 members is only "hinted" in the source |
| A7 | Prescribed-symmetry deformation preserving `T = ∂_t(∂_x² + ∂_y²)` | 3 | 4 | Lorentzian | off-shell | He–Li 2024 | verified |
| A8 | Bohlin-variant lift of 4-body Calogero | 3, 4 (up to `d` in `d+2`) | 6 | Lorentzian, conformally flat | not Einstein (its Λ-vacuum example is a patch of AdS, where every Killing tensor is reducible) | Galajinsky 2026 | verified |
| A9 | 2D Riemannian metrics on S² with an irreducible integral of **every** degree `k`; Valent's surfaces of revolution, any integer degree | any `k` | 2 | Riemannian | — | Kiyohara 2001; irreducibility at every `k` proved by Matveev 2025; Valent 2017 | verified (abstracts); the 4D Lorentzian lift (product with `R^{1,1}`) is *expected* to stay irreducible — **unverified** |
| B1 | Eisenhart lift of Drach's 2D systems on a `(1,1)` base | 3 | 4, 5, 6 | **(2,2), (2,3), (2,4)** | **Ricci-flat**; one 4D metric anti-self-dual | CG 2015 | verified; sibling's exact prover finds exactly one irreducible rank-3 on the 4D metric |
| B2 | same, oxidised (CG eq. 26 = the sibling's `_kt_cg5d.py`) | 4 | 5, 6 | **(2,3), (2,4)** | Ricci-flat | CG 2015 §4 | verified; sibling finds exactly one irreducible rank-4 on the 5D metric |
| B3 | note reiterating B1/B2 | 3, 4 | ≥ 4 | ultrahyperbolic | Ricci-flat | Galajinsky 2017 (PPNL, no arXiv) | abstract only |
| **C** | **Ricci-flat or Einstein, Lorentzian, any dimension, rank ≥ 3** | — | — | — | — | **nothing found** | see quotes |

**C, in the sources' own words.** CG 2015: *"It is important to stress, however, that none of the
Lorentzian spacetimes studied in [5],[7]–[12] solves the vacuum Einstein equations."* … *"Close
inspection of two-dimensional integrable models possessing a cubic (or higher) integral of motion
[13] shows that none of them is described by a harmonic function. Thus the construction of
four-dimensional spacetimes of signature (1,3) which admit higher rank Killing tensors seems to be
problematic within the Eisenhart approach."* Their conclusion names the open problem: *"whether an
integrable system with a cubic (or higher) integral of motion can be constructed which is governed
by a harmonic potential."* Fordy–Galajinsky 2019: *"no solution to the vacuum Einstein equations
admitting higher rank Killing tensors is presently known. This empirical barrier of rank–2 seems
rather puzzling."* Nothing in the forward citations of any of these papers through Aug 2026
changes that. **Grade: verified as the state of the literature I could reach; a negative sweep is
never complete.**

### Results — non-existence and bounds

| result | scope | source | grade |
|---|---|---|---|
| ZV δ=2: no nontrivial polynomial integral of degree < 7 | one metric, one δ | Kruglikov–Matveev 2012 | verified |
| Tomimatsu–Sato ≤ 7, C-metric ≤ 9, Zipoy–Voorhees ≤ 11 | three vacuum metrics | Vollmer 2017 | verified — `TASK.md`'s "Vollmer 2016, one family, valence 11" is right on ZV, incomplete on the rest |
| slowly-rotating dCS: none through rank 6; sGB: none through rank 2 | perturbative metrics | Owen–Yunes–Witek 2021 | verified (abstract) |
| Wils metric: none up to degree 6; **generic** conformally-flat pp-wave: all degree-3 and -4 Killing tensors reducible | pp-wave subfamily | Kruglikov–Steneker 2022 (Thm 15, Cor 14) | verified |
| Weyl class (static axisymmetric, 2 Killing vectors): no irreducible **rank-2** | vacuum/electrovac | Kokkinos 2026 | verified (post-cutoff paper, abstract fetched) |
| **generic** real-analytic metric: no nontrivial polynomial (or analytic) integral, any degree | Baire-generic | Kruglikov–Matveev 2016 | verified |
| Kerr, rank ≥ 3 | — | **no theorem found**; sibling's exact den¹ runs give rank 3 = 8, rank 4 = 14, both fully reducible | sibling's computation; not a theorem |
| dimension of rank-`r` Killing tensors in dim `n` ≤ `(1/n)·C(n+r−1,r)·C(n+r,r+1)`; equality on constant curvature, where **all** Killing tensors are polynomials in Killing vectors | any metric | Delong–Takeuchi–Thompson (Thompson 1986); reducibility statement as quoted by Fordy–Galajinsky 2019 and McLenaghan–Milson–Smirnov 2004 | verified via secondary sources; Thompson's own text is paywalled (403) |
| Killing equation is of finite type at every rank ⇒ each rank is finite-dimensional | any metric | Kruglikov–Steneker 2022 Thm 6; Houri–Tomoda–Yasui 2018 | verified |
| **rank bound in 4D** | — | **none exists.** Item A9 gives 4D Lorentzian metrics with irreducible Killing tensors of every rank once field equations are dropped; so any 4D rank bound must come from field equations, and none is known | verified (as a consequence of the above) |

For `n = 4` the DTT bound reads 10, 50, 175, 490, 1176, 2520 at ranks 1–6.

### The outcome-F check, answered

- **"Rank ≥ 5, broader class than vacuum 4D, class stated" (outcome B) is already in the
  literature**: Galajinsky 2012, Lorentzian, `D = n+2 ≥ 7`, no field equations, explicit rank-5
  components. It is F, not B. (His irreducibility argument is "by construction" — the leading
  momentum symbol is the power sum `Σ p_i^r`, algebraically independent of the Killing-vector
  symbols — plausible, and cheap to check exactly; not done here.)
- 4D Lorentzian, no field equations, rank ≥ 5: no explicit published example found, but it is a
  corollary of A9 (or of the TTW-type superintegrable systems, whose extra integral has degree
  growing with the parameter `k`). Writing one down would be a control, not a result.
- Ricci-flat, rank ≥ 5, **any** signature: nothing. CG 2015 propose it as a direction
  ("systematically extend Drach's work … quartic or higher integrals").
- Ricci-flat **Lorentzian**, rank ≥ 3, any dimension: nothing. **This is the actual gap**, and the
  literature states it as open (CG 2015, Fordy–Galajinsky 2019).

### Corrections to `TASK.md` (item 4)

1. **"Above rank 4 the landscape is unexplored"** — *wrong without field equations* (Galajinsky
   2012; Lense–Thirring towers to arbitrary rank). *Right for Ricci-flat*, in every signature. And
   the Lorentzian-vacuum frontier is not rank 5 — it is **rank 3**.
2. **"CG 1503.02162 … may be 5D"** — CG's rank-3 metrics are in **4, 5 and 6** dimensions and the
   rank-4 ones in **5 and 6**; every one of them is **ultrahyperbolic `(2,q)`**, none Lorentzian.
   The sibling's control (`_kt_cg5d.py`) is their eq. 26: 5D, signature (2,3). So "the 4D question
   may be open at rank 3" is true in a sharper form: *the Lorentzian vacuum question is open at
   rank 3 in every dimension.*
3. **"Vollmer 2016 … one specific metric family, valence 11"** — J. Geom. Phys. 115 (2017) 28;
   three metrics: TS ≤ 7, C-metric ≤ 9, ZV ≤ 11.
4. **"SymPy decides in seconds"** — not at the ranks in question. The sibling's 4D rank-4 den¹ run
   took 66 min; Kruglikov–Steneker's quartic prolongation matrix was 495 880 × 371 910. Budget
   hours, not seconds, for rank 5.
5. **"validated across ranks 1–6"** — true, but at denominator power 1 (den² only at ZV rank 4),
   and its positive controls are the ultrahyperbolic CG metrics. Fine for an instrument; say so.
6. **"almost no other spacetime has anything like [Carter]"** — rhetorical; rank-2 hidden
   symmetries are common (Kerr–NUT–(A)dS towers, pp-waves, Lense–Thirring). Harmless, left as is.
7. The framing "rank 3 and 4 … constructed, not found" — correct (GHKW 2011, Gibbons–Rugina 2011).

### Analysis — one structural observation, and why it matters (UNVERIFIED)

CG's Ricci-flat condition on the `(1,1)` base is `∂_x ∂_y U = 0`, i.e. `U = f(x) + g(y)`. Put
`x = z`, `y = z̄`: the base kinetic term `2 dx dy` becomes `2(dX² + dY²)` and `U` becomes
`f(z) + g(z̄)`, which is **harmonic** on the Euclidean plane; it is real iff `g = f̄`. So every CG
`(2,2)` Ricci-flat metric is the complex form of a **Lorentzian vacuum pp-wave** with a harmonic
profile. For CG's second Drach potential `U = α/√x + β/√y` the real form is
`V = 2 Re(α z^{−1/2}) = (a√(r+x) + b√(r−x))/r`, which is the `σ = 0` member of the 1965
Friš–Mandrosov–Smorodinsky–Uhlíř–Winternitz potential `V^(4)` — second-order superintegrable.
Drach's cubic integral, analytically continued, has real and imaginary parts that are each
integrals of the real system (`H` is real, the bracket is bilinear); at least one is a nonzero
cubic with a pure `(p_X, p_Y)` leading part, and since `V` has no continuous symmetry the only
Killing vectors are `∂_t, ∂_s`, so every reducible rank-3 tensor carries a factor `p_t` or `p_s`
and cannot reproduce that leading part. **If this survives the three exact checks it is a 4D
Lorentzian vacuum spacetime with an irreducible rank-3 Killing tensor — the object CG 2015 and
Fordy–Galajinsky 2019 say is not known.** The same substitution on CG eq. 26 would give a 5D
`(1,4)` vacuum metric with rank 4.

Two caveats, both load-bearing. (i) By Popper–Post–Winternitz 2012, any third-order integral of a
parabolic-separable potential is the Poisson bracket of two second-order ones; the sibling's
rank-2 count on CG-4D (reducible span 10 at rank 3 ⇒ two quadratic integrals beyond `H`) says the
same. So the cubic will be **polynomially irreducible but functionally dependent** — it passes
check 3 as written in `TASK.md`, and it is what GHKW/GOKK call irreducible, but an
integrable-systems referee would call it dependent. Which notion counts is the user's call.
(ii) Nothing above has been computed. Tier 1 is minutes with the sibling's prover.

**Consequence for rank ≥ 5.** For a 2D base that is second-order superintegrable the polynomial
integrals close at rank 3 (quadratic algebra: `{K_1, X}` is a polynomial in `H, K_1, K_2`;
`X² ∈ ℂ[H,K_1,K_2]`), so no polynomially-irreducible rank ≥ 4 comes from such a base
(*expected, unverified*). Rank ≥ 5 in vacuum needs a harmonic potential with a *genuinely*
quintic integral — CG report none in Hietarinta's list — or a base of dimension ≥ 3, where CG
call even the cubic case "intractable". No route is known to me.

**Grade of this entry.** Map (tables A–C, non-existence table): *verified* against fetched
primary sources unless marked. Corrections 1–5: *verified*. The Wick-rotation observation:
*unverified hypothesis*, with a stated cheap falsifier.

**Implementation.** Files: `report.md` (this entry), `TODO.md` (rewritten), `TASK.md`
(corrections applied in place, marked `[EXP-001]`), `prior_art/` (PDFs and `pdftotext`
extractions of 1103.5366, 1107.5987, 1201.3085, 1503.02162, 1901.03699, 2112.07649, 2207.03474,
2407.11178, 2504.18287, 2603.15626, with a manifest). No code, no sibling files touched.

**Next steps.** Stop here (the brief). Decisions needed before EXP-002: (a) which irreducibility
notion; (b) whether `(2,q)` signature counts; (c) whether to re-target to Lorentzian vacuum rank 3
(cheap, closes a stated open problem if it works) rather than rank ≥ 5 (no known route in
vacuum, already done without field equations). Tier-2 controls for whatever follows: run CG-4D
rank 3 and CG-5D rank 4 through `_kt_exact.py` here (sibling did it; must be reproduced from this
repo), and the Galajinsky-2012 rank-5 tensor as the only known rank-5 positive control.

### References (all checked against the source today; "abs" = arXiv abstract page, "full" = full text read)

- G. W. Gibbons, T. Houri, D. Kubizňák, C. M. Warnick, *Some spacetimes with higher rank Killing–Stäckel tensors*, Phys. Lett. B 700 (2011) 68–74, arXiv:1103.5366 [full]
- G. W. Gibbons, C. Rugina, *Goryachev–Chaplygin, Kovalevskaya, and Brdička–Eardley–Nappi–Witten pp-waves spacetimes with higher rank Stäckel–Killing tensors*, J. Math. Phys. 52 (2011) 122901, arXiv:1107.5987 [full]
- A. Galajinsky, *Higher rank Killing tensors and Calogero model*, Phys. Rev. D 85 (2012) 085002, arXiv:1201.3085 [full]
- M. Cariglia, A. Galajinsky, *Ricci-flat spacetimes admitting higher rank Killing tensors*, Phys. Lett. B 744 (2015) 320–324, arXiv:1503.02162 [full]
- S. Filyukov, A. Galajinsky, *Self-dual metrics with maximally superintegrable geodesic flows*, Phys. Rev. D 91 (2015) 104020, arXiv:1504.03826 [abs; rank 2, (2,q)]
- A. Galajinsky, *Eisenhart lift in pseudo-Euclidean space and higher rank Killing tensors*, Phys. Part. Nucl. Lett. 14 (2017) 328–330, no arXiv [abstract via INSPIRE]
- A. P. Fordy, A. Galajinsky, *Eisenhart lift of 2-dimensional mechanics*, Eur. Phys. J. C 79 (2019) 301, arXiv:1901.03699 [full]
- F. Gray, D. Kubizňák, *Slowly rotating black holes with exact Killing tensor symmetries*, Phys. Rev. D 105 (2022) 064017, arXiv:2110.14671 [abs]
- F. Gray, R. A. Hennigar, D. Kubizňák, R. B. Mann, M. Srivastava, *Generalized Lense–Thirring metrics: higher-curvature corrections and solutions with matter*, JHEP 04 (2022) 070, arXiv:2112.07649 [full]
- S. He, Y. Li, *Spacetimes with prescribed Killing tensor symmetries*, Phys. Rev. D 110 (2024) 084076, arXiv:2407.11178 [full]
- F. Gray, G. Odak, P. Krtouš, D. Kubizňák, *On a lower-dimensional Killing vector origin of irreducible Killing tensors*, JHEP 07 (2025) 098, arXiv:2504.18287 [full]
- A. Galajinsky, *The Bohlin variant of the Eisenhart lift*, arXiv:2603.15626 (2026) [full]
- A. J. Keane, B. O. J. Tupper, *Killing tensors in pp-wave spacetimes*, Class. Quantum Grav. 27 (2010) 245011, arXiv:1011.6401 [abs; rank 2]
- B. Kruglikov, W. Steneker, *Killing tensors in Koutras–McIntosh spacetimes*, Class. Quantum Grav. 39 (2022) 225005, arXiv:2207.03474 [full]
- J. Gregorovič, L. Zalabová, *Irreducible Killing and conformal Killing tensors on homogeneous plane waves*, Phys. Scr. 100 (2025) 095210, arXiv:2505.07368 [abs; rank 2]
- B. S. Kruglikov, V. S. Matveev, *Nonexistence of an integral of the 6th degree in momenta for the Zipoy–Voorhees metric*, Phys. Rev. D 85 (2012) 124057, arXiv:1111.4690 [abs]
- A. Vollmer, *Killing tensors in stationary and axially symmetric space-times*, J. Geom. Phys. 115 (2017) 28–36, arXiv:1602.08968 [abs]
- B. Kruglikov, V. S. Matveev, *The geodesic flow of a generic metric does not admit nontrivial integrals polynomial in momenta*, Nonlinearity 29 (2016) 1755–1768, arXiv:1510.01493 [abs]
- C. B. Owen, N. Yunes, H. Witek, *Petrov type, principal null directions, and Killing tensors of slowly rotating black holes in quadratic gravity*, Phys. Rev. D 103 (2021) 124057, arXiv:2103.15891 [abs]
- D. Kokkinos, *Killing tensors of Weyl's class*, arXiv:2608.22523 (2026) [abs]
- T. Houri, K. Tomoda, Y. Yasui, *On integrability of the Killing equation*, Class. Quantum Grav. 35 (2018) 075014, arXiv:1704.02074 [abs]
- G. Thompson, *Killing tensors in spaces of constant curvature*, J. Math. Phys. 27 (1986) 2693 [title/journal only; text paywalled]
- R. G. McLenaghan, R. Milson, R. G. Smirnov, *Killing tensors as irreducible representations of the general linear group*, C. R. Acad. Sci. Paris, Ser. I (2004), doi:10.1016/j.crma.2004.07.017 [abs]
- K. Kiyohara, *Two-dimensional geodesic flows having first integrals of higher degree*, Math. Ann. 320 (2001) 487–505 [secondary]
- V. S. Matveev, *Real-analyticity of 2-dimensional superintegrable metrics and solution of two Bolsinov–Kozlov–Fomenko conjectures*, arXiv:2501.18485 (2025) [abs]
- G. Valent, *Superintegrable models on Riemannian surfaces of revolution with integrals of any integer degree (I)*, Regul. Chaotic Dyn. 22 (2017) 319–352, arXiv:1703.10870 [abs]
- J. Friš, V. Mandrosov, Ya. A. Smorodinsky, M. Uhlíř, P. Winternitz, *On higher symmetries in quantum mechanics*, Phys. Lett. 16 (1965) 354 [secondary]
- I. Popper, S. Post, P. Winternitz, *Third-order superintegrable systems separable in parabolic coordinates*, J. Math. Phys. 53 (2012) 062105, arXiv:1204.0700 [abs]
- F. Tremblay, A. V. Turbiner, P. Winternitz, *An infinite family of solvable and integrable quantum systems on a plane*, J. Phys. A 42 (2009) 242001, arXiv:0904.0738 [abs; the "degree 2k" statement is from secondary sources — partially verified]
- J. Hietarinta, *Direct methods for the search of the second invariant*, Phys. Rep. 147 (1987) 87–154 [secondary; CG's [13]]
- Sibling: `../conjecture_machine` JOURNAL.md 2026-08-16 and 2026-08-21, RESULTS.md §124, §127, DECISIONS.md D39 (attribution: their computations, not mine)

## EXP-002  Wick rotation of CG's second Drach metric: a 4D Lorentzian vacuum pp-wave with an irreducible rank-3 Killing tensor — 2026-09-05

**Goal.** Test the EXP-001 observation: continue Cariglia–Galajinsky's signature-(2,2) Ricci-flat
metric (arXiv:1503.02162 eq. 1, 20, 21) to Lorentzian signature and run the three exact checks on
the continued cubic — field equations, `{H,F} = 0`, irreducibility in **both** senses (user's
decision (a)), signature stated next to the rank (decision (b)).

**Hypothesis.** `x = z, y = z̄` turns CG's `(1,1)` base into the Euclidean plane and `U = f(x)+g(y)`
into a harmonic function, so the `(2,2)` metric is a complex form of a vacuum pp-wave. The
continued cubic should be conserved and polynomially irreducible; because the base is second-order
superintegrable it should be functionally dependent on the quadratics.

**Method (M2).** Coordinates `(t, ξ, η, s)`; `w = ξ + iη`, `x = w²`, `y = w̄²` (so `√x = w`,
`X + iY = w²` are Cartesian transverse coordinates and `(ξ,η)` parabolic ones); `ρ² = ξ² + η²`;
`α = β = a` real (reality of `U` needs `β = ᾱ`; `a → −a` is `ξ → −ξ`, `|a|` is a gauge by
`t → μt, s → s/μ`, so `a = 1` is general). `H = ½ g^{ab} p_a p_b`,
`{A,B} = Σ_a (∂_{x^a}A ∂_{p_a}B − ∂_{p_a}A ∂_{x^a}B)`. Reducible (polynomial) = linear combination
of symmetrized products of lower-rank Killing tensors; functional = Jacobian rank on the 8-dim
phase space. All symbolic work in SymPy 1.14 with exact rationals, `a` symbolic wherever it costs
nothing; run with the sibling's venv interpreter on files in this repo.

**The object.**

    ds² = −(4aξ/ρ²) dt² + 2 dt ds + 8ρ² (dξ² + dη²)                    signature (1,3)
        = −2√2 a (√(r+X)/r) dt² + 2 dt ds + 2(dX² + dY²),   r² = X² + Y²        [Cartesian form]

i.e. a Brinkmann pp-wave with profile `−2U`, `U = 2a Re(z^{−1/2})`, harmonic. Smooth on
`(w-plane ∖ {0}) × R²`, which double-covers the punctured `(X,Y)` plane (`w → −w` flips `U`);
singular at `w = 0`; not geodesically complete — the same caveats CG state for theirs.

    H  = p_t p_s + 2aξ p_s²/ρ² + (p_ξ² + p_η²)/(16ρ²)
    Q1 = p_ξ²/16 + 2aξ p_s² − ξ²(H − p_t p_s)                              rank 2
    Q2 = (p_ξ − p_η)²/32 + a(ξ − η) p_s² − ½(ξ − η)²(H − p_t p_s)          rank 2
    F  = (η p_ξ − ξ p_η)(p_ξ² + p_η²)/(32ρ²) + (a p_s²/ρ²)[ξη p_ξ + ½(η² − ξ²) p_η]     rank 3

`F` is the imaginary part of the continued CG cubic (the real part vanishes identically) and equals
`−4{Q1,Q2}` identically. Nonzero contravariant components (index order `t, ξ, η, s`):
`K^{ξξξ} = η/(32ρ²)`, `K^{ηηη} = −ξ/(32ρ²)`, `K^{ξξη} = −ξ/(96ρ²)`, `K^{ξηη} = η/(96ρ²)`,
`K^{ssξ} = aξη/(3ρ²)`, `K^{ssη} = a(η² − ξ²)/(6ρ²)`. In Cartesian terms the pure part is
`−¼ L (p_X² + p_Y²)`, `L = X p_Y − Y p_X`.

**Implementation.** `scripts/exp002_ppwave.py` (checks 1, 2, 3a, 3b), `exp002_relation_check.py`
(the algebraic relation, reducible-span rank), `exp002_sibling_prover.py` (the sibling's
`_kt_search.solve_kt_modp` **by import**, `ckpt=None`, nothing written; PID 63481, 3.4 min, one
core), `exp002_geodesic_check.py` (numerical route with a known-fail), `exp002_cg22_bracket.py`
(CG's own variables), `exp002_jac_noQ2.py`, `exp002_tower.py`. Logs in `results/exp002_*.log`.
`../conjecture_machine` untouched; PID 1655 untouched.

**Results.**

| # | check | method | result | grade |
|---|---|---|---|---|
| 1 | field equations | Ricci tensor, symbolic `a`, exact | `R_ab ≡ 0`; Riemann has 16 nonzero components (e.g. `R^ξ_{ttξ} ∝ aξ(3η²−ξ²)/ρ⁸`); Kretschmann `= 0` (VSI, as for every pp-wave) | **verified** |
| 1 | signature | `(t,s)` block has `det = −1` → (1,1); transverse block `8ρ² I` → (0,2) | **(1,3) Lorentzian** wherever `ρ ≠ 0`; numeric eigenvalues at a sample point `(−1.72, 0.58, 46.7, 46.7)` | **verified** |
| 2 | transcription control | CG eq. 20 in *their* variables, `{H₂, I} = 0` | `True`; footnote-9 quadratic recovered as `x p_x p_y − y p_y² + βx/√y − α√x` (the pdf-garbled term is `−α√x`) | verified |
| 2 | conservation | `{H, F_D} = 0` exact, symbolic `a` | `True`; `Re F_D ≡ 0`, `Im F_D ≠ 0`, `{H, Im F_D} = 0` | **verified** |
| 2 | conservation, independent route | RK4 geodesics, 5 orbits × 20 000 steps, `h = 10⁻³` | max relative drift of `F`: `1.6e-13 … 1.8e-12`; `H, Q1, Q2` similar; **known-fail** `p_ξ³ + p_t p_s p_η` drifts by `6 … 1.3e4` | verified |
| 3a | `dim K1` | 1-jet count: every Killing vector must satisfy `L_ξ R = 0` and `L_ξ ∇R = 0` at every point; rank of that linear system in the 10-dim jet at two generic points | rank 8 → at most 2 Killing vectors; `∂_t, ∂_s` are two → **`dim K1 = 2`** (no ansatz) | **verified** |
| 3a | polynomial irreducibility | every element of `K1 ⊙ K2` carries a factor `p_t` or `p_s`; pure `(p_ξ,p_η)`-cubic part of `F` is `(η p_ξ − ξ p_η)(p_ξ²+p_η²)/(32ρ²) ≠ 0` | **`F` is not a sum of products of lower-rank Killing tensors** | **verified** |
| 3a | `F` vs `{Q1,Q2}` | linear solve modulo `K1 ⊙ K2` | `F = −4{Q1,Q2}` identically; the 10 products span a 10-dim space, `F` raises it to 11 | verified |
| 3a | independent instrument | sibling's modular sampled nullspace, two primes, ansatz `poly_{≤6}(ξ,η)/ρ²`, `t,s`-independent coefficients | **control** (their CG (2,2) metric, `den = ru`): ranks 1/2/3 → `2 / 6 / 11` = their published numbers. **pp-wave**: `2 / 6 / 11` | verified |
| 3a | squeeze | lower bound 11 from exhibited solutions (10 reducible + `F`), upper bound 11 from the sampled nullspace | `dim K3 = 11` **within that ansatz**: exactly one irreducible rank-3 direction, and it is `F` | verified (ansatz-scoped) |
| 3b | functional | Jacobian rank on the 8-dim phase space, 3 random rational points | `rank(p_t,p_s,H,Q1,Q2) = 5 = rank(p_t,p_s,H,Q1,Q2,F)` → **`F` is functionally dependent** | **verified** |
| 3b | the relation | weighted-homogeneous fit, then identity check with symbolic `a` | **`F² = 4[(H − p_t p_s)(Q1² + Q2²) − a² Q1 p_s⁴]`** identically | **verified** |
| 3b | CG's framing | without `Q2` | `rank(p_t,p_s,H,Q1,F) = 5`: `F` *is* independent of `{p_t,p_s,H,Q1}` — CG's footnote-9 statement holds; it is `Q2` that makes `F` dependent | verified |
| — | CG's own example | their (2,2) variables | their cubic `I = −½{Q_a, Q_b}` exactly, with `Q_b` the `(x,α)↔(y,β)` image of their footnote-9 quadratic; functional rank of `(H₂,Q_a,Q_b,I)` is 3 | verified |

**Analysis.**

*What was asked, answered in order.* (1) The continued metric is exactly Ricci-flat and
Lorentzian (1,3). (2) The continued cubic is exactly conserved; its real part is identically zero
and its imaginary part is the Killing tensor. (3) Irreducible in the **polynomial** sense — proved
without any ansatz, from `dim K1 = 2` plus a nonzero pure part — and **dependent** in the
**functional** sense, with the explicit relation `F² = 4[(H − p_t p_s)(Q1² + Q2²) − a² Q1 p_s⁴]`.
(4) Nothing failed.

*Both halves, together, as instructed.* Under the definition CG 2015 and Fordy–Galajinsky 2019
use when they say no vacuum solution with a higher-rank Killing tensor is known, **this is a
4D Lorentzian vacuum spacetime with an irreducible rank-3 Killing tensor**, and the "empirical
barrier of rank 2" they call puzzling is not a barrier in that sense. Under the functional
definition, `F` is the Schouten–Nijenhuis bracket of the two parabolic separation constants of a
second-order-superintegrable harmonic profile; it adds no constant of motion the quadratics do not
already supply, and an integrable-systems referee will say so. **The same is true of CG's own
published (2,2) examples**: their cubic is `−½{Q_a,Q_b}` in their own variables. So the new object
sits on exactly the footing of the ones the literature already calls irreducible — no better, no
worse — and its only new content is the signature.

*Why it was missed.* The Ricci-flat condition on CG's `(1,1)` base, `U = f(x)+g(y)`, is the
complex form of harmonicity; the continuation costs nothing. CG's search for Lorentzian examples
went through Hietarinta's list of *genuinely* cubic systems, which excludes bracket-type cubics by
construction, so the 1965 Friš–Mandrosov–Smorodinsky–Uhlíř–Winternitz potential
`V⁽⁴⁾|_{σ=0} = (α√(r+x) + β√(r−x))/r` — harmonic, and the real form of CG's second Drach
potential — never came up. This suggests the "barrier" is a definitional artefact rather than a
theorem: any vacuum pp-wave whose harmonic profile is multiseparable with non-commuting separation
tensors and no extra Killing vectors will carry a polynomially-irreducible `{Q_a,Q_b}`.
*(Generalisation unverified; only this metric was computed.)*

*Scope.* `dim K1 = 2` and polynomial irreducibility are unconditional. `dim K2 = 6` and
`dim K3 = 11` are statements within the ansatz "coefficients polynomial of degree ≤ 6 in `(ξ,η)`
over `ρ²`, independent of `t, s`" — the same scope as the sibling's published counts. "At least one
irreducible rank-3" is unconditional; "exactly one" is ansatz-scoped.

*Rank ≥ 4 from this metric: the tower closes.* Bracketing the relation gives the closure
`{Q1,F} = −(H − p_t p_s) Q2`, `{Q2,F} = (H − p_t p_s) Q1 − ½ a² p_s⁴`; both verified at 40 random
rational phase-space points for `a = 1` and `a = 3/2` (`scripts/exp002_tower.py`,
`results/exp002_tower.log`), and both rank-4 brackets lie in the rank-4 reducible span
`K2 ⊙ K2 + K1 ⊙ F` (rank 22 of 23 generators — the one relation is `(p_t p_s)² = p_t² · p_s²` —
unchanged when either bracket is adjoined, two primes). So this metric yields no
polynomially-irreducible rank 4 by the bracket route.

*A check that fired, and why (rule: ask why before acting on it).* The first run of the tower test
reported `{Q2,F}` as a **new irreducible rank-4 tensor**. It was the test: the coupling `a` had
been randomised per sample point, but "in the span" means with *constant* coefficients, and the
closure formula carries `a²`. Fixing `a` per run (it is part of the metric, not a phase-space
variable) removed the finding. The same per-point randomisation in `exp002_relation_check.py` is
harmless there, because that test's conclusions are all of the "not in the span" kind, which a
varying parameter can only make harder. Also recorded: three earlier versions of this check
stalled silently for 5 min each — `sp.solve` on coefficient identities, then `Matrix.rank` on a
50 × 23 rational matrix; pointwise evaluation plus a hand-written GF(p) elimination took 2 s.

**Grade.** Checks 1, 2, 3a, 3b: **verified**, by two routes each where a second route existed
(symbolic bracket + numerical geodesics; my nullspace count + the sibling's). The generalisation
to other multiseparable harmonic profiles: **unverified**.

**Next steps.** (i) The same continuation on CG eq. 26 should give a 5D Lorentzian vacuum metric
with a rank-4 Killing tensor — signature (1,4), ~10 minutes, not run. (ii) A one-page write-up
would be the natural product: the object, the two definitions, both verdicts. (iii) Rank ≥ 4 in 4D
vacuum is not reached by this route — the tower closes at rank 3, verified; rank ≥ 5 remains as
EXP-001 left it.

## EXP-003  Prior art on the object; the (2,2) computation made explicit; a 5D vacuum companion — 2026-09-05

**Goal.** Three ordered items from the user: (1) sweep for *the metric* (a vacuum pp-wave with
profile `Re z^{−1/2}`, the σ = 0 Smorodinsky–Winternitz V⁽⁴⁾ lift) — outcome F if found; (2) put
the computation behind "CG's cubic is `−½{Q_a,Q_b}`" on the page; (3) extend to 5D on CG eq. 26.

**Method.** (1) Targeted searches (SW lifts, pp-wave profiles, higher-rank Killing tensors on
pp-waves, Stäckel/Shapovalov waves), INSPIRE full-text queries, forward citations of Keane–Tupper
2010, Cariñena et al. 2017, Fordy–Galajinsky 2019, Kubů–Tempesta 2025; full texts of
Cariñena et al. 2017 (arXiv:1701.05783), Kubů–Tempesta (arXiv:2509.19950), Andrzejewski et al.
(arXiv:2003.07649) and Cariglia's 2014 review added to `prior_art/`. (2)
`scripts/exp002_cg22_bracket.py`, `exp002_cg22_relation.py`, everything printed. (3) An invariant
obstruction for eq. 26/30/33/35, then a different 5D construction, `scripts/exp003_5d_gyraton.py`
and `exp003_5d_squeeze.py`.

**Results.**

*(1) Prior art on the object — NOT FOUND.* Nearest neighbours, with what each does and does not
contain:

| paper | contains | does not contain |
|---|---|---|
| GHKW 2011 §4 | the general Lorentzian lift `g = dx²+dy²−2V dt²+2dt ds`, `R_tt = ΔV`; "many superintegrable systems … give rise to higher-rank Killing tensors" | any SW potential; any vacuum example (only Post–Winternitz, `ΔV ≠ 0`) |
| Cariñena–Herranz–Rañada 2017 | Eisenhart lifts of all four SW families incl. V⁽⁴⁾ (`V_d`, "separable in two parabolic systems") | Lorentzian signature (it is the Riemannian `diag(1,1,V)` lift); any rank > 2 ("we restrict our study to … p = 2 Killing tensors"; p > 2 named open) |
| Kubů–Tempesta 2025/26 | SW I, II lifts in Stäckel form; "analogous analysis can be performed for … IV" | the analysis; their Lorentzian example is a non-Einstein Platonic wave with `1/x²` potential |
| Fordy–Galajinsky 2019 §3.1.4 | a bracket cubic `F3 = {F1,F2}` with its quadratic-algebra relation on a Darboux–Koenigs lift | vacuum (curved base); and states no vacuum solution with higher-rank KT is known |
| Keane–Tupper 2010; Gregorovič–Zalabová 2025 | rank-2 Killing tensors of pp-waves / homogeneous plane waves | rank 3 |
| Kruglikov–Steneker 2022 | generic conformally-flat pp-waves: all degree-3/4 KTs reducible | type-N (vacuum) profiles |

Grade: *verified as not found in the reachable literature*; a negative sweep is never complete.

*(2) CG's (2,2) computation, explicit* (`results/exp002_cg22_bracket.log`, `exp002_cg22_relation.log`):

    H  = p_x p_y + α/√x + β/√y
    I  = x p_x² p_y − y p_x p_y² + βx p_x/√y − αy p_y/√x                          (CG eq. 20)
    Q_a = x p_x p_y − y p_y² + βx/√y − α√x                                        (CG footnote 9)
    Q_b = y p_x p_y − x p_x² + αy/√x − β√y                                        (mirror)
    {H,Q_a} = {H,Q_b} = {H,I} = 0
    {Q_a,Q_b} = 2αy p_y/√x − 2βx p_x/√y − 2x p_x² p_y + 2y p_x p_y² = −2 I        (identity)
    rank J(H,Q_a,I) = 3 ;  rank J(H,Q_a,Q_b) = 3 ;  rank J(H,Q_a,Q_b,I) = 3
    I² = −H Q_a Q_b − β² Q_a − α² Q_b                                              (identity)

So the published (2,2) rank-3 tensor is a bracket cubic, functionally dependent on the three
quadratics, with an explicit cubic Casimir — the same structure as the Lorentzian object. Grade:
**verified**.

*(3a) CG eq. 26 does not continue.* eq. 26/30 come from Drach's first system,
`U = αy + γ/√x − (αx)²/2`: not symmetric in `x ↔ y`, cross term `2αx dt dw`; under `x = z, y = z̄`
nothing is real for any nonzero `(α,γ)`. Invariant form in 4D: CG say the first-system metric is
anti-self-dual; a non-flat ASD (2,2) metric has no Lorentzian real form (`W⁻ = 0` ⇒ `W = 0` ⇒
flat). eq. 33 has a complex cross term `−(2/√x) dt dw`; eq. 35 under `w = conj(u)` gives
`dw² + du² = 2(dχ² − dψ²)`, signature (2,4). **Rank 4 in Lorentzian vacuum is not reached by
continuation.** Grade: verified (componentwise reality), the ASD argument is standard.

*(3b) A 5D Lorentzian vacuum member, by a different route* (`results/exp003_5d.log`):

    ds² = −2U dt² + 2 dt ds + 2A dt dv + dv² + 8ρ²(dξ² + dη²),   A = 2κξ/ρ²,
    U   = 2aξ/ρ² − λA² + 2μ(ξ² − η²)/ρ⁴

| step | result |
|---|---|
| `R_ab = 0` | only `R_tt = −κ²(4λ−1)/(4ρ⁶)` ≠ 0 → `λ = ¼`; then `R_ab ≡ 0` with `a, κ, μ` symbolic |
| signature | `(t,s)` block det −1, `v` direction +1, transverse `8ρ² I` → **(1,4)** |
| reduced system | `ρ² V_eff` polynomial of degree ≤ 1 iff `μ = −κ²/4`; then `ρ² V_eff = κ²p_s²/2 + 2p_s(a p_s − κ p_v) ξ` — SW-IV with σ ≠ 0 |
| `Q1, Q2, F = −4{Q1,Q2}` | `{H,Q1} = {H,Q2} = {H,F} = 0` exact; `F ≠ 0`; pure part `(ηp_ξ − ξp_η)(p_ξ²+p_η²)/(32ρ²)`; `F|_{κ=0}` = the 4D tensor |
| `dim K1` | jets at two points: `L_ξR` alone gives rank 12 of 15 → ≤ 3; `∂_t, ∂_s, ∂_v` → **= 3** |
| polynomial irreducibility | reducibles carry `p_t`, `p_s` or `p_v`; pure part ≠ 0 → **irreducible** |
| functional | `rank(p_t,p_s,p_v,H,Q1,Q2) = 6 = rank(…,F)` → **dependent** |
| squeeze (`a = κ = 1`) | exhibited: `K1 = 3`, `K2 = 9`, `K1⊙K2 = 19`, `+F = 20`; sibling's 5D sampled nullspace (`set_dim`, `poly_{≤8}/ρ⁴`, `ckpt=None`): rank 1 → 3, rank 2 → 9, rank 3 → **20** (477 s). Squeeze closed: `dim K3 = 20` in that ansatz, one irreducible direction, `F` |

Reading: `ds₅² = ds₄² + (dv + A dt)²`, `ds₄²` the pp-wave with profile `2U + A² = (4aξ + κ²)/ρ²` —
the KK lift of a 4D Einstein–Maxwell pp-wave whose null Maxwell field sources the Kepler term of
SW-IV (standard reduction, not re-verified). Grade: **verified**; the count is ansatz-scoped as in EXP-002.

**Analysis.** The family is {4D (1,3), 5D (1,4)} at rank 3, both vacuum, both polynomially
irreducible and functionally dependent, both sharing the same cubic. Rank 4 is blocked at the
source: the only rank-4 systems CG have are the asymmetric Drach ones. Step (2) settles the
load-bearing defence: the objection "it is only a bracket" applies with equal force to the
examples the literature already accepts.

**Implementation.** `scripts/exp002_cg22_bracket.py`, `exp002_cg22_relation.py`,
`exp003_5d_gyraton.py`, `exp003_5d_squeeze.py`; `results/exp002_cg22_*.log`, `exp003_5d*.log`;
`prior_art/` += 1701.05783, 2509.19950, 2003.07649, 1411.1262 (+ text). `WRITEUP.md` written.
Sibling repo untouched; PID 1655 untouched; my runs single-core, longest 12 min.

**Next steps.** None planned: rank ≥ 5 stays parked per the user; write-up delivered.
