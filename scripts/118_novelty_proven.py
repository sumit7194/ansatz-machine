#!/usr/bin/env python3
"""Step 118 — NOVELTY, PROOF-BACKED: the fingerprint filter's verdicts adjudicated by CK.

This closes the loop the whole Cartan-Karlhede arc was for. §02's docstring has said from the
beginning that its verdicts are heuristic:

    "Invariants are necessary, not sufficient: matching curves do NOT prove equivalence
     (Cartan-Karlhede would; no Python implementation exists). A match is reported as
     KNOWN_LIKELY, not 'same'."
    FLAT_OR_VSI -- "invariants are blind here, Cartan-Karlhede needed"
    BLIND_SPOT  -- "invariants are blind here, CK needed"

The implementation now exists (§116/§117), so those three deferrals can be honoured:

  UPGRADE  KNOWN_LIKELY(name)  ->  PROVEN_KNOWN(name)     the heuristic match becomes a proof
  ADJUDICATE  FLAT_OR_VSI / BLIND_SPOT  ->  a real verdict, exactly where invariants are blind
  BACK      CANDIDATE_NEW  ->  PROVEN_NEW_vs_CATALOG      inequivalent to EVERY catalog entry

WHAT "PROVEN_NEW" DOES AND DOES NOT MEAN, stated plainly: it means CK proved the geometry
inequivalent to every entry in OUR catalog. It is not a claim of novelty in the literature --
that would require the catalog to be the literature. It upgrades "no curve matched" (which could
be a fingerprint miss) to "no catalog entry IS this spacetime" (which is a decision).

Repro: .venv/bin/python scripts/118_novelty_proven.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

import ck
from gr_engine import Geometry

t, r, th, ph = sp.symbols("t r theta phi", positive=True)
rho = sp.Symbol("rho", positive=True)
u, v_, x, y, z_ = sp.symbols("u v x y z", real=True)

PROVEN_KNOWN = "PROVEN_KNOWN"
PROVEN_NEW = "PROVEN_NEW_vs_CATALOG"
UNDECIDED = "UNDECIDED"


def sph(f, M=None):
    return Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph])


def catalog():
    """The reference catalog, each entry with the domain it is valid on."""
    return [
        ("Minkowski", Geometry(sp.diag(-1, 1, 1, 1), [t, x, y, z_]), None, None),
        ("Schwarzschild (M=1)", sph(1 - 2 / r), sp.Q.positive(r - 2), None),
        ("Reissner-Nordstrom (M=3,Q=1)", sph(1 - 6 / r + 1 / r**2),
         sp.Q.positive(1 - 6 / r + 1 / r**2), None),
        ("de Sitter (H=1)", sph(1 - r**2), sp.Q.positive(1 - r**2), None),
        ("pp-wave (H = x^2-y^2)",
         Geometry(sp.Matrix([[x**2 - y**2, -1, 0, 0], [-1, 0, 0, 0],
                             [0, 0, 1, 0], [0, 0, 0, 1]]), [u, v_, x, y]), None,
         ([0, 1, 0, 0], [1, (x**2 - y**2) / 2, 0, 0],
          [0, 0, 1 / sp.sqrt(2), sp.I / sp.sqrt(2)],
          [0, 0, 1 / sp.sqrt(2), -sp.I / sp.sqrt(2)])),
    ]


def adjudicate(geo, label, dom, tet, cat):
    """Decide `geo` against the catalog with CK. Three-valued."""
    ck.set_domain(dom, sp.Q.positive(sp.sin(th)))
    sig = ck.ck_signature(geo, label, tet=tet)
    undec = []
    for name, cgeo, cdom, ctet in cat:
        ck.set_domain(cdom, sp.Q.positive(sp.sin(th)))
        csig = ck.ck_signature(cgeo, name, tet=ctet)
        verdict, why = ck.equivalent(sig, csig)
        if verdict == ck.EQUIVALENT:
            return PROVEN_KNOWN, name, why[0] if why else ""
        if verdict == ck.UNDECIDED:
            undec.append(name)
    if undec:
        return UNDECIDED, None, f"could not decide against: {undec}"
    return PROVEN_NEW, None, "CK proved inequivalent to every catalog entry"


def main():
    print("NOVELTY, PROOF-BACKED — §02's heuristic verdicts adjudicated by Cartan-Karlhede\n")
    cat = catalog()
    print(f"  catalog: {[c[0] for c in cat]}\n")
    ok = []

    s2 = sp.sqrt(2)
    Hb = 2 * x * y
    cases = [
        # (label, geometry, domain, seed tetrad, what §02 says, expected CK verdict, expected name)
        ("Schwarzschild in ISOTROPIC coords",
         Geometry(sp.diag(-((1 - 1 / (2 * rho)) / (1 + 1 / (2 * rho)))**2,
                          (1 + 1 / (2 * rho))**4, (1 + 1 / (2 * rho))**4 * rho**2,
                          (1 + 1 / (2 * rho))**4 * rho**2 * sp.sin(th)**2), [t, rho, th, ph]),
         sp.Q.positive(rho - sp.Rational(1, 2)), None,
         "KNOWN_LIKELY(Schwarzschild) -- a curve match, not a proof",
         PROVEN_KNOWN, "Schwarzschild (M=1)"),

        ("Minkowski", Geometry(sp.diag(-1, 1, 1, 1), [t, x, y, z_]), None, None,
         "FLAT_OR_VSI -- declines: 'invariants are blind here, CK needed'",
         PROVEN_KNOWN, "Minkowski"),

        ("pp-wave H = 2xy (a rotation of the catalog's)",
         Geometry(sp.Matrix([[Hb, -1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]),
                  [u, v_, x, y]), None,
         ([0, 1, 0, 0], [1, Hb / 2, 0, 0], [0, 0, 1 / s2, sp.I / s2],
          [0, 0, 1 / s2, -sp.I / s2]),
         "FLAT_OR_VSI -- every polynomial invariant vanishes; totally blind",
         PROVEN_KNOWN, "pp-wave (H = x^2-y^2)"),

        ("de Sitter (H=1)", sph(1 - r**2), sp.Q.positive(1 - r**2), None,
         "BLIND_SPOT -- invariants constant (CSI class); declines",
         PROVEN_KNOWN, "de Sitter (H=1)"),

        ("Reissner-Nordstrom (M=3,Q=1) in ingoing Eddington-Finkelstein",
         Geometry(sp.Matrix([[-(1 - 6 / r + 1 / r**2), 1, 0, 0], [1, 0, 0, 0],
                             [0, 0, r**2, 0], [0, 0, 0, r**2 * sp.sin(th)**2]]),
                  [v_, r, th, ph]),
         sp.Q.positive(1 - 6 / r + 1 / r**2), None,
         "a different chart entirely -- off-diagonal, horizon-penetrating",
         PROVEN_KNOWN, "Reissner-Nordstrom (M=3,Q=1)"),

        ("Schwarzschild M=5 (not in the catalog)", sph(1 - 10 / r),
         sp.Q.positive(r - 10), None,
         "CANDIDATE_NEW -- no catalog curve matched",
         PROVEN_NEW, None),
    ]

    for lab, geo, dom, tet, says02, expect_v, expect_n in cases:
        verdict, name, why = adjudicate(geo, lab, dom, tet, cat)
        good = (verdict == expect_v) and (expect_n is None or name == expect_n)
        ok.append(good)
        print(f"  {lab}")
        print(f"      §02 says : {says02}")
        print(f"      CK says  : {verdict}{(' = ' + name) if name else ''}   "
              f"{'✅' if good else '❌ want ' + expect_v + ' ' + str(expect_n)}")
        print(f"                 {str(why)[:120]}")

    passed = all(ok)
    print(f"\nNOVELTY PROOF-BACKED: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          f"({sum(ok)}/{len(ok)}) — KNOWN_LIKELY upgraded to a proof, FLAT_OR_VSI and BLIND_SPOT "
          "adjudicated where invariants are blind, CANDIDATE_NEW backed by a decision. "
          "PROVEN_NEW = inequivalent to every CATALOG entry, not a literature-novelty claim.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
