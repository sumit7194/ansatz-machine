#!/usr/bin/env python3
"""Verify the derived O(zeta chi^2) metric at points NOT used in the solve.

The solve imposed the field equations at 220 sampled points. Checking the answer at those same
points proves nothing about the rest of the domain. This evaluates the residual at FRESH rational
points, with a different seed and a different radial range, which is the difference between "fits
where it was fitted" and "satisfies the equation".

The system was over-determined 231 equations to 90 unknowns, so overfitting is not possible in
principle -- but that argument is about the linear algebra, and this checks the object.
"""
import os, sys, time, pathlib, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp

r, th = sp.symbols("r theta", positive=True)
m = sp.Symbol("m", positive=True)
zeta, chi = sp.symbols("zeta chi")
f = 1 - 2*m/r

H02 = -m**3*(-8820000*m**8 + 8173200*m**7*r + 15803900*m**6*r**2 - 4198950*m**5*r**3 - 4061710*m**4*r**4 - 2275145*m**3*r**5 + 164874*m**2*r**6 + 187446*m*r**7 + 187446*r**8)/(110250*r**10*(-2*m + r))
H22 = -m**3*(149940000*m**8 - 201978000*m**7*r + 101014900*m**6*r**2 - 18766650*m**5*r**3 + 11833890*m**4*r**4 - 7545095*m**3*r**5 - 55626*m**2*r**6 + 150696*m*r**7 + 187446*r**8)/(110250*r**10*(-2*m + r))
K2  = -m**3*(8820000*m**7 - 6213200*m**6*r - 3416700*m**5*r**2 - 1855650*m**4*r**3 + 887110*m**3*r**4 + 800733*m**2*r**5 + 435540*m*r**6 + 187446*r**7)/(110250*r**10)
H00 =  m**3*(800*m**7 - 11264*m**6*r + 2172*m**5*r**2 + 1020*m**4*r**3 + 1214*m**3*r**4 + 156*m**2*r**5 + 210*m*r**6 + 15*r**7)/(90*r**9*(-2*m + r))
H20 =  m**2*(8000*m**9 + 25312*m**8*r - 22664*m**7*r**2 - 724*m**6*r**3 + 640*m**5*r**4 + 1090*m**4*r**5 - 180*m**3*r**6 + 150*m**2*r**7 - 15*m*r**8 + 15*r**9)/(30*r**9*(-2*m + r)**2)

if __name__ == "__main__":
    t0 = time.time()
    S = sp.zeros(4,4)
    for line in pathlib.Path("data/kt_chi2_stage5_src.txt").read_text().splitlines():
        k,_,v = line.partition(": ")
        a,b = (int(x) for x in k.split(",")); S[a,b] = sp.sympify(v)
    LHS = {}
    for line in pathlib.Path("data/kt_chi2_stage4_lhs.txt").read_text().splitlines():
        k,_,v = line.partition(": ")
        LHS[eval(k)] = sp.sympify(v)
    print(f"  loaded checkpoints [{time.time()-t0:.0f}s]", flush=True)

    subs = {sp.Function("H02")(r): H02, sp.Function("H22")(r): H22, sp.Function("K2")(r): K2,
            sp.Function("H00")(r): H00, sp.Function("H20")(r): H20}
    rng = random.Random(31415)                  # DIFFERENT seed from the solve (20260903)
    bad = 0; tot = 0
    for k in [c for c in LHS if LHS[c] != 0]:
        expr = LHS[k]
        for fn, v in subs.items():
            expr = expr.subs(fn, v)
        expr = expr.doit() - S[k[0],k[1]]
        for _ in range(12):
            # DIFFERENT radial range too: the solve used r in [3,12], this uses [13,40].
            pt = {m: sp.Integer(1), r: sp.Rational(rng.randint(130,400),10),
                  th: sp.acos(sp.Rational(rng.randint(-9,9),10))}
            v = sp.cancel(sp.together(expr.subs(pt)))
            tot += 1
            if v != 0:
                bad += 1
                if bad <= 3:
                    print(f"    RESIDUAL NONZERO at {k}, r={pt[r]}: {v}", flush=True)
        print(f"    {k}: checked [{time.time()-t0:.0f}s]", flush=True)
    print(f"\n  {tot-bad}/{tot} fresh-point residuals vanish", flush=True)
    print("  VERIFIED: the derived metric satisfies the O(zeta chi^2) field equations at points "
          "outside the solve's sample." if bad == 0 else
          f"  FAILED: {bad} nonzero residuals at fresh points -- the solution does not hold "
          f"off the fitted sample.", flush=True)
