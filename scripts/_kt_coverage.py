#!/usr/bin/env python3
"""Coverage of the reducible span: how much of the generator algebra the ansatz can actually hold.

WHY THIS EXISTS. A null result is a statement about a SEARCH SPACE, and this repo reported nulls
for weeks without ever stating how much of the relevant structure that space contained. The ZV
tables in CLAUDE.md §2 grew LINEARLY per rank (2 4 6 8 10 12) while the generator algebra they
claimed to exhaust grows COMBINATORIALLY (2 4 6 9 12 16). Nobody noticed, because the numbers were
correct, monotone, plausible, and sitting in a file that loads every session. The defect was in a
growth rate that was never compared to anything.

THE DIAGNOSTIC, which costs nothing and is checkable by inspection:

    a reported null sequence growing LINEARLY where the structure it claims to exhaust grows
    COMBINATORIALLY is the signature of a truncating search space.

THE FIX. Where the search space is enumerable -- and a polynomial box is -- report the COVERAGE
RATIO alongside the null. "Zero irreducible at rank 6" and "zero irreducible at rank 6, over 17 of
30 reducible directions" are the same measurement and a different claim. The first invites the
reading that the structure was exhausted; only the second is true.

Note the asymmetry that makes this tractable here and not everywhere: a polynomial box can be
counted, so blindness is MEASURABLE. A literature sweep's space of query phrasings cannot be, so
there the only remedy is to widen and re-check. Same failure, different remedy.
"""


def algebra_span(rank, gens, denpow=None):
    """Monomials p_t^a p_phi^b H^c Lsq^e of total momentum degree `rank`.

    gens: which rank-2 generators exist, as a subset of {"H", "Lsq"}. Each carries one power of the
    denominator L, so `denpow` (when given) caps c+e -- that cap is exactly what the ansatz imposes,
    and dropping it gives the unrestricted algebra."""
    hi = "H" in gens
    lo = "Lsq" in gens
    n = 0
    for a in range(rank + 1):
        for b in range(rank + 1):
            for c in range(rank // 2 + 1 if hi else 1):
                for e in range(rank // 2 + 1 if lo else 1):
                    if a + b + 2 * c + 2 * e != rank:
                        continue
                    if denpow is not None and c + e > denpow:
                        continue
                    n += 1
    return n


def coverage(rank, gens, denpow):
    """(representable, unrestricted, ratio) for the reducible span at this rank."""
    r = algebra_span(rank, gens, denpow)
    u = algebra_span(rank, gens, None)
    return r, u, (r / u if u else 1.0)


if __name__ == "__main__":
    print(__doc__.split("\n\n")[0], "\n")
    cases = [("ZV delta=2  (p_t,p_phi,H)        den^1", ("H",), 1,
              [2, 4, 6, 8, 10, 12]),
             ("ZV delta=1  (p_t,p_phi,H,Lsq)    den^1", ("H", "Lsq"), 1,
              [2, 5, 8, 11, 14, 17]),
             ("sGB rank2-6 (p_t,p_phi,H)        den^6", ("H",), 6, None)]
    for label, gens, dp, published in cases:
        print(f"  {label}")
        row_r, row_u, row_p = [], [], []
        for rk in range(1, 7):
            r, u, f = coverage(rk, gens, dp)
            row_r.append(r); row_u.append(u); row_p.append(f)
        print("    representable :", "  ".join(f"{v:3d}" for v in row_r))
        print("    algebra       :", "  ".join(f"{v:3d}" for v in row_u))
        print("    coverage      :", "  ".join(f"{v*100:3.0f}%" for v in row_p))
        if published:
            ok = published == row_r
            print(f"    published     : {'  '.join(f'{v:3d}' for v in published)}   "
                  f"reproduced: {ok}")
            assert ok, "the model does not reproduce the published row -- fix the model, not the row"
        print()
    print("  READING. den^1 truncates hard and the ZV closures are den^1 -- at rank 6, delta=1 saw")
    print("  17 of 30 reducible directions. den^6 is not a restriction at these ranks: c+e <= 6 is")
    print("  never binding for rank <= 6, so the sGB ladder covers its algebra completely and its")
    print("  nulls carry no coverage caveat. That difference is the point of measuring rather than")
    print("  assuming -- the same guard is decisive on one substrate and vacuous on the other.")
