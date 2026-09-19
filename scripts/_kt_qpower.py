#!/usr/bin/env python3
"""Does the Killing-tensor ladder measure the POLE ORDER of a surviving Carter?  (§141)

§140: for two shape deformations of Kerr, Carter survives only as a rational integral Q + eps*G with
G = K1/(2Q) -- one power of Q in the denominator -- and Carter^2 comes back as a polynomial. The same
algebra says: if G carries Q^m in its denominator, the first polynomial power is Q^(m+1). So at rank 6:

  P1  for d1, d2 (pole order 1): survivors = floor 16 + Q^2 x (p_t^2, p_t p_phi, p_phi^2, H) 4 + Q^3 1 = 21,
      and no Q x (degree 4) direction.
  P2  the space where the pure Q^3 chain survives contains rank 4's pure-Q^2 space (restricted here).
  P3  (open) it may be LARGER: extra directions would be pole order 2 -- survivors 16 + Q^3 only = 17.

Restricted to the shape sector (l2tt, l2rr, l2ang), where §140's directions live, plus two controls.
Survivors are broken down by their leading power of Q (read off the Schwarzschild part in the basis of
reducible products of p_t, p_phi, H0 and L^2).
Usage: _kt_qpower.py [--rank 6 --denpow 8 --margin 6 --slots l2tt,l2rr,l2ang --kmax 6]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

from _kt_carter_space import (arg, build_space, intersect_np, kernel_np, rank_np,  # noqa: E402
                              representable_only, rref_np, setup)
from _kt_rank4_rule import chain_to_products, pair_tower  # noqa: E402


def chain_to_products_fast(ctx, chains, p):
    """chain_to_products, evaluated mod p at random INTEGER points: each coefficient is turned into a
    polynomial once and evaluated by Horner, instead of SymPy-substituting a rational point into a
    rank-6 expression 1,400 times. Linear relations between functions hold identically, hence mod p
    at any point; 16 spare points over-determine the solve, and the kernel check catches a failure."""
    import random
    import _kt_exact as EX
    import _kt_search as K
    x, y = sp.symbols("x y", real=True)
    gnames, prods, pnames = EX.generators(ctx["GI"][0], ctx["rank"], ctx["den"])
    mons = ctx["mons"]
    rng = random.Random(40)
    npts = len(prods) + 16
    pts = [{"x": rng.randrange(3, p - 3), "y": rng.randrange(3, p - 3),
            **{str(m): rng.randrange(1, p) for m in K.MOM}} for _ in range(npts)]

    def ev(expr, pt):
        e = sp.sympify(expr)
        num, den = sp.fraction(sp.together(e.subs({s_: pt[s_.name] for s_ in e.free_symbols})))
        return int(num) % p * pow(int(den) % p, p - 2, p) % p

    Pm = np.array([[ev(pr, pt) for pt in pts] for pr in prods], dtype=np.int64)
    polys = []
    for ch in chains:
        row = []
        for mi, e in enumerate(mons):
            num, den = sp.fraction(sp.cancel(ch[0][mi]))
            row.append((sp.Poly(num, x, y), sp.Poly(den, x, y)))
        polys.append(row)

    def mono_val(e, pt):
        v = 1
        for m, k in zip(K.MOM, e):
            v = v * pow(pt[str(m)], k, p) % p
        return v

    C = np.zeros((len(chains), npts), dtype=np.int64)
    for k, row in enumerate(polys):
        for j, pt in enumerate(pts):
            acc = 0
            for (Pn, Pd), e in zip(row, mons):
                if Pn.is_zero:
                    continue
                nv = int(Pn.eval({x: pt["x"], y: pt["y"]})) % p
                dv = int(Pd.eval({x: pt["x"], y: pt["y"]})) % p
                acc = (acc + nv * pow(dv, p - 2, p) % p * mono_val(e, pt)) % p
            C[k, j] = acc
    Kp = Pm.shape[0]
    T = np.zeros((len(chains), Kp), dtype=np.int64)
    for k in range(len(chains)):
        M = np.concatenate([Pm.T, (-C[k][:, None]) % p], axis=1)
        sol = [v for v in kernel_np(M, Kp + 1, p) if v[-1] % p]
        if not sol:
            sys.exit(f"chain {k}: Schwarzschild part is not a combination of the reducible products")
        T[k] = (sol[0][:Kp] * pow(int(sol[0][-1]), p - 2, p)) % p
    return T, [str(n) for n in pnames]


def lsq_power(name):
    for tok in name.split():
        if tok.startswith("Lsq"):
            return int(tok.split("^")[1]) if "^" in tok else 1
    return 0


def solve_gamma(T, target, p):
    """gamma (over chains) with gamma T = target (product coordinates)."""
    Kc, Kp = T.shape
    M = np.concatenate([T.T, (-np.asarray(target, dtype=np.int64)[:, None]) % p], axis=1)
    g = [v for v in kernel_np(M, Kc + 1, p) if v[-1] % p]
    return (g[0][:Kc] * pow(int(g[0][-1]), p - 2, p)) % p


if __name__ == "__main__":
    kmax = arg("--kmax", 6)
    slots = arg("--slots", "l2tt,l2rr,l2ang", str).split(",")
    ctx = setup(arg("--rank", 6), arg("--denpow", 8), arg("--margin", 6), arg("--prime", 0))
    p, Kc, rank_ = ctx["p"], ctx["Kc"], ctx["rank"]
    t0 = ctx["t0"]
    names, gis, roles = build_space(ctx["GI"], kmax)
    keep = [i for i, (nm, r) in enumerate(zip(names, roles))
            if (r == "slot" and nm.rsplit("_", 1)[0] in slots) or nm in ("spin", "gauge_r")]
    names, gis, roles = [names[i] for i in keep], [gis[i] for i in keep], [roles[i] for i in keep]
    names, gis, roles = representable_only(ctx, names, gis, roles)
    print(f"rank {rank_}, box {ctx['dx']}x{ctx['dy']}: {len(names)} deformations ({slots} x^-1..x^-{kmax} + "
          f"controls), {Kc} Kerr chains [{time.time()-t0:.0f}s]", flush=True)

    T, pnames = chain_to_products_fast(ctx, ctx["chains"], p)
    lp = np.array([lsq_power(n) for n in pnames])
    qmax = rank_ // 2
    top = [i for i, n in enumerate(pnames) if n.strip() == f"Lsq^{qmax}"]
    counts = {m: int((lp == m).sum()) for m in range(qmax + 1)}
    print(f"  {len(pnames)} products; by power of Q: {counts}; pure Q^{qmax} = product {top}", flush=True)
    e_top = np.zeros(len(pnames), dtype=np.int64); e_top[top[0]] = 1
    gamma_top = solve_gamma(T, e_top, p)

    alive, keys, V = pair_tower(ctx, names, gis)
    A, S = len(alive), Kc * len(alive)
    col = {key: j for j, key in enumerate(keys)}
    nm_alive = [names[a] for a in alive]
    role_alive = [roles[a] for a in alive]

    def survivors(w):
        """(total, {leading Q power m: count}) of surviving directions for weights w."""
        U = np.zeros((Kc, S), dtype=np.int64)
        for k in range(Kc):
            for i, a in enumerate(alive):
                U[k, col[(k, a)]] = w[i]
        ker = kernel_np(np.concatenate([U, V]).T, Kc + V.shape[0], p)
        G = rref_np(ker[:, :Kc], p)[0] if ker.shape[0] else np.zeros((0, Kc), np.int64)
        if G.shape[0] == 0:
            return 0, {}
        PG = (G @ T) % p
        r_ge = [rank_np(PG[:, lp >= m], int((lp >= m).sum()), p) if (lp >= m).any() else 0
                for m in range(qmax + 2)]
        return G.shape[0], {m: r_ge[m] - r_ge[m + 1] for m in range(qmax + 1)}

    def block_space(gamma):
        Ug = np.zeros((A, S), dtype=np.int64)
        for i, a in enumerate(alive):
            for k in range(Kc):
                Ug[i, col[(k, a)]] = gamma[k]
        I = intersect_np(V, Ug, S, p)
        sol = []
        for r in I:
            M = np.concatenate([Ug.T, (-r[:, None]) % p], axis=1)
            kk = [v for v in kernel_np(M, A + 1, p) if v[-1] % p]
            sol.append((kk[0][:A] * pow(int(kk[0][-1]), p - 2, p)) % p)
        return rref_np(np.array(sol), p)[0] if sol else np.zeros((0, A), np.int64)

    Wall = None
    for k in range(Kc):
        e = np.zeros(Kc, dtype=np.int64); e[k] = 1
        Wk = block_space(e)
        Wall = Wk if Wall is None else intersect_np(Wall, Wk, A, p)
    Wtop = block_space(gamma_top)
    slot_alive = [i for i, r in enumerate(role_alive) if r == "slot"]
    ns = len(slot_alive)

    def on_slots(W):
        E = np.zeros((ns, A), dtype=np.int64)
        for r_, i in enumerate(slot_alive):
            E[r_, i] = 1
        I = intersect_np(W, E, A, p)
        return I[:, slot_alive] if I.shape[0] else np.zeros((0, ns), np.int64)

    def load_on(names_src, W_src):
        """A saved subspace (rows over names_src) restricted to our slot coordinates, by name."""
        idx = [list(names_src).index(nm_alive[i]) for i in slot_alive]
        Esub = np.eye(len(names_src), dtype=np.int64)[idx]
        I = intersect_np(W_src, Esub, len(names_src), p)
        return I[:, idx] if I.shape[0] else np.zeros((0, ns), np.int64)

    Walls, Wtops = on_slots(Wall), on_slots(Wtop)
    print(f"\n  shape-sector deformations keeping ALL {Kc}: dim {Walls.shape[0]} of {ns}")
    print(f"  shape-sector deformations keeping pure Q^{qmax}:  dim {Wtops.shape[0]} of {ns}", flush=True)

    all66 = [n for n, r in zip(*build_space(ctx["GI"], kmax)[::2]) if r == "slot"]
    W2 = load_on(all66, np.load(f"data/anat/compat_slots_r2_k{kmax}.npy"))
    st = np.load("data/anat/rank4_state.npz")
    r4names = [str(st["names"][a]) for a in st["alive"]]
    WQ2 = load_on(r4names, st["WQ2"])
    for label, Wref in (("rank 2 Carter-compatible", W2), ("rank 4 pure-Q^2", WQ2)):
        both = intersect_np(Wtops, Wref, ns, p).shape[0]
        print(f"  vs {label} (dim {Wref.shape[0]} here): contained in pure-Q^{qmax} space: "
              f"{both == Wref.shape[0]}", flush=True)
    both_all = intersect_np(Walls, W2, ns, p).shape[0]
    print(f"  all-{Kc} space == rank 2 Carter-compatible: {both_all == Walls.shape[0] == W2.shape[0]}")

    def rat_named(w):
        from _kt_carter_space import ratrec
        out = []
        for i, c in enumerate(w):
            if c:
                q = ratrec(int(c), p)
                out.append(f"{q[0]}/{q[1]}*{nm_alive[slot_alive[i]]}" if q and q[1] != 1
                           else f"{q[0] if q else c}*{nm_alive[slot_alive[i]]}")
        return " + ".join(out)

    base = np.concatenate([W2, WQ2]) if WQ2.shape[0] else W2
    base = rref_np(base, p)[0]
    extra = []
    for r in Wtops:
        if rank_np(np.concatenate([base, r[None, :]] if base.shape[0] else [r[None, :]]), ns, p) > base.shape[0]:
            extra.append(r)
            base = rref_np(np.concatenate([base, r[None, :]]), p)[0]
    print(f"\n  pure-Q^{qmax} directions BEYOND rank 4's pure-Q^2 space: {len(extra)}")
    for r in extra:
        w = np.zeros(A, dtype=np.int64); w[slot_alive] = r
        tot, br = survivors(w)
        print(f"    {rat_named(r)}\n      survivors {tot} of {Kc}, by leading Q power {br}", flush=True)

    print("\n  P1: the two rank-4 directions (§140)")
    d = {"d1": {"l2rr_3": 1, "l2ang_3": 1, "l2ang_4": sp.Rational(3, 2)},
         "d2": {"l2rr_4": 1, "l2ang_3": sp.Rational(-10, 21), "l2ang_4": sp.Rational(-5, 14),
                "l2ang_5": sp.Rational(4, 7)}}
    for lab, coef in d.items():
        w = np.zeros(A, dtype=np.int64)
        for nm, c in coef.items():
            q = sp.Rational(c)
            w[nm_alive.index(nm)] = int(q.p) % p * pow(int(q.q) % p, p - 2, p) % p
        tot, br = survivors(w)
        print(f"    {lab}: survivors {tot} of {Kc}, by leading Q power {br}   "
              f"(predicted 21: {{0: 16, 2: 4, 3: 1}})", flush=True)
    print("\n  controls and random shape deformations")
    for i, a in enumerate(alive):
        if role_alive[i] == "control":
            w = np.zeros(A, dtype=np.int64); w[i] = 1
            print(f"    {nm_alive[i]:8s} {survivors(w)}", flush=True)
    rng = np.random.default_rng(6)
    for t_ in range(4):
        w = np.zeros(A, dtype=np.int64); w[slot_alive] = rng.integers(1, p, ns)
        print(f"    random #{t_}: {survivors(w)}", flush=True)
    if "--save" in sys.argv:
        np.savez(arg("--save", None, str), V=V, keys=np.array(keys), alive=np.array(alive), T=T,
                 Wall=Wall, Wtop=Wtop, names=np.array(names), roles=np.array(roles), lp=lp)
    print(f"\n  total {time.time()-t0:.0f}s")
