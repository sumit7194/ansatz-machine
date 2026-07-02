#!/usr/bin/env python3
"""Step 109 — integrability/chaos as a single analyzer verdict (plan item 2: fold the toolchain into
the ONE general tool).

§84/§105/§106/§107 built a chaos toolchain as per-metric scripts; this makes it a report-card LENS on
the general analyzer: analyzer.integrability_signature(geo) samples bound orbits of any
stationary-axisymmetric metric and classifies the dynamics from the two validated section diagnostics
(box_dimension geometric + frequency_drift area-blind/thin-layer), returning one honest three-valued
verdict {NON-INTEGRABLE (chaos) | NON-INTEGRABLE (thin-layer) | no chaos detected (consistent with
integrable) | UNKNOWN}. Callable oracle, NOT auto-run in analyze() (orbit integration is heavy) --
the same design as invariant_fingerprint (§76).

  (A) KERR (a=0.6, integrable) -> no chaos detected in any sampled orbit (consistent with integrable).
  (B) ZV delta=2 (the §106 metric) -> NON-INTEGRABLE (thin-layer): the detector FIRES on the
      island-chain-edge orbits (x0=7.545, 7.565) and stays quiet on the island centre + far tori --
      i.e. the lens reproduces §106's hand-found anatomy automatically, on the general tool.

It can RULE IN chaos (positive detection) or report 'no chaos detected' (evidence toward integrability,
NOT a proof -- the algebraic Killing-tensor route §78/§85/§97/§99 is the proof side). The lens is the
DYNAMICAL companion to that algebraic route, now living on the analyzer beside petrov/tidal/komar.

Optional dep: numpy. Repro: .venv/bin/python scripts/109_integrability_lens.py
"""
import math
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
        print("INTEGRABILITY LENS: SKIPPED (numpy not installed)")
        return 0

    import sympy as sp

    from analyzer import integrability_signature
    from gr_engine import Geometry

    t, x, y, ph = sp.symbols("t x y phi", real=True)

    # Kerr a=3/5
    a = sp.Rational(3, 5)
    Sig = x**2 + a**2 * sp.cos(y)**2
    De = x**2 - 2 * x + a**2
    s2 = sp.sin(y)**2
    kerr = sp.zeros(4)
    kerr[0, 0] = -(1 - 2 * x / Sig)
    kerr[0, 3] = kerr[3, 0] = -2 * x * a * s2 / Sig
    kerr[1, 1] = Sig / De
    kerr[2, 2] = Sig
    kerr[3, 3] = (x**2 + a**2 + 2 * x * a**2 * s2 / Sig) * s2

    # Zipoy-Voorhees delta=2 (the §106 metric)
    F = ((x - 1) / (x + 1))**2
    H = ((x * x - 1) / (x * x - y * y))**4
    zv = sp.diag(-F, 1 / F * H * (x * x - y * y) / (x * x - 1),
                 1 / F * H * (x * x - y * y) / (1 - y * y), 1 / F * (x * x - 1) * (1 - y * y))

    print("INTEGRABILITY / CHAOS LENS on the general analyzer (one verdict per metric)\n")
    ok = []

    kr = integrability_signature(Geometry(kerr, [t, x, y, ph]), E=0.95, L=3.4, q2_eq=math.pi / 2,
                                 x0s=[7.5, 8.0, 8.5], bounds=((1.9, 200.0), (0.2, math.pi - 0.2)))
    okA = kr["n_chaotic"] == 0 and kr["n_sampled"] >= 3 and "integrable" in kr["verdict"]
    ok.append(okA)
    print(f"  (A) KERR (a=0.6): {kr['n_sampled']} orbits, {kr['n_chaotic']} chaotic")
    print(f"      verdict: {kr['verdict']}   {'✅' if okA else '❌'}")

    zr = integrability_signature(Geometry(zv, [t, x, y, ph]), E=0.95, L=3.0, q2_eq=0.0,
                                 x0s=[7.545, 7.560, 7.565, 8.0])
    fired = [o for o in zr["orbits"] if o[4] == "CHAOTIC"]
    okB = zr["n_chaotic"] >= 1 and "NON-INTEGRABLE" in zr["verdict"]
    ok.append(okB)
    print(f"\n  (B) ZV delta=2: {zr['n_sampled']} orbits, {zr['n_chaotic']} chaotic "
          f"(fired at x0={[round(o[0], 3) for o in fired]})")
    print(f"      verdict: {zr['verdict']}   {'✅' if okB else '❌'}")

    # (C) specificity: the island centre (x0=7.560) must read regular, not a blanket 'chaotic'
    centre = [o for o in zr["orbits"] if abs(o[0] - 7.560) < 1e-6]
    okC = bool(centre) and centre[0][4] == "regular"
    ok.append(okC)
    print(f"\n  (C) specificity — island centre x0=7.560 reads: "
          f"{centre[0][4] if centre else '??'} (must be regular, not blanket-chaotic)   "
          f"{'✅' if okC else '❌'}")

    passed = all(ok)
    print(f"\nINTEGRABILITY LENS: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Kerr integrable · ZV non-integrable thin-layer · specific — the toolchain, one verdict)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
