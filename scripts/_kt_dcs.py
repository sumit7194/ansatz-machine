#!/usr/bin/env python3
"""The dynamical Chern-Simons tensor machinery: Levi-Civita, dual Riemann, Pontryagin, C-tensor.

WHY IT HAS TO BE BUILT. dCS is the one quadratic-gravity sibling of sGB whose field equation is not
expressible with the objects gr_engine already has. It needs the Levi-Civita TENSOR (symbol / sqrt(-g)),
the left dual of Riemann, the Pontryagin density *RR, and covariant derivatives of Ricci -- none of
which exist in this repo. Everything here is validated against known-nonzero cases before use, because
a silently wrong C-tensor yields a metric solving no field equation, on which "no Killing tensor
survives" is guaranteed and vacuous (CLAUDE.md §5, the §124 error).

CONVENTIONS, stated because they are where the sign errors live.
  eps_symbol[0,1,2,3] = +1 on the coordinate order given.
  eps^{abcd} = eps_symbol / sqrt(-g)   and   eps_{abcd} = -sqrt(-g) * eps_symbol   (Lorentzian).
  *R^{abcd} = (1/2) eps^{abef} R_{ef}^{cd}
  *RR = *R^{abcd} R_{abcd}   (the Pontryagin density; = R~R in Alexander-Yunes)

THE FIELD EQUATION, in the normalisation-agnostic form this repo uses for sGB too:
    dG_ab = c1 * C_ab + c2 * T_ab      with c1, c2 FITTED, not assumed
  C^{ab} = eps^{cde(a} grad_c theta grad_e R^{b)}_d  +  grad_c grad_d theta  *R^{d(ab)c}
  T_ab   = grad_a theta grad_b theta - (1/2) g_ab (grad theta)^2
Conventions differ between sources by factors of 2 and by the sign of eps, and guessing one and
declaring a mismatch would blame the derivation for a convention (the sGB lesson, _kt_sgb_verify).

Repro:  .venv/bin/python scripts/_kt_dcs.py          # the validation battery
"""
import os
import sys
from itertools import permutations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from gr_engine import Geometry  # noqa: E402


def _perm_sign(p):
    s, p = 1, list(p)
    for i in range(len(p)):
        while p[i] != i:
            j = p[i]
            p[i], p[j] = p[j], p[i]
            s = -s
    return s


EPS4 = {}
for _p in permutations(range(4)):
    EPS4[_p] = _perm_sign(_p)


