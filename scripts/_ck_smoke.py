#!/usr/bin/env python3
"""Smoke test — the riskiest joint: does the frame machinery survive an OFF-DIAGONAL chart?

Schwarzschild in (a) Schwarzschild coords [diagonal, easy] and (b) Painleve-Gullstrand
[off-diagonal: g_tr != 0, so Gram-Schmidt and PND alignment both get exercised].
Both must give Psi2 = -M/r^3 (the same invariant), everything else zero.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

import ck
from gr_engine import Geometry

t, r, th, ph = sp.symbols("t r theta phi", positive=True)
M = sp.Symbol("M", positive=True)

# declare the exterior region: outside the horizon, and 0 < theta < pi
ck.set_domain(sp.Q.positive(r - 2 * M), sp.Q.positive(sp.sin(th)))

print("SMOKE: frame machinery on diagonal vs off-diagonal charts (domain: r > 2M)\n")

# (a) Schwarzschild coordinates
f = 1 - 2 * M / r
gS = Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph])
print("(a) Schwarzschild coords")
tet = ck.null_tetrad(gS)
print(f"    tetrad normalization violations: {ck.check_tetrad(gS, tet) or 'NONE ✅'}")
C = ck.weyl_tensor(gS)
P = ck.psis(C, tet)
print(f"    raw Psi = {P}")
tet2, P2, ty, iso, note = ck.canonical_frame(gS, C, tet, verbose=True)
print(f"    canonical Psi = {P2}")
print(f"    type {ty}, isotropy {iso}")
print(f"    Psi2 == -M/r^3 ? {sp.simplify(P2[2] + M/r**3) == 0}")

# (b) Painleve-Gullstrand: ds^2 = -(1-2M/r)dT^2 + 2 sqrt(2M/r) dT dr + dr^2 + r^2 dOmega^2
print("\n(b) Painleve-Gullstrand coords (OFF-DIAGONAL -- the real test)")
sq = sp.sqrt(2 * M / r)
gPG = sp.Matrix([[-(1 - 2 * M / r), sq, 0, 0],
                 [sq, 1, 0, 0],
                 [0, 0, r**2, 0],
                 [0, 0, 0, r**2 * sp.sin(th)**2]])
gPGgeo = Geometry(gPG, [t, r, th, ph])
tetPG = ck.null_tetrad(gPGgeo)
print(f"    tetrad normalization violations: {ck.check_tetrad(gPGgeo, tetPG) or 'NONE ✅'}")
CPG = ck.weyl_tensor(gPGgeo)
PPG = ck.psis(CPG, tetPG)
print(f"    raw Psi = {PPG}")
tetPG2, PPG2, tyPG, isoPG, notePG = ck.canonical_frame(gPGgeo, CPG, tetPG, verbose=True)
print(f"    canonical Psi = {PPG2}")
print(f"    type {tyPG}, isotropy {isoPG}")
print(f"    Psi2 == -M/r^3 ? {sp.simplify(PPG2[2] + M/r**3) == 0}")
print("\nSMOKE DONE.")
