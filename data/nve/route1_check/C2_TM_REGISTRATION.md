# C2-TM registration: an Arb Taylor-model layer in dk (the registered fallback (A)). Committed BEFORE any C2-TM code
**Office ansatz-machine, 2026-11-28.** GO from the Bridge's final C2 ruling, after the Neon outside view.
- It is THE route for P1 (the circle), and for P2 and P3 only if C2-M (`C2_M_REGISTRATION.md`) fails there.
- C2-M uses the compute first; the TM code may be written meanwhile, at no compute cost.
- The C2 time box stands: STOP by 2026-12-12 if no pilot certifies.

## Why (from step 0' and step 0'', `C2_STEP0P_RESULT.md`, `C2_STEP0PP_RESULT.md`)
- CAPD's first-order doubleton keeps the dk-LINEAR part (C r0) tight, but everything beyond first order goes into an
  interval remainder.
- Near G2's zeros, q ~ 1/G2^2 turns that interval width (of c0) into a wide interval for q, and Y' = A(q) Y wraps
  exponentially. P2: ln(width of F) is 135, 32, 16.5 for R/5, R/10, R/20. P1: c0's width accumulates round the circle.
- **The TRUE k-sensitivity is tame.** Step 0 sampled |dq/dk| at about 11 at P2. A design probe for this draft
  (8-point samples, the v7B field, not a certificate) puts G2's relative variation over a k-disc at Gamma's worst
  vertices (|G2(kc)| about 0.013) at theta = sup|G2(k) - G2(kc)|/|G2(kc)|: about 0.18 for rho = R (the whole box),
  0.09 for R/2, and 0.04 for R/5.
- So the amplification is of an OVERESTIMATE, not of a genuine variation. A representation that carries c0(k), G2(k)
  and q(k) as polynomials in dk, never as intervals over k, does not form the width that 1/G2^2 amplifies.
- **The 8-point theta numbers are DESIGN GUIDANCE ONLY** (point samples, not enclosures). What certifies is the
  run-time theta-guard of every reciprocal and sqrt (Design 2), evaluated rigorously on each TM.

## Design
**1. The object: a univariate COMPLEX Taylor model in dk.** Everything is analytic in k, so one complex variable
suffices, not two real ones.
- A TM is (p, eps): p an acb_poly of degree <= d in dk, eps an upper bound, with
  |f(kc + dk) - p(dk)| <= eps for all |dk| <= rho (a disc).
- The arithmetic is truncated at degree d, and the dropped products are bounded into eps by sum |coef| rho^j.
  python-flint's acb_poly is used for the polynomial part; the remainder logic is our own.

**2. Operations, each with a stated remainder rule and a precondition that refuses:**
- +, -, x and scalar multiplication;
- the reciprocal 1/T: with T = T0 (1 + u), it requires theta = sup_disc |u| <= 1/2 (certified by the sum of |coef|
  rho^j bound), and then 1/(1 + u) = sum_{m<=d} (-u)^m + a remainder <= theta^(d+1)/(1 - theta), times 1/|T0|;
