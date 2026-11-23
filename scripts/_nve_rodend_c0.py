"""c0 at the rod endpoints, and the real-line branch of c0'' on the lower axis (Bridge rev-3 item 9; 2026-11-24).
Declared peak < 100 MB; guard aborts at ru_maxrss > 1.5 GB. Run: NVE_SPIN=<a> nice -n 10 .venv/bin/python
scripts/_nve_rodend_c0.py  (appends to data/nve/rodend_c0.out).

Hand claim being checked (MRS §3 note 2026-11-24): for 0 < k <= 30/7, B(u^2, k) > 0 on the real line, so along each real
segment of U (u > 1 and u < 1; the tree crosses R only at u = 1) sqrt(B) keeps one sign. It is + as u -> +inf (the
normalisation) and, continuing through infinity, + as u -> -inf for k < 30/7 (sqrt(B) ~ sqrt(90 - 21k) u^2 is even) but
- at k = 30/7 (sqrt(B) ~ sqrt(120/7) u is odd). Hence
  upper side:  c0(z) =  int_z^inf (s - z) c0''(s) ds        with c0'' < 0         -> c0 < 0 at z = 1 + sqrt(1 - a^2)
  lower side:  c0(z) =  int_-inf^z (z - s) c0''(s) ds       with c0'' < 0 (k < 30/7), > 0 (k = 30/7)
and c0 != 0 at both rod endpoints. Cross-check of the branch: the code's own Laurent series at infinity
(_nve_lower.c0_laurent, analytic in 1/z, so it IS the continuation through infinity) evaluated at z = +2 and z = -2
must equal these real-line quadratures, wherever rho_c < 2 (k <= 4.1)."""
import os
import resource
import sys

import mpmath as mp
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_lower as L          # noqa: E402

mp.mp.dps = 40
A = mp.mpf(sp.N(L.A, 50))
SIG = mp.sqrt(1 - A**2)
CAP = 1.5 * 1024**3
OUT = os.path.join(L.OUT, "rodend_c0.out")


def guard():
    if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > CAP:
        print("ABORT: memory cap"); sys.exit(2)


def c0pp(s, k, sgn):
    u = s / A
    w = u * u
    B = (90 - 21 * k) * w * w - (60 - 18 * k) * w + (10 - k)
    return -sgn * 2 * mp.sqrt(10) / (5 * A**3) * mp.sqrt(B) / (w + 1) ** 3


def c0_upper(z, k):
    return mp.quad(lambda s: (s - z) * c0pp(s, k, 1), [z, z + 1, z + 10, mp.inf])


def c0_lower(z, k):
    sgn = -1 if k == mp.mpf(30) / 7 else 1
    return mp.quad(lambda s: (z - s) * c0pp(s, k, sgn), [-mp.inf, z - 10, z - 1, z])


lines = [f"spin a = {L.A}: rod endpoints z = {mp.nstr(1 - SIG, 12)}, {mp.nstr(1 + SIG, 12)}"]
ks = [sp.Rational(1, 10**6), sp.Rational(1, 100), sp.Rational(1, 2), 1, 2, 3, sp.Rational(39, 10), 4,
      sp.Rational(41, 10), sp.Rational(42, 10), sp.Rational(30, 7) - sp.Rational(1, 10**6), sp.Rational(30, 7)]
for kr in ks:
    k = mp.mpf(sp.N(kr, 50))
    lo, up = c0_lower(1 - SIG, k), c0_upper(1 + SIG, k)
    row = f"k = {mp.nstr(k, 10):>14}: c0(lower rod end) = {mp.nstr(lo, 12):>16}   c0(upper rod end) = {mp.nstr(up, 12):>16}"
    C = None
    try:
        C, rho, _nw, _ = L.c0_laurent(kr)          # fails (no convergent series to |z| = 0.9) once rho_c is too big
    except (StopIteration, RuntimeError, ValueError, ZeroDivisionError):
        row += "   (Laurent series unavailable here: rho_c too large)"
    if C is not None:
        if rho < 1.9:
            dl = abs(L.c0_eval(C, mp.mpf(-2)) - c0_lower(mp.mpf(-2), k))
            du = abs(L.c0_eval(C, mp.mpf(2)) - c0_upper(mp.mpf(2), k))
            row += f"   Laurent vs quadrature at z=-2: {mp.nstr(dl, 3)}, at z=+2: {mp.nstr(du, 3)} (rho_c {mp.nstr(rho, 3)})"
    # must-fail: the wrong lower-side branch (opposite sign) must disagree with Laurent at z = -2
    if kr == 1 and C is not None:
        wrong = -c0_lower(mp.mpf(-2), k)
        row += f"   [must-fail, wrong lower branch: diff {mp.nstr(abs(L.c0_eval(C, mp.mpf(-2)) - wrong), 3)}]"
    lines.append(row)
    print(row, flush=True)
    guard()
k0 = mp.mpf(1) / 10**6
lines.append(f"c0''(z = 0) at k = 1e-6: {mp.nstr(c0pp(mp.mpf(0), k0, 1), 10)};  Kerr c0''(0) = +4/a^3 = {mp.nstr(4 / A**3, 10)}")
lines.append(f"peak ru_maxrss = {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.1f} MB")
print(lines[-2]); print(lines[-1])
with open(OUT, "a") as fh:
    fh.write("\n".join(lines) + "\n\n")
