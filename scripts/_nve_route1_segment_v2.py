#!/usr/bin/env python3
"""Route (i), the first CERTIFIED segment, VERSION 2: spin 3/5, E = 4/5, real k in [1, 1.1]  (data/nve/ROUTE1_SEGMENT.md).
[model: Fable 5.2; UNVERIFIED until the office ansatz-machine checks it]

Claim certified when the run prints VERDICT: CERTIFIED: for every real k in [1, 1.1],
    F(k) != 0,  tr M0(k) != 0,  tr M1(k) not in [-2, 2],
with M0 the circle polygon |z| = 1.35 and M1 the engine's lasso polygon of k_c = 21/20 (data/nve/eps/route1_floats.json).

Run with Quantum's pinned interpreter, read-only:
    /Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_segment_v2.py prove 1
    ... _nve_route1_segment_v2.py verdict 1 partB   (the verdict on the node values of the Part B evaluator)
    ... _nve_route1_segment_v2.py nodes 1 arb       (point evaluations by THIS file's all-ball evaluator; resumable)
    ... _nve_route1_segment_v2.py verdict 1 arb     (the verdict on those)
Outputs: data/nve/eps/route1_seg_*v2*, route1_seg_nodes_arb.jsonl.   One process, 1 core, peak well under 300 MB.

VERSION 2 (2026-11-26, the Bridge's follow-up to _nve_route1_segment.py, which is left as committed in 604d520):
every BOUND is a ball (Arb) from the first evaluation to the printed verdict numbers. Python floats remain only as
CHOICES, any value of which would be valid: the polygon vertices and step points (exact binary numbers, converted
exactly), the disc radius rho of a step, the Bernstein rho, n, the gauge matrix C, the sample points of the controls.
Printed bounds are rounded outward in decimal (lo_dec, hi_sci).

The chain:
 1. Laurent-disc precondition: for every k in the k-box, the zeros of 1 - k phi (closed form), the pole of phi and
    the poles of c_K'' lie strictly outside the disc |omega| <= 0.9/a (omega = 1/z), so c0'' is holomorphic there.
 2. Reference: the validated solution at k_c along both loops; on every step the first row (v1, v2) of the
    fundamental matrix is enclosed on the WHOLE step segment (Taylor polynomial on a ball + its tail).
 3. Perturbation: on a box Z containing each step segment and the k-box K (a square containing the disc |k - k_c| <= R),
    an enclosure of dq/dk by the chain rule on balls, in the combined form (2b) of _nve_route1_kc_identity.py.
    d c0/dk, d c0'/dk at k_c: the k-derivative of the Laurent series, with its own Cauchy tail. Over K, cut into
    KSUB x KSUB sub-boxes dk: Taylor in k with the second k-derivative (a radial integral from infinity, enclosed on
    the whole of K by a rectangle rule on balls) as the remainder.
    G1 != 0, G2 != 0 and Re(1 - k phi) > 0 are certified on every box (holomorphy in k, and no singular point reaches
    the loops).  |q(k) - q(k_c)| <= R sup |dq/dk| (K is convex).
 4. Dyson, in a constant gauge C: Y_k = Phi_c C T C^-1, T' = -dq (Phi_c C)^-1 E21 (Phi_c C) T, and with det Phi_c = 1
    (Abel) ||(Phi_c C)^-1 E21 (Phi_c C)||_2 = |(v1, v2) C|^2 / |det C|.  So ||T||_2 <= exp(I),
    I = R * sum sup|dq/dk| sup |(v1, v2) C|^2 |h| / |det C|.  ANY invertible C gives a valid bound.
 5. M:  ||M(k)||_F <= ||M(k_c) C||_F ||C^-1||_F e^I;  |tr M(k)| <= sqrt2 ||C^-1 M(k_c) C||_F e^I;
        |F(k)| <= 2 + ||M1(k)||_F^2 ||M0(k)||_F^2   (2x2, det 1: ||X^-1||_F = ||X||_F).
 6. ATAP Thm 8.2 (read at source by the office): |f - p_n| <= 4 M rho^-n / (rho - 1) on the segment.
 7. The interpolant's enclosure on balls of theta covering [0, pi] (t = cos theta), +- the bound.

The point evaluator here (laurent, c0_at, step, walk, evaluate) is the Part B one (_nve_route1_proto.py) with three
changes: (a) the three tail bounds are balls, not floats with a 1e-7 inflation; (b) every step ends on an exact
binary point and every polygon edge ends exactly on its vertex (the Part B walk computes the end point of an edge in
floats, which can miss the vertex by one unit in the last place); (c) a step also returns the enclosure on its whole
segment. Part B's file is untouched.
"""
import json
import math
import os
import resource
import sys
import time
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal, getcontext

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flint                                     # noqa: E402
from flint import acb, acb_series, arb, ctx      # noqa: E402
import _nve_route1_proto as P                    # noqa: E402  (sets ctx.prec = 256; used: horner, mmul, minv, rad)

A, E2, NT, NW = P.A, P.E2, P.NT, P.NW
OUTD = os.path.join(P.ROOT, "data", "nve", "eps")
LOG = os.path.join(OUTD, "route1_seg_3_5_v2.out")
NODEFILE = dict(arb=os.path.join(OUTD, "route1_seg_nodes_arb.jsonl"), partB=os.path.join(OUTD, "route1_seg_nodes.jsonl"))
SEG = "spin 3/5|k in [1, 1.1]"
TOL_F = 1e-3                                     # target for the choice of n (a choice, not a bound)
SM = 24                                          # sub-intervals of the radial integrals
KSUB = 5                                         # the k-box is cut into KSUB x KSUB sub-boxes
RHOS = (3.0, 4.0, 5.0, 6.5, 8.0, 10.0)           # exact binary numbers
NSUB = 256                                       # balls of theta
getcontext().prec = 400                          # decimal digits for the outward-rounded printing only
UNIT = acb(arb(0, 1), arb(0, 1))                 # the box [-1, 1] + i [-1, 1]
I01 = arb(0, 1)                                  # the interval [-1, 1]


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG, "a") as fh:
        fh.write(s + "\n")


def amax(xs):
    """Largest of a sequence of POINT arbs (exact numbers; comparisons are decidable)."""
    cur = None
    for x in xs:
        if cur is None or x > cur:
            cur = x
    return cur


def lo_dec(x, d=6):
    """A decimal string with d places, CERTIFIED <= x (x an arb)."""
    v = x.lower()
    q = Decimal(10) ** -d
    c = Decimal(repr(float(v))).quantize(q, rounding=ROUND_FLOOR)
    while not arb(format(c, "f")) <= v:
        c -= q
    return format(c, "f")


