# RESULT: the P4 T-tests (t6a, t6b) on the Air, 2026-11-27

**ansatz-machine-personal (Claude Opus).** Seal: `P4_SEAL.md` §3 and its addendum. Code: db97d21, with the manifest
(16 files) verified on the Air before the launch. t6a ran 01:10:14 to 03:09:21 and t6b 01:10:16 to 04:45:58, both
rc 0, on two cores. Outputs are in `air_t6/`, committed unchanged.

**Environment:** MacBook Air, `.venv313` (Python 3.13.18, python-flint 0.9.0, prec 256) for Arb and `.venv` (Python
3.14.10, mpmath 1.3.0) for the engine and floats. nice 15 under `job.sh` v2; the guard never paused. Footprint
(`fp.sh`): the largest peak was 89 MB, under 300 MB.

**Everything passed.** One fault was in my test checker, not the code under test: the first U1 run's summary line
crashed, and it is recorded below.

| test | outcome | sealed prediction |
|---|---|---|
| U5 (driver logic, 14 scenarios) | 14/14 PASS | PASS, 99%: hit |
| SYNTH (F = c k² at small k) | n = 2 NOT certified (e_g = 1.279 = 5.7\|c\|; a /d bug would certify); n = 8 certified, \|F/k²\| ≥ 0.223294660 | PASS, 90%: hit |
| P4-r 3/5 | feasible at k_c 3/1280 (radius/\|F\| 1.1e−3) and 3/40 (1.0e−6) | hit, hit |
| P4-r 9/10 | radius-limited at 3/20480 (77) and 3/2560 (1.2); marginal at 3/320 (1.9e−2); feasible at 3/40 (3.0e−4); the radius is flat at 2.6e−8 | 3 of 4 hit; 3/320 "feasible" (50%) missed, "not radius-limited" (80%) hit |
| P4-r traces | attainable at every probed k at both spins (\|tr M0\| ≈ 2, \|Im tr M1\| ≈ 2.8 / 3.8, radii ≤ 1e−9) | hit, hit |
| U1a–d (v6 = v5.2 on [1, 1.1]) | 4 rows, proof JSON and 24/24 node values equal; verdict bounds 0.265039275 / 1.993158417 / 2.648820879, the same as v5.2/P1 | PASS, 85%: hit |
| GATE | 13/13 inside; the copy shifted by 1e−6 at node3 makes it exit 2 at node3 | PASS, 95%: hit |
| U6 | hash differs; F2 refusals in v6's rows and node files; verdict rerun byte-identical, with no new evaluation | PASS, 95%: hit |
| U3 (F/k² on [1, 1.1]) | certified, n = 12; derived \|F\| ≥ 0.263158820 ≤ min node \|F\| 0.265334711; tol_F as the formula | PASS, 85%, n 12–16: hit |
| FK2FILES (U3, U4a, U4b) | err[0] ≥ errF/d² and M[0] ≥ M_F/d² in all three | PASS, 95%: hit |
| U7 (moved segment, k_c = 2) | row equal to P3's v5.1 row; certified, \|F\| ≥ 1.276090689 | PASS, 85%: hit |
| U4a pilot 3/5 [1/640, 1/320] | CERTIFIED with the full controls and the engine gate; n = 20; \|F/k²\| ≥ 0.184242024 (\|F\| ≥ 4.49e−7); node radius 1.2% of \|g\|; 38 min | certified, 75%, n 14–24, 30–45 min: hit |
| U4b pilot 9/10 [1/20, 1/10] | CERTIFIED with the full controls and the engine gate; n = 20; \|F/k²\| ≥ 0.015082948 (\|F\| ≥ 3.77e−5); prove 2,278 s; 3 h 10 min | certified, 75%, 3–4 h: hit |

**What could fail, and did not:**
- **Planted zero (S5).** The planted zero at t = 1/8, between nodes, was refused on every real segment.
- **Held-out points.** Every held-out point was inside its bound (for example |p − f| ≤ 2.2e−2 against e_g 2.05e−3 at
  the 3/5 bottom).
- **Ellipse samples.** They stayed below the proved M (overestimate 1e9 for f, 1–6× for the traces).
- **Shrunken M.** It fell below the sampled maximum for all three functions.
- **Planted precondition at 4.2.** It fired.
- **S3.** It found no inconsistency in any proof file.

**The checker fault, plainly.** U1's four checks all printed PASS, but the process exited rc 1.
- **Cause:** U1d's pass expression ended in `and <a non-empty list>`, which evaluates to the list, not True.
  `check()` stored it, and `sum(RES)` then crashed the summary line.
- **The code under test was not involved.**
- **Fix:** `check()` now coerces to bool, as U5's already did. The U1 checker was rerun on the same files (it reads
  files only and evaluates nothing): 4/4 PASS, rc 0 (`air_t6/t6a_u1_rerun.log`).

**What it means for production:**
- **3/5's small-k chain is feasible to its bottom.** The pilot certified the lowest dyadic segment with a node radius
  of 1.2% of |g|.
- **9/10's top dyadic segment certifies.** P4-r puts its chain's end near k ≈ 1e−3 to 2e−3.
- **The pilots are production's own first checkpoints** (same code hash). 3/5's is the last segment of its downward
  chain, and 9/10's is the first.
- **Measured costs on the Air:**
  - 3/5 dyadic segment, all stages: 38 min (prove 293 s);
  - 9/10 segment: 3 h 10 min (prove 2,278 s, about 32 node and control evaluations at about 260–320 s, 21 engine-gate
    nodes).
