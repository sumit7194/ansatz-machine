#!/usr/bin/env python3
"""EXP-004 -- verify that the 5D vacuum metric of EXP-003 is the Kaluza-Klein lift of a 4D
Einstein-Maxwell pp-wave, by direct computation (no reduction formula is assumed).

5D (coordinates t, xi, eta, s, v; rho^2 = xi^2 + eta^2):
    ds5^2 = -2U dt^2 + 2 dt ds + 2A dt dv + dv^2 + 8 rho^2 (dxi^2 + deta^2)
    A = 2 kappa xi/rho^2,   U = 2 a xi/rho^2 + kappa^2 (eta^2 - 3 xi^2)/(2 rho^4)

Claim:  ds5^2 = ds4^2 + (dv + A dt)^2,   ds4^2 = -2V dt^2 + 2 dt ds + 8 rho^2 (dxi^2 + deta^2),
        2V = 2U + A^2 = (4 a xi + kappa^2)/rho^2,
and (g4, A_mu dx^mu = A dt) solves 4D Einstein-Maxwell in the KK normalisation
        R4_mn = 1/2 F_mr F_n^r - 1/8 g_mn F^2 ... (with F^2 = 0 here),  nabla_m F^mn = 0,
where the constant-dilaton KK identities are (horizontal frame e^v = dv + A):
        Rhat_mn = R4_mn - 1/2 F_mr F_n^r,   Rhat_mv = 1/2 nabla^r F_mr  (sign fixed by STEP B, see results/exp004_kk_firstrun.log),
        Rhat_vv = 1/4 F_rs F^rs.

STEP A checks the identity ds5 = ds4 + (dv+A dt)^2 and the 4D profile.
STEP B checks the KK identities OFF-SHELL, with U(xi,eta), A(xi,eta) arbitrary functions, so the
       formulas are verified on this family rather than quoted.
STEP C checks the on-shell 4D equations: Einstein-Maxwell, Maxwell, F null, energy density >= 0.
STEP D KNOWN-FAIL: wrong coupling (R4 = 1 * F F) and a non-harmonic A must both be caught.
"""
import itertools, time
import sympy as sp
from sympy import Rational as Q_

T0 = time.time()
def log(m): print(f"[{time.time()-T0:6.1f}s] {m}", flush=True)

t, xi, eta, s, v = sp.symbols("t xi eta s v", real=True)
a, kap = sp.symbols("a kappa", real=True)
X5 = [t, xi, eta, s, v]
X4 = [t, xi, eta, s]
rho2 = xi**2 + eta**2


def geometry(g, X):
    n = len(X)
    gi = g.inv().applyfunc(sp.cancel)
    Gam = [[[sp.cancel(Q_(1, 2) * sum(gi[i, l] * (sp.diff(g[l, j], X[k]) + sp.diff(g[l, k], X[j]) - sp.diff(g[j, k], X[l]))
                                       for l in range(n))) for k in range(n)] for j in range(n)] for i in range(n)]
    def Rup(i, j, k, l):
        return (sp.diff(Gam[i][l][j], X[k]) - sp.diff(Gam[i][k][j], X[l])
                + sum(Gam[i][k][m] * Gam[m][l][j] - Gam[i][l][m] * Gam[m][k][j] for m in range(n)))
    Ric = sp.Matrix(n, n, lambda j, l: sp.cancel(sum(Rup(i, j, i, l) for i in range(n))))
    return gi, Gam, Ric


def g5_of(U, A):
    g = sp.zeros(5, 5)
    g[0, 0] = -2 * U; g[0, 3] = g[3, 0] = 1; g[0, 4] = g[4, 0] = A; g[4, 4] = 1
    g[1, 1] = g[2, 2] = 8 * rho2
    return g


def g4_of(V):
    g = sp.zeros(4, 4)
    g[0, 0] = -2 * V; g[0, 3] = g[3, 0] = 1; g[1, 1] = g[2, 2] = 8 * rho2
    return g


