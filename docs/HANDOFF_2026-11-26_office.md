# Handoff: office ansatz-machine → ansatz-machine-personal (2026-11-26)

The office account is paused (weekly limit). The work continues in `ansatz-machine-personal`. This file is the state
of things as of this commit. Every hash below was printed by git. **No job of the office session is running** (see §6).

## 1. The claim: v3.1 stands, unchanged by today's work
- **Where it is:** `data/nve/CLAIM_FAMILY_II.md`, VERSION 3.1 (2026-11-26).
- **What v3.1 says:** Statement A, the local result near Kerr. It has an explicit, interval-certified ε_a per spin
  (2.79e−3, 1.92e−3, 8.39e−4, 1.06e−4; each corrected r is rounded down).
- **Its lineage:**
  - eps certifier: Fable 75957fd, merged with the office fix 9d0ee9f in main bd74e05;
  - office check: `EPS_OFFICE_CHECK.md`;
  - c2 formula and certificate: `C2_ANALYTIC.md` and `C2_OFFICE_CHECK.md`;
  - Lemma K: `MRS_SECTION.md` §5d.
- The one-sentence claim is still numerical overall.
- `ONLY_KERR.md`, `ONE_PAGER.md`, `README.md` and `CITATION.cff` carry the v3.1 status. Release v1.1.0 is DOI
  10.5281/zenodo.24533026; the concept DOI is 10.5281/zenodo.24431694.
- **Nothing public changed today.** Route (i) is unregistered. The two certified segments below are internal results
  and are not in the claim.

## 2. Route (i): certifying the claim over whole k-ranges in interval arithmetic (NOT registered)
**What a segment certificate is.** For every real k in a segment: F ≠ 0, tr M0 ≠ 0 and tr M1 ∉ [−2, 2]. The method
is Chebyshev interpolation on validated Arb node values, with ATAP Thm 8.2 error bounds. M (the bound on the
analytic continuation in an ellipse) is proved by a Dyson bound in a constant gauge, relative to the validated
reference solution at k_c.

**Two certified segments, both k ∈ [1, 1.1]:**

| spin | how it was certified | margins | commits |
|---|---|---|---|
| 3/5 | Fable v2, n = 24, ρ = 4 | \|F\| ≥ 0.265023401, \|tr M0\| ≥ 1.993158418, \|Im tr M1\| ≥ 2.648820919 | Fable 604d520 + d855810; office VERIFIED b38af7d |
| 3/5 | v3 (n = 18) | certifies; it also certifies at equal n = 24 | 8b9971c, 6d411a8 |
| 3/5 | v4 | certifies at equal n = 24, with every bound ≥ v2's | 6d411a8 |
| **9/10** | **v4 M, ρ = 4, n = 18**, on Fable's unchanged v2 nodes/verdict | **\|F\| ≥ 0.052377152, \|tr M0\| ≥ 1.976145507, \|Im tr M1\| ≥ 3.842809556**; all five controls pass | seal 10a843a, outputs c2dd39c, record 2aebf34 |

**The enclosure lineage.** All versions use the same chain; only the bound on |dq/dk| per step changes.

