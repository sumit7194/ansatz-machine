#!/usr/bin/env python3
"""C2-L (data/nve/route1_check/C2_L_REGISTRATION.md with erratum E1): a redrawn lasso with CERTIFIED clearance.
For the P2 segment (region B, spin 3/5) and its rho = 4 k-box K, cut into k-cells (v2's kbox cells, each refined into
quadrants when a certificate fails, down to MAXLEV levels):
  sweep     Krawczyk enclosures, per k-cell, of r+ (the zero of G1 on the real axis) and p+, p- (the zeros of G2): a box
            with exactly one zero for EVERY k in the cell. s(.) = max over the cells of |box - point(k_c)| (upper bound).
  L'        the floats lasso's tail from bB, then the boundary of the convex hull of D(r+, rho_r) and D(p+, rho_p),
            traversed counter-clockwise (L's orientation), then back. rho_p = s(p+) + 1.5 c;
            rho_r = the midpoint of [s(r+) + c, d(r+, p-) - s(p-) - c]. An empty window refuses before anything runs.
  c-tube    every box of the closed c-tube about L' (c = 0.03), x every k-cell: G1 G2 != 0, B != 0, z^2 + a^2 != 0.
  homotopy  L and L' resampled to matched vertices (L's and L''s own vertices kept, so both curves are unchanged), by
            angle about an interior point; each patch of the piecewise-linear homotopy lies in the convex hull of its 4
            corners, which is covered by boxes, x every k-cell: the same four nonzero tests.
c0 and c0' on a z-box x a k-cell (CellField): a Taylor model in k about the cell's centre kc, from C0's own walk at the
POINT kc with deriv=True (the carried branch, unchanged), plus a certified bound on the second k-derivative (see the
class); then a second-order Taylor in z over the box with the exact c0''(midpoint) and sup |c0'''| over a square
containing it. f0, f0' by centred forms. (A walk with k a BALL was tried first and is not used: Arb's series recurrence
over-estimates exponentially with a ball parameter, and its integrator cannot meet a tolerance; both gave vacuous
enclosures, about 1e16.) Every certificate is Arb ball arithmetic.
Stages: design (items 1-2 only; writes c2/c2l_P2_design.json, an empty window is the registered refusal) and certify.
    BOX=P2 <P2's R1_* env> .venv313/bin/python -I -u scripts/_nve_c2l.py design|certify
"""
import cmath
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _nve_route1_segment_v7B as L         # noqa: E402
import _nve_v7_c0 as V7                     # noqa: E402
from flint import acb, arb, ctx             # noqa: E402

ctx.prec = 256
V = L.V
A, E2 = V.A, V.E2
REF = L.S6.REF
KC, HALF = L.S6.KC, L.S6.HALF
CLEAR = arb(3) / 100                         # c = 0.03 (registered)
MAXLEV = 3                                   # k-cell refinement: R/5 -> R/10 -> R/20 -> R/40
ROOT = os.path.dirname(HERE)
OUTD = os.path.join(ROOT, "data", "nve", "route1_check", "c2")
R = (HALF * (arb(4) + arb(1) / 4) / 2).upper()
LAS = list(L.LAS)
BB = LAS[0]


def kcells():
    _K, subs = V.kbox(acb(KC), R)
    out = []
    for d in subs:
        b = acb(KC) + d
        c = acb(b.real.mid(), b.imag.mid())
        h = arb(max(b.real.rad(), b.imag.rad())).upper()
        out.append((c, h))
    return out


def quarter(c, h):
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            q = c + acb(sx * h / 2, sy * h / 2)
            qc = acb(q.real.mid(), q.imag.mid())
            err = max((q.real - qc.real).abs_upper(), (q.imag - qc.imag).abs_upper())
            out.append((qc, (h / 2 + err).upper()))
    return out


