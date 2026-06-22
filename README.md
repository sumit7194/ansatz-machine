# Ansatz Machine

*A propose → verify → evolve loop hunting for new exact solutions of Einstein's
field equations. Genetic programming proposes metrics, SymPy proves them —
theorem or nothing — and curvature-invariant fingerprints unmask century-old
solutions in disguise.*

## Quickstart

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./verify.sh          # runs every battery: verifier (incl. Kerr), fingerprints,
                     # blind rediscovery, discovery campaign, catalog growth,
                     # two-function hall. All must end green.
```

Requires Python ≥ 3.12 and exactly one dependency (SymPy). Everything runs on a
laptop CPU in minutes; no GPU, no API, no LLM.

**Docs:** [RESULTS.md](RESULTS.md) (lab notebook — measured results, failure→fix
tables) · [docs/JOURNAL.md](docs/JOURNAL.md) (dated activity log) ·
[docs/DECISIONS.md](docs/DECISIONS.md) (design rules and what bought them) ·
[docs/GLOSSARY.md](docs/GLOSSARY.md) (the vocabulary, CS-framed) ·
[docs/ROADMAP.md](docs/ROADMAP.md) (what's next, ranked).

---

## 1. The idea in one paragraph

Einstein's equation is a balance: geometry on one side, matter on the other. A
"solution" is a metric — the rulebook for how distances and clock rates vary from
place to place — that balances the equation everywhere, *exactly*. These are rare
treasures, found historically by humans guessing a simplifying ansatz. But the
checking part is pure algebra: a computer can verify a candidate metric
mechanically, and a verified solution is **true the moment the algebra says so** —
no experiment, no peer review needed for the math itself. So we build a loop:
something cheap proposes candidate metrics, SymPy reduces and verifies them, a
fingerprint check catches known solutions in disguise, and an evolutionary outer
loop keeps the near-misses and mutates them. The verifier is mathematics itself.

**CS framing:** it's fuzzing, but the target is the universe's field equations and
the sanitizer is symbolic algebra. Or: property-based testing where a "pass" is a
publishable theorem.

---

## 2. Why solutions are rare (the verified history)

- **The equations.** The metric in 3+1 dimensions is a symmetric 4×4 tensor, so the
  Einstein field equations are **10 coupled nonlinear PDEs** (n(n+1)/2 for n
  spacetime dimensions: 6 in 2+1, 10 in 3+1, 15 in 4+1). The contracted Bianchi
  identities make only 10 − 4 = 6 truly independent — the other 4 are coordinate
  (gauge) freedom. Expanded in a general metric, the 10 equations have *thousands
  of terms each* (MacCallum, [gr-qc/0601102](https://arxiv.org/abs/gr-qc/0601102)).
- **Schwarzschild, December 1915.** Karl Schwarzschild found the first non-trivial
  exact solution within weeks of Einstein publishing the theory, communicated in a
  letter to Einstein dated 22 Dec 1915, presented to the Prussian Academy 13 Jan
  1916 — derived while serving on the WWI Russian front
  ([history survey](https://arxiv.org/abs/2312.01865)). (Pedantic but honest:
  calling it "the first black-hole solution" is anachronistic — the horizon
  interpretation came decades later, the term "black hole" only ~1967.)
- **Kerr, 1963.** The spinning generalization took **47 more years**: R. P. Kerr,
  Phys. Rev. Lett. **11**, 237 (1 Sept 1963)
  ([APS](https://link.aps.org/doi/10.1103/PhysRevLett.11.237)). Found not by a
  metric-symmetry guess but by an *algebraic* ansatz (Petrov type D / algebraically
  special Weyl tensor).
- **How every solution was found.** "Only some special solutions can be found,
  principally those with some special symmetry or algebraic property" — MacCallum,
  co-author of the canonical catalog. Nearly every known solution came from an
  ansatz: spacetime symmetry, algebraic specialness, or a restricted metric form.
  (One honest counterexample: the Szekeres dust solutions (1975) have *no Killing
  vectors at all* — but they too came from a restricted coordinate-form ansatz.
  Solution-generating machinery like Belinski–Zakharov inverse scattering creates
  infinite families, but requires two commuting Killing vectors, so symmetry is
  still doing the work.)
- **The catalog.** Stephani, Kramer, MacCallum, Hoenselaers & Herlt, *Exact
  Solutions of Einstein's Field Equations*, 2nd ed., Cambridge 2003
  ([frontmatter](https://assets.cambridge.org/97805214/61368/frontmatter/9780521461368_frontmatter.pdf)).
  ~700 pages, thousands of papers surveyed; no canonical "number of solutions"
  exists. Crucially, its scope is **4D GR only** with four source types — no higher
  dimensions, no modified gravity. Those are off the map.
- **The mood of the field**, already in 1962 (Ehlers & Kundt): the main problem "is
  not to construct more but rather to understand more completely the known
  solutions." And MacCallum keeps a list of the *ten most commonly rediscovered
  solutions* — relativists keep "finding" Schwarzschild in funny coordinates. That
  failure mode is exactly what our novelty check (§5) exists for.

---

## 3. The loop

```
 PROPOSE ──► REDUCE ──► VERIFY ──► NOVELTY ──► (publish ✨)
    ▲          (SymPy)   (2-stage)  (invariant
    │                       │        fingerprint)
    └────── EVOLVE ◄────────┘
         keep near-misses,
         mutate, repeat
