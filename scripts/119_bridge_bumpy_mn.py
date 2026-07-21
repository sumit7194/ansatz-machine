#!/usr/bin/env python3
"""Step 119 — BRIDGE ROUND 7: is "bumpy eps=0.35" the same spacetime as "Manko-Novikov q=0.5"?

The bridge's leg Q counts these as two of three independent non-integrable classes. If they are
the same spacetime the headline is two classes, not three. Both are rotating quadrupole
deformations of Kerr, both genuinely two-variable -- the regime where our CK signatures wall.

The bridge proposed three tiers (T1 Petrov type, T2 the I-J relation, T3 full CK). THE PAIR IS
DECIDED AT A TIER BELOW ALL THREE, using §117's order-0 Ricci/Segre sector, with no canonical
frame, no PND quartic and no gradient of Weyl computed at all:

    Manko-Novikov q=0.5  is an EXACT VACUUM solution      (R_ab = 0)
    bumpy eps=0.35       is NOT a vacuum solution         (R != 0, proven symbolically)

Different Segre/matter type is a rigorous INEQUIVALENT. The bumpy metric multiplies Kerr's g_tt
by bump = 1 + eps*6u^2/r and leaves the rest of Kerr alone; that is an ad-hoc deformation, and
ad-hoc deformations of a vacuum solution are essentially never Ricci-flat. It is a legitimate
testbed for geodesic dynamics -- which is what leg Q used it for -- but it is not a vacuum
spacetime, so it cannot be diffeomorphic to one.

WHAT THIS DOES AND DOES NOT SETTLE: it settles the equivalence question the bridge asked
(rigorously, and cheaply). It does NOT by itself collapse leg Q's "three classes" claim to two --
the two entries are genuinely different spacetimes. If anything the finding is the other way: the
two classes are distinct, but one of them is not a vacuum spacetime, which the bridge may want to
state when it describes the class.

Repro: .venv/bin/python scripts/119_bridge_bumpy_mn.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry
from manko_novikov import manko_novikov
from numeric_curvature import ricci_numeric

t, r, ph = sp.symbols("t r phi", real=True)
u = sp.Symbol("u", real=True)


def bumpy_symbolic(eps, a=sp.Rational(3, 5)):
    """The bridge's leg-O survey_catalog.delta_metric, exactly as supplied."""
    om = 1 - u**2
    Sig = r**2 + a**2 * u**2
    D = r**2 - 2 * r + a**2
    bump = 1 + eps * 6 * u**2 / r
    g = sp.zeros(4)
    g[0, 0] = -(D - a**2 * om) / Sig * bump
    g[0, 3] = g[3, 0] = -a * om * (r**2 + a**2 - D) / Sig
    g[1, 1] = Sig / D
    g[2, 2] = Sig / om
    g[3, 3] = om * ((r**2 + a**2)**2 - D * a**2 * om) / Sig
    return Geometry(g, [t, r, u, ph])


def bumpy_numeric(eps, a=0.6):
    def g(X):
        _, rr, uu, _ = X
        om = 1 - uu * uu
        Sig = rr * rr + a * a * uu * uu
        D = rr * rr - 2 * rr + a * a
        bump = 1 + eps * 6 * uu * uu / rr
        m = [[0.0] * 4 for _ in range(4)]
        m[0][0] = -(D - a * a * om) / Sig * bump
        m[0][3] = m[3][0] = -a * om * (rr * rr + a * a - D) / Sig
        m[1][1] = Sig / D
        m[2][2] = Sig / om
        m[3][3] = om * ((rr * rr + a * a)**2 - D * a * a * om) / Sig
        return m
    return g


def worst_ricci(gfun, pts, h=1e-5):
    w = 0.0
    for P in pts:
        R = ricci_numeric(gfun, P, h=h)
        w = max(w, max(abs(R[i][j]) for i in range(4) for j in range(4)))
    return w


