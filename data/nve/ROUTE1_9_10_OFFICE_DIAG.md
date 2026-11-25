# Office notes on Fable's spin-9/10 segment attempt (seal 620c470, results d18de63), 2026-11-26

## (1) The spin-3/5 reproduction after the v2 change, and the restore: CONFIRMED
- **The code change is inert at spin 3/5.**
  - A becomes arb("3")/arb("5"), the same exact rational.
  - `LIMZ = max(1.0, a/0.855·1.005)` = 1.0, as before.
  - `safe_step` only turns a would-be crash into a refused box.
- **Clean checkout of d18de63, NVE_SPIN=3/5:** I reran prove, `verdict partB`, `nodes arb` (all 36 recomputed) and
  `verdict arb`. The proved-M JSON, both verdict JSONs and all 36 node records are BYTE-IDENTICAL to d855810. Both
  verdicts are CERTIFIED.
- **`route1_floats.json` at d18de63 is identical to 604d520,** so the self-reported overwrite was restored cleanly.

## (2) Diagnosis: the "46× harder circle" is an ENCLOSURE ARTIFACT, not intrinsic
**Intrinsic constants, by a float measurement.** Source: `scripts/_nve_route1_circle_diag.py` →
`route1_circle_diag.out`, the 50-digit engine, 720 points on the circle, k_c = 21/20.
- dq/dk is a central difference in k, and (v1, v2) is the reference first row.
- The base-basis constant is tr W, and the optimised constant-gauge constant is 2√det W, with
  W = Σ |dq/dk| |dz| r†r. That is exactly the minimum Fable's gauge achieves at a point k.

| spin, R0 | intrinsic constant per unit k (base / optimised gauge) | ∫\|dq/dk\|\|dz\| | Fable's certified (optimised, K a point) | inflation |
|---|---|---|---|---|
| 3/5, 1.35 | 0.41 / 0.36 | 0.155 | 10.5 | ×29 |
| 9/10, 1.2639 | 0.89 / 0.65 | 0.276 | 478 | ×735 |
| 9/10, 1.35 | 0.94 / 0.75 | 0.324 | — | — |
| 9/10, 1.45 | 1.15 / 1.04 | 0.521 | — | — |

- **The intrinsic constant at spin 9/10 is only about 1.8× the spin-3/5 one.**
- **Where it peaks.** At spin 9/10 with R0 = 1.2639, the integrand peaks at θ ≈ ±90° (40% of the base-basis
  integral comes from [45°, 135°] and 32% from [−135°, −45°]). That is the direction of the inner poles ±ia, which are
  0.364 away, against 0.75 at spin 3/5. So Fable's "inner ring" guess is right for the profile, but it accounts for a
  factor of about 2, not 46.
- **A larger circle does not help intrinsically.** At R0 = 1.45 the peak moves to θ ≈ 0, toward r₊ and p₊.

**The inflation, located.** Source: `scripts/_nve_route1_box_inflation.py` → `route1_box_inflation.out`, Fable's own
`dq_sup` from d18de63.
- At a point, its enclosure equals my float value to 2–3 digits: 0.0568 against 0.0569; 0.066/0.070 against
  0.067/0.072.
- On a box of half-side 0.002, about one step, it inflates as follows:

  | spin | θ = 22.8° | θ = 90° | θ = 180° |
  |---|---|---|---|
  | 3/5 | ×19 | ×7.6 | ×2.1 |
  | 9/10 | **×5,900** | ×56 | ×2.1 |

- This is the dependency (wrapping) effect of evaluating the Laurent-series c0 and the rational expression for dq/dk
  directly on a box. It is worst where the Laurent ratio is large: ρ_c/R0 = 0.71 at spin 9/10, against 0.44 at 3/5.
  It is also worst where the denominators G1 and G2 are small, toward the outer singular points.
- **So the proved M, the node count and the cost estimates are dominated by enclosure overestimation.** Its effect is
  modest at spin 3/5 (about 30× on the circle constant) and dominant at spin 9/10.

**The fix, not built.** Enclose dq/dk on each step box in a CENTRED (mean-value) form:
dq/dk(Z) ⊂ dq/dk(z_m) + (Z − z_m)·sup|∂_z dq/dk|. Alternatively, subdivide the step box, or use a Taylor model in z.
- Evaluated at the point, the enclosure already agrees with the true value, and the box term is only O(box width).
- Expected effect: the certified constants fall toward the intrinsic ones. At spin 9/10 the circle constant would fall
  from 478 toward the order of 1.
- That would collapse n from about 140 to about the spin-3/5 count, and cut the full route-(i) cost by an order of
  magnitude or more at every spin.
- The lasso constant was not measured intrinsically here; the same fix should shrink it too.

## (3) Is the 7.5-core-hour spin-9/10 segment worth a slot? Not yet
- It would certify one segment with an M inflated by orders of magnitude, at ~7.5 core-h. The centred-form fix (a
  small code change) should bring the same certificate down to minutes.
- **Recommendation:** first build the centred enclosure, re-measure the certified constants at both spins, and only
  then decide on long runs. The ~250–300 core-h figure for spin 9/10 region A should not go into the route-(i)
  registration as it stands; it is an artifact estimate.
- **For the registration:** carry both spins' constants in two columns, certified-as-coded and intrinsic (float), with
  this note. The intrinsic values are 0.36/0.65 on the circle at spins 3/5/9/10.
