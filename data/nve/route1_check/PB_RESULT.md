# v7 stage P-B: result. PASS at spin 3/5 (region-B loops in Arb with the v7 c0; the premortem's check)

**Office ansatz-machine (Claude Opus), 2026-11-28.** The registration is `V7_REGISTRATION.md` (P-B, deadline day 14).
- **Code:** `scripts/_nve_v7_pb.py`, committed before its run (142e113). The engine's span-rule fix and the runner were
  committed before the Arb run.
- **Runs:**
  - engine mode under `.venv` (Python 3.14.5, mpmath 1.3.0, 50 digits; HP engine NC_B 220, RATIO_B 0.6);
  - Arb mode under `.venv313` (Python 3.13.12, python-flint 0.9.0, FLINT 3.6.0), launched 16:02:25 as PID 98530,
    rc 0, 32 s. Mac mini, nice 10, under the pause-only guard.
- **Outputs:** `v7/pb_engine_3_5.json/.out`, `v7/pb_arb_3_5.json`, and `v7/v7_pb.log`.

## Design
- **Geometry, by the registered rule:** r+ and p± are tracked from Kerr's points to the endpoint, then back to each
  target. Z0 = 2 (as in §162 and the closure check). bB = max(Re r+(endpoint) − 0.3, a + 0.08) = 1.5008. The loops
  are `HalfB.loops`, a capsule lasso around [r+, p+] and the Γ disc, both based at bB.
- **Engine guards:** all pass at both nodes (ratio 0.245 against 0.6; cut_ok with the run-mode span, the loops' reach
  + 0.05 = 0.352).
  - The first engine pass used span 99, which made cut_ok examine a huge region and read False. The engine values do
    not depend on the span. It was corrected to the registered rule, and the values were unchanged.
- **The Arb side:**
  - FieldB: c0 from V1's C0, started at the real base bB and continued only inside |z − Z0| ≤ 0.9 R_c, with R_c a
    certified lower bound (2.035 at 4.2; 2.030 at 30/7 − 1e−6);
  - a v7-native step: the c0'' series comes from the field's carried √B branch, certified against it at each step;
    v2's c_K''√(1 − kφ) is not used;
  - v2's walk, monodromies and traces otherwise unchanged.

## Measured

| node | quantity | Arb value | radius | ≤ 1e−3 \|value\| | engine inside |
|---|---|---|---|---|---|
| k = 4.2 | F | −1.1660434 − 3.4525651i | 2.4e−8 | yes | yes |
| | tr M1 | −1.91054666218 + 0.90355425482i | 1.1e−12 | yes | yes |
| | tr Γ | −0.013355457005 | 1.9e−13 | yes | yes |
| k = 30/7 − 1e−6 | F | −0.737256 − 2.769026i | 1.6e−7 | yes | yes |
| | tr M1 | −1.94191878071 + 0.71296134208i | 2.1e−12 | yes | yes |
| | tr Γ | −0.003116881397 | 2.0e−13 | yes | yes |

There were 2617 native steps (lasso and Γ: 624 + 675 at 4.2, 639 + 679 near 30/7), at about 16 s per node.

**P-B at spin 3/5: PASS.** The premortem's worry, enclosures too wide near 30/7 for the region-B port, does not
materialise at single nodes. The F radius grows only from 2.4e−8 to 1.6e−7 between k = 4.2 and 30/7 − 1e−6.

**Reading for P:**
- tr Γ is small (−0.013 and −0.003) and real, so the region-B pilot's imprimitivity test should use tr Γ ≠ 0 or
  tr M1Γ ≠ 0, as registered for region B. With a radius of about 2e−13 this is far from a problem.
- The ellipse M bound in region B needs the field's d/dk and a k-uniform second-derivative bound. v2's d2kc0 is a
  radial integral and is not automatically valid in the half-plane. That is the next build step, for pilot 2 and the
  dyadic pilot 3.
