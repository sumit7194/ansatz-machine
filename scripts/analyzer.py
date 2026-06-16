"""The general spacetime analyzer — `analyze(metric, coords)` → one report.

The widening (2026-06-16): instead of a bespoke script per domain, ONE entry
point that eats ANY metric — black hole, expanding universe, wormhole, warp
bubble, any coordinates, any dimension — and returns one honest report. This is
the CORE: it answers three questions, and leaves room to grow (symmetries,
singularities, horizons/thermodynamics come next).

    • what is it made of?     — read the stress-energy off the Einstein tensor,
                                 then classify (vacuum / Λ / perfect fluid /
                                 traceless / anisotropic);
    • is that matter physical? — the energy conditions, computed FRAME-
                                 INDEPENDENTLY from the principal components of
                                 T^a_b (the single upgrade that frees the check
                                 from the static-black-hole frame and makes it
                                 work on cosmology, wormholes, warp, …);
    • does it solve Einstein's equations? — vacuum / vacuum+Λ / sourced.

Design rules inherited from the engine: pure SymPy, reuse gr_engine.Geometry for
all curvature, and stay THREE-VALUED — every answer is True / False / UNKNOWN,
never a guess. It does NOT touch scripts 01–38; those stay frozen as the proven
base and the analyzer's regression suite (see 40_analyzer.py).
"""

import os
import random
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gr_engine import Geometry, zero_simplify

UNKNOWN = None  # three-valued, as everywhere in this project


# ---------------------------------------------------------------------------
# sign / nonneg helpers (three-valued)
# ---------------------------------------------------------------------------

def _sign(expr):
    """+1 / −1 / 0 / None — sign of expr over the physical domain (positive
    parameters & coordinates). Symbolic when SymPy can decide, else sampled;
    None (UNKNOWN) if a sample is not real-evaluable or the sign is mixed."""
    e = sp.simplify(expr)
    if e == 0:
        return 0
    if e.is_positive:
        return 1
    if e.is_negative:
        return -1
    rng = random.Random(0)
    free = sorted(e.free_symbols, key=str)
    seen = set()
    for _ in range(60):
        sub = {s: sp.Rational(rng.randint(1, 25), rng.randint(1, 6)) for s in free}
        try:
            v = float(e.subs(sub))
        except (TypeError, ValueError):
            return None
        if v > 1e-12:
            seen.add(1)
        elif v < -1e-12:
            seen.add(-1)
        else:
            seen.add(0)
    if seen == {1}:
        return 1
    if seen == {-1}:
        return -1
    if seen <= {0}:
        return 0
    return None        # mixed sign over the domain ⇒ cannot give one verdict


def _nonneg(expr):
    s = _sign(expr)
    return None if s is None else (s >= 0)


def _all(*vals):
    if any(v is False for v in vals):
        return False
    if any(v is None for v in vals):
        return None
    return True


def _is_zero_matrix(M):
    return all(zero_simplify(M[i, j]) == 0 for i in range(M.rows) for j in range(M.cols))


# ---------------------------------------------------------------------------
# the matter and its physicality
# ---------------------------------------------------------------------------

def stress_energy(geo):
    """Mixed stress-energy T^a_b = G^a_b / 8π that sources the metric."""
    G = geo.ricci - sp.Rational(1, 2) * geo.ricci_scalar * geo.g
    return sp.simplify(geo.ginv * G / (8 * sp.pi))


def principal_components(geo, Tmix):
    """Frame-independent (ρ, [pressures]) — the energy density and principal
    pressures, i.e. the eigenvalues of T^a_b (timelike eigenvalue = −ρ,
    spacelike = pressures). Returns (UNKNOWN, UNKNOWN) if not cleanly Type I.

    Diagonal metrics (the common case — FLRW, wormhole, RN, …) take the direct
    route with coordinate 0 as the time direction; off-diagonal metrics go
    through a genuine eigen-decomposition and are UNKNOWN if it isn't clean."""
    n = geo.n
    if Tmix.is_diagonal():
        rho = sp.simplify(-Tmix[0, 0])
        pressures = [sp.simplify(Tmix[i, i]) for i in range(1, n)]
        return rho, pressures
    try:
        eig = Tmix.eigenvects()
    except Exception:
        return UNKNOWN, UNKNOWN
    rho, pressures = None, []
    for val, _mult, vecs in eig:
        for v in vecs:
            v = sp.Matrix(v)
            norm = _sign(sp.simplify((v.T * geo.g * v)[0]))
            if norm is None:
                return UNKNOWN, UNKNOWN
            if norm < 0:                       # timelike eigenvector ⇒ density
                if rho is not None:
                    return UNKNOWN, UNKNOWN     # >1 timelike ⇒ not Type I
                rho = sp.simplify(-val)
            else:
                pressures.append(sp.simplify(val))
    if rho is None or len(pressures) != n - 1:
        return UNKNOWN, UNKNOWN
    return rho, pressures


