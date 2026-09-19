#!/usr/bin/env python3
"""The space of deformations of Kerr that keep Carter's constant -- mapped, to O(eps chi^2).

§138 answered "why does Carter die in sGB": three sGB pieces each obstruct it, independently. This
asks the general question: WHICH deformations of Kerr keep it? Not sGB's, any.

THE SPACE. Every stationary, axisymmetric, reflection-symmetric O(eps) deformation of the slowly
rotating Kerr metric, in Regge-Wheeler-type slots, each with a free radial profile:

    eps chi^0   static, spherical      tt, rr, ang          (ang = r^2 dOmega^2 part)
    eps chi^1   frame dragging         drag1 (l=1, as in Kerr and sGB), drag3 (l=3, an octupole current)
    eps chi^2   spherical              l0tt, l0rr, l0ang
    eps chi^2   quadrupolar, the shape l2tt, l2rr, l2ang    (angular dependence Y2 = 3y^2 - 1)

Each profile is spanned by x^-1 .. x^-KMAX. Plus four controls that MUST keep Carter: Kerr's spin
shift, its mass shift, and two pure coordinate changes.

THE METHOD, general enough not to assume anything survives. At fixed Kerr background the zeta tower
is linear in the deformation. Level by level (eps chi^0, chi^1, chi^2) every (Kerr chain, admissible
deformation) source becomes a column of one system; its nullspace gives V; the deformations for which
EVERY Kerr direction still extends are  W = intersection over chains k of { w : e_k (x) w in V }.
Only those are carried to the next level, with particular solutions for a basis of them. What is left
after eps chi^2 is the Carter-compatible space. The conditions defining it are printed as rational
relations between profile coefficients.

Usage:  _kt_carter_space.py [--rank 2 --denpow 6 --margin 6 --kmax 6]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
import _kt_exact as EX  # noqa: E402
import _kt_metrics as MM  # noqa: E402
import _kt_perturb as PB  # noqa: E402
import _kt_search as K  # noqa: E402
from _kt_anatomy import chi_pieces, lie_inverse  # noqa: E402
from _kt_ckcompare import load  # noqa: E402
from _kt_opfast import operator_from_templates  # noqa: E402

x, y = sp.symbols("x y", real=True)
chi = KD.chi


def arg(fl, d, c=int):
    return c(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else d


# ---------------------------------------------------------------- linear algebra mod p (numpy)

def rref_np(M, p, track=False):
    """RREF of an int64 matrix mod p. With track=True also returns T such that R = T M (rows)."""
    M = np.array(M, dtype=np.int64) % p
    m, n = M.shape
    T = np.eye(m, dtype=np.int64) if track else None
    piv, r = [], 0
    for c in range(n):
        if r == m:
            break
        nz = np.nonzero(M[r:, c])[0]
        if nz.size == 0:
            continue
        k = r + int(nz[0])
        if k != r:
            M[[r, k]] = M[[k, r]]
            if track:
                T[[r, k]] = T[[k, r]]
        inv = pow(int(M[r, c]), p - 2, p)
        M[r] = M[r] * inv % p
        if track:
            T[r] = T[r] * inv % p
        f = M[:, c].copy()
        f[r] = 0
        rows = np.nonzero(f)[0]
        if rows.size:
            M[rows] = (M[rows] - (f[rows, None] * M[r][None, :]) % p) % p
            if track:
                T[rows] = (T[rows] - (f[rows, None] * T[r][None, :]) % p) % p
        piv.append(c)
        r += 1
    return (M[:r], piv, T[:r] if track else None)


def rank_np(rows, n, p):
    return 0 if len(rows) == 0 else len(rref_np(np.array(rows).reshape(-1, n), p)[1])


def kernel_np(rows, n, p):
    """Basis (rows) of { v : rows . v = 0 } in GF(p)^n."""
    if len(rows) == 0:
        return np.eye(n, dtype=np.int64)
    R, piv, _ = rref_np(np.array(rows).reshape(-1, n), p)
    free = [c for c in range(n) if c not in piv]
    out = np.zeros((len(free), n), dtype=np.int64)
    for i, f in enumerate(free):
        out[i, f] = 1
        for j, c in enumerate(piv):
            out[i, c] = (-R[j, f]) % p
    return out


def intersect_np(A, B, n, p):
    A = np.array(A, dtype=np.int64).reshape(-1, n)
    B = np.array(B, dtype=np.int64).reshape(-1, n)
    if A.shape[0] == 0 or B.shape[0] == 0:
        return np.zeros((0, n), dtype=np.int64)
    Mt = np.concatenate([A, (-B) % p], axis=0).T          # n x (a + b)
    sol = kernel_np(Mt, A.shape[0] + B.shape[0], p)
    vecs = np.zeros((sol.shape[0], n), dtype=np.int64)
    for i in range(sol.shape[0]):
        for j in range(A.shape[0]):
            if sol[i, j]:
                vecs[i] = (vecs[i] + sol[i, j] * A[j]) % p
    if vecs.shape[0] == 0:
        return vecs
    return rref_np(vecs, p)[0]


def ratrec(a, p):
    """Rational reconstruction of a mod p: (num, den) with |num|, den <= sqrt(p/2)."""
    a %= p
    bound = int((p // 2) ** 0.5)
    r0, r1, s0, s1 = p, a, 0, 1
    while r1 > bound:
        q = r0 // r1
        r0, r1, s0, s1 = r1, r0 - q * r1, s1, s0 - q * s1
    if s1 == 0 or abs(s1) > bound:
        return None
    return (r1, s1) if s1 > 0 else (-r1, -s1)


# ---------------------------------------------------------------- the deformation space

SLOTS = ("tt", "rr", "ang", "drag1", "drag3", "l0tt", "l0rr", "l0ang", "l2tt", "l2rr", "l2ang")


def slot_h(slot, R):
    """Lower-index perturbation h_ab for one slot with radial profile R(x)."""
    Y2 = 3 * y ** 2 - 1
    h = sp.zeros(4, 4)
    ang = lambda F: (x ** 2 * F / (1 - y ** 2), x ** 2 * (1 - y ** 2) * F)   # (h_yy, h_phiphi)
    if slot == "tt":
        h[0, 0] = R
    elif slot == "rr":
        h[1, 1] = R
    elif slot == "ang":
        h[2, 2], h[3, 3] = ang(R)
    elif slot == "drag1":
        h[0, 3] = h[3, 0] = chi * R * (1 - y ** 2)
    elif slot == "drag3":
        h[0, 3] = h[3, 0] = chi * R * (1 - y ** 2) * (5 * y ** 2 - 1)
    elif slot == "l0tt":
        h[0, 0] = chi ** 2 * R
    elif slot == "l0rr":
        h[1, 1] = chi ** 2 * R
    elif slot == "l0ang":
        h[2, 2], h[3, 3] = ang(chi ** 2 * R)
    elif slot == "l2tt":
        h[0, 0] = chi ** 2 * R * Y2
    elif slot == "l2rr":
        h[1, 1] = chi ** 2 * R * Y2
    elif slot == "l2ang":
        h[2, 2], h[3, 3] = ang(chi ** 2 * R * Y2)
    return h


def build_space(GI, kmax):
    names, gis, roles = [], [], []
    for slot in SLOTS:
        for k in range(1, kmax + 1):
            names.append(f"{slot}_{k}")
            gis.append(KD.ginv_perturbation(GI, slot_h(slot, x ** -k)))
            roles.append("slot")
    names.append("spin"); gis.append([sp.zeros(4, 4), GI[1], 2 * GI[2]]); roles.append("control")
    m = sp.Symbol("m", positive=True)
    GIm = KD.kerr_chi_pieces(M=m)
    names.append("mass")
    gis.append([sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.diff(G[i, j], m).subs(m, 1))) for G in GIm])
    roles.append("control")
    giK = sum((chi ** n * GI[n] for n in range(3)), sp.zeros(4, 4))
    t_, x_, y_, ph_ = K.COORDS
    for nm, xi in (("gauge_r", [0, 1 / x_, 0, 0]), ("gauge_y", [0, 0, y_ * (1 - y_ ** 2) / x_ ** 2, 0])):
        names.append(nm); gis.append(chi_pieces(lie_inverse(giK, xi))); roles.append("control")
    return names, gis, roles


def setup(rank_=2, denpow=6, margin=6, prime=0):
    """Operator, Kerr chains and the rest of the fixed context for a Carter-compatibility run."""
    p = KD.PRIMES[prime]
    t0 = time.time()
    t_, ph = sp.symbols("t phi", real=True)
    K.set_dim((t_, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    GI = KD.kerr_chi_pieces()
    L, _, _ = MM.denominator(GI[0])
    den = L ** denpow
    _, prods, _ = EX.generators(GI[0], rank_, den)
    bx, by = EX.reducible_box(prods, den)
    dx, dy = bx + margin, by + margin
    mons = K.monomials(rank_)
    cols, _ = PB.coefficient_basis(mons, dx, dy, den)
    H = [KD.hamiltonian(GI[n]) for n in range(3)]
    dicts0, D = operator_from_templates(H[0], mons, dx, dy, den, p)
    pfx = "" if p == KD.PRIMES[0] else f"_p{KD.PRIMES.index(p)}"
    chains = [[[sp.sympify(e) for e in lvl] for lvl in ch]
              for ch in load(f"data/kt_double_chains_r{rank_}_d{denpow}_b{dx}x{dy}{pfx}.pkl")["chains"]]
    return dict(p=p, t0=t0, GI=GI, den=den, dx=dx, dy=dy, mons=mons, cols=cols, n_w=len(cols), H=H,
                D=D, op=KD._OpArrays(dicts0, p), chains=chains, Kc=len(chains), rank=rank_)


def representable_only(ctx, names, gis, roles):
    keep = []
    for i, nm in enumerate(names):
        bad = [n for n in range(3) if PB.check_perturbation_representable(gis[i][n], ctx["dx"], ctx["dy"],
                                                                          ctx["den"])]
        if bad:
            print(f"  {nm}: outside the ansatz at chi^{bad} -- dropped", flush=True)
        else:
            keep.append(i)
    return [names[i] for i in keep], [gis[i] for i in keep], [roles[i] for i in keep]


def compatible_space(ctx, names, gis):
    """RREF basis (rows, over the given deformations) of those keeping EVERY Kerr direction alive."""
    p, t0, mons, cols, den, n_w = ctx["p"], ctx["t0"], ctx["mons"], ctx["cols"], ctx["den"], ctx["n_w"]
    H, D, op, chains, Kc = ctx["H"], ctx["D"], ctx["op"], ctx["chains"], ctx["Kc"]
    A = len(names)
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

    # Admissible basis: weight vectors over the A deformations. Fsol[(k, b, n)] = F^(1,n) for chain k,
    # basis element b. HSb[b][j] = its Hamiltonian pieces.
    Bw = np.eye(A, dtype=np.int64)
    HSb = [HS[a] for a in range(A)]
    Fsol = {}
    for n in range(3):
        nb = Bw.shape[0]
        srcs = []
        for k, ch in enumerate(chains):
            for b in range(nb):
                acc = sp.Integer(0)
                for j in range(1, n + 1):
                    acc += br(Fsol[(k, b, n - j)], H[j])
                for j in range(0, n + 1):
                    acc += br(ch[n - j], HSb[b][j])
                srcs.append(acc)
        S = len(srcs)
        lev = KD._prep_level(srcs, D, op, None, p, f"eps chi^{n}")
        ns = KD.nullspace_dicts(lev, n_w + S, p)
        C = np.array([[int(z) % p for z in v[n_w:]] for v in ns], dtype=np.int64).reshape(-1, S)
        Fb = [np.asarray(v[:n_w], dtype=np.int64) % p for v in ns]
        # W_n over the current basis: for each chain, V ∩ block_k
        V = rref_np(C, p)[0] if C.shape[0] else np.zeros((0, S), np.int64)
        Wn = None
        for k in range(Kc):
            Uk = np.zeros((nb, S), dtype=np.int64)
            for b in range(nb):
                Uk[b, k * nb + b] = 1
            Ik = intersect_np(V, Uk, S, p)
            Wk = Ik[:, k * nb:(k + 1) * nb] if Ik.shape[0] else np.zeros((0, nb), np.int64)
            Wn = Wk if Wn is None else intersect_np(Wn, Wk, nb, p)
        Wn = rref_np(Wn, p)[0] if Wn.shape[0] else Wn
        print(f"  eps chi^{n}: {S} columns, every Kerr direction extends for a {Wn.shape[0]}-dim space "
              f"of the {nb} [{time.time()-t0:.0f}s]", flush=True)
        newBw = (Wn @ Bw) % p if Wn.shape[0] else np.zeros((0, A), np.int64)
        if n == 2 or Wn.shape[0] == 0:
            Bw = newBw
            break
        # particular solutions for the new basis: targets e_k (x) u, expressed through the nullspace
        R, piv, T = rref_np(C, p, track=True)
        newF = {}
        for i, u in enumerate(Wn):
            for k in range(Kc):
                t = np.zeros(S, dtype=np.int64)
                t[k * nb:(k + 1) * nb] = u
                mu = t[piv] % p                       # t = mu . R  (t lies in the row space)
                chk = np.zeros(S, dtype=np.int64)
                lam = np.zeros(C.shape[0], dtype=np.int64)
                for j, c in enumerate(mu):
                    if c:
                        chk = (chk + c * R[j]) % p
                        lam = (lam + c * T[j]) % p
                if not np.array_equal(chk, t % p):
                    sys.exit("target not in the row space -- W computation is inconsistent")
                F = np.zeros(n_w, dtype=np.int64)
                for j, c in enumerate(lam):
                    if c:
                        F = (F + int(c) * Fb[j]) % p
                newF[(k, i, n)] = vec_to_co(F)
                for mlev in range(n):                  # lower levels combine linearly
                    acc = [sp.Integer(0)] * len(mons)
                    for b in range(nb):
                        if u[b]:
                            for mi in range(len(mons)):
                                acc[mi] += int(u[b]) * Fsol[(k, b, mlev)][mi]
                    newF[(k, i, mlev)] = [sp.cancel(a_) for a_ in acc]
        Fsol = newF
        HSb = [[sum((int(w[a]) * HS[a][j] for a in range(A) if w[a]), sp.Integer(0)) for j in range(3)]
               for w in newBw]
        Bw = newBw

    return rref_np(Bw, p)[0] if Bw.shape[0] else Bw


if __name__ == "__main__":
    ctx = setup(arg("--rank", 2), arg("--denpow", 6), arg("--margin", 6), arg("--prime", 0))
    kmax = arg("--kmax", 6)
    p, t0 = ctx["p"], ctx["t0"]
    names, gis, roles = representable_only(ctx, *build_space(ctx["GI"], kmax))
    A = len(names)
    print(f"rank {ctx['rank']}, box {ctx['dx']}x{ctx['dy']}: {A} deformations ({roles.count('slot')} slot "
          f"profiles x^-1..x^-{kmax}, {roles.count('control')} controls), {ctx['Kc']} Kerr chains "
          f"[{time.time()-t0:.0f}s]", flush=True)
    Bw = compatible_space(ctx, names, gis)
    W = rref_np(Bw, p)[0] if Bw.shape[0] else Bw
    print(f"\n  CARTER-COMPATIBLE DEFORMATIONS: dim {W.shape[0]} of {A}", flush=True)
    ctrl = [a for a in range(A) if roles[a] == "control"]
    for a in ctrl:
        e = np.zeros((1, A), dtype=np.int64); e[0, a] = 1
        inside = rank_np(np.concatenate([W, e]), A, p) == W.shape[0]
        print(f"    control {names[a]:8s} inside: {inside}")
    slot_idx = [a for a in range(A) if roles[a] == "slot"]
    Es = np.zeros((len(slot_idx), A), dtype=np.int64)
    for i, a in enumerate(slot_idx):
        Es[i, a] = 1
    Ws = intersect_np(W, Es, A, p)[:, slot_idx]
    if "--save" in sys.argv:
        np.savez(arg("--save", None, str), Ws=Ws, slot_names=np.array([names[a] for a in slot_idx]))
    print(f"\n  built from the slot profiles alone: dim {Ws.shape[0]} of {len(slot_idx)}")
    for slot in SLOTS:
        idx = [i for i, a in enumerate(slot_idx) if names[a].rsplit("_", 1)[0] == slot]
        E = np.zeros((len(idx), len(slot_idx)), dtype=np.int64)
        for r_, i in enumerate(idx):
            E[r_, i] = 1
        d = intersect_np(Ws, E, len(slot_idx), p).shape[0] if idx else 0
        print(f"    {slot:6s} alone: {d} of {len(idx)} profiles keep Carter")
    cond = kernel_np(Ws, len(slot_idx), p) if Ws.shape[0] else np.eye(len(slot_idx), dtype=np.int64)
    cond = rref_np(cond, p)[0]
    print(f"\n  CONDITIONS: a slot deformation keeps Carter iff these {cond.shape[0]} relations hold "
          f"(coefficient of x^-k in each slot):")
    for r_ in cond:
        terms = []
        for i, c in enumerate(r_):
            if c:
                q = ratrec(int(c), p)
                cs = f"{q[0]}/{q[1]}" if q and q[1] != 1 else (str(q[0]) if q else str(int(c)))
                terms.append(f"{cs}*{names[slot_idx[i]]}")
        print("    " + " + ".join(terms) + " = 0")
    print(f"\n  total {time.time()-t0:.0f}s")

