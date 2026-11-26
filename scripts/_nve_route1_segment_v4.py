#!/usr/bin/env python3
"""Route (i), proof stage, v4: the centred z-enclosure of v3 with k-TAYLOR starting values (office, 2026-11-26;
branch office/2026-11-26-ktaylor; seal data/nve/ROUTE1_KTAYLOR_SEAL.md, committed before any run).

v3 (8b9971c) built the z-series of dq/dk at the step midpoint z_m with k a ball over a k-sub-box, taking its starting
values c0, c0', dc0/dk, dc0'/dk at z_m from the order-190 Laurent series evaluated AT THAT k-BALL. Measured at spin
9/10, that inflates (radius 0.08-4.2 against |c0| ~ 0.01-0.07), and the centred bound failed or lost on ~75% of pairs.

v4 changes only those starting values, to the form Fable's v2 dq_sup already uses (and the office verified):
    c0(z_m; k)    in c0(z_m; k_c)  + dk d_k c0(z_m; k_c)  + (dk^2 / 2) E0,
    c0'(z_m; k)   in c0'(z_m; k_c) + dk d_k c0'(z_m; k_c) + (dk^2 / 2) E1,
    d_k c0(z_m; k)  in d_k c0(z_m; k_c)  + dk E0,     d_k c0'(z_m; k)  in d_k c0'(z_m; k_c) + dk E1,
with the point-k_c values from POINT Laurent series (+ their Cauchy tail), and (E0, E1) = v2.d2kc0(z_m, K): an
ENCLOSURE of (d^2_k c0, d^2_k c0') on the whole k-square K (radial integral from infinity, rectangle rule on balls of s,
Re(1 - k phi) > 0 certified on every ball). Taylor's theorem with integral remainder on the segment [k_c, k] (inside the
convex K) puts the remainder in (dk^2/2) x (the convex box containing d^2_k c0 on K), and the first-derivative
remainder in dk x (that box). If d2kc0 is not certified at z_m, that step keeps v2's crude bound.
The z-series itself (c0'' = c_K'' sqrt(1 - k phi) and its k-derivative in closed form, k a ball), the outer-box Cauchy
remainder in z (v2 dq_sup on a box 2x, else 1.5x, wider), min(centred, crude) and the order 30 are v3's, imported.

Checkpoints: each finished rho row is appended to data/nve/eps/route1_seg_v4{TAG}_rows.jsonl (a rerun skips rows
already there), and within a row the per-step dq bounds go to route1_seg_v4{TAG}_dqck.jsonl every R1_CK_EVERY (200)
steps, flushed and fsynced, exact (added after the 2026-11-26 power cut; resume test: _nve_route1_v4_cktest.py). No caps. Choice of rows: R1_RHOS (default "3,4,5,6.5").
    NVE_SPIN=3/5 R1_R0=1.35 nice -n 12 <quantum python> -I -u scripts/_nve_route1_segment_v4.py
Outputs: data/nve/eps/route1_seg_M_v4{TAG}_nseg1.json, route1_seg_{spin}_v4.out.  One process, one core, < 300 MB.
(Restored verbatim 2026-11-26 after the power cut: the first copy lived in a /private/tmp worktree, which the reboot
cleared before it was committed.)"""
import hashlib
import json
import math
import os
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flint                                       # noqa: E402
from flint import acb, acb_series, arb, ctx        # noqa: E402
import _nve_route1_segment_v2 as V                 # noqa: E402
import _nve_route1_segment_v3 as S3                # noqa: E402

A, E2, NORD = V.A, V.E2, S3.NORD
RHOS4 = tuple(float(x) for x in os.environ.get("R1_RHOS", "3,4,5,6.5").split(","))
LOG4 = V.LOG.replace("_v2.out", "_v4.out")
ROWS = os.path.join(V.OUTD, f"route1_seg_v4{V.TAG}_rows.jsonl")
STATS = dict(centred=0, crude_kept=0, no_series=0, no_d2k=0, rout2=0, rout15=0)
CK_EVERY = int(os.environ.get("R1_CK_EVERY", "200"))
CKFILE = os.environ.get("R1_CKFILE", os.path.join(V.OUTD, f"route1_seg_v4{V.TAG}_dqck.jsonl"))


