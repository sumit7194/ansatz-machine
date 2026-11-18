# When is the TS δ = 2 capture edge the stable manifold of the §154 orbit? Reasoning, 2026-11-18, NOTHING RUN

**Ask:** Sumit, relayed by the Bridge (2026-11-18): "window vs saddle", reasoning first, then an Opus review, then a
pre-registration, all before anything runs.
**Model provenance:** the reasoning in §0–§5 is by Claude Fable 5.2 (`claude-fable-5-2`), session
ansatz-machine-personal. The review in §6 is by a Claude Opus subagent that saw this file and the repo, not my
conclusions in chat. No integration, map evaluation or data fit was run to write this.
**Inputs used:** RESULTS §150 and §154 as published, `TANGLE_PREREGISTRATION.md`, `SADDLE_REDESIGN_PROPOSAL.md`, the
stored `tangle/*.json` headline values, and the scripts (to read definitions). Nothing from tabula, the Bridge's
ledgers or any sibling repo.

---

## 0. The simple version

- A particle falls in only by passing one "gate": the unstable orbit γ of §154. An orbit that arrives exactly on the
  borderline between falling in and bouncing back never does either: it circles γ for ever. The set of all such
  orbits is γ's **stable manifold** W^s.
- So the capture edge should be W^s. This note says exactly when that is true, and in which direction.
- **One direction is nearly free.** W^s is always part of the edge, as long as the orbits that leave γ inward really
  do plunge. With §154's transverse crossing, W^s folds back on itself infinitely often, so the edge contains a
  Cantor set. That fractal piece is guaranteed to sit **just above the fixed point x\***, not specifically in the
  §150 window.
- **The other direction needs a real hypothesis:** that the gate is one-way and is the only gate. If it is, every
  end of every "plunging" interval between x\* and the outer turning point x_h, which includes the §150 window, is a
  point of W^s. On our starting line these are exactly the **symmetric homoclinic points** of γ.
- **What the horseshoe does not give:** the measured exponent α ≈ 0.05. That number is set by sticky, long-lived
  orbits next to regular islands, not by γ's horseshoe.
- Three cheap tests can break the link. They are in §4.

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
- **Plunge (operational, as in §150 and §154).** An orbit plunges when it first has x < x_pl, with x_pl = 1.5. This
  level has no equatorial ridge, so the scan's cut is the default 1.5; `_ts_tangle.py` uses the same value. Plunging
  is absorbing: the orbit is removed.
- **Capture set.** B = {z ∈ Σ : the forward orbit plunges}. C_N = {plunges within N upward crossings}; §150's α used
  N = 300 and 600. B is open (x < x_pl at a finite time is an open condition). Its complement is the trapped set.
- **Capture edge.** ∂B, in Σ or on ℓ. "W^s" below means points whose forward orbit converges to γ **without**
  plunging first.
- **The window.** §150's α window is x0 ∈ [9.912067, 9.945202] on ℓ: 0.108 to 0.141 above x\*.

### 1.2 Two facts that need no hypothesis

- **F-a. ℓ ∩ W^s = ℓ ∩ W^u.** If z ∈ ℓ ∩ W^s then z = R(z) ∈ R(W^s) = W^u. So every point of W^s on the start line is
  a **symmetric homoclinic point** of γ (or z\* itself). "The window's switches are W^s strands" and "the window's
  switches are symmetric homoclinic points of γ" are the same claim.
- **F-b. h is a primary intersection point, automatically.** U = W^u_out from z\* to h stays on one side of ℓ
  (h is the *first* crossing). Its mirror image S = R(U) is the piece of W^s_out from h to z\* and stays on the other
  side. They meet only at z\* and h. So U ∪ S bounds a Jordan domain **D**, symmetric under R, with
  **D ∩ ℓ = (x\*, x_h)**. The window lies inside D.

### 1.3 Theorem 1: W^s is always in the edge (the "accumulates on" direction)

