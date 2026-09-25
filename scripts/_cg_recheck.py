#!/usr/bin/env python3
"""Fresh re-derivation of the two EXP-003 statements the rank-3 note borrows (Bridge ask, 2026-09-26).
Pre-registered in data/cg_recheck/PREREGISTRATION.md. Source: CG 2015 (arXiv:1503.02162), typeset PDF only.
EXP-003's code is neither imported nor read.

(a) CG eq (20): is their cubic I = -1/2 {Q_a, Q_b}, and which relation I^2 = P(H, Q_a, Q_b) holds? DERIVED by a
    linear fit over all monomials H^i Q_a^j Q_b^k, i+j+k <= 3, not merely checked. With a sabotage.
(b) What the anti-self-duality argument actually covers: the 4D lift of Drach's first system (CG eq 16), and the
    5D / 6D rank-4 oxidations (CG eqs 26, 30) through their Kaluza-Klein bases.

    .venv/bin/python scripts/_cg_recheck.py
"""
import itertools
import random
import sys

import sympy as sp

FAILS = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if detail else ""), flush=True)
    if not ok:
        FAILS.append(label)


# ------------------------------------------------------------------------------------------------ (a)
x, y = sp.symbols("x y", positive=True)
px, py = sp.symbols("p_x p_y")
al, be = sp.symbols("alpha beta", positive=True)


def pb(A, B):
    return sp.expand(sp.diff(A, x) * sp.diff(B, px) - sp.diff(A, px) * sp.diff(B, x)
                     + sp.diff(A, y) * sp.diff(B, py) - sp.diff(A, py) * sp.diff(B, y))


def zero(e):
    return sp.simplify(e) == 0


def fit_relation(I, H, Qa, Qb, params, npts=45, seed=3):
    """Unknowns c_ijk: I^2 = sum c_ijk H^i Qa^j Qb^k, i+j+k <= 3, at FIXED rational (alpha, beta) = params.
    Exact rational linear equations from phase-space points with x, y perfect squares (square roots stay
    rational). Returns {monomial: value} for the unique solution, None if inconsistent, 'free' if not unique.
    (A symbolic-parameter solve ran >20 min; generic rational parameters plus the symbolic identity check below
    carry the same content.)"""
    mons = [m for m in itertools.product(range(4), repeat=3) if sum(m) <= 3]
    cs = sp.symbols(f"c0:{len(mons)}")
    rnd = random.Random(seed)
    E = [e.subs(params) for e in (H, Qa, Qb, I ** 2)]
    rows, rhs = [], []
    for _ in range(npts):
        pt = {x: sp.Rational(rnd.randint(2, 9), rnd.randint(1, 4)) ** 2,
              y: sp.Rational(rnd.randint(2, 9), rnd.randint(1, 4)) ** 2,
              px: sp.Rational(rnd.randint(-9, 9), rnd.randint(1, 5)),
              py: sp.Rational(rnd.randint(-9, 9), rnd.randint(1, 5))}
        h, a, b, i2 = (e.subs(pt) for e in E)
        rows.append([h ** m[0] * a ** m[1] * b ** m[2] for m in mons])
        rhs.append(i2)
    from sympy.polys.matrices import DomainMatrix
    from sympy import QQ
    Aug = DomainMatrix([[QQ(sp.Rational(e).p, sp.Rational(e).q) for e in r + [b]] for r, b in zip(rows, rhs)],
                       (len(rows), len(mons) + 1), QQ)
    R, piv = Aug.rref()                                    # exact over QQ (sympy Matrix.rank stalled here)
    if len(mons) in piv:
        return None                                        # inconsistent: no relation
    if len(piv) < len(mons):
        return "free"                                      # not unique
    Rl = R.to_Matrix()
    return {m: Rl[i, len(mons)] for i, m in enumerate(mons) if Rl[i, len(mons)] != 0}


