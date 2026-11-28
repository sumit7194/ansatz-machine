# C2-M P3: CERTIFIED (the first C2 pilot to certify). Region B, spin 3/5, k_c = 59979/14000 (about 4.284207), half 1/2000
**Claim, certified for EVERY real k in [k_c - 1/2000, k_c + 1/2000]:**
- F(k) != 0;
- tr M0(k) != 0;
- tr M1(k) is not in [-2, 2].

M0 is the region-B Gamma loop and M1 the lasso (`route1_floats_v7B_3_5.json`, entry 59979/14000).

**Run:** `air/c2m_pilot.sh P3`, once, at b02a2ee (C2_M_REGISTRATION.md, addendum C2-M-1, erratum C2-M-2), from 2026-11-28 21:07:55
to 2026-11-28 22:31:34. Driver v2 (C2-4, IdQR). The code hash covers the driver binary and is in `v7/c2m_P3.log`.

**Grade line:** post-failure, informed by step 0'''s widths; the bar change is efficiency-only, and the certificate's
soundness is unaffected (C2-M registration). The C2 chain behind it: step 0' FAILED; C2-4 was the post-failure fix;
step 0'' FAILED; C2-M was ruled by the Bridge.

## Every gate of addendum C2-M-1
| gate | result |
|---|---|
| M3 (dry: every accept() refusal branch takes refinement; R/20 STOP) | FIRED, all 5 modes, and the STOP |
| cover: 25 R/5 cells, refinement rule | 31 leaves of 33 cells (2 cells refined to R/10, all 8 quadrants accepted), no STOP; every leaf shows H1–H4 |
| M = max over the leaves | M_F 3.507e6, M_T0 0.6032, M_T1 484.4 |
| M1 (containment of 31 new point values, one per leaf) | PASS, all contained |
| verdict, v6 with full controls (n = 14 from v5's formula, rho = 4) | **CERTIFIED**, no ALARM |
| v6's own controls | held-out consistent; proved M >= sampled; planted zero refused; planted precondition fires; the shrunken M breaks it |
| M2F, M2T0, M2T1 (M planted at 0.5 x the sampled max) | each ALARMed: "proved M below a sample" |
| M4 (a planted F-node radius of 1e-2) | tripped the node-precision assertion (the unplanted verdict passes it) |
| engine gate B (the HP engine) | 20/20 node values inside their enclosures |

**The certified margins:**
- |F| >= 2.8456 against F's error bound 1.743e-2;
- |tr M0| >= 0.0033003 against 2.996e-9;
- |Im tr M1| >= 0.71235 against 2.406e-6;
- the largest node radius is 7.9e-7.

**Cost against the 3 h bar:** CAPD 6613 s / 2 cores (about 55 min), the nodes (26 evaluations), and M1 (31 evaluations, about
17 s each) come to about 1.1 h per segment, so the bar is met. Total wall time for everything, the controls included:
the start and end times above.

**Reading:** the C2 time box is met (at least 1 pilot certified by 2026-12-12). Per the C2 registration's table,
"1–2 certified: partial: report and re-gate". P2 was stopped at the value gate (C2_M_P2_RESULT.md); P1 (the circle) is
out of C2-M's scope, and its C2-TM probe failed (C2_TM_PROBE_RESULT.md).
