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
