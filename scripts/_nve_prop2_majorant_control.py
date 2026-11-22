"""Proposition 2 (MRS_SECTION §4b), numerical sanity control for the majorant proof (Bridge ask, 2026-11-22).
v2, BOUNDED MEMORY. v1 used symbolic SymPy rational functions and grew to ~10 GB (resource slip, JOURNAL 2026-11-22).
This version represents every coefficient a_n(z) as a truncated Taylor array in w = z - z0, with mpmath at 30 digits.
Declared peak: < 100 MB. Guard: aborts if ru_maxrss > 1.5 GB (checked every order). Run at nice 10, single core.

1. The complexified Ernst recursion (t = rho^2, E = sum a_n t^n, E~ = sum b_n t^n, c_n = (a_n + b_n)/2):
     4n^2 c0 a_n = - sum_{j=1}^{n-1} 4(n-j)^2 c_j a_{n-j} - sum_{i+j=n-1} c_j a_i'' + 4 sum_{i+j=n, i,j>=1} i j a_i a_j
                   + sum_{i+j=n-1} a_i' a_j'                       (and a <-> b)
   on Kerr's upper-axis data in the claim's shifted z (a0 = (z - ia - 2)/(z - ia), b0 its conjugate function; M = 1,
   spin 3/5). The partial sums are compared with Kerr's exact off-axis Ernst potential at z0 = 6 and several rho.
   Must-fail control: flip the sign of the j-sum; the result must disagree.
2. The majorant's guaranteed radius in t at the disc centre, x0 R^2 with x0 = 4 m^2/(5 e^2 M (4m + 5M)), must not
   exceed the true radius (z0 - 1 - sigma)^2 (the nearest rod end), nor the radius suggested by |a_n|^(-1/n).
    nice -n 10 .venv/bin/python scripts/_nve_prop2_majorant_control.py      -> data/nve/prop2_majorant_control.out"""
import resource
import sys

import mpmath as mp

mp.mp.dps = 30
A = mp.mpf(3) / 5
Z0 = mp.mpf(6)
NMAX = 12
L = 2 * NMAX + 3                       # Taylor length needed: a_n uses 2 derivatives per step
CAP = 1.5 * 1024**3
out = []


def say(*s):
    line = " ".join(str(v) for v in s)
    print(line, flush=True)
    out.append(line)


def guard():
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss          # bytes on macOS
    if rss > CAP:
        say(f"ABORT: ru_maxrss {rss / 1e9:.2f} GB > cap")
        sys.exit(2)
    return rss


def mul(u, v):
    w = [mp.mpc(0)] * L
    for i, ui in enumerate(u):
        if ui == 0:
            continue
        for j in range(L - i):
            w[i + j] += ui * v[j]
    return w


def add(*us):
    return [mp.fsum(col) for col in zip(*us)] if len(us) > 1 else list(us[0])


def scal(s, u):
    return [s * x for x in u]


def der(u):
    return [(k + 1) * u[k + 1] for k in range(L - 1)] + [mp.mpc(0)]


def inv(u):
    w = [mp.mpc(0)] * L
    w[0] = 1 / u[0]
    for k in range(1, L):
        w[k] = -mp.fsum(u[j] * w[k - j] for j in range(1, k + 1)) / u[0]
    return w


def axis_data(sgn):
    # e = 1 - 2/(z - s i a), s = +1 for e, -1 for its conjugate function; Taylor in w = z - Z0
    p = Z0 - sgn * 1j * A
    return [mp.mpc(1) - 2 / p] + [-2 * (-1) ** k / p ** (k + 1) for k in range(1, L)]


def recursion(sign=1):
    a, b = [axis_data(1)], [axis_data(-1)]
    c = lambda j: scal(mp.mpf(1) / 2, add(a[j], b[j]))
    ic0 = inv(c(0))
    for n in range(1, NMAX + 1):
        new = []
        for u in (a, b):
            terms = []
            for j in range(1, n):
                terms.append(scal(-sign * 4 * (n - j) ** 2, mul(c(j), u[n - j])))
            for j in range(0, n):
                terms.append(scal(-1, mul(c(j), der(der(u[n - 1 - j])))))
            for i in range(1, n):
                terms.append(scal(4 * i * (n - i), mul(u[i], u[n - i])))
            for i in range(0, n):
                terms.append(mul(der(u[i]), der(u[n - 1 - i])))
            rhs = add(*terms)
            new.append(scal(mp.mpf(1) / (4 * n**2), mul(ic0, rhs)))
        a.append(new[0])
        b.append(new[1])
        guard()
    return a, b


def kerr_exact(rho):
    s = mp.sqrt(1 - A**2)
    zc = Z0 - 1
    Rp, Rm = mp.sqrt(rho**2 + (zc + s) ** 2), mp.sqrt(rho**2 + (zc - s) ** 2)
    x, y = (Rp + Rm) / (2 * s), (Rp - Rm) / (2 * s)
    return 1 - 2 / (1 + s * x - 1j * A * y)


a, _ = recursion()
vals = [an[0] for an in a]
say("a_n(z0 = 6), n = 0..%d:" % NMAX, [mp.nstr(v, 6) for v in vals])
for rho in (mp.mpf("0.5"), mp.mpf(1), mp.mpf(2), mp.mpf(3)):
    t = rho**2
    ps = mp.fsum(v * t**n for n, v in enumerate(vals))
    ex = kerr_exact(rho)
    say(f"rho={rho}: partial sum (n<={NMAX}) = {mp.nstr(ps, 15)}  exact Kerr = {mp.nstr(ex, 15)}  |diff| = {mp.nstr(abs(ps - ex), 3)}")
af, _ = recursion(sign=-1)
psf = mp.fsum(an[0] for an in af)
say(f"must-fail control (j-sum sign flipped), rho=1: |diff| = {mp.nstr(abs(psf - kerr_exact(mp.mpf(1))), 3)}")
say("|a_n|^(-1/n), n >= 3:", [mp.nstr(abs(v) ** (-mp.mpf(1) / n), 5) for n, v in enumerate(vals) if n >= 3])
sig = mp.sqrt(1 - A**2)
say("true radius in t (nearest rod end, (z0 - 1 - sigma)^2):", mp.nstr((Z0 - 1 - sig) ** 2, 8))
for R in (2, 3, 4):
    pts = [Z0 + R * mp.expj(2 * mp.pi * k / 720) for k in range(720)]
    fa = lambda z: 1 - 2 / (z - 1j * A)
    fb = lambda z: 1 - 2 / (z + 1j * A)
    M = max(max(abs(fa(p)), abs(fb(p))) for p in pts)
    m = min(abs((fa(p) + fb(p)) / 2) for p in pts)
    x0 = 4 * m**2 / (5 * mp.e**2 * M * (4 * m + 5 * M))
    say(f"R={R}: M={mp.nstr(M, 6)} m={mp.nstr(m, 6)} x0={mp.nstr(x0, 6)}  guaranteed radius in t at z0: x0 R^2 = {mp.nstr(x0 * R**2, 6)}")
say(f"peak ru_maxrss = {guard() / 1e6:.1f} MB")
open("data/nve/prop2_majorant_control.out", "w").write("\n".join(out) + "\n")
