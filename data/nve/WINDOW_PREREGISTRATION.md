# The window k ∈ [3.95, 30/7 − 10⁻¹²]: half-plane argument-principle count (pre-registration, 2026-11-21)

**Ask.** The Bridge GO (2026-11-21), after §161: "endpoint + continuity" covers only an unknown neighbourhood of 30/7,
and gap B stops at 4.05.

**Fixed.** Spin a = 3/5, M = 1, E = 4/5. The lower-axis first-order NVE as in §159 / gap B / §161.
- Region R = [3.95, 30/7 − 10⁻¹²] × [−0.25, 0.25]i. Its boundary is traversed counter-clockwise, sampled at spacing
  ≤ 0.025, and refined until |Δarg| ≤ π/4 (at most 5 levels).
- R excludes the branch point of k ↦ c0 at 30/7 (terms c4^{3/2} and c4² log c4).

## The engine (`scripts/_nve_lower_hp.py`), and why it is needed
- Near 30/7 the Laurent radius ρ_c → ∞ (one √B root escapes along the imaginary direction), so gap B's circle picture
  and its Laurent c0 are unavailable.
- Instead: c0″ = −√(N_k/lcD)/(z² + a²)³, with N_k the exact radicand numerator (linear in k) written as a product of
  principal square roots over its roots ζ_i.
- The sign and branch match the Laurent convention on the positive real axis at large z.
- Constants by quadrature: c0′(2) = −∫₂^∞ c0″ and c0(2) = ∫₂^∞ (t − 2)c0″.
- A 220-term Taylor series about z = 2 gives c0 and c0′. Local Taylor data of c0″ at any point come directly from N_k.
- **Guards, at every k used:** no cut ray {ζ_i − t} crosses the working region or the real ray [1, ∞); and every loop
  point lies within 0.6 R_c of z = 2, where R_c is the distance to the nearest ζ_i or ±ia.
- **Measured before registration:** engine vs Laurent at k = 4 and k = 30/7 agree to ≤ 1.3e−51 (c0 and c0′). A 12-term
  series differs by ~1e−8. One evaluation takes ~8 s.

## Loops (half-plane picture, based at 1.35)
- M1 = the capsule lasso around [r+, p+] (as §161).
- Γ = a disc lasso around {r+, p+, p−}.
- r−, ζ_i and ±ia stay outside both; they are passed to the walker for step control.
- **Kerr makes the trace conditions essential.** For Kerr's two-simple-pole data, Γ encloses three branch points of
  √(ND) and M1 two. So M1 is diagonal and Γ antidiagonal: tr Γ = tr M1Γ = 0. The pair is irreducible but imprimitive,
  hence VA. **So F_h ≠ 0 alone proves nothing.**

## Functions and the verdict rule
Counted over ∂R from the same samples:
- F_h = tr[M1, Γ] − 2; T1 = tr M1; TΓ = tr Γ; T1Γ = tr(M1Γ);
- and T1 − s for every s in S = {±2, ±1, 0, ±√2, ±(√5 − 1)/2, ±(√5 + 1)/2} (the finite-subgroup traces of SL₂).

**NO EXCEPTIONAL k IN R** requires:
- count(F_h) = 0, so the pair is irreducible;
- count(T1) = 0, and count(TΓ) = 0 or count(T1Γ) = 0, so it is not imprimitive (that needs two of the three traces
  zero at the same k);
- count(T1 − s) = 0 for all s, so it is not finite.

Then ⟨M1, Γ⟩ is Zariski-dense in SL₂ at every k ∈ R.

**If both TΓ and T1Γ have zeros in R:** their zeros are located by sub-rectangle counts. Coinciding zeros make the
result **UNDETERMINED (possible imprimitive point)**.

## Controls (any failure → VOID)
| control | what | must give |
|---|---|---|
| C-repro | engine vs Laurent c0, c0′ at k = 4 and 30/7, at 6 points with \|z − 2\| ≤ 0.65 | ≤ 1e−40 |
| C-repro-F | F_h, T1, TΓ at k = 4.05 from the engine vs the same loops on the Laurent c0 (ρ_c = 0.85 there); and at 30/7 vs §161's F_h = −0.737260531790084 − 2.7690338008439i | ≤ 1e−20 and ≤ 1e−12 |
| MF-trunc, must fail | the engine with its series truncated to 12 terms | C-repro must FAIL (diff ≥ 1e−30), and F_h at 4.05 must differ from the full engine by ≥ 1e−15 |
| P1 Kerr, must be VA (imprimitive) | k = 0 through the same engine, loops and classifier | \|TΓ\| ≤ 1e−15 and \|T1Γ\| ≤ 1e−15 (classifier says imprimitive → VA) |
| P2 planted non-VA member inside the window | k = 41/10: the circle pair (Laurent, ρ_c = 1.05 < 1.1) gives non-VA independently (F, tr M0, tr M1 ≠ 0; tr M1 ∉ S); the half-plane classifier must also say non-VA | both say non-VA |
| C2 counter must-detect | F_h·(k − k_p), with k_p = 4.15 + 0.1i inside R; F_h/(k − k_p); and k_p = 5 + i outside | count + 1, count − 1, unchanged |
| G-geo | interior grid (Re step 0.025, Im step 0.05) plus every boundary sample: engine guards; lasso clearance ≥ 0.3 × dist(p−, [r+, p+]); disc clearance ≥ 0.05 from every excluded singular point; Newton converges | all hold |
| G-count | G1 and G2 zeros in \|z − 1.85\| < 0.6 at the 4 corners, at (4.1, 0) and at (30/7 − 10⁻¹², 0); every loop point must lie in \|z − 1.85\| ≤ 0.55 (checked at every boundary sample) | (1, 2) everywhere; containment holds |
| G-step | every 4th boundary sample at steps 0.35, 0.2 and 0.12: all functions, every pair | relative ≤ 1e−15 |
| G-arg | after refinement | \|Δarg\| ≤ π/4 for every counted function, otherwise UNDETERMINED |

## Scope, if it passes
- At (E 4/5, spin 3/5): no k ∈ [3.95, 30/7 − 10⁻¹²] is exceptional.
- With gap B, covering (0, 4.05], and §161 (the endpoint, with no accumulation), K*(3/5) ∩ (0, 30/7] is contained in
  (30/7 − 10⁻¹², 30/7), and is finite there.
- That last open sliver is reported with samples (F_h, T1 at 30/7 − 10^{−j}, j = 13, 14, 15), not counted.
- 50-digit floating point; not an interval certificate; one (E, spin).
- Peak memory expected < 1 GB (the engine stores ~220-term series). Estimated ~30–60 min, 1 core, nice 10.
