#!/usr/bin/env python3
"""SAMPLED dense rank: a global, ansatz-bounded upper bound on the Killing-tensor count, one parity sector at a time.

The ansatz is that of _kt_exact_op / _kt_exact_sector: F = sum_j c_j w_j, with w_j = m(p) x^a y^b / L^d over the box
(reducible box + margin) and the parity sector. Instead of expanding the cleared operator symbolically (templates,
185M nonzeros at rank 6), {H, w_j} is computed exactly mod p at random points (x0, y0, p_t, p_x, p_y, p_phi), one
dense row per point:

    {H, w} = x^a y^b L^-d [ sum_q H_q dm/dp_q - m H_px (a/x - d L_x/L) - m H_py (b/y - d L_y/L) ]

where H_q = dH/dq and H_pq = dH/dp_q = g^qq p_q. The row is scaled by L^d, a nonzero residue, and points where any
denominator vanishes are skipped. Each row is a linear functional of the true coefficient rows, so
rank(sampled) <= rank_p(true) <= rank_Q(true). The sampled nullity is an UPPER bound on the true one, and sampled =
reducible count PROVES the null. Over-sampled by `--extra` rows. Rank by rust/ktdense (u32 in place) or FLINT.
`--plant` duplicates one column (a planted kernel vector): the nullity must rise by exactly one (a sabotage check).

    .venv/bin/python scripts/_kt_sampled.py --metric ts2:4/5 --rank 6 --denpow 3 --sector 0 [--prime 0] [--extra 64]
        [--engine rust|flint] [--plant]
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_exact as EX  # noqa: E402
import _kt_metrics as MM  # noqa: E402
import _kt_search as K  # noqa: E402
from _kt_exact_op import get_metric  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIMES = (2147483647, 2147483629)
SECTORS = [(0, 0), (1, 0), (0, 1), (1, 1)]
x, y = MM.x, MM.y


def poly_coeffs(expr, p):
    """Polynomial in x, y (rational coefficients) -> list of (a, b, c mod p)."""
    P = sp.Poly(sp.expand(expr), x, y)
    out = []
    for (a, b), c in zip(P.monoms(), P.coeffs()):
        c = sp.Rational(c)
        if c.q % p == 0:
            raise ValueError(f"prime divides a coefficient denominator {c.q}")
        out.append((a, b, (c.p % p) * pow(c.q % p, p - 2, p) % p))
    return out


def poly_at(coeffs, X, Y, p, maxa, maxb):
    """A polynomial at arrays of points mod p (vectorised; operands < 2^31 so products < 2^62)."""
    Xp = [np.ones_like(X)]
    for _ in range(maxa):
        Xp.append(Xp[-1] * X % p)
    Yp = [np.ones_like(Y)]
    for _ in range(maxb):
        Yp.append(Yp[-1] * Y % p)
    s = np.zeros_like(X)
    for a, b, c in coeffs:
        s = (s + c * (Xp[a] * Yp[b] % p)) % p
    return s


def inv_mod(v, p):
    """Elementwise modular inverse of an int64 array (Fermat)."""
    r = np.ones_like(v); b = v % p; e = p - 2
    while e:
        if e & 1:
            r = r * b % p
        b = b * b % p; e >>= 1
    return r


def main():
    def arg(fl, d=None, c=str):
        return c(sys.argv[sys.argv.index(fl) + 1]) if fl in sys.argv else d
    t0 = time.time()
    spec, rank, denpow = arg("--metric"), arg("--rank", 2, int), arg("--denpow", 1, int)
    margin, sector, prime = arg("--margin", EX.MARGIN, int), arg("--sector", 0, int), arg("--prime", 0, int)
    extra, engine, threads = arg("--extra", 64, int), arg("--engine", "rust"), arg("--threads", 8, int)
    p = PRIMES[prime]
    sy, sT = SECTORS[sector]
    t_, ph = sp.symbols("t phi", real=True)
    K.set_dim((t_, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    ginv, name = get_metric(spec)
    for (a, b) in ((0, 1), (0, 2), (1, 2), (1, 3), (2, 3)):
        assert ginv[a, b] == 0, "assumes no t/phi - x/y and no x-y cross terms"
    L, _, _ = MM.denominator(ginv)
    den = L ** denpow
    _, prods, _ = EX.generators(ginv, rank, den)
    bx, by = EX.reducible_box(prods, den)          # raises if a reducible is not representable (the ">= floor" half)
    dx, dy = bx + margin, by + margin
    mons = K.monomials(rank)
    cols = [(mi, a, b) for mi, m in enumerate(mons) if (m[0] + m[3]) % 2 == sT
            for a in range(dx + 1) for b in range(dy + 1) if (b + m[2]) % 2 == sy]
    n = len(cols)
    floor = len(prods) if (sy, sT) == (0, rank % 2) else 0      # products of p_t, p_phi, H: y-even, (t,phi)-parity = rank
    nrows = n + extra
    print(f"{name}: rank {rank}, den L^{denpow}, box {dx}x{dy}, sector {sector} (sy={sy}, sT={sT}): {n} columns, "
          f"{nrows} sampled rows, prime {p}; reducible products in this sector: {floor}", flush=True)
    pieces = {}
    for ab in ((0, 0), (0, 3), (3, 3), (1, 1), (2, 2)):
        num, dd = sp.fraction(sp.cancel(sp.together(ginv[ab])))
        pieces[ab] = dict(N=num, D=dd, Nx=sp.diff(num, x), Ny=sp.diff(num, y), Dx=sp.diff(dd, x), Dy=sp.diff(dd, y))
    Lc = {k: poly_coeffs(e, p) for k, e in (("L", L), ("Lx", sp.diff(L, x)), ("Ly", sp.diff(L, y)))}
    pc = {ab: {k: poly_coeffs(e, p) for k, e in d.items()} for ab, d in pieces.items()}
    allc = [c for d in pc.values() for c in d.values()] + list(Lc.values())
    maxa = max(max((a for a, _, _ in c), default=0) for c in allc)
    maxb = max(max((b for _, b, _ in c), default=0) for c in allc)
    rng = np.random.default_rng(20261010 + 97 * sector + 7919 * prime + 13 * rank)
    X, Y, PM, skipped = [], [], [], 0
    while len(X) < nrows:
        B = 4096
        Xb = rng.integers(2, p - 1, B, dtype=np.int64); Yb = rng.integers(2, p - 1, B, dtype=np.int64)
        ok = poly_at(Lc["L"], Xb, Yb, p, maxa, maxb) != 0
        for d in pc.values():
            ok &= poly_at(d["D"], Xb, Yb, p, maxa, maxb) != 0
        skipped += int((~ok).sum())
        X.extend(Xb[ok].tolist()); Y.extend(Yb[ok].tolist())
        PM.extend(rng.integers(1, p - 1, (int(ok.sum()), 4), dtype=np.int64).tolist())
    X = np.array(X[:nrows], np.int64); Y = np.array(Y[:nrows], np.int64); PM = np.array(PM[:nrows], np.int64)
    at = lambda c: poly_at(c, X, Y, p, maxa, maxb)
    G, Gx, Gy = {}, {}, {}
    for ab, d in pc.items():
        N_, D_, Nx_, Ny_, Dx_, Dy_ = (at(d[k]) for k in ("N", "D", "Nx", "Ny", "Dx", "Dy"))
        Di = inv_mod(D_, p); Di2 = Di * Di % p
        G[ab] = N_ * Di % p
        Gx[ab] = (Nx_ * D_ % p - N_ * Dx_ % p) % p * Di2 % p
        Gy[ab] = (Ny_ * D_ % p - N_ * Dy_ % p) % p * Di2 % p
    Lv, Lxv, Lyv = at(Lc["L"]), at(Lc["Lx"]), at(Lc["Ly"])
    Li = inv_mod(Lv, p)
    pt_, px_, py_, pf_ = PM[:, 0], PM[:, 1], PM[:, 2], PM[:, 3]
    half = pow(2, p - 2, p)

    def quad(D):   # 1/2 g^ab p_a p_b, the t-phi cross term counted twice
        return (half * ((D[(0, 0)] * pt_ % p * pt_ + D[(3, 3)] * pf_ % p * pf_) % p
                        + (D[(1, 1)] * px_ % p * px_ + D[(2, 2)] * py_ % p * py_) % p) % p
                + D[(0, 3)] * pt_ % p * pf_) % p
    Hx, Hy = quad(Gx), quad(Gy)
    Hpx, Hpy = G[(1, 1)] * px_ % p, G[(2, 2)] * py_ % p
    xi, yi = inv_mod(X, p), inv_mod(Y, p)
    axL = denpow * Lxv % p * Li % p            # d L_x / L
    ayL = denpow * Lyv % p * Li % p
    P4 = [pt_, px_, py_, pf_]
    out = os.path.join(ROOT, "data", f"sampled_{os.getpid()}.ktd")
    plant = "--plant" in sys.argv
    ncol_out = n + (1 if plant else 0)
    cm = np.array([c[0] for c in cols]); ca = np.array([c[1] for c in cols], np.int64)
    cb = np.array([c[2] for c in cols], np.int64)
    with open(out, "wb") as fh:
        fh.write(b"KTD1"); fh.write(np.array([nrows, ncol_out, p], "<u8").tobytes())
        CH = 256
        for r0 in range(0, nrows, CH):
            sl = slice(r0, min(nrows, r0 + CH))
            k = sl.stop - sl.start
            Am = np.zeros((len(mons), k), np.int64); Bm = np.zeros_like(Am); Cm = np.zeros_like(Am)
            for mi, m in enumerate(mons):
                mv = np.ones(k, np.int64)
                for q in range(4):
                    for _ in range(m[q]):
                        mv = mv * P4[q][sl] % p

                def dm(q):
                    if m[q] == 0:
                        return np.zeros(k, np.int64)
                    v = np.full(k, m[q], np.int64)
                    for qq in range(4):
                        for _ in range(m[qq] - (1 if qq == q else 0)):
                            v = v * P4[qq][sl] % p
                    return v
                Am[mi] = (Hx[sl] * dm(1) % p + Hy[sl] * dm(2) % p) % p
                Bm[mi] = mv * Hpx[sl] % p
                Cm[mi] = mv * Hpy[sl] % p
            XP = np.ones((dx + 1, k), np.int64)
            for a in range(1, dx + 1):
                XP[a] = XP[a - 1] * X[sl] % p
            YP = np.ones((dy + 1, k), np.int64)
            for b in range(1, dy + 1):
                YP[b] = YP[b - 1] * Y[sl] % p
            fa = (ca[:, None] * xi[sl][None, :] % p - axL[sl][None, :]) % p          # a/x - d L_x/L
            fb = (cb[:, None] * yi[sl][None, :] % p - ayL[sl][None, :]) % p
            bracket = (Am[cm] - Bm[cm] * fa % p - Cm[cm] * fb % p) % p
            vals = XP[ca] * YP[cb] % p * bracket % p                                    # (ncols, k)
            block = vals.T
            if plant:
                block = np.concatenate([block, block[:, :1]], axis=1)
            fh.write(np.ascontiguousarray(block).astype("<u4").tobytes())
    tg = time.time() - t0
    exe = os.path.join(ROOT, "native", "flint_rank") if engine == "flint" else \
        os.path.join(ROOT, "rust", "ktdense", "target", "release", "ktdense")
    try:
        res = subprocess.run([exe, out, str(threads)], capture_output=True, text=True, check=True)
    finally:
        os.remove(out)
    r = json.loads(res.stdout.strip().splitlines()[-1])
    nul = r["nullity"]
    fl = floor + (1 if plant else 0)
    tag = " [PLANTED duplicate column]" if plant else ""
    verdict = ("NULL PROVED (bound = reducible)" if nul == fl else
               f"bound exceeds reducible by {nul - fl} (INCONCLUSIVE until resolved)" if nul > fl else
               "BELOW the floor: generator or ansatz ERROR")
    print(f"  generated {nrows}x{ncol_out} in {tg:.0f}s (skipped {skipped} bad points); {engine} rank {r['rank']} "
          f"in {r['seconds']}s", flush=True)
    print(f"VERDICT {name} rank {rank} den^{denpow} box {dx}x{dy} sector {sector} prime {prime}{tag}: sampled nullity "
          f"{nul} (upper bound), expected floor {fl} -> {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
