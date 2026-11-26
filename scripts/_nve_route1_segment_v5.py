#!/usr/bin/env python3
"""Route (i), v5 = v4 plus the three REQUIRED fixes of the registration (docs/ROUTE1_REGISTRATION.md v1, §3(d)),
from the non-author read data/nve/ROUTE1_V3V4_READ.md. [ansatz-machine-personal, 2026-11-26; NOT yet run or tested]

The mathematics is v4's, unchanged: this file imports v2, v3, v4 (and Part B's proto) and adds only checks and keys.
  F1  Re(1 - k phi(z)) > 0 is ASSERTED at every expansion point of a series step: v2's Taylor step (reference walks
      and node evaluations) and v4's dq-series at the step midpoint (k a ball). A failure raises AssertionError, a
      correctness gate: it is NOT the "refused box, halve rho" path (v2's safe_step catches only RuntimeError).
  F2  A code hash (sha256 of proto, v2, v3, v4, this file, and [A1] the Python and python-flint versions and the
      working precision) is part of every checkpoint key: the per-step dq
      checkpoint, the rows file and the node file. Files are named by the hash, and every record carries it; a
      record whose hash differs from the running code makes the run STOP (it is never reused).
  F3  Coverage counts go into the proof JSON (per loop: steps, step bounds, k-sub-boxes, pairs), and the verdict
      stage asserts them against counts it recomputes from the step lists' lengths, plus the code hash. v2's own
      boxes == expected_boxes assert is then fed real numbers again (v4's wrappers had set both to [0, 0]).
Segments: v2's single segment [1, 1.1] by default. v5.1 (for pilot P3): R1_KC and R1_HALF (exact rationals, e.g.
R1_KC=2 R1_HALF=1/20) move the PROOF stage to [kc - half, kc + half], with the lasso and singular points of k = R1_KC
from the floats file and every output file tagged _kc<kc>. Unset, every line of v5 runs as before. The verdict
stage refuses a moved segment (v2's verdict and node stages still state [1, 1.1]); generalising them is a
registration item.
    NVE_SPIN=3/5 R1_R0=1.35 nice -n 15 <quantum python> -I -u scripts/_nve_route1_segment_v5.py prove
    NVE_SPIN=3/5 R1_R0=1.35 nice -n 15 <quantum python> -I -u scripts/_nve_route1_segment_v5.py verdict
Outputs: data/nve/eps/route1_seg_*_v5{TAG}_<hash>*. One process, one core, < 300 MB."""
import hashlib
import json
import math
import os
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flint                                       # noqa: E402
from flint import acb, arb, ctx                    # noqa: E402
import _nve_route1_proto as P                      # noqa: E402
import _nve_route1_segment_v2 as V                 # noqa: E402
import _nve_route1_segment_v3 as S3                # noqa: E402
import _nve_route1_segment_v4 as S4                # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_FILES = ("_nve_route1_proto.py", "_nve_route1_segment_v2.py", "_nve_route1_segment_v3.py",
              "_nve_route1_segment_v4.py", "_nve_route1_segment_v5.py")
# A1 (the Bridge's v5 read): the hash also covers the run-time environment that does the arithmetic, so a checkpoint
# written by another Python or python-flint version (e.g. the other machine) is refused like one from other code.
ENVSTR = f"python {sys.version.split()[0]}; python-flint {flint.__version__}; prec {ctx.prec}"
CODE = hashlib.sha256(b"".join(open(os.path.join(HERE, f), "rb").read() for f in CODE_FILES)
                      + ENVSTR.encode()).hexdigest()[:16]
A = V.A
KSUB2 = V.KSUB * V.KSUB
# v5.1: the segment from the environment (P3). Default: v2's SEG and seg_centres untouched, floats key "21/20".
KCS, HALFS = os.environ.get("R1_KC"), os.environ.get("R1_HALF", "1/20")
KREF = "21/20"
KTAG = ""
if KCS is not None:
    from flint import fmpq
    _q = lambda t: fmpq(*[int(x) for x in t.split("/")]) if "/" in t else fmpq(int(t))
    _kc, _h = _q(KCS), _q(HALFS)
    assert _h > 0 and _kc - _h > 0
    V.SEG = f"spin {V.SPIN}|k in [{_kc - _h}, {_kc + _h}]"

    def _seg_centres(nseg):
        assert nseg == 1, "v5.1 moves one segment only"
        return [(arb(_kc), arb(_h))]
    V.seg_centres = _seg_centres
    KREF, KTAG = KCS, "_kc" + KCS.replace("/", "o") + "h" + HALFS.replace("/", "o")
    V.FLOATS = os.environ.get("R1_FLOATS", V.FLOATS)   # P3's own floats file (the committed ones stay untouched)
