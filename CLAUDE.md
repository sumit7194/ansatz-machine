# Ansatz Machine — working brief

*A propose → verify → evolve loop hunting for exact solutions of Einstein's field equations.
Genetic programming proposes metrics, SymPy proves them — theorem or nothing.*

**Read `docs/ROADMAP.md` for the current direction and `RESULTS.md` for the lab notebook. This file
is the operating contract: what is load-bearing, what the open question is, and the failure modes
this repo has already paid for.**

---

## 0. The rule that comes before the work

This repo is one of four sibling projects, cross-validated read-only by a fifth (`trivium` / The
Bridge). The siblings are **kept ignorant of each other's results on purpose** — when two agree,
that is evidence rather than echo.

> **Do not import a sibling's findings into this repo.** Requests arrive as *asks* — a question, a
> candidate metric to test, a control to run — never as conclusions to reproduce. If a result from
> another project is needed to justify something here, that is a bridge leg, and it belongs in the
> bridge. §120–§122 are the correct shape: a bridge round asks, this repo answers with its own
> instrument.

Everything else below is about this repo's own mathematics.

---

## 1. The open question

**Does the quadrupole-deformed Kerr metric admit an irreducible Killing tensor of rank 3 or rank 4
— and more ambitiously, of *any* rank?**

A rank-*r* Killing tensor is exactly a conserved quantity

    F = K^{a1..ar} p_a1 .. p_ar        homogeneous of degree r in the momenta,   {H, F} = 0

Kerr carries one at rank 2 — the Carter constant — and that single object is why Kerr geodesics
separate. Almost nothing else has one. Whether that is structural or a coincidence of type-D vacua
is not settled, and it is not a curiosity: the absence of a Carter-like constant means orbits are
not integrable, which is an assumption the EMRI waveform programme is built on.

> **But keep the motivation and the claim apart, because they are not the same statement.** What
> this repo can establish is *"this metric admits no irreducible Killing tensor of rank r, within a
> stated ansatz, analytic in the coupling"*. What the paragraph above reaches for is *"real orbits
> around real objects are not integrable"*. The exactness of a GF(p) null bears entirely on the
> first and **not at all — not weakly, not with a large error bar, but not at all** — on the second.
> The gap between them is the substrate: our sGB metric is a **double truncation, at O(ζ) and
> O(χ²)**, and an external measurement (relayed, not verified here) puts the O(χ²) spin-truncation
> error of the Kerr 220 mode at ~6% at χ=0.69 and ~19% at χ=0.90 — and χ~0.9 is where EMRI central
> objects actually sit. **The computation is exact; whether the object is the right one is a
> separate question, and only the first is protected by working over a finite field.**
>
> *Which way the gap cuts is worth stating, because it is not symmetric.* Finding a Killing tensor
> **present** in a truncation would be the fragile result — truncations are often more symmetric
> than what they approximate, so an accidental symmetry is ordinary. Finding it **absent** is the
> robust direction: restoring a hidden symmetry by adding higher-order terms takes a conspiracy
> nothing supplies. **With one caveat that is our own §3 ceiling in a second coat** — that
> robustness argument assumes analyticity. A symmetry of the full metric that is non-perturbative
> in ζ or χ is not "fine-tuning"; it is simply invisible to an order-by-order method, and no
> amount of agreement between truncation orders would reveal it.
>
> So: report the null as exact for the truncated metric, **strongly suggestive** for the physical
> one, and never as a statement about EMRI orbits. That last step is a different claim needing a
> different instrument, and this repo does not have one.

**Why this repo can attack it at all.** Most integrability claims in the literature are numerical
null-space screens over sampled orbits — they can only ever report *we did not find one here*. An
exact linear-algebra null over a stated ansatz, over GF(p) with two primes, is a statement about
the equation. **A negative result is a THEOREM, not a screen.**

**Prior art swept.** Nothing excludes rank-3 or rank-4 for Kerr or deformed Kerr. Ramond
(arXiv:2607.27129) is a *tidal* quadrupole on the body, rank 2 only. Cariglia–Galajinsky
(arXiv:1503.02162) **construct** Ricci-flat metrics carrying irreducible rank-3 and rank-4 tensors —
so the objects exist, and they are the positive control. **Their signature is (2,3) —
ultrahyperbolic, not Lorentzian** (verified here: `scripts/_kt_cg5d.py` prints it, eigenvalue signs
−2 +3 at every point tested). The control is unaffected — the Killing equation is signature-blind,
so finding a rank-4 tensor there still proves the prover is not a null-machine. What it changes is
what our nulls *mean*: no Lorentzian Ricci-flat spacetime with an irreducible Killing tensor of
rank ≥ 3 is known in any dimension, so a Lorentzian null is one more datum in an unbroken pattern
rather than a quirk of the substrate. **Read "the objects exist" as "in signature (2,3)".**

