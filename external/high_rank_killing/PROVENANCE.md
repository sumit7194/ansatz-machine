# Imported work — NOT produced by this repository, NOT yet verified by its instrument

**What this is.** A separate evaluation workspace (`~/Github/high_rank_killing`, local-only, run on
Fable 5.1) constructed a 4D Lorentzian vacuum pp-wave carrying a polynomially irreducible rank-3
Killing tensor, plus a 5D (1,4) companion. If it holds it closes what Cariglia–Galajinsky (2015)
and Fordy–Galajinsky (2019) both state as open — FG's "empirical barrier of rank 2".

**Why it is in this repo at all, given §0 of CLAUDE.md.** §0 says sibling findings do not enter here
as conclusions to host; they arrive as *asks* and this repo answers with its own instrument. That
rule was suspended for this import **by the user directly**, after the request first arrived
second-hand through the bridge and was declined on exactly those grounds. Recorded because the rule
still stands for everything else, and a reader finding imported conclusions here should know the
exception was deliberate and authorised rather than an erosion.

**Verification status: NONE from this repository, as of import.**

The originating workspace used *this repo's prover* by import (`ckpt=None`, nothing written back)
and reports **2/6/11** in 4D against a reducible span of 10, and **3/9/20** in 5D. That is this
repo's code producing those numbers — it is *not* this repo verifying them, because the same
implementation run twice is one measurement, not two. What is planned, and what would actually be
worth something to them:

- [ ] rebuild the metric and the tensor **from their equations, not their code path**, and see
      whether an independent route reproduces 2/6/11 with the span at 10
- [ ] check `{H, F} = 0` exactly on this repo's own bracket machinery
- [ ] confirm Ricci-flat with `a` symbolic, and signature (1,3) away from ρ = 0
- [ ] the load-bearing step: **exactly two Killing vectors**. Their jet count (`L_ξ R = 0`,
      `L_ξ ∇R = 0`, rank 8 of 10) is ansatz-free and is the real argument. This repo contributed a
      second, complementary handle: three Killing vectors would force a rank-3 reducible span of
      `10 + 3 + 6 = 19` against 11 measured, which is impossible since span ≤ measured — but that
      only excludes a third KV *representable in the ansatz*, so it does not replace the jet count,
      it covers a different case.

**Sensitivity, which is the reassuring part.** Wrong *downward* on the rank-2 count makes the result
stronger (one irreducible rank-2 instead of two drops the span to 8 and raises the irreducible count
at rank 3 from 1 to 3). Wrong *upward* is impossible (measured 6 minus reducible 4 caps it at 2).
**The only fatal direction is extra Killing vectors** — which is where they spent their effort.

**Contents.** `WRITEUP.md` (the standalone result), `report.md` (EXP-001 prior-art map, EXP-002 4D,
EXP-003 5D), `scripts/` + `results/` (reproduce every number), `TODO.md` (their open items, carried
across unedited — including that the KK reading of the 5D metric is stated but not re-verified),
`prior_art/SOURCES.md` (14 works; the PDFs themselves are gitignored — this repo is public and they
are published papers).

Workspace scaffolding (`TASK.md`, `CLAUDE.md`, `SISTERS.md`, `README.md`) was deliberately not copied.

Source commits at import: `6a5b66c` (EXP-003), `9384d7f` (EXP-002), `41e1a77` (EXP-001).
