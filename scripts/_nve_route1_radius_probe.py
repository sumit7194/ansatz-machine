#!/usr/bin/env python3
"""Pilot P4-r: is the small-k (dyadic) chain feasible? One Arb evaluation of F at each given k_c, against the 50-digit
engine's |F(k_c)|. [ansatz-machine-personal, 2026-11-27; read-only, no proof]

At small k, F = tr(M1 M0 M1^-1 M0^-1) - 2 cancels to about c2 k^2, while the Arb evaluator's absolute radius of F is
set by its Taylor tails over the walk and does not shrink with k. A segment can certify only if the node radius is
well below |F|. This measures that ratio at a few dyadic centres. It uses v2's
evaluator unchanged (`V.evaluate`), on the circle and the lasso of k_c from the floats file. It writes nothing but
its own log. It also reports the margins of the two TRACE conditions (tr M0 != 0, tr M1 not in [-2, 2]) against
their radii, since a trace failure cannot be cured by splitting either.
    NVE_SPIN=9/10 R1_R0=1.2639 R1_FLOATS=route1_floats_prod_9_10.json <.venv313 python> -I -u \
        scripts/_nve_route1_radius_probe.py 3/20480 3/2560 3/320 3/40"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_route1_segment_v2 as V            # noqa: E402
from flint import acb, arb                     # noqa: E402

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
          f"; steps {r['steps']}, {r['sec']} s", flush=True)
    # the Bridge's read: are the two TRACE conditions attainable at small k? A trace failure cannot be cured by
    # splitting either. Margins: |tr M0| for tr M0 != 0; max(|Im tr M1|, |Re tr M1| - 2) for tr M1 not in [-2, 2].
    T0 = acb(arb(r["T0"][0]), arb(r["T0"][1]))
    T1 = acb(arb(r["T1"][0]), arb(r["T1"][1]))
    m0 = float(T0.abs_lower())
    m1 = max(float(T1.imag.abs_lower()), float(T1.real.abs_lower()) - 2)
    print(f"    traces: tr M0 = {complex(float(T0.real.mid()), float(T0.imag.mid())):.6f} (radius {float(T0.rad()):.2e}; "
          f"margin |tr M0| {m0:.3e}); tr M1 = {complex(float(T1.real.mid()), float(T1.imag.mid())):.6f} (radius "
          f"{float(T1.rad()):.2e}; margin {m1:.3e}) -> trace conditions {'attainable' if m0 > 10 * float(T0.rad()) and m1 > 10 * float(T1.rad()) else 'AT RISK'}",
          flush=True)
print("== P4R_DONE", flush=True)
