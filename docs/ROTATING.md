# v5 — rotating EdGB (slow-rotation rung first)

*Pre-registered design. Full rotating EdGB is a 2D PDE problem (metric
functions of r AND θ) — gated until the 1D machinery proves out here.*

## The rung: frame dragging at first order in spin

Perturb the validated static EdGB background (steps 10–11) with
`g_tφ = −ε·w(r)·r²sin²θ` and expand the EdGB action to O(ε²). The
Euler-Lagrange equation of w is a LINEAR second-order ODE on the
background — 1D, exactly what our machinery handles. The dilaton and
the diagonal metric receive no correction at O(ε) (standard slow-rotation
structure; verified against literature by the research pass).

## Batteries (gates before hunts)

- **R0 (derivation):** derive w's ODE from the reduced action.
  Validations: (a) **GR limit** — at α′=0 on Schwarzschild, w = c/r³ must
  solve it exactly (the known exterior slow-rotation result); (b) the
  equation is linear and second order in w; (c) no stray θ remains after
  the symbolic θ-integration.
- **R1 (shooting):** integrate w on EdGB backgrounds (horizon-regular,
  normalized by J at infinity). Validations: p→0 recovers w = 2J/r³
  everywhere; the EdGB deviation profile is smooth in p and vanishes as
  p→0. Literature anchor for magnitudes: slow-rotation EdGB moment-of-
  inertia corrections (research pass to verify citable numbers).
- **R2 (the prize):** universal closed-form fit for the frame-dragging
  correction across the family — same protocol as the static arc
  (GN + continuation, training p ∈ [0.1, 0.6], SEALED p=0.7 holdout
  built before any fitting).

## Status
- [x] R0′ (derive-and-verify at exact probes — see result section; the
  brute-force R0 stays parked) · [x] R1 (shooting + κ_c=1.0, now
  CONFIRMED by R0′) · [x] R2 (universal fit, two sealed holdouts —
  see result + disclosure)

## Literature anchors (web-verified 2026-06-12)

- **The O(χ) ODE**: Pani & Cardoso, PRD 79, 084031 (arXiv:0902.1569),
  eqs. 30–39: only g_tφ modified at O(χ); for the l=1 mode the equation
  is Ω″ + (G₂/G₃)Ω′ = 0 — a pure QUADRATURE (no eigenvalue problem),
  with G₂/G₃ → 4/r − (Γ′+Λ′)/2 in the GR limit, i.e.
  (r⁴e^{−(Γ+Λ)/2}Ω′)′ = 0 → ω = 2J/r³ exactly (Hartle/Lense–Thirring).
  Our R0 derivation must reproduce this structure.
- **Quantitative anchors** (mutually reconciled; ζ_AY = ζ_M²/16):
  (A) Maselli et al. arXiv:1507.00680 eq. 41 — I/M³ = 4 − 0.2625ζ² − …;
  (B) Ayzenberg–Yunes arXiv:1405.2133 v4 — closed-form small-coupling
  g_tφ (eq. 15) and Ω_H = Ω_H,Kerr(1 + (21/20)ζ_AY);
  (C) Pani–Cardoso: MΩ_H ≈ 0.37 J/M² at near-maximal coupling
  (Kerr: 0.25) — frame dragging up to ~40% stronger.
- **Convention traps**: ω sign per signature; J read from the 2J/r³
  tail is UNcontaminated by GB (correction decays faster); the constant
  mode of the quadrature is a rigid-frame gauge — kill via Ω(∞)=0;
  Ω_H is an output, never a boundary condition; coupling normalization
  Kanti α′e^φ/8 vs PC/Maselli (α/4)e^φ — factor-of-2 risk, validate
  against the GR-limit structure first.
- **The gap (confirmed)**: no KKZ-style closed-form fit and no
  AI/symbolic-regression work exists for rotating or slow-rotating
  EdGB. R2's prize is unclaimed territory.