```

| Stage | What it does | Cost |
|---|---|---|
| **PROPOSE** | Emit a candidate metric ansatz (symbolic matrix). Genetic programming over expression trees, à la PySR — *no LLM/API required*. Optionally a small local model later. | ~free |
| **REDUCE** | Compute Christoffels → Riemann → Ricci → Einstein tensor for the candidate. | ms–s |
| **VERIFY** | Stage 1: numeric spot-check at random points (ms — kills almost everything). Stage 2: symbolic proof `simplify(G_ab + Λg_ab) ≡ 0` (s–min, only for survivors). | cheap → moderate |
| **NOVELTY** | Curvature-invariant fingerprint vs. the known-solution library; escalate suspicious matches. | s |
| **EVOLVE** | Fitness = smallness of the numeric residual. Near-misses breed; exact hits exit the loop. | ~free |

The economics insight (borrowed from
[FunSearch](https://www.nature.com/articles/s41586-023-06924-6) /
[AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)):
in propose-verify systems most of the win lives in the **evaluator and the
evolutionary bookkeeping**, not the proposer's IQ. AlphaEvolve confirmed the
cheap-model-for-volume + strong-model-for-quality split (Gemini 2.0 Flash for
breadth, Pro for depth); PySR ([Cranmer](https://arxiv.org/abs/2305.01582))
dispenses with language models entirely and still discovers equations. The real
cost of this project is our time, not tokens.

**Is this niche actually open?** Searched hard (June 2026; prior-art re-audited
2026-06-23): no published work has used an AI/GA/LLM loop to find a genuinely
**new exact metric**. The closest precedent — and proof the genre works — is a
March 2026 neuro-symbolic paper (Gemini Deep Think + tree search + numeric
feedback) that found novel exact analytic solutions for cosmic-string
gravitational radiation integrals
([arXiv:2603.04735](https://arxiv.org/abs/2603.04735)); the genre of GP recovering
*analytic* (not just numeric) solutions to differential equations is also
established (Oh et al. 2023). Exact GR-adjacent results from a propose-verify
pipeline — but a radiation integral, not a metric. The metric-hunting *method*
appears unclaimed — **but our actual solutions are rediscoveries, so this is a
capability demo, not a novelty pillar.** (And a 2026-06-23 re-audit overturned our
separate "rotating-EdGB gap" claim — closed-form rotating EdGB does exist; treat
all novelty claims here as provisional until re-searched.)

---

## 4. Verification: subtler than it looks ⚠️

The slogan "the verifier is mathematics itself" is true but needs three honest
footnotes — all now encoded in `scripts/01_verifier.py`:

1. **Zero-testing is literally undecidable.** Richardson's theorem (1968): deciding
   whether a symbolic expression involving exp/sin/π is identically zero is
   undecidable — proved by reduction from the **halting problem**
   ([Wikipedia](https://en.wikipedia.org/wiki/Richardson%27s_theorem)). So
   `simplify(...) != 0` never *proves* a candidate fails; it may just mean SymPy
   didn't find the cancellation. Verdicts must be **three-valued**:
   - ✅ `VERIFIED` — simplified to zero. A theorem.
   - ❌ `REJECTED` — nonzero at a numeric sample point. Definitive (up to tolerance).
   - ⚠️ `UNPROVEN` — numerically zero everywhere we look, symbolically stuck.
     A conjecture-within-the-conjecture-machine; worth human attention.
2. **Numeric-first is standard CAS practice.** Random-point evaluation
   (Schwartz–Zippel-flavored probabilistic zero-testing) is the canonical
   workaround for Richardson undecidability. Our spot-check uses exact rational
   substitutions + 30-digit evalf, and rejects in ~20 ms.
3. **Assumptions are load-bearing.** Without `positive=True` on M and r, SymPy
   correctly refuses `sqrt(x²) → x` (branch cuts), and expressions that are zero on
   the physical domain won't reduce. Also: targeted `together/cancel/trigsimp`
   beats blanket `simplify()` (a slow heuristic), and simplifying Christoffels
   *before* building Riemann prevents combinatorial expression-swell
   ([SymPy docs](https://docs.sympy.org/latest/tutorials/intro-tutorial/simplification.html)).

Tooling note: we hand-rolled the GR engine in ~100 lines of pure SymPy rather than
depend on a GR library. EinsteinPy's symbolic module is semi-dormant (last release
2021, targets Python 3.8 — we're on 3.14); OGRePy
([arXiv:2409.03803](https://arxiv.org/abs/2409.03803)) is the maintained modern
option if we ever want a cross-check. Zero black boxes between a candidate and its
verdict is worth 100 lines.

**The Kerr stress test — a measured engineering arc.** Verifying Kerr (the metric
that took humans 47 extra years) taught the engine three lessons, each bought by a
real failure:
1. Blanket `simplify()` on Kerr's full Einstein matrix ran **>12 CPU-minutes
   without terminating.** Fix: check the **Ricci form** of the field equations,
   `R_ab = [2Λ/(n−2)]g_ab` — equivalent for n>2 (take the trace), but skips the
   Ricci scalar and Einstein tensor entirely.
2. Even then, Boyer–Lindquist trig form drowned: 500 s → **UNPROVEN** (numerically
   vacuum to 10⁻¹³², symbolically stuck in sin 6θ swamps). The three-valued verdict
   doing exactly its job — Richardson's theorem in the wild.
3. The kill shot is a *coordinate choice*: substitute **u = cos θ** and every Kerr
   component becomes a **rational function** — where zero-testing is *decidable*
   (Richardson needs transcendental functions). Same spacetime: **VERIFIED in 9
   seconds.** Engine design rule, now permanent: prefer coordinates that make the
   metric rational. Undecidability is sometimes just a bad parameterization.

---

## 5. Novelty: the hard part 🔀

"Catches Schwarzschild in a funny costume" — the costume problem is real (see
MacCallum's most-rediscovered list) and harder than it sounds.

**CS framing:** two metrics related by a coordinate change are the same program
compiled with different register names. You can't diff the source; you need either
a *canonical form* or a *behavioral fingerprint*. Curvature invariants are the
fingerprint — hash functions that coordinate changes can't touch.

- **Invariants are necessary, not sufficient.** If any scalar invariant differs,
  the spacetimes are genuinely different — a clean inequivalence proof. But
  matching invariants do **not** prove equivalence. Worst case: **VSI spacetimes**
  (e.g. pp-waves), which are curved yet have *every* polynomial invariant equal to
  zero — by invariants alone, indistinguishable from flat space
  ([Coley–Hervik–Pelavas](https://arxiv.org/abs/0901.0791)). Our fingerprint filter
  is blind exactly there (Kundt-class metrics), and must say so rather than bluff.
- **Practical fingerprint set:** Ricci scalar R, Kretschmann K = R_abcd R^abcd,
  Ricci-squared, plus Carminati–McLenaghan invariants if needed
  ([CM set](https://en.wikipedia.org/wiki/Carminati%E2%80%93McLenaghan_invariants)).
  Since invariants are *functions* of position, compare functional relations
  (e.g. K as a function of areal radius), not raw expressions. Sanity anchor:
  Schwarzschild has R = 0 (useless alone!) and **K = 48M²/r⁶** — which our engine
  reproduces exactly.
- **The real equivalence test** is the **Cartan–Karlhede algorithm** (compare
  Riemann + covariant derivatives in canonically-fixed frames; decidable in ≤7
  derivative orders, usually ≤3) ([review](https://arxiv.org/abs/2007.04123)).
  Notable gap: it exists only in legacy SHEEP/CLASSI and Maple — **no Python
  implementation exists** as of mid-2026. If this project ever needs CK, building
  it would itself be a useful contribution.
- **Pipeline:** invariant fingerprint as the cheap filter → escalate fingerprint
  matches to human/CK scrutiny → fingerprint *mismatches with a verified zero
  Einstein tensor* are the treasure.

---

## 6. Where to aim (the honest risk profile)

A century of brilliant relativists strip-mined the symmetric ansatz families in
4D. Aiming the loop there means re-rediscovering catalog entries. The verified
unmined territory:

**(a) Higher dimensions** — the dimensional-ladder home game. In 4+1D the catalog
is real but thin: Myers–Perry rotating holes (1986), the Emparan–Reall **black
ring** (2002, [hep-th/0110260](https://arxiv.org/abs/hep-th/0110260)) which proved
black-hole *non-uniqueness* (same mass + spin, different topology!), Black Saturn
(2007, [hep-th/0701035](https://arxiv.org/abs/hep-th/0701035)). No uniqueness
theorem, classification of 5D stationary vacuum solutions still open, and
MacCallum: higher-D work is "for the most part still at the stage of using only
very simple metric forms." In d ≥ 6, rings/saturns are known only approximately.
✅ Our verifier is already dimension-agnostic and passed 4+1 Tangherlini.

**(b) Modified gravity** — genuinely thin. f(R) equations are fourth-order; the
Einstein-dilaton-Gauss-Bonnet black hole is known **only numerically** since 1996 —
no closed form exists even for the simplest static case. No Stephani-style catalog
exists for any modified theory. (Requires extending the verifier beyond G_ab + Λg_ab
— a later rung.)

**(c) Closed-form approximations to numerical solutions** — an established,
publishable genre: Konoplya & Zhidenko fit a continued-fraction closed form to the
numerical EdGB metric to <1% and published it in PRD
([arXiv:1706.07460](https://arxiv.org/abs/1706.07460)), explicitly usable "in the
same way as an exact solution." Different verifier (fit quality, not exact zero),
very PySR-shaped problem.

And one warm-up that ties to the ladder docs: **2+1 with Λ < 0**. Vacuum 2+1 GR has
no local degrees of freedom, yet the BTZ black hole (Bañados–Teitelboim–Zanelli
1992, [Carlip's review](https://arxiv.org/abs/gr-qc/9506079)) exists — a black hole
built by identification of AdS₃. Already in our verifier's ground-truth battery,
and the cleanest known microscopic derivation of S = A/4 lives there (the holography
thread again).

---

## 7. Ground rules (mirroring `echoes/`)

1. **Verifier before proposer.** Built and validated first — same spirit as
   "injections before search." ✅ done.
2. **Rediscovery before discovery.** Before aiming at unmined territory, the full
   loop must *re*-discover Schwarzschild from a generic static spherically
   symmetric ansatz it was never told the answer to. That's our injection test —
   if the loop can't find the thing we hid, it can't find anything.
3. **Three-valued honesty.** VERIFIED / REJECTED / UNPROVEN, never "probably fine."
4. **The fingerprint filter must declare its blind spot** (constant/vanishing
   invariants → escalate, don't conclude).
5. **Null results are results.** "The loop explored ansatz family X exhaustively
   and found nothing new" is a real finding about where solutions aren't.

---

## 8. Status & roadmap

| Step | What | Status |
|---|---|---|
| 01 | **Verifier** ([01_verifier.py](scripts/01_verifier.py), engine in [gr_engine.py](scripts/gr_engine.py)): dimension-agnostic, two-stage (numeric spot-check → symbolic proof), three-valued verdicts. Ground truth: BTZ (2+1), Schwarzschild + de Sitter (3+1), Tangherlini (4+1) ✅ VERIFIED; Kretschmann = 48M²/r⁶ reproduced; sabotaged metrics ❌ REJECTED in ~20 ms; **Kerr ✅ VERIFIED in 9 s** (rational u=cosθ form — see §4 for the arc). | ✅ |
| 02 | **Fingerprint library** ([02_fingerprints.py](scripts/02_fingerprints.py)): (K, \|∇K\|²) invariant-curve comparison with data-driven root-finding. Costume tests pass: Schwarzschild in **isotropic** and **Painlevé–Gullstrand** coordinates both unmasked with the correct mass recovered (M≈1, M≈2); Schwarzschild–de Sitter distinguished from Schwarzschild; flat space and CSI blind spots **declared**, never bluffed. | ✅ |
| 03 | **Rediscovery loop** ([03_rediscover.py](scripts/03_rediscover.py)): GP over exact-rational expression trees; full propose→reduce→verify→novelty→evolve. **Injection test PASSED**: Schwarzschild rediscovered blind in 3 generations (~6 s), BTZ in 1, Tangherlini in 2. | ✅ |
| 04 | **Campaign** ([04_campaign.py](scripts/04_campaign.py)): six rungs across the ladder, including two aimed deliberately outside the catalog to exercise the CANDIDATE_NEW pathway. Kept as the frozen *memoryless* regression — the time capsule of first discovery. Results in [RESULTS.md](RESULTS.md). | ✅ |
| 05 | **Catalog auto-growth** ([05_generalize.py](scripts/05_generalize.py)) — the machine's memory. A confirmed find gets its constants tested one by one against the full symbolic verifier: free ones are "hair" (mass), fixed ones are law (the Λ coefficient). The resulting family is proved as a theorem and persisted to `catalog_discoveries.json`; the machine never rediscovers it again. | ✅ |
| 06 | **Two-function hall** ([06_two_function.py](scripts/06_two_function.py)): ansatz −f(r)dt² + dr²/h(r) + r²dΩ² with independent genomes for f and h. Birkhoff's theorem says this hall holds nothing beyond the knowns — making it a pure honesty stress test, **passed with zero false novelty**: every hit classified as known/grown, every gauge check came out f/h = constant. | ✅ |
| 07 | Genuinely unmined territory next: stationary/off-diagonal rational forms (the Kerr lesson), modified-gravity field equations (EdGB genre), maybe an LLM proposer if GP plateaus. | ⬜ next |

Environment: `.venv` (Python ≥3.12, SymPy 1.14). Run everything: `./verify.sh`

### Lessons the machine taught us (measured, not designed)

- **The loop is lazy: it found flat space first.** `f ≡ 1` solves the vacuum
  equations perfectly, so generation 0 "discovered" Minkowski. Fix: a triviality
  penalty in fitness (numerically-constant f, catches `r/r` tricks) plus a
  Kretschmann ≡ 0 rejection at promotion. Lesson: *a verifier defines what counts
  as a solution; only a novelty layer defines what counts as a discovery.*
- **The equations don't share our taste in mass.** The GP's first Schwarzschild was
  `f = 1 + 2/r` — **negative mass**, a naked singularity, exact vacuum all the
  same. The fingerprint must match the signed-parameter branch and say so.
- **2+1 confirmed its own ladder lesson unprompted.** Every Λ<0 vacuum the loop
  finds in 2+1 is locally AdS₃ — BTZ differs only globally (no local degrees of
  freedom in 3D gravity), so the fingerprint's honest verdict there is BLIND_SPOT,
  forever. The dimensional ladder's "⚠️ degenerate" tag, rediscovered by a machine.
- **Gene duplication is real (v2).** With two independent genomes (f, h),
  per-slot crossover stagnated on every seed: a building block discovered in the
  h-slot could never reach the f-slot, and Birkhoff-type solutions need the same
  structure (same mass constant) in both. One operator — copy/graft one slot onto
  the other, then let mutations diverge them — and the hall fell in generations.
  Biology's oldest trick, rediscovered as a necessity.
- **The machine recognized its own discovery (v2).** The two-function hunt in
  (4+1, Λ<0) found `f = h = r²/6 + 1 + 8/(9r²)` and classified it against the
  family *it had itself discovered and generalized* the day before
  (`catalog_discoveries.json`). The loop is closed: discover → generalize →
  remember → recognize.

---

## What's next

Lives in [docs/ROADMAP.md](docs/ROADMAP.md), ranked. Headlines: the stationary
hall (off-diagonal g_tφ in rational coordinates — rotating BTZ first, the
Kerr-shaped mansion later), the modified-gravity REDUCE (the EdGB black hole,
known only numerically since 1996, via the closed-form-fit genre), and the
missing-from-the-world Python Cartan–Karlhede. Two early open threads were
answered by the machine itself: the 2+1 rung's permanent blind spot IS the
"no local degrees of freedom in 3D" lesson, and catalog growth went from
open thread to shipped feature (05/07).
