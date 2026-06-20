#!/usr/bin/env python3
"""Step 82 — THE INTEGRABILITY FRONTIER: deform Kerr — does its integrability survive?

A rigorous, HONEST probe of ROADMAP item 3 (rotating modified-gravity BHs). The full
prize — solving a modified theory's O(a²) field equations (a 2D PDE) — is NOT done here.
Item 3's scientific core is answerable with the tools just built (§78 symbolic
Killing-tensor verifier + §79 chaos lens): is Kerr's Carter-constant integrability
SPECIAL to exact Kerr, or robust under deformation? We deform Kerr by a quadrupole (l=2)
"bump" ε·(3cos²θ−1)/r³ on g_tt (the deviation-from-Kerr framework) and ask.

The honest result is more subtle than the naive "deform ⇒ chaos" guess — and the
stress-test (the whole point of this engine) is what surfaced it:

  (A) Kerr (ε=0): the Carter tensor IS Killing (∇₍ₐK_bc₎≡0, proven §78) — integrable;
  (B) deformed (ε≠0): the KERR Carter tensor is NO LONGER Killing (residual ≠ 0,
      symbolic + numeric). The *canonical* hidden symmetry does not carry over verbatim;
  (C) YET the geodesics show NO detectable chaos: across a broad orbit scan (radii 4–6,
      inclinations 0.05–1.0, ε up to 0.6) every Lyapunov exponent sits at the regular
      ~0.01 floor — same as Kerr. Deforming does NOT visibly destroy integrability;
  (D) so the fate is UNDETERMINED by these tools: either a *different* Killing tensor
      survives (the deformed metric stays integrable), or chaos hides below detection
      (thin KAM layers). Deciding it needs a modified-Killing-tensor PDE search or
      orbit-resolved Poincaré sections — and the SPECIFIC modified-gravity rotating
      metric needs its field equations solved (the open 2D PDE).

The lesson (and why we stress-test): the naive expectation "break the canonical Carter
tensor ⇒ chaos" is NOT borne out. Integrability is robust enough that losing the literal
Kerr tensor doesn't visibly destroy it. We assert only what's verified — and flag the
rest as open, not faked.

Run:  .venv/bin/python scripts/82_integrability_frontier.py
"""

import math
import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry
from geodesic_chaos import lyapunov


def carter_tensor(a):
    """The Kerr Carter Killing tensor (lower indices) in rational (t,r,u=cosθ,φ)."""
    t, r, u, ph = sp.symbols("t r u phi", real=True)
    M = sp.Symbol("M", positive=True)
    Sig = r**2 + a**2 * u**2
    De = r**2 - 2 * M * r + a**2
    om = 1 - u**2
    gK = sp.zeros(4)
    gK[0, 0] = -(1 - 2 * M * r / Sig)
    gK[0, 3] = gK[3, 0] = -2 * M * r * a * om / Sig
    gK[1, 1] = Sig / De
    gK[2, 2] = Sig / om
    gK[3, 3] = (r**2 + a**2 + 2 * M * r * a**2 * om / Sig) * om
    giK = gK.inv()
    l = [(r**2 + a**2) / De, 1, 0, a / De]
    nv = [(r**2 + a**2) / (2 * Sig), -De / (2 * Sig), 0, a / (2 * Sig)]
    Kup = sp.Matrix(4, 4, lambda i, j: Sig * (l[i] * nv[j] + l[j] * nv[i]) + r**2 * giK[i, j])
    return sp.Matrix(4, 4, lambda i, j: sp.cancel(sp.together(
        sum(gK[i, p] * gK[j, q] * Kup[p, q] for p in range(4) for q in range(4)))))


def deformed_kerr_sym(a, eps):
    """Quadrupole-deformed Kerr (symbolic, rational coords); eps=0 is exact Kerr."""
    t, r, u, ph = sp.symbols("t r u phi", real=True)
    M = sp.Symbol("M", positive=True)
    Sig = r**2 + a**2 * u**2
    De = r**2 - 2 * M * r + a**2
    om = 1 - u**2
    bump = 1 + eps * (3 * u**2 - 1) / r**3
    g = sp.zeros(4)
    g[0, 0] = -(1 - 2 * M * r / Sig) * bump
    g[0, 3] = g[3, 0] = -2 * M * r * a * om / Sig
    g[1, 1] = Sig / De
    g[2, 2] = Sig / om
    g[3, 3] = (r**2 + a**2 + 2 * M * r * a**2 * om / Sig) * om
    return Geometry(g, [t, r, u, ph]), r, M, u


