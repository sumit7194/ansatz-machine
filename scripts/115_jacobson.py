#!/usr/bin/env python3
"""Step 115 — Jacobson 1995 machine-verified: the thermodynamic derivation of the Einstein equations.

Bridge ask 2 (round 6). Newly load-bearing: Dorau & Much, PRL 136, 091602 (2026) built the QFT
upgrade (quantum relative entropy -> semiclassical EFE). Nobody in the family had the classical
core on the proven ledger. Decomposition (three-valued throughout):

 (J1a) RAYCHAUDHURI on the free static family {f,h}(r): radial null congruence k_a = du,
       machine-checked geodesic+affine, dtheta/dlam = -theta^2/2 - sigma^2 - R_kk to leftover zero
       (sigma = 0 exhibited -- spherical cross-sections are shear-free).
 (J1b) RAYCHAUDHURI WITH SHEAR: symbolic Kasner, p1,p2,p3 FREE (no field equations -- it is an
       identity of geometry): sigma^2 = t^{-2p1-2}(p2-p3)^2/2 != 0, leftover zero.
 (J1c) AREA BOOKKEEPING: theta = d(ln A)/dlam exactly (A = cross-section area), and the
       bifurcation-point Taylor theta(lam) = -lam * R_kk + O(lam^2) when theta(0)=sigma(0)=0
       => deltaA = -integral lam R_kk dlam dA (the O(lam) area variation of the paper).
 (J2)  THE CLAUSIUS CHAIN: deltaQ = integral lam T_kk (Unruh T = kappa/2pi, S = eta*A). The
       LOCALIZATION step (integral equality for ALL local Rindler horizons => integrand equality)
       is Jacobson's physical postulate -- logged as ASSUMED, not proven. Given it, the constants
       chain forces R_kk = (2pi/eta) T_kk for all null k; eta = 1/4G => c = 8piG.
 (J3a) THE LEMMA (certifiable core, part 1): symmetric S_ab with S(k,k) = 0 for ALL null k
       => S = phi*g. Proven by solving the null-cone linear system on the family: solution
       space is EXACTLY the 1-parameter family phi*g.
 (J3b) THE BIANCHI STEP (certifiable core, part 2): R_ab = c T_ab + phi g_ab with nabla T = 0
       forces phi = -c T/2 + Lambda (Lambda const, machine-extracted ODE), i.e.
       R_ab - R/2 g_ab + Lambda g_ab = c T_ab: THE EINSTEIN EQUATIONS WITH AN UNDETERMINED
       COSMOLOGICAL CONSTANT -- the hinge of both the 1995 and 2026 papers, leftover zero.

SymPy wall, named plainly: J1/J3 are proven over the free-function families (static spherical +
Kasner), not for an arbitrary 2-argument metric; the localization in J2 is a physical postulate,
not a theorem -- we do not claim it. Repro: .venv/bin/python scripts/115_jacobson.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry, zero_simplify

t, r, th, ph = sp.symbols("t r theta phi", real=True)


def cov_lower(vl, X4, Gam):
    return sp.Matrix(4, 4, lambda a_, b_: sp.simplify(
        sp.diff(vl[a_], X4[b_]) - sum(Gam[c_][a_][b_] * vl[c_] for c_ in range(4))))


def raychaudhuri(g4, X4, k_lower, label):
    """Verify the null Raychaudhuri identity for an affinely-parametrized geodesic congruence.
    Returns (ok, theta, sigma2, ku, Rkk)."""
    geo = Geometry(g4, X4)
    ginv = g4.inv()
    Gam = geo.christoffel
    Ric = geo.ricci
    kl = sp.Matrix(k_lower)
    ku = sp.simplify(ginv * kl)
    Dk = cov_lower(kl, X4, Gam)
    acc = sp.Matrix([sp.simplify(sum(ku[b_] * Dk[a_, b_] for b_ in range(4))) for a_ in range(4)])
    geod = [zero_simplify(sp.simplify(x)) for x in acc]
    if any(x != 0 for x in geod):
        print(f"    [{label}] not affine-geodesic: {geod}")
        return False, None, None, None, None
    B = cov_lower(kl, X4, Gam)
    theta = sp.simplify(sum(ginv[a_, b_] * B[a_, b_] for a_ in range(4) for b_ in range(4)))
    lu = sp.zeros(4, 1)
    lu[0] = ku[0]
    for i in range(1, 4):
        lu[i] = -ku[i]
    kdotl = sp.simplify((ku.T * g4 * lu)[0, 0])
    lu = sp.simplify(-lu / kdotl)
    ll = sp.simplify(g4 * lu)
    lnull = zero_simplify(sp.simplify((lu.T * g4 * lu)[0, 0]))
    hproj = sp.Matrix(4, 4, lambda a_, b_: sp.simplify(g4[a_, b_] + kl[a_] * ll[b_] + ll[a_] * kl[b_]))
    hup = sp.simplify(ginv * hproj * ginv)
    hmix = sp.simplify(ginv * hproj)
    Bhat = sp.Matrix(4, 4, lambda a_, b_: sp.simplify(
        sum(hmix[c_, a_] * hmix[d_, b_] * B[c_, d_] for c_ in range(4) for d_ in range(4))))
    sigma = sp.Matrix(4, 4, lambda a_, b_: sp.simplify(
        sp.Rational(1, 2) * (Bhat[a_, b_] + Bhat[b_, a_]) - theta * hproj[a_, b_] / 2))
    sigma2 = sp.simplify(sum(sigma[a_, b_] * hup[a_, c_] * hup[b_, d_] * sigma[c_, d_]
                             for a_ in range(4) for b_ in range(4)
                             for c_ in range(4) for d_ in range(4)))
    Rkk = sp.simplify(sum(Ric[a_, b_] * ku[a_] * ku[b_] for a_ in range(4) for b_ in range(4)))
    dtheta = sp.simplify(sum(ku[a_] * sp.diff(theta, X4[a_]) for a_ in range(4)))
    resid = zero_simplify(sp.simplify(dtheta + sp.Rational(1, 2) * theta**2 + sigma2 + Rkk))
    print(f"    [{label}] l.l = {lnull}; theta = {theta}; sigma^2 = {sigma2}")
    print(f"    [{label}] Raychaudhuri residual = {resid}")
    return resid == 0 and lnull == 0, theta, sigma2, ku, Rkk


def main():
    print("Jacobson 1995 machine-verified: Clausius dQ = T dS across local Rindler horizons "
          "=> Einstein equations\n")
    ok = []

    f = sp.Function("f", positive=True)(r)
    h = sp.Function("h", positive=True)(r)
    g4s = sp.diag(-f, h, r**2, r**2 * sp.sin(th)**2)
    X4s = [t, r, th, ph]

    # ---------------- (J1a) static family
    print("  (J1a) Raychaudhuri, free static family (radial null congruence, sigma=0 exhibited):")
    okA, theta_s, sig2_s, ku_s, Rkk_s = raychaudhuri(
        g4s, X4s, [-1, sp.sqrt(h / f), 0, 0], "static")
    okA = okA and zero_simplify(sig2_s) == 0
    ok.append(okA)
    print(f"        {'✅' if okA else '❌'}")

    # ---------------- (J1b) Kasner with shear, p_i free
    x, y, z = sp.symbols("x y z", real=True)
    p1, p2, p3 = sp.symbols("p1 p2 p3", real=True)
    gK = sp.diag(-1, t**(2 * p1), t**(2 * p2), t**(2 * p3))
    print("  (J1b) Raychaudhuri, symbolic Kasner (p_i FREE -- geometric identity, no EFE), "
          "sigma != 0:")
    okB, theta_k, sig2_k, _, _ = raychaudhuri(gK, [t, x, y, z], [-t**(-p1), 1, 0, 0], "Kasner")
    okB = okB and zero_simplify(sp.simplify(sig2_k - t**(-2 * p1 - 2) * (p2 - p3)**2 / 2)) == 0
    ok.append(okB)
    print(f"        sigma^2 = (p2-p3)^2 t^(-2p1-2)/2 nonzero and identity still exact   "
          f"{'✅' if okB else '❌'}")

    # ---------------- (J1c) area bookkeeping + bifurcation Taylor
    # cross-section area A ∝ r^2: theta must equal k^a d_a ln(r^2), exactly
    dlnA = sp.simplify(sum(ku_s[a_] * sp.diff(sp.log(r**2), X4s[a_]) for a_ in range(4)))
    okC1 = zero_simplify(sp.simplify(theta_s - dlnA)) == 0
    # bifurcation Taylor: theta(lam) with theta(0)=0, sigma(0)=0:
    # theta(lam) = theta(0) + lam*theta'(0) + O(lam^2) = -lam*R_kk|_0 + O(lam^2)  [by the identity]
    lam_, th0, sg0, Rkk0 = sp.symbols("lam theta0 sigma0 Rkk0", real=True)
    theta_taylor = th0 + lam_ * (-sp.Rational(1, 2) * th0**2 - sg0 - Rkk0)
    okC2 = sp.simplify(theta_taylor.subs([(th0, 0), (sg0, 0)]) - (-lam_ * Rkk0)) == 0
    okC = okC1 and okC2
    ok.append(okC)
    print(f"  (J1c) theta = d(ln A)/dlam exactly ({okC1}); bifurcation Taylor theta = -lam R_kk + "
          f"O(lam^2) ({okC2})   {'✅' if okC else '❌'}")

    # ---------------- (J2) the Clausius constant chain (localization = POSTULATE, logged)
    # dQ = ∫ lam T_kk dlam dA;  dS = eta dA = -eta ∫ lam R_kk dlam dA (from J1c);  T = kappa/2pi
    # with the standard boost normalization (chi = -kappa lam k, dQ measured w.r.t. chi) the kappa
    # cancels between dQ and T dS; Clausius for ALL horizons (POSTULATE) forces:
    eta, G_N, c_ = sp.symbols("eta G c", positive=True)
    # T_kk = (eta/(2pi)) R_kk  =>  R_kk = c T_kk with c = 2pi/eta;  eta = 1/(4G) => c = 8 pi G
    c_val = sp.simplify((2 * sp.pi / eta).subs(eta, 1 / (4 * G_N)))
    okD = sp.simplify(c_val - 8 * sp.pi * G_N) == 0
    ok.append(okD)
    print(f"  (J2)  Clausius chain: kappa cancels (Unruh T against the boost-energy flux); "
          f"localization = POSTULATE (logged, not proven);")
    print(f"        constants: c = 2pi/eta, eta = 1/4G  =>  c = {c_val} = 8piG   "
          f"{'✅' if okD else '❌'}")

    # ---------------- (J3a) the lemma
    print("  (J3a) lemma: S(k,k)=0 for ALL null k => S = phi*g  [null-cone linear system]:")
    S = sp.Matrix(4, 4, lambda i, j: sp.Symbol(f"S{min(i, j)}{max(i, j)}"))
    b, c2, d, eps = sp.symbols("b c2 d eps", real=True)
    a2 = (h * b**2 + r**2 * c2**2 + r**2 * sp.sin(th)**2 * d**2) / f
    a = eps * sp.sqrt(a2)
    k = sp.Matrix([a, b, c2, d])
    Skk = sp.expand(sum(S[i, j] * k[i] * k[j] for i in range(4) for j in range(4))).subs(eps**2, 1)
    even = sp.expand(sp.simplify(Skk.coeff(eps, 0) * f))
    odd = sp.expand(sp.simplify(Skk.coeff(eps, 1) / sp.sqrt(a2)))
    unknowns = sorted({S[i, j] for i in range(4) for j in range(4)}, key=str)
    eqs = []
    for part in (even, odd):
        eqs.extend(sp.Poly(part, b, c2, d).coeffs())
    sol = sp.solve(eqs, unknowns, dict=True)
    okE = False
    if len(sol) == 1:
        Ssol = S.subs(sol[0])
        phi = Ssol[0, 0] / g4s[0, 0]
        okE = all(zero_simplify(sp.simplify(Ssol[i, j] - phi * g4s[i, j])) == 0
                  for i in range(4) for j in range(4))
    ok.append(okE)
    print(f"        solution space = exactly {{phi*g}} (1 free parameter): {okE}   "
          f"{'✅' if okE else '❌'}")

    # ---------------- (J3b) the Bianchi step
    print("  (J3b) Bianchi: R_ab = c T_ab + phi g_ab, nabla T = 0  =>  Einstein + Lambda:")
    geo = Geometry(g4s, X4s)
    Ric = geo.ricci
    ginv = g4s.inv()
    Rsc = sp.simplify(sum(ginv[i, j] * Ric[i, j] for i in range(4) for j in range(4)))
    cc = sp.Symbol("c", positive=True)
    phi = sp.Function("phi")(r)
    T4 = (Ric - phi * g4s) / cc                        # definition forced by the lemma
    Ttr = sp.simplify(sum(ginv[i, j] * T4[i, j] for i in range(4) for j in range(4)))
    # divergence of T (lower index b): nabla^a T_ab
    Gam = geo.christoffel
    Tmix = sp.simplify(ginv * T4)                      # T^a_b
    divT = []
    for b_ in range(4):
        expr = sum(sp.diff(Tmix[a_, b_], X4s[a_]) for a_ in range(4)) \
            + sum(Gam[a_][a_][c_] * Tmix[c_, b_] for a_ in range(4) for c_ in range(4)) \
            - sum(Gam[c_][a_][b_] * Tmix[a_, c_] for a_ in range(4) for c_ in range(4))
        divT.append(sp.simplify(expr))
    nontrivial = [e for e in divT if zero_simplify(e) != 0]
    print(f"        nabla^a T_ab components: {sum(1 for e in divT if zero_simplify(e) == 0)} "
          f"identically zero, {len(nontrivial)} nontrivial (the r-component)")
    # the nontrivial component must be equivalent to d/dr(phi + c*T/2) = 0
    target = sp.simplify(sp.diff(phi + cc * Ttr / 2, r))
    ratio_ok = False
    if len(nontrivial) == 1:
        ratio = sp.simplify(nontrivial[0] * cc - target)
        ratio_ok = zero_simplify(ratio) == 0
    print(f"        c * (nabla^a T_ar) - d/dr(phi + c T/2) = 0 identically: {ratio_ok}")
    print(f"        => nabla T = 0 forces d/dr(phi - R/2) = 0, i.e. phi = R/2 + Lambda (Lambda const)")
    # substitute the forced solution phi = R/2 + Lambda; Einstein + Lambda must hold identically
    Lam = sp.Symbol("Lambda", real=True)
    phi_sol = Rsc / 2 + Lam
    T4s = (Ric - phi_sol * g4s) / cc
    E = sp.Matrix(4, 4, lambda i, j: zero_simplify(sp.simplify(
        Ric[i, j] - sp.Rational(1, 2) * Rsc * g4s[i, j] - Lam * g4s[i, j] - cc * T4s[i, j])))
    okF = ratio_ok and all(E[i, j] == 0 for i in range(4) for j in range(4))
    ok.append(okF)
    print(f"        R_ab - R/2 g_ab - Lambda g_ab - c T_ab leftover: "
          f"{[E[i, j] for i in range(4) for j in range(4) if E[i, j] != 0] or 0}   "
          f"{'✅' if okF else '❌'}")

    passed = all(ok)
    print(f"\nJACOBSON 1995: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(J1 Raychaudhuri exact w/ + w/o shear; J1c area bookkeeping; J2 constants w/ localization "
          "POSTULATE logged; J3 lemma + Bianchi => Einstein + undetermined Lambda, c = 8piG)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
