#!/usr/bin/env python3
"""Step 60 — FRAME DRAGGING & THE ERGOSPHERE: how a spinning black hole drags space.

A different flavour from the recent curvature/symmetry lenses: the purely ROTATIONAL
structure of Kerr. A spinning mass drags spacetime around with it (the Lense–Thirring
effect), and close in there is a region — the ERGOSPHERE — where the dragging is so
strong that NO observer can stand still: you are forced to orbit with the hole. It is
also where you can mine the hole's spin energy (the Penrose process). All exact and
algebraic from the metric — now in the analyzer report card (`analyzer.frame_dragging`).

  (A) the ERGOSPHERE (static limit, g_tt=0): r = M + √(M²−a²cos²θ), which lies OUTSIDE
      the horizon r₊ = M+√(M²−a²) (they touch at the poles; at the equator it reaches
      2M). Inside it g_tt>0 ⇒ ∂_t is spacelike ⇒ no static observers — you MUST co-rotate;
  (B) FRAME DRAGGING ω = −g_tφ/g_φφ — the angular velocity dragging is rigid at the
      horizon: ω(r₊) = Ω_H = a/(r₊²+a²), everything co-rotates with the hole there;
  (C) far away ω → 2J/r³ with J=Ma (Lense–Thirring) — the same dragging Gravity Probe B
      / LARES measured around the spinning Earth;
  (D) the PENROSE PROCESS: the irreducible mass M_irr=√(A/16π)=√(Mr₊/2) is the part that
      CAN'T be extracted; for an extremal hole (a=M) M_irr=M/√2, so up to 1−1/√2 ≈ 29%
      of the mass is extractable spin energy;
  (E) no spin (a→0): the ergosphere collapses onto the horizon and ω→0 — frame dragging
      is purely a rotational effect.

Honest scope: textbook Kerr (Boyer–Lindquist). New is the same engine reading the
rotational structure straight off the metric, beside everything else.

Run:  .venv/bin/python scripts/60_frame_dragging.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry
from analyzer import frame_dragging


def main():
    print("FRAME DRAGGING & THE ERGOSPHERE — how a spinning black hole drags space\n")
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    M, a = sp.symbols("M a", positive=True)
    Sig = r**2 + a**2 * sp.cos(th)**2
    s2 = sp.sin(th)**2
    g = sp.zeros(4)
    g[0, 0] = -(1 - 2 * M * r / Sig)
    g[0, 3] = g[3, 0] = -2 * M * r * a * s2 / Sig
    g[1, 1] = Sig / (r**2 - 2 * M * r + a**2)
    g[2, 2] = Sig
    g[3, 3] = (r**2 + a**2 + 2 * M * r * a**2 * s2 / Sig) * s2
    geo = Geometry(g, [t, r, th, ph])
    fd = frame_dragging(geo)
    rplus = M + sp.sqrt(M**2 - a**2)
    ok = []

    # (A) ergosphere outside the horizon; g_tt>0 inside
    ergo_outer = M + sp.sqrt(M**2 - a**2 * sp.cos(th)**2)
    okA1 = any(sp.simplify(e - ergo_outer) == 0 for e in fd["ergosphere"])
    eq = sp.simplify(ergo_outer.subs(th, sp.pi / 2))          # equatorial static limit
    okA2 = (eq == 2 * M) and sp.simplify(ergo_outer.subs(th, 0) - rplus) == 0
    gtt_in = g[0, 0].subs({r: sp.Rational(3, 2), th: sp.pi / 2, a: sp.Rational(6, 10), M: 1})
    okA3 = float(gtt_in) > 0
    ok += [okA1, okA2, okA3]
    print(f"  (A) ergosphere (g_tt=0): r = {ergo_outer}")
    print(f"      = 2M at equator, = r₊ at poles ⇒ wraps OUTSIDE the horizon   {'✅' if okA1 and okA2 else '❌'}")
    print(f"      g_tt = {float(gtt_in):.3f} > 0 just inside (a=.6) ⇒ no static observers, must co-rotate   "
          f"{'✅' if okA3 else '❌'}")

    # (B) frame dragging ω, rigid co-rotation at the horizon
    omega = fd["omega"]
    omega_H = sp.simplify(omega.subs(r, rplus))
    Om_known = sp.simplify(a / (rplus**2 + a**2))
    okB = sp.simplify(omega_H - Om_known) == 0
    ok.append(okB)
    print(f"\n  (B) frame dragging ω = −g_tφ/g_φφ;  ω(r₊) = Ω_H = a/(r₊²+a²)   {'✅ rigid co-rotation' if okB else '❌'}")

    # (C) Lense–Thirring far field ω → 2J/r³ (J = Ma)
    lead = sp.simplify(sp.limit(omega * r**3, r, sp.oo))
    okC = sp.simplify(lead - 2 * M * a * s2) == 0 or sp.simplify(lead - 2 * M * a) == 0
    ok.append(okC)
    print(f"\n  (C) far field: ω·r³ → {lead}  ⇒ ω ~ 2J/r³, J=Ma (Lense–Thirring; Gravity Probe B)   "
          f"{'✅' if okC else '❌'}")

    # (D) Penrose process: irreducible mass and extractable spin energy
    area = sp.simplify(4 * sp.pi * (rplus**2 + a**2))          # Kerr horizon area
    M_irr = sp.sqrt(area / (16 * sp.pi))
    M_irr_ext = sp.simplify(M_irr.subs(a, M))                  # extremal a=M
    frac = sp.simplify(1 - M_irr_ext / M)
    okD = sp.simplify(M_irr_ext - M / sp.sqrt(2)) == 0 and abs(float(frac) - 0.2929) < 1e-3
    ok.append(okD)
    print(f"\n  (D) Penrose process: M_irr = √(A/16π) = {sp.simplify(M_irr)}")
    print(f"      extremal a=M ⇒ M_irr = {M_irr_ext} = M/√2 ⇒ up to {float(frac)*100:.1f}% of M is "
          f"extractable spin energy   {'✅' if okD else '❌'}")

    # (E) no spin ⇒ no ergosphere, no dragging
    okE = (sp.simplify(ergo_outer.subs(a, 0) - 2 * M) == 0
           and sp.simplify(omega.subs(a, 0)) == 0)
    ok.append(okE)
    print(f"\n  (E) a→0: ergosphere → 2M = horizon, ω → {sp.simplify(omega.subs(a,0))}   "
          f"{'✅ no spin, no dragging' if okE else '❌'}")

    passed = all(ok)
    print(f"\nFRAME DRAGGING: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(ergosphere, rigid horizon co-rotation, Lense–Thirring, 29% Penrose energy)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
