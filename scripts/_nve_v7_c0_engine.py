#!/usr/bin/env python3
"""v7 stage V1: the independent 50-digit engine for c0 (mpmath; registration V7_REGISTRATION.md).

Shares ONLY the formula for c0'' with the Arb evaluator (_nve_v7_c0.py). Differences by design:
  - start: direct t-space quadrature to +inf (mp.quad on [z_s, 4, 16, inf]) instead of the s = 1/t substitution;
  - propagation: per sub-segment quadrature (mp.quad) of c0'' and of (1 - tau) c0'' instead of Taylor series,
    with the branch of sqrt B fixed on each short sub-segment by nearness to its value at the sub-segment start;
  - no ball arithmetic.
    from _nve_v7_c0_engine import E0;  e = E0(spin, k);  st = e.start(zs);  states = e.walk(vertices, st)
"""
from fractions import Fraction

import mpmath as mp

mp.mp.dps = 50


class E0:
    def __init__(self, spin, k):
        q = Fraction(spin)
        self.a = mp.mpf(q.numerator) / q.denominator
        self.k = mp.mpc(k)
        self.pref = -mp.sqrt(mp.mpf(8) / 5) * self.a ** 3

    def B(self, z):
        w = z * z / (self.a * self.a)
        k = self.k
        return (90 - 21 * k) * w * w - (60 - 18 * k) * w + (10 - k)

    def c0pp(self, z, sref):
        s = mp.sqrt(self.B(z))
        if abs(s + sref) < abs(s - sref):
            s = -s
        return self.pref * s / (z * z + self.a * self.a) ** 3, s

    def start(self, zs):
        zs = mp.mpf(zs)
        f = lambda t: self.pref * mp.sqrt(self.B(t)) / (t * t + self.a * self.a) ** 3   # B > 0 on [zs, inf)
        c0p = -mp.quad(f, [zs, 4, 16, mp.inf])
        c0 = mp.quad(lambda t: (t - zs) * f(t), [zs, 4, 16, mp.inf])
        return dict(z=mp.mpc(zs), c0=mp.mpc(c0), c0p=mp.mpc(c0p), s=mp.sqrt(self.B(zs)))

    def sing_points(self):
        k, a = self.k, self.a
        c2, c1, c0 = 90 - 21 * k, -(60 - 18 * k), 10 - k
        pts = [mp.mpc(0, a), mp.mpc(0, -a)]
        if abs(c2) > mp.mpf(10) ** -40:
            d = mp.sqrt(c1 * c1 - 4 * c2 * c0)
            for w in ((-c1 + d) / (2 * c2), (-c1 - d) / (2 * c2)):
                r = a * mp.sqrt(w)
                pts += [r, -r]
        return pts

    def seg(self, st, z1):
        z0, s0 = st["z"], st["s"]
        h = z1 - z0
        g = lambda tau: self.c0pp(z0 + tau * h, s0)[0]
        d1 = h * mp.quad(g, [0, 1])
        d2 = h * h * mp.quad(lambda tau: (1 - tau) * g(tau), [0, 1])
        _, s1 = self.c0pp(z1, s0)
        return dict(z=z1, c0=st["c0"] + st["c0p"] * h + d2, c0p=st["c0p"] + d1, s=s1)

    def walk(self, vertices, st, frac=mp.mpf("0.1")):
        sing = self.sing_points()
        out = [st]
        for v1 in vertices[1:]:
            v1 = mp.mpc(v1)
            while True:
                d = min(abs(st["z"] - p) for p in sing)
                hmax = frac * d
                rem = v1 - st["z"]
                if abs(rem) <= hmax:
                    st = self.seg(st, v1)
                    break
                st = self.seg(st, st["z"] + rem / abs(rem) * hmax)
            out.append(st)
        return out
