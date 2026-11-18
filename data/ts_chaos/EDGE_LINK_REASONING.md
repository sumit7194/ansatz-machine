# When is the TS δ = 2 capture edge the stable manifold of the §154 orbit? Reasoning, 2026-11-18, NOTHING RUN

**Ask:** Sumit, relayed by the Bridge (2026-11-18): "window vs saddle", reasoning first, then an Opus review, then a
pre-registration, all before anything runs.
**Model provenance:**
- §0–§5: Claude Fable 5.2 (`claude-fable-5-2`), session ansatz-machine-personal.
- §6: review by a Claude Opus subagent that was given the v1 file and the repo, not my conclusions. Its only
  computation was a few lines of mpmath arithmetic for the Kerr numbers of §2.
- **This is v2.** v1, as written before the review, is commit 73427e4. §6 lists every change the review caused.
- No integration, map evaluation or data fit was run to write this.

**Inputs used:** RESULTS §150 and §154 as published, `TANGLE_PREREGISTRATION.md`, `SADDLE_REDESIGN_PROPOSAL.md`, the
stored `tangle/*.json` headline values, and the scripts (to read definitions). Nothing from tabula, the Bridge's
ledgers or any sibling repo.

---

## 0. The simple version

- A particle falls in only by passing one "gate": the unstable orbit γ of §154. An orbit that arrives exactly on the
  borderline between falling in and bouncing back does neither: it circles γ for ever. The set of all such orbits is
  γ's **stable manifold** W^s.
- The capture edge should be W^s **together with its limit points**. This note says exactly when that is true, and
  in which direction.
- **One direction is nearly free.** W^s is always part of the edge, as long as orbits that leave γ inward do plunge.
  With §154's transverse crossing, W^s folds back on itself infinitely often, so the edge contains a Cantor set.
  That guaranteed fractal piece sits **just above the fixed point x\***, not specifically in the §150 window.
- **The other direction needs a real hypothesis:** the gate must be one-way. If it is, every place where the outcome
  switches along our start line between x\* and the outer turning point x_h, which includes the §150 window, is a
  point of W^s. On the start line those are exactly the **symmetric homoclinic points** of γ.
- **What the crossing alone does not give:** the size of the measured exponent α ≈ 0.05, or an exponent below 1 in
  the infinite-time limit. Those need more than "the manifolds cross" (§1.6).
- Three cheap tests can break the link (§4).

---

## 1. The statement, with every hypothesis named

### 1.1 Objects

- **System.** Geodesics at fixed (E, L), reduced to 2 degrees of freedom (x, y, p_x, p_y) on the shell H = −1/2.
  TS level: p = 4/5, E = 97/100, L = 41/8. Kerr control: same E, L = 2.550268. E < 1, so no orbit escapes to infinity.
- **Section.** Σ = {y = 0, p_y > 0}, coordinates z = (x, p_x). P is the first-return map. P is only partially
  defined: an orbit that plunges has no next crossing.
- **Symmetries (exact, checked in sympy for §154).** T reverses both momenta. S reflects y. On Σ the reversor is
  R = S∘T: (x, p_x) → (x, −p_x), with P∘R = R∘P⁻¹. The **symmetry line** is ℓ = Fix(R) = {p_x = 0}. Every §150 start
  point lies on ℓ.
- **γ.** The unstable spherical-type orbit. Its fixed point is z\* = (x\*, 0) ∈ ℓ, with multiplier λ > 1
  (TS: x\* ≈ 9.8046, λ ≈ 38.39; Kerr: x\* = 4.99330, λ ≈ 39.84). It has four branches: W^u_out, W^u_in,
  W^s_out = R(W^u_out), W^s_in = R(W^u_in).
- **h.** The first point where W^u_out meets ℓ (TS: x_h ≈ 56.861; Kerr: 28.416). By symmetry h ∈ W^s too.
- **Plunge (operational, as in §150 and §154).** An orbit plunges when it first has x < x_pl, with x_pl = 1.5
  (engine status 1). This level has no equatorial ridge, so the scan's cut is the default 1.5; `_ts_tangle.py` uses
  the same value. Plunging is absorbing. Status 2 ("escape": x > 2000 or |y| > 0.999999) and status 3 (step cap) are
  **not** plunges and are counted separately.
