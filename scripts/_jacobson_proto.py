#!/usr/bin/env python3
"""Prototype — §115 Jacobson 1995, the risky legs (bridge ask 2).

(J3a) THE LEMMA: symmetric S_ab with S(k,k)=0 for ALL null k  =>  S = phi * g.
      Machine proof on the free static family: parametrize the null cone, expand S(k,k) as a
      polynomial in the free spatial components, solve the linear system in the 10 unknown S_ab.
      The solution space must be EXACTLY the 1-parameter family S = phi*g.

(J1a) RAYCHAUDHURI on the free family: radial null congruence k_a = grad(t - r*), machine-affinized,
      verify d(theta)/dlam = -theta^2/2 - sigma^2 - R_ab k^a k^b to leftover zero (sigma = 0 here).

(J1b) RAYCHAUDHURI with SHEAR: symbolic Kasner ds^2 = -dt^2 + t^{2p1}dx^2 + t^{2p2}dy^2 + t^{2p3}dz^2
      (p1,p2,p3 FREE symbols -- the identity needs no field equations), null congruence along x,
      sigma^2 != 0, verify the full identity to leftover zero.

Durable log data/jacobson_proto.log.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry, zero_simplify

t, r, th, ph = sp.symbols("t r theta phi", real=True)


# ---------------------------------------------------------------- (J3a) the lemma
def lemma_null_cone():
    print("(J3a) lemma: S(k,k)=0 for all null k  =>  S = phi*g   [free static family]")
    f = sp.Function("f", positive=True)(r)
    h = sp.Function("h", positive=True)(r)
    g4 = sp.diag(-f, h, r**2, r**2 * sp.sin(th)**2)
    S = sp.Matrix(4, 4, lambda i, j: sp.Symbol(f"S{min(i,j)}{max(i,j)}"))
    b, c, d, eps = sp.symbols("b c d eps", real=True)     # spatial direction + sign of k^t
    a2 = (h * b**2 + r**2 * c**2 + r**2 * sp.sin(th)**2 * d**2) / f   # (k^t)^2 from nullness
    a = eps * sp.sqrt(a2)                                  # eps = +-1 covers both cone sheets
    k = sp.Matrix([a, b, c, d])
    Skk = sp.expand(sum(S[i, j] * k[i] * k[j] for i in range(4) for j in range(4)))
    # both signs of eps: even part (eps^2 -> 1) and odd part (coefficient of eps) vanish separately
    Skk = Skk.subs(eps**2, 1)
    even = Skk.coeff(eps, 0)
    odd = Skk.coeff(eps, 1)
    unknowns = sorted({S[i, j] for i in range(4) for j in range(4)}, key=str)
    # odd part = sqrt(a2) * (linear in b,c,d); sqrt(a2) > 0 generically -> divide it out.
    odd = sp.expand(sp.simplify(odd / sp.sqrt(a2)))
    even = sp.expand(sp.simplify(even * f))          # clear the 1/f from a^2 = a2
    eqs = []
    for part in (even, odd):
        poly = sp.Poly(part, b, c, d)
        eqs.extend(poly.coeffs())
    sol = sp.solve(eqs, unknowns, dict=True)
    print(f"    linear system solved: {sol}")
    if len(sol) == 1:
        s = sol[0]
        Ssol = S.subs(s)
        # the solution must be proportional to g: S = (S00/g00) * g
        phi = Ssol[0, 0] / g4[0, 0]
        ok = all(zero_simplify(sp.simplify(Ssol[i, j] - phi * g4[i, j])) == 0
                 for i in range(4) for j in range(4))
        print(f"    S = phi*g with phi = {sp.simplify(phi)}: {ok}")
        return ok
    return False


# ---------------------------------------------------------------- Raychaudhuri machinery
def raychaudhuri(g4, X4, k_lower, label):
    """Verify d(theta)/dlam = -theta^2/2 - sigma^2 - R_ab k^a k^b for an affinely-parametrized
    null geodesic congruence given by k_a (lower index). Machine-affinizes if needed."""
    print(f"(J1) Raychaudhuri [{label}]")
    geo = Geometry(g4, X4)
    ginv = g4.inv()
    Gam = geo.christoffel
    Ric = geo.ricci
    kl = sp.Matrix(k_lower)
    ku = sp.simplify(ginv * kl)

    def cov_lower(vl):
        # nabla_b v_a  (a rows, b cols)
        return sp.Matrix(4, 4, lambda a_, b_: sp.simplify(
            sp.diff(vl[a_], X4[b_]) - sum(Gam[c_][a_][b_] * vl[c_] for c_ in range(4))))

    # geodesic check + affinization: k^b nabla_b k_a = kappa k_a
    Dk = cov_lower(kl)
    acc = sp.Matrix([sp.simplify(sum(ku[b_] * Dk[a_, b_] for b_ in range(4))) for a_ in range(4)])
    kap = sp.simplify(acc[0] / kl[0]) if kl[0] != 0 else sp.simplify(acc[1] / kl[1])
    nonaff = [zero_simplify(sp.simplify(acc[a_] - kap * kl[a_])) for a_ in range(4)]
    print(f"    geodesic (k.grad k = kappa k): residuals {nonaff}, kappa = {kap}")
    if any(x != 0 for x in nonaff):
        print("    NOT geodesic -- abort"); return False
    if zero_simplify(kap) != 0:
        # affinize: k -> e^psi k with k^a d_a psi = -kappa (psi = psi(r) or psi(t) by symmetry)
        var = X4[1] if all(sp.diff(kap, X4[0]) == 0 for _ in [0]) and ku[1] != 0 else X4[0]
        psi = sp.Symbol("psi_placeholder")
        # solve k^a d_a psi(var) = -kappa  ->  psi' = -kappa / k^var
        idx = X4.index(var)
        psip = sp.simplify(-kap / ku[idx])
        Psi = sp.integrate(psip, var)
        scale = sp.exp(Psi)
        kl = sp.simplify(scale * kl)
        ku = sp.simplify(ginv * kl)
        Dk = cov_lower(kl)
        acc = sp.Matrix([sp.simplify(sum(ku[b_] * Dk[a_, b_] for b_ in range(4))) for a_ in range(4)])
        aff = [zero_simplify(sp.simplify(x)) for x in acc]
        print(f"    affinized with e^psi, psi' = {psip}: residuals {aff}")
        if any(x != 0 for x in aff):
            print("    affinization failed -- abort"); return False

    # B_ab = nabla_b k_a; theta = g^{ab} B_ab (affine null geodesic: trace = 2D expansion)
    B = cov_lower(kl)
    theta = sp.simplify(sum(ginv[a_, b_] * B[a_, b_] for a_ in range(4) for b_ in range(4)))
    # auxiliary null l with k.l = -1 to build the transverse projector
    # construct l: try l ~ (k_t, -k_r, 0, 0)-type reflection, normalized
    lu = sp.zeros(4, 1)
    # generic construction: flip the spatial part of k^a, then normalize
    ku_t = ku[0]
    lu[0] = ku_t
    for i in range(1, 4):
        lu[i] = -ku[i]
    # make l null: it is (same cone, reflected) if metric static diag -- verify, then normalize k.l = -1
    ll = sp.simplify(g4 * lu)
    lnull = zero_simplify(sp.simplify((lu.T * g4 * lu)[0, 0]))
    kdotl = sp.simplify((ku.T * g4 * lu)[0, 0])
    lu = sp.simplify(-lu / kdotl)
    ll = sp.simplify(g4 * lu)
    print(f"    aux null l built (l.l = {lnull}), normalized k.l = -1")
    hproj = sp.Matrix(4, 4, lambda a_, b_: sp.simplify(
        g4[a_, b_] + kl[a_] * ll[b_] + ll[a_] * kl[b_]))
    hup = sp.simplify(ginv * hproj * ginv)   # h^{ab}
    # transverse-projected B: Bhat_{ab} = h_a^c h_b^d B_{cd}; sigma = sym traceless part
    hmix = sp.simplify(ginv * hproj)          # h^a_b ... careful ordering
    Bhat = sp.Matrix(4, 4, lambda a_, b_: sp.simplify(
        sum(hmix[c_, a_] * hmix[d_, b_] * B[c_, d_] for c_ in range(4) for d_ in range(4))))
    theta_check = sp.simplify(sum(hup[a_, b_] * Bhat[a_, b_] for a_ in range(4) for b_ in range(4)))
    sigma = sp.Matrix(4, 4, lambda a_, b_: sp.simplify(
        sp.Rational(1, 2) * (Bhat[a_, b_] + Bhat[b_, a_]) - sp.Rational(1, 2) * theta * hproj[a_, b_] / 1))
    # NOTE: transverse space is 2D -> trace removal uses theta/2 * h_ab
    sigma2 = sp.simplify(sum(sigma[a_, b_] * hup[a_, c_] * hup[b_, d_] * sigma[c_, d_]
                             for a_ in range(4) for b_ in range(4) for c_ in range(4) for d_ in range(4)))
    Rkk = sp.simplify(sum(Ric[a_, b_] * ku[a_] * ku[b_] for a_ in range(4) for b_ in range(4)))
    dtheta = sp.simplify(sum(ku[a_] * sp.diff(theta, X4[a_]) for a_ in range(4)))
    resid = zero_simplify(sp.simplify(dtheta + sp.Rational(1, 2) * theta**2 + sigma2 + Rkk))
    print(f"    theta = {theta}  (transverse-trace check: {zero_simplify(sp.simplify(theta - theta_check))})")
    print(f"    sigma^2 = {sigma2}")
    print(f"    RAYCHAUDHURI residual dtheta/dlam + theta^2/2 + sigma^2 + R_kk = {resid}   "
          f"{'OK' if resid == 0 else 'FAIL'}")
    return resid == 0


ok1 = lemma_null_cone()
print()

# (J1a) free static family, radial outgoing null congruence: k_a = -(dt - sqrt(h/f) dr) (ingoing sign
# choice irrelevant); gradient of u = t - r_* -> automatically geodesic (non-affine in general)
f = sp.Function("f", positive=True)(r)
h = sp.Function("h", positive=True)(r)
g4s = sp.diag(-f, h, r**2, r**2 * sp.sin(th)**2)
kl_static = [-1, sp.sqrt(h / f), 0, 0]     # k_a from du, sign for future-outgoing k^a
ok2 = raychaudhuri(g4s, [t, r, th, ph], kl_static, "free static family (sigma=0 expected)")
print()

# (J1b) symbolic Kasner, congruence along x: k_a = (-t^{p1}, 1, 0, 0) -- closed 1-form, null
x, y, z = sp.symbols("x y z", real=True)
p1, p2, p3 = sp.symbols("p1 p2 p3", real=True)
gK = sp.diag(-1, t**(2 * p1), t**(2 * p2), t**(2 * p3))
kl_kasner = [-t**(-p1), 1, 0, 0]
ok3 = raychaudhuri(gK, [t, x, y, z], kl_kasner, "symbolic Kasner (sigma != 0, p_i FREE)")

print(f"\nPROTO: lemma {ok1}, static Raychaudhuri {ok2}, Kasner Raychaudhuri {ok3}")
