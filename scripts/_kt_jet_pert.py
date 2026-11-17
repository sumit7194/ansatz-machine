#!/usr/bin/env python3
"""First-order ansatz-free jet test: which Kerr Killing tensors survive a small deformation? (data/jet/PERTURB_PREREGISTRATION.md)

H = H0 + eps H1, F = F0 + eps F1 (invariant valence-d tensors). {H, F} = O(eps^2) <=> {H0, F0} = 0 and
{H0, F1} + {H1, F0} = 0. The M-th prolongation of BOTH equations at a point P, in the jets of (F0, F1), gives
B(d) = #cols - rank >= dim{(F0, F1)}. With B0(d) = the bound of the first equation alone (Kerr: = K(d)),
S(d) = B(d) - B0(d) is an upper bound on the number of Kerr tensors that extend to first order. S(d) = T(d) (the
trivial floor 2, 4, 6, 9, ...) proves that nothing beyond p_t, p_phi, H products survives (local, any coefficient form,
invariant class, first order in eps).
The bracket coefficients reuse _kt_jet.build's term logic, rewritten to return keyed entries so the blocks share
row/column keys. Base: Kerr in the MN chart (beta = 0) with R0-rational points (as in section 151).
    .venv/bin/python scripts/_kt_jet_pert.py stage1 [--ranks 1-4] [--threads 1]
    .venv/bin/python scripts/_kt_jet_pert.py target [--ranks 1-4] [--threads 1]
"""
import itertools
import os
import sys
import time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_jet as KJ  # noqa: E402
import _kt_jet_mn as JM  # noqa: E402
import _mn_build as MB  # noqa: E402

x, y, R = MB.x, MB.y, MB.R
EA, EB, EP, EQ = MB.EA, MB.EB, MB.EP, MB.EQ
K_KERR = {1: 2, 2: 5, 3: 8, 4: 14, 5: 20, 6: 30}    # Kerr: products of p_t, p_phi, H, Q (checked by B0, not assumed)


def entries(G, d, M, mons, J, p):
    """{H_G, I} jet coefficients as {((mrow, i, j), (m, (a, b))): value}; H_G = 1/2 G^ab p_a p_b. Same terms as
    _kt_jet.build (term A: sum_q d_q H * dI/dp_q; term B: - sum_q dH/dp_q * d_q I), no x-y or t/phi-x/y cross terms."""
    half = pow(2, p - 2, p)
    Hs = {}
    for (a, b), s in G.items():
        e = [0, 0, 0, 0]; e[a] += 1; e[b] += 1
        Hs[tuple(e)] = KJ.Series(s.T, p, s.a * (half if a == b else 1) % p)
    dHx = {e: s.du() for e, s in Hs.items()}
    dHy = {e: s.dv() for e, s in Hs.items()}
    gxx, gyy = G.get((1, 1)), G.get((2, 2))
    out = {}

    def add(mrow, i, j, col, val):
        if i + j > M or val % p == 0:
            return
        key = (tuple(mrow), i, j)
        out[(key, col)] = (out.get((key, col), 0) + val) % p
    for m in mons:
        for (i, j) in J:
            col = (m, (i, j))
            for q, dH in ((1, dHx), (2, dHy)):
                if m[q] == 0:
                    continue
                mq = list(m); mq[q] -= 1
                for eh, s in dH.items():
                    mr = tuple(a + b for a, b in zip(mq, eh))
                    for (a, b) in zip(*np.nonzero(s.a)):
                        add(mr, a + i, b + j, col, m[q] * int(s.a[a, b]))
            for q, g, di, dj in ((1, gxx, 1, 0), (2, gyy, 0, 1)):
                if g is None:
                    continue
                k = i if q == 1 else j
                if k == 0:
                    continue
                mr = list(m); mr[q] += 1
                for (a, b) in zip(*np.nonzero(g.a)):
                    add(mr, a + i - di, b + j - dj, col, -k * int(g.a[a, b]))
    return out


def bounds(G0, G1, d, M, p, threads):
    """Return (B0, B, S) summed over the two (p_x, p_y)-parity branches."""
    J = [(i, j) for i in range(M + 2) for j in range(M + 2 - i)]
    B0t = Bt = 0
    for branch in (0, 1):
        mons = [m for m in KJ.monomials(d) if (m[1] + m[2]) % 2 == branch]
        e00 = entries(G0, d, M, mons, J, p)                       # {H0, F0}
        e01 = entries(G1, d, M, mons, J, p)                       # {H1, F0}
        cols = {c: n for n, c in enumerate(itertools.product((0, 1), [(m, ij) for m in mons for ij in J]))}
        rk0 = sorted({r for r, _ in e00})
        A0 = np.zeros((len(rk0), len(mons) * len(J)), np.int64)
        ri0 = {r: n for n, r in enumerate(rk0)}
        for (r, c), v in e00.items():
            A0[ri0[r], cols[(0, c)]] = v
        b0 = A0.shape[1] - KJ.rank_of(A0, p, "flint", threads)["rank"] if A0.size else A0.shape[1]
        rows = sorted({(0, r) for r, _ in e00} | {(1, r) for r, _ in e00} | {(1, r) for r, _ in e01})
        ri = {r: n for n, r in enumerate(rows)}
        A = np.zeros((len(rows), len(cols)), np.int64)
        for (r, c), v in e00.items():
            A[ri[(0, r)], cols[(0, c)]] = v                     # eq 0: {H0, F0}
            A[ri[(1, r)], cols[(1, c)]] = v                     # eq 1: {H0, F1} ...
        for (r, c), v in e01.items():
            A[ri[(1, r)], cols[(0, c)]] = (A[ri[(1, r)], cols[(0, c)]] + v) % p   # ... + {H1, F0}
        b = A.shape[1] - KJ.rank_of(A, p, "flint", threads)["rank"]
        B0t += b0
        Bt += b
    return B0t, Bt, Bt - B0t


