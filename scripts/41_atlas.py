#!/usr/bin/env python3
"""Step 41 — the ATLAS: one tool, a whole catalog of known spacetimes.

Attack angle #3. Turn the general analyzer (analyzer.py) loose on a catalog of
famous exact solutions and print one uniform comparison — a "report card for
every spacetime". This both shows the tool off and stress-tests it on inputs we
didn't design (which is how the depth gaps surface — see the frontier note).

Each row is produced by a single analyze() call; the columns are its report.

Run:  .venv/bin/python scripts/41_atlas.py
"""

import os
import sys

import sympy as sp

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from gr_engine import R_SYM
from analyzer import analyze, UNKNOWN

r = R_SYM
t, x, y, z = sp.symbols("t x y z", real=True)
th, ch, ph = sp.symbols("theta chi phi", real=True)
M, Q, L, Lam, mu, r0, H = sp.symbols("M Q L Lambda mu r0 H", positive=True)


def diag4(f):
    return sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(th)**2), [t, r, th, ph]


def catalog():
    cases = []
    cases.append(("Minkowski (flat)", sp.diag(-1, 1, 1, 1), [t, x, y, z]))
    cases.append(("Schwarzschild", *diag4(1 - 2 * M / r)))
    cases.append(("Reissner–Nordström", *diag4(1 - 2 * M / r + Q**2 / r**2)))
    cases.append(("Schwarzschild–de Sitter", *diag4(1 - 2 * M / r - Lam * r**2 / 3)))
    cases.append(("anti–de Sitter", *diag4(1 + r**2 / L**2)))
    aD = sp.exp(H * t)
    cases.append(("de Sitter (expanding)", sp.diag(-1, aD**2, aD**2, aD**2), [t, x, y, z]))
    cases.append(("Tangherlini 5D",
                  sp.diag(-(1 - mu / r**2), 1 / (1 - mu / r**2), r**2,
                          r**2 * sp.sin(th)**2, r**2 * sp.sin(th)**2 * sp.sin(ch)**2),
                  [t, r, th, ch, ph]))
    cases.append(("FLRW radiation", sp.diag(-1, t, t, t), [t, x, y, z]))           # a=t^½
    a23 = t**sp.Rational(2, 3)
    cases.append(("FLRW dust", sp.diag(-1, a23**2, a23**2, a23**2), [t, x, y, z]))
    cases.append(("Morris–Thorne wormhole",
                  sp.diag(-1, 1 / (1 - r0**2 / r**2), r**2, r**2 * sp.sin(th)**2), [t, r, th, ph]))
    # Kerr (rotating) — the OFF-DIAGONAL milestone, in rational u=cosθ form so the
    # analyzer (and the D4 rule) handle it; the trig form swamps. ~6s.
    a = sp.Symbol("a", positive=True)
    u = sp.Symbol("u", real=True)
    Sig = r**2 + a**2 * u**2
    Del = r**2 - 2 * M * r + a**2
    kerr = sp.zeros(4, 4)
    kerr[0, 0] = -(1 - 2 * M * r / Sig)
    kerr[0, 3] = kerr[3, 0] = -2 * M * r * a * (1 - u**2) / Sig
    kerr[1, 1] = Sig / Del
    kerr[2, 2] = Sig / (1 - u**2)
    kerr[3, 3] = (r**2 + a**2 + 2 * M * r * a**2 * (1 - u**2) / Sig) * (1 - u**2)
    cases.append(("Kerr (rotating)", kerr, [t, r, u, ph]))
    # Gödel (rotating universe with closed timelike curves) — off-diagonal, homogeneous,
    # sourced. Total effective stress-energy is a stiff perfect fluid (p=ρ). ~0.1s.
    ex = sp.exp(x)
    godel = sp.Matrix([[-1, 0, 0, -ex], [0, 1, 0, 0], [0, 0, 1, 0], [-ex, 0, 0, -ex**2 / 2]])
    cases.append(("Gödel (rotating universe)", godel, [t, x, y, z]))
    return cases


def _made(m):
    if "vacuum" in m:
        return "vacuum"
    if "cosmological constant" in m:
        return "Λ (dark energy)"
    if "traceless" in m:
        return "EM / radiation"
    if "perfect fluid" in m:
        return "perfect fluid w=" + m.split("w = ")[1].rstrip(")")
    if "anisotropic" in m:
        return "anisotropic"
    return m[:18]


def _phys(p):
    return "physical" if p is True else ("EXOTIC" if p is False else "—")


def _sing(s):
    if s is UNKNOWN:
        return "?"
    if s == []:
        return "none"
    return ",".join(f"{v}={val}" for v, val in s)[:8]


def _hor(h):
    if h is UNKNOWN:
        return "?(complex)"
    if h == []:
        return "none"
    return f"{len(h)}× r_h"


def _solves(s):
    if "sourced" in s:
        return "sourced"
    return "vacuum+Λ" if "Λ" in s else "vacuum"


def main():
    print("THE ATLAS — one analyzer, a catalog of spacetimes\n")
    hdr = f"  {'spacetime':24s} {'made of':19s} {'physical':9s} {'sym':4s} {'singular':9s} {'horizon':10s} {'solves':9s}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    ok = True
    for label, metric, coords in catalog():
        try:
            R = analyze(metric, coords)
        except Exception as e:
            print(f"  {label:24s} ERROR {type(e).__name__}")
            ok = False
            continue
        print(f"  {label:24s} {_made(R['made_of']):19s} {_phys(R['physical']):9s} "
              f"{str(len(R['symmetries'])):4s} {_sing(R['singularities']):9s} "
              f"{_hor(R['horizon']):10s} {_solves(R['solves_einstein']):9s}")

    # a few load-bearing sanity checks (the table is the real product)
    checks = []
    for label, metric, coords in catalog():
        R = analyze(metric, coords)
        if label == "Schwarzschild":
            checks.append("vacuum" in R["made_of"] and R["horizon"] not in (None, []))
        if label == "Morris–Thorne wormhole":
            checks.append(R["physical"] is False)
        if label == "FLRW radiation":
            checks.append("perfect fluid" in R["made_of"] and R["physical"] is True)
        if label == "de Sitter (expanding)":
            checks.append(R["energy_conditions"]["SEC"] is False)
        if label == "Kerr (rotating)":
            checks.append("vacuum" in R["made_of"] and len(R["horizon"]) == 2)
        if label == "Gödel (rotating universe)":
            checks.append("perfect fluid" in R["made_of"] and R["physical"] is True)
    ok = ok and all(checks)

    print("\n  off-diagonal: Kerr (vacuum, 2 horizons M±√(M²−a²)) and Gödel (stiff")
    print("  perfect fluid p=ρ, physical) both land — the key was rational coordinates")
    print("  (u=cosθ for Kerr) and homogeneity (Gödel). Documented limits: the warp")
    print("  drive (√ + arbitrary shape fn — but it's proven exotic in battery 38),")
    print("  rotating-horizon T,S (numerically exact, symbolically irreducible), and the")
    print("  ring singularity (off-diagonal Kretschmann swamps). See ATTACK_ANGLES §2/§6.")
    print(f"\nATLAS: {'PASSED ✅' if ok else 'FAILED ❌'}  (one analyze() per row; "
          "12 famous spacetimes incl. rotating Kerr & Gödel, uniform report)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
