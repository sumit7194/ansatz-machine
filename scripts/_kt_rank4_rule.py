#!/usr/bin/env python3
"""Does Carter^2 follow the same rule as Carter?  (§140)

§139: at rank 2, a deformation of Kerr keeps Carter's constant iff it is separable (up to a coordinate
change). Rank 4 is the first rung where Q^2 appears (D42). Kerr's rank-4 Killing space is 14:
9 floor (p_t^a p_phi^b H^c) + 4 (Q times p_t^2, p_t p_phi, p_phi^2, H) + 1 (Q^2). The rule predicts:
the deformations keeping Q^2 are exactly those keeping Q. Two ways it could fail, both interesting:

  (1) all 14 directions survive but Q dies     -> an IRREDUCIBLE rank-4 hidden symmetry
  (2) Q^2 survives (with floor) while Q dies    -> the same, weaker

METHOD. Same deformation space as §139 (slots x radial profiles, controls) plus the four sGB pieces.
Every (rank-4 Kerr chain, deformation) pair is carried through eps chi^0 and eps chi^1 with its own
particular solution (pairs that fail are reported, and their deformation set aside); at eps chi^2 all
pairs are columns of one system, giving V. Then:
  W_all  = { w : e_k (x) w in V for all 14 chains }                       (linear)
  W_Q2   = { w : gamma_Q2 (x) w in V }   with gamma_Q2 the pure-Q^2 chain  (linear)
  survivors(w) and whether they contain a Q^2 component, ANY admixture allowed (per w)
and W_all, W_Q2 are compared with rank 2's Carter-compatible space (data/anat/compat_slots_r2_k6.npy).
Chains are identified by their Schwarzschild part, expanded exactly (mod p, at random points) in the 14
reducible products of p_t, p_phi, H0 and L^2.
"""
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
import _kt_exact as EX  # noqa: E402
import _kt_perturb as PB  # noqa: E402
import _kt_search as K  # noqa: E402
from _kt_carter_space import (arg, build_space, intersect_np, kernel_np, rank_np,  # noqa: E402
                              representable_only, rref_np, setup)

x, y = sp.symbols("x y", real=True)


def eval_modp(expr, pts, syms, p):
    """Exact value mod p at each point. Substitutes BY NAME: EX.generators builds its products from
    symbols that print the same as ours but need not carry the same assumptions (real=True), and
    SymPy treats those as different symbols -- a positional subs left y in place (2026-09-19)."""
    names = [str(s) for s in syms]
    out = []
    for pt in pts:
        val = dict(zip(names, pt))
        e = expr.subs({s: val[s.name] for s in expr.free_symbols})
        if e.free_symbols:
            raise ValueError(f"unsubstituted symbols {e.free_symbols}")
        num, den = sp.fraction(sp.together(e))
        out.append(int(num) % p * pow(int(den) % p, p - 2, p) % p)
    return out


def chain_to_products(ctx, chains, p):
    """T (K x K) with chain_k's Schwarzschild part = sum_j T[k, j] * product_j, and the product names."""
    GI = ctx["GI"]
    gnames, prods, pnames = EX.generators(GI[0], ctx["rank"], ctx["den"])
    mons = ctx["mons"]
    syms = [x, y, *K.MOM]
    rng = random.Random(40)
    pts = [[sp.Rational(rng.randint(3, 97), rng.randint(2, 31)) + 2 if s == x else
            sp.Rational(rng.randint(1, 29), 31) if s == y else
            sp.Rational(rng.randint(-40, 40), rng.randint(1, 13)) for s in syms]
           for _ in range(len(prods) + 16)]
    P = np.array([eval_modp(sp.sympify(pr), pts, syms, p) for pr in prods], dtype=np.int64)
    C = []
    for ch in chains:
        F0 = sum((ch[0][mi] * K.mono_expr(e) for mi, e in enumerate(mons)), sp.Integer(0))
        C.append(eval_modp(F0, pts, syms, p))
    C = np.array(C, dtype=np.int64)
    # solve T P = C  (rows): T = C P^+ via kernel of [P^T | -c^T]
    Kp = P.shape[0]
    T = np.zeros((len(chains), Kp), dtype=np.int64)
    for k in range(len(chains)):
        M = np.concatenate([P.T, (-C[k][:, None]) % p], axis=1)       # npts x (Kp + 1)
        ker = kernel_np(M, Kp + 1, p)
        sol = [v for v in ker if v[-1] % p]
        if not sol:
            sys.exit(f"chain {k}: Schwarzschild part is not a combination of the reducible products")
        v = sol[0]
        inv = pow(int(v[-1]), p - 2, p)
        T[k] = (v[:Kp] * inv) % p
    return T, [str(n) for n in pnames]


