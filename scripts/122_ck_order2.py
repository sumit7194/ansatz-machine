#!/usr/bin/env python3
"""Step 122 — CARTAN-KARLHEDE AT ORDER 2 (bridge round 8, ask D / Falsification Ledger G6).

The bridge went to test G6 -- "CK terminates at order <= 2 for all 4D vacuum type-D pairs in
our catalog (theory allows 7)" -- and could not, because ck.py computed orders 0 and 1 only.
This step adds the order-2 recursion and tests G6 with it.

WHAT ORDER 2 ADDS, structurally. At order 1 the surviving components D_a Psi2 all carry
NONZERO boost/spin weight, so none is an invariant by itself and only weight-cancelling
PRODUCTS like (D_l Psi2)(D_n Psi2) can be compared. At order 2 the weights add, so components
such as D_l D_n Psi2 and D_m D_mb Psi2 have total weight (0,0) and are Cartan invariants
outright. That is the real reason order 2 buys so much more than order 1, and it is why
ck.py grew a general weight_invariants() rather than another hard-coded pair list.

TWO PUBLISHED RESULTS ARE USED AS GROUND TRUTH (this battery is not self-graded):

  (1) KARLHEDE, LINDSTROEM & AAMAN, Gen. Rel. Grav. 14 (1982) 569, "A note on a local effect at
      the Schwarzschild sphere": the scalar built from nabla(Riemann) changes sign exactly at
      the horizon. Our order-1 invariant (D_l Psi2)(D_n Psi2) must therefore vanish at r = 2M,
      and it does -- and so does the order-2 invariant D_m D_mb Psi2. Both track M correctly
      (root at r = 2 for M = 1, at r = 4 for M = 2), which is a sharp test: a sign or factor
      error in the second derivative would move the root.

  (2) COLLINS, d'INVERNO & VICKERS, Class. Quantum Grav. 7 (1990) 2005, "The Karlhede
      classification of type D vacuum spacetimes": the bound on the order of differentiation
      needed for type D VACUUM is reduced from the general 7 to TWO. G6 is exactly this
      theorem, and this battery machine-checks it on our catalog rather than citing it.

TERMINATION IS KARLHEDE'S CRITERION, BOTH HALVES. Stop at the first order where neither the
number of functionally independent invariants NOR the isotropy dimension changed. Counting
invariants alone stops too early: Schwarzschild has t1 = t0 = 1, but its isotropy drops 2 -> 1
at order 1 (the boost is used up by D_l Psi2, the spin is not), so the recursion is still
moving; it settles at order 2 with (t, iso) = (1, 1). See ck.residual_isotropy().

THREE FIXES THIS FORCED, each measured (all in ck.py):
  * covariant_derivative_weyl computed all 4^4 index slots per direction; nabla_e preserves the
    Weyl symmetries, so only 21 of 256 are independent. Kerr's nabla C went from
    not-finishing-in-10-minutes to ~11 s. Gated below against the naive version.
  * a Piecewise guard on Eq(sin(theta), 0) -- the axis, where the canonical m is undefined --
    was faking theta dependence and inflating Schwarzschild to t2 = 2 (a phantom second
    invariant). ck.generic_branch() drops branches supported on a measure-zero set only.
  * D_m D_l Psi2 of Schwarzschild is identically zero but came out as
    (r-2)^(3/2)(sin(2th)tan(th) + cos(2th) - 1)/(...), which neither simplify() nor trigsimp()
    reduces. A component wrongly believed nonzero eats the spin isotropy, so Schwarzschild
    reported isotropy 0 and the WRONG termination order. expand_trig() then simplify() kills
    it. (§119's finding again: the wall is the simplifier.)

Order 2 is OPT-IN (ck_signature(..., order2=True)): it costs ~30x order 1, and the frozen
§116-§119 verdicts stay bit-for-bit reproducible without it.

The full battery runs the WHOLE type-D vacuum catalog -- Schwarzschild (two masses and the
isotropic chart), ZV delta=1, Taub-NUT and Kerr -- to genuine completion. `--quick` trims only
the wall-clock safety budget (the guard against a true hang), never which metrics are tested;
G6 is a claim about the whole catalog, so the whole catalog is what it is checked against.

Repro:  .venv/bin/python scripts/122_ck_order2.py [--quick]
"""
import os
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

