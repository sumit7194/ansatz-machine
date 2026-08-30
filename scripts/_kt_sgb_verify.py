#!/usr/bin/env python3
"""VERIFY the transcribed static sGB metric against the EdGB field equations.

WHAT THIS IS FOR. `_kt_sgb.py` transcribes Eqs (12)-(14) of arXiv:1405.2133 out of a PDF whose
fraction bars do not survive text extraction. A single mis-read coefficient is SILENT: it produces
a metric that solves no field equation, on which "no Killing tensor survives" is guaranteed and
meaningless. Structural checks (zeta -> 0 gives Schwarzschild, corrections vanish at infinity)
cannot see such an error. The field equations can.

THE EQUATION, AT THE ORDER THAT MATTERS. The background is Schwarzschild, which is Ricci FLAT, so
R = 0 and R_ab = 0 there. That kills every term of D_ab (their Eq. (5)) except the last:

    D_ab = 4 R_acbd  grad^c grad^d theta                (on a Ricci-flat background)

The dilaton is O(alpha), so T_ab^(theta) ~ alpha^2 and (alpha/2kappa) D_ab ~ alpha^2 -- both the
same order as the metric correction, which is O(alpha^2) = O(zeta). Since G_ab[Schwarzschild] = 0,
the O(zeta) field equation is

    dG_ab  =  c1 * D_ab  +  c2 * T_ab

with dG_ab the zeta-derivative of the Einstein tensor of the corrected metric, and c1, c2 constants
fixed by the action's normalisation.

WHY WE SOLVE FOR c1, c2 INSTEAD OF ASSUMING THEM. Conventions differ between sources (Kanti's
exp(phi) coupling with a -1/4 kinetic term, versus this paper's (1 + theta) with beta), and the
scalar-equation check already showed a clean factor of 2 between the paper's Eq. (6) as read and
the equation its own solution satisfies. Guessing a normalisation and declaring a mismatch would
blame the transcription for a convention. So: fit c1 and c2 from ONE tensor component, then demand
the SAME constants reproduce the others. A transcription error cannot be absorbed by two constants
-- it changes the r-dependence, and the residual on the remaining components will not vanish.
That is the whole test: two unknowns, several independent equations.

Repro:  .venv/bin/python scripts/_kt_sgb_verify.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
from gr_engine import Geometry

r, th = sp.symbols("r theta", positive=True)
t, ph = sp.symbols("t phi", real=True)
zeta = sp.Symbol("zeta")
m = sp.Symbol("m", positive=True)
COORDS = [t, r, th, ph]

f = 1 - 2 * m / r

# --- the transcription under test, in (t, r, theta, phi) -------------------------------
# Eq. (13): the O(zeta chi^0) correction to g_tt
dg_tt = -(m**3) / (3 * r**3) * (
    1 + 26 * m / r + sp.Rational(66, 5) * m**2 / r**2
    + sp.Rational(96, 5) * m**3 / r**3 - 80 * m**4 / r**4)
# Eq. (14): the O(zeta chi^0) correction to g_rr
dg_rr = -(m**2) / (f**2 * r**2) * (
    1 + m / r + sp.Rational(52, 3) * m**2 / r**2 + 2 * m**3 / r**3
    + sp.Rational(16, 5) * m**4 / r**4 - sp.Rational(368, 3) * m**5 / r**5)
# Eq. (12): the O(alpha) dilaton (alpha/beta scaled out; it only sets the overall constants)
theta_d = (1 / (m * r)) * (1 + m / r + sp.Rational(4, 3) * m**2 / r**2)


def einstein(gm):
    geo = Geometry(gm, COORDS)
    Ric, Rs = geo.ricci, geo.ricci_scalar
    return sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(
        Ric[i, j] - sp.Rational(1, 2) * gm[i, j] * Rs))), geo


if __name__ == "__main__":
    g0 = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2)
    gz = sp.diag(-f + zeta * dg_tt, 1 / f + zeta * dg_rr, r**2, r**2 * sp.sin(th)**2)

    print("Verifying the static sGB transcription against the EdGB field equations.\n", flush=True)

    # Sanity: the background really is Ricci-flat, which is what collapses D_ab to one term.
    G0, geo0 = einstein(g0)
    flat = all(sp.simplify(geo0.ricci[i, j]) == 0 for i in range(4) for j in range(4))
    print(f"  background Ricci-flat (so D_ab keeps only the Riemann term): {flat}", flush=True)
    if not flat:
        sys.exit("  background is not Schwarzschild -- abort")

    # dG_ab : the O(zeta) piece of the Einstein tensor of the corrected metric.
    Gz, _ = einstein(gz)
    dG = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(
        sp.diff(Gz[i, j], zeta).subs(zeta, 0))))
    print("  computed dG_ab (zeta-derivative of the Einstein tensor)", flush=True)

    # grad_a grad_b theta on the background
    Gam = geo0.christoffel
    gi0 = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(g0.inv()[i, j])))
    dth = [sp.diff(theta_d, c) for c in COORDS]
    hess = sp.Matrix(4, 4, lambda a, b: sp.cancel(sp.together(
        sp.diff(theta_d, COORDS[a], COORDS[b])
        - sum(Gam[c][a][b] * dth[c] for c in range(4)))))
    hup = sp.Matrix(4, 4, lambda c, d: sp.cancel(sp.together(
        sum(gi0[c, e] * gi0[d, ff] * hess[e, ff] for e in range(4) for ff in range(4)))))

    # D_ab = 4 R_acbd grad^c grad^d theta, with R_abcd = g_ae R^e_bcd
    Riem = geo0.riemann
    Rl = [[[[sp.cancel(sp.together(sum(g0[a, e] * Riem[e][b][c][d] for e in range(4))))
             for d in range(4)] for c in range(4)] for b in range(4)] for a in range(4)]
    D = sp.Matrix(4, 4, lambda a, b: sp.cancel(sp.together(
        4 * sum(Rl[a][c][b][d] * hup[c, d] for c in range(4) for d in range(4)))))
    print("  computed D_ab = 4 R_acbd grad^c grad^d theta", flush=True)

    # T_ab = grad_a theta grad_b theta - 1/2 g_ab (grad theta)^2   (beta scaled into c2)
    sq = sp.cancel(sp.together(sum(gi0[a, b] * dth[a] * dth[b]
                                   for a in range(4) for b in range(4))))
    T = sp.Matrix(4, 4, lambda a, b: sp.cancel(sp.together(
        dth[a] * dth[b] - sp.Rational(1, 2) * g0[a, b] * sq)))
    print("  computed T_ab\n", flush=True)

    # Fit c1, c2 on the tt component, then REQUIRE the same constants elsewhere.
    # Fit the two constants NUMERICALLY at two radii (well outside the horizon at r = 2m),
    # then verify SYMBOLICALLY everywhere. Extracting polynomial coefficients in r is fragile on
    # rational functions; two points determine two unknowns, and the symbolic check that follows
    # is what actually decides.
    # The constants carry MASS DIMENSION and must be solved for as functions of m, not fixed to
    # pure numbers. zeta = alpha^2/(beta kappa m^4), and zeta was scaled out of the metric
    # correction while alpha/beta was scaled out of the dilaton, so the two sides differ by a power
    # of m. Fixing m = 1 in the fit and then testing at symbolic m made every residual come out
    # proportional to (m^4 - 1) -- i.e. vanishing exactly where the fit was made. That is a
    # dimensional artifact of the ansatz, NOT a wrong coefficient, and reporting it as "the
    # transcription is wrong" would have condemned a correct metric.
    c1, c2 = sp.symbols("c1 c2")
    subs_pt = [{r: sp.Integer(3), th: sp.pi / 3},
               {r: sp.Integer(5), th: sp.pi / 4}]
    eqs = [sp.Eq((dG[0, 0] - c1 * D[0, 0] - c2 * T[0, 0]).subs(pt), 0) for pt in subs_pt]
    sol = sp.solve(eqs, [c1, c2], dict=True)
    print(f"  constants fitted at two radii on the tt component (m symbolic): "
          f"{ {k: sp.simplify(v) for k, v in sol[0].items()} if sol else sol}", flush=True)
    if not sol:
        sys.exit("\n  NO CONSTANTS FIT -- the transcription satisfies the field equations in no "
                 "normalisation, so a coefficient is wrong.")
    s = sol[0]
    ok = True
    for (a, b), nm in (((0, 0), "tt"), ((1, 1), "rr"), ((2, 2), "thth"), ((3, 3), "phiphi")):
        res = sp.simplify((dG[a, b] - c1 * D[a, b] - c2 * T[a, b]).subs(s))
        good = (res == 0)
        ok &= good
        print(f"    {nm:7s} residual {'0 -- satisfied' if good else 'NONZERO: ' + str(res)}",
              flush=True)
    if ok:
        print(f"\n  VERIFIED: Eqs (12)-(14) satisfy the O(zeta) EdGB field equations with a single "
              f"normalisation {s}. Two constants cannot absorb a wrong r-dependence, so the "
              f"coefficients are right.", flush=True)
    else:
        sys.exit("\n  FAILED: the constants that fit tt do not satisfy the other components. "
                 "The transcription is wrong -- do NOT use this metric.")
