# RESULT: loop closure for a finite-loop c0 (CLOSES), and the 9/10 stop-(c) scan (no singularity found)

**Office ansatz-machine (Claude Opus), 2026-11-28.** The seal is `CLOSURE_STOPC_SEAL.md`, committed before either
float part ran, with both scripts (97c0221).
- **Where it ran:** the Mac mini, seven processes at nice 15, launched 2026-11-27 22:08:19. PIDs are in
  `closure_stopc/pids.txt`. All exited normally.
- **Outputs:** `closure_stopc/*.out`.
- **Environment, corrected:** the seal said Python 3.14.10. The interpreter actually used
  (`conjecture_machine/.venv/bin/python`) is **Python 3.14.5**, with mpmath 1.3.0, sympy 1.14.0 and numpy 2.4.6.
- **The Air was not touched.**

## 1. Loop closure: answer CLOSES

**Mathematics (seal §1).**
- A loop in a simply connected region free of c0's singularities closes automatically. That covers region B's disc
  loops.
- A loop enclosing ALL of c0's finite singularities closes, since the residues at ∞ are zero. That covers the region-A
  circle, while every branch point is inside it.

**Float check** (50 digits; the periodic trapezoid rule at 8000 and 16000 points, agreeing to about 1e−49; 74 s per
spin). The formula for c0'' matched the code's radicand to about 1e−50 at every k.

| k | 3/10: circle / B | 3/5: circle / B | 4/5: circle / B | 9/10: circle / B |
|---|---|---|---|---|
| 3, 3.5, 3.9, 4 − 1e−6, 4.02 | closes / closes | closes / closes | closes / closes | closes / closes |
| 4.1 | closes / closes | closes / closes | **does not** / closes | **does not** / closes |
| 4.2 | closes / closes | **does not** / closes | **does not** / closes | **does not** / closes |
| 4.25, 4.28 | **does not** / closes | **does not** / closes | **does not** / closes | **does not** / closes |
| 30/7 − 1e−6 | unresolved / closes | unresolved / closes | unresolved / closes | unresolved / closes |

- "Closes" means the sheet returns (+1) and |Δc0'|, |Δc0| are about 1e−50.
- "Does not" means the sheet returns, but |Δc0'| is 0.1–1.0 just past k_cross and falls to 2.6e−4 to 2.3e−3 at 4.28.
- **The circle closes exactly where all four branch points lie inside it**, and fails exactly where the outer one has
  left: the script's "all branch points inside" flag matches the verdict in every row. That agrees with k_cross =
  4.23, 4.16, 4.09 and 4.05 from the algebra.
- At 30/7 − 1e−6 the circle's period is 7.6e−12 to 6.9e−11. That lies between my registered thresholds (1e−30 and
  1e−10, scaled), so it is **UNRESOLVED by the criterion**. It is nonzero, and it shrinks as the outer pair escapes,
  so the circle is not a valid loop there. This is a threshold-design miss on my part, not a mathematical one.

**Against the seal (§2):**

| prediction | P | outcome |
|---|---|---|
| the circle closes at every tested k ≤ k_cross | 95% | **HIT** |
| the circle does NOT close at every tested k > k_cross | 90% | HIT at every such k except 30/7 − 1e−6 (unresolved): **partial MISS** |
| the region-B test circle closes at every tested k | 97% | **HIT** (40 of 40) |
| for k < 4, R_c (and the test circle) is smaller; it still closes | 90% | **HIT** |
| overall answer "closes" | 90% | **HIT** |
| wall time under 10 min | 85% | 74 s: **HIT** |

**Neon's claims, settled here:**
- **Claim 1** (for k ∈ [4, 30/7) every c0 singularity lies on Re z = 0, so half-plane loops close automatically):
  **CONFIRMED**, with two corrections.
  - The circle stays valid up to k_cross (4.05–4.23), not only to about 3.85–3.95.
  - For k < 4, two branch points lie in Re z > 0. There only loops inside region B's guarded disc are automatic, not
    the whole half-plane.
