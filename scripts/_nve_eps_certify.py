#!/usr/bin/env python3
"""An EXPLICIT epsilon for Statement A (data/nve/EPS_EFFECTIVE.md, Part A).
[model: Fable 5.2; UNVERIFIED until the office ansatz-machine checks it]

For one spin (NVE_SPIN), E = 4/5, this certifies in mpmath.iv a number r > 0 such that for every complex k with
0 < |k| <= r the pair M0(k) (circle |z| = R0) and M1(k) (the k = 0 capsule lasso, kept FIXED) satisfies
    (Z1) F = tr[M1, M0] - 2 != 0,   (Z2) tr M0 != 0 and tr M1 != 0,   (Z3) tr M1 not in [-2, 2].

The bound (derivation in EPS_EFFECTIVE.md):
  - exact identity, N = M0 - I:   F = tr(N^2) - tr(M1 N M1^-1 N);
  - in Kerr's basis M1(0) = -diag(m, 1/m), so F0 := tr(N^2) - tr(M1(0) N M1(0)^-1 N) = -4 sinh^2(kappa omega) n12 n21;
  - N = k X + E,  |E|_F <= C_E |k|^2   (first-order Dyson term with an explicit second-order remainder in the
    twist, plus the Dyson tail);
  - M1(k) = M1(0) Z1, |Z1 - I|_F <= eta = exp(c_L |k|) - 1 (crude Dyson bound along the lasso);
  - |F - c2 k^2| <= 4|sinh^2| ( |k|^3 sqrt(|x12|^2 + |x21|^2) C_E + C_E^2 |k|^4 ) + mu^2 eta (2 + eta) |N|_F^2.
Twist: c0 = c_K + k c1 + eps2 on |z| >= a nu0, with |eps2| <= A0 Phi |k|^2 / (8 (1 - |k| Phi)) from the binomial
series of sqrt(1 - k phi) along the radial ray (modulus majorants A0, A1, Phi, tabulated once).
q is expanded in (c0, c0') around Kerr with the remainder enclosed on interval boxes; a box on which G1 or G2 could
vanish raises, so a returned r also certifies that q(z; k) is holomorphic for |k| <= r on both loops.

    NVE_SPIN=3/5 EPS_R0=1.35 python scripts/_nve_eps_certify.py          (about 1-2 min, one core, < 300 MB)
Controls:  EPS_REFUSE=1 (c2 interval replaced by one containing 0: must print NO r).
"""
import bisect
from fractions import Fraction
import cmath
import json
import math
import os
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_c2_certify as CC                                      # noqa: E402  (spin from NVE_SPIN; iv.dps = 40)
from _nve_c2_certify import (A, C, C0, E2, I1, NotRHP, R, ROOTS, S3, Uf, a, cexp, clog, csqrt, fl, iv, iv_s,  # noqa: E402
                             kappa, n0, n1, n2, p_minus, p_plus, r_minus, r_plus, sqND)

t0 = time.time()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "nve", "eps")
R0S = os.environ.get("EPS_R0", {"3/10": "1.1492", "3/5": "1.35", "4/5": "1.3382", "9/10": "1.2639",
                                "227/250": "1.30"}.get(str(A), "1.30"))
_f = Fraction(R0S)
R0C = R(_f.numerator, _f.denominator)
REFUSE = os.environ.get("EPS_REFUSE", "") == "1"
DELTA = os.environ.get("EPS_DELTA", "")               # "" = registered capsule; "wide" or a number = alternative
TAG = os.environ.get("EPS_TAG", "")
KC_ARCS = int(os.environ.get("EPS_KC", "720"))        # boxes on the circle
H_L = float(os.environ.get("EPS_HL", "0.003"))        # piece length on the lasso
RREFS = [float(x) for x in os.environ.get("EPS_RREFS", "0.3,0.1,0.03,0.01,0.003,0.001,0.0003,0.0001,3e-5,1e-5,1e-6,1e-7").split(",")]
af = fl(a.mid)


def ub(x):
    return float(iv.mpf(x).b)


def lb(x):
    return float(iv.mpf(x).a)


