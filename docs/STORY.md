# The Ansatz Machine: teaching a fuzzer general relativity

*The story of a propose→verify→evolve loop that rediscovered a century of
exact spacetimes blind, built its own memory, survived its own gauge-evasion
tricks, learned modified gravity, and produced a holdout-validated universal
formula for a black hole that has no exact solution. Built in ~2 days on a
laptop with one dependency (SymPy). Repo:
https://github.com/sumit7194/ansatz-machine*

---

## 1. The idea, in CS terms

Einstein's field equations are a balance: geometry on one side, matter on
the other. A "solution" is a metric — the rulebook for distances and clock
rates — that balances the equation *exactly, everywhere*. They are rare
treasures: ten coupled nonlinear PDEs with thousands of terms each, and
essentially every known solution came from a human guessing a simplifying
ansatz. Schwarzschild guessed in December 1915; the spinning version took
until **1963**.

But *checking* a candidate is pure algebra. So: **a fuzzer with a two-tier
oracle.** A genetic program proposes metric formulas (expression trees,
exact rational constants); a millisecond numeric oracle kills almost
everything; survivors face a symbolic proof — and a pass there is a
*theorem*, not a fit. A fingerprint layer (curvature invariants — hashes
that coordinate changes can't touch) dedupes against a century of prior
art. Near-misses breed.

The ground rules came from our gravitational-wave projects: **verifier
before proposer, rediscovery before discovery, null results are results,
blind spots declared rather than bluffed.**

## 2. What the machine did (v1→v4, honestly labeled)

**v1 — it works, and it's lazy in instructive ways.** The verifier was
validated in both directions first (Schwarzschild must pass; sabotaged
metrics must fail). Kerr — the 1963 metric — initially defeated symbolic
verification *in the standard coordinates* (trig swamps; the zero-test is
literally undecidable in general, by reduction from the halting problem),
then verified in **9 seconds** after one coordinate change (u = cos θ)
made every component a rational function, where zero-testing IS decidable.
Then the loop ran blind — and its first "discoveries" were flat space and
the de Sitter ground state: perfect solutions that discover nothing. *A
verifier defines solutions; only a novelty layer defines discoveries.*
With triviality penalties in place, it rediscovered Schwarzschild in 3
generations (~6 s), BTZ instantly, and higher-dimensional black holes it
was never told about — escalating the ones missing from its catalog as
candidate-new, correctly.

**v2 — memory.** Confirmed finds get *generalized*: each constant is
replaced by a symbol and re-proved. Constants that stay free are physics
("hair" — mass); constants the equations pin are law (the cosmological
term's coefficient). Families are persisted; the machine never
rediscovers the same thing twice. The Birkhoff stress test passed with
zero false novelty: in a doubled search space where a theorem guarantees
nothing new exists, the machine found only knowns — including recognizing
*its own* discovery from the previous day.

**v3 — the gauge wars.** Hunting rotating solutions, the optimizer evaded
the objective three times: a constant frame-dragging term (a rotating
*camera*, not rotating *spacetime*), then physically-negligible rotation
that dodged the penalty, then structures whose only exact completions
were gauge-trivial. Every loophole it found was a true fact about gauge
freedom — Goodhart's law running inside general relativity. The fix that
ended the war: an **algebraic finisher** — when evolution gets close,
symbolize the constants, enrich with the falloff terms GP rarely
composes, and let computer algebra solve the family *exactly*, free
parameters and all. Division of labor: evolution finds the leading
structure; algebra nails the tail. Hunts that took 150 generations
dropped to 2–17. The full dimensional ladder then fell in one sweep —
**all 17 static-vacuum rungs (2+1 → 7+1, three Λ sectors), 11
machine-proved solution families** in the catalog.

**v4 — modified gravity, and the real prize-shaped target.** The
Einstein-dilaton-Gauss-Bonnet black hole has been known **only
numerically since 1996**; the published state of the art is a hand-fitted
continued fraction (Kokkotas–Konoplya–Zhidenko 2017, ~0.1–0.3% error,
~10 coefficient functions). The machine: derived the EdGB field equations
itself and matched the 1996 paper symbol-for-symbol; built its own
numerical black holes reproducing the published mass-shift relation;
then — the part that still surprises me — its genetic search
**rediscovered the continued-fraction functional shape unprompted** and
fitted it to 0.23% at a single coupling. The finale: a **universal
formula** across the whole black-hole family. With x = 1 − r_h/r:

    e^Γ = x·A,  e^Λ = B²/(x·A)
    A = 1 + c1(p)(1−x)/(1 + c2(p)x)
    B = 1 + c3(p)(1−x)²/(1 + c4(p)x)
    (c's = quadratics in p — twelve numbers total; RESULTS.md has them)

Final banked version (3-dof structures, cubic coefficients): pointwise ≤0.098%
at every training coupling — finer than the published fit's stated accuracy —
and **0.275% on a sealed
holdout** at a coupling never used in any fit. Pre-registered, holdout
sealed before fitting, first attempt failed honestly at 3.6% (weak
optimizer — replaced hill-climbing with Gauss–Newton + continuation, same
data, 7× better).

## 3. What's new here and what isn't

Not new to science: every exact solution the machine found is in the
literature, and the EdGB comparison is against the published fit's STATED
accuracy (a head-to-head reimplementation of their coefficients remains
open). The final formula is pointwise finer than that stated accuracy with
fewer constants, and within their class on sealed extrapolation. New, as far as we could verify (June 2026): no published work
has an AI/GP loop finding exact metrics with symbolic proof as the
verifier, and no symbolic-regression work on the EdGB metric. The
machinery — three-valued verdicts, invariant fingerprints with declared
blind spots, the algebraic finisher, catalog self-growth — is the actual
contribution, and it's all reproducible: one dependency, `./verify.sh`,
every battery green.

## 4. The lessons that transfer beyond physics

1. **Optimizers find your spec's loopholes, not your intent** — and each
   loophole is information about the problem's symmetries.
2. **Canonicalize before you reason.** Four separate bugs — solver
   failures, invisible coefficients, unprovable zeros — were all "the
   same object in different costumes" problems. So was the physics
   (Schwarzschild in disguise). The machine's central skill and its
   central bug-class were the same thing.
3. **Verify both directions.** Every test battery requires knowns to pass
   AND sabotage to fail. Half the bugs were caught only by the second half.
4. **Seal the holdout before you fit, and report the failures.** The 3.6%
   failure made the 0.53% pass mean something.
5. **NaN is not a number, and `max()` doesn't care.** Twice.

*Living doc. Repo docs (JOURNAL/DECISIONS/GLOSSARY/RESULTS) hold the full
per-day record with every measured failure and citation.*
