"""EXPLORATORY — the §85 numerical second-invariant search applied to the EXACT Zipoy-Voorhees
vacuum metric (closed form, no interpolation). Does a Carter-like conserved quadratic survive
the quadrupole deformation delta?

VALIDATION GATE (same logic as _qinvariant on Kerr): delta=1 IS Schwarzschild, whose Carter
constant in these prolate-spheroidal coords is K = (1-y^2) p_y^2 + L^2/(1-y^2) — it lives in
the basis below, so the search MUST return one machine-zero singular value there. Only then is
the delta!=1 result (expected: NO machine-zero SV ⇒ no second invariant) trustworthy.

This is the algebraic companion to the Poincaré/chaos test: chaos shows non-integrability
geometrically; the absent conserved quadratic shows it algebraically. Two independent detectors.
"""

import math
import sys

import numpy as np
import sympy as sp

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from poincare import _rk4, build_hamilton, p_on_shell

t, x, y, ph = sp.symbols("t x y phi", real=True)


def metric(delta):
    sigma = 1.0 / delta                      # fix mass M = sigma*delta = 1
    s2 = sigma * sigma
    F = ((x - 1) / (x + 1))**delta
    H = ((x * x - 1) / (x * x - y * y))**(delta * delta)
    g = sp.diag(-F, s2 / F * H * (x * x - y * y) / (x * x - 1),
                s2 / F * H * (x * x - y * y) / (1 - y * y), s2 / F * (x * x - 1) * (1 - y * y))
    return build_hamilton(g, [t, x, y, ph], 1, 2, 0, 3)


def trajectory(f, E, L, p2, x0, steps=9000, h=0.02):
    p1 = p_on_shell(f, x0, 0.0, p2, E, L)            # start on equator y=0, p_y=p2, solve p_x
    if p1 is None:
        return None
    s = [x0, 0.0, p1, p2]
    pts = []
    for _ in range(steps):
        try:
            s = _rk4(f, s, h, E, L)
        except (OverflowError, ZeroDivisionError, ValueError):
            break
        if s[0] < 1.3 or s[0] > 120 or abs(s[1]) > 0.999:
            break
        pts.append(tuple(s))
    return pts


def basis(s):
    x_, y_, px, py = s
    om = 1.0 - y_ * y_
    # mirror of the Kerr/_qinvariant basis: u->y, sin^2->om, r->x. Contains the delta=1
    # Carter constant (1-y^2)py^2 + L^2/(1-y^2) = py^2 - y^2 py^2 + L^2(y^2/om) (+const).
    return [py * py, px * px, px * py,
            y_ * y_, y_ * y_ / om,
            py * py * y_ * y_, px * px * y_ * y_,
            x_ * py * py, x_ * x_ * py * py, px * px * x_, px * px * x_ * x_]


BNAMES = ["py2", "px2", "px*py", "y2", "y2/om", "py2*y2", "px2*y2",
          "x*py2", "x2*py2", "px2*x", "px2*x2"]


def check_independence():
    rng = [[(4 + 14 * ((i * 37 + j * 13) % 100) / 100),
            (-0.7 + 1.4 * ((i * 7 + j * 29) % 100) / 100),
            (-1 + 2 * ((i * 17 + j * 5) % 100) / 100),
            (-1 + 2 * ((i * 3 + j * 41) % 100) / 100)]
           for i in range(40) for j in range(2)]
    Phi = np.array([basis(s) for s in rng], dtype=float)
    Phi = Phi - Phi.mean(axis=0, keepdims=True)
    S = np.linalg.svd(Phi / (np.linalg.norm(Phi, axis=0) + 1e-30), compute_uv=False)
    return S[-1]


def fit(f, E, L, p2list, x0):
    blocks, used = [], 0
    for p2 in p2list:
        pts = trajectory(f, E, L, p2, x0)
        if not pts or len(pts) < 2500:
            continue
        used += 1
        sub = pts[:: max(1, len(pts) // 250)]
        Phi = np.array([basis(s) for s in sub], dtype=float)
        Phi = Phi - Phi.mean(axis=0, keepdims=True)
        blocks.append(Phi)
    if len(blocks) < 3:
        return None, used, None
    D = np.vstack(blocks)
    scale = np.linalg.norm(D, axis=0) + 1e-30
    U, S, Vt = np.linalg.svd(D / scale, full_matrices=False)
    inv_vec = Vt[-1] / scale
    inv_vec = inv_vec / np.max(np.abs(inv_vec))
    return S, used, inv_vec


if __name__ == "__main__":
    E, L, x0 = 0.97, 4.0, 11.0
    p2list = [round(0.06 + 0.05 * k, 3) for k in range(16)]
    indep = check_independence()
    print(f"basis independence (smallest SV on random points, must be >0): {indep:.2e}  "
          f"{'OK' if indep > 1e-6 else 'DEGENERATE!'}\n", flush=True)
    print("smallest 5 singular values; GENUINE invariant ⇒ smallest ≈1e-12 AND a big gap:\n", flush=True)
    for delta in (1.0, 0.8, 1.3, 2.0):
        f = metric(delta)
        S, used, vec = fit(f, E, L, p2list, x0)
        if S is None:
            print(f"  delta={delta}: too few bound orbits at this (E,L)"); continue
        tail = ", ".join(f"{v:.2e}" for v in S[-5:])
        gap = S[-2] / S[-1] if S[-1] > 0 else float("inf")
        lab = "delta=1 (Schwarzschild)" if delta == 1.0 else f"delta={delta} (deformed)"
        print(f"  {lab:24s} [{used:2d} orbits]: {tail}   gap={gap:.1e}", flush=True)
        if S[-1] < 1e-8 and gap > 50:
            terms = sorted(zip(BNAMES, vec), key=lambda kv: -abs(kv[1]))[:5]
            print("        invariant ≈ " + " + ".join(f"{c:+.3f}·{n}" for n, c in terms), flush=True)
