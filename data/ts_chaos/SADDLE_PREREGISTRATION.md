# Is the TS δ = 2 capture-edge boundary a genuine fractal? A lifetime-interval (topological-entropy) test. Pre-registration, 2026-11-17, BEFORE any run

Ask: the user, via the Bridge ("go on all proposed items"). This is the one open item of §150. The HP crossover test
(fdb028d) returned "finite-time artefact" by its rule, but it lacked power: most sampled orbits plunge early, so doubling
the horizon N did not lengthen their exposure (post-hoc diagnosis in §150).

## The question, made testable
Along a line of initial conditions x0 (y = 0, p_x = 0, p_y from the shell) across the inner survive/plunge window W, let
n(x0) be the orbit's LIFETIME: section crossings before plunge, capped at N_max = 600. For a threshold t, let
𝒩(t) = the number of disjoint intervals (maximal runs) of {x0 ∈ W : n(x0) ≥ t}.
- **Chaotic saddle, i.e. a genuine fractal boundary in the N → ∞ limit:** long-lived x0 lie near the saddle's stable
  manifold, a Cantor set on the line. The set {n ≥ t} breaks into exponentially many intervals: 𝒩(t) ~ e^{h t} with
  h > 0, the topological-entropy signature. New, longer-lived peaks keep appearing inside every long-lived interval.
- **Smooth boundary (no saddle, e.g. Kerr):** long lifetimes occur only near isolated boundary points (log-divergent
  whirl lifetimes), so 𝒩(t) stays bounded: one interval per boundary point, for every t.

This statistic does not depend on horizon doubling. It conditions on lifetime directly, which is what the post-hoc
diagnosis called for.

## Instrument
- The validated DD engine (`scripts/_hp_dd.py`, ~32 digits, GBS k = 12), at **R1 (tol 1e−22)** for the search.
- **Extension:** x0 is passed as a DD value (hi + lo), so brackets down to ~1e−20 relative are representable; until
  now x0 was a double, ulp ~2e−15 at x ~ 10. The double-only path is unchanged when lo = 0, and that is checked.
- Lifetime n: crossings before plunge (x < 1.5) or escape, capped at 600 (a survivor counts as 600). Event conventions
  are as in the HP probe.

## Search (fixed now)
- **Level 0:** a uniform grid of 2001 points over W.
- **Level ℓ + 1:** for each level-ℓ LOCAL MAXIMUM of n with n ≥ 20 (n_i > n_{i−1} and n_i ≥ n_{i+1}; a plateau
  counts as one maximum), place 17 equally spaced points across its bracket [x_{i−1}, x_{i+1}].
- At most 300 brackets per level (highest n first). Stop at bracket width < 1e−18 relative, at level 10, or at the
  orbit budget.
- **Budgets:** TS 10,000 orbits; Kerr 3,000.
- 𝒩(t) is computed from ALL evaluated points sorted by x0 (maximal runs with n ≥ t), for
  t ∈ {50, 100, 150, 200, 300, 400, 500, 600}. Every count is a LOWER BOUND on the true 𝒩(t) (unsampled intervals are
  missed), and it is reported as such.
- **h** = the slope of ln 𝒩(t) against t, by least squares over t ∈ [50, 400] where 𝒩(t) ≥ 2, with a bootstrap CI over
  level-0 cells (1000 resamples).

## Systems and windows
- **TS:** p = 4/5, E = 0.97, L = 41/8 (α level L1), W = [9.912067, 9.945202].
- **Kerr:** p = 4/5, the separatrix-matched L = 2.550268, W = the 0.03-wide window centred on its boundary point (the
  α addendum-2 rule), so the control has room to show branching if it had any.

## Controls
- **Positive (instrument can see branching):** a 1D map with a known Cantor survivor set, scanned by the SAME
  refinement code: the open tent map x ↦ 3x (mod the escape gap), 𝒩(t) = 2^t, h = ln 2. It must recover
  h ∈ [0.6, 0.8], fitted over t ∈ [2, 8] (beyond that, 2^t exceeds the 300-bracket search cap, by design).
- **Negative (smooth):** Kerr above. 𝒩(t) ≤ 2 for all t is required; otherwise the TS reading is void.
- **Precision:** the 30 longest-lived TS peaks are re-run at R2 (1e−28). n must be identical in ≥ 27/30; otherwise
  the peak counts above the lowest disagreeing lifetime are flagged unreliable.

## Predictions (sealed by this commit)
| item | prediction | confidence |
|---|---|---|
| positive control h ∈ [0.6, 0.8] | yes | ~95% |
| Kerr 𝒩(t) ≤ 2 for all t | yes | ~90% |
| TS 𝒩(t) grows with t, h > 0 with the CI excluding 0, and 𝒩(400) ≥ 3·𝒩(100) | **supports a genuine chaotic saddle (fractal in the limit)** | ~65% |
| TS 𝒩(t) bounded (≤ 3) | supports no saddle (the HP "artefact" reading) | ~25% |
| R2 lifetime agreement ≥ 27/30 | yes | ~80% |

