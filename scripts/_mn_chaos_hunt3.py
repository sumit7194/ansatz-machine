"""EXPLORATORY hunt #3 — reach Manko-Novikov's BOUND CHAOTIC zone (the bridge's Ask B).
The equatorial apo-launch family (x0,y=0,px=0,py on-shell) found only regular orbits; the
documented MN chaos (Gair 2008; Lukes-Gerakopoulos 2010) lives at LOW angular momentum, in
the strong-field inner region. Scan low-L, deeper (small-x) launches across q, looking for a
bound orbit whose Poincare section fills an area (box-dim -> 2). That orbit then validates BOTH
chaos detectors (poincare.box_dimension AND the de-noised geodesic_chaos.lyapunov) on real chaos.
"""
import math
import sys

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from _mn_invariant import build_hamilton_numeric
from poincare import box_dimension, section


def py_onshell(f, x, y, px, E, L):
    val = (-1 - f["W"](x, y, E, L) - f["g11"](x, y, E, L) * px * px) / f["g22"](x, y, E, L)
    return math.sqrt(val) if val > 0 else None


def scan(M, a, q, EL_list, x0s, maxst=900000):
    f = build_hamilton_numeric(M, a, q)
    hits = []
    for (E, L) in EL_list:
        for x0 in x0s:
            py = py_onshell(f, x0, 0.0, 0.0, E, L)
            if py is None or py < 0.05:
                continue
            pts, drift, st = section(f, [x0, 0.0, 0.0, py], E, L, sec_idx=1, sec_val=0.0,
                                     rec=(0, 2), n=160, h=0.02, maxst=maxst, bounds=((1.05, 50.0), (-1.0, 1.0)))
            if len(pts) < 40:
                continue
            bd, _ = box_dimension(pts)
            tag = "  <<< CHAOTIC" if bd > 1.4 else ("  < borderline" if bd > 1.25 else "")
            if bd > 1.2:
                print(f"  q={q} E={E} L={L} x0={x0:.1f}: {len(pts):3d} pts box-dim={bd:.2f}{tag}", flush=True)
            hits.append((q, E, L, x0, bd, len(pts)))
    return hits


if __name__ == "__main__":
    print("HUNT #3 — Manko-Novikov bound chaos (low-L, inner region; bridge Ask B)\n")
    M, a = 1.0, 0.5
    # low angular momentum, deeper launches; sweep q (stronger bump = stronger chaos)
    EL = [(0.95, 1.8), (0.95, 2.2), (0.96, 1.8), (0.96, 2.2), (0.97, 2.0), (0.97, 2.5), (0.94, 2.0)]
    x0s = [3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0]
    allhits = []
    for q in (0.5, 0.7, 0.9, 1.2):
        print(f"--- q={q} ---", flush=True)
        allhits += scan(M, a, q, EL, x0s)
    chaos = sorted([h for h in allhits if h[4] > 1.4], key=lambda h: -h[4])
    print(f"\n=== {len(chaos)} chaotic orbit(s) (box-dim>1.4) ===")
    for h in chaos[:8]:
        print(f"  q={h[0]} E={h[1]} L={h[2]} x0={h[3]} -> box-dim={h[4]:.2f} ({h[5]} pts)")
    if not chaos:
        top = sorted(allhits, key=lambda h: -h[4])[:5]
        print("  none > 1.4; most-elevated:")
        for h in top:
            print(f"  q={h[0]} E={h[1]} L={h[2]} x0={h[3]} -> box-dim={h[4]:.2f}")
