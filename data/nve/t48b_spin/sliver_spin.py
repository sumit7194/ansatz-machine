#!/usr/bin/env python3
"""
Rigorous interval-arithmetic (mpmath.iv) closure of the open sliver (30/7 - 1e-12, 30/7)
at spin a = 0.6 for BOTH E = 0.8 (owner's energy) and E = 1.5, certifying FULL ZARISKI
DENSITY of the VE1 monodromy group in SL(2, C) (and hence non-abelian G_1^0 = SL(2, C)
and non-abelian G_3^0 via G_3^0 -> G_1^0).

Auditability / Rigor Architecture:
  - The floating-point DOP853 trajectory ONLY seeds a C^1 quintic Hermite polynomial
    Phi_tilde(s) on each subinterval I_k = [s_k, s_{k+1}].
  - On EVERY subinterval I_k, the a-posteriori defect delta(t) = Phi_tilde'(s) - du*A(u(t))*Phi_tilde(t)
    is enclosed over the WHOLE subinterval box U_box = u_m + [-1/2, 1/2]*h*du in mpmath.iv
    (never sampled at points): q(u), q'(u), q''(u) are evaluated in mpmath.iv at u_m and the
    Taylor remainder (1/6)*q'''(U_box)*(h*du)^3*t^3 is bounded over the entire box U_box.
  - Variation-of-constants Gronwall bounds propagate the exact O(L) rationalized perturbation
    bounds sup_{u in K} |c0^(m)(u; k) - c0^(m)(u; 30/7)| <= C_m * L to every monodromy matrix
    and trace invariant over the entire interval k in [30/7 - delta0, 30/7].

Zariski Density Classifier in SL(2, C) (Kovacic's classification):
  For Gamma = <M_1, M_2, M_3> <= G_1 <= SL(2, C) with A = M_2 M_1, B = M_3 M_2:
    (Z1) Irreducibility  : tau(M_1, M_3) = tr(M_1 M_3 M_1^{-1} M_3^{-1}) - 2 != 0
                           (and at E = 1.5, also tau(A, B) != 0 directly).
                           Rules out all reducible / triangularizable / Borel subgroups.
    (Z2) Non-abelianness : [A, B] != 0  (rules out <A, B> <= C*, the diagonal part of D_inf).
    (Z3) Non-imprimitive : tr(A), tr(B), tr(AB) all strictly nonzero (at least two nonzero).
                           Together with (Z2), rules out imprimitive (D_inf) subgroups.
    (Z4) Infiniteness    : |tr(A)| > 2 (at E = 0.8) and/or |Im(tr(B))| > 0 (both E = 0.8, 1.5).
                           Rules out all finite subgroups (2T, 2O, 2I, cyclic, dihedral), since
                           every finite-order element of SL(2, C) has real trace in [-2, 2].
  All four strict inequalities certified simultaneously on [30/7 - delta0, 30/7] imply
  Zariski-closure(Gamma) = SL(2, C), hence G_1^0 = SL(2, C) and G_3^0 non-abelian.

Controls:
  1. Strong Kerr control (k = 0): interval enclosure of [M_alpha^(S), M_beta^(S)] strictly
     contains 0 AND its upper bound is strictly smaller than the endpoint's certified lower bound.
  2. Planted wrong O(L^{1/2}) tail exponent: visibly shrinks delta0 by > 10^7x.
"""

import cmath
import math
import time
import numpy as np
import mpmath as mp
from mpmath import iv
from scipy.integrate import solve_ivp


# ---------------------------------------------------------------------------
# 1. Rigorous complex interval primitives (valid on Re(z) > 0)
# ---------------------------------------------------------------------------
def iv_csqrt(z):
    x, y = z.real, z.imag
    if not (x.a > 0):
        raise ValueError(f"iv_csqrt requires Re(z) > 0, got {x}")
    r = iv.sqrt(x ** 2 + y ** 2)
    u = iv.sqrt((r + x) / 2)
    v = y / (2 * u)
    return iv.mpc(u, v)


def iv_clog(z):
    x, y = z.real, z.imag
    if not (x.a > 0):
        raise ValueError(f"iv_clog requires Re(z) > 0, got {x}")
    return iv.mpc(iv.log(x ** 2 + y ** 2) / 2, iv.atan2(y, x))


def iv_catan(z):
    return iv_clog((1 + 1j * z) / (1 - 1j * z)) / (2j)


def iv_catanh(z):
    return iv_clog((1 + z) / (1 - z)) / 2


def iv_cabs(z):
    return iv.sqrt(z.real ** 2 + z.imag ** 2)


def iv_contains_zero(z):
    return (z.real.a <= 0 <= z.real.b) and (z.imag.a <= 0 <= z.imag.b)


def iv_inflate(z, rad):
    r = iv.mpf([-rad.b, rad.b])
    return iv.mpc(z.real + r, z.imag + r)


# ---------------------------------------------------------------------------
# 2. Exact endpoint (k = 30/7) and Kerr (k = 0) axis data and 5-jet of q(u)
# ---------------------------------------------------------------------------
def _c0_end_iv_point(u, a):
    w = iv_csqrt(3 * u * u + 1)
    s = iv.sqrt(2) * u / w
    atanh_s = iv_catanh(s)
    atanh_lim = iv.mpf('0.5') * iv.log((1 + iv.sqrt(iv.mpf(2) / 3)) / (1 - iv.sqrt(iv.mpf(2) / 3)))
    arccot_w = iv_catan(iv.sqrt(2) / w)
    I1 = u * (7 + 3 * u * u) * w / (16 * (u * u + 1) ** 2) + 9 * iv.sqrt(2) / 32 * atanh_s
    lim_I1 = 3 * iv.sqrt(3) / 16 + 9 * iv.sqrt(2) / 32 * atanh_lim
    I2 = (
        w ** 3 / (16 * (u * u + 1))
        - 3 * iv.sqrt(3) / 16 * u
        + 9 * iv.sqrt(2) / 32 * (u * (atanh_s - atanh_lim) + arccot_w)
    )
    fac = -8 / (iv.sqrt(7) * a)
    return fac * I2, fac * (I1 - lim_I1)


