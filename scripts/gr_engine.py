"""The GR engine — shared by all conjecture-machine steps.

Pure SymPy, no GR library: zero black boxes between a candidate metric
and its verdict. Dimension-agnostic.

Design notes (each one bought by a measured failure):
- Vacuum check uses the RICCI form of the field equations,
  R_ab = [2Λ/(n-2)] g_ab, which is equivalent to G_ab + Λ g_ab = 0 for
  n > 2 (take the trace) but avoids building the Ricci scalar and
  Einstein tensor — blanket simplify() on Kerr's full Einstein matrix
  ran >12 CPU-minutes without terminating; the Ricci form is tractable.
- Christoffels are simplified BEFORE Riemann is built: intermediate
  simplification prevents combinatorial expression-swell downstream.
- Symbolic zero-testing uses a cheap→expensive cascade with early exit
  instead of one blanket simplify() call.
- Verdicts are THREE-valued (Richardson's theorem: zero-equivalence is
  undecidable, so "didn't simplify to zero" never proves "nonzero"):
    VERIFIED  — residual ≡ 0 symbolically: a theorem.
    REJECTED  — residual ≠ 0 at a numeric point: definitive.
    UNPROVEN  — numerically zero, symbolically stuck: needs a human.
"""

import random
from functools import cached_property

import sympy as sp

VERIFIED, REJECTED, UNPROVEN = "VERIFIED", "REJECTED", "UNPROVEN"

R_SYM = sp.Symbol("r", positive=True)


def build_ansatz_metric(n, fexpr):
    """The static one-function ansatz in n spacetime dimensions:
    diag(-f, 1/f, r², r²sin²θ, r²sin²θsin²φ, ...). Shared by the GP
    loop, the catalog loader, and family generalization."""
    t = sp.Symbol("t", real=True)
    angles = sp.symbols(f"x1:{n - 1}", real=True)  # x1..x_{n-2}
    parts = [-fexpr, 1 / fexpr]
    area = R_SYM**2
    for i in range(n - 2):
        parts.append(area)
        area = area * sp.sin(angles[i]) ** 2
    coords = [t, R_SYM] + list(angles)
    return sp.diag(*parts), coords, angles


def zero_simplify(expr):
    """Cheap-to-expensive simplification cascade with early exit at zero."""
    if expr == 0:
        return sp.S.Zero
    for fn in (lambda e: sp.cancel(sp.together(e)),
               sp.factor,
               sp.trigsimp,
               sp.simplify):
        try:
            expr = fn(expr)
        except Exception:
            continue  # a stage choking must not sink the candidate
        if expr == 0:
            return sp.S.Zero
    return expr


