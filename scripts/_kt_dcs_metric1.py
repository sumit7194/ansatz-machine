#!/usr/bin/env python3
"""dCS step 3: the O(zeta chi) metric correction, derived.  (dCS build)

THE ORDER COUNTING, which is what makes this step cheap. The field equation is
    dG_ab = c1 C_ab + c2 T_ab.
theta is O(chi) (step 2), so T_ab ~ (grad theta)^2 is O(chi^2) and DOES NOT CONTRIBUTE here. C_ab is
linear in theta, and on Schwarzschild R_ab = 0 kills its grad-Ricci term outright, so at O(zeta chi)
    dG_ab = c1 * C_ab[Schwarzschild, theta_dipole],
with the left side the Einstein tensor linearised about Schwarzschild in the unknown correction.
The correction is ODD-parity: g_t phi. (Yagi, Yunes & Tanaka 2012 -- the even sector opens only at
O(zeta chi^2), which is the order that matters for Carter and the reason this whole build exists.)

WHAT CAN FAIL. The ansatz H(r) sin^2(th) is imposed at every power of 1/r independently against a
single free normalisation c1, so a wrong C-tensor or a wrong theta cannot be absorbed. The published
Yunes-Pretorius profile (1 + 12M/7r + 27M^2/10r^2)/r^4 is then a CHECK, not an input.

Repro:  .venv/bin/python scripts/_kt_dcs_metric1.py [--nterms 7]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from gr_engine import Geometry  # noqa: E402
from _kt_dcs import c_tensor  # noqa: E402

t, ph = sp.symbols("t phi", real=True)
r, th = sp.symbols("r theta", positive=True)
M = sp.Symbol("M", positive=True)
eps = sp.Symbol("epsilon")

def unabs(e):
    """Drop Abs(sin(th)) -> sin(th): the coordinate range is 0 < th < pi, where sin(th) > 0."""
    return e.replace(sp.Abs, lambda z: z)


if __name__ == "__main__":
    N = 7
    if "--nterms" in sys.argv:
        N = int(sys.argv[sys.argv.index("--nterms") + 1])
    f = 1 - 2 * M / r
    gS = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th) ** 2)
    print("dCS O(zeta chi) metric correction, derived\n", flush=True)

    # theta from step 2, with its normalisation folded into the single constant fitted below.
    theta = sp.cos(th) / r**2 * (1 + 2 * M / r + sp.Rational(18, 5) * M**2 / r**2)
    print("  C-tensor on Schwarzschild with the dipole ...", flush=True)
    C = c_tensor(Geometry(gS, [t, r, th, ph]), theta)
    # sqrt(-g) = r^2 |sin(th)|; on 0 < th < pi that is r^2 sin(th). SymPy keeps the Abs because it
    # cannot know the range, and it would break the polynomial extraction downstream.
    Ctp = sp.cancel(sp.together(unabs(C[0, 3])))
    print(f"  C^(t phi) = {sp.simplify(Ctp)}\n", flush=True)

    # The unknown: h_t phi = H(r) sin^2(th). Powers 1/r^2..1/r^(N+1); 1/r is EXCLUDED because it is
    # the homogeneous Kerr mode (a shift of the spin parameter), which would make the fit degenerate.
    # LINEARISE ONCE, WITH AN UNDETERMINED FUNCTION. Putting N symbolic coefficients inside the Ricci
    # computation ran 4 h without finishing (expression swell, the same trap as the O(a) scalar route).
    # A generic H(r) keeps every derivative symbolic, so the operator comes out in ONE cheap pass and
    # the series is substituted afterwards.
    Hf = sp.Function("H")(r)
    g = gS.copy()
    g[0, 3] = g[3, 0] = eps * Hf * sp.sin(th) ** 2
    print("  linearising the Einstein tensor in a generic H(r) ...", flush=True)
    lin = sp.diff(Geometry(g, [t, r, th, ph]).ricci[0, 3], eps).subs(eps, 0)
    lin = sp.cancel(sp.together(unabs(lin)))
    print(f"  linearised operator: {sp.simplify(lin / sp.sin(th)**2)}\n", flush=True)

    ds = sp.symbols(f"d0:{N}")
    H = sum(ds[k] * M**k / r ** (k + 2) for k in range(N))
    print(f"  ansatz h_(t phi) = sin^2(th) * sum_k d_k M^k / r^(k+2),  k = 0..{N-1}", flush=True)
    lin = lin.subs({sp.Derivative(Hf, (r, 2)): sp.diff(H, r, 2),
                    sp.Derivative(Hf, r): sp.diff(H, r), Hf: H}).doit()
    lin = sp.cancel(sp.together(lin))

    # c1 is the NORMALISATION and must be FIXED, not solved for: the system is linear and homogeneous
    # in (d_k, c1) together, so handing c1 to the solver admits the trivial solution -- which is what
    # happened, and the shape check then reported "same shape" on H == 0 because 0/shape is constant
    # in r. A guard that passes on the zero solution is not a guard. With c1 = 1 the system is 8
    # equations in 7 unknowns: genuinely overdetermined, so a solution existing IS the check.
    c1 = sp.Integer(1)
    # lin is the linearised R_{t phi} (indices DOWN); C[0,3] as built has indices UP. Lower it.
    Ctp_dn = sp.cancel(sp.together(unabs(gS[0, 0] * gS[3, 3] * Ctp)))
    # BOTH sides carry a common sin^2(th); divide it out of each side SEPARATELY rather than trying
    # to detect it in the combined numerator. The earlier conditional version silently left sin(th)
    # in the expression when its is_polynomial test failed, and Poly then produced equations with no
    # common solution -- reported as "NO SOLUTION" while the algebra by hand solved cleanly.
    # Both sides carry a common sin^2(th). Dividing is not enough: sympy holds the linearised Ricci
    # in a form with sin*cos pieces that cancel only under simplify, so the quotient still contained
    # tan(th) -- and Poly then swept sin(th)/tan(th) into the coefficients and returned equations with
    # no common solution. That printed as "NO SOLUTION" for a system that solves in one line.
    # GUARD: after separating, ASSERT the angular dependence is gone. Cheap, and it localises this
    # whole class of failure instead of letting it masquerade as physics.
    s2 = sp.sin(th) ** 2
    linr = sp.cancel(sp.together(sp.simplify(sp.expand(lin) / s2)))
    Cr = sp.cancel(sp.together(sp.simplify(sp.expand(Ctp_dn) / s2)))
    for nm, e in (("linearised side", linr), ("source side", Cr)):
        if th in e.free_symbols:
            print(f"  the {nm} did not separate: {th} survives in {sp.denom(e)}")
            raise SystemExit(1)
    print("  both sides separated cleanly (no angular dependence left)", flush=True)
    resid = sp.cancel(sp.together(linr - c1 * Cr))
    eqs = sp.Poly(sp.expand(sp.numer(resid)), r).all_coeffs()
    print(f"  {len(eqs)} independent powers of r against {N} unknowns + the normalisation c1",
          flush=True)
    sol = sp.solve(eqs, list(ds), dict=True)
    if not sol:
        print("  NO SOLUTION -- the ansatz cannot satisfy the equation.")
        raise SystemExit(1)
    s0 = sol[0]
    if all(sp.simplify(s0.get(d, 0)) == 0 for d in ds):
        print("  ONLY THE TRIVIAL SOLUTION -- the source cannot be balanced by this ansatz.")
        raise SystemExit(1)
    print(f"  solution: {s0}", flush=True)
    Hs = sp.simplify(H.subs(s0))
    print(f"\n  h_(t phi) / sin^2(th) = {Hs}", flush=True)
    shape = (1 + sp.Rational(12, 7) * M / r + sp.Rational(27, 10) * M**2 / r**2) / r**4
    ratio = sp.cancel(sp.simplify(Hs / shape))
    flat = sp.simplify(sp.diff(ratio, r)) == 0 and sp.simplify(Hs) != 0
    print(f"\n  published (Yunes-Pretorius): (1 + 12M/7r + 27M^2/10r^2)/r^4", flush=True)
    print(f"  ratio = {ratio}", flush=True)
    print(f"  -> SAME SHAPE: {flat}", flush=True)
    print(f"  (nonzero: {sp.simplify(Hs) != 0} -- required, since 0/shape is also constant in r)")
    print("\n  " + ("PASS: the derived O(zeta chi) correction reproduces the published profile."
                    if flat else "MISMATCH: r-dependence differs from the published profile."))
