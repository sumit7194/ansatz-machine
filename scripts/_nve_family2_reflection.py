"""Is family (ii) equatorially reflection-symmetric for some k != 0? (Bridge ask, 2026-11-22; decides how Markakis 2014
is cited.)
Criterion (Ernst-Manko-Ruiz 2006, gr-qc/0701112, Eqs. 52-54; equivalent to Kordas / Meinel-Neugebauer
e(z_c) conj e(-z_c) = 1): with z_c the CENTRED Weyl coordinate, xi = (1 - e)/(1 + e) and
xi~(zbar) = z_c * xi on the upper axis = sum m_n zbar^n (zbar = 1/z_c), an asymptotically flat solution is
equatorially symmetric about z_c = 0 iff m_n is real for even n and imaginary for odd n.
A plane elsewhere (z_c = c) is a shift of origin. So we also test every real c: Re m_1 = 0 fixes c, then the next orders
must hold.
Family (ii), in the claim's conventions (M = 1; z = z_Weyl + 1, so z_c = z - 1; u = z/a):
  f0 = 1 - 2z/(z^2 + a^2) (Kerr's), and d^2 c0/du^2 = -sqrt(8/5) s^4 sqrt(Bh(s^2)) / (a (1 + s^2)^3), s = 1/u,
  Bh = (90 - 21k) - (60 - 18k) s^2 + (10 - k) s^4 (positive branch at s = 0), c0 = O(s^2), integrated twice from u = inf.
Exact arithmetic: R = sqrt(90 - 21k) is a symbol (k = (90 - R^2)/21), so every coefficient is rational in (R, a, c).
All series are truncated power series in zbar (real and imaginary parts carried separately; no simplify of big
expressions).
Control: k = 0 (R = sqrt 90) must reproduce Kerr's c0 = -2a/(z^2 + a^2) and pass at c = 0.
    .venv/bin/python scripts/_nve_family2_reflection.py      -> data/nve/family2_reflection.out"""
import sympy as sp

R, a, s, t, c = sp.symbols("R a s t c", real=True)     # t = zbar' = 1/(z_c - c)
NS = 10                                                   # orders in s
NT = 6                                                    # orders in t checked: m_0 .. m_5
out = []


def say(*x):
    line = " ".join(str(y) for y in x)
    print(line, flush=True)
    out.append(line)


def trunc(expr, var, n):
    p = sp.Poly(sp.expand(expr), var)
    return sum(cf * var**m for (m,), cf in p.terms() if m < n)


def mul(x, y, var, n):
    return trunc(sp.expand(x * y), var, n)


def inv(x, var, n):
    """1/x for a truncated series x with x(0) != 0."""
    x0 = sp.expand(x).subs(var, 0)
    d = sp.expand(x / x0 - 1)
    acc, term = 1, 1
    for _ in range(1, n):
        term = mul(term, -d, var, n)
        acc += term
    return sp.expand(trunc(acc, var, n) / x0)


k = (90 - R**2) / 21
# sqrt(Bh) = R sqrt(1 + q), q = (-(60 - 18k) s^2 + (10 - k) s^4)/R^2
q = sp.expand((-(60 - 18 * k) * s**2 + (10 - k) * s**4) / R**2)
sq, term = 1, 1
for j in range(1, NS):
    term = mul(term, q, s, 2 * NS)
    sq += sp.binomial(sp.Rational(1, 2), j) * term
sq = trunc(sp.expand(R * sq), s, 2 * NS)
den = inv(sp.expand((1 + s**2) ** 3), s, 2 * NS)
d2 = sp.expand(-sp.sqrt(sp.Rational(8, 5)) * s**4 * mul(sq, den, s, 2 * NS))
c0 = 0
for j in range(2, NS):
    bj = sp.expand(d2).coeff(s, 2 * j)
    c0 += bj * s ** (2 * j - 2) / ((2 * j - 1) * (2 * j - 2))
c0 = sp.expand(c0 / a)
kerr = trunc(sp.series(-(2 / a) * s**2 / (1 + s**2), s, 0, 2 * NS - 2).removeO(), s, 2 * NS - 2)
say("control k=0: c0 - Kerr's c0 (series in s) =", sp.simplify(trunc(c0, s, 2 * NS - 2).subs(R, sp.sqrt(90)) - kerr))

