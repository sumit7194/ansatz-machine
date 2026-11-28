# Region A by analyticity in k: a design note, v2 (the Bridge's ruling (C); text only, nothing runs)
**Office ansatz-machine. v1 2026-11-29 (committed 6dd2482). v2 2026-11-29, after two hostile reads (Neon, and an independent Opus reader on the same prompt), relayed and graded by the Bridge.** Both reads confirmed the core: the group lemma, and the monodromy lying in the Galois group (no Fuchsian hypothesis needed). v2 answers all ten of the Bridge's points. **Changed paragraphs carry [v2, point n]**, so the readers can re-read only those.

| point | what was raised | where v2 answers it |
|---|---|---|
| 1 | closed lifts; name Γ and K | §1.1 (Γ, K, the closed-lift lemma), §2 Q1; certified in item 1's check (f) |
| 2 | BASED homotopy of the pair, the stem, the normalisation path, b vs R0 | §1.2 (b = R0); §2 Q2 |
| 3 | point certificates of all four functions on every chain piece meeting [3, 4] | §1.4, §2 Q2 |
| 4 | the normalisation integral: α(k), uniform decay, the branch at ∞ | §1.3 |
| 5 | certify non-vanishing directly, not by tracking roots | §1.2, §4 item 1 (as built: box covers; sweeps dropped) |
| 6 | p± on the CONTINUED branch; one uniform complex neighbourhood | §1.2, §1.3 |
| 7 | the NVE in sl₂ | §1.1 |
| 8 | the Jensen number overstated | §2 Q3 (dropped) |
| 9 | scope of the theorem; D inside [3, 4]; no accumulation claim at 30/7; numerics for all four functions | §2 Q3, §3 |
| 10 | "holomorphic on a connected complex neighbourhood", not "real-analytic" | throughout (§1.3, §1.4) |

**Short answer (unchanged in substance).**
- At spin 3/5 the circle-picture words define ONE family of monodromies, holomorphic on a connected complex neighbourhood of a real interval J ⊃ [3, 4]. J also contains route (i)'s certified [2.9, 3.0].
- So each of F, tr M0, tr M1 and P_fin(tr M1) vanishes only at finitely many k in [3, 4].
- Hence non-integrability holds on [3, 4] except possibly at a finite set D, relative to the applicability chain.
- No k-uniform integration in region A is needed. What is needed is item 1's loop-continuity certificate (C2_AN_REGISTRATION.md with addendum C2-AN-1), which certifies no monodromy value.

## 1. The argument, made self-contained [v2]
### 1.1 The equation, its Riemann surface, and the group [v2, points 1 and 7]
**The equation.** NVE1 in the variable v, MRS §2 and Lemma C(b): v″ + q(z; k) v = 0, with q = (3/16)(P′/P)², P = E² − f0⁻ and f0⁻ = f0/(f0² + c0²).
- As a first-order system Y′ = [[0, 1], [−q, 0]] Y the matrix is trace-free, so every monodromy has det = 1 (Abel). It lies in SL₂.
- The first-derivative term was removed by MRS Lemma C(b)'s algebraic gauge ξ1 = f0^{1/2} P^{−1/4} v, which leaves the identity component of the Galois group unchanged. **[point 7]**

**The Riemann surface [point 1].**
- Let ρ(k) = max(a, a·max|w±(k)|^{1/2}), where w± are the roots of B(w, k) = (90 − 21k)w² − (60 − 18k)w + (10 − k). This is the modulus of c0″'s farthest singular point: ±ia and the four zeros ±a√w± of B(z²/a², k).
- On Ω_k = {|z| > ρ(k)}, c0″ = −√(8/5)·a³·√B/(z² + a²)³ is single-valued and holomorphic, including at ∞:
  - B has an even number (four) of zeros inside, so √B returns round any circle in Ω_k;
  - √B ~ √α(k)·z²/a² at ∞, so c0″ = O(z⁻⁴).
