#!/usr/bin/env python3
"""Prototype — the integrability/chaos LENS: one verdict for any stationary-axisymmetric metric.

Folds §84/§105/§106/§107's toolchain into a single callable that samples bound orbits of a metric and
classifies the dynamics from the two validated section diagnostics — box_dimension (geometric) and
frequency_drift (area-blind, thin-layer). Honest three-valued: it can RULE IN chaos (a positive
detection on any sampled orbit) or report 'no chaos detected in the sampled orbits' (evidence toward
integrability, NOT a proof — the algebraic Killing-tensor route §78/§85/§97/§99 is the proof side).

  integrability_signature(g, coords, E, L, q2_eq, x0s, ...) -> dict:
      per-orbit (x0, box_dim, freq_drift, n, verdict) + overall {chaotic | thin-layer | no-chaos-detected}

This prototype validates it on Kerr (integrable -> no chaos) and ZV delta=2 (its known layer -> chaos),
before folding into analyzer.py + a gated battery.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from poincare import box_dimension, build_hamilton, frequency_drift, section

DRIFT_THR = 0.0115
BOX_CHAOS = 1.35


def integrability_signature(g, coords, E=0.95, L=3.0, q2_eq=0.0, x0s=None,
                            q1i=1, q2i=2, ti=0, phii=3, n=200, h=0.02, maxst=2_000_000,
                            bounds=((1.2, 200.0), (-0.999, 0.999))):
    """Sample bound orbits (launched at the radial turning point p1=0, p2 on-shell in the q2_eq plane)
    and classify each via box-dim + frequency-drift. Returns per-orbit data + an overall verdict."""
    f = build_hamilton(sp.Matrix(g), list(coords), q1i, q2i, ti, phii)
    if x0s is None:
        x0s = [6.0 + 0.5 * i for i in range(9)]
    orbits = []
    for x0 in x0s:
        val = (-1 - f["W"](x0, q2_eq, E, L)) / f["g22"](x0, q2_eq, E, L)
        if val <= 0:
            continue
        p2 = math.sqrt(val)
        # section/rec index the REDUCED STATE [q1,q2,p1,p2] (positions 0,1,2,3), NOT the coord indices
        pts, drift, st = section(f, [x0, q2_eq, 0.0, p2], E, L, sec_idx=1, sec_val=q2_eq,
                                 rec=(0, 2), n=n, h=h, maxst=maxst, bounds=bounds)
        if len(pts) < 60:
            orbits.append((x0, None, None, len(pts), "insufficient/plunge"))
            continue
        bd = box_dimension(pts)[0]
        fd = frequency_drift([p[0] for p in pts])
        chaotic = fd > DRIFT_THR or bd > BOX_CHAOS
        v = "CHAOTIC" if chaotic else "regular"
        orbits.append((x0, bd, fd, len(pts), v))
    good = [o for o in orbits if o[1] is not None]
    chaos = [o for o in good if o[4] == "CHAOTIC"]
    thin = [o for o in chaos if o[1] <= BOX_CHAOS]                 # drift fired but not area-filling
    if not good:
        verdict = "UNKNOWN (no bound orbits sampled)"
    elif chaos and len(thin) == len(chaos):
        verdict = "NON-INTEGRABLE (thin-layer chaos detected)"
    elif chaos:
        verdict = "NON-INTEGRABLE (chaos detected)"
    else:
        verdict = f"no chaos detected in {len(good)} sampled orbits (consistent with integrable)"
    return {"orbits": orbits, "verdict": verdict, "n_sampled": len(good), "n_chaotic": len(chaos)}


# ---- validation metrics ----
def kerr_g(coords):
    t, r, th, ph = coords
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
    return g


def zv_g(coords, delta=2.0, sigma=1.0):
    t, x, y, ph = coords
    s2 = sigma * sigma
    F = ((x - 1) / (x + 1))**delta
    H = ((x * x - 1) / (x * x - y * y))**(delta * delta)
    return sp.diag(-F, s2 / F * H * (x * x - y * y) / (x * x - 1),
                   s2 / F * H * (x * x - y * y) / (1 - y * y), s2 / F * (x * x - 1) * (1 - y * y))


if __name__ == "__main__":
    tt, xx, yy, pp = sp.symbols("t x y phi", real=True)
    print("INTEGRABILITY LENS — validation\n")

    print("KERR (a=0.6, integrable) — expect: no chaos detected:")
    r = integrability_signature(kerr_g([tt, xx, yy, pp]), [tt, xx, yy, pp], E=0.95, L=3.4,
                                q2_eq=math.pi / 2, x0s=[7.0, 7.5, 8.0, 8.5, 9.0],
                                bounds=((1.9, 200.0), (0.2, math.pi - 0.2)))
    for o in r["orbits"]:
        print(f"    x0={o[0]:.2f}: box-dim={o[1]}, drift={o[2]}, n={o[3]} -> {o[4]}")
    print(f"  VERDICT: {r['verdict']}\n")

    print("ZV delta=2 (has the §106 thin layer) — expect: chaos detected in the island-chain zone:")
    r = integrability_signature(zv_g([tt, xx, yy, pp]), [tt, xx, yy, pp], E=0.95, L=3.0, q2_eq=0.0,
                                x0s=[7.545, 7.560, 7.565, 7.60, 7.65, 8.0, 9.0])
    for o in r["orbits"]:
        print(f"    x0={o[0]:.3f}: box-dim={o[1]}, drift={o[2]}, n={o[3]} -> {o[4]}")
    print(f"  VERDICT: {r['verdict']}")
