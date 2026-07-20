#!/usr/bin/env python3
"""ck.py — Cartan–Karlhede machinery: the DECISION procedure for spacetime equivalence.

The costume problem, properly. Our §02 fingerprint filter compares curvature invariants:
necessary but NOT sufficient (matching invariants prove nothing), and on VSI/Kundt spacetimes
every polynomial invariant vanishes so the filter is blind by construction (README declares it).
Cartan–Karlhede is the actual decision procedure: compare curvature in a CANONICALLY FIXED frame,
order by order, until the invariant count and isotropy group both stabilize.

The pipeline (all three-valued -- UNDECIDED is a legitimate output):
    1. null_tetrad(geo)          arbitrary null tetrad from the metric (Gram-Schmidt, any chart)
    2. canonical_frame(geo, ...) fix the frame using the Petrov type (PND alignment + normalization)
    3. cartan_invariants(...)    the surviving frame components of curvature at orders 0, 1, ...
    4. equivalent(geo1, geo2)    compare invariant counts, isotropy dimensions, functional relations

CONVENTIONS (match analyzer.py, verified against §57): signature (-,+,+,+); tetrad vectors are
CONTRAVARIANT; l.n = -1, m.mbar = +1, all other products zero;
Psi0 = C(l,m,l,m), Psi1 = C(l,n,l,m), Psi2 = C(l,m,mbar,n), Psi3 = C(l,n,mbar,n), Psi4 = C(n,mbar,n,mbar).

NOTHING is trusted from memory: the null-rotation transformation laws are DERIVED by transforming
the tetrad vectors and recomputing the scalars from the Weyl tensor (the §102 discipline -- never
trust a textbook constant you can machine-check). The isotropy tables have literature errata as
recent as MacCallum (2020), so we compute rather than tabulate wherever we can.

STATUS: v0 spike -- 4D, Petrov types D and N, vacuum and Lambda-vacuum. Everything else UNDECIDED.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

from analyzer import UNKNOWN, petrov_type, weyl_scalars, weyl_tensor

EQUIVALENT = "EQUIVALENT"
INEQUIVALENT = "INEQUIVALENT"
UNDECIDED = "UNDECIDED"

# --------------------------------------------------------------------------- domain
# A CK tool MUST let the caller declare the domain: signs of frame normalizations and even
# the Petrov type can change across a horizon, and SymPy will otherwise carry |...| branch
# artifacts forever (the §111 |sin theta| lesson). Declare e.g. set_domain(sp.Q.positive(r - 2*M)).
_ASSUME = []


def set_domain(*conds):
    """Declare the region of validity (SymPy assumption predicates)."""
    global _ASSUME
    _ASSUME = [c for c in conds if c is not None]


def domain():
    return sp.And(*_ASSUME) if _ASSUME else None


def refine(e):
    d = domain()
    return sp.refine(e, d) if d is not None else e


def domain_samples(free, tries=40):
    """Numeric points satisfying the declared domain -- used only to DECIDE A BRANCH,
    never to prove anything: every branch choice is verified downstream (check_tetrad)."""
    import itertools
    import random
    d = domain()
    grid = [sp.Rational(1, 2), 1, 2, 3, 5, 7, sp.Rational(3, 2), 11]
    free = list(free)
    out = []
    rnd = random.Random(20260721)
    for _ in range(tries):
        sub = {s: rnd.choice(grid) for s in free}
        if d is not None:
            try:
                if d.subs(sub) is sp.false:
                    continue
                val = sp.simplify(d.subs(sub))
                if val is sp.false or val == False:            # noqa: E712
                    continue
            except Exception:
                continue
        out.append(sub)
        if len(out) >= 6:
            break
    return out


def sign_of(e):
    """Sign of an expression IN THE DECLARED DOMAIN: -1, +1, or None (undecided).

    Three escalating routes: (1) assumption query; (2) structural -- factor and look for
    a signed product of even powers (this is what catches -(2rho-M)^2/(2rho+M)^2, the
    isotropic-chart lapse); (3) consistent numeric probing inside the domain."""
    e = refine(sp.simplify(e))
    d = domain()
    if e.is_number:
        return 1 if e > 0 else (-1 if e < 0 else None)
    if d is not None and sp.ask(sp.Q.positive(e), d):
        return 1
    if d is not None and sp.ask(sp.Q.negative(e), d):
        return -1
    if d is None and e.is_positive:
        return 1
    if d is None and e.is_negative:
        return -1
    s = sp.simplify(sp.sign(refine(e)))
    if s == 1:
        return 1
    if s == -1:
        return -1
    # (2) structural: is it (sign) x (even powers only)?
    fe = sp.factor(sp.together(e))
    num, den = sp.fraction(fe)

    def _even_power_sign(expr):
        """+1/-1 if expr is a nonzero constant times even powers, else None."""
        c, factors = sp.factor(expr).as_coeff_mul()
        sgn = 1 if c > 0 else -1
        for f in factors:
            b, ex = f.as_base_exp()
            if ex.is_Integer and ex % 2 == 0:
                continue
            if (sp.ask(sp.Q.positive(f), d) if d is not None else f.is_positive):
                continue
            if (sp.ask(sp.Q.negative(f), d) if d is not None else f.is_negative):
                sgn = -sgn
                continue
            return None
        return sgn
    sn, sd = _even_power_sign(num), _even_power_sign(den)
    if sn is not None and sd is not None:
        return sn * sd
    # (3) numeric probe inside the domain (branch selection only; verified downstream)
    samples = domain_samples(e.free_symbols)
    signs = set()
    for sub in samples:
        try:
            v = sp.N(e.subs(sub))
            if v.is_real and abs(v) > 1e-12:
                signs.add(1 if v > 0 else -1)
        except Exception:
            continue
    if len(signs) == 1:
        return signs.pop()
    return None


# --------------------------------------------------------------------------- basics
def zsimp(e):
    """Aggressive-but-safe zero test / simplifier for frame components, domain-aware."""
    e = refine(sp.simplify(sp.expand(sp.together(e))))
    if e == 0:
        return sp.S.Zero
    r = refine(sp.radsimp(e))
    r = sp.simplify(sp.expand(sp.powdenest(r, force=True)))
    return sp.S.Zero if sp.simplify(r) == 0 else r


def dot(g, u, v):
    n = g.shape[0]
    return zsimp(sum(g[a, b] * u[a] * v[b] for a in range(n) for b in range(n)))


def orthonormal_frame(geo, seeds=None):
    """Gram-Schmidt an orthonormal frame (e0 timelike, e1..e3 spacelike) out of the
    coordinate basis. Chart-agnostic: works for off-diagonal metrics (PG, Kerr-like)."""
    g, n = geo.g, geo.n
    seeds = list(range(n)) if seeds is None else list(seeds)
    built = []
    for i in seeds:
        v = [sp.Integer(1) if k == i else sp.Integer(0) for k in range(n)]
        for u, nu in built:
            c = sp.simplify(dot(g, v, u) / nu)
            v = [zsimp(v[k] - c * u[k]) for k in range(n)]
        nv = dot(g, v, v)
        if nv == 0:
            raise ValueError(f"Gram-Schmidt hit a null direction on seed {i}")
        built.append((v, nv))
    frame, sigs = [], []
    for v, nv in built:
        sg = sign_of(nv)
        if sg is None:
            raise ValueError(
                f"cannot determine the sign of a frame norm in the declared domain: {nv}. "
                "Declare the region with ck.set_domain(...) -- signs (and the Petrov type) "
                "genuinely differ across horizons.")
        s = sp.sqrt(refine(sp.simplify(sg * nv)))       # positive argument: no Abs branch
        frame.append([zsimp(x / s) for x in v])
        sigs.append(sg)
    # the timelike leg must come first
    if sigs[0] != -1:
        for j, s in enumerate(sigs):
            if s == -1:
                frame[0], frame[j] = frame[j], frame[0]
                sigs[0], sigs[j] = sigs[j], sigs[0]
                break
    return frame


def null_tetrad(geo, seeds=None):
    """(l, n, m, mbar) with l.n = -1, m.mbar = 1 -- from an arbitrary chart."""
    e = orthonormal_frame(geo, seeds)
    s2 = sp.sqrt(2)
    l = [zsimp((e[0][k] + e[1][k]) / s2) for k in range(4)]
    nn = [zsimp((e[0][k] - e[1][k]) / s2) for k in range(4)]
    m = [zsimp((e[2][k] + sp.I * e[3][k]) / s2) for k in range(4)]
    mb = [zsimp((e[2][k] - sp.I * e[3][k]) / s2) for k in range(4)]
    return (l, nn, m, mb)


def check_tetrad(geo, tet):
    """Verify the null-tetrad normalization (a self-check we never skip)."""
    l, nn, m, mb = tet
    g = geo.g
    conds = {"l.l": dot(g, l, l), "n.n": dot(g, nn, nn), "m.m": dot(g, m, m),
             "l.n+1": dot(g, l, nn) + 1, "m.mb-1": dot(g, m, mb) - 1,
             "l.m": dot(g, l, m), "n.m": dot(g, nn, m)}
    return {k: v for k, v in conds.items() if v != 0}


# --------------------------------------------------------------------------- Lorentz moves
def null_rotation_about_n(tet, a):
    """Keeps n, moves l: l -> l + a mbar + abar m + |a|^2 n."""
    l, nn, m, mb = tet
    ab = sp.conjugate(a)
    l2 = [zsimp(l[k] + a * mb[k] + ab * m[k] + a * ab * nn[k]) for k in range(4)]
    m2 = [zsimp(m[k] + a * nn[k]) for k in range(4)]
    mb2 = [zsimp(mb[k] + ab * nn[k]) for k in range(4)]
    return (l2, nn, m2, mb2)


def null_rotation_about_l(tet, b):
    """Keeps l, moves n: n -> n + b mbar + bbar m + |b|^2 l."""
    l, nn, m, mb = tet
    bb = sp.conjugate(b)
    n2 = [zsimp(nn[k] + b * mb[k] + bb * m[k] + b * bb * l[k]) for k in range(4)]
    m2 = [zsimp(m[k] + b * l[k]) for k in range(4)]
    mb2 = [zsimp(mb[k] + bb * l[k]) for k in range(4)]
    return (l, n2, m2, mb2)


def boost_spin(tet, A=1, theta=0):
    """l -> A l, n -> n/A, m -> e^{i theta} m (the 2-dim isotropy of type D)."""
    l, nn, m, mb = tet
    ph = sp.exp(sp.I * theta)
    return ([zsimp(A * x) for x in l], [zsimp(x / A) for x in nn],
            [zsimp(ph * x) for x in m], [zsimp(sp.conjugate(ph) * x) for x in mb])


def psis(C, tet):
    return [zsimp(p) for p in weyl_scalars(C, tet)]


# --------------------------------------------------------------------------- canonical frame
def canonical_frame(geo, C=None, tet=None, verbose=False):
    """Align the tetrad with the principal null directions and normalize.

    Returns (tetrad, Psi, type, isotropy_dim, note). Three-valued: type may be UNKNOWN.
    The PND equation is SOLVED, not assumed: we null-rotate about n with parameter a and
    require Psi0(a) = 0 -- the quartic whose roots are the PNDs -- then rotate about l to
    kill Psi4. For type D this leaves only Psi2 (isotropy: boost+spin, dim 2). For type N,
    only Psi4, which a boost/spin normalizes to 1 (isotropy: dim 2, the null rotations
    fixing l -- the case whose tables carried literature errata, so we verify explicitly)."""
    C = weyl_tensor(geo) if C is None else C
    tet = null_tetrad(geo) if tet is None else tet
    P = psis(C, tet)
    ty = petrov_type(P)
    if ty == "O":
        return tet, P, "O", 6, "conformally flat: Weyl gives nothing; Ricci carries all of it"

    a = sp.Symbol("a_pnd")
    # --- align l with a PND: solve Psi0(a) = 0 after a null rotation about n
    if P[0] != 0:
        P0a = psis(C, null_rotation_about_n(tet, a))[0]
        roots = sp.solve(sp.Eq(sp.numer(sp.together(P0a)), 0), a, dict=True)
        if not roots:
            return tet, P, UNKNOWN, UNKNOWN, "PND quartic unsolvable symbolically"
        tet = null_rotation_about_n(tet, roots[0][a])
        P = psis(C, tet)
        if verbose:
            print(f"      null rotation about n, a = {roots[0][a]} -> Psi = {P}")

    # --- align n with the second PND: solve Psi4(b) = 0 via a null rotation about l
    b = sp.Symbol("b_pnd")
    if P[4] != 0:
        P4b = psis(C, null_rotation_about_l(tet, b))[4]
        roots = sp.solve(sp.Eq(sp.numer(sp.together(P4b)), 0), b, dict=True)
        if roots:
            cand = null_rotation_about_l(tet, roots[0][b])
            Pc = psis(C, cand)
            if Pc[0] == 0 or petrov_type(Pc) in ("D", "N"):
                tet, P = cand, Pc
                if verbose:
                    print(f"      null rotation about l, b = {roots[0][b]} -> Psi = {P}")

    ty = petrov_type(P)
    if ty == "D":
        # canonical: only Psi2. Remaining freedom: boost + spin (l,n scale oppositely,
        # m phase) -- Psi2 is invariant under both, so isotropy dim = 2.
        iso = 2
        note = "type D: only Psi2 survives; boost+spin leave it invariant (isotropy dim 2)"
    elif ty == "N":
        # Canonical form: normalize Psi4 -> 1 using the boost+spin. Psi4 has boost weight -2
        # and spin weight -2, so under (A, theta) it scales by A^-2 e^{-2 i theta}: choosing
        # A = |Psi4|^{1/2}, theta = arg(Psi4)/2 sends Psi4 -> 1. CONSEQUENCE (and this is the
        # standard type-N fact, not a shortcut): after normalization type N has NO order-0
        # Cartan invariants at all -- every distinction lives at order 1 and beyond. Two
        # pp-waves related by a rotation differ only by this spin, which is exactly why the
        # un-normalized frame would wrongly call them inequivalent.
        P4 = P[4]
        if P4 != 0:
            A = sp.sqrt(sp.Abs(P4))
            theta = sp.arg(P4) / 2
            cand = boost_spin(tet, A=A, theta=theta)
            Pc = psis(C, cand)
            if zsimp(Pc[4] - 1) == 0:
                tet, P = cand, Pc
                if verbose:
                    print(f"      type-N normalization: boost A={A}, spin={theta} -> Psi4 = 1")
            else:
                return tet, P, "N", UNKNOWN, (
                    f"type N: Psi4 normalization did not land on 1 (got {Pc[4]}) -- UNDECIDED")
        iso = 2
        note = ("type N: Psi4 normalized to 1; residual isotropy = null rotations about l "
                "(dim 2). No order-0 invariants survive -- all information is at order >= 1.")
    else:
        iso = UNKNOWN
        note = f"type {ty}: canonicalization beyond D/N not implemented in v0"
    return tet, P, ty, iso, note


# --------------------------------------------------------------------------- curvature derivatives
def covariant_derivative_weyl(geo, C=None):
    """nabla_e C_{abcd}, all indices down (index order: [e][a][b][c][d])."""
    C = weyl_tensor(geo) if C is None else C
    n, x, Gam = geo.n, geo.coords, geo.christoffel
    out = [[[[[None] * n for _ in range(n)] for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for e in range(n):
        for a in range(n):
            for b in range(n):
                for c in range(n):
                    for d in range(n):
                        t = sp.diff(C[a][b][c][d], x[e])
                        for f in range(n):
                            t -= (Gam[f][e][a] * C[f][b][c][d] + Gam[f][e][b] * C[a][f][c][d]
                                  + Gam[f][e][c] * C[a][b][f][d] + Gam[f][e][d] * C[a][b][c][f])
                        out[e][a][b][c][d] = sp.cancel(sp.together(t))
    return out


def frame_component5(DC, vs):
    """Contract nabla C with five tetrad vectors."""
    n = 4
    s = sp.S.Zero
    v0, v1, v2, v3, v4 = vs
    for e in range(n):
        if v0[e] == 0:
            continue
        for a in range(n):
            if v1[a] == 0:
                continue
            for b in range(n):
                if v2[b] == 0:
                    continue
                for c in range(n):
                    if v3[c] == 0:
                        continue
                    for d in range(n):
                        if v4[d] != 0:
                            s += DC[e][a][b][c][d] * v0[e] * v1[a] * v2[b] * v3[c] * v4[d]
    return zsimp(s)


def isotropy_invariants(comp, ty):
    """Combine boost/spin-COVARIANT frame components into genuine ISOTROPY INVARIANTS.

    This is the step the literature warns about (and where errata persisted to MacCallum
    2020): a single frame component of nabla C is NOT a Cartan invariant unless it is
    neutral under the isotropy group left over after canonicalization. Under the type-D
    residual isotropy (boost l->A l, n->A^-1 n; spin m->e^{i th} m, mb->e^{-i th} mb) the
    component D_l Psi2 has boost weight +1 and D_n Psi2 weight -1 -- only weight-cancelling
    products such as (D_l Psi2)(D_n Psi2) are invariant. Bonus: the products are rational
    where the individual components carry sqrt(f), so elimination becomes polynomial.

    Weight bookkeeping (boost b, spin s) for a derivative direction applied to Psi2 (which is
    itself neutral): l -> (+1, 0), n -> (-1, 0), m -> (0, +1), mb -> (0, -1)."""
    W = {"l": (1, 0), "n": (-1, 0), "m": (0, 1), "mb": (0, -1)}
    inv = {}
    if ty == "D":
        for a, b in (("l", "n"), ("m", "mb")):
            ka, kb = f"D_{a}_Psi2", f"D_{b}_Psi2"
            if ka in comp and kb in comp:
                inv[f"({ka})({kb})"] = zsimp(comp[ka] * comp[kb])
            elif ka in comp or kb in comp:
                # one of a weight-conjugate pair nonzero: the PRODUCT is zero, and that
                # (a vanishing invariant with a nonvanishing covariant piece) is itself
                # invariant information -- record it explicitly rather than dropping it.
                inv[f"({ka})({kb})"] = sp.S.Zero
        # squared magnitudes are also neutral (|D_m Psi2|^2 etc.) when m-derivatives exist
        if "D_m_Psi2" in comp and "D_mb_Psi2" not in comp:
            inv["|D_m_Psi2|^2"] = zsimp(comp["D_m_Psi2"] * sp.conjugate(comp["D_m_Psi2"]))
    elif ty == "N":
        # Psi4 is boost-covariant (weight -2) and normalized to 1 by the boost; the residual
        # isotropy is the 2-parameter null-rotation group about l. Ratios of like-weight
        # components are then the invariant data. v0: report the ratios we can form.
        base = comp.get("D_l_Psi4")
        for k, v in comp.items():
            if k == "D_l_Psi4" or v == 0:
                continue
            inv[f"{k}/D_l_Psi4"] = zsimp(v / base) if base not in (None, 0) else UNDECIDED
        if base not in (None, 0):
            inv["D_l_Psi4"] = base
    else:
        for k, v in comp.items():
            inv[k] = v
    return {k: v for k, v in inv.items() if v is not UNDECIDED}


def cartan_order1(geo, tet, C=None, DC=None, which=None):
    """Order-1 frame components of nabla C in the canonical frame (boost/spin COVARIANT --
    pass through isotropy_invariants() before comparing). Returns the NONZERO ones."""
    C = weyl_tensor(geo) if C is None else C
    DC = covariant_derivative_weyl(geo, C) if DC is None else DC
    l, nn, m, mb = tet
    names = {"l": l, "n": nn, "m": m, "mb": mb}
    # the components that matter for D/N: derivatives of the surviving Psi's along the frame
    combos = which or [
        ("D_l_Psi2", ("l", "l", "m", "mb", "n")), ("D_n_Psi2", ("n", "l", "m", "mb", "n")),
        ("D_m_Psi2", ("m", "l", "m", "mb", "n")), ("D_mb_Psi2", ("mb", "l", "m", "mb", "n")),
        ("D_l_Psi4", ("l", "n", "mb", "n", "mb")), ("D_n_Psi4", ("n", "n", "mb", "n", "mb")),
        ("D_m_Psi4", ("m", "n", "mb", "n", "mb")), ("D_mb_Psi4", ("mb", "n", "mb", "n", "mb")),
        ("D_l_Psi0", ("l", "l", "m", "l", "m")), ("D_n_Psi0", ("n", "l", "m", "l", "m")),
    ]
    out = {}
    for lab, ks in combos:
        val = frame_component5(DC, [names[k] for k in ks])
        if val != 0:
            out[lab] = val
    return out


# --------------------------------------------------------------------------- functional relations
def functional_rank(exprs, coords):
    """Number of functionally independent functions among `exprs` = rank of the Jacobian.
    Returns (rank, UNDECIDED-flag). Symbolic rank is exactly where SymPy is weakest, so the
    flag is honest: if we cannot decide the rank, we say so rather than guessing."""
    exprs = [e for e in exprs if e != 0]
    if not exprs:
        return 0, False
    Jm = sp.Matrix([[sp.simplify(sp.diff(e, c)) for c in coords] for e in exprs])
    try:
        r = Jm.rank(simplify=True)
        return int(r), False
    except Exception:
        return UNDECIDED, True


def relation_certificate_resultant(inv0, inv1, coords):
    """The coordinate-free certificate WITHOUT inverting anything.

    For each order-1 invariant z = I1(x) and the order-0 invariant w = I0(x), eliminate the
    coordinate x by RESULTANT: Res_x(numer(w - I0), numer(z - I1)) = 0 is an implicit
    algebraic relation F(w, z) = 0 that holds on the manifold and is chart-independent.
    Robust where explicit inversion dies (the isotropic chart's order-0 invariant is a
    degree-6 rational in rho -- solve() gives up, the resultant does not)."""
    w, z = sp.symbols("w z")
    base = [e for e in inv0 if e != 0]
    if not base:
        return None, ["no nonzero order-0 invariant to parametrize by"]
    I0 = base[0]
    var = next((c for c in coords if sp.diff(I0, c) != 0), None)
    if var is None:
        return {"I0_constant": sp.simplify(I0)}, []
    p1 = sp.numer(sp.together(w - I0))
    cert, fails = {}, []
    for lab in sorted(inv1):
        e = inv1[lab]
        try:
            if e == 0:
                cert[lab] = sp.S.Zero
                continue
            p2 = sp.numer(sp.together(z - e))
            res = sp.resultant(sp.Poly(p1, var), sp.Poly(p2, var), var)
            res = sp.factor(sp.simplify(res))
            # drop factors free of z (they come from cleared denominators, not the relation)
            fl = sp.factor_list(res)
            # SQUAREFREE (radical) part: drop multiplicities. A chart that covers the
            # geometry k-to-1 (isotropic coordinates double-cover the exterior via
            # rho <-> M^2/4rho) returns the same relation raised to the k-th power --
            # same geometry, so the canonical certificate is the radical, not the power.
            keep = [f for f, _k in fl[1] if f.has(z)]
            if not keep:
                fails.append(f"{lab}: resultant carried no z-dependence")
                continue
            rel = sp.factor(sp.Mul(*keep))
            # canonical normalization so two charts give literally comparable polynomials
            pz = sp.Poly(sp.expand(rel), z)
            rel = sp.factor(sp.expand(pz.monic().as_expr()))
            cert[lab] = sp.simplify(rel)
        except Exception as exc:
            fails.append(f"{lab}: resultant failed ({type(exc).__name__}: {exc})")
    return cert, fails


def relation_certificate(inv0, inv1, coords):
    """The coordinate-free certificate: express each order-1 invariant as a function of the
    order-0 invariants by ELIMINATING the coordinates. This is the step that decides
    EQUIVALENT vs UNDECIDED -- and the step most likely to fail, so it reports honestly.

    Strategy: pick a functionally independent order-0 invariant w = I0(x); solve for the
    coordinate it depends on; substitute into each order-1 invariant. The resulting
    expressions in w are chart-independent and directly comparable between metrics."""
    w = sp.Symbol("w", real=True)      # NOT positive: Psi2 = -M/r^3 < 0 for a black hole
    cert, failures = {}, []
    base = [e for e in inv0 if e != 0]
    if not base:
        return None, ["no nonzero order-0 invariant to parametrize by"]
    I0 = base[0]
    var = None
    for c in coords:
        if sp.diff(I0, c) != 0:
            var = c
            break
    if var is None:
        return {"constant_I0": sp.simplify(I0)}, []
    try:
        sols = sp.solve(sp.Eq(I0, w), var, dict=True)
    except Exception as exc:                                   # pragma: no cover
        return None, [f"solve failed: {exc}"]
    if not sols:
        return None, [f"could not invert the order-0 invariant for {var}"]
    # Pick the branch by VERIFYING it inverts correctly at a probe point inside the domain:
    # evaluate w0 = I0(x0), then keep the root that maps w0 back to x0. sols[0] is often a
    # complex cube root -- taking it blindly would silently corrupt every comparison.
    cands = [sp.simplify(s[var]) for s in sols]
    chosen, probe_note = None, None
    for sub_pt in domain_samples(I0.free_symbols | {var}):
        try:
            x0 = sp.N(sub_pt.get(var, 2))
            rest = {k: v for k, v in sub_pt.items() if k != var}
            w0 = sp.N(I0.subs(rest).subs(var, x0))
            if not w0.is_real:
                continue
            for cand in cands:
                back = sp.N(cand.subs(rest).subs(w, w0))
                if back.is_real and abs(complex(back).real - float(x0)) < 1e-8:
                    chosen = cand
                    probe_note = f"branch verified at {var}={x0}"
                    break
        except Exception:
            continue
        if chosen is not None:
            break
    if chosen is None:
        reals = [v for v in cands if not v.has(sp.I)]
        if not reals:
            return None, [f"no real inverse branch for {var}"]
        chosen, probe_note = reals[0], "branch UNVERIFIED (fell back to first real root)"
    sub = chosen
    if probe_note and probe_note.startswith("branch UNVERIFIED"):
        failures.append(probe_note)
    others = [c for c in coords if c != var]
    for lab, e in sorted(inv1.items()):
        try:
            val = sp.simplify(sp.powsimp(sp.simplify(e.subs(var, sub)), force=True))
            val = sp.radsimp(sp.simplify(sp.powdenest(val, force=True)))
            if others and val.has(*others):
                failures.append(f"{lab}: residual coordinate dependence after elimination")
            else:
                cert[lab] = sp.simplify(val)
        except Exception as exc:                               # pragma: no cover
            failures.append(f"{lab}: {exc}")
    return cert, failures


# --------------------------------------------------------------------------- the top-level call
def ck_signature(geo, label="", verbose=False, tet=None):
    """The full order-0 + order-1 Cartan signature of a spacetime, chart-independent.

    `tet` optionally seeds the starting null tetrad. Canonicalization makes the seed
    irrelevant to the RESULT, but some geometries have no timelike coordinate direction to
    Gram-Schmidt from -- pp-waves are the standard case (d_v is null, g_uu = H changes sign),
    so the caller supplies the natural null frame and CK proceeds from there."""
    C = weyl_tensor(geo)
    tet = null_tetrad(geo) if tet is None else tet
    bad = check_tetrad(geo, tet)
    if bad:
        return {"label": label, "error": f"tetrad normalization failed: {bad}"}
    tet, P, ty, iso, note = canonical_frame(geo, C, tet, verbose=verbose)
    Rs = zsimp(geo.ricci_scalar)
    inv0 = [p for p in P if p != 0] + ([Rs] if Rs != 0 else [])
    t0, und0 = functional_rank(inv0, geo.coords)
    # Whether nabla C vanishes identically is a TENSORIAL (frame-independent) fact, so it is a
    # rigorous discriminator even for type N, where we cannot yet reduce individual order-1
    # components modulo the residual null rotations. nabla C = 0 also means order 1 adds
    # nothing, so the CK recursion terminates there.
    DC = covariant_derivative_weyl(geo, C)
    dc_zero = all(zsimp(DC[e][a][b][c][d]) == 0
                  for e in range(4) for a in range(4) for b in range(4)
                  for c in range(4) for d in range(4))
    comp1 = cartan_order1(geo, tet, C, DC)                # boost/spin COVARIANT components
    inv1 = isotropy_invariants(comp1, ty)                 # -> genuine isotropy invariants
    t1, und1 = functional_rank(inv0 + [v for v in inv1.values() if v != 0], geo.coords)
    cert, fails = relation_certificate_resultant(inv0, inv1, geo.coords)
    return {"label": label, "petrov": ty, "isotropy_dim": iso, "note": note,
            "psi": P, "ricci_scalar": Rs, "order0": inv0, "t0": t0,
            "order1_components": sorted(comp1), "order1_invariants": inv1,
            "order1_labels": sorted(inv1), "t1": t1, "nabla_C_zero": dc_zero,
            "certificate": cert, "cert_failures": fails, "undecided": und0 or und1}


def equivalent(sig1, sig2):
    """Three-valued comparison of two CK signatures."""
    reasons = []
    if "error" in sig1 or "error" in sig2:
        return UNDECIDED, [sig1.get("error"), sig2.get("error")]
    if sig1["petrov"] != sig2["petrov"]:
        return INEQUIVALENT, [f"Petrov type {sig1['petrov']} vs {sig2['petrov']}"]
    if sig1["isotropy_dim"] != sig2["isotropy_dim"]:
        return INEQUIVALENT, [f"isotropy dim {sig1['isotropy_dim']} vs {sig2['isotropy_dim']}"]
    z1, z2 = sig1["ricci_scalar"] == 0, sig2["ricci_scalar"] == 0
    if z1 != z2:
        return INEQUIVALENT, [f"Ricci scalar {sig1['ricci_scalar']} vs {sig2['ricci_scalar']}"]
    if not z1 and not z2 and sp.simplify(sig1["ricci_scalar"] - sig2["ricci_scalar"]) != 0:
        return INEQUIVALENT, [f"Ricci scalar {sig1['ricci_scalar']} vs {sig2['ricci_scalar']}"]
    if sig1["t0"] != sig2["t0"] or sig1["t1"] != sig2["t1"]:
        return INEQUIVALENT, [f"invariant counts (t0,t1) "
                              f"({sig1['t0']},{sig1['t1']}) vs ({sig2['t0']},{sig2['t1']})"]
    # Type N: after Psi4 -> 1 there are no order-0 invariants, and the residual isotropy is the
    # 2-parameter null-rotation group about l. Differing (t0,t1) counts are still a RIGOROUS
    # discriminator (the counts are invariants) and were already checked above. Beyond that,
    # v0 has not established the null-rotation-invariant combinations at order 1 -- the case
    # whose tables carried errata to MacCallum (2020) -- so we say UNDECIDED instead of
    # guessing. That is the honest boundary of this version, not a failure of the method.
    if sig1["petrov"] == "N":
        d1, d2 = sig1.get("nabla_C_zero"), sig2.get("nabla_C_zero")
        if d1 != d2:
            return INEQUIVALENT, [
                f"nabla C vanishes identically for one and not the other "
                f"({sig1['label']}: {d1}, {sig2['label']}: {d2}). This is a TENSORIAL "
                f"statement -- true in every frame -- so it decides the pair rigorously "
                f"even though every polynomial invariant vanishes for both."]
        if d1 and d2:
            # Both have nabla C = 0: order 1 adds no new invariant and cannot shrink the
            # isotropy, so the CK recursion TERMINATES at order 1. With matching Petrov type,
            # matching normalized Psi, matching (t0,t1) and matching isotropy dimension (all
            # checked above), the Cartan data agree at the terminating order.
            return EQUIVALENT, [
                "nabla C = 0 for both: the CK recursion terminates at order 1, and the "
                "order-0 data agree (type N, Psi4 normalized to 1, t0 = t1 = 0, isotropy 2).",
                "This is the covariantly-constant-curvature (symmetric plane-wave) case."]
        i1, i2 = sig1.get("order1_invariants", {}), sig2.get("order1_invariants", {})
        same = set(i1) == set(i2) and all(sp.simplify(i1[k] - i2[k]) == 0 for k in i1)
        if same and i1:
            return EQUIVALENT, [f"type N: order-1 invariants match: {sorted(i1)}"]
        return UNDECIDED, ["type N with nabla C != 0 for both: v0 has not reduced the order-1 "
                           "components modulo the residual null rotations about l (the case "
                           "whose isotropy tables carried errata to MacCallum 2020), so a real "
                           "difference cannot be separated from a frame artifact. Needs order 2."]

    c1, c2 = sig1["certificate"], sig2["certificate"]
    if c1 is None or c2 is None or sig1["cert_failures"] or sig2["cert_failures"]:
        return UNDECIDED, ["certificate incomplete: "
                           + "; ".join(sig1["cert_failures"] + sig2["cert_failures"])]
    if set(c1) != set(c2):
        return INEQUIVALENT, [f"different surviving order-1 components: "
                              f"{sorted(set(c1) ^ set(c2))}"]
    for k in sorted(c1):
        d = sp.simplify(c1[k] - c2[k])
        if d != 0:
            # allow the sign/phase freedom left in the canonical frame
            if sp.simplify(c1[k] + c2[k]) == 0:
                continue
            return INEQUIVALENT, [f"certificate mismatch on {k}: {c1[k]} vs {c2[k]}"]
        reasons.append(f"{k} matches: {c1[k]}")
    return EQUIVALENT, reasons
