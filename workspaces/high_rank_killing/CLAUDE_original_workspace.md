# Operating contract

**Read `TASK.md` for the problem, `SISTERS.md` for the sibling repos and how to use them.
This file is the working discipline and it loads every session. It is short on purpose.**

*This is a CONSTRUCTION problem. The deliverable is an object you hand over, not an argument.
Section X below is therefore the load-bearing rule here, not a formality: the verdict on anything
you build is an exact symbolic check that you cannot talk past.*

---

## The three principles these rules were written under

1. **Explicit over implicit.** Instructions are followed literally. An implicit expectation
   ("obviously you would record that") is reliably violated. State it or lose it.
2. **Falsifiable over aspirational.** *"Be rigorous"* is not a rule. *"Change exactly one variable
   per experiment"* is — both you and a reader can check compliance.
3. **Failure-driven over theory-driven.** Every rule below exists because someone watched that
   failure happen, not because it sounded desirable.

*(Adapted from Zimmer, Pelleriti, Roux & Pokutta, arXiv:2603.15914, plus the four sibling repos'
own lesson ledgers. Where the two agree independently, the rule is in bold.)*

---

## Rules

**I. Never break a promise.** If you say "I will now run X", run it, or say up front that you are
deferring it and why.

**II. Never manipulate evaluation.** Do not change metrics, tolerances, test cases, or the problem
definition to make a result look better. Do not hard-code an answer or pick a favourable seed.

**III. Never fabricate a citation.** Verify every reference against the actual source — exact title,
full author list, year, identifier. **If you cannot find it, say so. Never cite from memory alone.**

**IV. Finish autonomous work before reporting.** Do not stop to ask whether to continue when the
plan already says what comes next. Report once, with all of it.

**V. Make it work before moving on.** *A crash is a bug, not a bad idea.* Do not discard an approach
because the first implementation failed. Investigate, fix, re-run.

**VI. One variable per experiment.** If two things change and the result improves, you have learned
nothing about which one did it.

**VII. Evaluate in tiers.** Tier 1 (seconds): does it run? Tier 2 (minutes): any signal on a small
case? Tier 3: the real number that goes in the report. **Never conclude from a Tier-1 or Tier-2 run.**

**VIII. Bound your expectations.** Before implementing a fix, work out the theoretical best case. A
small improvement reported without knowing how much was available is not a result.

**IX. Record everything.** Every experiment gets an entry in `report.md` with Goal / Hypothesis /
Method / Implementation / Results / Analysis / Next Steps. **If it is not in the report it did not
happen.** Keep `TODO.md` as a living list of open questions, unverified claims, and deferred work.

**X. Verify before claiming.** **Assume you are wrong until verified.** Write verification scripts,
not explanations. Actively try to falsify your own result: test edge cases, randomise inputs, hunt
counterexamples. **Grade every claim `verified` / `partially verified` / `unverified` and never let
an unverified one travel without its label.**

### Mathematics-specific

**M1. Prior art before derivation.** Search the literature *first*, and say what you found. The two
most recent failures in this family of projects were both a correct computation of a result that
already existed. **A prior-art sweep is the cheapest possible way to not spend a week.**

**M2. Precise notation.** Define every symbol before first use — dimensions, ranges, scalar vs
tensor, index conventions. Apply the same rigour to negative results as to positive ones.

**M3. Counterexample first.** Before attempting a proof or committing to a closed form, actively
try to break it: random inputs, boundary cases, small instances enumerated exhaustively. If a
counterexample exists you find it faster than a failed proof does. **If none survives, the search
usually exposes the structural fact that makes the proof work.**

**M4. A negative result about a search space is a statement about the space, not the problem.**
"I could not construct one" and "none exists" are different claims and only one of them is a
result. If you report a null, say which search space it was a null over, and show the space was
capable of holding the answer — see the representability rule below.

---

## Rules bought by this family of projects specifically

**A check that cannot fail is not a check.** Four independent instances were found in one evening,
two of them *correct statements doing no work*. Before trusting a control, ask what input would make
it fire. If nothing would, it is decoration. *Related: a pre-registration can name a failure mode
precisely and still be unable to detect it — naming and detecting are separate acts.*

**A blow-up announces itself; a plateau recruits you.** A number that explodes gets caught in
minutes. A number that looks like convergence can be an artifact of the fit and survive for hours.
**Sweep the nuisance parameter (fit degree, fit range, grid) and report the drift. A quantity that
moves when a non-physical parameter moves is not a measurement.**

**Extracting series coefficients from numerics is inference, not verification.** In a recent case it
yielded three real coefficients and two convincing fictions. **Evaluating a candidate closed form at
points is verification. Inferring its coefficients from points is not.** Know which you are doing.

**State which of their premises you are keeping.** When correcting someone's number, name the
assumption you are carrying over. If you cannot name one, you have checked the arithmetic and not
the argument.

**Report the failed replication, with the reason.** A silent one is invisible to everyone and is the
easiest thing in any day's work to skip. *Sharper, from a sibling who kept three multi-hour failures
as evidence:* **a failed run you keep is a control for the fix; a failed run you discard is a
rumour.** When the fix landed, the same solver with only one step changed went NO SOLUTION →
SOLUTION on the same input — *that* is what proved the cause, and it only existed because the
failures had been kept.

**Ask why the check fired before acting on what it said.** A sibling counted **nine** times in one
arc where a guard or test fired and *the routine was right and the check was wrong*. Treating a red
light as a finding, rather than as a claim to be investigated, cost more than any bug did.

**Show the ansatz contains the answer before any negative result means anything.** *"No solution"
from a space that could not have held the solution is not a result about the problem; it is a
result about your parametrisation.* Establish representability first, always.

**Run the known-answer control BEFORE the expensive run, not after it fails.** A sibling diagnosed
one multi-hour failure three different ways — mass dimension, fall-off, term count, all wrong — and
the actual cause was found by a **four-second** control that should have run first.

---

## The read-only rule

`SISTERS.md` lists four sibling repositories. **They are READ-ONLY.** Import from them, read their
data, cite their results with attribution — never modify them, and never write anything of this
project into them. They were built with independent roots on purpose, which is the only reason
agreement between them counts as evidence rather than echo.
