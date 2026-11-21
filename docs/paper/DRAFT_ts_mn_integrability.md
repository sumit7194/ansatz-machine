# DRAFT v1 — Hidden symmetries and transient chaos in two non-Kerr stationary vacua: Tomimatsu–Sato δ = 2 and Manko–Novikov

*Working draft (ansatz-machine; v0 2026-11-17, v1 2026-11-21). Not for circulation. Sources are this repo's RESULTS
§148–§157 only; v1 changes are listed in "v1 audit" at the end. **EMBARGO: this file contains TS chaos numbers (α,
the fate-map counts). Do not forward it, or any number in it, to tabula (tools/EMBARGOES.json).**
References marked **[verify]** have not yet been checked at the source; nothing goes out until every one is checked.
Cross-references to independent fleet work (the Bridge's reproductions; tabula's TS measurements) are placeholders:
they are relayed, not verified here, and a combined paper is the user's decision.*

---

## Abstract (draft)
We study whether geodesic motion in two exact stationary axisymmetric vacuum spacetimes with non-Kerr multipoles,
Tomimatsu–Sato with δ = 2 (TS2) and the Manko–Novikov (MN) q-anomaly family, admits a hidden conserved quantity
beyond energy, axial angular momentum and the mass shell. Using an ansatz-free prolongation bound evaluated in exact
modular arithmetic, we find that neither admits a Killing tensor invariant under ∂_t and ∂_φ beyond the trivial ones:
- TS2 up to valence 10 at two parameter points, and up to valence 8 at eight more (p from 0.28 to 0.96);
- MN up to valence 10 at two parameter points of opposite anomalous quadrupole;
- and, deforming Kerr by the MN anomalous quadrupole to first order, none of Kerr's Killing tensors of valence 1–6
  survives, not even a power of the Carter constant.

The MN results exclude, at these points, the fourth-order generalised Carter constant suggested numerically by Brink.
In TS2, a separatrix-matched comparison with Kerr locates the dynamical consequence: geodesics near the capture
(survive/plunge) edge show transient chaos. Kerr shows none under identical tests. The survive/plunge boundary has an
effective uncertainty exponent α ≈ 0.04–0.16 for TS2 against α ≈ 1 for Kerr, and it remains fractal-like down to
initial-condition scales ε ≈ 10⁻¹⁴ in 32-digit arithmetic. At one energy and angular-momentum level next to that edge,
the unstable spherical-type orbit has a transverse homoclinic point (Kerr: zero splitting), so a chaotic saddle exists
there; this is numerical, not a computer-assisted proof. Whether the edge's fine structure is that saddle's stable
manifold was tested three times, pre-registered, and is not established. Poincaré sections at 300 crossings do not discriminate,
which explains the earlier report of complete integrability. We state exactly what is and is not claimed: rank-bounded,
local and invariant-class for the symmetry nulls; finite-horizon for the chaos; and no strict-limit fractal.

## 1. Introduction (outline)
- Kerr's Carter constant, why integrability matters (EMRI waveforms), and non-Kerr test spacetimes.
- Prior claims:
  - Dubeibe, Pachón & Sanabria-Gómez 2007 call TS2 "completely integrable" from regular Poincaré sections, while
    finding chaos in a deformed (Manko et al.) solution (gr-qc/0701065, verified);
  - Brink, *Spacetime Encodings IV* (arXiv:0911.1595), writes that numerical experiments (his ref. [6] is Gair–Li–
    Mandel) suggest "a large number of SAV spacetimes may possess a fourth-order Killing tensor" (verified, intro);
  - Gair, Li & Mandel 2008: most MN geodesics have an approximate fourth constant, which can be lost (chaos) for some
    orbits in oblately deformed MN (verified, abstract);
  - Contopoulos, Harsoula & Lukes-Gerakopoulos 2012: escapes to the central bumpy black hole in MN, framed as chaotic
    scattering (verified, abstract and introduction).
- Methods lineage: Kruglikov–Matveev arXiv:1111.4690 (ZV δ = 2: no integral polynomial in momenta of degree ≤ 6, by
  prolongation on jets; verified, body); Vollmer arXiv:1602.08968 (TS2 at δ = 2, p = 3/5: no KT to valence 7,
  restricted to tensors in involution with dt, dφ and the metric, the same invariant class as ours; verified, body).
