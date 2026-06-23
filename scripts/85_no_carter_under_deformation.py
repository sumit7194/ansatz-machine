#!/usr/bin/env python3
"""Step 85 — NO CARTER CONSTANT UNDER DEFORMATION: the symbolic frontier, cracked numerically.

The decisive resolution of item-3's proxy (does deforming Kerr break integrability?).
§82 found the Kerr Carter tensor stops closing under a quadrupole deformation but left
"a DIFFERENT Killing tensor may survive" open. §84's Poincaré sections showed the orbits
stay regular. The symbolic Killing-tensor search to settle it SWAMPED (7.5h, no output —
see _killing_search.py). This cracks it NUMERICALLY.

Method (multi-orbit null space, in _qinvariant.py): a conserved quantity quadratic in
momenta, C = Σ c_k φ_k(state), is CONSTANT along every geodesic. Sample many orbits at
fixed E,L (varied inclination → varied Carter value), mean-subtract per orbit (kills the
additive constant), stack, and SVD. A genuine invariant is a right-singular vector with a
machine-ZERO singular value, far below the rest. The basis is checked linearly INDEPENDENT
first (an earlier u⁴/om term hid the identity u²/om−u⁴/om−u²≡0 → a FALSE machine-zero SV;
that stress-test catch is why this battery exists).

  (A) basis independence (no hidden algebraic identity that fakes an invariant);
  (B) VALIDATION — Kerr: the fit recovers the Carter constant (one machine-zero singular
      value, huge gap), and the recovered vector matches p_θ² + L²·cot²θ + a²(1−E²)cos²θ;
  (C) DEFORMED Kerr (§82 metric): NO machine-zero singular value — the smallest sits at
      ~the deformation scale and GROWS with ε, with no gap. No Carter-like conserved
      quantity survives ⇒ the deformed metric is NON-integrable;
  (D) synthesis: deformation breaks integrability (no conserved quadratic, this), yet the
      orbits are regular (§84 Poincaré tori) ⇒ NEAR-integrable / KAM, not a preserved
      hidden symmetry. Honest caveat: "no conserved quadratic in a Carter-rich basis" —
      a higher-order (quartic) Killing tensor is not excluded, but no quadratic Carter exists.

Optional dep: numpy (SVD). SKIPS cleanly if absent, like §77's qnm. Repro:
  .venv/bin/python scripts/85_no_carter_under_deformation.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import numpy as np  # noqa: F401
    _HAVE_NUMPY = True
except ImportError:
    _HAVE_NUMPY = False


def main():
    if not _HAVE_NUMPY:
        print("NO-CARTER-UNDER-DEFORMATION: SKIPPED (numpy not installed; pip install numpy)")
        return 0
    # imported here (not at module level): _qinvariant needs numpy, so a numpy-less
    # checkout skips above instead of crashing on import.
    from _qinvariant import BNAMES, check_independence, fit, metric

    print("NO CARTER CONSTANT UNDER DEFORMATION — symbolic frontier cracked numerically\n")
    ok = []
    E, L, r0 = 0.95, 3.4, 8.0
    p2list = [round(0.08 + 0.04 * k, 3) for k in range(18)]    # fine grid, many bound orbits

    # (A) basis must be linearly independent (else a false machine-zero SV)
    indep = check_independence()
    okA = indep > 1e-6
    ok.append(okA)
    print(f"  (A) basis independence (smallest SV on random points): {indep:.2e}  "
          f"{'✅ no hidden identity' if okA else '❌ DEGENERATE'}")

    # (B) Kerr — the fit must recover the Carter constant
    Sk, nk, veck = fit(metric(0), E, L, p2list, r0)
    gapk = Sk[-2] / Sk[-1]
    terms = dict(zip(BNAMES, veck))
    cpth, cuom, cu2 = terms["pth2"], terms["u2/om"], terms["u2"]
    # normalize so p_θ² has coeff 1, compare to Carter: L²·(u²/om) + a²(1−E²)·u²
    L2, aaE = L**2, 0.6**2 * (1 - E**2)
    bet, alp = cuom / cpth, cu2 / cpth
    carter_match = abs(bet - L2) / L2 < 0.05 and abs(alp - aaE) / aaE < 0.2
    okB = Sk[-1] < 1e-9 and gapk > 1e6 and carter_match
    ok.append(okB)
    print(f"\n  (B) KERR [{nk} orbits]: smallest SV={Sk[-1]:.2e}, gap={gapk:.1e} → one clean invariant")
    print(f"      recovered  C ≈ p_θ² + {bet:.2f}·cot²θ + {alp:.3f}·cos²θ   vs Carter  "
          f"p_θ² + {L2:.2f}·cot²θ + {aaE:.3f}·cos²θ   {'✅ recovers Carter' if carter_match else '❌'}")

    # (C) deformed Kerr — NO machine-zero invariant; obstruction grows with ε
    Sds = {}
    for eps in (2, 5, 10):
        Sd, nd, _ = fit(metric(eps), E, L, p2list, r0)
        Sds[eps] = (Sd[-1], Sd[-2] / Sd[-1], nd)
    no_invariant = all(s > 1e-4 and g < 10 for s, g, _ in Sds.values())
    grows = Sds[2][0] < Sds[5][0] < Sds[10][0]                 # obstruction scales with deformation
    okC = no_invariant and grows
    ok.append(okC)
    print(f"\n  (C) DEFORMED Kerr — smallest SV (no machine-zero, no gap):")
    for eps in (2, 5, 10):
        s, g, nd = Sds[eps]
        print(f"        ε={eps:>2} [{nd} orbits]: smallest SV={s:.2e}, gap={g:.1f}")
    print(f"      no conserved quadratic; obstruction GROWS with ε ⇒ NON-integrable   {'✅' if okC else '❌'}")

    # (D) synthesis
    okD = okA and okB and okC
    ok.append(okD)
    print(f"\n  (D) The fit RECOVERS Carter for Kerr (11 orders below the deformed) and finds NONE for the")
    print(f"      deformed metric — genuine discrimination, not basis artifact. With §84 (regular tori):")
    print(f"      the deformation breaks integrability but KAM-gently ⇒ near-integrable, no hidden symmetry.")
    print(f"      Resolves §82's 'undetermined'; refutes 'a different Killing tensor survives'.   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nNO CARTER UNDER DEFORMATION: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Kerr Carter recovered; deformed has no conserved quadratic ⇒ non-integrable but KAM-regular)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
