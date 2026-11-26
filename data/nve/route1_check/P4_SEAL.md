# P4 build: design for the Bridge's read, and SEAL of its T-tests (before any run)

**ansatz-machine-personal (Claude Opus), 2026-11-27.** This is the order's item 1: the relative TOL_F, the production
runner and the segment plan for the reach Sumit fixed (spin 3/5 up to k ≈ 3, spin 9/10 up to k ≈ 2, the dyadic
small-k segments included). Nothing has run. The tests run on the Air only after the Bridge's non-author read.

## 0. A feasibility risk, found while building, stated first

**At spin 9/10 the bottom of the dyadic chain is very likely out of reach with the current evaluator, and splitting
cannot fix it.**
- **The cause.** At small k, F = tr(M1 M0 M1⁻¹ M0⁻¹) − 2 cancels down to about c2·k². The Arb evaluator's absolute
  radius of F does not shrink with k. It is set by the Taylor tails accumulated over the walk.
- **3/5 has room.** |c2| ≈ 0.217 (C2_ANALYTIC), so near ε_a = 1.92e−3, |F| ≈ 1e−6, against node radii near 1e−9.
- **9/10 does not.** |c2| ≈ 0.0159, so |F| ≈ 3e−10 near ε_a = 1.06e−4. The 9/10 node radii were up to 7.4e−8 in the
  engine check at k ≈ 1.
- **Estimate (not measured).** On that estimate the 9/10 dyadic chain reaches down only to about k ≈ 1e−2. That would
  leave [1.06e−4, ~1e−2] uncovered at 9/10.
- **Pilot P4-r measures it before anything long runs**: one Arb evaluation per dyadic centre, minutes each.
- **The only fix I see is an evaluator change** (a higher Taylor order or smaller steps), so it falls under "no new
  code mid-run". It is a decision for the Bridge and Sumit, not something I would start. If P4-r confirms the risk,
  "good enough" at 9/10 would have to be [the lowest feasible k, 2], with the gap reported plainly.

## 1. What was built (all at the commit of this file)

