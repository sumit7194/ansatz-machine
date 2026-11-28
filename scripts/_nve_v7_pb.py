#!/usr/bin/env python3
"""v7 stage P-B (registration V7_REGISTRATION.md): the region-B (half-plane) loops in Arb, with the V1 c0, at single
nodes. PASS: at spin 3/5, the Arb enclosures of F = tr[M1, Gamma] - 2, tr M1 and tr Gamma at k = 4.2 and k = 30/7 - 1e-6
have radius <= 1e-3 |value|, and the 50-digit engine's values lie inside them (as 1e-40 balls, addendum 2's rule).
    NVE_SPIN=3/5 R1_R0=1.35 .venv/bin/python    -I scripts/_nve_v7_pb.py engine   # mpmath: geometry + engine values
    NVE_SPIN=3/5 R1_R0=1.35 .venv313/bin/python -I scripts/_nve_v7_pb.py arb      # Arb: field B + v7-native step
Geometry (fixed by the registered rule of _nve_spin_scan.geo, region B): r+, p+- tracked from Kerr's points along k;
series centre Z0 = 2 at spin 3/5 (as in section 162 and the closure check); base bB = max(Re r+(endpoint) - 0.3, a + 0.08);
loops = _nve_spin_scan.HalfB.loops (capsule lasso around [r+, p+], Gamma disc around r+, p+, p-), both based at bB.
Arb side:
  - FieldB: c0 (V1's C0) started at the real base point bB (s = 1/t quadrature along the real axis to +inf), and
    continued ONLY inside the disc |z - Z0| <= 0.9 R_c, R_c = a certified lower bound of the distance from Z0 to c0's
    singular points (Arb roots of B and +-ia). The disc is simply connected and free of them, so c0 is single-valued
    there (CLOSURE_STOPC_RESULT.md); any query outside it is refused (RuntimeError = a refused box).
  - v7-native step: v2's step with the c0'' series built from the field's carried branch of sqrt B (no use of
    c_K'' sqrt(1 - k phi), whose principal branch need not be the right one in the half-plane).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SPIN = os.environ.get("NVE_SPIN", "3/5")
TAG = SPIN.replace("/", "_")
OUTD = os.path.join(os.path.dirname(HERE), "data", "nve", "route1_check", "v7")
os.makedirs(OUTD, exist_ok=True)
GJSON = os.path.join(OUTD, f"pb_engine_{TAG}.json")
TARGETS = [("21/5", "4.2"), ("30/7-1e-6", "30/7 - 1e-6")]


# ================================================================================================ engine mode
def run_engine():
    import mpmath as mp
    import _nve_spin_scan as SS
    import _nve_lower_kc as KC
    mp.mp.dps = 50
    A = SS.A
    seeds = SS.kerr_points()
    st = [seeds[0], seeds[2], seeds[3]]
    Z0 = mp.mpf(2)
    B_X1 = SS.B_X1
    RB0 = SS.HalfB(Z0, mp.mpf(0), 0, mp.mpf(99))
    for q in range(1, 43):                                   # to the endpoint, as the registered geo rule
        prb = RB0.problem(B_X1 * q / 42)
        st = [(KC.newton(prb, x, w), w) for x, w in st]
    endpts = list(st)
    cen0 = sum(x for x, _ in endpts) / 3
    bB = max(mp.re(endpts[0][0]) - mp.mpf("0.3"), A + mp.mpf("0.08"))
    RB = SS.HalfB(Z0, bB, cen0, mp.mpf(99))
    out = dict(spin=SPIN, Z0=str(Z0), bB=str(bB), cen0=[str(mp.re(cen0)), str(mp.im(cen0))], nodes={},
               meta=dict(python=sys.version.split()[0], mpmath=mp.__version__, dps=mp.mp.dps, NC_B=SS.NC_B,
                         RATIO_B=str(SS.RATIO_B)))
    for key, _lab in TARGETS:
        kt = (mp.mpf(21) / 5) if key == "21/5" else (mp.mpf(30) / 7 - mp.mpf(10) ** -6)
        s2 = list(endpts)
        for q in range(1, 21):                               # back from the endpoint to the target
            prb = RB.problem(B_X1 + (kt - B_X1) * q / 20)
            s2 = [(KC.newton(prb, x, w), w) for x, w in s2]
        prb = RB.problem(kt)
        pos = [KC.newton(prb, x, w) for x, w in s2]
        lasso, gam, g = RB.loops(prb, pos)
        r = RB.evaluate(prb, pos, lasso, gam)
        cs = lambda x: [str(mp.re(x)), str(mp.im(x))]
        out["nodes"][key] = dict(
            pos=[cs(p) for p in pos], sing=[cs(s) for s in prb.eng.sing], Rc=str(prb.eng.Rc), guards=g,
            lasso=[[float(mp.re(p)), float(mp.im(p))] for p in lasso],
            gam=[[float(mp.re(p)), float(mp.im(p))] for p in gam],
            F=cs(r["F"]), T1=cs(r["T1"]), TG=cs(r["TG"]), T1G=cs(r["T1G"]))
        print(f"engine k = {key}: guards ok {g['ok']}; F {mp.nstr(r['F'], 12)}, T1 {mp.nstr(r['T1'], 12)}, "
              f"TG {mp.nstr(r['TG'], 12)}; Rc {mp.nstr(prb.eng.Rc, 6)}", flush=True)
    json.dump(out, open(GJSON, "w"), indent=1, default=str)
    print(f"== engine done -> {GJSON}", flush=True)


# ================================================================================================ arb mode
def run_arb():
    import time
    import flint
    from flint import acb, acb_series, arb, ctx
    import _nve_route1_segment_v2 as V
    import _nve_v7_c0 as V7
    import _nve_route1_proto as P
    G = json.load(open(GJSON))
    a = V.A
    Z0 = arb(G["Z0"])
    U = acb(arb(0, 1), arb(0, 1))

    class FieldB:
        def __init__(self, k, zs):
            self.c = V7.C0(SPIN, k, deriv=True)
            K = self.c.k
            den = 90 - 21 * K
            sq = (60 * K * (K - 4)).sqrt()
            ws = [((30 - 9 * K) + sq) / den, ((30 - 9 * K) - sq) / den]
            pts = []
            for w in ws:
                r = a * w.sqrt()
                pts += [r, -r]
            pts += [acb(0, a), acb(0, -a)]
            self.Rc = min((acb(Z0) - p).abs_lower() for p in pts)      # certified lower bound
            self.Rd = (self.Rc * arb("0.9")).lower()
            self.zs = acb(zs)
            if not ((self.zs - acb(Z0)).abs_upper() < self.Rd):
                raise RuntimeError("fieldB: base point outside the disc")
            self.cache = [self.c.start(arb(zs))]

        def inside(self, z, extra=0.0):
            return bool((acb(z) - acb(Z0)).abs_upper() + arb(extra) < self.Rd)

        def at(self, z):
            if not self.inside(z):
                raise RuntimeError(f"fieldB: {z} outside the disc |z - Z0| < 0.9 R_c")
            zc = complex(z.mid())
            best = min(self.cache, key=lambda s: abs(complex(s["z"].mid()) - zc))
            if best["z"] == z and z.real.rad() == 0 and z.imag.rad() == 0:
                return best
            try:
                out = self.c.walk([best["z"], z], best)     # straight segment, inside the convex disc
            except AssertionError as e:
                raise RuntimeError(f"fieldB: {e}")
            self.cache.append(out[-1])
            return out[-1]

        def box(self, Zb):
            zm = acb(Zb.real.mid(), Zb.imag.mid())
            r = max(float(Zb.real.rad()), float(Zb.imag.rad())) * 1.0000001
            if not self.inside(zm, extra=r * 1.42):
                raise RuntimeError("fieldB: box leaves the disc")
            st = self.at(zm)
            if r == 0:
                return st["c0"], st["c0p"]
            try:
                M, _MD, _MS = self.c.sup_box(zm, arb(r))
            except AssertionError as e:
                raise RuntimeError(f"fieldB: {e}")
            dz = Zb - zm
            d = dz.abs_upper()
            return st["c0"] + st["c0p"] * dz + (M * d * d / 2).upper() * U, st["c0p"] + (M * d).upper() * U

    class ViewB:
        def __init__(self, f):
            self.field = f

        def c0_at(self, z):
            if z.real.rad() == 0 and z.imag.rad() == 0:
                st = self.field.at(z)
                return st["c0"], st["c0p"]
            return self.field.box(z)

    V.c0_at = lambda z, lau: lau.c0_at(z)
    NB = dict(native=0)
    _q_ball = V.q_ball

    def step_native(zc, hvec, k, lau, rho):
        """v2's step with the c0'' series from the field's carried branch of sqrt B."""
        rb = arb(rho)
        Q = _q_ball(zc + rb * V.UNIT, k, lau)
        if Q is None:
            return None
        if not Q.abs_upper() * rb * rb < arb(2 * V.NT * (V.NT + 1) * 9) / 10:
            return None
        fld = lau.field
        st = fld.at(zc)
        cap0 = ctx.cap
        try:
            ctx.cap = V.NT + 3
            t = acb_series([zc, 1])
            z2 = t * t
            sq = fld.c.B(t).sqrt()
            c0s = sq.coeffs()[0]
            if not (abs(c0s - st["s"]) < abs(c0s + st["s"])):
                sq = -sq
            if not (abs(sq.coeffs()[0] - st["s"]) < abs(sq.coeffs()[0] + st["s"])):
                raise AssertionError("native step: branch of sqrt B not certified against the field")
            c0pp = fld.c.pref * sq / ((z2 + a * a) ** 3)
            c0p = c0pp.integral() + st["c0p"]
            c0 = c0p.integral() + st["c0"]
            f0 = (z2 - 2 * t + a * a) / (z2 + a * a)
            f0p = f0.derivative()
            G2 = f0 * f0 + c0 * c0
            dG2 = 2 * (f0 * f0p + c0 * c0p)
            G1 = V.E2 * G2 - f0
            dG1 = V.E2 * dG2 - f0p
            lam = dG1 / G1 - dG2 / G2
            qc = (lam * lam * 3 / 16).coeffs()
        finally:
            ctx.cap = cap0
        NT = V.NT
        if len(qc) < NT - 1:
            qc = qc + [acb(0)] * (NT - 1 - len(qc))
        mu = 2 / rb
        hm = hvec.abs_upper()
        x = (mu * hm).upper()
        assert x < arb(51) / 100
        hb = hvec / 2 + (hm / 2) * V.UNIT
        cols, Y = [], []
        for v0, v1 in ((acb(1), acb(0)), (acb(0), acb(1))):
            v = [v0, v1]
            for j in range(NT - 1):
                s = acb(0)
                for i in range(j + 1):
                    s += qc[i] * v[j - i]
                v.append(-s / ((j + 1) * (j + 2)))
            Kc = V.amax((v[j].abs_upper() / mu ** j).upper() for j in range(NT + 1))
            tail = (Kc * x ** (NT + 1) / (1 - x)).upper()
            dtail = (Kc * mu * (NT + 1) * x ** NT / ((1 - x) * (1 - x))).upper()
            val = P.horner(v, hvec) + tail * V.UNIT
            der = P.horner([v[j] * j for j in range(1, NT + 1)], hvec) + dtail * V.UNIT
            cols.append((val, der))
            Y.append(P.horner(v, hb) + tail * V.UNIT)
        T = [[cols[0][0], cols[1][0]], [cols[0][1], cols[1][1]]]
        if not all(e.is_finite() for r_ in T for e in r_) or not all(y.is_finite() for y in Y):
            return None
        NB["native"] += 1
        return T, Y, zc + hb, hm

    V.step = step_native
    BAR = arb("1e-3")
    ok_all = True
    log = []

    def say(s):
        print(s, flush=True)
        log.append(s)

    say(f"== v7 P-B (arb) == spin {SPIN}; Z0 {G['Z0']}, bB {G['bB']}; python {sys.version.split()[0]}, python-flint "
        f"{flint.__version__}, FLINT {getattr(flint, '__FLINT_VERSION__', '?')}; engine {G['meta']}")
    for key, lab in TARGETS:
        t0 = time.time()
        nd = G["nodes"][key]
        k = acb(arb(21) / 5) if key == "21/5" else acb(arb(30) / 7 - arb(10) ** -6)
        fld = FieldB(k, arb(G["bB"]))
        lau = ViewB(fld)
        sing = [complex(float(p[0]), float(p[1])) for p in nd["pos"]]
        lasso = [complex(p[0], p[1]) for p in nd["lasso"]]
        gam = [complex(p[0], p[1]) for p in nd["gam"]]
        assert lasso[0] == lasso[-1] and gam[0] == gam[-1] and lasso[0] == gam[0]
        M1, n1 = V.walk(lasso, k, lau, sing)
        MG, nG = V.walk(gam, k, lau, sing)
        Cm = P.mmul(P.mmul(M1, MG), P.mmul(P.minv(M1), P.minv(MG)))
        vals = dict(F=Cm[0][0] + Cm[1][1] - 2, T1=M1[0][0] + M1[1][1], TG=MG[0][0] + MG[1][1])
        good = True
        for nm, v in vals.items():
            e = acb(arb(nd[nm][0]), arb(nd[nm][1]))
            rad = max(float(v.real.rad()), float(v.imag.rad()))
            rel_ok = bool(arb(rad) <= BAR * v.abs_lower())
            eng_ok = bool((v - e).abs_upper() <= 2 * arb(rad) + arb("1e-40"))
            good &= rel_ok and eng_ok
            say(f"  k = {lab}: {nm} = {v.str(12)}; radius {rad:.2e} (<= 1e-3 |value|: {rel_ok}); engine inside: {eng_ok}")
        ok_all &= good
        say(f"  k = {lab}: steps lasso {n1}, Gamma {nG}; field R_c >= {float(fld.Rc):.4f}; "
            f"{'PASS' if good else 'NOT PASS'}   [{time.time() - t0:.0f} s]")
    say(f"VERDICT P-B spin {SPIN}: {'PASS' if ok_all else 'NOT PASS'}; native steps {NB['native']}")
    json.dump(dict(log=log, verdict="PASS" if ok_all else "NOT PASS"), open(os.path.join(OUTD, f"pb_arb_{TAG}.json"), "w"),
              indent=1)


if __name__ == "__main__":
    {"engine": run_engine, "arb": run_arb}[sys.argv[1]]()
