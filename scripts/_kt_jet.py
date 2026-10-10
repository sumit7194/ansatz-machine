#!/usr/bin/env python3
"""ANSATZ-FREE upper bound on the number of Killing tensors of rank d, by prolongation at ONE point (Cartan-Kaehler /
prolongation-projection, as in Kruglikov-Matveev arXiv:1111.4690 and Vollmer arXiv:1602.08968).

THE IDEA. A Killing tensor invariant under the two Killing vectors d_t, d_phi is I = sum_m m(p) K_m(x, y), m running over
momentum monomials of degree d. Expand each K_m in Taylor series at a regular point P = (x0, y0):
K_m = sum c_{m,ij} u^i v^j, u = x - x0, v = y - y0. The Taylor coefficients of {H, I} of total degree <= M are linear in
the c's with |i + j| <= M + 1: they ARE the M-th prolongation of the PDE system, evaluated at P. Every true Killing tensor
gives a kernel vector, and distinct tensors give distinct jets, so

    number of Killing tensors (invariant under d_t, d_phi)  <=  #columns - rank        (an UPPER BOUND, no ansatz).

When the bound equals the number of trivial tensors (products of p_t, p_phi, H), nonexistence is PROVED, locally near P,
for smooth coefficients of any form. There is no basis box and no denominator. Over GF(p) the rank can only drop, so the
mod-p bound is still a valid upper bound. A bad prime or point gives "inconclusive", never a false null.

Branches: H is even in (p_x, p_y), so I splits by the parity of its (p_x, p_y)-degree (Vollmer's e = 0 / 1). Each is
solved separately, and the bound is the sum.

Exactness: the metric is rational with rational coefficients. Taylor series are computed mod p by polynomial shift and
truncated series division. No floats, no symbolic differentiation of large expressions.

    .venv/bin/python scripts/_kt_jet.py --metric ts2:4/5 --rank 6 [--M 6] [--point 1/2,2] [--prime 0] [--engine flint|rust]
"""
import itertools
import json
import os
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_metrics as MM  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIMES = (2147483647, 2147483629)
x, y = MM.x, MM.y


def modq(r, p):
    """A rational -> GF(p). Refuses if p divides the denominator: that would be a silent wrong answer."""
    r = sp.Rational(r)
    if r.q % p == 0:
        raise ValueError(f"prime {p} divides a denominator ({r.q})")
    return (r.p % p) * pow(r.q % p, p - 2, p) % p


class Series:
    """Truncated bivariate power series sum a_ij u^i v^j (i + j <= T) over GF(p), as a (T+1)x(T+1) int64 array."""

    def __init__(self, T, p, a=None):
        self.T, self.p = T, p
        self.a = np.zeros((T + 1, T + 1), np.int64) if a is None else a
        i, j = np.indices((T + 1, T + 1))
        self.a[i + j > T] = 0

    def mul(self, o):
        T, p = self.T, self.p
        out = np.zeros((T + 1, T + 1), np.int64)
        for i in range(T + 1):
            for j in range(T + 1 - i):
                c = int(self.a[i, j])
                if c:
                    out[i:, j:] = (out[i:, j:] + c * o.a[:T + 1 - i, :T + 1 - j]) % p
        return Series(T, p, out)

    def inv(self):
        T, p = self.T, self.p
        c0 = int(self.a[0, 0])
        if c0 == 0:
            raise ValueError("series not invertible at the point (denominator vanishes there)")
        c0i = pow(c0, p - 2, p)
        # 1/(c0 (1 + e)) = c0^-1 sum (-e)^k, e has no constant term: k <= T suffices
        e = Series(T, p, self.a * c0i % p)
        e.a[0, 0] = 0
        term = Series(T, p); term.a[0, 0] = 1
        tot = Series(T, p); tot.a[0, 0] = 1
        neg_e = Series(T, p, (-e.a) % p)
        for _ in range(T):
            term = term.mul(neg_e)
            tot = Series(T, p, (tot.a + term.a) % p)
        return Series(T, p, tot.a * c0i % p)

    def du(self):
        T, p = self.T, self.p
        out = np.zeros((T + 1, T + 1), np.int64)
        out[:T, :] = (self.a[1:, :] * np.arange(1, T + 1)[:, None]) % p
        return Series(T, p, out)

    def dv(self):
        T, p = self.T, self.p
        out = np.zeros((T + 1, T + 1), np.int64)
        out[:, :T] = (self.a[:, 1:] * np.arange(1, T + 1)[None, :]) % p
        return Series(T, p, out)


