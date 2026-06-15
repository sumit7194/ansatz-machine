#!/usr/bin/env python3
"""Step 34 — the HAIR CRITERION: one principle behind no-hair AND charge-hair.

32/33 proved a minimally-coupled scalar adds NO hair; 28 found Maxwell adds a
Q²/r² charge term (RN). This step extracts the single structural reason and
turns it into a predictor — the engine doesn't just find/prove solutions, it
reads off WHY.

The static lapse f(r) is pinned by ONE component of the field equations: the
angular (θθ) Einstein equation,
        R_θθ − [2Λ/(n−2)] g_θθ  =  (source)_θθ.
Its left side is the universal, f-determining operator (for the canonical
r²-ansatz, (n−3)(1−f) − r f' up to the Λ term). Therefore:

    a static source adds hair to f  ⇔  its angular component (source)_θθ ≠ 0,
    and the engine reads the extra term straight off this one ODE (via dsolve).

  • scalar φ(r):   (κ ∂_aφ ∂_bφ)_θθ = ∂_θφ = 0   →  f forced to Tangherlini
                   → NO HAIR (mass only);
  • Maxwell A_t=Q/r:  T_θθ = Q²/(2r²) ≠ 0  (f-independent)  →  dsolve gives
                   f = 1 − 2M/r + Q²/r²  — RN, the charge term DERIVED.

And it PREDICTS unseen cases: a magnetic charge (never solved by this engine)
must hair the metric exactly like electric charge — T_θθ = (Q²+P²)/(2r²) → dsolve
gives dyonic RN f = 1 − 2M/r + (Q²+P²)/r², which then passes the FULL
Einstein–Maxwell verifier. (Magnetic ≡ electric in f is the structural face of
EM duality.) The lapse is fixed by ONE equation, and the full-system check
confirms that one equation was sufficient.

So no-hair and charge-hair are the SAME mechanism read two ways. Not a new
source rung (D26) — the unifying principle already latent in 28 and 32/33.

Run:  .venv/bin/python scripts/34_hair_criterion.py
"""

import importlib.util
import os
import sys

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from gr_engine import Geometry, build_ansatz_metric, R_SYM, VERIFIED

_mx = importlib.util.spec_from_file_location("mx", os.path.join(_here, "28_maxwell.py"))
mx = importlib.util.module_from_spec(_mx); _mx.loader.exec_module(mx)


def derive_lapse(angular_source, n=4, Lam=sp.S.Zero):
    """Read f(r) off the angular Einstein equation for a given angular source
    component (source)_θθ. Returns the symbolic f the engine derives via dsolve."""
    r = R_SYM
    f = sp.Function("f")
    metric, coords, _ = build_ansatz_metric(n, f(r))
    geo = Geometry(metric, coords)
    ang_eq = sp.simplify(geo.ricci[2, 2] - (2 * Lam / (n - 2)) * geo.g[2, 2]
                         - angular_source)
    return sp.simplify(sp.dsolve(sp.Eq(ang_eq, 0), f(r)).rhs)


def scalar_angular_source():
    """(κ ∂_aφ ∂_bφ)_θθ for a static φ=φ(r): identically zero."""
    r = R_SYM
    phi = sp.Function("phi")
    kappa = sp.Symbol("kappa", positive=True)
    # the θθ index: ∂_θ φ(r) = 0
    return sp.simplify(kappa * sp.diff(phi(r), sp.Symbol("x1", real=True))**2)


def maxwell_angular_source(Q, kappa=sp.Integer(2)):
    """κ T_θθ for A_t = Q/r, computed by the engine with f(r) symbolic — and it
    comes out f-INDEPENDENT (= κ Q²/(2r²)), so the angular eq is a clean ODE."""
    r = R_SYM
    f = sp.Function("f")
    metric, coords, _ = build_ansatz_metric(4, f(r))
    geo = Geometry(metric, coords)
    F = mx.faraday([Q / r, 0, 0, 0], coords)
    T = mx.em_stress(geo, F)
    Tang = sp.simplify(T[2, 2])
    return kappa * Tang, (not Tang.has(f(r)))


def dyonic_field(Q, P):
    """Electric A_t=Q/r PLUS a magnetic monopole A_φ=−P cosθ (so F_θφ=P sinθ)."""
    r = R_SYM
    f = sp.Function("f")
    metric, coords, _ = build_ansatz_metric(4, f(r))
    th = coords[2]
    return [Q / r, 0, 0, -P * sp.cos(th)], metric, coords