# ------------------------------------------------------------------------------------------ Kerr data on a box
def kerr_rat(z):
    """Well-conditioned Kerr rational functions on a box: L = P_K'/P_K, g = -4 a Delta/(D N), gamma = Delta/N."""
    Nz, Dz = CC.Nf(z), CC.Df(z)
    Dl = z.sq() - 2 * z + a * a
    dN, dD, dDl = z * (2 * n2) + n1, 2 * (z - 2), 2 * z - 2
    den = Dz * Nz
    dden = dD * Nz + Dz * dN
    return dict(L=dN / Nz - dD / Dz, g=Dl * (-4 * a) / den, dg=(dDl * den - Dl * dden) * (-4 * a) / den.sq(),
                gam=Dl / Nz, dgam=(dDl * Nz - Dl * dN) / Nz.sq(), Dp=z.sq() + a * a, dDp=2 * z, iDm=Dz.inv(), dDm=dD)


def c1_fun(z):
    """c1 = d c0/dk at k = 0 and its z-derivative (closed form; needs |z| > a)."""
    u = z / a
    w = u.sq()
    Lg = clog((u * S3 - 1) / (u * S3 + 1))
    acot = clog((u + I1) / (u - I1)) / C(0, 2)
    l3 = clog((w + 1) / (w - R(1, 3)))
    Iu = (w + 1).inv() * R(5, 4) - u * acot * R(3, 8) - u * Lg * (3 * S3 / 16) - l3 * R(3, 16)
    R1 = acot * R(3, 8) + Lg * (3 * S3 / 16) + u * R(5, 2) / (w + 1).sq()
    return Iu / (5 * a), -R1 / (5 * a * a)


def dq_first(z):
    K = kerr_rat(z)
    c1, dc1 = c1_fun(z)
    return K["L"] * (K["dg"] * c1 + K["g"] * dc1) * R(3, 8), K, c1, dc1


# ------------------------------------------------------------------------------------------ radial majorants
def phibar(nu):
    x = nu * nu
    return (21 * x * x + 18 * x + 1) / (10 * (3 * x - 1) ** 2)       # >= |phi| on |u| = nu; decreasing in nu


def hmaj(nu):
    x = nu * nu
    return 4 * (3 * x + 1) / (a ** 3 * (x - 1) ** 3) * phibar(nu)     # >= |c_K''| |phi| on |u| = nu; decreasing


NUG = [1.2 * 1.004 ** j for j in range(1460)]                         # nu grid up to about 400
_V = iv.mpf(NUG[-1])
_ct = 4 * iv.mpf("3.002") * phibar(_V) / a ** 3                        # h <= _ct / nu^4 for nu >= V
T1 = [None] * len(NUG)
SS = [None] * len(NUG)
T1[-1] = _ct / (3 * _V ** 3)
SS[-1] = _ct / (6 * _V ** 2)
for j in range(len(NUG) - 2, -1, -1):
    d = iv.mpf(NUG[j + 1]) - iv.mpf(NUG[j])
    T1[j] = T1[j + 1] + hmaj(iv.mpf(NUG[j])) * d                      # left endpoint of a decreasing function
    SS[j] = SS[j + 1] + T1[j] * d
T1U = [ub(a * x) for x in T1]                                         # A1(nu0) = int |c_K''||phi| |ds| along the ray
S_U = [ub(a * a * x) for x in SS]                                     # A0(nu0) = int |s - z| |c_K''||phi| |ds|
PHU = [ub(phibar(iv.mpf(x))) for x in NUG]


def majorants(z):
    nu0 = lb(iv.sqrt(z.abs2()) / a)
    j = bisect.bisect_right(NUG, nu0) - 1
    if j < 0:
        raise NotRHP("path point with |z|/a below the majorant grid")
    return S_U[j], T1U[j], PHU[j]