class CellField:
    """c0, c0' over z-boxes for every k in one k-cell (centre c, half-side h; h = 0 means the point k = c).
    For a k-BALL the values are a Taylor model in k about the centre, so the k-dependence keeps its correlation:
        c(z, k) in c(z, kc) + c_k(z, kc) dk + U Q(z) |dk|^2 / 2,
    with c and c_k from C0's own walk at the POINT kc (deriv=True: the carried branch, unchanged), and Q a bound on
    |c_kk| over the straight segment from the base point BB to z for every k in the ball:
        |c0_kk(z)|  <= E0 + E1 l + Mkk l^2 / 2,   |c0'_kk(z)| <= E1 + Mkk l,   l = |z - BB|,
    E0, E1 bounding |c0_kk|, |c0'_kk| at BB (an enclosed rectangle rule on s-balls of the start integrals'
    k-derivative, d^2 sqrt P/dk^2 = -(1/4) P_k^2 P^(-3/2)), and Mkk = sup |c0_kk''| = sup |pref (dB/dk)^2 /
    (4 B^(3/2) (z^2 + a^2)^3)| over the working square x the ball (a box cover; B != 0 there is certified). c_kk is
    single-valued on the square (convex, free of c0's singular points for every k), so the straight segment's bound
    holds whatever path the point walk took. (A direct walk with a ball k was tried first: Arb's series recurrence then
    over-estimates exponentially, and the start integrator cannot meet its tolerance; both gave vacuous enclosures.)"""

    def __init__(self, c, h):
        self.kc, self.h = c, h
        self.kb = c + acb(arb(0, h), arb(0, h)) if h > 0 else c
        if not L.free_square(self.kb, L.RREQ):            # c0 has no singular point in the working square for ANY k
            raise RuntimeError("cell field: the working square is not certified free of c0's singular points")
        sq = L.Z0 + acb(arb(0, L.RREQ), arb(0, L.RREQ))
        if not (sq.real.contains(arb(BB.real)) and sq.imag.contains(arb(BB.imag))):
            raise RuntimeError("cell field: the base point is not in the working square")
        self.c0 = V7.C0(V.SPIN, self.kb)                   # for sup_box only (branch-free) over the ball
        self.cp = V7.C0(V.SPIN, c, deriv=h > 0)            # the point walk at the centre
        self.cache = {BB: self.cp.start(acb(BB))}
        if h > 0:
            self.E0, self.E1 = self._base_kk()
            self.Mkk = self._sup_kk()
            dk = self.kb - c
            self.dk = dk
            self.d2 = (dk.abs_upper() ** 2 / 2).upper()

    def _base_kk(self, sm=256):
        a = V.A
        k8 = (arb(8) / 5).sqrt() * a
        zs = acb(BB)
        L_ = (1 / zs).real
        cc2, cc1, cc0 = self.c0.c2, self.c0.c1, self.c0.c0
        e1, e0 = arb(0), arb(0)
        for i in range(sm):
            sb = acb(L_ * (2 * i + 1) / (2 * sm) + arb(0, L_ / (2 * sm)))
            a2s2 = a * a * sb * sb
            P = cc2 + cc1 * a2s2 + cc0 * a2s2 * a2s2
            P1 = -21 + 18 * a2s2 - a2s2 * a2s2
            if not (P.real > 0):
                raise RuntimeError("cell field: Re P not certified positive on the k-ball at the base")
            g = (P1.abs_upper() ** 2 / 4 / P.abs_lower() ** (arb(3) / 2) / ((1 + a2s2) ** 3).abs_lower()).upper()
            e1 += ((sb * sb).abs_upper() * g * L_ / sm).upper()
            e0 += ((sb - zs * sb * sb).abs_upper() * g * L_ / sm).upper()
        return (k8 * e0).upper(), (k8 * e1).upper()

    def _sup_kk(self, m=16, depth=4):
        C = self.c0
        r = arb(L.RREQ)

        def bound(cx, cy, hw, d):
            bx = acb(L.Z0) + acb(arb(cx, hw), arb(cy, hw))
            Bb = C.B_mv(bx)
            Db = bx * bx + C.a * C.a
            if not (Bb.contains(0) or Db.contains(0)):
                return (C.pref.abs_upper() * C.dB(bx).abs_upper() ** 2 / 4 / Bb.abs_lower() ** (arb(3) / 2)
                        / Db.abs_lower() ** 3).upper()
            if d == 0:
                raise RuntimeError("cell field: c0_kk'' not bounded on the working square")
            h2 = (hw / 2).upper()
            return max(bound(cx + sx * h2, cy + sy * h2, h2, d - 1) for sx in (-1, 1) for sy in (-1, 1))
        hw = (r / m).upper()
        M = arb(0)
        for i in range(m):
            for j in range(m):
                cx = (-r + hw * (2 * i + 1)).mid()
                cy = (-r + hw * (2 * j + 1)).mid()
                M = max(M, bound(arb(cx), arb(cy), hw, depth))
        return M.upper()

    def _point(self, z):
        if z not in self.cache:
            assert abs(z - complex(float(L.Z0.mid()))) < float(L.RREQ) - 1e-9, "cell field: point outside the square"
            near = min(self.cache, key=lambda q: abs(q - z))
            self.cache[z] = self.cp.walk([acb(near.real, near.imag), acb(z.real, z.imag)], self.cache[near])[-1]
        return self.cache[z]

    def at(self, z):
        """the state at the exact point z for every k in the cell"""
        st = self._point(z)
        if self.h == 0:
            return st
        l = (acb(z) - acb(BB)).abs_upper()
        Q0 = (self.E0 + self.E1 * l + self.Mkk * l * l / 2).upper()
        Q1 = (self.E1 + self.Mkk * l).upper()
        U = acb(arb(0, 1), arb(0, 1))
        return dict(c0=st["c0"] + st["D0"] * self.dk + (Q0 * self.d2).upper() * U,
                    c0p=st["c0p"] + st["D1"] * self.dk + (Q1 * self.d2).upper() * U)

    def c0pp(self, z):
        """c0''(z) for every k in the cell, at the exact point z: pref s_c sqrt(B_K / B_c) / (z^2 + a^2)^3, with s_c the
        point walk's carried root at kc and the PRINCIPAL root of the ratio, certified in the right half-plane (the
        ratio is 1 at kc and B is linear in k, so over the convex ball it stays off the cut and the principal root is
        the continuation of the carried branch)"""
        s_c = self._point(z)["s"]
        za = acb(z)
        D3 = (za * za + V.A * V.A) ** 3
        if self.h == 0:
            return self.cp.pref * s_c / D3
        q = self.c0.B(za) / self.cp.B(za)
        if not (q.real > 0):
            raise RuntimeError("cell field: B_K / B_c not certified in the right half-plane")
        return self.c0.pref * s_c * q.sqrt() / D3

    def sup3(self, z, r, m=4, depth=3):
        """sup |c0 third derivative| over the square z + [-r, r]^2 for every k:
        |pref| (|B_z| / (2 |B|^(1/2) |D|^3) + 6 |x| |B|^(1/2) / |D|^4), branch-free"""
        C = self.c0

        def bound(cx, cy, hw, d):
            bx = z + acb(arb(cx, hw), arb(cy, hw))
            Bb = C.B_mv(bx)
            Db = bx * bx + C.a * C.a
            if not (Bb.contains(0) or Db.contains(0)):
                w = bx * bx / (C.a * C.a)
                Bz = (2 * bx / (C.a * C.a)) * (2 * C.c2 * w + C.c1)
                return (C.pref.abs_upper() * (Bz.abs_upper() / (2 * Bb.abs_lower().sqrt() * Db.abs_lower() ** 3)
                        + 6 * bx.abs_upper() * Bb.abs_upper().sqrt() / Db.abs_lower() ** 4)).upper()
            if d == 0:
                raise AssertionError("sup3: a singular point of c0 is within the box")
            h2 = (hw / 2).upper()
            return max(bound(cx + sx * h2, cy + sy * h2, h2, d - 1) for sx in (-1, 1) for sy in (-1, 1))
        hw = (arb(r) / m).upper()
        M = arb(0)
        for i in range(m):
            for j in range(m):
                cx = (-arb(r) + hw * (2 * i + 1)).mid()
                cy = (-arb(r) + hw * (2 * j + 1)).mid()
                M = max(M, bound(arb(cx), arb(cy), hw, depth))
        return M.upper()

    def box(self, Zb):
        """c0, c0' over the box Zb for every k: second-order Taylor about the box's (float) midpoint zm with the exact
        c0''(zm) and M3 = sup |c0'''| over the square zm +- r (which contains Zb, hence every segment zm -> x in Zb):
        c0 in c0(zm) + c0'(zm) dz + c0''(zm) dz^2 / 2 + U M3 d^3 / 6,  c0' in c0'(zm) + c0''(zm) dz + U M3 d^2 / 2"""
        zm = complex(Zb.mid())
        zm = complex(float(zm.real), float(zm.imag))
        st = self.at(zm)
        r = max(float(Zb.real.rad()), float(Zb.imag.rad())) * 1.0000001 + abs(complex(Zb.mid()) - zm)
        M3 = self.sup3(acb(zm.real, zm.imag), arb(r))
        f2 = self.c0pp(zm)
        dz = Zb - acb(zm.real, zm.imag)
        d = dz.abs_upper()
        U = acb(arb(0, 1), arb(0, 1))
        return (st["c0"] + st["c0p"] * dz + f2 * dz * dz / 2 + (M3 * d * d * d / 6).upper() * U,
                st["c0p"] + f2 * dz + (M3 * d * d / 2).upper() * U)


