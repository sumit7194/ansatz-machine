#!/usr/bin/env python3
"""Independent verification of high_rank_killing EXP-002: a Lorentzian vacuum pp-wave with a rank-3
Killing tensor that is irreducible in the polynomial sense.  (RESULTS §147)

PROVENANCE OF THE CLAIM.  Constructed in the high_rank_killing workspace, EXP-002-004, commits 9384d7f /
6a5b66c / b2ebbef.  Relayed here by The Bridge on the user's instruction, as the OBJECT ONLY:

    ds^2 = -(4 a xi / rho^2) dt^2 + 2 dt ds + 8 rho^2 (dxi^2 + deta^2),   rho^2 = xi^2 + eta^2
    F    = (eta p_xi - xi p_eta)(p_xi^2 + p_eta^2)/(32 rho^2)
           + (a p_s^2 / rho^2) [ xi eta p_xi + (eta^2 - xi^2)/2 p_eta ]

INDEPENDENCE.  The author's own irreducibility count ran on this repo's solve_kt_modp, so re-running it
would be the same instrument.  THIS SCRIPT IMPORTS NOTHING FROM THE REPO: plain SymPy, its own
Christoffels, its own Poisson bracket, its own Killing-algebra computation.  Irreducibility needs only two
facts, both checked here by other means:
  (i)  dim K1 = 2 (the only Killing vectors are d_t and d_s), and
  (ii) F has a nonzero pure (p_xi, p_eta) part.
Every reducible rank-3 tensor is a sum of (linear KT) x (rank-2 KT) + cubic in linear KTs, so by (i) each
of its monomials carries p_t or p_s; F has monomials carrying neither, so F is not reducible.

dim K1 BY INTEGRABILITY CONDITIONS, NOT BY A FIRST-ORDER JET COUNT.  A Killing vector is fixed by its jet
(X^a, W_ab = nabla_a X_b) at one point, which is 10 numbers, and it must satisfy L_X (nabla^k R) = 0 for
every k.  Stacking k = 0..K at a generic point gives an UPPER bound on dim K1 that tightens as K grows.
On a pp-wave the curvature is null and degenerate, so k = 0 alone is NOT tight (the Bridge's warning): the
bound is reported per K, and read only once it meets the known lower bound (d_t and d_s give 2).
Control: Schwarzschild must come out at exactly 4.

Usage: _pp_wave_verify.py      (a few minutes; exits nonzero if any check fails)
"""
import itertools
import random
import sys

import sympy as sp

FAILS = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(label)


def christoffel(g, ginv, X):
    n = len(X)
    return [[[sp.cancel(sum(ginv[a, d] * (sp.diff(g[d, b], X[c]) + sp.diff(g[d, c], X[b]) - sp.diff(g[b, c], X[d]))
                            for d in range(n)) / 2) for c in range(n)] for b in range(n)] for a in range(n)]


def riemann_down(g, G, X):
    """R_abcd with R^a_bcd = d_c G^a_db - d_d G^a_cb + G^a_ce G^e_db - G^a_de G^e_cb, lowered on a."""
    n = len(X)
    Rup = {}
    for a, b, c, d in itertools.product(range(n), repeat=4):
        Rup[a, b, c, d] = (sp.diff(G[a][d][b], X[c]) - sp.diff(G[a][c][b], X[d])
                           + sum(G[a][c][e] * G[e][d][b] - G[a][d][e] * G[e][c][b] for e in range(n)))
    return {(a, b, c, d): sp.cancel(sum(g[a, e] * Rup[e, b, c, d] for e in range(n)))
            for a, b, c, d in itertools.product(range(n), repeat=4)}


def cov_deriv(T, rank, G, X):
    """nabla T for a (0,rank) tensor stored as dict keyed by index tuples; new index FIRST."""
    n = len(X)
    out = {}
    for e in range(n):
        for idx in itertools.product(range(n), repeat=rank):
            v = sp.diff(T[idx], X[e])
            for i in range(rank):
                for f in range(n):
                    j = list(idx); j[i] = f
                    v -= G[f][e][idx[i]] * T[tuple(j)]
            out[(e,) + idx] = v
    return out


