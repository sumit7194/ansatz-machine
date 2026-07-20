#!/usr/bin/env python3
"""THE CK SPIKE — de-risking Cartan-Karlhede before committing weeks.

Two questions, honestly answered:
  RISK A  can we canonically fix the frame from an ARBITRARY coordinate presentation?
  RISK B  does the comparison layer (functional relations / elimination) drown in UNDECIDED?

Tests, all with known ground truth:
  T1  PND path exercised: deliberately DE-canonicalize Schwarzschild's frame with a known
      null rotation, then check canonical_frame() recovers Psi = (0,0,-M/r^3,0,0).
  T2  Schwarzschild (Schwarzschild chart) vs Schwarzschild (isotropic chart)  -> EQUIVALENT
  T3  Schwarzschild vs Painleve-Gullstrand                                    -> EQUIVALENT
  T4  Schwarzschild M=1 vs Schwarzschild M=2  (THE SHARP TEST)                -> INEQUIVALENT
  T5  Schwarzschild vs Schwarzschild-de Sitter                                -> INEQUIVALENT
  T6  THE KILLER DEMO -- VSI pp-waves, where every polynomial invariant VANISHES so the §02
      fingerprint filter is blind by construction, and CK must decide anyway.

Durable log data/ck_spike.log.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

import ck
from gr_engine import Geometry

t, r, th, ph = sp.symbols("t r theta phi", positive=True)
rho = sp.Symbol("rho", positive=True)
M = sp.Symbol("M", positive=True)
T0 = time.time()


def stamp(msg):
    print(f"[{time.time()-T0:7.1f}s] {msg}")
    sys.stdout.flush()


def sph(f, M_):
    return Geometry(sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph])


# ============================================================ T1: exercise the PND path
print("=" * 78)
print("T1 -- PND canonicalization path (deliberately de-canonicalized frame)")
print("=" * 78)
ck.set_domain(sp.Q.positive(r - 2 * M), sp.Q.positive(sp.sin(th)))
gS = sph(1 - 2 * M / r, M)
C = ck.weyl_tensor(gS)
tet = ck.null_tetrad(gS)
stamp(f"canonical frame Psi (baseline) = {ck.psis(C, tet)}")

# de-canonicalize: a null rotation about n with a REAL parameter mixes Psi0..Psi4
tet_bad = ck.null_rotation_about_n(tet, sp.Rational(1, 2))
P_bad = ck.psis(C, tet_bad)
stamp(f"after null rotation a=1/2  Psi = {P_bad}")
decanon = sum(1 for k in (0, 1, 3, 4) if P_bad[k] != 0)
print(f"    de-canonicalized? {decanon} of Psi0,Psi1,Psi3,Psi4 are now nonzero "
      f"{'✅' if decanon > 0 else '❌ (rotation did nothing)'}")

tet_rec, P_rec, ty_rec, iso_rec, note_rec = ck.canonical_frame(gS, C, tet_bad, verbose=True)
ok_rec = (sp.simplify(P_rec[2] + M / r**3) == 0
          and all(P_rec[k] == 0 for k in (0, 1, 3, 4)))
stamp(f"recovered Psi = {P_rec}   type {ty_rec}")
print(f"    PND path recovers the canonical frame: {'✅' if ok_rec else '❌'}\n")

# ============================================================ signatures
print("=" * 78)
print("T2-T5 -- CK signatures and pairwise verdicts")
print("=" * 78)

stamp("computing signature: Schwarzschild (Schwarzschild chart)...")
sig_schw = ck.ck_signature(gS, "Schwarzschild [Schwarzschild chart]")
stamp(f"  petrov={sig_schw['petrov']} iso={sig_schw['isotropy_dim']} "
      f"t0={sig_schw['t0']} t1={sig_schw['t1']}")
print(f"     order0 = {sig_schw['order0']}")
print(f"     order1 components (covariant) = {sig_schw['order1_components']}")
print(f"     order1 INVARIANTS = {sig_schw['order1_invariants']}")
print(f"     certificate = {sig_schw['certificate']}")
print(f"     failures = {sig_schw['cert_failures']}")

# --- isotropic chart: ds^2 = -((1-M/2rho)/(1+M/2rho))^2 dt^2 + (1+M/2rho)^4 (drho^2+rho^2 dOmega^2)
stamp("computing signature: Schwarzschild (ISOTROPIC chart)...")
A = (1 - M / (2 * rho)) / (1 + M / (2 * rho))
B = (1 + M / (2 * rho))**4
g_iso = Geometry(sp.diag(-A**2, B, B * rho**2, B * rho**2 * sp.sin(th)**2), [t, rho, th, ph])
ck.set_domain(sp.Q.positive(rho - M / 2), sp.Q.positive(sp.sin(th)))
sig_iso = ck.ck_signature(g_iso, "Schwarzschild [isotropic chart]")
stamp(f"  petrov={sig_iso['petrov']} iso={sig_iso['isotropy_dim']} "
      f"t0={sig_iso['t0']} t1={sig_iso['t1']}")
print(f"     order0 = {sig_iso['order0']}")
print(f"     certificate = {sig_iso['certificate']}")
print(f"     failures = {sig_iso['cert_failures']}")

# --- Painleve-Gullstrand
stamp("computing signature: Schwarzschild (PAINLEVE-GULLSTRAND chart)...")
sq = sp.sqrt(2 * M / r)
g_pg = Geometry(sp.Matrix([[-(1 - 2 * M / r), sq, 0, 0], [sq, 1, 0, 0],
                           [0, 0, r**2, 0], [0, 0, 0, r**2 * sp.sin(th)**2]]), [t, r, th, ph])
ck.set_domain(sp.Q.positive(r - 2 * M), sp.Q.positive(sp.sin(th)))
sig_pg = ck.ck_signature(g_pg, "Schwarzschild [Painleve-Gullstrand]")
stamp(f"  petrov={sig_pg['petrov']} iso={sig_pg['isotropy_dim']} "
      f"t0={sig_pg['t0']} t1={sig_pg['t1']}")
print(f"     certificate = {sig_pg['certificate']}")
print(f"     failures = {sig_pg['cert_failures']}")

# --- different masses (the sharp test)
stamp("computing signatures: Schwarzschild M=1 and M=2...")
ck.set_domain(sp.Q.positive(r - 4))
g_m1 = Geometry(sp.diag(-(1 - 2 / r), 1 / (1 - 2 / r), r**2, r**2 * sp.sin(th)**2),
                [t, r, th, ph])
g_m2 = Geometry(sp.diag(-(1 - 4 / r), 1 / (1 - 4 / r), r**2, r**2 * sp.sin(th)**2),
                [t, r, th, ph])
ck.set_domain(sp.Q.positive(r - 4), sp.Q.positive(sp.sin(th)))
sig_m1 = ck.ck_signature(g_m1, "Schwarzschild M=1")
sig_m2 = ck.ck_signature(g_m2, "Schwarzschild M=2")
print(f"     M=1 certificate = {sig_m1['certificate']}")
print(f"     M=2 certificate = {sig_m2['certificate']}")

# --- Schwarzschild-de Sitter
stamp("computing signature: Schwarzschild-de Sitter...")
Lam = sp.Symbol("Lambda", positive=True)
ck.set_domain(sp.Q.positive(r - 2 * M), sp.Q.positive(sp.sin(th)))
g_sds = sph(1 - 2 * M / r - Lam * r**2 / 3, M)
sig_sds = ck.ck_signature(g_sds, "Schwarzschild-de Sitter")
stamp(f"  ricci scalar = {sig_sds['ricci_scalar']} (Schwarzschild: {sig_schw['ricci_scalar']})")

print("\n--- VERDICTS ---")
for lab, a, b, expect in [
        ("T2 Schw[Schw chart] vs Schw[isotropic]", sig_schw, sig_iso, ck.EQUIVALENT),
        ("T3 Schw[Schw chart] vs Schw[PG]", sig_schw, sig_pg, ck.EQUIVALENT),
        ("T4 Schw M=1 vs Schw M=2", sig_m1, sig_m2, ck.INEQUIVALENT),
        ("T5 Schw vs Schw-de Sitter", sig_schw, sig_sds, ck.INEQUIVALENT)]:
    v, why = ck.equivalent(a, b)
    mark = "✅" if v == expect else ("⚠️ UNDECIDED" if v == ck.UNDECIDED else "❌")
    print(f"  {lab:42s} -> {v:14s} (want {expect:12s}) {mark}")
    for wline in why[:3]:
        print(f"       · {wline}")

# ============================================================ T6: the killer demo
print("\n" + "=" * 78)
print("T6 -- THE KILLER DEMO: VSI pp-waves (fingerprint filter is BLIND here)")
print("=" * 78)
u, v, x, y = sp.symbols("u v x y", real=True)
ck.set_domain()          # no domain restriction needed for pp-waves


def ppwave(H, lab):
    g = Geometry(sp.Matrix([[H, -1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]),
                 [u, v, x, y])
    return g, lab


# harmonic H => vacuum pp-wave (type N, VSI: every polynomial invariant vanishes)
g_a, la = ppwave(x**2 - y**2, "pp-wave  H = x^2 - y^2")
g_b, lb = ppwave(2 * x * y, "pp-wave  H = 2xy  (a 45-degree rotation of the first)")
g_c, lc = ppwave(u**(-2) * (x**2 - y**2), "pp-wave  H = (x^2-y^2)/u^2  (u-dependent amplitude)")

for g_, l_ in [(g_a, la), (g_b, lb), (g_c, lc)]:
    K = sp.simplify(g_.kretschmann)
    Rs = sp.simplify(g_.ricci_scalar)
    vac = g_.ricci.is_zero_matrix
    print(f"  {l_:52s} vacuum={vac}  Kretschmann={K}  R={Rs}")
print("  => every polynomial curvature invariant VANISHES for all three: the §02 fingerprint")
print("     filter reports BLIND_SPOT and cannot separate them. Now CK:\n")

def pp_tetrad(H):
    """The natural pp-wave null frame: l = d_v (null), n = d_u + (H/2) d_v, m = (d_x+i d_y)/sqrt2.
    Gram-Schmidt cannot start here (no coordinate direction is reliably timelike: g_vv = 0 and
    g_uu = H changes sign), so we seed the frame -- canonicalization does the rest."""
    s2 = sp.sqrt(2)
    return ([0, 1, 0, 0], [1, H / 2, 0, 0],
            [0, 0, 1 / s2, sp.I / s2], [0, 0, 1 / s2, -sp.I / s2])


HS = {la: x**2 - y**2, lb: 2 * x * y, lc: (x**2 - y**2) / u**2}
sigs = {}
for g_, l_ in [(g_a, la), (g_b, lb), (g_c, lc)]:
    stamp(f"CK signature: {l_}")
    s = ck.ck_signature(g_, l_, tet=pp_tetrad(HS[l_]))
    sigs[l_] = s
    print(f"     petrov={s['petrov']} iso={s['isotropy_dim']} t0={s['t0']} t1={s['t1']}")
    print(f"     Psi = {s['psi']}")
    print(f"     order1 components = {s['order1_components']}   nabla_C_zero = {s['nabla_C_zero']}")
    print(f"     order1 INVARIANTS = {s['order1_invariants']}")
    print(f"     certificate = {s['certificate']}  failures={s['cert_failures']}")

print("\n--- VSI VERDICTS ---")
v1, w1 = ck.equivalent(sigs[la], sigs[lb])
print(f"  {la}\n     vs {lb}\n     -> {v1}   (ground truth: EQUIVALENT -- a 45-degree rotation)")
for wl in w1[:3]:
    print(f"        · {wl}")
v2, w2 = ck.equivalent(sigs[la], sigs[lc])
print(f"  {la}\n     vs {lc}\n     -> {v2}   (ground truth: INEQUIVALENT -- u-dependent amplitude)")
for wl in w2[:3]:
    print(f"        · {wl}")

stamp("SPIKE COMPLETE")