- the principal sqrt for s (C2-4's closed form): sqrt(A0 (1 + u)) with |u| <= 1/2 and A0 certified off the cut, by
  the binomial series plus a remainder;
- the off-cut and disc guards of C2-4, carried over unchanged.

**3. The start, as a TM in dk:**
- P (the start-integral polynomial of `_nve_v7_c0.py`) is linear in k: P = P0 + P1 dk.
- So sqrt(P) = sqrt(P0) sum_j binom(1/2, j) (P1/P0)^j dk^j, exactly, under |P1/P0| rho < 1. That is certified per s on
  the s-balls, with a geometric tail.
- Each dk-coefficient of c0(zb) and c0'(zb) is then a 1-D Arb integral like V1's start (validated machinery). The
  remainder is the tail of the binomial series, bounded uniformly on the s-balls.

**4. The walk:** v2's z-Taylor step (`_nve_route1_segment_v2.py` `step`), with every coefficient a TM instead of an
acb ball:
- the z-series of c0'' (now pref s(z, k)/(z^2 + a^2)^3 with s from (2)), integrated twice;
- f0, G1, G2, lambda and q as z-series with TM coefficients;
- Y's recurrence.
- The z-tail bound: v2's majorant |v_j| <= K mu^j, with Q >= sup |q| over the z-box x the k-disc, from q's TM
  evaluated on the z-box: sum_j |a_j(Zbox)| rho^j + eps. Only a MAGNITUDE bound, so no dq/dk.
- The step sizes and the loops are unchanged (the floats entries, Gamma, the lasso, the circle), and so is the walk's
  rho-halving.

**4b. Preconditioning of Y by the point-kc flow (Neon's recommendation (i), registered now, before code).**
- For each loop, a point walk at kc (the same steps) gives each step's transfer T_i(kc), and with it EXACT midpoint
  matrices C_0 = I, C_{i+1} = mid(T_i(kc) C_i) (exact binary points).
- The TM walk carries W_i(dk) with W_0 = I and W_{i+1} = (C_{i+1}^-1 T_i(dk) C_i) W_i, so Y_i(dk) = C_i W_i(dk) and the
  monodromy is M(dk) = C_N W_N(dk).
- **This is an exact algebraic identity for ANY invertible C_i, so rigour does not depend on C_i's accuracy.**
  C_{i+1}^-1 is the exact adjugate of a point matrix divided by its determinant, enclosed in Arb, with the determinant
  certified nonzero.
- Each factor C_{i+1}^-1 T_i(dk) C_i is I + O(dk) + a small step error. So W's remainder grows like the product of the
  norms of near-identity factors, not like the product ||T_i||. That keeps the kc-flow's stretching out of eps, which
  is the named risk.

**5. Output and covering (Bridge edit 2: covering is computed, not assumed):**
- M0 and M1 entries are TMs, F = tr(M1 M0 M1^-1 M0^-1) - 2 with the adjugate inverse, and tr M0, tr M1 likewise.
- sup|F| over a k-disc <= sum |f_j| rho^j + eps.
- **The region to cover is E_rho.** For the segment k_c +- half (rho = 4), the Bernstein ellipse has semi-axes
  a_e = half (rho + 1/rho)/2 = R along the real axis and b_e = half (rho - 1/rho)/2 = (15/17) R along the imaginary
  axis. So E_rho lies inside the disc |dk| <= R, touching it only at dk = +-R.
- **One disc for the whole box:** radius rho_k = R (1 + 2^-10), the margin covering the touching points with room.
- **Discs for sub-boxes:** each of the 25 closed sub-boxes of v2's kbox (half-side hs = R/5) gets the disc
  circumscribing it, radius sqrt 2 hs (1 + 2^-10), centred at the sub-box centre.
- **Checked in code, in Arb, before any walk:**
  - the one-disc case: every point of E_rho is inside, certified on the parametrised boundary
    a_e cos t + i b_e sin t, t covered by balls, with |dk|^2 <= rho_k^2 - margin;
  - the sub-box case: every corner of every sub-box lies strictly inside its disc, and the 25 sub-boxes cover the
    square box, which contains E_rho (v2's kbox asserts).
  A failure stops the run before it starts.
- M_F, M_T0 and M_T1 are the maxima over the discs; ATAP unchanged.
- **Remainder logging (Bridge edit 3):** the walk records eps (the largest remainder over the state's TMs) at the end
  of every EDGE, along Gamma or the circle and along the lasso, in the probe record. If the probe fails, the record
  then shows where the remainder grew, and whether deforming Gamma, or something else, is the right amendment.

## Question for the Bridge (asked to be put here)
**Does a single higher-degree TM over the whole box beat sub-boxing near |G2| about 0.01, or does the 1/G2^2 factor
need its own treatment (a rescaled variable, or splitting Gamma away from G2's zeros)?**

**My answer from the design probe above, for you to check:**
- In this design 1/G2 is a TM reciprocal, whose convergence is governed by G2's relative k-variation theta, not by
  |G2| itself. At Gamma's worst vertices theta is about 0.18 over the whole box (rho = R), so the reciprocal converges
  like 0.18^(d+1) (about 1e-7 relative at d = 8), and q = (3/16) lambda^2 follows. So in the k-direction, raising the
  degree should suffice, even with ONE disc.
- The 1/G2^2 factor still matters in the z-direction: small z-steps and a large Q in the tail bound. But the point-k
  walk already handles that at about 20 s per k for both loops, and the TM walk inherits the same z-steps.
- **The genuine risk is not 1/G2^2 but remainder accumulation along the loop.** Each step's eps is propagated
  linearly through Y, whose transfer norm along Gamma and the lasso can be large, so eps grows roughly like the
  product of the step transfer norms. That is the TM analogue of wrapping, but without the interval-over-k width that
  CAPD amplified.
- Deforming Gamma outward to raise min |G2| is a second lever. The monodromy is homotopy-invariant if the deformed
  loop stays in the same class for every k (the closure, precondition and free_square machinery). I would hold it in
  reserve, for amendment ONLY if the probe shows the z-direction binding.

## Controls (each must be able to fail; each recorded with the guard that refused)
- **(T1) positive check:** the TM of F, tr M0 and tr M1, evaluated at each of the 81 grid points of the probe disc
  (the step 0' R/5 grid), must CONTAIN the point-walk node value there; and eps must be <= 1e-3 x the sampled max |F|
  (not vacuous).
- **(T2) a guaranteed-fail plant on the checker (Bridge edit 1).** At ONE grid point the TM's value is shifted by
  10 x (eps + the node value's ball radius) before T1's containment test. It MUST be caught at that point; if it is
  not, the containment checker is not testing anything. This can fail only through a defect in the checker, never on
  a correct but loose build.
  - **Reported, not pass/fail:** the TIGHTNESS ratio, the largest eps/1e6 that still contains every node; equivalently
    min over nodes of (eps - |p(k_i) - node_i| + rad_i)/eps. It says how loose eps is.
- **(T3) reciprocal precondition:** a planted theta >= 1 (rho planted at 10 R) must be REFUSED by the reciprocal's
  theta-guard (the refusal message names the guard), not by an incidental one.
- **(T4) start TM, with a tolerance from the method (Bridge edit 4).** At the base point zb:
  - the first-order coefficient of c0 and c0' is compared with the central difference
    D1 = [f(kc + h) - f(kc - h)]/(2h), where f is V1's point start and h = rho/4. The error is
    |D1 - f'(kc)| <= h^2 sup|f'''|/6 + (rad f(kc + h) + rad f(kc - h))/(2h);
  - the second-order coefficient is compared with D2 = [f(kc + h) - 2 f(kc) + f(kc - h)]/h^2, whose error is
    <= h^2 sup|f''''|/12 + the ball radii/h^2;
  - **sup|f'''| and sup|f''''| over [kc - h, kc + h]** come from a SEPARATE Arb integral of the explicit k-derivatives
    of the start integrand. P is linear in k, so d^3 sqrt P/dk^3 = (3/8) P1^3 P^(-5/2) and
    d^4 sqrt P/dk^4 = -(15/16) P1^4 P^(-7/2), integrated with the start's weights on the s-balls, with k as a ball
    over the FD interval. That integral is independent of the TM coefficients being tested;
  - PASS: each coefficient's ball, widened by its error bound, overlaps the FD value. Plus a must-fail plant: the
    first-order coefficient planted x1.01 must be outside the tolerance (if it is not, the tolerance is too loose to
    test anything).
- **(T5) a loop crossing a G2 zero inside the disc (Bridge edit 5).** A k-disc is placed so that, for some k in it, a
  G2 zero lies ON a Gamma edge (a disc centred where Gamma's nearest G2 zero is closest to Gamma; its radius is the
  computed k-distance at which the zero crosses, plus margin).
  - **EXPECTED refusing guard:** the reciprocal theta-guard on 1/G2 in the z-tail bound's q-magnitude (theta >= 1/2
    where G2 at kc is small relative to its variation over the disc).
  - It is recorded whether it was that guard or another (for example the z-box domain guard). As with K2s, a refusal
    by a different guard is reported as "refused, not as specified", and the test is not loosened afterwards.

## Probe (the hard gate, by 2026-12-04)
- **What (Bridge ruling: the P2 disc plus ONE P1 disc):**
  - **P2 (k_c 83/20):** the disc circumscribing step 0''s centre R/5 sub-box, rho = sqrt 2 hs (1 + 2^-10); and, if
    that passes, also rho = R (1 + 2^-10), the whole of E_rho in one disc. Each judged.
  - **P1 (k_c 79/20, the circle):** the disc circumscribing step 0''s centre R/5 sub-box, rho = sqrt 2 hs (1 + 2^-10),
    judged against the step 0' P1 R/5 grid samples.
  - **A pilot runs only on a box whose probe passed.**
- **The probe record includes** eps per edge for every loop (edit 3), and T2's tightness ratio (edit 1).
- **Bar (unchanged from C2-3):** finite; contains every sampled value (the reused step 0' grids); sup|TM| <= 100x the
  sampled max |.|, for F, tr M0 and tr M1.
- **Cost bar:** (time per disc) x (discs covering E_rho) / 2 cores <= 2 h per segment.
- **Degree: d = 12**, fixed now, with no tuning after the numbers. Neon recommended 12–16 over 8: with theta <= about
  0.2 over the whole box (design guidance), theta^13 is about 1e-9 per reciprocal, at about (13/9)^2, roughly 2x,
  d = 8's cost per operation.
- **Outcomes:**
  - PASS: the pilots P1, P2, P3 once each, by 12-12;
  - FAIL, or not run by 12-04: STOP, and the top is parked at numerical grade.

## Reserve amendments (named now; used ONLY if the probe's eps-per-edge log shows where; graded "post-failure" if used)
- **(ii)** QR or parallelepiped preconditioning of the c0/c0' remainder, if c0's remainder grows round the circle
  (Neher, Jackson and Nedialkov 2007).
- **(v)** sub-discs of about rho/2, if a reciprocal's range bound trips the theta <= 1/2 guard.
- Deforming Gamma outward, if the z-direction binds (as before).
Each needs its addendum committed before the re-run, and only ONE post-failure amendment per failure.

## Provenance of the outside view
The Neon answer, relayed by the Bridge, which checked the citations at source (Crossref/arXiv):
- Taylor models are the field's standard for parameter-uniform enclosures: Berz and Makino 1998,
  doi:10.1023/A:1024467732637; Neher, Jackson and Nedialkov 2007, doi:10.1137/050638448; Buenger 2020,
  doi:10.1016/j.cam.2019.112511.
- No off-the-shelf tool does parameter-uniform monodromy in the complex domain.
These are NOT read here. The design's soundness rests on its own remainder rules, the exact preconditioning identity
(4b), and the controls and read, not on the citations.

## Order
1. Registration, committed.
2. Code: the TM class, then the walk port, then the start.
3. A unit self-test of the TM arithmetic against mpmath at random points.
4. A non-author read (TM remainder rules, the reciprocal and sqrt guards, the z-tail bound with TM coefficients).
5. Controls T1–T5.
6. Probe.
7. Pilots.
Every addendum is committed before the run it governs.

## Predictions (to be recorded at registration)
- the TM reciprocal guard holds over the whole box on Gamma (theta <= 1/2): 80%;
- the probe passes at rho = sqrt 2 hs: 40%; at rho = R as well: 25%;
- the cost bar is met: 55%;
- a pilot certifies by 12-12: 20%.
