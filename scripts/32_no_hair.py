#!/usr/bin/env python3
"""Step 32 — NO-HAIR, rediscovered AND proven by the engine.

The dual of Reissner–Nordström (28). Give the engine an electromagnetic
source and it BUILDS a charged hole — it gains a Q²/r² term. Give it a
minimally-coupled massless scalar on the SAME canonical static ansatz
(angular part exactly r²) and it can build nothing new: the only solution is
φ = const, f = Schwarzschild. That is the no-hair theorem.

The engine establishes it two ways.

  (1) PROOF (exact, no assumption on φ's form). With f(r), φ(r) symbolic:
        • the angular Einstein equation has ZERO scalar source
          (φ = φ(r) ⇒ ∂_θφ = 0), so  R_θθ = 1 − f − r f' = 0  ⇒  f = 1 + C/r
          — Schwarzschild is FORCED by the angular equation alone;
        • on that f the radial Ricci vanishes, so the radial equation
          R_rr = κ φ'²  collapses to  κ φ'² = 0  ⇒  φ' = 0  ⇒  φ = const.
      A clean symbolic chain: the field equations themselves forbid hair.

  (2) SEARCH (the loop's verifier, three-valued). On the forced background a
      menu of non-constant profiles — 1/r, ln r, r, and the JNW/dilaton log
      ln(1−2M/r) — is every one REJECTED; only φ = const VERIFIES.

Honest footnote: the one genuine scalar-haired solution, JNW, escapes only by
deforming the angular part to (1−b/r)^{1−γ} r² — a fractional power, exactly
the branch-cut wall the project's D4 rule keeps out. No-hair here means
"no hair without leaving the rational r²-ansatz."

Run:  .venv/bin/python scripts/32_no_hair.py
"""

import importlib.util
import os
import sys

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from gr_engine import Geometry, build_ansatz_metric, R_SYM, VERIFIED, REJECTED

_s = importlib.util.spec_from_file_location("sc", os.path.join(_here, "27_scalar.py"))
sc = importlib.util.module_from_spec(_s); _s.loader.exec_module(sc)


def prove_no_hair():
    """The theorem, derived symbolically. Returns (ok, forced_f, phi_prime_sols)."""
    r = R_SYM
    kappa = sp.Symbol("kappa", positive=True)
    f = sp.Function("f")
    phi = sp.Function("phi")

    # General static ansatz with f(r) left as an unknown function.
    metric, coords, _ = build_ansatz_metric(4, f(r))
    geo = Geometry(metric, coords)

    # Angular equation: source is κ(∂_θφ)² = 0 because φ = φ(r). So R_θθ = 0.
    Rthth = sp.simplify(geo.ricci[2, 2])           # = 1 − f − r f'
    fsol = sp.dsolve(sp.Eq(Rthth, 0), f(r))        # ⇒ f(r) = 1 + C1/r
    forced_f = sp.simplify(fsol.rhs)

    # Substitute the forced f and turn to the radial equation R_rr = κ φ'².
    C1 = sp.Symbol("C1")
    metric2, coords2, _ = build_ansatz_metric(4, 1 + C1 / r)
    geo2 = Geometry(metric2, coords2)
    Rrr = sp.simplify(geo2.ricci[1, 1])            # = 0 (Schwarzschild is Ricci-flat)
    dphi = sp.diff(phi(r), r)
    radial = sp.simplify(geo2.ricci[1, 1] - kappa * dphi**2)   # = −κ φ'²
    d = sp.Symbol("d")
    phi_prime_sols = sp.solve(radial.subs(dphi, d), d)         # ⇒ [0]

    ok = (Rthth == 1 - f(r) - r * sp.diff(f(r), r)
          and forced_f.equals(1 + C1 / r)
          and Rrr == 0
          and phi_prime_sols == [0])
    return ok, Rthth, forced_f, Rrr, radial, phi_prime_sols


def search_for_hair():
    """The loop's verifier on the forced (Schwarzschild) background: only a
    constant scalar survives; every rational/log profile is rejected."""
    r = R_SYM
    M = sp.Symbol("M", positive=True)
    C = sp.Symbol("C", positive=True)
    metric, coords, _ = build_ansatz_metric(4, 1 - 2 * M / r)
    menu = [
        ("φ = const (the only survivor)", sp.Integer(7), VERIFIED),
        ("φ = C/r",                       C / r,                    REJECTED),
        ("φ = C·ln r",                    C * sp.log(r),            REJECTED),
        ("φ = C·r",                       C * r,                    REJECTED),
        ("φ = C·ln(1−2M/r)  [JNW shape]", C * sp.log(1 - 2 * M / r), REJECTED),
    ]
    results = []
    for name, phi, expect in menu:
        v, _ = sc.verify_scalar(metric, coords, phi, params=(M, C))
        results.append((name, v, expect, v == expect))
    return results


def main():
    print("NO-HAIR — rediscovered and proven by the engine\n")

    # (1) the proof
    print("  [proof] f(r), φ(r) symbolic — let the field equations decide:")
    ok_proof, Rthth, forced_f, Rrr, radial, phi_p = prove_no_hair()
    print(f"     angular eq (zero scalar source):  R_θθ = {Rthth} = 0")
    print(f"        ⇒ f(r) = {forced_f}   (Schwarzschild, FORCED)")
    print(f"     radial eq on that f:  R_rr = {Rrr},  so  R_rr − κφ'² = {radial} = 0")
    print(f"        ⇒ φ'(r) ∈ {phi_p}   ⇒  φ = const   (NO HAIR)")
    print(f"     proof: {'✅ holds' if ok_proof else '❌ broke'}")

    # (2) the search
    print("\n  [search] verifier on the forced background — hunting for hair:")
    results = search_for_hair()
    ok_search = all(good for *_, good in results)
    for name, v, expect, good in results:
        print(f"     {name:32s} → {v:9s} (expect {expect:9s}) {'✓' if good else '✗'}")

    print("\n  footnote: JNW (the real haired solution) escapes only by bending the")
    print("  angular part to (1−b/r)^(1−γ)·r² — a fractional power, the D4 branch-cut")
    print("  wall. No hair WITHOUT leaving the rational r²-ansatz.")

    passed = ok_proof and ok_search
    print(f"\nNO-HAIR: {'PASSED ✅  (engine proves it, then fails to find any hair)' if passed else 'FAILED ❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
