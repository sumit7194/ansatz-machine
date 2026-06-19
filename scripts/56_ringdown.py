#!/usr/bin/env python3
"""Step 56 — RINGDOWN: how a black hole rings, derived exactly from the metric.

A new exact lens for the engine, sitting right beside the observables (§45 photon
sphere/shadow/ISCO, §49–51 bending/precession/redshift): black-hole PERTURBATION
THEORY. Strike a black hole — with infalling matter, a merger — and it rings down
like a struck bell, at a discrete set of complex frequencies (quasinormal modes):
the real part is the pitch, the imaginary part the damping. This is what LIGO hears
in the final moments of a merger.

What ansatz can give EXACTLY (its identity — symbolic, proven), and what it cannot:

  (A) the exact WAVE POTENTIAL. A perturbation of any static metric obeys a wave
      equation d²ψ/dr*² + (ω² − V)ψ = 0; the engine DERIVES the potential
          V(r) = f(r) [ ℓ(ℓ+1)/r² + f'(r)/r ]   (massless scalar, ANY f)
      straight from □Φ=0 — verified as an identity, not assumed. The spin-s family
      (scalar/EM/gravitational) V_s = f[ℓ(ℓ+1)/r² + (1−s²)f'/r] recovers the
      textbook Regge–Wheeler potentials for Schwarzschild.
  (B) the exact EIKONAL spectrum from the PHOTON SPHERE (Cardoso's correspondence):
          ω = ℓ Ω_c − i(n+½)λ,   Ω_c = √f_c/r_c,  λ = √(f_c(2f_c−r_c²f_c'')/(2r_c²))
      both closed-form in the photon-sphere data the engine already computes (§45).
      Schwarzschild: Ω_c = λ = 1/(3√3 M) exactly.
  (C) the UNIFICATION: Ω_c·b_c = 1, so ω_R = ℓ / b_shadow — the ringdown pitch is ℓ
      over the EHT shadow radius. The LIGO ringdown and the EHT image are the SAME
      photon sphere, two ways of seeing it.
  (D) the HONEST BOUNDARY: the full overtone spectrum (finite ℓ, n≥1) has NO closed
      form — it needs Leaver's continued-fraction method (the maintained `qnm`
      package). ansatz supplies the exact potential and the exact eikonal limit; the
      precise overtones are numerical. Stated, not hidden.

Run:  .venv/bin/python scripts/56_ringdown.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import R_SYM

r = R_SYM


def wave_potential(fexpr, ell, spin=0):
    """The Regge–Wheeler/scalar potential V(r) for lapse f, multipole ℓ, spin s.
    For s=0 this is the exact massless-scalar potential for ANY f (see verify
    below); the (1−s²) term is the Schwarzschild spin-s family."""
    return fexpr * (ell * (ell + 1) / r**2 + (1 - spin**2) * sp.diff(fexpr, r) / r)


def photon_sphere(fexpr):
    """Outermost photon-sphere radius (2f = r f'), the unstable circular null orbit."""
    roots = sp.solve(sp.Eq(2 * fexpr, r * sp.diff(fexpr, r)), r)
    real = [x for x in roots if x.is_real and x > 0]
    return max(real) if real else None


def eikonal_qnm(fexpr):
    """(Ω_c, λ): the eikonal real-frequency unit and damping rate from the photon
    sphere. ω = ℓ Ω_c − i(n+½)λ."""
    rc = photon_sphere(fexpr)
    fc = fexpr.subs(r, rc)
    fcpp = sp.diff(fexpr, r, 2).subs(r, rc)
    Om = sp.sqrt(fc) / rc
    lam = sp.sqrt(fc * (2 * fc - rc**2 * fcpp) / (2 * rc**2))
    return sp.simplify(Om), sp.simplify(lam), rc, fc


def main():
    print("RINGDOWN — how a black hole rings, derived exactly from the metric\n")
    M, Q = sp.symbols("M Q", positive=True)
    ell, n = sp.symbols("ell n", positive=True)

    # (A) the wave potential is EXACT for any f — derive & verify as an identity
    f = sp.Function("f")
    psi = sp.Function("psi")
    R = psi(r) / r
    E_R = (sp.Symbol("omega")**2 * R
           + (f(r) / r**2) * sp.diff(r**2 * f(r) * sp.diff(R, r), r)
           - f(r) * ell * (ell + 1) / r**2 * R)
    V_gen = f(r) * (ell * (ell + 1) / r**2 + sp.diff(f(r), r) / r)
    master = (f(r) * sp.diff(f(r) * sp.diff(psi(r), r), r)
              + (sp.Symbol("omega")**2 - V_gen) * psi(r))
    okA = sp.simplify(r * E_R - master) == 0
    print(f"  (A) exact wave potential  V = f[ℓ(ℓ+1)/r² + f'/r]  for ANY metric f   "
          f"{'✅ derived (identity)' if okA else '❌'}")
    # spin-s family recovers the textbook Schwarzschild Regge–Wheeler potentials
    fS = 1 - 2 * M / r
    names = {0: "scalar", 1: "electromagnetic", 2: "gravitational (axial)"}
    expect = {0: fS * (ell * (ell + 1) / r**2 + 2 * M / r**3),
              1: fS * (ell * (ell + 1) / r**2),
              2: fS * (ell * (ell + 1) / r**2 - 6 * M / r**3)}
    okAs = True
    for s in (0, 1, 2):
        got = sp.simplify(wave_potential(fS, ell, s) - expect[s]) == 0
        okAs = okAs and got
        print(f"        spin {s} ({names[s]:22s}): V_s = f[ℓ(ℓ+1)/r² + (1−s²)·2M/r³]   {'✓' if got else '✗'}")

    # (B) the eikonal spectrum, closed-form from the photon sphere
    Om, lam, rc, fc = eikonal_qnm(fS)
    want = 1 / (3 * sp.sqrt(3) * M)
    okB = sp.simplify(Om - want) == 0 and sp.simplify(lam - want) == 0
    print(f"\n  (B) eikonal QNM  ω = ℓΩ_c − i(n+½)λ   from the photon sphere r_c = {rc}:")
    print(f"        Ω_c = {Om}   λ = {lam}   {'✅ both = 1/(3√3 M)' if okB else '❌'}")
    # calibrate against the known (Leaver) ℓ=2,n=0 gravitational mode  Mω≈0.3737−0.0890i
    wR = float((2 * Om).subs(M, 1))                 # ℓ=2
    wI = float((sp.Rational(1, 2) * lam).subs(M, 1))  # n=0
    print(f"        ℓ=2,n=0 eikonal Mω = {wR:.3f} − {wI:.3f}i   vs exact (Leaver) 0.374 − 0.089i")
    okCal = abs(wR - 0.374) < 0.02 and abs(wI - 0.089) < 0.012
    print(f"        → within a few % already, and tightens as ℓ grows   {'✅' if okCal else '❌'}")

    # (C) the unification: ω_R = ℓ / b_shadow  (Ω_c · b_c = 1)
    b_c = rc / sp.sqrt(fc)                            # shadow radius (§45)
    okC = sp.simplify(Om * b_c - 1) == 0
    print(f"\n  (C) Ω_c · b_shadow = {sp.simplify(Om * b_c)}   ⇒  ω_R = ℓ / b_shadow   {'✅' if okC else '❌'}")
    print("      the LIGO ringdown pitch and the EHT shadow are the SAME photon sphere.")
    # charge tightens both, consistently (Reissner–Nordström) — evaluate numerically
    # (the symbolic RN photon-sphere root [3M±√(9M²−8Q²)]/2 has undecidable is_real)
    fRN = (1 - 2 * M / r + Q**2 / r**2).subs({M: 1, Q: sp.Rational(1, 2)})
    OmRN, lamRN, rcRN, fcRN = eikonal_qnm(fRN)
    wR_s = float((2 * Om).subs(M, 1)); wR_rn = float(2 * OmRN)
    okD = wR_rn > wR_s and sp.simplify(OmRN * (rcRN / sp.sqrt(fcRN)) - 1) == 0
    print(f"      charge (Q=M/2): ω_R = {wR_rn:.4f} > Schwarzschild {wR_s:.4f} (tighter orbit, higher pitch)   "
          f"{'✅' if okD else '❌'}")

    # (E) the honest boundary
    print("\n  (E) honest boundary: the full overtone spectrum (finite ℓ, n≥1) has NO closed")
    print("      form — it needs Leaver's continued-fraction method (the `qnm` package). ansatz")
    print("      gives the exact potential (A) and the exact eikonal limit (B); overtones are numerical.")

    passed = okA and okAs and okB and okCal and okC and okD
    print(f"\nRINGDOWN: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(exact wave potential + eikonal spectrum from the metric; overtones honestly deferred to Leaver)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