## R0 amendment (honest, 2026-06-12)

Own-derivation of the O(ε²) action via brute-force expansion is PARKED
after three measured attempts: laptop SymPy twice (>2.2 GB and climbing
at 18 CPU-min, both full and series-truncated forms), then
`19b_rot_reduce_fast.py` on the GCP VM (8 cores / 31 GB): 2.3 h at
99.9% CPU, RSS plateaued at 14.0 GB, no progress past the contraction
phase — **stopped by choice (SIGTERM), not by crash or OOM**. The flat
RSS does not prove intractability (SymPy grinds CPU-bound inside stable
memory); what it proves is that the *expand-everything route* is
exponentially wasteful: intermediates are GB-scale while the final ODE
is two lines. A resurrection route exists — see R0′ below. Meanwhile
R0's validation role is replaced by TRIPLE-ANCHOR calibration of the
PC-transcribed G₂/G₃ (arXiv:0902.1569 eqs. 31-32):
(G1) exact GR limit; (G2) small-coupling frame-dragging correction
shape vs Ayzenberg-Yunes eq. 15; (G3) MΩ_H/(J/M²) runs 0.25 (p→0)
toward ~0.37 (near-max, Pani-Cardoso Fig. 5). The κ_c
coupling-normalization factor ∈ ±{½,1,2} is selected by G2 and
documented.

## R1 measurement redesign + disclosure (2026-06-12)

The first G2/G3 design was contaminated (J-read error injected a
spurious 1/r³ component; G3 band lacked the p↔ζ mapping). The
redesign (in `20_rot_shoot.py`): G2 projects δω onto the basis
{AY ω-profile, 1/r³} so the 1/r³ admixture absorbs the J error.
Two transcription bugs were found and fixed against AY eq. 15
(independently re-fetched and re-verified): the AY bracket multiplies
M⁴/r⁵ in ω-space (not r³ — that is the g_tφ power), and the ω-space
sign is NEGATIVE (AY's +ζ correction to a negative Kerr g_tφ weakens
dragging) ⇒ gate requires c_ay < 0.

**Disclosure (criteria-integrity):** an intermediate version of the
gate used a 0.7% residual bound chosen *after* seeing a 0.5% result —
post-hoc, rejected. Replaced by a threshold-free rule: κ_c = argmin of
the projection residual among sign+sanity qualifiers, runner-up ≥1.5×
worse. The measured residual curve is V-shaped
(14.8 → 6.2 → 4.0 → 1.4 → **0.5** → 0.8 % across κ_c = −2…+2), with the
minimum at κ_c = 1.0 — i.e. PC's equation as written, no fudge factor.
G3's δΩ_H ∝ ζ² ratio test passes for ALL κ_c (1.79–1.86 vs predicted
1.61, within 20%) ⇒ G3 is a physics sanity gate, NOT a discriminator;
all selecting power is in G2. The sealed honesty test for v5 remains
R2's rotating holdout, built before any fitting.

## R0′ pre-registration: fingerprint derivation (queued)

Derive G₂/G₃ ourselves WITHOUT materializing the giant intermediates —
probabilistically-exact interpolation (Schwartz–Zippel), the
"terms-as-vector → random projections" idea (credit: Sumit's
vector-embedding intuition, 2026-06-12 discussion):

1. Ansatz: G₂, G₃ = unknown rational-coefficient combinations of a
   graded monomial basis in {r, e^Γ, e^Λ, e^φ, Γ′, Λ′, φ′, φ″, α′}.
2. Instantiate all background functions/derivatives with random exact
   rationals; evaluate the O(ε²) action's W-variation NUMERICALLY
   (every intermediate is one fraction — swell never happens).
3. Each probe yields one exact linear equation on the coefficients;
   solve the system; recover G₂/G₃ exactly.