def hi_sci(x, sig=4):
    """A decimal string with sig significant digits, CERTIFIED >= x (x an arb, x > 0)."""
    v = x.upper()
    c = Decimal(repr(float(v)))
    q = Decimal(10) ** (c.adjusted() - sig + 1)
    c = c.quantize(q, rounding=ROUND_CEILING)
    while not arb(format(c, "f")) >= v:
        c += q
    return f"{c:.{sig - 1}E}"


def ser(x):
    """An arb as a string whose parse contains it."""
    return x.str(50)


def par_up(s):
    return arb(s).upper()


# --------------------------------------------------------------------------------- 1. Laurent-disc precondition
def precondition(K):
    """K: acb box of k. ok iff CERTIFIED that c0'' = c_K'' sqrt(1 - k phi) is holomorphic on |omega| <= 0.9/a for
    every k in K. In w = z^2/a^2 the disc is |w| >= 1/0.81, so every singular w must have |w| < 1/0.81:
    zeros of 1 - k phi: w = [(30 - 9k) +- sqrt(60 k (k - 4))] / (90 - 21 k); pole of phi: w = 1/3; poles of c_K'': w = -1."""
    lim = 1 / (arb("0.9") * arb("0.9"))
    den = 90 - 21 * K
    out = dict(k_box=[str(K.real), str(K.imag)], lim=float(lim.lower()))
    if den.contains(0):
        out.update(ok=False, why="90 - 21 k contains 0: a root is at infinity")
        return out
    sq = (60 * K * (K - 4)).sqrt()
    roots = [((30 - 9 * K) + sq) / den, ((30 - 9 * K) - sq) / den]
    if not all(r.is_finite() for r in roots):
        out.update(ok=False, why="root enclosure not finite")
        return out
    mx = amax(r.abs_upper() for r in roots)
    out.update(max_root_abs_w=float(mx), ok=bool(mx < lim) and bool(arb(1) < lim) and bool(arb(1) / 3 < lim))
    if not out["ok"]:
        out["why"] = f"a zero of 1 - k phi has |w| up to {float(mx):.4f} >= {float(lim.lower()):.4f}: inside the Laurent disc"
    return out


# --------------------------------------------------------------------------------- the point evaluator, all in balls
def laurent(k, deriv=False):
    """d_n with c0'' = sum_n d_n omega^n (deriv: d c0''/dk = -c_K'' phi / (2 sqrt(1 - k phi))), and a Cauchy bound M
    (a point arb) of the function on |omega| = 0.9/a, by 400 arcs. Needs the precondition."""
    ctx.cap = NW + 2
    w = acb_series([0, 1])
    a2w2 = w * w * (A * A)
    cK2 = w * w * w * w * (-4 * A) * (3 - a2w2) / ((1 + a2w2) * (1 + a2w2) * (1 + a2w2))
    phi = (21 - 18 * a2w2 + a2w2 * a2w2) / (10 * (3 - a2w2) * (3 - a2w2))
    sq = (1 - k * phi).sqrt()
    d = (cK2 * phi * (-1) / (sq * 2)).coeffs() if deriv else (cK2 * sq).coeffs()
    d = d + [acb(0)] * (NW + 2 - len(d))
    rw = arb("0.9") / A
    NA = 400
    vals = []
    for j in range(NA):
        th = arb.pi() * (2 * j + 1) / NA + I01 * arb.pi() / NA            # the arcs cover the circle exactly
        ww = acb(0, th).exp() * rw
        x = ww * ww * (A * A)
        ph = (21 - 18 * x + x * x) / (10 * (3 - x) * (3 - x))
        s = (1 - k * ph).sqrt()
        val = ww * ww * ww * ww * (-4 * A) * (3 - x) / ((1 + x) * (1 + x) * (1 + x)) * (ph / (s * 2) if deriv else s)
        if not val.is_finite():
            raise RuntimeError("Laurent tail bound: non-finite on |omega| = 0.9/a")
        vals.append(val.abs_upper())
    return d, amax(vals), rw


def c0_at(z, lau):
    """(c0, c0') on the ball z (or their k-derivatives, for lau = laurent(k, True)), with the Laurent tail added."""
    d, M, rw = lau
    w = 1 / z
    c0 = P.horner([d[n] / ((n - 1) * (n - 2)) for n in range(4, NW + 1)], w) * w * w
    c0p = -P.horner([d[n] / (n - 1) for n in range(4, NW + 1)], w) * w * w * w
    wm = w.abs_upper()
    th = (wm / rw).upper()
    if not th < arb("0.95"):
        raise RuntimeError("point too close to the Laurent circle")
    t = M * th ** (NW + 1) / (1 - th)
    return c0 + (t / (wm * wm)).upper() * UNIT, c0p + (t / wm).upper() * UNIT


def q_ball(z, k, lau):
    Dp = z * z + A * A
    f0 = (z * z - 2 * z + A * A) / Dp
    f0p = 2 * (z * z - A * A) / (Dp * Dp)
    c0, c0p = c0_at(z, lau)
    G2 = f0 * f0 + c0 * c0
    dG2 = 2 * (f0 * f0p + c0 * c0p)
    G1 = E2 * G2 - f0
    dG1 = E2 * dG2 - f0p
    if G1.contains(0) or G2.contains(0):
        return None
    lam = dG1 / G1 - dG2 / G2
    q = lam * lam * 3 / 16
    return q if q.is_finite() else None


