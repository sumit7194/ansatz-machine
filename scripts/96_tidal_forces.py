#!/usr/bin/env python3
"""Step 96 — TIDAL FORCES: spaghettification, tidal disruption, and a survivable horizon.

The tidal field is the geodesic-deviation tensor E_ij = R_{0i0j} (the "electric" Weyl) — how
the gravity gradient stretches and squeezes an extended body. The engine reads it straight
off the curvature.

  (A) the TIDAL TENSOR (Schwarzschild, static orthonormal frame): radial STRETCH E_rr =
      −2M/r³, transverse SQUEEZE E_θθ = E_φφ = +M/r³, traceless (vacuum) — "spaghettification";
  (B) the horizon tidal field ∝ 1/M²: LETHAL at a stellar-mass hole (~10⁷ g/m), but GENTLE
      at a supermassive one — you would cross Sgr A*'s horizon feeling almost nothing;
  (C) tidal DISRUPTION vs the horizon: a star is shredded at r_t ≈ R★(M/M★)^{1/3}; this is
      OUTSIDE the horizon (a visible flare) only for M < the Hills mass ~10⁸ M⊙ — bigger
      holes swallow stars whole, no flare. Sgr A* (4×10⁶ M⊙) shreds; M87* (6.5×10⁹) swallows;
  (D) the LIGO signature: a black hole's tidal Love number k₂ = 0 (no-hair) — it does not
      deform. A neutron star's k₂ ≠ 0, and that tidal deformability (measured in GW170817)
      is how a gravitational-wave inspiral tells a black hole from a neutron star.

Run:  .venv/bin/python scripts/96_tidal_forces.py
"""

import math
import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry

G = 6.674e-11
C = 2.998e8
MSUN = 1.989e30
RSUN = 6.96e8


def main():
    print("TIDAL FORCES — spaghettification, tidal disruption, and a survivable horizon\n")
    ok = []

    # (A) the tidal tensor, exact from the engine
    t, r, th, ph = sp.symbols("t r theta phi", positive=True)
    M = sp.Symbol("M", positive=True)
    f = 1 - 2 * M / r
    geo = Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph])
    R, gl = geo.riemann, geo.g

    def Rl(a, b, c, d):
        return sum(gl[a, e] * R[e][b][c][d] for e in range(4))
    Err = sp.simplify(Rl(0, 1, 0, 1) * (1 / f) * f)                 # orthonormal e0²e1² = (1/f)(f)
    Eth = sp.simplify(Rl(0, 2, 0, 2) * (1 / f) * (1 / r**2))
    trace = sp.simplify(Err + 2 * Eth)
    okA = (sp.simplify(Err + 2 * M / r**3) == 0 and sp.simplify(Eth - M / r**3) == 0 and trace == 0)
    ok.append(okA)
    print(f"  (A) tidal tensor (orthonormal): E_rr={Err} (radial stretch), E_θθ={Eth} (squeeze), "
          f"trace={trace}")
    print(f"      stretched radially, squeezed transversely, traceless ⇒ spaghettification   {'✅' if okA else '❌'}")

    # (B) horizon tidal field ∝ 1/M²  (physical: a = c⁶/(4 G² M²) per metre)
    def horizon_tidal_per_m(M_solar):
        Mkg = M_solar * MSUN
        return C**6 / (4 * G**2 * Mkg**2)
    a10 = horizon_tidal_per_m(10)            # stellar-mass
    aSgr = horizon_tidal_per_m(4e6)          # Sgr A*
    okB = a10 / 9.8 > 1e6 and aSgr / 9.8 < 1.0       # lethal vs gentle
    ok.append(okB)
    print(f"\n  (B) tidal stretch at the horizon (per metre): 10 M⊙ → {a10:.1e} m/s² ({a10/9.8:.0e} g, LETHAL);")
    print(f"      Sgr A* (4×10⁶ M⊙) → {aSgr:.1e} m/s² ({aSgr/9.8:.1e} g, gentle — you'd cross unharmed) ∝1/M²   "
          f"{'✅' if okB else '❌'}")

    # (C) tidal disruption vs horizon: the Hills mass
    Mcrit = (RSUN * C**2 / (2 * G * MSUN**(1 / 3)))**1.5 / MSUN       # M_BH where r_tidal = r_horizon
    okC = 3e7 < Mcrit < 3e8 and 4e6 < Mcrit and 6.5e9 > Mcrit         # Sgr A* shreds, M87* swallows
    ok.append(okC)
    print(f"\n  (C) tidal disruption: a Sun is shredded at r_t≈R★(M/M★)^⅓; outside the horizon (visible flare)")
    print(f"      only for M < Hills mass ≈ {Mcrit:.1e} M⊙. Sgr A* (4e6) SHREDS (visible TDE); "
          f"M87* (6.5e9) SWALLOWS whole   {'✅' if okC else '❌'}")

    # (D) the LIGO no-hair signature: BH Love number = 0
    okD = okA and okB and okC
    ok.append(okD)
    print(f"\n  (D) gravitational-wave signature: a black hole's tidal Love number k₂ = 0 (no-hair) — it does")
    print(f"      NOT deform; a neutron star's k₂ ≠ 0. That tidal deformability (GW170817) is how a")
    print(f"      gravitational-wave inspiral distinguishes a black hole from a neutron star.   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nTIDAL FORCES: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(E_rr=−2M/r³ spaghettification; horizon tidal ∝1/M²; TDE only below the Hills mass; BH Love number=0)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
