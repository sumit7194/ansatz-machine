#!/usr/bin/env python3
"""Lower-axis first-order NVE for the "invisible" twist family (data/nve/LOWER_AXIS_PREREGISTRATION.md).
Blind second implementation for the Bridge V26. c0 by its Laurent series at infinity; monodromy by power-series
continuation in |z| > 1.3; virtually-abelian test with built-in step refinement.
    .venv/bin/python scripts/_nve_lower.py gates      # rho_c and k = 0 control of the c0 series
    .venv/bin/python scripts/_nve_lower.py run        # all controls + targets
"""
import json
import os
import random
import sys
import time

import mpmath as mp
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
mp.mp.dps = 50
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "nve")
z = sp.symbols("z")
A = sp.Rational(3, 5)
RIN = mp.mpf("1.3")
KSER = 50


# ---------------------------------------------------------------------------------------------- c0 Laurent series
def radicand(k):
    D = z**2 + A**2
    cK = -2 * A / D
    cK2 = sp.diff(cK, z, 2)
    v = (z + sp.I * A) / (z - sp.I * A)
    Q = sp.together(sp.expand(v**3 + v**-3 - sp.Rational(3, 5) * (v + 1 / v) - sp.Rational(4, 5)))
    R = sp.cancel(sp.together(cK2**2 + k * Q / D**3))
    return R


def c0_laurent(k):
    """-> (C list: c0 = sum C[m] w^m, rho_c, NW). Branch: c0'' leading coefficient negative (as c_K'')."""
    R = radicand(sp.Rational(k))
    N, Dn = sp.fraction(R)
    Np, Dp = sp.Poly(sp.expand(N), z), sp.Poly(sp.expand(Dn), z)
    zeros = []
    for fac, _m in sp.sqf_list(Np)[1]:
        if fac.degree() > 0:
            zeros += [complex(r) for r in fac.nroots(n=30, maxsteps=500)]
    poles = []
    for fac, _m in sp.sqf_list(Dp)[1]:
        if fac.degree() > 0:
            poles += [complex(r) for r in fac.nroots(n=30, maxsteps=500)]
    rho = max([abs(q) for q in zeros + poles])
    NW = int(45 * mp.log(10) / mp.log(RIN / mp.mpf(rho))) + 20
    # R(1/w) = w^(dD - dN) * Nrev(w) / Drev(w)
    nc = [mp.mpf(sp.N(c, 60)) for c in reversed(Np.all_coeffs())]    # ascending powers of z
    dc = [mp.mpf(sp.N(c, 60)) for c in reversed(Dp.all_coeffs())]
    dN, dD = len(nc) - 1, len(dc) - 1
    Nrev = [nc[dN - j] for j in range(dN + 1)]                     # coefficients of w^j in w^dN N(1/w)
    Drev = [dc[dD - j] for j in range(dD + 1)]
    L = NW + 12
    Nrev += [mp.mpf(0)] * (L - len(Nrev))
    Drev += [mp.mpf(0)] * (L - len(Drev))
    S = [mp.mpf(0)] * L                                             # S = Nrev / Drev
    for j in range(L):
        S[j] = (Nrev[j] - mp.fsum(S[i] * Drev[j - i] for i in range(j))) / Drev[0]
    shift = dD - dN                                                  # R = w^shift * S(w)
    j0 = next(j for j in range(L) if abs(S[j]) > mp.mpf(10) ** (-40))
    lead = shift + j0
    if lead != 8:
        raise RuntimeError(f"radicand leading power w^{lead}, expected w^8")
    Sa = S[j0:]
    B = [mp.mpf(0)] * NW
    B[0] = -mp.sqrt(Sa[0])                                           # c0'' ~ -12a w^4 at k = 0
    for j in range(1, NW):
        B[j] = (Sa[j] - mp.fsum(B[i] * B[j - i] for i in range(1, j))) / (2 * B[0])
    C = [mp.mpf(0)] * (NW + 3)
    for jj in range(NW):
        n = jj + 4                                                   # c0'' = sum B[jj] w^(jj+4)
        C[n - 2] = B[jj] / ((n - 1) * (n - 2))
    return C, rho, NW, dict(zeros=zeros, poles=poles)


def c0_eval(C, zz, deriv=0):
    w = 1 / zz
    if deriv == 0:
        return mp.fsum(C[m] * w**m for m in range(2, len(C)) if C[m] != 0)
    return mp.fsum(-m * C[m] * w ** (m + 1) for m in range(2, len(C)) if C[m] != 0)