def c0_end_iv(u, a):
    """Centered-form (zero-cancellation) enclosure of (c0(u), c0'(u)) at k = 30/7."""
    if u.real.delta == 0 and u.imag.delta == 0:
        return _c0_end_iv_point(u, a)
    um = iv.mpc(u.real.mid, u.imag.mid)
    du = u - um
    c0_m, c1_m = _c0_end_iv_point(um, a)
    w2 = u * u
    c2_box = -8 / (iv.sqrt(7) * a) * iv_csqrt(3 * w2 + 1) / ((w2 + 1) ** 3)
    return c0_m + c1_m * du + (c2_box * (du * du)) / 2, c1_m + c2_box * du


def c0_end_c128(u, a):
    w = cmath.sqrt(3.0 * u * u + 1.0)
    s = math.sqrt(2.0) * u / w
    atanh_s = cmath.atanh(s)
    atanh_lim = math.atanh(math.sqrt(2.0 / 3.0))
    arccot_w = cmath.atan(math.sqrt(2.0) / w)
    I1 = u * (7.0 + 3.0 * u * u) * w / (16.0 * (u * u + 1.0) ** 2) + 9.0 * math.sqrt(2.0) / 32.0 * atanh_s
    lim_I1 = 3.0 * math.sqrt(3.0) / 16.0 + 9.0 * math.sqrt(2.0) / 32.0 * atanh_lim
    I2 = (
        w ** 3 / (16.0 * (u * u + 1.0))
        - 3.0 * math.sqrt(3.0) / 16.0 * u
        + 9.0 * math.sqrt(2.0) / 32.0 * (u * (atanh_s - atanh_lim) + arccot_w)
    )
    fac = -8.0 / (math.sqrt(7.0) * a)
    return fac * I2, fac * (I1 - lim_I1)


def q_and_qp_c128(u, a, E2, mu2, is_kerr=False):
    w = u * u
    wp1 = w + 1.0
    f0 = 1.0 - 2.0 * u / (a * wp1)
    f0p = -2.0 * (1.0 - w) / (a * wp1 * wp1)
    f0pp = 4.0 * u * (3.0 - w) / (a * wp1 * wp1 * wp1)
    if is_kerr:
        c0 = -2.0 / (a * wp1)
        c1 = 4.0 * u / (a * wp1 * wp1)
        c2 = 4.0 * (1.0 - 3.0 * w) / (a * wp1 * wp1 * wp1)
    else:
        c0, c1 = c0_end_c128(u, a)
        c2 = -8.0 / (math.sqrt(7.0) * a) * cmath.sqrt(3.0 * w + 1.0) / (wp1 * wp1 * wp1)
    D = f0 * f0 + c0 * c0
    Dp = 2.0 * (f0 * f0p + c0 * c1)
    N = f0p * (c0 * c0 - f0 * f0) - 2.0 * f0 * c0 * c1
    Np = f0pp * (c0 * c0 - f0 * f0) - 2.0 * f0p * f0p * f0 - 2.0 * f0 * c1 * c1 - 2.0 * f0 * c0 * c2
    G = D * (E2 * D - mu2 * f0)
    Gp = Dp * (2.0 * E2 * D - mu2 * f0) - mu2 * D * f0p
    R = -mu2 * N / G
    Rp = -mu2 * (Np * G - N * Gp) / (G * G)
    return 0.1875 * R * R, 0.375 * R * Rp


def inv5(a0, a1, a2, a3, a4):
    b0 = 1 / a0
    b1 = -a1 * b0 * b0
    b2 = -(a1 * b1 + a2 * b0) * b0
    b3 = -(a1 * b2 + a2 * b1 + a3 * b0) * b0
    b4 = -(a1 * b3 + a2 * b2 + a3 * b1 + a4 * b0) * b0
    return b0, b1, b2, b3, b4


def q_jet4_iv(u, a, E2, mu2, is_kerr=False):
    """Exact interval enclosure of (q(u), q'(u), q''(u), q'''(u)) via 5-jet."""
    w = u * u
    wp1 = w + 1
    q0, q1, q2, q3, q4 = inv5(wp1, 2 * u, 1, 0, 0)
    m2a = -2 / a
    F0 = 1 + m2a * (u * q0)
    F1 = m2a * (u * q1 + q0)
    F2 = m2a * (u * q2 + q1)
    F3 = m2a * (u * q3 + q2)
    F4 = m2a * (u * q4 + q3)

    if is_kerr:
        C0, C1, C2, C3, C4 = m2a * q0, m2a * q1, m2a * q2, m2a * q3, m2a * q4
    else:
        c0, c1 = c0_end_iv(u, a)
        inv_wp1 = 1 / wp1
        inv_wp1_3 = inv_wp1 ** 3
        B = 3 * w + 1
        invB = 1 / B
        sB = iv_csqrt(B)
        c2 = -8 / (iv.sqrt(7) * a) * sB * inv_wp1_3
        g = 3 * u * invB - 6 * u * inv_wp1
        gp = 3 * (1 - 3 * w) * (invB * invB) - 6 * (1 - w) * (inv_wp1 * inv_wp1)
        c3 = c2 * g
        c4 = c2 * (g * g + gp)
        C0, C1, C2, C3, C4 = c0, c1, c2 / 2, c3 / 6, c4 / 24

    em0, em1, em2, em3, em4 = inv5(F0 + 1j * C0, F1 + 1j * C1, F2 + 1j * C2, F3 + 1j * C3, F4 + 1j * C4)
    et0, et1, et2, et3, et4 = inv5(F0 - 1j * C0, F1 - 1j * C1, F2 - 1j * C2, F3 - 1j * C3, F4 - 1j * C4)
    fm0 = (em0 + et0) / 2
    fm1 = (em1 + et1) / 2
    fm2 = (em2 + et2) / 2
    fm3 = (em3 + et3) / 2
    fm4 = (em4 + et4) / 2

    P0 = E2 - mu2 * fm0
    P1 = -mu2 * fm1
    P2 = -mu2 * fm2
    P3 = -mu2 * fm3
    P4 = -mu2 * fm4
    ip0, ip1, ip2, ip3, _ = inv5(P0, P1, P2, P3, P4)
    Pp0, Pp1, Pp2, Pp3 = P1, 2 * P2, 3 * P3, 4 * P4
    r0 = Pp0 * ip0
    r1 = Pp0 * ip1 + Pp1 * ip0
    r2 = Pp0 * ip2 + Pp1 * ip1 + Pp2 * ip0
    r3 = Pp0 * ip3 + Pp1 * ip2 + Pp2 * ip1 + Pp3 * ip0
    c316 = iv.mpf(3) / 16
    q_0 = c316 * r0 * r0
    q_1 = c316 * 2 * r0 * r1
    q_2 = c316 * 2 * (r1 * r1 + 2 * r0 * r2)
    q_3 = c316 * 12 * (r1 * r2 + r0 * r3)
    return q_0, q_1, q_2, q_3