def f0s(Zb):
    """f0 = 1 - 2z/(z^2 + a^2) and f0' = 2(z^2 - a^2)/(z^2 + a^2)^2 over the box Zb by centred forms about its
    midpoint m (f0'' = 4z(3a^2 - z^2)/(z^2 + a^2)^3 over the box; the integral remainders lie in the convex box
    enclosure): f0 in f0(m) + f0'(m) dz + f0''(Zb) dz^2 / 2, f0' in f0'(m) + f0''(Zb) dz. Naive ball evaluation of the
    rational functions over-estimates enough to stop Krawczyk contracting."""
    D = Zb * Zb + A * A
    m = acb(Zb.real.mid(), Zb.imag.mid())
    Dm = m * m + A * A
    f0m = (m * m - 2 * m + A * A) / Dm
    f0pm = 2 * (m * m - A * A) / (Dm * Dm)
    f0pp = 4 * Zb * (3 * A * A - Zb * Zb) / (D * D * D)
    dz = Zb - m
    return f0m + f0pm * dz + f0pp * dz * dz / 2, f0pm + f0pp * dz, D


def Gs(Zb, cf):
    c0, c0p = cf.box(Zb)
    f0, f0p, D = f0s(Zb)
    G2 = f0 * f0 + c0 * c0
    dG2 = 2 * (f0 * f0p + c0 * c0p)
    G1 = E2 * G2 - f0
    dG1 = E2 * dG2 - f0p
    return G1, dG1, G2, dG2, D


