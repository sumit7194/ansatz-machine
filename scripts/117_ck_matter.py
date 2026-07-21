#!/usr/bin/env python3
"""Step 117 — CARTAN-KARLHEDE, THE MATTER SECTOR: Ricci invariants and the Segre type.

§116 gated CK on the WEYL sector (types D, I, N). But it compared matter using only the Ricci
SCALAR, and the scalar is blind to traceless matter: Reissner-Nordstrom has R = 0, and so does a
radiation-filled universe. The demonstrated hole (measured before fixing):

    Minkowski      : Petrov O, t0 = t1 = 0, order0 = [], R = 0
    radiation FRW  : Petrov O, t0 = t1 = 0, order0 = [], R = 0     <- IDENTICAL signature
    verdict        : UNDECIDED

Flat spacetime and a radiation cosmology were indistinguishable, because the entire matter sector
was invisible. This step adds it:

  (A) RICCI INVARIANTS: the traces tr((R^a_b)^k), k = 1..4, which fix the characteristic polynomial
      of the mixed Ricci tensor and hence its eigenvalue structure. They are frame-INDEPENDENT, so
      they are order-0 Cartan invariants that need no frame fixing at all.
  (B) THE SEGRE TYPE: matter classified by the eigenvalue structure of R^a_b -- eigenvalues FIRST,
      tracelessness second (getting that order wrong mislabels a radiation fluid, which is
      traceless, as an electrovac). The machine derives Segre [(11)(1,1)] for Reissner-Nordstrom
      and Segre [1,(111)] for the FRW fluids on its own.
  (C) THE MATTER COSTUME TEST: Reissner-Nordstrom in the Schwarzschild chart vs in INGOING
      EDDINGTON-FINKELSTEIN coordinates (off-diagonal, horizon-penetrating) -> EQUIVALENT.

HONEST SCOPE: this uses frame-free Ricci invariants plus the Segre type. Differing invariants are
a rigorous INEQUIVALENT; matching ones are necessary but not sufficient, so full rigour for matter
still wants the Segre-canonical frame alignment (the NP Phi_ab in a Ricci-adapted tetrad), which is
NOT implemented here. Repro: .venv/bin/python scripts/117_ck_matter.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

import ck
from gr_engine import Geometry

t, r, th, ph = sp.symbols("t r theta phi", positive=True)
x, y, z_, v_ = sp.symbols("x y z v", real=True)
M, Q = sp.symbols("M Q", positive=True)


def sph(f, coords=None):
    return Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), coords or [t, r, th, ph])


def main():
    print("CARTAN-KARLHEDE, THE MATTER SECTOR — Ricci invariants + Segre type\n")
    ok = []

    def verdict(lab, s1, s2, expect):
        vv, why = ck.equivalent(s1, s2)
        good = (vv == expect)
        ok.append(good)
        print(f"  {lab:50s} {vv:13s} (want {expect:12s}) {'✅' if good else '❌'}")
        if why:
            print(f"       └ {str(why[0])[:140]}")

    # ---------------------------------------------------------------- (A) the Segre table
    print("(A) SEGRE CLASSIFICATION — matter type from the eigenvalue structure of R^a_b:")
    table = [
        ("Minkowski", sp.diag(-1, 1, 1, 1), [t, x, y, z_], None, "vacuum"),
        ("radiation FRW (a^2 = t)", sp.diag(-1, t, t, t), [t, x, y, z_],
         sp.Q.positive(t), "perfect fluid, radiation"),
        ("dust FRW (a^2 = t^4/3)", sp.diag(-1, t**sp.Rational(4, 3), t**sp.Rational(4, 3),
                                           t**sp.Rational(4, 3)), [t, x, y, z_],
         sp.Q.positive(t), "perfect fluid"),
        ("de Sitter", sp.diag(-(1 - r**2), 1 / (1 - r**2), r**2, r**2 * sp.sin(th)**2),
         [t, r, th, ph], sp.Q.positive(1 - r**2), "Einstein space"),
        ("Schwarzschild", sp.diag(-(1 - 2 * M / r), 1 / (1 - 2 * M / r), r**2,
                                  r**2 * sp.sin(th)**2), [t, r, th, ph],
         sp.Q.positive(r - 2 * M), "vacuum"),
        ("Reissner-Nordstrom", sp.diag(-(1 - 2 * M / r + Q**2 / r**2),
                                       1 / (1 - 2 * M / r + Q**2 / r**2), r**2,
                                       r**2 * sp.sin(th)**2), [t, r, th, ph],
         sp.Q.positive(1 - 2 * M / r + Q**2 / r**2), "non-null electromagnetic"),
    ]
    for nm, g, co, dom, expect in table:
        ck.set_domain(dom, sp.Q.positive(sp.sin(th)))
        seg = ck.segre_type(Geometry(g, co))
        good = isinstance(seg, str) and seg.startswith(expect)
        ok.append(good)
        print(f"    {nm:26s} -> {str(seg):58s} {'✅' if good else '❌ want ' + expect}")

    # ---------------------------------------------------------------- (B) the closed hole
    print("\n(B) THE HOLE §116 LEFT OPEN — flat spacetime vs a radiation universe:")
    ck.set_domain(sp.Q.positive(t))
    s_mink = ck.ck_signature(Geometry(sp.diag(-1, 1, 1, 1), [t, x, y, z_]), "Minkowski")
    s_frw = ck.ck_signature(Geometry(sp.diag(-1, t, t, t), [t, x, y, z_]), "radiation FRW")
    print(f"    Minkowski     : Petrov {s_mink['petrov']}, R = {s_mink['ricci_scalar']}, "
          f"tr(R^k) = {s_mink['ricci_traces']}")
    print(f"    radiation FRW : Petrov {s_frw['petrov']}, R = {s_frw['ricci_scalar']}, "
          f"tr(R^k) = {s_frw['ricci_traces']}")
    print("    (both Petrov O with R = 0: the Weyl sector and the Ricci SCALAR see nothing)")
    verdict("Minkowski vs radiation FRW", s_mink, s_frw, ck.INEQUIVALENT)

    ck.set_domain(sp.Q.positive(t))
    s_dust = ck.ck_signature(
        Geometry(sp.diag(-1, t**sp.Rational(4, 3), t**sp.Rational(4, 3),
                         t**sp.Rational(4, 3)), [t, x, y, z_]), "dust FRW")
    verdict("radiation FRW vs dust FRW (both perfect fluids)", s_frw, s_dust, ck.INEQUIVALENT)

    # ---------------------------------------------------------------- (C) charged black holes
    print("\n(C) CHARGED BLACK HOLES — matter type, charge, and the matter costume test:")
    f_rn = 1 - 2 * M / r + Q**2 / r**2
    ck.set_domain(sp.Q.positive(f_rn), sp.Q.positive(sp.sin(th)))
    s_rn = ck.ck_signature(sph(f_rn), "Reissner-Nordstrom [Schwarzschild chart]")
    print(f"    RN : Petrov {s_rn['petrov']}, Psi2 = {s_rn['psi'][2]}")
    print(f"         segre = {s_rn['segre']}")

    ck.set_domain(sp.Q.positive(r - 2 * M), sp.Q.positive(sp.sin(th)))
    s_schw = ck.ck_signature(sph(1 - 2 * M / r), "Schwarzschild")
    verdict("Reissner-Nordstrom vs Schwarzschild", s_rn, s_schw, ck.INEQUIVALENT)

    # different charge
    f1 = 1 - 2 * 3 / r + 1 / r**2
    f2 = 1 - 2 * 3 / r + 4 / r**2
    ck.set_domain(sp.Q.positive(f1), sp.Q.positive(sp.sin(th)))
    s_q1 = ck.ck_signature(sph(f1), "RN M=3 Q=1")
    ck.set_domain(sp.Q.positive(f2), sp.Q.positive(sp.sin(th)))
    s_q2 = ck.ck_signature(sph(f2), "RN M=3 Q=2")
    verdict("RN(M=3,Q=1) vs RN(M=3,Q=2)", s_q1, s_q2, ck.INEQUIVALENT)

    # THE MATTER COSTUME TEST: same RN, ingoing Eddington-Finkelstein (off-diagonal, and the
    # chart is horizon-penetrating -- nothing about it looks like the Schwarzschild chart)
    print("    ingoing Eddington-Finkelstein: ds^2 = -f dv^2 + 2 dv dr + r^2 dOmega^2 "
          "(off-diagonal)")
    g_ef = sp.Matrix([[-f_rn, 1, 0, 0], [1, 0, 0, 0], [0, 0, r**2, 0],
                      [0, 0, 0, r**2 * sp.sin(th)**2]])
    ck.set_domain(sp.Q.positive(f_rn), sp.Q.positive(sp.sin(th)))
    s_ef = ck.ck_signature(Geometry(g_ef, [v_, r, th, ph]), "RN [ingoing Eddington-Finkelstein]")
    print(f"    RN EF : Petrov {s_ef['petrov']}, segre = {s_ef['segre']}")
    verdict("RN [Schwarzschild chart] vs RN [Eddington-Finkelstein]", s_rn, s_ef, ck.EQUIVALENT)

    # ---------------------------------------------------------------- (D) conformally flat pair
    print("\n(D) BOTH PETROV O — the Weyl sector is empty, so matter must decide:")
    ck.set_domain(sp.Q.positive(1 - r**2), sp.Q.positive(sp.sin(th)))
    s_ds = ck.ck_signature(sph(1 - r**2), "de Sitter")
    ck.set_domain()
    s_mink2 = ck.ck_signature(Geometry(sp.diag(-1, 1, 1, 1), [t, x, y, z_]), "Minkowski")
    verdict("de Sitter vs Minkowski (both Petrov O)", s_ds, s_mink2, ck.INEQUIVALENT)

    passed = all(ok)
    print(f"\nCK MATTER SECTOR: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          f"({sum(ok)}/{len(ok)} checks; Segre types derived, the radiation-universe hole closed, "
          "RN recognized across charts)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
