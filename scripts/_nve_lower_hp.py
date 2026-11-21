"""Half-plane c0 engine for the lower-axis NVE near the endpoint k = 30/7 (window (4.05, 30/7); prereg to follow).
The Laurent series of c0 at infinity dies there (rho_c -> infinity as k -> 30/7). Instead:
  c0''(z) = -sqrt(lc) * prod_i sqrt(z - zeta_i) / (z^2 + a^2)^3        (principal square roots)
where N_k(z) = lc * prod (z - zeta_i) is the radicand numerator (linear in k, from _nve_lower_kc) and the radicand is
N_k / (z^2 + a^2)^6. The sign -1 and principal branches match the Laurent convention (c0'' ~ -sqrt(Sa0) w^m0) on the
positive real axis at large z, provided no zeta_i lies on [x, inf) and no cut ray {zeta_i - t} crosses the working
region (guarded). Integration constants: c0'(Z0) = -int_Z0^inf c0'', c0(Z0) = int_Z0^inf (t - Z0) c0''(t) dt, Z0 = 2.
A Taylor series of c0 about Z0 gives c0, c0' anywhere in |z - Z0| < 0.6 R_c (R_c = distance to the nearest zeta or
+-ia); local Taylor data of c0'' at any point come from N_k directly (series sqrt seeded by the product value)."""
import os
import sys

import mpmath as mp
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_lower as L                     # noqa: E402
import _nve_lower_kc as KC                 # noqa: E402

A = mp.mpf(3) / 5
Z0 = mp.mpf(2)


def _series_sqrt(s, lead, n):
    """sqrt of power series s (s[0] != 0) with leading value lead (lead^2 = s[0]); n coefficients."""
    out = [mp.mpc(0)] * n
    out[0] = lead
    for j in range(1, n):
        out[j] = (s[j] - mp.fsum(out[i] * out[j - i] for i in range(1, j))) / (2 * lead)
    return out


def _poly_shift(desc, z0, n):
    """Taylor coefficients (ascending in t) of the polynomial (descending coeffs) at z0 + t, length n."""
    c = list(desc)
    out = []
    fact = mp.mpf(1)
    for j in range(n):
        if not c:
            out.append(mp.mpc(0)); continue
        out.append(L.peval(c, z0) / fact)
        c = L.pder(c) if len(c) > 1 else []
        fact *= (j + 1)
    return out


def _inv_series(s, n):
    q = [mp.mpc(0)] * n
    q[0] = 1 / s[0]
    for j in range(1, n):
        q[j] = -mp.fsum(s[i] * q[j - i] for i in range(1, min(j, len(s) - 1) + 1)) / s[0]
    return q


def _mul(a, b, n):
    return [mp.fsum(a[i] * b[j - i] for i in range(j + 1) if i < len(a) and j - i < len(b)) for j in range(n)]


