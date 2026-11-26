#!/usr/bin/env python3
"""T2, T3, T4 (and, on v5.2, T5) of the route-(i) registration (§3(d)), each tested in BOTH directions. [ansatz-machine-personal, 2026-11-26]
    NVE_SPIN=3/5 R1_R0=1.35 <.venv313 python> -I -u scripts/_nve_route1_t234.py
Run after T1, which leaves this code's v5 dq checkpoint, rows file and proof JSON on disk. Every planted file is
backed up first and restored afterwards, and the restore is checked by sha256.

Pass criteria (fixed before the run):
  T2 (F2, a foreign code hash STOPS the run): a record with another code hash planted in (a) the dq checkpoint,
     (b) the rows file, (c) the proof JSON, (d) the node file each makes the stage exit non-zero with "F2 gate" in its
     output, without writing any new record. Other direction: the untampered prove reruns entirely from this code's
     checkpoint (rc 0, "from this code's checkpoint" for every row, the proof JSON unchanged apart from `sec`), and the
     untampered verdict CERTIFIES.
  T3 (F1, a bad expansion point raises): at z with Re(1 - k phi) <= 0, (a) v2's step through safe_step (which catches
     only RuntimeError, the "refused box" path) and (b) v4's dq-series both raise AssertionError with "F1 gate".
     Other direction: at a point on the reference circle the gate passes and the patched step returns normally.
  T4 (F3, coverage asserted): the proof JSON with (a) the chosen row's circle pair count + 1, (b) its lasso bound count
     + 1, makes the verdict exit non-zero with "F3 gate", before any node is evaluated (node file unchanged). Other
     direction: the untampered verdict certifies (T2's run), and a rerun reads every node from disk (rc 0)."""
import hashlib
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_route1_segment_v5 as S5          # noqa: E402  (imports and patches v2/v4; runs nothing)
from flint import acb, arb                    # noqa: E402

