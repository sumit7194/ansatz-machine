# C2-4 focused non-author read (Bridge condition 2), 2026-11-28

**Reader:** a fresh agent (not the author). Read-only. It read CAPD's own sources for the claims below.
**Reviewed:** commit 5f5d42d (driver v2 and glue).

## Verdicts
- **(i) PASS.** The closed-form root equals the field's branch at the start.
  - On the circle at the real base, w * sqrt_p(B/w^2) = sqrt_p(B) identically.
  - (a3) can fire: Re s0 > 0, so the balls s0 and -s0 are disjoint.
  - It stays continuous along every edge for every k in the sub-box: the root depends only on (z, k), and k is constant
    along each trajectory.
  - No gap between the guarded set and where CAPD evaluates the field. getLastEnclosure is the enclosure on which the
    remainder coefficients are computed; the Taylor and Jacobian coefficients are evaluated on the hull inside it; a
    step shrunk after the inclusion test makes the guarded time range a subset, which is the safe direction.
  - CAPD's interval sqrt throws on a negative lower bound, and division by an interval containing 0 throws, so a set
    straddling the cut cannot pass silently.
  - The a priori edgeGuard is sound on its own (whole edge x the true k box); the per-step guard is a second proof.
- **(ii) PASS.** The (a2) disc is checked on every edge and every step, in the conservative direction (upper(d^2) <=
  lower(Irad^2)). The reader's Arb check over the full P1 box gives sup|I - Ic| <= 6.30 and Re c2 >= 4.819, matching E1.
  At R/5: <= 3.18 on the circle and <= 3.00 on the lasso, |w| >= 5.05.
- **(iii) PASS with one major finding (F1).** Time stays a point, retries halve exactly, and inexact times or edge ends
  are refused.
- **Other: PASS.** Exact I/O, the row mapping (the Y rows are 4..11; the k columns are 12/13) and the domain checks are
  sound.

## Findings and what was done (fixes in the commit after 5f5d42d; a re-read follows)
- **F1, major: the retry could continue from a corrupted set.** CAPD's C0DoubletonSet::move can overwrite x, C and B
  before a late logic_error, while the time stays at t. Reachable only via CAPD's "fatal" path or bad_alloc.
  **Fixed:** the set is copied before each step and restored in the catch; the restored time is asserted to be t.
- **F2, minor: no control exercised the per-step (a1)/(a2) guards** (K2 and K3 are refused a priori).
  **Fixed:** a `skip_edge_guard` input flag, set only by the plants K2s and K3s, recorded in the driver's output
  header and asserted by the glue. Expected: K3s is refused by the per-step (a2) guard. K2s is refused by the per-step
  (a1) guard, or, for a cut crossing, by CAPD's interval sqrt throwing, so the step can never validate; the record says
  which.
- **F3, minor: Kbox relied on input structure that was never checked.**
  **Fixed:** the driver asserts that the k rows of C are the identity and that their radii are 0.
- **F4, minor: the step-size comment and the development notes were inaccurate.** CAPD also rescales steps exactly
  (by 0.95 and by an approval factor), and the step after a fresh one is limited to twice the previous step.
  **Fixed in the comment.** This affects cost only; the point and end checks still refuse any inexact time.
- **Small gap: the glue did not check the driver's DONE line or its header.**
  **Fixed:** both are asserted (sform and skip_edge_guard).

**Regression smoke after the fixes** (P2 and P1 at hs/10, retraced): identical to before. F is +-0.0118 and +-3.51e-3,
and the Arb walk is contained.
