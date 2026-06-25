"""EXPLORATORY hunt #2 — reproduce the KNOWN Zipoy-Voorhees delta=2 chaos at the literature's
parameters (Lukes-Gerakopoulos 2012: E=0.95, Lz=3, section z=0). The chaos sits in a razor-thin
stochastic layer (chaotic at rho=7.518 vs regular at rho=7.548), so the scan must be FINE. This
validates our §84 Poincare/box-counting tool on a genuinely chaotic BLACK-HOLE spacetime (it has
only ever seen toy Henon-Heiles chaos + regular Kerr).
"""
import math
import sys

import sympy as sp

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from poincare import build_hamilton, box_dimension, section

t, x, y, ph = sp.symbols("t x y phi", real=True)


def zv(delta, sigma):
    s2 = sigma * sigma
    F = ((x - 1) / (x + 1))**delta
    H = ((x * x - 1) / (x * x - y * y))**(delta * delta)
    return sp.diag(-F, s2 / F * H * (x * x - y * y) / (x * x - 1),
                   s2 / F * H * (x * x - y * y) / (1 - y * y), s2 / F * (x * x - 1) * (1 - y * y))


def p_y_onshell(f, q1, q2, p1, E, L):
    val = (-1 - f["W"](q1, q2, E, L) - f["g11"](q1, q2, E, L) * p1 * p1) / f["g22"](q1, q2, E, L)
    return math.sqrt(val) if val > 0 else None


def hunt(sigma, E, L, x_lo, x_hi, dx):
    f = build_hamilton(zv(2.0, sigma), [t, x, y, ph], 1, 2, 0, 3)
    print(f"  sigma={sigma} (M={2*sigma}), E={E}, L={L}: scanning x0 in [{x_lo},{x_hi}] step {dx} "
          f"(rho=sigma*sqrt(x^2-1) at y=0)")
    best = []
    x0 = x_lo
    while x0 <= x_hi:
        py = p_y_onshell(f, x0, 0.0, 0.0, E, L)
        if py is not None and py > 0.05:
            pts, drift, st = section(f, [x0, 0.0, 0.0, py], E, L, sec_idx=1, sec_val=0.0,
                                     rec=(0, 2), n=140, h=0.02, maxst=900000,
                                     bounds=((1.2, 200.0), (-1.0, 1.0)))
            if len(pts) >= 40:
                bd, _ = box_dimension(pts)
                rho = sigma * math.sqrt(x0 * x0 - 1)
                tag = "  <<< CHAOTIC" if bd > 1.35 else ""
                if bd > 1.25 or tag:
                    print(f"    x0={x0:.3f} (rho={rho:.3f}): {len(pts)} pts box-dim={bd:.2f}{tag}", flush=True)
                best.append((x0, rho, bd, len(pts)))
        x0 += dx
    return best


if __name__ == "__main__":
    print("HUNT #2 — reproducing ZV delta=2 chaos at literature params (E=0.95, Lz=3)\n")
    allres = {}
    for sigma in (1.0, 0.5):
        res = hunt(sigma, 0.95, 3.0, 3.0, 12.0, 0.05)
        allres[sigma] = res
        ch = [r for r in res if r[2] > 1.35]
        print(f"  -> sigma={sigma}: {len(ch)} chaotic (box-dim>1.35) of {len(res)} bound orbits\n", flush=True)
    # report the most chaotic orbit found, and a nearby regular one (the thin-layer contrast)
    print("=== most chaotic orbits found ===")
    for sigma, res in allres.items():
        if not res:
            continue
        top = sorted(res, key=lambda r: -r[2])[:3]
        for (x0, rho, bd, n) in top:
            print(f"  sigma={sigma}: x0={x0:.3f} rho={rho:.3f} box-dim={bd:.2f} ({n} pts)")