class C0Engine:
    def __init__(self, k, NC=220):
        k = mp.mpc(k)
        dN = max(KC.N0.degree(), KC.N1.degree())
        asc = [x + k * y for x, y in zip(KC._asc(KC.N0, dN), KC._asc(KC.N1, dN))]
        while abs(asc[-1]) < mp.mpf(10) ** -40:
            asc.pop()
        self.desc = list(reversed(asc))
        lcD = mp.mpf(sp.N(KC.DEN.LC(), 60))                 # DEN = lcD * (z^2 + a^2)^6 (checked: lcD = 5^12)
        assert sp.simplify(KC.DEN.as_expr() - KC.DEN.LC() * (KC.z**2 + KC.A**2) ** 6) == 0
        self.lc = self.desc[0] / lcD
        self.zeta = mp.polyroots(self.desc, maxsteps=800, extraprec=400)
        self.sing = list(self.zeta) + [mp.mpc(0, A), mp.mpc(0, -A)]
        self.Rc = min(abs(Z0 - s) for s in self.sing)
        self.NC = NC
        # c0'' series about Z0
        nser = [x / lcD for x in _poly_shift(self.desc, Z0, NC)]
        self.lcD = lcD
        lead = self.sqrtN(Z0)
        sq = _series_sqrt(nser, lead, NC)
        g = _poly_shift([1, 0, A**2], Z0, 3)                      # z^2 + a^2 at Z0 + t
        g3 = _mul(_mul(g, g, NC), g, NC)
        self.c2 = [-x for x in _mul(sq, _inv_series(g3, NC), NC)]   # c0'' coefficients about Z0
        # constants
        f2 = lambda t: self.c0pp(t)
        self.c1_0 = -mp.quad(f2, [Z0, 4, 16, mp.inf])
        self.c0_0 = mp.quad(lambda t: (t - Z0) * f2(t), [Z0, 4, 16, mp.inf])
        # c0 series about Z0: c0 = c0_0 + c1_0 t + sum c2[j] t^(j+2)/((j+1)(j+2))
        self.cser = [self.c0_0, self.c1_0] + [self.c2[j] / ((j + 1) * (j + 2)) for j in range(NC)]

    def sqrtN(self, z):                  # sqrt(N_k(z) / lcD), principal factors
        v = mp.sqrt(self.lc)
        for r in self.zeta:
            v *= mp.sqrt(z - r)
        return v

    def c0pp(self, z):
        return -self.sqrtN(z) / (z**2 + A**2) ** 3

    def c0(self, z, deriv=0):
        t = z - Z0
        if deriv == 0:
            return L.peval(list(reversed(self.cser)), t)
        return mp.fsum(j * self.cser[j] * t ** (j - 1) for j in range(1, len(self.cser)))

    def c0_taylor(self, z0, K):
        """Taylor coefficients of c0 at z0 up to order K: values from the Z0 series, the rest from c0'' directly."""
        nser = [x / self.lcD for x in _poly_shift(self.desc, z0, K)]
        sq = _series_sqrt(nser, self.sqrtN(z0), K)
        g = _poly_shift([1, 0, A**2], z0, 3)
        g3 = _mul(_mul(g, g, K), g, K)
        c2 = [-x for x in _mul(sq, _inv_series(g3, K), K)]
        return [self.c0(z0), self.c0(z0, 1)] + [c2[j] / ((j + 1) * (j + 2)) for j in range(K - 1)]

    def guard(self, region_center=mp.mpc(1.9, 0), region_radius=mp.mpf("0.75")):
        """branch-cut and convergence guard for the working region |z - region_center| <= region_radius."""
        cut_ok = True
        for r in self.zeta:
            # cut ray {r - t, t >= 0} must miss the working disc and the real ray [Z0 - 1, inf)
            if mp.re(r) > mp.re(region_center) - region_radius and abs(mp.im(r) - mp.im(region_center)) < region_radius + mp.mpf("0.1"):
                cut_ok = False
            if abs(mp.im(r)) < mp.mpf("1e-6") and mp.re(r) > Z0 - 1:
                cut_ok = False
        reach = abs(region_center - Z0) + region_radius
        return dict(cut_ok=cut_ok, Rc=float(self.Rc), reach=float(reach), conv_ok=bool(reach <= mp.mpf("0.6") * self.Rc))


class ProblemHP(L.Problem):
    """Problem with c0 from C0Engine (only valid inside the guarded working region)."""
    def __init__(self, f0, k, E2, NC=220):
        n, g = sp.fraction(sp.cancel(sp.together(f0)))
        self.n, self.g = L.poly_mp(n), L.poly_mp(g)
        self.dn, self.dg = L.pder(self.n), L.pder(self.g)
        self.eng = C0Engine(k, NC)
        self.rho = mp.mpf(0)          # Walker's |w| - rho term is replaced by passing eng.sing as extra singular points
        self.E2 = mp.mpf(sp.N(E2, 60))

    def G(self, x):
        n, g, dn, dg = L.peval(self.n, x), L.peval(self.g, x), L.peval(self.dn, x), L.peval(self.dg, x)
        c, dc = self.eng.c0(x), self.eng.c0(x, 1)
        G2 = n * n + c * c * g * g
        dG2 = 2 * n * dn + 2 * c * dc * g * g + 2 * c * c * g * dg
        return self.E2 * G2 - n * g, self.E2 * dG2 - dn * g - n * dg, G2, dG2

    def taylor(self, z0, K):
        def ptay(cf):
            return _poly_shift(cf, z0, K + 1)
        n_, g_ = ptay(self.n), ptay(self.g)
        T = self.eng.c0_taylor(z0, K + 1)
        T = (T + [mp.mpc(0)] * (K + 1))[:K + 1]
        def mul(a, b):
            return [mp.fsum(a[i] * b[j - i] for i in range(j + 1)) for j in range(K + 1)]
        nn, cg = mul(n_, n_), mul(T, g_)
        G2 = [x + y for x, y in zip(nn, mul(cg, cg))]
        ng = mul(n_, g_)
        G1 = [self.E2 * x - y for x, y in zip(G2, ng)]
        return G1, G2