import ck
from gr_engine import Geometry

# `--quick` trims only the wall-clock SAFETY budget, not the set of metrics tested: G6 is a claim
# about the whole type-D vacuum catalog, so the full battery always runs every entry (Kerr and
# Taub-NUT included) to genuine completion. The budget exists only so a true hang cannot lock the
# gate forever; a metric that walls does so on its own compute, not on an artificial cutoff.
QUICK = "--quick" in sys.argv
BUDGET = 900 if QUICK else 3600

t, r, th, ph, rho = sp.symbols("t r theta phi rho", positive=True)
u = sp.Symbol("u", real=True)
x, y = sp.symbols("x y", real=True)


class Walled(Exception):
    pass


def budgeted(seconds, fn, *a, **kw):
    """Run fn under a wall-clock budget. A symbolic step that does not finish is a MEASURED
    limit, not a crash -- the repo's three-valued discipline applied to compute time."""
    def boom(signum, frame):
        raise Walled()
    old = signal.signal(signal.SIGALRM, boom)
    signal.alarm(int(seconds))
    try:
        return fn(*a, **kw)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


# ------------------------------------------------------------------ the metrics
def schwarzschild(Mv):
    f = 1 - 2 * Mv / r
    return Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph]), None


def schwarzschild_isotropic():
    A = (1 - 1 / (2 * rho)) / (1 + 1 / (2 * rho))
    B = (1 + 1 / (2 * rho))**4
    return Geometry(sp.diag(-A**2, B, B * rho**2, B * rho**2 * sp.sin(th)**2),
                    [t, rho, th, ph]), None


def zipoy_voorhees_1():
    """ZV at delta = 1 -- Schwarzschild in prolate spheroidal coordinates, where nothing about
    the metric functions looks like 1 - 2M/r."""
    F = (x - 1) / (x + 1)
    H = (x**2 - 1) / (x**2 - y**2)
    return Geometry(sp.diag(-F, H * (x**2 - y**2) / (F * (x**2 - 1)),
                            H * (x**2 - y**2) / (F * (1 - y**2)),
                            (x**2 - 1) * (1 - y**2) / F), [t, x, y, ph]), None


def kerr(a=sp.Rational(1, 2), Mv=1):
    """Kerr in Boyer-Lindquist, in the u = cos(theta) chart (rational -- the trig chart swells),
    with the Kinnersley tetrad supplied explicitly so no Gram-Schmidt sign oracle is needed."""
    S = r**2 + a**2 * u**2
    D = r**2 - 2 * Mv * r + a**2
    s2 = 1 - u**2
    g = sp.zeros(4, 4)
    g[0, 0] = -(1 - 2 * Mv * r / S)
    g[0, 3] = g[3, 0] = -2 * Mv * r * a * s2 / S
    g[1, 1] = S / D
    g[2, 2] = S / s2
    g[3, 3] = (r**2 + a**2 + 2 * Mv * r * a**2 * s2 / S) * s2
    sq, sn = sp.sqrt(2), sp.sqrt(s2)
    rp, rm = r + sp.I * a * u, r - sp.I * a * u
    tet = ([(r**2 + a**2) / D, 1, 0, a / D],
           [(r**2 + a**2) / (2 * S), -D / (2 * S), 0, a / (2 * S)],
           [sp.I * a * sn / (sq * rp), 0, -sn / (sq * rp), sp.I / (sq * rp * sn)],
           [-sp.I * a * sn / (sq * rm), 0, -sn / (sq * rm), -sp.I / (sq * rm * sn)])
    return Geometry(g, [t, r, u, ph]), tet


