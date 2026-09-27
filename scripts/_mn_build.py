#!/usr/bin/env python3
"""Manko-Novikov (MN) metric package for the Morales-Ramis / Kovacic tool (fleet chain 2, K5; Bridge ask 2026-09-27).

SOURCE, stated plainly: the functions are the published MN q-anomaly subclass in the form used by Gair, Li & Mandel
(PRD 77, 024035, 2008), as already coded (in floating point) in scripts/manko_novikov.py. That is a TRANSCRIPTION, not
a derivation from the Ernst equation, so per CLAUDE.md §5 it is not trusted until it passes R_ab = 0 here, exactly.
One published constant is corrected: gamma's additive constant is fixed so e^{2 gamma} -> 1 at infinity (the vacuum
equations cannot see it; axis regularity and asymptotic flatness can, and both are checked exactly below).

EXACT TEST DESPITE NON-RATIONAL FUNCTIONS. MN contains R = sqrt(x^2 + y^2 - 1) and exponentials of algebraic
functions, so R_ab cannot be evaluated in rational arithmetic at a point. Instead every function is written in the
DIFFERENTIAL FIELD Q(x, y, R, EA, EB, EP, EQ): R and the four exponentials become symbols, and d/dx, d/dy act by the
chain rule (dR/dx = x/R, dE/dx = E * d(exponent)/dx). R_ab is then a rational function of those symbols. It is tested
at random rational points with R^2 = x^2 + y^2 - 1 enforced and the exponential symbols set to random rationals
(Schwartz-Zippel). A formal zero implies the true zero: SOUND. A formal nonzero could be spurious only if the
exponentials were algebraically dependent, and that is why gamma's exponential is expressed through EA, EB, EQ.

    .venv/bin/python scripts/_mn_build.py
"""
import itertools
import random
import sys

import mpmath as mp
import sympy as sp

x, y, R = sp.symbols("x y R", positive=True)
EA, EB, EP, EQ = sp.symbols("E_A E_B E_P E_Q", positive=True)
FAILS = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if detail else ""), flush=True)
    if not ok:
        FAILS.append(label)


def P(n, u):
    return sp.legendre(n, u)


def mn_functions(M, a, beta):
    """Return dict of the MN building blocks for rational M, a (M^2 - a^2 a square) and rational beta."""
    chi = sp.Rational(a) / M
    k = sp.sqrt(sp.Rational(M) ** 2 - sp.Rational(a) ** 2)
    alpha = (-1 + sp.sqrt(1 - chi ** 2)) / chi
    assert k.is_Rational and alpha.is_Rational, "choose M, a with M^2 - a^2 a perfect square"
    assert sp.simplify(k - M * (1 - alpha ** 2) / (1 + alpha ** 2)) == 0
    u = x * y / R
    Sa = sum((x - y) * P(l, u) / R ** (l + 1) for l in range(3))
    Sb = sum((-1) ** (3 - l) * (x + y) * P(l, u) / R ** (l + 1) for l in range(3))
    expo = {EA: 2 * beta * (Sa - 1),                                  # a = -alpha / EA
            EB: 2 * beta * (Sb + 1),                                  # b =  alpha * EB
            EP: 2 * beta * P(2, u) / R ** 3,                          # e^{2 psi}, psi = beta P2 / R^3
            EQ: 3 * beta ** 2 * (P(3, u) ** 2 - P(2, u) ** 2) / R ** 6}
    aa, bb = -alpha / EA, alpha * EB
    A = (x ** 2 - 1) * (1 + aa * bb) ** 2 - (1 - y ** 2) * (bb - aa) ** 2
    B = (x + 1 + (x - 1) * aa * bb) ** 2 + ((1 + y) * aa + (1 - y) * bb) ** 2
    C = ((x ** 2 - 1) * (1 + aa * bb) * (bb - aa - y * (aa + bb))
         + (1 - y ** 2) * (bb - aa) * (1 + aa * bb + x * (1 - aa * bb)))
    f = EP * A / B
    om = 2 * k * C / (EP * A) - 4 * k * alpha / (1 - alpha ** 2)
    # published gamma' = 1/2 ln((x^2-1)/(x^2-y^2)) + 3/2 beta^2 (P3^2-P2^2)/R^6 + beta sum_l[(x-y+(-1)^l(x+y))P_l/R^(l+1) - 2]
    # and sum_l[...] = (Sa - 1) - (Sb + 1) - 4; the -4 (i.e. e^{-8 beta}) is the constant removed for flatness.
    e2g = EQ * EA / EB * A / ((x ** 2 - y ** 2) * (1 - alpha ** 2) ** 2)
    return dict(k=k, alpha=alpha, beta=beta, f=f, om=om, e2g=e2g, A=A, B=B, C=C, expo=expo, a=aa, b=bb)


