"""Endpoint (k = 30/7, E = 4/5) obstruction size vs spin, on the S2 loop rule (single-point loops M1 ~ p+, M2 ~ p-,
M3 ~ r+, based on the real axis; A = M2M1, B = M3M2; X = M3M1 (lasso-like), Y = M2M3M1 (Gamma-like)).
Reports tau(A,B) (= tau of any pair of the three single-point loops: ABC=I relation, one number), tau(M1,M3),
tr X, tr Y, tr XY, at two walker steps and two precisions. Run once per spin via NVE_SPIN. Output appended to
data/nve/endpoint_scaling.out"""
import json, os, sys
import mpmath as mp
import sympy as sp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_lower as L, _nve_lower_kc as KC
from _nve_monodromy import mul, inv
TAG = str(L.A).replace("/", "_")
GEO = {"3_5": None}


def run(dps, step):
    mp.mp.dps = dps
    a = mp.mpf(sp.N(L.A, dps + 10)); k = mp.mpf(30) / 7
    pr = KC.ProblemC(KC.FK, k, sp.Rational(16, 25))
    g = json.load(open(f"data/nve/t48b_spin/geo_{TAG}.json"))
    upr, upi, utp = mp.mpf(g["end_up_re"]), mp.mpf(g["end_up_im"]), mp.mpf(g["end_utp"])
    seeds = [(utp * a, 1), (mp.mpc(upr, upi) * a, 2), (mp.mpc(upr, -upi) * a, 2)]
    pos = [KC.newton(pr, x, w) for x, w in seeds]
    U = lambda x, y: mp.mpc(x, y) * a
    u0 = U(max(upr, utp) + max(mp.mpf("0.25"), 2 * upi), 0); d = mp.mpf("0.49") * upi; h3 = mp.mpf("0.45") * upi
    l1 = [u0, U(upr + d, upi + d), U(upr - d, upi + d), U(upr - d, upi - d), U(upr + d, upi - d), u0]
    l2 = [mp.conj(p) for p in l1]
    l3 = [u0, U(utp + mp.mpf("0.1"), h3), U(utp - mp.mpf("0.1"), h3), U(utp - mp.mpf("0.1"), -h3), U(utp + mp.mpf("0.1"), -h3), u0]
    def dens(path, n=60):
        out = [path[0]]
        for A_, B_ in zip(path[:-1], path[1:]):
            out += [A_ + (B_ - A_) * j / n for j in range(1, n + 1)]
        return out
    I2 = lambda: [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]]
    tr = lambda M: M[0][0] + M[1][1]
    tau = lambda X, Y: tr(mul(mul(X, Y), mul(inv(X), inv(Y)))) - 2
    W = L.Walker(pr, pos, step)
    M1, M2, M3 = (W.walk(dens(p), I2()) for p in (l1, l2, l3))
    A_, B_ = mul(M2, M1), mul(M3, M2)
    X, Y = mul(M3, M1), mul(M2, mul(M3, M1))
    return dict(tauAB=tau(A_, B_), tau13=tau(M1, M3), trX=tr(X), trY=tr(Y), trXY=tr(mul(X, Y)), trA=tr(A_), trB=tr(B_))


res = {(d, s): run(d, s) for d, s in ((50, "0.35"), (50, "0.2"), (70, "0.2"))}
mp.mp.dps = 70
ref = res[(70, "0.2")]
with open("data/nve/endpoint_scaling.out", "a") as fh:
    for key in ref:
        spread = max(abs(res[k_][key] - ref[key]) for k_ in res)
        line = f"spin {L.A}: {key} = {mp.nstr(ref[key], 15)}   max |diff| over (dps,step) runs = {mp.nstr(spread, 3)}"
        print(line, flush=True); fh.write(line + "\n")
