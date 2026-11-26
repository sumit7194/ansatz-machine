# Tests T1–T4 of the route-(i) registration (§3(d)): record

[ansatz-machine-personal, 2026-11-26. On the MacBook Air at `~/GitHub/ansatz-air/`, `.venv313` (Homebrew Python 3.13.18,
python-flint 0.9.0, mpmath 1.3.0, sympy 1.14.0, numpy 2.5.0), nice 15, pause-only guard, one process.]

## Code reads (non-author, the Bridge)
- **7f96efc** (v5 with v4's `ratio_median`/`ratio_max` restored): read by the Bridge; the restored expression is
  character-for-character v4's (c2dd39c line 250), with r0/r1 from the same `dq_list_v4` call, and nothing else in v5
  changed. Approved; T1–T4 on 7f96efc count.
- **fa7859f** (v5.1, segment from `R1_KC`/`R1_HALF`/`R1_FLOATS`): approved, with fix B1 (fail closed when half-set).
  Full read: TheBridge `fleet/reads/ansatz_v5.1_read_2026-11-26.md`.
- **b64a43c** (B1): approved. An empty `R1_KC=""` also refuses (int("") fails).

## Run 1: tests.sh on 7f96efc (17:25:59 to 18:13:04; manifest 95b0e71, 56 files verified)

**T1: FAIL.** Outputs are in `air_tests/`.
- v4's proof stage at 3/5 on the Air (Python 3.13.18) reproduces the committed 3.13.12 v4 rows exactly, minus `sec`
  (information only; that is a cross-environment comparison).
- v5's rows equal v4's in every field (every Arb bound, M, n, the gauge floats, `ratio_*`) **except `stats`**. v5's
  counters are short by exactly one pass over the reference steps: `centred` by 2866 = 2163 + 703, split as 2757 + 109 between
  `rout2` and `rout15`, at all four ρ.
- **Cause:** v4's prove runs a z-direction control with K a point ("circle, K a point … v4 ≤ 4.153E-1") before the
  rows, and its cumulative `STATS` include that pass. v5's prove had dropped the control. A whole-proof-JSON comparison
  (added after this failure) also shows v5's proof JSON lacked `norder` and `point_constants`.
- No bound, certificate or gate is affected: the dropped items are a printed control and diagnostic counters. But T1's
  rule is that v5 may differ from v4 only by its additions, so this is a v5 bug, and T1 did its job in catching it.
- **T2–T4 did not run** (`tests.sh` stops at the failed T1).

**Fix (v5.1, after b64a43c):** v4's K-point control is restored in v5's prove with v4's code, along with `norder`
and `point_constants` in the proof JSON. T1's comparison now also covers the whole proof JSON (`T1_MJSON`): v5 may add only
`version`, `code`, `code_env`, `code_files`, plus `coverage`/`code`/`f1` per row. I checked that the extended comparison
can fail: run on the 7f96efc outputs, it reports `chosen`, `norder`, `point_constants` and `rows`.

**Consequence for P2:** its seal made running on v5 conditional on T1 passing, so P2 runs on v4 as registered (the seal's
amendment, committed before P2).

**Timeline of the P2 amendment** (the Bridge's record item; commit times from git on the Mac mini, P2's from its
logs on the Air; the clocks agree to within 0.1 s, measured by ssh round trip, offset Air − Mac mini = +0.07 s):

| time (IST) | event |
|---|---|
| 18:13:04 | tests.sh on 7f96efc exits rc 1 (T1 FAIL) |
| **18:17:15** | **4bc2ebd committed: P2 seal amendment (P2 on v4), the v5.1 fix, this record** |
| 18:17:26 | P2 starts on the Air (`guard_p2.log`: "started p2 pid 31946"; first step, the 3/10 floats, the same second) |
| 18:18:20 | 68486b9 committed: the P2 addendum manifest. Its three hashes were computed on the Mac mini and verified on the Air (`shasum -c`, all OK) in the same command that launched P2, before the launch; the commit itself came 54 s after the launch. |

So the amendment precedes every P2 computation by 11 s. The manifest's content was checked before the launch, but its
commit followed it: a slip against "commit before launch", recorded here. The next manifest (v5.1) is committed before
its run.

**The fix read:** 4bc2ebd was read and approved by the Bridge (TheBridge `fleet/reads/ansatz_v5.1_fix_4bc2ebd_read_2026-11-26.md`).
The z-control is line for line v4's apart from the `S4.` prefix, in v4's position before the rows. `norder` and
`point_constants` are v4's expressions, and the T1_MJSON allow-list is right. P2 on v4 is accepted.

**The Bridge's check of the slip:** the three hashes in 68486b9 equal the files as committed at 4bc2ebd (floats
a2c0718b…, p2.sh d415bbd9…, v4 c2675521…; I reproduced them with `git show 4bc2ebd:<file> | shasum -a 256`). So the code
P2 ran was in git 11 s before the launch, and only the hash list came 54 s late.

