"""The algebraic finisher (D14), shared by every hunt loop.

GP finds the leading structure; algebra solves the family. Given a
near-miss candidate (one expression per metric-function slot), symbolize
every numeric constant, ENRICH each slot with sub-leading falloff terms
k·r^p the GP rarely composes, substitute the family into the symbolic
field-equation residuals, demand each vanish identically in r
(polynomial coefficients = 0), and let sp.solve deliver exact constants.

Free symbols in a solution branch are FAMILY PARAMETERS (mass, spin) —
instantiate them generically (original value or ±1), never zero, or the
branch collapses to its trivial member (measured: the rotating-BTZ branch
kept collapsing to constant-ω frame gauge until this rule).

Also home to the numeric-leaf surgery shared with 05_generalize
(positional, because sympy .subs is value-based and would hit exponents).
"""

import sympy as sp

from gr_engine import R_SYM


def numeric_slots(expr):
    """Paths to numeric leaves, excluding Pow exponents."""
    slots = []

    def walk(e, path):
        if e.is_Number:
            slots.append(path)
            return
        if e.is_Pow and e.exp.is_Number:
            walk(e.base, path + (0,))
            return
        for i, a in enumerate(e.args):
            walk(a, path + (i,))

    walk(expr, ())
    return slots


def replace_slots(expr, paths, syms):
    mapping = dict(zip(paths, syms))

    def rebuild(e, path):
        if path in mapping:
            return mapping[path]
        if not e.args:
            return e
        if e.is_Pow and e.exp.is_Number:
            return e.func(rebuild(e.base, path + (0,)), e.exp)
        return e.func(*[rebuild(a, path + (i,))
                        for i, a in enumerate(e.args)])

    return rebuild(expr, ())


def slot_values(expr, paths):
    out = []
    for p in paths:
        v = expr
        for j in p:
            v = v.args[j]
        out.append(v)
    return out


def structure_sig(exprs):
    """Constant-blind signature: one snap attempt per structure."""
    k0 = sp.Symbol("k0")
    return "|".join(sp.srepr(replace_slots(e, numeric_slots(e),
                                           [k0] * len(numeric_slots(e))))
                    for e in exprs)


def _laurent_coeffs(e):
    """{power: coeff} if e is a finite Laurent polynomial in r, else None."""
    ex = sp.expand(sp.cancel(sp.together(e)))
    out = {}
    for term in sp.Add.make_args(ex):
        c, rpart = term.as_independent(R_SYM)
        if rpart == 1:
            p = 0
        elif rpart == R_SYM:
            p = 1
        elif rpart.is_Pow and rpart.base == R_SYM \
                and rpart.exp.is_Integer:
            p = int(rpart.exp)
        else:
            return None
        if not c.is_Number:
            return None
        out[p] = out.get(p, sp.S.Zero) + c
    return out


def snap_constants(exprs, sym_res, fn_objs, enrich_powers=(-2, -1),
                   max_consts=12, max_sols=8):
    """Solve a near-miss structure's constants exactly.

    exprs    — one sympy expression per metric-function slot
    sym_res  — field-equation residuals, symbolic in the fn_objs
    fn_objs  — the sympy Function instances (e.g. F(r), H(r), W(r))
               in slot order
    Returns a list of exact per-slot expression tuples (possibly empty).

    CANONICALIZATION (bought by a measured failure): symbolizing raw
    tree constants creates redundant parametrizations — k1·(k2·r + ...)
    has a scaling gauge in constant-space, the solution variety goes
    positive-dimensional, and sp.solve returns [] instead of parametric
    families. So Laurent-polynomial candidates are first rewritten as
    Σ k_p·r^p with ONE unknown per power (no redundancy, well-posed);
    tree-slot symbolization remains as the fallback for structures with
    genuine poles like 1/(r+c)."""
    syms, fams, originals = [], [], {}
    laurent = [_laurent_coeffs(e) for e in exprs]
    if all(lc is not None for lc in laurent):
        for lc in laurent:
            powers = sorted(set(lc) | set(enrich_powers))
            fam = sp.S.Zero
            for p in powers:
                s = sp.Symbol(f"k{len(syms) + 1}", real=True)
                originals[s] = lc.get(p, sp.S.Zero)
                syms.append(s)
                fam += s * R_SYM**p
            fams.append(fam)
    else:
        for e in exprs:
            paths = numeric_slots(e)
            slot_syms = [sp.Symbol(f"k{len(syms) + i + 1}", real=True)
                         for i in range(len(paths))]
            for s, v in zip(slot_syms, slot_values(e, paths)):
                originals[s] = v
            syms += slot_syms
            fams.append(replace_slots(e, paths, slot_syms))
        for idx in range(len(fams)):
            for p in enrich_powers:
                s = sp.Symbol(f"k{len(syms) + 1}", real=True)
                originals[s] = sp.S.Zero
                syms.append(s)
                fams[idx] = fams[idx] + s * R_SYM**p
    if not syms or len(syms) > max_consts:
        return []

    eqs = set()
    for res in sym_res:
        sub = res.subs(dict(zip(fn_objs, fams))).doit()
        num = sp.numer(sp.together(sub))
        try:
            poly = sp.Poly(sp.expand(num), R_SYM)
        except sp.PolynomialError:
            return []
        for c in poly.all_coeffs():
            # angle-fixing leaves unsimplified trig CONSTANTS in the
            # coefficients (measured: −4tan(11/10)+4sin(11/5)−4cos(11/5)
            # tan(11/10), which IS zero) — without simplification solve
            # sees "nonzero constant = 0" and reports the whole system
            # inconsistent
            c = sp.simplify(c)
            if c == 0:
                continue
            if not (c.free_symbols & set(syms)):
                return []  # genuinely nonzero constant: no solution here
            eqs.add(c)
    try:
        sols = sp.solve(list(eqs), syms, dict=True)
    except Exception:
        return []

    out = []
    for sol in sols[:max_sols]:
        free = [s for s in syms if s not in sol]
        fills = [{s: (originals[s] if originals[s] != 0 else sp.S.One)
                  for s in free}]
        if any(originals[s] == 0 for s in free):
            fills.append({s: sp.S.NegativeOne for s in free})
        for fill in fills:
            full = dict(sol)
            full.update(fill)
            full = {s: sp.simplify(sp.sympify(v).subs(full))
                    for s, v in full.items()}
            if any(v.free_symbols or not v.is_real
                   for v in full.values()):
                continue
            cand = tuple(sp.simplify(f.subs(full)) for f in fams)
            if cand not in out:
                out.append(cand)
    return out
