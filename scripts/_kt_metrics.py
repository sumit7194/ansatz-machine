#!/usr/bin/env python3
"""Metric registry for the Killing-tensor pipeline -- one place that knows what a substrate is.

WHY A REGISTRY AND NOT ANOTHER PER-SUBSTRATE SCRIPT. The prover, the reducible-span measurement and
the exact test are all substrate-independent; only g^ab differs. Every metric added as its own
script duplicates the box logic and the denominator logic, which is where the silent errors live
(see §124: an ansatz degree guessed from the denominator instead of measured from the numerators
produced a solution space SMALLER than the reducible span, which is impossible).

COORDINATES ARE (t, x, y, phi) WITH x, y THE NON-CYCLIC PAIR. Kerr is given in Boyer-Lindquist with
y = cos(theta), which is what makes every component RATIONAL and zero-testing decidable; ZV is in
prolate spheroidal coordinates. Both therefore run through the same sampler without special cases.

PARAMETERS ARE NUMERIC, DELIBERATELY. Carrying symbolic M and a through a rank-4 assembly multiplies
the coefficient blowup by two more indeterminates for no gain: the question "is there an irreducible
Killing tensor" is asked at a point of parameter space, and a generic point answers it. a is
therefore a specific nonzero rational -- NOT zero, which would silently hand back Schwarzschild and
a larger symmetry algebra, turning a positive control into a different question.
"""
import sympy as sp

t, x, y, ph = sp.symbols("t x y phi", real=True)


def zv_metric(delta):
    """Zipoy-Voorhees in prolate spheroidal coordinates. delta = 1 is Schwarzschild."""
    F = ((x - 1) / (x + 1))**delta
    Hh = ((x**2 - 1) / (x**2 - y**2))**(delta**2)
    return sp.diag(-F,
                   Hh * (x**2 - y**2) / (F * (x**2 - 1)),
                   Hh * (x**2 - y**2) / (F * (1 - y**2)),
                   (x**2 - 1) * (1 - y**2) / F)


def kerr_metric(M=sp.Integer(1), a=sp.Rational(1, 2)):
    """Kerr in Boyer-Lindquist with x = r and y = cos(theta), the rational form.

    KNOWN ANSWER, WHICH IS THE POINT. Kerr carries the Carter constant -- an irreducible rank-2
    Killing tensor -- so a prover that reports zero irreducible here is broken. a must be nonzero
    or this degenerates to Schwarzschild."""
    Sig = x**2 + a**2 * y**2
    Dl = x**2 - 2 * M * x + a**2
    g = sp.zeros(4, 4)
    g[0, 0] = -(1 - 2 * M * x / Sig)
    g[0, 3] = g[3, 0] = -2 * M * x * a * (1 - y**2) / Sig
    g[1, 1] = Sig / Dl
    g[2, 2] = Sig / (1 - y**2)
    g[3, 3] = (x**2 + a**2 + 2 * M * x * a**2 * (1 - y**2) / Sig) * (1 - y**2)
    return g


def inverse(g):
    g = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(g[i, j])))
    gi = g.inv()
    return sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(gi[i, j])))


def get(spec):
    """'zv:2' -> Zipoy-Voorhees delta=2; 'kerr' or 'kerr:1:1/2' -> Kerr with those M, a."""
    parts = spec.split(":")
    if parts[0] == "zv":
        return inverse(zv_metric(int(parts[1]))), f"ZV delta={parts[1]}"
    if parts[0] == "kerr":
        M = sp.Rational(parts[1]) if len(parts) > 1 else sp.Integer(1)
        a = sp.Rational(parts[2]) if len(parts) > 2 else sp.Rational(1, 2)
        if a == 0:
            raise ValueError("kerr with a=0 is Schwarzschild -- a different substrate with a "
                             "larger symmetry algebra, not a Kerr control")
        return inverse(kerr_metric(M, a)), f"Kerr M={M} a={a}"
    raise ValueError(f"unknown metric spec: {spec}")


def denominator(ginv):
    """L = lcm of the denominators of g^ab, and the numerator degrees measured from g^ab itself.

    The degrees are MEASURED, never inferred from deg(L): on ZV the numerators reach y-degree 10
    while L is only y-degree 2, and guessing there produced an impossible answer (§124)."""
    dens = set()
    for i in range(4):
        for j in range(4):
            if ginv[i, j] != 0:
                d = sp.denom(sp.together(ginv[i, j]))
                if d != 1:
                    dens.add(d)
    L = sp.Integer(1)
    for d in dens:
        L = sp.lcm(L, d)
    L = sp.factor(L)
    nx = ny = 0
    for i in range(4):
        for j in range(i, 4):
            if ginv[i, j] != 0:
                pN = sp.Poly(sp.expand(sp.cancel(sp.together(ginv[i, j]) * L)), x, y)
                nx, ny = max(nx, pN.degree(x)), max(ny, pN.degree(y))
    return L, nx, ny


if __name__ == "__main__":
    import sys
    ginv, name = get(sys.argv[1] if len(sys.argv) > 1 else "kerr")
    L, nx, ny = denominator(ginv)
    pL = sp.Poly(sp.expand(L), x, y)
    print(f"{name}")
    print(f"  L = {L}")
    print(f"  L degrees x,y: {pL.degree(x)}, {pL.degree(y)}")
    print(f"  numerator degrees x,y: {nx}, {ny}")
    for i in range(4):
        for j in range(i, 4):
            if ginv[i, j] != 0:
                print(f"  g^{i}{j} = {sp.simplify(ginv[i, j])}")
