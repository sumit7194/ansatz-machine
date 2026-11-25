#!/usr/bin/env python3
"""Route (i), first build step: a VALIDATED monodromy evaluator for the circle picture, with k a complex ball
(data/nve/EPS_EFFECTIVE.md, Part B).  [model: Fable 5.2; UNVERIFIED until the office ansatz-machine checks it]

Arb ball arithmetic through python-flint. Run with Quantum's pinned interpreter, read-only:
    /Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_proto.py <k_mid> <k_rad> [more pairs]
    ... _nve_route1_proto.py segment 21/20 0.05 7 8        (one-segment demonstration of the k-layer; checkpointed)
Spin 3/5, E = 4/5, circle R0 = 1.35, the engine's own lasso polygon at k_mid (from data/nve/eps/route1_floats.json).

What is enclosed: M0 (circle) and M1 (lasso) of v'' + q(z; k) v = 0 for EVERY k in the ball, hence tr M0, tr M1 and
F = tr[M1, M0] - 2.
  - c0, c0' at a point: Laurent series at infinity of c0'' = c_K'' sqrt(1 - k phi), to w^NW, with a Cauchy tail from a
    bound of |c0''| on |w| = 0.9/a.
  - one step: Taylor series of q at the centre by ball power-series arithmetic (order NT); the two solutions by the
    recurrence; the tail beyond NT from the majorant  |v_j| <= K mu^j, mu = 2/rho, valid once Q rho^2 <= 2 NT (NT+1),
    where Q >= sup |q| on the disc of radius rho (ball evaluation; a disc on which G1 or G2 could vanish is refused
    and rho is halved). Step length h = rho/4, so the tail is K 2^-(NT+1) / (1 - 1/2).
NOT validated here: nothing certifies that the polygon is the engine's homotopy class beyond using the same vertices
(for a ball of k the singular points move; that the path stays clear of them IS certified, by the disc evaluations).
One process, 1 core; a few seconds per evaluation; peak well under 300 MB.
"""
import json
import math
import os
import resource
import sys
import time

import flint
from flint import acb, acb_series, arb, ctx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ctx.prec = 256
NT, NW = 70, 190
A = arb(3) / 5
E2 = arb(16) / 25
R0 = arb(27) / 20
AF = 0.6


def horner(cs, x):
    acc = acb(0)
    for c in reversed(cs):
        acc = acc * x + c
    return acc


# ------------------------------------------------------------------------------------------ c0 from infinity
def laurent(k):
    """d_n with c0'' = sum_n d_n w^n, w = 1/z; and a bound M with |d_n| <= M (0.9/a)^-n."""
    ctx.cap = NW + 2
    w = acb_series([0, 1])
    a2w2 = w * w * (A * A)
    cK2 = w * w * w * w * (-4 * A) * (3 - a2w2) / ((1 + a2w2) * (1 + a2w2) * (1 + a2w2))
    phi = (21 - 18 * a2w2 + a2w2 * a2w2) / (10 * (3 - a2w2) * (3 - a2w2))
    d = (cK2 * (1 - k * phi).sqrt()).coeffs()
    d = d + [acb(0)] * (NW + 2 - len(d))
    rw = arb("0.9") / A
    M = 0.0
    NA = 400
    for j in range(NA):
        th = arb((j + 0.5) * 2 * math.pi / NA, 1.001 * math.pi / NA)
        ww = acb(0, th).exp() * rw
        x = ww * ww * (A * A)
        val = ww * ww * ww * ww * (-4 * A) * (3 - x) / ((1 + x) * (1 + x) * (1 + x)) \
            * (1 - k * (21 - 18 * x + x * x) / (10 * (3 - x) * (3 - x))).sqrt()
        if not val.is_finite():
            raise RuntimeError("Laurent tail bound: non-finite |c0''| on |w| = 0.9/a")
        M = max(M, float(val.abs_upper()))
    return d, M * 1.0000001, float(rw.lower())


def c0_at(z, lau):
    """(c0, c0') on the ball z, with the Laurent tail added."""
    d, M, rw = lau
    w = 1 / z
    c0 = horner([d[n] / ((n - 1) * (n - 2)) for n in range(4, NW + 1)], w) * w * w
    c0p = -horner([d[n] / (n - 1) for n in range(4, NW + 1)], w) * w * w * w
    wm = float(w.abs_upper())
    th = wm / rw
    if not th < 0.95:
        raise RuntimeError("point too close to the Laurent circle")
    t0 = M * th ** (NW + 1) / (1 - th) / wm ** 2 * 1.0000001
    t1 = M * th ** (NW + 1) / (1 - th) / wm * 1.0000001
    return c0 + acb(arb(0, t0), arb(0, t0)), c0p + acb(arb(0, t1), arb(0, t1))


