#!/usr/bin/env python3
"""Independent check of the axis-NVE classification (data/nve/NVE_PREREGISTRATION.md).

y'' = r y,  r = -(3/16) L^2,  L = P'/P,  P = E^2 - f0  (mu = 1). Monodromy by power-series analytic continuation in
mpmath (40 digits); solvability of G^0 by the derived-subgroup test (G' abelian), plus reducibility and finiteness.
    .venv/bin/python scripts/_nve_monodromy.py
"""
import cmath
import json
import os
import random
import sys
import time

import mpmath as mp
import sympy as sp

mp.mp.dps = 40
STEP = mp.mpf("0.4")          # step / distance-to-nearest-singular-point (truncation control)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "nve")
z = sp.symbols("z")
R = sp.Rational
I = sp.I
CASES = [
    ("K", 1 - 1 / (z - R(3, 5) * I) - 1 / (z + R(3, 5) * I), [R(4, 5), R(19, 20)], "SOLVABLE"),
    ("Z", ((z - 1) / (z + 1)) ** 2, [R(1, 2), R(4, 5)], "SOLVABLE"),
    ("S1", 1 - 2 / (z + 1), [R(7, 10)], "SOLVABLE"),
    ("G2", 1 - 1 / (z - 1) - 2 / (z + 3), [R(3, 5), R(9, 10)], "SOLVABLE"),
    ("A3", 1 - 1 / (z - 1) - 1 / (z + 2) - 1 / (z - 3), [R(7, 10), R(9, 10), R(13, 10)], "NON-SOLVABLE"),
    ("B3", ((z - 1) / (z + 1)) ** 3, [R(3, 5), R(9, 10)], "NON-SOLVABLE"),
    ("C3", (z**3 + 2 * z + 1) / (z**3 + z + 1), [R(4, 5), R(6, 5)], "NON-SOLVABLE"),
    # M2: f0 - 1/2 = (1/2)(z-1)^2(z-3)/((z+1)(z+2)(z+4)); at E^2 = 1/2 two zeros merge at z = 1
    ("M2", R(1, 2) + R(1, 2) * (z - 1) ** 2 * (z - 3) / ((z + 1) * (z + 2) * (z + 4)), ["sqrt1/2"], "NON-SOLVABLE"),
    # M3: three zeros merge at z = 1 at E^2 = 1/2
    ("M3", R(1, 2) + R(1, 2) * ((z - 1) / (z + 1)) ** 3, ["sqrt1/2"], "SOLVABLE"),
]


def singular_points(f0, E2):
    P = sp.together(E2 - f0)
    N, D = sp.fraction(sp.cancel(P))
    pts = []
    for poly, sgn in ((N, 1), (D, -1)):
        _, facs = sp.sqf_list(sp.Poly(poly, z))
        for fac, mult in facs:
            if fac.degree() == 0:
                continue
            coeffs = [mp.mpc(complex(sp.N(c, 50))) if not c.is_real else mp.mpf(sp.N(c, 50)) for c in fac.all_coeffs()]
            for root in mp.polyroots(coeffs, maxsteps=200, extraprec=200):
                pts.append((mp.mpc(root), sgn * mult))
    deg_f0 = max(sp.degree(sp.fraction(sp.cancel(f0))[0], z), sp.degree(sp.fraction(sp.cancel(f0))[1], z))
    return pts, int(deg_f0)


def taylor_r(pts, z0, K):
    L = [mp.fsum(m * (-1) ** k / (z0 - c) ** (k + 1) for c, m in pts) for k in range(K + 1)]
    return [mp.mpf(-3) / 16 * mp.fsum(L[j] * L[k - j] for j in range(k + 1)) for k in range(K + 1)]


def step(pts, z0, h, Y, K=60):
    """Advance the 2x2 fundamental matrix Y = [[y1, y2], [y1', y2']] from z0 to z0 + h."""
    r = taylor_r(pts, z0, K)
    out = [[None, None], [None, None]]
    for col in range(2):
        a = [Y[0][col], Y[1][col]] + [mp.mpc(0)] * (K + 1)
        for k in range(K - 1):
            a[k + 2] = mp.fsum(r[j] * a[k - j] for j in range(k + 1)) / ((k + 1) * (k + 2))
        y = mp.fsum(a[k] * h**k for k in range(K + 1))
        yp = mp.fsum(k * a[k] * h ** (k - 1) for k in range(1, K + 1))
        out[0][col], out[1][col] = y, yp
    return out


