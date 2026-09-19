#!/usr/bin/env python3
"""The reducible floor, measured correctly for every c -- and fast.

WHAT THE FLOOR NEEDS (D44). A reducible direction p_t^a p_phi^b H^c is exactly conserved, but the
double tower can only FIND it if every piece of its zeta-correction lies in the ansatz
{x^i y^j / L^denpow, i <= dx, j <= dy}. With H = H_K + zeta HS and H_K = H0 + chi H1 + chi^2 H2,
HS = HS0 + chi HS1 + chi^2 HS2, the O(zeta chi^n) piece of H^c is

        C_n(c) = c * sum_{j=0..n} [H_K^(c-1)]_(n-j) * HS_j ,

where [H_K^m]_k is the chi^k coefficient of (H0 + chi H1 + chi^2 H2)^m.

THE BUG THIS REPLACES (found 2026-09-19, reading the code). _kt_double used
c * sum_{i+j=2} H_i^(c-1) * HS_j. For c <= 2 that IS C_2(c). For c = 3 -- which first exists at
rank 6 -- it tests H0^2 HS2 + H1^2 HS1 + H2^2 HS0 instead of
H0^2 HS2 + 2 H0 H1 HS1 + (H1^2 + 2 H0 H2) HS0: a different expression. And only n = 2 was tested;
the solver needs n = 0 and n = 1 to fit too. So the rank-6 "16 of 16 REPRESENTABLE" was never
measured on the right object. Ranks 2-4 (c <= 2) are unaffected.

HOW IT IS FAST. Each piece is kept as numerator/denominator in the sparse ring QQ[x, y, momenta];
products and sums never cancel, so the running denominator Q is a (non-reduced) multiple of the
true one. Then C = P/Q is representable  <=>  Q divides den*P  and the quotient has degree
<= (dx, dy). For a single divisor the division remainder is 0 exactly when it divides, so this is
an exact test with no gcd and no expression trees. The expression-based PB.representable is the
reference it is validated against (c <= 2, both verdicts) in the self-test.
"""
import sympy as sp

import _kt_perturb as PB

x, y = sp.symbols("x y", real=True)


class _Frac:
    """P/Q in the ring PB._ring(); arithmetic without cancellation."""

    def __init__(self, P, Q):
        self.P, self.Q = P, Q

    @classmethod
    def of(cls, expr):
        R = PB._ring()
        num, den = sp.fraction(sp.together(expr))
        return cls(R.from_expr(num), R.from_expr(den))

    def __mul__(self, o):
        return _Frac(self.P * o.P, self.Q * o.Q)

    def __add__(self, o):
        if self.Q == o.Q:
            return _Frac(self.P + o.P, self.Q)
        return _Frac(self.P * o.Q + o.P * self.Q, self.Q * o.Q)

    def scale(self, k):
        return _Frac(self.P * k, self.Q)


def _series_pow(HK, m, order=2):
    """chi-coefficients [H_K^m]_0..order of (HK[0] + chi HK[1] + chi^2 HK[2])^m, truncated."""
    R = PB._ring()
    one = _Frac(R.one, R.one)
    out = [one] + [None] * order
    for _ in range(m):
        new = [None] * (order + 1)
        for a in range(order + 1):
            if out[a] is None:
                continue
            for b in range(order + 1 - a):
                t = out[a] * HK[b]
                new[a + b] = t if new[a + b] is None else new[a + b] + t
        out = new
    return out


def corrections(c, HK, HS, order=2):
    """[C_0(c), C_1(c), C_2(c)] as _Frac, the O(zeta chi^n) pieces of H^c. None for c = 0."""
    if c == 0:
        return [None] * (order + 1)
    P = _series_pow(HK, c - 1, order)
    out = []
    for n in range(order + 1):
        acc = None
        for j in range(n + 1):
            if P[n - j] is None:
                continue
            t = P[n - j] * HS[j]
            acc = t if acc is None else acc + t
        out.append(acc.scale(c) if acc is not None else None)
    return out


def representable_frac(f, dx, dy, den):
    """Is P/Q = N/den with N a polynomial of degree <= (dx, dy) in (x, y)?  Exact."""
    if f is None or f.P == 0:
        return True
    R = PB._ring()
    G = f.P * R.from_expr(sp.expand(den))
    N, r = G.div(f.Q)
    if r != 0:
        return False
    return N.degree(0) <= dx and N.degree(1) <= dy


