#!/usr/bin/env python3
"""v7 stage V1: the twist potential c0 WITHOUT the Laurent series, in Arb (registration V7_REGISTRATION.md).

    c0''(z) = -sqrt(8/5) a^3 sqrt(B(z^2/a^2, k)) / (z^2 + a^2)^3,   B(w, k) = (90 - 21k) w^2 - (60 - 18k) w + (10 - k),
normalised by c0, c0' -> 0 as z -> +inf, with sqrt(B) the branch that is positive at large positive real z.

Starting constants at a real base point z_s > 0 (exact, no cutoff): with t = 1/s,
    c0'(z_s) = -int_{z_s}^inf c0''(t) dt = sqrt(8/5) a int_0^{1/z_s} s^2 sqrt(P(s)) / (1 + a^2 s^2)^3 ds,
    c0(z_s)  =  int_{z_s}^inf (t - z_s) c0''(t) dt = -sqrt(8/5) a int_0^{1/z_s} (s - z_s s^2) sqrt(P(s)) / (1 + a^2 s^2)^3 ds,
    P(s) = (90 - 21k) - (60 - 18k) a^2 s^2 + (10 - k) a^4 s^4   (= a^4 s^4 B(1/(a^2 s^2), k)).
P is analytic in s and Re P > 0 on [0, 1/z_s] for every k with Re k <= 30/7 and z_s >= 0.9 a sqrt(...) (checked at run
time: the integrand returns NaN on any ball where Re P > 0 is not certified, so Arb's integrator refuses it). On that
interval the principal sqrt IS the global branch (positive at s = 0+, i.e. at z = +inf).

Propagation along a polygon path: Taylor series of c0'' at each step point (acb_series, N terms), integrated once and
twice, plus a Cauchy remainder from M = sup |c0''| on a box enclosing the disc of radius r, with |h| <= r / 4. The
branch of sqrt(B) is carried by continuity and asserted at every step (the predicted and recomputed values must be
certifiably closer than their negatives). Works for k a point or a complex ball.
    from _nve_v7_c0 import C0;  c = C0(spin, k);  st = c.start(zs);  states = c.walk(vertices, st)
"""
import os
import sys
from fractions import Fraction

from flint import acb, acb_series, arb, ctx

ctx.prec = 256
NTERMS = 80          # series length; with |h| <= r/4 the truncation is <= M r 4^-80 / (1 - 1/4)


def _arb_frac(q):
    q = Fraction(q)
    return arb(q.numerator) / q.denominator


