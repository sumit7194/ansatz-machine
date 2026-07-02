# Journal

*Dated activity log, newest first. One entry per working session: what was
built, what broke, what the machine taught us. Numbers live in
[RESULTS.md](../RESULTS.md); decisions live in [DECISIONS.md](DECISIONS.md).*

---

## 2026-06-24 — NEW CAMPAIGN: observational signatures ("what would we see?"); §86 rotating face
- After banking item-3 (the eyes-open swing confirmed the symbolic wall — `_quadrupole_deriv.py` swamped, 2.5h
  Ricci), stepped back and picked a new direction that LEANS INTO the engine's numerical strength and avoids
  the (r,θ)-symbolic wall: the observational lens — given any black hole, what does a telescope measure?
- Surveyed: the engine already has scattered observational pieces — §45/analyzer.observables (static photon
  sphere, shadow, ISCO, eikonal QNM), §68 (Kerr shadow edges), §56/§77 (QNM), §49/§67 (lensing), §50/§51
  (precession/redshift). The campaign's value is UNIFYING + filling gaps.
- §86 fills the two real rotating gaps: (A) the Kerr ISCO (Bardeen–Press–Teukolsky) — a=0→6M, extremal→1M
  prograde (horizon) / 9M retrograde, monotone; (B) the FULL shadow silhouette (α,β) — the actual EHT image
  curve, not just §68's edges: a→0 circle (area exactly 27π), a>0 displaced/flattened D-shape (centroid 0→+1.12,
  area shrinks). (C) spin is written in BOTH the ISCO (X-ray) and the shadow (EHT). Cross-validated: edges
  (|2|,|7|)M match §68's independent computation; ISCO hits 6/1/9; circle area = 27π. All closed-form exact.
- One tolerance fix caught: prograde ISCO → 1M only in the singular a→1 limit (1.016M at a=0.999999), not at
  finite spin — loosened the check.
- §87 = the GENERAL version (the campaign's real power): `observe_rotating.py` computes the photon ring,
  shadow b=L/E, and ISCO NUMERICALLY from any rotating hole's equatorial g_tt,g_tφ,g_φφ (+ finite-diff
  derivatives) — so it works for modified/discovered holes, not just Kerr. Validated on Kerr to <1% (photon
  ring 0.00%, ISCO 0.01–0.70% vs the closed forms). DISCRIMINATION: Kerr–Newman (Q=0.5) shrinks shadow (Δb≈0.35)
  + ISCO (Δ≈0.55, charge tightens the light); §85's deformed Kerr shifts photon ring (Δ≈0.34) + ISCO (Δ≈1.3).
  ⇒ an EHT shadow + an X-ray ISCO would distinguish these from Kerr — the "is it exactly Kerr?" test, run by
  the engine. This is the observational lens working as a GENERAL tool (the standing "widen" steer).
- §88 = the THREE MESSENGERS (campaign capstone): added the eikonal RINGDOWN to observe_rotating (LIGO's QNM
  from the photon ring, ω=ℓΩ_c−i(n+½)|λ|, Cardoso correspondence) — validated vs precise Leaver (§77) to
  eikonal accuracy (~1.5–5.5% on ω_R, correct spin trend). So from one metric: shadow (EHT) + ISCO (X-ray) +
  ringdown (LIGO). DISCRIMINATION with COMPLEMENTARY sensitivity — and the stress-test made it honest:
  (1) cranking the §85 bump to ε=5 gave a shadow-b shift of 68.768M — GARBAGE: the photon ring fell inside the
  ergosphere (r<2) where b=L/E diverges. Guarded to a physical range + used ε=1. (2) At ε=1 the deformed
  ringdown shifts only 0.009 (vs shadow 0.067, ISCO 0.242) — NOT a failure but PHYSICS: the 1/r³ bump is
  near-horizon, so the disk-edge observables feel it but the photon-ring ringdown barely does. Reframed (C) to
  that complementary-sensitivity finding (different messengers probe different radii) — a better, truer claim
  than the original "all three move." Kerr–Newman (global) moves all three.
- §89 = the PHOTON SUBRINGS (one instability, two telescopes): the n-th photon subring is demagnified by e^{−γ},
  γ=π·λ/Ω_c. (A) Schwarzschild γ=π EXACTLY (demag ~23×). (B) γ falls with spin (23×→2× at a→0.99 — fast holes'
  subrings are resolvable); Kerr–Newman shifts it. (C) THE DEEP LINK: the same photon-ring λ sets BOTH the EHT
  subring γ AND the LIGO ringdown damping ω_I — one instability, two observations. Stress-test caught: my first
  (C) test (γΩ_c/π == ω_I/(n+½)) was a TAUTOLOGY (both built from the same λ → λ==λ); replaced with the
  INDEPENDENT cross-check (ω_I vs precise Leaver §77, ~5–8% eikonal; γ anchored at π) so the correspondence is
  genuinely demonstrated, not a code identity. Added subring_gamma/subring_demag to observe_rotating's ringdown.
- §90 = BLACK HOLE OR IMPOSTER? — the campaign's sharpest caution: a shadow proves a PHOTON SPHERE, not a
  HORIZON. (A) the Ellis wormhole (no horizon, no singularity) casts a shadow of radius b₀; tuned b₀=3√3 it's
  IDENTICAL in size to Schwarzschild (5.196) — EHT can't tell them apart by shadow. (B) over-spinning Kerr
  (a>1, naked singularity) has NO prograde light ring (closed form undefined for a>1, confirmed numerically) —
  a horizonless object need not even cast a normal shadow. (C) so what proves a BH? Not the shadow — need the
  ISCO/disk, the ringdown + ABSENCE of echoes a surface makes, the horizon's absorption: the multi-messenger
  program is the real test. Stress-test caught: a=1.0's "no light ring" was a search-range artifact (the ring
  is at r=1=horizon) — tightened the claim to the rigorous a>1 case. The observational campaign is now §86–§90.
- §91 = THE EHT IMAGE'S TILT: the shadow shape depends on observer inclination θ_obs (Bardeen formulas).
  (A) the asymmetry (centroid displacement/radius) scales with tilt — Kerr a=0.9: 0.38 edge-on → 0.04 face-on,
  monotone. (B) edge-on = §86's D-shape; face-on → circle. (C) the SPIN–INCLINATION DEGENERACY made
  quantitative: a=0.9 face-on (0.037) is MORE circular than a=0.3 edge-on (0.116) ⇒ a round shadow does NOT
  imply low spin; M87* (~17°, near face-on) → 0.121, consistent with its near-circular ring; the shape alone
  can't fix spin (need brightness asymmetry). Honest caveat made quantitative. Campaign now §86–§91 (7 batteries).
- §92 = THE ACCRETION ENGINE (the X-ray messenger made concrete — how spin is actually measured):
  (A) radiative efficiency η=1−E_ISCO: Schwarzschild 5.72% (=1−√(8/9)), rising to ~38% at a=0.9999 (→42.3%
  extremal) — most efficient steady engine known (fusion 0.7%); computed from our ISCO + _energy. (B) disk
  T_peak ∝ r_ISCO^(−3/4): smaller ISCO (higher spin) ⇒ hotter ⇒ harder X-ray (1×→3.6×). (C) the chain spin→
  ISCO→{efficiency,temperature}→thermal continuum IS the continuum-fitting method (Cygnus X-1, GRS 1915).
  Campaign now §86–§92 (8 batteries). All textbook physics, computed from the metric.
- §93 = WEIGHING THE SPIN THREE WAYS (campaign capstone, ties §86–§92): a null test of the Kerr hypothesis.
  Assume Kerr, infer the spin from each of the shadow / ISCO / ringdown, check agreement. (A) true Kerr a=0.70
  → all three give 0.700 (spread 2e-4, consistent). (B) the BLIND SPOT (honest): Kerr–Newman (a=0.6,Q=0.5) →
  all infer a≈0.72 (charge mimics spin CONSISTENTLY) — the test doesn't flag it; passing ≠ proving Kerr.
  (C) the SIGNAL: the §85 near-horizon bump shifts the ISCO more than the photon-ring observables (§88's
  complementary sensitivity) → the three DISAGREE, spread grows with ε (0→0.034, ISCO disagrees most) ⇒ failing
  proves non-Kerr. Stress-test caught: KN was supposed to be my "inconsistency" example but it's Kerr-DEGENERATE
  (consistent) — turned that into the honest (B) blind-spot result, and used the near-horizon deformation as the
  real (C) signal. Campaign now §86–§93 (9 batteries).

## 2026-06-23 — ITEM-3 PROXY RESOLVED: no Carter constant under deformation (§85)
- Cracked the decisive symbolic step NUMERICALLY after the full-symbolic route swamped (7.5h at 98% CPU, no
  output — the classic SymPy blow-up; killed it, recorded the dead end in `_killing_search.py`). User caught
  the 7h run on the dashboard ("its running from 7 hours") — right call.
- Method (`_qinvariant.py`): a conserved quadratic C=Σc_k φ_k(r,θ,p_r,p_θ) is constant along every geodesic;
  sample many orbits at fixed E,L (varied inclination → varied Carter value), mean-subtract per orbit, SVD —
  a genuine invariant is a right-singular vector with a machine-ZERO singular value, far below the rest.
- TWO false positives caught by stress-testing (this is the whole point):
  (1) with few orbits, near-zero SVs are DIMENSIONAL artifacts (5 orbits × 2-tori = 10 dims < 13 basis) — fixed
      by flooding with orbits (2N >> basis);
  (2) the extracted "invariant" was +1·u²/om −1·u⁴/om −1·u² which ≡ 0 since om=1−u² — a BASIS IDENTITY, a false
      machine-zero SV. Fixed by removing u⁴/om + an explicit linear-independence check on random points.
- RESULT (stress-tested, clean): VALIDATION — the fit recovers Kerr's Carter constant exactly (smallest SV
  5.6e-14, gap 3.6e10, recovered C = p_θ²+11.56·cot²θ+0.035·cos²θ = Carter to the digit). DEFORMED Kerr — NO
  machine-zero SV: smallest 3e-3 (ε=2) → 5.7e-3 (ε=5) → 1.6e-2 (ε=10), GROWING with ε, no gap, 11 orders above
  Kerr's. So the deformed metric has no conserved quadratic ⇒ NON-integrable. With §84 (regular tori): the
  deformation breaks integrability KAM-gently ⇒ near-integrable, no hidden symmetry. Resolves §82's
  "undetermined"; refutes "a different Killing tensor survives." Caveat: no quadratic Carter; a quartic Killing
  tensor isn't excluded. Battery §85 (numpy optional, skips like §77). The full modified-gravity 2D-PDE (the
  real metric) remains the open frontier; the PROXY question is answered.

## 2026-06-23 — POINCARÉ SECTIONS: sharper integrability lens (§84); + prior-art correction
- Resumed item-3 (integrability frontier). Built `scripts/poincare.py` — a native Poincaré surface-of-section
  tool via the Hamiltonian 2-DOF reduction (E, L conserved; analytic inverse metric, lambdified). The reduced
  H is conserved to ~1e-14 — the integrator is essentially exact. This is the SHARPER companion to
  `geodesic_chaos.lyapunov`: Lyapunov averages weak chaos away; a Poincaré section SEES it (torus = closed
  curve, box-dim≈1; chaos = filled area, box-dim→2). Box-counting discriminator VALIDATED on Hénon–Heiles
  (regular 0.95, chaotic 1.34).
- Battery §84: (A) discriminator validated; (B) Kerr → clean torus (0.68), H-drift 8e-16 → integrable;
  (C) the §82 quadrupole-deformed Kerr → REGULAR where bound orbits survive; where the deformation is strong
  (eccentric orbit to pericenter ~3, 30–70% bump) the orbit is DESTROYED (unbound), NOT chaotic. Across every
  orbit sampled: regular-or-destroyed, NO bounded chaotic sea found.
- The numerical reality that shaped this: a 1/r³ quadrupole is negligible at far orbits (~0.03% at r~8 — so
  "deformed Kerr regular there" is near-trivial) and DESTROYS bound orbits when cranked strong (no clean
  bounded-chaotic regime exists for it). I caught the "negligible at the orbit" issue myself mid-run — the
  honest correction. So §84 is a SHARPER null than §82 (Poincaré > Lyapunov), but still evidence, not proof.
- The decisive step left on the proxy is the symbolic Killing-tensor SEARCH (does a DIFFERENT Carter-like
  tensor close for the deformed metric?). The dynamical evidence now favors "integrability preserved."
- Also (2026-06-23): a prior-art re-audit (another session) OVERTURNED our rotating-EdGB "no closed form /
  unclaimed gap" claim — closed-form rotating EdGB exists (Ayzenberg–Yunes, Maselli, arXiv:2510.05208).
  Corrected the wording across 5 docs to "compact 4-number fit, compactness only." Memory updated: search each
  claim separately by exact wording; "unclaimed territory" in our docs is now provisional. See DECISIONS/README.

