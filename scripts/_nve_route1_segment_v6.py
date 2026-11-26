#!/usr/bin/env python3
"""Route (i) v6 = v5.2 + the P4 build: production on a general segment. [ansatz-machine-personal, 2026-11-27;
NOT yet read or tested]

The mathematics of the proof stage is v5.2's, unchanged: this file imports v5 (which imports and patches v2, v3, v4)
and changes only how n is targeted, plus a verdict stage for a segment other than [1, 1.1].
  P4a  The n target is RELATIVE (registration §5.3): the error bound must be <= 1e-2 x |F(k_c)|, with |F(k_c)| from the
       50-digit engine's floats at k_c. (v5 used an absolute 1e-3.) This steers n only; a loose target can make the
       verdict fail, never pass. R1_TOLMODE=abs restores v5's 1e-3, for the reproduction test U1 only.
  P4b  F/k^2 on the small-k (dyadic) segments (§4.2), R1_MODE=Fk2. F has a double zero at k = 0, so on [x, 2x] the
       function interpolated is g = F/k^2. On the Bernstein ellipse (inside the disc |k - k_c| <= R) |k| >= k_c - R > 0,
       so M_g = M_F / (k_c - R)^2 and the interpolation bound is e_g = e_F / (k_c - R)^2 (the same ATAP bound, divided).
       F != 0 on the segment iff g != 0 there (k > 0). The n target is 1e-2 x |g(k_c)|; v5's row_for, which sizes n for
       F, is given the equivalent tolerance 1e-2 |F(k_c)| ((k_c - R)/k_c)^2 per row (P4a's wrapper).
  P4c  A verdict for the general segment: v2's interp() and conditions() unchanged, on the chosen row's n + 1 Chebyshev
       nodes (Arb evaluator, one fsynced jsonl line per node, keyed by v6's code hash), with the registration's
       per-segment controls (§6): the planted zero (f - f(t = 1/8), at the held-out value, S5) must be REFUSED; one held-out point
       (t = 1/8) must lie inside interpolant +- bound; two ellipse samples must lie below the proved M. With R1_FULLCTL=1
       (one segment per spin): three held-out points, eight ellipse samples, the shrunken-M control (all bounds / 1e12)
       and the planted precondition at k = 4.2 +- 0.01 (must fire). The engine gate at every node is a separate process
       (`_nve_route1_engine_gate.py`, the 50-digit engine, another Python).
  F2   v6's code hash covers proto, v2..v5 AND this file (plus v5's environment string), and replaces v5's in every key
       and file name, so a v5.2 checkpoint is never reused by v6 and vice versa.
Outcome (verdict JSON `route1_seg_verdict_<BASE>.json`, deterministic: no times in it):
  certified        the three conditions hold on every theta ball, self-test and precondition true, and every control passed
  not_certified    a condition is not certified, controls passed (the split rule's case; radius_limited marks a
                   failure that splitting cannot cure: it fails even with zero interpolation error, P4d/S6)
  ALARM            a control failed (planted zero given, held-out outside its bound, proved M below a sample, the planted
                   precondition not firing): a correctness alarm, exit code 3; production STOPS.
Environment: NVE_SPIN, R1_R0, R1_KC, R1_HALF (exact rationals), R1_FLOATS (the floats file, key = R1_KC), R1_RHOS,
R1_MODE (F | Fk2), R1_TOLMODE (rel | abs), R1_FULLCTL (1 or unset).
    <.venv313 python> -I -u scripts/_nve_route1_segment_v6.py prove | verdict"""
import hashlib
import json
import math
import os
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
assert os.environ.get("R1_KC") and os.environ.get("R1_HALF") and os.environ.get("R1_FLOATS"), \
    "v6 runs a stated segment only: set R1_KC, R1_HALF and R1_FLOATS"
MODE = os.environ.get("R1_MODE", "F")
TOLMODE = os.environ.get("R1_TOLMODE", "rel")
FULLCTL = os.environ.get("R1_FULLCTL") == "1"
assert MODE in ("F", "Fk2") and TOLMODE in ("rel", "abs"), (MODE, TOLMODE)

import _nve_route1_segment_v5 as S5           # noqa: E402  (imports and patches v2, v3, v4; runs nothing)
from flint import acb, arb                     # noqa: E402

