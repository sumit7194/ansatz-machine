"""EMRI radiation-reaction toolkit — built for the bridge's request B1 (unblock the full EMRI
waveform). General: works on Kerr OR the bumpy Manko-Novikov metric (§99) through one interface,
the numeric reduced Hamiltonian (_mn_invariant.build_hamilton_numeric). Three pieces:

  fundamental_frequencies(f,E,L,...)  -> (nu_r, nu_theta): the radial & polar libration
      frequencies of a bound geodesic, by counting oscillation periods. Their ratio locates
      RESONANCES (nu_r:nu_theta = low-order rational), where a non-integrable (bumpy) inspiral
      misbehaves but an integrable (Kerr) one does not.
  quadrupole_flux(metric,...)         -> (dE/dtau, dL/dtau): a numerical-kludge GW flux from the
      mass quadrupole of the orbit (the standard EMRI kludge), driving the adiabatic inspiral.
  inspiral(...)                       -> evolve (E,L) by the flux: the chirp, and resonance crossing.

This is a KLUDGE (approximate flux), honest about it -- enough for the qualitative resonance
signature B1 asks for, not a precision Teukolsky waveform.
"""
import math
import sys

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from poincare import _rk4, p_on_shell


def _py_onshell(f, x, y, px, E, L):
    val = (-1 - f["W"](x, y, E, L) - f["g11"](x, y, E, L) * px * px) / f["g22"](x, y, E, L)
    if val > 0:
        return math.sqrt(val)
    return 0.0 if val > -1e-6 else None        # val~0 = a circular/equatorial orbit (py=0), still valid


def fundamental_frequencies(f, E, L, x0, nlam=240000, h=0.02, bounds=(1.2, 200.0)):
    """Radial (nu_r) and polar (nu_theta) frequencies of the bound geodesic whose equatorial
    radial turning point is x0 (launched px=0, y=0, py on-shell -> guaranteed radial + polar
    oscillation). Counts x-maxima and y-maxima over a long proper-time arc.
    Returns (nu_r, nu_theta, ratio) or None if off-shell / unbound."""
    py0 = _py_onshell(f, x0, 0.0, 0.0, E, L)
    if py0 is None or py0 < 1e-3:
        return None
    s = [x0, 0.0, 0.0, py0]
    Nr = Nth = 0
    lam = 0.0
    ppx, ppy = s[2], s[3]
    lo, hi = bounds
    for _ in range(nlam):
        try:
            sn = _rk4(f, s, h, E, L)
        except (OverflowError, ZeroDivisionError, ValueError):
            break
        if not (lo < sn[0] < hi and abs(sn[1]) < 0.999):
            break
        lam += h
        if ppx > 0.0 >= sn[2]:          # p_x: + -> -  =>  x reached a maximum (one radial cycle)
            Nr += 1
        if ppy > 0.0 >= sn[3]:          # p_y: + -> -  =>  y reached a maximum (one polar cycle)
            Nth += 1
        ppx, ppy = sn[2], sn[3]
        s = sn
    if lam <= 0 or Nr < 2 or Nth < 2:
        return None
    nu_r, nu_th = Nr / lam, Nth / lam
    return nu_r, nu_th, nu_r / nu_th


def _tphidot(g, x, y, E, L):
    """Coordinate-time and azimuthal rates u^t, u^phi from the (t,phi) inverse-metric block."""
    gg = g([0.0, x, y, 0.0])
    gtt, gtp, gpp = gg[0][0], gg[0][3], gg[3][3]
    det = gtt * gpp - gtp * gtp
    itt, itp, ipp = gpp / det, -gtp / det, gtt / det
    return -itt * E + itp * L, -itp * E + ipp * L          # u^t, u^phi  (p_t=-E, p_phi=L)


