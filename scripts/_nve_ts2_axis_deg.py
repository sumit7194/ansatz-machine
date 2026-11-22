"""deg f0 of Tomimatsu-Sato delta = 2 upper-axis data (Bridge ask, 2026-11-22), with deg as in scripts/_nve_monodromy.py
(max of numerator and denominator degree of the reduced rational f0). The Ernst potential is the one in
scripts/_ts2_build.py, which that script verifies is vacuum (R_ab = 0). Upper axis: y = 1, x > 1, z_c = sigma x.
f0 = Re E continued as a rational function: (E(x) + Ebar(x))/2 with conjugated coefficients. Also: the reflection
test e(x) conj e(-x) = 1, and controls on Kerr (delta = 1), which must give deg 2.
    .venv/bin/python scripts/_nve_ts2_axis_deg.py      -> data/nve/ts2_axis_deg.out"""
import sympy as sp

x = sp.symbols("x", real=True)
out = []


def say(*s):
    line = " ".join(str(v) for v in s)
    print(line, flush=True)
    out.append(line)


def axis_E(delta, p, q):
    y = 1
    if delta == 1:
        N, D = p * x - sp.I * q * y, 1
    else:
        N = p**2 * x**4 + q**2 * y**4 - 1 - 2 * sp.I * p * q * x * y * (x**2 - y**2)
        D = 2 * p * x * (x**2 - 1) - 2 * sp.I * q * y * (1 - y**2)
    xi = N / D
    return sp.cancel((xi - 1) / (xi + 1))


def conjf(e):
    return sp.cancel(sp.conjugate(e).subs(sp.conjugate(x), x))


for tt in (sp.Rational(1, 2), sp.Rational(1, 3), sp.Rational(2, 7)):
    p, q = (1 - tt**2) / (1 + tt**2), 2 * tt / (1 + tt**2)
    for delta in (1, 2):
        e = axis_E(delta, p, q)
        f0 = sp.cancel((e + conjf(e)) / 2)
        n, d = sp.fraction(f0)
        deg = max(sp.degree(n, x), sp.degree(d, x))
        refl = sp.simplify(e * conjf(e).subs(x, -x) - 1)
        say(f"p={p} q={q} delta={delta}: e_+ = {sp.factor(e)}")
        say(f"   f0 = {sp.factor(f0)}   deg f0 = {deg}   reflection e(x) conj e(-x) - 1 = {refl}")
        say(f"   poles of f0 squarefree: {sp.Poly(d, x).sqf_list()[1] == [(sp.Poly(d, x).monic(), 1)] or all(m == 1 for _, m in sp.Poly(d, x).sqf_list()[1])}"
            f"; disc(den) = {sp.discriminant(d, x)}")
open("data/nve/ts2_axis_deg.out", "w").write("\n".join(out) + "\n")
