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
