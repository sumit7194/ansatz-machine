# Campaign results — the conjecture machine's first runs

*Lab-notebook record (2026-06-10). Same honesty rules as `echoes/`: failures are
recorded, fixes are bought by measured failures, null results are results.*

---

## TL;DR

The full loop — **PROPOSE** (genetic programming, exact-rational expression
trees) → **REDUCE** (SymPy, ansatz → ODE residuals) → **VERIFY** (numeric
spot-check → symbolic proof) → **NOVELTY** (invariant-curve fingerprint) →
**EVOLVE** — works end to end. Six rungs across the dimensional ladder,
**80.5 s total**, all verdicts correct:

| Rung | Found f(r) | Verify | Novelty verdict | Gen | Time |
|---|---|---|---|---|---|
| A. 3+1, Λ=0 | `(r + 9/4)/r` | ✅ theorem | KNOWN: Schwarzschild, M̂=−1.125 | 2 | 2.8 s |
| B. 2+1, Λ=−1 | `r² + 3/40` | ✅ theorem | BLIND_SPOT (CSI) — see below | 0 | 0.5 s |
| C. 4+1, Λ=0 | `1 + 4/(3r²)` | ✅ theorem | KNOWN: Tangherlini, μ̂=−4/3 | 2 | 3.0 s |
| D. 3+1, Λ=3/4 | `1 + 1/r − r²/4` | ✅ theorem | KNOWN: Schwarzschild–de Sitter, M̂=−0.5 | 23 | 28.6 s |
| E. 5+1, Λ=0 | `1 − 375/(32r³)` | ✅ theorem | **CANDIDATE_NEW** → escalate | 5 | 11.8 s |
| F. 4+1, Λ=−1 | `r²/6 + 1 − 2/(3r²)` | ✅ theorem | **CANDIDATE_NEW** → escalate | 51 | 33.9 s |

Rungs A–D are the injection test: the machine, never told any solution,
re-derived GR's greatest hits from random expression trees and recognized them.
Rungs E–F were aimed deliberately **outside the fingerprint catalog**, and the
machine did exactly the right thing: verified the solutions to theorem level,
found no catalog match, and escalated to the human.

**Honesty box:** E is the 6D Schwarzschild–Tangherlini black hole (μ = 375/32)
and F is the 5D Tangherlini–AdS black hole (μ = 2/3, ℓ² = 6) — both *known to
the literature*, both new to the machine's catalog. What was demonstrated is the
**discovery pathway**, not a new theorem about nature. Aiming at genuinely
unmined ansatz families (two-function metrics, rotating rational forms,
modified-gravity field equations) is the next phase, and it runs on exactly
this machinery.

---

## What the machine found that we didn't ask for

**1. It discovered flat space, then the de Sitter ground state — the same
lesson twice.** In campaign v1, rung A's generation-0 "discovery" was `f ≡ 1`
(Minkowski: solves vacuum perfectly, discovers nothing), and rung D's was
`f = 1 − r²/4` (pure de Sitter — the vacuum ground state of that Λ, same
laziness one level up). The general fix: the maximally-symmetric member of
every (n, Λ) family is `f = 1 − 2Λr²/((n−1)(n−2))`, computable in advance;
fitness now penalizes candidates sitting on it, and promotion rejects
constant-invariant hits when hunting mass. *A verifier defines what counts as
a solution; only a novelty layer defines what counts as a discovery.*

**2. The equations don't share our taste in mass.** On every unconstrained
rung the GP's first exact hit had **negative mass** (`f = 1 + 9/(4r)` etc.) —
naked-singularity branches, exact vacuum all the same. Plausible reason (flagged
as hypothesis, not measured): negative-mass f has no horizon zero near the
sample radii, so the fitness landscape is smoother there. The fingerprint
matches the signed branch and reports it (M̂ = −1.125, μ̂ = −4/3, M̂ = −0.5).
Interestingly, on the two uncatalogued rungs the machine delivered
**positive-mass black holes** — E and F have genuine horizons.

**3. The 2+1 rung graded its own ladder.** Rung B's verdict is permanently
BLIND_SPOT, and that is *correct physics*, not a tool limitation you can fix:
2+1 gravity has no local degrees of freedom, every Λ<0 vacuum is locally AdS₃,
and BTZ differs from `f = r² + 3/40` only **globally** (quotient
identification — a black hole made of topology). No local invariant can ever
tell them apart. The dimensional ladder's "⚠️ degenerate" verdict for Flatland
gravity, rediscovered by a machine in 0.5 seconds.

---

## Fixes bought by measured failures (campaign v1 → v2)

| Failure (measured) | Fix |
|---|---|
| Kerr blanket-simplify ran >12 CPU-min, never finished | Verify the **Ricci form** `R_ab = 2Λ/(n−2)·g_ab` (equivalent for n>2, much smaller) |
| Kerr in Boyer–Lindquist: 500 s → UNPROVEN (sin 6θ swamps; numerically vacuum to 10⁻¹³²) | **u = cos θ** substitution → all components rational → zero-testing decidable → **VERIFIED in 9 s** |
| Loop "discovered" Minkowski, then pure de Sitter | Vacuum-ground-state penalty + CSI rejection at promotion (except 2+1, where CSI is the result) |
| Fingerprint missed Schwarzschild-in-PG-coordinates | nsolve absolute tolerance vs ~10⁻⁸ invariant values → **ratio-form equations** + explicit tol |
| Fingerprint missed the negative-μ Tangherlini branch | Hand-picked Newton starts → **data-driven starts** (signed log-grid over the parameter; 1D bisection onto the K-surface) |
| Fingerprint missed SdS: at sampled radii the mass term is a 10⁻⁵ ripple on the Λ floor of K | **Variation-aware sampling** — sample the invariant curve where it varies, deterministically |
| One GP seed stagnated 140 generations (2200 s) at residual 6.8×10⁻⁴ | **Stagnation cutoff** (30 flat generations → restart with fresh seed); campaign time 2300 s → 80 s |

Every one of these is now a regression test: `01_verifier.py --kerr`,
`02_fingerprints.py`, `03_rediscover.py`, `04_campaign.py` all end with an
ALL-EXPECTATIONS-MET / PASSED gate, in both directions (knowns must pass,
sabotage must fail, costumes must be unmasked, blind spots must be declared).

---

## Where this leaves the risk profile

- The static one-function ansatz is now **strip-mined by us too** — within it,
  the machine finds everything that exists in minutes. This was the point: the
  ansatz was the training ground, not the target.
- The machinery that survives contact with harder targets: the three-valued
  verifier (rational-coordinates rule), the fingerprint filter with declared
  blind spots, the triviality ladder (flat → ground-state → known), the
  stagnation-restart evolutionary harness.
- Next targets, in order of reach: **two-function ansatz** `−f(r)dt² +
  dr²/h(r) + r²dΩ²` (where f≠h lives e.g. interior solutions and many modified-
  gravity black holes); **stationary rational forms** (the Kerr lesson says
  off-diagonal is fine if rational); **catalog growth** (every confirmed find
  gets generalized to a symbolic family and added — the catalog is the
  machine's memory); **modified-gravity REDUCE** (the EdGB metric, known only
  numerically since 1996, as the marquee genre-(c) target).

---

# v2 (2026-06-11): memory + the bigger hall

v1's two declared caveats — no memory, one-function room — are closed.

## 05 — catalog auto-growth (the machine's memory)

`05_generalize.py` takes a confirmed find and tests each numeric constant
against the full symbolic verifier: replace it with a symbol, re-prove. The
machine sorted hair from law autonomously:

| v1 find | constant | verdict |
|---|---|---|
| `1 − (375/32)/r³` (6D) | `1` | structural — fixed by field equations |
| | `375/32` | **free** → family `1 − c₁/r³`, proved for all c₁ |
| `r²/6 + 1 − (2/3)/r²` (5D AdS) | `1/6` | structural — it IS the Λ=−1 coefficient |
| | `1` | structural |
| | `2/3` | **free** → family `r²/6 + 1 − c₁/r²` |

Families are theorems (verified with the parameter symbolic), persisted to
`catalog_discoveries.json`, loaded by every future `build_catalog()` call.
Memory test: both original numeric finds re-classify as KNOWN_LIKELY with the
correct parameter recovered (c₁ ≈ −11.7187 = −375/32; c₁ ≈ −2/3). The 04
campaign deliberately runs memoryless (`include_discoveries=False`) as the
frozen v1 regression.

## 06 — the two-function hall (Birkhoff stress test)