def step(zc, hvec, k, lau, rho):
    """One Taylor step from the exact point zc to zc + hvec. -> (T, Y, Z, hm) or None.
    T: fundamental matrix; Y = (Y1, Y2): enclosures of the two local solutions on the WHOLE segment {zc + t hvec};
    Z: a box containing that segment; hm: an upper bound of |hvec| (point arb).
    Tail: |v_j| <= K mu^j for all j, mu = 2/rho, once Q rho^2 <= 0.9 * 2 NT (NT+1), Q >= sup |q| on the box of
    half-side rho around zc (a box on which G1 or G2 could vanish is refused)."""
    rb = arb(rho)
    Q = q_ball(zc + rb * UNIT, k, lau)
    if Q is None:
        return None
    if not Q.abs_upper() * rb * rb < arb(2 * NT * (NT + 1) * 9) / 10:
        return None
    ctx.cap = NT + 3
    t = acb_series([zc, 1])
    z2 = t * t
    u2 = z2 / (A * A)
    cK2 = (3 * u2 - 1) * (-4) / ((u2 + 1) * (u2 + 1) * (u2 + 1) * (A * A * A))
    phi = (21 * u2 * u2 - 18 * u2 + 1) / (10 * (3 * u2 - 1) * (3 * u2 - 1))
    c0pp = cK2 * (1 - k * phi).sqrt()
    c0v, c0pv = c0_at(zc, lau)
    c0p = c0pp.integral() + c0pv
    c0 = c0p.integral() + c0v
    f0 = (z2 - 2 * t + A * A) / (z2 + A * A)
    f0p = f0.derivative()
    G2 = f0 * f0 + c0 * c0
    dG2 = 2 * (f0 * f0p + c0 * c0p)
    G1 = E2 * G2 - f0
    dG1 = E2 * dG2 - f0p
    lam = dG1 / G1 - dG2 / G2
    qc = (lam * lam * 3 / 16).coeffs()
    if len(qc) < NT - 1:
        qc = qc + [acb(0)] * (NT - 1 - len(qc))
    mu = 2 / rb
    hm = hvec.abs_upper()
    x = (mu * hm).upper()
    assert x < arb(51) / 100
    hb = hvec / 2 + (hm / 2) * UNIT              # contains {t hvec, 0 <= t <= 1}
    cols, Y = [], []
    for v0, v1 in ((acb(1), acb(0)), (acb(0), acb(1))):
        v = [v0, v1]
        for j in range(NT - 1):
            s = acb(0)
            for i in range(j + 1):
                s += qc[i] * v[j - i]
            v.append(-s / ((j + 1) * (j + 2)))
        Kc = amax((v[j].abs_upper() / mu ** j).upper() for j in range(NT + 1))
        tail = (Kc * x ** (NT + 1) / (1 - x)).upper()
        dtail = (Kc * mu * (NT + 1) * x ** NT / ((1 - x) * (1 - x))).upper()
        val = P.horner(v, hvec) + tail * UNIT
        der = P.horner([v[j] * j for j in range(1, NT + 1)], hvec) + dtail * UNIT
        cols.append((val, der))
        Y.append(P.horner(v, hb) + tail * UNIT)  # the tail bound is monotone in |h'|, so it covers the segment
    T = [[cols[0][0], cols[1][0]], [cols[0][1], cols[1][1]]]
    if not all(e.is_finite() for r in T for e in r) or not all(y.is_finite() for y in Y):
        return None
    return T, Y, zc + hb, hm


def walk(vertices, k, lau, sing, record=False):
    """Transport along the closed polygon through `vertices` (complex floats = exact binary points).
    Every step runs from an exact point to an exact point; the last step of an edge ends ON the vertex.
    record: also return, per step, (Z, hm, a1, a2): a box containing the step segment, an upper bound of its length,
    and enclosures of the first row (v1, v2) of the fundamental matrix on the whole segment."""
    assert vertices[0] == vertices[-1], "the polygon is not closed"
    M = [[acb(1), acb(0)], [acb(0), acb(1)]]
    steps, nst = [], 0
    for P0, P1 in zip(vertices[:-1], vertices[1:]):
        pos = P0
        while pos != P1:
            dist = min([abs(pos - s) for s in sing] + [abs(pos) - 1.0])
            rho = 0.5 * dist
            rem = abs(P1 - pos)
            while True:
                nxt = P1 if rem <= rho / 4 else pos + (P1 - pos) * ((rho / 4) / rem)
                zc = acb(pos.real, pos.imag)
                zn = acb(nxt.real, nxt.imag)
                r = step(zc, zn - zc, k, lau, rho)
                if r is not None:
                    break
                rho /= 2
                if rho < 1e-4:
                    raise RuntimeError(f"no admissible disc at {pos}")
            T, Y, Z, hm = r
            if record:
                assert Z.contains(zc) and Z.contains(zn)          # the box holds both ends of the step
                a1 = Y[0] * M[0][0] + Y[1] * M[1][0]
                a2 = Y[0] * M[0][1] + Y[1] * M[1][1]
                steps.append((Z, hm, a1, a2))
            M = P.mmul(T, M)
            pos, nst = nxt, nst + 1
    return M, (steps if record else nst)


def circle_vertices(n=96):
    r0 = 1.35
    return [complex(r0 * math.cos(2 * math.pi * j / n), r0 * math.sin(2 * math.pi * j / n)) for j in range(n)] + [complex(r0, 0)]


def evaluate(kre, kim, ref):
    """tr M0, tr M1, F at the POINT k = mid(kre) + i mid(kim), on the circle polygon and the lasso of `ref`."""
    t0 = time.time()
    k = acb(kre.mid(), kim.mid())
    lau = laurent(k)
    sing = [complex(float(p[0]), float(p[1])) for p in ref["points"]]
    lasso = [complex(float(p[0]), float(p[1])) for p in ref["lasso"]]
    M0, n0 = walk(circle_vertices(), k, lau, sing)
    M1, n1 = walk(lasso, k, lau, sing)
    Cm = P.mmul(P.mmul(M1, M0), P.mmul(P.minv(M1), P.minv(M0)))
    F = Cm[0][0] + Cm[1][1] - 2
    T0, T1 = M0[0][0] + M0[1][1], M1[0][0] + M1[1][1]
    return dict(k=[str(k.real), str(k.imag), 0], F=[str(F.real), str(F.imag)], T0=[str(T0.real), str(T0.imag)],
                T1=[str(T1.real), str(T1.imag)], rad_F=P.rad(F), steps=[n0, n1], sec=round(time.time() - t0, 2))


# --------------------------------------------------------------------------------- 3. dq/dk on Z x K
SB = [arb(2 * j + 1) / (2 * SM) + I01 / (2 * SM) for j in range(SM)]      # balls of s covering [0, 1]
SUBS = [arb.pi() * (2 * i + 1) / (2 * NSUB) + I01 * arb.pi() / (2 * NSUB) for i in range(NSUB)]   # theta, covering [0, pi]


def coverage_asserts():
    """Fails if the balls of s do not cover [0, 1] or the balls of theta do not cover [0, pi]."""
    for j in range(SM):
        assert SB[j].contains(arb(j) / SM) and SB[j].contains(arb(j + 1) / SM)
    for i in range(NSUB):
        assert SUBS[i].contains(arb.pi() * i / NSUB) and SUBS[i].contains(arb.pi() * (i + 1) / NSUB)