def nonsingular(Zb, cf):
    """certified: G1 != 0, G2 != 0, B != 0, z^2 + a^2 != 0 on the box Zb x the cell"""
    D = Zb * Zb + A * A
    if D.contains(0):
        return False
    K = cf.kb
    w = Zb * Zb / (A * A)
    zm = acb(Zb.real.mid(), Zb.imag.mid())
    wm = zm * zm / (A * A)
    Bm = (90 - 21 * K) * wm * wm - (60 - 18 * K) * wm + (10 - K)
    dB = (2 * Zb / (A * A)) * (2 * (90 - 21 * K) * w - (60 - 18 * K))
    if (Bm + dB * (Zb - zm)).contains(0):
        return False
    try:
        G1, _d1, G2, _d2, _D = Gs(Zb, cf)
    except AssertionError:
        return False
    return not (G1.contains(0) or G2.contains(0))


def cover_ok(cx, cy, hw, cf, depth=5):
    """the closed square [cx +- hw] x [cy +- hw] certified nonsingular for the cell, splitting up to `depth` times"""
    Zb = acb(arb(cx, hw), arb(cy, hw))
    if nonsingular(Zb, cf):
        return True
    if depth == 0:
        return False
    h2 = (arb(hw) / 2).upper()
    return all(cover_ok(cx + sx * float(h2), cy + sy * float(h2), h2, cf, depth - 1) for sx in (-1, 1) for sy in (-1, 1))


def krawczyk(z0, rad, which, cf, it=6):
    """a box with exactly one zero of G1 (which=1) or G2 (which=2) for EVERY k in the cell, or None"""
    Z = acb(arb(z0.real, rad), arb(z0.imag, rad))
    proven = False
    for _ in range(it):
        m = acb(Z.real.mid(), Z.imag.mid())
        G1m, _a, G2m, _b, _D = Gs(m, cf)
        _G1, dG1, _G2, dG2, _D2 = Gs(Z, cf)
        g, dgZ = (G1m, dG1) if which == 1 else (G2m, dG2)
        _G1m, dG1m, _G2m, dG2m, _Dm = Gs(acb(m.real.mid(), m.imag.mid()), cf)
        Y = 1 / acb((dG1m if which == 1 else dG2m).mid())
        Kz = m - Y * g + (1 - Y * dgZ) * (Z - m)
        inside = (Kz.real.lower() > Z.real.lower() and Kz.real.upper() < Z.real.upper()
                  and Kz.imag.lower() > Z.imag.lower() and Kz.imag.upper() < Z.imag.upper())
        if inside:
            proven = True
        elif not proven:
            return None
        # once K(Z) lies in the interior of Z (existence and uniqueness in Z, for every k in the cell), the later
        # iterations only tighten: Z := Z meet K(Z), which still holds the zero. (Requiring strict inclusion again
        # fails at the fixed point, whose width is the zero's own sweep over the cell.)
        lo_r, hi_r = max(Kz.real.lower(), Z.real.lower()), min(Kz.real.upper(), Z.real.upper())
        lo_i, hi_i = max(Kz.imag.lower(), Z.imag.lower()), min(Kz.imag.upper(), Z.imag.upper())
        Z = acb(arb((lo_r + hi_r) / 2, ((hi_r - lo_r) / 2).upper()), arb((lo_i + hi_i) / 2, ((hi_i - lo_i) / 2).upper()))
        Z = acb(arb(Z.real.mid(), (Z.real.rad() * (1 + arb(2) ** -40)).upper() + arb(2) ** -200),
                arb(Z.imag.mid(), (Z.imag.rad() * (1 + arb(2) ** -40)).upper() + arb(2) ** -200))
    return Z


