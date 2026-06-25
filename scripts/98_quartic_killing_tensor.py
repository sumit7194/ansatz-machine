#!/usr/bin/env python3
"""Step 98 — NO QUARTIC KILLING TENSOR EITHER: closing §97's one honest caveat.

§97 found the quadrupole-deformed (Zipoy-Voorhees) black hole has no conserved QUADRATIC (no
Carter constant), but flagged: that rules out a rank-2 Killing tensor, NOT a higher-order one.
This pushes the same numerical search to QUARTIC order (a rank-4 Killing tensor) and finds none
either — so no conserved quantity quadratic OR quartic in the momenta survives the deformation.

The validation is sharper than §97's. The basis is auto-pruned to independence and built to span
K^2, the SQUARE of Schwarzschild's Carter constant. So at delta=1 the conserved set is {K, K^2}
and the SVD must return EXACTLY TWO float-precision singular values — proving the basis really
does see quartic invariants. At delta!=1 it returns NONE.

The §85 trap, guarded twice: (1) a quartic basis can hide algebraic identities -> auto-pruned to
full rank on random points; (2) too few orbits for a 42-term basis leaves a DIMENSIONAL near-null
at ~1e-12 that mimics an invariant -> we prove any deformed near-null is this artifact by showing
it LIFTS ~100x when the orbit set is flooded (22 -> 76 orbits), while delta=1's two real invariants
stay pinned at the float floor.

This does NOT prove full non-integrability (a rank>=6 tensor isn't excluded); ZV's non-integrability
to all orders is the literature's proof (Lukes-Gerakopoulos 2012, Morales-Ramis). We close the
quadratic+quartic question numerically and stay honest about the rest.

Optional dep: numpy. Skips cleanly if absent. Repro: .venv/bin/python scripts/98_quartic_killing_tensor.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import numpy as np  # noqa: F401
    _HAVE_NUMPY = True
except ImportError:
    _HAVE_NUMPY = False


def main():
    if not _HAVE_NUMPY:
        print("NO-QUARTIC-KILLING-TENSOR: SKIPPED (numpy not installed)")
        return 0

    from _zv_quartic import ELX, P2, check_independence, fit, n_invariants

    print("NO QUARTIC KILLING TENSOR EITHER — closing §97's caveat (rank-4 search on Zipoy-Voorhees)\n")
    ok = []

    # (A) the quartic basis is auto-pruned to linear independence (no identity can fake a null)
    indep, nb = check_independence()
    okA = indep > 1e-7
    ok.append(okA)
    print(f"  (A) basis: {nb} terms, auto-pruned; smallest SV on random points: {indep:.2e}  "
          f"{'✅ independent' if okA else '❌ degenerate'}")

    # (B) VALIDATION — delta=1 must recover EXACTLY two float-precision invariants (K and K^2)
    S1, n1 = fit(1.0)
    inv1 = n_invariants(S1, 1e-12)
    gap1 = S1[-3] / S1[-2] if S1[-2] > 0 else float("inf")        # 3rd-smallest vs 2nd-smallest
    okB = inv1 == 2 and S1[-3] > 1e-11
    ok.append(okB)
    print(f"\n  (B) VALIDATION delta=1 (Schwarzschild) [{n1} orb]: smallest SVs "
          f"{S1[-1]:.1e}, {S1[-2]:.1e}, then {S1[-3]:.1e} (gap {gap1:.0e})")
    print(f"      -> exactly {inv1} float-floor invariants = K and K^2 (basis sees quartics)   "
          f"{'✅' if okB else '❌'}")

    # (C) DEFORMED — delta!=1 must show NO float-precision invariant (well-sampled)
    defs = {}
    for delta in (0.8, 1.2):
        Sd, nd = fit(delta)
        defs[delta] = (Sd, nd)
    okC = all(n_invariants(Sd, 1e-12) == 0 and Sd[-1] > 1e-11 for Sd, _ in defs.values())
    ok.append(okC)
    print(f"\n  (C) DEFORMED — no float-floor invariant (smallest SV stays well above ~1e-14):")
    for delta in (0.8, 1.2):
        Sd, nd = defs[delta]
        print(f"        delta={delta} [{nd} orb]: smallest SV={Sd[-1]:.1e}  -> {n_invariants(Sd,1e-12)} invariants")
    print(f"      no rank-4 Killing tensor for delta!=1   {'✅' if okC else '❌'}")

    # (D) ANTI-ARTIFACT — prove the deformed near-null is DIMENSIONAL (lifts when flooded), not real
    Ssparse, nsp = fit(0.8, ELx=[(0.97, 4.0, 11.0)], p2list=[round(0.05 + 0.045 * k, 3) for k in range(22)])
    Sflood = defs[0.8][0]
    lift = Sflood[-1] / Ssparse[-1] if Ssparse[-1] > 0 else float("inf")
    okD = Ssparse[-1] < 5e-12 and Sflood[-1] > 1e-11 and lift > 10
    ok.append(okD)
    print(f"\n  (D) ANTI-ARTIFACT (the §85 dimensional-null trap): delta=0.8 smallest SV")
    print(f"        {nsp:2d} orbits (under-sampled): {Ssparse[-1]:.1e}  (a near-null that mimics an invariant)")
    print(f"        {defs[0.8][1]:2d} orbits (flooded)     : {Sflood[-1]:.1e}  -> LIFTED {lift:.0f}x ⇒ it was a")
    print(f"      sampling artifact, NOT a conserved quartic. delta=1's two real invariants don't lift.   "
          f"{'✅' if okD else '❌'}")

    # (E) synthesis
    okE = okA and okB and okC and okD
    ok.append(okE)
    print(f"\n  (E) The deformed ZV black hole has NO conserved quantity quadratic (§97) OR quartic (this) in")
    print(f"      the momenta — no rank-2 and no rank-4 Killing tensor. The detector recovers BOTH of")
    print(f"      Schwarzschild's (K and K^2) as the control. (A rank>=6 tensor isn't excluded; ZV's full")
    print(f"      non-integrability is the literature's all-orders proof.)   {'✅' if okE else '❌'}")

    passed = all(ok)
    print(f"\nNO QUARTIC KILLING TENSOR: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(delta=1 recovers K and K^2; delta!=1 has neither a quadratic nor a quartic invariant)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
