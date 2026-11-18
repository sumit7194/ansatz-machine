# Edge-link v2: are the §150 window's switches strands of W^s(γ)? Exit-sign bisection. Pre-registration, 2026-11-18, BEFORE any code

**Ask:** Sumit's go, relayed by the Bridge, on the redesign proposal (`EDGE_LINK_REDESIGN_PROPOSAL.md`, a5daf8e).
**Model:** design and implementation by Claude Opus 5.5 (ansatz-machine session).
**State at registration:** no code exists for this. Data already seen: everything in §155 (edge-link v1), including
its TS outcome. That is disclosed, and it is why the must-fail controls use v1's actual artefacts.

## Correction to the proposal, made before any code
The proposal said ρ_min ∝ w (slope 1) on a strand and ∝ w² at x\*. **That is wrong.**
- **On a strand:** a point at distance w from a strand of W^s has u₀ ∝ w and s₀ = O(1) when it arrives near γ.
  After j crossings, |u| ≈ u₀λ^j and |s| ≈ s₀λ^(−j), so the closest approach is ρ_min ≈ √(u₀ s₀) ∝ **w^(1/2)**.
- **At x\*** (where ℓ passes through γ): the start point is already within ~d of γ in both directions, so
  ρ_min ∝ **d (slope 1)**.
- **On a boundary γ does not own:** ρ_min does not shrink (slope ≈ 0).
- The registered targets below use 1/2, 1 and 0.

## Definitions (fixed)
- **Level:** TS `ts2:4/5`, E = 97/100, L = 41/8. **Kerr:** `ts2kerr:4/5`, L = 2550268/1000000. The section, ℓ, z\*, λ,
  v_u (a > 0), v_s = R(v_u) and the eigenframe (u, s) with ρ = max(|u|, |s|) are as in §155. The engine is
  `_ts_edge.EdgeMap` (gate passed in §155); plunge is status 1 at x_pl = 1.5.
- **Visit** (ε_c = 1e−2): a maximal run of consecutive section points (the start point counts as index 0) with
  ρ ≤ ε_c.
  - It ends at the first later crossing with ρ > ε_c. **σ = sign(u)** there.
  - If the orbit plunges (status ≠ 0) before such a crossing, σ = −1.
  - **ρ_min(visit)** = the smallest ρ during the visit.
- **History H(x):** the list of σ for successive visits. It stops at the first σ = −1, at K = 6 visits, or at the
  300-crossing cap. **Fate F(x)** = plunges within 300 crossings (status 1).
- **Bisection on σ_v:** for a pair whose histories agree on visits 1 … v−1 and differ in σ_v (both have visit v).
  The midpoint goes to the side whose σ_v it shares. If a midpoint's prefix differs, or it has no visit v, the
  bracket is **broken**: it stops and is logged.
  - Stop at relative width 1e−18, or after 70 halvings.
  - At every stage record w (the bracket width) and ρ_min(w), the LARGER of the two members' visit-v minima.
- **Ownership slope:** a least-squares fit of log ρ_min against log w over the stages with w/x ∈ [1e−15, 1e−5].
  At least 6 decades of w are needed, or the result is "insufficient".
  - **"Transverse strand"** = slope in [0.4, 0.6].
  - "At γ" = slope in [0.85, 1.15].
  - "Not owned" = slope < 0.2.
- **Precision:** σ_v at R1 must agree with R2 at every 10th stage and at the final stage.
- **ε-independence:** the final pair, rerun with ε_c = 3e−3, must give the same σ_v (the visit index may shift; the
  sign at the decisive visit must not).

## Controls (run first, in this order; any failure means VOID)
| control | input | must give |
|---|---|---|
| K-sep | Kerr pair x_h ± 1e−6 on ℓ (x_h in closed form) | a σ flip; bisection converges to x_h within 1e−16; slope "transverse strand" |
| K-star | Kerr pair x\* ± 1e−6 | a σ flip; converges to x\* within 1e−16; slope "at γ" (so NOT classed as a transverse strand) |
| MF-1 (must fail) | the §155 T-BANDS edge pair (TS, edge j = 244, d(1 ± 1e−10)) | identical histories (no σ flip). Then bisected on the v1 artefact predicate ("a leg's max x > 30") to w/x = 1e−15: slope "not owned" |
| MF-2 (must fail) | the §155 K-O′ section-cut boundary (Kerr, x_c = 11.458) | identical histories. Bisected on the section-cut fate to w/x = 1e−15: slope "not owned" |
| T-sep | TS pair x_h ± 1e−6 around §154's x_h | a σ flip; converges within 1e−14 of the stored x_h; slope "transverse strand" |

