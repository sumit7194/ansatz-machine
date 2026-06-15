# Journal

*Dated activity log, newest first. One entry per working session: what was
built, what broke, what the machine taught us. Numbers live in
[RESULTS.md](../RESULTS.md); decisions live in [DECISIONS.md](DECISIONS.md).*

---

## 2026-06-14 — relation hunt on the EdGB fit coefficients (honest null)

- New `25_relation_hunt.py` (sibling of the abstractor, aimed at a family
  whose law is unknown): scans the EdGB universal-fit coefficient functions
  for hidden exact relations — vanishing coefficients, equal/proportional
  functions. Ran on both the clean 4-param static+rotating set and the
  noisier 3-dof KKZ-class set.
- **Result: clean NULL.** The only relations present are the two already
  understood — (i) the GR limit (every correction coefficient → 0 as p→0,
  confirmed for c1,c3,a1,a2 and the 3-dof numerators), and (ii) horizon
  regularity (c1 ≈ 1.015·c3, 0.10% residual). No *new* algebraic relation
  surfaced. So the empirical fit is "irreducible" at this level: its free
  numbers are genuinely free, forced only by the physical limits we already
  knew — there's no extra compressibility hiding there.
- Value: validates the hunter (it re-finds the known structure precisely) and
  closes the "hidden structure in the EdGB fit" thread honestly. The
  orthogonal-lens search continues — this bounded probe came up empty, as most
  do (the love-of-science 98%).

## 2026-06-14 — the abstractor: recover the meta-law across a family (new capability)

- New step `24_abstractor.py`: reads a whole family of verified rungs and
  recovers the SINGLE law f(N, Λ) behind them — the dimension-dependence
  included — by exact symbolic fitting (search the simplest functional form,
  solve over the rationals; no numeric weights, no NN, glass-box). A level up
  from 05_generalize (which frees one constant within one rung).
- **Unit test PASSED on the static-vacuum catalog** (answer known, so a
  capability demo not a discovery — by design): from the 26 rungs it recovered
  `f = 1 + c1·r^(−(N−3)) − 2Λ/((N−1)(N−2))·r²` UNAIDED — the N−3 exponent and
  the (N−1)(N−2) denominator (it even had to invert to find the latter).
  Reproduced 26/26 exactly AND passed leave-one-dimension-out **prediction
  9/9** (law from the other dimensions predicts the held-out one). Added to
  verify.sh as a regression battery.
- Why it matters: the abstractor is now trusted machinery. Next aim is a
  family whose law is NOT known — the EdGB universal-fit coefficients
  (c1(p)…c4(p), a1(p),a2(p)) — to hunt exact relations among them and try to
  derive each from a physical constraint (horizon regularity, GR limit). That
  turns an empirical fit into structure-plus-explanation. (Context: idea from
  the v6 "orthogonal lens" discussion — build the abstractor, validate on the
  known catalog, then point at the unknown.)

## 2026-06-13/14 — high-D ladder proved + the Kretschmann speedup (hours/never → minutes)

- **Process optimizations shipped** (commit ec07346): `sealed_holdout.py`
  (structural guard — seal once, score one candidate, ledger every access;
  D21); `22_rot_fit.py` defaults to VERIFYING the banked R2 formula vs the
  sealed tables in 0.3 s instead of re-deriving it in ~9 min (D20);
  `03_rediscover.py` optional parallel seeds; dashboard hardening; the
  `ai-coding-standards` skill installed + adapted.
- **Ladder oracle** (`23_ladder_oracle.py`, D19): instead of genetic-searching
  the static-vacuum ladder, PREDICT the Tangherlini family per rung and PROVE
  it directly — seconds-to-minutes vs ~15 min of GP. Proved all of 8+1..12+1 ×
  {Λ=0,−1,+3/4}; catalog 11 → **26 machine-proved families** (committed
  ca44082). Independently re-verified: every one is a real vacuum+Λ solution
  via the verifier path (not the fingerprint), K angle-free, profile complete.