# ------------------------------------------------------------------------------------------------ geometry
def zeros_at_kc():
    """r+ (G1's zero), p+ and p- (G2's zeros) at k_c, by the floats entry's exact point strings (labelled by |G|)"""
    pts = [acb(arb(p[0]).mid(), arb(p[1]).mid()) for p in REF["points"]]
    cf = CellField(acb(arb(KC).mid()), arb(0))
    out = {}
    for z in pts:
        G1, _a, G2, _b, _D = Gs(z, cf)
        zc = complex(z.mid())
        if G1.abs_upper() < arb("1e-20"):
            out["r+"] = zc
        elif G2.abs_upper() < arb("1e-20"):
            out["p+" if zc.imag > 0 else "p-"] = zc
    assert set(out) == {"r+", "p+", "p-"}, f"zeros at k_c: {out}"
    return out


def winding(poly, z):
    w = 0.0
    for a, b in zip(poly[:-1], poly[1:]):
        r = (b - z) / (a - z)
        w += math.atan2(r.imag, r.real)
    return round(w / (2 * math.pi))


def hull_loop(r0, rr, p0, rp, n=96):
    """the boundary of conv(D(r0, rr) u D(p0, rp)) as a counter-clockwise polygon, starting at its leftmost vertex
    (exact doubles); the polygon is inscribed in the arcs, and it is THE curve that is certified (not the arcs)"""
    pts = []
    for j in range(n):
        t = 2 * math.pi * j / n
        for c, r in ((r0, rr), (p0, rp)):
            pts.append(c + r * cmath.exp(1j * t))
    pts = sorted(set((round(p.real, 15), round(p.imag, 15)) for p in pts))
    pts = [complex(x, y) for x, y in pts]

    def cross(o, a, b):
        return (a.real - o.real) * (b.imag - o.imag) - (a.imag - o.imag) * (b.real - o.real)
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]                       # counter-clockwise, starting at the leftmost point
    return [complex(float(z.real), float(z.imag)) for z in hull]


def ray_hit(poly, O, th, closed=True):
    """the point where the ray from O at angle th meets the polygon (star-shaped about O: unique), or None"""
    d = cmath.exp(1j * th)
    best = None
    edges = list(zip(poly, poly[1:] + poly[:1])) if closed else list(zip(poly[:-1], poly[1:]))
    for a, b in edges:
        m00, m01, m10, m11 = d.real, -(b - a).real, d.imag, -(b - a).imag
        det = m00 * m11 - m01 * m10
        if abs(det) < 1e-300:
            continue
        rx, ry = (a - O).real, (a - O).imag
        t = (rx * m11 - m01 * ry) / det
        u = (m00 * ry - rx * m10) / det
        if t > 0 and -1e-12 <= u <= 1 + 1e-12:
            p = a + (b - a) * min(1.0, max(0.0, u))
            if best is None or abs(p - O) > abs(best - O):
                best = p
    return None if best is None else complex(float(best.real), float(best.imag))


def new_lasso(hull, O):
    """L' = bB -> J -> the hull counter-clockwise -> J' -> bB, where J and J' are the hull's crossings of the rays from O
    through L's own junction vertices L[1] and L[-2] (so the radial homotopy below is continuous at both tails)"""
    ta, tb = cmath.phase(LAS[1] - O), cmath.phase(LAS[-2] - O)
    J, Jp = ray_hit(hull, O, ta), ray_hit(hull, O, tb)
    assert J is not None and Jp is not None
    # the hull's vertices strictly between angle ta and the angle tb reached by turning counter-clockwise from ta
    span = (tb - ta) % (2 * math.pi) or 2 * math.pi
    inner = sorted((((cmath.phase(v - O) - ta) % (2 * math.pi)), v) for v in hull)
    inner = [v for a, v in inner if 1e-12 < a < span - 1e-12]
    return [BB, J] + inner + [Jp, BB]


def densify(poly, h):
    out = [poly[0]]
    for a, b in zip(poly[:-1], poly[1:]):
        m = max(1, math.ceil(abs(b - a) / h))
        for i in range(1, m + 1):
            p = a + (b - a) * i / m
            out.append(complex(float(p.real), float(p.imag)))
    return out


def sweeps(cells):
    """per k-cell Krawczyk boxes for r+, p+, p-, refining a cell into quarters where Krawczyk fails (down to MAXLEV
    levels); -> (zeros at k_c, radii s(.), boxes per leaf cell, the leaf cells) or raises"""
    z0 = zeros_at_kc()
    s = {k: arb(0) for k in z0}
    boxes = {}
    todo = [(c, h, 0) for c, h in cells]
    leaves = []
    while todo:
        c, h, lev = todo.pop(0)
        try:
            bx = _sweep_cell(c, h, z0)
        except RuntimeError:
            if lev >= MAXLEV:
                raise
            todo += [(qc, qh, lev + 1) for qc, qh in quarter(c, h)]
            continue
        leaves.append((c, h))
        boxes[complex(c.mid())] = bx
        for nm, Z in bx.items():
            s[nm] = V.amax((s[nm], (Z - acb(z0[nm].real, z0[nm].imag)).abs_upper()))
    return z0, s, boxes, leaves