def levi_civita_up(geom):
    """eps^{abcd} = eps_symbol[abcd] / sqrt(-g)."""
    detg = sp.simplify(geom.g.det())
    root = sp.sqrt(-detg)
    E = [[[[sp.S.Zero] * 4 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for p, s in EPS4.items():
        a, b, c, d = p
        E[a][b][c][d] = sp.Integer(s) / root
    return E


def riemann_dddd(geom):
    """R_{abcd} = g_ae R^e_{bcd}."""
    n, g, R = 4, geom.g, geom.riemann
    out = [[[[sp.S.Zero] * n for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(n):
                for d in range(c + 1, n):
                    e = sp.cancel(sp.together(sum(g[a, k] * R[k][b][c][d] for k in range(n))))
                    out[a][b][c][d] = e
                    out[a][b][d][c] = -e
    return out


def riemann_uudd(geom):
    """R^{ab}_{cd} = g^{be} R^a_{e c d}."""
    n, gi, R = 4, geom.ginv, geom.riemann
    out = [[[[sp.S.Zero] * n for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(n):
                for d in range(c + 1, n):
                    e = sp.cancel(sp.together(sum(gi[b, k] * R[a][k][c][d] for k in range(n))))
                    out[a][b][c][d] = e
                    out[a][b][d][c] = -e
    return out


def pontryagin(geom, simplify=True):
    """*RR = (1/2) eps^{abef} R_{ef}^{cd} R_{abcd}, contracted to a scalar.

    Written as (1/2) eps^{abef} R_{efcd} R_{ab}^{cd} so only two index placements are needed.
    simplify=False returns the raw sum: on a rotating metric the final simplify is the expensive
    step by orders of magnitude, and a numeric spot-check does not need it."""
    E = levi_civita_up(geom)
    Rdddd = riemann_dddd(geom)
    Ruudd = riemann_uudd(geom)
    tot = sp.S.Zero
    for (a, b, e, f), s in EPS4.items():
        pre = E[a][b][e][f]
        if pre == 0:
            continue
        # *RR = (1/2) eps^{abef} R_{ef}^{cd} R_{abcd}. The (cd) pair must be contracted UP against
        # DOWN: R_{ef}^{cd} = R^{cd}_{ef} (pair symmetry) = Ruudd[c][d][e][f], against R_{abcd}.
        # An earlier version multiplied Rdddd[e][f][c][d] by Ruudd[a][b][c][d], which leaves (cd)
        # DOWN in both factors -- a sum over coordinate components, not a contraction. It was caught
        # by the Kerr control (non-constant ratio), which is precisely what that control is for.
        inner = sum(Ruudd[c][d][e][f] * Rdddd[a][b][c][d] for c in range(4) for d in range(4))
        tot += pre * inner
    return sp.simplify(tot / 2) if simplify else tot / 2


if __name__ == "__main__":
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    M, a = sp.symbols("M a", positive=True)

    print("dCS machinery validation\n")

    # CONTROL 1 (must be ZERO): Schwarzschild is parity-even, so *RR vanishes identically.
    f = 1 - 2 * M / r
    gS = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th) ** 2)
    pS = pontryagin(Geometry(gS, [t, r, th, ph]))
    print(f"  Schwarzschild  *RR = {pS}      (must be 0)", flush=True)

    # CONTROL 2 (must be NONZERO, and must match a closed form): Kerr.
    # A control that can only return zero is not a control -- CLAUDE.md §5.
    Sig = r**2 + a**2 * sp.cos(th) ** 2
    Del = r**2 - 2 * M * r + a**2
    gK = sp.zeros(4, 4)
    gK[0, 0] = -(1 - 2 * M * r / Sig)
    gK[0, 3] = gK[3, 0] = -2 * M * a * r * sp.sin(th) ** 2 / Sig
    gK[1, 1] = Sig / Del
    gK[2, 2] = Sig
    gK[3, 3] = (r**2 + a**2 + 2 * M * a**2 * r * sp.sin(th) ** 2 / Sig) * sp.sin(th) ** 2
    print("  Kerr: building curvature (slow) ...", flush=True)
    pK = sp.simplify(pontryagin(Geometry(gK, [t, r, th, ph])))
    c = sp.cos(th)
    known = (96 * M**2 * a * r * c * (3 * r**2 - a**2 * c**2) * (r**2 - 3 * a**2 * c**2)) / Sig**6
    diff = sp.simplify(sp.together(pK - known))
    print(f"  Kerr           *RR nonzero: {sp.simplify(pK) != 0}", flush=True)
    print(f"  Kerr           *RR  -  96 M^2 a r cos(th)(3r^2-a^2c^2)(r^2-3a^2c^2)/Sigma^6  =  {diff}", flush=True)
    ratio = sp.simplify(pK / known) if known != 0 else None
    print(f"  Kerr           ratio to that closed form = {ratio}", flush=True)
    print(f"  Kerr a->0      *RR = {sp.simplify(pK.subs(a, 0))}      (must be 0)", flush=True)


def dual_riemann_uuuu(geom, E=None):
    """*R^{abcd} = (1/2) eps^{abef} R_{ef}^{cd}, dual taken on the FIRST pair.

    Index care, after the contraction bug this file already paid for: R_{ef}^{cd} = R^{cd}_{ef} by
    the pair symmetry, so the factor wanted is Ruudd[c][d][e][f], raised on (ab) by eps^{abef}."""
    E = levi_civita_up(geom) if E is None else E
    Ruudd = riemann_uudd(geom)
    gi = geom.ginv
    # R^{cd}_{ef} -> R^{cdef}
    Ruuuu = [[[[sp.S.Zero] * 4 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for c in range(4):
        for d in range(4):
            for e in range(4):
                for f in range(4):
                    Ruuuu[c][d][e][f] = sp.cancel(sp.together(
                        sum(gi[e, k] * sum(gi[f, l] * Ruudd[c][d][k][l] for l in range(4))
                            for k in range(4))))
    out = [[[[sp.S.Zero] * 4 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    tot = sp.S.Zero
                    for (A, B, e, f), s in EPS4.items():
                        if A != a or B != b:
                            continue
                        tot += E[a][b][e][f] * Ruuuu[c][d][e][f]
                    out[a][b][c][d] = sp.cancel(sp.together(tot / 2))
    return out


def ricci_ud(geom):
    """R^a_b = g^{ac} R_cb."""
    gi, Ric = geom.ginv, geom.ricci
    return [[sp.cancel(sp.together(sum(gi[A, c] * Ric[c, B] for c in range(4))))
             for B in range(4)] for A in range(4)]


def cov_deriv_ricci_ud(geom):
    """grad_e R^b_d = d_e R^b_d + Gam^b_{ek} R^k_d - Gam^k_{ed} R^b_k.  Returned as [e][b][d]."""
    x, Gam, R = geom.coords, geom.christoffel, ricci_ud(geom)
    out = [[[sp.S.Zero] * 4 for _ in range(4)] for _ in range(4)]
    for e in range(4):
        for b in range(4):
            for d in range(4):
                out[e][b][d] = sp.cancel(sp.together(
                    sp.diff(R[b][d], x[e])
                    + sum(Gam[b][e][k] * R[k][d] for k in range(4))
                    - sum(Gam[k][e][d] * R[b][k] for k in range(4))))
    return out


def hessian_scalar(geom, s):
    """grad_c grad_d s = d_c d_d s - Gam^k_{cd} d_k s."""
    x, Gam = geom.coords, geom.christoffel
    return [[sp.cancel(sp.together(
        sp.diff(s, x[c], x[d]) - sum(Gam[k][c][d] * sp.diff(s, x[k]) for k in range(4))))
        for d in range(4)] for c in range(4)]


def c_tensor(geom, theta):
    """C^{mu nu} = grad_s theta eps^{s mu al be} grad_al R^nu_be + grad_s grad_ta theta *R^{ta mu s nu},
    symmetrised on (mu nu).  Alexander & Yunes, Phys. Rept. 480 (2009), Eqs. (6) and (16); the dual
    is on the LAST pair, *R^{ta mu s nu} = (1/2) eps^{s nu al be} R^{ta mu}_{al be}.

    HISTORY, because it cost two controls. The first coding of this put the Levi-Civita free index in
    the last slot and took the dual on the FIRST pair, and it FAILED tracelessness (g_ab C^ab ~ 1e-5
    instead of 0) -- while passing the weak "C = 0 for constant theta" check, exactly as *RR's wrong
    contraction passed "Schwarzschild = 0". A scan then showed all four slot/dual combinations of the
    correct form are the SAME tensor (_kt_dcs_variants, _kt_dcs_compare: maxdiff exactly 0), so the
    convention is cosmetic and the original was simply wrong.

    Controls: tracelessness (necessary, and it rejected the bug) and the divergence identity
    grad_a C^{ab} = const * (grad^b theta) *RR, which also fixes the normalisation.
    """
    x = geom.coords
    E = levi_civita_up(geom)
    dR = cov_deriv_ricci_ud(geom)                  # dR[al][nu][be] = grad_al R^nu_be
    H = hessian_scalar(geom, theta)                # H[s][ta]        = grad_s grad_ta theta
    Dr = dual_riemann_right(geom, E)               # Dr[ta][mu][s][nu]
    dth = [sp.diff(theta, xi) for xi in x]
    C = sp.zeros(4, 4)
    for mu in range(4):
        for nu in range(mu, 4):
            tot = sp.S.Zero
            for m_, n_ in ((mu, nu), (nu, mu)):    # the (mu nu) symmetrisation
                for s in range(4):
                    if dth[s] == 0:
                        continue
                    for al in range(4):
                        for be in range(4):
                            e = E[s][m_][al][be]
                            if e != 0:
                                tot += dth[s] * e * dR[al][n_][be]
                for s in range(4):
                    for ta in range(4):
                        if H[s][ta] != 0:
                            tot += H[s][ta] * Dr[ta][m_][s][n_]
            v = sp.cancel(sp.together(tot / 2))
            C[mu, nu] = C[nu, mu] = v
    return C


def dual_riemann_right(geom, E=None):
    """*R^{ab cd} = (1/2) eps^{cdef} R^{ab}_{ef} -- dual on the LAST pair (Alexander-Yunes Eq. 6)."""
    E = levi_civita_up(geom) if E is None else E
    Ruudd = riemann_uudd(geom)
    out = [[[[sp.S.Zero] * 4 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    out[a][b][c][d] = sp.cancel(sp.together(
                        sum(E[c][d][e][f] * Ruudd[a][b][e][f]
                            for e in range(4) for f in range(4)) / 2))
    return out


def stress_theta(geom, theta):
    """T_ab = grad_a theta grad_b theta - (1/2) g_ab (grad theta)^2."""
    x, g, gi = geom.coords, geom.g, geom.ginv
    d = [sp.diff(theta, xi) for xi in x]
    sq = sum(gi[A, B] * d[A] * d[B] for A in range(4) for B in range(4))
    return sp.Matrix(4, 4, lambda A, B: sp.cancel(sp.together(d[A] * d[B] - g[A, B] * sq / 2)))