class Geometry:
    """All curvature objects derived from a metric, computed lazily & cached."""

    def __init__(self, metric: sp.Matrix, coords):
        self.g = sp.Matrix(metric)
        self.coords = list(coords)
        self.n = len(self.coords)
        assert self.g.shape == (self.n, self.n)

    @cached_property
    def ginv(self):
        return self.g.inv()

    @cached_property
    def christoffel(self):
        """Gamma^a_{bc} = 1/2 g^{ad} (d_b g_dc + d_c g_db - d_d g_bc),
        simplified eagerly — they are small, and clean Christoffels keep
        Riemann from exploding."""
        n, g, ginv, x = self.n, self.g, self.ginv, self.coords
        Gamma = [[[sp.S.Zero] * n for _ in range(n)] for _ in range(n)]
        for a in range(n):
            for b in range(n):
                for c in range(b, n):
                    expr = sum(
                        ginv[a, d] * (sp.diff(g[d, c], x[b])
                                      + sp.diff(g[d, b], x[c])
                                      - sp.diff(g[b, c], x[d]))
                        for d in range(n)) / 2
                    expr = sp.simplify(sp.cancel(sp.together(expr)))
                    Gamma[a][b][c] = expr
                    Gamma[a][c][b] = expr
        return Gamma

    @cached_property
    def riemann(self):
        """R^a_{bcd} = d_c Gamma^a_{db} - d_d Gamma^a_{cb}
                       + Gamma^a_{ce} Gamma^e_{db} - Gamma^a_{de} Gamma^e_{cb}."""
        n, x = self.n, self.coords
        Gamma = self.christoffel
        R = [[[[sp.S.Zero] * n for _ in range(n)] for _ in range(n)]
             for _ in range(n)]
        for a in range(n):
            for b in range(n):
                for c in range(n):
                    for d in range(c + 1, n):
                        expr = (sp.diff(Gamma[a][d][b], x[c])
                                - sp.diff(Gamma[a][c][b], x[d])
                                + sum(Gamma[a][c][e] * Gamma[e][d][b]
                                      - Gamma[a][d][e] * Gamma[e][c][b]
                                      for e in range(n)))
                        expr = sp.cancel(sp.together(expr))
                        R[a][b][c][d] = expr
                        R[a][b][d][c] = -expr
        return R

    @cached_property
    def ricci(self):
        """R_{bd} = R^a_{bad}."""
        n = self.n
        Riem = self.riemann
        Ric = sp.zeros(n, n)
        for b in range(n):
            for d in range(b, n):
                expr = sp.cancel(sp.together(
                    sum(Riem[a][b][a][d] for a in range(n))))
                Ric[b, d] = expr
                Ric[d, b] = expr
        return Ric

    @cached_property
    def ricci_scalar(self):
        Ric = self.ricci
        return zero_simplify(sum(self.ginv[a, b] * Ric[a, b]
                                 for a in range(self.n)
                                 for b in range(self.n)))

    @cached_property
    def ricci_squared(self):
        """R_ab R^ab — second invariant of the fingerprint set."""
        n, ginv, Ric = self.n, self.ginv, self.ricci
        return sp.simplify(sum(
            ginv[a, p] * ginv[b, q] * Ric[a, b] * Ric[p, q]
            for a in range(n) for b in range(n)
            for p in range(n) for q in range(n)))

    @cached_property
    def kretschmann(self):
        """K = R_{abcd} R^{abcd} — the coordinate-independent fingerprint."""
        n, g, ginv = self.n, self.g, self.ginv
        Riem = self.riemann
        # Two measured bottlenecks, two fixes (see below). Final reduction in
        # BOTH branches is cancel(together(K)) not simplify(K): blanket
        # simplify() drowns in multivariate-GCD blowup on Λ≠0 families
        # (measured: >20 CPU-hours unfinished on an n=9 AdS case), while
        # cancel/together yields the identical rational function in under a
        # second — same rule as zero_simplify and the D2/D4 design notes.
        if g.is_diagonal():
            # Diagonal metric ⇒ g and g^{-1} are diagonal, so
            #   R_{abcd} = g_{aa} R^a_{bcd}   (no sum over e), and raising all
            # four indices is multiplication by the diagonal inverse, giving
            #   K = Σ_{abcd} g^{aa}g^{bb}g^{cc}g^{dd} (g_{aa} R^a_{bcd})².
            # This is O(n⁴), not O(n⁸): the giant Σ_{pqrs} index contraction
            # collapses to one surviving term. Every build_ansatz_metric
            # metric is diagonal; the general branch below still serves Kerr.
            gd = [g[i, i] for i in range(n)]
            gi = [ginv[i, i] for i in range(n)]
            K = sp.S.Zero
            for a in range(n):
                for b in range(n):
                    for c in range(n):
                        for d in range(n):
                            Re = Riem[a][b][c][d]
                            if Re == 0:
                                continue
                            K += gi[a] * gi[b] * gi[c] * gi[d] * (gd[a] * Re)**2
            # K is independent of the angular coordinates (spherical symmetry
            # of the ansatz). Reducing the raw K over r AND all those trig
            # variables is what blew up at high n. Instead evaluate the angles
            # at a real regular point where every trig value is a nonzero
            # rational — atan(3/4): sin=3/5, cos=4/5, tan=3/4, sin2θ=24/25,
            # cos2θ=7/25 — with expand_trig to resolve the multiple-angle
            # terms the curvature produces. That leaves K(r), so the final
            # reduction is over r alone and cancel/together is near-instant.
            angles = [x for x in self.coords
                      if g.has(sp.sin(x)) or g.has(sp.cos(x))]
            if angles:
                K = sp.expand_trig(
                    K.subs({x: sp.atan(sp.Rational(3, 4)) for x in angles}))
            return sp.cancel(sp.together(K))
        Rdown = [[[[sp.cancel(sp.together(sum(g[a, e] * Riem[e][b][c][d]
                                              for e in range(n))))
                    for d in range(n)] for c in range(n)]
                  for b in range(n)] for a in range(n)]
        K = sp.S.Zero
        for a in range(n):
            for b in range(n):
                for c in range(n):
                    for d in range(n):
                        if Rdown[a][b][c][d] == 0:
                            continue
                        Rup = sum(ginv[a, p] * ginv[b, q] * ginv[c, r]
                                  * ginv[d, s] * Rdown[p][q][r][s]
                                  for p in range(n) for q in range(n)
                                  for r in range(n) for s in range(n))
                        K += Rdown[a][b][c][d] * Rup
        # General (non-diagonal, e.g. Painlevé-Gullstrand, Kerr) path keeps
        # full simplify: it must collapse coordinate-dependence that a bare
        # cancel/together leaves behind (a θ-dependent K broke the P-G costume
        # test), and these metrics are rare + small so simplify is affordable.
        # The fast diagonal branch above is the only one that needed the
        # cancel/together + angle-eval treatment.
        return sp.simplify(K)

    def grad_invariant(self, scalar):
        """|∇S|² = g^{ab} ∂_a S ∂_b S — a differential invariant of any
        scalar invariant S. The pair (S, |∇S|²) gives a coordinate-free
        curve: the poor man's Cartan invariant."""
        n, x = self.n, self.coords
        return sp.simplify(sum(self.ginv[a, b]
                               * sp.diff(scalar, x[a]) * sp.diff(scalar, x[b])
                               for a in range(n) for b in range(n)))

    def vacuum_residual(self, Lambda=sp.S.Zero):
        """Field equations in Ricci form: R_ab - [2Λ/(n-2)] g_ab.
        Identically zero  <=>  G_ab + Λ g_ab = 0  (for n > 2)."""
        return self.ricci - (2 * Lambda / (self.n - 2)) * self.g


