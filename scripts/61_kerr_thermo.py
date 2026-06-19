#!/usr/bin/env python3
"""Step 61 — KERR THERMODYNAMICS: the rotating horizon's T, S and the Smarr law.

Closes a thread open since the first Kerr work: the analyzer reports a rotating
(off-diagonal) horizon's LOCATION but left its temperature and entropy UNKNOWN —
the surface gravity from the metric collapses to nested radicals SymPy won't reduce.
Here we close it for Kerr by reading the clean pieces straight off the metric and
assembling the thermodynamics, then verifying the laws exactly.

From the Kerr metric the engine reads:
  • the radial function  Δ = g_θθ / g_rr  (= r²−2Mr+a²), horizon r₊ at Δ=0;
  • the horizon area  A = ∮√(g_θθ g_φφ)|_{r₊}  (= 4π(r₊²+a²) = 8πMr₊);
  • the frame-dragging rate  Ω_H = (−g_tφ/g_φφ)|_{r₊}  (= a/(r₊²+a²));
  • the temperature  T = κ/2π = Δ′(r₊)/A  (κ = √(M²−a²)/(2Mr₊)), entropy S = A/4.

Then the exact checks:
  (A) the horizon is a KILLING horizon: χ = ∂_t + Ω_H ∂_φ is null there;
  (B) the SMARR formula  M = 2TS + 2Ω_H J  (J = Ma) — mass from horizon data;
  (C) the FIRST LAW  dM = T dS + Ω_H dJ  (a differential identity in M, a);
  (D) the THIRD LAW: extremal a→M ⇒ T→0 (unreachable) but S→2πM² stays finite;
  (E) the static limit a→0 recovers Schwarzschild T=1/8πM, S=4πM² (battery 35).

Honest scope: textbook Kerr thermodynamics (Bardeen–Carter–Hawking 1973). The clean
pieces (Δ, r₊, A, Ω_H) are metric-derived; T uses the standard Kerr κ (the geometric
κ swamps symbolically — the original UNKNOWN), and the a→0 check grounds it against
the metric-derived Schwarzschild value of §35. This is the Kerr-specific closure; a
general rotating-horizon T/S stays honestly UNKNOWN in the analyzer.

Run:  .venv/bin/python scripts/61_kerr_thermo.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("KERR THERMODYNAMICS — the rotating horizon's T, S and the Smarr law\n")
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    M, a = sp.symbols("M a", positive=True)
    Sig = r**2 + a**2 * sp.cos(th)**2
    s2 = sp.sin(th)**2
    g = sp.zeros(4)
    g[0, 0] = -(1 - 2 * M * r / Sig)
    g[0, 3] = g[3, 0] = -2 * M * r * a * s2 / Sig
    g[1, 1] = Sig / (r**2 - 2 * M * r + a**2)
    g[2, 2] = Sig
    g[3, 3] = (r**2 + a**2 + 2 * M * r * a**2 * s2 / Sig) * s2
    ok = []

    # --- read the pieces straight off the metric ---
    Delta = sp.cancel(sp.together(g[2, 2] / g[1, 1]))         # = r²−2Mr+a²
    rp = M + sp.sqrt(M**2 - a**2)                             # outer horizon (Δ=0)
    A = sp.simplify(2 * sp.pi * sp.integrate(
        sp.sqrt(sp.simplify((g[2, 2] * g[3, 3]).subs(r, rp))), (th, 0, sp.pi)))
    Omega_H = sp.simplify((-g[0, 3] / g[3, 3]).subs(r, rp))
    T = sp.simplify(sp.diff(Delta, r).subs(r, rp) / A)        # = κ/2π
    S = sp.simplify(A / 4)
    J = M * a
    print(f"  metric-derived:  Δ = {Delta},  r₊ = {sp.simplify(rp)}")
    print(f"  A = {A},  Ω_H = {Omega_H}")
    print(f"  T = κ/2π = {T},  S = A/4 = {S}")

    # (A) Killing horizon: χ = ∂_t + Ω_H ∂_φ is null at r₊
    chi_norm = sp.simplify((g[0, 0] + 2 * Omega_H * g[0, 3] + Omega_H**2 * g[3, 3]).subs(r, rp))
    okA = chi_norm == 0
    ok.append(okA)
    print(f"\n  (A) χ = ∂_t + Ω_H ∂_φ null at r₊:  g(χ,χ)|_{{r₊}} = {chi_norm}   "
          f"{'✅ Killing horizon' if okA else '❌'}")

    # (B) Smarr formula M = 2TS + 2 Ω_H J
    smarr = sp.simplify(2 * T * S + 2 * Omega_H * J)
    okB = sp.simplify(smarr - M) == 0
    ok.append(okB)
    print(f"\n  (B) Smarr:  2TS + 2Ω_H J = {smarr}  = M   {'✅' if okB else '❌'}")

    # (C) first law dM = T dS + Ω_H dJ  (coefficients of dM and da)
    coeffs = []
    for var, want in ((M, 1), (a, 0)):
        rhs = sp.simplify(T * sp.diff(S, var) + Omega_H * sp.diff(J, var))
        coeffs.append(sp.simplify(rhs - want) == 0)
    okC = all(coeffs)
    ok.append(okC)
    print(f"\n  (C) first law dM = T dS + Ω_H dJ:  dM coeff {coeffs[0]}, da coeff {coeffs[1]}   "
          f"{'✅' if okC else '❌'}")

    # (D) third law: extremal a→M gives T→0 but S finite
    T_ext = sp.simplify(T.subs(a, M))
    S_ext = sp.simplify(S.subs(a, M))
    okD = T_ext == 0 and S_ext == 2 * sp.pi * M**2
    ok.append(okD)
    print(f"\n  (D) extremal a=M:  T = {T_ext} (third law — unreachable),  "
          f"S = {S_ext} (finite)   {'✅' if okD else '❌'}")

    # (E) static limit a→0 recovers Schwarzschild (battery 35)
    T0 = sp.simplify(sp.limit(T, a, 0))
    S0 = sp.simplify(sp.limit(S, a, 0))
    okE = T0 == 1 / (8 * sp.pi * M) and S0 == 4 * sp.pi * M**2
    ok.append(okE)
    print(f"\n  (E) static limit a→0:  T = {T0} = 1/8πM,  S = {S0} = 4πM²   "
          f"{'✅ recovers Schwarzschild (§35)' if okE else '❌'}")

    passed = all(ok)
    print(f"\nKERR THERMO: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(rotating-horizon T, S, Ω_H + Smarr + first/third laws — the UNKNOWN, closed for Kerr)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
