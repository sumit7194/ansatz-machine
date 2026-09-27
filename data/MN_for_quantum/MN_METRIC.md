# Manko–Novikov (q-anomaly subclass): target metric for the Morales–Ramis / Kovacic tool

*Supplied by ansatz-machine (repo `conjecture_machine`), 2026-09-27. **Metric and scope manifest only.** There
is no normal variational equation here, no choice of particular solution, and no statement or expectation about
integrability. The supplier's expectation is committed and sealed separately; do not ask for it before your verdict
is committed.*

## Headline for feasibility

**The MN metric functions are NOT rational in (x, y) for q ≠ 0.** They are not even algebraic. They contain
R = √(x² + y² − 1) and exponentials of non-constant algebraic functions, for example
e^{2ψ} = exp(2β P₂(xy/R)/R³). These do not become rational on the natural invariant sets either:
- on the symmetry axis y = 1: e^{2ψ} = exp(2β/x³), an essential singularity at x = 0;
- on the equator y = 0: e^{2ψ} = exp(−β/(x² − 1)^{3/2}).

A Kovacic-based tool, which needs coefficients in C(t), therefore cannot be applied to MN's variational
equations as they stand. Only the Kerr limit (q = 0), supplied below as a control, is rational.

## The object

Stationary axisymmetric vacuum, Weyl–Papapetrou form, prolate spheroidal (x, y), signature (−,+,+,+), coordinates
(t, x, y, φ):

    ds² = −f (dt − ω dφ)² + k² f⁻¹ [ e^{2γ} (x² − y²) ( dx²/(x² − 1) + dy²/(1 − y²) ) + (x² − 1)(1 − y²) dφ² ]

    χ = a/M,  α = (−1 + √(1 − χ²))/χ,  k = M(1 − α²)/(1 + α²) = √(M² − a²),  β = q M³/k³
    R = √(x² + y² − 1),  u = xy/R,  P_l = Legendre
    ψ = β P₂(u)/R³
    a_ = −α exp(−2β(−1 + Σ_{l=0}^{2} (x − y) P_l(u)/R^{l+1})),   b_ = α exp(2β(1 + Σ_{l=0}^{2} (−1)^{3−l}(x + y) P_l(u)/R^{l+1}))
    A = (x² − 1)(1 + a_b_)² − (1 − y²)(b_ − a_)²
    B = (x + 1 + (x − 1) a_b_)² + ((1 + y) a_ + (1 − y) b_)²
    C = (x² − 1)(1 + a_b_)(b_ − a_ − y(a_ + b_)) + (1 − y²)(b_ − a_)(1 + a_b_ + x(1 − a_b_))
    f = e^{2ψ} A/B,   ω = 2k e^{−2ψ} C/A − 4kα/(1 − α²)
    e^{2γ} = [(x² − 1)/(x² − y²)] · exp(3β²(P₃² − P₂²)/R⁶ + 2β Σ_l[(x − y + (−1)^l (x + y)) P_l/R^{l+1} − 2] + 8β)
             · A/((x² − 1)(1 − α²)²)

The final **+ 8β** is the one change from the published γ′. It fixes γ's additive constant so that e^{2γ} → 1 at
infinity. The vacuum equations cannot see this constant; asymptotic flatness and axis regularity can, and both are
checked below.

**Explicit components** (SymPy `srepr`; true functions of x, y with `sqrt` and `exp`; symbols `x, y` positive):

| file | M | a | β | q = βk³/M³ | k | α |
|---|---|---|---|---|---|---|
| `mn_metric_components_p1.txt` | 5 | 3 | 1/5 | 64/625 | 4 | −1/3 |
| `mn_metric_components_p2.txt` | 13 | 5 | −1/3 | −576/2197 | 12 | −1/5 |
| `mn_metric_components_KERR_p1.txt`, `_KERR_p2.txt` | same | same | 0 | 0 (Kerr control) | | |

Parameters were chosen so that k and α are rational. The two points have opposite signs of q.

## Scope manifest

