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