---

## 2. What is already established

The two results below matter more than anything else here, because between them they show the
instrument works in **both** directions. A checker that has only ever returned "nothing" has not
been shown able to say "something".

**Positive control — Kerr M=1, a=1/2, rank 2, den^1, box 8x8 (81 funcs), 64 points** (§127)

    sampled 5   exact 5   reducible 4   ->   IRREDUCIBLE 1     both primes

Generators came out `[p_t, p_phi, H]` with `Lsq` correctly **rejected** — Kerr is not spherically
symmetric, and the generator set is verified per substrate by `{H,Lsq}=0` rather than carried over
from a table. The direction is *identified*, not merely counted: constructing the textbook constant

    Q = p_theta^2 + y^2 [ a^2 (mu^2 - E^2) + L_z^2/(1-y^2) ]

gives `{H,Q} = 0` exactly, and adjoining `Q` to the reducible span raises its rank **4 -> 5**,
matching the measured exact dimension.

**Zipoy–Voorhees, an exact vacuum deformation, verified Ricci-flat before use** (§124, §126)

    delta=2      rank            1    2    3    4    5    6
                 prover dim      2    4    6    8   10   12
                 reducible       2    4    6    8   10   12
                 IRREDUCIBLE     0    0    0    0    0    0

    delta=1      prover dim      2    5    8   11   14   17
    (Schwarz.)   IRREDUCIBLE     0    0    0    0    0    0

**The δ=1 row is the free control and it is on-substrate by construction.** ZV at δ=1 *is*
Schwarzschild, in prolate spheroidal coordinates where nothing looks like `1 - 2M/r` — so the prover
must recover Schwarzschild's Killing algebra in the same coordinate family and the same denominator
structure as the δ=2 run. Contrast §119, where ε=0 was *not* a valid control for deformed Kerr:
ε=0 is Kerr, a different substrate, with denominator degree collapsing 11 → 4.

---

## 3. The ceiling — state it, do not paper over it

**Every result above is rank-bounded.** Closing ranks 1–6 is not the statement "no irreducible
Killing tensor exists." The grading theorem (`scripts/_p3_grading_check.py`, verified not assumed)
makes each rank an **independent finite** linear problem — which is what makes the computation
tractable, and exactly why no finite ladder of them adds up to a claim about all ranks.

> Turning rank-bounded computational nulls into a **rank-unbounded structural obstruction** requires
> an actual argument. This repo does not have one. Anything claiming otherwise is overreach and
> should be caught in review.

**And the rank bound is not the largest hole — stating it alone gets the emphasis wrong.** There are
three ceilings, and they are listed here in order of severity, which is the reverse of how obvious
they are:

1. **Analyticity, for anything perturbative — and this one no amount of compute relaxes.** The
   double-expansion solver works order by order: `{H₀,F₁} + {H₁,F₀} = 0`, so the leading term `F₀`
   must be a Killing tensor of the *unperturbed* background. Every tensor the method can find is
   therefore **analytic in the coupling with a root on the background**. A tensor that is
   non-analytic in ζ (a `ζ^{1/2}`, anything non-perturbative like `e^{−1/ζ}`) or that exists only at
   finite coupling has no such root and is **structurally invisible — not missed for want of a
   bigger box or a higher rank, but outside what the method can express at all.** Ranks 1–6 can be
   bought with compute; this cannot be bought at any price, and it is why a perturbative null is a
   weaker object than an exact one at the same rank. §130/§131 are perturbative. Say so.
2. **Rank.** As below — each rank is an independent finite problem, so no finite ladder reaches a
   statement about all ranks. Buyable with compute, one rank at a time. And see **D42**: ranks are
   not equally informative, so a long ladder can be fewer independent tests than its length.
3. **The ansatz.** A null means nothing until the search space is shown to CONTAIN the answer —
   the D40 lesson. Every reported closure is relative to a stated box and denominator power, and
   the representability guard must have passed, not merely not fired.

Report closures as what they are: *no irreducible KT at ranks 1–N on substrate X, **analytic in the
coupling with a background root** (if perturbative), within ansatz `{x^a y^b / L^d}` for the stated
box, by exact null over GF(p), with the reducible span subtracted and both primes agreeing.*

---

## 4. The sequence, which is not optional