def energy_conditions(rho, pressures):
    """NEC / WEC / DEC / SEC, three-valued, from (ρ, pressures)."""
    if rho is UNKNOWN:
        return {k: UNKNOWN for k in ("NEC", "WEC", "DEC", "SEC")}
    nec = _all(*[_nonneg(rho + p) for p in pressures])
    wec = _all(nec, _nonneg(rho))
    dec = _all(_nonneg(rho), *[_nonneg(rho - p) for p in pressures],
               *[_nonneg(rho + p) for p in pressures])
    sec = _all(nec, _nonneg(rho + sum(pressures)))
    return {"NEC": nec, "WEC": wec, "DEC": dec, "SEC": sec}


def matter_type(geo, Tmix):
    """A plain-language description of what sources the metric, plus its
    principal components (computed for everything except true vacuum, so the
    energy conditions can always be evaluated when there is matter)."""
    n = geo.n
    if _is_zero_matrix(Tmix):
        return "vacuum (empty space)", UNKNOWN, UNKNOWN
    rho, pressures = principal_components(geo, Tmix)
    if rho is UNKNOWN:
        return "matter (could not classify — UNKNOWN)", rho, pressures
    if _is_zero_matrix(Tmix - Tmix[0, 0] * sp.eye(n)):   # T^a_b ∝ δ ⇒ p = −ρ
        return "cosmological constant Λ (w = −1)", rho, pressures
    if all(zero_simplify(p - pressures[0]) == 0 for p in pressures):
        w = sp.simplify(pressures[0] / rho) if rho != 0 else UNKNOWN
        return f"perfect fluid (isotropic, w = {w})", rho, pressures
    if zero_simplify(sum([-rho] + pressures)) == 0:   # traceless: −ρ+Σp = 0
        return "traceless matter (radiation / electromagnetic-like)", rho, pressures
    return "anisotropic matter", rho, pressures


def field_verdict(geo):
    """vacuum (Ricci-flat) / vacuum + Λ / sourced — three-valued."""
    Ric = geo.ricci
    if _is_zero_matrix(Ric):
        return "vacuum (Ricci-flat)"
    n = geo.n
    Lam = sp.simplify(geo.ricci_scalar * (n - 2) / (2 * n))
    if not Lam.free_symbols or Lam.is_number:
        resid = Ric - (2 * Lam / (n - 2)) * geo.g
        if _is_zero_matrix(resid):
            return f"vacuum + cosmological constant (Λ = {Lam})"
    # constant-but-symbolic Λ (e.g. a Λ symbol): test the residual directly
    resid = Ric - (2 * Lam / (n - 2)) * geo.g
    if _is_zero_matrix(resid):
        return f"vacuum + cosmological constant (Λ = {Lam})"
    return "sourced (non-vacuum matter)"


# ---------------------------------------------------------------------------
# the report
# ---------------------------------------------------------------------------

def analyze(metric, coords):
    """Run the core analysis on any metric. Returns a report dict."""
    geo = Geometry(sp.Matrix(metric), list(coords))
    Tmix = stress_energy(geo)
    desc, rho, pressures = matter_type(geo, Tmix)
    ec = energy_conditions(rho, pressures)
    physical = _all(*[ec[k] for k in ("NEC", "WEC", "DEC", "SEC")])
    return {
        "dim": geo.n,
        "ricci_scalar": geo.ricci_scalar,
        "made_of": desc,
        "rho": rho,
        "pressures": pressures,
        "energy_conditions": ec,
        "physical": physical,           # all four hold? True/False/UNKNOWN
        "solves_einstein": field_verdict(geo),
    }


def _mark(v):
    return "hold" if v is True else ("VIOLATED" if v is False else "UNKNOWN")


def format_report(report):
    ec = report["energy_conditions"]
    phys = ("physical (all conditions hold)" if report["physical"] is True else
            "EXOTIC (an energy condition is violated)" if report["physical"] is False
            else "UNKNOWN")
    lines = [
        f"  made of    : {report['made_of']}",
        f"  density ρ  : {report['rho']}",
        f"  pressures  : {report['pressures']}",
        f"  physical?  : {phys}   [" + ", ".join(f"{k}:{_mark(ec[k])}" for k in
                                                 ('NEC', 'WEC', 'DEC', 'SEC')) + "]",
        f"  solves EFE : {report['solves_einstein']}",
        f"  dimension  : {report['dim']}",
    ]
    return "\n".join(lines)