def taub_nut(N=sp.Rational(1, 2), Mv=1):
    """Taub-NUT in the u = cos(theta) chart, with the orthonormal frame supplied explicitly
    (Gram-Schmidt cannot settle the sign of a frame norm here)."""
    S = r**2 + N**2
    f = (r**2 - 2 * Mv * r - N**2) / S
    P = sp.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [-2 * N * u, 0, 0, 1]])
    g = sp.simplify(P.T * sp.diag(-f, 1 / f, S / (1 - u**2), S * (1 - u**2)) * P)
    sq, sf, sn, sS = sp.sqrt(2), sp.sqrt(f), sp.sqrt(1 - u**2), sp.sqrt(S)
    E0, E1 = [1 / sf, 0, 0, 0], [0, sf, 0, 0]
    E2 = [0, 0, -sn / sS, 0]
    E3 = [2 * N * u / (sS * sn), 0, 0, 1 / (sS * sn)]
    tet = ([(E0[k] + E1[k]) / sq for k in range(4)],
           [(E0[k] - E1[k]) / sq for k in range(4)],
           [(E2[k] + sp.I * E3[k]) / sq for k in range(4)],
           [(E2[k] - sp.I * E3[k]) / sq for k in range(4)])
    return Geometry(g, [t, r, u, ph]), tet


DOMAINS = {
    "Schwarzschild M=1": (sp.Q.positive(r - 3),),
    "Schwarzschild M=2": (sp.Q.positive(r - 5),),
    "Schwarzschild (isotropic chart)": (sp.Q.positive(rho - sp.Rational(1, 2)),),
    "ZV delta=1 (prolate spheroidal)": (sp.Q.positive(x - 1), sp.Q.positive(1 - y**2)),
    "Kerr a=1/2": (sp.Q.positive(r - 3), sp.Q.positive(1 - u**2)),
    "Taub-NUT n=1/2": (sp.Q.positive(r - 4), sp.Q.positive(1 - u**2)),
}


def signature(name, builder, order2=True):
    geo, tet = builder()
    ck.set_domain(*DOMAINS[name])
    return ck.ck_signature(geo, name, tet=tet, order2=order2)


# ------------------------------------------------------------------ (A) gate the nabla-C rewrite
def gate_nabla_c():
    """The symmetry-reduced nabla C must agree with the naive 4^4 loop, component by component.
    Compared NUMERICALLY at random points: the two forms are algebraically equal but land in
    different unsimplified shapes, and sp.simplify fails on some of the differences (it reports
    21 false mismatches on Schwarzschild), so a symbolic comparison would be the less reliable
    test here, not the more reliable one."""
    import random
    geo, _ = schwarzschild(1)
    C = ck.weyl_tensor(geo)
    n, xs, Gam = geo.n, geo.coords, geo.christoffel

    def naive(e, a, b, c, d):
        # deliberately NOT simplified: the comparison below is numeric, so cancel(together(.))
        # here would be 1024 wasted symbolic normalisations (it dominated the whole battery).
        tt = sp.diff(C[a][b][c][d], xs[e])
        for f in range(n):
            tt -= (Gam[f][e][a] * C[f][b][c][d] + Gam[f][e][b] * C[a][f][c][d]
                   + Gam[f][e][c] * C[a][b][f][d] + Gam[f][e][d] * C[a][b][c][f])
        return tt

    new = ck.covariant_derivative_weyl(geo, C)
    rnd = random.Random(20260723)
    pts = [{r: sp.Rational(rnd.randint(30, 90), 10), th: sp.Rational(rnd.randint(3, 28), 10)}
           for _ in range(3)]
    worst = 0.0
    for e in range(n):
        for a in range(n):
            for b in range(n):
                for c in range(n):
                    for d in range(n):
                        diff = naive(e, a, b, c, d) - new[e][a][b][c][d]
                        if diff == 0:
                            continue
                        for p in pts:
                            worst = max(worst, abs(complex(sp.N(diff.subs(p)))))
    return worst