- **Capture set.** B = {z ∈ Σ : the forward orbit plunges}. C_N = {plunges within N upward crossings}; §150's α used
  N = 300 and 600. B is open. Its complement is the trapped set.
- **Capture edge.** ∂B in Σ. Along the start line the object that §150 sees is the **switch set**: the endpoints of
  the plunging intervals of ℓ. These are two different objects (§1.4).
- "W^s" below means points whose forward orbit converges to γ **without** plunging first.
- **The window.** §150's α window is x0 ∈ [9.912067, 9.945202] on ℓ: 0.108 to 0.141 above x\*.

### 1.2 Two structural facts

- **F-a. ℓ ∩ W^s = ℓ ∩ W^u.** If z ∈ ℓ ∩ W^s then z = R(z) ∈ R(W^s) = W^u. So every point of W^s on the start line is
  a **symmetric homoclinic point** of γ (or z\* itself). "The window's switches are W^s strands" and "the window's
  switches are symmetric homoclinic points of γ" are the same claim.
- **F-b. h is a primary intersection point**, given one hypothesis.
  - **Hypothesis F-b′:** h is the first **intersection** of W^u_out with ℓ, not merely the first sign change of p_x
    that §154's 48-samples-per-domain tracer detected. (A tangential touch, or two crossings between samples, would
    break what follows. To be checked, §4.)
  - Then U = W^u_out from z\* to h stays on one side of ℓ, and its mirror image S = R(U), the piece of W^s_out from
    h to z\*, stays on the other. They meet only at z\* and h. Σ is simply connected here (no equatorial ridge), so
    U ∪ S bounds a Jordan domain **D**, symmetric under R, with **D ∩ ℓ = (x\*, x_h)**. The window lies inside D.

### 1.3 Theorem 1: W^s is always in the edge (the "accumulates on" direction)

