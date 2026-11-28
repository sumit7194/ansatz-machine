# C2-M P2: STOPPED AT THE VALUE GATE. The cost bar is projected to fail (12–26 h against 3 h); NO soundness verdict

**Ruling (the Bridge, value gate, option (b)):** stop P2 and record it; run C2-M on P3 as registered. Neon was not
asked, with the stated reason that the decision NOT to spend rests on a computed property of our own system (the zero's
clearance against the lasso), which no field practice changes.

**The stop:** SIGCONT, then SIGTERM, of the 6 PIDs logged at the pause (runner, cover, 2 in-flight cells), taken from
the pid file only. None was still alive after 3 s (`v7/guard_c2m_P2.log`). Lane B's sample process, which the P2 runner
had paused, was resumed. The partial cover (7 cells' records and logs) is archived in `c2/archive_c2m_P2_stopped/` and
is NOT reused without a ruling.

**The two points that matter most:**
- the clean split at a centre clearance of about 0.022;
- the boundary winding stays 1 (no crossing), so F is analytic on E_4.
The obstruction is CLEARANCE, not analyticity.

## History before the stop
Paused 2026-11-28 about 21:10 IST (the Bridge: the projected cost passed 12 h, so pause and inform).
**What was paused:** the C2-M P2 tree (the runner, the cover, and the 2 in-flight cells: 6 PIDs, from its pid file).
It was paused with SIGSTOP, which is lossless, and logged in `v7/guard_c2m_P2.log`. A resume continues the in-flight
cells exactly.

**Done so far:** 7 R/5 cells, of which 4 were REFUSED (L0_0, L0_1, L0_4, L0_5) and 3 were ok (L0_2, L0_6, L0_12 in
development). Every refusal is on the lasso, around edges 38–39, at CAPD's minimal step, after 10–14 minutes each.

**Projection:** about 12 h if roughly 60% of the R/5 cells refuse and half of their R/10 quadrants refuse; about 20–26 h
if most off-axis cells reach R/20. The registered bar is 3 h.

**Diagnosis** (design numbers, not certified: the v7B field at point k, Newton on G1 and G2, the distance to the lasso
polygon):
- At k_c, the lasso winds once around G2's upper zero (z about 1.8143 + 0.1425i), with a clearance of about 0.057.
- The zero moves with k, about 0.4 in z per unit k.
- Its clearance from the lasso at each cell centre: refused L0_0 0.011, L0_4 0.012, L0_5 0.018, L0_1 0.020; ok L0_2
  0.024, L0_6 0.032, the centre 0.057. A clean split at about 0.022. Inside an R/5 cell it sweeps about +-0.04 more.
- On E_4's boundary (32 points) the winding stays 1, so there is NO crossing and F stays analytic on E_4. But the
  minimum clearance is 0.0136; it is 0.025 on E_3 and 0.032 on E_2.

**What follows:**
- R/20 cells still sweep about +-0.01 against a clearance of about 0.014, and the cover's square reaches beyond E_4 at
  its corners, where the clearance is smaller still. So an R/20 STOP at the corners is likely.
- For C2-TM, predicted before its probe: G2's reciprocal theta on the lasso is about sweep/clearance. That is about 0.2
  for the sub disc (it should pass) and about 0.8 for the whole disc (the guard should refuse).

**The options that went to the Bridge's value gate** (it chose (b); (c), the redrawn lasso, is to be drafted only
after the TM sub-disc probe, for a ruling):
- (a) resume as registered;
- (b) stop and record it (recommended), then run C2-M on P3, whose box is about 100x smaller;
- (c) later, a new mechanism: a smaller rho, or a redrawn lasso with uniform clearance.
