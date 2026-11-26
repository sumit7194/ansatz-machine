# Route (i): the production cost estimate, re-done from P1 to P3 (registration §5, §7)

**ansatz-machine-personal (Claude Opus), 2026-11-26.** For the Bridge, to take to Sumit with the production question.
Inputs: `P1_RESULT.md`, `P2_RESULT.md`, `P3_RESULT.md`, `AIR_REPRO_9_10.md` (engine nodes). Every measurement below
is from the MacBook Air on the loaded fleet: one process, nice 15, Python 3.13.18, v4 or v5.1. **This replaces the k ≈ 1
table of registration §7**, which was measured on the Mac mini and assumed the constants stay as they are at k ≈ 1.

## 1. Where the method stops (measured, ρ = 4, half-width 1/20, fixed 400 Laurent arcs)

- **It stops at every spin somewhere between k_c 3 and 3.9.** At k_c = 3.9 the Laurent derivative bound is non-finite
  at the centre point. min |1 − kφ| on |x| = 0.81 is about 0.02 there, and the fixed 400 arcs cannot bound
  1/√(1 − kφ). This depends on x = a²ω² only, so it does not depend on the spin. **Splitting segments does not help,
  because it fails at k_c itself.** The engine fails closed there, and the ρ = 4 precondition would have rejected the
  row anyway (max |w| ≈ 1.70 against the limit 1.2346).
- **At 9/10 it stops earlier, between k_c 2 and 3.** At k_c = 3 the circle-side dq bounds over the complex k-square
  (half-side 0.106) grew about 22,000× from k_c = 2. At the centre point they did not grow. M_F's Arb ball passed the
  float range, and the code crashed computing n. That is spin-dependent. Splitting might recover it, because a narrower
  segment means a smaller k-square, but **that is untested**, and it first needs code change C1 below.
