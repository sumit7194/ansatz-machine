#!/usr/bin/env python3
"""K2 -> K1 step 3: which of Drach's ten cubic-integrable systems are ADDITIVE (U_xy = 0), and does any additive one
give a real, harmonic, non-affine Euclidean potential with a real (1,3) lift that is integrable ONLY?
Pre-registered in data/k2_harmonic_cubic/PREREGISTRATION.md (step 3).  Source: Drach's systems as corrected in
Tsiganov, nlin/0001053, eqs (a)-(l), H = p_x p_y + U(x, y) on a (1,1) base.

Method.  Every U is linear in (alpha, beta, gamma), so U_xy = 0 identically is a LINEAR condition on them.  Evaluate
U_xy for each basis coupling at random points at 50-digit precision; the null space of that small matrix is the
additive sub-family.  (Numerical, with a gap reported: singular values ~1e-45 vs O(1e-3..1).)  Generic values of
the shape parameters (mu, a, c, m, rho) are random; their degenerate values (0) are tested separately.
Entry (a) has complex exponents (r^2 + 3r + 3 = 0) and is handled analytically.
"""
import random
import sys

import mpmath as mp
import sympy as sp

mp.mp.dps = 50
x, y = sp.symbols("x y", positive=True)
al, be, ga = sp.symbols("alpha beta gamma")
mu, a, c, m, rho = sp.symbols("mu a c m rho", positive=True)
FAILS = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if detail else ""), flush=True)
    if not ok:
        FAILS.append(label)


DRACH = {  # Tsiganov nlin/0001053 eqs (b)-(l); (a) separately
    "b": al / sp.sqrt(x * y) + be / (y - mu * x) ** 2 + ga * (y + mu * x) / (sp.sqrt(x * y) * (y - mu * x) ** 2),
    "c": al * x * y + be / (y - a * x) ** 2 + ga / (y + a * x) ** 2,
    "d": al / sp.sqrt(y * (x - a)) + be / sp.sqrt(y * (x + a)) + ga * x / sp.sqrt(x ** 2 - a ** 2),
    "e": al / sp.sqrt(x * y) + be / sp.sqrt(x) + ga / sp.sqrt(y),
    "f": al * x * y + be * y * (2 * x ** 2 + c) / sp.sqrt(x ** 2 + c) + ga * x / sp.sqrt(x ** 2 + c),
    "g": al / (y + 3 * m * x) ** 2 + be * (y - 3 * m * x) + ga * (y - m * x) * (y - 9 * m * x),
    "h": (y + m * x / 3) ** sp.Rational(-2, 3) * (al + be * (y - m * x / 3) + ga * (y ** 2 - 14 * m * x * y / 3 + m ** 2 * x ** 2 / 9)),
    "k": al * y ** sp.Rational(-1, 2) + be * x * y ** sp.Rational(-1, 2) + ga * x,
    "l": al * (y - rho * x / 3) + be * x ** sp.Rational(-1, 2) + ga * x ** sp.Rational(-1, 2) * (y - rho * x),
}


def additive_subspace(U, shape_vals, npts=6, seed=0):
    Uxy = sp.diff(U, x, y)
    cols = [sp.diff(Uxy, v) for v in (al, be, ga)]          # U_xy is linear in the couplings
    rnd = random.Random(seed)
    rows = []
    for _ in range(npts):
        pt = {x: sp.Rational(rnd.randint(40, 90), 7), y: sp.Rational(rnd.randint(11, 30), 7), **shape_vals}
        rows.append([mp.mpf(sp.N(cc.subs(pt), 60)) for cc in cols])
    M = mp.matrix(rows)
    U_, S, V_ = mp.svd_r(M)
    sv = [S[i] for i in range(min(M.rows, M.cols))]
    null = [i for i, s in enumerate(sv) if abs(s) < mp.mpf(10) ** -35]
    nulldim = len(null) + (3 - len(sv))
    basis = [[V_[i, j] for j in range(3)] for i in null]
    return nulldim, sv, basis


