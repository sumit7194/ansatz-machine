# Active plan — analyzer growth

Agreed ordered roadmap (2026-06-16). Work top to bottom; each builds on the last.
Full menu of other directions lives in [ATTACK_ANGLES.md](ATTACK_ANGLES.md).

## 1. Crack the off-diagonal frontier  ◀ DONE (Kerr + Gödel land; rest are honest limits)
**Outcome:** the two famous off-diagonal spacetimes both analyze correctly — Kerr (rotating black
hole, ~6s: vacuum, 2 Killing vectors, both horizons M±√(M²−a²)) and Gödel (rotating universe with
CTCs, ~0.1s: stiff perfect fluid p=ρ, physical, 3 Killing vectors). The remaining off-diagonal items
are GENUINE symbolic limits, handled honestly (three-valued UNKNOWN), not failures:
- **Alcubierre warp**: full path intractable (√(x²+y²+z²) branch cut + arbitrary shape fn) — but it's
  already proven exotic directly in battery 38, so its physics is covered.
- **Rotating-horizon T,S**: numerically exact but symbolically irreducible (explicit horizon radical
  won't collapse; needs r_h-parametrization the analyzer can't auto-generate). Report location, mark T,S UNKNOWN.
- **Ring singularity**: off-diagonal Kretschmann swamps simplify (~500s) — UNKNOWN for now.
**Lesson banked:** off-diagonal is tractable when the metric is rational (Kerr via u=cosθ — the D4
rule extends) or homogeneous (Gödel); transcendental shape functions + branch cuts are the wall.

### (superseded notes)
Teach the analyzer to handle OFF-DIAGONAL metrics (Kerr, Alcubierre warp, Gödel)
without hanging — the most famous spacetimes the tool couldn't touch.
- **DONE (Kerr, ~6s in the atlas):** (a) `analyze()` decides the solution TYPE
  first with a NUMERIC pre-check on the Ricci, so vacuum metrics skip both
  `ricci_scalar` (the heavy contraction) and `stress_energy` — that was the hang;
  (b) `stress_energy` made lazy (per-component `cancel(together)`, no blanket
  simplify); (c) horizon detection generalized to `g^{rr}=0` (Kerr's Δ=0 →
  r=M±√(M²−a²), both horizons); (d) off-diagonal singularities → UNKNOWN (Kretschmann
  too heavy). **Key lesson: off-diagonal needs RATIONAL coordinates (u=cosθ) — the
  trig form swamps (500s); the D4 rule extends to off-diagonal.** Kerr added to the
  atlas (row 11).
- **Still open in #1:** Alcubierre warp + Gödel (their own structure — warp's
  Eulerian energy, Gödel's rotating dust+Λ via the eigenvalue path); rotating-horizon
  T,S; the ring singularity (needs a cheaper off-diagonal invariant than Kretschmann).

## 2. Causal-structure lens (§6)
Classify a singularity as **spacelike** ("the end of time" — Schwarzschild r=0) vs
**timelike** ("a place you can avoid" — Reissner–Nordström r=0), and detect the
**signature flip** inside a horizon (timelike direction rotating ∂_t→∂_r). Calibrated
by the Schwarzschild-vs-RN contrast (both in the zoo). Sister NN-project resonance
(kept separate): our exact tool is the ground-truth oracle for what their net claims
to have learned.

## 3. Make it discover
Point the GP search engine at the analyzer's report as the fitness/filter — so the
tool INVENTS spacetimes to spec ("find a physical metric with a horizon sourced by a
perfect fluid") instead of only describing given ones. Closes the circle back to the
project's original propose→verify→evolve loop, now in the general setting.
