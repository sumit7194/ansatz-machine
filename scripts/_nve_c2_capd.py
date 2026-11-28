#!/usr/bin/env python3
"""C2 glue (C2_REGISTRATION.md, addendum C2-1, step 0'): the CAPD monodromy enclosure over ONE complex k-sub-box.

Modes (BOX = P1 | P2, with that pilot's R1_* environment, as in air/v7_p1.sh and air/v7_pB.sh):
  drive    build the affine-in-dk initial doubleton at the loops' base point, run scripts/c2_capd/build/c2_driver on
           both loops (loop 0 = the circle (P1) or Gamma (P2): M0; loop 1 = the lasso: M1), read the final sets back
           EXACTLY and enclose F = tr(M1 M0 M1^-1 M0^-1) - 2, tr M0 and tr M1 over the sub-box, by first-order affine
           arithmetic in (u, v) = (Re dk, Im dk) (the C r0 part CAPD keeps) with a rigorous quadratic remainder.
  samples  F at the sub-box's 9 x 9 grid (corners included) from the node evaluator V.evaluate (the v7 / v7B field),
           point k; resumable jsonl; SLICE=i/n takes every n-th point from i (two processes on two cores).
  judge    step 0''s registered pass bar on the drive record and the samples.

The sub-box: centre kc0 = the exact binary midpoint of arb(R1_KC); half-side hs = upper(R/5), R = upper(half (4 + 1/4)/2)
(the rho = 4 ellipse box's half-side, as in v2's kbox; KSUB = 5 cuts it into 25 sub-boxes of half-side R/5).

The initial doubleton (addendum C2-1): for each complex start value f in (s, c0, c0'), at the base point zb (the loops'
common first vertex, an exact double):
  f(k) = f(kc0) + f'(kc0) dk + rem,   |rem| <= sup_K |f''| |dk|^2 / 2 <= sup_K |f''| hs^2       (|dk|^2 <= 2 hs^2),
  sup |c0''_kk|, |c0'_kk|: the module's d2kc0 on (zb, K) (v2's radial integral for P1, addendum 5's d2kc0_B for P2);
  s'' = -(dB/dk)^2 / (4 s^3) (B is linear in k), enclosed with |s|^3 >= |B(zb, K)|^(3/2).
Real components: Re f = Re f0 + Re f' u - Im f' v,  Im f = Im f0 + Im f' u + Re f' v.  x = exact midpoints, C = exact
midpoints of f', and r = ball radii + |rad f'| (|u| + |v|) + rem.  Y0 = I; k = kc0 + (u, v) exactly (C = identity there).
    BOX=P2 <env> .venv313/bin/python -I -u scripts/_nve_c2_capd.py drive|samples|judge
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BOX = os.environ["BOX"]
if BOX == "P1":
    import _nve_route1_segment_v7 as L      # noqa: E402
else:
    import _nve_route1_segment_v7B as L     # noqa: E402
import _nve_v7_c0 as V7                     # noqa: E402
from flint import acb, arb, ctx             # noqa: E402

ctx.prec = 256
V = L.V
A, E2 = V.A, V.E2
OUTD = os.path.join(os.path.dirname(HERE), "data", "nve", "route1_check", "c2")
DRIVER = os.path.join(HERE, "c2_capd", "build", "c2_driver" + os.environ.get("C2_VARIANT", ""))
ORDER = int(os.environ.get("C2_ORDER", "20"))
TOL = os.environ.get("C2_TOL", "1e-30")
KDIV = int(os.environ.get("C2_KDIV", "5"))     # addendum C2-3: sub-box half-side R/KDIV, KDIV in {5, 10, 20}
assert KDIV in (5, 10, 20), "C2_KDIV must be 5, 10 or 20 (addendum C2-3)"
STAGE = os.environ.get("C2_STAGE", "step0p")     # C2-4 runs use step0pp (the samples stay step0p_*: reused)
PLANT = os.environ.get("C2_PLANT", "")            # C2-4 controls: K1 (wrong start sign), K2 (cut crossing), K3, K4
C24 = STAGE != "step0p"
TAG = f"{BOX}_k{KDIV}_o{ORDER}" + os.environ.get("C2_VARIANT", "") + ("" if TOL == "1e-30" else "_tol" + TOL) + \
    (f"_{PLANT}" if PLANT else "")

kc0 = acb(arb(L.S6.KC).mid())
R = (L.S6.HALF * (arb(4) + arb(1) / 4) / 2).upper()
hs = (R / KDIV).upper()
HSDIV = int(os.environ.get("C2_HSDIV", "1"))   # development only (smoke): shrink the sub-box; step 0' uses 1
if HSDIV != 1:
    assert os.environ.get("C2_SMOKE") == "1", "C2_HSDIV is a development switch for smoke runs only"
    hs = (hs / HSDIV).upper()
K = kc0 + hs * V.UNIT                        # the closed sub-box (a square of half-side hs)
REF = L.S6.REF
if BOX == "P1":
    LOOP0 = V.circle_vertices()
    LOOP1 = [complex(float(p[0]), float(p[1])) for p in REF["lasso"]]
else:
    LOOP0, LOOP1 = list(L.GAM), list(L.LAS)
SMOKE = os.environ.get("C2_SMOKE") == "1"     # development check only (not step 0'): short closed loops, compared
if SMOKE:                                      # with the Arb walk's monodromy at kc0
    LOOP0, LOOP1 = LOOP0[:3] + LOOP0[1::-1], LOOP1[:3] + LOOP1[1::-1]      # out and back: M = I exactly
    TAG += "_smoke" + (f"_hs{HSDIV}" if HSDIV != 1 else "")
if PLANT == "K2":                              # control (K2): a segment from the base point across B's cut and back
    import cmath
    assert BOX == "P2" and C24
    kk = complex(kc0.mid())
    c2_, c1_, cc_ = 90 - 21 * kk, -(60 - 18 * kk), 10 - kk
    a_ = float(A.mid())
    best = None
    for sg in (1, -1):                         # B(w) = -20: c2 w^2 + c1 w + (cc + 20) = 0
        w = (-c1_ + sg * cmath.sqrt(c1_ * c1_ - 4 * c2_ * (cc_ + 20))) / (2 * c2_)
        for zz in (a_ * cmath.sqrt(w), -a_ * cmath.sqrt(w)):
            if best is None or abs(zz - LOOP0[0]) < abs(best - LOOP0[0]):
                best = zz
    zfar = 2 * best - LOOP0[0]                 # the straight segment base -> zfar passes through best (B = -20) at tau 1/2
    LOOP0 = LOOP1 = [LOOP0[0], complex(float(zfar.real), float(zfar.imag)), LOOP0[0]]
    K2_POINT = best
assert LOOP0[0] == LOOP0[-1] == LOOP1[0] == LOOP1[-1], "the two loops must share their base point"
ZB = LOOP0[0]
assert ZB.imag == 0 and ZB.real > 0


def me(x):
    """exact 'mantissa exponent' of a point arb"""
    m, e = x.man_exp()
    return f"{int(m)} {int(e)}"


def up(x):
    return (x if isinstance(x, arb) else arb(x)).upper()


def from_me(m, e):
    if m == "nan":
        raise ValueError("non-finite value from the driver")
    return arb(int(m)) * arb(2) ** int(e)


def interval(lo, hi):
    """an arb ball containing the exact interval [lo, hi]"""
    assert lo <= hi
    return lo.union(hi)


# ------------------------------------------------------------------------------------------------ the initial set
def s_formula(z, k):
    """C2-4: the closed-form principal root at a point (acb): disc sqrt_p(B); circle w sqrt_p(I)"""
    w = z * z / (A * A)
    c2, c1, cc = 90 - 21 * k, -(60 - 18 * k), 10 - k
    if BOX == "P1":
        return w * (c2 + c1 / w + cc / (w * w)).sqrt()
    return (c2 * w * w + c1 * w + cc).sqrt()


def initial():
    c = V7.C0(V.SPIN, kc0, deriv=True)
    st = c.start(acb(ZB))
    zb = acb(ZB)
    dB = c.dB(zb)
    s0 = st["s"]
    ds = dB / (2 * s0)
    d2 = V.d2kc0(zb, K)
    if d2 is None:
        raise RuntimeError("d2kc0 refused at the base point over the sub-box")
    E0, E1 = d2[0].abs_upper(), d2[1].abs_upper()
    a2 = A * A
    w = zb * zb / a2
    Bk = (90 - 21 * K) * w * w - (60 - 18 * K) * w + (10 - K)       # B(zb, K): linear in k, an exact enclosure
    if Bk.contains(0):
        raise RuntimeError("B(zb, K) contains 0")
    babs = Bk.abs_lower()
    Es = (dB.abs_upper() ** 2 / (4 * babs * babs.sqrt())).upper()
    h2 = (hs * hs).upper()
    info = {}
    if C24:
        # (a3): the formula's branch at the start equals the field's carried branch (V1's s0), and not the other one
        sf = s_formula(zb, kc0)
        ref = -s0 if PLANT == "K1" else s0
        a3 = bool(sf.overlaps(ref)) and not bool(sf.overlaps(-ref))
        info.update(a3_formula=sf.str(12), a3_ref=ref.str(12), a3_ok=a3)
        if not a3:
            raise RuntimeError("(a3) the closed-form root does not match the field's branch at the start")
        vals = [(st["c0"], st["D0"], E0), (st["c0p"], st["D1"], E1)]
    else:
        vals = [(s0, ds, Es), (st["c0"], st["D0"], E0), (st["c0p"], st["D1"], E1)]
    x, C, r = [], [], []
    for f0, d, E in vals:
        rem = (E * h2).upper()
        cerr = ((d.real.rad() + d.imag.rad()) * hs).upper()
        for part, crow in ((f0.real, (d.real.mid(), -d.imag.mid())), (f0.imag, (d.imag.mid(), d.real.mid()))):
            x.append(part.mid())
            C.append(crow)
            r.append((part.rad() + cerr + rem).upper())
    for i in range(4):                                               # Y = I: (1, 0, 0, 1) as complex entries
        x += [arb(1) if i in (0, 3) else arb(0), arb(0)]
        C += [(arb(0), arb(0))] * 2
        r += [arb(0)] * 2
    x += [kc0.real.mid(), kc0.imag.mid()]
    C += [(arb(1), arb(0)), (arb(0), arb(1))]
    r += [arb(0), arb(0)]
    info.update(zb=[ZB.real, ZB.imag], s0=s0.str(12), c0=st["c0"].str(12), c0p=st["c0p"].str(12), E_s=float(Es),
                E0=float(E0), E1=float(E1), rem_max=float(max(Es, E0, E1) * h2), r_max=float(max(r)))
    return x, C, r, info


def write_input(path, x, C, r):
    pref = -(arb(8) / 5).sqrt() * A ** 3
    lines = ["prec 256", f"order {ORDER}", f"tol {TOL}"]
    if C24:
        Ic = acb((90 - 21 * kc0).real.mid(), (90 - 21 * kc0).imag.mid())   # the disc's exact centre (within 1e-76
        #                                                            of c2(kc0); the disc bound has a 0.55 margin)
        irad = arb("0.01") if PLANT == "K3" else arb(13) / 2         # (a2) radius 6.5 (erratum E1); K3 plants 0.01
        irad = irad.mid()
        lines += [f"sform {'circle' if BOX == 'P1' else 'disc'}", f"Ic {me(Ic.real)} {me(Ic.imag)}",
                  f"Irad {me(irad)}", f"plant_time {1 if PLANT == 'K4' else 0}"]
    for name, v in (("a", A), ("E2", E2), ("pref", pref)):
        lines.append(f"{name} {me(v.lower())} {me(v.upper())}")
    lines.append(f"R {me(hs)}")
    lines.append("x " + " ".join(me(v) for v in x))
    lines.append("C " + " ".join(f"{me(p)} {me(q)}" for p, q in C))
    lines.append("r " + " ".join(me(v) for v in r))
    lines.append("nloops 2")
    for lp in (LOOP0, LOOP1):
        lines.append(f"loop {len(lp)}")
        for z in lp:
            lines.append(f"{me(arb(z.real))} {me(arb(z.imag))}")
    open(path, "w").write("\n".join(lines) + "\n")


# ------------------------------------------------------------------------------------------------ affine arithmetic
class Af:
    """c + a u + b v + E, with u, v in [-hs, hs] real and |E| <= e (c, a, b acb balls; e a point arb upper bound)"""

    def __init__(self, c, a=None, b=None, e=None):
        self.c, self.a, self.b = c, a if a is not None else acb(0), b if b is not None else acb(0)
        self.e = e if e is not None else arb(0)

    def L(self):
        return ((self.a.abs_upper() + self.b.abs_upper()) * hs).upper()

    def __add__(self, o):
        return Af(self.c + o.c, self.a + o.a, self.b + o.b, (self.e + o.e).upper())

    def __sub__(self, o):
        return Af(self.c - o.c, self.a - o.a, self.b - o.b, (self.e + o.e).upper())

    def __mul__(self, o):
        L1, L2 = self.L(), o.L()
        c1, c2 = self.c.abs_upper(), o.c.abs_upper()
        e = L1 * L2 + c1 * o.e + c2 * self.e + self.e * (L2 + o.e) + o.e * L1
        return Af(self.c * o.c, self.c * o.a + o.c * self.a, self.c * o.b + o.c * self.b, e.upper())

    def neg(self):
        return Af(-self.c, -self.a, -self.b, self.e)

    def range(self):
        U = arb(0, hs)
        e = self.e
        return self.c + self.a * U + self.b * U + acb(arb(0, e), arb(0, e))


def mats(rows):
    """the two monodromy matrices as 2x2 of Af, and as plain hull boxes"""
    def ent(i):
        re, im = rows[i], rows[i + 1]
        c = acb(re["x"], im["x"])
        a = acb(re["ck0"], im["ck0"])
        b = acb(re["ck1"], im["ck1"])
        e = (acb(re["br"], im["br"])).abs_upper()
        return Af(c, a, b, e.upper()), acb(re["hull"], im["hull"])
    afs = [ent(i) for i in ((4, 6, 8, 10) if C24 else (6, 8, 10, 12))]
    A_ = [[afs[0][0], afs[1][0]], [afs[2][0], afs[3][0]]]
    H_ = [[afs[0][1], afs[1][1]], [afs[2][1], afs[3][1]]]
    return A_, H_


def mm(X, Y, add, mul):
    return [[add(mul(X[i][0], Y[0][j]), mul(X[i][1], Y[1][j])) for j in range(2)] for i in range(2)]


def adj(X, neg):
    return [[X[1][1], neg(X[0][1])], [neg(X[1][0]), X[0][0]]]     # = X^-1 (det X = 1, Abel: tr of [[0,1],[-q,0]] = 0)


def F_tr(M0, M1, add, mul, neg, two):
    Cm = mm(mm(M1, M0, add, mul), mm(adj(M1, neg), adj(M0, neg), add, mul), add, mul)
    return add(add(Cm[0][0], Cm[1][1]), neg(two)), add(M0[0][0], M0[1][1]), add(M1[0][0], M1[1][1])


# ------------------------------------------------------------------------------------------------ modes
def drive():
    os.makedirs(OUTD, exist_ok=True)
    t0 = time.time()
    try:
        x, C, r, info = initial()
    except RuntimeError as e:
        rec = dict(stage=STAGE, box=BOX, plant=PLANT, rc=2, refused=[f"REFUSED start: {e}"])
        print(f"{STAGE} {BOX}: REFUSED at the start: {e}", flush=True)
        json.dump(rec, open(os.path.join(OUTD, f"{STAGE}_{TAG}_drive.json"), "w"), indent=1)
        return
    t_init = time.time() - t0
    inp = os.path.join(OUTD, f"{STAGE}_{TAG}_input.txt")
    outp = os.path.join(OUTD, f"{STAGE}_{TAG}_capd.txt")
    logp = os.path.join(OUTD, f"{STAGE}_{TAG}_steps.log")
    write_input(inp, x, C, r)
    t1 = time.time()
    pr = subprocess.run([DRIVER, inp, outp, logp], capture_output=True, text=True)
    t_capd = time.time() - t1
    rec = dict(stage=STAGE, plant=PLANT, box=BOX, k_c=str(L.S6.KC), kc0=[kc0.real.str(20), kc0.imag.str(20)], hs=float(hs), R=float(R),
               order=ORDER, tol=TOL, init=info, t_init=round(t_init, 1), t_capd=round(t_capd, 1), rc=pr.returncode,
               stderr=pr.stderr[-2000:])
    txt = open(outp).read() if os.path.exists(outp) else ""
    if pr.returncode != 0:
        rec["refused"] = [ln for ln in txt.splitlines() if ln.startswith("REFUSED")] or ["driver exit " + str(pr.returncode)]
        print(f"step 0' {BOX}: driver REFUSED/failed: {rec['refused']} {pr.stderr[-300:]}", flush=True)
    else:
        loops, cur = [], None
        for ln in txt.splitlines():
            t = ln.split()
            if t[0] == "loop":
                cur = dict(steps=int(t[3]), dtmin=float(t[5]), dtmax=float(t[7]), rows=[])
                loops.append(cur)
            elif t[0] == "row":
                d = {}
                for j, key in enumerate(("x", "ck0", "ck1", "br", "hull")):
                    p = 3 + j * 5
                    d[key] = interval(from_me(t[p], t[p + 1]), from_me(t[p + 2], t[p + 3]))
                cur["rows"].append(d)
        assert len(loops) == 2 and all(len(lp["rows"]) == (14 if C24 else 16) for lp in loops)
        (A0, H0), (A1, H1) = mats(loops[0]["rows"]), mats(loops[1]["rows"])
        Fa, T0a, T1a = F_tr(A0, A1, lambda p, q: p + q, lambda p, q: p * q, lambda p: p.neg(), Af(acb(2)))
        Fh, T0h, T1h = F_tr(H0, H1, lambda p, q: p + q, lambda p, q: p * q, lambda p: -p, acb(2))
        Fr, T0r, T1r = Fa.range(), T0a.range(), T1a.range()
        rec.update(steps=[lp["steps"] for lp in loops], dt=[[lp["dtmin"], lp["dtmax"]] for lp in loops],
                   F=[Fr.real.str(15), Fr.imag.str(15)], T0=[T0r.real.str(15), T0r.imag.str(15)],
                   T1=[T1r.real.str(15), T1r.imag.str(15)], F_affine_e=float(Fa.e),
                   F_hull=[Fh.real.str(8), Fh.imag.str(8)],
                   M0_entry_rad=max(float(H0[i][j].rad()) for i in range(2) for j in range(2)),
                   M1_entry_rad=max(float(H1[i][j].rad()) for i in range(2) for j in range(2)))
        if SMOKE:
            lau = V.laurent(kc0)
            sing = [complex(float(p[0]), float(p[1])) for p in REF["points"]]
            ok = []
            for lp, H in ((LOOP0, H0), (LOOP1, H1)):
                Mw, _n = V.walk(lp, kc0, lau, sing)
                ok.append(all(H[i][j].contains(Mw[i][j]) for i in range(2) for j in range(2)))
                rec.setdefault("smoke_arb_M", []).append([[Mw[i][j].str(10) for j in range(2)] for i in range(2)])
            rec["smoke_contains"] = ok
            print(f"SMOKE: Arb walk M at kc0 inside the CAPD hull: {ok}", flush=True)
        print(f"step 0' {BOX}: CAPD {t_capd:.0f} s, steps {rec['steps']}; F over the sub-box {rec['F']} "
              f"(hull form {rec['F_hull']}); tr M0 {rec['T0']}; tr M1 {rec['T1']}", flush=True)
    json.dump(rec, open(os.path.join(OUTD, f"{STAGE}_{TAG}_drive.json"), "w"), indent=1)


def grid():
    pts = []
    for i in range(9):
        for j in range(9):
            pts.append((i, j, kc0.real.mid() - hs + 2 * hs * i / 8, kc0.imag.mid() - hs + 2 * hs * j / 8))
    return pts


def samples():
    sl = os.environ.get("SLICE", "0/1")
    i0, n = (int(v) for v in sl.split("/"))
    path = os.path.join(OUTD, f"step0p_{BOX}_k{KDIV}_samples.jsonl")
    done = set()
    if os.path.exists(path):
        for ln in open(path):
            d = json.loads(ln)
            done.add((d["i"], d["j"]))
    for idx, (i, j, kr, ki) in enumerate(grid()):
        if idx % n != i0 or (i, j) in done:
            continue
        kr, ki = arb(kr.mid()), arb(ki.mid())
        r = V.evaluate(kr, ki, REF)
        d = dict(i=i, j=j, k=[kr.str(25), ki.str(25)], F=r["F"], T0=r["T0"], T1=r["T1"], sec=r["sec"])
        with open(path, "a") as fh:
            fh.write(json.dumps(d) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        print(f"sample {i},{j}: F {r['F']} [{r['sec']} s]", flush=True)


def judge():
    """Addendum C2-3's bar, per box and size: finite, contains every sample, and sup|enclosure| <= 100 x the sampled
    max |.|, for F, tr M0 and tr M1; cost <= 2 h per segment (the (R/hs)^2 = KDIV^2 sub-boxes covering the square,
    on 2 cores). The ORIGINAL bar (width of F <= 100 x the sampled range of F) is reported alongside, not hidden."""
    rec = json.load(open(os.path.join(OUTD, f"{STAGE}_{TAG}_drive.json")))
    S = [json.loads(ln) for ln in open(os.path.join(OUTD, f"step0p_{BOX}_k{KDIV}_samples.jsonl"))]
    assert len({(d["i"], d["j"]) for d in S}) == 81, f"{len(S)} samples, 81 needed"
    out = dict(stage=STAGE, box=BOX, kdiv=KDIV, hs=rec["hs"], order=ORDER, tol=TOL, t_capd=rec["t_capd"],
               steps=rec.get("steps"))
    if C24:
        out["grade"] = "post-failure fix after step 0' FAILED (C2-4)"
    if rec["rc"] != 0:
        out.update(verdict="FAIL (the enclosure was refused or not finite)", refused=rec.get("refused"),
                   original_bar="FAIL (refused)")
    else:
        per = {}
        allok = True
        for q in ("F", "T0", "T1"):
            E = acb(arb(rec[q][0]), arb(rec[q][1]))
            Ss = [acb(arb(d[q][0]), arb(d[q][1])) for d in S]
            sup_enc = float(E.abs_upper())
            sup_samp = max(float(x.abs_upper()) for x in Ss)
            ok = bool(E.is_finite()) and all(E.contains(x) for x in Ss) and sup_enc <= 100 * sup_samp
            per[q] = dict(finite=bool(E.is_finite()), contains_all=all(E.contains(x) for x in Ss),
                          overlaps_all=all(E.overlaps(x) for x in Ss), sup_enclosure=sup_enc, sampled_max=sup_samp,
                          sup_ratio=sup_enc / sup_samp, ok=ok)
            allok = allok and ok
        F = acb(arb(rec["F"][0]), arb(rec["F"][1]))
        Fs = [acb(arb(d["F"][0]), arb(d["F"][1])) for d in S]
        res = [float(f.real.mid()) for f in Fs]
        ims = [float(f.imag.mid()) for f in Fs]
        srange = max(max(res) - min(res), max(ims) - min(ims))
        width = 2 * max(float(F.real.rad()), float(F.imag.rad()))
        orig_ok = bool(F.is_finite()) and all(F.contains(f) for f in Fs) and width <= 100 * srange
        proj_h = (rec["t_capd"] + rec["t_init"]) * KDIV * KDIV / 2 / 3600
        cost_ok = proj_h <= 2
        out.update(per=per, F_width=width, F_sampled_range=srange, F_width_over_range=width / srange,
                   original_bar="PASS" if orig_ok else "FAIL", projected_hours_per_segment=round(proj_h, 3),
                   cost_ok=cost_ok, sample_sec_mean=round(sum(d["sec"] for d in S) / len(S), 1),
                   verdict="PASS" if (allok and cost_ok) else "FAIL")
    print(f"step 0' {BOX} R/{KDIV} judge: {out}", flush=True)
    json.dump(out, open(os.path.join(OUTD, f"{STAGE}_{TAG}_judge.json"), "w"), indent=1)


if __name__ == "__main__":
    {"drive": drive, "samples": samples, "judge": judge}[sys.argv[1]]()
