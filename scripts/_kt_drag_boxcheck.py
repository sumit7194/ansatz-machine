#!/usr/bin/env python3
"""Is drag3's "chains do not extend" the PHYSICS or the BOX?  (§146 follow-up)

THE FINDING UNDER TEST.  Running the physical odd-parity slots through _kt_qpower at rank 4, margin 6:

    drag1 (axial l = 1):  every chain extends at eps chi^0 and eps chi^1
    drag3 (axial l = 3):  all six profiles set aside at eps chi^1 -- chains
                          [3, 4, 6, 7, 9, 10, 11, 12, 13] do not extend

"Does not extend" means the inhomogeneous equation {H0, F} = -source has NO particular solution
INSIDE THE ANSATZ.  That is a null, and a null is worth nothing until the search space is shown to
contain the answer (D40).  drag1 extending in the same box is suggestive but not decisive: A_3 carries
two more powers of y than A_1, so drag3 could simply need a wider box.

WHY THIS SCRIPT RATHER THAN --margin 8.  _kt_qpower keys its cached Kerr chi-tower on the box, so a
wider margin demands a fresh multi-hour chain build.  But the chains are Kerr's OWN objects -- lists
of coefficient expressions, not box-relative vectors -- and the margin-6 run reports all 14, which is
the complete rank-4 set ({0:9, 1:4, 2:1} = 14), so none is missing.  So the honest minimal control is
to hold the chains fixed and widen ONLY the space the particular solution is sought in.

READING IT.  If the failing chains start extending as the box grows, the original finding was an
ansatz artifact and must be withdrawn.  If they still fail at every width, the obstruction is real:
the odd l = 3 deformation cannot extend those Kerr chains at first order in eps and chi, and the
tower breaks one chi order BELOW where the pole-order test looks.

Usage: _kt_drag_boxcheck.py [--slots drag3] [--margins 6,8,10] [--rank 4] [--denpow 7] [--chainmargin 6]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
import _kt_exact as EX  # noqa: E402
import _kt_metrics as MM  # noqa: E402
import _kt_perturb as PB  # noqa: E402
import _kt_search as K  # noqa: E402
from _kt_carter_space import arg, build_space, load  # noqa: E402
from _kt_opfast import operator_from_templates  # noqa: E402

x, y = sp.symbols("x y", real=True)


def run(rank_, denpow, margin, chains, slots, kmax, p):
    """Levels eps chi^0 and eps chi^1 for one solution-box width.  Returns {slot: failing chains}."""
    GI = KD.kerr_chi_pieces()
    L, _, _ = MM.denominator(GI[0])
    den = L ** denpow
    _, prods, _ = EX.generators(GI[0], rank_, den)
    bx, by = EX.reducible_box(prods, den)
    dx, dy = bx + margin, by + margin
    mons = K.monomials(rank_)
    cols, _ = PB.coefficient_basis(mons, dx, dy, den)
    n_w = len(cols)
    H = [KD.hamiltonian(GI[n]) for n in range(3)]
    dicts0, D = operator_from_templates(H[0], mons, dx, dy, den, p)
    op = KD._OpArrays(dicts0, p)

    names, gis, roles = build_space(GI, kmax)
    keep = [i for i, (nm, r) in enumerate(zip(names, roles))
            if r == "slot" and nm.rsplit("_", 1)[0] in slots]
    if not keep:
        sys.exit(f"--slots named nothing among the built slots: {slots}")
    names, gis = [names[i] for i in keep], [gis[i] for i in keep]
    # representability of the DEFORMATION in this box, reported separately from chain extension:
    # a slot outside the ansatz would fail to extend for a reason that has nothing to do with physics
    bad = {nm: [n for n in range(3) if PB.check_perturbation_representable(g[n], dx, dy, den)]
           for nm, g in zip(names, gis)}
    for nm, b in bad.items():
        if b:
            print(f"    WARNING {nm} is outside the ansatz at chi^{b} in this box", flush=True)
    HS = [[KD.hamiltonian(g) for g in gi] for gi in gis]
    A = len(names)

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

    F1, failing = {}, {}
    alive = list(range(A))
    for n in (0, 1):
        srcs, keys = [], []
        for k, ch in enumerate(chains):
            for a in alive:
                acc = sp.Integer(0)
                for j in range(1, n + 1):
                    acc += br(F1.get((k, a, n - j)), H[j])
                for j in range(0, n + 1):
                    acc += br(ch[n - j], HS[a][j])
                srcs.append(acc)
                keys.append((k, a))
        lev = KD._prep_level(srcs, D, op, None, p, f"eps chi^{n}")
        ns = KD.nullspace_dicts(lev, n_w + len(srcs), p)
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
        for j, key in enumerate(keys):
            if key[1] not in failed:
                F1[(key[0], key[1], n)] = vec_to_co(part[j][:n_w])
        for a, ks in failed.items():
            failing.setdefault(names[a], []).append((n, ks))
        alive = [a for a in alive if a not in failed]
    return dx, dy, n_w, {nm: failing.get(nm, []) for nm in names}


if __name__ == "__main__":
    t0 = time.time()
    rank_, denpow = arg("--rank", 4), arg("--denpow", 7)
    chainmargin, kmax = arg("--chainmargin", 6), arg("--kmax", 6)
    slots = arg("--slots", "drag3", str).split(",")
    margins = [int(m) for m in arg("--margins", "6,8,10", str).split(",")]
    p = KD.PRIMES[arg("--prime", 0)]

    t_, ph = sp.symbols("t phi", real=True)
    K.set_dim((t_, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    GI = KD.kerr_chi_pieces()
    L, _, _ = MM.denominator(GI[0])
    _, prods, _ = EX.generators(GI[0], rank_, L ** denpow)
    bx, by = EX.reducible_box(prods, L ** denpow)
    cdx, cdy = bx + chainmargin, by + chainmargin
    pfx = "" if p == KD.PRIMES[0] else f"_p{KD.PRIMES.index(p)}"
    ckf = f"data/kt_double_chains_r{rank_}_d{denpow}_b{cdx}x{cdy}{pfx}.pkl"
    chains = [[[sp.sympify(e) for e in lvl] for lvl in ch] for ch in load(ckf)["chains"]]
    print(f"chains: {len(chains)} from {ckf} (held FIXED across box widths)", flush=True)
    print(f"slots {slots}, solution-box margins {margins}, prime {p}\n", flush=True)

    table = {}
    for m in margins:
        dx, dy, n_w, fail = run(rank_, denpow, m, chains, slots, kmax, p)
        table[m] = fail
        print(f"  margin {m:2d}  box {dx}x{dy}  {n_w} unknowns  [{time.time()-t0:.0f}s]", flush=True)
        for nm in sorted(fail):
            if not fail[nm]:
                print(f"      {nm:10s} every chain extends at eps chi^0 and eps chi^1")
            else:
                for n, ks in fail[nm]:
                    print(f"      {nm:10s} eps chi^{n}: chains {ks} DO NOT EXTEND")
        print(flush=True)

    print("VERDICT")
    per = {m: sum(len(ks) for v in table[m].values() for _, ks in v) for m in margins}
    print(f"  total failing (slot, chain) pairs by margin: {per}")
    if len(set(per.values())) == 1 and list(per.values())[0] > 0:
        print("  UNCHANGED as the box grows -> the obstruction is REAL, not an ansatz artifact")
    elif list(per.values())[-1] == 0:
        print("  FAILURES VANISH in the wider box -> the original finding was an ARTIFACT; withdraw it")
    else:
        print("  failures CHANGE with box width -> not yet converged; widen further before claiming")
