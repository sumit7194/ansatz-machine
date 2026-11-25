#!/usr/bin/env python3
"""c2 of F(k) = tr[M1, M0] - 2 = c2 k^2 + O(k^3), from Kerr's explicit solutions (data/nve/C2_ANALYTIC.md).
[model: Fable 5.2; UNVERIFIED until the office ansatz-machine checks it]

Small double-precision check (numpy, one core, about a second per spin). It shares no code with the monodromy
engines. E = 4/5.

    c2 = sinh^2(kappa*omega) * I_plus * I_minus / kappa^2,     kappa^2 = a^2 (1 - E^2),
    I_pm = contour integral over |z| = R0 of  dq(z) * sqrt(N D)(z) * exp(+-2 kappa U(z)) dz,
    U(z) = int_0^z ds / sqrt(N D),   omega = closed integral of dz / sqrt(N D) around r+ and p+,
    dq = (3/8) (P'/P) (g c1)',  g = -4 a Delta / (D N),  c1 = d c0/dk at k = 0 (closed form, logs).

Second route to I_pm, sharing only the Kerr data: residues of Psi * c1'' (c1'' is rational), where Psi'' = -T' g and
T = (3/8)(P'/P) sqrt(N D) exp(+-2 kappa U). Also x11, for the stored tr M0 - 2.

    NVE_SPIN=3/5 python scripts/_nve_c2_analytic.py          # optional: C2_R0=1.5 moves the circle
"""
import os
import sys
import time
from fractions import Fraction

import numpy as np
from scipy import integrate

t0 = time.time()
A = Fraction(os.environ.get("NVE_SPIN", "3/5"))
a = A.numerator / A.denominator
E2 = 16 / 25                               # E = 4/5
kappa = a * np.sqrt(1 - E2)
R0 = float(os.environ.get("C2_R0", "1.3"))
S3 = np.sqrt(3.0)
GX, GW = np.polynomial.legendre.leggauss(96)
GX, GW = (GX + 1) / 2, GW / 2              # nodes and weights on [0, 1]

# ---------------------------------------------------------------- Kerr lower-axis data (k = 0)
n2, n1, n0 = E2 - 1, 2 - 4 * E2, E2 * (4 + a * a) - a * a      # N = n2 z^2 + n1 z + n0
_d = np.sqrt(n1 * n1 - 4 * n2 * n0)
r_plus, r_minus = (-n1 - _d) / (2 * n2), (-n1 + _d) / (2 * n2)
p_plus, p_minus = complex(2, a), complex(2, -a)
ROOTS = [r_plus, r_minus, p_plus, p_minus]


def Dm(z):
    return (z - 2) ** 2 + a * a


def Delta(z):
    return z * z - 2 * z + a * a


def N(z):
    return n2 * z * z + n1 * z + n0


C0 = np.sqrt(N(0.0) * Dm(0.0))             # N(0) D(0) > 0


def sqND(z):
    """sqrt(N D), holomorphic in |z| < min|root|, positive on the real segment there."""
    z = np.asarray(z, dtype=complex)
    v = C0 * np.ones_like(z)
    for r in ROOTS:
        v = v * np.sqrt(1 - z / r)
    return v


def dsqND(z):
    z = np.asarray(z, dtype=complex)
    return sqND(z) * 0.5 * sum(1 / (z - r) for r in ROOTS)


def U(z):
    """int_0^z ds / sqrt(N D) along the ray (Gauss-Legendre; the integrand is analytic on |s| < min|root|)."""
    z = np.asarray(z, dtype=complex)
    return z * np.tensordot(GW, 1 / sqND(np.multiply.outer(GX, z)), axes=1)


def L(z):                                   # P'/P, P = N/D
    return (2 * n2 * z + n1) / N(z) - 2 * (z - 2) / Dm(z)


def dL(z):
    return 2 * n2 / N(z) - ((2 * n2 * z + n1) / N(z)) ** 2 - 2 / Dm(z) + (2 * (z - 2) / Dm(z)) ** 2


def g(z):
    return -4 * a * Delta(z) / (Dm(z) * N(z))


def dg(z):
    den = Dm(z) * N(z)
    dden = 2 * (z - 2) * N(z) + Dm(z) * (2 * n2 * z + n1)
    return -4 * a * ((2 * z - 2) * den - Delta(z) * dden) / den ** 2


# ---------------------------------------------------------------- c1 = d c0 / dk at k = 0 (closed form)
def Lg(u):
    return np.log((S3 * u - 1) / (S3 * u + 1))         # cut on [-1/sqrt3, 1/sqrt3]


def acot(u):
    return np.log((u + 1j) / (u - 1j)) / 2j             # cut on [-i, i]; -> 0 at infinity


