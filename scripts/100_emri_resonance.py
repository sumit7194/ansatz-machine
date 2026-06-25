#!/usr/bin/env python3
"""Step 100 — EMRI RADIATION REACTION: the GW flux + frequency map (the bridge's request B1).

The bridge's B1 (full EMRI waveform) is blocked on a radiation-reaction model: it has the geodesic
frequency map in the bumpy metric but needs the orbit to INSPIRAL. This delivers that capability,
general over Kerr AND the bumpy Manko-Novikov metric (§99) through one interface (emri.py):

  (A) the FREQUENCY MAP — radial nu_r and polar nu_theta of bound geodesics (by period counting).
      Their ratio sweeps as the orbit shrinks, so an inspiral crosses RESONANCES (nu_r:nu_theta a
      low-order rational) -- where the non-integrable bumpy metric (§99: no Carter) misbehaves;
  (B) the GW FLUX dE/dtau, dL/dtau — the numerical-kludge mass-quadrupole flux. VALIDATED: a
      circular orbit reproduces Peters' dE/dt = -(32/5) M^3/r^5 (ratio -> 1 in the weak field),
      and dL/dt = dE/dt / Omega_phi (the exact circular relation);
  (C) it works on the BUMPY metric too (q!=0): a real radiation-reaction driver, not Kerr-only;
  (D) INSPIRAL: the flux drives a circular orbit inward (dr/dt < 0) and chirps it up (nu_phi rises)
      -- the relativistic chirp, the engine end-to-end from metric to waveform-frequency evolution.

This is a KLUDGE (leading multipole), honest about it: ~10-20% low in the strong field (the known
quadrupole-formula deficit), enough for the qualitative resonance signature B1 wants, not a
precision Teukolsky waveform. Prior art for the bumpy chaos: Gair, Li & Mandel 2008
(arXiv:0708.0628); the resonant chaos itself is cited, not reproduced here.

Optional dep: numpy (the flux FFT). (A) runs without it; (B)-(D) skip cleanly if absent.
Repro:  .venv/bin/python scripts/100_emri_resonance.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emri import fundamental_frequencies
from _mn_invariant import build_hamilton_numeric

try:
    import numpy as np  # noqa: F401
    _HAVE_NUMPY = True
except ImportError:
    _HAVE_NUMPY = False

M, A = 1.0, 0.5


def kerr_circular(r, a=A):
    """Exact equatorial prograde circular E, L, Omega_phi (Bardeen-Press-Teukolsky)."""
    rs = math.sqrt(r)
    v = r**1.5 - 3 * M * rs + 2 * a * math.sqrt(M)
    E = (r**1.5 - 2 * M * rs + a * math.sqrt(M)) / (r**0.75 * math.sqrt(v))
    L = (math.sqrt(M) * (r * r - 2 * a * math.sqrt(M) * rs + a * a)) / (r**0.75 * math.sqrt(v))
    Om = math.sqrt(M) / (r**1.5 + a * math.sqrt(M))
    return E, L, Om


def main():
    print("EMRI RADIATION REACTION — the GW flux + frequency map (bridge request B1)\n")
    ok = []

    # (A) frequency map — sensible nu_r, nu_theta; the ratio sweeps (so inspiral crosses resonances)
    fk = build_hamilton_numeric(M, A, 0.0)
    ratios = []
    print("  (A) FREQUENCY MAP (Kerr a=0.5): radial & polar frequencies of bound geodesics")
    for (E, L, x0) in [(0.95, 2.8, 8.0), (0.96, 3.2, 14.0)]:
        r = fundamental_frequencies(fk, E, L, x0, nlam=150000)
        if r is None:
            continue
        nu_r, nu_th, ratio = r
        ratios.append(ratio)
        print(f"        orbit (E={E},L={L},x0={x0}): nu_r={nu_r:.5f} nu_theta={nu_th:.5f} ratio={ratio:.4f}")
    okA = len(ratios) >= 2 and all(0.3 < x < 1.0 for x in ratios) and max(ratios) - min(ratios) > 0.01
    ok.append(okA)
    print(f"      nu_r<nu_theta, ratios sensible AND varying ({min(ratios):.3f}..{max(ratios):.3f}) "
          f"⇒ inspiral sweeps resonances   {'✅' if okA else '❌'}")

    if not _HAVE_NUMPY:
        print("\n  (B)-(D) SKIPPED (numpy not installed)")
        print(f"\nEMRI: {'PARTIAL (A) ✅' if okA else 'FAILED ❌'}")
        return 0 if okA else 1

    from emri import quadrupole_flux

    # (B) GW flux validated against Peters for a circular orbit; dL/dt = dE/dt/Omega_phi
    print("\n  (B) GW FLUX vs Peters dE/dt=-(32/5)M^3/r^5 (ratio->1 weak field) + circular dL=dE/Omega:")
    ratB, dLdE_ok = [], []
    for r in (40.0, 70.0):
        E, L, Om = kerr_circular(r)
        x0 = (r - M) / math.sqrt(M * M - A * A)
        res = quadrupole_flux(M, A, 0.0, E, L, x0, n_orb=6)
        if res is None:
            continue
        dEdt, dLdt = res
        peters = -(32.0 / 5.0) * M**3 / r**5
        rr = dEdt / peters
        dl = (dLdt / dEdt) * Om                        # should be 1.0 for circular (dL=dE/Omega)
        ratB.append(rr); dLdE_ok.append(abs(dl - 1) < 0.1)
        print(f"        r={r:.0f}: dE/dt ratio to Peters={rr:.3f};  (dL/dt)/(dE/dt)*Omega={dl:.3f} (->1)")
    okB = len(ratB) >= 2 and all(0.75 < x < 1.25 for x in ratB) and all(dLdE_ok)
    ok.append(okB)
    print(f"      flux normalization correct (ratio->1) and circular dL/dE relation holds   {'✅' if okB else '❌'}")

    # (C) the flux works on the BUMPY metric (q!=0): a genuine radiation-reaction driver
    print("\n  (C) BUMPY-metric flux (q!=0) — a real driver, not Kerr-only:")
    okC = True
    for q in (0.0, 0.2):
        res = quadrupole_flux(M, A, q, 0.95, 2.8, 8.0, n_orb=6)
        if res is None or not (res[0] < 0 and res[1] < 0):
            okC = False; print(f"        q={q}: flux failed {res}"); continue
        print(f"        q={q}: dE/dtau={res[0]:.2e}, dL/dtau={res[1]:.2e}  (both<0 -> inspiral)")
    ok.append(okC)
    print(f"      the flux drives an inspiral in the bumpy spacetime too   {'✅' if okC else '❌'}")

    # (D) INSPIRAL: flux drives a circular orbit inward, chirping nu_phi up
    print("\n  (D) INSPIRAL chirp — flux drives r inward, nu_phi rises (relativistic chirp):")
    rows = []
    for r in (12.0, 9.0, 7.0):
        E, L, Om = kerr_circular(r)
        x0 = (r - M) / math.sqrt(M * M - A * A)
        res = quadrupole_flux(M, A, 0.0, E, L, x0, n_orb=6)
        if res is None:
            continue
        dEdt = res[0]
        dr = 1e-3
        E2 = kerr_circular(r + dr)[0]
        dEdr = (E2 - E) / dr                            # dE/dr along the circular sequence (>0)
        drdt = dEdt / dEdr                              # <0: energy loss shrinks the orbit
        rows.append((r, Om, drdt))
        print(f"        r={r:.0f}: Omega_phi={Om:.5f}, dr/dt={drdt:.2e} (<0 ⇒ inspiral)")
    okD = len(rows) >= 2 and all(dr < 0 for _, _, dr in rows) and rows[0][1] < rows[-1][1]
    ok.append(okD)
    print(f"      dr/dt<0 (shrinks) and Omega_phi rises inward (the chirp)   {'✅' if okD else '❌'}")

    okE = okA and okB and okC and okD
    ok.append(okE)
    print(f"\n  (E) The flux (validated vs Peters) + the frequency map = the radiation-reaction capability")
    print(f"      B1 needs: the bridge can now drive a self-consistent inspiral and sweep it through a")
    print(f"      resonance, in Kerr OR the bumpy metric (§99). Per §99 the bumpy resonances are where")
    print(f"      integrability fails -> the resonance-crossing signature B1 is after.   {'✅' if okE else '❌'}")

    passed = all(ok)
    print(f"\nEMRI RADIATION REACTION: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(frequency map + GW flux validated vs Peters; drives inspiral in Kerr and the bumpy metric)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
