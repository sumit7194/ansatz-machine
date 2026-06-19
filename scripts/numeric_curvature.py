"""Numeric curvature — the finite-difference companion to the symbolic gr_engine.

Why it exists (2026-06-17): some metrics (Kerr–de Sitter) have a symbolic Ricci so
large it OOMs sympy. But for SEARCH (and for verification at a point) we never need
the symbolic form — only the curvature's VALUE at sample points. This computes the
Ricci tensor numerically from the metric via central finite differences: no symbolic
blow-up, microseconds-to-milliseconds per point, pure Python (no numpy).

    g_metric(x) -> 4x4 list of floats        (the metric at x = [x0,x1,x2,x3])
    ricci_numeric(g_metric, x) -> 4x4 R_ab   (numeric Ricci at x)

Accuracy is finite-difference (≈1e-5 with the default step) — plenty for a GP
fitness (minimize a residual) and for spot-checking; a hit still gets the exact
symbolic proof from gr_engine. Validated in battery 46 against Schwarzschild and
Kerr (Ricci ≈ 0) and Kerr–de Sitter (Ricci ≈ Λ g) — the case the symbolic engine
can't reduce.
"""

N = 4


def inv4(g):
    """4x4 matrix inverse via Gauss–Jordan (pure Python, no deps)."""
    A = [list(row) + [1.0 if i == j else 0.0 for j in range(N)] for i, row in enumerate(g)]
    for c in range(N):
        p = max(range(c, N), key=lambda i: abs(A[i][c]))
        A[c], A[p] = A[p], A[c]
        piv = A[c][c]
        A[c] = [v / piv for v in A[c]]
        for i in range(N):
            if i != c:
                f = A[i][c]
                A[i] = [A[i][k] - f * A[c][k] for k in range(2 * N)]
    return [row[N:] for row in A]


def _shift(x, d, dh):
    return [x[k] + (dh if k == d else 0.0) for k in range(N)]


def christoffel_numeric(g_metric, x, h=1e-5):
    """Γ^a_bc = ½ g^{ad}(∂_b g_dc + ∂_c g_db − ∂_d g_bc), derivatives by central FD."""
    g = g_metric(x)
    gi = inv4(g)
    dg = [[[ (g_metric(_shift(x, d, h))[a][b] - g_metric(_shift(x, d, -h))[a][b]) / (2 * h)
             for b in range(N)] for a in range(N)] for d in range(N)]
    return [[[ 0.5 * sum(gi[a][e] * (dg[b][e][c] + dg[c][e][b] - dg[e][b][c]) for e in range(N))
               for c in range(N)] for b in range(N)] for a in range(N)]


def ricci_numeric(g_metric, x, h=1e-5):
    """R_bd = ∂_a Γ^a_bd − ∂_d Γ^a_ba + Γ^a_ae Γ^e_bd − Γ^a_de Γ^e_ba (numeric)."""
    G = christoffel_numeric(g_metric, x, h)
    dG = [[[[ (christoffel_numeric(g_metric, _shift(x, d, h), h)[a][b][c]
              - christoffel_numeric(g_metric, _shift(x, d, -h), h)[a][b][c]) / (2 * h)
              for c in range(N)] for b in range(N)] for a in range(N)] for d in range(N)]
    R = [[0.0] * N for _ in range(N)]
    for b in range(N):
        for d in range(N):
            s = sum(dG[a][a][b][d] - dG[d][a][b][a] for a in range(N))
            s += sum(G[a][a][e] * G[e][b][d] - G[a][d][e] * G[e][b][a]
                     for a in range(N) for e in range(N))
            R[b][d] = s
    return R


def kretschmann_numeric(g_metric, x, h=1e-4):
    """Kretschmann scalar K = R_abcd R^abcd at x, by finite differences. Lets us
    probe curvature singularities of metrics whose symbolic K won't build (Kerr's
    ring singularity at Σ=0). Reuses the numeric Christoffels."""
    g = g_metric(x)
    gi = inv4(g)
    G = christoffel_numeric(g_metric, x, h)
    dG = [[[[ (christoffel_numeric(g_metric, _shift(x, d, h), h)[a][b][c]
              - christoffel_numeric(g_metric, _shift(x, d, -h), h)[a][b][c]) / (2 * h)
              for c in range(N)] for b in range(N)] for a in range(N)] for d in range(N)]
    Rup = [[[[ dG[c][a][d][b] - dG[d][a][c][b]
              + sum(G[a][c][e] * G[e][d][b] - G[a][d][e] * G[e][c][b] for e in range(N))
              for d in range(N)] for c in range(N)] for b in range(N)] for a in range(N)]
    Rl = [[[[ sum(g[a][e] * Rup[e][b][c][d] for e in range(N))
              for d in range(N)] for c in range(N)] for b in range(N)] for a in range(N)]
    K = 0.0
    for a in range(N):
        for b in range(N):
            for c in range(N):
                for d in range(N):
                    if Rl[a][b][c][d] == 0:
                        continue
                    K += Rl[a][b][c][d] * sum(
                        gi[a][p] * gi[b][q] * gi[c][s] * gi[d][w] * Rl[p][q][s][w]
                        for p in range(N) for q in range(N) for s in range(N) for w in range(N))
    return K