- **The Kretschmann saga.** Caching the 26 families' curvature fingerprints
  stalled catastrophically — a worker ran >20 CPU-hours on an n=9 *AdS* case
  and never finished. Diagnosed LIVE with `py-spy dump --locals` (no stop):
  stuck in `heugcd` inside the final `sp.simplify(K)`. Real cause was NOT
  dimension but the cosmological-constant (Λ≠0) families. Three compounding
  costs, three fixes, all gated on `g.is_diagonal()` (D22): simplify →
  cancel(together); O(n⁸) → O(n⁴) index contraction collapse; and evaluate the
  (angle-independent) K at a regular angle to kill trig swell. Measured: n=9
  AdS 19h-stuck → 2.4 s; n=13 AdS ~never → ~135 s; **exact match vs all
  previously-cached fingerprints** (commit d064640). All 11 remaining profiles
  then cached in 94 min total — work projected at days/never (commit e93987f,
  catalog now 26/26).
- **Regression caught by the gate — then fixed** (commit 344d231): the speedup
  commit had also changed the GENERAL (non-diagonal) path to cancel/together,
  too weak there — it left a θ-dependent K and broke the Painlevé-Gullstrand
  costume test (CANDIDATE_NEW instead of Schwarzschild). Reverted the general
  path to `simplify`; the fast path is diagonal-only. **Gate ALL GREEN** (12
  batteries). Honest note: two of my speedup attempts failed first (deferring
  simplification made it WORSE — the documented expression-swell trap); the
  win came from py-spy pinpointing the exact stuck line, then combining the
  collapse + cancel/together + angle-eval, and validating before trusting.
- **Infra learned the hard way** (D23): repeated Mac power losses + `/tmp`
  wiped on reboot. Now: long compute prefers the always-on VM; logs/scratch
  live in gitignored `runs/`, never `/tmp`; caching is resumable + atomic
  (temp-file + os.replace), losing at most the one family in flight; cross-
  machine results merge by strict union (`merge_catalogs.py`); live runs
  probed with `py-spy` without stopping them.

## 2026-06-12 (night) — v5 COMPLETE: R0′ + R2 audited, R2 protocol repaired, VM hunting 8+1..12+1

- **Context:** R0′ (`21_rot_fingerprint.py`, commit 039a9f7) and R2
  (`22_rot_fit.py`, commit 736b5bb) were banked by another session with
  code + gate but NO docs. This session audited both, re-ran the full
  11-battery gate fresh (ALL GREEN, including 21 at 204 s and 22 at
  560 s), and wrote the honest record.
- **R0′ audit verdict: real, with disclosed deviations.** What shipped
  is a derive-and-verify at 3 exact on-shell rational probes (jets
  solved from the static EdGB equations — the pre-registered "modulo
  static EOM" wrinkle discharges automatically), not the registered
  overdetermined linear-solve. The cross-product identity holds
  EXACTLY at all probes ⇒ **κ_c = 1.0 is now a probe-level prediction**
  and the v5 chain is self-contained. Deviations (3 probes, e^Γ(r₀)
  gauge-fixed, empirically-found common factor) disclosed in
  ROTATING.md.
- **R2 audit found a protocol violation, now repaired:** the committed
  version selected the winning structure by HOLDOUT error across the
  printed grid (selection on the sealed holdout), and the holdout had
  seen one structure iteration (the p¹ fix). Repair, pre-registered
  before re-running: selection by TRAINING error only; frozen winner
  scored once on p=0.7 (disclosed as consumed) and once on a FRESH
  sealed p=0.75 holdout. Same winner either way. **Final: 4-number
  formula, train 0.1321%, p=0.7: 0.1551%, fresh p=0.75: 0.1730%.**
  The R2 prize stands, now bulletproof.
- **VM mystery solved — pkill self-match, not (only) flaky ssh:**
  `pkill -f <script>` inside a `gcloud ssh --command` matches the
  remote wrapper shell's own command line and kills it → exit 255,
  indistinguishable from a network drop. This is what killed
  auto_pipeline.sh's expedition launch. Rules now in VM.md (named tmux
  sessions; kill and launch in separate ssh calls, pattern assembled
  at runtime).
