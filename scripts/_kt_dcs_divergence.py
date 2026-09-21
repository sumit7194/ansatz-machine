#!/usr/bin/env python3
"""The decisive C-tensor control: the divergence identity.  (dCS step 1c)

WHY THIS ONE. Tracelessness rejected the first (wrong) coding but then passed all four index
conventions of the correct form -- which turned out to be the same tensor anyway (_kt_dcs_compare:
maxdiff exactly 0). So tracelessness cannot certify the C-tensor on its own. The identity

    grad_a C^{ab}  =  k * (grad^b theta) * (*RR)

is what makes dCS consistent (with the scalar equation it gives back conservation), it holds for ANY
metric and ANY theta, and it constrains the C-tensor's normalisation as well as its index structure.
A symmetrisation accident cannot satisfy it.

CONVENTION-AGNOSTIC BY DESIGN. k is MEASURED, not assumed: the test demands that the ratio be the
SAME CONSTANT for every free index b and at every sample point. Sources differ on k (-1/8 is common),
and demanding a particular value would blame the derivation for a convention -- the c1/c2 lesson from
_kt_sgb_verify. A wrong C-tensor fails by giving a non-constant ratio, which is unforgeable.

Repro:  .venv/bin/python scripts/_kt_dcs_divergence.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from gr_engine import Geometry  # noqa: E402
from _kt_dcs import c_tensor, pontryagin  # noqa: E402

t, r, th, ph = sp.symbols("t r theta phi", real=True)


def divergence_up2(geom, C):
    """grad_a C^{ab} = (1/sqrt(-g)) d_a( sqrt(-g) C^{ab} ) + Gam^b_{ac} C^{ac}  (C symmetric)."""
    x, Gam = geom.coords, geom.christoffel
    root = sp.sqrt(-sp.simplify(geom.g.det()))
    out = []
    for b in range(4):
        term = sum(sp.diff(root * C[A, b], x[A]) for A in range(4)) / root
        term += sum(Gam[b][A][c] * C[A, c] for A in range(4) for c in range(4))
        out.append(sp.together(term))
    return out


if __name__ == "__main__":
    M, a = sp.Integer(1), sp.Rational(1, 5)
    f = 1 - 2 * M / r
    g = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th) ** 2)
    g[0, 3] = g[3, 0] = -2 * M * a * sp.sin(th) ** 2 / r
    geom = Geometry(g, [t, r, th, ph])
    theta = sp.cos(th) / r**2 * (1 + 2 * M / r + sp.Rational(18, 5) * M**2 / r**2)
    print(f"background Schwarzschild + Lense-Thirring, M={M}, a={a}; dipole theta\n", flush=True)

    print("  C-tensor ...", flush=True)
    C = c_tensor(geom, theta)
    print("  divergence ...", flush=True)
    div = divergence_up2(geom, C)
    print("  *RR ...", flush=True)
    P = pontryagin(geom, simplify=False)
    gi = geom.ginv
    v = [sum(gi[b, c] * sp.diff(theta, (t, r, th, ph)[c]) for c in range(4)) for b in range(4)]
    print("  built; measuring the ratio\n", flush=True)

    pts = [(sp.Rational(7, 2), sp.Rational(1, 3)), (sp.Rational(5), sp.Rational(-2, 5)),
           (sp.Rational(11, 4), sp.Rational(3, 4))]
    ks = []
    for rv, cv in pts:
        sub = {r: rv, th: sp.acos(cv)}
        Pv = sp.N(P.subs(sub), 40)
        for b in range(4):
            rhs = sp.N((v[b] * P).subs(sub), 40)
            lhs = sp.N(div[b].subs(sub), 40)
            if abs(rhs) < sp.Float("1e-30"):
                status = "both ~0" if abs(lhs) < sp.Float("1e-25") else f"LHS={sp.N(lhs,6)} but RHS~0"
                print(f"  r={rv} c={cv} b={b}: {status}", flush=True)
                continue
            k = lhs / rhs
            ks.append(k)
            print(f"  r={rv} c={cv} b={b}:  k = {sp.N(k, 20)}", flush=True)

    print()
    if not ks:
        print("  INCONCLUSIVE: every component had a vanishing right-hand side.")
        raise SystemExit(1)
    spread = max(abs(k - ks[0]) for k in ks)
    print(f"  {len(ks)} measurements, spread {sp.N(spread, 6)}")
    if spread < sp.Float("1e-20"):
        print(f"  PASS: grad_a C^ab = k (grad^b theta)(*RR) with a single constant k = {sp.N(ks[0], 20)}")
        print(f"        (nearest simple rational: {sp.nsimplify(sp.N(ks[0], 20), rational=True).limit_denominator(64)})")
    else:
        print("  FAIL: the ratio is not constant -- the C-tensor is still wrong.")
        raise SystemExit(1)
