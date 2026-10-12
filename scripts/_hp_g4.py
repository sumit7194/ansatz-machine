#!/usr/bin/env python3
"""G4 of the high-precision probe (HP_PREREGISTRATION.md addendum 2): full-state agreement at a FIXED proper time T
between DD at R2 (tol 1e-28) and mpmath at 50 digits (tol 1e-40). 2 Kerr probe x0 at T = 2400; the first STABLE and the
first SENSITIVE TS x0 at T = 1000, each the first whose base R2 run survives past T (addendum 3). Pass: max relative state difference <= 1e-20 for Kerr and the stable TS; the
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
    b = P.ck_load("base")
    surv = lambda tag, s, lst, T: [v for i, v in lst if b[f"{tag}:{s}:{i}:R2"]["t_end"] > T]   # addendum 3
    TK, TT = 2400.0, 1000.0
    cases = [("kerr", x["x0"], TK, True) for x in surv("K", "kerr", kerr, TK)[:2]] + \
            [("ts", surv("T", "ts", stab, TT)[0]["x0"], TT, True), ("ts", surv("S", "ts", sens, TT)[0]["x0"], TT, False)]
    out = []
    ok = True
    for sys_, x0, T, gated in cases:
        lv = P.LEV[sys_]
        d = H.DDEngine(lv["spec"])
        m = H.MPEngine(lv["spec"], dps=50)
        mp.mp.dps = 50
        t0 = time.time()
        sh, sl = H.dd_state_at(d, x0, lv["E"], lv["L"], T, tol=1e-28)
        M = H.mp_state_at(m, x0, lv["E"], lv["L"], T, tol=1e-40)
        if not (sh[0] == sh[0]) or sh[0] < 0 or M is None:          # addendum 3: plunge / non-finite before T
            rel = float("inf")
        else:
            A = [mp.mpf(a) + bb for a, bb in zip(sh, sl)]
            rel = float(max(abs(a - c) / (1 + abs(c)) for a, c in zip(A, M)))
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
