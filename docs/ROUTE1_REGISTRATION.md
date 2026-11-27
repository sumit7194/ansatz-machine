# Route (i) pre-registration — DRAFT v1, NOT APPROVED (2026-11-26)

**v1 (2026-11-26), on the Bridge's ruling after the non-author read (`data/nve/ROUTE1_V3V4_READ.md`):** adds §3(d),
three REQUIRED code fixes before any production run, and §3(e), an audit of the earlier reproductions. Production
now runs from v5 (§5), not v4. Nothing else changes.

**Status.** A draft for the Bridge and Sumit. Nothing in it may run until both approve it. Approval is recorded here
as a dated line, with the commit that adds it. Until then the only route-(i) results are the two internal segments in
§1, and neither is in the claim.

**Written by** ansatz-machine-personal (Claude Opus), the session that took over ansatz after the office handoff
(`docs/HANDOFF_2026-11-26_office.md`, 1e8ce36). **Inputs:** `docs/ROUTE1_REGISTRATION_INPUT.md`,
`data/nve/ROUTE1_KTAYLOR_OFFICE.md`, `data/nve/ROUTE1_CENTRED_OFFICE.md`, `data/nve/ROUTE1_OFFICE_CHECK.md`,
`data/nve/ROUTE1_9_10_OFFICE_DIAG.md`, and the branch `office/2026-11-26-ktaylor` (head c2dd39c).

## 0. In one paragraph
Route (i) replaces the 50-digit floating-point counts of region A with interval-arithmetic certificates, stretch by
stretch in k. Each stretch is certified by Chebyshev interpolation of validated node values, with an error bound that
uses a PROVED bound M on an ellipse in complex k. The method works: two 0.1-wide stretches are certified (spins 3/5 and
9/10). This draft fixes, before any production run: what is targeted, the three steps that must be done first (§3),
the rule for cutting the k-range into segments (§5), the controls (§6), the cost and its limits (§7), and what a
result does and does not change (§8).

## 1. What exists now (internal; unregistered)

| spin | k-stretch | method | certified margins | commits |
|---|---|---|---|---|
| 3/5 | [1, 1.1] | v2 (Fable), ρ = 4, n = 24 | \|F\| ≥ 0.265023401, \|tr M0\| ≥ 1.993158418, \|Im tr M1\| ≥ 2.648820919 | 604d520, d855810; office check b38af7d |
| 3/5 | [1, 1.1] | v4 M, on v2's 24 nodes (equal-n control) | every bound ≥ v2's; \|F\| ≥ 0.265334372 | 6d411a8 |
| 9/10 | [1, 1.1] | v4 M, ρ = 4, n = 18, v2's unchanged nodes/verdict | \|F\| ≥ 0.052377152, \|tr M0\| ≥ 1.976145507, \|Im tr M1\| ≥ 3.842809556 | seal 10a843a, outputs c2dd39c, record 2aebf34 |

The verdict conditions are, for every real k in the stretch: F ≠ 0 (irreducible), tr M0 ≠ 0 and tr M1 ≠ 0 (not
imprimitive; tr M1 ∉ [−2, 2] implies tr M1 ≠ 0), and tr M1 ∉ [−2, 2] (infinite order, so not finite). These are the
same conditions as the registered region-A counts (`SPIN_PREREGISTRATION.md`), and stronger in one place: the counts
exclude finitely many traces s, the certificate excludes the whole interval [−2, 2].

## 2. Target and scope
- **Target, per spin a ∈ {3/10, 3/5, 4/5, 9/10}, E = 4/5:** every REAL k in [ε_a, A_top(a)] satisfies the three
  conditions of §1.
  - ε_a is Statement A's radius (claim v3.1): 2.79e−3, 1.92e−3, 8.39e−4, 1.06e−4. The first segment overlaps it.
  - A_top is the top of region A as registered: 4 (spins 3/10, 4/5), 3.85 (9/10). For 3/5 it is ≈ 4.05 in the
    earlier runs, but see §4 item 1: the method as built cannot pass about 4.006. The registered region B starts at
    3.95 (3/10, 4/5) and 3.8 (9/10).
- **Real k only.** The claim is about real k. Route (i) was never registered as a complex argument-principle count
  (`EPS_OFFICE_CHECK.md` B2), so this is a stated choice, not a swap.
