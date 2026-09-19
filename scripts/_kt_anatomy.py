#!/usr/bin/env python3
"""Which deformations of Kerr keep Carter's constant alive? The exact answer, at O(zeta chi^2).

THE QUESTION BEHIND THE COUNT. The double tower says Carter dies in the sGB black hole (§130). The
anatomy runs (data/anat/) say more: switch the sGB correction on piece by piece, and the static
reshaping, the frame-dragging change and the quadrupolar shape change EACH kill Carter alone, while
the spherical O(chi^2) piece does not. Counts cannot say whether those three obstructions are
related -- whether some COMBINATION of them would let Carter live. This computes that exactly.

HOW. At fixed Kerr background, every equation of the zeta tower is linear in the deformation. So
each piece a is carried through zeta chi^0 and zeta chi^1 separately, for every Kerr chain k, and at
zeta chi^2 all the sources s_{k,a} become columns of ONE system [M | s_{1,1} ... s_{K,A}]. Its
nullspace gives V = { c : sum c_{k,a} s_{k,a} lies in the image of M }. A deformation with weights w
keeps a direction gamma alive iff gamma (x) w lies in V. So:

    W_k = { w : e_k (x) w in V }          and      Carter-preserving deformations = intersection of W_k

(every chain survives, Carter included). Survivor counts for any w follow too, and must reproduce the
anatomy table -- a built-in consistency check.

CONTROLS THAT MUST PRESERVE CARTER (and so must land in the subspace -- if they do not, the method is
wrong, not the physics): a shift of Kerr's SPIN (d/dchi of the Kerr family), a shift of its MASS at
fixed chi (another Kerr), and two pure COORDINATE changes (Lie derivatives of the Kerr metric along a
radial and an angular vector field -- the same black hole, relabelled).

Usage:  _kt_anatomy.py [--rank 2 --denpow 6 --margin 6]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
import _kt_exact as EX  # noqa: E402
import _kt_metrics as MM  # noqa: E402
import _kt_perturb as PB  # noqa: E402
import _kt_search as K  # noqa: E402
from _kt_ckcompare import load  # noqa: E402
from _kt_opfast import operator_from_templates  # noqa: E402

x, y = sp.symbols("x y", real=True)
chi = KD.chi


def arg(fl, d, c=int):
    return c(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else d


# ---------------------------------------------------------------- small dense linear algebra mod p

def rref(rows, ncols, p):
    """Row-reduced echelon form (list of rows) and pivot columns."""
    M = [[v % p for v in r] for r in rows]
    piv, r = [], 0
    for c in range(ncols):
        k = next((i for i in range(r, len(M)) if M[i][c]), None)
        if k is None:
            continue
        M[r], M[k] = M[k], M[r]
        inv = pow(M[r][c], p - 2, p)
        M[r] = [v * inv % p for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
        piv.append(c)
        r += 1
    return M[:r], piv


def rank(rows, ncols, p):
    return len(rref(rows, ncols, p)[0]) if rows else 0


def kernel(rows, ncols, p):
    """Basis of { v : rows . v = 0 }."""
    R, piv = rref(rows, ncols, p) if rows else ([], [])
    free = [c for c in range(ncols) if c not in piv]
    out = []
    for f in free:
        v = [0] * ncols
        v[f] = 1
        for i, c in enumerate(piv):
            v[c] = (-R[i][f]) % p
        out.append(v)
    return out


def intersect(A, B, n, p):
    """Basis of span(A) ∩ span(B) in GF(p)^n."""
    if not A or not B:
        return []
    # x.A = y.B  <=>  [A; -B]^T (x, y) = 0
    cols = [[a[j] for a in A] + [(-b[j]) % p for b in B] for j in range(n)]
    sol = kernel(cols, len(A) + len(B), p)
    vecs = [[sum(s[i] * A[i][j] for i in range(len(A))) % p for j in range(n)] for s in sol]
    return rref(vecs, n, p)[0]


# ---------------------------------------------------------------- deformation pieces

def lie_inverse(giK, xi):
    """Inverse-metric perturbation of a pure coordinate change along xi: -L_xi g^{ab}."""
    C = K.COORDS
    n = len(C)
    out = sp.zeros(n, n)
    for a in range(n):
        for b in range(n):
            e = sum(xi[c] * sp.diff(giK[a, b], C[c]) for c in range(n))
            e -= sum(giK[c, b] * sp.diff(xi[a], C[c]) for c in range(n))
            e -= sum(giK[a, c] * sp.diff(xi[b], C[c]) for c in range(n))
            out[a, b] = -e
    return out


def chi_pieces(mat_expr):
    """chi^0..chi^2 coefficient matrices of a matrix expression in chi."""
    out = []
    for n in range(3):
        out.append(sp.Matrix(mat_expr.shape[0], mat_expr.shape[1], lambda i, j: sp.cancel(sp.together(
            sp.diff(mat_expr[i, j], chi, n).subs(chi, 0) / sp.factorial(n)))))
    return out


def build_pieces(GI):
    """name -> ([g^ab pieces chi^0..2], role). Every one is an O(zeta) deformation of Kerr."""
    pieces = {}
    for name in KD.SGB_ALL:
        pieces[name] = (KD.sgb_ginv_pieces(GI, keep=(name,)), "sGB")
    # spin shift: chi -> chi (1 + eps) scales the chi^n piece by n
    pieces["spin"] = ([sp.zeros(4, 4), GI[1], 2 * GI[2]], "control")
    # mass shift at fixed chi: d/dM of the Kerr family at M = 1
    m = sp.Symbol("m", positive=True)
    GIm = KD.kerr_chi_pieces(M=m)
    pieces["mass"] = ([sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.diff(G[i, j], m).subs(m, 1)))
                       for G in GIm], "control")
    # pure coordinate changes, preserving stationarity, axisymmetry and the reflection y -> -y
    giK = sum((chi ** n * GI[n] for n in range(3)), sp.zeros(4, 4))
    t_, x_, y_, ph_ = K.COORDS
    for name, xi in (("gauge_r", [0, 1 / x_, 0, 0]), ("gauge_y", [0, 0, y_ * (1 - y_ ** 2) / x_ ** 2, 0])):
        pieces[name] = (chi_pieces(lie_inverse(giK, xi)), "control")
    return pieces


# ---------------------------------------------------------------- the level solves

def level_solve(srcs, D, op, p, tag, n_w):
    """Nullspace of [M | srcs]; returns (list of particular F-vectors or None per source, V rows)."""
    lev = KD._prep_level(srcs, D, op, None, p, tag)
    ns = KD.nullspace_dicts(lev, n_w + len(srcs), p)
    S = len(srcs)
    part = [None] * S
    V = []
    for v in ns:
        cb = [int(z) % p for z in v[n_w:]]
        if any(cb):
            V.append(cb)
            nz = [j for j, c in enumerate(cb) if c]
            if len(nz) == 1 and cb[nz[0]] == 1:
                part[nz[0]] = v
    return part, V


if __name__ == "__main__":
    rank_, denpow, margin = arg("--rank", 2), arg("--denpow", 6), arg("--margin", 6)
    p = KD.PRIMES[arg("--prime", 0)]
    t0 = time.time()
    t_, ph = sp.symbols("t phi", real=True)
    K.set_dim((t_, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    GI = KD.kerr_chi_pieces()
    L, _, _ = MM.denominator(GI[0])
    den = L ** denpow
    _, prods, _ = EX.generators(GI[0], rank_, den)
    bx, by = EX.reducible_box(prods, den)
    dx, dy = bx + margin, by + margin
    mons = K.monomials(rank_)
    cols, _ = PB.coefficient_basis(mons, dx, dy, den)
    n_w = len(cols)
    H = [KD.hamiltonian(GI[n]) for n in range(3)]
    dicts0, D = operator_from_templates(H[0], mons, dx, dy, den, p)
    op = KD._OpArrays(dicts0, p)
    pfx = "" if p == KD.PRIMES[0] else f"_p{KD.PRIMES.index(p)}"
    ck = f"data/kt_double_chains_r{rank_}_d{denpow}_b{dx}x{dy}{pfx}.pkl"
    chains = [[[sp.sympify(e) for e in lvl] for lvl in ch] for ch in load(ck)["chains"]]
    Kc = len(chains)
    print(f"rank {rank_}, denpow {denpow}, box {dx}x{dy}: {n_w} unknowns, {Kc} Kerr chains from {ck}",
          flush=True)

    def vec_to_co(v):
        F = [sp.Integer(0)] * len(mons)
        for j, (mi, a_, b_) in enumerate(cols):
            c_ = int(v[j]) % p
            if c_:
                F[mi] += c_ * x ** a_ * y ** b_
        return [sp.cancel(f / den) for f in F]

    pieces = build_pieces(GI)
    names = list(pieces)
    A = len(names)
    HS = {}
    for nm in names:
        gis, role = pieces[nm]
        bad = [(n, PB.check_perturbation_representable(gis[n], dx, dy, den)) for n in range(3)]
        bad = [(n, b) for n, b in bad if b]
        HS[nm] = [KD.hamiltonian(g) for g in gis]
        print(f"  piece {nm:8s} ({role:7s}) representable: {'yes' if not bad else bad}", flush=True)
        if bad:
            sys.exit(f"piece {nm} lies outside the ansatz; widen --denpow/--margin")

    def br(F, Hh):
        if Hh == 0 or all(f == 0 for f in F):
            return sp.Integer(0)
        return PB.bracket_raw_coeffs(F, Hh, mons)[0]

    # zeta chi^0 and zeta chi^1: particular solutions per (chain, piece)
    F1 = {}          # (k, name, n) -> coefficient list
    for n in (0, 1):
        srcs, keys = [], []
        for k, ch in enumerate(chains):
            for nm in names:
                acc = sp.Integer(0)
                for j in range(1, n + 1):
                    acc += br(F1[(k, nm, n - j)], H[j])
                for j in range(0, n + 1):
                    acc += br(ch[n - j], HS[nm][j])
                srcs.append(acc)
                keys.append((k, nm))
        part, _ = level_solve(srcs, D, op, p, f"zeta chi^{n}", n_w)
        fails = [keys[i] for i, v in enumerate(part) if v is None]
        if fails:
            sys.exit(f"zeta chi^{n}: no particular solution for {fails} -- a direction dies before "
                     f"chi^2, which the anatomy runs did not see; investigate before interpreting")
        for i, key in enumerate(keys):
            F1[(key[0], key[1], n)] = vec_to_co(part[i][:n_w])
        print(f"  zeta chi^{n}: all {len(srcs)} (chain, piece) sources solvable [{time.time()-t0:.0f}s]",
              flush=True)

    # zeta chi^2: one system, every (chain, piece) source a column
    srcs, keys = [], []
    for k, ch in enumerate(chains):
        for nm in names:
            acc = br(F1[(k, nm, 1)], H[1]) + br(F1[(k, nm, 0)], H[2])
            for j in range(3):
                acc += br(ch[2 - j], HS[nm][j])
            srcs.append(acc)
            keys.append((k, nm))
    _, V = level_solve(srcs, D, op, p, "zeta chi^2", n_w)
    S = len(srcs)
    V = rref(V, S, p)[0]
    print(f"  zeta chi^2: {S} columns, solvable combinations dim V = {len(V)} [{time.time()-t0:.0f}s]",
          flush=True)

    def block(k):
        return [k * A + a for a in range(A)]

    # W_k = { w : e_k (x) w in V }
    W = None
    for k in range(Kc):
        Uk = [[1 if j == k * A + a else 0 for j in range(S)] for a in range(A)]
        Ik = intersect(V, Uk, S, p)
        Wk = [[r[j] for j in block(k)] for r in Ik]
        W = Wk if W is None else intersect(W, Wk, A, p)

    def survivors(w):
        U = [[w[j % A] if j // A == k else 0 for j in range(S)] for k in range(Kc)]   # e_k (x) w
        return Kc - (rank(V + U, S, p) - rank(V, S, p))

    print("\n  SURVIVORS per single piece (must match the anatomy runs; floor = Kc - 1 at rank 2):")
    for a, nm in enumerate(names):
        w = [1 if b == a else 0 for b in range(A)]
        print(f"    {nm:8s} {survivors(w)} of {Kc}   ({pieces[nm][1]})", flush=True)
    wfull = [1 if pieces[nm][1] == "sGB" else 0 for nm in names]
    print(f"    full sGB {survivors(wfull)} of {Kc}", flush=True)

    print(f"\n  CARTER-PRESERVING DEFORMATIONS: dim {len(W)} of {A}  (pieces: {names})")
    for r in rref(W, A, p)[0]:
        terms = []
        for a, c in enumerate(r):
            if c:
                cc = c if c <= p // 2 else c - p
                terms.append(f"{cc}*{names[a]}")
        print("    " + " + ".join(terms))
    ctrl = [a for a, nm in enumerate(names) if pieces[nm][1] == "control"]
    ctrl_in = all(rank(W + [[1 if b == a else 0 for b in range(A)]], A, p) == len(W) for a in ctrl)
    sgb = [a for a, nm in enumerate(names) if pieces[nm][1] == "sGB"]
    Wsgb = intersect(W, [[1 if b == a else 0 for b in range(A)] for a in sgb], A, p)
    print(f"\n  controls (spin, mass, gauges) all Carter-preserving: {ctrl_in}")
    print(f"  Carter-preserving combinations of the sGB pieces alone: dim {len(Wsgb)}")
    for r in rref(Wsgb, A, p)[0]:
        print("    " + " + ".join(f"{(c if c <= p//2 else c - p)}*{names[a]}" for a, c in enumerate(r) if c))
    print(f"\n  total {time.time()-t0:.0f}s")
