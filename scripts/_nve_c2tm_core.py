#!/usr/bin/env python3
"""C2-TM core (data/nve/route1_check/C2_TM_REGISTRATION.md, Design 1-2): univariate COMPLEX Taylor models in dk.

A TM is (c, e): c a list of D+1 acb coefficients (degree <= D in dk), e a point arb with
    |f(kc + dk) - sum_j c_j dk^j| <= e   for every |dk| <= RHOK (a closed disc).
Coefficients may be BALLS (a ball coefficient means: for some choice inside the ball; every operation below is
monotone in that sense, so ball coefficients are rigorous).

Operations and their remainder rules:
  +, -, scalar x                 exact on the coefficients; e adds (times |scalar| for the scalar product);
  x                              the full product's degrees > D are bounded by sum |c_j| RHOK^j into e, plus
                                 |p| e' + |p'| e + e e', where |p| <= B(p) := sum |c_j| RHOK^j;
  recip(T)                       theta-guard: theta = B(T - c0)/|c0| + e/|c0| <= 1/2 certified, else TMRefuse.
                                 q = the truncated series inverse of p (acb_series); the error is |1/T - q| <=
                                 B(1 - T q)/inf|T|, inf|T| >= |c0| (1 - theta);
  sqrt(T)                        theta-guard as recip, AND c0 off the cut (Re c0 > 0, or Im c0 != 0 certified).
                                 The result encloses the CONTINUATION over the disc of the principal root at c0 (TM
                                 read F4): it is the principal root on the whole disc only where T's range is itself
                                 certified off the cut (the walk's off-cut guard ensures that). q = the truncated
                                 series sqrt (principal at c0); |sqrt T - q| = |T - q^2| / |sqrt T + q| with
                                 |sqrt T + q| >= |sqrt c0| (sqrt(1 - theta) + 1 - B(q - q0)/|sqrt c0|), required > 0.
The bound B and every inequality are evaluated in Arb (upper/lower bounds), never in floats.
"""
from flint import acb, acb_poly, acb_series, arb, ctx

ctx.prec = 256
D = 12                       # the registered degree (C2-TM: d = 12, fixed)
RHOK = arb(0)                # the disc radius; set by set_disc()
RPOW = []                    # RHOK^j, j = 0 .. 2D (upper bounds), precomputed by set_disc()


class TMRefuse(Exception):
    """a guard refused (the message names it)"""


def set_disc(rho, force=False):
    """TM read F9: RHOK is module-global, so TMs built for one disc are invalid under another. A second, different
    disc in one process is refused unless force=True (the self-test, which restores the old disc)."""
    global RHOK, RPOW
    if RHOK > 0 and not force and not (arb(rho) == RHOK):
        raise TMRefuse("set_disc: a second, different disc in this process (TMs of the first would be invalid)")
    RHOK = arb(rho)
    assert RHOK > 0
    RPOW = [(RHOK ** j).upper() for j in range(2 * D + 2)]


def _B(c, start=0):
    """upper bound of sup_{|dk| <= RHOK} |sum_j c_j dk^(start + j)|"""
    tot = arb(0)
    for j, x in enumerate(c):
        tot += x.abs_upper() * RPOW[start + j]
    return tot.upper()