**Hypotheses.**
- **A1.** γ is hyperbolic, and h is a transverse homoclinic point. (§154, numerical; the Bridge's V20.)
- **A2.** At least one point of the inward branch W^u_in plunges (status 1). (§154's tracer seeded 48 points across
  a fundamental domain of that branch and all terminated, but it did not record *which* status ended them.)

**Claims.**
1. cl(W^s(γ)) ⊂ ∂B.
2. ∂B ∩ ℓ ∩ (x\*, x\* + δ) contains a Cantor set of positive Hausdorff dimension, for every δ > 0.
3. Near x\* that structure is **asymptotically** self-similar under (x0 − x\*) → (x0 − x\*)/λ, with γ's own λ.

**Why.**
- Take w ∈ W^s. Its iterates approach z\*. Near z\*, points on one side of W^s_loc leave along W^u_in and shadow it.
  By A2, openness of B and the λ-lemma, some of them plunge. Pull back along the orbit of w: plunging points lie
  arbitrarily close to w, and w itself never plunges. So w ∈ ∂B. ∂B is closed, which gives claim 1.
- A1 gives a horseshoe Λ ∋ z\* (Smale–Birkhoff). W^s(γ) accumulates on the stable leaves of every periodic point of
  Λ, so cl(W^s(γ)) ⊇ W^s_loc(Λ): a Cantor set of curves accumulating on W^s_loc(z\*) from the W^u_out side.
- With v_u = (a, b), a > 0, the stable direction is v_s = R v_u = (a, −b). So ℓ is transverse to W^s_loc at z\*, and
  its half x0 > x\* bisects the sector between W^u_out and W^s_out, which is where the leaves are. A leaf at unstable
  offset s meets ℓ at x\* + 2as, and P⁻¹ sends s to s/λ. That gives claims 2 and 3 (C¹ linearisation holds in 2D).

**What this buys, and where.** "The horseshoe implies a fractal capture edge in the infinite-time limit" is TRUE in
the set sense under A1 + A2 alone, with no global assumption. But the guaranteed piece is **immediately above x\***.
Theorem 1 does not put a single point of W^s inside the window.

### 1.4 Theorem 2: every switch between x\* and x_h is on W^s (the "equal to" direction)

**Hypotheses, in addition to F-b′.**
- **L2 (no shortcut out of D).** P is defined, continuous and injective on cl(D): no orbit starting in cl(D)
  plunges before its next crossing of Σ.
- **L3 (one-way gate).** Every orbit that leaves cl(D) (z ∈ D, P(z) ∉ cl(D)) plunges and never re-enters D.

**Claim.** Every endpoint of every connected component of B ∩ ℓ ∩ D is a point of W^s(γ), hence (F-a) a symmetric
homoclinic point of γ. In symbols, on [x\*, x_h]:

    (switch set along ℓ)  ⊂  cl( W^s(γ) ∩ ℓ )  ⊂  ∂B ∩ ℓ .

- The second inclusion is Theorem 1 (it needs A2).
- The first is an equality only if no symmetric homoclinic point in (x\*, x_h) is a tangency of W^s with ℓ.
- B is not symmetric under R, so the 2D edge restricted to ℓ and the switch set along ℓ are different objects. The
  theorem is about the switch set.
- No hyperbolicity of the trapped set is assumed: regular islands are allowed. Their boundaries are never ends of
  plunging intervals; they can be in ∂B only as limits.
- Nothing is claimed for ℓ outside [x\*, x_h].

**Why.**
- Let L = {z ∈ D : P(z) ∉ cl(D)}, the exit lobe. By L3 the first exit is final, so the sets
  E_k = D ∩ P⁻ᵏ(L) are disjoint and cover B ∩ D. They are open: a forward iterate of a point of D can land on ∂D only
  on S (never on U, because W^u points move away from z\* along W^u), and a point on S never exits.
- So a connected piece I of B ∩ ℓ ∩ D lies in a single E_k. Its endpoint e is not in B, so its orbit never leaves
  cl(D), and by continuity Pᵏ(e) ∈ ∂L.
- ∂L ∩ D ⊂ P⁻¹(∂D) ∩ D ⊂ P⁻¹(S) ⊂ W^s, because P⁻¹(U) ⊂ U ⊂ ∂D. The rest of ∂L lies on ∂D = U ∪ S. A point of the
  open arc U that bounds L maps outside cl(D) and so plunges (L3), which e does not. Hence Pᵏ(e) ∈ W^s, and e ∈ W^s.
- Only continuity and injectivity of P on cl(D) are used.

**A heuristic picture, not a proof (H1).** One expects L2 and L3 when γ is a brake orbit whose curve in the (x, y)
plane spans the allowed region (nothing can go around it), γ is the only invariant set in the neck, and nothing that
passes inward comes back. **These do not imply L3:** they say nothing about an orbit that leaves cl(D) and wanders
outside it without entering the neck. So L3 itself is the hypothesis, and it is tested directly (§4).

### 1.5 What Theorem 2 implies for the §150 window

- **W-1. Where a finite-horizon switch sits.** Let two start points have different outcomes at horizon N, both
  confirmed in double-double. Then a true switch point lies between them, or both lie in one plunging interval I and
  the nearer end of I is within about λ^−(N − n)·|I| of the pair, where n is the plunging member's lifetime. That
  distance is negligible when N − n is large and **not** negligible when the plunger's lifetime is close to N. (Needs
  L2 and L3. About 17–40% of window start points are realisation-sensitive in double precision, so the stored
  switches must be re-confirmed first.)
- **W-2. Cantor structure inside the window.** If one symmetric homoclinic point x_w of γ lies in the window and W^s
  crosses ℓ there (a sign change, which a certified switch gives), then pulling back Theorem 1's lamination along the
  orbit of x_w puts a Cantor set of edge points next to x_w. This needs A1, A2 and that one point.
- **W-3. Lifetimes.** On a plunging interval the lifetime is finite, changes in unit steps, and diverges at both ends
  like log(1/distance)/log λ.

### 1.6 Three meanings of "fractal edge", and which one the crossing gives

| | meaning | implied by A1 + A2? |
|---|---|---|
| **Fr-1** | the edge contains a Cantor set of positive dimension | **Yes**, near x\* (Theorem 1). In the window: yes if W-2's point exists. |
| **Fr-2** | the lifetime function is singular on a fractal set | Yes, the same set as Fr-1. |
| **Fr-3** | the plunge-vs-never **outcome** has uncertainty exponent α < 1 as N → ∞ | **No.** |

