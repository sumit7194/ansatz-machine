#!/usr/bin/env python3
"""Float check of loop closure for a finite-loop c0 (seal: data/nve/route1_check/CLOSURE_STOPC_SEAL.md §2).

c0'' = -sqrt(8/5) a^3 sqrt(B(z^2/a^2, k)) / (z^2 + a^2)^3, sqrt continued by continuity from the base point (on the
positive real axis, where B > 0 and the global branch is the positive root). For a loop gamma based at z_s:
    dc1 = oint c0'' dz,  dc0 = z_s dc1 - oint z c0'' dz,  sheet = sqrt at the end / sqrt at the start (+1 or -1).
The formula for (c0'')^2 is checked against the code's radicand (_nve_lower_kc N0, N1, DEN) at a test point first.
    NVE_SPIN=<a> python scripts/_closure_check.py
"""
import os
import sys
import time

import mpmath as mp
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_lower_kc as KC          # noqa: E402  (reads NVE_SPIN)

mp.mp.dps = 50
SPIN = os.environ.get("NVE_SPIN", "3/5")
A = mp.mpf(sp.N(sp.Rational(SPIN), 60))
R0 = {"3/10": "1.1492", "3/5": "1.35", "4/5": "1.3382", "9/10": "1.2639"}[SPIN]
Z0 = {"3/10": "1.9540", "3/5": "2", "4/5": "1.6181", "9/10": "1.4926"}[SPIN]
R0, Z0 = mp.mpf(R0), mp.mpf(Z0)
KS = [mp.mpf(3), mp.mpf("3.5"), mp.mpf("3.9"), 4 - mp.mpf(10) ** -6, mp.mpf("4.02"), mp.mpf("4.1"), mp.mpf("4.2"),
      mp.mpf("4.25"), mp.mpf("4.28"), mp.mpf(30) / 7 - mp.mpf(10) ** -6]


def Bw(w, k):
    return (90 - 21 * k) * w**2 - (60 - 18 * k) * w + (10 - k)


def c0pp_sq(z, k):
    return mp.mpf(8) / 5 * A**6 * Bw(z**2 / A**2, k) / (z**2 + A**2) ** 6


def check_formula(k):
    zt = mp.mpc("1.7", "0.4")
    dN = max(KC.N0.degree(), KC.N1.degree())
    nc = [x + k * y for x, y in zip(KC._asc(KC.N0, dN), KC._asc(KC.N1, dN))]
    dc = KC._asc(KC.DEN, KC.DEN.degree())
    R = mp.polyval(list(reversed(nc)), zt) / mp.polyval(list(reversed(dc)), zt)
    return abs(R - c0pp_sq(zt, k)) / abs(R)


def sing(k):
    a_, b_, c_ = 90 - 21 * k, -(60 - 18 * k), 10 - k
    d = mp.sqrt(b_ * b_ - 4 * a_ * c_)
    ws = [(-b_ + d) / (2 * a_), (-b_ - d) / (2 * a_)]
    pts = []
    for w in ws:
        r = A * mp.sqrt(mp.mpc(w))
        pts += [r, -r]
    return pts, [mp.mpc(0, A), mp.mpc(0, -A)]


def _trap(k, centre, rad, N):
    zs = centre + rad
    s0 = mp.sqrt(Bw(zs**2 / A**2, k))
    assert mp.re(s0) > 0 and abs(mp.im(s0)) < mp.mpf(10) ** -40, "base point: B must be positive"
    s = mp.mpc(s0)
    I1 = mp.mpc(0)
    I2 = mp.mpc(0)
    scale = mp.mpf(0)
    pref = -mp.sqrt(mp.mpf(8) / 5) * A**3
    for j in range(N + 1):
        t = 2 * mp.pi * j / N
        z = centre + rad * mp.expj(t)
        q = mp.sqrt(Bw(z**2 / A**2, k))
        if abs(q - s) > abs(q + s):
            q = -q
        if abs(q - s) > mp.mpf("0.5") * abs(s):
            raise RuntimeError(f"branch jump at t = {t}")
        s = q
        if j == N:
            break
        f = pref * s / (z**2 + A**2) ** 3
        dz = 1j * rad * mp.expj(t) * 2 * mp.pi / N
        I1 += f * dz
        I2 += z * f * dz
        scale = max(scale, abs(f))
    sheet = 1 if abs(s - s0) < abs(s + s0) else -1
    return dict(sheet=sheet, I1=I1, I2=I2, zs=zs, scale=scale)


def loop_integrals(k, centre, rad, N=8000):
    """circle |z - centre| = rad, based at centre + rad (real, > 0), counter-clockwise; periodic trapezoid rule
    (exponentially convergent for an integrand analytic on an annulus), at N and 2N points: the change is reported."""
    a, b = _trap(k, centre, rad, N), _trap(k, centre, rad, 2 * N)
    if a["sheet"] != b["sheet"]:
        raise RuntimeError("sheet differs between N and 2N")
    dc1, dc0 = b["I1"], b["zs"] * b["I1"] - b["I2"]
    err = max(abs(dc1 - a["I1"]), abs(dc0 - (a["zs"] * a["I1"] - a["I2"])))
    return dict(sheet=b["sheet"], dc1=abs(dc1), dc0=abs(dc0), scale=b["scale"], err=err)


def verdict(r):
    tol_c, tol_n = mp.mpf(10) ** -30 * max(1, r["scale"]), mp.mpf(10) ** -10 * max(1, r["scale"])
    if r["sheet"] == 1 and r["dc1"] <= tol_c and r["dc0"] <= tol_c:
        return "CLOSES"
    if r["sheet"] == -1 or r["dc1"] > tol_n or r["dc0"] > tol_n:
        return "DOES NOT CLOSE"
    return "UNRESOLVED"


def main():
    t0 = time.time()
    print(f"== closure check == spin {SPIN}, R0 {R0}, Z0 {Z0}; periodic trapezoid at 8000 and 16000 points, dps {mp.mp.dps}", flush=True)
    for k in KS:
        print(f"-- k = {mp.nstr(k, 12)}: formula vs code radicand, rel. diff {mp.nstr(check_formula(k), 3)}", flush=True)
        bps, poles = sing(k)
        rmax = max(abs(p) for p in bps)
        print(f"   branch points {[mp.nstr(p, 6) for p in bps]}; max |bp| {mp.nstr(rmax, 6)} vs R0 {R0}", flush=True)
        r = loop_integrals(k, mp.mpf(0), R0)
        print(f"   circle |z| = R0: sheet {r['sheet']}, |dc0'| {mp.nstr(r['dc1'], 3)}, |dc0| {mp.nstr(r['dc0'], 3)}, "
              f"scale {mp.nstr(r['scale'], 3)}, N vs 2N {mp.nstr(r['err'], 3)} -> {verdict(r)}  (all branch points inside: {rmax < R0})", flush=True)
        Rc = min(abs(Z0 - p) for p in bps + poles)
        rb = mp.mpf("0.7") * Rc
        r = loop_integrals(k, Z0, rb)
        print(f"   region-B test circle |z - Z0| = 0.7 R_c = {mp.nstr(rb, 6)} (R_c {mp.nstr(Rc, 6)}): sheet {r['sheet']}, "
              f"|dc0'| {mp.nstr(r['dc1'], 3)}, |dc0| {mp.nstr(r['dc0'], 3)}, scale {mp.nstr(r['scale'], 3)}, N vs 2N {mp.nstr(r['err'], 3)} -> {verdict(r)}",
              flush=True)
    print(f"== done, {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
