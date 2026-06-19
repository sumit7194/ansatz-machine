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

## 0. The universal analyzer — GENERALIZATION (CORE BUILT 2026-06-16; growing)
**Status: core landed** as `scripts/analyzer.py` + battery `40_analyzer.py`. `analyze(metric, coords)`
eats ANY metric and reports: what it's **made of** (vacuum / Λ / perfect fluid / traceless / anisotropic),
whether it's **physical** (frame-independent energy conditions via the principal components of T^a_b —
the key upgrade, three-valued), and whether it **solves the field equations** (vacuum / vacuum+Λ /
sourced). Validated against the frozen zoo (Minkowski, Schwarzschild, RN, FLRW dust, de Sitter,
Morris–Thorne) — one tool reproduces 27–38. Does NOT touch 01–38.
**Increments LANDED (2026-06-16):** singularity scan (Kretschmann blow-ups; e.g. Schwarzschild r=0,
Big Bang t=0), manifest symmetries (cyclic-coordinate Killing vectors — a lower bound on the isometry
group), and horizon + thermodynamics (Schwarzschild → r=2M, T=1/8πM, S=4πM²; RN → both horizons). The
report card from the mockup is now fully populated.
**Atlas run (41_atlas.py, 2026-06-16):** one `analyze()` per row across 10 famous spacetimes
(Minkowski → Schwarzschild → RN → SdS → AdS → de Sitter → Tangherlini-5D → FLRW rad/dust →
Morris–Thorne) — uniform report card, all exact & fast. Surfaced + fixed three guards (generic-symbol
singularity solve; quadratic-cap horizon roots; skip off-diagonal Kretschmann).
**OFF-DIAGONAL FRONTIER — Kerr DONE (2026-06-17, PLAN #1):** the analyzer now lands Kerr in ~6s
(vacuum, 2 Killing vectors, both horizons M±√(M²−a²)) via: decide-type-first with a numeric Ricci
pre-check (vacuum skips ricci_scalar + stress_energy), lazy stress_energy, and `g^{rr}=0` horizon
detection — PLUS feeding rational u=cosθ coordinates (the trig form swamps; D4 extends off-diagonal).
Remaining: Alcubierre warp + Gödel (own structure), rotating-horizon T/S, off-diagonal Kretschmann
(ring singularity).
**STAR REACHED (2026-06-17, `55_analyzer_star.py`):** the general tool reads a perfect-fluid stellar
interior with no stellar-specific code — perfect fluid (isotropic), constant ρ=3M/4πR³, static+axisymmetric,
regular (no singularity), signature-flip False (a star, not a hole). Honest edge found + recorded: `physical?`
is UNKNOWN because the interior is real only for r≤R and the `_sign` sampler is domain-blind (fixed `_sign`
to skip — not bail on — out-of-domain non-real samples, with a quorum guard; regression-free). **DOMAIN-AWARE
`analyze()` now SHIPPED:** an optional `domain={r:(0,R)}` argument bounds where coordinates are sampled, and
the same general tool then certifies the interior PHYSICAL (NEC/WEC/DEC/SEC all hold); `domain=None`
reproduces the original behaviour byte-for-byte. The honest UNKNOWN became a real capability.
**Still open:** off-diagonal handling (the frontier), a FULL Killing-vector solver (coordinate-mixing
symmetries like the rotation group), richer source ID, and folding the GP discovery loop in so the analyzer
can also DISCOVER, not just analyze. Original design notes below.


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

## 2. Observables — what a telescope actually sees  ◀ DONE
DONE: photon sphere + shadow + ISCO (`45_observables.py`, folded into the analyzer report card) —
Schwarzschild 3M / 3√3 M / 6M exact, charge tightens all. And the THREE CLASSIC TESTS, each from the
metric: LIGHT BENDING (`49_light_bending.py`, 1919 Eddington — Δφ=2∫dr/(r²√(1/b²−f/r²))−π → 4M/b weak
field, →∞ near the photon sphere); PERIHELION PRECESSION (`50_precession.py`, Mercury 43″/cy —
Δφ=2π(1/√(1−6M/r)−1) → 6πM/r, diverges at the ISCO r=6M); GRAVITATIONAL REDSHIFT (`51_redshift.py`,
Pound–Rebka — z=1/√f−1 → M/r, →∞ at the horizon). Charge reduces all three.
And RINGDOWN (`56_ringdown.py`, 2026-06-19): black-hole perturbation theory — the exact wave potential
V=f[ℓ(ℓ+1)/r²+f′/r] DERIVED for any metric (verified as an identity), the exact eikonal QNM ω=ℓΩ_c−i(n+½)λ
from the photon sphere (Schwarzschild Ω_c=λ=1/3√3M; ω_R=ℓ/b_shadow ties the LIGO ringdown to the EHT shadow),
folded into the report card. Honest edge: overtones (finite ℓ, n≥1) need Leaver / the maintained `qnm`
package — ansatz gives the exact potential + eikonal limit, not a numerical Leaver clone.
STILL OPEN: full geodesic integration / ray-tracing; a WKB overtone estimate off the exact potential.
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
- **anisotropic universes (Kasner)** ◀ DONE (`47_kasner.py`): engine recovered the conditions
  `p₁+p₂+p₃ = 1`, `p₁²+p₂²+p₃² = 1` from the vacuum residual (R_tt·t²=Σp−Σp²; R_xx·t²∝p₁(Σp−1)),
  necessary + sufficient — the abstractor move (24) in a cosmological setting.
- DONE: perfect-fluid **stellar structure** (`52_stellar_structure.py`) — from the interior metric with
  Φ(r), m(r) free the engine recovers the mass function dm/dr=4πr²ρ, the potential eq, and (via Bianchi
  ∇G≡0 on an isotropic fluid) the **TOV equation** dp/dr=−(ρ+p)(m+4πr³p)/(r(r−2m)), with the Newtonian
  limit −ρm/r² derived by post-Newtonian ordering. The engine's first STAR (matter, not a hole).
  Also DONE: the constant-density interior Schwarzschild sphere + the **Buchdahl bound** M/R≤4/9
  (`53_buchdahl.py`) — the exact star satisfies the engine's TOV, and its central pressure diverges at
  compactness 4/9, the onset of collapse. STILL OPEN: other exact interiors (Tolman IV/VII), and an
  equation-of-state → mass–radius relation sweep. — NOW DONE (`54_mass_radius.py`): numeric RK4 TOV
  integration with a Γ=2 polytrope traces the M–R curve and finds its turnover, the **Oppenheimer–Volkoff
  maximum mass** (past which a neutron star collapses to a black hole). The stellar arc is closed end-to-end:
  recover TOV (52) → exact star + Buchdahl (53) → predict a maximum mass (54). STILL OPEN here: other exact
  interiors (Tolman IV/VII), realistic tabulated EoS, slow-rotation (Hartle) corrections.

## 6. Causal-structure lens (signature flip + singularity character)
A natural analyzer extension: don't just LOCATE singularities — classify the spacetime's causal
structure. (a) Detect the **signature flip** inside a horizon (the timelike direction rotating from
∂_t to ∂_r as g_tt changes sign across r=2M — the very thing the analyzer's ρ-anchoring already
brushes against). (b) Classify a singularity as **spacelike** (Schwarzschild r=0 — "the end of time")
vs **timelike** (Reissner–Nordström r=0 — avoidable, "a place"); adding charge flips it, a clean
calibrated test since Schwarzschild & RN are both in the zoo. Idea seeded by a hand-shared note from
the sister NN project (tabula-geometrica) — kept SEPARATE (no code crossover); the link is that our
EXACT analyzer is the ground-truth oracle for what their net claims to have learned (signature flip,
spacelike singularity, charge→timelike). [[project-state-v6]] keeps the separation rule.

## 5. The symmetry / structure lens
Compute a spacetime's **Killing vectors** and conserved quantities directly;
classify metrics by their symmetry algebra rather than by parameters. A
different axis on "what makes a spacetime special".
DONE — **Petrov classification** (`57_petrov.py`, 2026-06-19): the algebraic type of the Weyl tensor from
its Newman–Penrose scalars Ψ0…Ψ4, now in the analyzer report card (`analyzer.petrov`). Black holes = type D
(Schwarzschild Ψ2=−M/r³, RN charge-corrected), conformally flat = O (de Sitter/Minkowski, Weyl≡0), a vacuum
pp-wave = N (only Ψ4, a pure gravitational wave — ties to §56). Frame-independent speciality I³=27J² for
D/O/N. Perf-guarded: Weyl computed only for the static spherical diagonal form; off-diagonal → instant
UNKNOWN.
Also DONE — **Killing symmetries** (`58_killing.py`, 2026-06-19): `analyzer.is_killing_vector` /
`killing_vectors` find & verify the **coordinate-mixing SO(3)** generators (R_x, R_y) the cyclic detector
misses, so Schwarzschild's full algebra ℝ_t×SO(3) (dim 4) comes out; they close [R_x,R_y]=−R_z; a Minkowski
Lorentz boost verifies too. Headline: **Kerr's hidden Killing TENSOR (Carter constant)** verified numerically
(∇_(aK_bc)=0 ~3e-8, irreducible), and the Carter constant conserved to ~1e-12 along an actual Kerr orbit
(E, L, μ², C → 4 constants ⇒ integrable). STILL OPEN: a fully general Killing solver for arbitrary metrics
(solving the Killing PDEs from scratch, not verifying/structured ansätze), and the Killing–Yano root.

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
