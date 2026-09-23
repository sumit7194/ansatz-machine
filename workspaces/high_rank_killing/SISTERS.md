# The sibling repositories — a reference map

**READ-ONLY, without exception.** Import from them, read their data, run their code in place, cite
their results with attribution. Never modify them; never write anything of this project into them.

They were built with independent roots on purpose and are kept ignorant of each other. That is the
only reason agreement between two of them counts as evidence rather than echo. A result relayed
from one to another is *repeated*, not *corroborated* — name the originating repo in the same
sentence as the number.

**This file is a map, not a payload.** Nothing below needs to be in context by default.

---

## The one that matters here

### `../conjecture_machine` — *ansatz machine* · exact symbolic GR

**This holds your instrument.** Genetic programming proposes metrics, SymPy verifies them —
theorem or nothing. It has spent weeks on exactly the Killing-tensor question and its tooling is
validated in both directions.

    scripts/_kt_exact.py      the prover. --metric, --rank, --denpow, optional --box.
                              Exact nullspace over GF(p), two primes, with the reducible span
                              subtracted. This is what decides your object.
    scripts/_kt_metrics.py    the single place that knows what a substrate is; denominator and
                              numerator degrees MEASURED from g^ab rather than inferred
    scripts/_kt_cg5d.py       THE RANK-4 POSITIVE CONTROL. Read its docstring before anything
                              else -- it carries a transcription hazard that cost real time, and
                              it names the dimension of the known examples
    scripts/_kt_nullvec.py    the identity checker: validates "is this F a solution", NOT the
                              dimension pipeline
    scripts/_kt_double.py     the double-expansion solver (coupling and spin towers)
    RESULTS.md                sections 124-127 are the Killing-tensor arc. S127 is the model:
                              an instrument that had only ever returned "nothing" made to
                              return "something" on a substrate with a known answer
    docs/DECISIONS.md         D39 onward: what each design rule cost. D39 records a prior-art
                              find that retired a whole line of work
    docs/ROADMAP.md           the open question in that repo's own words
    verify.sh                 the local gate; run from inside that repo

**Two warnings from their own record, both paid for in hours:**

- *`_kt_nullvec --selftest` validates the identity checker, not the dimension pipeline.* The
  headline number comes from the C matrix, the nullity and the reducible-span subtraction. Those
  need a known-nonzero substrate to be trusted.
- *A sampled nullspace count is an upper bound, not a measurement.* The squeeze is
  `reducible ≤ true ≤ sampled`.

**To run their code, cd into their repo so its environment and imports resolve:**

    cd ../conjecture_machine && ./verify.sh
    cd ../conjecture_machine && .venv/bin/python scripts/_kt_exact.py --metric kerr:1:1/2 --rank 2 --denpow 1

**Do not copy their source into this repo. Reference it.** If you need a modified version, write
your own here and name the sibling file it derives from in the header.

---

## The others

### `../SpaceTime` — *tabula geometrica* · neural geometry, inductive

Its methods writeups are more use to you than its physics.

    writeups/silent_nulls.md    45+ measured ways a BUG reads as a RESULT, each with the
                                diagnostic that caught it. READ BEFORE BUILDING ANY CONTROL.
    writeups/representability_frontier.md   a diagnostic for whether a cheap legible code
                                exists / is unique / is global / is linear

### `../BlackHole` — *DeepStrain* · real LIGO data, empirical

Relevant only if you want the observational stake: whether a hidden symmetry's presence or absence
is measurable. Source of the "plateau recruits you" failure mode.

### `../TheBridge` — *trivium* · the cross-validation layer

Where cross-repo claims belong. If you need a result from one sibling to justify something about
another, that is a bridge leg, not a line in this project.

    CAPSTONE.md           program scoreboard and honest-miss ledger
    FALSIFICATION_V2.md   twelve standing lessons, each bought by a named failure
    SISTER_REQUESTS.md    how asks are filed; Round-13 shows a prior-art gate killing a
                          framing before any compute

### `../quantum` — *vestigium* · verified QM lattice numerics

Not relevant to this task. Listed for completeness.

### `../corner_function` — a parallel run on an unrelated problem

**Another session may be working there right now.** Do not read it before you have done your own
prior-art sweep — its conclusions are about a different problem and would only be noise. Do not
write to it.

---

## Live sessions

Other sessions may be running in these repos. **Identify a session by its working directory, never
by its name** — verify with `lsof -a -p <pid> -d cwd`. A name prefix is not proof.

**Several sessions on this machine are unrelated office work and are off limits.** If you need to
coordinate, route it through the user rather than messaging directly.
