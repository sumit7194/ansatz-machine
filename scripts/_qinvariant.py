"""EXPLORATORY (underscore = not a battery). NUMERICAL second-invariant search for the
quadrupole-deformed Kerr — the tractable replacement for the swamped symbolic route
(_killing_search.py). Does a Carter-like conserved quantity survive the deformation?

Method (multi-orbit null space): a quadratic-in-momenta invariant C = Σ c_k φ_k(state)
is CONSTANT along each orbit. Sample several orbits (fixed E,L, varied inclination → varied
Carter value), mean-subtract per orbit (kills the additive constant), stack, and SVD. A
genuine invariant is a right-singular vector with a near-ZERO singular value (≈1e-10),
well separated from the rest. VALIDATION GATE: on Kerr this must recover the Carter
constant (exactly one machine-zero singular value). Only then is the deformed result
trustworthy. Singular value ~ε (not ~1e-10) ⇒ Kerr-Q only approximately works ⇒ NO exact
second invariant in the basis.
"""

import math
import sys

import numpy as np
import sympy as sp

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from poincare import build_hamilton, _rk4, p_on_shell

A_SPIN = sp.Rational(3, 5)
t, r, th, ph = sp.symbols("t r theta phi", real=True)
Sig = r**2 + A_SPIN**2 * sp.cos(th)**2
De = r**2 - 2 * r + A_SPIN**2
s2 = sp.sin(th)**2


def metric(eps=0):
    g = sp.zeros(4)
    g[0, 0] = -(1 - 2 * r / Sig)
    g[0, 3] = g[3, 0] = -2 * r * A_SPIN * s2 / Sig
    g[1, 1] = Sig / De
    g[2, 2] = Sig
    g[3, 3] = (r**2 + A_SPIN**2 + 2 * r * A_SPIN**2 * s2 / Sig) * s2
    if eps:
        g[0, 0] = -(1 - 2 * r / Sig) * (1 + sp.Integer(eps) * (3 * sp.cos(th)**2 - 1) / r**3)
    return build_hamilton(g, [t, r, th, ph], 1, 2)


def trajectory(f, E, L, p2, r0, steps=9000, h=0.02):
    p1 = p_on_shell(f, r0, math.pi / 2, p2, E, L)
    if p1 is None:
        return None
    s = [r0, math.pi / 2, p1, p2]
    pts = []
    for _ in range(steps):
        s = _rk4(f, s, h, E, L)
        if s[0] < 1.9 or s[0] > 30:
            break
        pts.append(tuple(s))
    return pts


def basis(s):
    r_, th_, pr, pth = s
    u = math.cos(th_)
    om = 1 - u * u
    # quadratic-in-momenta × Carter-structured spatial functions. LINEARLY INDEPENDENT
    # (the earlier u4/om made the identity u2/om - u4/om - u2 = 0 — a false machine-zero SV).
    return [pth * pth, pr * pr, pr * pth,
            u * u, u * u / om,
            pth * pth * u * u, pr * pr * u * u,
            r_ * pth * pth, r_ * r_ * pth * pth, pr * pr * r_, pr * pr * r_ * r_]


BNAMES = ["pth2", "pr2", "pr*pth", "u2", "u2/om", "pth2*u2", "pr2*u2",
          "r*pth2", "r2*pth2", "pr2*r", "pr2*r2"]


def check_independence():
    """SVD the basis on random phase-space points — every singular value must be > 0
    (full column rank), else the basis has a hidden identity (false invariants)."""
    rng = [[(2 + 9 * ((i * 37 + j * 13) % 100) / 100),                      # r in [2,11]
            (0.6 + 1.9 * ((i * 7 + j * 29) % 100) / 100),                    # theta in [0.6,2.5]
            (-1 + 2 * ((i * 17 + j * 5) % 100) / 100),                       # p_r
            (-1 + 2 * ((i * 3 + j * 41) % 100) / 100)]                       # p_theta
           for i in range(40) for j in range(2)]
    Phi = np.array([basis(s) for s in rng], dtype=float)
    Phi = Phi - Phi.mean(axis=0, keepdims=True)
    S = np.linalg.svd(Phi / (np.linalg.norm(Phi, axis=0) + 1e-30), compute_uv=False)
    return S[-1]


def fit(f, E, L, p2list, r0):
    blocks, used = [], 0
    for p2 in p2list:
        pts = trajectory(f, E, L, p2, r0)
        if not pts or len(pts) < 2500:
            continue
        used += 1
        sub = pts[:: max(1, len(pts) // 250)]
        Phi = np.array([basis(s) for s in sub], dtype=float)
        Phi = Phi - Phi.mean(axis=0, keepdims=True)
        blocks.append(Phi)
    D = np.vstack(blocks)
    scale = np.linalg.norm(D, axis=0) + 1e-30
    U, S, Vt = np.linalg.svd(D / scale, full_matrices=False)
    inv_vec = Vt[-1] / scale                 # the smallest-SV right vector → invariant coeffs (un-scaled)
    inv_vec = inv_vec / np.max(np.abs(inv_vec))
    return S, used, inv_vec


if __name__ == "__main__":
    E, L, r0 = 0.95, 3.4, 8.0
    # MANY orbits at fixed E,L (vary inclination → vary Carter value) — fine grid in the
    # bound range so 2*N_orbits >> #basis, killing dimensional nulls.
    p2list = [round(0.08 + 0.04 * k, 3) for k in range(18)]    # 0.08 .. 0.76
    indep = check_independence()
    print(f"basis independence (smallest SV on random points, must be >0): {indep:.2e}  "
          f"{'OK' if indep > 1e-6 else 'DEGENERATE!'}\n", flush=True)
    print("smallest 5 singular values; GENUINE invariant ⇒ smallest ≈1e-12 AND a big gap to S[-2]:\n", flush=True)
    for eps in (0, 2, 5, 10):
        f = metric(eps)
        S, used, vec = fit(f, E, L, p2list, r0)
        tail = ", ".join(f"{v:.2e}" for v in S[-5:])
        gap = S[-2] / S[-1] if S[-1] > 0 else float("inf")
        lab = "KERR (must find Carter)" if eps == 0 else f"deformed eps={eps}"
        print(f"  {lab:26s} [{used:2d} orbits]: {tail}   gap={gap:.1e}", flush=True)
        if S[-1] < 1e-8 and gap > 50:        # a clean invariant — show its dominant terms
            terms = sorted(zip(BNAMES, vec), key=lambda kv: -abs(kv[1]))[:5]
            print("        invariant ≈ " + " + ".join(f"{c:+.3f}·{n}" for n, c in terms), flush=True)