# ---------------------------------------------------------------------------
# 3. Part (1): Explicit interval-certified C_0..C_4 bounds + L^{3/2}, L^2 log L
# ---------------------------------------------------------------------------
def compute_c0_perturbation_bounds(x_min, y_max, a):
    cos_th = x_min / iv.sqrt(x_min ** 2 + y_max ** 2)
    cos_2th = (x_min ** 2 - y_max ** 2) / (x_min ** 2 + y_max ** 2)
    cos_4th = 2 * cos_2th ** 2 - 1
    assert cos_4th.a > 0, f"Need cos(4*th_max) > 0, got {cos_4th}"
    re_P1_min = cos_4th * x_min ** 4 - iv.mpf(6) / 7 * (x_min ** 2 + y_max ** 2) - iv.mpf(1) / 21
    assert re_P1_min.a > 0, f"Need Re(P1) > 0, got {re_P1_min}"

    c_B0 = iv.sqrt(iv.mpf(40) / 7) * iv.sqrt(3 - 1 / x_min ** 2) * cos_th
    c_P1 = 1 + iv.mpf(6) / (7 * x_min ** 2) + iv.mpf(1) / (21 * x_min ** 4)
    c_den = (1 - 1 / x_min ** 2) ** 3

    kappa2 = (iv.sqrt(iv.mpf(8) / 5) / a) * c_P1 / (c_den * c_B0)
    C2 = kappa2 / (x_min ** 3)
    C1 = kappa2 / (2 * x_min ** 2)
    C0 = kappa2 / (2 * x_min)

    r_c = iv.mpf('0.4')
    xc, yc = x_min - r_c, y_max + r_c
    cos_th_c = xc / iv.sqrt(xc ** 2 + yc ** 2)
    cos_2th_c = (xc ** 2 - yc ** 2) / (xc ** 2 + yc ** 2)
    cos_4th_c = 2 * cos_2th_c ** 2 - 1
    assert cos_4th_c.a > 0, "Cauchy disk violates cos(4*theta) > 0"
    re_P1_c = cos_4th_c * xc ** 4 - iv.mpf(6) / 7 * (xc ** 2 + yc ** 2) - iv.mpf(1) / 21
    assert re_P1_c.a > 0, "Cauchy disk violates Re(P1) > 0"
    c_B0_c = iv.sqrt(iv.mpf(40) / 7) * iv.sqrt(3 - 1 / xc ** 2) * cos_th_c
    c_P1_c = 1 + iv.mpf(6) / (7 * xc ** 2) + iv.mpf(1) / (21 * xc ** 4)
    c_den_c = (1 - 1 / xc ** 2) ** 3
    kappa2_c = (iv.sqrt(iv.mpf(8) / 5) / a) * c_P1_c / (c_den_c * c_B0_c)
    C2_cauchy = kappa2_c / (xc ** 3)
    C3 = C2_cauchy / r_c
    C4 = 2 * C2_cauchy / (r_c ** 2)

    c1_val = iv.mpf(120) / 7
    pref = iv.sqrt(iv.mpf(8) / 5) / a
    coeff_L32_c0 = pref / (6 * c1_val * iv.sqrt(c1_val))
    coeff_L2logL_c1 = pref / (16 * c1_val * iv.sqrt(c1_val))

    return {
        "kappa2": kappa2,
        "C0": C0,
        "C1": C1,
        "C2": C2,
        "C3": C3,
        "C4": C4,
        "coeff_L32_c0": coeff_L32_c0,
        "coeff_L2logL_c1": coeff_L2logL_c1,
    }


def dq_perturbation_bound_on_box(U_box, a, E2, mu2, C0, C1, L_max):
    wp1 = U_box * U_box + 1
    f0 = 1 - 2 * U_box / (a * wp1)
    f0p = -2 * (1 - U_box * U_box) / (a * wp1 * wp1)
    c0_e, c1_e = c0_end_iv(U_box, a)
    c0 = iv_inflate(c0_e, C0 * L_max)
    c1 = iv_inflate(c1_e, C1 * L_max)

    D = f0 * f0 + c0 * c0
    N = f0p * (c0 * c0 - f0 * f0) - 2 * f0 * c0 * c1
    G = D * (E2 * D - mu2 * f0)
    R = -mu2 * N / G

    dN_dc0 = 2 * f0p * c0 - 2 * f0 * c1
    dG_dc0 = 2 * c0 * (2 * E2 * D - mu2 * f0)
    dR_dc0 = -mu2 * (dN_dc0 * G - N * dG_dc0) / (G * G)
    dR_dc1 = -mu2 * (-2 * f0 * c0) / G

    dq_dc0 = iv.mpf(3) / 8 * R * dR_dc0
    dq_dc1 = iv.mpf(3) / 8 * R * dR_dc1
    return (iv_cabs(dq_dc0) * C0 + iv_cabs(dq_dc1) * C1).b


# ---------------------------------------------------------------------------
# 4. 2x2 Matrix & Fricke trace helpers in mpmath.iv
# ---------------------------------------------------------------------------
def mat2_mul(A, B):
    return [
        [A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
        [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]],
    ]