def point_data(z, k, lau):
    Dp = z * z + A * A
    f0 = (z * z - 2 * z + A * A) / Dp
    f0p = 2 * (z * z - A * A) / (Dp * Dp)
    c0, c0p = c0_at(z, lau)
    G2 = f0 * f0 + c0 * c0
    dG2 = 2 * (f0 * f0p + c0 * c0p)
    G1 = E2 * G2 - f0
    dG1 = E2 * dG2 - f0p
    return G1, dG1, G2, dG2


def q_ball(z, k, lau):
    G1, dG1, G2, dG2 = point_data(z, k, lau)
    if G1.contains(0) or G2.contains(0):
        return None
    lam = dG1 / G1 - dG2 / G2
    q = lam * lam * 3 / 16
    return q if q.is_finite() else None


# ------------------------------------------------------------------------------------------ one Taylor step
def step(zc, hvec, k, lau, rho):
    """Fundamental matrix from zc to zc + hvec (|hvec| <= rho/4), entries as balls; plus diagnostics."""
    Q = q_ball(acb(arb(zc.real.mid(), rho), arb(zc.imag.mid(), rho)), k, lau)
    if Q is None:
        return None
    Qf = float(Q.abs_upper())
    if not Qf * rho * rho <= 2 * NT * (NT + 1) * 0.9:
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
    mu = 2.0 / rho
    hm = float(hvec.abs_upper())
    assert mu * hm <= 0.5000001
    cols = []
    for v0, v1 in ((acb(1), acb(0)), (acb(0), acb(1))):
        v = [v0, v1]
        for j in range(NT - 1):
            s = acb(0)
            for i in range(j + 1):
                s += qc[i] * v[j - i]
            v.append(-s / ((j + 1) * (j + 2)))
        K = max(float(v[j].abs_upper()) * mu ** (-j) for j in range(NT + 1)) * 1.0000001
        tail = K * (mu * hm) ** (NT + 1) / (1 - mu * hm) * 1.0000001
        dtail = K * mu * (NT + 1) * (mu * hm) ** NT / (1 - mu * hm) ** 2 * 1.0000001
        val = horner(v, hvec) + acb(arb(0, tail), arb(0, tail))
        der = horner([v[j] * j for j in range(1, NT + 1)], hvec) + acb(arb(0, dtail), arb(0, dtail))
        cols.append((val, der))
    return [[cols[0][0], cols[1][0]], [cols[0][1], cols[1][1]]], Qf


def mmul(X, Y):
    return [[X[0][0] * Y[0][0] + X[0][1] * Y[1][0], X[0][0] * Y[0][1] + X[0][1] * Y[1][1]],
            [X[1][0] * Y[0][0] + X[1][1] * Y[1][0], X[1][0] * Y[0][1] + X[1][1] * Y[1][1]]]


def minv(X):
    d = X[0][0] * X[1][1] - X[0][1] * X[1][0]
    return [[X[1][1] / d, -X[0][1] / d], [-X[1][0] / d, X[0][0] / d]]


def walk(vertices, k, lau, sing):
    """Transport along the polyline through `vertices` (complex floats). -> (matrix, steps, max Q)."""
    M = [[acb(1), acb(0)], [acb(0), acb(1)]]
    nst, Qmax = 0, 0.0
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
                r = step(zc, acb(nxt.real, nxt.imag) - zc, k, lau, rho)
                if r is not None:
                    break
                rho /= 2
                if rho < 1e-4:
                    raise RuntimeError(f"no admissible disc at {pos}")
            T, Qf = r
            M = mmul(T, M)
            Qmax = max(Qmax, Qf)
            pos, done, nst = nxt, done + h, nst + 1
    return M, nst, Qmax


def circle_vertices(n=96):
    r0 = float(R0.mid())
    return [complex(r0 * math.cos(2 * math.pi * j / n), r0 * math.sin(2 * math.pi * j / n)) for j in range(n)] + [complex(r0, 0)]


def rad(x):
    return max(float(x.real.rad()), float(x.imag.rad()))


