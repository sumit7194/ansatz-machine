#!/usr/bin/env python3
"""EXP-002 Tier 3 (independent route): integrate geodesics numerically and watch F.
Shares no code path with the symbolic bracket: Hamilton's equations from H are integrated with an
RK4 stepper in numpy; F, H, Q1, Q2 are evaluated along the orbit. A KNOWN-FAIL control (p_xi^3,
not conserved) must drift, or the check is decoration."""
import random, sympy as sp, numpy as np
from sympy import Rational as Q_
exec(open("scripts/exp002_ppwave.py").read().split("# ----------------------------------------------------------------------------- CHECK 1")[0])
Hb = H - pt*ps
Q1 = sp.expand(pxi**2/16 + 2*a*xi*ps**2 - xi**2*Hb)
Q2 = sp.expand((pxi-peta)**2/32 + a*(xi-eta)*ps**2 - Q_(1,2)*(xi-eta)**2*Hb)
F = sp.expand(-4*poisson(Q1, Q2))
Gfail = pxi**3 + pt*ps*peta          # known-fail: a cubic that is NOT conserved
a1 = {a: 1}
vars_ = [xi, eta, pxi, peta, pt, ps]
rhs = sp.lambdify(vars_, [sp.diff(H, pxi), sp.diff(H, peta), -sp.diff(H, xi), -sp.diff(H, eta)]
                  , "numpy")
funcs = {n: sp.lambdify(vars_, f.subs(a1), "numpy") for n, f in
         (("H", H), ("Q1", Q1), ("Q2", Q2), ("F", F), ("KNOWN-FAIL p_xi^3+p_t p_s p_eta", Gfail))}
rhs1 = sp.lambdify(vars_, [e.subs(a1) for e in [sp.diff(H, pxi), sp.diff(H, peta), -sp.diff(H, xi), -sp.diff(H, eta)]], "numpy")

def rk4(y, ptv, psv, h, n):
    out = [y.copy()]
    for _ in range(n):
        k1 = np.array(rhs1(*y, ptv, psv)); k2 = np.array(rhs1(*(y+h/2*k1), ptv, psv))
        k3 = np.array(rhs1(*(y+h/2*k2), ptv, psv)); k4 = np.array(rhs1(*(y+h*k3), ptv, psv))
        y = y + h/6*(k1+2*k2+2*k3+k4); out.append(y.copy())
    return np.array(out)

rng = np.random.default_rng(1)
print(f"{'orbit':>5} {'quantity':>32} {'|F0|':>10} {'max rel drift':>14}")
for orb in range(5):
    y0 = np.array([rng.uniform(0.7, 2.0), rng.uniform(-1.5, 1.5), rng.uniform(-1, 1), rng.uniform(-1, 1)])
    ptv, psv = rng.uniform(-1, 1), rng.uniform(0.5, 1.5)
    traj = rk4(y0, ptv, psv, 1e-3, 20000)
    if np.min(traj[:, 0]**2 + traj[:, 1]**2) < 0.05:
        print(f"{orb:>5}  orbit approached rho=0, skipped"); continue
    for n, f in funcs.items():
        vals = f(traj[:, 0], traj[:, 1], traj[:, 2], traj[:, 3], ptv, psv)
        drift = np.max(np.abs(vals - vals[0])) / max(abs(vals[0]), 1e-12)
        print(f"{orb:>5} {n:>32} {abs(vals[0]):10.3e} {drift:14.2e}")
