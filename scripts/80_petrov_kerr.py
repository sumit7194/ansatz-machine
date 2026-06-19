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

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from numeric_curvature import petrov_type_numeric, weyl_scalars_numeric

M, A = 1.0, 0.6


def static_diag(ffun):
    """A static spherical diagonal metric g from a lapse function f(r)."""
    def g(x):
        _, r, th, _ = x
        f = ffun(r)
        return [[-f, 0, 0, 0], [0, 1 / f, 0, 0], [0, 0, r * r, 0],
                [0, 0, 0, r * r * math.sin(th)**2]]
    return g


def static_tetrad(x, ffun):
    """The standard null tetrad for the static spherical diagonal form."""
    _, r, th, _ = x
    f = ffun(r)
    s2 = math.sqrt(2)
    return ([1 / f, 1, 0, 0], [0.5, -f / 2, 0, 0],
            [0, 0, 1 / (r * s2), 1j / (r * s2 * math.sin(th))],
            [0, 0, 1 / (r * s2), -1j / (r * s2 * math.sin(th))])


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

    # (A) Kerr → type D at MANY points (stress-tested), with Ψ2 matching the exact form
    print("  (A) Kerr → type D across the spacetime, Ψ2 = −M/(r−ia cosθ)³ exactly:")
    allD = True
    for r in (3.0, 5.0, 8.0, 15.0, 30.0):
        for th in (0.6, 1.1, 1.5):
            x = [0.0, r, th, 0.0]
            P = weyl_scalars_numeric(kerr, x, kinnersley(x))
            ty = petrov_type_numeric(P)
            psi2_exact = -M / (r - 1j * A * math.cos(th))**3
            good = ty == "D" and abs(P[2] - psi2_exact) < 1e-4
            allD = allD and good
    ok.append(allD)
    print(f"      15 points (r∈[3,30] × θ): all type D and Ψ2 exact   {'✅' if allD else '❌'}")

    # (B) frame-independent speciality I³ = 27 J² (algebraically special, ⇒ D)
    x = [0.0, 5.0, 1.1, 0.0]
    P = weyl_scalars_numeric(kerr, x, kinnersley(x))
    P0, P1, P2, P3, P4 = P
    Iinv = P0 * P4 - 4 * P1 * P3 + 3 * P2**2
    Jinv = (P4 * (P2 * P0 - P1 * P1) - P3 * (P3 * P0 - P1 * P2) + P2 * (P3 * P1 - P2 * P2))
    okB = abs(Iinv**3 - 27 * Jinv**2) < 1e-6 * max(abs(Iinv**3), 1e-12)
    ok.append(okB)
    print(f"\n  (B) speciality I³−27J² ≈ {abs(Iinv**3 - 27*Jinv**2):.0e} ⇒ algebraically special (type D)   "
          f"{'✅' if okB else '❌'}")

    # (C) CROSS-CHECK the numeric pipeline vs §57's SYMBOLIC types (locks the classifier)
    schw = static_diag(lambda r: 1 - 2 / r)
    ds = static_diag(lambda r: 1 - 0.04 * r * r)        # de Sitter, H²=0.04
    xs = [0.0, 5.0, 1.0, 0.0]
    ty_s = petrov_type_numeric(weyl_scalars_numeric(schw, xs, static_tetrad(xs, lambda r: 1 - 2 / r)))
    xd = [0.0, 3.0, 1.0, 0.0]
    ty_d = petrov_type_numeric(weyl_scalars_numeric(ds, xd, static_tetrad(xd, lambda r: 1 - 0.04 * r * r)))
    okC = ty_s == "D" and ty_d == "O"
    ok.append(okC)
    print(f"\n  (C) cross-check vs §57 symbolic: Schwarzschild → {ty_s} (want D), de Sitter → {ty_d} (want O)")
    print(f"      — the numeric classifier agrees with the symbolic types (incl. conformally-flat O)   "
          f"{'✅' if okC else '❌'}")

    okD = allD and okB and okC
    ok.append(okD)
    print(f"\n  (D) the Petrov lens (§57) now covers Kerr (numeric companion, like §58/§69/§79)   "
          f"{'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nPETROV-KERR: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Kerr = type D at 15 points; de Sitter → O, Schwarzschild → D cross-check; §57 UNKNOWN closed)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
