"""§159 post-unblinding, for the Bridge (V26, check of Neon's group-theory step; Neon's file NOT opened here).
Based at b = 1.35: M0 = circle |z| = 1.35 (ccw); M1 = ccw rectangle enclosing exactly {upper pole ~2+0.6i, zero ~1.93}.
Reports tr M1, tr[M1, M0] - 2, at two steps; a homotopy control (second rectangle, same class: must agree) and a
must-fail (rectangle also enclosing the lower pole: must differ)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import sympy as sp
import mpmath as mp
from _nve_lower import Problem, find_zeros, Walker, arc, A, z, OUT
from _nve_monodromy import comm
from _ts_edge2 import fleet_guard


def rect(x0, x1, y0, y1, b=mp.mpf("1.35")):
    c = [mp.mpc(x0, 0), mp.mpc(x0, y0), mp.mpc(x1, y0), mp.mpc(x1, y1), mp.mpc(x0, y1), mp.mpc(x0, 0)]
    return [mp.mpc(b, 0)] + c + [mp.mpc(b, 0)]


def wind(path, c):
    return int(mp.nint(mp.fsum(mp.im(mp.log((B - c) / (A_ - c))) for A_, B in zip(path[:-1], path[1:])) / (2 * mp.pi)))


I2 = lambda: [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]]

if __name__ == "__main__":
    g = fleet_guard()
    if g:
        raise SystemExit(f"NOT STARTED: {g}")
    fK = 1 - 1 / (z - sp.I * A) - 1 / (z + sp.I * A)
    E = sp.Rational(4, 5)
    R = sp.Rational
    shapes = dict(M1=rect(1.6, 2.4, -0.3, 0.9), M1_alt=rect(1.55, 2.6, -0.25, 1.1), MF_3pts=rect(1.6, 2.4, -0.9, 0.9))
    ck = os.path.join(OUT, "lower_comm.jsonl")
    for k in (R(1, 100), R(1, 30), R(1, 10), R(0)):
        pr = Problem(fK, k, E**2)
        z1, _ = find_zeros(pr, 1); z2, _ = find_zeros(pr, 2)
        i1, _ = find_zeros(pr, 1, rmin=0.9, rmax=1.3); i2, _ = find_zeros(pr, 2, rmin=0.9, rmax=1.3)
        sing = z1 + z2
        rec = dict(k=str(k), E=str(E), enclosed={}, out={})
        for nm, p in shapes.items():
            rec["enclosed"][nm] = [mp.nstr(c, 8) for c in sing if wind(p, c) != 0]
        for st in ("0.35", "0.2"):
            W = Walker(pr, sing + i1 + i2, st)
            M0 = W.walk(arc(mp.mpf("1.35"), 0, 2 * mp.pi), I2())
            o = dict(trM0m2=mp.nstr(M0[0][0] + M0[1][1] - 2, 15))
            for nm, p in shapes.items():
                M1 = W.walk(p, I2())
                C = comm(M1, M0)
                o[nm] = dict(tr=mp.nstr(M1[0][0] + M1[1][1], 15), trC_m2=mp.nstr(C[0][0] + C[1][1] - 2, 15))
            rec["out"][st] = o
        open(ck, "a").write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)