def pair_tower(ctx, names, gis):
    """Particular solutions per (chain, deformation) through eps chi^1; V at eps chi^2."""
    p, n_w, mons, cols, den = ctx["p"], ctx["n_w"], ctx["mons"], ctx["cols"], ctx["den"]
    H, D, op, chains = ctx["H"], ctx["D"], ctx["op"], ctx["chains"]
    Kc, A = len(chains), len(names)
    HS = [[KD.hamiltonian(g) for g in gi] for gi in gis]

    def vec_to_co(v):
        F = [sp.Integer(0)] * len(mons)
        for j, (mi, a_, b_) in enumerate(cols):
            c_ = int(v[j]) % p
            if c_:
                F[mi] += c_ * x ** a_ * y ** b_
        return [sp.cancel(f / den) for f in F]

    def br(F, Hh):
        if Hh == 0 or F is None or all(f == 0 for f in F):
            return sp.Integer(0)
        return PB.bracket_raw_coeffs(F, Hh, mons)[0]

    alive = list(range(A))
    F1 = {}
    for n in range(3):
        srcs, keys = [], []
        for k, ch in enumerate(chains):
            for a in alive:
                acc = sp.Integer(0)
                for j in range(1, n + 1):
                    acc += br(F1[(k, a, n - j)], H[j])
                for j in range(0, n + 1):
                    acc += br(ch[n - j], HS[a][j])
                srcs.append(acc)
                keys.append((k, a))
        lev = KD._prep_level(srcs, D, op, None, p, f"eps chi^{n}")
        ns = KD.nullspace_dicts(lev, n_w + len(srcs), p)
        if n == 2:
            C = np.array([[int(z) % p for z in v[n_w:]] for v in ns], dtype=np.int64).reshape(-1, len(srcs))
            V = rref_np(C, p)[0] if C.shape[0] else np.zeros((0, len(srcs)), np.int64)
            print(f"  eps chi^2: {len(srcs)} (chain, deformation) columns, dim V = {V.shape[0]} "
                  f"[{time.time()-ctx['t0']:.0f}s]", flush=True)
            return alive, keys, V
        part = {}
        for v in ns:
            cb = [int(z) % p for z in v[n_w:]]
            nz = [j for j, c in enumerate(cb) if c]
            if len(nz) == 1 and cb[nz[0]] == 1:
                part[nz[0]] = v
        failed = {}
        for j, key in enumerate(keys):
            if j not in part:
                failed.setdefault(key[1], []).append(key[0])
        for a, ks in failed.items():
            print(f"  eps chi^{n}: {names[a]} -- chains {ks} do not extend; deformation set aside", flush=True)
        for j, key in enumerate(keys):
            if key[1] not in failed:
                F1[(key[0], key[1], n)] = vec_to_co(part[j][:n_w])
        alive = [a for a in alive if a not in failed]
        print(f"  eps chi^{n}: {len(srcs)} columns, {len(alive)} deformations with every chain extending "
              f"[{time.time()-ctx['t0']:.0f}s]", flush=True)


