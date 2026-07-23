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


# --------------------------------------------------------------------------- jet plumbing
def _truncate(expr, d, order):
    """Multivariate Taylor polynomial of a RATIONAL expression in the shift variables `d`,
    to total degree `order`, computed by polynomial arithmetic rather than differentiation.

    Why this exists: substituting a shifted point into a Christoffel symbol leaves a rational
    function whose numerator, once expanded, is enormous -- and every term of degree > order is
    dead weight, because the jet unknowns have non-negative degree so a high-degree Christoffel
    term can only feed Taylor coefficients we are about to discard. Truncating here turned the
    Killing-tensor counts from minutes-per-call into seconds-per-call."""
    num, den = sp.fraction(sp.cancel(sp.together(expr)))
    at0 = {di: 0 for di in d}
    c = den.subs(at0)
    if c == 0:
        raise ValueError("denominator vanishes at the base point")
    if den == c:
        return sp.Poly(sp.expand(num / c), *d).as_expr()
    # 1/den = (1/c) * sum_k E^k  with E = 1 - den/c  (no constant term)
    E = sp.Poly(sp.expand(1 - den / c), *d)
    acc, term = sp.Poly(1, *d), sp.Poly(1, *d)
    for _ in range(order):
        term = _trunc_poly(term * E, order)
        if term.is_zero:
            break
        acc = acc + term
    out = _trunc_poly(sp.Poly(sp.expand(num), *d) * acc, order)
    return (out.as_expr() / c)


def _trunc_poly(p, order):
    return sp.Poly({m: c for m, c in p.terms() if sum(m) <= order}, *p.gens) \
        if p.terms() else p


def _tr(e, d, order):
    """Truncate an already-polynomial expression in `d` to total degree `order`."""
    p = sp.Poly(sp.expand(e), *d)
    return _trunc_poly(p, order).as_expr() if p.terms() else sp.S.Zero


def christoffel_jet(g, coords, base, d, order):
    """Taylor polynomials of Gamma^f_ab about `base`, to total degree `order`, built by
    TRUNCATED POLYNOMIAL ARITHMETIC off the metric -- never touching the full symbolic
    Christoffel symbols.

    This is the difference between a usable tool and an unusable one: gr_engine's Christoffels
    for a two-variable metric are large rational functions, and merely substituting a shifted
    point and calling cancel() on them dominated everything downstream (tens of seconds per
    call, worse at higher order). Here the metric -- which is simple -- is expanded once, the
    inverse is obtained from a Neumann series, and every product is truncated immediately, so
    the cost depends on the jet order rather than on how ugly the Christoffels happen to be."""
    n = len(coords)
    shift = {coords[i]: base[i] + d[i] for i in range(n)}
    G = sp.Matrix(n, n, lambda a, b: _truncate(g[a, b].subs(shift), d, order + 1))
    G0 = G.subs({di: 0 for di in d})
    if G0.det() == 0:
        raise ValueError(f"metric is degenerate at the base point {base}")
    G0i = G0.inv()
    Delta = G - G0
    # (G0 + Delta)^{-1} = sum_k (-G0^{-1} Delta)^k G0^{-1}, truncated at `order`
    Gi, term = sp.Matrix(G0i), sp.eye(n)
    for _ in range(order):
        term = sp.Matrix(n, n, lambda a, b: _tr((-term * G0i * Delta)[a, b], d, order))
        if term.is_zero_matrix:
            break
        Gi = Gi + term * G0i
    Gi = sp.Matrix(n, n, lambda a, b: _tr(Gi[a, b], d, order))
    dG = [sp.Matrix(n, n, lambda a, b: sp.diff(G[a, b], d[e])) for e in range(n)]
    out = [[[sp.S.Zero] * n for _ in range(n)] for _ in range(n)]
    for f in range(n):
        for a in range(n):
            for b in range(a, n):
                s = sp.S.Zero
                for e in range(n):
                    s += Gi[f, e] * (dG[a][e, b] + dG[b][e, a] - dG[e][a, b])
                out[f][a][b] = out[f][b][a] = _tr(s / 2, d, order)
    return out


