#!/usr/bin/env python3
"""Step 80 — PETROV TYPE OF KERR (numeric): completing the lens off-diagonal.

§57 classified the Petrov type of static (diagonal) metrics but returned UNKNOWN for
Kerr — `analyzer.petrov` skips off-diagonal because Kerr's symbolic Weyl tensor swamps
(the §48/§57 limit; the Killing-tensor proof §78 dodged it by needing only Christoffels,
but Petrov genuinely needs Weyl). This completes the lens for Kerr the same way §58/§69/
§79 handle Kerr's other hard quantities — NUMERICALLY (finite-difference Weyl, which
trig doesn't faze): `numeric_curvature.weyl_scalars_numeric` + `petrov_type_numeric`.

  (A) Kerr's Weyl scalars in the Kinnersley tetrad: only Ψ2 ≠ 0 (Ψ0,Ψ1,Ψ3,Ψ4 ~ 1e-10)
      ⇒ type D — the canonical rotating-black-hole signature, now obtained off-diagonal;
  (B) Ψ2 matches the exact closed form −M/(r − i a cosθ)³ (Kerr's single curvature
      scalar) — a strong correctness check, not just a pattern;
  (C) the frame-independent speciality I³ = 27 J² holds (Kerr is algebraically special),
      computed from the numeric Ψ's — consistent with type D;
  (D) so the Petrov lens (§57) now covers Kerr too. (Kept as a NUMERIC companion, like
      §58/§69/§79 for Kerr; `analyzer.petrov` stays symbolic + perf-guarded — a fully
      automatic principal-null-direction finder for arbitrary metrics is the general
      extension.)

Run:  .venv/bin/python scripts/80_petrov_kerr.py
"""

import cmath
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from numeric_curvature import petrov_type_numeric, weyl_scalars_numeric

M, A = 1.0, 0.6


def kerr(x):
    _, r, th, _ = x
    Sig = r * r + A * A * math.cos(th)**2
    De = r * r - 2 * M * r + A * A
    s2 = math.sin(th)**2
    g = [[0.0] * 4 for _ in range(4)]
    g[0][0] = -(1 - 2 * M * r / Sig)
    g[0][3] = g[3][0] = -2 * M * r * A * s2 / Sig
    g[1][1] = Sig / De
    g[2][2] = Sig
    g[3][3] = (r * r + A * A + 2 * M * r * A * A * s2 / Sig) * s2
    return g


def kinnersley(x):
    """The Kinnersley null tetrad (l, n, m, mbar) for Kerr at x (Boyer–Lindquist)."""
    _, r, th, _ = x
    Sig = r * r + A * A * math.cos(th)**2
    De = r * r - 2 * M * r + A * A
    sth, cth = math.sin(th), math.cos(th)
    s2 = math.sqrt(2)
    rho = r + 1j * A * cth
    l = [(r * r + A * A) / De, 1, 0, A / De]
    n = [(r * r + A * A) / (2 * Sig), -De / (2 * Sig), 0, A / (2 * Sig)]
    m = [1j * A * sth / (s2 * rho), 0, 1 / (s2 * rho), 1j / (sth * s2 * rho)]
    mb = [z.conjugate() for z in m]
    return l, n, m, mb


def main():
    print("PETROV TYPE OF KERR (numeric) — completing the lens off-diagonal\n")
    ok = []
    x = [0.0, 5.0, 1.1, 0.0]
    P = weyl_scalars_numeric(kerr, x, kinnersley(x))

    # (A) only Ψ2 ≠ 0 ⇒ type D
    big = max(abs(p) for p in P)
    pattern = [("≠0" if abs(p) / big > 1e-6 else "0") for p in P]
    ty = petrov_type_numeric(P)
    okA = ty == "D" and pattern == ["0", "0", "≠0", "0", "0"]
    ok.append(okA)
    print(f"  (A) Kerr Weyl scalars (Kinnersley tetrad): |Ψ| pattern = {pattern} → type {ty}")
    print(f"      (Ψ0,Ψ1,Ψ3,Ψ4 ~ {max(abs(P[k]) for k in (0,1,3,4)):.0e}, Ψ2 = {abs(P[2]):.3e})   "
          f"{'✅ canonical type D, off-diagonal' if okA else '❌'}")

    # (B) Ψ2 matches the exact −M/(r − i a cosθ)³
    r, th = x[1], x[2]
    psi2_exact = -M / (r - 1j * A * math.cos(th))**3
    okB = abs(P[2] - psi2_exact) < 1e-5
    ok.append(okB)
    print(f"\n  (B) Ψ2 = {P[2]:.6f}  vs exact −M/(r−ia cosθ)³ = {psi2_exact:.6f}   {'✅' if okB else '❌'}")

    # (C) frame-independent speciality I³ = 27 J² (from the numeric Ψ's)
    P0, P1, P2, P3, P4 = P
    Iinv = P0 * P4 - 4 * P1 * P3 + 3 * P2**2
    Jinv = (P4 * (P2 * P0 - P1 * P1) - P3 * (P3 * P0 - P1 * P2) + P2 * (P3 * P1 - P2 * P2))
    okC = abs(Iinv**3 - 27 * Jinv**2) < 1e-6 * max(abs(Iinv**3), 1e-12)
    ok.append(okC)
    print(f"\n  (C) speciality I³−27J² = {abs(Iinv**3 - 27*Jinv**2):.1e} ≈ 0 ⇒ algebraically special (type D)   "
          f"{'✅' if okC else '❌'}")

    okD = okA and okB and okC
    ok.append(okD)
    print(f"\n  (D) the Petrov lens (§57) now covers Kerr (numeric companion, like §58/§69/§79)   "
          f"{'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nPETROV-KERR: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Kerr = type D numerically; Ψ2 matches −M/(r−ia cosθ)³; the §57 UNKNOWN, closed)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