# ------------------------------------------------------------------------------------------ per-box bounds
def box_bounds(z, r):
    """-> (|dq|_up, alpha, beta): for |k| <= r,  |Delta q| <= alpha |k|/r  and  |Delta q - k dq| <= beta (|k|/r)^2.
    Exact structure: with delta = c0 - c_K,  sigma = (-4 a delta + D+ delta^2)/D-,  s = sigma/(1 + sigma),
    P = P_K (1 + gamma s),  lambda = (gamma s)'/(1 + gamma s),  Delta q = (3/8) L lambda + (3/16) lambda^2.
    Everything below is a bound by moduli; sigma < 1/2 and |gamma s| < 1/2 certify G2 != 0 and P != 0 on the box."""
    dq, K, c1, dc1 = dq_first(z)
    A0, A1, PH = majorants(z)
    if r * PH >= 0.5:
        raise NotRHP("|k| phi >= 1/2 on the radial ray")
    fac = iv.mpf(PH) * r * r / (8 * (1 - iv.mpf(r) * PH))
    e0, e1 = iv.mpf(ub(A0 * fac)), iv.mpf(ub(A1 * fac))
    r0, r1 = r * iv.mpf(c1.absub()) + e0, r * iv.mpf(dc1.absub()) + e1          # |delta|, |delta'| at |k| = r
    m = {k_: iv.mpf(v.absub()) for k_, v in K.items()}
    sig = (4 * a * r0 + m["Dp"] * r0 ** 2) * m["iDm"]
    if not sig.b < 0.5:
        raise NotRHP("sigma >= 1/2: G2 could vanish")
    dsig = (4 * a * r1 + m["dDp"] * r0 ** 2 + 2 * m["Dp"] * r0 * r1) * m["iDm"] + sig * m["dDm"] * m["iDm"]
    s_, ds_ = sig / (1 - sig), dsig / (1 - sig) ** 2
    tau = m["gam"] * s_
    if not tau.b < 0.5:
        raise NotRHP("|gamma s| >= 1/2: P could vanish")
    dtau = m["dgam"] * s_ + m["gam"] * ds_
    th = m["Dp"] * r0 ** 2 * m["iDm"] + sig ** 2 / (1 - sig)
    dth = ((m["dDp"] * r0 ** 2 + 2 * m["Dp"] * r0 * r1) * m["iDm"] + m["Dp"] * r0 ** 2 * m["dDm"] * m["iDm"] ** 2
           + sig * dsig * (2 + sig) / (1 - sig) ** 2)
    lam = dtau / (1 - tau)
    beta = R(3, 8) * m["L"] * (m["dg"] * e0 + m["g"] * e1 + m["dgam"] * th + m["gam"] * dth + tau * dtau / (1 - tau)) \
        + R(3, 16) * lam ** 2
    alpha = R(3, 8) * m["L"] * lam + R(3, 16) * lam ** 2
    return ub(dq.absub()), ub(alpha), ub(beta), dq


def float_gate():
    """Floats only: the closed form Delta q = (3/8) L lambda + (3/16) lambda^2 against the definition of q."""
    import cmath as cm
    aa, e2 = af, 16 / 25
    worst = 0.0
    for zz, dl, ddl in ((1.2 + 0.5j, 0.03 - 0.02j, 0.01 + 0.04j), (1.9 + 0.75j, -0.02 + 0.01j, 0.03j)):
        def qdef(c, dc, z=zz):
            Dp = z * z + aa * aa
            f0, df0 = (z * z - 2 * z + aa * aa) / Dp, 2 * (z * z - aa * aa) / Dp ** 2
            G2, dG2 = f0 * f0 + c * c, 2 * (f0 * df0 + c * dc)
            G1, dG1 = e2 * G2 - f0, e2 * dG2 - df0
            return 3 / 16 * (dG1 / G1 - dG2 / G2) ** 2
        Dp, dDp = zz * zz + aa * aa, 2 * zz
        cK, dcK = -2 * aa / Dp, 4 * aa * zz / Dp ** 2
        Dm, dDm = (zz - 2) ** 2 + aa * aa, 2 * (zz - 2)
        Nn = (e2 - 1) * zz * zz + (2 - 4 * e2) * zz + e2 * (4 + aa * aa) - aa * aa
        dN = 2 * (e2 - 1) * zz + (2 - 4 * e2)
        Dl, dDl = zz * zz - 2 * zz + aa * aa, 2 * zz - 2
        L = dN / Nn - dDm / Dm
        gam, dgam = Dl / Nn, (dDl * Nn - Dl * dN) / Nn ** 2
        sg = (-4 * aa * dl + Dp * dl * dl) / Dm
        dsg = (-4 * aa * ddl + dDp * dl * dl + 2 * Dp * dl * ddl) / Dm - sg * dDm / Dm
        s_, ds_ = sg / (1 + sg), dsg / (1 + sg) ** 2
        lam = (dgam * s_ + gam * ds_) / (1 + gam * s_)
        lhs = qdef(cK + dl, dcK + ddl) - qdef(cK, dcK)
        rhs = 3 / 8 * L * lam + 3 / 16 * lam * lam
        worst = max(worst, abs(lhs - rhs) / abs(lhs))
    return worst


