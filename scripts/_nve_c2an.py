#!/usr/bin/env python3
"""C2-AN item 1 (data/nve/route1_check/C2_AN_REGISTRATION.md): the circle-picture LOOP CHAIN on real k, spin 3/5.
Certifies that route (i)'s words (M0 = the 96-gon |z| = R0 = 1.35, M1 = the per-k_c capsule lasso) define ONE
real-analytic family on J = [2.895, 4.005]; it certifies NO monodromy value.
For each link i (k_c = 59/20 + i/10, i = 0..10; J_i = [k_c - 0.055, k_c + 0.055]) and each real k-cell (width 0.01,
halved on failure down to MAXLEV levels):
  (a) circle   every edge of the 96-gon covered by boxes certified nonsingular for every k in the cell, with c0
               continued ALONG the polygon from R0 (PathField);
  (b) lasso    every edge of L_i likewise, with c0 from the square field (SquareField: the convex square 2 +- 1.15(1+i),
               certified free of c0's singular points for every k in the cell, so c0 is single-valued there);
  (c) start    Re P > 0 on s in [0, 1/R0] for every k in the cell (B > 0 on [R0, +inf)): the normalisation from +inf is
               analytic in k on the cell (checked inside the fields' base-point bound);
  (d) gluing   on the overlap O_i = [k_c,i + 0.045, k_c,i + 0.055]: the straight-line homotopy L_i -> L_{i+1} (vertex i to
               vertex i; both lassos have the same vertex count, asserted) sweeps the union of the quadrilaterals
               conv(L_i[j], L_i[j+1], L_{i+1}[j+1], L_{i+1}[j]); each is covered by boxes certified nonsingular.
  (e) diagnostics: the float clearance of the lasso from r+ and p+ at the cell centre (not gated; loop placement only).
  (f) closed lifts (hostile-read point 1): the circle's, by every c0 branch point (B's zeros, +-ia) certified inside
      |z| < R0 for every k in the cell (closed_lift_circle); each lasso's, because it lies in the square where c0 is
      single-valued (SquareField's freedom certificate), every box asserted inside the square.
  Based homotopy of the PAIR (point 2): both words are based at R0 = the normalisation point b (b = R0 in the circle
  picture; c0 is normalised from +inf along [R0, +inf)); the circle is common; the lasso homotopy fixes R0 (vertex 0).
"Nonsingular" on a box x a k-cell: G1 = E^2 (f0^2 + c0^2) - f0, G2 = f0^2 + c0^2, B(z^2/a^2, k), z^2 + a^2 all nonzero.
c0, c0' on a box: a Taylor model in k about the cell centre (C0's point walk with deriv=True, the carried branch) with a
certified bound on |c0_kk| (path length from R0 x sup |c0_kk''| over the path's boxes, or over the square), then a
second-order Taylor model in z with the exact c0'' and sup |c0'''| (as in _nve_c2l.py). f0 by centred forms.
Controls (registration): K1 (a lasso vertex moved onto p+), K1c (the circle of radius a through +-ia), K2 (a lasso
swapped for its complex conjugate on the gluing): each must refuse.
    NVE_SPIN=3/5 R1_R0=1.35 .venv313/bin/python -I -u scripts/_nve_c2an.py run|K1|K1c|K2|K3
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _nve_route1_segment_v2 as V            # noqa: E402  (constants A, E2, SPIN, the circle polygon; runs nothing)
import _nve_v7_c0 as V7                        # noqa: E402
from flint import acb, arb, ctx                # noqa: E402

ctx.prec = 256
assert V.SPIN == "3/5" and os.environ.get("R1_R0", "1.35") == "1.35"
A, E2 = V.A, V.E2
ROOT = os.path.dirname(HERE)
OUTD = os.path.join(ROOT, "data", "nve", "route1_check", "c2")
FLOATS = os.path.join(ROOT, "data", "nve", "eps", "route1_floats_an_3_5.json")
LINKS = ["59/20", "61/20", "63/20", "13/4", "67/20", "69/20", "71/20", "73/20", "15/4", "77/20", "79/20"]
HALFJ, CELLW, OV0, OV1 = arb("0.055"), arb("0.01"), arb("0.045"), arb("0.055")
SQ_C, SQ_R = 2.0, 1.15
MAXLEV = 3
R0 = complex(1.35, 0.0)                         # the binary double route (i) used (circle_vertices()[0] = lasso[0])
U = acb(arb(0, 1), arb(0, 1))
PIECE = 0.01                                    # boxes along an edge: pieces of at most this length


def frac(s):
    n, _, d = s.partition("/")
    return arb(int(n)) / int(d or 1)


# ------------------------------------------------------------------------------------------------ the k-cell model
class KModel:
    """the k-ball (a REAL ball c +- h) and the Taylor-model pieces common to both fields"""

    def __init__(self, c, h):
        self.kc, self.h = c, h                   # c: exact arb (a dyadic point); h: arb >= 0
        self.kb = acb(c + arb(0, 1) * h) if h > 0 else acb(c)
        self.cb = V7.C0(V.SPIN, self.kb)         # for B, sup bounds over the ball (branch-free)
        self.cp = V7.C0(V.SPIN, acb(c), deriv=h > 0)
        self.dk = self.kb - acb(c)
        self.d2 = (self.dk.abs_upper() ** 2 / 2).upper()
        if h > 0:
            self.E0, self.E1 = self._base_kk(acb(R0))

    def _base_kk(self, zs, sm=256):
        """|c0_kk|, |c0'_kk| at the real base point over the ball (rectangle rule on s-balls; Re P > 0 certified on
        [0, 1/zs], which is (c): B > 0 on [zs, +inf) for every k in the ball)"""
        a = A
        k8 = (arb(8) / 5).sqrt() * a
        L_ = (1 / zs).real
        C = self.cb
        e1, e0 = arb(0), arb(0)
        for i in range(sm):
            sb = acb(L_ * (2 * i + 1) / (2 * sm) + arb(0, L_ / (2 * sm)))
            a2s2 = a * a * sb * sb
            P = C.c2 + C.c1 * a2s2 + C.c0 * a2s2 * a2s2
            P1 = -21 + 18 * a2s2 - a2s2 * a2s2
            if not (P.real > 0):
                raise RuntimeError("(c): Re P not certified positive on [0, 1/R0] for the k-cell")
            g = (P1.abs_upper() ** 2 / 4 / P.abs_lower() ** (arb(3) / 2) / ((1 + a2s2) ** 3).abs_lower()).upper()
            e1 += ((sb * sb).abs_upper() * g * L_ / sm).upper()
            e0 += ((sb - zs * sb * sb).abs_upper() * g * L_ / sm).upper()
        return (k8 * e0).upper(), (k8 * e1).upper()

    def kk_sup(self, bx):
        """sup |c0_kk''| over the box bx x the ball = |pref| |dB/dk|^2 / (4 |B|^(3/2) |D|^3), or None"""
        C = self.cb
        Bb = C.B_mv(bx)
        Db = bx * bx + C.a * C.a
        if Bb.contains(0) or Db.contains(0):
            return None
        return (C.pref.abs_upper() * C.dB(bx).abs_upper() ** 2 / 4 / Bb.abs_lower() ** (arb(3) / 2)
                / Db.abs_lower() ** 3).upper()

    def compose(self, st, l, Mkk):
        """c0, c0' for every k in the ball at the point of state st (point walk at kc), path length l from R0"""
        if self.h == 0:
            return st["c0"], st["c0p"]
        Q0 = (self.E0 + self.E1 * l + Mkk * l * l / 2).upper()
        Q1 = (self.E1 + Mkk * l).upper()
        return (st["c0"] + st["D0"] * self.dk + (Q0 * self.d2).upper() * U,
                st["c0p"] + st["D1"] * self.dk + (Q1 * self.d2).upper() * U)

    def c0pp(self, z, s_c):
        za = acb(z)
        D3 = (za * za + A * A) ** 3
        if self.h == 0:
            return self.cp.pref * s_c / D3
        q = self.cb.B(za) / self.cp.B(za)
        if not (q.real > 0):
            raise RuntimeError("B_K / B_c not certified in the right half-plane")
        return self.cb.pref * s_c * q.sqrt() / D3

    def sup3(self, z, r, m=4, depth=3):
        C = self.cb

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

    def taylor_box(self, Zb, zm, c0m, c0pm, s_c):
        """c0, c0' over the box Zb from the values at its float midpoint zm (second order, exact c0'', sup |c0'''|)"""
        r = max(float(Zb.real.rad()), float(Zb.imag.rad())) * 1.0000001 + abs(complex(Zb.mid()) - zm)
        M3 = self.sup3(acb(zm.real, zm.imag), arb(r))
        f2 = self.c0pp(zm, s_c)
        dz = Zb - acb(zm.real, zm.imag)
        d = dz.abs_upper()
        return (c0m + c0pm * dz + f2 * dz * dz / 2 + (M3 * d * d * d / 6).upper() * U,
                c0pm + f2 * dz + (M3 * d * d / 2).upper() * U)