def part_a():
    print("(a) CG eq (20): H = p_x p_y + alpha/sqrt(x) + beta/sqrt(y)")
    H = px * py + al / sp.sqrt(x) + be / sp.sqrt(y)
    I = x * px ** 2 * py - y * px * py ** 2 + be * x / sp.sqrt(y) * px - al * y / sp.sqrt(x) * py
    Qa = x * px * py - y * py ** 2 + be * x / sp.sqrt(y) - al * sp.sqrt(x)          # CG footnote 9
    swap = {x: y, y: x, px: py, py: px, al: be, be: al}
    Qb = Qa.subs(swap, simultaneous=True)
    check("H is invariant under (x, p_x, alpha) <-> (y, p_y, beta)", zero(H.subs(swap, simultaneous=True) - H))
    check("A1 {H, I} = 0", zero(pb(H, I)))
    check("A1 {H, Q_a} = 0  (footnote 9 as read from the typeset PDF)", zero(pb(H, Qa)))
    check("A1 {H, Q_b} = 0", zero(pb(H, Qb)))
    br = pb(Qa, Qb)
    check("A2 {Q_a, Q_b} = -2 I, i.e. I = -1/2 {Q_a, Q_b}", zero(br + 2 * I), f"{{Qa,Qb}} = {sp.factor(br)}")
    stated = {(1, 1, 1): sp.Integer(-1), (0, 1, 0): -be ** 2, (0, 0, 1): -al ** 2}
    for params in ({al: sp.Rational(2, 3), be: sp.Rational(7, 5)}, {al: sp.Rational(11, 4), be: sp.Rational(3, 13)},
                   {al: sp.Integer(5), be: sp.Rational(1, 6)}):
        rel = fit_relation(I, H, Qa, Qb, params)
        shown = (" + ".join(f"({v})*H^{m[0]} Qa^{m[1]} Qb^{m[2]}" for m, v in rel.items())
                 if isinstance(rel, dict) else rel)
        print(f"     A3 derived at {params}: I^2 = {shown}")
        want = {m: v.subs(params) for m, v in stated.items()}
        check(f"A3 unique relation at {params} equals the stated one", isinstance(rel, dict) and rel == want)
    check("A3 symbolic identity I^2 + H Qa Qb + beta^2 Qa + alpha^2 Qb = 0 for all alpha, beta",
          zero(I ** 2 + H * Qa * Qb + be ** 2 * Qa + al ** 2 * Qb))
    pt = {x: sp.Rational(9, 4), y: sp.Rational(25, 9), px: sp.Rational(3, 7), py: sp.Rational(-5, 3),
          al: sp.Rational(2, 3), be: sp.Rational(7, 5)}
    J = lambda Fs: sp.Matrix([[sp.diff(F, v) for v in (x, y, px, py)] for F in Fs]).subs(pt).rank()
    check("A4 functional rank (H, Qa, I) = 3", J([H, Qa, I]) == 3)
    check("A4 functional rank (H, Qa, Qb, I) = 3  (I is functionally dependent)", J([H, Qa, Qb, I]) == 3)
    # sabotage: flip the sign of I's beta term
    Ib = x * px ** 2 * py - y * px * py ** 2 - be * x / sp.sqrt(y) * px - al * y / sp.sqrt(x) * py
    red1 = not zero(pb(H, Ib))
    red2 = not zero(br + 2 * Ib)
    red3 = fit_relation(Ib, H, Qa, Qb, {al: sp.Rational(2, 3), be: sp.Rational(7, 5)}) is None
    check("SABOTAGE (beta-term sign flipped): {H,I} != 0, bracket identity fails, no relation found",
          red1 and red2 and red3, f"{red1} {red2} {red3}")


# ------------------------------------------------------------------------------------------------ (b)
def curvature(g, X):
    n = len(X)
    gi = g.inv()
    Gam = [[[sp.simplify(sum(gi[a, e] * (sp.diff(g[e, b], X[c]) + sp.diff(g[e, c], X[b]) - sp.diff(g[b, c], X[e]))
                             for e in range(n)) / 2) for c in range(n)] for b in range(n)] for a in range(n)]
    R = sp.MutableDenseNDimArray.zeros(n, n, n, n)   # R^a_{bcd}
    for a, b, c, d in itertools.product(range(n), repeat=4):
        if c < d:
            v = sp.diff(Gam[a][d][b], X[c]) - sp.diff(Gam[a][c][b], X[d]) + sum(
                Gam[a][c][e] * Gam[e][d][b] - Gam[a][d][e] * Gam[e][c][b] for e in range(n))
            v = sp.simplify(v)
            R[a, b, c, d] = v
            R[a, b, d, c] = -v
    Ric = sp.Matrix(n, n, lambda b, d: sp.simplify(sum(R[a, b, a, d] for a in range(n))))
    return gi, R, Ric


t, s, w, u = sp.symbols("t s w u", real=True)
ga, bb = sp.symbols("gamma beta_1", positive=True)