def metric(F):
    k, f, om, e2g = F["k"], F["f"], F["om"], F["e2g"]
    g = sp.zeros(4, 4)                                   # order (t, x, y, phi)
    g[0, 0] = -f
    g[0, 3] = g[3, 0] = f * om
    g[3, 3] = -f * om ** 2 + k ** 2 * (x ** 2 - 1) * (1 - y ** 2) / f
    g[1, 1] = k ** 2 * e2g * (x ** 2 - y ** 2) / (f * (x ** 2 - 1))
    g[2, 2] = k ** 2 * e2g * (x ** 2 - y ** 2) / (f * (1 - y ** 2))
    return g


def make_D(expo):
    """Chain-rule derivations on Q(x, y, R, E...)."""
    dexp = {}

    def D(F, v):
        out = sp.diff(F, v) + sp.diff(F, R) * (v / R)
        for E, ex in expo.items():
            if F.has(E):
                if (E, v) not in dexp:
                    dexp[(E, v)] = sp.diff(ex, v) + sp.diff(ex, R) * (v / R)
                out += sp.diff(F, E) * E * dexp[(E, v)]
        return out
    return D


def rational_point(rnd):
    """(x, y, R) rational with R^2 = x^2 + y^2 - 1, x > 1, |y| < 1: x -+ R from a factorisation of 1 - y^2."""
    while True:
        yv = sp.Rational(rnd.randint(-8, 8), 10)
        c = 1 - yv ** 2
        s = sp.Rational(rnd.randint(1, 9), rnd.randint(11, 30))
        xv, Rv = (s + c / s) / 2, (c / s - s) / 2
        if Rv < 0:
            Rv = -Rv
        if xv > 1 and Rv > 0 and sp.simplify(Rv ** 2 - (xv ** 2 + yv ** 2 - 1)) == 0:
            return xv, yv, Rv


def ricci_at(g, D, pts):
    """R_ab at exact points. g depends on (x, y) only (index 1, 2). Returns list of 4x4 exact matrices."""
    X = {1: x, 2: y}
    dg = {c: g.applyfunc(lambda e: D(e, X[c])) for c in (1, 2)}
    ddg = {(c, d): dg[c].applyfunc(lambda e: D(e, X[d])) for c in (1, 2) for d in (1, 2) if c <= d}
    ddg[(2, 1)] = ddg[(1, 2)]
    out = []
    for sub in pts:
        ev = lambda e: sp.sympify(e).xreplace(sub) if e != 0 else sp.Integer(0)
        G = g.applyfunc(ev)
        Gi = G.inv()
        dG = {c: (dg[c].applyfunc(ev) if c in (1, 2) else sp.zeros(4, 4)) for c in range(4)}
        ddG = {(c, d): (ddg[(c, d)].applyfunc(ev) if c in (1, 2) and d in (1, 2) else sp.zeros(4, 4))
               for c in range(4) for d in range(4)}
        dGi = {c: -Gi * dG[c] * Gi for c in range(4)}
        Gam = [[[sum(Gi[a_, e] * (dG[b][e, c] + dG[c][e, b] - dG[e][b, c]) for e in range(4)) / 2
                 for c in range(4)] for b in range(4)] for a_ in range(4)]
        dGam = [[[[sum(dGi[d][a_, e] * (dG[b][e, c] + dG[c][e, b] - dG[e][b, c])
                       + Gi[a_, e] * (ddG[(d, b)][e, c] + ddG[(d, c)][e, b] - ddG[(d, e)][b, c]) for e in range(4)) / 2
                   for c in range(4)] for b in range(4)] for a_ in range(4)] for d in range(4)]
        Ric = sp.Matrix(4, 4, lambda b, d: sp.expand(
            sum(dGam[a_][a_][b][d] - dGam[d][a_][b][a_] for a_ in range(4))
            + sum(Gam[a_][a_][e] * Gam[e][b][d] - Gam[a_][d][e] * Gam[e][b][a_] for a_ in range(4) for e in range(4))))
        out.append(Ric)
    return out


def vacuum_test(g, expo, label, npts=3, seed=11, expect_zero=True):
    D = make_D(expo)
    rnd = random.Random(seed)
    pts = []
    for _ in range(npts):
        xv, yv, Rv = rational_point(rnd)
        sub = {x: xv, y: yv, R: Rv}
        for E in (EA, EB, EP, EQ):
            sub[E] = sp.Rational(rnd.randint(2, 19), rnd.randint(2, 19))
        pts.append(sub)
    Rics = ricci_at(g, D, pts)
    nz = [max((abs(v) for v in Ric), default=0) for Ric in Rics]
    allzero = all(Ric == sp.zeros(4, 4) for Ric in Rics)
    print(f"     {label}: max|R_ab| per point = {[str(v) if v == 0 else sp.N(v, 4) for v in nz]}")
    return allzero


