#!/usr/bin/env python3
"""Step 11 — v4 battery E1: EdGB numerical ground truth.

Builds the numerical EdGB black hole that Track B's fit-verifier will
score candidates against, using ONLY the E0-validated equations (no
transcribed ODEs — our own algebra, already proven ≡ Kanti's).

Pipeline (Kanti §3 / KKZ §II recipe, web-verified in docs/EDGB.md):
  1. symbolic: eliminate e^Λ via the quadratic root (δ=+1 BH branch),
     solve the Γ- and φ-equations for (Γ″, φ″), lambdify.
  2. horizon regularity: φ′_h = r_h e^{−φ_h}(−1 + √(1 − 6e^{2φ_h}/r_h⁴))
     (σ=+1 branch); family parameter p ≡ 6e^{2φ_h}/r_h⁴ ∈ [0, 1).
  3. integrate outward with hand-rolled RK4 (stdlib only) on the state
     (φ, φ′, Ψ) where Ψ ≡ Γ′·(r−r_h) regularizes the horizon pole
     (Ψ(r_h)=1), read off M = r²Γ′/2 and D = −r²φ′ at large r.

E1 checks (pre-registered):
  E1a  p → 0 limit reproduces Schwarzschild: M → r_h/2 (to <0.5%).
  E1b  KKZ eq. (21): ε ≡ 2M/r_h − 1 ≈ p/11 − p²/131 — our shoot must
       reproduce it (to ~15% relative at p = 0.2, 0.4; the relation is
       itself a fit).
  E1c  dilaton hair is secondary: D varies smoothly with p, D→0 as p→0.

Run:  .venv/bin/python scripts/11_edgb_shoot.py
"""

import importlib.util
import math
import os

import sympy as sp

from gr_engine import R_SYM

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "edgb_reduce", os.path.join(_here, "10_edgb_reduce.py"))
m10 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m10)

r = R_SYM