# ---------------------------------------------------------------------------------------------- problem data
def poly_mp(expr):
    pc = sp.Poly(sp.expand(expr), z).all_coeffs()
    return [mp.mpf(sp.N(c, 60)) for c in pc]                  # descending powers


def peval(c, x):
    v = mp.mpf(0)
    for a in c:
        v = v * x + a
    return v


def pder(c):
    n = len(c) - 1
    return [c[i] * (n - i) for i in range(n)]


class Problem:
    def __init__(self, f0, k, E2):
        n, g = sp.fraction(sp.cancel(sp.together(f0)))
        self.n, self.g = poly_mp(n), poly_mp(g)
        self.dn, self.dg = pder(self.n), pder(self.g)
        self.C, self.rho, self.NW, self.info = c0_laurent(k)
        self.E2 = mp.mpf(sp.N(E2, 60))

    def G(self, x):
        """G1 = E2 (n^2 + c0^2 g^2) - n g ; G2 = n^2 + c0^2 g^2, and derivatives."""
        n, g, dn, dg = peval(self.n, x), peval(self.g, x), peval(self.dn, x), peval(self.dg, x)
        c, dc = c0_eval(self.C, x), c0_eval(self.C, x, 1)
        G2 = n * n + c * c * g * g
        dG2 = 2 * n * dn + 2 * c * dc * g * g + 2 * c * c * g * dg
        G1 = self.E2 * G2 - n * g
        dG1 = self.E2 * dG2 - dn * g - n * dg
        return G1, dG1, G2, dG2

    def taylor(self, z0, K):
        """Taylor coefficients (in t) of G1, G2 at z0."""
        def ptay(c):
            out, cur = [], list(c)
            fact = mp.mpf(1)
            for j in range(K + 1):
                out.append(peval(cur, z0) / fact) if cur else out.append(mp.mpf(0))
                cur = pder(cur) if len(cur) > 1 else []
                fact *= (j + 1)
            return out
        n_, g_ = ptay(self.n), ptay(self.g)
        w = 1 / z0
        T = [mp.mpc(0)] * (K + 1)
        for m in range(2, len(self.C)):
            if self.C[m] == 0:
                continue
            term = self.C[m] * w**m
            for j in range(K + 1):
                T[j] += term
                term *= -(m + j) / mp.mpf(j + 1) * w
        def mul(a, b):
            return [mp.fsum(a[i] * b[j - i] for i in range(j + 1)) for j in range(K + 1)]
        nn, cg = mul(n_, n_), mul(T, g_)
        G2 = [x + y for x, y in zip(nn, mul(cg, cg))]
        ng = mul(n_, g_)
        G1 = [self.E2 * x - y for x, y in zip(G2, ng)]
        return G1, G2


def winding(fun, radius, N=6000):
    tot, prev = mp.mpf(0), None
    for j in range(N + 1):
        val = fun(radius * mp.expj(2 * mp.pi * j / N))
        if prev is not None:
            tot += mp.arg(val / prev)
        prev = val
    return int(mp.nint(tot / (2 * mp.pi)))


def find_zeros(pr, which, rmin=1.3, rmax=60):
    f = (lambda x: pr.G(x)[0]) if which == 1 else (lambda x: pr.G(x)[2])
    nexp = winding(f, mp.mpf(rmax)) - winding(f, mp.mpf(rmin))
    found = []
    for ir in range(14):
        rr = mp.mpf(rmin) * (mp.mpf(rmax) / rmin) ** (mp.mpf(ir + 0.5) / 14)
        for it in range(24):
            x = rr * mp.expj(2 * mp.pi * (it + 0.5) / 24)
            for _ in range(60):
                G1, dG1, G2, dG2 = pr.G(x)
                F, dF = (G1, dG1) if which == 1 else (G2, dG2)
                if dF == 0:
                    break
                dx = F / dF
                x = x - dx
                if abs(x) < rmin * 0.9 or abs(x) > rmax * 2:
                    break
                if abs(dx) < mp.mpf(10) ** (-40):
                    break
            if rmin < abs(x) < rmax and abs((pr.G(x)[0] if which == 1 else pr.G(x)[2])) < mp.mpf(10) ** (-35):
                if all(abs(x - y) > mp.mpf(10) ** (-20) for y in found):
                    found.append(x)
    return found, nexp


# ---------------------------------------------------------------------------------------------- monodromy
def sdiv(a, b, K):
    q = [mp.mpc(0)] * (K + 1)
    for j in range(K + 1):
        q[j] = (a[j] - mp.fsum(q[i] * b[j - i] for i in range(j))) / b[0]
    return q