def d2kc0(Z, K):
    """Enclosures of d^2 c0/dk^2 and d^2 c0'/dk^2 on Z x K:  z^-2 int_0^1 (s - s^2) g2(s/z) ds,  -z^-3 int_0^1 s^2 g2 ds,
    g2 = omega^-4 d^2 c0''/dk^2 = g phi / (2 (1 - k phi)),  g = 4a (21 - 18x + x^2) / (20 (3 - x)(1 + x)^3 sqrt(1 - k phi)),
    x = a^2 omega^2. Rectangle rule: on each of the SM balls of s the integrand is ENCLOSED (not sampled), times the
    width 1/SM. None if Re(1 - k phi) > 0 is not certified on a ball."""
    ob = 1 / Z
    i0, i1 = acb(0), acb(0)
    for S in SB:
        om = ob * S
        x = om * om * (A * A)
        num = 21 - 18 * x + x * x
        ph = num / (10 * (3 - x) * (3 - x))
        rad = 1 - K * ph
        if not rad.real > 0:
            return None
        g2 = num * (4 * A) / (20 * (3 - x) * (1 + x) * (1 + x) * (1 + x) * rad.sqrt()) * ph / (rad * 2)
        i1 += S * S * g2
        i0 += S * (1 - S) * g2
    return i0 * ob * ob / SM, -i1 * ob * ob * ob / SM


def dq_sup(Z, K, dKs, lau_c, laud_c):
    """(sup |dq/dk| on Z x K as a point arb, number of k-sub-boxes evaluated), or None if holomorphy is not certified.
    dKs: None for K a point; else boxes dk covering K - k_c. On each, by Taylor in k with the second derivative
    (E0, E1) enclosed on the whole of K (convex):
        d c0/dk = D0c + dk E0,   c0 = c0c + dk D0c + dk^2 E0 / 2     (same for c0')."""
    c0c, c0pc = c0_at(Z, lau_c)
    D0c, D1c = c0_at(Z, laud_c)
    if dKs is None:
        dKs, E0, E1 = [acb(0)], acb(0), acb(0)
    else:
        e = d2kc0(Z, K)
        if e is None:
            return None
        E0, E1 = e
    Dp = Z * Z + A * A
    f0 = (Z * Z - 2 * Z + A * A) / Dp
    f0p = 2 * (Z * Z - A * A) / (Dp * Dp)
    worst, nb = None, 0
    for dk in dKs:
        D0, D1 = D0c + dk * E0, D1c + dk * E1
        dk2 = dk * dk / 2
        c0 = c0c + dk * D0c + dk2 * E0
        c0p = c0pc + dk * D1c + dk2 * E1
        G2 = f0 * f0 + c0 * c0
        dG2 = 2 * (f0 * f0p + c0 * c0p)
        G1 = E2 * G2 - f0
        dG1 = E2 * dG2 - f0p
        if G1.contains(0) or G2.contains(0):
            return None
        G12 = G1 * G2
        lam = dG1 / G1 - dG2 / G2
        X = 2 * f0 * c0 * D0 / G12
        dlam = 2 * (f0p * c0 * D0 + f0 * c0p * D0 + f0 * c0 * D1) / G12 - X * (dG1 / G1 + dG2 / G2)
        dq = lam * dlam * 3 / 8
        if not dq.is_finite():
            return None
        u = dq.abs_upper()
        worst = u if worst is None or u > worst else worst
        nb += 1
    assert nb == len(dKs) and worst.is_finite()
    return worst, nb


def kbox(kc, R):
    """(K, sub-boxes of K - k_c): K the closed square of half-side R (a point arb) around k_c, cut into KSUB x KSUB
    closed sub-boxes. NONE is dropped; the asserts fail if they do not cover the square."""
    K = kc + R * UNIT
    if not R > 0:
        return K, None
    r = R / KSUB
    edges = [-R + 2 * i * r for i in range(KSUB + 1)]
    cells = [(-R + (2 * i + 1) * r) + r * I01 for i in range(KSUB)]
    for i in range(KSUB):
        assert cells[i].contains(edges[i]) and cells[i].contains(edges[i + 1])
    assert edges[0].contains(-R) and edges[KSUB].contains(R)
    subs = [acb(cx, cy) for cx in cells for cy in cells]
    assert len(subs) == KSUB * KSUB
    return K, subs


def dq_list(steps, kc, R, lau_c, laud_c):
    """sup |dq/dk| on every step box (point arbs) and the number of (step box, k-sub-box) pairs enclosed; or
    (None, where) if a holomorphy box fails. The asserts fail if any step box or any k-sub-box was skipped."""
    K, dKs = kbox(kc, R)
    nk = 1 if dKs is None else len(dKs)
    out, tot = [], 0
    for Z, _hm, _a1, _a2 in steps:
        r = dq_sup(Z, K, dKs, lau_c, laud_c)
        if r is None:
            return None, complex(Z.real.mid(), Z.imag.mid())
        out.append(r[0])
        tot += r[1]
    assert len(out) == len(steps) and tot == len(steps) * nk and all(x.is_finite() for x in out)
    return out, tot


def gauge(steps, dqs):
    """A constant matrix C (floats, det ~ 1) minimising sum dq |(a1, a2) C|^2 h in midpoint arithmetic:
    C C^dagger = sqrt(det W) W^-1,  W = sum dq h r^dagger r.  A CHOICE, not part of the proof: any invertible C gives
    a valid bound, and dyson_sum / gauge_norms recompute everything for this C in balls."""
    W11 = W22 = 0.0
    W12 = 0j
    for (Z, hm, a1, a2), dq in zip(steps, dqs):
        x1 = complex(a1.real.mid(), a1.imag.mid())
        x2 = complex(a2.real.mid(), a2.imag.mid())
        w = float(dq) * float(hm)
        W11 += w * abs(x1) ** 2
        W22 += w * abs(x2) ** 2
        W12 += w * x1.conjugate() * x2
    l11 = math.sqrt(W11)
    l21 = W12.conjugate() / l11
    l22 = math.sqrt(max(W22 - abs(l21) ** 2, 1e-30))
    s = math.sqrt(l11 * l22)
    return [[s / l11, -s * l21.conjugate() / (l11 * l22)], [0.0, s / l22]]


def cmat(C):
    """The float matrix C as balls, exactly (binary floats convert without rounding)."""
    return [[acb(complex(C[i][j]).real, complex(C[i][j]).imag) for j in range(2)] for i in range(2)]