def dyonic_angular_source(Q, P, kappa=sp.Integer(2)):
    """κ T_θθ for the dyonic field, by the engine with f(r) symbolic. It comes
    out κ(Q²+P²)/(2r²) — f- AND θ-independent — so magnetic charge enters the
    angular ODE exactly like electric charge (the structural face of EM duality)."""
    A, metric, coords = dyonic_field(Q, P)
    geo = Geometry(metric, coords)
    F = mx.faraday(A, coords)
    Tang = sp.simplify(mx.em_stress(geo, F)[2, 2])
    f = sp.Function("f")
    clean = (not Tang.has(f(R_SYM))) and (not Tang.has(coords[2]))
    return kappa * Tang, clean


def main():
    r = R_SYM
    Q, M = sp.symbols("Q M", positive=True)
    C1 = sp.Symbol("C1")
    print("THE HAIR CRITERION — why scalars give no hair but charge does\n")

    vacuum_f = 1 + C1 / r          # Tangherlini 4D, Λ=0: mass only

    # 1) scalar: zero angular source ⇒ no hair
    s_src = scalar_angular_source()
    f_scalar = derive_lapse(s_src)
    scalar_hairless = sp.simplify(f_scalar - vacuum_f) == 0
    print(f"  scalar φ(r):   (source)_θθ = {s_src}")
    print(f"     ⇒ angular eq forces f = {f_scalar}")
    print(f"     hair term beyond mass: {sp.simplify(f_scalar - vacuum_f)}   "
          f"→ {'NO HAIR ✅' if scalar_hairless else 'unexpected ❌'}")

    # 2) Maxwell: nonzero angular source ⇒ the charge term, derived
    m_src, f_indep = maxwell_angular_source(Q)
    f_maxwell = derive_lapse(m_src)
    hair_term = sp.simplify(f_maxwell - vacuum_f)
    maxwell_hairy = (hair_term == Q**2 / r**2)
    print(f"\n  Maxwell A_t=Q/r:   (source)_θθ = {m_src}   "
          f"(f-independent: {'yes' if f_indep else 'NO'})")
    print(f"     ⇒ angular eq forces f = {f_maxwell}")
    print(f"     hair term beyond mass: {hair_term}   "
          f"→ {'CHARGE HAIR (RN), DERIVED ✅' if maxwell_hairy else 'unexpected ❌'}")

    # 3) PREDICT an unseen case. The criterion says hair = whatever the angular
    #    source injects — so a magnetic charge (never solved by our engine) should
    #    hair the metric exactly like electric charge (Q²→Q²+P², dyonic RN). Derive
    #    it from the angular eq, then confirm it solves the FULL system (the lapse
    #    was fixed by ONE equation — this checks the one-equation criterion is sound).
    P = sp.Symbol("P", positive=True)
    d_src, d_clean = dyonic_angular_source(Q, P)
    f_dyon = derive_lapse(d_src)
    predicted = sp.simplify(f_dyon - (1 + C1 / r + (Q**2 + P**2) / r**2)) == 0
    A_dyon, _, _ = dyonic_field(Q, P)
    metric, coords, _ = build_ansatz_metric(4, f_dyon.subs(C1, -2 * M))
    v, _d = mx.verify_em(metric, coords, A_dyon, sp.Integer(2), params=(M, Q, P))
    full_ok = (v == VERIFIED)
    print(f"\n  PREDICT (magnetic charge — unseen by the engine): (source)_θθ = {d_src}")
    print(f"     ⇒ angular eq forces f = {f_dyon}")
    print(f"     criterion predicted Q²→Q²+P² (dyonic RN): {'✅' if predicted else '❌'}")
    print(f"     and that angular-derived f solves the FULL Einstein–Maxwell system: "
          f"{v}  {'✅ one-eq criterion sound' if full_ok else '❌'}")

    print("\n  criterion: a static source adds hair ⇔ its angular Einstein")
    print("  component (source)_θθ ≠ 0; the engine reads the extra term off that")
    print("  one ODE. No-hair (32/33) and charge-hair (28) are one mechanism, and")
    print("  it PREDICTS new cases (magnetic charge → dyonic RN, verified).")

    passed = scalar_hairless and maxwell_hairy and f_indep and d_clean and predicted and full_ok
    print(f"\nHAIR CRITERION: {'PASSED ✅' if passed else 'FAILED ❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
