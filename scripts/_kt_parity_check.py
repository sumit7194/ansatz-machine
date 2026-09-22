#!/usr/bin/env python3
"""p_phi parity is an EXACT grading of the deformation problem -- the axis §143 never varied.  (§146)

THE CLAIM.  On a stationary, axisymmetric background, write the parity of a momentum polynomial as
the parity of its degree in p_phi.  Then

    parity({A, B}) = parity(A) + parity(B)   (mod 2)

for any two such polynomials.  The reason is one line: t and phi are cyclic, so the Poisson bracket
reduces to the x and y terms, and neither d/dx nor d/dy nor d/dp_x nor d/dp_y changes the degree in
p_phi.  Nothing here is special to Kerr; it needs only the two Killing vectors.

WHY IT MATTERS.  The perturbative equation is {H0, F} = -{dH, K}.  H0 is p_phi-even and so are the
Schwarzschild building blocks H0 and L^2, so a product K = p_t^a p_phi^b H0^c (L^2)^e has parity b.
Then

    POLAR deformation (h_tt, h_rr, h_ang):   dH is p_phi-EVEN  -> source parity = b, SAME class as K
    AXIAL deformation (h_tphi, h_rphi, h_yphi): dH is p_phi-ODD -> source parity = b+1, OPPOSITE class

So F is sought in the same parity block as K for a polar deformation and in the other block for an
axial one.  These are different linear systems, not a harder and an easier version of one system --
which is why §143's prediction that the pole-order increments (2, 1, 0) hold "for every angular
sector" fails in the axial sector.  §143 varied the angular DEGREE (l = 2 -> l = 4) and correctly
found the increments unchanged; every case it tested was polar, so parity was held fixed throughout
and could not show up as a variable.

ONE OBSERVATION WORTH KEEPING.  drag1 and drag3 are the physical odd-parity slots, but they enter at
O(chi^1), and their O(chi^2) SLICE -- the piece the §142 reduction consumes -- comes from beating the
chi^1 deformation against Kerr's own chi^1 frame dragging, so it is p_phi-EVEN.  Reading "drag3 is the
odd sector" off the slot name and handing its chi^2 slice to the reduced solver would therefore test
the polar block while believing it tested the axial one.  The o1/o3 probe slots carry the axial
angular function at O(chi^2) directly and are genuinely odd; that is why they exist.

Usage: _kt_parity_check.py [--sabotage]   (seconds; exits nonzero on FAIL)

--sabotage inverts the expectation for the axial slots, which MUST turn the run red.  A checker that
has only ever printed "ok" has not been shown able to print anything else -- §5 of the brief, and the
reason this flag is not optional decoration.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

import _kt_carter_space as CS  # noqa: E402
import _kt_double as KD  # noqa: E402
import _kt_search as K  # noqa: E402

x, y = CS.x, CS.y


def setup():
    t_, ph = sp.symbols("t phi", real=True)
    K.set_dim((t_, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1, 2))
    return KD.kerr_chi_pieces()


def parities(expr):
    """The set of p_phi-degree parities present in a momentum polynomial (empty for 0)."""
    mom = list(K.MOM)
    i = [str(m) for m in mom].index("P_phi")
    num, _ = sp.fraction(sp.together(sp.expand(expr)))
    if num == 0:
        return set()
    return {m[i] % 2 for m in sp.Poly(sp.expand(num), *mom).monoms()}


def bracket(A, B):
    """Poisson bracket for a stationary axisymmetric system: only the x and y terms survive."""
    mom = list(K.MOM)
    Px, Py = mom[1], mom[2]
    s = sum(sp.diff(A, q) * sp.diff(B, pq) - sp.diff(A, pq) * sp.diff(B, q)
            for q, pq in ((x, Px), (y, Py)))
    return sp.cancel(sp.together(s))


def main(sabotage=False):
    GI = setup()
    Pt, Px, Py, Pphi = list(K.MOM)
    H0 = KD.hamiltonian(GI[0])
    Lsq = Py ** 2 + Pphi ** 2 / (1 - y ** 2)
    fails = []

    def check(label, got, want):
        ok = got == {want}
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<58s} parity {sorted(got)}  expect [{want}]")
        if not ok:
            fails.append(label)

    print("1. the building blocks are p_phi-even, so a product's parity is its power of p_phi")
    for nm, e in (("H0", H0), ("L^2", Lsq)):
        check(f"{nm}", parities(e), 0)

    print("\n2. the bracket adds parities (the grading itself)")
    basis = [("H0", H0, 0), ("L^2", Lsq, 0), ("p_phi", Pphi, 1), ("p_phi p_y", Pphi * Py, 1)]
    for na, A, pa in basis:
        for nb, B, pb in basis:
            r = bracket(A, B)
            if r == 0:
                continue
            check(f"{{{na}, {nb}}}", parities(r), (pa + pb) % 2)

    print("\n3. polar deformations are p_phi-even, axial ones are p_phi-odd")
    polar = ("l2tt", "l2rr", "l2ang", "l4tt", "l4rr", "l4ang")
    axial = ("o1tphi", "o3tphi", "o3rphi", "o3yphi")
    for s in polar + axial:
        dH = KD.hamiltonian(KD.ginv_perturbation(GI, CS.slot_h(s, x ** -2))[2])
        want = 0 if s in polar else 1
        check(f"dH[{s}]", parities(dH), (1 - want) if (sabotage and s in axial) else want)

    print("\n4. and therefore the two sectors pose sources in OPPOSITE parity blocks")
    for s, want_even in (("l2tt", True), ("o3tphi", False)):
        dH = KD.hamiltonian(KD.ginv_perturbation(GI, CS.slot_h(s, x ** -2))[2])
        for kn, Kp, b in (("K=L^2 (b=0)", Lsq, 0), ("K=p_phi p_y (b=1)", Pphi * Py, 1)):
            check(f"{{dH[{s}], {kn}}}", parities(bracket(dH, Kp)), b if want_even else (b + 1) % 2)

    print("\n5. the physical drag slots' O(chi^2) SLICE is even, not odd -- it is not the axial block")
    for s in ("drag1", "drag3"):
        dH = KD.hamiltonian(KD.ginv_perturbation(GI, CS.slot_h(s, x ** -2))[2])
        check(f"dH[{s}] chi^2 slice", parities(dH), 0)

    print("\n6. p_phi parity grades the PERTURBATIVE operator H0, NOT full Kerr")
    # H_Kerr carries g^tphi p_t p_phi, which is p_phi-ODD, so H_Kerr is not p_phi-homogeneous and
    # p_phi parity does not grade the unreduced problem.  What survives there is the COMBINED
    # (deg_t + deg_phi) parity.  Stated because "p_phi parity grades Kerr" would be a false reading
    # of §146, and the grading is a property of the operator the §142 reduction hands us.
    mom = list(K.MOM)
    def par2(e):
        num, _ = sp.fraction(sp.together(sp.expand(e)))
        return set() if num == 0 else {(m[0] % 2, m[3] % 2)
                                       for m in sp.Poly(sp.expand(num), *mom).monoms()}
    Hk = sum(KD.chi ** n * KD.hamiltonian(GI[n]) for n in range(3))
    d0, dk = par2(H0), par2(Hk)
    for nm, d, want_phi, want_comb in (("H0   ", d0, True, True), ("H_Kerr", dk, False, True)):
        got_phi = len({b for _, b in d}) == 1
        got_comb = len({(a + b) % 2 for a, b in d}) == 1
        for what, got, want in (("p_phi parity homogeneous", got_phi, want_phi),
                                ("combined t+phi homogeneous", got_comb, want_comb)):
            ok = got == want
            print(f"  {'ok  ' if ok else 'FAIL'}  {nm} {what:<30s} {got}  expect {want}")
            if not ok:
                fails.append(f"{nm} {what}")

    if sabotage:
        good = len(fails) == len(axial)
        print(f"\n{'PASS' if good else 'FAIL'} -- sabotage inverted {len(axial)} axial expectations "
              f"and the checker rejected {len(fails)} of them")
        return 0 if good else 1
    print("\n" + ("PASS -- p_phi parity is an exact grading; the axial sector is a different block"
                  if not fails else f"FAIL ({len(fails)}): {fails}"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sabotage="--sabotage" in sys.argv))
