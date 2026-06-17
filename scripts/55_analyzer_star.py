#!/usr/bin/env python3
"""Step 55 — THE GENERAL ANALYZER REACHES A STAR (and an honest boundary).

Tonight's stellar work (§52–54) was done with focused scripts. This battery checks
the thing that actually matters per the project's north star: the ONE general tool —
analyze() — reaches the new domain too. Point it at a star (the constant-density
interior Schwarzschild sphere, a perfect-fluid ball, NOT a black hole) and read its
report card. With no stellar-specific code, the general analyzer should get the
STRUCTURE right:

  • made of      : perfect fluid (isotropic)   — it detects p_r = p_t;
  • density ρ    : 3M/(4πR³), constant          — exactly the uniform density;
  • symmetries   : ∂/∂t, ∂/∂φ                   — static + axisymmetric;
  • singularities: none                          — a regular star, no curvature blow-up;
  • signature flip: False                        — time stays timelike: a STAR, not a hole.

An HONEST boundary, surfaced AND then resolved: from the bare metric the report's
physical? verdict is UNKNOWN — the interior's √(1−2Mr²/R³) is real only for r ≤ R, so the
analyzer's domain-blind sign sampler can't certify the energy conditions. That's a true
three-valued UNKNOWN, not a unphysical verdict. The fix is to give the tool the missing
fact: `analyze(metric, coords, domain={r: (0, R)})` bounds where the radial coordinate is
sampled, and the SAME general tool then certifies the interior PHYSICAL (NEC/WEC/DEC/SEC all
hold). So this battery shows both the boundary and its resolution — the general analyzer
made domain-aware enough to handle interior solutions, not just global ones.

Run:  .venv/bin/python scripts/55_analyzer_star.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyzer import UNKNOWN, analyze


def interior_metric(M, R):
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    sj = sp.sqrt(1 - 2 * M * r**2 / R**3)
    sR = sp.sqrt(1 - 2 * M / R)
    gtt = -(sp.Rational(3, 2) * sR - sp.Rational(1, 2) * sj) ** 2
    g = sp.diag(gtt, 1 / (1 - 2 * M * r**2 / R**3), r**2, r**2 * sp.sin(th) ** 2)
    return g, (t, r, th, ph), r


def main():
    print("THE GENERAL ANALYZER REACHES A STAR (perfect-fluid interior)\n")
    M, R = sp.Rational(1, 5), sp.Integer(1)        # compactness M/R = 0.2 (stable)
    g, coords, r = interior_metric(M, R)
    rep = analyze(g, coords)

    # --- the general tool gets the STRUCTURE right, no stellar-specific code ---
    made = rep["made_of"]
    okFluid = made.startswith("perfect fluid")
    rho_const = sp.simplify(rep["rho"] - 3 * M / (4 * sp.pi * R**3)) == 0
    sym = {str(s) for s in rep["symmetries"]}
    okSym = {"t", "phi"} <= sym
    okSing = rep["singularities"] == []
    flip = rep.get("causal", {}).get("signature_flip", None)
    okStar = flip is False                          # no horizon ⇒ a star, not a hole
    okSourced = "sourced" in rep["solves_einstein"]

    print(f"  made of       : {made[:34]}...   {'✅ perfect fluid' if okFluid else '❌'}")
    print(f"  density ρ     : {rep['rho']}   {'✅ = 3M/4πR³ (constant)' if rho_const else '❌'}")
    print(f"  symmetries    : {', '.join(sorted(sym))}   {'✅ static + axisymmetric' if okSym else '❌'}")
    print(f"  singularities : {rep['singularities']}   {'✅ regular (no blow-up)' if okSing else '❌'}")
    print(f"  signature flip: {flip}   {'✅ time stays timelike → a STAR, not a hole' if okStar else '❌'}")
    print(f"  solves EFE    : {rep['solves_einstein']}   {'✅ matter' if okSourced else '❌'}")

    # --- the HONEST boundary: physical? is UNKNOWN from the bare metric ---
    phys = rep["physical"]
    okHonest = phys is UNKNOWN
    print(f"\n  physical?     : {phys}   "
          f"{'✅ honestly UNKNOWN (domain-blind from a bare metric)' if okHonest else '❌'}")

    # --- the RESOLUTION: tell analyze() the domain (r ≤ R) and it certifies ---
    # The interior is real only inside the star; with that bound the same general
    # tool certifies the energy conditions instead of returning UNKNOWN.
    rep_d = analyze(g, coords, domain={r: (0, R)})
    ec_d = rep_d["energy_conditions"]
    okCertified = rep_d["physical"] is True
    print(f"\n  …now WITH domain r∈(0,R):")
    print(f"  physical?     : {rep_d['physical']}   "
          f"[" + ", ".join(f"{k}:{ec_d[k]}" for k in ('NEC', 'WEC', 'DEC', 'SEC')) + "]   "
          f"{'✅ certified PHYSICAL' if okCertified else '❌'}")
    print("     ⇒ the UNKNOWN was missing domain knowledge (r≤R), not a real failure;")
    print("       analyze(metric, coords, domain={r:(0,R)}) now certifies the interior.")

    passed = all([okFluid, rho_const, okSym, okSing, okStar, okSourced, okHonest, okCertified])
    print(f"\nANALYZER-STAR: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(the one general tool reaches stars — structure read; boundary found AND resolved "
          "via domain-aware analyze())")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