**Reading rules:** a Kerr failure or a positive-control failure voids the TS verdict. Any other outcome (growth, but
below the 3× criterion) is reported as INCONCLUSIVE with the numbers. Nothing here is re-scored after the data.

## Resources (the Bridge's box rules)
- 2 workers, nice 10, detached, checkpointed per orbit, < 1 GB RAM, < 100 MB disk.
- Stop guard: free disk < 5 GB, or memory pressure not normal, or swap > 2 GB → stop cleanly (the checkpoint keeps
  progress).
- ~8 h estimated. The Bridge is told at launch and at finish.

## Addendum 1 (2026-11-17, after the Kerr control finished and BEFORE any TS output was read)
**Defect seen in the Kerr log:** levels 1–10 each "refined" the same single bracket (width 0.015) and added no orbits.
The top local maximum was a plateau of points surviving to the cap (n = 600), and 17 points placed across a capped
plateau just reproduce the plateau. For Kerr this is harmless (N(t) = 1 is still the smooth-boundary answer). For TS,
capped plateaus come first in the highest-n ordering, so they could fill the 300-bracket cap and starve the real
(n < 600) peaks where any branching lives. The TS run was stopped by its owner at 15 orbits; nothing was read.

**Fix (the same for TS, Kerr and the control):**
1. A local-maximum plateau AT THE CAP is refined at its two EDGES, [x_{i−1}, x_i] and [x_j, x_{j+1}], not across its
   interior. That is where the survive/plunge boundary structure is. Plateaus below the cap are refined across, as
   before.
2. A bracket already refined (same endpoints) is never refined again, and does not count toward the 300 cap.

Everything else is unchanged: thresholds, budgets, the statistic, the controls, the predictions, the reading rules.
Kerr and the tent control are re-run under the fix (orbits come from the checkpoint cache).

## Addendum 2 (2026-11-18, after the Kerr control FAILED and BEFORE any TS output was read)
**Outcome of the registered test: VOID.** Kerr gave 𝒩(t) = 112–141 against the required ≤ 2. The reading rules void
the TS verdict, and nothing here changes that. The TS R1 data are committed and sealed unread (02682bb; sha256 of
ts.jsonl 9876f3c9…8317) and will STAY unread until the rerun below has its own verdict.

**Diagnosis (Kerr data only):** every extra Kerr interval lies in a band 1.8e−10 wide at the boundary point, reached
at refinement levels 6–7. 24 random band points rerun at R2 (tol 1e−28): **all 24 survive to 600 at R2. At R1 only 6/24
did; the others plunged spuriously after 21–476 crossings** (data/ts_chaos/saddle/kerr_band_R2.json). Near Kerr's
separatrix the R1 integration error decides on which radial pass the orbit plunges. That is a precision floor of the
instrument, and the prereg's search refines straight through it. The control did its job: it caught an instrument
defect that the TS data alone would have shown as "branching".

**Proposed rerun (a new verdict; the original stays VOID):**
1. **Kerr first, at R2**, with the identical search (window, grid, thresholds, budget 3,000). Pass = 𝒩(t) ≤ 2 for all
   t. If it fails, stop: the DD engine cannot resolve this boundary, and §150 keeps "finite-horizon" wording.
2. **Only if Kerr passes: TS at R2**, with the identical search and a budget of 3,000 orbits (R2 costs ~4× R1). The
   statistic, h fit, bootstrap and thresholds are as in the prereg and `analyse`, unchanged.
3. **Precision check, made stricter:** the top-30 TS peaks AND 30 random points with 20 ≤ n < 600 are rerun at
   tol 1e−31 (near the DD floor). Pass needs ≥ 27/30 identical in each set. If either fails, the TS verdict is
   INCONCLUSIVE (precision-limited).
4. Reading rules and predictions as in the prereg. The budget cut lowers the counts (they are lower bounds), so the
   3× criterion is unchanged and is stated to be harder to meet.
Needs a slot from the Bridge (step 1 ≈ 2 h on 2 cores; step 2 ≈ 12–14 h on 2 cores).

### Addendum 2, step 1 outcome (2026-11-18 08:33): Kerr at R2 FAILS. Stop, as pre-registered.
At R2 the Kerr search stayed on one bracket through level 7 (width 9e−13), past where R1 broke down. Spurious
intervals appeared at levels 9–10 (widths 3e−15 to 2e−16): 𝒩(t) was far above 2 again (counts in
data/ts_chaos/saddle/kerr_R2_summary.json). **Step 2 is NOT run. The TS R1 data stay sealed and unread.** §150 keeps
"finite-horizon fractal-like" wording.
**Reading (post hoc, labelled as such):** the failure scale tracks the tolerance. It sat near 1e−11 at tol 1e−22 and
near 1e−15 at tol 1e−28, roughly width ∝ √tol. That fits a margin quadratic in the distance to the separatrix
(Δx² ~ integration error). On that scaling the double-double floor (~1e−32) cannot resolve below ~1e−16 to 1e−17. The
prereg's refinement to 1e−18 was therefore unreachable for this engine at any rung. A valid version would need a
refinement floor set by a Kerr calibration (stop at width ~10·√tol), or a higher-precision engine. That is a new
design, not a rescue of this one.
