# Is the TS δ = 2 capture edge on the start line the stable manifold of the §154 orbit? Pre-registration, 2026-11-18, BEFORE any run

**Ask:** Sumit, relayed by the Bridge (2026-11-18): the open "window vs saddle" step, as reasoning → Opus review →
pre-registration → run.
**Reasoning this rests on:** `data/ts_chaos/EDGE_LINK_REASONING.md` v2 (Theorems 1 and 2; hypotheses F-b′, A1, A2,
L2, L3; the Opus review and what it changed are in its §6).
**Model provenance:** design and predictions by Claude Fable 5.2 (`claude-fable-5-2`), session
ansatz-machine-personal. The Opus review of the reasoning changed the designs below before this file was committed
(a redesigned census, a stricter certificate, a must-fail control that can actually fail, a cut-independence check).
**State at registration:** no code for these tests exists, and no orbit or map has been evaluated for them.

## Data seen before registration (disclosure)
- Read: RESULTS §150 and §154 as published; the headline values in `tangle/{kerr,ts}_R2_d1e-12.json` (fixed points,
  multipliers, x_h, angle); the window bounds; the scripts, for definitions. The reviewer also read the tracer's
  stored last rows for the inward branch (all seeds terminated; last x about 1.57).
- NOT read: the lifetime profiles in `bscan_ts45_v2.json`; the samples in `alpha*.json`; anything from the void
  saddle test (its TS data stay sealed); anything of tabula's or the Bridge's.

## Level and definitions (fixed)
- **TS:** `ts2:4/5`, E = 97/100, L = 41/8. **Kerr control:** `ts2kerr:4/5`, E = 97/100, L = 2550268/1000000.
- Section Σ = {y = 0, p_y > 0}, coordinates (x, p_x); start line ℓ = {p_x = 0}.
- **Plunge** = engine status 1 (first x < x_pl, x_pl = 1.5 unless stated). Status 2 (escape) and 3 (step cap) are
  recorded as themselves and are never counted as plunges.
- z\* = (x\*, 0), λ and x_h are taken from `tangle/*_R2_d1e-12.json` at full stored precision. v_u = (a, b) with
  a > 0 (outward) and v_s = (a, −b) are the unit eigenvectors of DP(z\*), recomputed.
- **Eigenframe:** z − z\* = u·v_u + s·v_s. **ρ(z)** = max(|u|, |s|). Distances between section points use the same
  max-norm.
- **Excursion:** the largest x reached between two consecutive crossings exceeds X_far (TS 30, Kerr 15).
- **Lifetime n:** the number of upward crossings completed before the plunge.
- **Rungs:** R2 (tol 1e−28) is primary; R1 (1e−22) is the agreement check.

## Engine
- New script `scripts/_ts_edge.py`. It imports the fixed-point, eigenvector and double-double machinery of
  `scripts/_ts_tangle.py` and `scripts/_hp_dd.py` unchanged.
- It adds one variant of the section routine that also returns the exit status, the largest x since the last
  crossing, takes x_pl as an argument, and can stop at the first **downward** crossing.
- **Engine gate:** the variant must reproduce the stored §154 Kerr fixed point and multiplier to ≤ 1e−20 relative.
- **Order:** every Kerr step is run and read first. TS output goes to files and is not printed until the Kerr gates
  and controls of that test have passed.

## T-L3: is the gate one-way? (tests F-b′, A2, L2, L3)
**Setup.**
- **U** = W^u_out from z\* to h, traced as in §154 (δ = 1e−12) at 400 seeds per fundamental domain, and 3200 per
  domain on the last two domains.
- **F-b′ check:** p_x has one sign on every sample of U before h.
- **D** = the polygon z\* → U → h → R(U) → z\*. A crossing closer than 1e−3 to the polygon is "ambiguous" and takes
  no part in inside/outside decisions.

**Sample orbits (each ≤ 60 crossings).**
- (a) on ℓ inside D: the T-BANDS grid; and x0 = x_h − 10^(−g), g = 1, 1.06, …, 7 (101 points).
- (b) off ℓ: a 31 × 31 box around z\* (±0.3 in x, ±0.3·|b/a| in p_x), keeping the points inside D.
- (c) on ℓ outside D: x0 = x_h + 10^(−g), same g.

