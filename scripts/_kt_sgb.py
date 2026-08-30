#!/usr/bin/env python3
"""The slowly-rotating Einstein-dilaton-Gauss-Bonnet black hole, transcribed AND VERIFIED.

WHY THIS FILE IS MOSTLY ABOUT VERIFICATION. The metric is transcribed from a paper, and a
transcription error -- one coefficient mis-read out of a PDF whose fraction bars do not survive
text extraction -- is SILENT. It would produce a metric that is not a solution of any field
equation, on which "no Killing tensor survives" is guaranteed and meaningless. That is the same
failure mode as §124's substrate-independent reducible table: a correct computation answering the
wrong question. So nothing here is used until it has been checked against something independent.

SOURCE. Ayzenberg & Yunes, "Slowly rotating black holes in Einstein-Dilaton-Gauss-Bonnet gravity:
Quadratic order in spin solutions", PRD 90, 044066 (2014), arXiv:1405.2133 (+ erratum PRD 91,
069905). Conventions there: field equations G_ab + (alpha/2kappa) D_ab = (1/kappa) T_ab with
exp(theta) Taylor-expanded to 1 + theta, V(theta) = 0, and

    zeta = alpha^2 / (beta kappa m^4),   f = 1 - 2m/r,   chi = a/m.

ORDER LABELS. g^(n,k) is order n in the coupling alpha' and k in the spin chi; zeta ~ alpha'^2, so
the O(alpha'^2) pieces are the O(zeta) corrections. The full metric is
g = g_Kerr + g^(0,2) + g^(1,2) + g^(2,2) + ..., reducing EXACTLY to Kerr as zeta -> 0.

WHY STATIC (chi^0) FIRST, EVEN THOUGH IT IS NOT THE OPEN QUESTION. Two reasons, both about being
able to tell whether we are right:
  1. It is the only order whose field equations this repo ALREADY has, validated against Kanti et
     al. in scripts/10_edgb_reduce.py. So the transcription can be CHECKED rather than trusted.
  2. Its answer is known independently: the static solution is spherically symmetric, so total
     angular momentum is still conserved and EVERY background Killing tensor must survive. A
     pipeline that reports anything else at chi^0 is broken, which makes this a positive control
     on real sGB data rather than on a synthetic perturbation.
The open question (ranks 3-6 at O(chi^2)) is only worth computing once both of those pass.

INDEPENDENT CORROBORATION OF ONE COMPONENT. g_rr^(0,2) below was additionally recovered verbatim
from a separate secondary source, so at least that line is not a single-source reading.
"""
import sympy as sp

# Coordinates match the rest of the pipeline: x = r, y = cos(theta), t and phi cyclic.
t, x, y, ph = sp.symbols("t x y phi", real=True)
zeta, chi = sp.symbols("zeta chi", real=True)


def dilaton_static(m=sp.Integer(1), alpha=sp.Integer(1), beta=sp.Integer(1)):
    """theta^(0,1), Eq. (12): (alpha/(beta m r)) (1 + m/r + 4/3 m^2/r^2)."""
    return (alpha / (beta * m * x)) * (1 + m / x + sp.Rational(4, 3) * m**2 / x**2)


def g_tt_02(m=sp.Integer(1)):
    """Eq. (13): the O(zeta chi^0) correction to g_tt."""
    return -(zeta * m**3) / (3 * x**3) * (
        1 + 26 * m / x + sp.Rational(66, 5) * m**2 / x**2
        + sp.Rational(96, 5) * m**3 / x**3 - 80 * m**4 / x**4)


def g_rr_02(m=sp.Integer(1)):
    """Eq. (14): the O(zeta chi^0) correction to g_rr. f = 1 - 2m/r."""
    f = 1 - 2 * m / x
    return -(zeta * m**2) / (f**2 * x**2) * (
        1 + m / x + sp.Rational(52, 3) * m**2 / x**2 + 2 * m**3 / x**3
        + sp.Rational(16, 5) * m**4 / x**4 - sp.Rational(368, 3) * m**5 / x**5)


