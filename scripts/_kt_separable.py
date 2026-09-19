#!/usr/bin/env python3
"""Is "keeps Carter" the same as "stays separable"?  (§139)

Johannsen (PRD 88, 044002; arXiv:1501.02809, Eq. 10-11) writes the most general Kerr-like CONTRAVARIANT
metric whose Hamilton-Jacobi equation stays separable, with eight free functions:

    g^ab d_a d_b = -1/(Delta St) [ (r^2+a^2) A1(r) d_t + a A2(r) d_phi ]^2
                   + 1/(St sin^2) [ A3(th) d_phi + a sin^2 A4(th) d_t ]^2
                   + Delta/St A5(r) d_r^2 + 1/St A6(th) d_th^2,      St = Sigma + f(r) + g(th).

Every member keeps a Carter constant EXACTLY (St * H splits into an r-part plus a theta-part). This
script: (1) checks the transcription -- all functions trivial must give our Kerr pieces exactly, and
the r/theta split must hold for arbitrary symbolic functions; (2) runs every linearized separable
deformation through the Carter-compatibility machinery of _kt_carter_space -- ALL must pass, a test
the map can fail; (3) compares, as metric perturbations, the Carter-compatible slot deformations of
§139 with separable + pure-gauge ones.
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
from _kt_anatomy import chi_pieces, lie_inverse  # noqa: E402
from _kt_carter_space import (arg, matmul_mod, build_space, compatible_space, rank_np, rref_np,  # noqa: E402
                              representable_only, setup, intersect_np)

x, y = sp.symbols("x y", real=True)
chi = KD.chi


def johannsen_ginv(A1, A2, A3, A4, A5, A6, f, g, a):
    """Eq. (10)-(11) in (t, x = r, y = cos th, phi), M = 1: (d_th)^2 = (1 - y^2) (d_y)^2."""
    Delta = x ** 2 - 2 * x + a ** 2
    St = x ** 2 + a ** 2 * y ** 2 + f + g
    s2 = 1 - y ** 2
    gi = sp.zeros(4, 4)
    P, Q = (x ** 2 + a ** 2) * A1, a * A2                  # -(P d_t + Q d_phi)^2 / (Delta St)
    gi[0, 0] += -P ** 2 / (Delta * St)
    gi[0, 3] += -P * Q / (Delta * St)
    gi[3, 3] += -Q ** 2 / (Delta * St)
    U, V = A3, a * s2 * A4                                 # (U d_phi + V d_t)^2 / (St s2)
    gi[3, 3] += U ** 2 / (St * s2)
    gi[0, 3] += U * V / (St * s2)
    gi[0, 0] += V ** 2 / (St * s2)
    gi[3, 0] = gi[0, 3]
    gi[1, 1] = Delta * A5 / St
    gi[2, 2] = s2 * A6 / St
    return gi


def transcription_checks(GI):
    ok = True
    kerr = chi_pieces(johannsen_ginv(1, 1, 1, 1, 1, 1, 0, 0, chi))
    same = all(sp.cancel(kerr[n][i, j] - GI[n][i, j]) == 0 for n in range(3) for i in range(4) for j in range(4))
    print(f"  (1a) trivial functions reproduce our Kerr pieces through chi^2: {same}", flush=True)
    ok &= same
    Fr = [sp.Function(nm)(x) for nm in ("A1", "A2", "A5", "f")]
    Fy = [sp.Function(nm)(y) for nm in ("A3", "A4", "A6", "g")]
    a = sp.Symbol("a")
    gi = johannsen_ginv(Fr[0], Fr[1], Fy[0], Fy[1], Fr[2], Fy[2], Fr[3], Fy[3], a)
    St = x ** 2 + a ** 2 * y ** 2 + Fr[3] + Fy[3]
    Hs = sp.Rational(1, 2) * St * sum(gi[i, j] * K.MOM[i] * K.MOM[j] for i in range(4) for j in range(4))
    split = sp.simplify(sp.diff(sp.together(Hs), x, y)) == 0
    print(f"  (1b) St*H splits into r-part + theta-part for ARBITRARY functions: {split}", flush=True)
    ok &= split
    return ok


def radial_profiles(kmax, jmax, shift=0):
    """x^(shift-k) (x-2)^-j: pure powers (j = 0) and the horizon factors a 1/f = x/(x-2) brings in."""
    return [x ** (shift - k) * (x - 2) ** -j for j in range(jmax + 1) for k in range(1, kmax + 1)]


def separable_pieces(kmax, jmax=0):
    """Linearized separable deformations: each free function nudged by eps * profile * chi^n."""
    names, gis = [], []
    base = dict(A1=1, A2=1, A3=1, A4=1, A5=1, A6=1, f=0, g=0)
    eps = sp.Symbol("eps")
    radial = {"A1": radial_profiles(kmax, jmax), "A2": radial_profiles(kmax, jmax),
              "A5": radial_profiles(kmax, jmax), "f": radial_profiles(kmax, jmax, shift=2)}
    angular = {nm: [sp.Integer(1), y ** 2] for nm in ("A3", "A4", "A6", "g")}
    for fam in (radial, angular):
        for nm, profiles in fam.items():
            for i, prof in enumerate(profiles):
                for n in range(3):
                    args = dict(base)
                    args[nm] = base[nm] + eps * prof * chi ** n
                    gi = johannsen_ginv(args["A1"], args["A2"], args["A3"], args["A4"], args["A5"],
                                        args["A6"], args["f"], args["g"], chi)
                    d = gi.applyfunc(lambda e: sp.diff(e, eps).subs(eps, 0))
                    pcs = chi_pieces(d)
                    if all(M == sp.zeros(4, 4) for M in pcs):
                        continue
                    names.append(f"sep_{nm}_{i}_chi{n}")
                    gis.append(pcs)
    return names, gis


def general_separable_pieces(kmax, jmax=0):
    """Linearized deformations of the GENERAL separable (Carter / Benenti-Francaviglia) class:

        St g^ab = [A_tt(r), A_tphi(r), A_phiphi(r) on the (t,phi) block; A_rr(r) d_r^2]
                + [B_tt(th), B_tphi(th), B_phiphi(th) on the (t,phi) block; B_thth(th) d_th^2],
        St = R(r) + Theta(th).

    Johannsen's Eq. (10) is the subfamily whose radial (t,phi) block is a perfect square; the general
    class lets it be any symmetric matrix. Kerr: R = r^2, Theta = a^2 cos^2, radial block
    -[(r^2+a^2) d_t + a d_phi]^2 / Delta + Delta d_r^2, angular [d_phi + a sin^2 d_t]^2/sin^2 + d_th^2."""
    a = chi
    s2 = 1 - y ** 2
    Delta = x ** 2 - 2 * x + a ** 2
    Rk, Thk = x ** 2, a ** 2 * y ** 2
    Pr = [[-((x ** 2 + a ** 2) ** 2) / Delta, 0, 0, -(x ** 2 + a ** 2) * a / Delta],
          [0, Delta, 0, 0], [0, 0, 0, 0],
          [-(x ** 2 + a ** 2) * a / Delta, 0, 0, -a ** 2 / Delta]]
    Pt = [[a ** 2 * s2, 0, 0, a], [0, 0, 0, 0], [0, 0, s2, 0], [a, 0, 0, 1 / s2]]   # (d_th)^2 -> s2 (d_y)^2
    St = Rk + Thk
    rprofs = [x ** (2 - k) * (x - 2) ** -j for j in range(jmax + 1) for k in range(0, kmax + 3)]
    aprofs = [sp.Integer(1), y ** 2, y ** 4]
    slots_r = {"R": None, "Att": (0, 0), "Atp": (0, 3), "App": (3, 3), "Arr": (1, 1)}
    slots_t = {"Th": None, "Btt": (0, 0), "Btp": (0, 3), "Bpp": (3, 3), "Byy": (2, 2)}
    names, gis = [], []
    for slots, profs, tag in ((slots_r, rprofs, "r"), (slots_t, aprofs, "t")):
        for nm, idx in slots.items():
            for i, prof in enumerate(profs):
                for n in range(3):
                    d = prof * chi ** n
                    dg = sp.zeros(4, 4)
                    if idx is None:                      # St -> St + d: every entry scales by -d/St
                        for u in range(4):
                            for v in range(4):
                                dg[u, v] = -(Pr[u][v] + Pt[u][v]) * d / St ** 2
                    else:
                        u, v = idx
                        dg[u, v] = d / St
                        dg[v, u] = d / St
                    pcs = chi_pieces(dg)
                    if all(M == sp.zeros(4, 4) for M in pcs):
                        continue
                    names.append(f"gsep_{nm}_{i}_chi{n}")
                    gis.append(pcs)
    return names, gis


def gauge_pieces(GI, kmax, jmax=0):
    """Pure coordinate changes that keep stationarity, axisymmetry and the reflection y -> -y."""
    giK = sum((chi ** n * GI[n] for n in range(3)), sp.zeros(4, 4))
    names, gis = [], []
    profs = [sp.Integer(1)] + radial_profiles(kmax + 1, jmax)
    for i, prof in enumerate(profs):
        for n in range(3):
            # radial with l=0 AND l=2 angular pattern: the l=2 one generates shape (Y2) deformations,
            # and leaving it out made separable + gauge look narrower than it is (2026-09-19)
            for nm, xi in ((f"gauge_r_{i}_chi{n}", [0, chi ** n * prof, 0, 0]),
                           (f"gauge_rY2_{i}_chi{n}", [0, chi ** n * (3 * y ** 2 - 1) * prof, 0, 0]),
                           (f"gauge_y_{i}_chi{n}", [0, 0, chi ** n * y * (1 - y ** 2) * prof, 0])):
                names.append(nm)
                gis.append(chi_pieces(lie_inverse(giK, xi)))
    return names, gis


def vectorize(gis_list, p):
    """Each deformation -> coefficient vector of its cleared chi^0..chi^2 Hamiltonian pieces."""
    Hs = [[KD.hamiltonian(g) for g in gi] for gi in gis_list]
    Dn = [sp.Integer(1)] * 3
    for hs in Hs:
        for n in range(3):
            if hs[n] != 0:
                Dn[n] = sp.lcm(Dn[n], sp.denom(sp.together(hs[n])))
    keys, rows = {}, []
    for hs in Hs:
        row = {}
        for n in range(3):
            if hs[n] != 0:
                for kk, v in PB.clear(sp.together(hs[n]), Dn[n], p).items():
                    row[(n, kk)] = v
        rows.append(row)
        for kk in row:
            keys.setdefault(kk, len(keys))
    M = np.zeros((len(rows), len(keys)), dtype=np.int64)
    for i, row in enumerate(rows):
        for kk, v in row.items():
            M[i, keys[kk]] = v
    return M


if __name__ == "__main__":
    kmax = arg("--kmax", 6)
    ctx = setup(arg("--rank", 2), arg("--denpow", 6), arg("--margin", 6), arg("--prime", 0))
    p, t0, GI = ctx["p"], ctx["t0"], ctx["GI"]
    print("(1) transcription of Johannsen Eq. (10)-(11)", flush=True)
    if not transcription_checks(GI):
        sys.exit("transcription check FAILED -- do not interpret anything below")

    jmax = arg("--jmax", 0)
    snames, sgis = (general_separable_pieces(kmax, jmax) if "--general" in sys.argv
                    else separable_pieces(kmax, jmax))
    snames, sgis, _ = representable_only(ctx, snames, sgis, ["sep"] * len(snames))
    if "--span-only" not in sys.argv:
        print("\n(2) every separable deformation must keep Carter", flush=True)
        Wsep = compatible_space(ctx, snames, sgis)
        print(f"  separable deformations: {len(snames)}; Carter-compatible: {Wsep.shape[0]} of {len(snames)}"
              f"  -> {'ALL, as they must' if Wsep.shape[0] == len(snames) else 'NOT ALL -- the map or the transcription is wrong'}",
              flush=True)

    print(f"\n(3) are the Carter-compatible slot deformations exactly separable + gauge? "
          f"(separable/gauge profiles x^-k (x-2)^-j, j <= {jmax})", flush=True)
    names, gis, roles = representable_only(ctx, *build_space(GI, kmax))
    slot_idx = [a for a in range(len(names)) if roles[a] == "slot"]
    cache = f"data/anat/compat_slots_r{ctx['rank']}_k{kmax}.npy"
    if os.path.exists(cache):
        Ws = np.load(cache)
        print(f"  compatible slot space loaded from {cache} (dim {Ws.shape[0]})", flush=True)
    else:
        W = compatible_space(ctx, names, gis)
        Es = np.zeros((len(slot_idx), len(names)), dtype=np.int64)
        for i, a in enumerate(slot_idx):
            Es[i, a] = 1
        Ws = intersect_np(W, Es, len(names), p)[:, slot_idx]
        np.save(cache, Ws)
    gnames, ggis = gauge_pieces(GI, kmax, jmax)
    gnames, ggis, _ = representable_only(ctx, gnames, ggis, ["gauge"] * len(gnames))
    allv = vectorize(sgis + ggis + [gis[a] for a in slot_idx], p)
    ns, ng = len(sgis), len(ggis)
    SG = allv[:ns + ng]
    SL = allv[ns + ng:]
    compat = matmul_mod(Ws, SL, p) if Ws.shape[0] else np.zeros((0, allv.shape[1]), np.int64)
    ncols = allv.shape[1]
    r_sg = rank_np(SG, ncols, p)
    r_all = rank_np(np.concatenate([SG, SL]), ncols, p)
    r_cmp = rank_np(np.concatenate([SG, compat]), ncols, p)
    r_slots = rank_np(SL, ncols, p)
    r_both = rank_np(SL, ncols, p) + r_sg - r_all       # dim(span(slots) ∩ span(sep + gauge))
    print(f"  separable + gauge span: rank {r_sg}")
    print(f"  slot deformations: rank {r_slots}; of which inside separable + gauge: {r_both}")
    print(f"  Carter-compatible slot deformations: {Ws.shape[0]}; adding them to separable + gauge "
          f"raises the rank by {r_cmp - r_sg}")
    if r_cmp == r_sg:
        print("  => every Carter-compatible slot deformation IS separable + gauge "
              f"({'non-vacuous: ' + str(r_slots - r_both) + ' slot directions are not' if r_slots > r_both else 'VACUOUS: all slots are'})")
    else:
        print(f"  => {r_cmp - r_sg} Carter-compatible direction(s) are NOT separable + gauge within this basis")
    print(f"\n  total {time.time()-t0:.0f}s")