def vacuum_lambda_residual(g_metric, x, Lam=0.0, h=1e-5):
    """Worst |R_ab − Λ g_ab| at x — zero iff x solves the vacuum+Λ equations there."""
    g = g_metric(x)
    R = ricci_numeric(g_metric, x, h)
    return max(abs(R[i][j] - Lam * g[i][j]) for i in range(N) for j in range(N))


def _riemann_lower_numeric(g_metric, x, h=1e-4):
    """R_{abcd} at x (all indices down), by finite differences."""
    g = g_metric(x)
    G = christoffel_numeric(g_metric, x, h)
    dG = [[[[ (christoffel_numeric(g_metric, _shift(x, d, h), h)[a][b][c]
              - christoffel_numeric(g_metric, _shift(x, d, -h), h)[a][b][c]) / (2 * h)
              for c in range(N)] for b in range(N)] for a in range(N)] for d in range(N)]
    Rup = [[[[ dG[c][a][d][b] - dG[d][a][c][b]
              + sum(G[a][c][e] * G[e][d][b] - G[a][d][e] * G[e][c][b] for e in range(N))
              for d in range(N)] for c in range(N)] for b in range(N)] for a in range(N)]
    return [[[[ sum(g[a][e] * Rup[e][b][c][d] for e in range(N))
               for d in range(N)] for c in range(N)] for b in range(N)] for a in range(N)]


def weyl_scalars_numeric(g_metric, x, tetrad, h=1e-4):
    """The five Newman–Penrose Weyl scalars (Ψ0…Ψ4) at x, given a null tetrad
    (l, n, m, mbar) — numeric, so it handles metrics whose symbolic Weyl swamps
    (Kerr). Weyl = Riemann − Ricci terms (in 4D). Tetrad entries may be complex."""
    g = g_metric(x)
    R = _riemann_lower_numeric(g_metric, x, h)
    Ric = ricci_numeric(g_metric, x, h)
    Rs = sum(inv4(g)[a][b] * Ric[a][b] for a in range(N) for b in range(N))

    def C(a, b, c, d):
        return (R[a][b][c][d]
                - 0.5 * (g[a][c] * Ric[b][d] - g[a][d] * Ric[b][c]
                         - g[b][c] * Ric[a][d] + g[b][d] * Ric[a][c])
                + (Rs / 6.0) * (g[a][c] * g[b][d] - g[a][d] * g[b][c]))

    def k(v1, v2, v3, v4):
        return sum(C(a, b, c, d) * v1[a] * v2[b] * v3[c] * v4[d]
                   for a in range(N) for b in range(N) for c in range(N) for d in range(N))

    l, n, m, mb = tetrad
    return (k(l, m, l, m), k(l, n, l, m), k(l, m, mb, n), k(l, n, mb, n), k(n, mb, n, mb))


def petrov_type_numeric(Psi, floor=1e-7, rel=1e-5):
    """Petrov type from the |Ψ|-pattern (numeric) in an adapted tetrad. A Weyl scalar
    counts as NON-zero only if it clears BOTH an ABSOLUTE noise floor (finite-difference
    Weyl noise is ~1e-9 in geometric units M~1) and a relative tolerance. If every |Ψ|
    is below the floor the Weyl is numerically zero ⇒ type O (conformally flat).

    The absolute floor is essential: a purely relative tolerance misclassifies type O
    (all-noise) as type I, and a weak field (tiny Ψ2 at large r) as type II — both bugs
    a stress test caught. Assumes geometric/order-1 units; for very weak fields raise
    `floor` or the finite-difference precision."""
    mags = [abs(p) for p in Psi]
    big = max(mags)
    if big < floor:                         # all Weyl scalars are noise ⇒ conformally flat
        return "O"
    thr = max(floor, rel * big)
    s = {k for k, m in enumerate(mags) if m > thr}
    if not s:
        return "O"
    if s == {2}:
        return "D"
    if s in ({0}, {4}):
        return "N"
    if s <= {0, 1} or s <= {3, 4}:
        return "III"
    if s <= {0, 1, 2} or s <= {2, 3, 4}:
        return "II"
    return "I"
