#!/usr/bin/env python3
"""Step 16 — T3 attempt: Gauss-Newton + continuation for the universal fit.

The measured bottlenecks from step 15 (sealed-holdout FAIL at 3.6%):
hill-climb under-convergence and non-corresponding basins across p.
Both die here:
  - hand-rolled Gauss-Newton/Levenberg on the 2×306 RESIDUAL VECTOR
    (L2 objective, numeric Jacobian, 4-6 params → normal equations are
    a tiny linear solve; stdlib only, quadratic convergence near optima)
  - CONTINUATION in p: fit p=0.10, warm-start 0.15, ... walk to 0.60 in
    0.05 steps — constants drift smoothly by construction
  - universal assembly: per-constant polynomial in p (degree 2, least
    squares over the 11 training points), then the SEALED p=0.7 verdict
    (holdout from step 15, untouched by any fit — pre-registration
    holds; training-grid densification is free choice).

Pass bars on the sealed holdout: <1% = universal formula stands;
<0.3% = KKZ-class universal; <0.1% = T3.

Run:  .venv/bin/python scripts/16_edgb_t3.py
"""

import importlib.util
import json
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(_here, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m11 = _load("edgb_shoot", "11_edgb_shoot.py")
m12 = _load("edgb_fit", "12_edgb_fit.py")

HOLDOUT_PATH = os.path.join(_here, "..", "edgb_truth_holdout.json")
TRAIN_PATH = os.path.join(_here, "..", "edgb_truth_dense.json")
P_TRAIN = [round(0.10 + 0.05 * i, 2) for i in range(11)]  # 0.10..0.60
P_HOLD = 0.7


# structure (winner of step 15's selection, normalized — 2 dof each):
#   A = 1 + a1(1−x)/(1 + a2 x),   B = 1 + b1(1−x)²/(1 + b2 x)
def model_A(x, a1, a2):
    return 1 + a1 * (1 - x) / (1 + a2 * x)


def model_B(x, b1, b2):
    return 1 + b1 * (1 - x)**2 / (1 + b2 * x)


def residuals(entry, params):
    a1, a2, b1, b2 = params
    out = []
    for rv, A, B, _ in entry["rows"]:
        x = 1 - 1.0 / rv
        out.append(model_A(x, a1, a2) / A - 1)
        out.append(model_B(x, b1, b2) / B - 1)
    return out


def linf(entry, params):
    return max(abs(r) for r in residuals(entry, params))


def gauss_newton(entry, p0, iters=60, lam0=1e-3):
    """Levenberg-damped Gauss-Newton on the L2 residual; stdlib only."""
    p = list(p0)
    lam = lam0
    f = residuals(entry, p)
    cost = sum(r * r for r in f)
    n = len(p)
    for it in range(iters):
        # numeric Jacobian
        J = []
        for j in range(n):
            dp = max(1e-7, abs(p[j]) * 1e-7)
            p2 = list(p)
            p2[j] += dp
            f2 = residuals(entry, p2)
            J.append([(b - a) / dp for a, b in zip(f, f2)])
        # normal equations (J^T J + λI) δ = -J^T f
        JTJ = [[sum(J[i][k] * J[j][k] for k in range(len(f)))
                for j in range(n)] for i in range(n)]
        JTf = [sum(J[i][k] * f[k] for k in range(len(f))) for i in range(n)]
        for attempt in range(8):
            Mx = [[JTJ[i][j] + (lam if i == j else 0) for j in range(n)]
                  for i in range(n)]
            # Gaussian elimination
            aug = [row[:] + [-JTf[i]] for i, row in enumerate(Mx)]
            ok = True
            for c in range(n):
                piv = max(range(c, n), key=lambda r_: abs(aug[r_][c]))
                if abs(aug[piv][c]) < 1e-14:
                    ok = False
                    break
                aug[c], aug[piv] = aug[piv], aug[c]
                for r_ in range(n):
                    if r_ != c:
                        fct = aug[r_][c] / aug[c][c]
                        for cc in range(c, n + 1):
                            aug[r_][cc] -= fct * aug[c][cc]
            if not ok:
                lam *= 10
                continue
            delta = [aug[i][n] / aug[i][i] for i in range(n)]
            p_new = [a + d for a, d in zip(p, delta)]
            f_new = residuals(entry, p_new)
            cost_new = sum(r * r for r in f_new)
            if cost_new < cost and all(math.isfinite(c_) for c_ in p_new):
                p, f, cost = p_new, f_new, cost_new
                lam = max(lam / 3, 1e-12)
                break
            lam *= 10
        else:
            break  # no improvement at any damping — converged
        if lam > 1e8:
            break
    return p, linf(entry, p)


def build_train():
    if os.path.exists(TRAIN_PATH):
        with open(TRAIN_PATH) as fh:
            return json.load(fh)
    print("   building dense training truth (one-time)...")
    f_g2, f_p2, f_y = m11.build_rhs(verbose=False)
    out = {}
    for p in P_TRAIN:
        rec = []
        M, D, ok = m11.shoot(f_g2, f_p2, p, record=rec)
        assert ok is True, f"shoot failed p={p}: {ok}"
        Gacc_inf, r_inf = rec[-1][4], rec[-1][0]
        norm = 1 - 2 * M / r_inf
        rows = []
        for (rv, phi, p1, gp, gacc) in rec:
            if rv > m12.R_FIT_MAX or rv < 1.0001:
                continue
            eG = math.exp(gacc - Gacc_inf) * norm
            eL = f_y(rv, phi, p1, gp)
            rows.append([rv, eG / (1 - 1.0 / rv),
                         math.sqrt(max(eG * eL, 0.0)), phi])
        out[str(p)] = {"M": M, "D": D, "rows": rows}
        print(f"     p={p}: M={M:.6f}")
    with open(TRAIN_PATH, "w") as fh:
        json.dump(out, fh)
    return out


def polyfit(xs, ys, deg):
    """Least-squares polynomial fit, stdlib (normal equations)."""
    n = deg + 1
    A = [[sum(x**(i + j) for x in xs) for j in range(n)] for i in range(n)]
    b = [sum(y * x**i for x, y in zip(xs, ys)) for i in range(n)]
    aug = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r_: abs(aug[r_][c]))
        aug[c], aug[piv] = aug[piv], aug[c]
        for r_ in range(n):
            if r_ != c:
                fct = aug[r_][c] / aug[c][c]
                for cc in range(c, n + 1):
                    aug[r_][cc] -= fct * aug[c][cc]
    return [aug[i][n] / aug[i][i] for i in range(n)]


