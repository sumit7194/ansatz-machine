#!/usr/bin/env python3
"""Step 54 — MASS–RADIUS & the MAXIMUM NEUTRON-STAR MASS (Oppenheimer–Volkoff).

The capstone of the stellar arc: take the engine's recovered TOV equation (§52),
give it an equation of state, and integrate it numerically to predict the one thing
telescopes actually measure for a neutron star — its mass–radius relation. The
headline that falls out is the reason stellar-mass black holes exist:

    there is a MAXIMUM MASS. Build a star heavier than it and no pressure — however
    stiff the matter — can hold it up; it collapses to a black hole.

Method (pure Python, hand-rolled RK4 — no numpy/scipy, matching the project ethos):
integrate  dm/dr = 4πr²ρ,  dp/dr = −(ρ+p)(m+4πr³p)/(r(r−2m))  (the TOV pair from §52)
outward from the centre with a chosen central pressure, with a polytropic EoS
p = Kρ^Γ (Γ=2, K=100 in geometric units), until the pressure hits zero — that radius
is the surface R, the enclosed mass is M. Scan the central pressure to trace M(R).

Experiments:
  (A) each integration yields a valid star (pressure falls monotonically to 0 at a
      finite surface, finite M, and compactness M/R below the Buchdahl bound 4/9 §53);
  (B) the MASS–RADIUS curve TURNS OVER — M rises with central density, reaches a
      maximum, then DECREASES: the Oppenheimer–Volkoff MAXIMUM MASS;
  (C) past that peak, denser stars are LIGHTER ⇒ unstable ⇒ collapse to a black hole —
      so the engine's own equations forbid arbitrarily heavy neutron stars.

Honest scope: textbook TOV numerics with a toy polytrope; the numbers are in arbitrary
geometric units (the turnover, not the value, is the physics). New is the end-to-end
chain — the same engine recovers TOV, builds an exact star (§53), and here predicts a
maximum mass, the bridge from stellar structure to why black holes form.

Run:  .venv/bin/python scripts/54_mass_radius.py
"""

import math

PI = math.pi
K = 100.0      # polytropic constant (geometric units)
GAMMA = 2.0    # polytropic index (stiff, neutron-star toy)


def rho_of(p):
    """Energy density from pressure for the polytrope p = K ρ^Γ."""
    return (p / K) ** (1.0 / GAMMA) if p > 0 else 0.0


def _derivs(r, m, p):
    """The TOV pair (dm/dr, dp/dr); None if the metric factor r−2m fails."""
    rho = rho_of(p)
    denom = r * (r - 2 * m)
    if denom <= 0:
        return None
    dm = 4 * PI * r * r * rho
    dp = -(rho + p) * (m + 4 * PI * r**3 * p) / denom
    return dm, dp


def integrate_star(pc, dr=0.005, rmax=80.0):
    """RK4-integrate TOV from the centre at central pressure pc → (R, M)."""
    r = 1e-6
    m = 4.0 / 3.0 * PI * rho_of(pc) * r**3
    p = pc
    while r < rmax and p > 1e-12 * pc:
        k1 = _derivs(r, m, p)
        if k1 is None:
            break
        k2 = _derivs(r + dr / 2, m + dr / 2 * k1[0], p + dr / 2 * k1[1])
        if k2 is None:
            break
        k3 = _derivs(r + dr / 2, m + dr / 2 * k2[0], p + dr / 2 * k2[1])
        if k3 is None:
            break
        k4 = _derivs(r + dr, m + dr * k3[0], p + dr * k3[1])
        if k4 is None:
            break
        m += dr / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        p += dr / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        r += dr
    return r, m


def main():
    print("MASS–RADIUS & the MAXIMUM NEUTRON-STAR MASS (TOV, Γ=2 polytrope)\n")

    # log-spaced central-pressure scan spanning the turnover
    n = 25
    lo, hi = math.log10(3e-5), math.log10(2.0)
    pcs = [10 ** (lo + (hi - lo) * i / (n - 1)) for i in range(n)]
    curve = [(pc, *integrate_star(pc)) for pc in pcs]   # (pc, R, M)

    # (A) valid stars: finite R, M, compactness below Buchdahl 4/9
    compactness = [M / R for (_, R, M) in curve]
    okA = all(0 < R < 80 and M > 0 for (_, R, M) in curve) and max(compactness) < 4 / 9
    print(f"  (A) all {n} integrations give valid stars; max compactness "
          f"M/R = {max(compactness):.3f} < 4/9 (Buchdahl §53)   {'✅' if okA else '❌'}")

    # (B) the turnover: M rises, peaks, falls → a MAXIMUM MASS
    masses = [M for (_, _, M) in curve]
    imax = max(range(n), key=lambda i: masses[i])
    M_max, R_at_max, pc_at_max = masses[imax], curve[imax][1], curve[imax][0]
    rises = any(masses[i] < masses[imax] for i in range(imax))         # grew up to peak
    falls = any(masses[i] < masses[imax] for i in range(imax + 1, n))  # shrank after
    interior = 0 < imax < n - 1
    okB = rises and falls and interior
    print(f"\n  (B) mass–radius curve (M vs central pressure):")
    for i, (pc, R, M) in enumerate(curve):
        if i % 2 == 0 or i == imax:
            mark = "  ◀ MAXIMUM MASS" if i == imax else ""
            print(f"        pc={pc:8.2e}  R={R:6.3f}  M={M:6.4f}{mark}")
    print(f"      ⇒ MAXIMUM MASS M_max = {M_max:.4f} at R = {R_at_max:.3f} "
          f"(pc={pc_at_max:.2e})   {'✅ turnover found' if okB else '❌'}")

    # (C) beyond the peak: denser ⇒ lighter ⇒ unstable ⇒ must collapse
    beyond = masses[imax + 1:]
    okC = len(beyond) > 0 and beyond[-1] < M_max and all(
        beyond[j] <= beyond[j - 1] + 1e-6 for j in range(1, len(beyond)))
    print(f"\n  (C) past the peak, higher central density gives LOWER mass "
          f"({M_max:.3f} → {masses[-1]:.3f})")
    print(f"      ⇒ those stars are unstable and collapse to black holes   "
          f"{'✅' if okC else '❌'}")
    print("      — the engine's own TOV forbids arbitrarily heavy neutron stars.")

    passed = okA and okB and okC
    print(f"\nMASS–RADIUS: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(end-to-end: TOV → star → a maximum mass, the seed of black holes)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
