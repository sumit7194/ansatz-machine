# Attack angles — orthogonal directions to try

*A banked menu of orthogonal experiments for the engine, beyond the
static-black-hole / hair corner we started in. Pick from here whenever there's
nothing else running.*

**The reframe (2026-06-16):** we don't have a black-hole engine — we have a
**general engine for exact solutions of Einstein's equations**, plus a toolkit
built around it. Black holes + hair was just the proving ground. Every angle
below re-aims the SAME toolkit at a new domain or a new question.

## The toolkit we can re-aim
- **discovery loop** — GP over exact-rational ansätze, numeric-residual fitness
- **prover** — three-valued symbolic verdict (VERIFIED / REJECTED / UNPROVEN)
- **abstractor** (24) — recover the hidden *law* across a family (e.g. the
  Tangherlini meta-law, the N−3 exponent)
- **information/hair meter** (29) — count genuinely-free parameters, three-valued
- **energy-condition classifier** (36) — physical / exotic / dark-energy-like
- **thermodynamics reader** (35) — derive the laws, recover constants (S=A/4)
- **hair criterion** (34) — a source's angular component ⇒ which term appears

## Status
- **ACTIVE** (2026-06-16): **#1 cosmology** and **#3 impossible spacetimes** — building several
  small diverse experiments in each to map the terrain (breadth over depth) before deciding next.
- **QUEUED, THE BIG ONE — the universal analyzer (#0 below).** User's explicit steer
  (2026-06-16): widen into ONE general tool, don't keep building bespoke domain scripts. Do this
  LATER, after the breadth experiments clarify the picture. [[feedback-prefer-general-tools]]
- QUEUED: the rest.

## 0. The universal analyzer — GENERALIZATION (queued; the big one)
Instead of a new script per domain, build ONE `analyze(metric, coords)` that eats ANY spacetime
(black hole, FLRW universe, wormhole, warp bubble, rotating, any dimension) and returns one honest
report: what matter sources it (read T_ab off the Einstein tensor + classify), is that matter
physical (energy conditions — **generalize 36 to the frame-independent eigenvalues of T^a_b**, the
single upgrade that unlocks ALL domains at once), its symmetries (Killing vectors), whether it
solves the field equations (three-valued), and — if it has a horizon — its thermodynamics (35).
We already have the pieces (curvature in gr_engine, EC in 36, freedom in 29, thermo in 35); the job
is to UNGLUE them from the static ansatz and unify. Then every domain below becomes a one-line input,
not a project. This is the "more general tool, wider view" the user wants. Build after the
breadth pass below.

---

## 1. Cosmology — the whole universe (time-dependent), not one object  [ACTIVE]
FLRW `ds² = −dt² + a(t)²[dr²/(1−kr²) + r²dΩ²]` solves the same equations with a
fluid source. Ideas:
- **abstractor** recovers the law `a(t) ∝ t^{2/3(1+w)}` linking equation-of-state
  `w` to the expansion — the Tangherlini-meta-law move, now in cosmology.
- **energy conditions (36)** find their headline application: cosmic acceleration
  / **dark energy is literally an SEC violation** (`w < −1/3`); a phantom
  `w < −1` violates NEC too.
- recover/verify de Sitter, radiation (a∝t^½), matter (a∝t^⅔), ΛCDM.
- rational-friendly for power-law `a(t)`.

## 2. Observables — what a telescope actually sees
Geodesics *through* a metric (orthogonal to its structure): light bending,
Mercury's perihelion precession (43″/century), the photon sphere, the
**black-hole shadow** (EHT). Turns "here's a solution" into "here's what you'd
measure". Radii are rational-friendly.

## 3. "Impossible" spacetimes — exotic matter quantified  [ACTIVE]
Wormholes (Morris–Thorne, Ellis), warp drive (Alcubierre), rotating universes
with time loops (Gödel). These metrics are *known* — the interesting question is
**how exotic must the matter be?**, which is exactly what the energy-condition
classifier (36) measures. Our last-night tool becomes the centerpiece.

## 4. Exact matter that isn't a black hole
- perfect-fluid **stellar interiors** (TOV, Tolman IV/VII, Schwarzschild interior)
- **anisotropic universes (Kasner)**: the conditions `p₁+p₂+p₃ = 1`,
  `p₁²+p₂²+p₃² = 1` are a gorgeous **abstractor** target (hidden constraints).

## 5. The symmetry / structure lens
Compute a spacetime's **Killing vectors** and conserved quantities directly;
classify metrics by their symmetry algebra rather than by parameters. A
different axis on "what makes a spacetime special".

## Matter-arc leftovers (from the hair work)
- **inverse design** — name a hair term you want → compute the required source's
  angular stress → use 36 to check if a physical field can produce it (chains 34+36).
- **source reconstruction** — given a metric, GP-discover what matter sources it.

---
*Honest framing for all of these: most are mature fields, and a genuinely-new
exact solution is hard everywhere. The value is the engine-as-capability shown
broadly + honestly, with a real chance of a thin corner (a new meta-law, an
unexplored family). Same bet we've been making — orthogonal lens, accept 98%
failure, for the love of science.*
