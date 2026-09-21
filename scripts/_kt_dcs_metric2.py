#!/usr/bin/env python3
"""dCS step 4b: the O(zeta chi^2) EVEN-PARITY metric correction -- the order Carter dies at.

THE LEFT-HAND SIDE IS NOT JUST L[h2], and getting that wrong would be invisible. At O(zeta chi^2)
the Einstein tensor picks up, besides the linearised operator acting on the new even correction,
CROSS TERMS between the O(zeta chi) correction of step 3 and the O(chi) Lense-Thirring background --
both odd, so their product is even and lands exactly here. Dropping them yields a wrong metric that
still looks plausible and that no downstream control would catch (the §124 failure mode). So the LHS
is built from the FULL metric with both zeta and chi truncated, never assembled piecewise.

CONTROL FIRST, PHYSICS SECOND. Before any dCS source is used, the same machinery is asked a question
whose answer is known: Kerr truncated at O(chi^2) must satisfy the VACUUM equations to that order.
That validates the truncated curvature, the perturbative inverse and the order extraction together,
on an object that can fail -- unlike "the correction vanishes when the coupling vanishes".

Repro:  .venv/bin/python scripts/_kt_dcs_metric2.py [--control-only]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from _kt_dcs_order2 import M, X, chi, christoffel, pinv, r, ricci_dd, riemann_uddd, th, tr  # noqa: E402

zeta = sp.Symbol("zeta")
f = 1 - 2 * M / r
s2 = sp.sin(th) ** 2
P2 = (3 * sp.cos(th) ** 2 - 1) / 2


def kerr_chi2():
    """Kerr in Boyer-Lindquist with a = M chi, series-truncated at chi^2."""
    a = M * chi
    Sig = r**2 + a**2 * sp.cos(th) ** 2
    Dl = r**2 - 2 * M * r + a**2
    g = sp.zeros(4, 4)
    g[0, 0] = -(1 - 2 * M * r / Sig)
    g[0, 3] = g[3, 0] = -2 * M * a * r * s2 / Sig
    g[1, 1] = Sig / Dl
    g[2, 2] = Sig
    g[3, 3] = (r**2 + a**2 + 2 * M * a**2 * r * s2 / Sig) * s2
    return sp.Matrix(4, 4, lambda i, j: sp.expand(
        sp.series(sp.together(g[i, j]), chi, 0, 3).removeO()) if g[i, j] != 0 else sp.S.Zero)


def einstein_trunc(g, g0, gi0, label=""):
    """G_ab of a metric, truncated at every step."""
    gi = pinv(g, g0, gi0)
    Gam = christoffel(g, gi)
    Ric = ricci_dd(riemann_uddd(Gam))
    Rs = tr(sp.expand(sum(gi[A, B] * Ric[A, B] for A in range(4) for B in range(4))))
    G = sp.Matrix(4, 4, lambda A, B: tr(sp.expand(Ric[A, B] - g[A, B] * Rs / 2)))
    return G


def chi_coeff(e, n):
    """The chi^n coefficient, WITHOUT sp.simplify."""
    return sp.cancel(sp.together(sp.diff(sp.expand(e), chi, n).subs(chi, 0) / sp.factorial(n)))


# Random exact-rational sample points; cos(th) rational so nothing is coerced (the trap that
# produced garbage in the Pontryagin spot-check).
_PTS = [(sp.Integer(1), sp.Rational(7, 2), sp.Rational(1, 3)),
        (sp.Integer(1), sp.Rational(5), sp.Rational(-2, 5)),
        (sp.Integer(1), sp.Rational(11, 4), sp.Rational(3, 4)),
        (sp.Integer(1), sp.Rational(13, 5), sp.Rational(-4, 9))]


def is_zero(e, pts=_PTS):
    """Zero test by high-precision evaluation at several random points, not by sp.simplify.

    WHY. Profiling the vacuum control: the whole curvature chain (perturbative inverse, Christoffel,
    Riemann, Ricci, Ricci scalar, G) costs 136 s, and then sp.simplify on the extracted coefficients
    ran past 8 MINUTES and was still going -- it was 97% of the job and it was answering a question
    nobody asked. A simplified FORM is not needed; only the verdict zero / nonzero is.

    A nonzero rational function of (r, cos th) cannot vanish at four random rational points except
    by coincidence, and a NONZERO reading is exact and immediate. The residual risk is one-sided and
    tiny: a false "zero". Anything reported zero here that matters is re-checked symbolically."""
    if e == 0:
        return True
    for Mv, rv, cv in pts:
        v = sp.N(e.subs({M: Mv, r: rv, th: sp.acos(cv)}), 40)
        if abs(v) > sp.Float("1e-30"):
            return False
    return True


if __name__ == "__main__":
    t0 = time.time()
    g0 = sp.diag(-f, 1 / f, r**2, r**2 * s2)
    gi0 = sp.diag(-1 / f, f, 1 / r**2, 1 / (r**2 * s2))

    print("CONTROL: Kerr truncated at O(chi^2) must be vacuum to that order\n", flush=True)
    gK = kerr_chi2()
    G = einstein_trunc(gK, g0, gi0)
    bad = []
    for i in range(4):
        for j in range(i, 4):
            for n in (0, 1, 2):
                c = chi_coeff(G[i, j], n)
                if not is_zero(c):
                    bad.append((i, j, n, c))
    if bad:
        print(f"  FAIL: G is nonzero at {[(i, j, n) for i, j, n, _ in bad]}", flush=True)
        for i, j, n, c in bad[:4]:
            print(f"    G[{i},{j}] at chi^{n} = {c}", flush=True)
        raise SystemExit(1)
    print(f"  PASS: every component of G vanishes at chi^0, chi^1 and chi^2 "
          f"[{time.time()-t0:.0f}s]", flush=True)
    print("        (truncated curvature, perturbative inverse and order extraction all validated)\n",
          flush=True)
    if "--control-only" in sys.argv:
        raise SystemExit(0)


# ---------------------------------------------------------------- the solve
NZ = 1                                      # keep to O(zeta^NZ)


def tr2(e):
    """Truncate in BOTH zeta (<= NZ) and chi (<= 2). The LHS needs both: the O(zeta chi^2) part of G
    contains cross terms between the O(zeta chi) correction and the O(chi) background, and those are
    only visible if zeta and chi are carried together and cut together."""
    e = sp.expand(e)
    out = []
    for q in sp.Add.make_args(e):
        try:
            if sp.degree(q, chi) <= 2 and sp.degree(q, zeta) <= NZ:
                out.append(q)
        except (sp.PolynomialError, TypeError, NotImplementedError):
            tr2.fallbacks += 1
            out.append(sp.expand(sp.series(sp.series(q, chi, 0, 3).removeO(), zeta, 0, NZ + 1).removeO()))
    return sp.Add(*out)


tr2.fallbacks = 0


def even_ansatz():
    """The unknown O(zeta chi^2) even-parity correction, as generic functions of r.

    l = 0 and l = 2 in every even slot, INCLUDING r-theta: the O(zeta chi^2) source has a nonzero
    r-theta component (step 4a), so a gauge that sets h_rth = 0 is not obviously available and
    imposing it would be an unstated assumption. Gauge freedom, if present, will appear as free
    parameters in the solution rather than being assumed away."""
    fs = {n: sp.Function(n)(r) for n in ("a0", "a2", "b0", "b2", "c0", "c2", "d0", "d2", "e2")}
    h = sp.zeros(4, 4)
    h[0, 0] = fs["a0"] + fs["a2"] * P2
    h[1, 1] = fs["b0"] + fs["b2"] * P2
    h[2, 2] = fs["c0"] + fs["c2"] * P2
    h[3, 3] = (fs["d0"] + fs["d2"] * P2) * s2
    h[1, 2] = h[2, 1] = fs["e2"] * sp.sin(th) * sp.cos(th)
    return h, fs


def build_lhs(verbose=True):
    """The O(zeta chi^2) part of G_ab for  g = Kerr(chi^2) + zeta[ chi*h1 + chi^2*h2 ].

    h1 is step 3's derived O(zeta chi) correction, carried EXPLICITLY rather than dropped: its cross
    terms with the O(chi) Lense-Thirring background are even and land at exactly this order."""
    g0 = sp.diag(-f, 1 / f, r**2, r**2 * s2)
    gi0 = sp.diag(-1 / f, f, 1 / r**2, 1 / (r**2 * s2))
    H1 = -M / r**4 * (1 + sp.Rational(12, 7) * M / r + sp.Rational(27, 10) * M**2 / r**2)
    h2, fs = even_ansatz()
    g = kerr_chi2()
    g[0, 3] = g[3, 0] = g[0, 3] + zeta * chi * H1 * s2
    for i in range(4):
        for j in range(4):
            if h2[i, j] != 0:
                g[i, j] = g[i, j] + zeta * chi**2 * h2[i, j]
    g = sp.Matrix(4, 4, lambda i, j: tr2(g[i, j]))
    if verbose:
        print("  metric assembled (Kerr chi^2 + zeta chi h1 + zeta chi^2 h2)", flush=True)

    dg = sp.Matrix(4, 4, lambda i, j: sp.expand(g[i, j] - g0[i, j]))
    A = gi0 * dg
    gi = gi0
    term = sp.eye(4)
    for _ in range(4):
        term = -A * term
        gi = gi + term * gi0
    gi = sp.Matrix(4, 4, lambda i, j: tr2(sp.expand(gi[i, j])))
    chk = sp.Matrix(4, 4, lambda i, j: tr2(sp.expand(sum(gi[i, k] * g[k, j] for k in range(4)))))
    for i in range(4):
        for j in range(4):
            if sp.simplify(chk[i, j] - (1 if i == j else 0)) != 0:
                raise ValueError(f"perturbative inverse wrong at ({i},{j})")
    if verbose:
        print("  perturbative inverse verified to O(zeta chi^2)", flush=True)

    Gam = [[[tr2(sp.expand(sum(gi[a_, d] * (sp.diff(g[d, c], X[b_]) + sp.diff(g[d, b_], X[c])
                                            - sp.diff(g[b_, c], X[d])) for d in range(4)) / 2))
             for c in range(4)] for b_ in range(4)] for a_ in range(4)]
    if verbose:
        print("  christoffel done", flush=True)

    def ric(b_, d):
        e = sum(sp.diff(Gam[a_][b_][d], X[a_]) - sp.diff(Gam[a_][b_][a_], X[d]) for a_ in range(4))
        e += sum(Gam[a_][a_][c] * Gam[c][b_][d] - Gam[a_][d][c] * Gam[c][b_][a_]
                 for a_ in range(4) for c in range(4))
        return tr2(sp.expand(e))

    Ric = sp.Matrix(4, 4, lambda i, j: ric(i, j) if i <= j else 0)
    Ric = sp.Matrix(4, 4, lambda i, j: Ric[i, j] if i <= j else Ric[j, i])
    if verbose:
        print("  ricci done", flush=True)
    Rs = tr2(sp.expand(sum(gi[a_, b_] * Ric[a_, b_] for a_ in range(4) for b_ in range(4))))
    G = sp.Matrix(4, 4, lambda i, j: tr2(sp.expand(Ric[i, j] - g[i, j] * Rs / 2)))
    if verbose:
        print("  G assembled", flush=True)
    out = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(
        sp.diff(sp.expand(G[i, j]), zeta, chi, chi).subs({zeta: 0, chi: 0}) / 2)))
    return out, fs


if __name__ == "__main__" and "--control-only" not in sys.argv:
    t1 = time.time()
    print("\nLHS: the O(zeta chi^2) Einstein tensor with generic even-parity unknowns\n", flush=True)
    L, fs = build_lhs()
    print(f"\n  built [{time.time()-t1:.0f}s]; nonzero components:", flush=True)
    for i in range(4):
        for j in range(i, 4):
            if L[i, j] != 0:
                print(f"    ({i},{j})  {len(sp.Add.make_args(sp.expand(L[i, j])))} terms", flush=True)
    print(f"\n  truncation fallbacks: {tr2.fallbacks}")
