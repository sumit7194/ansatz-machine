# C2 step 0' result (addendum C2-3's amended probe): FAIL. All six drives were refused; two of the refusals are a
driver time-bookkeeping artefact

**Office ansatz-machine, 2026-11-28.** The run is `air/c2_step0p_lane.sh` lane A at 31ca0bc, with the IdQR driver.
Settings were fixed in C2-3: 256 bits, order 20, tolerance 1e-15. Records are in `c2/step0p_P{1,2}_k{5,10,20}_o20_id_tol1e-15_*`,
the lane logs in `v7/c2_step0p_{A,B}.log`.

**Grading line:** step-0' bar amended (C2-3) after development smoke runs indicated the registered width/range bar would
fail at R/5; the new bar matches the certificate's use (sup bounds). The smoke widths at R/5, R/50 and R/500 on
retraced loops were seen. **Verdict: FAIL** (no size gave an enclosure, so neither the sup bar nor the original bar
can pass).

| case | outcome | where | CAPD time to refusal |
|---|---|---|---|
| P2 R/5 | REFUSED, division by zero in CAPD (no step validates) | Gamma, edge 25 of 98 | 29 s |
| P2 R/10 | REFUSED, "the edge did not end at its final time" | Gamma, edge 59 | 46 s |
| P2 R/20 | REFUSED, "the edge did not end at its final time" | Gamma, edge 65 | 43 s |
| P1 R/5 | REFUSED, division by zero | circle, edge 6 of 96 | 12 s |
| P1 R/10 | REFUSED, division by zero | circle, edge 10 | 19 s |
| P1 R/20 | REFUSED, division by zero | circle, edge 16 | 27 s |

For every case, the original bar FAILS and the sup bar FAILS (no enclosure). The point samples (lanes A and B) are still
running and are kept: the same sub-boxes and grids serve any re-run.

**Predictions against the outcome:**
- original bar fails at R/5 at P2: predicted 90%; it failed;
- sup bar passes for F at R/5 at P2: predicted 55%; it did not;
- cost: not reached;
- step 0' PASS: predicted 40%; it FAILED.

## Diagnosis (read-only on the records, plus diagnostic drives that change no result)
**1. The two "did not end" refusals are a driver artefact, not mathematics.**
- CAPD's TimeMap retries a failed step with maxStep/1.5. That value is not dyadic, so the step, and then the set's time,
  becomes an interval.
- The step logs show it: 172 of the 179 step sizes at P2 R/10 are non-dyadic (for example 0.475 = 0.7125/1.5).
- The driver's end-of-edge check (the final time inside the set's time, and a width below 1e-60) then fails after many
  edges.
- A trivial two-dimensional system with no retries keeps the time exact over 80 edges (scratch test).
- Rigour was never at risk: the box was refused, not accepted.

**2. The four division-by-zero refusals are a blow-up of the s = sqrt B STATE's remainder, not of the k-dependence.**
- A diagnostic drive at P1 R/20 logged per-block widths (the IdQR driver plus logging; lane B was paused meanwhile, so
  the 2-core limit held). Record: `c2/step0p_P1_k20_o20_iddiag_tol1e-15_steps.log`.
- The B r part of s grows about 1.4x per edge: 0.09 (edge 5), 0.18, 0.33, 0.62, 1.33, 2.25, 7.8, 15 (edge 16).
- The C r0 part of s, the dk-linear part C2 exists to carry, stays at 0.2–0.4.
- c0, c0' and Y never exceed 0.06.
- Near edge 16 the certified min |s|^2 falls to 11 (true |B| about 156), the rough enclosures stop validating, and the
  step is refused.
- The same drive with Rect2 (FullQRWithPivoting) fails at edge 15 with the same diameter profile, so QR does not cure
  it.
- P2 R/5's Gamma refusal shows the same signature: min |s|^2 falls from 179 to 6 on edge 25.

**What this means:** the k-correlation machinery works (C r0 is tight). What fails is carrying an ALGEBRAIC function,
sqrt B(z, k), as a dynamical state, whose accumulated remainder grows. The registration's fallback is an own Arb TM
layer, or STOP. A narrower remedy is put to the Bridge as a proposed addendum C2-4: eliminate s as a state (a closed-form
principal root, branch-certified per step), plus exact-time stepping. It is NOT applied until ruled on.
