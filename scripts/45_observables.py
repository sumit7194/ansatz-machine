#!/usr/bin/env python3
"""Step 45 — OBSERVABLES: what a telescope actually sees (photon sphere + shadow).

A new lens, orthogonal to a metric's structure: the light that grazes a black hole.
For the static ansatz −f dt² + dr²/f + r²dΩ²:

  • PHOTON SPHERE — the radius where light orbits in a circle, the bright "light
    ring": circular null geodesics satisfy  2f(r) = r f'(r).
  • SHADOW — the dark silhouette an observer sees (the Event Horizon Telescope
    image of M87* / Sgr A*): set by the critical impact parameter
        b_c = r_ph / √f(r_ph).

Schwarzschild gives the textbook icons exactly — photon sphere at r = 3M, shadow
b_c = 3√3 M ≈ 5.196 M. Adding CHARGE shrinks both (the light ring tightens). This
turns "here's a metric" into "here's what you'd measure" — the observational face
of the engine.

Run:  .venv/bin/python scripts/45_observables.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import R_SYM

r = R_SYM


def photon_sphere_shadow(f):
    """Return [(r_ph, b_c), …] for the static lapse f: circular null orbits at
    2f = r f', shadow b_c = r_ph/√f(r_ph). Real radii only."""
    cond = sp.numer(sp.together(sp.simplify(2 * f - r * sp.diff(f, r))))
    out = []
    try:
        roots = sp.solve(cond, r)
    except Exception:
        return out
    for rp in roots:
        if rp.is_real is False or (rp.is_positive is False):
            continue
        fp = sp.simplify(f.subs(r, rp))
        b = sp.simplify(rp / sp.sqrt(fp)) if fp != 0 and fp.is_positive is not False else None
        out.append((sp.simplify(rp), b))
    return out


def main():
    M, Q = sp.symbols("M Q", positive=True)
    print("OBSERVABLES — the light ring and the black-hole shadow\n")

    # Schwarzschild: the textbook icons, exact
    sch = photon_sphere_shadow(1 - 2 * M / r)
    rp_s = [rp for rp, _ in sch if sp.simplify(rp - 3 * M) == 0]
    b_s = [b for rp, b in sch if sp.simplify(rp - 3 * M) == 0]
    ok_sch = bool(rp_s) and bool(b_s) and sp.simplify(b_s[0] - 3 * sp.sqrt(3) * M) == 0
    print("  Schwarzschild:")
    print(f"     photon sphere r_ph = 3M,  shadow b_c = {b_s[0] if b_s else '?'}  "
          f"(= 3√3 M ≈ 5.196 M)   {'✅' if ok_sch else '❌'}")

    # Reissner–Nordström: charge shrinks the light ring
    rn = photon_sphere_shadow(1 - 2 * M / r + Q**2 / r**2)
    outer = max((rp for rp, _ in rn), key=lambda e: sp.simplify(e.subs({M: 1, Q: sp.Rational(1, 2)})))
    rp_num = float(outer.subs({M: 1, Q: sp.Rational(1, 2)}))
    print("\n  Reissner–Nordström (charged):")
    print(f"     outer photon sphere r_ph = {outer}")
    print(f"     at M=1, Q=1/2:  r_ph = {rp_num:.4f} M  (< 3M — charge tightens the light ring)")
    ok_rn = rp_num < 3.0

    # the shadow shrinks with charge too (numeric)
    fRN = (1 - 2 * M / r + Q**2 / r**2)
    b_rn = (outer / sp.sqrt(fRN.subs(r, outer))).subs({M: 1, Q: sp.Rational(1, 2)})
    b_num = float(sp.simplify(b_rn))
    print(f"     shadow b_c = {b_num:.4f} M   (< 3√3 ≈ 5.196 — a smaller dark disk than Schwarzschild)")
    ok_shadow = b_num < float(3 * sp.sqrt(3))

    passed = ok_sch and ok_rn and ok_shadow
    print("\n  the engine now reports what an observer would SEE — the EHT light ring")
    print("  and shadow — straight from the metric; charge makes both smaller.")
    print(f"\nOBSERVABLES: {'PASSED ✅' if passed else 'FAILED ❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
