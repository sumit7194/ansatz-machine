#!/usr/bin/env python3
"""Step 46 — NUMERIC CURVATURE: do what symbolic can't (Kerr–de Sitter).

The symbolic engine (gr_engine) is exact but its Ricci can OOM on the heaviest
off-diagonal metrics — Kerr–de Sitter is the wall (the symbolic residual never
finishes building). `numeric_curvature.py` computes the Ricci by finite differences
instead: no symbolic blow-up, milliseconds per point, pure Python.

This battery validates it: the numeric R_ab − Λ g_ab vanishes (to FD precision) for
  • Schwarzschild   (vacuum, Λ=0),
  • Kerr            (vacuum, Λ=0, off-diagonal, rational u=cosθ),
  • KERR–DE SITTER  (vacuum + Λ — THE case symbolic can't reduce),
and a deliberately WRONG Δ_r for Kerr–dS gives a large residual (so it's a real
test, not always-zero). This is the tool that unlocks off-diagonal discovery
(e.g. Kerr–dS) without the VM.

Run:  .venv/bin/python scripts/46_numeric_curvature.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from numeric_curvature import vacuum_lambda_residual

M, a = 1.0, 0.5


def schwarzschild(x):
    t, r, th, ph = x
    f = 1 - 2 * M / r
    return [[-f, 0, 0, 0], [0, 1 / f, 0, 0], [0, 0, r * r, 0], [0, 0, 0, r * r * math.sin(th)**2]]


def kerr(x):                       # rational u = cosθ form
    t, r, u, ph = x
    s2 = 1 - u * u
    Sig = r * r + a * a * u * u
    D = r * r - 2 * M * r + a * a
    g = [[0.0] * 4 for _ in range(4)]
    g[0][0] = -(D - a * a * s2) / Sig
    g[0][3] = g[3][0] = -a * s2 * (r * r + a * a - D) / Sig
    g[1][1] = Sig / D
    g[2][2] = Sig / s2
    g[3][3] = s2 * ((r * r + a * a)**2 - D * a * a * s2) / Sig
    return g


def kerr_ds_factory(Dr):
    """Kerr–de Sitter (Carter form), radial function Dr(r), with Λ-fixed angular parts."""
    L = 0.2

    def g_metric(x):
        t, r, u, ph = x
        s2 = 1 - u * u
        Sig = r * r + a * a * u * u
        Du = 1 + L * a * a * u * u / 3
        Xi = 1 + L * a * a / 3
        D = Dr(r)
        g = [[0.0] * 4 for _ in range(4)]
        g[0][0] = -(D - a * a * s2 * Du) / Sig
        g[0][3] = g[3][0] = a * s2 / (Sig * Xi) * (D - Du * (r * r + a * a))
        g[1][1] = Sig / D
        g[2][2] = Sig / (Du * s2)
        g[3][3] = s2 / (Sig * Xi * Xi) * (-D * a * a * s2 + Du * (r * r + a * a)**2)
        return g
    return g_metric, L


def main():
    print("NUMERIC CURVATURE — finite-difference Ricci (does what symbolic can't)\n")
    # 3rd coord (θ for Schwarzschild, u=cosθ for Kerr/Kerr-dS) kept away from the axis
    pts = [[0.0, 4.0, 0.5, 0.4], [0.0, 5.0, 0.3, 0.4], [0.0, 6.0, 0.7, 0.4], [0.0, 8.0, 0.85, 0.4]]

    def worst(gm, Lam):
        return max(vacuum_lambda_residual(gm, p, Lam) for p in pts)

    w_sch = worst(schwarzschild, 0.0)
    w_kerr = worst(kerr, 0.0)
    L = 0.2
    Dr_correct = lambda r: (r * r + a * a) * (1 - L * r * r / 3) - 2 * M * r
    gm_kds, _ = kerr_ds_factory(Dr_correct)
    w_kds = worst(gm_kds, L)
    # negative control: a WRONG Δ_r (drop the Λ term) should NOT be vacuum+Λ
    gm_wrong, _ = kerr_ds_factory(lambda r: r * r - 2 * M * r + a * a)
    w_wrong = worst(gm_wrong, L)

    print(f"  Schwarzschild   |R−Λg| = {w_sch:.2e}   (vacuum, expect ≈0)        {'✅' if w_sch < 1e-3 else '❌'}")
    print(f"  Kerr            |R−Λg| = {w_kerr:.2e}   (vacuum, off-diagonal)     {'✅' if w_kerr < 1e-3 else '❌'}")
    print(f"  KERR–de SITTER  |R−Λg| = {w_kds:.2e}   (vacuum+Λ — symbolic OOMs) {'✅' if w_kds < 1e-3 else '❌'}")
    print(f"  control: WRONG Δ_r → |R−Λg| = {w_wrong:.2e}  (large ⇒ real test)   {'✅' if w_wrong > 1e-2 else '❌'}")

    passed = w_sch < 1e-3 and w_kerr < 1e-3 and w_kds < 1e-3 and w_wrong > 1e-2
    print("\n  the numeric engine verifies Kerr–de Sitter — the metric the symbolic")
    print("  Ricci can't even build. This is what unlocks off-diagonal discovery (no VM).")
    print(f"\nNUMERIC CURVATURE: {'PASSED ✅' if passed else 'FAILED ❌'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
