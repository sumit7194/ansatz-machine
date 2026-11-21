"""T38 point 2a (for the Bridge): the first-order axis NVE v'' + (3/16)(P'/P)^2 v = 0 with P = E^2 - mu^2 f0,
f0 = Delta/D, D = (z-z1)(z-z2) two simple poles, has the Liouvillian solutions v = (N D)^(1/4) exp(+-kappa u),
u = int dz / sqrt(N D), N = E^2 D - mu^2 Delta, with
    kappa^2 = [E^2 (z1-z2)^2 + mu^2 (2 a0 + a1 (z1+z2) + 2 a2 z1 z2)] / 4      (Delta = a2 z^2 + a1 z + a0).
(1) symbolic: N D (g''/g + (3/16)(P'/P)^2) with g = (N D)^(1/4) is constant in z, = -kappa^2 (generic data).
(2) cross-check: the predicted trace c (e^{kappa w} + e^{-kappa w}) of the §159 loop M1 (k = 0, Kerr lower axis, E = 4/5)
    against the independent 50-digit monodromy value in data/nve/lower_comm.jsonl.
(3) kappa*omega(E) for that loop at several E: non-constant (G1^0 = C* at generic E).  Output: data/nve/kappa_omega.out"""
import sympy as sp
import mpmath as mp

z, E, mu, z1, z2, a0, a1, a2 = sp.symbols('z E mu z1 z2 a0 a1 a2')
D = (z - z1) * (z - z2); Dl = a2 * z**2 + a1 * z + a0
N = sp.expand(E**2 * D - mu**2 * Dl); P = N / D
g = (N * D) ** sp.Rational(1, 4)
Q = sp.simplify(N * D * (sp.diff(g, z, 2) / g + sp.Rational(3, 16) * (sp.diff(P, z) / P) ** 2))
print("(1) dQ/dz == 0:", sp.simplify(sp.diff(Q, z)) == 0, "; kappa^2 = -Q =", sp.factor(-sp.simplify(Q.subs(z, 0))))

mp.mp.dps = 30
a = mp.mpf(3) / 5


def loop_trace(Ev, n=400):
    Delta = lambda x: x**2 - 2 * x + a**2
    Dd = lambda x: (x - 2)**2 + a**2
    F = lambda x: (Ev**2 * Dd(x) - Delta(x)) * Dd(x)
    kap = mp.sqrt(a**2 * (1 - Ev**2))
    c = [mp.mpc(1.6, 0), mp.mpc(1.6, -0.3), mp.mpc(2.4, -0.3), mp.mpc(2.4, 0.9), mp.mpc(1.6, 0.9), mp.mpc(1.6, 0)]
    pts = [A + (B - A) * j / n for A, B in zip(c[:-1], c[1:]) for j in range(n)] + [c[-1]]
    s = mp.sqrt(F(pts[0])); q = F(pts[0]) ** mp.mpf(0.25); s0, q0 = s, q; om = mp.mpf(0)
    for A, B in zip(pts[:-1], pts[1:]):
        def br(x, ref):
            y = mp.sqrt(F(x)); return y if abs(y - ref) <= abs(y + ref) else -y
        sm, sB = br((A + B) / 2, s), br(B, s)
        qB = min([F(B) ** mp.mpf(0.25) * mp.expj(mp.pi / 2 * m) for m in range(4)], key=lambda x: abs(x - q))
        om += (B - A) / 6 * (1 / s + 4 / sm + 1 / sB); s, q = sB, qB
    cf = q / q0
    return kap, om, cf * (mp.exp(kap * om) + mp.exp(-kap * om))


kap, om, tr = loop_trace(mp.mpf(4) / 5)
print("(2) predicted tr M1 =", mp.nstr(tr, 14), " measured (lower_comm, k=0) = -0.984309504290635 + 2.7772800733203j",
      " |diff| =", mp.nstr(abs(tr - mp.mpc('-0.984309504290635', '2.7772800733203')), 3))
for Ev in ("0.6", "0.7", "0.8", "0.9"):
    kap, om, tr = loop_trace(mp.mpf(Ev))
    print(f"(3) E={Ev}: kappa*omega = {mp.nstr(kap * om, 12)}   |e^(kappa*omega)| = {mp.nstr(abs(mp.exp(kap * om)), 8)}")
