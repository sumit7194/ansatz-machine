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
