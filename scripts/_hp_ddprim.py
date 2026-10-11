"""Double-double (DD) arithmetic primitives for numba: a value is a pair (hi, lo) with |lo| <= ulp(hi)/2, giving
~106 bits (~32 significant digits). Error-free transformations after Dekker (1971) and Knuth (TAOCP 4.2.2), in the
"accurate" variants of Hida-Li-Bailey's QD library. No FMA is assumed (Dekker split), so results do not depend on
whether the compiler contracts a*b+c. Every function returns a (hi, lo) tuple.
Used by scripts/_hp_dd.py (high-precision probe, data/ts_chaos/HP_PREREGISTRATION.md)."""
import math

import numba

njit = numba.njit(fastmath=False, cache=True)     # NOT inline="always": the generated TS RHS makes ~1000 calls; IR-level inlining made numba compile time explode (killed after 10 min). LLVM still inlines these small functions.


@njit
def two_sum(a, b):
    s = a + b
    bb = s - a
    return s, (a - (s - bb)) + (b - bb)


@njit
def quick_two_sum(a, b):
    s = a + b
    return s, b - (s - a)


@njit
def split(a):
    t = 134217729.0 * a                  # 2^27 + 1
    hi = t - (t - a)
    return hi, a - hi


@njit
def two_prod(a, b):
    p = a * b
    ah, al = split(a)
    bh, bl = split(b)
    return p, ((ah * bh - p) + ah * bl + al * bh) + al * bl


@njit
def dd_add(ah, al, bh, bl):
    s, e = two_sum(ah, bh)
    t, f = two_sum(al, bl)
    e += t
    s, e = quick_two_sum(s, e)
    e += f
    return quick_two_sum(s, e)


@njit
def dd_sub(ah, al, bh, bl):
    return dd_add(ah, al, -bh, -bl)


@njit
def dd_mul(ah, al, bh, bl):
    p, e = two_prod(ah, bh)
    e += ah * bl + al * bh
    return quick_two_sum(p, e)


@njit
def dd_mul_d(ah, al, b):
    p, e = two_prod(ah, b)
    e += al * b
    return quick_two_sum(p, e)


@njit
def dd_div(ah, al, bh, bl):
    q1 = ah / bh
    ph, pl = dd_mul_d(bh, bl, q1)
    rh, rl = dd_sub(ah, al, ph, pl)
    q2 = rh / bh
    ph, pl = dd_mul_d(bh, bl, q2)
    rh, rl = dd_sub(rh, rl, ph, pl)
    q3 = rh / bh
    q1, q2 = quick_two_sum(q1, q2)
    return dd_add(q1, q2, q3, 0.0)


@njit
def dd_sqrt(ah, al):
    if ah <= 0.0:
        return 0.0, 0.0
    s = math.sqrt(ah)
    ph, pl = two_prod(s, s)
    rh, rl = dd_sub(ah, al, ph, pl)
    return quick_two_sum(s, rh / (2.0 * s))