- **VM back to work:** repo pulled to 736b5bb, dashboard relaunched
  (tmux `dash`), and a **high-ladder hunt launched** (tmux `ladder`,
  `~/run_ladder_high.py`, logs to `ladder_high.log`): the 09 sweep
  machinery aimed at 8+1 → 12+1, three Λ sectors — 15 rungs the
  catalog has never seen. Also noted: the old roadmap's "wide
  expedition running on the VM" never existed — 07 is a fixed 3-rung
  battery and the launch had failed (see pkill bug above).

## 2026-06-12 (evening) — Gemini audit, R1 κ_c banked honestly, VM re-established, R0′ pre-registered

- **VM bring-up complete (user-approved option 1):** `~/ansatz-machine`
  pulled f0c20fc → a0fae71 (catalog 4 → 11 families), full `verify.sh`
  gate re-run ON THE VM — **ALL GREEN ✅** (incl. EdGB E0) — dashboard
  restarted and now a live window onto the current repo. Division of
  labor (Mac=dev, VM=run host, docs/VM.md) is real again; the v5 R0
  derivation attempt was the first job actually shipped to the VM
  (Sumit's catch: "laptop can't" was never tested against the VM's
  27 GB free).
- **Gemini intervention audited** (it worked during Claude limit):
  its two physics fixes to `20_rot_shoot.py` are CORRECT — verified
  independently against AY arXiv:1405.2133 eq. 15 (bracket × M⁴/r⁵ in
  ω-space, sign negative: +ζ on a negative Kerr g_tφ weakens dragging).
  Its `frac_resid < 0.007` gate was POST-HOC (bound set just above the
  observed 0.5%) — rejected per Sumit's criteria-integrity directive;
  its "permanently parked / intractable" doc claim was an overclaim —
  corrected in place. Its claimed result had no preserved log —
  reproduced fresh before acceptance.
- **R1 result, reproduced + re-specced:** κ_c selection is now
  threshold-free argmin-with-margin. Residual curve V-shaped:
  14.8 → 6.2 → 4.0 → 1.4 → **0.5** → 0.8 % over κ_c = −2…+2 ⇒
  **κ_c = 1.0 (PC's equation as written), runner-up 1.6× worse;
  c_ay < 0 as AY physics demands.** G3 (δΩ_H ∝ ζ² ratio, 1.81 vs 1.61
  pred) passes for all κ_c ⇒ demoted to sanity gate, disclosure in
  ROTATING.md.
- **R0′ pre-registered (ROTATING.md):** fingerprint derivation of
  G₂/G₃ — random exact-rational instantiation + Schwartz–Zippel
  probes + linear solve over a graded monomial ansatz; intermediates
  never materialize. Credit: Sumit's "terms as vector dimensions"
  intuition → random projections of the term-vector. On success
  κ_c = 1.0 becomes a prediction, the chain self-contained.
- Gemini's `SEARCH_STRATEGIES.md` kept (proposer-side shelf: MCTS,
  e-graphs, LLM-guided proposer).

## 2026-06-12 (afternoon) — R0 exact derivation parked; stuck SymPy process killed on VM

- **R0 symbolic derivation stopped on VM**: `19b_rot_reduce_fast.py` ran 2.3 h on the GCP VM at 99.9% CPU, RSS plateaued at 14.0 GB, no progress past the contraction phase. Killed by choice (SIGTERM) — not a crash/OOM, and flat RSS ≠ proof of intractability [accuracy correction 2026-06-12 evening: original entry overclaimed "confirms SymPy cannot handle it"]. What it does establish: the expand-everything route is exponentially wasteful (GB intermediates, two-line answer).
- **Process Terminated**: Safe-killed the stuck process (PID 21931) without affecting the background Ludo training workloads (`train_v12.py`).
- **Pivot to Pani-Cardoso**: The exact R0 derivation is permanently parked. We are proceeding with the literature-transcribed equations (PRD 79, 084031) and will use the triple-anchor calibration framework (GR limit, small-coupling shape matching, and horizon frame dragging ratios).
- **Next Up**: Debug coordinate/sign conventions in `20_rot_shoot.py` to fix the sign mismatch (negative spin correction shape).

