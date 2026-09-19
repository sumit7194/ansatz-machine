#!/usr/bin/env python3
"""Where does the source-clearing time go?  (measurement before any FLINT work)

After the operator templates and the rescale, the dominant cost left in a level is PB.clear() on the
level's SOURCE expressions: at rank 3, zeta chi^2, 210 s of a 346 s run went to clearing 8 sources.
This rebuilds exactly those sources from the zeta chi^1 checkpoint and times each phase of clear():

    together(sum) -> fraction -> cancel(D2/dd) -> expand(num*q) -> Poly in momenta -> Poly in x,y

It changes nothing; it only reports. Checkpoints are read through _kt_ckcompare.load, which refuses
every class lookup. Usage:  _kt_srcprof.py [--rank 3 --denpow 6 --margin 6]
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
from _kt_ckcompare import load  # noqa: E402
from _kt_opfast import operator_from_templates  # noqa: E402

x, y = sp.symbols("x y", real=True)


def arg(fl, d, c=int):
    return c(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else d


def phases(tog, D, p):
    """clear(tog, D, p), phase by phase. Returns (dict, {phase: seconds})."""
    t = {}
    s = time.time(); num, dd = sp.fraction(sp.together(tog)); t["together+fraction"] = time.time() - s
    s = time.time(); q = sp.cancel(D / dd); t["cancel D/dd"] = time.time() - s
    s = time.time(); cl = sp.expand(num * q); t["expand num*q"] = time.time() - s
    s = time.time(); poly = sp.Poly(sp.expand(cl), *K.MOM); t["Poly(momenta)"] = time.time() - s
    s = time.time()
    out = {}
    for e, co in zip(poly.monoms(), poly.coeffs()):
        pp = sp.Poly(sp.expand(co), x, y)
        for jk, c2 in zip(pp.monoms(), pp.coeffs()):
            r = int(c2) % p
            if r:
                out[(e, jk)] = r
    t["Poly(x,y) per coeff"] = time.time() - s
    return out, t


def build_sources(rank=3, denpow=6, margin=6, n=2):
    """The zeta chi^n sources of a level exactly as _kt_double builds them, and their D2."""
    p = KD.PRIMES[0]
    t, ph = sp.symbols("t phi", real=True)
    K.set_dim((t, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    GI = KD.kerr_chi_pieces()
    L, _, _ = MM.denominator(GI[0])
    den = L ** denpow
    _, prods, _ = EX.generators(GI[0], rank, den)
    bx, by = EX.reducible_box(prods, den)
    dx, dy = bx + margin, by + margin
    mons = K.monomials(rank)
    H = [KD.hamiltonian(GI[n]) for n in range(3)]
    HS = [KD.hamiltonian(M) for M in KD.sgb_ginv_pieces(GI)]
    _, D = operator_from_templates(H[0], mons, dx, dy, den, p)

    data = load(f"data/kt_double_z_r{rank}_d{denpow}_n{n - 1}.pkl")
    chains = [[[sp.sympify(e) for e in lvl] for lvl in ch] for ch in data["chains"]]
    zchains = [[[sp.sympify(e) for e in lvl] for lvl in ch] for ch in data["zchains"]]
    s = time.time()
    srcs, pieces = [], []
    for k, ch in enumerate(chains):
        acc, pk = sp.Integer(0), []
        for j in range(1, n + 1):
            if n - j < len(zchains[k]):
                tg, _ = PB.bracket_raw_coeffs(zchains[k][n - j], H[j], mons)
                acc += tg; pk.append(tg)
        for j in range(0, n + 1):
            if n - j < len(ch):
                tg, _ = PB.bracket_raw_coeffs(ch[n - j], HS[j], mons)
                acc += tg; pk.append(tg)
        srcs.append(acc); pieces.append(pk)
    print(f"rank {rank}: {len(srcs)} zeta chi^2 sources, {sum(map(len, pieces))} bracket pieces, "
          f"brackets {time.time() - s:.1f}s", flush=True)

    s = time.time()
    D2 = D
    for e in srcs:
        D2 = sp.lcm(D2, sp.denom(sp.together(e)))
    print(f"  lcm over sources: {time.time() - s:.1f}s   D2/D = {sp.factor(sp.cancel(D2 / D))}",
          flush=True)
    return srcs, pieces, D2, p


if __name__ == "__main__":
    srcs, pieces, D2, p = build_sources(arg("--rank", 3), arg("--denpow", 6), arg("--margin", 6))
    tot = {}
    for i, e in enumerate(srcs[:3]):
        _, ti = phases(e, D2, p)
        print(f"  source {i}: " + "  ".join(f"{k} {v:.1f}s" for k, v in ti.items()), flush=True)
        for k, v in ti.items():
            tot[k] = tot.get(k, 0) + v
    print("  total over 3 sources: " + "  ".join(f"{k} {v:.1f}s" for k, v in tot.items()))
