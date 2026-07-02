#!/usr/bin/env python3
"""ZV delta=2 thin-layer refinement: fine x0 steps across the island-chain boundary + partitioned-launch
px variation (the §104 move -- §98 noted the layer is 'elusive to a 1D p_x=0 scan').

The coarse pass (_zv_freqdrift_hunt.py) found the structure at sigma=1, E=0.95, Lz=3:
plunge below x0~7.55 | island chain ~7.56-7.59 (box-dim 0.3-0.5 = near-periodic) | circulating tori above.
The stochastic layer hugs the island-chain separatrix -- BETWEEN 0.02-wide steps and possibly off the
p_x=0 axis. This refines: x0 step 0.002 across [7.545, 7.61] at p_x=0, then p_x-partitioned launches
(f_r = 0.15, 0.4) on the same bracket.

Exploratory. Repro: .venv/bin/python scripts/_zv_freqdrift_refine.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from poincare import build_hamilton, box_dimension, frequency_drift, section

t, x, y, ph = sp.symbols("t x y phi", real=True)
THR = 0.0115


def zv(delta, sigma):
    s2 = sigma * sigma
    F = ((x - 1) / (x + 1))**delta
    H = ((x * x - 1) / (x * x - y * y))**(delta * delta)
    return sp.diag(-F, s2 / F * H * (x * x - y * y) / (x * x - 1),
                   s2 / F * H * (x * x - y * y) / (1 - y * y), s2 / F * (x * x - 1) * (1 - y * y))


def probe(f, sigma, E, L, x0, fr, n=240, h=0.02, maxst=2_500_000):
    """launch at x0,y=0 with kinetic-energy fraction fr in p_x (fr=0 -> the old p_x=0 convention)."""
    ke = -1 - f["W"](x0, 0.0, E, L)
    g11 = f["g11"](x0, 0.0, E, L)
    g22 = f["g22"](x0, 0.0, E, L)
    if ke <= 0 or g11 <= 0 or g22 <= 0:
        return None
    px = -math.sqrt(fr * ke / g11)
    py = math.sqrt((1 - fr) * ke / g22)
    pts, dr, st = section(f, [x0, 0.0, px, py], E, L, sec_idx=1, sec_val=0.0,
                          rec=(0, 2), n=n, h=h, maxst=maxst, bounds=((1.2, 200.0), (-1.0, 1.0)))
    if len(pts) < 100:
        return ("plunge", len(pts), st)
    xs = [p[0] for p in pts]
    return ("ok", frequency_drift(xs), box_dimension(pts)[0], len(pts))


if __name__ == "__main__":
    sigma, E, L = 1.0, 0.95, 3.0
    f = build_hamilton(zv(2.0, sigma), [t, x, y, ph], 1, 2, 0, 3)
    hits = []
    for fr in (0.0, 0.15, 0.4):
        print(f"\n=== f_r={fr} (p_x fraction) ===")
        print("    x0       rho      result")
        x0 = 7.545
        while x0 <= 7.611:
            r = probe(f, sigma, E, L, x0, fr)
            rho = sigma * math.sqrt(x0 * x0 - 1)
            if r is None:
                pass
            elif r[0] == "plunge":
                print(f"    {x0:7.3f}  {rho:7.3f}  plunge ({r[1]} cross)", flush=True)
            else:
                _, fd, bd, np_ = r
                tag = "  <<< CHAOS (drift fires)" if fd > THR else ""
                print(f"    {x0:7.3f}  {rho:7.3f}  drift={fd:.4f} box-dim={bd:.3f} ({np_} cr){tag}", flush=True)
                if fd > THR:
                    hits.append((fr, x0, rho, fd, bd))
            x0 += 0.002
    print()
    if hits:
        print("=== DRIFT FIRES ===")
        for (fr, x0, rho, fd, bd) in hits:
            print(f"  f_r={fr}: x0={x0:.3f} rho={rho:.3f} drift={fd:.4f} box-dim={bd:.3f}")
    else:
        print("no drift in the refined bracket at any f_r")
