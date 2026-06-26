"""Poincaré surface-of-section + a box-counting integrability diagnostic — native tools.

The sharper companion to `geodesic_chaos.lyapunov`. For a stationary-axisymmetric (or
static-axisymmetric) metric, energy E and axial angular momentum L are conserved, so
geodesic motion reduces to 2 degrees of freedom (q1,q2) governed by a Hamiltonian
H = ½ g^{ab} p_a p_b with the (t,φ) momenta frozen at (−E, L). We build a fast RHS from
the ANALYTIC inverse metric (lambdified), integrate it with RK4 (H is conserved to
~1e-15 in practice), record a surface-of-section, and read off whether an orbit lies on
an invariant torus (the section is a closed curve, box-dim ≈ 1 → REGULAR/integrable) or
fills a chaotic sea (box-dim → 2 → CHAOTIC). This SEES weak chaos that the
largest-Lyapunov exponent averages away (thin chaotic layers between KAM tori).

Assumes the inverse metric is block-diagonal: a (t,φ) block {g^{tt}, g^{tφ}, g^{φφ}}
and the two dynamical coords {g^{q1q1}, g^{q2q2}} with no cross terms — true for Kerr
(Boyer–Lindquist), its deformations, and Weyl/Majumdar–Papapetrou static-axisymmetric
forms. q1i,q2i are the dynamical-coord indices; ti,phii the cyclic ones.

  build_hamilton(g, coords, q1i, q2i, ti, phii) -> dict of fast functions
  p_on_shell(f, q1, q2, p2, E, L)               -> p1 making H = −½ (timelike mass shell)
  section(f, s0, E, L, ...)                      -> (section points, H-drift, steps)
  box_dimension(pts)                            -> box-counting dim (~1 regular, ~2 chaos)
"""

import math

import sympy as sp


def build_hamilton(gexpr, coords, q1i, q2i, ti=0, phii=3):
    """Lambdified Hamilton RHS pieces for the 2-DOF reduction (E, L conserved)."""
    g = sp.Matrix(gexpr)
    gi = g.inv()
    q1, q2 = coords[q1i], coords[q2i]
    E, L = sp.symbols("E L", real=True)
    W = gi[ti, ti] * E**2 - 2 * gi[ti, phii] * E * L + gi[phii, phii] * L**2  # potential from frozen momenta
    g11, g22 = gi[q1i, q1i], gi[q2i, q2i]
    lam = lambda expr: sp.lambdify((q1, q2, E, L), expr, "math")
    return {
        "g11": lam(g11), "g22": lam(g22), "W": lam(W),
        "dW1": lam(sp.diff(W, q1)), "dW2": lam(sp.diff(W, q2)),
        "dg11_1": lam(sp.diff(g11, q1)), "dg11_2": lam(sp.diff(g11, q2)),
        "dg22_1": lam(sp.diff(g22, q1)), "dg22_2": lam(sp.diff(g22, q2)),
    }


def H_value(f, s, E, L):
    q1, q2, p1, p2 = s
    return 0.5 * (f["W"](q1, q2, E, L) + f["g11"](q1, q2, E, L) * p1 * p1 + f["g22"](q1, q2, E, L) * p2 * p2)


def _rhs(f, s, E, L):
    q1, q2, p1, p2 = s
    return [
        f["g11"](q1, q2, E, L) * p1,
        f["g22"](q1, q2, E, L) * p2,
        -0.5 * (f["dW1"](q1, q2, E, L) + f["dg11_1"](q1, q2, E, L) * p1 * p1 + f["dg22_1"](q1, q2, E, L) * p2 * p2),
        -0.5 * (f["dW2"](q1, q2, E, L) + f["dg11_2"](q1, q2, E, L) * p1 * p1 + f["dg22_2"](q1, q2, E, L) * p2 * p2),
    ]


def _rk4(f, s, h, E, L):
    k1 = _rhs(f, s, E, L)
    k2 = _rhs(f, [s[i] + h / 2 * k1[i] for i in range(4)], E, L)
    k3 = _rhs(f, [s[i] + h / 2 * k2[i] for i in range(4)], E, L)
    k4 = _rhs(f, [s[i] + h * k3[i] for i in range(4)], E, L)
    return [s[i] + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(4)]


def p_on_shell(f, q1, q2, p2, E, L):
    """Solve H = −½ for p1 ≥ 0 (timelike geodesic); None if off-shell here."""
    val = (-1 - f["W"](q1, q2, E, L) - f["g22"](q1, q2, E, L) * p2 * p2) / f["g11"](q1, q2, E, L)
    return math.sqrt(val) if val > 0 else None