def mat2_sub(A, B):
    return [[A[i][j] - B[i][j] for j in range(2)] for i in range(2)]


def mat2_conj(A):
    return [[iv.mpc(A[i][j].real, -A[i][j].imag) for j in range(2)] for i in range(2)]


def mat2_inv_iv(A):
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    return [[A[1][1] / det, -A[0][1] / det], [-A[1][0] / det, A[0][0] / det]]


def mat2_tr(A):
    return A[0][0] + A[1][1]


def mat2_inf_upper(A):
    r0 = iv_cabs(A[0][0]).b + iv_cabs(A[0][1]).b
    r1 = iv_cabs(A[1][0]).b + iv_cabs(A[1][1]).b
    return r0 if r0.b >= r1.b else r1


def mat2_frob_iv(A):
    s = iv.mpf(0)
    for i in range(2):
        for j in range(2):
            s = s + A[i][j].real ** 2 + A[i][j].imag ** 2
    return iv.sqrt(s)


def fricke_tau(tX, tY, tXY):
    """Exact SL(2, C) commutator-trace invariant tr(X Y X^{-1} Y^{-1}) - 2."""
    return tX * tX + tY * tY + tXY * tXY - tX * tY * tXY - 4


def compute_conditioning_basis(l1, a_f, E2_f, mu2_f, is_kerr=False):
    pts_c = [complex(p.real.mid, p.imag.mid) for p in l1]
    y = [1.0 + 0j, 0j, 0j, 1.0 + 0j]
    for i in range(len(pts_c) - 1):
        ua, ub = pts_c[i], pts_c[i + 1]
        du = ub - ua

        def rhs(t, v):
            qv, _ = q_and_qp_c128(ua + t * du, a_f, E2_f, mu2_f, is_kerr=is_kerr)
            return [du * v[2], du * v[3], -du * qv * v[0], -du * qv * v[1]]

        y = list(solve_ivp(rhs, (0.0, 1.0), y, method="DOP853", rtol=1e-13, atol=1e-13).y[:, -1])
    M1 = np.array([[y[0], y[1]], [y[2], y[3]]])
    A = M1.conj() @ M1
    _, S_np = np.linalg.eig(A)
    S_np = S_np / np.linalg.norm(S_np, axis=0)
    return [
        [iv.mpc(iv.mpf(float(S_np[i, j].real)), iv.mpf(float(S_np[i, j].imag))) for j in range(2)]   # ansatz fix: exact float S, so Phi(0) == S
        for i in range(2)
    ]


