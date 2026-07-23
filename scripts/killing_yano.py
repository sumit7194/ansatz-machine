"""killing_yano.py — general Killing-tensor / Killing-Yano machinery.

§69 verified Kerr's Killing-Yano 2-form numerically, hard-coded. This module is the general
tool behind it: given ANY metric it can

    is_killing_tensor(geo, K)         is K_ab a Killing tensor?        (symbolic, exact)
    killing_tensor_reducible(...)     is it just  c*g + sum c_IJ xi_I xi_J ?
    ky_root_spectrum_certificate()    THE POINTWISE OBSTRUCTION (below), proved by machine
    has_ky_root(geo, Kmix)            can K be Y.Y for SOME 2-form Y, anywhere?
    killing_yano_jet_bound(geo, ...)  an UPPER bound on dim{Killing-Yano tensors}

THE POINTWISE OBSTRUCTION — why a Killing tensor need not have a Killing-Yano root.
Write K_ab = Y_ac Y_b{}^c with Y antisymmetric. Raising one index,

    K^a{}_b = g^{ac} Y_cd g^{de} Y_eb = -(g^{-1} Y)^2      (using Y^T = -Y),

so K (mixed) is minus the SQUARE of A := g^{-1} Y. Now A is g-antisymmetric: A^T = -g A g^{-1},
so A is similar to -A^T, hence to -A, so spec(A) = -spec(A) and the eigenvalues of A come in
+/- pairs. The eigenvalues of K = -A^2 are therefore -mu^2, and each +/-mu pair contributes the
SAME value twice:

    ** every eigenvalue of (Y.Y)^a{}_b has EVEN multiplicity, for every 2-form Y. **

Contrapositive, and this is the certificate: a Killing tensor whose mixed eigenvalues are four
DISTINCT numbers at even one point is not the square of any antisymmetric tensor there -- let
alone of a Killing-Yano one. This is stronger than "the Killing-Yano equation has no solution":
it fails already at the level of pointwise linear algebra, so no amount of PDE-solving can help.

The argument is proved by machine in ky_root_spectrum_certificate() rather than quoted -- the
characteristic polynomial of -(g^{-1}Y)^2 is verified to be a perfect square for a general
symmetric g and a general antisymmetric Y (§102 discipline: never trust a fact you can check).

THE JET BOUND — a one-sided but RIGOROUS "no Killing-Yano tensor exists" certificate.
Every smooth Killing-Yano tensor has a Taylor jet at a point, and that jet must satisfy the
Taylor coefficients of nabla_(a Y_b)c = 0. Truncating at order N gives a finite linear system;
its solution space CONTAINS the jets of all true solutions. So the computed dimension is an
UPPER bound -- and an upper bound of 0 at a point p proves Y(p) = 0 for every Killing-Yano
tensor. Repeat at several points and Y vanishes identically. (Lower bounds are NOT implied: a
nonzero jet dimension only means the truncation did not yet decide.)

Validated in both directions: Minkowski returns 10 (the maximal Killing-Yano space in 4D flat
space) and Schwarzschild returns 1 (its single known Killing-Yano tensor) -- so the bound is
not vacuously zero. See scripts/120_candidate_A_no_ky.py.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import zero_simplify


# --------------------------------------------------------------------------- Killing tensors
def is_killing_tensor(geo, Kdn, simp=zero_simplify):
    """Residuals of nabla_(a K_bc) = 0 for a symmetric COVARIANT K_ab. Returns the list of
    (a,b,c, residual) that did not simplify to zero -- empty list means VERIFIED."""
    n, x, Gam = geo.n, geo.coords, geo.christoffel

    def nab(a, b, c):
        e = sp.diff(Kdn[b, c], x[a])
        for f in range(n):
            e -= Gam[f][a][b] * Kdn[f, c] + Gam[f][a][c] * Kdn[b, f]
        return e

    bad = []
    for a in range(n):
        for b in range(a, n):
            for c in range(b, n):
                r = simp(nab(a, b, c) + nab(b, c, a) + nab(c, a, b))
                if r != 0:
                    bad.append((a, b, c, r))
    return bad


def killing_tensor_reducible(geo, Kup, kvs):
    """Is the CONTRAVARIANT Killing tensor K^{ab} a trivial combination
    c0 g^{ab} + sum_IJ c_IJ xi_I^a xi_J^b with CONSTANT coefficients? (kvs = Killing vectors,
    each a length-n list of components.) Returns (reducible?, solution-or-None).

    A reducible Killing tensor carries no new conserved quantity, so irreducibility is what
    makes a "hidden symmetry" hidden."""
    n = geo.n
    cs = []
    T = geo.ginv * sp.Symbol("c_g")
    cs.append(sp.Symbol("c_g"))
    for i, xi in enumerate(kvs):
        for j, et in enumerate(kvs):
            if j < i:
                continue
            c = sp.Symbol(f"c_{i}{j}")
            cs.append(c)
            blk = sp.Matrix(n, n, lambda a, b: (xi[a] * et[b] + xi[b] * et[a]) / 2)
            T = T + c * blk
    eqs = [sp.together(sp.expand(Kup[a, b] - T[a, b])) for a in range(n) for b in range(a, n)]
    eqs = [sp.numer(sp.cancel(e)) for e in eqs]
    sol = sp.solve(eqs, cs, dict=True)
    good = [s for s in sol if not any(v.free_symbols - set(cs) for v in s.values())]
    return (bool(good), good[0] if good else None)


# --------------------------------------------------------------------------- the KY-root obstruction
def ky_root_spectrum_certificate(trials=200, seed=20260723):
    """MACHINE PROOF of the pointwise obstruction: the characteristic polynomial of
    (Y.Y)^a{}_b is a PERFECT SQUARE, so every eigenvalue has even multiplicity.

    Proved in an ORTHONORMAL FRAME (g = eta), which loses no generality: the mixed tensor
    K^a{}_b transforms by conjugation under a change of frame, so its characteristic
    polynomial is frame-independent, and every Lorentzian metric admits an orthonormal frame
    at every point. Y stays completely general (6 free symbols).

    The frame step is the one piece of reasoning the symbolic run does not itself execute, so
    it is ALSO checked numerically against random NON-orthonormal Lorentzian metrics: random
    symmetric g of signature (-,+,+,+) and random Y, verifying the eigenvalues of -(g^-1 Y)^2
    always come in equal pairs. Returns (ok, char_poly, sqrt_poly, worst_numeric_pair_gap)."""
    import random

    import numpy as np

    lam = sp.Symbol("lambda")
    eta = sp.diag(-1, 1, 1, 1)
    ys = sp.symbols("y0:6", real=True)
    Y, k = sp.zeros(4, 4), 0
    for a in range(4):
        for b in range(a + 1, 4):
            Y[a, b], Y[b, a] = ys[k], -ys[k]
            k += 1
    A = eta * Y                                      # eta^{-1} = eta
    Kmix = -(A * A)                                  # K^a_b = -(g^{-1} Y)^2
    cp = sp.Poly(sp.expand((lam * sp.eye(4) - Kmix).det()), lam)
    c = cp.all_coeffs()                              # [1, c3, c2, c1, c0]
    p = sp.expand(c[1] / 2)
    q = sp.expand(c[2] / 2 - p * p / 2)
    resid = sp.expand(cp.as_expr() - (lam**2 + p * lam + q)**2)
    ok_sym = sp.simplify(resid) == 0

    # numeric check on random NON-orthonormal Lorentzian metrics (guards the frame step)
    rnd = random.Random(seed)
    worst = 0.0
    for _ in range(trials):
        L = np.array([[rnd.uniform(-1, 1) for _ in range(4)] for _ in range(4)])
        while abs(np.linalg.det(L)) < 1e-3:
            L = np.array([[rnd.uniform(-1, 1) for _ in range(4)] for _ in range(4)])
        gN = L.T @ np.diag([-1.0, 1, 1, 1]) @ L      # random Lorentzian metric
        yN = np.zeros((4, 4))
        for a in range(4):
            for b in range(a + 1, 4):
                yN[a, b] = rnd.uniform(-2, 2)
                yN[b, a] = -yN[a, b]
        Am = np.linalg.solve(gN, yN)
        ev = np.sort_complex(np.linalg.eigvals(-Am @ Am))
        # eigenvalues must pair up: after sorting, |e0-e1| and |e2-e3| are ~0
        scale = max(1.0, float(np.max(np.abs(ev))))
        worst = max(worst, float(abs(ev[0] - ev[1]) + abs(ev[2] - ev[3])) / scale)
    return (ok_sym and worst < 1e-6, cp.as_expr(), lam**2 + p * lam + q, worst)


def ky_root_obstruction(geo, Kup, points=None, simp=zero_simplify):
    """Apply the certificate to a specific Killing tensor. Kup is CONTRAVARIANT K^{ab}.

    Returns a dict with the mixed tensor's eigenvalues, whether all four are pairwise
    distinct (symbolically and/or at sample points), and the verdict:
        NO_KY_ROOT   -- a simple eigenvalue exists => K != Y.Y for any 2-form Y
        HAS_EVEN_SPECTRUM -- the spectrum is compatible with a root (nothing proved either way)
    """
    n = geo.n
    Kmix = sp.simplify(Kup * geo.g)
    lam = sp.Symbol("lambda")
    cp = sp.factor((lam * sp.eye(n) - Kmix).det())
    evs = [sp.simplify(r) for r in sp.roots(sp.Poly(cp, lam), multiple=True)]
    pairs = [(i, j) for i in range(len(evs)) for j in range(i + 1, len(evs))]
    diffs = {(i, j): simp(evs[i] - evs[j]) for i, j in pairs}
    distinct_sym = all(d != 0 for d in diffs.values())
    witness = None
    if points:
        for pt in points:
            sub = dict(zip(geo.coords, pt))
            vals = [sp.nsimplify(sp.simplify(e.subs(sub))) for e in evs]
            if len(set(map(sp.srepr, vals))) == n:
                witness = (pt, vals)
                break
    ok = distinct_sym and witness is not None
    return {"char_poly": cp, "eigenvalues": evs, "pairwise_distinct_symbolic": distinct_sym,
            "witness_point": witness,
            "verdict": "NO_KY_ROOT" if ok else "HAS_EVEN_SPECTRUM"}


# --------------------------------------------------------------------------- the jet bound
def killing_yano_jet_bound(geo, base, order):
    """UPPER bound on dim{Killing-Yano 2-forms}, from the order-`order` Taylor jet of
    nabla_(a Y_b)c = 0 at the point `base` (a list of coordinate values).

    One-sided by construction: every true solution's jet lies in the computed space, so the
    returned number is >= the true dimension. 0 therefore PROVES Y(base) = 0 for every
    Killing-Yano tensor. The equations are cleared of denominators before the Taylor
    coefficients are read off, which is legitimate exactly because the denominators are checked
    to be nonzero at `base`."""
    n, coords, Gam = geo.n, geo.coords, geo.christoffel
    d = sp.symbols(f"jd0:{n}", real=True)
    at0 = {di: 0 for di in d}
    shift = {coords[i]: base[i] + d[i] for i in range(n)}
    mons = [m for k in range(order + 1)
            for m in itertools.combinations_with_replacement(range(n), k)]

    def mono(m):
        e = sp.Integer(1)
        for i in m:
            e *= d[i]
        return e

    unk, Y = [], [[sp.S.Zero] * n for _ in range(n)]
    for a in range(n):
        for b in range(a + 1, n):
            expr = sp.S.Zero
            for k, m in enumerate(mons):
                c = sp.Symbol(f"kyc_{a}{b}_{k}")
                unk.append(c)
                expr += c * mono(m)
            Y[a][b], Y[b][a] = expr, -expr

    Gl = [[[sp.S.Zero] * n for _ in range(n)] for _ in range(n)]
    for f in range(n):
        for a in range(n):
            for b in range(a, n):
                Gl[f][a][b] = Gl[f][b][a] = sp.cancel(sp.together(Gam[f][a][b])).subs(shift)

    def nab(a, b, c):
        e = sp.diff(Y[b][c], d[a])
        for f in range(n):
            e -= Gl[f][a][b] * Y[f][c] + Gl[f][a][c] * Y[b][f]
        return e

    tmons = [m for k in range(order)
             for m in itertools.combinations_with_replacement(range(n), k)]
    rows = []
    for a in range(n):
        for b in range(a, n):
            for c in range(n):
                e = sp.cancel(sp.together(nab(a, b, c) + nab(b, a, c)))
                num, den = sp.fraction(e)
                if den.subs(at0) == 0:
                    raise ValueError(f"denominator vanishes at the base point {base}")
                poly = sp.Poly(sp.expand(num), *d)
                for m in tmons:
                    deg = [0] * n
                    for i in m:
                        deg[i] += 1
                    co = poly.coeff_monomial(sp.prod([d[i]**deg[i] for i in range(n)]))
                    if co != 0:
                        rows.append(co)
    if not rows:
        return len(unk)
    M, _ = sp.linear_eq_to_matrix(rows, unk)
    return len(unk) - M.rank()