def main():
    print("BRIDGE ROUND 7 — bumpy eps=0.35  vs  Manko-Novikov q=0.5\n")
    ok = []
    pts = [[0.0, 4.0, 0.3, 0.0], [0.0, 6.0, -0.5, 0.0], [0.0, 3.5, 0.7, 0.0]]

    # (A) the numeric harness, validated on its own control
    print("(A) NUMERIC SCREEN (harness validated by its own eps=0 control):")
    w_kerr = worst_ricci(bumpy_numeric(0.0), pts)
    w_bump = worst_ricci(bumpy_numeric(0.35), pts)
    okA = w_kerr < 1e-4 and w_bump > 1e-2
    ok.append(okA)
    print(f"    bumpy at eps=0 (i.e. exactly Kerr) : max|R_ab| = {w_kerr:.3e}  <- FD floor, vacuum")
    print(f"    bumpy at eps=0.35                  : max|R_ab| = {w_bump:.3e}  <- {w_bump/max(w_kerr,1e-30):.0f}x the floor")
    print(f"    => the bump breaks vacuum, and the control proves it is not a harness artefact "
          f"{'✅' if okA else '❌'}")

    # (B) Manko-Novikov really is vacuum: the residual is ROUNDOFF, not signal. Two checks --
    # it scales like roundoff in h, and it is the same size at q=0 (which is exactly Kerr).
    print("\n(B) MANKO-NOVIKOV IS VACUUM (residual is roundoff, not signal):")
    mn_pts = [[0.0, 6.0, 0.3, 0.0], [0.0, 8.0, -0.4, 0.0]]
    rows = []
    for q in (0.0, 0.5):
        gm = manko_novikov(1.0, 0.6, q)
        rows.append((q, worst_ricci(gm, mn_pts, h=1e-4), worst_ricci(gm, mn_pts, h=1e-5)))
    for q, c4, c5 in rows:
        print(f"    MN q={q}: max|R_ab| = {c4:.3e} (h=1e-4), {c5:.3e} (h=1e-5)  "
              "<- grows as h shrinks = roundoff")
    okB = (rows[1][1] < 1e-3 and rows[1][2] < 1e-3
           and rows[1][2] / max(rows[1][1], 1e-30) > 10)     # roundoff amplification, not signal
    same_class = rows[1][2] / max(rows[0][2], 1e-30) < 100   # q=0.5 behaves like q=0 (exactly Kerr)
    ok.append(okB and same_class)
    print(f"    q=0.5 residual is the same class as q=0 (exactly Kerr, certainly vacuum): "
          f"{same_class}   {'✅' if okB and same_class else '❌'}")
    print("    (and MN was verified line-by-line against Gair-Li-Mandel in §103)")

    # (C) THE PROOF: the bumpy metric is not even scalar-flat, symbolically
    print("\n(C) SYMBOLIC PROOF — the bumpy metric is not vacuum:")
    t0 = time.time()
    Rs = sp.simplify(bumpy_symbolic(sp.Rational(7, 20)).ricci_scalar)
    okC = (Rs != 0)
    val = sp.N(Rs.subs({r: 4, u: sp.Rational(3, 10)})) if okC else 0
    ok.append(okC)
    print(f"    Ricci scalar R computed exactly in {time.time()-t0:.0f}s; "
          f"identically zero? {Rs == 0}")
    print(f"    R(r=4, u=0.3) = {val}   (a vacuum solution would have R_ab = 0, hence R = 0)")
    print(f"    => bumpy eps=0.35 is NOT Ricci-flat -- it is not even scalar-flat   "
          f"{'✅' if okC else '❌'}")

    # (D) the verdict
    print("\n(D) VERDICT:")
    print("    Manko-Novikov q=0.5 : vacuum        (R_ab = 0, Segre type 'vacuum')")
    print("    bumpy eps=0.35      : NOT vacuum    (R != 0, proven above)")
    print("    Different Segre/matter type is a rigorous INEQUIVALENT (§117, order 0).")
    print("    => THE TWO ARE DIFFERENT SPACETIMES. Decided below the bridge's tier T1:")
    print("       no canonical frame, no PND quartic, no gradient of Weyl was needed.")

    passed = all(ok)
    print(f"\nBRIDGE ROUND 7: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          f"({sum(ok)}/{len(ok)}) — bumpy vs MN decided INEQUIVALENT at order 0 via the "
          "Ricci/Segre sector")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
