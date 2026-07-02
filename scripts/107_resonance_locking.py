#!/usr/bin/env python3
"""Step 107 — the devil's staircase: resonance frequency-LOCKING in a bumpy black hole (plan item 1a).

The quasi-static half of the LISA bumpy-metric signature (Lukes-Gerakopoulos/Apostolatos/Contopoulos
PRD 81 124005): inside a resonance island the orbit's rotation number is LOCKED to the rational across
the island's finite width; in integrable Kerr, resonant tori are measure-zero -- no islands, no locking
width. §106 found ZV delta=2's island chain; this sweeps ACROSS it and exhibits the staircase:

  plunge | chaotic layer | 1/5 LOCK (x0 7.555-7.565: nu = 0.20000 EXACT) | layer |
  smooth climb (0.2141 -> 0.2458 over 13 steps, ~0.002/step) |
  1/4 LOCK (x0 7.645-7.665: nu = 0.25000 EXACT, FIVE steps -- the approach SNAPS from 0.2458
  onto the rational and HOLDS) | release (0.2539 ->) -- two rational plateaus, the fatter one the
  lower-order resonance (KAM ordering).

The instrument is the SECTION-sequence dominant frequency (the §105-validated estimator): a locked
orbit's section sequence is q-periodic => frequency EXACTLY p/q; a circulating torus varies smoothly.
(Two trajectory-FFT estimators were tried first and FOOLED -- by libration peaks, then by the fully
COMMENSURATE spectra near locks; the section measurement is unambiguous, and the commensurate
trajectory spectra independently CONFIRM the locks.) Kerr control: distinct tori (p_r=0 launches, the
same convention) show a smoothly varying rotation number, no multi-step lock. This is why a bumpy-metric
EMRI crossing a resonance would show a FREQUENCY PLATEAU (item 1b makes it dynamic).

Optional dep: numpy. Repro: .venv/bin/python scripts/107_resonance_locking.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import numpy as np  # noqa: F401
    _HAVE_NUMPY = True
except ImportError:
    _HAVE_NUMPY = False

LOCK_TOL = 3e-4


def main():
    if not _HAVE_NUMPY:
        print("RESONANCE LOCKING: SKIPPED (numpy not installed)")
        return 0

    import sympy as sp
    from poincare import build_hamilton, section

    from _plateau_v3_section import kerr_metric, section_freq, zv_metric

    t, x, y, ph = sp.symbols("t x y phi", real=True)

    def nu_of(f, s0, E, L, bnds):
        pts, dr, st = section(f, s0, E, L, sec_idx=1, sec_val=s0[1], rec=(0, 2),
                              n=200, h=0.02, maxst=2_000_000, bounds=bnds)
        return section_freq([p[0] for p in pts]), len(pts)

    print("RESONANCE FREQUENCY-LOCKING — the devil's staircase (ZV delta=2 vs Kerr)\n")
    ok = []
    E, L = 0.95, 3.0
    fzv = build_hamilton(zv_metric(2.0, 1.0), [t, x, y, ph], 1, 2, 0, 3)
    zb = ((1.2, 200.0), (-1.0, 1.0))

    def zv_nu(x0):
        val = (-1 - fzv["W"](x0, 0.0, E, L)) / fzv["g22"](x0, 0.0, E, L)
        return nu_of(fzv, [x0, 0.0, 0.0, math.sqrt(val)], E, L, zb)

    # (A) the 1/5 island: two interior orbits LOCKED at exactly 1/5
    nA1, _ = zv_nu(7.555)
    nA2, _ = zv_nu(7.560)
    okA = nA1 is not None and nA2 is not None and abs(nA1 - 0.2) < LOCK_TOL and abs(nA2 - 0.2) < LOCK_TOL
    ok.append(okA)
    print(f"  (A) 1/5 island (x0=7.555, 7.560): nu = {nA1:.5f}, {nA2:.5f}  -> LOCKED at 1/5   "
          f"{'✅' if okA else '❌'}")

    # (B) circulating tori between the islands: off-lock AND moving (the staircase's risers)
    nB1, _ = zv_nu(7.585)
    nB2, _ = zv_nu(7.605)
    okB = (nB1 is not None and nB2 is not None
           and min(abs(nB1 - p / q) for q in range(2, 9) for p in range(1, q)) > 3e-3
           and min(abs(nB2 - p / q) for q in range(2, 9) for p in range(1, q)) > 3e-3
           and abs(nB2 - nB1) > 5e-3)
    ok.append(okB)
    print(f"  (B) tori between islands (7.585, 7.605): nu = {nB1:.5f}, {nB2:.5f}  -> off-lock, MOVING "
          f"(d={abs(nB2-nB1):.4f})   {'✅' if okB else '❌'}")

    # (C) the 1/4 island: two interior orbits LOCKED at exactly 1/4 (the fatter, lower-order island)
    nC1, _ = zv_nu(7.650)
    nC2, _ = zv_nu(7.660)
    okC = nC1 is not None and nC2 is not None and abs(nC1 - 0.25) < LOCK_TOL and abs(nC2 - 0.25) < LOCK_TOL
    ok.append(okC)
    print(f"  (C) 1/4 island (x0=7.650, 7.660): nu = {nC1:.5f}, {nC2:.5f}  -> LOCKED at 1/4   "
          f"{'✅' if okC else '❌'}")

    # (D) KERR control: distinct tori (p_r=0 launches) -> smoothly varying, NO lock at any low-order
    # rational (integrable => resonant tori measure-zero, no islands)
    fk = build_hamilton(kerr_metric(), [t, x, y, ph], 1, 2, 0, 3)
    kb = ((1.9, 200.0), (0.2, math.pi - 0.2))
    Ek, Lk = 0.95, 3.4
    nus = []
    for r0 in (7.90, 8.05, 8.20):
        val = (-1 - fk["W"](r0, math.pi / 2, Ek, Lk)) / fk["g22"](r0, math.pi / 2, Ek, Lk)
        nu, _ = nu_of(fk, [r0, math.pi / 2, 0.0, math.sqrt(val)], Ek, Lk, kb)
        nus.append(nu)
    # Kerr's nu(r0) gradient is ~10x gentler than ZV's (measured ~7e-4 per 0.1 in r0), so the
    # "moving" threshold is matched to that scale; the no-lock margin (|d|~0.016) is huge regardless.
    okD = (all(n is not None for n in nus)
           and all(min(abs(n - p / q) for q in range(2, 9) for p in range(1, q)) > LOCK_TOL for n in nus)
           and max(nus) - min(nus) > 5e-4)
    ok.append(okD)
    print(f"  (D) Kerr control (r0=7.90,8.05,8.20): nu = " + ", ".join(f"{n:.5f}" for n in nus))
    print(f"      no rational lock, smoothly varying (spread {max(nus)-min(nus):.4f})   "
          f"{'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nRESONANCE LOCKING: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(devil's staircase: 1/5 and 1/4 plateaus in the bumpy metric; no locking in Kerr)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