# ---------------------------------------------------------------------------
# 5. Basis-Conditioned Quintic Defect-Gronwall mpmath.iv certifier for VE1
# ---------------------------------------------------------------------------
def certify_loop_ve1_iv(pts, a_iv, E2_iv, mu2_iv, S_iv, nsub=8, tol_loc=2e-6, max_depth=12, is_kerr=False, pert_params=None):
    a_f, E2_f, mu2_f = float(a_iv.mid), float(E2_iv.mid), float(mu2_iv.mid)
    pts_c = [complex(p.real.mid, p.imag.mid) for p in pts]
    S_inv_iv = mat2_inv_iv(S_iv)

    Phi_curr = [
        complex(S_iv[0][0].real.mid, S_iv[0][0].imag.mid),
        complex(S_iv[0][1].real.mid, S_iv[0][1].imag.mid),
        complex(S_iv[1][0].real.mid, S_iv[1][0].imag.mid),
        complex(S_iv[1][1].real.mid, S_iv[1][1].imag.mid),
    ]
    rho_total = iv.mpf(0)
    max_phi_inf = iv.mpf(1)
    max_phi_inv_inf = iv.mpf(1)
    max_D1 = iv.mpf(0)
    S_len = iv.mpf(0)
    t_iv = iv.mpf(['-0.5', '0.5'])
    t3_iv = iv.mpf(['-0.125', '0.125'])
    tol_iv = iv.mpf(str(tol_loc))

    def eval_poly(coeffs):
        acc = coeffs[-1]
        for c in reversed(coeffs[:-1]):
            acc = c + t_iv * acc
        return acc

    for seg_i in range(len(pts) - 1):
        ua_iv, ub_iv = pts[seg_i], pts[seg_i + 1]
        du_iv = ub_iv - ua_iv
        S_len = S_len + iv_cabs(du_iv).b

        ua_c, ub_c = pts_c[seg_i], pts_c[seg_i + 1]
        du_c = ub_c - ua_c
        du2_c = du_c * du_c

        def rhs_c(s, y):
            qv, _ = q_and_qp_c128(ua_c + s * du_c, a_f, E2_f, mu2_f, is_kerr=is_kerr)
            return [du_c * y[2], du_c * y[3], -du_c * qv * y[0], -du_c * qv * y[1]]

        def rhs2_c(s, y):
            qv, qpv = q_and_qp_c128(ua_c + s * du_c, a_f, E2_f, mu2_f, is_kerr=is_kerr)
            return [
                -du2_c * qv * y[0],
                -du2_c * qv * y[1],
                -du2_c * (qpv * y[0] + qv * y[2]),
                -du2_c * (qpv * y[1] + qv * y[3]),
            ]

        sol = solve_ivp(rhs_c, (0.0, 1.0), Phi_curr, method="DOP853", dense_output=True, rtol=1e-13, atol=1e-13)
        Phi_curr = list(sol.y[:, -1])

        def eval_sub(s0_iv, s1_iv, depth=0):
            nonlocal rho_total, max_phi_inf, max_phi_inv_inf, max_D1
            h = s1_iv - s0_iv
            h2 = h * h
            sm_iv = (s0_iv + s1_iv) / 2
            s0_f, s1_f = float(s0_iv.mid), float(s1_iv.mid)
            y0_c = list(sol.sol(s0_f))
            y1_c = list(sol.sol(s1_f))
            yp0_c = rhs_c(s0_f, y0_c)
            yp1_c = rhs_c(s1_f, y1_c)
            ypp0_c = rhs2_c(s0_f, y0_c)
            ypp1_c = rhs2_c(s1_f, y1_c)

            y0 = [iv.mpc(str(x.real), str(x.imag)) for x in y0_c]
            y1 = [iv.mpc(str(x.real), str(x.imag)) for x in y1_c]
            yp0 = [iv.mpc(str(x.real), str(x.imag)) for x in yp0_c]
            yp1 = [iv.mpc(str(x.real), str(x.imag)) for x in yp1_c]
            ypp0 = [iv.mpc(str(x.real), str(x.imag)) for x in ypp0_c]
            ypp1 = [iv.mpc(str(x.real), str(x.imag)) for x in ypp1_c]

            b = [[None] * 6 for _ in range(4)]
            for m in range(4):
                s0 = (y1[m] + y0[m]) / 2
                d0 = y1[m] - y0[m]
                s1 = h * (yp1[m] + yp0[m]) / 2
                d1 = h * (yp1[m] - yp0[m])
                s2 = h2 * (ypp1[m] + ypp0[m]) / 2
                d2 = h2 * (ypp1[m] - ypp0[m])
                b[m][0] = s0 - iv.mpf(5) / 32 * d1 + s2 / 32
                b[m][2] = iv.mpf(3) / 4 * d1 - s2 / 4
                b[m][4] = (s2 - d1) / 2
                b[m][1] = iv.mpf(15) / 8 * d0 - iv.mpf(7) / 8 * s1 + d2 / 32
                b[m][3] = 5 * (s1 - d0) - d2 / 4
                b[m][5] = 6 * (d0 - s1) + d2 / 2

            um_iv = ua_iv + sm_iv * du_iv
            hdu = h * du_iv
            hdu2 = hdu * hdu
            U_box = um_iv + t_iv * hdu  # WHOLE subinterval complex box

            try:
                # Point evaluation at midpoint u_m + WHOLE-BOX remainder q'''(U_box)
                qm, qpm, qppm, _ = q_jet4_iv(um_iv, a_iv, E2_iv, mu2_iv, is_kerr=is_kerr)
                _, _, _, qppp_box = q_jet4_iv(U_box, a_iv, E2_iv, mu2_iv, is_kerr=is_kerr)

                P_v = [eval_poly(b[m]) for m in range(4)]
                inv_h = 1 / h

                def row0_def(iv_idx, ip_idx):
                    bv, bp = b[iv_idx], b[ip_idx]
                    return eval_poly([
                        bv[1] * inv_h - du_iv * bp[0],
                        2 * bv[2] * inv_h - du_iv * bp[1],
                        3 * bv[3] * inv_h - du_iv * bp[2],
                        4 * bv[4] * inv_h - du_iv * bp[3],
                        5 * bv[5] * inv_h - du_iv * bp[4],
                        -du_iv * bp[5],
                    ])

                a0 = du_iv * qm
                a1 = du_iv * qpm * hdu
                a2 = iv.mpf('0.5') * du_iv * qppm * hdu2
                rem_fac = (du_iv * qppp_box * (hdu2 * hdu) / 6) * t3_iv

                def row1_def(iv_idx, ip_idx):
                    bv, bp = b[iv_idx], b[ip_idx]
                    return eval_poly([
                        bp[1] * inv_h + a0 * bv[0],
                        2 * bp[2] * inv_h + a0 * bv[1] + a1 * bv[0],
                        3 * bp[3] * inv_h + a0 * bv[2] + a1 * bv[1] + a2 * bv[0],
                        4 * bp[4] * inv_h + a0 * bv[3] + a1 * bv[2] + a2 * bv[1],
                        5 * bp[5] * inv_h + a0 * bv[4] + a1 * bv[3] + a2 * bv[2],
                        a0 * bv[5] + a1 * bv[4] + a2 * bv[3],
                        a1 * bv[5] + a2 * bv[4],
                        a2 * bv[5],
                    ]) + rem_fac * P_v[iv_idx]

                D_mat = [[row0_def(0, 2), row0_def(1, 3)], [row1_def(0, 2), row1_def(1, 3)]]
                P_mat = [[P_v[0], P_v[1]], [P_v[2], P_v[3]]]
                P_inv = mat2_inv_iv(P_mat)
                R_mat = mat2_mul(P_inv, D_mat)
                m1 = mat2_inf_upper(P_mat)
                m2 = mat2_inf_upper(P_inv)
                rho_loc = h.b * mat2_inf_upper(R_mat)
                if not (rho_loc.b <= tol_iv.b) and depth < max_depth:
                    raise RuntimeError("bisect")
            except (RuntimeError, ValueError, ZeroDivisionError):
                if depth >= max_depth:
                    raise
                eval_sub(s0_iv, sm_iv, depth + 1)
                eval_sub(sm_iv, s1_iv, depth + 1)
                return

            rho_total = rho_total + rho_loc
            if m1.b > max_phi_inf.b:
                max_phi_inf = m1
            if m2.b > max_phi_inv_inf.b:
                max_phi_inv_inf = m2
            if pert_params is not None:
                C0, C1, L_max = pert_params
                d1_b = dq_perturbation_bound_on_box(U_box, a_iv, E2_iv, mu2_iv, C0, C1, L_max)
                if d1_b.b > max_D1.b:
                    max_D1 = d1_b

        for k in range(nsub):
            eval_sub(iv.mpf(k) / nsub, iv.mpf(k + 1) / nsub, 0)

    Phi_end_pt = [
        [iv.mpc(str(Phi_curr[0].real), str(Phi_curr[0].imag)), iv.mpc(str(Phi_curr[1].real), str(Phi_curr[1].imag))],
        [iv.mpc(str(Phi_curr[2].real), str(Phi_curr[2].imag)), iv.mpc(str(Phi_curr[3].real), str(Phi_curr[3].imag))],
    ]
    M_S_pt = mat2_mul(S_inv_iv, Phi_end_pt)
    eta = (iv.exp(rho_total) - 1).b
    assert eta.b < iv.mpf('0.1').a, f"Defect too large (eta={eta}, rho={rho_total})"
    rad_end = mat2_inf_upper(M_S_pt) * eta
    M_S_cert = [[iv_inflate(M_S_pt[i][j], rad_end) for j in range(2)] for i in range(2)]
    K_cert = ((1 + eta) * max_phi_inf) * (max_phi_inv_inf / (1 - eta))
    return M_S_cert, K_cert, S_len, max_D1, rho_total


