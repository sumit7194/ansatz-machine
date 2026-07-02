#!/usr/bin/env python3
"""Step 106 — Zipoy-Voorhees' own thin-layer chaos, exhibited (closes §97/§98's elusive target).

§97/§98 proved ZV delta!=1 non-integrable ALGEBRAICALLY (no rank-2 or rank-4 Killing tensor) but the
GEOMETRIC chaos stayed a cited-literature caveat: box-dim scans grazed it (the delta=2 stochastic layer
at E=0.95, Lz=3 is razor-thin -- Lukes-Gerakopoulos PRD 86, 044013). §105's area-blind frequency-drift
detector re-hunts it and finds the layer's full anatomy at the plunge separatrix (sigma=1, x0 steps of
0.002 at p_x=0):

    plunge | LAYER (x0=7.545: drift 0.027, escapes after 210 crossings)
           | island chain (7.555-7.563: drift ~1e-4, box-dim 0.3-0.7, never escapes)
           | LAYER (x0=7.565: drift 0.013, escapes after 184 crossings) | circulating tori (7.60+)

The chaos verdict rests on TWO independent signatures the regular neighbors never show: the frequency
drift fires (with the dominant frequency WANDERING progressively along the series), and the orbit has a
FINITE bounded lifetime -- it sticks for ~200 crossings then escapes through the separatrix (chaotic
transport; KAM tori are eternal). H-drift ~1e-12 throughout (the signal is physics, not integration).
Honest notes: (i) this is TRANSIENT/sticky layer chaos -- the drift magnitude varies with the integration
step (exponential shadowing sensitivity: different h = a different realization of the same layer), but
BOTH signatures persist at h and h/2 while the island/torus controls show neither at any h; (ii) the layer
sits at rho~7.48-7.50 vs the literature's quoted 7.518 (~0.5%; units/convention nuance) -- we exhibit the
documented layer's existence at the documented (delta, E, Lz), not the exact quoted coordinate.

With §105 (Manko-Novikov), BOTH exact bumpy-BH metrics in the engine now have their non-integrability
(§97-§99) backed by an exhibited geometric chaos positive-control, each settled by the frequency-drift
detector where box-dim was ambiguous.

Optional dep: numpy (frequency_drift's FFT). Repro: .venv/bin/python scripts/106_zv_thin_layer_chaos.py
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

THR = 0.0115


def main():
    if not _HAVE_NUMPY:
        print("ZV THIN-LAYER CHAOS: SKIPPED (numpy not installed)")
        return 0

    import sympy as sp
    from poincare import build_hamilton, box_dimension, frequency_drift, section

    t, x, y, ph = sp.symbols("t x y phi", real=True)
    delta, sigma = 2.0, 1.0
    s2 = sigma * sigma
    F = ((x - 1) / (x + 1))**delta
    H = ((x * x - 1) / (x * x - y * y))**(delta * delta)
    g = sp.diag(-F, s2 / F * H * (x * x - y * y) / (x * x - 1),
                s2 / F * H * (x * x - y * y) / (1 - y * y), s2 / F * (x * x - 1) * (1 - y * y))
    f = build_hamilton(g, [t, x, y, ph], 1, 2, 0, 3)
    E, L = 0.95, 3.0

    def probe(x0, n=240, h=0.02, maxst=2_500_000):
        val = (-1 - f["W"](x0, 0.0, E, L)) / f["g22"](x0, 0.0, E, L)
        py = math.sqrt(val)
        pts, dr, st = section(f, [x0, 0.0, 0.0, py], E, L, sec_idx=1, sec_val=0.0,
                              rec=(0, 2), n=n, h=h, maxst=maxst, bounds=((1.2, 200.0), (-1.0, 1.0)))
        xs = [p[0] for p in pts]
        fd = frequency_drift(xs) if len(xs) >= 100 else None
        bd = box_dimension(pts)[0] if len(pts) >= 100 else None
        return len(pts), fd, bd, dr

    print("ZIPOY-VOORHEES delta=2 THIN-LAYER CHAOS (E=0.95, Lz=3; the §97/§98 elusive target)\n")
    ok = []

    # (A) the stochastic layer at the plunge separatrix: drift FIRES + FINITE bounded lifetime
    nA, fdA, bdA, drA = probe(7.545)
    okA = fdA is not None and fdA > THR and nA < 240 and drA < 1e-9
    ok.append(okA)
    print(f"  (A) LAYER orbit x0=7.545 (rho=7.478): drift={fdA:.4f} (fires >{THR}), "
          f"{nA} crossings then ESCAPES (<240), H-drift={drA:.0e}")
    print(f"      both chaos signatures: frequency wander + finite lifetime (tori are eternal)   "
          f"{'✅' if okA else '❌'}")

    # (B) the island of stability two steps away: drift ~0 and NEVER escapes
    nB, fdB, bdB, drB = probe(7.557)
    okB = fdB is not None and fdB < 0.005 and nB >= 240
    ok.append(okB)
    print(f"\n  (B) ISLAND orbit x0=7.557 (rho=7.491): drift={fdB:.4f}, {nB} crossings (survives), "
          f"box-dim={bdB:.2f}")
    print(f"      the razor-thin contrast: {(fdA/max(fdB,1e-6)):.0f}x drift ratio 0.012 apart in x0   "
          f"{'✅' if okB else '❌'}")

    # (C) a circulating torus above the chain: also quiet (the detector isn't just flagging everything)
    nC, fdC, bdC, drC = probe(7.62)
    okC = fdC is not None and fdC < 0.005 and nC >= 240
    ok.append(okC)
    print(f"\n  (C) TORUS orbit x0=7.62 (rho=7.554): drift={fdC:.4f}, {nC} crossings (survives), "
          f"box-dim={bdC:.2f}")
    print(f"      regular background reads quiet -> the layer signal is specific, not generic   "
          f"{'✅' if okC else '❌'}")

    passed = all(ok)
    print(f"\nZV THIN-LAYER CHAOS: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(the documented delta=2 stochastic layer exhibited; §97/§98's geometric caveat closed)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
