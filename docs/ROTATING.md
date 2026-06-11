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
- [ ] R0 · [ ] R1 · [ ] R2

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
