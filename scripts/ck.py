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

from analyzer import (UNKNOWN, petrov_type, weyl_invariants, weyl_scalars,
                      weyl_tensor)

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


def _predicate_to_relational(p):
    """Q.positive(e) -> e > 0 etc., so a domain condition can actually be TESTED at a point.
    SymPy assumption predicates do NOT evaluate under .subs -- Q.positive(1-y**2).subs(y,3)
    stays symbolic rather than becoming false -- so sampling against them naively accepts
    out-of-domain points and can return a confidently WRONG sign."""
    out = []
    for q in (p.args if isinstance(p, sp.And) else [p]):
        if isinstance(q, sp.core.relational.Relational):
            out.append(q)
            continue
        fn = getattr(q, "function", None)
        args = getattr(q, "arguments", None) or getattr(q, "args", None)
        if fn is None or not args:
            continue
        arg = args[0]
        name = str(fn).lower()
        rel = None
        if "positive" in name:
            rel = arg > 0
        elif "negative" in name:
            rel = arg < 0
        elif "nonzero" in name:
            rel = sp.Ne(arg, 0)
        # a condition on an already-declared symbol (Q.positive(r) with r positive) collapses
        # to BooleanTrue, which carries no rel_op -- keep only genuine relations.
        if isinstance(rel, sp.core.relational.Relational):
            out.append(rel)
    return out


def domain_free_symbols():
    d = domain()
    return set().union(*[c.free_symbols for c in _predicate_to_relational(d)]) if d is not None else set()


def domain_samples(free, tries=400):
    """Numeric points that GENUINELY satisfy the declared domain -- used only to DECIDE A
    BRANCH, never to prove anything: every branch choice is verified downstream by
    check_tetrad. Each condition is converted to a relational and evaluated numerically."""
    import random
    conds = _predicate_to_relational(domain()) if domain() is not None else []
    grid = [sp.Rational(1, 5), sp.Rational(1, 2), sp.Rational(3, 4), sp.Rational(6, 5),
            sp.Rational(3, 2), 2, 3, 5, 7, 11]
    free = sorted(free, key=str)
    out, rnd = [], random.Random(20260721)
    for _ in range(tries):
        sub = {s: rnd.choice(grid) for s in free}
        good = True
        for c in conds:
            try:
                gap = (c.lhs - c.rhs).subs(sub)
                if gap.free_symbols:            # mentions symbols we are not probing: skip
                    continue
                gap = sp.N(gap)                 # numeric: compare directly, never via bool(Boolean)
                if c.rel_op in (">", ">=") and not gap > 0:
                    good = False
                elif c.rel_op in ("<", "<=") and not gap < 0:
                    good = False
                elif c.rel_op in ("!=", "ne") and gap == 0:
                    good = False
            except Exception:
                good = False
            if not good:
                break
        if not good:
            continue
        out.append(sub)
        if len(out) >= 8:
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
    # (1b) DIRECT MATCH against a declared condition. SymPy's assumption engine will not
    # connect "Lambda*r**2/3 + 2*M/r - 1" to a declared positive "1 - 2*M/r - Lambda*r**2/3",
    # though they are exact negatives -- so check for that explicitly. This is what lets a
    # two-horizon spacetime (Schwarzschild-de Sitter) be handled by naming its static region.
    if d is not None:
        for c in _predicate_to_relational(d):
            if c.rel_op not in (">", ">="):
                continue
            q = sp.simplify(c.lhs - c.rhs)          # q > 0 was declared
            if q == 0:
                continue
            if zsimp(e - q) == 0:
                return 1
            if zsimp(e + q) == 0:
                return -1
            ratio = sp.simplify(sp.cancel(e / q))   # e = (positive const) * q  =>  same sign
            if ratio.is_number:
                if ratio.is_positive:
                    return 1
                if ratio.is_negative:
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
    # (3) numeric probe inside the domain (branch selection only; verified downstream).
    # Probe the domain's symbols too, or its conditions cannot be tested at the sample point.
    samples = domain_samples(e.free_symbols | domain_free_symbols())
    if not samples:
        return None
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
    elif ty == "I":
        # THE GENERIC CASE. Four distinct PNDs; l and n are already aligned with two of them
        # above, so Psi0 = Psi4 = 0. (Psi0 survives the second rotation: a null rotation about
        # l sends m -> m + b l, and Psi0 = C(l,m,l,m) picks up only terms with C(l,l,...) = 0.)
        # The residual boost+spin is fixed by demanding Psi1 = Psi3: under (A, theta),
        # Psi1 -> A e^{i th} Psi1 (weight +1,+1) and Psi3 -> A^-1 e^{-i th} Psi3 (weight -1,-1),
        # so A^2 e^{2 i th} = Psi3/Psi1 does it. Isotropy is then DISCRETE (dim 0), which is what
        # makes type I the easy case for comparison: every canonical component is an invariant.
        if P[1] != 0 and P[3] != 0:
            ratio = zsimp(P[3] / P[1])
            A = sp.sqrt(sp.Abs(ratio))
            theta = sp.arg(ratio) / 2
            cand = boost_spin(tet, A=A, theta=theta)
            Pc = psis(C, cand)
            if zsimp(Pc[1] - Pc[3]) == 0:
                tet, P = cand, Pc
                if verbose:
                    print(f"      type-I normalization: boost A={A}, spin={theta} -> Psi1 = Psi3")
            else:
                return tet, P, "I", UNKNOWN, (
                    "type I: Psi1 = Psi3 normalization did not close -- UNDECIDED")
        elif P[1] == 0 and P[3] == 0:
            note = ("type I with Psi1 = Psi3 = 0 already (an extra reflection symmetry); "
                    "boost+spin still free up to the Psi2 phase")
            return tet, P, "I", 0, note
        iso = 0
        note = ("type I: Psi0 = Psi4 = 0, Psi1 = Psi3; isotropy is discrete (dim 0), so every "
                "canonical frame component is itself a Cartan invariant")
    else:
        iso = UNKNOWN
        note = f"type {ty}: canonicalization for types II/III not implemented in v0"
    return tet, P, ty, iso, note