def dyson_sum(steps, dqs, C):
    """sum sup|dq/dk| sup |(v1, v2) C|^2 |h| / |det C|   (a point arb, an upper bound; the exponent per unit |k - k_c|)."""
    Cb = cmat(C)
    det = Cb[0][0] * Cb[1][1] - Cb[0][1] * Cb[1][0]
    assert not det.contains(0)
    tot = arb(0)
    for (Z, hm, a1, a2), dq in zip(steps, dqs):
        b1 = a1 * Cb[0][0] + a2 * Cb[1][0]
        b2 = a1 * Cb[0][1] + a2 * Cb[1][1]
        tot += dq * hm * (b1.abs_upper() ** 2 + b2.abs_upper() ** 2)
    out = (tot / det.abs_lower()).upper()
    assert out.is_finite()
    return out


def fro(M):
    """Upper bound of the Frobenius norm (point arb)."""
    return sum((M[i][j].abs_upper() ** 2 for i in range(2) for j in range(2)), arb(0)).sqrt().upper()


def gauge_norms(M, C):
    """(||M C||_F ||C^-1||_F,  ||C^-1 M C||_F,  ||C||_F ||C^-1||_F), upper bounds."""
    Cb = cmat(C)
    Ci = P.minv(Cb)
    return (fro(P.mmul(M, Cb)) * fro(Ci)).upper(), fro(P.mmul(Ci, P.mmul(M, Cb))), (fro(Cb) * fro(Ci)).upper()


def selftest(kc, lau_c, laud_c):
    """Can fail: at k = k_c, the enclosures of d c0/dk, d c0'/dk against central differences in k, the second
    derivative against its difference, and |FD of q| <= sup |dq/dk| (the ratio measures how tight the enclosure is)."""
    h = arb(1) / 10 ** 6
    lp, lm = laurent(acb(kc + h)), laurent(acb(kc - h))
    ldp, ldm = laurent(acb(kc + h), True), laurent(acb(kc - h), True)
    ok = True
    for zz in (complex(0.3, 1.3162), complex(-1.35, 0.0), complex(1.757, -0.003), complex(2.05, -0.03), complex(2.11, 0.55)):
        Z = acb(zz.real, zz.imag)
        D0, D1 = c0_at(Z, laud_c)
        cp, cm = c0_at(Z, lp), c0_at(Z, lm)
        fd0, fd1 = (cp[0] - cm[0]) / (2 * h), (cp[1] - cm[1]) / (2 * h)
        fdq = (q_ball(Z, acb(kc + h), lp) - q_ball(Z, acb(kc - h), lm)) / (2 * h)
        sup = dq_sup(Z, acb(kc), None, lau_c, laud_c)[0]
        e0 = float((D0 - fd0).abs_upper())
        e1 = float((D1 - fd1).abs_upper())
        rq = float(fdq.abs_lower()) / float(sup)
        e2 = d2kc0(Z, acb(kc))
        f2 = (c0_at(Z, ldp)[0] - c0_at(Z, ldm)[0]) / (2 * h)
        o2 = bool(e2[0].overlaps(f2 + arb("1e-8") * UNIT))
        good = e0 < 1e-8 and e1 < 1e-8 and 0.5 < rq <= 1.0000001 and o2
        ok &= good
        say(f"    z = {zz}: |D0 - FD| <= {e0:.1e}, |D1 - FD| <= {e1:.1e}; |FD dq/dk| / sup = {rq:.6f}; "
            f"second derivative enclosure overlaps its FD: {o2}  -> {'ok' if good else 'FAIL'}")
    return ok


# --------------------------------------------------------------------------------- stage: prove
def seg_centres(nseg):
    return [(arb(1) + arb(2 * i + 1) / (20 * nseg), arb(1) / (20 * nseg)) for i in range(nseg)]


def fmtC(C):
    return "[[" + "], [".join(", ".join(f"{complex(x):.6f}" for x in r) for r in C) + "]]"


