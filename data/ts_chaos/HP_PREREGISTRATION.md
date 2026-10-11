# High-precision probe: genuine fractal or finite-time artefact? Pre-registration, 2026-10-11, BEFORE any probe run

Ask: the user ("yes let ansatz build the high precision probe"), via the Bridge. This is an independent leg to V12 E1,
which was NOT EVALUABLE in double precision because 17–22% of the TS window changes outcome between rtol 1e−11 and
1e−13. This probe uses its own x0 selection, code and arithmetic, and none of the Bridge's x0 lists.

## The question, made precise
For fixed horizon N, the outcome map x0 ↦ {survive N crossings, plunge, escape} is piecewise smooth. So below some
scale ε_c(N), the uncertain fraction must fall like f ∝ ε (slope s = 1), even for a chaotic system.
- **Genuine fractal (chaotic transient):** ε_c(N) shrinks roughly exponentially with N, ε_c ~ W·e^{−λ t_N}, and in
  the N → ∞ limit the boundary is fractal.
- **Finite-time artefact:** ε_c(N) does not move with N.
- **Decision statistic:** ε_c(600) < ε_c(300) supports a genuine fractal. ε_c(600) ≈ ε_c(300) (within one ε step)
  supports an artefact.

## Arithmetic and integrator (`scripts/_hp_dd.py`)
- **RHS:** generated from the SAME exact rational inverse metric as `_ts_chaos.py` (sympy → CSE), emitted as
  double-double (DD, ~32 significant digits; Dekker/Knuth error-free transformations, no FMA), compiled with numba.
  E, L and x0 enter as exact DD values: E = 97/100 exactly, and x0 is its double value.
- **Integrator:** Gragg–Bulirsch–Stoer (modified midpoint, step sequence 2, 4, …, 2k, Aitken–Neville extrapolation),
  fixed order k = 12, with adaptive step control on the difference of the last two extrapolants (mixed abs/rel norm).
- **Events, checked at step ends** with h ≤ h_max = min(20, 0.1 × the last inter-crossing proper time), so no step
  can contain two crossings:
  - a crossing is y: − → + with p_y > 0;
  - plunge is x < x_pl (1.5, the α definition);
  - escape is x > 2000 or |y| > 0.999999;
  - proper time is capped at 5e6.
- **Outcome at horizon N:** SURVIVE (≥ N crossings), PLUNGE or ESCAPE. One 600-crossing integration gives both the
  N = 300 and the N = 600 outcome.
- **Precision ladder:**

  | rung | arithmetic | tolerance |
  |---|---|---|
  | R0 | double DP5(4), existing engine | 1e−11 / 1e−12 / 1e−13 |
  | R1 | DD GBS | 1e−22 |
  | R2 | DD GBS | 1e−28 |
  | R3 (spot check only) | mpmath GBS at 50 digits | 1e−40 |

  - An x0's outcome is CONVERGED if (outcome, crossing count) agree at R1 and R2 for the horizon in question.
    Otherwise it is "unresolved at DD".

## Gates (all must pass before any probe number is read)
- **G1, Kerr Carter:** in the Weyl chart Ω(W + 1) = A(x) + B(y) separates for Kerr, with Ω = (x² − 1)/g^xx. So
  Q = (1 − y²)p_y² + G(x*, y) − G(x*, 0), with G = (x² − 1)(W + 1)/g^xx, is conserved. On 5 Kerr L1 x0 at R2, the
  maximum relative drift of Q over 300 crossings must be ≤ 1e−24.
- **G2, mass shell:** max |2H + 1| ≤ 1e−24 at R2 on the same orbits, and on 5 TS orbits.
- **G3, agreement with the double engine:** on 20 tolerance-STABLE TS x0 and all Kerr x0, the R1 outcome at
  N = 300 equals the DP5 outcome in ≥ 90% of TS cases and 100% of Kerr cases. Disagreements are reported, not dropped.
- **G4, ladder sanity:** the R3 (mpmath 50-digit) outcome equals the converged R1 = R2 outcome on 3 Kerr and 3 TS
  orbits (subject to cost, see below).

## Samples (seeded, my own)
- **Pool:** 200 x0 uniform in the α L1 TS window [9.912067, 9.945202] (seed 2026101101), and 25 x0 uniform in the α L1
  Kerr window [4.990213, 4.996584] (seed 2026101102), at E = 0.97, L = +5.125 / +2.550268.
- **Classification at R0:** DP5 at tol 1e−11, 1e−12 and 1e−13, maxsteps 3e7, N = 300. SENSITIVE if (outcome, n)
  differs across the three; STABLE otherwise. The first 50 SENSITIVE and the first 50 STABLE in seeded order form the
  probe set, with all 25 Kerr.
