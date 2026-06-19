#!/usr/bin/env python3
"""Step 58 — KILLING SYMMETRIES: the manifest algebra and the HIDDEN one.

The structure lens (attack angle #5), completed. A spacetime's symmetries are its
Killing vectors ξ (∇_(a ξ_b)=0), each giving a conserved quantity. Two layers:

  MANIFEST — the engine's cyclic detector already finds the obvious ones (∂_t, ∂_φ).
  COORDINATE-MIXING — the rotation group SO(3) of a spherical metric has THREE
    generators; only ∂_φ is manifest, the other two mix θ and φ. The engine now
    finds and verifies them (`analyzer.killing_vectors`), so Schwarzschild's full
    isometry algebra ℝ_t × SO(3) (dimension 4) comes out, not just the 2 cyclic ones.

  HIDDEN — some spacetimes have a symmetry no Killing VECTOR captures: a Killing
    TENSOR K_ab (∇_(a K_bc)=0), giving a conserved quantity QUADRATIC in momentum.
    Kerr's is famous: the CARTER CONSTANT. It is the hidden symmetry that makes a
    spinning black hole's orbits integrable — without it, geodesics around Kerr would
    be chaotic. The engine verifies Kerr's Killing tensor (numerically, since Kerr's
    symbolic curvature swamps) and shows the Carter constant is conserved along an
    actual orbit, alongside energy and angular momentum.

Experiments:
  (A) Schwarzschild: killing_vectors finds 4 (∂_t + SO(3)); the cyclic detector finds
      only 2 — the 2 coordinate-mixing rotations are the gap, now filled & verified;
  (B) the rotation generators close into so(3): [R_x, R_y] = R_z;
  (C) a Lorentz BOOST of Minkowski (x∂_t + t∂_x) is Killing — the verifier handles
      non-rotational, coordinate-mixing symmetries too;
  (D) Kerr's Killing TENSOR (Carter): ∇_(a K_bc)=0 (numeric), and it is IRREDUCIBLE
      (not ∝ g) — a genuine hidden symmetry;
  (E) along a Kerr geodesic, the Carter constant C = K_ab u^a u^b is CONSERVED, with
      energy and angular momentum — four constants of motion ⇒ Kerr is integrable.

Honest scope: textbook (Carter 1968; Walker–Penrose 1970). New is that the same engine
finds the manifest algebra exactly and verifies the hidden tensor on the metric.

Run:  .venv/bin/python scripts/58_killing.py
"""

import math
import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry
from analyzer import is_killing_vector, killing_vectors
from numeric_curvature import christoffel_numeric, inv4

A_SPIN, M_BH = 0.6, 1.0


def kerr_num(x):
    """Kerr metric (Boyer–Lindquist, M=1) as a 4×4 float list at x=(t,r,θ,φ)."""
    _, r, th, _ = x
    Sig = r * r + A_SPIN**2 * math.cos(th)**2
    De = r * r - 2 * M_BH * r + A_SPIN**2
    s2 = math.sin(th)**2
    g = [[0.0] * 4 for _ in range(4)]
    g[0][0] = -(1 - 2 * M_BH * r / Sig)
    g[0][3] = g[3][0] = -2 * M_BH * r * A_SPIN * s2 / Sig
    g[1][1] = Sig / De
    g[2][2] = Sig
    g[3][3] = (r * r + A_SPIN**2 + 2 * M_BH * r * A_SPIN**2 * s2 / Sig) * s2
    return g


def kerr_K_lower(x):
    """The Carter Killing tensor K_{μν} = 2Σ l_{(μ}n_{ν)} + r² g_{μν} (lowered)."""
    _, r, th, _ = x
    Sig = r * r + A_SPIN**2 * math.cos(th)**2
    De = r * r - 2 * M_BH * r + A_SPIN**2
    l = [(r * r + A_SPIN**2) / De, 1.0, 0.0, A_SPIN / De]            # principal null
    nv = [(r * r + A_SPIN**2) / (2 * Sig), -De / (2 * Sig), 0.0, A_SPIN / (2 * Sig)]
    g = kerr_num(x)
    gi = inv4(g)
    Kup = [[2 * Sig * 0.5 * (l[i] * nv[j] + l[j] * nv[i]) + r * r * gi[i][j]
            for j in range(4)] for i in range(4)]
    return [[sum(g[i][a] * g[j][b] * Kup[a][b] for a in range(4) for b in range(4))
             for j in range(4)] for i in range(4)]


