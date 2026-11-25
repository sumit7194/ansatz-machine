"""Office check (2026-11-26) of Fable's route-(i) segment certificate (fable/2026-11-26-route1-seg, 604d520), item (d):
an INDEPENDENT second implementation (the registered 50-digit floating-point engine, _nve_lower / _nve_lower_kc /
_nve_spin_scan; no shared code with the Arb evaluator) on the SAME fixed loops:
  - the circle: the 96-gon of radius 1.35 based at 1.35 (as P.circle_vertices);
  - the lasso: the fixed polygon of k = 21/20 from data/nve/eps/route1_floats.json.
Checks:
  (1) at two interior Chebyshev nodes (j = 6, 18 of n = 24), F, tr M0, tr M1 from the engine lie inside the certified
      node enclosures (route1_seg_nodes.jsonl);
  (2) the proved-M chain on the k-disc: at 4 complex k on |k - 21/20| = R (R of the chosen row), with T = C^-1 M_c^-1 M(k) C
      (C the certificate's own gauge matrix for that loop, M_c the engine's monodromy at k_c), ||T||_2 <= exp(I) for the
      circle (I0) and the lasso (I1); and |F|, |tr M0|, |tr M1| <= M_F, M_trM0, M_trM1.
    NVE_SPIN=3/5 SEGDIR=<checkout> nice -n 12 .venv/bin/python -u scripts/_nve_route1_office_engine.py
Declared peak < 300 MB; one core; no caps."""
import json
import math
import os
import sys

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_lower as L            # noqa: E402
import _nve_lower_kc as KC        # noqa: E402
import _nve_spin_scan as S        # noqa: E402

mp.mp.dps = 50
SEG = os.environ["SEGDIR"]
ref = json.load(open(os.path.join(SEG, "data/nve/eps/route1_floats.json")))["21/20"]
lasso = [mp.mpc(float(p[0]), float(p[1])) for p in ref["lasso"]]
circle = [mp.mpc(1.35 * math.cos(2 * math.pi * j / 96), 1.35 * math.sin(2 * math.pi * j / 96)) for j in range(96)] + [mp.mpc(1.35, 0)]
Mj = json.load(open(os.path.join(SEG, "data/nve/eps/route1_seg_M_nseg1.json")))
ch = Mj["segs"][0]["chosen"]
R, I0, I1 = ch["R"], ch["I0"], ch["I1"]
C0 = [[complex(x) for x in r] for r in ch["C0"]]
C1 = [[complex(x) for x in r] for r in ch["C1"]]
nodes = {}
for line in open(os.path.join(SEG, "data/nve/eps/route1_seg_nodes.jsonl")):
    r = json.loads(line)
    nodes[r["key"]] = r


def monodromies(k):
    """engine M0 (circle 96-gon) and M1 (fixed lasso), with singular points tracked from Kerr to k."""
    path = [k * mp.mpf(j) / 40 for j in range(1, 41)]
    pr, st = S.track_laurent(path, S.kerr_points()[:4])
    sing = [x for x, _ in st]
    W = L.Walker(pr, sing, "0.35")
    M0 = W.walk(circle, KC.I2())
    M1 = W.walk(lasso, KC.I2())
    return M0, M1, sing


def mm(A, B):
    return [[A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
            [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]]


def inv(A):
    d = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    return [[A[1][1] / d, -A[0][1] / d], [-A[1][0] / d, A[0][0] / d]]


def tr(A):
    return A[0][0] + A[1][1]


def F_of(M0, M1):
    return tr(mm(mm(M1, M0), mm(inv(M1), inv(M0)))) - 2


def norm2(A):
    a = mp.matrix([[A[0][0], A[0][1]], [A[1][0], A[1][1]]])
    return max(mp.svd_c(a, compute_uv=False))


def ball(s):
    """'[mid +/- rad]' or a plain number -> (mid, rad)."""
    s = s.strip()
    if s.startswith("["):
        body = s[1:s.index("]")]
        if "+/-" in body:
            m, r = body.split("+/-")
            return (mp.mpf(m.strip()) if m.strip() else mp.mpf(0)), mp.mpf(r.strip())
        return mp.mpf(body), mp.mpf(0)
    return mp.mpf(s), mp.mpf(0)


def inside(val, enc):
    (mr, rr), (mi, ri) = ball(enc[0]), ball(enc[1])
    return abs(mp.re(val) - mr) <= rr * 1.000001 + mp.mpf(10) ** -40 and abs(mp.im(val) - mi) <= ri * 1.000001 + mp.mpf(10) ** -40


print(f"segment chosen row: rho = {ch['rho']}, n = {ch['n']}, R = {R:.6f}, I0 = {I0:.4f}, I1 = {I1:.4f}; "
      f"M_F = {ch['MF']:.3e}, M_trM0 = {ch['MT0']:.3e}, M_trM1 = {ch['MT1']:.3e}", flush=True)
ok_all = True
# (1) interior nodes
for j in (6, 18):
    k = mp.mpf("1.05") + mp.mpf("0.05") * mp.cos(mp.pi * j / ch["n"])
    M0, M1, _ = monodromies(k)
    vals = dict(F=F_of(M0, M1), T0=tr(M0), T1=tr(M1))
    rec = nodes[f"spin 3/5|k in [1, 1.1]|seg0/1|n={ch['n']}|node{j}"]
    ins = {nm: inside(vals[nm], rec[nm]) for nm in vals}
    ok_all &= all(ins.values())
    print(f"(1) node {j}, k = {mp.nstr(k, 12)}: engine F = {mp.nstr(vals['F'], 14)}, tr M0 = {mp.nstr(vals['T0'], 14)}, "
          f"tr M1 = {mp.nstr(vals['T1'], 14)}; inside the certified node enclosures: {ins}", flush=True)
# (2) the proved-M chain at 4 complex k on the disc boundary
kc = mp.mpf("1.05")
M0c, M1c, _ = monodromies(kc)
for th in (45, 135, 225, 315):
    k = kc + R * mp.expj(mp.pi * th / 180)
    M0, M1, _ = monodromies(k)
    res = []
    for nm, Mc, Mk, C, I in (("circle", M0c, M0, C0, I0), ("lasso", M1c, M1, C1, I1)):
        Cm = [[mp.mpc(C[i][j]) for j in range(2)] for i in range(2)]
        T = mm(inv(Cm), mm(mm(inv(Mc), Mk), Cm))
        n2 = norm2(T)
        ok = n2 <= mp.e ** I
        ok_all &= bool(ok)
        res.append(f"{nm}: ||T||_2 = {mp.nstr(n2, 6)} <= exp(I) = {mp.nstr(mp.e ** I, 6)}: {bool(ok)}")
    F = F_of(M0, M1)
    okM = abs(F) <= ch["MF"] and abs(tr(M0)) <= ch["MT0"] and abs(tr(M1)) <= ch["MT1"]
    ok_all &= bool(okM)
    print(f"(2) k = 1.05 + R e^(i {th} deg): " + "; ".join(res) + f"; |F| = {mp.nstr(abs(F), 6)}, |tr M0| = "
          f"{mp.nstr(abs(tr(M0)), 6)}, |tr M1| = {mp.nstr(abs(tr(M1)), 6)} within the proved M: {bool(okM)}", flush=True)
print(f"ALL CHECKS PASS: {bool(ok_all)}")