def poly_series(expr, x0, y0, T, p):
    """Polynomial in x, y with rational coefficients -> its Taylor series at (x0, y0), truncated at total degree T."""
    P = sp.Poly(sp.expand(expr), x, y)
    X0, Y0 = modq(x0, p), modq(y0, p)
    from math import comb
    out = np.zeros((T + 1, T + 1), np.int64)
    for (a, b), c in zip(P.monoms(), P.coeffs()):
        cm = modq(c, p)
        if not cm:
            continue
        # (x0 + u)^a (y0 + v)^b = sum_k sum_l C(a,k) C(b,l) x0^(a-k) y0^(b-l) u^k v^l
        for k in range(min(a, T) + 1):
            ck = cm * comb(a, k) % p * pow(X0, a - k, p) % p
            for l in range(min(b, T - k) + 1):
                out[k, l] = (out[k, l] + ck * comb(b, l) % p * pow(Y0, b - l, p)) % p
    return Series(T, p, out)


def rational_series(expr, x0, y0, T, p):
    num, den = sp.fraction(sp.cancel(sp.together(expr)))
    return poly_series(num, x0, y0, T, p).mul(poly_series(den, x0, y0, T, p).inv())


def monomials(d):
    """Exponent tuples (e_t, e_x, e_y, e_phi) of total degree d."""
    return [e for e in itertools.product(range(d + 1), repeat=4) if sum(e) == d]


def build(ginv, d, M, x0, y0, p, branch, G=None):
    """The M-th prolongation matrix at P for rank d, one (p_x, p_y)-parity branch. Returns (rows, cols, dense int64).
    G: optional precomputed {(a, b): Series of g^ab at P, truncated at M + 2} for non-rational metrics (_kt_jet_mn)."""
    T = M + 2                         # H's series needed to degree M+1 after one derivative
    if G is None:
        G = {}
        for a in range(4):
            for b in range(a, 4):
                if ginv[a, b] != 0:
                    G[(a, b)] = rational_series(ginv[a, b], x0, y0, T, p)
    for (a, b) in G:
        if (a, b) in ((0, 1), (0, 2), (1, 3), (2, 3), (1, 2)):
            raise ValueError("this implementation assumes no t/phi - x/y and no x-y cross terms in g^ab")
    # H = 1/2 g^ab p_a p_b  ->  as {momentum exponent: series}; off-diagonal (a<b) appears twice in the sum: factor 1
    half = pow(2, p - 2, p)
    Hs = {}
    for (a, b), s in G.items():
        e = [0, 0, 0, 0]; e[a] += 1; e[b] += 1
        fac = half if a == b else 1
        Hs[tuple(e)] = Series(T, p, s.a * fac % p)
    dHx = {e: s.du() for e, s in Hs.items()}
    dHy = {e: s.dv() for e, s in Hs.items()}
    gxx, gyy = G[(1, 1)], G[(2, 2)]           # dH/dp_x = g^xx p_x, dH/dp_y = g^yy p_y
    mons = [m for m in monomials(d) if (m[1] + m[2]) % 2 == branch]
    J = [(i, j) for i in range(M + 2) for j in range(M + 2 - i)]          # unknown jets, i+j <= M+1
    R = [(i, j) for i in range(M + 1) for j in range(M + 1 - i)]          # equations, i+j <= M
    col = {(m, ij): n for n, (m, ij) in enumerate((m, ij) for m in mons for ij in J)}
    rowk = {}
    entries = {}

    def add(mrow, i, j, cidx, val):
        if i + j > M or val % p == 0:
            return
        key = (mrow, i, j)
        r = rowk.setdefault(key, len(rowk))
        entries[(r, cidx)] = (entries.get((r, cidx), 0) + val) % p

    def addm(e, d_):
        return tuple(a + b for a, b in zip(e, d_))

    for m in mons:
        for (i, j) in J:
            c = col[(m, (i, j))]
            # term A: sum_q (d_q H)(dI/dp_q): dI/dp_x = e_x * m/p_x * u^i v^j
            for q, dH in ((1, dHx), (2, dHy)):
                if m[q] == 0:
                    continue
                mq = list(m); mq[q] -= 1
                for eh, s in dH.items():
                    mr = addm(tuple(mq), eh)
                    for (a, b) in zip(*np.nonzero(s.a)):
                        add(mr, a + i, b + j, c, m[q] * int(s.a[a, b]))
            # term B: - sum_q (dH/dp_q)(d_q I): dH/dp_x = g^xx p_x ; d_x (u^i v^j) = i u^(i-1) v^j
            for q, g, di, dj in ((1, gxx, 1, 0), (2, gyy, 0, 1)):
                k = i if q == 1 else j
                if k == 0:
                    continue
                mr = list(m); mr[q] += 1
                ii, jj = i - di, j - dj
                for (a, b) in zip(*np.nonzero(g.a)):
                    add(tuple(mr), a + ii, b + jj, c, -k * int(g.a[a, b]))
    A = np.zeros((len(rowk), len(col)), np.int64)
    for (r, c), v in entries.items():
        A[r, c] = v % p
    return A, mons, J


