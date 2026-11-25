#!/usr/bin/env python3
"""Interval certificate that c2 != 0 (data/nve/C2_ANALYTIC.md, section 6).
[model: Fable 5.2; UNVERIFIED until the office ansatz-machine checks it]

Certifies, in mpmath.iv (outward-rounded interval arithmetic), at E = 4/5 and one spin:
    Im I_plus != 0,   Im I_minus != 0,   Re(kappa*omega) != 0,
where c2 = sinh^2(kappa*omega) * I_plus * I_minus / kappa^2. Formulas are those of scripts/_nve_c2_analytic.py,
re-implemented here on intervals.

Method (the same for both integrals). For h 2*pi-periodic, analytic and |h| <= M on the strip |Im theta| <= sigma,
the N-point trapezoid sum T_N obeys |T_N - integral| <= 4*pi*M / (exp(sigma*N) - 1) (Trefethen-Weideman 2014,
Thm 3.2). So an enclosure needs: (1) h at the N nodes, on intervals; (2) ANY rigorous M, taken here from interval
boxes covering the two boundary lines of the strip (maximum modulus on the periodic strip).
  - I_pm: theta is the angle on |z| = R0; the strip is the annulus R_in <= |z| <= R_out, with a < R_in and
    R_out < min|root|, so the integrand is analytic there (its only singularities are the cross
    [-a/sqrt3, a/sqrt3] u [-ia, ia] and the roots r+-, p+-).
  - omega: z = c - (d/2) cos(phi) maps [0, pi] onto the segment r+ -> p+; the integrand is even and periodic.
  - U(z) = int_0^z ds/sqrt(N D): Taylor series at 0 with a rigorous tail from the majorant
    prod (1 - x/|root|)^(-1/2).
Every square root and logarithm is taken of a box with positive real part (checked on every call; a box that fails
is subdivided, and the run aborts if that does not help).

    NVE_SPIN=3/5 python scripts/_nve_c2_certify.py       # about 10 s on one core
    NVE_SPIN=3/5 C2_PLANT=holo python scripts/_nve_c2_certify.py     # must-fail control
"""
import os
import sys
import time
from fractions import Fraction

from mpmath import iv

iv.dps = 40
t0 = time.time()
A = Fraction(os.environ.get("NVE_SPIN", "3/5"))
PLANT = os.environ.get("C2_PLANT", "") == "holo"


def R(p, q=1):
    return iv.mpf(p) / iv.mpf(q)


class NotRHP(Exception):
    pass


class C:
    """Complex interval box."""
    __slots__ = ("re", "im")

    def __init__(self, re, im=0):
        self.re, self.im = iv.mpf(re), iv.mpf(im)

    def __add__(self, o):
        o = o if isinstance(o, C) else C(o)
        return C(self.re + o.re, self.im + o.im)
    __radd__ = __add__

    def __neg__(self):
        return C(-self.re, -self.im)

    def __sub__(self, o):
        o = o if isinstance(o, C) else C(o)
        return C(self.re - o.re, self.im - o.im)

    def __rsub__(self, o):
        return C(o) - self

    def __mul__(self, o):
        if not isinstance(o, C):
            o = iv.mpf(o)
            return C(self.re * o, self.im * o)
        return C(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)
    __rmul__ = __mul__

    def sq(self):
        return C(self.re ** 2 - self.im ** 2, 2 * self.re * self.im)

    def abs2(self):
        return self.re ** 2 + self.im ** 2

    def inv(self):
        d = self.abs2()
        if not d.a > 0:
            raise NotRHP("division by a box containing 0")
        return C(self.re / d, -self.im / d)

    def __truediv__(self, o):
        if not isinstance(o, C):
            o = iv.mpf(o)
            return C(self.re / o, self.im / o)
        return self * o.inv()

    def __rtruediv__(self, o):
        return C(o) * self.inv()

    def absub(self):
        return iv.sqrt(self.abs2()).b