- Our contributions:
  - (i) valence-10 nulls for TS2 at a new parameter point, and beyond Vollmer at his;
  - (ii) a parameter sweep;
  - (iii) KT nulls for MN (no earlier KT nonexistence result for MN was found in our sweep, §151; we do not claim
    "first"), with a sound treatment of its transcendental metric functions, at finite quadrupole and to first order
    about Kerr;
  - (iv) the dynamical counterpart in TS2: transient chaos localised at the capture edge, with a matched Kerr control,
    and a chaotic saddle at one level.

## 2. The spacetimes
- TS2 from its Ernst potential, rational parameterisation p = (1 − t²)/(1 + t²) so that every component is rational;
  each metric verified vacuum exactly (Ernst equation; R_ab = 0 at random rational points; a perturbed metric must
  fail; mass and spin read off). [RESULTS §148, §152; TS2_METRIC.md]
- MN in Weyl–Papapetrou form with the q-anomaly subclass; non-rational (√ and exponentials of rational functions);
  vacuum verified by a formal differential-field test. [MN_METRIC.md]

## 3. Method A: ansatz-free prolongation bound for invariant Killing tensors [§149, §151]
- The valence-d invariant KT ansatz I = Σ_m m(p) K_m(x, y). The M-th prolongation at a regular point P; jet
  injectivity at order d + 1; #cols − rank is an upper bound; equality with the trivial count proves nonexistence
  locally, for smooth coefficients of any form.
- Exactness: GF(p) with rank_p ≤ rank_Q.
- MN: points with R0 rational; the exponentials' constants are powers of one transcendental T; T ↦ t ∈ GF(p)* is
  sound, while independent random values would not be (multiplicative dependence).
- Validation by reproduction: Kerr Carter (2, 5, 8, 14); Kruglikov–Matveev's ZV matrix; Vollmer's TS2 p = 3/5
  valence-7 count; sabotage controls in both directions; Ricci-from-series for MN.
- Independent implementations: a second, code-independent implementation reproduced TS2 (valence 1–10) and MN
  (valence 1–10), and the MN first-order test (valence 1–6). It ran on the same Python stack, so independence is in
  the code only. [placeholder: the Bridge V10, V10-MN, V17; relayed]

## 4. Results A: no hidden polynomial symmetries
- Table 1: TS2 p = 4/5, valence 1–10, bound = trivial (2, 4, 6, 9, 12, 16, 20, 25, 30, 36), at four points; p = 3/5,
  valence 8–10. Robust to M = d + 1 and to the prime.
- Table 2: the TS2 p-sweep, 8 new p, valence 1–8, at two points; Kerr Carter recovered at every p.
- Table 3: MN p1, p2, valence 1–10.
- Table 1b (global, box-bounded complement to the local bounds): TS2 p = 4/5 has no irreducible KT at ranks 2, 3,
  4 exactly on two primes in {x^a y^b / L^d} (§148), and none at rank 6 in the box {x^a y^b / L³}, 34 × 34, all four
  parity sectors, by a sampled exact rank (§149, B1). Three methods sharing no linear algebra agree at rank 6.
- Table 3b: MN to first order in its quadrupole β about Kerr (§153): the number of Kerr KTs that extend to first order
  is the trivial floor 2, 4, 6, 9, 12, 16 at valence 1–6 (Kerr itself: 2, 5, 8, 14, 20, 30), at two parameter
  points, two jet points, two draws. Carter, Carter² and Carter³ all die, so a surviving rational Carter would need
  pole order ≥ 3. Validated by reproducing the published pole-order ladder of §141 (Carter dies, Carter² survives,
  etc. for the shape deformations). Ceiling: first order in β (analytic in β with a Kerr root).
- Scope paragraph: invariant class only (tensors that are not invariant under ∂_t, ∂_φ, e.g. e^{λt+imφ} or Jordan
  chains under the Killing vectors, are not covered; v0 attributed this route to Kruglikov–Steneker, but their 2022
  paper does not treat it, so no citation), local, rank ≤ 10, finite parameter points.

