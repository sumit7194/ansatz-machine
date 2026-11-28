# C2-4 must-fire controls (Bridge condition 3): the record. 2026-11-28, run at 1d2a4cf (erratum E2)
Runner: `scripts/_nve_c2_c24_controls.py`; record `c2/c24_controls.json`; per-control files `c2/step0pp_*_K*`. Each
control must be refused by ITS OWN guard (matched on the refusal message).

| control | what it plants | refused by | verdict |
|---|---|---|---|
| K1, P2 | -s0 handed to the (a3) start match | "(a3) the closed-form root does not match the field's branch at the start" | **FIRED** |
| K1, P1 | the same, circle form | (a3), as above | **FIRED** |
| K2, P2 | a segment from bB across B's cut (B = -20 at tau = 1/2) and back | "(a1) root argument not certified off the cut on this edge" (a priori, before any step) | **FIRED** |
| K3, P1 | circle disc radius 0.01 | "(a2) … on this edge" (a priori) | **FIRED** |
| K4, P2 | a non-point time on every attempt (E2) | "(b) no step with an exact time above the minimal step" | **FIRED** |
| K3s, P1 (read F2) | K3 with the a priori guard skipped | "(a2) … on the whole-step enclosure" (the per-step guard) | **FIRED** |
| K2s, P2 (read F2) | K2 with the a priori guard skipped | CAPD: "High Order Enclosure Error: minimal time step reached", at tau = 0.378 on the planted edge | **REFUSED, NOT as specified** |

**All four registered controls (K1–K4) FIRED**, on both boxes where K1 applies.

**K2s, reported as it is.** The box was refused, so a cut crossing was not accepted. But the refusal is neither the
per-step (a1) guard nor the CAPD sqrt/division-by-zero text that the re-read's tightened test asks for, so by the
registered test it did NOT fire. It is not loosened after the fact.

**Diagnosis (the step log plus an Arb probe of the planted edge):**
- Along the edge, |B| + Re B falls from 418 (tau 0) to 44 (0.30), 13 (0.378) and 0 at the crossing (tau 0.5).
- B's zeros stay about 0.7 away.
- At the stall the singular-point margins are healthy: |z^2 + a^2|^2 about 0.78, |G1|^2 about 5, |G2|^2 about 3.
- The c0' block's width explodes, 1.5 -> 12.7 -> 296 -> 1e5, while the steps shrink to 1e-12.
- Over the R/5 k-box, B's range nears the cut before it does at kc0, and the real-variable principal-root formula's
  derivatives blow up near the cut (re ~ sqrt(|B| + Re B)), so CAPD's Taylor step collapses before the per-step guard
  can be reached.

**What this shows and what it does not:** the cause is the cut, through CAPD's own step collapse, and a cut crossing
cannot be accepted. It does NOT exercise the per-step (a1) guard. The read found that guard redundant: the a priori
guard is sound on its own (K2), and the per-step plumbing is exercised by K3s's (a2) branch. The "second accept
condition" of E2 (an exact time with an inexact remainder) has no control of its own; that is minor, per the re-read.
