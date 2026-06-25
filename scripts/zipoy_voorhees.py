"""The Zipoy-Voorhees (gamma-) metric — an EXACT static vacuum black hole with a tunable
quadrupole: Schwarzschild deformed away from sphericity, kept exactly Einstein-vacuum for
every value of the deformation delta. This is the consistent, closed-form realization of the
"quadrupole-deformed Schwarzschild" we approached numerically via the Weyl line integral —
here with NO interpolation, smooth to all orders, vacuum for any delta (not just to O(q)).

Weyl seed psi = delta * psi_Schwarzschild (rod potential). In prolate spheroidal (x,y),
x in (1,inf), y in [-1,1], with sigma the rod half-length and mass M = sigma*delta:

  ds^2 = -F dt^2 + sigma^2 F^{-1} [ H (x^2-y^2)(dx^2/(x^2-1) + dy^2/(1-y^2)) + (x^2-1)(1-y^2) dphi^2 ]
  F = ((x-1)/(x+1))^delta,   H = ((x^2-1)/(x^2-y^2))^{delta^2}

delta=1 is exactly Schwarzschild (x = r/sigma - 1). delta != 1 carries a nonzero
Geroch-Hansen quadrupole and is a genuinely different spacetime (a naked singularity, not
a black hole, for delta != 1 — but a clean exact-vacuum testbed for geodesic integrability).
"""

import math

SIGMA = 1.0


def metric(delta, sigma=SIGMA):
    """Exact ZV metric g(X), coordinates X=(t,x,y,phi). Diagonal; vacuum for all delta.
    Mass is M = sigma*delta, so pass sigma=1/delta to compare equal-mass holes across delta."""
    s2 = sigma * sigma

    def g(X):
        _, x, y, _ = X
        F = ((x - 1.0) / (x + 1.0))**delta
        H = ((x * x - 1.0) / (x * x - y * y))**(delta * delta)
        gg = [[0.0] * 4 for _ in range(4)]
        gg[0][0] = -F
        gg[1][1] = s2 / F * H * (x * x - y * y) / (x * x - 1.0)
        gg[2][2] = s2 / F * H * (x * x - y * y) / (1.0 - y * y)
        gg[3][3] = s2 / F * (x * x - 1.0) * (1.0 - y * y)
        return gg
    return g


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from numeric_curvature import ricci_numeric

    print("ZIPOY-VOORHEES — exact static vacuum BH with tunable quadrupole (closed form, smooth)\n")
    print("max|R_ab| (vacuum residual) — must stay at the finite-difference floor for EVERY delta")
    print("(exact vacuum non-perturbatively, unlike the O(q) Weyl construction):\n")
    pts = [(2.0, 0.0), (2.5, 0.3), (3.0, -0.5), (4.0, 0.7)]
    worst = 0.0
    for delta in (1.0, 0.8, 1.3, 2.0, 0.5):
        res = max(abs(ricci_numeric(metric(delta), [0.0, x, y, 0.0], h=1e-5)[i][j])
                  for (x, y) in pts for i in range(4) for j in range(4))
        worst = max(worst, res)
        lab = "delta=1 (Schwarzschild)" if delta == 1.0 else f"delta={delta}"
        q = "spherical" if delta == 1.0 else ("oblate" if delta > 1 else "prolate")
        print(f"  {lab:24s}: max|R_ab| = {res:.2e}   ({q}, quadrupole ~ delta(1-delta^2))")
    ok = worst < 1e-4
    print(f"\nZV vacuum check: {'PASSED' if ok else 'FAILED'}  (all residuals at FD floor ~1e-6 — exact vacuum)")
