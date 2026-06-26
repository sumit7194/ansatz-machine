"""A first-class geodesic integrator + chaos lens — native tools (ROADMAP §v8.4).

The bridge built geodesic integration and a chaos diagnostic as throwaway code; this
makes them native and reusable, so ansatz can study the INTEGRABILITY / CHAOS of its
own discovered metrics — a lens right beside the Killing tensors (§58/§69/§78). Pure
Python (finite-difference Christoffels via numeric_curvature; no numpy), so it stays in
the one-dependency core.

  trajectory(g_func, x0, u0)      -> the geodesic path (RK4) in any metric g_func(x)
  lyapunov(g_func, x0, u0)        -> the largest Lyapunov exponent (≈0 regular, >0 chaos)

g_func(x) returns the 4×4 metric (nested list) at a point x=(x0,x1,x2,x3); states are
8-vectors [position(4), 4-velocity(4)]; τ is the affine parameter.
"""

import math

from numeric_curvature import christoffel_numeric


def _rhs(g_func, s, ch=1e-4):
    x, u = s[:4], s[4:]
    G = christoffel_numeric(g_func, x, h=ch)
    acc = [-sum(G[i][b][c] * u[b] * u[c] for b in range(4) for c in range(4)) for i in range(4)]
    return list(u) + acc


def _rk4(g_func, s, h, ch=1e-4):
    k1 = _rhs(g_func, s, ch)
    k2 = _rhs(g_func, [s[i] + h / 2 * k1[i] for i in range(8)], ch)
    k3 = _rhs(g_func, [s[i] + h / 2 * k2[i] for i in range(8)], ch)
    k4 = _rhs(g_func, [s[i] + h * k3[i] for i in range(8)], ch)
    return [s[i] + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(8)]


def trajectory(g_func, x0, u0, dtau=0.1, steps=200, ch=1e-4):
    """RK4-integrate the geodesic ẍ^a = −Γ^a_bc ẋ^b ẋ^c. Returns the list of
    phase-space states [x(4), u(4)] along the path."""
    s = list(x0) + list(u0)
    out = [s[:]]
    for _ in range(steps):
        try:
            s = _rk4(g_func, s, dtau, ch)
        except (ValueError, OverflowError, ZeroDivisionError):
            break  # geodesic reached a non-physical region (e.g. MN's A<0 / rod) — stop cleanly
        out.append(s[:])
    return out


def lyapunov(g_func, x0, u0, dtau=0.15, blocks=500, renorm_every=4, d0=1e-6, idx=5, ch=1e-4):
    """Largest Lyapunov exponent via two renormalized nearby geodesics: integrate the
    reference and a partner started d0 away (perturbing component `idx`), and accumulate
    the log-stretch, renormalizing the separation back to d0 each block. λ ≈ 0 for a
    regular (integrable) system, λ > 0 (a plateau) for chaos.

    NOTE (de-noised defaults, after a sister-project finding): the separation d0 must sit
    ABOVE the finite-difference Christoffel roundoff floor (~eps/ch). With the old d0=1e-8,
    ch=1e-5 the roundoff (~1e-11) drove a FALSE-POSITIVE chaos on bumpy metrics (λ~0.1-0.3
    where the box-counting dimension correctly read regular). d0=1e-6, ch=1e-4 keeps the
    signal above the noise. For a definitive chaos verdict prefer poincare.box_dimension —
    a geometric diagnostic immune to this roundoff."""
    s = list(x0) + list(u0)
    sp = s[:]
    sp[idx] += d0
    acc, T = 0.0, 0.0
    for _ in range(blocks):
        try:
            for _ in range(renorm_every):
                s = _rk4(g_func, s, dtau, ch)
                sp = _rk4(g_func, sp, dtau, ch)
        except (ValueError, OverflowError, ZeroDivisionError):
            break  # geodesic reached a non-physical region (e.g. MN's A<0 / rod) — stop cleanly
        T += renorm_every * dtau
        d = math.sqrt(sum((sp[i] - s[i])**2 for i in range(8)))
        if d <= 0:
            break
        acc += math.log(d / d0)
        sp = [s[i] + (d0 / d) * (sp[i] - s[i]) for i in range(8)]
    return acc / T if T > 0 else 0.0
