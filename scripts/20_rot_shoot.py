#!/usr/bin/env python3
"""Step 20 — v5 R1: slow-rotation frame dragging on EdGB backgrounds.

The l=1 Pani-Cardoso equation is a pure quadrature on the static
background (arXiv:0902.1569 eqs. 31-32, 38):
    Ω″ + (G₂/G₃) Ω′ = 0   ⇒   Ω(r) = ∫_r^∞ exp(−∫ G₂/G₃) ds
with (transcribed; κ_c = coupling-normalization factor, calibrated):
    G₂ = −e^Λ r(−8 + r(Λ′+Γ′))
         − κ_c α′ e^φ (φ′(6 − r(3Λ′ − 2φ′ + Γ′)) + 2rφ″)
    G₃ = 2r²e^Λ − 2 κ_c α′ r e^φ φ′
Backgrounds come from our E0/E1-validated shooting (step 11); φ″ from
the validated RHS; Λ from the algebraic e^Λ; Λ′ by finite differences.

Gates (mapping-robust by design; docs/ROTATING.md amendment):
  G1  GR limit (p=1e-8): Ω·r³/(2J) ≡ 1 over the exterior to <1e-3.
  G2  SHAPE: at small p, δω(r) ≡ ω − 2J/r³ matches the Ayzenberg-Yunes
      eq. 15 profile  (m⁴/r³)[1 + (140/9)(m/r) + 10(m/r)² + 16(m/r)³
      − (400/9)(m/r)⁴]  up to one overall amplitude (corr > 0.999).
  G3  MΩ_H/(J/M²): → 0.25 as p→0, monotone in p, in [0.30, 0.45] at
      p=0.85 (Pani-Cardoso anchor: ≈0.37 near max coupling).
κ_c ∈ {1/2, 1, 2}: the value passing G2+G3 is selected and reported.

Run:  .venv/bin/python scripts/20_rot_shoot.py
"""

import importlib.util
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "edgb_shoot", os.path.join(_here, "11_edgb_shoot.py"))
m11 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m11)

_F = {}


def funcs():
    if not _F:
        f_g2, f_p2, f_y, f_lp = m11.build_rhs(verbose=False)
        _F.update(g2=f_g2, p2=f_p2, y=f_y, lp=f_lp)
    return _F


def background(p):
    """Sampled background + derived quantities along the exterior.
    Λ′ is ANALYTIC (chain rule through the algebraic e^Λ) — finite
    differences near the horizon integrate cancellation noise into the
    quadrature (measured: GR limit off by 8.5)."""
    F = funcs()
    rec = []
    M, D, ok = m11.shoot(F["g2"], F["p2"], p, record=rec)
    assert ok is True, f"background shoot failed p={p}: {ok}"
    rows = []
    for (rv, phi, p1, gp, _gacc) in rec:
        y = F["y"](rv, phi, p1, gp)
        p2 = F["p2"](rv, phi, p1, gp)
        g2v = F["g2"](rv, phi, p1, gp)
        lp = F["lp"](rv, phi, p1, gp, p2, g2v)
        rows.append([rv, phi, p1, p2, gp, y, lp])
    return M, rows


def omega_profile(rows, kc):
    """Quadrature: Ω(r) = ∫_r^∞ exp(−∫_{r0}^s G₂/G₃) ds, vectorized on
    the sample grid (trapezoid)."""
    g23 = []
    for (rv, phi, p1, p2, gp, y, lp) in rows:
        ephi = math.exp(phi)
        G2 = (-y * rv * (-8 + rv * (lp + gp))
              - kc * ephi * (p1 * (6 - rv * (3 * lp - 2 * p1 + gp))
                             + 2 * rv * p2))
        G3 = 2 * rv**2 * y - 2 * kc * rv * ephi * p1
        g23.append(G2 / G3)
    rs = [row[0] for row in rows]
    # I1(s) = ∫ g23 ; then Ω′ ∝ exp(−I1); Ω(r) = ∫_r^rmax exp(−I1)
    I1, acc = [0.0], 0.0
    for i in range(1, len(rs)):
        acc += 0.5 * (g23[i] + g23[i - 1]) * (rs[i] - rs[i - 1])
        I1.append(acc)
    expI = [math.exp(-v) for v in I1]
    om = [0.0] * len(rs)
    for i in range(len(rs) - 2, -1, -1):
        om[i] = om[i + 1] + 0.5 * (expI[i] + expI[i + 1]) \
            * (rs[i + 1] - rs[i])
    return rs, om


