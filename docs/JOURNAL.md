# Journal

*Dated activity log, newest first. One entry per working session: what was
built, what broke, what the machine taught us. Numbers live in
[RESULTS.md](../RESULTS.md); decisions live in [DECISIONS.md](DECISIONS.md).*

---

## 2026-06-17 — PLAN #1: cracked the off-diagonal frontier (Kerr lands in 6s)

- Agreed ordered plan (docs/PLAN.md): #1 off-diagonal frontier → #2 causal-structure lens →
  #3 make-it-discover. Working #1.
- **Made the analyzer handle Kerr** (was hanging forever). Two parts:
  - **Analyzer restructure:** `analyze()` now decides the solution TYPE first via a NUMERIC
    pre-check on the Ricci — if Ricci samples to zero it's vacuum, confirmed symbolically WITHOUT
    ever forming `ricci_scalar` (the heavy contraction) or `stress_energy` (which blanket-simplified
    huge off-diagonal expressions). Those two were the hang. Also: `stress_energy` made lazy
    (per-component cancel/together), and horizon detection generalized from `g_tt=0` to `g^{rr}=0`
    so it catches Kerr's Δ=0 horizons at r=M±√(M²−a²). Off-diagonal singularities stay UNKNOWN
    (Kretschmann too heavy).
  - **The real unlock (D4 extended):** the analyzer fixes weren't enough alone — Kerr's TRIG form
    swamps `simplify` (~500s, per battery 01's own note). Feeding Kerr in RATIONAL u=cosθ
    coordinates makes it tractable. So the D4 rational-coordinates rule extends to off-diagonal.
- **Result:** Kerr analyzes in **6.4s** → vacuum, ∂/∂t & ∂/∂φ (2 Killing vectors), both horizons
  M±√(M²−a²), singularity UNKNOWN (honest). Added to the atlas as row 11; battery 41 checks it.
  Diagonal zoo (battery 40) unregressed.
- **Debugging notes:** a stray `pkill -f` over-match killed an earlier verify mid-run (re-ran;
  lesson: kill by PID). Also fixed the dashboard staleness — verify.sh now writes ROOT/gate.log
  live (it had been reading a 3-day-old file), so the panel reflects the current 28→29 batteries.
- **Still open in #1:** Alcubierre warp + Gödel, rotating-horizon T/S, ring singularity.

## 2026-06-16 (cont.) — THE ATLAS: the analyzer turned loose on a catalog (#3)

- User picked attack angle #3 (atlas) over deepening (#2), with #2 folded in as gaps surface.
  Built `41_atlas.py`: one `analyze()` per row, a uniform "report card for every famous spacetime".
- **The catalog (10, all exact & fast):** Minkowski, Schwarzschild, Reissner–Nordström (EM/physical,
  2 horizons), Schwarzschild–de Sitter, anti–de Sitter, de Sitter, Tangherlini 5D, FLRW radiation
  (perfect fluid w=1/3), FLRW dust (w=0), Morris–Thorne wormhole (exotic). The table reads cleanly:
  made-of / physical / #symmetries / singularity / horizon / solves, all from one tool.
- **#2 depth gaps the atlas surfaced (and I fixed, as guards in analyzer.py):**
  (a) `R_SYM` is positive, so the singularity solver hid r=0 → solve the Kretschmann denominator over
  a generic real symbol; (b) cubic/quartic horizons (Schwarzschild–dS, RN–dS) hung the root-solver →
  cap clean horizon roots at quadratics, report higher as "?(complex)"; (c) off-diagonal metrics
  (Kerr, Gödel, warp) choke the blanket simplify → singularities skip non-diagonal (UNKNOWN), and Kerr
  is left as a noted FRONTIER, not a battery row. All honest three-valued behavior.
- **Frontier identified:** off-diagonal (rotating/warp) metrics need smarter, structured simplification
  before the analyzer handles them at speed — the clear next depth pass (ATTACK_ANGLES §2). Also banked
  §6 (causal-structure lens: signature flip + spacelike-vs-timelike singularity) from a hand-shared
  idea with the sister NN project — kept separate, our exact tool as its ground-truth oracle.
- Battery 41 added. Full battery 28/28.

## 2026-06-16 (cont.) — THE GENERAL TOOL: universal analyzer, core landed

- User's steer crystallized: stop building bespoke domain scripts, build ONE general tool —
  and build it SEPARATELY so the proven 01–38 base stays frozen. [[feedback-prefer-general-tools]]
  Showed a mockup of the target (one `analyze()` → one report card for any spacetime), got the
  go-ahead, built the core.
- **`scripts/analyzer.py` (new module, reuses gr_engine, touches nothing else)** — `analyze(metric,
  coords)` returns one report: (a) what it's **made of** — reads the stress-energy off the Einstein
  tensor and classifies (vacuum / cosmological constant / perfect fluid w / traceless-EM-like /
  anisotropic); (b) is it **physical** — the **key generalization**: energy conditions from the
  FRAME-INDEPENDENT principal components (eigenvalues) of T^a_b, so the check is no longer welded to
  the static-black-hole frame — works on diagonal metrics directly (any coords/dim) and attempts an
  eigen-decomposition for off-diagonal, three-valued (UNKNOWN, never a guess); (c) does it **solve
  the field equations** — vacuum / vacuum+Λ / sourced.
- **`40_analyzer.py` battery — the proof it's sound.** One `analyze()` reproduces 27–38 across a zoo
  of totally different metrics: Minkowski (vacuum), Schwarzschild (vacuum/Ricci-flat), RN (traceless
  EM matter, physical), FLRW dust (perfect fluid w=0, physical), de Sitter (cosmological constant,
  SEC violated = accelerating), Morris–Thorne wormhole (anisotropic, ρ<0, all conditions violated =
  exotic). All correct. Full battery 27/27.
- The 01–38 scripts are now ALSO the analyzer's regression suite — the general tool agrees with the
  frozen base before we point it anywhere new. From here, a new domain is a one-line input, not a new
  script — the widening the user asked for.
- **Increments landed same session (user: "keep continuing"):** the analyzer now also reports
  (a) **singularities** — Kretschmann blow-ups (Schwarzschild/RN at r=0, Big Bang at t=0, none for
  de Sitter); the r>0 assumption on R_SYM hid r=0, fixed by solving over a generic real symbol;
  (b) **symmetries** — manifest (cyclic-coordinate) Killing vectors, a lower bound (Minkowski 4,
  Schwarzschild/wormhole 2, FLRW/dS 3); (c) **horizon + thermodynamics** — for g_tt=−f, g_rr=1/f:
  Schwarzschild → r=2M, T=1/8πM, S=4πM² (area by integrating the angular block); RN → both horizons.
  The mockup's report card is now fully populated; battery 40 checks all of it. Full battery 27/27.
  Still open: a full coordinate-mixing Killing solver, richer source ID, and folding the GP discovery
  loop into the analyzer so it can DISCOVER, not just analyze.

## 2026-06-16 (cont.) — BREADTH PASS: the engine leaves black holes (cosmology + exotic spacetimes)

- User's steer: widen the view, try several DIFFERENT things across cosmology (#1) and
  exotic/"impossible" spacetimes (#3) to build a holistic picture before deciding next; the
  big generalization (one universal analyzer) is banked in docs/ATTACK_ANGLES.md for later.
  [[feedback-prefer-general-tools]]. Did a quick lit-scout first (research-before-building):
  ML-cosmology is data-driven (DESI/PySR fitting w(z)); warp/wormhole analysis has a NUMERICAL
  incumbent (Warp Factory) and a track record of positive-energy claims refuted by exact
  recomputation (Lentz). Our orthogonal lane is the usual one: exact + proven + structural.
- **`37_cosmology.py` — the engine takes on the expanding universe.** Same engine, FLRW metric
  instead of static vacuum. (A) recovers the Friedmann equations straight from the metric
  (ρ=3H²/8π); (B) the EXPANSION-LAW META-LAW — for a=t^q it derives w=p/ρ and inverts to
  **q(w)=2/(3(1+w))** (radiation→½, matter→⅔, stiff→⅓), the abstractor move now in cosmology;
  (C) de Sitter → w=−1; (D) the energy-condition map: **acceleration is exactly an SEC violation**
  (w<−1/3), phantom is NEC violation (w<−1); (E) the **Big Bang singularity** via a different lens —
  Kretschmann K∝1/t⁴→∞ for radiation/matter but constant for de Sitter (no singularity); (F) a
  **bounce** a=cosh(t) has ρ+p=−1/4π<0 at the bounce ⇒ avoiding the Big Bang needs EXOTIC matter,
  which ties cosmology straight to the wormhole/warp lens. All exact. Battery 37.
- **`38_exotic_spacetimes.py` — proves "impossible" spacetimes need exotic matter.** (1)
  Morris–Thorne wormhole: reads stress-energy off the Einstein tensor and PROVES the no-go —
  at the throat ρ+p_r=(b'(r₀)−1)/(8πr₀²)<0 because flaring-out needs b'<1, so NEC is necessarily
  violated for ANY shape (exotic matter forced; our signature "prove an impossibility" move).
  (2) Alcubierre warp drive: the Eulerian energy density comes out ρ=−v²(y²+z²)f'²/(32π r_s²)≤0,
  manifestly negative — the exact computation that busts "positive-energy warp" claims. Battery 38.
- Both are textbook results; the point is breadth + that the exact discover/prove/abstract engine
  handles wholly new domains (time-dependent cosmology, off-diagonal warp metric) with no
  black-hole machinery. Map-the-terrain pass, toward the general tool. Full battery 26/26.

## 2026-06-16 (cont., autonomous) — ATTACK ANGLE #2: energy-condition classifier (is the matter physical?)

- Second new lens of the night (`36_energy_conditions.py`). Motivation: the GP
  returns "VERIFIED" for exotic branches too (its beloved negative-mass /
  negative-charge solutions), but VERIFIED only means "solves the field
  equations" — not "the matter is physically allowed". This adds that second gate.
- For ANY static metric it reads the stress-energy off the Einstein tensor
  (ρ=−G^t_t/8π, p_r=G^r_r/8π, p_t=G^θ_θ/8π in the orthonormal frame) and tests the
  standard pointwise conditions NEC/WEC/DEC/SEC. Sign-checking is three-valued:
  symbolic when SymPy decides, else over a sampled positive domain (a negative
  sample = definitive violation), UNKNOWN if undecidable — same honesty as the meter.
- **Validation reproduces the textbook verdicts AND discriminates regimes:**
  Schwarzschild → vacuum (all saturated); RN → all four hold (physical EM field);
  exotic f=1−2M/r−Q²/r² → ρ<0, WEC/NEC violated (flagged exotic); de Sitter → only
  SEC violated (the dark-energy / acceleration signature). So the classifier tells
  physical, exotic, and dark-energy-like apart. A judgment layer on the engine, not
  a new source rung (D26). Battery 36 added.

## 2026-06-16 (cont., autonomous) — NEW LENS: black-hole thermodynamics, engine recovers S=A/4

- User (still awake, heading to sleep) pushed for MORE attack angles before any
  write-up. Opened a new lens orthogonal to "find a metric": take a solution and
  have the engine AUTONOMOUSLY derive its thermodynamics and verify the laws
  (`35_thermodynamics.py`).
- Glass-box recipe, all exact: parametrize by the HORIZON RADIUS r_h (not mass) so
  everything stays RATIONAL — M read off f(r_h)=0, dodging the √(M²−Q²) branch-cut
  wall (the D4 lesson applied to thermodynamics). T = f'(r_h)/4π (surface gravity).
  Entropy S = α·Area with α UNKNOWN; then DEMAND the first law dM = TdS + ΣΦ_i dq_i.
- **What the engine recovers unaided:** (1) the Bekenstein–Hawking coefficient
  **α = 1/4** (S = A/4) — and it's the SAME 1/4 in every dimension 4D–7D, a
  structural fact echoing the no-hair ladder (33); (2) the charge potentials
  Φ_Q = Q/r_h, Φ_P = P/r_h from ∂M/∂q; (3) the first law and the generalized Smarr
  relation (n−3)M = (n−2)TS + ΣΦq, verified ≡0 symbolically for Schwarzschild, RN,
  the dyonic hole, and Tangherlini 5D/6D.
- **Unification (the real payoff):** the meter's hairs (29) ARE these thermodynamic
  charges — M↔S, Q↔Φ_Q, P↔Φ_P — and the first law is the bookkeeping that links
  them. The whole matter arc (discover → count hair → thermodynamics) now closes a
  loop. Honest: rediscovery of 1916–1973 BH thermodynamics; new is the automated
  exact-derivation CAPABILITY + the unification. Not a new source rung (D26).
  Battery 35 added.

## 2026-06-16 (cont., autonomous) — the HAIR CRITERION: one principle unifies 28 and 32/33

- Asked the obvious question after 32/33: scalars give NO hair, but Maxwell gives
  the Q²/r² charge term (28) — WHY the difference? Found the single structural
  reason and turned it into a predictor (`34_hair_criterion.py`).
- The static lapse f(r) is pinned by ONE field-equation component, the angular
  (θθ) Einstein equation `R_θθ − [2Λ/(n−2)]g_θθ = (source)_θθ`. Its left side is
  the universal f-determining operator. So: **a static source adds hair ⇔ its
  angular component (source)_θθ ≠ 0**, and the engine reads the extra term off
  that one ODE.
  - scalar φ(r): (source)_θθ = ∂_θφ = 0 → f forced to Tangherlini → NO HAIR;
  - Maxwell A_t=Q/r: the engine computes T_θθ = Q²/(2r²) (f-INDEPENDENT, so the
    angular eq is a clean ODE), and `dsolve` returns f = 1 − 2M/r + Q²/r² — **RN's
    charge term DERIVED from the angular equation alone**, no GP needed.
- So no-hair (32/33) and charge-hair (28) are the SAME mechanism read two ways.
  The engine now doesn't just find/prove solutions — it reads off WHY one source
  haired and another didn't. D26-compliant (a unifying principle, not a new source
  rung). Battery 34 added.
- **And the criterion PREDICTS, not just explains.** Fed a magnetic charge (a field
  config the engine had never solved): A_φ=−P cosθ. The engine computes T_θθ =
  (Q²+P²)/(2r²) — f- and θ-independent, the sin²θ cancels — so the criterion
  predicts magnetic charge hairs f exactly like electric (Q²→Q²+P²). `dsolve`
  returns dyonic RN `f = 1−2M/r+(Q²+P²)/r²`, and that angular-derived f then passes
  the FULL Einstein–Maxwell verifier (all components + ∇F). So: lapse fixed by ONE
  equation, full system confirms it was sufficient. Magnetic≡electric in f is the
  structural face of EM duality, and the engine derived it from the criterion.

## 2026-06-16 (cont., autonomous) — no-hair is STRUCTURAL: the proof generalizes across the ladder

- Turned the abstractor lens (24) onto a THEOREM instead of a metric: ran the
  step-32 no-hair proof at every rung 4D..7D with an arbitrary symbolic Λ
  (`33_no_hair_ladder.py`). The SAME mechanism fires at every rung:
  - a static scalar puts zero source in the angular equation, so the angular
    equation alone forces the unique Tangherlini–(A)dS lapse
    `f = 1 + C/r^(n−3) − [2Λ/((n−1)(n−2))] r²` (engine derives it via `dsolve`,
    matched against the closed form — exact at 4,5,6,7D);
  - that f is radially Ricci-balanced, so the radial equation collapses to
    `κφ'² = 0 ⇒ φ' = 0`.
- **Meta-theorem the machine discovered:** within the static rational r²-ansatz,
  a minimally-coupled scalar admits NO hair in ANY dimension n≥4 and for ANY Λ —
  the angular equation is the executioner, n and Λ are spectators. The 4D no-hair
  theorem (32) is just one rung. This is the same move as 23/24 (generalize a
  result across the ladder), so it's D26-compliant — generalization, not a new
  source rung. Battery 33 added; full battery 20/20 ALL GREEN.
- Done autonomously overnight (user asleep) under the standing "keep going until
  we can't think of anything" instruction. Work committed immediately (D23 habit,
  power-loss insurance).

## 2026-06-16 — Path 2 capstone: the engine PROVES the no-hair theorem (the dual of RN)

- Built `32_no_hair.py`, the deliberate dual of the RN discovery (31/28). RN was
  the engine GAINING a term (give it charge → it builds Q²/r²); no-hair is the
  engine PROVING it can gain nothing — the matter span's other bookend.
- **The proof leg (exact, no assumption on φ's form).** With f(r), φ(r) left as
  symbolic Functions on the canonical static ansatz (angular part exactly r²):
  - the angular Einstein equation has ZERO scalar source (φ=φ(r) ⇒ ∂_θφ=0), so
    `R_θθ = 1 − f − r f' = 0`, and `dsolve` returns `f = 1 + C1/r` — Schwarzschild
    is FORCED by the angular equation alone, before φ is even mentioned;
  - on that f the radial Ricci `R_rr` is identically 0, so the radial equation
    `R_rr = κφ'²` collapses to `κφ'² = 0`, and `solve` returns `φ' = 0` ⇒ φ=const.
  A clean symbolic chain: the field equations themselves forbid scalar hair.
- **The search leg (the loop's own verifier).** On the forced background a menu of
  non-constant profiles — C/r, C·ln r, C·r, and the JNW/dilaton log C·ln(1−2M/r)
  — is every one REJECTED (numeric residual catches them); only φ=const VERIFIES.
  The loop hunts for hair and comes back empty, the empirical shadow of the proof.
- **Honest footnote, banked in the script.** The one genuine scalar-haired
  solution, JNW, escapes ONLY by deforming the angular part to (1−b/r)^(1−γ)·r²
  — a fractional power, the exact branch-cut wall the D4 rational-coordinates rule
  keeps out. So "no-hair" here is precisely "no hair without leaving the rational
  r²-ansatz" — the theorem and the engine's scope coincide, which is the honest
  thing to say. Battery 32 added (19 batteries, all green).
- **Why this is the capstone, not just another demo.** The engine now spans the
  field menu in BOTH directions: vacuum (Schwarzschild→Tangherlini→26-family
  ladder), matter-discovery (RN, gains a term), secondary-hair reading (GHS
  dilaton), AND theorem-rediscovery (no-hair, proves a term is forbidden). That
  closes the build phase: the contribution is the glass-box discover-AND-prove
  engine spanning vacuum→matter, differentiated from the numerical-ML cousin
  (AInstein, arXiv:2502.13043) by being EXACT and PROVEN. Decision D26.



- Turned the original propose→verify→evolve loop (GP over exact-rational f(r),
  numeric residual fitness, symbolic proof) loose on a SOURCED theory for the
  first time: Einstein–Maxwell with a unit-charge field A_t=Q/r, RN not supplied
  (`31_matter_hunt.py`, reuses 03's GP + 28's EM machinery).
- **Result:** in ~4 s the machine found f = 1 + 3/(4r) + 1/r², residual 1e-17,
  and the exact verifier returned VERIFIED (R_ab=κT_ab and ∇F=0). The Q²/r²
  charge term emerged unaided (coeff = Q² = 1); mass came out M=−3/8 (the
  negative-mass branch the GP has always preferred). I.e. the loop AUTONOMOUSLY
  DISCOVERED an exact Reissner–Nordström black hole in a matter theory.
- **Honest scope:** RN is 1916–18 physics, so this is rediscovery (like the
  vacuum campaign rediscovering Schwarzschild). What's new is the CAPABILITY —
  the discovery loop now operates in sourced gravity, the genuinely-
  unclaimed-by-machines thing (per the literature sweep, no competing
  ML/symbolic exact-metric discovery exists). Battery 31 added.
- Path 1 (automate the SPSM physical-vs-gauge criterion) is being scoped by the
  external session in parallel; this is Path 2 (our hands).

## 2026-06-15 (cont.) — literature check: hair-lens is taken; discovery-engine still unclaimed

- An external session ran a real literature sweep (so we stop redoing done work).
  Findings, banked honestly:
  - The hair / parameter-counting / "complexity of a theory" lens is a MATURE,
    ACTIVE field. Primary/secondary hair is standard vocabulary; 2024–25 has a
    flood of primary-hair papers (Beyond-Horndeski, Proca-Gauss-Bonnet,
    Lovelock-Proca). The free-parameter-count question is FORMALIZED WITH AN
    ALGORITHM: Hajian–Sheikh-Jabbari, arXiv:1612.09279.
  - Every case our plan would touch is published: the EMD a=0,1,√3 coupling map,
    D=Q²/2M secondary, the light-ring topological-charge jump at a=√3, discrete
    allowed dilaton couplings, the a↔SUSY (4,8,16) lineup. So "aimed-A" (the KK
    map) is textbook — a nice internal bridge to the NN project, not new physics.
  - Our meter is the COARSE version: it asks "is X EOM-fixed?", not the finer
    "physical vs gauge-redundant vs residual-symmetry charge, and first-law
    role." It conflates gauge-redundant with EOM-secondary and is BLIND to
    symmetry-removable params (canonical case: asymptotic dilaton φ₀, redundant
    by shift symmetry). Declared as the D25 blind spot.
  - The exact-metric DISCOVERY loop (our original engine) is STILL genuinely
    unclaimed (matches our README's June search; only adjacent ML work found).
- Net: the hair-meter is not a new lens or a discovery tool — but a hardened,
  honest, AUTOMATED classifier (the SPSM physical-vs-redundant criterion, with
  worked examples as a test suite) could be a real *tooling* contribution.
  Open scoping question: is SPSM already effectively automated on paper, or is
  the glass-box automated version genuinely missing? Steer AWAY from
  hand-discovering new hair (crowded race). (Credit: external review session.)

## 2026-06-15 (cont.) — meter hardened to three-valued honesty (external review)

- An external Claude session reviewed the meter code and caught a real, serious
  flaw: it OVER-reported. Empty/un-extractable constraints → "all free"; a
  swallowed solve() failure → constant counted as free; an unreduced
  transcendental → silent max count. No UNKNOWN verdict anywhere — so a
  counting instrument would return the MAXIMUM the moment it choked. And it was
  load-bearing: the GHS "2+secondary" only worked because I hand-rationalized
  the coupling first.
- **Fixed (D24).** Both meters (26 vacuum, 29 matter) are now three-valued: a
  residual that won't reduce to a clean polynomial in r → UNKNOWN (declared
  blind spot); a solve() that errors → UNKNOWN. Certified adversarially:
  fractional-power and log(r) residuals both read UNKNOWN, while RN reads 2 and
  GHS reads 2-free + D secondary (=Q²/2M). Also fixed: a √|g| Abs artifact in
  □φ and ∇·F (switched to rational Christoffel forms in 27/28) that had been
  spuriously flagging clean GHS; and the secondary label now prefers the
  caller's candidate-derived constant (D), via reversed elimination.
- Lesson, in-character: the GHS catch was real but UNCALIBRATED — the meter
  couldn't tell us when it was wrong, the one thing this project refuses to
  tolerate. Now it can. (Credit: external review session, kept separate.)

## 2026-06-15 (cont.) — THE PRIZE: meter catches a SECONDARY hair (dilaton black hole)

- Climbed the field menu past the JNW wall by going around it (rational metrics):
  **Maxwell** (`28`, Reissner–Nordström, engine recovered κ=2 itself, R_ab=κT_ab
  + ∇F=0 VERIFIED), then a **matter meter** (`29`, generalizes the vacuum
  hair-counter to sourced solutions; RN → 2 primary hairs M,Q), then the
  **dilaton** (`30`, Einstein–Maxwell–dilaton / GHS).
- **The payoff.** Fed GHS with M, Q, D (dilaton charge) ALL symbolic. Numeric
  gate confirmed the transcription (residual 8e-143 at D=Q²/2M). Then the matter
  meter, told nothing, read:
      M: free (hair) · Q: free (hair) · **D: SECONDARY (= Q²/(2M))**
  — it caught that the dilaton charge only *looks* free but is forced by mass and
  charge. That is the EdGB secondary-dilaton-charge phenomenon, demonstrated on
  its closed-form cousin, **detected automatically by our instrument**. The
  primary/secondary distinction the whole v6 reframe was about — now working on a
  real solution.
- Fix that unlocked it: the meter's solve() was asking for a single POINT in
  (M,Q,D); the solution is a 2-D family, so it returned empty. Replaced with
  greedy elimination (solve for one constant in terms of the rest, substitute,
  repeat) → counts the variety's dimension correctly. RN regression intact (2).
- **Honest scope:** GHS / secondary dilaton hair is known physics (1991) — so
  this is *rediscovery with the instrument* (like the abstractor on Tangherlini,
  the meter on Birkhoff), validating the tool on exactly the subtle case it was
  built for. The genuinely-new use is next: point it where the hair count is
  unknown or contested. New verify.sh batteries: 28, 29, 30.

## 2026-06-15 — field menu opened: scalar source works; JNW recovered, then a branch-cut wall

- **Engine extended beyond vacuum** (`27_scalar.py`): a minimally-coupled massless
  scalar now sources gravity, trace-reversed form R_ab−[2Λ/(n−2)]g = κ∂φ∂φ plus
  □φ=0, three-valued verdict on the coupled system. Sanity gate passes (const
  scalar leaves Schwarzschild verified; bogus scalar rejected). First rung of the
  v6 field menu (scalar → Maxwell → dilaton/EMD).
- **WIN — the engine recovered a scalar solution's existence condition itself.**
  Fed the JNW (Janis–Newman–Winicour) ansatz with parameters b, γ, C, κ ALL
  symbolic, the source residual R_rr−κ(∂φ)² gave, cleanly:
  **γ² + 2κC² = 1**  (equivalently κ = (1−γ²)/(2C²)) — the exact JNW relation,
  derived, not supplied. (runs/jnw_test.py)
- **DEAD-END (honest, instructive) — fractional powers stall the symbolic EOM.**
  JNW's metric carries u^γ = (1−b/r)^γ. The scalar EOM □φ is **numerically zero**
  (0j at a regular point; by hand √|g|gʳʳφ′ = C·b·sinθ is r-constant ⇒ □φ=0) but
  the symbolic zero-test drowns in branch cuts (Abs/re/im/Piecewise) → UNPROVEN.
  This is the **D4 lesson resurfacing for matter** (Kerr-in-trig was 500 s→
  UNPROVEN until u=cosθ rationalized it): fractional-power solutions need a
  rationalizing substitution before the symbolic EOM closes. Known-direction fix,
  not done tonight.
- **Also noted for the list:** the information meter (26) is vacuum-only; reading
  a matter solution's hair (JNW has 2: mass + scalar charge) needs a "matter
  meter" variant. Cheap once the scalar verifier is trusted.
- Net: a real new capability (matter source) + a real recovered relation + a
  cleanly-characterized limit with a known fix. Good night's dead-end. Next rungs
  (Maxwell, then EMD for the *secondary*-hair surprise) are now concretely open.

## 2026-06-14 — the irreducible-information meter (the abstractor, reframed + extended)

- Built `26_information_meter.py`, the v6 reframe made concrete: point it at a
  solution family and it reports how many constants are GENUINELY FREE (hair)
  vs FORCED vs SECONDARY (determined by the free ones — the primary/secondary
  distinction, e.g. EdGB's secondary dilaton charge). Glass-box: demand the
  vacuum+Λ residual ≡ 0, reduce to equations on the constants, solve, count
  survivors. No NN.
- **Validated 0/1/2, including a real rotating black hole:** de Sitter → 0;
  Schwarzschild (4D & 6D) → 1; Schwarzschild-dS → 1 with the r² coefficient
  correctly tagged SECONDARY (= −Λ/3) — i.e. the meter rederived Birkhoff;
  mass + floating Λ → 2; a fake 1/r² hair → rejected (forced to 0); and
  **rotating BTZ (2+1, off-diagonal) → 2 (M, J)**. It even caught a
  transcription bug in my first BTZ metric (forced J=0 on the wrong g_tt) —
  it refuses a metric that isn't actually a solution. Added as verify.sh
  battery.
- **Honest dead-end found (where we chose to stop):** the instrument is solid,
  but its NOVEL use — detecting a *surprising* secondary hair (a constant that
  looks free but is forced, the genuinely-new thing) — needs CLOSED-FORM
  modified-gravity solutions, and the marquee ones (EdGB, dCS) are
  numerical-only, so the symbolic meter can't chew them. Crossing that needs
  an engine extension to new sources/theories (e.g. Einstein-Maxwell →
  charged 2-hair, or a closed-form modified theory) — a real next project, not
  a one-night push. So tonight: instrument built + validated; next frontier
  named.

## 2026-06-14 — relation hunt on the EdGB fit coefficients (honest null)

- New `25_relation_hunt.py` (sibling of the abstractor, aimed at a family
  whose law is unknown): scans the EdGB universal-fit coefficient functions
  for hidden exact relations — vanishing coefficients, equal/proportional
  functions. Ran on both the clean 4-param static+rotating set and the
  noisier 3-dof KKZ-class set.
- **Result: clean NULL.** The only relations present are the two already
  understood — (i) the GR limit (every correction coefficient → 0 as p→0,
  confirmed for c1,c3,a1,a2 and the 3-dof numerators), and (ii) horizon
  regularity (c1 ≈ 1.015·c3, 0.10% residual). No *new* algebraic relation
  surfaced. So the empirical fit is "irreducible" at this level: its free
  numbers are genuinely free, forced only by the physical limits we already
  knew — there's no extra compressibility hiding there.
- Value: validates the hunter (it re-finds the known structure precisely) and
  closes the "hidden structure in the EdGB fit" thread honestly. The
  orthogonal-lens search continues — this bounded probe came up empty, as most
  do (the love-of-science 98%).

## 2026-06-14 — the abstractor: recover the meta-law across a family (new capability)

- New step `24_abstractor.py`: reads a whole family of verified rungs and
  recovers the SINGLE law f(N, Λ) behind them — the dimension-dependence
  included — by exact symbolic fitting (search the simplest functional form,
  solve over the rationals; no numeric weights, no NN, glass-box). A level up
  from 05_generalize (which frees one constant within one rung).
- **Unit test PASSED on the static-vacuum catalog** (answer known, so a
  capability demo not a discovery — by design): from the 26 rungs it recovered
  `f = 1 + c1·r^(−(N−3)) − 2Λ/((N−1)(N−2))·r²` UNAIDED — the N−3 exponent and
  the (N−1)(N−2) denominator (it even had to invert to find the latter).
  Reproduced 26/26 exactly AND passed leave-one-dimension-out **prediction
  9/9** (law from the other dimensions predicts the held-out one). Added to
  verify.sh as a regression battery.
- Why it matters: the abstractor is now trusted machinery. Next aim is a
  family whose law is NOT known — the EdGB universal-fit coefficients
  (c1(p)…c4(p), a1(p),a2(p)) — to hunt exact relations among them and try to
  derive each from a physical constraint (horizon regularity, GR limit). That
  turns an empirical fit into structure-plus-explanation. (Context: idea from
  the v6 "orthogonal lens" discussion — build the abstractor, validate on the
  known catalog, then point at the unknown.)

## 2026-06-13/14 — high-D ladder proved + the Kretschmann speedup (hours/never → minutes)

- **Process optimizations shipped** (commit ec07346): `sealed_holdout.py`
  (structural guard — seal once, score one candidate, ledger every access;
  D21); `22_rot_fit.py` defaults to VERIFYING the banked R2 formula vs the
  sealed tables in 0.3 s instead of re-deriving it in ~9 min (D20);
  `03_rediscover.py` optional parallel seeds; dashboard hardening; the
  `ai-coding-standards` skill installed + adapted.
- **Ladder oracle** (`23_ladder_oracle.py`, D19): instead of genetic-searching
  the static-vacuum ladder, PREDICT the Tangherlini family per rung and PROVE
  it directly — seconds-to-minutes vs ~15 min of GP. Proved all of 8+1..12+1 ×
  {Λ=0,−1,+3/4}; catalog 11 → **26 machine-proved families** (committed
  ca44082). Independently re-verified: every one is a real vacuum+Λ solution
  via the verifier path (not the fingerprint), K angle-free, profile complete.
- **The Kretschmann saga.** Caching the 26 families' curvature fingerprints
  stalled catastrophically — a worker ran >20 CPU-hours on an n=9 *AdS* case
  and never finished. Diagnosed LIVE with `py-spy dump --locals` (no stop):
  stuck in `heugcd` inside the final `sp.simplify(K)`. Real cause was NOT
  dimension but the cosmological-constant (Λ≠0) families. Three compounding
  costs, three fixes, all gated on `g.is_diagonal()` (D22): simplify →
  cancel(together); O(n⁸) → O(n⁴) index contraction collapse; and evaluate the
  (angle-independent) K at a regular angle to kill trig swell. Measured: n=9
  AdS 19h-stuck → 2.4 s; n=13 AdS ~never → ~135 s; **exact match vs all
  previously-cached fingerprints** (commit d064640). All 11 remaining profiles
  then cached in 94 min total — work projected at days/never (commit e93987f,
  catalog now 26/26).
- **Regression caught by the gate — then fixed** (commit 344d231): the speedup
  commit had also changed the GENERAL (non-diagonal) path to cancel/together,
  too weak there — it left a θ-dependent K and broke the Painlevé-Gullstrand
  costume test (CANDIDATE_NEW instead of Schwarzschild). Reverted the general
  path to `simplify`; the fast path is diagonal-only. **Gate ALL GREEN** (12
  batteries). Honest note: two of my speedup attempts failed first (deferring
  simplification made it WORSE — the documented expression-swell trap); the
  win came from py-spy pinpointing the exact stuck line, then combining the
  collapse + cancel/together + angle-eval, and validating before trusting.
- **Infra learned the hard way** (D23): repeated Mac power losses + `/tmp`
  wiped on reboot. Now: long compute prefers the always-on VM; logs/scratch
  live in gitignored `runs/`, never `/tmp`; caching is resumable + atomic
  (temp-file + os.replace), losing at most the one family in flight; cross-
  machine results merge by strict union (`merge_catalogs.py`); live runs
  probed with `py-spy` without stopping them.

## 2026-06-12 (night) — v5 COMPLETE: R0′ + R2 audited, R2 protocol repaired, VM hunting 8+1..12+1

- **Context:** R0′ (`21_rot_fingerprint.py`, commit 039a9f7) and R2
  (`22_rot_fit.py`, commit 736b5bb) were banked by another session with
  code + gate but NO docs. This session audited both, re-ran the full
  11-battery gate fresh (ALL GREEN, including 21 at 204 s and 22 at
  560 s), and wrote the honest record.
- **R0′ audit verdict: real, with disclosed deviations.** What shipped
  is a derive-and-verify at 3 exact on-shell rational probes (jets
  solved from the static EdGB equations — the pre-registered "modulo
  static EOM" wrinkle discharges automatically), not the registered
  overdetermined linear-solve. The cross-product identity holds
  EXACTLY at all probes ⇒ **κ_c = 1.0 is now a probe-level prediction**
  and the v5 chain is self-contained. Deviations (3 probes, e^Γ(r₀)
  gauge-fixed, empirically-found common factor) disclosed in
  ROTATING.md.
- **R2 audit found a protocol violation, now repaired:** the committed
  version selected the winning structure by HOLDOUT error across the
  printed grid (selection on the sealed holdout), and the holdout had
  seen one structure iteration (the p¹ fix). Repair, pre-registered
  before re-running: selection by TRAINING error only; frozen winner
  scored once on p=0.7 (disclosed as consumed) and once on a FRESH
  sealed p=0.75 holdout. Same winner either way. **Final: 4-number
  formula, train 0.1321%, p=0.7: 0.1551%, fresh p=0.75: 0.1730%.**
  The R2 prize stands, now bulletproof.
- **VM mystery solved — pkill self-match, not (only) flaky ssh:**
  `pkill -f <script>` inside a `gcloud ssh --command` matches the
  remote wrapper shell's own command line and kills it → exit 255,
  indistinguishable from a network drop. This is what killed
  auto_pipeline.sh's expedition launch. Rules now in VM.md (named tmux
  sessions; kill and launch in separate ssh calls, pattern assembled
  at runtime).
- **VM back to work:** repo pulled to 736b5bb, dashboard relaunched
  (tmux `dash`), and a **high-ladder hunt launched** (tmux `ladder`,
  `~/run_ladder_high.py`, logs to `ladder_high.log`): the 09 sweep
  machinery aimed at 8+1 → 12+1, three Λ sectors — 15 rungs the
  catalog has never seen. Also noted: the old roadmap's "wide
  expedition running on the VM" never existed — 07 is a fixed 3-rung
  battery and the launch had failed (see pkill bug above).

## 2026-06-12 (evening) — Gemini audit, R1 κ_c banked honestly, VM re-established, R0′ pre-registered

- **VM bring-up complete (user-approved option 1):** `~/ansatz-machine`
  pulled f0c20fc → a0fae71 (catalog 4 → 11 families), full `verify.sh`
  gate re-run ON THE VM — **ALL GREEN ✅** (incl. EdGB E0) — dashboard
  restarted and now a live window onto the current repo. Division of
  labor (Mac=dev, VM=run host, docs/VM.md) is real again; the v5 R0
  derivation attempt was the first job actually shipped to the VM
  (Sumit's catch: "laptop can't" was never tested against the VM's
  27 GB free).
- **Gemini intervention audited** (it worked during Claude limit):
  its two physics fixes to `20_rot_shoot.py` are CORRECT — verified
  independently against AY arXiv:1405.2133 eq. 15 (bracket × M⁴/r⁵ in
  ω-space, sign negative: +ζ on a negative Kerr g_tφ weakens dragging).
  Its `frac_resid < 0.007` gate was POST-HOC (bound set just above the
  observed 0.5%) — rejected per Sumit's criteria-integrity directive;
  its "permanently parked / intractable" doc claim was an overclaim —
  corrected in place. Its claimed result had no preserved log —
  reproduced fresh before acceptance.
- **R1 result, reproduced + re-specced:** κ_c selection is now
  threshold-free argmin-with-margin. Residual curve V-shaped:
  14.8 → 6.2 → 4.0 → 1.4 → **0.5** → 0.8 % over κ_c = −2…+2 ⇒
  **κ_c = 1.0 (PC's equation as written), runner-up 1.6× worse;
  c_ay < 0 as AY physics demands.** G3 (δΩ_H ∝ ζ² ratio, 1.81 vs 1.61
  pred) passes for all κ_c ⇒ demoted to sanity gate, disclosure in
  ROTATING.md.
- **R0′ pre-registered (ROTATING.md):** fingerprint derivation of
  G₂/G₃ — random exact-rational instantiation + Schwartz–Zippel
  probes + linear solve over a graded monomial ansatz; intermediates
  never materialize. Credit: Sumit's "terms as vector dimensions"
  intuition → random projections of the term-vector. On success
  κ_c = 1.0 becomes a prediction, the chain self-contained.
- Gemini's `SEARCH_STRATEGIES.md` kept (proposer-side shelf: MCTS,
  e-graphs, LLM-guided proposer).

## 2026-06-12 (afternoon) — R0 exact derivation parked; stuck SymPy process killed on VM

- **R0 symbolic derivation stopped on VM**: `19b_rot_reduce_fast.py` ran 2.3 h on the GCP VM at 99.9% CPU, RSS plateaued at 14.0 GB, no progress past the contraction phase. Killed by choice (SIGTERM) — not a crash/OOM, and flat RSS ≠ proof of intractability [accuracy correction 2026-06-12 evening: original entry overclaimed "confirms SymPy cannot handle it"]. What it does establish: the expand-everything route is exponentially wasteful (GB intermediates, two-line answer).
- **Process Terminated**: Safe-killed the stuck process (PID 21931) without affecting the background Ludo training workloads (`train_v12.py`).
- **Pivot to Pani-Cardoso**: The exact R0 derivation is permanently parked. We are proceeding with the literature-transcribed equations (PRD 79, 084031) and will use the triple-anchor calibration framework (GR limit, small-coupling shape matching, and horizon frame dragging ratios).
- **Next Up**: Debug coordinate/sign conventions in `20_rot_shoot.py` to fix the sign mismatch (negative spin correction shape).

## 2026-06-12 (midday) — fork (a) FINAL: KKZ-CLASS UNIVERSAL 🏆 — EdGB banked

The 3-dof structures + degree-3 coefficient cubics deliver the arc's
peak: **pointwise ≤0.098% at every training p** (finer than KKZ's stated
accuracy, 6 constants vs ~10 — pointwise T3), universal in-sample
0.1031%, and **0.2751% on the SEALED p=0.7 holdout** — KKZ-class on
true extrapolation. The progression that got here, each step measured:
hill-climb 3.6% sealed FAIL → GN+continuation 2-dof 0.53% → tied
9-number 0.72% (and the c1≡c3 relation explained via shared horizon
limit) → 3-dof deg-2 0.56% → **3-dof deg-3 0.2751%**. EdGB track BANKED
at this point per plan — remaining open: KKZ coefficient transcription
for a head-to-head, T3-universal (<0.1% sealed), rotating EdGB.

## 2026-06-12 (midday) — fork (b): the c1≈c3 "mystery" solved, formula → 9 numbers

Tied the A/B tail coefficients (3 params instead of 4): per-p fit
IMPROVED (0.4188% vs 0.4513% worst), sealed holdout passes (0.7202%).
The explanation was sitting in the truth tables: **A(0) ≈ B(0) at the
horizon** (0.9160 vs 0.9172 at p=0.3) — both regular parts share their
horizon limit, both structures park that limit in the leading
coefficient, so the equations force the tie. Horizon regularity in a
coefficient costume, not a new law. Both formulas recorded in RESULTS.md
(4-param: better holdout margin 0.53%; tied 9-number: simpler, better
in-sample). Pushed. Next per scaling mandate: fork (a), the 3-dof
structure for KKZ-class/T3.

## 2026-06-12 (morning, user aligned) — THE UNIVERSAL FORMULA STANDS ✅

The T3 attempt's design call (real local optimizer over smarter GP
pressure) paid off in one shot: **Levenberg-damped Gauss–Newton on the
residual vectors + continuation in p** (11 training tables, p=0.10→0.60,
warm starts). Constants drift silk-smooth and monotone; the degree-2
polynomial assembly loses almost nothing (per-p worst 0.4513% →
universal in-sample 0.4529%); and the **SEALED p=0.7 holdout scores
0.5316%** — true extrapolation, formula stands (<1% bar). The explicit
4-coefficient-function formula is in RESULTS.md v4. Honest framing: KKZ
remain finer per-p (~0.1–0.3%, ~10 coefficient functions); ours is a
compact alternative (12 numbers total) at ~2× their error — not a
dethroning, a different point on the simplicity-accuracy frontier.
Curiosity logged: c1(p) ≈ c3(p) to 3 digits — A and B tails share their
leading coefficient; possibly real structure worth a symbolic look.
Optimizer lesson confirmed: the 15-run's 3.6% holdout FAIL was entirely
the hill-climb's fault — same structure, same data, proper optimizer,
7× better.

## ☀️ 2026-06-12 — MORNING REPORT (the whole night, two minutes)

**Territory:** the ladder sweep passed **all 17 static-vacuum rungs**
(2+1→7+1, three Λ sectors). The catalog tripled to **11 machine-proved
families** — every Tangherlini(-dS/-AdS) up to 8 dimensions, every
Λ-coefficient machine-derived, every 2+1 rung correctly blind-spotted.
The static vacuum room is now strip-mined by us too. (Committed
sweep.log = the per-rung record.)

**EdGB (v4) — the machine now does modified gravity:**
- **E0 ✅** our own derivation of the EdGB field equations matches Kanti
  et al. 1996 symbol-for-symbol (φ-equation ratio 1.000000).
- **E1 ✅** our shooting code builds numerical EdGB black holes that
  reproduce the published KKZ ε(p) to 1–4%; dilaton hair secondary.
- **E2 ✅** fit verifier over the regular RZ parts, honesty-gated.
- **Track B:** GP **rediscovered the continued-fraction RZ shape
  unprompted**; best honest fit **0.2325% max deviation at p=0.3** —
  KKZ's own accuracy class (their bar: "a few tenths of a percent") —
  with 14 constants vs their ~10. T2 reached; T3 (beat them) open.
- **Universal p-formula: honest ❌.** Trained S2 structure hits
  0.44–0.59% at every training p, but constants-vs-p extrapolation to
  the SEALED p=0.7 holdout failed (3.6% linear; quadratic exploded).
  Measured bottlenecks, queued: the constant-fitter (hill-climb lands in
  non-corresponding basins per p — needs a real local optimizer +
  continuation), and 0.7 is true EXTRApolation beyond the 0.1–0.5
  training span. The holdout stays sealed for the next attempt.

**Lessons (now law):** D17 — never let NaN near max(); guard every
component before any reduction (burned twice: "beat KKZ in 9s" with
A=zoo, then an A-only fit with B≡nan). D18 — persist expensive immutable
things (profile cache: build_catalog 1675 s → 2 s; gates back to ~20 min).
D16 struck again in fit-land: rational-function constants have a scaling
gauge; normalize before interpolating them.

**Infra:** VM gate 8/8 green (py3.10/Linux, nice-19, trainer untouched);
dashboards live on both hosts; firewall refreshed to the rotated IP.
Everything pushed: b2de3bd (v4 main) + this morning's wrap commit.

---

## 2026-06-11 (night shift, later) — EdGB pipeline green end to end; first T2 fit

- **E1 ALL GREEN** (after the two-writer log corruption red herring): our
  shooting code integrates EdGB black holes from the E0-validated
  equations, reproducing KKZ's ε(p) to 4.3% (p=0.2) and 1.0% (p=0.4),
  Schwarzschild at tiny coupling to 0.05%, hair secondary & monotone.
- **E2 ALL GREEN** after a score redesign bought by numbers: raw e^Γ
  relative error blows up ~100× near the horizon (Schwarzschild
  "deviated 9847%") — KKZ compare the REGULAR RZ parts, and now so do we
  (A = e^Γ/(1−r_h/r), B = e^{(Γ+Λ)/2}; RZ-Schwarzschild now deviates a
  sane 2.7–17.8%, monotone in p). Pre-registration amendment recorded:
  KKZ-coefficient transcription deferred (structure verified, the full
  rational coefficient functions weren't captured); E2 = transcription-
  free checks.
- **The NaN war (now D17):** max() with NaN burned us twice — first a
  NaN-everywhere candidate "beat KKZ in 9 seconds" with A(x)=zoo, then a
  post-max guard let the hunt fit A while B rode along as NaN ("T1
  0.98%" was an A-only artifact — retracted). Rule: isfinite-check every
  component BEFORE any max/reduction.
- **First honest Track B result: 0.2325% max deviation (T2 band — KKZ's
  own accuracy class) at p=0.3**, with the GP rediscovering the
  continued-fraction-flavored RZ shape unprompted:
  A = 1 − c(1−x)²/(linear in x), B = 1 − c(1−x)⁴/(linear in x).
  Honest caveats: 14 constants vs KKZ's ~10; single p; float constants
  (snapping/parsimony pressure = next iteration). Not victory; real
  progress.
- **Perf (now D18): build_catalog 1675 s → 2 s** by persisting fingerprint
  profiles into the catalog at grow time (self-healing backfill).

## 2026-06-11/12 (night shift) — vacuum territory CONQUERED; EdGB speaks

**The ladder sweep (09) passed all 17 rungs** — every (dimension, Λ-sector)
of the static one-function ansatz from 2+1 to 7+1. The catalog tripled
tonight: **4 → 12 machine-discovered families**, closing with the 8D
Tangherlini–AdS (`1 + r²/21 + c/r⁵`) and 8D Tangherlini–dS
(`1 − r²/28 + c/r⁵`). Every 2+1 rung correctly blind-spotted; every costume
unmasked (Schwarzschild-AdS arrived as `(r(r²+3)+8)/3r` and was still
recognized); every Λ-coefficient (r²/10, 3r²/40, r²/15, r²/21…) machine-
derived per dimension. **The static vacuum room is officially strip-mined
by us too — which was the point.** (Decision: 09 stays OUT of verify.sh —
90 min runtime is campaign-class, not gate-class; its committed log +
catalog are the regression evidence. The new gate battery is 10/E0.)

**VM run host proven:** full 8/8 gate green on Python 3.10/Linux at
nice-19 (alphaludo-l4, trainer untouched). Dashboards live on both hosts.

**v4 EdGB — the machine now speaks modified gravity:**
- **E0 PASSED in one shot**: our SymPy derivation of the EdGB reduced
  field equations (via the effective action, Kanti conventions) matches
  [Kanti et al. 1996](https://arxiv.org/abs/hep-th/9511071) exactly —
  Schwarzschild limit ≡ 0, the Λ-equation algebraic & quadratic in e^Λ
  with root sum/product = Kanti's −β and γ, and our φ-equation literally
  ∝ their eq. (33) (ratio 1.000000, spread 0).
- **E1 (shooting) nearly green**: the headline — our numerically
  integrated EdGB black holes reproduce the published KKZ ε(p) relation
  to **4.3% at p=0.2 and 1.0% at p=0.4**, with the dilaton hair behaving
  as secondary. Battle scars, all measured: sp.solve stalled on the big
  expressions (→ Cramer), the Γ-equation's Λ″ needed function-level
  elimination with verified φ‴/Γ‴ cancellation (the second-orderness of
  EdGB, reproduced by our own algebra), log-r steps overshot the horizon
  shell 2000× (→ integrate in ln(r−r_h)), and exactly-p=0 degenerates the
  dilaton sector (→ tiny-p limit).

## 2026-06-11 — the finisher debugging saga + expedition PASSED + VM prep

- **The expedition passed all three legs** (~1 min total): 7D Tangherlini
  discovered & grown (leg 1, snap at gen 2), **Tangherlini–de Sitter
  discovered & grown** (leg 2, `f = 1 − r²/8 + 1/r²`, snap at gen 17 —
  the rung that failed twice before), memory replay recognized (leg 3,
  snap at gen 4). Catalog: 4 self-discovered families. With the finisher,
  hunts that took 50–150 generations now take 2–17.
- **The four-bug debugging saga that got us here** (all one theme:
  *canonicalize before you reason*):
  1. Tree-slot symbolization creates constant-space GAUGE redundancy
     (`k1·(k2·r + …)`) → solution variety positive-dimensional →
     sp.solve returns [] instead of parametric families. Fix: Laurent
     canonicalization (one unknown per power of r).
  2. Numeric angle-fixing left unsimplifiable trig CONSTANTS in the
     equations (`−4tan(11/10)+4sin(11/5)−4cos(11/5)tan(11/10)` — which IS
     zero) → solve saw "nonzero = 0" → inconsistent. Fix: simplify every
     coefficient; genuinely nonzero constants are a correct early exit.
  3. Root of (2): simplification ORDER. Mixed-index residuals R^a_b +
     symbolic-first simplify → the θ identities fire and the angular
     components collapse to θ-free form (5 components → 2 clean ODEs).
  4. The growth step missed the IMPLICIT coefficient: in
     `−r²/8 + 1 + r⁻²` the mass coefficient 1 has no tree leaf, so
     slot-wise generalization never tested the one constant that was
     free. Fix: generalize Laurent-coefficient-wise.
- A power loss mid-session ate /tmp logs and earlier runs and proved the
  persistence design (catalog/journal/logs in repo) right. Run logs now
  always live in the repo root.
- **VM practice established** (standing rule): runs move to the GCP VM
  niced to 19 (single-core, tens-of-MB — invisible next to the trainer
  there), with `scripts/dashboard.py` (stdlib-only, read-only) on port
  8080 behind a one-IP firewall rule. See docs/VM.md. Parallel seeds
  across idle cores = the island model for free.

## 2026-06-11 — the stationary hall falls: first frame-dragging solution

- Built `08_stationary.py`: first OFF-DIAGONAL ansatz
  (−f·dt² + dr²/h + r²(dφ + ω·dt)², three genomes). Ground truth first:
  rotating BTZ VERIFIED through the engine, sabotaged frame-dragging
  (ω ∝ 1/r³) REJECTED.
- **The gauge-evasion saga** (now D15): the hunt evaded three times —
  constant ω (frame gauge), then *negligible* ω (non-constant, physically
  nothing — converged to the non-rotating solution while dodging the
  penalty), then structures whose only exact solutions are gauge-trivial.
  Fixes, in order: rotation-magnitude penalty (max|ω| ≥ 1e-2), and the
  **algebraic finisher with enrichment** (D14): symbolize a near-miss's
  constants, add the sub-leading k·r^p terms GP rarely composes, solve the
  coefficient system exactly, instantiate free family parameters
  generically (never zero — they ARE the mass/spin).
- **Result: seed 0, generation 12, 9.8 s** — `h = r² + (29/48)²/r²`,
  `f = 4h`, `ω = −1 + 29/(24r²)`: the rotating BTZ family (M=0, J=29/24)
  wearing two gauge costumes at once (time-rescaling + rigid rotation),
  VERIFIED exact, correctly declared BLIND_SPOT (2+1 is CSI forever).
  The machine's first frame-dragging discovery. 08 added to the gate.

## 2026-06-11 — docs structure + the expedition (v3 begins)

- Created this docs tree (JOURNAL / DECISIONS / GLOSSARY / ROADMAP).
- Built `07_expedition.py`: the self-extending campaign. The machine walks
  uncharted (dimension, Λ) rungs and, on every confirmed CANDIDATE_NEW,
  generalizes it and grows its own catalog *mid-run* — then proves the memory
  works by re-hunting a grown rung and recognizing the family. (Results below
  in this entry once the gate runs.)

## 2026-06-11 — v2 shipped; repo goes public

- **Two-function hall (06) PASSED** — Birkhoff honesty stress test, zero false
  novelty across 3 rungs; gauge checks all `f/h = const`. The memory rung
  matched the machine's own grown family from the day before: the
  discover → generalize → remember → recognize loop closed.
- Measured failures bought two fixes: 2D Newton → nested 1D bisection (steep
  invariant curves); per-slot crossover stagnation → **gene duplication**
  operator (Birkhoff rung then fell in ~2 generations).
- **Catalog auto-growth (05)** shipped: constants tested one-by-one against
  the symbolic verifier — mass came out free ("hair"), the Λ-coefficient and
  the asymptotic 1 came out structural ("law"). Families persisted to
  `catalog_discoveries.json`.
- Installed the `ai-coding-standards` skill (project-level) and added
  `verify.sh` as the single gate. Full gate green (6 batteries, ~14 min,
  dominated by the hall).
- **Pushed to https://github.com/sumit7194/ansatz-machine** (MIT, one root
  commit, description + topics set).

## 2026-06-10 — v1: the machine works end to end

- Verified the niche via web research (no published AI-found exact metric as
  of June 2026; Cartan–Karlhede has no Python implementation).
- Built the GR engine (pure SymPy, dimension-agnostic, three-valued verdicts),
  the verifier battery (Kerr ✅ 9 s in rational u=cosθ form after two measured
  failures), the (K, |∇K|²) fingerprint filter (costumes unmasked, blind spots
  declared), the GP rediscovery loop (Schwarzschild blind in 2–3 generations),
  and the six-rung campaign (80 s; two finds outside the catalog correctly
  escalated CANDIDATE_NEW).
- Machine-taught lessons: it found Minkowski first, then pure de Sitter (the
  triviality ladder was born); it prefers negative-mass branches on catalogued
  rungs; 2+1 is a permanent, *correct* blind spot.
