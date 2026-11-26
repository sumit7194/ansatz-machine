# v4 (k-Taylor) and the 2026-11-26 power cut: what was lost, what is NOT a result

**What happened.** The worktree for this branch lived in the session scratchpad under /private/tmp. macOS clears
/private/tmp at boot, so the power cut at about 06:52 and the restart at 08:45 deleted the following:
- the uncommitted v4 code;
- every v4 output;
- the running spin-9/10 job.

The seal (5bcca66) survived because it had been pushed. The code was restored verbatim from the session transcript
(`scripts/_nve_route1_segment_v4.py`, `scripts/_nve_route1_eqn_verdict.py`). The worktree now lives at
/Users/sumit/Github/conjecture_machine-ktaylor.

**Seen in the session before the cut. These are NOT results.** The artefacts are lost, and these lines will be
regenerated and compared against the regenerated output:
- **Spin 3/5, v4 prove (692 s, 37 MB):**
  - point constants identical to v3 (4.153E-1 / 9.325E+0);
  - ρ = 3: 0.839 / 13.98 per unit k, n = 16;
  - ρ = 4: 1.039 / 15.84, n = 14, M_F ≤ 2.438E+4, M_trM0 ≤ 2.258, M_trM1 ≤ 38.73;
  - ρ = 5: n = 12;
  - ρ = 6.5: n = 12 (chosen);
  - crude bound kept on ≤ 8 steps.
- **Equal-n controls (v2's 25 nodes, n = 24, ρ = 4), both CERTIFIED:**
  - v4: |F| ≥ 0.265334372, |tr M0| ≥ 1.993158418, |Im tr M1| ≥ 2.648820919;
  - v3: |F| ≥ 0.265334299, with the other two the same;
  - the node copies were byte-identical to v2's file.
- **Spin 9/10 v4 prove:** running at the cut. No row line had been read.

**Lesson (now a rule).** Never keep a working tree or uncommitted work in /private/tmp: it is cleared at boot. Put
worktrees beside the repo and commit the code before launching any job.