- **Claim 3** (c0 drops out by Ernst's shift invariance, so only c0' needs closing): **REFUTED for our equation.**
  - The lower-axis coefficient is f0⁻ = f0/(f0² + c0²), from e₋ = 1/e₊ (`MRS_SECTION.md` §5a). It depends on c0
    itself; `MRS_SECTION.md` also says q is holomorphic in (c0, c0′).
  - The shift freedom is used up by the normalisation c0(∞) = 0 that e₋ = 1/e₊ requires. The lower-axis twist c0⁻,
    which would be shift-free, does not enter the equation.
  - So both c0' and c0 must close, which is what was tested.

**For v7:** use the circle up to an A/B switch at k ≤ 4.0, where every spin has margin to its k_cross, and region B's
disc loops above it. No closed words are needed, and there is no extra cost.

## 2. The stop-(c) scan at spin 9/10: no singularity found

**The run:** region A's own machinery at 9/10, with the circle R0 = 1.2639 and the capsule lasso built at k_c. For each
k_c ∈ {2, 2.5, 3}, a 9 × 9 grid over the route-(i) square [k_c ± 0.10625] × [±0.10625]i. Each grid point tracked the
four outer points, located all zeros of G1 and G2 in max(1.05, ρ_c + 0.12) < |z| < 2.5, and counted them by winding.

| k_c | max \|w_root\| (limit 1.2346) | max ρ_c | nearest point to the circle | nearest point to the lasso | (G1, G2) zeros in the annulus |
|---|---|---|---|---|---|
| 2 | 0.432 | 0.9 | 0.439 (r+) | 0.132 (p+, the point the lasso encloses) | (1, 2) at every grid point |
| 2.5 | 0.480 | 0.9 | 0.395 (r+) | 0.128 (p+, enclosed) | (1, 2) at every grid point |
| 3 | 0.562 | 0.9 | 0.346 (r+) | 0.123 (p+, enclosed) | (1, 2) at every grid point |

**What it shows:**
- No singular point of the ρ-equation comes anywhere near the circle (≥ 0.35).
- No point other than the lasso's own enclosed p+ comes within 0.123 of the lasso. p+ sits at about the capsule
  radius δ = 0.15 by construction, and moves by only about 0.01 from k_c = 2 to 3.
- There are no extra zeros: the annulus holds exactly r+ (G1) and p± (G2) everywhere.
- The c0 branch points stay far inside the Laurent limit (|w| ≤ 0.56 against 1.23).
- **So the 22,000× growth of the walk-side dq bounds between k_c = 2 and 3 is NOT caused by a singular point
  approaching a loop, nor by a c0 branch point.** Its cause is open.
- Remaining candidates, none of them tested:
  - growth of the solution's own size along the lasso as k grows (a Dyson-type exponential);
  - the outer-box Cauchy remainder in z × k.

The cheapest discriminator: one v6 prove-only stage at 9/10 with k_c = 2.5, at half-width 1/20 and at 1/40, printing
the dq-bound attribution. That is about 1 h each on one core. Not run, and it needs a machine allocation.

**Against the seal (§3):**

| prediction | P | outcome |
|---|---|---|
| at k_c = 2, nothing within 0.15 of either loop | 80% | **MISS by the registered rule**: the lasso's own enclosed p+ sits at 0.132. The rule should have excluded the enclosed points; every other point is ≥ 0.35 away |
| at k_c = 3, "singularity found" | 55% | **not found** (the 45% branch) |
| if found, a zero of G1 or G2 | 75% | n/a |
| max \|w_root\| < 1/0.81 on all three squares | 90% | **HIT** (≤ 0.56) |
| zero counts constant over each square | 80% | **HIT** ((1, 2) everywhere) |
| wall time under 30 min (parallel) | 75% | **MISS**: 10.5 h. Each grid point took about 7.6 min (six Laurent rebuilds at about 300 terms and 50 digits, about 480 Newton starts, four windings). I underestimated about ×20 |

**For the v7 plan:** 9/10's [2, 3] is not blocked by geometry. The question is a cost or enclosure one, to be settled
by the discriminator above. It can be folded into v7's stages, or run on its own (about 2 core-h) if Sumit wants 9/10
extended to 3 before v7.
