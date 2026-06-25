"""EXPLORATORY hunt — find a chaotic geodesic in the Zipoy-Voorhees (delta!=1) spacetime.
An integrable system has NO chaotic orbits, so a single clearly-chaotic section (box-dim
well above 1) is a proof of non-integrability. delta=1 (Schwarzschild) is the regular control.
"""
import math
import sys

import sympy as sp

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from poincare import build_hamilton, box_dimension, section

t, x, y, ph = sp.symbols("t x y phi", real=True)


def zv_sympy(delta, sigma):
    s2 = sigma * sigma
    F = ((x - 1) / (x + 1))**delta
    H = ((x * x - 1) / (x * x - y * y))**(delta * delta)
    return sp.diag(-F, s2 / F * H * (x * x - y * y) / (x * x - 1),
                   s2 / F * H * (x * x - y * y) / (1 - y * y), s2 / F * (x * x - 1) * (1 - y * y))


def p_y_onshell(f, q1, q2, p1, E, L):
    val = (-1 - f["W"](q1, q2, E, L) - f["g11"](q1, q2, E, L) * p1 * p1) / f["g22"](q1, q2, E, L)
    return math.sqrt(val) if val > 0 else None


def scan(delta, EL_list, x0s, maxst=1_600_000):
    sigma = 1.0 / delta
    f = build_hamilton(zv_sympy(delta, sigma), [t, x, y, ph], 1, 2, 0, 3)
    found = []
    for (E, L) in EL_list:
        for x0 in x0s:
            py = p_y_onshell(f, x0, 0.0, 0.0, E, L)
            if py is None:
                continue
            pts, drift, st = section(f, [x0, 0.0, 0.0, py], E, L, sec_idx=1, sec_val=0.0,
                                     rec=(0, 2), n=180, h=0.02, maxst=maxst,
                                     bounds=((1.2, 120.0), (-1.0, 1.0)))
            if len(pts) < 40:
                continue
            bd, _ = box_dimension(pts)
            tag = "CHAOTIC" if bd > 1.4 else ("regular" if bd < 1.2 else "borderline")
            print(f"  delta={delta} E={E} L={L} x0={x0:5.1f}: {len(pts):3d} pts drift={drift:.0e} "
                  f"box-dim={bd:.2f}  {tag}", flush=True)
            found.append((delta, E, L, x0, bd, len(pts)))
    return found


if __name__ == "__main__":
    print("HUNT — chaotic geodesics in Zipoy-Voorhees (delta=2) vs the Schwarzschild control\n")
    print("delta=1 (Schwarzschild) — expect ALL regular (box-dim ~ 1):")
    scan(1.0, [(0.97, 4.0)], [8.0, 11.0, 14.0, 18.0])
    print("\ndelta=2 (deformed) — hunting for chaos (box-dim > 1.4 = non-integrable):")
    res = scan(2.0, [(0.93, 3.0), (0.95, 3.0), (0.95, 3.5), (0.96, 3.5), (0.97, 4.0)],
               [3.5, 4.5, 6.0, 8.0, 11.0, 15.0, 20.0])
    chaos = [r for r in res if r[4] > 1.4]
    print(f"\n=== {len(chaos)} chaotic orbit(s) found for delta=2 ===")
    for r in sorted(chaos, key=lambda r: -r[4]):
        print(f"  E={r[1]} L={r[2]} x0={r[3]} -> box-dim={r[4]:.2f} ({r[5]} pts)")