def circle_boxes():
    out = []
    for j in range(KC_ARCS):
        th = iv.mpf([(2 * iv.pi * j / KC_ARCS).a, (2 * iv.pi * (j + 1) / KC_ARCS).b])
        z = C(R0C * iv.cos(th), R0C * iv.sin(th))
        ln = ub(R0C * 2 * iv.pi / KC_ARCS)
        out.append(dict(z=z, len=ln, sq=sqND(z).absub(), reU=Uf(z).re))
    return out


def capsule_polygon():
    """The registered lasso at k = 0: _nve_lower_kc.capsule_lasso(r+, p+, [r-, p-], b = R0), in floats. Any fixed
    polygon is a legitimate loop; this one is the engine's k = 0 lasso to float accuracy."""
    rp, rm = complex(fl(r_plus.mid)), complex(fl(r_minus.mid))
    pp, pm = complex(2, af), complex(2, -af)
    b = complex(fl(R0C.mid))

    def seg_dist(c, A_, B_):
        ab = B_ - A_
        t = max(0.0, min(1.0, ((c - A_) * ab.conjugate()).real / abs(ab) ** 2))
        return abs(A_ + t * ab - c)
    clear = min(seg_dist(c, rp, pp) for c in (rm, pm))
    delta = min(0.15, 0.4 * clear)                       # the registered rule
    if DELTA:
        delta = float(DELTA) if DELTA != "wide" else 0.4 * clear     # a wider representative of the same class
    e = (pp - rp) / abs(pp - rp)
    th = cmath.phase(e)
    npts = 24
    cap = [pp + delta * cmath.exp(1j * (th - math.pi / 2 + math.pi * j / npts)) for j in range(npts + 1)]
    cap += [rp + delta * cmath.exp(1j * (th + math.pi / 2 + math.pi * j / npts)) for j in range(npts + 1)]
    i0 = min(range(len(cap)), key=lambda i: abs(cap[i] - b))
    ring = cap[i0:] + cap[:i0] + [cap[i0]]
    return [b] + ring + [b], delta


def lasso_boxes():
    """Pieces of the lasso with enclosures of sqrt(N D) (continuous branch, tracked) and of U (interval Euler)."""
    poly, delta = capsule_polygon()
    pieces = []
    for P0, P1 in zip(poly[:-1], poly[1:]):
        n = max(1, int(math.ceil(abs(P1 - P0) / H_L)))
        for i in range(n):
            pieces.append((P0 + (P1 - P0) * i / n, P0 + (P1 - P0) * (i + 1) / n))
    rootsf = [complex(fl(r.re.mid), fl(r.im.mid)) for r in ROOTS]
    b = poly[0]
    theta = [cmath.phase(1 - b / rf) for rf in rootsf]
    th0 = list(theta)
    U = Uf(C(iv.mpf(b.real), iv.mpf(b.imag)))
    U0 = U
    out = []
    for z0, z1 in pieces:
        zb = C(iv.mpf([min(z0.real, z1.real), max(z0.real, z1.real)]), iv.mpf([min(z0.imag, z1.imag), max(z0.imag, z1.imag)]))
        zm = (z0 + z1) / 2
        s = C(C0)
        for i, (rt, rf) in enumerate(zip(ROOTS, rootsf)):
            ang = cmath.phase(1 - zm / rf)
            ang += 2 * math.pi * round((theta[i] - ang) / (2 * math.pi))
            assert abs(ang - theta[i]) < 0.5, "branch tracking step too large"
            theta[i] = ang
            t = iv.mpf(ang)
            rot_m = C(iv.cos(t), -iv.sin(t))
            rot_h = C(iv.cos(t / 2), iv.sin(t / 2))
            s = s * rot_h * csqrt((1 - zb / rt) * rot_m)
        g = s.inv()
        dz = C(iv.mpf(z1.real) - iv.mpf(z0.real), iv.mpf(z1.imag) - iv.mpf(z0.imag))
        step = dz * g
        hull = C(U.re + step.re * iv.mpf([0, 1]), U.im + step.im * iv.mpf([0, 1]))
        out.append(dict(z=zb, len=ub(iv.sqrt(dz.abs2())), sq=s.absub(), reU=hull.re))
        U = U + step
    wind = [(t1 - t0_) / (2 * math.pi) for t1, t0_ in zip(theta, th0)]
    return out, delta, U - U0, wind, len(poly)


