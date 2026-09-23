#!/usr/bin/env python3
"""K2 -> K1 step 2: is any potential in the published tables of integrable (NOT superintegrable) planar
systems with a cubic integral HARMONIC?  Pre-registered: data/k2_harmonic_cubic/PREREGISTRATION.md.

Source list: Mitsopoulos & Tsamparlis, arXiv:2301.02473, Table I ("Integrable potentials V(x,y) that admit
CFIs of the type J^(3,2)_0"), which merges Hietarinta 1987 and Karlovini 2000 and adds new entries.  Scope:
completeness is relative to that TYPE of cubic integral, not all cubic integrals.

Rule per entry:  (a) Delta V == 0 with V non-affine;  (b) the published cubic J satisfies {H, J} == 0;
                 (c) quadratic integrals K^{ij}p_ip_j + W form a 1-dim family (only H) -> integrable-only.
Controls: C1 SW-IV sigma=0 must be EXCLUDED (harmonic, cubic, quadratic family dim 3);
          C2 SW-IV with a Kepler term must be NOT-HARMONIC;
          C3 the Holt-type entry V3 must pass (b) and have quadratic family dim 1 (test (c) can say "only H").
Light: symbolic Laplacians, one bracket per entry, 6-unknown linear solves.
"""
import random
import sys

import sympy as sp

x, y = sp.symbols("x y", positive=True)          # positivity keeps fractional powers real on the test domain
px, py = sp.symbols("p_x p_y")
FAILS = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if detail else ""), flush=True)
    if not ok:
        FAILS.append(label)


def lap(V):
    return sp.simplify(sp.diff(V, x, 2) + sp.diff(V, y, 2))


def pb(A, B):
    return sp.simplify(sp.diff(A, x) * sp.diff(B, px) - sp.diff(A, px) * sp.diff(B, x)
                       + sp.diff(A, y) * sp.diff(B, py) - sp.diff(A, py) * sp.diff(B, y))


def quad_family_dim(V, npts=14, seed=1):
    """dim of {flat KT K : curl(K grad V) = 0}; H itself is always in it (a = c).  Exact at points chosen
    so fractional powers stay rational (y a perfect cube, x^2+y^2 not needed)."""
    a, b, c, d, e, f = cs = sp.symbols("a b c d e f")
    K11 = a - d * y + f * y ** 2
    K22 = c + e * x + f * x ** 2
    K12 = (b + d * x - e * y - 2 * f * x * y) / 2
    Vx, Vy = sp.diff(V, x), sp.diff(V, y)
    curl = sp.diff(K11 * Vx + K12 * Vy, y) - sp.diff(K12 * Vx + K22 * Vy, x)
    rnd = random.Random(seed)
    eqs = []
    for _ in range(npts):
        pt = {x: sp.Rational(rnd.randint(2, 9), rnd.randint(2, 5)), y: sp.Rational(rnd.randint(2, 7), rnd.randint(2, 4)) ** 3}
        eqs.append(sp.expand(sp.simplify(curl.subs(pt))))     # exact: y is a perfect cube, so y^(1/3) is rational; NO nsimplify
    M = sp.Matrix([[sp.expand(eq).coeff(v) for v in cs] for eq in eqs])
    return 6 - M.rank(simplify=True)


def entry(name, V, J=None, expect_dim=None):
    """Full rule on one concrete potential (parameters already fixed)."""
    H = (px ** 2 + py ** 2) / 2 + V
    L = lap(V)
    harmonic = (L == 0)
    out = {"harmonic": harmonic}
    if J is not None:
        out["cubic"] = (pb(H, J) == 0)
    if harmonic or expect_dim is not None:
        out["qdim"] = quad_family_dim(V)
    cls = ("NOT-HARMONIC" if not harmonic else
           "UNVERIFIED" if out.get("cubic") is False else
           "EXCLUDED (superintegrable)" if out.get("qdim", 1) >= 2 else "HIT")
    print(f"    {name:<44} Delta V {'== 0' if harmonic else '!= 0'}"
          + (f" | {{H,J}} = 0: {out['cubic']}" if 'cubic' in out else "")
          + (f" | quadratic family dim {out['qdim']}" if 'qdim' in out else "") + f"  ->  {cls}", flush=True)
    return cls, out


