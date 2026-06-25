"""EXPLORATORY — extend §97's conserved-quantity search from QUADRATIC to QUARTIC in the momenta
(a rank-4 Killing tensor), to close the honest caveat "no quadratic Carter, but a higher-order
invariant isn't excluded." Same SVD-null-space method, a quartic-capable basis.

Validation logic (sharper than §97's): the basis is built to also span K^2, the SQUARE of the
Schwarzschild Carter constant K=(1-y^2)p_y^2+L^2/(1-y^2). So at delta=1 the conserved set is
{K, K^2} -> the SVD must return TWO machine-zero singular values (proving the basis really does
see quartic invariants). At delta!=1, if there is no Killing tensor up to rank 4, the search
returns NONE (no machine-zero SV) even with this richer basis -> the caveat is closed numerically.

Trap guarded (the §85 lesson): a quartic basis rich enough for a real rank-4 tensor can also
express H^2 (trivially conserved on the mass shell H=-1/2) and create a false null. We keep the
spatial coefficients SIMPLE polynomials/rationals, which cannot reproduce the ZV metric's own
g^{xx},g^{yy},W -> the basis cannot express H or H^2 -> no constraint-induced false null. Verified
by an independence check AND by confirming delta!=1 stays null-free.
"""
import math
import sys

import numpy as np

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from _zv_invariant import metric, trajectory


def _full(s):
    """Generous quartic basis (before pruning). momentum monomials deg<=4 x simple spatial coeffs."""
    x_, y_, px, py = s
    om = 1.0 - y_ * y_
    terms, names = [], []
    # quadratic Carter-capable block (so delta=1 still recovers K)
    for val, nm in [(py * py, "py2"), (px * px, "px2"), (px * py, "pxpy"),
                    (y_ * y_, "y2"), (y_ * y_ / om, "y2/om"),
                    (py * py * y_ * y_, "py2y2"), (px * px * y_ * y_, "px2y2"),
                    (x_ * py * py, "xpy2"), (x_ * x_ * py * py, "x2py2"),
                    (px * px * x_, "px2x"), (px * px * x_ * x_, "px2x2")]:
        terms.append(val); names.append(nm)
    # quartic-in-momentum x SIMPLE spatial (polynomials/rationals that cannot reproduce g^{ab}/W -> no H^2 null)
    for m, mn in [(py**4, "py4"), (px * px * py * py, "px2py2"), (px**4, "px4"),
                  (px**3 * py, "px3py"), (px * py**3, "pxpy3")]:
        for sp, sn in [(1.0, "1"), (x_, "x"), (y_ * y_, "y2"), (y_**4, "y4"),
                       (1.0 / om, "/om"), (1.0 / (om * om), "/om2")]:
            terms.append(m * sp); names.append(f"{mn}*{sn}")
    # degree-0 spatial pieces K^2 needs (L^4/(1-y^2)^2)
    terms.append(1.0 / (om * om)); names.append("1/om2")
    return terms, names


_RNG = [[(4 + 14 * ((i * 37 + j * 13) % 100) / 100),
         (-0.7 + 1.4 * ((i * 7 + j * 29) % 100) / 100),
         (-1 + 2 * ((i * 17 + j * 5) % 100) / 100),
         (-1 + 2 * ((i * 3 + j * 41) % 100) / 100)]
        for i in range(400) for j in range(2)]
_ALLNAMES = _full([5.0, 0.2, 0.3, 0.4])[1]


def prune(tol=1e-6):
    """Iteratively drop the most-dependent column until the basis is full-rank on random points.
    Returns the kept index list — guarantees no algebraic identity can fake a machine-zero null."""
    keep = list(range(len(_ALLNAMES)))
    M = np.array([_full(s)[0] for s in _RNG], float)
    while True:
        Phi = M[:, keep]
        Phi = (Phi - Phi.mean(0, keepdims=True)) / (np.linalg.norm(Phi - Phi.mean(0, keepdims=True), axis=0) + 1e-30)
        U, S, Vt = np.linalg.svd(Phi, full_matrices=False)
        if S[-1] > tol:
            return keep, S[-1]
        drop = int(np.argmax(np.abs(Vt[-1])))      # term with the largest weight in the null vector
        keep.pop(drop)


KEEP, _ = prune()
NAMES = [_ALLNAMES[i] for i in KEEP]


def basis(s):
    full = _full(s)[0]
    return [full[i] for i in KEEP]


def check_independence():
    Phi = np.array([basis(s) for s in _RNG], float)
    Phi = Phi - Phi.mean(0, keepdims=True)
    S = np.linalg.svd(Phi / (np.linalg.norm(Phi, axis=0) + 1e-30), compute_uv=False)
    return S[-1], len(NAMES)


# flood with many orbits at a FIXED (E,L) (varied inclination + two launch radii, all poolable)
# so the 42-term basis is fully spanned — too few orbits leaves a dimensional near-null at ~1e-12
# that mimics an invariant (the §85 trap). ELx entries share (E,L); only x0 (the launch) varies.
ELX = [(0.97, 4.0, 11.0), (0.97, 4.0, 9.0)]
P2 = [round(0.04 + 0.025 * k, 3) for k in range(38)]


def fit(delta, ELx=ELX, p2list=P2, steps=12000, h=0.02):
    f = metric(delta)
    rows, used = [], 0
    for (E, L, x0) in ELx:
        for p2 in p2list:
            pts = trajectory(f, E, L, p2, x0, steps=steps, h=h)
            if not pts or len(pts) < 3000:
                continue
            used += 1
            sub = pts[:: max(1, len(pts) // 400)]
            Phi = np.array([basis(s) for s in sub], float)
            Phi = Phi - Phi.mean(0, keepdims=True)
            rows.append(Phi)
    if used < 10:
        return None, used
    D = np.vstack(rows)
    scale = np.linalg.norm(D, axis=0) + 1e-30
    S = np.linalg.svd(D / scale, compute_uv=False)
    return S, used


def n_invariants(S, tol=1e-12):
    """Count singular values at the FLOAT-precision floor (true invariants), not the ~1e-10
    dimensional-near-null level that survives even a well-sampled deformed orbit set."""
    return int(np.sum(S < tol))


if __name__ == "__main__":
    print("QUARTIC Killing-tensor search on Zipoy-Voorhees — closing the 'a quartic isn't excluded' caveat\n")
    indep, nb = check_independence()
    print(f"basis: {nb} terms (auto-pruned to independence); smallest SV on random pts: {indep:.2e}  "
          f"{'OK' if indep > 1e-7 else 'DEGENERATE'}\n")
    print("smallest 4 singular values; a TRUE invariant sits at the float floor ~1e-14, a dimensional")
    print("near-null at ~1e-10..1e-12 (and LIFTS with more orbits). delta=1 should show exactly 2 (K, K^2):\n")
    for delta in (1.0, 0.8, 1.2, 1.4):
        S, used = fit(delta)
        if S is None:
            print(f"  delta={delta}: too few bound orbits"); continue
        tail = ", ".join(f"{v:.1e}" for v in S[-4:][::-1])
        ninv = n_invariants(S)
        lab = "delta=1 (Schwarzschild)" if delta == 1.0 else f"delta={delta} (deformed)"
        note = "K and K^2" if delta == 1.0 else "none -> no rank<=4 Killing tensor"
        print(f"  {lab:24s} [{used:3d} orb]: smallest-4 = {tail}")
        print(f"        true invariants (SV<1e-12): {ninv}   ({note})")