def r_series(pr, z0, K):
    G1, G2 = pr.taylor(z0, K + 1)
    d1 = [(j + 1) * G1[j + 1] for j in range(K + 1)]
    d2 = [(j + 1) * G2[j + 1] for j in range(K + 1)]
    L = [x - y for x, y in zip(sdiv(d1, G1[:K + 1], K), sdiv(d2, G2[:K + 1], K))]
    return [mp.mpf(-3) / 16 * mp.fsum(L[i] * L[j - i] for i in range(j + 1)) for j in range(K + 1)]


def step(pr, z0, h, Y, K=KSER):
    r = r_series(pr, z0, K)
    out = [[None, None], [None, None]]
    for col in range(2):
        a = [Y[0][col], Y[1][col]] + [mp.mpc(0)] * (K + 1)
        for kk in range(K - 1):
            a[kk + 2] = mp.fsum(r[j] * a[kk - j] for j in range(kk + 1)) / ((kk + 1) * (kk + 2))
        out[0][col] = mp.fsum(a[kk] * h**kk for kk in range(K + 1))
        out[1][col] = mp.fsum(kk * a[kk] * h ** (kk - 1) for kk in range(1, K + 1))
    return out


class Walker:
    def __init__(self, pr, sing, STEP):
        self.pr, self.sing, self.STEP = pr, sing, mp.mpf(STEP)

    def hmax(self, w):
        d = min([abs(w - c) for c in self.sing] + [abs(w) - mp.mpf(self.pr.rho)])
        return self.STEP * d

    def walk(self, path, Y):
        for A_, B_ in zip(path[:-1], path[1:]):
            w = A_
            while abs(B_ - w) > mp.mpf(10) ** (-30):
                hm = self.hmax(w)
                sg = B_ - w
                h = sg if abs(sg) <= hm else sg / abs(sg) * hm
                Y = step(self.pr, w, h, Y)
                w = w + h
        return Y


def arc(R, t0, t1, dmax=mp.pi / 36):
    n = max(1, int(abs(t1 - t0) / dmax) + 1)
    return [R * mp.expj(t0 + (t1 - t0) * j / n) for j in range(n + 1)]


def clear_path(path, sing, skip, margin):
    for A_, B_ in zip(path[:-1], path[1:]):
        for c in sing:
            if skip is not None and c is skip:
                continue
            ab = B_ - A_
            t = max(0, min(1, float(mp.re((c - A_) * mp.conj(ab)) / (abs(ab) ** 2 + mp.mpf(10) ** -60))))
            if abs(A_ + t * ab - c) < margin:
                return False
    return True


def loops(sing, Rb=mp.mpf(40), rin=mp.mpf("1.35")):
    out = []
    for c in sing:
        others = [d for d in sing if d is not c]
        rho = min([mp.mpf("0.35") * abs(c - d) for d in others] + [mp.mpf("0.5") * (abs(c) - mp.mpf("1.3"))])
        th = mp.arg(c) % (2 * mp.pi)
        made = None
        for dlt in (0, 0.05, -0.05, 0.1, -0.1, 0.2, -0.2, 0.35, -0.35):
            th2 = th + dlt
            e_r = abs(c) + rho
            tail = arc(Rb, mp.mpf(0), th2) + [e_r * mp.expj(th2)] + (arc(e_r, th2, th)[1:] if dlt else [])
            circ = [c + rho * mp.expj(th + 2 * mp.pi * j / 24) for j in range(25)]
            path = tail + circ[1:] + list(reversed(tail))[1:]
            if clear_path(tail, sing, c, mp.mpf("0.6") * rho if others else 0) and \
               clear_path(tail, others, None, min([mp.mpf("0.3") * abs(c - d) for d in others] + [1])):
                made = path
                break
        if made is None:
            raise RuntimeError(f"no clear loop for {c}")
        out.append(("pt", c, th, made))
    best = max((mp.mpf(j) * 2 * mp.pi / 72 for j in range(72)),
               key=lambda t: min([abs(mp.expj(t) * abs(c) - c) for c in sing] + [99]))
    tail = arc(Rb, mp.mpf(0), best) + [rin * mp.expj(best)]
    circ = arc(rin, best, best + 2 * mp.pi, mp.pi / 64)
    out.append(("inner", None, best, tail + circ[1:] + list(reversed(tail))[1:]))
    return out


