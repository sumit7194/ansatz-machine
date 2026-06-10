# Glossary

*The project's vocabulary, explained for a computer engineer first and a
physicist second. One honest sentence each; links for depth.*

## The physics

- **Metric (g_ab)** — the rulebook for distances and clock rates at every
  point of spacetime; a symmetric matrix of functions. The thing we hunt.
- **Einstein field equations (EFE)** — geometry = matter, as n(n+1)/2 coupled
  nonlinear PDEs (10 in 3+1D). A metric that balances them *exactly,
  everywhere* is an **exact solution**.
- **Vacuum solution** — no matter anywhere; the equations reduce to
  `R_ab = [2Λ/(n−2)] g_ab`. All our halls so far are vacuum (+Λ).
- **Λ (cosmological constant)** — spacetime's built-in tension. Λ=0 → flat
  asymptotics, Λ>0 → de Sitter, Λ<0 → anti-de Sitter (AdS).
- **Ansatz** — the guessed *shape* of a metric with unknowns left in (e.g.
  "static, spherical, one unknown f(r)"). Every historical solution came from
  one; an ansatz is the search space.
- **Schwarzschild / Kerr** — the non-spinning (Dec 1915) and spinning (1963)
  black holes. The 47-year gap between them is why "machine proposes, algebra
  verifies" is interesting at all.
- **BTZ** — the 2+1-dimensional black hole (1992, needs Λ<0). Locally it is
  just AdS₃ — a black hole made of topology, not local curvature.
- **Tangherlini** — Schwarzschild's higher-dimensional family,
  f = 1 − μ/r^(n−3).
- **Birkhoff's theorem** — static spherical vacuum is *unique*: there is
  nothing in that ansatz beyond the known families. Makes our two-function
  hall a perfect honesty test (correct output = zero false novelty).
- **Curvature invariant** — a number computed from curvature that every
  coordinate system agrees on. CS framing: a hash that survives renaming all
  the variables.
- **Kretschmann scalar (K)** — the workhorse invariant, K = R_abcd R^abcd;
  48M²/r⁶ for Schwarzschild.
- **CSI / VSI spacetimes** — all invariants Constant / Vanishing. The
  fingerprint's declared blind spots: de Sitter and BTZ are CSI; pp-waves are
  VSI (curved, yet every invariant is zero — indistinguishable from flat by
  hashes alone).
- **Cartan–Karlhede algorithm** — the real equivalence test (frame-fixed
  curvature derivatives), decidable in ≤7 derivative orders. No Python
  implementation exists anywhere (verified June 2026) — building one is an
  open contribution.
- **Naked singularity** — a singularity with no horizon around it; the
  negative-mass branches the GP keeps finding first. Exact vacuum all the
  same — the equations don't share our taste in mass.
- **Richardson's theorem** — deciding whether a symbolic expression is
  identically zero is undecidable (reduction from the halting problem). The
  reason verdicts are three-valued, and the reason the rational-coordinates
  rule matters (rational zero-testing IS decidable).

## The machine

- **PROPOSE → REDUCE → VERIFY → NOVELTY → EVOLVE** — the loop. GP proposes an
  f(r); the ansatz (reduced symbolically ONCE) turns it into fast numeric
  residuals; survivors get the symbolic proof; verified hits get
  fingerprinted; everything else breeds.
- **Genome** — an expression tree (AST) over {+,−,×,÷,int-powers} with leaves
  r and exact Rationals. A pair of trees in the two-function hall.
- **Fitness** — mean |field-equation residual| at 6 sample radii, plus a
  parsimony tax and the triviality penalties (ground-state members score
  perfectly and discover nothing).
- **Promotion** — residual < 1e-10 → the exact expression goes to the full
  symbolic verifier. Theorem or back to the population.
- **Gene duplication** — copy/graft one genome slot onto the other; the
  operator that made the two-function hall solvable.
- **Verdicts** — VERIFIED (theorem) / REJECTED (numerically nonzero,
  definitive) / UNPROVEN (numerically vacuum, symbolically stuck) from the
  verifier; KNOWN_LIKELY / CANDIDATE_NEW / BLIND_SPOT / FLAT_OR_VSI from the
  fingerprint.
- **The catalog** — `02_fingerprints.py`'s built-ins plus
  `catalog_discoveries.json`, the machine's persistent memory of every family
  it has discovered and generalized itself.
- **Hair vs law** — when generalizing a find, constants that stay free under
  symbolic re-proof are physical parameters ("hair", e.g. mass); constants
  the equations pin are structural ("law", e.g. the Λ coefficient).
