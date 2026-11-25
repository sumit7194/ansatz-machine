"""Diagnosis (office, 2026-11-26) of the circle's Dyson constant at spin 9/10 (Fable's d18de63 measured 478 per unit k,
against 10.5 at spin 3/5). A float measurement with the 50-digit engine, NOT a certificate.
At k_c = 21/20, along the circle |z| = R0 (720 points, base point R0):
  - dq/dk by a central difference in k of q(z; k) = (3/16)(G1'/G1 - G2'/G2)^2 (c0 from the engine's Laurent series);
  - the reference solution's first row (v1, v2) (fundamental matrix = I at the base point), by the engine's walker;
  - W = sum |dq/dk| |dz| r^dagger r, r = (v1, v2):
    base-basis constant = tr W;  optimised constant-gauge constant = 2 sqrt(det W) (the minimum over constant C of
    sum |dq/dk| |r C|^2 |dz| / |det C|; this is what Fable's gauge achieves at a point k).
Reports the profile along theta (where the integrand peaks) and the constants, for each (spin, R0) given.
    NVE_SPIN=9/10 nice -n 12 .venv/bin/python -u scripts/_nve_route1_circle_diag.py 1.2639 1.35 1.45"""
import math
import os
import sys

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_lower as L            # noqa: E402
import _nve_lower_kc as KC        # noqa: E402
import _nve_spin_scan as S        # noqa: E402

mp.mp.dps = 50
A = S.A
E2 = mp.mpf(16) / 25
KC_ = mp.mpf(21) / 20
H = mp.mpf("1e-10")
NPT = 720


def qval(C, z):
    c0, c0p = L.c0_eval(C, z), L.c0_eval(C, z, 1)
    Dp = z * z + A * A
    f0, f0p = (z * z - 2 * z + A * A) / Dp, 2 * (z * z - A * A) / Dp ** 2
    G2, G2p = f0 * f0 + c0 * c0, 2 * (f0 * f0p + c0 * c0p)
    G1, G1p = E2 * G2 - f0, E2 * G2p - f0p
    return mp.mpf(3) / 16 * (G1p / G1 - G2p / G2) ** 2


def run(R0):
    lau = S.LauA(mp.mpf(R0))
    pr = lau.problem(KC_)
    prp, prm = lau.problem(KC_ + H), lau.problem(KC_ - H)
    path = [KC_ * j / 40 for j in range(1, 41)]
    _p, st = S.track_laurent(path, S.kerr_points()[:4])
    sing = [x for x, _ in st]
    W = L.Walker(pr, sing, "0.35")
    pts = [mp.mpf(R0) * mp.expj(2 * mp.pi * j / NPT) for j in range(NPT + 1)]
    Y = KC.I2()
    W11 = W22 = mp.mpf(0)
    W12 = mp.mpc(0)
    prof = []
    dz = 2 * mp.pi * mp.mpf(R0) / NPT
    for j in range(NPT):
        zm = mp.mpf(R0) * mp.expj(2 * mp.pi * (j + 0.5) / NPT)
        Ym = W.walk([pts[j], zm], Y)                         # first row at the midpoint
        v1, v2 = Ym[0][0], Ym[0][1]
        dq = abs((qval(prp.C, zm) - qval(prm.C, zm)) / (2 * H))
        w = dq * dz
        W11 += w * abs(v1) ** 2
        W22 += w * abs(v2) ** 2
        W12 += w * mp.conj(v1) * v2
        prof.append((float(mp.arg(zm)) * 180 / math.pi, float(dq), float(abs(v1) ** 2 + abs(v2) ** 2), float(dq * (abs(v1) ** 2 + abs(v2) ** 2))))
        Y = W.walk([pts[j], pts[j + 1]], Y)
    det = W11 * W22 - abs(W12) ** 2
    base, opt = float(W11 + W22), float(2 * mp.sqrt(det))
    tr0 = Y[0][0] + Y[1][1]
    print(f"spin {S.SPIN}, R0 = {R0}: constant per unit k at k_c = 21/20: base basis {base:.2f}, optimised gauge {opt:.2f}; "
          f"int |dq/dk| |dz| = {sum(p[1] for p in prof) * float(dz):.3f}; tr M0(k_c) = {mp.nstr(tr0, 8)} (closure check)", flush=True)
    srt = sorted(prof, key=lambda p: -p[3])
    print("   largest integrand |dq/dk| |v|^2 at theta (deg): " + ", ".join(f"{p[0]:.1f} ({p[3]:.3g}; |dq/dk| {p[1]:.3g}, |v|^2 {p[2]:.3g})" for p in srt[:4]))
    for lo, hi in ((-180, -135), (-135, -45), (-45, 45), (45, 135), (135, 180)):
        sel = [p for p in prof if lo <= p[0] < hi]
        print(f"   theta in [{lo}, {hi}): share of base-basis integral {sum(p[3] for p in sel) / sum(p[3] for p in prof):.3f}; "
              f"max |dq/dk| {max(p[1] for p in sel):.3g}; max |v|^2 {max(p[2] for p in sel):.3g}")
    print(f"   nearest inner singularities: +-ia at distance {R0 - float(A):.4f}; Laurent ratio rho_c/R0 = {float(pr.rho) / R0:.3f}", flush=True)


for r in sys.argv[1:]:
    run(float(r))