def evaluate(kmid, krad, ref, kim=0):
    """kmid, kim: centre of the k-ball (arb or float); krad: its radius (0 = a point)."""
    t0 = time.time()
    k = acb(arb(kmid, krad), arb(kim, krad))
    lau = laurent(k)
    sing = [complex(float(p[0]), float(p[1])) for p in ref["points"]]
    lasso = [complex(float(p[0]), float(p[1])) for p in ref["lasso"]]
    M0, n0, Q0 = walk(circle_vertices(), k, lau, sing)
    M1, n1, Q1 = walk(lasso, k, lau, sing)
    Cm = mmul(mmul(M1, M0), mmul(minv(M1), minv(M0)))
    F = Cm[0][0] + Cm[1][1] - 2
    T0, T1 = M0[0][0] + M0[1][1], M1[0][0] + M1[1][1]
    det0 = M0[0][0] * M0[1][1] - M0[0][1] * M0[1][0]
    out = dict(k=[str(kmid), str(kim), krad], F=[str(F.real), str(F.imag)], T0=[str(T0.real), str(T0.imag)],
               T1=[str(T1.real), str(T1.imag)], rad_F=rad(F), rad_T0=rad(T0), rad_T1=rad(T1), steps=[n0, n1],
               Qmax=[Q0, Q1], det_M0_minus_1=float((det0 - 1).abs_upper()), sec=round(time.time() - t0, 2),
               excludes_zero=dict(F=not F.contains(0), T0=not T0.contains(0), T1=not T1.contains(0)))
    if ref.get("F") and kim == 0 and krad == 0 and ref.get("own"):
        for nm, val in (("F", F), ("T0", T0), ("T1", T1)):
            fl = acb(arb(ref[nm][0]), arb(ref[nm][1]))
            out["float_inside_" + nm] = bool(val.overlaps(fl))
            out["float_dist_" + nm] = float((val - fl).abs_lower())
    return out, (F, T0, T1)


def segment(refs, label, half, n, rho_e):
    """One-segment demonstration of the k-layer: Chebyshev interpolation (n + 1 extreme points) of F, tr M0, tr M1 on
    [c - half, c + half] from POINT evaluations, all on the fixed loops of k = c. The interpolation error bound is
    4 M rho^-n / (rho - 1) for a function bounded by M on the Bernstein ellipse of parameter rho (Trefethen, ATAP,
    Thm 8.2; quoted from memory). Here M is only SAMPLED at 8 points of the ellipse, so the resulting enclosure is a
    measurement of what the method would give, not a certificate."""
    outp = os.path.join(ROOT, "data", "nve", "eps", "route1_segment.jsonl")
    done = {}
    if os.path.exists(outp):
        for line in open(outp):
            r = json.loads(line)
            done[r["key"]] = r
    ref = dict(refs[label])
    num, _, den = label.partition("/")
    c = arb(num) / arb(den or 1)
    h = arb(half)
    t_all = time.time()
    vals = {}

    def get(key, kre, kim):
        if key in done:
            r = done[key]
        else:
            o, _v = evaluate(kre, 0, ref, kim=kim)
            r = dict(key=key, **o)
            with open(outp, "a") as fh:
                fh.write(json.dumps(r) + "\n")
            print(f"  {key}: {o['sec']} s, steps {o['steps']}, radius of F {o['rad_F']:.1e}", flush=True)
        return tuple(acb(arb(r[nm][0]), arb(r[nm][1])) for nm in ("F", "T0", "T1")), r["sec"]
    nodes = []
    for j in range(n + 1):
        tj = (arb.pi() * j / n).cos()
        v, sec = get(f"node{j}/{n}", c + h * tj, 0)
        nodes.append(v)
    ell = []
    for j in range(8):
        th = 2 * math.pi * (j + 0.5) / 8
        tt = complex((rho_e * complex(math.cos(th), math.sin(th)) + complex(math.cos(th), -math.sin(th)) / rho_e) / 2)
        v, sec = get(f"ellipse{j}/8 rho={rho_e}", c + h * arb(tt.real), h * arb(tt.imag))
        ell.append(v)
    names = ("F", "tr M0", "tr M1")
    print(f"segment k in [{label} - {half}, {label} + {half}], {n + 1} Chebyshev points, Bernstein rho = {rho_e} "
          f"(ellipse reaches {float(half) * (rho_e + 1 / rho_e) / 2:.3f} from the centre along the real axis, "
          f"{float(half) * (rho_e - 1 / rho_e) / 2:.3f} off it)")
    for idx, nm in enumerate(names):
        f = [v[idx] for v in nodes]
        coef = []
        for m in range(n + 1):
            s_ = acb(0)
            for j in range(n + 1):
                term = f[j] * (arb.pi() * m * j / n).cos()
                s_ += term / 2 if j in (0, n) else term
            coef.append(s_ * 2 / n)
        Msamp = max(float(v[idx].abs_upper()) for v in ell)
        err = 4 * Msamp * rho_e ** (-n) / (rho_e - 1)

        def p_at(t):
            """Interpolant at t (a ball or a number in [-1, 1]); Chebyshev recurrence, no acos (acos of a ball that
            touches -1 or 1 is not finite, which silently dropped the two end sub-balls in the first version)."""
            t = arb(t) if isinstance(t, (int, float)) else t
            Tm_prev, Tm = arb(1), t
            tot = coef[0] / 2
            for m in range(1, n + 1):
                tot += coef[m] * Tm / 2 if m == n else coef[m] * Tm
                Tm_prev, Tm = Tm, 2 * t * Tm - Tm_prev
            return tot
        # enclosure over the segment: 64 sub-balls of t in [-1, 1]
        lo = None
        minabs = 1e300
        for i in range(64):
            tb = arb(-1 + (2 * i + 1) / 64, 1 / 64)
            pv = p_at(tb)
            assert pv.is_finite()
            lo = pv if lo is None else lo.union(pv)
            minabs = min(minabs, float(pv.abs_lower()))
        mid = p_at(arb(0))
        own = refs[label]
        fl = acb(arb(own[("F", "T0", "T1")[idx]][0]), arb(own[("F", "T0", "T1")[idx]][1]))
        print(f"  {nm}: sampled max on the ellipse {Msamp:.4f}; interpolation error bound {err:.2e}; "
              f"min |interpolant| over the segment >= {minabs:.5f}; so {nm} != 0 on the segment (given M): {minabs > err}")
        print(f"      test at the centre k = {label} (not a node): |interpolant - engine float| = "
              f"{float((mid - fl).abs_upper()):.2e}  (bound {err:.2e})")
    secs = sum(r["sec"] for r in (json.loads(l) for l in open(outp)))
    print(f"  total evaluation time for this segment: {secs:.0f} s for {n + 1 + 8} point evaluations "
          f"({n + 1} nodes + 8 ellipse samples); wall this call {time.time() - t_all:.0f} s")


