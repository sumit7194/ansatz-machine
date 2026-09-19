#!/usr/bin/env python3
"""The deformations where Carter^2 survives but Carter dies: extract them, then try to kill them. (§140)

_kt_rank4_rule found the slot deformations where the pure-Q^2 chain extends to O(eps chi^2) span 45
dimensions, against 43 where Carter itself extends (the same 43 where all 14 rank-4 directions do).
Two extra directions: at face value, deformations of Kerr with a Carter^2-like conserved quantity and no
Carter -- an IRREDUCIBLE rank-4 hidden symmetry at this order. This script, in order:

  1. extracts the two directions modulo the Carter-compatible space, in reduced rational form;
  2. recounts survivors for each from the saved rank-4 system (expect 10 of 14, one carrying Q^2);
  3. builds each as ONE concrete metric deformation and re-tests it from scratch, with bigger ansaetze
     and the other prime: Carter at rank 2 (must still die, or Q^2 is reducible after all) and Q^2 at
     rank 4 (must still survive).
Usage: _kt_q2_candidate.py [--state data/anat/rank4_state.npz]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
from _kt_carter_space import (arg, matmul_mod, build_space, compatible_space, intersect_np, kernel_np,  # noqa: E402
                              rank_np, ratrec, rref_np, setup)
from _kt_rank4_rule import chain_to_products, pair_tower  # noqa: E402

P0 = KD.PRIMES[0]


def rat(c, p):
    q = ratrec(int(c), p)
    return sp.Rational(q[0], q[1]) if q else None


def survivors(V, keys, alive, Kc, T, q2, w, p):
    S = V.shape[1]
    col = {(int(k), int(a)): j for j, (k, a) in enumerate(keys)}
    U = np.zeros((Kc, S), dtype=np.int64)
    for k in range(Kc):
        for i, a in enumerate(alive):
            U[k, col[(k, int(a))]] = w[i]
    ker = kernel_np(np.concatenate([U, V]).T, Kc + V.shape[0], p)
    G = rref_np(ker[:, :Kc], p)[0] if ker.shape[0] else np.zeros((0, Kc), np.int64)
    prodG = matmul_mod(G, T, p) if G.shape[0] else G
    return G.shape[0], bool(G.shape[0]) and bool(np.any(prodG[:, q2] % p)), prodG


def combine(gis_list, weights):
    """One deformation = sum_a w_a * piece_a (g^ab pieces, chi^0..chi^2), rational weights."""
    out = []
    for n in range(3):
        M = sp.zeros(4, 4)
        for g, w in zip(gis_list, weights):
            if w:
                M += w * g[n]
        out.append(M.applyfunc(sp.cancel))
    return out


if __name__ == "__main__":
    t0 = time.time()
    st = np.load(arg("--state", "data/anat/rank4_state.npz", str))
    V, keys, alive, T = st["V"], st["keys"], st["alive"], st["T"]
    WQ2, Wall, names, roles = st["WQ2"], st["Wall"], list(st["names"]), list(st["roles"])
    q2 = int(st["q2"][0])
    p, Kc = P0, T.shape[0]
    A = len(alive)
    role_alive = [roles[a] for a in alive]
    nm_alive = [names[a] for a in alive]
    slot_alive = [i for i, r in enumerate(role_alive) if r == "slot"]

    def on_slots(W):
        E = np.zeros((len(slot_alive), A), dtype=np.int64)
        for r_, i in enumerate(slot_alive):
            E[r_, i] = 1
        I = intersect_np(W, E, A, p)
        return I[:, slot_alive] if I.shape[0] else np.zeros((0, len(slot_alive)), np.int64)

    WQ2s, Walls = on_slots(WQ2), on_slots(Wall)
    n = len(slot_alive)
    print(f"slot space {n}; all-14 {Walls.shape[0]}; pure-Q^2 {WQ2s.shape[0]}", flush=True)

    # 1. two directions of WQ2s beyond Walls (= the Carter-compatible space), reduced mod Walls
    R, piv, _ = rref_np(Walls, p)
    extra = []
    basis = Walls.copy()
    for r in WQ2s:
        if rank_np(np.concatenate([basis, r[None, :]]), n, p) > basis.shape[0]:
            v = r.copy()
            for j, c in enumerate(piv):
                if v[c]:
                    v = (v - v[c] * R[j]) % p
            extra.append(v)
            basis = np.concatenate([basis, r[None, :]])
    extra = rref_np(np.array(extra), p)[0]
    print(f"\n1. {extra.shape[0]} direction(s) where Q^2 survives and Carter does not (mod the compatible space):")
    ws = []
    for e in extra:
        terms, wr = [], [sp.Integer(0)] * n
        for i, c in enumerate(e):
            if c:
                q = rat(c, p)
                wr[i] = q
                terms.append(f"{q}*{nm_alive[slot_alive[i]]}")
        ws.append(wr)
        print("   " + " + ".join(terms), flush=True)

    # 2. survivors from the saved system
    print("\n2. survivors of 14 at rank 4 (saved system, prime 0):")
    for e in extra:
        w = np.zeros(A, dtype=np.int64)
        w[slot_alive] = e
        d, has, prodG = survivors(V, keys, alive, Kc, T, q2, w, p)
        print(f"   {d} of 14, Q^2 among them: {has}", flush=True)

    # 3. each as ONE concrete metric, from scratch, bigger ansaetze, both primes
    kmax = arg("--kmax", 6)
    print("\n3. from scratch, as single concrete deformations:", flush=True)
    for label, rank_, denpow, margin in (("Carter, rank 2", 2, 8, 10), ("Q^2, rank 4", 4, 7, 6)):
        for prime in (0, 1):
            ctx = setup(rank_, denpow, margin, prime)
            snames, sgis, sroles = build_space(ctx["GI"], kmax)
            slot_gis = [g for g, r in zip(sgis, sroles) if r == "slot"]
            slot_nm = [nm for nm, r in zip(snames, sroles) if r == "slot"]
            dnames, dgis = [], []
            for t_, wr in enumerate(ws):
                full = [sp.Integer(0)] * len(slot_nm)
                for i, q in enumerate(wr):
                    if q:
                        full[slot_nm.index(nm_alive[slot_alive[i]])] = q
                dnames.append(f"candidate_{t_}")
                dgis.append(combine(slot_gis, full))
            if rank_ == 2:
                W = compatible_space(ctx, dnames, dgis)
                print(f"   {label}, L^{denpow}, box {ctx['dx']}x{ctx['dy']}, prime {prime}: Carter survives for "
                      f"a {W.shape[0]}-dim part of the {len(dnames)} candidates (0 = dies for all)", flush=True)
            else:
                T4, pn = chain_to_products(ctx, ctx["chains"], ctx["p"])
                q2i = [i for i, nm in enumerate(pn) if "Lsq^2" in nm][0]
                al, ks, V4 = pair_tower(ctx, dnames, dgis)
                for i_, a in enumerate(al):
                    w = np.zeros(len(al), dtype=np.int64); w[i_] = 1
                    d, has, _ = survivors(V4, np.array(ks), np.array(al), ctx["Kc"], T4, q2i, w, ctx["p"])
                    print(f"   {label}, L^{denpow}, prime {prime}: {dnames[a]}: {d} of 14 survive, Q^2 among "
                          f"them: {has}", flush=True)
    print(f"\n  total {time.time()-t0:.0f}s")
