# Ansatz-free prolongation bounds (Vollmer method), pre-registration — 2026-10-10 ~02:10, BEFORE any new-territory run

Method: `scripts/_kt_jet.py`. The M-th prolongation of {H, I} = 0 at one regular point, for I polynomial of degree d
in the momenta with coefficients any smooth functions of (x, y), i.e. invariant under d_t and d_phi. Exact over GF(p),
rank by FLINT (native/flint_rank) or the in-house Rust dense engine (rust/ktdense). #columns − rank is an UPPER
BOUND on the number of such Killing tensors; when it equals the trivial count, nonexistence is PROVED locally, with no
basis box and no denominator.

## Validation already passed (by reproduction; logs in data/jet/validation.out)
- Kerr (M=1, a=1/2), point (3, 1/3), ranks 1–4: bounds 2, 5, 8, 14 = the true counts, Carter included.
- ZV δ=2, rank 6, point (1/2, 2): 1680×1584 with rank 1568 → 16, and 1680×1440 at full rank → 0. These are exactly
  Kruglikov–Matveev's matrix sizes and Vollmer's result.
- TS δ=2, p = 3/5 (Vollmer's metric; same p convention, p multiplies the x-terms, checked in his eq. 9d), rank 7,
  point (1/2, 2): 2880×2700 → 20 = trivial, and 3060×2700 → 0. That is Vollmer's Theorem 1, reproduced.
- Sabotage: Kerr with g^xx·(1 + x·y/7) (non-separable) → bound 4, so Carter disappears as it must. A separable
  sabotage, g^xx·(1 + x/7), kept Carter at 5, consistent with §139.
- Engines: FLINT and Rust give identical bounds (TS p=3/5 r7; Kerr r4 on prime 1).

## Predictions for new territory (sealed by this commit)
| target | ranks | predicted bound | confidence |
|---|---|---|---|
| TS δ=2, p = 4/5 (q = 3/5): our §148 point, not in print | 1–10 (higher if cheap) | = trivial count at every rank | ~95% |
| TS δ=2, p = 3/5 (Vollmer's point) | 8–10 (beyond his 7) | = trivial count at every rank | ~95% |

Trivial count: the number of p_t^a p_phi^b H^c with a + b + 2c = d (16 at d = 6, 20 at d = 7, 25 at d = 8).

## Protocol
- Point (1/2, 2) as in Vollmer, plus a second point (3, 1/3) inside the physical domain. Prime 0, plus prime 1 for any
  bound above trivial.
- M = d by default. A bound above trivial at M = d is NOT a positive: rerun at M = d+1, d+2, then a second point and
  prime. Only a bound that survives all of these is reported, and then to the Bridge for an independent check, with no
  claim before that.
- Scope of a null: "no Killing tensor of valence d invariant under d_t, d_phi beyond the trivial ones, locally near
  the point (smooth coefficients of any form)". Non-invariant Killing tensors are NOT covered (Kruglikov–Steneker).
  Global statements need analytic continuation, which is not claimed here.