def Rr(u):                                              # 5 a^3 c1''
    return (21 * u ** 4 - 18 * u ** 2 + 1) / ((u * u + 1) ** 3 * (3 * u * u - 1))


def R1(u):                                              # int_u^inf Rr
    return 3 / 8 * acot(u) + 3 * S3 / 16 * Lg(u) + 5 / 2 * u / (u * u + 1) ** 2


def Iu(u):                                              # int_u^inf (s - u) Rr(s) ds
    return (5 / 4 / (u * u + 1) - 3 / 8 * u * acot(u) - 3 * S3 / 16 * u * Lg(u)
            - 3 / 16 * np.log((u * u + 1) / (u * u - 1 / 3)))


def c1(z):
    return Iu(np.asarray(z, dtype=complex) / a) / (5 * a)


def dc1(z):
    return -R1(np.asarray(z, dtype=complex) / a) / (5 * a * a)


def ddc1(z):
    return Rr(np.asarray(z, dtype=complex) / a) / (5 * a ** 3)


def dq(z):
    return 3 / 8 * L(z) * (dg(z) * c1(z) + g(z) * dc1(z))


# ---------------------------------------------------------------- gates on the closed forms
def gates():
    ok = True
    # (1) c1 against direct quadrature of the rational c1'' on the real line; derivatives by central differences
    for zz in (1.3, -2.1, 7.0):
        f = lambda s: float(np.real(ddc1(s)))                                   # noqa: E731
        if zz > 0:
            direct = integrate.quad(lambda s: (s - zz) * f(s), zz, np.inf, epsabs=1e-13, epsrel=1e-13)[0]
        else:   # c1 is holomorphic at infinity, so the lower axis is reached by integrating from -infinity
            direct = integrate.quad(lambda s: (zz - s) * f(s), -np.inf, zz, epsabs=1e-13, epsrel=1e-13)[0]
        h = 1e-4
        e1 = abs(c1(zz) - direct)
        e2 = abs((c1(zz + h) - c1(zz - h)) / (2 * h) - dc1(zz))
        e3 = abs((dc1(zz + h) - dc1(zz - h)) / (2 * h) - ddc1(zz))
        print(f"  gate c1 at z = {zz}: |closed - quadrature| = {e1:.1e}, |c1' err| = {e2:.1e}, |c1'' err| = {e3:.1e}")
        ok &= e1 < 1e-10 and e2 < 1e-7 and e3 < 1e-7
    # (2) c1'' is d/dk of the family's published c0'' at k = 0; and c0''(k = 0) is Kerr's
    def c0pp(z, k):
        w = (z / a) ** 2
        B = (90 - 21 * k) * w * w - (60 - 18 * k) * w + (10 - k)
        return -(2 * np.sqrt(10) / (5 * a ** 3)) * np.sqrt(B) / (w + 1) ** 3
    zz, h = 1.7, 1e-5
    e = abs((c0pp(zz, h) - c0pp(zz, -h)) / (2 * h) - ddc1(zz))
    cK = lambda s: -2 * a / (s * s + a * a)                                     # noqa: E731
    kerr = abs(c0pp(zz, 0.0) - (cK(zz + 1e-3) - 2 * cK(zz) + cK(zz - 1e-3)) / 1e-6)
    print(f"  gate d/dk c0'' at k = 0 (z = 1.7): |finite difference - closed| = {e:.1e}; "
          f"|c0''(k = 0) - Kerr's| = {kerr:.1e}")
    ok &= e < 1e-8 and kerr < 1e-5
    # (3) the published identity f0m = Delta/Dm at k = 0, and d f0m/dk = 4 a Delta c1 / Dm^2
    def f0m(z, c):
        f0 = Delta(z) / (z * z + a * a)
        return f0 / (f0 * f0 + c * c)
    zz = 0.7 + 0.4j
    e_a = abs(f0m(zz, cK(zz)) - Delta(zz) / Dm(zz))
    e_b = abs((f0m(zz, cK(zz) + 1e-6) - f0m(zz, cK(zz) - 1e-6)) / 2e-6 - 4 * a * Delta(zz) / Dm(zz) ** 2)
    print(f"  gate lower-axis data: |f0m - Delta/Dm| = {e_a:.1e}; |d f0m/d c0 - 4 a Delta/Dm^2| = {e_b:.1e}")
    ok &= e_a < 1e-12 and e_b < 1e-7
    # (4) Kerr solutions: v = (N D)^(1/4) exp(kappa U) solves v'' + (3/16)(P'/P)^2 v = 0
    v = lambda s: np.sqrt(sqND(s)) * np.exp(kappa * U(s))                       # noqa: E731
    zz, h = 0.4 + 0.3j, 1e-3
    d2 = (v(zz + h) - 2 * v(zz) + v(zz - h)) / h ** 2
    res = abs(d2 + 3 / 16 * L(zz) ** 2 * v(zz)) / abs(v(zz))
    print(f"  gate Kerr solution: relative ODE residual = {res:.1e} (finite differences, h = 1e-3)")
    ok &= res < 1e-5
    return ok


