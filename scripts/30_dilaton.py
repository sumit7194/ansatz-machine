#!/usr/bin/env python3
"""Step 30 — DILATON (Einstein–Maxwell–dilaton): the secondary-hair prize.

Third field-menu rung and the payoff. Action (a=1, GHS):
    S = ∫√-g [ R − 2(∂φ)² − e^{−2φ} F² ]
giving, in trace-reversed form,
    R_ab = 2 ∂_aφ ∂_bφ + 2 e^{−2φ}(F_ac F_b{}^c − ¼ g_ab F²)
    □φ   = −½ e^{−2φ} F²                     (dilaton EOM)
    ∇_a(e^{−2φ} F^{ab}) = 0                   (dilaton-modified Maxwell)

The GHS dilaton black hole is RATIONAL (no JNW branch-cut wall):
    g_tt=−(1−2M/r), g_rr=1/(1−2M/r), angular = r(r−2D),
    φ = ½ ln(1−2D/r), A_t = Q/r,  with the dilaton charge D = Q²/(2M).

The whole point: D is **secondary** — fixed by M and Q. Feed M,Q,D all
symbolic; the equations must force D=Q²/(2M), and the matter meter (29) must
read M,Q as primary hair and D as SECONDARY. That is the project's first
genuinely non-trivial hair reading.

Run:  .venv/bin/python scripts/30_dilaton.py
"""

import importlib.util
import os
import random
import sys

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from gr_engine import Geometry, R_SYM


def _load(name, fn):
    s = importlib.util.spec_from_file_location(name, os.path.join(_here, fn))
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


sc = _load("sc", "27_scalar.py")
mx = _load("mx", "28_maxwell.py")
mm = _load("mm", "29_matter_meter.py")


def ghs(M, Q, D):
    t, r, th, chi = sp.Symbol("t", real=True), R_SYM, sp.Symbol("theta", real=True), sp.Symbol("chi", real=True)
    coords = [t, r, th, chi]
    f = 1 - 2 * M / r
    ang = r**2 - 2 * D * r          # r(r−2D)
    g = sp.diag(-f, 1 / f, ang, ang * sp.sin(th)**2)
    phi = sp.Rational(1, 2) * sp.log(1 - 2 * D / r)
    A = [Q / r, 0, 0, 0]
    return g, coords, phi, A


def emd_residuals(M, Q, D):
    g, coords, phi, A = ghs(M, Q, D)
    geo = Geometry(g, coords)
    n = geo.n
    F = mx.faraday(A, coords)
    W = 1 / (1 - 2 * D / R_SYM)                 # e^{−2φ} in explicit rational form
    # F² = F_cd F^cd
    ginv = geo.ginv
    Fsq = sum(F[c, d] * sum(ginv[c, a] * ginv[d, e] * F[a, e]
                            for a in range(n) for e in range(n))
              for c in range(n) for d in range(n))
    emT = mx.em_stress(geo, F)                 # F_ac F_b^c − ¼ g F²
    res = sp.zeros(n, n)
    for a in range(n):
        for b in range(a, n):
            r_ab = geo.ricci[a, b] - 2 * sp.diff(phi, coords[a]) * sp.diff(phi, coords[b]) \
                   - 2 * W * emT[a, b]
            res[a, b] = res[b, a] = sp.cancel(sp.together(r_ab))
    dil = sp.cancel(sp.together(sc.box(geo, phi) + sp.Rational(1, 2) * W * Fsq))
    # weighted Maxwell: ∇_a(W F^{ab}) = (1/√|g|)∂_a(√|g| W F^{ab})
    sq = sp.sqrt(sp.Abs(g.det()))
    Fuu = [[sum(ginv[a, c] * ginv[b, d] * F[c, d] for c in range(n) for d in range(n))
            for b in range(n)] for a in range(n)]
    maxw = [sp.cancel(sp.together(sum(sp.diff(sq * W * Fuu[a][b], coords[a])
                                      for a in range(n)) / sq)) for b in range(n)]
    comps = [res[i, j] for i in range(n) for j in range(i, n)] + [dil] + maxw
    return coords, comps


def main():
    M, Q, D = sp.symbols("M Q D", positive=True)
    print("DILATON (EMD / GHS) — the secondary-hair prize\n")

    # 1) transcription gate: numeric check at the known relation D = Q²/2M
    print("  [gate] numeric residual check at D = Q²/(2M) ...", flush=True)
    coords, comps = emd_residuals(M, Q, D)
    rng = random.Random(3)
    worst = 0.0
    for _ in range(4):
        Mv = sp.Rational(rng.randint(5, 9))
        Qv = sp.Rational(rng.randint(1, 3))
        sub = {M: Mv, Q: Qv, D: Qv**2 / (2 * Mv),
               coords[0]: sp.Rational(2), R_SYM: sp.Rational(7),
               coords[2]: sp.Rational(1), coords[3]: sp.Rational(1)}
        for c in comps:
            try:
                worst = max(worst, abs(complex(c.subs(sub).evalf(30))))
            except (TypeError, ValueError):
                worst = float("inf")
    print(f"  [gate] worst |residual| at D=Q²/2M: {worst:.2e}  "
          f"{'✓ transcription OK' if worst < 1e-9 else '✗ check conventions'}")
    if not (worst < 1e-9):
        print("  (stopping before the meter — fix transcription first)")
        return 1

    # 2) the prize: feed M,Q,D symbolic, count hair
    print("\n  [meter] M,Q,D all symbolic — counting hair ...", flush=True)
    nfree, cls = mm.count_free_matter(coords, comps, [M, Q, D])
    print(f"  hair count = {nfree}")
    for c, k in cls.items():
        print(f"    {c}: {k}")
    secondary = any("secondary" in v for v in cls.values())
    print(f"\n  → {'✅ SECONDARY HAIR CAUGHT' if secondary else '❌ no secondary found'}")
    return 0 if secondary else 1


if __name__ == "__main__":
    raise SystemExit(main())