def ck_key(steps, R, name):
    """Identity of a dq list: segment, R, loop, number of steps and a hash of every step (box, length)."""
    h = hashlib.sha256("".join(f"{Z}|{hm};" for Z, hm, _a1, _a2 in steps).encode()).hexdigest()[:16]
    return f"{V.SEG}|R={V.ser(R)}|{name}|nsteps={len(steps)}|steps={h}"


def ck_enc(x):
    """An EXACT point arb (an upper bound) as integers (mantissa, exponent): the reload is the same number."""
    assert x.rad() == 0
    m, e = x.man_exp()
    return [int(m), int(e)]


def ck_dec(me):
    return arb(me[0]) * arb(2) ** me[1]


def ck_load(key):
    """-> {step index: (bound, ratio, how)} for this key. A torn LAST line (power cut mid-write) is dropped and the
    file truncated to the last complete record; a bad line anywhere else is a correctness gate (raises)."""
    got = {}
    if not os.path.exists(CKFILE):
        return got
    raw = open(CKFILE, "rb").read()
    cut = raw.rfind(b"\n") + 1
    if cut < len(raw):
        say(f"  checkpoint: torn last record ({len(raw) - cut} bytes) dropped; file truncated to {cut} bytes")
        with open(CKFILE, "r+b") as fh:
            fh.truncate(cut)
            fh.flush()
            os.fsync(fh.fileno())
    for ln in raw[:cut].split(b"\n")[:-1]:
        r = json.loads(ln)
        if r["key"] != key:
            continue
        for i, me, rat, how in r["vals"]:
            got[i] = (ck_dec(me), rat, how)
    assert sorted(got) == list(range(len(got))), "checkpoint records are not a prefix of the step list"
    return got


def ck_write(key, buf):
    with open(CKFILE, "a") as fh:
        fh.write(json.dumps(dict(key=key, vals=buf)) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG4, "a") as fh:
        fh.write(s + "\n")


def series_from_init(zm, kball, init):
    """v3's _dq_series with the starting values passed in (c0v, c0pv, D0v, D1v), not read from a k-ball Laurent."""
    try:
        ctx.cap = NORD + 4
        c0v, c0pv, D0v, D1v = init
        t = acb_series([zm, 1])
        z2 = t * t
        u2 = z2 / (A * A)
        cK2 = (3 * u2 - 1) * (-4) / ((u2 + 1) * (u2 + 1) * (u2 + 1) * (A * A * A))
        phi = (21 * u2 * u2 - 18 * u2 + 1) / (10 * (3 * u2 - 1) * (3 * u2 - 1))
        sq = (1 - kball * phi).sqrt()
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
        if G1.coeffs()[0].contains(0) or G2.coeffs()[0].contains(0):
            return None
        G12 = G1 * G2
        lam = dG1 / G1 - dG2 / G2
        X = 2 * f0 * c0 * D0 / G12
        dlam = 2 * (f0p * c0 * D0 + f0 * c0p * D0 + f0 * c0 * D1) / G12 - X * (dG1 / G1 + dG2 / G2)
        c = (lam * dlam * 3 / 8).coeffs()
        c = (c + [acb(0)] * (NORD + 1 - len(c)))[:NORD + 1]
        return c if all(x.is_finite() for x in c) else None
    except (ValueError, ZeroDivisionError):
        return None


