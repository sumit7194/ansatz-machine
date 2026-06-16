#!/usr/bin/env python3
"""Step 38 — "IMPOSSIBLE" SPACETIMES: the engine proves they need exotic matter.

First breadth experiment in attack angle #3. Wormholes and warp drives are valid
geometries — the real question is how unphysical the matter that sources them must
be. This is the energy-condition lens (36) in its most dramatic setting, and our
signature move (prove an impossibility) applied to faster-than-light travel.

Two famous cases, both shown EXACTLY to demand exotic (energy-condition-violating)
matter:

  (1) MORRIS–THORNE WORMHOLE  ds² = −dt² + dr²/(1−b(r)/r) + r²dΩ².
      The engine reads the stress-energy off the Einstein tensor and PROVES the
      no-go: at the throat (b=r₀, flaring-out ⇒ b'(r₀)<1),
          ρ + p_r = (b'(r₀) − 1)/(8π r₀²) < 0,
      so the null energy condition is necessarily violated — a traversable
      wormhole requires exotic matter, derived symbolically, for ANY shape b(r).

  (2) ALCUBIERRE WARP DRIVE  ds² = −dt² + (dx − v f(r_s) dt)² + dy² + dz².
      The Eulerian energy density (lapse 1 ⇒ ρ = G^{00}/8π) comes out
          ρ = −v²(y²+z²) f'(r_s)² / (32π r_s²)  ≤ 0,
      manifestly negative — the warp bubble needs negative energy. (This is the
      exact computation that has repeatedly refuted "positive-energy warp" claims;
      our engine does it with no numerical error.)

Honest scope: both results are known; the point is the engine derives them
exactly and uniformly, the "claim-checker / prove-the-no-go" capability in a
domain where claims get made and busted. Breadth, toward the general tool.

Run:  .venv/bin/python scripts/38_exotic_spacetimes.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry, R_SYM


def morris_thorne():
    """Returns (ρ, p_r, p_t) for the zero-tidal Morris–Thorne wormhole, b(r) free."""
    r = R_SYM
    t, th, ph = sp.symbols("t theta phi", real=True)
    b = sp.Function("b", positive=True)
    g = sp.diag(-1, 1 / (1 - b(r) / r), r**2, r**2 * sp.sin(th)**2)
    geo = Geometry(g, [t, r, th, ph])
    G = geo.ricci - sp.Rational(1, 2) * geo.ricci_scalar * geo.g
    Gmix = sp.simplify(geo.ginv * G)
    rho = sp.simplify(-Gmix[0, 0] / (8 * sp.pi))
    p_r = sp.simplify(Gmix[1, 1] / (8 * sp.pi))
    p_t = sp.simplify(Gmix[2, 2] / (8 * sp.pi))
    return b, rho, p_r, p_t


def alcubierre_rho():
    """Eulerian energy density of the Alcubierre warp drive (ship at origin)."""
    t, x, y, z = sp.symbols("t x y z", real=True)
    v = sp.Symbol("v", positive=True)
    f = sp.Function("f")
    rs = sp.sqrt(x**2 + y**2 + z**2)
    F = f(rs)
    g = sp.Matrix([
        [-(1 - v**2 * F**2), -v * F, 0, 0],
        [-v * F, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])
    geo = Geometry(g, [t, x, y, z])
    G = geo.ricci - sp.Rational(1, 2) * geo.ricci_scalar * geo.g
    ginv = geo.ginv
    Guu00 = sum(ginv[0, a] * ginv[0, c] * G[a, c] for a in range(4) for c in range(4))
    return x, y, z, v, f, rs, sp.simplify(Guu00 / (8 * sp.pi))


def main():
    r = R_SYM
    print("'IMPOSSIBLE' SPACETIMES — the engine proves they need exotic matter\n")

    # (1) Morris–Thorne wormhole
    b, rho, p_r, p_t = morris_thorne()
    nec = sp.simplify(rho + p_r)                       # = (r b' − b)/(8π r³)
    r0, bp = sp.symbols("r0 bprime", positive=True)
    nec_throat = nec.subs([(sp.Derivative(b(r), r), bp), (b(r), r)]).subs(r, r0)
    nec_throat = sp.simplify(nec_throat)               # = (bprime − 1)/(8π r0²)
    expected = (bp - 1) / (8 * sp.pi * r0**2)
    okMT_form = (sp.simplify(nec_throat - expected) == 0)
    # flaring-out b'(r0) < 1 ⇒ negative. Demonstrate at a sample b'=1/2:
    nec_sample = nec_throat.subs(bp, sp.Rational(1, 2))
    okMT_neg = (nec_sample < 0)
    # concrete shape b = r0²/r
    nec_ex = sp.simplify(nec.subs(b(r), r0**2 / r).doit())
    okMT_ex = (sp.simplify(nec_ex.subs(r, r0)) < 0)
    print("  (1) Morris–Thorne wormhole:")
    print(f"      ρ={rho},  p_r={p_r}")
    print(f"      NEC ρ+p_r at throat = {nec_throat}")
    print(f"        flaring-out b'(r₀)<1 ⇒ NEGATIVE (e.g. b'=½ → {nec_sample}) "
          f"⇒ NEC VIOLATED ⇒ exotic matter FORCED  {'✅' if okMT_form and okMT_neg else '❌'}")
    print(f"        example b=r₀²/r: ρ+p_r={nec_ex} (<0 everywhere)  {'✓' if okMT_ex else '✗'}")

    # (2) Alcubierre warp drive
    x, y, z, v, f, rs, rho_w = alcubierre_rho()
    xi = sp.Symbol("xi")
    fp = sp.Subs(sp.Derivative(f(xi), xi), xi, rs)
    textbook = -(v**2 / (32 * sp.pi)) * (y**2 + z**2) / rs**2 * fp**2
    okW = (sp.simplify(rho_w - textbook) == 0)
    print("\n  (2) Alcubierre warp drive:")
    print(f"      Eulerian ρ = {rho_w}")
    print(f"        = −v²(y²+z²)f'(r_s)²/(32π r_s²)  ≤ 0  (manifestly negative) "
          f"⇒ needs NEGATIVE energy  {'✅' if okW else '❌'}")

    passed = okMT_form and okMT_neg and okMT_ex and okW
    print(f"\nEXOTIC SPACETIMES: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(wormhole NEC no-go + warp negative energy, both exact)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
