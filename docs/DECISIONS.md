# Decisions

*ADR-lite. Every standing design rule, the measured failure that bought it,
and what it implies for new code. Supersede entries explicitly — never
silently contradict one.*

---

**D1 — Hand-rolled pure-SymPy GR engine; exactly one dependency.**
Context: EinsteinPy symbolic is semi-dormant (last release 2021, Python 3.8
era); we're on 3.14. Zero black boxes between a candidate and its verdict.
Consequence: all curvature math goes through `gr_engine.py`; adding any
package needs explicit justification.

**D2 — Verify the Ricci form, `R_ab = [2Λ/(n−2)] g_ab`, not the Einstein
tensor.** Bought by: blanket `simplify()` on Kerr's full Einstein matrix ran
>12 CPU-minutes without terminating. Equivalent for n>2 (trace), far smaller
expressions.

**D3 — Three-valued verdicts: VERIFIED / REJECTED / UNPROVEN.** Context:
Richardson's theorem — symbolic zero-testing is undecidable, so "didn't
simplify to zero" never proves "nonzero". UNPROVEN is an honest verdict, not
a failure state.

**D4 — The rational-coordinates rule.** Bought by: Kerr in Boyer–Lindquist
trig form → 500 s → UNPROVEN (sin 6θ swamps); with u = cosθ every component
is rational → VERIFIED in 9 s. Zero-testing of rational functions is
decidable. Prefer coordinates that make the metric rational; design new
ansatz halls rational from the start.

**D5 — GP constants are exact Rationals end to end.** A numeric hit is
already an exact symbolic object — promotion to theorem needs no
constant-snapping. Floats exist only at the lambdify/evaluation boundary.

**D6 — Two-stage verification: numeric spot-check (~ms) before symbolic
proof (~s–min).** Standard probabilistic zero-testing (Schwartz–Zippel
flavored) as the cheap oracle; only survivors get the expensive proof.

**D7 — The triviality ladder: flat → Λ-ground-state → known.** Bought by:
the loop "discovered" Minkowski (gen 0), then pure de Sitter. A verifier
defines solutions; only the novelty layer defines discoveries. Fitness
penalizes the maximally-symmetric member `f_vac = 1 − 2Λr²/((n−1)(n−2))`;
promotion rejects flat (K≡0) and, where mass is hunted, constant-K (CSI)
hits. Exception: 2+1, where CSI is all that locally exists — there the
declared blind spot IS the result.

**D8 — Fingerprint = invariant curves (K, |∇K|²); blind spots are DECLARED.**
Invariants are necessary, never sufficient (Cartan–Karlhede would be, but no
Python implementation exists). Matches report KNOWN_LIKELY, never "same".
Constant invariants → BLIND_SPOT; all-zero → FLAT_OR_VSI. Sample the curve
where it varies (bought by: SdS's mass term is a 1e-5 ripple on the Λ floor
at large r — random radii were hopelessly ill-conditioned).

**D9 — No Newton in the curve matcher; nested 1D bisection only.** Bought
by: on G1 ∝ p⁴(p+r³)/r²⁵ 2D Newton stalled at ~1e-6 from every start. Solve
the K-equation for the coordinate by bisection at each trial parameter;
bisect the parameter on the G1-mismatch sign change. Also: sp.nsolve's
default tolerance at high prec (~1e-34) can never be met by float64 inputs —
if nsolve is ever reintroduced, pass explicit `tol` and use ratio-form
equations.

**D10 — Gene duplication is a required operator for multi-function genomes.**
Bought by: per-slot crossover stagnated at residual ~1–3 on every
two-function seed — a building block found in the h-slot could never reach
the f-slot, and Birkhoff-type solutions need the same structure (same mass
constant) in both. Copy/graft one slot onto the other; mutations diverge
them afterwards.

**D11 — The catalog is the machine's memory; the campaign stays memoryless.**
Confirmed finds are generalized (each constant symbolized and re-proved:
free = hair, fixed = law), proved as families, persisted to
`catalog_discoveries.json` (committed — its git history is the discovery
log). `04_campaign.py` runs with `include_discoveries=False` forever: it is
the frozen v1 regression, the time capsule of first discovery.

**D12 — Evolution hygiene: stagnation cutoff + restart beats bigger budgets.**
Bought by: one seed sat at 6.8e-4 for 140 generations (2200 s). 30 flat
generations → restart with a fresh seed (campaign: 2300 s → 80 s). Islands
remain NOT implemented — add them only when a hall measurably stagnates
across all seeds (no speculative abstraction).