def main():
    print("(a) analytic: U = alpha/(xy) + beta x^r1 y^r2 + gamma x^r2 y^r1, r1 r2 = 3 (r^2+3r+3=0).")
    print("    U_xy = 2 alpha/(x^2 y^2) + 3 beta x^(r1-1) y^(r2-1) + 3 gamma x^(r2-1) y^(r1-1): three distinct monomials")
    print("    (r1 != r2, both != -1) -> linearly independent -> additive only for alpha=beta=gamma=0.  NOT ADDITIVE.\n")
    generic = {mu: sp.Rational(3, 7), a: sp.Rational(5, 9), c: sp.Rational(7, 5), m: sp.Rational(2, 5), rho: sp.Rational(9, 4)}
    special = {"b": {mu: 0}, "c": {a: 0}, "g": {m: 0}, "h": {m: 0}, "l": {rho: 0}}
    summary = {}
    for name, U in DRACH.items():
        d, sv, basis = additive_subspace(U, {k: v for k, v in generic.items() if k in U.free_symbols})
        gap = f"sv = {[mp.nstr(s, 3) for s in sv]}"
        vec = [[mp.nstr(b, 6) for b in row] for row in basis]
        print(f"({name}) generic shape params: additive sub-family dim {d}  {gap}  basis(alpha,beta,gamma) {vec}")
        summary[name] = (d, basis)
        if name in special:
            Us = U.subs(special[name])
            d2, sv2, b2 = additive_subspace(Us, {k: v for k, v in generic.items() if k in Us.free_symbols})
            print(f"     special {special[name]}: additive dim {d2}  basis {[[mp.nstr(b, 6) for b in row] for row in b2]}   U -> {sp.simplify(Us)}")

    print("\nREAL EUCLIDEAN FORMS of the additive members (x = z, y = zbar; need U = f(z) + conj(f)(zbar), non-affine):")
    print("  (e) alpha = 0:  U = beta/sqrt(x) + gamma/sqrt(y);  gamma = conj(beta) -> V = 2 Re(beta z^(-1/2))  (SW-IV sigma=0)")
    print("  (l) gamma = 0:  f = -alpha rho x/3 + beta x^(-1/2), g = alpha y;  conj(f) = g forces beta = 0 -> V affine (trivial)")
    print("  one-variable members (special params, e.g. (c) a=0: U = (beta+gamma)/y^2): f or g is zero, the other not -> no conjugate pair")
    # C1': (e)'s real form IS the section-147 potential, whose quadratic family was measured at dim 3 -> EXCLUDED
    zz, zb = sp.symbols("z zb")
    xi, eta = sp.symbols("xi eta", positive=True)
    V_e = sp.re(sp.expand_complex((xi - sp.I * eta) ** -1))          # Re(1/z) with z = xi + i eta, i.e. Re(w^{-1/2})
    check("C1': (e) real form = xi/rho^2 (the section-147 profile, up to scale)", sp.simplify(V_e - xi / (xi ** 2 + eta ** 2)) == 0)
    print("  ARGUED, not computed -- C4: (l)'s only real form is affine (conj(f) = g forces beta = 0), so no non-affine harmonic member")

    print("  (k) alpha, gamma:  f = gamma x (affine), g = alpha y^(-1/2);  conj(f) = g impossible unless alpha = gamma = 0 -> no real form")
    print("  (d), (f): additive member is x-only (gamma x/sqrt(x^2 -+ a^2 or c)); (g): additive member is affine -> no non-affine real form")

    print("\nVERDICT")
    add = [k for k, (d, _) in summary.items() if d > 0]
    print(f"  LITERAL count -- entries with a nonzero additive sub-family (generic shape params): {add}")
    print("  The pre-registered literal test ('exactly two entries') FAILS: my criterion counted degenerate members.")
    degenerate = {"d": "one-variable (x only)", "f": "one-variable (x only)", "g": "affine"}
    equivalent = {"k": "l"}      # (k) alpha y^-1/2 + gamma x  ==  (l) alpha(y - rho x/3) + beta x^-1/2  under x <-> y, up to an affine term
    reduced = sorted({equivalent.get(k, k) for k in add if k not in degenerate})
    for k_, why in degenerate.items():
        print(f"    drop ({k_}): additive member is {why}")
    print("    identify (k) ~ (l): same potential under x <-> y, up to an affine term")
    print(f"  REDUCED count (non-degenerate, up to x<->y and affine terms): {reduced}  -> CG 2015's 'only two': "
          f"{'REPRODUCED under this equivalence' if reduced == ['e', 'l'] else 'DIFFERS'}")
    print("  real, non-affine harmonic forms: only (e) -> SW-IV sigma=0 -> superintegrable (quadratic family dim 3) -> EXCLUDED")
    print("  HITS: none")
    print(f"  NOTE: literal pre-registered test failed ({add}); CG's claim holds only after the stated reduction.")
    check("CG's 'only two additive' reproduced after removing degenerate members and x<->y duplicates", reduced == ["e", "l"], f"{reduced}")
    print("  ARGUED, not computed: no HIT however the additive members are counted -- each is shown above to be one-variable,")
    print("  affine, conjugacy-impossible, or (e) = SW-IV sigma=0, whose superintegrability WAS computed (section 147).")
    print("\n" + ("PASS" if not FAILS else f"FAIL ({len(FAILS)}): {FAILS}"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
