#!/usr/bin/env python3
"""Option 1a v3 — the rotation-number staircase measured on the SECTION (the unambiguous instrument).

v2 (trajectory FFT) exposed a real subtlety: near strong resonances the trajectory spectrum is fully
commensurate with dominant subharmonics/sidebands (pericenter alternation), so 'pick the fundamental'
is ambiguous. The clean quantity is the ROTATION NUMBER measured on the Poincare section itself: the
dominant frequency (per crossing) of the section x-sequence -- the §105/§106-validated estimator.
Locked orbit => the sequence is q-periodic => frequency EXACTLY rational (p/q); circulating torus =>
irrational, varying smoothly with x0. The staircase's flat steps ARE the resonance islands.

Sweep: ZV delta=2, E=0.95, Lz=3, x0 in [7.50, 7.71]; Kerr control r0 sweep after.
Exploratory. Repro: .venv/bin/python scripts/_plateau_v3_section.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import sympy as sp

from poincare import build_hamilton, section

t, x, y, ph = sp.symbols("t x y phi", real=True)


def zv_metric(delta, sigma):
    s2 = sigma * sigma
    F = ((x - 1) / (x + 1))**delta
    H = ((x * x - 1) / (x * x - y * y))**(delta * delta)
    return sp.diag(-F, s2 / F * H * (x * x - y * y) / (x * x - 1),
                   s2 / F * H * (x * x - y * y) / (1 - y * y), s2 / F * (x * x - 1) * (1 - y * y))


def kerr_metric():
    a = sp.Rational(3, 5)
    r, th = x, y
    Sig = r**2 + a**2 * sp.cos(th)**2
    De = r**2 - 2 * r + a**2
    s2 = sp.sin(th)**2
    g = sp.zeros(4)
    g[0, 0] = -(1 - 2 * r / Sig)
    g[0, 3] = g[3, 0] = -2 * r * a * s2 / Sig
    g[1, 1] = Sig / De
    g[2, 2] = Sig
    g[3, 3] = (r**2 + a**2 + 2 * r * a**2 * s2 / Sig) * s2
    return g


def section_freq(series):
    """dominant per-crossing frequency of the section sequence (Hann + parabolic sub-bin) = the
    rotation number's fractional part. Rational lock p/q -> exactly p/q; torus -> irrational."""
    s = np.asarray(series, float)
    s = s - s.mean()
    n = len(s)
    if n < 60:
        return None
    F = np.abs(np.fft.rfft(s * np.hanning(n)))
    F[0] = 0.0
    k = int(np.argmax(F))
    if 1 <= k < len(F) - 1:
        a, b, c = F[k - 1], F[k], F[k + 1]
        d = 0.5 * (a - c) / (a - 2 * b + c + 1e-30)
    else:
        d = 0.0
    return (k + d) / n


if __name__ == "__main__":
    E, L = 0.95, 3.0
    fzv = build_hamilton(zv_metric(2.0, 1.0), [t, x, y, ph], 1, 2, 0, 3)
    print("ZV delta=2 staircase, SECTION rotation number (E=0.95, Lz=3):")
    print("    x0      sect-freq    nearest p/q (q<=8)      n")
    x0 = 7.500
    while x0 <= 7.712:
        val = (-1 - fzv["W"](x0, 0.0, E, L)) / fzv["g22"](x0, 0.0, E, L)
        if val > 0:
            py = math.sqrt(val)
            pts, dr, st = section(fzv, [x0, 0.0, 0.0, py], E, L, sec_idx=1, sec_val=0.0,
                                  rec=(0, 2), n=240, h=0.02, maxst=2_500_000,
                                  bounds=((1.2, 200.0), (-1.0, 1.0)))
            nu = section_freq([p[0] for p in pts])
            if nu is None:
                print(f"    {x0:6.3f}   (escaped/plunged, {len(pts)} cross)", flush=True)
            else:
                best = min(((p, q) for q in range(2, 9) for p in range(1, q)),
                           key=lambda pq: abs(nu - pq[0] / pq[1]))
                dd = abs(nu - best[0] / best[1])
                tag = f"  == {best[0]}/{best[1]} LOCKED" if dd < 3e-4 else ""
                print(f"    {x0:6.3f}   {nu:.5f}     {best[0]}/{best[1]} (|d|={dd:.5f})    {len(pts)}{tag}",
                      flush=True)
        x0 += 0.005

    print("\nKERR control (a=0.6, E=0.95, L=3.4, p_th=0.4; integrable -> no multi-step lock):")
    print("    r0      sect-freq    nearest p/q (q<=8)      n")
    fk = build_hamilton(kerr_metric(), [t, x, y, ph], 1, 2, 0, 3)
    r0 = 7.0
    while r0 <= 10.05:
        p2 = 0.4
        val = (-1 - fk["W"](r0, math.pi / 2, 0.95, 3.4) - fk["g22"](r0, math.pi / 2, 0.95, 3.4) * p2 * p2) \
            / fk["g11"](r0, math.pi / 2, 0.95, 3.4)
        if val > 0:
            p1 = math.sqrt(val)
            pts, dr, st = section(fk, [r0, math.pi / 2, p1, p2], 0.95, 3.4, sec_idx=1,
                                  sec_val=math.pi / 2, rec=(0, 2), n=240, h=0.02, maxst=2_500_000,
                                  bounds=((1.9, 200.0), (0.2, math.pi - 0.2)))
            nu = section_freq([p[0] for p in pts])
            if nu is not None:
                best = min(((p, q) for q in range(2, 9) for p in range(1, q)),
                           key=lambda pq: abs(nu - pq[0] / pq[1]))
                dd = abs(nu - best[0] / best[1])
                print(f"    {r0:6.3f}   {nu:.5f}     {best[0]}/{best[1]} (|d|={dd:.5f})    {len(pts)}",
                      flush=True)
        r0 += 0.25