**Counters.**
| | counts | link needs |
|---|---|---|
| C0 | start points in D with no next crossing | 0 |
| exits | orbits from (a), (b) that leave cl(D) | ≥ 30 in TS, or the test is VACUOUS |
| C1 re-entry | after leaving cl(D), a later crossing inside D | 0 |
| C2 stall | after leaving cl(D), no plunge within 40 further crossings | 0 |
| C3 odd end | any orbit ending with status 2, 3 or off-shell | reported |
| C4 deep return | a crossing at x < 0.9·x\* followed later by one at x > x\* (no polygon needed) | 0 |
| C5 outside | orbits from (c) that do not plunge within 40 crossings | 0 |
| A2 | 64 seeds across one fundamental domain of W^u_in (δ = 1e−6), ≤ 40 crossings | all end with status 1 |

**Kerr gate (must pass).** F-b′ holds; exits = 0 from (a), (b); C4 = C5 = 0; all 64 inward seeds status 1.
**Must-fail controls (both systems).**
- C4 with a misplaced gate ("inside" x < 2·x\*, "outside" x > 2.5·x\*) must be > 0.
- C1 with the polygon shrunk by a factor 0.5 about its centroid must be > 0.

**Diagnostic, report-only:** the brake check |H(z\*) − z\*|, where H is the half-return map (up-crossing to first
down-crossing). A non-zero value would mean γ has a mirror twin (failure B5/B6 of the reasoning).

## T-SWITCH: are the window's switches strands of W^s(γ)?
**Straddle certificate for a pair (p, q) on ℓ.** All of:
1. There is a crossing index k at which ρ(Pᵏp) ≤ 1e−2 and ρ(Pᵏq) ≤ 1e−2.
2. The segment is intact and short up to k: both ends and 7 equally spaced interior points are alive at every
   crossing j ≤ k, and at every such j all 9 images lie within 1e−6 of one another.
3. Opposite exits: at its first crossing after k with ρ > 1e−2 (or its last crossing), p has u < 0 and q has u > 0.
   Then p plunges with no further excursion, and q makes an excursion.
4. Items 1–3 hold at R1 as well, with the same k.

**Source and stopping rule.** The stored TS samples of `data/ts_chaos/alpha.json`, in stored (seeded random) order. A
candidate pair is (x0, x0 − 3e−5), then (x0, x0 + 3e−5), wherever the two stored statuses differ. Stop at **8
accepted or 60 examined**, whichever comes first.

**Acceptance (R2, ≤ 120 crossings).** Exactly one member ("a") plunges, with n_a ≤ 60, and the other has not plunged
by crossing n_a + 24. Every rejection is logged with its reason. The acceptance rate is reported: it is the scope of
the test.

**Bisection.** On Π(x) = "plunges with n ≤ n_a + 12". The certificate is tried after 25 halvings (width ≤ 1e−12) and
then after every 5 more, down to width ≤ 1e−18.

**Classes.**
- **H** — the certificate holds at some stage.
- **A** — both final members plunge and their lifetimes differ by ≤ 2 (a smooth lifetime step).
- **O** — the fates differ; at the last crossing where p and q are still within 1e−6 of each other, and at the 8
  crossings before it, both have ρ > 1e−2; and R1 and R2 agree on both lifetimes. **A discontinuity that γ does not
  own.**
- **U** — anything else (precision ran out, or the segment never became short).

**Cut independence.** For every H pair, the final (p, q) are re-run with x_pl = 1.3 and x_pl = 1.7. The fates must
not change.

**Controls, run first. If any fails, T-SWITCH is VOID.**
| control | what | must give |
|---|---|---|
| K-x_h | closed-form Kerr x_h (double root of R, then Vieta) against the stored §154 crossing | agreement ≤ 1e−18 |
| K-H | Kerr pair (x_h + 1e−5, x_h − 2e−5), same procedure | H; closed-form x_h inside the final bracket; cut-independent |
| K-O | Kerr with the plunge cut **raised** to the midpoint between x\* and the stable spherical orbit; the fate flip on ℓ between that orbit and x_h, found by scan then bisection | **O** (orbits graze the cut; γ does not own this boundary) |
| K-A | a Kerr one-whirl lifetime step outside x_h, found by bisection on "n ≤ n₀" | A |
| T-H | TS pair (x_h + 1e−12, x_h − 1e−12) around §154's x_h (same engine, different procedure) | the certificate |