V, S4 = S5.V, S5.S4
PY, ME = sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_nve_route1_segment_v5.py")
FOREIGN = "0" * 16
NODEF = os.path.join(V.OUTD, f"route1_seg_nodes_arb{V.TAG}_v5cert_{S5.CODE}.jsonl")
RES = []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def run(stage):
    p = subprocess.run([PY, "-I", "-u", ME, stage], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def record(name, ok, note):
    RES.append((name, ok))
    print(f"{name}: {'PASS' if ok else 'FAIL'}  ({note})", flush=True)


def planted(name, path, mutate, stage, gate):
    """Back up path, mutate it, run the stage, expect rc != 0 and the gate's message; restore and check the restore."""
    bak = path + ".t234bak"
    shutil.copy2(path, bak)
    h0 = sha(path)
    watch = [S4.CKFILE, S5.ROWS, NODEF]
    before = {p: sha(p) for p in watch if p != path}
    try:
        mutate(path)
        assert sha(path) != h0, "the plant changed nothing"
        rc, out = run(stage)
        unchanged = all(sha(p) == h for p, h in before.items())
        hit = rc != 0 and gate in out
        line = next((l for l in out.splitlines() if gate in l), out.strip().splitlines()[-1] if out.strip() else "")
        record(name, hit and unchanged, f"rc {rc}; other checkpoint files unchanged {unchanged}; {line.strip()[:160]}")
    finally:
        shutil.move(bak, path)
        assert sha(path) == h0, f"restore of {path} failed"


def append_foreign_line(field):
    def f(path):
        recs = [l for l in open(path, "rb").read().split(b"\n") if l.strip()]
        r = json.loads(recs[0])
        if field == "key":
            r["key"] = r["key"].replace(f"|code={S5.CODE}", f"|code={FOREIGN}")
        else:
            r[field] = FOREIGN
        with open(path, "ab") as fh:
            fh.write((json.dumps(r) + "\n").encode())
    return f


def edit_json(fn):
    def f(path):
        J = json.load(open(path))
        fn(J)
        json.dump(J, open(path, "w"), indent=1)
    return f


print(f"== T2-T4 == {V.SEG}; code {S5.CODE}; python {sys.version.split()[0]}", flush=True)
for p in (S4.CKFILE, S5.ROWS, S5.MJSON):
    assert os.path.exists(p), f"T1 output missing: {p}"
assert not os.path.exists(NODEF), "node file exists before the control verdict: refusing to reuse it"

# ---- T2, the other direction first: untampered prove reruns from this code's checkpoint
J0 = json.load(open(S5.MJSON))
rc, out = run("prove")
J1 = json.load(open(S5.MJSON))
nfrom = out.count("from this code's checkpoint")
same = json.dumps(J0, sort_keys=True) == json.dumps(J1, sort_keys=True)
record("T2 control: untampered prove resumes", rc == 0 and nfrom == len(S4.RHOS4) and same,
       f"rc {rc}; rows from checkpoint {nfrom}/{len(S4.RHOS4)}; proof JSON unchanged {same}")
# ---- T2 (a) to (c)
planted("T2a foreign record in the dq checkpoint", S4.CKFILE, append_foreign_line("key"), "prove", "F2 gate")
planted("T2b foreign record in the rows file", S5.ROWS, append_foreign_line("code"), "prove", "F2 gate")
planted("T2c foreign code in the proof JSON", S5.MJSON, edit_json(lambda J: J.__setitem__("code", FOREIGN)), "verdict", "F2 gate")

# ---- T4 (before any node exists: a refusal must come before node evaluation, so no node file may appear)
def bump(loop, field):
    def fn(J):
        J["chosen"]["coverage"][loop][field] += 1
    return fn


for nm, loop, field in (("T4a circle pair count + 1", "circle", "pairs"), ("T4b lasso bound count + 1", "lasso", "bounds")):
    planted(nm, S5.MJSON, edit_json(bump(loop, field)), "verdict", "F3 gate")
    if os.path.exists(NODEF):
        record(nm + ": no node evaluated", False, "a node file appeared")

# ---- the control verdict (untampered): must certify; this is the full v5 verdict at the chosen row
rc, out = run("verdict")
cert = rc == 0 and "VERDICT: CERTIFIED" in out
vline = next((l for l in out.splitlines() if "VERDICT" in l), "")
fline = next((l for l in out.splitlines() if "|F| >=" in l), "")
record("T2/T4 control: untampered v5 verdict certifies", cert, f"rc {rc}; {vline.strip()}; {fline.strip()[:120]}")
print(out[-3000:], flush=True)

# ---- T2 (d) and the T4 rerun direction
if os.path.exists(NODEF):
    rc, out = run("verdict")
    record("T4 control: verdict rerun reads every node from disk", rc == 0 and "VERDICT: CERTIFIED" in out
           and "s, steps" not in out, f"rc {rc}")
    planted("T2d foreign record in the node file", NODEF, append_foreign_line("code"), "verdict", "F2 gate")
else:
    record("T2d foreign record in the node file", False, "no node file after the control verdict")

# ---- T3, in-process
(kc, half), = V.seg_centres(1)
kb = acb(kc)
zbad = V.A * acb(arb(1) / 3, arb("0.1")).sqrt()
vbad = S5.one_minus_kphi(zbad, kb)
print(f"T3 point: z = {zbad}, 1 - k phi = {vbad}", flush=True)
for nm, call in (("T3a v2 step via safe_step", lambda: V.safe_step(zbad, None, kb, None, None)),
                 ("T3b v4 dq-series", lambda: S4.series_from_init(zbad, kb, None))):
    try:
        call()
        record(nm, False, "no exception")
    except AssertionError as e:
        record(nm, "F1 gate" in str(e) and not (vbad.real > 0), f"AssertionError: {str(e)[:100]}")
    except Exception as e:
        record(nm, False, f"{type(e).__name__}: {str(e)[:100]}")
cv = V.circle_vertices()
zgood, znext = acb(cv[0].real, cv[0].imag), acb(cv[1].real, cv[1].imag)
n0 = S5.F1_COUNT["step"]
try:
    r = V.safe_step(zgood, (znext - zgood) / 8, kb, V.laurent(kb), 0.05)   # walk's convention: exact point, short step
    record("T3 control: gate passes on the reference circle", r is not None and S5.F1_COUNT["step"] == n0 + 1,
           f"1 - k phi = {S5.one_minus_kphi(zgood, kb)}; patched step {'returned a step' if r is not None else 'refused the box'}; "
           f"F1 step checks {n0} -> {S5.F1_COUNT['step']}")
except AssertionError as e:
    record("T3 control: gate passes on the reference circle", False, str(e)[:120])

# ---- B1 (v5.1 only): R1_HALF or R1_FLOATS without R1_KC must refuse before anything runs
if hasattr(S5, "KCS"):
    for extra in ({"R1_KCC": "2", "R1_HALF": "1/20"}, {"R1_FLOATS": "route1_floats.json"}):
        before = {p: sha(p) for p in (S4.CKFILE, S5.ROWS, S5.MJSON)}
        p = subprocess.run([PY, "-I", "-u", ME, "prove"], capture_output=True, text=True, env={**os.environ, **extra})
        out = p.stdout + p.stderr
        record(f"B1 half-set environment {sorted(extra)} refused", p.returncode != 0 and "B1 gate" in out
               and all(sha(q) == h for q, h in before.items()), f"rc {p.returncode}")

# ---- T5 (v5.2 only, C1): the n formula fails closed. row_for runs in-process with its expensive inputs stubbed
# (kbox, precondition, the dq lists, gauge, Dyson sum, gauge norms), so that M_F = 2 + exp(4 I) with I = R * D for a
# chosen D (both loops alike, all gauge norms 1). Pass criteria (fixed before the run):
#   T5a a runaway M_F (beyond the float range; P3's spin 9/10 k_c 3 case) gives a REJECTED row ("n > 40"), no
#       exception, and the row serialises with json.dumps as prove writes it. Other direction: v5.1's float expression raises OverflowError on that same M_F.
#   T5b n_raw in (40, 41) gives n = 42 after evening, so the SECOND branch must reject it ("n = 42 > 40").
#   T5c control: n_raw about 20.3 gives an ADMITTED row whose n equals v5.1's float expression (22).
if hasattr(S5, "NMAX"):
    import math
    saved = (V.kbox, V.precondition, S4.dq_list_v4, V.gauge, V.dyson_sum, V.gauge_norms)
    rho, half, kc = 4.0, arb(1) / 20, arb(21) / 20
    rb = arb(rho)
    R = (half * (rb + 1 / rb) / 2).upper()

    def D_for(nraw):
        """D such that log(4 M_F / ((rho - 1) TOL)) / log(rho) = nraw, with M_F = 2 + exp(4 R D)."""
        MF = (rb - 1) * arb(V.TOL_F) * rb ** arb(nraw) / 4
        return ((MF - 2).log() / (4 * R)).upper()

    def run_row(D):
        V.kbox = lambda kc_, R_: (None, [0] * V.KSUB * V.KSUB)
        V.precondition = lambda K: dict(ok=True, stub=True)
        S4.dq_list_v4 = lambda st, kc_, R_, lc, ldc, name=None: ([arb(1)] * len(st), None, [1.0])
        V.gauge = lambda st, d: [[1.0, 0.0], [0.0, 1.0]]
        V.dyson_sum = lambda st, d, C: D
        V.gauge_norms = lambda M, C: (arb(1), arb(1), arb(1))
        try:
            return S5.row_for(rho, half, kc, [0] * 3, [0] * 3, None, None, None, None)
        finally:
            V.kbox, V.precondition, S4.dq_list_v4, V.gauge, V.dyson_sum, V.gauge_norms = saved

    def old_n(D):
        MF = (2 + (4 * R * D).exp()).upper()
        n = max(2, math.ceil(math.log(4 * float(MF) / ((rho - 1) * V.TOL_F)) / math.log(rho)))
        return n + n % 2

    try:
        r = run_row(arb(10) ** 5)
        try:
            old_n(arb(10) ** 5)
            old = "v5.1's expression did NOT raise"
        except OverflowError:
            old = "v5.1's expression raises OverflowError"
        json.dumps(r)                                      # prove writes the row with json.dumps
        record("T5a runaway M_F rejected, no exception", "rejected" in r and r["rejected"].startswith("n > 40")
               and old.endswith("raises OverflowError"), f"{r.get('rejected')}; {old}; row serialises")
    except Exception as e:
        record("T5a runaway M_F rejected, no exception", False, f"{type(e).__name__}: {e}"[:160])
    try:
        D = D_for("40.5")
        r = run_row(D)
        record("T5b n = 42 rejected by the second branch", r.get("rejected", "").startswith("n = 42 > 40")
               and old_n(D) == 42, f"{r.get('rejected')}; v5.1 n {old_n(D)}")
    except Exception as e:
        record("T5b n = 42 rejected by the second branch", False, f"{type(e).__name__}: {e}"[:160])
    try:
        D = D_for("20.3")
        r = run_row(D)
        record("T5c control: n = 22 admitted, equal to v5.1's", "rejected" not in r and r["n"] == old_n(D) == 22,
               f"n {r.get('n')}, v5.1 n {old_n(D)}, rejected {r.get('rejected')}")
    except Exception as e:
        record("T5c control: n = 22 admitted, equal to v5.1's", False, f"{type(e).__name__}: {e}"[:160])

print("T2-T4 RESULT:", "PASS" if all(ok for _, ok in RES) else "FAIL", f"({sum(ok for _, ok in RES)}/{len(RES)})")
sys.exit(0 if all(ok for _, ok in RES) else 1)