def main():
    refs = json.load(open(os.path.join(ROOT, "data", "nve", "eps", "route1_floats.json")))
    outp = os.path.join(ROOT, "data", "nve", "eps", "route1_proto.jsonl")
    print(f"python {sys.version.split()[0]}, python-flint {flint.__version__}, interpreter {sys.executable}; "
          f"prec {ctx.prec} bits, Taylor order {NT}, Laurent order {NW}; spin 3/5, E = 4/5, R0 = 1.35", flush=True)
    args = sys.argv[1:]
    if args and args[0] == "segment":
        segment(refs, args[1], args[2], int(args[3]), float(args[4]))
        args = []
    for kms, krs in zip(args[0::2], args[1::2]):
        num, _, den = kms.partition("/")
        kmid = arb(num) / arb(den or 1)
        ref = dict(refs[kms], own=True)
        o, _v = evaluate(kmid, float(krs), ref)
        o["k_label"] = kms
        o["env"] = dict(python=sys.version.split()[0], flint=flint.__version__, interpreter=sys.executable)
        with open(outp, "a") as fh:
            fh.write(json.dumps(o) + "\n")
        print(f"k = {kms} +- {krs}: steps {o['steps']}, {o['sec']} s, max Q {o['Qmax'][0]:.3g}/{o['Qmax'][1]:.3g}; "
              f"radius of F {o['rad_F']:.2e}, tr M0 {o['rad_T0']:.2e}, tr M1 {o['rad_T1']:.2e}; "
              f"|det M0 - 1| <= {o['det_M0_minus_1']:.1e}; excludes 0: {o['excludes_zero']}", flush=True)
        print(f"     F in {o['F'][0][:40]} + i {o['F'][1][:40]}", flush=True)
        if "float_dist_F" in o:
            print(f"     engine float inside the enclosure: F {o['float_inside_F']}, tr M0 {o['float_inside_T0']}, "
                  f"tr M1 {o['float_inside_T1']}", flush=True)
    print(f"peak {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")


if __name__ == "__main__":
    main()