def prove(nseg, *_):
    t0 = time.time()
    coverage_asserts()
    refs = json.load(open(os.path.join(OUTD, "route1_floats.json")))
    ref = refs["21/20"]
    sing = [complex(float(p[0]), float(p[1])) for p in ref["points"]]
    lasso = [complex(float(p[0]), float(p[1])) for p in ref["lasso"]]
    say(f"== prove (v2, all bounds in balls) == NSEG = {nseg}; python {sys.version.split()[0]}, python-flint {flint.__version__}, "
        f"interpreter {sys.executable}; prec {ctx.prec} bits, Taylor order {NT}, Laurent order {NW}; {SEG}; lasso and "
        f"singular points of k = 21/20 from route1_floats.json; k sub-boxes {KSUB} x {KSUB}, {SM} balls of s")
    segs = []
    for i, (kc, half) in enumerate(seg_centres(nseg)):
        ts = time.time()
        kcs = f"{float(kc.mid()):.6f}"
        lau_c, laud_c = laurent(acb(kc)), laurent(acb(kc), True)
        say(f"  -- sub-segment {i}: k_c = {kcs}, half-width {float(half.mid()):.6f} --")
        st_ok = selftest(kc, lau_c, laud_c)
        say(f"  derivative self-test passes: {st_ok}")
        M0, st0 = walk(circle_vertices(), acb(kc), lau_c, sing, record=True)
        M1, st1 = walk(lasso, acb(kc), lau_c, sing, record=True)
        Cm = P.mmul(P.mmul(M1, M0), P.mmul(P.minv(M1), P.minv(M0)))
        Fc = Cm[0][0] + Cm[1][1] - 2
        say(f"  reference: circle {len(st0)} steps, lasso {len(st1)} steps, {time.time() - ts:.0f} s; ||M0||_F <= {hi_sci(fro(M0), 7)}, "
            f"||M1||_F <= {hi_sci(fro(M1), 7)}; F = {complex(Fc.real.mid(), Fc.imag.mid()):.10f}")
        ident = [[1.0, 0.0], [0.0, 1.0]]
        pt = []
        for st in (st0, st1):
            dqs, _n = dq_list(st, kc, arb(0), lau_c, laud_c)
            C = gauge(st, dqs)
            pt.append((dyson_sum(st, dqs, ident), dyson_sum(st, dqs, C)))
        say(f"  Dyson constants at k_c (exponent per unit |k - k_c|, K a point): circle <= {hi_sci(pt[0][0])} (base "
            f"basis), <= {hi_sci(pt[0][1])} (optimised gauge); lasso <= {hi_sci(pt[1][0])}, <= {hi_sci(pt[1][1])}")
        rows = []
        for rho in RHOS:
            rb = arb(rho)
            R = (half * (rb + 1 / rb) / 2).upper()
            pre = precondition(kbox(kc, R)[0])
            if not pre["ok"]:
                say(f"  rho = {rho}: R = {float(R):.4f}: Laurent-disc precondition NOT certified ({pre['why']})")
                continue
            d0, w0 = dq_list(st0, kc, R, lau_c, laud_c)
            d1, w1 = dq_list(st1, kc, R, lau_c, laud_c) if d0 is not None else (None, None)
            if d0 is None or d1 is None:
                say(f"  rho = {rho}: R = {float(R):.4f}: a holomorphy box fails at z = {w0 if d0 is None else w1}; rejected")
                continue
            C0, C1 = gauge(st0, d0), gauge(st1, d1)
            I0, I1 = (R * dyson_sum(st0, d0, C0)).upper(), (R * dyson_sum(st1, d1, C1)).upper()
            g0, g1 = gauge_norms(M0, C0), gauge_norms(M1, C1)
            if float(I0 + I1) > 300:
                continue
            nM0, nM1 = g0[0] * I0.exp(), g1[0] * I1.exp()
            MF = (2 + nM1 * nM1 * nM0 * nM0).upper()
            MT0 = (arb(2).sqrt() * g0[1] * I0.exp()).upper()
            MT1 = (arb(2).sqrt() * g1[1] * I1.exp()).upper()
            n = max(2, math.ceil(math.log(4 * float(MF) / ((rho - 1) * TOL_F)) / math.log(rho)))
            n += n % 2
            den = rb ** n * (rb - 1)
            eF, e0, e1 = (4 * MF / den).upper(), (4 * MT0 / den).upper(), (4 * MT1 / den).upper()
            exp_boxes = [len(st0) * KSUB * KSUB, len(st1) * KSUB * KSUB]
            assert [w0, w1] == exp_boxes
            gp = (f"C0 = {fmtC(C0)}, C1 = {fmtC(C1)}; ||C||_F ||C^-1||_F <= {hi_sci(g0[2])} (circle), {hi_sci(g1[2])} (lasso); "
                  f"||M_c C||_F ||C^-1||_F <= {hi_sci(g0[0])}, {hi_sci(g1[0])}; ||C^-1 M_c C||_F <= {hi_sci(g0[1])}, {hi_sci(g1[1])}")
            rows.append(dict(rho=rho, n=n, R=ser(R), I0=ser(I0), I1=ser(I1), MF=ser(MF), MT0=ser(MT0), MT1=ser(MT1),
                             errF=ser(eF), errT0=ser(e0), errT1=ser(e1), precondition=pre, boxes=[w0, w1],
                             expected_boxes=exp_boxes, gauge_print=gp,
                             gauge=dict(C0=[[str(x) for x in r] for r in C0], C1=[[str(x) for x in r] for r in C1],
                                        norms0=[ser(x) for x in g0], norms1=[ser(x) for x in g1])))
            say(f"  rho = {rho}: R <= {hi_sci(R)}; precondition ok (max |w_root| {pre['max_root_abs_w']:.4f} < {pre['lim']:.4f}); "
                f"all {w0} + {w1} (step box, k-sub-box) pairs enclosed; I0 <= {hi_sci(I0)}, I1 <= {hi_sci(I1)}; gauge factors "
                f"<= {hi_sci(g0[0])}, {hi_sci(g1[0])}; M_F <= {hi_sci(MF)}, M_trM0 <= {hi_sci(MT0)}, M_trM1 <= {hi_sci(MT1)}; n = {n} "
                f"(bounds F {hi_sci(eF)}, tr M0 {hi_sci(e0)}, tr M1 {hi_sci(e1)})")
        best = min(rows, key=lambda r: (r["n"], float(arb(r["errF"]).mid()))) if rows else None
        segs.append(dict(i=i, kc=kcs, selftest=st_ok, rows=rows, chosen=best, Fc=[str(Fc.real), str(Fc.imag)],
                         steps=[len(st0), len(st1)], c_point=[[ser(x) for x in p] for p in pt]))
        if best:
            say(f"  CHOSEN for sub-segment {i}: rho = {best['rho']}, n = {best['n']} ({best['n'] + 1} Chebyshev points)   "
                f"[{time.time() - ts:.0f} s]")
            say(f"  gauge of the chosen row: {best['gauge_print']}")
        else:
            say(f"  sub-segment {i}: NO admissible (rho, n): no proved M")
    out = dict(seg=SEG, nseg=nseg, segs=segs, version=2,
               env=dict(python=sys.version.split()[0], flint=flint.__version__, interpreter=sys.executable))
    json.dump(out, open(os.path.join(OUTD, f"route1_seg_M_v2_nseg{nseg}.json"), "w"), indent=1)
    say(f"  prove: {time.time() - t0:.0f} s, peak rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")


# --------------------------------------------------------------------------------- stage: nodes
def load_nodes(which):
    done = {}
    if os.path.exists(NODEFILE[which]):
        for line in open(NODEFILE[which]):
            r = json.loads(line)
            done[r["key"]] = r
    return done


def get(done, which, key, kre, kim, ref):
    if key not in done:
        if which != "arb":
            raise RuntimeError(f"missing Part B node value {key}")
        r = dict(key=key, **evaluate(kre, kim, ref))
        with open(NODEFILE[which], "a") as fh:
            fh.write(json.dumps(r) + "\n")
        done[key] = r
        say(f"  {key}: {r['sec']} s, steps {r['steps']}, radius of F {r['rad_F']:.1e}")
    r = done[key]
    return tuple(acb(arb(r[nm][0]), arb(r[nm][1])) for nm in ("F", "T0", "T1"))


def frac(s):
    num, _, den = s.partition("/")
    return arb(num) / arb(den or 1)


