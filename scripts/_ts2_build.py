#!/usr/bin/env python3
"""Tomimatsu-Sato delta = 2, built from its Ernst potential and verified vacuum -- the sealed target for the
fleet's Morales-Ramis / Kovacic tool.  (Supplier side only.)

WHAT THIS DOES AND DOES NOT DO.  It constructs the metric and checks the vacuum field equations.  It does
NOT derive a normal variational equation, pick a particular solution, or say anything about
integrability -- that is the receiving tool's job, kept independent on purpose.

CONSTRUCTION (nothing long is transcribed; every formula below is either the short standard Ernst
potential or is DERIVED here, and the whole metric is then checked against R_ab = 0):
  prolate spheroidal (x, y), x > 1, |y| < 1;  p^2 + q^2 = 1, rationalised as p = (1-t^2)/(1+t^2),
  q = 2t/(1+t^2) so every metric component is rational.
  delta = 2 Ernst potential   xi = [p^2 x^4 + q^2 y^4 - 1 - 2i p q x y (x^2 - y^2)] / [2p x (x^2-1) - 2i q y (1-y^2)]
  delta = 1 (Kerr) control     xi = p x - i q y
  E = (xi - 1)/(xi + 1),  f = Re E,  chi = Im E
  omega from the twist equations  d_x omega = s sigma (1-y^2) f^-2 d_y chi,  d_y omega = -s sigma (x^2-1) f^-2 d_x chi,
       solved by an exact polynomial ansatz omega * A = (1 - y^2) P(x, y); the sign s is chosen by consistency
  e^{2 gamma} = A / (p^{2 delta} (x^2 - y^2)^{delta^2}),  A = |N|^2 - |D|^2 (the numerator of f)
  ds^2 = -f (dt - omega dphi)^2 + f^-1 [ e^{2 gamma} sigma^2 (x^2-y^2) (dx^2/(x^2-1) + dy^2/(1-y^2))
                                           + sigma^2 (x^2-1)(1-y^2) dphi^2 ]
VERIFICATION: R_ab evaluated EXACTLY (rational arithmetic, from symbolic first/second derivatives) at random
rational points and parameter values -- a probabilistic identity test (Schwartz-Zippel), not a symbolic
proof.  Controls: Kerr through the same pipeline must be vacuum; a perturbed TS metric must NOT be.

Usage: _ts2_build.py      (light: a few minutes, well under 1 GB)
"""
import itertools
import random
import sys

import sympy as sp

x, y, t, sig = sp.symbols("x y t sigma", real=True)
T, PHI = sp.symbols("T phi", real=True)
FAILS = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if detail else ""), flush=True)
    if not ok:
        FAILS.append(label)


T_FIXED = None          # --t 1/2 fixes the spin parameter at a rational value (p = 3/5, q = 4/5 for t = 1/2)


def pq():
    tt = t if T_FIXED is None else T_FIXED
    return (1 - tt ** 2) / (1 + tt ** 2), 2 * tt / (1 + tt ** 2)


def ernst(delta):
    p, q = pq()
    if delta == 1:
        N, D = p * x - sp.I * q * y, sp.Integer(1)
    else:
        N = p ** 2 * x ** 4 + q ** 2 * y ** 4 - 1 - 2 * sp.I * p * q * x * y * (x ** 2 - y ** 2)
        D = 2 * p * x * (x ** 2 - 1) - 2 * sp.I * q * y * (1 - y ** 2)
    return N, D


def re_im(z):
    zr, zi = sp.expand(z).as_real_imag()
    return sp.together(zr), sp.together(zi)