**D13 — Every battery is a gate, tested in both directions.** Knowns must
pass AND sabotage must fail; costumes must be unmasked AND blind spots
declared. `./verify.sh` runs all of them; no "done" claim without its fresh
output.

**D14 — The algebraic finisher: GP finds the leading structure, algebra
solves the family.** Bought by: stationary-hall hunts converged into the
right basin (residual ~5e-6) and stalled — constant-jitter is a poor local
optimizer for CORRELATED constants (J²/4 in f vs J/2 in ω). When a candidate
gets close (residual < 1e-2), symbolize every numeric constant, ENRICH each
slot with the sub-leading falloffs k·r^p (p = −1, −2) the GP rarely
composes, substitute the family into the symbolic residuals, demand each
vanish identically in r, and sp.solve the coefficient system. Free symbols
in a solution branch are FAMILY PARAMETERS (mass, spin) — instantiate them
generically (original value or ±1), never zero, or the branch collapses to
the trivial member. One snap attempt per structure signature.

**D16 — Canonicalize before you reason (the four-bug lesson).** Whenever an
expression crosses from the GP's tree world into algebra (finisher,
generalizer), rewrite it canonically first: Laurent form (one coefficient
per power of r) kills constant-space gauge redundancy AND exposes implicit
coefficients (the invisible 1 on r⁻² that slot-wise generalization missed);
mixed-index residuals R^a_b with SYMBOLIC-first simplification keep trig
constants out of equation systems (numeric-angle-first left unprovable-zero
constants that made sp.solve report consistent systems as inconsistent).
Tree-slot symbolization survives only as the fallback for genuine pole
structures.

**D17 — Never let NaN near max(); guard every part before any reduction.**
Bought twice in one night: Python's max() returns its FIRST argument when
comparisons are False, and every NaN comparison is False — so (1) a
NaN-everywhere candidate "scored" a perfect 0.0000% and `A(x)=zoo` "beat
KKZ in 9 seconds"; (2) after the first guard, max(finite, nan) inside the
two-part deviation still swallowed the nan and the hunt fitted A while B
rode along as nan. Rule: compute each component, isfinite-check each,
THEN reduce. Applies to every scorer/fitness in the repo.

**D18 — Persist what is expensive and immutable.** build_catalog recomputed
symbolic fingerprint profiles on every call: 1675 s at 12 families (n=8
Kretschmann dominates). Profiles never change once a family is proved —
they are now persisted (srepr) into catalog_discoveries.json at grow time,
with a self-healing backfill path. Measured: 1675 s → 2 s.

**D15 — Fitness must demand measurable physics, not just non-triviality.**
Bought by: the gauge-evasion catalog from the stationary hall. The loop
found, in order: (1) constant ω — pure frame gauge; (2) NEGLIGIBLE ω
(~tiny/r: non-constant, physically nothing) — converging to the
non-rotating solution while dodging the constancy penalty; (3) structures
whose only exact solutions are gauge-trivial. Penalties must bound the
MAGNITUDE of the physical effect (here: max|ω| ≥ 1e-2 at samples), and the
finisher must be able to complete structures (D14). Expect every new hall
to produce its own evasion catalog — optimization pressure finds gauge
loopholes reliably; that is data, not annoyance.

**D19 — Prove before you search (the oracle rule).** Bought by: the VM
high-ladder hunt was spending ~12–17 min of genetic search per rung on
8+1..12+1 static vacuum — rungs whose answer is predictable from one
pattern (the Tangherlini family). The verifier can PROVE the predicted
family for a rung in seconds-to-a-minute (scripts/23_ladder_oracle.py),
and the proof is the identical theorem the hunt would have produced.
Rule: when a hall's outcome is predictable, prove the prediction first;
spend search compute only where predictions fail or don't exist. The
search machinery's job shifts to blind CROSS-CHECKS of oracle claims
(memoryless hunt, graded against the proved family — a mismatch would
be the discovery).

**D20 — Regression batteries verify the banked artifact; they never
re-derive it.** Bought by: battery 22 re-ran the full R2 grid search
(~9 min) on every gate run — slow, and a silent re-fit could drift from
the published formula without anyone noticing. Now the winning
coefficients are FROZEN in the script and the battery just re-scores
them against the stored truth tables (0.3 s, deterministic, asserts the
recorded numbers). Re-derivation lives behind --refit. Batteries that
genuinely re-verify mathematics from scratch (01, 10, 21) are exempt —
re-deriving IS their job.

