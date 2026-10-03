#!/usr/bin/env python3
"""Overnight queue for the TS δ=2 p=4/5 exact rungs (data/ts2_exact/PREREGISTRATION.md, sealed at 788dcc9).

Runs G1 (controls) -> G2 (TS ranks 2, 3) -> G3 (TS rank 4), each on BOTH primes, one job at a time, and scores every
VERDICT line against the pre-registered prediction. Stop rules exactly as pre-registered:
  control mismatch -> STOP;  prime disagreement -> STOP;  condemned / crashed -> STOP;
  TS irreducible > 0 -> finish that configuration's second prime, then STOP (report; no claim).
G4 (rank 6) is NOT queued here: it needs G3's measured size first, and a human-checked go.
Detached use:  nohup .venv/bin/python -u scripts/ts2_exact_queue.py > data/ts2_exact/queue.log 2>&1 &
"""
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = "data/ts2_exact"
INBOX = "/Users/sumit/Github/.claude-coordination/inbox/bridge"
PY = ".venv/bin/python"
THREADS = os.environ.get("THREADS", "2")

# (gate, label, metric, rank, denpow, predicted (exact, reducible, irreducible), is_target)
QUEUE = [
    ("G1", "kerr_r2", "ts2kerr:4/5", 2, 1, (5, 4, 1), False),
    ("G1", "kerr_r3", "ts2kerr:4/5", 3, 1, (8, 6, 2), False),
    ("G1", "kerr_r4", "ts2kerr:4/5", 4, 2, (14, 9, 5), False),
    ("G1", "zv2_r4", "zv:2", 4, 2, (9, 9, 0), False),
    ("G2", "ts_r2", "ts2:4/5", 2, 1, (4, 4, 0), True),
    ("G2", "ts_r3", "ts2:4/5", 3, 1, (6, 6, 0), True),
    ("G3", "ts_r4", "ts2:4/5", 4, 2, (9, 9, 0), True),
]


def log(msg):
    line = f"[{time.strftime('%a %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(f"{OUT}/STATUS.md", "a") as fh:
        fh.write(line + "\n")


def inbox(topic, text):
    os.makedirs(INBOX, exist_ok=True)
    with open(f"{INBOX}/{time.strftime('%Y-%m-%d')}_ansatz_ts2exact_{topic}.md", "w") as fh:
        fh.write(text + "\n")


def run(label, metric, rank, denpow, prime):
    out = f"{OUT}/{label}_p{prime}.out"
    if os.path.exists(out) and "VERDICT" in open(out).read():
        log(f"  {label} p{prime}: already complete, reusing {out}")
    else:
        cmd = (f"exec {PY} -u scripts/_kt_exact_op.py --metric {metric} --rank {rank} --denpow {denpow} "
               f"--prime {prime} > '{out}' 2>&1")
        env = dict(os.environ, KT_SOLVER="rust", KT_THREADS=THREADS)
        t0 = time.time()
        with open(out + ".time", "w") as tf:
            proc = subprocess.Popen(["/usr/bin/time", "-l", "bash", "-c", cmd], env=env, stderr=tf,
                                    stdin=subprocess.DEVNULL)
            with open(f"{OUT}/PIDS", "a") as pf:
                pf.write(f"{proc.pid} {label} p{prime} {time.strftime('%F %T')} {cmd}\n")
            rc = proc.wait()
        mins = (time.time() - t0) / 60
        fp = re.search(r"(\d+)\s+peak memory footprint", open(out + ".time").read())
        log(f"  {label} p{prime}: exit {rc}, {mins:.1f} min, peak footprint "
            f"{int(fp.group(1)) / 2**30:.2f} GB" if fp else f"  {label} p{prime}: exit {rc}, {mins:.1f} min")
    m = re.search(r"VERDICT .*: exact (\d+), reducible (\d+), IRREDUCIBLE (-?\d+)", open(out).read())
    return tuple(int(v) for v in m.groups()) if m else None


def main():
    log(f"=== ts2_exact_queue start, driver pid {os.getpid()}, threads {THREADS}; predictions sealed at "
        f"{subprocess.run(['git', 'log', '-1', '--format=%h', '--', f'{OUT}/PREREGISTRATION.md'], capture_output=True, text=True).stdout.strip()}")
    if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", f"{OUT}/PREREGISTRATION.md"]).returncode:
        log("REFUSE: PREREGISTRATION.md has uncommitted edits"); return 4
    results = {}
    gate_done = None
    for gate, label, metric, rank, denpow, pred, target in QUEUE:
        if gate_done and gate != gate_done:
            inbox(gate_done, f"ansatz: gate {gate_done} passed. Results so far: {json.dumps(results)}. See {OUT}/STATUS.md.")
            log(f"--- gate {gate_done} PASSED")
        gate_done = gate
        v0 = run(label, metric, rank, denpow, 0)
        v1 = run(label, metric, rank, denpow, 1)
        results[label] = {"p0": v0, "p1": v1, "predicted": pred}
        if v0 is None or v1 is None:
            log(f"STOP: {label} produced no verdict (crash or condemned) -- see {OUT}/{label}_p*.out")
            inbox("STOP", f"ansatz: STOP at {label}: no verdict. {json.dumps(results)}"); return 3
        if v0 != v1:
            log(f"STOP: prime disagreement at {label}: {v0} vs {v1}")
            inbox("STOP", f"ansatz: STOP at {label}: primes disagree {v0} vs {v1}"); return 3
        verdict = "MATCH" if v0 == pred else "MISMATCH"
        log(f"{gate} {label}: exact/reducible/irreducible = {v0} (both primes), predicted {pred} -> {verdict}")
        if target and v0[2] > 0:
            log(f"STOP: TS IRREDUCIBLE {v0[2]} at {label} on both primes. No claim; awaiting the Bridge's check.")
            inbox("POSITIVE", f"ansatz: TS irreducible {v0[2]} at {label} (both primes). STOPPED, no claim. {json.dumps(results)}")
            return 0
        if verdict == "MISMATCH":
            log(f"STOP: {label} does not match its prediction ({'control' if not target else 'target'})")
            inbox("STOP", f"ansatz: STOP at {label}: {v0} vs predicted {pred}. {json.dumps(results)}"); return 3
    log(f"--- gate {gate_done} PASSED")
    inbox("G3_done", f"ansatz: G1-G3 all MATCH on both primes. {json.dumps(results)}. G4 (rank 6) awaits a size check.")
    with open(f"{OUT}/results.json", "w") as fh:
        json.dump(results, fh, indent=1)
    log("=== queue finished: all predictions matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
