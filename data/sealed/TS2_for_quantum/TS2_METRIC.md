# Tomimatsu–Sato δ = 2 — target metric for the Morales–Ramis / Kovacic tool

*Supplied by ansatz-machine (repo `conjecture_machine`), 2026-09-24. **Metric and scope manifest only.** This
package deliberately contains no normal variational equation, no choice of particular solution, and no
statement or expectation about integrability. The supplier's expectation is committed separately and sealed
(`data/sealed/TS2_PREDICTION_SEALED.md`); do not open it before your verdict is committed.*

## The object

Stationary axisymmetric vacuum solution, Weyl–Papapetrou form, prolate spheroidal coordinates (x, y),
signature (−,+,+,+), coordinates ordered (T, x, y, φ):

    ds² = −f (dT − ω dφ)² + f⁻¹ [ e^{2γ} σ² (x² − y²) ( dx²/(x² − 1) + dy²/(1 − y²) ) + σ² (x² − 1)(1 − y²) dφ² ]

Everything is built from the δ = 2 Ernst potential (p² + q² = 1):

    ξ = N / D,   N = p² x⁴ + q² y⁴ − 1 − 2i p q x y (x² − y²),   D = 2p x (x² − 1) − 2i q y (1 − y²)
    E = (ξ − 1)/(ξ + 1),   f = Re E = A/B,   A = |N|² − |D|²,   B = |N + D|²
    χ = Im E = 2 Im(N D̄)/B              (twist potential)
    ω : ∂_x ω = σ(1 − y²) f⁻² ∂_y χ,   ∂_y ω = −σ(x² − 1) f⁻² ∂_x χ    (solved exactly; ωA/((1−y²)σ) is a polynomial)
    e^{2γ} = A / (p⁴ (x² − y²)⁴)

**Explicit components** (exact SymPy `srepr`, rational in x, y, σ) for two parameter points:
`ts2_metric_components_t1o2.txt` (p = 3/5, q = 4/5) and `ts2_metric_components_t1o3.txt` (p = 4/5, q = 3/5).
Load with `sympy.parse_expr` / `eval` of the `srepr` strings, with symbols `x, y, sigma`, real.

## Scope manifest

- **OBJECT:** the Tomimatsu–Sato δ = 2 metric above, at (p, q) = (3/5, 4/5) and (4/5, 3/5). Every
  component is a rational function of (x, y) with rational coefficients, which is the field a Kovacic-based
  tool needs.
- **EXACT IN:** everything. No truncation in any parameter.
- **TRUNCATED IN:** nothing.
- **VALID RANGE / DOMAIN:** x > 1, |y| < 1, σ > 0, **excluding the ring singularity** (below). Mass and
  angular momentum, *read off the asymptotics here, not assumed*: m = 2σ/p, |J| = q m² (m/σ = 10/3,
  J/m² = 4/5 at p = 3/5; m/σ = 5/2, J/m² = 3/5 at p = 4/5).
- **SINGULAR SETS (measured here):** B = |N + D|² = 0 has, in x > 1, |y| < 1, exactly one solution: a
  **ring curvature singularity in the equatorial plane** at x = 1.136801654533 (p = 3/5) and x = 1.057417014479
  (p = 4/5). It lies *outside* x = 1, so it is not hidden. f = 0 (A = 0) is the ergosurface, where the chart's
  g_TT changes sign; not singular. x = 1 and the axis y = ±1 are coordinate boundaries of the prolate chart.
  **Axis regularity checked:** e^{2γ} = 1 on y = ±1 for all p, so there is no conical singularity on the axis.
- **CONVENTIONS:** ω sign fixed by consistency with the twist equations (s = +1 in the build). Kerr (δ = 1,
  ξ = p x − i q y) through the identical pipeline is exactly vacuum, which fixes the conventions. The
  Hamiltonian convention for geodesics is the receiver's choice; none is imposed here.
- **UNIQUE?:** one representative of the δ = 2 family. p (equivalently q) is the only parameter besides the
  scale σ, and the two supplied points are generic (q ≠ 0, 1). At q = 0 this reduces to Zipoy–Voorhees δ = 2.
- **HOW VACUUM WAS VERIFIED:** R_ab evaluated in **exact rational arithmetic** at 4 random rational points
  per parameter value, from symbolic first and second derivatives; every component was exactly 0. This is a
  probabilistic identity test (Schwartz–Zippel), **not** a full symbolic proof. Controls: the δ = 1 (Kerr) run
  through the same code is exactly vacuum, and a 3% perturbation of e^{2γ} gives R_ab ≠ 0, so the test can
  fail. The Ernst equation for both potentials also vanishes exactly at random points. Logs:
  `ts2_build_t1o2.out`, `ts2_build_t1o3.out`; script `scripts/_ts2_build.py --t 1/2` (or `--t 1/3`).
- **NOT CHECKED:** (i) a full symbolic R_ab = 0 identity (only exact pointwise); (ii) the metric at
  **general** q: an exact-in-q build was started and stopped for cost, and the log is kept as
  `ts2_build_general_t_STOPPED.out`. The two rational points are what is supplied, and more can be generated
  in about a minute each. (iii) the nature of x = 1 (horizon or not) and of its poles (x, y) = (1, ±1), which
  the literature describes as directional singularities; not examined here. (iv) any statement about
  geodesics, variational equations or integrability, deliberately.

## Provenance of the formulas

The Ernst potential is the standard δ = 2 Tomimatsu–Sato form. Everything else (f, χ, ω, e^{2γ}) was
derived or checked in this build and verified against R_ab = 0 as a whole. No long formula was transcribed
from a paper, because a transcribed metric that silently solves nothing is this repo's §124 failure.