# ------------------------------------------------------------------------------------------------ the two fields
class PathField:
    """c0 continued along a closed polygon from R0 (the circle): states at every vertex by C0's walk along the polygon,
    and at points ON an edge by a walk along that edge from its first vertex; the k-remainder uses the path length"""

    def __init__(self, km, poly):
        self.km, self.poly = km, poly
        assert poly[0] == R0
        st = km.cp.start(acb(R0))
        self.vst, self.arc = [st], [0.0]
        for v0, v1 in zip(poly[:-1], poly[1:]):
            st = km.cp.walk([acb(v0.real, v0.imag), acb(v1.real, v1.imag)], st)[-1]
            self.vst.append(st)
            self.arc.append(self.arc[-1] + abs(v1 - v0))
        self.Mkk = None
        if km.h > 0:                             # sup |c0_kk''| over boxes covering every edge (the walked path)
            M = arb(0)
            for v0, v1 in zip(poly[:-1], poly[1:]):
                n = max(1, int(abs(v1 - v0) / PIECE) + 1)
                for j in range(n):
                    a, b = v0 + (v1 - v0) * j / n, v0 + (v1 - v0) * (j + 1) / n
                    m, hw = (a + b) / 2, abs(b - a) / 2 * 1.0001 + 1e-12
                    s = km.kk_sup(acb(arb(m.real, hw), arb(m.imag, hw)))
                    if s is None:
                        raise RuntimeError("PathField: c0_kk'' not bounded on the path (a singular point of c0 nearby)")
                    M = max(M, s)
            self.Mkk = M.upper()
        self.cache = {}

    def box(self, Zb, edge, t):
        """c0, c0' over the box Zb, which contains the point poly[edge] + t (poly[edge+1] - poly[edge])"""
        v0, v1 = self.poly[edge], self.poly[edge + 1]
        zm = v0 + (v1 - v0) * t
        zm = complex(float(zm.real), float(zm.imag))
        key = (edge, zm)
        if key not in self.cache:
            st = self.km.cp.walk([acb(v0.real, v0.imag), acb(zm.real, zm.imag)], self.vst[edge])[-1] if t > 0 \
                else self.vst[edge]
            l = arb(self.arc[edge] + abs(zm - v0)) * (1 + arb(2) ** -40)
            c0m, c0pm = self.km.compose(st, l, self.Mkk or arb(0))
            self.cache[key] = (c0m, c0pm, st["s"])
        c0m, c0pm, s_c = self.cache[key]
        return self.km.taylor_box(Zb, zm, c0m, c0pm, s_c)


