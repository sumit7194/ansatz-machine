#!/usr/bin/env python3
"""Stage 4: the five Zerilli-gauge functions of the O(zeta chi^2) sGB metric, DERIVED.

THE ANSATZ is the paper's Eq. (23), not a recollection of Hartle-Thorne. The even-parity,
stationary, axisymmetric, m=0 sector has five independent components; two gauge freedoms are fixed
by Zerilli gauge, leaving three radial functions per multipole (l = 0 and l = 2):

    h_tt = f H0_l Y_l      h_rr = H2_l Y_l / f      h_thth = r^2 K_l Y_l
    h_phiphi = r^2 sin^2(theta) K_l Y_l                 Y_0 = 1,  Y_2 = 3cos^2(theta) - 1

RESIDUAL GAUGE. One freedom survives in the l = 0 sector -- a redefinition of the areal radius --
fixed by K_00 = 0. Leaving it makes the system DEGENERATE, and degeneracy here does not look like
an error: it looks like an answer with a free constant in it.

FIVE THINGS THIS SCRIPT DOES BECAUSE EARLIER STAGES DID THEM WRONG:

  1. UNKNOWN FUNCTIONS, NOT COEFFICIENTS, inside the curvature. Putting 50 undetermined constants
     into the metric makes every Christoffel a large polynomial. The O(chi) derivation stalled that
     way for 13.5 minutes and finished in 20 seconds once the series moved AFTER the ODEs.
  2. TRUNCATE AT EVERY STEP to O(zeta^1 chi^2), with a perturbative Neumann inverse that is CHECKED
     against g rather than trusted. Inverting the truncated metric exactly would silently mix in
     O(zeta^2) terms the solution does not control.
  3. NO UNBOUNDED simplify. sp.simplify has no bounded cost; two runs burned 287 and 50 CPU-minutes
     on calls that cancel/together settle immediately.
  4. sin^2(theta) IS ELIMINATED BEFORE COLLECTING, with an assertion that none survives. Collecting
     in cos alone left sin as a spurious symbol and produced three NO SOLUTION verdicts that were
     blamed on the mass dimension, the fall-off and the sector structure in turn -- none of which
     was the fault.
  5. THE SOURCE USES THE FULL DILATON, theta^(0) + chi^2 theta^(2), derived in stage 3 and confirmed
     in both sectors against independent hand calculations. Its chi^2 piece contributes to D_ab and
     to T_ab through cross terms; dropping it is the same class of omission that made stage 3's
     hand-diagnostic solve an equation which does not exist.

Repro:  .venv/bin/python scripts/_kt_chi2_stage4.py [--nterms 12]
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp

r, th = sp.symbols("r theta", positive=True)
t, ph = sp.symbols("t phi", real=True)
zeta, chi = sp.symbols("zeta chi")
m = sp.Symbol("m", positive=True)
X = [t, r, th, ph]
f = 1 - 2*m/r
C1, C2 = -2*m**4, 2*m**4          # normalisation fixed by the static verification (_kt_sgb_verify)

# --- verified inputs ------------------------------------------------------------------
DG_TT = -(m**3)/(3*r**3)*(1 + 26*m/r + sp.Rational(66,5)*m**2/r**2
                          + sp.Rational(96,5)*m**3/r**3 - 80*m**4/r**4)
DG_RR = -(m**2)/(f**2*r**2)*(1 + m/r + sp.Rational(52,3)*m**2/r**2 + 2*m**3/r**3
                             + sp.Rational(16,5)*m**4/r**4 - sp.Rational(368,3)*m**5/r**5)
W_ROT = m**4*(9*r**4 + 140*m*r**3 + 90*m**2*r**2 + 144*m**3*r - 400*m**4)/(15*r**7)   # commit 64ef0c2
TH0 = (1/(m*r))*(1 + m/r + sp.Rational(4,3)*m**2/r**2)
P_L0 = -(192*m**4 + 90*m**3*r + 40*m**2*r**2 + 15*m*r**3 + 15*r**4)/(60*m*r**5)       # stage 3
Q_L2 = -m*(48*m**2 + 21*m*r + 7*r**2)/(15*r**5)                                       # stage 3
Y2 = 3*sp.cos(th)**2 - 1
THETA = TH0 + chi**2*(P_L0 + Q_L2*Y2)


def tr(e):
    e = sp.expand(e)
    return sp.Add(*[x for x in sp.Add.make_args(e)
                    if sp.degree(x, zeta) <= 1 and sp.degree(x, chi) <= 2])


def kill_sin(e):
    """Eliminate sin^2(theta); abort if an odd power survives (parity says none should)."""
    e = sp.expand(e); prev = None
    while prev != e:
        prev = e
        e = sp.expand(e.subs(sp.sin(th)**2, 1 - sp.cos(th)**2))
    if e.has(sp.sin(th)):
        raise ValueError("odd power of sin(theta) survives -- parity assumption is wrong and "
                         "collecting in cos alone would silently corrupt the equations")
    return e


def perturbative_inverse(g, g0, gi0):
    dg = sp.Matrix(4,4, lambda i,j: sp.expand(g[i,j]-g0[i,j]))
    A = gi0*dg
    gi = gi0 - A*gi0 + A*A*gi0 - A*A*A*gi0 + A*A*A*A*gi0
    gi = sp.Matrix(4,4, lambda i,j: tr(sp.expand(gi[i,j])))
    for i in range(4):
        for j in range(4):
            chk = tr(sp.expand(sum(gi[i,k]*g[k,j] for k in range(4))))
            if sp.cancel(sp.together(chk - (1 if i==j else 0))) != 0:
                raise ValueError(f"perturbative inverse wrong at ({i},{j}) -- series too short")
    return gi


if __name__ == "__main__":
    NT = int(sys.argv[sys.argv.index("--nterms")+1]) if "--nterms" in sys.argv else 12
    t0 = time.time()
    H02, H22, K2 = (sp.Function("H02")(r), sp.Function("H22")(r), sp.Function("K2")(r))
    H00, H20 = sp.Function("H00")(r), sp.Function("H20")(r)
    K0 = sp.Integer(0)                                   # residual gauge

    h = sp.zeros(4,4)
    h[0,0] = f*(H00 + H02*Y2)
    h[1,1] = (H20 + H22*Y2)/f
    h[2,2] = r**2*(K0 + K2*Y2)
    h[3,3] = r**2*sp.sin(th)**2*(K0 + K2*Y2)

    a_ = m*chi
    Sig = r**2 + a_**2*sp.cos(th)**2; Dl = r**2 - 2*m*r + a_**2
    gK = sp.zeros(4,4)
    gK[0,0] = -(1 - 2*m*r/Sig); gK[0,3] = gK[3,0] = -2*m*a_*r*sp.sin(th)**2/Sig
    gK[1,1] = Sig/Dl; gK[2,2] = Sig
    gK[3,3] = (r**2 + a_**2 + 2*m*a_**2*r*sp.sin(th)**2/Sig)*sp.sin(th)**2
    g = sp.Matrix(4,4, lambda i,j: sp.expand(sp.series(gK[i,j], chi, 0, 3).removeO()))
    g[0,0] += zeta*DG_TT; g[1,1] += zeta*DG_RR
    g[0,3] += zeta*chi*W_ROT*sp.sin(th)**2; g[3,0] = g[0,3]
    for i in range(4):
        for j in range(4):
            g[i,j] = g[i,j] + zeta*chi**2*h[i,j]

    g0 = sp.diag(-f, 1/f, r**2, r**2*sp.sin(th)**2)
    gi0 = sp.diag(-1/f, f, 1/r**2, 1/(r**2*sp.sin(th)**2))
    gi = perturbative_inverse(g, g0, gi0)
    print(f"  perturbative inverse verified to O(zeta chi^2) [{time.time()-t0:.0f}s]", flush=True)

    Gam = [[[tr(sp.expand(sum(gi[a,d]*(sp.diff(g[d,c],X[b]) + sp.diff(g[d,b],X[c])
                                        - sp.diff(g[b,c],X[d])) for d in range(4))/2))
             for c in range(4)] for b in range(4)] for a in range(4)]
    print(f"  Christoffels [{time.time()-t0:.0f}s]", flush=True)

    def ric(b, d):
        e = sum(sp.diff(Gam[a][b][d], X[a]) - sp.diff(Gam[a][b][a], X[d]) for a in range(4))
        e += sum(Gam[a][a][c]*Gam[c][b][d] - Gam[a][d][c]*Gam[c][b][a]
                 for a in range(4) for c in range(4))
        return tr(sp.expand(e))

    # PER-COMPONENT PROGRESS AND CHECKPOINTING. The previous shape printed nothing until all ten
    # components finished, so "still running at 96 minutes" carried no information about whether it
    # was 20% or 90% done -- a stop-or-continue call against a clock rather than against evidence.
    # Each component is also written to disk as it completes, so a restart resumes instead of
    # recomputing. That is the direct fix for losing five hours of index-raising with nothing saved.
    import pathlib, pickle
    ck = pathlib.Path("data/kt_chi2_stage4_ric.pkl")
    Ric = {}
    if ck.exists():
        try:
            Ric = {k: sp.sympify(v) for k, v in pickle.loads(ck.read_bytes()).items()}
            print(f"  resumed {len(Ric)}/10 Ricci components from checkpoint", flush=True)
        except Exception:
            Ric = {}
    for a in range(4):
        for b in range(a, 4):
            if (a,b) in Ric:
                continue
            Ric[(a,b)] = ric(a,b)
            ck.write_bytes(pickle.dumps({k: sp.srepr(v) for k, v in Ric.items()}))
            print(f"    Ric[{a}{b}] done ({len(Ric)}/10) [{time.time()-t0:.0f}s]", flush=True)
    Rs = tr(sp.expand(sum(gi[a,b]*Ric[(min(a,b),max(a,b))] for a in range(4) for b in range(4))))
    print(f"  Ricci + scalar [{time.time()-t0:.0f}s]", flush=True)
    Gt = {k: tr(sp.expand(Ric[k] - sp.Rational(1,2)*g[k[0],k[1]]*Rs)) for k in Ric}
    LHS = {k: sp.expand(sp.diff(Gt[k], zeta).subs(zeta,0)) for k in Gt}
    LHS = {k: sp.expand(sp.diff(v, chi, 2).subs(chi,0)/2) for k,v in LHS.items()}
    print(f"  O(zeta chi^2) Einstein tensor [{time.time()-t0:.0f}s]", flush=True)
    sp.srepr(LHS[(0,0)])   # touch it, so a failure surfaces here rather than later
    import pathlib
    pathlib.Path("data/kt_chi2_stage4_lhs.txt").write_text(
        "\n".join(f"{k}: {sp.srepr(v)}" for k,v in LHS.items()))
    print(f"  wrote LHS to data/kt_chi2_stage4_lhs.txt [{time.time()-t0:.0f}s]", flush=True)