def gates():
    out = {}
    for k in (0, sp.Rational(1, 100), sp.Rational(1, 30), sp.Rational(1, 10)):
        C, rho, NW, info = c0_laurent(k)
        rec = dict(k=str(k), rho_c=rho, NW=NW, rho_ok=rho <= 1.2,
                   R_zeros_max=max([abs(q) for q in info["zeros"]], default=0))
        if k == 0:
            err = max(abs(c0_eval(C, mp.mpf(1.5) * mp.expj(2 * mp.pi * j / 17)) -
                          (-2 * mp.mpf(A.p) / A.q) / ((mp.mpf(1.5) * mp.expj(2 * mp.pi * j / 17)) ** 2 + (mp.mpf(A.p) / A.q) ** 2))
                      for j in range(17))
            rec["k0_vs_cK"] = float(err)
            rec["k0_ok"] = err < 1e-30
        out[str(k)] = rec
        print(rec, flush=True)
    return out


# ---------------------------------------------------------------------------------------------- statistic, runs
from _nve_monodromy import comm, dist_I, inv, mul, nrm  # noqa: E402


def statistic(gens):
    g0 = gens[0]
    tr0 = g0[0][0] + g0[1][1]
    det0 = g0[0][0] * g0[1][1] - g0[0][1] * g0[1][0]
    red = False
    for sg in (1, -1):
        l_ = (tr0 + sg * mp.sqrt(tr0**2 - 4 * det0)) / 2
        v = [g0[0][1], l_ - g0[0][0]] if abs(g0[0][1]) > mp.mpf(10) ** -30 else [l_ - g0[1][1], g0[1][0]]
        nv = mp.sqrt(abs(v[0]) ** 2 + abs(v[1]) ** 2)
        if nv < mp.mpf(10) ** -30:
            continue
        v = [v[0] / nv, v[1] / nv]
        if all(abs((g[0][0] * v[0] + g[0][1] * v[1]) * v[1] - (g[1][0] * v[0] + g[1][1] * v[1]) * v[0]) / (1 + nrm(g))
               <= mp.mpf(10) ** -15 for g in gens):
            red = True
    if red:
        S = max(dist_I(comm(gens[i], gens[j])) / (1 + nrm(gens[i]) ** 2 * nrm(gens[j]) ** 2)
                for i in range(len(gens)) for j in range(i + 1, len(gens)))
    else:
        Cs = [comm(gens[i], gens[j]) for i in range(len(gens)) for j in range(i + 1, len(gens))]
        Cs += [mul(mul(g, C), inv(g)) for g in gens for C in list(Cs)]
        S = max([dist_I(comm(Cs[a], Cs[b])) / (1 + nrm(Cs[a]) ** 2 * nrm(Cs[b]) ** 2)
                 for a in range(len(Cs)) for b in range(a + 1, len(Cs))] + [mp.mpf(0)])
    random.seed(11)
    trs = []
    for _ in range(200):
        W = [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]]
        for _ in range(random.randint(2, 8)):
            g = random.choice(gens)
            W = mul(W, g if random.random() < 0.5 else inv(g))
        trs.append(W[0][0] + W[1][1])
    finite = all(abs(mp.im(t)) < 1e-15 and abs(mp.re(t)) <= 2 + 1e-15 for t in trs)
    return S, red, finite


def monodromy(pr, sing, ms, STEP):
    W = Walker(pr, sing, STEP)
    Ls = loops(sing)
    gens, gates = [], dict(det=0.0, eig=0.0)
    for kind, c, th, path in Ls:
        Y = W.walk(path, [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]])
        gens.append(Y)
        det = Y[0][0] * Y[1][1] - Y[0][1] * Y[1][0]
        gates["det"] = max(gates["det"], float(abs(det - 1)))
        if kind == "pt":
            ex = [mp.expj(2 * mp.pi * q) for q in (mp.mpf(1) / 4, mp.mpf(3) / 4)]
            tr = Y[0][0] + Y[1][1]
            ev = [(tr + sg * mp.sqrt(tr**2 - 4 * det)) / 2 for sg in (1, -1)]
            mis = min(max(abs(ev[0] - ex[0]), abs(ev[1] - ex[1])), max(abs(ev[0] - ex[1]), abs(ev[1] - ex[0])))
            gates["eig"] = max(gates["eig"], float(mis))
    order = sorted(range(len(Ls)), key=lambda i: float(Ls[i][2]))
    prods = []
    for seq in (order, order[::-1]):
        Mp = [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]]
        for i in seq:
            Mp = mul(Mp, gens[i])
        prods.append(float(dist_I(Mp) / (1 + nrm(Mp))))
    gates["prod_inf"] = min(prods)
    gates["pass"] = gates["det"] <= 1e-20 and gates["eig"] <= 1e-15 and gates["prod_inf"] <= 1e-15
    S, red, finite = statistic(gens)
    return dict(gates=gates, S=float(S), reducible=red, finite=finite,
                inner_trace=str(complex(gens[-1][0][0] + gens[-1][1][1])))


