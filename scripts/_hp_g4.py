#!/usr/bin/env python3
"""G4 of the high-precision probe (HP_PREREGISTRATION.md addendum 2): full-state agreement at a FIXED proper time T
between DD at R2 (tol 1e-28) and mpmath at 50 digits (tol 1e-40). 2 Kerr probe x0 at T = 2400; the first STABLE and the
first SENSITIVE TS x0 at T = 4000. Pass: max relative state difference <= 1e-20 for Kerr and the stable TS; the
sensitive TS value is reported (informative).
    .venv/bin/python scripts/_hp_g4.py        (needs the `select` phase done; ~1 core, slow: mpmath)
"""
import json
import os
import sys
import time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpmath as mp  # noqa: E402

import _hp_dd as H  # noqa: E402
import _hp_probe as P  # noqa: E402


def main():
    sens, stab, kerr = P.probe_set()
    cases = [("kerr", kerr[0][1]["x0"], 2400.0, True), ("kerr", kerr[1][1]["x0"], 2400.0, True),
             ("ts", stab[0][1]["x0"], 4000.0, True), ("ts", sens[0][1]["x0"], 4000.0, False)]
    out = []
    ok = True
    for sys_, x0, T, gated in cases:
        lv = P.LEV[sys_]
        d = H.DDEngine(lv["spec"])
        m = H.MPEngine(lv["spec"], dps=50)
        mp.mp.dps = 50
        t0 = time.time()
        sh, sl = H.dd_state_at(d, x0, lv["E"], lv["L"], T, tol=1e-28)
        A = [mp.mpf(a) + b for a, b in zip(sh, sl)]
        M = H.mp_state_at(m, x0, lv["E"], lv["L"], T, tol=1e-40)
        rel = float(max(abs(a - b) / (1 + abs(b)) for a, b in zip(A, M)))
        passed = rel <= 1e-20
        if gated:
            ok &= passed
        rec = dict(sys=sys_, x0=x0, T=T, gated=gated, rel=rel, seconds=round(time.time() - t0))
        out.append(rec)
        print(f"  G4 {sys_} x0={x0:.9f} T={T}: DD-R2 vs MP50 max rel state diff {rel:.2e}  "
              f"{'(gate) ' + ('PASS' if passed else 'FAIL') if gated else '(sensitive TS: informative)'}  [{rec['seconds']}s]",
              flush=True)
        json.dump(out, open(os.path.join(P.OUT, "g4.json"), "w"), indent=1)
    print(f"VERDICT-G4: {'PASS' if ok else 'FAIL'}", flush=True)


if __name__ == "__main__":
    main()
