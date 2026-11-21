"""Reproduction of T50's degenerate spin a_c (Bridge request; known target 0.858446198791717...). Spin via NVE_SPIN.
    NVE_SPIN=<a> python scripts/_nve_ac.py trY       -> prints tr Y at the endpoint k = 30/7, E = 4/5 (S2 loop rule)
    NVE_SPIN=<a> python scripts/_nve_ac.py circle    -> the circle pair (M0 = |z| = R0, M1 = capsule lasso) with Z1-Z4
Endpoint seeds are interpolated from our spin 0.8 and 0.9 endpoint positions (spin_geo_4_5/9_10.json)."""
import json, os, sys
import mpmath as mp
import sympy as sp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_lower as L, _nve_lower_kc as KC
from _nve_monodromy import comm, mul, inv
mp.mp.dps = 50
a = mp.mpf(sp.N(L.A, 60)); K = mp.mpf(30) / 7; E2 = sp.Rational(16, 25)
pc = lambda s: mp.mpmathify(complex(s.replace(" ", "")))
G8, G9 = (json.load(open(f"data/nve/spin_geo_{t}.json")) for t in ("4_5", "9_10"))
t = (a - mp.mpf("0.8")) / mp.mpf("0.1")
P8 = [pc(x) for x in G8["endpoint_points"]]; P9 = [pc(x) for x in G9["endpoint_points"]]
pr = KC.ProblemC(KC.FK, K, E2)
pos = [KC.newton(pr, P8[i] + t * (P9[i] - P8[i]), w) for i, w in ((0, 1), (1, 2), (2, 2))]
rp, pp, pm = pos
I2 = lambda: [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]]
tr = lambda M: M[0][0] + M[1][1]
S_FIN = [2, -2, 1, -1, 0, mp.sqrt(2), -mp.sqrt(2), (mp.sqrt(5) - 1) / 2, -(mp.sqrt(5) - 1) / 2, (mp.sqrt(5) + 1) / 2, -(mp.sqrt(5) + 1) / 2]


def dens(path, n=60):
    out = [path[0]]
    for A_, B_ in zip(path[:-1], path[1:]):
        out += [A_ + (B_ - A_) * j / n for j in range(1, n + 1)]
    return out


if sys.argv[1] == "trY":
    upr, upi, utp = mp.re(pp) / a, abs(mp.im(pp)) / a, mp.re(rp) / a
    U = lambda x, y: mp.mpc(x, y) * a
    u0 = U(max(upr, utp) + max(mp.mpf("0.25"), 2 * upi), 0); d = mp.mpf("0.49") * upi; h3 = mp.mpf("0.45") * upi
    l1 = [u0, U(upr + d, upi + d), U(upr - d, upi + d), U(upr - d, upi - d), U(upr + d, upi - d), u0]
    l2 = [mp.conj(p) for p in l1]
    l3 = [u0, U(utp + mp.mpf("0.1"), h3), U(utp - mp.mpf("0.1"), h3), U(utp - mp.mpf("0.1"), -h3), U(utp + mp.mpf("0.1"), -h3), u0]
    W = L.Walker(pr, pos, sys.argv[2] if len(sys.argv) > 2 else "0.2")
    M1, M2, M3 = (W.walk(dens(p), I2()) for p in (l1, l2, l3))
    print(mp.nstr(tr(mul(M2, mul(M3, M1))), 30))
else:
    rho = pr.rho
    om = min(abs(x) for x in pos + [KC.newton(pr, mp.mpc(-3.4, 0), 1)])
    R0 = (rho + min(abs(x) for x in pos)) / 2
    M0p = L.arc(R0, 0, 2 * mp.pi)
    rm = KC.newton(pr, mp.mpc(-3.4, 0), 1)
    lasso, delta = KC.capsule_lasso(rp, pp, [rm, pm], b=R0)
    res = {}
    for st in ("0.2", "0.12"):
        W = L.Walker(pr, pos + [rm], st)
        M0, M1 = W.walk(M0p, I2()), W.walk(lasso, I2())
        res[st] = dict(F=tr(comm(M1, M0)) - 2, trM0=tr(M0), trM1=tr(M1), trM0M1=tr(mul(M0, M1)))
    r = res["0.12"]
    rel = max(float(abs(res["0.2"][x] - r[x]) / abs(r[x])) for x in r)
    ok = bool(all(abs(r[x]) >= 1e-8 for x in r) and abs(mp.im(r["trM1"])) >= 1e-8 and min(abs(r["trM1"] - s) for s in S_FIN) >= 1e-3)
    print(json.dumps(dict(spin=str(L.A), rho=float(rho), R0=float(R0), outer_min=float(min(abs(x) for x in pos)),
                          lasso_clr=float(min(KC.path_dist(c, lasso) for c in (rm, pm))),
                          **{x: mp.nstr(v, 14) for x, v in r.items()}, dist_trM1_S=float(min(abs(r["trM1"] - s) for s in S_FIN)),
                          step_rel=rel, Z1to4_nonVA=ok)))