4. Gates: (a) reproduces the GR limit symbolically; (b) matches the
   PC-transcribed G₂/G₃ identically — possibly modulo the static field
   equations (PC may quote on-shell-simplified forms; the check must
   be modulo the static EOM ideal — pre-registered wrinkle); (c) extra
   probes beyond the solve must all verify (overdetermination check).
   On success: κ_c = 1.0 upgrades from calibration to PREDICTION, and
   the v5 chain is self-contained again.

## R0′ result (2026-06-12, `21_rot_fingerprint.py`) — ALL GREEN, with honest deviations

What shipped is a **derive-and-verify at exact probes**, stronger in one
way and weaker in another than the registration above. It does NOT posit
a monomial basis and linear-solve; instead it derives the operator
directly per probe: build the perturbed metric as Taylor jets around an
exact-rational r₀, solve the STATIC EdGB field equations for the higher
jet coefficients (so every probe background is on-shell — this is what
discharges the "modulo static EOM" wrinkle automatically), compute the
O(ε²) action with an ε-graded curvature engine (intermediates stay
probe-sized — the swell never happens, as predicted), vary in w, and
read off G₂, G₃ exactly.

Gates passed: cross-product `G₂ᵈᵉʳ·G₃ˡⁱᵗ − G₃ᵈᵉʳ·G₂ˡⁱᵗ = 0` **exactly**
at 3 independent rational probes with nonzero coupling; GR limit
`G₂/G₃ = 4/r − (Γ′+Λ′)/2` symbolically; common factor matches
`(2/3)r₀²y₀^{−3/2}` (an overall factor is gauge for the quadrature —
the ratio is what the physics uses).

Deviations from the registration, disclosed: (1) no overdetermined
linear solve / held-out probes — the "G0" gate as implemented is 3
exact probe identities, not the registered N−K verification; (2)
e^Γ(r₀) is fixed to 1 in all probes (defensible as time-rescaling
gauge, untested); (3) the expected common factor was identified
empirically on the first probe, then verified exactly on all three.
Net: the PC transcription is now SELF-DERIVED at exact on-shell probe
points — κ_c = 1.0 stands as a probe-level prediction, not a mere
calibration. A full symbolic-form recovery (the registered linear-solve
version) remains available if ever needed.

## R2 result (2026-06-12, `22_rot_fit.py`) — the universal rotating formula, two sealed holdouts

**Disclosure first (criteria-integrity):** the first committed version
selected the winning structure by HOLDOUT error across a printed
6-combination grid — model selection on the sealed holdout, exactly the
post-hoc sin these docs forbid; the p=0.7 holdout also saw at least one
structure iteration (the p¹ scaling fix). Caught in audit, repaired
with a pre-registered protocol: winner selected by TRAINING error only
(holdouts never consulted during selection); frozen winner scored ONCE
on p=0.7 (disclosed as consumed) and ONCE on a FRESH sealed p=0.75
holdout built before any fitting. The train-selected winner is the
identical formula — and the fresh holdout is the number that counts.

With x ≡ 1 − r_h/r and H ≡ ω·r³/(2J):

    H(x, p) = 1 + (1 − x)²·a₁(p) / (1 + a₂(p)·x)
    a₁(p) = −0.119480·p − 0.006615·p²
    a₂(p) = +8.296716·p − 5.306262·p²

**Four numbers.** Horizon-regular by construction; → 2J/r³ as p→0 by
construction (a_i ∝ p). Scoreboard (max relative deviation, exterior to
50 r_h): training p ∈ [0.1, 0.6]: 0.1321%; p=0.7 holdout: 0.1551%
(consumed — reported, not load-bearing); **p=0.75 fresh sealed holdout:
0.1730%** — true extrapolation past both the training family and the
original holdout. The gap stands closed: no closed-form slow-rotating
EdGB frame-dragging profile existed in the literature. Truth tables:
`rot_truth_holdout.json`, `rot_truth_holdout2.json`.