## T-BANDS: engine and Theorem-1 check (not part of the falsification verdict)
- Start points x0 = x\* + d_j, d_j = 0.14·λ^(−j/96), j = 0 … 372 (down to d ≈ 1e−7); λ is the system's own.
- **First-return fate:** T = plunges after exactly one excursion; B = starts a second excursion; X = anything else.
- Statistics on the deep range d ≤ 1e−2 (j ≥ 70): the T-fraction; the agreement A(τ) between the fate sequence and
  itself shifted by τ grid steps, τ = 60 … 140.
- Edges: every fate change in the two deepest full periods (at most 8) is bisected in d to relative width 1e−10,
  tested with the straddle certificate, and the ratio of each edge to the matching edge one period deeper is formed.
- **As predicted means:** T-fraction in [0.1, 0.9]; the best τ in [93, 99]; A(96) ≥ 0.9; edge ratios within 0.5% of
  λ; at least 4 edges certified.
- **Kerr gate:** zero T and zero X on the whole grid. **VOID** if more than 2% of TS points are X.

## Verdict rule (for this (E, L) level only)
- **VOID** (per test) if its engine gate, Kerr gate or a control fails.
- **VACUOUS** for T-L3 if fewer than 30 TS exits were observed.
- **LINK FALSIFIED** if, in TS and agreeing at R1 and R2: C1, C2, C4 or C5 > 0; or any class-O switch; or an H
  switch that changes fate with the cut. (A2 failing falsifies Theorem 1's hypothesis instead, and is reported as
  that.)
- **LINK SUPPORTED on the sample** if nothing is VOID or VACUOUS and, in TS: F-b′ holds; C0 = C1 = C2 = C4 = C5 = 0;
  all 64 inward seeds end with status 1; T-SWITCH has at least 3 H, no O, and every H is cut-independent.
  - The extra sentence "a Cantor set of edge points lies inside the §150 window" then needs only one of those H
    switches (reasoning W-2).
  - The sentence "a Cantor set of edge points accumulates on x\*" needs A2 and T-BANDS as predicted.
- **NOT ESTABLISHED** otherwise (for example F-b′ fails, so D must be rebuilt; or all switches come out U or A).
- No outcome licenses a statement about α at any horizon, about other levels, or about EMRIs. Everything is
  numerical, not rigorous, and "supported" means on the sampled orbits.

## Predictions (sealed by this commit)
| item | prediction | confidence |
|---|---|---|
| engine gate, Kerr gates and all five T-SWITCH controls behave | yes | ~75% (new code; K-O is new) |
| K-x_h: closed form equals the traced crossing to ≤ 1e−18 | yes | ~85% |
| F-b′ holds in TS | yes | ~90% |
| A2: all 64 TS inward seeds end with status 1 | yes | ~85% |
| TS exits ≥ 30 | yes | ~85% |
| C1 = C2 = C4 = C5 = 0 in TS | yes | ~75% (TS has no horizon; the inner region is the main risk) |
| brake diagnostic: γ is a brake orbit in TS | yes | ~90% |
| T-BANDS: both fates present, T-fraction in [0.1, 0.9] | yes | ~80% |
| T-BANDS: best τ in [93, 99], A(96) ≥ 0.9, edge ratios within 0.5% of λ | yes | ~70% |
| T-BANDS: exactly 2 fate changes per period | yes | ~60% |
| T-SWITCH: acceptance rate | 20–70% of examined pairs | ~55% |
| T-SWITCH: at least 3 H | yes | ~60% |
| T-SWITCH: any O | no | ~85% |
| T-SWITCH: every H is cut-independent | yes | ~85% |
| Overall verdict | LINK SUPPORTED on the sample | ~45% |