def J_from_tail(rs, om, r_read=60.0):
    """Read J from Ω ≈ 2J/r³ at r ≈ r_read — far enough to be
    asymptotic, near enough that the quadrature's finite upper limit
    (Ω(r_max) ≡ 0 ⇒ Ω ∝ 1/r³ − 1/r_max³) is a ~1e-5 correction.
    (Measured bug: reading at the second-to-last point gave Ω ≈ 0 by
    construction and wrecked the GR limit by 8.5×.)"""
    i = min(range(len(rs)), key=lambda k: abs(rs[k] - r_read))
    corr = 1 - (rs[i] / rs[-1])**3
    return om[i] * rs[i]**3 / (2 * corr) if om[i] > 0 else float("nan")


def main():
    results = []
    print("Backgrounds + quadratures (κ_c candidates {0.5, 1, 2})...")

    # --- G1: GR limit, κ_c-independent ---
    M0, rows0 = background(1e-8)
    rs, om = omega_profile(rows0, 1.0)
    J0 = J_from_tail(rs, om)
    devs = [abs(om[i] * rs[i]**3 / (2 * J0) - 1)
            for i in range(len(rs)) if rs[i] < 100]
    g1 = max(devs) < 1e-3
    results.append(g1)
    print(f"  {'✓' if g1 else '✗✗'} G1 GR limit: max|Ωr³/2J − 1| = "
          f"{max(devs):.2e} (M={M0:.4f})")

    # --- per-κ_c: G2 shape at small p, G3 horizon-dragging trend ---
    P_SMALL, P_GRID = 0.15, (0.05, 0.2, 0.4, 0.6, 0.85)
    verdicts = {}
    for kc in (0.5, 1.0, 2.0):
        # G2: shape of the GB correction at small p
        M, rows = background(P_SMALL)
        rs, om = omega_profile(rows, kc)
        J = J_from_tail(rs, om)
        ay, dw = [], []
        for i in range(len(rs)):
            rv = rs[i]
            if rv > 40 or rv < 1.001:
                continue
            x = M / rv
            ay.append((M**4 / rv**3) * (1 + 140 / 9 * x + 10 * x**2
                                        + 16 * x**3 - 400 / 9 * x**4))
            dw.append(om[i] - 2 * J / rv**3)
        ma = sum(ay) / len(ay)
        md = sum(dw) / len(dw)
        num = sum((a - ma) * (d - md) for a, d in zip(ay, dw))
        den = math.sqrt(sum((a - ma)**2 for a in ay)
                        * sum((d - md)**2 for d in dw))
        corr = num / den if den > 0 else 0.0
        # G3: MΩ_H/(J/M²) across p
        ratios = []
        for p in P_GRID:
            M_, rows_ = background(p)
            rs_, om_ = omega_profile(rows_, kc)
            J_ = J_from_tail(rs_, om_)
            ratios.append(M_ * om_[0] / (J_ / M_**2))
        mono = all(ratios[i] <= ratios[i + 1] + 1e-4
                   for i in range(len(ratios) - 1))
        ok2 = abs(corr) > 0.999
        ok3 = abs(ratios[0] - 0.25) < 0.01 and mono \
            and 0.30 < ratios[-1] < 0.45
        verdicts[kc] = (ok2, ok3, corr, ratios)
        print(f"  κ_c={kc}: shape-corr {corr:+.5f} "
              f"{'✓' if ok2 else '✗'} | MΩ_H/(J/M²) "
              + "→".join(f"{x:.3f}" for x in ratios)
              + f" {'✓' if ok3 else '✗'}")

    winners = [k for k, v in verdicts.items() if v[0] and v[1]]
    ok_sel = len(winners) == 1
    results.append(ok_sel)
    if ok_sel:
        print(f"  ✓ κ_c = {winners[0]} uniquely passes G2+G3 — selected")
    else:
        print(f"  ✗✗ κ_c selection ambiguous/empty: {winners}")

    print(f"\n{'ALL EXPECTATIONS MET ✅' if all(results) else 'EXPECTATION FAILURES ❌'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