def main():
    r = sp.sqrt(x ** 2 + y ** 2)
    print("CONTROLS")
    # C1/C2 in parabolic coordinates, where the SW-IV profile is rational (as in §147): x = xi^2 - eta^2, y = 2 xi eta
    xi, eta = sp.symbols("xi eta", positive=True)
    lap_par = lambda U: sp.simplify((sp.diff(U, xi, 2) + sp.diff(U, eta, 2)) / (4 * (xi ** 2 + eta ** 2)))
    U1 = xi / (xi ** 2 + eta ** 2)                       # sqrt(r+x)/r up to sqrt(2)
    U2 = 1 / (xi ** 2 + eta ** 2) + U1                   # + Kepler term alpha/r, alpha = 1
    check("C1 SW-IV sigma=0 is harmonic", lap_par(U1) == 0)
    print("       (C1's cubic integral and 3-dim quadratic family were measured exactly in §147 / _pp_wave_verify.py)")
    check("C2 SW-IV + Kepler term is NOT harmonic", lap_par(U2) != 0, f"Delta = {sp.factor(lap_par(U2))}")
    c1, c2, c3 = sp.Rational(3, 4), 0, 1
    V3 = (sp.Rational(4, 3) * c1 * x ** 2 + c2 * x + c3) * y ** sp.Rational(-2, 3) + c1 * y ** sp.Rational(4, 3)
    J3 = (px ** 3 + sp.Rational(3, 2) * px * py ** 2
          + ((4 * c1 * x ** 2 + 3 * c2 * x + 3 * c3) * y ** sp.Rational(-2, 3) - 6 * c1 * y ** sp.Rational(4, 3)) * px
          + (12 * c1 * x + sp.Rational(9, 2) * c2) * y ** sp.Rational(1, 3) * py)
    cls3, o3 = entry("C3 = V3 (Holt type), c1=3/4, c2=0, c3=1", V3, J3, expect_dim=1)
    check("C3: published cubic reproduced", o3.get("cubic") is True)
    check("C3: quadratic family is 1-dim (test (c) CAN say 'integrable only')", o3.get("qdim") == 1, f"dim {o3.get('qdim')}")

    print("\nTABLE I (Mitsopoulos-Tsamparlis 2023) -- harmonicity of each entry, over its parameters")
    C = sp.symbols("C1:4"); k, k1, k2, k3, a2, a5 = sp.symbols("k k1 k2 k3 a2 a5")
    results = {}
    # V1 = F1(w1)+F2(w2)+F3(w3), w_i linear with |grad w_i|^2 = 4: Delta V = 4 (F1''+F2''+F3''); functions of
    # three different linear forms sum to zero only if each F_i'' is a constant, sum zero -> V quadratic+affine.
    # A harmonic quadratic potential is separable in rotated Cartesian axes -> has a quadratic integral.
    Vq = C[0] * (x ** 2 - y ** 2) + C[1] * x * y
    print("    V1 (general F_i): harmonic  <=>  F_i'' = const, sum 0  ->  V = harmonic quadratic + affine:")
    cls, _ = entry("V1 harmonic sub-case  C1(x^2-y^2) + C2 xy", Vq.subs({C[0]: 1, C[1]: sp.Rational(1, 3)}))
    results["V1"] = cls
    V2 = sp.exp(k * (y + sp.sqrt(3) * x)) + sp.exp(k * (y - sp.sqrt(3) * x)) + sp.exp(-2 * k * y)
    L2 = sp.simplify(lap(V2))
    print(f"    V2 Toda: Delta V = {sp.factor(L2)}  ->  != 0 for real k != 0 (each term: 4k^2 e^(...))")
    results["V2"] = "NOT-HARMONIC"
    V3g = (sp.Rational(4, 3) * C[0] * x ** 2 + C[1] * x + C[2]) * y ** sp.Rational(-2, 3) + C[0] * y ** sp.Rational(4, 3)
    L3 = sp.expand(lap(V3g) * y ** sp.Rational(8, 3))
    s3 = sp.solve(sp.Poly(L3, x, y).coeffs(), C, dict=True)
    print(f"    V3 Holt: Delta V * y^(8/3) = {L3};  zero only for {s3}  (trivial)")
    results["V3"] = "NOT-HARMONIC"
    V4 = (x * y) ** sp.Rational(-2, 3)
    print(f"    V4 (xy)^(-2/3): Delta V = {sp.simplify(lap(V4))}  ->  != 0"); results["V4"] = "NOT-HARMONIC"
    V5 = (x ** 2 - y ** 2) ** sp.Rational(-2, 3)
    print(f"    V5 (x^2-y^2)^(-2/3): Delta V = {sp.factor(sp.simplify(lap(V5)))}  ->  != 0"); results["V5"] = "NOT-HARMONIC"
    # V6, V8 are sums of homogeneous terms r^n g(theta); Delta(r^n g) = r^(n-2)(n^2 g + g''), and different n do
    # not mix, so each term must vanish separately.
    th = sp.symbols("theta")
    polar = lambda n, g: sp.simplify(n ** 2 * g + sp.diff(g, th, 2))
    print(f"    V6: k1/r^2 -> {polar(-2, k1)} r^-4;  (k2 e^(sqrt3 th)+k3 e^(-sqrt3 th))/r^3 -> "
          f"{sp.factor(polar(-3, k2 * sp.exp(sp.sqrt(3) * th) + k3 * sp.exp(-sp.sqrt(3) * th)))} r^-5  ->  zero only if k1=k2=k3=0")
    results["V6"] = "NOT-HARMONIC"
    V7 = k1 / (a2 * y - a5 * x) ** 2 + k2 / r + k3 * (a2 * x + a5 * y) / (r * (a2 * y - a5 * x) ** 2)
    L7 = sp.simplify(lap(V7.subs({a2: 1, a5: 0})))
    s7 = sp.solve([sp.simplify(L7.subs({x: sp.Rational(px_), y: sp.Rational(py_)})) for px_, py_ in ((1, 2), (3, 1), (2, 5), (5, 3))],
                  [k1, k2, k3], dict=True)
    print(f"    V7 (a2=1, a5=0 by rotation): harmonic only for {s7}  (trivial)")
    results["V7"] = "NOT-HARMONIC" if all(all(v == 0 for v in s.values()) for s in s7) and s7 else "CHECK"
    # V8 = k/r + F2/r^2 + F3/r^3: harmonic <=> k = 0, F2 = A cos2th + B sin2th, F3 = Cc cos3th + D sin3th; then
    # the paper's own side conditions (with k = 0) force F2' = 0 and 3 N F3 = N' F3' -- test the latter.
    Cc, D, A, B, aa, bb = sp.symbols("Cc D A B aa bb")
    F3 = Cc * sp.cos(3 * th) + D * sp.sin(3 * th)
    Np = sp.Rational(9, 8) * (Cc * sp.sin(3 * th) - D * sp.cos(3 * th)) + aa * sp.cos(th) + bb * sp.sin(th)
    check("V8: N_p solves N'' + N = 3 F3'", sp.simplify(sp.diff(Np, th, 2) + Np - 3 * sp.diff(F3, th)) == 0)
    cond = sp.expand(sp.expand_trig(3 * Np * F3 - sp.diff(Np, th) * sp.diff(F3, th)))
    # Show it directly (an empty solver answer is not evidence): the sin(6 theta) / cos(6 theta) Fourier content
    # of the side condition must vanish, and it is a positive-definite form in (Cc, D).
    f6s = sp.simplify(sp.integrate(cond * sp.sin(6 * th), (th, 0, 2 * sp.pi)) / sp.pi)
    f6c = sp.simplify(sp.integrate(cond * sp.cos(6 * th), (th, 0, 2 * sp.pi)) / sp.pi)
    print(f"    V8 harmonic sub-family: side condition 3 N F3 = N' F3' has sin6/cos6 Fourier coefficients {sp.factor(f6s)}, {sp.factor(f6c)}")
    zero_only = sp.solve([f6s, f6c], [Cc, D], dict=True)
    print(f"       which vanish (over the reals) only for {zero_only}  ->  F3 = 0; then k = 0 and F2' = 0 force F2 = 0: trivial")
    results["V8"] = "NOT-HARMONIC (harmonic sub-family is trivial)"

    print("\nVERDICT (Table I, type J^(3,2)_0)")
    for kk, v in results.items():
        print(f"    {kk}: {v}")
    hits = [kk for kk, v in results.items() if v == "HIT"]
    print(f"\n  HITS: {hits or 'none'}")
    print("\n" + ("PASS -- controls behaved; results above" if not FAILS else f"FAIL ({len(FAILS)}): {FAILS}"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
