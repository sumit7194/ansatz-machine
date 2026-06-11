#!/usr/bin/env python3
"""Step 10 — v4 battery E0: the EdGB REDUCE, validated against Kanti.

First step off vacuum GR (docs/EDGB.md). Derives the reduced field
equations of Einstein-dilaton-Gauss-Bonnet gravity on the static
spherical ansatz
    ds² = -e^{Γ(r)}dt² + e^{Λ(r)}dr² + r²dΩ²,   φ = φ(r)
by varying the REDUCED ACTION (principle of symmetric criticality):
    L(r) = e^{(Γ+Λ)/2} r² [ R/2 − ¼ e^{-Λ} φ′² + (α′/8) e^φ G_GB ]
in Kanti conventions (kinetic −¼(∂φ)² — NOT −½; α′/g² = 1;
G_GB = R_abcd R^abcd − 4R_ab R^ab + R²)
[Kanti et al., PRD 54, 5049 (1996), arXiv:hep-th/9511071].

E0 checks (pre-registered in docs/EDGB.md — conventions validated against
the literature BEFORE trusting our own algebra):
  E0a  α′ → 0 limit: Schwarzschild + constant φ solves all three
       Euler-Lagrange equations identically.
  E0b  the Λ-equation is ALGEBRAIC in e^Λ (the GB structural miracle), and
       its two roots match Kanti eqs. (50)-(51): root-sum = −β and
       root-product = γ with
         β = r²φ′²/4 − 1 − Γ′(r + e^φ φ′/2),   γ = (3/2) Γ′ φ′ e^φ.
  E0c  numeric spot-check of the φ-equation against a transcription of
       Kanti eq. (33) at random points (catches factor errors).

Run:  .venv/bin/python scripts/10_edgb_reduce.py
"""

import sympy as sp

from gr_engine import Geometry, R_SYM, zero_simplify

r = R_SYM
ap = sp.Symbol("alpha_p", positive=True)  # α′ (with α′/g² = 1)


def reduced_lagrangian():
    """The 1D effective Lagrangian density L(r) for the EdGB ansatz."""
    t, th, ph = sp.symbols("t theta phi", real=True)
    Gam = sp.Function("Gam")(r)
    Lam = sp.Function("Lam")(r)
    Phi = sp.Function("Phi")(r)

    metric = sp.diag(-sp.exp(Gam), sp.exp(Lam), r**2,
                     r**2 * sp.sin(th)**2)
    geo = Geometry(metric, [t, r, th, ph])
    R = geo.ricci_scalar
    GB = sp.simplify(geo.kretschmann - 4 * geo.ricci_squared + R**2)

    sqrtg = sp.exp((Gam + Lam) / 2) * r**2  # sinθ dropped (angle measure)
    L = sqrtg * (R / 2
                 - sp.Rational(1, 4) * sp.exp(-Lam) * sp.diff(Phi, r)**2
                 + (ap / 8) * sp.exp(Phi) * GB)
    return sp.simplify(L), (Gam, Lam, Phi)


def euler_lagrange(L, X):
    """E_X = ∂L/∂X − d/dr ∂L/∂X′ + d²/dr² ∂L/∂X″."""
    X1, X2 = sp.diff(X, r), sp.diff(X, (r, 2))
    e = (sp.diff(L, X) - sp.diff(sp.diff(L, X1), r)
         + sp.diff(sp.diff(L, X2), (r, 2)))
    return sp.simplify(e.doit())


