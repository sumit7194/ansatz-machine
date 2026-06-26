#!/usr/bin/env python3
"""Ask 2, principled attempt: MN bound chaos via the ROTATION NUMBER (the literature's tool).

Gross box-dimension scanning grazed MN chaos (max ~1.22) because the chaos is in THIN layers near
low-order resonances, not a gross area-filling sea (Lukes-Gerakopoulos-Apostolatos-Contopoulos 2010
detect it via the rotation number nu_theta/nu_r developing a PLATEAU across a resonance, with a thin
chaotic layer at the plateau's edge). So: scan a family of bound orbits, and for each compute BOTH
the box-dimension AND the rotation number on the Poincare section. A resonance shows as a plateau in
the rotation number; a chaotic layer shows as a box-dim spike + an erratic (non-monotone) rotation
number there. Run at clean moderate q (the q=0.95 second region abuts the metric's CTC pathology).

Exploratory; not a gated battery until a verdict is in.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _mn_invariant import build_hamilton_numeric
from poincare import section, box_dimension

M, a = 1.0, 0.5  # the standing test spin (clean metric; chaos here is the honest, non-pathological case)
E = 0.95


def rotation_number(pts):
    """mean angular advance per crossing about the section's center (turns/crossing).
    regular orbit -> smooth/convergent; resonance -> rational plateau; chaos -> erratic."""
    if len(pts) < 8:
        return None
    xc = sum(p[0] for p in pts) / len(pts)
    pc = sum(p[1] for p in pts) / len(pts)
    ang = [math.atan2(p[1] - pc, p[0] - xc) for p in pts]
    tot, n = 0.0, 0
    for i in range(1, len(ang)):
        d = ang[i] - ang[i - 1]
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        tot += d; n += 1
    return abs(tot / n) / (2 * math.pi) if n else None


def scan(q, Lz, x0s, bnds):
    f = build_hamilton_numeric(M, a, q)
    print(f"\nq={q}, Lz={Lz}: scanning {len(x0s)} bound orbits (box-dim + rotation number):")
    rows = []
    for x0 in x0s:
        try:
            W0 = f["W"](x0, 0.0, E, Lz); g22 = f["g22"](x0, 0.0, E, Lz)
        except Exception:
            continue
        ke = -1.0 - W0
        if ke <= 0 or g22 <= 0:
            continue
        py = math.sqrt(ke / g22)  # launch at radial turning point (px=0), full energy latitudinal
        pts, dr, st = section(f, [x0, 0.0, 0.0, py], E, Lz, sec_idx=1, sec_val=0.0, rec=(0, 2),
                              n=200, h=0.012, maxst=500000, bounds=bnds)
        if len(pts) < 40:
            print(f"    x0={x0:5.2f}: {len(pts):3d} cross (insufficient)")
            continue
        bd, _ = box_dimension(pts)
        rot = rotation_number(pts)
        flag = "  <-- CHAOS?" if bd > 1.35 else ""
        print(f"    x0={x0:5.2f}: {len(pts):3d} cross  box-dim={bd:.3f}  rot-num={rot:.4f}{flag}")
        rows.append((x0, bd, rot))
    return rows


if __name__ == "__main__":
    # outer bound region for q=0.5, E=0.95, Lz=3: a fine sweep of launch radii (each a different torus)
    x0s = [6.4 + 0.4 * i for i in range(20)]   # 6.4 .. 14.0 (trim the inner-edge separatrix)
    rows = scan(0.5, 3.0, x0s, ((2.0, 60.0), (-0.95, 0.95)))
    # a stronger bump (q=0.8) where deviations are larger -> resonance layers wider
    rows2 = scan(0.8, 3.0, [6.4 + 0.4 * i for i in range(20)], ((2.0, 60.0), (-0.95, 0.95)))

    allrows = rows + rows2
    if allrows:
        best = max(allrows, key=lambda r: r[1])
        print(f"\nmax box-dim across the sweep: {best[1]:.3f} at x0={best[0]:.2f}")
        print("CHAOS CONFIRMED (box-dim>1.35)" if best[1] > 1.35 else
              "no gross chaos; rotation-number plateaus/jumps mark where thin layers sit")