def kk_sides(U, A):
    """Return (R5 coordinate components, the KK prediction built from 4D quantities)."""
    V = U + A**2 / 2
    g5, g4 = g5_of(U, A), g4_of(V)
    _, _, R5 = geometry(g5, X5)
    g4i, Gam4, R4 = geometry(g4, X4)
    Avec = [A, 0, 0, 0]                                   # A_mu
    F = sp.Matrix(4, 4, lambda m, n: sp.diff(Avec[n], X4[m]) - sp.diff(Avec[m], X4[n]))
    Fup_mixed = (F * g4i)                                 # F_m^r = F_ms g^sr
    FF = sp.Matrix(4, 4, lambda m, n: sp.cancel(sum(F[m, r] * Fup_mixed[n, r] for r in range(4))))
    F2 = sp.cancel(sum(F[m, n] * (g4i * F * g4i)[m, n] for m in range(4) for n in range(4)))
    # divergence  (nabla^r F_rm) = g^rs nabla_s F_rm
    def covF(sidx, r, m):
        e = sp.diff(F[r, m], X4[sidx])
        e -= sum(Gam4[k][sidx][r] * F[k, m] + Gam4[k][sidx][m] * F[r, k] for k in range(4))
        return e
    divF = [sp.cancel(sum(g4i[r, s_] * covF(s_, r, m) for r in range(4) for s_ in range(4))) for m in range(4)]
    Rh = sp.zeros(5, 5)
    for m in range(4):
        for n in range(4):
            Rh[m, n] = R4[m, n] - Q_(1, 2) * FF[m, n]
        # SIGN: first run used +1/2 nabla^r F_rm and the off-shell check (STEP B) caught it --
        # the mismatch was exactly -Delta A/(8 rho^2) = -2 x prediction.  Correct: 1/2 nabla^r F_mr.
        Rh[m, 4] = Rh[4, m] = -Q_(1, 2) * divF[m]
    Rh[4, 4] = Q_(1, 4) * F2
    # frame -> coordinate:  e^v = dv + A_m dx^m, so R5_{mn} = Rh_mn + A_m Rh_vn + A_n Rh_mv + A_m A_n Rh_vv,
    # R5_{mv} = Rh_mv + A_m Rh_vv, R5_vv = Rh_vv.   (index 4 = v; A_s = 0 for the s slot)
    Afull = Avec
    pred = sp.zeros(5, 5)
    for m in range(4):
        for n in range(4):
            pred[m, n] = Rh[m, n] + Afull[m] * Rh[4, n] + Afull[n] * Rh[m, 4] + Afull[m] * Afull[n] * Rh[4, 4]
        pred[m, 4] = pred[4, m] = Rh[m, 4] + Afull[m] * Rh[4, 4]
    pred[4, 4] = Rh[4, 4]
    return R5, pred, R4, FF, F2, divF, g4i, F


# ---------------------------------------------------------------- STEP A
log("STEP A: the identity ds5 = ds4 + (dv + A dt)^2 and the 4D profile")
A0 = 2 * kap * xi / rho2
U0 = 2 * a * xi / rho2 + kap**2 * (eta**2 - 3 * xi**2) / (2 * rho2**2)
V0 = sp.cancel(U0 + A0**2 / 2)
log(f"  2V = 2U + A^2 = {sp.factor(2 * V0)}")
dX = sp.symbols("dt dxi deta ds dv")
line5 = sum(g5_of(U0, A0)[i, j] * dX[i] * dX[j] for i in range(5) for j in range(5))
line4 = sum(g4_of(V0)[i, j] * dX[i] * dX[j] for i in range(4) for j in range(4))
log(f"  ds5^2 - ds4^2 - (dv + A dt)^2 == 0: {sp.cancel(sp.expand(line5 - line4 - (dX[4] + A0 * dX[0])**2)) == 0}")