**D21 — Sealed-holdout access goes through the ledger.** Bought by: two
criteria-integrity violations in two days (the Gemini post-hoc
threshold; R2's selection-by-holdout), both caught only by human audit.
scripts/sealed_holdout.py now enforces the protocol structurally: truth
data is sealed once; the first candidate scored is locked in; scoring a
different candidate raises unless an override REASON is recorded
forever in the .ledger.json next to the truth file. Audits are the last
line of defense, not the only one.

**D22 — Diagonal metrics get a fast Kretschmann path; the general path keeps
`simplify`.** Bought by: caching curvature fingerprints for the high-dimension
catalog families stalled catastrophically — an n=9 AdS (Λ≠0) case ran >20
CPU-hours unfinished, diagnosed live with `py-spy` as stuck in `heugcd` inside
the final `sp.simplify(K)`. Three compounding costs, three fixes, all gated on
`g.is_diagonal()` (every `build_ansatz_metric` metric is diagonal):
(1) final reduction `simplify(K)` → `cancel(together(K))` — `simplify` drowns
in multivariate-GCD blowup on Λ≠0 families; cancel/together gives the identical
rational function in well under a second;
(2) index contraction O(n⁸) → O(n⁴) — for a diagonal metric only the
p=a,q=b,r=c,s=d term of the raise-all-indices sum survives;
(3) angular swell — K is angle-independent (spherical symmetry), so evaluate
the angles at a real regular point (`atan(3/4)`: all trig nonzero rational)
before reducing, leaving K(r). Measured: n=9 AdS 19h-stuck → 2.4s; n=13 AdS
~never → ~135s; exact match vs all previously-cached fingerprints. CRUCIAL
SCOPE (regression caught by gate battery 02, then fixed): the general
(non-diagonal) path — Painlevé-Gullstrand, Kerr — KEEPS full `simplify(K)`;
cancel/together is too weak there (left a θ-dependent K, breaking the P-G
costume test). Non-diagonal metrics are rare and small, so `simplify` is
affordable; the fast path is diagonal-only. Lesson echoed: targeted reduction
beats blanket simplify (D2/D4), but only where the structure (diagonality)
guarantees it's sufficient.

**D23 — Long compute lives on the always-on host; logs persist, never `/tmp`.**
Bought by: repeated power losses on the Mac dev box wiped in-flight multi-hour
runs, AND `/tmp` getting cleared on reboot left dangling log symlinks that
crashed the dashboard. Consequences: (a) profile caching / long grinds default
to the VM (cloud, no power loss) when they can't finish inside the Mac's
uptime — though once the D22 fix made caching minutes-not-hours this mattered
less; (b) run logs and ad-hoc scripts go in the gitignored `runs/` dir (or repo
root), never `/tmp`; (c) the caching itself is resumable + atomic-write
(temp-file + os.replace) so a power loss costs at most the one family in
flight; (d) cross-machine results merge by strict union (`merge_catalogs.py`)
so two machines can never erase each other's work. Live process state can be
probed without stopping a run via `py-spy dump --pid <pid> --locals` (sampling;
pauses only milliseconds).

**D24 — The information/hair meter is three-valued; it says UNKNOWN rather
than over-count.** Bought by an external-session code review (2026-06-15): the
meter's failure mode was to OVER-report — empty/un-extractable constraints →
"all free", a swallowed solve() exception → constant lands in the free pile,
an unreduced transcendental → Poly throws → silent max count. For a
null-/count-measuring instrument that is the one fatal direction. Now (26, 29):
a residual that won't reduce to a clean polynomial in r (log/exp/Abs/re/im/
Piecewise, fractional power, or stray symbol) ⇒ return UNKNOWN with a declared
blind spot; a solve() that ERRORS ⇒ UNKNOWN (not freedom). Certified
adversarially: a fractional-power residual and a log(r) residual both read
UNKNOWN, while RN reads 2 and GHS reads 2-free-+-secondary. Same three-valued
honesty the verifier (D3) and fingerprint already obey. NOTE: the meter counts
free constants up to GAUGE — it does not yet mod out coordinate redundancy;
treat a "free" count as an upper bound on physical hair until gauge-fixed.
