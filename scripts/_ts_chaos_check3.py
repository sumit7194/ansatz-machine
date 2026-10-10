#!/usr/bin/env python3
"""Third, report-only check on the chaos detections (section 150): a harmonic-proof frequency drift from the COMPLEX
section signal z = (x - <x>)/sx + i (p_x - <p_x>)/sp. A regular orbit on a torus winds around its section curve with
one rotation number. The dominant peak of the complex spectrum is that winding frequency, which removes the
fundamental/harmonic ambiguity of the real-signal estimator (amendment 6). Drift = |f1 - f2| / |f_avg| between halves.
Runs at tol 1e-13 with an uncapped budget. Saves the section points for figures.
    .venv/bin/python scripts/_ts_chaos_check3.py
"""
import json
import os
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

from _ts_chaos_scan import PLUNGE_X, SYSTEMS, _engine  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "ts_chaos")


def complex_drift(xs, ps):
    def dom(zx, zp):
        z = (zx - zx.mean()) / (zx.std() + 1e-30) + 1j * (zp - zp.mean()) / (zp.std() + 1e-30)
        n = len(z)
        F = np.abs(np.fft.fft(z * np.hanning(n)))
        F[0] = 0.0
        k = int(np.argmax(F))
        a, b, c = F[(k - 1) % n], F[k], F[(k + 1) % n]
        d = 0.5 * (a - c) / (a - 2 * b + c + 1e-30)
        f = (k + d) / n
        return f if f <= 0.5 else f - 1.0          # signed winding frequency
    xs, ps = np.asarray(xs), np.asarray(ps)
    h = len(xs) // 2
    f1, f2 = dom(xs[:h], ps[:h]), dom(xs[h:], ps[h:])
    return abs(f1 - f2) / (0.5 * abs(f1 + f2) + 1e-30)


def _job(a):
    sysname, label, E, L, x0 = a
    spec, m, x_in = SYSTEMS[sysname]
    import _ts_chaos_scan as S
    eng = _engine(spec)
    r = eng.orbit(x0, E, L, nsec=300, tmax=5e6, xmin=max(x_in, PLUNGE_X), xmax=2000.0, tol=1e-13, maxsteps=30_000_000)
    if r is None:
        return dict(system=sysname, label=label, E=E, L=L, x0=x0, n=0, status=-1, fd=float("nan"), sex=float("nan"),
                    cdrift=float("nan"), secx=[], secpx=[], note="forbidden start (p_y^2 < 0)")
    cd = complex_drift(r["secx"], r["secpx"]) if r["n"] >= 100 else float("nan")
    return dict(system=sysname, label=label, E=E, L=L, x0=x0, n=r["n"], status=r["status"], fd=r["fd"], sex=r["sex"],
                cdrift=float(cd), secx=list(map(float, r["secx"])), secpx=list(map(float, r["secpx"])))


def main():
    jobs = []
    for s in ("ts45", "ts35", "kerr45", "kerr35"):
        for c in json.load(open(os.path.join(D, f"bscan_{s}_v2_confirm.json"))):
            if s.startswith("ts") and c["verdict"] != "CONFIRMED":
                continue
            lab = ("TS-confirmed" + ("-SUSPECT-flip" if 0.55 < c["fd13"] < 0.8 else "")) if s.startswith("ts") else "Kerr-candidate"
            jobs.append((s, lab, c["E"], c["L"], c["x0"]))
    for L, x0, lab in ((2.9, 7.56263, "ZV-layer"), (3.0, 7.57274, "ZV-layer"), (3.0, 7.62, "ZV-torus"), (3.0, 7.557, "ZV-island")):
        jobs.append(("zv2", lab, 0.95, L, x0))
    with Pool(7) as pool:
        out = pool.map(_job, jobs, chunksize=1)
    json.dump(out, open(os.path.join(D, "check3.json"), "w"))
    for lab in ("ZV-layer", "ZV-torus", "ZV-island", "Kerr-candidate", "TS-confirmed", "TS-confirmed-SUSPECT-flip"):
        v = [o["cdrift"] for o in out if o["label"] == lab and o["cdrift"] == o["cdrift"]]
        if v:
            print(f"  {lab:28s} n={len(v):3d}  complex-drift median {np.median(v):.4f}  min {min(v):.4f}  max {max(v):.4f}  "
                  f"frac > 0.0115: {np.mean(np.array(v) > 0.0115):.2f}", flush=True)


if __name__ == "__main__":
    main()
