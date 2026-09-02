#!/usr/bin/env python3
"""Stage 5: solve the O(zeta chi^2) field equations for the five Zerilli functions.

WHY RATIONAL-POINT EVALUATION AND NOT SYMBOLIC COLLECTION. The checkpointed Einstein tensor has
components of 500k-800k characters. Substituting a 50-coefficient series into those and collecting
in r and cos(theta) is the same shape as the two computations that burned 287 and 50 CPU-minutes
this session without finishing. But the equations are LINEAR in the unknown coefficients, so
evaluating the residual at exact RATIONAL points turns each point into linear equations with
rational coefficients -- arithmetic instead of symbolic normal forms. Enough independent points
over-determine the system, which is what lets a wrong ansatz FAIL rather than fit.

THE SOURCE is c1 D_ab + c2 T_ab at O(chi^2), with c1 = -2m^4, c2 = +2m^4 fixed by the static
verification, using the FULL dilaton theta^(0) + chi^2 theta^(2) derived in stage 3 and confirmed
in both sectors against independent hand calculations. D_ab keeps only 4 R_acbd grad^c grad^d theta
because stage 1 established the background is Ricci-flat THROUGH O(chi^2) -- checked, not assumed.

Repro:  .venv/bin/python scripts/_kt_chi2_stage5.py [--nterms 12] [--points 90]
"""
import os, sys, time, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp

r, th = sp.symbols("r theta", positive=True)
t, ph = sp.symbols("t phi", real=True)
zeta, chi = sp.symbols("zeta chi")
m = sp.Symbol("m", positive=True)
X = [t, r, th, ph]
f = 1 - 2*m/r
C1, C2 = -2*m**4, 2*m**4
TH0 = (1/(m*r))*(1 + m/r + sp.Rational(4,3)*m**2/r**2)
P_L0 = -(192*m**4 + 90*m**3*r + 40*m**2*r**2 + 15*m*r**3 + 15*r**4)/(60*m*r**5)
Q_L2 = -m*(48*m**2 + 21*m*r + 7*r**2)/(15*r**5)
Y2 = 3*sp.cos(th)**2 - 1
THETA = TH0 + chi**2*(P_L0 + Q_L2*Y2)


def tr(e, nz=1, nc=2):
    e = sp.expand(e)
    return sp.Add(*[x for x in sp.Add.make_args(e)
                    if sp.degree(x, zeta) <= nz and sp.degree(x, chi) <= nc])


def kerr_chi2():
    a = m*chi
    Sig = r**2 + a**2*sp.cos(th)**2; Dl = r**2 - 2*m*r + a**2
    gK = sp.zeros(4,4)
    gK[0,0] = -(1 - 2*m*r/Sig); gK[0,3] = gK[3,0] = -2*m*a*r*sp.sin(th)**2/Sig
    gK[1,1] = Sig/Dl; gK[2,2] = Sig
    gK[3,3] = (r**2 + a**2 + 2*m*a**2*r*sp.sin(th)**2/Sig)*sp.sin(th)**2
    return sp.Matrix(4,4, lambda i,j: sp.expand(sp.series(gK[i,j], chi, 0, 3).removeO()))