def floor_representable(c, H, HS, dx, dy, den):
    """(ok, [ok_n for n = 0, 1, 2]) for the direction H^c (times any p_t^a p_phi^b)."""
    Hk = [_Frac.of(h) for h in H]
    Hs = [_Frac.of(h) for h in HS]
    per = [representable_frac(f, dx, dy, den) for f in corrections(c, Hk, Hs)]
    return all(per), per


if __name__ == "__main__":
    # VALIDATION: the ring test == PB.representable on the same expressions, in BOTH verdicts;
    # the series == the old formula where they must agree (c <= 2, n = 2); and the c = 3 answer.
    import os
    import sys
    import time
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _kt_double as KD
    import _kt_exact as EX
    import _kt_metrics as MM
    import _kt_search as K

    t_, ph = sp.symbols("t phi", real=True)
    K.set_dim((t_, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    GI = KD.kerr_chi_pieces()
    L, _, _ = MM.denominator(GI[0])
    H = [KD.hamiltonian(GI[n]) for n in range(3)]
    HS = [KD.hamiltonian(M) for M in KD.sgb_ginv_pieces(GI)]
    Hk = [_Frac.of(h) for h in H]
    Hs = [_Frac.of(h) for h in HS]
    ok = True

    def expr_of(f):
        return f.P.as_expr() / f.Q.as_expr()

    # 1. the series reproduces the old formula where the old formula is right (c = 1, 2; n = 2)
    def equal(f, g):                      # P1/Q1 == P2/Q2  <=>  P1 Q2 == P2 Q1, in the ring
        return f.P * g.Q == g.P * f.Q

    for c in (1, 2):
        new = corrections(c, Hk, Hs)[2]
        old = Hs[2] if c == 1 else None
        if c == 2:
            for i in range(3):
                t = (Hk[i] * Hs[2 - i]).scale(2)
                old = t if old is None else old + t
        same = equal(new, old)
        print(f"  c={c}: series C_2 == old formula: {same}", flush=True)
        ok &= same
    # ... and does NOT where the old one is wrong (c = 3): they must differ
    new3 = corrections(3, Hk, Hs)[2]
    old3 = None
    for i in range(3):
        t = (Hk[i] * Hk[i] * Hs[2 - i]).scale(3)
        old3 = t if old3 is None else old3 + t
    differ = not equal(new3, old3)
    print(f"  c=3: series C_2 differs from the old formula (it must): {differ}", flush=True)
    ok &= differ

    # 2. ring representability == PB.representable, both verdicts (rank 4: c=2 fails at denpow 6
    #    and passes at denpow 7 -- the D44 case), on every piece n = 0, 1, 2
    for rank, denpow, margin in ((4, 6, 6), (4, 7, 6)):
        den = L ** denpow
        _, prods, _ = EX.generators(GI[0], rank, den)
        bx, by = EX.reducible_box(prods, den)
        dx, dy = bx + margin, by + margin
        for c in (1, 2):
            fr = corrections(c, Hk, Hs)
            t0 = time.time(); fast = [representable_frac(f, dx, dy, den) for f in fr]; tf = time.time() - t0
            t0 = time.time(); ref = [PB.representable(expr_of(f), dx, dy, den) for f in fr]; tr = time.time() - t0
            print(f"  rank {rank} denpow {denpow} box {dx}x{dy} c={c}: ring {fast} ({tf:.1f}s)  "
                  f"expr {ref} ({tr:.1f}s)  agree {fast == ref}", flush=True)
            ok &= fast == ref
    print("\n  " + ("VALIDATED: ring floor test == expression test; series == old formula for c<=2."
                    if ok else "FAILED"))

    # 3. THE QUESTION: rank 6, denpow 8, box 30x28, c = 3, correct pieces.
    den = L ** 8
    t0 = time.time()
    allok, per = floor_representable(3, H, HS, 30, 28, den)
    print(f"\n  rank 6 denpow 8 box 30x28, H^3: pieces n=0,1,2 representable {per} -> "
          f"{'REPRESENTABLE' if allok else 'NOT representable'}  ({time.time() - t0:.1f}s)")
    print(f"  (the old formula's expression, same test: {representable_frac(old3, 30, 28, den)})")
    sys.exit(0 if ok else 1)
