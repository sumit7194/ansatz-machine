"""Driver for the Part A runs (one process at a time, nice 12). Each run writes its own .out; reruns skip finished ones.
[model: Fable 5.2]"""
import os, subprocess, sys
PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RUNS = [("3/10", {}, "eps_3_10"), ("3/5", {}, "eps_3_5"), ("4/5", {}, "eps_4_5"), ("9/10", {}, "eps_9_10"),
        ("227/250", {"EPS_R0": "1.30"}, "eps_227_250_CONTROL"),
        ("3/5", {"EPS_REFUSE": "1"}, "eps_3_5_REFUSE_CONTROL"),
        ("3/10", {"EPS_DELTA": "wide", "EPS_TAG": "_wide"}, "eps_3_10_wide"),
        ("3/5", {"EPS_DELTA": "wide", "EPS_TAG": "_wide"}, "eps_3_5_wide"),
        ("4/5", {"EPS_DELTA": "wide", "EPS_TAG": "_wide"}, "eps_4_5_wide"),
        ("9/10", {"EPS_DELTA": "wide", "EPS_TAG": "_wide"}, "eps_9_10_wide")]
for spin, extra, name in RUNS:
    out = os.path.join(HERE, name + ".out")
    if os.path.exists(out) and "VERDICT" in open(out).read():
        print("skip (done):", name, flush=True)
        continue
    env = dict(os.environ, NVE_SPIN=spin, **extra)
    with open(out, "w") as fh:
        subprocess.run(["nice", "-n", "12", PY, "-u", os.path.join(ROOT, "scripts", "_nve_eps_certify.py")], env=env,
                       stdout=fh, stderr=subprocess.STDOUT)
    last = [l for l in open(out).read().splitlines() if l.strip()][-1]
    print(name, "->", last[:230], flush=True)