## 5. Method B: chaos diagnostics with a matched Kerr control [§150]
- Reduced 2-DOF Hamiltonian; exact rational RHS compiled; DP5(4) in double; a double-double GBS for 32 digits.
- Detectors: frequency drift and excess stretching, with an AND rule; a complex-signal check; Kerr at matched
  separatrix distance at every level.
- Outcome-only measures: the fate map; the uncertainty exponent α (fit validated on synthetic smooth and Cantor
  boundaries).

## 6. Results B: transient chaos at the capture edge
- Dubeibe's level reproduced: the far field is regular (Fig. sections).
- Thin chaotic layers at the plunge boundary: TS2 confirmed counts against Kerr 0, ε-matched.
- Fate map (Fig.): Kerr switches survive/plunge once across its window; TS2 switches 370 times, and 53 times in a 10×
  zoom.
- α: TS2 0.04–0.16 against Kerr ≈ 1 at three levels, both p, two horizons (Table 4). An independent reproduction
  agrees in all cells. [placeholder: the Bridge V12]
- High precision: outcomes determinate at 32 digits; sensitivity down to ε ≈ 10⁻¹⁴.
- **The pre-registered crossover test returned "finite-time artefact".** That is stated as is; the post-hoc lifetime
  reading follows, labelled.
- **Homoclinic tangle (§154, pre-registered 7c43e03 + addendum 1).** At the capture-edge level, the unstable
  spherical-type orbit (Kerr: exactly the boundary point, matching the analytic spherical orbit to 8e−28) has a
  TRANSVERSE homoclinic point in TS and a zero splitting in Kerr. Controls: the forced pendulum vs Melnikov, and
  precision and seed checks. So a horseshoe, and hence a chaotic saddle, exists at this (E, L) level (numerically).
  The link to the §150 window (0.11 above the orbit) is not checked, so the window keeps the finite-horizon wording. A rigorous interval-arithmetic version is possible.
- The earlier lifetime-interval test (471f76c) was VOID: the Kerr control failed, and the R2 rerun stopped at its Kerr
  gate. Lifetimes near a separatrix are blurred over a width ~√tol. We report it as a methods lesson; the tangle test
  sidesteps it.
- Why sections mislead: chaotic and regular orbits both trace near-curves at 300 crossings, because the layers are thin.

## 7. Discussion
- What the two halves say together: no polynomial integral, plus localised transient chaos, is consistent with
  non-integrability. Independent Morales–Ramis / Ziglin obstructions near the equatorial orbit at the §150 levels are reported by a sister
  project [placeholder: Quantum 1b8c3f5; relayed, not verified here, and not a claim of this paper].
- What is NOT claimed: no all-rank statement; no global KT statement (beyond the box-bounded Table 1b); no EMRI-orbit
  statement; no strict-limit fractal for the §150 window.
- **The edge-link chain (§155–§157), stated plainly.** Three pre-registered attempts asked whether the window's
  switches are strands of the §154 orbit's stable manifold. Net: the one-way gate holds; the slope instrument that
  tells a strand from an artefact is validated on Kerr; the window's switches are decided only after ~200–290 chaotic
  crossings, beyond pointwise resolution in 32-digit arithmetic. Neither established nor refuted. The grade is kept
  visible: each version needed a post-failure amendment before any TS run of it.
