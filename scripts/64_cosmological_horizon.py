#!/usr/bin/env python3
"""Step 64 — THE COSMOLOGICAL HORIZON: the universe itself has a temperature.

A horizon need not surround a black hole. In de Sitter space — the empty,
exponentially expanding universe that ΛCDM approaches as t→∞ (§37) — every observer
is surrounded by a COSMOLOGICAL horizon at r_c = 1/H, beyond which space recedes
faster than light. Gibbons & Hawking (1977) showed it radiates, exactly like a black
hole: it has a temperature and an entropy. The same engine that did black-hole
thermodynamics (§35) and Kerr's (§61) now does the universe's — and the analyzer
reports it correctly (after fixing the sign: a cosmological horizon has f′<0, but its
temperature is still positive).

  (A) the analyzer finds the cosmological horizon r_c=1/H with T=H/2π, S=π/H²
      (validates `analyzer.horizon_thermo` and the |f′| temperature fix);
  (B) Gibbons–Hawking temperature T = κ/2π = H/2π — the universe has a temperature
      set by its expansion rate (κ = H);
  (C) the horizon carries Bekenstein–Hawking entropy S = A/4 = π/H²;
  (D) tie to cosmology (§37): de Sitter is Λ-dominated with Λ = 3H², so T = √(Λ/3)/2π
      and S = 3π/Λ — the universe's temperature and entropy read straight off the
      cosmological constant; a larger Λ (faster expansion) means a SMALLER, hotter
      horizon and LESS entropy (a tighter bound on the observable universe).

Honest scope: textbook de Sitter thermodynamics (Gibbons–Hawking 1977). New is the
same engine handling a cosmological horizon with no black-hole-specific code, and the
sign fix that makes its temperature come out positive.

Run:  .venv/bin/python scripts/64_cosmological_horizon.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry
from analyzer import horizon_thermo


def main():
    print("THE COSMOLOGICAL HORIZON — the universe itself has a temperature\n")
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    H, Lam = sp.symbols("H Lambda", positive=True)
    f = 1 - H**2 * r**2
    geo = Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph])
    ok = []

    # (A) the analyzer finds the cosmological horizon with positive T and S=A/4
    hz = horizon_thermo(geo)
    outer = [h for h in hz if sp.simplify(h[0] - 1 / H) == 0]
    okA = (len(outer) == 1
           and sp.simplify(outer[0][1] - H / (2 * sp.pi)) == 0
           and sp.simplify(outer[0][2] - sp.pi / H**2) == 0)
    ok.append(okA)
    print(f"  (A) analyzer.horizon_thermo: r_c={outer[0][0] if outer else '?'}, "
          f"T={outer[0][1] if outer else '?'}, S={outer[0][2] if outer else '?'}   "
          f"{'✅ (T>0 after the |f′| fix)' if okA else '❌'}")

    # (B) Gibbons–Hawking temperature κ = H, T = H/2π
    kappa = sp.Abs(sp.diff(f, r).subs(r, 1 / H)) / 2
    T = sp.simplify(kappa / (2 * sp.pi))
    okB = sp.simplify(kappa - H) == 0 and sp.simplify(T - H / (2 * sp.pi)) == 0
    ok.append(okB)
    print(f"\n  (B) surface gravity κ = {sp.simplify(kappa)} = H;  T = κ/2π = {T} = H/2π   "
          f"{'✅ Gibbons–Hawking — the universe has a temperature' if okB else '❌'}")

    # (C) Bekenstein–Hawking entropy S = A/4 = π/H²
    A = 4 * sp.pi * (1 / H)**2
    S = sp.simplify(A / 4)
    okC = sp.simplify(S - sp.pi / H**2) == 0
    ok.append(okC)
    print(f"\n  (C) horizon area A = {sp.simplify(A)},  entropy S = A/4 = {S} = π/H²   "
          f"{'✅' if okC else '❌'}")

    # (D) tie to cosmology (§37): de Sitter is Λ-dominated, Λ = 3H²
    H_of_Lam = sp.sqrt(Lam / 3)                        # H = √(Λ/3)
    T_Lam = sp.simplify((H / (2 * sp.pi)).subs(H, H_of_Lam))
    S_Lam = sp.simplify((sp.pi / H**2).subs(H, H_of_Lam))
    okD = sp.simplify(T_Lam - sp.sqrt(Lam / 3) / (2 * sp.pi)) == 0 and sp.simplify(S_Lam - 3 * sp.pi / Lam) == 0
    ok.append(okD)
    print(f"\n  (D) de Sitter is Λ-dominated (Λ=3H²):  T = {T_Lam},  S = {S_Lam}")
    print(f"      → the universe's temperature & entropy from its cosmological constant;")
    print(f"        larger Λ ⇒ smaller, hotter horizon, less entropy   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nCOSMOLOGICAL HORIZON: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Gibbons–Hawking T=H/2π, S=π/H², tied to Λ — the universe is thermal)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
