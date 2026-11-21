"""Review check for a relayed all-spin loop construction (Neon T11/T14, via the Bridge), 2026-11-21.
(1) T14 finite-interval ray formula for c0 vs our Laurent c0 (_nve_lower), spin 3/5.
(2) Argument-principle count of zeros of G1 = E^2(n^2+c0^2 g^2) - n g (zeros of P, r+-) and G2 = n^2+c0^2 g^2
    (poles of P, p+-) in Re z > 1 closed by |z-1| = 40 (CCW, so counts are positive), c0 from the ray formula.
T14 certifies G2 != 0 on Re z = 1 only; G1 (E-dependent) is not covered there. Output: data/nve/t11_check.out"""
import sys, os
sys.path.insert(0, "scripts")
import mpmath as mp, sympy as sp
from _nve_lower import c0_laurent, c0_eval
mp.mp.dps = 30
a = mp.mpf(3)/5
def c0_ray(zz, k):
    u = zz/a
    c4, c2, c0p = 90-21*k, -(60-18*k), 10-k
    f = lambda x: x*(1-x)*u**-2*(1+x**2*u**-2)**-3*mp.sqrt(c4 + c2*x**2*u**-2 + c0p*x**4*u**-4)
    return -(mp.sqrt(mp.mpf(8)/5)/a)*mp.quad(f, [0, 1])
for k in (0, sp.Rational(1,10), 4, -5):
    C, rho, NW, _ = c0_laurent(k)
    for zz in (mp.mpc(2.5, 0.7), mp.mpc(-1.8, 2.2), mp.mpc(1.5, -3)):
        print(k, float(rho), complex(zz), complex(c0_ray(zz, float(k))), complex(c0_eval(C, zz)))
print("---- zero counts in Re z > 1", flush=True)
mp.mp.dps = 20
Y = mp.mpf(40)
ys = [Y*mp.sinh(mp.mpf(6)*(j/1500 - 1))/mp.sinh(6) for j in range(3001)]      # -Y..Y, dense near 0
line = [mp.mpc(1, y) for y in ys][::-1]                                          # from 1+iY down to 1-iY
arcp = [1 + Y*mp.expj(-mp.pi/2 + mp.pi*j/1200) for j in range(1201)]             # 1-iY -> 1+iY through Re z > 1
path = line + arcp[1:]
for k in (-50, -22.59, -5, 0, 0.1, 2, 4, 4.2):
    cs = [c0_ray(zz, k) for zz in path]
    rows = []
    for E in (0.8, 1.05, 1.3, 2.0, 3.0, 10.0):
        E2 = mp.mpf(E)**2
        tot1 = tot2 = mp.mpf(0); prev1 = prev2 = None; mn1 = mn2 = mp.inf
        for i, (zz, c) in enumerate(zip(path, cs)):
            n, g = zz**2 - 2*zz + a**2, zz**2 + a**2
            G2 = n*n + c*c*g*g; G1 = E2*G2 - n*g
            if i < len(line):
                mn1 = min(mn1, abs(G1)/(abs(E2*G2)+abs(n*g))); mn2 = min(mn2, abs(G2)/(abs(n*n)+abs(c*g)**2))
            if prev1 is not None:
                tot1 += mp.arg(G1/prev1); tot2 += mp.arg(G2/prev2)
            prev1, prev2 = G1, G2
        rows.append(f"E={E}: #G1={int(mp.nint(tot1/(2*mp.pi)))} #G2={int(mp.nint(tot2/(2*mp.pi)))} minrel|G1|line={float(mn1):.2e}")
    print(f"k={k}: " + " | ".join(rows) + f" | minrel|G2|line={float(mn2):.2e}", flush=True)
