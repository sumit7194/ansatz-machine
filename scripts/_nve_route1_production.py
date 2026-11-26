#!/usr/bin/env python3
"""Route (i) production driver for one spin (registration §5, Sumit's scope 2026-11-27). [ansatz-machine-personal,
2026-11-27; read by the Bridge at 10707e1; this version folds in its S1, S2, S7]

SCOPE (fixed before launch): the measured reach only. The certified range is to be [eps_a, TOP] at that spin:
  - a DOWNWARD chain of dyadic segments [0.1/2^m, 0.1/2^(m-1)], m = 1, 2, ... until the lower end is <= eps_a, in
    mode Fk2 (F/k^2, §4.2);
  - then an UPWARD chain of 0.1-wide segments [0.1, 0.2], [0.2, 0.3], ... up to TOP, in mode F.
The two chains meet at k = 0.1. The top of region A is parked and not attempted.

PER SEGMENT, one child process at a time (the driver itself only waits):
  1. floats at k_c (the 50-digit engine, .venv / Python 3.14): the lasso and singular points of k_c, and F(k_c),
     which steers n. Skipped when the floats file already holds k_c. geometry_ok must be True, or the run STOPS.
  2. v6 prove (.venv313 / Python 3.13, R1_RHOS=4). Any non-zero exit (a gate: F1, F2, F3, B1) STOPS the run. No
     admissible row (n > 40, a refused box, R >= k_c in F/k^2) -> split.
  3. v6 verdict. Exit 3 (ALARM: a control failed) STOPS the run. not_certified -> split (or, if radius_limited, the
     chain stops). certified -> on the FIRST certified segment of each mode (S2) the verdict runs again with the full
     controls (R1_FULLCTL=1), which must also certify -> 4.
  4. The engine gate at every node (.venv). A miss (exit 2) STOPS the run. All inside -> the segment is CERTIFIED.
SPLIT RULE (§5.4) with the STOP RULE (Sumit, 2026-11-27): a segment that has no admissible row or is not certified is
halved, down to depth DMAX (default 2: a 0.1-wide segment down to 0.025). A segment that still fails at depth DMAX
STOPS ITS CHAIN. A failure the verdict marks radius_limited (a condition fails even with zero interpolation error, so
splitting cannot cure it) stops its chain at once. A stopped chain is reported; the other chain still runs. No new code
mid-run.
S1 (the Bridge's read): every state record carries the v6 code base (file names + code hash) its stages used. A resume
recomputes the base for every record and STOPS on a mismatch (a record from other code is never trusted). The batch
rerun recomputes the paths, asserts they equal the record's, reruns the verdict with the same controls, and requires a
byte-identical verdict JSON and an unchanged node file (no new evaluation). The reach and covers_target are computed
ONLY from segments whose rerun is identical.
END: S2's assertion (one full-controls pass per mode used), the batch rerun, then the reach: [lowest contiguous
certified lower end of the downward chain, highest contiguous certified upper end of the upward chain].
STATE: one fsynced jsonl line per segment outcome (route1_prod_<spin>_state.jsonl); a rerun resumes, replaying recorded
splits and skipping certified segments; every stage resumes from its own checkpoints. A correctness STOP is recorded,
and a rerun refuses to resume it without a decision.
Environment: NVE_SPIN, R1_R0, PROD_TOP, PROD_EPS, PROD_DMAX (2), PY313, PY314 (interpreter paths).
    PY313=.venv313/bin/python PY314=.venv/bin/python NVE_SPIN=3/5 R1_R0=1.35 PROD_TOP=3 PROD_EPS=1.92e-3 \
        .venv313/bin/python -I -u scripts/_nve_route1_production.py
    ... _nve_route1_production.py pilot <lo> <hi> <F|Fk2>      one segment, outside the production state"""
import hashlib
import json
import os
import subprocess
import sys
import time
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTD = os.path.join(ROOT, "data", "nve", "eps")
SPIN = os.environ.get("NVE_SPIN", "3/5")
TAGS = SPIN.replace("/", "_")
FLOATS = f"route1_floats_prod_{TAGS}.json"
STATE = os.path.join(OUTD, f"route1_prod_{TAGS}_state.jsonl")
LOG = os.path.join(OUTD, f"route1_prod_{TAGS}.out")
DMAX = int(os.environ.get("PROD_DMAX", "2"))


def say(s):
    line = f"[{time.strftime('%F %T')}] {s}"
    print(line, flush=True)
    with open(LOG, "a") as fh:
        fh.write(line + "\n")


