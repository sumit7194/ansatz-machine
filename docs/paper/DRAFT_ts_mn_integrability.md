# DRAFT v0 — Hidden symmetries and transient chaos in two non-Kerr stationary vacua: Tomimatsu–Sato δ = 2 and Manko–Novikov

*Working draft (ansatz-machine, 2026-11-17). Not for circulation. Sources are this repo's RESULTS §148–§152 only.
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
- MN up to valence 10 at two parameter points of opposite anomalous quadrupole.

The MN result excludes, at these points, the fourth-order generalised Carter constant suggested numerically by Brink.
In TS2, a separatrix-matched comparison with Kerr locates the dynamical consequence: geodesics near the capture
(survive/plunge) edge show transient chaos. Kerr shows none under identical tests. The survive/plunge boundary has an
effective uncertainty exponent α ≈ 0.04–0.16 for TS2 against α ≈ 1 for Kerr, and it remains fractal-like down to
initial-condition scales ε ≈ 10⁻¹⁴ in 32-digit arithmetic. Poincaré sections at 300 crossings do not discriminate,
which explains the earlier report of complete integrability. We state exactly what is and is not claimed: rank-bounded,
local and invariant-class for the symmetry nulls; finite-horizon for the chaos; and no strict-limit fractal.

## 1. Introduction (outline)
- Kerr's Carter constant, why integrability matters (EMRI waveforms), and non-Kerr test spacetimes.
- Prior claims:
  - Dubeibe, Pachón & Sanabria-Gómez 2007 call TS2 "completely integrable" from regular sections
    (gr-qc/0701065) **[verify]**;
  - Brink, *Spacetime Encodings IV* (arXiv:0911.1595), suggests that many SAV spacetimes may carry a 4th-order KT
    **[verify]**;
  - Gair, Li & Mandel 2008 report MN chaos **[verify]**;
  - Contopoulos, Harsoula & Lukes-Gerakopoulos 2012: chaotic scattering of plunging MN orbits **[verify]**.
- Methods lineage: Kruglikov–Matveev arXiv:1111.4690 (ZV) **[verify]**; Vollmer arXiv:1602.08968 (TS2, p = 3/5,
  valence ≤ 7) **[verify]**.
- Our contributions:
  - (i) valence-10 nulls for TS2 at a new parameter point, and beyond Vollmer at his;
  - (ii) a parameter sweep;
  - (iii) the first KT nulls for MN, with a sound treatment of its transcendental metric functions;
  - (iv) the dynamical counterpart in TS2: transient chaos localised at the capture edge, with a matched Kerr control.

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
  (valence 1–10). It ran on the same Python stack, so independence is in the code only. [placeholder: the Bridge
  V10, V10-MN]

## 4. Results A: no hidden polynomial symmetries
- Table 1: TS2 p = 4/5, valence 1–10, bound = trivial (2, 4, 6, 9, 12, 16, 20, 25, 30, 36), at four points; p = 3/5,
  valence 8–10. Robust to M = d + 1 and to the prime.
- Table 2: the TS2 p-sweep, 8 new p, valence 1–8, at two points; Kerr Carter recovered at every p.
- Table 3: MN p1, p2, valence 1–10.
- Scope paragraph: invariant class only (Kruglikov–Steneker non-invariant KTs not covered **[verify]**), local, rank
  ≤ 10, finite parameter points.

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
- [PENDING] The lifetime-interval (topological-entropy) test, pre-registered 471f76c. Its outcome decides whether this
  section may speak of a chaotic saddle / fractal in the limit, or only of finite-horizon fractal-like structure.
- Why sections mislead: chaotic and regular orbits both trace near-curves at 300 crossings, because the layers are thin.

## 7. Discussion
- What the two halves say together: no polynomial integral, plus localised transient chaos, is consistent with
  non-integrability. Independent Morales–Ramis obstructions exist [placeholder: Quantum, relayed].
- What is NOT claimed: no all-rank statement; no global KT statement; no EMRI-orbit statement; no strict-limit fractal
  unless the pending test supports it.
- Relation to tabula's TS2 measurements [placeholder; terminology aligned; content only via the Bridge].
- Literature context: Ramond 2026 (tidally perturbed Kerr, fractal basin boundaries, no Kerr control) **[verify]**;
  Shoom 2017 (null rays) **[verify]**; Lai & Tél 2011 and Lau, Finn & Ott 1991 (stickiness → small α) **[verify]**.

## Reproducibility
- Environment, commands and logs: ENVIRONMENT/README.md.
- All verdicts pre-registered (commit hashes listed per section in RESULTS).

## Reference checklist (each must be opened at the source before citing)
| ref | used for | status |
|---|---|---|
| Tomimatsu & Sato 1972/73 (original TS solutions) | §2 | [verify] |
| Manko & Novikov 1992 | §2 | [verify] |
| Gair, Li & Mandel 2008, PRD 77, 024035 | MN form, MN chaos | [verify] |
| Dubeibe, Pachón & Sanabria-Gómez 2007, gr-qc/0701065 | the integrability claim | [verify] |
| Brink 2009, arXiv:0911.1595 | 4th-order KT suggestion | [verify] |
| Kruglikov & Matveev, arXiv:1111.4690 | prolongation method, ZV | [verify] |
| Vollmer 2016, arXiv:1602.08968 | TS2 p = 3/5 to valence 7 | [verify] |
| Kruglikov & Steneker (non-invariant KTs) | scope | [verify] |
| Contopoulos, Harsoula & Lukes-Gerakopoulos 2012, CMDA 113, 255 | MN chaotic scattering | [verify] |
| Ramond 2026, arXiv:2607.27129 | closest comparison | [verify] |
| Shoom 2017, PRD 96, 084056 | fractal photon boundary | [verify] |
| Lai & Tél 2011, *Transient Chaos* | framework | [verify] |
| Lau, Finn & Ott 1991 | stickiness → α → 0 | [verify] |
| Maciejewski, Przybylska & Stachowiak 2013, PRD 88, 064003 | ZV non-integrability (context) | [verify] |
