# Route (i): non-author read of the office's v3/v4 code (registration §3(a), reading part). 2026-11-26

**Reader:** ansatz-machine-personal (Claude Opus). **Authorship, kept visible:** this session wrote v2
(`_nve_route1_segment_v2.py`, as the Fable side-session, 604d520/d855810/d18de63). It did NOT write v3, v4 or the
verdict wrappers (the office session did), and did not run the 9/10 certificate. So this is a non-author read of v3,
v4 and the 9/10 run only; v2 was checked by the office (b38af7d).

**Asked by** "Bridge - claude personal" (registration draft c3a61ab, §3(a)). **Code read at** c2dd39c
(`office/2026-11-26-ktaylor`), in a clean worktree beside the repo. `_nve_route1_segment_v2.py` and
`_nve_route1_proto.py` are unchanged between d18de63 and c2dd39c (checked with `git diff`).

**What is NOT done yet:** the reproduction of the 9/10 certificate from c2dd39c, the engine check at the nodes
(§3(b)) and pilot P1. They hold for the Bridge's go (cores needed elsewhere). The reproduction run script is
committed on `personal/2026-11-26-route1-check` (0cc8115), not started.

## Verdict of the read: no error found; four findings, none of which changes a certified number

### What was checked, line by line
**v3, `_nve_route1_segment_v3.py` (the centred z-enclosure), per step and per k-sub-box:**
- **The series.** The Taylor coefficients c_j of dq/dk in t = z − z_m at the point z_m are built by series
  arithmetic: c0″ = c_K″√(1 − kφ), integrated twice from the values at z_m, and the same for ∂_k c0.
  - The truncation is safe: cap = order + 4, and the first order + 1 coefficients are kept.
  - The values at z_m come from the Laurent series at the k-ball, with its Cauchy tail.
- **The remainder.** Σ_{j>N} |c_j| r^j ≤ M_out q^{N+1}/(1 − q), with q = r/R_out.
  - It is valid because M_out is v2's `dq_sup` on the square of half-side R_out around z_m, over the whole k-square.
  - That evaluation also certifies holomorphy there: G1, G2 ≠ 0, finite values, and Re(1 − kφ) > 0 on the rays.
  - So Cauchy's estimate |c_j| ≤ M_out R_out^−j holds for the true coefficients at every k.
- **The radius used.** r = hm is an upper bound of the step length, while every point of the step lies within hm/2
  (+ rounding) of z_m. That is conservative by a factor of 2.
- **min(centred, crude).** Both are upper bounds, so the minimum is one. If v2's crude evaluation fails on a step
  box, the whole ρ row is rejected (`return None`), exactly as in v2.

**v4, `_nve_route1_segment_v4.py` (k-Taylor starting values):**
- **The starting values** at z_m, for k = k_c + dk with dk a sub-box: c0 ∈ c0(k_c) + dk ∂_k c0(k_c) + (dk²/2)E0,
  ∂_k c0 ∈ ∂_k c0(k_c) + dk E0, and the same for c0′.
  - E0 = `d2kc0(z_m, K)` encloses ∂²_k c0 on the whole k-square.
  - The integral remainder of Taylor's theorem on the segment [k_c, k] ⊂ K is (dk²/2) times a weighted average of
    ∂²_k c0 with weight 2(1 − t) ≥ 0 of total mass 1. It therefore lies in the convex box E0, and ball arithmetic on
    the ball dk encloses the product. The first-derivative remainder is the same with weight 1.
- **When E0 is not certified** (d2kc0 returns None), the step keeps the crude bound.
- **Everything downstream of the starting values** is v3's, reused unchanged: the series, the remainder and
  min(centred, crude).
- **The ρ rows:** the precondition on K is checked per row, and so is the holomorphy of every step box (via the crude
  evaluation); the gauge, Dyson sum and M formulas are v2's.

**`_nve_route1_v4_verdict.py`:** it writes the v4 chosen row in v2's JSON format and runs v2's unchanged `nodes` and
`verdict`. The only behavioural changes are an fsync per node record and torn-last-record repair. `V.get` is
monkeypatched, and v2's stages look `get` up at call time, so the patch takes effect.

