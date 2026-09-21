#!/usr/bin/env python3
"""dCS step 4b: the O(zeta chi^2) EVEN-PARITY metric correction -- the order Carter dies at.

THE LEFT-HAND SIDE IS NOT JUST L[h2], and getting that wrong would be invisible. At O(zeta chi^2)
the Einstein tensor picks up, besides the linearised operator acting on the new even correction,
CROSS TERMS between the O(zeta chi) correction of step 3 and the O(chi) Lense-Thirring background --
both odd, so their product is even and lands exactly here. Dropping them yields a wrong metric that
still looks plausible and that no downstream control would catch (the §124 failure mode). So the LHS
is built from the FULL metric with both zeta and chi truncated, never assembled piecewise.

CONTROL FIRST, PHYSICS SECOND. Before any dCS source is used, the same machinery is asked a question
whose answer is known: Kerr truncated at O(chi^2) must satisfy the VACUUM equations to that order.
That validates the truncated curvature, the perturbative inverse and the order extraction together,
on an object that can fail -- unlike "the correction vanishes when the coupling vanishes".

Repro:  .venv/bin/python scripts/_kt_dcs_metric2.py [--control-only]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from _kt_dcs_order2 import M, X, chi, christoffel, pinv, r, ricci_dd, riemann_uddd, th, tr  # noqa: E402

zeta = sp.Symbol("zeta")
f = 1 - 2 * M / r
s2 = sp.sin(th) ** 2
P2 = (3 * sp.cos(th) ** 2 - 1) / 2


def kerr_chi2():
    """Kerr in Boyer-Lindquist with a = M chi, series-truncated at chi^2."""
    a = M * chi
    Sig = r**2 + a**2 * sp.cos(th) ** 2
    Dl = r**2 - 2 * M * r + a**2
    g = sp.zeros(4, 4)
    g[0, 0] = -(1 - 2 * M * r / Sig)
    g[0, 3] = g[3, 0] = -2 * M * a * r * s2 / Sig
    g[1, 1] = Sig / Dl
    g[2, 2] = Sig
    g[3, 3] = (r**2 + a**2 + 2 * M * a**2 * r * s2 / Sig) * s2
    return sp.Matrix(4, 4, lambda i, j: sp.expand(
        sp.series(sp.together(g[i, j]), chi, 0, 3).removeO()) if g[i, j] != 0 else sp.S.Zero)


def einstein_trunc(g, g0, gi0, label=""):
    """G_ab of a metric, truncated at every step."""
    gi = pinv(g, g0, gi0)
    Gam = christoffel(g, gi)
    Ric = ricci_dd(riemann_uddd(Gam))
    Rs = tr(sp.expand(sum(gi[A, B] * Ric[A, B] for A in range(4) for B in range(4))))
    G = sp.Matrix(4, 4, lambda A, B: tr(sp.expand(Ric[A, B] - g[A, B] * Rs / 2)))
    return G


def chi_coeff(e, n):
    """The chi^n coefficient, WITHOUT sp.simplify."""
    return sp.cancel(sp.together(sp.diff(sp.expand(e), chi, n).subs(chi, 0) / sp.factorial(n)))


# Random exact-rational sample points; cos(th) rational so nothing is coerced (the trap that
# produced garbage in the Pontryagin spot-check).
_PTS = [(sp.Integer(1), sp.Rational(7, 2), sp.Rational(1, 3)),
        (sp.Integer(1), sp.Rational(5), sp.Rational(-2, 5)),
        (sp.Integer(1), sp.Rational(11, 4), sp.Rational(3, 4)),
        (sp.Integer(1), sp.Rational(13, 5), sp.Rational(-4, 9))]


def is_zero(e, pts=_PTS):
    """Zero test by high-precision evaluation at several random points, not by sp.simplify.

    WHY. Profiling the vacuum control: the whole curvature chain (perturbative inverse, Christoffel,
    Riemann, Ricci, Ricci scalar, G) costs 136 s, and then sp.simplify on the extracted coefficients
    ran past 8 MINUTES and was still going -- it was 97% of the job and it was answering a question
    nobody asked. A simplified FORM is not needed; only the verdict zero / nonzero is.

    A nonzero rational function of (r, cos th) cannot vanish at four random rational points except
    by coincidence, and a NONZERO reading is exact and immediate. The residual risk is one-sided and
    tiny: a false "zero". Anything reported zero here that matters is re-checked symbolically."""
    if e == 0:
        return True
    for Mv, rv, cv in pts:
        v = sp.N(e.subs({M: Mv, r: rv, th: sp.acos(cv)}), 40)
        if abs(v) > sp.Float("1e-30"):
            return False
    return True


if __name__ == "__main__":
    t0 = time.time()
    g0 = sp.diag(-f, 1 / f, r**2, r**2 * s2)
    gi0 = sp.diag(-1 / f, f, 1 / r**2, 1 / (r**2 * s2))

    print("CONTROL: Kerr truncated at O(chi^2) must be vacuum to that order\n", flush=True)
    gK = kerr_chi2()
    G = einstein_trunc(gK, g0, gi0)
    bad = []
    for i in range(4):
        for j in range(i, 4):
            for n in (0, 1, 2):
                c = chi_coeff(G[i, j], n)
                if not is_zero(c):
                    bad.append((i, j, n, c))
    if bad:
        print(f"  FAIL: G is nonzero at {[(i, j, n) for i, j, n, _ in bad]}", flush=True)
        for i, j, n, c in bad[:4]:
            print(f"    G[{i},{j}] at chi^{n} = {c}", flush=True)
        raise SystemExit(1)
    print(f"  PASS: every component of G vanishes at chi^0, chi^1 and chi^2 "
          f"[{time.time()-t0:.0f}s]", flush=True)
    print("        (truncated curvature, perturbative inverse and order extraction all validated)\n",
          flush=True)
    if "--control-only" in sys.argv:
        raise SystemExit(0)