BASE = f"v5{V.TAG}{KTAG}_{CODE}"
S4.CKFILE = os.path.join(V.OUTD, f"route1_seg_{BASE}_dqck.jsonl")
ROWS = os.path.join(V.OUTD, f"route1_seg_{BASE}_rows.jsonl")
MJSON = os.path.join(V.OUTD, f"route1_seg_M_{BASE}_nseg1.json")
LOG5 = os.path.join(V.OUTD, f"route1_seg_{V.SPIN.replace('/', '_')}{KTAG}_v5.out")
F1_COUNT = dict(step=0, series=0)


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG5, "a") as fh:
        fh.write(s + "\n")


V.LOG = LOG5      # v2's and v4's log lines from this process go to the v5 log, never to their committed logs
S4.say = say      # (the verdict stage redirects V.LOG again, to its own file)


# --------------------------------------------------------------------------------- F1: the branch assert
def one_minus_kphi(z, k):
    u2 = z * z / (A * A)
    phi = (21 * u2 * u2 - 18 * u2 + 1) / (10 * (3 * u2 - 1) * (3 * u2 - 1))
    return 1 - k * phi


def assert_branch(z, k, where):
    v = one_minus_kphi(z, k)
    assert v.is_finite() and v.real > 0, (f"F1 gate: Re(1 - k phi) > 0 not certified at the expansion point of a "
                                          f"{where} (z = {z}, k = {k}, 1 - k phi = {v})")


_v2_step = V.step
_v4_series = S4.series_from_init


def step_checked(zc, hvec, k, lau, rho):
    assert_branch(zc, k, "Taylor step")
    F1_COUNT["step"] += 1
    return _v2_step(zc, hvec, k, lau, rho)


def series_checked(zm, kball, init):
    assert_branch(zm, kball, "dq-series")
    F1_COUNT["series"] += 1
    return _v4_series(zm, kball, init)


V.step = step_checked                 # v2's safe_step looks `step` up at call time
S4.series_from_init = series_checked  # v4's dq_list_v4 looks it up at call time


# --------------------------------------------------------------------------------- F2: code hash in every key
_v4_ck_key = S4.ck_key


def ck_key_coded(steps, R, name):
    return _v4_ck_key(steps, R, name) + f"|code={CODE}"


S4.ck_key = ck_key_coded


def refuse_foreign(path, field="code"):
    """Every record of an existing checkpoint file must carry this code's hash; any other hash STOPS the run."""
    if not os.path.exists(path):
        return 0
    n = 0
    for ln in open(path, "rb").read().split(b"\n"):
        if not ln.strip():
            continue
        try:
            r = json.loads(ln)
        except ValueError:
            continue                          # a torn last record; the loaders handle it
        got = r.get(field) if field != "key" else r["key"].rsplit("|code=", 1)[-1] if "|code=" in r["key"] else None
        assert got == CODE, f"F2 gate: {os.path.basename(path)} holds a record from code {got}, not {CODE}: not reused"
        n += 1
    return n


