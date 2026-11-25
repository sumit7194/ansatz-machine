"""Office check (2026-11-26) of Fable's eps certifier (branch fable/2026-11-25-eps, 75957fd), item 3:
are the per-box bounds alpha >= |Delta q| and beta >= |Delta q - k dq| (and e0, e1 for the twist remainder) valid?
Truth is computed INDEPENDENTLY: c0(z; k), c0'(z; k) by direct mpmath quadrature of c_K''(s) sqrt(1 - k phi(w)) along
the radial ray (not the majorants), c1 by quadrature (not the closed form), q from its definition, dq as a numerical
directional derivative. The bounds come from the certifier's own box_bounds()/majorants() on its own boxes.
For each sampled box and 8 values of k on |k| = r_ref the ratios truth/bound must be <= 1.
    NVE_SPIN=3/5 EPSDIR=<checkout>/scripts nice -n 12 .venv/bin/python scripts/_nve_eps_office_tailcheck.py 0.003,0.3
Declared peak < 300 MB. No caps; one core."""
import os
import sys

import mpmath as mp

sys.path.insert(0, os.environ["EPSDIR"])
import _nve_eps_certify as EC          # noqa: E402  (the certifier under test; spin from NVE_SPIN)

mp.mp.dps = 30
a = mp.mpf(EC.af)
E2 = mp.mpf(16) / 25
RREFS = [float(x) for x in sys.argv[1].split(",")]


def cKpp(s):
    return -4 * a * (3 * s * s - a * a) / (s * s + a * a) ** 3


def phi(s):
    w = (s / a) ** 2
    return (21 * w * w - 18 * w + 1) / (10 * (3 * w - 1) ** 2)


def c0_pair(z, k):
    """c0, c0' at z by quadrature along the radial ray s = z t, t >= 1 (k = 0 gives Kerr)."""
    f = lambda t: cKpp(z * t) * mp.sqrt(1 - k * phi(z * t))           # noqa: E731
    c0 = z * z * mp.quad(lambda t: (t - 1) * f(t), [1, 2, 10, mp.inf])
    c0p = -z * mp.quad(f, [1, 2, 10, mp.inf])
    return c0, c0p


def c1_pair(z):
    f = lambda t: cKpp(z * t) * (-phi(z * t) / 2)                     # noqa: E731
    return z * z * mp.quad(lambda t: (t - 1) * f(t), [1, 2, 10, mp.inf]), -z * mp.quad(f, [1, 2, 10, mp.inf])


def q_of(z, c, cp):
    Dp = z * z + a * a
    f0, f0p = (z * z - 2 * z + a * a) / Dp, 2 * (z * z - a * a) / Dp ** 2
    G2, G2p = f0 * f0 + c * c, 2 * (f0 * f0p + c * cp)
    G1, G1p = E2 * G2 - f0, E2 * G2p - f0p
    return mp.mpf(3) / 16 * (G1p / G1 - G2p / G2) ** 2


def midpoint(bx):
    zb = bx["z"]
    return mp.mpc(float(zb.re.mid), float(zb.im.mid))


cb = EC.circle_boxes()
lbx, delta, _dU, _w, _nv = EC.lasso_boxes()
# sample: 12 circle boxes, and 24 lasso boxes including the 8 closest to r+ and p+
rp, pp = complex(EC.fl(EC.r_plus.mid)), complex(2, EC.af)
lsort = sorted(range(len(lbx)), key=lambda i: min(abs(complex(midpoint(lbx[i])) - rp), abs(complex(midpoint(lbx[i])) - pp)))
pick_L = sorted(set(lsort[:8] + list(range(0, len(lbx), max(1, len(lbx) // 16)))))
pick_C = list(range(0, len(cb), max(1, len(cb) // 12)))
print(f"spin {EC.A}: R0 = {EC.R0S}; {len(pick_C)} circle boxes, {len(pick_L)} lasso boxes (capsule radius {delta:.4f}); "
      f"8 values of k on each |k| = r_ref", flush=True)
worst = {}
for rref in RREFS:
    wa = wb = we0 = we1 = 0.0
    for kind, boxes, picks in (("C", cb, pick_C), ("L", lbx, pick_L)):
        for i in picks:
            bx = boxes[i]
            _dqub, alpha, beta, _dq = EC.box_bounds(bx["z"], rref)
            A0, A1, PH = EC.majorants(bx["z"])
            fac = PH * rref * rref / (8 * (1 - rref * PH))
            e0b, e1b = A0 * fac, A1 * fac
            z = midpoint(bx)
            cK, cKp = c0_pair(z, 0)
            c1, c1p = c1_pair(z)
            qK = q_of(z, cK, cKp)
            dq = mp.diff(lambda t: q_of(z, cK + t * c1, cKp + t * c1p), 0)
            for j in range(8):
                k = mp.mpf(rref) * mp.expj(2 * mp.pi * (j + 0.5) / 8)
                c, cp = c0_pair(z, k)
                Dq = q_of(z, c, cp) - qK
                wa = max(wa, float(abs(Dq) / alpha))
                wb = max(wb, float(abs(Dq - k * dq) / beta))
                we0 = max(we0, float(abs(c - cK - k * c1) / e0b))
                we1 = max(we1, float(abs(cp - cKp - k * c1p) / e1b))
    worst[rref] = (wa, wb, we0, we1)
    print(f"  r_ref = {rref:g}: max truth/bound  |Dq|/alpha = {wa:.3e}   |Dq - k dq|/beta = {wb:.3e}   "
          f"|eps2|/e0 = {we0:.3e}   |eps2'|/e1 = {we1:.3e}   -> {'PASS' if max(wa, wb, we0, we1) <= 1 else 'FAIL'}",
          flush=True)
# must-fail: a bound shrunk 1000x must be violated somewhere (shows the comparison can fail)
mf = {r: max(v) * 1000 for r, v in worst.items()}
print(f"  must-fail (bounds / 1000): max ratio {max(mf.values()):.3e} -> {'FIRES' if max(mf.values()) > 1 else 'DOES NOT FIRE'}")