class C0:
    def __init__(self, spin, k, plant=None, exact_control_k0=False):
        self.a = _arb_frac(spin) if not isinstance(spin, arb) else spin
        self.k = k if isinstance(k, acb) else acb(k)
        self.plant = plant or {}
        a, kk = self.a, self.k
        self.pref = -(arb(8) / 5).sqrt() * a ** 3
        self.c2, self.c1, self.c0 = 90 - 21 * kk, -(60 - 18 * kk), 10 - kk
        # B != 0 guard for real u: by the registration's lemma, real k-values must lie in (0, 30/7]
        k0_ok = exact_control_k0 and self.k.is_zero()     # Kerr: B = 10(3w - 1)^2 has a DOUBLE zero, no branch point
        if self.k.imag.is_zero() and not k0_ok and not (self.k.real > 0 and self.k.real <= arb(30) / 7):
            raise ValueError("k outside (0, 30/7]: B may vanish on the real u-axis; refused")
        self.steps = 0

    # ---------------------------------------------------------------------------------------------- pointwise
    def B(self, z):
        w = z * z / (self.a * self.a)
        return self.c2 * w * w + self.c1 * w + self.c0

    def B_mv(self, bx):
        """B on a box by the mean-value form: B(bx) is contained in B(m) + B'(bx) (bx - m), m the box's midpoint
        (rigorous: B is a polynomial in z; far tighter than direct ball evaluation near a small |B|)."""
        m = acb(bx.mid())
        w = bx * bx / (self.a * self.a)
        dB = (2 * bx / (self.a * self.a)) * (2 * self.c2 * w + self.c1)
        return self.B(m) + dB * (bx - m)

    def c0pp(self, z, s):
        return self.pref * s / ((z * z + self.a * self.a) ** 3)

    # ---------------------------------------------------------------------------------------------- start
    def _P(self, s):
        a2s2 = self.a * self.a * s * s
        return self.c2 + self.c1 * a2s2 + self.c0 * a2s2 * a2s2

    def start(self, zs):
        """(c0, c0', sqrt B) at the real base point zs > 0, as acb balls."""
        zs = acb(zs)
        a = self.a
        lim = 1 / zs

        def make(weight):
            def f(s, analytic):
                P = self._P(s)
                if analytic and not (P.real > 0):
                    return acb("nan")
                return weight(s) * P.sqrt() / ((1 + a * a * s * s) ** 3)
            return f

        I1 = acb.integral(make(lambda s: s * s), 0, lim, rel_tol=arb(2) ** -240)
        I0 = acb.integral(make(lambda s: s - zs * s * s), 0, lim, rel_tol=arb(2) ** -240)
        k8 = (arb(8) / 5).sqrt() * a
        c0p = k8 * I1
        c0v = -k8 * I0
        if "dc0p" in self.plant:
            c0p = c0p + acb(self.plant["dc0p"])
        s = self.B(zs).sqrt()
        if not (s.real > 0):
            raise AssertionError("start: sqrt B at the base point is not certified positive-real-part")
        return dict(z=zs, c0=c0v, c0p=c0p, s=s)

    # ---------------------------------------------------------------------------------------------- singularities
    def sing_points(self):
        """midpoints (complex floats) of the branch points +-a sqrt(w+-) and the poles +-ia, for step control only."""
        km = complex(self.k.mid())
        a = float(self.a.mid())
        c2, c1, c0 = 90 - 21 * km, -(60 - 18 * km), 10 - km
        pts = [1j * a, -1j * a]
        if abs(c2) > 1e-30:
            d = (c1 * c1 - 4 * c2 * c0) ** 0.5
            for w in ((-c1 + d) / (2 * c2), (-c1 - d) / (2 * c2)):
                r = a * w ** 0.5
                pts += [r, -r]
        return pts

    # ---------------------------------------------------------------------------------------------- Cauchy bound
    def sup_box(self, z, r, m=8, depth=5):
        """An upper bound for |c0''| on the square z + [-r, r]^2 (which contains the disc |x - z| <= r), from an m x m
        cover by sub-boxes, each split in four (up to `depth` times) while B != 0 or z^2 + a^2 != 0 is not yet
        certified on it. If some piece still cannot be certified, a singular point may be inside: refused. So sqrt B
        is holomorphic on the disc (B has no zero there). |sqrt B| = sqrt|B|, branch-free."""
        def bound(cx, cy, hw, d):
            bx = z + acb(arb(cx, hw), arb(cy, hw))
            Bb = self.B_mv(bx)
            Db = bx * bx + self.a * self.a
            if not (Bb.contains(0) or Db.contains(0)):
                return (self.pref.abs_upper() * Bb.abs_upper().sqrt() / (Db.abs_lower() ** 3)).upper()
            if d == 0:
                raise AssertionError("step: a singular point of c0'' is within the Cauchy disc")
            h2 = (hw / 2).upper()
            return max(bound(cx + sx * h2, cy + sy * h2, h2, d - 1) for sx in (-1, 1) for sy in (-1, 1))
        M = arb(0)
        hw = (arb(r) / m).upper()
        for i in range(m):
            for j in range(m):
                cx = (-arb(r) + hw * (2 * i + 1)).mid()
                cy = (-arb(r) + hw * (2 * j + 1)).mid()
                M = max(M, bound(arb(cx), arb(cy), hw, depth))
        return M.upper()

    # ---------------------------------------------------------------------------------------------- one step
    def step(self, st, h, r):
        """advance (c0, c0', s) from st['z'] by h (acb), with Cauchy radius r (arb, |h| <= r/4 required)."""
        z, s0 = st["z"], st["s"]
        habs = acb(h).abs_upper()
        if not habs <= r / 4:
            raise AssertionError("step: |h| > r/4")
        # sup |c0''| on the box containing the disc |x - z| <= r (branch-free: |sqrt B| = sqrt |B|)
        M = self.sup_box(z, r)
        # Taylor series of c0'' at z
        ctx.cap = NTERMS
        x = acb_series([z, 1])
        Bs = self.B(x)
        sq = Bs.sqrt()
        c = sq.coeffs()
        if not (abs(c[0] - s0) < abs(c[0] + s0)):        # principal at z vs the carried branch
            sq = -sq
            c = sq.coeffs()
        if not (abs(c[0] - s0) < abs(c[0] + s0)):
            raise AssertionError("step: branch of sqrt B ambiguous at the step start")
        f = (self.pref * sq / ((x * x + self.a * self.a) ** 3)).coeffs()
        f = f + [acb(0)] * (NTERMS - len(f))
        # integrate once and twice
        hp = acb(h)
        d1 = acb(0)
        d2 = acb(0)
        hn = hp
        for n in range(NTERMS):
            d1 += f[n] * hn / (n + 1)
            d2 += f[n] * hn * hp / ((n + 1) * (n + 2))
            hn *= hp
        th = (arb(habs) / r).upper()
        tail1 = (M * habs * th ** NTERMS / (1 - th)).upper()
        tail2 = (M * habs * habs * th ** NTERMS / (1 - th)).upper()
        u1 = acb(arb(0, tail1), arb(0, tail1))
        u2 = acb(arb(0, tail2), arb(0, tail2))
        znew = z + hp
        c0p = st["c0p"] + d1 + u1
        c0v = st["c0"] + st["c0p"] * hp + d2 + u2
        # carry the branch: the series prediction of sqrt B at z + h vs the principal value there
        pred = acb(0)
        hn = acb(1)
        for n, cn in enumerate(c):
            pred += cn * hn
            hn *= hp
        snew = self.B(znew).sqrt()
        if abs(snew + pred) < abs(snew - pred):
            snew = -snew
        if "flip_at" in self.plant and self.steps == self.plant["flip_at"]:
            snew = -snew                                    # must-fail control (ii): a wrong branch choice at the step end
        if not (abs(snew - pred) < abs(snew + pred)):
            raise AssertionError(f"step {self.steps}: branch continuity of sqrt B not certified")
        self.steps += 1
        return dict(z=znew, c0=c0v, c0p=c0p, s=snew)

    # ---------------------------------------------------------------------------------------------- walk a path
    def walk(self, vertices, st, frac=0.5):
        """vertices: list of acb (the first equal to st['z']). Returns the state at every vertex (sub-steps inside)."""
        sing = self.sing_points()
        out = [st]
        for v0, v1 in zip(vertices[:-1], vertices[1:]):
            z = st["z"]
            while True:
                zc = complex(z.mid())
                d = min(abs(zc - p) for p in sing)
                if d < 1e-8:
                    raise AssertionError(f"walk: the path meets a singular point of c0'' near {zc}")
                r = arb(frac * d)
                rem = complex((acb(v1) - z).mid())
                hmax = 0.24 * frac * d
                if abs(rem) <= hmax:
                    h = acb(v1) - z
                    st = self.step(st, h, r)
                    st["z"] = acb(v1)                        # exact vertex (h was v1 - z)
                    break
                h = acb(rem / abs(rem) * hmax)
                st = self.step(st, h, r)
                z = st["z"]
            out.append(st)
        return out


def circle_vertices(R, n, start_angle=0):
    """n+1 vertices on |z| = R from angle 0 back to 2 pi (exact last = first)."""
    out = [acb(R)]
    for j in range(1, n):
        th = 2 * arb.pi() * j / n
        out.append(acb(R) * acb(0, th).exp())
    out.append(acb(R))
    return out


if __name__ == "__main__":
    sp = os.environ.get("NVE_SPIN", "3/5")
    c = C0(sp, acb(3))
    st = c.start(arb("1.35"))
    print("start", st["c0"], st["c0p"])
    sys.exit(0)
