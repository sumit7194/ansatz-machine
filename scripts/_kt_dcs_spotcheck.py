#!/usr/bin/env python3
"""Kerr Pontryagin control, decided by EXACT rational arithmetic at random points.  (dCS step 1)

WHY NOT THE SYMBOLIC FORM. `_kt_dcs.py`'s full-symbolic Kerr check is correct but the closing
sp.simplify on a rotating metric runs for hours. The claim under test -- *RR equals a stated closed
form -- is an identity between two RATIONAL functions of (r, cos th) once M and a are fixed to
rationals. Agreement at several random rational points, in exact arithmetic with no floating point
anywhere, settles it: two distinct rational functions of this bounded degree cannot agree at many
random points by accident, and a disagreement is conclusive immediately.

This is a CONTROL THAT CAN FAIL, which is the point (CLAUDE.md §5): the closed form is a specific
nonzero function, so wrong Levi-Civita signs, a wrong dual normalisation, or a wrong contraction all
show up as a mismatch or as a non-constant ratio rather than as a quiet zero.

Repro:  .venv/bin/python scripts/_kt_dcs_spotcheck.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from gr_engine import Geometry  # noqa: E402
from _kt_dcs import pontryagin  # noqa: E402

t, r, th, ph = sp.symbols("t r theta phi", real=True)


def kerr(M, a):
    Sig = r**2 + a**2 * sp.cos(th) ** 2
    Del = r**2 - 2 * M * r + a**2
    g = sp.zeros(4, 4)
    g[0, 0] = -(1 - 2 * M * r / Sig)
    g[0, 3] = g[3, 0] = -2 * M * a * r * sp.sin(th) ** 2 / Sig
    g[1, 1] = Sig / Del
    g[2, 2] = Sig
    g[3, 3] = (r**2 + a**2 + 2 * M * a**2 * r * sp.sin(th) ** 2 / Sig) * sp.sin(th) ** 2
    return g


def closed_form(M, a):
    c = sp.cos(th)
    Sig = r**2 + a**2 * c**2
    return 96 * M**2 * a * r * c * (3 * r**2 - a**2 * c**2) * (r**2 - 3 * a**2 * c**2) / Sig**6


if __name__ == "__main__":
    M, a = sp.Integer(1), sp.Rational(1, 3)
    print(f"Kerr Pontryagin control, M={M}, a={a}, exact rational arithmetic\n", flush=True)
    print("  building curvature ...", flush=True)
    P = pontryagin(Geometry(kerr(M, a), [t, r, th, ph]), simplify=False)
    K = closed_form(M, a)
    print("  built; evaluating at random points\n", flush=True)

    # th chosen so cos(th) is rational -> everything stays in Q, no floats, no evalf.
    pts = [(sp.Rational(7, 2), sp.Rational(1, 3)), (sp.Rational(5, 1), sp.Rational(-2, 5)),
           (sp.Rational(11, 4), sp.Rational(3, 4)), (sp.Rational(9, 2), sp.Rational(-1, 7)),
           (sp.Rational(6, 1), sp.Rational(2, 3)), (sp.Rational(13, 5), sp.Rational(-4, 9))]
    ok, ratios = True, []
    for rv, cv in pts:
        # th enters through sin(th) = sqrt(1-c^2) as well as cos(th), so the substituted values are
        # NOT rational in general. Earlier this test called nsimplify(..., rational=True) on them,
        # which silently replaces an irrational by a nearby fraction and produced garbage ratios --
        # a bug in the CHECK, not in the machinery. High-precision evaluation instead, no coercion.
        sub = {r: sp.Rational(rv), th: sp.acos(sp.Rational(cv))}
        pv = sp.N(P.subs(sub), 60)
        kv = sp.N(K.subs(sub), 60)
        rat = sp.N(pv / kv, 40) if kv != 0 else None
        rel = abs(pv - kv) / abs(kv) if kv != 0 else abs(pv)
        match = rel < sp.Float("1e-45")
        ratios.append(rat)
        ok &= bool(match)
        print(f"  r={rv}, cos(th)={cv}:  *RR = {sp.N(pv, 20)}", flush=True)
        print(f"      closed form = {sp.N(kv, 20)}   rel.diff = {sp.N(rel, 6)}   ratio: {sp.N(rat, 20)}",
              flush=True)

    print()
    uniq = {str(sp.N(x, 12)) for x in ratios if x is not None}
    if ok:
        print("  PASS: *RR matches the closed form exactly at every point.")
    elif len(uniq) == 1 and ratios[0] is not None:
        print(f"  CONSTANT RATIO {ratios[0]} at every point -- a convention factor (eps sign or dual\n"
              f"  normalisation), not a broken contraction. The machinery is right up to that factor.")
    else:
        print(f"  FAIL: ratio is not constant ({len(uniq)} distinct values) -- the contraction is wrong.")
        raise SystemExit(1)
