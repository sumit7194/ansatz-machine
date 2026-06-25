"""EXPLORATORY — integrability of the Manko-Novikov (exact rotating bumpy-Kerr vacuum) metric.
Does the quadrupole anomaly q break the Carter constant, as it did for the STATIC ZV case (§97)?
This is the rotating analog. The metric is _manko_novikov.manko_novikov (vacuum-verified).

We build the reduced 2-DOF Hamiltonian NUMERICALLY from the metric (finite-difference — the metric
has exp(Legendre) factors that would swamp SymPy), producing the same callable interface as
poincare.build_hamilton, so §97's detector (_zv_invariant.fit/basis) runs on it unchanged.
q=0 must recover Kerr's Carter (validation); q!=0 should have none.
"""
import math
import sys

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from manko_novikov import manko_novikov
from _zv_invariant import basis, BNAMES, check_independence, fit  # reuse the §97 detector


def build_hamilton_numeric(M, a, q, h=1e-6):
    """Reduced (E,L-frozen) 2-DOF Hamiltonian for MN, as poincare.build_hamilton's dict of
    callables but computed numerically. q1=x, q2=y."""
    g = manko_novikov(M, a, q)

    def comps(x, y):
        gg = g([0.0, x, y, 0.0])
        gtt, gtp, gpp = gg[0][0], gg[0][3], gg[3][3]
        det = gtt * gpp - gtp * gtp                       # (t,phi) block determinant
        itt, itp, ipp = gpp / det, -gtp / det, gtt / det  # inverse (t,phi) block
        return itt, itp, ipp, 1.0 / gg[1][1], 1.0 / gg[2][2]

    def W(x, y, E, L):
        itt, itp, ipp, _, _ = comps(x, y)
        return itt * E * E - 2 * itp * E * L + ipp * L * L
    def g11(x, y, E, L):
        return comps(x, y)[3]
    def g22(x, y, E, L):
        return comps(x, y)[4]

    def dx(fn):
        return lambda x, y, E, L: (fn(x + h, y, E, L) - fn(x - h, y, E, L)) / (2 * h)
    def dy(fn):
        return lambda x, y, E, L: (fn(x, y + h, E, L) - fn(x, y - h, E, L)) / (2 * h)

    return {"g11": g11, "g22": g22, "W": W,
            "dW1": dx(W), "dW2": dy(W),
            "dg11_1": dx(g11), "dg11_2": dy(g11),
            "dg22_1": dx(g22), "dg22_2": dy(g22)}


if __name__ == "__main__":
    M, a = 1.0, 0.5
    E, L, x0 = 0.95, 2.8, 6.0
    p2list = [round(0.05 + 0.05 * k, 3) for k in range(16)]
    indep = check_independence()
    print("MANKO-NOVIKOV integrability — does the rotating bumpy-Kerr keep a Carter constant?\n")
    print(f"basis independence (random pts): {indep:.2e}  {'OK' if indep > 1e-6 else 'DEGENERATE'}\n")
    print("smallest 5 singular values; q=0 (Kerr) must recover Carter (~1e-13 + gap); q!=0 should not:\n")
    for q in (0.0, 0.1, 0.2, 0.4):
        f = build_hamilton_numeric(M, a, q)
        S, used, vec = fit(f, E, L, p2list, x0)
        if S is None:
            print(f"  q={q}: too few bound orbits ({used})"); continue
        tail = ", ".join(f"{v:.2e}" for v in S[-5:])
        gap = S[-2] / S[-1] if S[-1] > 0 else float("inf")
        lab = "q=0 (Kerr)" if q == 0 else f"q={q} (bumpy)"
        print(f"  {lab:14s} [{used:2d} orb]: {tail}   gap={gap:.1e}")