def csqrt(z):
    if not z.re.a > 0:
        raise NotRHP("sqrt of a box not in the right half-plane")
    r = iv.sqrt(z.abs2())
    u = iv.sqrt((r + z.re) / 2)
    return C(u, z.im / (2 * u))


def clog(z):
    if not z.re.a > 0:
        raise NotRHP("log of a box not in the right half-plane")
    return C(iv.log(z.abs2()) / 2, iv.atan2(z.im, z.re))


def cexp(z):
    e = iv.exp(z.re)
    return C(e * iv.cos(z.im), e * iv.sin(z.im))


def fl(x):
    return float(iv.mpf(x).a) if not isinstance(x, float) else x


def iv_s(x):
    """Display only (endpoints rounded to 13 digits). Every verdict below compares the exact interval endpoints."""
    x = iv.mpf(x)
    return f"[{float(x.a):.13g}, {float(x.b):.13g}]"


I1 = C(0, 1)
a = R(A.numerator, A.denominator)
E2 = R(16, 25)
kappa = a * R(3, 5)                         # a sqrt(1 - E^2), exactly
S3 = iv.sqrt(3)
n2, n1 = E2 - 1, 2 - 4 * E2
n0 = E2 * (4 + a * a) - a * a
_d = iv.sqrt(n1 * n1 - 4 * n2 * n0)
r_plus, r_minus = (-n1 - _d) / (2 * n2), (-n1 + _d) / (2 * n2)
p_plus, p_minus = C(2, a), C(2, -a)
ROOTS = [C(r_plus), C(r_minus), p_plus, p_minus]
ABSR = [abs(r_plus), abs(r_minus), iv.sqrt(4 + a * a), iv.sqrt(4 + a * a)]
p0 = n0 * (4 + a * a)                       # N(0) D(0) > 0
assert p0.a > 0
C0 = iv.sqrt(p0)
# geometry of the certificate
R_IN, R_OUT = R(105, 100), R(155, 100)
R0 = iv.sqrt(R_IN * R_OUT)
SIGMA = iv.log(R_OUT / R_IN) / 2
NNODE, KARC, NMAX = 128, 360, 260
RHO1 = R(170, 100)                          # majorant radius: R_OUT < RHO1 < min|root|
assert a.b < R_IN.a and RHO1.b < min(x.a for x in ABSR), "annulus must avoid the cross and the roots"

# ---- Taylor series of (N D / p0)^(-1/2) at 0, and U
# The coefficients are computed EXACTLY in rational arithmetic (a and E are rational) and only then enclosed.
# An interval version of this recurrence is useless: its widths grow like 1.4^n (wrapping), measured.
aF, E2F = A, Fraction(16, 25)
pNF = [E2F * (4 + aF * aF) - aF * aF, 2 - 4 * E2F, E2F - 1]
pDF = [4 + aF * aF, Fraction(-4), Fraction(1)]
prodF = [Fraction(0)] * 5
for i_, x_ in enumerate(pNF):
    for j_, y_ in enumerate(pDF):
        prodF[i_ + j_] += x_ * y_
qF = [c / prodF[0] for c in prodF]
sF = [Fraction(1)]
for m in range(1, NMAX + 1):
    acc = Fraction(0)
    for j in range(1, min(4, m) + 1):
        acc += qF[j] * (m - Fraction(j, 2)) * sF[m - j]
    sF.append(-acc / m)
s = [R(x.numerator, x.denominator) for x in sF]
UC = [s[n] / (n + 1) for n in range(NMAX + 1)]          # U = (z / C0) * sum UC[n] z^n
theta_ = R_OUT / RHO1
Shat = iv.mpf(1)
for x_ in ABSR:
    Shat *= 1 / iv.sqrt(1 - RHO1 / x_)
U_TAIL = (Shat / C0 * R_OUT * theta_ ** (NMAX + 1) / (1 - theta_)).b
TB = iv.mpf([-U_TAIL, U_TAIL])