# --------------------------------------------------------------------------- Ricci / Segre
def ricci_invariants(geo):
    """Frame-INDEPENDENT invariants of the mixed Ricci tensor R^a_b: the traces of its powers.

    The Ricci SCALAR alone is blind to traceless matter -- Reissner-Nordstrom has R = 0, and so
    does a radiation-filled universe, so a Weyl-plus-R comparison cannot tell flat spacetime from
    a radiation cosmology (their CK signatures come out identical). tr(R^k) for k = 1..4 fixes the
    characteristic polynomial of R^a_b, hence its eigenvalue structure, and every one of them is a
    genuine order-0 Cartan invariant needing no frame fixing at all."""
    n, g = geo.n, geo.g
    Rm = sp.simplify(g.inv() * geo.ricci)              # R^a_b (mixed)
    out, P = [], sp.eye(n)
    for _k in range(1, 5):
        P = sp.simplify(P * Rm)
        out.append(zsimp(P.trace()))
    return out, Rm


def segre_type(geo, Rm=None):
    """Matter classification from the EIGENVALUE STRUCTURE of R^a_b (the Segre type).

    Eigenvalue structure first, tracelessness second -- getting that order wrong mislabels a
    radiation fluid (p = rho/3, which is traceless) as an electrovac. Three-valued: UNKNOWN when
    the eigenvalues cannot be decided symbolically.

        R_ab = 0                          vacuum
        R_ab = Lambda g_ab                Einstein space
        all eigenvalues 0 but R_ab != 0   null radiation: R^a_b is NILPOTENT (Segre [(11,2)])
        multiplicities [3,1]              perfect fluid, Segre [1,(111)] (rho, p, p, p)
        multiplicities [2,2]              non-null electromagnetic, Segre [(11)(1,1)]
    """
    n = geo.n
    Rm = sp.simplify(geo.g.inv() * geo.ricci) if Rm is None else Rm
    if all(zsimp(Rm[i, j]) == 0 for i in range(n) for j in range(n)):
        return "vacuum (R_ab = 0)"
    Rs = zsimp(geo.ricci_scalar)
    lam = sp.Rational(1, 4) * Rs
    if all(zsimp(Rm[i, j] - (lam if i == j else 0)) == 0 for i in range(n) for j in range(n)):
        return "Einstein space (R_ab = Lambda g_ab)"
    traceless = (Rs == 0)
    try:
        ev = Rm.eigenvals()
        ev = {zsimp(k): v for k, v in ev.items()}
        mult = sorted(ev.values(), reverse=True)
        if set(ev) == {sp.S.Zero}:
            # every eigenvalue zero yet R_ab != 0: nilpotent => aligned null vector
            return "null radiation / pure radiation (R^a_b nilpotent, Segre [(11,2)])"
        if mult == [3, 1]:
            return ("perfect fluid, radiation (Segre [1,(111)], traceless: p = rho/3)"
                    if traceless else "perfect fluid (Segre [1,(111)]: rho, p, p, p)")
        if mult == [2, 2]:
            return ("non-null electromagnetic (Segre [(11)(1,1)], traceless)" if traceless
                    else "two double eigenvalues (Segre [(11)(1,1)], not traceless)")
        if mult == [4]:
            return "Einstein space (degenerate)"
        return (f"anisotropic matter (eigenvalue multiplicities {mult}"
                + (", traceless)" if traceless else ")"))
    except Exception:
        return UNKNOWN


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
    elif ty == "I":
        # Isotropy is discrete: every canonical component is already an invariant.
        inv = dict(comp)
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


