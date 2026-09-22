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

## D41 — rank 2 in sGB is settled three ways; the value is at ranks 3–6 (2026-09-03)

**A narrowing found in the source paper itself, not in a literature search.** While reading
arXiv:1405.2133 for the O(χ²) metric structure, the discussion section states:

> the solution … is of Petrov type I. **Petrov type I spacetimes do not possess a second-order
> Killing tensor or a Carter-like constant.** This implies that geodesic motion may be chaotic once
> corrections of O(α′²χ′²) are included.

So the rank-2 answer for sGB at O(χ²) is argued **in the paper that supplies the metric**, by a
Petrov-type argument that is independent of any Killing-equation computation.

**That makes three independent arguments for rank 2**, none of them ours: Ayzenberg & Yunes by
Petrov type; Owen, Yunes & Witek (PRD 103, 124057) by solving the Killing equation directly; and
Deich, Cárdenas-Avendaño & Yunes (arXiv:2203.00524) from Poincaré sections showing chaotic phase
space. A rank-2 result from us would be a fourth confirmation of a settled point — worth having as a
**control** on our instrument, and worth nothing as a contribution.

**Decision: rank 2 is demoted to a control, and the claim we pursue is ranks 3–6 only.** Two reasons
this is not merely a matter of emphasis:

1. **The Petrov argument does not reach higher rank.** Type I excludes a second-order Killing
   tensor. It says nothing about rank 3, 4, 5 or 6, and the literature contains no argument that
   does — OYW searched dCS through rank 6 but sGB only through rank 2, conjecturing without proof
   that nothing exists at any rank.
2. **It changes what a null means.** At rank 2 a null is a fourth confirmation. At ranks 3–6 a null
   closes a stated conjecture by exact method, which is a different and citable object.

**The falsifier tightens correspondingly.** Deich et al. find chaos numerically in this theory. If
our method reports that Carter-like structure *survives* at rank 2 — where three independent
arguments say it cannot — the instrument is the first suspect and not the physics. That is now a
sharp, published disagreement to fail against rather than a quiet null, and it is the strongest
external check available to this project.

**Recorded also because of how it was found.** This was not turned up by a prior-art search; it was
sitting in the discussion section of a paper we had already mined for equations, and it went unread
for two days while its O(χ²) metric was being derived. **Reading the paper you are already using is
cheaper than any literature gate**, and the parts that constrain a claim are rarely in the equations
you came for.

## D42 — a rank is only "new" if its Kerr Killing space has a new Q-power (2026-09-04)

**The mistake this records.** While rank 3 was running it was described — to a sibling session, in
this repo's own framing — as "the open rung nobody has reached." That is true about the *literature*
and misleading about the *content*. The rank-3 Kerr Killing space is

    8  =  6 (p_t^a p_phi^b H^c)  +  2 (Q p_t, Q p_phi)

so every direction above the floor is Carter times a momentum, and Carter had already died at rank 2
(§130). The rank-3 answer was strongly favoured before the 8.5-hour run started.

**The decomposition, which reproduces Kerr's known dimensions and so is not a guess.** Writing the
rank-r space as `Q^q x (reducible of degree r-2q)`:

    rank 2:  4 + 1                 =  5     known 5
    rank 3:  6 + 2                 =  8     known 8
    rank 4:  9 + 4 + 1             = 14     known 14
    rank 5: 12 + 6 + 2             = 20
    rank 6: 16 + 9 + 4 + 1         = 30

**The rule.** A rank whose non-floor directions are all `Q^1 x (momenta)` tests the same obstruction
`{H1,Q}` that the rank below already tested, multiplied through. Its answer is not *implied* — the
solution `G1` need not factor, so the obstruction sits in a larger space and could have been killed
there — but it is expected, and reporting it as an independent result overstates it. **The first
genuinely uncharted rank is the first one carrying a new power of Q: rank 4, where `Q²` appears.**

**Consequence for sequencing.** Ranks 3 and 5 are consistency rungs; ranks 4 and 6 are the ones that
can surprise. If compute is scarce, rank 4 before rank 5 — which inverts the natural ladder order
and is the whole point of writing this down.

