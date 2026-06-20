#!/usr/bin/env python3
"""Step 83 — TETRAD-FREE ALGEBRAIC TYPE: the fingerprint's Petrov type, coordinate-free.

Closes the §76 caveat. The invariant fingerprint already had a coordinate-free MAGNITUDE
(the Weyl-square, §76(D)). What it lacked was a coordinate-free TYPE: the complex Weyl
invariants I, J (whose ratio gives the Petrov class via I³=27J² ⟺ algebraically special)
were computed only in the canonical −f,1/f tetrad, so they vanished in any other chart.

Here I, J are computed TETRAD-FREE — as pure Weyl-tensor contractions:
    I = (A − iB)/16,  J = (C₃ − iD₃)/96,
    A = C_abcd C^abcd,  B = C_abcd *C^abcd,  C₃ = C^ab_cd C^cd_ef C^ef_ab,  D₃ = (cubic, one dual),
the constants CALIBRATED against the Newman–Penrose I, J on Schwarzschild and Kerr.

  (A) the tetrad-free I, J reproduce the NP (tetrad) I, J on the zoo — Schwarzschild,
      RN, de Sitter — to the symbol (cross-check vs an independent computation);
  (B) COORDINATE-INVARIANCE of the TYPE: Schwarzschild in standard vs ISOTROPIC coords
      gives identical I, J at the mapped physical point — the caveat the old tetrad
      version could not meet (it only worked in the −f,1/f form);
  (C) the speciality index I³−27J² is a coordinate-free SPECIALITY detector: 0 ⟺
      algebraically special. For the zoo it separates type-D (I,J≠0, I³=27J²) from
      type-O de Sitter (I=J=0, conformally flat);
  (D) OFF-DIAGONAL capstone: Kerr (Boyer–Lindquist, off-diagonal — symbolic Weyl swamps)
      via the NUMERIC tetrad-free route reproduces I=3Ψ₂², J=−Ψ₂³ and I³=27J² (type D),
      WITHOUT any tetrad — the magnetic (B, D₃) part validated where it is non-zero;
  (E) the HONEST boundary: I, J do NOT give the full Petrov type. They cannot split
      {II from D} (both I³=27J², I,J≠0) nor {III, N, O} (all I=J=0). A type-N vacuum
      pp-wave has I=J=0 (and Weyl-square 0) yet Weyl≠0 — indistinguishable from type O by
      these polynomial invariants. Full classification still needs the adapted tetrad
      (§80, numeric) or differential invariants. We close the §76 CHART caveat (I,J in any
      chart), not the inherent incompleteness of scalar invariants.

Run:  .venv/bin/python scripts/83_tetradfree_type.py
"""

import math
import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry
from analyzer import weyl_invariants, weyl_invariants_tensor, weyl_scalars, weyl_tensor
import numeric_curvature as nc


def sph(f, M=None):
    """Static spherical −f,1/f,r²,r²sin²θ as a Geometry, plus the canonical null tetrad."""
    t, r, th, ph = sp.symbols("t r theta phi", positive=True)
    g = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2)
    return Geometry(g, [t, r, th, ph]), r, th


def np_IJ(f):
    """The NP (tetrad) I, J for the −f,1/f form — the independent reference."""
    geo, r, th = sph(f)
    s2 = sp.sqrt(2)
    tet = ([1 / f, 1, 0, 0], [sp.Rational(1, 2), -f / 2, 0, 0],
           [0, 0, 1 / (r * s2), sp.I / (r * s2 * sp.sin(th))],
           [0, 0, 1 / (r * s2), -sp.I / (r * s2 * sp.sin(th))])
    return weyl_invariants(weyl_scalars(weyl_tensor(geo), tet))


