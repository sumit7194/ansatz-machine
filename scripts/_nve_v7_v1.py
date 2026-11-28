#!/usr/bin/env python3
"""v7 stage V1 test harness (registration V7_REGISTRATION.md, addenda 1-2). Two modes, two interpreters:
    NVE_SPIN=3/5 R1_R0=1.35   .venv/bin/python    -I scripts/_nve_v7_v1.py engine   # mpmath engine -> json
    NVE_SPIN=3/5 R1_R0=1.35   .venv313/bin/python -I scripts/_nve_v7_v1.py arb      # Arb, exact, Laurent, verdict
(and NVE_SPIN=9/10 R1_R0=1.2639). Outputs in data/nve/route1_check/v7/.
Criteria:
  (a) exact controls at k = 0 and k = 4: Arb balls contain the exact c0, c0' with radius <= 1e-40; engine within 1e-40.
  (b) k = 1, 1.3, ..., 3.7 at two circle points (120 and 240 deg): v7 and Laurent balls both radius <= 1e-30 and
      overlapping; the engine as a 1e-40 ball overlapping the v7 ball. Wider balls -> UNINFORMATIVE.
  (c) one circuit of |z| = R0 at k = 3 and 3.9: returned balls radius <= 1e-30 and containing the start.
  (d) must-fail controls (i)-(iv) must FIRE.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SPIN = os.environ["NVE_SPIN"]
R0S = os.environ["R1_R0"]
TAG = SPIN.replace("/", "_")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTD = os.path.join(ROOT, "data", "nve", "route1_check", "v7")
os.makedirs(OUTD, exist_ok=True)
EJSON = os.path.join(OUTD, f"v1_engine_{TAG}.json")

KB = [f"{10 + 3 * j}/10" for j in range(10)]          # 1, 1.3, ..., 3.7
NCIRC_A, NREAL_A, NCIRC_B, NCIRC_C = 5, 5, 6, 16


def plan():
    """(name, k, path kind, number of vertices) -- shared by both modes."""
    out = []
    for k in ("0", "4"):
        out.append((f"a_circle_k{k}", k, "circle", NCIRC_A))
        out.append((f"a_real_k{k}", k, "real", NREAL_A))
    for k in KB:
        out.append((f"b_k{k}", k, "circle", NCIRC_B))
    for k in ("3", "39/10"):
        out.append((f"c_k{k}", k, "circle", NCIRC_C))
    return out


# ================================================================================================ engine mode (mpmath)
def run_engine():
    import mpmath as mp
    from _nve_v7_c0_engine import E0
    mp.mp.dps = 50
    R0 = mp.mpf(R0S)
    res = {}
    t0 = time.time()
    for name, k, kind, n in plan():
        kk = mp.mpf(k.split("/")[0]) / (mp.mpf(k.split("/")[1]) if "/" in k else 1)
        e = E0(SPIN, kk)
        st = e.start(R0)
        if kind == "circle":
            vs = [R0 * mp.expj(2 * mp.pi * j / n) for j in range(n + 1)]
            vs[-1] = mp.mpc(R0)
        else:
            vs = [R0 + (4 - R0) * j / n for j in range(n + 1)]
        sts = e.walk(vs, st)
        cs = lambda x: [str(mp.re(x)), str(mp.im(x))]
        res[name] = [[cs(s["z"]), cs(s["c0"]), cs(s["c0p"])] for s in sts]
        print(f"engine {name}: {len(sts)} states, c0 at the end {mp.nstr(sts[-1]['c0'], 15)}", flush=True)
    res["_meta"] = dict(python=sys.version.split()[0], mpmath=mp.__version__, dps=mp.mp.dps, sec=round(time.time() - t0, 1))
    json.dump(res, open(EJSON, "w"), indent=1)
    print(f"== engine done, {time.time() - t0:.0f} s -> {EJSON}", flush=True)


# ================================================================================================ arb mode
def run_arb():
    import flint
    from flint import acb, arb
    import _nve_v7_c0 as V7
    import _nve_route1_segment_v2 as V                   # the production Laurent evaluator (spin, R0 from env)
    import mpmath as mp
    mp.mp.dps = 50
    eng = json.load(open(EJSON))
    a = arb(SPIN.split("/")[0]) / arb(SPIN.split("/")[1])
    R0 = arb(R0S)
    BAR_A, BAR_B, ENG = arb("1e-40"), arb("1e-30"), arb("1e-40")
    log = []

    def say(s):
        print(s, flush=True)
        log.append(s)

    def karb(k):
        return arb(k.split("/")[0]) / arb(k.split("/")[1]) if "/" in k else arb(k)

    def verts(kind, n):
        if kind == "circle":
            v = [acb(R0)] + [acb(R0) * acb(0, 2 * arb.pi() * j / n).exp() for j in range(1, n)] + [acb(R0)]
        else:
            v = [acb(R0 + (4 - R0) * j / n) for j in range(n + 1)]
        return v

    def eball(s):
        return acb(arb(s[0]), arb(s[1]))

    def engine_ok(vball, estr):
        e = eball(estr)
        d = (vball - e).abs_upper()
        return bool(d <= 2 * rad(vball) + ENG)

    def exact(k, z):
        if k == "0":
            D = z * z + a * a
            return -2 * a / D, 4 * a * z / (D * D)
        c = (arb(48) / 5).sqrt() * a
        D = z * z + a * a
        J = (a / z).atan() / (2 * a ** 3) - z / (2 * a * a * D)
        return -c * (1 / (2 * D) - z * J), c * J

    def rad(x):
        return max(float(x.real.rad()), float(x.imag.rad()))

    say(f"== v7 V1 (arb) == spin {SPIN}, R0 {R0S}; python {sys.version.split()[0]}, python-flint {flint.__version__}, "
        f"FLINT {getattr(flint, '__FLINT_VERSION__', '?')}; engine json {os.path.basename(EJSON)} "
        f"(python {eng['_meta']['python']}, mpmath {eng['_meta']['mpmath']})")
    t0 = time.time()
    out = {}
    res = dict(a=True, b=True, b_informative=True, c=True, c_informative=True)
    for name, k, kind, n in plan():
        c = V7.C0(SPIN, acb(karb(k)), exact_control_k0=(k == "0"))
        st = c.start(R0)
        sts = c.walk(verts(kind, n), st)
        E = eng[name]
        if name.startswith("a_"):
            worst_r, ok_x, ok_e = 0.0, True, True
            for j, s in enumerate(sts):
                ex0, ex1 = exact(k, s["z"])
                ok_x &= bool(s["c0"].overlaps(ex0) and s["c0p"].overlaps(ex1))
                worst_r = max(worst_r, rad(s["c0"]), rad(s["c0p"]))
                d0 = (eball(E[j][1]) - ex0).abs_upper()
                d1 = (eball(E[j][2]) - ex1).abs_upper()
                ok_e &= bool(d0 <= ENG and d1 <= ENG)
            ok = ok_x and worst_r <= 1e-40 and ok_e
            res["a"] &= ok
            say(f"  (a) {name}: exact inside v7 balls {ok_x}; worst radius {worst_r:.2e} (bar 1e-40); engine within 1e-40 "
                f"of exact {ok_e} -> {'PASS' if ok else 'FAIL'}   [{c.steps} steps]")
        elif name.startswith("b_"):
            lau = V.laurent(acb(karb(k)))
            for j in (2, 4):                                # 120 and 240 degrees
                s = sts[j]
                L0, L1 = V.c0_at(s["z"], lau)
                rv, rl = max(rad(s["c0"]), rad(s["c0p"])), max(rad(L0), rad(L1))
                inf_ = rv <= 1e-30 and rl <= 1e-30
                agree = bool(s["c0"].overlaps(L0) and s["c0p"].overlaps(L1))
                eok = engine_ok(s["c0"], E[j][1]) and engine_ok(s["c0p"], E[j][2])
                res["b_informative"] &= inf_
                res["b"] &= agree and eok
                diff = float((s["c0"] - L0).abs_upper())
                say(f"  (b) k {k} point {j * 60} deg: v7 radius {rv:.1e}, Laurent radius {rl:.1e} (bar 1e-30: "
                    f"{'ok' if inf_ else 'UNINFORMATIVE'}); overlap {agree}, |v7 - Laurent| <= {diff:.1e}; engine {eok}")
        else:
            s0, s1 = sts[0], sts[-1]
            rr = max(rad(s1["c0"]), rad(s1["c0p"]))
            inf_ = rr <= 1e-30
            cont = bool(s1["c0"].contains(s0["c0"].mid()) and s1["c0p"].contains(s0["c0p"].mid())
                        and s1["c0"].overlaps(s0["c0"]) and s1["c0p"].overlaps(s0["c0p"]))
            eok = engine_ok(s1["c0"], E[-1][1]) and engine_ok(s1["c0p"], E[-1][2])
            res["c_informative"] &= inf_
            res["c"] &= cont and eok
            say(f"  (c) {name}: one circuit, returned radius {rr:.1e} (bar 1e-30: {'ok' if inf_ else 'UNINFORMATIVE'}); "
                f"contains the start {cont}; engine {eok}   [{c.steps} steps]")
        out[name] = [[s["z"].str(30), s["c0"].str(30), s["c0p"].str(30)] for s in sts]

    # ---- (d) must-fail controls
    fired = {}
    try:                                               # (i) planted 1e-30 in c0'(z_s) at k = 0: (a) must fail
        c = V7.C0(SPIN, acb(0), plant={"dc0p": "1e-30"}, exact_control_k0=True)
        st = c.start(R0)
        s = c.walk(verts("real", 2), st)[-1]
        ex0, ex1 = exact("0", s["z"])
        fired["i"] = not (s["c0"].overlaps(ex0) and s["c0p"].overlaps(ex1))
    except Exception as e:                             # noqa: BLE001
        fired["i"] = f"raised {type(e).__name__} (not the intended failure mode)"
    try:                                               # (ii) planted sqrt sign flip at step 3
        c = V7.C0(SPIN, acb(3), plant={"flip_at": 3})
        c.walk(verts("circle", 8), c.start(R0))
        fired["ii"] = False
    except AssertionError as e:
        fired["ii"] = True if "branch" in str(e) else f"AssertionError: {e}"
    try:                                               # (iii) k = 4.5 must be refused
        V7.C0(SPIN, acb(arb(9) / 2))
        fired["iii"] = False
    except ValueError:
        fired["iii"] = True
    try:                                               # (iv) a path through a branch point must be refused
        c = V7.C0(SPIN, acb(3))
        p = [q for q in c.sing_points() if q.real > 0 and q.imag > 0 and abs(q - 1j * float(a.mid())) > 1e-6][0]
        st = c.start(R0)
        c.walk([acb(R0), acb(p.real, p.imag), acb(p.real, p.imag + 0.3)], st)
        fired["iv"] = False
    except AssertionError as e:
        fired["iv"] = True if ("singular" in str(e)) else f"AssertionError: {e}"
    dok = all(v is True for v in fired.values())
    say(f"  (d) must-fail controls fired: {fired} -> {'PASS' if dok else 'FAIL'}")

    b_v = "PASS" if (res["b"] and res["b_informative"]) else ("UNINFORMATIVE" if res["b"] else "FAIL")
    c_v = "PASS" if (res["c"] and res["c_informative"]) else ("UNINFORMATIVE" if res["c"] else "FAIL")
    a_v = "PASS" if res["a"] else "FAIL"
    overall = "PASS" if (a_v == b_v == c_v == "PASS" and dok) else "NOT PASS"
    say(f"VERDICT V1 spin {SPIN}: (a) {a_v}, (b) {b_v}, (c) {c_v}, (d) {'PASS' if dok else 'FAIL'} -> {overall}   "
        f"[{time.time() - t0:.0f} s]")
    json.dump(dict(log=log, states=out, fired={k: str(v) for k, v in fired.items()}, verdict=overall,
                   env=dict(python=sys.version.split()[0], flint=flint.__version__)),
              open(os.path.join(OUTD, f"v1_arb_{TAG}.json"), "w"), indent=1)


if __name__ == "__main__":
    {"engine": run_engine, "arb": run_arb}[sys.argv[1]]()
