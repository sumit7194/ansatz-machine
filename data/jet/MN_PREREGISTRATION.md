# Manko–Novikov: ansatz-free prolongation bound — pre-registration, 2026-10-10, BEFORE any MN Killing-tensor run

Ask: the Bridge, 2026-10-10 (option A of two; the user asked that the machine be kept busy overnight). Motivation:
- Brink, *Spacetime Encodings IV* (arXiv:0911.1595), suggests from numerics (his own and Gair–Li–Mandel 2008) that
  many stationary axisymmetric vacua may possess a FOURTH-order Killing tensor, a generalised Carter constant. MN is
  the standard test case.
- Quantum has a Morales–Ramis obstruction for MN, which covers meromorphic integrals near a particular solution.
- A literature sweep (today) found no polynomial-integral / Killing-tensor nonexistence result for MN at any rank.

This is the §149 method (`scripts/_kt_jet.py`, validated there by reproducing Kruglikov–Matveev and Vollmer) extended
to non-rational metric functions.

## Object
MN q-anomaly subclass, exactly as built and verified Ricci-flat in `scripts/_mn_build.py` (data/MN_for_quantum/):
- p1: M = 5, a = 3, β = 1/5 (q = 64/625);
- p2: M = 13, a = 5, β = −1/3 (q = −576/2197);
- controls: the same with β = 0, which is Kerr.

## Method, and why the bound stays an UPPER bound with exponentials
The jet point (x0, y0) is chosen with R0 = √(x0² + y0² − 1) rational. Every function is evaluated as a truncated Taylor
series mod p:
- R by the binomial series about R0;
- each exponential E_i = exp(Z_i) as exp(Z_i(P)) · exp(Z_i − Z_i(P)), the second factor by its power series.

The constants exp(Z_i(P)) are the only transcendental inputs. Each Z_i(P) is rational. With N the lcm of their
denominators over ALL exponentials appearing (E_A, E_B, E_P = e^{2ψ}, E_Q, the last three also inside e^{2γ}), every
constant equals T^{n_i} with T = e^{1/N} and n_i = N·Z_i(P) an integer. So every matrix entry lies in Q[T, 1/T].
- T is transcendental (Lindemann), so the TRUE rank equals the rank over Q(T).
- Substituting T ↦ t, a random nonzero element of GF(p), can only LOWER the rank. So cols − rank_p ≥ the true bound:
  still a valid upper bound.
- Treating the E_i as INDEPENDENT random values would compute the generic rank over Q(E_1..E_4). That can exceed the
  true rank, since the true constants are multiplicatively dependent, and would UNDERSTATE the bound. It is NOT used.

Assertions: t ≠ 0, and every denominator (metric, series inversion, the factorials and binomials of the series) is
nonzero mod p; the code refuses otherwise. Each verdict is the MINIMUM bound over 2 independent draws (prime 0 with t
from seed 1, prime 1 with t from seed 2), since a single draw can only over-state.

## Controls (all must pass before any MN number is read)
1. Inverse-metric formula: g^ab as assembled from (f, ω, e^{2γ}) equals SymPy's inverse of `_mn_build.metric`
   exactly, at a rational point with random rational E values (this is an identity in the field).
2. Series machinery: the Ricci tensor computed FROM THE SERIES (Christoffels by series arithmetic) vanishes to the
   truncation order at the jet point, for p1 and p2, on both draws. Sabotage: the exponent of E_P mismatched by a
   factor (1 + 1/50) in f only must give a nonzero Ricci series. This tests sqrt, exp and the T-specialisation
   together, since Ricci-flatness is a formal identity in the differential field and so holds under any specialisation.
3. Kerr limit through the SAME code path (β = 0): ranks 1–4 bounds 2, 5, 8, 14 = the true counts, Carter included.
   This is the raise direction: the pipeline can report more than trivial.
4. Kerr limit with the non-separable sabotage g^xx·(1 + x·y/7): Carter disappears, rank-2 bound 4. The lower direction.

## Points
- P1 = (x, y) = (17/10, 3/5), R0 = 3/2.
- P2 = (19/9, −1/3), R0 = 17/9.

Both lie in the physical domain x > 1, |y| < 1, off the equator and the axis. Any denominator vanishing there makes
the code refuse.

## Predictions (sealed by this commit)
| target | ranks | predicted bound | confidence |
|---|---|---|---|
| MN p1 | 1–8 (to 10 if cheap) | = trivial (2, 4, 6, 9, 12, 16, 20, 25, 30, 36) | ~88% |
| MN p2 | 1–8 (to 10 if cheap) | = trivial | ~88% |
| the pointed one: MN rank 4 | 4 | = trivial (9), i.e. NO 4th-order KT, against Brink's suggestion for MN | ~85% |

## Protocol
- M = d. A bound above trivial is NOT a positive. Rerun at M = d+1 and d+2, at the second point, with both draws.
  Only a survivor goes to the Bridge for independent reproduction, with no claim before that.
- Resources: at most 2 worker threads (the box is shared overnight); BLAS and rank-engine threads pinned.
- Scope of a null: "no Killing tensor of valence d invariant under ∂t, ∂φ beyond the trivial ones, locally near the
  point, with smooth coefficients of any form". Non-invariant tensors are NOT covered. No global or analytic-continuation
  claim. It does not speak to non-polynomial integrals (that is Quantum's Morales–Ramis).