def invariant_ratios(invs, tag="I", max_items=4):
    """Dimensionless RATIOS of a set of Cartan invariants -- pure numbers, hence chart-free.

    When a set of invariants all scale the same way with the coordinate (Kasner: every canonical
    Psi goes like T^-14, every order-1 component like T^-15) their mutual ratios are pure NUMBERS
    -- genuine chart-free labels. Cheap and rigorous, and it is what makes type I tractable:
    with isotropy dim 0 every order-1 component is an invariant, and eliminating the coordinate
    from those by resultant (T^24 powers, nested radicals like sqrt(4 sqrt(5)+9)) does not
    finish, while the ratios drop out in milliseconds."""
    # Cap the number of invariants compared: each ratio costs a simplify/radsimp over
    # radical-laden expressions, and the cheapest few already label the geometry.
    base = sorted([e for e in invs if e != 0], key=sp.count_ops)[:max_items]
    out = {}
    for i in range(len(base)):
        for j in range(i + 1, len(base)):
            rat = sp.radsimp(sp.simplify(sp.cancel(base[j] / base[i])))
            if not rat.free_symbols:                    # a pure number: a chart-free label
                out[f"{tag}{j}/{tag}{i}"] = sp.nsimplify(rat)
    return out


def order0_ratios(inv0):
    return invariant_ratios(inv0, "I")