# ------------------------------------------------------------------------------------------ k = 0 certificates
def first_order_certificate():
    """Enclosures of I+, I-, I0 = closed integral of dq * sqrt(N D) * {exp(2 kappa U), exp(-2 kappa U), 1} dz."""
    def three(z):
        base = dq_first(z)[0] * sqND(z)
        e = cexp(Uf(z) * (2 * kappa))
        return base * e, base / e, base

    def node(th):
        z = C(CC.R0 * iv.cos(th), CC.R0 * iv.sin(th))
        return [f * I1 * z for f in three(z)]

    def bound(thbox):
        out = [0.0, 0.0, 0.0]
        for rad in (CC.R_IN, CC.R_OUT):
            z = C(rad * iv.cos(thbox), rad * iv.sin(thbox))
            out = [max(o, (f * z).absub()) for o, f in zip(out, three(z))]
        return out
    (Ip, Im, I0), M, err = CC.periodic_integral(node, bound, CC.SIGMA, CC.NNODE, CC.KARC, 3)
    return Ip, Im, I0, (M, err)


def omega_certificate():
    """w = 2 a exp(-i pi/4) J, with kappa*omega = -+ w (as in _nve_c2_certify.main)."""
    cmid = (C(r_plus) + p_plus) / 2
    dhalf = (p_plus - C(r_plus)) / 2
    SIG2 = R(1, 2)

    def Fphi(phi):
        ey = iv.exp(phi.im)
        ch, sh = (ey + 1 / ey) / 2, (ey - 1 / ey) / 2
        z = cmid - dhalf * C(iv.cos(phi.re) * ch, -iv.sin(phi.re) * sh)
        return 1 / (csqrt(z - r_minus) * csqrt((z - p_minus) * C(0, -1)))
    (J2,), _M, _e = CC.periodic_integral(lambda th: [Fphi(C(th, 0))],
                                         lambda tb: [max(Fphi(C(tb, SIG2)).absub(), Fphi(C(tb, -SIG2)).absub())],
                                         SIG2, CC.NNODE, CC.KARC, 1)
    rt = iv.sqrt(2) / 2
    return (J2 / 2) * C(rt, -rt) * (2 * a)