def cg_metric(U):
    """CG eq (1) in the order (t, s, x, y): -2U dt^2 + 2 dt ds + 2 dx dy."""
    g = sp.zeros(4, 4)
    g[0, 0] = -2 * U
    g[0, 1] = g[1, 0] = 1
    g[2, 3] = g[3, 2] = 1
    return g


def asd_test(U, name):
    """CG eq (6): 1/2 sqrt(g) g^{ml} g^{nr} eps_{lrqs} R^p_{kmn} = +- R^p_{kqs}. Returns (nonflat, ricciflat,
    upper sign holds, lower sign holds, Kretschmann)."""
    X = [t, s, x, y]
    g = cg_metric(U)
    gi, R, Ric = curvature(g, X)
    detg = sp.simplify(g.det())
    sq = sp.sqrt(detg)
    lhs = sp.MutableDenseNDimArray.zeros(4, 4, 4, 4)
    for p_, k, q, s_ in itertools.product(range(4), repeat=4):
        lhs[p_, k, q, s_] = sp.simplify(sq / 2 * sum(gi[m, l] * gi[n, r] * sp.LeviCivita(l, r, q, s_) * R[p_, k, m, n]
                                                     for m, n, l, r in itertools.product(range(4), repeat=4)
                                                     if R[p_, k, m, n] != 0 and gi[m, l] != 0 and gi[n, r] != 0))
    nonflat = any(R[i] != 0 for i in itertools.product(range(4), repeat=4))
    up = all(sp.simplify(lhs[i] - R[i]) == 0 for i in itertools.product(range(4), repeat=4))
    lo = all(sp.simplify(lhs[i] + R[i]) == 0 for i in itertools.product(range(4), repeat=4))
    Rdown = lambda a, b, c, d: sum(g[a, e] * R[e, b, c, d] for e in range(4))
    Rup = lambda a, b, c, d: sum(gi[b, f] * gi[c, h] * gi[d, k] * R[a, f, h, k]
                                 for f, h, k in itertools.product(range(4), repeat=3))
    kret = sp.simplify(sum(Rdown(a, b, c, d) * Rup(a, b, c, d) for a, b, c, d in itertools.product(range(4), repeat=4)
                           if R[a, b, c, d] != 0))
    ricciflat = Ric == sp.zeros(4, 4)
    print(f"     {name}: det g = {detg}, non-flat {nonflat}, Ricci-flat {ricciflat}, "
          f"eq(6) upper(SD) {up}, lower(ASD) {lo}, Kretschmann {kret}")
    return nonflat, ricciflat, up, lo, kret


def hodge_square_sign(sig):
    """** on 2-forms for a constant diagonal metric of signature sig: returns c with ** = c * Id."""
    g = sp.diag(*sig)
    gi = g.inv()
    sq = sp.sqrt(abs(g.det()))
    pairs = [(a, b) for a in range(4) for b in range(a + 1, 4)]

    def star(F):   # F: antisymmetric 4x4 of lower components
        Fu = gi * F * gi.T
        return sp.Matrix(4, 4, lambda c, d: sq / 2 * sum(sp.LeviCivita(a, b, c, d) * Fu[a, b]
                                                        for a in range(4) for b in range(4)))
    cs = set()
    for a, b in pairs:
        F = sp.zeros(4, 4); F[a, b] = 1; F[b, a] = -1
        SS = star(star(F))
        cs.add(sp.simplify(SS[a, b] / F[a, b]))
        if any(SS[i, j] != 0 for i in range(4) for j in range(4) if (i, j) not in ((a, b), (b, a))):
            cs.add("not proportional")
    return cs


