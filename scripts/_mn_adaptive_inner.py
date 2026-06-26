#!/usr/bin/env python3
"""Adaptive-step Poincare section for MN's near-rod INNER CZV (the bridge's robust chaos target).

The literature's chaotic MN orbit (chi=0.9, q=0.95, E=0.95, Lz=3) lives in the inner permissible
region, between the rod (x=1) and a REAL A=0 surface at x~3. In prolate-spheroidal coords that zone
is coordinate-stiff (g_xx,g_yy->0 => g^xx,g^yy->inf => huge velocities), so poincare.section's
fixed-step RK4 dies there. This adds step-doubling error control: the step shrinks where the metric
is stiff and grows where it's smooth, with a floor so it can't stall at the rod. Metric is the EXACT
Manko-Novikov (verified vs Gair-Li-Mandel 2008); this is a pure numerical-integration upgrade.

Exploratory. Repro: .venv/bin/python scripts/_mn_adaptive_inner.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _mn_invariant import build_hamilton_numeric
from poincare import _rk4, H_value, box_dimension


def adaptive_section(f, s0, E, L, sec_val=0.0, n=250, h0=2e-4, hmin=1e-10, tol=1e-8,
                     maxst=8_000_000, bounds=((1.04, 2.2), (-0.95, 0.95))):
    """Section on q2 (y) up-crossing sec_val; record (x, px). Step-doubling adaptive RK4:
    accept the two-half-step result, halve h if the full-vs-half disagreement exceeds tol,
    grow h back when it's comfortably small. hmin floors the step so a stiff patch can't stall."""
    s = list(s0); h = h0; pts = []; Hs = []; prev = s[1] - sec_val; st = 0
    while len(pts) < n and st < maxst:
        if not (bounds[0][0] <= s[0] <= bounds[0][1] and bounds[1][0] <= s[1] <= bounds[1][1]):
            break
        try:
            sf = _rk4(f, s, h, E, L)
            sh = _rk4(f, _rk4(f, s, h / 2, E, L), h / 2, E, L)
        except (OverflowError, ZeroDivisionError, ValueError):
            if h > hmin * 4:
                h = h / 4; continue          # step flung us into a bad region -> refine and retry
            break                            # already at the floor: genuinely stuck
        err = max(abs(sf[i] - sh[i]) for i in range(4))
        if err > tol and h > hmin * 2:
            h = max(h / 2, hmin); continue          # reject, refine
        sn = sh; st += 1
        cur = sn[1] - sec_val
        if prev < 0 <= cur:
            fr = prev / (prev - cur)
            pts.append((s[0] + fr * (sn[0] - s[0]), s[2] + fr * (sn[2] - s[2])))
            Hs.append(H_value(f, sn, E, L))
        prev = cur; s = sn
        if err < tol / 10:
            h = min(h * 1.3, h0)                     # relax where smooth
    drift = (max(Hs) - min(Hs)) if Hs else float("inf")
    return pts, drift, st


if __name__ == "__main__":
    M, a, q = 1.0, 0.9, 0.95
    E, Lz = 0.95, 3.0
    f = build_hamilton_numeric(M, a, q)
    print(f"adaptive INNER-CZV section, exact MN chi=0.9 q=0.95 E=0.95 Lz=3 (literature chaos params):")
    print("  x0     cross  box-dim   H-drift    x-range          verdict")
    for x0 in [1.30, 1.38, 1.45, 1.52, 1.60]:
        try:
            W0 = f["W"](x0, 0.0, E, Lz); g22 = f["g22"](x0, 0.0, E, Lz)
        except Exception as e:
            print(f"  {x0:.2f}   metric raise ({type(e).__name__})"); continue
        if -1 - W0 <= 0 or g22 <= 0:
            print(f"  {x0:.2f}   not launchable (W={W0:.1f})"); continue
        py = math.sqrt((-1 - W0) / g22)
        pts, dr, st = adaptive_section(f, [x0, 0.0, 0.0, py], E, Lz)
        if len(pts) > 20:
            bd = box_dimension(pts)[0]
            xr = (min(p[0] for p in pts), max(p[0] for p in pts))
            v = "CHAOTIC" if bd > 1.3 else "regular" if bd < 1.15 else "intermediate"
            print(f"  {x0:.2f}   {len(pts):4d}   {bd:.3f}   {dr:.1e}   [{xr[0]:.3f},{xr[1]:.3f}]   {v}")
        else:
            print(f"  {x0:.2f}   {len(pts):4d}  cross (st={st}; stiffness floored h or A=0 wall)")
