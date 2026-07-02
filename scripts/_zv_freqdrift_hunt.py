#!/usr/bin/env python3
"""ZV delta=2 thin-layer chaos via the frequency-drift detector (the §105 playbook, applied to §97/§98's
elusive target).

Lukes-Gerakopoulos 2012 (PRD 86, 044013): ZV delta=2, E=0.95, Lz=3 has a RAZOR-THIN stochastic layer --
chaotic at rho=7.518 vs regular at rho=7.548. Box-dim scans (_zv_chaos_hunt2.py) missed it: the layer is
too thin to fill area. poincare.frequency_drift is area-blind (validated §105: MN's thin layer fired 0.98
where box-dim read a borderline 1.22), so this re-hunts with the right tool.

Convention note: rho = sigma*sqrt(x0^2-1) at y=0, and M = delta*sigma. hunt2 scanned x0 in [3,12] for BOTH
sigma=1.0 and sigma=0.5 -- but at sigma=0.5 the literature layer (rho=7.518) sits at x0~15.07, OUTSIDE that
range. So the layer may never have been sampled at the M=1 convention. This scan brackets it at both.

Exploratory. Repro: .venv/bin/python scripts/_zv_freqdrift_hunt.py
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


def hunt(sigma, E, L, x0s, n=240, h=0.02, maxst=2_500_000):
    f = build_hamilton(zv(2.0, sigma), [t, x, y, ph], 1, 2, 0, 3)
    hits = []
    print(f"  sigma={sigma} (M={2*sigma}), E={E}, Lz={L}:")
    print(f"    x0       rho      cross  box-dim  freq-drift   verdict")
    for x0 in x0s:
        val = (-1 - f["W"](x0, 0.0, E, L)) / f["g22"](x0, 0.0, E, L)
        if val <= 0:
            continue
        py = math.sqrt(val)
        pts, dr, st = section(f, [x0, 0.0, 0.0, py], E, L, sec_idx=1, sec_val=0.0,
                              rec=(0, 2), n=n, h=h, maxst=maxst, bounds=((1.2, 200.0), (-1.0, 1.0)))
        if len(pts) < 100:
            print(f"    {x0:7.3f}  {sigma*math.sqrt(x0*x0-1):7.3f}  {len(pts):4d}  (insufficient, st={st})",
                  flush=True)
            continue
        xs = [p[0] for p in pts]
        fd = frequency_drift(xs)
        bd = box_dimension(pts)[0]
        rho = sigma * math.sqrt(x0 * x0 - 1)
        tag = "  <<< CHAOS (drift fires)" if fd > THR else ""
        print(f"    {x0:7.3f}  {rho:7.3f}  {len(pts):4d}   {bd:5.3f}   {fd:8.4f} {tag}", flush=True)
        if fd > THR:
            hits.append((sigma, x0, rho, fd, bd))
    return hits


if __name__ == "__main__":
    print("ZV delta=2 thin-layer hunt with frequency_drift (literature: chaotic rho=7.518, regular 7.548)\n")
    hits = []
    # sigma=1.0 (M=2): literature rho=7.518 -> x0 = sqrt((7.518)^2+1) ~ 7.584; fine bracket
    hits += hunt(1.0, 0.95, 3.0, [7.40 + 0.02 * i for i in range(16)])          # x0 7.40..7.70
    # sigma=0.5 (M=1): rho=7.518 -> x0 ~ 15.07; hunt2 NEVER scanned here
    hits += hunt(0.5, 0.95, 3.0, [14.90 + 0.03 * i for i in range(12)])         # x0 14.90..15.23
    print()
    if hits:
        print("=== DRIFT FIRES (thin-layer chaos candidates) ===")
        for (s, x0, rho, fd, bd) in hits:
            print(f"  sigma={s}: x0={x0:.3f} rho={rho:.3f} drift={fd:.4f} box-dim={bd:.3f}")
    else:
        print("no drift above threshold anywhere in the bracket -- layer thinner than sampled or elsewhere")