def kerr_prolate_exact(M, a):
    k = sp.sqrt(sp.Rational(M) ** 2 - sp.Rational(a) ** 2)
    r = k * x + M
    Sig = r ** 2 + a ** 2 * y ** 2
    Del = r ** 2 - 2 * M * r + a ** 2
    st2 = 1 - y ** 2
    g = sp.zeros(4, 4)
    g[0, 0] = -(1 - 2 * M * r / Sig)
    g[0, 3] = g[3, 0] = -2 * M * a * r * st2 / Sig
    g[1, 1] = Sig / Del * k ** 2
    g[2, 2] = Sig / st2
    g[3, 3] = (r ** 2 + a ** 2 + 2 * M * a ** 2 * r * st2 / Sig) * st2
    return g


def main():
    POINTS = [("p1", 5, 3, sp.Rational(1, 5)), ("p2", 13, 5, sp.Rational(-1, 3))]
    print("MANKO-NOVIKOV package build\n")
    for tag, M, a, beta in POINTS:
        F = mn_functions(M, a, beta)
        q = beta * F["k"] ** 3 / M ** 3
        print(f"[{tag}] M = {M}, a = {a} (chi = {sp.Rational(a, M)}), beta = {beta} -> q = beta k^3/M^3 = {q};"
              f" k = {F['k']}, alpha = {F['alpha']}")
        g = metric(F)
        # 1. vacuum, exact (formal differential field)
        check(f"[{tag}] R_ab = 0 exactly at 3 random rational points (formal test, sound)",
              vacuum_test(g, F["expo"], "MN"))
        # 2. perturbation control: e^{2 gamma} * (1 + y^2/30) must break vacuum
        Fb = dict(F); Fb["e2g"] = F["e2g"] * (1 + y ** 2 / 30)
        check(f"[{tag}] CONTROL: e^{{2 gamma}} * (1 + y^2/30) gives R_ab != 0",
              not vacuum_test(metric(Fb), F["expo"], "perturbed", npts=1))
        # 3. psi perturbed only in f: must break vacuum too (tests the exponential machinery itself)
        Fc = dict(F); Fc["f"] = F["f"] * EP ** sp.Rational(1, 50)
        check(f"[{tag}] CONTROL: f * e^{{psi/25}} (exponent mismatched) gives R_ab != 0",
              not vacuum_test(metric(Fc), F["expo"], "psi-mismatch", npts=1))
        # 4. axis regularity and asymptotic flatness, exact
        subsA = {}
        for yv in (1, -1):
            Rax = x
            ex = {E: sp.simplify(e.subs(R, Rax).subs(y, yv)) for E, e in F["expo"].items()}
            e2g_ax = F["e2g"].subs(R, Rax).subs(y, yv).subs({E: sp.exp(v) for E, v in ex.items()})
            check(f"[{tag}] e^{{2 gamma}} = 1 on the axis y = {yv} (no conical singularity)",
                  sp.simplify(e2g_ax - 1) == 0, f"{sp.simplify(e2g_ax)}")
        mp.mp.dps = 40
        xs = mp.mpf(10) ** 8
        for yv in (mp.mpf("0.3"), mp.mpf("-0.7")):
            Rv = mp.sqrt(xs ** 2 + yv ** 2 - 1)
            num = {x: xs, y: yv, R: Rv}
            vals = {E: mp.e ** sp.lambdify((x, y, R), e, "mpmath")(xs, yv, Rv) for E, e in F["expo"].items()}
            e2g_v = sp.lambdify((x, y, R, EA, EB, EP, EQ), F["e2g"], "mpmath")(xs, yv, Rv, *[vals[E] for E in (EA, EB, EP, EQ)])
            check(f"[{tag}] e^{{2 gamma}} -> 1 at infinity (x = 1e8, y = {yv})", abs(e2g_v - 1) < mp.mpf(10) ** -6,
                  mp.nstr(e2g_v, 12))
        # 5. mass and spin read off the asymptotics (numeric, high precision)
        fl = sp.lambdify((x, y, R, EA, EB, EP, EQ), F["f"], "mpmath")
        oml = sp.lambdify((x, y, R, EA, EB, EP, EQ), F["om"], "mpmath")
        xs, yv = mp.mpf(10) ** 7, mp.mpf("0.2")
        Rv = mp.sqrt(xs ** 2 + yv ** 2 - 1)
        vals = [mp.e ** sp.lambdify((x, y, R), F["expo"][E], "mpmath")(xs, yv, Rv) for E in (EA, EB, EP, EQ)]
        fv, omv = fl(xs, yv, Rv, *vals), oml(xs, yv, Rv, *vals)
        r = F["k"] * xs + M
        m_read = (1 - fv) * r / 2
        # g_tphi = f om ~ -2 J (1-y^2)/r  =>  J = -f om r / (2 (1-y^2))
        J_read = -fv * omv * r / (2 * (1 - yv ** 2))
        print(f"     asymptotics (numeric, x = 1e7): mass = {mp.nstr(m_read, 10)}, J = {mp.nstr(J_read, 10)},"
              f" J/M^2 = {mp.nstr(J_read / m_read ** 2, 10)}")
        check(f"[{tag}] asymptotic mass = M and J = a M (numeric, 1e-5)",
              abs(m_read - M) < 1e-5 * M and abs(J_read - a * M) < 1e-5 * a * M)
        print()

    # 6. Kerr limit through the SAME functions: beta = 0 must be exactly Kerr (from Boyer-Lindquist)
    print("KERR LIMIT (beta = 0) through the same code")
    for M, a in ((5, 3), (13, 5)):
        F0 = mn_functions(M, a, sp.Integer(0))
        g0 = metric(F0).subs({EA: 1, EB: 1, EP: 1, EQ: 1})
        diff = (g0 - kerr_prolate_exact(M, a)).applyfunc(sp.simplify)
        check(f"beta = 0, M = {M}, a = {a}: metric == exact Kerr (Boyer-Lindquist -> prolate), all components",
              diff == sp.zeros(4, 4))
        check(f"beta = 0, M = {M}, a = {a}: every exponent vanishes identically",
              all(sp.simplify(e) == 0 for e in F0["expo"].values()))
    # 7. rationality: the question quantum's feasibility turns on
    print("\nRATIONALITY in (x, y)")
    F = mn_functions(5, 3, sp.Rational(1, 5))
    for E, e in F["expo"].items():
        print(f"     exponent of {E}: {sp.simplify(e)}")
    ax = sp.simplify(F["expo"][EP].subs(R, x).subs(y, 1))
    eq = sp.simplify(F["expo"][EP].subs(R, sp.sqrt(x ** 2 - 1)).subs(y, 0))
    print(f"     on the axis y = 1:   2 psi = {ax}     -> e^{{2psi}} = exp({ax}): essential singularity at x = 0")
    print(f"     on the equator y = 0: 2 psi = {eq}  -> not rational (and not algebraic) in x")
    check("MN components are NOT rational in (x, y) for beta != 0: e^{2 psi} with non-constant exponent",
          sp.simplify(sp.diff(F["expo"][EP].subs(R, sp.sqrt(x ** 2 + y ** 2 - 1)), x)) != 0)
    print("\n" + ("PASS" if not FAILS else f"FAIL ({len(FAILS)}): {FAILS}"))
    return 1 if FAILS else 0