V, S4 = S5.V, S5.S4
REF = json.load(open(os.path.join(V.OUTD, V.FLOATS)))[S5.KREF]
# S7 (the Bridge's v6 read): the hash covers every file a production result depends on (the proof code, the engine
# gate, the driver, the floats script), the environment (Python, python-flint, precision), the circle R1_R0, the rows
# R1_RHOS, and the floats ENTRY of k_c that the run uses (its lasso, singular points and F(k_c)). The entry, not the
# whole floats file: production adds an entry per k_c, and the file's hash would orphan every earlier checkpoint.
CODE_FILES = S5.CODE_FILES + ("_nve_route1_segment_v6.py", "_nve_route1_engine_gate.py", "_nve_route1_production.py",
                              "_nve_route1_floats.py")
ENV6 = (f"{S5.ENVSTR}; R0 {V.R0S}; rhos {','.join(str(r) for r in S4.RHOS4)}; floats entry "
        f"{hashlib.sha256(json.dumps(REF, sort_keys=True).encode()).hexdigest()}")
CODE = hashlib.sha256(b"".join(open(os.path.join(HERE, f), "rb").read() for f in CODE_FILES)
                      + ENV6.encode()).hexdigest()[:16]
MTAG = ("" if MODE == "F" else "_Fk2") + ("" if TOLMODE == "rel" else "_tolabs")
BASE = f"v6{V.TAG}{S5.KTAG}{MTAG}_{CODE}"
# F2: v6's hash replaces v5's everywhere v5 looks it up (module globals, read at call time)
S5.CODE, S5.CODE_FILES, S5.BASE, S5.ENVSTR = CODE, CODE_FILES, BASE, ENV6
S4.CKFILE = os.path.join(V.OUTD, f"route1_seg_{BASE}_dqck.jsonl")
S5.ROWS = os.path.join(V.OUTD, f"route1_seg_{BASE}_rows.jsonl")
S5.MJSON = os.path.join(V.OUTD, f"route1_seg_M_{BASE}.json")
S5.LOG5 = V.LOG = os.path.join(V.OUTD, f"route1_seg_{BASE}.out")
NODEF = os.path.join(V.OUTD, f"route1_seg_nodes_{BASE}.jsonl")
VJSON = os.path.join(V.OUTD, f"route1_seg_verdict_{BASE}.json")
say = S5.say

FC = complex(float(REF["F"][0]), float(REF["F"][1]))       # the engine's F(k_c): steers n only
(KC, HALF), = V.seg_centres(1)
KCF, HALFF = float(KC.mid()), float(HALF.mid())


def r_of(rho):
    return HALFF * (rho + 1 / rho) / 2


def tol_for(rho):
    """The tolerance handed to v5's row_for (a choice that steers n; never part of a bound)."""
    if TOLMODE == "abs":
        return 1e-3
    t = 1e-2 * abs(FC)
    if MODE == "Fk2":
        t *= ((KCF - r_of(rho)) / KCF) ** 2          # = 1e-2 |g(k_c)| (k_c - R)^2 : n is then n_g
    return t


_row_for5 = S5.row_for


def row_for6(rho, half, kc, *a):
    if MODE == "Fk2" and not r_of(rho) < KCF:           # the Bridge's read: rejected, not asserted
        return dict(rho=rho, rejected=f"Fk2: the k-disc of rho = {rho} reaches k = 0 (R >= k_c)", code=CODE,
                    mode=MODE, tolmode=TOLMODE)
    V.TOL_F = tol_for(rho)
    r = _row_for5(rho, half, kc, *a)
    r.update(tol_F=V.TOL_F, mode=MODE, tolmode=TOLMODE)
    return r


S5.row_for = row_for6                             # v5's prove looks row_for up at call time


def prove():
    say(f"== v6 prove == {V.SEG}; mode {MODE}, tol {TOLMODE}; |F(k_c)| (engine) {abs(FC):.6e}; code {CODE}")
    S5.prove()


# --------------------------------------------------------------------------------- verdict (P4c)
def load_nodes():
    done = {}
    if os.path.exists(NODEF):
        raw = open(NODEF, "rb").read()
        cut = raw.rfind(b"\n") + 1
        if cut < len(raw):                       # a torn last record is dropped (v4 wrapper's repair)
            with open(NODEF, "r+b") as fh:
                fh.truncate(cut)
                fh.flush()
                os.fsync(fh.fileno())
        for ln in raw[:cut].split(b"\n")[:-1]:
            r = json.loads(ln)
            assert r.get("code") == CODE, f"F2 gate: node record {r.get('key')} from code {r.get('code')}, not {CODE}"
            done[r["key"]] = r
    return done


NEW = [0]