def relation_certificate_resultant(inv0, inv1, coords, max_terms=3):
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
    # Resultants over messy invariants are the expensive step; take the simplest few and SAY SO
    # (a silent cap would read as "we covered everything" when we did not).
    ranked = sorted(inv1, key=lambda k: sp.count_ops(inv1[k]))
    chosen, dropped = ranked[:max_terms], ranked[max_terms:]
    if dropped:
        fails.append(f"certificate limited to the {max_terms} simplest order-1 invariants; "
                     f"not eliminated: {dropped}")
    for lab in chosen:
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
    # The Ricci sector: frame-independent trace invariants + the Segre/matter type. Appended
    # AFTER the Weyl invariants so the certificate keeps parametrizing by Psi where it did before.
    ric_tr, Rmix = ricci_invariants(geo)
    segre = segre_type(geo, Rmix)
    inv0 = ([p for p in P if p != 0] + ([Rs] if Rs != 0 else [])
            + [e for e in ric_tr[1:] if e != 0])
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
    ratios = order0_ratios(inv0)
    ratios1 = invariant_ratios([v for v in inv1.values() if v != 0], "J")
    # THE DISCRETE PND FREEDOM. Type I has four distinct principal null directions and the
    # quartic solver returns them in an arbitrary order, so "align l with roots[0]" is a
    # CHOICE: relabelling the axes of a Kasner permutes the PNDs and lands on a different --
    # equally valid -- canonical frame, with different frame components. The frame-independent
    # Weyl invariants I and J are symmetric under that relabelling by construction, so the
    # dimensionless I^3/J^2 is a label immune to it (and I^3 = 27 J^2 is exactly the
    # algebraically-special condition, so it also encodes the type).
    Ivl, Jvl = weyl_invariants(P)
    speciality = UNDECIDED
    try:
        if zsimp(Jvl) != 0:
            cand = sp.radsimp(sp.simplify(sp.cancel(Ivl**3 / Jvl**2)))
            speciality = sp.nsimplify(cand) if not cand.free_symbols else sp.simplify(cand)
    except Exception:
        speciality = UNDECIDED
    # Type I: isotropy dim 0 makes every order-1 component an invariant, and eliminating the
    # coordinate from those by resultant does not terminate in practice. The dimensionless
    # ratios above are chart-free and decide such pairs, so we skip the elimination there and
    # SAY we skipped it rather than reporting a silently partial certificate.
    if ty == "I":
        cert, fails = {}, ["order-1 coordinate elimination skipped for type I (resultants over "
                           "radical-laden components do not terminate); decided on the "
                           "dimensionless order-0/order-1 invariant ratios instead"]
    else:
        cert, fails = relation_certificate_resultant(inv0, inv1, geo.coords, max_terms=3)
    return {"label": label, "petrov": ty, "isotropy_dim": iso, "note": note,
            "psi": P, "ricci_scalar": Rs, "order0": inv0, "t0": t0, "order0_ratios": ratios,
            "ricci_traces": ric_tr, "segre": segre,
            "order1_ratios": ratios1, "weyl_I": Ivl, "weyl_J": Jvl,
            "speciality_I3_over_J2": speciality,
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
    # --- the Ricci sector (frame-free, so it decides without any frame fixing at all)
    if sig1.get("segre") != sig2.get("segre"):
        return INEQUIVALENT, [f"matter type differs: {sig1.get('segre')} vs {sig2.get('segre')}"]
    tr1, tr2 = sig1.get("ricci_traces") or [], sig2.get("ricci_traces") or []
    if len(tr1) == len(tr2):
        for k, (a, b) in enumerate(zip(tr1, tr2), start=1):
            if (a == 0) != (b == 0):
                return INEQUIVALENT, [f"Ricci invariant tr(R^{k}) vanishes for one and not the "
                                      f"other: {a} vs {b}"]
    z1, z2 = sig1["ricci_scalar"] == 0, sig2["ricci_scalar"] == 0
    if z1 != z2:
        return INEQUIVALENT, [f"Ricci scalar {sig1['ricci_scalar']} vs {sig2['ricci_scalar']}"]
    if not z1 and not z2 and sp.simplify(sig1["ricci_scalar"] - sig2["ricci_scalar"]) != 0:
        return INEQUIVALENT, [f"Ricci scalar {sig1['ricci_scalar']} vs {sig2['ricci_scalar']}"]
    if sig1["t0"] != sig2["t0"] or sig1["t1"] != sig2["t1"]:
        return INEQUIVALENT, [f"invariant counts (t0,t1) "
                              f"({sig1['t0']},{sig1['t1']}) vs ({sig2['t0']},{sig2['t1']})"]
    # Dimensionless ratios of the invariants: pure numbers, hence chart-free labels. Differing
    # ratios are a rigorous INEQUIVALENT (invariants disagree); matching ones are necessary.
    matched_ratios = []
    # For type I the frame-component ratios depend on WHICH of the four PNDs was aligned first,
    # so they are not comparable across presentations; use the relabelling-immune I^3/J^2.
    ratio_keys = () if sig1["petrov"] == "I" else ("order0_ratios", "order1_ratios")
    if sig1["petrov"] == "I":
        a, b = sig1.get("speciality_I3_over_J2"), sig2.get("speciality_I3_over_J2")
        if a is UNDECIDED or b is UNDECIDED or a is None or b is None:
            return UNDECIDED, ["type I: could not form the relabelling-immune invariant I^3/J^2"]
        if sp.simplify(sp.radsimp(a - b)) != 0:
            return INEQUIVALENT, [f"Weyl speciality invariant I^3/J^2 differs: {a} vs {b}"]
        matched_ratios.append(f"I^3/J^2 = {a} (immune to PND relabelling)")
    for key in ratio_keys:
        r1, r2 = sig1.get(key, {}), sig2.get(key, {})
        if set(r1) != set(r2):
            return INEQUIVALENT, [f"{key}: different sets of dimensionless invariants "
                                  f"{sorted(set(r1) ^ set(r2))}"]
        bad = [k for k in r1 if sp.simplify(sp.radsimp(r1[k] - r2[k])) != 0]
        if bad:
            return INEQUIVALENT, [f"{key} {k} differs: {r1[k]} vs {r2[k]}" for k in bad]
        matched_ratios.extend(f"{key}:{k}={r1[k]}" for k in sorted(r1))

    if sig1["petrov"] == "I":
        # Isotropy is already trivial (dim 0) at order 0, and t1 == t0 (checked above) means
        # order 1 produced no new functional dependence -- so the CK recursion TERMINATES at
        # order 1. With the type, the isotropy dimension, the invariant counts and all
        # dimensionless invariant ratios agreeing at the terminating order, the Cartan data match.
        if sig1["t0"] == sig1["t1"] and matched_ratios:
            return EQUIVALENT, ["type I: isotropy already discrete and t1 = t0, so CK terminates "
                                "at order 1; all dimensionless invariant ratios agree.",
                                *matched_ratios[:4]]
        return UNDECIDED, ["type I: the recursion has not demonstrably terminated (t1 != t0) and "
                           "the order-1 elimination was skipped -- needs order 2."]
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
