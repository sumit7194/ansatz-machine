#!/usr/bin/env python3
"""The pole-order test for pure O(chi^2) deformations, reduced to ONE linear system.  (§142)

WHY IT REDUCES. A deformation that enters only at O(eps chi^2) -- the shape sector, and any O(chi^2)
coordinate change -- has zero sources at eps chi^0 and eps chi^1, so its particular solutions there are
zero, and its eps chi^2 source for a Kerr direction is just {dH, K} with K the direction's SCHWARZSCHILD
part. The Schwarzschild Killing tensors at rank r are known exactly: the products of p_t, p_phi, H0 and
L^2. So instead of building the Kerr chi-tower (55 chains at rank 8) and identifying chains, solve

    { H0, F } = -{ dH_a, K_j }        for every (product K_j, deformation a)  -- one system

and read survivors directly in product coordinates. Exactly equivalent to _kt_qpower's pair tower for
these deformations; validated by reproducing its rank-4 and rank-6 results before use at rank 8.
Control: a pure O(chi^2) coordinate change with the l=2 pattern must keep every direction.
Usage: _kt_pole_reduced.py --rank 8 --denpow 7 --margin 4 [--kmax 6] [--prime 0]
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
from _kt_carter_space import (arg, build_space, intersect_np, kernel_np, rank_np, ratrec,  # noqa: E402
                              rref_np)
from _kt_opfast import operator_from_templates  # noqa: E402
from _kt_qpower import lsq_power  # noqa: E402

x, y = sp.symbols("x y", real=True)
chi = KD.chi


def product_coeffs(expr, mons):
    """A Schwarzschild product (expression in momenta) -> coefficient list over the momentum monomials."""
    e = sp.sympify(expr)
    byname = {str(m): m for m in K.MOM}
    e = e.subs({s: byname[s.name] for s in e.free_symbols if s.name in byname})
    e = e.subs({s: {"x": x, "y": y}[s.name] for s in e.free_symbols if s.name in ("x", "y")})
    num, den = sp.fraction(sp.together(e))
    P = sp.Poly(sp.expand(num), *K.MOM)
    co = {mono: c for mono, c in zip(P.monoms(), P.coeffs())}
    return [sp.cancel(co.get(tuple(m), 0) / den) for m in mons]


if __name__ == "__main__":
    t0 = time.time()
    rank_, denpow, margin = arg("--rank", 8), arg("--denpow", 7), arg("--margin", 4)
    kmax, prime = arg("--kmax", 6), arg("--prime", 0)
    p = KD.PRIMES[prime]
    t_, ph = sp.symbols("t phi", real=True)
    K.set_dim((t_, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    GI = KD.kerr_chi_pieces()
    L, _, _ = MM.denominator(GI[0])
    den = L ** denpow
    _, prods, pnames = EX.generators(GI[0], rank_, den)
    pnames = [str(n) for n in pnames]
    bx, by = EX.reducible_box(prods, den)
    dx, dy = bx + margin, by + margin
    mons = K.monomials(rank_)
    cols, _ = PB.coefficient_basis(mons, dx, dy, den)
    n_w = len(cols)
    H0 = KD.hamiltonian(GI[0])
    dicts0, D = operator_from_templates(H0, mons, dx, dy, den, p)
    op = KD._OpArrays(dicts0, p)
    lp = np.array([lsq_power(n) for n in pnames])
    qmax = rank_ // 2
    print(f"rank {rank_}, L^{denpow}, box {dx}x{dy}: {n_w} unknowns, {len(prods)} Schwarzschild products "
          f"(by Q power {dict((m, int((lp == m).sum())) for m in range(qmax + 1))}), prime {prime} "
          f"[{time.time()-t0:.0f}s]", flush=True)

    # deformations: the shape sector, plus pure O(chi^2) l=2 coordinate changes (controls)
    want = arg("--slots", "l2tt,l2rr,l2ang", str).split(",")
    from _kt_carter_space import SLOTS, SLOTS_L4, SLOTS_AXIAL
    all_slots = tuple(SLOTS) + tuple(SLOTS_L4) + tuple(sl for ell in sorted(SLOTS_AXIAL) for sl in SLOTS_AXIAL[ell])
    unknown = [w for w in want if w not in all_slots]
    if unknown:
        sys.exit(f"--slots names nothing: {unknown}\n  known: {' '.join(all_slots)}")
    names, gis, roles = build_space(GI, kmax, slots=all_slots)
    keep = [i for i, (n, r) in enumerate(zip(names, roles)) if r == "slot" and n.rsplit("_", 1)[0] in want]
    # A run with zero deformations is not a null, it is an empty question: every product survives
    # trivially and the random control cannot fire.  It printed "dim 0 of 0" and exited 0 once.
    if not keep:
        sys.exit("no deformation slots selected -- refusing to report a vacuous null")
    names = [names[i] for i in keep]; gis = [gis[i] for i in keep]; roles = ["slot"] * len(keep)
    giK = sum((chi ** n * GI[n] for n in range(3)), sp.zeros(4, 4))
    for k in (1, 3):
        for nm, xi in ((f"gaugeY2r_{k}", [0, chi ** 2 * (3 * y ** 2 - 1) * x ** -k, 0, 0]),
                       (f"gaugeY2y_{k}", [0, 0, chi ** 2 * y * (1 - y ** 2) * x ** -k, 0])):
            names.append(nm); gis.append(chi_pieces(lie_inverse(giK, xi))); roles.append("control")
    # AXIAL gauge controls.  The two above drag along r and theta, so they land in the POLAR sector:
    # they show the system is not killing things generically, but they say nothing about whether the
    # solution box is wide enough to express the F that an ODD-parity deformation needs.  A null in
    # the axial family is worth nothing without a positive control inside that family (D40), and a
    # drag along phi is exactly it -- pure gauge, so it MUST keep every product.
    # --axial-controls 0 reproduces the pre-§146 configuration exactly (four polar gauge controls):
    # a second-prime rerun of §142/§143 must match its first prime column for column, and extra
    # control columns would change dim V and the nullity even though no slot-sector number moves.
    for k in ((1, 3) if arg("--axial-controls", 1) else ()):
        for wn, W in (("1", sp.Integer(1)), ("y2", y ** 2)):
            nm = f"gaugeAx{wn}_{k}"
            names.append(nm); gis.append(chi_pieces(lie_inverse(giK, [0, 0, 0, chi ** 2 * W * x ** -k])))
            roles.append("control")
    for nm, g in zip(names, gis):
        if g[0] != sp.zeros(4, 4) or g[1] != sp.zeros(4, 4):
            sys.exit(f"{nm} is not a pure O(chi^2) deformation -- the reduction does not apply")
    HS2 = [KD.hamiltonian(g[2]) for g in gis]
    A = len(names)
    Fk = [product_coeffs(pr, mons) for pr in prods]
    Kc = len(Fk)

    srcs = []
    for j in range(Kc):
        for a in range(A):
            srcs.append(PB.bracket_raw_coeffs(Fk[j], HS2[a], mons)[0])
    print(f"  {len(srcs)} sources built [{time.time()-t0:.0f}s]", flush=True)
    lev = KD._prep_level(srcs, D, op, None, p, "eps chi^2")
    ns = KD.nullspace_dicts(lev, n_w + len(srcs), p)
    S = len(srcs)
    C = np.array([[int(z) % p for z in v[n_w:]] for v in ns], dtype=np.int64).reshape(-1, S)
    V = rref_np(C, p)[0] if C.shape[0] else np.zeros((0, S), np.int64)
    print(f"  one system: {S} (product, deformation) columns, dim V = {V.shape[0]} [{time.time()-t0:.0f}s]",
          flush=True)
    col = lambda j, a: j * A + a

    def survivors(w):
        U = np.zeros((Kc, S), dtype=np.int64)
        for j in range(Kc):
            for a in range(A):
                U[j, col(j, a)] = w[a]
        ker = kernel_np(np.concatenate([U, V]).T, Kc + V.shape[0], p)
        G = rref_np(ker[:, :Kc], p)[0] if ker.shape[0] else np.zeros((0, Kc), np.int64)
        if G.shape[0] == 0:
            return 0, {}
        r = [rank_np(G[:, lp >= m], int((lp >= m).sum()), p) if (lp >= m).any() else 0 for m in range(qmax + 2)]
        return G.shape[0], {m: r[m] - r[m + 1] for m in range(qmax + 1)}

    def space_for(gamma):
        Ug = np.zeros((A, S), dtype=np.int64)
        for a in range(A):
            for j in range(Kc):
                Ug[a, col(j, a)] = gamma[j]
        I = intersect_np(V, Ug, S, p)
        sol = []
        for r in I:
            M = np.concatenate([Ug.T, (-r[:, None]) % p], axis=1)
            kk = [v for v in kernel_np(M, A + 1, p) if v[-1] % p]
            sol.append((kk[0][:A] * pow(int(kk[0][-1]), p - 2, p)) % p)
        return rref_np(np.array(sol), p)[0] if sol else np.zeros((0, A), np.int64)

    slot_idx = [a for a in range(A) if roles[a] == "slot"]
    ns_ = len(slot_idx)

    def on_slots(W):
        E = np.zeros((ns_, A), dtype=np.int64)
        for r_, a in enumerate(slot_idx):
            E[r_, a] = 1
        I = intersect_np(W, E, A, p)
        return I[:, slot_idx] if I.shape[0] else np.zeros((0, ns_), np.int64)

    Wall = None
    for j in range(Kc):
        e = np.zeros(Kc, dtype=np.int64); e[j] = 1
        Wj = space_for(e)
        Wall = Wj if Wall is None else intersect_np(Wall, Wj, A, p)
    def exps(name):
        out = {}
        for tok in name.split():
            base, _, e_ = tok.partition("^")
            out[base] = int(e_) if e_ else 1
        return out

    # rung m: the product H^(qmax-m) L^(2m) -- the first product carrying Q^m that a Carter with a pole
    # of order m-1 lets through (a pure Q^m is not a rank-r product below the top rung)
    Wq = {}
    for m in range(1, qmax + 1):
        want = {"Lsq": m, **({"H": qmax - m} if qmax > m else {})}
        idx = [i for i, n in enumerate(pnames) if exps(n) == want]
        if len(idx) != 1:
            sys.exit(f"could not find the product H^{qmax-m} Lsq^{m} among {pnames}")
        e = np.zeros(Kc, dtype=np.int64); e[idx[0]] = 1
        Wq[m] = on_slots(space_for(e))
    Walls = on_slots(Wall)
    print(f"\n  shape-sector deformations keeping ALL {Kc}: dim {Walls.shape[0]} of {ns_}")
    for m in range(1, qmax + 1):
        print(f"  shape-sector deformations keeping H^{qmax-m} Q^{m} (pole order <= {m-1}): dim {Wq[m].shape[0]}",
              flush=True)

    # new directions at each rung, and their breakdowns
    base = Walls
    for m in range(2, qmax + 1):
        new = []
        for r in Wq[m]:
            if rank_np(np.concatenate([base, r[None, :]]), ns_, p) > base.shape[0]:
                new.append(r)
                base = rref_np(np.concatenate([base, r[None, :]]), p)[0]
        print(f"\n  directions first appearing with Q^{m} (pole order {m-1}): {len(new)}")
        for r in new:
            w = np.zeros(A, dtype=np.int64); w[slot_idx] = r
            terms = []
            for i, c in enumerate(r):
                if c:
                    q = ratrec(int(c), p)
                    terms.append((f"{q[0]}/{q[1]}" if q and q[1] != 1 else str(q[0] if q else c))
                                 + "*" + names[slot_idx[i]])
            print(f"    {' + '.join(terms)}\n      survivors {survivors(w)}", flush=True)

    print("\n  named directions (§140, §141):")
    known = {"d1": {"l2rr_3": 1, "l2ang_3": 1, "l2ang_4": "3/2"},
             "d2": {"l2rr_4": 1, "l2ang_3": "-10/21", "l2ang_4": "-5/14", "l2ang_5": "4/7"},
             "d3": {"l2rr_5": 1, "l2ang_3": "100/609", "l2ang_4": "25/203", "l2ang_5": "321/2030",
                    "l2ang_6": "103/174"}}
    for lab, coef in known.items():
        if any(nm not in names for nm in coef):        # e.g. the l=2 directions in an l=4 run
            continue
        w = np.zeros(A, dtype=np.int64)
        for nm, c in coef.items():
            q = sp.Rational(c); w[names.index(nm)] = int(q.p) % p * pow(int(q.q) % p, p - 2, p) % p
        print(f"    {lab}: {survivors(w)}", flush=True)
    for a in range(A):
        if roles[a] == "control":
            w = np.zeros(A, dtype=np.int64); w[a] = 1
            print(f"    control {names[a]}: {survivors(w)}", flush=True)
    rng = np.random.default_rng(8)
    for t in range(3):
        w = np.zeros(A, dtype=np.int64); w[slot_idx] = rng.integers(1, p, ns_)
        print(f"    random #{t}: {survivors(w)}", flush=True)
    if "--save" in sys.argv:
        np.savez(arg("--save", None, str), V=V, lp=lp, names=np.array(names), roles=np.array(roles),
                 pnames=np.array(pnames))
    print(f"\n  total {time.time()-t0:.0f}s")