- Related fleet work, kept separate (placeholder; relayed, not part of this paper's claims): the axis
  normal-variational-equation classification ("only Kerr", our independent check §158) and its twist-family extension
  (§159; the Bridge's V26 with addendum K). If cited, cite with its own caveat line: one (E, spin), a 50-digit
  argument principle, not an interval certificate. Whether TS2 and MN fall under that classification is NOT checked
  here and must not be implied.
- Relation to tabula's TS2 measurements [placeholder; terminology aligned; content only via the Bridge].
- Literature context: Ramond 2026 (a body with a tidally induced quadrupole moving in Kerr: analytic non-integrability, fractal basin boundaries in escape-time maps; verified at abstract);
  Shoom 2017 (photon sphere → fractal basin boundary, with box-counting dimension and uncertainty exponent, in a
  Schwarzschild black hole distorted by an external quadrupole; verified, abstract); Lai & Tél 2011 (the transient-
  chaos framework); Lau, Finn & Ott 1991 (nonhyperbolic scattering with KAM tori gives a fractal dimension near 1,
  i.e. an uncertainty exponent near 0; the link to our small α is our reading, not their statement).

## Conventions and units (aligned with tabula's terminology, 2026-11-17; terms only, no results exchanged)
- TS δ = 2 with (p, q), p² + q² = 1, prolate (x, y). THIS draft uses σ = 1 (so m = 2/p for TS2, m = 1/p for Kerr);
  tabula works in m = 1 with σ = p/2. L and p_x differ by the factor σ, so state units explicitly and compare only
  coordinate-invariant quantities (e.g. α).
- Terms: "timelike geodesic" on first use, "orbit" after; "Poincaré section y = 0 crossed upward (p_y > 0), coordinates
  (x, p_x)"; "unstable circular orbit" / "saddle-centre"; "Lyapunov orbit"; "open level" vs "closed pocket";
  "separatrix" (the Kerr homoclinic loop); "homoclinic tangle"; "chaotic saddle"; "plunge (capture)" and "plunge
  boundary". "Capture edge" in our headline = the plunge boundary. α = 1 − D for the singular set of the escape-time
  function along a line.
- BLINDING: tabula's §200 also measures an uncertainty exponent near the plunge boundary. No α numbers are exchanged
  until the Bridge arranges a comparison (embargo in tools/EMBARGOES.json).

## Reproducibility
- Environment, commands and logs: ENVIRONMENT/README.md.
- All verdicts pre-registered (commit hashes listed per section in RESULTS).

## Reference checklist (checked 2026-11-17 at arXiv abstract/HTML; "verified" = the claim was read in the source text)
| ref | used for | status |
|---|---|---|
| Dubeibe, Pachón & Sanabria-Gómez, PRD 75, 023008 (2007), gr-qc/0701065 | the integrability claim | **verified (body).** §III.1 and the conclusions call TS δ=2 motion "completely integrable" / "only integrable geodesics", from Poincaré sections (Fig. 1b, E = 0.94, L = −3.12; other (E, L) not listed; q not given). NOTE: the paper's chaos result is for the deformed Manko et al. solution (b ≠ 0), not TS2. Say both. |
| Brink, PRD 81, 022002 (2010), arXiv:0911.1595 | 4th-order KT suggestion | **verified (intro):** numerical experiments suggest "a large number of SAV spacetimes may possess a fourth-order Killing tensor". MN is not named in the part read. Whether his ref [6] is Gair–Li–Mandel: **unverified**. |
| Gair, Li & Mandel, "Observable properties of orbits in exact bumpy spacetimes", PRD 77, 024035 (2008), arXiv:0708.0628 | MN orbits | **verified (abstract):** most MN geodesics have an approximate 4th constant; it can be lost (chaos) for some orbits in OBLATE MN. Not "ergodic". |
| Kruglikov & Matveev, "Nonexistence of an integral of the 6th degree in momenta for the Zipoy–Voorhees metric", PRD 85, 124057 (2012), arXiv:1111.4690 | ZV δ = 2, no polynomial integral of degree ≤ 6 | **verified (body, 2026-11-21):** prolongation on jets (§2.1); degree-6 matrix 1680 × 1584, which our validation reproduces. Degree 7 excluded "with other methods" (not shown). |
| Vollmer, "Killing tensors in stationary and axially symmetric space-times", J. Geom. Phys. 115, 28–36 (2017), arXiv:1602.08968 | TS no KT to valence 7 (also C-metric to 9, ZV to 11) | **verified (body, 2026-11-21):** δ = 2, p = 3/5 (q = 4/5); all three theorems exclude only tensors in involution with dt, dφ and the metric. Our reproduction matches his count. |
| Maciejewski, Przybylska & Stachowiak, "Nonexistence of the final first integral in the Zipoy–Voorhees space-time", PRD 88, 064003 (2013), arXiv:1302.4234 | ZV: no additional meromorphic integral | **verified (abstract); body read in full by the Bridge, 2026-11-21 (relayed, not re-read here):** meromorphic non-integrability of ZV geodesics for δ = 2 at all energy levels (Theorem 3), and a check of δ = 1/2. Method: the first-order NVE along an equatorial radial geodesic (y = 0, p₃ = 0; p₃ = 1 at the special levels), reduced to ξ″ = rξ, then Kovacic. No classification over δ and nothing on the axis NVE. Vollmer notes they treat analytic integrals. |
| Ramond 2026, arXiv:2607.27129 (preprint) | closest comparison | **verified (abstract):** a non-spinning body with a TIDALLY INDUCED QUADRUPOLE moving in Kerr (not "tidally perturbed Kerr"); analytic non-integrability for generic couplings/spin; fractal basin boundaries in escape-time maps. |
| Contopoulos, Harsoula & Lukes-Gerakopoulos, "Periodic orbits and escapes in dynamical systems", CMDA 113, 255–278 (2012), arXiv:1203.1010 | MN escapes / chaotic scattering | **verified (abstract, intro):** escapes to the central bumpy black hole; "plunging" is our word, not theirs. Also studies a coupled-oscillator system. |
| Shoom, "Metamorphoses of a photon sphere", PRD 96, 084056 (2017), arXiv:1708.00019 | fractal photon boundary | **verified (abstract):** distorted Schwarzschild (external quadrupole), not a non-Kerr vacuum; photon sphere becomes a fractal basin boundary. |
| Tomimatsu & Sato, PRL 29, 1344 (1972); Prog. Theor. Phys. 50, 95 (1973) | §2 | **verified (metadata).** |
| Manko & Novikov, "Generalizations of the Kerr and Kerr–Newman metrics possessing an arbitrary set of mass-multipole moments", CQG 9, 2477 (1992) | §2 | **verified (metadata).** The paper has two metrics; say which (the vacuum one). |
| ~~Kruglikov & Steneker (non-invariant KTs)~~ | scope | **REMOVED:** their 2022 paper (CQG 39, arXiv:2207.03474) is on Koutras–McIntosh / pp-wave KTs, not on non-invariant tensors. The scope statement stays, uncited. |
| Lai & Tél, *Transient Chaos: Complex Dynamics on Finite Time Scales*, Springer AMS 173 (2011); Lau, Finn & Ott, PRL 66, 978 (1991) | framework | **verified (catalog; abstract):** Lau–Finn–Ott give strong evidence for dimension 1 in KAM-type nonhyperbolic scattering. "Stickiness → small α" is our paraphrase. |

---

## v1 audit (2026-11-21): claims checked against registered results, and what is not backed
Every number in the abstract and in §4 and §6 was traced to a registered RESULTS section: §148 (ranks 2–4 exact),
§149 (valence 1–10 counts, four points, B1 rank-6 box), §150 (α 0.04–0.16, 370/53 switches, 1e−14, the "finite-time
artefact" verdict, Dubeibe reproduced), §151 (MN valence 10), §152 (the p sweep 0.28–0.96), §153 (MN first order,
added in v1), §154 (the tangle), and §155–§157 (the edge link, added in v1).

**Not backed by a registered result here (kept only as labelled placeholders):**
1. All independent reproductions (the Bridge V10, V10-MN, V11, V12, V17, V20): relayed, not verified here.
2. The Morales–Ramis / Ziglin obstructions at the §150 levels (Quantum 1b8c3f5): relayed.
3. tabula's TS2 measurements: placeholder only, and embargoed.
4. Any link to the "only Kerr" axis-NVE classification for TS2 or MN: not checked anywhere; not to be implied.
5. "Globally" for the jet nulls: the §149 ceiling says globalisation by analytic continuation is not written out. The
   draft says "local" and must keep saying it.

**Corrections made in v1:** the Kruglikov–Steneker attribution for non-invariant tensors was wrong and is removed
(this also affects RESULTS §149's ceiling wording, corrected there by note); "first KT nulls for MN" softened to "no
earlier result found"; Vollmer's involution restriction stated; Contopoulos et al. described as escapes, not
plunges; Shoom's spacetime named correctly.

**Still open before circulation:** MPS's method (body not read); a real figure set; the combined-paper decision
(the user's). The §150 window statement stays "finite-horizon" (the edge link is not established).