def killing_tensor_residual(x, h=1e-5):
    """max |∇_(a K_bc)| (the fully symmetrized covariant derivative) at x."""
    G = christoffel_numeric(kerr_num, x)

    def dK(d):
        xp, xm = list(x), list(x)
        xp[d] += h
        xm[d] -= h
        Kp, Km = kerr_K_lower(xp), kerr_K_lower(xm)
        return [[(Kp[i][j] - Km[i][j]) / (2 * h) for j in range(4)] for i in range(4)]

    dKa = [dK(d) for d in range(4)]
    K = kerr_K_lower(x)

    def nab(a, b, c):
        return dKa[a][b][c] - sum(G[e][a][b] * K[e][c] + G[e][a][c] * K[b][e]
                                  for e in range(4))
    return max(abs(nab(a, b, c) + nab(b, c, a) + nab(c, a, b))
               for a in range(4) for b in range(4) for c in range(4))


def circular_orbit_u(x0, uth):
    """A near-circular equatorial Kerr orbit (small latitude tilt uth so the Carter
    constant is non-trivial): normalize a timelike u, then set the circular φ-rate."""
    g = kerr_num(x0)
    r0 = x0[1]
    A_, B_, Cc = g[0][0], 0.0, g[2][2] * uth * uth + 1
    ut = (-B_ - math.sqrt(B_ * B_ - 4 * A_ * Cc)) / (2 * A_)
    Omega = 1 / (r0**1.5 + A_SPIN)             # equatorial circular angular velocity
    return [ut, 0.0, uth, Omega * ut]


def geodesic_constants(x0, u0, steps=240, dtau=0.1):
    """RK4-integrate a Kerr geodesic; return the drift of (E, L, μ², Carter C)."""
    def rhs(state):
        x, u = state[:4], state[4:]
        G = christoffel_numeric(kerr_num, x)
        a = [-sum(G[i][b][c] * u[b] * u[c] for b in range(4) for c in range(4))
             for i in range(4)]
        return u + a

    def consts(x, u):
        g, K = kerr_num(x), kerr_K_lower(x)
        ul = [sum(g[i][j] * u[j] for j in range(4)) for i in range(4)]
        E = -ul[0]
        L = ul[3]
        mu2 = sum(g[i][j] * u[i] * u[j] for i in range(4) for j in range(4))
        C = sum(K[i][j] * u[i] * u[j] for i in range(4) for j in range(4))
        return E, L, mu2, C

    state = list(x0) + list(u0)
    track = [consts(state[:4], state[4:])]
    for _ in range(steps):
        k1 = rhs(state)
        k2 = rhs([state[i] + dtau / 2 * k1[i] for i in range(8)])
        k3 = rhs([state[i] + dtau / 2 * k2[i] for i in range(8)])
        k4 = rhs([state[i] + dtau * k3[i] for i in range(8)])
        state = [state[i] + dtau / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
                 for i in range(8)]
        track.append(consts(state[:4], state[4:]))
    drift = []
    for j in range(4):
        vals = [tr[j] for tr in track]
        scale = max(abs(v) for v in vals) or 1.0
        drift.append((max(vals) - min(vals)) / scale)
    return drift, track[0]


