#!/usr/bin/env python3
"""Route (i), the first CERTIFIED segment: spin 3/5, E = 4/5, real k in [1, 1.1]   (data/nve/ROUTE1_SEGMENT.md).
[model: Fable 5.2; UNVERIFIED until the office ansatz-machine checks it]

Claim certified when the run prints VERDICT: CERTIFIED: for every real k in [1, 1.1],
    F(k) != 0,  tr M0(k) != 0,  tr M1(k) not in [-2, 2],
with M0 the circle |z| = 1.35 and M1 the engine's lasso polygon of k_c = 21/20 (data/nve/eps/route1_floats.json).

Run with Quantum's pinned interpreter, read-only:
    /Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_segment.py prove <NSEG>
    ... _nve_route1_segment.py nodes <NSEG>   (point evaluations; one jsonl line each; a rerun resumes)
    ... _nve_route1_segment.py verdict <NSEG> (enclosure, verdict, controls)
The certified run used NSEG = 1.
Outputs: data/nve/eps/route1_seg_*.   One process, 1 core, peak well under 300 MB.

The chain (each link is ball arithmetic unless marked):
 1. Laurent-disc precondition: for every k in the k-box, the zeros of 1 - k phi (closed form), the pole of phi and
    the poles of c_K'' lie strictly outside the disc |omega| <= 0.9/a (omega = 1/z), so c0'' is holomorphic there.
 2. Reference: the validated solution at k_c along both loops; on every step the first row (v1, v2) of the
    fundamental matrix is enclosed on the WHOLE step segment (Taylor polynomial on a ball + its tail).
 3. Perturbation: on a ball Z covering each step segment and the k-box K (a square containing the disc |k - k_c| <= R),
    an enclosure of dq/dk by the chain rule on balls, in the combined form (2b) of _nve_route1_kc_identity.py.
    d c0/dk, d c0'/dk at k_c: the k-derivative of the Laurent series, with its own Cauchy tail. Over K, cut into
    KSUB x KSUB sub-boxes dk: Taylor in k with the second k-derivative (a radial integral from infinity, enclosed on
    the whole of K by a rectangle rule on balls) as the remainder.
    G1 != 0, G2 != 0 and Re(1 - k phi) > 0 are certified on every box (holomorphy in k, and no singular point reaches
    the loops).  |q(k) - q(k_c)| <= R sup |dq/dk| (K is convex).
 4. Dyson, in a constant gauge C: Y_k = Phi_c C T C^-1, T' = -dq (Phi_c C)^-1 E21 (Phi_c C) T, and with det Phi_c = 1
    (Abel) ||(Phi_c C)^-1 E21 (Phi_c C)||_2 = |(v1, v2) C|^2 / |det C|.  So ||T||_2 <= exp(I),
    I = R * sum sup|dq/dk| sup |(v1, v2) C|^2 |h| / |det C|.  ANY C gives a valid bound; C is chosen (in floats) to
    minimise the sum.
 5. M:  ||M(k)||_F <= ||M(k_c) C||_F ||C^-1||_F e^I;  |tr M(k)| <= sqrt2 ||C^-1 M(k_c) C||_F e^I;
        |F(k)| <= 2 + ||M1(k)||_F^2 ||M0(k)||_F^2   (2x2, det 1: ||X^-1||_F = ||X||_F).
 The segment [1, 1.1] is cut into NSEG equal sub-segments, each with its own reference k_c (its midpoint), k-disc,
 Bernstein ellipse and nodes; the loops are the same for all of them.
 6. ATAP Thm 8.2 (read at source by the office): |f - p_n| <= 4 M rho^-n / (rho - 1) on the segment.
 7. The interpolant's enclosure on sub-balls of the segment (in theta, t = cos theta), +- the bound.
"""
import json
import math
import os
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flint                                     # noqa: E402
from flint import acb, arb, ctx                  # noqa: E402
import _nve_route1_proto as P                    # noqa: E402

A, E2, NT = P.A, P.E2, P.NT
OUTD = os.path.join(P.ROOT, "data", "nve", "eps")
LOG = os.path.join(OUTD, "route1_seg_3_5.out")
NODES = os.path.join(OUTD, "route1_seg_nodes.jsonl")
SEG = "spin 3/5|k in [1, 1.1]"
TOL_F = 1e-3
SM = 24                                          # sub-intervals of the radial integrals
UP = 1.0000001


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG, "a") as fh:
        fh.write(s + "\n")


def up(x):
    """float upper bound of |x| (arb or acb)."""
    return float(x.abs_upper()) * UP