def dq_list_v4(steps, kc, R, lau_c, laud_c, name=None):
    """Per step: a point arb >= sup |dq/dk| on the step segment for every k in the k-square; (None, where) if v2's
    crude enclosure itself fails (a holomorphy box), exactly as v2/v3 reject the row.
    name: if given, per-step bounds are checkpointed to CKFILE every CK_EVERY steps (flushed, fsynced) and a rerun
    resumes after the last complete record. The stored bounds are exact, so a resumed list equals an uninterrupted one."""
    K, dKs = V.kbox(kc, R)
    dks = [acb(0)] if dKs is None else dKs
    out, ratios = [], []
    key = ck_key(steps, R, name) if name else None
    have = ck_load(key) if key else {}
    if have:
        say(f"  checkpoint: {name}, R = {V.hi_sci(R)}: resuming after {len(have)} of {len(steps)} steps")
    buf = []
    for idx, (Z, hm, _a1, _a2) in enumerate(steps):
        if idx in have:
            b, rat, how = have[idx]
            out.append(b)
            ratios.append(rat)
            STATS["centred" if how == "c" else "crude_kept"] += 1
            continue
        nb = len(out)
        crude = V.dq_sup(Z, K, dKs, lau_c, laud_c)
        if crude is None:
            return None, complex(Z.real.mid(), Z.imag.mid()), None
        crude = crude[0]
        zm = acb(Z.real.mid(), Z.imag.mid())
        r = hm
        best = None
        c0c, c0pc = V.c0_at(zm, lau_c)
        D0c, D1c = V.c0_at(zm, laud_c)
        if dKs is None:
            E0 = E1 = acb(0)
        else:
            e = V.d2kc0(zm, K)
            if e is None:
                STATS["no_d2k"] += 1
                e = None
            E0, E1 = e if e is not None else (None, None)
        if E0 is not None:
            for fac in (2, 1.5):
                try:
                    mo = V.dq_sup(zm + r * fac * V.UNIT, K, dKs, lau_c, laud_c)
                except RuntimeError:
                    mo = None
                if mo is None:
                    continue
                q = 1 / arb(fac)
                rem = (mo[0] * q ** (NORD + 1) / (1 - q)).upper()
                worst, ok = None, True
                for dk in dks:
                    dk2 = dk * dk / 2
                    init = (c0c + dk * D0c + dk2 * E0, c0pc + dk * D1c + dk2 * E1, D0c + dk * E0, D1c + dk * E1)
                    c = series_from_init(zm, kc + dk, init)
                    if c is None:
                        ok = False
                        break
                    pol, rp = c[0].abs_upper(), arb(1)
                    for j in range(1, NORD + 1):
                        rp = rp * r
                        pol = pol + c[j].abs_upper() * rp
                    val = (pol + rem).upper()
                    worst = val if worst is None or val > worst else worst
                if ok:
                    best = worst
                    STATS["rout2" if fac == 2 else "rout15"] += 1
                    break
                STATS["no_series"] += 1
        if best is not None and best < crude:
            out.append(best)
            STATS["centred"] += 1
        else:
            out.append(crude)
            STATS["crude_kept"] += 1
        ratios.append(float(crude) / float(out[-1]))
        if key:
            buf.append([idx, ck_enc(out[-1]), ratios[-1], "c" if best is not None and best < crude else "k"])
            if len(buf) >= CK_EVERY or idx == len(steps) - 1:
                ck_write(key, buf)
                buf = []
        assert len(out) == nb + 1
    assert len(out) == len(steps) and all(x.is_finite() for x in out)
    return out, None, ratios