- **So with the code as it stands, the top of region A is out of reach at every spin.** That is roughly k ≳ 3 to the
  registered A_top (4 at spins 3/10 and 4/5, 3.85 at 9/10, and at 3/5 the precondition's own ≈ 4.006). At 9/10 the gap
  starts lower. **Neither stop says where the last certifiable segment ends.**

## 2. What P1 to P3 measured, per 0.1-wide segment

| | spin 3/5 | spin 9/10 |
|---|---|---|
| n at ρ = 4 (k_c = 1/2, 21/20, 2, 3) | 14, 14, 14, 20 | 16, 18, 22, none |
| chosen n, 4 rows, k_c = 21/20 | 12 (ρ 6.5; P1 certifies at it) | 18 |
| **proof stage, one row (ρ = 4)** | **472–482 s ≈ 8 min** (P3, k_c 1/2 to 3) | **2,760–3,455 s ≈ 46–58 min** (P3, k_c 1/2 and 2) |
| proof stage, four rows | ≈ 25 min (estimate from P2: 24 min at 3/10, 34 min at 4/5) | ≈ 2.3–2.6 h (estimate: per row 1,870–2,170 s in P3; the Air repro of v4 took 1,082–2,331 s per row) |
| one node (Arb evaluator) | 41 s (P1, 24 evaluations) | **not measured on the Air**; 170 s on the Mac mini, so ≈ 280 s by the 3/5 Air/Mac ratio of 1.6 |
| one node (50-digit engine) | 54 s | 76 s |
| circle walk steps (k_c 1/2 → 3) | 2,165 → 2,164 (flat) | 19,809 → 15,624 → 13,535 (falls with k) |

At 3/10 and 4/5 (P2, k_c = 21/20 only): chosen n 10 and 16, four-row proof stage 24 and 34 min. No k-growth has
been measured at those two spins.

## 3. The estimate (one Air core; nodes = n + 1; engine at every node; 3 control evaluations per segment)

**Per segment:**
- **spin 3/5:** one row 8 + (n+1)(41 + 54) s + 2 min, so **≈ 34 min at n = 14 and ≈ 43 min at n = 20**. Four rows add
  ≈ 17 min.
- **spin 9/10:** one row ≈ 50 min + (n+1)(280 + 76) s + 14 min, so **≈ 2.7 h at n = 16 and ≈ 3.4 h at n = 22**. Four
  rows add ≈ 1.5 h. The node figure is the unmeasured one.

**Per spin, over the measured reach only** (0.1-wide from 0.1; the dyadic small-k segments of §4.2 are not built, P4):

| | segments | one row | four rows | wall time, one core |
|---|---|---|---|---|
| spin 3/5, k ∈ [0.1, 3] | 29 (+ ≈ 6 dyadic) | **≈ 18 h** (+ ≈ 3 h dyadic) | ≈ 26 h | ≈ 1 day |
| spin 9/10, k ∈ [0.1, 2] | 19 (+ ≈ 10 dyadic) | **≈ 55–65 h** (+ ≈ 25 h dyadic) | ≈ 85–95 h | ≈ 3.5 days |
| spins 3/10, 4/5 | unmeasured above k_c = 21/20 | likely between the two rows above | | |

**Beyond the measured reach:** there is no estimate. At 9/10, k ∈ [2, 3] needs C1, then a pilot to see whether the
split rule (§5.4) recovers it and at what width. Each split at least doubles the proof stages over its span. Above
about k = 3, at every spin, it needs C2 and its own pilot.

**Against registration §7:**
- 3/5 is in line with the old ≈ 17 core-h, but over [0.1, 3] instead of the whole region. The Air is slower, and n
  grows with k (14 → 20), so the two roughly cancel the shorter range.
- 9/10 per segment is higher than the old ≈ 1.5–2.3 core-h, at ≈ 2.7–3.4 h, because the Air's nodes are slower. But
  the measured reach is only half of region A.
- On the Mac mini the per-node figures are about 1/1.6 of these, if the Bridge would rather production run there.
  T1's same-machine rule then means T1 to T4 rerun on the Mac mini first.

## 4. Code changes production would need (each needs its own non-author read and a T1–T4 rerun)

- **C1 (needed at any scope): fail closed in the n formula.** `row_for` computes n from `float(MF)`. A runaway but
  finite M_F crashes the runner instead of rejecting the row. That is not unsound (nothing was written), but it ends
  the job, which the no-caps policy forbids, and it hides the case from the split rule. Fix: compute n in Arb, and
  reject a row whose n exceeds 40, the split threshold of §5.4. The change is small and local, and T1 should come out
  identical wherever M_F is moderate.
- **C2 (only if production must reach the top of region A): adaptive Laurent arcs.** Subdivide an arc only where its
  ball for 1 − kφ contains 0, so every number below the stop stays bit-identical and T1 can still pass identically.
  Then a pilot locating the last k_c that passes. The precondition's own crossing (≈ 4.006 at 3/5, §4.1) is still a
  hard limit above it.
- **C3 (already planned): the F/k² dyadic segments** (§4.2, P4). Not built.

## 5. Cheap probes that would sharpen this before production (not run; each needs a go)

1. **Locate the Laurent stop:** `V.laurent(k, deriv=True)` alone at k = 3.1, 3.2, …, 3.8. That is seconds per k on
   the evaluator, no proof stage. It says where the spin-independent stop sits, which sets the top of the reach for
   all four spins with the current code.
2. **Locate the 9/10 walk-side stop:** the 9/10 proof stage at k_c 2.5 (and 2.25 or 2.75 after it), one row, about
   50 min each. It needs C1 first, or it can crash the same way. It says how much of [2, 3] 0.1-wide segments cover.
3. **The split test:** 9/10 at k_c = 3 with half-width 1/40. It also needs C1. If it admits a row, the split rule
   covers the 9/10 gap at a known cost.

## 6. The production question, as I would put it

The design can run now, after C1 only, over the measured reach:
- 3/5 (and likely 3/10 and 4/5) to about k = 3;
- 9/10 to k = 2.

That costs about 1 day of one Air core for 3/5 and about 3.5 days for 9/10, more with the dyadic segments. **It
certifies a lower part of region A, not all of it**, so it would support at most a partial status line (§8), with the
rest of region A numerical. Reaching the top needs C2, the probes and more pilots, and that cost is not estimable yet.
