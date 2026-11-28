#!/usr/bin/env python3
"""C2-TM must-fire controls T3-T5 (data/nve/route1_check/C2_TM_REGISTRATION.md; T1 and T2 run inside the probe).
Each control records the guard that refused, and is judged against the guard it names:
  T3  the reciprocal precondition in the walk's own use: q_on_box at the base point with c0's TM given a planted wide
      remainder, so G2's relative variation over the box x disc exceeds 1/2. EXPECTED: "reciprocal theta-guard (G2 on
      the box)". (A planted 10R disc would trip the START's r < 1 guard first, an incidental guard, so the plant sits
      at the TM level.)
  T4  the start TM's coefficients against central differences of V1's point starts (h = rho/4, real direction), with
      the tolerance from the METHOD: |D1 - f'| <= h^2 sup|f'''|/6 + (rad f+ + rad f-)/(2h) and
      |D2 - f''| <= h^2 sup|f''''|/12 + (rad f+ + 2 rad f0 + rad f-)/h^2. sup|f'''| and sup|f''''| over [kc - h, kc + h]
      come from a SEPARATE rectangle-rule enclosure of the explicit k-derivatives of the start integrand
      (d^3 sqrt P/dk^3 = (3/8) P1^3 P^(-5/2), d^4 = -(15/16) P1^4 P^(-7/2)), independent of the TM. PASS: each
      coefficient's ball, widened by its error bound, overlaps the FD value. Must-fail plant: c1 x 1.01 outside.
  T5  a loop through a G2 zero: a planted Gamma-like edge passes exactly through G2's zero at k = kc0, which lies inside
      the disc. EXPECTED: refused through the step control, with the last refusal "reciprocal theta-guard (G2 on the
      box)" or the G2 reciprocal's constant-coefficient guard. A refusal by any other guard is recorded as "refused,
      not as specified" (as with K2s), and the test is not loosened afterwards.
    BOX=P2 <the pilot's R1_* env> .venv313/bin/python -I -u scripts/_nve_c2tm_controls.py T3|T4|T5
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BOX = os.environ["BOX"]
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
R = (HALF * (arb(4) + 1 / arb(4)) / 2).upper()
hs = (R / 5).upper()
rho = ((arb(2).sqrt() * hs) * (1 + arb(2) ** -10)).upper()      # the probe's sub disc
REF = L.S6.REF
LOOP0 = V.circle_vertices() if BOX == "P1" else list(L.GAM)
ZB = LOOP0[0]
SFORM = "circle" if BOX == "P1" else "disc"


def out(name, rec):
    json.dump(rec, open(os.path.join(OUTD, f"c2tm_{BOX}_{name}.json"), "w"), indent=1)
    print(f"C2-TM control {name} {BOX}: {rec['verdict']}  ({rec.get('why', '')})", flush=True)


def t3():
    disc = W.Disc(kc0, rho)
    st = W.start_tm(V.A, ZB, disc)
    wk = W.Walker(V, V7.C0, V.SPIN, SFORM, disc)
    zc = acb(ZB)
    rz = 0.01
    M, _md, _ms = wk.c0k.sup_box(zc, arb(rz))
    real_ok = True
    try:
        wk.q_on_box(zc, rz, st, M)
    except TMRefuse:
        real_ok = False
    planted = dict(st)
    planted["c0"] = st["c0"] + W.ball_tm(arb(1))                 # a remainder of 1 on c0: G2's variation >> |G2|
    why = None
    try:
        wk.q_on_box(zc, rz, planted, M)
    except TMRefuse as e:
        why = str(e)
    fired = why is not None and "reciprocal theta-guard (G2 on the box)" in why
    out("T3", dict(verdict="FIRED" if (fired and real_ok) else "DID NOT FIRE", why=why,
                   unplanted_passes=real_ok, expected="reciprocal theta-guard (G2 on the box)"))


def sup_kderiv(order, zb, kb, sm=256):
    """an enclosed bound of |d^order/dk^order| of c0(zb) and c0'(zb) over the k-ball kb (rectangle rule on s-balls)"""
    a = V.A
    k8 = (arb(8) / 5).sqrt() * a
    L_ = (1 / acb(zb)).real
    c2, c1, cc = 90 - 21 * kb, -(60 - 18 * kb), 10 - kb
    coef = {3: arb(3) / 8, 4: -arb(15) / 16}[order]
    e1, e0 = arb(0), arb(0)
    for i in range(sm):
        sb = acb(L_ * (2 * i + 1) / (2 * sm) + arb(0, L_ / (2 * sm)))
        a2s2 = a * a * sb * sb
        P = c2 + c1 * a2s2 + cc * a2s2 * a2s2
        P1 = -21 + 18 * a2s2 - a2s2 * a2s2
        if not (P.real > 0):
            raise TMRefuse("T4: Re P not certified positive")
        g = (coef.abs_upper() * P1.abs_upper() ** order / P.abs_lower() ** (order - arb(1) / 2)
             / ((1 + a2s2) ** 3).abs_lower()).upper()
        e1 += (sb * sb).abs_upper() * g * L_ / sm
        e0 += (sb - acb(zb) * sb * sb).abs_upper() * g * L_ / sm
    return (k8 * e0).upper(), (k8 * e1).upper()