def main():
    train = build_train()
    with open(HOLDOUT_PATH) as fh:
        hold = json.load(fh)
    print("\n== continuation fit (Gauss-Newton), p = 0.10 → 0.60 ==")
    params = [-0.05, 1.0, -0.05, 1.0]
    fits = []
    for p in P_TRAIN:
        params, s = gauss_newton(train[str(p)], params)
        fits.append((p, s, list(params)))
        print(f"   p={p:4.2f}: L∞ {s:.4%}  "
              + ", ".join(f"{v:+.5f}" for v in params))
    worst_train = max(s for _, s, _ in fits)

    print("\n== constants as polynomials in p (degree 2, LSQ) ==")
    ps = [f[0] for f in fits]
    coeff_fns = []
    for i in range(4):
        ys = [f[2][i] for f in fits]
        cs = polyfit(ps, ys, 2)
        coeff_fns.append(cs)
        print(f"   c{i + 1}(p) = {cs[0]:+.5f} {cs[1]:+.5f}p {cs[2]:+.5f}p²")

    def consts_at(p):
        return [cs[0] + cs[1] * p + cs[2] * p * p for cs in coeff_fns]

    # in-sample sanity of the universal formula
    uni_train = max(linf(train[str(p)], consts_at(p)) for p in P_TRAIN)

    print("\n== SEALED HOLDOUT p=0.7 ==")
    s_hold = linf(hold, consts_at(P_HOLD))
    print(f"   per-p training worst:        {worst_train:.4%}")
    print(f"   universal in-sample worst:   {uni_train:.4%}")
    print(f"   universal on SEALED p=0.7:   {s_hold:.4%}")
    tier = ("T3 — beats KKZ ✅" if s_hold < 0.001 else
            "KKZ-class universal ✅" if s_hold < 0.003 else
            "universal formula stands (<1%) ✅" if s_hold < 0.01 else
            "does not generalize ❌")
    print(f"\nVERDICT: {tier}")
    return 0 if s_hold < 0.01 else 1


if __name__ == "__main__":
    raise SystemExit(main())
