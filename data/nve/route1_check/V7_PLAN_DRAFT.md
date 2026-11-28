# v7 plan: interval certificates for the top of the twist range. DRAFT for Sumit, via the Bridge; NOT started

**Office ansatz-machine (Claude Opus), 2026-11-28.** This is registration-ready: if Sumit says go, it becomes a §5B
amendment to `docs/ROUTE1_REGISTRATION.md`, with seals per stage. Nothing here has been built or run.

**Inputs:**
- Neon's card-1 answer and follow-up (UNVERIFIED there, graded here);
- my grade of it;
- the closure check (`CLOSURE_STOPC_RESULT.md`, which supersedes the predictions in `CLOSURE_STOPC_SEAL.md`);
- the stop-(c) scan (§6: no singularity found);
- the four running or finished productions.

## 1. Where things stand, and what v7 would add

| piece of (0, 30/7] at each tested spin | how it is covered now |
|---|---|
| (0, ε_a] | Statement A: rigorous relative to the applicability chain |
| [ε_a, small-k floor] | numerical only. The gaps are none at 3/5 and 4/5; [2.79e−3, 3.13e−3] at 3/10; [1.06e−4, 1/80] at 9/10 |
| [floor, 3] ([floor, 2] at 9/10) | route (i) production. 3/5 is done and checked; 3/10 finishes today; 4/5 and 9/10 finish about 11-29 |
| [3, 30/7 − δ0] ([2, ...] at 9/10) | **numerical only** (50-digit argument-principle counts). **v7's target** |
| (30/7 − δ0, 30/7] and the endpoint | interval-certified (δ0 = 7.4e−15, 1.37e−11, 2.4e−10, 3.6e−10) |

## 2. The value gate (fleet rule 1)

- **What it decides.** If v7 certifies its target at a spin, then every real k in (0, 30/7] at that spin is covered by
  interval arithmetic, except that spin's small-k gap. The coverage is relative to the same applicability chain as
  Statement A. That would let the claim's status line change **in kind** at that spin, from "a numerical result" to
  "a computer-assisted proof, relative to the chain, apart from [gap]".
  - At 3/5 and 4/5 there is no gap, so the statement would be whole.
  - At 3/10 and 9/10 the small-k gaps would remain (a separate item, §7).
  - If v7 fails, the claim stays as it is, and we learn which piece of the top resists.
  - **No other planned work changes the claim's grade.**
- **Cost.**
  - **Development:** about 3–5 working sessions plus a non-author read. Outside view ×1.5: **5–8 sessions, about
    1–2 weeks of calendar time** (Neon independently says 1–2 weeks).
  - **Compute:** per spin, the circle segments from 3 to the A/B switch (about 10, 0.1 wide), region-B segments from
    the switch to about 4.2 (about 3), then a dyadic chain in 30/7 − k down to δ0. The traces are not analytic at
    30/7 (§3e), so the chain is needed. It has 44, 33, 29 and 28 segments at 3/10, 3/5, 4/5 and 9/10, so about 57, 46,
    42 and 41 segments in all.
  - At today's per-segment costs on the Air (3/10 about 20–25 min, 3/5 about 30–35 min, 4/5 about 1–2 h, 9/10 about
    2.8 h), that is **about 20, 25, 60 and 115 core-h**. 9/10 also needs [2, 3], about 10 more segments or 30 core-h,
    depending on stop (c) (§6).
  - **Total about 250 core-h; outside view ×1.5, about 375 core-h.**
  - Our route-(i) record ran at 0.6–1.0× its estimates, but the region-B evaluator is new, so ×1.5 stands.
  - That is over 3 days of machine time, so it goes to Sumit (rule 1).
  - **Machine:** the Air is reserved for AlphaMate. This needs an allocation from the Bridge: the Mac mini at night,
    or the Air after AlphaMate.
- **Premortem.** "If wasted, most likely because region B's Arb port gives enclosures too wide to certify near
  30/7. The 220–300-term series centred at Z0 with ratio 0.6–0.7 loses about one digit per 7 terms of tail, and the
  dyadic chain needs the M bound on ellipses that shrink toward the k = 30/7 branch point."
  - It can be checked cheaply first. Stage P-B below is a single-node enclosure at k = 4.2 and k = 30/7 − 10⁻⁶, before
    any production.
- **Dependencies, none of them yet shown to work:**
  - the new c0 evaluator;
  - the region-B port;
  - the complex-k quadrature for c0, which the M bound needs on the ellipse;
  - each is a stage below, and each gates the next.

## 3. The route

- **(a) c0 without the Laurent series.**
  - c0' and c0 are carried along every loop as ODE states (dc0'/dz = c0'', dc0/dz = c0').
  - c0'' = −√(8/5)·a³·√B(z²/a², k)/(z² + a²)³, with √B continued by continuity.
  - The starting constants are c0'(z_s) = −∫_{z_s}^∞ c0'' and c0(z_s) = ∫_{z_s}^∞ (t − z_s) c0''(t) dt along the real
    axis. The integrand is singularity-free there for every k in (0, 30/7), and also for the complex k of the
    ellipses: a stage-V1 geometric check, since B(u², k) ≠ 0 for real u is needed on each k-ellipse.
  - Arb's rigorous quadrature is used up to a cutoff U, with an explicit tail bound from c0'' = O(u⁻⁴) beyond it.
  - This is region B's own normalisation (`_nve_lower_hp`), which equals the Laurent C[0] = C[1] = 0 convention.
  - **This removes stops (a) and (b) by construction.** It also removes the common-mode risk of registration §3(b),
    since the Laurent formula is no longer shared with the engine.
