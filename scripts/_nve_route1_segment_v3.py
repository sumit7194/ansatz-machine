#!/usr/bin/env python3
"""Route (i), proof stage with a CENTRED enclosure of dq/dk (office, 2026-11-26; branch office/2026-11-26-centred-encl).
Builds on Fable's _nve_route1_segment_v2.py (d18de63), imported unchanged; only the per-step bound on |dq/dk| changes.

Why: v2 encloses dq/dk by evaluating the Laurent-series c0 and the rational dq/dk directly on each step box. The
dependency (wrapping) effect inflates that by up to x19 at spin 3/5 and up to x5,900 at spin 9/10
(data/nve/ROUTE1_9_10_OFFICE_DIAG.md), so the certified Dyson constants were 29x and 735x the intrinsic ones.

The centred bound, per step segment S (midpoint z_m, length <= hm) and per k-sub-box Kj:
  - the Taylor series of dq/dk in z at the POINT z_m, to order N, with k the BALL Kj (series arithmetic: c0'' =
    c_K'' sqrt(1 - k phi) and d c0''/dk integrated twice from the point values at z_m, which come from the Laurent series
    at the ball Kj with its Cauchy tail); coefficients c_j (balls, valid for every k in Kj);
  - on S, |z - z_m| <= r := hm, so |dq/dk| <= |c_0| + sum_{j=1..N} |c_j| r^j + Mout q^(N+1)/(1 - q),  q = r/Rout,
    where Mout >= sup |dq/dk| over the box of half-side Rout around z_m and every k in the whole k-square K (Fable's own
    crude enclosure v2.dq_sup, which also CERTIFIES holomorphy there: G1, G2 != 0, Re(1 - k phi) > 0), so Cauchy's
    estimate |c_j| <= Mout Rout^-j applies to the true coefficients.
  - the per-step value is min(centred, v2 crude on the step box): both are valid upper bounds, so v3 is never weaker
    than v2. Rout = 2 r first, then 1.5 r (order 30; a first try with order 10 and 4r/2r was
    stopped: the 4r box does not certify and the 2r remainder dominated at order 10, measured); if neither outer box certifies, only the v2 value is used.
Everything is ball arithmetic; floats are choices only (N, Rout/r).
    NVE_SPIN=3/5 R1_R0=1.35 nice -n 12 <quantum python> -I -u scripts/_nve_route1_segment_v3.py
Outputs: data/nve/eps/route1_seg_M_v3{TAG}_nseg1.json, route1_seg_{spin}_v3.out.  One process, one core.
Declared footprint: < 300 MB (v2 measured 33 MB)."""
import json
import math
import os
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flint                                       # noqa: E402
from flint import acb, acb_series, arb, ctx        # noqa: E402
import _nve_route1_segment_v2 as V                 # noqa: E402  (spin from NVE_SPIN, circle from R1_R0)
import _nve_route1_proto as P                      # noqa: E402

A, E2 = V.A, V.E2
NORD = 30
RHOS3 = (3.0, 4.0, 5.0, 6.5)
LOG3 = V.LOG.replace("_v2.out", "_v3.out")
STATS = dict(centred=0, crude_only=0, rout2=0, rout15=0)


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG3, "a") as fh:
        fh.write(s + "\n")


def dq_series(zm, kball, lau_k, laud_k):
    """Robust wrapper: a series division whose leading term contains 0 (wide balls) means "no centred bound here";
    the caller then keeps the v2 crude bound, which is valid."""
    try:
        return _dq_series(zm, kball, lau_k, laud_k)
    except (ValueError, ZeroDivisionError):
        return None


def _dq_series(zm, kball, lau_k, laud_k):
    """Coefficients c_0..c_NORD (balls) of dq/dk(z_m + t; k) for all k in kball, or None if a denominator contains 0."""
    ctx.cap = NORD + 4
    t = acb_series([zm, 1])
    z2 = t * t
    u2 = z2 / (A * A)
    cK2 = (3 * u2 - 1) * (-4) / ((u2 + 1) * (u2 + 1) * (u2 + 1) * (A * A * A))
    phi = (21 * u2 * u2 - 18 * u2 + 1) / (10 * (3 * u2 - 1) * (3 * u2 - 1))
    sq = (1 - kball * phi).sqrt()
    c0v, c0pv = V.c0_at(zm, lau_k)
    D0v, D1v = V.c0_at(zm, laud_k)
    c0p = (cK2 * sq).integral() + c0pv
    c0 = c0p.integral() + c0v
    D1 = (cK2 * phi * (-1) / (sq * 2)).integral() + D1v
    D0 = D1.integral() + D0v
    f0 = (z2 - 2 * t + A * A) / (z2 + A * A)
    f0p = f0.derivative()
    G2 = f0 * f0 + c0 * c0
    dG2 = 2 * (f0 * f0p + c0 * c0p)
    G1 = E2 * G2 - f0
    dG1 = E2 * dG2 - f0p
    g1c, g2c = G1.coeffs()[0], G2.coeffs()[0]
    if g1c.contains(0) or g2c.contains(0):
        return None
    G12 = G1 * G2
    lam = dG1 / G1 - dG2 / G2
    X = 2 * f0 * c0 * D0 / G12
    dlam = 2 * (f0p * c0 * D0 + f0 * c0p * D0 + f0 * c0 * D1) / G12 - X * (dG1 / G1 + dG2 / G2)
    c = (lam * dlam * 3 / 8).coeffs()
    c = c + [acb(0)] * (NORD + 1 - len(c))
    c = c[:NORD + 1]
    return c if all(x.is_finite() for x in c) else None