# ---------------------------------------------------------------------------
# The two-stage verifier
# ---------------------------------------------------------------------------

def numeric_spot_check(residual: sp.Matrix, coords, params, n_points=5,
                       tol=1e-8, seed=0):
    """Stage 1: evaluate the residual at random exact-rational points.
    Returns (passed, max_abs_residual). False is a definitive rejection."""
    rng = random.Random(seed)
    free = list(coords) + list(params)
    worst = 0.0
    for _ in range(n_points):
        subs = {s: sp.Rational(rng.randint(11, 99), rng.randint(7, 13))
                for s in free}
        for i in range(residual.rows):
            for j in range(i, residual.cols):
                try:
                    val = complex(residual[i, j].subs(subs).evalf(30))
                except (TypeError, ValueError):
                    return False, float("inf")
                worst = max(worst, abs(val))
                if worst > tol:
                    return False, worst
    return True, worst


def verify(metric, coords, params=(), Lambda=sp.S.Zero):
    """Full two-stage verdict on one candidate.
    Returns (verdict, detail) with verdict in {VERIFIED, REJECTED, UNPROVEN}."""
    geo = Geometry(metric, coords)
    residual = geo.vacuum_residual(Lambda)

    ok, worst = numeric_spot_check(residual, coords, params)
    if not ok:
        return REJECTED, f"numeric residual {worst:.3e}"

    stuck = []
    for i in range(geo.n):
        for j in range(i, geo.n):
            r = zero_simplify(residual[i, j])
            if r != 0:
                stuck.append(((i, j), r))
    if not stuck:
        return VERIFIED, "R_ab - [2Λ/(n-2)] g_ab ≡ 0 symbolically"
    return UNPROVEN, (f"numerically vacuum (max {worst:.1e}) but "
                      f"{len(stuck)} component(s) symbolically stuck, "
                      f"e.g. {stuck[0]}")