## T1–T4 plus B1 on v5.1 (1f3d3d7 manifest, b7e17c4): PASS

**Run:** `air/tests51.sh`, chained to start on P2's rc 0. It started 19:20:43 and ended `JOB_EXIT 0` at 20:14:34, on
the Air, `.venv313`, Python 3.13.18, python-flint 0.9.0, one process, nice 15, pause-only guard (never paused). Outputs
were copied back unchanged into `air_tests51/` (the log, the v5.1 rows, dq checkpoint, proof JSON, node file and
verdict). The v4 reference is today's T1 run on the same machine and the same Python (`route1_seg_M_v4_nseg1_T1run.json`
and the v4 rows from that run), as the amended registration requires.

**T1 (v5.1 at the default segment vs v4): PASS.** All four rows (ρ = 3, 4, 5, 6.5) are IDENTICAL after dropping only
v5's additions and `sec`, `stats` included this time. The **whole proof JSON is IDENTICAL** under the `T1_MJSON` rule,
with v5's `code`, `code_env` and `code_files` present. The restored K-point control printed 4.153E-1 (circle) and
9.325E+0 (lasso), v3's and v4's values. Coverage at every row: circle 2163 steps = 2163 bounds, 25 k-subpoints, 54075
pairs; lasso 703 = 703, 25, 17575. The F1 step checks (12304) never fired. Proof stage 1694 s, peak RSS 35 MB.

**T2–T4 and B1: 14/14 PASS.**

| test | outcome |
|---|---|
| T2 control: untampered prove resumes | rc 0, rows from checkpoint 4/4, proof JSON unchanged |
| T2a foreign record in the dq checkpoint | refused, "F2 gate", other files unchanged |
| T2b foreign record in the rows file | refused, "F2 gate", other files unchanged |
| T2c foreign code in the proof JSON | refused, "F2 gate", other files unchanged |
| T4a circle pair count + 1 | refused, "F3 gate", other files unchanged |
| T4b lasso bound count + 1 | refused, "F3 gate", other files unchanged |
| T2/T4 control: untampered v5 verdict | CERTIFIED, \|F\| ≥ 0.265039275 (P1's number), planted-zero control refused |
| T4 control: verdict rerun reads every node from disk | rc 0 |
| T2d foreign record in the node file | refused, "F2 gate", other files unchanged |
| T3a bad point (1 − kφ ≈ −2.356 − 0.467i) via `safe_step` | AssertionError "F1 gate" |
| T3b the same point via the v4 dq-series | AssertionError "F1 gate" |
| T3 control: on the reference circle (1 − kφ ≈ 0.766) | step returned, F1 step count 0 → 1 |
| B1 `R1_HALF` set, `R1_KC` unset (sent as `R1_KCC`) | refused, rc 1, "B1 gate" in output |
| B1 `R1_FLOATS` alone | refused, rc 1, "B1 gate" in output |

Every plant was backed up, restored and checked by sha256 (t234's "other files unchanged"). The B1 rows require the
string "B1 gate" in the output, not just a nonzero rc.

**Consequence:** v5.1 is cleared for P3 under the Bridge's order (P3 waits until these results are read and sent).
