#!/usr/bin/env python3
"""Step 52 — STELLAR STRUCTURE: the engine leaves the black hole, builds a STAR.

Until now the engine has only ever handled black holes (vacuum/charged/rotating)
and cosmologies. Here it takes on MATTER that isn't a hole: a static relativistic
star — a self-gravitating ball of perfect fluid. From the standard interior metric

    ds² = −e^{2Φ(r)} dt² + dr²/(1 − 2m(r)/r) + r² dΩ²

with Φ(r) and m(r) FREE functions, the engine recovers the equations of stellar
structure — the abstractor move (cf. Friedmann §37, Kasner §47), now for stars:

  (A) the MASS FUNCTION  dm/dr = 4π r² ρ   (m(r) = mass inside radius r);
  (B) the POTENTIAL eq   dΦ/dr = (m + 4π r³ p) / (r(r − 2m));
  (C) BIANCHI ⇒ conservation: ∇_μ G^μ_r ≡ 0 expands to the hydrostatic balance,
      and for an ISOTROPIC (perfect-fluid) star gives the
          TOLMAN–OPPENHEIMER–VOLKOFF equation
          dp/dr = −(ρ + p)(m + 4π r³ p) / (r(r − 2m));
  (D) the NEWTONIAN limit (p≪ρ, m≪r): TOV → dp/dr = −ρ m/r², ordinary
      hydrostatic equilibrium — the relativistic corrections switch off.

Honest scope: TOV is textbook (1939). New is that our exact prove/discover/abstract
engine derives it with no black-hole machinery — breadth toward the general tool,
and the first time the engine describes matter holding ITSELF up against gravity.
8π=1 is NOT used here (kept explicit) so the 4π/8π factors read as the textbook.

Run:  .venv/bin/python scripts/52_stellar_structure.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry


def interior_geometry():
    """Static spherically symmetric interior metric with Φ(r), m(r) free."""
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    Phi = sp.Function("Phi")(r)
    m = sp.Function("m")(r)
    g = sp.diag(-sp.exp(2 * Phi), 1 / (1 - 2 * m / r), r**2, r**2 * sp.sin(th)**2)
    geo = Geometry(g, [t, r, th, ph])
    return geo, (t, r, th, ph), Phi, m


def einstein_mixed(geo):
    """G^μ_ν = R^μ_ν − ½ R δ^μ_ν."""
    G = geo.ricci - sp.Rational(1, 2) * geo.ricci_scalar * geo.g
    return sp.simplify(geo.ginv * G)


def covariant_div_r(Tud, geo, r_index=1):
    """(∇_μ T^μ_ν) for ν = r_index, T given mixed (T^μ_ν)."""
    n, x, Gamma = geo.n, geo.coords, geo.christoffel
    nu = r_index
    term = sum(sp.diff(Tud[mu, nu], x[mu]) for mu in range(n))
    term += sum(Gamma[mu][mu][lam] * Tud[lam, nu]
                for mu in range(n) for lam in range(n))
    term -= sum(Gamma[lam][nu][mu] * Tud[mu, lam]
                for mu in range(n) for lam in range(n))
    return sp.simplify(term)


def main():
    print("STELLAR STRUCTURE — the engine builds a relativistic star (TOV)\n")
    geo, (t, r, th, ph), Phi, m = interior_geometry()
    Gud = einstein_mixed(geo)

    # matter content read straight off the Einstein tensor (8πT^μ_ν = G^μ_ν)
    rho = sp.simplify(-Gud[0, 0] / (8 * sp.pi))   # T^t_t = −ρ
    p_r = sp.simplify(Gud[1, 1] / (8 * sp.pi))    # T^r_r = p_radial
    p_t = sp.simplify(Gud[2, 2] / (8 * sp.pi))    # T^θ_θ = p_tangential
    dPhi = sp.diff(Phi, r)
    dm = sp.diff(m, r)

    # (A) mass function  dm/dr = 4π r² ρ
    okA = sp.simplify(rho - dm / (4 * sp.pi * r**2)) == 0
    print("  (A) mass function:")
    print(f"      8πρ = {sp.simplify(8*sp.pi*rho)}")
    print(f"      ⇒ dm/dr = 4π r² ρ   {'✅' if okA else '❌'}  (m(r) = mass inside r)")

    # (B) potential equation  dΦ/dr = (m + 4π r³ p) / (r(r − 2m))
    rhsB = (m + 4 * sp.pi * r**3 * p_r) / (r * (r - 2 * m))
    okB = sp.simplify(dPhi - rhsB) == 0
    print("\n  (B) potential equation:")
    print(f"      dΦ/dr = (m + 4π r³ p) / (r(r − 2m))   {'✅' if okB else '❌'}")

    # (C) Bianchi ⇒ conservation ⇒ TOV.  ∇_μ G^μ_r ≡ 0 (engine self-test), and the
    #     SAME divergence of the perfect-fluid stress (p_r = p_t = p) is the
    #     hydrostatic balance p' + (ρ+p)Φ' = 0.
    div_G = covariant_div_r(Gud, geo)            # must vanish identically (Bianchi)
    bianchi_ok = sp.simplify(div_G) == 0
    print("\n  (C) Bianchi identity  ∇_μ G^μ_r =", sp.simplify(div_G),
          "✅" if bianchi_ok else "❌", "(engine self-consistency)")

    p = sp.Symbol("p")           # treat pressure as the field for the ODE statement
    rho_s = sp.Symbol("rho")
    # hydrostatic balance from conservation:  p' = −(ρ+p) Φ', then sub (B):
    tov_rhs = -(rho_s + p) * (m + 4 * sp.pi * r**3 * p) / (r * (r - 2 * m))
    # verify the perfect-fluid divergence really is p' + (ρ+p)Φ' (isotropic):
    pp = sp.Function("p")(r)
    rr = sp.Function("rho")(r)
    Tpf = sp.diag(-rr, pp, pp, pp)   # T^μ_ν for a perfect fluid
    div_pf = covariant_div_r(Tpf, geo)
    hydro = sp.diff(pp, r) + (rr + pp) * dPhi
    okC = bianchi_ok and sp.simplify(div_pf - hydro) == 0
    print("      perfect-fluid ∇_μ T^μ_r = p'(r) + (ρ+p) Φ'(r)   "
          f"{'✅' if sp.simplify(div_pf - hydro) == 0 else '❌'}")
    print("      ⇒ TOV:  dp/dr = −(ρ + p)(m + 4π r³ p) / (r(r − 2m))   "
          f"{'✅' if okC else '❌'}")
    print(f"              {sp.Eq(sp.Derivative(p, r), tov_rhs, evaluate=False)}")

    # (D) Newtonian limit, DERIVED (not assumed): post-Newtonian ordering — the
    #     compactness m/r is O(v²) and the pressure p/ρ is O(v⁴), one order smaller.
    #     Tag m→λm, p→λ²p and read the leading (λ¹) coefficient of the TOV RHS; the
    #     three relativistic factors (ρ+p, 4πr³p, 2m) all drop, leaving −ρ m/r².
    lam = sp.Symbol("lambda", positive=True)
    tov_lam = tov_rhs.subs({p: lam**2 * p, m: lam * m})
    tov_lead = sp.simplify(sp.diff(tov_lam, lam).subs(lam, 0))   # the λ¹ coefficient
    newt = -rho_s * m / r**2
    okD = sp.simplify(tov_lead - newt) == 0
    print("\n  (D) Newtonian limit (m/r = O(v²), p/ρ = O(v⁴)), leading order:")
    print(f"      dp/dr → {tov_lead}")
    print(f"      = −ρ m / r²   {'✅' if okD else '❌'}  (ordinary hydrostatic equilibrium)")

    passed = okA and okB and okC and okD
    print(f"\nSTELLAR STRUCTURE: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(mass function + potential + TOV + Newtonian limit, all from the metric)")
    print("  the engine now describes matter holding ITSELF up against gravity — a star,")
    print("  not a hole — and recovers the 1939 equation of relativistic stellar structure.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
