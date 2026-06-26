#!/usr/bin/env python3
"""Ask 2 (the bridge): hunt MN's OWN bound chaos in the second permissible region.

After the asymptotic-flatness gauge-fix made the high-quadrupole metric computable, map the
permissible regions at the literature params (chi=0.9, q=0.95, E=0.95, Lz=3) and launch bound
orbits in the SECOND (inner) region — where MN's documented chaos lives (Gair-Li-Mandel 2008;
Lukes-Gerakopoulos-Apostolatos-Contopoulos 2010). Box-dimension is the primary verdict
(geometric, roundoff-immune); de-noised lambda alongside. The outer region is the regular control.

Exploratory (underscore-prefixed; not a gated battery until a verdict is in).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _mn_invariant import build_hamilton_numeric
from poincare import section, box_dimension

M, a, q = 1.0, 0.9, 0.95
E, Lz = 0.95, 3.0
f = build_hamilton_numeric(M, a, q)


def physical(x, y):
    """allowed (W<=-1) AND metric non-degenerate (g^xx,g^yy>0, i.e. MN's A>0)."""
    try:
        return (f["W"](x, y, E, Lz) <= -1.0
                and f["g11"](x, y, E, Lz) > 0.0 and f["g22"](x, y, E, Lz) > 0.0)
    except Exception:
        return False


def run(x0, y0, frac, bnds, lab):
    """launch a bound orbit, partitioning kinetic energy frac:(1-frac) into (px:py); section on y0."""
    try:
        W0 = f["W"](x0, y0, E, Lz); g11 = f["g11"](x0, y0, E, Lz); g22 = f["g22"](x0, y0, E, Lz)
    except Exception as e:
        print(f"  {lab}: x0={x0:.2f} frac={frac:.1f}: metric raised at launch ({type(e).__name__})")
        return None
    ke = -1.0 - W0
    if ke <= 0 or g11 <= 0 or g22 <= 0:
        print(f"  {lab}: x0={x0:.2f} frac={frac:.1f}: not launchable (ke={ke:.2f})")
        return None
    px = math.sqrt(frac * ke / g11); py = math.sqrt((1 - frac) * ke / g22)
    pts, dr, st = section(f, [x0, y0, px, py], E, Lz, sec_idx=1, sec_val=y0, rec=(0, 2),
                          n=300, h=0.01, maxst=1200000, bounds=bnds)
    if len(pts) > 30:
        bd, _ = box_dimension(pts)
        xr = (min(p[0] for p in pts), max(p[0] for p in pts))
        verdict = "CHAOTIC" if bd > 1.45 else "regular" if bd < 1.30 else "INTERMEDIATE/thin-layer"
        print(f"  {lab}: x0={x0:.2f} frac={frac:.1f}: {len(pts):4d} cross  x[{xr[0]:.2f},{xr[1]:.2f}]  "
              f"box-dim={bd:.3f} -> {verdict}")
        return bd
    print(f"  {lab}: x0={x0:.2f} frac={frac:.1f}: only {len(pts)} cross (escaped/crashed st={st})")
    return None


if __name__ == "__main__":
    # 1. permissible intervals at y=0
    xs = [1.02 + 0.02 * i for i in range(1500)]
    ints, start = [], None
    for x in xs:
        ok = physical(x, 0.0)
        if ok and start is None:
            start = x
        if not ok and start is not None:
            ints.append((start, x - 0.02)); start = None
    if start is not None:
        ints.append((start, xs[-1]))
    print(f"physical permissible intervals (W<=-1 AND non-degenerate), y=0:")
    for s, e in ints:
        print(f"    x in [{s:.2f}, {e:.2f}]")
    print()

    # 2. scan the SECOND region (the bound pocket separate from the outer one)
    print("SECOND-REGION pocket orbits (candidate MN bound chaos):")
    pocket = [iv for iv in ints if iv[0] < 5.0 and iv[1] - iv[0] > 0.3 and iv[0] > 2.0]
    if pocket:
        s, e = pocket[0]
        bnds = ((max(1.5, s - 0.3), e + 0.3), (-0.9, 0.9))
        for x0 in [s + (e - s) * fr for fr in (0.3, 0.5, 0.7)]:
            for frac in (0.2, 0.5, 0.8):
                run(x0, 0.0, frac, bnds, "pocket")
    else:
        print("    (no clean second pocket found at y=0)")

    # 3. outer-region control (must read regular)
    print("\nOUTER-region control (must read regular):")
    run(12.0, 0.0, 0.5, ((5.4, 40.0), (-0.9, 0.9)), "outer ")