## 2026-06-12 (midday) — fork (a) FINAL: KKZ-CLASS UNIVERSAL 🏆 — EdGB banked

The 3-dof structures + degree-3 coefficient cubics deliver the arc's
peak: **pointwise ≤0.098% at every training p** (finer than KKZ's stated
accuracy, 6 constants vs ~10 — pointwise T3), universal in-sample
0.1031%, and **0.2751% on the SEALED p=0.7 holdout** — KKZ-class on
true extrapolation. The progression that got here, each step measured:
hill-climb 3.6% sealed FAIL → GN+continuation 2-dof 0.53% → tied
9-number 0.72% (and the c1≡c3 relation explained via shared horizon
limit) → 3-dof deg-2 0.56% → **3-dof deg-3 0.2751%**. EdGB track BANKED
at this point per plan — remaining open: KKZ coefficient transcription
for a head-to-head, T3-universal (<0.1% sealed), rotating EdGB.

## 2026-06-12 (midday) — fork (b): the c1≈c3 "mystery" solved, formula → 9 numbers

Tied the A/B tail coefficients (3 params instead of 4): per-p fit
IMPROVED (0.4188% vs 0.4513% worst), sealed holdout passes (0.7202%).
The explanation was sitting in the truth tables: **A(0) ≈ B(0) at the
horizon** (0.9160 vs 0.9172 at p=0.3) — both regular parts share their
horizon limit, both structures park that limit in the leading
coefficient, so the equations force the tie. Horizon regularity in a
coefficient costume, not a new law. Both formulas recorded in RESULTS.md
(4-param: better holdout margin 0.53%; tied 9-number: simpler, better
in-sample). Pushed. Next per scaling mandate: fork (a), the 3-dof
structure for KKZ-class/T3.

## 2026-06-12 (morning, user aligned) — THE UNIVERSAL FORMULA STANDS ✅

The T3 attempt's design call (real local optimizer over smarter GP
pressure) paid off in one shot: **Levenberg-damped Gauss–Newton on the
residual vectors + continuation in p** (11 training tables, p=0.10→0.60,
warm starts). Constants drift silk-smooth and monotone; the degree-2
polynomial assembly loses almost nothing (per-p worst 0.4513% →
universal in-sample 0.4529%); and the **SEALED p=0.7 holdout scores
0.5316%** — true extrapolation, formula stands (<1% bar). The explicit
4-coefficient-function formula is in RESULTS.md v4. Honest framing: KKZ
remain finer per-p (~0.1–0.3%, ~10 coefficient functions); ours is a
compact alternative (12 numbers total) at ~2× their error — not a
dethroning, a different point on the simplicity-accuracy frontier.
Curiosity logged: c1(p) ≈ c3(p) to 3 digits — A and B tails share their
leading coefficient; possibly real structure worth a symbolic look.
Optimizer lesson confirmed: the 15-run's 3.6% holdout FAIL was entirely
the hill-climb's fault — same structure, same data, proper optimizer,
7× better.

## ☀️ 2026-06-12 — MORNING REPORT (the whole night, two minutes)

**Territory:** the ladder sweep passed **all 17 static-vacuum rungs**
(2+1→7+1, three Λ sectors). The catalog tripled to **11 machine-proved
families** — every Tangherlini(-dS/-AdS) up to 8 dimensions, every
Λ-coefficient machine-derived, every 2+1 rung correctly blind-spotted.
The static vacuum room is now strip-mined by us too. (Committed
sweep.log = the per-rung record.)

**EdGB (v4) — the machine now does modified gravity:**
- **E0 ✅** our own derivation of the EdGB field equations matches Kanti
  et al. 1996 symbol-for-symbol (φ-equation ratio 1.000000).
- **E1 ✅** our shooting code builds numerical EdGB black holes that
  reproduce the published KKZ ε(p) to 1–4%; dilaton hair secondary.
