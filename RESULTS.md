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
solution but the reason. Repro: `scripts/34_hair_criterion.py`.

**Where the niche stands (own literature sweep, 2026-06-16).** Path 1 (automate
the physical-vs-gauge / SPSM criterion) is closed: xCPS (arXiv:2606.05204, open
source) already automates covariant phase space, Noether charges, and Wald
entropy from a generic Lagrangian — so don't build it. The nearest neighbour to
this engine is AInstein (arXiv:2502.13043, Oct 2025), which finds Einstein
metrics via ML but **numerically** (Euclidean, approximate). The differentiator
is therefore sharp: this engine is **exact, symbolic, and proven** — and now
spans vacuum→matter in both discovery and proof. A genuinely-new exact metric
remains the hard standing problem for everyone and is explicitly not claimed (D26).