- **OBJECT:** the MN q-anomaly subclass above, at the two parameter points and their Kerr limits.
- **EXACT IN:** everything. There is no truncation in any parameter; the functions are closed-form.
- **TRUNCATED IN:** nothing.
- **RATIONAL IN (x, y)?** **No** for q ≠ 0 (see the headline). Yes for the Kerr controls.
- **VALID RANGE / DOMAIN:** x > 1, |y| < 1, excluding the singular sets below. Mass and angular momentum were
  *read off the asymptotics here* (numerically, x = 10⁷): mass = M and J = aM at both points (p1: 5, 15;
  p2: 13, 65).
- **SINGULAR AND PATHOLOGICAL SETS (measured here, numerical grid scan, `mn_singular_scan.out`):**
  - **R = 0, i.e. (x, y) = (1, 0):** the exponents diverge like R⁻¹² (for example, −3·10⁴ at R = 0.1 for p1), so the
    metric is essentially singular there. f is non-finite or larger than 10¹² in a neighbourhood reaching
    R ≈ 0.22 (x − 1 ≲ 6·10⁻³, |y| ≲ 0.22 for p1; x − 1 ≲ 2·10⁻², |y| ≲ 0.15 for p2).
  - **Closed timelike curves, g_φφ < 0:** present for q ≠ 0 and absent for Kerr. p1: x from 1 to 1.075,
    |y| ≤ 0.47. p2: x from 1 to 1.122, |y| ≤ 0.49.
  - **Ergoregion, f < 0:** p1 out to x = 1.354; p2 out to x = 1.174. It touches x → 1. This is not a
    singularity.
  - **B = 0** (would make f blow up): not found on the grid (min |B| = 1.6·10⁻², 3.8·10⁻²).
  - **x = 1:** a horizon for Kerr. For q ≠ 0 its nature is **not examined here** (the literature describes the
    MN horizon as destroyed); treat x = 1 as a boundary of the valid domain.
  - **Axis y = ±1:** **regular**: e^{2γ} = 1 exactly on both half-axes, at both points, so there is no conical
    singularity.
- **CONVENTIONS:** the ω sign and all other conventions are fixed by the Kerr limit. At q = 0 the metric equals
  exact Kerr (Boyer–Lindquist, r = kx + M, cos θ = y), component by component, symbolically, at both (M, a). The
  geodesic Hamiltonian convention is the receiver's choice.
- **UNIQUE?:** MN has more general members; this is the q-anomaly subclass with the three parameters M, a, q.
- **HOW VACUUM WAS VERIFIED:** exactly. The functions were placed in the differential field Q(x, y, R, E_A, E_B,
  E_P, E_Q): R and four independent exponentials are symbols, differentiated by the chain rule. R_ab was evaluated
  in exact rational arithmetic at 3 random points per parameter set (with R² = x² + y² − 1 enforced) and was
  exactly 0 at every point. A formal zero implies the true zero, so the test is **sound**. It is a probabilistic
  identity test (Schwartz–Zippel), **not** a full symbolic proof. **Controls that must fail, and did:** a
  1 + y²/30 factor on e^{2γ} (R_ab ≠ 0 at both points), and a mismatched exponent in f (R_ab ≠ 0). The Kerr limit
  is exactly Kerr. Log: `mn_build.out`; script: `scripts/_mn_build.py` (11 s, 70 MB).
- **PROVENANCE, stated plainly:** the formulas are the **published** MN form, as used by Gair, Li & Mandel (PRD 77,
  024035, 2008). That makes them a transcription, not a derivation from the Ernst equation. Everything above
  verifies the transcription (exact vacuum, exact Kerr limit, exact axis regularity) rather than trusting it. The one
  correction (+8β in γ) is explained above.
- **NOT CHECKED:** (i) a full symbolic R_ab = 0 identity (only exact pointwise in the formal field); (ii) the nature
  of x = 1 for q ≠ 0; (iii) the singular-set extents are grid measurements, not exact loci; (iv) general (M, a, q)
  (two points are supplied, and more take seconds); (v) any statement about geodesics, variational equations or
  integrability, deliberately.
