#!/usr/bin/env python3
"""Step 36 — ENERGY CONDITIONS: is the matter PHYSICAL? (a classifier lens)

Attack angle #2 (orthogonal to "find a metric"): the GP keeps proposing exotic
branches (e.g. the negative-mass RN it likes), and a bare "VERIFIED" only says
"solves the field equations" — not "the matter that sources it is physically
allowed". This step adds that judgment. For ANY static metric it reads off the
stress-energy from the Einstein tensor and tests the standard pointwise energy
conditions, turning the engine into a physicality classifier.

From G^a_b = 8π T^a_b in the orthonormal frame (static diagonal ansatz):
    ρ = −G^t_t/8π  (energy density),  p_r = G^r_r/8π,  p_t = G^θ_θ/8π.
Conditions tested (pointwise, over r>0 with positive parameters):
    NEC: ρ+p_r ≥ 0, ρ+p_t ≥ 0
    WEC: NEC and ρ ≥ 0
    DEC: WEC and ρ ≥ |p_r|, ρ ≥ |p_t|
    SEC: NEC and ρ + p_r + 2p_t ≥ 0

Validation reproduces the textbook verdicts and shows the classifier
DISCRIMINATES the regimes:
  • Schwarzschild — vacuum, all densities 0 (saturated);
  • Reissner–Nordström — all four hold (a physical EM field);
  • "exotic charge" f=1−2M/r−Q²/r² — ρ<0, WEC/NEC VIOLATED (flagged exotic);
  • de Sitter — only SEC violated (the dark-energy / acceleration signature).

Honest scope: pointwise conditions; signs are checked symbolically when SymPy
can decide and otherwise over a sampled positive domain (a negative sample is a
definitive violation). Not a new source rung (D26) — a judgment layer on top of
the existing engine.

Run:  .venv/bin/python scripts/36_energy_conditions.py
"""

import os
import random
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry, build_ansatz_metric, R_SYM

r = R_SYM


def densities(f, n=4):
    """ρ, p_r, p_t (orthonormal frame) from the mixed Einstein tensor G^a_b."""
    metric, coords, _ = build_ansatz_metric(n, f)
    geo = Geometry(metric, coords)
    G = geo.ricci - sp.Rational(1, 2) * geo.ricci_scalar * geo.g  # G_ab (lower)
    Gmix = sp.simplify(geo.ginv * G)                              # G^a_b
    rho = sp.simplify(-Gmix[0, 0] / (8 * sp.pi))                  # T^t_t = −ρ
    p_r = sp.simplify(Gmix[1, 1] / (8 * sp.pi))
    p_t = sp.simplify(Gmix[2, 2] / (8 * sp.pi))
    return rho, p_r, p_t


def nonneg(expr):
    """Three-valued: is expr ≥ 0 for all r>0 and positive parameters?
    Symbolic when SymPy can decide; else sampled (a negative sample is a
    definitive violation)."""
    e = sp.simplify(expr)
    if e == 0 or e.is_nonnegative:
        return True
    if e.is_negative or (e.is_nonpositive and e != 0):
        return False
    rng = random.Random(0)
    free = sorted(e.free_symbols, key=str)
    holds = True
    for _ in range(60):
        sub = {s: sp.Rational(rng.randint(1, 25), rng.randint(1, 6)) for s in free}
        try:
            v = float(e.subs(sub))
        except (TypeError, ValueError):
            return None                     # cannot decide → UNKNOWN
        if v < -1e-12:
            return False                    # definitive violation
    return holds


def classify(rho, p_r, p_t):
    """Return dict of condition → True/False/None(UNKNOWN)."""
    nec = _and(nonneg(rho + p_r), nonneg(rho + p_t))
    wec = _and(nec, nonneg(rho))
    dec = _and(wec, nonneg(rho - p_r), nonneg(rho + p_r),
               nonneg(rho - p_t), nonneg(rho + p_t))
    sec = _and(nec, nonneg(rho + p_r + 2 * p_t))
    return {"NEC": nec, "WEC": wec, "DEC": dec, "SEC": sec}


def _and(*vals):
    if any(v is False for v in vals):
        return False
    if any(v is None for v in vals):
        return None
    return True


def _mark(v):
    return "hold" if v is True else ("VIOLATED" if v is False else "UNKNOWN")


def main():
    M, Q, L = sp.symbols("M Q Lambda", positive=True)
    print("ENERGY CONDITIONS — is the matter physical? (classifier)\n")

    # (label, f, expected {cond: bool})
    cases = [
        ("Schwarzschild (vacuum)", 1 - 2 * M / r,
         {"NEC": True, "WEC": True, "DEC": True, "SEC": True}),
        ("Reissner–Nordström", 1 - 2 * M / r + Q**2 / r**2,
         {"NEC": True, "WEC": True, "DEC": True, "SEC": True}),
        ("exotic charge −Q²/r²", 1 - 2 * M / r - Q**2 / r**2,
         {"NEC": False, "WEC": False, "DEC": False, "SEC": False}),
        ("de Sitter (Λ>0)", 1 - L * r**2 / 3,
         {"NEC": True, "WEC": True, "DEC": True, "SEC": False}),
    ]

    ok_all = True
    for label, f, expect in cases:
        rho, p_r, p_t = densities(f)
        verdict = classify(rho, p_r, p_t)
        match = all(verdict[k] is expect[k] for k in expect)
        ok_all = ok_all and match
        regime = ("vacuum" if rho == 0 else
                  "exotic (ρ<0)" if verdict["WEC"] is False else
                  "dark-energy-like (SEC only)" if verdict["SEC"] is False else
                  "physical")
        print(f"  {label:24s}: ρ={rho}")
        print(f"     " + "  ".join(f"{k}:{_mark(verdict[k])}" for k in
                                    ("NEC", "WEC", "DEC", "SEC"))
              + f"   → {regime}   {'✓' if match else '✗ (expected '+str(expect)+')'}")

    print("\n  use: the GP returns 'VERIFIED' for exotic branches too (e.g. its")
    print("  negative-mass / negative-charge favourites); this lens is the second")
    print("  gate — solves-the-equations AND is-physically-allowed are different.")
    print(f"\nENERGY CONDITIONS: {'PASSED ✅' if ok_all else 'FAILED ❌'}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
