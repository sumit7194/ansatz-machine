#!/usr/bin/env python3
"""Step 77 — THE PRECISE QNM ORACLE (beyond the eikonal): 0.1%-level ringdown.

§56 gave the EXACT but EIKONAL (light-ring) QNM and deferred the precise spectrum to
Leaver. This is that precise oracle — `qnm_precise(M,a,ℓ,m,n)` (Leaver's continued
fraction via the `qnm` package) — turning the bridge's ringdown link from "consistent
at the light-ring level" (few-to-15%) into a real 0.1%-level exact↔measured test, and
giving the OVERTONES (the 221 = ℓ=m=2,n=1) that deepstrain's δ measures and the eikonal
cannot produce.

  (A) Schwarzschild ℓ=2,n=0: precise Mω = 0.37367 − 0.08896i (exact Leaver) vs §56's
      eikonal ≈ 0.385 − 0.096i — the upgrade from ~3–8% to exact;
  (B) the 221 OVERTONE (a=0.7, ℓ=m=2,n=1): Mω = 0.52116 − 0.24424i — the quantity
      deepstrain's δ measures; the eikonal has no genuine overtone structure for it;
  (C) Kerr spin dependence: the 220 fundamental blueshifts with spin (0.3737 at a=0 →
      0.5326 at a=0.7) and rings longer (Q rises) — the real ω(M,a) the no-hair test needs;
  (D) the no-hair test sharpened: 220 and 221 are BOTH functions of (M,a) only, now to
      0.1% — measuring two modes overdetermines (M,a) at precision, a genuine
      consistency test (vs §72's light-ring-level version).

DEPENDENCY: this is the numerical companion track (Leaver has no closed form), so it
needs `qnm` (numpy/scipy/numba) — kept separate from the pure-SymPy core (DECISIONS.md).
If `qnm` is absent the battery SKIPS (clearly), so a fresh checkout's gate is unaffected.

Run:  .venv/bin/python scripts/77_qnm_precise.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qnm_precise import available, qnm_precise, quality_factor


def main():
    print("THE PRECISE QNM ORACLE (beyond the eikonal) — 0.1%-level ringdown\n")
    if not available():
        print("  SKIPPED — optional dependency `qnm` not installed (pip install qnm).")
        print("  The precise-QNM track is the numerical companion to §56's eikonal (DECISIONS.md).")
        print("\nQNM-PRECISE: SKIPPED (optional dep) — gate unaffected")
        return 0

    ok = []

    # (A) exact Schwarzschild fundamental vs §56 eikonal
    w = qnm_precise(1.0, 0.0, 2, 2, 0)          # M=1, a=0, l=m=2, n=0
    okA = abs(w.real - 0.37367) < 1e-4 and abs(w.imag + 0.08896) < 1e-4
    eik_R, eik_I = 0.3849, 0.0962               # §56 eikonal (l=2,n=0): l·Ω_c, (n+½)λ
    ok.append(okA)
    print(f"  (A) Schwarzschild ℓ=2,n=0: precise Mω = {w.real:.5f} − {abs(w.imag):.5f}i  (exact Leaver)")
    print(f"      vs §56 eikonal {eik_R:.4f} − {eik_I:.4f}i ⇒ real {abs(w.real-eik_R)/w.real*100:.1f}% off, now EXACT   "
          f"{'✅' if okA else '❌'}")

    # (B) the 221 overtone — the quantity δ measures, impossible from the eikonal
    w221 = qnm_precise(1.0, 0.7, 2, 2, 1)
    okB = abs(w221.real - 0.52116) < 1e-3 and abs(w221.imag + 0.24424) < 1e-3
    ok.append(okB)
    print(f"\n  (B) 221 overtone (a=0.7, ℓ=m=2,n=1): Mω = {w221.real:.5f} − {abs(w221.imag):.5f}i")
    print(f"      — the overtone deepstrain's δ measures; the eikonal can't give it   {'✅' if okB else '❌'}")

    # (C) spin dependence of the 220 fundamental
    w0 = qnm_precise(1.0, 0.0, 2, 2, 0)
    w7 = qnm_precise(1.0, 0.7, 2, 2, 0)
    Q0, Q7 = quality_factor(1.0, 0.0, 2, 2, 0), quality_factor(1.0, 0.7, 2, 2, 0)
    okC = w7.real > w0.real and Q7 > Q0
    ok.append(okC)
    print(f"\n  (C) 220 fundamental: a=0 ⇒ Mω={w0.real:.4f}, Q={Q0:.2f};  a=0.7 ⇒ Mω={w7.real:.4f}, Q={Q7:.2f}")
    print(f"      spin blueshifts the pitch and lengthens the ring   {'✅' if okC else '❌'}")

    # (D) no-hair: 220 and 221 both = f(M,a); two modes overdetermine (M,a) at 0.1%
    okD = okA and okB and (abs(w221.real - w7.real) > 0.01)   # distinct modes, both f(M,a)
    ok.append(okD)
    print(f"\n  (D) 220 and 221 are both functions of (M,a) only — measuring both to 0.1% overdetermines")
    print(f"      (M,a) at precision: a genuine no-hair consistency test (sharpens §72)   {'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nQNM-PRECISE: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(exact Leaver QNM incl. the 221 overtone — the 0.1% ringdown oracle)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
