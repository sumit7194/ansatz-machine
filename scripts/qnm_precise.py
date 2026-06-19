"""Precise Kerr quasinormal-mode oracle — the numerical companion to §56.

§56 gives the EXACT but EIKONAL (light-ring) QNM, and explicitly defers the precise
overtone spectrum to "Leaver / the qnm package." This module is that precise oracle:
it wraps Leaver's continued-fraction method (via the `qnm` package, Stein 2019) into a
first-class call

    qnm_precise(M, a, l, m, n, s=-2)  ->  complex frequency ω (physical units)

so the bridge's ringdown link becomes a 0.1%-level exact↔measured test, and the
overtones (e.g. the 221 = ℓ=m=2,n=1 that deepstrain's δ measures) are available — which
the eikonal cannot give.

DEPENDENCY NOTE (see DECISIONS.md): a precise QNM is inherently NUMERICAL — Leaver's
continued fraction has no closed form — so this track needs `qnm` (which pulls
numpy/scipy/numba). It is kept SEPARATE from the pure-SymPy core: nothing in the 76
core batteries imports it, and the analyzer stays pure. `a` is the dimensionless spin
a/M ∈ [0,1); frequencies are returned with mass M factored back in (ω = Mω / M).
"""

try:
    import qnm as _qnm
    _AVAILABLE = True
except Exception:                       # optional dependency — the core never needs it
    _AVAILABLE = False

_cache = {}


def available():
    return _AVAILABLE


def qnm_precise(M, a, l, m, n, s=-2):
    """Complex QNM frequency ω = ω_R − i/τ (physical units). M = mass, a = dimensionless
    spin a/M ∈ [0,1), (l,m,n) the mode, s the spin weight (−2 gravitational, −1 EM, 0
    scalar). Mω (dimensionless) comes from Leaver; ω = Mω / M."""
    if not _AVAILABLE:
        raise RuntimeError("the `qnm` package is not installed (pip install qnm)")
    key = (s, l, m, n)
    if key not in _cache:
        _cache[key] = _qnm.modes_cache(s=s, l=l, m=m, n=n)
    Momega, _A, _C = _cache[key](a=a)
    return complex(Momega) / M


def damping_time(M, a, l, m, n, s=-2):
    """τ = −1/Im(ω): the ringdown e-folding time of the mode."""
    return -1.0 / qnm_precise(M, a, l, m, n, s).imag


def quality_factor(M, a, l, m, n, s=-2):
    """Q = |ω_R| / (2|ω_I|): cycles before damping."""
    w = qnm_precise(M, a, l, m, n, s)
    return abs(w.real) / (2 * abs(w.imag))
