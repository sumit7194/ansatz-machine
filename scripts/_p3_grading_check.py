#!/usr/bin/env python3
"""P3 PREP -- does an analytic-in-p first integral really decompose degree-by-degree?

WHY THIS EXISTS. tabula's P3 pre-registration leans on a "grading theorem": that the whole
analytic-in-momenta axis splits into independent rungs, one per Killing-tensor rank, and is
therefore "decidable and finite". Our half is the one that converts a rung into a THEOREM, so
we do not get to take that on trust. This checks the mechanism instead of assuming it, and
marks exactly where the claim stops being true.

VERDICT (see output): the grading half is TRUE and elementary. The "finite" half is NOT
established by it -- see the note at the bottom of this file.

Claim (tabula's 'grading theorem'): if F = sum_k F_k with F_k homogeneous of degree k in the
momenta and F is conserved, then EACH F_k is conserved -- so the search splits into independent
rungs, one per Killing-tensor rank.

The mechanism it rests on: for a PURE GEODESIC Hamiltonian H = 1/2 g^{ab}(x) p_a p_b, the
Hamiltonian vector field raises p-degree by EXACTLY ONE. If so, {H, F_k} lands in degree k+1
alone, the graded pieces of {H,F}=0 cannot cancel each other, and each must vanish separately.
Test it on a GENERIC metric with arbitrary functions -- no symmetry to hide behind.
"""
import sympy as sp

x, y = sp.symbols("x y", real=True)
px, py = sp.symbols("p_x p_y", real=True)
X, P = [x, y], [px, py]

# a generic 2D inverse metric: three arbitrary functions of BOTH coordinates
A, B, Cc = (sp.Function(n)(x, y) for n in ("A", "B", "C"))
H = sp.Rational(1, 2) * (A * px**2 + 2 * B * px * py + Cc * py**2)

def pb(F, G):
    return sum(sp.diff(F, X[i]) * sp.diff(G, P[i]) - sp.diff(F, P[i]) * sp.diff(G, X[i])
               for i in range(2))

def pdeg(e):
    """set of p-degrees present in e (None if not a polynomial in p)"""
    e = sp.expand(e)
    poly = sp.Poly(e, *P)
    return sorted({sum(m) for m in poly.monoms()})

print("H has p-degrees", pdeg(H), " (pure geodesic: degree 2 only)")
print()
print("  k   deg({H, F_k})        graded?   test F_k")
ok_all = True
for k in range(0, 6):
    # a generic homogeneous-degree-k F_k with arbitrary coefficient functions
    Fk = sum(sp.Function(f"f{k}{j}")(x, y) * px**(k - j) * py**j for j in range(k + 1))
    d = pdeg(pb(H, Fk))
    graded = (d == [k + 1]) or (d == [] )
    ok_all &= graded
    print(f"  {k}   {str(d):20s} {'YES' if graded else 'NO ':9s} generic degree-{k}")

print()
print("=> {H, .} maps degree k to degree k+1 EXACTLY." if ok_all else "=> NOT graded (!)")
print("   So sum_k {H,F_k} = 0 with each term in its own graded slot => each {H,F_k} = 0.")
print("   The rungs are independent. GRADING THEOREM CONFIRMED for pure geodesic flow.")

# --- and the boundary of the claim: add a potential and watch it break
print()
V = sp.Function("V")(x, y)
Hv = H + V
print("with a POTENTIAL, H = T + V(x):")
for k in (2, 3):
    Fk = sum(sp.Function(f"g{k}{j}")(x, y) * px**(k - j) * py**j for j in range(k + 1))
    print(f"  k={k}: deg({{H_V, F_k}}) = {pdeg(pb(Hv, Fk))}   <- TWO slots, k+1 and k-1")
print("  => components mix by +/-1: only the EVEN/ODD parity decouples, not each degree.")
print("     The theorem is a statement about GEODESIC flow specifically.")


# ---------------------------------------------------------------- what this does NOT establish
# GRADING gives INDEPENDENCE of the rungs. It does not give FINITENESS of the ladder:
#
#   * At each FIXED degree r the Killing-tensor equation is an overdetermined system of finite
#     type, so that rung is a finite-dimensional linear problem and is decidable in principle.
#   * There is no a priori bound on r. Nothing above rules out an irreducible Killing tensor of
#     degree 7 for a metric with none at degrees 2-6.
#
# So "CERTIFY-NO-INVARIANT-IN[F, order N]" is a statement about degrees up to N and must be
# reported that way. A screen over degrees 1..4 is a map of where we looked, which is exactly
# what tabula's own pre-reg says about families -- the same honesty is owed to the degree axis.
#
# The analytic (non-polynomial) case reduces to the polynomial one: the homogeneous Taylor
# components in p are unique and, inside the radius of convergence, {H, .} may be applied
# termwise, so an analytic first integral is an infinite family of polynomial ones. That makes
# the analytic axis no MORE finite than the polynomial axis, not less.
#
# Repro: .venv/bin/python scripts/_p3_grading_check.py
