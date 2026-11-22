"""T51 point 1: is e_- = 1/e_+ (upper-axis data continued through z = infinity) tied to equatorial reflection symmetry?
Exact (SymPy) checks, in the claim's own coordinate z = z_Weyl + M (so that f0 = 1 - 2Mz/(z^2 + a^2) for Kerr):
  (1) Kerr from its closed-form Ernst potential E = 1 - 2M/(r - i a cos(theta)): the upper axis (theta = 0) is z = r, the
      lower axis (theta = pi) is z = 2M - r. Check e_-(z) * e_+(z) == 1, and evaluate the reflection condition
      e_+(z) conj(e_+(-conj z)) = 1 in BOTH the shifted z (origin not on the equatorial plane) and the centred z_c = z - M.
  (2) Static Weyl, two Curzon particles of UNEQUAL masses (no plane of reflection symmetry): f = exp(2 psi),
      psi = -sum m_i / sqrt(rho^2 + (z - z_i)^2). Check psi_- == -psi_+ (so e_- = 1/e_+) and that no plane z = z0 makes
      the axis data reflection-symmetric.
    .venv/bin/python scripts/_nve_t51_axis_check.py      -> data/nve/t51_axis_check.out"""
import sympy as sp

z, r, a, M, t, z0 = sp.symbols("z r a M t z0", real=True)
m1, m2, z1, z2 = sp.symbols("m1 m2 z1 z2", real=True)
out = []


def say(*s):
    line = " ".join(str(x) for x in s)
    print(line, flush=True)
    out.append(line)


# (1) Kerr, from the closed form, not from the claim's own formulas
E = lambda rr, ct: 1 - 2 * M / (rr - sp.I * a * ct)
e_up = sp.simplify(E(r, 1).subs(r, z))               # theta = 0, z = r
e_lo = sp.simplify(E(r, -1).subs(r, 2 * M - z))      # theta = pi, z = 2M - r
say("Kerr e_+(z) =", sp.factor(e_up), "  e_-(z) =", sp.factor(e_lo))
say("Kerr e_- * e_+ - 1 =", sp.simplify(e_up * e_lo - 1))
f0 = sp.simplify(sp.re(sp.expand_complex(e_up)))
say("Kerr f0 = Re e_+ on real z:", sp.factor(f0))
conjfun = lambda expr: sp.conjugate(expr.subs(z, -z))   # conj(e(-conj z)) for real z
refl_shift = sp.simplify(e_up * conjfun(e_up) - 1)
say("reflection condition in the SHIFTED z (claim's z), e_+(z) conj e_+(-z) - 1 =", sp.factor(refl_shift))
zc = sp.symbols("z_c", real=True)
e_up_c = e_up.subs(z, zc + M)
refl_c = sp.simplify(e_up_c * sp.conjugate(e_up_c.subs(zc, -zc)) - 1)
say("reflection condition in the CENTRED z_c = z - M:", sp.simplify(refl_c))

# (2) two unequal Curzon particles, z1 < z2; upper axis z > z2, lower axis z < z1
psi = lambda rho, zz: -(m1 / sp.sqrt(rho**2 + (zz - z1) ** 2) + m2 / sp.sqrt(rho**2 + (zz - z2) ** 2))
psi_up = -(m1 / (z - z1) + m2 / (z - z2))            # sqrt((z - zi)^2) = z - zi for z > z2
psi_lo = -(m1 / (z1 - z) + m2 / (z2 - z))            # = zi - z for z < z1
chk_up = sp.simplify(psi(0, 10).subs({z1: 0, z2: 1, m1: 1, m2: 3}) - psi_up.subs({z: 10, z1: 0, z2: 1, m1: 1, m2: 3}))
chk_lo = sp.simplify(psi(0, -10).subs({z1: 0, z2: 1, m1: 1, m2: 3}) - psi_lo.subs({z: -10, z1: 0, z2: 1, m1: 1, m2: 3}))
say("two-Curzon axis limits (spot check at z = +-10):", chk_up, chk_lo)
say("two-Curzon psi_- + psi_+ =", sp.simplify(psi_lo + psi_up), " => e_- = exp(2 psi_-) = 1/e_+")
S = sp.series((psi_up.subs(z, z0 + t) + psi_up.subs(z, z0 - t)).subs({m1: 1, m2: 3, z1: 0, z2: 1}), t, sp.oo, 6).removeO()
say("two-Curzon psi_+(z0+t) + psi_+(z0-t), large t, masses 1 and 3 at 0 and 1:", sp.collect(sp.expand(S), t))
c2 = sp.expand(S).coeff(t, -2)
sol = sp.solve(sp.Eq(c2, 0), z0)
say("t^-2 coefficient vanishes only at z0 =", sol)
for s0 in sol:
    say("  at z0 =", s0, "the t^-4 coefficient is", sp.nsimplify(sp.expand(S.subs(z0, s0)).coeff(t, -4)), "(nonzero: no reflection plane)")

open("data/nve/t51_axis_check.out", "w").write("\n".join(out) + "\n")