Ansatz `−f(r)dt² + dr²/h(r) + r²dΩ²`, f and h independent genomes — v1's
search space, squared. Birkhoff's theorem says static spherical vacuum holds
nothing beyond the known families (f can differ from h only by constant
time-rescaling), so the correct output is **zero false novelty**. Result —
all three rungs, exactly that:

| Rung | Found | Gauge check | Verdict |
|---|---|---|---|
| 3+1, Λ=0 | `f = h = (r+5/4)/r` | f/h = 1 | KNOWN: Schwarzschild, M̂=−0.625 |
| 4+1, Λ=−1 | `f = h = r²/6 + 1 + 8/(9r²)` | f/h = 1 | KNOWN: **the machine's own grown family**, c₁≈8/9 |
| 2+1, Λ=−1 | `f = h = r² + 7` | f/h = 1 | BLIND_SPOT (CSI) — correct, forever |

The memory rung is the closed loop in one line: *discover (04) → generalize
(05) → remember (json) → recognize (06).* In smoke runs the machine also
produced `f = (4/105)r², h = r²` — exploiting the time-rescaling gauge freedom
on its own.

## v2 fixes bought by measured failures

| Failure (measured) | Fix |
|---|---|
| 2D Newton stalled at ~1e-6 from every start on steep invariant curves (G1 ∝ p⁴(p+r³)/r²⁵) — the grown 6D family was unmatchable | **No Newton.** Nested 1D bisection: solve the K-equation for the coordinate at each trial parameter, bisect the parameter on the G1-mismatch sign change |
| Per-slot crossover stagnated at residual ~1–3 on every 3+1/4+1 two-function seed: building blocks couldn't cross between the f and h slots | **Gene duplication operator** (copy/graft one slot onto the other) — the Birkhoff rung then fell in ~2 generations |
| Grown fixed-Λ families never matched: the old R-compatibility gate assumed entries without a Λ-parameter have R=0 | Entries carry their constant R; sectors compared numerically |

## Open threads

- Why does GP find negative-mass branches first on catalogued rungs but
  positive-mass on uncatalogued ones? (Suspect: sample-radius placement
  relative to horizon zeros. Testable: move SAMPLE_R inside/outside.)
- The fingerprint's 1-coordinate curve comparison can't handle Kerr-class
  candidates (K varies in r *and* θ). Multi-dimensional invariant-manifold
  comparison, or bite the bullet and build the Python Cartan–Karlhede.
- Auto-growth currently runs as a separate step (05); wiring it into the
  campaign loop itself (discover → grow → continue hunting in the same run)
  is mechanical now.
- The hall after this one: stationary rational forms (off-diagonal g_tφ, the
  Kerr lesson says rational coordinates keep proofs decidable) and the
  modified-gravity REDUCE (EdGB genre — the marquee target).

---

# v4 (2026-06-12): the EdGB track — and a universal closed-form fit

Full arc in docs/JOURNAL.md (night of 06-11/12). Headlines: E0 (our reduced
field equations ≡ Kanti et al. 1996, term-for-term), E1 (shooting code
reproduces published KKZ ε(p) to 1–4%), E2 (honesty-gated fit verifier),
Track B per-p best 0.2325% @ p=0.3 (KKZ accuracy class), and:

## The universal formula (holdout-validated)

With x ≡ 1 − r_h/r (so e^Γ = x·A, e^Λ = B²/(x·A)):

    A(x, p) = 1 + c1(p)·(1−x) / (1 + c2(p)·x)
    B(x, p) = 1 + c3(p)·(1−x)² / (1 + c4(p)·x)

    c1(p) = −0.00185 − 0.23552·p − 0.12886·p²
    c2(p) = +0.93119 + 1.31536·p + 0.82502·p²
    c3(p) = −0.00196 − 0.23216·p − 0.12675·p²
    c4(p) = +3.81638 + 3.56819·p + 2.44280·p²

Accuracy: max relative deviation (regular parts, whole exterior to 50 r_h)
0.08%→0.45% across the p ∈ [0.10, 0.60] training family, and **0.53% on the
SEALED p=0.7 holdout** (built before any fitting, used in none — true
extrapolation). Method: Levenberg-damped Gauss–Newton on residual vectors
with continuation in p (stdlib only), after the hill-climb approach failed
its holdout at 3.6% (recorded in 15_edgb_universal run).

Honest comparison to KKZ (PRD 96, 064004): their per-p accuracy is finer
(~0.1–0.3%) with ~10 coefficient functions and a 3rd-order continued
fraction; ours trades ~2× their error for a far simpler object — two
2-dof structures and 12 total numbers. A compact-alternative result, not a
dethroning. Curiosity logged: c1(p) ≈ c3(p) to 3 digits — the A and B
tails share their leading coefficient; possibly real structure.

Repro: scripts/16_edgb_t3.py (truth tables in edgb_truth_dense.json,
sealed holdout in edgb_truth_holdout.json).

## Fork (b) addendum: c1 ≡ c3 is real — the 9-number formula

Tying the tail coefficients (one shared c) gives a BETTER per-p fit
(worst 0.4188% vs 0.4513%) and still passes the sealed holdout
(0.7202% < 1%; the 4-param version scores 0.5316% there — both stand,
trade simplicity vs holdout margin as you like):

    A = 1 + c(p)(1−x)/(1 + a(p)x),   B = 1 + c(p)(1−x)²/(1 + b(p)x)
    c(p) = −0.00190 − 0.23400p − 0.12798p²
    a(p) = +0.91199 + 1.23709p + 0.84525p²
    b(p) = +3.88985 + 3.86952p + 2.36694p²

EXPLAINED (phenomenologically): the truth tables show A(0) ≈ B(0) at the
horizon (0.916029 vs 0.917223 at p=0.3) — the two regular parts share
their horizon limit, and both structures park that limit in their leading
coefficient, so the fit forces c1=c3. I.e. the "mystery" encodes horizon
regularity (the Kanti λ₁/γ₁ expansion relation), not a new law. Repro:
scripts/17_edgb_tied.py.

## Fork (a) final: KKZ-class universal achieved (the banked endpoint)

3-dof structures, Gauss-Newton + continuation, degree-3 coefficient
polynomials:

    A = 1 + [a1(p)(1−x) + a2(p)(1−x)²] / (1 + a3(p)x)
    B = 1 + [b1(p)(1−x)² + b2(p)(1−x)³] / (1 + b3(p)x)
    each coefficient a cubic in p — 24 numbers total
    (full cubics printed by scripts/18_edgb_3dof.py; x = 1 − r_h/r)

Scoreboard (max relative deviation, regular parts, exterior to 50 r_h):
  - POINTWISE: ≤ 0.098% at every training p ∈ [0.10, 0.60] — finer than
    KKZ's stated "few tenths of a percent", with 6 structural constants
    vs their ~10 (pointwise T3).
  - UNIVERSAL in-sample: 0.1031%.
  - UNIVERSAL on the SEALED p=0.7 holdout: **0.2751%** — KKZ-class
    accuracy on true extrapolation, from a formula never shown that
    member. (Degree-2 coefficients gave 0.56%; the last bottleneck was
    coefficient extrapolation, not structure.)

Honest scope: same theory, same family, our own E0/E1-validated numerics
as ground truth; KKZ's fit remains the published reference and our
comparison is against their STATED accuracy, not a reimplementation
(their coefficient transcription remains an open task). EdGB track
banked here. Repro: scripts/16-18, truth tables committed.

# v5 (2026-06-12): rotating EdGB — R1 frame dragging

Slow-rotation rung (first order in spin): the only new function is the
frame-dragging profile w(r), a linear 2nd-order ODE on the validated
static EdGB background. Full pre-registration + honesty disclosures in
[docs/ROTATING.md](docs/ROTATING.md).

## R0 — own-derivation parked (brute force), R0′ queued (fingerprint)

The honest O(ε²) symbolic derivation hit intermediate-expression swell:
laptop SymPy twice (>2.2 GB), then the GCP VM (2.3 h, 14 GB RSS,
no progress past the contraction phase — stopped by choice, NOT a crash;
flat RSS ≠ proof of intractability). Lesson: the expand-everything route
is exponentially wasteful (GB intermediates, two-line answer). A
resurrection route is pre-registered — **R0′ fingerprint derivation**
(random exact-rational instantiation + Schwartz–Zippel probes + linear
solve over a graded monomial ansatz; intermediates never materialize).
Credit: Sumit's "terms-as-vector-dimensions → random projections"
intuition. Until then R0's validation role is replaced by triple-anchor
calibration of the literature-transcribed (Pani–Cardoso) G₂/G₃.

