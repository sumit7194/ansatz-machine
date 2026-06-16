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

## 2. Causal-structure lens (§6)  ◀ DONE
Added to the analyzer (`causal_structure`, `signature_flip`) + battery `42_causal_structure.py`.
- **Singularity character** from the sign of g^{kk} along the singular direction: g^{kk}<0 ⇒
  spacelike ('a moment, the end of time'); g^{kk}>0 ⇒ timelike ('a place'). Schwarzschild r=0 →
  spacelike; **adding CHARGE flips RN's r=0 → timelike** (the calibration); FLRW Big Bang (t=0) →
  spacelike, all exact.
- **Signature flip** (∂_t goes spacelike inside a horizon, t↔r swap): True for Schwarzschild/RN,
  False for FLRW/wormhole/Minkowski.
- The report card gained a `causal` row. Sister NN-project resonance (kept separate): our exact tool
  is the ground-truth oracle for the signature flip + charge-driven spacelike→timelike flip a net
  should reproduce.

## 3. Make it discover  ◀ DONE
`43_discover.py` — reuses 03's genetic loop over rational f(r), with a LIGHT fitness that scores only
the requested report-card boxes (ρ, p_t reduce to closed formulas in f,f',f''; evaluated numerically
per candidate, milliseconds). The full report runs once, on the winner.
- **Stage 1** {vacuum, horizon, asymptotic} → rediscovers **Schwarzschild** (f = 1 − 1/(4r)).
- **Stage 2** {asymptotic, physical, horizon, timelike singularity} → invents a SURVIVABLE black hole:
  the engine discovered **f = 1 − 5/(6r) + 1/(6r²)** — Reissner–Nordström form, it **invented the charge
  term**! The analyzer independently confirms: traceless EM-like matter, physical, two horizons,
  timelike (avoidable) singularity. From a physical WISH it rediscovered that survivability needs charge.
- Ties all three plan items: discover (#3) → analyze (#1) → causal structure (#2). Battery 43 (--quick).
- **Scope:** static spherical search space (fast). Rotating discovery = the later heavy VM run
  (analyzing each rotating candidate is ~6s, so that loop wants hours on the VM alongside Ludo).