- **(b) Loops, by the closure check (answer CLOSES).**
  - The region-A circle |z| = R0 and its capsule lasso are used up to the A/B switch at k_AB ≤ 4.0. The circle closes
    up to k_cross = 4.02–4.2 by spin, so there is margin.
  - Region B's capsule lasso and Γ disc are used above the switch, inside |z − Z0| ≤ ratio·R_c, where closure is
    automatic.
  - Each segment's k-ellipse gets the same geometric guards, for every complex k in it.
- **(c) Conditions:** F ≠ 0, tr M0 ≠ 0 (or tr Γ, tr M1Γ in region B as registered) and **P_fin(tr M1) ≠ 0** in place
  of tr M1 ∉ [−2, 2]. These are the region A/B counts' own conditions, and the logic was graded sound. This needs the
  §5B amendment.
- **(d) Certification:** unchanged in kind. That means Chebyshev interpolation of Arb node values, plus a proved M on
  a ρ-ellipse (the Dyson bound), plus ATAP, with the engine gate at every node.
- **(e) Near 30/7:** c0 has an ε^{3/2} term and c0' an ε² log ε term (ε = 30/7 − k; my scaling argument). So the
  traces have a branch point at k = 30/7.
  - Segments [30/7 − 2d, 30/7 − d] are dyadic down to δ0, where they meet the existing sliver certificate. Each
    ellipse must exclude 30/7, as the k = 0 chain excludes 0 (ρ ≤ 5).
  - Exact controls: c0'' is rational at k = 4 (B = 6(w + 1)²) and at k = 0 (B = 10(3w − 1)²). The new evaluator must
    reproduce c0 there: closed forms −4u/(u² + 1)² at k = 0, and the atan form at 4.

## 4. Stages, each with its own seal (kill criteria: a state AND a date; dates count from the go, day 0)

| stage | what | good enough | stop |
|---|---|---|---|
| V1 | the new c0 evaluator (Arb) and the same in the 50-digit engine | exact controls at k = 0 and 4 reproduced to 40 digits; agreement inside enclosures with the Laurent evaluator at 20 points on [1, 3.7], at two spins; B ≠ 0 on the real u-axis certified for the ellipses used | not met by **day 7** → stop, report |
| V2 | non-author read of V1, then T1–T4 reruns at one existing certified segment ([1, 1.1] at 3/5) with v7 replacing c0 | T1–T4 pass; same verdict, with bounds no worse than 2× | not met by **day 10** → stop |
| P-B | region-B Arb port; single-node enclosures at k = 4.2 and 30/7 − 10⁻⁶ at 3/5 (premortem check) | node radius ≤ 10⁻³ × \|F\| at both | not met by **day 14** → stop, and bring a fresh plan (e.g. a finer centre grid) |
| P | three pilot segments at 3/5: circle at k_c = 3.95, region B at 4.15, dyadic at 30/7 − 1.5·10⁻³ | all three certify | none certifies by **day 17** → stop; 1–2 → report and re-gate |
| Prod | the top at all four spins (9/10's [2, 3] per §6) | each spin certified over [3, 30/7 − δ0] (9/10 [2, ...]), and any uncovered piece stated | per spin: not at k = 4 by start + its central estimate × 2 → re-gate; whole run over 375 core-h → re-gate |

**Headline odds (my own, for the gate):**
- V1 passes: 75%;
- P-B passes: 55%;
- all three pilots certify: 45%;
- the top is certified at 3/5 and 3/10: 40%;
- at all four spins: 25%.

## 5. What it does not do
- It does not touch the small-k gaps at 3/10 and 9/10 (§7).
- It does not make anything public. The claim text changes only by a new claim version, on Sumit's go.
- It does not cover spins other than the four tested, or E ≠ 4/5.

## 6. Stop (c) at 9/10: the scan result (`CLOSURE_STOPC_RESULT.md` §2)
- **No singularity found.** On the route-(i) k-squares at k_c = 2, 2.5 and 3:
  - no singular point of the ρ-equation comes within 0.35 of the circle;
  - no point other than the lasso's own enclosed p+ comes within 0.12 of the lasso;
  - no extra zeros appear;
  - c0's branch points stay at |w| ≤ 0.56, against the 1.23 limit.
- So the 22,000× growth of the walk-side bounds is an enclosure or cost effect, not geometry. Its cause is open.
- **Plan consequence:** 9/10's [2, 3] is not blocked in principle.
  - A cheap discriminator (about 2 core-h) settles whether a narrower segment fixes it inside v6: a v6 prove-only stage
    at k_c = 2.5, at half-width 1/20 and at 1/40, printing the dq attribution.
  - If it does, 9/10 [2, 3] is about 10–20 segments of v6 (about 30–60 core-h), and v7 starts at 3 at every spin.
  - If not, 9/10 [2, 3] joins v7, with the new evaluator's own bounds.
  - Either way it needs a machine allocation from the Bridge.
- **Machine time:** add about 30–60 core-h at 9/10 to §2's total. The outside-view total stays about 375–450 core-h.

## 7. Separate item, not in v7: the small-k gaps
The floor is the Arb evaluator's own node radius against |F| ≈ |c2|k². Closing [2.79e−3, 3.13e−3] at 3/10 and
[1.06e−4, 1/80] at 9/10 would need tighter node enclosures (higher working precision in the walk, or a centred form
in k). That is its own small study. It decides whether 3/10 and 9/10 can join a whole-range statement.
