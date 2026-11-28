#!/usr/bin/env python3
"""Route (i) segment certifier v7 = v6 with c0 taken from the V1-validated evaluator instead of the Laurent series
(registration V7_REGISTRATION.md, stage V2). Circle picture only (region A loops); region B is stage P-B.

What changes (everything else is v6, byte-identical, imported):
  - V.laurent(k[, deriv]) returns a View of a c0 FIELD (_nve_v7_field.Field) at that k: c0, c0', d c0/dk, d c0'/dk
    carried by C0 (s = 1/t start quadrature at z_s = R0, Taylor propagation with a Cauchy remainder, continuity-asserted
    branch of sqrt B), and box queries by a certified sup |c0''| on a square;
  - V.c0_at(z, view) answers from that field;
  - V.precondition(K): the CIRCLE-picture condition. For every k in K, every c0 singular point (the four sqrt B branch
    points and +-ia) has |z| <= R0 - 0.1, so the circle encloses all of them (it closes; CLOSURE_STOPC_RESULT.md) and
    the walk stays where c0 is single-valued;
  - F1b (new gate, fail closed): at every Taylor-step start and every dq-series centre, the principal-branch formula
    for c0'' that v2/v4 use must equal the field's carried branch (certified, not just overlapping);
  - the code hash covers v6's files plus the three v7 files, so no v6 checkpoint or node record is reused (T4').
The second k-derivative d2kc0 (v2's radial integral, already Laurent-free) is unchanged.
    R1_KC=21/20 R1_HALF=1/20 R1_FLOATS=... R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel NVE_SPIN=3/5 R1_R0=1.35 \\
        .venv313/bin/python -I -u scripts/_nve_route1_segment_v7.py prove|verdict
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _nve_route1_segment_v6 as S6           # noqa: E402  (v6's import-time setup; runs nothing)
import _nve_v7_field as FLD                    # noqa: E402
from flint import acb, arb                     # noqa: E402

S5, V, S4 = S6.S5, S6.V, S6.S4
A = V.A

# ------------------------------------------------------------------------------------------------ hash and file names
CODE_FILES = S6.CODE_FILES + ("_nve_v7_c0.py", "_nve_v7_field.py", "_nve_route1_segment_v7.py")
ENV7 = S6.ENV6 + "; c0 v7 field"
CODE = hashlib.sha256(b"".join(open(os.path.join(HERE, f), "rb").read() for f in CODE_FILES)
                      + ENV7.encode()).hexdigest()[:16]
BASE = f"v7{V.TAG}{S5.KTAG}{S6.MTAG}_{CODE}"
S5.CODE, S5.CODE_FILES, S5.BASE, S5.ENVSTR = CODE, CODE_FILES, BASE, ENV7
S6.CODE, S6.CODE_FILES, S6.BASE = CODE, CODE_FILES, BASE
S4.CKFILE = os.path.join(V.OUTD, f"route1_seg_{BASE}_dqck.jsonl")
S5.ROWS = os.path.join(V.OUTD, f"route1_seg_{BASE}_rows.jsonl")
S5.MJSON = os.path.join(V.OUTD, f"route1_seg_M_{BASE}.json")
S5.LOG5 = V.LOG = os.path.join(V.OUTD, f"route1_seg_{BASE}.out")
S6.NODEF = os.path.join(V.OUTD, f"route1_seg_nodes_{BASE}.jsonl")
S6.VJSON = os.path.join(V.OUTD, f"route1_seg_verdict_{BASE}.json")

# ------------------------------------------------------------------------------------------------ the c0 field
_FIELDS = {}


def field_for(k):
    k = k if isinstance(k, acb) else acb(k)
    assert float(k.real.rad()) <= 1e-30 and float(k.imag.rad()) <= 1e-30, "v7 fields are built at point k only"
    key = (k.real.mid().str(60), k.imag.mid().str(60))
    if key not in _FIELDS:
        _FIELDS[key] = FLD.Field(V.SPIN, k, V.R0S)
    return _FIELDS[key]


def laurent7(k, deriv=False):
    return FLD.View(field_for(k), deriv)


def c0_at7(z, lau):
    return lau.c0_at(z)


def precondition7(K):
    """circle picture: every c0 singular point has |z| <= R0 - 0.1 for every k in K (w = z^2/a^2)."""
    R0 = arb(V.R0S)
    limw = ((R0 - arb("0.1")) / A) ** 2
    out = dict(k_box=[str(K.real), str(K.imag)], lim=float(limw.lower()), picture="circle (v7)")
    den = 90 - 21 * K
    if den.contains(0):
        out.update(ok=False, why="90 - 21 k contains 0: a branch point is at infinity")
        return out
    sq = (60 * K * (K - 4)).sqrt()
    roots = [((30 - 9 * K) + sq) / den, ((30 - 9 * K) - sq) / den]
    if not all(r.is_finite() for r in roots):
        out.update(ok=False, why="root enclosure not finite")
        return out
    mx = max(r.abs_upper() for r in roots)
    ok = bool(mx < limw) and bool(arb(1) < limw)          # the poles +-ia have |w| = 1
    out.update(max_root_abs_w=float(mx), ok=ok)
    if not ok:
        out["why"] = f"a c0 singular point has |w| up to {float(mx):.4f} >= {float(limw.lower()):.4f}: outside R0 - 0.1"
    return out


V.laurent, V.c0_at, V.precondition = laurent7, c0_at7, precondition7

# ------------------------------------------------------------------------------------------------ F1b
F1B = dict(step=0, series=0)


def _same_branch(z, k, fld):
    """the principal-branch formula c_K'' sqrt(1 - k phi) at z equals the field's c0'' (certified)."""
    st = fld.at(z)
    u2 = z * z / (A * A)
    cK2 = (3 * u2 - 1) * (-4) / ((u2 + 1) * (u2 + 1) * (u2 + 1) * (A * A * A))
    phi = (21 * u2 * u2 - 18 * u2 + 1) / (10 * (3 * u2 - 1) * (3 * u2 - 1))
    val = cK2 * (1 - k * phi).sqrt()
    mine = fld.c.c0pp(z, st["s"])
    assert (val - mine).abs_upper() < (val + mine).abs_lower(), \
        f"F1b gate: the principal-branch c0'' differs from the field's branch at z = {z}, k = {k}"


_step6 = V.step


def step7(zc, hvec, k, lau, rho):
    _same_branch(zc, k, lau.field)
    F1B["step"] += 1
    return _step6(zc, hvec, k, lau, rho)


V.step = step7

_series6 = S4.series_from_init


def series7(zm, kball, init):
    _same_branch(zm, acb(S6.KC), field_for(acb(S6.KC)))
    F1B["series"] += 1
    return _series6(zm, kball, init)


S4.series_from_init = series7

# ------------------------------------------------------------------------------------------------ entry
say = S5.say


def prove():
    say(f"== v7 prove (v6 + c0 field) == {V.SEG}; code {CODE}; files {', '.join(CODE_FILES[-3:])}")
    S6.prove()
    say(f"  F1b checks: {F1B}; c0 fields built: {len(_FIELDS)}")


def verdict():
    say(f"== v7 verdict (v6 + c0 field) == {V.SEG}; code {CODE}")
    try:
        S6.verdict()
    finally:
        say(f"  F1b checks: {F1B}; c0 fields built: {len(_FIELDS)}")


if __name__ == "__main__":
    dict(prove=prove, verdict=verdict)[sys.argv[1]]()
