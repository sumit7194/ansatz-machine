#!/usr/bin/env python3
"""Route (i) production driver for one spin (registration §5, Sumit's scope 2026-11-27). [ansatz-machine-personal,
2026-11-27; NOT yet read or tested]

SCOPE (fixed before launch): the measured reach only. The certified range is to be [eps_a, TOP] at that spin:
  - a DOWNWARD chain of dyadic segments [0.1/2^m, 0.1/2^(m-1)], m = 1, 2, ... until the lower end is <= eps_a, in
    mode Fk2 (F/k^2, §4.2);
  - then an UPWARD chain of 0.1-wide segments [0.1, 0.2], [0.2, 0.3], ... up to TOP, in mode F.
The two chains meet at k = 0.1. The top of region A is parked and not attempted.

PER SEGMENT, one child process at a time (the driver itself only waits):
  1. floats at k_c (the 50-digit engine, .venv / Python 3.14): the lasso and singular points of k_c, and F(k_c),
     which steers n. Skipped when the floats file already holds k_c. geometry_ok must be True, or the run STOPS.
  2. v6 prove (.venv313 / Python 3.13, R1_RHOS=4). Any non-zero exit (a gate: F1, F2, F3, B1) STOPS the run. No
     admissible row (n > 40 or a refused box) -> split.
  3. v6 verdict (R1_FULLCTL=1 on the first 0.1-wide segment, [0.1, 0.2], depth 0). Exit 3 (ALARM: a control failed)
     STOPS the run. not_certified -> split. certified -> 4.
  4. The engine gate at every node (.venv). A miss (exit 2) STOPS the run. All inside -> the segment is CERTIFIED.
SPLIT RULE (§5.4) with the STOP RULE (Sumit, 2026-11-27): a segment that has no admissible row or is not certified is
halved, down to depth DMAX. A failure the verdict marks radius_limited (the node balls, not the interpolation bound,
block it; splitting cannot cure that) stops its chain at once, without splitting (default 2, i.e. a 0.1-wide segment down to 0.025). A segment that still fails at depth DMAX
STOPS ITS CHAIN: the reach achieved is reported, and the other chain still runs. No new code mid-run.
END: the verdict stage is rerun for every certified segment from its node file; each verdict JSON must be byte-identical
(sha256) and need no new evaluation (§6, per batch). Then the reach is reported: [lowest contiguous certified lower end of
the downward chain, highest contiguous certified upper end of the upward chain].
STATE: one fsynced jsonl line per segment outcome (route1_prod_<spin>_state.jsonl); a rerun resumes, replaying recorded
splits and skipping certified segments; every stage resumes from its own checkpoints.
Environment: NVE_SPIN, R1_R0, PROD_TOP, PROD_EPS, PROD_DMAX (2), PY313, PY314 (interpreter paths).
    PY313=.venv313/bin/python PY314=.venv/bin/python NVE_SPIN=3/5 R1_R0=1.35 PROD_TOP=3 PROD_EPS=1.92e-3 \
        .venv313/bin/python -I -u scripts/_nve_route1_production.py"""
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


# ------------------------------------------------------------------ the real stages (replaced in the driver test U5)
def env_for(lo, hi, mode, fullctl):
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