- **Fr-3.** Outcome uncertainty needs two outcomes of positive measure. A hyperbolic Cantor set has measure zero:
  where the trapped set is only that, almost every pair of neighbours both plunge. An infinite-time outcome exponent
  in the window would be a property of whatever trapped set has positive measure there (regular islands, the regular
  core), not of γ's horseshoe.
- **The finite-N α ≈ 0.05 has two possible sources, and this note does not decide between them.**
  - Slow hyperbolic escape: a hyperbolic saddle gives α_N ≈ κ/λ̄ over the measured ε range (Kantz–Grassberger; κ the
    escape rate per crossing, λ̄ the mean stretching rate). A small splitting means a small turnstile and a small κ,
    so a small α is reachable with no islands at all.
  - Stickiness near islands (Lau–Finn–Ott), which §150 suggested.
  - Telling them apart needs κ (the exponential tail of lifetimes) and λ̄, compared with α. Not proposed here.
- **So even with the link shown, the correct upgrade is Fr-1 / Fr-2 wording, not a statement about α.**

---

## 2. What holds exactly in Kerr (the control)

- **Integrable.** Carter's Q is conserved, so Σ is foliated by curves of constant Q. Convention: chart L > 0 is
  Boyer–Lindquist L < 0 (retrograde), as in `kerr_xsph`. With m = 5/4, a = 3/4, E = 0.97, L_BL = −2.550268 the
  unstable spherical orbit has r_sph = 6.2433047 (x\* = r_sph − m) and Q_sph = 18.029.
- **Separatrix.** W^s = W^u = {Q = Q_sph} minus γ. The outer branch is one homoclinic loop (Levin & Perez-Giz). The
  splitting is zero (§154 G2: ≤ 1e−13).
- **Radial polynomial at Q_sph.** R(r) = (E² − 1)(r − r_sph)²(r − r_a)(r − r_b), and by Vieta
  r_a + r_b = 2m/(1 − E²) − 2 r_sph = 29.8146.
  - r_a = 29.66618 is the apoapsis of the homoclinic orbit, so **x_h is known in closed form.** (The reviewer's
    arithmetic puts r_a − m within about 1e−10 of §154's traced x_h. That is relayed from the review; the registered
    check is in §4.)
  - r_b = 0.1484 is inside the horizon (r₊ = 2.25), and the plunge cut sits at r = 2.75. So R > 0 from the cut to
    r_sph: **the gate is exactly one-way.**
- **Capture set.** An orbit survives iff Q > Q_sph and it sits in the outer radial well.
- **On the start line** the edge is exactly **two points**: x\* (the fixed point itself) and x_h. Between them
  everything survives for ever; outside them everything plunges. Hence α = 1, as §150 measured.
- **Two kinds of edge point, with different precision floors.** Every return leg arrives with an offset from W^s
  proportional to Q − Q_sph.
  - At x_h, W^s crosses ℓ transversally: the offset is linear in the distance d.
  - At x\*, ℓ passes through the fixed point: the offset is ∝ d². A phase-space error δ per return then blurs
    outcomes over a width ~√δ. This matches the floor that voided the lifetime test, whose Kerr band sat at x\*.
  - This is a Kerr statement (it uses Q). It does not carry over to TS as it stands.
  - Design consequence: **use x_h, not x\*, as the Kerr control point.**

---

## 3. Where TS could break the link