A dependency order, not a checklist. Step 3 produces a number worth nothing without 1 and 2.

1. **Measure the system size and confirm the bracket builds at all.** Before any physics. The
   failure being avoided is a multi-hour hang that hides a malformed target.

2. **Validate the prover on KNOWN-NONZERO cases.** Kerr rank 2 must yield Carter (§127, done).
   Cariglia–Galajinsky must yield its rank-3/4 tensor — the control is `scripts/_kt_cg5d.py`, and
   its docstring carries the hazard: **derive the target from their Eq. (24), do NOT transcribe
   Eq. (29).** PDF-to-text collapsed an index there (`K_ttxw` read as `K_tttw`) and the transcribed
   tensor is not conserved, drift 0.30. A silently wrong target reads as "the control failed" or,
   far worse, as "no rank-4 KT exists."

3. **Only then, deformed Kerr.** A null from an unvalidated prover is worthless.

The earlier attempt (`scripts/_killing_search.py`) is marked **DEAD END** — 7.5 h, no output, the
expand-everything blow-up. The obstruction was the normalizer, not the mathematics. The
momentum-space form the grading theorem licenses makes the system size measurable up front rather
than discovered by hanging.

---

## 5. Failure modes already paid for

Not general advice — each is an error made here, and the reason a specific guard exists.

- **A correct computation answering the wrong question.** The §124 error. A mis-transcribed metric
  solves no field equation, and "no Killing tensor survives" on it is guaranteed and meaningless.
  **Verify a transcribed metric is Ricci-flat (or satisfies its field equations) before calling it a
  spacetime.** The Taub-NUT entry was neither Taub-NUT nor vacuum, and a nine-hour hang hid it.

- **A control that cannot fail is not a control.** And a threshold tested in one direction only is
  not tested.

- **Residuals that vanish exactly where the fit was made are a fit artifact, not a physics failure.**
  This nearly condemned a correct sGB metric: fitting the constants as pure numbers at m=1 made
  every residual proportional to `(m^4 - 1)`. Solving for `c1(m), c2(m)` symbolically recovered the
  dimensional relation instead of discarding it. Clean fitted integers point the same way.

- **Sampled counts are upper bounds, not measurements** (§126, D38). Sampling slack is a property of
  the substrate and box, not a constant of the method. The squeeze is `reducible <= true <= sampled`.

- **Provenance.** `data/kt_*.out` was once gitignored, which made every number in a published
  section uncommitted. A size rule is not a judgement about evidentiary value — if a number backs a
  claim, its artifact is tracked.

- **Report the failed replication, with the reason.** A silent one is invisible to everyone and is
  the easiest thing in any day's work to skip.

---

## 6. Running it

```bash
./verify.sh          # the local gate: every battery, both directions (knowns pass,
                     # sabotage fails), one verdict. Run before any "done" claim.

.venv/bin/python scripts/_kt_exact.py --metric kerr:1:1/2 --rank 2 --denpow 1
```

`_kt_exact` takes `--metric` (`zv:<delta>`, `kerr[:M[:a]]`), `--rank`, `--denpow`, and an optional
`--box`. `scripts/_kt_metrics.py` is the single place that knows what a substrate is, with
denominator and numerator degrees **measured** from `g^ab` rather than inferred from `deg(L)` — the
§124 error that once produced a solution space smaller than its own reducible span.

`_kt_nullvec --selftest` validates the *identity checker* ("is this F a solution?"), **not** the
dimension pipeline — the C matrix, the nullity, the reducible-span subtraction — which is what
produces the headline number. Those need a known-nonzero substrate, which is what §127 is for.

Python >= 3.12, one dependency (SymPy), laptop CPU. No GPU, no API, no LLM in the loop.

---

## 7. Where the rest lives

| file | what |
|---|---|
| `RESULTS.md` | lab notebook — §124 ZV closure, §126 δ=2 rank 4, §127 the Kerr control |
| `docs/ROADMAP.md` | current direction, in the user's own steer, and what preceded it |
| `docs/DECISIONS.md` | design rules and what bought them |
| `docs/EDGB.md` | the beyond-GR thread; field equations validated, corrections derivable |
| `docs/JOURNAL.md` | dated activity log |
| `docs/GLOSSARY.md` | the vocabulary, CS-framed |

**The user's standing steer, verbatim:** *"are we just doing what others have already done with
smaller machine, or are we trying new things, I would prefer later even if it continues to fail...
we dont want to run just for sake of running."* And: *"dont worry about risks, we have nothing
depending on these, its just side projects."*
