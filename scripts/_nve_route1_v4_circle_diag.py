#!/usr/bin/env python3
"""Why is the spin-9/10 circle constant on the k-disc 11x its point value under v4? (office, 2026-11-26; diagnosis,
not a proof). For every circle step at rho = 3 (R from row_for), three numbers at the step:
    P = v4 bound with K the point k_c                    (recomputed here, v4 code, R = 0)
    S = max |dq/dk| at the step MIDPOINT over 8 points k on the disc boundary |k - k_c| = R, and k_c itself
        (point-k Laurents; a SAMPLED lower estimate of the intrinsic sup over the disc, by max modulus)
    B = v4 certified bound on the k-disc                 (read from the committed per-step checkpoint, exact)
S/P is the intrinsic k-variation; B/S the enclosure overhead in k. Contributions to the Dyson sum are weighted
exactly as in v2.dyson_sum, in the rho = 3 row's own gauge C0 (so sum B w reproduces that row's circle constant).
Binned by the polar angle of the step midpoint. Also |1 - k_c phi| at the midpoint (the seal's suspect).
    NVE_SPIN=9/10 R1_R0=1.2639 nice -n 12 <quantum python> -I -u scripts/_nve_route1_v4_circle_diag.py"""
import cmath
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flint import acb, arb             # noqa: E402
import _nve_route1_segment_v2 as V     # noqa: E402
import _nve_route1_segment_v4 as W     # noqa: E402

OUT = os.path.join(V.OUTD, f"route1_v4_circle_diag{V.TAG}.out")
W.LOG4 = OUT
say = W.say
t0 = time.time()
ref = json.load(open(os.path.join(V.OUTD, V.FLOATS)))["21/20"]
sing = [complex(float(p[0]), float(p[1])) for p in ref["points"]]
(kc, half), = V.seg_centres(1)
lau_c, laud_c = V.laurent(acb(kc)), V.laurent(acb(kc), True)
M0, st0 = V.walk(V.circle_vertices(), acb(kc), lau_c, sing, record=True)
rb = arb(3)
R = (half * (rb + 1 / rb) / 2).upper()
say(f"== v4 circle diagnosis == {V.SEG}; circle {V.R0S}, {len(st0)} steps; rho = 3, R <= {V.hi_sci(R)}  [{time.time() - t0:.0f} s]")
key = W.ck_key(st0, R, "circle")
have = W.ck_load(key)
assert len(have) == len(st0), f"checkpoint has {len(have)} of {len(st0)} steps for this key"
B = [float(have[i][0]) for i in range(len(st0))]
P = [float(x) for x in W.dq_list_v4(st0, kc, arb(0), lau_c, laud_c)[0]]
say(f"  P (point) recomputed, B (disc) from checkpoint  [{time.time() - t0:.0f} s]")
ks = [kc] + [kc + R * acb(math.cos(2 * math.pi * j / 8), math.sin(2 * math.pi * j / 8)) for j in range(8)]
laus = [(V.laurent(k), V.laurent(k, True)) for k in ks]
row3 = next(json.loads(ln) for ln in open(W.ROWS) if json.loads(ln)["rho"] == 3.0)
Cb = V.cmat([[complex(x) for x in r] for r in row3["gauge"]["C0"]])
detC = (Cb[0][0] * Cb[1][1] - Cb[0][1] * Cb[1][0]).abs_lower()
S, ang, w, onekphi = [], [], [], []
A2 = float((V.A * V.A).mid())
for Z, hm, a1, a2 in st0:
    zm = acb(Z.real.mid(), Z.imag.mid())
    best = 0.0
    for k, (la, lad) in zip(ks, laus):
        r = V.dq_sup(zm, k, None, la, lad)
        best = max(best, float(r[0])) if r is not None else float("inf")
    S.append(best)
    z = complex(float(Z.real.mid()), float(Z.imag.mid()))
    ang.append(math.degrees(cmath.phase(z)))
    b1 = a1 * Cb[0][0] + a2 * Cb[1][0]
    b2 = a1 * Cb[0][1] + a2 * Cb[1][1]
    w.append(float(hm * (b1.abs_upper() ** 2 + b2.abs_upper() ** 2) / detC))
    u2 = z * z / A2
    phi = (21 * u2 * u2 - 18 * u2 + 1) / (10 * (3 * u2 - 1) ** 2)
    onekphi.append(abs(1 - 1.05 * phi))
say(f"  S (sampled disc max at the midpoint, 9 k-points) done  [{time.time() - t0:.0f} s]")
tot = {nm: sum(x * y for x, y in zip(v, w)) for nm, v in (("P", P), ("S", S), ("B", B))}
say(f"  weighted sums (row gauge C0; B-sum should equal the row constant {row3['c0_per_k']:.3f}): P {tot['P']:.4g}, S {tot['S']:.4g}, B {tot['B']:.4g}; "
    f"S/P {tot['S'] / tot['P']:.2f} (intrinsic k-variation), B/S {tot['B'] / tot['S']:.2f} (enclosure overhead), "
    f"B/P {tot['B'] / tot['P']:.2f}")
say("  by polar angle of the midpoint (deg): share of the B-sum, share of the P-sum, weighted S/P, weighted B/S, min |1 - k_c phi|")
edges = list(range(-180, 181, 30))
for lo, hi in zip(edges[:-1], edges[1:]):
    idx = [i for i, a in enumerate(ang) if lo <= a < hi or (hi == 180 and a == 180)]
    if not idx:
        continue
    sb = sum(B[i] * w[i] for i in idx)
    sp = sum(P[i] * w[i] for i in idx)
    ss = sum(S[i] * w[i] for i in idx)
    say(f"    [{lo:4d}, {hi:4d}): B {100 * sb / tot['B']:5.1f}%  P {100 * sp / tot['P']:5.1f}%  S/P {ss / sp:6.2f}  "
        f"B/S {sb / ss:6.2f}  min|1-kphi| {min(onekphi[i] for i in idx):.3g}   ({len(idx)} steps)")
top = sorted(range(len(st0)), key=lambda i: -B[i] * w[i])[:8]
say("  the 8 steps with the largest B contribution: angle, B/P, S/P, |1 - k_c phi|")
for i in top:
    say(f"    {ang[i]:8.2f}  B/P {B[i] / P[i]:8.2f}  S/P {S[i] / P[i]:6.2f}  |1-kphi| {onekphi[i]:.3g}")
say(f"  done in {time.time() - t0:.0f} s")
