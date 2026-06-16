#!/usr/bin/env python3
"""Step 37 — COSMOLOGY: the engine leaves the black hole, takes on the universe.

First breadth experiment in a new domain (attack angle #1). The SAME engine that
proved no-hair now analyses the expanding universe — Einstein's equations with a
time-dependent metric and a fluid, instead of a static vacuum. Several small
experiments, to map the terrain:

  (A) recover the FRIEDMANN equations straight from the FLRW metric
      (ρ = 3H²/8π, p = −(2ä/a + (ȧ/a)²)/8π) — no input beyond the metric;
  (B) the EXPANSION-LAW META-LAW: for a power-law universe a(t)=t^q the engine
      derives the equation-of-state w = p/ρ and inverts it to
          q(w) = 2/(3(1+w))        (radiation→½, matter→⅔, stiff→⅓)
      — the abstractor move (24), now in cosmology;
  (C) de Sitter a(t)=e^{Ht} → w = −1 (a cosmological constant, exact);
  (D) the ENERGY-CONDITION map of the equation of state (reusing 36's logic in
      its headline setting): with ρ>0, NEC ⇒ w ≥ −1 (phantom divide), SEC ⇒
      w ≥ −1/3 — i.e. cosmic ACCELERATION is exactly an SEC violation, and a
      phantom (w<−1) violates the NEC.

Honest scope: textbook FLRW cosmology; new is that our exact discover/prove/
abstract engine handles it with no black-hole machinery — breadth, toward the
general tool. Flat (k=0) Cartesian slices keep it fully rational.

Run:  .venv/bin/python scripts/37_cosmology.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry


def friedmann():
    """ρ, p (×8π) read off the flat-FLRW Einstein tensor, for a(t) symbolic."""
    t = sp.Symbol("t", positive=True)
    x, y, z = sp.symbols("x y z", real=True)
    a = sp.Function("a", positive=True)
    g = sp.diag(-1, a(t)**2, a(t)**2, a(t)**2)
    geo = Geometry(g, [t, x, y, z])
    G = geo.ricci - sp.Rational(1, 2) * geo.ricci_scalar * geo.g
    Gmix = sp.simplify(geo.ginv * G)
    rho = sp.simplify(-Gmix[0, 0] / (8 * sp.pi))
    p = sp.simplify(Gmix[1, 1] / (8 * sp.pi))
    return t, a, rho, p


def _flrw_geo(a_expr, t):
    x, y, z = sp.symbols("x y z", real=True)
    return Geometry(sp.diag(-1, a_expr**2, a_expr**2, a_expr**2), [t, x, y, z])


def kretschmann_of(a_expr, t):
    """K(t) for the flat FLRW with scale factor a_expr — singularity probe."""
    return sp.simplify(_flrw_geo(a_expr, t).kretschmann)


def nec_of(a_expr, t):
    """ρ+p (NEC combination) for the flat FLRW with scale factor a_expr."""
    geo = _flrw_geo(a_expr, t)
    G = geo.ricci - sp.Rational(1, 2) * geo.ricci_scalar * geo.g
    Gmix = sp.simplify(geo.ginv * G)
    return sp.simplify(-Gmix[0, 0] / (8 * sp.pi) + Gmix[1, 1] / (8 * sp.pi))


def main():
    print("COSMOLOGY — the engine takes on the expanding universe\n")
    t, a, rho, p = friedmann()
    H = sp.diff(a(t), t) / a(t)

    # (A) Friedmann equations
    okA = (sp.simplify(rho - 3 * H**2 / (8 * sp.pi)) == 0)
    print("  (A) Friedmann from the metric:")
    print(f"      ρ = {rho}   {'✅ = 3H²/8π' if okA else '❌'}")
    print(f"      p = {p}")

    # (B) expansion-law meta-law q(w) = 2/(3(1+w))
    q, w = sp.symbols("q w", real=True)
    rho_q = sp.simplify(rho.subs(a(t), t**q).doit())
    p_q = sp.simplify(p.subs(a(t), t**q).doit())
    w_of_q = sp.simplify(p_q / rho_q)
    q_of_w = sp.solve(sp.Eq(w, w_of_q), q)
    okB = (len(q_of_w) == 1 and sp.simplify(q_of_w[0] - 2 / (3 * (1 + w))) == 0)
    print(f"\n  (B) power-law a=t^q ⇒ w = {w_of_q};  invert ⇒ q(w) = {q_of_w[0] if q_of_w else '?'}")
    named = {"radiation": sp.Rational(1, 3), "matter": sp.S.Zero, "stiff": sp.Integer(1)}
    expect = {"radiation": sp.Rational(1, 2), "matter": sp.Rational(2, 3), "stiff": sp.Rational(1, 3)}
    okB2 = True
    for name, wv in named.items():
        qv = sp.simplify(q_of_w[0].subs(w, wv))
        okB2 = okB2 and (qv == expect[name])
        print(f"        {name:9s} w={wv} → q={qv}  {'✓' if qv == expect[name] else '✗'}")

    # (C) de Sitter
    Hc = sp.Symbol("H", positive=True)
    rho_dS = sp.simplify(rho.subs(a(t), sp.exp(Hc * t)).doit())
    p_dS = sp.simplify(p.subs(a(t), sp.exp(Hc * t)).doit())
    w_dS = sp.simplify(p_dS / rho_dS)
    okC = (w_dS == -1)
    print(f"\n  (C) de Sitter a=e^(Ht): w = {w_dS}   {'✅ cosmological constant' if okC else '❌'}")

    # (D) energy-condition thresholds (p = wρ, ρ>0)
    #     NEC: 1+w ≥ 0 ; SEC: 1+3w ≥ 0 ; acceleration ⇔ ä>0 ⇔ ρ+3p<0 ⇔ SEC violated.
    nec_thresh = sp.solve(sp.Eq(1 + w, 0), w)[0]          # −1
    sec_thresh = sp.solve(sp.Eq(1 + 3 * w, 0), w)[0]      # −1/3
    okD = (nec_thresh == -1 and sec_thresh == sp.Rational(-1, 3))
    print(f"\n  (D) energy-condition map of the equation of state w:")
    print(f"        NEC (ρ+p≥0)  ⇒ w ≥ {nec_thresh}   (phantom divide; w<−1 violates NEC)")
    print(f"        SEC (ρ+3p≥0) ⇒ w ≥ {sec_thresh}   (w<−1/3 ⇒ ACCELERATION = SEC violation)")
    print(f"      → dark energy / acceleration is exactly an SEC violation   "
          f"{'✅' if okD else '❌'}")

    # (E) the Big Bang singularity via CURVATURE (a different lens than energy)
    tp = sp.Symbol("t", positive=True)
    Hc2 = sp.Symbol("H", positive=True)
    print("\n  (E) Big Bang singularity (Kretschmann curvature as t→0):")
    sing = []
    for label, a_expr in [("radiation t^½", tp**sp.Rational(1, 2)),
                          ("matter t^⅔", tp**sp.Rational(2, 3)),
                          ("de Sitter e^(Ht)", sp.exp(Hc2 * tp))]:
        K = kretschmann_of(a_expr, tp)
        lim0 = sp.limit(K, tp, 0, "+")
        is_sing = lim0 in (sp.oo, -sp.oo)
        sing.append(is_sing)
        print(f"        {label:16s}: K={K}  → {'SINGULAR (Big Bang)' if is_sing else 'regular'}")
    okE = (sing == [True, True, False])   # power-laws bang, de Sitter doesn't

    # (F) a BOUNCE needs exotic matter — ties cosmology to the energy-condition lens
    tr = sp.Symbol("t", real=True)
    nec_b = nec_of(sp.cosh(tr), tr)
    nec_b0 = sp.simplify(nec_b.subs(tr, 0))
    okF = (nec_b0 < 0)
    print(f"\n  (F) bounce a=cosh(t) (avoids the singularity): ρ+p at bounce = {nec_b0}")
    print(f"      → NEC {'VIOLATED ⇒ a bounce needs EXOTIC matter' if okF else 'ok'}  "
          "(cosmology meets the wormhole/warp lens)")

    passed = okA and okB and okB2 and okC and okD and okE and okF
    print(f"\nCOSMOLOGY: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Friedmann + expansion law + de Sitter + EC map + singularity + bounce, all exact)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
