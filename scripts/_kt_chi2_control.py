#!/usr/bin/env python3
"""KNOWN-ANSWER CONTROL for the stage-5 solver: can it recover the STATIC sGB correction?

Three NO SOLUTION verdicts at O(chi^2) have each been blamed on the ansatz and twice that blame was
wrong. Before adjusting it a fourth time, this asks whether the SOLVER works at all, on the one case
whose answer is already verified: the O(zeta chi^0) static correction, confirmed against the EdGB
field equations in _kt_sgb_verify (c1 = -2m^4, c2 = +2m^4, four components, residuals zero).

Same machinery -- unknown radial functions in Zerilli form, source c1 D + c2 T, residual evaluated
at exact rational points, linear solve -- but at chi^0 where the target is known. If it cannot
recover DG_TT and DG_RR, the fault is in the solver and no amount of ansatz-widening at O(chi^2)
will help. If it can, the fault is upstairs and the O(chi^2) structure is the suspect.

This is the discipline the project already paid for once: validate the prover on a KNOWN-NONZERO
case before trusting a null from it.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp

r, th = sp.symbols("r theta", positive=True)
t, ph = sp.symbols("t phi", real=True)
zeta = sp.Symbol("zeta"); m = sp.Symbol("m", positive=True)
X = [t, r, th, ph]
f = 1 - 2*m/r
C1, C2 = -2*m**4, 2*m**4
TH0 = (1/(m*r))*(1 + m/r + sp.Rational(4,3)*m**2/r**2)
TARGET_TT = -(m**3)/(3*r**3)*(1 + 26*m/r + sp.Rational(66,5)*m**2/r**2
                              + sp.Rational(96,5)*m**3/r**3 - 80*m**4/r**4)
TARGET_RR = -(m**2)/(f**2*r**2)*(1 + m/r + sp.Rational(52,3)*m**2/r**2 + 2*m**3/r**3
                                 + sp.Rational(16,5)*m**4/r**4 - sp.Rational(368,3)*m**5/r**5)

def tr(e):
    e = sp.expand(e)
    return sp.Add(*[x for x in sp.Add.make_args(e) if sp.degree(x, zeta) <= 1])

if __name__ == "__main__":
    NT = int(sys.argv[sys.argv.index("--nterms")+1]) if "--nterms" in sys.argv else 13
    NP = int(sys.argv[sys.argv.index("--points")+1]) if "--points" in sys.argv else 80
    t0 = time.time()
    A, B = 8, 4
    H0f, H2f = sp.Function("H0")(r), sp.Function("H2")(r)
    ca = sp.symbols(f"a0:{NT}"); cb = sp.symbols(f"b0:{NT}")
    serH0 = sum(ca[k]*m**(A+B-k)*r**k for k in range(NT))/(r**A*(r-2*m)**B)
    serH2 = sum(cb[k]*m**(A+B-k)*r**k for k in range(NT))/(r**A*(r-2*m)**B)
    UNK = list(ca)+list(cb)

    g0 = sp.diag(-f, 1/f, r**2, r**2*sp.sin(th)**2)
    gi0 = sp.diag(-1/f, f, 1/r**2, 1/(r**2*sp.sin(th)**2))
    g = sp.Matrix(g0)
    g[0,0] = -f + zeta*f*H0f
    g[1,1] = 1/f + zeta*H2f/f
    dg = sp.Matrix(4,4, lambda i,j: sp.expand(g[i,j]-g0[i,j])); Am = gi0*dg
    gi = gi0 - Am*gi0 + Am*Am*gi0
    gi = sp.Matrix(4,4, lambda i,j: tr(sp.expand(gi[i,j])))
    Gam = [[[tr(sp.expand(sum(gi[a,d]*(sp.diff(g[d,c],X[b]) + sp.diff(g[d,b],X[c])
                                       - sp.diff(g[b,c],X[d])) for d in range(4))/2))
             for c in range(4)] for b in range(4)] for a in range(4)]
    def ric(b,d):
        e = sum(sp.diff(Gam[a][b][d],X[a]) - sp.diff(Gam[a][b][a],X[d]) for a in range(4))
        e += sum(Gam[a][a][c]*Gam[c][b][d] - Gam[a][d][c]*Gam[c][b][a]
                 for a in range(4) for c in range(4))
        return tr(sp.expand(e))
    Ric = {(a,b): ric(a,b) for a in range(4) for b in range(a,4)}
    Rs = tr(sp.expand(sum(gi[a,b]*Ric[(min(a,b),max(a,b))] for a in range(4) for b in range(4))))
    LHS = {k: sp.expand(sp.diff(tr(sp.expand(Ric[k] - sp.Rational(1,2)*g[k[0],k[1]]*Rs)),
                                zeta).subs(zeta,0)) for k in Ric}
    print(f"  O(zeta) Einstein tensor [{time.time()-t0:.0f}s]", flush=True)

    # source on Schwarzschild with theta^(0)
    Gam0 = [[[sp.cancel(sp.together(sum(gi0[a,d]*(sp.diff(g0[d,c],X[b]) + sp.diff(g0[d,b],X[c])
                                                  - sp.diff(g0[b,c],X[d])) for d in range(4))/2))
              for c in range(4)] for b in range(4)] for a in range(4)]
    Riem0=[[[[sp.cancel(sp.together(sp.diff(Gam0[a][d][b],X[c]) - sp.diff(Gam0[a][c][b],X[d])
            + sum(Gam0[a][c][e]*Gam0[e][d][b]-Gam0[a][d][e]*Gam0[e][c][b] for e in range(4))))
            for d in range(4)] for c in range(4)] for b in range(4)] for a in range(4)]
    dth=[sp.diff(TH0,c) for c in X]
    hess=sp.Matrix(4,4,lambda a,b: sp.diff(TH0,X[a],X[b])-sum(Gam0[c][a][b]*dth[c] for c in range(4)))
    hup=sp.Matrix(4,4,lambda c,d: sum(gi0[c,e]*gi0[d,ff]*hess[e,ff] for e in range(4) for ff in range(4)))
    Rl=[[[[sum(g0[a,e]*Riem0[e][b][c][d] for e in range(4)) for d in range(4)]
          for c in range(4)] for b in range(4)] for a in range(4)]
    D=sp.Matrix(4,4,lambda a,b: 4*sum(Rl[a][c][b][d]*hup[c,d] for c in range(4) for d in range(4)))
    sq=sum(gi0[a,b]*dth[a]*dth[b] for a in range(4) for b in range(4))
    T=sp.Matrix(4,4,lambda a,b: dth[a]*dth[b]-sp.Rational(1,2)*g0[a,b]*sq)
    S=sp.Matrix(4,4,lambda a,b: sp.cancel(sp.together(C1*D[a,b]+C2*T[a,b])))
    print(f"  source [{time.time()-t0:.0f}s]", flush=True)

    import random
    rng=random.Random(7)
    eqs=[]
    for k in [c for c in LHS if LHS[c]!=0]:
        expr = LHS[k].subs(H0f,serH0).subs(H2f,serH2).doit() - S[k[0],k[1]]
        for _ in range(NP//4+1):
            pt={m:sp.Integer(1), r:sp.Rational(rng.randint(30,140),10), th:sp.pi/3}
            v=sp.expand(sp.together(expr.subs(pt)))
            if v!=0: eqs.append(sp.numer(sp.together(v)))
    # BOUNDARY CONDITIONS. Without these the solve returns a FAMILY, not an answer: the control
    # recovered the correct particular solution plus a12*f + b11*m/r, two homogeneous modes.
    #   asymptotic flatness  -> the correction must vanish as r -> infinity, killing a12*f
    #   physical mass        -> no 1/r term in the g_tt correction, killing b11*m/r
    # Both conditions were written into the stage-4 docstring and neither was implemented.
    u = sp.Symbol("u", positive=True)          # u = 1/r, so r -> oo is u -> 0
    for corr in (f*serH0, serH2/f):
        ser_u = sp.series(corr.subs(r, 1/u).subs(m, 1), u, 0, 3).removeO()
        pu = sp.Poly(sp.expand(ser_u), u)
        for pw in (0, 1):                       # u^0 = constant at infinity; u^1 = the 1/r term
            co = pu.coeff_monomial(u**pw) if pw else pu.coeff_monomial(1)
            if co != 0:
                eqs.append(sp.numer(sp.together(co)))
    print(f"  {len(eqs)} equations for {len(UNK)} unknowns (incl. boundary conditions) "
          f"[{time.time()-t0:.0f}s]", flush=True)
    sol=sp.solve(eqs,UNK,dict=True)
    if not sol:
        sys.exit("\n  CONTROL FAILED: the solver cannot recover the KNOWN static solution. The fault "
                 "is in the solver, not in the O(chi^2) ansatz -- widening that further is wasted.")
    s_=sol[0]
    gotH0=sp.cancel(sp.together(serH0.subs(s_))); gotH2=sp.cancel(sp.together(serH2.subs(s_)))
    okH0 = sp.cancel(sp.together(f*gotH0 - TARGET_TT))==0
    okH2 = sp.cancel(sp.together(gotH2/f - TARGET_RR))==0
    print(f"  g_tt correction recovered: {okH0}")
    print(f"  g_rr correction recovered: {okH2}")
    if okH0 and okH2:
        print("\n  CONTROL PASSED: the solver recovers the verified static solution, so the "
              "machinery is sound and the O(chi^2) structure is the suspect.")
    else:
        print(f"\n  CONTROL FAILED ON VALUES: solved, but not to the known answer.")
        print(f"    got f*H0 = {sp.factor(sp.cancel(f*gotH0))}")
        print(f"    want     = {sp.factor(TARGET_TT)}")