class TM:
    __slots__ = ("c", "e")

    def __init__(self, c, e=None):
        c = [x if isinstance(x, acb) else acb(x) for x in c]
        if len(c) < D + 1:
            c = c + [acb(0)] * (D + 1 - len(c))
        assert len(c) == D + 1, "a TM has exactly D + 1 coefficients"
        self.c = c
        self.e = arb(0) if e is None else arb(e).upper()
        assert self.e >= 0

    # ------------------------------------------------------------------ constructors
    @staticmethod
    def const(x):
        return TM([x])

    @staticmethod
    def dk():
        return TM([acb(0), acb(1)])

    # ------------------------------------------------------------------ queries
    def bound(self):
        """upper bound of sup |f| over the disc"""
        return (_B(self.c) + self.e).upper()

    def at(self, dk):
        """an enclosure of f(kc + dk) for |dk| <= RHOK (dk an acb point or ball inside the disc)"""
        assert (dk.abs_upper() <= RHOK), "evaluation point outside the disc"
        v = acb(0)
        for x in reversed(self.c):
            v = v * dk + x
        return v + acb(arb(0, self.e), arb(0, self.e))

    def range(self):
        """an enclosure of f over the whole disc (a complex ball)"""
        b = (_B([acb(0)] + self.c[1:]) + self.e).upper()
        return self.c[0] + acb(arb(0, b), arb(0, b))

    def is_finite(self):
        return all(x.is_finite() for x in self.c) and self.e.is_finite()

    # ------------------------------------------------------------------ arithmetic
    def __add__(self, o):
        if not isinstance(o, TM):
            o = TM.const(o)
        return TM([a + b for a, b in zip(self.c, o.c)], self.e + o.e)

    __radd__ = __add__

    def __neg__(self):
        return TM([-a for a in self.c], self.e)

    def __sub__(self, o):
        if not isinstance(o, TM):
            o = TM.const(o)
        return TM([a - b for a, b in zip(self.c, o.c)], self.e + o.e)

    def __rsub__(self, o):
        return TM.const(o) - self

    def scale(self, s):
        s = s if isinstance(s, acb) else acb(s)
        return TM([a * s for a in self.c], self.e * s.abs_upper())

    def __mul__(self, o):
        if not isinstance(o, TM):
            return self.scale(o)
        full = (acb_poly(self.c) * acb_poly(o.c)).coeffs()        # C-level product (python-flint acb_poly)
        low = full[:D + 1]
        hi = _B(full[D + 1:], D + 1) if len(full) > D + 1 else arb(0)
        e = hi + _B(self.c) * o.e + _B(o.c) * self.e + self.e * o.e
        return TM(low, e)

    __rmul__ = __mul__

    # ------------------------------------------------------------------ the theta guard
    def theta(self, name=""):
        c0 = self.c[0]
        if c0.contains(0):
            raise TMRefuse(f"theta-guard{(' (' + name + ')') if name else ''}: the constant coefficient contains 0")
        a0 = c0.abs_lower()
        return ((_B([acb(0)] + self.c[1:]) + self.e) / a0).upper()

    def _series(self, op):
        """op applied to the dk-series of the coefficients, truncated at D + 1 terms. python-flint truncates every series
        at ctx.cap (default 10) whatever prec is passed, so the cap is set to D + 1 here and restored afterwards
        (the z-series code sets its own cap)."""
        old = ctx.cap
        ctx.cap = D + 1
        try:
            assert ctx.cap == D + 1
            out = op(acb_series(self.c)).coeffs()
            assert len(out) <= D + 1, "series longer than the cap"
        finally:
            ctx.cap = old
        return [out[j] if j < len(out) else acb(0) for j in range(D + 1)]

    def recip(self, name=""):
        th = self.theta(name)
        if not th <= arb(1) / 2:
            raise TMRefuse(f"reciprocal theta-guard{(' (' + name + ')') if name else ''}: theta {float(th.mid()):.3g} > 1/2")
        q = self._series(lambda x: 1 / x)
        Q = TM(q)
        r = TM.const(1) - self * Q                       # 1 - T q, rigorous (its own e included)
        inf_T = (self.c[0].abs_lower() * (1 - th)).lower()
        if not inf_T > 0:
            raise TMRefuse("reciprocal: inf |T| not certified positive")
        return TM(q, (r.bound() / inf_T).upper())

    def sqrt(self, name=""):
        c0 = self.c[0]
        if not (c0.real > 0 or c0.imag > 0 or c0.imag < 0):
            raise TMRefuse(f"sqrt cut-guard{(' (' + name + ')') if name else ''}: the constant term is not certified off "
                           f"the cut")
        th = self.theta(name)
        if not th <= arb(1) / 2:
            raise TMRefuse(f"sqrt theta-guard{(' (' + name + ')') if name else ''}: theta {float(th.mid()):.3g} > 1/2")
        q = self._series(lambda x: x.sqrt())
        Q = TM(q)
        num = (self - Q * Q).bound()
        s0 = c0.sqrt()
        a = s0.abs_lower()
        if not a > 0:
            raise TMRefuse("sqrt: |sqrt c0| not certified positive")
        den = a * ((1 - th).sqrt() + 1 - _B([acb(0)] + q[1:]) / a)
        if not den > 0:
            raise TMRefuse("sqrt: the denominator |sqrt T + q| is not certified positive")
        return TM(q, (num / den).upper())

    def __truediv__(self, o):
        if not isinstance(o, TM):
            o = o if isinstance(o, acb) else acb(o)
            return self.scale(1 / o)
        return self * o.recip()

    def __repr__(self):
        return f"TM(c0={self.c[0].str(8)}, B={float(self.bound().mid()):.3e}, e={float(self.e.mid()):.3e})"


