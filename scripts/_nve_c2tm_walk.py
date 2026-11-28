#!/usr/bin/env python3
"""C2-TM walk (data/nve/route1_check/C2_TM_REGISTRATION.md, Design 3-5): the monodromy as Taylor models in dk over a
k-disc |k - kc0| <= rho, by v2's z-Taylor walk with TM coefficients.

Per step (centre zc, step h, radius rz; |h| <= rz/4 as in v2 and in C0):
  guards   * the off-cut guard (C2-4 (a1)): B (region B) or I (circle) certified off the cut (lower(|A| + Re A) > 0) on
             the box of the step SEGMENT x the k-disc's ball. So the principal root is ONE continuous branch along the
             path for every k in the disc;
           * C0.sup_box over the z-box (half-side rz) x the k-disc's ball: sup |c0''|, with B and z^2 + a^2 certified
             nonzero there (else the step is refused and rz halved, as in v2's walk);
           * q on the z-box x the disc as a TM (c0 and c0' on the box by Taylor with M |dz|^2/2), through TM
             reciprocals (theta-guards): Q = its bound; Q rz^2 < 0.9 * 2 NT (NT + 1) (v2's tail condition).
  series   s = sqrt_p(B) (or w sqrt_p(I)) as a z-series of TMs (the TM sqrt and recip carry the theta and cut guards);
           c0'' = pref s/(z^2 + a^2)^3; c0', c0 by integration from the carried TMs; f0 and f0' are dk-free; G1, G2,
           lambda and q as z-series of TMs; Y's recurrence v_{j+2} = -sum q_i v_{j-i} / ((j+1)(j+2)).
  tails    Y: v2's majorant (|v_j| <= Kc mu^j, mu = 2/rz, x = mu |h|), with Kc from the TM bounds; c0, c0': C0's Cauchy
           tails with M = sup |c0''| (uniform over the disc). All tails are added to the TM remainders.
Preconditioning (registration 4b): C_0 = I, C_{i+1} = mid(T_i(kc0) C_i) (exact points); W_{i+1} = (C_{i+1}^-1 T_i C_i)
W_i; M = C_N W_N. C^-1 = adj(C)/det(C) with det(C) certified nonzero (else TMRefuse).
Logged: eps = max remainder over W's entries at the end of every edge.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from flint import acb, acb_series, arb, ctx      # noqa: E402
import _nve_c2tm_core as T                       # noqa: E402
from _nve_c2tm_core import TM, TMRefuse, D       # noqa: E402

ctx.prec = 256


class Disc:
    """the k-disc |k - kc0| <= rho, its square ball, and the TM of k"""

    def __init__(self, kc0, rho):
        assert kc0.real.rad() == 0 and kc0.imag.rad() == 0
        self.kc0, self.rho = kc0, arb(rho).upper()
        T.set_disc(self.rho)
        self.ball = kc0 + acb(arb(0, self.rho), arb(0, self.rho))     # a square containing the disc
        self.k = TM([kc0, acb(1)])


# ------------------------------------------------------------------------------------------------ z-series of TMs
def lift(cs, N):
    cs = list(cs) + [acb(0)] * (N - len(cs))
    return [TM.const(c) for c in cs[:N]]


def zmul(A, B, N):
    return [sum((A[i] * B[n - i] for i in range(n + 1)), TM.const(0)) for n in range(N)]


def zscal(A, s, N):
    """A (TMs) times a dk-free series s (acb coefficients)"""
    s = list(s) + [acb(0)] * (N - len(s))
    return [sum((A[i].scale(s[n - i]) for i in range(n + 1) if not s[n - i].is_zero()), TM.const(0))
            for n in range(N)]                                   # TM read F2: is_zero(), not != (a ball may contain 0)


def zrecip(A, N, name):
    r0 = A[0].recip(name)
    out = [r0]
    for n in range(1, N):
        acc = sum((A[i] * out[n - i] for i in range(1, n + 1)), TM.const(0))
        out.append(-(r0 * acc))
    return out


def zsqrt(A, N, name):
    s0 = A[0].sqrt(name)
    inv = (s0.scale(acb(2))).recip(name + " 2s0")
    out = [s0]
    for n in range(1, N):
        acc = A[n] - sum((out[i] * out[n - i] for i in range(1, n)), TM.const(0))
        out.append(inv * acc)
    return out


def zint(A, c, N):
    return [c] + [A[n].scale(acb(1) / (n + 1)) for n in range(N - 1)]


def zeval(A, h):
    v = TM.const(0)
    hp = acb(1)
    for a in A:
        v = v + a.scale(hp)
        hp *= h
    return v


def ball_tm(r):
    """a TM for an unknown complex x with |x| <= r (r a MODULUS bound), as a pure remainder"""
    return TM([acb(0)], arb(r).upper())


# ------------------------------------------------------------------------------------------------ the start
def start_tm(spin_a, zb, disc, sm=64):
    """c0(zb) and c0'(zb) as TMs in dk (registration Design 3). P(s, k) = P0(s) + P1(s) dk is LINEAR in k, so
    sqrt P = sqrt P0 sum_j binom(1/2, j) (P1/P0)^j dk^j exactly where |P1/P0| rho < 1. Coefficient j is a 1-D Arb
    integral like V1's start (s = 1/t on [0, 1/zb]; Re P0 > 0 required on every ball, else NaN and the integrator
    refuses). The tail j > D: |binom(1/2, j)| <= 1/2, so |sum_{j>D}| <= |w| |sqrt P0| r^(D+1)/(2 (1 - r)) /(1+a^2 s^2)^3,
    r = |P1/P0| rho, bounded by a rectangle rule on sm balls of s (enclosed, not sampled; r < 1 asserted)."""
    from fractions import Fraction
    a = spin_a
    kc = disc.kc0
    zb = acb(zb)
    lim = 1 / zb
    k8 = (arb(8) / 5).sqrt() * a
    c2, c1, cc = 90 - 21 * kc, -(60 - 18 * kc), 10 - kc

    def P0(s):
        a2s2 = a * a * s * s
        return c2 + c1 * a2s2 + cc * a2s2 * a2s2

    def P1(s):
        a2s2 = a * a * s * s
        return -21 + 18 * a2s2 - a2s2 * a2s2

    binom = [Fraction(1)]
    for j in range(1, D + 1):
        binom.append(binom[-1] * (Fraction(1, 2) - (j - 1)) / j)

    def make(weight, j):
        bj = arb(binom[j].numerator) / binom[j].denominator

        def f(s, analytic):
            p0 = P0(s)
            if analytic and not (p0.real > 0):
                return acb("nan")
            return weight(s) * p0.sqrt() * bj * (P1(s) / p0) ** j / ((1 + a * a * s * s) ** 3)
        return f

    c0p, c0v = [], []
    for j in range(D + 1):
        I1 = acb.integral(make(lambda s: s * s, j), 0, lim, rel_tol=arb(2) ** -230)
        I0 = acb.integral(make(lambda s: s - zb * s * s, j), 0, lim, rel_tol=arb(2) ** -230)
        if not (I1.is_finite() and I0.is_finite()):
            raise TMRefuse(f"start: coefficient {j}'s integral is not finite")
        c0p.append(k8 * I1)
        c0v.append(-k8 * I0)
    # the tail, by a rectangle rule over sm balls of s covering [0, 1/zb] (zb real positive)
    L = lim.real
    assert zb.imag == 0 and L > 0
    e1, e0 = arb(0), arb(0)
    for i in range(sm):
        sb = acb(L * (2 * i + 1) / (2 * sm) + arb(0, L / (2 * sm)))
        p0 = P0(sb)
        if not (p0.real > 0):
            raise TMRefuse("start tail: Re P0 not certified positive")
        r = (P1(sb) / p0).abs_upper() * disc.rho
        if not r < 1:
            raise TMRefuse("start tail: |P1/P0| rho not certified < 1")
        g = (p0.abs_upper().sqrt() * r ** (D + 1) / (2 * (1 - r)) / ((1 + a * a * sb * sb) ** 3).abs_lower()).upper()
        e1 += (sb * sb).abs_upper() * g * L / sm
        e0 += (sb - zb * sb * sb).abs_upper() * g * L / sm
    return dict(c0p=TM(c0p, (k8 * e1).upper()), c0=TM(c0v, (k8 * e0).upper()))


# ------------------------------------------------------------------------------------------------ the walker
class Walker:
    def __init__(self, V, C0cls, spin, sform, disc, NT=None):
        self.V, self.A, self.E2 = V, V.A, V.E2
        self.NT = NT or V.NT
        self.sform, self.disc = sform, disc
        self.c0k = C0cls(spin, disc.ball)                      # C0 with k the disc's ball: sup_box over z-box x disc
        self.pref = -(arb(8) / 5).sqrt() * self.A ** 3
        k = disc.k
        self.c2, self.c1, self.cc = 90 - k.scale(acb(21)), k.scale(acb(18)) - 60, 10 - k
        self.eps_log = []

    # the off-cut guard on (Z, the disc's ball)
    def offcut(self, Z):
        K = self.disc.ball
        w = Z * Z / (self.A * self.A)
        c2, c1, cc = 90 - 21 * K, -(60 - 18 * K), 10 - K
        Aarg = (c2 * w * w + c1 * w + cc) if self.sform == "disc" else (c2 + c1 / w + cc / (w * w))
        g = (Aarg.real * Aarg.real + Aarg.imag * Aarg.imag).sqrt() + Aarg.real
        if not (g.is_finite() and g > 0):
            raise TMRefuse("off-cut guard: the root's argument is not certified off the cut on the step")

    def q_on_box(self, zc, rz, st, M):
        """sup |q| over the z-box zc + rz UNIT x the disc, as the bound of q's TM"""
        A, E2 = self.A, self.E2
        Zb = zc + arb(rz) * self.V.UNIT
        dz = Zb - zc
        d = dz.abs_upper()
        c0 = st["c0"] + st["c0p"].scale(dz) + ball_tm((M * d * d / 2).upper())
        c0p = st["c0p"] + ball_tm((M * d).upper())
        Dp = Zb * Zb + A * A
        f0 = (Zb * Zb - 2 * Zb + A * A) / Dp
        f0p = 2 * (Zb * Zb - A * A) / (Dp * Dp)
        G2 = c0 * c0 + f0 * f0
        dG2 = (c0 * c0p + f0 * f0p).scale(acb(2))
        G1 = G2.scale(acb(E2)) - f0
        dG1 = dG2.scale(acb(E2)) - f0p
        lam = dG1 * G1.recip("G1 on the box") - dG2 * G2.recip("G2 on the box")
        q = (lam * lam).scale(acb(3) / 16)
        return q.bound()

    def step(self, zc, hvec, rz, st):
        """-> (T (2x2 TMs), new st) or raises TMRefuse"""
        V, A, E2, NT = self.V, self.A, self.E2, self.NT
        habs = hvec.abs_upper()
        if not habs <= arb(rz) / 4:
            raise TMRefuse("step: |h| > rz/4")
        hb = zc + hvec / 2 + (habs / 2) * V.UNIT                 # the box of the step segment
        self.offcut(hb)
        try:
            M, _MD, _MS = self.c0k.sup_box(zc, arb(rz))
        except AssertionError as e:
            raise TMRefuse(f"sup_box: {e}")
        Q = self.q_on_box(zc, rz, st, M)
        rb = arb(rz)
        if not Q * rb * rb < arb(2 * NT * (NT + 1) * 9) / 10:
            raise TMRefuse("step: Q rz^2 too large for the tail")
        cap0 = ctx.cap
        ctx.cap = NT + 3
        try:
            assert ctx.cap == NT + 3                             # the Bridge: python-flint truncates at ctx.cap
            x = acb_series([zc, 1])
            w = (x * x / (A * A)).coeffs()
            if self.sform == "disc":
                w2 = (x * x * x * x / (A ** 4)).coeffs()
                Bser = [a + b + c for a, b, c in zip(
                    [self.c2.scale(c) for c in (w2 + [acb(0)] * NT)[:NT]],
                    [self.c1.scale(c) for c in (w + [acb(0)] * NT)[:NT]],
                    [self.cc] + [TM.const(0)] * (NT - 1))]
                s = zsqrt(Bser, NT, "sqrt B")
            else:
                iw = (A * A / (x * x)).coeffs()
                iw2 = (A ** 4 / (x * x * x * x)).coeffs()
                Iser = [a + b + c for a, b, c in zip(
                    [self.c2] + [TM.const(0)] * (NT - 1),
                    [self.c1.scale(c) for c in (iw + [acb(0)] * NT)[:NT]],
                    [self.cc.scale(c) for c in (iw2 + [acb(0)] * NT)[:NT]])]
                s = zscal(zsqrt(Iser, NT, "sqrt I"), w, NT)
            D3inv = (1 / ((x * x + A * A) ** 3)).coeffs()
            c0pp = [t.scale(self.pref) for t in zscal(s, D3inv, NT)]
            c0p = zint(c0pp, st["c0p"], NT)
            c0 = zint(c0p, st["c0"], NT)
            f0s = ((x * x - 2 * x + A * A) / (x * x + A * A))
            f0 = f0s.coeffs()
            f0p = f0s.derivative().coeffs()
            for nm_, cs_ in (("w", w), ("D3inv", D3inv), ("f0", f0), ("f0p", f0p)):
                assert len(cs_) <= NT + 3, f"series {nm_}: {len(cs_)} coefficients > the cap"
            assert len(D3inv) >= NT and len(f0) >= NT, "a dense series came back shorter than NT (truncated?)"
        finally:
            ctx.cap = cap0
        f0 = (f0 + [acb(0)] * NT)[:NT]
        f0p = (f0p + [acb(0)] * NT)[:NT]
        f0f0 = []
        for n in range(NT):
            f0f0.append(sum((f0[i] * f0[n - i] for i in range(n + 1)), acb(0)))
        f0f0p = [sum((f0[i] * f0p[n - i] for i in range(n + 1)), acb(0)) for n in range(NT)]
        G2 = [a + TM.const(b) for a, b in zip(zmul(c0, c0, NT), f0f0)]
        dG2 = [(a + TM.const(b)).scale(acb(2)) for a, b in zip(zmul(c0, c0p, NT), f0f0p)]
        G1 = [g.scale(acb(E2)) - TM.const(f) for g, f in zip(G2, f0)]
        dG1 = [g.scale(acb(E2)) - TM.const(f) for g, f in zip(dG2, f0p)]
        lam = [a - b for a, b in zip(zmul(dG1, zrecip(G1, NT, "1/G1"), NT), zmul(dG2, zrecip(G2, NT, "1/G2"), NT))]
        q = [t.scale(acb(3) / 16) for t in zmul(lam, lam, NT)]
        # Y's recurrence (two columns), majorant tail as v2
        mu = 2 / rb
        xh = (mu * habs).upper()
        assert xh < arb(51) / 100
        cols = []
        for v0, v1 in ((1, 0), (0, 1)):
            v = [TM.const(v0), TM.const(v1)]
            for j in range(NT - 1):
                acc = sum((q[i] * v[j - i] for i in range(j + 1)), TM.const(0))
                v.append(acc.scale(acb(-1) / ((j + 1) * (j + 2))))
            Kc = max((v[j].bound() / mu ** j).upper() for j in range(NT + 1))
            tail = (Kc * xh ** (NT + 1) / (1 - xh)).upper()
            dtail = (Kc * mu * (NT + 1) * xh ** NT / ((1 - xh) * (1 - xh))).upper()
            val = zeval(v, hvec) + ball_tm(tail)
            der = zeval([v[j].scale(acb(j)) for j in range(1, NT + 1)], hvec) + ball_tm(dtail)
            cols.append((val, der))
        Tm = [[cols[0][0], cols[1][0]], [cols[0][1], cols[1][1]]]
        # c0, c0' at the step end: series values plus C0's Cauchy tails (M uniform over the disc)
        # TM read F1: zint keeps N - 1 input terms, so c0' uses c0''_n for n <= NT - 2 and c0 for n <= NT - 3. With
        # |c0''_n| <= M / rz^n (Cauchy on the disc of radius rz inside sup_box's square), the tails are
        #   c0':  sum_{n >= NT-1} M |h|^(n+1) / (rz^n (n+1)) <= M |h| th^(NT-1) / (NT (1 - th)),
        #   c0:   sum_{n >= NT-2} M |h|^(n+2) / (rz^n (n+1)(n+2)) <= M |h|^2 th^(NT-2) / ((NT-1) NT (1 - th)).
        th = (habs / rb).upper()
        tail1 = (M * habs * th ** (NT - 1) / (NT * (1 - th))).upper()
        tail2 = (M * habs * habs * th ** (NT - 2) / ((NT - 1) * NT * (1 - th))).upper()
        new = dict(c0=zeval(c0, hvec) + ball_tm(tail2), c0p=zeval(c0p, hvec) + ball_tm(tail1))
        for row in Tm:
            for t in row:
                if not t.is_finite():
                    raise TMRefuse("step: a non-finite TM")
        return Tm, new

    def walk(self, vertices, st0, sing, limz):
        """the loop through `vertices` (complex floats; exact binary points), from the TM state st0 at vertices[0].
        -> M (2x2 TMs), steps. v2's step control: rz = dist/2, h <= rz/4, rz halved on a refusal down to 1e-4."""
        assert vertices[0] == vertices[-1]
        C = [[acb(1), acb(0)], [acb(0), acb(1)]]
        W = [[TM.const(1), TM.const(0)], [TM.const(0), TM.const(1)]]
        st, nst = st0, 0
        for ei, (P0, P1) in enumerate(zip(vertices[:-1], vertices[1:])):
            pos = P0
            while pos != P1:
                dist = min([abs(pos - s) for s in sing] + [abs(pos) - limz])
                rho = 0.5 * dist
                rem = abs(P1 - pos)
                while True:
                    nxt = P1 if rem <= 0.24 * rho else pos + (P1 - pos) * ((0.24 * rho) / rem)   # TM read F5: as C0
                    zc, zn = acb(pos.real, pos.imag), acb(nxt.real, nxt.imag)
                    try:
                        Tm, new = self.step(zc, zn - zc, rho, st)
                        break
                    except TMRefuse as e:
                        last = str(e)
                        rho /= 2
                        if rho < 1e-4:
                            raise TMRefuse(f"no admissible step at {pos} (last refusal: {last})")
                # preconditioned accumulation (registration 4b)
                T0 = [[Tm[i][j].c[0] for j in range(2)] for i in range(2)]
                Cn = [[acb((T0[i][0] * C[0][j] + T0[i][1] * C[1][j]).mid()) for j in range(2)] for i in range(2)]
                det = Cn[0][0] * Cn[1][1] - Cn[0][1] * Cn[1][0]
                if det.contains(0):
                    raise TMRefuse("preconditioner: det(C) not certified nonzero")
                Ci = [[Cn[1][1] / det, -Cn[0][1] / det], [-Cn[1][0] / det, Cn[0][0] / det]]
                TC = [[Tm[i][0].scale(C[0][j]) + Tm[i][1].scale(C[1][j]) for j in range(2)] for i in range(2)]
                S = [[TC[0][j].scale(Ci[i][0]) + TC[1][j].scale(Ci[i][1]) for j in range(2)] for i in range(2)]
                W = [[S[i][0] * W[0][j] + S[i][1] * W[1][j] for j in range(2)] for i in range(2)]
                C = Cn
                st = new
                pos, nst = nxt, nst + 1
            self.eps_log.append(dict(edge=ei, steps=nst, eps=float(max(W[i][j].e for i in range(2) for j in range(2)).mid())))
        Mm = [[W[0][j].scale(C[i][0]) + W[1][j].scale(C[i][1]) for j in range(2)] for i in range(2)]
        self.final_state = st                                     # TM read F7: c0's closure is checked by the probe
        return Mm, nst
