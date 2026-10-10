#!/usr/bin/env python3
"""Ansatz-free prolongation bound (scripts/_kt_jet.py, section 149) for the NON-RATIONAL Manko-Novikov metric.
Pre-registration: data/jet/MN_PREREGISTRATION.md (11bb066).

MN contains R = sqrt(x^2 + y^2 - 1) and exponentials of rational functions of (x, y, R) (scripts/_mn_build.py, where
the metric is verified Ricci-flat exactly). At a jet point P with R0 rational, everything is a truncated Taylor series
mod p:
    R   = R0 * sum_k binom(1/2, k) w^k,          w = (x^2 + y^2 - 1)/R0^2 - 1   (no constant term)
    E_i = exp(Z_i(P)) * sum_k (Z_i - Z_i(P))^k / k!
The constants exp(Z_i(P)) are the ONLY transcendental input. Each Z_i(P) is rational, so with N = lcm of their
denominators, exp(Z_i(P)) = T^(n_i), T = e^(1/N), n_i = N Z_i(P). Every matrix entry is in Q[T, 1/T]. T is
transcendental (Lindemann), so the true rank is the rank over Q(T). T -> t in GF(p)* can only LOWER it, so
cols - rank_p >= the true bound. (Independent random E_i would compute a generic rank that can EXCEED the true one, so
they are NOT used.) Verdict = minimum over two draws (prime 0 / t from seed 1, prime 1 / t from seed 2).

    .venv/bin/python scripts/_kt_jet_mn.py --controls                    # controls 1-4 of the pre-registration
    .venv/bin/python scripts/_kt_jet_mn.py --mn p1 --ranks 1-8 [--threads 2]
"""
import os
import random
import sys
import time
from math import factorial, lcm

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_jet as KJ  # noqa: E402
import _mn_build as MB  # noqa: E402

x, y, R = MB.x, MB.y, MB.R
EA, EB, EP, EQ = MB.EA, MB.EB, MB.EP, MB.EQ
PRIMES = KJ.PRIMES
Series, modq = KJ.Series, KJ.modq
TARGETS = {"p1": (5, 3, sp.Rational(1, 5)), "p2": (13, 5, sp.Rational(-1, 3)),
           "kerr1": (5, 3, sp.Integer(0)), "kerr2": (13, 5, sp.Integer(0))}
POINTS = {"P1": (sp.Rational(17, 10), sp.Rational(3, 5), sp.Rational(3, 2)),
          "P2": (sp.Rational(19, 9), sp.Rational(-1, 3), sp.Rational(17, 9))}
DRAWS = ((0, 1), (1, 2))          # (prime index, seed for t)


def ps(expr, x0, y0, T, p):
    """poly_series on an expression in _mn_build's symbols (x, y positive) -- _kt_jet uses _kt_metrics' own x, y."""
    return KJ.poly_series(sp.sympify(expr).xreplace({x: KJ.x, y: KJ.y}), x0, y0, T, p)


# ---------------------------------------------------------------------------------------------------- series algebra
def s_const(c, T, p):
    s = Series(T, p); s.a[0, 0] = c % p; return s


def s_add(a, b):
    return Series(a.T, a.p, (a.a + b.a) % a.p)


def s_scale(a, c):
    return Series(a.T, a.p, a.a * (c % a.p) % a.p)


def s_pow(a, n):
    if n < 0:
        return s_pow(a.inv(), -n)
    out = s_const(1, a.T, a.p)
    base = a
    while n:
        if n & 1:
            out = out.mul(base)
        base = base.mul(base)
        n >>= 1
    return out


def s_powser(w, coeffs):
    """sum_k coeffs[k] w^k for w with no constant term (k <= T)."""
    T, p = w.T, w.p
    if w.a[0, 0] % p:
        raise ValueError("power series argument has a constant term")
    out = s_const(coeffs[0], T, p)
    term = s_const(1, T, p)
    for k in range(1, T + 1):
        term = term.mul(w)
        out = s_add(out, s_scale(term, coeffs[k]))
    return out


