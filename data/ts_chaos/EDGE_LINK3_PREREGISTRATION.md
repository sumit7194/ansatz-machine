# Edge-link v3: classify the §150 window's fate switches by the ownership slope. Pre-registration, 2026-11-19, BEFORE any code

**Ask:** Sumit's go, relayed by the Bridge, on the §156 proposal: fate bisection plus the ownership slope. The Kerr
precision check comes first.
**Model:** Claude Opus 5.5 (ansatz-machine).
**Data seen before registration:** §155 and §156 in full, including §156's window counts. 160 of 400 samples plunge
within 300 crossings; there are ~119 fate-flip neighbour pairs; 7 samples visit γ.

## Why this works, and the one trap (reasoning, written before code)
- **Every fate boundary inside D lies on W^s(γ).** T-L3′ gives a one-way gate: an orbit that leaves cl(D) plunges and
  never returns. Inside D, the boundary of the exit lobe L = D ∩ P⁻¹(Σ \ cl(D)) is P⁻¹(∂D) ∩ D. Of ∂D = U ∪ R(U),
  P⁻¹(U) ⊂ U lies on ∂D, so the interior part is P⁻¹(R(U)) ⊂ W^s. The boundaries of {exits at step k} are preimages
  of that, so also W^s. On ℓ, symmetry (F-a) adds nothing new.
- **The trap: timing steps.** Lifetime = (crossings to exit D) + (crossings from exit to plunge). The second term can
  step by one where the plunge happens just before versus just after a section crossing (the K-A type). That
  boundary is not on W^s, and its slope is 0. **It must not count as a falsifier.**
  - It is recognised because both members plunge and their lifetimes differ by ≤ 2 when continued to a larger cap.
  - A strand separates an inward exit from an outward excursion, so the lifetimes differ by an excursion or more.
- **Ownership slope** (validated in §156): ρ_min ∝ w^(1/2) on a W^s strand, ∝ w at γ, and constant when not owned.
  Here ρ_min is the larger of the two members' minimum ρ over all crossings up to the cap, so no visit threshold is
  needed. This is the fix for §156's vacuity.

## Definitions (fixed)
- Engine, level, frame and ρ as in §155/§156 (`_ts_edge.EdgeMap`, `_ts_edge2.history`).
- **Fate F_N(x)** = plunges (status 1) within N crossings. Primary N = 300.
- **Bisection on F_300** between neighbours with different F_300, to w/x ≤ 1e−18 or 70 halvings. Each stage records
  w and ρ_min(w) as above.
- **Slope** fit and classes exactly as in §156: fit over w/x ∈ [1e−15, 1e−5]; ≥ 6 decades needed;
  "strand" = [0.4, 0.6], "at γ" = [0.85, 1.15], "not owned" < 0.2.
- **Final checks** on the final pair (p: F_300 true, q: false):
  - lifetimes at cap 600, at R2 and R1;
  - F_300 at R1.

## Classes for a bisected switch
- **TIMING** (cap artefact, γ not involved): both members plunge within 600 at R2, and |n_p − n_q| ≤ 2.
- **STRAND:** not TIMING, slope "strand", and R1 agrees on F_300 for both members.
- **FALSIFIER:** all of:
  - not TIMING;
  - slope < 0.2 over ≥ 6 decades;
  - final ρ_min ≥ 0.1;
  - R1 agrees on F_300 and on the cap-600 fates of both members.
- **OTHER:** anything else (reported, with reasons).

## Step 1: the Kerr precision check (run FIRST; if it fails, STOP and report before any TS)
| check | what | must give |
|---|---|---|
| P-log | Kerr lifetimes n(d) at x_h + d, d = 10^(−k/2), k = 4 … 32 | dn/dlog₁₀(1/d) within 5% of 1/log₁₀ λ_Kerr; this is the law that places cap steps at d\* ~ λ^(−(N − n₀)), far below resolution |
| K-sep-F | Kerr: bisect F_300 from x_h ± 1e−6 | converges to the closed-form x_h within 1e−16; class STRAND |
| K-timing | Kerr: a timing step outside x_h, found by scan, then bisected on F_N with N = the smaller lifetime | class TIMING (and so NOT FALSIFIER) |
| MF-1, MF-2 | §156's artefact pairs, re-classified under these classes | NOT STRAND |

## Step 2: TS window (only if step 1 passes)
- The 400 window samples' F_300 values are **reused** from §156's checkpoint (`edge2/window_ts_histories.jsonl`, R2,
  cap 300).
- Candidates: neighbour pairs with different F_300. The **first 16 in x order** are bisected and classified. (The cap
  is for cost; 16 × ~12 min ≈ 3.2 h.)
- **Verdict words (this (E, L) level only):**
  - **VOID:** step 1 fails.
  - **FALSIFIED:** any FALSIFIER.
  - **SUPPORTED on the sample:** ≥ 3 STRAND, 0 FALSIFIER, and ≥ 80% of the non-TIMING switches are STRAND.
    - With §154's horseshoe and reasoning W-2, this licenses "a Cantor set of edge points lies in the §150 window".
    - It also licenses "every sampled non-timing switch is on W^s(γ)". Numerical, on the sample.
  - **VACUOUS:** fewer than 5 non-TIMING switches classified.
  - **NOT ESTABLISHED:** otherwise.
- Nothing licenses α, other levels or EMRIs.

## Predictions (sealed by this commit)
| item | prediction | confidence |
|---|---|---|
| step 1 passes | yes | ~75% |
| verdict SUPPORTED | yes | ~55% |
| verdict FALSIFIED | no | ~90% |
| TIMING among the 16 switches | some (1–8) | ~60% |

## Grade, to carry forward visibly
This is the third design in a chain:
- v1 registered T-L3 and T-SWITCH were VOID, then amended (§155, NOT ESTABLISHED);
- v2 registered controls were VOID, then amended (§156, VACUOUS);
- v3 is designed after seeing §155/§156 outcomes, but before any v3 code or bisection.

## Resources
- 1 core, nice 10, < 1 GB, per-history checkpoint plus stop guards.
- Step 1 on Kerr is ~15 min. Step 2 is ~3.2 h, which is over 2 h, so that number goes to the Bridge before TS.

## Addendum 1 (2026-11-19, after step 1, BEFORE any TS run)
**Step 1 as registered: FAIL, so STOP (`edge3/step1.json`):**
- **P-log PASS:** slope 0.6256 against 1/log₁₀ λ = 0.6249 (0.1%), with 29 plunging points from n = 2 to 11.
- **K-sep-F PASS:** STRAND, slope 0.497 over 7.5 decades, converged to the closed-form x_h within 7e−18.
- MF-1 and MF-2 PASS: not strand.
- **K-timing FAIL: "F equal at ends".**

**Diagnosis, an off-by-one in the control's parameter (an implementation bug):** in code, F_N = `history(cap=N).fate`.
That is true iff the orbit plunges with lifetime n ≤ N − 1 (it completes at most N − 1 crossings before the plunge).
K-timing set N = the smaller lifetime of the step pair (n = 2 vs 3), so F_2 was false for both members.

**Fix:** keep F_N's definition as coded, since §156's stored window F_300 means the same thing (n ≤ 299). For
K-timing, set N = the smaller lifetime + 1. Nothing else changes. Step 1 is rerun in full under the fixed code. The
window run still waits for a Bridge OK on cost.
