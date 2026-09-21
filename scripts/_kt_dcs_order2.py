#!/usr/bin/env python3
"""dCS step 4a: the O(zeta chi^2) SOURCE -- where the Carter obstruction comes from.

WHY THIS ORDER AND NOT EARLIER. O(zeta chi) is odd-parity (g_t phi) and leaves the black hole Petrov
type D, which still admits a Carter-like tensor; Owen-Yunes-Witek find the rank-2 tensor survives
there. The obstruction appears at O(zeta chi^2), in the EVEN-parity sector. That is the order this
whole build exists to reach.

WHAT ENTERS, and the order counting that keeps it finite:
  T_ab = grad_a th grad_b th - (1/2) g_ab (grad th)^2, with th = O(chi): its O(chi^2) part needs only
      the SCHWARZSCHILD background.
  C_ab is LINEAR in theta, so with th = chi*th1 and g = g0 + chi*g1 + ..., the O(chi^2) part of C is
      the chi-derivative of C[g(chi), th1] at chi = 0 -- the background to O(chi) suffices, and the
      O(chi^2) piece of Kerr never enters the source.
  The O(zeta chi) correction h1 cannot contribute: C is linear in theta, so C[g0 + zeta*chi*h1, th]
      would be O(zeta^2 chi^2).

TRUNCATE AT EVERY STEP. Building exact curvature with chi symbolic and expanding afterwards is what
stalled twice in this build; gr_engine's eager per-Christoffel simplify dominates. Everything below
carries its own truncated Christoffel/Riemann/Ricci, following scripts/_kt_chi2_stage12.py.

CONTROLS. (1) The source must be even under (t,phi) -> (-t,-phi): only tt, rr, thth, phph and no
t-phi piece at this order. (2) Its angular content must be l = 0 and l = 2 ONLY -- a slow-rotation
expansion at quadratic order cannot produce l = 4. Both are checked, and both can fail.

Repro:  .venv/bin/python scripts/_kt_dcs_order2.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

t, ph = sp.symbols("t phi", real=True)
r, th = sp.symbols("r theta", positive=True)
chi = sp.Symbol("chi")
M = sp.Symbol("M", positive=True)
X = [t, r, th, ph]
NORD = 2                                   # keep to O(chi^NORD)


def tr(e):
    """Drop every term beyond O(chi^NORD).

    Defensive: sp.degree raises on a term that is not polynomial in chi (chi under a sqrt, or in a
    denominator). That happened once here -- levi_up built sqrt(-det g) exactly -- and the failure
    was a crash rather than a wrong answer only by luck. Such a term is now series-expanded instead,
    and counted, so a silent non-polynomial creeping in is visible rather than invisible."""
    e = sp.expand(e)
    out = []
    for q in sp.Add.make_args(e):
        try:
            if sp.degree(q, chi) <= NORD:
                out.append(q)
        except (sp.PolynomialError, TypeError, NotImplementedError):
            tr.fallbacks += 1
            out.append(sp.expand(sp.series(q, chi, 0, NORD + 1).removeO()))
    return sp.Add(*out)


tr.fallbacks = 0


def pinv(g, g0, gi0):
    """Perturbative inverse, Neumann series truncated in chi, then CHECKED against g."""
    dg = sp.Matrix(4, 4, lambda i, j: sp.expand(g[i, j] - g0[i, j]))
    A = gi0 * dg
    gi = gi0 - A * gi0 + A * A * gi0 - A * A * A * gi0
    gi = sp.Matrix(4, 4, lambda i, j: tr(sp.expand(gi[i, j])))
    chk = sp.Matrix(4, 4, lambda i, j: tr(sp.expand(sum(gi[i, k] * g[k, j] for k in range(4)))))
    for i in range(4):
        for j in range(4):
            if sp.simplify(chk[i, j] - (1 if i == j else 0)) != 0:
                raise ValueError(f"perturbative inverse wrong at ({i},{j})")
    return gi


def christoffel(g, gi):
    return [[[tr(sp.expand(sum(gi[A, d] * (sp.diff(g[d, c], X[b]) + sp.diff(g[d, b], X[c])
                                           - sp.diff(g[b, c], X[d])) for d in range(4)) / 2))
              for c in range(4)] for b in range(4)] for A in range(4)]


def riemann_uddd(Gam):
    """R^a_{bcd}, truncated."""
    R = [[[[sp.S.Zero] * 4 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for A in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(c + 1, 4):
                    e = tr(sp.expand(sp.diff(Gam[A][d][b], X[c]) - sp.diff(Gam[A][c][b], X[d])
                                     + sum(Gam[A][c][k] * Gam[k][d][b]
                                           - Gam[A][d][k] * Gam[k][c][b] for k in range(4))))
                    R[A][b][c][d] = e
                    R[A][b][d][c] = -e
    return R


def ricci_dd(R):
    return sp.Matrix(4, 4, lambda b, d: tr(sp.expand(sum(R[A][b][A][d] for A in range(4)))))


def levi_up(g):
    """eps^{abcd} = sign / sqrt(-g), with 1/sqrt(-g) EXPANDED IN chi.

    Building sqrt(-det g) exactly puts chi inside a radical, which is not polynomial in chi -- so the
    truncation could not classify the term at all and the build crashed. Write -det = D0 (1 + u) with
    D0 the chi = 0 value and u = O(chi^2); then 1/sqrt(-det) = (1/sqrt(-D0))(1 - u/2 + 3u^2/8 - ...),
    truncated like everything else. For this background -det = r^4 sin^2(th) + 4 M^4 chi^2 sin^4(th)/f."""
    det = sp.cancel(sp.together(g.det()))
    D0 = sp.simplify(det.subs(chi, 0))
    u = tr(sp.expand(sp.cancel(sp.together(det / D0 - 1))))
    root0 = sp.sqrt(sp.simplify(-D0)).replace(sp.Abs, lambda z: z)
    inv_root = sp.cancel(1 / root0) * tr(sp.expand(1 - u / 2 + 3 * u**2 / 8))
    inv_root = tr(sp.expand(inv_root))
    from _kt_dcs import EPS4
    E = [[[[sp.S.Zero] * 4 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for p_, s_ in EPS4.items():
        A, b, c, d = p_
        E[A][b][c][d] = sp.Integer(s_) * inv_root
    return E


def legendre_split(e):
    """Write an expression in cos(th) as c0 + c2 P2(cos th) + remainder; return (c0, c2, rest)."""
    u = sp.Symbol("u")
    ex = sp.expand(sp.simplify(e.rewrite(sp.cos).subs(sp.sin(th) ** 2, 1 - sp.cos(th) ** 2)))
    ex = sp.expand(ex.subs(sp.cos(th), u))
    if not ex.is_polynomial(u):
        return None, None, ex
    p = sp.Poly(ex, u)
    if p.degree() > 2:
        return None, None, ex
    c = {k: p.coeff_monomial(u**k) for k in range(3)}
    c2 = sp.simplify(2 * c[2] / 3)                      # P2 = (3u^2 - 1)/2
    c0 = sp.simplify(c[0] + c[2] / 3)
    rest = sp.simplify(ex - (c0 + c2 * (3 * u**2 - 1) / 2))
    return c0, sp.simplify(c[1]), sp.simplify(rest) if rest != 0 else sp.S.Zero


def build_source(verbose=True):
    """The O(zeta chi^2) source: the chi^2 coefficient of  c1*C_ab + c2*T_ab."""
    f = 1 - 2 * M / r
    s2 = sp.sin(th) ** 2
    g0 = sp.diag(-f, 1 / f, r**2, r**2 * s2)
    gi0 = sp.diag(-1 / f, f, 1 / r**2, 1 / (r**2 * s2))
    # background to O(chi): Schwarzschild + Lense-Thirring with a = M chi
    g = g0.copy()
    g[0, 3] = g[3, 0] = -2 * M**2 * chi * s2 / r
    gi = pinv(g, g0, gi0)
    if verbose:
        print("  perturbative inverse verified", flush=True)

    theta1 = sp.cos(th) / r**2 * (1 + 2 * M / r + sp.Rational(18, 5) * M**2 / r**2)
    theta = chi * theta1                                   # the dipole is O(chi)

    Gam = christoffel(g, gi)
    Riem = riemann_uddd(Gam)
    Ric = ricci_dd(Riem)
    if verbose:
        print("  truncated curvature built", flush=True)

    # --- T_ab, needs only the chi^2 part, i.e. the Schwarzschild background ---
    dth = [sp.diff(theta, x) for x in X]
    sq = tr(sp.expand(sum(gi[A, B] * dth[A] * dth[B] for A in range(4) for B in range(4))))
    T = sp.Matrix(4, 4, lambda A, B: tr(sp.expand(dth[A] * dth[B] - g[A, B] * sq / 2)))

    # --- C_ab ---
    E = levi_up(g)
    Ricud = [[tr(sp.expand(sum(gi[A, c] * Ric[c, B] for c in range(4)))) for B in range(4)]
             for A in range(4)]
    dRic = [[[tr(sp.expand(sp.diff(Ricud[b][d], X[e])
                           + sum(Gam[b][e][k] * Ricud[k][d] for k in range(4))
                           - sum(Gam[k][e][d] * Ricud[b][k] for k in range(4))))
              for d in range(4)] for b in range(4)] for e in range(4)]
    H = [[tr(sp.expand(sp.diff(theta, X[c], X[d])
                       - sum(Gam[k][c][d] * sp.diff(theta, X[k]) for k in range(4))))
          for d in range(4)] for c in range(4)]
    Ruudd = [[[[tr(sp.expand(sum(gi[b, k] * Riem[A][k][c][d] for k in range(4))))
                for d in range(4)] for c in range(4)] for b in range(4)] for A in range(4)]
    Dr = [[[[tr(sp.expand(sum(E[c][d][e][ff] * Ruudd[A][b][e][ff]
                              for e in range(4) for ff in range(4)) / 2))
             for d in range(4)] for c in range(4)] for b in range(4)] for A in range(4)]
    if verbose:
        print("  C-tensor pieces built", flush=True)

    Cup = sp.zeros(4, 4)
    for mu in range(4):
        for nu in range(mu, 4):
            tot = sp.S.Zero
            for m_, n_ in ((mu, nu), (nu, mu)):
                for s_ in range(4):
                    if dth[s_] == 0:
                        continue
                    for al in range(4):
                        for be in range(4):
                            if E[s_][m_][al][be] != 0:
                                tot += dth[s_] * E[s_][m_][al][be] * dRic[al][n_][be]
                for s_ in range(4):
                    for ta in range(4):
                        if H[s_][ta] != 0:
                            tot += H[s_][ta] * Dr[ta][m_][s_][n_]
            v = tr(sp.expand(tot / 2))
            Cup[mu, nu] = Cup[nu, mu] = v
    # lower both indices with the truncated metric
    C = sp.Matrix(4, 4, lambda A, B: tr(sp.expand(
        sum(g[A, c] * g[B, d] * Cup[c, d] for c in range(4) for d in range(4)))))
    return C, T


def chi2_part(e):
    return sp.simplify(sp.diff(sp.expand(e), chi, 2).subs(chi, 0) / 2)


if __name__ == "__main__":
    t0 = time.time()
    print("dCS O(zeta chi^2) source\n", flush=True)
    C, T = build_source()
    print(f"  built [{time.time()-t0:.0f}s]\n", flush=True)
    # CIRCULARITY, stated properly. A stationary axisymmetric circular spacetime may have
    #   {tt, tphi, rr, rth, thth, phph};  circularity forbids {tr, tth, rphi, thphi}.
    # Within the allowed set g_tphi is ODD in chi (frame dragging) and the rest are EVEN -- g_rth
    # among them. An earlier version of this control listed rth as odd and duly "failed" on a correct
    # source: T_rth = d_r(th) d_v(th) is manifestly nonzero for a dipole, so the control was demanding
    # something false. A control can be wrong in the direction of firing, not only of staying silent.
    names = {(0, 0): "tt", (1, 1): "rr", (2, 2): "thth", (3, 3): "phph", (1, 2): "rth",
             (0, 3): "tphi", (0, 1): "tr", (0, 2): "tth", (1, 3): "rphi", (2, 3): "thphi"}
    print("  chi^2 part of each component (C and T):", flush=True)
    bad = []
    for (i, j), nm in names.items():
        c2 = chi2_part(C[i, j])
        t2 = chi2_part(T[i, j])
        odd = nm in ("tphi", "tr", "tth", "rphi", "thphi")   # must all vanish at O(chi^2)
        flag = ""
        if odd and (c2 != 0 or t2 != 0):
            flag = "   <-- ODD component nonzero at chi^2: parity control FAILED"
            bad.append(nm)
        print(f"    {nm:5s}: C {'0' if c2 == 0 else 'nonzero'}   T {'0' if t2 == 0 else 'nonzero'}{flag}",
              flush=True)
    print(f"\n  parity control (only even components at O(chi^2)): {'FAIL ' + str(bad) if bad else 'PASS'}",
          flush=True)

    print("\n  angular content of the even components (must be l = 0 and l = 2 only):", flush=True)
    okl = True
    for (i, j), nm in (((0, 0), "tt"), ((1, 1), "rr"), ((2, 2), "thth"), ((3, 3), "phph")):
        for tag, e in (("C", chi2_part(C[i, j])), ("T", chi2_part(T[i, j]))):
            if e == 0:
                continue
            base = sp.sin(th) ** 2 if nm == "phph" else sp.S.One
            c0, c1_, rest = legendre_split(sp.simplify(e / base))
            ok = (c0 is not None) and c1_ == 0 and rest == 0
            okl &= bool(ok)
            print(f"    {nm:5s} {tag}: l=0 {'yes' if c0 not in (None, 0) else 'no '}  "
                  f"l=2 {'yes' if (c0 is not None and sp.simplify(e) != 0) else '?'}  "
                  f"higher-l residue: {'none' if ok else 'PRESENT'}", flush=True)
    print(f"\n  angular control: {'PASS' if okl else 'FAIL'}")
    print(f"\n  truncation fallbacks (non-polynomial in chi): {tr.fallbacks}")
    print(f"  total {time.time()-t0:.0f}s")
