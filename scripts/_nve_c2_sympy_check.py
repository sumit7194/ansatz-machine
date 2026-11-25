"""Office check of Fable's C2_ANALYTIC.md (branch fable/2026-11-25-c2-analytic, 5b6110b), the exact parts (2026-11-25).
Declared peak < 300 MB (small rational expressions); guard at 1.5 GB. Seconds. Independent of Fable's script.
    nice -n 12 .venv/bin/python scripts/_nve_c2_sympy_check.py   -> data/nve/c2_sympy_check.out
Checks (each prints PASS/FAIL):
 S1  c1'' = d/dk c0''|_{k=0}, from the repo's radicand(): d/dk (c0'')^2 = 2 c_K'' c1''  (symbolic in z, at spin 3/5,
     and with a symbolic spin through the family formula).
 S2  Fable's partial fractions of 5a^3 c1''.
 S3  Fable's closed forms: d/du R1 = -Rr, d/du Iu = -R1 (so Iu'' = Rr), and Iu, R1 -> 0 as u -> +inf.
 S4  f0- = Delta/D at k = 0; d f0-/dk = 4 a Delta c1 / D^2.
 S5  the Wronskian of v+- = (N D)^(1/4) exp(+-kappa U) is -2 kappa, and they solve v'' + (3/16)(P'/P)^2 v = 0
     (T38 addendum identity, rechecked symbolically for the Kerr lower-axis data).
 S6  must-fail: a wrong sign in the partial fractions is detected."""
import os
import resource
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("NVE_SPIN", "3/5")
import _nve_lower as L     # noqa: E402

out = []


def say(s):
    print(s, flush=True)
    out.append(s)


def check(name, expr):
    ok = sp.simplify(expr) == 0
    say(f"{name}: {'PASS' if ok else 'FAIL'}")
    if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > 1.5 * 1024**3:
        say("ABORT: memory"); sys.exit(2)
    return ok


z, u, a, k, E = sp.symbols("z u a k E", positive=True)
w = u**2
# S1 at spin 3/5 against the repo's radicand()
A35 = L.A
zz = L.z
R = L.radicand(k)                                   # (c0'')^2 as used by the engine, k symbolic
cK2 = sp.diff(-2 * A35 / (zz**2 + A35**2), zz, 2)
c1pp_repo = sp.diff(R, k).subs(k, 0) / (2 * cK2)
uu = zz / A35
c1pp_fable = (21 * uu**4 - 18 * uu**2 + 1) / (5 * A35**3 * (uu**2 + 1) ** 3 * (3 * uu**2 - 1))
check("S1a c1'' (Fable) = d/dk c0'' at k=0 from radicand(), spin 3/5", c1pp_repo - c1pp_fable)
# S1b symbolic spin, via the family formula (c0'')^2 = 8B/(5a^6(u^2+1)^6) and Kerr's c_K''
B = (90 - 21 * k) * w**2 - (60 - 18 * k) * w + (10 - k)
cKpp_u = -4 * (3 * u**2 - 1) / (a**3 * (u**2 + 1) ** 3)          # Kerr's c0'' in u (z-derivatives)
c1pp_sym = sp.diff(8 * B / (5 * a**6 * (w + 1) ** 6), k).subs(k, 0) / (2 * cKpp_u)
check("S1b same, symbolic spin", c1pp_sym - (21 * u**4 - 18 * u**2 + 1) / (5 * a**3 * (u**2 + 1) ** 3 * (3 * u**2 - 1)))
# S2 partial fractions
Rr = (21 * u**4 - 18 * u**2 + 1) / ((u**2 + 1) ** 3 * (3 * u**2 - 1))
pf = -sp.Rational(9, 8) / (3 * u**2 - 1) + sp.Rational(3, 8) / (u**2 + 1) + sp.Rational(15, 2) / (u**2 + 1) ** 2 - 10 / (u**2 + 1) ** 3
check("S2 partial fractions", Rr - pf)
# S3 closed forms (as in Fable's script: acot = (1/2i) log((u+i)/(u-i)), Lg = log((sqrt3 u - 1)/(sqrt3 u + 1)))
S3 = sp.sqrt(3)
acot = sp.log((u + sp.I) / (u - sp.I)) / (2 * sp.I)
Lg = sp.log((S3 * u - 1) / (S3 * u + 1))
R1 = sp.Rational(3, 8) * acot + 3 * S3 / 16 * Lg + sp.Rational(5, 2) * u / (u**2 + 1) ** 2
Iu = sp.Rational(5, 4) / (u**2 + 1) - sp.Rational(3, 8) * u * acot - 3 * S3 / 16 * u * Lg \
    - sp.Rational(3, 16) * sp.log((u**2 + 1) / (u**2 - sp.Rational(1, 3)))
