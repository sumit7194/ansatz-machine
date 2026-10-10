import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")      # one thread per worker: no BLAS/OpenMP oversubscription (the Bridge, load 21 on 10 cores)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import numpy as np
from _ts_chaos_scan import boundary_scan

if __name__ == "__main__":      # multiprocessing spawn re-imports this file in every worker
    Lms = np.round(np.arange(1.0, 3.56, 0.15), 3)
    for sysname in ("kerr45", "ts45", "ts35", "kerr35"):
        boundary_scan(sysname, [0.95, 0.97], Lms, signs=(+1, -1), ndense=200, workers=7, tag="_v2")
    print("ALL DONE", flush=True)
