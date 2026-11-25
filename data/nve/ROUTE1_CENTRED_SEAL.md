# SEAL (office, 2026-11-26, BEFORE any run): the centred enclosure of dq/dk, predictions

Branch `office/2026-11-26-centred-encl` from Fable's d18de63. Method to be built: per step, a Taylor series of dq/dk
in z at the step midpoint (order N, k a ball over each k-sub-box), plus a Cauchy remainder from Fable's own crude
enclosure on a box 4x larger (which also certifies holomorphy). Proof stage only; certified constants are the
optimised-gauge Dyson exponents per unit k ON the k-disc (rho = 4 row unless stated).

| quantity | v2 as coded (Fable) | intrinsic (office float, at the point k_c) | PREDICTION with the centred enclosure |
|---|---|---|---|
| circle, spin 3/5 | 14.3 (disc) / 10.5 (point) | 0.36 | 0.4 – 3 |
| lasso, spin 3/5 | 72.6 (disc) / 45.8 (point) | not measured | 5 – 40 |
| circle, spin 9/10 | 478 (point) | 0.65 | 0.7 – 10 |
| lasso, spin 9/10 | 83.6 (point) | not measured | 5 – 60 |
| n (rho = 4 or best), spin 3/5 | 24 | — | 10 – 18 |
| n (best rho), spin 9/10 | 140 | — | 12 – 40 |

- P(n at 9/10 <= 40) = 75%.
- Spin 3/5 must still pass every v2 check, with n <= 24 and M_F <= 6.57e10 (no weaker).
- The gauge factors (||M_c C|| ||C^-1||) are NOT expected to change much; if n stays high, they or the lasso will be why.
