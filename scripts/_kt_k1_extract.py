#!/usr/bin/env python3
"""Extract K1: the FIRST-ORDER CORRECTION to Carter for one deformation.  (leg 6)

WHY IT IS NEEDED. compatible_space answers "can Carter be corrected?" and throws the correction away.
A collaborator measured the drift of BARE Q on our objects and found it non-conserved -- correctly,
because bare Q is not what survives. What survives on a compatible deformation is Q + eps*K1, and
until K1 is written down nobody can test the object that is actually claimed to be conserved.

WHAT IT RETURNS. K1 = sum_n chi^n F^(1,n) for the Carter chain, as an explicit polynomial in the
momenta with coefficients rational in (x = r, y = cos theta). Coefficients are rational-reconstructed
from GF(p), and the reconstruction is CHECKED by re-reducing mod p.

NON-UNIQUENESS, stated because it matters for the test: K1 is defined up to adding any Killing tensor
of the undeformed background. Two valid K1 differ by a conserved quantity, so the drift of Q + eps*K1
does not depend on the choice -- but the printed expression does.

Repro:  .venv/bin/python scripts/_kt_k1_extract.py --obj A [--prime 0]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
import _kt_perturb as PB  # noqa: E402
import _kt_search as K  # noqa: E402
from _kt_carter_space import (arg, build_space, intersect_np, matmul_mod, ratrec,  # noqa: E402
                              rref_np, setup, x, y)
from _kt_q2_candidate import combine  # noqa: E402

chi = KD.chi
FAMILY = ("l2tt", "l2rr", "l2ang")
KMAX = 6
COEF = {
    "A": {"l2tt_2": 1, "l2tt_5": -32, "l2tt_6": 48, "l2rr_3": 4, "l2rr_4": -84,
          "l2ang_3": 4, "l2ang_4": 8, "l2ang_5": -48},
    "C": {"l2rr_3": 1, "l2ang_3": 1, "l2ang_4": sp.Rational(3, 2)},
}
CARTER_CHAIN = 4        # its chi^0 part is supported on p_y^2 and p_phi^2, i.e. L^2


def corrections(ctx, gi):
    """Fsol[(k, n)] for a SINGLE deformation: the chain-k correction at order chi^n, or None."""
    p, mons, cols, den, n_w = ctx["p"], ctx["mons"], ctx["cols"], ctx["den"], ctx["n_w"]
    H, D, op, chains, Kc = ctx["H"], ctx["D"], ctx["op"], ctx["chains"], ctx["Kc"]
    HS = [KD.hamiltonian(g) for g in gi]

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

    Fsol = {}
    for n in range(3):
        srcs = []
        for k, ch in enumerate(chains):
            acc = sp.Integer(0)
            for j in range(1, n + 1):
                acc += br(Fsol.get((k, n - j)), H[j])
            for j in range(0, n + 1):
                acc += br(ch[n - j], HS[j])
            srcs.append(acc)
        S = len(srcs)
        lev = KD._prep_level(srcs, D, op, None, p, f"eps chi^{n}")
        ns = KD.nullspace_dicts(lev, n_w + S, p)
        C = np.array([[int(z) % p for z in v[n_w:]] for v in ns], dtype=np.int64).reshape(-1, S)
        Fb = [np.asarray(v[:n_w], dtype=np.int64) % p for v in ns]
        R, piv, T = rref_np(C, p, track=True)
        for k in range(Kc):
            t = np.zeros(S, dtype=np.int64)
            t[k] = 1                                   # target: extend chain k with weight 1
            mu = t[piv] % p
            chk = np.zeros(S, dtype=np.int64)
            lam = np.zeros(C.shape[0], dtype=np.int64)
            for j, c in enumerate(mu):
                if c:
                    chk = (chk + c * R[j]) % p
                    lam = (lam + c * T[j]) % p
            if not np.array_equal(chk, t % p):
                Fsol[(k, n)] = None                    # chain k does NOT extend at this order
                continue
            F = np.zeros(n_w, dtype=np.int64)
            for j, c in enumerate(lam):
                if c:
                    F = (F + int(c) * Fb[j]) % p
            Fsol[(k, n)] = vec_to_co(F)
        print(f"  eps chi^{n}: chains extending = "
              f"{[k for k in range(Kc) if Fsol[(k, n)] is not None]}", flush=True)
    return Fsol


def ratrec_mod(a, M):
    """Rational reconstruction against an arbitrary modulus M (ratrec hardcodes a prime)."""
    a %= M
    bound = int((M // 2) ** 0.5)
    r0, r1, s0, s1 = M, a, 0, 1
    while r1 > bound:
        q = r0 // r1
        r0, r1, s0, s1 = r1, r0 - q * r1, s1, s0 - q * s1
    if s1 == 0 or abs(s1) > bound:
        return None
    return (r1, s1) if s1 > 0 else (-r1, -s1)


def to_rational_crt(e0, e1, p0, p1):
    """Reconstruct from residues mod TWO primes via CRT, then check against both.

    One prime was not enough: sqrt(p/2) ~ 32767 and a real coefficient came out 149632, so
    reconstruction failed on a value that is simply larger than the single-prime bound. CRT lifts the
    modulus to p0*p1 ~ 4.6e18, giving a bound of ~1.5e9 -- and because the answer must re-reduce
    correctly mod BOTH primes, the two-prime agreement is a check rather than just more room."""
    M = p0 * p1
    inv = pow(p0 % p1, p1 - 2, p1)
    n0, d0 = sp.fraction(sp.together(sp.cancel(e0)))
    n1, d1 = sp.fraction(sp.together(sp.cancel(e1)))
    P0, P1 = sp.Poly(sp.expand(n0), x, y), sp.Poly(sp.expand(n1), x, y)
    c1 = dict(zip(P1.monoms(), [int(c) % p1 for c in P1.coeffs()]))
    if set(P0.monoms()) != set(c1):
        raise ValueError("the two primes produced different monomial supports")
    out = sp.Integer(0)
    for mono, c in zip(P0.monoms(), P0.coeffs()):
        a0, a1 = int(c) % p0, c1[mono]
        a = (a0 + p0 * (((a1 - a0) * inv) % p1)) % M          # CRT lift
        q = ratrec_mod(a, M)
        if q is None:
            raise ValueError(f"reconstruction failed even over two primes for residue {a0}")
        if (q[0] - q[1] * a0) % p0 or (q[0] - q[1] * a1) % p1:
            raise ValueError("reconstruction does not re-reduce mod BOTH primes")
        out += sp.Rational(q[0], q[1]) * x ** mono[0] * y ** mono[1]
    if sp.simplify(d0 - d1) != 0:
        raise ValueError("the two primes produced different denominators")
    return sp.cancel(out / d0)


if __name__ == "__main__":
    t0 = time.time()
    obj = arg("--obj", "A", str)
    prime = arg("--prime", 0)
    ctxs, Fs = [], []
    for pr in (0, 1):
        ctxs.append(setup(2, 8, 10, pr))
    ctx = ctxs[0]
    p = ctx["p"]
    names, gis, roles = build_space(ctx["GI"], KMAX, slots=FAMILY)
    keep = [i for i, r_ in enumerate(roles) if r_ == "slot"]
    names = [names[i] for i in keep]
    gis = [gis[i] for i in keep]
    gi = combine(gis, [sp.Rational(COEF[obj].get(n, 0)) for n in names])
    if obj == "C":
        from _kt_anatomy import chi_pieces, lie_inverse
        giK = sum((chi ** n * ctx["GI"][n] for n in range(3)), sp.zeros(4, 4))
        G = chi_pieces(lie_inverse(giK, [0, chi ** 2 * (3 * y ** 2 - 1) / x, 0, 0]))
        gi = [sp.Matrix(gi[k]) + sp.Matrix(G[k]) for k in range(3)]
    print(f"object {obj}, rank 2, prime {prime} [{time.time()-t0:.0f}s]\n", flush=True)

    for c_ in ctxs:
        print(f"\n  --- prime {KD.PRIMES.index(c_['p'])} ---", flush=True)
        Fs.append(corrections(c_, gi))
    Fsol = Fs[0]
    ok = all(Fs[i][(CARTER_CHAIN, n)] is not None for n in range(3) for i in (0, 1))
    print(f"\n  Carter chain ({CARTER_CHAIN}) extends at every order: {ok}", flush=True)
    if not ok:
        bad = [n for n in range(3) if Fsol[(CARTER_CHAIN, n)] is None]
        print(f"  It FAILS at chi^{bad} -- so no polynomial K1 exists for {obj}. That asymmetry IS")
        print(f"  the content and must be reported, not worked around.")
        raise SystemExit(0)

    mons = ctx["mons"]
    P_t, P_x, P_y, P_ph = K.MOM
    terms = []
    for n in range(3):
        for mi, m in enumerate(mons):
            c = Fsol[(CARTER_CHAIN, n)][mi]
            if sp.simplify(c) == 0:
                continue
            cr = to_rational_crt(c, Fs[1][(CARTER_CHAIN, n)][mi], ctxs[0]["p"], ctxs[1]["p"])
            terms.append(chi ** n * cr * P_t ** m[0] * P_x ** m[1] * P_y ** m[2] * P_ph ** m[3])
    K1 = sp.Add(*terms)
    print(f"\n  K1 assembled, {len(terms)} terms [{time.time()-t0:.0f}s]", flush=True)
    out = f"data/triple/K1_{obj}.txt"
    with open(out, "w") as fh:
        fh.write(f"K1 for object {obj}: the O(eps) correction to Carter, so that Q + eps*K1 is\n"
                 f"conserved to O(eps^2). Coordinates x = r, y = cos(theta); momenta P_t, P_x, P_y,\n"
                 f"P_phi; chi is the spin parameter a (M = 1). Defined up to adding any Killing\n"
                 f"tensor of the undeformed background.\n\nK1 =\n{sp.sstr(sp.simplify(K1))}\n")
    print(f"  wrote {out} ({os.path.getsize(out)} bytes)")
    print(f"\n  total {time.time()-t0:.0f}s")