def section(f, s0, E, L, sec_idx=1, sec_val=math.pi / 2, rec=(0, 2), n=160, h=0.02, maxst=1_800_000,
            bounds=None):
    """Record (state[rec[0]], state[rec[1]]) each time state[sec_idx] up-crosses sec_val.
    Returns (points, H_drift, steps). State is [q1, q2, p1, p2].

    `bounds`, if given, is ((q1lo,q1hi),(q2lo,q2hi)): the orbit is stopped cleanly the moment
    q1 or q2 leaves the box (a plunge into a singularity / an escape), returning what was
    recorded so far. We also catch the OverflowError/ZeroDivisionError that a near-singularity
    RHS evaluation can throw mid-step and treat it as a plunge — so a chaotic orbit that dives
    toward the centre ends the integration instead of crashing it."""
    s = list(s0)
    pts, Hs = [], []
    prev = s[sec_idx] - sec_val
    st = 0
    while len(pts) < n and st < maxst:
        if bounds is not None:
            (a1, b1), (a2, b2) = bounds
            if not (a1 <= s[0] <= b1 and a2 <= s[1] <= b2):
                break
        try:
            sn = _rk4(f, s, h, E, L)
        except (OverflowError, ZeroDivisionError, ValueError):
            break
        st += 1
        cur = sn[sec_idx] - sec_val
        if prev < 0 <= cur:
            fr = prev / (prev - cur)
            pts.append((s[rec[0]] + fr * (sn[rec[0]] - s[rec[0]]), s[rec[1]] + fr * (sn[rec[1]] - s[rec[1]])))
            Hs.append(H_value(f, sn, E, L))
        prev = cur
        s = sn
    drift = (max(Hs) - min(Hs)) if Hs else float("inf")
    return pts, drift, st


def box_dimension(pts, grids=(4, 8, 16)):
    """Box-counting dimension of the 2-D section point set (normalized to its bounding
    box): ≈1 for a regular orbit (the section is a 1-D closed curve), →2 for a chaotic
    orbit (the points fill a 2-D area). Returns (dimension, occupied-cell counts)."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)

    def occ(G):
        cells = set()
        for x, y in pts:
            cells.add((min(G - 1, int(G * (x - x0) / (x1 - x0 + 1e-30))),
                       min(G - 1, int(G * (y - y0) / (y1 - y0 + 1e-30)))))
        return len(cells)

    Ns = [occ(G) for G in grids]
    lg = [math.log(G) for G in grids]
    ln = [math.log(N) for N in Ns]
    mg, mn = sum(lg) / len(lg), sum(ln) / len(ln)
    slope = sum((lg[i] - mg) * (ln[i] - mn) for i in range(len(lg))) / sum((lg[i] - mg)**2 for i in range(len(lg)))
    return slope, Ns


def frequency_drift(series):
    """Laskar-style frequency-drift chaos indicator on a section-coordinate sequence.

    The dominant frequency of the sequence (the orbit's rotation number on the section)
    is CONSTANT on an invariant torus — a regular orbit OR a resonant island — and DRIFTS
    only when the orbit is chaotic. Returns |f1 − f2| / f_avg between the first and second
    half of the sequence: ≈0 for regular, O(1) for chaos. It is AREA-BLIND, so it resolves
    thin chaotic layers that box_dimension grazes (the §101 box-dim≈1.2 ambiguity) and,
    unlike the largest-Lyapunov exponent, it does not false-positive on finite-difference
    roundoff or on resonant islands. Validated on Hénon–Heiles (regular→0, chaotic→>1) and
    on Kerr (integrable→0); threshold ≈0.0115. Requires numpy (the FFT).

    f is estimated by the windowed-FFT peak with parabolic (sub-bin) refinement — a
    lightweight NAFF; for a clean quasi-periodic signal the two halves agree to machine
    zero, so a regular orbit reads exactly 0.0."""
    import numpy as np

    def _dom(seg):
        seg = np.asarray(seg, float)
        n = len(seg)
        if n < 8:
            return 0.0
        seg = seg - seg.mean()
        F = np.abs(np.fft.rfft(seg * np.hanning(n)))
        F[0] = 0.0                                            # kill the DC bin
        k = int(np.argmax(F))
        if 1 <= k < len(F) - 1:
            a, b, c = F[k - 1], F[k], F[k + 1]
            d = 0.5 * (a - c) / (a - 2 * b + c + 1e-30)       # parabolic sub-bin refinement
        else:
            d = 0.0
        return (k + d) / n

    s = list(series)
    n = len(s)
    h = n // 2
    f1, f2 = _dom(s[:h]), _dom(s[h:])
    return abs(f1 - f2) / (0.5 * (f1 + f2) + 1e-30)
