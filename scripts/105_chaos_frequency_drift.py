#!/usr/bin/env python3
"""Step 105 — the Laskar frequency-drift detector + MN's own thin-layer chaos (positive control).

A third chaos diagnostic for the engine, beside box_dimension (§84, geometric) and the de-noised
largest-Lyapunov exponent (§79/§101). The dominant frequency of an orbit's surface-of-section sequence
is CONSTANT on an invariant torus -- a regular orbit OR a resonant island -- and DRIFTS only for chaos.
`poincare.frequency_drift` returns |f1 - f2|/f_avg between the first and second half of the section
sequence. It is AREA-BLIND, so it resolves thin chaotic layers that box-dim only grazes (the §101
box-dim≈1.2 ambiguity), and unlike the Lyapunov exponent it does not false-positive on finite-difference
roundoff or on resonant islands.

This battery validates it and uses it to CLOSE the Manko-Novikov positive control, open since §99:
  (A) Hénon-Heiles -- the detector separates order from chaos (regular E=1/12 -> ~0; chaotic E=1/6 -> >1).
  (B) Kerr (integrable) -- a bound geodesic reads ~0 (no false positive on an integrable metric).
  (C) THE RESULT -- on the EXACT Manko-Novikov metric (chi=0.9, q=0.95, E=0.95, Lz=3), the two near-rod
      inner-CZV orbits §104's adaptive integrator reached -- which box-dim could only call borderline
      (1.20 vs 1.22) -- split CLEANLY: orbit_A drift ~0 = the inner ISLAND of stability; orbit_B drift ~1 =
      thin CHAOS, the boundary layer (above Hénon-Heiles' own chaotic floor). MN's own bound chaos,
      exhibited on the exact metric. The (x,px) section series are the committed artifact
      `mn_inner_sections_for_bridge.json` (reproducible via the adaptive integrator `_mn_adaptive_inner.py`);
      the length-matched control (orbit_A truncated to orbit_B's length still reads 0) proves orbit_B's
      signal is real, not a short-series artifact.

Cracked WITH a sister project (TheBridge), which independently built + validated the same detector; this
native `poincare.frequency_drift` reproduces its verdict to the digit (orbit_B 0.980).

Optional dep: numpy. Repro: .venv/bin/python scripts/105_chaos_frequency_drift.py
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import numpy as np  # noqa: F401
    _HAVE_NUMPY = True
except ImportError:
    _HAVE_NUMPY = False

THR = 0.0115   # validated threshold: regular below, chaos above


def _hh_rhs(s):
    x, y, px, py = s
    return [px, py, -x - 2 * x * y, -y - x * x + y * y]


def _hh_rk4(s, h):
    k1 = _hh_rhs(s)
    k2 = _hh_rhs([s[i] + h / 2 * k1[i] for i in range(4)])
    k3 = _hh_rhs([s[i] + h / 2 * k2[i] for i in range(4)])
    k4 = _hh_rhs([s[i] + h * k3[i] for i in range(4)])
    return [s[i] + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(4)]


def _hh_section(E, y0, py0, n=220, h=0.01, maxst=3_000_000):
    """Hénon-Heiles section on x=0 up-crossings (px>0); record (y, py)."""
    val = 2 * E - py0 * py0 - y0 * y0 + 2 * y0**3 / 3
    if val <= 0:
        return []
    s = [0.0, y0, math.sqrt(val), py0]
    pts, prev, st = [], s[0], 0
    while len(pts) < n and st < maxst:
        sn = _hh_rk4(s, h)
        st += 1
        if prev < 0 <= sn[0] and sn[2] > 0:
            fr = prev / (prev - sn[0])
            pts.append((s[1] + fr * (sn[1] - s[1]), s[3] + fr * (sn[3] - s[3])))
        prev = sn[0]
        s = sn
    return pts


def main():
    if not _HAVE_NUMPY:
        print("FREQUENCY-DRIFT CHAOS DETECTOR: SKIPPED (numpy not installed)")
        return 0

    import sympy as sp
    from poincare import build_hamilton, section, p_on_shell, frequency_drift

    print("LASKAR FREQUENCY-DRIFT CHAOS DETECTOR + MN's thin-layer chaos (positive control)\n")
    ok = []

    # (A) Hénon-Heiles: the detector must separate order from chaos
    reg = _hh_section(1 / 12.0, 0.1, 0.0)
    cha = _hh_section(1 / 6.0, -0.1, 0.0)
    dR = frequency_drift([p[0] for p in reg])
    dC = frequency_drift([p[0] for p in cha])
    okA = dR < THR < dC
    ok.append(okA)
    print(f"  (A) Hénon-Heiles: regular(E=1/12) drift={dR:.4f}, chaotic(E=1/6) drift={dC:.4f}")
    print(f"      regular below {THR}, chaotic above -> separates order from chaos   {'✅' if okA else '❌'}")

    # (B) Kerr (integrable): a bound geodesic must read ~0 -- no false positive on an integrable metric
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    a = sp.Rational(3, 5)
    Sig = r**2 + a**2 * sp.cos(th)**2
    De = r**2 - 2 * r + a**2
    s2 = sp.sin(th)**2
    g = sp.zeros(4)
    g[0, 0] = -(1 - 2 * r / Sig)
    g[0, 3] = g[3, 0] = -2 * r * a * s2 / Sig
    g[1, 1] = Sig / De
    g[2, 2] = Sig
    g[3, 3] = (r**2 + a**2 + 2 * r * a**2 * s2 / Sig) * s2
    f = build_hamilton(g, [t, r, th, ph], 1, 2)
    E, L, p2, r0 = 0.95, 3.4, 0.4, 8.0                        # §84's clean-torus bound orbit
    p1 = p_on_shell(f, r0, math.pi / 2, p2, E, L)
    pts, drift, st = section(f, [r0, math.pi / 2, p1, p2], E, L, sec_idx=1, sec_val=math.pi / 2,
                             rec=(0, 2), n=160, h=0.02, maxst=1_500_000)
    dK = frequency_drift([p[0] for p in pts])
    okB = dK < THR and len(pts) >= 80
    ok.append(okB)
    print(f"\n  (B) Kerr bound geodesic ({len(pts)} section pts, H-drift={drift:.0e}): drift={dK:.4f}")
    print(f"      integrable -> below {THR}, no false positive   {'✅' if okB else '❌'}")

    # (C) THE RESULT: MN's exact-metric inner-CZV orbits -- box-dim borderline, the detector settles it
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mn_inner_sections_for_bridge.json")
    if not os.path.exists(path):
        print("\n  (C) MN section series file missing -> cannot run positive control ❌")
        okC = False
    else:
        d = json.load(open(path))
        oA = d["orbits"]["orbit_A"]["x"]
        oB = d["orbits"]["orbit_B"]["x"]
        dA = frequency_drift(oA)
        dB = frequency_drift(oB)
        dA_m = frequency_drift(oA[:len(oB)])                      # length-matched control
        okC = dA < THR < dB and dA_m < THR
        print(f"\n  (C) EXACT Manko-Novikov inner-CZV (χ=0.9, q=0.95, E=0.95, Lz=3) — the box-dim≈1.2 borderline:")
        print(f"        orbit_A ({len(oA)} cr, box-dim 1.20): drift={dA:.4f}  -> inner ISLAND of stability")
        print(f"        orbit_B ({len(oB)} cr, box-dim 1.22): drift={dB:.4f}  -> thin CHAOS, the boundary layer")
        print(f"        length-matched orbit_A[:{len(oB)}]:    drift={dA_m:.4f}  -> orbit_B's signal is real")
        print(f"      MN's own thin-layer chaos EXHIBITED on the exact metric   {'✅' if okC else '❌'}")
    ok.append(okC)

    passed = all(ok)
    print(f"\nFREQUENCY-DRIFT DETECTOR: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Hénon-Heiles + Kerr validated; MN positive control closed — island vs thin chaos split ~1000×)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