def main():
    print("TETRAD-FREE ALGEBRAIC TYPE — the fingerprint's Petrov class, coordinate-free\n")
    ok = []
    t, r, th, ph, rho = sp.symbols("t r theta phi rho", positive=True)
    M, Q, L = sp.symbols("M Q L", positive=True)

    zoo = {
        "Schwarzschild": 1 - 2 * M / r,
        "Reissner–Nordström": 1 - 2 * M / r + Q**2 / r**2,
        "de Sitter": 1 - r**2 / L**2,
    }

    # (A) tetrad-free I,J == NP (tetrad) I,J on the zoo
    print("  (A) tetrad-free I,J  vs  Newman–Penrose (tetrad) I,J:")
    okA = True
    IJ = {}
    for nm, f in zoo.items():
        geo, _, _ = sph(f)
        It, Jt = weyl_invariants_tensor(geo)        # tetrad-free
        In, Jn = np_IJ(f)                           # tetrad (independent)
        IJ[nm] = (sp.simplify(It), sp.simplify(Jt))
        match = sp.simplify(It - In) == 0 and sp.simplify(Jt - Jn) == 0
        okA = okA and match
        print(f"      {nm:20s}: I={IJ[nm][0]}, J={IJ[nm][1]}   {'✅' if match else '❌ ≠ NP'}")
    ok.append(okA)
    print(f"      ⇒ the tetrad-free route reproduces the tetrad invariants   {'✅' if okA else '❌'}")

    # (B) coordinate-invariance of the TYPE: standard vs isotropic Schwarzschild
    A = (1 - M / (2 * rho)) / (1 + M / (2 * rho))
    Bf = (1 + M / (2 * rho))**2
    g_iso = sp.diag(-A**2, Bf**2, Bf**2 * rho**2, Bf**2 * rho**2 * sp.sin(th)**2)
    Ii, Ji = weyl_invariants_tensor(Geometry(g_iso, [t, rho, th, ph]))
    rho0, Mv = sp.Integer(2), sp.Integer(1)
    r_map = float(rho0 * (1 + Mv / (2 * rho0))**2)
    Istd, Jstd = IJ["Schwarzschild"]
    okB = (abs(float(Ii.subs({rho: rho0, M: Mv})) - float(Istd.subs({r: r_map, M: Mv}))) < 1e-9 and
           abs(float(Ji.subs({rho: rho0, M: Mv})) - float(Jstd.subs({r: r_map, M: Mv}))) < 1e-9)
    ok.append(okB)
    print(f"\n  (B) coordinate-invariance of TYPE: Schwarzschild I,J in standard vs ISOTROPIC coords")
    print(f"      agree at the mapped point — I={float(Ii.subs({rho:rho0,M:Mv})):.6g}, "
          f"J={float(Ji.subs({rho:rho0,M:Mv})):.6g}   {'✅ (the §76 caveat, closed)' if okB else '❌'}")

    # (C) speciality I³−27J² as a coordinate-free SPECIALITY detector
    specs = {nm: sp.simplify(I**3 - 27 * J**2) for nm, (I, J) in IJ.items()}
    spec_iso = sp.simplify(Ii**3 - 27 * Ji**2)
    okC = (all(specs[nm] == 0 for nm in zoo) and spec_iso == 0 and
           IJ["Schwarzschild"][0] != 0 and IJ["de Sitter"][0] == 0)   # D has I≠0; O has I=0
    ok.append(okC)
    print(f"\n  (C) speciality I³−27J²: " +
          ", ".join(f"{nm.split('–')[0]}={specs[nm]}" for nm in zoo) + f", isotropic={spec_iso}")
    print(f"      all 0 ⇒ algebraically special; here type-D (I,J≠0) vs type-O de Sitter (I=J=0)   "
          f"{'✅' if okC else '❌'}")

    # (D) OFF-DIAGONAL capstone: Kerr via the numeric tetrad-free route
    a_k, Mk = 0.7, 1.0

    def kerr(xx):
        _, rr, tth, _ = xx
        Sig = rr * rr + a_k * a_k * math.cos(tth)**2
        De = rr * rr - 2 * Mk * rr + a_k * a_k
        s2 = math.sin(tth)**2
        gg = [[0.0] * 4 for _ in range(4)]
        gg[0][0] = -(1 - 2 * Mk * rr / Sig)
        gg[0][3] = gg[3][0] = -2 * Mk * rr * a_k * s2 / Sig
        gg[1][1] = Sig / De
        gg[2][2] = Sig
        gg[3][3] = (rr * rr + a_k * a_k + 2 * Mk * rr * a_k * a_k * s2 / Sig) * s2
        return gg
    xk = [0.0, 6.0, 1.1, 0.0]
    Ik, Jk = nc.weyl_invariants_numeric(kerr, xk)
    Psi2 = -Mk / (xk[1] - 1j * a_k * math.cos(xk[2]))**3
    Iexp, Jexp = 3 * Psi2**2, -Psi2**3
    okD = (abs(Ik - Iexp) < 1e-6 * abs(Iexp) and abs(Jk - Jexp) < 1e-6 * abs(Jexp) and
           abs(Ik**3 - 27 * Jk**2) < 1e-6 * abs(Ik**3))     # off-diagonal, type D, no tetrad
    ok.append(okD)
    print(f"\n  (D) OFF-DIAGONAL Kerr (numeric, no tetrad): I={Ik:.4g} vs 3Ψ₂²={Iexp:.4g};  "
          f"J={Jk:.4g} vs −Ψ₂³={Jexp:.4g}")
    print(f"      |I³−27J²|/|I³| = {abs(Ik**3-27*Jk**2)/abs(Ik**3):.1e} ⇒ type D, coordinate-free off-diagonal   "
          f"{'✅' if okD else '❌'}")

    # (E) the HONEST boundary: I,J don't give the full type — a type-N pp-wave looks like type O
    u, vv, xx, yy = sp.symbols("u v x y", real=True)
    Hpp = xx**2 - yy**2                          # harmonic ⇒ vacuum pp-wave, Petrov type N
    gpp = sp.Matrix([[Hpp, -1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    geo_pp = Geometry(gpp, [u, vv, xx, yy])
    Ipp, Jpp = weyl_invariants_tensor(geo_pp)
    Cpp = weyl_tensor(geo_pp)
    weyl_zero = all(sp.simplify(Cpp[a][b][c][d]) == 0 for a in range(4) for b in range(4)
                    for c in range(4) for d in range(4))
    okE = (sp.simplify(Ipp) == 0 and sp.simplify(Jpp) == 0 and not weyl_zero
           and sp.simplify(geo_pp.ricci_scalar) == 0)
    ok.append(okE)
    print(f"\n  (E) honest boundary: type-N vacuum pp-wave has I={sp.simplify(Ipp)}, J={sp.simplify(Jpp)} "
          f"(like type O) — yet Weyl≠0 ({not weyl_zero}).")
    print(f"      I,J give SPECIALITY, not the full type; {{II|D}} and {{III|N|O}} need the tetrad (§80)   "
          f"{'✅ scope stated' if okE else '❌'}")

    passed = all(ok)
    print(f"\nTETRAD-FREE TYPE: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(I,J = NP; TYPE coordinate-invariant; speciality detector; off-diagonal Kerr type D — §76 caveat closed)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
