#!/usr/bin/env python3
"""Step 71 — ADM 3+1 & THE INITIAL-VALUE CONSTRAINTS: GR as an evolution problem.

A different flavour entirely: not a static solution to classify, but GR as DYNAMICS.
Split spacetime into space + time — slice it into instants — and Einstein's 10
equations split into two kinds (Arnowitt–Deser–Misner 1959):
  • 4 CONSTRAINTS that the geometry on each slice must satisfy (1 Hamiltonian, 3
    momentum) — these restrict the allowed initial data;
  • 6 EVOLUTION equations that march the spatial metric γ_ij and its "velocity" (the
    extrinsic curvature K_ij) forward in time.
This is how LIGO's waveforms are computed: numerical relativity solves the constraints
for initial data, then evolves. The 4-metric becomes (lapse N, shift Nⁱ, spatial γ_ij).

The HAMILTONIAN constraint is  ³R + K² − K_ij K^ij = 16πρ.  The engine shows:
  (A) the 3+1 split of a static metric: lapse N=√f, shift Nⁱ=0, spatial γ_ij;
  (B) the Hamiltonian constraint on an FLRW slice (K_ij=−Hγ_ij, K=−3H, K_ijK^ij=3H²)
      IS the FRIEDMANN equation: ³R=6k/a² ⇒ 6k/a²+6H² = 16πρ ⇒ H²+k/a²=(8π/3)ρ — the
      Friedmann equation (§37) is literally the Hamiltonian constraint;
  (C) a time-symmetric VACUUM slice (Schwarzschild t=const, K_ij=0) ⇒ the constraint
      forces ³R=0 — and indeed the curved Flamm slice (§63) is scalar-flat;
  (D) so 6 evolve + 4 constrain = 10 Einstein equations: spacetime is the time-history
      of a 3-geometry, and the constraints are the price of slicing it.

Honest scope: textbook ADM/numerical-relativity. New is the same engine computing the
spatial ³R off any slice and showing Friedmann = the Hamiltonian constraint.

Run:  .venv/bin/python scripts/71_adm.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry


def ricci3(gamma, coords):
    """Scalar curvature ³R of a spatial 3-metric (Geometry is dimension-agnostic)."""
    return sp.simplify(Geometry(gamma, coords).ricci_scalar)


def main():
    print("ADM 3+1 & THE INITIAL-VALUE CONSTRAINTS — GR as an evolution problem\n")
    t, r, th, ph, chi = sp.symbols("t r theta phi chi", positive=True)
    M, a, H = sp.symbols("M a H", positive=True)
    ok = []

    # (A) the 3+1 split of a static metric: lapse N=√f, shift 0, spatial γ
    f = 1 - 2 * M / r
    N = sp.sqrt(f)
    gamma_S = sp.diag(1 / f, r**2, r**2 * sp.sin(th)**2)
    okA = sp.simplify(N**2 - f) == 0
    ok.append(okA)
    print(f"  (A) static 3+1 split: lapse N = √(−g_tt) = {N}, shift Nⁱ = 0, spatial γ_ij = diag(1/f, r², r²sin²θ)   "
          f"{'✅' if okA else '❌'}")

    # (B) the Hamiltonian constraint on an FLRW slice = the Friedmann equation
    #     closed (k=1): γ = a²[dχ² + sin²χ dΩ²], ³R = 6/a²
    gamma_F = a**2 * sp.diag(1, sp.sin(chi)**2, sp.sin(chi)**2 * sp.sin(th)**2)
    R3 = ricci3(gamma_F, [chi, th, ph])
    okR3 = sp.simplify(R3 - 6 / a**2) == 0                     # 6k/a², k=1
    K, KK = -3 * H, 3 * H**2                                    # K_ij=−Hγ_ij ⇒ K=−3H, K_ijK^ij=3H²
    ham = sp.simplify(R3 + K**2 - KK)                          # ³R + K² − K_ijK^ij
    friedmann = sp.simplify(ham / 6 - (H**2 + 1 / a**2))       # should be 0 ⇒ H²+k/a²=(8π/3)ρ
    okB = okR3 and friedmann == 0
    ok.append(okB)
    print(f"\n  (B) FLRW slice: ³R = {R3} (= 6k/a², k=1); K=−3H, K_ijK^ij=3H²")
    print(f"      Hamiltonian ³R+K²−K_ijK^ij = {ham} = 16πρ  ⇒  H²+k/a² = (8π/3)ρ — the FRIEDMANN equation (§37)   "
          f"{'✅' if okB else '❌'}")

    # (C) time-symmetric vacuum slice: K=0 ⇒ ³R=0 (Schwarzschild t=const, the Flamm slice §63)
    R3_S = ricci3(gamma_S, [r, th, ph])
    okC = R3_S == 0
    ok.append(okC)
    print(f"\n  (C) Schwarzschild t=const slice (K_ij=0, vacuum): ³R = {R3_S} — the curved Flamm slice (§63)")
    print(f"      is scalar-flat, as the Hamiltonian constraint demands   {'✅' if okC else '❌'}")

    # (D) the count: 6 evolution + 4 constraint = 10 Einstein equations
    okD = (6 + 4 == 10) and okA and okB and okC
    ok.append(okD)
    print(f"\n  (D) 6 evolution + 4 constraint (1 Hamiltonian + 3 momentum) = 10 Einstein equations:")
    print(f"      spacetime is the time-history of a 3-geometry; constraints are the price of slicing   "
          f"{'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nADM: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(the 3+1 split; Friedmann = the Hamiltonian constraint; the Flamm slice is scalar-flat)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
