"""Gap B design measurement (geometry only, no F values): Newton-continued outer singular points r+, r-, p+, p- of the
§159 lower-axis problem (spin 3/5, E = 4/5) along lines Im k = const in complex k; rho_c; clearances of the adaptive
M1 lasso (capsule around [r+, p+]) and of M0 (circle 1.35); sparse argument-principle counts of G1/G2 zeros in
1.3 < |z| < 60 (expect 2, 2) and in rho+0.1 < |z| < 1.3 (expect 0, 0). Output: data/nve/kc_geometry.out"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpmath as mp
import sympy as sp
import _nve_lower as L
import _nve_lower_kc as KC
mp.mp.dps = 30
TOL = mp.mpf(10) ** -25
E2 = sp.Rational(16, 25)


def clearances(P):
    rp, rm, pp, pm = P
    lasso, delta = KC.capsule_lasso(rp, pp, [rm, pm])
    dl = min(KC.path_dist(c, lasso) for c in (rm, pm))
    d0 = min(abs(c) for c in P) - mp.mpf("1.35")
    return float(delta), float(dl), float(d0)


def counts(pr):
    w = lambda f, R: L.winding(f, mp.mpf(R), N=1200)
    g1 = lambda x: pr.G(x)[0]
    g2 = lambda x: pr.G(x)[2]
    rin = pr.rho + mp.mpf("0.1")
    return (w(g1, 60) - w(g1, 1.3), w(g2, 60) - w(g2, 1.3), w(g1, 1.3) - w(g1, rin), w(g2, 1.3) - w(g2, rin))


if __name__ == "__main__":
    lines = [float(x) for x in sys.argv[1:]] or [0.0, 1.0, -1.0, 2.0, -2.0, 3.0, -3.0]
    start = [mp.mpc("1.934426", 0), mp.mpc("-3.49", 0), mp.mpc(2, "0.6"), mp.mpc(2, "-0.6")]
    for im in lines:
        P = list(start)
        for j in range(1, 13):                                   # climb from k = 0 to k = i*im
            pr = KC.ProblemC(KC.FK, mp.mpc(0, im * j / 12), E2)
            P = [KC.newton(pr, P[i], 1 if i < 2 else 2, TOL) for i in range(4)]
        base = list(P)
        for direction, xs in (("+", [x / 4 for x in range(0, 17)] + [4.05, 4.1]), ("-", [-x / 4 for x in range(1, 201)])):
            P = list(base)
            worst = (9, 9, 9)
            for x in xs:
                k = mp.mpc(x, im)
                try:
                    pr = KC.ProblemC(KC.FK, k, E2)
                    P = [KC.newton(pr, P[i], 1 if i < 2 else 2, TOL) for i in range(4)]
                except RuntimeError as ex:
                    print(f"k={x}{im:+}i STOP: {ex}", flush=True)
                    break
                cl = clearances(P)
                worst = tuple(min(a, b) for a, b in zip(worst, cl))
                show = x in (0, 1, 2, 3, 3.5, 4, 4.05, 4.1) or (x < 0 and x % 5 == 0)
                if show:
                    cnt = counts(pr) if (x in (0, 4) or x % 10 == 0) else None
                    print(f"k={x}{im:+}i rho={float(pr.rho):.2f} pts=" + ",".join(f"{complex(c):.3f}" for c in P) +
                          f" delta={cl[0]:.3f} lassoclr={cl[1]:.3f} M0clr={cl[2]:.3f}" + (f" counts={cnt}" if cnt else ""), flush=True)
            print(f"line Im k={im} dir {direction}: worst delta/lassoclr/M0clr = {worst}", flush=True)