def _g_num(eps, A):
    """Quadrupole-deformed Kerr as a numeric metric function g(x), x=(t,r,θ,φ)."""
    def g(x):
        _, rr, th, _ = x
        Sg = rr * rr + A * A * math.cos(th)**2
        Dl = rr * rr - 2 * rr + A * A
        s2 = math.sin(th)**2
        bump = 1 + eps * (3 * math.cos(th)**2 - 1) / rr**3
        gg = [[0.0] * 4 for _ in range(4)]
        gg[0][0] = -(1 - 2 * rr / Sg) * bump
        gg[0][3] = gg[3][0] = -2 * rr * A * s2 / Sg
        gg[1][1] = Sg / Dl
        gg[2][2] = Sg
        gg[3][3] = (rr * rr + A * A + 2 * rr * A * A * s2 / Sg) * s2
        return gg
    return g


def _lam(eps, A, r0, uth):
    g = _g_num(eps, A)
    x0 = [0.0, r0, math.pi / 2, 0.0]
    G = g(x0)
    val = (G[2][2] * uth * uth + 1) / (-G[0][0])
    if val <= 0:
        return None
    ut = math.sqrt(val)
    u0 = [ut, 0.0, uth, (1 / (r0**1.5 + A)) * ut]
    return lyapunov(g, x0, u0, dtau=0.2, blocks=500)


def main():
    print("THE INTEGRABILITY FRONTIER — deform Kerr: does its integrability survive?\n")
    ok = []
    a = sp.Rational(3, 5)
    K = carter_tensor(a)

    # (A) Kerr (ε=0): Carter tensor is Killing
    geo0, _, _, _ = deformed_kerr_sym(a, sp.Integer(0))
    okA = geo0.is_killing_tensor(K)
    ok.append(okA)
    print(f"  (A) Kerr (ε=0): Carter tensor ∇₍ₐK_bc₎ ≡ 0 → is_killing_tensor = {okA}  (integrable, §78)   "
          f"{'✅' if okA else '❌'}")

    # (B) deformed (ε≠0): the KERR Carter tensor no longer closes (symbolic fact)
    geoR, r, M, u = deformed_kerr_sym(a, sp.Rational(3, 10))
    resR = geoR.killing_tensor_residual(K)
    pt = {M: 1, r: 5, u: sp.Rational(1, 2)}
    okB = resR != 0 and float(sp.Abs(resR.subs(pt))) > 1e-9
    ok.append(okB)
    print(f"\n  (B) deformed (ε=0.3): the KERR Carter tensor is NOT Killing — residual ≠ 0 "
          f"(|res|={float(sp.Abs(resR.subs(pt))):.3e})")
    print(f"      ⇒ the canonical hidden symmetry does not carry over verbatim   {'✅' if okB else '❌'}")

    # (C) yet NO detectable chaos across a broad orbit scan (the honest, stress-tested finding)
    A = 0.6
    floor = 0.05
    lam_kerr = _lam(0.0, A, 8.0, 0.05)
    chaotic = []
    sampled = 0
    for eps in (0.3, 0.6):
        for r0 in (4.0, 5.0, 6.0, 8.0):
            for uth in (0.05, 0.3, 0.6, 1.0):
                lam = _lam(eps, A, r0, uth)
                if lam is None:
                    continue
                sampled += 1
                if lam > floor:
                    chaotic.append((eps, r0, uth, lam))
    okC = not chaotic
    ok.append(okC)
    print(f"\n  (C) chaos lens: λ(Kerr)={lam_kerr:.4f} (regular floor). Scanned {sampled} deformed orbits "
          f"(ε≤0.6, r∈[4,8], incl∈[0.05,1.0]):")
    print(f"      {len(chaotic)} above the {floor} chaos threshold — deforming does NOT visibly destroy "
          f"integrability   {'✅' if okC else '❌'}")

    # (D) honest synthesis: the fate is UNDETERMINED — not faked either way
    okD = okA and okB and okC
    ok.append(okD)
    print(f"\n  (D) HONEST: (B) the literal Kerr Carter tensor fails, yet (C) geodesics stay regular ⇒ the")
    print(f"      deformed metric's integrability is UNDETERMINED — a different Killing tensor may survive,")
    print(f"      or chaos hides below detection. Deciding needs a Killing-tensor PDE search or Poincaré")
    print(f"      sections; the modified-gravity metric itself needs its field-equation solve (open).")
    print(f"      The naive 'deform ⇒ chaos' guess is NOT borne out — we assert only what's verified.   "
          f"{'✅' if okD else '❌'}")

    passed = all(ok)
    print(f"\nINTEGRABILITY FRONTIER: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(Kerr integrable; Kerr's Carter tensor fails under deformation; NO visible chaos; fate open — not faked)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