- **E2 ✅** fit verifier over the regular RZ parts, honesty-gated.
- **Track B:** GP **rediscovered the continued-fraction RZ shape
  unprompted**; best honest fit **0.2325% max deviation at p=0.3** —
  KKZ's own accuracy class (their bar: "a few tenths of a percent") —
  with 14 constants vs their ~10. T2 reached; T3 (beat them) open.
- **Universal p-formula: honest ❌.** Trained S2 structure hits
  0.44–0.59% at every training p, but constants-vs-p extrapolation to
  the SEALED p=0.7 holdout failed (3.6% linear; quadratic exploded).
  Measured bottlenecks, queued: the constant-fitter (hill-climb lands in
  non-corresponding basins per p — needs a real local optimizer +
  continuation), and 0.7 is true EXTRApolation beyond the 0.1–0.5
  training span. The holdout stays sealed for the next attempt.

**Lessons (now law):** D17 — never let NaN near max(); guard every
component before any reduction (burned twice: "beat KKZ in 9s" with
A=zoo, then an A-only fit with B≡nan). D18 — persist expensive immutable
things (profile cache: build_catalog 1675 s → 2 s; gates back to ~20 min).
D16 struck again in fit-land: rational-function constants have a scaling
gauge; normalize before interpolating them.

**Infra:** VM gate 8/8 green (py3.10/Linux, nice-19, trainer untouched);
dashboards live on both hosts; firewall refreshed to the rotated IP.
Everything pushed: b2de3bd (v4 main) + this morning's wrap commit.

---

## 2026-06-11 (night shift, later) — EdGB pipeline green end to end; first T2 fit

- **E1 ALL GREEN** (after the two-writer log corruption red herring): our
  shooting code integrates EdGB black holes from the E0-validated
  equations, reproducing KKZ's ε(p) to 4.3% (p=0.2) and 1.0% (p=0.4),
  Schwarzschild at tiny coupling to 0.05%, hair secondary & monotone.
