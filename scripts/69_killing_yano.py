#!/usr/bin/env python3
"""Step 69 — THE KILLING–YANO TENSOR: the root of the Carter constant.

§58 found Kerr's hidden symmetry as a Killing TENSOR K_ab (the Carter constant). But
that tensor is itself a SQUARE: there is a deeper object, an antisymmetric Killing–Yano
2-form Y_ab (Penrose–Floyd 1973), with
        K_ab = Y_ac Y_b{}^c     and     ∇_(a Y_b)c = 0.
Y is the true root of the hidden symmetry — and it does more than K: it is why not just
geodesics but the Dirac, Maxwell and gravitational perturbation equations all SEPARATE
in Kerr. The symmetry hierarchy of a spinning black hole:

    Killing VECTOR ξ      (∂_t, ∂_φ)   — conserved quantity LINEAR in momentum (E, L)
    Killing TENSOR K_ab   (Carter)     — conserved quantity QUADRATIC in momentum (§58)
    Killing–YANO Y_ab     (this)       — the antisymmetric root, K = Y·Y

Verified numerically (Kerr's symbolic curvature swamps, as in §58):
  (A) the Killing–Yano equation ∇_(a Y_b)c = 0 holds for Kerr's Y;
  (B) Y_ac Y_b{}^c reproduces the §58 Carter Killing tensor exactly — Y is its root;
  (C) so the chain ξ → K → Y is the full tower of Kerr's symmetry, each level hidden
      one layer deeper than the last.

Honest scope: textbook (Penrose–Floyd 1973). New is the same engine verifying the KY
equation and that Y squares to the Carter tensor, off the metric.

Run:  .venv/bin/python scripts/69_killing_yano.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from numeric_curvature import christoffel_numeric, inv4

M, A = 1.0, 0.6


def kerr(x):
    _, r, th, _ = x
    Sig = r * r + A * A * math.cos(th)**2
    De = r * r - 2 * M * r + A * A
    s2 = math.sin(th)**2
    g = [[0.0] * 4 for _ in range(4)]
    g[0][0] = -(1 - 2 * M * r / Sig)
    g[0][3] = g[3][0] = -2 * M * r * A * s2 / Sig
    g[1][1] = Sig / De
    g[2][2] = Sig
    g[3][3] = (r * r + A * A + 2 * M * r * A * A * s2 / Sig) * s2
    return g


def killing_yano(x):
    """Kerr's Killing–Yano 2-form Y_{μν} (antisymmetric), Boyer–Lindquist."""
    _, r, th, _ = x
    c, s = math.cos(th), math.sin(th)
    Y = [[0.0] * 4 for _ in range(4)]
    Y[0][1] = -A * c
    Y[0][2] = A * r * s
    Y[1][3] = -A * A * c * s * s
    Y[2][3] = r * (r * r + A * A) * s
    for i in range(4):
        for j in range(i):
            Y[i][j] = -Y[j][i]
    return Y


def carter_K(x):
    """The §58 Carter Killing tensor K_{μν} = 2Σ l_(μ n_ν) + r² g_{μν}."""
    _, r, th, _ = x
    Sig = r * r + A * A * math.cos(th)**2
    De = r * r - 2 * M * r + A * A
    l = [(r * r + A * A) / De, 1.0, 0.0, A / De]
    nv = [(r * r + A * A) / (2 * Sig), -De / (2 * Sig), 0.0, A / (2 * Sig)]
    g = kerr(x)
    gi = inv4(g)
    Ku = [[2 * Sig * 0.5 * (l[i] * nv[j] + l[j] * nv[i]) + r * r * gi[i][j]
           for j in range(4)] for i in range(4)]
    return [[sum(g[i][a] * g[j][b] * Ku[a][b] for a in range(4) for b in range(4))
             for j in range(4)] for i in range(4)]


def ky_residual(x, h=1e-5):
    """max |∇_(a Y_b)c| (symmetric part of ∇_a Y_bc in a,b — the KY equation)."""
    G = christoffel_numeric(kerr, x)

    def dY(d):
        xp, xm = list(x), list(x)
        xp[d] += h
        xm[d] -= h
        Yp, Ym = killing_yano(xp), killing_yano(xm)
        return [[(Yp[i][j] - Ym[i][j]) / (2 * h) for j in range(4)] for i in range(4)]

    dYa = [dY(d) for d in range(4)]
    Y = killing_yano(x)

    def nab(a, b, c):
        return dYa[a][b][c] - sum(G[e][a][b] * Y[e][c] + G[e][a][c] * Y[b][e] for e in range(4))
    return max(abs(nab(a, b, c) + nab(b, a, c)) for a in range(4) for b in range(4) for c in range(4))


def main():
    print("THE KILLING–YANO TENSOR — the root of the Carter constant\n")
    pts = [[0.0, 4.0, 1.1, 0.0], [0.0, 6.0, 0.7, 0.3], [0.0, 3.0, 1.4, 0.5]]
    ok = []

    # (A) the Killing–Yano equation ∇_(a Y_b)c = 0
    ky = max(ky_residual(p) for p in pts)
    okA = ky < 1e-5
    ok.append(okA)
    print(f"  (A) Killing–Yano equation ∇_(a Y_b)c = 0:  max residual = {ky:.1e}   "
          f"{'✅ a deeper (antisymmetric) symmetry' if okA else '❌'}")

    # (B) Y_ac Y_b^c = the §58 Carter Killing tensor — Y is its square root
    worst = 0.0
    for x in pts:
        g, Y, K = kerr(x), killing_yano(x), carter_K(x)
        gi = inv4(g)
        Ysq = [[sum(Y[i][a] * gi[a][b] * Y[j][b] for a in range(4) for b in range(4))
                for j in range(4)] for i in range(4)]
        worst = max(worst, max(abs(Ysq[i][j] - K[i][j]) for i in range(4) for j in range(4)))
    okB = worst < 1e-9
    ok.append(okB)
    print(f"\n  (B) Y_ac Y_b^c − K_Carter(§58):  max |Δ| = {worst:.1e}   "
          f"{'✅ Y squares to the Carter tensor' if okB else '❌'}")

    # (C) the symmetry tower
    okC = okA and okB
    ok.append(okC)
    print(f"\n  (C) the full hidden-symmetry tower of Kerr:")
    print(f"        Killing VECTOR ξ (∂_t,∂_φ)  → E, L   (linear in momentum)")
    print(f"        Killing TENSOR K (Carter)   → C      (quadratic, §58)")
    print(f"        Killing–YANO  Y             → K = Y·Y (the antisymmetric root)   "
          f"{'✅' if okC else '❌'}")
    print(f"      Y is also why Dirac/Maxwell/perturbation equations all separate in Kerr.")

    passed = all(ok)
    print(f"\nKILLING–YANO: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(the KY equation holds; Y² = the Carter tensor — the root of the hidden symmetry)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
