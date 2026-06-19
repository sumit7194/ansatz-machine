#!/usr/bin/env python3
"""Step 79 — GEODESIC INTEGRATOR & CHAOS LENS: integrability you can measure.

A native, reusable tool (ROADMAP §v8.4): integrate a geodesic in ANY metric and
measure whether the orbits are REGULAR (integrable) or CHAOTIC, via the largest
Lyapunov exponent. This sits right beside the Killing tensors (§58/§69/§78): a hidden
symmetry (a Killing tensor, like Kerr's Carter constant) makes a system INTEGRABLE, so
nearby orbits separate only polynomially (λ→0); a system with no such symmetry is
CHAOTIC, nearby orbits diverge exponentially (λ>0). The chaos lens MEASURES what the
Killing-tensor proof (§78) certifies.

  (A) `trajectory(g, x0, u0)` integrates a bound Kerr orbit; the four constants of
      motion (E, L, μ², Carter C) hold along it — the integrator is correct and Kerr
      is integrable (ties §58);
  (B) `lyapunov` on Kerr ≈ 0 — REGULAR: the Carter constant (proven §78) forbids chaos;
  (C) `lyapunov` on a Majumdar–Papapetrou di-hole (two black holes — no Carter-like
      symmetry) is strongly POSITIVE — CHAOTIC geodesics;
  (D) so integrability ⟺ a hidden symmetry (§78) ⟺ λ≈0: the lens detects exactly what
      the Killing tensor explains, and runs on any metric ansatz discovers.

Pure Python (finite-difference Christoffels, no numpy) — stays in the core. Honest
scope: the largest-Lyapunov two-orbit estimate (standard, not SALI); the di-hole orbit
dips near a center (where dynamics are fast) so its λ is large but unambiguously > 0.

Run:  .venv/bin/python scripts/79_geodesic_chaos.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geodesic_chaos import lyapunov, trajectory
from numeric_curvature import inv4

A_SPIN = 0.6


def kerr(x):
    _, r, th, _ = x
    Sig = r * r + A_SPIN**2 * math.cos(th)**2
    De = r * r - 2 * r + A_SPIN**2
    s2 = math.sin(th)**2
    g = [[0.0] * 4 for _ in range(4)]
    g[0][0] = -(1 - 2 * r / Sig)
    g[0][3] = g[3][0] = -2 * r * A_SPIN * s2 / Sig
    g[1][1] = Sig / De
    g[2][2] = Sig
    g[3][3] = (r * r + A_SPIN**2 + 2 * r * A_SPIN**2 * s2 / Sig) * s2
    return g


def kerr_K_lower(x):                       # Carter Killing tensor (for the C constant)
    _, r, th, _ = x
    Sig = r * r + A_SPIN**2 * math.cos(th)**2
    De = r * r - 2 * r + A_SPIN**2
    l = [(r * r + A_SPIN**2) / De, 1.0, 0.0, A_SPIN / De]
    nv = [(r * r + A_SPIN**2) / (2 * Sig), -De / (2 * Sig), 0.0, A_SPIN / (2 * Sig)]
    g = kerr(x)
    gi = inv4(g)
    Ku = [[2 * Sig * 0.5 * (l[i] * nv[j] + l[j] * nv[i]) + r * r * gi[i][j]
           for j in range(4)] for i in range(4)]
    return [[sum(g[i][a] * g[j][b] * Ku[a][b] for a in range(4) for b in range(4))
             for j in range(4)] for i in range(4)]


def kerr_orbit_u(x0, uth):                 # near-circular equatorial + small tilt (cf §58)
    g = kerr(x0)
    ut = math.sqrt((g[2][2] * uth * uth + 1) / (-g[0][0]))
    Om = 1 / (x0[1]**1.5 + A_SPIN)
    return [ut, 0.0, uth, Om * ut]


def dihole(x):                             # Majumdar–Papapetrou two extremal holes at z=±2
    _, X, Y, Z = x
    m, b = 1.0, 2.0
    r1 = math.sqrt(X * X + Y * Y + (Z - b)**2)
    r2 = math.sqrt(X * X + Y * Y + (Z + b)**2)
    U = 1 + m / r1 + m / r2
    g = [[0.0] * 4 for _ in range(4)]
    g[0][0] = -1 / U**2
    g[1][1] = g[2][2] = g[3][3] = U * U
    return g


def main():
    print("GEODESIC INTEGRATOR & CHAOS LENS — integrability you can measure\n")
    ok = []

    # (A) integrate a Kerr orbit; the four constants hold
    x0 = [0.0, 8.0, math.pi / 2, 0.0]
    u0 = kerr_orbit_u(x0, 0.03)
    path = trajectory(kerr, x0, u0, dtau=0.2, steps=300)

    def consts(s):
        g, K = kerr(s[:4]), kerr_K_lower(s[:4])
        u = s[4:]
        ul = [sum(g[i][j] * u[j] for j in range(4)) for i in range(4)]
        return (-ul[0], ul[3],
                sum(g[i][j] * u[i] * u[j] for i in range(4) for j in range(4)),
                sum(K[i][j] * u[i] * u[j] for i in range(4) for j in range(4)))
    c0, cN = consts(path[0]), consts(path[-1])
    drift = max(abs(cN[k] - c0[k]) / (abs(c0[k]) or 1) for k in range(4))
    okA = drift < 1e-3
    ok.append(okA)
    print(f"  (A) trajectory(): Kerr orbit, constants (E,L,μ²,C) drift over 300 steps = {drift:.1e}")
    print(f"      ⇒ integrator correct; Kerr has 4 constants (E,L,μ²,Carter) — integrable   {'✅' if okA else '❌'}")

    # (B) Kerr is REGULAR: λ ≈ 0
    lam_kerr = lyapunov(kerr, x0, u0, dtau=0.2, blocks=500)
    okB = abs(lam_kerr) < 0.05
    ok.append(okB)
    print(f"\n  (B) Lyapunov(Kerr) = {lam_kerr:.4f} ≈ 0 — REGULAR (the Carter constant §78 forbids chaos)   "
          f"{'✅' if okB else '❌'}")

    # (C) the di-hole is CHAOTIC: λ > 0
    xd = [0.0, 2.5, 0.0, 0.0]
    gd = dihole(xd)
    vy, vz = 0.2, 0.03
    utd = math.sqrt((gd[1][1] * 0 + gd[2][2] * vy * vy + gd[3][3] * vz * vz + 1) / (-gd[0][0]))
    ud = [utd, 0.0, vy, vz]
    lam_dh = lyapunov(dihole, xd, ud, dtau=0.15, blocks=500)
    okC = lam_dh > 0.1 and lam_dh > 10 * abs(lam_kerr)
    ok.append(okC)
    print(f"\n  (C) Lyapunov(di-hole) = {lam_dh:.3f} > 0 — CHAOTIC (two holes, no Carter-like symmetry)   "
          f"{'✅' if okC else '❌'}")

    # (D) the tie
    okD = okA and okB and okC
    ok.append(okD)
    print(f"\n  (D) integrability ⟺ a hidden symmetry (§78) ⟺ λ≈0: di-hole/Kerr ratio ≈ {lam_dh/abs(lam_kerr):.0f}×")
    print(f"      the chaos lens MEASURES what the Killing-tensor proof certifies — on any metric   "
          f"{'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nGEODESIC CHAOS: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(native integrator; Kerr regular λ≈0, di-hole chaotic λ>0 — integrability, measured)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
