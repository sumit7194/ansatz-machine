#!/usr/bin/env python3
"""Step 01 — VERIFIER ground-truth battery.

Ground rule (same spirit as echoes/ "injections before search"):
build and validate the judge BEFORE writing any proposer. The verifier
is tested against 100 years of ground truth, in both directions:
known solutions must PASS, sabotaged metrics must FAIL.

The engine lives in gr_engine.py (shared with later steps); see its
docstring for the design decisions (Ricci-form check, intermediate
simplification, three-valued verdicts).

Run:  .venv/bin/python scripts/01_verifier.py [--kerr]
"""

import argparse
import time

import sympy as sp

from gr_engine import Geometry, verify, VERIFIED, REJECTED


def check(name, expected, metric, coords, params=(), Lambda=sp.S.Zero,
          note=""):
    t0 = time.time()
    verdict, detail = verify(metric, coords, params, Lambda)
    dt = time.time() - t0
    ok = verdict == expected
    mark = "✓" if ok else "✗✗ EXPECTATION FAILED"
    print(f"  {mark} {name}: {verdict} ({detail}, {dt:.2f}s)"
          + (f"  [{note}]" if note else ""))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kerr", action="store_true",
                    help="also run the Kerr stress test (slow)")
    args = ap.parse_args()

    t, r, th, ph, z = sp.symbols("t r theta phi z", real=True)
    M, ell, mu = sp.symbols("M ell mu", positive=True)
    results = []

    print("== Known solutions must VERIFY ==")

    # --- 3+1 Schwarzschild (Dec 1915): the original ---
    f = 1 - 2 * M / r
    schw = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2)
    results.append(check("Schwarzschild 3+1", VERIFIED,
                         schw, [t, r, th, ph], params=[M]))

    # its Kretschmann fingerprint: should be 48 M^2 / r^6
    K = Geometry(schw, [t, r, th, ph]).kretschmann
    match = sp.simplify(K - 48 * M**2 / r**6) == 0
    results.append(match)
    print(f"  {'✓' if match else '✗✗'} Kretschmann(Schwarzschild) = {K} "
          f"(expected 48M²/r⁶: {'match' if match else 'MISMATCH'})")

    # --- 3+1 de Sitter static patch: tests the Λ pathway ---
    L3 = sp.symbols("Lambda", positive=True)
    fds = 1 - L3 * r**2 / 3
    ds = sp.diag(-fds, 1 / fds, r**2, r**2 * sp.sin(th)**2)
    results.append(check("de Sitter 3+1 (Λ>0)", VERIFIED,
                         ds, [t, r, th, ph], params=[L3], Lambda=L3))

    # --- 2+1 BTZ black hole (1992): the Flatland rung, Λ = -1/ℓ² ---
    fb = r**2 / ell**2 - M
    btz = sp.diag(-fb, 1 / fb, r**2)
    results.append(check("BTZ 2+1 (Λ<0)", VERIFIED,
                         btz, [t, r, ph], params=[M, ell],
                         Lambda=-1 / ell**2))

    # --- 4+1 Schwarzschild-Tangherlini: the rung above us ---
    ft = 1 - mu / r**2
    tang = sp.diag(-ft, 1 / ft, r**2, r**2 * sp.sin(th)**2,
                   r**2 * sp.sin(th)**2 * sp.sin(ph)**2)
    results.append(check("Schwarzschild-Tangherlini 4+1", VERIFIED,
                         tang, [t, r, th, ph, z], params=[mu]))

    print("\n== Sabotaged metrics must be REJECTED ==")

    # wrong falloff (2M/r -> 2M/r²): plausible-looking, wrong
    fbad = 1 - 2 * M / r**2
    bad = sp.diag(-fbad, 1 / fbad, r**2, r**2 * sp.sin(th)**2)
    results.append(check("fake-Schwarzschild (2M/r²)", REJECTED,
                         bad, [t, r, th, ph], params=[M]))

    # missing 1/f on g_rr: classic hand-error
    bad2 = sp.diag(-f, sp.S.One, r**2, r**2 * sp.sin(th)**2)
    results.append(check("Schwarzschild w/ g_rr=1", REJECTED,
                         bad2, [t, r, th, ph], params=[M]))

    if args.kerr:
        print("\n== Stress test: Kerr (1963) ==")
        # In Boyer-Lindquist trig form the symbolic stage drowns in
        # sin(6θ) swamps: 500s -> UNPROVEN (numerically vacuum to
        # 1e-132, symbolically stuck — Richardson's theorem in the
        # wild). The fix is a coordinate choice, u = cos(θ): every
        # component becomes a RATIONAL function, where zero-testing is
        # decidable. Same spacetime, 9s theorem. Engine design rule:
        # prefer coordinates that make the metric rational.
        u = sp.symbols("u", real=True)
        a = sp.symbols("a", positive=True)
        Sigma = r**2 + a**2 * u**2
        Delta = r**2 - 2 * M * r + a**2
        kerr = sp.zeros(4, 4)
        kerr[0, 0] = -(1 - 2 * M * r / Sigma)
        kerr[0, 3] = kerr[3, 0] = -2 * M * r * a * (1 - u**2) / Sigma
        kerr[1, 1] = Sigma / Delta
        kerr[2, 2] = Sigma / (1 - u**2)
        kerr[3, 3] = (r**2 + a**2
                      + 2 * M * r * a**2 * (1 - u**2) / Sigma) * (1 - u**2)
        results.append(check("Kerr 3+1 (rational u=cosθ form)", VERIFIED,
                             kerr, [t, r, u, ph], params=[M, a],
                             note="off-diagonal, 47 years harder than "
                                  "Schwarzschild"))

    print(f"\n{'ALL EXPECTATIONS MET ✅' if all(results) else 'EXPECTATION FAILURES ❌'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
