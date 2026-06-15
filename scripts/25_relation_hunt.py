#!/usr/bin/env python3
"""Step 25 — RELATION HUNT on the EdGB universal-fit coefficients.

A sibling of the abstractor (24): same instinct — find hidden exact
structure — but aimed at a family whose law is NOT known, the empirical
coefficient functions of our EdGB closed-form fits (v4 static, v5
rotating). We already found ONE relation by hand (c1≈c3, explained as
horizon regularity); this asks systematically whether there is more.

It scans the coefficient functions (polynomials in the coupling p) for:
  (a) coefficients that vanish — especially the constant term, which the
      GR limit (p→0 ⇒ Schwarzschild/Lense-Thirring, corrections vanish)
      forces to zero;
  (b) pairs that are proportional, c_i ≈ k·c_j, for a simple k — equal
      functions (k=1) are the strongest structural ties;
and labels each candidate KNOWN (already explained) or NEW (worth a look).

These are PUBLISHED-PRECISION (~5-digit) fit values, so a "relation" here
is a candidate to be confirmed at full precision and then derived from a
physical constraint — not yet a theorem.

Run:  .venv/bin/python scripts/25_relation_hunt.py
"""

import itertools
import math

# Coefficient functions as {power-of-p: value}. Static 4-param universal
# formula (RESULTS.md v4); rotating R2 formula (22_rot_fit, banked).
STATIC = {
    "c1": {0: -0.00185, 1: -0.23552, 2: -0.12886},   # A-numerator
    "c2": {0: +0.93119, 1: +1.31536, 2: +0.82502},   # A-denominator
    "c3": {0: -0.00196, 1: -0.23216, 2: -0.12675},   # B-numerator
    "c4": {0: +3.81638, 1: +3.56819, 2: +2.44280},   # B-denominator
}
ROTATING = {
    "a1": {0: 0.0, 1: -0.119480, 2: -0.006615},      # frame-drag numerator
    "a2": {0: 0.0, 1: +8.296716, 2: -5.306262},      # frame-drag denominator
}
# 3-dof KKZ-class static fit (edgb_3dof.log): A = 1+[a1(1−x)+a2(1−x)²]/(1+a3x),
# B = 1+[b1(1−x)²+b2(1−x)³]/(1+b3x). Cubics in p. CAVEAT: degree-3 fit from
# only 6 points → p²,p³ terms are over-fit/noisy; treat relations here as
# lower-confidence than the 4-param set.
THREEDOF = {
    "a1": {0: +0.00451, 1: -0.13018, 2: +0.11338, 3: -0.51098},  # A-num 1
    "a2": {0: -0.00386, 1: -0.13378, 2: -0.14577, 3: +0.41707},  # A-num 2
    "a3": {0: -0.20274, 1: +2.93308, 2: -2.41756, 3: +4.37016},  # A-denom
    "b1": {0: +0.00340, 1: -0.02138, 2: +0.22400, 3: -0.41827},  # B-num 1
    "b2": {0: -0.00278, 1: -0.23996, 2: -0.25127, 3: +0.32267},  # B-num 2
    "b3": {0: +1.71992, 1: +5.54592, 2: -4.66218, 3: +8.35701},  # B-denom
}
ALL = {**STATIC, **ROTATING}

# relations we already understand, so the hunt can label them
KNOWN = {
    ("c1", "c3"): "horizon regularity (A,B share their horizon limit)",
}
# all NUMERATOR coefficients must vanish as p→0 (corrections → 0, GR limit):
# 4-param c1/c3, rotating a1/a2, and 3-dof A/B numerators a1,a2,b1,b2.
GR_LIMIT_VANISH = {"c1", "c3", "a1", "a2", "b1", "b2"}


_DEG = 2  # power basis size; bumped to 3 when hunting the cubic 3-dof set


def vec(c):
    return [c.get(k, 0.0) for k in range(_DEG + 1)]


def norm(v):
    return math.sqrt(sum(x * x for x in v))


def report_vanishing(group=None):
    group = group or ALL
    print("== (a) coefficients consistent with ZERO (limit constraints) ==")
    for name, c in group.items():
        scale = norm(vec(c)) or 1.0
        for k, label in [(0, "const  → GR limit p→0")]:
            val = c.get(k, 0.0)
            rel = abs(val) / scale
            if rel < 0.02:
                tag = "GR limit (expected)" if name in GR_LIMIT_VANISH else "NEW?"
                print(f"  {name}[p^{k}] = {val:+.5f}  (|val|/‖{name}‖ = "
                      f"{rel:.2%}) ≈ 0  → {label} [{tag}]")


def report_proportional(group=None):
    group = group or ALL
    print("\n== (b) proportional pairs  c_i ≈ k·c_j  (k=1 ⇒ equal) ==")
    rows = []
    for (n1, c1), (n2, c2) in itertools.combinations(group.items(), 2):
        u, v = vec(c1), vec(c2)
        vv = sum(x * x for x in v)
        if vv == 0:
            continue
        k = sum(a * b for a, b in zip(u, v)) / vv      # best-fit proportionality
        resid = norm([a - k * b for a, b in zip(u, v)]) / (norm(u) or 1.0)
        rows.append((resid, n1, n2, k))
    rows.sort()
    for resid, n1, n2, k in rows:
        if resid > 0.05:
            continue  # only show genuinely-close pairs
        known = KNOWN.get((n1, n2)) or KNOWN.get((n2, n1))
        ksimple = min(abs(k - s) for s in (1, 0.5, 2, -1, -0.5, -2, 3, 1/3))
        ktag = "simple k" if ksimple < 0.03 else f"k={k:+.3f}"
        tag = f"KNOWN: {known}" if known else "NEW?"
        print(f"  {n1} ≈ ({k:+.4f})·{n2}   residual {resid:.2%}  [{ktag}]  → {tag}")


def main():
    global _DEG
    print("RELATION HUNT — EdGB universal-fit coefficients\n")
    print(f"--- SET 1: 4-param static + rotating ({len(STATIC)}+{len(ROTATING)} "
          "functions, degree-2, clean) ---")
    _DEG = 2
    report_vanishing(ALL)
    report_proportional(ALL)

    print(f"\n--- SET 2: 3-dof KKZ-class static ({len(THREEDOF)} functions, "
          "degree-3) — LOWER CONFIDENCE (over-fit p²,p³) ---")
    _DEG = 3
    report_vanishing(THREEDOF)
    report_proportional(THREEDOF)

    print("\nNote: published-precision values; any NEW candidate gets "
          "re-checked at full fit precision, then we try to DERIVE it from a "
          "physical constraint. KNOWN/GR-limit hits validate the hunter.")


if __name__ == "__main__":
    main()
