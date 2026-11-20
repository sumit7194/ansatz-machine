"""Post-hoc k -> 0 scan for §159 (not part of the registered verdict). Checks whether S is continuous in k at k = 0."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import sympy as sp
from _nve_lower import run_case, A, z, OUT
from _ts_edge2 import fleet_guard

if __name__ == "__main__":
    g = fleet_guard()
    if g:
        raise SystemExit(f"NOT STARTED: {g}")
    fK = 1 - 1 / (z - sp.I * A) - 1 / (z + sp.I * A)
    ck = os.path.join(OUT, "lower_kscan.jsonl")
    done = set()
    if os.path.exists(ck):
        done = {json.loads(l)["k"] for l in open(ck)}
    for k in (sp.Rational(1, 10000), sp.Rational(1, 1000), sp.Rational(1, 300)):
        if str(k) in done:
            continue
        r = run_case("T-scan", fK, k, sp.Rational(4, 5))
        open(ck, "a").write(json.dumps(r, default=str) + "\n")
        print(f"k={k} E=4/5: S(0.35)={r['runs']['0.35']['S']:.4e} S(0.2)={r['runs']['0.2']['S']:.4e} "
              f"poles {r['poles_P']} gates {'PASS' if r['gates_ok'] else 'FAIL'} -> {r['cls']} [{r['sec']:.0f}s]", flush=True)