def Uf(z):
    """Enclosure of U on the box z. Horner is used only at the box's midpoint: on a box with both parts non-zero,
    interval Horner gains (|x| + |y|)/min|root| > 1 per step and diverges (measured). The rest of the box is
    covered by the mean-value bound |U(z) - U(zm)| <= sup_box |U'| * |z - zm|, with U' = 1/sqrt(N D)."""
    zm = C(z.re.mid, z.im.mid)
    acc = C(UC[NMAX])
    for n in range(NMAX - 1, -1, -1):
        acc = acc * zm + UC[n]
    u = acc * zm / C0
    rad = iv.sqrt((z.re.delta / 2) ** 2 + (z.im.delta / 2) ** 2)
    r = (iv.mpf(sqND(z).inv().absub()) * rad).b + U_TAIL
    rb = iv.mpf([-r, r])
    return C(u.re + rb, u.im + rb)


def sqND(z):
    v = C(C0)
    for r in ROOTS:
        v = v * csqrt(1 - z / r)
    return v


def Nf(z):
    return z.sq() * n2 + z * n1 + n0


def Df(z):
    return (z - 2).sq() + a * a


def integrand(z):
    """-> (f_plus, f_minus), f = dq * sqrt(N D) * exp(+-2 kappa U)."""
    Nz, Dz, Dl = Nf(z), Df(z), z.sq() - 2 * z + a * a
    dN, dD = z * (2 * n2) + n1, 2 * (z - 2)
    L = dN / Nz - dD / Dz
    den = Dz * Nz
    g = Dl * (-4 * a) / den
    dden = dD * Nz + Dz * dN
    dg = ((2 * z - 2) * den - Dl * dden) * (-4 * a) / den.sq()
    u = z / a
    w = u.sq()
    Lg = clog((u * S3 - 1) / (u * S3 + 1))
    acot = clog((u + I1) / (u - I1)) / C(0, 2)
    l3 = clog((w + 1) / (w - R(1, 3)))
    Iu = (w + 1).inv() * R(5, 4) - u * acot * R(3, 8) - u * Lg * (3 * S3 / 16) - l3 * R(3, 16)
    R1 = acot * R(3, 8) + Lg * (3 * S3 / 16) + u * R(5, 2) / (w + 1).sq()
    c1, dc1 = Iu / (5 * a), -R1 / (5 * a * a)
    if PLANT:        # must-fail control: c1 := 1 makes the integrand holomorphic in the disc, so I+- = 0 exactly
        c1, dc1 = C(1), C(0)
    dq = L * (dg * c1 + g * dc1) * R(3, 8)
    base = dq * sqND(z)
    e = cexp(Uf(z) * (2 * kappa))
    return base * e, base / e


def sup_on(fun, lo, hi, depth=0):
    """Upper bound of fun on [lo, hi] (fun maps an interval to a list of nonnegative upper bounds)."""
    try:
        return fun(iv.mpf([lo, hi]))
    except NotRHP:
        if depth > 8:
            raise
        mid = (lo + hi) / 2
        x, y = sup_on(fun, lo, mid, depth + 1), sup_on(fun, mid, hi, depth + 1)
        return [max(p, q_) for p, q_ in zip(x, y)]


def periodic_integral(node_fun, bound_fun, sigma, nnode, karc, nout):
    """Enclosures of int_0^{2 pi} h_i for the nout components of node_fun, with the trapezoid error bound."""
    tot = [C(0) for _ in range(nout)]
    for j in range(nnode):
        vals = node_fun(2 * iv.pi * j / nnode)
        tot = [t + v for t, v in zip(tot, vals)]
    tot = [t * (2 * iv.pi / nnode) for t in tot]
    M = [0.0] * nout
    for j in range(karc):
        lo, hi = (2 * iv.pi * j / karc).a, (2 * iv.pi * (j + 1) / karc).b
        b = sup_on(bound_fun, lo, hi)
        M = [max(x, y) for x, y in zip(M, b)]
    err = [(4 * iv.pi * iv.mpf(m) / (iv.exp(sigma * nnode) - 1)).b for m in M]
    out = []
    for t, e in zip(tot, err):
        eb = iv.mpf([-e, e])
        out.append(C(t.re + eb, t.im + eb))
    return out, M, err


