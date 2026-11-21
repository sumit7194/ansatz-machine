"""POST-HOC (not in the gap-B prereg; no new evaluations): finite-group exclusion over R from the cached gap-B boundary
samples. A finite irreducible subgroup of SL2(C) has every trace in S = {2cos(2 pi j/n): n in 1,2,3,4,5,6,8,10}
= {+-2, +-1, 0, +-sqrt2, +-(sqrt5-1)/2, +-(sqrt5+1)/2}. Count zeros of tr M1 - s over R for each s (argument principle,
same 134 samples, with the same |darg| <= pi/4 resolution requirement). Output: data/nve/gapb_finite.out"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpmath as mp
import _nve_lower_kc_count as G
mp.mp.dps = 50
ks = G.rect_boundary(G.X0, G.X1, G.Y)
T1 = [mp.mpc(*G.CACHED[(G.key(k), "0.35")]["T1"]) for k in ks]
T0 = [mp.mpc(*G.CACHED[(G.key(k), "0.35")]["T0"]) for k in ks]
S = [2, -2, 1, -1, 0, mp.sqrt(2), -mp.sqrt(2), (mp.sqrt(5) - 1) / 2, -(mp.sqrt(5) - 1) / 2, (mp.sqrt(5) + 1) / 2, -(mp.sqrt(5) + 1) / 2]
ok = True
for s in S:
    c1, c0 = G.count([t - s for t in T1]), G.count([t - s for t in T0])
    good = c1[0] == 0 and c1[2] <= G.PI4
    ok &= good
    print(f"s={mp.nstr(s, 6):>9}: zeros of trM1-s in R = {c1[0]} (raw {c1[1]:+.2e}, max|darg| {c1[2]:.3f}); trM0-s: {c0[0]} (max|darg| {c0[2]:.3f})")
print("min |Im tr M1| on boundary samples:", mp.nstr(min(abs(mp.im(t)) for t in T1), 6), "; min |tr M1 - s| over s, samples:",
      mp.nstr(min(abs(t - s) for t in T1 for s in S), 6))
print("tr M1 avoids every finite-group trace value throughout R:", ok)