def write_components(outdir):
    """Explicit components as true functions of (x, y): R -> sqrt(x^2 + y^2 - 1), E -> exp(exponent). SymPy srepr."""
    import os
    os.makedirs(outdir, exist_ok=True)
    for tag, M, a, beta in (("p1", 5, 3, sp.Rational(1, 5)), ("p2", 13, 5, sp.Rational(-1, 3)),
                            ("KERR_p1", 5, 3, sp.Integer(0)), ("KERR_p2", 13, 5, sp.Integer(0))):
        F = mn_functions(M, a, beta)
        g = metric(F)
        rep = {E: sp.exp(e) for E, e in F["expo"].items()}
        Rx = sp.sqrt(x ** 2 + y ** 2 - 1)
        with open(os.path.join(outdir, f"mn_metric_components_{tag}.txt"), "w") as fh:
            fh.write(f"# Manko-Novikov, M = {M}, a = {a}, beta = {beta} (q = beta k^3/M^3 = {beta * F['k']**3 / M**3}),"
                     f" k = {F['k']}, alpha = {F['alpha']}\n# coordinates (t, x, y, phi); symbols x, y positive; srepr strings\n")
            for (i, j), nm in (((0, 0), "g_tt"), ((0, 3), "g_tphi"), ((3, 3), "g_phiphi"), ((1, 1), "g_xx"), ((2, 2), "g_yy")):
                e = g[i, j].xreplace(rep).xreplace({R: Rx})
                fh.write(f"{nm} = {sp.srepr(e)}\n")
        print(f"  wrote mn_metric_components_{tag}.txt")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--write":
        write_components(sys.argv[2])
        sys.exit(0)
    sys.exit(main())
