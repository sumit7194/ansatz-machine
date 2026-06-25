"""EXPLORATORY — building the Manko-Novikov metric (exact rotating vacuum "bumpy Kerr") the
verification-driven way. Step 1: pin the q=0 baseline against EXACT Kerr (transformed from
Boyer-Lindquist, which we know exactly), so the prolate-spheroidal MN form is trustworthy
before the quadrupole anomaly q is switched on.

Prolate spheroidal (x,y): r = k x + M, cos(theta) = y, k = sqrt(M^2 - a^2).
MN params: alpha = (-1 + sqrt(1-chi^2))/chi (chi=a/M), k = M(1-alpha^2)/(1+alpha^2) = sqrt(M^2-a^2),
beta = q M^3 / k^3 (q = dimensionless quadrupole deviation from Kerr; q=0 -> Kerr).
"""
import math


# ---------- EXACT Kerr in prolate spheroidal (ground truth, from Boyer-Lindquist) ----------
def kerr_prolate(M, a):
    k = math.sqrt(M * M - a * a)

    def g(X):
        _, x, y, _ = X
        r = k * x + M
        ct = y
        st2 = 1.0 - y * y
        Sig = r * r + a * a * ct * ct
        Del = r * r - 2 * M * r + a * a
        gg = [[0.0] * 4 for _ in range(4)]
        gg[0][0] = -(1 - 2 * M * r / Sig)
        gg[0][3] = gg[3][0] = -2 * M * a * r * st2 / Sig
        gg[1][1] = (Sig / Del) * k * k                       # dr = k dx
        gg[2][2] = Sig / st2                                 # dtheta = -dy/sin -> dtheta^2 = dy^2/(1-y^2)
        gg[3][3] = (r * r + a * a + 2 * M * a * a * r * st2 / Sig) * st2
        return gg
    return g


# ---------- Manko-Novikov form (q-anomaly subclass) ----------
def _legP(n, u):
    if n == 0:
        return 1.0
    if n == 1:
        return u
    if n == 2:
        return 0.5 * (3 * u * u - 1)
    if n == 3:
        return 0.5 * (5 * u**3 - 3 * u)
    raise ValueError(n)


def manko_novikov(M, a, q, deform=True):
    chi = a / M
    s = math.sqrt(1 - chi * chi)
    alpha = (-1 + s) / chi
    k = M * (1 - alpha * alpha) / (1 + alpha * alpha)
    beta = q * M**3 / k**3

    def g(X):
        _, x, y, _ = X
        R = math.sqrt(x * x + y * y - 1)
        u = x * y / R
        P2 = _legP(2, u)
        psi = beta * R**(-3) * P2                            # anomaly potential (alpha_2 = beta)
        if deform and beta != 0.0:
            # a,b acquire multipole-exponential factors; gamma' gets anomaly corrections.
            # (best transcription of Gair et al 2008 eqs 3g-3j; Ricci=0 is the arbiter)
            Sa = sum((x - y) * _legP(l, u) / R**(l + 1) for l in range(3))
            Sb = sum((-1)**(3 - l) * (x + y) * _legP(l, u) / R**(l + 1) for l in range(3))
            aa = -alpha * math.exp(-2 * beta * (-1 + Sa))
            bb = alpha * math.exp(2 * beta * (1 + Sb))
            P3 = _legP(3, u)
            Sg = sum(((x - y + (-1)**(2 - l) * (x + y)) / R**(l + 1) * _legP(l, u) - 2)
                     for l in range(3))
            gp_corr = (1.5 * beta * beta / R**6) * (P3 * P3 - P2 * P2) + beta * Sg
        else:
            aa, bb, gp_corr = -alpha, alpha, 0.0
        A = (x * x - 1) * (1 + aa * bb)**2 - (1 - y * y) * (bb - aa)**2
        B = (x + 1 + (x - 1) * aa * bb)**2 + ((1 + y) * aa + (1 - y) * bb)**2
        C = ((x * x - 1) * (1 + aa * bb) * (bb - aa - y * (aa + bb))
             + (1 - y * y) * (bb - aa) * (1 + aa * bb + x * (1 - aa * bb)))
        gp = 0.5 * math.log((x * x - 1) / (x * x - y * y)) + gp_corr   # gamma' (baseline + anomaly)
        f = math.exp(2 * psi) * A / B
        om = 2 * k * math.exp(-2 * psi) * C / A - 4 * k * alpha / (1 - alpha * alpha)
        e2g = math.exp(2 * gp) * A / ((x * x - 1) * (1 - alpha * alpha)**2)
        gg = [[0.0] * 4 for _ in range(4)]
        # ds^2 = -f (dt - om dphi)^2 + k^2/f [ e2g (x^2-y^2)(dx^2/(x^2-1)+dy^2/(1-y^2)) + (x^2-1)(1-y^2) dphi^2 ]
        gg[0][0] = -f
        gg[0][3] = gg[3][0] = f * om
        gg[3][3] = -f * om * om + (k * k / f) * (x * x - 1) * (1 - y * y)
        gg[1][1] = (k * k / f) * e2g * (x * x - y * y) / (x * x - 1)
        gg[2][2] = (k * k / f) * e2g * (x * x - y * y) / (1 - y * y)
        return gg
    return g


if __name__ == "__main__":
    M, a = 1.0, 0.5
    gk = kerr_prolate(M, a)
    gm = manko_novikov(M, a, 0.0)
    print("STEP 1 — does the MN form at q=0 reproduce EXACT Kerr? (component-by-component, M=1 a=0.5)\n")
    pts = [(2.0, 0.3), (3.0, -0.5), (4.0, 0.7), (5.0, 0.1)]
    labels = [(0, 0, "g_tt"), (0, 3, "g_tphi"), (3, 3, "g_phiphi"), (1, 1, "g_xx"), (2, 2, "g_yy")]
    worst = 0.0
    for (x, y) in pts:
        K = gk([0, x, y, 0]); Mn = gm([0, x, y, 0])
        print(f"  (x={x}, y={y}):")
        for i, j, nm in labels:
            d = abs(K[i][j] - Mn[i][j])
            rel = d / (abs(K[i][j]) + 1e-30)
            worst = max(worst, rel)
            flag = "OK" if rel < 1e-9 else "MISMATCH"
            print(f"      {nm:9s} Kerr={K[i][j]:+.6f}  MN={Mn[i][j]:+.6f}  rel={rel:.1e}  {flag}")
    print(f"\n  worst relative mismatch: {worst:.2e}  -> {'BASELINE CONFIRMED' if worst < 1e-9 else 'a,b or form needs fixing'}")

    # STEP 2 — is the DEFORMED (q!=0) metric vacuum? Ricci=0 is the arbiter of the transcription.
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from numeric_curvature import ricci_numeric
    print("\nSTEP 2 — vacuum check: max|R_ab| for q=0 (must be ~FD floor) vs q=0.1 (vacuum iff transcription right):")
    for q in (0.0, 0.1):
        gq = manko_novikov(M, a, q)
        res = max(abs(ricci_numeric(gq, [0.0, x, y, 0.0], h=1e-5)[i][j])
                  for (x, y) in [(3.0, 0.3), (4.0, -0.4), (5.0, 0.6)] for i in range(4) for j in range(4))
        print(f"    q={q}: max|R_ab| = {res:.2e}")
    print("  (q=0 small confirms numeric Ricci works on this metric; q=0.1 small ⇒ MN transcription correct)")
