"""POST-HOC (labelled): at spin 4/5, E = 4/5 the half-plane pair <M1, Gamma> has a COMMON zero of tr Gamma and tr M1Gamma
at k* ~ 4.0081645 (real), i.e. that pair is imprimitive there. Imprimitivity of a PAIR is not imprimitivity of the GROUP.
Evaluate at k* (and two neighbours) the independent circle-picture pair (M0 = circle R0, M1 lasso; Laurent c0, region-A
machinery) and the 3-generator group {M0, M1_lasso, Gamma} traces. Output: data/nve/spin_kstar_4_5.out"""
import json, os, sys
import mpmath as mp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_spin_scan as SS, _nve_lower_kc as KC, _nve_lower as L
from _nve_monodromy import comm, mul, inv
mp.mp.dps = 50
KSTAR = mp.mpf("4.008164511150082")
G = json.load(open(os.path.join(L.OUT, f"spin_geo_{SS.TAG}.json")))
RA = SS.LauA(G["A"]["R0"])
seeds = SS.kerr_points()
st = list(seeds)
for kk in [mp.mpf(j) / 8 for j in range(1, 33)]:
    pr, st, ex = RA.state(kk, st)
tr = lambda M: M[0][0] + M[1][1]
S = SS.S_FIN
res = {}
for kk in (KSTAR - mp.mpf("0.002"), KSTAR, KSTAR + mp.mpf("0.002")):
    pr, st2, ex = RA.state(kk, st)
    lasso, gg = RA.loops(pr, st2, ex)
    W = L.Walker(pr, [x for x, _ in st2], "0.2")
    M0, M1 = W.walk(RA.M0, KC.I2()), W.walk(lasso, KC.I2())
    F = tr(comm(M1, M0)) - 2
    d = dict(geo_ok=gg["ok"], rho=float(pr.rho), F=mp.nstr(F, 14), trM0=mp.nstr(tr(M0), 14), trM1=mp.nstr(tr(M1), 14),
             trM0M1=mp.nstr(tr(mul(M0, M1)), 14), dist_trM1_S=float(min(abs(tr(M1) - s) for s in S)))
    d["circle_nonVA"] = bool(abs(F) > 1e-8 and abs(tr(M0)) > 1e-8 and abs(tr(M1)) > 1e-8 and abs(mp.im(tr(M1))) > 1e-8 and d["dist_trM1_S"] > 1e-3)
    res[mp.nstr(kk, 16)] = d
    print(mp.nstr(kk, 16), d, flush=True)
json.dump(res, open(os.path.join(L.OUT, "spin_kstar_4_5.json"), "w"), indent=1, default=str)
