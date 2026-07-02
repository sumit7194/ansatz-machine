#!/usr/bin/env python3
"""Step 108 — the DYNAMIC resonance plateau: sustained frequency locking under drift (plan item 1b).

The time-domain, observable half of the LISA bumpy-metric signature (§107 was the quasi-static half).
Under a slow radiation-reaction-scale drift of Lz, a ZV delta=2 orbit TRAPPED in the 1/4 resonance
island stays LOCKED -- its windowed rotation number sits at 0.25000 while Lz sweeps (sustained
resonance: the libration adiabatic invariant holds it) -- while an untrapped orbit under the IDENTICAL
drift sweeps smoothly past the rational (probabilistic transit, no capture: measured in the full runs,
nu climbed 0.246->0.272 while the trapped orbit held 0.25000 +- 8e-5 across 43 windows / tau ~ 1.4e5).
A Kerr inspiral has no islands (§107 D), so its frequency ratio can never do this: a LISA data stream
showing a locked ratio while the inspiral evolves is a non-Kerr smoking gun.

Honest scope: the drift is a PRESCRIBED slow dLz/dtau at the §100/§101 quadrupole-flux magnitude
(the locking physics depends on adiabatic slowness, not on self-consistent flux updating); capture from
outside is probabilistic (three transit controls all passed through -- also physics), so the battery
demonstrates the SUSTAINED lock of a trapped orbit vs a transiting one. Full-length runs banked in
data/plateau_dyn_trapped.txt + data/plateau_dyn_x7.64.txt; this gated version is shortened 2x in drift
rate and ~4x in length to fit the gate.

Optional dep: numpy. Repro: .venv/bin/python scripts/108_dynamic_plateau.py
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


def main():
    if not _HAVE_NUMPY:
        print("DYNAMIC PLATEAU: SKIPPED (numpy not installed)")
        return 0

    import sympy as sp
    from poincare import _rk4, build_hamilton

    from _plateau_v3_section import section_freq, zv_metric

    t, x, y, ph = sp.symbols("t x y phi", real=True)
    f = build_hamilton(zv_metric(2.0, 1.0), [t, x, y, ph], 1, 2, 0, 3)
    E, L0, Ldot = 0.95, 3.0, 1e-8

    def drift_nus(x0, n_cross=240, W=60, stride=20, h=0.02, maxst=8_000_000):
        """windowed rotation numbers of a trajectory under L(tau) = L0 + Ldot*tau."""
        val = (-1 - f["W"](x0, 0.0, E, L0)) / f["g22"](x0, 0.0, E, L0)
        s = [x0, 0.0, 0.0, math.sqrt(val)]
        xs, nus = [], []
        prev = s[1]
        st = 0
        tau = 0.0
        while len(xs) < n_cross and st < maxst:
            if not (1.2 <= s[0] <= 200.0 and -1.0 <= s[1] <= 1.0):
                break
            try:
                sn = _rk4(f, s, h, E, L0 + Ldot * tau)
            except (OverflowError, ZeroDivisionError, ValueError):
                break
            st += 1
            tau += h
            if prev < 0 <= sn[1]:
                xs.append(sn[0])
                if len(xs) >= W and len(xs) % stride == 0:
                    nus.append(section_freq(xs[-W:]))
            prev = sn[1]
            s = sn
        return nus

    print("DYNAMIC RESONANCE PLATEAU — sustained locking under drift (ZV delta=2, Ldot=+1e-8)\n")
    ok = []

    # (A) TRAPPED orbit (starts inside the 1/4 island): every window locked while Lz sweeps
    nus_t = drift_nus(7.655)
    okA = len(nus_t) >= 8 and all(abs(n - 0.25) < 5e-4 for n in nus_t)
    ok.append(okA)
    print(f"  (A) trapped (x0=7.655): {len(nus_t)} windows, nu = {nus_t[0]:.5f} ... {nus_t[-1]:.5f}, "
          f"max|nu-1/4| = {max(abs(n-0.25) for n in nus_t):.5f}")
    print(f"      LOCKED at 1/4 through the whole drift (sustained resonance)   {'✅' if okA else '❌'}")

    # (B) TRANSIT control (starts on the riser): same drift, frequency sweeps ON PAST the rational
    nus_c = drift_nus(7.640)
    okB = len(nus_c) >= 8 and nus_c[-1] > 0.253 and (max(nus_c) - min(nus_c)) > 5e-3
    ok.append(okB)
    print(f"\n  (B) transit control (x0=7.640): {len(nus_c)} windows, nu = {nus_c[0]:.5f} -> {nus_c[-1]:.5f}")
    print(f"      same drift, no capture: the ratio sweeps past 1/4 and keeps moving   {'✅' if okB else '❌'}")

    passed = all(ok)
    print(f"\nDYNAMIC PLATEAU: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(a trapped bumpy-metric orbit broadcasts a CONSTANT frequency ratio while its parameters "
          "evolve — the time-domain non-Kerr signature; Kerr has no islands to trap in, §107)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