**Hypotheses.**
- **A1.** γ is hyperbolic, and h is a transverse homoclinic point. (§154, numerical; the Bridge's V20.)
- **A2.** One fundamental domain of the inward branch W^u_in reaches x < x_pl. (§154 reports "the inward branch
  plunges"; a full fundamental domain has not been checked.)

**Claims.**
1. cl(W^s(γ)) ⊂ ∂B.
2. ∂B ∩ ℓ ∩ (x\*, x\* + δ) contains a Cantor set of positive Hausdorff dimension, for every δ > 0.
3. Near x\* that structure is self-similar under (x0 − x\*) → (x0 − x\*)/λ, with γ's own λ.

**Why.**
- Take w ∈ W^s. Its iterates approach z\*. Near z\*, points on one side of W^s_loc leave along W^u_in, and by A2 and
  openness of B they plunge. Pull back along the orbit of w: there are plunging points arbitrarily close to w, and w
  itself never plunges. So w ∈ ∂B. ∂B is closed, which gives claim 1.
- A1 gives a horseshoe Λ ∋ z\* (Smale–Birkhoff). By the λ-lemma, W^s(γ) accumulates on the stable leaves of every
  periodic point of Λ, so cl(W^s(γ)) ⊇ W^s_loc(Λ), a Cantor set of curves that accumulates on W^s_loc(z\*) from the
  side where W^u_out lies.
- ℓ crosses W^s_loc(z\*) transversally at z\*: the direction of ℓ is fixed by R, and the stable direction is not,
  because R swaps it with the unstable one. The part of ℓ with x0 > x\* lies between W^u_out and W^s_out, which is
  where the leaves are. So ℓ cuts the Cantor lamination transversally, arbitrarily close to x\*. That gives claims
  2 and 3.

**What this buys, and where.** "The horseshoe implies a fractal capture edge in the infinite-time limit" is TRUE in
the set sense under A1 + A2 alone, with no global assumption. But the guaranteed piece is **immediately above x\***.
Theorem 1 does not put a single point of W^s inside the window.

### 1.4 Theorem 2: every edge point between x\* and x_h is on W^s (the "equal to" direction)

**Hypotheses, in addition to A1–A2.**
- **L2 (no shortcut out of D).** P and P⁻¹ are defined and continuous on the closed domain D: no orbit starting in D
  plunges before its next crossing of Σ.
- **L3 (one-way gate).** Every orbit that leaves D (z ∈ D, P(z) ∉ D) plunges and never re-enters D.

**Claim.** Every endpoint of every connected component of B ∩ ℓ ∩ D is a point of W^s(γ), hence (F-a) a symmetric
homoclinic point of γ. So

    ∂B ∩ ℓ ∩ D  =  cl( W^s(γ) ∩ ℓ ∩ D ),

and with the two ends, the whole capture edge on the start line is {x\*} ∪ {x_h} ∪ cl(symmetric homoclinic points in
(x\*, x_h)). No hyperbolicity of the trapped set is assumed: regular islands are allowed. Their boundaries are in ∂B
only as **limits** of W^s points, never as ends of plunging intervals.

**Why (lobe dynamics; MacKay–Meiss–Percival, Rom-Kedar–Wiggins).**
- D is bounded by pieces of invariant manifolds, so a point can leave D in one step only through the **exit lobe**
  L ⊂ D. P(L) lies outside D against the W^s side of ∂D. (This uses L2: P is a homeomorphism on D.)
- By L3 the first exit is final, so the sets D ∩ P⁻ᵏ(L) are disjoint, open, and cover B ∩ D.
- A connected piece I of B ∩ ℓ ∩ D therefore lies in a single P⁻ᵏ(L). Its endpoint e is not in B, so e lies on the
  boundary of that lobe preimage: an arc of W^u(γ) or an arc of W^s(γ).
- The open W^u arcs of the lobe boundary are on the transit side and plunge, so they are in B. Hence e is on a
  W^s arc, or is a corner (a homoclinic point). Either way e ∈ W^s(γ).

**The same hypotheses in geometric words (H1).** L2 and L3 hold if:
- **H1a.** γ is a brake orbit (both momenta vanish at its turning points in y), and its curve in the (x, y) plane,
  together with the zero-velocity curve, cuts the allowed region into an outer part (containing ℓ ∩ {x > x\*}) and an
  inner part (containing x = x_pl). Then nothing can go around the gate.
- **H1b.** γ is the only invariant set in the neck.
- **H1c.** Once through the gate inward, every orbit reaches x_pl without coming back.

### 1.5 What Theorem 2 implies for the §150 window

- **W-1. Finite horizon is not the problem for existence.** Take any pair of start points with different outcomes at
  horizon N (a "switch"). If both are in B they lie in different plunging intervals, or within a negligible distance
  (a factor λ^−(N − n) of the interval length) of one end. If one is trapped, the edge is between them. In every
  case **a true point of ∂B lies between or right next to the pair.** So each observed switch marks an infinite-time
  edge point at the resolution of the pair. Under Theorem 2 that point is in cl(W^s(γ)).
- **W-2. Cantor structure inside the window.** Suppose one symmetric homoclinic point x_w of γ lies in the window
  and is transverse (W^s there is neither along ℓ nor perpendicular to it). Then W^s(γ) accumulates on its own
  strand through x_w, and ∂B ∩ window contains a Cantor set. This needs only A2 and that one point.
- **W-3. Lifetimes.** On a plunging interval the lifetime is finite, changes in unit steps, and diverges at both ends
  like log(1/distance)/log λ. Where a strand crosses ℓ transversally the "margin" is linear in the distance.

### 1.6 Three meanings of "fractal edge", and which one the horseshoe gives

| | meaning | implied by the horseshoe? |
|---|---|---|
| **Fr-1** | ∂B contains a Cantor set of positive dimension | **Yes**, near x\* (Theorem 1). In the window: yes if W-2's point exists. |
| **Fr-2** | the lifetime function is singular on a fractal set | Yes, the same set as Fr-1. |
| **Fr-3** | the plunge-vs-never **outcome** has uncertainty exponent α < 1 as N → ∞ | **No.** See below. |

- Outcome uncertainty needs two outcomes of positive measure. A hyperbolic Cantor set has measure zero: where the
  trapped set is only that, almost every pair of neighbours both plunge, and the outcome exponent is not even defined.
- In the window the trapped set has positive measure only through regular islands and the regular core. So an
  infinite-time outcome exponent there is a property of the **island hierarchy** (a "fat fractal"), not of γ's
  horseshoe.
- §150's α at N = 300 is a hybrid: "survive" includes long transients that plunge later. Its small value
  (≈ 0.05) is the known signature of sticky, non-hyperbolic scattering (Lau–Finn–Ott), as §150 already says.
- **So even with the link proven, the correct upgrade is Fr-1 / Fr-2 wording, not "α stays below 1 for ever".**

---

## 2. What holds exactly in Kerr (the control)

- **Integrable.** Carter's Q is conserved, so Σ is foliated by curves of constant Q. At this (E, L) the unstable
  spherical orbit has r_sph = 6.2433047 (x\* = r_sph − m, m = 5/4) and Q_sph ≈ 18.1.
- **Separatrix.** W^s = W^u = {Q = Q_sph} minus γ. The outer branch is one homoclinic loop (Levin & Perez-Giz). The
  splitting is zero (§154 G2: ≤ 1e−13).
- **Radial polynomial at Q_sph.** R(r) = (E² − 1)(r − r_sph)²(r − r_a)(r − r_b). By Vieta,
  r_a + r_b = 2m/(1 − E²) − 2 r_sph. With §154's x_h this gives r_a ≈ 29.666 and r_b ≈ 0.149.
  - r_a is the apoapsis of the homoclinic orbit: **x_h is known in closed form.**
  - r_b lies inside the horizon (r₊ = 2.25), so R > 0 on (r₊, r_sph): **the gate is exactly one-way (H1c).**
- **Capture set.** An orbit survives iff Q > Q_sph and it sits in the outer radial well. So ∂B = cl(W^s), exactly.
- **On the start line** the edge is exactly **two points**: x\* (the fixed point itself) and x_h. Between them
  everything survives for ever; outside them everything plunges. Hence α = 1, as §150 measured.
- **Two kinds of edge point, with different precision floors.**
  - At x_h, W^s crosses ℓ transversally: the margin is linear in the distance.
  - At x\*, ℓ passes through the fixed point: the conserved margin is **quadratic**, ∝ (x0 − x\*)². An integration
    error of size tol then blurs outcomes over a width ~√tol. This is exactly the floor that voided the lifetime
    test, whose Kerr band sat at x\*.
  - Consequence for design: **use x_h, not x\*, as the Kerr control point.**

---

## 3. Where TS could break the link

| # | failure | what it breaks | how it would show |
|---|---|---|---|
| **B1** | **Return from inside.** TS δ = 2 has no regular horizon: a ring singularity, an ergoregion, possibly repulsive regions. An orbit could pass γ inward, turn round above x_pl = 1.5, and come back out. | L3 / H1c. The edge would then also carry the stable manifold of an **inner** invariant set, and would depend on the choice of x_pl. | an orbit with a crossing at x < x\* followed later by one at x > x\* |
| **B2** | **Bypass.** γ is not a brake orbit, or its curve does not span the allowed region. | L2 / H1a | the allowed region stays connected with γ's curve removed; the half-return map does not fix z\* |
| **B3** | **A second gate.** Another hyperbolic orbit with a whole unstable half-branch that plunges: an asymmetric twin pair S(γ') ≠ γ', or an inner unstable orbit. | H1b | a lifetime discontinuity whose bracketing orbits do **not** converge to γ |
| **B4** | **A2 fails:** part of W^u_in does not plunge. | Theorem 1 itself | a seed on the inward branch that survives |
| **B5** | **The window is sticky territory.** It sits at the outer rim of the chaotic layer, against the regular core. | Nothing in Theorem 2. But it breaks the *reading*: α there is set by islands and cantori (§1.6), and long-lived orbits amplify offsets by up to ~1e14, so their strands cannot be resolved even in double-double. | switches whose brackets cannot be refined before precision runs out |
| **B6** | **The test cannot fail.** If W^s strands are dense at the comparison tolerance, "the switch is within ε of W^s" is true for any point at all. | the Bridge's first suggested test, as worded | — |

B6 is the reason the tests in §4 never use distance to the manifold. They use a property of the orbit itself.

---

## 4. Cheap tests that could falsify the link

All use the validated double-double section map of §154 (about 0.04 s per TS crossing at R2). Each is a single
process, 1 thread, nice 10, and should take under 30 minutes; cost is measured on Kerr first. Every TS number they
produce is a TS chaos number and falls under the existing embargo.

### T-GATE: is γ a one-way gate that cannot be bypassed? (targets B1, B2, B4)

1. **Brake check.** Let H be the half-return map (up-crossing → down-crossing, reflected by S), so P = H∘H. γ is a
   brake orbit iff H(z\*) = z\*. Kerr: exact (r is constant).
2. **Separation.** Flood-fill the allowed region {W ≤ −1} on a grid with γ's curve as a wall: the window side and
   x = x_pl must be disconnected. Must-fail control: without the wall they must connect.
3. **Inward branch.** 64 seeds across one fundamental domain of W^u_in: all must plunge.
4. **Return census.** A grid of start points in a box around z\* (and every orbit computed in the other two tests):
   count orbits with a crossing at x < x\* − 1e−6 followed by a crossing at x > x\*. The link needs **zero**.
   Must-fail control: with the gate position moved outward by 1, the same counter must find returns.

**Falsifies:** L2/L3. Any return, any surviving inward seed, or a connected allowed region breaks Theorem 2 as
stated.

### T-BANDS: does the edge accumulate on x\* with γ's own scaling? (targets Theorem 1, B4)

- Start points x0 = x\* + d, with d on a logarithmic grid from 0.14 down to 1e−7, 96 points per factor λ.
- Record each orbit's **first-return fate**: T (plunges after exactly one outward excursion) or B (starts a second
  excursion).
- **Prediction.** For d ≲ 1e−2 the T/B pattern repeats with period ln λ in ln d, using §154's λ (no free parameter).
  Both fates occur. Each band edge is a two-loop symmetric homoclinic point of γ.
- **Kerr control:** no T at all (everything between x\* and x_h bounces for ever).
- **Falsifies:** if there are no bands, or the period is not ln λ, the structure at the fixed point is not γ's.

### T-SWITCH: is a window switch a strand of W^s(γ)? (targets B3, and W-2)

- **Certificate (the criterion; it does not use distance to any manifold).** Two start points p, q on ℓ **straddle a
  strand of W^s(γ)** if, at one common crossing index k, both are within 1e−2 of z\* (in γ's eigenframe), and then p
  plunges with no further excursion while q leaves outward. By continuity some point between them stays at γ for
  ever.
- **Procedure.** Take stored §150 switch pairs (neighbours 3e−5 apart with different status) in stored random order.
  Accept a pair if, in double-double, one member plunges within 60 crossings and the other outlives it by ≥ 24.
  Bisect on "plunges within n + 12 crossings" down to 1e−12. Classify the final pair:
  - **H:** certificate holds.
  - **A:** the lifetime passes smoothly through the cap (no discontinuity found).
  - **O:** a discontinuity with no approach to γ, stable between R1 and R2, even after refining to 1e−18.
    **O falsifies the link.**
  - **Unresolved:** R1 and R2 disagree (precision ran out; B5).
- **Controls, same code.**
  - Kerr at x_h: must give H, and the bracket must contain the closed-form x_h.
  - TS at x_h: must give H, and must contain §154's x_h (a cross-check between two engines).
  - Must-fail: a Kerr pair on the same side of x_h, and a Kerr lifetime step that is only one extra whirl, must NOT
    get the certificate.
- **Extra, for W-2:** for up to two certified strands, check that (x_w, ±η) in p_x also have opposite fates. Together
  with the sign change along ℓ this shows the homoclinic point is transverse.
- **Scope.** Only switches whose plunging member is short-lived are testable. The sticky majority may not be.

---

## 5. What each outcome would license

- **T-GATE passes, T-BANDS as predicted, T-SWITCH ≥ 1 certified transverse strand and no O.** Then, at this (E, L)
  level: "the capture edge on the start line contains the stable manifold of γ; a Cantor set of edge points
  accumulates on x\* and exists inside the §150 window (Fr-1). Numerical, not rigorous." The α values keep their
  finite-horizon wording.
- **T-GATE fails.** The link is not established and Theorem 2 is not available. Report which hypothesis failed.
  Theorem 1 may survive if A2 does.
- **Any O in T-SWITCH.** Another invariant set owns part of the edge. Report it; do not upgrade the window wording.
- **T-SWITCH all unresolved or all A.** No statement about the window. Theorem 1's statement near x\* stands on
  T-BANDS alone.
- **Never licensed here:** a claim about α in the infinite-time limit, about other levels, or about EMRI orbits.

---

## 6. Opus review

*(to be filled in after the review: each point, accepted or overruled, with the reason)*
