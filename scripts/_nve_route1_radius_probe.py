#!/usr/bin/env python3
"""Pilot P4-r: is the small-k (dyadic) chain feasible? One Arb evaluation of F at each given k_c, against the 50-digit
engine's |F(k_c)|. [ansatz-machine-personal, 2026-11-27; read-only, no proof]

At small k, F = tr(M1 M0 M1^-1 M0^-1) - 2 cancels to about c2 k^2, while the Arb evaluator's absolute radius of F is
set by its Taylor tails over the walk and does not shrink with k. A segment can certify only if the node radius is
well below |F| (P4d's radius-limited rule uses 1/10). This measures that ratio at a few dyadic centres. It uses v2's
evaluator unchanged (`V.evaluate`), on the circle and the lasso of k_c from the floats file. It writes nothing but
its own log.
    NVE_SPIN=9/10 R1_R0=1.2639 R1_FLOATS=route1_floats_prod_9_10.json <.venv313 python> -I -u \
        scripts/_nve_route1_radius_probe.py 3/20480 3/2560 3/320 3/40"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_route1_segment_v2 as V            # noqa: E402
from flint import arb                          # noqa: E402

refs = json.load(open(os.path.join(V.OUTD, os.environ["R1_FLOATS"])))
print(f"== P4-r radius probe == spin {V.SPIN}, R0 {V.R0S}; k_c {sys.argv[1:]}", flush=True)
for ks in sys.argv[1:]:
    num, _, den = ks.partition("/")
    k = arb(num) / arb(den or 1)
    ref = refs[ks]
    r = V.evaluate(k, arb(0), ref)
    Fe = complex(float(ref["F"][0]), float(ref["F"][1]))
    ratio = r["rad_F"] / abs(Fe)
    print(f"k_c = {ks} ({float(k.mid()):.4e}): engine |F| {abs(Fe):.3e}; Arb radius of F {r['rad_F']:.3e}; "
          f"radius / |F| {ratio:.2e} -> {'feasible' if ratio < 1e-2 else 'MARGINAL' if ratio < 1e-1 else 'RADIUS-LIMITED'}"
          f" (P4d flags >= 1e-1); steps {r['steps']}, {r['sec']} s", flush=True)
print("== P4R_DONE", flush=True)