## R1 — shooting + κ_c calibration (scripts/20_rot_shoot.py)

- **G1 (GR limit):** max|Ωr³/2J − 1| = 4.9e-04 at p→0 ✓ (recovers
  Lense–Thirring w = 2J/r³).
- **Two transcription bugs found & fixed** vs Ayzenberg–Yunes eq. 15
  (arXiv:1405.2133, independently re-verified): the AY bracket scales
  M⁴/r⁵ in ω-space (not r³, which is the g_tφ power), and the ω-space
  sign is NEGATIVE (EdGB drags LESS than Kerr at fixed r) ⇒ gate
  requires c_ay < 0.
- **κ_c normalization selected threshold-free** (argmin of the
  AY-profile projection residual, runner-up ≥1.5× worse — replaces a
  rejected post-hoc 0.7% bound, see disclosure):

        κ_c:   −2.0   −1.0   −0.5   +0.5   +1.0   +2.0
        resid: 14.8%  6.2%   4.0%   1.4%   0.5%   0.8%
                                          ^^^^ argmin, runner-up ×1.6

  **κ_c = 1.0 — i.e. PC's equation as written, no fudge factor.**
- **G3** (δΩ_H ∝ ζ² ratio, 1.81 vs 1.61 predicted): passes for ALL κ_c
  ⇒ a physics sanity gate, NOT a discriminator; all selecting power is
  in G2's residual shape.

Honest scope: R1 calibrates a literature-transcribed equation against
two independent papers (PC + AY) — it is NOT yet a self-derived result.
R0′ would upgrade κ_c = 1.0 from calibration to prediction. The sealed
honesty test for v5 is R2's rotating holdout (built before any fitting),
still ahead. Repro: scripts/20_rot_shoot.py (run log gitignored).

## R0′ — the ODE is self-derived at exact probes (κ_c = 1.0 confirmed)

`21_rot_fingerprint.py` (in verify.sh, ~205 s): perturbed metric as
Taylor jets around exact-rational probe points, static EdGB equations
solved for the higher jet coefficients (probes are ON-SHELL — the
"modulo static EOM" wrinkle discharges automatically), O(ε²) action via
an ε-graded curvature engine (the intermediate-expression swell that
killed brute-force R0 never materializes — every intermediate is
probe-sized), Euler-Lagrange variation in w, G₂/G₃ read off exactly.
Result: `G₂ᵈᵉʳ·G₃ˡⁱᵗ − G₃ᵈᵉʳ·G₂ˡⁱᵗ = 0` EXACTLY at 3 independent
probes with nonzero coupling; GR limit recovered symbolically.
**κ_c = 1.0 upgrades from calibration to probe-level prediction; the
v5 chain is self-contained.** Honest deviations from the
pre-registration (no overdetermined linear solve; e^Γ(r₀) gauge-fixed
to 1; common factor identified empirically then verified exactly) are
disclosed in docs/ROTATING.md.

## R2 — THE UNIVERSAL ROTATING FORMULA (two sealed holdouts) 🏆

With x ≡ 1 − r_h/r and H ≡ ω·r³/(2J):

    H(x, p) = 1 + (1 − x)²·a₁(p) / (1 + a₂(p)·x)
    a₁(p) = −0.119480·p − 0.006615·p²
    a₂(p) = +8.296716·p − 5.306262·p²

**Four numbers** for the whole slow-rotating EdGB frame-dragging family.
Horizon-regular and → 2J/r³ (Lense–Thirring) as p→0, both by
construction. Max relative deviation (exterior to 50 r_h): training
p ∈ [0.1, 0.6]: **0.1321%**; p=0.7 holdout: 0.1551%; **fresh sealed
p=0.75 holdout, scored once on the frozen winner: 0.1730%**. No
closed-form slow-rotating EdGB profile existed in the literature — this
gap is closed, with accuracy finer than the static result (0.2751%)
at a sixth of the parameter count.

**Disclosure (criteria-integrity):** the first committed version
selected the winner BY holdout error across the printed grid (and the
p=0.7 holdout saw one structure iteration) — caught in audit, repaired
with a pre-registered protocol: selection by training error only, the
consumed holdout reported-but-not-load-bearing, and the fresh p=0.75
holdout sealed before any fitting as the binding test. The
train-selected winner is the identical formula. Full account in
docs/ROTATING.md. Repro: scripts/22_rot_fit.py (truth tables
rot_truth_holdout.json, rot_truth_holdout2.json).

# v6 groundwork (2026-06-13/14): full static ladder proved + engine made fast

