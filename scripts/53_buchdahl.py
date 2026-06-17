#!/usr/bin/env python3
"""Step 53 — THE BUCHDAHL BOUND: how compact a star can be before it must collapse.

Grounds §52's abstract TOV equation in a concrete, exact star — the constant-density
interior Schwarzschild sphere (1916) — and recovers a celebrated theorem: NO static
fluid star can be more compact than M/R = 4/9. Squeeze it past that and even an
INFINITE central pressure cannot hold it up; it must collapse to a black hole.

For uniform density ρ = 3M/(4πR³) the mass inside r is m(r) = M r³/R³, and TOV
(§52) integrates to the exact pressure

    p(r) = ρ · [√(1 − 2Mr²/R³) − √(1 − 2M/R)] / [3√(1 − 2M/R) − √(1 − 2Mr²/R³)].

Experiments:
  (A) this exact p(r) SATISFIES the engine's TOV ODE (numeric spot-check across r —
      sympy won't prove the radical identity, cf. §50);
  (B) the boundary condition p(R) = 0 (the star's surface is where pressure vanishes);
  (C) the central pressure p_c = p(0) DIVERGES as the compactness M/R → 4/9 — the
      BUCHDAHL BOUND, solved exactly from the denominator going to zero;
  (D) numerically: p_c climbs without limit as M/R approaches 4/9.

Honest scope: textbook (Schwarzschild 1916 interior; Buchdahl 1959). New is that it
falls straight out of the engine's own recovered TOV — a star with a maximum
compactness, found by the same tool that does black holes and the universe.

Run:  .venv/bin/python scripts/53_buchdahl.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("THE BUCHDAHL BOUND — the most compact a static fluid star can be\n")
    r, M, R = sp.symbols("r M R", positive=True)

    rho = 3 * M / (4 * sp.pi * R**3)          # uniform density
    m = M * r**3 / R**3                        # mass inside radius r (= (4π/3)ρr³)
    sj = sp.sqrt(1 - 2 * M * r**2 / R**3)      # √(1−2Mr²/R³)
    sR = sp.sqrt(1 - 2 * M / R)                # √(1−2M/R)  (surface value)
    p = rho * (sj - sR) / (3 * sR - sj)        # interior-Schwarzschild pressure

    # (A) does this exact star satisfy the engine's TOV ODE?  (numeric — radical ID)
    tov_rhs = -(rho + p) * (m + 4 * sp.pi * r**3 * p) / (r * (r - 2 * m))
    resid = sp.diff(p, r) - tov_rhs
    subs0 = {M: sp.Rational(1, 5), R: 1}       # compactness 0.2, comfortably stable
    okA = all(abs(complex(resid.subs(subs0).subs(r, rv).evalf())) < 1e-9
              for rv in (sp.Rational(1, 10), sp.Rational(3, 10), sp.Rational(1, 2),
                         sp.Rational(7, 10), sp.Rational(9, 10)))
    print(f"  (A) exact p(r) satisfies the engine's TOV ODE   {'✅' if okA else '❌'}  "
          "(numeric spot-check, 5 radii)")

    # (B) surface boundary condition p(R)=0
    okB = sp.simplify(p.subs(r, R)) == 0
    print(f"  (B) surface pressure p(R) = {sp.simplify(p.subs(r, R))}   {'✅' if okB else '❌'}  "
          "(the star ends where pressure vanishes)")

    # (C) central pressure & the Buchdahl bound: p_c diverges where 3√(1−2M/R)=√1=1
    p_c = sp.simplify(p.subs(r, 0))
    print(f"\n  (C) central pressure p_c = p(0) = {p_c}")
    # solve the denominator 3√(1−2M/R) − 1 = 0  for the compactness x = M/R
    x = sp.Symbol("x", positive=True)           # x = M/R
    bound = sp.solve(sp.Eq(3 * sp.sqrt(1 - 2 * x), 1), x)
    okC = (len(bound) == 1 and bound[0] == sp.Rational(4, 9))
    print(f"      p_c → ∞  when  3√(1−2M/R) = 1  ⇒  M/R = {bound[0] if bound else '?'}"
          f"   {'✅  the BUCHDAHL BOUND (4/9)' if okC else '❌'}")

    # (D) numeric: central pressure runs away as compactness → 4/9 (≈0.4444)
    pc_x = p_c.subs(M, x * R)                   # p_c as a function of compactness x
    vals = [(sp.Rational(2, 10), None), (sp.Rational(4, 10), None),
            (sp.Rational(44, 100), None), (sp.Rational(444, 1000), None)]
    seq = [float((pc_x / rho.subs(M, x * R)).subs(x, xv).evalf()) for xv, _ in vals]
    okD = all(seq[i] < seq[i + 1] for i in range(len(seq) - 1)) and seq[-1] > 10
    print("\n  (D) central pressure p_c/ρ as compactness M/R climbs toward 4/9:")
    for (xv, _), s in zip(vals, seq):
        print(f"        M/R = {float(xv):.3f}  →  p_c/ρ = {s:.3f}")
    print(f"      runs away (→∞ at 4/9)   {'✅' if okD else '❌'}  "
          "— past 4/9 no static fluid star exists; it must collapse")

    passed = okA and okB and okC and okD
    print(f"\nBUCHDAHL: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(exact star solves TOV; max compactness M/R=4/9 recovered)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