# --------------------------------------------------------------------------------- 1. Laurent-disc precondition
def precondition(K):
    """K: acb box of k. True iff CERTIFIED that c0'' = c_K'' sqrt(1 - k phi) is holomorphic on |omega| <= 0.9/a for
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
    mx = max(float(r.abs_upper()) for r in roots)
    fixed = max(float((arb(1) / 3).abs_upper()), 1.0)
    out.update(max_root_abs_w=mx, fixed_poles_abs_w=fixed,
               ok=bool(mx * UP < float(lim.lower()) and fixed * UP < float(lim.lower())))
    if not out["ok"]:
        out["why"] = f"a zero of 1 - k phi has |w| up to {mx:.4f} >= {float(lim.lower()):.4f}: inside the Laurent disc"
    return out


# --------------------------------------------------------------------------------- 2. reference walk at k_c
def step_ref(zc, hvec, k, lau, rho):
    """P.step, plus enclosures Y1, Y2 of the two local solutions (value row) on the whole segment {zc + t hvec}."""
    Q = P.q_ball(acb(arb(zc.real.mid(), rho), arb(zc.imag.mid(), rho)), k, lau)
    if Q is None:
        return None
    Qf = float(Q.abs_upper())
    if not Qf * rho * rho <= 2 * NT * (NT + 1) * 0.9:
        return None
    ctx.cap = NT + 3
    t = flint.acb_series([zc, 1])
    z2 = t * t
    u2 = z2 / (A * A)
    cK2 = (3 * u2 - 1) * (-4) / ((u2 + 1) * (u2 + 1) * (u2 + 1) * (A * A * A))
    phi = (21 * u2 * u2 - 18 * u2 + 1) / (10 * (3 * u2 - 1) * (3 * u2 - 1))
    c0pp = cK2 * (1 - k * phi).sqrt()
    c0v, c0pv = P.c0_at(zc, lau)
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
    mu = 2.0 / rho
    hm = float(hvec.abs_upper())
    assert mu * hm <= 0.5000001
    hr = hm / 2 * UP
    hb = acb(arb(hvec.real.mid() / 2, hr), arb(hvec.imag.mid() / 2, hr))      # ball containing {t hvec, 0 <= t <= 1}
    cols, Y = [], []
    for v0, v1 in ((acb(1), acb(0)), (acb(0), acb(1))):
        v = [v0, v1]
        for j in range(NT - 1):
            s = acb(0)
            for i in range(j + 1):
                s += qc[i] * v[j - i]
            v.append(-s / ((j + 1) * (j + 2)))
        Kc = max(float(v[j].abs_upper()) * mu ** (-j) for j in range(NT + 1)) * UP
        tail = Kc * (mu * hm) ** (NT + 1) / (1 - mu * hm) * UP
        dtail = Kc * mu * (NT + 1) * (mu * hm) ** NT / (1 - mu * hm) ** 2 * UP
        tb = acb(arb(0, tail), arb(0, tail))
        val = P.horner(v, hvec) + tb
        der = P.horner([v[j] * j for j in range(1, NT + 1)], hvec) + acb(arb(0, dtail), arb(0, dtail))
        cols.append((val, der))
        Y.append(P.horner(v, hb) + tb)           # the tail bound is monotone in |h'|, so it covers the segment
    return [[cols[0][0], cols[1][0]], [cols[0][1], cols[1][1]]], Qf, Y


def walk_ref(vertices, k, lau, sing):
    """P.walk at a point k, recording per step: segment midpoint, length, and enclosures (a1, a2) of the first row
    (v1, v2) of the fundamental matrix on the whole step segment."""
    M = [[acb(1), acb(0)], [acb(0), acb(1)]]
    steps = []
    for P0, P1 in zip(vertices[:-1], vertices[1:]):
        pos, seglen = P0, abs(P1 - P0)
        done = 0.0
        while done < seglen - 1e-15:
            dist = min([abs(pos - s) for s in sing] + [abs(pos) - 1.0])
            rho = 0.5 * dist
            while True:
                h = min(rho / 4, seglen - done)
                nxt = P0 + (P1 - P0) * ((done + h) / seglen)
                zc = acb(pos.real, pos.imag)
                r = step_ref(zc, acb(nxt.real, nxt.imag) - zc, k, lau, rho)
                if r is not None:
                    break
                rho /= 2
                if rho < 1e-4:
                    raise RuntimeError(f"no admissible disc at {pos}")
            T, Qf, Y = r
            a1 = Y[0] * M[0][0] + Y[1] * M[1][0]
            a2 = Y[0] * M[0][1] + Y[1] * M[1][1]
            steps.append(((pos + nxt) / 2, abs(nxt - pos) * UP, a1, a2))
            M = P.mmul(T, M)
            pos, done = nxt, done + h
    return M, steps


# --------------------------------------------------------------------------------- 3. dq/dk on Z x K
SB = [arb((j + 0.5) / SM, 0.5 / SM * UP) for j in range(SM)]


def laurent_dk(k):
    """As P.laurent, for d c0''/dk = -c_K'' phi / (2 sqrt(1 - k phi)): coefficients and a Cauchy bound on |omega| = 0.9/a.
    Its holomorphy in the disc is the same precondition (the zeros of 1 - k phi become poles)."""
    ctx.cap = P.NW + 2
    w = flint.acb_series([0, 1])
    a2w2 = w * w * (A * A)
    cK2 = w * w * w * w * (-4 * A) * (3 - a2w2) / ((1 + a2w2) * (1 + a2w2) * (1 + a2w2))
    phi = (21 - 18 * a2w2 + a2w2 * a2w2) / (10 * (3 - a2w2) * (3 - a2w2))
    d = (cK2 * phi * (-1) / ((1 - k * phi).sqrt() * 2)).coeffs()
    d = d + [acb(0)] * (P.NW + 2 - len(d))
    rw = arb("0.9") / A
    M = 0.0
    NA = 400
    for j in range(NA):
        th = arb((j + 0.5) * 2 * math.pi / NA, 1.001 * math.pi / NA)
        ww = acb(0, th).exp() * rw
        x = ww * ww * (A * A)
        ph = (21 - 18 * x + x * x) / (10 * (3 - x) * (3 - x))
        val = ww * ww * ww * ww * (-4 * A) * (3 - x) / ((1 + x) * (1 + x) * (1 + x)) * ph / ((1 - k * ph).sqrt() * 2)
        if not val.is_finite():
            raise RuntimeError("Laurent tail bound (k-derivative): non-finite on |w| = 0.9/a")
        M = max(M, float(val.abs_upper()))
    return d, M * UP, float(rw.lower())


def d2kc0(Z, K):
    """Enclosures of d^2 c0/dk^2 and d^2 c0'/dk^2 on Z x K:  z^-2 int_0^1 (s - s^2) g2(s/z) ds,  -z^-3 int_0^1 s^2 g2 ds,
    g2 = omega^-4 d^2 c0''/dk^2 = g phi / (2 (1 - k phi)),  g = 4a (21 - 18x + x^2) / (20 (3 - x)(1 + x)^3 sqrt(1 - k phi)),
    x = a^2 omega^2. Rectangle rule on SM balls of s. None if Re(1 - k phi) > 0 is not certified on a ball."""
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
    """sup |dq/dk| on Z x K (float), or None if holomorphy is not certified there.
    dKs: None for K a point; else boxes dk covering {k - k_c : k in the k-disc}. On each, by Taylor in k with the
    second derivative (E0, E1) enclosed on the whole of K (convex):
        d c0/dk = D0c + dk E0,   c0 = c0c + dk D0c + dk^2 E0 / 2     (same for c0')."""
    c0c, c0pc = P.c0_at(Z, lau_c)
    D0c, D1c = P.c0_at(Z, laud_c)
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
    worst = 0.0
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
        worst = max(worst, up(dq))
    return worst


RHOS = (3.0, 4.0, 5.0, 6.5, 8.0, 10.0)
KSUB = 5                                         # the k-box is cut into KSUB x KSUB sub-boxes


def kbox(kc, R):
    """(K, sub-boxes of K - k_c): K the square of half-side R around k_c; sub-boxes wholly outside the disc are dropped."""
    K = acb(kc + arb(0, R), arb(0, R))
    if R == 0:
        return K, None
    r = R / KSUB
    subs = []
    for i in range(KSUB):
        for j in range(KSUB):
            cx, cy = -R + (2 * i + 1) * r, -R + (2 * j + 1) * r
            if math.hypot(max(abs(cx) - r, 0.0), max(abs(cy) - r, 0.0)) > R * UP:
                continue
            subs.append(acb(arb(cx, r * UP), arb(cy, r * UP)))
    return K, subs


def dq_list(steps, kc, R, lau_c, laud_c):
    """sup |dq/dk| on every step box, or (None, where) if a holomorphy box fails."""
    K, dKs = kbox(kc, R)
    out = []
    for zm, hl, _a1, _a2 in steps:
        Z = acb(arb(zm.real, hl / 2), arb(zm.imag, hl / 2))
        r = dq_sup(Z, K, dKs, lau_c, laud_c)
        if r is None:
            return None, zm
        out.append(r)
    return out, None


def gauge(steps, dqs):
    """A constant matrix C (floats, det ~ 1) minimising sum dq |(a1, a2) C|^2 h in midpoint arithmetic:
    C C^dagger = sqrt(det W) W^-1,  W = sum dq h r^dagger r.  Not part of the proof: any C gives a valid bound."""
    W11 = W22 = 0.0
    W12 = 0j
    for (zm, hl, a1, a2), dq in zip(steps, dqs):
        x1 = complex(a1.real.mid(), a1.imag.mid())
        x2 = complex(a2.real.mid(), a2.imag.mid())
        w = dq * hl
        W11 += w * abs(x1) ** 2
        W22 += w * abs(x2) ** 2
        W12 += w * x1.conjugate() * x2
    l11 = math.sqrt(W11)
    l21 = W12.conjugate() / l11
    l22 = math.sqrt(max(W22 - abs(l21) ** 2, 1e-30))
    s = math.sqrt(l11 * l22)
    return [[s / l11, -s * l21.conjugate() / (l11 * l22)], [0.0, s / l22]], (W11 + W22, 2 * l11 * l22)


def cmat(C):
    return [[acb(complex(C[i][j]).real, complex(C[i][j]).imag) for j in range(2)] for i in range(2)]


def dyson_sum(steps, dqs, C):
    """sum sup|dq/dk| sup |(v1, v2) C|^2 |h| / |det C|   (rigorous; the exponent per unit |k - k_c|)."""
    Cb = cmat(C)
    det = Cb[0][0] * Cb[1][1] - Cb[0][1] * Cb[1][0]
    tot = arb(0)
    for (zm, hl, a1, a2), dq in zip(steps, dqs):
        b1 = a1 * Cb[0][0] + a2 * Cb[1][0]
        b2 = a1 * Cb[0][1] + a2 * Cb[1][1]
        tot += arb(dq) * arb(hl) * (arb(up(b1)) ** 2 + arb(up(b2)) ** 2)
    return float((tot / det.abs_lower()).abs_upper()) * UP


def fro(M):
    return math.sqrt(sum(up(M[i][j]) ** 2 for i in range(2) for j in range(2))) * UP


def gauge_norms(M, C):
    """(||M C||_F ||C^-1||_F,  ||C^-1 M C||_F)."""
    Cb = cmat(C)
    Ci = P.minv(Cb)
    return fro(P.mmul(M, Cb)) * fro(Ci), fro(P.mmul(Ci, P.mmul(M, Cb)))


def selftest(kc, lau_c, laud_c):
    """Can fail: at k = k_c, the enclosures of d c0/dk, d c0'/dk against central differences in k, and
    |FD of q| <= sup |dq/dk| (with the ratio, which measures how tight the enclosure is)."""
    h = arb(1) / 10 ** 6
    lp, lm = P.laurent(acb(kc + h)), P.laurent(acb(kc - h))
    ok = True
    for zz in (complex(0.3, 1.3162), complex(-1.35, 0.0), complex(1.757, -0.003), complex(2.05, -0.03), complex(2.11, 0.55)):
        Z = acb(zz.real, zz.imag)
        D0, D1 = P.c0_at(Z, laud_c)
        cp, cm = P.c0_at(Z, lp), P.c0_at(Z, lm)
        fd0, fd1 = (cp[0] - cm[0]) / (2 * h), (cp[1] - cm[1]) / (2 * h)
        fdq = (P.q_ball(Z, acb(kc + h), lp) - P.q_ball(Z, acb(kc - h), lm)) / (2 * h)
        sup = dq_sup(Z, acb(kc), None, lau_c, laud_c)
        e0 = float((D0 - fd0).abs_upper())
        e1 = float((D1 - fd1).abs_upper())
        rq = float(fdq.abs_lower()) / sup
        # the box variation term: d2kc0 at the point against the FD of the Laurent derivative
        ldp, ldm = laurent_dk(acb(kc + h)), laurent_dk(acb(kc - h))
        dp_, dm_ = P.c0_at(Z, ldp), P.c0_at(Z, ldm)
        e2 = d2kc0(Z, acb(kc))
        f2 = (dp_[0] - dm_[0]) / (2 * h)
        o2 = bool(e2[0].overlaps(f2 + acb(arb(0, 1e-8), arb(0, 1e-8))))
        good = e0 < 1e-8 and e1 < 1e-8 and 0.5 < rq <= 1.0000001 and o2
        ok &= good
        say(f"    z = {zz}: |D0 - FD| <= {e0:.1e}, |D1 - FD| <= {e1:.1e}; |FD dq/dk| / sup = {rq:.6f}; "
            f"second derivative enclosure overlaps its FD: {o2} (rel. radius {float(e2[0].real.rad()) / up(e2[0]):.1e})"
            f"  -> {'ok' if good else 'FAIL'}")
    return ok


# --------------------------------------------------------------------------------- stage: prove
def seg_centres(nseg):
    return [(arb(1) + arb(2 * i + 1) / (20 * nseg), arb(1) / (20 * nseg)) for i in range(nseg)]


def prove(nseg):
    t0 = time.time()
    refs = json.load(open(os.path.join(OUTD, "route1_floats.json")))
    ref = refs["21/20"]
    sing = [complex(float(p[0]), float(p[1])) for p in ref["points"]]
    lasso = [complex(float(p[0]), float(p[1])) for p in ref["lasso"]]
    say(f"== prove == NSEG = {nseg}; python {sys.version.split()[0]}, python-flint {flint.__version__}, interpreter "
        f"{sys.executable}; prec {ctx.prec} bits, Taylor order {NT}, Laurent order {P.NW}; {SEG}; lasso and singular "
        f"points of k = 21/20 from route1_floats.json")
    segs = []
    for i, (kc, half) in enumerate(seg_centres(nseg)):
        ts = time.time()
        kcs = f"{float(kc.mid()):.6f}"
        lau_c, laud_c = P.laurent(acb(kc)), laurent_dk(acb(kc))
        say(f"  -- sub-segment {i}: k_c = {kcs}, half-width {float(half.mid()):.6f} --")
        st_ok = selftest(kc, lau_c, laud_c)
        say(f"  derivative self-test passes: {st_ok}")
        M0, st0 = walk_ref(P.circle_vertices(), acb(kc), lau_c, sing)
        M1, st1 = walk_ref(lasso, acb(kc), lau_c, sing)
        Cm = P.mmul(P.mmul(M1, M0), P.mmul(P.minv(M1), P.minv(M0)))
        Fc = Cm[0][0] + Cm[1][1] - 2
        say(f"  reference: circle {len(st0)} steps, lasso {len(st1)} steps, {time.time() - ts:.0f} s; ||M0||_F <= {fro(M0):.6f}, "
            f"||M1||_F <= {fro(M1):.6f}; F = {complex(Fc.real.mid(), Fc.imag.mid()):.10f}")
        # the constants at the point k_c
        ident = [[1.0, 0.0], [0.0, 1.0]]
        pt = []
        for st in (st0, st1):
            dqs, _w = dq_list(st, kc, 0.0, lau_c, laud_c)
            C, (trW, twoSqrtDet) = gauge(st, dqs)
            pt.append((dyson_sum(st, dqs, ident), dyson_sum(st, dqs, C), sum(d * s[1] for d, s in zip(dqs, st))))
        say(f"  MEASURED Dyson constants at k_c (exponent per unit |k - k_c|, K a point): circle {pt[0][0]:.3f} (base "
            f"gauge) -> {pt[0][1]:.3f} (optimised gauge); lasso {pt[1][0]:.3f} -> {pt[1][1]:.3f};  "
            f"int sup|dq/dk| |dz|: {pt[0][2]:.3f}, {pt[1][2]:.3f}")
        rows = []
        for rho in RHOS:
            R = float(half.upper()) * (rho + 1 / rho) / 2 * UP
            pre = precondition(kbox(kc, R)[0])
            if not pre["ok"]:
                say(f"  rho = {rho}: R = {R:.4f}: Laurent-disc precondition NOT certified ({pre['why']})")
                continue
            d0, w0 = dq_list(st0, kc, R, lau_c, laud_c)
            d1, w1 = dq_list(st1, kc, R, lau_c, laud_c) if d0 is not None else (None, None)
            if d0 is None or d1 is None:
                say(f"  rho = {rho}: R = {R:.4f}: a holomorphy box fails at z = {w0 if d0 is None else w1}; rejected")
                continue
            C0, _x = gauge(st0, d0)
            C1, _x = gauge(st1, d1)
            I0, I1 = R * dyson_sum(st0, d0, C0) * UP, R * dyson_sum(st1, d1, C1) * UP
            g0, g1 = gauge_norms(M0, C0), gauge_norms(M1, C1)
            if I0 + I1 > 300:
                continue
            nM0 = g0[0] * math.exp(I0) * UP
            nM1 = g1[0] * math.exp(I1) * UP
            MF = (2 + nM1 ** 2 * nM0 ** 2) * UP
            MT0 = math.sqrt(2) * g0[1] * math.exp(I0) * UP
            MT1 = math.sqrt(2) * g1[1] * math.exp(I1) * UP
            n = max(2, math.ceil(math.log(4 * MF / ((rho - 1) * TOL_F)) / math.log(rho)))
            n += n % 2
            rows.append(dict(rho=rho, R=R, I0=I0, I1=I1, c0_box=I0 / R, c1_box=I1 / R, MF=MF, MT0=MT0, MT1=MT1, n=n,
                             errF=4 * MF * rho ** (-n) / (rho - 1) * UP, errT0=4 * MT0 * rho ** (-n) / (rho - 1) * UP,
                             errT1=4 * MT1 * rho ** (-n) / (rho - 1) * UP, precondition=pre, gauge_norms=[g0, g1],
                             C0=[[str(x) for x in r] for r in C0], C1=[[str(x) for x in r] for r in C1]))
            say(f"  rho = {rho}: R = {R:.4f}; precondition ok (max |w_root| {pre['max_root_abs_w']:.4f} < {pre['lim']:.4f}); "
                f"I0 = {I0:.3f}, I1 = {I1:.3f} (per unit k on the box: {I0 / R:.2f}, {I1 / R:.2f}); gauge factors "
                f"{g0[0]:.2f}, {g1[0]:.2f}; M_F = {MF:.3e}, M_trM0 = {MT0:.3e}, M_trM1 = {MT1:.3e}; n = {n} "
                f"(bounds F {rows[-1]['errF']:.2e}, tr M0 {rows[-1]['errT0']:.2e}, tr M1 {rows[-1]['errT1']:.2e})")
        best = min(rows, key=lambda r: (r["n"], r["errF"])) if rows else None
        segs.append(dict(i=i, kc=kcs, selftest=st_ok, n0c=fro(M0), n1c=fro(M1), c_point=[list(pt[0]), list(pt[1])],
                         rows=rows, chosen=best, Fc=[str(Fc.real), str(Fc.imag)], steps=[len(st0), len(st1)]))
        if best:
            say(f"  CHOSEN for sub-segment {i}: rho = {best['rho']}, n = {best['n']} ({best['n'] + 1} Chebyshev points), "
                f"proved M_F = {best['MF']:.3e}   [{time.time() - ts:.0f} s]")
        else:
            say(f"  sub-segment {i}: NO admissible (rho, n): no proved M")
    tot = sum(s["chosen"]["n"] + 1 for s in segs if s["chosen"])
    out = dict(seg=SEG, nseg=nseg, segs=segs, total_nodes=tot,
               env=dict(python=sys.version.split()[0], flint=flint.__version__, interpreter=sys.executable))
    json.dump(out, open(os.path.join(OUTD, f"route1_seg_M_nseg{nseg}.json"), "w"), indent=1)
    say(f"  NSEG = {nseg}: total point evaluations needed {tot} (shared end points counted twice); "
        f"prove: {time.time() - t0:.0f} s, peak rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")


# --------------------------------------------------------------------------------- stage: nodes
def load_nodes():
    done = {}
    if os.path.exists(NODES):
        for line in open(NODES):
            r = json.loads(line)
            done[r["key"]] = r
    return done


def get(done, key, kre, kim, ref):
    if key not in done:
        o, _v = P.evaluate(kre, 0, ref, kim=kim)
        r = dict(key=key, **o)
        with open(NODES, "a") as fh:
            fh.write(json.dumps(r) + "\n")
        done[key] = r
        say(f"  {key}: {o['sec']} s, steps {o['steps']}, radius of F {o['rad_F']:.1e}")
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


def nodes(nseg):
    J = json.load(open(os.path.join(OUTD, f"route1_seg_M_nseg{nseg}.json")))
    ref = dict(json.load(open(os.path.join(OUTD, "route1_floats.json")))["21/20"])
    done = load_nodes()
    t0 = time.time()
    cen = seg_centres(nseg)
    say(f"== nodes == NSEG = {nseg}; {len(done)} records already on disk")
    for sg in J["segs"]:
        ch, (kc, half) = sg["chosen"], cen[sg["i"]]
        kn, kh, ke = keys(nseg, sg["i"], ch)
        for j in range(ch["n"] + 1):
            get(done, kn(j), kc + half * (arb.pi() * j / ch["n"]).cos(), 0, ref)
    for i, s in held_plan(nseg):
        kc, half = cen[i]
        get(done, keys(nseg, i, J["segs"][i]["chosen"])[1](s), kc + half * frac(s), 0, ref)
    ch, (kc, half) = J["segs"][0]["chosen"], cen[0]
    for j in range(8):
        tt = ell_pt(j, ch["rho"])
        get(done, keys(nseg, 0, ch)[2](j), kc + half * arb(tt.real), half * arb(tt.imag), ref)
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


NSUB = 256
# balls of theta covering [0, pi]; t = cos(theta) then covers the whole segment [-1, 1]
SUBS = [arb.pi() * (2 * i + 1) / (2 * NSUB) + arb(0, 3.14159266 / (2 * NSUB)) for i in range(NSUB)]


def conditions(pF, p0, p1, eF, e0, e1):
    """-> (ok_F, ok_T0, ok_T1, min margins); pF, p0, p1 take a ball of theta. Every sub-ball must pass; a non-finite
    enclosure is an assertion error."""
    okF = ok0 = ok1 = True
    mF = m0 = m1 = 1e300
    for tb in SUBS:
        vF, v0, v1 = pF(tb), p0(tb), p1(tb)
        assert vF.is_finite() and v0.is_finite() and v1.is_finite()
        a = float(vF.abs_lower()) / UP
        b = float(v0.abs_lower()) / UP
        im = float(v1.imag.abs_lower()) / UP
        re = float(v1.real.abs_lower()) / UP
        okF &= a > eF
        ok0 &= b > e0
        ok1 &= (im > e1) or (re > 2 + e1)
        mF, m0, m1 = min(mF, a), min(m0, b), min(m1, max(im, re - 2))
    return okF, ok0, ok1, (mF, m0, m1)


def verdict(nseg):
    J = json.load(open(os.path.join(OUTD, f"route1_seg_M_nseg{nseg}.json")))
    refs = json.load(open(os.path.join(OUTD, "route1_floats.json")))
    ref = dict(refs["21/20"])
    done = load_nodes()
    cen = seg_centres(nseg)
    say(f"== verdict == {SEG}; NSEG = {nseg}")
    res = dict(nseg=nseg, segs=[])
    cert_all, planted_all, shrunk_verdict = True, True, True
    interps = {}
    for sg in J["segs"]:
        i, ch, (kc, half) = sg["i"], sg["chosen"], cen[sg["i"]]
        n, rho, R = ch["n"], ch["rho"], ch["R"]
        kn, kh, ke = keys(nseg, i, ch)
        dist = R - float(half.upper())                  # every point of the sub-segment is this far inside the k-disc
        Ms = (ch["MF"], ch["MT0"], ch["MT1"])
        vals = []
        for j in range(n + 1):
            kj = kc + half * (arb.pi() * j / n).cos()
            v = get(done, kn(j), kj, 0, ref)
            # the evaluation was at the midpoint of the ball kj; Cauchy: |f'| <= M / dist on the sub-segment
            dk = float(kj.rad()) * 2 + 1e-70
            vals.append(tuple(v[m] + acb(arb(0, Ms[m] / dist * dk), arb(0, Ms[m] / dist * dk)) for m in range(3)))
        (pF, qF), (p0, q0), (p1, q1) = (interp([v[m] for v in vals], n) for m in range(3))
        eF, e0, e1 = ch["errF"], ch["errT0"], ch["errT1"]
        okF, ok0, ok1, mg = conditions(qF, q0, q1, eF, e0, e1)
        cert = bool(okF and ok0 and ok1 and sg["selftest"] and ch["precondition"]["ok"])
        cert_all &= cert
        say(f"  sub-segment {i} (k_c = {sg['kc']}; rho = {rho}, n = {n}; proved M_F = {Ms[0]:.3e}, M_trM0 = {Ms[1]:.3e}, M_trM1 = {Ms[2]:.3e}):")
        say(f"    F:     min |p| >= {mg[0]:.6f}; proved error bound {eF:.3e}  -> F != 0: {okF}")
        say(f"    tr M0: min |p| >= {mg[1]:.6f}; proved error bound {e0:.3e}  -> tr M0 != 0: {ok0}")
        say(f"    tr M1: min over sub-balls of max(|Im p|, |Re p| - 2) >= {mg[2]:.6f}; proved error bound {e1:.3e}  "
            f"-> tr M1 not in [-2, 2]: {ok1}")
        # control: planted zero, F - F(k_c) (k_c is the middle node, n even)
        Fc = vals[n // 2][0]
        _pG, qG = interp([v[0] - Fc for v in vals], n)
        eG = eF * (Ms[0] + up(Fc)) / Ms[0]
        okG, _a, _b, mgG = conditions(qG, q0, q1, eG, e0, e1)
        planted_all &= not okG
        say(f"    control, planted zero (F - F(k_c)): min |p| >= {mgG[0]:.3e}, bound {eG:.3e} -> certificate "
            f"{'GIVEN (CONTROL FAILED)' if okG else 'REFUSED (as it must be)'}")
        sh = 1e-12
        o2 = conditions(qF, q0, q1, eF * sh, e0 * sh, e1 * sh)
        shrunk_verdict &= bool(o2[0] and o2[1] and o2[2])
        interps[i] = (pF, p0, p1, eF, e0, e1, vals, Ms, n, rho)
        res["segs"].append(dict(i=i, certified=cert, min_abs_F_certified=mg[0] - eF, margins=list(mg), errors=[eF, e0, e1],
                                planted_zero_refused=not okG))
    minF = min(s["min_abs_F_certified"] for s in res["segs"])
    say(f"  certified min |F| on [1, 1.1] >= {minF:.6f}")
    say(f"  VERDICT: {'CERTIFIED' if cert_all else 'NOT CERTIFIED'}  (F != 0, tr M0 != 0, tr M1 not in [-2, 2] for every real k in [1, 1.1])")
    say("  -- controls --")
    say(f"  planted zero refused on every sub-segment: {planted_all}")
    for kk, rr in (("4.2", 0.01), ("4.01", 0.001), ("4.0", 0.001), ("1.05", 0.2)):
        pre = precondition(acb(arb(kk) + arb(0, rr), arb(0, rr)))
        say(f"  planted precondition at k = {kk} +- {rr} (complex box): certified {pre['ok']}"
            + (f"; {pre['why']}" if not pre["ok"] else f"; max |w_root| {pre['max_root_abs_w']:.4f} < {pre['lim']:.4f}"))
        if kk == "4.2":
            res["planted_precondition_fires"] = not pre["ok"]
    hold_ok, hold = True, []
    for i, s in held_plan(nseg):
        pF, p0, p1, eF, e0, e1, vals, Ms, n, rho = interps[i]
        kc, half = cen[i]
        t = frac(s)
        v = get(done, keys(nseg, i, J["segs"][i]["chosen"])[1](s), kc + half * t, 0, ref)
        row = []
        for m, (p, e) in enumerate(((pF, eF), (p0, e0), (p1, e1))):
            d = p(t) - v[m]
            row.append((float(d.abs_lower()), float(d.abs_upper()), e))
            hold_ok &= float(d.abs_lower()) <= e
        hold.append((i, s, row))
        say(f"  held-out, sub-segment {i}, t = {s}: |p - f| in [{row[0][0]:.1e}, {row[0][1]:.1e}] (F), [{row[1][0]:.1e}, "
            f"{row[1][1]:.1e}] (tr M0), [{row[2][0]:.1e}, {row[2][1]:.1e}] (tr M1); bounds {eF:.1e}, {e0:.1e}, {e1:.1e}")
    res["held_out_consistent"] = hold_ok
    say(f"  held-out points consistent with interpolant +- bound: {hold_ok}")
    pF, p0, p1, eF, e0, e1, vals, Ms, n, rho = interps[0]
    kc, half = cen[0]
    samp = [0.0, 0.0, 0.0]
    for j in range(8):
        tt = ell_pt(j, rho)
        v = get(done, keys(nseg, 0, J["segs"][0]["chosen"])[2](j), kc + half * arb(tt.real), half * arb(tt.imag), ref)
        samp = [max(samp[m], up(v[m])) for m in range(3)]
    res["proved_M_ge_sampled"] = all(samp[m] <= Ms[m] for m in range(3))
    say(f"  proved M >= sampled on the ellipse rho = {rho} of sub-segment 0 (8 points): sampled max |F| {samp[0]:.4f}, "
        f"|tr M0| {samp[1]:.4f}, |tr M1| {samp[2]:.4f}; proved {Ms[0]:.3e}, {Ms[1]:.3e}, {Ms[2]:.3e} -> "
        f"{res['proved_M_ge_sampled']} (overestimate x{Ms[0] / samp[0]:.1e}, x{Ms[1] / samp[1]:.1e}, x{Ms[2] / samp[2]:.1e})")
    eng_ok = True
    for lab, i, pick in (("11/10", nseg - 1, 0), ("1", 0, -1)):
        e = refs[lab]
        vals = interps[i][6]
        for m, nm in enumerate(("F", "T0", "T1")):
            fl = acb(arb(e[nm][0]), arb(e[nm][1]))
            inside = bool(vals[pick][m].overlaps(fl))
            eng_ok &= inside
            say(f"  engine {nm} at k = {lab} (an end node; the engine used its own lasso of that k): inside the node "
                f"enclosure {inside}; distance >= {float((vals[pick][m] - fl).abs_lower()):.1e}, node radius {P.rad(vals[pick][m]):.1e}")
    res["engine_inside"] = eng_ok
    broke = []
    for i, s, row in hold:
        for m in range(3):
            if row[m][0] > row[m][2] * 1e-12:
                broke.append((i, s, ("F", "tr M0", "tr M1")[m]))
    res["shrunken_M_breaks"] = bool(broke) or not shrunk_verdict
    m_break = [nm for m, nm in enumerate(("F", "tr M0", "tr M1")) if Ms[m] * 1e-12 < samp[m]]
    res["shrunken_M_below_sampled"] = m_break
    say(f"  shrunken M (all bounds / 1e12): verdict still passes {shrunk_verdict}; held-out inconsistencies: "
        f"{broke if broke else 'none'}  -> {'BREAKS' if res['shrunken_M_breaks'] else 'NOTHING BREAKS in the verdict or the held-out test (uninformative there)'}")
    say(f"    the shrunken M is below the SAMPLED maximum for: {m_break if m_break else 'none'}  (so the control 'proved M >= "
        f"sampled' {'refuses it' if m_break else 'does not refuse it'})")
    res.update(certified=cert_all, min_abs_F_certified=minF, planted_zero_refused=planted_all)
    json.dump(res, open(os.path.join(OUTD, f"route1_seg_verdict_nseg{nseg}.json"), "w"), indent=1)
    say(f"  peak rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")


if __name__ == "__main__":
    dict(prove=prove, nodes=nodes, verdict=verdict)[sys.argv[1]](int(sys.argv[2]))
