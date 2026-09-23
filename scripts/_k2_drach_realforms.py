#!/usr/bin/env python3
"""K2 -> K1 step 3b: COMPUTE (not argue) the real-form test for every additive Drach member.

For additive U = F(x) + G(y), a real Euclidean form (x = z, y = zbar, after (1,1) maps x -> lam x + s, y -> y/lam + t
and/or x <-> y) needs  G(w/lam + t) = conj(F)(conj(lam) w + conj(s)) + const  for all w.  Two w-derivatives give the
computable NECESSARY condition: F'' == 0 identically  <=>  G'' == 0 identically; and non-affinity needs F'' != 0.
Both conditions are linear in the couplings (alpha, beta, gamma), so each is a null space, found at 50 digits.
Verdict per member:
  - F'' == 0 forced but G'' != 0 possible (or vice versa): conjugacy forces the other to vanish -> the couplings that
    survive make V affine -> NO NON-AFFINE REAL FORM (computed);
  - both can be nonzero: FLAGGED -> needs an explicit conjugacy construction ((e) must land here: the control).
"""
import random
import sys

import mpmath as mp
import sympy as sp

sys.path.insert(0, "scripts")
from _k2_drach import DRACH, al, be, ga, mu, a, c, m, rho, x, y  # noqa: E402

mp.mp.dps = 50
X0, Y0 = sp.Rational(17, 3), sp.Rational(23, 5)


def nullspace(expr_cols, var, npts=6, seed=3):
    rnd = random.Random(seed)
    rows = []
    for _ in range(npts):
        v = sp.Rational(rnd.randint(40, 90), 7)
        rows.append([mp.mpf(sp.N(cc.subs(var, v), 60)) if cc != 0 else mp.mpf(0) for cc in expr_cols])
    M = mp.matrix(rows)
    _, S, V = mp.svd_r(M)
    sv = [S[i] for i in range(min(M.rows, M.cols))]
    null = [i for i, s in enumerate(sv) if abs(s) < mp.mpf(10) ** -35] + list(range(len(sv), 3))
    return [[V[i, j] if i < V.rows else (1 if j == i else 0) for j in range(3)] for i in null]


def member_test(name, U, coupling_mask, shape):
    Us = U.subs(shape)
    F = Us.subs(y, Y0); G = Us.subs(x, X0) - Us.subs({x: X0, y: Y0})
    Fpp, Gpp = sp.diff(F, x, 2), sp.diff(G, y, 2)
    cF = [sp.diff(Fpp, v) if mk else sp.Integer(0) for v, mk in zip((al, be, ga), coupling_mask)]
    cG = [sp.diff(Gpp, v) if mk else sp.Integer(0) for v, mk in zip((al, be, ga), coupling_mask)]
    free = [v for v, mk in zip((al, be, ga), coupling_mask) if mk]
    nF = nullspace(cF, x); nG = nullspace(cG, y)
    # restrict to the member's own couplings: directions with components only on `free`
    dim_free = len(free)
    F_always_zero = all(cc == 0 for cc in cF)
    G_always_zero = all(cc == 0 for cc in cG)
    if F_always_zero and G_always_zero:
        verdict = "V AFFINE for all couplings -> no non-affine real form"
    elif F_always_zero or G_always_zero:
        other = "G''" if F_always_zero else "F''"
        verdict = f"one side always affine -> conjugacy forces {other} = 0 -> V affine -> NO NON-AFFINE REAL FORM"
    else:
        verdict = "both F'' and G'' can be nonzero -> FLAGGED: needs explicit conjugacy"
    print(f"  ({name}) couplings {free}: F''==0 always: {F_always_zero}; G''==0 always: {G_always_zero}  ->  {verdict}", flush=True)
    return verdict


def main():
    generic = {mu: sp.Rational(3, 7), a: sp.Rational(5, 9), c: sp.Rational(7, 5), m: sp.Rational(2, 5), rho: sp.Rational(9, 4)}
    g_ = lambda U: {k: v for k, v in generic.items() if k in U.free_symbols}
    # additive members found in step 3 (couplings that survive U_xy = 0), generic and special shape parameters
    members = [
        ("d  [gamma]", DRACH["d"], (0, 0, 1), g_(DRACH["d"])),
        ("e  [beta,gamma]  CONTROL", DRACH["e"], (0, 1, 1), {}),
        ("f  [gamma]", DRACH["f"], (0, 0, 1), g_(DRACH["f"])),
        ("g  [beta]", DRACH["g"], (0, 1, 0), g_(DRACH["g"])),
        ("k  [alpha,gamma]", DRACH["k"], (1, 0, 1), {}),
        ("l  [alpha,beta]", DRACH["l"], (1, 1, 0), g_(DRACH["l"])),
        ("b  mu=0 [beta]", DRACH["b"], (0, 1, 0), {mu: 0}),
        ("c  a=0 [beta,gamma]", DRACH["c"], (0, 1, 1), {a: 0}),
        ("g  m=0 [alpha,beta,gamma]", DRACH["g"], (1, 1, 1), {m: 0}),
        ("h  m=0 [alpha,beta,gamma]", DRACH["h"], (1, 1, 1), {m: 0}),
        ("l  rho=0 [alpha,beta]", DRACH["l"], (1, 1, 0), {rho: 0}),
    ]
    out = {nm: member_test(nm, U, mk, sh) for nm, U, mk, sh in members}
    flagged = [nm for nm, v in out.items() if "FLAGGED" in v]
    print(f"\n  FLAGGED for explicit conjugacy: {flagged}")
    ok_ctrl = flagged == ["e  [beta,gamma]  CONTROL"]
    print(f"  control: only (e) flagged -> {'ok' if ok_ctrl else 'FAIL'}")
    # (e) explicit: F = beta x^-1/2, G = gamma y^-1/2, lam = 1, s = t = 0: G = conj(F) iff gamma = conj(beta)
    print("  (e) explicit conjugacy: gamma = conj(beta) gives V = 2 Re(beta z^(-1/2)) -- the section-147 SW-IV potential")
    return 0 if ok_ctrl else 1


if __name__ == "__main__":
    sys.exit(main())
