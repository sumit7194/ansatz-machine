#!/usr/bin/env python3
"""dCS step 2: the scalar dipole, derived from its own field equation.  (dCS build)

THE STRUCTURAL POINT, which decides the whole tower. *RR vanishes on any parity-even metric, so
Schwarzschild sources NO scalar: dCS has no static correction at all, unlike sGB. The scalar first
appears at O(chi) as a dipole; the metric correction it sources is odd-parity at O(zeta chi); and the
even-parity sector -- where the Carter obstruction lives -- only opens at O(zeta chi^2).

THE SOURCE IS VALIDATED, NOT ASSUMED. *RR for Kerr was checked against the machinery in
_kt_dcs_spotcheck (ratio exactly 1 at six random points, exact arithmetic), so its O(a) limit,
288 M^2 a cos(th) / r^7, follows by analyticity of *RR in the metric. Computing it instead by series-
expanding the raw Pontryagin sum was tried and ran 10 h without finishing -- expression swell, not a
physics obstacle.

WHAT IS DERIVED. The radial profile, by solving box theta = K * (*RR) with UNDETERMINED coefficients
and an undetermined normalisation K. The equation is imposed at every power of 1/r independently, so
an error cannot be absorbed into the coefficients: either the ansatz solves it or the solve fails.
The published Yunes-Pretorius profile is then an independent CHECK, not an input.

Repro:  .venv/bin/python scripts/_kt_dcs_scalar.py [--nterms 5]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from gr_engine import Geometry  # noqa: E402

t, r, th, ph = sp.symbols("t r theta phi", real=True)
M = sp.Symbol("M", positive=True)
a = sp.Symbol("a")


def box_scalar(geom, s):
    """box s = (1/sqrt(-g)) d_A ( sqrt(-g) g^{AB} d_B s )."""
    x = geom.coords
    root = sp.sqrt(-sp.simplify(geom.g.det()))
    gi = geom.ginv
    tot = sum(sp.diff(root * sum(gi[A, B] * sp.diff(s, x[B]) for B in range(4)), x[A])
              for A in range(4))
    return sp.simplify(sp.together(tot / root))


if __name__ == "__main__":
    N = 5
    if "--nterms" in sys.argv:
        N = int(sys.argv[sys.argv.index("--nterms") + 1])
    print("dCS scalar dipole, derived\n", flush=True)

    src = 288 * M**2 * a * sp.cos(th) / r**7          # *RR at O(a); validated, see the docstring
    print(f"  source  *RR|_O(a) = {src}", flush=True)

    Kc = sp.Symbol("K")
    cs = sp.symbols(f"c0:{N}")
    theta = sp.cos(th) / r**2 * sum(cs[k] * (M / r) ** k for k in range(N))
    f = 1 - 2 * M / r
    gS = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th) ** 2)
    print(f"  ansatz  theta = (cos th / r^2) * sum_k c_k (M/r)^k,  k = 0..{N-1}\n", flush=True)

    # The 4-D box on a separable field produces a Piecewise from sp.simplify (it branches on
    # sin(th) = 0), which Poly cannot read. Separate the angular part instead: for theta = Th(r)cos(v)
    # the l=1 radial operator is L[Th] = (1/r^2)(r^2 f Th')' - 2 Th/r^2. DERIVED, then CHECKED against
    # the full 4-D box numerically below, so the shortcut is verified rather than asserted.
    Th = sum(cs[k] * (M / r) ** k for k in range(N)) / r**2

    def L(u):
        return sp.expand(sp.cancel(sp.diff(r**2 * f * sp.diff(u, r), r) / r**2 - 2 * u / r**2))

    probe = 1 / r**3 + M / r**4
    lhs4 = box_scalar(Geometry(gS, [t, r, th, ph]), probe * sp.cos(th))
    chk = [sp.N((lhs4 - L(probe) * sp.cos(th)).subs({M: 1, r: rv, th: sp.Rational(2, 5)}), 30)
           for rv in (sp.Rational(7, 2), sp.Rational(5), sp.Rational(23, 4))]
    print(f"  radial-operator check vs the full 4-D box: {[str(sp.N(c, 4)) for c in chk]}", flush=True)
    if any(abs(c) > sp.Float("1e-25") for c in chk):
        print("  the separated operator does not match the 4-D box -- stopping.")
        raise SystemExit(1)
    print("  separated operator verified\n", flush=True)

    resid = sp.cancel(sp.together(L(Th) - Kc * 288 * M**2 * a / r**7))
    eqs = sp.Poly(sp.expand(sp.numer(resid)), r).all_coeffs()
    tag = "overdetermined" if len(eqs) > N else ("square" if len(eqs) == N else "underdetermined")
    print(f"  {len(eqs)} independent powers of r against {N} unknowns -- {tag}.", flush=True)
    if tag != "overdetermined":
        print("  (so existence of a solution is not itself the check; the SHAPE match below is,\n"
              "   together with the top coefficients coming out zero on their own)", flush=True)
    sol = sp.solve(eqs, list(cs), dict=True)
    if not sol:
        print("\n  NO SOLUTION: the ansatz cannot satisfy the equation.")
        raise SystemExit(1)
    s0 = sol[0]
    got = sp.simplify((Th * sp.cos(th)).subs(s0))
    print(f"  solution: {s0}", flush=True)
    print(f"\n  theta = {got}", flush=True)

    shape = sp.cos(th) / r**2 * (1 + 2 * M / r + sp.Rational(18, 5) * M**2 / r**2)
    ratio = sp.cancel(sp.simplify(got / shape))
    flat = sp.simplify(sp.diff(ratio, r)) == 0
    print(f"\n  published shape (Yunes-Pretorius): (1 + 2M/r + 18M^2/5r^2) cos(th)/r^2", flush=True)
    print(f"  ratio to it = {ratio}", flush=True)
    print(f"  -> SAME SHAPE (ratio independent of r): {flat}", flush=True)
    if flat:
        print("\n  PASS: the derived profile reproduces the published one up to normalisation.")
    else:
        print("\n  MISMATCH: the r-dependence differs from the published profile.")
