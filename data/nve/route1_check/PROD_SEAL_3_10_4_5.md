# Route (i) production at spins 3/10 and 4/5: top-check result, the SEAL for 3/10, and 4/5 held for a re-gate

**Office ansatz-machine (Claude Opus), 2026-11-27.** Owner of `~/GitHub/ansatz-air` since this afternoon.
**Scope (Sumit, "yes go ahead with both spins", via the Bridge):**
- 3/10 on [ε_a, 3] and 4/5 on [ε_a, 3], with ε_a from claim v3.1;
- the top of region A parked;
- any small-k gap reported plainly.

**Code:** v6, the engine gate and the driver, byte-identical to `MANIFEST_PROD` (the 3/5 and 9/10 productions). The
runners differ from `prod_3_5.sh` only in spin, R0 and ε_a.

## 1. The top-of-reach check: result (seal in `P4R_3_10_4_5_RESULT.md`, at 2f1ff69)
Both runs were v6 prove-only on [29/10, 3] (k_c 59/20), with the driver's settings, launched 14:46:32. Outputs are in
`air_top_3_10_4_5/`, with hashes equal to the Air's copies.

| | 3/10 | 4/5 |
|---|---|---|
| floats at 59/20 | geo True, 29 s | geo True, about 2.4 min |
| walks (circle/lasso) | 1937 / 694 | 2502 / 728 |
| row at ρ = 4 | admissible: M_F ≤ 3.47e8, **n = 18** | admissible: M_F ≤ 1.93e21, **n = 38** |
| F1 checks | 8828 step + 68406 series, none fired | 14485 + 82530, none fired |
| prove time, peak rss | 408 s, 33 MB | 508 s, 35 MB |

| prediction | outcome |
|---|---|
| 3/10: admissible row, n in [12, 24] (75%) | n = 18: **HIT** |
| 4/5: admissible row, n in [14, 30] (60%) | admissible, but n = 38: **MISS** (high) |
| 4/5: no admissible row (25%) | did not happen |
| F1 never fires, rc 0 (95%) | **HIT** |
| wall time 3/10 5–15 min, 4/5 8–25 min | 7.5 and 11 min: **HIT** |
| peak footprint < 150 MB | **HIT** |

**Reading:**
- There is no walk-side stop below k = 3 at either spin, so the Bridge's launch condition is met.
- But at 4/5, n rises from 16 (k ≈ 1, P2) to 38 at the top. That is just under the driver's n > 40 rejection, beyond
  which a segment is split. Near the top, 4/5 segments are therefore about 2.5× as costly as near k = 1, and some may
  split. **That changes the 4/5 cost by more than 2×** (§3), so 4/5 is re-gated before launch. 3/10 is on its estimate.

## 2. SEAL: production at spin 3/10 (launches with this commit)

**Gate paragraph (fleet practice 2026-11-27, rule 1):**
- **What it decides:** whether the route-(i) status line can say "certified over [near ε_a, 3] at all four tested
  spins" (a uniform partial result) rather than at two or three of them. This changes the wording of the claim's
  route-(i) line and of the v1.x notes.
- **Cost, from the pilots:**
  - per node: 46 s (Arb) and 34 s (engine);
  - per prove: about 6–7 min;
  - n rises from 10 (k ≈ 1) to 18 (k = 3);
  - so about 20–30 min per segment, over 6 dyadic + 29 = 35 segments: **about 15 h**.
- **Outside view:** our own route-(i) record so far ran at 0.6–1.0× its sealed estimates (the 9/10 verdict 1.42 h
  against 1.5–2.5; 3/5 production pacing at about 15 h against 18–30). The fleet's worst case (kerr_e, ×10 and more)
  is a different reference class: unbounded covering growth, whereas our segment count is fixed. ×1.5 is used: **about
  23 h**.
- **Premortem:** "If wasted, most likely because the top segments needed splits that multiplied the cost." Checked
  first: n = 18 at the top, far from 40.
- **Dependencies:** v6 was tested at 3/5 and 9/10. Its first run at 3/10 is the top check above, and it ran clean.
- **Good enough:** certified from the lowest reachable dyadic end up to 3, with any bottom gap stated.
- **Stop:**
  - if by **2026-11-28 18:00** the upward chain has not reached k = 2, stop and bring a short plan to the Bridge and
    Sumit;
  - any ALARM or engine miss stops the run for a decision (the driver does this).
- **25% check-in:** at **2026-11-27 19:00** (about 4 h in). If the projection then exceeds 30 h (2× the estimate),
  re-gate.

**What runs:**
- `air/prod_3_10.sh`: NVE_SPIN=3/10, R1_R0=1.1492, PROD_TOP=3, PROD_EPS=2.79e−3, PROD_DMAX=2.
- One Air core, nice 15, under `job.sh`, with `fp.sh`.
- Manifest `MANIFEST_PROD_3_10.sha256`.
- It reuses the top check's checkpoint for [29/10, 3] and the P4-r floats entries.

**Predictions:**

| | prediction | P |
|---|---|---|
| no ALARM, engine miss or gate stop | holds | 90% |
| the downward chain stops radius-limited at [1/640, 1/320]; reach [1/320, 3]; **gap [2.79e−3, 3.13e−3]** above Statement A | holds | 60% |
| the downward chain certifies to the bottom (no gap) | — | 25% |
| the downward chain stops higher than [1/640, 1/320] | — | 15% |
| upward chain completes to 3 with 0–2 splits | holds | 80% |
| n on the upward chain within [10, 20] on every segment | holds | 80% |
| batch rerun byte-identical, full controls passed per mode | holds | 95% |
| wall time | 11–25 h | 70% |
| peak footprint < 150 MB | holds | 95% |

## 3. Spin 4/5: re-gate (NOT launched with this commit)
- **The cost, revised by the top check:**
  - per node: 55 s (Arb) and about 150 s (engine);
  - per prove: about 8–9 min;
  - n rises from about 16 to 38;
  - so per segment about 1 h near k = 1 and about 2.4 h near k = 3;
  - over 7 dyadic + 29 segments, with an average n of about 25, **about 45–55 h**, against 25–35 h in my proposal.
  - Outside view ×1.5: **about 70–80 h, over 3 days**, which by rule 1 goes to Sumit.
- **Extra risk:** segments near the top may exceed n = 40 and split. Each split roughly doubles that span's cost, but
  halves its width, which lowers n.
- **The expected small-k gap is unchanged:** full reach, or [1/640, 3] with gap [8.39e−4, 1.56e−3].
- **Options for Sumit:**
  - (a) launch 4/5 on [ε_a, 3] at the revised cost;
  - (b) launch 4/5 on [ε_a, 2], about 25–30 h, and leave [2, 3] for later;
  - (c) hold 4/5.

  The runner `air/prod_4_5.sh` is committed but not deployed. Its seal follows the decision.
