#!/usr/bin/env python3
"""dCS step 5: does the dCS black hole keep Carter's constant -- polynomially, or rationally?

THE QUESTION, and why it is not a repeat of anyone's ladder. Owen, Yunes & Witek closed dCS ranks
2-6 at O(chi^2 zeta) -- our exact truncation -- so a rank ladder here would be reproduction (D53).
What nobody has asked is whether Carter survives as a RATIONAL first integral, Q + eps K1/(2 Q^m),
which is invisible to every polynomial Killing-tensor search including theirs, and which would
reconcile their null with Cardenas-Avendano's opposite chaos-based conjecture.

WHAT MAKES IT FALSIFIABLE AGAINST US. §141-§142 established that a rational Carter of pole order m
reappears as a POLYNOMIAL Killing tensor at rank 2(m+1), and that the pole order saturates at 2 in
the families mapped so far. So if dCS kept a rational Carter at pole order 1 or 2, a tensor would
exist at rank 4 or rank 6 -- and Owen-Yunes-Witek report none. Our own framework therefore PREDICTS
their null. Finding a survivor contradicts one of us; finding none confirms both by two methods that
share no code.

STEP 1 HERE IS THE RANK-2 QUESTION, which is also an independent check of a published result: they
solved by hand and in Maple/Mathematica with arbitrary functions of (r, theta); this is an exact
nullspace over GF(p) in a polynomial box. Different instrument, same question.

THE METRIC IS OURS. Not transcribed: derived in steps 1-4b and back-substituted into the field
equations under three random gauge choices (_kt_dcs_verify2).

Repro:  .venv/bin/python scripts/_kt_dcs_carter.py [--prime 0] [--denpow 8] [--margin 10]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
from _kt_carter_space import arg, compatible_space, setup, x, y  # noqa: E402
from _kt_dcs_metric2 import even_ansatz, r, th, subs_series  # noqa: E402
from _kt_dcs_order2 import build_source, chi2_part  # noqa: E402

M = sp.Symbol("M", positive=True)
KMAX = 12
chi = KD.chi


def dcs_solution(verbose=True):
    """The O(zeta chi^2) even-parity correction, re-solved from the cached LHS, in a fixed gauge."""
    _, fs = even_ansatz()
    lines = open("data/dcs_lhs_srepr.txt").read().strip().split("\n")
    L, comps = {}, []
    for k in range(0, len(lines), 2):
        i, j = (int(v) for v in lines[k].split())
        L[(i, j)] = sp.sympify(lines[k + 1])
        comps.append((i, j))
    c2 = sp.Symbol("c2")
    ser, unk = {}, []
    for n in fs:
        cs = sp.symbols(f"{n}_0:{KMAX}")
        unk += list(cs)
        ser[n] = sum(cs[k] / r**(k + 1) for k in range(KMAX))
    Cs, Ts = build_source(verbose=False)
    u, sv = sp.Symbol("u"), sp.Symbol("sv")
    S_, C_ = sp.sin(th), sp.cos(th)

    def ang(num):
        e = sp.expand(sp.expand_trig(sp.sympify(num)).subs({S_: sv, C_: u}))
        A = B = sp.S.Zero
        for (k,), coef in sp.Poly(e, sv).terms():
            t_ = sp.expand(coef * (1 - u**2) ** (k // 2))
            B, A = (B + t_, A) if k % 2 else (B, A + t_)
        return [c for part in (sp.expand(A), sp.expand(B)) if part != 0
                for c in sp.Poly(part, u, r).coeffs()]

    eqs = []
    for i, j in comps:
        lhs = subs_series(L[(i, j)], fs, ser)
        rhs = chi2_part(Cs[i, j]) + c2 * chi2_part(Ts[i, j])
        eqs += ang(sp.expand(sp.numer(sp.cancel(sp.together(lhs - rhs)))))
    eqs = [e for e in eqs if e != 0]
    A_, b_ = sp.linear_eq_to_matrix(eqs, unk + [c2])
    sol = list(sp.linsolve((A_, b_), unk + [c2]))[0]
    subs0 = dict(zip(unk + [c2], sol))
    free = sorted({s for v in sol for s in v.free_symbols} & set(unk), key=str)
    # GAUGE FIX: every free coefficient to zero. This is a CHOICE and it is recorded as one; the
    # verification ran three random alternatives and all satisfied the field equations, so the
    # physics below cannot depend on it. Setting e2_* = 0 also removes the r-theta component, which
    # the Killing machinery's coordinates (t, x=r, y=cos th, phi) express most simply.
    g0 = {s: sp.S.Zero for s in free}
    vals = {k_: sp.simplify(v.subs(g0)) for k_, v in subs0.items()}
    vals.update(g0)
    if verbose:
        print(f"  solution re-derived: {len(eqs)} equations, {len(free)} gauge parameters set to 0",
              flush=True)
        print(f"  c2 = {sp.nsimplify(vals[c2])}", flush=True)
    out = {}
    for n in fs:
        cs = sp.symbols(f"{n}_0:{KMAX}")
        out[n] = sp.cancel(sum(vals[cs[k]] / r**(k + 1) for k in range(KMAX)))
    return out


def dcs_h_lower(fn):
    """h_ab in the Killing machinery's coordinates (t, x = r, y = cos th, phi), carrying chi^2.

    Conversions, stated because they are where a sign hides:
      h_yy   = h_(theta theta) / sin^2(th) = h_(theta theta) / (1 - y^2)
      P2     = (3 cos^2 th - 1)/2 = (3 y^2 - 1)/2
    The r-theta slot is absent by the gauge choice above (e2 = 0)."""
    P2y = (3 * y**2 - 1) / 2
    # M -> 1: the Killing machinery builds its Kerr background with M = 1 (kerr_chi_pieces), so a
    # deformation carrying symbolic M is in different units and _kt_prep chokes on it
    # (sp.Rational(94080*M**3)). Our derived solution is exact in M, so this is a unit choice, not
    # a truncation -- every coefficient is a rational number once M = 1.
    sub = {r: x, M: 1}
    a0, a2 = fn["a0"].subs(sub), fn["a2"].subs(sub)
    b0, b2 = fn["b0"].subs(sub), fn["b2"].subs(sub)
    c0, c2f = fn["c0"].subs(sub), fn["c2"].subs(sub)
    d0, d2 = fn["d0"].subs(sub), fn["d2"].subs(sub)
    h = sp.zeros(4, 4)
    h[0, 0] = chi**2 * (a0 + a2 * P2y)
    h[1, 1] = chi**2 * (b0 + b2 * P2y)
    h[2, 2] = chi**2 * (c0 + c2f * P2y) / (1 - y**2)
    h[3, 3] = chi**2 * (d0 + d2 * P2y) * (1 - y**2)
    return sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(h[i, j])))


if __name__ == "__main__":
    t0 = time.time()
    denpow, margin, prime = arg("--denpow", 8), arg("--margin", 10), arg("--prime", 0)
    print("dCS step 5: does Carter survive the derived O(zeta chi^2) dCS metric?\n", flush=True)
    fn = dcs_solution()
    h = dcs_h_lower(fn)
    nz = [(i, j) for i in range(4) for j in range(4) if h[i, j] != 0]
    print(f"  h_ab nonzero at {nz}  (r-theta absent by gauge)\n", flush=True)

    ctx = setup(2, denpow, margin, prime)
    print(f"  rank 2, L^{denpow}, box {ctx['dx']}x{ctx['dy']}, prime {prime}, "
          f"{ctx['Kc']} Kerr directions [{time.time()-t0:.0f}s]", flush=True)
    gi = KD.ginv_perturbation(ctx["GI"], h)
    W = compatible_space(ctx, ["dcs"], [gi])
    print(f"\n  CARTER SURVIVES AT RANK 2: {W.shape[0] == 1}", flush=True)
    print(f"  (compatible space dimension {W.shape[0]} of 1 deformation)", flush=True)
    print(f"\n  Owen-Yunes-Witek report no rank-2 Killing tensor at O(chi^2 zeta).", flush=True)
    print(f"  Independent agreement: {W.shape[0] == 0}", flush=True)
    print(f"\n  total {time.time()-t0:.0f}s")


def breakdown_at(rank_, denpow, margin, prime, h):
    """Survivors by leading power of Carter at a given rank, for one deformation."""
    from _kt_pole_check import breakdown_single
    ctx = setup(rank_, denpow, margin, prime)
    gi = KD.ginv_perturbation(ctx["GI"], h)
    return ctx, breakdown_single(ctx, gi)