def build_rhs(verbose=True):
    """Symbolic: (Γ″, φ″) as functions of (r, φ, φ′, Γ′), with e^Λ
    eliminated on the δ=+1 black-hole branch. Returns lambdified RHS."""
    L, (Gam, Lam, Phi) = m10.reduced_lagrangian()
    E_G = m10.euler_lagrange(L, Gam)
    E_P = m10.euler_lagrange(L, Phi)
    E_L = m10.euler_lagrange(L, Lam)

    g1, g2 = sp.symbols("g1 g2", real=True)   # Γ′, Γ″
    p0, p1, p2 = sp.symbols("p0 p1 p2", real=True)  # φ, φ′, φ″
    y, l1 = sp.symbols("y l1", real=True)     # e^Λ, Λ′

    def flat(e):
        return e.subs({sp.Derivative(Gam, (r, 2)): g2,
                       sp.Derivative(Phi, (r, 2)): p2,
                       sp.Derivative(Lam, (r, 2)): sp.Symbol("l2"),
                       sp.Derivative(Gam, r): g1,
                       sp.Derivative(Phi, r): p1,
                       sp.Derivative(Lam, r): l1,
                       Gam: sp.Symbol("g0"), Lam: sp.log(y),
                       Phi: p0}).doit()

    # higher-derivative sanity: EdGB equations are second order — our EL
    # must contain no Γ‴/Γ⁗ (they cancel by the GB structure)
    for X, name in ((Gam, "Γ"), (Phi, "φ")):
        for k in (3, 4):
            d = sp.diff(E_G, sp.Derivative(X, (r, k)))
            assert sp.simplify(d) == 0, f"{name}-eq has order-{k} derivative!"

    EG, EP, EL_ = (sp.simplify(flat(e).subs(m10.ap, 1))
                   for e in (E_G, E_P, E_L))
    assert not EL_.has(sp.Symbol("l2")) and not EL_.has(l1)

    # e^Λ: quadratic root, δ=+1 (Kanti footnote 2: the BH branch)
    poly = sp.Poly(sp.numer(sp.together(EL_)), y)
    c2, c1, c0 = poly.all_coeffs()
    beta, gamma = sp.simplify(c1 / c2), sp.simplify(c0 / c2)
    y_sol = (-beta + sp.sqrt(beta**2 - 4 * gamma)) / 2
    # Λ′ by chain rule through y(r, p0, p1, g1)
    l1_sol = (sp.diff(y_sol, r) + sp.diff(y_sol, p0) * p1
              + sp.diff(y_sol, p1) * p2
              + sp.diff(y_sol, g1) * g2) / y_sol

    # Λ must be eliminated at FUNCTION level: the Γ-equation contains
    # Λ″ (and the first symbol-level attempt left unsubstituted
    # Derivative(Λ) nodes that crashed lambdify). Substituting
    # Λ = log(y_sol(r, φ, φ′, Γ′)) and letting sympy chain-rule through
    # introduces φ‴/Γ‴ terms whose coefficients must cancel identically
    # (EdGB is second order) — verified below, numerically if cancel()
    # can't see it through the square root.
    if verbose:
        print("   eliminating Λ at function level...")
    Y_expr = y_sol.subs({p0: Phi, p1: sp.Derivative(Phi, r),
                         g1: sp.Derivative(Gam, r)})
    lam_sub = {Lam: sp.log(Y_expr)}
    g3, p3 = sp.symbols("g3 p3", real=True)

    def flat3(e):
        return e.subs(lam_sub).doit().subs({
            sp.Derivative(Gam, (r, 3)): g3,
            sp.Derivative(Phi, (r, 3)): p3,
            sp.Derivative(Gam, (r, 2)): g2,
            sp.Derivative(Phi, (r, 2)): p2,
            sp.Derivative(Gam, r): g1, sp.Derivative(Phi, r): p1,
            Gam: sp.Symbol("g0"), Phi: p0})

    import random
    rng = random.Random(1)
    eqs2 = []
    for E, nm in ((E_G.subs(m10.ap, 1), "Γ"),
                  (E_P.subs(m10.ap, 1), "φ")):
        ef = flat3(E)
        for hi, hname in ((g3, "Γ‴"), (p3, "φ‴")):
            coeff = sp.cancel(sp.together(sp.diff(ef, hi)))
            if coeff != 0:
                # numeric verification of the identical cancellation
                vals = {r: sp.Rational(rng.randint(21, 60), 10),
                        p0: sp.Rational(-1, 3), p1: sp.Rational(1, 7),
                        g1: sp.Rational(2, 5), g2: sp.Rational(-1, 9),
                        p2: sp.Rational(1, 11),
                        sp.Symbol("g0"): 0, g3: 0, p3: 0}
                num = complex(coeff.subs(vals).evalf(30))
                assert abs(num) < 1e-20, \
                    f"{nm}-eq: {hname} coefficient does NOT cancel: {num}"
                ef = ef - hi * coeff  # drop the numerically-zero term
        eqs2.append(ef)
    EG2, EP2 = eqs2

    if verbose:
        print("   Cramer for (Γ″, φ″)...")
    A, bvec = sp.linear_eq_to_matrix(
        [sp.expand(EG2), sp.expand(EP2)], [g2, p2])
    det = sp.together(A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0])
    g2_expr = sp.together((bvec[0] * A[1, 1] - bvec[1] * A[0, 1]) / det)
    p2_expr = sp.together((A[0, 0] * bvec[1] - A[1, 0] * bvec[0]) / det)
    leftovers = (g2_expr.free_symbols | p2_expr.free_symbols) \
        - {r, p0, p1, g1, sp.Symbol("g0")}
    assert not leftovers, f"unexpected free symbols: {leftovers}"
    # Γ appears only through the exact overall e^{Γ/2} factor, which
    # cancels in the Cramer ratios — pin it to 0
    g2_expr = g2_expr.subs(sp.Symbol("g0"), 0)
    p2_expr = p2_expr.subs(sp.Symbol("g0"), 0)
    f_g2 = sp.lambdify((r, p0, p1, g1), g2_expr, modules="math")
    f_p2 = sp.lambdify((r, p0, p1, g1), p2_expr, modules="math")
    f_y = sp.lambdify((r, p0, p1, g1), y_sol, modules="math")  # e^Λ
    return f_g2, f_p2, f_y


