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
Invariants are necessary, never sufficient (Cartan–Karlhede is). Matches report
KNOWN_LIKELY, never "same". SUPERSEDED IN PART (2026-07-22): CK is now implemented
(scripts/ck.py, §116–§118) and §118 escalates these verdicts to PROVEN_KNOWN /
PROVEN_NEW_vs_CATALOG; the fingerprint remains the cheap first-pass filter.
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

**D25 — The meter measures EOM-independence *modulo gauge*, NOT physical-vs-
redundant; declare the blind spot.** Bought by an external literature review
(2026-06-15): the hair/parameter-counting lens is a mature field, and the
finer question — is a free constant a PHYSICAL charge, a GAUGE/moduli
redundancy, or a residual-symmetry charge, and does it enter the first law —
is formalized with an algorithm (Hajian–Sheikh-Jabbari, arXiv:1612.09279,
"Redundant and Physical Black Hole Parameters"). Our meter answers only the
COARSE question ("is X fixed by the field equations?"). It therefore (a)
conflates gauge-redundant with EOM-secondary, and (b) is BLIND to
symmetry-removable parameters that are not EOM-constrained — the canonical
case being the asymptotic dilaton value φ₀, redundant by shift symmetry, which
the meter would wrongly call free. Consequence: a meter "free" count is an
UPPER BOUND on physical hair, declared as such; the physical-vs-gauge
classification (the SPSM integrability/first-law criterion) is not implemented
and is the only thing that would make the meter a genuine methods contribution
rather than a coarse automation. Steer AWAY from hand-discovering new
primary/secondary hair (the crowded 2024–25 Beyond-Horndeski / Proca-GB /
Lovelock-Proca race). The exact-metric DISCOVERY loop (the original engine) is plausibly
unclaimed as a METHOD (GP/symbolic-regression aimed at the Einstein
equations; genre precedent Oh et al. 2023, which recovered analytic ODE
solutions) — but since our solutions are REDISCOVERIES, it is a capability
demo, not a novelty pillar. (Caveat added 2026-06-23: "per all searches"
proved over-confident — a proper search overturned the rotating-EdGB
"unclaimed gap" claim; treat all such novelty claims as provisional.)

**D26 — The build phase is complete; the contribution is the glass-box
discover-AND-prove engine spanning vacuum→matter. Stop adding source rungs.**
Bought by: my own literature sweep (2026-06-16) confirming the external
session's verdict twice over — (a) xCPS (arXiv:2606.05204, open source)
automates covariant phase space / Noether charges / Wald entropy from a generic
Lagrangian, so the SPSM physical-vs-gauge tooling (Path 1) is genuinely closed
— do NOT build it; (b) the nearest neighbour to our loop is AInstein
(arXiv:2502.13043, Oct 2025), which finds Einstein metrics via ML but
NUMERICALLY (Euclidean, approximate) — so our differentiator is sharp and
defensible: EXACT, symbolic, PROVEN metrics; proof is the moat. Consequence:
the engine now demonstrably spans the field menu in both directions — vacuum
rediscovery+generalization (Schwarzschild→Tangherlini→26-family meta-law),
matter discovery (RN, `31`, GAINS a charge term), secondary-hair reading (GHS
dilaton, `30`), and theorem-rediscovery (no-hair, `32`, PROVES a term is
forbidden). That is a complete, honest, self-contained body of work. Further
source rungs (Proca, Yang-Mills, higher-D charged) would only restate the same
capability, so the build phase STOPS here; the next move is consolidation /
write-up with the AInstein-differentiated framing, not more rungs. A
genuinely-new exact metric remains the hard standing problem for everyone and
is explicitly NOT claimed.