def dq_list_centred(steps, kc, R, lau_c, laud_c, laus):
    """Per step: (bound, how) with bound a point arb >= sup |dq/dk| on the step segment for all k in the k-square."""
    K, dKs = V.kbox(kc, R)
    subs = [acb(kc)] if dKs is None else [kc + dk for dk in dKs]
    assert len(laus) == len(subs)
    out, ratios = [], []
    for Z, hm, _a1, _a2 in steps:
        crude = V.dq_sup(Z, K, dKs, lau_c, laud_c)
        if crude is None:
            return None, complex(Z.real.mid(), Z.imag.mid()), None
        crude = crude[0]
        zm = acb(Z.real.mid(), Z.imag.mid())
        r = hm
        best = None
        for fac in (2, 1.5):
            Rout = r * fac
            try:
                mo = V.dq_sup(zm + Rout * V.UNIT, K, dKs, lau_c, laud_c)
            except RuntimeError:
                mo = None
            if mo is None:
                continue
            Mout = mo[0]
            q = 1 / arb(fac)
            rem = (Mout * q ** (NORD + 1) / (1 - q)).upper()
            worst = None
            ok = True
            for kb, (lk, ldk) in zip(subs, laus):
                c = dq_series(zm, kb, lk, ldk)
                if c is None:
                    ok = False
                    break
                pol = c[0].abs_upper()
                rp = arb(1)
                for j in range(1, NORD + 1):
                    rp = rp * r
                    pol = pol + c[j].abs_upper() * rp
                val = (pol + rem).upper()
                worst = val if worst is None or val > worst else worst
            if ok:
                best = worst
                STATS["rout2" if fac == 2 else "rout15"] += 1
                break
        if best is not None and best < crude:
            out.append(best)
            STATS["centred"] += 1
        else:
            out.append(crude)
            STATS["crude_only"] += 1 if best is None else 0
            if best is not None:
                STATS["centred"] += 0
        ratios.append(float(crude) / float(out[-1]))
    return out, None, ratios


