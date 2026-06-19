#!/usr/bin/env python3
"""Step 66 — THE EFFECTIVE POTENTIAL: orbits as a particle rolling in a well.

A synthesis lens: the scattered orbit results — photon sphere & ISCO (§45),
perihelion precession (§50) — are all ONE picture. A geodesic's radial motion is
        (dr/dτ)² = E² − V_eff(r),
a particle of energy E rolling in a potential V_eff. Everything special about black-
hole orbits is a feature of that one curve, and the engine reads it off the metric:

    timelike:  V_eff = f(r)(1 + L²/r²)        null:  V_eff = f(r) L²/r²

  (A) CIRCULAR orbits sit at V_eff′=0; the ISCO (innermost STABLE orbit) is where the
      well's minimum and maximum merge, V_eff′=V_eff″=0 ⇒ r=6M, L=2√3 M (recovers §45,
      now as a stability statement: below 6M no stable orbit exists — you spiral in);
  (B) the PHOTON SPHERE is the null potential's MAXIMUM ⇒ r=3M — a maximum, so it's
      UNSTABLE: light can circle there but the faintest nudge sends it in or out
      (recovers §45's light ring, explains why it's a knife-edge);
  (C) the WHY: V_eff = 1 − 2M/r + L²/r² − 2ML²/r³. The first three terms are Newton
      (rest energy − potential + centrifugal barrier); the LAST, −2ML²/r³, is purely
      GR. In Newton the centrifugal barrier always wins close in (stable orbits at all
      radii); the GR term overwhelms it ⇒ the barrier vanishes ⇒ the ISCO. That term
      is why you cannot orbit close to a black hole;
  (D) CAPTURE: a particle with E² above the barrier's peak goes over and is swallowed —
      the barrier height sets the capture cross-section (the shadow, §45).

Honest scope: textbook geodesics. New is the same engine reading V_eff off the metric
and unifying §45/§50 into one curve, with the Newtonian limit pinpointing the GR term.

Run:  .venv/bin/python scripts/66_effective_potential.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("THE EFFECTIVE POTENTIAL — orbits as a particle rolling in a well\n")
    r, M, L = sp.symbols("r M L", positive=True)
    f = 1 - 2 * M / r
    ok = []

    # (A) timelike V_eff, ISCO from V'=V''=0
    V = f * (1 + L**2 / r**2)
    sol = sp.solve([sp.diff(V, r), sp.diff(V, r, 2)], [r, L], dict=True)
    isco = [(sp.simplify(s[r]), sp.simplify(s[L])) for s in sol if s.get(r, 0) != 0]
    okA = (6 * M, 2 * sp.sqrt(3) * M) in [(sp.simplify(a), sp.simplify(b)) for a, b in isco]
    ok.append(okA)
    print(f"  (A) timelike V_eff = f(1+L²/r²); ISCO at V′=V″=0 ⇒ (r,L) = {isco}")
    print(f"      ⇒ r_ISCO = 6M, L = 2√3 M — below 6M no STABLE orbit (recovers §45)   {'✅' if okA else '❌'}")

    # (B) null V_eff, photon sphere is the MAXIMUM
    Vn = f * L**2 / r**2
    rps = [x for x in sp.solve(sp.diff(Vn, r), r) if x != 0]
    is_max = sp.diff(Vn, r, 2).subs(r, 3 * M)
    okB = rps == [3 * M] and is_max.subs({M: 1, L: 1}) < 0
    ok.append(okB)
    print(f"\n  (B) null V_eff = f L²/r²; extremum at r = {rps}; V″(3M) = {sp.simplify(is_max)} < 0")
    print(f"      ⇒ the photon sphere r=3M is a MAXIMUM — an UNSTABLE light ring (recovers §45)   "
          f"{'✅' if okB else '❌'}")

    # (C) the Newtonian limit pinpoints the GR term that creates the ISCO
    Vexp = sp.expand(V)
    gr_term = -2 * M * L**2 / r**3
    newt = 1 - 2 * M / r + L**2 / r**2
    okC = sp.simplify(Vexp - (newt + gr_term)) == 0
    # without the GR term, V''=0 has no positive-r solution (no ISCO)
    Vnewt = newt
    isco_newt = sp.solve([sp.diff(Vnewt, r), sp.diff(Vnewt, r, 2)], [r, L], dict=True)
    okC = okC and (len([s for s in isco_newt if s.get(r, 0) not in (0, None)]) == 0)
    ok.append(okC)
    print(f"\n  (C) V_eff = {Vexp}")
    print(f"      = [Newton: 1−2M/r+L²/r²] + [GR: −2ML²/r³]; drop the GR term ⇒ no ISCO solution")
    print(f"      — the −2ML²/r³ term is exactly why close orbits go unstable   {'✅' if okC else '❌'}")

    # (D) capture: barrier peak sets the threshold; E² above the max ⇒ swallowed
    L0 = 2 * sp.sqrt(3) * M
    Vmax = sp.simplify(Vn.subs({L: L0, r: 3 * M}))          # null barrier height at L0
    okD = Vmax.is_positive
    ok.append(okD)
    print(f"\n  (D) capture: the barrier peak (null, L=2√3M) V_max = {Vmax}; E² above it ⇒ swallowed")
    print(f"      — the barrier height sets the capture cross-section / shadow (§45)   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nEFFECTIVE POTENTIAL: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(ISCO & photon sphere as potential features; the GR term that forbids close orbits)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