def killing_dim_bound(g, X, point, kmax):
    """Upper bounds on dim(Killing algebra) from L_X nabla^k R = 0, k = 0..K, at `point`. Returns list per K."""
    n = len(X)
    ginv = g.inv()
    G = christoffel(g, ginv, X)
    Ts = [riemann_down(g, G, X)]
    for k in range(kmax + 1):
        Ts.append(cov_deriv(Ts[-1], 4 + k, G, X))
    sub = dict(zip(X, point))
    gi = ginv.subs(sub)
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]      # W_ab, a < b
    ncol = n + len(pairs)
    rows, bounds = [], []
    for k in range(kmax + 1):
        T, Tn, rk = Ts[k], Ts[k + 1], 4 + k
        Tv = {i: sp.nsimplify(v.subs(sub)) for i, v in T.items()}
        Tnv = {i: sp.nsimplify(v.subs(sub)) for i, v in Tn.items()}
        for idx in itertools.product(range(n), repeat=rk):
            row = [sp.Integer(0)] * ncol
            for e in range(n):                                          # X^e nabla_e T
                row[e] += Tnv[(e,) + idx]
            for i in range(rk):                                         # + T_{..f..} nabla_{a_i} X^f
                for f in range(n):
                    j = list(idx); j[i] = f
                    tval = Tv[tuple(j)]
                    if tval == 0:
                        continue
                    for h in range(n):                                  # nabla_{a_i} X^f = g^{fh} W_{a_i h}
                        if gi[f, h] == 0 or h == idx[i]:
                            continue
                        a_, b_ = (idx[i], h) if idx[i] < h else (h, idx[i])
                        sign = 1 if idx[i] < h else -1
                        row[n + pairs.index((a_, b_))] += tval * gi[f, h] * sign
            if any(r != 0 for r in row):
                rows.append(row)
        r = sp.Matrix(rows).rank() if rows else 0
        bounds.append(ncol - r)
        print(f"      K = {k}: stacked rank {r} of {ncol}  ->  dim K1 <= {ncol - r}", flush=True)
    return bounds