def circle(f, npts):
    """(closed integral of f dz) on |z| = R0, counter-clockwise; trapezoid."""
    zz = R0 * np.exp(2j * np.pi * np.arange(npts) / npts)
    return np.sum(f(zz) * 1j * zz) * 2 * np.pi / npts


def main():
    print(f"spin a = {A}, E = 4/5, kappa = {kappa:.15f}, circle R0 = {R0}")
    mr = min(abs(r) for r in ROOTS)
    print(f"  r+ = {r_plus:.12f}, r- = {r_minus:.12f}, p+- = 2 +- {a} i; min|root| = {mr:.6f} (need a < R0 < min|root|)")
    assert a < R0 < mr
    if not gates():
        print("GATES FAILED")
        return 1
    # omega = 2 * int_{r+}^{p+} dz / sqrt(N D), with z = r+ + t d, t = (1 - cos phi)/2
    d = p_plus - r_plus
    phi = np.pi * GX
    zz = r_plus + (1 - np.cos(phi)) / 2 * d
    pref = 2 * d / (np.sqrt(complex(n2)) * np.sqrt(-d * d))
    omega = pref * np.pi * np.sum(GW / (np.sqrt(zz - r_minus) * np.sqrt(zz - p_minus)))
    trM1 = -2 * np.cosh(kappa * omega)
    print(f"  kappa*omega = {kappa * omega:.13f} (overall sign is a branch choice); tr M1(0) = -2 cosh = {trM1:.13f}")
    res = {}
    for npts in (1024, 4096):
        Ip = circle(lambda s: dq(s) * sqND(s) * np.exp(2 * kappa * U(s)), npts)
        Im = circle(lambda s: dq(s) * sqND(s) * np.exp(-2 * kappa * U(s)), npts)
        I0 = circle(lambda s: dq(s) * sqND(s), npts)
        res[npts] = (Ip, Im, I0)
    (Ip, Im, I0), (Ip2, Im2, _) = res[4096], res[1024]
    print(f"  I+ = {Ip:.13e}   (1024 vs 4096 points: {abs(Ip - Ip2):.1e})")
    print(f"  I- = {Im:.13e}   (1024 vs 4096 points: {abs(Im - Im2):.1e})")
    c2 = np.sinh(kappa * omega) ** 2 * Ip * Im / kappa ** 2
    x11 = -I0 / (2 * kappa)
    x12x21 = -Ip * Im / (4 * kappa ** 2)
    print(f"  c2 = sinh^2(kappa omega) I+ I- / kappa^2 = {c2:.12f}")
    print(f"  x11 = {x11:.12f};  x11^2 + x12 x21 = {x11 ** 2 + x12x21:.12e}  (= lim (tr M0 - 2)/k^2)")
    # residue route: I = 2 pi i * (sum of residues of Psi * c1'' inside the circle), Psi(z) = int_0^z (z - s) G(s) ds
    out = {}
    for sgn in (1, -1):
        def G(s, sgn=sgn):
            dT = 3 / 8 * (dL(s) * sqND(s) + L(s) * (dsqND(s) + 2 * sgn * kappa)) * np.exp(2 * sgn * kappa * U(s))
            return -dT * g(s)

        def Psi(zv):
            zv = np.asarray(zv, dtype=complex)
            s = np.multiply.outer(GX, zv)
            return zv ** 2 * np.tensordot(GW * (1 - GX), G(s), axes=1)
        tot = 0j
        vals = []
        for zp in (a / S3, -a / S3, 1j * a, -1j * a):
            m, rad = 64, 0.08
            w = rad * np.exp(2j * np.pi * np.arange(m) / m)
            rs = np.sum(Psi(zp + w) * ddc1(zp + w) * w) / m
            vals.append(rs)
            tot += rs
        out[sgn] = (2j * np.pi * tot, vals)
    print(f"  residue route: I+ = {out[1][0]:.13e}  (difference from the circle: {abs(out[1][0] - Ip):.1e})")
    print(f"                 I- = {out[-1][0]:.13e}  (difference from the circle: {abs(out[-1][0] - Im):.1e})")
    for sgn in (1, -1):
        rl, ri = out[sgn][1][0] + out[sgn][1][1], out[sgn][1][2] + out[sgn][1][3]
        print(f"    residues for I{'+' if sgn > 0 else '-'}: real-cut pair {rl:.6e}, +-ia pair {ri:.6e}")
    print(f"  wall {time.time() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