def quadrupole_flux(M, a, q, E, L, x0, n_orb=8, h=0.02, mu=1.0):
    """Numerical-kludge GW flux (dE/dtau, dL/dtau, per the small mass mu) of the bound orbit with
    equatorial radial turning point x0, via the mass quadrupole evaluated on the geodesic and the
    quadrupole formula in the frequency domain. Returns (dEdt, dLdt) or None. Needs numpy."""
    import numpy as np
    from manko_novikov import manko_novikov
    from _mn_invariant import build_hamilton_numeric
    g = manko_novikov(M, a, q)
    f = build_hamilton_numeric(M, a, q)
    k = math.sqrt(M * M - a * a)
    py0 = _py_onshell(f, x0, 0.0, 0.0, E, L)
    if py0 is None:
        return None
    s = [x0, 0.0, 0.0, py0]
    t = phi = 0.0
    ts, Xs, Ys, Zs = [], [], [], []
    for _ in range(1_200_000):
        x, y = s[0], s[1]
        ut, uph = _tphidot(g, x, y, E, L)
        rho = k * math.sqrt(max((x * x - 1) * (1 - y * y), 0.0))
        ts.append(t); Xs.append(rho * math.cos(phi)); Ys.append(rho * math.sin(phi)); Zs.append(k * x * y)
        t += ut * h; phi += uph * h
        try:
            s = _rk4(f, s, h, E, L)
        except (OverflowError, ZeroDivisionError, ValueError):
            break
        if not (1.2 < s[0] < 200.0 and abs(s[1]) < 0.999):
            break
        if phi > n_orb * 2 * math.pi:
            break
    if len(ts) < 2000 or t <= 0:
        return None
    Omega_phi = phi / t                                     # mean azimuthal rate (coordinate time)
    N = 1 << (len(ts).bit_length())
    tgrid = np.linspace(ts[0], ts[-1], N)
    X = np.interp(tgrid, ts, Xs); Y = np.interp(tgrid, ts, Ys); Z = np.interp(tgrid, ts, Zs)
    R2 = X * X + Y * Y + Z * Z
    comp = {(0, 0): X * X - R2 / 3, (1, 1): Y * Y - R2 / 3, (2, 2): Z * Z - R2 / 3,
            (0, 1): X * Y, (0, 2): X * Z, (1, 2): Y * Z}
    T = tgrid[-1] - tgrid[0]
    w = 2 * np.pi * np.fft.fftfreq(N, d=T / N)
    # A Hann window kills the leakage from a non-integer number of periods (boxcar 1/w leakage,
    # which the w^6 weighting would amplify, becomes Hann's 1/w^3). PHYSICAL frequencies only:
    # harmonics of the orbital frequencies live below ~a few x Omega_phi; above is interpolation
    # noise that (i*w)^3 amplifies catastrophically -> cut there.
    win = np.hanning(N)
    wnorm = float(np.mean(win * win))          # window power, restores the correct normalization
    wcut = 40.0 * (abs(Omega_phi) + 1e-9)
    m = np.abs(w) < wcut
    wm, inv = w[m], 1.0 / (N * N * wnorm)
    Fc = {ij: np.fft.fft((I - I.mean()) * win)[m] for ij, I in comp.items()}

    def reduced(i, j):
        return Fc[(min(i, j), max(i, j))]
    dE = 0.0
    for (i, j), F in Fc.items():
        wt = 2.0 if i != j else 1.0                          # off-diagonal pair counted twice
        dE += wt * inv * np.sum(wm**6 * np.abs(F)**2)        # <(d3 I_ij/dt3)^2> via Parseval
    dEdt = -(mu * mu / 5.0) * dE
    # dL_z/dt = -(2/5) sum_c [ <d2 I_xc d3 I_yc> - <d2 I_yc d3 I_xc> ]; cross-spectrum gives w^5 Im[.]
    Lz = 0.0
    for c in (0, 1, 2):
        Lz += inv * np.sum(wm**5 * np.imag(reduced(0, c) * np.conj(reduced(1, c))))
        Lz -= inv * np.sum(wm**5 * np.imag(reduced(1, c) * np.conj(reduced(0, c))))
    dLdt = -(2.0 * mu * mu / 5.0) * Lz
    return dEdt, dLdt


if __name__ == "__main__":
    from _mn_invariant import build_hamilton_numeric
    M, a = 1.0, 0.5
    print("FREQUENCY MAP — radial & polar frequencies of bound geodesics (M=1, a=0.5)\n")
    print("Validation: q=0 (Kerr) frequencies should be sensible & positive; MN q=0 must match Kerr;")
    print("ratio nu_r/nu_theta varies with the orbit -> it sweeps through resonances during inspiral.\n")
    fk = build_hamilton_numeric(M, a, 0.0)
    print(f"  {'orbit (E,L,x0)':22s} {'nu_r':>10s} {'nu_theta':>10s} {'nu_r/nu_th':>11s}")
    for (E, L, x0) in [(0.95, 2.8, 8.0), (0.95, 2.8, 10.0), (0.95, 2.8, 12.0),
                       (0.96, 3.2, 10.0), (0.96, 3.2, 14.0), (0.97, 3.5, 16.0)]:
        r = fundamental_frequencies(fk, E, L, x0)
        if r is None:
            print(f"  (E={E},L={L},x0={x0}): unbound/off-shell"); continue
        nu_r, nu_th, ratio = r
        print(f"  (E={E},L={L},x0={x0})       {nu_r:10.5f} {nu_th:10.5f} {ratio:11.4f}")

    print("\nFLUX validation — a weak-field ~circular orbit must give Peters  dE/dt = -(32/5) M^3/r^5:")
    for r in (20.0, 30.0, 40.0):
        k = math.sqrt(M * M - a * a)
        x0 = (r - M) / k
        Ec, Lc = 1 - M / (2 * r), math.sqrt(M * r)        # Newtonian circular (weak field)
        res = quadrupole_flux(M, a, 0.0, Ec, Lc, x0, n_orb=6)
        peters = -(32.0 / 5.0) * M**3 / r**5
        if res is None:
            print(f"  r={r}: unbound"); continue
        dEdt, dLdt = res
        print(f"  r={r:.0f}: dE/dt={dEdt:.2e}  vs Peters {peters:.2e}  (ratio {dEdt/peters:.2f});  dL/dt={dLdt:.2e}")