| file | what |
|---|---|
| `scripts/_nve_route1_segment_v6.py` | v6 = v5.2 + P4a (relative n target, §5.3) + P4b (F/k² on dyadic segments, §4.2) + P4c (a verdict for a general segment, with §6's per-segment controls) + P4d (the radius-limited flag). v6's own code hash covers v2..v6. |
| `scripts/_nve_route1_engine_gate.py` | the 50-digit engine at every node of a v6 segment: `_nve_route1_engine_nodes.py` generalised from 21/20 |
| `scripts/_nve_route1_production.py` | the driver: segment plan, the four stages per segment, the split and stop rules, resume, the batch rerun, the reach |
| `scripts/_nve_route1_production_test.py` | U5: the driver's logic with simulated stages (10 scenarios; 10/10 PASS on the Mac mini, system Python, no arithmetic) |
| `scripts/_nve_route1_t6.py` | U1, U3, U6 and the gate test, checked from the files |
| `scripts/_nve_route1_radius_probe.py` | P4-r |
| `air/t6a.sh`, `air/t6b.sh`, `air/MANIFEST_P4_*.sha256` | the runners (one per core) and the manifest |

**The mathematics of the proof stage is unchanged.** v6 sets v5's n tolerance per row, and it rebinds v5's code hash
and file names, nothing else.

**P4a, the relative n target.**
- The target is 1e−2 × |F(k_c)|, with F(k_c) from the engine's floats at k_c.
- In Fk2 mode it is 1e−2 × |g(k_c)|. v5's row_for gets the equivalent F tolerance 1e−2 |F(k_c)| ((k_c − R)/k_c)², so its
  n is then n_g.
- n is driven by F (or g) as in v5. The traces get whatever error that n gives them, and the verdict checks it.
- R1_TOLMODE=abs restores v5's absolute 1e−3, for the reproduction test only.

**P4b, F/k² on the dyadic segments.**
- On [x, 2x] with ρ = 4, R = 1.0625x < k_c = 1.5x. So |k| ≥ k_c − R > 0 on the ellipse.
- With d = (k_c − R).lower(): M_g = M_F/d² and e_g = e_F/d², the same ATAP bound divided by d².
- A node value is g = F/k_mid², at the exact point where the node was evaluated, plus the Cauchy term in M_g.

**P4c, the general verdict.** It uses v2's interp() and conditions() unchanged, on the chosen row's n + 1 nodes.
- **Controls on every segment:** the planted zero (must be refused), one held-out point t = 1/8, and two ellipse
  samples (j = 0, 4).
- **On [0.1, 0.2] per spin (R1_FULLCTL):** three held-out points, eight ellipse samples, the shrunken-M control and
  the planted precondition at 4.2.
- **A failed control is an ALARM** (exit 3), and production stops.
- The verdict JSON holds no times, so the batch rerun can be compared byte for byte.

**P4d, radius-limited.** A failed f condition with the largest node radius ≥ 1/10 of the smallest node |f| is marked
radius_limited.

## 2. Design decisions for the read (each a choice, none a soundness question)

1. **One row, ρ = 4, in production**, not registration §5.2's four rows. P3 measured the single-row proof stage. In
   the cost redo, four rows cost about 40% more for at most a few nodes fewer. ρ = 4 also keeps R < k_c on every dyadic
   segment and its halves, which the F/k² bound needs.
2. **Split depth DMAX = 2.** A 0.1-wide segment splits down to 0.025 at most. A segment that still fails stops its
   chain (Sumit's stop rule). This is the time box: one full split costs about 3× a segment.
3. **A radius-limited failure stops its chain at once, without splitting** (§0: splitting cannot cure it). This only
   affects efficiency, and it saves about 9 h per hopeless 9/10 segment.
4. **Order:** first the downward dyadic chain from 0.1 (mode Fk2), then the upward 0.1-wide chain (mode F). The two
   meet at 0.1. A stop in one chain does not stop the other. The reach is the contiguous certified range around 0.1.
5. **Floats per segment:** the engine at each k_c, about 1–1.5 min, which the cost redo left out. A geometry_ok False
   stops the run.
6. **The engine gate runs at the Chebyshev nodes only**, as in §3(b), not at the held-out and ellipse points.
7. **A correctness stop** (any non-zero prove exit, a verdict ALARM, an engine miss, bad floats) is recorded, and a
   rerun refuses to resume it without a decision.

**Open question for the Bridge:** the order says "under the guard with true-memory measurement". Our `job.sh` v2
watches the memory-pressure level and free disk. Is there a newer fleet guard that measures true memory, and where is
it? I have not changed `job.sh`.

## 3. SEAL: the T-tests (Air; core A runs t6a.sh, core B runs t6b.sh)

| test | pass criterion (fixed in `_nve_route1_t6.py` / the runners) | prediction |
|---|---|---|
| U5 (on the Air too) | 10/10 scenarios | PASS, P = 99% |
| P4-r 3/5, k_c 3/1280 and 3/40 | radius/|F| < 1e−2 = feasible | feasible at both, P = 85% (≈ 1e−3 at 3/1280) |
| P4-r 9/10, k_c 3/20480 | as above | **RADIUS-LIMITED** (ratio ≥ 0.1), P = 95% |
| P4-r 9/10, k_c 3/2560 | | radius-limited, P = 80% |
| P4-r 9/10, k_c 3/320 | | not radius-limited (ratio < 0.1), P = 80%; feasible (< 1e−2), P = 50% |
| P4-r 9/10, k_c 3/40 | | feasible, P = 90% |
| U1a–d (v6 = v5.2 on [1, 1.1]) | rows, proof JSON and 24 node values equal; verdict bounds 0.265039275 / 1.993158417 / 2.648820879 | PASS, P = 85%. The one risk: k_c's ball radius differs by about 5e−79 between v5's default and the moved segment (midpoints equal; checked), which could show in a far digit |
| GATE | 13/13 on u1's nodes; exit 2 at node3 of a copy shifted by 1e−6 | PASS, P = 95% |
| U6 | hash differs; F2 refusals in v6's rows and node files; byte-identical rerun with no new evaluation | PASS, P = 95% |
| U3 (F/k² on [1, 1.1]) | certified; derived \|F\| bound ≤ min node \|F\|; tol_F as the formula | PASS, P = 85%; n in 12–16 |
| U4a pilot 3/5 [1/640, 1/320] | the production stages give CERTIFIED | certified, P = 75%; n in 14–24; about 30–45 min |
| U4b pilot 9/10 [1/20, 1/10] | as above | certified, P = 75%; about 3–4 h |

**Wall time:** core A about 3 h, core B about 4 h. Each core is one process at nice 15 under `job.sh`.

**What would surprise me:**
- P4-r calling 9/10 at 3/20480 feasible. My radius model would then be wrong, and the dyadic chain would be cheap.
- Any U1 difference outside the far digits.
- An ALARM in a pilot.
