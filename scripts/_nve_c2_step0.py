#!/usr/bin/env python3
"""C2 step 0 (C2_REGISTRATION.md): measure first. On a refused/inflated step box Z with the pilot k-box K, compare
  (a) v2's crude dq bound sup |dq/dk| on Z x K (dq_sup, as the certifier computes it), with
  (b) the SAMPLED sup of |dq/dk| over Z x K: point k on a 9 x 9 grid of K (corners included), z = Z's centre and four
      corners, dq/dk from the v7 field at that POINT k (c0, c0', dc0/dk, dc0'/dk; V1/V2-validated) and v2's exact
      formula (no k-Taylor), and (c) the sampled sup of |q| and |dq/dk| at k_c.
Reading (fixed in the registration): dependency artifact if (a)/(b) >= 1e3 or (a) refused with (b) finite; GEOMETRY if
(b) >= 1e6 x |dq/dk| at k_c. Diagnostic only.
    BOX=P1|P2|S1 <env for that segment> .venv313/bin/python -I -u scripts/_nve_c2_step0.py
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BOX = os.environ["BOX"]
if BOX == "P1":
    import _nve_route1_segment_v7 as L      # noqa: E402
    field = lambda k: L.field_for(k)
else:
    import _nve_route1_segment_v7B as L     # noqa: E402
    field = lambda k: L.fieldB_for(k)
from flint import acb, arb                  # noqa: E402

V = L.V
A, E2 = V.A, V.E2
kc = L.S6.KC
half = L.S6.HALF
R = (half * (arb(4) + arb(1) / 4) / 2).upper()
K, subs = V.kbox(kc, R)
lau_c, laud_c = V.laurent(acb(kc)), V.laurent(acb(kc), True)
t0 = time.time()

if BOX == "P1":
    Z = acb(arb("1.3212671876211906"), arb("0.27535020507557856")) + arb("0.01") * V.UNIT
elif BOX == "P2":
    Z = acb(arb("1.5032047629632235"), arb(0)) + arb("0.01") * V.UNIT
else:                                       # S1: the lasso step with the largest stored bound (index 486)
    sing = [complex(float(p[0]), float(p[1])) for p in L.REF["points"]]
    _M1, st1 = V.walk(L.LAS, acb(kc), lau_c, sing, record=True)
    Z = st1[486][0]


def dq_point(z, k):
    fld = field(k)
    st = fld.at(z)
    c0, c0p, D0, D1 = st["c0"], st["c0p"], st["D0"], st["D1"]
    Dp = z * z + A * A
    f0 = (z * z - 2 * z + A * A) / Dp
    f0p = 2 * (z * z - A * A) / (Dp * Dp)
    G2 = f0 * f0 + c0 * c0
    dG2 = 2 * (f0 * f0p + c0 * c0p)
    G1 = E2 * G2 - f0
    dG1 = E2 * dG2 - f0p
    G12 = G1 * G2
    lam = dG1 / G1 - dG2 / G2
    X = 2 * f0 * c0 * D0 / G12
    dlam = 2 * (f0p * c0 * D0 + f0 * c0p * D0 + f0 * c0 * D1) / G12 - X * (dG1 / G1 + dG2 / G2)
    return lam * dlam * 3 / 8, lam * lam * 3 / 16


crude = V.dq_sup(Z, K, subs, lau_c, laud_c)
crude_v = None if crude is None else float(crude[0])
zs = [acb(Z.real.mid(), Z.imag.mid())]
for sx in (-1, 1):
    for sy in (-1, 1):
        zs.append(acb(Z.real.mid() + sx * Z.real.rad(), Z.imag.mid() + sy * Z.imag.rad()))
samp_dq, samp_q = 0.0, 0.0
n = 0
for i in range(9):
    for j in range(9):
        k = acb(kc - R + 2 * R * i / 8, -R + 2 * R * j / 8)
        k = acb(k.real.mid(), k.imag.mid())
        for z in zs:
            dq, q = dq_point(z, k)
            samp_dq = max(samp_dq, float(dq.abs_upper()))
            samp_q = max(samp_q, float(q.abs_upper()))
            n += 1
dq_c, q_c = dq_point(zs[0], acb(kc))
dq_c = float(dq_c.abs_upper())
ratio = None if crude_v is None else crude_v / samp_dq
if (crude_v is None and samp_dq < float("inf")) or (ratio is not None and ratio >= 1e3):
    reading = "DEPENDENCY ARTIFACT"
elif samp_dq >= 1e6 * dq_c:
    reading = "GEOMETRY"
else:
    reading = "NEITHER (crude within 1e3 of the sampled sup, and no explosion)"
if samp_dq >= 1e6 * dq_c:
    reading += " [also: sampled sup >= 1e6 x the k_c value]"
out = dict(box=BOX, k_c=str(kc), R=float(R), Z=[Z.real.str(10), Z.imag.str(10)], crude=crude_v, sampled_dq=samp_dq,
           sampled_q=samp_q, dq_at_kc=dq_c, ratio=ratio, n_samples=n, reading=reading, sec=round(time.time() - t0, 1))
print(f"C2 step 0 {BOX}: crude {crude_v}; sampled sup |dq/dk| {samp_dq:.3e} ({n} samples), at k_c {dq_c:.3e}; "
      f"sampled sup |q| {samp_q:.3e}; crude/sampled {ratio}; -> {reading}   [{out['sec']} s]", flush=True)
OUTD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "nve", "route1_check", "v7")
json.dump(out, open(os.path.join(OUTD, f"c2_step0_{BOX}.json"), "w"), indent=1)