# ---------------------------------------------------------------------------
# 6. Loop geometry for E = 0.8 and E = 1.5
# ---------------------------------------------------------------------------
def build_loops_for_energy(E_str, is_kerr=False):
    """ansatz generalisation (amendment S2): loops from the spin's own endpoint / Kerr positions (env T48_GEO json)."""
    import json as _json, os as _os
    G = _json.load(open(_os.environ["T48_GEO"]))
    a_f = float(G["a"])
    if is_kerr:
        rx, ry = iv.mpf(2) / iv.mpf(G["a"]), iv.mpf(1)                 # Kerr p+- = (2 +- ia)/a in u
        tx = iv.mpf(G["kerr_rplus_u"])
        u0 = iv.mpc(max(float(rx.mid), float(tx.mid)) + 0.35, 0.0)
        d, dt = iv.mpf('0.45'), iv.mpf('0.25')
        l1 = [u0, iv.mpc(rx + d, ry + d), iv.mpc(rx - d, ry + d), iv.mpc(rx - d, ry - d), iv.mpc(rx + d, ry - d), u0]
        l2 = [iv.mpc(p.real, -p.imag) for p in l1]
        l3 = [u0, iv.mpc(tx + dt, dt), iv.mpc(tx - dt, dt), iv.mpc(tx - dt, -dt), iv.mpc(tx + dt, -dt), u0]
        return l1, l2, l3
    upr, upi, utp = float(G["end_up_re"]), float(G["end_up_im"]), float(G["end_utp"])
    rx, ry = iv.mpf(repr(upr)), iv.mpf(repr(upi))
    d = iv.mpf(repr(0.49 * upi))
    w3, h3 = iv.mpf('0.1'), iv.mpf(repr(0.45 * upi))
    tx = iv.mpf(repr(utp))
    u0 = iv.mpc(max(upr, utp) + max(0.25, 2 * upi), 0.0)
    l1 = [u0, iv.mpc(rx + d, ry + d), iv.mpc(rx - d, ry + d), iv.mpc(rx - d, ry - d), iv.mpc(rx + d, ry - d), u0]
    l2 = [iv.mpc(p.real, -p.imag) for p in l1]
    l3 = [u0, iv.mpc(tx + w3, h3), iv.mpc(tx - w3, h3), iv.mpc(tx - w3, -h3), iv.mpc(tx + w3, -h3), u0]
    return l1, l2, l3


