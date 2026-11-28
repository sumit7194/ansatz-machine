# C2-TM non-author read (registration order step 4), 2026-11-28
**Reader:** a fresh agent (not the author). Read-only, with small Arb checks and no long runs. It read the working
tree at d30bc57; the re-read covered d30bc57..ac1b5fb, plus one minor fix after it.

## First read: one formal soundness bug, one control weaker than registered, minors
**Passed:**
- the core remainder rules (stress-tested: 2400 random points per case, 0 violations, max |mid - true|/e = 0.95);
- the step guards and the branch argument;
- the Y majorant and q_on_box;
- the start (its integrals match C0.start; one TM step overlaps C0's point step at 4 dk values);
- the preconditioning;
- the covering, T1 and the sup bar.

**Findings:**
- **F1, major (formal; at most about 1e-129, so no number changes):** the step-end c0/c0' Cauchy tails used th^NT,
  but zint keeps one term fewer.
- **F3, major (control scope):** T2 did not go through T1's code path.
- **Minor:**
  - F2: zscal dropped ball terms containing 0;
  - F4: the sqrt docstring overclaimed principal-ness;
  - F5: float rounding refused 10/118 Gamma and 123/308 lasso step attempts;
  - F6: non-vacuity checked only e;
  - F7: no base or closure check;
  - F8: weak sampling of the whole disc;
  - F9: module-global disc.

## Fixes (ac1b5fb) and re-read: all PASS, no new blocker or major
- F1: th^(NT-1)/NT and th^(NT-2)/((NT-1)NT).
- F2: is_zero().
- F3: T2 goes through T1's contain().
- F5: the step factor is 0.24 rho. Rounding refusals are now 0/114 and 0/161.
- F6: the evaluation width is checked too.
- F7: a shared-base assert and a c0 closure check at 5 disc points.
- F8: 8 points at |dk| = 0.99 rho.
- F9: one disc per process.
- The coordinator's series-count asserts are in place.
- After the re-read: the self-test now restores "no disc set" exactly (a minor finding of the re-read).

**Provenance note (from the re-read):** commit d30bc57's core still had the old loop-based TM multiplication, which
skipped the high-degree remainder when those coefficients were balls containing 0. The acb_poly version was in the
working tree but was only committed at ac1b5fb. The one run made in between, the development retraced walk, used the
working-tree acb_poly core. No registered result depends on d30bc57's core.