def t4():
    disc = W.Disc(kc0, rho)
    st = W.start_tm(V.A, ZB, disc)
    h = (rho / 4).mid()
    pts = {}
    for nm_, kk in (("m", kc0 - h), ("0", kc0), ("p", kc0 + h)):
        p = V7.C0(V.SPIN, acb(kk.real.mid(), kk.imag.mid())).start(acb(ZB))
        pts[nm_] = p
    kb = kc0 + arb(0, h)
    s3 = sup_kderiv(3, ZB, kb)
    s4 = sup_kderiv(4, ZB, kb)
    res, ok = {}, True
    for i, q in enumerate(("c0", "c0p")):
        fm, f0, fp = pts["m"][q], pts["0"][q], pts["p"][q]
        D1 = (fp - fm) / (2 * h)
        D2 = (fp - 2 * f0 + fm) / (h * h)
        err1 = (h * h * s3[i] / 6 + (fp.rad() + fm.rad()) / (2 * h)).upper()
        err2 = (h * h * s4[i] / 12 + (fp.rad() + 2 * f0.rad() + fm.rad()) / (h * h)).upper()
        c1, c2 = st[q].c[1], st[q].c[2]
        e1 = st[q].e / rho                     # the TM's remainder also bounds the coefficient error (Cauchy, |dk| = rho)
        e2 = st[q].e / (rho * rho)
        w1 = c1 + acb(arb(0, err1 + e1), arb(0, err1 + e1))
        w2 = 2 * c2 + acb(arb(0, err2 + 2 * e2), arb(0, err2 + 2 * e2))
        ok1, ok2 = bool(w1.overlaps(D1)), bool(w2.overlaps(D2))
        planted = c1 * arb("1.01") + acb(arb(0, err1 + e1), arb(0, err1 + e1))
        caught = not bool(planted.overlaps(D1))
        res[q] = dict(first=ok1, second=ok2, plant_caught=caught, tol1=float(err1), tol2=float(err2))
        ok &= ok1 and ok2 and caught
    out("T4", dict(verdict="PASS" if ok else "FAIL", why=json.dumps(res), detail=res))


def t5():
    """a planted edge through G2's zero at kc0 (G2's zero nearest Gamma, from the floats entry's points)"""
    disc = W.Disc(kc0, rho)
    st = W.start_tm(V.A, ZB, disc)
    pts = [complex(float(p[0]), float(p[1])) for p in REF["points"]]
    fld = L.field_for if BOX == "P1" else L.fieldB_for
    A, E2 = V.A, V.E2

    exact = {complex(float(q[0]), float(q[1])): acb(arb(q[0]).mid(), arb(q[1]).mid()) for q in REF["points"]}

    def g2(p):
        z = exact[p]               # the floats entry's EXACT point strings (a rounded double gives |G2| about 1e-16)
        c0 = fld(kc0).at(z)["c0"]
        f0 = (z * z - 2 * z + A * A) / (z * z + A * A)
        return (f0 * f0 + c0 * c0).abs_upper()
    g2zeros = [p for p in pts if g2(p) < arb("1e-20")]               # the floats points that are zeros of G2 (not G1)
    assert g2zeros, "T5: no G2 zero among the floats entry's points"
    zstar = min(g2zeros, key=lambda p: min(abs(p - g) for g in LOOP0))
    far = 2 * zstar - ZB                                          # the segment ZB -> far passes through zstar
    loop = [ZB, complex(float(far.real), float(far.imag)), ZB]
    wk = W.Walker(V, V7.C0, V.SPIN, SFORM, disc)
    sing = [p for p in pts if abs(p - zstar) > 1e-9]             # the planted point is NOT announced to the step control
    why = None
    try:
        wk.walk(loop, st, sing, V.LIMZ)
    except TMRefuse as e:
        why = str(e)
    expected = ("reciprocal theta-guard (G2 on the box)", "theta-guard (G2 on the box): the constant coefficient contains 0")
    # (the glance's concern: the constant-coefficient refusal now names its reciprocal, so only G2's guard counts)
    if why is None:
        verdict = "DID NOT FIRE (the walk through a G2 zero was accepted)"
    elif any(x in why for x in expected):
        verdict = "FIRED"
    else:
        verdict = "refused, not as specified"
    out("T5", dict(verdict=verdict, why=why, zstar=[zstar.real, zstar.imag], expected=list(expected)))


if __name__ == "__main__":
    {"T3": t3, "T4": t4, "T5": t5}[sys.argv[1]]()
