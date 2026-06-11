# v4 — the EdGB track (modified gravity)

*Pre-registered design, written before any v4 code. All physics below was
web-verified 2026-06-11; citations inline. This is the machine's first step
off vacuum GR and the first place a genuinely new-to-literature result could
live.*

## The target, verified

The **Einstein-dilaton-Gauss-Bonnet (EdGB) black hole** — known to exist
since [Kanti, Mavromatos, Rizos, Tamvakis & Winstanley, PRD 54, 5049
(1996)](https://arxiv.org/abs/hep-th/9511071) — has **no closed form as of
2026**. The state of the art is a hand-fitted continued-fraction
approximation ([Kokkotas, Konoplya & Zhidenko, PRD 96, 064004
(2017)](https://arxiv.org/abs/1706.07460), accuracy "a few tenths of one
percent" for p ≲ 0.97), built on the [Rezzolla–Zhidenko parametrization,
PRD 90, 084009 (2014)](https://arxiv.org/abs/1407.3086). No AI/symbolic-
regression work on this metric was found (2023–2026 scan) — the niche is
open in both directions: an exact form (lottery ticket) or a better/simpler
fit (publishable genre).

## The theory (Kanti conventions — our cross-check standard)

- Lagrangian: `L = R/2 − ¼(∂φ)² + (α′/8g²)·e^φ·G_GB`, with
  `G_GB = R_abcd R^abcd − 4R_ab R^ab + R²`. **Kinetic term is −¼, not −½**
  — the #1 factor hazard. Set α′/g² = 1 by shifting φ.
- Field equations stay **second order** (the GB double-dual structure;
  [Stein's note](https://duetosymmetry.com/notes/note-on-simple-eoms-for-edgb-dcs/)).
- Static spherical ansatz `ds² = −e^{Γ(r)}dt² + e^{Λ(r)}dr² + r²dΩ²` +
  scalar φ(r) reduces to Kanti **eqs. (33)–(36)**; e^Λ eliminates
  algebraically (eqs. 50–51), leaving a 2-ODE system `φ″ = −d₁/d,
  Γ″ = −d₂/d` with d, d₁, d₂ printed in **main-text eqs. (54)–(56)**
  (NOT the appendix, despite KKZ's pointer).
- Horizon regularity fixes `φ′_h` as a quadratic root (σ=+1 branch) with
  discriminant condition `e^{φ_h} < r_h²/√6` — the minimum-size constraint
  AND the numerical shooting seed. One-parameter family per r_h; integrate
  outward (RK4, ~1e-8), no fine-tuned shooting. KKZ regularize Γ′'s horizon
  pole via Ψ ≡ Γ′·(r−r₀).

## The two-track design

**Track A — REDUCE for EdGB (exact hunt).** Extend the engine: given the
(f, h, φ) ansatz, derive the field-equation residuals symbolically (Einstein
+ scalar), cross-checked term-by-term against Kanti eqs. (33)–(36) and the
p=0 Schwarzschild limit BEFORE anything else (ground rule 1: verifier before
proposer; conventions validated against the literature before trusting our
own algebra). Then the standard loop hunts (f, h, φ) triples with the
finisher. Honest odds: low — the field expects no closed form. Null result =
"the rational/Laurent ansatz class provably contains no EdGB solution",
which is itself worth recording.

**Track B — the fit verifier (the realistic prize).** A SECOND verifier
track, fit-quality instead of exact-zero:
1. Numerical ground truth: implement the Kanti/KKZ shooting recipe
   (horizon expansion → σ=+1 root → RK4 outward → read M, D from
   asymptotics). Validate against published numbers (KKZ Table/figures,
   ε ≈ p/11 relation) before use.
2. Fitness of a symbolic candidate = max relative deviation from the
   numerical metric over the exterior (and its error at the photon sphere,
   where KKZ's error peaks — beat them where they're weakest).
3. GP + finisher hunt compact closed forms; the bar is KKZ's
   ~0.1–0.3% at third order with their ~10 fitted coefficients. A win is
   simpler-or-more-accurate; report both.

## Pre-registered batteries (gates before glory)

- **E0 (conventions):** our symbolic reduction reproduces Kanti (33)–(36)
  exactly (term diff = 0), and collapses to Schwarzschild at α′=0.
- **E1 (numeric ground truth):** shooting code reproduces the
  e^{φ_h} < r_h²/√6 boundary, the secondary-hair relation D(M), and KKZ's
  ε ≈ p/11 to stated accuracy.
- **E2 (fit-verifier honesty):** feeding KKZ's own published fit through our
  fit verifier must score ~their stated accuracy; feeding Schwarzschild must
  score the known EdGB deviation (the verifier must not "absorb" the new
  physics — KKZ's own criterion).
- Only after E0–E2 green does any hunting start.

## Status

- [ ] E0 conventions battery
- [ ] E1 numerical ground truth
- [ ] E2 fit-verifier honesty
- [ ] Track B hunt · [ ] Track A hunt · [ ] write-up