def build(delta, perturb=0):
    p, q = pq()
    N, D = ernst(delta)
    Nr, Ni = re_im(N); Dr, Di = re_im(D)
    A = sp.expand(Nr ** 2 + Ni ** 2 - Dr ** 2 - Di ** 2)               # |N|^2 - |D|^2
    B = sp.expand((Nr + Dr) ** 2 + (Ni + Di) ** 2)                     # |N + D|^2
    f = A / B
    chi = sp.cancel(2 * (Ni * Dr - Nr * Di) / B)                       # Im[(N-D)(N+D)*]/|N+D|^2
    return p, q, A, B, f, chi


def solve_omega(A, B, f, chi, deg):
    """omega * A = (1-y^2) * sum c_ij x^i y^j (even in y); fit the twist equations EXACTLY at points."""
    cs, P = [], 0
    for i in range(deg + 1):
        for j in range(0, deg + 1, 2):
            c = sp.Symbol(f"c_{i}_{j}"); cs.append(c); P += c * x ** i * y ** j
    om = (1 - y ** 2) * P / A
    dchix, dchiy = sp.diff(chi, x), sp.diff(chi, y)
    for s in (1, -1):
        eqs = []
        rnd = random.Random(11 + s)
        e1 = sp.diff(om, x) - s * sig * (1 - y ** 2) * dchiy / f ** 2
        e2 = sp.diff(om, y) + s * sig * (x ** 2 - 1) * dchix / f ** 2
        for _ in range(len(cs) + 12):
            # t stays SYMBOLIC: the coefficients c_ij are functions of (p, q); fitting constants at random t
            # values would make the system inconsistent for the wrong reason
            pt = {x: sp.Rational(rnd.randint(11, 40), 7), y: sp.Rational(rnd.randint(-6, 6), 7), sig: 1}
            for e in (e1, e2):
                eqs.append(sp.numer(sp.together(e.subs(pt))))
        sol = sp.linsolve(eqs, cs)
        sol = list(sol)
        if sol and not any(v.free_symbols & set(cs) for v in sol[0]):
            sub = dict(zip(cs, sol[0]))
            return s, sp.cancel(om.subs(sub) * sig)                                  # omega scales with sigma
    return None, None


def metric(delta, perturb=0):
    p, q, A, B, f, chi = build(delta)
    s, om = solve_omega(A, B, f, chi, deg=3 if delta == 1 else 8)
    e2g = A / (p ** (2 * delta) * (x ** 2 - y ** 2) ** (delta ** 2))
    if perturb:
        e2g = e2g * (1 + sp.Rational(perturb, 100) * x / (x ** 2 + 1))
    rho2 = sig ** 2 * (x ** 2 - 1) * (1 - y ** 2)
    g = sp.zeros(4, 4)
    g[0, 0] = -f
    g[0, 3] = g[3, 0] = f * om
    g[3, 3] = -f * om ** 2 + rho2 / f
    g[1, 1] = e2g * sig ** 2 * (x ** 2 - y ** 2) / (f * (x ** 2 - 1))
    g[2, 2] = e2g * sig ** 2 * (x ** 2 - y ** 2) / (f * (1 - y ** 2))
    return g, dict(p=p, q=q, A=A, B=B, f=f, chi=chi, omega=om, e2g=e2g, sign=s)


