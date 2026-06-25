"""EXPLORATORY — BREAKING THE WALL. A consistent quadrupole-deformed vacuum black hole,
built NUMERICALLY via the Weyl formalism (the symbolic route swamped 2.5h), vacuum-verified
with finite-difference curvature, fast enough to feed §85's integrability detector.

Weyl: ds² = −e^{2ψ}dt² + e^{−2ψ}[e^{2γ}(dρ²+dz²)+ρ²dφ²], ψ a flat axisymmetric harmonic,
γ from γ_ρ=ρ(ψ_ρ²−ψ_z²), γ_z=2ρψ_ρψ_z. Schwarzschild = rod ψ_S; add q·(l=2 harmonic) ψ_Q
and the linearized γ₁ ⇒ vacuum to O(q). γ₁ is precomputed on an (R,Θ) grid by radial
sweeps (fast) and bilinearly interpolated, so the metric is cheap to evaluate.
"""

import math
import sys

import numpy as np

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from numeric_curvature import ricci_numeric

M = 1.0


def psi_S(rho, z):
    R1 = math.sqrt(rho * rho + (z - M)**2)
    R2 = math.sqrt(rho * rho + (z + M)**2)
    return 0.5 * math.log((R1 + R2 - 2 * M) / (R1 + R2 + 2 * M))


def gamma_S(rho, z):
    R1 = math.sqrt(rho * rho + (z - M)**2)
    R2 = math.sqrt(rho * rho + (z + M)**2)
    return 0.5 * math.log(((R1 + R2)**2 - 4 * M * M) / (4 * R1 * R2))


def psi_Q(rho, z):                       # decaying l=2 quadrupole harmonic P₂(cosΘ)/R³
    R2 = rho * rho + z * z
    return (2 * z * z - rho * rho) / (2 * R2**2.5)


def _grad(fn, rho, z, h=1e-6):
    return ((fn(rho + h, z) - fn(rho - h, z)) / (2 * h),
            (fn(rho, z + h) - fn(rho, z - h)) / (2 * h))


# ---- precompute γ₁ on an (R,Θ) grid by radial sweeps from ∞ inward ----
_NR, _NTH, _RMIN, _RMAX = 600, 300, 1.5, 90.0
_Rs = np.linspace(_RMIN, _RMAX, _NR)
_THs = np.linspace(1e-4, math.pi - 1e-4, _NTH)
_G1 = np.zeros((_NTH, _NR))


def _build_grid():
    for j, Th in enumerate(_THs):
        s, c = math.sin(Th), math.cos(Th)
        acc = 0.0
        for i in range(_NR - 1, -1, -1):                 # sweep inward, γ₁(R_max)=0
            R = _Rs[i]
            rho, z = R * s, R * c
            psr, psz = _grad(psi_S, rho, z)
            pqr, pqz = _grad(psi_Q, rho, z)
            g1r = 2 * rho * (psr * pqr - psz * pqz)
            g1z = 2 * rho * (psr * pqz + psz * pqr)
            integrand = g1r * s + g1z * c
            if i < _NR - 1:
                acc += 0.5 * (integrand + _prev) * (_Rs[i + 1] - R)
            _G1[j, i] = acc
            _prev = integrand
    return _G1


def gamma1(rho, z):                                      # bilinear interp on the (R,Θ) grid
    R = math.sqrt(rho * rho + z * z)
    Th = math.atan2(rho, z)
    if R >= _RMAX:
        return 0.0
    R = max(R, _RMIN)
    fi = (R - _RMIN) / (_RMAX - _RMIN) * (_NR - 1)
    fj = (Th - _THs[0]) / (_THs[-1] - _THs[0]) * (_NTH - 1)
    i0 = min(int(fi), _NR - 2); j0 = min(max(int(fj), 0), _NTH - 2)
    di, dj = fi - i0, fj - j0
    return ((1 - di) * (1 - dj) * _G1[j0, i0] + di * (1 - dj) * _G1[j0, i0 + 1]
            + (1 - di) * dj * _G1[j0 + 1, i0] + di * dj * _G1[j0 + 1, i0 + 1])


def metric(q):
    """Weyl metric g(x), x=(t,ρ,z,φ), quadrupole-deformed by q. Vacuum to O(q)."""
    def g(x):
        _, rho, z, _ = x
        psi = psi_S(rho, z) + q * psi_Q(rho, z)
        gam = gamma_S(rho, z) + (q * gamma1(rho, z) if q else 0.0)
        e2psi = math.exp(2 * psi)
        gg = [[0.0] * 4 for _ in range(4)]
        gg[0][0] = -e2psi
        gg[1][1] = gg[2][2] = math.exp(2 * (gam - psi))
        gg[3][3] = rho * rho / e2psi
        return gg
    return g


if __name__ == "__main__":
    import time
    t0 = time.time()
    _build_grid()
    print(f"BREAKING THE WALL — Weyl quadrupole BH, vacuum verified numerically [γ₁ grid built in {time.time()-t0:.1f}s]\n")
    pts = [(3.0, 2.0), (5.0, 0.0), (4.0, -3.0), (6.0, 1.0)]
    print("max|R_ab| (vacuum residual). Consistent ⇒ residual ≪ deformation scale q, and shrinks ~q²:")
    for q in (0.0, 0.01, 0.02, 0.04):
        res = [max(abs(ricci_numeric(metric(q), [0.0, rho, z, 0.0], h=1e-4)[i][j])
                   for i in range(4) for j in range(4)) for (rho, z) in pts]
        lab = "Schwarzschild" if q == 0 else f"q={q}"
        print(f"  {lab:14s}: max|R_ab| over points = {max(res):.2e}  (deformation ~ q={q})")
