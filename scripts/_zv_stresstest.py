"""ADVERSARIAL stress-test of §97's claim: "delta=1 has an exact conserved quadratic (Carter),
delta!=1 has none." Try to BREAK it five ways. Each test prints a verdict; a real result
survives all five, a "saw-what-we-wanted" artifact fails at least one.
"""
import math
import sys

import numpy as np

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from poincare import _rk4, p_on_shell
from _zv_invariant import metric, trajectory, basis as base_basis, BNAMES

E0, L0, X0 = 0.97, 4.0, 11.0


def fit_general(f, E, L, x0, p2list, bfun, steps=9000, h=0.02):
    """SVD null-space fit with an arbitrary basis function bfun; returns (S, used, vec)."""
    blocks = 0
    rows = []
    used = 0
    for p2 in p2list:
        pts = trajectory(f, E, L, p2, x0, steps=steps, h=h)
        if not pts or len(pts) < 2500:
            continue
        used += 1
        sub = pts[:: max(1, len(pts) // 250)]
        Phi = np.array([bfun(s) for s in sub], float)
        Phi = Phi - Phi.mean(axis=0, keepdims=True)
        rows.append(Phi)
    if used < 3:
        return None, used, None
    D = np.vstack(rows)
    scale = np.linalg.norm(D, axis=0) + 1e-30
    U, S, Vt = np.linalg.svd(D / scale, full_matrices=False)
    vec = (Vt[-1] / scale)
    vec = vec / np.max(np.abs(vec))
    return S, used, vec


def p2grid(n=16):
    return [round(0.06 + 0.05 * k, 3) for k in range(n)]


# ---------- TEST 1: is ZV(delta=1) really Schwarzschild, with a genuinely conserved Carter? ----------
def test1():
    print("TEST 1 — is delta=1 really the integrable control (ZV(1)=Schwarzschild, Carter conserved)?")
    # (a) metric: g_tt = -(x-1)/(x+1) = -(1-2/r) with r=x+1 (sigma=1) -> Schwarzschild
    g = metric(1.0)  # build_hamilton dict (reduced); instead compare raw metric via zipoy_voorhees
    from zipoy_voorhees import metric as zvg
    gg = zvg(1.0)
    bad = 0
    for (x, y) in [(3.0, 0.2), (5.0, -0.4), (8.0, 0.6)]:
        r = x + 1.0
        gtt = gg([0, x, y, 0])[0][0]
        if abs(gtt - (-(1 - 2.0 / r))) > 1e-12:
            bad += 1
    # (b) the EXACT Schwarzschild Carter p_theta^2 + L^2/sin^2 must be conserved along a ZV(1) orbit.
    # In (x,y): p_theta^2 = (1-y^2) p_y^2, sin^2 = 1-y^2, so K = (1-y^2)p_y^2 + L^2/(1-y^2).
    f = metric(1.0)
    p1 = p_on_shell(f, X0, 0.0, 0.3, E0, L0)
    s = [X0, 0.0, p1, 0.3]
    Ks = []
    for _ in range(40000):
        s = _rk4(f, s, 0.02, E0, L0)
        if not (1.3 < s[0] < 120 and abs(s[1]) < 0.999):
            break
        x, y, px, py = s
        Ks.append((1 - y * y) * py * py + L0 * L0 / (1 - y * y))
    drift = (max(Ks) - min(Ks)) / (sum(Ks) / len(Ks))
    okA = bad == 0
    okB = drift < 1e-10
    print(f"  (a) g_tt matches Schwarzschild -(1-2/r) at all test points: {'YES' if okA else 'NO'}")
    print(f"  (b) exact Schwarzschild Carter (1-y^2)p_y^2+L^2/(1-y^2) drift along orbit = {drift:.1e} "
          f"-> {'CONSERVED' if okB else 'NOT conserved'}")
    print(f"  VERDICT: delta=1 control is {'LEGIT' if okA and okB else 'SUSPECT'}\n")
    return okA and okB


# ---------- TEST 2: is "no invariant at delta!=1" real, or under-resolution? ----------
def test2():
    print("TEST 2 — is delta!=1's 1e-5 a REAL non-invariant, or under-sampling/integration error?")
    print("  (if it DROPS toward 1e-15 with more orbits or tighter steps, an invariant DOES exist)")
    out = {}
    for label, kw in [("16 orbits, h=0.02", dict(p2list=p2grid(16), h=0.02)),
                      ("24 orbits, h=0.02", dict(p2list=p2grid(24), h=0.02)),
                      ("32 orbits, h=0.02", dict(p2list=p2grid(32), h=0.02)),
                      ("16 orbits, h=0.01", dict(p2list=p2grid(16), h=0.01, steps=18000))]:
        for delta in (1.0, 1.3):
            S, used, _ = fit_general(metric(delta), E0, L0, X0, kw.get("p2list"), base_basis,
                                     steps=kw.get("steps", 9000), h=kw["h"])
            out[(label, delta)] = (S[-1], used)
    print(f"  {'config':22s} | delta=1 SV (control) | delta=1.3 SV (test)")
    d13 = []
    for label in ["16 orbits, h=0.02", "24 orbits, h=0.02", "32 orbits, h=0.02", "16 orbits, h=0.01"]:
        s1 = out[(label, 1.0)][0]
        s13 = out[(label, 1.3)][0]
        d13.append(s13)
        print(f"  {label:22s} | {s1:.2e}           | {s13:.2e}")
    # real if delta=1.3 SV stays ~1e-5 (within a decade) and never collapses toward the delta=1 floor
    stable = max(d13) / min(d13) < 30 and min(d13) > 1e-7
    print(f"  VERDICT: delta=1.3 SV {'STABLE ~1e-5 (real non-invariant)' if stable else 'COLLAPSES (artifact!)'}\n")
    return stable


# ---------- TEST 3: basis rigging? enrich the basis, see if the contrast survives ----------
def enriched(s):
    x_, y_, px, py = s
    om = 1.0 - y_ * y_
    return base_basis(s) + [px * py * y_ * y_, px * py * x_, py * py * x_ * y_ * y_,
                            px * px * x_ * x_ * x_, py * py / om]


def test3():
    print("TEST 3 — did I rig the basis? Enrich it (+5 higher-order terms) and re-check the contrast.")
    r = {}
    for delta in (1.0, 1.3):
        S, used, _ = fit_general(metric(delta), E0, L0, X0, p2grid(20), enriched)
        r[delta] = S[-1]
    keep1 = r[1.0] < 1e-9          # delta=1 must STILL find Carter (not destroyed by extra terms)
    no13 = r[1.3] > 1e-7           # delta=1.3 must STILL have none (no spurious invariant created)
    print(f"  enriched basis (16 terms): delta=1 SV={r[1.0]:.2e}, delta=1.3 SV={r[1.3]:.2e}")
    print(f"  VERDICT: {'ROBUST (Carter survives, no spurious invariant)' if keep1 and no13 else 'BASIS-DEPENDENT (suspect!)'}\n")
    return keep1 and no13


# ---------- TEST 4: out-of-sample — fit on some orbits, test conservation on a HELD-OUT orbit ----------
def test4():
    print("TEST 4 — out-of-sample (anti-overfit): fit the invariant on orbits, test it on a HELD-OUT orbit.")
    res = {}
    for delta in (1.0, 1.3):
        f = metric(delta)
        train = p2grid(16)[:12]     # fit on these
        S, used, vec = fit_general(f, E0, L0, X0, train, base_basis)
        # held-out orbit (a p2 not in train)
        pts = trajectory(f, E0, L0, 0.93, X0)      # 0.93 is outside the 0.06..0.61 train grid
        Cs = [float(np.dot(vec, base_basis(s))) for s in pts[:: max(1, len(pts) // 300)]]
        rel = (max(Cs) - min(Cs)) / (np.std(Cs) + abs(np.mean(Cs)) + 1e-30)
        res[delta] = rel
    okfit = res[1.0] < 1e-3 and res[1.3] > 10 * res[1.0]
    print(f"  held-out invariant spread: delta=1 = {res[1.0]:.1e} (should be ~0, conserved),  "
          f"delta=1.3 = {res[1.3]:.1e} (should be large, NOT conserved)")
    print(f"  VERDICT: {'GENERALIZES (delta=1 holds out-of-sample, delta=1.3 does not)' if okfit else 'OVERFIT (suspect!)'}\n")
    return okfit


# ---------- TEST 5: cherry-picked orbit family? robust across (E,L,x0)? ----------
def test5():
    print("TEST 5 — cherry-picked? Repeat the delta=1-vs-1.3 contrast at DIFFERENT (E,L,x0).")
    ok = True
    for (E, L, x0) in [(0.96, 3.8, 9.0), (0.98, 4.3, 14.0), (0.95, 3.6, 8.0)]:
        S1, u1, _ = fit_general(metric(1.0), E, L, x0, p2grid(16), base_basis)
        S13, u13, _ = fit_general(metric(1.3), E, L, x0, p2grid(16), base_basis)
        if S1 is None or S13 is None:
            print(f"  (E={E},L={L},x0={x0}): too few bound orbits, skipped"); continue
        good = S1[-1] < 1e-9 and S13[-1] > 1e-7
        ok = ok and good
        print(f"  (E={E},L={L},x0={x0}): delta=1 SV={S1[-1]:.1e} [{u1} orb], "
              f"delta=1.3 SV={S13[-1]:.1e} [{u13} orb]  {'OK' if good else 'FAIL'}")
    print(f"  VERDICT: {'ROBUST across orbit families' if ok else 'CHERRY-PICKED (suspect!)'}\n")
    return ok


if __name__ == "__main__":
    print("=" * 78)
    print("ADVERSARIAL STRESS-TEST — did we break the wall, or see what we wanted?")
    print("=" * 78 + "\n")
    v = [test1(), test2(), test3(), test4(), test5()]
    print("=" * 78)
    names = ["delta=1 control legit", "delta!=1 non-invariant real", "basis not rigged",
             "generalizes out-of-sample", "robust across orbits"]
    for n, ok in zip(names, v):
        print(f"  [{'PASS' if ok else 'FAIL'}]  {n}")
    print(f"\n  OVERALL: {'CLAIM SURVIVES all 5 adversarial tests ✅' if all(v) else 'CLAIM BROKEN — at least one failure ❌'}")
    print("=" * 78)
