# SEAL (before any run): pilot P2, the proof stage at k_c = 21/20 for spins 3/10 and 4/5

**ansatz-machine-personal (Claude Opus), 2026-11-26. Written and committed before anything of P2 is computed,
including its floats inputs.** Registration v1 §5, P2. Nothing at spins 3/10 or 4/5 has been run with v2, v4 or v5.

**What runs (on the Air, `.venv313`, Python 3.13.18, one process, nice 15, pause-only guard):**
1. Inputs: `_nve_route1_floats.py 21/20` with the 50-digit engine, giving the singular points and the k = 21/20 lasso,
   at `NVE_SPIN=3/10 R1_R0=1.1492` (→ `route1_floats_3_10.json`) and `NVE_SPIN=4/5 R1_R0=1.3382` (→ `route1_floats_4_5.json`).
2. The proof stage of **v5 at 7f96efc** (`_nve_route1_segment_v5.py prove`), rows ρ ∈ {3, 4, 5, 6.5}, segment
   [1, 1.1], at each spin. **Deviation from the registration's wording ("v4 proof stage"):** v5 is v4 plus checks and
   code-hashed checkpoints, and T1 compares their rows for equality on this machine and Python before P2 starts. If T1
   fails, P2 does not run on v5.

**The basis for the numbers.** The measured v4 rows at ρ = 4 (constants per unit k: circle c0, lasso c1) are 1.04 and
15.8 at spin 3/5, and 7.89 and 40.3 at spin 9/10. The certified k = 0 loop constants (`EPS_EFFECTIVE.md` §4) are lasso
c_L = 40, 81, 176, 383 and circle C_E = 8.1, 11.2, 15.2, 24.5 for spins 3/10, 3/5, 4/5, 9/10. I scale c1 as c_L^0.6
(the exponent that maps 3/5 to 9/10), and take the gauge factor as ~600 at both measured spins. Then I recompute n with
v4's rule. The circle constant c0 has no clean scaling (it is set by the circle's distance to the Laurent radius), so
its ranges are wide.

**Predictions:**

| quantity | spin 3/10 | spin 4/5 |
|---|---|---|
| floats inputs: geometry_ok | True (P = 95%) | True (P = 95%) |
| all four rows admissible (precondition and holomorphy certified) | P = 85% | P = 85% |
| c1 per unit k at ρ = 4 (lasso) | 7 to 15 (point estimate 10) | 18 to 35 (point estimate 25) |
| c0 per unit k at ρ = 4 (circle) | 0.2 to 2 | 1 to 6 |
| chosen n | 8 to 12 (point estimate 10) | 12 to 18 (point estimate 14) |
| chosen ρ | 5 or 6.5 | 4, 5 or 6.5 |
| circle reference walk steps | 1,000 to 3,000 | 3,000 to 10,000 |
| proof stage wall time on the Air | 8 to 25 min | 15 to 60 min |
| F1 gate never fires (no AssertionError) | P = 97% | P = 97% |

**Ordering I expect, with more confidence than any single number (P = 85%):** n(3/10) ≤ n(3/5) = 12 ≤ n(4/5) ≤
n(9/10) = 18, and c1(3/10) < c1(3/5) < c1(4/5) < c1(9/10) at every ρ.

**What would surprise me:** a rejected row at either spin at k ≈ 1 (the Laurent precondition has only been seen to fail
near k = 4), or a 3/10 circle constant larger than 3/5's. Neither invalidates anything; P2 measures cost, it certifies
nothing.

## Amendment, committed before any P2 computation (2026-11-26, after T1 on 7f96efc)

T1 on 7f96efc **failed**. Every bound and gauge in the v5 rows equals v4's; the difference is one diagnostic field,
`stats`. v5 had dropped v4's K-point z-direction control, and v4's cumulative counters include that pass. The proof
JSON also lacked `norder` and `point_constants`. By the condition above, **P2 does not run on v5.** It runs on **v4
(c2dd39c's `_nve_route1_segment_v4.py`, unchanged), as the registration words it.** The runner is `p2.sh` v2: the same
floats step, then v4's proof stage under `.venv313`, refusing if any v4 3/10 or 4/5 file exists. Every prediction above is unchanged,
except the F1 row, which does not apply: v4 has no F1 gate.
