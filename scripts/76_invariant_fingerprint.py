#!/usr/bin/env python3
"""Step 76 — THE CURVATURE-INVARIANT FINGERPRINT: a coordinate-free signature.

Future use (why this is built): the sister learned-geometry project (tabula-geometrica)
needs GROUND TRUTH that does not depend on coordinates — a net can represent a spacetime
any way it likes, so to check it learned the RIGHT geometry you compare COORDINATE-FREE
scalar invariants. §42 (causal structure) was built as one such oracle; this is the
curvature one. It also fills a real gap (no Python Cartan–Karlhede): a practical
fingerprint that tells geometries apart invariantly.

The signature splits into two complementary sectors (`analyzer.invariant_fingerprint`):
  • RICCI sector {R, R_ab R^ab} — the MATTER content (zero in vacuum);
  • WEYL sector {I, J} — the FREE gravity (tidal field / waves; zero if conformally flat).

  (A) the fingerprint distinguishes the zoo coordinate-free: flat (all 0), Schwarzschild
      (Ricci 0, Weyl≠0), Reissner–Nordström (Ricci≠0, Weyl≠0), de Sitter (Ricci≠0, Weyl 0);
  (B) it RESOLVES A DEGENERACY a single invariant misses: Schwarzschild and RN BOTH have
      R=0, but R_ab R^ab = 0 vs 4Q⁴/r⁸ — the charge shows up invariantly. A scalar alone
      (or a coordinate-dependent feature) can't tell them apart; the full vector can;
  (C) the two sectors are COMPLEMENTARY: Schwarzschild is vacuum (Ricci=0) but curved by
      free gravity (Weyl≠0); de Sitter is conformally flat (Weyl=0) but full of Λ
      (Ricci≠0) — matter vs tidal field, cleanly separated;
  (D) so a learned-geometry model's output is checked against this invariant fingerprint —
      coordinate-proof ground truth.

Honest scope: a finite invariant set (a practical fingerprint, not the full
Cartan–Karlhede equivalence). It distinguishes inequivalent geometries here; in rare
cases distinct geometries can share low-order invariants (then add gradients, §02).
Coordinate-freeness (stress-tested + hardened 2026-06-20): the Ricci sector {R, R_abR^ab}
and the **tetrad-free Weyl-square** Weyl_sq = C_abcd C^abcd = K − 2R_abR^ab + R²/3 are
genuine coordinate scalars, computed for ANY diagonal metric — so the fingerprint now
agrees across charts (test D below: standard vs isotropic Schwarzschild match at the
mapped point). The NP Weyl invariants {Weyl_I, Weyl_J} (which carry the algebraic TYPE)
are still computed only in the canonical −f,1/f form (they need the adapted tetrad);
off-diagonal metrics skip the Kretschmann-level work (heavy). So cross-chart comparison
works via the Ricci sector + Weyl-square; type-level discrimination is canonical-form.

Run:  .venv/bin/python scripts/76_invariant_fingerprint.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry
from analyzer import invariant_fingerprint


def main():
    print("THE CURVATURE-INVARIANT FINGERPRINT — a coordinate-free signature\n")
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    M, Q, L = sp.symbols("M Q L", positive=True)
    ok = []

    def fp(f):
        g = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2)
        return invariant_fingerprint(Geometry(g, [t, r, th, ph]))

    zoo = {
        "flat": fp(sp.Integer(1)),
        "Schwarzschild": fp(1 - 2 * M / r),
        "Reissner–Nordström": fp(1 - 2 * M / r + Q**2 / r**2),
        "de Sitter": fp(1 - r**2 / L**2),
    }

    # (A) distinct fingerprints across the zoo
    print("  (A) coordinate-free fingerprints:")
    for nm, f in zoo.items():
        print(f"      {nm:20s}: R={f['R']}, Ric²={f['Ricci_sq']}, WeylI={f.get('Weyl_I')}, WeylJ={f.get('Weyl_J')}")
    keys = ("R", "Ricci_sq", "Weyl_I", "Weyl_J")
    vecs = [tuple(sp.simplify(zoo[nm].get(k, 0)) for k in keys) for nm in zoo]
    distinct = all(vecs[i] != vecs[j] for i in range(len(vecs)) for j in range(i + 1, len(vecs)))
    ok.append(distinct)
    print(f"      ⇒ all four fingerprints distinct   {'✅' if distinct else '❌'}")

    # (B) resolves the Schwarzschild/RN degeneracy (both R=0)
    okB = (zoo["Schwarzschild"]["R"] == 0 and zoo["Reissner–Nordström"]["R"] == 0
           and zoo["Schwarzschild"]["Ricci_sq"] == 0
           and sp.simplify(zoo["Reissner–Nordström"]["Ricci_sq"] - 4 * Q**4 / r**8) == 0)
    ok.append(okB)
    print(f"\n  (B) Schwarzschild & RN BOTH have R=0, but Ric² = 0 vs {zoo['Reissner–Nordström']['Ricci_sq']}")
    print(f"      ⇒ the charge shows up coordinate-free; a single scalar can't tell them apart   {'✅' if okB else '❌'}")

    # (C) the two sectors are complementary (matter vs free gravity)
    okC = (zoo["Schwarzschild"]["Ricci_sq"] == 0 and zoo["Schwarzschild"]["Weyl_I"] != 0     # vacuum, curved
           and zoo["de Sitter"]["Weyl_I"] == 0 and zoo["de Sitter"]["R"] != 0)               # conf. flat, Λ
    ok.append(okC)
    print(f"\n  (C) sectors complementary: Schwarzschild Ricci=0 but Weyl≠0 (free gravity);")
    print(f"      de Sitter Weyl=0 but R≠0 (matter/Λ) — matter vs tidal field, cleanly split   {'✅' if okC else '❌'}")

    # (D) COORDINATE-INVARIANCE (the oracle's core promise): the same geometry in a
    #     DIFFERENT chart gives the SAME invariant. Schwarzschild standard vs isotropic,
    #     compared at the mapped physical point r = ρ(1+M/2ρ)², via the tetrad-free Weyl-square.
    rho = sp.symbols("rho", positive=True)
    A = (1 - M / (2 * rho)) / (1 + M / (2 * rho))
    B = (1 + M / (2 * rho))**2
    g_iso = sp.diag(-A**2, B**2, B**2 * rho**2, B**2 * rho**2 * sp.sin(th)**2)
    fp_iso = invariant_fingerprint(Geometry(g_iso, [t, rho, th, ph]))
    W_std = zoo["Schwarzschild"]["Weyl_sq"]                       # = 48M²/r⁶
    rho0, Mv = sp.Integer(2), sp.Integer(1)
    r_map = float((rho0 * (1 + Mv / (2 * rho0))**2))              # physical radius
    okD = (abs(float(fp_iso["Weyl_sq"].subs({rho: rho0, M: Mv}))
               - float(W_std.subs({r: r_map, M: Mv}))) < 1e-9)
    ok.append(okD)
    print(f"\n  (D) coordinate-invariance: Schwarzschild Weyl-square (tetrad-free C²) in standard vs")
    print(f"      ISOTROPIC coords agree at the mapped point ({float(fp_iso['Weyl_sq'].subs({rho:rho0,M:Mv})):.6f}) "
          f"— a genuine coordinate-free scalar   {'✅' if okD else '❌'}")

    # (E) the oracle role
    okE = distinct and okB and okC and okD
    ok.append(okE)
    print(f"\n  (E) USE: a learned-geometry model's output is validated against this invariant")
    print(f"      fingerprint — coordinate-proof ground truth (the tabula-geometrica oracle)   {'✅' if okE else '❌'}")

    passed = all(ok)
    print(f"\nINVARIANT FINGERPRINT: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(coordinate-free signature; resolves the R=0 degeneracy; matter/gravity sectors)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