# upper axis, in t = 1/(z_c - c): z = z_c + 1 = 1/t + c + 1, s = a/z = a t/(1 + (c + 1) t)
s_t = trunc(sp.series(a * t / (1 + (c + 1) * t), t, 0, NT + 2).removeO(), t, NT + 2)
powers = {0: 1}
for m in range(1, 2 * NS):
    powers[m] = mul(powers[m - 1], s_t, t, NT + 2)
c0_t = sp.expand(sum(sp.expand(c0).coeff(s, m) * powers[m] for m in range(1, 2 * NS)))
c0_t = trunc(c0_t, t, NT + 2)
# f0 = 1 - 2z/(z^2 + a^2) = 1 - 2 (1/s) s^2/a^2 ... write in s: z = a/s -> f0 = 1 - 2 a s/(a^2 (1 + s^2)) * ... :
# 2z/(z^2 + a^2) = 2 (a/s)/(a^2/s^2 + a^2) = (2/a) s/(1 + s^2)
f0_s = 1 - (2 / a) * mul(s, inv(1 + s**2, s, 2 * NS), s, 2 * NS)
f0_t = trunc(sp.expand(sum(sp.expand(f0_s).coeff(s, m) * powers[m] for m in range(0, 2 * NS))), t, NT + 2)
# xi = (1 - e)/(1 + e), e = f0 + i c0. xi~ = (z_c - c) xi = xi / t. Note 1 - e = O(t), so xi = O(t).
num_re, num_im = sp.expand(1 - f0_t), sp.expand(-c0_t)
den_re, den_im = sp.expand(1 + f0_t), sp.expand(c0_t)
# 1/(A + iB) = (A - iB)/(A^2 + B^2)
mod = inv(sp.expand(mul(den_re, den_re, t, NT + 2) + mul(den_im, den_im, t, NT + 2)), t, NT + 2)
inv_re, inv_im = mul(den_re, mod, t, NT + 2), mul(-den_im, mod, t, NT + 2)
xi_re = sp.expand(mul(num_re, inv_re, t, NT + 2) - mul(num_im, inv_im, t, NT + 2))
xi_im = sp.expand(mul(num_re, inv_im, t, NT + 2) + mul(num_im, inv_re, t, NT + 2))
m_re = [sp.factor(sp.cancel(xi_re.coeff(t, n + 1))) for n in range(NT)]
m_im = [sp.factor(sp.cancel(xi_im.coeff(t, n + 1))) for n in range(NT)]
viol = [m_im[n] if n % 2 == 0 else m_re[n] for n in range(NT)]
for n in range(NT):
    say(f"m_{n}: Re = {m_re[n]}")
    say(f"      Im = {m_im[n]}")
    say(f"      symmetry-violating part = {viol[n]}")
R0 = sp.sqrt(90)
say("control k = 0 (R = sqrt 90), c = 0: violating parts =", [sp.simplify(v.subs({R: R0, c: 0})) for v in viol])
cs = sp.solve(sp.Eq(viol[1], 0), c)
say("Re m_1 = 0 forces c =", cs)
for cc in cs:
    rest = [sp.factor(sp.cancel(v.subs(c, cc))) for v in viol[2:]]
    for n, v in enumerate(rest, start=2):
        say(f"  at c = {cc}: violating part of m_{n} =", v)
    # which R (i.e. k) make ALL vanish, for generic a?
    sol = sp.solve([sp.numer(sp.together(v)) for v in rest if v != 0], R, dict=True)
    say("  common real solutions in R = sqrt(90 - 21k):", sol, " (k = (90 - R^2)/21)")
for kv in (sp.Rational(1, 2), 1, 2, 4, sp.Rational(30, 7)):
    Rv = sp.sqrt(90 - 21 * kv)
    for cc in cs:
        vals = [sp.N(v.subs({R: Rv, c: cc, a: sp.Rational(3, 5)}), 12) for v in viol]
        say(f"a=3/5 k={kv} c={sp.N(cc.subs({R: Rv, a: sp.Rational(3, 5)}), 8)}: violating m_0..m_{NT - 1} =", [str(v) for v in vals])
open("data/nve/family2_reflection.out", "w").write("\n".join(out) + "\n")