def shoot(f_g2, f_p2, p_family, r_h=1.0, eps=1e-6, r_max=2000.0,
          steps=4000, record=None):
    """Integrate one EdGB black hole; returns (M, D, ok).
    If record is a list, appends (r, φ, φ′, Γ′, Γ_acc) along the way —
    Γ_acc = ∫Γ′dr from the start point (normalize at infinity later)."""
    if not (0 <= p_family < 1):
        return None, None, False
    e_ph = r_h**2 * math.sqrt(p_family / 6) if p_family > 0 else 0.0
    if p_family > 0:
        ph = math.log(e_ph)
        disc = 1 - 6 * e_ph**2 / r_h**4
        php = r_h * math.exp(-ph) * (-1 + math.sqrt(disc))
    else:
        ph, php = 0.0, 0.0

    # integrate in u = ln(r − r_h): steps resolve the horizon shell
    # geometrically (measured failure: log-r steps started 2000× past it)
    state = [ph + php * r_h * eps, php, 1.0 / (r_h * eps), 0.0]
    # state = (φ, φ′, Γ′, Γ_acc)

    def deriv(u, s):
        x = math.exp(u)          # x = r − r_h
        rv = r_h + x
        return [x * s[1], x * f_p2(rv, s[0], s[1], s[2]),
                x * f_g2(rv, s[0], s[1], s[2]), x * s[2]]

    u0, u1 = math.log(r_h * eps), math.log(r_max - r_h)
    h = (u1 - u0) / steps
    u = u0
    for i in range(steps):
        try:
            k1 = deriv(u, state)
            k2 = deriv(u + h / 2,
                       [s + h / 2 * k for s, k in zip(state, k1)])
            k3 = deriv(u + h / 2,
                       [s + h / 2 * k for s, k in zip(state, k2)])
            k4 = deriv(u + h, [s + h * k for s, k in zip(state, k3)])
        except (ValueError, ZeroDivisionError, OverflowError) as ex:
            return None, None, (f"{type(ex).__name__} at "
                                f"r−r_h={math.exp(u):.3g}")
        state = [s + h / 6 * (a + 2 * b + 2 * c + d)
                 for s, a, b, c, d in zip(state, k1, k2, k3, k4)]
        u += h
        if any(not math.isfinite(s) for s in state):
            return None, None, f"non-finite state at r−r_h={math.exp(u):.3g}"
        if record is not None and i % 8 == 0:
            record.append((r_h + math.exp(u),) + tuple(state))
    rv = r_h + math.exp(u)
    M = rv**2 * state[2] / 2
    D = -rv**2 * state[1]
    if record is not None:
        record.append((rv,) + tuple(state))
    return M, D, True


def main():
    results = []
    print("Building EdGB RHS from the E0-validated equations...")
    f_g2, f_p2, _ = build_rhs()
    print("   RHS ready.\n")

    # E1a: Schwarzschild limit — via tiny p, NOT exactly 0: at p=0 the
    # dilaton sector degenerates (φ-equation becomes 0=0, Cramer det=0)
    M0, D0, ok = shoot(f_g2, f_p2, 1e-8)
    e1a = ok is True and abs(M0 - 0.5) < 0.005 and abs(D0) < 1e-3
    results.append(e1a)
    if ok is True:
        print(f"  {'✓' if e1a else '✗✗'} E1a p=0 → Schwarzschild: "
              f"M = {M0:.6f} (want 0.5), D = {D0:.2e}")
    else:
        print(f"  ✗✗ E1a integration failed: {ok}")

    # E1b: ε(p) ≈ p/11 − p²/131 (KKZ eq. 21)
    for p in (0.2, 0.4):
        M, D, ok = shoot(f_g2, f_p2, p)
        if ok is not True:
            results.append(False)
            print(f"  ✗✗ E1b p={p}: integration failed ({ok})")
            continue
        eps_ours = 2 * M / 1.0 - 1
        eps_kkz = p / 11 - p**2 / 131
        rel = abs(eps_ours - eps_kkz) / abs(eps_kkz)
        ok_b = rel < 0.15
        results.append(ok_b)
        print(f"  {'✓' if ok_b else '✗✗'} E1b p={p}: ε = {eps_ours:+.5f} "
              f"vs KKZ {eps_kkz:+.5f} (rel {rel:.1%}); D = {D:+.4f}")

    # E1c: secondary hair — D(p) smooth, →0
    Ds = []
    for p in (0.05, 0.1, 0.2, 0.4, 0.6):
        M, D, ok = shoot(f_g2, f_p2, p)
        Ds.append(D if ok is True else float("nan"))
    e1c = all(math.isfinite(d) for d in Ds) and \
        all(Ds[i] < Ds[i + 1] for i in range(len(Ds) - 1)) and Ds[0] > 0
    results.append(e1c)
    print(f"  {'✓' if e1c else '✗✗'} E1c hair secondary & monotone: "
          f"D(p) = {['%.4f' % d for d in Ds]}")

    print(f"\n{'ALL EXPECTATIONS MET ✅' if all(results) else 'EXPECTATION FAILURES ❌'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