- Hence c0′ = −∫_z^∞ c0″ and c0 = ∫_z^∞ (s − z) c0″ ds are single-valued holomorphic on Ω_k. Round any circle in Ω_k, the changes ∮c0″ and ∮s c0″ are −2πi times residues at ∞ of O(z⁻⁴) and O(z⁻³) terms, hence 0.
- **Γ_k := Ω_k minus the zeros of P and of f0² + c0² (r±, p±, …) and minus the rod endpoints (f0 = 0; ordinary for NVE1, removed only for Proposition 2, MRS §5c).**
- **K := M(Γ_k)**, the meromorphic functions on Γ_k. Then q ∈ K.
- Every closed loop in Γ_k based at R0 therefore has a CLOSED lift: q, c0 and c0′ return along it, and its monodromy is an element of the Galois group of NVE1 over K. (Morales–Ramis' Γ is the orbit on the double cover y² = P; MRS Lemma C relates the two, with the same identity component.)
- **Both words lie in Γ_k for k ∈ J:**
  - the circle |z| = R0 = 1.35 needs ρ(k) < R0. This is item 1's check (f), certified per k-cell: it holds through 4.1 and refuses at 4.2, so k_cross ∈ (4.1, 4.2) at 3/5;
  - each capsule lasso lies in the square 2 ± 1.15(1 + i), which is disjoint from {|z| ≤ ρ(k)} and certified free of c0's singular points per cell;
  - both words avoid r±, p± and the other zeros by item 1's direct box covers.

**The group lemma (both reads: correct).** Let G = ⟨M0, M1⟩ ⊂ SL₂(ℂ). If tr[M1, M0] ≠ 2, tr M0 ≠ 0 and P_fin(tr M1) ≠ 0, then the Zariski closure of G is SL₂. Here P_fin is the polynomial whose roots are the set T_fin of traces of elements of the binary tetrahedral, octahedral and icosahedral groups.
- **Proof.** The proper algebraic subgroups are reducible, imprimitive or finite:
  - **reducible** means a common eigenvector, which gives tr[M1, M0] = 2;
  - **imprimitive** (in the normaliser of a torus): every element is diagonal or has trace 0. With tr M0 ≠ 0 and tr M1 ≠ 0 both are diagonal, so they commute, so F = 0;
  - **finite primitive:** every trace is in T_fin.
- **[v2, from the reads]** 0 ∈ T_fin, so P_fin(tr M1) ≠ 0 already gives tr M1 ≠ 0. The separate condition is redundant and is dropped.
- **The bad conditions are therefore three:** F = 0, tr M0 = 0, P_fin(tr M1) = 0.
- The Galois group over K contains the monodromy group, so it too is Zariski-dense in SL₂: G_v⁰ = SL₂, and MRS applies.

### 1.2 Continuing the based pair in k [v2, points 2, 5 and 6]
- **b = R0.** In the circle picture the normalisation point and the base point coincide: c0 is normalised from +∞ along [R0, +∞), and both words start and end at R0. There is no segment b → R0. **[point 2]**
- **Links.** Item 1 fixes the words on overlapping real k-intervals J_i:
  - M0 is the same 96-gon for every link;
  - M1 for link i is the capsule lasso of k_c,i.
- **For every k ∈ J_i, item 1 certifies directly on box covers that G1 = E²(f0² + c0²) − f0, G2 = f0² + c0², B and z² + a² are nonzero:**
  - on every edge of both words;
  - with c0 the branch CONTINUED along that word from R0 (along the polygon for the circle; the single-valued square for the lasso);
  - and Re P > 0 on [R0, +∞) for the normalisation.
- **No root is tracked as the certificate [point 5].** An unexpected extra zero would make a box fail. The zeros of G1 and G2 are exactly the zeros of P and of f0² + c0² on the continued sheet **[point 6]**.
- **Gluing.** On each overlap O_i, the straight-line homotopy from L_i to L_{i+1}, vertex to vertex, fixes R0 (vertex 0) and moves the stem with everything else. Its image lies in the union of the quadrilaterals conv(L_i[j], L_i[j+1], L_{i+1}[j+1], L_{i+1}[j]). Each quadrilateral is covered by boxes certified nonsingular for every k ∈ O_i.
  - So for each k ∈ O_i the based pairs (M0, M1^(i)) and (M0, M1^(i+1)) are the same elements of π₁(Γ_k, R0).
  - So the two monodromy pairs are equal, not merely conjugate, and tr[M1, M0] agrees. **[point 2: the pair, not L1 alone]**

### 1.3 Holomorphy in k on one connected complex neighbourhood [v2, points 4, 6 and 10]
**The normalisation [point 4].**
- α(k) = 90 − 21k is B's leading coefficient in w, and α > 0 on J ⊂ (0, 30/7), certified per cell by (f).
- √B = (z²/a²)·√α·(1 + β(k)a²/z² + γ(k)a⁴/z⁴)^{1/2}, with β = −(60 − 18k)/α and γ = (10 − k)/α. The principal root of the bracket is holomorphic in (z, k) for |z| ≥ R1 (some R1 ≥ R0) and k in a complex neighbourhood U of J. This defines √B at +∞ holomorphically in k.
- On [R0, ∞) × U: B ≠ 0 (Re P > 0 for real k in the cells, then openness), and |c0″| ≤ C |z|⁻⁴ uniformly on [R1, ∞) × U (compact U). So the integrals defining c0(R0) and c0′(R0) converge uniformly, and are holomorphic in k on U (Weierstrass). This is Lemma K's step 3 with "|k| < δ" replaced by "k ∈ U".

**Compactness [point 6].**
- For each real k* ∈ J, the coefficient A(z; k) is holomorphic on a neighbourhood of (the two words, the normalisation path) × {k*}. All nonvanishing conditions hold on the compact words × {k*}, so they hold on (the words) × D(k*, r(k*)).
- J is compact, so finitely many such discs cover it. Their union U_J is a connected open neighbourhood of J; it is connected because each disc meets the real interval.
- On each link's part of U_J the monodromies are holomorphic (Picard iteration: holomorphic iterates, uniformly convergent). On overlaps they agree, by the gluing of §1.2 at real k plus the identity theorem.
- **So F, tr M0, tr M1 and P_fin(tr M1) are HOLOMORPHIC on the connected complex neighbourhood U_J of J [point 10].** They need not be real on J; the traces in region B are not.

### 1.4 Finiteness, and the point values [v2, points 3 and 10]
- **The argument.** A function holomorphic on a connected open set and nonzero at one point has isolated zeros, so only finitely many in any compact subset.
- **The one chain piece.** If item 1's chain is unbroken (all 11 links and all 10 gluings), there is ONE piece J = [2.895, 4.005]. It contains route (i)'s certified segment [2.9, 3.0], with the same words (link 0's lasso equals route (i)'s 59/20 entry vertex for vertex).
- **The point values [point 3].** Route (i) certifies, for every real k there, F ≠ 0, tr M0 ≠ 0 and tr M1 ∉ [−2, 2]. Since T_fin ⊂ [−2, 2], that also gives P_fin(tr M1) ≠ 0. So all four functions are nonzero at points of the piece.
- **If the chain breaks at some O_i,** each piece meeting [3, 4] needs its own rigorous point values of all three conditions. A piece wholly inside (3, 4) would need a fixed-k rigorous evaluation there.
  - That is feasible: route (i)'s v6 node evaluations are rigorous at a point k (Arb walks with certified enclosures). What failed in region A was k-UNIFORM enclosure, not point evaluation.
  - This would be a ruling, and is not needed if the chain is unbroken.
- **The conclusion:** D := {k ∈ [3, 4] : F(k) = 0 or tr M0(k) = 0 or P_fin(tr M1(k)) = 0} is finite, since [3, 4] is a compact subset of J's interior.

## 2. The Bridge's questions (revised)
### Q1. Collisions and branch structure [v2, point 1]
- **The only collision of c0's singular points for real k ∈ (0, 30/7) is at k = 4,** where B = 6(w + 1)² and its zeros meet ±ia. It lies inside |z| < R0, so it is harmless: the circle's lift closes for every k with ρ(k) < R0, which (f) certifies per cell across k = 4.
- **The real limit of the circle picture** is the outer pair ±a√w₋ crossing |z| = R0: certified to lie in (4.1, 4.2) at 3/5.
- **At the endpoints:**
  - at k → 0 the B zeros pinch ℝ at u = ±1/√3, far from every word (Lemma K);
  - at k = 30/7, α → 0, two zeros escape to ∞ and the traces are not analytic. That endpoint is not in J.
- **r±, p± and any other zeros of P or f0² + c0²** are excluded from the words, the homotopy regions and the normalisation path by direct box certificates, never by tracking.

### Q2. The boundaries at k = 3 and k = 4 [v2, points 2 and 3]
- **k = 3 is not a construction boundary;** it is only where route (i)'s reach ends. Item 1's gluing certifies that the based pair continues across it.
- **k = 4 (the A/B switch) changes the words.** But J ends at 4.005 inside the circle picture, so [3, 4] never crosses the switch. Region B's certificates stand on their own words. Point 4 itself is covered both by J (the circle picture) and by region B's U00 segment.

### Q3. The theorem [v2, points 8 and 9]
**Theorem (target; relative to the applicability chain: Proposition 2, Lemma C, MRS §5b, the conventions of MRS §5).** Fix spin 3/5 and E = 4/5.
- For every real k ∈ [3, 4] outside a finite set D ⊂ [3, 4], the identity component of the differential Galois group of NVE1 along the lower-axis orbit Γ0 is SL₂(ℂ).
- Hence the t-reduced geodesic Hamiltonian H_E admits no first integral that is independent of H_E and p_φ, in involution with them, and meromorphic in a neighbourhood of the complexified orbit Γ0 (MRS §1). Here H_E is MRS §1's system: three degrees of freedom on (x, y, z, p_x, p_y, p_z), on the level H_E = −μ²/2.
- Equivalently, on T*M: no fourth integral beyond H, p_t and p_φ.

**Notes on scope.**
- **[point 9, a note on wording]** The Bridge's "reduced 2-DoF system" is not the system MRS §1 (corrected 2026-11-24) applies the theorem to. MRS says not to reduce by p_φ, because the S¹ action is singular on the axis. The statement above uses MRS's system.
- **Combined with the certified stretches,** the same conclusion holds for every k ∈ (0, 30/7] outside D ∪ (any stretch not yet certified at 3/5, as of the region-B production).
- **[point 9]** D is defined inside [3, 4]. **No finiteness is claimed near 30/7:** zeros of these functions could accumulate at 30/7, where they are not analytic, so the near-30/7 gap needs the certified sliver and the dyadic chain, not this template.
- **[point 9] Numerically D is empty for all three conditions,** not only F. The gap-B counts (GAPB_PREREGISTRATION.md, 50-digit argument principle over R = [−10.5, 4.05] × [−1, 1]i, spin 3/5, E 4/5) give:
  - count(F) = 2 (the double zero at k = 0);
  - count(tr M0) = count(tr M1) = 0;
  - post hoc, count(tr M1 − s) = 0 for every s ∈ T_fin, with min |tr M1 − s| = 1.16.
  These are floating-point counts, not certificates.
- **[point 8] The Jensen number is dropped.** v1's "N of the order of 100" was overstated: the Opus reader estimates N ~ 260–2900. A sound version would need discs centred at certified points and complex-k loop certification, which this design does not do.

## 3. What it would NOT do [v2, point 9]
- **It would not remove D.** D is finite, not shown empty. Removing it needs a k-uniform certificate on [3, 4] (the route that failed), or a certified argument-principle count on a complex k-contour around [3, 4].
- **It would not make finiteness statements near 30/7, or near any endpoint of J.**
- **It would not be stronger than the applicability chain,** nor reach other energies or spins without their own item-1 chains. The template carries over, but each spin's J, words and point values must be certified separately.
- **It would not change the claim's physical scope:** not black holes, off-axis regularity unchecked, null geodesics untested.

## 4. What is built and what remains
1. **Item 1 (the loop chain).** Registered (C2_AN_REGISTRATION.md, addendum C2-AN-1); code e73b3e4; non-author read in progress, then one run at 3/5. It certifies (a)–(d) and (f) of §1.1–1.2. Krawczyk sweeps are dropped as certificates **[point 5]**.
2. **Item 3 (the lemmas in MRS_SECTION.md), self-contained as Neon advises:**
   - the group lemma (§1.1);
   - the closed-lift lemma for Γ_k (§1.1);
   - the based-pair gluing lemma (§1.2);
   - the holomorphy-on-U_J lemma (§1.3);
   - the finiteness corollary (§1.4).
   Then their read. Item 3 is not built on any point the re-reads flag as MAJOR.
3. **Precedent.** Neither reader knows an exact precedent for "one rigorous point value plus analyticity in the parameter, giving all but finitely many". Neon's warning stands: referees will scrutinise the gluing lemmas, hence their self-contained write-up.
