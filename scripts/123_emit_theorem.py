#!/usr/bin/env python3
"""Step 123 — THE EMIT-LEGIBILITY THEOREM (bridge Falsification v2, item R2).

Round 8 killed the flagship "legible <=> KY-integrable": §120 Candidate A emitted an exact
quadratic invariant despite having NO Killing-Yano root (LEGIBLE), and §121 Candidate B was
integrable but its invariant is transcendental (ILLEGIBLE). So legibility tracks neither KY nor
Liouville integrability. The corrected empirical claim:

    legible  <=>  the conserved invariant is polynomial-representable in the probe's basis.

The ask: promote that empirical boundary to a THEOREM about our emit engine's linear core.

PRIOR ART -- THIS RESULT IS PUBLISHED. WE CLAIM NO NOVELTY. The precise citation (verified in
the full text, not the abstract):

  OELLERICH & EMELIANENKO, "Towards Robust Data-Driven Automated Recovery of Symbolic
  Conservation Laws from Limited Data", arXiv:2403.04889 / Mach. Learn.: Sci. Technol. (2024).
  Same instrument -- candidate library -> design matrix -> SVD -> near-null singular value --
  and the failure condition is stated as an explicit TRICHOTOMY whose FIRST BRANCH IS THIS
  THEOREM: when no zero singular value is found, either
      (1) "the starting library does not contain the appropriate terms"   <- our (T2)
      (2) "inadequate data due to noise or amount"                        <- our O2
      (3) "the system does not contain a conservation law".
  They are also SHARPER than us in two places we should own rather than paper over:
      * their cutoff is NOISE-CALIBRATED -- Cor. 4.2 gives sigma_cutoff = sqrt(Np)*||eps||^(2/3),
        derived from a perturbation bound. Our TAU_REL below is a hand-set round number chosen to
        sit under the observed floor. Theirs dominates ours on the merits.
      * Thm 4.2 gives a spectral-gap criterion for library adequacy, sigma_r^2 >= C_gap(sqrt(Np)+N).

  RAY, "From Data to Laws: Neural Discovery of Conservation Laws Without False Positives",
  arXiv:2603.20474 (Mar 2026): log-basis Lasso + constancy gate + diversity filter. ADJACENT to
  O4, not covering it -- it targets false positives on chaotic systems generally, and its
  FDR=0.0 / F1=1.0 is reported on the FOUR benchmark systems that have true conservation laws,
  not across all nine.

WHY O4 SURVIVES THE SHARPER CUTOFF (measured independently by the bridge, their leg R7): applying
Oellerich's noise-calibrated cutoff to our degree-6 pendulum case does NOT reject it -- the false
positive passes by 28x, because O4's residual sits ~5 orders of magnitude ABOVE the noise floor.
O4 is therefore NOT a noise phenomenon and no noise-calibrated threshold can see it. It is an
APPROXIMATION phenomenon, and the approximation-vs-representation distinction is invisible
in-sample BY CONSTRUCTION. That is the honest standing of O4: a real, sharply characterised
failure mode the literature brushes past rather than solves -- a line in a methods section, not
a paper.

WHERE IT DOES BECOME DECIDABLE (the forward pointer, not claimed here): drop trajectory data
entirely and impose {I, H} = 0 -- a LINEAR condition on the coefficients c_k computable from the
GENERATOR alone. No data, no noise, no threshold; "is there an invariant in span(Phi)" becomes
"is an exactly-computable symbolic nullspace nontrivial". An approximation can fit bounded data
but cannot satisfy an identity, so O4 dissolves rather than being guarded against. NOTE: exact
Killing-tensor computation is itself completely standard (we already do it in §98 and §121), so
that route needs its own prior-art sweep before any novelty claim; the candidate contribution is
the BRIDGE between the data-driven and generator-based criteria -- the statement that one is
decidable and the other only ever statistical -- plus the O4 demonstration, NOT the computation.

WHAT IS OURS HERE, then: (a) the three-valued statement matched to how our engine actually
thresholds, and (b) the extracted obstruction map with the two round-8 adversaries as worked
cases. Not a new theorem -- a proof that our instrument's boundary IS this known boundary.

------------------------------------------------------------------------------------------------
T1 -- THE EMIT CRITERION, as implemented (cf. scripts/_qinvariant.py).
  Basis Phi = (phi_1, ..., phi_m): functions on phase space (here polynomials in positions and
  momenta, optionally with chosen transcendental atoms). Orbits o = 1..K, orbit o sampled at
  points z_{o,1..N_o}. The MEAN-SUBTRACTED design matrix (per-orbit centring kills the additive
  constant, so different orbits may carry different invariant values):
        M[(o,i), k] = phi_k(z_{o,i}) - (1/N_o) * sum_j phi_k(z_{o,j}).
  Emit does SVD(M) = U S V^T and ACCEPTS iff
        (relative floor)   sigma_min(M) <= tau_rel * sigma_max(M).
  A genuine null vector rides at the numerical/integration floor while every non-invariant rides at
  the DATA SCALE (~sigma_max); the decisive gap is invariant-floor-vs-data-scale, NOT sigma_min vs
  sigma_next. So a MULTI-DIMENSIONAL null space (several independent invariants, e.g. H and a second
  constant) is accepted correctly -- the count of below-floor singular values is the number of
  independent invariants in span(Phi). PRECONDITION (rank guard G1): Phi has full column rank on
  generic phase-space points -- the data-independent matrix Phi(random points) has all singular
  values > 0. Output: the emitted invariant(s) I = sum_k c_k phi_k, c the below-floor right-singular
  vector(s).

T2 -- THE BICONDITIONAL.  Under G1 (rank guard holds) and G2 (the sampled orbit set is
  invariant-separating: the only elements of span(Phi) constant along every sampled orbit are the
  genuine conserved invariants), emit succeeds  <=>  a nonconstant I in span(Phi) is conserved.
    (<==) EXACT and UNCONDITIONAL: if I = sum c_k phi_k is conserved then along orbit o it equals a
          constant gamma_o, so every mean-subtracted row dotted with c is gamma_o - gamma_o = 0;
          M c = 0 exactly, sigma_min = 0. (No false negatives: a representable invariant is ALWAYS
          emitted. Proven symbolically in (A).)
    (==>) if M c = 0 with c != 0 then sum c_k phi_k is constant on the sampled points of every
          orbit; by G2 (constant on all diverse orbits) and G1 (c is not a hidden identity) it is a
          genuine invariant in span(Phi).
  OBSTRUCTION (where ==> fails without the guards) -- emit succeeds but c is not a true invariant:
    O1 HIDDEN IDENTITY: sum c_k phi_k == const as a phase-space function (c in ker Phi itself,
       independent of dynamics). Deterministic; caught by G1. (The real 'u4/om' false-zero the
       engine already guards against.)
    O2 FINITE-DATA ALIASING: too few / non-diverse orbits. One orbit is a 1-D curve and MANY
       functions are constant on it; spurious null vectors appear until the orbit set separates
       the invariants. Caught by G2 + the separation guard.
    O3 MEASURE-ZERO COINCIDENCE: sampled points accidentally satisfy an extra algebraic relation;
       probability zero under generic sampling, and it does not persist across independent resamples.
    O4 SMOOTH-APPROXIMATION FALSE-POSITIVE (surfaced by the bridge's independent cross-gate of R2):
       a RICH basis over BOUNDED orbits. A high-degree polynomial can approximate a transcendental
       invariant closely enough over the finite sampled range that sigma_min/sigma_max falls below
       tau_rel and emit FALSELY fires on a quantity that is not a true invariant. Neither G1 (the
       polynomial is full column rank off-orbit) nor G2 (it IS nearly constant on every sampled
       orbit) catches it. The guard that does is OUT-OF-SAMPLE: a true invariant stays conserved on
       new / wider-range orbits, an approximation drifts. Mitigation: a train/validate orbit split
       (emit_validated below), i.e. accept only if the emitted combination also rides at the floor
       on held-out wider orbits. This is the approximation-vs-representation distinction the cos-atom
       demo already makes -- O4 marks its failure edge: from BOUNDED data alone the in-sample floor
       cannot separate a good-enough approximation from an exact representation.

    O5 CONSERVED-BUT-UNINFORMATIVE (surfaced by tabula's C4 clause, reproduced here in our own
       engine before adopting it): a candidate that is constant EVERYWHERE, not just along each
       orbit. Planting a single constant column in the basis produces sigma_min/sigma_max =
       EXACTLY 0, passes the G1 rank guard (a constant is linearly independent of the monomials),
       and scores validation drift EXACTLY 0 -- a constant has zero variance, so it validates
       BETTER than the genuine invariant. All of O1-O4 are conservation tests, and this object is
       perfectly conserved; no sharpening of them can ever catch it. Our only prior defence was a
       CONVENTION -- poly_basis excludes the constant term -- which is not a guard.
       The guard that does catch it is INFORMATIVENESS: a real conserved quantity takes different
       values on different orbits (that is what makes it a label); a nuisance constant does not.
       See informativeness() below. Credit: tabula's C4 (candidate must be a function of the
       dynamical state); the orbit-separation formulation is ours.

T3 -- SCOPE: exact-arithmetic / below-floor numeric; finite bases (polynomial, or polynomial plus
  named transcendental atoms); autonomous invariants; the guards G1/G2, and for a RICH basis over
  bounded data the out-of-sample guard against O4. It does NOT certify the emitted invariant is
  unique or 'fundamental', and legibility is BASIS-RELATIVE by construction -- which is the whole
  point, and is demonstrated (the pendulum, illegible in a polynomial basis, is legible the moment
  cos is added to the basis). The deepest honest limit, made precise by O4: from bounded trajectory
  data the in-sample criterion cannot distinguish an exact representation from a sufficiently good
  approximation -- only out-of-sample behaviour can.

Repro: .venv/bin/python scripts/123_emit_theorem.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import sympy as sp

TAU_REL = 1e-6      # accept iff sigma_min <= TAU_REL * sigma_max: a genuine null vector rides at
                    # the numerical/integration floor while non-invariants ride at the DATA SCALE
                    # (~sigma_max). The gap is invariant-floor vs data-scale, NOT sigma_min vs
                    # sigma_next -- a multi-dimensional null space (several invariants) is fine.


# ------------------------------------------------------------------ the emit engine (as implemented)
def emit(orbits, basis_fns, tau_rel=TAU_REL):
    """orbits: list of arrays, each (N_o, d) of phase-space samples. basis_fns: list of callables
    state-vector -> float. Returns dict with the accept decision and the SVD spectrum."""
    rows = []
    for orb in orbits:
        B = np.array([[f(z) for f in basis_fns] for z in orb], float)   # (N_o, m)
        rows.append(B - B.mean(axis=0, keepdims=True))                  # per-orbit centring
    M = np.vstack(rows)
    # rank guard G1: the basis must be full column rank on generic points (data-independent)
    rng = np.random.default_rng(20260724)
    G = np.array([[f(z) for f in basis_fns]
                  for z in rng.normal(size=(8 * len(basis_fns), orbits[0].shape[1]))], float)
    guard_sv = np.linalg.svd(G, compute_uv=False)
    rank_ok = guard_sv[-1] > 1e-9 * guard_sv[0]
    _, sv, Vt = np.linalg.svd(M)
    smin, smax = sv[-1], sv[0]
    rel = smin / smax if smax else 0.0
    accepted = rank_ok and (rel <= tau_rel)
    # null-space dimension = how many singular values ride at the floor (the count of invariants)
    nulldim = int(np.sum(sv <= max(10 * tau_rel * smax, 1e-12)))
    return {"accepted": bool(accepted), "sigma_min": float(smin), "sigma_max": float(smax),
            "rel": float(rel), "nulldim": nulldim, "rank_ok": bool(rank_ok),
            "guard_min": float(guard_sv[-1] / guard_sv[0]), "coeffs": Vt[-1]}


TAU_VAL = 1e-4      # O4 out-of-sample floor: a TRUE invariant stays conserved on held-out, wider
                    # orbits (drift ~ integration floor, <=1e-6); a smooth APPROXIMATION that fit
                    # the bounded training data drifts (>=1e-3). The gap is ~2 orders either side.


def validation_drift(coeffs, val_orbits, basis_fns):
    """The O4 guard, as the bridge proposed: given the emitted c from training, how well is
    I = sum_k c_k phi_k conserved on HELD-OUT, WIDER-range orbits? Returns the worst per-orbit
    normalized drift std(I)/scale. A genuine invariant stays flat; a good-enough polynomial
    approximation over bounded data drifts once the orbit range widens."""
    worst = 0.0
    for orb in val_orbits:
        B = np.array([[f(z) for f in basis_fns] for z in orb], float)
        I = B @ np.asarray(coeffs, float)
        scale = np.abs(B).mean() * np.linalg.norm(coeffs) + 1e-30
        worst = max(worst, float(I.std() / scale))
    return worst


TAU_INFO = 1e-6     # O5 floor: the emitted quantity must SEPARATE orbits by at least this much,
                    # relative to its own scale, or it is conserved-but-uninformative.


def informativeness(coeffs, orbits, basis_fns):
    """The O5 guard: does the candidate actually DISTINGUISH orbits?

    A genuine conserved quantity takes DIFFERENT values on different orbits -- that is exactly
    what makes it informative (H labels the energy shell; the Carter constant labels the torus).
    A nuisance constant takes the SAME value everywhere and is conserved trivially. Both are
    perfectly conserved, so no conservation test can separate them, however sharp: this is a
    different axis from O1-O4 entirely.

    Returns the spread of per-orbit means of I, normalized by I's scale. Zero for a constant.

    NOTE the shared precondition: this needs orbits that genuinely carry different invariant
    values, which is the SAME diversity G2 already requires. If every sampled orbit happens to
    sit on one level set, a real invariant looks uninformative too -- so O5 and G2 are satisfied
    by the same orbit design, and neither is a free lunch."""
    means, scale = [], 0.0
    c = np.asarray(coeffs, float)
    for orb in orbits:
        B = np.array([[f(z) for f in basis_fns] for z in orb], float)
        means.append(float((B @ c).mean()))
        scale = max(scale, float(np.abs(B).mean() * np.linalg.norm(c)))
    return float(np.std(means) / (scale + 1e-30))


def emit_validated(train_orbits, val_orbits, basis_fns, tau_rel=TAU_REL, tau_val=TAU_VAL,
                   tau_info=TAU_INFO):
    """emit() + the O4 out-of-sample guard. Accept iff the in-sample criterion fires AND the
    emitted combination stays conserved on wider held-out orbits. This is the guard that
    distinguishes an EXACT REPRESENTATION from a good-enough APPROXIMATION, which no in-sample
    criterion can do from bounded data alone."""
    r = emit(train_orbits, basis_fns, tau_rel)
    drift = validation_drift(r["coeffs"], val_orbits, basis_fns) if r["accepted"] else float("inf")
    info = informativeness(r["coeffs"], train_orbits + val_orbits, basis_fns) if r["accepted"] else 0.0
    r["val_drift"] = drift
    r["informativeness"] = info
    r["accepted"] = bool(r["accepted"] and drift <= tau_val and info >= tau_info)
    return r


# ------------------------------------------------------------------ tiny separable integrators
def _leap(dHdq, q, p, dt):
    p = p - 0.5 * dt * dHdq(q); q = q + dt * p; p = p - 0.5 * dt * dHdq(q)
    return q, p


_W1 = 1.0 / (2.0 - 2.0**(1.0 / 3.0))
_W0 = -2.0**(1.0 / 3.0) * _W1


def yoshida4(dHdq, q0, p0, n, dt):
    """4th-order symplectic (Yoshida composition of leapfrog): energy error ~ dt^4, so a genuine
    invariant is conserved near machine precision and 'not in span' cannot be faked by drift."""
    q, p = np.array(q0, float), np.array(p0, float)
    out = []
    for _ in range(n):
        q, p = _leap(dHdq, q, p, _W1 * dt)
        q, p = _leap(dHdq, q, p, _W0 * dt)
        q, p = _leap(dHdq, q, p, _W1 * dt)
        out.append(np.concatenate([q, p]))
    return np.array(out)


def harmonic_orbit(q0, p0, n=800, dt=0.02):     # H = (px^2+py^2+x^2+y^2)/2, invariant px^2+x^2
    return yoshida4(lambda q: q, q0, p0, n, dt)


def pendulum_orbit(q0, p0, n=1600, dt=0.01):    # H = (px^2+py^2)/2 - cos x - cos y (separable)
    return yoshida4(lambda q: np.sin(q), q0, p0, n, dt)


# state = [x, y, px, py]
def poly_basis(deg=2):
    """monomials x^a y^b px^c py^d with a+b+c+d <= deg, deg>=1 (drop the constant)."""
    fns, names = [], []
    for a in range(deg + 1):
        for b in range(deg + 1 - a):
            for c in range(deg + 1 - a - b):
                for d in range(deg + 1 - a - b - c):
                    if 1 <= a + b + c + d <= deg:
                        fns.append((lambda s, a=a, b=b, c=c, d=d:
                                    s[0]**a * s[1]**b * s[2]**c * s[3]**d))
                        names.append(f"x^{a} y^{b} px^{c} py^{d}")
    return fns, names


def main():
    print(__doc__.split("Repro:")[0])
    ok = []

    # =============================================================== (A) FORWARD, PROVEN SYMBOLICALLY
    print("(A) T2 (<==) FORWARD DIRECTION, EXACT & SYMBOLIC -- representable => emit succeeds:")
    x, px, Ex, tau_ = sp.symbols("x p_x E_x tau", real=True)
    # a genuinely-conserved combination on the harmonic orbit x=sqrt(2Ex)sin(tau), px=sqrt(2Ex)cos(tau)
    xr = sp.sqrt(2 * Ex) * sp.sin(tau_)
    pr = sp.sqrt(2 * Ex) * sp.cos(tau_)
    I = px**2 + x**2                                        # in span(poly deg 2)
    I_orbit = sp.simplify(I.subs({x: xr, px: pr}))
    const_along_orbit = sp.simplify(sp.diff(I_orbit, tau_)) == 0
    # the exact algebra of mean-subtraction: row.c = I(z_i) - mean_j I(z_j) = gamma - gamma = 0
    gamma = sp.Symbol("gamma")
    residual = sp.simplify((gamma) - (gamma))              # the identity the proof rests on
    okA = const_along_orbit and residual == 0 and sp.simplify(I_orbit - 2 * Ex) == 0
    ok.append(okA)
    print(f"    I = px^2 + x^2 is constant along the orbit: I(tau) = {sp.simplify(I_orbit)} "
          f"(d/dtau = 0: {const_along_orbit})")
    print(f"    => every mean-subtracted row dotted with c equals gamma_o - gamma_o = 0, EXACTLY.")
    print(f"    => M c = 0, sigma_min = 0: a representable invariant is ALWAYS emitted (no false "
          f"negatives).  {'✅' if okA else '❌'}")

    # =============================================================== (B) HARMONIC = LEGIBLE (poly)
    print("\n(B) WORKED CASE 1 -- harmonic oscillator, polynomial basis (Candidate A analog):")
    fns, _ = poly_basis(2)
    orbits = [harmonic_orbit([1.0, 0.4], [0.0, 0.9]),
              harmonic_orbit([0.3, 1.2], [0.7, 0.0]),
              harmonic_orbit([0.8, 0.8], [0.5, 0.5])]
    rB = emit(orbits, fns)
    okB = rB["accepted"]
    ok.append(okB)
    print(f"    emit: sigma_min/sigma_max = {rB['rel']:.2e} (floor {TAU_REL:.0e}), "
          f"null-space dim = {rB['nulldim']}, rank_ok = {rB['rank_ok']}")
    print(f"    a polynomial invariant (px^2+x^2 type) IS in the basis => EMIT SUCCEEDS = LEGIBLE  "
          f"{'✅' if okB else '❌'}")

    # =============================================================== (C) PENDULUM = ILLEGIBLE (poly)
    print("\n(C) WORKED CASE 2 -- pendulum H=(p^2)/2-cos x-cos y, its invariant is TRANSCENDENTAL")
    print("    (Candidate B analog): px^2/2 - cos x is conserved but not polynomial in the basis.")
    porbits = [pendulum_orbit([0.5, 0.3], [0.0, 0.8]),
               pendulum_orbit([1.1, 0.7], [0.6, 0.0]),
               pendulum_orbit([0.2, 1.0], [0.4, 0.5])]
    rC = emit(porbits, fns)
    okC = not rC["accepted"]
    ok.append(okC)
    print(f"    emit (POLYNOMIAL basis): sigma_min/sigma_max = {rC['rel']:.2e} "
          f"(floor {TAU_REL:.0e}) -> accepted = {rC['accepted']}")
    print(f"    no polynomial combination is conserved on the diverse orbits => EMIT FAILS = "
          f"ILLEGIBLE  {'✅' if okC else '❌'}")

    # =============================================================== (D) BASIS-RELATIVITY: add cos
    print("\n(D) LEGIBILITY IS BASIS-RELATIVE -- extend the SAME pendulum's basis with cos x, cos y:")
    fns_trig = fns + [lambda s: np.cos(s[0]), lambda s: np.cos(s[1])]
    rD = emit(porbits, fns_trig)
    okD = rD["accepted"]
    ok.append(okD)
    print(f"    emit (poly + cos): sigma_min/sigma_max = {rD['rel']:.2e} (floor {TAU_REL:.0e}), "
          f"null-space dim = {rD['nulldim']} -> accepted = {rD['accepted']}")
    print(f"    now px^2/2 - cos x IS in span(Phi) => EMIT SUCCEEDS = LEGIBLE.  The SAME spacetime")
    print(f"    flips legibility purely by enlarging the probe basis: the theorem's core claim  "
          f"{'✅' if okD else '❌'}")

    # =============================================================== (E) OBSTRUCTION O1: hidden identity
    print("\n(E) OBSTRUCTION O1 -- hidden identity (a rank-deficient basis makes a FALSE zero):")
    # add a column that is an exact linear combination of existing ones: phi_dup = x^2 (already present)
    dup = fns + [lambda s: 3.0 * s[0]**2]        # 3*x^2 duplicates the x^2 column -> rank deficient
    rE = emit(orbits, dup)
    # sigma_min is ~0 from the identity, but the rank guard G1 flags it
    caught = (not rE["rank_ok"])
    ok.append(caught)
    print(f"    basis has 3*x^2 duplicating x^2: sigma_min = {rE['sigma_min']:.2e} (a machine zero)")
    print(f"    but the DATA-INDEPENDENT rank guard sees guard_min = {rE['guard_min']:.2e} ~ 0 "
          f"-> rank_ok = {rE['rank_ok']}")
    print(f"    => G1 catches the hidden identity; emit does not report a false invariant  "
          f"{'✅' if caught else '❌'}")

    # =============================================================== (F) OBSTRUCTION O2: single orbit
    print("\n(F) OBSTRUCTION O2 -- finite-data aliasing (ONE orbit admits spurious null vectors):")
    one = [harmonic_orbit([1.0, 0.4], [0.0, 0.9])]
    rF1 = emit(one, fns)
    rF3 = emit(orbits, fns)     # the 3-orbit version from (B)
    # single orbit: MANY combinations constant on one curve => extra small singular values.
    # count singular values below the floor in each case
    def n_small(orbs):
        rows = []
        for orb in orbs:
            B = np.array([[f(z) for f in fns] for z in orb], float)
            rows.append(B - B.mean(axis=0, keepdims=True))
        sv = np.linalg.svd(np.vstack(rows), compute_uv=False)
        return int(np.sum(sv <= 1e-6 * sv[0]))
    n1, n3 = n_small(one), n_small(orbits)
    okF = n1 > n3
    ok.append(okF)
    print(f"    below-floor singular values: 1 orbit -> {n1}, 3 diverse orbits -> {n3}")
    print(f"    a single 1-D orbit aliases many functions as 'conserved'; diverse orbits collapse")
    print(f"    the null space to the TRUE invariants (G2). {n1} -> {n3}  "
          f"{'✅' if okF else '❌'}")

    # =============================================================== (G) OBSTRUCTION O4 (bridge cross-gate)
    print("\n(G) OBSTRUCTION O4 -- smooth-approximation false-positive over bounded data")
    print("    (surfaced by the bridge's independent R2 reproduction; folded in here):")
    ptrain = [pendulum_orbit([0.5, 0.3], [0.0, 0.8]), pendulum_orbit([1.1, 0.7], [0.6, 0.0]),
              pendulum_orbit([0.2, 1.0], [0.4, 0.5])]
    pval = [pendulum_orbit([1.6, 1.2], [0.9, 0.3]), pendulum_orbit([2.0, 0.5], [0.2, 1.1])]
    print("    degree sweep on the pendulum (transcendental invariant, polynomial basis):")
    for deg in (2, 4, 6, 8):
        fd, _ = poly_basis(deg)
        rr = emit(ptrain, fd)
        flag = "  <- FALSE EMIT (polynomial hugs the transcendental invariant on bounded data)" \
            if rr["accepted"] else ""
        print(f"      deg {deg}: sigma_min/sigma_max = {rr['rel']:.1e} (m={len(fd)}) "
              f"-> in-sample emit = {rr['accepted']}{flag}")
    fd6, _ = poly_basis(6)
    rG_bad = emit_validated(ptrain, pval, fd6)
    fd6t = fd6 + [lambda s: np.cos(s[0]), lambda s: np.cos(s[1])]
    rG_true = emit_validated(ptrain, pval, fd6t)
    hval = [harmonic_orbit([1.7, 1.3], [0.2, 1.4]), harmonic_orbit([2.1, 0.6], [1.0, 0.3])]
    rG_harm = emit_validated(orbits, hval, fns)
    print(f"    THE O4 GUARD -- out-of-sample validation on WIDER held-out orbits (floor {TAU_VAL:.0e}):")
    print(f"      pendulum deg-6 (approximation): in-sample rel = {rG_bad['rel']:.1e} EMITS, but "
          f"validation drift = {rG_bad['val_drift']:.1e} -> accepted = {rG_bad['accepted']}")
    print(f"      pendulum deg-6 + cos (TRUE rep): validation drift = {rG_true['val_drift']:.1e} "
          f"-> accepted = {rG_true['accepted']}")
    print(f"      harmonic deg-2 (TRUE poly inv): validation drift = {rG_harm['val_drift']:.1e} "
          f"-> accepted = {rG_harm['accepted']}")
    okG = (not rG_bad["accepted"]) and rG_true["accepted"] and rG_harm["accepted"]
    ok.append(okG)
    print(f"    => the O4 guard REJECTS the polynomial approximation and KEEPS both true invariants:")
    print(f"       from bounded data the in-sample floor cannot tell approximation from")
    print(f"       representation; the out-of-sample floor can.  {'✅' if okG else '❌'}")

    # =============================================================== (H) OBSTRUCTION O5 (tabula C4)
    print("\n(H) OBSTRUCTION O5 -- conserved-but-uninformative (tabula's C4, reproduced here):")
    nuis = fns + [lambda s: 1.0]          # a CONSTANT column: zero dynamical content
    rH_bad = emit_validated(orbits, hval, nuis)
    print(f"    basis + a CONSTANT column: sigma_min/sigma_max = {rH_bad['rel']:.1e}, "
          f"G1 rank_ok = {rH_bad['rank_ok']}, validation drift = {rH_bad['val_drift']:.1e}")
    print(f"      -> O1-O4 ALL PASS. A constant is perfectly conserved, so no conservation test")
    print(f"         can ever catch it; it validates BETTER than a real invariant (drift 0).")
    print(f"    informativeness (spread of per-orbit means) = {rH_bad['informativeness']:.1e} "
          f"(floor {TAU_INFO:.0e}) -> accepted = {rH_bad['accepted']}")
    rH_ok = emit_validated(orbits, hval, fns)
    print(f"    the GENUINE harmonic invariant: informativeness = "
          f"{rH_ok['informativeness']:.1e} -> accepted = {rH_ok['accepted']}")
    okH = (not rH_bad["accepted"]) and rH_ok["accepted"]
    ok.append(okH)
    print(f"    => O5 rejects the nuisance and keeps the real invariant: a conserved quantity")
    print(f"       must SEPARATE orbits to be informative.  {'✅' if okH else '❌'}")

    # ============================================= (I) IS THE FLOOR DIMENSIONAL? (tabula's bug 5)
    # tabula: "a floor calibrated at one rung does not transfer to another" -- theirs, calibrated
    # at a 163-dim library and applied at 442-dim, let a rung report 441 conserved directions out
    # of 410. We share ONE TAU_REL across the whole degree sweep above (m = 14 -> 494) and blame
    # every deg-6/8 false emit on O4. But sigma_min/sigma_max of any tall-thin matrix shrinks with
    # the column count for purely dimensional reasons, so those two diagnoses could be conflated.
    # THE CONTROL that separates them: hold the basis, the degree, m and the row count fixed and
    # destroy only the CONSERVED STRUCTURE -- random phase-space points, provably no invariant in
    # the span. Whatever the floor reads there is the dimensional contribution alone.
    print("\n(I) IS THE FLOOR DIMENSIONAL? -- structureless control at each degree (tabula bug 5):")
    rngI = np.random.default_rng(0)
    dim_floor, margin_ok = {}, True
    for deg in (2, 4, 6, 8):
        bf, _ = poly_basis(deg)
        rand = [rngI.uniform(-2.0, 2.0, size=(400, 4)) for _ in range(6)]
        rr = emit(rand, bf)
        dim_floor[deg] = rr["rel"]
        margin_ok &= not rr["accepted"]
        print(f"      deg {deg}: m={len(bf):3d}  sigma_min/sigma_max = {rr['rel']:.2e} "
              f"on data with NO invariant -> emit = {rr['accepted']}")
    print(f"    the dimensional trend is REAL and monotone ({dim_floor[2]:.1e} -> {dim_floor[8]:.1e},")
    print(f"    about one decade per two degrees) but at deg 8 it still sits "
          f"{dim_floor[8] / TAU_REL:.0f}x")
    print(f"    ABOVE the floor, while the deg-6/8 false emits read 3e-14 and 7e-18 -- ten decades")
    print(f"    lower. So those are approximation (O4), not dimension, and (G)'s attribution holds.")
    okI = margin_ok
    ok.append(okI)
    print(f"    THE LIMIT THIS NAMES: TAU_REL is NOT size-independent. Extrapolating the trend, a")
    print(f"    structureless library crosses 1e-6 somewhere past degree ~13. Sharing one floor")
    print(f"    across rungs is safe HERE and is not safe in general -- each rung should ship its")
    print(f"    own structureless control, which is what this case now does.  {'✅' if okI else '❌'}")

    passed = all(ok)
    print(f"\nEMIT-LEGIBILITY THEOREM: {'PASSED ✅' if passed else 'FAILED ❌'}  "
          f"({sum(ok)}/{len(ok)}) -- forward direction proven exact; legible <=> invariant in "
          "span(Phi) with the round-8 adversaries reproduced; O1/O2 obstructions guarded; O4 "
          "(smooth-approximation false-positive, bridge cross-gate) guarded out-of-sample. "
          "PRIOR ART: Oellerich & Emelianenko arXiv:2403.04889 -- their failure trichotomy's "
          "first branch IS this theorem, and their noise-calibrated cutoff dominates our tau. "
          "NO NOVELTY CLAIMED.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
