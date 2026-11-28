# RESULT: the stop-(c) discriminator at spin 9/10. Both widths admit a row at k_c = 5/2; the growth is box-size sensitivity

**Office ansatz-machine (Claude Opus), 2026-11-28.** The seal is `STOPC_DISCRIM_SEAL.md`, committed with its runner
and manifest before launch (6dc9912).
- **The run:** on the Mac mini, launched 14:59:41 as PID 22322; prove A was PID 22593 and prove B PID 22594. All
  exited rc 0 by 15:13:12. Nice 10, under the pause-only guard, which never paused.
- **Outputs** are in `stopc_discrim/`: the logs, `prove_A.out`, `prove_B.out`, and `eps/` with the rows, the dq
  checkpoints, the M json and the floats.

## Environment, side by side with production (read from each interpreter)

| | this run (Mac mini) | production (Air) |
|---|---|---|
| Arb side | Python 3.13.12, python-flint 0.9.0, **FLINT 3.6.0**, mpmath 1.3.0, numpy 2.4.6, sympy 1.14.0 | Python 3.13.18, python-flint 0.9.0, **FLINT 3.6.0**, mpmath 1.3.0, numpy 2.5.0, sympy 1.14.0 |
| floats | `.venv` Python 3.14.5, mpmath 1.3.0 | `.venv` Python 3.14.10, mpmath 1.3.0 |

**Grade: same code, same arithmetic library, different interpreter patch release.**
- The code is v2–v6, byte-identical to `MANIFEST_PROD`.
- Interval widths could differ only through the float gauge inputs. A difference there would show as a small change
  in M_F, not a change of regime. This is a diagnostic, not a certificate.

## Measured

| | A: half-width 1/20 (R = 0.10625) | B: half-width 1/40 (R = 0.053125) | P3 baseline, k_c = 2, half 1/20 |
|---|---|---|---|
| row at ρ = 4 | **admitted, n = 28** | **admitted, n = 12** | admitted, n = 22 |
| M_F | 1.2e14 | 1.3e5 | 2.7e9 |
| I0 (circle) / c0 per k | 3.488 / 32.8 | 0.258 / 4.85 | 1.164 / 11.0 |
| I1 (lasso) / c1 per k | 9.372 / 88.2 | 2.384 / 44.9 | 6.459 / 60.8 |
| prove time, peak footprint | 774 s, 54 MB | 777 s, 53 MB | about 46 min on the Air |

The floats at k_c 5/2 took 20 s (geo True). No F1 assertion fired.

## The registered reading
- **Row 1 of the table applies.** A admits a row with n = 28 ≤ 40, so 0.1-wide segments work at least to k = 2.5 at
  9/10. The stop lies in (2.5, 3], and [2, 2.5] is coverable inside v6 at production width.
- **And B shows the split rule recovers it cheaply.** At half-width 1/40, n drops to 12 and M_F by about 9 orders of
  magnitude.
- **Attribution:** halving R cut I0 (circle) by 13.5×, far more than the 2× from R alone. The circle's per-unit-R
  density fell 6.8× (32.8 → 4.85). I1 (lasso) fell 3.9×.
  - So **the circle-side growth is sensitivity to complex k at the edge of the k-box, and a smaller box cures it.**
  - That fits the scan's finding of no singular point near the loops. Its exact source, likely the k-dependence of
    the Laurent c0 enclosure on the circle, is not isolated here.
- **I0(A)/I0(P3, k_c = 2) = 3.0:** the growth is moderate up to 2.5 and steepens beyond it.

**For 9/10's [2, 3]:**
- At production width the segments up to 2.5 are admissible (n near 28 at 2.5).
- Beyond 2.5 the split rule (depth 1 or 2) is expected to recover the rest.
- The k_c = 3 row at half 1/40 is untested; it is the natural first segment of any extension.
- **9/10's [2, 3] does not need v7.**

## Against the seal

| prediction | P | outcome |
|---|---|---|
| A admits a row with n ≤ 40 | 55% | n = 28: **HIT** |
| B admits a row with n ≤ 40 | 80% | n = 12: **HIT** |
| if both admit, n(B) < n(A) | 85% | 12 < 28: **HIT** |
| I0(A)/I0(P3, k_c = 2) in [1, 3] | 60% | 2.996: **HIT** (at the edge) |
| I0(B) < I0(A)/2 | 50% | 13.5× smaller: **HIT** |
| F1 never fires; both rc 0 | 95% | **HIT** |
| wall time per prove 30–70 min | 70% | about 13 min: **MISS** (under; the Mac mini is faster than the Air's 46 min) |
| peak footprint < 150 MB | 95% | 54 MB: **HIT** |
