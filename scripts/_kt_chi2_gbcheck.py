"""Validate Eq. (16) against OUR OWN Riemann tensor, numerically at exact rational points.

WHY NOT THE FULL SYMBOLIC CONTRACTION. Raising all four indices and contracting symbolically ran
287 CPU-minutes without finishing -- the expression blows up even though the answer is two terms.
But the validation does not need the symbolic contraction: substituting exact RATIONAL values for
r, theta and m (keeping chi symbolic, since we want its chi^2 coefficient) turns the 256-term
contraction into arithmetic. Agreement at several independent points, for rational functions of
bounded degree, is decisive.

WHY Eq. (16) IS SAFE TO READ WHERE THE OTHER EQUATIONS WERE NOT. It is two terms with no nested
fractions -- 48m^2/r^6 and 1008 chi^2 m^4 cos^2(theta)/r^8 -- so the PDF extraction is unambiguous
here, unlike the ten-term series whose numerators and denominators interleave. Transcribe-then-
verify is the right trade when transcription is unambiguous AND verification is cheap; deriving
was the right trade when it was neither.
"""
import sys, time
sys.path.insert(0, '/Users/sumit/Github/conjecture_machine/scripts')
import sympy as sp

r, th = sp.symbols("r theta", positive=True)
t, ph = sp.symbols("t phi", real=True)
chi = sp.Symbol("chi"); m = sp.Symbol("m", positive=True)
X = [t, r, th, ph]; N = 2

def tr(e):
    e = sp.expand(e)
    return sp.Add(*[tm for tm in sp.Add.make_args(e) if sp.degree(tm, chi) <= N])

a = m*chi
Sig = r**2 + a**2*sp.cos(th)**2; Dl = r**2 - 2*m*r + a**2
gK = sp.zeros(4,4)
gK[0,0] = -(1 - 2*m*r/Sig); gK[0,3] = gK[3,0] = -2*m*a*r*sp.sin(th)**2/Sig
gK[1,1] = Sig/Dl; gK[2,2] = Sig
gK[3,3] = (r**2 + a**2 + 2*m*a**2*r*sp.sin(th)**2/Sig)*sp.sin(th)**2
g = sp.Matrix(4,4, lambda i,j: sp.expand(sp.series(gK[i,j], chi, 0, N+1).removeO()))
f = 1-2*m/r
g0 = sp.diag(-f, 1/f, r**2, r**2*sp.sin(th)**2)
gi0 = sp.diag(-1/f, f, 1/r**2, 1/(r**2*sp.sin(th)**2))
dg = sp.Matrix(4,4, lambda i,j: sp.expand(g[i,j]-g0[i,j]))
A = gi0*dg
gi = gi0 - A*gi0 + A*A*gi0 - A*A*A*gi0
gi = sp.Matrix(4,4, lambda i,j: tr(sp.expand(gi[i,j])))

t0=time.time()
Gam=[[[tr(sp.expand(sum(gi[a_,d]*(sp.diff(g[d,c],X[b])+sp.diff(g[d,b],X[c])-sp.diff(g[b,c],X[d]))
      for d in range(4))/2)) for c in range(4)] for b in range(4)] for a_ in range(4)]
Riem=[[[[tr(sp.expand(sp.diff(Gam[a_][d][b],X[c])-sp.diff(Gam[a_][c][b],X[d])
        +sum(Gam[a_][c][e]*Gam[e][d][b]-Gam[a_][d][e]*Gam[e][c][b] for e in range(4))))
        for d in range(4)] for c in range(4)] for b in range(4)] for a_ in range(4)]
print(f"  Riemann built [{time.time()-t0:.0f}s]", flush=True)

target = 48*m**2/r**6 - 1008*chi**2*m**4*sp.cos(th)**2/r**8
PTS = [{m: sp.Integer(1), r: sp.Integer(3), th: sp.pi/3},
       {m: sp.Integer(1), r: sp.Integer(5), th: sp.pi/4},
       {m: sp.Integer(2), r: sp.Integer(7), th: sp.pi/6},
       {m: sp.Rational(3,2), r: sp.Integer(4), th: sp.pi/3}]
ok = True
for n, pt in enumerate(PTS):
    gs = g.subs(pt); gis = gi.subs(pt)
    Rl = [[[[sp.nsimplify(sum(gs[a_,e]*Riem[e][b][c][d].subs(pt) for e in range(4)))
             for d in range(4)] for c in range(4)] for b in range(4)] for a_ in range(4)]
    Ru = [[[[sum(gis[a_,e]*gis[b,ff]*gis[c,gg]*gis[d,hh]*Rl[e][ff][gg][hh]
             for e in range(4) for ff in range(4) for gg in range(4) for hh in range(4))
             for d in range(4)] for c in range(4)] for b in range(4)] for a_ in range(4)]
    Kr = sp.expand(sum(Rl[a_][b][c][d]*Ru[a_][b][c][d]
                       for a_ in range(4) for b in range(4) for c in range(4) for d in range(4)))
    # compare only the chi^0 and chi^2 coefficients; chi^3+ is truncation debris
    ours0 = sp.simplify(Kr.subs(chi,0)); ours2 = sp.simplify(sp.diff(Kr,chi,2).subs(chi,0)/2)
    tg = target.subs(pt)
    tg0 = sp.simplify(tg.subs(chi,0)); tg2 = sp.simplify(sp.diff(tg,chi,2).subs(chi,0)/2)
    good = (sp.simplify(ours0-tg0)==0 and sp.simplify(ours2-tg2)==0)
    ok &= good
    print(f"  point {n}: chi^0 {ours0} vs {tg0} | chi^2 {ours2} vs {tg2} -> {'MATCH' if good else 'DIFFER'}",
          flush=True)
print(f"\n  Eq.(16) confirmed against our own Riemann at {len(PTS)} points: {ok}  [{time.time()-t0:.0f}s]",
      flush=True)