def held_plan(nseg):
    return [(0, "-5/8"), (0, "1/8"), (0, "3/4")] if nseg == 1 else [(0, "1/8"), (nseg // 2, "-5/8"), (nseg - 1, "3/4")]


def ell_pt(j, rho):
    th = 2 * math.pi * (j + 0.5) / 8
    return complex((rho * complex(math.cos(th), math.sin(th)) + complex(math.cos(th), -math.sin(th)) / rho) / 2)


def keys(nseg, i, ch):
    base = f"{SEG}|seg{i}/{nseg}"
    return (lambda j: f"{base}|n={ch['n']}|node{j}", lambda s: f"{base}|held t={s}",
            lambda j: f"{base}|ellipse{j}/8 rho={ch['rho']}")


def nodes(nseg, which="arb"):
    J = json.load(open(os.path.join(OUTD, f"route1_seg_M_v2_nseg{nseg}.json")))
    ref = dict(json.load(open(os.path.join(OUTD, "route1_floats.json")))["21/20"])
    done = load_nodes(which)
    t0 = time.time()
    cen = seg_centres(nseg)
    say(f"== nodes ({which} evaluator) == NSEG = {nseg}; {len(done)} records already on disk")
    for sg in J["segs"]:
        ch, (kc, half) = sg["chosen"], cen[sg["i"]]
        kn, kh, ke = keys(nseg, sg["i"], ch)
        for j in range(ch["n"] + 1):
            get(done, which, kn(j), kc + half * (arb.pi() * j / ch["n"]).cos(), arb(0), ref)
    for i, s in held_plan(nseg):
        kc, half = cen[i]
        get(done, which, keys(nseg, i, J["segs"][i]["chosen"])[1](s), kc + half * frac(s), arb(0), ref)
    ch, (kc, half) = J["segs"][0]["chosen"], cen[0]
    for j in range(8):
        tt = ell_pt(j, ch["rho"])
        get(done, which, keys(nseg, 0, ch)[2](j), kc + half * arb(tt.real), half * arb(tt.imag), ref)
    say(f"  nodes: wall {time.time() - t0:.0f} s this call; peak rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")


# --------------------------------------------------------------------------------- stage: verdict
def interp(f, n):
    """-> (p_at, p_th): the Chebyshev interpolant through f at cos(j pi / n).
    p_at(t): by the three-term recurrence; for a POINT t only (on a wide ball the recurrence inflates like 2.4^m).
    p_th(theta): sum'' c_m cos(m theta), for a BALL of theta; the width grows only like m * radius."""
    coef = []
    for m in range(n + 1):
        s_ = acb(0)
        for j in range(n + 1):
            term = f[j] * (arb.pi() * m * j / n).cos()
            s_ += term / 2 if j in (0, n) else term
        coef.append(s_ * 2 / n)

    def p_at(t):
        Tp, Tm = arb(1), t
        tot = coef[0] / 2
        for m in range(1, n + 1):
            tot += coef[m] * Tm / 2 if m == n else coef[m] * Tm
            Tp, Tm = Tm, 2 * t * Tm - Tp
        return tot

    def p_th(th):
        tot = coef[0] / 2
        for m in range(1, n + 1):
            c = (th * m).cos()
            tot += coef[m] * c / 2 if m == n else coef[m] * c
        return tot
    return p_at, p_th


def conditions(qF, q0, q1, eF, e0, e1):
    """-> (ok_F, ok_T0, ok_T1, (min |p_F|, min |p_T0|, min |Im p_T1|)) over ALL the balls of theta; point arbs.
    Comparisons are between balls: True only when certain. A non-finite enclosure is an assertion error."""
    okF = ok0 = ok1 = True
    mF = m0 = m1 = None
    cnt = 0
    for tb in SUBS:
        vF, v0, v1 = qF(tb), q0(tb), q1(tb)
        assert vF.is_finite() and v0.is_finite() and v1.is_finite()
        a, b = vF.abs_lower(), v0.abs_lower()
        im, re = v1.imag.abs_lower(), v1.real.abs_lower()
        okF &= bool(a > eF)
        ok0 &= bool(b > e0)
        ok1 &= bool(im > e1) or bool(re > 2 + e1)
        mF = a if mF is None or a < mF else mF
        m0 = b if m0 is None or b < m0 else m0
        m1 = im if m1 is None or im < m1 else m1
        cnt += 1
    assert cnt == NSUB
    return okF, ok0, ok1, (mF, m0, m1)


def verdict(nseg, which="arb"):
    coverage_asserts()
    J = json.load(open(os.path.join(OUTD, f"route1_seg_M_v2_nseg{nseg}.json")))
    refs = json.load(open(os.path.join(OUTD, "route1_floats.json")))
    ref = dict(refs["21/20"])
    done = load_nodes(which)
    cen = seg_centres(nseg)
    say(f"== verdict (v2; node values: {which} evaluator, {os.path.basename(NODEFILE[which])}) == {SEG}; NSEG = {nseg}")
    res = dict(nseg=nseg, nodes=which, segs=[])
    cert_all, planted_all, shrunk_verdict = True, True, True
    interps = {}
    sh = arb(10) ** 12
    for sg in J["segs"]:
        i, ch, (kc, half) = sg["i"], sg["chosen"], cen[sg["i"]]
        n, rho = ch["n"], ch["rho"]
        assert ch["boxes"] == ch["expected_boxes"]
        R = par_up(ch["R"])
        Ms = tuple(par_up(ch[nm]) for nm in ("MF", "MT0", "MT1"))
        eF, e0, e1 = (par_up(ch[nm]) for nm in ("errF", "errT0", "errT1"))
        kn, kh, ke = keys(nseg, i, ch)
        dist = (R - half).lower()                       # every point of the sub-segment is this far inside the k-disc
        assert dist > 0
        vals = []
        for j in range(n + 1):
            kj = kc + half * (arb.pi() * j / n).cos()
            v = get(done, which, kn(j), kj, arb(0), ref)
            # the evaluation was at the midpoint of the ball kj; Cauchy: |f'| <= M / dist on the sub-segment
            dk = kj.rad() * 2
            vals.append(tuple(v[m] + (Ms[m] / dist * dk).upper() * UNIT for m in range(3)))
        (pF, qF), (p0, q0), (p1, q1) = (interp([v[m] for v in vals], n) for m in range(3))
        okF, ok0, ok1, mg = conditions(qF, q0, q1, eF, e0, e1)
        cert = bool(okF and ok0 and ok1 and sg["selftest"] and ch["precondition"]["ok"])
        cert_all &= cert
        lows = (mg[0] - eF, mg[1] - e0, mg[2] - e1)
        say(f"  sub-segment {i} (k_c = {sg['kc']}; rho = {rho}, n = {n}; proved M_F <= {hi_sci(Ms[0])}, M_trM0 <= {hi_sci(Ms[1])}, "
            f"M_trM1 <= {hi_sci(Ms[2])}):")
        say(f"    F:     min |p| >= {lo_dec(mg[0], 9)}; proved error bound <= {hi_sci(eF)}  -> |F| >= {lo_dec(lows[0], 9)}; F != 0: {okF}")
        say(f"    tr M0: min |p| >= {lo_dec(mg[1], 9)}; proved error bound <= {hi_sci(e0)}  -> |tr M0| >= {lo_dec(lows[1], 9)}; tr M0 != 0: {ok0}")
        say(f"    tr M1: min |Im p| >= {lo_dec(mg[2], 9)}; proved error bound <= {hi_sci(e1)}  -> |Im tr M1| >= {lo_dec(lows[2], 9)}; "
            f"tr M1 not in [-2, 2]: {ok1}")
        Fc = vals[n // 2][0]
        _pG, qG = interp([v[0] - Fc for v in vals], n)
        eG = (eF * (Ms[0] + Fc.abs_upper()) / Ms[0]).upper()
        okG, _a, _b, mgG = conditions(qG, q0, q1, eG, e0, e1)
        planted_all &= not okG
        say(f"    control, planted zero (F - F(k_c)): min |p| >= {float(mgG[0]):.3e}, bound {hi_sci(eG)} -> certificate "
            f"{'GIVEN (CONTROL FAILED)' if okG else 'REFUSED (as it must be)'}")
        o2 = conditions(qF, q0, q1, eF / sh, e0 / sh, e1 / sh)
        shrunk_verdict &= bool(o2[0] and o2[1] and o2[2])
        interps[i] = (pF, p0, p1, eF, e0, e1, vals, Ms, n, rho)
        res["segs"].append(dict(i=i, certified=cert, abs_F_ge=lo_dec(lows[0], 9), abs_trM0_ge=lo_dec(lows[1], 9),
                                abs_Im_trM1_ge=lo_dec(lows[2], 9), planted_zero_refused=not okG))
    say(f"  VERDICT: {'CERTIFIED' if cert_all else 'NOT CERTIFIED'}  (F != 0, tr M0 != 0, tr M1 not in [-2, 2] for every real k in [1, 1.1])")
    say("  -- controls --")
    say(f"  planted zero refused on every sub-segment: {planted_all}")
    for kk, rr in (("4.2", "0.01"), ("4.01", "0.001"), ("4.0", "0.001"), ("1.05", "0.2")):
        pre = precondition(arb(kk) + arb(rr) * UNIT)
        say(f"  planted precondition at k = {kk} +- {rr} (complex box): certified {pre['ok']}"
            + (f"; {pre['why']}" if not pre["ok"] else f"; max |w_root| {pre['max_root_abs_w']:.4f} < {pre['lim']:.4f}"))
        if kk == "4.2":
            res["planted_precondition_fires"] = not pre["ok"]
    hold_ok, hold = True, []
    for i, s in held_plan(nseg):
        pF, p0, p1, eF, e0, e1, vals, Ms, n, rho = interps[i]
        kc, half = cen[i]
        t = frac(s)
        v = get(done, which, keys(nseg, i, J["segs"][i]["chosen"])[1](s), kc + half * t, arb(0), ref)
        row = []
        for m, (p, e) in enumerate(((pF, eF), (p0, e0), (p1, e1))):
            d = p(t) - v[m]
            row.append((d.abs_lower(), d.abs_upper(), e))
            hold_ok &= bool(d.abs_lower() <= e)
        hold.append((i, s, row))
        say(f"  held-out, sub-segment {i}, t = {s}: |p - f| in [{float(row[0][0]):.1e}, {float(row[0][1]):.1e}] (F), "
            f"[{float(row[1][0]):.1e}, {float(row[1][1]):.1e}] (tr M0), [{float(row[2][0]):.1e}, {float(row[2][1]):.1e}] (tr M1)")
    res["held_out_consistent"] = hold_ok
    say(f"  held-out points consistent with interpolant +- bound: {hold_ok}")
    pF, p0, p1, eF, e0, e1, vals, Ms, n, rho = interps[0]
    kc, half = cen[0]
    samp = [arb(0), arb(0), arb(0)]
    for j in range(8):
        tt = ell_pt(j, rho)
        v = get(done, which, keys(nseg, 0, J["segs"][0]["chosen"])[2](j), kc + half * arb(tt.real), half * arb(tt.imag), ref)
        samp = [amax((samp[m], v[m].abs_upper())) for m in range(3)]
    res["proved_M_ge_sampled"] = all(bool(samp[m] <= Ms[m]) for m in range(3))
    say(f"  proved M >= sampled on the ellipse rho = {rho} of sub-segment 0 (8 points): sampled max |F| {float(samp[0]):.4f}, "
        f"|tr M0| {float(samp[1]):.4f}, |tr M1| {float(samp[2]):.4f} -> {res['proved_M_ge_sampled']} "
        f"(overestimate x{float(Ms[0] / samp[0]):.1e}, x{float(Ms[1] / samp[1]):.1e}, x{float(Ms[2] / samp[2]):.1e})")
    eng_ok = True
    for lab, i, pick in (("11/10", nseg - 1, 0), ("1", 0, -1)):
        e = refs[lab]
        vals = interps[i][6]
        ins = []
        for m, nm in enumerate(("F", "T0", "T1")):
            fl = acb(arb(e[nm][0]), arb(e[nm][1]))
            ins.append(bool(vals[pick][m].overlaps(fl)))
        eng_ok &= all(ins)
        say(f"  engine F, tr M0, tr M1 at k = {lab} (an end node; the engine used its own lasso of that k): inside the node "
            f"enclosures {ins}; node radius of F {P.rad(vals[pick][0]):.1e}")
    res["engine_inside"] = eng_ok
    broke = [(i, s, ("F", "tr M0", "tr M1")[m]) for i, s, row in hold for m in range(3) if bool(row[m][0] > row[m][2] / sh)]
    res["shrunken_M_breaks_verdict_or_heldout"] = bool(broke) or not shrunk_verdict
    m_break = [nm for m, nm in enumerate(("F", "tr M0", "tr M1")) if bool(Ms[m] / sh < samp[m])]
    res["shrunken_M_below_sampled"] = m_break
    say(f"  shrunken M (all bounds / 1e12): verdict still passes {shrunk_verdict}; held-out inconsistencies: "
        f"{broke if broke else 'none'}; below the SAMPLED maximum for: {m_break if m_break else 'none'}")
    res.update(certified=cert_all, planted_zero_refused=planted_all)
    json.dump(res, open(os.path.join(OUTD, f"route1_seg_verdict_v2_{which}_nseg{nseg}.json"), "w"), indent=1)
    say(f"  peak rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")


if __name__ == "__main__":
    dict(prove=prove, nodes=nodes, verdict=verdict)[sys.argv[1]](int(sys.argv[2]), *sys.argv[3:4])
