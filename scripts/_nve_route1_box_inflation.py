"""Office diagnosis (2026-11-26): pointwise vs box enclosure of dq/dk in Fable's v2 code (d18de63), at three points of the
circle. Run from a checkout of d18de63 (cwd), with NVE_SPIN and R1_R0 set, under Quantum's python-flint (read-only, -I)."""
import os, sys, math
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
import _nve_route1_segment_v2 as V
from flint import acb, arb
kc = arb(21)/20
lau, laud = V.laurent(acb(kc)), V.laurent(acb(kc), True)
R0 = float(V.R0S)
for th in (22.8, 90.0, 180.0):
    z = complex(R0*math.cos(math.radians(th)), R0*math.sin(math.radians(th)))
    Z = acb(z.real, z.imag)
    pt = V.dq_sup(Z, acb(kc), None, lau, laud)[0]
    # a step-sized box around the same point (h ~ 0.004 as on the circle)
    hb = 0.002
    Zb = acb(arb(z.real, hb), arb(z.imag, hb))
    bx = V.dq_sup(Zb, acb(kc), None, lau, laud)[0]
    print(f"spin {V.SPIN} R0 {R0} theta {th}: |dq/dk| at the point <= {float(pt):.6g}; on a box of half-side {hb}: <= {float(bx):.6g} (x{float(bx)/float(pt):.1f})")