def _nullity(rows, unk, prime=2147483647):
    """dim of the solution space of the linear system `rows` = 0 in the unknowns `unk`.

    The rank is taken over GF(p) for a large prime. rank_GF(p) <= rank_Q always, so the
    returned nullity is >= the true nullity: the ONE-SIDED (upper-bound) character of the jet
    argument survives the shortcut, which is the only property the certificate relies on."""
    if not rows:
        return len(unk)
    M, _ = sp.linear_eq_to_matrix(rows, unk)
    # Clear denominators row by row, then reduce mod p. Without this the exact-rational
    # row reduction spends all its time in gcd on the huge fractions the Neumann series
    # produces -- it was 41 of the 42 seconds of a call that is otherwise instant.
    try:
        from sympy.polys.domains import GF
        from sympy.polys.matrices import DomainMatrix
        K = GF(prime)
        rowsp = []
        for i in range(M.rows):
            row = []
            for j in range(M.cols):
                v = M[i, j]
                if not v.is_Rational:
                    raise TypeError(f"non-rational matrix entry {v}")
                row.append(K(int(v.p) * pow(int(v.q), -1, prime)))
            rowsp.append(row)
        return len(unk) - DomainMatrix(rowsp, (M.rows, M.cols), K).rank()
    except Exception:
        return len(unk) - M.rank()


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
    n, coords = geo.n, geo.coords
    d = sp.symbols(f"jd0:{n}", real=True)
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

    Gl = christoffel_jet(geo.g, coords, base, d, order)

    def nab(a, b, c):
        e = sp.diff(Y[b][c], d[a])
        for f in range(n):
            e -= Gl[f][a][b] * Y[f][c] + Gl[f][a][c] * Y[b][f]
        return e

    rows = []
    for a in range(n):
        for b in range(a, n):
            for c in range(n):
                poly = sp.Poly(sp.expand(nab(a, b, c) + nab(b, a, c)), *d)
                rows.extend(co for m, co in poly.terms() if sum(m) < order and co != 0)
    return _nullity(rows, unk)


def killing_tensor_jet_bound(geo, base, rank, order):
    """UPPER bound on dim{rank-`rank` Killing tensors}, by the same one-sided jet argument as
    killing_yano_jet_bound: the Taylor coefficients of nabla_(a0 K_a1...an) = 0 at `base`.

    A rank-n Killing tensor is exactly a degree-n homogeneous polynomial first integral of the
    geodesic flow, so this counts the polynomial invariants of that degree. The count INCLUDES
    the trivial ones (symmetrised products of the metric and of lower-rank Killing tensors) --
    e.g. flat 2D returns 3, 6, 10, 15 for ranks 1..4 -- so "no hidden invariant" means the
    bound equals the trivial count, not zero."""
    n, coords = geo.n, geo.coords
    d = sp.symbols(f"ktd0:{n}", real=True)
    jets = [m for k in range(order + 1)
            for m in itertools.combinations_with_replacement(range(n), k)]
    comps = list(itertools.combinations_with_replacement(range(n), rank))

    def mono(m):
        e = sp.Integer(1)
        for i in m:
            e *= d[i]
        return e

    unk, K = [], {}
    for ci, comp in enumerate(comps):
        expr = sp.S.Zero
        for k, m in enumerate(jets):
            c = sp.Symbol(f"ktc_{ci}_{k}")
            unk.append(c)
            expr += c * mono(m)
        K[comp] = expr

    def Kof(idx):
        return K[tuple(sorted(idx))]

    Gl = christoffel_jet(geo.g, coords, base, d, order)

    def nab(b, idx):
        e = sp.diff(Kof(idx), d[b])
        for j in range(rank):
            for f in range(n):
                e -= Gl[f][b][idx[j]] * Kof(idx[:j] + (f,) + idx[j + 1:])
        return e

    rows = []
    for M in itertools.combinations_with_replacement(range(n), rank + 1):
        # symmetrisation over which slot carries the derivative (K is already symmetric)
        e = sp.S.Zero
        for i in range(rank + 1):
            e += nab(M[i], M[:i] + M[i + 1:])
        poly = sp.Poly(sp.expand(e), *d)
        rows.extend(co for m, co in poly.terms() if sum(m) < order and co != 0)
    return _nullity(rows, unk)
