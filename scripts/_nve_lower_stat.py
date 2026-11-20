"""§159 post-hoc / POST-UNBLINDING: S (ours) and S_B (the Bridge's statistic) from the same 50-digit monodromy.
S_B = max over pairs of K = [M_i, M_j] of ||K K' - K' K||_F / (||K||_F ||K'||_F), K = M_i M_j M_i^-1 M_j^-1.
Reported for all generators and for the point loops only (no inner loop). E = 4/5; k -> 0 scan plus the §159 k."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import sympy as sp
import mpmath as mp
from _nve_lower import Problem, find_zeros, Walker, loops, statistic, A, z, OUT
from _nve_monodromy import comm, mul, nrm
from _ts_edge2 import fleet_guard

I2 = lambda: [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]]


def sub(X, Y):
    return [[X[i][j] - Y[i][j] for j in range(2)] for i in range(2)]


def s_bridge(gens):
    Ks = [comm(gens[i], gens[j]) for i in range(len(gens)) for j in range(i + 1, len(gens))]
    best, best_un, arg = mp.mpf(0), mp.mpf(0), None
    for a in range(len(Ks)):
        for b in range(a + 1, len(Ks)):
            d = nrm(sub(mul(Ks[a], Ks[b]), mul(Ks[b], Ks[a])))
            v = d / (nrm(Ks[a]) * nrm(Ks[b]))
            if v > best:
                best, arg = v, (a, b)
            best_un = max(best_un, d)
    return float(best), float(best_un), arg, [float(nrm(K)) for K in Ks]


def gens_at(pr, sing, extra, step):
    W = Walker(pr, list(sing) + list(extra), step)
    return [W.walk(p, I2()) for _, _, _, p in loops(sing)]


if __name__ == "__main__":
    g = fleet_guard()
    if g:
        raise SystemExit(f"NOT STARTED: {g}")
    mp.mp.dps = max(mp.mp.dps, 50)
    fK = 1 - 1 / (z - sp.I * A) - 1 / (z + sp.I * A)
    E = sp.Rational(4, 5)
    ck = os.path.join(OUT, "lower_stat.jsonl")
    done = {json.loads(l)["k"] for l in open(ck)} if os.path.exists(ck) else set()
    R = sp.Rational
    for k in (R(1, 10), R(1, 30), R(1, 100), R(3, 1000), R(1, 1000), R(1, 10000), R(0)):
        if str(k) in done:
            continue
        pr = Problem(fK, k, E**2)
        z1, n1 = find_zeros(pr, 1); z2, n2 = find_zeros(pr, 2)
        i1, _ = find_zeros(pr, 1, rmin=0.9, rmax=1.3); i2, _ = find_zeros(pr, 2, rmin=0.9, rmax=1.3)
        rec = dict(k=str(k), E=str(E), count_ok=(len(z1) == n1 and len(z2) == n2), npts=len(z1) + len(z2), steps={})
        for st in ("0.35", "0.2"):
            G = gens_at(pr, z1 + z2, i1 + i2, st)
            S, red, fin = statistic(G)
            sb_all = s_bridge(G)
            sb_pts = s_bridge(G[:-1])
            rec["steps"][st] = dict(S_ours=float(S), red=red, finite=fin,
                                    SB_all=sb_all[0], SB_all_unnorm=sb_all[1], SB_all_arg=sb_all[2],
                                    SB_pts=sb_pts[0], SB_pts_unnorm=sb_pts[1], K_norms_pts=sb_pts[3],
                                    gen_norms=[float(nrm(M)) for M in G])
            if st == "0.2":
                rec["gens_0.2"] = [[[mp.nstr(M[i][j], 30) for j in range(2)] for i in range(2)] for M in G]
        open(ck, "a").write(json.dumps(rec, default=str) + "\n")
        s = rec["steps"]
        print(f"k={k}: S_ours {s['0.35']['S_ours']:.4e}/{s['0.2']['S_ours']:.4e}  "
              f"SB_pts {s['0.35']['SB_pts']:.4e}/{s['0.2']['SB_pts']:.4e} (unnorm {s['0.2']['SB_pts_unnorm']:.4e})  "
              f"SB_all {s['0.2']['SB_all']:.4e} (unnorm {s['0.2']['SB_all_unnorm']:.4e})  "
              f"gen norms {[round(x, 3) for x in s['0.2']['gen_norms']]}", flush=True)
