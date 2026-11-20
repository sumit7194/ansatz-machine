"""§159 post-unblinding, for the Bridge (V26 addendum D follow-up): basis-free inner-circle trace tr(g_in) - 2 on
|z| = 1.35 (control r = 1.6 must agree), versus k at E = 0.7, 0.8, 0.9, at two steps. k^2 coefficient by a linear fit in k."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import sympy as sp
import mpmath as mp
from fractions import Fraction
from _nve_lower import Problem, find_zeros, Walker, arc, A, z, OUT
from _ts_edge2 import fleet_guard

if __name__ == "__main__":
    g = fleet_guard()
    if g:
        raise SystemExit(f"NOT STARTED: {g}")
    fK = 1 - 1 / (z - sp.I * A) - 1 / (z + sp.I * A)
    R = sp.Rational
    ck = os.path.join(OUT, "lower_trace.jsonl")
    done = {(json.loads(l)["E"], json.loads(l)["k"]) for l in open(ck)} if os.path.exists(ck) else set()
    for E in (R(7, 10), R(4, 5), R(9, 10)):
        for k in (R(1, 1000), R(1, 100), R(1, 30), R(1, 10), R(0)):
            if (str(E), str(k)) in done:
                continue
            pr = Problem(fK, k, E**2)
            z1, _ = find_zeros(pr, 1); z2, _ = find_zeros(pr, 2)
            i1, _ = find_zeros(pr, 1, rmin=0.9, rmax=1.3); i2, _ = find_zeros(pr, 2, rmin=0.9, rmax=1.3)
            rec = dict(E=str(E), k=str(k), rmin_annulus=min(float(abs(c)) for c in z1 + z2), tr={})
            for r_ in ("1.35", "1.6"):
                for st in ("0.35", "0.2"):
                    W = Walker(pr, z1 + z2 + i1 + i2, st)
                    Y = W.walk(arc(mp.mpf(r_), 0, 2 * mp.pi), [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]])
                    rec["tr"][f"r{r_}_s{st}"] = mp.nstr(Y[0][0] + Y[1][1] - 2, 20)
            open(ck, "a").write(json.dumps(rec) + "\n")
            print(E, k, rec["rmin_annulus"], rec["tr"], flush=True)
