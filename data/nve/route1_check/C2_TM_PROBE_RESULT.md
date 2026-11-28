# C2-TM probe: FAIL on both registered sub discs (P2 and P1). By the registration, no C2-TM pilot runs
**Run:** `air/c2tm_probe.sh P2|P1 sub`, once each, at a3c5f56 (C2_TM_REGISTRATION.md; controls T3–T5 in
C2_TM_CONTROLS.md; read in C2_TM_READ.md). The disc circumscribes step 0''s centre R/5 sub-box, rho = sqrt2 hs
(1 + 2^-10), with degree 12. The covering is certified, and T1 and T2 (the plant caught) hold on both.

| | P2 (region B) | P1 (circle) |
|---|---|---|
| tr M0 (Gamma / circle): sup / sampled max | 0.02040 / 0.01961 = 1.04; e 3.8e-7 | 1.8034 / 1.8014 = 1.001; e 7.0e-12 |
| tr M1 (lasso): sup / sampled max | 1.3e29 / 2.19 | 9.4e3 / 2.28 |
| F: sup / sampled max | 2.3e59 / 4.32 | 1.9e8 / 15.4 |
| every sample contained (T1); T2 caught; c0 closure | yes; yes; yes | yes; yes; yes |
| cost (time per disc x 25 / 2 cores) | 9.0 h | 14.9 h |
| verdict | FAIL | FAIL |

**Where it failed (the eps-per-edge log, registration edit 3):**
- The closed loops (Gamma, the circle) end with remainders of 1e-7 and 1e-12: the TM machinery is essentially exact
  there (sup/max = 1.04 and 1.001).
- On the LASSO the remainder grows on the return leg after winding round its singular point: P2 1.7e-2 at edge 25,
  4.5e14 at edge 45, then about x10 per edge to 1.6e28; P1 8e-12 at edge 20, 1.1e-2 at edge 45, 7.4e2 at edge 51.
- This is the risk the registration named (remainder accumulation along the loop). A likely mechanism, design
  guidance only, not diagnosed: near the singular point the point-kc fundamental matrix C used for preconditioning is
  ill-conditioned (a growing and a decaying solution), so C^-1 (...) C amplifies the dk-part.
- None of the named reserve amendments matches it: (ii) is for c0's remainder round the circle, (v) is for a tripping
  theta-guard, and the Gamma deformation is for the z-direction binding. A fix (for example QR preconditioning of W,
  or the redrawn lasso with uniform clearance) is a new mechanism that needs a ruling.
- **Cost fails independently** at sub-disc size: 9–15 h per segment against the 2 h bar.

**Predictions against the outcome:**
- the theta-guard holds on the sub discs (theta about one fifth): it did (no guard refused);
- the probe passes at rho = sqrt2 hs (40%): it did NOT;
- cost met (55%): NOT;
- the P2 whole disc was not run (it requires the sub disc to pass).

## Re-gate (A): does named reserve (ii) match the failure? NO, so C2-TM is STOPPED
The Bridge asked whether reserve (ii), QR or parallelepiped preconditioning, matches my reading of an ILL-CONDITIONED
point-kc preconditioner near the singular point. I tested that reading before answering, and it is **refuted**:
- Along both lassos at kc (a point walk with step records, P2 628 steps, P1 677 steps), the fundamental matrix's first
  row stays small, |Y| <= 6.5 at P2 and 6.6 at P1.
- With det = 1, cond(C) is about |Y|^2 <= 43. So C is well conditioned, and C^-1 (...) C cannot amplify by more than
  about 43.

QR preconditioning cures ill-conditioning; the measured growth is about 1e30, not about 43, so (ii) does not address it.
Independently, the probes FAIL the cost bar (9.0 h and 14.9 h per segment against 2 h) at the sub-disc size, and a QR
frame changes neither the step count nor the TM operation count. So even a perfect remainder fix could not make the
registered probes pass with the same bars. **(ii) is not used, and C2-TM is STOPPED.**

**The real mechanism of the lasso's remainder growth is NOT diagnosed** (my earlier reading was wrong; recorded as
such). A diagnosis would need per-step logging of which TM operation's e grows (the reciprocals near G2's zero, the
majorant tail, the B(.) bound inside the products). That is not pursued without a new ruling.
