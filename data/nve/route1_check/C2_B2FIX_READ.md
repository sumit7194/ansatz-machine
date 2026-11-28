# The base2 fix: non-author read (registration order step 2), 2026-11-29
**Reader:** a fresh agent (not the author). Read-only, with short snippets. It read c802bac against 408b56e.
**Verdict: sound to run the controls and B5.** It found no way to a false enclosure, or to a pass where a refusal is due.

| item | finding | grade | action |
|---|---|---|---|
| 1 | The integrand enclosure is valid for every s in a piece and every k in K: the clamp at 0, `_sq_up`, the a2s2 clamp, and a4s4 from the endpoints. With complex coefficients, independence only widens the enclosure. | none | — |
| 2 | `Pv.real > 0` is a "certainly" test (False for a NaN or a straddling ball). exp(−1.5 log P) is the principal 1/(P √P) on Re P > 0. | none | — |
| 3 | The tiling is exact, but the pieces' endpoints and widths are BALLS, not "exact" as the docstring said (SM = 96). Still sound: the s-range is taken outward and the width ball contains the true width. | minor | wording fixed |
| 4 | Every refusal propagates as None, with no partial sum. | none | — |
| 5 | Caching is per process and keyed by K; a radius below about 1e−308 would collide (not reachable here). | none | — |
| 6 | B2 checked containment, not finiteness. B2's reference shares the integrand formula. There was no truth test on a BOX K. | minor | B2 now requires finiteness; B6 added (a k-second-difference of the undifferentiated √P integrals, which is formula-independent); B7 added (corner, centre and edge point quadratures of complex worst cells, 36 points). The reader ran both and they passed. |
| 7 | d2kc0_B's s-ball loop: `4 Bv √Bv` can contain 0 when Bv passes both guards, so g is NaN. That NaN is returned uncaught. Every consumer traced fails closed (dq_sup, v4, the glue's `me()` crash), but the glue's path is by accident. selftest_B's `overlaps` passes vacuously on a NaN. | minor | d2kc0_B returns None (refused "nonfinite") when its result is not finite; `initial()` in the glue raises RuntimeError on a non-finite d2kc0. Fail-closed is now by design. |
| 8 | The floats file was uncommitted, and its generator still running. B5 reads it live. | process | B5 waits for the floats commit (done with this file) |

**Controls after the fixes:** B1, B2, B3 (26 k-sets), B4, B6 and B7 (36 points) all PASS (`c2/b2fix_controls.json`).
