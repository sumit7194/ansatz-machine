#!/usr/bin/env python3
"""Step 17 — fork (b): is c1 ≡ c3 real structure?

The universal fit (16) produced c1(p) ≈ c3(p) to ~3 digits. Test: TIE
them (one shared tail coefficient, 3 params total) and rerun the full
continuation + polynomial assembly + SEALED p=0.7 holdout. If accuracy
survives, the formula drops to 9 numbers and the A/B tails share their
leading coefficient — a discovered relation worth a symbolic look.

Run:  .venv/bin/python scripts/17_edgb_tied.py
"""
import importlib.util, json, math, os
_here = os.path.dirname(os.path.abspath(__file__))
def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_here, fname))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod
m16 = _load("edgb_t3", "16_edgb_t3.py")

def residuals3(entry, q):
    c, a2, b2 = q
    out = []
    for rv, A, B, _ in entry["rows"]:
        x = 1 - 1.0 / rv
        out.append((1 + c * (1 - x) / (1 + a2 * x)) / A - 1)
        out.append((1 + c * (1 - x)**2 / (1 + b2 * x)) / B - 1)
    return out

# monkey-wire the 3-param model into 16's GN by shadowing its residuals
m16.residuals = residuals3
m16.linf = lambda entry, q: max(abs(r) for r in residuals3(entry, q))

def main():
    train = m16.build_train()
    with open(m16.HOLDOUT_PATH) as fh:
        hold = json.load(fh)
    print("== tied-coefficient fit: A,B share c;  (c, a2, b2) ==")
    q = [-0.05, 1.0, 4.0]
    fits = []
    for p in m16.P_TRAIN:
        q, s = m16.gauss_newton(train[str(p)], q)
        fits.append((p, s, list(q)))
        print(f"   p={p:4.2f}: L∞ {s:.4%}  " + ", ".join(f"{v:+.5f}" for v in q))
    worst = max(s for _, s, _ in fits)
    ps = [f[0] for f in fits]
    coeffs = [m16.polyfit(ps, [f[2][i] for f in fits], 2) for i in range(3)]
    for i, cs in enumerate(coeffs):
        print(f"   q{i+1}(p) = {cs[0]:+.5f} {cs[1]:+.5f}p {cs[2]:+.5f}p²")
    def at(p): return [cs[0] + cs[1]*p + cs[2]*p*p for cs in coeffs]
    uni_train = max(m16.linf(train[str(p)], at(p)) for p in m16.P_TRAIN)
    s_hold = m16.linf(hold, at(0.7))
    print(f"\n   per-p worst {worst:.4%} | universal in-sample {uni_train:.4%} | SEALED p=0.7: {s_hold:.4%}")
    print("TIED-c VERDICT: " + ("c1≡c3 SURVIVES — 9-number formula ✅" if s_hold < 0.01 else "tying degrades — c1≈c3 was approximate ❌"))
    return 0 if s_hold < 0.01 else 1

if __name__ == "__main__":
    raise SystemExit(main())