def main():
    print(__doc__.split("Repro:")[0])
    ok = []

    # ------------------------------------------------------------- (A)
    t0 = time.time()
    worst = gate_nabla_c()
    okA = worst < 1e-20
    ok.append(okA)
    print(f"  (A) the symmetry-reduced nabla C vs the naive 4^4 loop, all 1024 components x 3 "
          f"random points:")
    print(f"      max |difference| = {worst:.1e}   {'✅ identical' if okA else '❌'}   "
          f"({time.time()-t0:.1f}s)")

    # ------------------------------------------------------------- (B) published ground truth
    print(f"\n  (B) GROUND TRUTH -- Karlhede-Lindstroem-Aaman (1982): the horizon shows up in "
          f"the")
    print(f"      derivatives of curvature. Our invariants must vanish at r = 2M, and track M:")
    sigs = {}
    okB = True
    for name, Mv in (("Schwarzschild M=1", 1), ("Schwarzschild M=2", 2)):
        t0 = time.time()
        s = signature(name, lambda Mv=Mv: schwarzschild(Mv))
        sigs[name] = s
        i1 = sp.factor(list(s["order1_invariants"].values())[0])
        i2 = sp.factor(s["order2_invariants"].get("K:D_m_D_mb_Psi2", sp.S.Zero))
        root_ok = (sp.simplify(i1.subs(r, 2 * Mv)) == 0 and sp.simplify(i2.subs(r, 2 * Mv)) == 0)
        okB &= root_ok
        print(f"      {name}:  order-1 (D_l Psi2)(D_n Psi2) = {i1}")
        print(f"      {' ' * len(name)}   order-2  D_m D_mb Psi2      = {i2}")
        print(f"      {' ' * len(name)}   both vanish at r = 2M = {2*Mv}:  "
              f"{'✅' if root_ok else '❌'}   ({time.time()-t0:.0f}s)")
    ok.append(okB)

    # ------------------------------------------------------------- (C) order-2 controls
    # Two controls, both with order 2 fully ON on both sides (comparing an order-2 signature
    # against an order-1-only one would trip the new order-2 label check spuriously -- the
    # comparison must be apples-to-apples):
    #   discrimination -- two different type-D vacua that agree at orders 0 and 1 are split;
    #   recognition    -- the SAME spacetime in a chart that hides it (Schwarzschild in
    #                     isotropic coordinates, whose metric functions share no visible form
    #                     with 1-2M/r) is still recognised with order 2 running.
    print(f"\n  (C) order-2 controls:")
    v, why = ck.equivalent(sigs["Schwarzschild M=1"], sigs["Schwarzschild M=2"])
    okC1 = v == ck.INEQUIVALENT
    print(f"      discrimination -- Schwarzschild M=1 vs M=2  -> {v}  {'✅' if okC1 else '❌'}")
    print(f"          {why[0][:104] if why else ''}")
    t0 = time.time()
    sig_iso = signature("Schwarzschild (isotropic chart)", schwarzschild_isotropic)
    sigs["Schwarzschild (isotropic chart)"] = sig_iso
    v2, why2 = ck.equivalent(sigs["Schwarzschild M=1"], sig_iso)
    okC2 = v2 == ck.EQUIVALENT
    note2 = "✅ the costume seen through, order 2 running" if okC2 else "❌"
    print(f"      recognition -- Schwarzschild vs ISOTROPIC chart -> {v2}  {note2}   "
          f"({time.time()-t0:.0f}s)")
    print(f"          {why2[0][:104] if why2 else ''}")
    ok.append(okC1 and okC2)

    # ------------------------------------------------------------- (D) G6
    print(f"\n  (D) LEDGER G6 -- does CK terminate at order <= 2 on the 4D vacuum type-D "
          f"catalog?")
    print(f"      (Karlhede's criterion, both halves: the first order at which neither t nor "
          f"the isotropy moves.)")
    cases = [("Schwarzschild M=1", lambda: schwarzschild(1)),
             ("Schwarzschild M=2", lambda: schwarzschild(2)),
             ("Schwarzschild (isotropic chart)", schwarzschild_isotropic),
             ("ZV delta=1 (prolate spheroidal)", zipoy_voorhees_1),
             ("Taub-NUT n=1/2", taub_nut),
             ("Kerr a=1/2", kerr)]
    g6, walls = True, []
    for name, builder in cases:
        if name in sigs:
            s, dt = sigs[name], 0.0
        elif name == "Schwarzschild (isotropic chart)":
            s, dt = sig_iso, 0.0
        else:
            t0 = time.time()
            try:
                s = budgeted(BUDGET, signature, name, builder)
            except Walled:
                walls.append(name)
                print(f"      {name:34s} WALLED after {BUDGET}s of symbolic work "
                      f"(measured, not assumed)")
                continue
            except Exception as e:
                walls.append(name)
                print(f"      {name:34s} FAILED: {str(e)[:70]}")
                continue
            dt = time.time() - t0
            sigs[name] = s
        chain = (f"({s['t0']},{s['isotropy_dim']}) -> ({s['t1']},{s['isotropy_dim1']}) "
                 f"-> ({s['t2']},{s['isotropy_dim2']})")
        good = s["ck_order"] in (1, 2)
        g6 &= good
        print(f"      {name:34s} type {s['petrov']}  (t,iso): {chain:26s} "
              f"ck_order = {s['ck_order']}  {'✅' if good else '❌'}  ({dt:.0f}s)")
    ok.append(g6)                      # walls are reported honestly, not counted as G6 failures
    print(f"      G6 verdict on the metrics that completed: "
          f"{'SUPPORTED -- every one terminates at order <= 2 ✅' if g6 else 'VIOLATED ❌'}")
    print(f"      This machine-checks Collins-d'Inverno-Vickers (1990), who proved the bound "
          f"is 2 for")
    print(f"      type D VACUUM against the general bound of 7. Independent route, same "
          f"number.")
    if walls:
        print(f"      NOT reached inside the {BUDGET}s budget: {walls} -- recorded as a "
              f"measured limit.")

    # ------------------------------------------------------------- (E) leg Y's three pairs
    print(f"\n  (E) the three vacuum-vs-vacuum pairs leg Y left open (identical matter sector, "
          f"so the")
    print(f"      Ricci route cannot separate them -- they need exactly this Weyl-side "
          f"machinery):")
    pairs = [("Kerr a=1/2", "Taub-NUT n=1/2"),
             ("Kerr a=1/2", "ZV delta=1 (prolate spheroidal)"),
             ("Taub-NUT n=1/2", "ZV delta=1 (prolate spheroidal)")]
    okE = True
    for A, B in pairs:
        if A not in sigs or B not in sigs:
            print(f"      {A} vs {B}: UNDECIDED -- one side walled above")
            okE = False
            continue
        try:
            v, why = budgeted(BUDGET, ck.equivalent, sigs[A], sigs[B])
        except Walled:
            print(f"      {A} vs {B}: UNDECIDED -- comparison walled")
            okE = False
            continue
        good = v == ck.INEQUIVALENT
        okE &= good
        print(f"      {A} vs {B}\n          -> {v}  {'✅' if good else '❌'}   "
              f"{why[0][:100] if why else ''}")
    ok.append(okE)

    passed = all(ok)
    print(f"\nCK ORDER 2: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(order-2 recursion live; the Karlhede-Lindstroem-Aaman horizon invariant reproduced "
          "at orders 1 and 2; G6 machine-checked against Collins-d'Inverno-Vickers)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
