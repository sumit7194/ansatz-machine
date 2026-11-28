#!/usr/bin/env python3
"""Route (i) segment certifier v7B: the REGION-B (half-plane) picture, on top of v7 (registration addenda 5, 6).
The loops are the floats entry's region-B lasso and its Gamma disc loop (walked where v6 walks the circle), both based at
bB; the c0 field is FieldB (disc-guarded); every c0'' series comes from the field's sqrt B branch (no c_K'' sqrt(1-k phi));
the k-uniform d2c0/dk2 bound is addendum 5's. Conditions: F != 0, tr Gamma != 0 (v6's "tr M0"), tr M1 not in [-2, 2].
    R1_KC=83/20 R1_HALF=1/20 R1_FLOATS=route1_floats_v7B_3_5.json R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel NVE_SPIN=3/5 \\
        R1_R0=1.35 .venv313/bin/python -I -u scripts/_nve_route1_segment_v7B.py prove|verdict
Sign of sqrt B (addendum 5, guard 2, made explicit): at the real base bB the field's branch is the principal value (B > 0
there; V1's start asserts it). Along the straight segment from bB to any z in the disc, if every tau-ball's B-ball (over
the whole k-box K) excludes 0 and lies in one open half-plane avoiding the cut (-inf, 0], the principal branch is
continuous on each ball, and consecutive balls share a point, so the principal branch IS the field's branch on the whole
segment, for every k in K (K contains k_c). Hence sigma = +1 wherever the guard is certified; anywhere it is not, the
bound returns None (a refused box).
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _nve_route1_segment_v7 as S7           # noqa: E402  (v6 + the circle-picture field; patched below for region B)
import _nve_v7_c0 as V7                        # noqa: E402
from flint import acb, acb_series, arb, ctx   # noqa: E402

S6, S5, V, S4 = S7.S6, S7.S5, S7.V, S7.S4
P = V.P
A = V.A
REF = S6.REF
assert REF.get("picture") == "B", "v7B needs a region-B floats entry (_nve_v7_floatsB.py)"
Z0 = arb(REF["Z0"])
BB = arb(REF["bB"])
GAM = [complex(float(p[0]), float(p[1])) for p in REF["gam"]]
LAS = [complex(float(p[0]), float(p[1])) for p in REF["lasso"]]
REACH = max(abs(v - complex(float(Z0.mid()))) for v in GAM + LAS)
RREQ_FIXED = REACH + 0.25         # addendum 9: the working-disc radius, fixed from the floats entry before any run
U = acb(arb(0, 1), arb(0, 1))
K8 = (arb(8) / 5).sqrt() * A
PREF = -(arb(8) / 5).sqrt() * A ** 3
SM = 96          # addendum 8: was 24; the E enclosures were 26-56% wide (reader item 4)

# ------------------------------------------------------------------------------------------------ hash and names
CODE_FILES = S7.CODE_FILES + ("_nve_route1_segment_v7B.py", "_nve_v7_floatsB.py", "_nve_v7_engine_gate_B.py")
ENV7B = S7.ENV7 + "; region B"
CODE = hashlib.sha256(b"".join(open(os.path.join(HERE, f), "rb").read() for f in CODE_FILES)
                      + ENV7B.encode()).hexdigest()[:16]
BASE = f"v7B{V.TAG}{S5.KTAG}{S6.MTAG}_{CODE}"
for mod in (S5, S6, S7):
    mod.CODE, mod.CODE_FILES, mod.BASE = CODE, CODE_FILES, BASE
S5.ENVSTR = ENV7B
S4.CKFILE = os.path.join(V.OUTD, f"route1_seg_{BASE}_dqck.jsonl")
S5.ROWS = os.path.join(V.OUTD, f"route1_seg_{BASE}_rows.jsonl")
S5.MJSON = os.path.join(V.OUTD, f"route1_seg_M_{BASE}.json")
S5.LOG5 = V.LOG = os.path.join(V.OUTD, f"route1_seg_{BASE}.out")
S6.NODEF = os.path.join(V.OUTD, f"route1_seg_nodes_{BASE}.jsonl")
S6.VJSON = os.path.join(V.OUTD, f"route1_seg_verdict_{BASE}.json")
say = S5.say


# ------------------------------------------------------------------------------------------------ singular points
def csqrt(x):
    """a square root of the ball x, choosing the representation that avoids Arb's cut (-inf, 0]: for Re x < 0
    certified, i sqrt(-x). (Callers use both signs, so either representation is valid; this one keeps the ball
    narrow, where x.sqrt() on a ball straddling the negative real axis returns both branches, centred at 0. Reader item 1.)"""
    if x.real < 0:
        return acb(0, 1) * (-x).sqrt()
    return x.sqrt()


def sing_balls(K):
    """the four branch points and +-ia as acb balls over the k-set K (None if not enclosable)"""
    den = 90 - 21 * K
    if den.contains(0):
        return None
    sq = csqrt(60 * K * (K - 4))
    out = [acb(0, A), acb(0, -A)]
    for w in (((30 - 9 * K) + sq) / den, ((30 - 9 * K) - sq) / den):
        if not w.is_finite():
            return None
        r = A * csqrt(w)
        out += [r, -r]
    return out


RREQ = RREQ_FIXED


def free_square(K, r, m=16, depth=4):
    """CERTIFIED: B(z^2/a^2, k) != 0 and z^2 + a^2 != 0 for every z in the square Z0 +- r(1 + i) and every k in K
    (addendum 9). The square is covered by m x m cells, each split in four (up to `depth` times) while not yet certified;
    K by its kbox sub-boxes (asserted to cover). B on a cell x K-box by the mean-value form in z (B is a polynomial in z;
    in k it is linear, so the K-ball enters exactly as a ball). False if any piece cannot be certified."""
    kc = acb(K.real.mid(), K.imag.mid())
    Rk = max(K.real.rad(), K.imag.rad())
    kboxes = [kc + d for d in V.kbox(kc, arb(Rk))[1]] if Rk > 0 else [K]
    r = arb(r)

    def cell_ok(cx, cy, hw, Kb, d):
        bx = acb(Z0) + acb(arb(cx, hw), arb(cy, hw))
        mz = acb(bx.real.mid(), bx.imag.mid())
        w = bx * bx / (A * A)
        wm = mz * mz / (A * A)
        Bm = (90 - 21 * Kb) * wm * wm - (60 - 18 * Kb) * wm + (10 - Kb)
        dB = (2 * bx / (A * A)) * (2 * (90 - 21 * Kb) * w - (60 - 18 * Kb))
        Bb = Bm + dB * (bx - mz)
        if not Bb.contains(0) and not (bx * bx + A * A).contains(0):
            return True
        if d == 0:
            return False
        h2 = (hw / 2).upper()
        return all(cell_ok(cx + sx * h2, cy + sy * h2, h2, Kb, d - 1) for sx in (-1, 1) for sy in (-1, 1))

    hw = (r / m).upper()
    for Kb in kboxes:
        for i in range(m):
            for j in range(m):
                cx = (-r + hw * (2 * i + 1)).mid()
                cy = (-r + hw * (2 * j + 1)).mid()
                if not cell_ok(arb(cx), arb(cy), hw, Kb, depth):
                    return False
    return True


def Rc_lower(K):
    """certified lower bound of the distance from Z0 to c0's singular points over K, using K's kbox sub-boxes"""
    kc = acb(K.real.mid(), K.imag.mid())
    Rk = max(K.real.rad(), K.imag.rad())
    boxes = [kc + d for d in V.kbox(kc, arb(Rk))[1]] if Rk > 0 else [K]
    best = None
    for Kb in boxes:
        pts = sing_balls(Kb)
        if pts is None:
            return None
        m = min((acb(Z0) - p).abs_lower() for p in pts)
        best = m if best is None or m < best else best
    return best


# ------------------------------------------------------------------------------------------------ the region-B field
class FieldB:
    def __init__(self, k):
        self.c = V7.C0(V.SPIN, k, deriv=True)
        if not free_square(self.c.k, RREQ):           # addendum 9: no c0 singular point in the working square
            raise RuntimeError("fieldB: the working square is not certified free of c0 singular points")
        self.Rd = arb(RREQ).lower()
        if not self.inside(acb(BB)):
            raise RuntimeError("fieldB: the base point bB is not certified inside the disc")
        self.cache = [self.c.start(BB)]

    def inside(self, z, extra=0.0):
        return bool((acb(z) - acb(Z0)).abs_upper() + arb(extra) < self.Rd)

    def at(self, z):
        if not self.inside(z):
            raise RuntimeError(f"fieldB: {complex(z.mid())} outside |z - Z0| < 0.9 R_c")
        zc = complex(z.mid())
        best = min(self.cache, key=lambda s: abs(complex(s["z"].mid()) - zc))
        if best["z"] == z and z.real.rad() == 0 and z.imag.rad() == 0:
            return best
        try:
            out = self.c.walk([best["z"], z], best)          # straight; the disc is convex
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
            return st["c0"], st["c0p"], st["D0"], st["D1"]
        try:
            M, MD, _MS = self.c.sup_box(zm, arb(r))
        except AssertionError as e:
            raise RuntimeError(f"fieldB: {e}")
        dz = Zb - zm
        d = dz.abs_upper()
        return (st["c0"] + st["c0p"] * dz + (M * d * d / 2).upper() * U, st["c0p"] + (M * d).upper() * U,
                st["D0"] + st["D1"] * dz + (MD * d * d / 2).upper() * U, st["D1"] + (MD * d).upper() * U)


class ViewB:
    def __init__(self, field, deriv):
        self.field, self.deriv = field, deriv

    def c0_at(self, z):
        if z.real.rad() == 0 and z.imag.rad() == 0:
            st = self.field.at(z)
            return (st["D0"], st["D1"]) if self.deriv else (st["c0"], st["c0p"])
        c0, c0p, D0, D1 = self.field.box(z)
        return (D0, D1) if self.deriv else (c0, c0p)


_FB = {}


def fieldB_for(k):
    k = k if isinstance(k, acb) else acb(k)
    assert float(k.real.rad()) <= 1e-30 and float(k.imag.rad()) <= 1e-30
    key = (k.real.mid().man_exp(), k.imag.mid().man_exp(), float(k.real.rad()), float(k.imag.rad()))
    if key not in _FB:
        _FB[key] = FieldB(k)
    return _FB[key]


V.laurent = lambda k, deriv=False: ViewB(fieldB_for(k), deriv)
V.c0_at = lambda z, lau: lau.c0_at(z)
V.circle_vertices = lambda n=96: list(GAM)

# ------------------------------------------------------------------------------------------------ native step / series
NAT = dict(step=0, series=0, d2k=0, d2k_none=0)


def step_native(zc, hvec, k, lau, rho):
    """v2's step with the c0'' series built from the field's sqrt B branch (as in _nve_v7_pb.py, which passed P-B)."""
    rb = arb(rho)
    Q = V.q_ball(zc + rb * V.UNIT, k, lau)
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
        if not (abs(sq.coeffs()[0] - st["s"]) < abs(sq.coeffs()[0] + st["s"])):
            sq = -sq
        if not (abs(sq.coeffs()[0] - st["s"]) < abs(sq.coeffs()[0] + st["s"])):
            raise AssertionError("native step: branch of sqrt B not certified against the field")
        c0pp = PREF * sq / ((z2 + A * A) ** 3)
        c0p = c0pp.integral() + st["c0p"]
        c0 = c0p.integral() + st["c0"]
        f0 = (z2 - 2 * t + A * A) / (z2 + A * A)
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
    NAT["step"] += 1
    return T, Y, zc + hb, hm


V.step = step_native                     # safe_step looks it up at call time (v5's F1 and v7's F1b wrappers bypassed)


def series_native(zm, kball, init):
    """v4's series_from_init with the c0'' and dc0''/dk series from sqrt B; the sign by the field at k_c, valid over the
    k-sub-box since B(zm; K) is certified off the cut (else None)."""
    try:
        fK = fieldB_for(acb(S6.KC))
        st = fK.at(zm)                                   # the field's carried branch at (zm, k_c)
        w = zm * zm / (A * A)
        Kh = acb(S6.KC) + (kball - acb(S6.KC)).abs_upper() * V.UNIT   # a square containing k_c and the k-sub-box (convex)
        BK = (90 - 21 * Kh) * w * w - (60 - 18 * Kh) * w + (10 - Kh)
        if BK.contains(0) or not (BK.real > 0 or BK.imag > 0 or BK.imag < 0):
            return None                                  # principal sqrt not certified continuous from k_c to kball
        s_c = fK.c.B(zm).sqrt()
        if abs(s_c - st["s"]) < abs(s_c + st["s"]):
            sig = 1
        elif abs(s_c + st["s"]) < abs(s_c - st["s"]):
            sig = -1
        else:
            return None
        cap0 = ctx.cap
        try:
            ctx.cap = S4.NORD + 4
            c0v, c0pv, D0v, D1v = init
            t = acb_series([zm, 1])
            z2 = t * t
            u2 = z2 / (A * A)
            Bs = (90 - 21 * kball) * u2 * u2 - (60 - 18 * kball) * u2 + (10 - kball)
            sq = Bs.sqrt() * sig
            D3 = (z2 + A * A) ** 3
            c0p = (PREF * sq / D3).integral() + c0pv
            c0 = c0p.integral() + c0v
            dB = -(21 * u2 * u2 - 18 * u2 + 1)
            D1 = (PREF * dB / (2 * sq) / D3).integral() + D1v
            D0 = D1.integral() + D0v
            f0 = (z2 - 2 * t + A * A) / (z2 + A * A)
            f0p = f0.derivative()
            G2 = f0 * f0 + c0 * c0
            dG2 = 2 * (f0 * f0p + c0 * c0p)
            G1 = V.E2 * G2 - f0
            dG1 = V.E2 * dG2 - f0p
            if G1.coeffs()[0].contains(0) or G2.coeffs()[0].contains(0):
                return None
            G12 = G1 * G2
            lam = dG1 / G1 - dG2 / G2
            X = 2 * f0 * c0 * D0 / G12
            dlam = 2 * (f0p * c0 * D0 + f0 * c0p * D0 + f0 * c0 * D1) / G12 - X * (dG1 / G1 + dG2 / G2)
            c = (lam * dlam * 3 / 8).coeffs()
        finally:
            ctx.cap = cap0
        c = (c + [acb(0)] * (S4.NORD + 1 - len(c)))[:S4.NORD + 1]
        NAT["series"] += 1
        return c if all(x.is_finite() for x in c) else None
    except (ValueError, ZeroDivisionError, RuntimeError):
        return None


S4.series_from_init = series_native


# ------------------------------------------------------------------------------------------------ addendum 5: d2 c0/dk2
SB = [arb(2 * j + 1) / (2 * SM) + arb(0, 1) / (2 * SM) for j in range(SM)]   # balls covering [0, 1]
for _j in range(SM):
    assert SB[_j].contains(arb(_j) / SM) and SB[_j].contains(arb(_j + 1) / SM)
_RD = {}


def _kkey(K):
    """exact key of a k-set: midpoints (mantissa, exponent) and radii (exact floats of the mag radii). Reader item 3."""
    return (K.real.mid().man_exp(), K.imag.mid().man_exp(), float(K.real.rad()), float(K.imag.rad()))


def Rd_for(K):
    key = _kkey(K)
    if key not in _RD:
        _RD[key] = arb(RREQ).lower() if free_square(K, RREQ) else None      # addendum 9
    return _RD[key]


_BASE2 = {}


def base2(K):
    """(d2 c0'/dk2 (bB), d2 c0/dk2 (bB)) enclosed over K; None if Re P > 0 is not certified on some s-ball x K."""
    key = _kkey(K)
    if key in _BASE2:
        return _BASE2[key]
    if not ((K.real - arb(30) / 7) < 0):
        _BASE2[key] = None
        return None
    lim = 1 / BB
    i1, i0 = acb(0), acb(0)
    for S in SB:
        s = S * lim
        a2s2 = A * A * s * s
        Pv = (90 - 21 * K) - (60 - 18 * K) * a2s2 + (10 - K) * a2s2 * a2s2
        if not (Pv.real > 0):
            _BASE2[key] = None
            return None
        dP = -21 + 18 * a2s2 - a2s2 * a2s2
        d2 = -(dP * dP) / (4 * Pv * Pv.sqrt())
        den = (1 + a2s2) ** 3
        i1 += s * s * d2 / den
        i0 += (s - BB * s * s) * d2 / den
    w = lim / SM
    _BASE2[key] = (K8 * i1 * w, -K8 * i0 * w)
    return _BASE2[key]


LAST = dict(refused=None)


def d2kc0_B(Z, K):
    """(E0, E1) = (d2 c0/dk2, d2 c0'/dk2) enclosed on Z x K by addendum 5's representation; None if any guard fails.
    LAST["refused"] records which guard refused (for the controls): "base", "disc" or "B-cut"."""
    NAT["d2k"] += 1
    LAST["refused"] = None
    Rd = Rd_for(K)
    b = base2(K)
    if Rd is None or b is None:
        NAT["d2k_none"] += 1
        LAST["refused"] = "base"
        return None
    e1b, e0b = b
    dz = Z - BB
    j1, j0 = acb(0), acb(0)
    for T in SB:
        t = BB + T * dz
        if not ((t - acb(Z0)).abs_upper() < Rd):
            NAT["d2k_none"] += 1
            LAST["refused"] = "disc"
            return None
        w = t * t / (A * A)
        Bv = (90 - 21 * K) * w * w - (60 - 18 * K) * w + (10 - K)
        if Bv.contains(0) or not (Bv.real > 0 or Bv.imag > 0 or Bv.imag < 0):
            NAT["d2k_none"] += 1
            LAST["refused"] = "B-cut"
            return None
        dB = -(21 * w * w - 18 * w + 1)
        g = PREF * (-(dB * dB) / (4 * Bv * Bv.sqrt())) / ((t * t + A * A) ** 3)     # sigma = +1 (see the docstring)
        j1 += g
        j0 += (1 - T) * g
    j1, j0 = j1 / SM, j0 / SM
    return e0b + e1b * dz + dz * dz * j0, e1b + dz * j1


V.d2kc0 = d2kc0_B


# ------------------------------------------------------------------------------------------------ precondition (region B)
PLANT = dict(substituted=0)


def precondition_B(K):
    out = dict(k_box=[str(K.real), str(K.imag)], picture="half-plane (v7B)")
    if abs(float(K.real.mid()) - 4.2) < 1e-12 and abs(float(K.imag.mid())) < 1e-12 and \
            abs(float(K.real.rad()) - 0.01) < 1e-6:
        # v6's planted control is hard-coded at 4.2 +- 0.01, a VALID region-B box. Substituted, openly, by a box that
        # crosses 30/7, which region B must refuse.
        PLANT["substituted"] += 1
        K = acb(arb(30) / 7 + arb("0.02")) + arb("0.01") * V.UNIT
        out["planted_substituted"] = "30/7 + 0.02 +- 0.01"
    if not ((K.real - arb(30) / 7) < 0):
        out.update(ok=False, why="Re k reaches 30/7 on K (the k-branch point; P(0, k) = 90 - 21k)")
        return out
    # addendum 9: the working square Z0 +- RREQ is certified free of c0's singular points for every k in K, and the
    # loops (plus 0.1 for step boxes) lie in the disc of radius RREQ. (RREQ is fixed: reach + 0.25.)
    if not REACH + 0.1 < RREQ:
        out.update(ok=False, why=f"loops' reach {REACH:.4f} + 0.1 >= the working radius {RREQ:.4f}")
        return out
    free = free_square(K, RREQ)
    out.update(ok=bool(free), Rd=RREQ, reach=REACH)
    if not free:
        out["why"] = f"the working square Z0 +- {RREQ:.4f} is not certified free of c0 singular points over K"
    return out


V.precondition = precondition_B


# ------------------------------------------------------------------------------------------------ self-test (region B points)
def selftest_B(kc, lau_c, laud_c):
    """v2's self-test at five points of the Gamma loop (inside the disc): dc0/dk and d2c0/dk2 (addendum 5) against
    central differences in k, and |FD dq/dk| <= sup |dq/dk| (addendum 5's positive check)."""
    h = arb(1) / 10 ** 6
    lp, lm = V.laurent(acb(kc + h)), V.laurent(acb(kc - h))
    ldp, ldm = V.laurent(acb(kc + h), True), V.laurent(acb(kc - h), True)
    ok = True
    pts = [GAM[j] for j in (1, len(GAM) // 4, len(GAM) // 2, 3 * len(GAM) // 4, len(GAM) - 2)]
    for zz in pts:
        Z = acb(zz.real, zz.imag)
        D0, D1 = V.c0_at(Z, laud_c)
        cp, cm = V.c0_at(Z, lp), V.c0_at(Z, lm)
        fd0, fd1 = (cp[0] - cm[0]) / (2 * h), (cp[1] - cm[1]) / (2 * h)
        fdq = (V.q_ball(Z, acb(kc + h), lp) - V.q_ball(Z, acb(kc - h), lm)) / (2 * h)
        sup = V.dq_sup(Z, acb(kc), None, lau_c, laud_c)[0]
        e0 = float((D0 - fd0).abs_upper())
        e1 = float((D1 - fd1).abs_upper())
        rq = float(fdq.abs_lower()) / float(sup)
        e2 = V.d2kc0(Z, acb(kc))                    # looked up at call time, so a control can replace it
        dp, dm = V.c0_at(Z, ldp), V.c0_at(Z, ldm)
        f2, f2p = (dp[0] - dm[0]) / (2 * h), (dp[1] - dm[1]) / (2 * h)
        o2 = e2 is not None and bool(e2[0].overlaps(f2 + arb("1e-8") * V.UNIT)) and \
            bool(e2[1].overlaps(f2p + arb("1e-8") * V.UNIT))          # E0 AND E1 (reader item 4)
        good = e0 < 1e-8 and e1 < 1e-8 and 0.5 < rq <= 1.0000001 and o2
        ok &= good
        say(f"    z = {zz}: |D0 - FD| <= {e0:.1e}, |D1 - FD| <= {e1:.1e}; |FD dq/dk| / sup = {rq:.6f}; "
            f"second derivatives E0, E1 (addendum 5) overlap their FD: {o2}  -> {'ok' if good else 'FAIL'}")
    return ok


V.selftest = selftest_B


# ------------------------------------------------------------------------------------------------ entry
def prove():
    say(f"== v7B prove (region B) == {V.SEG}; Z0 {REF['Z0']}, bB {REF['bB'][:12]}, Gamma {len(GAM)} / lasso {len(LAS)} "
        f"vertices, reach {REACH:.4f}; code {CODE}")
    S6.prove()
    say(f"  native: {NAT}; region-B fields built: {len(_FB)}")


def verdict():
    say(f"== v7B verdict (region B) == {V.SEG}; code {CODE}")
    try:
        S6.verdict()
    finally:
        say(f"  native: {NAT}; region-B fields built: {len(_FB)}; planted precondition substituted {PLANT['substituted']}x")


if __name__ == "__main__":
    dict(prove=prove, verdict=verdict)[sys.argv[1]]()