def static_metric(m=sp.Integer(1), truncate=True):
    """Schwarzschild + the O(zeta) sGB correction, in (t, x=r, y=cos theta, phi).

    g_yy and g_phiphi carry no O(zeta) correction at this order: Ayzenberg & Yunes state the only
    nonvanishing terms in g^(0,2) are g_tt and g_rr."""
    f = 1 - 2 * m / x
    g = sp.zeros(4, 4)
    g[0, 0] = -f + g_tt_02(m)
    g[1, 1] = 1 / f + g_rr_02(m)
    # theta -> y = cos(theta):  dtheta^2 = dy^2/(1-y^2),  sin^2(theta) = 1-y^2
    g[2, 2] = x**2 / (1 - y**2)
    g[3, 3] = x**2 * (1 - y**2)
    return g


def static_split(m=sp.Integer(1)):
    """(background, first-order correction) as separate matrices: g = g0 + zeta*h, h = dg/dzeta.

    Returned split rather than summed because the whole point of the perturbative treatment is
    that the two orders are never mixed: g0 sets the background Killing space, h sources the
    O(zeta) equation."""
    g = static_metric(m)
    h = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(sp.diff(g[i, j], zeta))))
    g0 = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(g[i, j].subs(zeta, 0))))
    return g0, h


def inverse_split(m=sp.Integer(1)):
    """(g^ab at zeta=0, d(g^ab)/d(zeta)) -- what the Killing pipeline actually consumes.

    NOT the inverse of the truncated metric: for g = g0 + zeta*h the inverse expands as
    g^{-1} = g0^{-1} - zeta * g0^{-1} h g0^{-1} + O(zeta^2), and using the exact inverse of the
    truncated metric would silently mix in O(zeta^2) terms that the solution does not control."""
    g0, h = static_split(m)
    gi0 = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(g0.inv()[i, j])))
    gi1 = -gi0 * h * gi0
    return gi0, sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(gi1[i, j])))


if __name__ == "__main__":
    import sys
    m = sp.Integer(1)
    print("sGB static (chi^0) metric, transcribed from arXiv:1405.2133 Eqs (12)-(14)\n")
    g = static_metric(m)
    for i in range(4):
        print(f"  g_{i}{i} = {sp.simplify(g[i, i])}")
    print(f"\n  dilaton theta^(0,1) = {sp.simplify(dilaton_static(m))}")

    # --- structural checks that need no field equations -------------------------------
    g0, h = static_split(m)
    ok = True
    f = 1 - 2 * m / x
    schw = sp.diag(-f, 1 / f, x**2 / (1 - y**2), x**2 * (1 - y**2))
    same = all(sp.simplify(g0[i, j] - schw[i, j]) == 0 for i in range(4) for j in range(4))
    print(f"\n  zeta -> 0 gives EXACTLY Schwarzschild: {same}")
    ok &= same
    # The correction must fall off faster than the Schwarzschild terms, or it is not a
    # small-coupling correction to an asymptotically flat solution.
    lim_tt = sp.limit(h[0, 0], x, sp.oo)
    lim_rr = sp.limit(h[1, 1], x, sp.oo)
    print(f"  correction vanishes at infinity: g_tt {lim_tt == 0}, g_rr {lim_rr == 0}")
    ok &= (lim_tt == 0 and lim_rr == 0)
    # Only g_tt and g_rr are corrected at this order (Ayzenberg & Yunes, below Eq. (12)).
    only = all(sp.simplify(h[i, j]) == 0 for i in range(4) for j in range(4)
               if (i, j) not in ((0, 0), (1, 1)))
    print(f"  only g_tt and g_rr corrected at O(zeta chi^0): {only}")
    ok &= only
    if not ok:
        sys.exit("\n  STRUCTURAL CHECKS FAILED -- the transcription is wrong before any field "
                 "equation is consulted.")
    print("\n  structural checks passed. These do NOT validate the coefficients; that needs the "
          "field equations (see _kt_sgb_verify.py).")
