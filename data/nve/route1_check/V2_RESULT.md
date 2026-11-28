# v7 stage V2: result. PASS at spin 3/5 (T1'–T4' pass, the non-author read's issues fixed and re-tested)

**Office ansatz-machine (Claude Opus), 2026-11-28.** The registration is `V7_REGISTRATION.md` with addenda 1–4.
- **Code:** at 12b1f50. The segment certifier is v7 = v6 plus the c0 field (`_nve_route1_segment_v7.py`,
  `_nve_v7_field.py`, `_nve_v7_c0.py`).
- **The registered run:** launched 2026-11-28 15:35:15 as PID 50245, under the fixed code's content hash
  (`v7/v7_t1r.log`). Prove, then verdict with full controls, then the engine gate. Exited rc 0 at 15:56:02.
- **Environment:** Mac mini, nice 10, under the pause-only guard, which never paused.
  - Arb side: `.venv313`, Python 3.13.12, python-flint 0.9.0, FLINT 3.6.0.
  - Engine: `.venv`, Python 3.14.5, mpmath 1.3.0.

**Grading (disclosures, part of the verdict):**
- The non-author read found two VACUOUS controls and three DOUBTFUL points. All were fixed under addendum 4 and
  re-tested before this run.
- **The F1b control's plant was corrected after it first failed to fire:** it corrupted a duplicate cached state that
  the next query did not use. It now corrupts every cached state.
- **The pre-fix development run's T1' numbers were seen before the registered run.** That run (15:22:50, the pre-fix
  content hash) gave M_F 2.425e4, n 12, a certified verdict and engine 13/13. The registered criterion, 2× of v6, was
  frozen before either run.

## T1'–T4' at spin 3/5, k ∈ [1, 11/10], against v6 on the same segment (production log, air_prod_3_5)

| | v6 (production) | v7 (this run) | within 2×? |
|---|---|---|---|
| verdict | CERTIFIED | **CERTIFIED** | |
| M_F (ρ = 4) | 2.438e4 | 2.425e4 | yes (0.99×) |
| n | 12 | 12 | yes |
| error bound on F | 1.938e−3 | 1.928e−3 | yes |
| \|F\| ≥ | 0.263396557 | 0.263406948 | (tighter) |
| tr M0 error bound | 1.795e−7 | 1.754e−7 | yes |
| tr M1 error bound | 3.078e−6 | 3.080e−6 | yes (1.0007×) |
| circle / lasso steps | 2163 / 703 | 2133 / 701 | |
| time | segment total 1314 s (Air) | prove 217 s; whole run 21 min with full controls and engine (Mac mini) | |
| peak footprint | 33 MB | 44 MB prove, 134 MB verdict | under 0.2 GB |

- **T1': PASS.** It certifies, with every bound within 2× of v6's; all are within 1%.
- **T2': PASS.** The engine gate had 13 of 13 node values inside their enclosures. The engine gate is `scripts/_nve_route1_engine_gate.py`, **unchanged from v6** (its sha256 equals the one in `MANIFEST_PROD.sha256`). The engine computes c0 by its own
  mpmath Laurent series, so the two implementations no longer share the c0 formula (registration §3(b)'s
  common-mode risk is removed).
- **T3': PASS.** The planted zero was refused, the held-out nodes broke nothing, the shrunken M was caught by the
  sampled-maximum check, and the planted precondition at k = 4.2 fired. (Under v7 the precondition is the
  circle-picture condition: a c0 branch point lies outside R0 − 0.1 there.)
- **T4': PASS.** v7's checkpoint, node and verdict files carry v7's own content hash. No v6 record was read: the
  run's 24 node evaluations were all new.
- **The non-author read:** every issue was fixed and re-tested (addendum 4: V1 re-tested in full at both spins, PASS;
  the F1b control PASS).
- **F1b gate:** 12,131 step checks and 73,684 dq-series checks in prove, and 291,150 step checks in the verdict, none
  firing. A clean field passes the F1b control, and a corrupted branch fires it.

**V2 at spin 3/5: PASS.** Next: P-B (the region-B port, the premortem's check). Per the registration, V2 has not been
run at 9/10. V1 passed there, and the gate holds per spin.