- **(1) Converged outcomes:** R1 and R2 on all 125 probe x0 (N = 600, so N = 300 comes free).
- **(2) Crossover test:** ε ∈ {1e−8, 1e−11, 1e−14, 1e−17, 1e−20}. Each probe x0 whose base outcome converged at BOTH
  horizons is integrated at x0 ± ε at R1 and R2. A neighbour counts only if converged. An x0 is UNCERTAIN at ε if a
  converged neighbour's outcome differs from the converged base, and is excluded at that ε if either neighbour is
  unresolved.
  - **Sizing rule (fixed now):** K_cross = the number of x0 that fits 12 h on 2 workers at the measured mean R1 + R2
    cost per 600-crossing orbit (10 orbits per x0 per rung), capped at 40, taken in seeded order from the converged
    set with SENSITIVE and STABLE alternating. If K_cross < 12, report INSUFFICIENT BUDGET instead of a verdict.
    Kerr: 10 converged Kerr x0 get the same neighbours.
- **ε_c(N)** = the largest ε in the set at which the pairwise slope between consecutive ε first exceeds 0.5, i.e.
  where f starts to fall toward s = 1. If f never falls (slope ≤ 0.5 throughout), ε_c(N) < 1e−20 ("below reach").
- **Kerr control on (2):** 0 uncertain x0 at every ε. An isolated smooth boundary point gives expected hits ~
  2ε/W·K ≪ 1. Any Kerr uncertain point voids (2).

## Predictions (sealed by this commit)
| item | prediction | confidence |
|---|---|---|
| G1–G3 pass | yes | ~80% (it is a new integrator) |
| (1) STABLE TS x0 converged at R1 = R2, N = 300 | ≥ 90% | ~85% |
| (1) SENSITIVE TS x0 converged at R1 = R2, N = 300 | ≥ 50% | ~60% |
| (1) Kerr converged at both N | 100% | ~95% |
| (2) TS ε_c(300) inside reach (≥ 1e−20) | yes | ~50% |
| (2) TS ε_c(600) < ε_c(300), or (600) below reach while (300) is inside | supports a genuine fractal | ~70% conditional on (300) inside reach |
| (2) Kerr uncertain at any ε | none | ~97% |

If ε_c(300) is also below reach, the verdict is "flat to 1e−20 at both horizons, not decidable at DD": an honest
null. The next rung would then be quad-double or arbitrary precision.

## Reading rules
- A gate failure stops the probe and is reported; it is fixed only under an addendum.
- Converged fractions are reported with the unresolved counts, never dropped.
- Resources: ≤ 2 worker processes, thread env vars = 1, load gate (5-min load < 8, free + inactive ≥ 3 GB),
  checkpointed per orbit. The environment is recorded under the reproducibility policy.

## Addendum 1 (2026-10-11, the Bridge's review, before ANY probe run)
1. **Tolerance headroom.** A neighbour outcome counts only if R1 (1e−22) and R2 (1e−28) agree, so integration error
   at R1 cannot masquerade as ε-sensitivity: it shows up as "unresolved". In addition, an ε rung enters the ε_c
   determination only if ≥ 80% of its neighbour outcomes converged; otherwise that rung is "below DD resolution" and
   ε_c is stated as an inequality.
2. **Unresolved outcomes.**
   - Base x0 whose outcome does not converge between R1 and R2 are excluded from the crossover set, and their count is
     reported as U(N), the fraction of the probe set whose outcome is decided below ~1e−28. A large U(N) is itself the
     answer that "ε_c lies below DD resolution".
   - For f(ε), PRIMARY: x0 with an unresolved neighbour are excluded at that ε (counts reported). SECONDARY BOUND:
     unresolved neighbours counted as uncertain (an upper bound on f).
   - The verdict uses PRIMARY. If PRIMARY and the SECONDARY BOUND give different ε_c, that is reported as
     "not robust".
3. **Conventions matched to the double engine** (for G3): a crossing is counted when y goes from < 0 to ≥ 0 with p_y > 0
   at an accepted step, so the start (y = 0) is not counted. Plunge and escape are checked at accepted step ends.

## Addendum 2 (2026-10-11, G4 redefined because of MEASURED cost; before any G4 or probe run)
Measured: the mpmath 50-digit GBS (R3) takes 609 s for 20 Kerr crossings (~30 s per crossing; TS ~5× more). G4 as
written (3 Kerr at N = 300, 3 TS at N = 100) would cost ~20 CPU-hours. It would also be weak, since outcomes over a few
crossings agree trivially. **G4 is replaced by a state-agreement check:**
- integrate to a FIXED proper time T, with the last step clipped to land exactly on T, in DD at R2 (tol 1e−28) and in
  mpmath at 50 digits (tol 1e−40). Compare the full state (x, y, p_x, p_y);
- 2 Kerr probe x0 at T = 2400 (~20 crossings), and 2 TS x0 (the first STABLE and the first SENSITIVE) at T = 4000
  (~10 crossings);
- **pass:** max relative state difference ≤ 1e−20 for Kerr and the STABLE TS. The SENSITIVE TS value is reported as
  the measured DD-vs-50-digit divergence at T, informative, not pass/fail.

G4 does not gate `base` (G1–G3 do, as before). It runs on one core after `base`, or alongside it if the load allows.
The functions used are separate from the probe's `run()` (new `run_to_time` / `state_at`), so the probe code path is
unchanged.
