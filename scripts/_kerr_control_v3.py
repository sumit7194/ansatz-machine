#!/usr/bin/env python3
"""§107's Kerr control, corrected + resumable.

CORRECTION: the first control varied r0 at FIXED (E, L, p_theta) on the equator -- but that pins the
Carter constant, so every r0 lands on the SAME invariant torus (all four points read an identical
rotation number, correctly but uselessly). Each point must be a DISTINCT torus: launch at the radial
turning point (p_r=0, p_theta on-shell), like the ZV sweep. Integrable Kerr then shows a rotation
number varying SMOOTHLY with r0 -- no multi-step rational lock (resonant tori are measure-zero, no
islands). Checkpointed per point to data/kerr_control_v3.txt (resumable across power losses, _ckpt).

Exploratory. Repro: .venv/bin/python scripts/_kerr_control_v3.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _ckpt import ckpt_add, ckpt_load
from _plateau_v3_section import kerr_metric, ph, section_freq, t, x, y
from poincare import build_hamilton, section

CKPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "kerr_control_v3.txt")

if __name__ == "__main__":
    fk = build_hamilton(kerr_metric(), [t, x, y, ph], 1, 2, 0, 3)
    E, L = 0.95, 3.4
    done = ckpt_load(CKPT)
    print(f"KERR control v3 (p_r=0 turning-point launch -> distinct tori; {len(done)} pts already done):")
    print("    r0      sect-freq    nearest p/q (q<=8)")
    for line in done.values():
        print("   " + line)
    r0 = 7.90
    while r0 <= 8.21:
        key = f"{r0:.3f}"
        if key not in done:
            val = (-1 - fk["W"](r0, math.pi / 2, E, L)) / fk["g22"](r0, math.pi / 2, E, L)
            if val > 0:
                p2 = math.sqrt(val)
                pts, dr, st = section(fk, [r0, math.pi / 2, 0.0, p2], E, L, sec_idx=1,
                                      sec_val=math.pi / 2, rec=(0, 2), n=240, h=0.02,
                                      maxst=2_500_000, bounds=((1.9, 200.0), (0.2, math.pi - 0.2)))
                nu = section_freq([p[0] for p in pts])
                if nu is not None:
                    best = min(((p, q) for q in range(2, 9) for p in range(1, q)),
                               key=lambda pq: abs(nu - pq[0] / pq[1]))
                    dd = abs(nu - best[0] / best[1])
                    tag = f"  == {best[0]}/{best[1]} LOCKED?!" if dd < 3e-4 else ""
                    line = f"{key}   {nu:.5f}     {best[0]}/{best[1]} (|d|={dd:.5f}){tag}"
                else:
                    line = f"{key}   insufficient ({len(pts)} cross)"
                ckpt_add(CKPT, key, line)
                print("   " + line, flush=True)
        r0 += 0.02
    print("\ndone; results durable in data/kerr_control_v3.txt")