**Equal-n and v3 wrappers:** read; same pattern.

### Findings
1. **An argued link, now written down: which branch of √(1 − kφ) is used.** Every series step (v3/v4's dq-series,
   and the node evaluator's Taylor step) takes the principal square root of the series' constant term.
   - That is the branch the Laurent series continues only if Re(1 − kφ) > 0 at the expansion point. The Laurent
     series at infinity starts from 1 − 7k/30 > 0 and runs along the ray.
   - The code never checks this at the expansion point itself. It holds because v2's `d2kc0`, called inside the crude
     `dq_sup` on every reference step box Z for the row's whole k-square K, certifies Re(1 − kφ) > 0 on every ray
     ω = s/z, s ∈ (0, 1], for every z in Z and k in K.
   - The node walks and the series points lie on the same polygon, inside those boxes, at k in K. So the branch is
     right for every k the certificate uses.
   - Two places where it is NOT certified are both outside the proof: the K-a-point diagnostic constants (dKs = None
     skips d2kc0), and any use of the evaluator at k outside the row's K.
   - Recommendation: assert Re(1 − kφ(z)) > 0 at each series point. It costs one ball evaluation per step.
2. **Checkpoint keys omit the code version.**
   - `ROWS` (`route1_seg_v4{TAG}_rows.jsonl`) is keyed by ρ alone, and a rerun prints "from checkpoint" and reuses
     the row.
   - `CKFILE`'s key (segment, R, loop, step count, step hash) has no NORD, no R_out factors and no version.
   - A stale file from an earlier code state, or a committed copy, is therefore reused silently. In particular, a
     "reproduction" in a checkout that still holds the committed rows/dqck files recomputes nothing. My reproduction
     script moves them aside first (0cc8115).
   - Recommendation for production: put a code hash in both keys, and refuse a mismatching file.
3. **The verdict wrappers switch off v2's coverage cross-check.** They set `boxes = expected_boxes = [0, 0]`.
   - v4 still asserts coverage while proving: one bound per step, 25 k-sub-boxes per step via v2's `dq_sup` assert,
     and step boxes containing both step ends.
   - But the verdict stage no longer checks that the proof file it reads came from a complete run.
   - Recommendation: write the step counts × sub-box count into the v4 JSON and have the wrapper assert them.
4. **The point constants are printed against hard-coded v3 values.** The "z-direction control" line compares with
   literal numbers in the format string, not with v3's file. It is fine as a log, not as a control.
   - **Relabelled.** In `ROUTE1_KTAYLOR_OFFICE.md`, control 1 is now marked a LOG comparison, not a control (the
     Bridge's ruling).

### Rulings (Bridge - claude personal, 2026-11-26)
- **Findings 1–3 are REQUIRED fixes before any production run.** They are now registration v1 §3(d), F1–F3, written
  as `scripts/_nve_route1_segment_v5.py` (43a2de1, not yet run). Tests T1–T4 are listed there.
- **Finding 4:** relabelled as above.

### Follow-up from finding 2: did any earlier reproduction reuse committed checkpoints? No.
The full audit is in the registration, §3(e). In short:
- the office's reproductions (b38af7d, 7dd8c18) deleted the node files before rerunning, and their logs show
  "0 records already on disk";
- v1, v2 and v3 have no other checkpoints;
- the v4 proof stages (6d411a8, a75d7e3) ran in a fresh worktree, and their rows/dqck files were first committed by
  those very runs;
- the 9/10 certificate (2aebf34) is an original run with "0 records already on disk".

So those records stand as stated. The hazard applies to future reruns at 6d411a8 or later, until F2 is in use.

### What this read does not cover
- The Dyson/gauge chain and the M formulas are v2's, checked by the office (b38af7d), and not re-derived here.
- The reproduction of the numbers. That waits for the go: the proof stage runs about 1.1 core-h at 9/10, and the
  verdict comes from the committed node file in seconds.
- ATAP Thm 8.2: read at source by the office (`EPS_OFFICE_CHECK.md` B1).
