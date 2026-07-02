#!/usr/bin/env python3
"""Option 1a — the quasi-static resonance plateau: rotation-number staircase across the ZV island.

Inside a resonance island the frequency ratio nu_x/nu_y is LOCKED to the rational across the island's
finite width; in integrable Kerr, resonances are measure-zero -- the ratio passes through the rational
smoothly with no locking (Lukes-Gerakopoulos/Apostolatos/Contopoulos PRD 81 124005's plateau). This
sweeps launch radius x0 across §106's ZV delta=2 island (E=0.95, Lz=3; island band x0~7.549-7.563).
FIRST-PASS FINDING: the island-centre (x0=7.560) ratio measured 0.49994 -> the §106 chain is the 1:2
resonance (not the 2/3 inferred from the literature quote); a naive dominant-FFT-peak estimator is fooled
off-centre by libration peaks, so the estimator here anchors on TURNING-POINT COUNTS and FFT-refines
within +-30% of that coarse value (~1e-4 relative resolution). Expect: a FLAT step at 0.50000 across the
island (the staircase plateau), then a Kerr control sweep with no flat step.

Exploratory. Repro: .venv/bin/python scripts/_plateau_quasistatic.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import sympy as sp

from poincare import build_hamilton, _rk4

t, x, y, ph = sp.symbols("t x y phi", real=True)


def zv_metric(delta, sigma):
    s2 = sigma * sigma
    F = ((x - 1) / (x + 1))**delta
    H = ((x * x - 1) / (x * x - y * y))**(delta * delta)
    return sp.diag(-F, s2 / F * H * (x * x - y * y) / (x * x - 1),
                   s2 / F * H * (x * x - y * y) / (1 - y * y), s2 / F * (x * x - 1) * (1 - y * y))


def kerr_metric():
    a = sp.Rational(3, 5)
    r, th = x, y                                            # reuse symbols: q1=r, q2=theta
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


def fund_freq(series, dsig, dt):
    """FUNDAMENTAL frequency of a uniformly-sampled oscillation, robust to libration/harmonic peaks:
    coarse nu from counting the derivative-signal's sign changes (turning points), then FFT-refine to
    the strongest peak within +-30% of the coarse value (Hann window + parabolic sub-bin)."""
    s = np.asarray(series, float)
    s = s - s.mean()
    n = len(s)
    d = np.asarray(dsig, float)
    flips = int(np.sum(np.abs(np.diff(np.signbit(d)))))       # 2 turning points per period
    nu0 = 0.5 * flips / (n * dt)
    F = np.abs(np.fft.rfft(s * np.hanning(n)))
    F[0] = 0.0
    klo = max(int(0.7 * nu0 * n * dt), 1)
    khi = min(int(1.3 * nu0 * n * dt) + 2, len(F) - 2)
    if khi <= klo:
        return nu0
    k = klo + int(np.argmax(F[klo:khi]))
    a, b, c = F[k - 1], F[k], F[k + 1]
    dd = 0.5 * (a - c) / (a - 2 * b + c + 1e-30)
    return (k + dd) / (n * dt)


def freq_ratio(f, s0, E, L, h=0.02, rec_every=8, n_samp=200_000, bounds=None):
    """integrate the reduced trajectory -> fundamental nu_x/nu_y via turning-point-anchored FFT."""
    s = list(s0)
    xs, ys, pxs, pys = [], [], [], []
    for i in range(n_samp * rec_every):
        if bounds is not None and not (bounds[0][0] <= s[0] <= bounds[0][1]
                                       and bounds[1][0] <= s[1] <= bounds[1][1]):
            break
        try:
            s = _rk4(f, s, h, E, L)
        except (OverflowError, ZeroDivisionError, ValueError):
            break
        if i % rec_every == 0:
            xs.append(s[0]); ys.append(s[1]); pxs.append(s[2]); pys.append(s[3])
    if len(xs) < 20_000:
        return None, len(xs)
    dt = h * rec_every
    return fund_freq(xs, pxs, dt) / fund_freq(ys, pys, dt), len(xs)


if __name__ == "__main__":
    E, L = 0.95, 3.0
    RAT = 0.5    # the §106 island is the 1:2 resonance (island-centre ratio measured 0.49994)
    fzv = build_hamilton(zv_metric(2.0, 1.0), [t, x, y, ph], 1, 2, 0, 3)
    print(f"ZV delta=2 sweep across the §106 island (E=0.95, Lz=3): ratio LOCKS at 1/2 = {RAT}?")
    print("    x0      nu_x/nu_y    |ratio-1/2|   n")
    x0 = 7.500
    while x0 <= 7.705:
        val = (-1 - fzv["W"](x0, 0.0, E, L)) / fzv["g22"](x0, 0.0, E, L)
        if val > 0:
            py = math.sqrt(val)
            r, n = freq_ratio(fzv, [x0, 0.0, 0.0, py], E, L, bounds=((1.2, 200.0), (-1.0, 1.0)))
            if r is None:
                print(f"    {x0:6.3f}   (escaped/plunged, {n} samples)", flush=True)
            else:
                tag = "  <<< LOCKED" if abs(r - RAT) < 4e-4 else ""
                print(f"    {x0:6.3f}   {r:.5f}     {abs(r-RAT):.5f}    {n}{tag}", flush=True)
        x0 += 0.005

    print("\nKERR control sweep (a=0.6, E=0.95, L=3.4, p_th=0.4 launch; integrable -> no locking width):")
    print("    r0      nu_r/nu_th   |ratio-1/2|   n")
    fk = build_hamilton(kerr_metric(), [t, x, y, ph], 1, 2, 0, 3)
    r0 = 7.0
    while r0 <= 10.05:
        p2 = 0.4
        val = (-1 - fk["W"](r0, math.pi / 2, 0.95, 3.4) - fk["g22"](r0, math.pi / 2, 0.95, 3.4) * p2 * p2) \
            / fk["g11"](r0, math.pi / 2, 0.95, 3.4)
        if val > 0:
            p1 = math.sqrt(val)
            r, n = freq_ratio(fk, [r0, math.pi / 2, p1, p2], 0.95, 3.4,
                              bounds=((1.9, 200.0), (0.2, math.pi - 0.2)))
            if r is not None:
                tag = "  (crosses 1/2 here)" if abs(r - RAT) < 4e-4 else ""
                print(f"    {r0:6.3f}   {r:.5f}     {abs(r-RAT):.5f}    {n}{tag}", flush=True)
        r0 += 0.25