| # | failure | what it breaks | how it would show |
|---|---|---|---|
| **B1** | **Return from inside.** TS δ = 2 has no regular horizon. An orbit could pass γ inward, turn round above x_pl = 1.5, and come back out. | L3 | an orbit that gets well inside the gate and later crosses at x > x\* |
| **B2** | **Inner trapping.** An orbit passes the gate, never reaches x_pl and never comes back. §150 would file it as "survive". | L3 | an orbit well inside the gate that has not plunged after many crossings |
| **B3** | **The cut owns part of the edge.** Orbits whose smallest x equals x_pl are edge points that are not on W^s(γ). | the claim, for those points | a switch that moves when x_pl is changed |
| **B4** | **Wandering outside D.** An orbit leaves cl(D) and neither plunges nor returns. | L3 | the same census as B2 |
| **B5** | **A second gate.** Another hyperbolic orbit with a whole unstable half-branch that plunges (an asymmetric twin of γ, or an inner unstable orbit). | L3 | a lifetime discontinuity whose bracketing orbits do not approach γ |
| **B6** | **Bypass.** γ is not a brake orbit, or its curve does not span the allowed region. | the heuristic H1; a warning for L2/L3 | the half-return map does not fix z\*; the allowed region stays connected with γ's curve as a wall |
| **B7** | **F-b′ fails:** W^u_out touches or crosses ℓ before h. | the domain D itself | \|p_x\| along U comes close to zero before h |
| **B8** | **A2 fails:** the inward branch ends by something other than a plunge. | Theorem 1 | status codes of the inward seeds |
| **B9** | **The window is hard territory.** Long-lived orbits there amplify offsets by up to ~1e14, so their strands cannot be resolved even in double-double. | nothing in the theorems; it limits what can be tested | switch brackets that cannot be refined before precision runs out |
| **B10** | **The test cannot fail.** If W^s strands are dense at the comparison tolerance, "the switch is within ε of W^s" is true for any point at all. | the Bridge's first suggested test, as worded | — |

B10 is why the tests in §4 never use distance to the manifold. They use what the orbit itself does.

---

## 4. Cheap tests that could falsify the link

The exact rules, thresholds and predictions are in `EDGE_LINK_PREREGISTRATION.md`. In outline:

### T-L3: is the gate one-way? (B1, B2, B4, B7, B8; diagnostics for B6)
- Build D as a polygon from §154's traced U and its mirror image; check F-b′ on a much finer sampling.
- Follow sample orbits started in D (on ℓ and off it). Each time one leaves cl(D), it must plunge (status 1) within
  a bounded number of crossings and must never be found in D again.
- Independently of the polygon: no orbit that reaches well inside the gate may later cross at x > x\*.
- Inward seeds are re-run with status codes.
- Kerr must pass all of it (there it is exact). Must-fail: the same counters with the gate deliberately misplaced.
- **Falsifies** L3, and with it Theorem 2.

### T-SWITCH: are the window's switches strands of W^s(γ)? (B3, B5; gives W-2)
- **Certificate.** A pair (p, q) on ℓ straddles a strand of W^s(γ) if the whole short segment between them is
  carried, intact and still short, into a small neighbourhood of z\*, and its two ends then leave on opposite sides
  (one inward to a plunge, one outward). It uses what the orbits do, never a distance to a computed manifold.
- Stored §150 switch pairs are re-confirmed in double-double, bisected, and classified: **H** (certificate), **A**
  (only a smooth lifetime step), **O** (a real discontinuity that does not go to γ), **U** (precision ran out).
  **O falsifies the link.**
- Each H switch is re-located with x_pl = 1.3 and 1.7 and must not move.
- Controls: Kerr and TS at x_h must give H. A must-fail control builds a fate boundary that γ does **not** own (a
  raised cut in Kerr that orbits graze) and must come out O.
- Scope: only switches whose plunging member is short-lived can be resolved. The acceptance rate is reported.

### T-BANDS: an engine and Theorem-1 check, not a test of the link
- Given A1 and A2, banding at x\* is a theorem. So this can only fail through the engine, precision or A2.
- First-return fates on a logarithmic grid above x\* must repeat with period ln λ; consecutive band edges must be in
  ratio λ to a tolerance fixed in advance. Kerr must show no bands.
- It is run because it is the direct numerical picture of Fr-1 at x\*. It does not enter the falsification verdict.

---

## 5. What each outcome would license

| claim | needs |
|---|---|
| "A Cantor set of edge points accumulates on x\*" (Fr-1 at the fixed point) | A1 (§154), A2 with status codes (T-L3), T-BANDS as predicted |
| "A Cantor set of edge points lies inside the §150 window" | the above, plus one H switch in the window (W-2) |
| "The switches tested in the window are symmetric homoclinic points of γ" | the H switches themselves; a statement about the tested, short-lived sample only |
| "Every switch between x\* and x_h is on W^s(γ)" (Theorem 2) | T-L3 passing; it remains "supported on a sample", never proved |