def get(done, key, kre, kim):
    """(F, T0, T1) at the POINT mid(kre) + i mid(kim), from the node file or evaluated now and appended (fsynced)."""
    if key not in done:
        r = dict(key=key, code=CODE, **V.evaluate(kre, kim, REF))
        with open(NODEF, "a") as fh:
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        done[key] = r
        NEW[0] += 1
        say(f"  {key.split('|')[-1]}: {r['sec']} s, steps {r['steps']}, radius of F {r['rad_F']:.1e}")
    r = done[key]
    assert r.get("code") == CODE
    return tuple(acb(arb(r[nm][0]), arb(r[nm][1])) for nm in ("F", "T0", "T1"))


def first(v, kmid):
    """The interpolated function at a node: F, or g = F / k^2 at the exact evaluation point kmid (an acb point)."""
    return v[0] if MODE == "F" else v[0] / (kmid * kmid)


def verdict():
    V.coverage_asserts()
    J = json.load(open(S5.MJSON))
    assert J["code"] == CODE, f"F2 gate: proof file from code {J['code']}, running code {CODE}"
    ch = J["chosen"]
    assert ch is not None, "no admissible row: the split rule's case, not a verdict"
    assert ch["code"] == CODE and ch["mode"] == MODE and ch["tolmode"] == TOLMODE
    cov = ch["coverage"]                          # F3, as v5's verdict
    assert [cov["circle"]["steps"], cov["lasso"]["steps"]] == J["steps"] and min(J["steps"]) > 0
    for loop in ("circle", "lasso"):
        c = cov[loop]
        assert c["bounds"] == c["steps"] and c["ksub"] == S5.KSUB2 and c["pairs"] == c["steps"] * S5.KSUB2, \
            f"F3 gate: {loop} {c}"
    done = load_nodes()
    n, rho = ch["n"], ch["rho"]
    MF, MT0, MT1 = (V.par_up(ch[nm]) for nm in ("MF", "MT0", "MT1"))
    # S3 (the Bridge's v6 read): R and the three error bounds are RECOMPUTED in balls from rho, n, half and the proved M,
    # not trusted from the proof file. The file's values must not be below them (an inconsistency is an ALARM), and
    # the larger of the two is used. In F/k^2 mode R feeds d = k_c - R.
    rb = arb(rho)
    Rr = (HALF * (rb + 1 / rb) / 2).upper()
    Rj = V.par_up(ch["R"])
    den = rb ** n * (rb - 1)
    er = [(4 * M / den).upper() for M in (MF, MT0, MT1)]
    ej_ = [V.par_up(ch[nm]) for nm in ("errF", "errT0", "errT1")]
    # (a relative margin of 1e-40: v5 formed errF from M_F before either was written as a 50-digit string, so the
    # recomputation from the parsed strings can exceed the file's value in the last digits; the larger one is used)
    tol = 1 + arb("1e-40")
    s3_bad = [nm for nm, ok in (("R", bool(Rj * tol >= Rr)), ("errF", bool(ej_[0] * tol >= er[0])),
                                ("errT0", bool(ej_[1] * tol >= er[1])), ("errT1", bool(ej_[2] * tol >= er[2]))) if not ok]
    R = V.amax((Rj, Rr))
    eF, e0, e1 = (V.amax((a, b)) for a, b in zip(ej_, er))
    if MODE == "Fk2":
        d = (KC - R).lower()
        assert d > 0, "Fk2: the k-disc reaches k = 0"
        MG, eG = (MF / (d * d)).upper(), (eF / (d * d)).upper()
    else:
        MG, eG = MF, eF
    Ms = (MG, MT0, MT1)
    dist = (R - HALF).lower()
    assert dist > 0
    base = f"{V.SEG}|{MODE}|n={n}"
    say(f"== v6 verdict == {V.SEG}; mode {MODE}; rho = {rho}, n = {n}; code {CODE}; node records on disk {len(done)}; "
        f"full controls {FULLCTL}")
    vals = []
    for j in range(n + 1):
        kj = KC + HALF * (arb.pi() * j / n).cos()
        v = get(done, f"{base}|node{j}", kj, arb(0))
        km = acb(kj.mid())
        dk = kj.rad() * 2
        f0 = first(v, km)
        vals.append(tuple(x + (Ms[m] / dist * dk).upper() * V.UNIT for m, x in enumerate((f0, v[1], v[2]))))
    (pF, qF), (p0, q0), (p1, q1) = (V.interp([v[m] for v in vals], n) for m in range(3))
    okF, ok0, ok1, mg = V.conditions(qF, q0, q1, eG, e0, e1)
    cond = bool(okF and ok0 and ok1 and J["selftest"] and ch["precondition"]["ok"])
    lows = (mg[0] - eG, mg[1] - e0, mg[2] - e1)
    fn = "F" if MODE == "F" else "F/k^2"
    say(f"  {fn}: min |p| >= {V.lo_dec(mg[0], 9)}; proved error bound <= {V.hi_sci(eG)} -> |{fn}| >= {V.lo_dec(lows[0], 9)}; "
        f"!= 0: {okF}")
    say(f"  tr M0: min |p| >= {V.lo_dec(mg[1], 9)}; bound <= {V.hi_sci(e0)} -> |tr M0| >= {V.lo_dec(lows[1], 9)}; != 0: {ok0}")
    say(f"  tr M1: min |Im p| >= {V.lo_dec(mg[2], 9)}; bound <= {V.hi_sci(e1)} -> |Im tr M1| >= {V.lo_dec(lows[2], 9)}; "
        f"not in [-2, 2]: {ok1}")
    # held-out point(s): inside interpolant +- bound
    held = ("-5/8", "1/8", "3/4") if FULLCTL else ("1/8",)
    hold_ok, hold = True, []
    for s in held:
        t = V.frac(s)
        kt = KC + HALF * t
        v = get(done, f"{base}|held t={s}", kt, arb(0))
        fv = (first(v, acb(kt.mid())), v[1], v[2])
        row = []
        for m, (p, e) in enumerate(((pF, eG), (p0, e0), (p1, e1))):
            dd = p(t) - fv[m]
            row.append((dd.abs_lower(), dd.abs_upper(), e))
            hold_ok &= bool(dd.abs_lower() <= e)
        hold.append((s, row))
        if s == "1/8":
            f18 = fv[0]
        say(f"  held-out t = {s}: |p - f| in [{float(row[0][0]):.1e}, {float(row[0][1]):.1e}] ({fn}), "
            f"[{float(row[1][0]):.1e}, {float(row[1][1]):.1e}] (tr M0), [{float(row[2][0]):.1e}, {float(row[2][1]):.1e}] (tr M1)")
    # S5 (the Bridge's read): the planted zero is f - f(t = 1/8), with f(1/8) the HELD-OUT value, so its zero falls
    # between nodes and the refusal depends on the error bound (at node n/2, as before, it was refused whatever e was).
    # The node balls and the ball of f(1/8) contain the true values, so with an honest bound the theta ball containing
    # acos(1/8) has |p| <= eP and the certificate MUST be refused; a refusal that fails is an ALARM.
    fc = f18
    _pG, qG = V.interp([v[0] - fc for v in vals], n)
    eP = (eG * (MG + fc.abs_upper()) / MG).upper()
    okP = V.conditions(qG, q0, q1, eP, e0, e1)[0]
    say(f"  control, planted zero ({fn} - {fn}(t = 1/8), between nodes): certificate "
        f"{'GIVEN (CONTROL FAILED)' if okP else 'REFUSED (as it must be)'}")
    # ellipse samples: the proved M must be at least each sampled |f|
    ej = range(8) if FULLCTL else (0, 4)
    samp = [arb(0), arb(0), arb(0)]
    for j in ej:
        tt = V.ell_pt(j, rho)
        kre, kim = KC + HALF * arb(tt.real), HALF * arb(tt.imag)
        v = get(done, f"{base}|ellipse{j}/8 rho={rho}", kre, kim)
        fv = (first(v, acb(kre.mid(), kim.mid())), v[1], v[2])
        samp = [V.amax((samp[m], fv[m].abs_upper())) for m in range(3)]
    m_ok = all(bool(samp[m] <= Ms[m]) for m in range(3))
    say(f"  proved M >= sampled on the ellipse rho = {rho} ({len(ej)} points): {m_ok} "
        f"(overestimate x{float(Ms[0] / samp[0]):.1e}, x{float(Ms[1] / samp[1]):.1e}, x{float(Ms[2] / samp[2]):.1e})")
    extra = {}
    if FULLCTL:
        sh = arb(10) ** 12
        o2 = V.conditions(qF, q0, q1, eG / sh, e0 / sh, e1 / sh)
        broke = [(s, ("f", "tr M0", "tr M1")[m]) for s, row in hold for m in range(3) if bool(row[m][0] > row[m][2] / sh)]
        below = [nm for m, nm in enumerate(("f", "tr M0", "tr M1")) if bool(Ms[m] / sh < samp[m])]
        pre = V.precondition(arb("4.2") + arb("0.01") * V.UNIT)
        extra = dict(shrunk_verdict_passes=bool(o2[0] and o2[1] and o2[2]), shrunk_heldout_breaks=[list(b) for b in broke],
                     shrunk_M_below_sampled=below, planted_precondition_fires=not pre["ok"])
        say(f"  shrunken M (/1e12): verdict still passes {extra['shrunk_verdict_passes']}; held-out breaks {broke or 'none'}; "
            f"below the sampled max for {below or 'none'}; planted precondition at 4.2 fires: {not pre['ok']}")
    alarm = [nm for nm, bad in (("proof file below the recomputed " + "/".join(s3_bad), bool(s3_bad)),
                                 ("planted zero GIVEN", okP), ("held-out outside its bound", not hold_ok),
                                 ("proved M below a sample", not m_ok),
                                 ("planted precondition did not fire", FULLCTL and not extra["planted_precondition_fires"]),
                                 ("shrunken M changed nothing", FULLCTL and not (extra["shrunk_heldout_breaks"]
                                                                                 or extra["shrunk_M_below_sampled"]
                                                                                 or not extra["shrunk_verdict_passes"])))
             if bad]
    outcome = "ALARM" if alarm else ("certified" if cond else "not_certified")
    # P4d, made decidable (S6, the Bridge's read): is a failure one that splitting cannot cure? Splitting shrinks the
    # interpolation bound (e ~ rho^-n over a shorter segment) but not the radius of each node value, which the
    # evaluator sets (its Taylor tails over the walk; at small k, F = tr(commutator) - 2 cancels to ~ c2 k^2 while the
    # radius does not shrink). Test: rerun conditions() with ZERO interpolation error. A condition that fails even then
    # is blocked by the node balls alone. radius_limited iff some failed condition also fails at e = 0. A stop decision
    # for the driver (efficiency only), never part of a certificate.
    z = arb(0)
    okF0, ok00, ok10, _m0 = V.conditions(qF, q0, q1, z, z, z)
    unsplit = [nm for nm, ok, ok_0 in (("f", okF, okF0), ("tr M0", ok0, ok00), ("tr M1", ok1, ok10)) if not ok and not ok_0]
    radius_limited = bool(unsplit)
    rad_max = max(float(v[0].rad()) for v in vals)
    fmin = min(float(v[0].abs_lower()) for v in vals) if all(bool(v[0].abs_lower() > 0) for v in vals) else 0.0
    say(f"  node balls: largest radius of {fn} {rad_max:.2e}, smallest |{fn}| {fmin:.2e}; conditions failing even at "
        f"e = 0 (splitting cannot cure): {unsplit or 'none'}")
    res = dict(seg=V.SEG, mode=MODE, tolmode=TOLMODE, code=CODE, rho=rho, n=n, outcome=outcome, alarm=alarm,
               conditions=dict(f=okF, trM0=ok0, trM1=ok1, selftest=J["selftest"], precondition=ch["precondition"]["ok"]),
               abs_f_ge=V.lo_dec(lows[0], 9), abs_trM0_ge=V.lo_dec(lows[1], 9), abs_Im_trM1_ge=V.lo_dec(lows[2], 9),
               err=[V.hi_sci(x) for x in (eG, e0, e1)], M=[V.hi_sci(x) for x in Ms], planted_zero_refused=not okP,
               held_out_consistent=hold_ok, proved_M_ge_sampled=m_ok, n_nodes=n + 1, n_held=len(held), n_ellipse=len(ej),
               node_radius_max=f"{rad_max:.3e}", node_abs_min=f"{fmin:.3e}", radius_limited=radius_limited,
               unsplittable=unsplit, s3_inconsistent=s3_bad,
               **extra)
    if MODE == "Fk2" and okF:
        klo = (KC - HALF).lower()
        res["abs_F_ge"] = V.lo_dec((lows[0] * klo * klo).lower(), 9)     # |F| = |g| k^2 >= low_g k_lo^2
    json.dump(res, open(VJSON, "w"), indent=1, sort_keys=True)
    say(f"  OUTCOME: {outcome.upper()}{'  ' + '; '.join(alarm) if alarm else ''}  ({fn} != 0, tr M0 != 0, tr M1 not in "
        f"[-2, 2] for every real k in the segment); new evaluations {NEW[0]}; peak rss "
        f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")
    if alarm:
        sys.exit(3)


if __name__ == "__main__":
    dict(prove=prove, verdict=verdict)[sys.argv[1]]()
