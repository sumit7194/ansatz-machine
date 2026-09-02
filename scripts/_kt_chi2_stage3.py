"""Stage 3: DERIVE the O(chi^2) dilaton from the scalar equation.

  beta * box(theta) = -(alpha/2) * G_GB          [normalisation fixed in _kt_sgb_verify: ratio 1/2]

At O(chi^2) the left side gets two contributions -- the Schwarzschild box acting on the unknown
theta^(2), AND the O(chi^2) part of the box operator acting on the known theta^(0). Dropping the
second would be an error no residual check downstream could see, so both are kept by simply
building box(theta) on the O(chi^2) background and extracting the chi^2 coefficient.

The source is READ from stage 2's output rather than transcribed from Eq. (16): it is the
Gauss-Bonnet invariant we computed ourselves, which equals Kretschmann because stage 1 confirmed
the background Ricci-flat to this order.
"""
import sys, time, pathlib
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

f = 1-2*m/r
g0 = sp.diag(-f, 1/f, r**2, r**2*sp.sin(th)**2)
gi0 = sp.diag(-1/f, f, 1/r**2, 1/(r**2*sp.sin(th)**2))
dg = sp.Matrix(4,4, lambda i,j: sp.expand(g[i,j]-g0[i,j]))
A = gi0*dg
gi = gi0 - A*gi0 + A*A*gi0 - A*A*A*gi0
gi = sp.Matrix(4,4, lambda i,j: tr(sp.expand(gi[i,j])))

# theta^(0), verified earlier against the scalar equation (ratio exactly 1/2, constant in r)
th0 = (1/(m*r))*(1 + m/r + sp.Rational(4,3)*m**2/r**2)
# Unknown O(chi^2) piece: an l=0 and an l=2 sector, series in m/r with undetermined coefficients.
NT = 8
p = sp.symbols(f"p0:{NT}"); q = sp.symbols(f"q0:{NT}")
P = sum(p[k]*m**k/r**(1+k) for k in range(NT))
Q = sum(q[k]*m**k/r**(1+k) for k in range(NT))
theta = th0 + chi**2*(P + Q*(3*sp.cos(th)**2 - 1))

t0=time.time()
# box(theta) = (1/sqrt(-g)) d_a ( sqrt(-g) g^ab d_b theta ), truncated to O(chi^2)
detg = sp.simplify(g.det())
sq = sp.sqrt(-detg)
box = sp.Integer(0)
for aa in range(4):
    inner = sp.Integer(0)
    for bb in range(4):
        inner += gi[aa,bb]*sp.diff(theta, X[bb])
    box += sp.diff(sq*inner, X[aa])
box = tr(sp.expand(sp.simplify(box/sq)))
lhs = sp.simplify(sp.diff(box, chi, 2).subs(chi, 0)/2)   # the chi^2 coefficient
print(f"  box(theta) at O(chi^2) built [{time.time()-t0:.0f}s]", flush=True)

gbf = pathlib.Path("data/kt_chi2_gb.txt")
if not gbf.exists():
    sys.exit("  stage 2 output missing -- run chi2_stage12 first (the source is OUR G_GB, not a transcription)")
GB = sp.sympify(gbf.read_text())
rhs_full = -sp.Rational(1,2)*GB          # beta*box = -(alpha/2) G_GB, with alpha/beta scaled out
rhs = sp.simplify(sp.diff(rhs_full, chi, 2).subs(chi, 0)/2)
print(f"  source at O(chi^2): {rhs}", flush=True)

resid = sp.simplify(lhs - rhs)
num = sp.numer(sp.together(sp.expand(resid)))
# Collect in BOTH r and cos(theta): the l=0 and l=2 sectors give independent equations.
c = sp.Symbol("c")
numc = sp.expand(num.subs(sp.cos(th), c))
eqs = []
pol = sp.Poly(numc, c)
for co in pol.all_coeffs():
    pr = sp.Poly(sp.expand(sp.numer(sp.together(co))), r)
    eqs.extend(pr.all_coeffs())
eqs = [sp.simplify(e) for e in eqs]
eqs = [e for e in eqs if e != 0]
sol = sp.solve(eqs, list(p)+list(q), dict=True)
print(f"\n  {len(eqs)} equations for {2*NT} unknowns", flush=True)
if not sol:
    sys.exit("  NO SOLUTION -- the assumed fall-off or sector structure is wrong. That is information.")
s = sol[0]
Psol = sp.simplify(P.subs(s)); Qsol = sp.simplify(Q.subs(s))
print(f"  l=0 part P(r) = {sp.factor(Psol)}")
print(f"  l=2 part Q(r) = {sp.factor(Qsol)}")
print(f"\n  theta^(2,1) = {sp.simplify(Psol + Qsol*(3*sp.cos(th)**2 - 1))}")