check("S3a dR1/du = -Rr", sp.diff(R1, u) + Rr)
check("S3b dIu/du = -R1", sp.diff(Iu, u) + R1)
lim1, lim2 = sp.limit(R1, u, sp.oo), sp.limit(Iu, u, sp.oo)
say(f"S3c limits at u -> +inf: R1 -> {lim1}, Iu -> {lim2}: {'PASS' if lim1 == 0 and lim2 == 0 else 'FAIL'}")
lead = sp.limit(Iu * u**2, u, sp.oo)
say(f"S3d u^2 Iu -> {lead} (so c1 = Iu/(5a) ~ (7/30) a / z^2 iff this is 7/6): {'PASS' if lead == sp.Rational(7, 6) else 'FAIL'}")
# S4 lower-axis data at k = 0
Dp, Dl, Dm = z**2 + a**2, z**2 - 2 * z + a**2, (z - 2) ** 2 + a**2
f0, cK, c = Dl / Dp, -2 * a / Dp, sp.symbols("c")
f0m = f0 / (f0**2 + c**2)
check("S4a f0- = Delta/D at k = 0", f0m.subs(c, cK) - Dl / Dm)
check("S4b d f0-/d c0 at k=0 = 4 a Delta / D^2", sp.diff(f0m, c).subs(c, cK) - 4 * a * Dl / Dm**2)
# S5 Kerr solutions: with N = E^2 D - Delta, h = 1/sqrt(N D), v = (N D)^(1/4) exp(kappa U), U' = h
Nn = E**2 * Dm - Dl
P = Nn / Dm
kap = a * sp.sqrt(1 - E**2)
G = Nn * Dm
gq = G ** sp.Rational(1, 4)
# v'' / v for v = g exp(kappa U): g''/g + 2 kappa g' h / g + kappa h' + kappa^2 h^2 ; with g = G^(1/4), h = G^(-1/2)
h = G ** sp.Rational(-1, 2)
vv_over_v = sp.diff(gq, z, 2) / gq + 2 * kap * sp.diff(gq, z) * h / gq + kap * sp.diff(h, z) + kap**2 * h**2
check("S5a v'' + (3/16)(P'/P)^2 v = 0 for v = (ND)^(1/4) exp(+kappa U)", sp.together(vv_over_v + sp.Rational(3, 16) * (sp.diff(P, z) / P) ** 2))
# Wronskian v+ v-' - v+' v- = g^2 (-2 kappa h) = -2 kappa
check("S5b Wronskian = -2 kappa", gq**2 * (-2 * kap * h) + 2 * kap)
# S6 must-fail
bad = check("S6 must-fail (sign flipped in partial fractions) -> expect FAIL", Rr - (pf + sp.Rational(9, 4) / (3 * u**2 - 1)))
say(f"S6 verdict: {'PASS (must-fail fired)' if not bad else 'FAIL (must-fail did not fire)'}")
say(f"peak ru_maxrss = {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")
open(os.path.join(L.OUT, "c2_sympy_check.out"), "w").write("\n".join(out) + "\n")
