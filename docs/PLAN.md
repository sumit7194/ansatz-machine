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
- **RING SINGULARITY CLOSED (2026-06-17, `48_ring_singularity.py`):** the numeric Kretschmann
  (numeric_curvature.py) reveals Kerr's singularity is a RING — K diverges as r→0 ON the equator
  (u=cosθ=0, Σ=0; ×244 from r=0.05→0.02) but stays bounded OFF it — the structure the symbolic
  Kretschmann (and hence the analyzer) had to mark UNKNOWN. Validated vs exact Schwarzschild K=48M²/r⁶.
- **Still open in #1:** rotating-horizon T,S (Kerr temperature/entropy — could now do numerically);
  warp + Gödel are HANDLED for analysis (Gödel via the eigenvalue path; warp proven exotic in 38).

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
- **Scope:** static spherical search space (fast).

## 4. Rotating discovery  ◀ DONE (and it didn't need the VM)
`44_discover_rotating.py` — invents a SPINNING black hole. The naive "search arbitrary rotating
metrics + fully analyze each (~6s)" would crawl (the VM-run we'd feared). The smart design instead:
FIX the rational Kerr structure (Σ=r²+a²u², off-diagonal frame) and search just the one radial
function Δ(r) inside it; REDUCE the vacuum residual ONCE (7s) to cheap formulas in (Δ,Δ',Δ''), then
score candidates numerically (ms). So it's a single-function search like the static loop —
**rediscovered KERR Δ=r²−2Mr+a² in ~22s LOCALLY** (analyzer confirms: vacuum, 2 Killing vectors, both
horizons M±√(M²−a²)). The "deep VM run" turned out unnecessary — the reduce-once trick made rotating
discovery fast. Battery 44 (--quick).
- **Kerr–Newman extension (charged rotating) DONE:** same Kerr-Δ ansatz + the Kerr–Newman EM field,
  Einstein–Maxwell residual reduced once (verified ≡0 at Δ_KN); target "charged" (Q=1/2) → discovered
  Δ = r²−2Mr+a²+Q² (const 1/2 = a²+Q²) — the engine added Q² to Δ's constant, the rotating analogue of
  the static RN discovery (battery 31). GP note: pick Q so a²+Q² has a SMALL denominator (constant-
  mutation explores small denominators — 5/16 was too hard, 1/2 is easy).
- **Kerr–de Sitter ATTEMPTED (2026-06-17, overnight) — parked, computational limit.** Insight held:
  with Δ_θ=1+Λa²u²/3 and Ξ=1+Λa²/3 FIXED by Λ, it IS a single-Δ_r search (built the Carter-form ansatz,
  reduces to Kerr at Λ=0). BUT the reduce-once step is the blocker: the Kerr–dS Ricci (with Δ_r symbolic)
  is far heavier than Kerr's — it never finished building the symbolic residual (OOM/>180s even alone),
  vs Kerr's clean 7s. So the SYMBOLIC reduce-once is infeasible here; would need a NUMERIC-curvature
  evaluator (substitute numeric Δ_r,r,u before computing curvature) — a different tool, parked.
  **UNBLOCKED (2026-06-17): built that numeric tool.** `numeric_curvature.py` computes the Ricci by
  finite differences (pure Python, ms/point, no symbolic blow-up); battery `46_numeric_curvature.py`
  validates it VERIFIES Kerr–de Sitter (vacuum+Λ, |R−Λg|≈2e-4) — the metric symbolic OOMs on — plus
  Schwarzschild/Kerr (≈0) and a wrong-Δ_r control (large). The VM was never the answer; a numeric engine
  was. **Kerr–dS analysis is fully unblocked.** The from-scratch GP DISCOVERY of the Kerr–dS Δ_r was
  then attempted (search Δ_r by the numeric residual) and is HARD — the target is a quartic
  (−r⁴+¾r²−2Mr+¼) and the GP's primitives (r, c, ×, powi 2/3) can't easily evolve the r⁴ term, plus the
  numeric fitness is slow; it stalled at the constant (fit ~0.03). NOT forced. The meaningful result is
  already in battery 46: the numeric engine VERIFIES Kerr–dS, and its control shows Kerr's own Δ
  (no Λ term) gives a LARGE residual in a Λ-universe — i.e. the engine confirms a rotating hole in a
  Λ-universe REQUIRES the −Λr⁴/3 correction. Full quartic discovery would need r⁴ in the GP primitives
  or a seeded search — a future tweak, not tonight.

---

## Follow-up plan (2026-07-02, evening discussion) — the pre-weekend push

The §99→§106 chain (exact bumpy metrics → proven non-integrability → exhibited chaos → 3 validated
detectors) is complete. Four follow-ups, to be tackled one by one; the write-up is the weekend move.

1. **The LISA observable — resonance-crossing frequency plateau (IN PROGRESS).** Drive an
   inspiral/sweep through the 2/3 resonance of a bumpy metric and exhibit the frequency-LOCKING
   plateau (Lukes-Gerakopoulos/Apostolatos/Contopoulos PRD 81 124005: inside a resonance island the
   rotation number locks to the rational; a Kerr inspiral shows no such plateau — the smoking-gun
   non-Kerr signature). Step 1 (quasi-static): rotation-number staircase vs launch radius across
   §106's ZV island (locked at 2/3 over the island's width) with a Kerr control (smooth, no plateau).
   Step 2 (dynamic): flux-driven (§100/§101) drift across the island → the plateau in TIME = what
   LISA would see. Synthesizes §97-§106 into a falsifiable observable; hands the bridge B1's endgame.

2. **Consolidate: chaos/integrability as ONE analyzer lens.** Fold the toolchain (Killing-tensor
   search + Poincaré + box-dim + de-noised Lyapunov + frequency-drift) into the general analyzer:
   any stationary-axisymmetric metric → verdict {integrable | non-integrable, thin-layer | chaotic}.
   The standing "widen the ONE tool" steer.

3. **Black-hole mimickers under the full engine.** Boson star / gravastar exteriors through the
   whole report card + observables + integrability: "how would you tell it's not a black hole,
   quantitatively, with every lens at once?" Extends §90 (imposters) beyond the shadow.

4. **(Parked) rotating EdGB O(a²) 2D-PDE.** The last item-3 wall. Prior art exists (closed-form
   rotating EdGB in the literature), so this is engine-capability, not new science. Only if 1-3 land.
