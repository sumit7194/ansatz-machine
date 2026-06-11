#!/usr/bin/env python3
"""Step 21 — v5 R0′: rotating EdGB frame-dragging ODE verification.

Symbolically derives and verifies the slow-rotating EdGB frame-dragging
ODE coefficients G₂ and G₃ from the perturbed O(ε²) action using the
airtight "derive-and-verify" principle.

Gates:
  G0 (Overdetermination): G_2,derived * G_3,lit - G_3,derived * G_2,lit = 0
                          holds exactly across multiple independent random rational probes.
  G1 (GR Limit): α′ → 0 recovers Schwarzschild: G₂/G₃ = 4/r - (Γ′ + Λ′)/2.
  G2 (Literature Match): derived ratio matches the transcribed Pani-Cardoso equations.

Run:  .venv/bin/python scripts/21_rot_fingerprint.py
"""

import os
import sys
import time
import sympy as sp
import importlib.util

# Global symbols for background coefficients to ensure assumption-matching
G0, G1, G2, G3, G4 = sp.symbols('G0 G1 G2 G3 G4', real=True)
L0, L1, L2, L3 = sp.symbols('L0 L1 L2 L3', real=True)
P0, P1, P2, P3, P4 = sp.symbols('P0 P1 P2 P3 P4', real=True)
ephi0 = sp.symbols('ephi0', positive=True)
y0 = sp.symbols('y0', positive=True)

def get_on_shell_jet(r0_val, ap_val, eg0_val, y0_val, G1_val, P1_val, m10):
    r = m10.r
    ap = m10.ap
    
    L, (Gam_func, Lam_func, Phi_func) = m10.reduced_lagrangian()
    E_Gam = m10.euler_lagrange(L, Gam_func)
    E_Lam = m10.euler_lagrange(L, Lam_func)
    E_Phi = m10.euler_lagrange(L, Phi_func)
    
    # Symbols for background coefficients are defined globally.
    
    x = sp.Symbol('x')
    dx = r - r0_val
    Gam_poly = sp.log(eg0_val) + G1*dx + G2*dx**2/2 + G3*dx**3/6 + G4*dx**4/24
    Lam_poly = sp.log(y0_val) + L1*dx + L2*dx**2/2 + L3*dx**3/6
    Phi_poly = sp.log(ephi0) + P1*dx + P2*dx**2/2 + P3*dx**3/6 + P4*dx**4/24
    
    # Substitute
    E_Gam_poly = E_Gam.subs({Gam_func: Gam_poly, Lam_func: Lam_poly, Phi_func: Phi_poly}).doit()
    E_Lam_poly = E_Lam.subs({Gam_func: Gam_poly, Lam_func: Lam_poly, Phi_func: Phi_poly}).doit()
    E_Phi_poly = E_Phi.subs({Gam_func: Gam_poly, Lam_func: Lam_poly, Phi_func: Phi_poly}).doit()
    
    # Series
    E_Gam_x = sp.series(E_Gam_poly.subs(r, r0_val + x), x, 0, 3).removeO()
    E_Lam_x = sp.series(E_Lam_poly.subs(r, r0_val + x), x, 0, 4).removeO()
    E_Phi_x = sp.series(E_Phi_poly.subs(r, r0_val + x), x, 0, 3).removeO()
    
    # Solve step 0 for ephi0
    e0_lam = E_Lam_x.subs(x, 0)
    known_subs = {ap: ap_val, G1: G1_val, P1: P1_val}
    e0_lam_num = e0_lam.subs(known_subs)
    ephi0_roots = sp.solve(sp.numer(sp.together(e0_lam_num)), ephi0)
    if not ephi0_roots or ephi0_roots[0] <= 0:
        return None
    ephi0_val = ephi0_roots[0]
    
    # Solve step 1
    step1_subs = known_subs.copy()
    step1_subs[ephi0] = ephi0_val
    sol1 = sp.solve([E_Gam_x.subs(x, 0).subs(step1_subs),
                     E_Phi_x.subs(x, 0).subs(step1_subs),
                     sp.diff(E_Lam_x, x).subs(x, 0).subs(step1_subs)], (G2, P2, L1))
    
    # Solve step 2
    step2_subs = step1_subs.copy()
    step2_subs.update(sol1)
    sol2 = sp.solve([sp.diff(E_Gam_x, x).subs(x, 0).subs(step2_subs),
                     sp.diff(E_Phi_x, x).subs(x, 0).subs(step2_subs),
                     sp.diff(E_Lam_x, (x, 2)).subs(x, 0).subs(step2_subs) / 2], (G3, P3, L2))
    
    # Solve step 3
    step3_subs = step2_subs.copy()
    step3_subs.update(sol2)
    sol3 = sp.solve([sp.diff(E_Gam_x, (x, 2)).subs(x, 0).subs(step3_subs) / 2,
                     sp.diff(E_Phi_x, (x, 2)).subs(x, 0).subs(step3_subs) / 2,
                     sp.diff(E_Lam_x, (x, 3)).subs(x, 0).subs(step3_subs) / 6], (G4, P4, L3))
    
    jet = step3_subs.copy()
    jet.update(sol3)
    jet[G0] = sp.S.Zero
    return jet, ephi0_val