def v6_paths(env):
    out = subprocess.run([os.environ["PY313"], "-I", "-c", "import sys; sys.path.insert(0, 'scripts'); "
                          "import _nve_route1_segment_v6 as S; print(S.BASE); print(S.S5.MJSON); print(S.NODEF); "
                          "print(S.VJSON)"], env=env, cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        raise Stop(f"v6 import failed: {out.stderr[-300:]}")
    return out.stdout.split()


class Real:
    def stage(self, lo, hi, mode, fullctl):
        """-> ('certified', info) | ('split', reason); raises Stop on a gate, an alarm or an engine miss."""
        env = env_for(lo, hi, mode, fullctl)
        kc = env["R1_KC"]
        fl = os.path.join(OUTD, FLOATS)
        if not (os.path.exists(fl) and kc in json.load(open(fl))):
            if run([os.environ["PY314"], "-I", "-u", "scripts/_nve_route1_floats.py", kc], env, f"floats k_c {kc}"):
                raise Stop(f"floats failed at k_c {kc}")
        if not json.load(open(fl))[kc]["geometry_ok"]:
            raise Stop(f"floats geometry_ok False at k_c {kc}")
        base, mjson, nodef, vjson = v6_paths(env)
        rc = run([os.environ["PY313"], "-I", "-u", "scripts/_nve_route1_segment_v6.py", "prove"], env, f"prove {base}")
        if rc:
            raise Stop(f"prove exited {rc} at {segkey(lo, hi)} (a gate fired)")
        J = json.load(open(mjson))
        if J["chosen"] is None:
            return "split", "no admissible row: " + "; ".join(str(r.get("rejected")) for r in self.rows(base))
        rc = run([os.environ["PY313"], "-I", "-u", "scripts/_nve_route1_segment_v6.py", "verdict"], env, f"verdict {base}")
        if rc == 3:
            raise Stop(f"verdict ALARM at {segkey(lo, hi)}: {json.load(open(vjson)).get('alarm')}")
        if rc:
            raise Stop(f"verdict exited {rc} at {segkey(lo, hi)}")
        Vd = json.load(open(vjson))
        if Vd["outcome"] != "certified":
            if Vd.get("radius_limited"):
                return "radius_limited", (f"not certified and node-radius limited (largest node radius "
                                          f"{Vd['node_radius_max']}, smallest |f| {Vd['node_abs_min']}): splitting cannot help")
            return "split", f"not certified: {Vd['conditions']}"
        gate = os.path.join(OUTD, f"route1_seg_engine_{base}.jsonl")
        rc = run([os.environ["PY314"], "-I", "-u", "scripts/_nve_route1_engine_gate.py"],
                 dict(env, NODES=nodef, FLOATS=fl, OUTJ=gate), f"engine gate {base}")
        if rc:
            raise Stop(f"engine gate exited {rc} at {segkey(lo, hi)} (2 = a node value outside its enclosure)")
        return "certified", dict(base=base, n=J["chosen"]["n"], abs_f_ge=Vd["abs_f_ge"], abs_F_ge=Vd.get("abs_F_ge"),
                                 vjson_sha=hashlib.sha256(open(vjson, "rb").read()).hexdigest(), vjson=vjson,
                                 nodef=nodef, nodes_sha=hashlib.sha256(open(nodef, "rb").read()).hexdigest())

    def rows(self, base):
        p = os.path.join(OUTD, f"route1_seg_{base}_rows.jsonl")
        return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []

    def rerun_verdict(self, lo, hi, mode, fullctl, info):
        env = env_for(lo, hi, mode, fullctl)
        rc = run([os.environ["PY313"], "-I", "-u", "scripts/_nve_route1_segment_v6.py", "verdict"], env,
                 f"batch rerun {info['base']}")
        same = (rc == 0 and hashlib.sha256(open(info["vjson"], "rb").read()).hexdigest() == info["vjson_sha"]
                and hashlib.sha256(open(info["nodef"], "rb").read()).hexdigest() == info["nodes_sha"])   # no new evaluation
        return same


# ------------------------------------------------------------------ the driver
def chain(name, segs, mode, st, S, fullctl_seg):
    """Process one chain in order with the split and stop rules. -> list of certified (lo, hi), stopped (bool)."""
    certified, stack = [], [(lo, hi, 0) for lo, hi in reversed(segs)]
    while stack:
        lo, hi, depth = stack.pop()
        key = segkey(lo, hi)
        r = st.get(key)
        if r and r["outcome"] == "certified":
            certified.append((lo, hi))
            continue
        if r and r["outcome"] == "split":
            stack += [(lo + (hi - lo) / 2, hi, depth + 1), (lo, lo + (hi - lo) / 2, depth + 1)][::(1 if name == "up" else -1)]
            continue
        if r and r["outcome"] == "chain_stopped":
            return certified, True
        t0 = time.time()
        say(f"{name} chain: segment [{lo}, {hi}] (k_c {(lo + hi) / 2}, depth {depth}, mode {mode})")
        outcome, info = S.stage(lo, hi, mode, (lo, hi, depth) == fullctl_seg)
        rec = dict(seg=key, lo=str(lo), hi=str(hi), depth=depth, mode=mode, chain=name, outcome=outcome,
                   sec=round(time.time() - t0))
        if outcome == "certified":
            rec.update(info)
            record(rec)
            st[key] = rec
            certified.append((lo, hi))
            say(f"  CERTIFIED [{lo}, {hi}]: n = {info['n']}, |f| >= {info['abs_f_ge']}  ({rec['sec']} s)")
        elif outcome == "radius_limited":
            rec.update(outcome="chain_stopped", reason=info)
            record(rec)
            st[key] = rec
            say(f"  STOP RULE (radius-limited): [{lo}, {hi}]: {info}; the {name} chain stops here without splitting")
            return certified, True
        elif depth < DMAX:
            rec.update(outcome="split", reason=info)
            record(rec)
            st[key] = rec
            say(f"  SPLIT [{lo}, {hi}] at depth {depth}: {info}")
            # the halves, in chain order (the upward chain takes the lower half first, the downward one the upper)
            stack += [(lo + (hi - lo) / 2, hi, depth + 1), (lo, lo + (hi - lo) / 2, depth + 1)][::(1 if name == "up" else -1)]
        else:
            rec.update(outcome="chain_stopped", reason=info)
            record(rec)
            st[key] = rec
            say(f"  STOP RULE: [{lo}, {hi}] fails at depth {depth} = DMAX ({info}); the {name} chain stops here")
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
    try:
        dc, dstop = chain("down", down, "Fk2", st, S, None)
        uc, ustop = chain("up", up, "F", st, S, (Q(1, 10), Q(2, 10), 0))
    except Stop as e:
        say(f"STOPPED (correctness gate or alarm): {e}")
        record(dict(seg="RUN", outcome="stopped", reason=str(e)))
        return 2
    lo, hi = reach(dc, uc)
    say(f"chains done: down {'STOPPED by the stop rule' if dstop else 'complete'} ({len(dc)} certified), "
        f"up {'STOPPED by the stop rule' if ustop else 'complete'} ({len(uc)} certified)")
    same_all = True
    for key, r in sorted(load_state().items()):
        if r.get("outcome") == "certified":
            fullctl = (Q(r["lo"]), Q(r["hi"]), r["depth"]) == (Q(1, 10), Q(2, 10), 0)
            same = S.rerun_verdict(Q(r["lo"]), Q(r["hi"]), r["mode"], fullctl, r)
            same_all &= same
            if not same:
                say(f"  BATCH RERUN DIFFERS at {key}")
    say(f"batch rerun of every certified verdict: byte-identical {same_all}")
    covers = lo <= eps and hi >= top
    say(f"REACH: certified contiguous [{lo}, {hi}] = [{float(lo):.4e}, {float(hi)}]; covers the target "
        f"[eps_a, {top}]: {covers}")
    record(dict(seg="RUN", outcome="done", reach=[str(lo), str(hi)], covers_target=covers, batch_identical=same_all,
                down_stopped=dstop, up_stopped=ustop))
    return 0 if same_all else 2


def pilot(lo, hi, mode):
    """One segment through the real stages, outside the production state (pilot P4). Production later reuses its
    checkpoints (same code hash, same file names): the stages resume, and no evaluation is repeated."""
    lo, hi = Q(lo), Q(hi)
    say(f"== pilot == spin {SPIN}; segment [{lo}, {hi}] (k_c {(lo + hi) / 2}), mode {mode}")
    try:
        outcome, info = Real().stage(lo, hi, mode, False)
    except Stop as e:
        say(f"PILOT STOPPED: {e}")
        return 2
    say(f"PILOT OUTCOME: {outcome}; {info}")
    return 0


if __name__ == "__main__":
    sys.exit(pilot(*sys.argv[2:5]) if sys.argv[1:2] == ["pilot"] else main())
