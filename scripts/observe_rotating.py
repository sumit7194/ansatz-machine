"""Numerical equatorial observables for ANY stationary, axisymmetric black hole — the
general companion to §86's Kerr-specific closed forms. Given only the equatorial metric
functions g_tt(r), g_tφ(r), g_φφ(r), it finds what a telescope measures:

  • the PHOTON RING radius (circular null orbit) and the SHADOW impact parameter b=L/E
    at it (the EHT silhouette edge), prograde and retrograde;
  • the ISCO (innermost stable circular orbit, the accretion-disk inner edge from X-ray),
    where dE/dr = 0 along the circular-orbit sequence;
  • (if g_rr is given) the EIKONAL RINGDOWN — the LIGO ringdown frequency from the photon
    ring (Cardoso et al.): ω = ℓ·Ω_c − i(n+½)|λ|, Ω_c the photon angular velocity, λ the
    orbit's Lyapunov instability rate. The corotating ℓ=m=2 mode uses the prograde ring.
    Eikonal ≈ exact to ~5–10% at ℓ=2 (the precise spectrum is §77's Leaver solver).

All from the metric + finite-difference derivatives — so it works for modified-gravity or
DISCOVERED rotating black holes, not just Kerr. Validated against Kerr's closed forms (§86)
to ~0.5% and the precise QNM (§77) to eikonal accuracy. Pure Python, no deps.

  equatorial_observables(gtt, gtp, gpp[, grr]) -> {photon_r, shadow_b, isco, ringdown} × {pro, retro}
"""

import math


def _d(fn, r, h=1e-6):
    return (fn(r + h) - fn(r - h)) / (2 * h)


def _omega(gtt, gtp, gpp, r, prograde):
    """Circular-orbit angular velocity Ω=dφ/dt (± branch = pro/retrograde)."""
    a_, b_, c_ = _d(gpp, r), _d(gtp, r), _d(gtt, r)
    disc = b_ * b_ - a_ * c_
    if disc < 0:
        return None
    return (-b_ + (1 if prograde else -1) * math.sqrt(disc)) / a_


def _null_norm(gtt, gtp, gpp, r, prograde):
    om = _omega(gtt, gtp, gpp, r, prograde)
    return None if om is None else gtt(r) + 2 * om * gtp(r) + om * om * gpp(r)


def _bisect_zero(fn, lo, hi, n=20000):
    flo = fn(lo)
    for k in range(1, n + 1):
        r = lo + (hi - lo) * k / n
        f = fn(r)
        if f is None or flo is None:
            flo = f
            continue
        if flo * f < 0:
            a, b = r - (hi - lo) / n, r
            for _ in range(60):
                m = (a + b) / 2
                fm = fn(m)
                if flo * fm < 0:
                    b = m
                else:
                    a, flo = m, fm
            return (a + b) / 2
        flo = f
    return None


def _energy(gtt, gtp, gpp, r, prograde):
    om = _omega(gtt, gtp, gpp, r, prograde)
    if om is None:
        return None
    den = -(gtt(r) + 2 * om * gtp(r) + om * om * gpp(r))
    return None if den <= 0 else -(gtt(r) + om * gtp(r)) / math.sqrt(den)


def _d2(fn, r, h=1e-4):
    return (fn(r + h) - 2 * fn(r) + fn(r - h)) / (h * h)


def _eikonal_ringdown(gtt, gtp, gpp, grr, rph, b, ell=2, n=0):
    """ω = ℓΩ_c − i(n+½)|λ| from the photon ring (Cardoso correspondence)."""
    om = abs(_omega(gtt, gtp, gpp, rph, True))                       # photon angular velocity
    def Dlow(r):
        return gtt(r) * gpp(r) - gtp(r)**2
    def R(r):                                                        # null radial potential ṙ²=R, E=1,L=b
        return -(gpp(r) + 2 * gtp(r) * b + gtt(r) * b * b) / (grr(r) * Dlow(r))
    tdot = -(gpp(rph) + gtp(rph) * b) / Dlow(rph)
    lam = math.sqrt(abs(_d2(R, rph)) / (2 * tdot * tdot))
    return {"omega_R": ell * om, "omega_I": (n + 0.5) * lam, "Omega_c": om, "lyapunov": lam}


def equatorial_observables(gtt, gtp, gpp, grr=None, rmin=1.02, rmax=15.0):
    """Photon ring, shadow impact parameter, ISCO (prograde & retrograde) for a
    stationary-axisymmetric metric given its equatorial functions; plus the eikonal
    RINGDOWN if g_rr is supplied. Numerical; ~0.5% vs Kerr closed forms (eikonal ringdown
    ~5–10%). Returns {} branches as None where an orbit doesn't exist."""
    out = {}
    for tag, pro in (("prograde", True), ("retrograde", False)):
        rph = _bisect_zero(lambda r: _null_norm(gtt, gtp, gpp, r, pro), rmin, rmax)
        b = None
        if rph is not None:
            om = _omega(gtt, gtp, gpp, rph, pro)
            E = -(gtt(rph) + om * gtp(rph))
            L = gtp(rph) + om * gpp(rph)
            b = L / E if E != 0 else None
        isco = _bisect_zero(
            lambda r: (_d(lambda rr: (_energy(gtt, gtp, gpp, rr, pro) or 0.0), r)),
            (rph + 0.02) if rph else rmin, rmax)
        rec = {"photon_r": rph, "shadow_b": b, "isco": isco}
        if grr is not None and rph is not None and b is not None and pro:   # ℓ=m=2 corotating ⇒ prograde
            rec["ringdown"] = _eikonal_ringdown(gtt, gtp, gpp, grr, rph, b)
        out[tag] = rec
    return out
