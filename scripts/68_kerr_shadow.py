#!/usr/bin/env python3
"""Step 68 — KERR PHOTON ORBITS & THE ASYMMETRIC SHADOW (the EHT image of spin).

Schwarzschild's light ring is a single radius (3M) and its shadow a circle (§45).
Spin breaks that: frame dragging (§60) SPLITS the equatorial light ring into a
co-rotating (prograde) orbit pulled inward and a counter-rotating (retrograde) one
pushed outward, and the black-hole shadow becomes DISPLACED and flattened on the
prograde side — the asymmetry the Event Horizon Telescope resolves in M87*/Sgr A*.
All exact from the Kerr metric.

  (A) equatorial photon-orbit radii (closed form 2M{1+cos[⅔ arccos(∓a/M)]}):
      a=0 ⇒ both 3M (the Schwarzschild ring); a>0 ⇒ r_pro < 3M < r_ret; extremal a=M
      ⇒ prograde → M (the horizon itself!), retrograde → 4M;
  (B) the SHADOW EDGES are the critical impact parameters b=L/E at those orbits
      (R(r)=0): a=0 ⇒ symmetric ±3√3 M (circular shadow, §45); a>0 ⇒ |b_pro| < 3√3M <
      |b_ret| — the shadow is offset toward the prograde side;
  (C) extremal a→M: b_pro → 2M, b_ret → −7M — strongly D-shaped;
  (D) so §45's circle + §60's dragging ⇒ the EHT's asymmetric shadow: the spin is
      written in the shape.

Honest scope: textbook Kerr null geodesics (Bardeen 1973). New is the same engine
reading the split light ring and shadow asymmetry off the metric, tying §45+§60.

Run:  .venv/bin/python scripts/68_kerr_shadow.py
"""

import math
import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

M = 1.0


def r_photon(a, sign):
    """Equatorial circular photon-orbit radius; sign=-1 prograde, +1 retrograde."""
    return 2 * M * (1 + math.cos((2.0 / 3) * math.acos(sign * a / M)))


def b_at(a, r):
    """Critical impact parameters b=L/E at radius r (equatorial, R(r)=0)."""
    De = r * r - 2 * M * r + a * a
    bb = sp.Symbol("bb", real=True)
    return sorted(float(s) for s in sp.solve((r * r + a * a - a * bb)**2 - De * (bb - a)**2, bb))


def main():
    print("KERR PHOTON ORBITS & THE ASYMMETRIC SHADOW — the EHT image of spin\n")
    ok = []
    b0 = 3 * math.sqrt(3)                       # Schwarzschild ±3√3 M

    # (A) the radii split
    a0_pro, a0_ret = r_photon(0, -1), r_photon(0, 1)
    okA0 = abs(a0_pro - 3) < 1e-9 and abs(a0_ret - 3) < 1e-9
    splits = all(r_photon(a, -1) < 3 < r_photon(a, 1) for a in (0.3, 0.6, 0.9))
    ext_pro = r_photon(0.99999, -1)
    ext_ret = r_photon(0.99999, 1)
    okA = okA0 and splits and ext_pro < 1.05 and abs(ext_ret - 4) < 0.05
    ok.append(okA)
    print(f"  (A) light-ring radii: a=0 ⇒ both {a0_pro:.2f}M; a>0 ⇒ prograde < 3M < retrograde;")
    print(f"      extremal a→M ⇒ prograde {ext_pro:.3f}M (→ horizon), retrograde {ext_ret:.3f}M   "
          f"{'✅ frame dragging splits the ring' if okA else '❌'}")

    # (B) the shadow edges (critical impact parameters) — symmetric at a=0, asymmetric a>0
    print(f"\n  (B) shadow edges b=L/E (a=0 ⇒ ±3√3M = ±{b0:.3f}):")
    asym = []
    for a in (0.0, 0.5, 0.9):
        bp = min(x for x in b_at(a, r_photon(a, -1)) if x > 0)     # prograde edge (co-rotating)
        br = min(b_at(a, r_photon(a, 1)))                          # retrograde edge (negative root)
        asym.append((a, bp, br))
        print(f"        a={a}:  b_prograde = {bp:+.3f}M,  b_retrograde = {br:+.3f}M  "
              f"(|Δ| asymmetry {abs(abs(br)-abs(bp)):.3f}M)")
    okB = (abs(asym[0][1] - b0) < 1e-6 and abs(asym[0][2] + b0) < 1e-6        # a=0 symmetric
           and asym[1][1] < b0 < abs(asym[1][2])                              # a>0 asymmetric
           and asym[2][1] < b0 < abs(asym[2][2]))
    ok.append(okB)
    print(f"      ⇒ a=0 symmetric, a>0 |b_pro| < 3√3M < |b_ret|: the shadow is OFFSET   {'✅' if okB else '❌'}")

    # (C) extremal limit: b_pro → 2M, b_ret → −7M
    bp_ext = min(x for x in b_at(0.99999, r_photon(0.99999, -1)) if x > 0)
    br_ext = min(b_at(0.99999, r_photon(0.99999, 1)))
    okC = abs(bp_ext - 2) < 0.05 and abs(br_ext + 7) < 0.05
    ok.append(okC)
    print(f"\n  (C) extremal a→M: b_prograde → {bp_ext:.3f}M (want 2M), b_retrograde → {br_ext:.3f}M (want −7M)   "
          f"{'✅ strongly D-shaped' if okC else '❌'}")

    # (D) the synthesis
    okD = okA and okB and okC
    ok.append(okD)
    print(f"\n  (D) §45's circle + §60's frame dragging ⇒ the EHT's asymmetric shadow:")
    print(f"      a spinning hole's shape encodes its spin (M87*, Sgr A*)   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nKERR SHADOW: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(split light ring, displaced/D-shaped shadow, extremal 2M/7M edges)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