def _sweep_cell(c, h, z0):
    try:
        return _sweep_cell_inner(c, h, z0)
    except AssertionError as e:                            # C0's branch or singular-point guards: refine the cell
        raise RuntimeError(f"sweep: a C0 guard refused on the k-cell at {complex(c.mid())}: {e}")


def _sweep_cell_inner(c, h, z0):
    if True:
        cf = CellField(c, h)
        cp = CellField(c, arb(0))                          # the point k = the cell's centre, for the Newton guess
        bx = {}
        for nm, zc in z0.items():
            z = zc
            for _ in range(30):                            # float Newton at the cell's centre k (a guess only)
                G1, dG1, G2, dG2, _D = Gs(acb(z.real, z.imag), cp)
                g, dg = (G1, dG1) if nm == "r+" else (G2, dG2)
                dz = complex(g.mid()) / complex(dg.mid())
                z = complex(float((z - dz).real), float((z - dz).imag))
                if abs(dz) < 1e-14:
                    break
            Z = None
            for rad in (0.005, 0.01, 0.02, 0.04):
                Z = krawczyk(z, rad, 1 if nm == "r+" else 2, cf)
                if Z is not None:
                    break
            if Z is None:
                raise RuntimeError(f"sweep: Krawczyk failed for {nm} on the k-cell at {complex(c.mid())}")
            bx[nm] = Z
        return bx


class DesignRefused(RuntimeError):
    """the registered rule: an empty window means there is no L' for the box, refused before any CAPD run"""

    def __init__(self, why, rec):
        super().__init__(why)
        self.rec = rec


def design(cells):
    z0, s, boxes, leaves = sweeps(cells)
    c = CLEAR
    d_rp = (acb(z0["r+"].real, z0["r+"].imag) - acb(z0["p-"].real, z0["p-"].imag)).abs_lower()
    lo, hi = (s["r+"] + c).upper(), (d_rp - s["p-"] - c).lower()
    if not lo < hi:
        raise DesignRefused(f"the rho_r window [{float(lo):.4f}, {float(hi):.4f}] is empty",
                            dict(zeros={k: [v.real, v.imag] for k, v in z0.items()},
                                 sweep={k: float(v) for k, v in s.items()}, d_rplus_pminus=float(d_rp),
                                 window=[float(lo), float(hi)], sweep_cells=len(leaves),
                                 sweep_levels=sorted({round(float(h), 6) for _c, h in leaves})))
    rho_r = float(((lo + hi) / 2).mid())
    rho_p = float((s["p+"] + c + c / 2).upper())
    hull = hull_loop(z0["r+"], rho_r, z0["p+"], rho_p)
    Lp = new_lasso(hull, (z0["r+"] + z0["p+"]) / 2)
    w = {nm: winding(Lp, z) for nm, z in z0.items()}
    wo = {nm: winding(LAS, z) for nm, z in z0.items()}
    rec = dict(zeros={k: [v.real, v.imag] for k, v in z0.items()}, sweep={k: float(v) for k, v in s.items()},
               d_rplus_pminus=float(d_rp), rho_r=rho_r, rho_p=rho_p, window=[float(lo), float(hi)],
               windings_new=w, windings_old=wo, n_vertices=len(Lp), sweep_cells=len(leaves))
    assert w == {"r+": 1, "p+": 1, "p-": 0} and w == wo, f"windings: new {w}, old {wo}"
    return Lp, rec


# ------------------------------------------------------------------------------------------------ certificates
def tube_ok(Lp, cf, h=None):
    """the closed c-tube about L' certified nonsingular for the cell. The tube lies inside the union of the discs of
    radius c + h/2 about the densified points (spacing h); each disc's bounding square is gridded into squares of side
    c/4, a square CERTIFIED disjoint from the disc (Arb distance from the centre point > c + h/2) is skipped, and every
    other square must pass cover_ok. -> (ok, where)"""
    h = h or float(CLEAR.mid()) / 2
    rad = (CLEAR + arb(h) / 2).upper()
    q = float((CLEAR / 8).upper())                          # half-side of the grid squares (side c/4)
    m = math.ceil(float(rad) / (2 * q))
    for p in densify(Lp, h):
        for i in range(-m, m):
            for j in range(-m, m):
                cx, cy = p.real + (2 * i + 1) * q, p.imag + (2 * j + 1) * q
                dx = (abs(arb(cx) - arb(p.real)) - arb(q))
                dy = (abs(arb(cy) - arb(p.imag)) - arb(q))
                dx = dx if dx > 0 else arb(0)
                dy = dy if dy > 0 else arb(0)
                if bool(dx * dx + dy * dy > rad * rad):        # certified: the square misses the disc
                    continue
                if not cover_ok(cx, cy, q * 1.0000001, cf):
                    return False, complex(cx, cy)
    return True, None