def plan(eps, top):
    """(downward dyadic chain, upward 0.1 chain): lists of (lo, hi) as exact Fractions."""
    down, m = [], 1
    while True:
        lo, hi = Q(1, 10) / 2 ** m, Q(1, 10) / 2 ** (m - 1)
        down.append((lo, hi))
        if lo <= eps:
            break
        m += 1
    up, lo = [], Q(1, 10)
    while lo + Q(1, 10) <= top:
        up.append((lo, lo + Q(1, 10)))
        lo += Q(1, 10)
    return down, up


def segkey(lo, hi):
    return f"{lo}..{hi}"


def load_state():
    st = {}
    if os.path.exists(STATE):
        for ln in open(STATE):
            if ln.strip():
                r = json.loads(ln)
                st[r["seg"]] = r
    return st


def record(r):
    with open(STATE, "a") as fh:
        fh.write(json.dumps(r) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


class Stop(Exception):
    """A correctness gate or alarm: the whole run stops here."""


def halves(lo, hi, depth, name):
    """The two halves, pushed so that the upward chain takes the lower half first and the downward chain the upper."""
    mid = lo + (hi - lo) / 2
    hs = [(mid, hi, depth + 1), (lo, mid, depth + 1)]
    return hs if name == "up" else hs[::-1]


# ------------------------------------------------------------------ the real stages (replaced in the driver test U5)
def env_for(lo, hi, mode, fullctl=False):
    kc, half = (lo + hi) / 2, (hi - lo) / 2
    e = dict(os.environ, R1_KC=str(kc), R1_HALF=str(half), R1_FLOATS=FLOATS, R1_RHOS="4", R1_MODE=mode,
             R1_TOLMODE="rel")
    e.pop("R1_FULLCTL", None)
    if fullctl:
        e["R1_FULLCTL"] = "1"
    return e


def run(cmd, env, label):
    with open(LOG, "a") as fh:
        fh.write(f"--- {label}: {' '.join(cmd[-2:])}\n")
        fh.flush()
        p = subprocess.run(cmd, env=env, stdout=fh, stderr=subprocess.STDOUT, cwd=ROOT)
    return p.returncode


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


class Real:
    def paths(self, lo, hi, mode):
        """v6's (base, proof JSON, node file, verdict JSON) for this segment, as v6 itself computes them (its code hash
        included). The floats entry of k_c must exist (it enters the hash)."""
        out = subprocess.run([os.environ["PY313"], "-I", "-c", "import sys; sys.path.insert(0, 'scripts'); "
                              "import _nve_route1_segment_v6 as S; print(S.BASE); print(S.S5.MJSON); print(S.NODEF); "
                              "print(S.VJSON)"], env=env_for(lo, hi, mode), cwd=ROOT, capture_output=True, text=True)
        if out.returncode != 0:
            raise Stop(f"v6 import failed: {out.stderr[-300:]}")
        return out.stdout.split()

    def base_of(self, lo, hi, mode):
        return self.paths(lo, hi, mode)[0]

    def stage(self, lo, hi, mode, want_full):
        """-> (outcome, info). outcome 'certified' | 'split' | 'radius_limited'; info always has 'base'. Raises Stop on a
        gate, an alarm, bad floats or an engine miss."""
        env = env_for(lo, hi, mode)
        kc = env["R1_KC"]
        fl = os.path.join(OUTD, FLOATS)
        if not (os.path.exists(fl) and kc in json.load(open(fl))):
            if run([os.environ["PY314"], "-I", "-u", "scripts/_nve_route1_floats.py", kc], env, f"floats k_c {kc}"):
                raise Stop(f"floats failed at k_c {kc}")
        if not json.load(open(fl))[kc]["geometry_ok"]:
            raise Stop(f"floats geometry_ok False at k_c {kc}")
        base, mjson, nodef, vjson = self.paths(lo, hi, mode)
        rc = run([os.environ["PY313"], "-I", "-u", "scripts/_nve_route1_segment_v6.py", "prove"], env, f"prove {base}")
        if rc:
            raise Stop(f"prove exited {rc} at {segkey(lo, hi)} (a gate fired)")
        J = json.load(open(mjson))
        if J["chosen"] is None:
            return "split", dict(base=base, reason="no admissible row: " + "; ".join(str(r.get("rejected")) for r in J["rows"]
                                                                                 or self.rows(base)))
        for full in ((False, True) if want_full else (False,)):
            rc = run([os.environ["PY313"], "-I", "-u", "scripts/_nve_route1_segment_v6.py", "verdict"],
                     env_for(lo, hi, mode, full), f"verdict{' (full controls)' if full else ''} {base}")
            if rc == 3:
                raise Stop(f"verdict ALARM at {segkey(lo, hi)}: {json.load(open(vjson)).get('alarm')}")
            if rc:
                raise Stop(f"verdict exited {rc} at {segkey(lo, hi)}")
            Vd = json.load(open(vjson))
            if Vd["outcome"] != "certified":
                if full:
                    raise Stop(f"the full-controls verdict at {segkey(lo, hi)} did not certify a segment the normal one did")
                if Vd.get("radius_limited"):
                    return "radius_limited", dict(base=base, reason=f"not certified; fails even with zero interpolation "
                                                  f"error for {Vd['unsplittable']} (largest node radius "
                                                  f"{Vd['node_radius_max']}, smallest |f| {Vd['node_abs_min']})")
                return "split", dict(base=base, reason=f"not certified: {Vd['conditions']}")
        gate = os.path.join(OUTD, f"route1_seg_engine_{base}.jsonl")
        rc = run([os.environ["PY314"], "-I", "-u", "scripts/_nve_route1_engine_gate.py"],
                 dict(env, NODES=nodef, FLOATS=fl, OUTJ=gate, R1_CODE=base.rsplit("_", 1)[1]), f"engine gate {base}")
        if rc:
            raise Stop(f"engine gate exited {rc} at {segkey(lo, hi)} (2 = a node value outside its enclosure)")
        return "certified", dict(base=base, n=J["chosen"]["n"], abs_f_ge=Vd["abs_f_ge"], abs_F_ge=Vd.get("abs_F_ge"),
                                 fullctl=bool(want_full), vjson=vjson, vjson_sha=sha(vjson), nodef=nodef,
                                 nodes_sha=sha(nodef), mjson=mjson)

    def rows(self, base):
        p = os.path.join(OUTD, f"route1_seg_{base}_rows.jsonl")
        return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []

    def rerun_verdict(self, lo, hi, mode, r):
        """S1: recompute the paths (they must equal the record's), rerun the verdict with the record's controls, and
        require a byte-identical verdict JSON and an unchanged node file."""
        base, mjson, nodef, vjson = self.paths(lo, hi, mode)
        if (base, nodef, vjson) != (r["base"], r["nodef"], r["vjson"]):
            return False, "paths differ from the record"
        rc = run([os.environ["PY313"], "-I", "-u", "scripts/_nve_route1_segment_v6.py", "verdict"],
                 env_for(lo, hi, mode, r["fullctl"]), f"batch rerun {base}")
        if rc:
            return False, f"verdict rerun exited {rc}"
        if sha(vjson) != r["vjson_sha"]:
            return False, "verdict JSON differs"
        if sha(nodef) != r["nodes_sha"]:
            return False, "node file changed (a new evaluation)"
        return True, "identical"


# ------------------------------------------------------------------ the driver
def chain(name, segs, mode, st, S, full_done):
    """Process one chain in order with the split and stop rules. -> certified records (in order), stopped (bool)."""
    certified, stack = [], [(lo, hi, 0) for lo, hi in reversed(segs)]
    while stack:
        lo, hi, depth = stack.pop()
        key = segkey(lo, hi)
        r = st.get(key)
        if r:                                          # S1: a recorded outcome is trusted only from this code
            b = S.base_of(lo, hi, mode)
            if r.get("base") != b:
                raise Stop(f"state record {key} is from code base {r.get('base')}, not {b}: refusing to resume it")
            if r["outcome"] == "certified":
                certified.append(r)
                full_done[mode] = full_done.get(mode) or r.get("fullctl", False)
                continue
            if r["outcome"] == "split":
                stack += halves(lo, hi, depth, name)
                continue
            if r["outcome"] == "chain_stopped":
                return certified, True
        t0 = time.time()
        want_full = not full_done.get(mode)
        say(f"{name} chain: segment [{lo}, {hi}] (k_c {(lo + hi) / 2}, depth {depth}, mode {mode}"
            f"{', full controls if it certifies' if want_full else ''})")
        outcome, info = S.stage(lo, hi, mode, want_full)
        rec = dict(seg=key, lo=str(lo), hi=str(hi), depth=depth, mode=mode, chain=name, outcome=outcome,
                   sec=round(time.time() - t0), **info)
        if outcome == "certified":
            record(rec)
            st[key] = rec
            certified.append(rec)
            full_done[mode] = full_done.get(mode) or rec["fullctl"]
            say(f"  CERTIFIED [{lo}, {hi}]: n = {info['n']}, |f| >= {info['abs_f_ge']}"
                f"{' (full controls passed)' if rec['fullctl'] else ''}  ({rec['sec']} s)")
        elif outcome == "radius_limited":
            rec.update(outcome="chain_stopped")
            record(rec)
            st[key] = rec
            say(f"  STOP RULE (radius-limited): [{lo}, {hi}]: {info['reason']}; the {name} chain stops here without splitting")
            return certified, True
        elif depth < DMAX:
            rec.update(outcome="split")
            record(rec)
            st[key] = rec
            say(f"  SPLIT [{lo}, {hi}] at depth {depth}: {info['reason']}")
            stack += halves(lo, hi, depth, name)
        else:
            rec.update(outcome="chain_stopped")
            record(rec)
            st[key] = rec
            say(f"  STOP RULE: [{lo}, {hi}] fails at depth {depth} = DMAX ({info['reason']}); the {name} chain stops here")
            return certified, True
    return certified, False


def reach(down_cert, up_cert):
    """Contiguous reach from k = 0.1: down to the lowest lower end, up to the highest upper end, without gaps."""
    lo, hi = Q(1, 10), Q(1, 10)
    for a, b in sorted(down_cert, key=lambda s: -s[1]):
        if b == lo:
            lo = a
    for a, b in sorted(up_cert):
        if a == hi:
            hi = b
    return lo, hi


def main(S=None):
    S = S or Real()
    eps, top = Q(os.environ["PROD_EPS"]), Q(os.environ["PROD_TOP"])
    down, up = plan(eps, top)
    st = load_state()
    if st.get("RUN", {}).get("outcome") == "stopped":
        say(f"REFUSE: this spin's run STOPPED on a correctness gate or alarm ({st['RUN']['reason']}); it is not resumed "
            f"without a decision")
        return 2
    say(f"== route (i) production == spin {SPIN}; target [eps_a = {float(eps):.3e}, {top}]; {len(down)} dyadic (Fk2) + "
        f"{len(up)} 0.1-wide (F) segments; DMAX {DMAX}; {len(st)} outcomes already on disk")
    full_done = {}
    try:
        dc, dstop = chain("down", down, "Fk2", st, S, full_done)
        uc, ustop = chain("up", up, "F", st, S, full_done)
    except Stop as e:
        say(f"STOPPED (correctness gate or alarm): {e}")
        record(dict(seg="RUN", outcome="stopped", reason=str(e)))
        return 2
    say(f"chains done: down {'STOPPED by the stop rule' if dstop else 'complete'} ({len(dc)} certified), "
        f"up {'STOPPED by the stop rule' if ustop else 'complete'} ({len(uc)} certified)")
    # S2: a full-controls pass for every mode that certified anything
    full_ok = all(full_done.get(m) for m, c in (("Fk2", dc), ("F", uc)) if c)
    say(f"full controls passed for every mode used: {full_ok} ({full_done})")
    # S1: the batch rerun; only identical segments count toward the reach
    good = {"down": [], "up": []}
    for r in dc + uc:
        same, why = S.rerun_verdict(Q(r["lo"]), Q(r["hi"]), r["mode"], r)
        if same:
            good[r["chain"]].append((Q(r["lo"]), Q(r["hi"])))
        else:
            say(f"  BATCH RERUN FAILS at {r['seg']}: {why}; the segment does not count toward the reach")
    same_all = len(good["down"]) + len(good["up"]) == len(dc) + len(uc)
    say(f"batch rerun of every certified verdict: identical {same_all}")
    lo, hi = reach(good["down"], good["up"])
    covers = bool(lo <= eps and hi >= top and full_ok and same_all)
    say(f"REACH (identical reruns only): certified contiguous [{lo}, {hi}] = [{float(lo):.4e}, {float(hi)}]; covers the "
        f"target [eps_a, {top}]: {covers}")
    record(dict(seg="RUN", outcome="done", reach=[str(lo), str(hi)], covers_target=covers, batch_identical=same_all,
                full_controls=full_ok, down_stopped=dstop, up_stopped=ustop))
    return 0 if (same_all and full_ok) else 2


def pilot(lo, hi, mode):
    """One segment through the real stages, outside the production state (pilot P4), with the full controls. Production
    later reuses its checkpoints (same code hash, same file names): the stages resume and no evaluation is repeated."""
    lo, hi = Q(lo), Q(hi)
    say(f"== pilot == spin {SPIN}; segment [{lo}, {hi}] (k_c {(lo + hi) / 2}), mode {mode}")
    try:
        outcome, info = Real().stage(lo, hi, mode, True)
    except Stop as e:
        say(f"PILOT STOPPED: {e}")
        return 2
    say(f"PILOT OUTCOME: {outcome}; {info}")
    return 0


if __name__ == "__main__":
    sys.exit(pilot(*sys.argv[2:5]) if sys.argv[1:2] == ["pilot"] else main())