def mindist(pts, w):
    return min(abs(w - c) for c, _ in pts)


def walk(pts, path, Y):
    for A, B in zip(path[:-1], path[1:]):
        w = A
        while abs(B - w) > mp.mpf("1e-30"):
            hmax = STEP * mindist(pts, w)
            seg = B - w
            h = seg if abs(seg) <= hmax else seg / abs(seg) * hmax
            Y = step(pts, w, h, Y)
            w = w + h
    return Y


def seg_clear(pts, A, B, skip, margin):
    for c, _ in pts:
        if c is skip:
            continue
        ab = B - A
        t = max(0, min(1, float(mp.re((c - A) * mp.conj(ab)) / (abs(ab) ** 2))))
        if abs(A + t * ab - c) < margin:
            return False
    return True


def loops(pts):
    cs = [c for c, _ in pts]
    span = max(abs(c) for c in cs) + 1
    best = None
    for k in range(24):
        b = mp.mpc(span * 1.7 * mp.cos(2 * mp.pi * k / 24 + 0.31), span * 1.7 * mp.sin(2 * mp.pi * k / 24 + 0.31))
        ok, clear = True, mp.inf
        for c in cs:
            rho = mp.mpf("0.35") * min([abs(c - d) for d in cs if d is not c] + [1])
            e = c + rho * (b - c) / abs(b - c)
            for cc, _ in pts:
                if cc is c:
                    continue
                ab = e - b
                t = max(0, min(1, float(mp.re((cc - b) * mp.conj(ab)) / (abs(ab) ** 2))))
                clear = min(clear, abs(b + t * ab - cc))
        if best is None or clear > best[1]:
            best = (b, clear)
    b = best[0]
    out = []
    for c, m in pts:
        rho = mp.mpf("0.35") * min([abs(c - d) for d, _ in pts if d is not c] + [1])
        u = (b - c) / abs(b - c)
        th0 = mp.arg(u)
        e = c + rho * u
        circ = [c + rho * mp.expj(th0 + 2 * mp.pi * j / 24) for j in range(25)]
        path = [b, e] + circ[1:] + [b]
        out.append((c, m, path))
    return b, best[1], out


def inv(M):
    d = M[0][0] * M[1][1] - M[0][1] * M[1][0]
    return [[M[1][1] / d, -M[0][1] / d], [-M[1][0] / d, M[0][0] / d]]


def mul(A, B):
    return [[A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
            [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]]


def nrm(A):
    return mp.sqrt(mp.fsum(abs(A[i][j]) ** 2 for i in range(2) for j in range(2)))


def dist_I(A):
    return nrm([[A[0][0] - 1, A[0][1]], [A[1][0], A[1][1] - 1]])


def comm(A, B):
    return mul(mul(A, B), mul(inv(A), inv(B)))


def analyse(gens):
    Cs = []
    for i in range(len(gens)):
        for j in range(i + 1, len(gens)):
            Cs.append(comm(gens[i], gens[j]))
    Cs += [mul(mul(g, C), inv(g)) for g in gens for C in list(Cs)]
    worst = mp.mpf(0)
    for a in range(len(Cs)):
        for b_ in range(a + 1, len(Cs)):
            x = dist_I(comm(Cs[a], Cs[b_])) / (1 + nrm(Cs[a]) ** 2 * nrm(Cs[b_]) ** 2)
            worst = max(worst, x)
    tr = [complex(g[0][0] + g[1][1]) for g in gens]
    random.seed(7)
    words_tr = []
    for _ in range(200):
        W = [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]]
        for _ in range(random.randint(2, 8)):
            g = random.choice(gens)
            W = mul(W, g if random.random() < 0.5 else inv(g))
        words_tr.append(complex(W[0][0] + W[1][1]))
    finite_like = all(abs(t.imag) < 1e-15 and abs(t.real) <= 2 + 1e-15 for t in tr + words_tr)
    # common eigenvector (reducible)
    g0 = gens[0]
    tr0, det0 = g0[0][0] + g0[1][1], g0[0][0] * g0[1][1] - g0[0][1] * g0[1][0]
    lam = [(tr0 + s * mp.sqrt(tr0**2 - 4 * det0)) / 2 for s in (1, -1)]
    red = False
    for l_ in lam:
        v = [g0[0][1], l_ - g0[0][0]] if abs(g0[0][1]) > 1e-30 else [l_ - g0[1][1], g0[1][0]]
        nv = mp.sqrt(abs(v[0]) ** 2 + abs(v[1]) ** 2)
        if nv < 1e-30:
            continue
        v = [v[0] / nv, v[1] / nv]
        ok = True
        for g in gens:
            w = [g[0][0] * v[0] + g[0][1] * v[1], g[1][0] * v[0] + g[1][1] * v[1]]
            if abs(w[0] * v[1] - w[1] * v[0]) / (1 + nrm(g)) > 1e-15:
                ok = False
        red = red or ok
    derived_abelian = worst <= mp.mpf("1e-15")
    if derived_abelian or finite_like:
        verdict = "SOLVABLE"
    elif worst >= mp.mpf("1e-6"):
        verdict = "NON-SOLVABLE"
    else:
        verdict = "UNDETERMINED"
    return dict(worst_comm=float(worst), derived_abelian=bool(derived_abelian), finite_like=finite_like,
                reducible=red, traces=[str(t) for t in tr], verdict=verdict)