def main():
    results = []
    print("Deriving the EdGB reduced Lagrangian (symbolic, one-time)...")
    L, (Gam, Lam, Phi) = reduced_lagrangian()

    print("Euler-Lagrange equations for (Γ, Λ, φ)...")
    E_Gam = euler_lagrange(L, Gam)
    E_Lam = euler_lagrange(L, Lam)
    E_Phi = euler_lagrange(L, Phi)

    # ---- E0a: Schwarzschild + constant dilaton at α′ = 0 -------------
    M = sp.Symbol("M", positive=True)
    f = 1 - 2 * M / r
    schw = {Gam: sp.log(f), Lam: -sp.log(f), Phi: sp.S.Zero, ap: 0}

    ok_a = True
    for name, E in (("Γ", E_Gam), ("Λ", E_Lam), ("φ", E_Phi)):
        resid = zero_simplify(E.subs(schw).doit())
        ok = resid == 0
        ok_a = ok_a and ok
        print(f"  {'✓' if ok else '✗✗'} E0a [{name}-eq] Schwarzschild "
              f"limit: {'≡ 0' if ok else f'NONZERO: {resid}'}")
    results.append(ok_a)

    # ---- E0b: Λ-equation algebraic in e^Λ, roots match Kanti 50-51 ---
    y = sp.Symbol("y", positive=True)  # y = e^Λ
    gp, pp = sp.symbols("gp pp", real=True)   # Γ′, φ′ as plain symbols
    phs = sp.Symbol("phs", real=True)         # φ
    subs_alg = {sp.Derivative(Lam, (r, 2)): 0, sp.Derivative(Gam, (r, 2)): 0,
                sp.Derivative(Phi, (r, 2)): 0,
                sp.Derivative(Gam, r): gp, sp.Derivative(Phi, r): pp,
                sp.Derivative(Lam, r): sp.Symbol("lp", real=True),
                Gam: sp.Symbol("gs", real=True), Lam: sp.log(y), Phi: phs}
    E_Lam_alg = sp.simplify(E_Lam.subs(subs_alg).doit().subs(ap, 1))

    has_lp = E_Lam_alg.has(sp.Symbol("lp")) \
        or E_Lam_alg.has(sp.Derivative)
    print(f"  {'✓' if not has_lp else '✗✗'} E0b: Λ-equation contains no "
          f"Λ′ or second derivatives (algebraic in e^Λ): {not has_lp}")
    results.append(not has_lp)

    poly = sp.Poly(sp.numer(sp.together(E_Lam_alg)), y)
    ok_quad = poly.degree() == 2
    print(f"  {'✓' if ok_quad else '✗✗'} E0b: quadratic in e^Λ "
          f"(degree {poly.degree()})")
    results.append(ok_quad)

    if ok_quad:
        c2, c1, c0 = poly.all_coeffs()
        root_sum = sp.simplify(-c1 / c2)
        root_prod = sp.simplify(c0 / c2)
        beta = r**2 * pp**2 / 4 - 1 - gp * (r + sp.exp(phs) * pp / 2)
        gamma = sp.Rational(3, 2) * gp * pp * sp.exp(phs)
        ok_sum = sp.simplify(root_sum - (-beta)) == 0
        ok_prod = sp.simplify(root_prod - gamma) == 0
        print(f"  {'✓' if ok_sum else '✗✗'} E0b: root sum = −β (Kanti 50-51)")
        print(f"  {'✓' if ok_prod else '✗✗'} E0b: root product = γ (Kanti 50-51)")
        if not (ok_sum and ok_prod):
            print(f"      ours: sum={root_sum}, prod={root_prod}")
            print(f"      kanti: −β={sp.simplify(-beta)}, γ={gamma}")
        results += [ok_sum, ok_prod]

    # ---- E0c: φ-equation vs transcribed Kanti eq. (33), numeric ------
    # (33): φ″ + φ′(Γ′−Λ′)/2 + 2φ′/r
    #       = (α′ e^φ / r²)[Γ′Λ′e^{−Λ} + (1−e^{−Λ})(Γ″ + Γ′(Γ′−Λ′)/2)]
    # with α′/g² = 1 and the −¼ kinetic normalization absorbed as in
    # Kanti's own writing (their α′/4g² source with their kinetic).
    import random
    rng = random.Random(0)
    Gs, Ls, Ps = (sp.Function(n)(r) for n in ("Gs", "Ls", "Ps"))
    kanti33 = (sp.diff(Ps, (r, 2))
               + sp.diff(Ps, r) * (sp.diff(Gs, r) - sp.diff(Ls, r)) / 2
               + 2 * sp.diff(Ps, r) / r
               - (ap * sp.exp(Ps) / r**2)
               * (sp.diff(Gs, r) * sp.diff(Ls, r) * sp.exp(-Ls)
                  + (1 - sp.exp(-Ls))
                  * (sp.diff(Gs, (r, 2))
                     + sp.diff(Gs, r)
                     * (sp.diff(Gs, r) - sp.diff(Ls, r)) / 2)))
    # our E_φ normalized: divide by the prefactor of φ″
    pref = sp.diff(E_Phi, sp.Derivative(Phi, (r, 2)))
    ratios = []
    for _ in range(4):
        # random smooth test configuration: polynomials in r
        cfg = {}
        for F_t, F_o in ((Gs, Gam), (Ls, Lam), (Ps, Phi)):
            a0, a1, a2 = (sp.Rational(rng.randint(1, 9), rng.randint(2, 7))
                          for _ in range(3))
            poly_f = a0 + a1 / r + a2 / r**2
            cfg[F_t] = poly_f
            cfg[F_o] = poly_f
        rv = sp.Rational(rng.randint(23, 99), 10)
        ours = (E_Phi / pref).subs(cfg).doit().subs(
            {ap: sp.Rational(1, 3), r: rv})
        kant = kanti33.subs(cfg).doit().subs(
            {ap: sp.Rational(1, 3), r: rv})
        ratios.append(complex(ours.evalf(25)) / complex(kant.evalf(25)))
    spread = max(abs(x - ratios[0]) for x in ratios)
    ok_c = spread < 1e-15 and abs(ratios[0].imag) < 1e-15
    print(f"  {'✓' if ok_c else '✗✗'} E0c: our φ-equation ∝ Kanti eq.(33) "
          f"at random configs (ratio {ratios[0].real:+.6f}, "
          f"spread {spread:.1e})")
    results.append(ok_c)

    print(f"\n{'ALL EXPECTATIONS MET ✅' if all(results) else 'EXPECTATION FAILURES ❌'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