## Blinding and resources
- A new embargo `ansatz-edge-link-ts` is added to `tools/EMBARGOES.json` in the same commit as this file. Band edges,
  strand positions, counter values and class counts of the TS runs go to nobody until the Bridge arranges it.
  Verdict words and seals may be sent.
- Three runs (T-L3, T-BANDS, T-SWITCH), each a single process, 1 thread, nice 10, detached with a log under
  `data/ts_chaos/edge/`, PID recorded in `data/ts_chaos/PIDS`. Cost is measured on Kerr first. Expected: under
  30 minutes each, under 1 GB, under 10 MB of disk. If a measurement predicts more than 30 minutes, a slot request
  goes to the Bridge before that run starts. Stop if free disk falls below 5 GB.

## Addendum 1 (2026-11-18, ansatz-machine session, Opus 5.5; after the Kerr T-L3 run, BEFORE any TS T-L3 run)
**Engine gate: PASS** (`data/ts_chaos/edge/engine_gate.json`). The new section routine is bit-identical to §154's for
Kerr and TS: fixed point, multiplier and one step all agree to 0. Deviation, recorded: the stored multiplier is a
double, so "≤ 1e−20 against stored" was checked as ≤ 1e−20 against the §154 routine recomputed (agreement 0), plus
5e−16 against the stored double.

**Kerr T-L3 (R2, `tl3_kerr_R2.json`):**
- F-b′ holds (7,496 samples, one sign).
- C0 = 0, exits = 0, C1 = C2 = C3 = C4 = C5 = 0.
- All 64 inward seeds end with status 1.
- Brake: |H(z\*) − z\*| = 2e−27.
- Must-fail C4 (misplaced gate) = 683 > 0: it fires, as it must.
- **Must-fail C1 (polygon shrunk ×0.5) = 0: it did NOT fire.** So by the registered rule, **T-L3 as registered is
  VOID.**

**Diagnosis (Kerr only):** every start point the design specifies hugs the separatrix. The T-BANDS grid sits within
0.14 of x\*; the x_h − 10^(−g) points sit within 0.1 of x_h; the box is a thin wedge at z\*. In Kerr these orbits
stay on invariant curves next to ∂D. That is why 34,074 of the ~41,600 crossings were "ambiguous" (within 1e−3 of the
polygon), and why no orbit ever came inside the half-size polygon. The control could not fire for lack of interior
orbits, not because the C1 detector is broken. The same feature would make TS exits harder to see; the VACUOUS guard
(≥ 30 exits) covers that.

**T-L3′ (a new verdict; the registered T-L3 stays VOID):** identical to T-L3, plus one sample group:
- **(m)** 60 points on ℓ, uniform in x over [x\* + 0.2, x_h − 0.2], counted with (a) in every counter.
- Same gates: the Kerr gate now also requires must-fail C1 > 0. Nothing else changes.

Cost measured on Kerr: 786 s (71,182 map calls). TS maps are about 4× dearer, so TS T-L3′ is estimated at ~1 h, which
needs a slot request.
- **Kerr T-L3′ result (`tl3_kerr_R2.json`): the Kerr gate PASSES.** F-b′ holds; exits = 0; C0–C5 = 0; all 64 inward
  seeds give status 1; must-fail C4 = 704 > 0; **must-fail C1 = 51 > 0**. Time 846 s. Next: TS T-L3′ at R2 (~1 h,
  slot requested). R1 runs only if a falsifying counter is non-zero, because the rule needs R1/R2 agreement only to
  falsify.
- **TS T-L3′ (R2, `tl3_ts_R2.json`; graded "post-failure amendment, blind to TS"): PASS, NOT VACUOUS.** F-b′ holds
  (8,467 samples, one sign); exits = 439 (≥ 30); C0 = C1 = C2 = C3 = C4 = C5 = 0; all 64 inward seeds give status 1
  (A2 holds); must-fail C4 = 620 > 0 and C1 = 52 > 0; brake diagnostic 6e−27 (γ is a brake orbit). No falsifying
  counter is non-zero, so no R1 run is needed. Time 4,033 s (56,590 map calls).
