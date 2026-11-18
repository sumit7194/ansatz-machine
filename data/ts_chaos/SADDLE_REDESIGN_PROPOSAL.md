# Redesign proposal: is the TS δ = 2 capture edge a genuine fractal? (2026-11-18, PROPOSAL ONLY, nothing run)

For Sumit, via the Bridge. Context: the registered lifetime-interval test is VOID, because its Kerr control failed
(SADDLE_PREREGISTRATION.md addendum 2). The R2 rerun stopped at its Kerr gate. The TS R1 data stay sealed and unread.

## Root cause, in one paragraph
Near a separatrix, whether an orbit plunges on pass k depends on a margin of order Δx², where Δx is the distance to the
boundary. Integration error of order tol therefore blurs lifetimes inside a strip of width ~√tol. Kerr went wrong at
~1e−11 (tol 1e−22) and at ~1e−15 (tol 1e−28): roughly √tol, though two points do not establish the exponent. The
registered search refined down to 1e−18, below what the double-double engine can resolve at any setting. Any
lifetime statistic taken below the floor measures integrator noise, not dynamics, in Kerr and in TS alike.

## (i) Options
| | idea | verdict |
|---|---|---|
| **A. Higher-precision engine** | quad-double (new numba primitives), mpmath, or Arb, deepening the floor | mpmath is **measured: 72× DD per crossing** (Kerr, 50 digits); 3,000 orbits × up to 600 crossings is thousands of core-hours, so **infeasible**. Arb is likely 10–30× (unmeasured) and still too slow at this scale. Quad-double is ~5–10× DD plus about a day to build and validate; each precision step buys only a fixed amount of lifetime, so it **moves the floor, it does not remove it**. |
| **B. Refinement floor calibrated on Kerr** | stop refining at width w_min = 10·√tol·C, with C and the exponent measured on Kerr; read 𝒩(t) only above the floor | cheap, uses the existing engine. **Risk:** at R2 the floor sits near level 7, and whether the t-range up to 400 can be resolved that shallow cannot be known in advance. It may simply come back INCONCLUSIVE. |
| **C. Homoclinic-tangle test (recommended)** | find TS's unstable (Lyapunov) periodic orbit at the α level; trace its stable and unstable manifolds on the y = 0 section; measure whether they cross **transversally** | a transverse homoclinic point implies a Smale horseshoe by theorem (Smale–Birkhoff), hence a chaotic saddle, hence a fractal boundary in the limit. Manifolds need only short integrations from near the orbit, so precision is not the bottleneck, and the splitting angle is checked at two precisions. **Kerr control: the manifolds coincide (zero splitting) because Kerr is integrable.** This is math over brute force, and it answers the question the lifetime test was a proxy for. |

## (ii) Cost (box rules: ≤ 2 cores, nice 10, < 1 GB, < 100 MB disk)
- **C:** building the periodic-orbit finder (Newton on the section return map) and the manifold tracer takes about
  1–2 days of my time. Compute: one periodic orbit plus ~200 manifold seeds × ≤ 10 passes, at R1 and R2, for TS and Kerr.
  Estimate **2–4 h on 2 cores** (to be measured before the slot request, per "measure first").
- **B:** Kerr calibration at 3 tolerances, about 1 h each on 2 cores; TS at R2 with 3,000 orbits, about 15–20 h on 2 cores
  (R2 measured at ~3× R1 on Kerr; TS R1 was ~16 core-s per orbit).
- **A (quad-double):** build about 1 day; TS ≥ 100 h on 2 cores at the original budget. Not proposed.

## (iii) Gates, pre-registered before any TS output
1. **Scaling gate (for B, and as a diagnostic for C):** Kerr's noise-onset width measured at tol 1e−20, 1e−24 and
   1e−28. The slope of log(onset) against log(tol) must lie in [0.4, 0.75] (√ predicts 0.5), with a hold-out check at
   1e−26: with the floor applied, Kerr 𝒩(t) ≤ 2. If this fails, the root-cause story is wrong; stop and rethink.
2. **Positive control for C:** a periodically forced pendulum with known Melnikov splitting. The tracer must recover a
   transverse crossing whose angle matches Melnikov to within 10%, and zero splitting when the forcing is off.
3. **Negative control for C:** Kerr at the matched separatrix level. The splitting must be zero to ≤ 1e−20 (R2).
4. **Precision gate for C:** the TS splitting angle at R1 and R2 must agree to ≥ 6 digits; an angle below 1e−8 counts
   as "not resolved", not as "zero".
5. A literature check before building: homoclinic-tangle studies of non-Kerr geodesics probably exist (e.g. the
   Lukes-Gerakopoulos / Apostolatos line). That determines what is new here, which may be TS2 itself, at Dubeibe's
   "integrable" level.

## (iv) What it could and could not tell us
- **C, transverse crossing found and robust:** "TS δ = 2 has a horseshoe at this energy and momentum level, hence a
  chaotic saddle; the capture edge is fractal in the limit." This would be a theorem-grade statement given a
  computer-verified transversality (interval arithmetic would make it rigorous; at two precisions it is strong numerical
  evidence). It upgrades the current "finite-horizon fractal-like" wording, and it directly contradicts the
  "completely integrable" claim at that level.
- **C, splitting not resolved:** no statement; the current wording stands. It would not show integrability (the
  splitting could be exponentially small).
- **B:** at best an 𝒩(t) growth rate over a precision-limited t-range. That is evidence, not a theorem, and the
  likeliest outcome is INCONCLUSIVE.
- **None of these** says anything about valences above 10, about EMRI orbits, or about other (E, L) levels.
- Unchanged by any outcome: the KT nulls (§149–§153) and the α measurements (finite horizon, as worded).

**Recommendation:** C, gated by its two controls, with the cheap scaling gate (1) run first as the root-cause check.
B only if C cannot locate the periodic orbit. A is not recommended.
