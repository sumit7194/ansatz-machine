# v7 stage V1: result. PASS at spin 3/5. At 9/10, (b) is UNINFORMATIVE, so V1 is not a PASS there; a ruling is needed

**Office ansatz-machine (Claude Opus), 2026-11-28.** The registration is `V7_REGISTRATION.md` (1f36852), with
addendum 1 (2176609: radius bars) and addendum 2 (5327dc8: the engine tolerance). All three were committed before the
registered tests ran. The V1 code was committed at 414c588 before its run, and later edits are listed below.

**Environment:**
- Arb side: `.venv313`, Python 3.13.12, python-flint 0.9.0, FLINT 3.6.0;
- engine side: `.venv`, Python 3.14.5, mpmath 1.3.0;
- Mac mini, nice 10, one core.
- Each run took a few seconds (engine 44–62 s).

Outputs are in `v7/`: `v1_arb_*.out/.json` and `v1_engine_*.out/.json`.

## Verdicts

| criterion | spin 3/5 | spin 9/10 |
|---|---|---|
| (a) exact controls, k = 0 and 4, circle and real axis: exact values inside the v7 balls, radius ≤ 1e−40, engine within 1e−40 | **PASS** (worst radius 1.7e−46) | **PASS** (worst radius 9.5e−46) |
| (b) v7 against the production Laurent c0, 10 values of k in [1, 3.7] × 2 circle points | **PASS**: 20/20 overlap; v7 radius ≤ 5e−47, Laurent radius ≤ 1e−54; \|v7 − Laurent\| ≤ 7e−47; engine 20/20 | **UNINFORMATIVE**: 20/20 overlap, engine 20/20, but the **Laurent** radius is 3e−16 to 8e−16, above the 1e−30 bar (v7 radius ≤ 3e−46) |
| (c) one circuit of \|z\| = R0 at k = 3 and 3.9: returned radius ≤ 1e−30 and the start contained | **PASS** (radius 4.8e−47, 1.8e−47) | **PASS** (radius 1.4e−46, 4.1e−47) |
| (d) must-fail controls (i)–(iv) fire | **PASS** (all four) | **PASS** (all four) |
| **V1** | **PASS** | **NOT PASS** (by the letter of (b)) |

**Grading of the development-run changes (the Bridge's ruling; part of the verdict, not only the change list).**
These changes were made after seeing development-run behaviour, before any registered verdict:
- **Must-fail control (ii):** "must-fail plant corrected after it first failed to fire (it flipped the prediction,
  not the branch)".
- **The Cauchy bound:** "the adaptive cover replaced the single-ball bound after a false flag near B's double zero".

V2's non-author read must cover both diffs.

## Why (b) is uninformative at 9/10
- The production Laurent evaluator at 9/10 encloses c0 only to about 1e−15. That is its own truncation (NW terms),
  with the circle at about 0.79 of the Laurent radius.
- The enclosure is valid, and it is what the 9/10 certificates used, so this is a fact about that evaluator, not a
  defect. But it means a 1e−30 comparison cannot be made against it at 9/10.
- The v7 balls agree with it to within its width at all 20 points. Separately, the independent 50-digit engine
  agrees with v7 to within 1e−40 at all 20 points.

**Options for the ruling:**
1. Accept (b) at 9/10 on the engine comparison: an independent implementation, 1e−40, 20/20.
2. Re-run (b) at 9/10 with the Laurent evaluator at a larger NW. Same formula, more terms, so its balls fall below
   1e−30. This needs an addendum, because it changes the comparison instrument's parameter.
3. Treat V1 as passed at 3/5 only, and continue V2 at 3/5 (the pilots are all at 3/5).

## Changes to the V1 code after 414c588, made before any registered verdict was taken; each is a fix, not a criterion change
1. **The Cauchy bound** `sup_box`. A single ball, then an 8 × 8 cover, flagged a "singular point" that was ball
   overestimation of the quartic B near its double zero (k = 0, z = a/√3).
   - Fixed by a mean-value form for B on a box, and an adaptive cover (a failing sub-box is split in four, up to five
     levels, before refusing).
   - Still rigorous: a true zero stays inside some sub-box at every level and is refused.
2. **Must-fail control (ii).** Its first plant negated the series PREDICTION, which the code then correctly followed,
   so it was self-consistent and could not fire. It now negates the CHOSEN branch value at the step end, which is
   the failure the control is meant to catch. It fires at both spins.
3. **A harness parsing bug.** The engine's complex numbers are now stored as separate real and imaginary strings.

## Rerun of V1(b) at 9/10 under addendum 3 (efb0768): PASS, so V1 PASSES at 9/10 too
- **The rerun:** the production Laurent evaluator (the same formula) at N = 386 terms, the count fixed in advance.
  Engine JSON reused. Output `v7/v1b_rerun_9_10.out` and `.json`.
- **20 of 20 points:**
  - Laurent radius 3.4e−36 to 9.1e−36 and v7 radius at most 2.8e−46, both under the 1e−30 bar;
  - the balls overlap, with |v7 − Laurent| ≤ 1.3e−35, i.e. within the Laurent width;
  - the engine agrees with v7 within 1e−40 at all 20.
- **V1(b) at 9/10: PASS.** With (a), (c) and (d) already passed, **V1 PASSES at spin 9/10.**
- At production's NW = 190, the 9/10 Laurent c0 is enclosed only to about 1e−15. The v7 evaluator (s = 1/t start plus
  Taylor propagation) gives about 1e−46 at the same points.
- **Order of events, from file metadata and git:**
  - addendum 3 was committed at 15:16:02 (efb0768);
  - the rerun's output file `v7/v1b_rerun_9_10.out` was created, by the shell redirect at process start, at
    **15:16:07**, and last written at 15:16:09; its JSON was written at 15:16:09;
  - the result was committed at 15:16:17 (e4543e9).
- So the whole 20-point comparison ran after the addendum. Only the N-selection bound computation (per-k Cauchy bounds
  M; no comparison values) ran before it, as the addendum states.