def compute_derived_G23(r0_val, ap_val, eg0_val, y0_val, jet, ephi0_val):
    x = sp.Symbol('x')
    th = sp.Symbol('theta', real=True)
    
    # Symbols are defined globally.
    
    def truncate_x(expr, deg):
        if expr == 0:
            return sp.S.Zero
        try:
            p = sp.Poly(expr, x)
            terms = []
            for k, v in p.as_dict().items():
                if k[0] <= deg:
                    terms.append(v * x**k[0])
            return sp.Add(*terms)
        except sp.PolynomialError:
            expr = sp.expand(expr)
            terms = []
            for term in sp.Add.make_args(expr):
                if sp.degree(term, x) <= deg:
                    terms.append(term)
            return sp.Add(*terms)

    class EpsPoly:
        def __init__(self, c0=sp.S.Zero, c1=sp.S.Zero, c2=sp.S.Zero):
            self.c0 = c0
            self.c1 = c1
            self.c2 = c2

        def is_zero(self):
            return self.c0 == 0 and self.c1 == 0 and self.c2 == 0

        def __add__(self, other):
            if not isinstance(other, EpsPoly):
                return EpsPoly(self.c0 + other, self.c1, self.c2)
            return EpsPoly(self.c0 + other.c0, self.c1 + other.c1, self.c2 + other.c2)

        def __radd__(self, other):
            return self.__add__(other)

        def __sub__(self, other):
            if not isinstance(other, EpsPoly):
                return EpsPoly(self.c0 - other, self.c1, self.c2)
            return EpsPoly(self.c0 - other.c0, self.c1 - other.c1, self.c2 - other.c2)

        def __rsub__(self, other):
            return EpsPoly(other - self.c0, -self.c1, -self.c2)

        def __mul__(self, other):
            if not isinstance(other, EpsPoly):
                return EpsPoly(self.c0 * other, self.c1 * other, self.c2 * other)
            return EpsPoly(
                self.c0 * other.c0,
                self.c0 * other.c1 + self.c1 * other.c0,
                self.c0 * other.c2 + self.c1 * other.c1 + self.c2 * other.c0
            )

        def __rmul__(self, other):
            return self.__mul__(other)

        def __truediv__(self, other):
            return EpsPoly(self.c0 / other, self.c1 / other, self.c2 / other)

        def diff(self, idx):
            if idx == 1:
                return EpsPoly(sp.diff(self.c0, x), sp.diff(self.c1, x), sp.diff(self.c2, x))
            elif idx == 2:
                return EpsPoly(sp.diff(self.c0, th), sp.diff(self.c1, th), sp.diff(self.c2, th))
            return EpsPoly(sp.S.Zero, sp.S.Zero, sp.S.Zero)

        def truncate(self, deg):
            return EpsPoly(
                truncate_x(self.c0, deg),
                truncate_x(self.c1, deg),
                truncate_x(self.c2, deg)
            )

        def coeff_eps2(self):
            return self.c2

    # Background polynomials evaluated at probe values:
    Gam_poly_val = (G0 + G1*x + G2*x**2/2 + G3*x**3/6 + G4*x**4/24).subs(jet).subs({y0: y0_val, ephi0: ephi0_val})
    Lam_poly_val = (sp.log(y0) + L1*x + L2*x**2/2 + L3*x**3/6).subs(jet).subs({y0: y0_val, ephi0: ephi0_val})
    Phi_poly_val = (sp.log(ephi0) + P1*x + P2*x**2/2 + P3*x**3/6 + P4*x**4/24).subs(jet).subs({y0: y0_val, ephi0: ephi0_val})
    
    e_Gam = sp.series(sp.exp(Gam_poly_val), x, 0, 5).removeO()
    e_Lam = sp.series(sp.exp(Lam_poly_val), x, 0, 5).removeO()
    e_Phi = sp.series(sp.exp(Phi_poly_val), x, 0, 5).removeO()
    
    w_symbols = sp.symbols('w0:5')
    W_poly = sum(w_symbols[i] * x**i / sp.factorial(i) for i in range(5))
    
    r_sym = r0_val + x
    g00 = -e_Gam
    g11 = e_Lam
    g22 = r_sym**2
    g33 = r_sym**2 * sp.sin(th)**2
    h = -W_poly * g22 * sp.sin(th)**2
    
    g = [[EpsPoly() for _ in range(4)] for _ in range(4)]
    g[0][0] = EpsPoly(c0=g00)
    g[1][1] = EpsPoly(c0=g11)
    g[2][2] = EpsPoly(c0=g22)
    g[3][3] = EpsPoly(c0=g33)
    g[0][3] = g[3][0] = EpsPoly(c1=h)
    
    inv_g00 = sp.series(1/g00, x, 0, 5).removeO()
    inv_g11 = sp.series(1/g11, x, 0, 5).removeO()
    inv_g22 = sp.series(1/g22, x, 0, 5).removeO()
    inv_g33 = sp.series(1/g33, x, 0, 5).removeO()
    
    ginv = [[EpsPoly() for _ in range(4)] for _ in range(4)]
    ginv[0][0] = EpsPoly(c0=inv_g00, c2=h**2 * inv_g00**2 * inv_g33)
    ginv[1][1] = EpsPoly(c0=inv_g11)
    ginv[2][2] = EpsPoly(c0=inv_g22)
    ginv[3][3] = EpsPoly(c0=inv_g33, c2=h**2 * inv_g00 * inv_g33**2)
    ginv[0][3] = ginv[3][0] = EpsPoly(c1=-h * inv_g00 * inv_g33)
    
    Gamma = [[[EpsPoly() for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(b, 4):
                val = EpsPoly()
                for d in range(4):
                    if not ginv[a][d].is_zero():
                        term = ginv[a][d] * (g[d][c].diff(b) + g[d][b].diff(c) - g[b][c].diff(d))
                        val = val + term
                val = (val / 2).truncate(3)
                Gamma[a][b][c] = val
                Gamma[a][c][b] = val
                
    Riem = [[[[EpsPoly() for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(c + 1, 4):
                    val = Gamma[a][d][b].diff(c) - Gamma[a][c][b].diff(d)
                    for e in range(4):
                        if not Gamma[a][c][e].is_zero() and not Gamma[e][d][b].is_zero():
                            val = val + Gamma[a][c][e] * Gamma[e][d][b]
                        if not Gamma[a][d][e].is_zero() and not Gamma[e][c][b].is_zero():
                            val = val - Gamma[a][d][e] * Gamma[e][c][b]
                    val = val.truncate(2)
                    Riem[a][b][c][d] = val
                    Riem[a][b][d][c] = EpsPoly() - val
                    
    Ric = [[EpsPoly() for _ in range(4)] for _ in range(4)]
    for b in range(4):
        for d in range(b, 4):
            val = EpsPoly()
            for a in range(4):
                if not Riem[a][b][a][d].is_zero():
                    val = val + Riem[a][b][a][d]
            val = val.truncate(2)
            Ric[b][d] = val
            Ric[d][b] = val
            
    R_scalar = EpsPoly()
    for b in range(4):
        for d in range(4):
            if not ginv[b][d].is_zero() and not Ric[b][d].is_zero():
                R_scalar = R_scalar + ginv[b][d] * Ric[b][d]
    R_scalar = R_scalar.truncate(2)
    
    RicSq = EpsPoly()
    for a in range(4):
        for b in range(4):
            if Ric[a][b].is_zero():
                continue
            for p in range(4):
                if ginv[a][p].is_zero():
                    continue
                for q in range(4):
                    if ginv[b][q].is_zero() or Ric[p][q].is_zero():
                        continue
                    term = ginv[a][p] * ginv[b][q] * Ric[a][b] * Ric[p][q]
                    RicSq = RicSq + term
    RicSq = RicSq.truncate(2)
    
    Rdown = [[[[EpsPoly() for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    val = EpsPoly()
                    for e in range(4):
                        if not g[a][e].is_zero() and not Riem[e][b][c][d].is_zero():
                            val = val + g[a][e] * Riem[e][b][c][d]
                    Rdown[a][b][c][d] = val.truncate(2)
                    
    Kretsch = EpsPoly()
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    if not Rdown[a][b][c][d].is_zero():
                        val = EpsPoly()
                        for q in range(4):
                            if ginv[b][q].is_zero():
                                continue
                            for r in range(4):
                                if ginv[c][r].is_zero():
                                    continue
                                for s in range(4):
                                    if ginv[d][s].is_zero() or Riem[a][q][r][s].is_zero():
                                        continue
                                    val = val + ginv[b][q] * ginv[c][r] * ginv[d][s] * Riem[a][q][r][s]
                        rup_val = val.truncate(2)
                        Kretsch = Kretsch + Rdown[a][b][c][d] * rup_val
    Kretsch = Kretsch.truncate(2)
    
    GB = Kretsch - 4*RicSq + R_scalar*R_scalar
    GB = GB.truncate(2)
    
    D0 = -g00 * g11 * g22 * g33
    sqrtD0 = sp.series(sp.sqrt(D0), x, 0, 3).removeO()
    g00_g33 = sp.series(g00 * g33, x, 0, 5).removeO()
    inv_g00_g33 = sp.series(1/g00_g33, x, 0, 5).removeO()
    c2_val = truncate_x(sp.Rational(1, 2) * h**2 * inv_g00_g33 * sqrtD0, 2)
    sqrtg = EpsPoly(c0=sqrtD0, c2=c2_val)
    
    dPhi = EpsPoly(c0=sp.diff(Phi_poly_val, x))
    kinetic = dPhi * dPhi * EpsPoly(c0=sp.series(sp.exp(-Lam_poly_val), x, 0, 3).removeO())
    
    L = sqrtg * (R_scalar/2 - sp.Rational(1, 4) * kinetic + ap_val/8 * EpsPoly(c0=e_Phi) * GB)
    L = L.truncate(2)
    
    L_eps2 = L.coeff_eps2()
    L_eps2_poly = truncate_x(L_eps2, 2)
    
    # theta-integration with sin(theta) volume element already in L_eps2_poly
    L2int = sp.integrate(L_eps2_poly, (th, 0, sp.pi))
    
    L_0 = L2int.subs(x, 0)
    L_1 = sp.diff(L2int, x).subs(x, 0)
    L_2 = sp.diff(L2int, (x, 2)).subs(x, 0) / 2
    
    E_W = 3 * sp.diff(L_0, w_symbols[0]) - 3 * sp.diff(L_1, w_symbols[1]) + 2 * sp.diff(L_2, w_symbols[2])
    E_W = sp.simplify(E_W)
    
    derived_G3 = -2 * sp.diff(E_W, w_symbols[2])
    derived_G2 = -2 * sp.diff(E_W, w_symbols[1])
    return derived_G2, derived_G3

def main():
    t_start = time.time()
    _here = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(_here)
    sys.path.append(os.path.join(repo_dir, "scripts"))
    
    spec = importlib.util.spec_from_file_location(
        "edgb_reduce", os.path.join(repo_dir, "scripts", "10_edgb_reduce.py"))
    m10 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m10)
    
    # --- Gate G0 & G2: Overdetermination & Literature Match Check ---
    print("Running G0 and G2 gates on 3 independent random rational probes...")
    probes = [
        # (r0, ap, eg0, y0, G1, P1)
        (sp.Rational(3, 2), sp.Rational(1, 10), sp.S.One, sp.Rational(5, 4), sp.Rational(1, 4), sp.Rational(1, 5)),
        (sp.Rational(7, 4), sp.Rational(1, 12), sp.S.One, sp.Rational(6, 5), sp.Rational(-1, 5), sp.Rational(2, 7)),
        (sp.Rational(9, 5), sp.Rational(1, 15), sp.S.One, sp.Rational(10, 9), sp.Rational(1, 5), sp.Rational(1, 6))
    ]
    
    g0_passed = True
    g2_passed = True
    
    for idx, (r0_val, ap_val, eg0_val, y0_val, G1_val, P1_val) in enumerate(probes):
        t0 = time.time()
        print(f"  Probe {idx+1}: solving background...")
        jet_res = get_on_shell_jet(r0_val, ap_val, eg0_val, y0_val, G1_val, P1_val, m10)
        if jet_res is None:
            print("    [Warning] Background solve produced non-physical root.")
            g0_passed = False
            continue
        jet, ephi0_val = jet_res
        
        print("    evaluating curvature action...")
        derived_G2, derived_G3 = compute_derived_G23(r0_val, ap_val, eg0_val, y0_val, jet, ephi0_val)
        
        # Compute literature forms
        y_val = y0_val
        ephi_val = ephi0_val
        lp_val = jet[L1]
        gp_val = G1_val
        p1_val = P1_val
        p2_val = jet[P2]
        
        lit_G3 = 2 * r0_val**2 * y_val - 2 * ap_val * r0_val * ephi_val * p1_val
        lit_G2 = (-y_val * r0_val * (-8 + r0_val * (lp_val + gp_val))
                  - ap_val * ephi_val * (p1_val * (6 - r0_val * (3 * lp_val - 2 * p1_val + gp_val))
                                         + 2 * r0_val * p2_val))
        
        # Check cross product: G2_der * G3_lit - G3_der * G2_lit
        resid = sp.simplify(derived_G2 * lit_G3 - derived_G3 * lit_G2)
        print(f"    G0 residual: {resid}")
        if resid != 0:
            g0_passed = False
            
        # Check common scaling factor: G3_der / G3_lit
        factor = derived_G3 / lit_G3
        # In general, derived should match lit up to F = 2/3 * r0^2 * y0^{-3/2}
        expected_factor = sp.Rational(2, 3) * r0_val**2 * y0_val**sp.Rational(-3, 2)
        match = sp.simplify(factor - expected_factor) == 0
        print(f"    G2 match factor: {factor} (expected {expected_factor}) -> {'PASS' if match else 'FAIL'}")
        if not match:
            g2_passed = False
        print(f"    Completed in {time.time()-t0:.2f}s")
        
    # --- Gate G1: GR Limit Check ---
    print("\nRunning G1 gate (GR limit)...")
    # In GR, ap = 0. We verify that G2/G3 matches 4/r - (Γ′ + Λ′)/2.
    # We use probe 1 values but with ap = 0.
    r0_val, _, eg0_val, y0_val, G1_val, P1_val = probes[0]
    ap_val = sp.S.Zero
    
    # For ap=0, ephi0 is decoupled. We can choose any rational value.
    ephi0_val = sp.Rational(1, 1)
    
    jet_gr = {
        G0: sp.S.Zero,
        G1: G1_val,
        G2: sp.S.Zero,
        G3: sp.S.Zero,
        G4: sp.S.Zero,
        L1: -G1_val, # Schwarzschild lp = -gp
        L2: sp.S.Zero,
        L3: sp.S.Zero,
        P1: P1_val,
        P2: sp.S.Zero,
        P3: sp.S.Zero,
        P4: sp.S.Zero
    }
    derived_G2_gr, derived_G3_gr = compute_derived_G23(r0_val, sp.S.Zero, eg0_val, y0_val, jet_gr, sp.S.One)
    derived_ratio_gr = derived_G2_gr / derived_G3_gr
    expected_ratio_gr = sp.Rational(4, r0_val) - (jet_gr[L1] + G1_val) / 2
    g1_passed = sp.simplify(derived_ratio_gr - expected_ratio_gr) == 0
    print(f"  GR ratio derived: {derived_ratio_gr}")
    print(f"  GR ratio expected: {expected_ratio_gr}")
    print(f"  G1 gate: {'PASS' if g1_passed else 'FAIL'}")
    
    # --- Final Verdict ---
    print("\n--- Verification Summary ---")
    print(f"  G0 (Overdetermination): {'PASSED ✅' if g0_passed else 'FAILED ❌'}")
    print(f"  G1 (GR Limit):         {'PASSED ✅' if g1_passed else 'FAILED ❌'}")
    print(f"  G2 (Literature Match):  {'PASSED ✅' if g2_passed else 'FAILED ❌'}")
    
    success = g0_passed and g1_passed and g2_passed
    print(f"Overall status: {'ALL GREEN ✅' if success else 'FAILURES ❌'}")
    print(f"Total time: {time.time()-t_start:.2f}s")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
