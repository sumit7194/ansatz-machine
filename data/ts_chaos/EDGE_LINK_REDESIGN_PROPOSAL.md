# Edge-link redesign: certify window switches with a predicate γ owns (2026-11-18, PROPOSAL ONLY, nothing run)

For Sumit, via the Bridge. It follows §155 (NOT ESTABLISHED). The one-way gate (T-L3′) holds. Switch certification
failed because both predicates used, "plunges within n crossings" and "a leg's max x exceeds 30", have boundaries
that γ does not own: lifetime steps and threshold crossings. Those boundaries sit next to the strands of W^s(γ), not
on them.

## The idea, in one line
Decide each orbit's fate where γ decides it: at a close approach to γ, the orbit leaves either inward (u < 0) or
outward (u > 0). A strand of W^s(γ) is exactly where that exit sign flips. Bisect on the exit sign.

## Definitions
- Eigenframe (u, s) at z\*, and ρ = max(|u|, |s|), as in §155.
- **Visit:** a maximal run of consecutive crossings with ρ ≤ ε_c (ε_c = 1e−2). Visit v ends at the first crossing
  with ρ > ε_c; **σ_v(x) = sign(u)** there. If the orbit plunges first, σ_v = −1 by convention.
- **History:** H(x) = (σ_1, σ_2, …) up to the first inward exit, or K = 6 visits.
- **Switch candidate:** neighbouring window samples whose histories first differ at visit v.
- **Bisection on σ_v** (the histories agree before v) down to a relative width of 1e−18.
- **Ownership certificate (the γ signature):** at each bisection stage w, both members reach a minimum distance
  ρ_min(w) during visit v. If the bracket closes on W^s, then **ρ_min ∝ w (slope 1 in log–log)**, because a point at
  distance w from the strand approaches γ to a distance proportional to w. Require a fitted slope in [0.9, 1.1] over
  ≥ 6 decades of w, and R1/R2 agreement on σ_v at every stage.

## Controls (run first; any failure VOIDs the run)
| control | what | must give |
|---|---|---|
| K-sep | Kerr: the σ_1 flip on ℓ near x_h | converges to the closed-form x_h to ≤ 1e−18; slope 1 ± 0.1 over ≥ 6 decades |
| K-star | Kerr: the σ flip at x\* itself (where ℓ passes through γ) | ρ_min ∝ w² there (the §155 / √tol geometry), so the certificate must report **"not a transverse strand"**: a known exception, and evidence that the slope test discriminates |
| **MF-1, must fail** | the T-BANDS artefact: bisect on "leg max x > 30" for the §155 edge pair | the histories are identical, so there is no σ flip; and ρ_min stays ≥ ε_c as w shrinks: **certificate FAILS** |
| **MF-2, must fail** | the K-O′ section-cut boundary (Kerr) | no σ flip; ρ_min ≥ ε_c: **certificate FAILS** |
| T-sep | TS: the σ flip next to the §154 x_h | certificate holds (slope 1) |

## Test on the window
- 400 samples on ℓ, uniform over [9.912067, 9.945202]. Histories at R2. Every candidate pair, at most 20 (taken in x
  order), is bisected and certified.
- **Falsifier:** a fate discontinuity (plunge within 300 crossings versus not) between window neighbours with
  IDENTICAL histories through K visits, whose fate flip persists under bisection to 1e−15 with ρ_min ≥ ε_c and R1/R2
  agreement. That is a boundary in the window that γ does not own.
- **SUPPORTED on the sample:** all controls behave; ≥ 3 window strands certified; 0 falsifiers among all window
  neighbours with differing fates.
- **NOT ESTABLISHED:** otherwise. **FALSIFIED:** any falsifier.

## Cost and risks
- Each history takes ≤ 60 crossings; each bisection about 60 stages × ≤ 60 crossings. Estimated ~1 h on 1 core for TS
  (Kerr first, measured).
- **Risk 1:** visits may be rare in the window within K = 6, which would make the test vacuous. Guard: ≥ 30 window
  samples with at least one visit, or VACUOUS.
- **Risk 2:** ε_c dependence. Rerun the certified strands at ε_c = 3e−3; σ_v must not change.

## What it could and could not license
- SUPPORTED would license "the §150 window's switches sampled here are strands of W^s(γ)", and with §154 (horseshoe)
  a Cantor set of edge points in the window (reasoning W-2). Numerical, on a sample, at one (E, L).
- It would not license any statement about α, other levels or EMRIs.