**And the guard.** `_kt_double.py` printed rank-2 corroboration prose ("Petrov type I;
Owen-Yunes-Witek; Deich et al.") at rank 3, where none of those arguments reach. Now rank-branched,
and the rank-general control message reproduces rank 2's hardcoded numbers exactly — the check that
a generalisation preserved the case it was generalised from. **Tenth instance in this arc of the
instrument, not the physics, being at fault; first instance where the fault was in prose rather than
in arithmetic, which is the kind that survives into a write-up.**

## D43 — the rank-4 positive control is ultrahyperbolic, and that changes the reading not the control (2026-09-04)

**Found by a sibling's prior-art sweep, verified here before being believed.** The bridge relayed
that Cariglia-Galajinsky's rank-3/4 examples are signature (2,q), not Lorentzian. Rather than import
that, the signature was computed locally on our own control metric (`scripts/_kt_cg5d.py`, their
Eq. 26):

    X=2, y=3     X=5, y=-7/2     X=1/2, y=-1     X=3, y=10
    eigen -2 +3  -2 +3           -2 +3           -2 +3        -> signature (2,3), ULTRAHYPERBOLIC

**The control is unaffected, and the reason is worth stating rather than assumed.** Its only job is
to show the prover can return "something" where something exists — that it is not a null-machine.
The Killing equation is linear in the metric components and makes no reference to signature, so
finding an irreducible rank-4 tensor on a (2,3) substrate proves exactly what it was built to prove.
Nothing in that argument uses Lorentzian.

**What it does change is what a null MEANS, and this is the substantive part.** Per the relayed
sweep (NOT verified here): no Lorentzian Ricci-flat or Einstein spacetime with an irreducible
Killing tensor of rank >= 3 is known in ANY dimension, stated open by Cariglia-Galajinsky 2015 and
Fordy-Galajinsky 2019. If that holds, our Lorentzian nulls are not facts about an awkward metric —
they are another datum in a pattern nobody has broken, which makes them less surprising and more
meaningful at once.

**CORRECTION, same day, and it matters more than the thing it corrects.** The paragraph above
originally called the Eisenhart-lift argument "the obstruction" and treated it as a mechanism
explaining why Lorentzian vacuum is empty. The bridge relayed it that way and then withdrew it
against the source. Cariglia-Galajinsky's actual sentence, quoted:

> "Close inspection of two-dimensional integrable models possessing a cubic (or higher) integral of
> motion [13] shows that none of them is described by a harmonic function. Thus the construction of
> four-dimensional spacetimes of signature (1,3) which admit higher rank Killing tensors **seems to
> be problematic within the Eisenhart approach**."

That is an obstruction to **one construction route**, hedged by its own authors, inherited from a
survey of 2d models. It is **not** a theorem about Lorentzian vacuum spacetimes. Calling it one
promoted a limitation of a technique into a property of the physics. (The attribution to
Hietarinta is also unverified — the paper says "[13]" and neither we nor the bridge opened it.)

**The operational consequence, recorded before rank 4's verdict lands rather than after.** *Nothing
currently on the table forbids an irreducible rank-4 Killing tensor in this setting.* So if rank 4
returns anything above floor 9, the D41 reflex — "this contradicts published arguments, so the
instrument is the first suspect" — **does not apply here**, because there is no such argument at
rank 4. The verification burden stays exactly as heavy for a different reason: a sampled nullspace
count is an UPPER bound, so a positive result is never self-certifying no matter what the
literature says. Verify because positives cannot certify themselves, not because a theorem is
being contradicted.

The one claim from the sweep that is the paper's own words, still relayed rather than read here:
"none of the Lorentzian spacetimes studied in [5],[7]-[12] solves the vacuum Einstein equations."
Note how much narrower that is than "no Lorentzian example is known in any dimension" — it is a
statement about the papers surveyed there. The narrower version is the one to quote.

**CLAUDE.md was materially incomplete and is corrected.** It said CG "construct Ricci-flat metrics
carrying irreducible rank-3 and rank-4 tensors — so the objects exist", which reads as though a
Lorentzian vacuum example exists. Now qualified, with the signature stated and the control's status
spelled out. **`_kt_cg5d.py` prints its own signature from now on** — the fix for "a property nobody
checked because nobody thought to" is to make the substrate report it, the same discipline as
verifying Ricci-flatness before calling something a spacetime (§124).

**What was NOT imported.** The sweep's other claims — the rank-bound dimensions, Vollmer being three
metric families rather than one (which would amend D39), the Kruglikov-Matveev and Kruglikov-Steneker
nulls — are recorded as *unverified relay* and will get an independent literature check before any
of them edits a decision here. Siblings send asks, not conclusions; copying a sibling's sweep in
destroys the only thing independent agreement is worth (§0).

## D44 — the reducible floor is not combinatorial; it must be measured (2026-09-05)

**What broke.** Rank 4 finished with 8 survivors against a hardcoded floor of 9 and condemned
itself, correctly: reducibles are exactly conserved, so `survivors < floor` is impossible. The
guard was right. **The floor was wrong.**

**Why.** A floor direction `p_t^a p_φ^b H^c` is conserved, but the solver can only *find* it if its
**ζ-correction** lies in the ansatz — and that correction carries denominator powers the background
product does not. At O(ζχ²) the `c=2` direction needs `2(HK0·H1_2 + HK1·H1_1 + HK2·H1_0)`, whose
denominator does not divide `L⁶`. Since `a+b+2c = rank` forces `c ≤ 1` for rank ≤ 3, **`H²` first
exists at rank 4** — so ranks 2 and 3 could not have exposed this, and did not.

**The rule.** *A floor is a claim about the search space, not about the algebra.* Counting conserved
products answers "what is conserved"; the solver needs "what is conserved AND findable here". The
solver now asks the representability guard per direction at run time and reports both numbers. The
measured floor reproduces every rank: 4 = 4, 6 = 6, 9 combinatorial → 8 representable = 8 measured.

**And the same error, committed twice in one day.** `scripts/_kt_coverage.py` was written that
morning precisely to stop unstated coverage assumptions, and shipped with one: it modelled whether
the *background product* fits, not its *ζ-correction*, and so reported sGB coverage as 100% when it
was 8/9. **The fix for the class was an instance of the class.** The wrong row is kept in the file,
labelled, because a counterexample inside the tool is worth more than a corrected number.

## D45 — denpow 7 at margin 4, and why not margin 6 (2026-09-05)

**The gap to close.** Only the `H²` direction was missing at denpow 6. Verified: its correction
divides `L⁷` with numerator degrees (19,20), so **denpow 7 makes the floor 9 of 9** — checked before
launching rather than hoped for, since a re-run that did not close the gap would be pure waste.

**Margin 4, not the 6 used at denpow 6, and the reason is memory not physics.**

    margin 4   box 25x22   20930 cols   matrix 3.8 GB   est peak 5.6 GB   floor 9/9
    margin 5   box 26x23   22680 cols   matrix 4.5 GB   est peak 6.6 GB
    margin 6   box 27x24   24500 cols   matrix 5.2 GB   est peak 7.6 GB   floor 9/9

Available memory at launch was 7.29 GB with swap already 739 MB used, so margin 6 sits inside its
own error bar on a 16 GB laptop running unattended. Margin 4 leaves 1.7 GB of headroom and closes
the gap just as completely.

**The honest cost, stated because it is easy to gloss.** Margin 6 would have been a **strict
superset** of the denpow-6 run: re-expressing `N/L⁶` as `N·L/L⁷` raises numerator degrees by
(3,2), so containing box 24×22 at denpow 7 needs 27×24. Margin 4's 25×22 does not contain it.
**So the two runs are complementary, not nested** — denpow 6 searched wider numerators at shallower
denominators, denpow 7 searches deeper denominators including the `H²` direction. Their union
covers more than either, and neither supersedes the other. Do not report the second as replacing
the first.

## D46 — the matrices are 0.01% dense, and the constraint was never storage (2026-09-07)

**How this surfaced.** Rank 6 was requested. Sizing it the usual way said ~29 GB dense against ~9 GB
usable, so it looked simply out of reach. Before reporting that, measured the matrix: **6.9 nonzeros
per column, 3 per row, density 0.0124%.** The rank-4 matrix carries ~168,000 nonzeros in 1.36×10⁹
cells — 5.1 GB of storage for ~1.3 MB of content.

**So every box decision for weeks has been sized against a number four orders of magnitude larger
than the information in the matrix.** That is not a small inefficiency; it is the reason rank 5 and
6 looked impossible. The dense representation was a choice inherited from rank 2, where it was
free, and never revisited when the ranks grew.

**Two eliminators, and the honest split between them.**

`_kt_stream.py` — a **certain** 2.27×. Elimination never needs the rows it has consumed: the echelon
basis holds at most `ncols` rows, and rows reducing to zero are discardable at that moment. Working
set becomes `ncols × ncols` rather than `nrows × ncols`. Rank 5 goes 13.0 → 5.7 GB and becomes
runnable. Rank 6 goes 19.7 → 8.7 GB but only at box 22×24, which is the floor's own minimum — zero
search slack, so not a real search (D38).

`_kt_sparse.py` — an **uncertain** but potentially much larger win, gated on fill-in. Storage would
be ~1.3 MB. Its self-test shows fill-in of 16× / 50× / 103× growing with size **on random
matrices**, which are the worst case and say nothing about structured bracket matrices.
`_kt_fillin_test.py` measures the real one against a known answer (rank-4 operator, nullity 14).

**Both are equality tests, not comparisons, and that is a property worth having.** Processing
columns left to right, the pivot columns are a property of the matrix and the reduced row echelon
form is **unique** — so any correct elimination returns the same nullspace basis, not merely an
equivalent one. A new eliminator that returns *approximately* the right nullity has a bug, not a
different valid answer.

**And the test that nearly did not exist.** The rank-2 smoke test of the rewired solver passed —
and exercised only the dense path, because its matrix is 0.3 GB, under the switch. Streaming would
first have run on a multi-day rank 5, where a bug has nothing cheap to disagree with. `STREAM_MIN_GB`
is now env-overridable so the streaming path can be forced onto a case whose answer is known
independently. *A code path that only executes on the expensive run is a code path with no control.*

**Measured before running, not after (the §132 lesson applied forward).** Rank 6 needs **denpow 8**:
its `H³` floor direction's ζ-correction needs `L⁸` with numerator degrees (22,24). The pattern is
one denominator power per power of `H` — c=1 → L⁶, c=2 → L⁷, c=3 → L⁸ — so the rank at which a new
`H^c` first appears is also the rank at which the required denominator deepens. That is now
predictable rather than discovered by a condemned run.

## D47 — Zipoy–Voorhees was closed at all ranks in 2013; our sweep missed it on vocabulary (2026-09-13)

**The finding** (§134). Maciejewski, Przybylska & Stachowiak (PRD 88, 064003; arXiv:1302.4234) prove
by Morales–Ramis differential Galois theory that geodesic motion in ZV at δ=2 has **no additional
meromorphic first integral** — every rank, any meromorphic form. §124/§126 closed ranks 1–6 in the
den¹ sector for the same δ, so in the functional sense they are a strict special case of a result
already in print. The residual not covered — a polynomially irreducible but functionally dependent
tensor — has no known mechanism on ZV, and §134 says so rather than overcorrecting.

**Why a prior-art sweep missed a paper on exactly our metric: vocabulary.** We searched in our own
terms — *Killing tensor, rank, irreducible*. That paper never uses them. It says *first integral,
meromorphic, Liouville integrable, normal variational equation*. **The same object has at least three
names in three communities** — Killing tensor (GR geometry), polynomial first integral (dynamical
systems), Liouville integrability (Hamiltonian mechanics) — and a sweep phrased in one community's
words cannot see results written in another's. It is quantum's rule from the bridge in a sharper form:
a negative sweep survives only as far as its query vocabulary reaches.

> **Rule.** Before calling anything unsearched, restate the question in each neighbouring
> community's vocabulary and search each. For this project that means at minimum: *Killing tensor*,
> *polynomial first integral*, *Liouville / non-integrability*, *differential Galois / Morales–Ramis*,
> *Painlevé / Kovalevskaya*.

**How it was found — credit where due.** Not by a sweep. The user asked whether the fluid-blowup
results (Chen–Hou; Buckmaster–Alpöge) had any bearing here. They don't transfer directly — blowup is
about a field becoming infinite, our question about an orbit being regular — but the question led to
the real bridge between singularities and conserved quantities: Kovalevskaya (1889) located an
integrable top by studying singularities in complex time, which grew through Painlevé and Ziglin into
Morales–Ramis. Searching *that* lineage turned up this paper in one query. **An outsider's analogy
reached a result our specialist sweep did not.**

**What it opens: a candidate next direction, proposed and not started.** Applying Morales–Ramis to the
sGB black hole would attack **two of §3's three ceilings at once**:

1. **Rank** — it excludes integrals of *every* degree, not one rank at a time.
2. **Analyticity** — it works on the Hamiltonian *as given* at finite ζ, not order by order, so it
   does not require an integral to have a Kerr root. For the truncated metric as an exact Hamiltonian
   system, a tensor non-analytic in ζ would *not* be invisible to it.

It would **not** touch the third ceiling's physics caveat — the substrate is still the O(ζ)O(χ²)
truncation — and it only excludes *meromorphic* integrals. Obstacles, unassessed: it needs a
particular solution whose normal variational equation is solvable enough to compute a Galois group
(the equatorial radial geodesic worked for ZV; sGB's slow-rotation terms may break that symmetry),
and Kovacic-type algorithms can become intractable on large rational coefficients. A quick search found
no application to EdGB/sGB — a narrow negative from a sweep phrased by me, so weak evidence that it is
untried, **and exactly the kind the rule above warns about.**

## D48 — stop rank 6 and replace the solver, not wait it out (2026-09-19)

**The decision.** Rank 6 was stopped in its final level after 10 days 20 hours, with ζχ⁰ and ζχ¹
complete and checkpointed. The user's call, and the right one: waiting had become sunk cost. The
run was thrashing at ~15% CPU with no way to see progress, the estimate to finish was ~two weeks
with a wide error bar, and a finished run would still have needed a second prime.

**What was actually wrong** — three independent costs, measured, which multiply:

1. **Storage.** `_kt_sparse` holds each nonzero in a Python dict-of-dicts, ~200 bytes. At the ζχ²
   peak that is ~22 GB; the same numbers as flat int32 arrays are ~0.9 GB.
2. **Interpretation.** The inner loop is integer arithmetic mod p, and in Python the interpreter
   overhead is the entire cost.
3. **Unused structure.** Every Hamiltonian piece (Kerr and sGB, χ⁰–χ²) was verified invariant under
   equatorial reflection `(y, p_y) -> -` and time reversal `(p_t, p_φ) -> -`, so the bracket never
   couples sectors of different parity. Rank 6's 75,516 unknowns split into **4 independent blocks
   of 18–20k**. The old solver used none of this.

Plus one algorithmic waste: it eliminated each pivot from rows already used as pivots — full RREF in
place — which only adds fill. Forward elimination plus back-substitution gives the identical basis.

**The replacement, and the rule it is held to.** `scripts/_kt_fast.py` (numba) finds the blocks
itself as connected components of the row/column graph — so correctness never rests on the symmetry
argument; if it were wrong the blocks would merge and it would only be slower. It stores rows as
flat arrays and compiles the kernel. A Rust port follows at the user's request, with the numba
version as its reference.

**Validation is an equality test, not a comparison:** the free-column-indexed nullspace basis is
unique, so the new solver must reproduce the old one *vector for vector* — on synthetic matrices,
then on the known answers already on disk (rank 2: 5; rank 4: 9; rank 6 tower and ζχ⁰/ζχ¹: 30).
Only after that does it touch ζχ².

**Operational requirements set by the user, to be built in:** pause/resume, checkpoints *inside* a
level rather than only between levels, and a controllable core count — few cores on weekdays while
the machine is in use, more at weekends. The block structure makes the last one natural: blocks are
independent, so parallelism is just how many run at once.

## D49 — the solver was never the whole cost: remove SymPy from the per-column path (2026-09-19)

**The measurement came first, at the user's request** ("measure the sympy step first"). With the
Rust solver in place (D48), rank 2's χ² level still took 2,285 s — and its solve took **0.4 s**.
Everything else was SymPy preparing the equations, in three places, each removed by an exact
identity rather than an approximation, and each validated by equality, not agreement:

1. **The operator, one SymPy bracket + clear per column** (75,516 at rank 6; 5,567 s to the
   operator matrix in the legacy run). A basis column is `m(p)·xᵃyᵇ/den`, and `(a,b)` enter the
   bracket only through `∂(xᵃyᵇ)`, so every cleared column is

       cleared(m,a,b) = xᵃyᵇ U + a·xᵃ⁻¹yᵇ V + b·xᵃyᵇ⁻¹ W

   with `U, V, W` read off the three columns `(a,b) = (0,0), (1,0), (0,1)`. **3 SymPy brackets per
   momentum monomial** (252 at rank 6) and integer shifting for the rest
   (`scripts/_kt_opfast.py`). Rank 6: **5,567 s → 24 s**, same 149,072 × 75,516 matrix.
2. **Re-clearing every operator column when a level's sources enlarge the denominator.** With
   `D₂ = D·q`, the cleared columns of `r·D₂` are those of `r·D` convolved with `q`'s coefficients —
   integer arithmetic mod p, no SymPy (`scripts/_kt_prep.py`; 426–1004× against the expression
   clear, still 100–218× against the ring clear of point 3).
3. **Clearing the sources themselves** — the cost left standing after 1 and 2, and measured before
   it was touched (`scripts/_kt_srcprof.py`): at rank 3 ζχ², **210 s of a 346 s run**, and 97% of it
   `sp.expand(num·q)` plus the Poly conversion after it — SymPy expanding an expression tree. The
   same product in a sparse polynomial ring `QQ[x, y, p]` is essentially free: **33 s → 1.0 s** on
   the largest source. `PB.clear` now does that; the old version stays as `PB.clear_expr`, the
   reference it is checked against (`scripts/_kt_clearcheck.py`).

**FLINT was not needed for any of it.** It was on the list for "whatever SymPy step is still slow".
Measuring showed the slow steps were slow *because of expression trees*, and SymPy's own
polynomial ring removes that; FLINT would speed up the ring further, which is not where the time is.
Kept on the list, not installed.

**Validation, end to end, against the legacy checkpoints — the strongest test available.** Rank 3
rerun from scratch on the new pipeline into a separate checkpoint directory (`KT_CKDIR`), then
every checkpoint compared as stored strings (`scripts/_kt_ckcompare.py`):

    rank 3, prime 0          legacy (Sep 3-4)   1+2 only   1+2+3     checkpoint (both reruns)
    operator matrix          563 s              4 s        3 s       27146 x 10500, same
    chi tower complete       6,273 s            65 s       22 s      480/480 identical
    zeta chi^0               9,405 s            88 s       37 s      640/640 identical
    zeta chi^1               13,385 s           102 s      49 s      800/800 identical
    zeta chi^2 (verdict)     30,714 s           346 s      92 s      720/720 identical, 6 = floor

**30,714 s → 92 s, 330×**, byte sizes identical too. Rank 2 likewise (chains 150/150 against legacy; ζχ⁰ 200/200 against the
Rust-on-legacy-prep run; ζχ¹ and ζχ² counts 5, 4 as in §130), in 183 s.

**Two operational fixes that fell out.** Checkpoint names now carry the prime (`_p1`) — a
second-prime run would otherwise have *resumed from the first prime's mod-p data* and reported it
as agreement. And `KT_CKDIR` points validation reruns at their own directory, so they neither
resume from nor overwrite the checkpoints they are compared against.

**In the gate.** `verify.sh` now runs the four equality tests (KT1 Rust, KT2 rescale, KT3 templates,
KT4 ring clear; the last two in `--quick` form, ~1 min each), so a regression in any replacement fails
the gate rather than surfacing as a changed count.

**What it buys, beyond speed:** the reporting standard in CLAUDE.md §3 asks for both primes, and
§130/§131/§133 each ran on one — at 8.5 h (rank 3) and 35 h (rank 4) per run it was never paid.
At minutes per run it is now the default.

## D50 — the level matrix as arrays, and a floor test that was testing the wrong thing (2026-09-19)

**The rescale moved the memory wall; it did not remove it.** Rescaling multiplies every operator
column by the same `q`, and that densifies the level matrix ~30×: rank 4 ζχ² went from 1.2M operator
nonzeros to 32.6M, a 6.8 GB process at ~200 B per Python dict entry. Rank 6 starts from 4.0M, so its
ζχ² would be ~100M entries — **~20 GB, the thrashing that stopped the legacy run (D48), rebuilt one
layer up.** The Rust solver holds the same matrix in ~1 GB. Found by extrapolating rank 4's
measured numbers *before* rank 6 got there, not by watching it thrash.

**Fix: the product never exists as dicts** (`scripts/_kt_coo.py`). A row key `(e, (j, k))` packs into
one integer `(e_id·W + j)·W + k`, so multiplying a column by `xᵃyᵇ` is `code + a·W + b`; the rescale
is vectorised over `q`'s terms and merged by sorting, in column chunks so the T-fold temporary never
exists for the whole matrix. The nullspace guard runs on the same arrays (bincount, exact below
2⁵³). Validated: entries identical to the dict rescale on the real rank-2 and rank-3 operators with
the real 168-term cofactor, nullspace identical, **guard silent on true vectors and firing on a
deliberately bent one**. End to end, both ranks' checkpoints identical to legacy again:

    rank 3   30,714 s legacy  ->  92 s (dicts)  ->  52 s (arrays)
    rank 4  126,332 s legacy  ->  418 s (dicts) -> 268 s (arrays)

**And, reading the floor code to speed it up, a bug.** D44's rule is right — a reducible direction
`p_t^a p_φ^b H^c` counts only if its ζ-correction fits the ansatz — but its implementation used
`c·Σ_{i+j=2} H_iᶜ⁻¹·HS_j`. That is the O(ζχ²) coefficient **only for c ≤ 2**. For c = 3, which
first exists at rank 6, the χ² coefficient of `3·H_K²·HS` is

    3 [ H0²·HS2 + 2·H0·H1·HS1 + (H1² + 2·H0·H2)·HS0 ]     not     3 [ H0²·HS2 + H1²·HS1 + H2²·HS0 ]

and only the χ² piece was ever tested, though the χ⁰ and χ¹ pieces must fit too. **So rank 6's
"16 of 16 REPRESENTABLE" (§135) was never measured on the right object.** `scripts/_kt_floor.py`
computes the exact series for any c, tests every piece, and does it in the polynomial ring (`Q`
divides `den·P` with bounded degree — an exact test, no gcd): **2 s where the expression version ran
17+ minutes at rank 6**. Validated against the expression test in both verdicts, including the D44
negative (rank 4, denpow 6: H²'s χ² piece does not fit).

**The answer did not change: the corrected H³ correction is representable at denpow 8, box 30×28,
in all three pieces — the floor is 16.** Recorded anyway, and in full, because a number that was
right by luck was not measured, and nothing about the wrong formula guaranteed the same luck at
c = 4 (rank 8).

**In the gate:** KT5 (arrays) and KT6 (floor) join KT1–KT4 in `verify.sh`.

**Addendum, same evening — the arrays were still too big, so the layout was tightened.** Rank 6's
ζχ¹ (46.8M nonzeros) ran at 4.4 GB in Python and 3.1 GB in Rust, which put ζχ² (~130M) back near
15 GB. Not abandoned — measured, then tightened (and the user's rule applies: a setback is a reason
to look again, not to fall back):

- **Python** stores `uint32` (12 B/entry, not 24), keeps the rescale as a list of chunk parts that
  are never concatenated, renumbers rows through a dense `(e, j, k)` lookup table instead of
  `np.unique`, writes the KTM file straight from the parts, **drops its copy before Rust starts**,
  and runs the nullspace guard from the file through a memory map.
- **Rust** takes the matrix by value, builds each block's rows directly (a counting pass sizes every
  row exactly — no tuple list, no CSR copy), drops the coordinate arrays as soon as rows exist, and
  hands each block to its worker by value so it is freed when solved. Measured on rank 4's real ζχ²
  matrix (32.6M nonzeros): **peak 1.62 GB → 1.03 GB (53 → 34 B/nonzero), same speed, identical
  nullspace**. The two clippy suggestions went in with it (`as_chunks`; no index loop).

Validated at every step: KT1 (random families, 1 and 4 threads), the real-operator array test through
the file path (guard both ways, via the memory map), and rank 3 end to end — all four checkpoints
identical to legacy again. **Rank 6's ζχ¹ on this pipeline: 30 of 30, checkpoint identical to legacy
(12,600 expressions, 21,235,858 bytes) — the level that took ~30 h in the legacy run.**

**Two operational controls the user asked for, now real and tested on a live run:**
`scripts/kt_pause.sh <pid> stop|cont` (refuses anything that is not this repo's `_kt_double.py`;
pauses the Rust child too) — tested: state `T`, log frozen for 15 s, resumed, finished, checkpoints
identical. And the core count is re-read before every solve from `data/KT_THREADS` (or a per-run
`data/KT_THREADS.<pid>`) — tested: 1 → 4 threads mid-run.

## D51 — literature check for the all-ranks direction: the gap is real, the obstacle is the order (2026-09-19)

**Why this check, and how.** Every closure so far is one rank at a time (CLAUDE.md §3, ceiling 2).
Morales–Ramis differential Galois theory is the known way past that ceiling: it rules out *any*
additional meromorphic first integral, every rank at once — it is what closed ZV in 2013 (D47). Before
building anything, per the ZV lesson, the search crossed every neighbouring vocabulary (Killing
tensor / Carter-like constant / hidden symmetry / first integral / Liouville / meromorphic /
differential Galois / Morales–Ramis / Ziglin / Kovacic / Melnikov / chaos) with the spacetimes (sGB,
EdGB, dCS, higher-derivative-corrected Kerr, bumpy / deformed Kerr). A web sweep, not a citation-graph
audit: "not found" below means not found by it.

**What is in print for this metric.**
- **Owen, Yunes & Witek**, PRD 103, 124057 (arXiv:2103.15891, v4 Jan 2024), read from the abstract
  page: small coupling, slow rotation; both spacetimes Petrov type I; Killing equation solved **through
  rank 6 in dCS but only rank 2 in scalar Gauss–Bonnet**, no nontrivial tensor found; they *conjecture*
  no fourth constant. **So §131, §133 and §137 (sGB ranks 3, 4, 6) go past the published sGB result.**
- **Deich et al., "Chaos in Quadratic Gravity"** (arXiv:2203.00524): Poincaré sections in sGB and dCS,
  chaotic features that are tiny and near the horizon — numerical, "likely" no fourth constant.
- **Cárdenas-Avendaño et al.** (arXiv:1804.04002), dCS only: *no* chaos found in sections through
  fifth order in spin, and the opposite conjecture — the exact dCS black hole *may be integrable*.
  **The dCS literature holds two contradictory numerical conjectures.**

**What analytic all-rank methods have been applied to.** ZV (Maciejewski, Przybylska & Stachowiak
2013), Chazy–Curzon, D-brane backgrounds, Schwarzschild perturbed by discs/rings and by gravitational
waves (Melnikov), and the tidal-quadrupole problem (arXiv:2607.27129, a Carter-deformation argument).
**None to sGB, EdGB, dCS, or any higher-derivative-corrected Kerr** — the gap D47 guessed at is there.

**How ZV was done, i.e. what would have to transfer** (read from the paper body): linearise around
radial motion through the centre in the equatorial plane — an invariant 2-D subsystem; change the
independent variable to the radial coordinate so the normal variational equation becomes
`ξ'' = r(x) ξ` with **rational** r; run Kovacic's algorithm to show it has no Liouvillian solution;
exclude a few special parameter hypersurfaces. Our metric has every ingredient: the equatorial plane
is invariant (the reflection symmetry was verified exactly, D48), the zero-angular-momentum radial
motion is a 1-D quadrature, and every coefficient is rational in x.

**The obstacle, stated before anyone builds: the order at which integrability breaks.** In the double
expansion the obstruction first appears at **O(ζχ²)** — static sGB is spherically symmetric and O(ζχ)
keeps Carter (the §130 prose). A first-order Morales–Ramis or Melnikov argument in a single small
parameter sees nothing there. Two honest routes, neither free:

1. **Finite-ζ Morales–Ramis on the truncated Hamiltonian.** Rigorous and algorithmic, but it proves
   non-integrability *of the truncation at finite coupling* — the object CLAUDE.md §1 already says is
   not the physical one, and a truncation being less integrable than its parent is not surprising. It
   removes the rank ceiling for the truncated metric; it does not touch analyticity-in-ζ physics.
2. **Higher-order variational equations** (Morales-Ruiz, Ramis & Simó, 2007) or a higher-order
   Melnikov integral, organised in the same (ζ, χ) double expansion as the tower. This is the version
   that matches what the metric can support, and it is harder: the monodromy correction has to be
   carried to the order where Carter first fails.

Tooling: SymPy 1.14 has **no Kovacic solver** (checked); it would have to be written, and validated on
known cases (ZV δ=2 must come out non-Liouvillian; Kerr's own NVE along the same orbit must come out
solvable — the positive control, D40's rule that a control must be able to fail).

**Recommendation.** Route 1 first, but framed correctly: as a *tool-building* step with Kerr and ZV as
controls, whose sGB answer is reported as a statement about the truncated Hamiltonian. Then judge
route 2 with that tool in hand. Discuss with the user before building (feedback-checkpoint-discuss).

## D52 — a surviving higher-rank direction is not new until it is shown not to be a power of a rational integral (2026-09-19)

**What forced it.** §140 found deformations of Kerr where a rank-4 Killing tensor survives with no rank-2
one beneath it — which the instrument's bookkeeping would report as an IRREDUCIBLE rank-4 tensor. It is
not a new symmetry: from K = Q² + εK₁, G = K₁/(2Q) solves Carter's own first-order equation. Carter
survives as a rational function; Carter² is its square.

**The rule.** "Irreducible" as computed here means *not a polynomial combination of lower-rank Killing
tensors*. That is weaker than *functionally independent*. Before any surviving direction above the
floor is called a hidden symmetry: (1) for each lower-rank integral Q whose power it contains, form
G = K₁/(m Q^(m−1)) and check whether it solves Q's first-order equation — if yes, it is a power of a
rational Q; (2) only a direction that survives this is a candidate for new structure. This is the ZV
residual of CLAUDE.md §2 made operational, and its first instance.

**What it does not change.** Every sGB verdict (ranks 2–6) landed exactly on the floor, so nothing
above the floor was ever claimed. The rule matters for the day something is.

## D53 — dCS is not a fresh ladder; the open question there is the rational class (2026-09-20)

**Why re-read a paper already cited.** Queuing "dCS next" needed the published result read at method
level, not abstract level. Owen, Yunes & Witek (PRD 103, 124057; arXiv:2103.15891v4) was pulled and
read in full. It confirms what D47 already recorded and adds three details that change what is worth
running.

**What they actually did.** Ansatz Eq. (38): `K = K^(0,0) + χ'K^(1,0) + χ'^2 K^(2,0) + ζ'χ'K^(1,1) +
ζ'χ'^2 K^(2,1)`, each `K^(m,n)` a completely symmetric tensor field of **arbitrary functions of
(r,θ)**. Solved order by order, "verified by hand, in Maple and in Mathematica". Through O(χζ) the
general solution is exactly the reducible span — products of `t^α`, `φ^α`, `g_αβ` and the dCS-corrected
Carter tensor `ξ^CS`. At O(χ²ζ) the system is **inconsistent**: 20 functions against 35 equations, with
a subset forcing a functional form another subset forbids. Ranks 3–6 repeat the pattern.

**Three consequences.**
1. **Ranks 2–6 in dCS are closed, at our exact truncation.** Running them here is reproduction. Ranks
   7–8 would be new but near-worthless: D42 says even ranks re-measure a Q-power rung already seen.
2. **Their ansatz is stronger than ours in one respect and weaker in another.** Arbitrary functions of
   (r,θ) beats our polynomial box (ceiling 3 of CLAUDE.md §3 does not bind them). Order-by-order CAS
   PDE solving is weaker than an exact GF(p) nullspace with the reducible span subtracted and two
   primes agreeing. Neither dominates; do not describe our instrument as simply better.
3. **dCS and sGB have the same shape.** Carter survives at O(χζ) and dies at O(χ²ζ) in both. That is
   the precondition for the §138–§142 anatomy to apply.

**The question nobody has asked of dCS.** D52: a Carter that dies as a polynomial can survive as a
*rational* integral `Q + ζ·K₁/(2Q)`, invisible to every polynomial Killing search including theirs,
and its powers `Q^(m+1)` reappear as polynomial tensors at rank `2(m+1)`. The dCS literature holds two
contradictory conjectures — OYW/Deich (no fourth constant, from Killing tensors and from chaos) versus
Cárdenas-Avendaño (a fourth constant, from chaos *shrinking* with spin order). **A rational Carter
reconciles them exactly**: no polynomial Killing tensor and no chaos, simultaneously.

**And it is falsifiable against a published number, which is why it is worth running.** §142 measured
pole-order saturation at 2 in the ℓ=2 shape sector. Pole order m predicts a surviving direction at rank
2(m+1). So if the dCS O(χ²ζ) obstruction sat at pole order ≤ 2, a rank-6 direction would exist — and
OYW report none. Our framework therefore *predicts* their null, and the run either confirms the
framework on a substrate it was not built from, or produces a conflict that has to be resolved. Both
outcomes are results; neither is reproduction.

**Scope note.** dCS's leading correction is odd-parity and O(χζ), so `_kt_pole_reduced`'s assumption of
zero sources below χ² does not hold. This needs the general tower (`_kt_double` / `_kt_anatomy`), not
the reduced single system. Rank-6 scale, which is 552 s of solve, not a week.

## D54 — the residual guard may be probabilistic, because its error is one-sided (2026-09-20)

**What forced it.** The rank-8 ℓ=4 run spent 2.9 h in the Rust nullspace and then **1.7 h of CPU in the
residual guard** — `residual_count_file` streams the whole 585 M-nonzero level matrix once per
nullspace vector, 941 times. More than a third of the run, and every future rank-8 run pays it again.
Found by benchmarking the inner loop (11.2 ns/nnz) rather than by guessing; the guess before measuring
was 5× too pessimistic, which is its own small lesson about ETAs.

**The replacement.** `_kt_coo.guard_vectors` (KT_GUARD). Collect the residuals as one matrix
`R = M Vᵀ`; the guard asks whether `R == 0`. Rather than check all 941 columns, check `R z` for k
uniformly random `z` over GF(p). If `R ≠ 0` then `R z = 0` with probability at most 1/p per probe, so
k probes give a false pass with probability at most `p^-k` — at p ≈ 2³¹ and k = 4, below 1e-37.

**Why this is a guard and not a sample, which is the whole argument.** `M (Σ zᵢ vᵢ) = Σ zᵢ (M vᵢ)`. If
every `M vᵢ` vanishes the probe vanishes *exactly*, so a nonzero probe residual **proves** a defect.
The error is one-sided: no false alarms, and a bounded chance of a false pass. A guard that checked a
random *subset* of the vectors would have the opposite and unacceptable profile — it would miss any
defect outside the subset with probability nowhere near `p^-k`. **This distinction is the reason the
change is allowed at all**, and D40's rule still binds: the control must be able to fail.

**Validated in both directions before use** (`scripts/_kt_guard_test.py`, gate KT7). On exact GF(p)
data, over 6 random systems: full and Freivalds agree on a correct nullspace; the probe combination is
itself exactly in the nullspace; and across 150 corruptions of **one unit in one coordinate of one
vector** — the smallest defect there is, and the one a sampling guard would most likely miss — both
`freivalds:4` and `freivalds:1` detected every one. End to end, a real rank-4 run under both policies
produced byte-identical physics output (4 probes against 269 vectors).

**Default unchanged, deliberately.** `KT_GUARD=full` remains the default; the fast path is opt-in via
`KT_GUARD=freivalds[:k]`. Both policies now **print which one ran**, so a result's log states what
protected it — the provenance rule of CLAUDE.md §5 applied to the guard itself rather than to the data.

## D55 — the pole-order saturation predicted two published nulls, and that is the result (2026-09-22)

**What happened.** D53 reframed dCS: not a rank ladder (Owen–Yunes–Witek closed ranks 2–6 at our own
truncation) but the rational-class question. It also recorded a *prediction*: §142 measured the pole
order saturating at 2, and by §141's dictionary a rational Carter of pole order m reappears at rank
2(m+1), so **if the framework is right there can be nothing at rank 4 or rank 6 for dCS** — which is
exactly what OYW report. §145 ran it. Rank 4: floor 9, zero above. Rank 6: floor 16, zero above.

**Why this is worth a decision entry rather than a results line.** The dCS null itself is a
confirmation of published work. What is new is that a picture built entirely from deformations of
Kerr in the sGB programme made a *falsifiable, dated, pre-registered* claim about a different theory
and it held. The prediction could have failed in the most visible way available — a survivor above
the floor would have contradicted a published null and forced one of us to be wrong.

**The rule this sets.** A framework earns its keep when it constrains a substrate it was not fitted
to. Before the next structural claim from the pole-order picture, ask what it forbids elsewhere and
whether anyone has already looked. That is cheaper than a new run and it is the only way this kind
of picture can be tested at all — its own family will always agree with it.

**What it does NOT license.** The OYW / Cárdenas-Avendaño disagreement is not resolved. We eliminated
one candidate reconciliation — a low-pole-order rational Carter — and eliminated it cleanly. The
remaining candidates (non-perturbative structure, pole order beyond our saturation, or the chaos
result being numerical artifact) are not separable by this instrument, and saying otherwise would be
the §1 overreach the repo is built to avoid.

## D56 — independence is a property of INPUTS, not of repositories (2026-09-22)

**What happened.** The bridge audited its own founding claim — *"the repos are kept ignorant of each
other, so agreement is evidence and not an echo"* — and killed it. The claim appears three times in
their repo, each time as a statement of policy or a defence of it, and **had never once been
measured**. Not "confirmed too easily" — there were no observations of any kind attached to it.

**The rule that replaces it, in their words:** *independence is a property of inputs, not of
repositories. Two repos agreeing about an object one of them supplied is one measurement.*

**What this repo contributed, and what it cost us.** Asked for our side, we found and reported:

  - **Unlogged channels exist.** Three siblings have messaged this session directly on their own
    sockets, never through the bridge. Their census could not see any of it. We also flagged that our
    own "no echo happened there" is a SELF-REPORT, not a measurement — a census asking each repo what
    it received is answered by the same recognition whose failure produces unlogged transfers.
  - **One entry against ourselves.** 28bee32: we verified the residue (ours to check) and accepted an
    operational bridge (not ours), then committed the whole as a result. It was wrong. No agreement
    was counted, so not an echo by their definition, but it is unverified cross-repo content becoming
    a committed claim here — the failure the policy exists to prevent. Logged as their edge 9.
  - **One refusal that is the strongest evidence the discipline is real**, and it had to be applied to
    the bridge: when they framed our algebra, our grading and tabula's measurement as three
    independent legs, we cut it to two — *two readings of ONE computation on ONE object from ONE
    pipeline*. Inflating an evidence count is the same error whoever does it.

**RELAYED AND NOT VERIFIED HERE** (handled like CLAUDE.md §1's external numbers): they report that
BlackHole is a fission product of SpaceTime, split 2026-06-13, with three docs byte-identical today,
verified by md5 and git log on their side. **We have not checked this.** If true it bears on the
premise of CLAUDE.md §0 — that the siblings are mutually ignorant — and that is the user's call to
make, not ours to edit into the operating contract on a peer's say-so.

## D57 — SEALED-CONSTRUCT / BLIND-SCORE, named as the standing repair

The audit found exactly one mechanism in the fleet that restores independence **by construction**
rather than by policy, and it is ours, built for §120 and never described as a fix:

    1. The supplying repo CONSTRUCTS the object and commits a SEALED verdict before transmission
       (data/bridge_round8/G2_candidate_A.json alongside G2_candidate_A_SEALED.json).
    2. The receiving instrument SCORES IT BLIND -- metric only, no labels, no motivation.
    3. Only then is the seal opened and the two compared.

We called it "designed adversaries" and filed the lesson under catalog homogeneity, so the repair went
unnamed and unreused for months. **It is now the standing protocol for any object leaving this repo
for measurement elsewhere**, and it composes with the eight-field scope manifest: the manifest makes
the object's claims legible, the seal makes the comparison independent. The A/B/C triple of
2026-09-22 was this protocol's second use.

## D58 — our own substrate caveat cited the wrong object (2026-09-22)

**Found by a sibling pointing at a paper, not by us.** CLAUDE.md §1 has quantified our double
truncation since it was written by quoting *"the O(χ²) spin-truncation error of the Kerr 220 mode at
~6% at χ=0.69 and ~19% at χ=0.90"*. **The Kerr 220 mode is a QNM frequency. Our substrate is the sGB
metric.** Different theory, different function, different series, potentially a different radius of
convergence. The number is correct about something else.

**The tag did not help.** It was marked "(relayed, not verified here)", which guarded its VALUE and
said nothing about its REFERENT. **A provenance tag is not a relevance tag** — and this one sat in the
operating contract, the file loaded at the start of every session, as the quantitative statement of
our substrate's limitation.

**The right measurement is now available.** arXiv:2406.11986 (PRD 110 064019) supplements the sGB
metric's spin series to **40 orders, raw and unresummed** — read from the body, since the abstract
quotes only the second-order frequency fit, one of three separate expansions in that paper.
DeepStrain is running the ratio test with their validated estimator.

**PRE-REGISTERED, so the interpretation is fixed before the number exists:**

    changes NO verdict     ranks 2-8 closed on the truncated metric remain exactly that. An exact
                           statement about a truncated object does not change when you learn how
                           good the truncation is.
    changes the CAVEAT     §1's limitation goes from a relayed number about the wrong object to a
                           measured one about ours.
    SHARPENS it a lot IF   R < ~0.9: at EMRI spins the O(χ²) truncation would then be outside the
    the radius is small    domain of convergence rather than merely inaccurate, and §1's "whether
                           the object is the right one" stops being a matter of degree.

**Hazard attached to the measurement, from their estimator work:** a SAME-SIGN competing singularity
biases a Domb–Sykes radius upward by up to +12% while leaving the ratio sequence monotone, smoothly
decelerating and free of sign flips. A clean-looking sequence is therefore not evidence of a single
dominant singularity — and with a coupling and a deformation both in play, sGB is *more* exposed to
this than vacuum Kerr, not less. We asked for the same-sign control run on this series specifically
rather than cited from an earlier calibration.

### D58, addendum — one structural fact survives; two were withdrawn at source (2026-09-22)

Three structural facts about the supplement were supplied, recorded here, and then **two of the three
were withdrawn by the supplier within hours** — before any measurement rested on them. Struck rather
than deleted, because the mechanism is the useful part.

**SURVIVES.** The coefficients are **rational functions of r** (powers 2–66), not numbers. **So the
radius may depend on r, and "what is R for the sGB metric spin series" is UNDER-SPECIFIED as asked.**
The honest form is *R at a stated r*; whether it varies is itself a result, and §1 may not be able to
carry a scalar caveat at all. This holds whether or not the parse ever finishes, and is independent
of which symbol turns out to be the spin.

**WITHDRAWN — "α appears only at power 2, so the supplement is O(α²), first order in ζ".** The census
counted `SuperscriptBox["α", n]` and so **could not see power-1 occurrences at all**; there are 2,233
bare α against 924 superscripted. The order in α is unknown. **The inference that this bounds the χ
half of our double truncation and leaves the ζ half untouched does not follow from anything measured.**

**WITHDRAWN — "the expansion variable is u = χ², so R_χ = √R_u".** The *evenness* holds, but two
symbols, χ and a, both appear only at even powers 2–40, and a single term carries χ²·α·a² together.
Which is the spin was assumed from the title, never checked against the paper's own definitions.

**THE MECHANISM, which is this month's species in a new costume.** Both bad facts came from regex
censuses that **answered a narrower question than the one asked of them**: a pattern requiring an
explicit exponent reports "α is always squared" when it means "among α's carrying a visible exponent,
all are 2." *A count that cannot see power 1 will never report power 1.* And a further census of
theirs returned **zeros for both symbols** from an over-escaped pattern — zero being exactly what a
working census returns when there is nothing there, which is rule 86's failure-as-a-value, logged by
that session two days earlier and then reproduced.

**Gate status:** the parser's evaluation gate has caught three distinct faults in sequence and failed
loudly each time rather than emitting a number. **No radius until a golden test reproduces something
the paper published.**

**Resolution, same day.** The supplier read the paper's own symbol definitions instead of inferring
them, and re-ran every census behind a positive control (each pattern first made to return 3 planted
matches before any count was believed). **χ is cos θ**, defined in one line of the paper; `a` is the
dimensionless spin. So the expansion is in `a` at even powers to 40 — u = a², 20 ratios, R_a = √R_u —
the angular dependence rides on χ = cos θ, and α sits at powers **1 and 2**, so the withdrawn α-order
claim stays withdrawn and is not replaced by a different one.

**The surviving fact got broader, not narrower.** The coefficients are functions of **r and θ**. The
honest form of the question is *R at a stated (r, θ)*; whether R varies over the angle is a second
question nobody has asked. §1's "under-specified as asked" holds more strongly than either of us
first wrote it.

**The root cause was upstream of the regex.** Their account: the title said "40th order in
dimensionless spin", a symbol was found with powers to 40, and *the title assigned the variable* — `a`
sat in the same expressions with an identical signature and was never asked about. The census method
was downstream of an attribution already made. Our matching half: we adopted a variable attribution
with no measurement behind it, from a supplier who had just said the method was regex. **Neither side
needed new information to catch this; the paper defines χ in one line and neither read it.**

**The positive control paid for itself on its first run** — its own probe construction was broken for
the escaped symbols, so it reported CONTROL FAILED for exactly the two patterns whose numbers had
already been sent. The two ABSENT rows in the corrected census are now *measurements* rather than
silence, because the pattern is demonstrated to count.

**One number still to watch, flagged back:** the corrected census reports `a` with **1 bare
occurrence** against 2,349 superscripted. One is not zero, and rule 104 is precisely that a count of
one in the column that would falsify "even powers only" deserves to be looked at rather than rounded
down.

**The flagged `a` resolved, and it turned into the exercise's first passed check.** The single bare
`a` is not in the metric functions at all: it is the overall factor in **Ω**, the frame-dragging
angular velocity, which *must* be odd in spin because it reverses when the hole spins the other way.
Per-cell counts: φ, H₁–H₄, κ all show bare 0 (even); Ω alone shows bare 1 (a × even = odd). **So the
parity split is the physics**, the evenness underpinning u = a² now rests on a control-validated zero
rather than on a one with an explanation attached, and the supplier has adopted parity as a standing
parser check — a parsed Ω coming back even, or a parsed H odd, condemns the parse regardless of the
golden test. Worth recording because it is the first thing in the exchange that **could have come out
wrong and did not**; everything before it was a check that fired or a claim that was withdrawn.

### D59 — before generalising from a sweep, write down what it held CONSTANT

§143 swept the angular degree (ℓ = 2 → ℓ = 4), found the pole-order increments (2, 1, 0) unchanged,
and concluded they hold "for every angular sector". Both cases were **polar**. p_φ-parity — which
turns out to be an exact grading of the whole problem — was constant across the entire evidence base
and therefore could not show up as a variable. The axial sector gives (0, 0) and (1, 0) instead.

**The rule.** A sweep licenses a claim about the axis it moved, and says nothing whatever about the
axes it pinned. Report *"the increments do not depend on the angular DEGREE, over ℓ = 2 and ℓ = 4,
both polar"* — which is true, useful, and was what was measured. The failure mode is not sloppiness:
the over-general claim is the **widest one consistent with the data**, which is precisely why it is
attractive and why it is wrong. So the discipline cannot be "be careful"; it has to be mechanical —
**list the held-fixed variables next to the varied one, in the write-up, every time.**

**Two corollaries, both bought here.**

*A positive control must live in the sector under test.* §142/§143's gauge controls drag along r and
θ and therefore sit in the polar sector; they show the system is not killing things generically but
cannot show the solution box is wide enough for an **odd** deformation. A null in a new sector needs
a known-keeps-everything object **in that sector** (D40) — a φ-drag here. Added, and it passes.

*A slot's name describes its angular pattern, not the block its truncated slice lands in.* `drag3` is
the physical odd ℓ = 3 slot, but it enters at O(χ¹) and the O(χ²) slice a reduction consumes is
p_φ-**even** — the χ¹ deformation beaten against the background's own χ¹ dragging. Feeding it to the
reduced solver tests the polar block under an axial label. Checked with one `Poly.monoms()` call per
slot, now battery KT8.

**D58, the measurement lands (2026-09-22, late).** The supplier sent the golden test side by side, as
asked: Yunes & Stein 2011 Eq. 8 static scalar, 1/rᵖ coefficients relative to 1/r, reproduced 1 and 4/3
against published 1 and 4/3, other powers ≤ 5e-44. Three internal gates tie the other cells together
(parity from the parsed expressions; horizon rigidity Ω⁽¹⁾ = Ω⁽⁰⁾(H2−H4) at r₊ to 6e-41; κ⁽¹⁾
re-derived from H1–H4 to 1e-29). Pre-registered, then measured, the O(a²) truncation error against the
a⁴⁰ series:

    a = 0.69 / 0.90       H1-H4 (r=3M, 6M)    1.1-6.1% / UNRESOLVED (reference not converged)
                          scalar              ~4.8%   / ~31%
                          kappa(1)            22.6%   / 93.8%
                          Omega(1)            84.6%   / 166%
    radius, Domb-Sykes in u = a^2:   Omega(1) R = 1 in every window;  kappa(1) in band in 2 of 3
    exploratory exponent at a = 1:   Kerr control +0.495 (true 0.5); kappa(1) -0.48; Omega(1) -0.54

Artifact: `ringdown_spectroscopy/results/38_sgb_supplement.json` @ 6ba9cea. **Relayed, not verified
here.**

**Which of these numbers is ours.** Our Killing-tensor search consumes the **metric functions**, not
Ω or κ, so our substrate's spin-truncation error is the H-row: **1–6% at a = 0.69 away from the
horizon, unresolved at 0.9**. Quoting the 166% as "our error" would be the Kerr-220 mistake inverted:
right source, wrong referent. **But** κ⁽¹⁾ is built from H1–H4 *evaluated at r₊*, so its slow
convergence is indirect evidence that the metric functions converge slowly **at the horizon**. Our
Killing tensor is global, so that matters. The near-horizon H truncation has been requested and is not
in hand. §1 says so.

**Verified here, not relayed:** the supplier flagged main.tex's printed Ω⁽⁰⁾ = a/(2Mb) as disagreeing
with the paper's own metric, a/(2M(1+b)). The textbook Kerr value is Ω_H = a/(r₊² + a²) = a/(2Mr₊) with
r₊ = M(1+b), so a/(2M(1+b)): the metric and the notebook are right, and the printed formula is the
misprint (or a different definition).

**Read as physics, labelled exploratory:** R = 1 with exponent −½ is what a branch point in b = √(1−a²)
at extremality produces. The Kerr background term vanishes like √(1−a²) there while the O(ζ)
correction diverges like 1/√(1−a²), so if this holds the small-coupling expansion is non-uniform
near extremality. At a = 0.9 the factor is 2.3: something to watch, not yet a breakdown.

**D58, the near-horizon number (2026-09-22, night; post-hoc, relayed — `38_sgb_supplement.json` @
cadfed9, block M1_posthoc).** Asked for because κ⁽¹⁾'s slow convergence implicated the metric functions
at r₊. At a = 0.69 (r₊ = 1.724M), O(a²) truncation of the metric functions:

    H4 (never near zero, the clean trend):  1.5 r+ 6.0%   2.2M 17%   1.2 r+ 26%   1.05 r+ 64%   r+ 88%
    H3:                                     0.2-5% everywhere
    H1, H2:  cross ZERO near the horizon, so relative errors (up to 1245%) are artifacts; their
             ABSOLUTE errors, 0.04-0.18, are comparable to H4's there

**"A few percent" describes our substrate only beyond ~1.5 r₊.** Inside ~2.2M it is off by tens of
percent already at a = 0.69. Our Killing tensor is a global object, so §1 now says the O(χ²) substrate
is a poor approximation near the horizon even at moderate spin. The supplier caught the zero-crossing
artifact themselves (H2's non-monotone r-dependence) before sending, and now prints absolute error beside
any entry whose value is under 20% of the largest |Hᵢ| — the right column for a global object.

At a = 0.90, with a conservative monotone tail bound on the reference (last · a²/(1−a²)): κ⁽¹⁾ 93.8 ±
2.4%, Ω⁽¹⁾ 166.2 ± 3.0%, scalar 30.5–32.4 ± 0.07%. The scalar's small bar is because its coefficients
decay faster; its exponent is not the horizon quantities' −½.