def ricci_at(g, pt):
    """R_ab at one point, exactly, from symbolic d g and d^2 g (only x, y matter)."""
    X = (T, x, y, PHI)
    n = 4
    dg = {(c, a, b): sp.diff(g[a, b], X[c]) if c in (1, 2) else 0 for c in range(n) for a in range(n) for b in range(n)}
    ddg = {(c, d, a, b): sp.diff(dg[(c, a, b)], X[d]) if (c in (1, 2) and d in (1, 2)) else 0
           for c in range(n) for d in range(n) for a in range(n) for b in range(n)}
    # NO nsimplify: it is a guesser, and on unevaluated exact expressions it goes through floats and invents
    # closed forms (2**(41/117)...) -- it manufactured a fake Kerr failure here once.  Exact or loud.
    def ev(e):
        if e == 0:
            return sp.Integer(0)
        v = sp.cancel(sp.together(e.subs(pt)))
        if not v.is_Rational:
            raise ValueError(f"non-rational value at a rational point: {v}")
        return v
    G = sp.Matrix(n, n, lambda a, b: ev(g[a, b])); Gi = G.inv()
    DG = {k: ev(v) for k, v in dg.items()}; DDG = {k: ev(v) for k, v in ddg.items()}
    # Gamma^a_bc and d_d Gamma^a_bc
    Gam = [[[sum(Gi[a, e] * (DG[(b, e, c)] + DG[(c, e, b)] - DG[(e, b, c)]) for e in range(n)) / 2
             for c in range(n)] for b in range(n)] for a in range(n)]
    dGi = {d: -Gi * sp.Matrix(n, n, lambda a, b: DG[(d, a, b)]) * Gi for d in range(n)}
    dGam = {}
    for d in range(n):
        for a, b, c in itertools.product(range(n), repeat=3):
            dGam[(d, a, b, c)] = sum(dGi[d][a, e] * (DG[(b, e, c)] + DG[(c, e, b)] - DG[(e, b, c)])
                                     + Gi[a, e] * (DDG[(b, d, e, c)] + DDG[(c, d, e, b)] - DDG[(e, d, b, c)])
                                     for e in range(n)) / 2
    Ric = sp.zeros(n, n)
    for b, c in itertools.product(range(n), repeat=2):
        Ric[b, c] = sum(dGam[(a, a, b, c)] - dGam[(c, a, b, a)]
                        + sum(Gam[a][a][e] * Gam[e][b][c] - Gam[a][c][e] * Gam[e][b][a] for e in range(n))
                        for a in range(n))
    return Ric


def vacuum_test(g, label, npts=4, seed=5):
    rnd = random.Random(seed)
    worst = 0
    for _ in range(npts):
        pt = {x: sp.Rational(rnd.randint(12, 45), 8), y: sp.Rational(rnd.randint(-7, 7), 8),
              t: sp.Rational(rnd.randint(1, 9), 13), sig: sp.Rational(rnd.randint(2, 9), 3)}
        R = ricci_at(g, pt)
        worst = max(worst, max(abs(v) for v in R))
    return worst


def ernst_residual(delta, npts=4):
    N, D = ernst(delta)
    xi = N / D
    xib = xi.subs(sp.I, -sp.I)
    op = ((xi * xib - 1) * (sp.diff((x ** 2 - 1) * sp.diff(xi, x), x) + sp.diff((1 - y ** 2) * sp.diff(xi, y), y))
          - 2 * xib * ((x ** 2 - 1) * sp.diff(xi, x) ** 2 + (1 - y ** 2) * sp.diff(xi, y) ** 2))
    rnd = random.Random(3)
    vals = []
    for _ in range(npts):
        pt = {x: sp.Rational(rnd.randint(12, 45), 8), y: sp.Rational(rnd.randint(-7, 7), 8), t: sp.Rational(rnd.randint(1, 9), 13)}
        vals.append(sp.cancel(sp.together(sp.expand(op.subs(pt)))))   # exact; no nsimplify
    return vals