if __name__ == "__main__":
    NT = int(sys.argv[sys.argv.index("--nterms")+1]) if "--nterms" in sys.argv else 12
    NP = int(sys.argv[sys.argv.index("--points")+1]) if "--points" in sys.argv else 90
    t0 = time.time()

    # ---- the source, on the background only (no unknowns) ----
    g = kerr_chi2()
    g0 = sp.diag(-f, 1/f, r**2, r**2*sp.sin(th)**2)
    gi0 = sp.diag(-1/f, f, 1/r**2, 1/(r**2*sp.sin(th)**2))
    dg = sp.Matrix(4,4, lambda i,j: sp.expand(g[i,j]-g0[i,j])); A = gi0*dg
    gi = gi0 - A*gi0 + A*A*gi0 - A*A*A*gi0
    gi = sp.Matrix(4,4, lambda i,j: tr(sp.expand(gi[i,j]), 0, 2))
    Gam = [[[tr(sp.expand(sum(gi[a,d]*(sp.diff(g[d,c],X[b]) + sp.diff(g[d,b],X[c])
                                       - sp.diff(g[b,c],X[d])) for d in range(4))/2), 0, 2)
             for c in range(4)] for b in range(4)] for a in range(4)]
    Riem = [[[[tr(sp.expand(sp.diff(Gam[a][d][b],X[c]) - sp.diff(Gam[a][c][b],X[d])
              + sum(Gam[a][c][e]*Gam[e][d][b] - Gam[a][d][e]*Gam[e][c][b] for e in range(4))), 0, 2)
              for d in range(4)] for c in range(4)] for b in range(4)] for a in range(4)]
    print(f"  background curvature [{time.time()-t0:.0f}s]", flush=True)
    dth = [sp.diff(THETA, c) for c in X]
    hess = sp.Matrix(4,4, lambda a,b: tr(sp.expand(sp.diff(THETA,X[a],X[b])
                     - sum(Gam[c][a][b]*dth[c] for c in range(4))), 0, 2))
    hup = sp.Matrix(4,4, lambda c,d: tr(sp.expand(sum(gi[c,e]*gi[d,ff]*hess[e,ff]
                    for e in range(4) for ff in range(4))), 0, 2))
    Rl = [[[[tr(sp.expand(sum(g[a,e]*Riem[e][b][c][d] for e in range(4))), 0, 2)
             for d in range(4)] for c in range(4)] for b in range(4)] for a in range(4)]
    D = sp.Matrix(4,4, lambda a,b: tr(sp.expand(4*sum(Rl[a][c][b][d]*hup[c,d]
                  for c in range(4) for d in range(4))), 0, 2))
    sq = tr(sp.expand(sum(gi[a,b]*dth[a]*dth[b] for a in range(4) for b in range(4))), 0, 2)
    T = sp.Matrix(4,4, lambda a,b: tr(sp.expand(dth[a]*dth[b] - sp.Rational(1,2)*g[a,b]*sq), 0, 2))
    S = sp.Matrix(4,4, lambda a,b: sp.expand(sp.diff(C1*D[a,b] + C2*T[a,b], chi, 2).subs(chi,0)/2))
    print(f"  source at O(chi^2) [{time.time()-t0:.0f}s]", flush=True)

    # ---- the unknowns ----
    H02,H22,K2,H00,H20 = (sp.Function(n)(r) for n in ("H02","H22","K2","H00","H20"))
    cs = {}
    ser = {}
    for nm, fn in (("a",H02),("b",H22),("c",K2),("d",H00),("e",H20)):
        co = sp.symbols(f"{nm}0:{NT}")
        cs[nm] = list(co)
        ser[fn] = sum(co[k]*m**(k+1)/r**(1+k) for k in range(NT))
    UNK = [x for v in cs.values() for x in v]
    print(f"  {len(UNK)} unknown coefficients, {NT} terms per function", flush=True)

    LHS = {}
    for line in pathlib.Path("data/kt_chi2_stage4_lhs.txt").read_text().splitlines():
        k,_,v = line.partition(": ")
        LHS[eval(k)] = sp.sympify(v)
    print(f"  loaded checkpointed Einstein tensor [{time.time()-t0:.0f}s]", flush=True)

    import random
    rng = random.Random(20260903)
    eqs = []
    comps = [k for k in LHS if LHS[k] != 0]
    for k in comps:
        expr = LHS[k]
        for fn, s_ in ser.items():
            expr = expr.subs(fn, s_)
        expr = expr.doit() - S[k[0],k[1]]
        for _ in range(NP // len(comps) + 1):
            pt = {m: sp.Integer(1), r: sp.Rational(rng.randint(30,120),10),
                  th: sp.acos(sp.Rational(rng.randint(-9,9),10))}
            val = sp.expand(sp.together(expr.subs(pt)))
            if val != 0:
                eqs.append(sp.numer(sp.together(val)))
        print(f"    component {k} -> {len(eqs)} equations [{time.time()-t0:.0f}s]", flush=True)

    print(f"\n  {len(eqs)} equations for {len(UNK)} unknowns", flush=True)
    sol = sp.solve(eqs, UNK, dict=True)
    if not sol:
        sys.exit("  NO SOLUTION -- the Zerilli ansatz or the term count is wrong. That is information.")
    s_ = sol[0]
    for nm, fn in (("a",H02),("b",H22),("c",K2),("d",H00),("e",H20)):
        val = sp.cancel(sp.together(ser[fn].subs(s_)))
        print(f"  {fn.func.__name__}(r) = {sp.factor(val)}", flush=True)
