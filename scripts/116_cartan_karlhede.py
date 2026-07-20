#!/usr/bin/env python3
"""Step 116 — CARTAN-KARLHEDE: the costume problem solved as a DECISION procedure.

Our §02 fingerprint filter compares curvature invariants: necessary but NOT sufficient
(matching invariants prove nothing), and on VSI/Kundt spacetimes every polynomial invariant
vanishes so the filter is blind by construction -- the README declares this. Cartan-Karlhede
is the actual decision procedure: compare curvature in a CANONICALLY FIXED frame, order by
order. This battery gates `scripts/ck.py` against pairs with published ground truth.

Prior art (own sweep, 2026-07-21): NO Python/SymPy implementation exists. EinsteinPy carries the
Weyl tensor but no null tetrads / NP scalars / Petrov classification; RicciPy is development-
halted; the procedure lives in CLASSI (SHEEP, Lisp-era) and Maple (Pollney; Anderson-Torre).
Spec + worked examples: Mergulhao & Batista, arXiv:2007.04123. Isotropy errata: MacCallum (2020).

THE TESTS (each with known ground truth):
  (A) TYPE D, same spacetime in three charts -- the costume problem:
      Schwarzschild vs isotropic vs Painleve-Gullstrand (off-diagonal)   -> EQUIVALENT
      and THE HARD ONE: Zipoy-Voorhees at delta=1, in PROLATE SPHEROIDAL coordinates, whose
      metric functions ((x-1)/(x+1))^delta etc. share no visible form with Schwarzschild's
      1-2M/r, is recognized as Schwarzschild.                            -> EQUIVALENT
  (B) TYPE D, genuinely different spacetimes:
      Schwarzschild M=1 vs M=2 (the mass is a curvature scale)           -> INEQUIVALENT
      Schwarzschild vs Schwarzschild-de Sitter                           -> INEQUIVALENT
  (C) TYPE I, the generic case (canonical frame: Psi0=Psi4=0, Psi1=Psi3, isotropy dim 0):
      Kasner(u=2) vs the same with two axes relabelled                   -> EQUIVALENT
      Kasner(u=2) [type I] vs Kasner(u=1) LRS [type D]                   -> INEQUIVALENT
  NOTE on cost: the exponents must be rationalized (t = T^N) or the type-I PND quartic does not
  finish; and N itself must stay small -- u=3 needs N=13, i.e. T^24, and the Weyl tensor alone
  then does not complete in 25 minutes. Expression swell scales brutally with the exponent
  denominator; that is a real limit of the symbolic route, recorded rather than hidden.
  (D) THE BLIND SPOT CLOSED -- VSI pp-waves, all with Kretschmann = 0 and every polynomial
      invariant vanishing, where §02 must report BLIND_SPOT:
      H = x^2-y^2 vs H = 2xy (a 45-degree rotation)                      -> EQUIVALENT
      H = x^2-y^2 vs H = (x^2-y^2)/u^2                                   -> INEQUIVALENT

HONEST SCOPE: types D, I and N (N decided via the tensorial nabla-C test); types II/III and the
null-rotation isotropy reduction at order 1 are NOT implemented and return UNDECIDED rather than
guessing. Repro: .venv/bin/python scripts/116_cartan_karlhede.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

import ck
from gr_engine import Geometry

t, r, th, ph = sp.symbols("t r theta phi", positive=True)
x, y, z_, rho = sp.symbols("x y z rho", real=True)
T = sp.Symbol("T", positive=True)
u, v = sp.symbols("u v", real=True)
M = sp.Symbol("M", positive=True)


def schwarzschild(Mv):
    f = 1 - 2 * Mv / r
    return Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph])


def zipoy_voorhees(delta, sigma=1):
    """Exact static vacuum with tunable quadrupole, in PROLATE SPHEROIDAL (x,y).
    delta = 1 is Schwarzschild of mass M = sigma*delta -- in coordinates that hide it."""
    F = ((x - 1) / (x + 1))**delta
    H = ((x**2 - 1) / (x**2 - y**2))**(delta**2)
    s2 = sigma**2
    return Geometry(sp.diag(-F,
                            s2 / F * H * (x**2 - y**2) / (x**2 - 1),
                            s2 / F * H * (x**2 - y**2) / (1 - y**2),
                            s2 / F * (x**2 - 1) * (1 - y**2)), [t, x, y, ph])


def kasner_exponents(uu):
    """The standard rational parametrization: p = (-u, 1+u, u(1+u)) / (1+u+u^2)."""
    d = 1 + uu + uu**2
    return (sp.Rational(-uu, d), sp.Rational(1 + uu, d), sp.Rational(uu * (1 + uu), d))


def kasner(p1, p2, p3, N):
    """Vacuum Kasner (sum p = sum p^2 = 1), spatially homogeneous, generically Petrov type I,
    written in the RATIONALIZED time coordinate t = T^N (N = the common denominator of the
    exponents), so every power of T is an integer:

        ds^2 = -N^2 T^(2N-2) dT^2 + T^(2 N p1) dx^2 + T^(2 N p2) dy^2 + T^(2 N p3) dz^2

    This is a coordinate change, so it cannot affect a chart-independent verdict -- but it is
    the difference between the type-I PND quartic solving in 2 seconds and not finishing in ten
    minutes. (The Kerr expression-swell lesson, transferred: rational parametrizations.)"""
    return Geometry(sp.diag(-N**2 * T**(2 * N - 2), T**(2 * N * p1),
                            T**(2 * N * p2), T**(2 * N * p3)), [T, x, y, z_])


def ppwave(H):
    return Geometry(sp.Matrix([[H, -1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]),
                    [u, v, x, y])


def pp_tetrad(H):
    s2 = sp.sqrt(2)
    return ([0, 1, 0, 0], [1, H / 2, 0, 0],
            [0, 0, 1 / s2, sp.I / s2], [0, 0, 1 / s2, -sp.I / s2])


def main():
    print("CARTAN-KARLHEDE — deciding spacetime equivalence in a canonically fixed frame\n")
    ok = []

    def verdict(lab, s1, s2, expect):
        v, why = ck.equivalent(s1, s2)
        good = (v == expect)
        ok.append(good)
        print(f"  {lab:52s} {v:13s} (want {expect:12s}) {'✅' if good else '❌'}")
        if why:
            print(f"       └ {str(why[0])[:150]}")
        return good

    # ---------------------------------------------------------------- (A) type D, one spacetime
    print("(A) THE COSTUME PROBLEM — one spacetime, four charts (Petrov D):")
    ck.set_domain(sp.Q.positive(r - 2 * M), sp.Q.positive(sp.sin(th)))
    s_schw = ck.ck_signature(schwarzschild(M), "Schwarzschild [Schwarzschild chart]")
    print(f"    Schwarzschild : type {s_schw['petrov']}, Psi2 = {s_schw['psi'][2]}, "
          f"t0={s_schw['t0']} t1={s_schw['t1']}")

    A_ = (1 - M / (2 * rho)) / (1 + M / (2 * rho))
    B_ = (1 + M / (2 * rho))**4
    g_iso = Geometry(sp.diag(-A_**2, B_, B_ * rho**2, B_ * rho**2 * sp.sin(th)**2),
                     [t, rho, th, ph])
    ck.set_domain(sp.Q.positive(rho - M / 2), sp.Q.positive(sp.sin(th)))
    s_iso = ck.ck_signature(g_iso, "Schwarzschild [isotropic]")
    print(f"    isotropic     : type {s_iso['petrov']}, Psi2 = {s_iso['psi'][2]}")

    sq = sp.sqrt(2 * M / r)
    g_pg = Geometry(sp.Matrix([[-(1 - 2 * M / r), sq, 0, 0], [sq, 1, 0, 0],
                               [0, 0, r**2, 0], [0, 0, 0, r**2 * sp.sin(th)**2]]), [t, r, th, ph])
    ck.set_domain(sp.Q.positive(r - 2 * M), sp.Q.positive(sp.sin(th)))
    s_pg = ck.ck_signature(g_pg, "Schwarzschild [Painleve-Gullstrand]")
    print(f"    Painleve-G.   : type {s_pg['petrov']} (off-diagonal chart)")

    # the hard one: ZV at delta=1 in prolate spheroidal coordinates IS Schwarzschild (M=sigma=1)
    ck.set_domain(sp.Q.positive(x - 1), sp.Q.positive(1 - y**2))
    s_zv1 = ck.ck_signature(zipoy_voorhees(1, 1), "Zipoy-Voorhees delta=1 [prolate spheroidal]")
    print(f"    ZV delta=1    : type {s_zv1['petrov']}, Psi2 = {s_zv1['psi'][2]}   "
          "← no visible resemblance to -M/r^3")

    ck.set_domain(sp.Q.positive(r - 2), sp.Q.positive(sp.sin(th)))
    s_schw1 = ck.ck_signature(schwarzschild(1), "Schwarzschild M=1")
    print(f"    Schwarzschild M=1 certificate : {s_schw1['certificate']}")
    print(f"    ZV delta=1        certificate : {s_zv1['certificate']}")

    verdict("Schwarzschild vs isotropic chart", s_schw, s_iso, ck.EQUIVALENT)
    verdict("Schwarzschild vs Painleve-Gullstrand", s_schw, s_pg, ck.EQUIVALENT)
    verdict("Schwarzschild M=1 vs ZV delta=1 (prolate)", s_schw1, s_zv1, ck.EQUIVALENT)

    # ---------------------------------------------------------------- (B) type D, different
    print("\n(B) GENUINELY DIFFERENT SPACETIMES (Petrov D):")
    ck.set_domain(sp.Q.positive(r - 4), sp.Q.positive(sp.sin(th)))
    s_m2 = ck.ck_signature(schwarzschild(2), "Schwarzschild M=2")
    print(f"    M=2 certificate : {s_m2['certificate']}")
    # Schwarzschild-de Sitter has TWO horizons, so "r > 2M" does not fix the lapse sign and the
    # tool correctly refuses to guess; declare the static region between them instead.
    Lam = sp.Symbol("Lambda", positive=True)
    f_sds = 1 - 2 * M / r - Lam * r**2 / 3
    ck.set_domain(sp.Q.positive(f_sds), sp.Q.positive(sp.sin(th)), sp.Q.positive(r))
    s_sds = ck.ck_signature(
        Geometry(sp.diag(-f_sds, 1 / f_sds, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph]),
        "Schwarzschild-de Sitter")
    verdict("Schwarzschild M=1 vs M=2", s_schw1, s_m2, ck.INEQUIVALENT)
    verdict("Schwarzschild vs Schwarzschild-de Sitter", s_schw, s_sds, ck.INEQUIVALENT)

    # ---------------------------------------------------------------- (C) type I
    print("\n(C) THE GENERIC CASE — Petrov type I (Kasner vacua):")
    ck.set_domain(sp.Q.positive(T))
    p1, p2, p3 = kasner_exponents(2)
    q1, q2, q3 = kasner_exponents(1)
    print(f"    Kasner(u=2) exponents {p1},{p2},{p3}   "
          f"sum={sp.nsimplify(p1+p2+p3)} sum_sq={sp.nsimplify(p1**2+p2**2+p3**2)}")
    print(f"    Kasner(u=1) exponents {q1},{q2},{q3}   "
          f"sum={sp.nsimplify(q1+q2+q3)} sum_sq={sp.nsimplify(q1**2+q2**2+q3**2)}  "
          "(two equal -> locally rotationally symmetric)")
    s_k2 = ck.ck_signature(kasner(p1, p2, p3, 7), "Kasner(u=2)")
    s_k2p = ck.ck_signature(kasner(p2, p1, p3, 7), "Kasner(u=2) axes relabelled")
    s_k3 = ck.ck_signature(kasner(q1, q2, q3, 3), "Kasner(u=1), LRS")
    for s in (s_k2, s_k2p, s_k3):
        print(f"    {s['label']:32s}: type {s['petrov']}, isotropy {s['isotropy_dim']}, "
              f"t0={s['t0']} t1={s['t1']}, vacuum={s['ricci_scalar'] == 0}")
        print(f"        canonical Psi1=Psi3 ? "
              f"{sp.simplify(s['psi'][1] - s['psi'][3]) == 0};  Psi0=Psi4=0 ? "
              f"{s['psi'][0] == 0 and s['psi'][4] == 0}")
        print(f"        order-0 dimensionless ratios (chart-free labels): {s['order0_ratios']}")
    verdict("Kasner(u=2) vs same with axes relabelled", s_k2, s_k2p, ck.EQUIVALENT)
    verdict("Kasner(u=2) [type I] vs Kasner(u=1) LRS [type D]", s_k2, s_k3,
            ck.INEQUIVALENT)

    # ---------------------------------------------------------------- (D) the blind spot
    print("\n(D) THE BLIND SPOT CLOSED — VSI pp-waves (every polynomial invariant vanishes):")
    ck.set_domain()
    Ha, Hb, Hc = x**2 - y**2, 2 * x * y, (x**2 - y**2) / u**2
    for H, lab in ((Ha, "H = x^2-y^2"), (Hb, "H = 2xy"), (Hc, "H = (x^2-y^2)/u^2")):
        g_ = ppwave(H)
        print(f"    {lab:20s}: vacuum={g_.ricci.is_zero_matrix}, "
              f"Kretschmann={sp.simplify(g_.kretschmann)}, R={sp.simplify(g_.ricci_scalar)} "
              "→ §02 fingerprint: BLIND_SPOT")
    s_a = ck.ck_signature(ppwave(Ha), "pp-wave x^2-y^2", tet=pp_tetrad(Ha))
    s_b = ck.ck_signature(ppwave(Hb), "pp-wave 2xy", tet=pp_tetrad(Hb))
    s_c = ck.ck_signature(ppwave(Hc), "pp-wave (x^2-y^2)/u^2", tet=pp_tetrad(Hc))
    for s in (s_a, s_b, s_c):
        print(f"    {s['label']:26s}: type {s['petrov']}, Psi4 normalized = {s['psi'][4]}, "
              f"nabla C = 0 ? {s['nabla_C_zero']}")
    verdict("pp-wave x^2-y^2 vs 2xy (a rotation)", s_a, s_b, ck.EQUIVALENT)
    verdict("pp-wave x^2-y^2 vs (x^2-y^2)/u^2", s_a, s_c, ck.INEQUIVALENT)

    passed = all(ok)
    print(f"\nCARTAN-KARLHEDE: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          f"({sum(ok)}/{len(ok)} verdicts correct; types D, I decided, N via the tensorial "
          "nabla-C test; II/III and null-rotation isotropy honestly UNDECIDED)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