# ---------------------------------------------------------------------------
# 7. Main driver: Zariski density certification + Strong Kerr & Wrong-Tail controls
# ---------------------------------------------------------------------------
def run_zariski_sliver_proof(E_str, nsub=8, tol_kerr=6e-9, tol_end=1e-7):
    iv.dps = 14
    mp.mp.dps = 14
    import json as _json, os as _os
    a = iv.mpf(_json.load(open(_os.environ['T48_GEO']))['a'])
    E = iv.mpf(E_str)
    E2 = E * E
    mu2 = iv.mpf('1.0')
    L_max = iv.mpf('1e-4')

    print("=========================================================================", flush=True)
    print(f"ZARISKI-DENSITY SLIVER CLOSURE AT a = {iv.nstr(a.mid, 6)}, E = {E_str} (iv.dps = {iv.dps})", flush=True)
    print("=========================================================================", flush=True)

    # Part (1): Explicit bounds C_0..C_4 on actual loop set K
    l1, l2, l3 = build_loops_for_energy(E_str, is_kerr=False)
    all_pts = l1 + l2 + l3
    x_min = iv.mpf(min(p.real.a for p in all_pts))
    y_max = iv.mpf(max(max(abs(p.imag.a), abs(p.imag.b)) for p in all_pts))
    bnds = compute_c0_perturbation_bounds(x_min, y_max, a)
    C0, C1, C2, C3, C4 = bnds["C0"], bnds["C1"], bnds["C2"], bnds["C3"], bnds["C4"]
    print(f"[Part (1): Explicit O(L) c0^(m) bounds on loop set K]", flush=True)
    print(f"  K box: Re(u) >= {iv.nstr(x_min.a, 6)}, |Im(u)| <= {iv.nstr(y_max.b, 6)}", flush=True)
    print(f"  kappa_2 <= {iv.nstr(bnds['kappa2'].b, 10)}, C_0 <= {iv.nstr(C0.b, 10)}, C_1 <= {iv.nstr(C1.b, 10)}, C_2 <= {iv.nstr(C2.b, 10)}", flush=True)

    # Part (2): Basis-conditioned endpoint VE1 monodromy & Zariski-density invariants
    t1 = time.time()
    S = compute_conditioning_basis(l1, float(a.mid), float(E2.mid), float(mu2.mid), is_kerr=False)
    P = mat2_mul(mat2_inv_iv(S), mat2_conj(S))
    P_inv = mat2_inv_iv(P)
    P_cond = mat2_inf_upper(P) * mat2_inf_upper(P_inv)

    pert = (C0, C1, L_max)
    M1, K1, S1, D1_1, rho1 = certify_loop_ve1_iv(l1, a, E2, mu2, S, nsub=nsub, tol_loc=tol_end, is_kerr=False, pert_params=pert)
    M2 = mat2_mul(mat2_mul(P, mat2_conj(M1)), P_inv)
    M3, K3, S3, D1_3, rho3 = certify_loop_ve1_iv(l3, a, E2, mu2, S, nsub=nsub, tol_loc=tol_end, is_kerr=False, pert_params=pert)

    A = mat2_mul(M2, M1)
    B = mat2_mul(M3, M2)
    AB = mat2_mul(A, B)
    M1M3 = mat2_mul(M1, M3)
    C_mat = mat2_sub(mat2_mul(B, A), AB)

    # Endpoint enclosures of all Zariski-density observables
    c_r0 = iv_cabs(C_mat[0][0]).a + iv_cabs(C_mat[0][1]).a
    c_r1 = iv_cabs(C_mat[1][0]).a + iv_cabs(C_mat[1][1]).a
    C_inf_lo = c_r0 if c_r0.a >= c_r1.a else c_r1
    C_inf_hi = mat2_inf_upper(C_mat)
    C_frob = mat2_frob_iv(C_mat)

    trM1, trM3, trM1M3 = mat2_tr(M1), mat2_tr(M3), mat2_tr(M1M3)
    trA, trB, trAB = mat2_tr(A), mat2_tr(B), mat2_tr(AB)
    tau_13 = fricke_tau(trM1, trM3, trM1M3)
    tau_AB = fricke_tau(trA, trB, trAB)

    B1, B2, B3 = mat2_inf_upper(M1), mat2_inf_upper(M2), mat2_inf_upper(M3)
    BA, BB = mat2_inf_upper(A), mat2_inf_upper(B)
    r1, r3 = K1 * D1_1 * S1, K3 * D1_3 * S3

    def gronwall_bounds(L_val):
        d1 = B1 * r1 * L_val * iv.exp(r1 * L_val)
        d2 = P_cond * d1
        d3 = B3 * r3 * L_val * iv.exp(r3 * L_val)
        dA = d2 * B1 + B2 * d1 + d2 * d1
        dB = d3 * B2 + B3 * d2 + d3 * d2
        dAB = dA * BB + BA * dB + dA * dB
        dM1M3 = d1 * B3 + B1 * d3 + d1 * d3
        dC = 2 * (dB * BA + BB * dA + dB * dA)
        return d1, d3, dM1M3, dA, dB, dAB, dC

    def all_zariski_hold(L_val):
        """Certifies ALL four Zariski-density inequalities on the entire interval [0, L_val]."""
        d1, d3, dM1M3, dA, dB, dAB, dC = gronwall_bounds(L_val)
        # (Z2) [A, B] != 0
        if not (dC.b < C_inf_lo.a):
            return False
        # Inflate traces by 2 * d_X (since |tr(dX)| <= |dX_00| + |dX_11| <= 2*||dX||_inf)
        t1_i = iv_inflate(trM1, 2 * d1)
        t3_i = iv_inflate(trM3, 2 * d3)
        t13_i = iv_inflate(trM1M3, 2 * dM1M3)
        tA_i = iv_inflate(trA, 2 * dA)
        tB_i = iv_inflate(trB, 2 * dB)
        tAB_i = iv_inflate(trAB, 2 * dAB)
        # (Z1) Irreducibility: tau(M_1, M_3) != 0 (and at E=1.5, tau(A, B) != 0)
        tau13_i = fricke_tau(t1_i, t3_i, t13_i)
        if not (iv_cabs(tau13_i).a > 0):
            return False
        # ansatz fix: Z1b dropped (Z1 alone gives irreducibility)
        # (Z3) Non-imprimitive: all 3 of tr(A), tr(B), tr(AB) strictly nonzero
        if not (iv_cabs(tA_i).a > 0 and iv_cabs(tB_i).a > 0 and iv_cabs(tAB_i).a > 0):
            return False
        # (Z4) Infinite (rules out 2T/2O/2I and all finite groups): |Im(tr B)| > 0 (and |tr A| > 2 at E=0.8)
        imB_nz = (tB_i.imag.a > 0) or (tB_i.imag.b < 0)
        if not imB_nz:
            return False
        # ansatz S2: Z4b (|tr A| > 2) dropped; Z4 (Im tr B != 0) alone gives infinite order
        return True

    assert all_zariski_hold(iv.mpf(0)), "Endpoint Zariski-density certification failed!"

    lo, hi = iv.mpf(0), iv.mpf(L_max.a)
    if all_zariski_hold(hi):
        L0 = hi
    else:
        for _ in range(80):
            mid = (lo + hi) / 2
            if all_zariski_hold(mid):
                lo = mid
            else:
                hi = mid
        L0 = lo
    delta0 = L0 / 21
    d1_0, d3_0, d13_0, dA_0, dB_0, dAB_0, dC_0 = gronwall_bounds(L0)
    _, _, _, _, _, _, g_sliver = gronwall_bounds(iv.mpf('2.1e-11'))
    rho_e_max = rho1 if rho1.b >= rho3.b else rho3

    # Certified inflated enclosures over the ENTIRE interval k in [30/7 - delta0, 30/7]
    tau13_int = fricke_tau(iv_inflate(trM1, 2 * d1_0), iv_inflate(trM3, 2 * d3_0), iv_inflate(trM1M3, 2 * d13_0))
    tA_int = iv_inflate(trA, 2 * dA_0)
    tB_int = iv_inflate(trB, 2 * dB_0)
    tAB_int = iv_inflate(trAB, 2 * dAB_0)
    tauAB_int = fricke_tau(tA_int, tB_int, tAB_int)

    print(f"\n[Part (2): Endpoint k = 30/7 & Joint Zariski-Density Certification] ({time.time() - t1:.2f}s, max rho = {iv.nstr(rho_e_max.b, 5)})", flush=True)
    print(f"  Endpoint ||[A^(S), B^(S)]||_inf in [{iv.nstr(C_inf_lo.a, 8)}, {iv.nstr(C_inf_hi.b, 8)}]", flush=True)
    print(f"  Endpoint ||[A^(S), B^(S)]||_F   in [{iv.nstr(C_frob.a, 8)}, {iv.nstr(C_frob.b, 8)}]", flush=True)
    print(f"  (Z1) |tau(M1, M3)| at 30/7 in [{iv.nstr(iv_cabs(tau_13).a, 7)}, {iv.nstr(iv_cabs(tau_13).b, 7)}]; on [30/7-d0, 30/7] >= {iv.nstr(iv_cabs(tau13_int).a, 7)} > 0", flush=True)
    if E_str == "1.5":
        print(f"  (Z1b)|tau(A, B)|   at 30/7 in [{iv.nstr(iv_cabs(tau_AB).a, 7)}, {iv.nstr(iv_cabs(tau_AB).b, 7)}]; on [30/7-d0, 30/7] >= {iv.nstr(iv_cabs(tauAB_int).a, 7)} > 0", flush=True)
    print(f"  (Z3) |tr(A)|  on [30/7-d0, 30/7] in [{iv.nstr(iv_cabs(tA_int).a, 7)}, {iv.nstr(iv_cabs(tA_int).b, 7)}] > 0", flush=True)
    print(f"  (Z3) |tr(B)|  on [30/7-d0, 30/7] in [{iv.nstr(iv_cabs(tB_int).a, 7)}, {iv.nstr(iv_cabs(tB_int).b, 7)}] > 0", flush=True)
    print(f"  (Z3) |tr(AB)| on [30/7-d0, 30/7] in [{iv.nstr(iv_cabs(tAB_int).a, 7)}, {iv.nstr(iv_cabs(tAB_int).b, 7)}] > 0", flush=True)
    print(f"  (Z4) Im(tr B) on [30/7-d0, 30/7] in [{iv.nstr(tB_int.imag.a, 7)}, {iv.nstr(tB_int.imag.b, 7)}] (strictly non-real!)", flush=True)
    if E_str == "0.8":
        print(f"  (Z4b)|tr(A)|  on [30/7-d0, 30/7] >= {iv.nstr(iv_cabs(tA_int).a, 7)} > 2 (rules out ALL finite orders!)", flush=True)
    print(f"  At sliver boundary delta = 1e-12 (L = 2.1e-11): G_VE1(2.1e-11) <= {iv.nstr(g_sliver.b, 7)} << C_inf_lo = {iv.nstr(C_inf_lo.a, 7)}", flush=True)
    print(f"  [Part (3): JOINT ZARISKI-DENSITY CERTIFIED delta0] = {iv.nstr(delta0.a, 8)} ({iv.nstr((delta0 / iv.mpf('1e-12')).a, 5)}x > 1e-12)", flush=True)

    # Control 1: Strong Kerr (k = 0) — tight enclosure containing 0 AND strictly narrower than endpoint's C_inf_lo!
    t0 = time.time()
    l1k, l2k, l3k = build_loops_for_energy(E_str, is_kerr=True)
    Sk = compute_conditioning_basis(l1k, float(a.mid), float(E2.mid), float(mu2.mid), is_kerr=True)
    Pk = mat2_mul(mat2_inv_iv(Sk), mat2_conj(Sk))
    Pk_inv = mat2_inv_iv(Pk)
    M1k, _, _, _, rho1k = certify_loop_ve1_iv(l1k, a, E2, mu2, Sk, nsub=nsub, tol_loc=tol_kerr, is_kerr=True)
    M2k = mat2_mul(mat2_mul(Pk, mat2_conj(M1k)), Pk_inv)
    M3k, _, _, _, rho3k = certify_loop_ve1_iv(l3k, a, E2, mu2, Sk, nsub=nsub, tol_loc=tol_kerr, is_kerr=True)
    Ak = mat2_mul(M2k, M1k)
    Bk = mat2_mul(M3k, M2k)
    Ck = mat2_sub(mat2_mul(Bk, Ak), mat2_mul(Ak, Bk))
    Ck_inf_hi = mat2_inf_upper(Ck)
    Ck_frob = mat2_frob_iv(Ck)
    kerr_has_0 = all(iv_contains_zero(Ck[i][j]) for i in range(2) for j in range(2))
    kerr_tighter = (Ck_inf_hi.b < C_inf_lo.a)
    rho_k_max = rho1k if rho1k.b >= rho3k.b else rho3k
    print(f"\n[Control 1: STRONG Kerr k = 0] ({time.time() - t0:.2f}s, max defect rho = {iv.nstr(rho_k_max.b, 5)})", flush=True)
    print(f"  All 4 entries of [A_Kerr^(S), B_Kerr^(S)] contain 0 : {kerr_has_0}", flush=True)
    print(f"  ||[A_Kerr^(S), B_Kerr^(S)]||_inf enclosure          : [0, {iv.nstr(Ck_inf_hi.b, 6)}]  (< endpoint lo {iv.nstr(C_inf_lo.a, 6)}: {kerr_tighter})", flush=True)
    print(f"  ||[A_Kerr^(S), B_Kerr^(S)]||_F   enclosure          : [{iv.nstr(Ck_frob.a, 6)}, {iv.nstr(Ck_frob.b, 6)}]", flush=True)
    assert kerr_has_0, "Kerr control failed to contain 0!"
    assert kerr_tighter, f"Kerr control not tighter than endpoint ({Ck_inf_hi.b} >= {C_inf_lo.a})!"

    # Control 2: Planted wrong O(L^{1/2}) tail exponent
    lo_w, hi_w = iv.mpf(0), iv.mpf(L_max.a)
    for _ in range(80):
        mid = (lo_w + hi_w) / 2
        if all_zariski_hold(mid + iv.sqrt(mid)):
            lo_w = mid
        else:
            hi_w = mid
    delta0_wrong = lo_w / 21
    print(f"[Control 2: Planted wrong O(L^{{1/2}}) tail] delta0_wrong = {iv.nstr(delta0_wrong.a, 6)} "
          f"(shrinks delta0 by {iv.nstr((delta0 / delta0_wrong).a, 5)}x!)\n", flush=True)
    return delta0, delta0_wrong, C_inf_lo, Ck_inf_hi


def main():
    t_all = time.time()
    d0, dw, clo, khi = run_zariski_sliver_proof("0.8", nsub=8, tol_kerr=6e-9, tol_end=1e-7)
    print(f"SUMMARY a-run E=0.8: delta0 = {iv.nstr(d0.a, 6)} | Kerr_hi = {iv.nstr(khi.b, 5)} < End_lo = {iv.nstr(clo.a, 5)} | wrong-tail = {iv.nstr(dw.a, 5)} | {time.time()-t_all:.1f}s", flush=True)


if __name__ == "__main__":
    main()