## Window test (TS, only if every control passes)
- 400 samples on ℓ, uniform over [9.912067, 9.945202]. Histories and fates at R2.
- **Vacuity guards:** ≥ 30 samples with at least one visit, AND among plunging samples ≥ 90% whose last visit before
  the plunge has σ = −1 (coverage: plunges go through γ's neighbourhood). If either fails: **VACUOUS**.
- **Strand candidates:** neighbouring samples whose histories first differ by a σ flip at some visit v. At most 20,
  in x order, are bisected and certified. A **certified strand** has slope "transverse strand", R1/R2 agreement, and
  ε-independence.
- **Falsifier candidates:** neighbouring samples with DIFFERENT fates and IDENTICAL complete histories. "Complete"
  means each ended with σ = −1 or reached the cap with fewer than K visits.
  - Bisect on fate to w/x = 1e−15.
  - It is a **FALSIFIER** if the fate flip persists, the histories stay identical at every stage, ρ_min along the
    final pair's orbits stays ≥ 0.1, and R1 agrees on both final fates.

## Verdict words (this (E, L) level only)
- **VOID:** any control fails.
- **VACUOUS:** a vacuity guard fails.
- **FALSIFIED:** any falsifier. The window contains a switch that γ does not own.
- **SUPPORTED on the sample:** ≥ 3 certified strands and 0 falsifiers. With §154 (horseshoe), this licenses "a
  Cantor set of edge points lies in the §150 window" (reasoning W-2). It is numerical, on a sample, at one level.
- **NOT ESTABLISHED:** otherwise.
- Nothing here licenses statements about α, other levels or EMRIs.

## Predictions (sealed by this commit)
| item | prediction | confidence |
|---|---|---|
| all 5 controls behave | yes | ~65% (a new pipeline; the slope fits have a phase jitter of up to λ^(1/2) per point) |
| vacuity guards pass | yes | ~70% |
| verdict SUPPORTED | yes | ~50% |
| verdict FALSIFIED | no | ~90% |

## Resources and blinding
- Slot from the Bridge: about 1 h for TS plus the Kerr measurement, 1 core, nice 10, < 1 GB. If the measured Kerr
  cost implies more than 1.5 h in total, the number goes to the Bridge before TS.
- Embargo `ansatz-edge-link-ts` covers TS strand positions, slopes, counts and class counts. Only the verdict word and
  seals go out.

## Addendum 1 (2026-11-19, after the controls run, BEFORE any window run)
**Controls (`edge2/controls.json`):**
- **K-sep: slope 0.499** over 7.5 decades, "strand"; converged to the closed-form x_h within 7e−18; R1/R2 and ε both
  pass.
- **K-star: slope 1.000** over 8.1 decades, "at γ", within 2e−18.
- **MF-2: slope 1e−8**, "not owned", with identical histories.
- **T-sep: PASS.**
- **MF-1: FAIL ("insufficient").** So **the controls as registered give VOID.**

The corrected theory (½ on a strand, 1 at γ, 0 not owned) is confirmed in Kerr to three digits.

**Diagnosis of MF-1, a defect in the registered INPUT:** the registered bracket d(1 ± 1e−10) around the §155 edge is
2.6e−15 wide, i.e. w/x = 2.6e−16. That is already below the fit window [1e−15, 1e−5], so no decades could be fitted.
The histories were identical, as required.

**v2′ (a new verdict; the registered v2 stays VOID).** MF-1's input becomes the two §155 T-BANDS grid neighbours
that bracket that edge, d_244 and d_245 (w/x ≈ 5e−8, more than 7 decades available). The predicate, the
identical-history requirement and the "not owned" target are unchanged. All five controls are rerun under the same
code.
- **v2′ controls: ALL PASS** (`edge2/controls.json`).
  - K-sep: slope 0.499 (strand).
  - K-star: slope 1.000 (at γ).
  - MF-2: slope 1e−8 (not owned).
  - **MF-1: slope 3e−4 over 7.2 decades, "not owned"**, with identical histories.
  - T-sep: pass.
  - The window run waits for a slot; its estimated cost is above 1.5 h.

## Outcome (2026-11-19 01:35; grade: registered controls VOID → v2′ via fde95e2 before any TS run; slope corrected before code)
**VERDICT: VACUOUS.** The vacuity guards failed.
- **Samples with at least one visit (ρ ≤ 1e−2): 7 of 400** (≥ 30 needed).
- **Coverage: 1.9%** of the 160 plunging samples ended with an inward exit from a visit (≥ 90% needed).
- So there was 1 σ-flip candidate and 119 fate-flip neighbour pairs. No bisection ran, because the guard failed
  first. Time 8,079 s (91,127 map calls). No certificates, no falsifiers.

**Post-hoc diagnosis (labelled as such):** the coverage guard encoded a FALSE premise, that plunging orbits leave
through γ's neighbourhood. They do not. Window orbits that plunge leave D through the exit lobe of the turnstile, whose
bulk lies far from z\* (ρ = O(1)). Only orbits near the lobe's BOUNDARY, a strand of W^s, pass close to γ. So "visits"
are rare by geometry, and exit-sign histories cannot label most switches. This agrees with T-L3′: exits are
one-way, but they are not near γ.

**What it points to (a proposal only, for Sumit):** drop visits altogether. Bisect directly on the 300-crossing fate
of window neighbours with different fates (119 pairs available), and classify each switch by the ownership slope of
the larger of the two members' whole-orbit ρ_min against w: ½ means a strand, 0 means not owned. The controls just
validated (K-sep ½, K-star 1, two must-fail artefacts at 0) carry over unchanged. The lifetime-step worry from v1 is
small at a 300-crossing cap: the step sits roughly λ^(−(300 − n)) from its strand, far below any resolvable w. That
argument needs checking before it is relied on.
