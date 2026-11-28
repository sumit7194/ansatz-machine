# SEAL: the stop-(c) discriminator at spin 9/10 (Mac mini; a diagnostic, not a certificate)

**Office ansatz-machine (Claude Opus), 2026-11-28.** The Bridge's go, under Sumit's go for the stop-(c) work:
- 2 cores, nice 10, under 0.2 GB per core, about 1 h, with pause-only guards (no kill caps);
- if it runs past 2 h, tell the Bridge and do not stop it.

This seal, its runner `air/stopc_discrim.sh` and the reading below are committed before launch.

## Why
- **The cost:** P3 found 9/10's ρ = 4 row at k_c = 3 (half-width 1/20) out of reach. The circle-side dq bounds over the
  complex k-square grew about 22,000× from k_c = 2, while at the centre point they did not grow.
- **What the scan ruled out** (`CLOSURE_STOPC_RESULT.md` §2): a singular point or a c0 branch point approaching
  either loop.
- **So the open question is whether a SMALLER k-box removes the growth.** If it does, the registered split rule covers
  9/10's [2, 3] inside v6.

## What runs (on the Mac mini, from this worktree)
1. **Floats** at k_c = 5/2: `.venv` (Python 3.14.5), `_nve_route1_floats.py 5/2`, into
   `R1_FLOATS=route1_floats_stopc_9_10.json`.
2. **Two v6 PROVE stages, in parallel, no verdict**, with the production driver's settings (ρ = 4 only, mode F, tol
   rel), at NVE_SPIN = 9/10, R1_R0 = 1.2639, R1_KC = 5/2:
   - **A:** R1_HALF = 1/20 (k-square half-side R = 0.10625, the production width);
   - **B:** R1_HALF = 1/40 (R = 0.053125, one split).
3. **Interpreter:** `.venv313` in this worktree. That is Homebrew Python 3.13.12 with python-flint 0.9.0, mpmath
   1.3.0, sympy 1.14.0 and numpy 2.4.6, created for this run. It is not the Air's 3.13.18, which is fine for a
   diagnostic. Nice 10, under `air/job.sh`'s pause-only logic, adapted to run here as `stopc_job.sh`.

**What is read from each:** whether a row is admitted, and if so n and M_F; otherwise the rejection reason. Then the
attribution: I0 (circle), I1 (lasso), c0/k and c1/k, and ratio_max, from the rows file, which records them even for a
rejected row. The baseline is P3's row at k_c = 2, half 1/20: n = 22, I0 = 1.164, I1 = 6.459, M_F = 2.66e9.

## The reading (registered here)

| A (1/20) | B (1/40) | what it means for 9/10's [2, 3] |
|---|---|---|
| row, n ≤ 40 | (either) | 0.1-wide segments work at least to 2.5. The stop lies in (2.5, 3]. A follow-up at k_c = 2.75 would locate it; [2, 2.5] is coverable inside v6 at production width |
| rejected | row, n ≤ 40 | **the split rule recovers it.** [2, 3] is coverable inside v6 with half-width segments, at about 2× the cost per unit k |
| rejected | rejected | one split does not suffice at 2.5. Depth 2 (1/80) is untested; otherwise [2, 3] goes to v7 |

**Attribution (independent of the table):**
- If I0 drops by much more than the 2× expected from R alone when R halves (B against A), the circle's growth is
  sensitivity to complex k at the edge of the box, which a smaller box cures.
- If I0 at A is close to P3's k_c = 2 value, the growth sets in between 2.5 and 3.

## Predictions

| | P |
|---|---|
| A admits a row with n ≤ 40 | 55% |
| B admits a row with n ≤ 40 | 80% |
| if both admit, n(B) < n(A) | 85% |
| I0(A) / I0(P3, k_c = 2) in [1, 3] (growth mostly beyond 2.5) | 60% |
| I0(B) < I0(A) / 2 (more than the R scaling) | 50% |
| F1 never fires; both exit rc 0 | 95% |
| wall time per prove 30–70 min (floats about 5 min first) | 70% |
| peak footprint under 150 MB per process | 95% |
