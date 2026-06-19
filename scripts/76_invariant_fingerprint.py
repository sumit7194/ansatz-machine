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
IMPLEMENTATION CAVEAT (stress-tested 2026-06-20): the invariants ARE coordinate-free
scalars — verified, e.g. Schwarzschild's Kretschmann matches in standard vs isotropic
coordinates at the mapped physical point to machine precision. BUT `invariant_fingerprint`
currently computes the WEYL sector {I, J} (and Kretschmann) only for the canonical
static-spherical form −f dt²+dr²/f+r²dΩ² (a performance choice — the Weyl tensor is heavy
for general metrics); in other coordinate charts it returns the Ricci sector {R, R_abR^ab}
only. So cross-chart comparison of the FULL fingerprint needs the canonical form for now;
the robustness upgrade is tetrad-free Weyl-tensor contraction invariants (ROADMAP).

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

    # (D) the oracle role
    okD = distinct and okB and okC
    ok.append(okD)
    print(f"\n  (D) USE: a learned-geometry model's output is validated against this invariant")
    print(f"      fingerprint — coordinate-proof ground truth (the tabula-geometrica oracle)   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nINVARIANT FINGERPRINT: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(coordinate-free signature; resolves the R=0 degeneracy; matter/gravity sectors)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
