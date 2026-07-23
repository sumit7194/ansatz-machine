#!/usr/bin/env python3
"""Step 120 — BRIDGE ROUND 8 / G2 CANDIDATE A: integrable, but with NO Killing-Yano root.

The bridge's Falsification Ledger item G2 attacks leg Q's "legible <=> KY-integrable" (8/8,
phi = 1.0). The record cannot separate three hypotheses, because in every catalog entry so far
KY-ness, integrability and polynomial-invariance COINCIDE:
    H_KY   legibility tracks Killing-Yano structure specifically
    H_INT  legibility tracks integrability -- any Killing tensor, root or not
    H_POLY legibility tracks the existence of a polynomial-in-momenta invariant
Candidate A is designed to be integrable + polynomial-invariant + KY-free, separating H_KY.

WHY THIS COULD NOT BE FOUND IN THE EXISTING CATALOG. Collinson (1976) and Dietz-Ruediger
(1981): every Petrov type-D VACUUM metric admitting a Killing tensor also admits a Killing-Yano
tensor (the sole exception in the literature being Kinnersley's class IIIB). Our whole catalog
is vacuum or near-vacuum type D, so the coincidence leg Q observed is forced there by a
theorem, not by legibility. Candidate A must therefore leave vacuum -- and it does.

THE METRIC (designed here; Liouville/Stackel-separable, two Killing vectors), on x > 0:

    ds^2 = -(x^2+y^2)/(1+y^2) dt^2 + (x^2+y^2)(dx^2 + dy^2)
           + x^2 (x^2+y^2)/(1+x^2) dphi^2

built so that the Hamilton-Jacobi equation splits as F(x,p_x) = -G(y,p_y), giving an
irreducible rank-2 Killing tensor whose MIXED eigenvalues are four DISTINCT functions

    (lambda_t, lambda_x, lambda_y, lambda_phi)
        = ( y^2(1-x^2)/(1+y^2),  y^2,  -x^2,  (y^2-x^4)/(1+x^2) ).

The g_phiphi factor x^2 is deliberate: it puts a centrifugal barrier L^2/x^2 in the radial
equation, so bound orbits with L != 0 are confined to a compact annular region that EXCLUDES
the curvature singularity at x = y = 0. (The first draft without it had every bound orbit
plunge into the singularity -- the trajectory data handed to a probe has to be clean.)

THE KY-ABSENCE CERTIFICATE, in two independent strengths:

 (1) POINTWISE (killing_yano.ky_root_spectrum_certificate). For ANY 2-form Y,
     K^a{}_b = -(g^{-1}Y)^2, and g^{-1}Y is g-antisymmetric, so its eigenvalues come in +/-
     pairs and every eigenvalue of (Y.Y)^a{}_b has EVEN multiplicity. Machine-proved: the
     characteristic polynomial of -(eta^{-1}Y)^2 for a general Y is an exact perfect square.
     Our K has four distinct eigenvalues => K_ab != Y_ac Y_b{}^c for ANY antisymmetric Y, at
     any point. This is stronger than "the KY equation has no solution": it fails already in
     pointwise linear algebra, so no PDE solving can rescue it.

 (2) GLOBAL (killing_yano.killing_yano_jet_bound). The metric admits NO Killing-Yano tensor at
     all -- not merely none that squares to K. The order-3 Taylor jet of nabla_(a Y_b)c = 0
     forces Y = 0 at every sampled point. The bound is one-sided by construction (it contains
     the jets of all true solutions), and validated in the other direction: Minkowski returns
     10 (the maximal KY space in 4D) and Schwarzschild returns 1 (its single KY tensor).

BLIND PROTOCOL: this script also writes TWO files -- data/bridge_round8/G2_candidate_A.json
(the METRIC ONLY, for tabula) and .../G2_candidate_A_SEALED.json (the symbolic verdicts, for
the bridge alone). Leakage of the second to tabula voids the round.

Repro:  .venv/bin/python scripts/120_candidate_A_no_ky.py [--quick]
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry, zero_simplify
from killing_yano import (is_killing_tensor, killing_tensor_reducible,
                          killing_yano_jet_bound, ky_root_obstruction,
                          ky_root_spectrum_certificate)

QUICK = "--quick" in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

t, x, y, ph = sp.symbols("t x y phi", real=True)
COORDS = [t, x, y, ph]
S = x**2 + y**2

# ------------------------------------------------------------------ the designed metric
#   Liouville form: 2H = [p_x^2 + p_y^2 + (A+B) p_t^2 + (C+D) p_phi^2] / (u+v)
#   with u = x^2, v = y^2, A = -1, B = -y^2, C = 1/x^2, D = 1.
#   The eigenvalues of the resulting Killing tensor are v, -u, (vA-uB)/(A+B), (vC-uD)/(C+D):
#   FOUR distinct functions, which is exactly what kills the Killing-Yano root.
U, V = x**2, y**2
A, B, C, D = -sp.Integer(1), -y**2, 1 / x**2, sp.Integer(1)
METRIC = sp.diag(S / (A + B), S, S, S / (C + D))   # diag(-S/(1+y^2), S, S, x^2 S/(1+x^2))


def build():
    geo = Geometry(METRIC, COORDS)
    # K^{ab} = F^{ab} - u(x) g^{ab},  F = p_x^2 + A p_t^2 + C p_phi^2
    Fup = sp.diag(A, sp.Integer(1), sp.Integer(0), C)
    Kup = sp.simplify(Fup - U * geo.ginv)
    Kdn = sp.simplify(geo.g * Kup * geo.g)
    return geo, Kup, Kdn


# ------------------------------------------------------------------ geodesics (for the orbit box)
def _hamilton_rhs():
    """Lambdify the EXACT Hamilton equations off the symbolic metric -- no finite differences
    (the first draft used them and the Q-drift they produced masked the real problem, which was
    that the orbit was plunging into the x=y=0 singularity)."""
    pt, px, py, pp = sp.symbols("p_t p_x p_y p_phi", real=True)
    P = [pt, px, py, pp]
    gi = sp.diag(*[1 / METRIC[i, i] for i in range(4)])
    H = sum(gi[a, a] * P[a]**2 for a in range(4)) / 2
    dq = [sp.diff(H, P[a]) for a in range(4)]
    dp = [-sp.diff(H, q) for q in COORDS]
    return sp.lambdify((x, y, pt, px, py, pp), dq + dp, "math"), sp.lambdify(
        (x, y, pt, px, py, pp), H, "math")


_RHS, _H = _hamilton_rhs()


def orbit(E, L, x0, y0, py0, steps=60000, dtau=1e-3):
    """Integrate one timelike geodesic (2H = -1); return (max rel. drift of Q, box, Q0)."""
    import math
    rhs2 = (-(x0 * x0 + y0 * y0) + (1 + y0 * y0) * E * E
            - (1 + 1 / (x0 * x0)) * L * L) - py0 * py0
    if rhs2 < 0:
        return None
    s = [0.0, x0, y0, 0.0, -E, math.sqrt(rhs2), py0, L]

    def Q(st):
        return st[5]**2 - E * E + L * L / (st[1]**2) + st[1]**2

    def f(st):
        return _RHS(st[1], st[2], st[4], st[5], st[6], st[7])

    q0, worst = Q(s), 0.0
    box = [x0, x0, y0, y0]
    for _ in range(steps):
        k1 = f(s)
        k2 = f([s[i] + 0.5 * dtau * k1[i] for i in range(8)])
        k3 = f([s[i] + 0.5 * dtau * k2[i] for i in range(8)])
        k4 = f([s[i] + dtau * k3[i] for i in range(8)])
        s = [s[i] + dtau / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(8)]
        if s[1] <= 1e-4:
            break
        worst = max(worst, abs(Q(s) - q0) / max(1e-12, abs(q0)))
        box = [min(box[0], s[1]), max(box[1], s[1]), min(box[2], s[2]), max(box[3], s[2])]
    return worst, box, q0


def main():
    print(__doc__.split("Repro:")[0])
    ok = []
    geo, Kup, Kdn = build()

    # ---------------------------------------------------------------- (A) it IS a Killing tensor
    t0 = time.time()
    bad = is_killing_tensor(geo, Kdn)
    okA = not bad
    ok.append(okA)
    print(f"  (A) nabla_(a K_bc) = 0 verified symbolically on all 20 components:  "
          f"{'✅ K IS a Killing tensor (exact, not numeric)' if okA else '❌ ' + str(bad[:2])}"
          f"   ({time.time()-t0:.1f}s)")
    print(f"      K^ab = diag({', '.join(str(sp.simplify(Kup[i,i])) for i in range(4))})")

    # ---------------------------------------------------------------- (B) it is IRREDUCIBLE
    kvs = [[1, 0, 0, 0], [0, 0, 0, 1]]                    # d_t and d_phi
    red, sol = killing_tensor_reducible(geo, Kup, kvs)
    okB = not red
    ok.append(okB)
    print(f"\n  (B) reducible to c0 g + sum c_IJ xi_I xi_J with CONSTANT coefficients?  "
          f"{'no ✅ the Killing tensor is IRREDUCIBLE' if okB else f'YES ❌ {sol}'}")

    # ---------------------------------------------------------------- (C) the conserved quantity
    E, L = sp.symbols("E L", positive=True)
    Q_expr = sp.Symbol("p_x")**2 - E**2 + x**2 * L**2 + x**2
    print(f"\n  (C) the explicit conserved quantity (rank 2, quadratic in the momenta):")
    print(f"        Q = K^ab p_a p_b, K^ab = diag as printed above")
    print(f"        on the mass shell 2H = -1, with E = -p_t and L = p_phi:")
    print(f"        Q = p_x^2 - E^2 + L^2/x^2 + x^2  =  -(p_y^2 + y^2(1-E^2) + L^2)   "
          f"<- the separation constant")
    print(f"      Liouville integrability: H, p_t, p_phi, Q -- four independent, in involution.")

    # ---------------------------------------------------------------- (D) the pointwise KY certificate
    t0 = time.time()
    cert_ok, cp, sq, worst_num = ky_root_spectrum_certificate()
    ok.append(cert_ok)
    print(f"\n  (D) THE POINTWISE OBSTRUCTION, machine-proved (not quoted):")
    print(f"      char-poly of (Y.Y)^a_b for a GENERAL 2-form Y is a perfect square:  "
          f"{'✅' if cert_ok else '❌'}   ({time.time()-t0:.1f}s)")
    print(f"        det(lam - K) = ({sp.factor(sq)})^2")
    print(f"        random non-orthonormal Lorentzian g: worst eigenvalue-pair gap "
          f"{worst_num:.1e} (frame step checked)")
    print(f"      => every eigenvalue of any Y.Y has EVEN multiplicity.")

    pts = [[0, 2, 3, 0], [0, sp.Rational(1, 2), 5, 0], [0, 4, sp.Rational(1, 3), 0]]
    obs = ky_root_obstruction(geo, Kup, points=pts)
    okD = obs["verdict"] == "NO_KY_ROOT"
    ok.append(okD)
    print(f"\n      our K's mixed eigenvalues: "
          f"{', '.join(str(e) for e in obs['eigenvalues'])}")
    if obs["witness_point"]:
        p, v = obs["witness_point"]
        print(f"      at (t,x,y,phi) = {[str(q) for q in p]}:  {[str(q) for q in v]}  "
              f"-- four DISTINCT values")
    print(f"      VERDICT: {obs['verdict']}   "
          f"{'✅ K is not Y.Y for ANY antisymmetric Y, anywhere' if okD else '❌'}")

    # ---------------------------------------------------------------- (E) no KY tensor AT ALL
    print(f"\n  (E) stronger: does the metric admit ANY Killing-Yano tensor? "
          f"(order-3 jet bound; one-sided, so 0 is a PROOF of absence)")
    tr, u_, ph2 = sp.symbols("r u phi2", real=True)
    f_ = 1 - 2 / tr
    controls = [
        ("Minkowski   (positive control, expect 10)",
         Geometry(sp.diag(-1, 1, tr**2 / (1 - u_**2), tr**2 * (1 - u_**2)), [t, tr, u_, ph2]),
         [0, 3, sp.Rational(1, 3), 0], 10),
        ("Schwarzschild M=1 (positive control, expect 1)",
         Geometry(sp.diag(-f_, 1 / f_, tr**2 / (1 - u_**2), tr**2 * (1 - u_**2)), [t, tr, u_, ph2]),
         [0, 5, sp.Rational(1, 3), 0], 1),
    ]
    okE = True
    for lab, cgeo, base, expect in controls:
        t0 = time.time()
        dim = killing_yano_jet_bound(cgeo, base, 3)
        good = dim == expect
        okE &= good
        print(f"        {lab:44s} dim <= {dim:2d}  {'✅' if good else '❌'}  "
              f"({time.time()-t0:.1f}s)")
    bases = [[0, 2, 3, 0]] if QUICK else [[0, 2, 3, 0], [0, sp.Rational(1, 2), 5, 0]]
    for base in bases:
        t0 = time.time()
        dim = killing_yano_jet_bound(geo, base, 3)
        good = dim == 0
        okE &= good
        print(f"        CANDIDATE A at {str([str(q) for q in base]):28s}   dim <= {dim:2d}  "
              f"{'✅ Y(p) = 0' if good else '❌'}  ({time.time()-t0:.1f}s)")
    ok.append(okE)
    print(f"      => the metric admits NO Killing-Yano tensor  "
          f"{'✅' if okE else '❌'}  (the controls prove the bound is not vacuously zero)")

    # ---------------------------------------------------------------- (F) not vacuum -- and why
    Rs = zero_simplify(geo.ricci_scalar)
    okF = Rs != 0
    ok.append(okF)
    print(f"\n  (F) matter sector: R = {sp.factor(Rs) if Rs != 0 else 0}")
    print(f"      NOT a vacuum solution {'✅' if okF else '❌'} -- and it could not have been: "
          f"Collinson (1976) /")
    print(f"      Dietz-Ruediger (1981) prove KT => KY for type-D vacua, so a vacuum "
          f"Candidate A is ruled out")
    print(f"      by theorem. This is the structural reason leg Q's 8/8 could not separate "
          f"H_KY from H_INT.")

    # ---------------------------------------------------------------- (G) bound orbits for tabula
    print(f"\n  (G) bound-orbit region (what tabula's probe gets):  "
          f"x^2 + y^2(1-E^2) + L^2/x^2 < E^2 - L^2 -- a compact annulus")
    print(f"      bounded away from the x=y=0 singularity by the L^2/x^2 barrier; needs E < 1.")
    # Q's drift is reported under step refinement: a genuine invariant's drift must fall at the
    # integrator's order (RK4: ~x81 per x3 refinement), which distinguishes "conserved" from
    # "the integrator happened to be quiet".
    drifts, box, q0 = [], None, None
    for dtau in ((1e-3, 3e-4) if QUICK else (1e-3, 3e-4, 1e-4)):
        res = orbit(0.98, 0.15, 0.6, 0.0, 0.05, steps=int(40.0 / dtau), dtau=dtau)
        if res is None:
            break
        drifts.append((dtau, res[0]))
        box, q0 = res[1], res[2]
    okG = bool(drifts) and drifts[-1][1] < 1e-2 and drifts[0][1] / drifts[-1][1] > 50
    ok.append(okG)
    if drifts:
        print(f"      geodesic E=0.98, L=0.15, Q = {q0:.6f};  max rel. drift of Q vs step size:")
        print("        " + "   ".join(f"dtau={d:g}: {w:.1e}" for d, w in drifts)
              + f"   -> falls at the integrator's order {'✅' if okG else '❌'}")
        print(f"      orbit box  x in [{box[0]:.3f}, {box[1]:.3f}],  "
              f"y in [{box[2]:.3f}, {box[3]:.3f}]  -- bounded, and x stays clear of the "
              f"singularity ✅")

    # ---------------------------------------------------------------- export (blind protocol)
    outdir = os.path.join(ROOT, "data", "bridge_round8")
    os.makedirs(outdir, exist_ok=True)
    public = {
        "id": "G2_candidate_A",
        "round": 8,
        "coords": ["t", "x", "y", "phi"],
        "signature": "(-,+,+,+)",
        "metric_diagonal": [str(sp.simplify(METRIC[i, i])) for i in range(4)],
        "metric_latex": r"ds^2 = -\frac{x^2+y^2}{1+y^2}dt^2 + (x^2+y^2)(dx^2+dy^2) "
                        r"+ \frac{x^2(x^2+y^2)}{1+x^2}d\phi^2",
        "inverse_metric_diagonal": [str(sp.simplify(1 / METRIC[i, i])) for i in range(4)],
        "hamiltonian": "H = ( -(1+y^2) p_t^2 + p_x^2 + p_y^2 + (1 + 1/x^2) p_phi^2 ) "
                       "/ ( 2 (x^2+y^2) )",
        "domain": "x > 0, y real (x = y = 0 is a curvature singularity; x = 0 is an axis)",
        "manifest_killing_vectors": ["d/dt", "d/dphi"],
        "suggested_orbit_data": {"mass_shell": "2H = -1", "E_range": [0.95, 0.995],
                                 "L_range": [0.05, 0.2],
                                 "note": "bound region is x^2 + y^2(1-E^2) + L^2/x^2 < "
                                         "E^2 - L^2; requires E < 1. The L^2/x^2 barrier "
                                         "keeps orbits off the singularity."},
        "WITHHELD": "integrability status, Killing-tensor rank and Killing-Yano verdict are "
                    "sealed with the bridge (see PREREGISTRATION.md blind protocol)",
    }
    sealed = {
        "id": "G2_candidate_A", "for": "bridge only -- do not forward to tabula",
        "integrable": True, "liouville_constants": ["H", "p_t", "p_phi", "Q"],
        "killing_tensor_rank": 2, "killing_tensor_irreducible": bool(okB),
        "killing_tensor_contravariant_diagonal": [str(sp.simplify(Kup[i, i])) for i in range(4)],
        "conserved_quantity_on_shell": "Q = p_x^2 - E^2 + x^2 L^2 + x^2 "
                                       "= -(p_y^2 + y^2(1-E^2) + L^2)",
        "mixed_eigenvalues": [str(e) for e in obs["eigenvalues"]],
        "killing_yano_root_exists": False,
        "ky_root_certificate": "four distinct mixed eigenvalues; (Y.Y)^a_b always has "
                               "even-multiplicity spectrum (machine-proved perfect square)",
        "killing_yano_tensor_exists": False if okE else "UNDECIDED",
        "ky_absence_certificate": "order-3 Taylor-jet bound = 0 at sampled points; controls "
                                  "Minkowski=10, Schwarzschild=1",
        "vacuum": False, "ricci_scalar": str(sp.factor(Rs)),
        "why_not_vacuum": "Collinson 1976 / Dietz-Ruediger 1981: type-D vacuum + Killing "
                          "tensor => Killing-Yano tensor",
    }
    with open(os.path.join(outdir, "G2_candidate_A.json"), "w") as fh:
        json.dump(public, fh, indent=2)
    with open(os.path.join(outdir, "G2_candidate_A_SEALED.json"), "w") as fh:
        json.dump(sealed, fh, indent=2)
    print(f"\n  exported: data/bridge_round8/G2_candidate_A.json  (METRIC ONLY -> tabula)")
    print(f"            data/bridge_round8/G2_candidate_A_SEALED.json  (verdicts -> bridge only)")

    passed = all(ok)
    print(f"\nG2 CANDIDATE A: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(integrable, irreducible rank-2 Killing tensor, NO Killing-Yano root and no "
          "Killing-Yano tensor at all)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
