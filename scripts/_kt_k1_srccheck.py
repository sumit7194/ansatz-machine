"""Definitive source check: is {H_deformed, chain4 + eps*K1} = O(eps^2)?
Exact, symbolic, in the code's own conventions -- no geodesics, no transit."""
import sys, time; sys.path.insert(0,'/Users/sumit/Github/conjecture_machine/scripts')
import sympy as sp
import _kt_double as KD, _kt_search as K, _kt_perturb as PB
from _kt_carter_space import build_space, setup, x, y
from _kt_q2_candidate import combine
chi = KD.chi
t0=time.time()
ctx = setup(2, 8, 10, 0)
mons = K.monomials(2); Pt,Px,Py,Pph = K.MOM
A_COEF={"l2tt_2":1,"l2tt_5":-32,"l2tt_6":48,"l2rr_3":4,"l2rr_4":-84,
        "l2ang_3":4,"l2ang_4":8,"l2ang_5":-48}
names,gis,roles = build_space(ctx["GI"], 6, slots=("l2tt","l2rr","l2ang"))
keep=[i for i,r_ in enumerate(roles) if r_=="slot"]
names=[names[i] for i in keep]; gis=[gis[i] for i in keep]
dgi = combine(gis,[sp.Rational(A_COEF.get(n,0)) for n in names])
H  = [KD.hamiltonian(g) for g in ctx["GI"]]     # Kerr, chi^0..2   (code convention: has the 1/2)
dH = [KD.hamiltonian(g) for g in dgi]           # deformation
# ctx["chains"] holds MOD-P coefficients. Bracketing those against a RATIONAL K1 is meaningless
# arithmetic -- residues and rationals are not the same ring. Use the CRT-reconstructed chain4.
# SYMBOL IDENTITY, not symbol name. sp.sympify on saved text creates FRESH symbols called P_t, P_x,
# ... which are NOT the solver's momenta (those carry real=True), so Poly extraction matched nothing
# and both objects silently parsed to zero. A bug this repo has hit before and I reintroduced.
_loc = {"P_t": Pt, "P_x": Px, "P_y": Py, "P_phi": Pph, "x": x, "y": y, "chi": chi}
_txt = open("data/triple/CHAIN4.txt").read().split("CHAIN4 =")[1].split("===")[0].strip()
CH4 = sp.sympify(_txt, locals=_loc)
# K1, reconstructed earlier, as coefficients over the momentum monomials per chi order
import re
txt = open("data/triple/K1_A.txt").read().split("K1 =")[1].split("=== chi^2")[0]
K1expr = sp.sympify(txt.strip(), locals=_loc)
print(f"  loaded [{time.time()-t0:.0f}s]", flush=True)
def coeffs_of(e):
    P = sp.Poly(sp.expand(e), Pt,Px,Py,Pph)
    d = {m:c for m,c in zip(P.monoms(), P.coeffs())}
    return [sp.cancel(d.get(tuple(m), 0)) for m in mons]
K1n = [coeffs_of(sp.expand(sp.diff(K1expr, chi, n).subs(chi,0)/sp.factorial(n))) for n in range(3)]
ch4 = [coeffs_of(sp.expand(sp.diff(CH4, chi, n).subs(chi,0)/sp.factorial(n))) for n in range(3)]
print(f"  chain4 and K1 both rational; chi-levels nonzero: "
      f"ch4 {[n for n in range(3) if any(c!=0 for c in ch4[n])]}, "
      f"K1 {[n for n in range(3) if any(c!=0 for c in K1n[n])]}", flush=True)
def br(F, Hh):
    # bracket_raw_coeffs returns (expr, denom) -- a SCALAR expression, not a coefficient list.
    if Hh == 0 or F is None or all(f == 0 for f in F): return sp.Integer(0)
    return PB.bracket_raw_coeffs(F, Hh, mons)[0]
print("  O(eps^1) residual by chi order:", flush=True)
allz = True
informative = []
for n in range(3):
    acc = sp.Integer(0); nontrivial = False
    for j in range(0, n+1):
        a = br(K1n[n-j], H[j]); b = br(ch4[n-j], dH[j])
        if a != 0 or b != 0: nontrivial = True
        acc = sp.cancel(sp.together(acc + a + b))
    z = sp.simplify(acc) == 0
    # A VACUOUS PASS IS NOT A PASS. A's deformation is pure chi^2 and K1 carries chi^2, so every
    # term at chi^0 and chi^1 is identically zero and "residual = 0" there says nothing at all.
    tag = "zero (INFORMATIVE)" if (z and nontrivial) else ("zero (VACUOUS -- every term was 0)"
                                                          if z else "NONZERO")
    if nontrivial: informative.append(z)
    allz &= z
    print(f"    chi^{n}: residual {tag}", flush=True)
if not informative:
    print("\n  NO INFORMATIVE LEVEL -- the check proved nothing.")
elif allz:
    print(f"\n  PASS: K1 is correct at source ({len(informative)} informative level(s))")
else:
    print("\n  FAIL: K1 does not solve the equation at source")
print(f"  total {time.time()-t0:.0f}s")