def run_case(name, f0, k, E):
    t0 = time.time()
    pr = Problem(f0, k, E**2)
    z1, n1 = find_zeros(pr, 1)
    z2, n2 = find_zeros(pr, 2)
    count_ok = (len(z1) == n1 and len(z2) == n2)
    sing = z1 + z2
    ms = [1] * len(z1) + [-1] * len(z2)
    runs = {}
    for st in ("0.35", "0.2"):
        runs[st] = monodromy(pr, sing, ms, st)
    S1, S2 = runs["0.35"]["S"], runs["0.2"]["S"]
    if runs["0.2"]["finite"] or S2 < 1e-30 or (S1 > 0 and S2 < 1e-6 * S1):
        cls = "VA"
    elif S2 > 1e-12 and abs(S1 - S2) / S2 < 1e-3:
        cls = "NON-VA"
    else:
        cls = "UNDETERMINED"
    gates_ok = count_ok and runs["0.35"]["gates"]["pass"] and runs["0.2"]["gates"]["pass"] and pr.rho <= 1.2
    return dict(case=name, k=str(k), E=str(E), rho_c=pr.rho, zeros_P=[str(complex(x)) for x in z1],
                poles_P=[str(complex(x)) for x in z2], count=dict(G1=(len(z1), n1), G2=(len(z2), n2)),
                count_ok=count_ok, runs=runs, cls=cls, gates_ok=gates_ok, sec=time.time() - t0)


def main():
    a = A
    fK = 1 - 1 / (z - sp.I * a) - 1 / (z + sp.I * a)
    fA3 = 1 - 1 / (z - 1) - 1 / (z + 2) - 1 / (z - 3)
    R_ = sp.Rational
    cases = [("C-K", fK, 0, R_(7, 10)), ("C-K", fK, 0, R_(4, 5)), ("C-K", fK, 0, R_(9, 10)),
             ("C-NV", fA3, 0, R_(4, 5))]
    cases += [("T", fK, k, E) for k in (R_(1, 100), R_(1, 30), R_(1, 10)) for E in (R_(7, 10), R_(4, 5), R_(9, 10))]
    res = []
    ck = os.path.join(OUT, "lower_results.jsonl")
    done = {}
    if os.path.exists(ck):
        for line in open(ck):
            r = json.loads(line)
            done[(r["case"], r["k"], r["E"])] = r
    for name, f0, k, E in cases:
        key = (name, str(k), str(E))
        if key in done:
            r = done[key]
        else:
            r = run_case(name, f0, k, E)
            with open(ck, "a") as fh:
                fh.write(json.dumps(r, default=str) + "\n")
        res.append(r)
        print(f"{name} k={k} E={E}: rho_c {r['rho_c']:.3f}; points P0 {r['count']['G1']} Pinf {r['count']['G2']}; "
              f"S(0.35)={r['runs']['0.35']['S']:.3e} S(0.2)={r['runs']['0.2']['S']:.3e}; red {r['runs']['0.2']['reducible']} "
              f"fin {r['runs']['0.2']['finite']}; gates {'PASS' if r['gates_ok'] else 'FAIL'} "
              f"{r['runs']['0.2']['gates']} -> {r['cls']} [{r['sec']:.0f}s]", flush=True)
    ctrl_ok = all(r["cls"] == "VA" for r in res if r["case"] == "C-K") and \
        all(r["cls"] == "NON-VA" for r in res if r["case"] == "C-NV") and all(r["gates_ok"] for r in res)
    tg = [r["cls"] for r in res if r["case"] == "T"]
    if not ctrl_ok:
        verdict = "VOID"
    elif all(c == "NON-VA" for c in tg):
        verdict = "OBSTRUCTED"
    elif all(c == "VA" for c in tg):
        verdict = "NOT OBSTRUCTED"
    else:
        verdict = "MIXED"
    json.dump(dict(results=res, verdict=verdict), open(os.path.join(OUT, "lower_results.json"), "w"), indent=1,
              default=str)
    print("VERDICT:", verdict, flush=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == "gates":
        o = gates()
        json.dump(o, open(os.path.join(OUT, "lower_gates.json"), "w"), indent=1, default=str)
    if sys.argv[1] == "run":
        from _ts_edge2 import fleet_guard
        g = fleet_guard()
        if g:
            raise SystemExit(f"NOT STARTED: {g}")
        main()
