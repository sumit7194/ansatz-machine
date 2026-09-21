#!/usr/bin/env python3
"""Which index convention makes the dCS C-tensor TRACELESS? Measured, not guessed.

WHY A SCAN AND NOT A CHOICE. Sources write C^{mu nu} with the Levi-Civita free index in different
slots and with the Riemann dual taken on either pair, and the two choices differ by a sign and by a
genuinely different tensor. Guessing one and reporting a mismatch would blame the derivation for a
convention -- the lesson _kt_sgb_verify.py already paid for with c1, c2.

g_ab C^{ab} = 0 is a nontrivial identity of the CORRECT C-tensor, so it discriminates: exactly the
variants that are right can pass, and the scan reports the trace of each at random points.

Alexander & Yunes, Phys. Rept. 480 (2009), Eqs. (6), (16):
    C^{mu nu} = grad_s theta eps^{s mu al be} grad_al R^nu_be  +  grad_s grad_ta theta *R^{ta mu s nu}
    *R^{ta mu s nu} = (1/2) eps^{s nu al be} R^{ta mu}_{al be}         (dual on the LAST pair)

Repro:  .venv/bin/python scripts/_kt_dcs_variants.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from gr_engine import Geometry  # noqa: E402
from _kt_dcs import (EPS4, cov_deriv_ricci_ud, hessian_scalar, levi_civita_up,  # noqa: E402
                     riemann_uudd)

t, r, th, ph = sp.symbols("t r theta phi", real=True)


def duals(geom, E):
    """Both duals of Riemann, all indices up.
       LEFT : Dl[a][b][c][d] = (1/2) eps^{abef} R^{cd}_{ef}   (dual on the FIRST pair)
       RIGHT: Dr[a][b][c][d] = (1/2) eps^{cdef} R^{ab}_{ef}   (dual on the LAST pair)"""
    Ruudd = riemann_uudd(geom)
    Dl = [[[[sp.S.Zero] * 4 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    Dr = [[[[sp.S.Zero] * 4 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    sl = sum(E[a][b][e][f] * Ruudd[c][d][e][f] for e in range(4) for f in range(4))
                    sr = sum(E[c][d][e][f] * Ruudd[a][b][e][f] for e in range(4) for f in range(4))
                    Dl[a][b][c][d] = sl / 2
                    Dr[a][b][c][d] = sr / 2
    return Dl, Dr


if __name__ == "__main__":
    M, a = sp.Integer(1), sp.Rational(1, 5)
    f = 1 - 2 * M / r
    g = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th) ** 2)
    g[0, 3] = g[3, 0] = -2 * M * a * sp.sin(th) ** 2 / r
    geom = Geometry(g, [t, r, th, ph])
    theta = sp.cos(th) / r**2 * (1 + 2 * M / r + sp.Rational(18, 5) * M**2 / r**2)
    print(f"background Schwarzschild + Lense-Thirring, M={M}, a={a}; dipole theta\n", flush=True)

    print("  building pieces ...", flush=True)
    E = levi_civita_up(geom)
    dR = cov_deriv_ricci_ud(geom)                  # dR[deriv][up][down] = grad_e R^b_d
    H = hessian_scalar(geom, theta)                # H[c][d] = grad_c grad_d theta
    Dl, Dr = duals(geom, E)
    dth = [sp.diff(theta, x) for x in (t, r, th, ph)]
    gi, gg = geom.ginv, geom.g
    print("  built; assembling variants\n", flush=True)

    def term1(mu, nu, slot):
        """slot='mid': eps^{s mu al be} (free index 2nd, Alexander-Yunes).
           slot='last': eps^{s al be mu} (free index last, the form first coded here)."""
        tot = sp.S.Zero
        for s in range(4):
            if dth[s] == 0:
                continue
            for al in range(4):
                for be in range(4):
                    e = E[s][mu][al][be] if slot == "mid" else E[s][al][be][mu]
                    if e == 0:
                        continue
                    tot += dth[s] * e * dR[al][nu][be]
        return tot

    def term2(mu, nu, which):
        """AY: grad_s grad_ta theta * R^{ta mu s nu}, dual on the last pair."""
        D = Dr if which == "right" else Dl
        tot = sp.S.Zero
        for s in range(4):
            for ta in range(4):
                if H[s][ta] == 0:
                    continue
                tot += H[s][ta] * D[ta][mu][s][nu]
        return tot

    pts = [(sp.Rational(7, 2), sp.Rational(1, 3)), (sp.Rational(5), sp.Rational(-2, 5)),
           (sp.Rational(11, 4), sp.Rational(3, 4))]
    best = []
    for slot in ("mid", "last"):
        for which in ("right", "left"):
            tr = sp.S.Zero
            nz = sp.S.Zero
            for mu in range(4):
                for nu in range(4):
                    C = (term1(mu, nu, slot) + term1(nu, mu, slot)
                         + term2(mu, nu, which) + term2(nu, mu, which)) / 2
                    tr += gg[mu, nu] * C if False else 0
                    # C has BOTH indices up, so the trace contracts with g_{mu nu}
                    tr += gg[mu, nu] * C
                    nz += C**2
            vals = [sp.N(tr.subs({r: rv, th: sp.acos(cv)}), 40) for rv, cv in pts]
            zero = all(abs(v) < sp.Float("1e-30") for v in vals)
            nzv = sp.N(nz.subs({r: pts[0][0], th: sp.acos(pts[0][1])}), 20)
            print(f"  eps free-slot={slot:4s}  dual={which:5s}  traceless: {str(zero):5s}   "
                  f"|C|^2 != 0: {nzv != 0}", flush=True)
            for (rv, cv), v in zip(pts, vals):
                print(f"        r={rv}, c={cv}: trace = {sp.N(v, 8)}", flush=True)
            if zero and nzv != 0:
                best.append((slot, which))
    print()
    if len(best) == 1:
        print(f"  SELECTED: eps free-slot={best[0][0]}, dual={best[0][1]} "
              f"-- the unique nonzero traceless variant.")
    elif best:
        print(f"  AMBIGUOUS: {best} all pass -- tracelessness does not discriminate; need another control.")
    else:
        print("  NONE traceless -- the error is not the convention. Check dR, the Hessian, or eps itself.")
