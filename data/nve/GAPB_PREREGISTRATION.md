# Gap B: argument-principle zero count of F(k) = tr[M1, M0](k) − 2 on a complex-k region (pre-registration, 2026-11-21)

**Ask.** Bridge, GO received 2026-11-21 ~09:20, after our second reading of the relayed all-spin proof (gap B in
`T11_LOOP_REVIEW.md`). The relayed proof calls the k-values where its continuation could fail ("K_bad") artefacts. A
finite test is to count the zeros of F on a closed k-region. If the count is exactly 2 (the known double zero at k = 0),
no k in the region makes this pair of monodromies reducible.

**Fixed.** Spin a = 3/5, M = 1, E = 4/5 (a bound orbit). This is the §159 lower-axis first-order NVE, unchanged: f0 = 1 −
1/(z − ia) − 1/(z + ia), the c0 Laurent series, 50 digits, Taylor order 50 (`_nve_lower.Walker`).

## Measured before registration (geometry and timing only; no F value outside the already-known real-k ones)
- **Reproduction.** `scripts/_nve_lower_kc.py` (complex-k c0: the radicand numerator is linear in k) reproduces the
  registered `lower_comm` value of F at k = 1/10 to 18 digits. At k = 0.1 + 0.5i, steps 0.35 and 0.2 agree to 18
  digits.
- **Cost.** About 10 s per k once singular points are Newton-tracked. The full search used before took ~390 s.
- **Why M1 must be adaptive.** The registered rectangle M1 (encloses {r+, p+}) stops being valid on the real line near
  k ≈ 3.5, because p− crosses its edge (`kc_geometry.out`). M1 is therefore the based lasso `capsule_lasso(r+, p+)`:
  - a straight tail from b = 1.35 to the nearest point of the capsule at distance δ around the segment [r+, p+];
  - δ = min(0.15, 0.4 × clearance of the other points).
  Its based class is constant while nothing touches it.
- **Extra inner points at k < 0** (`kc_extras` measurements, recorded in the run log):
  - A G1 zero and a G2 zero (in conjugate pairs) split off from ±ia and move outward as k decreases. Their |z| is
    0.67/0.65 at k = −1, 0.87/0.80 at −5, and 1.05/0.94 at −10.
  - The outer count reaches 4 zeros of G1 in 1.3 < |z| < 60 by k = −20, so they cross the M0 circle at some k between
    −10 and −20. They lie inside M0 on the region below, but they must be passed to the walker for step control.
- **Near 30/7 the series fails.** ρ_c(k) (the Laurent radius) grows: ρ_c(4.05) = 0.85, ρ_c(4.1) = 1.05.

## The region and the functions
- **Region** R = rectangle with corners −10.5 ± 1i and 4.05 ± 1i. Its boundary is sampled counter-clockwise at spacing
  0.25, then refined adaptively (below). R contains the real interval [−10.5, 4.05], including the special point k = 4.
- At each boundary k:
  - Newton-track r+, r−, p+, p− and the extras. An extra is dropped while |z| < ρ_c + 0.05, then re-seeded at radius
    ρ_c + 0.08 from its last argument.
  - Compute M0 (circle |z| = 1.35, based at 1.35) and M1 (capsule lasso), and record:
    - F = tr[M1, M0] − 2 (primary);
    - T0 = tr M0, and also tr M0 − 2;
    - T1 = tr M1.
- **Counts** are total arg change / 2π for:
  - F (primary);
  - tr M0 − 2 (consistency; the known double zero at 0 gives ≥ 2);
  - T0 and T1 (imprimitivity: if both have no zeros in R, then two traces of the pair are nonzero throughout R).

## Guards (any failure → VOID)
- **G-geo, over R and not only its boundary.** On an interior grid (Re step 0.5, Im step 0.25) plus the boundary
  samples:
  - lasso clearance (the other outer points' distance from the M1 path) ≥ 0.05;
  - outer points' |z| ≥ 1.35 + 0.2;
  - extras' |z| ≤ 1.25;
  - ρ_c ≤ 1.1;
  - Newton converges for every tracked point.
- **G-count.** Argument-principle counts of G1 and G2 zeros at 12 sparse points (the 4 corners, the 4 edge midpoints, k
  = 0, 4, −5, −10). Required:
  - (2, 2) in 1.3 < |z| < 60;
  - the inner annulus count (ρ_c + 0.05 < |z| < 1.3) equals the number of tracked extras.
- **G-step.** At every 4th boundary sample, F, T0 and T1 at step 0.2 agree with step 0.35 to a relative 1e−15.
- **G-arg.** After refinement, every consecutive |Δarg| ≤ π/4 for F, tr M0 − 2, T0 and T1. Refinement inserts midpoints,
  to at most 5 levels. If the bound cannot be met, the result is UNDETERMINED rather than VOID.

## Controls (run first)
| control | what | must give |
|---|---|---|
| C0 reproduction | capsule-lasso F at k = 1/10 vs the registered rectangle value 0.00196656555091338 + 0.00101256196325471i | agreement to 1e−15 (same based class) |
| C1 local count | circle \|k\| = 0.3, 16 samples, refined | count(F) = 2 and count(tr M0 − 2) = 2 (the known k² zeros) |
| C2 counter must-detect | on R's final samples: count of F·(k − ks), ks = −3 + 0.5i, inside R | count(F) + 1; and F/(k − ks) gives count(F) − 1; ks = 6 + 3i, outside R, leaves it unchanged |
| C3a must-fail (guard) | G-geo on a rectangle widened to Re k ∈ [−25, 4.05] | guard FIRES (extras cross 1.25) → VOID |
| C3b must-fail (guard) | G-geo on a rectangle widened to Re k ≤ 4.2 | guard FIRES (ρ_c > 1.1) → VOID |

## Outcomes (for R, E = 4/5, spin 3/5)
- **NO SPECIAL k IN R:** count(F) = 2, with all guards and controls passing. Then the pair ⟨M1, M0⟩ is irreducible at
  every k ≠ 0 in R. If also count(T0) = count(T1) = 0, it is not imprimitive anywhere in R.
- **SPECIAL k FOUND:** count(F) > 2. The zeros are then located by sub-rectangle counts, real ones listed first. A
  zero of this F means only that this pair is reducible there, not that the group is VA. Each one is a candidate for a
  second-pair check.
- **VOID:** any guard or control fails. **UNDETERMINED:** G-arg cannot be met.

## Scope
- One (E, spin) only, a bounded k-region only, and a floating-point argument principle (50 digits), not an interval
  certificate.
- The finite-group case is not counted here. Im T1 ≠ 0 is recorded on the real-k samples as evidence only.
- Nothing is claimed for k < −10.5, where the extras approach M0 and a different M0 is needed, or for k > 4.05.
- **Environment:** Python 3.14.5 (.venv), mpmath 1.3.0, sympy 1.14.0, numpy 2.4.6; 1 core, nice 10; estimated about 1 h.
