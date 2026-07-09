#!/usr/bin/env python3
"""Prototype — §114 Stage A: the FLUX dictionary. 6D Einstein-Maxwell + Lambda6 on the (twisted) T^2.

Setup: the §113 twisted-fibre metric with the KK vectors OFF (A^a=0 -- consistency of that truncation
is itself checked: no source mixes base and fibre when G lives purely on the fibre), plus a 6D Maxwell
field with FLUX WRAPPED ON THE HIDDEN T^2:
    G = n dw1 ^ dw2   (n = const flux quantum),   M = [[P1^2, chi],[chi, P2^2]],  detM = P1^2 P2^2 - chi^2
6D equations (units kappa=1, L = R - 2*Lambda6 - (1/4) G^2):
    E_MN := R_MN - 1/2 g_MN R + Lambda6 g_MN - [G_MP G_N^P - 1/4 g_MN G^2] = 0
    Maxwell: nabla_M G^{MN} = 0  and dG = 0.

DELIVERABLES of this prototype (machine-extracted, over the free family {f,h,P1,P2,chi}(r)):
  (1) Maxwell on the flux ansatz holds IDENTICALLY (dG=0 trivially; d*G=0 to be verified).
  (2) The base<->fibre mixed equations E_{mu,w_a} vanish identically (A^a=0 truncation consistent
      in the presence of pure-fibre flux).
  (3) The fibre-sector equations: kinetic structure = §112/§113 dictionary + EXTRACTED flux/Lambda6
      source terms (printed -- these become the potential's gradient in the atlas).
  (4) G^2 = 2 n^2 / detM  -- so the flux potential depends on the moduli ONLY through detM
      (volume+axion), never the shape: the machine sees which moduli the flux can stabilize.
Durable log data/flux_dict_proto.log.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry, zero_simplify

t, r, th, ph, w1, w2 = sp.symbols("t r theta phi w1 w2", real=True)
n, L6 = sp.symbols("n Lambda6", real=True)

f = sp.Function("f", positive=True)(r)
h = sp.Function("h", positive=True)(r)
P1 = sp.Function("Phi1", positive=True)(r)
P2 = sp.Function("Phi2", positive=True)(r)
chi = sp.Function("chi")(r)

g4 = sp.diag(-f, h, r**2, r**2 * sp.sin(th)**2)
M = sp.Matrix([[P1**2, chi], [chi, P2**2]])
detM = P1**2 * P2**2 - chi**2

X6 = [t, r, th, ph, w1, w2]
g6 = sp.zeros(6)
for m_ in range(4):
    for n_ in range(4):
        g6[m_, n_] = g4[m_, n_]
for a in range(2):
    for b in range(2):
        g6[4 + a, 4 + b] = M[a, b]

# 6D Maxwell field strength: G_{w1 w2} = n, antisymmetric, all else zero
G = sp.zeros(6)
G[4, 5] = n
G[5, 4] = -n

print("§114 Stage A -- flux dictionary: 6D Einstein-Maxwell + Lambda6, flux n on the twisted T^2\n")
print("  computing 6D geometry (free family f,h,Phi1,Phi2,chi of r)...")
sys.stdout.flush()
geo = Geometry(g6, X6)
R6 = geo.ricci
g6inv = g6.inv()
Rs = sp.simplify(sum(g6inv[i, j] * R6[i, j] for i in range(6) for j in range(6)))
print("  done. R6 scalar computed.")
sys.stdout.flush()

# G with upper indices; G^2
Gup = sp.zeros(6)
for i in range(6):
    for j in range(6):
        Gup[i, j] = sum(g6inv[i, p] * g6inv[j, q] * G[p, q] for p in range(6) for q in range(6))
G2 = sp.simplify(sum(G[i, j] * Gup[i, j] for i in range(6) for j in range(6)))
print(f"\n  (4) G^2 = {G2}")
print(f"      check G^2 - 2n^2/detM = {zero_simplify(sp.simplify(G2 - 2*n**2/detM))}  (0 = flux sees ONLY detM: volume+axion, never shape)")

# (1) Maxwell: nabla_M G^{MN} = (1/sqrt(g)) d_M (sqrt(g) G^{MN})
sq = sp.sqrt(-g6.det())
sq = sq.subs(sp.Abs(sp.sin(th)), sp.sin(th))
mx = [zero_simplify(sp.simplify(sum(sp.diff(sq * Gup[m_, n_], X6[m_]) for m_ in range(6)) / sq)) for n_ in range(6)]
print(f"\n  (1) Maxwell d*G components (all must be 0): {mx}")

# stress tensor and Einstein equations
T = sp.zeros(6)
for i in range(6):
    for j in range(6):
        T[i, j] = sum(G[i, p] * g6inv[p, q] * G[j, q] for p in range(6) for q in range(6)) - sp.Rational(1, 4) * g6[i, j] * G2
E = sp.zeros(6)
for i in range(6):
    for j in range(6):
        E[i, j] = R6[i, j] - sp.Rational(1, 2) * g6[i, j] * Rs + L6 * g6[i, j] - T[i, j]

# (2) mixed base-fibre equations vanish identically
mixed = [zero_simplify(sp.simplify(E[m_, 4 + a])) for m_ in range(4) for a in range(2)]
print(f"\n  (2) mixed E(mu, w_a) (all must be 0 -- A=0 truncation consistent under pure-fibre flux): {mixed}")

# (3) fibre-sector equations with sources extracted (use Ricci-form for readability:
#     R_MN = T_MN - g_MN T/(D-2) + 2 Lambda6 g_MN/(D-2), D=6)
Ttr = sp.simplify(sum(g6inv[i, j] * T[i, j] for i in range(6) for j in range(6)))
for (i, j, lab) in [(4, 4, "w1w1"), (5, 5, "w2w2"), (4, 5, "w1w2")]:
    rhs = sp.simplify(T[i, j] - g6[i, j] * Ttr / 4 + g6[i, j] * L6 / 2)
    print(f"\n  (3) [{lab}]  R6 = {sp.simplify(R6[i, j])}")
    print(f"      source (flux+Lambda6) = {rhs}")

print("\nDONE -- dictionary sources extracted.")
