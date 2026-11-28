# C2-AN item 1, the circle-picture loop chain at spin 3/5: CHAIN CERTIFIED (2026-11-29)
**Run:** `air/v7_job.sh c2an_chain … _nve_c2an.py run`, once. It ran at d6fde56 (C2_AN_REGISTRATION.md with addenda C2-AN-1 and C2-AN-2, after the non-author read C2_AN_READ.md). One core, nice 10, pause-only guard (no pause). Wall time 691 s, against the 3 h bar. Records: `c2/c2an_chain_3_5.json` and `v7/c2an_chain.log`.
**Environment:** Mac mini, `.venv313` (python-flint, Arb), ctx.prec 256.

## Result
**For every real k in J = [2.895, 4.005], at spin 3/5 and E = 4/5:**
- **(a)** the circle polygon (route (i)'s 96-gon, R0 = 1.35) and **(b)** the link's capsule lasso are covered by boxes on which G1, G2, B(z²/a², k) and z² + a² are certified nonzero, with c0 continued along each word from R0;
- **(c)** Re P > 0 on [0, 1/R0], so the normalisation from +∞ is analytic in k;
- **(f)** the circle's lift is closed: every singular point of c0″ lies inside the polygon. Each lasso lies in the certified single-valued square;
- **(d)** on every overlap O_i, the based straight-line homotopy L_i → L_{i+1} sweeps only certified-nonsingular boxes.

| | cells | refinement | min clearance of the lasso from r+ / p+ (float diagnostic) |
|---|---|---|---|
| 11 links (59/20 … 79/20) | 121 | none (all at level 0) | from 0.148 / 0.143 at 59/20, falling to 0.082 / 0.070 at 79/20 |
| 10 gluings | 10 | none | — |

**Controls** (after the read's fixes): K1, K1c, K2 and K3 each refused through its named guard (`c2/c2an_control_*.json`).
**Registered predictions:** (a)–(c) for all 11 links, 75%: held. (d) for all 10 overlaps, 85%: held. The controls as specified, 90%: held. Within the bar, 80%: held.

## What this establishes, and what it does not
- **It establishes the analyticity hypothesis of the design note (v2, §1.2–1.4).** The circle-picture based pair (M0, M1) continues as ONE family over J, with closed lifts. So F, tr M0, tr M1 and P_fin(tr M1) are each holomorphic on one connected complex neighbourhood of J.
- **J contains route (i)'s certified segment [2.9, 3.0],** where link 0's words are route (i)'s exactly. So none of the three conditions vanishes identically, and D ⊂ [3, 4] is finite **by the design note's argument**.
- **That argument is still under the hostile re-read.** The lemma (item 3) is not written into MRS_SECTION.md until the re-read verdicts are in. So this record is the certificate of a HYPOTHESIS. It is not yet the theorem.
- **It certifies no monodromy value.** D is not shown empty; the numerical counts say it is, but they are floating point.