def rank_of(A, p, engine, threads=8):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "m.ktd")
        with open(f, "wb") as fh:
            fh.write(b"KTD1"); fh.write(np.array([A.shape[0], A.shape[1], p], "<u8").tobytes())
            fh.write(np.ascontiguousarray(A % p).astype("<u4").tobytes())
        exe = os.path.join(ROOT, "native", "flint_rank") if engine == "flint" else \
            os.path.join(ROOT, "rust", "ktdense", "target", "release", "ktdense")
        out = subprocess.run([exe, f, str(threads)], capture_output=True, text=True, check=True)
        return json.loads(out.stdout.strip().splitlines()[-1])


def trivial_count(d, gen_lsq=False):
    """Products p_t^a p_phi^b H^c with a + b + 2c = d (all in the even (p_x,p_y)-parity branch)."""
    return sum(1 for a in range(d + 1) for b in range(d + 1) for c in range(d // 2 + 1) if a + b + 2 * c == d)


def main():
    def arg(fl, dflt=None, cast=str):
        return cast(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else dflt
    from _kt_exact_op import get_metric
    spec, d = arg("--metric"), arg("--rank", 2, int)
    M = arg("--M", d, int)
    pt = arg("--point", "1/2,2").split(",")
    x0, y0 = sp.Rational(pt[0]), sp.Rational(pt[1])
    prime = arg("--prime", 0, int); p = PRIMES[prime]
    engine = arg("--engine", "flint")
    sabotage = "--sabotage" in sys.argv
    t0 = time.time()
    ginv, name = get_metric(spec)
    if sabotage:   # a deliberately wrong, NON-SEPARABLE metric: g^xx*(1 + x*y/7). (A factor in x alone keeps Kerr separable and Carter alive -- section 139.)
        ginv = ginv.copy(); ginv[1, 1] = sp.cancel(ginv[1, 1] * (1 + x * y / 7))
        name += " [SABOTAGED g^xx*(1+x*y/7), non-separable]"
    tot = 0
    res = {}
    for branch in (0, 1):
        A, mons, J = build(ginv, d, M, x0, y0, p, branch)
        r = rank_of(A, p, engine)
        k = A.shape[1] - r["rank"]
        res[branch] = dict(rows=A.shape[0], cols=A.shape[1], rank=r["rank"], bound=k, seconds=r["seconds"])
        tot += k
        print(f"  {name} rank {d} M={M} at ({x0},{y0}) prime {prime} branch e={branch}: matrix {A.shape[0]}x{A.shape[1]} "
              f"({len(mons)} monomials x {len(J)} jets), rank {r['rank']} -> bound {k}  [{engine} {r['seconds']}s]",
              flush=True)
    triv = trivial_count(d)
    print(f"VERDICT {name} rank {d} M={M} point ({x0},{y0}) prime {prime}: upper bound {tot} (even {res[0]['bound']}, "
          f"odd {res[1]['bound']}); trivial {triv}; {'NO NONTRIVIAL KILLING TENSOR (bound = trivial)' if tot == triv else 'bound exceeds trivial by ' + str(tot - triv)}"
          f"  [{time.time()-t0:.0f}s]", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
