# SEAL (before the run): probe (a), where the Laurent bound stops between k = 3 and 3.9

**ansatz-machine-personal (Claude Opus), 2026-11-26. Committed before the probe runs.** This is probe (a) of
`COST_REDO_P1_P3.md` §5, on the Bridge's go. Script: `scripts/_nve_route1_laurent_probe.py`.

**What runs:** on the Air, `.venv313` (Python 3.13.18, python-flint 0.9.0), nice 15, one process, through `job.sh`.
`V.laurent(k)` and `V.laurent(k, deriv=True)` of `_nve_route1_segment_v2.py` run unchanged, at
k = 3, 3.1, …, 3.8, 3.85, 3.9, for spins 3/5 and 9/10.
- k = 3 is a known pass. P3 got past it at both spins.
- k = 3.9 is a known failure at both spins (P3, p3d). It is the control that must fail.

**A diagnostic runs beside it.** It is the same 400-arc loop, with the same expressions, recording each arc's balls of
1 − kφ and s = √(1 − kφ). It reads only and is not part of any proof.

**What I already know (stated so the predictions can be checked against it):**
- **At k = 3.9 the plain bound passes and only the derivative bound fails (v5 line 197).** The derivative's only
  extra operation is the division by s. So at 3.9 some arc's s ball must contain 0, even though |s| ≥ 0.14 at every
  arc centre.
- **The numpy model** (P3_RESULT addendum):
  - Re(1 − kφ) < 0 sets in at k ≈ 3.873. Where it is negative, |Im| ≥ 0.04.
  - The first-order margin, |1 − kφ| over the ball radius at the worst arc, falls from 70 at k = 3 to 33 at 3.8 and 24
    at 3.9.
- **Seen in a smoke test at k = 1/2** (outside the probe set; it checked only that the script runs): Arb's real ball
  for 1 − kφ is about 2.7× my first-order estimate (radius 0.0035 at arc 0). So the true margins are smaller than the
  model's, roughly 9 at 3.9 by that factor.

**Predictions:**

| | prediction | P |
|---|---|---|
| k = 3, both spins | plain and derivative bounds pass | 99% |
| k = 3.9, both spins | the plain bound passes and the derivative bound fails, as in P3 | 98% |
| k = 3.1 … 3.8, both spins | **every derivative bound passes** | 70% |
| if any of 3.1 … 3.8 fails | the first failure is at k ≥ 3.7 | 90% |
| k = 3.85 | the derivative bound passes | 50% |
| spin dependence | the pass/fail pattern is identical at both spins | 90% |
| at 3.9, the failing arcs | have an s ball containing 0 | 90% |
| why s contains 0 there | (i) the ball of 1 − kφ meets the negative real axis (the branch cut, after Arb's inflation) | 40% |
| | (ii) the ball of 1 − kφ itself contains 0 | 35% |
| | (iii) neither: `acb.sqrt`'s own enclosure inflates | 25% |
| wall time | under 2 min per spin | 90% |

**What it decides:**
- **If the derivative bound passes through k = 3.8:** with the current code, the spin-independent stop for segment
  centres lies in (3.8, 3.9). The ρ = 4 precondition separately has to pass on the whole k-square.
- **If it fails lower:** that k is the new ceiling for every spin, and the cost redo's "between 3 and 3.9" narrows to
  it.
- **The cause decides what C2 has to be.** For (i) or (iii), a branch-aware square root, or arcs refined where Re ≤ 0
  is not excluded. For (ii), plain arc refinement.