def main():
    print("0. the Ernst potentials satisfy the Ernst equation (exact, at random rational points)")
    for d in (1, 2):
        v = ernst_residual(d)
        check(f"delta = {d}: Ernst operator vanishes", all(w == 0 for w in v), f"{v}")

    print("\n1. CONTROL: Kerr (delta = 1) through the SAME pipeline must be vacuum")
    gK, infoK = metric(1)
    check("twist equations solved exactly for omega", infoK["sign"] is not None, f"sign s = {infoK['sign']}")
    wK = vacuum_test(gK, "Kerr")
    check("Kerr: R_ab = 0 exactly at 4 random rational points", wK == 0, f"max |R_ab| = {wK}")

    print("\n2. Tomimatsu-Sato delta = 2")
    g2, info2 = metric(2)
    check("twist equations solved exactly for omega (ansatz degree 8)", info2["sign"] is not None, f"sign s = {info2['sign']}")
    w2 = vacuum_test(g2, "TS2")
    check("TS delta=2: R_ab = 0 exactly at 4 random rational points", w2 == 0, f"max |R_ab| = {w2}")

    print("\n3. CONTROL: a perturbed TS metric must NOT be vacuum (the test can fail)")
    gP, _ = metric(2, perturb=3)
    wP = vacuum_test(gP, "TS2-perturbed", npts=1)
    check("perturbed e^{2gamma}: R_ab != 0", wP != 0, f"max |R_ab| = {sp.N(wP, 4)}")

    print("\n4. asymptotics: mass and angular momentum read off (not assumed)")
    p, q = pq()
    f, om = info2["f"], info2["omega"]
    m_over_sigma = sp.limit(sp.cancel((1 - f) * x / 2).subs({y: sp.Rational(1, 3)}), x, sp.oo)
    print(f"      m / sigma = {sp.simplify(m_over_sigma)}     (1 - f ~ 2m/(sigma x))")
    check("m = 2 sigma / p  (the delta = 2 relation sigma = m p / 2)", sp.simplify(m_over_sigma - 2 / p) == 0)
    J_lead = sp.limit(sp.cancel(om * x / (1 - y ** 2)).subs({y: sp.Rational(1, 3)}), x, sp.oo)
    Jm2 = sp.simplify(J_lead / (2 * (2 * sig / p) ** 2 / sig))       # omega ~ 2 J (1-y^2) / (sigma x)
    print(f"      omega ~ {sp.simplify(J_lead)} (1-y^2)/x  ->  J / m^2 = {Jm2}")
    check("|J| = q m^2 (sign fixed by the chart's orientation)", sp.simplify(Jm2 ** 2 - q ** 2) == 0)

    print("\n5. rational structure (what a Kovacic-based tool needs)")
    comps = [g2[0, 0], g2[0, 3], g2[3, 3], g2[1, 1], g2[2, 2]]
    rat = all(sp.cancel(c).is_rational_function(x, y, t, sig) for c in comps)
    check("every metric component is a rational function of (x, y, t, sigma)", rat)

    tag = "" if T_FIXED is None else f"_t{str(T_FIXED).replace('/', 'o')}"
    with open(f"data/sealed/TS2_for_quantum/ts2_metric_components{tag}.txt", "w") as fh:
        fh.write("# Tomimatsu-Sato delta=2, coordinates (T, x, y, phi); p=(1-t^2)/(1+t^2), q=2t/(1+t^2); srepr per component\n")
        for nm, c in (("g_TT", g2[0, 0]), ("g_Tphi", g2[0, 3]), ("g_phiphi", g2[3, 3]), ("g_xx", g2[1, 1]), ("g_yy", g2[2, 2])):
            fh.write(f"{nm} = {sp.srepr(sp.cancel(c))}\n")
        fh.write(f"omega = {sp.srepr(info2['omega'])}\n")
        fh.write(f"A = {sp.srepr(info2['A'])}\nB = {sp.srepr(info2['B'])}\n")
    print(f"\n  components written to data/sealed/TS2_for_quantum/ts2_metric_components{tag}.txt")
    print("\n" + ("PASS -- all checks" if not FAILS else f"FAIL ({len(FAILS)}): {FAILS}"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    # The exact-in-t solve is correct but slow (a 45-unknown linear system over Q(t)); a rational t makes it
    # pure rational arithmetic.  Every metric component stays rational in (x, y), which is what Kovacic needs.
    if "--t" in sys.argv:
        T_FIXED = sp.Rational(sys.argv[sys.argv.index("--t") + 1])
        print(f"spin parameter FIXED: t = {T_FIXED}  ->  p, q = {pq()}", flush=True)
    sys.exit(main())