def main():
    print("KILLING SYMMETRIES — the manifest algebra and the hidden one\n")
    t, r, th, ph = sp.symbols("t r theta phi", real=True)
    M = sp.Symbol("M", positive=True)
    ok = []

    # (A) Schwarzschild: full isometry algebra ℝ_t × SO(3), dim 4
    f = 1 - 2 * M / r
    gS = Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph])
    kvs = killing_vectors(gS)
    labels = [nm for nm, _ in kvs]
    allk = all(is_killing_vector(gS, v) for _, v in kvs)
    okA = len(kvs) == 4 and allk
    ok.append(okA)
    print(f"  (A) Schwarzschild Killing vectors: {labels}")
    print(f"      cyclic detector finds 2 (∂_t, ∂_phi); full algebra ℝ_t×SO(3) = dim {len(kvs)} "
          f"(the 2 mixing rotations now found & verified)   {'✅' if okA else '❌'}")

    # (B) so(3) closure: [R_x, R_y] = R_z = ∂_φ
    def bracket(u, v):                      # [u,v]^a = u^b ∂_b v^a − v^b ∂_b u^a
        X = [t, r, th, ph]
        return [sp.simplify(sum(u[b] * sp.diff(v[a], X[b]) - v[b] * sp.diff(u[a], X[b])
                                for b in range(4))) for a in range(4)]
    Rx = [0, 0, -sp.sin(ph), -sp.cos(ph) / sp.tan(th)]
    Ry = [0, 0, sp.cos(ph), -sp.sin(ph) / sp.tan(th)]
    Rz = [0, 0, 0, 1]
    comm = bracket(Rx, Ry)
    negRz = [0, 0, 0, -1]
    okB = all(sp.simplify(comm[i] - negRz[i]) == 0 for i in range(4))   # = −R_z (orientation)
    ok.append(okB)
    print(f"\n  (B) rotation generators close: [R_x, R_y] = {comm} = −R_z   "
          f"{'✅ so(3) closes' if okB else '❌'}  (sign is orientation convention)")

    # (C) a Lorentz boost of Minkowski is Killing
    x, y, z = sp.symbols("x y z", real=True)
    gM = Geometry(sp.diag(-1, 1, 1, 1), [t, x, y, z])
    boost = [x, t, 0, 0]                     # x ∂_t + t ∂_x
    okC = is_killing_vector(gM, boost)
    ok.append(okC)
    print(f"\n  (C) Minkowski Lorentz boost  x∂_t + t∂_x  Killing?  {'✅' if okC else '❌'}  "
          "(coordinate-mixing, non-rotational)")

    # (D) Kerr's hidden Killing TENSOR (Carter constant)
    pts = [[0.0, 4.0, 1.1, 0.0], [0.0, 6.0, 0.7, 0.3], [0.0, 3.0, 1.4, 0.5]]
    resid = max(killing_tensor_residual(p) for p in pts)
    okD1 = resid < 1e-5
    # irreducible: K is not proportional to the metric (carries structure beyond g)
    xp = [0.0, 5.0, 1.0, 0.0]
    g0, K0 = kerr_num(xp), kerr_K_lower(xp)
    ratios = [K0[i][i] / g0[i][i] for i in range(4) if abs(g0[i][i]) > 1e-9]
    okD2 = (max(ratios) - min(ratios)) > 1e-3
    ok.append(okD1 and okD2)
    print(f"\n  (D) Kerr Killing TENSOR (a=0.6): max|∇_(a K_bc)| = {resid:.1e}  → ∇_(a K_bc)=0   "
          f"{'✅' if okD1 else '❌'}")
    print(f"      irreducible (K ∝ g would give equal ratios; got spread "
          f"{max(ratios)-min(ratios):.2f})   {'✅ a genuine hidden symmetry' if okD2 else '❌'}")

    # (E) the Carter constant is conserved along an actual Kerr orbit
    x0 = [0.0, 10.0, math.pi / 2, 0.0]
    drift, c0 = geodesic_constants(x0, circular_orbit_u(x0, 0.015))
    names = ["E (energy)", "L (ang. mom.)", "μ² (norm)", "C (CARTER)"]
    okE = all(d < 2e-3 for d in drift)
    ok.append(okE)
    print(f"\n  (E) along a Kerr geodesic, relative drift over 240 steps:")
    for nm, d, c in zip(names, drift, c0):
        print(f"        {nm:16s} = {c:8.4f}   drift {d:.2e}   {'✓ conserved' if d < 2e-3 else '✗'}")
    print(f"      → 4 constants of motion (E, L, μ², C) ⇒ Kerr orbits are integrable   "
          f"{'✅' if okE else '❌'}")

    passed = all(ok)
    print(f"\nKILLING: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(manifest SO(3) + Lorentz boost + Kerr's hidden Carter Killing tensor)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
