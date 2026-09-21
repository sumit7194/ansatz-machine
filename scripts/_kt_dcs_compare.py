#!/usr/bin/env python3
"""Do the four C-tensor conventions actually differ? Compare them componentwise.

Tracelessness rejected the original coding but passed all four scanned variants (_kt_dcs_variants).
Before hunting for a sharper control, the cheap question is whether the four are the SAME TENSOR --
in which case the ambiguity is cosmetic and there is nothing left to discriminate.

Repro:  .venv/bin/python scripts/_kt_dcs_compare.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from gr_engine import Geometry  # noqa: E402
from _kt_dcs import cov_deriv_ricci_ud, hessian_scalar, levi_civita_up  # noqa: E402
from _kt_dcs_variants import duals  # noqa: E402

t, r, th, ph = sp.symbols("t r theta phi", real=True)

if __name__ == "__main__":
    M, a = sp.Integer(1), sp.Rational(1, 5)
    f = 1 - 2 * M / r
    g = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th) ** 2)
    g[0, 3] = g[3, 0] = -2 * M * a * sp.sin(th) ** 2 / r
    geom = Geometry(g, [t, r, th, ph])
    theta = sp.cos(th) / r**2 * (1 + 2 * M / r + sp.Rational(18, 5) * M**2 / r**2)
    print("building pieces ...", flush=True)
    E = levi_civita_up(geom)
    dR = cov_deriv_ricci_ud(geom)
    H = hessian_scalar(geom, theta)
    Dl, Dr = duals(geom, E)
    dth = [sp.diff(theta, x) for x in (t, r, th, ph)]
    sub = {r: sp.Rational(7, 2), th: sp.acos(sp.Rational(1, 3))}
    print("built; evaluating the four variants at one point\n", flush=True)

    def build(slot, which):
        D = Dr if which == "right" else Dl
        C = sp.zeros(4, 4)
        for mu in range(4):
            for nu in range(mu, 4):
                tot = sp.S.Zero
                for m_, n_ in ((mu, nu), (nu, mu)):
                    for s in range(4):
                        if dth[s] != 0:
                            for al in range(4):
                                for be in range(4):
                                    e = E[s][m_][al][be] if slot == "mid" else E[s][al][be][m_]
                                    if e != 0:
                                        tot += dth[s] * e * dR[al][n_][be]
                    for s in range(4):
                        for ta in range(4):
                            if H[s][ta] != 0:
                                tot += H[s][ta] * D[ta][m_][s][n_]
                v = sp.N(sp.together(tot / 2).subs(sub), 30)
                C[mu, nu] = C[nu, mu] = v
        return C

    variants = {}
    for slot in ("mid", "last"):
        for which in ("right", "left"):
            variants[(slot, which)] = build(slot, which)
            print(f"  built {slot}/{which}", flush=True)

    keys = list(variants)
    print("\n  C^{tt}, C^{tphi}, C^{rr} for each:")
    for k in keys:
        C = variants[k]
        print(f"    {k[0]:4s}/{k[1]:5s}: {sp.N(C[0,0],8)}  {sp.N(C[0,3],8)}  {sp.N(C[1,1],8)}", flush=True)

    print("\n  pairwise max |difference| and max |sum| (sum small => they differ only by sign):")
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            A, B = variants[keys[i]], variants[keys[j]]
            dmax = max(abs(sp.N(A[x, y] - B[x, y], 30)) for x in range(4) for y in range(4))
            smax = max(abs(sp.N(A[x, y] + B[x, y], 30)) for x in range(4) for y in range(4))
            tag = "IDENTICAL" if dmax < 1e-25 else ("OPPOSITE" if smax < 1e-25 else "different")
            print(f"    {keys[i][0]:4s}/{keys[i][1]:5s} vs {keys[j][0]:4s}/{keys[j][1]:5s}: "
                  f"maxdiff {sp.N(dmax,6)}  maxsum {sp.N(smax,6)}   -> {tag}", flush=True)