# ---------------------------------------------------------------------------------------------------- series at a point
def base_series(spec, pt, T, draw):
    """Kerr (MN chart, beta = 0) series object and G0 at point pt, truncation T."""
    Mm, a, _ = JM.TARGETS[spec]
    F0 = MB.mn_functions(Mm, a, sp.Integer(0))
    x0, y0, R0 = JM.POINTS[pt]
    pi, seed = draw
    p = JM.PRIMES[pi]
    S = JM.MNSeries(F0, x0, y0, R0, T, p, JM.draw_t(seed, p))
    return S, S.ginv(), p


def mn_beta_G1(spec, S):
    """d g^ab / d beta at beta = 0 for MN (exact): sum_i dG/dE_i |_{E=1} * dZ_i/dbeta |_{beta=0}."""
    Mm, a, _ = JM.TARGETS[spec]
    b = sp.Symbol("beta")
    F = MB.mn_functions(Mm, a, b)
    Gsym = JM.ginv_formula_symbolic(F)
    one = {EA: 1, EB: 1, EP: 1, EQ: 1}
    G1 = {}
    for (i, j) in ((0, 0), (0, 3), (3, 3), (1, 1), (2, 2)):
        tot = sp.Integer(0)
        for E, Z in F["expo"].items():
            dz = sp.diff(Z, b).subs(b, 0)
            if dz == 0:
                continue
            tot += sp.diff(Gsym[i, j], E).subs(b, 0).xreplace(one) * dz
        tot += sp.diff(Gsym[i, j], b).subs(b, 0).xreplace(one)         # any explicit beta (none expected)
        G1[(i, j)] = S.ev(tot) if tot != 0 else None
    return {k: v for k, v in G1.items() if v is not None}


def control_G1(kind, S, G0):
    """Stage-1 controls on the exact Kerr base (addendum 1)."""
    T, p = S.T, S.p
    X2m1 = S.ev(x ** 2 - 1)
    if kind == "separable":                                     # dg^xx = s(x) g0^xx / (x^2 - 1), s = x^3/7
        return {(1, 1): G0[(1, 1)].mul(S.ev(x ** 3 / 7)).mul(X2m1.inv())}
    if kind == "sabotage":                                      # dg^xx = (x y / 7) g0^xx
        return {(1, 1): G0[(1, 1)].mul(S.ev(x * y / 7))}
    if kind == "null":                                          # dg = -L_xi g, xi^x = s(x) = x^2/5
        s, ds = S.ev(x ** 2 / 5), S.ev(2 * x / 5)
        out = {}
        for k, g in G0.items():
            v = g.du().mul(s)
            if k == (1, 1):
                v = JM.s_add(v, JM.s_scale(g.mul(ds), -2))
            out[k] = JM.s_scale(v, -1)
        return out
    raise ValueError(kind)


def main():
    def arg(fl, dflt, cast=str):
        return cast(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else dflt
    mode = sys.argv[1]
    lo, hi = map(int, arg("--ranks", "1-4").split("-"))
    threads = arg("--threads", 1, int)
    jobs = ([(k, "kerr1", "P1") for k in ("null", "separable", "sabotage")] if mode == "stage1"
            else [("mn-beta", s, pt) for s in ("p1", "p2") for pt in ("P1", "P2")])
    for kind, spec, pt in jobs:
        for d in range(lo, hi + 1):
            t0 = time.time()
            Ss = []
            for draw in JM.DRAWS:
                S, G0, p = base_series("kerr1" if kind != "mn-beta" else {"p1": "kerr1", "p2": "kerr2"}[spec], pt, d + 2, draw)
                G1 = control_G1(kind, S, G0) if kind != "mn-beta" else mn_beta_G1(spec, S)
                Ss.append(bounds(G0, G1, d, d, p, threads))
            B0, B, Sd = min(Ss, key=lambda t: t[2])
            triv = KJ.trivial_count(d)
            tag = "" if mode == "stage1" else "  [PRE-VALIDATION: stage 2 not yet passed]"
            print(f"VERDICT {kind} {spec} {pt} d={d}: B0={B0} (Kerr K={K_KERR.get(d)}) B={B} -> S={Sd} "
                  f"(draws {[t[2] for t in Ss]}); trivial T={triv}{tag}  [{time.time() - t0:.0f}s]", flush=True)


if __name__ == "__main__":
    main()
