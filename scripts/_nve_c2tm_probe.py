#!/usr/bin/env python3
"""C2-TM probe (data/nve/route1_check/C2_TM_REGISTRATION.md, "Probe"): ONE k-disc, the monodromy of both loops as
Taylor models in dk (degree 12), judged against the registered bar.
    BOX=P2|P1 KIND=sub|whole <the pilot's R1_* env> .venv313/bin/python -I -u scripts/_nve_c2tm_probe.py
KIND sub:   the disc circumscribing step 0''s centre R/5 sub-box, rho = sqrt2 hs (1 + 2^-10);
KIND whole: rho = R (1 + 2^-10), the whole Bernstein ellipse E_4 in one disc (P2 only, and only after sub passed).
Covering is computed in Arb BEFORE any walk (registration 5): sub, every corner of the sub-box strictly inside; whole,
every point of E_4's boundary (t-balls covering [0, 2 pi]) strictly inside.
Judged (the C2-3 bar, unchanged): for F, tr M0, tr M1: the TM is finite; it CONTAINS every step 0' R/5 grid sample
(T1: the TM evaluated at the grid point overlaps the node value) with eps <= 1e-3 x the sampled max |F|;
sup |TM| <= 100 x the sampled max |.|; and the cost (time per disc x discs covering E_4 / 2 cores) <= 2 h per segment.
T2 (the checker plant): at one grid point the TM value is shifted by 10 x (eps + the node's radius); it MUST be caught.
Reported: the tightness ratio, eps per edge on every loop, the time.
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BOX = os.environ["BOX"]
KIND = os.environ.get("KIND", "sub")
assert KIND in ("sub", "whole") and not (KIND == "whole" and BOX != "P2")
if BOX == "P1":
    import _nve_route1_segment_v7 as L      # noqa: E402
else:
    import _nve_route1_segment_v7B as L     # noqa: E402
import _nve_v7_c0 as V7                     # noqa: E402
import _nve_c2tm_walk as W                  # noqa: E402
from _nve_c2tm_core import TM, TMRefuse     # noqa: E402
from flint import acb, arb, ctx             # noqa: E402

ctx.prec = 256
V = L.V
ROOT = os.path.dirname(HERE)
OUTD = os.path.join(ROOT, "data", "nve", "route1_check", "c2")
KC, HALF = L.S6.KC, L.S6.HALF
kc0 = acb(arb(KC).mid())
RHO_E = arb(4)
R = (HALF * (RHO_E + 1 / RHO_E) / 2).upper()
hs = (R / 5).upper()
MARGIN = 1 + arb(2) ** -10
rho = ((arb(2).sqrt() * hs) * MARGIN).upper() if KIND == "sub" else (R * MARGIN).upper()
REF = L.S6.REF
if BOX == "P1":
    LOOPS = [V.circle_vertices(), [complex(float(p[0]), float(p[1])) for p in REF["lasso"]]]
    SFORM = "circle"
else:
    LOOPS = [list(L.GAM), list(L.LAS)]
    SFORM = "disc"
SING = [complex(float(p[0]), float(p[1])) for p in REF["points"]]
TAG = f"c2tm_probe_{BOX}_{KIND}"


def covering():
    """certified in Arb: the region the probe stands for lies strictly inside the disc"""
    if KIND == "sub":
        for sx in (-1, 1):
            for sy in (-1, 1):
                corner = acb(sx * hs, sy * hs)
                if not (corner.real * corner.real + corner.imag * corner.imag) < rho * rho:
                    return False
        return True
    a_e = R
    b_e = (HALF * (RHO_E - 1 / RHO_E) / 2).upper()
    nb = 4096
    for i in range(nb):
        t = arb.pi() * 2 * (2 * i + 1) / (2 * nb) + arb(0, arb.pi() * 2 / (2 * nb))
        x, y = a_e * t.cos(), b_e * t.sin()
        if not (x * x + y * y) < rho * rho:
            return False
    return True


def adj(M):
    return [[M[1][1], -M[0][1]], [-M[1][0], M[0][0]]]


def mm(X, Y):
    return [[X[i][0] * Y[0][j] + X[i][1] * Y[1][j] for j in range(2)] for i in range(2)]


def main():
    t0 = time.time()
    cov = covering()
    rec = dict(box=BOX, kind=KIND, k_c=str(KC), rho=float(rho), R=float(R), hs=float(hs), covering=cov, d=W.D)
    if not cov:
        rec["verdict"] = "STOPPED: the covering is not certified"
        json.dump(rec, open(os.path.join(OUTD, f"{TAG}.json"), "w"), indent=1)
        print(f"C2-TM probe {BOX} {KIND}: STOPPED (covering)", flush=True)
        return
    disc = W.Disc(kc0, rho)
    zb = LOOPS[0][0]
    try:
        st0 = W.start_tm(V.A, zb, disc)
        Ms, logs, steps = [], [], []
        for lp in LOOPS:
            wk = W.Walker(V, V7.C0, V.SPIN, SFORM, disc)
            Mm, n = wk.walk(lp, st0, SING, V.LIMZ)
            Ms.append(Mm)
            logs.append(wk.eps_log)
            steps.append(n)
    except TMRefuse as e:
        rec.update(verdict=f"FAIL (refused: {e})", t=round(time.time() - t0, 1))
        json.dump(rec, open(os.path.join(OUTD, f"{TAG}.json"), "w"), indent=1)
        print(f"C2-TM probe {BOX} {KIND}: REFUSED: {e}", flush=True)
        return
    M0, M1 = Ms
    Cm = mm(mm(M1, M0), mm(adj(M1), adj(M0)))
    F = Cm[0][0] + Cm[1][1] - 2
    T0 = M0[0][0] + M0[1][1]
    T1 = M1[0][0] + M1[1][1]
    tms = dict(F=F, T0=T0, T1=T1)
    t_disc = time.time() - t0
    # T1 (containment) and T2 (the checker plant) on the step 0' R/5 grid samples
    S = [json.loads(ln) for ln in open(os.path.join(OUTD, f"step0p_{BOX}_k5_samples.jsonl"))]
    assert len({(d["i"], d["j"]) for d in S}) == 81
    per, contained_all, tight = {}, True, []
    sampled_max = {}
    for nm, tm in tms.items():
        ok = True
        smax = arb(0)
        for d in S:
            k = acb(arb(d["k"][0]), arb(d["k"][1]))
            dk = k - kc0
            val = tm.at(dk)
            node = acb(arb(d[nm][0]), arb(d[nm][1]))
            ok &= bool(val.overlaps(node))
            smax = max(smax, node.abs_upper())
            if nm == "F":
                gap = (acb(val.mid()) - acb(node.mid())).abs_upper()
                tight.append(float(((tm.e - gap + node.rad()) / tm.e).mid()) if tm.e > 0 else float("inf"))
        per[nm] = dict(contained=ok, sup=float(tm.bound().mid()), sampled_max=float(smax.mid()),
                       sup_ratio=float((tm.bound() / smax).mid()), e=float(tm.e.mid()),
                       ok=bool(ok and tm.is_finite() and tm.bound() <= 100 * smax))
        sampled_max[nm] = smax
        contained_all &= ok
    eps_small = bool(F.e <= sampled_max["F"] / 1000)
    # T2: shift the TM value at one grid point by 10 (e + rad); it must be caught there
    d = S[40]
    k = acb(arb(d["k"][0]), arb(d["k"][1]))
    node = acb(arb(d["F"][0]), arb(d["F"][1]))
    shift = (10 * (F.e + node.rad() * 2 + F.at(k - kc0).rad())).upper()
    t2 = not (F.at(k - kc0) + shift).overlaps(node)
    cost_h = t_disc * (25 if KIND == "sub" else 1) / 2 / 3600
    ok = all(p["ok"] for p in per.values()) and eps_small and cost_h <= 2 and t2
    rec.update(per=per, eps_le_1e3_samplemax=eps_small, T2_plant_caught=t2, tightness_min=min(tight),
               cost_hours_per_segment=round(cost_h, 3), t_disc=round(t_disc, 1), steps=steps, eps_log=logs,
               verdict="PASS" if ok else "FAIL")
    json.dump(rec, open(os.path.join(OUTD, f"{TAG}.json"), "w"), indent=1)
    print(f"C2-TM probe {BOX} {KIND}: {rec['verdict']}; per {per}; T2 caught {t2}; tightness {min(tight):.3g}; "
          f"cost {cost_h:.2f} h; {t_disc:.0f} s", flush=True)


if __name__ == "__main__":
    main()