- **Out of scope:** region B (half-plane loops), the stretch up to 30/7 − 10⁻¹², the endpoint 30/7, and the
  floating-point counts already registered (GAPB, WINDOW, SPIN), which stay as they are. Even a complete success here
  leaves the top of the range numerical (§8).

## 3. Required BEFORE any route-(i) result counts (the Bridge's items a–c)
None of these has been done. Each gets its own short record; a failure stops the registration until resolved.

**(a) A non-author check of the office's v3/v4 code and of the 9/10 certificate.**
- Read `scripts/_nve_route1_segment_v3.py` and `_v4.py` against their records: the centred z-series of dq/dk with
  its outer-box Cauchy remainder, the k-Taylor starting values with E = `d2kc0` enclosed on the whole k-square, the
  min(centred, crude) rule, and the per-step checkpoint and its gate.
- Read `_nve_route1_v4_verdict.py`: that it feeds v2's unchanged `nodes`/`verdict` the v4 row and nothing else, and
  that `boxes = expected_boxes` is set consistently (v2's coverage assert compares them).
- Reproduce the 9/10 certificate from c2dd39c on a clean checkout: the proof file byte for byte, and the verdict from
  the committed node file.
- Proposed reader: this session. It wrote v2 (as the Fable side-session) but not v3 or v4, so it is a non-author of
  exactly the parts that are unchecked.

**(b) A second, independent implementation of the node values (two-implementation rule).**
- The 50-digit engine (`_nve_spin_scan.LauA`, mpmath) shares no code with the Arb evaluator. Run it at EVERY node of
  the two certified stretches (25 at 3/5, 19 at 9/10), on the same circle and the same lasso, and require each engine
  value to lie inside its node enclosure. About 44 × 25–35 s ≈ 25 min.
- Common-mode risk that this does NOT remove: both implementations use the same formula for c0″ (the Laurent series
  of c_K″√(1 − kφ) at infinity) and the same lasso vertices. The formula was checked symbolically against Neon's
  B(w, k) at spins 3/5, 3/10 and 19/20 (`SPIN_PREREGISTRATION.md`). The lasso is a choice of loop, not a computed result (§5).
- In production (§6) the engine runs at every node of every segment, as a gate.

**(c) The open question: was v4 at its own n = 12 run to a verdict at spin 3/5?** **No** (answered from the logs).
- `route1_seg_M_v4_nseg1.json` (6d411a8) chooses ρ = 6.5, n = 12 (rows: n = 16, 14, 12, 12 at ρ = 3, 4, 5, 6.5).
- The only v4 verdict at spin 3/5 is the equal-n control `route1_seg_3_5_v4eqn24.out` / `..._v4eqn24_nseg1.json`
  (ρ = 4, v2's 24 nodes): CERTIFIED. No 13-node file at ρ = 6.5 and no verdict on it exist on the branch.
- The office Bridge confirmed this (2026-11-26).
- **Pre-registration item:** run it, because production chooses the smallest n and this is exactly what production
  would do. Cost: 13 nodes + 3 held-out + 8 ellipse points at about 25 s, plus the engine at the 13 nodes: ≈ 15 min.

**(d) Required code fixes before any production run (from the read's findings 1–3).** Written as
`scripts/_nve_route1_segment_v5.py` on `personal/2026-11-26-route1-check` (43a2de1): v4's mathematics unchanged, plus
checks and keys only. NOT yet run or tested.
- **F1, the branch of √(1 − kφ).** Assert Re(1 − kφ(z)) > 0 at every expansion point: v2's Taylor step (reference
  walks and node evaluations) and v4's dq-series at each step midpoint (k a ball). A failure is a correctness gate
  (AssertionError), not the "refused box, halve ρ" path.
- **F2, code hash in every checkpoint key.** The hash is sha256 of proto, v2, v3, v4 and v5. It goes into the per-step
  dq checkpoint key, the rows file and the node file (each named by the hash; each record carries it). Any record
  with another hash stops the run; nothing from other code is reused.
- **F3, coverage counts asserted.** The proof JSON records per loop: steps, step bounds, k-sub-boxes and pairs. The
  verdict recomputes the expected counts from the step counts, asserts them and the code hash, and gives v2's
  `boxes == expected_boxes` check real numbers again (v4's wrappers had set both to [0, 0]).
- **Tests required before production** (each can fail; run on the go, a few minutes each at spin 3/5):
  - T1: v5's proof stage at spin 3/5 reproduces v4's rows exactly (the same M, n and bounds). The fixes add checks
    only, so any difference is a bug.
  - T2: a planted checkpoint record with another code hash must STOP the run.
  - T3: a planted expansion point with Re(1 − kφ) ≤ 0 must raise the F1 gate.
  - T4: a planted change of one coverage count in the proof JSON must make the verdict refuse.
- **v5's non-author check: DONE** by the Bridge (TheBridge `fleet/reads/ansatz_v5_read_2026-11-26.md`, 1885ac4):
  approved for T1–T4. It added A1:
- **A1, the environment in the hash.** The code hash also covers the Python and python-flint versions and the
  working precision, so a checkpoint written in another environment (the other machine) is refused like one from other
  code. Done in v5 at f435345 (`code_env` in the proof JSON). Not run.
- **T1 must compare v5 and v4 runs on the SAME machine AND under the SAME Python version** (the Bridge's condition,
  widened 2026-11-26 after the Air reproduction). A1 already enforces this for checkpoints.
- **Why the Python version matters (measured 2026-11-26).** The Air reproduction of the 9/10 v4 certificate under
  Python 3.14.10 differed from the committed 3.13.12 run, and only in the rows that were not chosen (ρ = 3, 5, 6.5):
  - their float gauge matrices differ by an ulp, and the bounds computed through the gauge move with them by
    1e−12 to 1e−9 relative;
  - the dq checkpoint, the chosen row (ρ = 4) and the verdict are byte-identical.
  Cause: complex × complex results differ between Python 3.13 and 3.14. Both 3.14 builds (3.14.5 Mac mini, 3.14.10 Air)
  agree with each other, and the other float/libm operations the gauge uses hash identically under all versions tested.
  The gauge is a free choice (any invertible C gives a valid bound), so both runs are valid proofs.
  Record: `data/nve/route1_check/AIR_REPRO_9_10.md` (`personal/2026-11-26-route1-check`, d74218a).

**(e) Audit: did any earlier "reproduction" silently reuse committed checkpoints?** **No.** Checked from the office
session's commands and logs (its transcript, with the commands as run) and from the committed logs at c2dd39c:
- **b38af7d (office check of v1/v2):**
  - v1: the node file was deleted before the rerun, and the log shows "0 records already on disk".
  - v2: its node file was deleted the same way.
  - v1 and v2 have no other checkpoint.
- **7dd8c18 (the spin-3/5 rerun at d18de63):** the node file was deleted first.
- **The v3 reproduction (from 8b9971c):** v3 has no checkpoints.
- **6d411a8 and a75d7e3 (the v4 proof stages):** run in a fresh worktree after the power cut. Their rows and dqck
  files were first committed BY those runs, and the logs contain no "from checkpoint" or "resuming" line. So nothing
  existed to reuse.
- **2aebf34 (the 9/10 certificate):** the original run, not a reproduction. Its node log shows "0 records already on
  disk".
- **Reuse by design, and stated as such in its record:** the equal-n controls (6d411a8) ran on a copy of v2's node
  file ("36 records already on disk").

The hazard is real for FUTURE reruns: any checkout at 6d411a8 or later holds committed rows/dqck files that v4 would
read back. F2 closes it. Until then, a rerun must move them aside (as `run_repro_9_10.sh`, 0cc8115, does).

## 4. Gaps the method must close, with the plan for each
1. **The Laurent-disc precondition near k = 4.** c0″ is evaluated from its Laurent series at infinity, which needs
   the B roots inside |w| < 1/0.81 for every k in the segment's k-square. Certified at k = 4.0 ± 0.001 (largest root
   |w| = 1.0996); refused at 4.01 ± 0.001 (1.3431). The real crossing is near 4.006 (hand estimate).
   - Plan: segments near the top shrink until the precondition passes; region A is targeted only up to
     min(A_top, the last segment that passes). At spin 3/5 that leaves (~4.006, 4.05] uncovered. It is NOT certified
     by this registration; it would need another representation of c0 there, or the region-B design.
2. **Small F just above ε_a.** |F| ≈ |c2|k² is 1e−7 to 1e−10 there.
   - Plan: dyadic segments [x, 2x] from ε_a up to 0.1, interpolating F/k² (analytic: F has a double zero at k = 0).
     The ellipse must not contain k = 0: R < k_c, i.e. ρ + 1/ρ < 6 on [x, 2x], so ρ ≤ 5.
     M for F/k² is M_F/(k_c − R)². About 6 (spin 3/5) to 10 (spin 9/10) such segments.
   - Not built. It changes only the interpolated function and the bound, not the evaluator.
3. **Spin 9/10's third zero of F at k ≈ 0.11 + 0.34i.** A complex zero does not affect the certificate (F stays
   analytic), contrary to the input's "keep it outside the ellipses"; it only lowers min |F| on the real axis nearby.
   Listed so the cost estimate allows more nodes there.
4. **Spins 3/10 and 4/5 are unmeasured.** v2 (and so v4) reads the spin and circle from `NVE_SPIN`, `R1_R0`; neither
   has been run at these spins. Pilot P2 (§5) measures them.
5. **How the constants change with k.** Measured with v4 only at k ≈ 1. With v2's crude bound the 3/5 constants
   doubled from k = 1 to k = 3; v4's are unmeasured away from 1. Pilot P3 measures them.
6. **The 9/10 circle overhead near ±43.6°** (`ROUTE1_KTAYLOR_OFFICE.md`). Optional: a minutes-long attribution
   between the k-remainder and the outer-box remainder, then a local fix. It changes n only where the circle term
   dominates M_F; at k ≈ 1 the lasso dominates. Not a prerequisite.
7. **Evaluation cost at spin 9/10.** About 170 s per node against 25 s at 3/5, because the circle needs about 17,900
   Taylor steps: the step boxes are limited by the Laurent ratio (the circle sits at 0.79 of the Laurent radius).
   Optional speed-up: another representation of c0 near the circle. It needs its own non-author check. Not a
   prerequisite.

## 5. The production design (fixed before any run)
**Per segment [k_lo, k_hi], k_c its midpoint:**
1. **Loops:** circle |z| = R0(a) (1.1492, 1.35, 1.3382, 1.2639) and the engine's capsule lasso at k_c, fixed over the
   segment. The holomorphy boxes certify that no singular point reaches either loop for any k in the k-disc.
   Different segments may use different lassos: the three conditions are about the subgroup ⟨M0, M1⟩, and if that
   subgroup is Zariski-dense so is the monodromy group. No homotopy consistency between segments is needed.
2. **Proof stage:** v5 (`_nve_route1_segment_v5.py` = v4 + F1–F3, after §3(a) and §3(d) T1–T4), ρ ∈ {3, 4, 5, 6.5}. Choose the row with the smallest
   n; ties go to the smaller error bound. Precondition and holomorphy are certified per row; a row that fails is
   rejected. **Production runs pin the exact Python minor version** (and record the patch level) along with the
   pinned packages, because the float gauge, and so every non-certified number, depends on it (§3(d)).
3. **The n target:** the interpolation error bound must be ≤ 1e−2 × |F(k_c)| (from the reference solution), and the
   same for the traces. This only steers n; the verdict's validity does not depend on it.
4. **Split rule:** if no row is admissible, or the chosen n exceeds 40, split the segment in half and redo both halves.
   Splitting does not end any job; it is a design rule, fixed here. A segment narrower than 1e−4 that still fails is
   reported as UNCOVERED and is not split further.
5. **Nodes and verdict:** v2's unchanged `nodes`/`verdict` stages on the chosen row, through v5's `verdict` (F1–F3):
   one fsynced jsonl line per node, keyed (spin, segment, n, node) in a file named by the code hash, resumable.
6. **Initial segmentation:** 0.1-wide from 0.1 to the top, dyadic below 0.1 (§4.2).

**Pilots, in order, before production at any spin** (each sealed before it runs; one process, one core, nice 15
while the box is loaded):
- **P1:** §3(c), the spin-3/5 v4 verdict at its own n = 12 (≈ 15 min).
- **P2:** v4 proof stage at k_c = 21/20 for spins 3/10 and 4/5 (≈ 10–20 min each).
- **P3:** v4 proof stage, one row (ρ = 4), at k_c ∈ {1/2, 2, 3, 3.9} for spins 3/5 and 9/10 (≈ 5 min each at 3/5,
  ≈ 20 min each at 9/10): the constants and n as k grows.
- **P4:** one dyadic small-k segment at spin 3/5 with the F/k² interpolation (after it is built and checked).
- The production cost estimate (§7) is re-done from P1–P3 before the Bridge's go for production.

## 6. Controls (each must be able to fail)
**Per segment:**
- **Engine gate (two-implementation rule):** the 50-digit engine at every node; each value must lie inside its node
  enclosure. A miss stops the run at that node boundary and is reported.
- **Planted zero:** certify F − F(k_c) ≠ 0 on the same nodes; it must be REFUSED. No extra evaluations.
- **One held-out point** (t = 1/8 on the segment): it must lie inside interpolant ± bound.
- **Two ellipse samples:** the proved M must be at least each sampled |F|, |tr M0|, |tr M1|.

**Per spin, on one segment:** the full set used so far (3 held-out points, 8 ellipse samples, the shrunken-M control
M ÷ 1e12), and the planted precondition at k = 4.2 (must fire).

**Per production batch:** the verdict stage rerun from the committed node file must reproduce the verdict file byte
for byte.

**Gates, all stopping only at a checkpoint:** a non-finite enclosure, a failed holomorphy or precondition box (the row
is rejected; the run continues), a coverage-count mismatch, an engine miss, a failed self-test.

## 7. Cost, and the limits beside it
**Measured per 0.1-wide segment at k ≈ 1** (one core, busy box):

| | proof stage | nodes | engine at the nodes | per-segment controls | total |
|---|---|---|---|---|---|
| spin 3/5 (n = 12) | ≈ 0.17 core-h for 4 ρ rows (handoff) | 13 × 25 s ≈ 5.5 min | 13 × 25 s ≈ 5.5 min | 3 × 25 s ≈ 1.3 min | **≈ 0.4 core-h** |
| spin 9/10 (n = 18) | 4070 s for 4 rows (≈ 230 s walk + ≈ 16 min per row) | 19 × 170 s ≈ 54 min | 19 × 30 s ≈ 10 min | 3 × 170 s ≈ 8.5 min | **≈ 2.3 core-h** (≈ 1.5 with one row) |

**Region A per spin** (segment counts from §5.6; constants assumed as at k ≈ 1, which P3 will test):
- **spin 3/5:** about 40 segments of 0.1 plus about 6 dyadic ones: **≈ 17 core-h**, or ≈ 35 if the constants double
  with k as v2's did.
- **spin 9/10:** about 38 + 10 segments: **≈ 70–110 core-h** (one row or four), up to ≈ 2× more if the constants grow.
  Most of it is the 17,900-step circle walk (§4.7).
- **spins 3/10, 4/5:** unknown until P2.
- On one core, spin 9/10 alone is 3–9 days of wall time. Running segments in parallel would need the Bridge's cores.
- **Do not use** Fable's 250–300 core-h figure for 9/10: it was an enclosure artifact.

**Limits (no job-ending caps anywhere):**
- No wall-clock, step or iteration caps. Pressure (memory, disk) pauses this run's own verified PIDs and alerts the
  Bridge; it resumes on recovery.
- Checkpoints: one fsynced jsonl line per node; per-step dq checkpoints every 200 steps in the proof stage (v4,
  7187b5b). Loss on a crash: at most one node, or 200 steps of one proof stage.
- Peak memory measured at 28–76 MB (footprint 16 MB at 3/5).
- The split rule's floor (1e−4) is a coverage decision, not a cap: such a segment is reported, not dropped silently.
- One core, nice 12; it counts toward the fleet's 9.

## 8. What a result changes, and what it does not
- **Per spin, if every segment of [ε_a, A_top_reached] certifies** and §3(a)–(c) passed: the claim's status could say
  that at that spin the statement is interval-certified on (0, A_top_reached], rigorous relative to the applicability
  chain (the same caveats as Statement A), with the rest of the range still numerical.
- **Any claim text change needs Sumit's go via the Bridge,** as a new claim version. Nothing public changes from this
  registration by itself; no Zenodo release follows automatically.
- **An UNCOVERED or failed segment** is reported as such, with its reason. It does not make the claim false: the
  registered floating counts cover it numerically, and it stays numerical.
- **A certificate is a proof:** choices made in this design (segment widths, ρ, n) cannot make a wrong certificate
  right or a right one wrong. The pre-registration fixes scope, cost and reporting, so that what is claimed afterwards
  matches what was planned.

## 9. Branches and merging
## 5A. Amendment for production (2026-11-27, before the production seal)

**Scope (Sumit, via the Bridge):** the measured reach only:
- spin 3/5 from ε_a up to k = 3;
- spin 9/10 from ε_a up to k = 2;
- the dyadic small-k segments included.

The top of region A is parked. This is stated as a partial result covering part of region A.

**Code: v6** (`_nve_route1_segment_v6.py` = v5.2 + P4: a relative n target, F/k² on the dyadic segments, a
general-segment verdict, a radius-limited test), with the engine gate (`_nve_route1_engine_gate.py`) and the driver
(`_nve_route1_production.py`). The Bridge read it at 10707e1, and the fixes S1–S7 come before the T-tests.

**Amendments to §5:**
- **§5.2: ρ = 4 only, one row per segment.** This replaces ρ ∈ {3, 4, 5, 6.5}. P3 measured the single-row cost; four
  rows cost about 40% more for at most a few nodes fewer. ρ = 4 keeps R < k_c on every dyadic segment and its halves,
  which the F/k² bound needs. A row with R ≥ k_c in F/k² mode is rejected.
- **§5.3, the traces' n target:**
  - n is targeted on F (on F/k² for the dyadic segments) only, at error bound ≤ 1e−2 × |F(k_c)| (or |F(k_c)|/k_c²).
  - The traces' error bounds at that n are computed and checked by the verdict like F's. They are not separate n
    targets. In every row measured so far (P1–P3) they were orders of magnitude below their margins.
  - A trace condition that fails is not cured by splitting when it fails even with zero interpolation error. The
    radius-limited test covers that case.
- **§5.4, the split rule:**
  - a failing segment (no admissible row, or not certified) is halved down to depth 2;
  - a segment that still fails at depth 2 stops its chain (Sumit's stop rule);
  - a failure that persists with zero interpolation error (radius-limited) stops its chain without splitting;
  - the reach actually achieved is reported, and no new code is written mid-run.

  This replaces "narrower than 1e−4 → UNCOVERED".
- **§5.6, segmentation:** a downward chain of dyadic segments from 0.1 to below ε_a in F/k² mode, then an upward chain
  of 0.1-wide segments from 0.1 to the top in F mode.

**Amendments to §6:**
- The planted zero is placed at the held-out value (f − f(t = 1/8)), between nodes.
- The per-spin full controls run on the first certified segment of each mode.
- Every number the verdict uses (R, the error bounds) is recomputed in balls.

**A known risk, measured before the long runs (pilot P4-r):** at spin 9/10 the bottom of the dyadic chain is probably
out of reach.
- F ≈ c2 k² with |c2| ≈ 0.016 is about 3e−10 near ε_a.
- The evaluator's node radii are up to about 1e−8 to 1e−7.

If P4-r confirms this, the 9/10 result is [the lowest feasible k, 2], and the gap is reported plainly. The evaluator
change that could close it is parked.

`office/2026-11-26-ktaylor` (v4) and `fable/2026-11-26-route1-seg` (v2) are NOT merged into main by this draft. The
registration, once approved, says which code version production runs from (by commit), and the merge happens with
the first production record.

## Approval
- Draft v0: 2026-11-26, c3a61ab. Not approved.
- Draft v1: 2026-11-26, 8fd935b (adds §3(d) F1–F3 and tests T1–T4, §3(e) the reuse audit; production on v5).
  Not approved.
- Draft v1, amended 2026-11-26, 329ccfb: A1 added to §3(d); v5's non-author check recorded. Not approved.
- Draft v1, amended 2026-11-26, this commit (the Bridge's ruling on the Air reproduction): T1 under the same machine
  AND the same Python; production pins the Python minor version (§5.2); the Python-version finding recorded in §3(d).
  Not approved.
- Amendment §5A, 2026-11-27 (this commit): Sumit's production scope (the measured reach), ρ = 4 only, the traces' n
  target, the split and stop rules, the per-segment controls as built in v6, and the 9/10 small-k risk. It is written
  before the production seal, on the Bridge's read of the P4 build.
- **APPROVED (scope and production), recorded 2026-11-27.** Sumit approved the production scope via the Bridge:
  - spin 3/5 on [ε_a, 3];
  - spin 9/10 on [ε_a, 2];
  - the top of region A parked.

  Production was launched on 2026-11-27 at 04:49 (seal 019d7bc, on `personal/2026-11-26-route1-check`), under §5A.

  Later that day, Sumit also approved (via the Bridge) spin 3/10 and spin 4/5, each on [ε_a, 3]. They run the same
  code and settings, with seals 8d94f79 and 3ca2294 on the same branch, launched 15:00 and 15:02.

  This line was recorded afterwards, at the v1.2.0 release prep.
