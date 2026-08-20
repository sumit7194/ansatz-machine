#!/usr/bin/env python3
"""The rank-4 POSITIVE CONTROL: Cariglia & Galajinsky's 5D oxidation (arXiv:1503.02162, Eq. 26).

WHY A CONTROL AT ALL. Rank 4 is the last piece of §85's caveat ("a higher-order QUARTIC Killing
tensor isn't excluded"). A null there from an instrument never shown to find a rank-4 tensor when
one exists would be worth nothing -- rule 8.

TWO WARNINGS FROM tabula, BOTH ACTED ON:
  1. DERIVE the target from their Eq (24), do NOT transcribe Eq (29). Their PDF-to-text collapsed
     an index (K_ttxw read as K_tttw) and the transcribed tensor is NOT conserved -- drift 0.30.
     The published paper is correct (confirmed independently from the HTML rendering); the hazard
     is the extraction. A silently wrong target reads as "the control failed" or, far worse, as
     "no rank-4 KT exists".
  2. VERIFY THE TARGET IS CONSERVED before it gates anything -- the same discipline as verifying a
     transcribed metric is Ricci-flat before calling it a spacetime. Our Taub-NUT entry was neither
     Taub-NUT nor vacuum and a nine-hour hang hid that.

    Eq (26):  dtau^2 = -2(alpha*y + gamma/sqrt(x) - (alpha*x)^2/2) dt^2 + 2 dt ds + 2 dx dy
                       + 2 alpha*x dt dw + dw^2
The sqrt(x) is removed by x = X^2 (a Killing tensor is chart-independent, so this costs nothing),
giving 2 dx dy = 4 X dX dy and gamma/sqrt(x) = gamma/X.

Coordinates ordered so the two DEPENDENT ones sit at indices 1 and 2, matching the prover:
    (t, X, y, s, w)   -- metric depends on X and y only; t, s, w are ignorable (3 Killing vectors).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
from gr_engine import Geometry

t, X, y, s, w = sp.symbols("t X y s w", real=True)
ALPHA, GAMMA = sp.Integer(1), sp.Integer(1)


def cg5d_metric(alpha=ALPHA, gamma=GAMMA, extra=0):
    """Lower-index metric in (t, X, y, s, w). `extra` adds a term to U for the KNOWN-FAIL control."""
    U = alpha * y + gamma / X - (alpha * X**2)**2 / 2 + extra
    g = sp.zeros(5, 5)
    g[0, 0] = -2 * U
    g[0, 3] = g[3, 0] = 1                       # 2 dt ds
    g[0, 4] = g[4, 0] = alpha * X**2            # 2 alpha x dt dw, with x = X^2
    g[1, 2] = g[2, 1] = 2 * X                   # 2 dx dy = 4 X dX dy  -> g_Xy = 2X
    g[4, 4] = 1                                 # dw^2
    return g


if __name__ == "__main__":
    print("CG 5D OXIDATION -- substrate check before any control use\n")
    g = cg5d_metric()
    geo = Geometry(g, [t, X, y, s, w])
    pts = [{X: sp.Integer(2), y: sp.Integer(3)}, {X: sp.Integer(5), y: sp.Rational(-7, 2)}]
    mx = 0.0
    for pt in pts:
        for a in range(5):
            for b in range(5):
                v = sp.simplify(geo.ricci[a, b].subs(pt))
                mx = max(mx, abs(float(v)) if v.is_number else 1e99)
    print(f"  (A) Ricci-flat?  max |R_ab| = {mx:.3e}   "
          f"{'VACUUM ✓' if mx < 1e-12 else '*** NOT VACUUM ***'}")

    # KNOWN-FAIL: the paper's own Eq (4) says a non-additive term c*x*y in U sources R_tt = 2c.
    # A substrate check that cannot fail is not a check (rule 1).
    c = sp.Rational(1, 4)
    g2 = cg5d_metric(extra=c * X**2 * y)
    geo2 = Geometry(g2, [t, X, y, s, w])
    rtt = sp.simplify(geo2.ricci[0, 0].subs({X: sp.Integer(2), y: sp.Integer(3)}))
    others = max(abs(float(sp.simplify(geo2.ricci[a, b].subs({X: sp.Integer(2), y: sp.Integer(3)}))))
                 for a in range(5) for b in range(5) if (a, b) != (0, 0))
    print(f"  (B) KNOWN-FAIL, U += {c}*x*y:  R_tt = {float(rtt):.4f}  vs the paper's 2c = {float(2*c):.4f}"
          f"   {'✓' if abs(float(rtt) - float(2*c)) < 1e-9 else '✗'}")
    print(f"      every other component: max {others:.3e}   {'✓ isolated' if others < 1e-12 else '✗'}")
