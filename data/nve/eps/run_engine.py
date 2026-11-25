"""Driver for the engine-consistency control (one process at a time, nice 12). [model: Fable 5.2]"""
import os, subprocess, sys
PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for spin in ("3/5", "3/10", "4/5", "9/10", "227/250"):
    r = subprocess.run(["nice", "-n", "12", PY, "-u", os.path.join(ROOT, "scripts", "_nve_eps_engine_check.py")],
                       env=dict(os.environ, NVE_SPIN=spin), capture_output=True, text=True)
    print((r.stdout + r.stderr)[-1500:], flush=True)