def _disjoint(cx, cy, hw, poly):
    """CERTIFIED: the square [cx +- hw] x [cy +- hw] does not meet the convex polygon `poly` (ccw), by an edge with all 4
    corners strictly outside, in Arb (the corners and the edge's endpoints are exact)"""
    cs = [(arb(cx) + sx * arb(hw), arb(cy) + sy * arb(hw)) for sx in (-1, 1) for sy in (-1, 1)]
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ax, ay, bx, by = arb(a.real), arb(a.imag), arb(b.real), arb(b.imag)
        if all(bool(((bx - ax) * (y - ay) - (by - ay) * (x - ax)) < 0) for x, y in cs):
            return True
    return False


def conv4(pts):
    pts = sorted(set((p.real, p.imag) for p in pts))
    pts = [complex(x, y) for x, y in pts]
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a.real - o.real) * (b.imag - o.imag) - (a.imag - o.imag) * (b.real - o.real)
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def region_ok(poly, cf, box=0.01, depth=4):
    """the convex polygon certified nonsingular for the cell: its bounding box is gridded; a grid cell certified
    DISJOINT from the polygon is skipped; any other must pass cover_ok"""
    xs, ys = [p.real for p in poly], [p.imag for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    nx = max(1, math.ceil((x1 - x0) / box))
    ny = max(1, math.ceil((y1 - y0) / box))
    hx, hy = (x1 - x0) / nx / 2, (y1 - y0) / ny / 2
    hw = max(hx, hy) * 1.0000001 + 1e-15
    for i in range(nx):
        for j in range(ny):
            cx, cy = x0 + (2 * i + 1) * hx, y0 + (2 * j + 1) * hy
            if len(poly) >= 3 and _disjoint(cx, cy, hw, poly):
                continue
            if not cover_ok(cx, cy, hw, cf, depth):
                return False, complex(cx, cy)
    return True, None


def matched(Lold, Lnew, O):
    """the RADIAL straight-line homotopy: both loop parts (L[1] .. L[-2] and L'[1] .. L'[-2]) are star-shaped about O,
    and their junctions lie on the same rays from O. Points are matched at the SAME angle, at the union of both curves'
    own vertex angles (each curve keeps all its vertices, so both are unchanged). Each swept segment then lies on a ray
    from O, between the two curves' radii, and never reaches a point inside both (r+ and p+)."""
    ta = cmath.phase(Lold[1] - O)
    span = (cmath.phase(Lold[-2] - O) - ta) % (2 * math.pi) or 2 * math.pi
    assert abs(cmath.phase(Lnew[1] - O) - ta) < 1e-9 and abs(cmath.phase(Lnew[-2] - O) - cmath.phase(Lold[-2] - O)) < 1e-9

    def rel(v):
        return (cmath.phase(v - O) - ta) % (2 * math.pi)
    angs = sorted(set([0.0, span] + [rel(v) for v in Lold[1:-1] + Lnew[1:-1] if 1e-12 < rel(v) < span - 1e-12]))
    Po, Pn = Lold[1:-1], Lnew[1:-1]
    mo = [ray_hit(Po, O, ta + a, closed=False) for a in angs]
    mn = [ray_hit(Pn, O, ta + a, closed=False) for a in angs]
    assert all(x is not None for x in mo + mn), "matching: a ray missed a loop part (not star-shaped about O?)"
    return mo, mn


def homotopy_ok(Lold, Lnew, cf):
    """the straight-line homotopy L -> L' certified free of singular points for the cell: the patches between matched
    points of the loop parts, and the tail triangle (bB, L's first loop vertex, L''s), each covered"""
    z0 = zeros_at_kc()
    O = (z0["r+"] + z0["p+"]) / 2
    mo, mn = matched(Lold, Lnew, O)
    n = len(mo)
    for i in range(n - 1):                               # the loop parts are open polylines (tail to tail)
        q = conv4([mo[i], mo[i + 1], mn[i + 1], mn[i]])
        ok, where = region_ok(q, cf)
        if not ok:
            return False, ("patch", i, where)
    for tri in (conv4([BB, Lold[1], Lnew[1]]), conv4([BB, Lold[-2], Lnew[-2]])):
        ok, where = region_ok(tri, cf)
        if not ok:
            return False, ("tail", where)
    return True, None


# ------------------------------------------------------------------------------------------------ the run
def _cell_job(args):
    c_re, c_im, h, Lp = args
    c = acb(arb(c_re), arb(c_im))
    t0 = time.time()
    try:
        cf = CellField(c, arb(h))
        ok1, w1 = tube_ok(Lp, cf)
        ok2, w2 = homotopy_ok(LAS, Lp, cf) if ok1 else (False, None)
    except (RuntimeError, AssertionError) as e:
        return dict(ok=False, why=f"exception: {e}", t=round(time.time() - t0, 1))
    return dict(ok=bool(ok1 and ok2), tube=bool(ok1), tube_where=str(w1), homotopy=bool(ok2), homotopy_where=str(w2),
                t=round(time.time() - t0, 1))


def certify():
    """items 2-4 over the whole K-box: sweeps -> L' -> the tube and homotopy certificates per k-cell (refined where a
    certificate fails, down to MAXLEV; a failure at MAXLEV STOPS). Writes the floats entry route1_floats_v7BL_3_5.json
    [k_c] with the new lasso and the certificate record. Two worker processes."""
    import hashlib
    from multiprocessing import get_context
    t0 = time.time()
    code = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]
    Lp, rec = design(kcells())
    print(f"C2-L design: sweeps {rec['sweep']} over {rec['sweep_cells']} cells; rho_r {rec['rho_r']:.4f}, "
          f"rho_p {rec['rho_p']:.4f}; windings {rec['windings_new']} [{time.time() - t0:.0f} s]", flush=True)
    todo = [(c, h, 0) for c, h in kcells()]
    cells, stop = [], None
    with get_context("fork").Pool(2) as pool:
        while todo and stop is None:
            batch, todo = todo, []
            args = [(c.real.mid().str(40), c.imag.mid().str(40), float(h), Lp) for c, h, _l in batch]
            for (c, h, lev), r in zip(batch, pool.map(_cell_job, args)):
                r.update(centre=[complex(c.mid()).real, complex(c.mid()).imag], h=float(h), level=lev)
                cells.append(r)
                print(f"  cell {complex(c.mid()):.6f} h {float(h):.2e}: {'ok' if r['ok'] else 'FAIL'} "
                      f"({r.get('tube_where') if not r.get('tube', True) else r.get('homotopy_where', r.get('why'))}) "
                      f"[{r['t']} s]", flush=True)
                if not r["ok"]:
                    if lev < MAXLEV:
                        todo += [(qc, qh, lev + 1) for qc, qh in quarter(c, h)]
                    else:
                        stop = f"cell {complex(c.mid())} (level {lev}) not certified"
    leaves = [c for c in cells if c["ok"]]
    out = dict(code=code, k_c=str(KC), half=str(HALF), c=float(CLEAR.mid()), design=rec, cells=cells, stop=stop,
               n_leaves=len(leaves), wall=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(OUTD, "c2l_P2_certify.json"), "w"), indent=1)
    print(f"C2-L certify: {'STOP: ' + stop if stop else 'CERTIFIED'}; {len(leaves)} leaf cells; "
          f"{out['wall']} s", flush=True)
    if stop:
        return
    entry = dict(REF)
    entry["lasso"] = [[repr(float(z.real)), repr(float(z.imag))] for z in Lp]
    entry["c2l"] = dict(code=code, design=rec, leaves=len(leaves), certify_file="c2/c2l_P2_certify.json")
    fn = os.path.join(ROOT, "data", "nve", "eps", "route1_floats_v7BL_3_5.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    res[str(os.environ["R1_KC"])] = entry
    json.dump(res, open(fn, "w"), indent=1, default=str)
    print(f"C2-L: the floats entry with L' is written to {fn}", flush=True)


def design_only():
    """the design stage alone (items 1-2): the certified sweeps and the radius windows; writes c2/c2l_P2_design.json.
    An empty window is the registered refusal, recorded as such."""
    import hashlib
    t0 = time.time()
    code = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]
    try:
        Lp, rec = design(kcells())
        verdict = "DESIGNED"
    except DesignRefused as e:
        rec, verdict = e.rec, f"REFUSED (registered rule, before any CAPD run): {e}"
    out = dict(code=code, k_c=str(KC), half=str(HALF), c=float(CLEAR.mid()), verdict=verdict, design=rec,
               wall=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(OUTD, "c2l_P2_design.json"), "w"), indent=1)
    print(f"C2-L design P2: {verdict}; sweeps {rec['sweep']}; window {rec['window']} [{out['wall']} s]", flush=True)


if __name__ == "__main__":
    {"certify": certify, "design": design_only}[sys.argv[1]]()