class MNSeries:
    """All MN building blocks as series at P, for one (prime, t) draw."""

    def __init__(self, F, x0, y0, R0, T, p, t, sabotage_f=False):
        assert R0 > 0 and R0 ** 2 == x0 ** 2 + y0 ** 2 - 1, "R0 must be the positive rational root at P"
        assert p > T + 1, "factorials up to T must be invertible mod p"
        assert t % p, "t must be nonzero mod p"
        self.T, self.p, self.F = T, p, F
        X = ps(x, x0, y0, T, p)
        Y = ps(y, x0, y0, T, p)
        w = s_add(s_scale(ps(x ** 2 + y ** 2 - 1, x0, y0, T, p), modq(1 / R0 ** 2, p)), s_const(-1, T, p))
        bino = [modq(sp.binomial(sp.Rational(1, 2), k), p) for k in range(T + 1)]
        Rs = s_scale(s_powser(w, bino), modq(R0, p))
        self.base = {x: X, y: Y, R: Rs}
        self.memo = {}
        expo = F["expo"]
        sub = {x: x0, y: y0, R: R0}
        Z0 = {E: sp.nsimplify(sp.sympify(e).xreplace(sub)) for E, e in expo.items()}
        for E, z in Z0.items():
            assert z.is_Rational, f"exponent of {E} at P is not rational: {z}"
        N = 1
        for z in Z0.values():
            N = lcm(N, int(z.q))
        self.N, self.n = N, {E: int(z * N) for E, z in Z0.items()}
        inv_fact = [modq(sp.Rational(1, factorial(k)), p) for k in range(T + 1)]
        self.Zser = {}
        for E, e in expo.items():
            Zs = self.ev(e)
            assert (Zs.a[0, 0] - modq(Z0[E], p)) % p == 0, f"series constant of Z_{E} disagrees with the exact value"
            self.Zser[E] = Zs
            Zc = s_add(Zs, s_const(-modq(Z0[E], p), T, p))
            self.base[E] = s_scale(s_powser(Zc, inv_fact), pow(t, self.n[E] % (p - 1), p))
        if sabotage_f:   # control 2 sabotage: f carries exp((Z_P - Z_P(P))/50) extra -- exponent mismatched in f only
            Zc = s_add(self.Zser[EP], s_const(-modq(Z0[EP], p), T, p))
            self.f_extra = s_powser(s_scale(Zc, modq(sp.Rational(1, 50), p)), inv_fact)
        else:
            self.f_extra = None
        self.memo = {}

    def ev(self, e):
        """Series of a sympy expression in x, y, R, E_* with rational coefficients (memoised over the shared DAG)."""
        e = sp.sympify(e)
        if e in self.memo:
            return self.memo[e]
        T, p = self.T, self.p
        if e in self.base:
            out = self.base[e]
        elif e.is_Rational:
            out = s_const(modq(e, p), T, p)
        elif e.is_Add:
            out = s_const(0, T, p)
            for a in e.args:
                out = s_add(out, self.ev(a))
        elif e.is_Mul:
            out = s_const(1, T, p)
            for a in e.args:
                out = out.mul(self.ev(a))
        elif e.is_Pow and e.exp.is_Integer:
            out = s_pow(self.ev(e.base), int(e.exp))
        else:
            raise ValueError(f"cannot expand {type(e).__name__}: {e}")
        self.memo[e] = out
        return out

    def ginv(self):
        """g^ab from (f, omega, e^{2 gamma}); order (t, x, y, phi). Formula checked against SymPy (control 1)."""
        F, T, p = self.F, self.T, self.p
        k2 = modq(F["k"] ** 2, p)
        f = self.ev(F["f"])
        if self.f_extra is not None:
            f = f.mul(self.f_extra)
        om, e2g = self.ev(F["om"]), self.ev(F["e2g"])
        X2m1 = self.ev(x ** 2 - 1); Y1m = self.ev(1 - y ** 2); X2Y2 = self.ev(x ** 2 - y ** 2)
        rho2k2 = s_scale(X2m1.mul(Y1m), k2)
        irho = rho2k2.inv()
        G = {}
        G[(0, 0)] = s_add(f.mul(om).mul(om).mul(irho), s_scale(f.inv(), -1))
        G[(0, 3)] = f.mul(om).mul(irho)
        G[(3, 3)] = f.mul(irho)
        den = s_scale(e2g.mul(X2Y2), k2).inv()
        G[(1, 1)] = f.mul(X2m1).mul(den)
        G[(2, 2)] = f.mul(Y1m).mul(den)
        return G


def ginv_formula_symbolic(F):
    """The same formula as MNSeries.ginv, in SymPy, for control 1."""
    f, om, e2g, k = F["f"], F["om"], F["e2g"], F["k"]
    rho2 = (x ** 2 - 1) * (1 - y ** 2)
    G = sp.zeros(4, 4)
    G[0, 0] = f * om ** 2 / (k ** 2 * rho2) - 1 / f
    G[0, 3] = G[3, 0] = f * om / (k ** 2 * rho2)
    G[3, 3] = f / (k ** 2 * rho2)
    G[1, 1] = f * (x ** 2 - 1) / (k ** 2 * e2g * (x ** 2 - y ** 2))
    G[2, 2] = f * (1 - y ** 2) / (k ** 2 * e2g * (x ** 2 - y ** 2))
    return G