def main():
    t, s, xi, eta = sp.symbols("t s xi eta", real=True)
    a = sp.Symbol("a", real=True, nonzero=True)
    X = (t, s, xi, eta)
    rho2 = xi ** 2 + eta ** 2
    g = sp.Matrix([[-4 * a * xi / rho2, 1, 0, 0],
                   [1, 0, 0, 0],
                   [0, 0, 8 * rho2, 0],
                   [0, 0, 0, 8 * rho2]])
    ginv = sp.simplify(g.inv())

    print("1. the metric: Lorentzian, and vacuum (Ricci-flat) -- symbolic a")
    det = sp.factor(g.det())
    check("det g < 0 for rho > 0", sp.simplify(det + 64 * rho2 ** 2) == 0, f"det = {det}")
    ev_block = sp.Matrix([[-4 * a * xi / rho2, 1], [1, 0]]).det()
    check("(t,s) block has det -1 => one timelike + one spacelike; transverse block positive -> (1,3)",
          sp.simplify(ev_block + 1) == 0)
    G = christoffel(g, ginv, X)
    Rd = riemann_down(g, G, X)
    ric = sp.Matrix(4, 4, lambda b, d: sp.cancel(sum(ginv[a_, c] * Rd[c, b, a_, d] for a_ in range(4) for c in range(4))))
    check("Ricci tensor vanishes identically", ric == sp.zeros(4, 4))
    check("Riemann is NOT zero (a genuine wave, not flat space)", any(v != 0 for v in Rd.values()))
    z = sp.Symbol("z")
    # transverse metric 8 rho^2 |dz|^2 = 2 |d(z^2)|^2: flat, with (xi, eta) parabolic coordinates of w = z^2
    w_re, w_im = sp.expand((xi + sp.I * eta) ** 2).as_real_imag()
    jac = sp.Matrix([[sp.diff(w_re, xi), sp.diff(w_re, eta)], [sp.diff(w_im, xi), sp.diff(w_im, eta)]])
    check("transverse metric = 2|dw|^2 with w = (xi + i eta)^2  (flat; parabolic coordinates)",
          sp.simplify(2 * (jac.T * jac) - 8 * rho2 * sp.eye(2)) == sp.zeros(2, 2))
    check("profile 4a xi/rho^2 = 4a Re(1/z) is harmonic in (xi, eta)",
          sp.simplify(sp.diff(xi / rho2, xi, 2) + sp.diff(xi / rho2, eta, 2)) == 0)

    print("\n2. F is a first integral: {H, F} = 0 -- own bracket, symbolic a")
    pt, ps, px, pe = sp.symbols("p_t p_s p_xi p_eta", real=True)
    P = (pt, ps, px, pe)
    H = sp.expand(sum(ginv[i, j] * P[i] * P[j] for i in range(4) for j in range(4)) / 2)
    F = ((eta * px - xi * pe) * (px ** 2 + pe ** 2) / (32 * rho2)
         + (a * ps ** 2 / rho2) * (xi * eta * px + sp.Rational(1, 2) * (eta ** 2 - xi ** 2) * pe))
    pb = lambda A, B: sp.cancel(sum(sp.diff(A, X[i]) * sp.diff(B, P[i]) - sp.diff(A, P[i]) * sp.diff(B, X[i]) for i in range(4)))
    check("{H, F} = 0 identically", pb(H, F) == 0)
    check("{p_t, F} = {p_s, F} = 0 (no t or s dependence)", pb(pt, F) == 0 and pb(ps, F) == 0)
    Fbad = F + (eta * px) * (px ** 2) / (32 * rho2)
    check("CONTROL: a perturbed F is NOT conserved (the bracket can fail)", pb(H, Fbad) != 0)

    print("\n3. dim K1 by integrability conditions (upper bounds per order K)")
    random.seed(7)
    pt_pp = (sp.Integer(0), sp.Integer(0), sp.Rational(2, 3), sp.Rational(5, 4))
    g_num = g.subs(a, sp.Rational(3, 7))
    print("   pp-wave at a = 3/7, point (xi, eta) = (2/3, 5/4):")
    bpp = killing_dim_bound(g_num, X, pt_pp, kmax=2)   # K=1 already meets the lower bound 2; K=3 (nabla^4 R, 65k comps) adds nothing
    check("the bound reaches 2 at some order (with d_t, d_s known: dim K1 = 2 EXACTLY)", 2 in bpp,
          f"bounds per K = {bpp}")
    check("first-order (K=0) bound is NOT tight here, as warned", bpp[0] > 2, f"K=0 bound {bpp[0]}")
    print("   CONTROL -- Schwarzschild (x = cos theta), must give exactly 4:")
    tt, r, x, ph = sp.symbols("t r x phi", real=True)
    f = 1 - 2 / r
    gS = sp.diag(-f, 1 / f, r ** 2 / (1 - x ** 2), r ** 2 * (1 - x ** 2))
    bS = killing_dim_bound(gS, (tt, r, x, ph), (0, sp.Rational(7, 2), sp.Rational(1, 3), 0), kmax=1)
    check("Schwarzschild bound = 4 (the method can say something other than 2)", bS[-1] == 4, f"bounds {bS}")

    print("\n4. irreducibility (polynomial sense) from (i) dim K1 = 2 and (ii) the pure transverse part")
    pure = sp.expand(F.subs({pt: 0, ps: 0}))
    check("F restricted to p_t = p_s = 0 is nonzero", pure != 0, f"{sp.factor(pure)}")
    check("=> F is not in the ideal (p_t, p_s): polynomially IRREDUCIBLE", pure != 0 and 2 in bpp)

    print("\n5. functional (in)dependence -- the author disclosed 'functionally dependent'; measured here")
    # quadratic Staeckel integral from separation in the parabolic coordinates (xi, eta)
    # separation of rho^2 (H - p_t p_s) = (p_xi^2 + p_eta^2)/16 + 2a xi p_s^2 in (xi, eta):
    #   p_xi^2/16 + 2a xi p_s^2 - (H - p_t p_s) xi^2  =  -p_eta^2/16 + (H - p_t p_s) eta^2  =:  K2
    K2 = sp.cancel(sp.together(sp.expand(px ** 2 / 16 + 2 * a * xi * ps ** 2 - (H - pt * ps) * xi ** 2)))
    K2alt = sp.cancel(sp.together(sp.expand(-pe ** 2 / 16 + (H - pt * ps) * eta ** 2)))
    check("the two separated forms of K2 agree identically", sp.cancel(K2 - K2alt) == 0)
    check("a quadratic (rank-2) Killing tensor K2 exists (parabolic separation): {H, K2} = 0", pb(H, K2) == 0)
    Z = list(X) + list(P)
    rnd = {v: sp.Rational(random.randint(2, 19), random.randint(2, 13)) for v in Z}
    rnd[a] = sp.Rational(3, 7)
    J = lambda fs: sp.Matrix([[sp.diff(fn, v) for v in Z] for fn in fs]).subs(rnd).rank()
    r3 = J([pt, ps, H]); r4 = J([pt, ps, H, F]); r5 = J([pt, ps, H, K2, F]); r4k = J([pt, ps, H, K2])
    print(f"      Jacobian ranks at a random point: (p_t,p_s,H)={r3}  +F={r4}  (p_t,p_s,H,K2)={r4k}  +F={r5}")
    check("F is independent of {p_t, p_s, H} alone", r4 == 4)
    # MEASURED, not expected: this line originally asserted the author's disclosure ("functionally
    # dependent") and FAILED -- F is independent of {p_t, p_s, H, K2}.  A single nonzero 5x5 minor at one
    # rational point proves functional independence.  Recorded as the measurement it is.
    print(f"      MEASURED: F is functionally {'INDEPENDENT' if r5 == 5 else 'dependent'} of {{p_t, p_s, H, K2}}"
          f" (rank {r5}); with p_t, p_s that is {r5} independent integrals, the maximum 2+3 for the"
          " reduced 2-DOF motion -- so the flow is maximally superintegrable in the reduced sense.")

    print("\n6. does a SECOND independent quadratic integral exist?  (settles the author's 'functionally dependent')")
    # In the flat w-plane (w = z^2, metric 2|dw|^2), every quadratic integral of H = kinetic + V is
    # K^{ij} p_i p_j + W with K a flat Killing tensor: a p1^2 + b p1p2 + c p2^2 + d L p1 + e L p2 + f L^2,
    # L = w1 p2 - w2 p1, and W exists iff curl(K grad V) = 0.  Linear in (a..f): count the solutions.
    A_, B_, C_, D_, E_, Fc = sp.symbols("A B C D E Fc")
    w1, w2 = xi ** 2 - eta ** 2, 2 * xi * eta
    d1 = lambda fn: sp.cancel((xi * sp.diff(fn, xi) - eta * sp.diff(fn, eta)) / (2 * rho2))   # d/dw1
    d2 = lambda fn: sp.cancel((eta * sp.diff(fn, xi) + xi * sp.diff(fn, eta)) / (2 * rho2))   # d/dw2
    V = xi / rho2                                                   # the profile, = Re(1/z) = Re(w^-1/2)
    K11 = A_ - D_ * w2 + Fc * w2 ** 2
    K22 = C_ + E_ * w1 + Fc * w1 ** 2
    K12 = (B_ + D_ * w1 - E_ * w2 - 2 * Fc * w1 * w2) / 2
    G1 = K11 * d1(V) + K12 * d2(V)
    G2 = K12 * d1(V) + K22 * d2(V)
    curl = sp.cancel(sp.together(d2(G1) - d1(G2)))
    num = sp.Poly(sp.numer(curl), xi, eta)
    sol = sp.linsolve(num.coeffs(), [A_, B_, C_, D_, E_, Fc])
    sols = list(sol)[0] if sol else None
    free = sorted({str(v) for e_ in (sols or []) for v in sp.sympify(e_).free_symbols})
    dim = len(free)
    print(f"      quadratic integrals (incl. H itself): {dim}-dimensional family; free parameters {free}")
    print(f"      general K = {sols}")
    check("the family contains H (a=c) and at least the parabolic integral: dim >= 2", dim >= 2)
    print(f"      MEASURED: {'a SECOND independent quadratic integral EXISTS (dim 3): F is functionally dependent on the quadratics -- the author is right, relative to the full quadratic set' if dim >= 3 else 'NO second quadratic integral (dim 2): F is functionally independent of every rank <= 2 integral'}")

    print("\n" + ("PASS -- all checks" if not FAILS else f"FAIL ({len(FAILS)}): {FAILS}"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
