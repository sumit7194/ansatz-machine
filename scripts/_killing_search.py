"""EXPLORATORY (not a battery — underscore prefix, not collected by verify.sh).

Symbolic Killing-tensor search for the quadrupole-deformed Kerr (the §82 metric).
Decisive test for item-3's proxy: does a DIFFERENT (non-Kerr) rank-2 Killing tensor
close for the deformed metric? §84's Poincaré sections say the dynamics look integrable;
this tries to construct the conserved quantity perturbatively in ε.

⚠️ DEAD END (2026-06-23): this full-symbolic route SWAMPED — the O(ε) series-expansion
of the symmetrized covariant derivative ran 7.5 HOURS at 98% CPU with no output, the
same "expand-everything is exponentially wasteful" SymPy blow-up that killed the
rotating-EdGB R0 brute force (see DECISIONS.md). DO NOT re-run as-is. The tractable
replacement is NUMERICAL: sample the obstruction S_abc at many (r,u) points via numeric
Christoffels of the deformed metric (fast), posit a finite K_1 ansatz, and solve the
linear system ∇^Kerr K_1 = −S by least-squares — or fit a second quadratic invariant
C(r,u,p_r,p_u) along a regular orbit and test {C,H}=0 numerically. Kept as a record of
the dead end, not for re-running.

Step 1 (the swamped run): the O(ε) OBSTRUCTION — the symmetrized covariant derivative
S_abc = ∇_(a K_bc) of the Kerr Carter tensor K, evaluated in the DEFORMED connection,
to first order in ε. At ε=0 it vanishes (Kerr, §78); the O(ε) part is the source a
correction K_1 = (Kerr-operator)^{-1}(−S) must cancel. Its structure guides the K_1 ansatz.
"""

import sys
import time

import sympy as sp

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from gr_engine import Geometry

t, r, u, ph = sp.symbols("t r u phi", real=True)
M, a, eps = sp.symbols("M a epsilon", real=True)
Sig = r**2 + a**2 * u**2
De = r**2 - 2 * M * r + a**2
om = 1 - u**2

# deformed Kerr in u=cosθ coords
bump = 1 + eps * (3 * u**2 - 1) / r**3
g = sp.zeros(4)
g[0, 0] = -(1 - 2 * M * r / Sig) * bump
g[0, 3] = g[3, 0] = -2 * M * r * a * om / Sig
g[1, 1] = Sig / De
g[2, 2] = Sig / om
g[3, 3] = (r**2 + a**2 + 2 * M * r * a**2 * om / Sig) * om
geo = Geometry(g, [t, r, u, ph])

# Kerr Carter tensor (lower indices)
gK = sp.zeros(4)
gK[0, 0] = -(1 - 2 * M * r / Sig)
gK[0, 3] = gK[3, 0] = -2 * M * r * a * om / Sig
gK[1, 1] = Sig / De
gK[2, 2] = Sig / om
gK[3, 3] = (r**2 + a**2 + 2 * M * r * a**2 * om / Sig) * om
giK = gK.inv()
l = [(r**2 + a**2) / De, 1, 0, a / De]
nv = [(r**2 + a**2) / (2 * Sig), -De / (2 * Sig), 0, a / (2 * Sig)]
Kup = sp.Matrix(4, 4, lambda i, j: Sig * (l[i] * nv[j] + l[j] * nv[i]) + r**2 * giK[i, j])
Kd = sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(
    sum(gK[i, p] * gK[j, q] * Kup[p, q] for p in range(4) for q in range(4)))))

n, X, G = geo.n, geo.coords, geo.christoffel


def nab(a_, b, c):
    return sp.diff(Kd[b, c], X[a_]) - sum(G[d][a_][b] * Kd[d, c] + G[d][a_][c] * Kd[b, d] for d in range(n))


if __name__ == "__main__":
    t0 = time.time()
    comps = {}
    for a_ in range(n):
        for b in range(n):
            for c in range(b, n):
                S = nab(a_, b, c) + nab(b, c, a_) + nab(c, a_, b)
                S = sp.series(sp.cancel(sp.together(S)), eps, 0, 2).removeO()   # to O(ε)
                S = sp.simplify(S)
                if S != 0:
                    comps[(a_, b, c)] = S
    print("O(eps) Killing obstruction of Kerr-K for the deformed metric: %d nonzero components  [%.0fs]"
          % (len(comps), time.time() - t0), flush=True)
    for k, v in comps.items():
        print("  S", k, "=", sp.factor(v), flush=True)
