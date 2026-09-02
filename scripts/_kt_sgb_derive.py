#!/usr/bin/env python3
"""DERIVE the sGB metric corrections by solving the field equations, instead of transcribing them.

WHY DERIVE RATHER THAN READ. The O(chi) and O(chi^2) corrections in arXiv:1405.2133 are long
rational series, and the PDF text extraction interleaves numerators with denominators: at O(chi)
the fragments 140m, 10m^2, 16m^3, 400m^4 have to be paired with 9r, r^2, r^3, 9r^4 by guesswork.
Guessing is the silent-error category -- a mis-paired coefficient yields a metric solving no field
equation, on which "no Killing tensor survives" is guaranteed and vacuous.

The field-equation setup in _kt_sgb_verify.py is now VALIDATED: it reproduced the static Eqs
(12)-(14) exactly, with a single normalisation c1 = -2m^4, c2 = +2m^4 fitted on one component and
confirmed on three others. Run backwards, the same setup DETERMINES the metric: write the unknown
correction as a series with undetermined coefficients, impose the equation, and solve. Then the
paper's published values become an INDEPENDENT CHECK on our derivation rather than an input we must
trust -- the stronger arrangement, and the one that scales to O(chi^2) where the text is worst.

THE ORDER BOOKKEEPING. Two bookkeeping parameters, zeta (coupling) and chi (spin):

    g = g_Schw + chi*g_LT + zeta*dg_static + zeta*chi*W(r)sin^2(theta) [dt dphi] + ...

The O(zeta chi) piece of G_ab is extracted as the mixed partial d^2/dzeta dchi at the origin, which
picks up the nonlinear cross terms between the O(zeta) static correction and the O(chi)
frame-dragging term automatically -- they are physically present and dropping them would be an
error no residual check downstream could see.

The dilaton has NO O(chi) piece (it is even in spin by parity), so the source at this order is the
chi-derivative of c1*D_ab + c2*T_ab evaluated on Schwarzschild + chi*(Lense-Thirring).

Repro:  .venv/bin/python scripts/_kt_sgb_derive.py [--order 1] [--nterms 8]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
from gr_engine import Geometry

r, th = sp.symbols("r theta", positive=True)
t, ph = sp.symbols("t phi", real=True)
zeta, chi = sp.symbols("zeta chi")
m = sp.Symbol("m", positive=True)
COORDS = [t, r, th, ph]
f = 1 - 2 * m / r

# The verified static pieces (see _kt_sgb_verify.py; do not edit without re-running it).
DG_TT = -(m**3) / (3 * r**3) * (
    1 + 26 * m / r + sp.Rational(66, 5) * m**2 / r**2
    + sp.Rational(96, 5) * m**3 / r**3 - 80 * m**4 / r**4)
DG_RR = -(m**2) / (f**2 * r**2) * (
    1 + m / r + sp.Rational(52, 3) * m**2 / r**2 + 2 * m**3 / r**3
    + sp.Rational(16, 5) * m**4 / r**4 - sp.Rational(368, 3) * m**5 / r**5)
THETA = (1 / (m * r)) * (1 + m / r + sp.Rational(4, 3) * m**2 / r**2)
C1, C2 = -2 * m**4, 2 * m**4          # the normalisation fixed by the static verification


def einstein_of(gm):
    geo = Geometry(gm, COORDS)
    Ric, Rs = geo.ricci, geo.ricci_scalar
    G = sp.Matrix(4, 4, lambda i, j: Ric[i, j] - sp.Rational(1, 2) * gm[i, j] * Rs)
    return G, geo


def source_DT(gm_bg):
    """c1*D_ab + c2*T_ab on a given background, with D_ab = 4 R_acbd grad^c grad^d theta.

    The Ricci terms of their Eq. (5) are dropped, which is valid only where R and R_ab vanish to
    the order being used. The check below enforces that rather than assuming it -- on a background
    with curvature at the working order this source would be silently wrong."""
    geo = Geometry(gm_bg, COORDS)
    # RICCI-FLAT TO THE WORKING ORDER, not exactly. Schwarzschild + chi*(Lense-Thirring) is Kerr
    # truncated at linear order in spin, so its Ricci vanishes at O(chi^0) and O(chi^1) and is
    # nonzero at O(chi^2) -- precisely because Kerr's own O(chi^2) metric terms were dropped.
    # Demanding EXACT Ricci-flatness here rejects a perfectly valid background.
    #
    # The relaxation is justified rather than convenient: every term of D_ab that we drop carries
    # a factor of R or R_ab, so if R_ab = O(chi^2) those terms enter D_ab at O(chi^2), and this
    # routine is only ever used to O(chi^1). What is checked is therefore what is actually needed.
    # Extract the chi^0 and chi^1 parts by DERIVATIVES, not by degree-filtering the terms:
    # gr_engine inverts the background exactly, so the t-phi block determinant puts chi^2 into
    # denominators and sp.degree() then raises on those terms. subs/diff is well defined either way.
    bad = []
    for i in range(4):
        for j in range(i, 4):
            e = sp.together(geo.ricci[i, j])
            c0 = sp.simplify(e.subs(chi, 0))
            c1 = sp.simplify(sp.diff(e, chi).subs(chi, 0))
            if c0 != 0 or c1 != 0:
                bad.append((i, j))
    if bad:
        raise ValueError(f"background Ricci is nonzero at O(chi^0..1) at {bad}; D_ab would keep "
                         f"terms this routine drops")
    Gam = geo.christoffel
    gi = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(gm_bg.inv()[i, j])))
    dth = [sp.diff(THETA, c) for c in COORDS]
    hess = sp.Matrix(4, 4, lambda a, b: sp.diff(THETA, COORDS[a], COORDS[b])
                     - sum(Gam[c][a][b] * dth[c] for c in range(4)))
    hup = sp.Matrix(4, 4, lambda c, d: sum(gi[c, e] * gi[d, ff] * hess[e, ff]
                                           for e in range(4) for ff in range(4)))
    Riem = geo.riemann
    Rl = [[[[sum(gm_bg[a, e] * Riem[e][b][c][d] for e in range(4))
             for d in range(4)] for c in range(4)] for b in range(4)] for a in range(4)]
    D = sp.Matrix(4, 4, lambda a, b: 4 * sum(Rl[a][c][b][d] * hup[c, d]
                                             for c in range(4) for d in range(4)))
    sq = sum(gi[a, b] * dth[a] * dth[b] for a in range(4) for b in range(4))
    T = sp.Matrix(4, 4, lambda a, b: dth[a] * dth[b] - sp.Rational(1, 2) * gm_bg[a, b] * sq)
    return sp.Matrix(4, 4, lambda a, b: C1 * D[a, b] + C2 * T[a, b])


def trunc(e):
    """Drop every term beyond O(zeta^1 chi^1).

    Truncating at EVERY step is the whole trick. Building the exact Einstein tensor and
    differentiating afterwards makes sympy carry orders that are immediately discarded, and
    gr_engine's eager per-Christoffel simplify then dominates: that route was still inside the
    curvature computation after 13.5 minutes, where this one reaches the answer in 20 seconds."""
    e = sp.expand(e)
    out = sp.Integer(0)
    for tm in sp.Add.make_args(e):
        if sp.degree(tm, zeta) <= 1 and sp.degree(tm, chi) <= 1:
            out += tm
    return out


def perturbative_inverse(g, g0, gi0):
    """g^{-1} = gi0 - gi0 dg gi0 + ... truncated, NOT the exact inverse of the truncated metric.

    Inverting the full matrix is what puts zeta and chi into denominators and blows the
    expressions up; it would also silently mix in O(zeta^2) terms the solution does not control.
    The Neumann series is truncated to the order we keep, and then CHECKED against g to that
    order rather than trusted."""
    dg = sp.Matrix(4, 4, lambda i, j: sp.expand(g[i, j] - g0[i, j]))
    A = gi0 * dg
    gi = gi0 - A * gi0 + A * A * gi0 - A * A * A * gi0
    gi = sp.Matrix(4, 4, lambda i, j: trunc(sp.expand(gi[i, j])))
    chk = sp.Matrix(4, 4, lambda i, j: trunc(sp.expand(
        sum(gi[i, k] * g[k, j] for k in range(4)))))
    for i in range(4):
        for j in range(4):
            if sp.simplify(chk[i, j] - (1 if i == j else 0)) != 0:
                raise ValueError(f"perturbative inverse wrong at ({i},{j}) -- series truncated "
                                 f"too early for this metric")
    return gi


def einstein_tphi_zetachi(W, verbose=True):
    """The O(zeta chi) part of G_tphi for the sGB ansatz, with W(r) the unknown correction."""
    s2 = sp.sin(th)**2
    g = sp.zeros(4, 4)
    g[0, 0] = -f + zeta * DG_TT
    g[1, 1] = 1 / f + zeta * DG_RR
    g[2, 2] = r**2
    g[3, 3] = r**2 * s2
    g[0, 3] = g[3, 0] = chi * (-2 * m**2 * s2 / r) + zeta * chi * W * s2
    g0 = sp.diag(-f, 1 / f, r**2, r**2 * s2)
    gi0 = sp.diag(-1 / f, f, 1 / r**2, 1 / (r**2 * s2))
    gi = perturbative_inverse(g, g0, gi0)
    if verbose:
        print("  perturbative inverse verified to O(zeta chi)", flush=True)
    Gam = [[[trunc(sp.expand(sum(gi[a, d] * (sp.diff(g[d, c], COORDS[b])
                                             + sp.diff(g[d, b], COORDS[c])
                                             - sp.diff(g[b, c], COORDS[d]))
                                 for d in range(4)) / 2))
             for c in range(4)] for b in range(4)] for a in range(4)]

    def ric(b, d):
        e = sum(sp.diff(Gam[a][b][d], COORDS[a]) - sp.diff(Gam[a][b][a], COORDS[d])
                for a in range(4))
        e += sum(Gam[a][a][c] * Gam[c][b][d] - Gam[a][d][c] * Gam[c][b][a]
                 for a in range(4) for c in range(4))
        return trunc(sp.expand(e))

    Rs = trunc(sp.expand(sum(gi[a, b] * ric(a, b) for a in range(4) for b in range(4))))
    G03 = trunc(sp.expand(ric(0, 3) - sp.Rational(1, 2) * g[0, 3] * Rs))
    return sp.simplify(sp.diff(G03, zeta, chi).subs({zeta: 0, chi: 0}))


def derive_order_chi1(nterms=8, verbose=True):
    """Solve for W(r) in  g_tphi^(1,2) = zeta*chi*W(r)*sin^2(theta)."""
    Wf = sp.Function("W")(r)
    if verbose:
        print("  building the O(zeta chi) Einstein tensor (truncating at every step)...",
              flush=True)
    lhs = einstein_tphi_zetachi(Wf, verbose)
    if verbose:
        print("  extracted the O(zeta chi) part of G_tphi", flush=True)

    gbg = sp.zeros(4, 4)
    gbg[0, 0] = -f
    gbg[1, 1] = 1 / f
    gbg[2, 2] = r**2
    gbg[3, 3] = r**2 * sp.sin(th)**2
    gbg[0, 3] = gbg[3, 0] = chi * (-2 * m**2 * sp.sin(th)**2 / r)
    S = source_DT(gbg)
    rhs = sp.simplify(sp.diff(S[0, 3], chi).subs(chi, 0))
    if verbose:
        print("  extracted the O(chi) source\n", flush=True)

    ode = sp.simplify(lhs - rhs)
    if verbose:
        print("  ODE in W(r) obtained\n", flush=True)
    w = sp.symbols(f"w0:{nterms}")
    ser = sum(w[k] * m**(4 + k) / r**(3 + k) for k in range(nterms))
    sub = sp.expand(sp.together(ode.subs(Wf, ser).doit()))
    num = sp.numer(sp.together(sub))
    pol = sp.Poly(sp.expand(num), r)
    eqs = [sp.simplify(c) for c in pol.all_coeffs()]
    sol = sp.solve(eqs, list(w), dict=True)
    return ser, w, sol, len(eqs)


if __name__ == "__main__":
    nterms = int(sys.argv[sys.argv.index("--nterms") + 1]) if "--nterms" in sys.argv else 8
    print(f"Deriving the O(zeta chi) sGB correction from the field equations "
          f"({nterms}-term ansatz)\n", flush=True)
    W, w, sol, neq = derive_order_chi1(nterms)
    print(f"  {neq} equations for {nterms} unknowns", flush=True)
    if not sol:
        sys.exit("\n  NO SOLUTION for this ansatz -- either the assumed fall-off is wrong or the "
                 "series needs more terms. That is information, not a failure to hide.")
    s = sol[0]
    Wsol = sp.simplify(W.subs(s))
    print(f"  solution: {s}\n", flush=True)
    print(f"  W(r) = {sp.factor(sp.simplify(Wsol))}\n", flush=True)

    # Compare against the paper's Eq. (15) under BOTH readings of the ambiguous pairing, so the
    # comparison is decided by the field equations rather than by how the PDF happened to extract.
    readingA = sp.Rational(3, 5) * m**4 / r**3 * (
        1 + sp.Rational(140, 9) * m / r + 10 * m**2 / r**2 + 16 * m**3 / r**3
        - sp.Rational(400, 9) * m**4 / r**4)
    readingB = sp.Rational(3, 5) * m**4 / r**3 * (
        1 + sp.Rational(140, 9) * m / r + 10 * m**2 / r**2 + 16 * m**3 / r**3
        + sp.Rational(400, 9) * m**4 / r**4)
    for nm, cand in (("Eq.(15) reading A (last term -)", readingA),
                     ("Eq.(15) reading B (last term +)", readingB)):
        d = sp.simplify(Wsol - cand)
        print(f"  {nm}: {'MATCHES our derivation' if d == 0 else 'differs'}", flush=True)