def selftest(npts=300, seed=1):
    """the TM arithmetic against direct Arb evaluation at random points of the disc (registration order 3): every
    enclosure must OVERLAP the direct value (two independently rounded balls of the same true value need not nest,
    but a wrong enclosure is disjoint), and the midpoint error must be <= e. Plus must-fire checks: both guards
    refuse, and a planted coefficient error is caught. -> True / False"""
    global RHOK, RPOW
    import math
    import random
    old = RHOK
    set_disc(arb("0.1"), force=True)
    random.seed(seed)
    f = TM([acb(2), acb("0.7"), acb("-0.3"), acb(0, "0.1")])
    g = TM([acb("1.5"), acb(0, "-0.4")])

    def direct(dk, which):
        fv = 2 + acb("0.7") * dk - acb("0.3") * dk ** 2 + acb(0, "0.1") * dk ** 3
        gv = acb("1.5") + acb(0, "-0.4") * dk
        return {"mul": fv * gv, "recip": 1 / fv, "sqrt": fv.sqrt(), "div": fv / gv, "chain": (fv * gv + 1).sqrt() / fv}[which]

    tms = {"mul": f * g, "recip": f.recip(), "sqrt": f.sqrt(), "div": f / g, "chain": ((f * g) + 1).sqrt() / f}
    ok = True
    for nm, tm in tms.items():
        for _ in range(npts):
            r = random.random() * 0.1
            th = random.random() * 2 * math.pi
            dk = acb(r * math.cos(th), r * math.sin(th))
            a, b = tm.at(dk), direct(dk, nm)
            ok &= bool(a.overlaps(b)) and bool((acb(a.mid()) - acb(b.mid())).abs_upper() <= tm.e + b.rad() * 2 + arb("1e-70"))
    bad = f.recip()
    bad.c[3] = bad.c[3] + acb("1e-6")
    x = acb("0.09")
    planted = not bad.at(x).overlaps(1 / (2 + acb("0.7") * x - acb("0.3") * x ** 2 + acb(0, "0.1") * x ** 3))
    set_disc(arb(3), force=True)
    g1 = g2 = False
    try:
        f.recip()
    except TMRefuse:
        g1 = True
    try:
        TM([acb(-1), acb("0.01")]).sqrt()
    except TMRefuse:
        g2 = True
    if old > 0:
        set_disc(old, force=True)
    else:                                                # TM re-read: restore "no disc set" exactly
        RHOK, RPOW = arb(0), []
    return bool(ok and planted and g1 and g2)


if __name__ == "__main__":
    r = selftest()
    print(f"C2-TM core self-test: {'PASS' if r else 'FAIL'}", flush=True)
    raise SystemExit(0 if r else 1)