def part_b():
    print("\n(b) the anti-self-duality argument: what it covers")
    U16 = al * (y - be * x) + ga / sp.sqrt(x)
    nf, rf, up, lo, _ = asd_test(U16, "4D lift of Drach's first system (CG eq 16 in eq 1)")
    check("B1 4D first-system metric: non-flat, Ricci-flat, ASD (eq 6 lower sign) and not SD", nf and rf and lo and not up)
    c22, c13 = hodge_square_sign([-1, -1, 1, 1]), hodge_square_sign([-1, 1, 1, 1])
    check("B2 (computed part) ** = +1 on 2-forms in (2,2), ** = -1 in (1,3)", c22 == {1} and c13 == {-1}, f"{c22} {c13}")
    print("     B2 (ARGUED, textbook): in (1,3) * has eigenvalues +-i on real 2-forms, so the SD and ASD halves of a")
    print("        real Weyl tensor are complex conjugates. W^- = 0 is a holomorphic condition on the complexified")
    print("        metric, so it holds on every real slice; there it forces W = 0, and Ricci-flat + W = 0 is flat,")
    print("        contradicting B1. So the 4D first-system metric has NO Lorentzian real form. It carries rank 3, not 4.")

    # B3: 5D CG eq 26 = h + (dw + alpha x dt)^2
    print("\n     5D rank-4 metric, CG eq 26, order (t, s, x, y, w)")
    Ueff5 = al * y + ga / sp.sqrt(x) - (al * x) ** 2 / 2
    g5 = sp.zeros(5, 5)
    g5[:4, :4] = cg_metric(Ueff5)
    g5[0, 4] = g5[4, 0] = al * x
    g5[4, 4] = 1
    A = sp.Matrix([al * x, 0, 0, 0, 1])                 # the 1-form dw + alpha x dt
    base5 = sp.simplify(g5 - A * A.T)
    check("B3 eq 26 = h + (dw + alpha x dt)^2 with h = CG eq 1, U_base = alpha y + gamma/sqrt(x), no w-leg",
          base5[:4, :4] == cg_metric(al * y + ga / sp.sqrt(x)) and all(base5[i, 4] == 0 for i in range(5)))
    nf, rf, up, lo, kr = asd_test(al * y + ga / sp.sqrt(x), "KK base of eq 26")
    check("B3 the KK base is non-flat, Ricci-flat, ASD, Kretschmann 0", nf and rf and lo and not up and kr == 0)
    print("     B3 (ARGUED): g(d_w, d_w) = 1 identically. On any real Lorentzian slice where d_w is real, either d_w is")
    print("        spacelike and the base is a Lorentzian real form of h (excluded by B2), or d_w is timelike and")
    print("        the base is definite. A definite metric with Kretschmann 0 is flat, but h is not (excluded).")
    print("        Slices on which d_w is NOT real are not covered.")

    # B4: 6D CG eq 30 = base + (dw + alpha x dt)^2 + (du - dt/sqrt(x))^2
    print("\n     6D rank-4 metric, CG eq 30, order (t, s, x, y, w, u)")
    Ueff6 = al * y - 1 / (2 * x) - (al * x) ** 2 / 2
    g6 = sp.zeros(6, 6)
    g6[:4, :4] = cg_metric(Ueff6)
    g6[0, 4] = g6[4, 0] = al * x
    g6[0, 5] = g6[5, 0] = -1 / sp.sqrt(x)
    g6[4, 4] = g6[5, 5] = 1
    A1 = sp.Matrix([al * x, 0, 0, 0, 1, 0])
    A2 = sp.Matrix([-1 / sp.sqrt(x), 0, 0, 0, 0, 1])
    base6 = sp.simplify(g6 - A1 * A1.T - A2 * A2.T)
    Ub6 = sp.simplify(-base6[0, 0] / 2)
    check("B4 eq 30 = base + (dw + alpha x dt)^2 + (du - dt/sqrt(x))^2 with a CG-eq-1 base",
          all(base6[i, j] == cg_metric(Ub6)[i, j] for i in range(4) for j in range(4))
          and all(base6[i, k] == 0 for i in range(6) for k in (4, 5)), f"U_base = {Ub6}")
    nf6, _, _, _, _ = asd_test(Ub6, "KK base of eq 30")
    check("B4 the 6D KK base is FLAT, so the ASD argument does not transfer to eq 30", not nf6)


def main():
    part_a()
    part_b()
    print("\nLABELS")
    print("  (a) CONFIRMED" if not [f for f in FAILS if f.startswith(("A", "H", "SAB"))] else "  (a) NOT CONFIRMED -- see FAILs")
    print("  (b) CORRECTED: no rank-4 (2,2) metric exists in CG (rank 4 lives in 5D (2,3) eq 26 and 6D (2,4) eq 30).")
    print("      The ASD argument is sound for the 4D first-system metric (rank 3). It extends to eq 26 only on real")
    print("      slices where d_w is real, and not at all to eq 30, whose KK base is flat.")
    print("\n" + ("PASS" if not FAILS else f"FAIL ({len(FAILS)}): {FAILS}"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