def row_for(rho, half, kc, st0, st1, M0, M1, lau_c, laud_c, n_force=None):
    rb = arb(rho)
    R = (half * (rb + 1 / rb) / 2).upper()
    K, dKs = V.kbox(kc, R)
    pre = V.precondition(K)
    if not pre["ok"]:
        return dict(rho=rho, rejected="precondition not certified", precondition=pre)
    d0, w0, r0 = dq_list_v4(st0, kc, R, lau_c, laud_c, name="circle")
    d1, w1, r1 = dq_list_v4(st1, kc, R, lau_c, laud_c, name="lasso") if d0 is not None else (None, None, None)
    if d0 is None or d1 is None:
        return dict(rho=rho, rejected=f"holomorphy box fails at {w0 if d0 is None else w1}")
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
    return dict(rho=rho, n=n, R=V.ser(R), I0=V.ser(I0), I1=V.ser(I1), c0_per_k=float(I0 / R), c1_per_k=float(I1 / R),
                MF=V.ser(MF), MT0=V.ser(MT0), MT1=V.ser(MT1), errF=V.ser(eF), errT0=V.ser(e0), errT1=V.ser(e1),
                precondition=pre, gauge=dict(C0=[[str(x) for x in rr] for rr in C0], C1=[[str(x) for x in rr] for rr in C1],
                                            norms0=[V.ser(x) for x in g0], norms1=[V.ser(x) for x in g1]),
                ratio_median=[sorted(r0)[len(r0) // 2], sorted(r1)[len(r1) // 2]], ratio_max=[max(r0), max(r1)],
                stats=dict(STATS))


def prove():
    t0 = time.time()
    V.coverage_asserts()
    ref = json.load(open(os.path.join(V.OUTD, V.FLOATS)))["21/20"]
    sing = [complex(float(p[0]), float(p[1])) for p in ref["points"]]
    lasso = [complex(float(p[0]), float(p[1])) for p in ref["lasso"]]
    say(f"== prove (v4: centred z-series, k-Taylor starting values, order {NORD}) == {V.SEG}; circle {V.R0S}; "
        f"python {sys.version.split()[0]}, python-flint {flint.__version__}; prec {ctx.prec} bits; rows {RHOS4}")
    (kc, half), = V.seg_centres(1)
    lau_c, laud_c = V.laurent(acb(kc)), V.laurent(acb(kc), True)
    st_ok = V.selftest(kc, lau_c, laud_c)
    say(f"  derivative self-test (v2's): {st_ok}")
    M0, st0 = V.walk(V.circle_vertices(), acb(kc), lau_c, sing, record=True)
    M1, st1 = V.walk(lasso, acb(kc), lau_c, sing, record=True)
    say(f"  reference: circle {len(st0)} steps, lasso {len(st1)} steps, {time.time() - t0:.0f} s")
    pt = {}
    for nm, st in (("circle", st0), ("lasso", st1)):
        d4, _w, rat = dq_list_v4(st, kc, arb(0), lau_c, laud_c)
        pt[nm] = (V.dyson_sum(st, d4, V.gauge(st, d4)), max(rat), sorted(rat)[len(rat) // 2])
        say(f"  {nm}, K a point (z-direction control; v3 printed 4.153E-1 / 9.325E+0 at 3/5, 7.734E-1 / 2.179E+1 at 9/10): "
            f"v4 <= {V.hi_sci(pt[nm][0])}   [{time.time() - t0:.0f} s]")
    done = {}
    if os.path.exists(ROWS):
        for line in open(ROWS):
            rr = json.loads(line)
            done[rr["rho"]] = rr
    for rho in RHOS4:
        if rho in done:
            say(f"  rho = {rho}: from checkpoint {os.path.basename(ROWS)}")
            continue
        ts = time.time()
        row = row_for(rho, half, kc, st0, st1, M0, M1, lau_c, laud_c)
        row["sec"] = round(time.time() - ts)
        with open(ROWS, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        done[rho] = row
        if "rejected" in row:
            say(f"  rho = {rho}: REJECTED ({row['rejected']})")
            continue
        say(f"  rho = {rho}: I0 <= {V.hi_sci(arb(row['I0']))} ({row['c0_per_k']:.3f}/unit k), I1 <= {V.hi_sci(arb(row['I1']))} "
            f"({row['c1_per_k']:.3f}/unit k); M_F <= {V.hi_sci(arb(row['MF']))}, M_trM0 <= {V.hi_sci(arb(row['MT0']))}, "
            f"M_trM1 <= {V.hi_sci(arb(row['MT1']))}; n = {row['n']}; crude/v4 median {row['ratio_median'][0]:.1f} / "
            f"{row['ratio_median'][1]:.1f}; cumulative stats {row['stats']}   [{row['sec']} s]")
    rows = [done[r] for r in RHOS4 if r in done and "rejected" not in done[r]]
    best = min(rows, key=lambda r: (r["n"], float(arb(r["errF"]).mid()))) if rows else None
    if best:
        say(f"  CHOSEN: rho = {best['rho']}, n = {best['n']} ({best['n'] + 1} Chebyshev points); M_F <= {best['MF'][:20]}")
    out = dict(seg=V.SEG, version=4, norder=NORD, rows=rows, chosen=best, selftest=st_ok, steps=[len(st0), len(st1)],
               point_constants={k: [V.ser(v[0]), v[1], v[2]] for k, v in pt.items()},
               env=dict(python=sys.version.split()[0], flint=flint.__version__, interpreter=sys.executable))
    json.dump(out, open(os.path.join(V.OUTD, f"route1_seg_M_v4{V.TAG}_nseg1.json"), "w"), indent=1)
    say(f"  prove v4: {time.time() - t0:.0f} s, peak rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")


if __name__ == "__main__":
    prove()
