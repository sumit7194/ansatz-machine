#!/usr/bin/env python3
"""Step 42 — the CAUSAL-STRUCTURE lens (PLAN #2).

The analyzer locates singularities; this classifies their CHARACTER and the
spacetime's causal twist — the mind-bending structure of black-hole interiors,
made exact:

  • singularity character — is the singularity SPACELIKE ("a moment, the end of
    time" — you cannot avoid it once inside) or TIMELIKE ("a place" — you can
    steer around it)? Set by the sign of g^{kk} (the inverse-metric component
    along the singular direction) as you approach it: g^{kk}<0 ⇒ timelike normal
    ⇒ spacelike surface; g^{kk}>0 ⇒ timelike surface.
  • signature flip — does the timelike direction rotate ∂_t → ∂_r inside a
    horizon (g_tt changes sign)? That is the "space and time swap roles" effect.

The calibration is the Schwarzschild-vs-Reissner–Nordström contrast: adding
CHARGE flips the singularity from spacelike to timelike. Both are in the zoo, so
this is a clean, checkable test.

Why it matters beyond us (hand-shared with the sister NN project, kept separate):
our EXACT tool is the ground-truth oracle for exactly these phenomena — a net
that learned a spacetime from local observation should reproduce the signature
flip and the charge-driven spacelike→timelike flip; here are the exact answers.

Run:  .venv/bin/python scripts/42_causal_structure.py
"""

import os
import sys

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from gr_engine import R_SYM
from analyzer import analyze


def main():
    r = R_SYM
    t, x, y, z, th, ph = sp.symbols("t x y z theta phi", real=True)
    M, Q, r0 = sp.symbols("M Q r0", positive=True)
    print("CAUSAL STRUCTURE — singularity character + signature flip\n")

    def diag4(f):
        return sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph]

    a = t**sp.Rational(2, 3)
    cases = [
        # (label, metric, coords, expect_char_substr, expect_flip)
        ("Schwarzschild", *diag4(1 - 2 * M / r), "spacelike", True),
        ("Reissner–Nordström", *diag4(1 - 2 * M / r + Q**2 / r**2), "timelike", True),
        ("FLRW dust (Big Bang)", sp.diag(-1, a**2, a**2, a**2), [t, x, y, z], "spacelike", False),
        ("Morris–Thorne wormhole",
         sp.diag(-1, 1 / (1 - r0**2 / r**2), r**2, r**2 * sp.sin(th)**2), [t, r, th, ph], None, False),
        ("Minkowski", sp.diag(-1, 1, 1, 1), [t, x, y, z], None, False),
    ]

    ok = True
    for label, metric, coords, exp_char, exp_flip in cases:
        c = analyze(metric, coords)["causal"]
        chars = c["singularity_character"]
        flip = c["signature_flip"]
        char_str = "; ".join(f"{v}={val}: {ch}" for v, val, ch in chars) if chars else "no singularity"
        good = (flip is exp_flip) and (exp_char is None or any(exp_char in ch for *_, ch in chars))
        ok = ok and good
        print(f"  {label:24s} {'✓' if good else '✗'}")
        print(f"     singularity: {char_str}")
        print(f"     signature flip (t↔r inside horizon): {flip}")

    print("\n  calibration: CHARGE flips the singularity spacelike→timelike")
    print("  (Schwarzschild 'end of time' → Reissner–Nordström 'a place'). The")
    print("  exact ground-truth oracle for the sister NN project's learned causal structure.")
    print(f"\nCAUSAL STRUCTURE: {'PASSED ✅' if ok else 'FAILED ❌'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