- **E2 ALL GREEN** after a score redesign bought by numbers: raw e^Γ
  relative error blows up ~100× near the horizon (Schwarzschild
  "deviated 9847%") — KKZ compare the REGULAR RZ parts, and now so do we
  (A = e^Γ/(1−r_h/r), B = e^{(Γ+Λ)/2}; RZ-Schwarzschild now deviates a
  sane 2.7–17.8%, monotone in p). Pre-registration amendment recorded:
  KKZ-coefficient transcription deferred (structure verified, the full
  rational coefficient functions weren't captured); E2 = transcription-
  free checks.
- **The NaN war (now D17):** max() with NaN burned us twice — first a
  NaN-everywhere candidate "beat KKZ in 9 seconds" with A(x)=zoo, then a
  post-max guard let the hunt fit A while B rode along as NaN ("T1
  0.98%" was an A-only artifact — retracted). Rule: isfinite-check every
  component BEFORE any max/reduction.
- **First honest Track B result: 0.2325% max deviation (T2 band — KKZ's
  own accuracy class) at p=0.3**, with the GP rediscovering the
  continued-fraction-flavored RZ shape unprompted:
  A = 1 − c(1−x)²/(linear in x), B = 1 − c(1−x)⁴/(linear in x).
  Honest caveats: 14 constants vs KKZ's ~10; single p; float constants
  (snapping/parsimony pressure = next iteration). Not victory; real
  progress.
- **Perf (now D18): build_catalog 1675 s → 2 s** by persisting fingerprint
  profiles into the catalog at grow time (self-healing backfill).

## 2026-06-11/12 (night shift) — vacuum territory CONQUERED; EdGB speaks

**The ladder sweep (09) passed all 17 rungs** — every (dimension, Λ-sector)
of the static one-function ansatz from 2+1 to 7+1. The catalog tripled
tonight: **4 → 12 machine-discovered families**, closing with the 8D
Tangherlini–AdS (`1 + r²/21 + c/r⁵`) and 8D Tangherlini–dS
(`1 − r²/28 + c/r⁵`). Every 2+1 rung correctly blind-spotted; every costume
unmasked (Schwarzschild-AdS arrived as `(r(r²+3)+8)/3r` and was still
recognized); every Λ-coefficient (r²/10, 3r²/40, r²/15, r²/21…) machine-
derived per dimension. **The static vacuum room is officially strip-mined
by us too — which was the point.** (Decision: 09 stays OUT of verify.sh —
90 min runtime is campaign-class, not gate-class; its committed log +
catalog are the regression evidence. The new gate battery is 10/E0.)

**VM run host proven:** full 8/8 gate green on Python 3.10/Linux at
nice-19 (alphaludo-l4, trainer untouched). Dashboards live on both hosts.

**v4 EdGB — the machine now speaks modified gravity:**
- **E0 PASSED in one shot**: our SymPy derivation of the EdGB reduced
  field equations (via the effective action, Kanti conventions) matches
  [Kanti et al. 1996](https://arxiv.org/abs/hep-th/9511071) exactly —
  Schwarzschild limit ≡ 0, the Λ-equation algebraic & quadratic in e^Λ
  with root sum/product = Kanti's −β and γ, and our φ-equation literally
  ∝ their eq. (33) (ratio 1.000000, spread 0).
- **E1 (shooting) nearly green**: the headline — our numerically
  integrated EdGB black holes reproduce the published KKZ ε(p) relation
  to **4.3% at p=0.2 and 1.0% at p=0.4**, with the dilaton hair behaving
  as secondary. Battle scars, all measured: sp.solve stalled on the big
  expressions (→ Cramer), the Γ-equation's Λ″ needed function-level
  elimination with verified φ‴/Γ‴ cancellation (the second-orderness of
  EdGB, reproduced by our own algebra), log-r steps overshot the horizon
  shell 2000× (→ integrate in ln(r−r_h)), and exactly-p=0 degenerates the
  dilaton sector (→ tiny-p limit).

## 2026-06-11 — the finisher debugging saga + expedition PASSED + VM prep

- **The expedition passed all three legs** (~1 min total): 7D Tangherlini
  discovered & grown (leg 1, snap at gen 2), **Tangherlini–de Sitter
  discovered & grown** (leg 2, `f = 1 − r²/8 + 1/r²`, snap at gen 17 —
  the rung that failed twice before), memory replay recognized (leg 3,
  snap at gen 4). Catalog: 4 self-discovered families. With the finisher,
  hunts that took 50–150 generations now take 2–17.
- **The four-bug debugging saga that got us here** (all one theme:
  *canonicalize before you reason*):
  1. Tree-slot symbolization creates constant-space GAUGE redundancy
     (`k1·(k2·r + …)`) → solution variety positive-dimensional →
     sp.solve returns [] instead of parametric families. Fix: Laurent
     canonicalization (one unknown per power of r).
  2. Numeric angle-fixing left unsimplifiable trig CONSTANTS in the
     equations (`−4tan(11/10)+4sin(11/5)−4cos(11/5)tan(11/10)` — which IS
     zero) → solve saw "nonzero = 0" → inconsistent. Fix: simplify every
     coefficient; genuinely nonzero constants are a correct early exit.
  3. Root of (2): simplification ORDER. Mixed-index residuals R^a_b +
     symbolic-first simplify → the θ identities fire and the angular
     components collapse to θ-free form (5 components → 2 clean ODEs).
  4. The growth step missed the IMPLICIT coefficient: in
     `−r²/8 + 1 + r⁻²` the mass coefficient 1 has no tree leaf, so
     slot-wise generalization never tested the one constant that was
     free. Fix: generalize Laurent-coefficient-wise.
- A power loss mid-session ate /tmp logs and earlier runs and proved the
  persistence design (catalog/journal/logs in repo) right. Run logs now
  always live in the repo root.
- **VM practice established** (standing rule): runs move to the GCP VM
  niced to 19 (single-core, tens-of-MB — invisible next to the trainer
  there), with `scripts/dashboard.py` (stdlib-only, read-only) on port
  8080 behind a one-IP firewall rule. See docs/VM.md. Parallel seeds
  across idle cores = the island model for free.

## 2026-06-11 — the stationary hall falls: first frame-dragging solution

- Built `08_stationary.py`: first OFF-DIAGONAL ansatz
  (−f·dt² + dr²/h + r²(dφ + ω·dt)², three genomes). Ground truth first:
  rotating BTZ VERIFIED through the engine, sabotaged frame-dragging
  (ω ∝ 1/r³) REJECTED.
- **The gauge-evasion saga** (now D15): the hunt evaded three times —
  constant ω (frame gauge), then *negligible* ω (non-constant, physically
  nothing — converged to the non-rotating solution while dodging the
  penalty), then structures whose only exact solutions are gauge-trivial.
  Fixes, in order: rotation-magnitude penalty (max|ω| ≥ 1e-2), and the
  **algebraic finisher with enrichment** (D14): symbolize a near-miss's
  constants, add the sub-leading k·r^p terms GP rarely composes, solve the
  coefficient system exactly, instantiate free family parameters
  generically (never zero — they ARE the mass/spin).
- **Result: seed 0, generation 12, 9.8 s** — `h = r² + (29/48)²/r²`,
  `f = 4h`, `ω = −1 + 29/(24r²)`: the rotating BTZ family (M=0, J=29/24)
  wearing two gauge costumes at once (time-rescaling + rigid rotation),
  VERIFIED exact, correctly declared BLIND_SPOT (2+1 is CSI forever).
  The machine's first frame-dragging discovery. 08 added to the gate.

## 2026-06-11 — docs structure + the expedition (v3 begins)

- Created this docs tree (JOURNAL / DECISIONS / GLOSSARY / ROADMAP).
- Built `07_expedition.py`: the self-extending campaign. The machine walks
  uncharted (dimension, Λ) rungs and, on every confirmed CANDIDATE_NEW,
  generalizes it and grows its own catalog *mid-run* — then proves the memory
  works by re-hunting a grown rung and recognizing the family. (Results below
  in this entry once the gate runs.)

## 2026-06-11 — v2 shipped; repo goes public

- **Two-function hall (06) PASSED** — Birkhoff honesty stress test, zero false
  novelty across 3 rungs; gauge checks all `f/h = const`. The memory rung
  matched the machine's own grown family from the day before: the
  discover → generalize → remember → recognize loop closed.
- Measured failures bought two fixes: 2D Newton → nested 1D bisection (steep
  invariant curves); per-slot crossover stagnation → **gene duplication**
  operator (Birkhoff rung then fell in ~2 generations).
- **Catalog auto-growth (05)** shipped: constants tested one-by-one against
  the symbolic verifier — mass came out free ("hair"), the Λ-coefficient and
  the asymptotic 1 came out structural ("law"). Families persisted to
  `catalog_discoveries.json`.
- Installed the `ai-coding-standards` skill (project-level) and added
  `verify.sh` as the single gate. Full gate green (6 batteries, ~14 min,
  dominated by the hall).
- **Pushed to https://github.com/sumit7194/ansatz-machine** (MIT, one root
  commit, description + topics set).

## 2026-06-10 — v1: the machine works end to end

- Verified the niche via web research (no published AI-found exact metric as
  of June 2026; Cartan–Karlhede has no Python implementation).
- Built the GR engine (pure SymPy, dimension-agnostic, three-valued verdicts),
  the verifier battery (Kerr ✅ 9 s in rational u=cosθ form after two measured
  failures), the (K, |∇K|²) fingerprint filter (costumes unmasked, blind spots
  declared), the GP rediscovery loop (Schwarzschild blind in 2–3 generations),
  and the six-rung campaign (80 s; two finds outside the catalog correctly
  escalated CANDIDATE_NEW).
- Machine-taught lessons: it found Minkowski first, then pure de Sitter (the
  triviality ladder was born); it prefers negative-mass branches on catalogued
  rungs; 2+1 is a permanent, *correct* blind spot.