# ------------------------------------------------------------------------------------------ assembly
def assemble(cst, t, variant=None):
    """-> (ok, parts) for |k| = t <= r_ref, with every quantity an upper bound except c2lo."""
    v = variant or {}
    cL = cst["cL"] * v.get("cL", 1.0)
    CE = cst["CE"] * v.get("CE", 1.0)
    mu2 = cst["mu2"] * v.get("mu2", 1.0)
    T = iv.mpf(t)
    eta = iv.exp(cL * T) - 1
    nuN = T * cst["nX"] + CE * T * T
    circ = 4 * cst["S2"] * (T ** 3 * cst["xoff"] * CE + CE ** 2 * T ** 4)
    # |tr(M D M^-1 N)| with M = diag(m, 1/m): entry (1,2) of D is weighted by |m|^2 and pairs with n21, entry (2,1)
    # by |m|^-2 and pairs with n12 (roles swapped if |m| < 1). Cauchy-Schwarz over the four entries.
    big, small = (cst["a21"], cst["a12"]) if cst["m_gt_1"] else (cst["a12"], cst["a21"])
    e2 = CE * T * T
    wN = iv.sqrt(2 * (T * cst["a11"] + e2) ** 2 + mu2 ** 2 * (T * big + e2) ** 2 + (T * small + e2) ** 2 / mu2 ** 2)
    lass = eta * (2 + eta) * nuN * wN
    lhs = cst["c2lo"] * T * T
    z1 = lhs.a > (circ + lass).b
    z2 = (math.sqrt(2) * nuN).b < 2
    z3 = (cst["nM1"] * eta).b < cst["imtr"]
    return bool(z1 and z2 and z3), dict(lhs=lb(lhs), circ=ub(circ), lass=ub(lass), eta=ub(eta), nuN=ub(nuN),
                                        z1=bool(z1), z2=bool(z2), z3=bool(z3))


def largest_t(cst, rref, variant=None):
    if not assemble(cst, rref * 1e-12, variant)[0]:
        return 0.0
    if assemble(cst, rref, variant)[0]:
        return rref
    lo, hi = rref * 1e-12, rref
    for _ in range(60):
        mid = math.sqrt(lo * hi)
        if assemble(cst, mid, variant)[0]:
            lo = mid
        else:
            hi = mid
    return lo


