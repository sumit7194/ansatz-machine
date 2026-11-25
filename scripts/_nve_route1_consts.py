#!/usr/bin/env python3
"""Route (i): the Dyson constants and the implied node count at other k (a MEASUREMENT for the cost estimate of
data/nve/ROUTE1_SEGMENT.md section 9; it certifies nothing and runs no point evaluations).
[model: Fable 5.2; UNVERIFIED until the office ansatz-machine checks it]

For each k label given (it must be in data/nve/eps/route1_floats.json, which holds the engine's lasso of that k):
the validated reference solution at k_c = label, the Dyson constants at the point and on the k-box, and the node
count the proved M would ask for on the segment [k_c - 1/20, k_c + 1/20] at each rho. Same code as
_nve_route1_segment.prove, same loops rule (circle 1.35, the lasso of k_c).
    /Users/sumit/Github/quantum/sims/.venv/bin/python -I scripts/_nve_route1_consts.py 2 3
One process, 1 core, about 40 s per label, peak well under 300 MB. Appends to data/nve/eps/route1_seg_consts.out.
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flint                                     # noqa: E402
from flint import acb, arb                       # noqa: E402
import _nve_route1_proto as P                    # noqa: E402
import _nve_route1_segment as S                  # noqa: E402

S.LOG = os.path.join(S.OUTD, "route1_seg_consts.out")
refs = json.load(open(os.path.join(S.OUTD, "route1_floats.json")))
half = arb(1) / 20
S.say(f"== constants == python {sys.version.split()[0]}, python-flint {flint.__version__}, interpreter {sys.executable}; "
      f"spin 3/5, E = 4/5, circle 1.35, lasso of each k_c; segment half-width 1/20; k sub-boxes {S.KSUB} x {S.KSUB}")
for lab in sys.argv[1:]:
    t0 = time.time()
    ref = refs[lab]
    kc = S.frac(lab)
    sing = [complex(float(p[0]), float(p[1])) for p in ref["points"]]
    lasso = [complex(float(p[0]), float(p[1])) for p in ref["lasso"]]
    lau_c, laud_c = P.laurent(acb(kc)), S.laurent_dk(acb(kc))
    M0, st0 = S.walk_ref(P.circle_vertices(), acb(kc), lau_c, sing)
    M1, st1 = S.walk_ref(lasso, acb(kc), lau_c, sing)
    T0, T1 = M0[0][0] + M0[1][1], M1[0][0] + M1[1][1]
    Cm = P.mmul(P.mmul(M1, M0), P.mmul(P.minv(M1), P.minv(M0)))
    Fc = Cm[0][0] + Cm[1][1] - 2
    ident = [[1.0, 0.0], [0.0, 1.0]]
    pt = []
    for st in (st0, st1):
        dqs, _w = S.dq_list(st, kc, 0.0, lau_c, laud_c)
        C, _x = S.gauge(st, dqs)
        pt.append((S.dyson_sum(st, dqs, ident), S.dyson_sum(st, dqs, C)))
    S.say(f"  k_c = {lab}: steps {len(st0)} + {len(st1)}; |F| = {float(Fc.abs_lower()):.6f}, tr M0 = "
          f"{complex(T0.real.mid(), T0.imag.mid()):.6f}, tr M1 = {complex(T1.real.mid(), T1.imag.mid()):.6f}; "
          f"engine float inside: F {bool(Fc.overlaps(acb(arb(ref['F'][0]), arb(ref['F'][1]))))}")
    S.say(f"    Dyson constants at the point (per unit |k - k_c|): circle {pt[0][0]:.2f} -> {pt[0][1]:.2f} (optimised gauge); "
          f"lasso {pt[1][0]:.2f} -> {pt[1][1]:.2f}")
    tol = 1e-3 * float(Fc.abs_lower()) / 0.2958          # the same RELATIVE tolerance as the certified segment used
    for rho in S.RHOS:
        R = float(half.upper()) * (rho + 1 / rho) / 2 * S.UP
        pre = S.precondition(S.kbox(kc, R)[0])
        if not pre["ok"]:
            S.say(f"    rho = {rho}: R = {R:.4f}: precondition NOT certified ({pre['why']})")
            continue
        d0, w0 = S.dq_list(st0, kc, R, lau_c, laud_c)
        d1, w1 = S.dq_list(st1, kc, R, lau_c, laud_c) if d0 is not None else (None, None)
        if d0 is None or d1 is None:
            S.say(f"    rho = {rho}: R = {R:.4f}: a holomorphy box fails at z = {w0 if d0 is None else w1}")
            continue
        C0, _x = S.gauge(st0, d0)
        C1, _x = S.gauge(st1, d1)
        I0, I1 = R * S.dyson_sum(st0, d0, C0), R * S.dyson_sum(st1, d1, C1)
        g0, g1 = S.gauge_norms(M0, C0), S.gauge_norms(M1, C1)
        if I0 + I1 > 300:
            S.say(f"    rho = {rho}: R = {R:.4f}: exponents {I0:.1f}, {I1:.1f}: too large")
            continue
        lnMF = math.log(2 + (g1[0] * g0[0]) ** 2) + 2 * (I0 + I1)
        n = math.ceil((math.log(4 / ((rho - 1) * tol)) + lnMF) / math.log(rho))
        n += n % 2
        S.say(f"    rho = {rho}: R = {R:.4f}; max |w_root| {pre['max_root_abs_w']:.4f}; I0 = {I0:.3f}, I1 = {I1:.3f} (per unit k: "
              f"{I0 / R:.1f}, {I1 / R:.1f}); gauge factors {g0[0]:.2f}, {g1[0]:.2f}; log10 M_F = {lnMF / math.log(10):.1f}; "
              f"n = {n} for error {tol:.1e}")
    S.say(f"    [{time.time() - t0:.0f} s]")
