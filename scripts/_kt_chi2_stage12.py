"""Stages 1-2 with truncation at every step -- gr_engine's eager simplify stalls with chi symbolic."""
import sys, time
sys.path.insert(0, '/Users/sumit/Github/conjecture_machine/scripts')
import sympy as sp

r, th = sp.symbols("r theta", positive=True)
t, ph = sp.symbols("t phi", real=True)
chi = sp.Symbol("chi")
m = sp.Symbol("m", positive=True)
X = [t, r, th, ph]
N = 2

def tr(e):
    e = sp.expand(e)
    return sp.Add(*[tm for tm in sp.Add.make_args(e) if sp.degree(tm, chi) <= N])

a = m*chi
Sig = r**2 + a**2*sp.cos(th)**2
Dl = r**2 - 2*m*r + a**2
gK = sp.zeros(4,4)
gK[0,0] = -(1 - 2*m*r/Sig)
gK[0,3] = gK[3,0] = -2*m*a*r*sp.sin(th)**2/Sig
gK[1,1] = Sig/Dl
gK[2,2] = Sig
gK[3,3] = (r**2 + a**2 + 2*m*a**2*r*sp.sin(th)**2/Sig)*sp.sin(th)**2
g = sp.Matrix(4,4, lambda i,j: sp.expand(sp.series(gK[i,j], chi, 0, N+1).removeO()))

t0=time.time()
# Perturbative inverse about Schwarzschild, truncated -- never invert the chi-dependent matrix.
f = 1-2*m/r
g0 = sp.diag(-f, 1/f, r**2, r**2*sp.sin(th)**2)
gi0 = sp.diag(-1/f, f, 1/r**2, 1/(r**2*sp.sin(th)**2))
dg = sp.Matrix(4,4, lambda i,j: sp.expand(g[i,j]-g0[i,j]))
A = gi0*dg
gi = gi0 - A*gi0 + A*A*gi0 - A*A*A*gi0
gi = sp.Matrix(4,4, lambda i,j: tr(sp.expand(gi[i,j])))
chk = sp.Matrix(4,4, lambda i,j: tr(sp.expand(sum(gi[i,k]*g[k,j] for k in range(4)))))
ok = all(sp.simplify(chk[i,j]-(1 if i==j else 0))==0 for i in range(4) for j in range(4))
print(f"  perturbative inverse verified to O(chi^{N}): {ok}  [{time.time()-t0:.0f}s]", flush=True)

Gam=[[[tr(sp.expand(sum(gi[a_,d]*(sp.diff(g[d,c],X[b])+sp.diff(g[d,b],X[c])-sp.diff(g[b,c],X[d]))
      for d in range(4))/2)) for c in range(4)] for b in range(4)] for a_ in range(4)]
print(f"  Christoffels [{time.time()-t0:.0f}s]", flush=True)

def ric(b,d):
    e=sum(sp.diff(Gam[a_][b][d],X[a_])-sp.diff(Gam[a_][b][a_],X[d]) for a_ in range(4))
    e+=sum(Gam[a_][a_][c]*Gam[c][b][d]-Gam[a_][d][c]*Gam[c][b][a_] for a_ in range(4) for c in range(4))
    return tr(sp.expand(e))

bad=[(i,j) for i in range(4) for j in range(i,4) if sp.simplify(sp.cancel(sp.together(ric(i,j))))!=0]
print(f"\nSTAGE 1: Ricci vanishes through O(chi^{N}): {not bad}  {bad if bad else ''}  [{time.time()-t0:.0f}s]", flush=True)

# STAGE 2: Kretschmann against Eq. (16) -- a free check using none of our downstream choices.
Riem=[[[[tr(sp.expand(sp.diff(Gam[a_][d][b],X[c])-sp.diff(Gam[a_][c][b],X[d])
        +sum(Gam[a_][c][e]*Gam[e][d][b]-Gam[a_][d][e]*Gam[e][c][b] for e in range(4))))
        for d in range(4)] for c in range(4)] for b in range(4)] for a_ in range(4)]
print(f"  Riemann [{time.time()-t0:.0f}s]", flush=True)
Rl=[[[[tr(sp.expand(sum(g[a_,e]*Riem[e][b][c][d] for e in range(4)))) for d in range(4)]
      for c in range(4)] for b in range(4)] for a_ in range(4)]
# Raise indices ONE AT A TIME. The single quadruple sum is 4^4 components x 4^4 products = 65536
# symbolic multiplies and does not finish; four single-index passes are 4 x 256 x 4 = 4096.
def raise_last(T, slot):
    out=[[[[None]*4 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a_ in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    idx=[a_,b,c,d]
                    acc=sp.Integer(0)
                    for e in range(4):
                        j=list(idx); j[slot]=e
                        acc+=gi[idx[slot],e]*T[j[0]][j[1]][j[2]][j[3]]
                    out[a_][b][c][d]=tr(sp.expand(acc))
    return out
Ru=Rl
for slot in (3,2,1,0):
    Ru=raise_last(Ru, slot)
    print(f"  raised index {slot} [{time.time()-t0:.0f}s]", flush=True)
Kr=tr(sp.expand(sum(Rl[a_][b][c][d]*Ru[a_][b][c][d] for a_ in range(4) for b in range(4)
                    for c in range(4) for d in range(4))))
target=48*m**2/r**6-1008*chi**2*m**4*sp.cos(th)**2/r**8
print(f"STAGE 2: Kretschmann matches Eq.(16): {sp.simplify(Kr-target)==0}  [{time.time()-t0:.0f}s]", flush=True)
print(f"  ours  = {sp.simplify(Kr)}")
# The Gauss-Bonnet invariant equals the Kretschmann scalar on a Ricci-flat background (R and
# R_ab both vanish to O(chi^2), confirmed in stage 1), so this doubles as the source term needed
# to derive the O(chi^2) dilaton -- it is an input, not only a check.
import pickle, pathlib
pathlib.Path("data/kt_chi2_gb.txt").write_text(sp.srepr(sp.simplify(Kr)))
print("  wrote the O(chi^2) Gauss-Bonnet invariant to data/kt_chi2_gb.txt", flush=True)