class SquareField:
    """c0 on the convex square SQ_C +- SQ_R (1 + i), certified free of c0's singular points for every k in the ball,
    so c0 is single-valued there; states by straight walks from the nearest cached point (C2-L's CellField)"""

    def __init__(self, km):
        self.km = km
        self.Mkk = self._free_and_sup()
        self.cache = {R0: km.cp.start(acb(R0))}

    def _free_and_sup(self, m=16, depth=4):
        km = self.km
        r = arb(SQ_R)

        def bound(cx, cy, hw, d):
            bx = acb(SQ_C) + acb(arb(cx, hw), arb(cy, hw))
            s = km.kk_sup(bx)
            if s is not None:
                return s
            if d == 0:
                raise RuntimeError("SquareField: the square is not certified free of c0's singular points")
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
            assert abs(z.real - SQ_C) < SQ_R - 1e-9 and abs(z.imag) < SQ_R - 1e-9, "SquareField: outside the square"
            near = min(self.cache, key=lambda q: abs(q - z))
            self.cache[z] = self.km.cp.walk([acb(near.real, near.imag), acb(z.real, z.imag)], self.cache[near])[-1]
        return self.cache[z]

    def box(self, Zb, edge=None, t=None):
        zm = complex(Zb.mid())
        zm = complex(float(zm.real), float(zm.imag))
        st = self._point(zm)
        l = (acb(zm) - acb(R0)).abs_upper()
        c0m, c0pm = self.km.compose(st, l, self.Mkk)
        return self.km.taylor_box(Zb, zm, c0m, c0pm, st["s"])