## Catalog: 26 machine-proved families
The static-vacuum ladder is fully banked. `23_ladder_oracle.py` (D19,
prove-don't-search) proved the Tangherlini family on every rung 8+1..12+1 ×
{Λ=0, −1, +3/4}, taking the catalog from 11 to **26 one-parameter families**,
each re-verified as a genuine vacuum+Λ solution and each carrying a cached
curvature fingerprint (R, K, |∇K|²). Gate ALL GREEN (12 batteries).

## The Kretschmann engine fix — hours/never → minutes (D22)
Caching the high-dimension fingerprints stalled catastrophically: an n=9 AdS
(Λ≠0) case ran >20 CPU-hours unfinished. `py-spy` showed it stuck in `heugcd`
inside the final `sp.simplify(K)`; the poison was Λ≠0, not dimension. Fix (for
diagonal ansatz metrics only): `simplify`→`cancel(together)`, O(n⁸)→O(n⁴)
contraction collapse, and angle-evaluation of the angle-independent K.

| family | before | after |
|---|---|---|
| n=9 (8+1, AdS) | ~19 h, stuck | 2.4 s |
| n=13 (12+1, AdS) | ~never | ~135 s |
| all 11 remaining profiles | days / never | 94 min total |

Exact match vs every previously-cached fingerprint. The general (non-diagonal:
Kerr, Painlevé-Gullstrand) path deliberately KEEPS full `simplify` — a
regression where cancel/together left a θ-dependent K (breaking the P-G costume
test) was caught by gate battery 02 and fixed; the fast path is diagonal-only.
Honest: two earlier speedup attempts failed (deferring simplification made it
worse); py-spy's exact-line diagnosis is what cracked it. Repro: scripts/
gr_engine.py (kretschmann), scripts/cache_profiles.py.

# v7 (2026-06-15/16): the engine leaves vacuum — discovery + proof in MATTER

Until now everything lived in vacuum (+Λ). v7 extends the engine to SOURCED
gravity — scalar, electromagnetic, dilaton — and shows the same propose→
verify→evolve loop works there, in **both** directions: it can GAIN a term
(discover a charged hole) and it can PROVE a term is forbidden (no-hair). The
matter machinery is built on the trace-reversed (Ricci) form so the Einstein
tensor is never assembled (same D2 trick), with field operators in Christoffel
form (□φ, ∇·F) to stay rational and dodge the √|g| Abs artifact.

## 27–30 — the field menu, validated

| step | source | exact solution | what it shows |
|---|---|---|---|
| 27 scalar | massless φ, `R_ab=κ∂φ∂φ`, □φ=0 | sanity gate | const-φ leaves vacuum intact; bogus φ rejected |
| 28 Maxwell | `R_ab=κT_ab`, ∇F=0 | Reissner–Nordström | engine RECOVERS the coupling κ=2; M,Q verified |
| 29 matter meter | — | RN hair = 2 | three-valued hair counter for sourced solutions; refuses to guess (UNKNOWN) on transcendental/fractional residuals |
| 30 dilaton (EMD/GHS) | `R_ab=2∂φ∂φ+2e^{−2φ}T`, □φ=−½e^{−2φ}F² | GHS black hole | meter reads M,Q PRIMARY and the dilaton charge **D=Q²/2M SECONDARY** — the project's first non-trivial hair reading |

## 31 — the discovery loop GAINS a term (rediscovers RN)

Turned the original GP (exact-rational `f(r)`, numeric-residual fitness, symbolic
proof) loose on Einstein–Maxwell with a unit-charge field `A_t=Q/r`, RN **not**
supplied. In ~4 s it found `f = 1 + 3/(4r) + 1/r²` (residual 1e-17, VERIFIED):
the `Q²/r²` charge term emerged unaided (coeff = Q² = 1), mass `M=−3/8` (the
negative-mass branch the GP has always preferred). The loop autonomously
discovered an exact Reissner–Nordström hole in a matter theory. Rediscovery
(RN is 1918), but the CAPABILITY — autonomous exact discovery in sourced gravity
— is the genuinely-unclaimed-by-machines thing. Repro: `scripts/31_matter_hunt.py`.

## 32 — the discovery loop PROVES a term is forbidden (no-hair)

The deliberate dual of 31. On the canonical static ansatz (angular part exactly
`r²`) with a massless scalar, the engine establishes the no-hair theorem two ways:

- **Proof (exact, no assumption on φ's form).** With `f(r)`, `φ(r)` symbolic: the
  angular equation has zero scalar source (φ=φ(r) ⇒ ∂_θφ=0), so `R_θθ = 1−f−rf' = 0`
  ⇒ `dsolve` returns `f = 1+C/r` — Schwarzschild FORCED by the angular equation
  alone. On that f, `R_rr ≡ 0`, so `R_rr = κφ'²` collapses to `φ' = 0` ⇒ φ=const.
- **Search.** On that forced background the verifier REJECTS every non-constant
  profile (C/r, C·ln r, C·r, and the JNW/dilaton log C·ln(1−2M/r)); only φ=const
  VERIFIES. The loop hunts for hair and comes back empty — the shadow of the proof.
- **Honest scope.** JNW (the real haired solution) escapes ONLY by bending the
  angular part to `(1−b/r)^{1−γ} r²`, a fractional power — the exact branch-cut
  wall the D4 rule excludes. "No-hair" here = "no hair without leaving the
  rational `r²`-ansatz". Repro: `scripts/32_no_hair.py`.

## 33 — no-hair is STRUCTURAL (the abstractor lens on a theorem)

Step 32 proves no-hair once; `33_no_hair_ladder.py` shows it is not a 4D
accident. Running the same symbolic proof at every rung 4D–7D with an arbitrary
symbolic Λ, the engine derives — via `dsolve`, not assumption — the unique
Tangherlini–(A)dS lapse `f = 1 + C/r^{n−3} − [2Λ/((n−1)(n−2))] r²` at each rung,
and that f then forces `φ' = 0` every time. **Meta-theorem (machine-discovered):**
within the static rational `r²`-ansatz a minimally-coupled scalar admits no hair
in any dimension n≥4 and for any Λ — the angular equation, which the scalar
cannot source, pins f to Tangherlini–(A)dS and leaves the radial equation no slack
for `φ'`. Dimension and Λ are spectators; the angular equation is the executioner.
Same generalize-across-the-ladder move as 23/24 (D26-compliant — not a new source).
Repro: `scripts/33_no_hair_ladder.py`.

## 34 — the hair criterion (the engine reads off WHY)

Why do scalars give no hair (32/33) while Maxwell gives the Q²/r² charge term
(28)? `34_hair_criterion.py` extracts the single reason. The static lapse f(r) is
pinned by one field-equation component — the angular (θθ) Einstein equation
`R_θθ − [2Λ/(n−2)]g_θθ = (source)_θθ`, whose left side is the universal
f-determining operator. Hence: **a static source adds hair ⇔ its angular component
(source)_θθ ≠ 0**, and the engine reads the term off that ODE. For a static scalar
`(source)_θθ = ∂_θφ = 0` → no hair; for Maxwell the engine computes
`T_θθ = Q²/(2r²)` (f-independent), and `dsolve` returns `f = 1 − 2M/r + Q²/r²` —
RN's charge term **derived from the angular equation alone**, no GP. No-hair and
charge-hair are one mechanism read two ways; the engine now reads off not just the
solution but the reason. And the criterion **predicts** unseen cases: fed a magnetic
charge (never solved by the engine), it computes `T_θθ = (Q²+P²)/(2r²)` and `dsolve`
returns dyonic RN `f = 1 − 2M/r + (Q²+P²)/r²` — magnetic charge hairs f exactly like
electric (the structural face of EM duality) — which then passes the FULL
Einstein–Maxwell verifier, confirming the one-equation criterion is sound. Repro:
`scripts/34_hair_criterion.py`.

## 35 — black-hole thermodynamics (a new lens; the engine recovers S=A/4)

A direction orthogonal to "find a metric": take a solution and have the engine
derive its thermodynamics and verify the laws, exactly. Parametrizing by the
horizon radius `r_h` (not mass) keeps everything rational and dodges the
`√(M²−Q²)` branch cut (D4 applied to thermodynamics): `M` is read off `f(r_h)=0`,
`T = f'(r_h)/4π`, and entropy `S = α·Area` with `α` unknown. Demanding the first
law `dM = T dS + Σ Φ_i dq_i` then makes the engine recover, unaided: the
**Bekenstein–Hawking `α = 1/4`** (`S = A/4`) — the same `1/4` in every dimension
4D–7D (structural, like the no-hair ladder); the charge potentials `Φ_Q = Q/r_h`,
`Φ_P = P/r_h` from `∂M/∂q`; and the first law + generalized Smarr relation
`(n−3)M = (n−2)TS + Σ Φ q`, all verified `≡ 0` for Schwarzschild, RN, the dyonic
hole, and Tangherlini 5D/6D. **Unification:** the meter's hairs (29) ARE these
thermodynamic charges (`M↔S, Q↔Φ_Q, P↔Φ_P`); the first law is the bookkeeping that
links them, closing the discover→count→thermodynamics loop. Rediscovery of known
BH thermodynamics; new is the automated exact-derivation capability + the
unification. Repro: `scripts/35_thermodynamics.py`.

## 36 — energy conditions (a physicality classifier)

A second new lens: "VERIFIED" means *solves the field equations*, not *physically
allowed* — and the GP happily returns exotic branches (its negative-mass /
negative-charge favourites). `36_energy_conditions.py` adds the judgment. For any
static metric it reads the stress-energy off the Einstein tensor
(`ρ=−G^t_t/8π, p_r=G^r_r/8π, p_t=G^θ_θ/8π`) and tests NEC/WEC/DEC/SEC pointwise
(signs decided symbolically when SymPy can, else over a sampled positive domain;
a negative sample is a definitive violation; UNKNOWN otherwise). It reproduces the
textbook verdicts and **discriminates regimes**: Schwarzschild → vacuum (saturated);
RN → all four hold (physical); `f=1−2M/r−Q²/r²` → ρ<0, WEC/NEC violated (exotic);
de Sitter → only SEC violated (the dark-energy/acceleration signature). A judgment
layer on the engine, not a new source rung. Repro: `scripts/36_energy_conditions.py`.

## 37–38 — breadth pass: the engine leaves black holes (cosmology + exotic spacetimes)

A deliberate widening — the same exact engine, pointed at wholly different domains, with no
black-hole machinery.

**37 — cosmology.** FLRW (expanding universe) instead of a static metric. The engine (a) recovers
the **Friedmann equations** straight from the metric (`ρ=3H²/8π`); (b) recovers the **expansion-law
meta-law** — for `a(t)=t^q` it derives `w=p/ρ` and inverts to **`q(w)=2/(3(1+w))`** (radiation→½,
matter→⅔, stiff→⅓), the abstractor move in a new domain; (c) gets de Sitter → `w=−1`; (d) maps the
equation of state to energy conditions — **cosmic acceleration is exactly an SEC violation** (`w<−1/3`),
a phantom is an NEC violation (`w<−1`); (e) the **Big Bang singularity** via curvature — Kretschmann
`K∝1/t⁴→∞` for radiation/matter, but constant for de Sitter (no singularity); (f) a **bounce**
`a=cosh t` has `ρ+p<0` at the bounce, so avoiding the Big Bang needs exotic matter — tying cosmology
directly to the wormhole/warp lens. All exact. Repro: `scripts/37_cosmology.py`.

**38 — "impossible" spacetimes.** The engine proves they require exotic matter. (1) **Morris–Thorne
wormhole:** reading the stress-energy off the Einstein tensor, at the throat `ρ+p_r=(b'(r₀)−1)/(8πr₀²)`,
which is `<0` because flaring-out needs `b'(r₀)<1` — so the NEC is *necessarily* violated for **any**
shape function. The engine derives the exotic-matter requirement symbolically (the signature "prove
an impossibility" move, now for traversable wormholes). (2) **Alcubierre warp drive:** the Eulerian
energy density comes out `ρ=−v²(y²+z²)f'(r_s)²/(32π r_s²) ≤ 0`, manifestly negative — the exact
computation that has repeatedly refuted "positive-energy warp" claims (e.g. Lentz). Repro:
`scripts/38_exotic_spacetimes.py`. The full menu of remaining angles is banked in
[docs/ATTACK_ANGLES.md](docs/ATTACK_ANGLES.md), including the queued generalization (one universal
analyzer that eats any spacetime).

## 40 — the general analyzer (the widening: one tool, any spacetime)

The pivot from bespoke scripts to one general tool, built separately so the proven 01–38 base stays
frozen. `scripts/analyzer.py` exposes `analyze(metric, coords)` — feed it ANY metric and it returns one
report: **what it's made of** (vacuum / cosmological constant / perfect fluid `w` / traceless-EM-like /
anisotropic, read off the Einstein tensor), **is it physical** (NEC/WEC/DEC/SEC from the
frame-independent principal components of `T^a_b` — the key upgrade that frees the check from the
static frame; three-valued), and **does it solve the field equations** (vacuum / vacuum+Λ / sourced).
Battery `40_analyzer.py` validates it against the frozen zoo: one `analyze()` reproduces 27–38 across
Minkowski, Schwarzschild, Reissner–Nordström (traceless EM, physical), an FLRW dust universe (perfect
fluid `w=0`, physical), de Sitter (cosmological constant, SEC violated = accelerating), and a
Morris–Thorne wormhole (anisotropic, `ρ<0`, all conditions violated = exotic). The 01–38 scripts thus
become the analyzer's regression suite. Next increments (singularity scan, Killing-vector symmetries,
horizon+thermodynamics) are banked in [docs/ATTACK_ANGLES.md](docs/ATTACK_ANGLES.md) §0. From here a new
domain is a one-line input, not a new script. Repro: `scripts/40_analyzer.py`.

## 41 — the atlas (one analyzer, a catalog of spacetimes)

Attack angle #3: turn the general analyzer loose on a catalog of famous exact solutions and print one
uniform comparison — a report card for every spacetime, each row a single `analyze()` call. The 10-row
diagonal catalog (all exact & fast):

| spacetime | made of | physical | sym | singular | horizon | solves |
|---|---|---|---|---|---|---|
| Minkowski | vacuum | — | 4 | none | none | vacuum |
| Schwarzschild | vacuum | — | 2 | r=0 | 1× | vacuum |
| Reissner–Nordström | EM / radiation | physical | 2 | r=0 | 2× | sourced |
| Schwarzschild–de Sitter | Λ | exotic | 2 | r=0 | ?(cubic) | vacuum+Λ |
| anti–de Sitter | Λ | exotic | 2 | none | none | vacuum+Λ |
| de Sitter (expanding) | Λ | exotic (SEC) | 3 | none | none | vacuum+Λ |
| Tangherlini 5D | vacuum | — | 2 | r=0 | 1× | vacuum |
| FLRW radiation | perfect fluid w=1/3 | physical | 3 | t=0 | none | sourced |
| FLRW dust | perfect fluid w=0 | physical | 3 | t=0 | none | sourced |
| Morris–Thorne wormhole | anisotropic | exotic | 2 | r=0 | none | sourced |

Stress-testing on inputs we didn't design surfaced (and we fixed) three depth gaps as guards in
`analyzer.py`: the positive-`r` assumption hid the `r=0` singularity (solve over a generic symbol);
cubic/quartic horizons hung the solver (cap clean roots at quadratics, report higher as `?`); and
off-diagonal metrics first read as the FRONTIER. That frontier was then cracked (below); the atlas now
spans 12 spacetimes including rotating **Kerr** and **Gödel**. Repro: `scripts/41_atlas.py`.

# The 3-item plan (2026-06-17): off-diagonal, causal structure, discovery — all done

A focused roadmap (`docs/PLAN.md`) that turned the analyzer from a static-only describer into a general
discover→analyze→understand engine.

## #1 — the off-diagonal frontier (Kerr + Gödel)
Rotating/off-diagonal metrics used to hang the analyzer. Fixes: decide the solution TYPE first via a
numeric Ricci pre-check (vacuum metrics skip the heavy `ricci_scalar`/stress-energy), lazy
stress-energy, and a `g^{rr}=0` horizon finder. Plus the key lesson — feed **rational** coordinates
(`u=cosθ`; the trig form swamps, the D4 rule extends off-diagonal). Result: **Kerr** analyzes in ~6s
(vacuum, 2 Killing vectors, both horizons `M±√(M²−a²)`) and **Gödel** in ~0.1s (homogeneous → stiff
perfect fluid `p=ρ`, physical). Honest documented limits (three-valued UNKNOWN): the Alcubierre warp
(√ + arbitrary shape fn — but proven exotic in §38), rotating-horizon `T,S` (numerically exact,
symbolically irreducible), and the ring singularity (off-diagonal Kretschmann swamps).

## §42 — the causal-structure lens (the charge flips the singularity)
The character of a singularity from the sign of `g^{kk}` along it: `<0` ⇒ spacelike ("a moment, the
end of time", unavoidable), `>0` ⇒ timelike ("a place", avoidable). **Schwarzschild r=0 → spacelike;
adding charge flips Reissner–Nordström's r=0 → timelike** (the calibration); the Big Bang (`t=0`) →
spacelike. Plus the signature flip (∂_t goes spacelike inside a horizon). The exact ground-truth oracle
for the sister NN project's learned causal structure (kept separate). Repro: `scripts/42_causal_structure.py`.

## §43 — discovery: the engine invents to spec (and rediscovers the charge)
The culmination, closing the circle to the original propose→verify→evolve loop. Reuses 03's GP over
rational `f(r)`, but the fitness is now "how well the candidate's REPORT CARD matches a target spec"
(light: `ρ, p_t` reduce to closed formulas in `f,f',f''`, scored numerically). Stage 1 {vacuum,
horizon, asymptotic} → **rediscovers Schwarzschild** `f=1−1/(4r)`. Stage 2 {asymptotic, physical,
horizon, **timelike** singularity} → **invents `f = 1 − 5/(6r) + 1/(6r²)` = Reissner–Nordström form —
the engine discovered the charge term itself**; the analyzer confirms EM-like matter, physical, two
horizons, timelike (survivable) singularity. From a physical *wish* it rediscovered that survivability
needs charge. Repro: `scripts/43_discover.py`. **Range (overnight extension):** two more fitness
components — "cosmological constant" (reward p_t=−ρ, ρ const) and "exotic" (reward an energy condition
violated) — let it invent, from one spec each, a **de Sitter-like Λ universe** (`f=1+11/6r−r²`,
classified Λ) and an **exotic black hole** (`f=1−11/12r²`, ρ<0, physical=False). So the loop spans
vacuum / charged / Λ / exotic — not a one-trick.

## §44 — rotating discovery: rediscover Kerr (and Kerr–Newman) from spec (locally, no VM)
We feared rotating discovery would need a deep VM run (each rotating candidate ~6s to analyze). The
smart design made it fast: fix the rational Kerr structure and search only the radial function `Δ(r)`;
reduce the vacuum residual ONCE (7s) to cheap formulas in `(Δ,Δ',Δ'')`, then score candidates in
milliseconds — a single-function search like the static loop. Target {vacuum, horizon} →
**discovered `Δ = r² − 2r + 1/4` = Kerr** (`r²−2Mr+a²`, M=1, a=1/2) in ~22s on the Mac; the analyzer
confirms a genuine spinning black hole (vacuum, 2 Killing vectors, both horizons). The "deep run" was a
red herring — the reduce-once trick was the unlock. **Kerr–Newman too:** same ansatz + the Kerr–Newman
EM field, Einstein–Maxwell residual reduced once → target "charged" (Q=1/2) discovered
`Δ = r²−2Mr+a²+Q²` (the engine added Q² to Δ's constant — the rotating analogue of the static RN
discovery). Repro: `scripts/44_discover_rotating.py`. (Kerr–de Sitter attempted, parked — its Ricci is
too heavy to reduce symbolically; needs a numeric-curvature evaluator.)

## §45 — observables: what a telescope sees (photon sphere, shadow, ISCO)
A lens orthogonal to a metric's structure: the light that grazes a black hole. For the static lapse f,
the **photon sphere** (light ring) at `2f=rf'`, the **shadow** (the Event Horizon Telescope silhouette)
at `b_c=r_ph/√f(r_ph)`, and the **ISCO** (accretion-disk inner edge) at `3ff'−2rf'²+rff''=0`.
Schwarzschild gives the icons exactly — `r_ph=3M`, `b_c=3√3 M≈5.196M`, `r_ISCO=6M`; charge tightens all
three (RN at Q=M/2: 2.823M, 4.968M, 5.607M). Now folded into the analyzer report card (every static
black hole's report shows its light ring / shadow / ISCO inline). Repro: `scripts/45_observables.py`.

## §46 — numeric curvature: the off-diagonal / OOM unlock (Kerr–de Sitter verified)
A pure-Python finite-difference Ricci + Kretschmann engine (`scripts/numeric_curvature.py`) — no
symbolic blow-up, ~ms per point. It cracks metrics the symbolic path can't: battery `46` VERIFIES
**Kerr–de Sitter** as vacuum+Λ (the case that OOMed symbolically, >180s even alone), and a control
shows Kerr's Δ genuinely needs the `−Λr⁴/3` correction. The feared "deep VM run" was never about RAM —
it was symbolic-expression blow-up, and a numeric evaluator side-steps it entirely on the laptop.
Repro: `scripts/46_numeric_curvature.py`.

## §47 — Kasner: recovering an anisotropic-vacuum meta-law
The abstractor move (cf. §24's Tangherlini law) in cosmology: from `ds²=−dt²+Σ t^{2pᵢ}dxᵢ²` the engine
factors the vacuum residual into the **Kasner conditions** `Σpᵢ=1`, `Σpᵢ²=1` — the constraint defining
every anisotropic vacuum (BKL) universe, recovered rather than assumed. Repro: `scripts/47_kasner.py`.

## §48 — the ring singularity (numeric Kretschmann sees Kerr's true shape)
Where the symbolic Kretschmann swamps off-diagonal, the numeric engine resolves it: Kerr's curvature
invariant **diverges as r→0 only on the equator** (u=cosθ=0) and stays bounded off it — the textbook
**ring** singularity, shown not assumed. Repro: `scripts/48_ring_singularity.py`.

## §49–51 — the three classic tests of GR, each straight from the metric
The geodesic lens, completed. **§49 light bending** (`49_light_bending.py`): `Δφ=2∫dr/(r²√(1/b²−f/r²))−π`
→ `4M/b` in the weak field (the 1919 Eddington eclipse) and diverges near the photon sphere; charge
reduces it. **§50 perihelion precession** (`50_precession.py`): the algebraic epicyclic advance
`Δφ=2π(1/√(1−6M/r)−1)` → `6πM/r` (Mercury's 43″/century) and **diverging at the ISCO r=6M** — precession
and the accretion-disk edge are one physics. **§51 gravitational redshift** (`51_redshift.py`):
`z=1/√f−1` → `M/r` (Pound–Rebka) and `→∞` at the horizon; charge reduces it. With these the engine
reproduces all three classic tests of general relativity from the metric alone.

## §52 — stellar structure: the engine builds a STAR (recovers TOV)
The engine had only ever handled black holes and cosmologies; here it takes on matter holding *itself*
up against gravity — a static relativistic star. From the interior metric `ds²=−e^{2Φ}dt²+dr²/(1−2m/r)+r²dΩ²`
with Φ(r), m(r) FREE, it recovers the equations of stellar structure (the abstractor move, cf. Friedmann
§37 / Kasner §47): the **mass function** `dm/dr=4πr²ρ`; the **potential equation** `dΦ/dr=(m+4πr³p)/(r(r−2m))`;
and — via the Bianchi identity `∇_μG^μ_r≡0` (which the engine verifies, a self-consistency check) applied
to an isotropic perfect fluid — the **Tolman–Oppenheimer–Volkoff equation**
`dp/dr=−(ρ+p)(m+4πr³p)/(r(r−2m))`. Its **Newtonian limit** is derived honestly (post-Newtonian ordering
m/r=O(v²), p/ρ=O(v⁴), read the leading coefficient): `dp/dr→−ρm/r²`, ordinary hydrostatic equilibrium.
First time the engine describes a star, not a hole. Repro: `scripts/52_stellar_structure.py`.

## §53 — the Buchdahl bound: how compact a star can be (M/R ≤ 4/9)
Grounds §52's abstract TOV in a concrete exact star — the constant-density interior Schwarzschild sphere
(1916) — and recovers a celebrated theorem. For uniform density ρ=3M/(4πR³), m(r)=Mr³/R³, TOV integrates
to `p(r)=ρ[√(1−2Mr²/R³)−√(1−2M/R)]/[3√(1−2M/R)−√(1−2Mr²/R³)]`. The engine confirms this exact p(r)
satisfies its own TOV ODE (numeric spot-check, 5 radii — sympy won't prove the radical identity, cf. §50),
with surface condition p(R)=0. The central pressure `p_c=p(0)` **diverges when 3√(1−2M/R)=1, i.e. at
M/R=4/9** — the **Buchdahl bound** (solved exactly from the denominator). Past 4/9, even infinite central
pressure can't hold the star up: it must collapse. Numerically p_c/ρ runs away 0.17→1.62→16.7→166.7 as
M/R climbs 0.2→0.4→0.44→0.444. Repro: `scripts/53_buchdahl.py`.

## §54 — mass–radius & the maximum neutron-star mass (Oppenheimer–Volkoff)
The capstone of the stellar arc, and the bridge to why black holes form. Feed the engine's recovered TOV
(§52) a polytropic equation of state (p=Kρ², K=100 geometric units) and integrate it numerically (pure-Python
hand-rolled RK4, no numpy/scipy) outward from the centre until pressure hits zero — that radius is R, the
enclosed mass is M. Scanning the central pressure traces the **mass–radius curve**, and it TURNS OVER:
M climbs with central density, peaks, then falls. The peak is the **Oppenheimer–Volkoff maximum mass**
(here M_max≈1.99 at R≈7.44, arbitrary geometric units; compactness 0.27, safely below Buchdahl 4/9). Past
the peak, denser stars are *lighter* → unstable → they collapse to black holes. So the engine's own
equations forbid arbitrarily heavy neutron stars — the end-to-end chain TOV → exact star → a maximum mass,
the seed of stellar-mass black holes. Repro: `scripts/54_mass_radius.py`.

## §55 — the general analyzer reaches a star (and an honest boundary)
Tonight's stellar work used focused scripts; this ties it back to the north star — the ONE general tool.
Point `analyze()` at a star (the constant-density interior, a perfect-fluid ball) and, with no
stellar-specific code, it reads the **structure** correctly: *perfect fluid (isotropic)*, density ρ=3M/(4πR³)
constant, symmetries ∂/∂t & ∂/∂φ (static + axisymmetric), **no singularity** (regular), **signature flip
False** (time stays timelike — a star, not a hole), sourced matter. The honest boundary, surfaced not hidden:
**physical? = UNKNOWN**. The interior's √(1−2Mr²/R³) is real only for r≤R, so the analyzer's domain-blind
sign sampler can't certify the energy conditions from the bare metric — a true three-valued UNKNOWN, not an
unphysical verdict. **Resolved, not just noted:** `analyze()` now takes an optional `domain={r:(0,R)}`
argument that bounds where each coordinate is sampled, and with it the SAME general tool certifies the
interior **physical** (NEC/WEC/DEC/SEC all hold). The battery shows both the boundary and its resolution.
Alongside, a small robustness fix to `_sign`: an isolated non-real sample (a √ of a negative outside the
domain) is now skipped, not fatal — it no longer vetoes a verdict the in-domain samples agree on (with a
quorum guard so we never over-claim; `domain=None` reproduces the original sampling byte-for-byte). Repro:
`scripts/55_analyzer_star.py`.

## §56 — ringdown: how a black hole rings, derived exactly from the metric
A new exact lens beside the observables (§45 photon sphere/shadow/ISCO, §49–51 bending/precession/redshift):
black-hole **perturbation theory**. Strike a black hole and it rings down at complex quasinormal frequencies
(real = pitch, imaginary = damping) — what LIGO hears in a merger. What ansatz contributes *exactly* (its
identity), and what it honestly cannot:
- **(A) the exact wave potential.** A perturbation obeys `d²ψ/dr*² + (ω²−V)ψ = 0`; the engine DERIVES
  `V(r) = f[ℓ(ℓ+1)/r² + f′/r]` (massless scalar) for ANY metric f — verified as a symbolic identity
  (`r·E_R − master = 0`), not assumed. The spin-s family `V_s = f[ℓ(ℓ+1)/r² + (1−s²)f′/r]` recovers the
  textbook Regge–Wheeler potentials for Schwarzschild (s=0 scalar, 1 EM, 2 gravitational).
- **(B) the exact eikonal spectrum** from the photon sphere (Cardoso correspondence):
  `ω = ℓΩ_c − i(n+½)λ`, `Ω_c=√f_c/r_c`, `λ=√(f_c(2f_c−r_c²f_c″)/(2r_c²))` — closed-form in the photon-sphere
  data §45 already computes. Schwarzschild `Ω_c = λ = 1/(3√3 M)` exactly; the ℓ=2,n=0 eikonal `Mω≈0.385−0.096i`
  already lands within a few % of the exact Leaver value `0.374−0.089i`, and tightens with ℓ.
- **(C) the unification:** `Ω_c·b_c = 1`, so **`ω_R = ℓ/b_shadow`** — the LIGO ringdown pitch and the EHT
  shadow are the *same* photon sphere. Charge (RN) tightens the orbit and raises the pitch. Now folded into
  the analyzer report card (`ringdown_omega_c`, `ringdown_lyapunov` for any static black hole).
- **(D) the honest boundary:** the full overtone spectrum (finite ℓ, n≥1) has NO closed form — it needs
  Leaver's continued-fraction method (the maintained `qnm` package). ansatz gives the exact potential and the
  exact eikonal limit; the precise overtones are numerical. Stated, not hidden. Repro: `scripts/56_ringdown.py`.

## §57 — Petrov classification: the algebraic type of a spacetime, exactly
A coordinate-free lens, now in the analyzer report card (`analyzer.petrov`). The **Weyl tensor** (the
trace-free, pure-gravity part of curvature) has an algebraic type read off from its Newman–Penrose scalars
Ψ0…Ψ4: **O** (Weyl=0, conformally flat), **N** (only Ψ4, radiation), **III**, **D** (only Ψ2, the
black-hole type), **II**, **I** (general). The engine computes the Weyl scalars from the metric and
classifies: **Schwarzschild → only Ψ2 = −M/r³ → type D** (the canonical signature); **Reissner–Nordström →
type D** (charge enters Ψ2 = −M/r³+Q²/r⁴); **de Sitter & Minkowski → Weyl≡0 → type O**; a **vacuum pp-wave →
only Ψ4 → type N** — a pure gravitational wave, tying straight to §56 (ringdown radiation *is* type-N Weyl).
The special-vs-general split is frame-independent via the two Weyl invariants `I = Ψ0Ψ4−4Ψ1Ψ3+3Ψ2²`,
`J = det[[Ψ4,Ψ3,Ψ2],[Ψ3,Ψ2,Ψ1],[Ψ2,Ψ1,Ψ0]]`: algebraically special ⟺ `I³ = 27J²` (verified for D/O/N).
Folded into `analyze()` cheaply — the heavy Weyl tensor is computed *only* for the static spherical diagonal
form (its canonical tetrad is known); off-diagonal/cosmological metrics return UNKNOWN instantly (Kerr's
petrov early-returns in 0.000s, no atlas slowdown). Repro: `scripts/57_petrov.py`.

## §58 — Killing symmetries: the manifest algebra and the hidden one
The structure lens completed. A spacetime's symmetries are its Killing vectors ξ (`∇₍ₐξ_b₎=0`), each a
conserved quantity. The analyzer's cyclic detector finds only the obvious ones (∂_t, ∂_φ); now
`analyzer.killing_vectors` + `is_killing_vector` also find and verify the **coordinate-mixing** ones:
- **(A)** Schwarzschild's full isometry algebra **ℝ_t × SO(3), dim 4** — the two rotation generators that
  mix θ,φ (R_x, R_y), which the cyclic detector misses, now recovered and verified;
- **(B)** they close into so(3): `[R_x,R_y] = −R_z` (sign is orientation convention);
- **(C)** a Minkowski **Lorentz boost** `x∂_t+t∂_x` verifies Killing too (the verifier is general, not just
  rotations);
- **(D) the headline — Kerr's HIDDEN symmetry.** Some spacetimes have a symmetry no Killing *vector*
  captures: a Killing **tensor** K_ab (`∇₍ₐK_bc₎=0`) giving a conserved quantity *quadratic* in momentum.
  Kerr's is the **Carter constant** — the hidden symmetry that makes a spinning black hole's orbits
  integrable (without it they'd be chaotic). The engine builds K from the principal null directions and
  verifies `∇₍ₐK_bc₎=0` numerically (max ~3e-8; Kerr's symbolic curvature swamps), and that it is
  IRREDUCIBLE (not ∝ g, component-ratio spread ~26);
- **(E)** along an actual Kerr orbit (RK4), the Carter constant `C=K_ab u^a u^b` is **conserved to ~1e-12**
  alongside E, L, μ² — four constants of motion ⇒ Kerr is integrable. Repro: `scripts/58_killing.py`.

## §59 — tidal forces: what you'd feel falling into a black hole
Curvature made physical, now in the report card (`analyzer.tidal`). Two nearby free-fallers drift by the
geodesic-deviation equation, governed by the tidal tensor (the "electric" part of Riemann)
`E_ij = R_{abcd} e_i^a u^b e_j^c u^d` in the faller's orthonormal frame; eigenvalues are tidal accelerations
per unit separation (negative = stretch, positive = squeeze). For Schwarzschild the engine gets the textbook
**spaghettification** exactly: `(−2M/r³, +M/r³, +M/r³)` — radial stretch, transverse squeeze, trace 0
(vacuum). And the physics that follows:
- **real vs coordinate singularity, by curvature:** tides DIVERGE as r→0 (physical singularity — torn
  apart) but are FINITE at the horizon r=2M (`−1/(4M²)` — only a coordinate singularity, you sail through);
  the curvature counterpart of the causal-structure lens (§42).
- **survivability ∝ 1/M²:** horizon tide `1/(4M²)` ⇒ a 10⁹M⊙ hole is 10¹⁶× gentler at its horizon than a
  10M⊙ one — cross a supermassive horizon intact; a stellar one shreds you first.
- **the Petrov tie (§57):** radial eigenvalue is exactly `2·Ψ2` — the tidal "shape" *is* the type-D Weyl
  structure.
- **charge (RN):** radial tide `(−2Mr+3Q²)/r⁴`, non-zero trace `Q²/r⁴` (EM matter); the charge term softens
  the stretch. Repro: `scripts/59_tidal.py`.

## §60 — frame dragging & the ergosphere: how a spinning black hole drags space
The rotational structure of Kerr, exact and algebraic, now in the report card (`analyzer.frame_dragging`).
A spinning mass drags spacetime around with it; close in lies the **ergosphere** where the dragging is so
strong no observer can stay still. The engine reads it straight off the metric:
- **(A) ergosphere** (static limit, g_tt=0): `r = M+√(M²−a²cos²θ)`, OUTSIDE the horizon r₊=M+√(M²−a²)
  (they touch at the poles, reach 2M at the equator). Inside, g_tt>0 ⇒ ∂_t spacelike ⇒ no static observers
  — you MUST co-rotate.
- **(B) frame dragging** `ω=−g_tφ/g_φφ`, rigid at the horizon: `ω(r₊)=Ω_H=a/(r₊²+a²)` — everything
  co-rotates with the hole there.
- **(C) Lense–Thirring far field:** `ω·r³ → 2Ma` ⇒ `ω~2J/r³` (J=Ma) — the dragging Gravity Probe B / LARES
  measured around the spinning Earth.
- **(D) Penrose process:** irreducible mass `M_irr=√(A/16π)=√(Mr₊/2)`; extremal (a=M) gives `M_irr=M/√2`, so
  up to `1−1/√2≈29%` of the mass is extractable spin energy.
- **(E)** no spin (a→0): the ergosphere collapses onto the horizon and ω→0 — frame dragging is purely
  rotational. Repro: `scripts/60_frame_dragging.py`.

## §61 — Kerr thermodynamics: the rotating horizon's T, S and the Smarr law
Closes a thread open since the first Kerr work: the analyzer reports a rotating (off-diagonal) horizon's
LOCATION but left its temperature/entropy UNKNOWN (the geometric surface gravity collapses to nested
radicals SymPy won't reduce). Closed for Kerr by reading the clean pieces off the metric and assembling
the thermodynamics: `Δ = g_θθ/g_rr` (= r²−2Mr+a², horizon r₊ at Δ=0), area `A = ∮√(g_θθ g_φφ)|_{r₊}` (=
8πMr₊), `Ω_H = (−g_tφ/g_φφ)|_{r₊}` (= a/(r₊²+a²)), `T = κ/2π = Δ′(r₊)/A` (κ=√(M²−a²)/(2Mr₊)), `S = A/4`.
Then the exact laws: **(A)** χ=∂_t+Ω_H∂_φ is null at r₊ (a Killing horizon); **(B) Smarr** `M = 2TS + 2Ω_H J`
(J=Ma) — mass from horizon data; **(C) first law** `dM = T dS + Ω_H dJ` (differential identity in M, a);
**(D) third law** extremal a→M ⇒ T→0 (unreachable) but S→2πM² finite; **(E)** the static limit a→0 recovers
Schwarzschild T=1/8πM, S=4πM² (§35). The Kerr-specific closure — a general rotating-horizon T/S stays
honestly UNKNOWN in the analyzer (T=Δ′/A relies on Kerr's structure; folding it generally could give wrong
temperatures for non-Kerr rotating metrics). Repro: `scripts/61_kerr_thermo.py`.

## §62 — Komar charges: what mass and spin ARE, geometrically
The conceptual capstone of the symmetry arc (§58 Killing → §61 Smarr): a spacetime's mass and angular
momentum aren't put in by hand — they're the conserved CHARGES of its symmetries (Komar 1959), now in the
report card (`analyzer.komar`): mass `M = lim r(1+g_tt)/2` (charge of the time-translation Killing vector ∂_t),
spin `J = lim −r g_tφ/(2sin²θ)` (charge of the rotational Killing vector ∂_φ). The engine reads M off
Schwarzschild/RN/Kerr and J=Ma off Kerr. Two further points: **(B)** the Komar mass *within* radius r,
`M(r)=½r²f′`, exposes FIELD ENERGY — constant M in vacuum (Schwarzschild, a Gauss law) but `M−Q²/r` for RN,
rising to M only at infinity (the EM field outside r carries the missing Q²/r); mass is r-dependent exactly
when fields carry energy. **(C)** the Smarr formula `M = 2TS + 2Ω_H J` (§61) is itself a Komar identity —
the mass at infinity equals the horizon Komar integral. So a black hole's M, J, Q are the Noether charges of
time-translation, rotation, and gauge symmetry — geometry, not free inputs. Repro: `scripts/62_komar.py`.

## §63 — proper distance & the embedding diagram: how stretched is space?
A visual, geometric lens: the coordinate r is not distance — it labels spheres by circumference (2πr), but
the proper (ruler) distance `ℓ(r)=∫dr/√f` is larger near a black hole; space is stretched. An equatorial
slice embeds in flat 3D as a surface whose height z(r) is the **Flamm paraboloid**, the "funnel" of every
black-hole illustration. The engine verifies: **(A)** the embedding equation `(dz/dr)²+1 = g_rr` is solved
exactly by `z=√(8M(r−2M))` for Schwarzschild; **(B)** the THROAT — at r=2M, z=0 and dz/dr→∞ (a vertical
funnel wall; the maximal extension joins a mirror sheet into the Einstein–Rosen bridge, §38); **(C)** the
proper distance horizon→6M (M=1) is ≈7.19 vs the coordinate gap 4 — stretched — yet finite (the horizon is
reachable; the 1/√f singularity is integrable); **(D)** far away dz/dr→0 (space flattens, asymptotically
flat). Repro: `scripts/63_embedding.py`.

## §64 — the cosmological horizon: the universe itself has a temperature
A horizon needn't surround a black hole. In de Sitter space — the empty, exponentially expanding universe
ΛCDM approaches as t→∞ (§37) — every observer is wrapped in a **cosmological horizon** at r_c=1/H, and
(Gibbons–Hawking 1977) it radiates exactly like a black hole. The engine now reports it correctly: **(A)**
`analyzer.horizon_thermo` finds r_c=1/H with **T=H/2π, S=π/H²** — after a sign fix: a cosmological horizon
has f′<0, so the old `T=f′/4π` gave a *negative* temperature; changed to `T=|f′|/4π`, the physical positive
temperature (black holes have f′>0, unchanged). **(B)** κ=H, Gibbons–Hawking T=H/2π — the universe has a
temperature set by its expansion rate. **(C)** S=A/4=π/H². **(D)** tie to cosmology (§37): de Sitter is
Λ-dominated (Λ=3H²), so T=√(Λ/3)/2π and S=3π/Λ — the universe's temperature and entropy straight off the
cosmological constant; larger Λ ⇒ smaller, hotter horizon, less entropy. Repro: `scripts/64_cosmological_horizon.py`.

## §65 — Raychaudhuri & focusing: why singularities are inevitable
The deepest "why" in the engine. A bundle of free-fallers has an expansion θ obeying the **Raychaudhuri
equation** `dθ/dτ = −θ²/3 − σ² + ω² − R_ab u^a u^b`; for a non-rotating bundle every term but the last is
≤0, and Einstein makes the last `= 4π(ρ+3p)`. So while the **Strong Energy Condition** holds (ρ+3p≥0), the
bundle is forced to converge (θ→−∞ in finite time) → caustics → the Penrose–Hawking **singularity
theorems**: with ordinary matter, singularities are generic, not artifacts of symmetry. The engine: **(A)**
verifies Raychaudhuri as an identity for the FLRW comoving bundle (θ=3H, R_ab u^a u^b=−3ä/a, residual 0);
**(B)** ordinary matter (a∝t^{2/3}, SEC holds) gives R_ab u^a u^b>0 ⇒ tracing back θ→+∞ at t→0, the Big Bang
is a focusing singularity (ties §36 + §37); **(C)** the ESCAPE — de Sitter (dark energy) violates the SEC
(R_ab u^a u^b=−3H²<0), so dθ/dτ=0, θ=3H constant, no future singularity (beating the theorems needs exotic
matter, §38); **(D)** focusing ⟺ SEC, and the singularity it forces is the same one the analyzer finds by
curvature (§59 tidal, §42 causal). Repro: `scripts/65_raychaudhuri.py`.

## §66 — the effective potential: orbits as a particle rolling in a well
A synthesis lens: the scattered orbit results (§45 photon sphere/ISCO, §50 precession) are one picture. A
geodesic's radial motion is `(dr/dτ)² = E² − V_eff(r)` — a particle of energy E rolling in a potential, and
the engine reads V_eff off the metric (timelike `V_eff=f(1+L²/r²)`, null `f L²/r²`). **(A)** circular orbits
at V_eff′=0; the **ISCO** is where the well's min and max merge, V_eff′=V_eff″=0 ⇒ r=6M, L=2√3M — now a
*stability* statement (below 6M no stable orbit). **(B)** the **photon sphere** is the null potential's
MAXIMUM ⇒ r=3M, hence *unstable* (a knife-edge light ring). **(C)** the why: `V_eff = 1 − 2M/r + L²/r² −
2ML²/r³` — the first three terms are Newton (rest energy − potential + centrifugal barrier), the last
`−2ML²/r³` is purely GR; drop it and there's no ISCO solution. That term is exactly why you can't orbit
close to a black hole. **(D)** capture: energy above the barrier peak (null V_max=4/9 at L=2√3M) ⇒ swallowed
— the barrier sets the capture cross-section / shadow (§45). Repro: `scripts/66_effective_potential.py`.

## §67 — gravitational lensing & Einstein rings: what bending makes you see
§49 gave the bending angle; this is the observable it produces — the basis of dark-matter mapping and
microlensing planet searches. With the weak-field deflection α=4M/b (§49) and the thin-lens geometry, the
lens equation is `β = θ − θ_E²/θ` with the Einstein radius `θ_E² = 4M·D_LS/(D_L D_S)`. **(A)** perfect
alignment (β=0) ⇒ a full **Einstein ring** at θ_E; **(B)** off-axis ⇒ **two images** θ_±=(β±√(β²+4θ_E²))/2,
one each side; **(C)** total magnification `μ(u)=(u²+2)/(u√(u²+4))` (u=β/θ_E) — the microlensing light curve:
μ→∞ at u→0 (caustic spike on alignment), μ→1 for u≫1 (numeric-checked; sympy won't crack √(u⁴+8u²+16)=u²+4,
cf. §50); **(D)** θ_E ∝ √M — lensing weighs mass it cannot see. Repro: `scripts/67_lensing.py`.

**Where the niche stands (own literature sweep, 2026-06-16).** Path 1 (automate
the physical-vs-gauge / SPSM criterion) is closed: xCPS (arXiv:2606.05204, open
source) already automates covariant phase space, Noether charges, and Wald
entropy from a generic Lagrangian — so don't build it. The nearest neighbour to
this engine is AInstein (arXiv:2502.13043, Oct 2025), which finds Einstein
metrics via ML but **numerically** (Euclidean, approximate). The differentiator
is therefore sharp: this engine is **exact, symbolic, and proven** — and now
spans vacuum→matter in both discovery and proof. A genuinely-new exact metric
remains the hard standing problem for everyone and is explicitly not claimed (D26).
