#!/usr/bin/env python3
"""Sympy checks for the route (i) segment certificate (data/nve/ROUTE1_SEGMENT.md).
[model: Fable 5.2; UNVERIFIED until the office ansatz-machine checks it]   1 core, a few seconds, peak < 200 MB.
    .venv/bin/python scripts/_nve_route1_kc_identity.py        -> data/nve/eps/route1_seg_identity.out

(1) The closed form referenced to k_c (the brief's generalisation of Part A's k = 0 identity):
        delta = c0 - c0_c,  G2 = G2_c (1 + sigma_c),  sigma_c = (2 c0_c delta + delta^2) / G2_c,
        P = P_c (1 + gamma_c s_c),  s_c = sigma_c / (1 + sigma_c),  gamma_c = f0 / (G2_c P_c).
(2) The derivative rule the certifier actually uses: with c0, c0' depending on k and D0 = d c0/dk, D1 = d c0'/dk,
        d q / dk = (3/8) lam dlam,   lam = dG1/G1 - dG2/G2,
        dlam = ddG1/G1 - dG1 dG1k/G1^2 - ddG2/G2 + dG2 dG2k/G2^2,
    and (2b) the combined form the certifier evaluates (_nve_route1_segment.dq_sup):
        dlam = 2 (f0' c0 D0 + f0 c0' D0 + f0 c0 D1)/(G1 G2) - [2 f0 c0 D0/(G1 G2)] (dG1/G1 + dG2/G2).
(3) The two radial integrals for D0, D1 against the Laurent rule, on a monomial c0'' = zeta^-n.
(4) The closed-form roots of 1 - k phi(w) = 0 used by the Laurent-disc precondition.
Each line prints the simplified difference, which must be 0."""
import os

import sympy as sp

out = []
f0, f0p, c0c, dl, E2 = sp.symbols("f0 f0p c0c delta E2")
G2c = f0**2 + c0c**2
G2 = f0**2 + (c0c + dl)**2
sig = (2 * c0c * dl + dl**2) / G2c
s = sig / (1 + sig)
Pc = E2 - f0 / G2c
P = E2 - f0 / G2
gam = f0 / (G2c * Pc)
out.append(("(1a) G2 - G2_c (1 + sigma_c)", sp.simplify(G2 - G2c * (1 + sig))))
out.append(("(1b) P - P_c (1 + gamma_c s_c)", sp.simplify(P - Pc * (1 + gam * s))))

k = sp.Symbol("k")
c0 = sp.Function("c0")(k)
c0p = sp.Function("c0p")(k)
G2 = f0**2 + c0**2
dG2 = 2 * (f0 * f0p + c0 * c0p)
G1 = E2 * G2 - f0
dG1 = E2 * dG2 - f0p
lam = dG1 / G1 - dG2 / G2
q = sp.Rational(3, 16) * lam**2
D0, D1 = sp.diff(c0, k), sp.diff(c0p, k)
G2k = 2 * c0 * D0
dG2k = 2 * (D0 * c0p + c0 * D1)
G1k = E2 * G2k
dG1k = E2 * dG2k
dlam = dG1k / G1 - dG1 * G1k / G1**2 - dG2k / G2 + dG2 * G2k / G2**2
out.append(("(2) dq/dk - (3/8) lam dlam", sp.simplify(sp.diff(q, k) - sp.Rational(3, 8) * lam * dlam)))
# (2b) the same derivative with the E^2 terms combined first (the form the certifier evaluates; less cancellation):
#      d log P / dk = 2 f0 c0 D0 / (G1 G2),  dlam = d/dz of it
X = 2 * f0 * c0 * D0 / (G1 * G2)
dlam2 = 2 * (f0p * c0 * D0 + f0 * c0p * D0 + f0 * c0 * D1) / (G1 * G2) - X * (dG1 / G1 + dG2 / G2)
out.append(("(2b) dlam (combined form) - dlam", sp.simplify(dlam2 - dlam)))

z, sv = sp.symbols("z s", positive=True)
for n in (4, 5, 9):
    g = 1                                                     # c0'' = zeta^-n = omega^4 * omega^(n-4), omega = s/z
    gk = (sv / z) ** (n - 4)
    i0 = sp.integrate((sv - sv**2) * gk, (sv, 0, 1)) / z**2
    i1 = -sp.integrate(sv**2 * gk, (sv, 0, 1)) / z**3
    out.append((f"(3) n = {n}: c0 integral - z^(2-n)/((n-1)(n-2))", sp.simplify(i0 - z**(2 - n) / ((n - 1) * (n - 2)))))
    out.append((f"(3) n = {n}: c0' integral + z^(1-n)/(n-1)", sp.simplify(i1 + z**(1 - n) / (n - 1))))

w = sp.Symbol("w")
phi = (21 * w**2 - 18 * w + 1) / (10 * (3 * w - 1)**2)
for sgn in (1, -1):
    root = ((30 - 9 * k) + sgn * sp.sqrt(60 * k * (k - 4))) / (90 - 21 * k)
    out.append((f"(4) 1 - k phi at the root ({'+' if sgn > 0 else '-'})", sp.simplify((1 - k * phi).subs(w, root))))
a, om = sp.symbols("a omega")
x = a**2 * om**2
phi_om = (21 - 18 * x + x**2) / (10 * (3 - x)**2)
out.append(("(4) phi(omega form, x = a^2 omega^2) - phi(w = 1/x)", sp.simplify(phi_om - phi.subs(w, 1 / x))))

ok = all(v == 0 for _, v in out)
lines = [f"sympy {sp.__version__}"] + [f"  {nm}: {v}" for nm, v in out] + [f"ALL ZERO: {ok}"]
print("\n".join(lines))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "data", "nve", "eps", "route1_seg_identity.out"), "w") as fh:
    fh.write("\n".join(lines) + "\n")
