"""Gap B design measurement (no F): Newton-refined extra G1/G2 zeros in rho_c < |z| < 1.3 at real k < 0 (they split
off from +-ia), with annulus argument-principle counts. Seeds from a coarse |G| grid. Log: data/nve/kc_extras.out"""
import sys; sys.path.insert(0, "scripts")
import mpmath as mp, sympy as sp
import _nve_lower as L, _nve_lower_kc as KC
mp.mp.dps = 30
for kr, seeds in ((-10, [(-0.092+1.054j,1), (-0.241+0.900j,2)]), (-5, [(0.0+0.882j,1), (-0.14+0.794j,2)]), (-3, [(0.0+0.85j,1), (-0.14+0.76j,2)]), (-1, [(0.0+0.8j,1), (-0.1+0.72j,2)])):
    pr = KC.ProblemC(KC.FK, mp.mpc(kr, 0), sp.Rational(16, 25))
    for s, w in seeds:
        x = mp.mpc(s)
        ok = True
        for it in range(60):
            G1, dG1, G2, dG2 = pr.G(x)
            F, dF = (G1, dG1) if w == 1 else (G2, dG2)
            x = x - F / dF
            if abs(x) < pr.rho + 0.02 or abs(x) > 2: ok = False; break
            if abs(F / dF) < 1e-25: break
        res = abs(pr.G(x)[0 if w == 1 else 2])
        print(kr, f"G{w}", ok, mp.nstr(x, 8), "|z|", mp.nstr(abs(x), 6), "res", mp.nstr(res, 3), "it", it, flush=True)
    n1 = L.winding(lambda x: pr.G(x)[0], mp.mpf("1.3"), N=2000) - L.winding(lambda x: pr.G(x)[0], pr.rho + mp.mpf("0.05"), N=2000)
    n2 = L.winding(lambda x: pr.G(x)[2], mp.mpf("1.3"), N=2000) - L.winding(lambda x: pr.G(x)[2], pr.rho + mp.mpf("0.05"), N=2000)
    print(kr, "annulus counts", n1, n2, flush=True)
