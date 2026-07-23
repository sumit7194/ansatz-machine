#!/usr/bin/env python3
"""Step 121 — BRIDGE ROUND 8 / G2 CANDIDATE B: integrable, with a TRANSCENDENTAL invariant.

G2's second adversarial metric. Candidate A (§120) is integrable + polynomial + KY-free, which
separates H_KY from H_INT. Candidate B must be integrable but NOT polynomial: its conserved
quantity is transcendental in the momenta, with every polynomial invariant of degree <= 4
excluded. That separates H_POLY.

THE OBSTRUCTION FIRST -- because it says exactly what Candidate B has to look like.

  THEOREM (the momentum grading). Let H = (1/2) g^{ab}(x) p_a p_b be a geodesic Hamiltonian and
  let F be a first integral ANALYTIC in the momenta near p = 0. Expand F = sum_k F_k with F_k
  homogeneous of degree k in p. Then {H, F_k} is homogeneous of degree k+1, so the degrees do
  not mix and each F_k is SEPARATELY a first integral -- that is, a Killing tensor of rank k.

  So for a genuine geodesic flow there is no such thing as an "essentially transcendental"
  invariant that is analytic in p: its homogeneous parts are polynomial invariants, and if F is
  independent of H then some F_k is too. A transcendental geodesic invariant must therefore be
  NON-ANALYTIC in the momenta. That is not a loophole we exploit, it is the only door there is.

THE METRIC (identified in the literature, not invented here):
  A. Galajinsky, "Some metrics admitting nonpolynomial first integrals of the geodesic
  equation", Phys. Lett. B 820 (2021) 136483, arXiv:2106.09335 -- eqs. (11)-(13), the Bianchi
  type-IV example. The 2D Riemannian metric

      ds^2 = [ (1+y^2) dx^2 - 2(1 + y(x+y)) dx dy + (1+k^2+(x+y)^2) dy^2 ]
             / ( x^2 + k^2 (1+y^2) )

  has the geodesic Hamiltonian H = (1/2)[ (1+k^2+(x+y)^2) p_x^2 + 2(1+y(x+y)) p_x p_y
  + (1+y^2) p_y^2 ] and the exactly conserved

      I = p_y / p_x - ln p_x .

  ln p_x is precisely the predicted non-analyticity: I has a branch point at p_x = 0, which is
  why the grading theorem does not apply to it. Conservation of I is verified here symbolically
  ({I,H} = 0 exactly), not taken on trust.

THE 4D LORENTZIAN SPACETIME. Galajinsky's eq. (62): ds^2 -> ds^2 - 2 dt dv adds two null
directions, giving a genuine 4D Lorentzian metric whose geodesic flow still conserves I, plus
p_t and p_v. So {H_4, p_t, p_v, I} are four independent constants in involution -- Liouville
integrable, with the hidden one transcendental.

WHAT IS EXCLUDED. killing_tensor_jet_bound counts polynomial invariants of each degree
rigorously (one-sided jet bound; flat 2D returns the exact known 3, 6, 10, 15). On this metric
ranks 1..4 collapse to {0, 1, 0, 1}: the only survivors are g and g*g, i.e. H and H^2, which
carry no information beyond H itself. NO polynomial invariant of degree <= 4 exists.

ONE HONEST CAVEAT, FLAGGED FOR THE BRIDGE. Unlike Candidate A, the 4D lift is NOT Killing-Yano
empty: its Killing-Yano space is exactly 2-dimensional, spanned by dt ^ dv and the area form of
the (x,y) block. Both are COVARIANTLY CONSTANT and both square to REDUCIBLE Killing tensors
(the flat null block and g_2), so neither carries a hidden constant of motion -- and both are
forced by the product structure, so every metric (2D Riemannian) - 2 dt dv has them whether or
not it is integrable. Candidate B's HIDDEN symmetry is neither polynomial nor Killing-Yano;
but if the frozen G2 table is read as "admits any Killing-Yano tensor at all", that reading is
not discriminating here. Reported, not resolved: the gate is the bridge's to apply.

BLIND PROTOCOL: writes data/bridge_round8/G2_candidate_B.json (metric only, for tabula) and
.../G2_candidate_B_SEALED.json (verdicts, for the bridge alone).

Repro:  .venv/bin/python scripts/121_candidate_B_transcendental.py [--quick]
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry
from killing_yano import killing_tensor_jet_bound, killing_yano_jet_bound

QUICK = "--quick" in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

x, y, t, v = sp.symbols("x y t v", real=True)
px, py, pt, pv = sp.symbols("p_x p_y p_t p_v", real=True)
KAPPA = sp.Integer(1)                      # kappa = 1 (Galajinsky's free parameter)

GUP2 = sp.Matrix([[1 + KAPPA**2 + (x + y)**2, 1 + y * (x + y)],
                  [1 + y * (x + y), 1 + y**2]])
G2 = sp.simplify(GUP2.inv())
# 4D Lorentzian: ds^2 - 2 dt dv  (Galajinsky eq. 62), coords (t, v, x, y)
G4 = sp.zeros(4, 4)
G4[0, 1] = G4[1, 0] = -1
for a in range(2):
    for b in range(2):
        G4[2 + a, 2 + b] = G2[a, b]
COORDS4 = [t, v, x, y]

I_INV = py / px - sp.log(px)


def pb(f, g, pairs):
    return sum(sp.diff(f, q) * sp.diff(g, p) - sp.diff(f, p) * sp.diff(g, q) for q, p in pairs)


def grading_theorem_check(max_deg=5):
    """MACHINE CHECK of the grading step: for a general metric and a general homogeneous
    degree-k F_k, {H, F_k} is homogeneous of degree k+1 in the momenta -- verified with the
    Euler operator p.d/dp, which is what makes the degrees decouple."""
    a, b, c = [sp.Function(f)(x, y) for f in ("gxx", "gxy", "gyy")]
    H = (a * px**2 + 2 * b * px * py + c * py**2) / 2
    pairs = ((x, px), (y, py))
    out = []
    for k in range(0, max_deg + 1):
        Fk = sum(sp.Function(f"f{k}_{j}")(x, y) * px**(k - j) * py**j for j in range(k + 1))
        br = sp.expand(pb(H, Fk, pairs))
        euler = sp.expand(px * sp.diff(br, px) + py * sp.diff(br, py))
        out.append((k, sp.simplify(euler - (k + 1) * br) == 0))
    return out


def main():
    print(__doc__.split("Repro:")[0])
    ok = []

    # ---------------------------------------------------------------- (A) the grading theorem
    checks = grading_theorem_check()
    okA = all(good for _, good in checks)
    ok.append(okA)
    print(f"  (A) THE MOMENTUM GRADING, machine-checked for a GENERAL 2D metric:")
    print(f"      {{H, F_k}} is homogeneous of degree k+1 for k = "
          f"{', '.join(str(k) for k, _ in checks)}:  {'✅' if okA else '❌'}")
    print(f"      => every first integral of a geodesic flow that is ANALYTIC in p splits into")
    print(f"         polynomial (Killing-tensor) integrals. A transcendental one MUST be")
    print(f"         non-analytic in p. This is the obstruction, and it dictates the answer.")

    # ---------------------------------------------------------------- (B) the invariant
    H2 = (GUP2[0, 0] * px**2 + 2 * GUP2[0, 1] * px * py + GUP2[1, 1] * py**2) / 2
    br2 = sp.simplify(pb(I_INV, H2, ((x, px), (y, py))))
    okB = br2 == 0
    ok.append(okB)
    print(f"\n  (B) Galajinsky's type-IV metric (arXiv:2106.09335 eqs. 11-13), kappa = {KAPPA}:")
    print(f"      I = p_y/p_x - ln(p_x);   {{I, H}} = {br2}   "
          f"{'✅ EXACTLY conserved (symbolic, not numeric)' if okB else '❌'}")
    print(f"      non-analytic in p exactly as the theorem requires: ln has a branch point at "
          f"p_x = 0.")
    print(f"      det g^ij = {sp.factor(sp.simplify(GUP2.det()))}  (Galajinsky: x^2 + k^2(1+y^2)"
          f"), so the metric is regular for kappa != 0.")

    # ---------------------------------------------------------------- (C) the 4D Lorentzian lift
    H4 = sum(sp.Matrix(G4).inv()[i, j] * [pt, pv, px, py][i] * [pt, pv, px, py][j]
             for i in range(4) for j in range(4)) / 2
    pairs4 = ((t, pt), (v, pv), (x, px), (y, py))
    br4 = sp.simplify(pb(I_INV, H4, pairs4))
    ev = sp.Matrix(G4).subs({x: sp.Rational(1, 3), y: sp.Rational(2, 5)}).eigenvals()
    sig = sorted(sp.sign(sp.nsimplify(k)) for k, m in ev.items() for _ in range(m))
    okC = br4 == 0 and sig == [-1, 1, 1, 1]
    ok.append(okC)
    print(f"\n  (C) the 4D Lorentzian spacetime (Galajinsky eq. 62):  ds^2_4 = ds^2_2 - 2 dt dv")
    print(f"      signature at a sample point: {sig}  "
          f"{'✅ (-,+,+,+)' if sig == [-1,1,1,1] else '❌'}")
    print(f"      {{I, H_4}} = {br4};  {{p_t, H_4}} = "
          f"{sp.simplify(pb(pt, H4, pairs4))};  {{p_v, H_4}} = "
          f"{sp.simplify(pb(pv, H4, pairs4))}   {'✅' if okC else '❌'}")
    print(f"      => Liouville integrable on 4 d.o.f. with H_4, p_t, p_v, I -- the hidden "
          f"constant is TRANSCENDENTAL.")

    # ---------------------------------------------------------------- (D) polynomial invariants excluded
    print(f"\n  (D) polynomial invariants of degree <= 4, EXCLUDED (rigorous one-sided jet "
          f"bounds):")
    X_, Y_ = sp.symbols("X_ctrl Y_ctrl", real=True)
    flat = Geometry(sp.diag(1, 1), [X_, Y_])
    ctrl = [killing_tensor_jet_bound(flat, [sp.Rational(1, 3), sp.Rational(2, 5)], rk, rk + 3)
            for rk in (1, 2, 3, 4)]
    okD = ctrl == [3, 6, 10, 15]
    print(f"      control -- flat 2D, ranks 1..4: {ctrl}  (exact known dims 3, 6, 10, 15)  "
          f"{'✅' if okD else '❌'}")
    geo2 = Geometry(G2, [x, y])
    base = [sp.Integer(1), sp.Integer(2)]
    orders = {1: 4, 2: 6, 3: 8, 4: 10}
    expect = {1: 0, 2: 1, 3: 0, 4: 1}
    trivial = {1: "no Killing vectors", 2: "g only  (i.e. H)", 3: "none",
               4: "g*g only  (i.e. H^2)"}
    if QUICK:
        orders = {1: 4, 2: 6, 3: 8}
    for rk in sorted(orders):
        t0 = time.time()
        dim = killing_tensor_jet_bound(geo2, base, rk, orders[rk])
        good = dim == expect[rk]
        okD &= good
        print(f"      Candidate B rank {rk} (jet order {orders[rk]:2d}): dim <= {dim}   "
              f"[{trivial[rk]}]  {'✅' if good else '❌'}   ({time.time()-t0:.1f}s)")
    if QUICK:
        print(f"      (--quick: rank 4 skipped; it needs jet order 10 and ~70 s)")
    ok.append(okD)
    print(f"      => the ONLY polynomial invariants of degree <= 4 are H and H^2, which are "
          f"functions of H.")
    print(f"         No hidden polynomial invariant exists up to degree 4.  "
          f"{'✅' if okD else '❌'}")

    # ---------------------------------------------------------------- (E) the Killing-Yano sector
    # This is the one place Candidate B is NOT simply "KY-free", and the honest statement
    # matters for how the bridge reads a legibility verdict, so it is pinned down exactly
    # rather than reported as a bound.
    t0 = time.time()
    geo4 = Geometry(G4, COORDS4)
    kydim = killing_yano_jet_bound(geo4, [0, 0, sp.Integer(1), sp.Integer(2)], 3)
    exhibited, gi4 = [], G4.inv()
    Y1 = sp.zeros(4, 4)
    Y1[0, 1], Y1[1, 0] = 1, -1                                   # dt ^ dv
    area = sp.sqrt(sp.simplify(G2.det()))
    Y2 = sp.zeros(4, 4)
    Y2[2, 3], Y2[3, 2] = area, -area                             # the 2D block's area form
    Gam = geo4.christoffel
    for lab, Y in (("dt ^ dv", Y1), ("area form of the (x,y) block", Y2)):
        bad = 0
        for a in range(4):
            for b in range(4):
                for c in range(4):
                    e = sp.diff(Y[b, c], COORDS4[a])
                    for f in range(4):
                        e -= Gam[f][a][b] * Y[f, c] + Gam[f][a][c] * Y[b, f]
                    if sp.simplify(e) != 0:
                        bad += 1
        exhibited.append((lab, bad == 0, sp.simplify(Y * gi4 * Y.T)))
    n_exh = sum(1 for _, par, _ in exhibited if par)
    okE = kydim == n_exh == 2
    ok.append(okE)
    print(f"\n  (E) the Killing-Yano sector of the 4D lift -- determined EXACTLY, not bounded "
          f"({time.time()-t0:.1f}s):")
    print(f"      jet bound: dim <= {kydim};  and {n_exh} are exhibited explicitly, so "
          f"dim = {kydim} exactly  {'✅' if okE else '❌'}")
    for lab, par, sq in exhibited:
        red = "the flat null block g_4 - g_2" if lab.startswith("dt") else "the 2D block metric g_2"
        print(f"        Y = {lab:30s} nabla Y = 0 (COVARIANTLY CONSTANT) "
              f"{'✅' if par else '❌'};  Y.Y = {red}")
    print(f"      Both squares are REDUCIBLE Killing tensors, so neither Killing-Yano tensor")
    print(f"      produces a hidden constant of motion. They are forced by the product")
    print(f"      structure: ANY metric of the form (2D Riemannian) - 2 dt dv carries exactly")
    print(f"      these two parallel 2-forms, integrable or not -- so 'admits a Killing-Yano")
    print(f"      tensor' does not discriminate inside this family. THE BRIDGE SHOULD NOTE THIS")
    print(f"      when applying the frozen G2 table: Candidate B's HIDDEN symmetry is neither")
    print(f"      polynomial nor Killing-Yano, but the spacetime is not KY-empty in the naive "
          f"sense.")

    # ---------------------------------------------------------------- (F) numeric confirmation
    print(f"\n  (F) numeric cross-check on real trajectories (the §97/§98 instrument's "
          f"complement):")
    res = numeric_check(steps=4000 if QUICK else 20000)
    okF = res is not None and res[0] < 1e-8
    ok.append(okF)
    if res:
        drift, pxmin, pxmax = res
        print(f"      I conserved along an integrated geodesic to rel. {drift:.1e}  "
              f"{'✅' if okF else '❌'}")
        print(f"      p_x stayed in [{pxmin:.4f}, {pxmax:.4f}] -- strictly positive, so ln p_x "
              f"is single-valued along the flow")
        print(f"      (conservation of I itself forbids p_x from reaching 0: I -> +inf there).")

    # ---------------------------------------------------------------- export (blind protocol)
    outdir = os.path.join(ROOT, "data", "bridge_round8")
    os.makedirs(outdir, exist_ok=True)
    public = {
        "id": "G2_candidate_B", "round": 8,
        "coords": ["t", "v", "x", "y"], "signature": "(-,+,+,+)",
        "metric_matrix": [[str(sp.simplify(G4[i, j])) for j in range(4)] for i in range(4)],
        "metric_note": "ds^2 = ds^2_2(x,y) - 2 dt dv, with ds^2_2 the 2D block below",
        "metric_2d_inverse": [[str(GUP2[i, j]) for j in range(2)] for i in range(2)],
        "hamiltonian": "H_4 = -p_t p_v + ( (2+(x+y)^2) p_x^2 + 2(1+y(x+y)) p_x p_y "
                       "+ (1+y^2) p_y^2 ) / 2",
        "kappa": 1,
        "domain": "all x, y (det g^ij = x^2 + 1 + y^2 > 0); probe with p_x > 0",
        "manifest_killing_vectors": ["d/dt", "d/dv"],
        "suggested_orbit_data": {"mass_shell": "2H_4 = -1 (or 0 for null)",
                                 "note": "the 2D (x,y) block decouples; sample p_x > 0. "
                                         "p_t, p_v are free constants."},
        "WITHHELD": "integrability status, invariant, Killing-tensor and Killing-Yano verdicts "
                    "are sealed with the bridge (PREREGISTRATION.md blind protocol)",
    }
    sealed = {
        "id": "G2_candidate_B", "for": "bridge only -- do not forward to tabula",
        "source": "A. Galajinsky, Phys. Lett. B 820 (2021) 136483, arXiv:2106.09335, "
                  "Bianchi type-IV example, eqs. (11)-(13) and (62). IDENTIFIED from the "
                  "literature, not invented here.",
        "integrable": True, "liouville_constants": ["H_4", "p_t", "p_v", "I"],
        "invariant": "I = p_y/p_x - ln(p_x)", "invariant_polynomial_in_momenta": False,
        "invariant_analytic_in_momenta": False,
        "poisson_bracket_with_H_verified_symbolically": bool(okB and okC),
        "polynomial_invariants_degree_le_4": "NONE beyond H and H^2",
        "killing_tensor_jet_dims_rank_1_to_4": "{0, 1, 0, 1} (i.e. nothing, g, nothing, g*g)",
        "killing_yano_space_dimension": 2,
        "killing_yano_detail": "EXACTLY 2, both COVARIANTLY CONSTANT: dt^dv and the area form "
                               "of the (x,y) block. Their squares are the reducible Killing "
                               "tensors g_4 - g_2 and g_2, so neither gives a hidden constant. "
                               "They are forced by the product structure -- every metric "
                               "(2D Riemannian) - 2dtdv has them, integrable or not. The "
                               "HIDDEN symmetry of Candidate B is neither polynomial nor "
                               "Killing-Yano.",
        "why_transcendental_is_forced": "grading theorem: an integral analytic in p splits into "
                                        "polynomial Killing-tensor integrals, so a "
                                        "transcendental one must be non-analytic in p -- here "
                                        "via ln p_x.",
    }
    with open(os.path.join(outdir, "G2_candidate_B.json"), "w") as fh:
        json.dump(public, fh, indent=2)
    with open(os.path.join(outdir, "G2_candidate_B_SEALED.json"), "w") as fh:
        json.dump(sealed, fh, indent=2)
    print(f"\n  exported: data/bridge_round8/G2_candidate_B.json  (METRIC ONLY -> tabula)")
    print(f"            data/bridge_round8/G2_candidate_B_SEALED.json  (verdicts -> bridge only)")

    passed = all(ok)
    print(f"\nG2 CANDIDATE B: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Liouville integrable with a TRANSCENDENTAL invariant; no polynomial invariant of "
          "degree <= 4; the only Killing-Yano tensors are two covariantly constant ones whose "
          "squares are reducible)")
    return 0 if passed else 1


def numeric_check(steps=20000, h=2e-4):
    """Integrate a geodesic of the 2D block and watch I = p_y/p_x - ln p_x."""
    import math
    f = sp.lambdify((x, y, px, py),
                    [sp.diff(HAM2, px), sp.diff(HAM2, py),
                     -sp.diff(HAM2, x), -sp.diff(HAM2, y)], "math")
    Ifun = sp.lambdify((px, py), I_INV, "math")
    s = [0.3, -0.4, 0.9, 0.35]
    i0, worst = Ifun(s[2], s[3]), 0.0
    lo = hi = s[2]
    for _ in range(steps):
        k1 = f(*s)
        k2 = f(*[s[i] + h / 2 * k1[i] for i in range(4)])
        k3 = f(*[s[i] + h / 2 * k2[i] for i in range(4)])
        k4 = f(*[s[i] + h * k3[i] for i in range(4)])
        s = [s[i] + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(4)]
        if s[2] <= 1e-9:
            break
        lo, hi = min(lo, s[2]), max(hi, s[2])
        worst = max(worst, abs(Ifun(s[2], s[3]) - i0) / max(1e-12, abs(i0)))
    return worst, lo, hi


HAM2 = (GUP2[0, 0] * px**2 + 2 * GUP2[0, 1] * px * py + GUP2[1, 1] * py**2) / 2


if __name__ == "__main__":
    raise SystemExit(main())
