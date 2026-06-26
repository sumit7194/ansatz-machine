#!/usr/bin/env python3
"""Step 101 — EMRI Carter flux + a chaos-detector roundoff fix (sister-project follow-ups).

After the bridge closed B1 with §100's flux, it sent back two asks and a bug report. This banks
the fixes, all stress-tested.

  (A) Ask A — the Carter flux dQ/dtau. §100 returned dE/dtau, dL/dtau (so the bridge inspiral had
      to stay quasi-circular, Q=0). emri.quadrupole_flux(..., carter=True) now also returns dQ/dtau,
      built from the SAME quadrupole (the full angular-momentum-flux vector + the leading Carter
      Q=L^2-L_z^2). Validated: dQ/dtau = 0 for an equatorial orbit (Q=0), < 0 for an inclined one
      (radiation reduces inclination). Honest kludge (omits the relativistic a^2(1-E^2)cos^2 piece;
      for the bumpy metric Q is only an approximate third integral, §99).

  (B) THE BUG (a real one in our shipped code): geodesic_chaos.lyapunov false-positived "chaos" on
      bumpy metrics. Reproduced exactly: on an MN q=0.5 orbit that is REGULAR (box-dim -> ~1)
      pathologically-tight settings (Christoffel step ch=1e-7, separation d0=1e-10) report
      lambda~0.8 — pure finite-difference roundoff (~eps/ch) swamping the d0 separation. It is a
      corner artifact: it collapses to the floor as EITHER ch or d0 is increased. Fix: de-noised
      defaults (ch=1e-4, d0=1e-6) — now lambda ~ 0. (On the asymptotically-flat metric the artifact
      needs tighter ch than before — the gauge-fix improved the conditioning — but still exists.)

  (C) THE ROBUST DETECTOR: the box-counting dimension (poincare.box_dimension) is immune to that
      roundoff (geometric, not a divergence rate) and is the verdict to trust. Both detectors are
      independently validated on GENUINE chaos elsewhere — box-dim on Henon-Heiles (§84, 1.34),
      lyapunov on the di-hole (§79, 2.09). (Ask B — a bound MN orbit with box-dim -> 2 — was NOT
      found by systematic low-L scanning, max ~1.16-1.22, regular; MN's documented chaos needs the
      literature's specific initial data, like §97's ZV. emri.mn_bound_orbit is the launcher.)

Optional dep: numpy. Repro: .venv/bin/python scripts/101_emri_carter_and_chaos.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import numpy as np  # noqa: F401
    _HAVE_NUMPY = True
except ImportError:
    _HAVE_NUMPY = False

M, A = 1.0, 0.5


def kerr_circular(r, a=A):
    rs = math.sqrt(r); v = r**1.5 - 3 * M * rs + 2 * a * math.sqrt(M)
    E = (r**1.5 - 2 * M * rs + a * math.sqrt(M)) / (r**0.75 * math.sqrt(v))
    L = (math.sqrt(M) * (r * r - 2 * a * math.sqrt(M) * rs + a * a)) / (r**0.75 * math.sqrt(v))
    return E, L


def main():
    if not _HAVE_NUMPY:
        print("EMRI CARTER + CHAOS: SKIPPED (numpy not installed)")
        return 0

    from emri import quadrupole_flux, mn_bound_orbit
    from manko_novikov import manko_novikov
    from geodesic_chaos import lyapunov
    from _mn_invariant import build_hamilton_numeric
    from poincare import box_dimension, section

    print("EMRI CARTER FLUX + CHAOS-DETECTOR ROUNDOFF FIX (bridge follow-ups)\n")
    ok = []

    # (A) Carter flux dQ/dtau: ~0 equatorial (Q=0), <0 inclined; reliable on the STRONG BUMP
    # (a sister-project follow-up: the old kludge inflated dE 250x and flipped dQ>0 on MN q=0.2).
    r = 20.0; x0c = (r - M) / math.sqrt(M * M - A * A); E, L = kerr_circular(r)
    eq = quadrupole_flux(M, A, 0.0, E, L, x0c, n_orb=6, carter=True)
    inc = quadrupole_flux(M, A, 0.0, 0.95, 2.8, 9.0, n_orb=6, carter=True)
    mn = quadrupole_flux(M, A, 0.2, 0.95, 2.6, 8.0, n_orb=8, carter=True)   # the bridge's failing case
    okA = (eq and inc and mn and abs(eq[2]) < 0.05 * abs(eq[1]) and inc[2] < 0
           and abs(mn[0]) < 5e-4 and mn[2] < 0)                              # dE physical (not inflated), dQ<0
    ok.append(okA)
    print(f"  (A) Carter flux dQ/dtau (Ask A) — convergence-cutoff dE + radiation-reaction dQ:")
    print(f"        equatorial circular : (dE,dLz,dQ)=({eq[0]:.1e}, {eq[1]:.1e}, {eq[2]:.1e})  -> dQ~0 (Q=0)")
    print(f"        inclined Kerr       : (dE,dLz,dQ)=({inc[0]:.1e}, {inc[1]:.1e}, {inc[2]:.1e})  -> dQ<0 (de-inclines)")
    print(f"        MN q=0.2 strong bump: (dE,dLz,dQ)=({mn[0]:.1e}, {mn[1]:.1e}, {mn[2]:.1e})  -> dE physical, dQ<0")
    print(f"      equatorial->0, inclined->negative, reliable on the bump (no 250x inflation)   {'✅' if okA else '❌'}")

    # (B) lyapunov FD-roundoff false-positive on a REGULAR MN orbit, and the de-noised fix
    q = 0.5; E2, L2, x02 = 0.95, 3.0, 8.0
    f = build_hamilton_numeric(M, A, q)
    py = math.sqrt((-1 - f["W"](x02, 0.0, E2, L2)) / f["g22"](x02, 0.0, E2, L2))
    pts, dr, st = section(f, [x02, 0.0, 0.0, py], E2, L2, sec_idx=1, sec_val=0.0, rec=(0, 2),
                          n=140, h=0.02, maxst=800000, bounds=((1.1, 50.0), (-1.0, 1.0)))
    bd, _ = box_dimension(pts)
    pos, vel = mn_bound_orbit(M, A, q, E2, L2, x02)
    lam_old = lyapunov(manko_novikov(M, A, q), pos, vel, dtau=0.15, blocks=300, d0=1e-10, ch=1e-7)
    lam_new = lyapunov(manko_novikov(M, A, q), pos, vel, dtau=0.15, blocks=300, d0=1e-6, ch=1e-4)
    okB = lam_old > 0.3 and lam_new < 0.05 and bd < 1.3
    ok.append(okB)
    print(f"\n  (B) lyapunov on a REGULAR MN q=0.5 orbit (box-dim={bd:.2f}):")
    print(f"        NOISY  (ch=1e-7, d0=1e-10): lambda={lam_old:+.3f}  <- FALSE-POSITIVE chaos (FD roundoff)")
    print(f"        DEFAULT(ch=1e-4, d0=1e-6 ): lambda={lam_new:+.3f}  <- de-noised to the floor")
    print(f"      the roundoff artifact is reproduced and fixed   {'✅' if okB else '❌'}")

    # (C) box-dim is the robust detector (geometric, roundoff-immune); the orbit is regular
    okC = bd < 1.3 and lam_new < 0.02
    ok.append(okC)
    print(f"\n  (C) box-dimension (geometric, roundoff-immune) reads REGULAR ({bd:.2f}) — the verdict to")
    print(f"      trust; the de-noised lambda agrees. Both detectors are validated on GENUINE chaos")
    print(f"      elsewhere: box-dim on Henon-Heiles (§84, 1.34), lyapunov on the di-hole (§79, 2.09).")
    print(f"      RECOMMENDATION (relayed to the bridge): use box_dimension for the chaos verdict.   "
          f"{'✅' if okC else '❌'}")

    passed = all(ok)
    print(f"\nEMRI CARTER + CHAOS: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(dQ/dtau Carter flux; lyapunov FD false-positive reproduced + de-noised; box-dim is robust)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
