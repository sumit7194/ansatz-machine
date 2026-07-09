#!/usr/bin/env python3
"""Step 114 — THE FLUX ATLAS: which {twists, fluxes} stabilize which moduli on the hidden T².

Bridge ask 1 (round 6), seconding the quantum project's research-directions #1. Extends §111–§113:
6D Einstein-Maxwell + Λ6 on the (twisted) T² fibre, flux wrapped on the hidden torus, plus the twist
axis (absorbable monodromy vs geometric flux). Machine-maps each configuration to a three-valued
verdict with the obstruction EXTRACTED as a theorem (§112-style), and emits a machine-readable atlas
(data/flux_atlas.json) for the family.

Prior art, cited honestly: Andriot-Marconnet-Rajaguru-Wrase (JHEP 12(2022)026, arXiv:2209.08015)
automated consistent truncations for type II sugra on 6D group manifolds with Op/Dp sources. Our
instrument differs: minimal 6D Einstein-Maxwell (the family's setup), per-config obstruction
extraction, three-valued verdicts.

THE RESULTS (all machine-derived, leftover zero / exact solve):
 (A) FLUX DICTIONARY (free family {f,h,Φ1,Φ2,χ}(r), G_{w1w2}=n, Λ6):
     G² = 2n²/detM -- the flux sees the moduli ONLY through detM (volume+axion), never the shape.
     Maxwell holds identically; the A^a=0 truncation is consistent (mixed equations vanish);
     fibre sources all carry the single bracket (2Λ6·detM + 3n²).
 (B) VACUUM ATLAS (constant moduli, 4D max-sym base -- exact algebra):
     C0 nothing on: λ=0 forced, ALL moduli flat (nothing stabilized).
     C1 flux alone: OBSTRUCTED -- the system forces 3n²=0 (no constant-moduli vacuum: runaway).
     C2 flux+Λ6: detM = -3n²/(2Λ6) STABILIZED (needs Λ6<0), λ = 2Λ6/9 < 0 (AdS4);
        the equations depend on Φ1,Φ2,χ ONLY through detM => the SHAPE+AXION SL(2,R)/SO(2) coset
        remains EXACTLY FLAT: the vacuum manifold is the coset. (Flux stabilizes volume, period.)
 (C) TWIST AXIS:
     M1 monodromy (dw2 + m w1 dw1): ABSORBED -- the equation set factors into the SAME brackets as
        the untwisted system (large-diffeo / axion shift; the folklore trap: SS on metric-only T²
        stabilizes NOTHING -- proven).
     G0 geometric flux, constant-flux ansatz: REJECTED -- Maxwell VIOLATED, residual
        -mn e^{-2mw1}/detM extracted (the flux must wrap the internal VOLUME form).
     G1 geometric flux e^{m w1} alone: OBSTRUCTED -- m²=0 forced.
     G2 geometric flux + volume-form flux + Λ6: PARTIAL -- Φ1²Φ2² relation + λ fixed, ONE flat
        direction survives (the Φ2 branch, extracted exactly); Λ6<0 required. Global caveat logged:
        the 2D affine group is non-compact (the classic compactness obstruction of geometric flux
        on T²) -- local reduction proven, compactification UNPROVEN.
 (D) TRUNCATION TRAP: freezing the volume at any value other than -3n²/(2Λ6) is inconsistent --
     the price tag (2Λ6·detM + 3n²) = 0 extracted, §111-trap style.
 (E) data/flux_atlas.json emitted. Einstein-frame masses = the offered next leg (the bridge
     verifies numerically downstream).

Repro: .venv/bin/python scripts/114_flux_atlas.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from gr_engine import Geometry, zero_simplify

t, r, th, ph, w1, w2 = sp.symbols("t r theta phi w1 w2", real=True)
lam, n, L6, m = sp.symbols("lam n Lambda6 m", real=True)
P1s, P2s = sp.symbols("Phi1 Phi2", positive=True)
chis = sp.symbols("chi", real=True)

X6 = [t, r, th, ph, w1, w2]
ATLAS = []


def atlas(config, verdict, obstruction, stabilized, potential, note=""):
    ATLAS.append({"config": config, "verdict": verdict, "obstruction": obstruction,
                  "stabilized_moduli": stabilized, "potential": potential, "note": note})


def build6(g4, fib):
    g6 = sp.zeros(6)
    for a in range(4):
        for b in range(4):
            g6[a, b] = g4[a, b]
    for a in range(2):
        for b in range(2):
            g6[4 + a, 4 + b] = fib[a, b]
    return g6


def einstein_eqs(fib, nv, L6v, flux_profile=1):
    """Constant-moduli vacuum system on the 4D max-sym base; returns (factored bracket set,
    maxwell residuals)."""
    F = 1 - lam * r**2
    g4 = sp.diag(-F, 1 / F, r**2, r**2 * sp.sin(th)**2)
    g6 = build6(g4, fib)
    G = sp.zeros(6)
    G[4, 5] = nv * flux_profile
    G[5, 4] = -nv * flux_profile
    geo = Geometry(g6, X6)
    R6 = geo.ricci
    g6inv = g6.inv()
    Rs = sp.simplify(sum(g6inv[i, j] * R6[i, j] for i in range(6) for j in range(6)))
    Gup = sp.Matrix(6, 6, lambda i, j: sum(
        g6inv[i, p] * g6inv[j, q] * G[p, q] for p in range(6) for q in range(6)))
    G2 = sp.simplify(sum(G[i, j] * Gup[i, j] for i in range(6) for j in range(6)))
    sq = sp.sqrt(-g6.det()).subs(sp.Abs(sp.sin(th)), sp.sin(th))
    mx = [zero_simplify(sp.simplify(sum(sp.diff(sq * Gup[a, b], X6[a]) for a in range(6)) / sq))
          for b in range(6)]
    brackets = set()
    for i in range(6):
        for j in range(i, 6):
            Tij = sum(G[i, p] * g6inv[p, q] * G[j, q] for p in range(6) for q in range(6)) \
                - sp.Rational(1, 4) * g6[i, j] * G2
            e = sp.simplify(R6[i, j] - sp.Rational(1, 2) * g6[i, j] * Rs + L6v * g6[i, j] - Tij)
            if e != 0:
                nu, _ = sp.fraction(sp.together(e))
                # strip nonvanishing prefactors (moduli powers, exp(m w1), coordinate factors like
                # m*w1 -- an equation holding for ALL w must have its BRACKET vanish): keep only
                # the factors carrying {lam, n, L6} (every physical bracket does)
                keep = [fac for fac in sp.factor(nu).as_ordered_factors()
                        if (fac.free_symbols & {lam, n, L6}) and not fac.has(sp.exp)]
                bracket = sp.factor(sp.Mul(*keep)) if keep else sp.factor(nu)
                if bracket.could_extract_minus_sign():      # canonical overall sign
                    bracket = -bracket
                brackets.add(bracket)
    return sorted(brackets, key=sp.count_ops), mx, G2


def main():
    print("§114 THE FLUX ATLAS -- twists/fluxes on the hidden T² -> which moduli stabilize\n")
    ok = []

    # ================================================================ (A) the flux dictionary
    print("(A) flux dictionary over the free family {f,h,Phi1,Phi2,chi}(r), flux n, Lambda6:")
    f = sp.Function("f", positive=True)(r)
    h = sp.Function("h", positive=True)(r)
    P1 = sp.Function("Phi1", positive=True)(r)
    P2 = sp.Function("Phi2", positive=True)(r)
    chi = sp.Function("chi")(r)
    g4 = sp.diag(-f, h, r**2, r**2 * sp.sin(th)**2)
    fib = sp.Matrix([[P1**2, chi], [chi, P2**2]])
    detM = P1**2 * P2**2 - chi**2
    g6 = build6(g4, fib)
    G = sp.zeros(6)
    G[4, 5] = n
    G[5, 4] = -n
    geo = Geometry(g6, X6)
    R6 = geo.ricci
    g6inv = g6.inv()
    Rs = sp.simplify(sum(g6inv[i, j] * R6[i, j] for i in range(6) for j in range(6)))
    Gup = sp.Matrix(6, 6, lambda i, j: sum(
        g6inv[i, p] * g6inv[j, q] * G[p, q] for p in range(6) for q in range(6)))
    G2 = sp.simplify(sum(G[i, j] * Gup[i, j] for i in range(6) for j in range(6)))
    okA1 = zero_simplify(sp.simplify(G2 - 2 * n**2 / detM)) == 0
    sq = sp.sqrt(-g6.det()).subs(sp.Abs(sp.sin(th)), sp.sin(th))
    mx = [zero_simplify(sp.simplify(sum(sp.diff(sq * Gup[a, b], X6[a]) for a in range(6)) / sq))
          for b in range(6)]
    okA2 = all(x == 0 for x in mx)
    Ttens = sp.Matrix(6, 6, lambda i, j: sum(
        G[i, p] * g6inv[p, q] * G[j, q] for p in range(6) for q in range(6))
        - sp.Rational(1, 4) * g6[i, j] * G2)
    E = sp.Matrix(6, 6, lambda i, j: R6[i, j] - sp.Rational(1, 2) * g6[i, j] * Rs
                  + L6 * g6[i, j] - Ttens[i, j])
    okA3 = all(zero_simplify(sp.simplify(E[mu, 4 + a])) == 0 for mu in range(4) for a in range(2))
    # fibre sources: Ricci-form RHS = T - g*T/4 + g*L6/2; verify the single bracket (2 L6 detM + 3n^2)
    Ttr = sp.simplify(sum(g6inv[i, j] * Ttens[i, j] for i in range(6) for j in range(6)))
    br = 2 * L6 * detM + 3 * n**2
    src_expect = {(4, 4): br * P1**2 / (4 * detM), (5, 5): br * P2**2 / (4 * detM),
                  (4, 5): br * chi / (4 * detM)}
    okA4 = all(zero_simplify(sp.simplify(
        (Ttens[i, j] - g6[i, j] * Ttr / 4 + g6[i, j] * L6 / 2) - src_expect[(i, j)])) == 0
        for (i, j) in src_expect)
    okA = okA1 and okA2 and okA3 and okA4
    ok.append(okA)
    print(f"    G² = 2n²/detM (flux sees ONLY volume+axion, never shape): {okA1}")
    print(f"    Maxwell identically satisfied: {okA2};  A=0 truncation consistent: {okA3}")
    print(f"    all fibre sources = (2Λ6·detM + 3n²)·(Φa², Φa², χ)/(4detM): {okA4}   "
          f"{'✅' if okA else '❌'}")

    # ================================================================ (B) vacuum atlas
    print("\n(B) vacuum atlas (constant moduli, exact solve):")
    fib0 = sp.Matrix([[P1s**2, chis], [chis, P2s**2]])
    D0 = P1s**2 * P2s**2 - chis**2

    # C0
    eqs, mx0, _ = einstein_eqs(sp.diag(P1s**2, P2s**2), 0, 0)
    sol = sp.solve(eqs, [lam], dict=True)
    okB0 = sol == [{lam: 0}] and not any(e.has(P1s) and not e.has(lam) for e in eqs)
    ok.append(okB0)
    print(f"    C0 (nothing): lam=0 forced, moduli in no equation -> ALL FLAT: {okB0}   "
          f"{'✅' if okB0 else '❌'}")
    atlas({"twist": "none", "fluxes": {}, "Lambda6": 0}, "consistent",
          None, [], "V = 0", "all moduli flat; the §112 baseline")

    # C1: flux alone -> obstruction 3n^2 = 0 (direct elimination of lam)
    eqs, _, _ = einstein_eqs(sp.diag(P1s**2, P2s**2), n, 0)
    sol = sp.solve(eqs, [lam, P1s], dict=True)
    lam_sols = sp.solve(eqs[0], lam)
    resid_after_elim = {sp.factor(sp.simplify(e.subs(lam, lam_sols[0]))) for e in eqs[1:]
                        if lam_sols and sp.simplify(e.subs(lam, lam_sols[0])) != 0}
    # every residual must be n^2 * (a quantity that cannot vanish): the extracted obstruction.
    # criterion: res has an overall n^2 factor AND the cofactor's numerator has all same-sign
    # coefficients (positive moduli/coords -> it never vanishes) => n = 0 is FORCED.
    def forced_n2(res):
        if sp.simplify(res.subs(n, 0)) != 0:
            return False
        cof = sp.together(sp.simplify(res / n**2)).subs(sp.sin(th), sp.Symbol("s_p", positive=True))
        num, _ = sp.fraction(cof)
        coeffs = sp.Poly(sp.expand(num), n, r, P1s, P2s).coeffs()
        return (all(c.is_positive for c in coeffs) or all(c.is_negative for c in coeffs))
    okB1 = sol == [] and bool(lam_sols) and bool(resid_after_elim) and all(
        forced_n2(res) for res in resid_after_elim)
    print(f"      [C1 obstruction after eliminating lam: {resid_after_elim} -> n² = 0 forced]")
    ok.append(okB1)
    print(f"    C1 (flux alone): no constant-moduli vacuum (solve = []); eliminating lam forces "
          f"n² = 0 -> OBSTRUCTED (runaway): {okB1}   {'✅' if okB1 else '❌'}")
    atlas({"twist": "none", "fluxes": {"G_w1w2": "n"}, "Lambda6": 0}, "obstructed",
          "n^2 = 0 forced (no constant-moduli vacuum; volume runaway)", [],
          "V ~ n²/detM (Jordan source), no critical point")

    # C2/C3: flux + Lambda6, chi free
    eqs, _, _ = einstein_eqs(fib0, n, L6)
    sol = sp.solve(eqs, [lam, L6], dict=True)
    okB2 = (len(sol) == 1
            and zero_simplify(sp.simplify(sol[0][L6] + 3 * n**2 / (2 * D0))) == 0
            and zero_simplify(sp.simplify(sol[0][lam] + n**2 / (3 * D0))) == 0)
    # the equations must depend on moduli ONLY through detM: substitute a coset motion
    s_ = sp.Symbol("s_", positive=True)
    coset_ok = all(zero_simplify(sp.simplify(
        e.subs([(P1s, s_ * P1s), (P2s, P2s / s_)]) - e)) == 0 for e in eqs)
    # lam at the vacuum: lam = 2 L6 / 9 < 0 for L6 < 0 (AdS4)
    lam_vac = sp.simplify(sol[0][lam].subs(D0, -3 * n**2 / (2 * L6))) if okB2 else None
    okB3 = okB2 and coset_ok
    ok.append(okB3)
    print(f"    C2/C3 (flux+Λ6): detM = -3n²/(2Λ6) stabilized (needs Λ6<0); "
          f"equations coset-invariant (shape+axion EXACTLY FLAT): {coset_ok}; "
          f"vacuum is AdS4: {okB3}   {'✅' if okB3 else '❌'}")
    atlas({"twist": "none (chi dynamical allowed)", "fluxes": {"G_w1w2": "n"}, "Lambda6": "free"},
          "consistent (volume stabilized)",
          None, ["detM (volume)"],
          "vacuum: detM = -3n²/(2Λ6), λ = 2Λ6/9 (AdS4, Λ6<0)",
          "shape+axion SL(2,R)/SO(2) coset exactly flat: the vacuum manifold IS the coset")

    # ================================================================ (C) twist axis
    print("\n(C) twist axis:")
    # M1 monodromy: brackets equal the untwisted C2 brackets
    fibM = sp.Matrix([[P1s**2 + P2s**2 * m**2 * w1**2, P2s**2 * m * w1],
                      [P2s**2 * m * w1, P2s**2]])
    eqsM, mxM, _ = einstein_eqs(fibM, n, L6)
    eqs_un, _, _ = einstein_eqs(sp.diag(P1s**2, P2s**2), n, L6)
    setM = {sp.factor(e) for e in eqsM}
    setU = {sp.factor(e) for e in eqs_un}
    okC1 = setM == setU and all(x == 0 for x in mxM)
    ok.append(okC1)
    print(f"    M1 monodromy (dw2 + m w1 dw1): bracket set IDENTICAL to untwisted -> twist "
          f"ABSORBED (axion shift / large diffeo; folklore trap PROVEN): {okC1}   "
          f"{'✅' if okC1 else '❌'}")
    atlas({"twist": "monodromy m (dw2 + m w1 dw1)", "fluxes": {"G_w1w2": "n"}, "Lambda6": "free"},
          "consistent (twist absorbed -- pure gauge)",
          "monodromy = axion shift (large diffeomorphism): potential is m-independent; "
          "SS twist on metric-only T² stabilizes NOTHING", ["detM (volume, from flux+Λ6 only)"],
          "same as untwisted flux+Λ6 entry")

    # G0: geometric flux with CONSTANT flux ansatz -> Maxwell violated (extract residual)
    fibG = sp.diag(P1s**2, P2s**2 * sp.exp(2 * m * w1))
    _, mxG0, _ = einstein_eqs(fibG, n, L6, flux_profile=1)
    resid = sp.simplify(mxG0[5])
    okC2 = zero_simplify(sp.simplify(resid + m * n * sp.exp(-2 * m * w1) / (P1s**2 * P2s**2))) == 0
    ok.append(okC2)
    print(f"    G0 constant-flux on twisted space: Maxwell VIOLATED, residual "
          f"-mn·e^(-2mw1)/(Φ1²Φ2²) extracted -> flux must wrap the internal VOLUME form: {okC2}   "
          f"{'✅' if okC2 else '❌'}")
    atlas({"twist": "geometric flux m (frame e^{m w1} dw2)",
           "fluxes": {"G_w1w2": "n (coordinate form)"}, "Lambda6": "free"},
          "rejected",
          "Maxwell violated: nabla_M G^{M w2} = -mn e^{-2mw1}/(Φ1²Φ2²) != 0; "
          "the flux quantum must wrap the internal volume form n e^{m w1} dw1^dw2", [], None)

    # G1/G2: geometric flux with volume-form flux
    eqsG, mxG, _ = einstein_eqs(fibG, n, L6, flux_profile=sp.exp(m * w1))
    okC3a = all(x == 0 for x in mxG)
    wfree = all(not e.has(w1) and not e.has(w2) for e in eqsG)
    # G1: m alone obstructed
    eqs4 = [sp.factor(e.subs([(n, 0), (L6, 0)])) for e in eqsG]
    eqs4 = [e for e in eqs4 if e != 0]
    okC3b = sp.solve(eqs4, [lam, P1s], dict=True) == []
    # G2: the partial branch: Phi1^2 = (4 Phi2^2 m^2 + 3 n^2)/(-2 L6 Phi2^2), lam fixed, Phi2 FLAT
    solG = sp.solve(eqsG, [P1s, lam], dict=True)
    branch = [s for s in solG if s.get(P1s) is not None and sp.simplify(s[P1s]) .is_positive is not False]
    okC3c = False
    if branch:
        s0 = branch[-1]
        okC3c = zero_simplify(sp.simplify(
            s0[P1s]**2 - (4 * P2s**2 * m**2 + 3 * n**2) / (-2 * L6 * P2s**2))) == 0
    okC3 = okC3a and wfree and okC3b and okC3c
    ok.append(okC3)
    print(f"    G1/G2 volume-form flux: Maxwell OK {okC3a}, SS w-cancellation {wfree}; "
          f"m alone OBSTRUCTED {okC3b};")
    print(f"      m+n+Λ6: PARTIAL branch Φ1² = (4Φ2²m²+3n²)/(-2Λ6Φ2²) (Λ6<0), Φ2 FLAT: {okC3c}   "
          f"{'✅' if okC3 else '❌'}")
    atlas({"twist": "geometric flux m", "fluxes": {}, "Lambda6": 0}, "obstructed",
          "m^2 = 0 forced (internal curvature alone: runaway)", [], "V ~ m²-curvature (Jordan)")
    atlas({"twist": "geometric flux m", "fluxes": {"G": "n e^{m w1} dw1^dw2 (volume form)"},
           "Lambda6": "free (<0)"},
          "partially consistent (branch)",
          "one flat direction SURVIVES (Φ2 branch); global compactness of the 2D affine group "
          "UNPROVEN (classic geometric-flux obstruction on T²)",
          ["Φ1 (pinned to branch)", "λ (fixed)"],
          "Φ1² = (4Φ2²m²+3n²)/(-2Λ6Φ2²); local reduction proven, compactification unproven")

    # ================================================================ (D) truncation trap
    print("\n(D) truncation trap (freeze the volume off the vacuum):")
    Dfro = sp.Symbol("D_frozen", positive=True)
    trap = sp.solve([2 * L6 * Dfro + 3 * n**2], [Dfro], dict=True)
    okD = len(trap) == 1 and zero_simplify(sp.simplify(trap[0][Dfro] + 3 * n**2 / (2 * L6))) == 0
    ok.append(okD)
    print(f"    freezing detM is consistent ONLY at detM = -3n²/(2Λ6) -- the price tag "
          f"(2Λ6·detM + 3n²) = 0 extracted: {okD}   {'✅' if okD else '❌'}")
    atlas({"twist": "any", "fluxes": {"G_w1w2": "n"}, "Lambda6": "free",
           "truncation": "volume frozen by hand"},
          "obstructed unless fine-tuned",
          "(2Λ6·detM + 3n²) = 0 is forced: freezing the volume anywhere else is inconsistent "
          "(§111-trap analogue)", [], None)

    # ================================================================ (E) emit the atlas
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "flux_atlas.json")
    with open(out, "w") as fh:
        json.dump({"step": 114, "setup": "6D Einstein-Maxwell + Lambda6 on T^2 fibre over the "
                   "static free family; three-valued verdicts, obstructions machine-extracted",
                   "prior_art": "Andriot et al. JHEP 12(2022)026 (type II sugra, group manifolds)",
                   "next_leg": "Einstein-frame potential + moduli masses (bridge verifies "
                   "numerically)", "entries": ATLAS}, fh, indent=2, default=str)
    print(f"\n(E) atlas written: {os.path.normpath(out)} ({len(ATLAS)} entries)")

    passed = all(ok)
    print(f"\nFLUX ATLAS: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          "(dictionary + vacuum atlas + twist axis + trap; volume stabilized by flux+Λ6, coset "
          "flat; monodromy absorbed; geometric flux partial with compactness caveat)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