- **Any O, any return, any stall:** the link is falsified at this level, at least for part of the edge. Report it and
  do not upgrade the window wording.
- **All U or all A in T-SWITCH:** no statement about the window.
- **Never licensed here:** a claim about α at any horizon, about other levels, or about EMRI orbits. Everything is
  numerical, not rigorous.

---

## 6. Opus review: what it changed

The review found no blocker. 23 findings: 4 checked-and-held, 9 major, 10 minor.

**Accepted (all majors, and these minors).**

| # | finding | change made |
|---|---|---|
| 4 | L3 as written contradicted A1: W^s points inside D map onto ∂D, and "P(z) ∉ D" would make them plunge | L3 now says "leaves cl(D)" |
| 5 | one proof step put a W^u arc where there is none | proof replaced by the shorter ∂L ∩ D ⊂ P⁻¹(S) argument |
| 6 | the displayed equality was not proved; B is not R-symmetric, so the 2D edge on ℓ and the switch set differ | stated as two inclusions on [x\*, x_h]; equality only without tangencies |
| 7 | "H1 implies L2 and L3" was asserted and is false | H1 demoted to a heuristic; L3 is the hypothesis and is tested directly |
| 8 | the return census would have counted time-reversed plunges as returns, and failed in Kerr too | census redesigned: start in D, count only "well inside, then outside again" |
| 10 | missing failure modes: inner trapping, and edge points owned by the cut | B2, B3 added; switches are re-located at x_pl = 1.3 and 1.7 |
| 11 | W-1 overstated: a pair can sit in one plunging interval with lifetimes either side of N | W-1 restated with the λ^−(N − n)·\|I\| distance and the double-double condition |
| 12 | "α ≈ 0.05 is set by sticky orbits, not the horseshoe" was unsupported: slow hyperbolic escape gives a small α too | struck from §0 and §1.6; both sources named, neither claimed |
| 16 | the straddle certificate checked only the two ends | now requires the whole segment to stay short and intact up to the passage, and classifies the exit side there |
| 17 | the Kerr must-fail controls could not exercise the criteria (every Kerr fate boundary on ℓ is W^s) | replaced by a raised-cut grazing boundary, which γ does not own |
| 18 | the "±η transversality" check is invalid next to an accumulation of strands, and unnecessary | dropped; W-2 uses the crossing itself plus A1 and A2 |
| 1 | self-similarity is only asymptotic; A2 can be weaker | both edited |
| 3 | F-b needs "first intersection", and Σ simply connected | F-b′ added, with a check |
| 9 | §154 did seed the inward branch, but without status codes; α has a third outcome | A2 and §1.1 reworded; status codes everywhere |
| 13 | "circles γ for ever" is wrong for limit points | §0 reworded |
| 14 | Kerr numbers: Q_sph = 18.029 (not 18.1), r_b = 0.1484; state the sign convention | §2 corrected |
| 15 | the √δ floor uses Q and is a Kerr statement | caveat added |
| 19, 21, 22 | W-2 silently dropped A1; the licensed sentence did not say which test it used; "two engines" was wrong (same engine, different procedure) | W-2, §5 and the control wording fixed |

**Partly overruled.**

| # | finding | decision and reason |
|---|---|---|
| 20 | T-BANDS cannot test the link; define "excursion" by leaving a ball around z\* | First half accepted: T-BANDS is relabelled an engine and Theorem-1 check and leaves the verdict. Second half overruled: the excursion stays "largest x between two crossings exceeds X_far". It is equally operational, needs no extra radius, and the two definitions agree in the range used (d ≲ 1e−2). |
| 14 | cite the closed-form x_h agreeing with the tracer as an independent check | Not cited as established. It is the reviewer's arithmetic, so it is marked "relayed" and made a registered control instead. |
| 12 | (implied) measure κ and λ̄ to settle the source of α | Out of scope here. It is a separate question from the link and would need its own pre-registration. |