| version | what it is | 3/5 n | 9/10 n | commits / record |
|---|---|---|---|---|
| v2 (Fable) | crude box enclosure of dq/dk | 24 | 140 | 604d520 / d855810 / d18de63 |
| v3 (office) | centred Taylor model in z; the k-ball Laurent still inflates | 18 | 134 | 8b9971c; `data/nve/ROUTE1_CENTRED_OFFICE.md` |
| v4 (office) | v3 plus k-Taylor starting values (point-k_c Laurents + dk·∂_k + (dk²/2)·E, with E enclosed by v2's `d2kc0`), and per-step fsynced checkpoints | 12 | 18 | 5bcca66 → a75d7e3; `data/nve/ROUTE1_KTAYLOR_OFFICE.md` |

- **Constants per unit k on the k-disc:**

  | | v2 | v3 | v4 | intrinsic |
  |---|---|---|---|---|
  | 3/5 circle | 14.3 | 4.30 | 1.04 | 0.36 |
  | 3/5 lasso | 72.6 | 41.6 | 15.8 | — |
  | 9/10 circle | — | 669 | 8.62 | 0.65 |
  | 9/10 lasso | — | 124 | 34.5 | — |

  The full table is in `docs/ROUTE1_REGISTRATION_INPUT.md`, which also holds the v4 column.
- **Scripts on the branch `office/2026-11-26-ktaylor`:** `_nve_route1_segment_v4.py`, `_nve_route1_v4_verdict.py`,
  `_nve_route1_eqn_verdict.py`, `_nve_route1_v4_cktest.py`, `_nve_route1_v4_circle_diag.py`.
- **The interpreter:** Quantum's `/Users/sumit/Github/quantum/sims/.venv/bin/python -I`, read-only, with python-flint
  0.9.0.
- **The power cut (2026-11-26, about 06:52).** The first v4 worktree in /private/tmp was cleared at boot. The code was
  restored verbatim from the transcript (d08b1ca) and verified by reproducing every pre-cut number. See
  `data/nve/ROUTE1_KTAYLOR_OUTAGE.md` on the branch.

## 3. Open branches (all pushed; none merged into main)

| branch | head | holds |
|---|---|---|
| `office/2026-11-26-ktaylor` | c2dd39c | v4 code, checkpoints, the spin-3/5 and 9/10 proof-stage outputs, the 9/10 verdict (30 node records), the diagnosis, three seals |
| `office/2026-11-26-centred-encl` | 8b9971c | v3 code and outputs, seal 67c7661 |
| `office/2026-11-26-eps-fix` | 9d0ee9f | the office fix to Fable's eps certifier (already merged via bd74e05) |
| `fable/2026-11-26-route1-seg` | d18de63 | Fable's v2 route-(i) segment (3/5 certified, 9/10 proof stage only); worktree `/Users/sumit/Github/conjecture_machine-fable` |
| `fable/2026-11-25-eps` | 4bc7b37 | Fable's eps certifier (merged) |
| `fable/2026-11-25-c2-analytic` | 8d8d04c | Fable's c2 analytic work (merged) |

**Merging a route-(i) branch into main is a decision for the registration step,** not done here. The records on
main cite the branch commits.

## 4. Known issues
1. **The spin-9/10 circle overhead near ±43.6°.** The diagnosis (`route1_v4_circle_diag_9_10.out`, at 10a843a) shows
   the v4 circle constant (8.62) is about 10.9× the sampled true disc maximum. The true variation is 0.89× the point
   value.
   - About 70% of it comes from two dense step bins near polar angle ±43.6°, next to a singular point close to the
     circle. There the overhead is about 131× per bin and up to about 15,000× per step.
   - The seal's guess (inner poles, small √(1 − kφ)) is refuted: |1 − kφ| ≈ 0.74 everywhere.
2. **Attribution uncertain.** Between the (dk²/2)·E k-remainder and the outer-box Cauchy remainder (crude bound ×
   2⁻³¹), which one causes it is not yet measured.
3. **v4 uses the radial-integral enclosure of ∂²_k c0, not the Cauchy-on-Laurent-circle estimate** proposed in the
   design note. It is valid (an enclosure, not a sample) and already part of v2's verified chain. It is stated in
   seal 5bcca66.
4. **The checkpoint gate's behaviour on a garbled key.** A garbled key in a middle record is caught by the prefix
   check. A garbled key in the LAST complete record would only make that record be recomputed, which is harmless.
5. **Untracked on main, not from this work, left alone:** `data/nve/lower_kscan.out` (0 bytes, Nov 21) and
   `docs/SHARED_MOONSHOT_PLAN.md` (Sep 23).

## 5. Next steps, in order
1. **Draft the route-(i) registration** with the v4 costs for both spins. Inputs are in
   `docs/ROUTE1_REGISTRATION_INPUT.md`.
   - Measured per 0.1-wide segment at spin 9/10: proof stage about 1.1 core-h; nodes about 1.4 core-h at n = 18
     (161–190 s per node).
   - At spin 3/5: proof about 0.17 core-h; nodes at n = 12 cost about 13 × 25 s.
   - The registration must still close the gaps listed in that file: generalise beyond [1, 1.1], the Laurent-disc
     precondition per segment as k → 4, small-F spots, spin 4/5's k\*, region B, and a two-implementation rerun for
     any verdict.
   - The registration must be approved by the Bridge and Sumit before any run.
2. **Optional: the local circle fix at ±43.6°.** Finer k-sub-boxes or a smaller outer box on those steps only, after
   first attributing the overhead between the two candidate terms (a minutes-long measurement). Expected effect: the
   9/10 circle constant falls from about 8.6 toward 1. It matters only where the circle term starts to dominate M_F.
3. **The Zenodo v1.2 question** is waiting for Sumit. Nothing is to be released or edited publicly without his word,
   via the Bridge.

**Standing:** further spins and segments need the Bridge's word and the registration. Use the fleet rules: no caps,
pause-only guards, 1 core, nice 12, and checkpoints on durable disk. **No worktrees in /private/tmp.**

## 6. Sealed predictions and their status (2026-11-25 to 26)

| seal | what it predicted | status |
|---|---|---|
| f6988c8 (brief) / Fable's segment seal | spin 3/5 segment certifies | **HIT**; certified and office-VERIFIED (b38af7d) |
| 620c470 (Fable, 9/10 v2) | constants, ρ, n, precondition | graded by Fable in d18de63: circle (sealed 40) and n (sealed 50) **MISS**; lasso, ρ, precondition HIT; no certificate attempted |
| 67c7661 (office, v3 centred) | disc constants, n at both spins, P(n₉/₁₀ ≤ 40) = 75%, 3/5 certifies no weaker | n at 3/5 **HIT**; all 4 disc constants and n at 9/10 **MISS**; "certifies" PASS, "no weaker" **FAIL** by 1.3e−8 at fewer nodes (Bridge regrade, 180681e) |
| 5bcca66 (office, v4 k-Taylor) | z-direction identical; k-ratios; n; P(n₉/₁₀ ≤ 40) = 80%; equal-n controls; reproducibility | all **HIT** except the 9/10 circle disc ratio (**MISS**: 11× against 1.2–5×). Its named cause was later refuted (§4) |
| 10a843a (office, 9/10 verdict) | CERTIFIED; the three margins; five controls; cost 1.5–2.5 h | all **HIT**; cost slightly under (1.42 h) |

**Jobs: none running.** The office session's PIDs today were 3670, 7133, 9512, 21384 and 22607, each from its own
launch record. All have exited, checked with `kill -0`. The working tree is clean apart from the two untracked files
in §4.5. The ktaylor worktree has been removed after its branch was pushed; recreate it beside the repo with
`git worktree add`. No worktree is in /private/tmp.