# --------------------------------------------------------------------------------- prove (v4's, with F2/F3)
def row_for(rho, half, kc, st0, st1, M0, M1, lau_c, laud_c):
    rb = arb(rho)
    R = (half * (rb + 1 / rb) / 2).upper()
    K, dKs = V.kbox(kc, R)
    pre = V.precondition(K)
    if not pre["ok"]:
        return dict(rho=rho, rejected="precondition not certified", precondition=pre, code=CODE)
    d0, w0, r0 = S4.dq_list_v4(st0, kc, R, lau_c, laud_c, name="circle")
    d1, w1, r1 = S4.dq_list_v4(st1, kc, R, lau_c, laud_c, name="lasso") if d0 is not None else (None, None, None)
    if d0 is None or d1 is None:
        return dict(rho=rho, rejected=f"holomorphy box fails at {w0 if d0 is None else w1}", code=CODE)
    nk = len(dKs)
    cov = dict(circle=dict(steps=len(st0), bounds=len(d0), ksub=nk, pairs=len(d0) * nk),
               lasso=dict(steps=len(st1), bounds=len(d1), ksub=nk, pairs=len(d1) * nk))
    C0, C1 = V.gauge(st0, d0), V.gauge(st1, d1)
    I0, I1 = (R * V.dyson_sum(st0, d0, C0)).upper(), (R * V.dyson_sum(st1, d1, C1)).upper()
    g0, g1 = V.gauge_norms(M0, C0), V.gauge_norms(M1, C1)
    nM0, nM1 = g0[0] * I0.exp(), g1[0] * I1.exp()
    MF = (2 + nM1 * nM1 * nM0 * nM0).upper()
    MT0 = (arb(2).sqrt() * g0[1] * I0.exp()).upper()
    MT1 = (arb(2).sqrt() * g1[1] * I1.exp()).upper()
    n = max(2, math.ceil(math.log(4 * float(MF) / ((rho - 1) * V.TOL_F)) / math.log(rho)))
    n += n % 2
    den = rb ** n * (rb - 1)
    eF, e0, e1 = (4 * MF / den).upper(), (4 * MT0 / den).upper(), (4 * MT1 / den).upper()
    return dict(rho=rho, n=n, R=V.ser(R), I0=V.ser(I0), I1=V.ser(I1), c0_per_k=float(I0 / R), c1_per_k=float(I1 / R),
                MF=V.ser(MF), MT0=V.ser(MT0), MT1=V.ser(MT1), errF=V.ser(eF), errT0=V.ser(e0), errT1=V.ser(e1),
                precondition=pre, gauge=dict(C0=[[str(x) for x in rr] for rr in C0], C1=[[str(x) for x in rr] for rr in C1],
                                            norms0=[V.ser(x) for x in g0], norms1=[V.ser(x) for x in g1]),
                ratio_median=[sorted(r0)[len(r0) // 2], sorted(r1)[len(r1) // 2]], ratio_max=[max(r0), max(r1)],
                coverage=cov, code=CODE, stats=dict(S4.STATS), f1=dict(F1_COUNT))   # ratio_*: v4's diagnostics, restored (T1 prep)


def prove():
    t0 = time.time()
    V.coverage_asserts()
    nck, nrows = refuse_foreign(S4.CKFILE, "key"), refuse_foreign(ROWS)
    ref = json.load(open(os.path.join(V.OUTD, V.FLOATS)))[KREF]
    sing = [complex(float(p[0]), float(p[1])) for p in ref["points"]]
    lasso = [complex(float(p[0]), float(p[1])) for p in ref["lasso"]]
    say(f"== prove (v5 = v4 + F1 branch assert, F2 code-hash keys, F3 coverage counts) == {V.SEG}; circle {V.R0S}; "
        f"code {CODE}; python {sys.version.split()[0]}, python-flint {flint.__version__}; rows {S4.RHOS4}; "
        f"checkpoint records of this code already on disk: dq {nck}, rows {nrows}")
    (kc, half), = V.seg_centres(1)
    lau_c, laud_c = V.laurent(acb(kc)), V.laurent(acb(kc), True)
    st_ok = V.selftest(kc, lau_c, laud_c)
    M0, st0 = V.walk(V.circle_vertices(), acb(kc), lau_c, sing, record=True)
    M1, st1 = V.walk(lasso, acb(kc), lau_c, sing, record=True)
    say(f"  self-test {st_ok}; reference: circle {len(st0)} steps, lasso {len(st1)} steps; F1 checks so far {F1_COUNT}  "
        f"[{time.time() - t0:.0f} s]")
    done = {}
    if os.path.exists(ROWS):
        for line in open(ROWS):
            if line.strip():
                rr = json.loads(line)
                assert rr.get("code") == CODE
                done[rr["rho"]] = rr
    for rho in S4.RHOS4:
        if rho in done:
            say(f"  rho = {rho}: from this code's checkpoint")
            continue
        ts = time.time()
        row = row_for(rho, half, kc, st0, st1, M0, M1, lau_c, laud_c)
        row["sec"] = round(time.time() - ts)
        with open(ROWS, "a") as fh:
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        done[rho] = row
        if "rejected" in row:
            say(f"  rho = {rho}: REJECTED ({row['rejected']})")
            continue
        say(f"  rho = {rho}: M_F <= {V.hi_sci(arb(row['MF']))}, n = {row['n']}; coverage {row['coverage']}; "
            f"F1 checks {row['f1']}   [{row['sec']} s]")
    rows = [done[r] for r in S4.RHOS4 if r in done and "rejected" not in done[r]]
    best = min(rows, key=lambda r: (r["n"], float(arb(r["errF"]).mid()))) if rows else None
    out = dict(seg=V.SEG, version=5, code=CODE, code_env=ENVSTR, code_files=list(CODE_FILES), rows=rows, chosen=best, selftest=st_ok,
               steps=[len(st0), len(st1)], env=dict(python=sys.version.split()[0], flint=flint.__version__,
                                                    interpreter=sys.executable))
    json.dump(out, open(MJSON, "w"), indent=1)
    if best:
        say(f"  CHOSEN: rho = {best['rho']}, n = {best['n']}")
    say(f"  prove v5: {time.time() - t0:.0f} s, peak rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")


# --------------------------------------------------------------------------------- verdict (v2's, with F2/F3)
def verdict():
    assert KCS is None, "v5.1: the verdict stage runs only on the default segment [1, 1.1]"
    J = json.load(open(MJSON))
    assert J["code"] == CODE, f"F2 gate: proof file from code {J['code']}, running code {CODE}"
    ch = dict(J["chosen"])
    assert ch["code"] == CODE
    cov = ch["coverage"]
    # F3: recompute the expected counts independently from the step counts the proof stage recorded
    assert [cov["circle"]["steps"], cov["lasso"]["steps"]] == J["steps"] and min(J["steps"]) > 0
    for loop in ("circle", "lasso"):
        c = cov[loop]
        assert c["bounds"] == c["steps"] and c["ksub"] == KSUB2 and c["pairs"] == c["steps"] * KSUB2, f"F3 gate: {loop} {c}"
    ch["boxes"] = [cov["circle"]["pairs"], cov["lasso"]["pairs"]]
    ch["expected_boxes"] = [J["steps"][0] * KSUB2, J["steps"][1] * KSUB2]   # v2 asserts boxes == expected_boxes
    (kc, half), = V.seg_centres(1)
    seg = dict(i=0, kc=f"{float(kc.mid()):.6f}", selftest=J["selftest"], chosen=ch)
    tag = f"{V.TAG}_v5cert_{CODE}"
    json.dump(dict(seg=V.SEG, nseg=1, segs=[seg], version="5-cert", code=CODE),
              open(os.path.join(V.OUTD, f"route1_seg_M_v2{tag}_nseg1.json"), "w"), indent=1)
    V.TAG = tag
    V.NODEFILE["arb"] = nf = os.path.join(V.OUTD, f"route1_seg_nodes_arb{tag}.jsonl")
    V.LOG = os.path.join(V.OUTD, f"route1_seg_{V.SPIN.replace('/', '_')}_v5cert.out")
    if os.path.exists(nf):                      # torn last record: drop it (v4 wrapper's repair), then F2 on the rest
        raw = open(nf, "rb").read()
        cut = raw.rfind(b"\n") + 1
        if cut < len(raw):
            V.say(f"  node file: torn last record ({len(raw) - cut} bytes) dropped; truncated to {cut} bytes")
            with open(nf, "r+b") as fh:
                fh.truncate(cut)
                fh.flush()
                os.fsync(fh.fileno())
    nold = refuse_foreign(nf)

    def get_coded(done, which, key, kre, kim, ref):
        if key not in done:
            assert which == "arb"
            r = dict(key=key, code=CODE, **V.evaluate(kre, kim, ref))
            with open(V.NODEFILE[which], "a") as fh:
                fh.write(json.dumps(r) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            done[key] = r
            V.say(f"  {key}: {r['sec']} s, steps {r['steps']}, radius of F {r['rad_F']:.1e}")
        r = done[key]
        assert r.get("code") == CODE, f"F2 gate: node record {key} from code {r.get('code')}"
        return tuple(V.acb(V.arb(r[nm][0]), V.arb(r[nm][1])) for nm in ("F", "T0", "T1"))

    V.get = get_coded
    V.say(f"== v5 verdict == {V.SEG}; code {CODE}; rho = {ch['rho']}, n = {ch['n']}; coverage asserted {ch['boxes']}; "
          f"node records of this code on disk: {nold}")
    V.nodes(1, "arb")
    V.verdict(1, "arb")
    V.say(f"  F1 checks in this process: {F1_COUNT}")


if __name__ == "__main__":
    dict(prove=prove, verdict=verdict)[sys.argv[1]]()