**D27 — Add `qnm` (numpy/scipy/numba) as an OPTIONAL dependency for the
precise-QNM track only; the pure-SymPy core stays one-dependency.** Bought by:
the bridge review's highest-leverage item (ROADMAP §v8.1) — §56's QNM is exact
but eikonal (few-to-15% on the ringdown), and a PRECISE QNM is inherently
NUMERICAL (Leaver's continued fraction has no closed form), which is the actual
quantity deepstrain's δ measures (incl. the 221 overtone). The standing
constraint allows a new dependency if justified here first; this is that
justification. Containment: only `scripts/qnm_precise.py` + battery `77` import
`qnm`; nothing in the 76-battery pure-SymPy core touches it, the analyzer stays
pure, and battery 77 fail-soft SKIPS (clearly, exit 0) when `qnm` is absent so a
fresh checkout's gate is unaffected. So the "exact, symbolic, proven" identity
is intact for the core; the precise QNM is an explicitly-numerical companion
oracle (like the finite-difference `numeric_curvature.py`, but with the standard
peer-reviewed tool rather than a hand roll). Validated: Schwarzschild ℓ=2,n=0 =
0.37367−0.08896i (exact Leaver), the 221 overtone available — battery 77.

---

**D28 — P0 primary gate: MISSED. Recorded as missed; the bar is not restated.**

*The gate, as frozen before running (verbatim):* §122 completes its full catalog
**including Kerr a=1/2 and Taub–NUT**, unbudgeted, in under **60 minutes**
wall-clock on this machine, all G6 verdicts green, no section reporting
RESOURCE-WALLED. Binary, and explicitly *"not gameable by relaxing a threshold."*

*The pre-registered NULL:* "the wall is not crossable by normalisation; order-2
CK on rotating metrics requires a GHP-style representation change."

**VERDICT: MISSED.** Measured, 2026-08-16:

    Kerr a=1/2, full order-2 signature   3,501.2 s = 58.4 min   (first ever completion)
    Schwarzschild M=1                          32 s
    Schwarzschild M=2                          32 s
    ZV delta=1                                 37 s
                                             --------
    Kerr + statics                          60.1 min   -- past the bar already

**FACTOR, completed 2026-08-20** once Taub-NUT was fixed and could be measured at
all (it had never completed; see the journal for the two bugs that prevented it):

    Kerr a=1/2      3,501.2 s          Taub-NUT n=1/2      62.8 s
    statics (3)       101   s          isotropic chart   RESOURCE-WALL (see below)
                                       ---------------------------------
    Kerr + Taub-NUT + statics        =  61.1 min   -> MISSED by 1.02x
    with the isotropic chart         >  78    min  -> MISSED by >1.3x

The isotropic chart -- the SAME spacetime as Schwarzschild M=1, which costs 32 s --
ran 19+ minutes at 4.4 GB RSS with swap climbing, i.e. it resource-walls. The gate
also required "no section reporting RESOURCE-WALLED", so that clause fails
independently of the clock.

**THE NULL IS REFUTED, and that is the actual result.** Normalisation crossed the
wall: 29-87x on one frame contraction, 58x on `cartan_order1` (4,187.68 s ->
71.80 s), a signature that had never finished in three attempts (longest 6h11m
with ZERO of Kerr's 16 components done) -> 58.4 min. All six frozen batteries
(§116-§121) re-run verdict-identical. No representation change was needed.

**Why the bar is not being restated**, recorded because the temptation was real
and the miss is thin: 60 minutes was a guess made when the honest state of
knowledge was "this has never completed." A guess that turns out to be ~1x off is
a badly-calibrated bar, not a failed programme -- and the way to say that is to
report the miss AND the factor, not to move the bar so the sentence reads better.
Precedent: S3's gate was unreachable by construction, its postulate was supported,
the frozen bar was not met, and it was not relabelled.

Consequence for new code: a pre-registered gate is FROZEN once running starts.
If it turns out to have been set without knowing the size of the thing it
measures, that fact is reported next to the verdict -- it is never used to adjust
the verdict. See also the rule this day bought twice over: **every pre-registered
criterion needs a known-PASS and a known-FAIL before it gates anything** (our
"bit-identical" clause had no known-pass on output containing timestamps and
nearly forced a revert of a correct 87x fix).

---

**D29 — P0 primary gate: PASSED on re-evaluation (2026-08-20). D28's MISSED stands.**

*Same frozen criterion, second evaluation, after four wall fixes. This is NOT a
retroactive pass and D28 is NOT edited: on 2026-08-19 the gate was measured and
MISSED by 1.02x with the code as it then stood, and that remains true of that
code. What changed is the code, not the bar.*

**COLD RUN, cache directory emptied first so "cold" does not rest on hash
arithmetic** (`data/s122_cold.out`, 2026-08-20 15:04-15:58):

    Schwarzschild M=1                   32 s
    Schwarzschild M=2                   33 s
    Schwarzschild (isotropic chart)     18 s     <- was >8 h, never completed
    ZV delta=1 (prolate spheroidal)     36 s
    Taub-NUT n=1/2                      64 s     <- had NEVER completed
    Kerr a=1/2                       3,064 s     <- was 3,501 s
                                    ---------
    TOTAL WALL-CLOCK              3,248.76 s  =  54.15 min      (bar: 60 min)

Every clause checked separately, not inferred from the headline:
  1. full catalog incl. Kerr AND Taub-NUT ... 6/6 metrics computed
  2. unbudgeted .......................... "3248s of unlimited budget"
  3. under 60 minutes wall-clock ......... 54.15 min
  4. all G6 verdicts green ............... SUPPORTED, 6/6, every ck_order = 2
  5. no section RESOURCE-WALLED .......... 0 occurrences

**The pre-registered NULL remains REFUTED, and more strongly than in D28:** the
null said order-2 CK on rotating metrics "requires a GHP-style representation
change". Four walls were crossed without one -- all four were a normalizer handed
an input it could not cope with, and in three of the four the expensive work was
provably unnecessary (expand() inflating 3,710 ops to 90,841 so cancel could undo
it; refine() on an expression with nothing refinable in it; refine() walking a
whole tree to do node-local rewrites). The fourth was not a performance problem
at all -- the Taub-NUT entry was a WRONG METRIC that was not even a vacuum
solution, and its nine-hour hang was hiding that.

Consequence for new code, and the reason both entries stay: a frozen gate is
evaluated against the code AS IT STANDS, and a later evaluation is a NEW dated
result rather than a correction of the old one. Had the bar been restated on
2026-08-19 when it was 66 seconds over, yesterday's MISSED would have vanished --
and with it the record that four real bugs were sitting behind it.

## D30 — the reducible span becomes a measurement, and rank 6 becomes a pre-registered test (2026-08-21)

**What happened.** The δ=1 rank-5 prover returned DIMENSION 14 against a hand-counted reducible span
of 10. Subtracted the way every previous rung was subtracted, that reads **four irreducible Killing
tensors on Schwarzschild** — integrable since 1916. The prover was right; the hand-count was wrong.

**Why the hand-count was wrong, and it is not the failure we already catalogued.** The table
`{1:2, 2:4, 3:6, 4:8, 5:10, 6:13}` was **substrate-independent when the answer is substrate-dependent**.
It is correct for δ=2 at ranks 1–5. It is wrong for δ=1 from rank 2 onward, because δ=1 *is*
Schwarzschild and carries an extra conserved quantity, L². And L² is invisible where we looked for
generators: its building blocks L_x, L_y are **not axisymmetric**, so they are absent from the rank-1
ansatz and the prover correctly reports rank-1 dimension 2 — while **L² itself is axisymmetric** and
sits in rank 2 as an honest solution. *A generator can be invisible at its own rank and present at
twice it.* The undercount then compounds with every rank, which is why ranks 2 and 3 agreed and
rank 5 blew open. The sharpest form: **the δ=1 control's extra symmetry is exactly what a shared
table cannot express, and the control was built to be the trustworthy arm.**

**Why no existing guard caught it.** Our free structural check is `dim(reducible) ≤ dim(solution)`,
an impossibility that cannot fail. It catches an ansatz too small to hold its own reducibles. It is
**blind to a reducible count that is too small**, because undercounting keeps the inequality
satisfied and moves the surplus into the "irreducible" column. Opposite errors; only one has a free
guard, and the blind one relabels an accounting error **as a discovery**.

**Decision 1 — the reducible span is now measured by committed code**, `scripts/_kt_reducible.py`,
never hand-counted. Generators are validated by exact `{H,g} = 0` with a known-FAIL (`p_t² p_x p_y`,
correctly rejected), and the generator set is only accepted when the resulting counts reproduce
independently measured prover dimensions at three or more low ranks. The wrong table is deleted from
`_kt_zv_high.py` rather than left printing beside a correct number.

**Decision 2 — the comparison is made in the SAME space.** The prover's solution space is
`(bounded-degree polynomial)/L` — one power of the denominator. The reducible span is a fact about
the spacetime and knows nothing about L. So the honest quantity is
**dim(reducible AND den¹-representable)**, computed by construction per product, with every excluded
product named. Measured:

    δ=1   rank 1:  2 of  2      δ=2   rank 1:  2 of  2
          rank 2:  5 of  5            rank 2:  4 of  4
          rank 3:  8 of  8            rank 3:  6 of  6
          rank 4: 11 of 14            rank 4:  8 of  9   (drops H²)
          rank 5: 14 of 20            rank 5: 10 of 12
          rank 6: 17 of 30            rank 6: 12 of 16

Every product dropped contains **two or more degree-2 generators**, which carries L² past a den¹
ansatz. Against the prover: δ=1 ranks 1,2,3,4,5 = 2, 5, 8, 11, 14 and δ=1 representable =
2, 5, 8, 11, 14. δ=2 ranks 1,2,3,4 = 2, 4, 6, 8 and δ=2 representable = 2, 4, 6, 8. **Ten exact
agreements, no residual. Irreducible count is 0 at every rank measured so far, on both arms.**

**Decision 3 — PRE-REGISTERED, recorded before the runs land.** The den¹ representability count is
a *prediction* of what the prover must return:

    δ=2 rank 5  ->  10        (in flight at the time of writing, 20/147 points)
    δ=1 rank 6  ->  17
    δ=2 rank 6  ->  12

**Known-FAIL: any value other than these.** A number above the prediction is an irreducible tensor
and the headline result of this project; a number below it violates
`dim(reducible ∩ ansatz) ≤ dim(solution)` and condemns the ansatz. Either outcome is informative,
which is what makes rank 6 worth its ~5.6 h — it is no longer a box to tick. Note the earlier
hand-count also had δ=2 rank 6 at **13**, against a measured 12; that error was independent of the
δ=1 one and would have manufactured a spurious irreducible tensor there too.

**Standing rule adopted.** *If a claim is a difference of two numbers, both terms need the same
evidentiary standard, and the one that feels too obvious to script is the one to script.* Here the
first term was measured over GF(p), checkpointed and versioned; the second lived in throwaway
heredocs and was wrong four times.

## D31 — the first pre-registered prediction lands (2026-08-21, δ=1 rank 6)

**Predicted 17 in `0bddd58`, before the run started. Measured 17, on both primes.**

    mod 2147483647: rank 3511 -> nullspace dimension 17
    mod 2147483629: rank 3511 -> nullspace dimension 17
    ZV delta=1 RANK 6: DIMENSION 17   [815s]

The prediction was not a guess with a margin — it was the count of degree-6 products of the
measured generators `{p_t, p_φ, H, L²}` that a den¹ ansatz can represent: **17 of 30**, with the
13 excluded products named individually, every one containing two or more degree-2 generators.
A den² object cannot be held by a den¹ ansatz, so those 13 *must* be absent, and 17 *must* be what
the prover returns if there is no irreducible tensor. It returned 17.

**Why this is a different kind of evidence from the ten agreements that preceded it.** Those were
retrodictions: measured after the prover's number was known, and although the arithmetic was
independent, nothing stopped a wrong generator set from being tuned until it matched. This one was
**committed to disk, with a known-FAIL in both directions, before the run existed** — any value
above 17 is an irreducible Killing tensor and this project's headline; any value below violates
`dim(reducible ∩ ansatz) ≤ dim(solution)` and condemns the ansatz. The prediction had somewhere to
fail and did not.

**δ=1 (Schwarzschild, in prolate spheroidal coordinates, den¹ scope) now closes at ranks 1–6:**

    rank    1   2   3   4    5    6
    prover  2   5   8  11   14   17
    repr.   2   5   8  11   14   17
    irred.  0   0   0   0    0    0

Still open at the time of writing: δ=2 rank 5 (predicted 10) and δ=2 rank 6 (predicted 12).

## D32 — second pre-registered prediction lands (2026-08-21, δ=2 rank 5)

**Predicted 10 in `0bddd58`. Measured 10, on both primes.**

    mod 2147483647: rank 7998 -> nullspace dimension 10
    mod 2147483629: rank 7998 -> nullspace dimension 10
    ZV delta=2 RANK 5: DIMENSION 10   [5604s]

Representable reducible products at δ=2 rank 5: **10 of 12** (dropping `p_φ·H²` and `p_t·H²`, both
carrying L²), independent rank **10**. So irreducible = 0, and the **deformed vacuum** arm now closes
at ranks 1–5.

**One artifact in that output needs its provenance stated, because it is misleading and it is our own
rule 17.** The run printed a trailing line:

    hand-count of reducibles at this rank: 10  (MUST be measured before it is believed)

That line was **deleted from `_kt_zv_high.py` in `0bddd58`**, hours before this result landed. The
process had loaded the old code at launch and kept printing it — *don't edit code while a run using
it is in flight*, and the consequence here is cosmetic rather than corrupting. **It agrees with the
measurement (10) only because the old table happened to be correct for δ=2 at ranks 1–5** — it is
wrong for δ=1 from rank 2 on, and wrong for δ=2 at rank 6 (13 against a measured 12). Anyone reading
`data/kt_zvh_d2_r5.out` later should treat that line as a fossil of pre-`0bddd58` code, not as a
concurring source. The δ=2 rank-6 run, launched after the patch, does not print it.

**Standing after this:**

    δ=1   ranks 1-6 CLOSED    2, 5, 8, 11, 14, 17   irreducible 0 at every rank
    δ=2   ranks 1-5 CLOSED    2, 4, 6,  8, 10       irreducible 0 at every rank
    δ=2   rank 6 running, pre-registered 12, 70/154 points

Two pre-registered predictions made, two held. Both had a known-FAIL in each direction.

## D33 — third pre-registered prediction lands; ZV closed at ranks 1–6 on both arms (2026-08-22)

**Predicted 12 in `0bddd58`. Measured 12, on both primes.**

    mod 2147483647: rank 12000 -> nullspace dimension 12
    mod 2147483629: rank 12000 -> nullspace dimension 12
    ZV delta=2 RANK 6: DIMENSION 12   [11472s, 18480 rows, 12012 unknowns]

**FINAL STANDING — Zipoy-Voorhees, an exact vacuum solution, closed at momentum-ranks 1 through 6
on both arms:**

    rank                     1    2    3    4    5    6
    δ=1  prover              2    5    8   11   14   17
         representable       2    5    8   11   14   17
         independent rank    2    5    8   11   14   17
         IRREDUCIBLE         0    0    0    0    0    0

    δ=2  prover              2    4    6    8   10   12
         representable       2    4    6    8   10   12
         independent rank    2    4    6    8   10   12
         IRREDUCIBLE         0    0    0    0    0    0

**Twelve exact agreements. Three of them were pre-registered with a known-FAIL in both directions**
(δ=1 rank 6 → 17, δ=2 rank 5 → 10, δ=2 rank 6 → 12), all committed at 23:42 on 2026-08-21 before
any of the three runs had produced a result. **Three predictions made, three held.**

**The distinction that matters and that we are keeping in the record:** nine of the twelve are
**retrodictions** — the arithmetic was independent of the prover, but nothing structurally prevented
a wrong generator set from being tuned until it matched. The three pre-registered ones had somewhere
to fail. A fourth kind of evidence is stronger still and is not ours: the bridge's numerical
conservation screen returned **5 at δ=1 and 4 at δ=2 at momentum-degree 2**, on an instrument with
**no denominator scope at all**, confirming the one place our prover is blind rather than negative.

**Scope, unchanged and stated plainly.** This is den¹. Products carrying L² (H², H·L², L⁴ and their
multiples) fall outside the ansatz on **both** sides of the subtraction and are excluded from both,
by construction and by name — 13 of 30 at δ=1 rank 6, 4 of 16 at δ=2 rank 6. Widening to den² is
open; the bridge's degree-4 screen at den² is **coverage-limited, not representation-limited**
(basis rank rising 413 → 666 → 974 with orbit count) and therefore open rather than negative.
**Nothing bounds the rank** — the grading theorem gives rung independence and finiteness of each
rung, not of the ladder. So this extends §98's map; it does not close the question behind it.

## D34 — den² ladder: scope written FIRST, then predictions, then the runs (2026-08-22)

Per rule 37, the exclusion list is written **before** the headline, so it is a specification of what
this establishes rather than a subtraction from something already believed.

### WHAT THIS CANNOT REACH, stated before a single run

1. **den³ and beyond.** Coefficients carrying `L³` produce the same clean integer as their absence,
   exactly as den² did to the den¹ prover. This moves the blind spot; it does not remove it.
2. **Numerator degree above the stated box.** The ansatz is
   `(polynomial of degree ≤ dx, dy) / L²`. There is **no a priori bound** on the numerator degree of
   a genuine Killing tensor, so the box is a *choice*. It is set to the measured reducible-holding
   box **plus a margin of 4 in each variable** — strictly larger than what it must contain, and
   still finite.
3. **Rank ≥ 5 at den².** Not attempted here on cost grounds. Named, not silently omitted.
4. **Non-integer δ.** ZV is rational only at integer δ; δ = 1 and 2 only.
5. **Nothing bounds the rank.** Unchanged from §124. The grading theorem gives rung independence
   and finiteness of *each* rung, not of the ladder.

### THE FREE STRUCTURAL CHECK, and it is new

Any `p/L` equals `(p·L)/L²`. With the boxes below, the **den¹ ansatz sits strictly inside the den²
ansatz** — δ=1: den¹ (5,6) × L(3,2) = (8,8) ≤ (10,10); δ=2: den¹ (10,12) × L(8,2) = (18,14) ≤
(20,16). Therefore:

> **dim(den² solution) ≥ dim(den¹ solution), ALWAYS.**

A den² answer *below* the den¹ answer is impossible and condemns the run. Same class as
`dim(reducible) ≤ dim(solution)`, costs nothing, and — per rule 18 — it guards one direction only.

### PRE-REGISTERED PREDICTIONS, with two-sided known-FAILs

At den², **every** reducible product becomes representable — the exclusions that made §124's den¹
numbers smaller than the full spans disappear. So:

    arm/rank        den¹ measured    den² PREDICTED     what changes
    δ=1 rank 2            5                5           nothing was dropped at den¹
    δ=1 rank 3            8                8           nothing was dropped at den¹
    δ=1 rank 4           11               14           Lsq², H·Lsq, H² become representable
    δ=2 rank 2            4                4           nothing was dropped; ALSO bridge-confirmed
    δ=2 rank 3            6                6           nothing was dropped at den¹
    δ=2 rank 4            8                9           H² becomes representable

**The two rank-4 rows are the entire experiment. Ranks 2 and 3 are calibration** — they must
reproduce the den¹ answers exactly, because nothing was excluded there in the first place, and
δ=2 rank 2 carries an **external** check: the bridge's independent screen, which has no denominator
scope at all, returned 4.

**KNOWN-FAIL, both directions:**
- **Above the prediction** → a Killing tensor that is not a product of the measured generators,
  living at den². At δ=2 that is **an irreducible Killing tensor on an exact vacuum solution** and
  the headline result of this project.
- **Below the den¹ answer** → violates the containment above; the run is wrong, not the spacetime.
- **Between the den¹ answer and the prediction at rank 4** → the box does not hold what it was
  measured to hold; an assembly or degree bug, not a physics result.

### Sizes, so the cost is on record before it is spent

    δ=1 r2   1210 unknowns    94 points        δ=2 r2   3570 unknowns   271 points
    δ=1 r3   2420 unknowns   107 points        δ=2 r3   7140 unknowns   310 points
    δ=1 r4   5005 unknowns   138 points        δ=2 r4  18375 unknowns   496 points

Repro: `scripts/_kt_zv_den2.py <delta> <rank>`.

## D35 — a pre-registered prediction of MINE that FAILED (2026-08-22, the bridge's n=320)

Recorded at the same weight as D31/D32/D33, which recorded three that held. **A record showing only
successful pre-registrations is not a record of pre-registration.**

**I predicted the bridge's basis rank at n=320 would land at 1900–2100 if saturating and ~3900 if
linear, target 2205. Measured: 1364.** My band overestimated by **47%**. Their own clean-design
extrapolation gave 1957–2104 and was wrong in the same direction and by nearly the same amount, so
this is not a disagreement between us — **both extrapolations failed identically.**

    n= 20 -> 475      alpha 20->40   = 0.642
    n= 40 -> 741      alpha 40->80   = 0.501
    n= 80 -> 1049     alpha 80->320  = 0.189   <- collapsed
    n=320 -> 1364     predicted 1900-2100

**The methodological cause, which is theirs and is the transferable part:**

> **A decelerating trend has no stable exponent to extrapolate, and fitting one on consecutive pairs
> assumes exactly the thing it is measuring.**

I had warned them to *"compare against the α trend, not the gap"* — correct as far as it went, and
**still not enough**, because I then extrapolated using that trend as though it were stationary. The
α values were not a noisy estimate of one exponent; they were samples of a function still bending.
Note the error survived the design-confound correction: α was refitted on the clean ladder and the
extrapolation failed anyway, so **the fault is in the extrapolation, not in the inputs**.

**The finding this produces is stronger than the one I proposed.** Not *"degree 4 needs more
orbits"* but: **no affordable orbit count reaches full rank with this sampling design** — per-orbit
yield collapses faster than the deficit closes. At 8× the orbits and 16× the rows of the arm that
first failed, the screen recovers **4 conserved directions against the 14 required**. What would
help is a different sampling design (orbits spread over the (x,y) domain rather than drawn from a
radial window), not more of this one. **Their degree-4 den² arm therefore remains OPEN, not
negative** — and §124 already says so.

**Two additions from the bridge, and the second is a shape I had not named.**

**(1) The failure is JOINT, which is what makes it a method failure.** Their clean-design
extrapolation gave 1957–2104 and failed identically to mine. **Two independent people applying the
same method to the same corrected data got the same wrong answer.** Note the sting: this is the
non-intersecting-failure-modes argument (rule 31) arriving as a *counterexample* — our extrapolation
methods were **identical**, so agreement between them was worth exactly nothing. Two instruments
agreeing is evidence only when their failure modes differ; two applications of one method agreeing
is not a second opinion.

**(2) A CORRECTED INPUT DOES NOT LAUNDER THE INFERENCE BUILT ON IT.** The ordering is the
instructive part: I flagged the design confound, they corrected the ladder on that advice, α was
refitted on clean inputs, **and the extrapolation failed anyway.** Having fixed the data creates the
*feeling* of having fixed the analysis, and those are separate acts — the same structure as rule 30
(stating a rule versus encoding it), which I had for tooling and had not applied to inference.

**§124 is unaffected.** The degree-2 result it cites stands exactly as run: 5 at δ=1, 4 at δ=2,
threshold fixed on the control arm, ten-order gap at the cut, H recovered at 6.3e-15.

## D36 — den² calibration arm: three of three passed, including the external one (2026-08-22)

All three predicted in D34, before any den² run existed. All three measured on both primes.

    δ=1 rank 2 den² = 5    predicted 5    PASS   (den¹ was 5)
    δ=1 rank 3 den² = 8    predicted 8    PASS   (den¹ was 8)
    δ=2 rank 2 den² = 4    predicted 4    PASS   (den¹ was 4; ALSO the bridge's number)

**These had to reproduce the den¹ answers exactly**, because nothing was excluded at those ranks in
the first place — so a *change* here would have meant the wider box broke something rather than
revealed something. The containment check holds at all three: no den² answer fell below its den¹
counterpart.

**δ=2 rank 2 carries an external test as well.** The bridge's numerical screen — no denominator
scope, entirely different failure modes — returned **4** at momentum-degree 2 on δ=2, and stated
that value *as a prediction on the record before this run completed*. It now agrees with an exact
GF(p) nullspace over a den² ansatz. **Both instruments are at den² on this point**, rather than one
being extended to meet the other.

**What the calibration arm does NOT establish**, stated because the temptation is to read three
passes as more than they are: it shows the den² machinery reproduces known answers where nothing
was hidden. **It says nothing yet about the region the ladder was built for.** The two rank-4 rows
are the experiment — δ=1 predicted **14** against den¹'s 11, δ=2 predicted **9** against den¹'s 8 —
and the increase is exactly the products that L² makes representable. Anything above those is a
Killing tensor that is not a product of the measured generators.

**Interrupted by a power cut at ~13:57 IST**, losing δ=1 rank 4 at 70/138 points (rows bank at the
end of assembly, so that rung restarts from zero). δ=2 rank 2's 154 MB of banked rows survived and
its result had already landed. Restarted δ=1 rank 4 and δ=2 rank 3.

## D37 — den² ladder: five of six predicted and held; rank 4 CANCELLED on a memory finding (2026-08-22)

**All five predictions in D34 that could be tested were tested, and all five held**, each committed
before its run existed:

    δ=1  den²   rank 2 = 5    rank 3 = 8    rank 4 = 14      (den¹ gave 5, 8, 11)
    δ=2  den²   rank 2 = 4    rank 3 = 6    rank 4 = NOT RUN (den¹ gave 4, 6,  8)

The two informative rows both landed: **δ=1 rank 4 went 11 → 14, and the increase is exactly the
three products L² makes representable** (`Lsq²`, `H·Lsq`, `H²`) **and nothing else.** So widening
into the region the den¹ prover is blind in recovers precisely the reducibles that were being
excluded, with no residue — **no irreducible Killing tensor hiding at den² on the Schwarzschild arm
at rank 4.** δ=2 rank 2 additionally agreed with the bridge's independent screen, which has no
denominator scope at all.

**δ=2 RANK 4 IS CANCELLED, AND THE REASON IS A NUMBER OF OURS THAT WAS WRONG BY 8×.**

We published **4.75 GiB/prime** three times, and two sister sessions scheduled around it — one
pre-committed to pausing, one stayed off the machine entirely. That figure is the size of the
**numpy matrix at the rank step**. It is not the peak. The peak is the **assembly**, which
materialises every row as a Python list-of-lists of exact integers *before any numpy exists*:

    rank 3:  10850 ×  7140 =  77M entries  ->  MEASURED 4.58 GB   (63 bytes/entry)
    rank 4:  34720 × 18375 = 638M entries  ->  PROJECTED ~38 GB

**Rank 4 does not fit at any concurrency** — not alongside another session, not alone, not with
every process on the machine stopped. It was never a scheduling question, and the hours all three
sessions spent treating it as one were spent on the wrong problem.

**The class this belongs to, and it is the one the day's other fixes cannot touch.** Between three
sessions in one afternoon: quantum published `0.59 GB` (a real computation of the wrong quantity —
`free + speculative`, omitting `inactive`); the bridge published `mem_free_gb: 6.08` under a name
promising *free* while containing *free + inactive*, **94× what the name promised**; and we
published a correct computation, correctly performed, of a quantity that was not the one we named
it. **All three carry full measurement-authority. None is reachable by a freshness, liveness,
validity or staleness check, because in every case the plumbing works perfectly.**

> **Peers can detect staleness. Nobody can detect a confident fabrication.**

**And the check that would have caught ours was running in front of us for an hour.** Rank 3's RSS
climbed past every figure we had quoted — "a few hundred MB", 1.9, 2.5, 4.58 GB — and every reading
was consumed as a *scheduling fact* and never once as *evidence about the rank-4 estimate*. **We had
a live calibration for our own projection and never compared them.** The bridge offered to soften
this on the grounds that it is a category the mind does not offer; **declined, because we held a
prediction and they did not — a prediction with contradicting live data in front of it is the one
case where the comparison is owed.**

**What unblocks it: online elimination.** Reduce each row into a running basis as it arrives,
keeping at most `n_unk` rows, which bounds memory independently of the sample count. Deferred
deliberately — it is a change to the numerical core and gets what the resume fix got: a
**known-answer rung reproduced bit-identically** before it is trusted on a rung with no known
answer. And per the bridge: **verify the new ceiling by measurement, not by `18375² × 8` arithmetic**,
since that arithmetic is the same *kind* of object as the 4.75 figure — correct about a structure,
silent about which phase dominates.

**Standing after this:** ZV closed at ranks 1–6 den¹ on both arms; ranks 2–4 den² on δ=1; ranks 2–3
den² on δ=2. **δ=2 rank 4 at den² is OPEN and named as open**, blocked on tooling rather than on
mathematics.

## D38 — a count is an upper bound, not a measurement; and the Phase 4 pre-registration (2026-08-30)

**The defect in every den² number we have published.** `solve_kt_modp` returns the nullspace
dimension of a system sampled at random points. Sampling is sound for **rejecting** a candidate — a
fixed nonzero polynomial almost never vanishes at 338 random places — and it is **not** sound for
accepting one, because the nullspace is computed *after* the points are drawn. Schwartz–Zippel
bounds the wrong direction. All a count establishes is `dim(sampled) ≥ dim(true)`.

We did not notice because on δ=1 the two coincide, so four flat box sweeps looked like convergence
rather than like a substrate where the slack happens to be zero.

**What made it visible.** δ=2 rank 4 den² gave 14 / 24 / 34 at boxes 357 / 437 / 525 against a
reducible span of 9 — an exact line, `dim = 5·dx − 66`. A quantity that tracks the *ansatz* and not
the *geometry* is not a property of the spacetime. `_kt_nullvec.py` then reconstructed three basis
vectors and tested `{H,F}=0` as a polynomial identity: **two hold, one does not (298 nonzero
coefficients).** The sampled nullspace demonstrably contains non-solutions.

**Why one-at-a-time could not finish it.** True solutions form a *subspace*; the RREF basis is not
aligned to it. A vector failing does not remove exactly one dimension and a vector passing does not
certify its neighbours. Testing all 14 would still have left `2 ≤ dim ≤ 13`.

**The computation that did.** `{H,F}` is linear in `F`, so with `v = Σ aᵢvᵢ` over the sampled basis,
`dim(true) = nullity(C)` where `C` stacks every bracket coefficient — a 14-column solve rather than
another overnight sweep. Result at box 357, prime 2147483647: **exact dimension 9, reducible span 9,
irreducible 0.** The excess was `5(dx−15)` of pure sampling slack, and the true dimension was 9 at
every box all along. The D34–D37 prediction of 9 **holds**; the 34 that appeared to break it was
never a measurement.

**A guard fired on the real computation, not on a planted error.** Clearing each bracket with its
own `cancel()` is not a linear operation and would have corrupted `C` into a clean, wrong integer
with no error raised. Calibrating one fixed `L^M` on vector 0 was not enough either — at box 357
vectors 0–3 clear with `(x−1)⁸(x+1)²⁴(y−1)³(y+1)³` and vectors 4–13 need
`(x−1)¹⁵(x+1)⁴¹(y−1)⁵(y+1)⁵`. The run **stopped** rather than proceed. The fix takes the lcm of all
denominators before clearing any.

**Held open, not claimed.** Nine is one prime and one box. A nonzero rational can reduce to zero mod
p, so a false vanishing is exactly the failure two primes exist to catch. Both confirmations
(prime 2147483629 at box 357; box 437 where the sampled count was 24) are running.

### Pre-registration, recorded BEFORE the run lands

Phase 4 holds the box FIXED at 357 and raises points 338 → 500. The exact answer there is **9** and
the sampled answer at 338 points was **14**. We do **not** know which way this goes, and say so in
advance rather than after:

- **If it returns 14** — slack is structural in the ansatz, not point-limited. More points at fixed
  box do not help, and every sampled count in this project needs the exact test before it means
  anything.
- **If it returns 9** — slack was point-limited. The sampled route is salvageable by sampling
  harder, and the box sweeps were under-pointed rather than wrong in kind.
- **If it returns something between** — slack shrinks with points but does not close, and the exact
  test is required regardless.

The prior data cannot separate these: slack tracked box (5/15/25) while point count *also* rose
(338/413/496), so the two were never independently varied. That is precisely the confound Phase 4
was queued to break, and it was queued before we knew the exact answer.

### D38 resolved (2026-08-30 07:52) — the registered branch was "structural", and that is what landed

**Phase 4: box 357 FIXED, points 338 → 500, both primes → dimension 14.** Identical to 338 points.
Of the three branches recorded in advance, **"if it returns 14 — slack is structural in the ansatz,
not point-limited"** is the one that holds.

    box fixed at 357:   338 points -> 14      500 points -> 14      (+48% points, no change)
    points scaled:      box 357 -> 14   box 437 -> 24   box 525 -> 34

**Slack depends on the ansatz box alone and is invariant under point count.** The two were
confounded in every earlier run because point counts were derived from a row-count heuristic that
scaled with the box, so the sweeps varied both at once. Phase 4 was queued specifically to separate
them, and it was queued before the exact answer was known.

**The operational consequence.** *A sampled-vs-reducible gap cannot be closed by sampling harder.*
More points do not shrink it — not marginally, not at all. When a count exceeds the reducible span,
the exact test (`_kt_exact`) is the only instrument that resolves it. This retires the fallback that
would otherwise have been reached for first ("the 34 is under-sampled, throw points at it"), which
would have burned arbitrary compute and returned 34 every time.

**Scope unchanged.** The squeeze still holds: `reducible ≤ true ≤ sampled` pins every rung where
the ends coincide, which is all seventeen. What D38 changes is only the *remedy* for a rung where
they do not.

**A stale verdict line, flagged rather than quoted.** `phase4.sh` printed "14−9=5 remains
unexplained and needs the exact test" from a canned `case` written the previous night, before
`_kt_exact` existed. The 5 *is* explained — it is `rank(C)`, the bracket-map rank, measured at both
primes. A driver's pre-written commentary is not a finding, and reading it back as one is how a
superseded claim re-enters a record.

## D39 — direction change: ZV was reproduction, sGB ranks 3–6 are not (2026-09-02)

**The literature check that should have come first.** Vollmer (arXiv:1602.08968, 2016) already
proved nonexistence of a nontrivial Killing tensor for Zipoy–Voorhees **up to valence 11**; §124 and
§126 covered ranks 1–6. We are strictly inside a decade-old result, by five ranks. Worse for
novelty, Kokkinos (arXiv:2608.22523, posted 23 Aug 2026 — *during* our δ=2 rank-4 computation)
proves no irreducible rank-2 Killing tensor for the whole two-Killing-vector Weyl class in vacuum
or electrovacuum, treating the γ-metric explicitly.

Our work is correct, independently obtained and methodologically different (modular sampling plus
an exact intersection over GF(p), versus their rigorous computer algebra). It is **not new
knowledge.** That is exactly the outcome the user's standing steer names: *"are we just doing what
others have already done with a smaller machine."*

**The gap that is real.** Owen, Yunes & Witek (PRD 103, 124057, 2021) solved the Killing equation
through **rank 6 in dynamical Chern–Simons** but only **rank 2 in scalar Gauss–Bonnet**. They
conjecture — stating explicitly that they cannot prove — that no Killing tensor of any rank exists.
sGB ranks 3–6 are unsearched. Separately, a dynamical-systems argument (arXiv:1804.04002)
conjectures the exact dCS metric *does* possess a fourth constant, so the field is not settled.

**Decision: point the instrument at sGB ranks 3–6.** Three reasons. It is explicitly open and named
as such. The repo already carries EdGB machinery. And our route has a real methodological advantage
over the approach that stalled: they hit overdetermined and inconsistent systems solving
symbolically, where we have a modular sampler plus an exact test now validated in both directions
(§127 recovers Carter; §128's controls kill it when they should).

**What was built before asking the question, and why none of it was optional.** §128 records the
order-by-order solver, its five controls, the covariant cross-check, and the derivation of the
rotating correction. The rule underneath all of it: *a truncated perturbative metric solves no field
equation, so an exact-Killing-tensor search on one returns zero for free.* Asking the open question
with the wrong instrument would have produced a publishable-looking null that meant nothing.

**Named as still missing, not glossed.** The sGB solution is a double series in coupling ζ **and**
spin χ; the current solver expands in one parameter. Ranks 3–6 need consistent bookkeeping in both,
which is a real design step and not a parameter change. Until it exists, no sGB rank-3+ result can
be reported.

**Also fixed here: evidence that was not committed.** `data/*.log` blanket-ignored every log,
including `kt_boxnight.log`, which carries the §124–§127 phase results and the D38 timings quoted in
RESULTS.md. Zero `.log` files were tracked. This is the same provenance failure the repo already
records paying for with `data/kt_*.out`: **a size rule is not a judgement about evidentiary value.**
Narrow negation added; the ~60 watchdog and progress logs stay ignored.

## D40 — a NO SOLUTION that was a property of the ANSATZ, not of the equation (2026-09-02)

**The symptom.** The O(χ²) dilaton derivation returned `NO SOLUTION` twice — 20 equations for 16
unknowns, then 29 for 20. Both times the over-determined system was doing exactly what it was built
to do: refusing to fit rather than producing a plausible wrong answer.

**Both failures were the ansatz having the wrong SHAPE, and the second attempt moved further away.**
The first ansatz was `Σ p_k m^k/r^(1+k)`. Reasoning from the source (`504 m⁴cos²θ/r⁸`) and the fact
that the box operator lowers the radial power by two, the correction "must" lead with `m⁴/r⁶`, so
the ansatz became `Σ p_k m^(4+k)/r^(6+k)`. That is sound reasoning about the *particular* solution
and it is still wrong.

**What settled it was solving the ℓ=0 sector exactly by quadrature** rather than guessing a third
time:

    r(r-2m) P' = C - 168 m⁴/(5 r⁵)
    C = 21/(20m)                      forced by killing the residue at the horizon
    P(r) = -(7/100)[ 15/(mr) + 15/r² + 20m/r³ + 30m²/r⁴ + 48m³/r⁵ ]

The solution is rational, but *only* for that one value of `C`. Its terms run as `m^(k-1)/r^(1+k)`
— the structure of `ϑ⁽⁰⁾ = (1/mr)(1 + m/r + 4/3 m²/r²)` itself. The leading `1/(mr)` comes from a
**homogeneous admixture fixed by horizon regularity**, and it dominates the `m⁴/r⁶` behaviour that
dimensional analysis of the source predicts. The first ansatz was off by `m²`; the second was off by
much more.

**The general lesson, which is the reason this gets a decision line.** *Dimensional analysis of the
SOURCE constrains the particular solution and says nothing about the homogeneous admixture a
boundary condition will force.* Where regularity fixes an integration constant, that admixture can
dominate the asymptotics — so an ansatz derived from the source alone can be structurally incapable
of representing the answer, and no coefficient choice repairs it.

**And the failure mode this belongs to.** A `NO SOLUTION` from an over-determined system is
ambiguous in exactly the way a firing guard is: it may be a property of the equation (informative)
or of the ansatz (an artifact). Reading it as the former would have been "no O(χ²) dilaton exists",
which is false and would have blocked the whole sGB line. This is the seventh time in this arc that
the instrument rather than the physics was at fault, and the resolution was the same each time:
**ask why the check fired before acting on what it said.** Compare §128's three broken controls and
the `(m⁴-1)` residuals that nearly condemned a correct metric.

**Guard added:** the solver now cross-checks its ℓ=0 answer against the exact quadrature result. A
disagreement there means the solver is wrong rather than the ansatz — a stronger test than either
failing run had available.
