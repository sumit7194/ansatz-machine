# Journal

*Dated activity log, newest first. One entry per working session: what was
built, what broke, what the machine taught us. Numbers live in
[RESULTS.md](../RESULTS.md); decisions live in [DECISIONS.md](DECISIONS.md).*

---

## 2026-06-11 — the finisher debugging saga + expedition PASSED + VM prep

- **The expedition passed all three legs** (~1 min total): 7D Tangherlini
  discovered & grown (leg 1, snap at gen 2), **Tangherlini–de Sitter
  discovered & grown** (leg 2, `f = 1 − r²/8 + 1/r²`, snap at gen 17 —
  the rung that failed twice before), memory replay recognized (leg 3,
  snap at gen 4). Catalog: 4 self-discovered families. With the finisher,
  hunts that took 50–150 generations now take 2–17.
- **The four-bug debugging saga that got us here** (all one theme:
  *canonicalize before you reason*):
  1. Tree-slot symbolization creates constant-space GAUGE redundancy
     (`k1·(k2·r + …)`) → solution variety positive-dimensional →
     sp.solve returns [] instead of parametric families. Fix: Laurent
     canonicalization (one unknown per power of r).
  2. Numeric angle-fixing left unsimplifiable trig CONSTANTS in the
     equations (`−4tan(11/10)+4sin(11/5)−4cos(11/5)tan(11/10)` — which IS
     zero) → solve saw "nonzero = 0" → inconsistent. Fix: simplify every
     coefficient; genuinely nonzero constants are a correct early exit.
  3. Root of (2): simplification ORDER. Mixed-index residuals R^a_b +
     symbolic-first simplify → the θ identities fire and the angular
     components collapse to θ-free form (5 components → 2 clean ODEs).
  4. The growth step missed the IMPLICIT coefficient: in
     `−r²/8 + 1 + r⁻²` the mass coefficient 1 has no tree leaf, so
     slot-wise generalization never tested the one constant that was
     free. Fix: generalize Laurent-coefficient-wise.
- A power loss mid-session ate /tmp logs and earlier runs and proved the
  persistence design (catalog/journal/logs in repo) right. Run logs now
  always live in the repo root.
- **VM practice established** (standing rule): runs move to the GCP VM
  niced to 19 (single-core, tens-of-MB — invisible next to the trainer
  there), with `scripts/dashboard.py` (stdlib-only, read-only) on port
  8080 behind a one-IP firewall rule. See docs/VM.md. Parallel seeds
  across idle cores = the island model for free.

## 2026-06-11 — the stationary hall falls: first frame-dragging solution

- Built `08_stationary.py`: first OFF-DIAGONAL ansatz
  (−f·dt² + dr²/h + r²(dφ + ω·dt)², three genomes). Ground truth first:
  rotating BTZ VERIFIED through the engine, sabotaged frame-dragging
  (ω ∝ 1/r³) REJECTED.
- **The gauge-evasion saga** (now D15): the hunt evaded three times —
  constant ω (frame gauge), then *negligible* ω (non-constant, physically
  nothing — converged to the non-rotating solution while dodging the
  penalty), then structures whose only exact solutions are gauge-trivial.
  Fixes, in order: rotation-magnitude penalty (max|ω| ≥ 1e-2), and the
  **algebraic finisher with enrichment** (D14): symbolize a near-miss's
  constants, add the sub-leading k·r^p terms GP rarely composes, solve the
  coefficient system exactly, instantiate free family parameters
  generically (never zero — they ARE the mass/spin).
- **Result: seed 0, generation 12, 9.8 s** — `h = r² + (29/48)²/r²`,
  `f = 4h`, `ω = −1 + 29/(24r²)`: the rotating BTZ family (M=0, J=29/24)
  wearing two gauge costumes at once (time-rescaling + rigid rotation),
  VERIFIED exact, correctly declared BLIND_SPOT (2+1 is CSI forever).
  The machine's first frame-dragging discovery. 08 added to the gate.

## 2026-06-11 — docs structure + the expedition (v3 begins)

- Created this docs tree (JOURNAL / DECISIONS / GLOSSARY / ROADMAP).
- Built `07_expedition.py`: the self-extending campaign. The machine walks
  uncharted (dimension, Λ) rungs and, on every confirmed CANDIDATE_NEW,
  generalizes it and grows its own catalog *mid-run* — then proves the memory
  works by re-hunting a grown rung and recognizing the family. (Results below
  in this entry once the gate runs.)

## 2026-06-11 — v2 shipped; repo goes public

- **Two-function hall (06) PASSED** — Birkhoff honesty stress test, zero false
  novelty across 3 rungs; gauge checks all `f/h = const`. The memory rung
  matched the machine's own grown family from the day before: the
  discover → generalize → remember → recognize loop closed.
- Measured failures bought two fixes: 2D Newton → nested 1D bisection (steep
  invariant curves); per-slot crossover stagnation → **gene duplication**
  operator (Birkhoff rung then fell in ~2 generations).
- **Catalog auto-growth (05)** shipped: constants tested one-by-one against
  the symbolic verifier — mass came out free ("hair"), the Λ-coefficient and
  the asymptotic 1 came out structural ("law"). Families persisted to
  `catalog_discoveries.json`.
- Installed the `ai-coding-standards` skill (project-level) and added
  `verify.sh` as the single gate. Full gate green (6 batteries, ~14 min,
  dominated by the hall).
- **Pushed to https://github.com/sumit7194/ansatz-machine** (MIT, one root
  commit, description + topics set).

## 2026-06-10 — v1: the machine works end to end

- Verified the niche via web research (no published AI-found exact metric as
  of June 2026; Cartan–Karlhede has no Python implementation).
- Built the GR engine (pure SymPy, dimension-agnostic, three-valued verdicts),
  the verifier battery (Kerr ✅ 9 s in rational u=cosθ form after two measured
  failures), the (K, |∇K|²) fingerprint filter (costumes unmasked, blind spots
  declared), the GP rediscovery loop (Schwarzschild blind in 2–3 generations),
  and the six-rung campaign (80 s; two finds outside the catalog correctly
  escalated CANDIDATE_NEW).
- Machine-taught lessons: it found Minkowski first, then pure de Sitter (the
  triviality ladder was born); it prefers negative-mass branches on catalogued
  rungs; 2+1 is a permanent, *correct* blind spot.
