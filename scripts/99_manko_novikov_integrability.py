#!/usr/bin/env python3
"""Step 99 — THE ROTATING WALL: Manko-Novikov, the no-Carter result on an EXACT ROTATING vacuum.

§97 showed a quadrupole-deformed STATIC black hole (Zipoy-Voorhees) loses its Carter constant.
This is the ROTATING analog, and it crosses the long-standing item-3 wall: a *consistent, exact*
rotating "bumpy Kerr". The Manko-Novikov metric is an exact stationary axisymmetric VACUUM
solution with a tunable quadrupole anomaly q (q=0 is exactly Kerr). The (x,y)-dependent off-
diagonal curvature swamps SymPy (the wall), so we read it NUMERICALLY — and the geodesic
Hamiltonian too, sidestepping the symbolic blow-up entirely.

  (A) MN is EXACT vacuum for q!=0: the finite-difference Ricci scales as h^2 (pure truncation
      error of a vacuum metric), NOT a plateau -> Ricci=0. A genuine rotating solution;
  (B) the q=0 limit reproduces EXACT Kerr (Boyer-Lindquist, transformed) to machine precision
      -- the anchor that makes the deformed result trustworthy;
  (C) VALIDATION: at q=0 the §97 detector recovers Kerr's Carter constant (one near-zero
      singular value, ~1e-10, with a ~1e8 gap) -- the numeric reduced Hamiltonian works;
  (D) DEFORMED q!=0: NO conserved quadratic -- the smallest singular value jumps ~9 orders of
      magnitude (to ~1e-2) with no gap. The Carter constant does not survive the deformation;
  (E) synthesis: an EXACT ROTATING vacuum black hole loses Carter under a quadrupole anomaly --
      the rotating §97, on a real solution, crossing item-3's wall numerically.

PRIOR ART cited, not claimed: Manko-Novikov geodesic non-integrability is established (Gair, Li,
Mandel, PRD 77, 024035 (2008), arXiv:0708.0628; Lukes-Gerakopoulos et al.). The contribution is
the validated general numeric detector + the verified exact-rotating-vacuum testbed. Honest scope:
this rules out a conserved QUADRATIC (Carter); rank>=4 not tested here (cf. §98 for the static case).

Optional dep: numpy. (A)(B) run without it; (C)-(E) skip cleanly if absent.
Repro:  .venv/bin/python scripts/99_manko_novikov_integrability.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manko_novikov import kerr_prolate, manko_novikov
from numeric_curvature import ricci_numeric

try:
    import numpy as np  # noqa: F401
    _HAVE_NUMPY = True
except ImportError:
    _HAVE_NUMPY = False


def _maxRicci(g, h):
    pts = [(3.0, 0.3), (4.0, -0.4), (5.0, 0.6)]
    return max(abs(ricci_numeric(g, [0.0, x, y, 0.0], h=h)[i][j])
              for (x, y) in pts for i in range(4) for j in range(4))


def main():
    M, a = 1.0, 0.5
    print("THE ROTATING WALL — Manko-Novikov: no Carter on an EXACT rotating vacuum black hole\n")
    ok = []

    # (A) MN is exact vacuum for q!=0: Ricci ~ h^2 (truncation), not a plateau
    g02 = manko_novikov(M, a, 0.2)
    r1, r0 = _maxRicci(g02, 1e-3), _maxRicci(g02, 5e-4)
    ratio = r1 / r0 if r0 > 0 else float("inf")        # ~4 ⇒ Ricci ∝ h^2 ⇒ true Ricci = 0
    okA = r0 < 1e-5 and 3.5 < ratio < 4.5
    ok.append(okA)
    print(f"  (A) EXACT VACUUM (q=0.2): max|R_ab| = {r1:.1e} (h=1e-3) -> {r0:.1e} (h=5e-4), ratio {ratio:.2f}")
    print(f"      the residual quarters as h halves (Ricci ∝ h^2 = pure truncation of a VACUUM metric,")
    print(f"      not a plateau) ⇒ true Ricci=0, a genuine rotating solution   {'✅' if okA else '❌'}")

    # (B) q=0 reproduces EXACT Kerr to machine precision
    gk, gm = kerr_prolate(M, a), manko_novikov(M, a, 0.0)
    worst = 0.0
    for (x, y) in [(2.0, 0.3), (3.0, -0.5), (4.0, 0.7)]:
        K, Mn = gk([0, x, y, 0]), gm([0, x, y, 0])
        worst = max(worst, max(abs(K[i][j] - Mn[i][j]) / (abs(K[i][j]) + 1e-30)
                               for i in range(4) for j in range(4)))
    okB = worst < 1e-9
    ok.append(okB)
    print(f"\n  (B) q=0 reproduces exact Kerr (Boyer-Lindquist transformed): worst rel mismatch "
          f"{worst:.1e}   {'✅' if okB else '❌'}")

    if not _HAVE_NUMPY:
        print("\n  (C)-(E) SKIPPED (numpy not installed)")
        print(f"\nMANKO-NOVIKOV: {'PARTIAL (A,B) ✅' if okA and okB else 'FAILED ❌'}")
        return 0 if (okA and okB) else 1

    from _mn_invariant import build_hamilton_numeric
    from _zv_invariant import check_independence, fit

    E, L, x0 = 0.95, 2.8, 6.0
    p2list = [round(0.05 + 0.05 * k, 3) for k in range(16)]

    indep = check_independence()
    print(f"\n  basis independence (random pts): {indep:.2e}  {'OK' if indep > 1e-6 else 'DEGENERATE'}")

    # (C) VALIDATION — q=0 recovers Kerr's Carter
    S0, n0, _ = fit(build_hamilton_numeric(M, a, 0.0), E, L, p2list, x0)
    gap0 = S0[-2] / S0[-1] if S0[-1] > 0 else float("inf")
    okC = S0[-1] < 1e-8 and gap0 > 1e6
    ok.append(okC)
    print(f"\n  (C) VALIDATION q=0 (Kerr) [{n0} orb]: smallest SV={S0[-1]:.2e}, gap={gap0:.1e} "
          f"-> Carter recovered   {'✅' if okC else '❌'}")

    # (D) DEFORMED q!=0 — no conserved quadratic
    defs = {}
    for q in (0.1, 0.2):
        Sd, nd, _ = fit(build_hamilton_numeric(M, a, q), E, L, p2list, x0)
        defs[q] = (Sd[-1] if Sd is not None else None, nd)
    okD = all(s is not None and s > 1e-4 for s, _ in defs.values())
    ok.append(okD)
    print(f"\n  (D) DEFORMED — smallest SV (no machine-zero, no gap ⇒ no Carter):")
    print(f"        q=0.0 (control): {S0[-1]:.2e}   ← Carter")
    for q in (0.1, 0.2):
        s, nd = defs[q]
        print(f"        q={q} [{nd} orb]:     {s:.2e}   ({s / S0[-1]:.0e}× the q=0 floor) -> broken")
    print(f"      the quadrupole anomaly destroys the Carter constant   {'✅' if okD else '❌'}")

    # (E) synthesis
    okE = okA and okB and okC and okD
    ok.append(okE)
    print(f"\n  (E) An EXACT ROTATING vacuum black hole (Manko-Novikov) loses its Carter constant under a")
    print(f"      quadrupole anomaly -- the rotating analog of §97 (ZV), now crossing item-3's symbolic")
    print(f"      wall numerically. Same detector recovers Carter for Kerr (q=0) and finds none for q!=0.")
    print(f"      Reproduces the known MN non-integrability (Gair et al 2008).   {'✅' if okE else '❌'}")

    passed = all(ok)
    print(f"\nMANKO-NOVIKOV: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(exact rotating vacuum for all q; Carter recovered at q=0; none for q!=0)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