if __name__ == "__main__":
    kmax = arg("--kmax", 6)
    ctx = setup(arg("--rank", 4), arg("--denpow", 7), arg("--margin", 6), arg("--prime", 0))
    p = ctx["p"]
    names, gis, roles = build_space(ctx["GI"], kmax)
    for nm in KD.SGB_ALL:
        names.append(f"sGB_{nm}"); gis.append(KD.sgb_ginv_pieces(ctx["GI"], keep=(nm,))); roles.append("sGB")
    names, gis, roles = representable_only(ctx, names, gis, roles)
    Kc = ctx["Kc"]
    print(f"rank {ctx['rank']}, box {ctx['dx']}x{ctx['dy']}: {len(names)} deformations, {Kc} Kerr chains "
          f"[{time.time()-ctx['t0']:.0f}s]", flush=True)
    T, pnames = chain_to_products(ctx, ctx["chains"], p)
    q2 = [i for i, nm in enumerate(pnames) if "Lsq^2" in nm]           # EX.generators names: 'Lsq^2
    q1 = [i for i, nm in enumerate(pnames) if ("Lsq" in nm) and i not in q2]
    print(f"  products: {pnames}\n  Q^2 product index {q2}, Q x (degree 2) indices {q1}", flush=True)
    if len(q2) != 1:
        sys.exit("could not identify the unique Lsq^2 product")
    # pure-Q^2 chain combination: gamma with gamma T = e_{Q2}
    Tinv_rows = kernel_np(np.concatenate([T.T, np.eye(T.shape[1], dtype=np.int64)[q2].T * (p - 1) % p],
                                         axis=1), Kc + 1, p)
    g = [v for v in Tinv_rows if v[-1] % p]
    gammaQ2 = (g[0][:Kc] * pow(int(g[0][-1]), p - 2, p)) % p

    alive, keys, V = pair_tower(ctx, names, gis)
    A = len(alive)
    S = Kc * A
    col = {key: j for j, key in enumerate(keys)}

    def in_V(vec):
        return rank_np(np.concatenate([V, vec[None, :]]), S, p) == V.shape[0]

    def survivors(w):
        """(dim of surviving chain combinations, does it contain a Q^2 component) for weights w."""
        U = np.zeros((Kc, S), dtype=np.int64)
        for k in range(Kc):
            for i, a in enumerate(alive):
                U[k, col[(k, a)]] = w[i]
        # G(w) = { gamma : gamma U in V }: kernel of U modulo V
        B = np.concatenate([U, V]).T                           # S x (Kc + dimV)
        ker = kernel_np(B, Kc + V.shape[0], p)
        G = rref_np(ker[:, :Kc], p)[0] if ker.shape[0] else np.zeros((0, Kc), np.int64)
        prodG = (G @ T) % p if G.shape[0] else G
        hasQ2 = bool(G.shape[0]) and bool(np.any(prodG[:, q2[0]] % p))
        return G.shape[0], hasQ2

    # (1) all chains survive; (2) pure Q^2 survives
    def block_space(gamma):
        Ug = np.zeros((A, S), dtype=np.int64)
        for i, a in enumerate(alive):
            for k in range(Kc):
                Ug[i, col[(k, a)]] = gamma[k]
        I = intersect_np(V, Ug, S, p)
        if I.shape[0] == 0:
            return np.zeros((0, A), np.int64)
        # coefficients w of I rows in the basis Ug (Ug rows are independent)
        sol = []
        for r in I:
            M = np.concatenate([Ug.T, (-r[:, None]) % p], axis=1)
            kk = [v for v in kernel_np(M, A + 1, p) if v[-1] % p]
            sol.append((kk[0][:A] * pow(int(kk[0][-1]), p - 2, p)) % p)
        return rref_np(np.array(sol), p)[0]

    Wall = None
    for k in range(Kc):
        e = np.zeros(Kc, dtype=np.int64); e[k] = 1
        Wk = block_space(e)
        Wall = Wk if Wall is None else intersect_np(Wall, Wk, A, p)
    WQ2 = block_space(gammaQ2)
    nm_alive = [names[a] for a in alive]
    role_alive = [roles[a] for a in alive]
    if "--save" in sys.argv:
        np.savez(arg("--save", None, str), V=V, keys=np.array(keys), alive=np.array(alive), T=T,
                 gammaQ2=gammaQ2, Wall=Wall, WQ2=WQ2, names=np.array(names), roles=np.array(roles),
                 q2=np.array(q2), q1=np.array(q1))
    print(f"\n  ALL {Kc} rank-4 directions survive: dim {Wall.shape[0]} of {A}")
    print(f"  pure Q^2 survives:                dim {WQ2.shape[0]} of {A}")

    # compare with rank 2's Carter-compatible space, on the slot coordinates
    slot_alive = [i for i, r in enumerate(role_alive) if r == "slot"]
    all_slot_names = [n for n, r in zip(*build_space(ctx["GI"], kmax)[::2]) if r == "slot"]
    cache = f"data/anat/compat_slots_r2_k{kmax}.npy"
    if os.path.exists(cache):
        W2 = np.load(cache)                                    # over all_slot_names
        idx = [all_slot_names.index(nm_alive[i]) for i in slot_alive]
        dropped = [j for j in range(len(all_slot_names)) if j not in idx]
        W2_on_alive = intersect_np(W2, np.eye(len(all_slot_names), dtype=np.int64)[idx], len(all_slot_names), p)
        W2a = W2_on_alive[:, idx] if W2_on_alive.shape[0] else np.zeros((0, len(idx)), np.int64)

        def on_slots(W):
            E = np.zeros((len(slot_alive), A), dtype=np.int64)
            for r_, i in enumerate(slot_alive):
                E[r_, i] = 1
            I = intersect_np(W, E, A, p)
            return I[:, slot_alive] if I.shape[0] else np.zeros((0, len(slot_alive)), np.int64)
        for label, W in (("all 14 survive", Wall), ("pure Q^2 survives", WQ2)):
            Ws = on_slots(W)
            both = intersect_np(Ws, W2a, len(slot_alive), p).shape[0]
            print(f"  slot deformations where {label}: dim {Ws.shape[0]}; rank-2 Carter-compatible: "
                  f"dim {W2a.shape[0]}; common: {both}  -> "
                  f"{'SAME SPACE' if both == Ws.shape[0] == W2a.shape[0] else 'DIFFERENT'}", flush=True)
        if dropped:
            print(f"  (slot profiles set aside at rank 4 before chi^2: {[all_slot_names[j] for j in dropped]})")

    print("\n  per deformation: survivors of 14, and whether any survivor carries a Q^2 component")
    for i, a in enumerate(alive):
        if role_alive[i] in ("sGB", "control") or names[a].endswith("_1"):
            w = np.zeros(A, dtype=np.int64); w[i] = 1
            d, q = survivors(w)
            print(f"    {names[a]:12s} {d:2d} of {Kc}   Q^2 survives: {q}", flush=True)
    rng = np.random.default_rng(4)
    for t in range(6):
        w = np.zeros(A, dtype=np.int64)
        w[slot_alive] = rng.integers(1, p, len(slot_alive))
        d, q = survivors(w)
        print(f"    random slot deformation #{t}: {d:2d} of {Kc}   Q^2 survives: {q}", flush=True)
    wfull = np.array([1 if r == "sGB" else 0 for r in role_alive], dtype=np.int64)
    d, q = survivors(wfull)
    print(f"    full sGB     {d:2d} of {Kc}   Q^2 survives: {q}")
    print(f"\n  total {time.time()-ctx['t0']:.0f}s")
