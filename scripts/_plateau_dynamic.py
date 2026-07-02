#!/usr/bin/env python3
"""Item 1b — the DYNAMIC resonance plateau: frequency locking in TIME under slow Lz drift.

§107 exhibited the quasi-static staircase. The observable version: an EMRI's (E, Lz) drift slowly
under radiation reaction; when the evolving orbit's rotation number reaches a fat island (§107's 1/4),
the orbit is transiently TRAPPED -- the measured frequency ratio sits at the rational for a finite
TIME (the plateau in nu(t)) before releasing (Lukes-Gerakopoulos/Apostolatos/Contopoulos PRD 81
124005). Kerr under the same drift shows a smooth nu(t), no plateau.

Here the drift is a PRESCRIBED slow dLz/dtau (honest kludge: the magnitude is anchored to the §100/
§101 quadrupole-flux scale ~1e-6..1e-5 per tau for these orbits; self-consistent flux-updating changes
the rate, not the locking phenomenon). The trajectory is integrated continuously (RK4, L updated per
step -- adiabatic parameter), y=0 up-crossings recorded, and the rotation number measured in sliding
windows of W crossings. Start INSIDE the 1/4 island (x0=7.655, Lz=3.0) and drift Lz DOWN: the island
migrates; trapping shows as nu(t) HOLDING 0.25 while Lz sweeps a finite range, then releasing.

Checkpointed per window to data/plateau_dynamic_<tag>.txt (durable, _ckpt). Exploratory.
Repro: .venv/bin/python scripts/_plateau_dynamic.py [Ldot]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from _ckpt import ckpt_add, ckpt_load
from _plateau_v3_section import section_freq, zv_metric
from poincare import _rk4, build_hamilton

t, x, y, ph = sp.symbols("t x y phi", real=True)


def drift_run(f, s0, E, L0, Ldot, tag, n_cross=1200, W=80, h=0.02, maxst=30_000_000,
              bounds=((1.2, 200.0), (-1.0, 1.0))):
    """integrate with L(tau) = L0 + Ldot*tau; record y=0 up-crossings; every W/2 crossings emit the
    windowed rotation number of the last W crossings (checkpointed durable per window)."""
    ck = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                      f"plateau_dynamic_{tag}.txt")
    done = ckpt_load(ck)
    print(f"[{tag}] Ldot={Ldot:g}; {len(done)} windows already checkpointed")
    for line in done.values():
        print("   " + line)
    s = list(s0)
    xs = []
    prev = s[1]
    st = 0
    tau = 0.0
    wi = 0
    while len(xs) < n_cross and st < maxst:
        if not (bounds[0][0] <= s[0] <= bounds[0][1] and bounds[1][0] <= s[1] <= bounds[1][1]):
            print(f"   [{tag}] left bounds at tau={tau:.0f} ({len(xs)} crossings)")
            break
        L = L0 + Ldot * tau
        try:
            sn = _rk4(f, s, h, E, L)
        except (OverflowError, ZeroDivisionError, ValueError):
            print(f"   [{tag}] integrator raise at tau={tau:.0f} ({len(xs)} crossings)")
            break
        st += 1
        tau += h
        if prev < 0 <= sn[1]:
            xs.append(sn[0])
            if len(xs) >= W and len(xs) % (W // 2) == 0:
                wi += 1
                key = f"w{wi:03d}"
                if key not in done:
                    nu = section_freq(xs[-W:])
                    line = (f"{key}  tau={tau:9.0f}  L={L:.5f}  crossings={len(xs):4d}  "
                            f"nu={nu:.5f}  |nu-1/4|={abs(nu-0.25):.5f}")
                    ckpt_add(ck, key, line)
                    print("   " + line, flush=True)
        prev = sn[1]
        s = sn
    return


if __name__ == "__main__":
    Ldot = float(sys.argv[1]) if len(sys.argv) > 1 else -2e-7
    E, L0 = 0.95, 3.0
    fzv = build_hamilton(zv_metric(2.0, 1.0), [t, x, y, ph], 1, 2, 0, 3)
    x0 = 7.655                        # inside the 1/4 island at (E=0.95, Lz=3.0)
    val = (-1 - fzv["W"](x0, 0.0, E, L0)) / fzv["g22"](x0, 0.0, E, L0)
    drift_run(fzv, [x0, 0.0, 0.0, math.sqrt(val)], E, L0, Ldot, f"zv{abs(Ldot):g}")