def run_case(name, f0, E2):
    t0 = time.time()
    pts, d = singular_points(f0, E2)
    s = sum(1 for _, m in pts if abs(m) == 1)
    h = sum(1 for _, m in pts if abs(m) >= 2)
    b, clear, L = loops(pts)
    gens, gates = [], dict(det=0.0, eig=0.0)
    for c, m, path in L:
        Y = walk(pts, path, [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]])
        gens.append(Y)
        det = Y[0][0] * Y[1][1] - Y[0][1] * Y[1][0]
        gates["det"] = max(gates["det"], float(abs(det - 1)))
        rho = [mp.mpf(1) / 2 + sg * mp.sqrt(mp.mpc(1 - mp.mpf(3) / 4 * m * m)) / 2 for sg in (1, -1)]
        ex = [mp.expj(2 * mp.pi * q) for q in rho]
        tr, dt = Y[0][0] + Y[1][1], det
        ev = [(tr + sg * mp.sqrt(tr**2 - 4 * dt)) / 2 for sg in (1, -1)]
        mis = min(max(abs(ev[0] - ex[0]), abs(ev[1] - ex[1])), max(abs(ev[0] - ex[1]), abs(ev[1] - ex[0])))
        gates["eig"] = max(gates["eig"], float(mis / (1 + abs(ex[0]) + abs(ex[1]))))
    order = sorted(range(len(L)), key=lambda i: float(mp.arg(L[i][0] - b)))
    prods = []
    for seq in (order, order[::-1]):
        Mp = [[mp.mpc(1), mp.mpc(0)], [mp.mpc(0), mp.mpc(1)]]
        for i in seq:
            Mp = mul(Mp, gens[i])
        prods.append(float(dist_I(Mp) / (1 + nrm(Mp))))
    gates["prod_inf"] = min(prods)
    gates["pass"] = gates["det"] <= 1e-20 and gates["eig"] <= 1e-15 and gates["prod_inf"] <= 1e-15
    an = analyse(gens)
    return dict(case=name, E2=str(E2), deg_f0=d, s=s, h=h, s_plus_2h=s + 2 * h,
                kovacic_necessary_ok=(s + 2 * h <= 4), points=[(complex(c), m) for c, m in pts],
                base=str(complex(b)), clearance=float(clear), gates=gates, **an, sec=time.time() - t0)


def main():
    os.makedirs(OUT, exist_ok=True)
    res = []
    for name, f0, Es, pred in CASES:
        for E in Es:
            E2 = R(1, 2) if E == "sqrt1/2" else E**2
            r = run_case(name, f0, E2)
            r["prediction"] = pred
            r["agree"] = (r["verdict"] == pred) and r["gates"]["pass"]
            res.append(r)
            print(f"{name} E^2={E2}: deg {r['deg_f0']}, s={r['s']} h={r['h']} (s+2h={r['s_plus_2h']}); gates "
                  f"{'PASS' if r['gates']['pass'] else 'FAIL'} (det {r['gates']['det']:.1e}, eig {r['gates']['eig']:.1e}, "
                  f"prod {r['gates']['prod_inf']:.1e}); worst comm {r['worst_comm']:.2e}; red {r['reducible']}, "
                  f"finite {r['finite_like']} -> {r['verdict']} (pred {pred}) [{r['sec']:.0f}s]", flush=True)
    json.dump(res, open(os.path.join(OUT, "monodromy_results.json"), "w"), indent=1, default=str)
    ok = all(r["agree"] for r in res)
    print("ALL AS PREDICTED" if ok else "SOME CASE DIFFERS FROM PREDICTION", flush=True)


if __name__ == "__main__":
    main()