## 2026-06-20 — ROADMAP #2 DONE: tetrad-free Weyl invariants — coordinate-free type (§83)
- Closed the §76 caveat properly. §76's "coordinate-free oracle" computed the complex Weyl invariants I, J
  only in the canonical −f,1/f tetrad, so it lost the TYPE sector in any other chart. Now I, J are pure
  Weyl-tensor contractions (tetrad-free): I=(A−iB)/16, J=(C₃−iD₃)/96, with A=C·C, B=C·*C (the magnetic/
  Chern–Pontryagin part), C₃ the cubic, D₃ its dual. The constants 1/16, 1/96, −i were CALIBRATED against the
  known NP values — Schwarzschild (A=48M²/r⁶, C₃=96M³/r⁹ ⇒ I=3M²/r⁶, J=M³/r⁹) and Kerr numerically (I=3Ψ₂²,
  J=−Ψ₂³ to ~7 digits, including the magnetic B,D₃ part where it's non-zero).
- New: `analyzer.weyl_invariants_tensor(geo)` (symbolic, ~1-2s for diagonal) and
  `numeric_curvature.weyl_invariants_numeric(g,x)` (off-diagonal, Kerr). `invariant_fingerprint` now uses the
  tetrad-free I, J for any diagonal metric (so isotropic Schwarzschild gets them too — §76 still green, values
  identical). §83 validates: (A) tetrad-free I,J == NP I,J on the zoo (independent cross-check); (B) TYPE
  coordinate-invariant (standard vs isotropic Schwarzschild agree at the mapped point); (C) speciality I³−27J²
  chart-free detector; (D) OFF-DIAGONAL Kerr numeric → type D, |I³−27J²|/|I³|≈4e-14, no tetrad.
- Stress-test caught an overclaim before it shipped: I'd framed this as "the full Petrov TYPE, coordinate-free."
  Checked a type-N vacuum pp-wave (H=x²−y²): I=J=0 (and Weyl-square 0) YET Weyl≠0 — indistinguishable from
  type O by polynomial invariants. So I,J give SPECIALITY + magnitude, NOT the full type; {II|D} and {III|N|O}
  still need the adapted tetrad (§80). Added that as §83(E), an explicit honest boundary, and softened the
  invariant_fingerprint docstring + ROADMAP. The §76 CHART caveat is closed; the inherent incompleteness of
  scalar invariants is stated, not hidden.

## 2026-06-20 — ITEM 3 PROBED HONESTLY: the integrability frontier (§82)
- Took a real run at ROADMAP item 3 (rotating modified-gravity BHs). The full prize — solving a modified
  theory's O(a²) field equations — is a 2D PDE, genuinely research-scale; I did NOT fake it. Instead I
  attacked item 3's scientific CORE with tonight's verified tools (§78 Killing-tensor verifier + §79 chaos
  lens): deform Kerr by an l=2 quadrupole bump ε(3cos²θ−1)/r³ on g_tt, ask if integrability survives.
- This is a clean example of the stress-test discipline WORKING. First draft asserted a tidy headline:
  "the quadrupole deformation breaks the Carter constant at O(a²ε)." TWO things were wrong, both caught:
  (1) the "a²ε scaling" was me misreading the FIRST component the residual function returned — the numeric
  check showed the static (a=0) case gives a large residual too, so the scaling claim was false;
  (2) more importantly, the chaos scan REFUTED "deformation ⇒ chaos": across 32 deformed orbits (ε≤0.6,
  r∈[4,8], inclinations 0.05–1.0) NOT ONE shows chaos — λ sits at the regular ~0.01 floor, same as Kerr.
- The honest result (what §82 now asserts, all verified): (A) Kerr's Carter tensor is Killing (§78);
  (B) the *literal* Kerr Carter tensor stops closing for the deformed metric (residual≠0, symbolic+numeric);
  (C) YET no detectable chaos (the lens DOES see chaos when present — di-hole λ≈2.09 — so this is a real null);
  (D) therefore integrability's fate is UNDETERMINED — a different Killing tensor may survive, or chaos hides
  below detection. The naive "deform ⇒ chaos" guess FAILS. Deciding needs a Killing-tensor PDE search or
  Poincaré sections; the modified-gravity metric itself needs its field-equation solve (still open).
- Lesson reinforced: a green battery must assert only what's verified. The robust outcome of a hard frontier
  can be an honest "undetermined + here's what it'd take," not a forced clean claim.

## 2026-06-20 — V8 ROADMAP BUILD: precise QNM oracle (§77) [item 1, highest leverage]

- User: "work on these tonight, not for later" — building the bridge-driven v8 roadmap. Item 1 (highest
  leverage): the precise QNM oracle beyond §56's eikonal.
- First tried a pure 6th-order WKB (dependency-free, builds on §56's potential) — 2nd order was close
  (Schwarzschild ℓ=2 real 0.399 vs 0.374) but the higher-order Iyer-Will/Konoplya coefficients are
  error-prone from memory and my assembly was wrong (gave 0.20−0.18i). Rather than ship a subtly-wrong
  oracle, switched to the exact tool the roadmap names first.
- Installed `qnm` (Stein 2019, Leaver's continued fraction; pulls numpy/scipy/numba) — D27 records the
  dependency decision: precise QNM is inherently numerical, so it's an OPTIONAL companion track isolated
  from the pure-SymPy core (only `qnm_precise.py` + §77 import it; analyzer stays pure; §77 fail-soft skips
  if absent). `scripts/qnm_precise.py`: `qnm_precise(M,a,ℓ,m,n)` + damping_time + quality_factor.
- Battery §77: (A) Schwarzschild ℓ=2,n=0 = 0.37367−0.08896i EXACT (vs §56 eikonal 3% off); (B) the 221
  overtone (a=0.7) = 0.52116−0.24424i (deepstrain's δ; eikonal can't give it); (C) spin blueshift + Q rise;
  (D) no-hair now 0.1%-level (two modes overdetermine (M,a)). Turns Move B from few-% to a precision test.

## 2026-06-20 — STRESS-TESTING the v8 work (user: "robustness is the only north star")

- User reaffirmed the operating principle: correctness is the ONLY objective (nothing on the line — not
  publishing, not a career); stress-test every claim before it counts. A green gate proves the batteries
  RUN, not that the claims are SOUND. Adversarially probed all four v8 items.
- §78 (symbolic Killing-tensor PROOF) — highest risk (a lenient zero-test = false positive). SOUND: the real
  Carter tensor passes; all 4 perturbations REJECTED; reducible Killing tensors (ξ_aξ_b, ξ_(aη_b) from the
  KVs) accepted; K is genuinely irreducible (K_ii/g_ii ratios all differ, not ∝g). Baked the
  perturbation-rejection check into battery 78 (C') so the verifier can't silently go lenient.
- §79 (chaos lens) — CONVERGENCE test: Kerr & Schwarzschild λ HALVE as T doubles (λ~1/T→0, the regular
  signature); di-hole λ=2.0907 PLATEAUS flat across 8× integration time (a genuine Lyapunov exponent). The
  lens correctly distinguishes integrable from chaotic. SOLID.
- §77 (precise QNM) — matched published Leaver/Berti values for a=0 (l=2 n=0,1; l=3 n=0) and a=0.9, exact
  M-scaling (ω∝1/M), smooth a→0. One 3rd-digit discrepancy at a=0.5 traced to MY hand-typed reference being
  wrong (the qnm package is peer-reviewed + validated against Berti's tables and matched everything I'm sure
  of). Tool sound; my expected-value was the error — the test kept me honest.
- §80 (numeric Petrov) — FOUND TWO REAL BUGS: `petrov_type_numeric` used a RELATIVE-only tolerance, so (1)
  de Sitter (Weyl=0, type O) was misclassified as type I (pure noise looks like signal), and (2) large-r
  Kerr (tiny Ψ2) as type II (FD noise overtook the relative tol). FIXED: added an ABSOLUTE noise floor (~1e-7;
  measured FD noise ~1e-9) — all-below-floor ⇒ type O. Re-validated: Kerr type D at 15 points (r∈[3,30]),
  de Sitter→O, Schwarzschild→D. Baked the cross-checks into battery 80 so it can't regress.
- Outcome: §77/§78/§79 sound as claimed; §80 had a real classifier bug, now fixed + hardened. THIS is why
  we stress-test.
- Then made the audit PERMANENT: battery `81_analyzer_audit.py` pins the analyzer's core verdicts to ground
  truth — physical? (wormhole NON-physical/NEC, RN & dust physical, de Sitter SEC-only), made_of
  (vacuum/EM/Λ/perfect-fluid), singularities (r=0 for BHs, NONE for de Sitter/Minkowski — no hallucination),
  horizon (RN two horizons, both T,S>0, smaller hotter — the §64 |f′| fix). All ground-truth, all green. Any
  future regression on these now turns the gate red. Stress-testing is the standing discipline now.
- Also stress-tested the EARLIER bridge oracles (§72–76, built pre-directive). §76 (invariant fingerprint):
  found a real coordinate-freeness CAVEAT — the Weyl sector was computed only in the canonical −f,1/f form,
  so the "coordinate-free oracle" dropped the Weyl part in other charts (isotropic Schwarzschild). Confirmed
  the invariants ARE scalars (Kretschmann chart-invariant at a mapped point) → scope, not a correctness bug.
  HARDENED: added the tetrad-free Weyl-SQUARE C_abcd C^abcd = K−2R_abR^ab+R²/3 (4D identity) to
  invariant_fingerprint for any diagonal metric — genuinely coordinate-free (§76(D): standard vs isotropic
  Schwarzschild agree at the mapped point). The NP {I,J} (algebraic type) stay canonical-form-only; the
  tetrad-free cubic invariant is roadmapped. So: caveat found → invariants verified scalar → real fix shipped.

## 2026-06-20 — V8 minor: Petrov type of Kerr (§80, numeric) — the §57 UNKNOWN closed

- Minor item: petrov() auto-tetrad for Kerr. Found the real blocker isn't the tetrad — it's Kerr's symbolic
  WEYL tensor (swamps; the §48/§57 limit). The §78 Killing-tensor proof dodged this (Christoffels only), but
  Petrov genuinely needs Weyl. Tried symbolic u-coords + Kinnersley tetrad — the √(1−u²)/complex contractions
  swamped simplify (>2min, killed). Pivoted to NUMERIC (like §58/§69/§79 for Kerr).
- Added to numeric_curvature.py (purely additive): `_riemann_lower_numeric`, `weyl_scalars_numeric` (Weyl =
  Riemann − Ricci terms, finite-difference — trig doesn't faze it), `petrov_type_numeric` (|Ψ|-pattern with
  tolerance). Battery `80`: Kerr → only Ψ2≠0 (others ~1e-10) → type D; Ψ2 = −0.007859−0.001294i matches the
  exact −M/(r−ia cosθ)³; speciality I³−27J²≈1e-27. analyzer.petrov stays symbolic+perf-guarded; numeric
  companion closes the §57 Kerr UNKNOWN. A general auto-PND finder is the extension.

## 2026-06-20 — V8 item 4: geodesic integrator + chaos lens (§79) — integrability, measured

- Item 4: native `scripts/geodesic_chaos.py` — `trajectory(g,x0,u0)` (RK4) + `lyapunov(g,x0,u0)` (largest
  exponent via renormalized nearby orbits). Pure Python (finite-diff Christoffels, no numpy — stays in core).
  Battery `79`. The headline ties to §78: a hidden symmetry (Killing tensor) ⟺ integrable ⟺ λ≈0.
- (A) Kerr orbit conserves (E,L,μ²,Carter) to 1e-11 (integrator correct, 4 constants). (B) λ(Kerr)=0.0094≈0
  REGULAR. (C) λ(Majumdar–Papapetrou di-hole)=2.09 CHAOTIC (~222×). Debug: di-hole orbits plunged into a
  center until I added angular momentum (v_y, axial L) — then bounded & chaotic. (D) integrability ⟺ hidden
  symmetry (§78) ⟺ λ≈0 — the lens MEASURES what the proof CERTIFIES, on any metric.
- Purely additive (no existing-file change). Gate green.

## 2026-06-20 — V8 item 2: symbolic Killing-tensor verifier (§78) — the Carter constant PROVEN

- Item 2: turn §58/§69's NUMERIC Carter-constant check into a symbolic PROOF. Key insight: the
  Killing-tensor equation ∇_(aK_bc)=0 needs only CHRISTOFFELS (first derivatives), NOT Riemann — so it
  stays tractable where the full curvature swamps. And in rational u=cosθ coords Kerr's metric is rational,
  so the residual reduces by cancel/together with no trig blow-up. Prototype closed in ~1.6s (Christoffels
  0.7s + check 0.9s).
- Added `Geometry.is_killing_tensor` / `killing_tensor_residual` to gr_engine (zero-test: cancel→together
  then expand_trig+simplify — the same trick the Kretschmann uses for trig). Battery `78`: (A) metric g
  passes (∇g=0); (B) control fails (residual≠0); (C) Kerr Carter tensor Σ(lₐn_b+l_b nₐ)+r²g ⇒ ∇_(aK_bc)≡0
  SYMBOLICALLY — the Carter constant, certified as a theorem; (D) discover→verify now ends in a proof.
  Touched gr_engine ⇒ full gate is the regression check.

## 2026-06-19 — INVARIANT FINGERPRINT (§76): coordinate-free oracle for learned geometry

- Switched the bridge focus to the OTHER sister project (tabula-geometrica, learned geometry) — its oracle
  need is coordinate-free ground truth (cf §42 causal structure). Added `invariant_fingerprint(geo)` to
  analyzer (callable, NOT auto-run — invariants heavy for off-diagonal): Ricci sector {R, R_abR^ab} (matter,
  any metric) + Weyl sector {I,J} (free gravity, static spherical diagonal via §57 tetrad). Battery
  `76_invariant_fingerprint.py`. Future use: a learned-geometry net's output validated against the invariant
  fingerprint (coordinate-proof); fills the no-Python-Cartan–Karlhede gap.
- (A) distinguishes flat/Schwarzschild/RN/de Sitter coordinate-free. (B) resolves the R=0 degeneracy:
  Schwarzschild & RN both R=0 but Ric²=0 vs 4Q⁴/r⁸ (charge invariant). (C) sectors complementary:
  Schwarzschild vacuum (Ricci=0) but Weyl≠0; de Sitter conformally flat (Weyl=0) but R≠0 — matter vs tidal.
  RN Weyl I=3(Mr−Q²)²/r⁸ (charge in gravity sector too). Honest: finite set, not full Cartan–Karlhede; rare
  coincidences need gradients (§02). Gate: 63 green.

## 2026-06-19 — AREA THEOREM (§75): a merger-inference consistency oracle

- User steer: before building, think through FUTURE USE — don't build for the sake of it. So picked a hard
  CONSISTENCY CONSTRAINT (can't be useless): Hawking's area theorem as a check on inferred merger params.
  Battery `75_area_theorem.py` (standalone). Future use: deepstrain infers (m₁,m₂,M_f,a_f) from a waveform;
  the 2nd law A_f≥A_1+A_2 is a hard GR validation those numbers must pass.
- (A) Schwarzschild: A_f≥A_1+A_2 ⇒ M_final≥√(M₁²+M₂²). (B) radiated-energy bound ≤(M₁+M₂)−√(M₁²+M₂²); equal
  mass ≤ 1−1/√2 ≈ 29.3% — the SAME bound as Penrose §60 (both irreducible-mass). (C) Kerr: A=16πM_irr²
  (M_irr=√(Mr₊/2)), 2nd law M_irr,f²≥ΣM_irr². (D) real ~5% merger inside the 29.3% ceiling → consistent.
  Ties §60+§61+§72/73. Gate: 62 green.

## 2026-06-19 — GW POLARIZATIONS (§74): the modes-of-gravity test (GR null hypothesis)

- Another bridge oracle: the polarization content of a GW is a falsifiable GR test, and ansatz supplies the
  exact GR null hypothesis. Battery `74_gw_polarizations.py` (standalone). Ties §59 (a GW = time-varying
  tidal field). (A) TT strain h=[[h₊,h×],[h×,−h₊]] (2 dof, traceless); ring response δxⁱ=½hⁱⱼxʲ → + pattern
  (axes) and × pattern (45°). (B) SPIN-2 verified: under rotation ψ, (h₊+ih×)→e^{−2iψ}(h₊+ih×) (residual 0),
  45° swaps +↔×. (C) the modes-of-gravity test: GR=2 (tensor) polarizations, general metric theory up to 6
  (2 tensor + 2 vector + 2 scalar, Newman–Penrose E(2)); a vector/scalar mode in data ⇒ not GR. (D) clean
  GR-vs-modified-gravity discriminant for detectors. Gate: 61 green.

## 2026-06-19 — RINGDOWN TEMPLATE (§72) + INSPIRAL CHIRP (§73): the bridge waveforms

- User reframed: these lenses are TOOLS/ORACLES for the bridge + sister projects (deepstrain spectroscopy,
  tabula-geometrica geometry), not for a write-up. So picked the two most bridge-relevant: the full LIGO
  waveform as exact ground truth.
- §72 RINGDOWN TEMPLATE (`72_ringdown_template.py`, standalone). §56's QNMs → time-domain strain
  h(t)=Σ A_n e^{−t/τ_n}cos(ω_n t+φ_n) (verified it solves the damped-oscillator ODE). Damping = light-ring
  instability (τ=1/[(n+½)λ], §56/§66); Q=ℓ/(2n+1); ℓ=2,n=0 ⇒ Q=2, Mω_R=0.385 (Leaver 0.374). THE NO-HAIR
  TEST (deepstrain's): ω(ℓ,m,n)=f(M,a) only ⇒ ≥2 modes overdetermine (M,a) ⇒ Kerr-consistency; parameter-free
  ω_R(3)/ω_R(2)=3/2. ansatz = the exact ω(M,a) oracle a measured ringdown is fit against.
- §73 INSPIRAL CHIRP (`73_inspiral_chirp.py`, standalone). Quadrupole L=(32/5)μ²M³/r⁵ → orbit decays;
  dΩ/dt=(96/5)M_c^{5/3}Ω^{11/3} depends ONLY on the chirp mass M_c=(m₁m₂)^{3/5}/(m₁+m₂)^{1/5} (verified
  M_c^{5/3}=μM^{2/3}); Ω∝(t_c−t)^{−3/8} (the −3/8 from the 11/3 exponent). M_c (inspiral) + (M,a) (ringdown
  §72) = the full inspiral→merger→ringdown template, the engine's ground truth for the bridge. Gate: 60 green.

## 2026-06-19 — HAWKING SPECTRUM (§70) + ADM 3+1 (§71): two more (user: "lets continue with these")

- §70 HAWKING RADIATION & GREYBODY (`70_hawking_spectrum.py`, standalone). Builds on §56 (potential) + §64
  (T). Spectrum dN/dωdt = Γ_ℓ(ω)/[2π(e^{ω/T}∓1)] — thermal Planck × barrier transmission. Greybody limits
  (exact ends, full Γ(ω) numerical like §56's QNMs): high-ω → 27πM² (shadow §45/§68), low-ω s-wave → A_H=16πM²
  (area theorem). Negative heat capacity C=dM/dT=−1/(8πT²)<0 (heats as it shrinks). Death: L∝AT⁴∝1/M² ⇒
  dM/dt=−α/M² ⇒ t_evap=M₀³/3α ∝ M³. All symbolic.
- §71 ADM 3+1 & CONSTRAINTS (`71_adm.py`, standalone). GR as dynamics: 10 Einstein eqs = 4 constraints
  (1 Hamiltonian + 3 momentum) + 6 evolution (γ_ij, K_ij). 4-metric → (lapse N=√f, shift Nⁱ, spatial γ).
  HEADLINE: the Hamiltonian constraint ³R+K²−K_ijK^ij=16πρ on an FLRW slice (³R=6k/a² computed via Geometry
  on the 3-metric; K=−3H, K_ijK^ij=3H²) IS the Friedmann equation H²+k/a²=(8π/3)ρ — §37 is literally the
  Hamiltonian constraint. Also: Schwarzschild t=const vacuum slice (K=0) ⇒ ³R=0 (the curved Flamm slice §63
  is scalar-flat). Gate: 58 green.

## 2026-06-19 — KILLING–YANO: the root of the Carter constant (symmetry tower complete)

- Third of the "few more strong ones", and a satisfying capstone to the symmetry thread (§58). The Carter
  Killing TENSOR K is itself a square: there's a deeper antisymmetric Killing–YANO 2-form Y with K=Y·Y and
  ∇_(a Y_b)c=0. Battery `69_killing_yano.py` (numeric, like §58). Got the Kerr KY 2-form right first try
  (Y_tr=−a cosθ, Y_tθ=a r sinθ, Y_rφ=−a²cosθsin²θ, Y_θφ=r(r²+a²)sinθ) — verified it numerically rather than
  trust the convention: (A) KY equation residual ~1e-8; (B) Y_ac Y_b^c = §58 Carter K to ~1e-13.
- The full hidden-symmetry tower of Kerr now: Killing VECTOR ξ (E,L; linear) → Killing TENSOR K (Carter C;
  quadratic, §58) → Killing–YANO Y (K=Y·Y; the antisymmetric root). Y is also why Dirac/Maxwell/perturbation
  equations separate in Kerr. Gate: 56 green.

## 2026-06-19 — KERR SHADOW: the split light ring & asymmetric (D-shaped) shadow

- Second of the "few more strong ones". Spin breaks §45's circular shadow: frame dragging (§60) splits the
  equatorial light ring. Battery `68_kerr_shadow.py` (numeric, M=1; symbolic solve(R=R'=0) was too slow, so
  closed-form radii + solve R=0 for b at those radii). (A) radii 2M{1+cos[⅔arccos(∓a/M)]}: a=0→3M both,
  a>0→prograde<3M<retrograde, extremal→{M (horizon), 4M}. (B) shadow edges b=L/E: a=0 symmetric ±3√3M
  (=§45), a>0 |b_pro|<3√3<|b_ret| (a=0.9: +2.84/−6.83). Root selection: prograde = smallest positive root,
  retrograde = negative root (continuous with ±3√3 as a→0). (C) extremal a→M: b_pro→2M, b_ret→−7M (textbook,
  matched). (D) §45+§60 ⇒ the EHT asymmetric shadow. Gate: 55 green.

## 2026-06-19 — GRAVITATIONAL LENSING & EINSTEIN RINGS (user: "add a few more strong ones")

- User asked for a few more strong lenses after the §56–66 milestone. First: lensing — the OBSERVABLE
  consequence of bending (§49), what astronomers actually measure (dark-matter maps, microlensing).
  Battery `67_lensing.py` (standalone; metric input is α=4M/b from §49, plus thin-lens geometry).
- Lens eq β=θ−θ_E²/θ, θ_E²=4M D_LS/(D_L D_S). (A) β=0 ⇒ Einstein ring at θ_E; (B) off-axis ⇒ two images
  θ_±=(β±√(β²+4θ_E²))/2; (C) total magnification μ(u)=(u²+2)/(u√(u²+4)) — the microlensing curve, μ→∞ at
  u→0, μ→1 at u≫1 (checked numerically + limits; sympy won't reduce √(u⁴+8u²+16)=u²+4, same as §50); (D)
  θ_E∝√M, lensing weighs unseen mass. Gate: 54 green.

## 2026-06-19 — THE EFFECTIVE POTENTIAL: orbits as a particle in a well (synthesis)

- Synthesis lens unifying §45 (photon sphere/ISCO) + §50 (precession): radial geodesic motion is
  (dr/dτ)²=E²−V_eff, a particle rolling in V_eff(r), read off the metric. Battery `66_effective_potential.py`
  (standalone). (A) ISCO from V_eff′=V_eff″=0 ⇒ r=6M, L=2√3M (a stability statement: no stable orbit below
  6M). (B) photon sphere = null V_eff MAXIMUM ⇒ r=3M, hence unstable. (C) the WHY: V_eff=1−2M/r+L²/r²−2ML²/r³;
  the first three are Newton, the −2ML²/r³ is purely GR — drop it and there's NO ISCO solution (verified:
  Newtonian V has no V′=V″=0 root). That term is exactly why close orbits go unstable. (D) capture: null
  barrier peak V_max=4/9 (L=2√3M) sets the capture cross-section / shadow. Gate: 53 green.

## 2026-06-19 — RAYCHAUDHURI & FOCUSING: why singularities are inevitable

- The deepest "why" yet. A bundle of free-fallers has expansion θ obeying Raychaudhuri dθ/dτ=−θ²/3−σ²+ω²
  −R_ab u^a u^b; non-rotating ⇒ everything but the last term ≤0, and Einstein makes it 4π(ρ+3p). SEC
  (ρ+3p≥0) ⇒ forced convergence ⇒ caustics ⇒ Penrose–Hawking singularity theorems. Battery
  `65_raychaudhuri.py` (standalone). Fixed a symbol-scoping bug in the first draft (walrus `t` vs the
  helper's internal `t` — derivatives came out wrong); rewrote with one shared `T`.
- (A) Raychaudhuri verified as an identity for the FLRW comoving bundle: θ=3H, R_ab u^a u^b=−3ä/a, residual 0.
  (B) ordinary matter a∝t^{2/3} (SEC holds): R_ab u^a u^b=2/(3t²)>0 ⇒ θ→+∞ at t→0, Big Bang is a focusing
  singularity (ties §36 SEC + §37 cosmology). (C) the escape: de Sitter a=e^{Ht} violates SEC
  (R_ab u^a u^b=−3H²<0) ⇒ dθ/dτ=0, θ=3H const, no future singularity (dark energy / inflation beats the
  theorems; needs exotic matter cf §38). (D) focusing ⟺ SEC, and it's the same singularity the analyzer
  finds by curvature (§59/§42) — two views of one fact. Gate: 52 green.
- (Recovered from the 3rd power loss of the session mid-gate; §64 was already safe at 8e01cf7. Dashboard
  restarted again.)

## 2026-06-19 — THE COSMOLOGICAL HORIZON: the universe has a temperature (Gibbons–Hawking)

- Change of scenery into cosmology. A horizon needn't be a black hole's: de Sitter (the t→∞ fate of ΛCDM,
  §37) wraps every observer in a cosmological horizon at r_c=1/H that radiates (Gibbons–Hawking 1977).
  Battery `64_cosmological_horizon.py`.
- Found + fixed a genuine sign bug in the analyzer while doing it: `horizon_thermo` computed T=f′(r_h)/4π,
  which is NEGATIVE for a cosmological horizon (f′<0 there, vs f′>0 for a black hole). Physical temperature
  is |κ|/2π > 0. Changed to T=|f′|/4π — black holes unchanged (f′>0), de Sitter now correctly +H/2π.
  Regression-checked: 35/40/41 green before committing.
- Results: (A) analyzer reports r_c=1/H, T=H/2π, S=π/H² (validates the fix); (B) κ=H, T=H/2π Gibbons–Hawking;
  (C) S=A/4=π/H²; (D) de Sitter Λ-dominated (Λ=3H²) ⇒ T=√(Λ/3)/2π, S=3π/Λ — temperature & entropy from Λ;
  bigger Λ ⇒ smaller hotter horizon, less entropy. Core change (horizon_thermo) ⇒ full gate is the real
  regression check. Gate: 51 green.

## 2026-06-19 — PROPER DISTANCE & EMBEDDING: the Flamm funnel (a visual lens)

- A change of scenery from the curvature/symmetry/charge cluster: the geometric "how stretched is space"
  lens. Battery `63_embedding.py` (standalone, no analyzer change — it's geometry/visualization, not a
  report-card scalar). The coordinate r labels spheres by circumference 2πr, but proper distance ℓ=∫dr/√f
  is larger near a hole. (A) verified the embedding equation (dz/dr)²+1=g_rr is solved by the Flamm
  paraboloid z=√(8M(r−2M)) exactly (checked the residual =0, sidestepping sympy's r>2M branch issue by
  verifying dz/dr rather than integrating). (B) throat at r=2M: z=0, dz/dr→∞ — the funnel neck, maximal
  extension = Einstein–Rosen bridge (§38). (C) proper distance horizon→6M ≈7.19 vs coordinate 4 (stretched),
  finite to the horizon (1/√f integrable) — via mpmath.quad. (D) dz/dr→0 far away (flattens). Gate: 50 green.

## 2026-06-19 — KOMAR CHARGES: what mass and spin ARE (the symmetry-arc capstone)

- Conceptual capstone of §58 (Killing) → §61 (Smarr): mass and spin aren't inputs — they're the conserved
  CHARGES of the time-translation and rotation Killing symmetries. Added `komar_charges(geo)` to analyzer
  (mass=lim r(1+g_tt)/2, J=lim −r g_tφ/(2sin²θ); cheap asymptotic limits, n=4) + `komar` report-card field.
  Battery `62_komar.py`.
- (A) reads M off Schwarzschild/RN/Kerr, J=Ma off Kerr — mass↔∂_t, spin↔∂_φ. (B) the Komar mass WITHIN r,
  M(r)=½r²f′, exposes field energy: constant M for Schwarzschild (vacuum Gauss law) but M−Q²/r for RN (the EM
  field outside r carries the missing energy), → M at ∞. Mass is r-dependent exactly when fields carry
  energy. (C) the Smarr law M=2TS+2Ω_H J (§61) IS a Komar identity (mass at ∞ = horizon Komar integral).
  (D) so M, J, Q are Noether charges of time/rotation/gauge symmetry — a hole's hair is geometry, not input.
- Folded cheaply (asymptotic limits, no curvature); atlas unaffected. Gate: 49 green.

## 2026-06-19 — KERR THERMODYNAMICS: closing the rotating-horizon T/S thread (Smarr law)

- Closed a thread open since the first Kerr work: the analyzer gave a rotating horizon's LOCATION but T/S
  UNKNOWN (geometric surface gravity → nested radicals SymPy won't reduce). Key realization: don't compute
  κ geometrically — read the clean pieces off the metric. Δ = g_θθ/g_rr (= r²−2Mr+a²), r₊ at Δ=0, area
  A=∮√(g_θθg_φφ)|_{r₊}=8πMr₊, Ω_H=(−g_tφ/g_φφ)|_{r₊}, then T=κ/2π=Δ′(r₊)/A, S=A/4. Battery `61_kerr_thermo.py`.
- Verified exactly: (A) χ=∂_t+Ω_H∂_φ null at r₊ (Killing horizon); (B) Smarr M=2TS+2Ω_H J=M; (C) first law
  dM=TdS+Ω_H dJ (dM coeff 1, da coeff 0); (D) third law extremal a→M ⇒ T→0 but S→2πM² finite; (E) a→0
  recovers Schwarzschild T=1/8πM, S=4πM² (grounds it against §35's metric-derived value).
- HONESTY CALL: did NOT auto-fold T/S into the analyzer's general off-diagonal branch. T=Δ′/A relies on
  Kerr's specific structure (κ=Δ′/(2(r₊²+a²)) + A=4π(r₊²+a²)); folding it generally would risk WRONG
  temperatures for non-Kerr rotating metrics. So this is the Kerr-specific closure; analyzer's general
  rotating T/S stays honestly UNKNOWN. Purely additive battery, no analyzer change. Gate: 48 green.

## 2026-06-19 — FRAME DRAGGING & THE ERGOSPHERE: a spinning hole drags space

- Switched flavour from the curvature/symmetry cluster to Kerr's purely ROTATIONAL structure — exact,
  algebraic, no heavy curvature. Added `frame_dragging(geo)` to analyzer (ω=−g_tφ/g_φφ + ergosphere via
  g_tt=0, for stationary axisymmetric g_tφ≠0; UNKNOWN else — cheap, gated; atlas unchanged at 29s) + a
  `frame_dragging` report-card field. Battery `60_frame_dragging.py`.
- (A) ergosphere r=M+√(M²−a²cos²θ) wraps OUTSIDE the horizon (=2M equator, =r₊ poles); g_tt>0 inside ⇒ no
  static observers, must co-rotate. (B) ω rigid at horizon: ω(r₊)=Ω_H=a/(r₊²+a²) (the messy expression
  simplified to it). (C) far field ω·r³→2Ma ⇒ Lense–Thirring 2J/r³ (Gravity Probe B). (D) Penrose process:
  M_irr=√(A/16π)=√(Mr₊/2); extremal a=M ⇒ M_irr=M/√2 ⇒ 29.3% of mass extractable as spin energy. (E) a→0:
  ergosphere→horizon, ω→0 (purely rotational). Gate: 47 batteries green.

## 2026-06-19 — TIDAL FORCES: what you'd feel falling in (curvature made physical)

- Most physical/intuitive lens yet. The tidal tensor (geodesic deviation, the "electric" part of Riemann
  E_ij=R_{abcd}e_i^a u^b e_j^c u^d in the faller's orthonormal frame) — its eigenvalues are the tidal
  accelerations (negative=stretch, positive=squeeze). Added `tidal_tensor(geo)` to analyzer (static-observer
  tidal eigenvalues for the static spherical diagonal form; UNKNOWN else — reuses geo.riemann, gated like
  petrov so off-diagonal/cosmological cost nothing) and a `tidal` report-card field. Battery `59_tidal.py`.
- Schwarzschild eigenvalues = (−2M/r³, +M/r³, +M/r³) exactly — radial STRETCH, transverse SQUEEZE, trace 0:
  spaghettification, derived not asserted. Then the payoffs: (B) tides → ∞ at r→0 (REAL singularity) but
  FINITE −1/(4M²) at the horizon r=2M (COORDINATE singularity) — curvature settles the §42 question of which
  singularities are physical; (C) horizon tide ∝ 1/M² ⇒ 10⁹M⊙ hole 10¹⁶× gentler than 10M⊙ — supermassive
  horizons are survivable, stellar ones lethal; (D) radial tide = 2·Ψ2 (the type-D Weyl scalar, §57) — the
  tide IS the algebraic structure; (E) RN radial tide (−2Mr+3Q²)/r⁴, trace Q²/r⁴≠0 (EM matter). Fixed a
  trivial format bug (sympy Integer vs %e). Gate: 46 batteries green.

## 2026-06-19 — KILLING SYMMETRIES: the manifest algebra + Kerr's HIDDEN Carter constant

- The structure lens (#5) completed — the meatier of the three. Two layers: manifest Killing VECTORS and
  the hidden Killing TENSOR.
- Added `is_killing_vector` and `killing_vectors` to analyzer.py (reusable, symbolic). `killing_vectors` now
  finds the manifest cyclic KVs PLUS the **coordinate-mixing SO(3)** rotation generators (R_x, R_y, which
  mix θ,φ) when the metric is spherically symmetric — the gap `symmetries()` always flagged. Battery
  `58_killing.py`: Schwarzschild full algebra ℝ_t×SO(3) dim 4 (cyclic detector finds only 2); the rotations
  close [R_x,R_y]=−R_z (so(3), sign=orientation); a Minkowski Lorentz boost x∂_t+t∂_x verifies Killing too.
- **Headline — Kerr's hidden symmetry (Carter constant).** Some spacetimes have a symmetry no Killing
  VECTOR captures: a Killing TENSOR K_ab (∇_(aK_bc)=0), conserved quantity quadratic in momentum. Kerr's is
  the Carter constant, the thing that makes a spinning hole's orbits integrable (else chaotic). Verified
  NUMERICALLY (Kerr symbolic curvature swamps): built K=2Σl_(μn_ν)+r²g from the principal null directions
  (checked l·l=n·n=0, l·n=−1 first), then ∇_(aK_bc)=0 to ~3e-8 at random points; irreducible (not ∝g, ratio
  spread ~26). And the payoff: RK4-integrated an actual Kerr orbit and showed C=K_ab u^a u^b conserved to
  ~1e-12 alongside E, L, μ² — 4 constants ⇒ integrable.
- Debugging: first geodesic ICs plunged through the horizon (christoffel_numeric blows up as Δ→0) → all
  constants drifted 100%. Fixed with a near-circular orbit at r=10 (Ω=1/(r^1.5+a)) + a small θ-tilt so C is
  non-trivial; constants then flat to machine precision. so(3) bracket came out −R_z not +R_z — orientation
  convention, not a bug. Gate: 45 batteries green.

## 2026-06-19 — PETROV CLASSIFICATION: the algebraic type of a spacetime (new report-card lens)

- Second orthogonal lens (after ringdown), the one we'd flagged. The **Weyl tensor** (trace-free curvature,
  the pure-gravity tidal field) has an algebraic type — Petrov type — read off from its Newman–Penrose
  scalars Ψ0…Ψ4. Built it as a capability the GENERAL ANALYZER owns (`analyzer.weyl_tensor` / `weyl_scalars`
  / `petrov_type` / `weyl_invariants` / `petrov`), validated by battery `57_petrov.py` (same structure as
  observables↔§45). Prototyped the two anchors first: Schwarzschild Ψ2=−M/r³ (others 0) and a vacuum pp-wave
  Ψ4≠0 (others 0) — both came out clean on the first try.
- Results: **Schwarzschild → D** (Ψ2=−M/r³ exactly), **RN → D** (Ψ2=−M/r³+Q²/r⁴), **de Sitter & Minkowski →
  O** (Weyl≡0), **vacuum pp-wave → N** (only Ψ4) — a pure gravitational wave, which ties to §56 (ringdown
  radiation is type-N Weyl). Frame-independent speciality I³=27J² verified for D/O/N (I,J are Lorentz
  invariants even though the Ψ's aren't).
- Folded into the report card with a perf guard: `petrov(geo)` computes the heavy Weyl tensor ONLY for the
  static spherical diagonal form (−f,1/f,r²,r²sin²θ — canonical tetrad known); anything off-diagonal or
  cosmological early-returns UNKNOWN with NO Weyl computed. Measured: Kerr's petrov = None in 0.000s, atlas
  (41) still 28s (no slowdown), 40/45 green. Honest three-valued: the pp-wave's own type N is found via the
  exposed functions, but `analyzer.petrov(pp-wave)` returns UNKNOWN (off-diagonal ⇒ no auto tetrad) — stated,
  not faked. Gate: 44 batteries green.

## 2026-06-19 — RINGDOWN: black-hole perturbation theory, the exact pieces (and an honest edge)

- Back after a few days on the sister projects. User relayed a sharp critique of a floated "QNM module":
  (1) there is NO exact/closed-form Kerr QNM — they come from Leaver's continued fraction (numerical), and
  there's already a maintained `qnm` python package (Leo Stein, JOSS 2019) that does it; (2) the payoff
  (compare computed vs measured overtone) is just black-hole spectroscopy, which the sister project already
  runs. Both correct. Decision: DROP the bridge framing entirely, build only what improves OUR engine, and
  build the EXACT pieces that fit ansatz's identity — not a numerical Leaver clone.
- **Battery `56_ringdown.py` — the exact lens.** Web-checked the eikonal/photon-sphere correspondence
  (Cardoso) and the `qnm` package before building (both confirmed). Then:
  - **(A) exact wave potential, ANY metric.** Derived `V = f[ℓ(ℓ+1)/r² + f′/r]` from the separated scalar
    wave equation and VERIFIED it as a symbolic identity (`r·E_R − master = 0`, f a free Function) — true for
    every f, not just Schwarzschild. Spin-s family recovers the textbook Regge–Wheeler potentials.
  - **(B) exact eikonal QNM** from the photon sphere: `ω = ℓΩ_c − i(n+½)λ`. Schwarzschild `Ω_c = λ = 1/(3√3 M)`
    exactly; calibrated the ℓ=2,n=0 eikonal (0.385−0.096i) against the known Leaver value (0.374−0.089i) — a
    few % off, honest about the high-ℓ limit.
  - **(C) the unification** `ω_R = ℓ/b_shadow` (Ω_c·b_c=1): the LIGO ringdown and the EHT shadow are the same
    photon sphere. Folded `ringdown_omega_c`/`ringdown_lyapunov` into the general analyzer's report card
    (`observables()`), so every static black hole now reports its ringdown — regression-free (40/41/45 green).
  - **(D) honest boundary, stated in the battery:** overtones (finite ℓ, n≥1) need Leaver/the `qnm` package;
    ansatz gives the exact potential + eikonal limit, not the numerical spectrum. No diluted "exact" identity.
  - Fix while building: symbolic RN photon-sphere root `[3M±√(9M²−8Q²)]/2` has undecidable `is_real`, so the
    charge check evaluates numerically. Gate: 43 batteries green.

## 2026-06-17 (overnight, autonomous) — does the ONE general tool reach the star? (yes, with an honest edge)

- The night's stellar work (52–54) was focused scripts; checked it against the project's north star (the
  user's steer: ONE general analyzer, not a pile of narrow scripts). Pointed `analyze()` at a star (the
  constant-density interior, perfect-fluid ball) — with no stellar-specific code it reads the STRUCTURE
  right: perfect fluid (isotropic — it detects p_r=p_t), density ρ=3/(20π)=3M/4πR³ exactly, symmetries
  ∂/∂t & ∂/∂φ, no singularity, signature flip False (a STAR not a hole), sourced matter. Battery `55`.
- **Honest boundary, found + recorded (not hidden).** `physical?` came back UNKNOWN. Diagnosed precisely:
  the analyzer's `_sign` sampler draws the radial coord out to r=25, but the interior's √(1−2Mr²/R³) is
  real only for r≤R, so most samples are complex. The OLD `_sign` returned None the instant ANY sample
  was non-real — one out-of-domain point vetoed everything. **Fix:** skip non-real samples (don't bail),
  with a quorum guard (need ≥20 real samples to trust unanimity) so we never over-claim. Regression-free
  (full gate green both before and after). It's a genuine robustness gain, but it does NOT by itself
  certify the star — that needs the domain bound r≤R, which a bare metric doesn't carry. So 55 also
  verifies directly (sampling r<R) that NEC/WEC/DEC DO hold — the star is physical; the UNKNOWN is missing
  domain knowledge. Three-valued UNKNOWN done right.
- **Then SHIPPED the fix (same night).** Rather than leave it as a future note, implemented the domain-aware
  certification: `analyze(metric, coords, domain={r:(0,R)})` — an optional `domain` arg threaded through
  energy_conditions → _nonneg → _sign, which bounds where each coordinate is sampled. With it, the SAME
  general tool certifies the star PHYSICAL (NEC/WEC/DEC/SEC all True) instead of UNKNOWN. `domain=None`
  reproduces the original sampling byte-for-byte (the default rational draw runs first, bounded coords
  override after — so the rng sequence is untouched when no domain is given), and the full gate is green
  before AND after. Battery 55 upgraded to show both the boundary and its resolution. The general tool now
  handles interior solutions, not just global ones. Gate: 42 green, pushed.

## 2026-06-17 (overnight, autonomous) — MASS–RADIUS: the maximum neutron-star mass (capstone)

- Capstone of the stellar arc, and the bridge to why black holes form. Battery `54_mass_radius.py` feeds
  the engine's recovered TOV (52) a polytropic EoS (p=Kρ², Γ=2, K=100 geometric units) and integrates it
  numerically — pure-Python hand-rolled RK4, no numpy/scipy (consistent with numeric_curvature.py and the
  project ethos) — outward from the centre until p→0 (the surface R, enclosed mass M). Scanning central
  pressure traces the **mass–radius curve**, and it TURNS OVER:
        pc=1.9e-4 M=1.62 → pc=1.9e-3 M=1.995 (peak) → pc=2.0 M=1.43.
  The peak is the **Oppenheimer–Volkoff maximum mass** (M_max≈1.99 at R≈7.44; compactness 0.27 < Buchdahl
  4/9, consistent with 53). Past the peak, denser stars are LIGHTER ⇒ unstable ⇒ collapse to a black hole.
  So the engine's own TOV forbids arbitrarily heavy neutron stars — end-to-end: TOV → exact star → a maximum
  mass, the seed of stellar-mass black holes. Gate: 41 batteries green, pushed. Stellar arc closed.

## 2026-06-17 (overnight, autonomous) — the BUCHDAHL bound: a star's maximum compactness

- Grounded the abstract TOV (52) in a concrete exact star and recovered a famous theorem. Battery
  `53_buchdahl.py`: the constant-density interior Schwarzschild sphere — ρ=3M/(4πR³), m(r)=Mr³/R³, with
  the 1916 closed-form pressure p(r)=ρ[√(1−2Mr²/R³)−√(1−2M/R)]/[3√(1−2M/R)−√(1−2Mr²/R³)].
  - **(A)** the engine confirms this exact p(r) SATISFIES its own recovered TOV ODE — numeric spot-check
    at 5 radii (sympy won't prove the radical identity; same honest pattern as 50's precession check).
  - **(B)** surface p(R)=0 (symbolic).
  - **(C)** central pressure p_c=p(0) DIVERGES when 3√(1−2M/R)=1 → solved exactly → **M/R=4/9, the
    Buchdahl bound.** Past it, even infinite central pressure can't resist gravity — the star must collapse.
  - **(D)** numeric runaway: p_c/ρ = 0.17 → 1.62 → 16.7 → 166.7 as M/R climbs 0.2 → 0.4 → 0.44 → 0.444.
  Gate: 40 batteries green, pushed. The stellar arc (TOV + a concrete star + the compactness limit) closed.

## 2026-06-17 (overnight, autonomous) — STELLAR STRUCTURE: the engine builds a star (TOV)

- New domain, the cleanest remaining loose thread: the engine had only ever done black holes and
  cosmologies — never MATTER holding itself up. Battery `52_stellar_structure.py` takes the static
  interior metric ds²=−e^{2Φ(r)}dt²+dr²/(1−2m(r)/r)+r²dΩ² with **Φ(r), m(r) free** and recovers the
  equations of stellar structure (the abstractor move, cf. Friedmann 37 / Kasner 47):
  - **(A) mass function** dm/dr=4πr²ρ — read off G^t_t (m(r)=mass inside r).
  - **(B) potential eq** dΦ/dr=(m+4πr³p)/(r(r−2m)) — from G^r_r.
  - **(C) TOV.** First a genuine engine SELF-TEST: the covariant divergence ∇_μG^μ_r computes to
    identically 0 (the Bianchi identity — nice independent correctness check). The same divergence of an
    isotropic perfect-fluid stress (p_r=p_t=p) is p'(r)+(ρ+p)Φ'(r); set it to zero and substitute (B) →
    the **Tolman–Oppenheimer–Volkoff equation** dp/dr=−(ρ+p)(m+4πr³p)/(r(r−2m)). 1939, recovered.
  - **(D) Newtonian limit, DERIVED honestly** — first draft was dishonest (I hand-wrote the answer and
    "verified" it against itself; caught it, the honesty rules are load-bearing). Redid it as a real
    post-Newtonian ordering: tag m→λm (compactness O(v²)), p→λ²p (pressure O(v⁴)), read the λ¹ coefficient
    of the TOV RHS → −ρm/r² falls out, the three relativistic factors switching off. Ordinary hydrostatic
    equilibrium. Gate: 39 batteries green, pushed.
- Kept 8π explicit here (not the usual 8π=1) so the 4π/8π factors read as the textbook. Engine's first STAR.

## 2026-06-17 (overnight, autonomous) — the three classic tests, completed (precession + redshift)

- Rounded out the observables lens into the **three classic tests of GR**, each computed straight from
  the metric, joining light bending (49):
- **PERIHELION PRECESSION (`50_precession.py`) — Mercury's test.** The periastron advance per circular
  orbit, ALGEBRAIC via epicyclic frequencies (no integral): L²=f'r³/(2f−f'r), Δφ=2π(√(2L²/(r⁴V''))−1).
  For Schwarzschild this is exactly 2π(1/√(1−6M/r)−1) — checked NUMERICALLY (sympy won't prove the
  radical identity) at r=8,12,30. Verified: weak field → 6πM/r (Mercury's 43″/century), and it
  **diverges at r=6M, the ISCO** — precession and the accretion-disk inner edge are the same physics.
  Charge reduces it. Battery 50.
- **GRAVITATIONAL REDSHIFT (`51_redshift.py`) — Pound–Rebka, the third classic test.** z(r)=1/√f−1:
  weak field z≈M/r (the tower experiment, series-verified), z→∞ at the horizon (the surface fades to
  black, limit-verified), charge reduces it (f larger at fixed r). Trivial physics but completes the
  trilogy: the engine now reproduces light bending + perihelion precession + gravitational redshift,
  all from the metric alone. Battery 51. Gate: 38 batteries green, pushed.

## 2026-06-17 (overnight, autonomous) — closing loose threads: Kerr-dS numeric unlock + KASNER

- User to bed, full autonomy, "close the loose threads." Pushed authorization granted — committing AND
  pushing now (synced to origin/main).
- **Kerr–de Sitter, unblocked (`numeric_curvature.py` + battery 46).** The blocker was symbolic
  blow-up (OOM), not RAM — so the VM was the wrong tool. Built a finite-difference numeric Ricci (pure
  Python, ms/point): it VERIFIES Kerr–dS (vacuum+Λ, |R−Λg|≈2e-4) where symbolic OOMs, and its control
  shows Kerr's own Δ (no Λ term) gives a huge residual in a Λ-universe — i.e. the engine confirms a
  rotating hole in a Λ-universe REQUIRES the −Λr⁴/3 correction. The from-scratch GP discovery of the
  quartic Δ_r is hard (GP can't evolve r⁴ + slow numeric fitness) — attempted, stalled, removed the
  non-converging script, noted honestly (PLAN §4). The numeric engine is a general tool: unlocks ANY
  off-diagonal metric symbolic can't handle.
- **KASNER (`47_kasner.py`) — recovered the anisotropic-vacuum meta-law.** For ds²=−dt²+Σt^{2pᵢ}dxᵢ²,
  the engine factors the vacuum residual into the **Kasner conditions** Σpᵢ=1 AND Σpᵢ²=1 (R_tt·t²=Σp−Σp²;
  R_xx·t²∝p₁(Σp−1)), verified necessary + sufficient. The abstractor move (24) in a cosmological setting
  (the BKL building block). Closes ATTACK_ANGLES #4 (Kasner). Battery 47.
- **KERR'S RING SINGULARITY (`48_ring_singularity.py`) — closed via the numeric engine.** Added
  `kretschmann_numeric` to numeric_curvature.py (finite-difference K = R_abcd R^abcd). It validates vs
  exact Schwarzschild K=48M²/r⁶ (rel err 1e-8), then reveals Kerr's RING: K diverges as r→0 ON the
  equator (u=0, Σ=0; ×244 from r=0.05→0.02) but stays BOUNDED off it (×2.6) — the famous ring structure
  the symbolic Kretschmann (and the analyzer) had to mark UNKNOWN. Off-diagonal singularities, closed.
  Battery 48.
- **LIGHT BENDING (`49_light_bending.py`) — the 1919 Eddington test, closed.** Δφ=2∫dr/(r²√(1/b²−f/r²))−π
  integrated numerically (mpmath handles the turning-point √). Validated: weak field → 4M/b (ratio 1.006
  at r₀=500M — Einstein's value, twice Newton); strong field grows (3.09× at r₀=4M); near the photon
  sphere (r₀=3.5M) Δφ=3.2 rad (light nearly wraps); charge reduces it. Completes the observables lens
  (light ring, shadow, ISCO, deflection). Battery 49.

## 2026-06-17 (overnight, autonomous) — DISCOVERY RANGE: invents de Sitter + an exotic hole too

- Strengthened the headline ("invents to spec") by showing the discovery loop's RANGE — it's not a
  black-hole one-trick. Added two fitness components to 43: **"lambda"** (cosmological constant: reward
  p_t=−ρ i.e. T∝δ, ρ constant & nonzero) and **"exotic"** (reward an energy condition violated). Two new
  stages:
  - Stage 3 {lambda, horizon} → a **cosmological-constant universe** (found f=1+11/6r−r², classified Λ;
    it picked up a spurious mass term → Schwarzschild–de Sitter, whose horizon is a cubic the analyzer
    caps to UNKNOWN — fine, the MATTER is Λ, which is the defining feature, so the check is on made_of=Λ).
  - Stage 4 {exotic, horizon, asymptotic} → an **exotic black hole** (found f=1−11/(12r²): ρ<0, all
    energy conditions violated, physical=False, clean horizon at r=√Q²).
- So from a one-line spec each, the engine now invents: Schwarzschild, a survivable charged hole,
  de Sitter, AND an exotic hole — across vacuum / charged / Λ / exotic matter. Battery 43 now 4 stages.

## 2026-06-17 (overnight, autonomous) — Kerr–dS parked + OBSERVABLES lens (the EHT shadow)

- User went to bed, full autonomy. First tried **Kerr–de Sitter** rotating discovery: the insight held
  (with Δ_θ, Ξ fixed by Λ it's a single-Δ_r search; built the Carter-form ansatz, reduces to Kerr at
  Λ=0), but the reduce-once Ricci is far too heavy (OOM/>180s even alone, vs Kerr's 7s) — symbolic
  reduce-once infeasible; needs a numeric-curvature evaluator. PARKED honestly (docs/PLAN.md §4).
- Pivoted to a fresh angle (ATTACK_ANGLES #2): **`45_observables.py` — what a telescope SEES.** From the
  static lapse f: the PHOTON SPHERE (light ring) at 2f=rf', and the SHADOW (the Event Horizon Telescope
  silhouette) at b_c=r_ph/√f(r_ph). Schwarzschild gives the textbook icons EXACTLY — r_ph=3M, shadow
  b_c=3√3 M ≈ 5.196M; Reissner–Nordström: charge tightens both (r_ph=2.823M, shadow 4.968M at Q=M/2 < the
  Schwarzschild values). Turns "here's a metric" into "here's what you'd measure". Battery 45 added.

## 2026-06-17 (cont.) — ROTATING DISCOVERY: rediscovers KERR from spec (and skips the VM)

- User wanted rotating discovery as a deep VM run. I argued it could be FAST with the right design,
  and it was. The naive approach (GP over arbitrary off-diagonal metrics, ~6s full-analyze each) would
  crawl. The smart design: FIX the rational Kerr STRUCTURE (Σ=r²+a²u², the off-diagonal frame proven
  tractable in #1) and search just the one radial function Δ(r); REDUCE the vacuum residual ONCE (7s,
  feasibility-tested: real Kerr Δ=r²−2Mr+a² → Ricci≡0, residual depends only on Δ,Δ',Δ'') to cheap
  numeric formulas, then score candidates in ms — a single-function search like the static loop.
- **Result (`44_discover_rotating.py`): rediscovered KERR** — target {vacuum, horizon} →
  Δ(r) = r²−2r+1/4 (= r²−2Mr+a², M=1, a=1/2), in ~22s LOCALLY (--quick). The analyzer confirms the
  discovered metric is a genuine spinning black hole: vacuum, ∂/∂t & ∂/∂φ (2 Killing vectors), both
  horizons 1±√3/2 = M±√(M²−a²), Ricci-flat, signature flip True.
- **The honest punchline: the deep VM run was unnecessary.** The reduce-once trick (same lesson as the
  static loop) made rotating discovery fast on the Mac — no VM, no waiting on the local training.
  Battery 44 (--quick).
- **Kerr–Newman extension added same session:** the Kerr-Δ ansatz + the Kerr–Newman EM field, the
  Einstein–Maxwell residual reduced once (feasibility-verified ≡0 at Δ_KN=r²−2Mr+a²+Q²); target
  "charged" (Q=1/2) → discovered Δ=r²−8r/3+1/2 (const 1/2 = a²+Q²). The engine added Q² to Δ's constant
  — the rotating analogue of the static RN discovery. GP lesson surfaced live: the constant-mutation
  explores SMALL denominators, so a²+Q²=5/16 (Q=1/4) wouldn't converge but 1/2 (Q=1/2) does — pick the
  charge so the target constant is low-denominator. Kerr–de Sitter is a bigger build (2-function ansatz:
  Λ modifies the angular Δ_θ + Ξ factor, not just radial Δ) — noted, not done.

## 2026-06-17 (cont.) — PLAN #3: the engine INVENTS to spec (and rediscovers the charge)

- The culmination, and it closes the circle. `43_discover.py` reuses 03's genetic loop over rational
  f(r), but the fitness is now "how well does the candidate's REPORT CARD match a TARGET spec" — the
  analyzer becomes the judge. Fitness is LIGHT: ρ and p_t reduce to closed formulas in (f,f',f'')
  (ρ=(1−f−rf')/r², p_r=−ρ, p_t=(rf''+2f')/2r in 8π=1 units), evaluated numerically per candidate
  (ms); only the requested boxes are scored; the full report runs once on the winner. Runs locally in
  minutes (no VM needed yet).
- **Stage 1** {vacuum, horizon, asymptotic} → rediscovered **Schwarzschild** f = 1 − 1/(4r) (vacuum,
  spacelike singularity, one horizon).
- **Stage 2** {asymptotic, physical, horizon, TIMELIKE singularity} → the payoff: the engine invented
  **f = 1 − 5/(6r) + 1/(6r²)** — Reissner–Nordström FORM. It **discovered the charge term +1/(6r²)** on
  its own, and the analyzer independently classified the matter as traceless EM-like, physical, with
  TWO horizons and a TIMELIKE (avoidable) singularity. From a physical WISH ("a black hole you can
  survive falling into") the engine rediscovered that survivability requires electric charge. This
  unites #1 (analyze) + #2 (causal structure) + #3 (discover) in one result.
- Honest subtlety shown live: loose specs match many metrics → adding "asymptotically flat" steered
  Stage 2 from a weird f=1/r−7/2 to the recognizable RN family. Also fixed signature_flip to scan the
  radial coordinate densely (a narrow flip band between RN's two close horizons was missed by random
  sampling). Battery 43 (--quick) added. ALL THREE PLAN ITEMS DONE.

## 2026-06-17 (cont.) — PLAN #2: the causal-structure lens (the charge flips the singularity)

- Added `causal_structure` + `signature_flip` to the analyzer (the report card gained a `causal` row)
  and battery `42_causal_structure.py`. The mind-bending black-hole-interior structure, made exact:
  - **Singularity character** — spacelike ('a moment, the end of time', unavoidable) vs timelike
    ('a place', avoidable), from the sign of g^{kk} along the singular direction (g^{kk}<0 ⇒ timelike
    normal ⇒ spacelike surface). **Schwarzschild r=0 → spacelike; adding CHARGE flips RN's r=0 →
    timelike** — the exact calibration the sister NN project's context described. FLRW Big Bang (t=0)
    → spacelike. All exact, reusing the singularity scan.
  - **Signature flip** — does ∂_t go spacelike inside a horizon (t↔r swap)? Detected by g_tt changing
    sign over the domain. True for Schwarzschild/RN, False for FLRW/wormhole/Minkowski. (Bug found+fixed
    in prototype: sampled only coords, leaving the parameter M symbolic → fixed to sample all free symbols.)
- Battery 42 PASSES; battery 40 unregressed (the additions are robust/wrapped). Honest scope: this is
  the EXACT ground-truth oracle for what the sister NN net claims to have learned (signature flip,
  charge→timelike) — projects kept separate, link is hand-level only. #2 done; #3 (make-it-discover) next.

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
- **#1 COMPLETED same session.** Added **Gödel** (rotating universe with closed timelike curves)
  — analyzes in 0.1s: the analyzer reads its total effective stress-energy as a **stiff perfect fluid
  p=ρ** (correct — the dust + negative-Λ combine to isotropic pressure), physical, 3 Killing vectors.
  Works because Gödel is homogeneous (constant curvature). So both famous off-diagonal spacetimes —
  Kerr and Gödel — now land; both added to the atlas (now 12 rows).
- **The rest of #1 are GENUINE symbolic limits, handled honestly (not failures):** (a) Alcubierre
  warp — full analyzer path intractable (√ branch cut + arbitrary shape fn), but already proven exotic
  in battery 38; (b) rotating-horizon T,S — I derived a correct general surface-gravity formula
  (κ²=¼g^{rr}(∂_rχ)²/χ, validated: Schwarzschild κ=1/4M, Kerr numerically exact 0.2320508…) but the
  explicit horizon radical M+√(M²−a²) makes it symbolically irreducible (radsimp/simplify blow up) —
  needs r_h-parametrization the analyzer can't auto-generate, so report location + UNKNOWN T,S;
  (c) ring singularity — off-diagonal Kretschmann swamps. All three are honest three-valued UNKNOWNs
  with documented reasons. **Lesson: off-diagonal is tractable when rational (Kerr via u=cosθ) or
  homogeneous (Gödel); transcendental shape fns + branch cuts are the wall.** #1 done; ready for #2.

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

## 2026-06-24 (evening) — campaign extension: frame-dragging/QPOs, lensing, tidal (user-requested)
- §94 = RELATIVISTIC PRECESSION & QPOs (frame-dragging you can time): a circular orbit has 3 frequencies
  (orbital ν_φ, radial epicyclic ν_r, vertical ν_θ). (A) ν_r→0 at the ISCO — cross-checks the ISCO via an
  independent frequency. (B) periastron precession ν_φ−ν_r nonzero even at a=0 (strong-field Mercury). (C) nodal
  Lense–Thirring precession ν_φ−ν_θ EXACTLY 0 for Schwarzschild, ∝ spin (pure gravitomagnetism). (D) 10 M⊙ hole:
  ISCO ≈221 Hz (kHz-QPO band), nodal ~Hz (low-freq QPO). Closed-form Kerr (Stella–Vietri), cross-checked vs our
  numeric ISCO. The QPO relativistic-precession model, computed.
- §95 = STRONG-FIELD LENSING (Eddington 1919 -> relativistic images): the deflection integral
  α=2∫b dr/(r²√(1−b²f/r²))−π (turning point regularized by w=1−t²). (A) weak: α→4M/b (ratio→1 from above; a
  numerical caveat at huge b — tiny difference of large numbers — so validated at moderate b). (B) strong:
  α diverges as −ā ln(b/b_c−1), fitted ā=0.998 (Schwarzschild ā=1), photon loops >1 → relativistic images at
  the shadow edge. (C) THE UNIFICATION: ā=Ω_c/λ (the photon-ring Lyapunov), and ā·γ=π — so lensing, the subrings
  (§89), and the ringdown (§88) all encode ONE λ. ā(lensing)=0.998≈Ω_c/λ=1.000, ā·γ=3.135=π. Stress-test caught
  the (A) large-b numerical artifact (b=1000 dipped 1.8% below 4M/b); fixed to moderate b + honest caveat.
- §96 = TIDAL FORCES (the 3rd of the user's requests): tidal tensor E_ij=R_{0i0j} from the engine's curvature.
  (A) Schwarzschild E_rr=−2M/r³ (radial stretch), E_θθ=+M/r³ (squeeze), traceless — spaghettification, exact.
  (B) horizon tidal ∝1/M²: 10 M⊙ → ~10⁷ g (lethal), Sgr A* → ~10⁻⁴ g (gentle, you'd cross unharmed). (C) tidal
  disruption vs horizon: a Sun shredded outside the horizon (visible TDE) only for M < Hills mass ≈1.1e8 M⊙ —
  Sgr A* shreds, M87* swallows whole. (D) GW no-hair signature: BH tidal Love number k₂=0 (doesn't deform); NS
  k₂≠0 (GW170817 distinguishes them). All three user-requested topics done: §94 frame-dragging/QPOs, §95
  lensing, §96 tidal. Observational campaign now §86–§96 (11 batteries).

## 2026-06-25 — BREAKING THE WALL: Zipoy-Voorhees exact-vacuum integrability (§97)
- THE WALL = SymPy curvature of (r,θ)/(x,y)-dependent metrics swamps (EdGB O(a) 2.3h; symbolic Killing search
  7.5h; linearized quadrupole 2.5h). Broke it by going NUMERICAL — twice.
- FIRST ATTEMPT (Weyl numerics, scripts/_weyl_quadrupole.py): a quadrupole-deformed vacuum BH via the Weyl line
  integral — ψ=ψ_S+q·ψ_Q (decaying l=2 harmonic), γ₁ from the cross-term quadrature, precomputed on an (R,Θ)
  grid by radial sweeps (0.6s vs 14 MIN for the raw per-point line integral). STRESS-TEST CAUGHT a subtlety: the
  finite-difference Ricci residual scaled LINEARLY in q, not q². Resisted the easy "physics bug" read — checked
  the ANALYTIC vacuum conditions directly: ψ_S,ψ_Q harmonic to 1e-10, and γ₁ integrability ∂_z g1r=∂_ρ g1z to
  1e-7. Both clean ⇒ the metric IS vacuum-to-O(q) by construction; the linear residual is the bilinear-interp C0
  noise in the 2nd derivatives, NOT physics. Construction sound, but interpolation too rough for clean curvature.
- PIVOT to the EXACT closed form: the ZIPOY-VOORHEES (γ-) metric (scripts/zipoy_voorhees.py) — Schwarzschild with
  a tunable quadrupole δ, EXACT vacuum for ALL δ (δ=1=Schwarzschild), no interpolation. Vacuum residual ~1e-6
  FLAT in δ (non-perturbative), vs the Weyl metric's residual growing with q. The right object.
- FED IT TO §85's DETECTOR (scripts/_zv_invariant.py; basis u→y, om→1−y², r→x; mass fixed M=1 via σ=1/δ):
  (C) δ=1 recovers the Carter constant EXACTLY — SV 5.84e-15, gap 4.8e11, recovered C=(1−y²)p_y²+16.00/(1−y²)
  vs Carter L²=16 (match <1%). (D) δ≠1 → smallest SV jumps to 1e-6..1e-5 and GROWS monotonically with |δ−1|
  (sweep: 0.8→5.7e-6, 0.9→5.5e-6, 1.0→6e-15, 1.1→7.3e-6, 1.2→1.6e-5, 1.3→2.0e-5, 1.4→4.1e-5, 1.5→4.2e-4).
  No conserved quadratic ⇒ non-integrable. This UPGRADES §85 off its phenomenological non-vacuum Kerr-bump onto
  a GENUINE exact vacuum solution — answering "is that deformation a real spacetime?" with one that is.
- PRIOR ART web-checked FIRST (the lesson, applied): ZV non-integrability + absent Carter constant are KNOWN
  (Lukes-Gerakopoulos, PRD 86 044013 (2012), arXiv:1206.0660; δ=2 has chaotic orbits). Cited, NOT claimed — the
  contribution is the VALIDATED general detector (no closed-form Killing tensor / separability needed; works
  where the symbolic route swamps).
- CHAOS hunt (scripts/_zv_chaos_hunt.py): δ=1 regular tori (box-dim ~0.9), δ=2 bound orbits only MILDLY elevated
  (~1.1), 0 strongly-chaotic found — the strong δ=2 chaos the literature locates lives in strong-field resonant
  islands our coarse p_x=0 turning-point scan didn't hit (those orbits plunge). Honest caveat in the battery: the
  SHARP signal is the algebraic absent-conserved-quadratic, not the geometric chaos. Also hardened
  poincare.section() with a bounds-box + overflow guard (backwards-compatible; §84 re-verified green).
- ADVERSARIAL STRESS-TEST (user: "did we really break the wall, or just saw what we wanted?") —
  scripts/_zv_stresstest.py, 5 tests, ALL PASS: (1) δ=1 control genuinely Schwarzschild — the TEXTBOOK Carter
  (1−y²)p_y²+L²/(1−y²), NOT fitted, conserved along orbits to 6.6e-16; (2) THE DECISIVE ONE — δ≠1's 1e-5 is a
  REAL non-invariant: stays pinned (even RISES: 16→1.95e-5, 24/32→9.5e-5) under more orbits AND a halved step
  (h=0.01→1.95e-5), never collapsing toward the 1e-15 floor (if an invariant existed, more data would find it);
  (3) basis not rigged — +5 higher-order terms keep δ=1's Carter (6e-15) and create no spurious δ≠1 invariant
  (2.4e-5); (4) generalizes out-of-sample — δ=1 invariant holds on a HELD-OUT orbit (2.9e-14), δ≠1's best-fit
  drifts (1.4e-4); (5) robust across (E,L,x0). So the no-Carter contrast is PHYSICS, not seeing-what-we-wanted.
- TWO HONESTY FIXES the stress-test surfaced (applied to battery + RESULTS + verify.sh): (i) softened "no quadratic
  ⇒ non-integrable" — the detector only rules out a QUADRATIC Carter in its basis; a higher-order Killing tensor
  isn't excluded; ZV's full non-integrability is the LITERATURE's proof (Morales-Ramis), which our result is
  consistent with, not a re-derivation of. (ii) made "breaking the wall" precise: we did NOT make SymPy tractable
  — we went AROUND it (exact closed form + numeric curvature), and only for the STATIC case; the rotating O(a²)
  PDE is still open.
- §97 battery green; wired into verify.sh. Tools kept general (a detector + an exact-solution testbed), not narrow.
- §98 = NO QUARTIC KILLING TENSOR EITHER (closing §97's caveat; user picked this of the two "bigger prizes").
  Pushed the conserved-quantity search from quadratic (rank-2) to QUARTIC (rank-4). _zv_quartic.py: 42-term basis
  (momentum monomials deg<=4 x simple spatial coeffs), AUTO-PRUNED to independence (the first hand-built basis was
  DEGENERATE — caught by the independence check: hidden identity 1/om^2 - y^2/om^2 - y^2/om = 1; auto-prune drops
  the most-dependent column until full rank). Built to span K^2 (Schwarzschild Carter squared) so delta=1 must
  show EXACTLY 2 float-floor nulls. RESULT: delta=1 -> 2 invariants (7.5e-15, 2.5e-14 = K and K^2, gap 4e4 to the
  next); delta!=1 -> 0 (smallest ~1e-10..1e-9). THE RIGOR (two stress-tests on the way): (1) h-convergence — the
  deformed near-null at 1e-12 did NOT track integration step (not integration error); (2) FLOOD test — it LIFTED
  87x (1.1e-12 -> 1.0e-10) when orbits went 22 -> 76, proving it was the §85 DIMENSIONAL near-null (too few orbits
  for a 42-term basis), NOT a real invariant; delta=1's two real invariants stayed pinned under both. So: deformed
  ZV has no rank-2 (§97) AND no rank-4 (§98) Killing tensor; detector recovers BOTH Schwarzschild invariants as
  control. HONEST scope: rank>=6 not excluded; ZV all-orders non-integrability is the literature's Morales-Ramis
  proof. Battery §98 green, wired into verify.sh.
- CHAOS hunt #2 (literature params E=0.95 Lz=3, fine scan) ran 36 min, found NOTHING elevated -> the delta=2 chaos
  is genuinely razor-thin (chaotic rho=7.518 vs regular 7.548, dr=0.03) and elusive to a 1D p_x=0 scan; killed it.
  The geometric chaos stays a cited-literature caveat; our sharp signal is the ALGEBRAIC absent-Killing-tensor
  (§97 quadratic + §98 quartic). Honest: we did not reproduce the thin chaos ourselves.
- §99 = THE ROTATING WALL CROSSED: Manko-Novikov (user: "start the MN build now, we're just getting started").
  The rotating analog of §97/§98, on an EXACT ROTATING vacuum solution -- crossing item-3's long-standing wall.
  PATH (revised from EdGB, much cleaner): instead of transcribing modified-gravity O(a^2) field equations, used
  the Manko-Novikov "bumpy Kerr" -- an EXACT stationary-axisymmetric VACUUM solution with a tunable quadrupole
  anomaly q (q=0 = Kerr). Same ZV playbook (exact vacuum -> verify Ricci=0, no field equations). BUILD was
  verification-driven: (1) built exact Kerr in prolate-spheroidal coords by transforming Boyer-Lindquist (reliable
  ground truth); (2) the MN form at q=0 (a=-alpha, b=alpha) matched it to 1.2e-15 -> baseline anchored; (3) added
  the q-deformation (a,b multipole-exponential factors + gamma' corrections, transcribed from Gair et al 2008 via
  web -- I distrusted the fetched '-1/+1/-2' constants as garbling); (4) VINDICATED by the vacuum check: the
  deformed FD-Ricci scales h^2 (1.7e-5->4.4e-6 as h 1e-3->5e-4, ratio 3.94), NOT a plateau -> exactly vacuum ->
  transcription CORRECT. So the metric is a genuine exact rotating bumpy-Kerr. manko_novikov.py (metric, with the
  Kerr ground-truth + vacuum check). INTEGRABILITY: built the reduced 2-DOF Hamiltonian NUMERICALLY (finite-diff,
  _mn_invariant.py -- the metric's exp(Legendre) would swamp SymPy), exposing poincare.build_hamilton's dict
  interface so §97's detector (_zv_invariant.fit/basis) runs unchanged. RESULT: q=0 recovers Kerr's Carter (SV
  7.5e-11, gap 1.2e8 -- floor ~1e-10 not 1e-14 because the Hamiltonian is finite-differenced); q!=0 has NO
  conserved quadratic (SV ~3e-2, 1e8x the floor, no gap). STRESS-TESTED: H conserved (q=0 4e-11, q=0.2 1e-4);
  contrast robust across 3 (E,L) families; q=0 invariant holds OUT-OF-SAMPLE on a held-out orbit (3e-10) while
  q!=0 has nothing. PRIOR ART cited not claimed: MN non-integrability known (Gair/Li/Mandel 2008 arXiv:0708.0628).
  HONEST: rules out a QUADRATIC Carter (rank-2); numeric Hamiltonian noisier for deformed metric (H-drift 1e-4,
  still 300x below the q!=0 signal). Battery §99 green, wired into verify.sh. New files: manko_novikov.py (metric),
  _mn_invariant.py (numeric Hamiltonian + detector), _mn_chaos_hunt.py (exploratory chaos), 99_*.py (battery).
- §100 = EMRI RADIATION REACTION (the bridge's request B1; user: "lets build it so the other session isn't blocked").
  The bridge (sister project) needs a GW-flux/radiation-reaction model to inspiral orbits through resonances in
  Kerr + the bumpy metric. Built emri.py (general over any metric via _mn_invariant.build_hamilton_numeric):
  (1) fundamental_frequencies — radial nu_r, polar nu_theta by counting x/y oscillation periods (launch at the
  radial turning point px=0, py on-shell); ratio sweeps 0.65->0.73 -> inspiral crosses resonances. (2)
  quadrupole_flux — numerical-kludge mass-quadrupole GW flux dE/dtau,dL/dtau in the frequency domain. VALIDATED vs
  Peters -(32/5)M^3/r^5 for a circular orbit (ratio 0.92@r=40 -> 0.97@r=70 -> 1 weak field; dL/dt=dE/dt/Omega_phi
  to 1%). TWO REAL BUGS caught + fixed (the w^6 weighting is brutal): (i) interpolation noise amplified by (iw)^3
  -> flux 1e16 too big -> fixed with a physical frequency cutoff; (ii) spectral LEAKAGE from non-integer periods
  (the cutoff-edge leakage * w^6 dominated) -> flux 1e2 too big at large r -> fixed with a Hann window. The Peters
  convergence is the proof. (3) works on the BUMPY metric (q!=0, both fluxes <0 -> inspiral). (4) drives a circular
  inspiral: dr/dt<0, Omega_phi rises 0.024->0.053 (the relativistic chirp). VERIFICATION-DRIVEN throughout: the
  earlier '90x too big' was traced to non-circular test orbits (Newtonian E,L != exact BPT circular); used exact
  Kerr BPT E,L for the clean validation. HONEST: it's a KLUDGE (leading multipole, ~10-20% low strong-field); the
  bumpy RESONANT CHAOS is cited (Gair/Li/Mandel 2008 arXiv:0708.0628) not reproduced (elusive to coarse probing,
  like §97 ZV -- Kerr & MN both box-dim~1 at coarse strong-field orbits). Per §99 the bumpy resonances ARE where
  integrability fails -> the resonance-crossing signature B1 wants. Deliverable for the bridge: emri.quadrupole_flux
  + fundamental_frequencies. Battery §100 green. New files: emri.py (toolkit), 100_emri_resonance.py (battery).
- §101 = EMRI CARTER FLUX + CHAOS-DETECTOR FIX (the bridge CLOSED B1 with §100, sent back 2 asks + 1 bug report).
  Bridge closed B1: self-consistent quasi-circular MN inspiral through the w_r:w_theta resonance sequence, bump
  lowers orbital freq -5%->-13% per crossing. Follow-ups: ASK A (dQ/dtau Carter flux) -- extended
  emri.quadrupole_flux(carter=True) to also return dQ/dtau, from the SAME quadrupole (full angular-momentum-flux
  vector dL_i + leading Carter Q=L^2-L_z^2=L_x^2+L_y^2 -> dQ=2(Lx dLx+Ly dLy)). Validated: equatorial dQ~0 (Q=0,
  to 1e-18, by construction Lx=Ly=0) + inclined dQ<0 (de-inclines). Honest kludge (omits a^2(1-E^2)cos^2; bumpy Q
  approximate). §100 backwards-compat (carter=False default -> pair). HEADS-UP (a REAL bug in our shipped code):
  geodesic_chaos.lyapunov false-positives chaos on bumpy metrics -- REPRODUCED EXACTLY: MN q=0.5 REGULAR orbit
  (box-dim 1.12) gives lambda=0.321 at the bridge's settings (Christoffel ch=1e-6, d0=1e-8); it's a 2D corner
  artifact (needs BOTH small ch AND small d0; collapses if either grows). FIX: de-noised geodesic_chaos defaults
  ch=1e-4, d0=1e-6 (threaded ch through _rhs/_rk4/trajectory/lyapunov) -> lambda=0.001. Verified §79/§82/§89/§95
  all still pass with the new defaults. THE ROBUST DETECTOR: box_dimension (geometric, roundoff-immune) is the
  verdict to trust; both detectors validated on genuine chaos elsewhere (box-dim Henon-Heiles §84=1.34, lyapunov
  di-hole §79=2.09). ASK B (bound MN orbit box-dim->2): NOT found by systematic low-L scanning (_mn_chaos_hunt3.py,
  q up to 1.2, max box-dim 1.16-1.22 REGULAR -- box-dim DROPS with more crossings = under-resolution; a borderline
  orbit gave real-but-tiny d0-independent lambda=0.05 where box-dim converged regular = the exact disagreement that
  makes box-dim the verdict). MN clean chaos elusive like §97 ZV; needs literature initial data (Lukes-Gerakopoulos
  2010). Delivered emri.mn_bound_orbit (the launcher). Battery §101 green. New: 101_emri_carter_and_chaos.py,
  _mn_chaos_hunt3.py (exploratory); modified emri.py (carter + launcher), geodesic_chaos.py (de-noised).
- §101 REFINED (bridge's 2nd round: §101 landed, B1 evolves (E,L,Q) on Kerr, but the dQ kludge degraded on the
  strong bump). Concrete failing case (MN q=0.2, E=0.95, L=2.6, x0=8.0) had TWO bugs, both reproduced + fixed:
  (i) dE INFLATED 250x (-1.6e-2 vs Kerr -6.7e-5). Diagnosed via the SPECTRUM: the orbit sits at nu_r:nu_theta~2:3
  resonance; its GW power peaks at 6.6*Omega_phi (a high harmonic, 100x the fundamental) which the w^6 weighting
  amplifies. Verified it's a non-convergent spurious tail (dE GROWS with the freq cutoff: -9e-5@3Om -> -1.6e-2@40Om,
  while Kerr PLATEAUS). Not the integrator (h-independent, RK4-phase-independent) -- the near-resonant trajectory
  itself. FIX: CONVERGENCE-PLATEAU cutoff (stop where cumulative dE plateaus, <8% growth) -> keeps real eccentric
  harmonics, rejects the spurious tail. MN -> -9.0e-5 (physical, ~Kerr); Kerr unchanged; §100 Peters 0.81-0.95
  preserved. (ii) dQ>0 UNPHYSICAL (de-inclining orbit must give dQ<0). Root cause: the Newtonian-Carter formula
  2(Lx dLx+Ly dLy) with L=<XxV> -> the precessing orbital-plane averages Lx,Ly to ~0, so dQ->0 with a spurious
  sign (the bridge's 'L-vector noise-prone' instinct, deeper). FIX: RADIATION-REACTION (Burke-Thorne) force
  a^i=-(2/5)(d5 I_ij/dt5)X^j (5th deriv spectral, cut), Q=Lx^2+Ly^2, dQ=<2(Lx tau_x+Ly tau_y)>, tau=Xxa_RR --
  captures the precession correlation. Now dQ=0 equatorial, <0 inclined, MONOTONE with inclination on Kerr AND bump
  (Kerr L=3.4->2.6: dQ -2.4e-4->-3.45e-3; MN: -1.1e-3->-9.0e-3). §100/§101 still pass; §101(A) augmented with the
  MN strong-bump case as a regression guard. KEY: the bridge gave a CONCRETE failing case -> reproduce + spectrum-
  diagnose + fix both, exactly the two-way loop working. Honest: still a leading-multipole kludge (no a^2(1-E^2)cos^2).

## 2026-06-26 — §102 THE MANKO-NOVIKOV CHART BUG + FIX (asymptotic-flatness gauge-fix; bridge Ask 2 enabler)
- Bridge GREEN-LIT the rod-stable MN reimplementation for the literature's chi=0.9, q=0.95 chaotic orbit, with one
  firm constraint: keep the outer region numerically identical so existing results are untouched. Attempting it
  REVEALED A REAL BUG instead: our shipped MN metric is NOT asymptotically flat for ANY q!=0 -- g_xx -> 0.085x the
  Minkowski value at infinity (g_tt, g_tphi, g_phiphi all correctly ->1). Direct test: g_xx(q=0.2)/g_xx(q=0) at
  large x = 0.0851, not 1.
- WHY BOTH OUR CHECKS WERE BLIND: the vacuum residual is insensitive to a CONSTANT in gamma (Ricci=0 is preserved
  under gamma->gamma+c, since gamma enters only via derivatives), and the q=0=Kerr anchor has beta=0 so the bad
  constant vanishes there. So a wrong gamma'-constant passed vacuum AND passed q=0=Kerr -- the metric was vacuum
  but on a non-standard chart. It is ALSO why it overflowed at high q: the spurious constant is ~ -6*beta, driving
  e^{2 gamma} -> 0 (g_xx underflow) everywhere as beta grows -- NOT a near-rod-only problem (it failed even at x=2).
- THE FIX (gauge normalization, in LOG space): subtract gamma's value at infinity so e^{2 gamma} -> 1 exactly.
  loge2g_inf computed once at x=60; e2g = exp(2*gamma' + log(A/((x^2-1)*nrm)) - loge2g_inf). Doing it in log space
  is what removes the underflow, so chi=0.9, q=0.95 becomes computable. q=0 (beta=0) is BYTE-IDENTICAL to exact
  Kerr (rel ~1e-16, every component); vacuum preserved (Ricci h^2->0 for q=0.2 AND q=0.5); g_xx ratio q=0.2/q=0
  now 1.0004 (asymptotically flat).
- RE-VALIDATION (all green): §99 (no Carter for q!=0) UNCHANGED -- integrability is path-based hence
  chart-independent; §100 (Peters, q=0 Kerr) unaffected; §101 GREEN, and the corrected chart makes MN q=0.2
  dE/dtau = -6.7e-5, even CLOSER to Kerr's -6.7e-5 than the pre-fix -9e-5. WHY RESULTS SURVIVE: the fix is a
  CONSTANT rescaling of g_xx,g_yy, so orbit PATHS (Poincare, box-dim, integrability) are preserved exactly; only
  proper-time quantities (flux, frequencies) move, and they move toward correct.
- BRIDGE IMPACT (relayed): B1's box-dims / positive-controls UNCHANGED; B1's flux & frequency VALUES shift (they
  were on the non-flat chart) -> needs a re-run on the corrected metric.
- SIDE FIX: the log-form correctly RAISES on MN's A<0 region (the known near-rod CTC / naked-singularity
  pathology, where the OLD code silently produced g_xx<0). Made geodesic_chaos trajectory/lyapunov catch
  (ValueError, OverflowError, ZeroDivisionError) and stop cleanly. §101(B) demo re-tuned: the FD-roundoff
  false-positive now needs ch=1e-7 (was 1e-5) -- the gauge-fix improved conditioning -- but still reproduces
  (lambda=0.83 noisy vs 0.02 de-noised, box-dim 1.06 regular). Modified: manko_novikov.py (gauge-fix),
  geodesic_chaos.py (robust integrators), 101_emri_carter_and_chaos.py (re-tuned B).
- §102 ASK 2 (MN's own bound chaos, the intended positive control): CHARACTERIZED, not cleanly exhibited.
  With the metric now computable at chi=0.9, q=0.95, mapped the permissible region at E=0.95, Lz=3: it splits
  into THREE disconnected wells (Kerr has one) -- INNER [1.24,1.64] metric-DEGENERATE (g_tt,g_xx,g_yy->0,
  signature flip to CTCs by x~1.7 = MN's known near-rod naked-singularity pathology); SECOND lens [3.04,4.96]
  (bound in y by the W=-1 wall, but its inner edge ABUTS the degenerate zone -- traced an orbit launched at
  (4.0,0): it drifts inward to x~2.98 and hits the pathology); OUTER [5.58,31] clean (orbits REGULAR, box-dim
  0.97-1.03). So at this EXTREME quadrupole the candidate chaotic basin is PATHOLOGY-BOUND, not a clean sea --
  consistent with §97/§98 (ZV chaos elusive) and §100/§101. MN's documented chaos is thin-layer near resonances
  (the literature uses the rotation number, not gross area-filling); §99 already gives the rigorous statement
  (no quadratic Carter for q!=0). A clean box-dim->2 orbit was NOT exhibited: the thin layers need the exact
  literature ICs at moderate q or a rotation-number sweep, and the finite-differenced Hamiltonian makes a
  high-resolution section compute-prohibitive (orbits here have a ~300-proper-time latitudinal period -> ~20
  crossings in 150k steps, and sparse sections give artificially-high box-dim = the under-resolution trap §101
  flagged). HONEST OUTCOME: the corrected metric is the deliverable (a real correctness win + the q=0.95
  enabler); the geometric positive-control stays a well-characterized open item, exactly like ZV. New
  (exploratory): _mn_pocket_scan.py (region map + pocket launches), _mn_resonance_chaos.py (rotation-number hunt).

## 2026-06-26 — §103 BRIDGE ROUND 3: MN metric verified EXACT; inner chaos is a coordinate-stiffness wall
- The bridge built a thin-layer chaos detector (Laskar frequency-drift: section-frequency is constant for any
  regular orbit incl. resonant islands, drifts only for chaos; area-blind, ~100x margin on Henon-Heiles, no
  Kerr resonant-island false-positive). It asked for ONE set of literature ICs for a chaotic MN orbit to aim it.
- CONVENTION CONFIRMED (Gair-Li-Mandel 2008, arXiv:0708.0628): the bridge's q == our q (q=-(M2-M2_Kerr)/M^3).
  Literature chaos (Contopoulos/Lukes-Gerakopoulos/Apostolatos, arXiv:1108.5057): chi=0.9, q=0.95, E=0.95,
  Lz=3, INNER permissible region (two CZV for large Lz; inner mainly chaotic), 2/3 resonance.
- METRIC VERIFIED EXACT: fetched the explicit MN metric from Gair-Li-Mandel 2008 and checked a, b, A, B, C, psi
  LINE-BY-LINE vs manko_novikov.py -- ALL MATCH, including the -1/+1 a,b constants I kept distrusting (the -1
  cancels Sa's l=0 limit (x-y)/R->1, so a->Kerr at infinity). The gamma' asymptotic constant is exactly what
  the §102 normalization compensates. So our MN IS the exact Manko-Novikov; §99-§102 are on the correct metric.
  CHASED A GHOST first: tested 'remove the a,b constants' -- it fixes A(x=3)=0 but BREAKS asymptotic flatness
  (0.6%, the tell it's wrong). The A=0 surface at x~3 is a REAL MN feature at this extreme deformation.
- THE CLEAN TARGET (located the resonance a blind sweep misses): a=0.9, q=0.6, E=0.95, Lz=3.0 -- the bridge
  swept Lz=2.8, one slice off. nu_r/nu_theta=2/3 at x0~7.7 (7.5->0.657, 8.0->0.677). Outer-region layer is thin
  (box-dim grazes 1.03, de-noised lambda floored) -> the bridge's detector's job. Relayed.
- THE ROBUST INNER ORBIT IS A NUMERICAL WALL, not a metric one: the literature's chaos lives between the rod
  (x=1) and the A=0 surface (x~3), COORDINATE-STIFF in prolate spheroidal (g_xx,g_yy->0 => velocities
  ~1/sqrt(g)->inf). Built an adaptive step-doubling integrator (_mn_adaptive_inner.py): deep inner (x<1.5) too
  stiff (st=0 at the hmin floor); x~1.52 runs but H-drift=140 (garbage); x~1.60 conserves H but the y=0 section
  is a degenerate cluster (x-range 0.002 -- fast y-oscillation swamps the slow radial motion). Inner-chaos
  verdict INCONCLUSIVE in our toolkit -> needs Weyl (rho,z) coords + a different section surface (what the
  literature uses). KEY BANKABLE RESULT: our MN metric is the exact Manko-Novikov (line-by-line verified).
  New (exploratory): _mn_adaptive_inner.py.

## 2026-06-26 — §104 INNER-CZV CRACKED: trustworthy near-rod MN orbits via partitioned launch + adaptive step
- §103 called the inner region 'inconclusive, needs Weyl'. Kept pushing -- it's reachable WITHOUT Weyl. The
  fix was two NUMERICAL moves, not coordinates: (1) adaptive step-doubling must REFINE-ON-EXCEPTION (a step
  that flings the orbit into a bad region halves h and retries instead of breaking); (2) the LAUNCH must
  partition a small fraction of the kinetic energy into RADIAL momentum (px != 0) -- with px=0 the section
  degenerates to a cluster (no radial motion); too much px reaches the stiff deep-inner zone and H-drift blows
  up. Sweet spot f_r ~ 0.1-0.25 at x0 ~ 1.56-1.60 keeps the orbit in the tractable outer part of the inner CZV.
- RESULT: trustworthy (H-drift 1e-4..1e-3) Poincare sections at the LITERATURE's exact inner-region params
  (chi=0.9, q=0.95, E=0.95, Lz=3). Box-dim 1.12-1.22 = the borderline regime (thin chaos vs under-resolved
  torus, the §101 ambiguity) -- EXACTLY what the bridge's Laskar frequency-drift detector is built to settle.
  Best targets (reduced state [x,y,px,py]): [1.60, 0, -2.35e-4, 7.95e-4] (box-dim 1.203, H-drift 3e-4, 500
  crossings) and [1.56, 0, -3.5e-5, 7.3e-5] (box-dim 1.219, H-drift 6.8e-4). Relayed to the bridge -- their
  detector settles chaos-vs-regular on the EXACT metric leg J studies.
- So the inner-region orbit IS reachable in our prolate toolkit; §103's 'needs Weyl' was premature (Weyl is
  only 0.585x less stiff -- not worth it; the partitioned launch is the real lever). The DEEP chaotic sea
  (x<1.5) is still beyond trustworthy integration (H-drift blows up there) -- that part may genuinely need
  higher precision / different coords -- but the inner-CZV edge (island + boundary layer) is now computable.
  _mn_adaptive_inner.py updated (refine-on-exception).

## 2026-06-26 — §105 POSITIVE CONTROL CLOSED: MN's own thin-layer chaos exhibited on the EXACT metric
- The bridge ran its validated Laskar frequency-drift detector on the two §104 inner-CZV section series we
  exported (chi=0.9, q=0.95, E=0.95, Lz=3) and SETTLED the borderline box-dim-1.2 ambiguity:
  - orbit_A [1.60, 0, -2.35e-4, 7.95e-4], 800 crossings: drift 0.0000 -> REGULAR = inner ISLAND of stability.
  - orbit_B [1.56, 0, -3.5e-5, 7.3e-5], 126 crossings: drift 0.980 -> THIN CHAOS = the boundary layer (above
    Henon-Heiles' own 0.59 chaotic floor). Length-matched control airtight: orbit_A truncated to 126
    crossings STILL reads 0.0000, so orbit_B's 0.98 is real, not a short-series artifact.
- So our two box-dim-1.2 orbits split cleanly into ISLAND (A) and BOUNDARY LAYER (B). MN's OWN bound
  thin-layer chaos is now EXHIBITED on the EXACT metric -- the positive control open since the first MN run
  (§99). Box-dim could NOT call it (1.20 vs 1.22, the §101 ambiguity); the frequency-drift detector did
  (0.0000 vs 0.980, a clean ~1000x split). The whole point of the borderline-sensitive tool, demonstrated.
- Bridge's complementary outer sweep (their fixed-step handles the outer region fine): a=0.9, q=0.6, Lz=3.0,
  x0 in [7.3,8.1] (the 2/3 resonance we located) -- all 17 orbits regular incl. the centre x0=7.70. So the
  full CZV picture holds and is classified end-to-end by ONE validated detector: REGULAR outer region ·
  inner ISLAND of stability · thin CHAOTIC boundary layer.
- THE CHAIN that closed it: §102 (asymptotic-flatness fix) -> §103 (metric verified EXACT vs Gair-Li-Mandel
  2008) -> §104 (adaptive integrator + partitioned launch reach the stiff inner basin) -> bridge's
  frequency-drift detector settles the borderline. Cross-repo positive control CLOSED. Still open
  (someday/higher-precision, not a request): the deep chaotic sea at x<1.5.
- §105 BATTERY (this session, made self-contained): implemented poincare.frequency_drift (dominant
  frequency = windowed-FFT peak + parabolic sub-bin refinement, of first vs second half of the section
  sequence; |df|/f; area-blind, no FD-roundoff/resonant-island false positive) + gated battery
  105_chaos_frequency_drift.py: (A) Henon-Heiles regular(E=1/12)=0.0000 vs chaotic(E=1/6)=1.38 -> separates
  order/chaos; (B) Kerr bound geodesic=0.0000 (H-drift 2e-15) -> no false positive on an integrable metric;
  (C) EXACT MN inner-CZV: orbit_A 0.0000 (island) vs orbit_B 0.9798 (thin chaos), length-matched control
  airtight. Native detector reproduces the bridge's verdict to the digit (orbit_B 0.980). The positive
  control is now SELF-CONTAINED + GATED on our side -- a THIRD validated chaos lens beside box_dimension
  (§84) and de-noised lyapunov (§79/§101), and the one that succeeds exactly where they're ambiguous (the
  §101 box-dim~1.2 borderline). Battery count -> 89.

## 2026-07-02 — §106 ZV's OWN THIN-LAYER CHAOS EXHIBITED (autonomous day; the §97/§98 caveat closed) + GATE 89-GREEN
- FIRST: the full gate finally survived an uninterrupted run -- ALL 89 GREEN (the §105 addition confirmed
  in-gate; four power losses had killed every previous attempt).
- THEN the §105 playbook applied to the OTHER elusive target: ZV delta=2's razor-thin stochastic layer
  (Lukes-Gerakopoulos PRD 86 044013: E=0.95, Lz=3, chaotic rho=7.518 vs regular 7.548) that §97/§98's
  box-dim scans grazed. Hunted with the area-blind frequency_drift. COARSE scan (x0 step 0.02, sigma=1 and
  0.5 -- noting hunt2 NEVER reached the layer at the sigma=0.5/M=1 convention, x0~15.07): found the
  structure but read regular at p_x=0... then the REFINE (x0 step 0.002 across the island-chain boundary)
  found the layer's FULL ANATOMY at the plunge separatrix:
    plunge | LAYER x0=7.545 (drift 0.0266, 210 crossings then ESCAPES) | island chain 7.549-7.563
    (drift ~1e-4, box-dim 0.3-0.7, never escapes; sticky edges) | LAYER x0=7.565 (drift 0.0132,
    184 crossings then escapes) | circulating tori 7.60+ (drift ~1e-4)
  TWO independent layer hits on the two edges of the island chain, each with BOTH chaos signatures:
  frequency wander (quarter-pair drift GROWS along the series: 0.005->0.025->0.070) AND finite bounded
  lifetime (escapes through the separatrix; KAM tori are eternal). H-drift 5e-12 (physics, not noise).
- ADVERSARIAL STRESS (h-halving): at h=0.01 the half-vs-half drift drops to 0.0034 BUT the orbit still
  escapes (237 crossings) and the quarter-wander still grows (->0.0127). Reading: TRANSIENT/sticky layer
  chaos -- exponential shadowing means different h = different realization of the same layer; the
  INVARIANT signatures are drift-fires + finite-lifetime, which persist at both h while the island/torus
  controls show neither at any h. Honest: drift magnitude is h-sensitive (recorded, not hidden); layer
  found at rho~7.48-7.50 vs the literature's 7.518 (~0.5%, units/convention nuance) -- we exhibit the
  documented layer's existence at the documented (delta, E, Lz), not the exact quoted coordinate.
- BATTERY 106 (gated): (A) layer orbit fires (0.0266>0.0115) AND escapes (210<240) with H-drift 5e-12;
  (B) island 0.012 away in x0: drift 0.0001, survives -- a 267x contrast; (C) circulating torus: drift
  0.0000, survives (the signal is specific, not generic). PASSES. Battery count -> 90.
- WITH §105: BOTH exact bumpy-BH metrics in the engine (MN rotating, ZV static) now have their algebraic
  non-integrability (§97/§98/§99) backed by an EXHIBITED geometric chaos positive-control, each settled by
  the frequency-drift detector exactly where box-dim was ambiguous. The detector is 3-for-3 on thin layers
  (MN inner-CZV, MN island-vs-layer, ZV separatrix layer).
- New: 106_zv_thin_layer_chaos.py (battery), _zv_freqdrift_hunt.py + _zv_freqdrift_refine.py (exploratory).

## 2026-07-02/03 (evening->night) — §107 THE DEVIL'S STAIRCASE: resonance frequency-LOCKING exhibited (follow-up plan item 1a)
- Evening discussion set the pre-weekend follow-up plan (docs/PLAN.md): (1) the LISA resonance-plateau
  observable, (2) analyzer chaos lens, (3) BH mimickers, (4-parked) EdGB. Started item 1a: the
  QUASI-STATIC plateau -- inside a resonance island the frequency ratio is LOCKED to the rational across
  the island's finite width (Lukes-Gerakopoulos/Apostolatos/Contopoulos PRD 81 124005); integrable Kerr
  has no locking width. Swept x0 across §106's ZV delta=2 island zone (E=0.95, Lz=3, x0 in [7.50,7.71],
  step 0.005, 240 section crossings/orbit).
- TWO ESTIMATOR FALSE-STARTS, both caught + diagnosed (north-star discipline): (v1) naive dominant-FFT-peak
  of the trajectory is fooled by libration peaks off island-centre; (v2) turning-point-anchored FFT is
  fooled near strong resonances where the spectrum is FULLY COMMENSURATE with dominant subharmonics
  (pericenter alternation -- diagnosed by dumping top-5 peaks: at the locked zone EVERY peak is an integer
  multiple of the closure frequency 0.001612; on a circulating torus the y-peaks sit at (n+1/3)x = 
  incommensurate). The unambiguous instrument is the SECTION-sequence frequency (the §105/§106-validated
  estimator): a locked orbit's section sequence is q-periodic => frequency EXACTLY p/q; a torus varies
  smoothly. v3 = the definitive staircase.
- THE STAIRCASE (v3, ZV delta=2, E=0.95, Lz=3): plunge (<=7.540) | chaotic layer (7.545-7.550: nu=0.2035,
  0.1990 -- off-rational, escaping) | **1/5 LOCK 7.555-7.565** (0.20000, 0.20000 EXACT + 0.19982) | layer
  (7.570 off, 7.575 plunge) | SMOOTH CLIMB 7.580->7.640 (0.2141->0.2458, 13 points, monotone ~0.002/step,
  CONTINUOUS through the zone where v2's estimator had fake jumps) | **1/4 LOCK 7.645-7.665** (0.25001,
  0.25000 x4 -- FIVE consecutive points; the approach SNAPS from 0.2458 onto the rational and HOLDS) |
  release 7.670+ (0.2539->0.2648 smooth climb). Two rational plateaus; the 1/4 island (5 steps wide) fatter
  than the 1/5 (3 steps) = the KAM ordering. The v2 trajectory-spectra INDEPENDENTLY confirm the locks
  (exact commensurability at 7.555/7.560 with nu_x/nu_y=3/5 <-> section 1/5; the 7.645-7.665 zone
  commensurate with nu_x:nu_y=1:2 <-> section 1/4).
- Kerr control (integrable; same estimator): rotation number must vary smoothly with NO multi-step lock.
  [numbers landing as this is written; battery §107 asserts lock+contrast+control]. This is the
  quasi-static half of the LISA signature; item 1b (flux-driven drift through the island -> the plateau in
  TIME) is next. New: _plateau_quasistatic.py (v1/v2 + spectra diagnostic), _plateau_v3_section.py (v3).
