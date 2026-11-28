# Field-expert checklist for the preprint draft (fleet rule 7b; internal, for the Bridge's read)

What an expert in integrability and differential Galois theory, computer-assisted proof, and exact solutions in GR
would check first, with our status. **Done** means checked here; an outside check is named where one exists. **Open**
means not yet checked.

| # | the expert's first question | status |
|---|---|---|
| 1 | Is the variational equation the right one, i.e. the normal variational equation along a genuine particular solution of the geodesic Hamiltonian? | **done** internally (`MRS_SECTION.md` §5b–§5c); two hostile AI referee rounds (T38, T51). No human check: **open** |
| 2 | Does Morales–Ramis apply to this Hamiltonian, given that the metric off the axis is only defined by continuation from axis data? | done by our own majorant proof (Proposition 2, §4b) and a numerical control. **Open:** independent check of the proof |
| 3 | Is the covering/gauge step (monodromy on the orbit's Riemann surface, the identity component) correct? | done (Lemma C, `MRS_SECTION.md` §1). **Open:** one theorem number is cited secondhand (Morales-Ruiz–Ramis 2001, Thm 5) |
| 4 | Is Zariski-dense monodromy enough, i.e. is the monodromy contained in the differential Galois group? | done: monodromy ⊂ Galois always holds, so a dense monodromy forces Galois = SL₂ (standard; van der Put–Singer) |
| 5 | Are the test conditions (F ≠ 0, traces ≠ 0, finite traces excluded) complete for the SL₂ subgroup classification? | done by hand (a reducible / imprimitive / finite case analysis); graded sound in a separate read |
| 6 | Are the loops genuine closed loops for the multivalued twist c0? | done (float, 50 digits): `CLOSURE_STOPC_RESULT.md`. The circle closes exactly while it encloses all branch points |
| 7 | Known false positives of numerical argument-principle counts: zeros on or near the contour, branch cuts crossing the rectangle, insufficient step control | done in the pre-fixed protocols (step variation, contour-margin guards, a branch-cut guard; spin 0.95 dropped for this reason). **Open:** the counts are not interval-certified |
| 8 | Interval-arithmetic soundness: is every operation enclosed (Arb), is the ellipse bound M rigorous, is the analyticity domain checked? | done: Arb throughout; M by a Dyson bound; holomorphy boxes; must-fail controls; an independent 50-digit node check; a non-author code read (by an AI session). **Open:** human audit of the code |
| 9 | Is the family itself physical (vacuum, asymptotically flat, regular)? | axis regularity on both outer segments for 0 ≤ k ≤ 30/7 (T38 1c/1d). **Open:** off-axis regularity, horizons, CTCs (stated as not checked) |
| 10 | Prior art: is this known? | papers read at source are listed in the paper's introduction. **Open:** no systematic literature search beyond those, so no novelty claim is made |
| 11 | Does the result depend on the chosen energy, spin or orbit? | stated as four spins and one energy; E = 1.5 only on the end sliver at a = 0.6 |
| 12 | Who checked what? | stated in §4 and §7: AI sessions only; no human peer review |
