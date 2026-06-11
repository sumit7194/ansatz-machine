#!/usr/bin/env python3
"""Step 18 — fork (a): 3-dof structures for KKZ-class/T3.

The 2-dof structures saturate ~0.42% (measured floor). One more tail
term each:
    A = 1 + [a1(1−x) + a2(1−x)²] / (1 + a3·x)
    B = 1 + [b1(1−x)² + b2(1−x)³] / (1 + b3·x)
Same protocol as 16: GN + continuation p=0.10→0.60, degree-2 polynomial
coefficients, SEALED p=0.7 holdout. Bars: sealed <0.3% = KKZ-class
universal; per-p <0.1% = T3-grade pointwise.

Run:  .venv/bin/python scripts/18_edgb_3dof.py
"""
import importlib.util, json, os
_here = os.path.dirname(os.path.abspath(__file__))
def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_here, fname))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod
m16 = _load("edgb_t3", "16_edgb_t3.py")

def residuals6(entry, q):
    a1, a2, a3, b1, b2, b3 = q
    out = []
    for rv, A, B, _ in entry["rows"]:
        x = 1 - 1.0 / rv
        u = 1 - x
        out.append((1 + (a1*u + a2*u*u) / (1 + a3*x)) / A - 1)
        out.append((1 + (b1*u*u + b2*u**3) / (1 + b3*x)) / B - 1)
    return out

m16.residuals = residuals6
m16.linf = lambda entry, q: max(abs(r) for r in residuals6(entry, q))

def main():
    train = m16.build_train()
    with open(m16.HOLDOUT_PATH) as fh:
        hold = json.load(fh)
    print("== 3-dof fit (GN + continuation) ==")
    q = [-0.05, 0.0, 1.0, -0.05, 0.0, 4.0]
    fits = []
    for p in m16.P_TRAIN:
        q, s = m16.gauss_newton(train[str(p)], q, iters=120)
        fits.append((p, s, list(q)))
        print(f"   p={p:4.2f}: L∞ {s:.4%}  " + ", ".join(f"{v:+.5f}" for v in q))
    worst = max(s for _, s, _ in fits)
    ps = [f[0] for f in fits]
    coeffs = [m16.polyfit(ps, [f[2][i] for f in fits], 3) for i in range(6)]
    for i, cs in enumerate(coeffs):
        print(f"   q{i+1}(p) = {cs[0]:+.5f} {cs[1]:+.5f}p {cs[2]:+.5f}p² {cs[3]:+.5f}p³")
    def at(p): return [cs[0] + cs[1]*p + cs[2]*p*p + cs[3]*p**3 for cs in coeffs]
    uni = max(m16.linf(train[str(p)], at(p)) for p in m16.P_TRAIN)
    s_hold = m16.linf(hold, at(0.7))
    print(f"\n   per-p worst {worst:.4%} | universal in-sample {uni:.4%} | SEALED p=0.7: {s_hold:.4%}")
    tier = ("T3-grade sealed <0.1% 🏆" if s_hold < 0.001 else
            "KKZ-CLASS UNIVERSAL ✅ (<0.3%)" if s_hold < 0.003 else
            "stands (<1%) ✅" if s_hold < 0.01 else "❌")
    print("3-DOF VERDICT: " + tier)
    return 0 if s_hold < 0.01 else 1

if __name__ == "__main__":
    raise SystemExit(main())