def main():
    os.makedirs(OUT, exist_ok=True)
    print(f"spin a = {A}, E = 4/5, circle R0 = {R0S}; {KC_ARCS} circle boxes, lasso piece length {H_L}"
          + ("   [MUST-REFUSE CONTROL: c2 interval replaced by one containing 0]" if REFUSE else ""))
    gate = float_gate()
    print(f"  float gate, closed form of Delta q against the definition: relative error {gate:.1e}")
    assert gate < 1e-10
    Ip, Im, I0, err = first_order_certificate()
    w = omega_certificate()
    x12, x21, x11 = -Im / (2 * kappa), Ip / (2 * kappa), -I0 / (2 * kappa)
    e2w = cexp(w * 2)
    sinh2 = (e2w + e2w.inv() - 2) / 4                       # sinh^2(w) = (cosh 2w - 1)/2
    c2 = -sinh2 * x12 * x21 * 4
    ew = cexp(w)
    trM1 = -(ew + ew.inv())
    mu = math.exp(max(abs(lb(w.re)), abs(ub(w.re))))
    print(f"  first-order certificate: boundary bounds M = {[f'{fl(m):.3e}' for m in err[0]]}, trapezoid errors <= "
          f"{[f'{fl(e_):.1e}' for e_ in err[1]]}   [{time.time() - t0:.0f} s]")
    print(f"  X (Kerr basis): x11 = {iv_s(x11.re)} + i {iv_s(x11.im)}")
    print(f"                  x12 = {iv_s(x12.re)} + i {iv_s(x12.im)}")
    print(f"                  x21 = {iv_s(x21.re)} + i {iv_s(x21.im)}")
    print(f"  kappa*omega = -+({iv_s(w.re)} + i {iv_s(w.im)});  tr M1(0) = {iv_s(trM1.re)} + i {iv_s(trM1.im)}")
    print(f"  c2 = {iv_s(c2.re)} + i {iv_s(c2.im)}")
    def mig(x):                                              # smallest |value| in a real interval
        return 0.0 if lb(x) <= 0 <= ub(x) else min(abs(lb(x)), abs(ub(x)))
    c2lo = lb(iv.sqrt(iv.mpf(mig(c2.re)) ** 2 + iv.mpf(mig(c2.im)) ** 2))
    if REFUSE:
        c2lo = 0.0
    imtr = mig(trM1.im)
    S2 = sinh2.absub()
    nM1 = math.sqrt(mu ** 2 + 1) * 1.0000001                 # |M1(0)|_F = sqrt(|m|^2 + |m|^-2) <= sqrt(mu^2 + 1)
    print(f"  |c2| >= {c2lo:.6e};  |sinh^2| <= {fl(S2):.6f};  mu^2 = exp(2|Re kappa omega|) <= {mu ** 2:.4f};  "
          f"|Im tr M1(0)| >= {imtr:.4f}")

    cb = circle_boxes()
    lbx, delta, dU, wind, nv = lasso_boxes()
    kw = dU * kappa
    print(f"  lasso: {nv - 1} edges, capsule radius {delta:.4f}, {len(lbx)} pieces, length {sum(b['len'] for b in lbx):.4f}; "
          f"winding numbers about r+, r-, p+, p-: {', '.join(f'{x:+.6f}' for x in wind)}")
    print(f"         kappa * (U increment around the lasso) in {iv_s(kw.re)} + i {iv_s(kw.im)}  (must contain +- kappa*omega)")
    ok_w = all(abs(abs(wind[i]) - 1) < 1e-2 for i in (0, 2)) and all(abs(wind[i]) < 1e-2 for i in (1, 3))
    sgn = 1 if abs(fl(kw.re.mid) - fl(w.re.mid)) < abs(fl(kw.re.mid) + fl(w.re.mid)) else -1
    m_gt_1 = bool(kw.re.a > 0)
    if not (kw.re.a > 0 or kw.re.b < 0):
        print("  cannot decide the sign of Re(kappa omega) along the lasso"); return 1
    ok_u = (kw.re - sgn * w.re).a <= 0 <= (kw.re - sgn * w.re).b and (kw.im - sgn * w.im).a <= 0 <= (kw.im - sgn * w.im).b
    print(f"         homotopy checks: winding (1, 0, 1, 0) {ok_w}; U increment consistent with omega {ok_u}")
    # the free basis scaling v+- -> exp(-+ kappa u0) v+-: choose u0 from a few candidates
    reU_all = [fl(b["reU"].mid) for b in cb + lbx]
    u0s = [round(-1.5 + 0.1 * j, 1) for j in range(31)]
    best = None
    rows = []
    allc = []
    for rref in RREFS:
        try:
            for bx in cb + lbx:
                bx["dq"], bx["alpha"], bx["beta"], _ = box_bounds(bx["z"], rref)
        except NotRHP as e:
            rows.append(dict(rref=rref, domain=False, why=str(e)))
            print(f"  r_ref = {rref:g}: holomorphy boxes FAILED ({e})", flush=True)
            continue
        for u0 in u0s:
            def psi(bx):
                d = (bx["reU"] - u0) * (2 * kappa)
                return ub(iv.mpf(bx["sq"]) * iv.mpf(max(math.cosh(lb(d)), math.cosh(ub(d))) * 1.0000001) / kappa)
            lC = sum(b["len"] * b["alpha"] * psi(b) for b in cb) * 1.0000001
            eC = sum(b["len"] * b["beta"] * psi(b) for b in cb) * 1.0000001
            lL = sum(b["len"] * b["alpha"] * psi(b) for b in lbx) * 1.0000001
            if lC > 50:                       # exp(lC) is astronomically large: this r_ref is useless, not wrong
                rows.append(dict(rref=rref, u0=u0, domain=True, t=0.0, lC=lC, eC=eC, lL=lL, note="ell_C > 50"))
                continue
            CE = ub((iv.mpf(eC) + iv.mpf(lC) ** 2 * iv.exp(iv.mpf(lC)) / 2) / iv.mpf(rref) ** 2)
            sc = iv.exp(2 * kappa * u0)
            a12, a21 = iv.mpf(x12.absub()) * sc, iv.mpf(x21.absub()) / sc
            nX = ub(iv.sqrt(2 * iv.mpf(x11.absub()) ** 2 + a12 ** 2 + a21 ** 2))
            xoff = ub(iv.sqrt(a12 ** 2 + a21 ** 2))
            cst = dict(cL=lL / rref, CE=CE, nX=nX, xoff=xoff, S2=ub(S2), mu2=mu ** 2 * 1.0000001, c2lo=c2lo,
                       nM1=nM1, imtr=imtr, lC=lC, eC=eC, lL=lL, rref=rref, u0=u0, a11=ub(x11.absub()),
                       a12=ub(a12), a21=ub(a21), m_gt_1=m_gt_1)
            allc.append(cst)
            t = largest_t(cst, rref)
            rows.append(dict(rref=rref, u0=u0, domain=True, t=t, cL=cst["cL"], CE=CE, nX=nX, lC=lC, eC=eC, lL=lL))
            if best is None or t > best[0]:
                best = (t, cst)
        rr = max((r_ for r_ in rows if r_["rref"] == rref and r_.get("domain")), key=lambda r_: r_["t"])
        print(f"  r_ref = {rref:g}: holomorphy boxes ok on C and L; best certified t = {rr['t']:.4e}  "
              f"(ell_C = {rr['lC']:.3e}, eps_C = {rr['eC']:.3e}, ell_L = {rr['lL']:.3e}, u0 = {rr['u0']:.3f})   "
              f"[{time.time() - t0:.0f} s]", flush=True)
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    if best is None or best[0] <= 0:
        why = "c2 interval contains 0 (|c2| lower bound is 0), so (Z1) cannot be certified at any r" if c2lo == 0 \
            else "no r_ref passed the holomorphy boxes or the inequality"
        print(f"VERDICT spin {A}: NO r  ({why})   [{time.time() - t0:.0f} s, peak {peak:.0f} MB]")
        json.dump(dict(spin=str(A), R0=R0S, r=None, why=why, rows=rows, refuse=REFUSE),
                  open(os.path.join(OUT, f"eps_{str(A).replace('/', '_')}{TAG}{'_REFUSE' if REFUSE else ''}.json"), "w"), indent=1)
        return 0 if REFUSE else 1
    t, cst = best
    ok, parts = assemble(cst, t)
    print(f"  |m| > 1 in the basis (v+, v-): {cst['m_gt_1']};  |x11|, |x12|, |x21| after scaling: "
          f"{cst['a11']:.5f}, {cst['a12']:.5f}, {cst['a21']:.5f}")
    print(f"  constants at the best choice (r_ref = {cst['rref']:g}, u0 = {cst['u0']:.4f}): c_L = {cst['cL']:.4e}, "
          f"C_E = {cst['CE']:.4e}, |X|_F <= {cst['nX']:.5f}, ell_C/r = {cst['lC'] / cst['rref']:.4e}")
    print(f"  at |k| = r: |c2| r^2 >= {parts['lhs']:.4e};  circle remainder <= {parts['circ']:.4e};  "
          f"lasso remainder <= {parts['lass']:.4e};  eta <= {parts['eta']:.4e};  Z1 {parts['z1']} Z2 {parts['z2']} Z3 {parts['z3']}")
    sens = {}
    for name, var in (("lasso term 10x better (c_L/10)", dict(cL=0.1)), ("circle term 10x better (C_E/10)", dict(CE=0.1)),
                      ("no conjugation loss (mu^2 -> 1)", dict(mu2=1.0 / cst["mu2"])),
                      ("both 10x better", dict(cL=0.1, CE=0.1))):
        sens[name] = max(largest_t(c_, c_["rref"], var) for c_ in allc)
    print("  sensitivity (hypothetical, NOT certified): " + "; ".join(f"{k_}: r = {v_:.3e}" for k_, v_ in sens.items()))
    print(f"  bound on |F - c2 k^2| at |k| = r: {parts['circ'] + parts['lass']:.6e}")
    print(f"VERDICT spin {A}: Statement A holds with epsilon = r = {t:.6e}  (Z1, Z2, Z3 for all 0 < |k| <= r; "
          f"interval arithmetic)   [{time.time() - t0:.0f} s, peak {peak:.0f} MB]")
    json.dump(dict(spin=str(A), R0=R0S, r=t, constants={k_: v_ for k_, v_ in cst.items()}, parts=parts, sensitivity=sens,
                   rows=rows, c2=[lb(c2.re), ub(c2.re), lb(c2.im), ub(c2.im)], refuse=REFUSE),
              open(os.path.join(OUT, f"eps_{str(A).replace('/', '_')}{TAG}.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
