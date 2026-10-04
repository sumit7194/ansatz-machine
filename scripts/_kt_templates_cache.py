#!/usr/bin/env python3
"""Compute the D49 operator templates ONCE, exactly over Z, and cache them reduced mod each prime.

WHY. On TS the three SymPy template brackets per momentum monomial dominate the build (rank 2: 225 s for 30
templates; rank 6 has 252). Every sector process and both primes need the same templates, so they are computed once
as EXACT integer polynomials (the same arithmetic as _kt_perturb.clear, minus the final `% p`) and stored reduced mod
each prime as plain integer arrays (.npz, numpy's default safe loader). Loading is seconds.

EQUALITY, NOT AGREEMENT: `--selftest` checks the cached mod-p templates equal _kt_opfast.templates(...) dict for dict
on two small cases, for both primes, and that the common denominator D is identical.

    .venv/bin/python scripts/_kt_templates_cache.py --metric ts2:4/5 --rank 6 --denpow 3 --out data/ts2_exact/r6/templates
    .venv/bin/python scripts/_kt_templates_cache.py --selftest
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
import _kt_metrics as MM  # noqa: E402
import _kt_perturb as PB  # noqa: E402
import _kt_search as K  # noqa: E402

x, y = MM.x, MM.y
SREPR = {n: getattr(sp, n) for n in ("Add", "Mul", "Pow", "Integer", "Rational", "Symbol")}


def clear_int(tog, D):
    """_kt_perturb.clear without the final reduction: {(momentum exps, (j, k)): exact integer}."""
    num, dd = sp.fraction(sp.together(tog))
    q = sp.cancel(D / dd)
    if sp.denom(q) != 1:
        raise ValueError("the common denominator does not clear this bracket")
    R = PB._ring()
    Pq = R.from_expr(num) * R.from_expr(q)
    out = {}
    for m, c in Pq.items():
        if c.denominator != 1:
            raise ValueError(f"non-integer coefficient {c} after clearing")
        if c.numerator:
            out[(m[2:], m[:2])] = int(c.numerator)
    return out


def templates_exact(H0, mons, den):
    specs = []
    for mi in range(len(mons)):
        for (a, b) in ((0, 0), (1, 0), (0, 1)):
            F = [sp.Integer(0)] * len(mons)
            F[mi] = x**a * y**b / den
            specs.append((H0, F))
    raws, dens = PB.build_columns(specs, mons, False)
    D = sp.Integer(1)
    for d_ in dens:
        D = sp.lcm(D, d_)
    return D, [clear_int(r, D) for r in raws]


def save(path_stem, D, cl_int, primes):
    eids = sorted({e for d in cl_int for (e, _) in d})
    eid = {e: i for i, e in enumerate(eids)}
    for pi, p in enumerate(primes):
        off, E, J, Kk, V = [0], [], [], [], []
        for d in cl_int:
            for (e, (j, k)), v in d.items():
                r = v % p
                if r:
                    E.append(eid[e]); J.append(j); Kk.append(k); V.append(r)
            off.append(len(V))
        np.savez_compressed(f"{path_stem}_p{pi}.npz", off=np.array(off, np.int64), e=np.array(E, np.int32),
                            j=np.array(J, np.int32), k=np.array(Kk, np.int32), v=np.array(V, np.int64),
                            eids=np.array(eids, np.int32).reshape(len(eids), -1))
        with open(f"{path_stem}_D.txt", "w") as fh:
            fh.write(sp.srepr(D))


def load(path_stem, prime_index):
    z = np.load(f"{path_stem}_p{prime_index}.npz")
    eids = [tuple(int(t) for t in row) for row in z["eids"]]
    off, E, J, Kk, V = z["off"], z["e"], z["j"], z["k"], z["v"]
    cl = []
    for t in range(len(off) - 1):
        a, b = off[t], off[t + 1]
        cl.append({(eids[E[i]], (int(J[i]), int(Kk[i]))): int(V[i]) for i in range(a, b)})
    D = sp.sympify(open(f"{path_stem}_D.txt").read(), locals=SREPR)
    return D, cl


def setup(spec, rank, denpow):
    from _kt_exact_op import get_metric
    t_, ph = sp.symbols("t phi", real=True)
    K.set_dim((t_, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    ginv, name = get_metric(spec)
    L, _, _ = MM.denominator(ginv)
    return KD.hamiltonian(ginv), K.monomials(rank), L ** denpow, name


def main():
    def arg(fl, d=None, c=str):
        return c(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else d
    if "--selftest" in sys.argv:
        from _kt_opfast import templates
        import tempfile
        ok = True
        for spec, rank, denpow in (("ts2kerr:4/5", 3, 1), ("ts2:4/5", 2, 1)):
            t0 = time.time()
            H, mons, den, name = setup(spec, rank, denpow)
            D, cli = templates_exact(H, mons, den)
            with tempfile.TemporaryDirectory() as d:
                save(os.path.join(d, "t"), D, cli, KD.PRIMES)
                for pi, p in enumerate(KD.PRIMES):
                    Dl, cl = load(os.path.join(d, "t"), pi)
                    Dr, ref = templates(H, mons, den, p)
                    same = (sp.simplify(Dl - Dr) == 0) and len(cl) == len(ref) and all(a == b for a, b in zip(cl, ref))
                    ok &= same
                    print(f"  {name} r{rank} prime {pi}: cached == _kt_opfast.templates: {same} "
                          f"({len(cl)} templates) [{time.time()-t0:.0f}s]", flush=True)
        print("SELFTEST " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    spec, rank, denpow, out = arg("--metric"), arg("--rank", 2, int), arg("--denpow", 1, int), arg("--out")
    t0 = time.time()
    H, mons, den, name = setup(spec, rank, denpow)
    D, cli = templates_exact(H, mons, den)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    save(out, D, cli, KD.PRIMES)
    import json
    json.dump({"metric": spec, "rank": rank, "denpow": denpow, "templates": len(cli)}, open(f"{out}_meta.json", "w"))
    print(f"{name} rank {rank} den^{denpow}: {len(cli)} exact templates, {sum(len(d) for d in cli):,} terms, cached "
          f"mod both primes at {out}_p{{0,1}}.npz [{time.time()-t0:.0f}s]", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
