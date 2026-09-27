# SEALED — ansatz-machine's expectation for Manko–Novikov under the Morales–Ramis test

**Do not send to quantum or tabula. Do not discuss with them. Open only after quantum's verdict is committed.**
Written 2026-09-27, BEFORE the MN package was built (fleet plan chain 2, K5; Bridge-assigned, user-approved).

## What I expect, and how sure I am

1. **The truth: MN with a nonzero anomalous quadrupole is NOT (meromorphically) integrable.** Confidence
   **~90%**. Basis: numerical chaos. Gair, Li & Mandel (PRD 77, 024035, 2008) and Lukes-Gerakopoulos et al.
   (2010) report ergodic orbits, mainly in the region close to the source. This repo's own step 99 found no
   conserved quadratic for q ≠ 0. Also: nothing structural protects it, since there is no principal Killing–Yano
   tensor off Kerr. The ~10% is that the published chaos is numerical, so it is not a proof. I recall no
   Morales–Ramis proof for MN, but I have **not** swept for one; that is recalled, not searched.

2. **The tool: I expect the Kovacic route to be BLOCKED on MN, not to return a verdict.** Confidence **~80%**.
   Before building, I expect the MN metric functions to be **non-rational in (x, y)**. They contain
   R = √(x² + y² − 1) and, worse, exponentials of algebraic functions (e^{2ψ} with ψ ∝ P₂(xy/R)/R³, and the
   exponential factors in the a, b functions). If so, the normal variational equation along a generic particular
   solution has transcendental coefficients, and Kovacic, which needs coefficients in C(t), does not apply
   directly. I also expect the natural invariant sets (the symmetry axis, the equatorial plane) to keep an
   essential exponential (e^{c/x³} on the axis, e^{c/(x²−1)^{3/2}} on the equator), so restriction alone does
   not rescue rationality.

3. **If a verdict IS reached** (for example on a special invariant curve with a rationalising change of
   variable): I expect **non-integrable** (an identity component that is not abelian), ~85% conditional on a
   verdict.

## What would surprise me
- MN's components turning out rational in (x, y) in some chart I have not thought of (≤10%).
- A Kovacic verdict of "abelian identity component" on every curve tested: inconclusive, but surprising given
  the chaos.
- Any credible integrability result for MN at q ≠ 0 (≤3%). That would contradict the published chaos and my
  own step-99 null.
- The Kerr limit through the same pipeline failing to come out integrable/abelian. That would indict the
  tool, not the physics.
