#!/usr/bin/env python3
"""Step 78 — SYMBOLIC KILLING-TENSOR VERIFIER: the Carter constant, PROVEN.

§58/§69 found Kerr's Carter Killing tensor and checked ∇₍ₐK_bc₎=0 NUMERICALLY (a
residual ~1e-8) — honest, but a measurement, not a theorem. This makes it a PROOF:
`gr_engine` now certifies the Killing-tensor equation SYMBOLICALLY
(`Geometry.is_killing_tensor` / `killing_tensor_residual`), the same cancel→simplify
cascade the engine uses for the field equations. The discover→verify pipeline's
certification of a hidden symmetry is now exact.

The trick that makes it tractable (the full curvature swamps for Kerr): the
Killing-tensor equation needs only the CHRISTOFFEL symbols, not Riemann — and in the
rational u=cosθ coordinates Kerr's metric is rational, so the residual reduces by
cancel/together with no trig blow-up (it closes in ~1s).

  (A) sanity: the metric g is trivially a Killing tensor (∇g=0) — the verifier says True;
  (B) control: a non-Killing tensor (a coordinate-dependent symmetric tensor) — False,
      with a non-zero residual (the verifier isn't vacuously true);
  (C) THE PROOF: Kerr's Carter Killing tensor K = Σ(lₐn_b+l_b nₐ) + r²g_ab satisfies
      ∇₍ₐK_bc₎ ≡ 0 SYMBOLICALLY — the Carter constant, certified as a theorem (was a
      numeric residual in §58/§69);
  (D) so the most novel capability (discover a hidden symmetry → verify it) now ends in
      a proof, not a measurement.

Run:  .venv/bin/python scripts/78_killing_tensor_proof.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry


def kerr_u_geometry():
    """Kerr in rational coordinates (t, r, u=cosθ, φ) — no trig, so symbolic-tractable."""
    t, r, u, ph = sp.symbols("t r u phi", real=True)
    M, a = sp.symbols("M a", positive=True)
    Sig = r**2 + a**2 * u**2
    De = r**2 - 2 * M * r + a**2
    om = 1 - u**2                                   # sin²θ = 1 − u²
    g = sp.zeros(4)
    g[0, 0] = -(1 - 2 * M * r / Sig)
    g[0, 3] = g[3, 0] = -2 * M * r * a * om / Sig
    g[1, 1] = Sig / De
    g[2, 2] = Sig / om                              # g_θθ dθ² = Σ du²/(1−u²)
    g[3, 3] = (r**2 + a**2 + 2 * M * r * a**2 * om / Sig) * om
    geo = Geometry(g, [t, r, u, ph])
    return geo, r, M, a, Sig, De


def carter_tensor(geo, r, Sig, De, a):
    """Carter Killing tensor K_ab = Σ(lₐn_b + l_b nₐ) + r² g_ab (lower indices),
    from the principal null directions (θ/u component = 0)."""
    l = [(r**2 + a**2) / De, 1, 0, a / De]
    nv = [(r**2 + a**2) / (2 * Sig), -De / (2 * Sig), 0, a / (2 * Sig)]
    g, gi = geo.g, geo.ginv
    Kup = sp.Matrix(4, 4, lambda i, j: Sig * (l[i] * nv[j] + l[j] * nv[i]) + r**2 * gi[i, j])
    Kd = sp.Matrix(4, 4, lambda i, j: sum(g[i, a_] * g[j, b_] * Kup[a_, b_]
                                          for a_ in range(4) for b_ in range(4)))
    return sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(Kd[i, j])))


def main():
    print("SYMBOLIC KILLING-TENSOR VERIFIER — the Carter constant, PROVEN\n")
    ok = []
    geo, r, M, a, Sig, De = kerr_u_geometry()

    # (A) the metric is trivially a Killing tensor (∇g = 0)
    okA = geo.is_killing_tensor(geo.g)
    ok.append(okA)
    print(f"  (A) the metric g is a Killing tensor (∇g=0): verifier → {okA}   {'✅' if okA else '❌'}")

    # (B) a non-Killing-tensor control → False (verifier is not vacuously true)
    bad = sp.zeros(4)
    bad[1, 1] = r**2                                 # arbitrary coordinate-dependent symmetric tensor
    res_bad = geo.killing_tensor_residual(bad)
    okB = (not geo.is_killing_tensor(bad)) and res_bad != 0
    ok.append(okB)
    print(f"  (B) control (non-Killing tensor): verifier → {geo.is_killing_tensor(bad)}, residual ≠ 0 "
          f"({res_bad})   {'✅' if okB else '❌'}")

    # (C) THE PROOF: Kerr's Carter Killing tensor, symbolically
    K = carter_tensor(geo, r, Sig, De, a)
    res = geo.killing_tensor_residual(K)
    okC = res == 0
    ok.append(okC)
    print(f"\n  (C) Kerr Carter tensor K = Σ(lₐn_b+l_b nₐ)+r²g:  ∇₍ₐK_bc₎ = {res}")
    print(f"      ⇒ ∇₍ₐK_bc₎ ≡ 0 SYMBOLICALLY — the Carter constant PROVEN (was numeric in §58/§69)   "
          f"{'✅' if okC else '❌'}")

    # (C') SOUNDNESS: perturbing the real Carter tensor must be REJECTED — else the
    #      symbolic zero-test is too lenient and the "proof" is worthless.
    perts = [{(1, 1): sp.Rational(1, 10) * r**2}, {(0, 0): sp.Rational(1, 7)},
             {(2, 2): geo.coords[2]**2}, {(0, 3): r, (3, 0): r}]
    rejected = 0
    for dK in perts:
        Kp = sp.Matrix(K)
        for (i, j), v in dK.items():
            Kp[i, j] = Kp[i, j] + v
        if not geo.is_killing_tensor(Kp):
            rejected += 1
    okCp = rejected == len(perts)
    ok.append(okCp)
    print(f"\n  (C') soundness: {rejected}/{len(perts)} perturbations of K correctly REJECTED "
          f"(the zero-test isn't lenient)   {'✅' if okCp else '❌'}")

    # (D) the upgrade
    okD = okA and okB and okC and okCp
    ok.append(okD)
    print(f"\n  (D) the discover→verify pipeline's certification of a hidden symmetry is now a")
    print(f"      PROOF, not a measurement (`gr_engine.Geometry.is_killing_tensor`)   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nKILLING-TENSOR PROOF: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(symbolic ∇₍ₐK_bc₎=0 — Kerr's Carter constant, certified as a theorem)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