# ------------------------------------------------------------------------------------------------ the tests
def f0s(Zb):
    D = Zb * Zb + A * A
    m = acb(Zb.real.mid(), Zb.imag.mid())
    Dm = m * m + A * A
    f0m = (m * m - 2 * m + A * A) / Dm
    f0pm = 2 * (m * m - A * A) / (Dm * Dm)
    f0pp = 4 * Zb * (3 * A * A - Zb * Zb) / (D * D * D)
    dz = Zb - m
    return f0m + f0pm * dz + f0pp * dz * dz / 2, f0pm + f0pp * dz, D


def nonsingular(Zb, field, km, edge=None, t=None):
    D = Zb * Zb + A * A
    if D.contains(0):
        return False
    if km.cb.B_mv(Zb).contains(0):
        return False
    try:
        c0, c0p = field.box(Zb, edge, t)
    except (AssertionError, RuntimeError):
        return False
    f0, _f0p, _D = f0s(Zb)
    G2 = f0 * f0 + c0 * c0
    G1 = E2 * G2 - f0
    return not (G1.contains(0) or G2.contains(0))


def loop_ok(poly, field, km, depth=6):
    """every edge of the polygon covered by boxes certified nonsingular; -> (ok, where)"""
    for e, (v0, v1) in enumerate(zip(poly[:-1], poly[1:])):
        n = max(1, int(abs(v1 - v0) / PIECE) + 1)
        todo = [(j / n, (j + 1) / n, depth) for j in range(n)]
        while todo:
            t0, t1, d = todo.pop()
            a, b = v0 + (v1 - v0) * t0, v0 + (v1 - v0) * t1
            m, hw = (a + b) / 2, abs(b - a) / 2 * 1.0001 + 1e-15
            Zb = acb(arb(m.real, hw), arb(m.imag, hw))
            if nonsingular(Zb, field, km, e, (t0 + t1) / 2):
                continue
            if d == 0:
                return False, [m.real, m.imag, e]
            tm = (t0 + t1) / 2
            todo += [(t0, tm, d - 1), (tm, t1, d - 1)]
    return True, None


def _cross(o, a, b):
    return (a.real - o.real) * (b.imag - o.imag) - (a.imag - o.imag) * (b.real - o.real)


def conv(pts):
    P = sorted(set((p.real, p.imag) for p in pts))
    P = [complex(x, y) for x, y in P]
    if len(P) <= 2:
        return P
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and _cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and _cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def _disjoint(cx, cy, hw, poly):
    """the closed box [cx +- hw] x [cy +- hw] is certified disjoint from the convex polygon (a separating edge)"""
    corners = [complex(cx + sx * hw, cy + sy * hw) for sx in (-1, 1) for sy in (-1, 1)]
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if all(_cross(a, b, c) < -1e-12 for c in corners):
            return True
    return False


