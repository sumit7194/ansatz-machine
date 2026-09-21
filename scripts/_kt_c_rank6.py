"""Rank-6 grading of object C: does a simple pole (m=1) show grades 2 AND 3 occupied?"""
import sys, time; sys.path.insert(0,'/Users/sumit/Github/conjecture_machine/scripts')
import sympy as sp
from _kt_carter_space import setup, build_space, x, y
from _kt_q2_candidate import combine
from _kt_pole_check import breakdown_single
from _kt_anatomy import chi_pieces, lie_inverse
import _kt_double as KD
chi = KD.chi
t0=time.time()
C_COEF={"l2rr_3":1,"l2ang_3":1,"l2ang_4":sp.Rational(3,2)}
ctx = setup(6, 8, 6, 0)
names,gis,roles = build_space(ctx["GI"], 6, slots=("l2tt","l2rr","l2ang"))
keep=[i for i,r_ in enumerate(roles) if r_=="slot"]
names=[names[i] for i in keep]; gis=[gis[i] for i in keep]
gi = combine(gis,[sp.Rational(C_COEF.get(n,0)) for n in names])
giK = sum((chi**n*ctx["GI"][n] for n in range(3)), sp.zeros(4,4))
G = chi_pieces(lie_inverse(giK,[0,chi**2*(3*y**2-1)/x,0,0]))
gi = [sp.Matrix(gi[k])+sp.Matrix(G[k]) for k in range(3)]
print(f"  rank 6, L^8, box {ctx['dx']}x{ctx['dy']}, {ctx['Kc']} Kerr directions [{time.time()-t0:.0f}s]",
      flush=True)
res = breakdown_single(ctx, gi)
print(f"\n  C at rank 6: survivors {res}", flush=True)
if res:
    tot, by_q = res
    print(f"  floor (grade 0) = 16; above floor = {tot-16}", flush=True)
    occ = {k:v for k,v in by_q.items() if v}
    print(f"  occupied grades: {occ}", flush=True)
    g1, g2, g3 = by_q.get(1,0), by_q.get(2,0), by_q.get(3,0)
    print(f"\n  PREDICTION (simple pole m=1): grade1 EMPTY, grades 2 and 3 BOTH occupied")
    print(f"  grade1={g1}  grade2={g2}  grade3={g3}")
    if g1==0 and g2>0 and g3>0: print("  => CONFIRMS m = 1")
    elif g1==0 and g2>0 and g3==0: print("  => REFUTES m = 1 (grade 3 empty)")
    else: print("  => neither pattern; the hypothesis does not describe this")
print(f"\n  total {time.time()-t0:.0f}s")
