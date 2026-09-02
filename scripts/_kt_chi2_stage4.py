"""Stage 4: solve the O(zeta chi^2) field equation in ZERILLI GAUGE for the five unknown functions.

THE ANSATZ, taken from the paper's Eq. (23) rather than from memory of Hartle-Thorne. The
even-parity, stationary, axisymmetric, m=0 sector has five independent components; two gauge
degrees of freedom are fixed by Zerilli gauge, leaving three radial functions per multipole:

    h_tt = f H0_l(r) Y_l      h_rr = H2_l(r) Y_l / f
    h_thth = r^2 K_l(r) Y_l   h_phiphi = r^2 sin^2(theta) K_l(r) Y_l

with l = 0 and l = 2, Y_0 = 1 and Y_2 = 3cos^2(theta) - 1.

THE RESIDUAL GAUGE. One freedom survives in the l = 0 sector -- it is a redefinition of the
spherical areal radius -- and the paper fixes it with K_00 = 0. Leaving it unfixed makes the
linear system DEGENERATE (a one-parameter family of solutions), which would not look like an
error: it would look like an answer with a free constant. So it is imposed explicitly.

WHY THE WHOLE EINSTEIN TENSOR AND NOT G^[1] SEPARATELY. The paper splits G into linear, quadratic
and cubic pieces in the perturbation and moves the nonlinear ones into the source. Computing the
FULL Einstein tensor of the FULL metric and extracting the O(zeta chi^2) coefficient captures all
of those automatically -- the cross terms between the static correction, the frame-dragging term
and the chi^2 background are physically present, and assembling the source by hand is where one of
them would go missing unnoticed.
"""
import sys, time, pathlib
sys.path.insert(0, '/Users/sumit/Github/conjecture_machine/scripts')
import sympy as sp

r, th = sp.symbols("r theta", positive=True)
t, ph = sp.symbols("t phi", real=True)
zeta, chi = sp.symbols("zeta chi")
m = sp.Symbol("m", positive=True)
X = [t, r, th, ph]
f = 1 - 2*m/r

def tr(e):
    """Keep only zeta^0..1 and chi^0..2."""
    e = sp.expand(e)
    return sp.Add(*[tm for tm in sp.Add.make_args(e)
                    if sp.degree(tm, zeta) <= 1 and sp.degree(tm, chi) <= 2])

# --- known pieces -------------------------------------------------------------------
DG_TT = -(m**3)/(3*r**3)*(1 + 26*m/r + sp.Rational(66,5)*m**2/r**2
                          + sp.Rational(96,5)*m**3/r**3 - 80*m**4/r**4)
DG_RR = -(m**2)/(f**2*r**2)*(1 + m/r + sp.Rational(52,3)*m**2/r**2 + 2*m**3/r**3
                             + sp.Rational(16,5)*m**4/r**4 - sp.Rational(368,3)*m**5/r**5)
# the O(zeta chi) piece WE derived (commit 64ef0c2), not transcribed
W_ROT = m**4*(9*r**4 + 140*m*r**3 + 90*m**2*r**2 + 144*m**3*r - 400*m**4)/(15*r**7)

# --- unknowns: three functions at l=2, two at l=0 (K_00 = 0 by residual gauge) --------
NT = 10
def ser(sym):
    c = sp.symbols(f"{sym}0:{NT}")
    return sum(c[k]*m**k/r**k for k in range(NT)), list(c)
H0_2, cH02 = ser("a"); H2_2, cH22 = ser("b"); K_2, cK2 = ser("c")
H0_0, cH00 = ser("d"); H2_0, cH20 = ser("e")
K_0 = sp.Integer(0)                      # residual gauge: K_00 = 0
UNK = cH02 + cH22 + cK2 + cH00 + cH20

Y0, Y2 = sp.Integer(1), 3*sp.cos(th)**2 - 1
h = sp.zeros(4,4)
h[0,0] = f*(H0_0*Y0 + H0_2*Y2)
h[1,1] = (H2_0*Y0 + H2_2*Y2)/f
h[2,2] = r**2*(K_0*Y0 + K_2*Y2)
h[3,3] = r**2*sp.sin(th)**2*(K_0*Y0 + K_2*Y2)

# --- the full metric to O(zeta chi^2) ------------------------------------------------
a_ = m*chi
Sig = r**2 + a_**2*sp.cos(th)**2
Dl = r**2 - 2*m*r + a_**2
gK = sp.zeros(4,4)
gK[0,0] = -(1 - 2*m*r/Sig)
gK[0,3] = gK[3,0] = -2*m*a_*r*sp.sin(th)**2/Sig
gK[1,1] = Sig/Dl
gK[2,2] = Sig
gK[3,3] = (r**2 + a_**2 + 2*m*a_**2*r*sp.sin(th)**2/Sig)*sp.sin(th)**2
g = sp.Matrix(4,4, lambda i,j: sp.expand(sp.series(gK[i,j], chi, 0, 3).removeO()))
g[0,0] += zeta*DG_TT
g[1,1] += zeta*DG_RR
g[0,3] += zeta*chi*W_ROT*sp.sin(th)**2
g[3,0] = g[0,3]
for i in range(4):
    for j in range(4):
        g[i,j] = g[i,j] + zeta*chi**2*h[i,j]

print("stage 4: metric assembled; unknowns =", len(UNK), flush=True)
print("  (H0,H2,K at l=2; H0,H2 at l=0; K_00 = 0 by residual gauge)", flush=True)
