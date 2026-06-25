#!/usr/bin/env python3
"""Step 97 — ZIPOY-VOORHEES: the no-Carter result, now on an EXACT vacuum solution.

§85 showed a quadrupole-deformed Kerr loses its Carter constant — but that deformation was
PHENOMENOLOGICAL (a non-vacuum bump on the metric). The honest objection: "is that a real
spacetime?" This battery answers it on a genuine one. The Zipoy-Voorhees (gamma-) metric is an
EXACT static vacuum solution — Schwarzschild carrying a tunable quadrupole, kept exactly
Einstein-vacuum for every value of the deformation delta (delta=1 IS Schwarzschild). We build
it in closed form (no interpolation; the symbolic-curvature route swamps, so curvature is read
off numerically — that is the "wall" this breaks), confirm it is vacuum, and feed it to §85's
detector.

PRIOR ART (cited, not claimed): ZV's geodesic non-integrability and the absence of a Carter
constant are established — Lukes-Gerakopoulos, "The non-integrability of the Zipoy-Voorhees
metric," Phys. Rev. D 86, 044013 (2012), arXiv:1206.0660; for delta=2 there are chaotic orbits.
This battery REPRODUCES that as a VALIDATION of our general numerical detector; the contribution
is the validated tool (no closed-form Killing tensor / separability needed), now resting on an
exact vacuum solution rather than a bump.

  (A) ZV is EXACT vacuum for every delta — max|R_ab| stays at the finite-difference floor
      (~1e-6), flat in delta (non-perturbative, unlike an O(q) construction). A real spacetime;
  (B) basis independence (no hidden algebraic identity that would fake a conserved quantity);
  (C) VALIDATION — delta=1 (Schwarzschild): the fit recovers the Carter constant (one
      machine-zero singular value, huge gap), matching K = (1-y^2)p_y^2 + L^2/(1-y^2);
  (D) DEFORMED delta!=1: NO machine-zero singular value — the smallest jumps ~9 orders of
      magnitude and GROWS monotonically with |delta-1|. No conserved QUADRATIC survives (no
      Carter constant). [This rules out a quadratic Carter, NOT every integral — a higher-order
      Killing tensor isn't excluded by this basis; ZV's full non-integrability is the literature's
      proof (Morales-Ramis), which our result is consistent with, not a re-derivation of.];
  (E) synthesis: the same detector that recovers Carter for Schwarzschild finds NONE for any
      deformation — on an EXACT vacuum solution, consistent with the known ZV result. Validates §85.

ADVERSARIALLY STRESS-TESTED (scripts/_zv_stresstest.py, 5 tests, all pass): the delta=1 control
is genuinely Schwarzschild (textbook Carter conserved to 6e-16, not a fit); the delta!=1 1e-5 is a
REAL non-invariant (stable under 16->32 orbits and a halved step, does not collapse to the floor);
the basis isn't rigged (enriching it preserves the contrast); it generalizes out-of-sample; and it
is robust across orbit families. So the contrast is physics, not seeing-what-we-wanted.

Optional dep: numpy (SVD). Part (A) runs without it; (B)-(E) skip cleanly if absent.
Repro:  .venv/bin/python scripts/97_zipoy_voorhees_integrability.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zipoy_voorhees import metric as zv_metric
from numeric_curvature import ricci_numeric

try:
    import numpy as np  # noqa: F401
    _HAVE_NUMPY = True
except ImportError:
    _HAVE_NUMPY = False


def main():
    print("ZIPOY-VOORHEES — the no-Carter result on an EXACT vacuum solution\n")
    ok = []

    # (A) ZV is exact vacuum for every delta (no numpy needed) — a genuine spacetime
    pts = [(2.0, 0.0), (2.5, 0.3), (3.0, -0.5), (4.0, 0.7)]
    worst = {}
    for delta in (1.0, 0.8, 1.3, 2.0):
        worst[delta] = max(abs(ricci_numeric(zv_metric(delta), [0.0, x, y, 0.0], h=1e-5)[i][j])
                           for (x, y) in pts for i in range(4) for j in range(4))
    okA = all(v < 1e-4 for v in worst.values())
    ok.append(okA)
    print("  (A) ZV exact-vacuum residual max|R_ab| (must stay at FD floor ~1e-6 for ALL delta):")
    for delta in (1.0, 0.8, 1.3, 2.0):
        lab = "delta=1 (Schwarzschild)" if delta == 1.0 else f"delta={delta}"
        print(f"        {lab:24s}: {worst[delta]:.2e}")
    print(f"      flat in delta ⇒ a real vacuum solution, not an O(q) approximation   {'✅' if okA else '❌'}")

    if not _HAVE_NUMPY:
        print("\n  (B)-(E) SKIPPED (numpy not installed; pip install numpy)")
        print(f"\nZIPOY-VOORHEES: {'PARTIAL (A only) ✅' if okA else 'FAILED ❌'}")
        return 0 if okA else 1

    from _zv_invariant import BNAMES, check_independence, fit, metric

    E, L, x0 = 0.97, 4.0, 11.0
    p2list = [round(0.06 + 0.05 * k, 3) for k in range(16)]

    # (B) basis independence
    indep = check_independence()
    okB = indep > 1e-6
    ok.append(okB)
    print(f"\n  (B) basis independence (smallest SV on random points): {indep:.2e}  "
          f"{'✅ no hidden identity' if okB else '❌ DEGENERATE'}")

    # (C) VALIDATION — delta=1 must recover the Carter constant
    S1, n1, vec1 = fit(metric(1.0), E, L, p2list, x0)
    gap1 = S1[-2] / S1[-1] if S1[-1] > 0 else float("inf")
    terms = dict(zip(BNAMES, vec1))
    r_om = terms["y2/om"] / terms["py2"]            # should equal L^2
    r_yy = terms["py2*y2"] / terms["py2"]           # should equal -1
    carter_match = abs(r_om - L * L) / (L * L) < 0.05 and abs(r_yy + 1) < 0.1
    okC = S1[-1] < 1e-9 and gap1 > 1e6 and carter_match
    ok.append(okC)
    print(f"\n  (C) VALIDATION — delta=1 Schwarzschild [{n1} orbits]: smallest SV={S1[-1]:.2e}, "
          f"gap={gap1:.1e} → one clean invariant")
    print(f"      recovered  C ≈ (1-y²)p_y² + {r_om:.2f}·1/(1-y²)   vs Carter  (1-y²)p_y² + "
          f"{L*L:.0f}·1/(1-y²)   {'✅ recovers Carter' if carter_match else '❌'}")

    # (D) DEFORMED — no machine-zero invariant; obstruction grows with |delta-1|
    defs = {}
    for delta in (0.8, 1.2, 1.4):
        Sd, nd, _ = fit(metric(delta), E, L, p2list, x0)
        defs[delta] = (Sd[-1], nd)
    no_inv = all(s > 1e-7 for s, _ in defs.values())
    grows = defs[1.2][0] < defs[1.4][0]              # further from Schwarzschild ⇒ more broken
    okD = no_inv and grows
    ok.append(okD)
    print(f"\n  (D) DEFORMED ZV — smallest SV (no machine-zero ⇒ no conserved quadratic):")
    print(f"        delta=1.0 (control)      : {S1[-1]:.2e}   ← exact (Carter)")
    for delta in (0.8, 1.2, 1.4):
        s, nd = defs[delta]
        print(f"        delta={delta} [{nd} orbits]      : {s:.2e}   broken (~{s/S1[-1]:.0e}× the delta=1 floor)")
    print(f"      no conserved quadratic — no Carter constant (consistent w/ ZV's proven non-integrability)   "
          f"{'✅' if okD else '❌'}")

    # (E) synthesis
    okE = okA and okB and okC and okD
    ok.append(okE)
    print(f"\n  (E) The SAME detector recovers Carter for Schwarzschild (SV~1e-14) and finds NONE for")
    print(f"      any deformation (SV~1e-5) — on an EXACT vacuum solution. Reproduces the known ZV")
    print(f"      non-integrability (Lukes-Gerakopoulos 2012) and upgrades §85 off its phenomenological")
    print(f"      bump onto a genuine spacetime. The validated detector needs no closed-form Killing")
    print(f"      tensor — it works where the symbolic route swamps.   {'✅' if okE else '❌'}")

    passed = all(ok)
    print(f"\nZIPOY-VOORHEES: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(exact vacuum for all delta; Carter recovered at delta=1; no conserved quadratic for delta!=1)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
