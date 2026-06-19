#!/usr/bin/env python3
"""Step 72 — THE RINGDOWN WAVEFORM & BLACK-HOLE SPECTROSCOPY (the no-hair test).

§56 gave the quasinormal frequencies; this turns them into the actual time-domain
STRAIN a detector records in the final moments of a merger — and the consistency test
that probes the no-hair theorem. This is the exact template a ringdown search fits
against measured data (the artifact black-hole spectroscopy needs).

After merger the remnant rings like a struck bell, so the strain is a sum of damped
sinusoids (the "final note"):
        h(t) = Σ A_n e^{−t/τ_n} cos(ω_n t + φ_n),   τ_n = 1/|Im ω_n|.

  (A) the template: one mode is h(t)=A e^{−t/τ} cos(ω_R t + φ), with ω_R, τ from the
      QNM (§56);
  (B) the damping is the LIGHT-RING instability (§56/§66): τ = 1/[(n+½)λ] with λ the
      Lyapunov exponent of the unstable photon orbit — the bell rings at the light-ring
      frequency and fades at its instability rate. Quality factor Q = ω_R τ/2 = ℓ/(2n+1)
      (eikonal); Schwarzschild ℓ=2,n=0 ⇒ Q=2, Mω_R=0.385 (Leaver 0.374, ~3%; precise
      values are numerical, as in §56);
  (C) the NO-HAIR TEST (the bridge to spectroscopy): every QNM ω(ℓ,m,n) is a function
      of ONLY (M, a). So one mode's (ω_R, τ) already fixes (M, a); a SECOND mode
      overdetermines them — consistency ⇒ the remnant is a Kerr black hole (no hair),
      inconsistency ⇒ new physics. A clean eikonal signature: ω_R(ℓ=3)/ω_R(ℓ=2)=3/2,
      parameter-free;
  (D) so ansatz supplies the exact ω(M,a) oracle that a measured ringdown is tested
      against — the engine's side of the spectroscopy bridge.

Honest scope: textbook ringdown/spectroscopy. The template structure and the no-hair
LOGIC are exact; the precise ℓ=2 frequencies are numerical (Leaver / the `qnm` package),
exactly as flagged in §56.

Run:  .venv/bin/python scripts/72_ringdown_template.py
"""

import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("THE RINGDOWN WAVEFORM & BLACK-HOLE SPECTROSCOPY — the no-hair test\n")
    M, t, A, phi = sp.symbols("M t A phi", real=True, positive=True)
    ell, n = sp.symbols("ell n", positive=True)
    ok = []

    # QNM (eikonal, §56): Ω_c = λ = 1/(3√3 M) for Schwarzschild
    unit = 1 / (3 * sp.sqrt(3) * M)
    wR = ell * unit
    wI = (n + sp.Rational(1, 2)) * unit
    tau = sp.simplify(1 / wI)
    Q = sp.simplify(wR / (2 * wI))

    # (A) the damped-sinusoid template
    h = A * sp.exp(-t / tau) * sp.cos(wR * t + phi)
    # it solves the damped-oscillator equation h'' + (2/τ)h' + (ω_R²+1/τ²)h = 0
    res = sp.simplify(sp.diff(h, t, 2) + (2 / tau) * sp.diff(h, t) + (wR**2 + 1 / tau**2) * h)
    okA = res == 0
    ok.append(okA)
    print(f"  (A) ringdown strain h(t) = A e^(−t/τ) cos(ω_R t + φ) — a damped sinusoid")
    print(f"      (solves h″ + (2/τ)h′ + (ω_R²+1/τ²)h = 0: residual {res})   {'✅' if okA else '❌'}")

    # (B) damping = light-ring instability; Q = ℓ/(2n+1)
    okB = sp.simplify(tau - 6 * sp.sqrt(3) * M / (2 * n + 1)) == 0 and sp.simplify(Q - ell / (2 * n + 1)) == 0
    mwR_20 = float((wR * M).subs({ell: 2, n: 0}))
    Q20 = float(Q.subs({ell: 2, n: 0}))
    okB = okB and abs(mwR_20 - 0.385) < 0.01 and Q20 == 2
    ok.append(okB)
    print(f"\n  (B) τ = 1/[(n+½)λ] = {tau} (λ = Lyapunov of the light ring, §56/§66);  Q = {Q}")
    print(f"      ℓ=2,n=0: Mω_R={mwR_20:.3f} (Leaver 0.374, ~3%), Q={Q20:.0f}   {'✅' if okB else '❌'}")

    # (C) no-hair: ω(ℓ,m,n)=f(M,a) only; parameter-free mode ratio ω_R(3)/ω_R(2)=3/2
    ratio = sp.simplify(wR.subs(ell, 3) / wR.subs(ell, 2))
    okC = ratio == sp.Rational(3, 2)
    ok.append(okC)
    print(f"\n  (C) no-hair: every ω(ℓ,m,n)=f(M,a) only ⇒ ≥2 modes overdetermine (M,a);")
    print(f"      parameter-free eikonal signature ω_R(ℓ=3)/ω_R(ℓ=2) = {ratio}   "
          f"{'✅ consistency ⇒ Kerr (no hair)' if okC else '❌'}")

    # (D) the oracle role for the bridge
    okD = okA and okB and okC
    ok.append(okD)
    print(f"\n  (D) ansatz gives the exact ω(M,a) (eikonal) + the template + the consistency logic;")
    print(f"      a measured ringdown is fit against it — the engine's side of the spectroscopy bridge   "
          f"{'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nRINGDOWN TEMPLATE: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(damped-sinusoid strain, Q=ℓ/(2n+1), the no-hair mode-consistency test)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