def main():
    if PLANT:
        print("PLANTED CONTROL: c1 := 1 (integrand holomorphic in the disc; the true I+ and I- are 0). "
              "The I+- certificate MUST fail.")
    print(f"spin a = {A}, E = 4/5; annulus [1.05, 1.55], R0 = {fl(R0.a):.6f}, sigma = {fl(SIGMA.a):.6f}; "
          f"{NNODE} nodes, {KARC} boundary boxes per line")
    print(f"  r+ in {iv_s(r_plus)}; min|root| >= {fl(min(x.a for x in ABSR)):.6f}; U series to z^{NMAX}, "
          f"tail <= {fl(U_TAIL):.2e}")

    # ---------------- I_plus, I_minus
    def node(th):
        z = C(R0 * iv.cos(th), R0 * iv.sin(th))
        fp, fm = integrand(z)
        return [fp * I1 * z, fm * I1 * z]

    def bound(thbox):
        out = [0.0, 0.0]
        for rad in (R_IN, R_OUT):
            z = C(rad * iv.cos(thbox), rad * iv.sin(thbox))
            fp, fm = integrand(z)
            out = [max(out[0], (fp * z).absub()), max(out[1], (fm * z).absub())]
        return out
    (Ip, Im), M, err = periodic_integral(node, bound, SIGMA, NNODE, KARC, 2)
    print(f"  bounds on the annulus boundary: M+ = {fl(M[0]):.3e}, M- = {fl(M[1]):.3e}; "
          f"trapezoid errors <= {fl(err[0]):.1e}, {fl(err[1]):.1e}")
    print(f"  Im I+ in {iv_s(Ip.im)}   Re I+ in {iv_s(Ip.re)}")
    print(f"  Im I- in {iv_s(Im.im)}   Re I- in {iv_s(Im.re)}")
    okp = Ip.im.a > 0 or Ip.im.b < 0
    okm = Im.im.a > 0 or Im.im.b < 0

    # ---------------- omega: kappa*omega = -+ 2 a exp(-i pi/4) J,  J = int_0^pi F dphi = (1/2) int_0^{2 pi} F
    cmid = (C(r_plus) + p_plus) / 2
    dhalf = (p_plus - C(r_plus)) / 2
    SIG2 = R(1, 2)

    def Fphi(phi):                          # phi is a C box
        ey = iv.exp(phi.im)
        ch, sh = (ey + 1 / ey) / 2, (ey - 1 / ey) / 2
        cosphi = C(iv.cos(phi.re) * ch, -iv.sin(phi.re) * sh)
        z = cmid - dhalf * cosphi
        return 1 / (csqrt(z - r_minus) * csqrt((z - p_minus) * C(0, -1)))

    def node2(th):
        return [Fphi(C(th, 0))]

    def bound2(thbox):
        return [max(Fphi(C(thbox, SIG2)).absub(), Fphi(C(thbox, -SIG2)).absub())]
    (J2,), M2, err2 = periodic_integral(node2, bound2, SIG2, NNODE, KARC, 1)
    J = J2 / 2
    # Re(kappa omega) = -+ sqrt2 * a * (Re J + Im J)
    rk = iv.sqrt(2) * a * (J.re + J.im)
    ik = iv.sqrt(2) * a * (J.im - J.re)
    print(f"  J in {iv_s(J.re)} + i {iv_s(J.im)}; bound M = {fl(M2[0]):.3e}, trapezoid error <= {fl(err2[0]):.1e}")
    print(f"  Re(kappa omega) = -+ {iv_s(rk)};  Im(kappa omega) = -+ {iv_s(ik)}  (one overall branch sign)")
    okw = rk.a > 0 or rk.b < 0
    verdict = okp and okm and okw
    print(f"VERDICT spin {A}: Im I+ != 0: {okp}; Im I- != 0: {okm}; Re(kappa omega) != 0: {okw}  ->  "
          f"{'c2 != 0 CERTIFIED (interval arithmetic)' if verdict else 'NOT CERTIFIED'}   [{time.time() - t0:.0f} s]")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
