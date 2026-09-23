#!/usr/bin/env python3
"""K2 -> K1 step 4: a bounded Stackel / coupling-constant-metamorphosis (CCM) screen of MT 2023 Table I.
Pre-registered in data/k2_harmonic_cubic/PREREGISTRATION.md (step 4).

For a free coupling alpha_i of a term V_i whose log is harmonic (target metric V_i|dz|^2 flat), the CCM output with
new coupling E = 0 (forced, see the pre-registration) is U = sum_{j != i} alpha_j V_j / V_i.  Harmonicity is conformally
invariant, so Delta_z U = 0 is the vacuum test.  U is linear in the remaining couplings, so its harmonic sub-family is
the null space of Delta(V_j/V_i), sampled at 50 digits.  Eligibility (Delta log V_i == 0) is COMPUTED per term.
"""
import random
import sys

import mpmath as mp
import sympy as sp

mp.mp.dps = 50
x, y = sp.symbols("x y", positive=True)
r = sp.sqrt(x ** 2 + y ** 2)
th = sp.atan(y / x)                     # x > 0 on the test domain
s3 = sp.sqrt(3)
FAILS = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if detail else ""), flush=True)
    if not ok:
        FAILS.append(label)


def lap(f):
    return sp.diff(f, x, 2) + sp.diff(f, y, 2)


def at_points(exprs, npts=6, seed=9):
    rnd = random.Random(seed)
    rows = []
    for _ in range(npts):
        pt = {x: sp.Rational(rnd.randint(30, 90), 11), y: sp.Rational(rnd.randint(5, 60), 13)}
        rows.append([mp.mpf(sp.N(e.subs(pt), 60)) for e in exprs])
    return rows


def is_zero_fn(e):
    return all(abs(v[0]) < mp.mpf(10) ** -40 for v in at_points([e]))


def harmonic_subfamily(others, Vi):
    """others: list of (name, V_j) with free couplings; returns (null-space dim, basis, singular values)."""
    if not others:
        return 0, [], []
    cols = [lap(Vj / Vi) for _, Vj in others]
    M = mp.matrix(at_points(cols))
    _, S, V = mp.svd_r(M)
    sv = [S[i] for i in range(min(M.rows, M.cols))]
    null = [i for i, s in enumerate(sv) if abs(s) < mp.mpf(10) ** -35] + list(range(len(sv), len(others)))
    return len(null), [[V[i, j] for j in range(len(others))] for i in null if i < V.rows], sv


def screen(name, terms):
    """terms: list of (label, V_term) each with its own FREE coupling."""
    print(f"\n  {name}")
    res = []
    for lab, Vi in terms:
        elig = is_zero_fn(lap(sp.log(Vi)))
        if not elig:
            print(f"    CCM on {lab:<22} log V_i not harmonic -> target curved -> OUT OF SCOPE")
            continue
        others = [(l2, V2) for l2, V2 in terms if l2 != lab]
        d, basis, sv = harmonic_subfamily(others, Vi)
        hit = "no harmonic output except U = 0" if d == 0 else f"HARMONIC sub-family dim {d}: {[[mp.nstr(b, 5) for b in row] for row in basis]}"
        print(f"    CCM on {lab:<22} eligible; output U = sum_(j!=i) alpha_j V_j / V_i : {hit}   sv {[mp.nstr(s, 3) for s in sv]}")
        res.append((lab, d, basis, others, Vi))
    return res


def main():
    print("CONTROLS")
    ctrl = screen("C5/C6: oscillator + linear (+ constant)  [must reproduce SW-IV sigma=0; constant must spoil harmonicity]",
                  [("c1 (x^2+y^2)", x ** 2 + y ** 2), ("c2 x", x), ("c0 (constant)", sp.Integer(1))])
    c5 = [row for row in ctrl if row[0] == "c1 (x^2+y^2)"][0]
    # the harmonic sub-family must be exactly the c2 x direction (c0 = 0): U = c2 x / r^2 = c2 Re(1/z)
    names = [nm for nm, _ in c5[3]]
    ok5 = c5[1] == 1 and abs(c5[2][0][names.index("c0 (constant)")]) < 1e-30 and abs(c5[2][0][names.index("c2 x")]) > 0.5
    check("C5: CCM on c1|z|^2 gives a 1-dim harmonic family, the c2 x direction only", ok5)
    check("C5: that output is x/r^2 = Re(1/z), i.e. SW-IV sigma=0 in w = z^2/2 (superintegrable, dim 3 in §147)",
          sp.simplify(lap(x / r ** 2)) == 0)
    check("C6: the constant's output 1/r^2 is NOT harmonic (the Kepler term in w)", not is_zero_fn(lap(1 / r ** 2)))

    print("\nTABLE I (MT 2023) -- eligible terms and CCM outputs")
    k, cp, cm, c0 = sp.symbols("k c_p c_m c_0")
    kk = sp.Rational(3, 5)
    allres = {}
    allres["V2 Toda (c+, c-, c0 free)"] = screen("V2 Toda", [
        ("c+ e^{k(y+sqrt3 x)}", sp.exp(kk * (y + s3 * x))), ("c- e^{k(y-sqrt3 x)}", sp.exp(kk * (y - s3 * x))),
        ("c0 e^{-2ky}", sp.exp(-2 * kk * y))])
    allres["V6"] = screen("V6 (k1, k2, k3 free)", [
        ("k1/r^2", 1 / r ** 2), ("k2 e^{sqrt3 th}/r^3", sp.exp(s3 * th) / r ** 3), ("k3 e^{-sqrt3 th}/r^3", sp.exp(-s3 * th) / r ** 3)])
    allres["V7"] = screen("V7 (a2=1, a5=0 by rotation; k1, k2, k3 free)", [
        ("k1/y^2", 1 / y ** 2), ("k2/r", 1 / r), ("k3 x/(r y^2)", x / (r * y ** 2))])
    allres["V3"] = screen("V3 Holt type (c2, c3 free; c1 ties two pieces into one term)", [
        ("c1 (4/3 x^2 y^-2/3 + y^4/3)", sp.Rational(4, 3) * x ** 2 * y ** sp.Rational(-2, 3) + y ** sp.Rational(4, 3)),
        ("c2 x y^-2/3", x * y ** sp.Rational(-2, 3)), ("c3 y^-2/3", y ** sp.Rational(-2, 3))])
    allres["V4"] = screen("V4 (single term)", [("k (xy)^-2/3", (x * y) ** sp.Rational(-2, 3))])
    allres["V5"] = screen("V5 (single term)", [("k (x^2-y^2)^-2/3", (x ** 2 - y ** 2) ** sp.Rational(-2, 3))])
    print("\n  V1: terms F_i(w_i) along linear forms; log F_i harmonic <=> (log F_i)'' = 0 <=> F_i exponential -> reduces to V2")
    print("  V8: couplings k, F2, F3 are tied by the entry's side conditions -> no free coupling -> OUT OF SCOPE (as pre-registered)")

    print("\nVERDICT")
    harmonic_outputs = [(e, row[0], row[1]) for e, rows in allres.items() for row in rows if row[1] > 0]
    print(f"  CCM outputs with a nonzero harmonic sub-family: {harmonic_outputs or 'none'}")
    print(f"  HITS: {'none' if not harmonic_outputs else 'CANDIDATES -- need (c) and (b) before any claim'}")
    print("\n" + ("PASS -- controls behaved" if not FAILS else f"FAIL ({len(FAILS)}): {FAILS}"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
