"""EXPLORATORY — hunt for a chaotic geodesic in the Manko-Novikov (bumpy-Kerr) spacetime.
MN's chaos is documented as strong (ergodic regions; Gair et al 2008), unlike ZV's razor-thin
layer -- so this is the chance to SHOW a chaotic black-hole Poincare section. q=0 (Kerr) is the
regular control (box-dim ~1, KAM tori); q!=0 should show chaotic orbits (box-dim -> 2).
"""
import math
import sys

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from _mn_invariant import build_hamilton_numeric
from poincare import box_dimension, section


def p_y_onshell(f, x, y, p1, E, L):
    val = (-1 - f["W"](x, y, E, L) - f["g11"](x, y, E, L) * p1 * p1) / f["g22"](x, y, E, L)
    return math.sqrt(val) if val > 0 else None


def scan(q, E, L, x0s, maxst=700000):
    f = build_hamilton_numeric(1.0, 0.5, q)
    res = []
    for x0 in x0s:
        py = p_y_onshell(f, x0, 0.0, 0.0, E, L)
        if py is None or py < 0.05:
            continue
        pts, drift, st = section(f, [x0, 0.0, 0.0, py], E, L, sec_idx=1, sec_val=0.0,
                                 rec=(0, 2), n=120, h=0.02, maxst=maxst, bounds=((1.05, 60.0), (-1.0, 1.0)))
        if len(pts) < 30:
            continue
        bd, _ = box_dimension(pts)
        tag = "  <<< CHAOTIC" if bd > 1.4 else ""
        print(f"  q={q} x0={x0:.2f}: {len(pts):3d} pts, drift={drift:.0e}, box-dim={bd:.2f}{tag}", flush=True)
        res.append((q, x0, bd, len(pts)))
    return res


if __name__ == "__main__":
    print("HUNT — chaotic geodesics in Manko-Novikov (bumpy-Kerr) vs the q=0 (Kerr) control\n")
    x0s = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0]
    print("q=0 (Kerr) — expect ALL regular (box-dim ~1, integrable):")
    scan(0.0, 0.95, 2.8, x0s)
    print("\nq=0.5 (strongly bumpy) — hunting for chaos (box-dim > 1.4):")
    r5 = scan(0.5, 0.95, 2.8, x0s)
    print("\nq=0.9 (very bumpy):")
    r9 = scan(0.9, 0.95, 2.8, x0s)
    chaos = [r for r in (r5 + r9) if r[2] > 1.4]
    print(f"\n=== {len(chaos)} chaotic orbit(s) found ===")
    for r in sorted(chaos, key=lambda r: -r[2])[:5]:
        print(f"  q={r[0]} x0={r[1]} -> box-dim={r[2]:.2f} ({r[3]} pts)")