def prove():
    t0 = time.time()
    V.coverage_asserts()
    refs = json.load(open(os.path.join(V.OUTD, V.FLOATS)))
    ref = refs["21/20"]
    sing = [complex(float(p[0]), float(p[1])) for p in ref["points"]]
    lasso = [complex(float(p[0]), float(p[1])) for p in ref["lasso"]]
    say(f"== prove (v3: CENTRED dq/dk, order {NORD}) == {V.SEG}; circle {V.R0S}; python {sys.version.split()[0]}, "
        f"python-flint {flint.__version__}; prec {ctx.prec} bits")
    (kc, half), = V.seg_centres(1)
    lau_c, laud_c = V.laurent(acb(kc)), V.laurent(acb(kc), True)
    st_ok = V.selftest(kc, lau_c, laud_c)
    say(f"  derivative self-test (v2's): {st_ok}")
    M0, st0 = V.walk(V.circle_vertices(), acb(kc), lau_c, sing, record=True)
    M1, st1 = V.walk(lasso, acb(kc), lau_c, sing, record=True)
    say(f"  reference: circle {len(st0)} steps, lasso {len(st1)} steps, {time.time() - t0:.0f} s")
    ident = [[1.0, 0.0], [0.0, 1.0]]
    # constants at the point k_c: v2 crude vs v3 centred
    pt = {}
    for nm, st in (("circle", st0), ("lasso", st1)):
        d2, _n = V.dq_list(st, kc, arb(0), lau_c, laud_c)
        d3, _w, rat = dq_list_centred(st, kc, arb(0), lau_c, laud_c, [(lau_c, laud_c)])
        C2, C3 = V.gauge(st, d2), V.gauge(st, d3)
        pt[nm] = (V.dyson_sum(st, d2, C2), V.dyson_sum(st, d3, C3), max(rat), sorted(rat)[len(rat) // 2])
        say(f"  {nm}, K a point: optimised-gauge constant v2 <= {V.hi_sci(pt[nm][0])}, v3 (centred) <= {V.hi_sci(pt[nm][1])}; "
            f"per-step crude/centred ratio: median {pt[nm][3]:.2f}, max {pt[nm][2]:.3g}   [{time.time() - t0:.0f} s]")
    rows = []
    for rho in RHOS3:
        ts = time.time()
        rb = arb(rho)
        R = (half * (rb + 1 / rb) / 2).upper()
        K, dKs = V.kbox(kc, R)
        pre = V.precondition(K)
        if not pre["ok"]:
            say(f"  rho = {rho}: precondition NOT certified; skipped")
            continue
        laus = [(V.laurent(kc + dk), V.laurent(kc + dk, True)) for dk in dKs]
        d0, w0, r0 = dq_list_centred(st0, kc, R, lau_c, laud_c, laus)
        d1, w1, r1 = dq_list_centred(st1, kc, R, lau_c, laud_c, laus) if d0 is not None else (None, None, None)
        if d0 is None or d1 is None:
            say(f"  rho = {rho}: a holomorphy box fails at {w0 if d0 is None else w1}; rejected")
            continue
        C0, C1 = V.gauge(st0, d0), V.gauge(st1, d1)
        I0, I1 = (R * V.dyson_sum(st0, d0, C0)).upper(), (R * V.dyson_sum(st1, d1, C1)).upper()
        g0, g1 = V.gauge_norms(M0, C0), V.gauge_norms(M1, C1)
        nM0, nM1 = g0[0] * I0.exp(), g1[0] * I1.exp()
        MF = (2 + nM1 * nM1 * nM0 * nM0).upper()
        MT0 = (arb(2).sqrt() * g0[1] * I0.exp()).upper()
        MT1 = (arb(2).sqrt() * g1[1] * I1.exp()).upper()
        n = max(2, math.ceil(math.log(4 * float(MF) / ((rho - 1) * V.TOL_F)) / math.log(rho)))
        n += n % 2
        den = rb ** n * (rb - 1)
        eF, e0, e1 = (4 * MF / den).upper(), (4 * MT0 / den).upper(), (4 * MT1 / den).upper()
        rows.append(dict(rho=rho, n=n, R=V.ser(R), I0=V.ser(I0), I1=V.ser(I1), c0_per_k=float(I0 / R), c1_per_k=float(I1 / R),
                         MF=V.ser(MF), MT0=V.ser(MT0), MT1=V.ser(MT1), errF=V.ser(eF), errT0=V.ser(e0), errT1=V.ser(e1),
                         precondition=pre, gauge=dict(C0=[[str(x) for x in r] for r in C0], C1=[[str(x) for x in r] for r in C1],
                                                     norms0=[V.ser(x) for x in g0], norms1=[V.ser(x) for x in g1]),
                         ratio_median=[sorted(r0)[len(r0) // 2], sorted(r1)[len(r1) // 2]], ratio_max=[max(r0), max(r1)]))
        say(f"  rho = {rho}: R <= {V.hi_sci(R)}; I0 <= {V.hi_sci(I0)} ({float(I0 / R):.3f}/unit k), I1 <= {V.hi_sci(I1)} "
            f"({float(I1 / R):.3f}/unit k); gauge factors <= {V.hi_sci(g0[0])}, {V.hi_sci(g1[0])}; M_F <= {V.hi_sci(MF)}, "
            f"M_trM0 <= {V.hi_sci(MT0)}, M_trM1 <= {V.hi_sci(MT1)}; n = {n} (bound F {V.hi_sci(eF)}); crude/centred "
            f"median {rows[-1]['ratio_median'][0]:.1f} / {rows[-1]['ratio_median'][1]:.1f}   [{time.time() - ts:.0f} s]")
    best = min(rows, key=lambda r: (r["n"], float(arb(r["errF"]).mid()))) if rows else None
    if best:
        say(f"  CHOSEN: rho = {best['rho']}, n = {best['n']} ({best['n'] + 1} Chebyshev points); M_F <= {best['MF'][:20]}")
    say(f"  steps using the centred bound / crude only: {STATS}")
    out = dict(seg=V.SEG, version=3, norder=NORD, rows=rows, chosen=best, point_constants={k: [V.ser(v[0]), V.ser(v[1]), v[2], v[3]] for k, v in pt.items()},
               steps=[len(st0), len(st1)], selftest=st_ok, stats=STATS,
               env=dict(python=sys.version.split()[0], flint=flint.__version__, interpreter=sys.executable))
    json.dump(out, open(os.path.join(V.OUTD, f"route1_seg_M_v3{V.TAG}_nseg1.json"), "w"), indent=1)
    say(f"  prove v3: {time.time() - t0:.0f} s, peak rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")


if __name__ == "__main__":
    prove()
