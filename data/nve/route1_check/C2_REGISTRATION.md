# C2 registration: a k-uniform M machinery (a NEW registered stage after S1). Committed BEFORE any C2 code or measurement

**Office ansatz-machine (Claude Opus), 2026-11-28.** Go from the Bridge, under Sumit's delegation; production still goes
to Sumit. Up to 2 Mac mini cores, nice 10, pause-only guards.

**Time box (kill criterion, a state AND a date):** if C2's pilots have not certified at least one of the three P boxes
by **2026-12-12**, STOP. The top of the range then goes back to Sumit as "parked; numerical grade only", his
good-enough line of 11-25.

## Why it matters
- v7's new parts passed: V1 (both spins), V2 (3/5) and P-B, with the c0 evaluator, the field, the region-B port and
  the second-derivative bound all read as sound.
- Stage P and S1 showed the blocker is the INHERITED M machinery. v2/v4's crude dq bound encloses c0 over Z × K by a
  second-order k-Taylor, c0(k_c) + dk·D0 + dk²E/2, and evaluates dq/dk = (3/8)λλ' by plain ball arithmetic. That
  refuses boxes where the true G-zeros are 0.27–0.45 away, and where it does evaluate, it yields M_F up to 1e253
  (region B, depth 2).
- **Without a k-uniform M that keeps the k-correlation, no top segment can certify,** and the claim's top stays
  numerical.

## Step 0: measure first (a diagnostic; minutes; certifies nothing)
**Question:** on the refused boxes, is the inflation dependency (an artifact) or genuine?
- **Boxes:** P1's refused circle box (1.3213 + 0.2754i, k_c 79/20); P2's base-point box (1.5032, k_c 83/20); S1's
  1e253 segment (k_c 331/80; its largest per-step bound).
- **For each, three numbers:**
  - (a) the crude `dq_sup` value on Z × K (or "refused");
  - (b) the SAMPLED sup of |dq/dk| over Z × K: point k on a 9 × 9 grid of K and 5 points of Z, with dq/dk from the
    field at point k (V1/V2-validated) and an exact formula, no k-Taylor;
  - (c) the sampled sup of |q|, as a sanity check.
- **Reading, fixed now:**
  - (b) finite and (a)/(b) ≥ 1e3, or (a) refused while (b) is finite: **dependency artifact**, and C2's design
    proceeds;
  - (b) itself ≥ 1e6 × its value at k_c (q genuinely explodes on K): **geometry**. No k-uniform rewrite can help. C2
    stops, and the top is parked (numerical grade).
- Each box gets a verdict; the majority decides, and a split is reported.

## Design (chosen after step 0; weighed now)
**(A) Taylor models in dk (Berz–Makino), the Bridge's suggestion.**
- Carry c0, c0', the field's √B, G1, G2, λ, λ' and q as polynomials in dk = k − k_c of degree d, with a rigorous
  remainder ball (acb_poly coefficients plus an error ball).
- Bound sup over K of |dq/dk| by range-bounding the TM derivative.
- **Pro:** keeps the k-correlation through every operation, which is the textbook cure for exactly this blow-up.
- **Con:** needs TM arithmetic with remainders for products, √ and division (1/G) inside the field's Taylor
  propagation, which then becomes bivariate (z-series × dk-polynomials). That is a large new surface, every operation a
  place for a remainder error.

**(B) Cauchy in k from a larger circle (the K-uniform route, reusing validated parts).**
- sup over K of |∂q/∂k| ≤ sup over |k − k_c| = R' of |q(Z, k)| / (R' − R_K), with R_K the radius of the disc
  containing K and R' = 1.5·R_K. This is Cauchy's estimate for a function holomorphic in k on the disc of radius R'.
- The circle is covered by n_arc small k-balls. On each, q(Z, k-ball) comes from the V1/V2-validated field at that
  k-ball. A small radius means little dependency, and there is no k-Taylor.
- Needs a **holomorphy certificate:** G1, G2 ≠ 0 on Z × disc(R'), by a k-sub-box cover of the disc (adaptive). Only
  nonzero-ness, not magnitude, which is far less sensitive to dependency.
- **Pro:** the new mathematics is one textbook estimate plus one certificate, and the evaluators are already read and
  tested.
- **Con:** compute, since n_arc fields (say 16–32) walk the loops in parallel, an estimated 5–30× the current prove.

**Provisional choice: (B)**, because its new-mathematics surface is the smallest, and the review discipline (a read per
new piece) favours that. **(A)** if (B)'s cost probe exceeds 30× the current prove, or its bound is still too loose.
The choice is fixed in an addendum after step 0 and a one-box cost probe, before any pilot.

## Controls (must FIRE before any pilot)
- **Shrunken bound:** the new sup |dq/dk| divided by 1e6 must be caught by v6's sampled-maximum check on the ellipse,
  or, if that cannot see it, by a direct check against step 0's sampled values on the same box.
- **Planted spike:** a step box containing a true zero of G1 (r+), with K the pilot k-box, must be refused by the
  holomorphy certificate (B) or produce an unbounded TM remainder (A).
- **Positive check:** on the three step-0 boxes the new bound must be ≥ step 0's sampled sup, and within 1e3 of it (so
  it is not vacuous).

## Pilots (one attempt each; the same boxes as P)
P1 (circle, k_c 79/20, half 1/20), P2 (region B, k_c 83/20, half 1/20), P3 (region B, k_c 30/7 − 1.5e−3, half 1/2000).
Each runs prove, then verdict with full controls, then the engine gate.

| certified | reading |
|---|---|
| 3 | **C2 works**: a production projection goes to the Bridge and Sumit |
| 1–2 | **partial**: report and re-gate |
| 0 by 2026-12-12 | **STOP**: the top is parked, numerical grade |

## Order
1. This registration.
2. Step 0, with its result committed.
3. The design choice as an addendum, with a cost probe.
4. Code.
5. A non-author read of the design and the code.
6. Controls.
7. Pilots.

## Predictions

| | P |
|---|---|
| step 0 reads "dependency artifact" on at least 2 of the 3 boxes | 70% |
| (B) chosen after the cost probe | 60% |
| at least 1 pilot certifies by 2026-12-12 | 40% |
| all 3 certify | 15% |