def region_ok(poly, field, km, box=0.01, depth=4):
    """the convex polygon covered by boxes certified nonsingular (boxes certified disjoint from it are skipped)"""
    if len(poly) < 3:
        return True
    xs, ys = [p.real for p in poly], [p.imag for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    nx, ny = max(1, int((x1 - x0) / box) + 1), max(1, int((y1 - y0) / box) + 1)
    hx, hy = (x1 - x0) / nx / 2, (y1 - y0) / ny / 2
    hw0 = max(hx, hy) * 1.0001 + 1e-15

    def ok(cx, cy, hw, d):
        if _disjoint(cx, cy, hw, poly):
            return True
        if nonsingular(acb(arb(cx, hw), arb(cy, hw)), field, km):
            return True
        if d == 0:
            return False
        h2 = hw / 2
        return all(ok(cx + sx * h2, cy + sy * h2, h2, d - 1) for sx in (-1, 1) for sy in (-1, 1))
    for i in range(nx):
        for j in range(ny):
            if not ok(x0 + hx * (2 * i + 1), y0 + hy * (2 * j + 1), hw0, depth):
                return False
    return True


def homotopy_ok(La, Lb, field, km):
    """the straight-line homotopy La -> Lb (vertex j to vertex j) sweeps only certified-nonsingular points"""
    assert len(La) == len(Lb) and La[0] == Lb[0] == La[-1] == Lb[-1] == R0, "gluing: lassos must share the base"
    for j in range(len(La) - 1):
        if not region_ok(conv([La[j], La[j + 1], Lb[j + 1], Lb[j]]), field, km):
            return False, [La[j].real, La[j].imag, j]
    return True, None


# ------------------------------------------------------------------------------------------------ diagnostics (e)
def clearance(poly, field, km, ref):
    """float clearance of the lasso from r+ and p+ at the cell centre (Newton at kc on the point field), not gated"""
    pts = [complex(float(p[0]), float(p[1])) for p in ref["points"]]
    out = {}
    for nm, z in (("r+", pts[0]), ("p+", pts[2])):
        for _ in range(30):
            c0, c0p = field.box(acb(z.real, z.imag)) if isinstance(field, SquareField) else (None, None)
            if c0 is None:
                break
            f0, f0p, _D = f0s(acb(z.real, z.imag))
            G2 = f0 * f0 + c0 * c0
            dG2 = 2 * (f0 * f0p + c0 * c0p)
            g, dg = (E2 * G2 - f0, E2 * dG2 - f0p) if nm == "r+" else (G2, dG2)
            dz = complex(g.mid()) / complex(dg.mid())
            z = complex(float((z - dz).real), float((z - dz).imag))
            if abs(dz) < 1e-14:
                break

        def seg_d(p, a, b):
            ab = b - a
            t = max(0.0, min(1.0, ((p - a) * ab.conjugate()).real / max(abs(ab) ** 2, 1e-300)))
            return abs(p - (a + ab * t))
        out[nm] = min(seg_d(z, a, b) for a, b in zip(poly[:-1], poly[1:]))
    return out


# ------------------------------------------------------------------------------------------------ the chain
def load():
    F = json.load(open(FLOATS))
    refs = {k: F[k] for k in LINKS}
    for k, e in refs.items():
        assert e["geometry_ok"] is True, f"floats entry {k}: geometry not ok"
    las = {k: [complex(float(p[0]), float(p[1])) for p in e["lasso"]] for k, e in refs.items()}
    for k, L in las.items():
        assert L[0] == R0 and L[-1] == R0, f"lasso {k} not based at R0"
    return refs, las


def cells_of(lo, hi):
    """real k-cells (centre, half) of width CELLW covering [lo, hi]; centres are exact dyadic-rational balls' mids"""
    n = int(float(((hi - lo) / CELLW).upper()) + 0.999999)
    out = []
    for i in range(n):
        a = lo + (hi - lo) * i / n
        b = lo + (hi - lo) * (i + 1) / n
        c = arb(((a + b) / 2).mid())
        h = max((c - a).abs_upper(), (b - c).abs_upper())
        out.append((c, arb(h).upper()))
    return out


def halves(c, h):
    out = []
    for s in (-1, 1):
        q = c + s * h / 2
        qc = arb(q.mid())
        out.append((qc, (h / 2 + (q - qc).abs_upper()).upper()))
    return out


def certify_cells(lo, hi, job, label):
    """run job(KModel) on every cell of [lo, hi], halving on failure down to MAXLEV; -> (ok, records)"""
    todo = [(c, h, 0) for c, h in cells_of(lo, hi)]
    recs = []
    while todo:
        c, h, lev = todo.pop(0)
        t = time.time()
        try:
            km = KModel(c, h)
            ok, where = job(km)
        except (RuntimeError, AssertionError) as e:
            ok, where = False, str(e)[:200]
        recs.append(dict(k=float(c.mid()), h=float(h), level=lev, ok=ok, where=where, t=round(time.time() - t, 1)))
        print(f"  {label} cell {float(c.mid()):.5f} +- {float(h):.1e} L{lev}: {'ok' if ok else 'FAIL'} "
              f"{'' if ok else where} [{recs[-1]['t']} s]", flush=True)
        if not ok:
            if lev >= MAXLEV:
                return False, recs
            todo = [(qc, qh, lev + 1) for qc, qh in halves(c, h)] + todo
    return True, recs


def closed_lift_circle(km):
    """(f), hostile-read point 1: the circle's lift is CLOSED for every k in the cell. c0'' = pref sqrt(B)/(z^2 + a^2)^3
    has singular points only at +-ia and the zeros of B(z^2/a^2, k). If all of them lie in |z| < R0, then c0'' is
    single-valued and holomorphic on |z| >= R0 (an even number of B zeros inside, so sqrt B returns), including at infinity,
    where c0'' = O(z^-4). So the integrals of c0'' and of s c0'' round the circle vanish (no z^-1 term at infinity): c0 and c0'
    return, hence so does q. Certified: |w+-| < (R0/a)^2 for the roots w of c2 w^2 + c1 w + c0 over the k-ball, and
    |ia| = a < R0. -> (ok, where)"""
    K = km.kb
    c2, c1, c0 = 90 - 21 * K, -(60 - 18 * K), 10 - K
    if not (c2.real > 0):                        # alpha(k) = 90 - 21k > 0 on the cell (hostile-read point 4)
        return False, "alpha(k) = 90 - 21k not certified positive"
    sq = (c1 * c1 - 4 * c2 * c0).sqrt()          # a ball (wide near k = 4, where the discriminant vanishes): still valid
    lim = (arb(R0.real) / A) ** 2
    for w in ((-c1 + sq) / (2 * c2), (-c1 - sq) / (2 * c2)):
        if not (w.is_finite() and w.abs_upper() < lim):
            return False, f"a zero of B is not certified inside |z| < R0 (|w| <= {float(w.abs_upper()):.4g})"
    if not (A < arb(R0.real)):
        return False, "+-ia not inside |z| < R0"
    return True, None


def link_job(lasso, ref, diag):
    circ = V.circle_vertices()

    def job(km):
        ok, where = closed_lift_circle(km)
        if not ok:
            return False, ["closed lift"] + [where]
        pf = PathField(km, circ)
        ok, where = loop_ok(circ, pf, km)
        if not ok:
            return False, ["circle"] + where
        sf = SquareField(km)
        if not all(abs(z.real - SQ_C) < SQ_R - 0.05 and abs(z.imag) < SQ_R - 0.05 for z in lasso):
            return False, ["lasso", "a vertex is outside the single-valued square (closed lift not certified)"]
        ok, where = loop_ok(lasso, sf, km)
        if not ok:
            return False, ["lasso"] + where
        if diag is not None:
            diag.append(dict(k=float(km.kc.mid()), clearance=clearance(lasso, sf, km, ref)))
        return True, None
    return job


def glue_job(La, Lb):
    def job(km):
        sf = SquareField(km)
        return homotopy_ok(La, Lb, sf, km)
    return job


def run():
    t0 = time.time()
    refs, las = load()
    out = dict(links=[], glue=[], stop=None)
    for i, k in enumerate(LINKS):
        kc = frac(k)
        diag = []
        ok, recs = certify_cells(kc - HALFJ, kc + HALFJ, link_job(las[k], refs[k], diag), f"link {k}")
        out["links"].append(dict(k_c=k, ok=ok, cells=recs, clearance=diag))
        if not ok:
            out["stop"] = f"link {k}"
            break
        if i + 1 < len(LINKS):
            kn = LINKS[i + 1]
            assert len(las[k]) == len(las[kn]), f"gluing {k} -> {kn}: vertex counts differ"
            ok, recs = certify_cells(kc + OV0, kc + OV1, glue_job(las[k], las[kn]), f"glue {k}->{kn}")
            out["glue"].append(dict(pair=[k, kn], ok=ok, cells=recs))
            if not ok:
                out["stop"] = f"glue {k}->{kn}"
                break
    out["wall"] = round(time.time() - t0, 1)
    out["verdict"] = "CHAIN CERTIFIED" if out["stop"] is None else f"STOPPED at {out['stop']}"
    json.dump(out, open(os.path.join(OUTD, "c2an_chain_3_5.json"), "w"), indent=1)
    print(f"C2-AN chain 3/5: {out['verdict']}; {out['wall']} s", flush=True)


def control(name):
    refs, las = load()
    k, kn = "69/20", "71/20"                       # link 5 and its successor (registration: links 4, 5 -> 67/20, 69/20)
    if name == "K1":                               # a G2 zero (p+ of the floats entry) placed ON the lasso
        L = list(las[k])
        p = refs[k]["points"][2]
        L[len(L) // 2] = complex(float(p[0]), float(p[1]))
        kc = frac(k)
        ok, recs = certify_cells(kc - CELLW / 2, kc + CELLW / 2, link_job(L, refs[k], None), "K1")
        expected = "lasso"
    elif name == "K1c":                            # a polygon from R0 out to ia (c0's log branch point) and back
        poly = [R0, complex(0.0, 0.6), R0]
        kc = frac(k)

        def job(km):
            ok, where = loop_ok(poly, PathField(km, poly), km)
            return ok, ["circle"] + (where or [])
        ok, recs = certify_cells(kc - CELLW / 2, kc + CELLW / 2, job, "K1c")
        expected = "circle (the walk's singular-point guard or (a))"
    elif name == "K2":                             # L_5 replaced by its complex conjugate on the gluing 67/20 -> 69/20
        k, kn = "67/20", "69/20"
        Lb = [z.conjugate() for z in las[kn]]
        kc = frac(k)
        ok, recs = certify_cells(kc + OV0, kc + OV1, glue_job(las[k], Lb), "K2")
        expected = "gluing"
    elif name == "K3":                             # past k_cross: B's outer zeros leave the circle (addendum C2-AN-1)
        c = arb(arb("4.2").mid())
        ok, where = closed_lift_circle(KModel(c, arb("0.005")))
        recs = [dict(k=4.2, ok=ok, where=where)]
        expected = "closed lift"
    else:
        raise SystemExit(f"unknown control {name}")
    verdict = "REFUSED (as it must)" if not ok else "DID NOT REFUSE"
    json.dump(dict(control=name, ok=ok, cells=recs, expected=expected, verdict=verdict),
              open(os.path.join(OUTD, f"c2an_control_{name}.json"), "w"), indent=1)
    print(f"C2-AN control {name}: {verdict}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "run":
        run()
    else:
        control(cmd)