# ---------------------------------------------------------------- STEP B
log("STEP B: KK identities OFF-SHELL, U and A arbitrary functions of (xi, eta)")
Uf = sp.Function("U")(xi, eta)
Af = sp.Function("A")(xi, eta)
R5f, predf, *_ = kk_sides(Uf, Af)
diff = (R5f - predf).applyfunc(lambda e: sp.simplify(sp.expand(e)))
log(f"  R5 - KK prediction == 0 in all 15 components (arbitrary U, A): {diff == sp.zeros(5, 5)}")
if diff != sp.zeros(5, 5):
    for i in range(5):
        for j in range(i, 5):
            if diff[i, j] != 0: log(f"    mismatch ({i},{j}): {diff[i, j]}")

# ---------------------------------------------------------------- STEP C
log("STEP C: the actual solution, a and kappa symbolic")
R5, pred, R4, FF, F2, divF, g4i, F = kk_sides(U0, A0)
log(f"  5D Ricci identically zero: {R5.applyfunc(sp.cancel) == sp.zeros(5, 5)}")
log(f"  Maxwell nabla_r F^r_m == 0 (all m): {all(sp.cancel(e) == 0 for e in divF)}")
log(f"  F_rs F^rs == 0 (null field, so the constant dilaton is consistent): {sp.cancel(F2) == 0}")
EM = (R4 - Q_(1, 2) * FF).applyfunc(sp.cancel)
log(f"  4D Einstein-Maxwell  R4_mn = 1/2 F_mr F_n^r  (traceless T since F^2 = 0): {EM == sp.zeros(4, 4)}")
nz4 = {(i, j): sp.factor(R4[i, j]) for i in range(4) for j in range(i, 4) if R4[i, j] != 0}
log(f"  nonzero 4D Ricci components: {nz4}")
log(f"  kappa = 0 limit: 4D Ricci vanishes -> vacuum pp-wave of EXP-002: {all(sp.cancel(e.subs(kap, 0)) == 0 for e in R4)}")
# energy density along the timelike observer u = (dt - ... ): T_tt = R4_tt/(8 pi) in G=1 up to the KK normalisation
Ttt = sp.factor(R4[0, 0])
# first run compared against a hard-coded kappa^2/(16 rho^6) -- wrong constant; test positivity directly
log(f"  R4_tt = 1/2 F_tr F_t^r = {Ttt}   (a square over a positive denominator -> >= 0: {sp.factor(Ttt * 4 * rho2**3) == kap**2})")
# where the source sits: transverse Laplacian of the Kepler part vs. the harmonic part
Xc, Yc = sp.symbols("X Y", real=True)
lap = lambda f: sp.cancel((sp.diff(f, xi, 2) + sp.diff(f, eta, 2)) / (8 * rho2))   # Laplacian of 8 rho^2 (dxi^2+deta^2)
log(f"  Laplacian of 4 a xi/rho^2 (vacuum part): {lap(4 * a * xi / rho2)};   of kappa^2/rho^2 (Kepler part): {sp.factor(lap(kap**2 / rho2))}")
log(f"  Laplacian of A_t = 2 kappa xi/rho^2: {lap(A0)}  (harmonic, so Maxwell reduces to it)")

# ---------------------------------------------------------------- STEP D
log("STEP D: known-fail controls")
bad = (R4 - FF).applyfunc(sp.cancel)
log(f"  wrong coupling  R4 = 1 * F F : equations hold? {bad == sp.zeros(4, 4)}   (must be False)")
A_bad = 2 * kap * xi**2 / rho2                          # not harmonic
U_bad = U0
R5b, predb, R4b, FFb, F2b, divFb, *_ = kk_sides(U_bad, A_bad)
log(f"  non-harmonic A = 2 kappa xi^2/rho^2 : Maxwell holds? {all(sp.cancel(e) == 0 for e in divFb)}   (must be False)")
log(f"      and the KK identity still holds off-shell there: {(R5b - predb).applyfunc(lambda e: sp.cancel(sp.expand(e))) == sp.zeros(5, 5)}")
log("done")