def draw_t(seed, p):
    t = random.Random(seed).randrange(2, p - 1)
    assert t % p
    return t


# ---------------------------------------------------------------------------------------------------- Ricci from series
def ricci_series(G):
    """R_bd as series from g^ab series (x = index 1, y = index 2; no t, phi dependence). Valid to order T - 2."""
    T, p = G[(1, 1)].T, G[(1, 1)].p
    Z = s_const(0, T, p)
    gi = [[Z] * 4 for _ in range(4)]
    for (a, b), s in G.items():
        gi[a][b] = gi[b][a] = s
    gl = [[Z] * 4 for _ in range(4)]
    gl[1][1], gl[2][2] = gi[1][1].inv(), gi[2][2].inv()
    det = s_add(gi[0][0].mul(gi[3][3]), s_scale(gi[0][3].mul(gi[0][3]), -1))
    idet = det.inv()
    gl[0][0], gl[3][3] = gi[3][3].mul(idet), gi[0][0].mul(idet)
    gl[0][3] = gl[3][0] = s_scale(gi[0][3].mul(idet), -1)

    def d(s, c):
        return s.du() if c == 1 else (s.dv() if c == 2 else Z)
    dg = [[[d(gl[b][c], a) for c in range(4)] for b in range(4)] for a in range(4)]     # dg[a][b][c] = d_a g_bc
    half = pow(2, p - 2, p)
    Gam = [[[None] * 4 for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(b, 4):
                acc = Z
                for e in range(4):
                    if not gi[a][e].a.any():
                        continue
                    t_ = s_add(s_add(dg[b][e][c], dg[c][e][b]), s_scale(dg[e][b][c], -1))
                    acc = s_add(acc, gi[a][e].mul(t_))
                Gam[a][b][c] = Gam[a][c][b] = s_scale(acc, half)
    Ric = {}
    for b in range(4):
        for dd in range(b, 4):
            acc = Z
            for a in range(4):
                acc = s_add(acc, d(Gam[a][b][dd], a))
                acc = s_add(acc, s_scale(d(Gam[a][b][a], dd), -1))
                for e in range(4):
                    acc = s_add(acc, Gam[a][a][e].mul(Gam[e][b][dd]))
                    acc = s_add(acc, s_scale(Gam[a][dd][e].mul(Gam[e][b][a]), -1))
            Ric[(b, dd)] = acc
    return Ric


def ricci_max_order_zero(Ric, T):
    """Largest K such that every Ricci series coefficient of total order <= K is 0 (-1 if the constant term fails)."""
    for K in range(T - 1):
        for s in Ric.values():
            i, j = np.indices(s.a.shape)
            if (s.a[(i + j) == K] % s.p).any():
                return K - 1
    return T - 2


# ---------------------------------------------------------------------------------------------------- runs
def bound_at(spec, pt, d, M, draw, threads, engine="flint", sabotage_kerr=False):
    Mm, a, beta = TARGETS[spec]
    F = MB.mn_functions(Mm, a, beta)
    x0, y0, R0 = POINTS[pt]
    pi, seed = draw
    p = PRIMES[pi]
    t = draw_t(seed, p)
    S = MNSeries(F, x0, y0, R0, M + 2, p, t)
    G = S.ginv()
    if sabotage_kerr:
        G[(1, 1)] = G[(1, 1)].mul(S.ev(1 + x * y / 7))
    tot, parts = 0, []
    for branch in (0, 1):
        A, mons, J = KJ.build(None, d, M, x0, y0, p, branch, G=G)
        r = KJ.rank_of(A, p, engine, threads=threads)
        k = A.shape[1] - r["rank"]
        tot += k
        parts.append(f"e={branch} {A.shape[0]}x{A.shape[1]} rank {r['rank']} -> {k}")
    return tot, parts, S.N


def controls(threads):
    ok_all = True

    def check(label, ok, detail=""):
        nonlocal ok_all
        ok_all &= bool(ok)
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if detail else ""), flush=True)

    # 1. inverse-metric formula vs SymPy inverse, exact, at a rational point with random rational E values
    rnd = random.Random(7)
    for spec in ("p1", "p2"):
        Mm, a, beta = TARGETS[spec]
        F = MB.mn_functions(Mm, a, beta)
        xv, yv, Rv = MB.rational_point(rnd)
        sub = {x: xv, y: yv, R: Rv}
        for E in (EA, EB, EP, EQ):
            sub[E] = sp.Rational(rnd.randint(2, 19), rnd.randint(2, 19))
        g = MB.metric(F).applyfunc(lambda e: sp.sympify(e).xreplace(sub))
        Gf = ginv_formula_symbolic(F).applyfunc(lambda e: sp.sympify(e).xreplace(sub))
        check(f"[1] {spec}: g^ab formula == SymPy inverse of g_ab, exact", (g.inv() - Gf).applyfunc(sp.simplify) == sp.zeros(4, 4))
    # 2. Ricci from series: zero to truncation order on MN, nonzero under the exponent-mismatch sabotage
    T = 12                       # = M + 2 at rank 10: every series order the runs use is covered
    for spec in ("p1", "p2"):
        Mm, a, beta = TARGETS[spec]
        F = MB.mn_functions(Mm, a, beta)
        for pt in ("P1", "P2"):
            x0, y0, R0 = POINTS[pt]
            for pi, seed in DRAWS:
                p = PRIMES[pi]; t = draw_t(seed, p)
                S = MNSeries(F, x0, y0, R0, T, p, t)
                K = ricci_max_order_zero(ricci_series(S.ginv()), T)
                check(f"[2] {spec} {pt} draw {pi}: Ricci series = 0 to order {T - 2} (N = {S.N})", K == T - 2, f"zero to order {K}")
            p = PRIMES[0]; t = draw_t(1, p)
            Sb = MNSeries(F, x0, y0, R0, T, p, t, sabotage_f=True)
            Kb = ricci_max_order_zero(ricci_series(Sb.ginv()), T)
            check(f"[2] {spec} {pt} SABOTAGE f*exp((Z_P - Z_P(P))/50): Ricci series NONZERO", Kb < T - 2, f"zero only to order {Kb}")
        # an independent-E control in the wrong direction is NOT needed for soundness, but show the trap is real:
    # 3. Kerr limit (beta = 0) through the same code: ranks 1-4 -> 2, 5, 8, 14
    for spec in ("kerr1", "kerr2"):
        got = []
        for d, want in zip((1, 2, 3, 4), (2, 5, 8, 14)):
            b = min(bound_at(spec, "P1", d, d, dr, threads)[0] for dr in DRAWS)
            got.append(b)
        check(f"[3] {spec}: Kerr limit ranks 1-4 bounds {got} == [2, 5, 8, 14] (Carter recovered)", got == [2, 5, 8, 14])
    # 4. Kerr limit with the non-separable sabotage: Carter disappears at rank 2
    b = min(bound_at("kerr1", "P1", 2, 2, dr, threads, sabotage_kerr=True)[0] for dr in DRAWS)
    check(f"[4] kerr1 + sabotage g^xx*(1+x*y/7): rank-2 bound {b} == 4 (Carter gone)", b == 4)
    print(f"CONTROLS {'ALL PASS' if ok_all else 'FAILED'}", flush=True)
    return ok_all


def main():
    def arg(fl, dflt=None, cast=str):
        return cast(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else dflt
    threads = arg("--threads", 2, int)
    if "--controls" in sys.argv:
        return 0 if controls(threads) else 1
    spec = arg("--mn", "p1")
    lo, hi = map(int, arg("--ranks", "1-4").split("-"))
    pts = arg("--points", "P1,P2").split(",")
    for d in range(lo, hi + 1):
        M = arg("--M", d, int)
        triv = KJ.trivial_count(d)
        for pt in pts:
            t0 = time.time()
            bs = []
            for dr in DRAWS:
                b, parts, N = bound_at(spec, pt, d, M, dr, threads)
                bs.append(b)
                print(f"  MN {spec} rank {d} M={M} {pt} draw prime{dr[0]}/seed{dr[1]} (N={N}): bound {b}  [{'; '.join(parts)}]", flush=True)
            b = min(bs)
            print(f"VERDICT MN {spec} rank {d} M={M} {pt}: bound min{bs} = {b}; trivial {triv}; "
                  f"{'NO NONTRIVIAL KILLING TENSOR (bound = trivial)' if b == triv else 'bound exceeds trivial by ' + str(b - triv)}"
                  f"  [{time.time() - t0:.0f}s]", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
